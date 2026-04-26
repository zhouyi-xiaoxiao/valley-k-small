# Platform

`platform/` 放置“不是研究正文本身，但支撑研究交付、自动化和 agent handoff”的能力层。

## Subtrees
- `platform/web/`: Next.js 站点与 `public/data/v1` 预计算数据
- `platform/tools/repo/`: 注册表、归档、文档检查、摘要刷新、仓库维护
- `platform/tools/web/`: web payload、book、publication、agent pack 构建
- `platform/tools/automation/`: keepalive、review、content iteration、自动化辅助
- `platform/schemas/`: 数据契约与 schema
- `platform/skills/`: continuation skill 与参考材料

## Principles
- `scripts/` 是唯一公开脚本表面；真正实现都在 `platform/tools/`
- 研究正文与研究资产不放进 `platform/`
- 本地运行时状态不属于 canonical 树，统一写入 `.local/`
- agent 读取生成包，而不是依赖仓库中的第二套镜像目录

## Generated State
- 站点预计算输出: `platform/web/public/data/v1/`
- 站点公开静态资产: `platform/web/public/artifacts/`
- 本地隐藏状态:
  - `.local/checks/`
  - `.local/deliverables/`
  - `.local/keepalive/`
  - `.local/loop/`
