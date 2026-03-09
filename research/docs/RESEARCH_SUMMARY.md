# RESEARCH SUMMARY

最后更新: 2026-03-09

## 仓库定位
- 本仓库研究随机游走首达时间分布中的双峰、谷值、shortcut 机制与跨模型对比。
- `research/` 是研究主树，包含报告、研究文档与历史归档。
- `platform/` 承载网站、schema、自动化与 agent handoff 工具。
- `scripts/reportctl.py` 是唯一 Python CLI 入口。

## 当前主线
- Ring 系列:
  - `ring_lazy_flux`, `ring_lazy_jump*`, `ring_valley*`, `ring_two_target`, `ring_two_walker_encounter_shortcut`
  - 关注 lazy / non-lazy ring、shortcut 注入方式、峰谷判据与双峰窗口
- Grid2D 系列:
  - `grid2d_*`
  - 关注 corridor、rectangular geometry、two-target、reflecting / blackboard 等结构下的 valley 与 bimodality
- Cross-model:
  - `cross_luca_regime_map`
  - 关注跨模型 regime map、公平比较与 transfer 条件

## 建议阅读顺序
1. `research/reports/README.md`
2. `research/reports/report_registry.yaml`
3. 目标报告目录下的 `README.md`、`notes/`、`manuscript/`
4. 若需要交付或 agent 消费，再看 `platform/README.md`

## 研究与平台入口
- 人类阅读:
  - `research/docs/README.md`
  - `research/reports/README.md`
  - `platform/README.md`
- agent 入口:
  - `AGENTS.md`
  - `platform/skills/valley-k-small-continuation/`

## 常用命令
- `python3 scripts/reportctl.py list`
- `python3 scripts/reportctl.py resolve --report ring_valley_dst`
- `python3 scripts/reportctl.py build --report ring_valley_dst --lang cn`
- `python3 scripts/reportctl.py summary`
- `python3 scripts/reportctl.py doctor`
- `python3 scripts/reportctl.py agent-sync`
- `python3 scripts/reportctl.py agent-pack`

## 最新进展（手动追加）
- 仓库已收敛为 canonical 结构：`research/`、`platform/`、`packages/`、`scripts/`、`tests/`。
- 根目录兼容入口正在被移除，agent handoff 改为通过生成包输出到 `.local/deliverables/agent_pack/v1`。
- 文档、测试与 CLI 正在同步切换到单一 `reportctl` 表面。

## 自动索引（由脚本生成）
<!-- AUTO-INDEX:START -->
| report | pdfs | tex |
| --- | --- | --- |
<!-- AUTO-INDEX:END -->
