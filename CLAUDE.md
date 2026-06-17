# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

口才训练营 — a WeChat mini-program for public speaking training, with AI-powered text generation and voice evaluation. Three sub-projects in one monorepo.

## Common Commands

### Backend (server/)

```bash
cd server

# Install deps (pymysql NOT mysqlclient — Windows compat)
pip install -r requirements.txt

# Init DB + seed data (run both, order matters)
PYTHONIOENCODING=utf-8 PYTHONPATH=. python seeds/admin_seed.py
PYTHONIOENCODING=utf-8 PYTHONPATH=. python seeds/config_seed.py

# Dev server (port 5000, listens 0.0.0.0)
PYTHONIOENCODING=utf-8 PYTHONPATH=. python wsgi.py

# Test Qwen API directly
PYTHONIOENCODING=utf-8 PYTHONPATH=. python -c "
from app.services.qwen_client import qwen_client
print(qwen_client.chat('hello', max_tokens=50))
"
```

`PYTHONIOENCODING=utf-8` is **required on Windows** to prevent GBK encoding crashes. `PYTHONPATH=.` is required because the seed scripts and wsgi.py import from `app.` without being installed as a package.

### Admin Panel (admin/)

```bash
cd admin
npm install
npm run dev          # → http://localhost:3000
# Login: admin / admin123
```

Uses Vite with Element Plus auto-import (unplugin-vue-components). No manual component registration needed.

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

## Architecture

### Database

SQLite for local dev, MySQL (via pymysql) for production. Config lives in `server/.env` — `DATABASE_URL` key. 14 tables defined as SQLAlchemy ORM models in `app/models/`. Default admin password is hashed with bcrypt on first seed.

### API Design

Two blueprint groups under `/api`:
- **Mini-program APIs**: `auth`, `training`, `checkin`, `ai_text`, `ai_speech`, `user`, `upload` — most require user JWT
- **Admin APIs**: All under `/api/admin/*` — require admin JWT (identity is `{admin_id, role}` dict vs user's plain `user_id` string)

JWT issued by `flask-jwt-extended`. User JWT identity = `str(user.id)`, admin JWT identity = `{admin_id, role}`. The `login_required` vs `admin_required` decorators handle this difference.

CORS is configured in `app/extensions.py` with both Flask-CORS (explicit `/api/*` resources) AND an `@app.after_request` handler as a fallback — both are needed for preflight OPTIONS to work reliably.

### AI Integration

Two AI services:
- **Qwen (DashScope)**: `app/services/qwen_client.py` — uses `dashscope.Generation.call()`. The client is lazy-initialized (`_ensure_init()` pattern) because the API key in `.env` isn't loaded when the module is first imported. Without this pattern, the API key would be empty.
- **Speech Evaluation (Aliyun)**: `app/services/speech_eval.py` — API stub, endpoint exists but actual API call is TODO

### Training Data Seeds

`seeds/config_seed.py` populates default checkin tasks (3 tasks), growth goals (4 levels), and AI config. `seeds/admin_seed.py` creates the admin user. Both are idempotent — safe to re-run.

## Key Gotchas

### Windows Encoding
All Python commands must use `PYTHONIOENCODING=utf-8`. Chinese characters in seed scripts and API responses will crash with `UnicodeEncodeError` on GBK terminals otherwise.

### Flask Port Conflicts
Flask binds with `SO_REUSEADDR`, so `taskkill /F /IM python.exe` may leave zombie processes. Always check with `netstat -ano | grep :5000` after restart. PowerShell `Stop-Process -Force` kills them properly.

### Mini-Program Network
WeChat DevTools simulator **cannot reach `localhost`**. Use the machine's LAN IP (check with `ipconfig | grep 192.168`). Both `src/App.vue` (login) and `src/api/request.js` (all API calls) have a hardcoded `BASE_URL` that must be updated. On Windows, also run as admin: `netsh advfirewall firewall add rule name="Flask" dir=in action=allow protocol=TCP localport=5000`.

### uni-app Scoped Styles
Scoped `<style scoped>` in uni-app `.vue` files **overrides** the global `.page` class from `global.scss`. Never redefine `.page{...}` in scoped styles — it strips the global padding and safe-area settings. This was the cause of the "content cut off at edges" bug that took multiple iterations to find.

### npm install on uni-app
The `@dcloudio/uni-*` packages have aggressive peer dependency requirements. `npm install` without flags will fail. `--force` works but pulls in webpack as a transitive dep. `--legacy-peer-deps` skips too many deps. The official `npx degit dcloudio/uni-preset-vue#vite` template is the only reliable starting point — this project was scaffolded that way after the manual approach failed.

### Import Paths in uni-app
Vue reactivity APIs (`ref`, `computed`, `reactive`) must be imported from `'vue'`, NOT from `'@dcloudio/uni-app'`. Only uni-app lifecycle hooks (`onLoad`, `onShow`) come from `'@dcloudio/uni-app'`. Mixing these causes compile errors.

## Project State

- **Backend**: Working. All 25 admin routes + 10+ mini-program routes functional. Qwen API integration live with real key in `.env`.
- **Admin Panel**: Working. All 10 pages have real API integration with mock data fallback when API is unreachable.
- **Mini-Program**: Compiles and runs in WeChat DevTools. UI complete (10 pages, rpx responsive). Login auto-flows via WeChat `uni.login()`. Actual recording/upload/push features are stubbed with mock data — the API endpoints exist but frontend integration is placeholder.
- **Not Yet Implemented**: Real audio recording → OSS upload, WeChat subscription message push, Aliyun speech evaluation API call, production MySQL migration, paid membership system (planned phase 2).

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
# 每次改动后运行验证
cd server && PYTHONIOENCODING=utf-8 PYTHONPATH=. python verify.py

# 快速 API 冒烟测试
curl -s http://127.0.0.1:5000/api/training/items?page_size=1 | python -c "import sys,json; d=json.load(sys.stdin); print('API OK' if d['code']==200 else 'FAIL')"

# 小程序编译检查
cd miniapp && npx uni build -p mp-weixin 2>&1 | grep -q "DONE" && echo "BUILD OK" || echo "BUILD FAIL"
```

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
