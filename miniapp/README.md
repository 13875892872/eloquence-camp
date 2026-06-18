# 口才训练营 · 微信小程序

基于 **uni-app 3 + Vue 3 + Pinia** 的微信小程序端，提供打卡、训练、AI 文案、语音评测等完整用户功能。

---

## 功能页面

| Tab / 页面 | 路径 | 说明 |
|------------|------|------|
| 首页 | `pages/home/index` | 推荐训练、7 天入门、每日金句 |
| 打卡 | `pages/checkin/index` | 今日任务、补签/休息、成长弹窗 |
| 打卡日历 | `pages/checkin/calendar` | 月历状态 |
| 训练 | `pages/training/index` | 分类题库、等级锁定 |
| 排行榜 | `pages/training/leaderboard` | 周/月时长、连续天数 Top10 |
| 训练详情 | `pages/training/detail` | 录音练习、五维雷达、成绩对比 |
| AI 文案 | `pages/ai-tools/index` | 演讲/短视频/直播/面试/开场白 |
| 历史记录 | `pages/ai-tools/history` | AI 生成历史 |
| 我的 | `pages/profile/index` | 个人数据、成长等级 |
| 录音记录 | `pages/profile/records` | 练习历史 |
| 我的收藏 | `pages/profile/favorites` | 收藏素材 |
| 权益中心 | `pages/profile/quota` | AI 配额 |

---

## 快速开始

```bash
cd miniapp
npm install --force
npm run dev:mp-weixin
```

编译产物：`dist/dev/mp-weixin/`

### 微信开发者工具

| 设置 | 值 |
|------|-----|
| 项目目录 | `miniapp/dist/dev/mp-weixin` |
| AppID | 使用测试号 |
| 本地设置 | ☑ 不校验合法域名、web-view、TLS |

**前提**：先启动 `server/` 后端。

---

## API 地址配置

小程序**不能**使用 `localhost`，需改为电脑局域网 IP。

修改以下文件中的 `BASE_URL`：

- `src/api/request.js`
- `src/App.vue` → `getBaseUrl()`

```js
// 示例：改为你本机 IP
const BASE_URL = 'http://192.168.43.30:5000/api'
```

同时确保 Windows 防火墙放行 **5000** 端口。

---

## 常用命令

```bash
npm run dev:mp-weixin    # 开发编译（监听）
npm run build:mp-weixin  # 生产构建
npm run dev:h5           # 也可编译 H5（推荐用独立 h5/ 项目）
```

---

## 目录结构

```
miniapp/
├── src/
│   ├── pages/           # 页面
│   ├── components/      # ScoreRadar、Poster、OnboardingGuide 等
│   ├── api/request.js   # 接口封装
│   ├── store/           # Pinia（user、checkin）
│   ├── utils/           # 分类、录音缓存、订阅消息
│   ├── styles/          # 全局 SCSS（rpx 适配）
│   ├── pages.json       # 路由 + tabBar
│   └── manifest.json    # 小程序配置
├── static/              # tabBar 图标等
└── vite.config.js
```

---

## 登录流程

启动后 `App.vue` 自动调用 `uni.login()` 获取 code，请求 `POST /api/auth/wechat-login` 换取 JWT。开发阶段后端使用 mock openid。

---

## 常见问题

**编译报 vendor.js 错误**  
删除 `dist/` 和 `node_modules/.vite/` 后重新 `npm run dev:mp-weixin`。

**请求超时**  
检查 API 地址是否为局域网 IP，后端是否运行，防火墙是否放行。

**npm install 失败**  
使用 `npm install --force`。

**页面内容贴边**  
不要在页面 scoped 样式中重写 `.page`，使用 `global.scss` 中的全局类。

**录音/上传失败**  
确认已授权麦克风；开发工具中勾选不校验域名。

---

## 与 H5 版关系

浏览器访问请使用同级目录 [`h5/`](../h5/)，功能一致但无需微信发布。`miniapp/` 为小程序专用；两边源码独立，改动后需手动同步。

---

父项目说明见 [../README.md](../README.md)
