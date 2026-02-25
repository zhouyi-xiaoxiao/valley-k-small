# valley-k-small

## 最新整理
- `reports/ring_lazy_jump_ext/` 已前置整合结论并压缩配图层级，同时重绘精确 f(t) 图以突出 peak/valley，并收紧时间展示范围。
- `reports/ring_lazy_jump_ext/` 已按统一结构整理：扩展章节在 `sections/`，生成输出在 `outputs/`，报告主文件为 `ring_lazy_jump_ext_{cn,en}.tex`，复现步骤见 `reports/ring_lazy_jump_ext/notes/readme_ext.md`。
- `reports/` 已完成域前缀命名（`ring_*`/`grid2d_*`/`cross_*`），旧目录兼容层已清理。
- 新增共享代码层 `src/vkcore/`（ring/grid2d/common）与归档层 `archives/reports/`（历史 runs + manifest/index）。
- 可用 `python3 scripts/check_legacy_usage.py` 持续跟踪历史命名残留引用。

本仓库用于研究环网络（ring / lazy ring）上带单条有向 shortcut 的首达时间（first-passage time）分布、双峰判据与数值/解析交叉验证，并生成对应图表与报告。

## 研究汇总（给 ChatGPT Pro）
- 总览与关键结论: `docs/RESEARCH_SUMMARY.md`
- 文档索引: `docs/README.md`
- 自动刷新: `python3 scripts/update_research_summary.py`
- 本地清理: `python3 scripts/cleanup_local.py`
- 统一入口: `python3 scripts/reportctl.py list`
- 一键体检: `python3 scripts/reportctl.py doctor`
- 旧命名产物清理: `python3 scripts/reportctl.py prune-legacy-artifacts --dry-run`

## 目录结构（按“每个报告一个子文件夹”）
每个报告都在 `reports/<report_name>/` 下自包含：
- `*.tex` / `*.pdf`：报告源码与编译产物
- `code/`：报告入口脚本（薄封装）
- `figures/`、`data/`、`tables/`、`inputs/`、`outputs/`、`sections/`、`notes/`：报告资产（按需存在）
- `build/`：临时构建产物（可删、可重生成；不应纳入版本控制）

仓库级新增：
- `src/vkcore/`：跨报告复用核心模块（`ring/`, `grid2d/`, `common/`）
- `archives/reports/`：历史 `runs/<timestamp>` 归档与 `manifest.json`/`index.jsonl`

当前报告列表（见 `reports/` 目录）：
- `reports/ring_lazy_jump/`, `reports/ring_lazy_jump_ext/`, `reports/ring_lazy_jump_ext_rev2/`
- `reports/ring_valley/`, `reports/ring_valley_dst/`, `reports/ring_lazy_flux/`, `reports/ring_deriv_k2/`, `reports/ring_two_target/`
- `reports/grid2d_bimodality/`, `reports/grid2d_reflecting_bimodality/`, `reports/grid2d_blackboard_bimodality/`, `reports/grid2d_two_target_double_peak/`, `reports/grid2d_rect_bimodality/`
- `reports/cross_luca_regime_map/`

## 命名规范
- 报告目录：`reports/<topic>` 或 `reports/<topic>_ext`；`<topic>` 控制在 1-2 个短词（必要时缩写，如 `flux`, `jump`, `dst`, `k2`）。
- 主报告文件：单语 `<folder>.tex` / `<folder>.pdf`；双语 `<folder>_cn.tex` / `<folder>_en.tex`（PDF 同名）。
- 额外说明文档：`note_<slug>.tex`（`<slug>` 1-2 个短词）。

## 快速开始
- 安装依赖：`python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`
- 校验元数据：`python3 scripts/validate_registry.py && python3 scripts/validate_archives.py`

## Web 站点（Next.js + 预计算数据）
- 构建站点数据：`python3 scripts/reportctl.py web-data --mode full`
- 生成 agent 同步产物：`python3 scripts/reportctl.py agent-sync`
- 构建静态站点：`python3 scripts/reportctl.py web-build --mode full`
- 本地预览（先完成 web-build）：`python3 scripts/reportctl.py web-preview --port 4173`

## 复现示例
- 列出报告：`python3 scripts/reportctl.py list`
- 解析报告：`python3 scripts/reportctl.py resolve --report ring_valley_dst`
- 在报告目录执行命令：`python3 scripts/reportctl.py run --report ring_valley_dst -- python3 code/bimodality_flux_scan.py --help`
- 编译中文主报告：`python3 scripts/reportctl.py build --report ring_valley_dst --lang cn`
- 快速审计：`python3 scripts/reportctl.py audit --fast`
