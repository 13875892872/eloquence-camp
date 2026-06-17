---
name: architecture-decisions
description: 项目架构关键决策记录
metadata:
  type: project
---

# 架构决策记录 (ADR)

## ADR-001: 素材获取系统设计
- **日期**: 2026-06-17
- **决策**: 独立 Python 调度脚本 + Windows 计划任务 / Linux cron
- **备选**: Flask 内嵌 APScheduler（被拒：增加依赖，Windows 兼容性差）
- **理由**: 独立脚本更容易调试、可单独运行、不依赖 Flask 进程存活

## ADR-002: AI 统一用 DashScope (Qwen)
- **日期**: 项目初期
- **决策**: 所有 AI 能力（文本生成、TTS、语音评测）统一用阿里云 DashScope
- **备选**: 多平台混合（被拒：管理复杂度高）
- **理由**: 单一 API Key 管理，费用统一结算

## ADR-003: 前端条件编译区分环境
- **日期**: 2026-06-17
- **决策**: uni-app `#ifdef MP-WEIXIN` 条件编译区分开发/生产 API 地址
- **备选**: 运行时配置（被拒：小程序不支持动态切换合法域名）
- **理由**: 编译时确定，避免开发环境误连生产

## ADR-004: SQLite 开发 / MySQL 生产
- **日期**: 项目初期
- **决策**: 本地开发用 SQLite，生产用 MySQL（pymysql 驱动）
- **理由**: SQLite 零配置，开发效率高；MySQL 适合生产并发

## ADR-005: Monorepo 三个子项目
- **日期**: 项目初期
- **决策**: server/ + admin/ + miniapp/ 放在一个仓库
- **理由**: 小团队，跨项目改动频繁，一个 PR 覆盖前后端更方便
