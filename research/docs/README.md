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
- 单 target 窗口测度解释稿: `research/reports/grid2d_one_target_window_measures/`
  - 专门解释 one-target 对称基线里 `occupancy share` 与 `ever-visit probability` 的差别
  - 说明为什么 `target_funnel` 可以在路径事件意义下是必经区，但在时间加权占据意义下只占小比例
  - 现已同步提供中英文 manuscript，并把配置示意图与第一张 occupancy 主图并排纳入同一个 overview figure
- 单 target 出走时序 companion report: `research/reports/grid2d_one_target_exit_timing/`
  - 在同一对称基线下扫描对称膜通透率 `\kappa`
  - 区分 `\tau_out`（第一次离开 corridor）与 `\tau_mem`（第一次 corridor-to-outside 膜穿越）
  - 同时提供窗口条件 CDF、relative timing ratio，以及 early / late / no-exit 三分解
- 单 target valley / peak2 时间预算短稿: `research/reports/grid2d_one_target_valley_peak_budget/`
  - 保留配置图，但把主图改成单轴 ring-style 的 co-located bar-on-curve 结构
  - overview 只叠 `\kappa=0` 与 `\kappa=0.0040` 两条曲线
  - 不再单独拆 `target funnel`，而把它并入 merged outer/right-side share
  - 直接比较 valley 与 `peak2` 的 exact outside-time share
  - 再补一张膜相关的 post-first-crossing remaining-time budget proxy，并把 `peak1` 放回 timing 图里做对照
- Exact Recursion 教学主稿: `research/reports/exact_recursion_method_guide/`
  - 中文正式方法 companion，系统讲清 time recursion / exact recursion 的原理
  - 用 `grid2d_one_two_target_gating` 的 shared symmetric baseline 作为贯穿例子
  - 同时对照 AW 数值反演与 Luca/GF 路线，解释各自的适用边界
- 历史归档: `research/archives/`
- 平台、自动化、schema、skills: `platform/`
