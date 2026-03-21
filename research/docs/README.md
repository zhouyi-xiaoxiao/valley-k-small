# Research Docs

跨报告研究文档的主入口只保留当前有效材料。

## Active Documents
- `research/docs/RESEARCH_SUMMARY.md`: 单文件研究简报，给人和 LLM 快速上手
- `research/docs/research_log/`: 阶段日志与迁移记录
- `research/docs/submission/`: 提交材料 PDF

## Archived Material
- 历史 agent 过程文档已移到 `research/archives/meta/agent_reports/`

## Maintenance
- 先准备 repo-local 开发环境：
  - `python3 -m venv .venv`
  - `. .venv/bin/activate`
  - `python -m pip install -r requirements.txt`
- 刷新研究摘要日期和自动索引:
  - `python3 scripts/reportctl.py summary`
- 校验主文档路径:
  - `python3 scripts/reportctl.py check-docs-paths`
- 清理本地噪音:
  - `python3 scripts/reportctl.py cleanup`
- 文档里的公开路径示例应直接写 canonical 路径，而不是 legacy 根入口或报告根兼容链接。

## Relations
- 报告正文与资产: `research/reports/`
- 最新 one-/two-target 机制综合稿: `research/reports/grid2d_one_two_target_gating/`
  - 现在是 repo-native 的 canonical 子系统，而不是读取 zip 的整合摘要
  - one-target 主文现在固定共享对称基线 `sym_shared`，分开讨论 top/bottom 与 same-membrane directional 两种非对称；gate-free rollback `L0R0/L0R1/L1R0/L1R1` 是主要离散机制，真实集合 x-gate `G_{X_g}={x=X_g}` 只保留为 `N/P/Q` 时间锚点，committor 只保留为附录对照
- 历史归档: `research/archives/`
- 平台、自动化、schema、skills: `platform/`
