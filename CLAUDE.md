# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

口才训练营 — a public speaking training platform with AI-powered text generation, voice evaluation, and gamified check-in. **Four sub-projects** in one monorepo:

| Directory | Type | Framework |
|-----------|------|-----------|
| `server/` | Python Flask API | Flask 3 + SQLAlchemy + DashScope |
| `admin/` | Admin SPA | Vue 3 + Element Plus + Vite |
| `miniapp/` | WeChat Mini-Program | uni-app 3 + Pinia |
| `h5/` | Browser H5 | uni-app 3 (same codebase as miniapp) |

## Common Commands

### Backend (server/)

```bash
cd server

# Install deps (pymysql NOT mysqlclient — Windows compat)
pip install -r requirements.txt

# Init DB + seed data (run all, order matters)
PYTHONIOENCODING=utf-8 PYTHONPATH=. python seeds/admin_seed.py
PYTHONIOENCODING=utf-8 PYTHONPATH=. python seeds/config_seed.py
PYTHONIOENCODING=utf-8 PYTHONPATH=. python seeds/demo_data_seed.py

# Apply manual migrations (adds columns Alembic might miss)
PYTHONIOENCODING=utf-8 PYTHONPATH=. python app/migrate.py

# Dev server (port 5000, listens 0.0.0.0)
PYTHONIOENCODING=utf-8 PYTHONPATH=. python wsgi.py

# Verification script (DB health + API smoke test + optional miniapp build)
PYTHONIOENCODING=utf-8 PYTHONPATH=. python verify.py

# Run tests
PYTHONIOENCODING=utf-8 PYTHONPATH=. python -m unittest discover -s tests -p "test_*.py" -v

# Test Qwen API directly
PYTHONIOENCODING=utf-8 PYTHONPATH=. python -c "
from app.services.qwen_client import qwen_client
print(qwen_client.chat('hello', max_tokens=50))
"

# Run scheduler (daily material fetching pipeline)
PYTHONIOENCODING=utf-8 PYTHONPATH=. python scheduler/run.py

# Run push tasks (daily remind / new material notify)
PYTHONIOENCODING=utf-8 PYTHONPATH=. python scheduler/push_task.py --type remind
```

`PYTHONIOENCODING=utf-8` is **required on Windows** to prevent GBK encoding crashes. `PYTHONPATH=.` is required because scripts import from `app.` without being installed as a package.

### Admin Panel (admin/)

```bash
cd admin
npm install
npm run dev          # → http://localhost:3000
npm run build        # → dist/
# Login: admin / admin123
```

Uses Vite with Element Plus auto-import (`unplugin-vue-components`). No manual component registration needed. Role-based menu filtering via `src/utils/menu.js`.

### Mini-Program (miniapp/)

```bash
cd miniapp

# First install — use --force to get all @dcloudio peer deps
npm install --force

# If that fails, install base then add extras:
npm install
npm install pinia dayjs --legacy-peer-deps

# Compile (output: dist/dev/mp-weixin/)
npm run dev:mp-weixin

# Clean rebuild (if vendor.js errors)
rm -rf dist node_modules/.vite && npm run dev:mp-weixin
```

The uni-app dependency chain (`@dcloudio/*`) is **notoriously fragile** on npm. `--force` is the only reliable install method. The mini-program **must** be imported into WeChat DevTools at `dist/dev/mp-weixin` with "不校验合法域名" checked.

### H5 Browser (h5/)

```bash
cd h5
npm install --force
npm run dev:h5       # → http://localhost:5173
npm run build:h5     # → dist/build/h5
```

Shares the same uni-app 3 architecture as miniapp. Pages, components, and stores are nearly identical. Key difference: `src/utils/media.js` (Web Audio API instead of `uni.recorder`) and `src/utils/route.js` (vue-router instead of uni.navigateTo).

## Architecture

### App Factory Pattern (server)

`wsgi.py` → `app/__init__.py:create_app(env)` → loads `config_map[env]` → initializes extensions → registers blueprints → registers error handlers.

Config is class-based in `app/config.py`: `Config` base → `DevelopmentConfig` (SQLite default, DEBUG=True) / `ProductionConfig` (MySQL required, DEBUG=False). `config_map = {'development': DevelopmentConfig, 'production': ProductionConfig}`.

### Environment Files

Three `.env` files in `server/`:
- `.env` — active development config (SQLite, real DashScope key)
- `.env.development` — reference template (MySQL example)
- `.env.production` — production template (MySQL RDS, `qwen3-max`/`qwen3-flash`)

