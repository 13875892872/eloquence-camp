---
name: gotchas-discovered
description: 开发过程中发现的陷阱和解决方案
metadata:
  type: project
---

# 踩坑记录

## dashscope 版本兼容
- **问题**: dashscope 1.17.0 缺少 tts_v2 模块，TTS 无法使用
- **解决**: 升级到 1.25.22+
- **教训**: 新功能上线前先检查 SDK 版本是否支持

## 60s API 响应格式
- **问题**: news 字段返回字符串列表而非 dict 列表，导致解析崩溃
- **解决**: 兼容两种格式（str 和 dict），见 `sources/news_60s.py`
- **教训**: 第三方 API 响应格式可能不一致，需要防御性解析

## uni-app 条件编译
- **注意**: `#ifdef MP-WEIXIN` 只在生产构建生效，dev 构建走 `#ifndef` 分支
- **验证**: `grep "your-domain.com" dist/build/mp-weixin/app.js` 确认生效

## Flask CORS 双重配置
- **问题**: 只配 Flask-CORS 不够，preflight OPTIONS 可能失败
- **解决**: 同时加 `@app.after_request` 兜底处理器

## uni-app scoped styles
- **问题**: `<style scoped>` 中重定义 `.page` 会覆盖 global.scss
- **解决**: 永远不要在 scoped 中定义 `.page`

## Windows 编码
- **不设 PYTHONIOENCODING=utf-8 的后果**: 中文报 UnicodeEncodeError
- **所有 Python 命令**: 必须加 `PYTHONIOENCODING=utf-8 PYTHONPATH=.`
