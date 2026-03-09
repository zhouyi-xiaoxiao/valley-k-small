# Research Docs

跨报告研究文档的主入口只保留当前有效材料。

## Active Documents
- `research/docs/RESEARCH_SUMMARY.md`: 单文件研究简报，给人和 LLM 快速上手
- `research/docs/research_log/`: 阶段日志与迁移记录
- `research/docs/submission/`: 提交材料 PDF

## Archived Material
- 历史 agent 过程文档已移到 `research/archives/meta/agent_reports/`

## Maintenance
- 刷新研究摘要日期和自动索引:
  - `python3 scripts/reportctl.py summary`
- 校验主文档路径:
  - `python3 scripts/reportctl.py check-docs-paths`
- 清理本地噪音:
  - `python3 scripts/reportctl.py cleanup`

## Relations
- 报告正文与资产: `research/reports/`
- 历史归档: `research/archives/`
- 平台、自动化、schema、skills: `platform/`
