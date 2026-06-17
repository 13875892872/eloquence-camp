# 需求看板 — Loop Engineering 入口

> **使用方式**: 在本文件中添加 `- [ ] 需求描述`，Agent 会自动发现并实现。
> 实现完成后，Agent 会将 `[ ]` 改为 `[x]`，并附加实现摘要。

---

## 🔥 待实现

### 高优先级

### 中优先级

### 低优先级

---

## ✅ 已完成

- [x] ~~小程序 BASE_URL 条件编译（开发/生产自动切换）~~ — 2026-06-17
  > `request.js` 和 `App.vue` 使用 `#ifdef MP-WEIXIN` / `#ifndef MP-WEIXIN` 区分开发/生产域名。开发使用 LAN IP，生产使用正式域名。

- [x] ~~微信订阅消息推送~~ — 2026-06-17
  > 后端 `push.py` + `push_task.py` 完整实现。前端 `checkin/index.vue` 和 `profile/index.vue` 从 `/checkin/push-template-ids` API 获取真实模板 ID（替代空数组）。`config_seed.py` 支持从环境变量 `WX_TMPL_*` 读取微信模板 ID。

- [x] ~~阿里云语音评测 API 对接~~ — 2026-06-17
  > `speech_eval.py` 三层降级：NLS API → Qwen → 本地规则。本地评测改为确定性算法（`math.sin` 替代 `random.seed`），基于维度的差异化评分，改进反馈生成逻辑。NLS Token 管理和 REST API 集成就绪。

- [x] ~~小程序录音功能完善 — OSS 上传~~ — 2026-06-17
  > `oss_client.py` 集成 `oss2` SDK，支持 OSS/本地双模式。通过 `OSS_ACCESS_KEY_ID` 等环境变量控制。`upload.py` 自动判断 OSS URL vs 本地路径。前端上传流程无需改动。

- [x] ~~打卡日历页面~~ — 2026-06-17
  > 新增 `miniapp/src/pages/checkin/calendar.vue` — 月视图日历、月份切换、已打卡日期标记、今日高亮、打卡统计。后端 `GET /checkin/calendar` API 已复用。从打卡页→日历导航。

- [x] ~~训练题详情页增加「收藏」按钮~~ — 2026-06-17
  > `training/detail.vue` 标题栏增加 ⭐/☆ 收藏图标，调用 `POST /user/favorites/toggle`。`onLoad` 时自动检查当前收藏状态。

- [x] ~~管理员后台素材管理页 — AI 素材审核~~ — 2026-06-17
  > `TrainingItem` 模型新增 `source` 字段（manual/ai_generated）。Admin 训练列表页增加来源筛选、AI/人工标签显示、批量上下架按钮。移除 mock 数据降级——使用真实数据或空状态。

- [x] ~~小程序增加「每日一句」首页卡片~~ — 2026-06-17
  > `GET /checkin/today` 返回 `daily_quote` 字段（从 Hitokoto/Jinrishici 获取，带日期缓存）。首页新增浅橙色金句卡片，失败时优雅降级为静态名言。

- [x] ~~训练排行榜~~ — 2026-06-17
  > 新增 `GET /user/leaderboard` API（按连续打卡天数+练习时长排序，含当前用户排名）。新增 `miniapp/src/pages/training/leaderboard.vue` — 领奖台、排行榜列表、我的排名卡片。从训练题库页导航进入。

- [x] ~~分享海报功能~~ — 2026-06-17
  > 新增 `miniapp/src/components/poster.vue` — Canvas 绘制海报（渐变背景 → 白色卡片 → 标题 → 统计数据 → 底部引导文字）。支持打卡/成就/评分三种类型。保存到相册功能。

- [x] ~~暗黑模式支持~~ — 2026-06-17
  > `pages.json` 开启 `darkmode: true`。`variables.scss` 定义 CSS 自定义属性（亮色/暗色两套）。`global.scss` 核心样式使用 `var(--xxx)`。所有页面 scoped 样式批量替换硬编码颜色为 CSS 变量。个人中心增加手动暗黑模式开关。

- [x] ~~AI 工具页四种场景表单差异化~~ — 2026-06-17
  > 短视频/直播/开场白的字段标签、选项、可见性各有不同

- [x] ~~每日素材自动获取系统~~ — 2026-06-17
  > `scheduler/run.py` 从 3 个源获取素材，Qwen AI 加工入库，支持 Windows 计划任务

- [x] ~~TTS 范本播放修复~~ — 2026-06-17
  > 升级 dashscope 到 1.25.22，CosyVoice TTS v3-flash 可用

- [x] ~~演示数据初始化~~ — 2026-06-17
  > 24道训练题 + 打卡 + 练习记录 + 收藏

- [x] ~~完整发布指南~~ — 2026-06-17
  > `发布.md` 含服务器/Nginx/SSL/数据库/运维全流程

- [x] ~~推送模板配置从环境变量读取~~ — 2026-06-17
  > `config_seed.py` 新增 `os.environ.get('WX_TMPL_*')` 支持，可更新已有模板

- [x] ~~数据库文件 Git 追踪移除~~ — 2026-06-17
  > `git rm --cached server/eloquence_dev.db`，`.gitignore` 的 `*.db` 规则生效

---

## 📋 模板（复制以下格式添加新需求）

```markdown
- [ ] 【功能】简短描述
  > 详细说明、涉及的文件、验收标准
  > 优先级理由
```