Key env vars: `DATABASE_URL`, `DASHSCOPE_API_KEY`, `QWEN_TEXT_MODEL`, `QWEN_FEEDBACK_MODEL`, `WECHAT_APPID`, `WECHAT_SECRET`, `OSS_*`, `SCHEDULER_*`.

### Database

SQLite for local dev, MySQL (via pymysql) for production. 14 tables across 6 model files:

| File | Models |
|------|--------|
| `app/models/user.py` | `User`, `UserQuota` |
| `app/models/training.py` | `TrainingItem` |
| `app/models/checkin.py` | `CheckinRecord`, `DailyTaskConfig`, `GrowthGoalConfig` |
| `app/models/ai.py` | `AiTextRecord`, `AiConfig` |
| `app/models/admin.py` | `AdminUser`, `OperationLog`, `PushRecord`, `PushTemplate` |
| `app/models/common.py` | `PracticeRecord`, `UserFavorite`, `RecommendConfig` |

Models are imported in dependency order in `app/models/__init__.py`. `app/extensions.py` also imports all models so `flask db migrate` detects them.

Two migration paths:
1. **Flask-Migrate (Alembic)**: `server/migrations/` — the standard approach
2. **Manual**: `app/migrate.py` — lightweight ALTER TABLE script for `owner_user_id` and `checkin_records.status` columns, compatible with both SQLite and MySQL

### API Design

Two blueprint groups under `/api`:

**Mini-program APIs** (user JWT, identity = `str(user.id)`):
| Blueprint | File | Key Endpoints |
|-----------|------|---------------|
| `auth` | `api/auth.py` | `POST /wechat-login`, `PUT /sync-profile` |
| `training` | `api/training.py` | `GET /items`, `GET /items/<id>` (with difficulty unlock check) |
| `checkin` | `api/checkin.py` | `GET /today`, `POST /complete-task`, `POST /makeup`, `GET /calendar`, `GET /beginner-course`, `GET /push-template-ids`, `GET /growth-progress` |
| `ai_text` | `api/ai_text.py` | `GET /quota`, `POST /generate`, `GET /history`, `POST /import-practice` |
| `ai_speech` | `api/ai_speech.py` | `POST /evaluate`, `POST /tts` |
| `user` | `api/user.py` | `GET /profile`, `GET /favorites`, `POST /favorites/toggle`, `GET /practice-records`, `GET /leaderboard` |
| `upload` | `api/upload.py` | `POST /audio`, `GET /audio/<path>`, `GET /tts/<path>` |

**Admin APIs** (admin JWT, identity = `{admin_id, role}`):
| File | Key Endpoints |
|------|---------------|
| `api/admin/dashboard.py` | `POST /login`, `PUT /change-password`, `GET /dashboard` (stats, trends, retention, heatmap) |
| `api/admin/training.py` | CRUD `/training-items`, `PATCH .../status`, `POST .../batch-status`, `GET/PUT /recommend-config` |
| `api/admin/checkin.py` | `GET/PUT /checkin-config`, `GET/PUT /growth-config` |
| `api/admin/ai_config.py` | `GET/PUT /ai-config` |
| `api/admin/user.py` | `GET /users`, `GET /users/<id>`, `PUT /users/<id>/quota` |
| `api/admin/push.py` | `GET /push-templates`, `PUT /push-templates/<id>`, `POST /push/manual`, `GET /push-records` |
| `api/admin/settings.py` | `GET /operation-logs` (super_admin only) |

JWT issued by `flask-jwt-extended`. Decorators in `app/utils/decorators.py`: `login_required` (user JWT), `admin_required` (admin JWT), `optional_login`.

CORS is configured in `app/extensions.py` with both Flask-CORS (explicit `/api/*` resources) AND an `@app.after_request` handler as a fallback — both are needed for preflight OPTIONS to work reliably.

### Services Layer (`app/services/`)

