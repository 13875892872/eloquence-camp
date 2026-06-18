# 口才训练营 · 后台管理

PC 端后台管理系统，用于运营配置、数据看板、题库管理、用户与 AI 参数维护。

**技术栈**：Vue 3 · Vue Router · Pinia · Element Plus · ECharts · Vite

---

## 功能模块

| 页面 | 路径 | 说明 |
|------|------|------|
| 登录 | `/login` | 管理员 JWT 登录 |
| 数据看板 | `/dashboard` | 用户/DAU/打卡率趋势、训练热度、留存漏斗、练习热力图 |
| 训练题库 | `/training` | 素材 CRUD、分类筛选、上下架 |
| 素材编辑 | `/training/edit` | 新增/编辑训练题 |
| 热门推荐 | `/training/recommend` | 首页推荐位配置 |
| 打卡任务 | `/checkin/tasks` | 每日任务配置（时长、来源分类） |
| 成长目标 | `/checkin/growth` | 打卡里程碑与奖励 |
| AI 配置 | `/ai` | 模型参数、Prompt、评测权重 |
| 用户列表 | `/user` | 用户查询、统计概览 |
| 用户详情 | `/user/:id` | 练习记录、打卡、权益调整 |
| 消息推送 | `/push` | 推送模板与记录 |
| 系统设置 | `/settings` | 基础配置 |
| 操作日志 | `/settings/logs` | 管理员操作审计 |
| 修改密码 | `/settings/password` | 管理员改密 |

---

## 快速开始

```bash
cd admin
npm install
npm run dev
```

- 开发地址：http://localhost:3000
- 默认账号：`admin` / `admin123`
- API 代理：`/api` → `http://localhost:5000`（见 `vite.config.js`）

**前提**：先启动 `server/` 后端（端口 5000）。

---

## 常用命令

```bash
npm run dev       # 开发
npm run build     # 生产构建 → dist/
npm run preview   # 预览构建产物
```

---

## 目录结构

```
admin/
├── src/
│   ├── api/           # axios 封装
│   ├── router/        # 路由与鉴权守卫
│   ├── views/         # 页面
│   ├── components/    # 公共组件
│   ├── styles/        # 全局样式
│   └── App.vue
├── vite.config.js     # Vite + API 代理
└── package.json
```

---

## 接口说明

所有请求走 `/api/admin/*`，Header 携带：

```
Authorization: Bearer <admin_jwt_token>
```

登录接口：`POST /api/admin/login`

---

## 生产部署

```bash
npm run build
# 将 dist/ 部署到 Nginx 静态目录
# 配置 Nginx 将 /api 反向代理到后端
```

---

## 常见问题

**登录后接口 401**  
确认后端已启动，且 `vite.config.js` 中 proxy 目标正确。

**看板无数据**  
后端无数据时部分图表会使用默认占位数据；可先运行 `server/seeds/demo_data_seed.py` 填充演示数据。

**CORS 报错**  
开发环境应走 Vite 代理，不要直接请求 `localhost:5000`；检查 `src/api/request.js` 的 baseURL 是否为 `/api`。

---

父项目说明见 [../README.md](../README.md)
