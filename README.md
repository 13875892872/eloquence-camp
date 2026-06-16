# 🎤 口才训练营

> 每日科学练口才，自信表达看得见

一款轻量化微信端口才训练小程序，提供分阶口才练习、全场景话术实战、每日打卡监督、AI 文案辅助、AI 语音评测反馈五大核心能力，帮助用户利用碎片时间系统化提升表达能力。

---

## 📁 项目结构

```
eloquence-camp/
├── miniapp/        # 微信小程序 (uni-app Vue3)
│   ├── src/
│   │   ├── pages/            # 10 个页面
│   │   │   ├── home/         #   首页
│   │   │   ├── checkin/      #   每日打卡
│   │   │   ├── training/     #   训练题库 (列表+详情)
│   │   │   ├── ai-tools/     #   AI文案 (生成+历史)
│   │   │   └── profile/      #   个人中心 (首页+录音+收藏+权益)
│   │   ├── api/              #   接口封装
│   │   ├── store/            #   Pinia 状态管理
│   │   ├── components/       #   公共组件
│   │   └── styles/           #   全局样式 (rpx自适应)
│   └── dist/dev/mp-weixin/   # 编译产物 → 微信开发者工具导入
│
├── server/             # 后端 API (Python Flask)
│   ├── app/
│   │   ├── api/              #   RESTful API (小程序 + 后台管理)
│   │   │   └── admin/        #   后台管理接口
│   │   ├── models/           #   SQLAlchemy 数据模型 (14张表)
│   │   ├── services/         #   业务逻辑 (Qwen/Oss/语音评测)
│   │   └── utils/            #   工具 (JWT/响应/装饰器)
│   ├── seeds/                #   种子数据 (管理员/配置初始化)
│   └── migrations/           #   数据库迁移
│
├── admin/              # 后台管理系统 (Vue3 + Element Plus)
│   └── src/views/            # 10 个管理页面
│       ├── dashboard/        #   数据看板 (ECharts)
│       ├── training/         #   训练题库管理 + 热门推荐
│       ├── checkin/          #   每日任务 + 成长目标配置
│       ├── ai/               #   AI 参数配置
│       ├── user/             #   用户列表 + 详情
│       ├── push/             #   消息推送
│       └── settings/         #   系统设置
│
└── docs/                     # 项目文档 (PRD/技术方案)
```

---

## 🛠 技术栈

| 模块 | 技术 | 说明 |
|------|------|------|
| **小程序前端** | uni-app 3 + Vue 3 + Pinia | 编译为微信小程序，rpx 响应式适配全机型 |
| **后台管理** | Vue 3 + Element Plus + ECharts + Vite | PC 端管理后台，图表可视化 |
| **后端 API** | Python 3.12 + Flask 3 + SQLAlchemy | RESTful API，JWT 鉴权 |
| **数据库** | SQLite (开发) / MySQL (生产) | 14 张表，含用户/训练/打卡/AI/管理 |
| **AI 文案** | 阿里云百炼 DashScope (Qwen-Plus) | 4 种场景文案生成 |
| **语音评测** | 阿里云智能语音交互 API | 发音/流利度/完整度 5 维评分 |
| **文件存储** | 阿里云 OSS | 录音文件云端保存 |
| **部署** | Nginx + Gunicorn | 反向代理 + WSGI |

---

## 🚀 快速开始

### 环境要求

| 工具 | 版本要求 |
|------|----------|
| Python | ≥ 3.10 |
| Node.js | ≥ 18 |
| npm | ≥ 9 |
| 微信开发者工具 | 最新稳定版 |

### 1. 后端启动

```bash
cd server

# 安装依赖
pip install -r requirements.txt

# 初始化数据库和种子数据
PYTHONIOENCODING=utf-8 PYTHONPATH=. python seeds/admin_seed.py
PYTHONIOENCODING=utf-8 PYTHONPATH=. python seeds/config_seed.py

# 启动开发服务器 (http://localhost:5000)
PYTHONIOENCODING=utf-8 PYTHONPATH=. python wsgi.py
```

### 2. 后台管理启动

```bash
cd admin

# 安装依赖
npm install

# 启动开发服务器 (http://localhost:3000)
npm run dev
```

**登录账号**：`admin` / `admin123`

### 3. 小程序启动

```bash
cd miniapp

# 安装依赖 (如有依赖冲突用 --legacy-peer-deps)
npm install

# 编译为微信小程序
npm run dev:mp-weixin
```

编译后在 `dist/dev/mp-weixin/` 生成产物，用**微信开发者工具**导入：

| 设置项 | 值 |
|--------|-----|
| 项目目录 | `miniapp/dist/dev/mp-weixin` |
| AppID | 选择「使用测试号」 |
| 本地设置 | ☑ 不校验合法域名 |
| API 地址 | `http://192.168.x.x:5000/api` (见下方说明) |

> ⚠️ 小程序开发时需将 API 地址改为本机局域网 IP（不能直接用 localhost），修改 `src/App.vue` 和 `src/api/request.js` 中的 `BASE_URL`。

---

## ⚙️ 配置说明

编辑 `server/.env`：

```env
# 数据库 (开发用SQLite，生产换MySQL)
DATABASE_URL=sqlite:///eloquence_dev.db

# 阿里云百炼 - Qwen API
DASHSCOPE_API_KEY=sk-your-api-key
QWEN_TEXT_MODEL=qwen-plus

# 阿里云语音评测 (一期可留空)
ALIYUN_SPEECH_APP_KEY=your-speech-app-key

# 微信小程序 (生产环境必填)
WECHAT_APPID=your-miniprogram-appid
WECHAT_SECRET=your-miniprogram-secret

# 阿里云 OSS (生产环境必填)
OSS_ACCESS_KEY_ID=your-oss-ak
OSS_ACCESS_KEY_SECRET=your-oss-sk
OSS_BUCKET_NAME=eloquence-camp
```

