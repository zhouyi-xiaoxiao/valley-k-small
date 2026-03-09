# Platform

平台层承载“不是研究正文本身，但支撑研究交付和自动化”的能力。

## 子目录
- `platform/web/`: Next.js 站点、`public/data/v1` 预计算数据、前端源码。
- `platform/tools/repo/`: 仓库维护、注册表、归档、文档检查、摘要刷新。
- `platform/tools/web/`: 网站 payload、book/agent sync、交付构建。
- `platform/tools/automation/`: keepalive、优化循环、自动审查辅助。
- `platform/schemas/`: 网站、agent、book、archive 等 schema。
- `platform/skills/`: 仓库 continuation skill 与参考材料。
- `platform/agent/`: agent 身份/引导文档。
- `platform/runtime/`: 本地日志、keepalive 状态、交付缓存。

## 原则
- `scripts/` 只保留兼容包装器；真实实现放在这里。
- 研究正文与研究资产不要放进 `platform/`。
- 本地运行时噪音优先收进 `platform/runtime/`，避免污染仓库入口层。