| Service | Purpose |
|---------|---------|
| `qwen_client.py` | DashScope Qwen LLM — `chat()`, `generate_text()`, `generate_feedback()`. Lazy-initialized (`_ensure_init()`) because `.env` API key isn't loaded at import time. |
| `tts_client.py` | DashScope TTS v2 (CosyVoice) — text-to-speech with 6 voice options (longanyang/longxiaochun/longxiaoxia/longyue/longcheng/longhua). Returns local audio URL. |
| `speech_eval.py` | Speech evaluation with **three-tier fallback**: NLS API → Qwen multimodal → local duration-based. Reads Aliyun voice app credentials from env. |
| `oss_client.py` | File storage abstraction — local `uploads/` in dev, Aliyun OSS in production (gated by `OSS_ACCESS_KEY_ID` env var). |
| `checkin_service.py` | Check-in business logic: task validation, sequential unlocking, duration requirements, daily finalization with growth rewards. |
| `growth.py` | Growth level system — 5 levels (newbie→beginner→advanced→expert→master), difficulty caps per level, `apply_growth_rewards()` triggers on level-up. |
| `push.py` | WeChat subscription message push — manages access_token (2h cache), `send()` single-user, `send_batch()` bulk. |
| `admin_log.py` | Audit logging helper — writes to `operation_logs` table. |
| `wechat.py` | Stub for WeChat `code2Session` (actual logic in `auth.py`). |

### Scheduler (`scheduler/`)

Daily material-fetching pipeline. Run via `python scheduler/run.py` (one-shot, suitable for Windows Task Scheduler).

**Pipeline**: `run.py` → `pipeline.py` orchestrates: Fetch → Dedup → Process → Store

| Module | Role |
|--------|------|
| `config.py` | Three-layer config merge: defaults → `config.json` → `SCHEDULER_*` env vars. Sources: `news_60s`, `hot_topics`, `quotes` (enabled); `rss_feeds` (disabled by default). Max 12 items/run. |
| `sources/` | 4 content sources: News60s (60s.viki.moe), HotTopics (orz.ai Weibo), Quotes (Hitokoto + 今日诗词), RssFeeds (人民网/36氪/虎嗅). All extend `BaseSource`. |
| `dedup.py` | Two-layer dedup: SHA256-based source cache + DB similarity check. |
| `processor.py` | Qwen-powered: converts raw material → structured `TrainingItem` (category, title, sample_text, difficulty, tags). |
| `pipeline.py` | Master orchestrator — runs all enabled sources, reports success/fail/dup counts. |
| `push_task.py` | Separate push tasks: `--type remind` (daily practice reminder), `--type notify` (new material notification). Queries push templates and sends to subscribed users. |
| `logger.py` | Daily-rotating logs (30-day retention), `[source]` context labels. Logs at `scheduler/logs/`. |

### Seeds (`seeds/`)

All idempotent — safe to re-run:

| Seed | Creates |
|------|--------|
| `admin_seed.py` | Admin user (admin/admin123, bcrypt-hashed) |
| `config_seed.py` | 3 daily tasks, 4 growth goals (7/30/60/100 days), AI defaults, push templates (reads `WX_TMPL_*` env vars) |
| `demo_data_seed.py` | 30 training items (5 categories × 6), recommend slots, check-in + practice records, favorites, simulated user data |
| `extra_training_seed.py` | Expands categories (演讲/直播/即兴/面试/短视频/学生) to ≥15 items each |

