# 口才训练营 · H5 版

与微信小程序**功能一致**的浏览器版本，无需发布微信即可在手机/电脑浏览器中使用。

**技术栈**：uni-app 3 + Vue 3 + Pinia（编译目标为 H5）

---

## 为什么有 H5

- 开发调试方便，浏览器直接打开
- 无需微信审核即可演示、内测
- 手机浏览器访问：`http://<电脑IP>:5173`

---

## 快速开始

```bash
cd h5
npm install --force
npm run dev
```

| 环境 | 地址 |
|------|------|
| 电脑浏览器 | http://localhost:5173 |
| 手机（同 WiFi） | http://192.168.1.234:5173 |

> 手机不能用 `localhost`，必须用电脑的局域网 IP。IP 可通过 `ipconfig` 查看。

**前提**：先启动 `server/` 后端（端口 5000）。H5 开发环境通过 Vite 将 `/api` 代理到 `http://127.0.0.1:5000`。

---

## 常用命令

```bash
npm run dev       # 开发（端口 5173）
npm run build     # 构建 → dist/build/h5/
npm run preview   # 构建后本地预览（端口 8080）
```

---

## 与小程序的差异

| 项目 | H5 处理 |
|------|---------|
| 登录 | 自动 `POST /auth/wechat-login`，code 固定为 `h5_browser_user` |
| API | 开发：`/api` 代理；生产：同域 `/api` 或配置 `VITE_API_BASE` |
| 录音 | 浏览器 `getUserMedia` 申请麦克风 |
| 订阅消息 | 无（降级为空操作） |
| 海报 | 浏览器下载，非保存相册 |
| 布局 | 桌面端最大宽度 430px 居中 |

---

## 环境变量

`.env.development`：

```env
VITE_API_BASE=/api
VITE_API_PROXY=http://127.0.0.1:5000
```

`.env.production`：

```env
VITE_API_BASE=/api
```

生产部署时，Nginx 需将 `/api` 反向代理到后端；或设置 `VITE_API_BASE=http://your-api-host/api` 后重新 build（后端已开启 CORS）。

---

## 目录结构

```
h5/
├── src/                 # 与 miniapp 同源页面（已做 H5 适配）
│   ├── App.vue          # H5 模拟登录
│   ├── api/request.js   # /api 相对路径
│   ├── pages/           # 12 个页面（同小程序）
│   └── ...
├── vite.config.js       # 代理 + host 0.0.0.0
├── index.html
└── package.json
```

**H5 专属改动文件**（同步 miniapp 时注意保留）：

- `src/App.vue`
- `src/api/request.js`
- `src/utils/subscribe.js`
- `src/pages/training/detail.vue`（麦克风权限）
- `src/components/poster.vue`（海报下载）
- `src/styles/global.scss`（居中布局）
- `src/manifest.json`（h5 路由 hash 模式）

---

## 生产部署

```bash
npm run build
# 将 dist/build/h5/ 部署到 Nginx / 静态托管
```

Nginx 示例：

```nginx
location / {
    root /path/to/dist/build/h5;
    try_files $uri $uri/ /index.html;
}
location /api {
    proxy_pass http://127.0.0.1:5000;
}
```

---

## 常见问题

**手机打不开**  
1. 手机和电脑同一 WiFi  
2. 使用 `http://192.168.x.x:5173`，不要用 localhost  
3. Windows 防火墙放行 5173 端口（管理员）：
   ```powershell
   netsh advfirewall firewall add rule name="H5 Dev 5173" dir=in action=allow protocol=TCP localport=5173
   ```

**接口失败**  
确认后端在 5000 端口运行；开发模式 API 走 Vite 代理，无需改 CORS。

**录音无权限**  
浏览器需 HTTPS 或 localhost 才能录音；局域网 IP 访问时 Chrome 可能限制，可尝试 Edge 或给 H5 配 HTTPS。

**与 miniapp 同步**  
`h5/src/` 从 `miniapp/src/` 复制而来，小程序更新后需手动同步对应文件，并保留上表中的 H5 适配改动。

---

父项目说明见 [../README.md](../README.md)
