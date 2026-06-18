# 口才训练营

> 每日科学练口才，自信表达看得见

一款口才训练产品，包含微信小程序、H5 浏览器版、后台管理系统与统一后端 API。提供分阶练习、每日打卡、AI 文案生成、语音评测、成长激励等能力。

---

## 子项目

| 目录 | 说明 | 文档 |
|------|------|------|
| [`server/`](server/) | Python Flask 后端 API | 见下方「后端启动」 |
| [`miniapp/`](miniapp/) | 微信小程序（uni-app） | [miniapp/README.md](miniapp/README.md) |
| [`h5/`](h5/) | H5 浏览器版（与小程序功能一致） | [h5/README.md](h5/README.md) |
| [`admin/`](admin/) | 后台管理系统（Vue3 + Element Plus） | [admin/README.md](admin/README.md) |
| [`docs/`](docs/) | PRD、技术方案等项目文档 | — |

---

## 架构概览

```
┌─────────────┐   ┌─────────────┐   ┌─────────────┐
│   miniapp   │   │     h5      │   │    admin    │
│  微信小程序   │   │  浏览器 H5   │   │  后台管理    │
└──────┬──────┘   └──────┬──────┘   └──────┬──────┘
       │                 │                 │
       └─────────────────┼─────────────────┘
                         ▼
              ┌─────────────────────┐
              │   server (Flask)    │
              │   /api  小程序接口   │
              │   /api/admin 管理接口│
              └──────────┬──────────┘
                         ▼
              ┌─────────────────────┐
              │ SQLite / MySQL      │
              │ Qwen · OSS · 语音评测│
              └─────────────────────┘
```

---

## 环境要求

| 工具 | 版本 |
|------|------|
| Python | ≥ 3.10 |
| Node.js | ≥ 18 |
| 微信开发者工具 | 小程序调试（可选） |

---

## 一键启动（开发）

### 1. 后端（必须先启动）

```bash
cd server
pip install -r requirements.txt

# 首次：初始化数据库
# Windows PowerShell：
$env:PYTHONIOENCODING="utf-8"; $env:PYTHONPATH="."
python seeds/admin_seed.py
python seeds/config_seed.py
python seeds/demo_data_seed.py
python app/migrate.py

# 启动 API（端口 5000）
python wsgi.py
```

### 2. 按需启动前端

```bash
# 后台管理 → http://localhost:3000
cd admin && npm install && npm run dev

# 微信小程序 → 导入 miniapp/dist/dev/mp-weixin
cd miniapp && npm install --force && npm run dev:mp-weixin

# H5 浏览器 → http://localhost:5173
cd h5 && npm install --force && npm run dev
```

| 服务 | 地址 | 账号 |
|------|------|------|
| 后端 API | http://127.0.0.1:5000/api | — |
| 后台管理 | http://localhost:3000 | admin / admin123 |
| H5 | http://localhost:5173 | 自动登录 |
| 小程序 | 微信开发者工具导入 | 测试号 |

> **手机访问**：不能用 `localhost`，请用电脑局域网 IP，例如 `http://192.168.1.234:5173`（H5）或 `http://192.168.1.234:5000/api`（小程序 API）。

---

## 配置

编辑 `server/.env`（可参考 `.env.example`）：

```env
DATABASE_URL=sqlite:///eloquence_dev.db
DASHSCOPE_API_KEY=sk-xxx          # 阿里云百炼 Qwen
WECHAT_APPID=                     # 生产环境必填
WECHAT_SECRET=
OSS_ACCESS_KEY_ID=                # 录音上传
OSS_ACCESS_KEY_SECRET=
OSS_BUCKET_NAME=
```

Windows 下所有 Python 命令建议设置：

```powershell
$env:PYTHONIOENCODING="utf-8"
$env:PYTHONPATH="."
```

---

## API 概览

| 端 | 前缀 | 鉴权 |
|----|------|------|
| 小程序 / H5 | `/api/*` | 用户 JWT |
| 后台管理 | `/api/admin/*` | 管理员 JWT |

主要模块：`auth` · `training` · `checkin` · `ai-text` · `ai-speech` · `user` · `upload`

---

## 测试

```bash
cd server
$env:PYTHONIOENCODING="utf-8"; $env:PYTHONPATH="."
python -m unittest discover -s tests -p "test_*.py" -v
```

---

## 相关文档

- [小程序 PRD](docs/口才训练营小程序%20PRD_优化版.md)
- [后台管理需求](docs/后台管理PC端_功能需求.md)
- [技术方案设计](docs/技术方案设计文档.md)
- [发布说明](发布.md)

---

**版本** v1.0.0 · **更新** 2026-06-18