`app/data/beginner_course.py` holds a static 7-day beginner course plan (not a seed — it's imported at runtime).

### Admin Panel Architecture

**Router**: `src/router/index.js` with `beforeEach` guard (auth check + role-based access). `src/router/menus.js` is the **single source of truth** for sidebar — defining items, sub-menus, and icons.

**Role filtering**: `src/utils/menu.js:filterMenusByRole()` strips super_admin-only items (settings) for regular admins.

**Composables**: `src/composables/useChart.js` — ECharts lazy-loading with ResizeObserver lifecycle management.

**Components** (6 reusable):
- `AppLayout.vue` — shell with sidebar + header + tabbed views
- `SettingsLayout.vue` — nested router-view for settings sub-pages
- `PageHeader.vue` — page title bar with action slot
- `FilterCard.vue` — search/filter card wrapper
- `TableCard.vue` — table with card-style container
- `ChartCard.vue` — chart container card

**Store**: `src/store/app.js` (Pinia) — sidebar collapse, responsive breakpoint, visited-tabs (persisted to sessionStorage), `getAdminRole()`.

**Utils**: `dict.js` — business dictionaries (categories, growth levels with tag types, AI scenes). All pages use real API data with structured error handling (not mock fallback).

### Mini-Program / H5 Architecture

Both share the same uni-app 3 + Vue 3 + Pinia architecture. Pages are organized into 5 tab modules (home, checkin, training, ai-tools, profile) plus sub-pages.

**Stores** (Pinia):
- `store/user.js` — token (synced via `uni.setStorageSync`), userInfo, logout
- `store/checkin.js` — today's tasks, check-in status, stats

**Components**: `AppIcon.vue`, `OnboardingGuide.vue`, `ScoreRadar.vue` (radar chart), `poster.vue` (Canvas-based share poster with save-to-album).

**Key miniapp-only utils**: `recordingCache.js` (audio cache), `subscribe.js` (WeChat subscription message handling).

**Key h5-only utils**: `media.js` (Web Audio API recording), `route.js` (vue-router navigation).

**pages.json**: 12 registered pages, 5-tab bar, darkmode enabled (`darkmode: true`), EasyCom auto-scan for `uni-*` components.

**Dark mode**: CSS custom properties defined in `variables.scss` (light + dark sets), consumed across all pages via `var(--xxx)`. Manual toggle available in profile page.

### AI Integration

Three AI services, all Aliyun DashScope:
- **Qwen text generation**: `qwen_client.py` — model configurable via `QWEN_TEXT_MODEL` / `QWEN_FEEDBACK_MODEL` env vars
- **TTS (CosyVoice v3-flash)**: `tts_client.py` — 6 voice timbres, output saved locally
- **Speech evaluation**: `speech_eval.py` — NLS API as primary, Qwen as fallback, local scoring as last resort

The Qwen client uses `_ensure_init()` lazy pattern because the DashScope API key in `.env` isn't available at module import time.

## Key Gotchas

### Windows Encoding
All Python commands must use `PYTHONIOENCODING=utf-8`. Chinese characters in seed scripts and API responses will crash with `UnicodeEncodeError` on GBK terminals otherwise.

### Flask Port Conflicts
Flask binds with `SO_REUSEADDR`, so `taskkill /F /IM python.exe` may leave zombie processes. Always check with `netstat -ano | grep :5000` after restart. PowerShell `Stop-Process -Force` kills them properly.

### Mini-Program Network
WeChat DevTools simulator **cannot reach `localhost`**. Use the machine's LAN IP (check with `ipconfig | grep 192.168`). Both `src/App.vue` (login) and `src/api/request.js` (all API calls) have a hardcoded `BASE_URL` that must be updated. On Windows, also run as admin: `netsh advfirewall firewall add rule name="Flask" dir=in action=allow protocol=TCP localport=5000`.

The mini-program API layer uses `#ifdef MP-WEIXIN` / `#ifndef MP-WEIXIN` conditional compilation to switch between dev (LAN IP) and production domains.

### uni-app Scoped Styles
Scoped `<style scoped>` in uni-app `.vue` files **overrides** the global `.page` class from `global.scss`. Never redefine `.page{...}` in scoped styles — it strips the global padding and safe-area settings. This was the cause of the "content cut off at edges" bug that took multiple iterations to find.

### npm install on uni-app
The `@dcloudio/uni-*` packages have aggressive peer dependency requirements. `npm install` without flags will fail. `--force` works but pulls in webpack as a transitive dep. `--legacy-peer-deps` skips too many deps. The official `npx degit dcloudio/uni-preset-vue#vite` template is the only reliable starting point — this project was scaffolded that way after the manual approach failed.

### Import Paths in uni-app
Vue reactivity APIs (`ref`, `computed`, `reactive`) must be imported from `'vue'`, NOT from `'@dcloudio/uni-app'`. Only uni-app lifecycle hooks (`onLoad`, `onShow`) come from `'@dcloudio/uni-app'`. Mixing these causes compile errors.

### DashScope SDK Version
DashScope must be ≥1.25.0 for CosyVoice TTS v3-flash. Earlier versions fail on TTS calls with obscure API errors.

### Qwen Client Lazy Init
The `_ensure_init()` pattern in `qwen_client.py` is critical — the API key in `.env` isn't loaded when the module is first imported. Don't refactor to initialize in `__init__` or at module level.

### H5 vs Mini-Program Differences
While `h5/` and `miniapp/` share the same uni-app codebase, they differ in:
- Audio recording: Web Audio API (h5) vs `uni.getRecorderManager()` (miniapp)
- Navigation: vue-router (h5) vs uni.navigateTo (miniapp)
- Network: direct HTTP (h5) vs WeChat proxy (miniapp)
- Storage: localStorage (h5) vs `uni.setStorageSync` (miniapp)

These differences are handled via `#ifdef H5` / `#ifdef MP-WEIXIN` conditional compilation.

### Docker/Production Notes
- Never commit `.env` files with real credentials. `.env.example` should be the committed template.
- The scheduler `run.py` and `push_task.py` expect a running Flask app context — they create their own via `create_app()`.
- For production, `gunicorn wsgi:app` with `FLASK_ENV=production` is the intended deployment.

## Project State

- **Backend**: Fully functional. 30+ API endpoints across 8 blueprint groups. Qwen AI, TTS, speech evaluation (3-tier), OSS upload, WeChat push, scheduler pipeline all live.
- **Admin Panel**: Fully functional. 14 pages across 8 modules. Role-based access (admin vs super_admin). Real API integration throughout.
- **Mini-Program**: Fully functional. 12 pages, 5-tab navigation. Dark mode, leaderboard, share poster, calendar view, favorites all implemented. Recording/upload/push all connected to real APIs.
- **H5**: Fully functional. Shares same pages as mini-program. Web Audio API for recording, vue-router for navigation. Same backend API surface.
- **Not Yet Implemented**: Production MySQL migration, paid membership system (phase 2).

## Loop Engineering — 自主开发循环

> 本项目采用 Loop Engineering 方法论。你只需在 `requirements.md` 中添加需求，Agent 自动发现、实现、验证。

### 需求发现

每次会话开始时，Agent 应读取 `requirements.md`，找到第一个 `- [ ]` 条目作为当前任务。实现完成后将 `[ ]` 改为 `[x]`，并附加实现摘要和日期。

**工作流**:
1. 读取 `requirements.md` → 找到待实现条目
2. 按优先级排序（高 → 中 → 低）
3. 选择下一个 `- [ ]` 条目
4. 实现 → 验证 → 更新 `requirements.md`

### 验证命令

```bash
# 每次改动后运行验证（检查 DB 健康 + API 可达 + 数据完整性 + 可选编译）
cd server && PYTHONIOENCODING=utf-8 PYTHONPATH=. python verify.py

# 快速 API 冒烟测试
curl -s http://127.0.0.1:5000/api/training/items?page_size=1 | python -c "import sys,json; d=json.load(sys.stdin); print('API OK' if d['code']==200 else 'FAIL')"

# 小程序编译检查
cd miniapp && npx uni build -p mp-weixin 2>&1 | grep -q "DONE" && echo "BUILD OK" || echo "BUILD FAIL"

# H5 编译检查
cd h5 && npx uni build -p h5 2>&1 | grep -q "DONE" && echo "BUILD OK" || echo "BUILD FAIL"
```

`verify.py` checks: DB tables (≥14) → API endpoints (GET /items, GET /items/1) → seed data (≥10 training items, ≥3 tasks, ≥4 growth goals) → optional miniapp build. Exit code 0 on all pass, 1 on any failure.

### 停止条件

Agent 在以下情况应**停止并汇报**，不继续自动修改：
- 需要微信 AppID / Secret / 支付密钥等外部凭证
- 涉及生产数据库结构变更（ALTER TABLE）
- 改动影响 5 个以上文件且不确认方案
- 3 次重试仍未通过验证
- API 调用返回 401/403（权限不足）

### 状态文件

| 文件 | 用途 |
|------|------|
| `requirements.md` | 需求入口，用户唯一需要编辑的文件 |
| `CLAUDE.md` | 项目知识库，Agent 每会话必读 |
| `发布.md` | 生产部署手册 |
| `server/verify.py` | 自动化验证脚本 |
| `server/scheduler/logs/` | 素材获取日志 |

### 记忆持久化

Agent 应将重要发现写入 `.claude/memory/`：
- 用户偏好（`user-preferences.md`）
- 踩坑记录（`gotchas-discovered.md`）
- 架构决策（`adr-*.md`）

### 示例：一条需求的完整 Loop

```
1. 用户在 requirements.md 添加:
   - [ ] 小程序增加「每日一句」首页卡片

2. Agent 发现此条目 → 分析涉及的文件:
   - miniapp/src/pages/home/index.vue (UI)
   - server/app/api/checkin.py (API 数据源)
   - 数据库无需改动

3. Agent 实现:
   - 在 checkin API 中增加 daily_quote 字段
   - 在首页增加金句卡片组件
   - 编译验证

4. Agent 更新 requirements.md:
   - [x] 小程序增加「每日一句」首页卡片 — 2026-06-18
     > checkin/today API 新增 daily_quote，首页增加 .quote-card

5. Agent 运行 verify.py 确认无回归
```