---

## 📡 API 接口概览

### 小程序端

| 模块 | 路由前缀 | 主要接口 |
|------|----------|----------|
| 认证 | `/api/auth` | 微信登录、同步用户信息 |
| 训练 | `/api/training` | 题库列表/详情、提交练习录音 |
| 打卡 | `/api/checkin` | 今日任务、完成任务、日历、成长进度 |
| AI文案 | `/api/ai-text` | 配额查询、生成文案、历史记录 |
| 语音评测 | `/api/ai-speech` | 提交录音评测 |
| 用户 | `/api/user` | 个人信息、收藏、练习记录 |

### 后台管理端 (需管理员 JWT)

| 模块 | 路由前缀 | 主要接口 |
|------|----------|----------|
| 认证 | `/api/admin` | 登录、修改密码 |
| 看板 | `/api/admin` | 数据看板聚合 |
| 素材 | `/api/admin` | 训练题 CRUD、批量上下架、推荐位配置 |
| 打卡 | `/api/admin` | 任务配置、成长目标配置 |
| AI | `/api/admin` | AI 参数配置 |
| 用户 | `/api/admin` | 用户列表、详情、权益调整 |
| 推送 | `/api/admin` | 推送模板、手动推送、推送记录 |

---

## 🗄 数据库表结构

| 表名 | 说明 | 核心字段 |
|------|------|----------|
| `users` | 用户表 | openid, nickname, total_days, growth_level, ability_score |
| `user_quota` | 权益配额 | daily_ai_quota, daily_ai_used, extra_quota |
| `training_items` | 训练题库 | category, title, sample_text, difficulty, status |
| `practice_records` | 练习记录 | audio_url, duration, ai_score, dimension_scores, ai_feedback |
| `checkin_records` | 打卡记录 | task_date, status, completed_tasks |
| `daily_task_config` | 每日任务配置 | task_index, title, min_duration, source_type |
| `growth_goal_config` | 成长目标配置 | goal_level, required_days, reward_extra_ai |
| `ai_text_records` | AI文案记录 | scene_type, input_params, generated_content |
| `ai_config` | AI全局配置 | text_model, 评测权重, Prompt模板 |
| `user_favorites` | 用户收藏 | item_type, item_id |
| `recommend_config` | 推荐位配置 | slot, training_item_id, refresh_mode |
| `admin_users` | 管理员账号 | username, password_hash |
| `operation_logs` | 操作日志 | action, target_type, detail |
| `push_records` | 推送记录 | template_type, target_count, reach_count |

---

## 🚢 生产部署

### 后端 (CentOS/Ubuntu)

```bash
# 安装依赖
pip install -r requirements.txt

# 修改 .env 为生产配置
cp .env.production .env

# Gunicorn 启动 (4 workers)
gunicorn wsgi:app -w 4 -b 0.0.0.0:5000 --daemon

# Nginx 反向代理配置
# location /api { proxy_pass http://127.0.0.1:5000; }
```

### 后台管理

```bash
cd admin
npm run build
# 将 dist/ 部署到 Nginx 静态目录
```

### 小程序

```bash
cd miniapp
npm run build:mp-weixin
# 用微信开发者工具上传代码 → 提交审核 → 发布
```

---

## 📋 一期功能清单

- [x] 5 个 TabBar 页面 (首页/打卡/训练/AI/我的)
- [x] 10 个小程序页面完整布局 (rpx 自适应)
- [x] 25+ RESTful API 接口
- [x] 14 张数据库表 + SQLAlchemy ORM
- [x] 微信静默登录 (JWT 鉴权)
- [x] Qwen AI 文案生成 (4 种场景)
- [x] AI 语音评测接口 (阿里云)
- [x] 10 个后台管理页面 (Element Plus + ECharts)
- [x] 训练题库 CRUD + 批量管理
- [x] 打卡任务/成长目标可配置
- [x] AI 参数后台可调
- [x] 用户权益手动调整
- [x] 消息推送管理
- [x] 操作日志记录
- [ ] 录音真实上传 OSS (接口已预留)
- [ ] 微信订阅消息推送 (模板已预留)
- [ ] 会员/付费体系 (二期)

---

## ❓ 常见问题

**Q: 小程序编译报 vendor.js 错误？**
A: 关闭微信开发者工具 → 删除 `dist/` 和 `node_modules/.vite/` → 重新 `npm run dev:mp-weixin`。

**Q: 小程序请求 localhost 超时？**
A: 微信模拟器不能直接用 localhost。把 `App.vue` 和 `api/request.js` 中的地址改成本机局域网 IP (如 `192.168.1.100`)，并确保 Windows 防火墙放行 5000 端口。

**Q: npm install 报 peer dependency 冲突？**
A: 使用 `npm install --legacy-peer-deps`。

**Q: Flask 启动报 MySQLdb 找不到？**
A: 检查 `.env` 中 `DATABASE_URL` 是否以 `sqlite:///` 开头（本地开发）。生产环境用 `mysql+pymysql://`。

**Q: 后台登录报 CORS 错误？**
A: 确保 Flask 的 CORS 配置正确，且请求地址一致（不要混用 localhost 和 127.0.0.1）。

---

## 📞 相关文档

- [小程序 PRD](docs/口才训练营小程序%20PRD_优化版.md)
- [后台管理需求](docs/后台管理PC端_功能需求.md)
- [技术方案设计](docs/技术方案设计文档.md)

---

> **版本** v1.0.0 | **更新日期** 2026-06-16
