# 研究汇总（供 ChatGPT Pro）

最后更新: 2026-03-09

## 使用说明（只给这一份文件即可）
这份文件设计为**自包含**的项目总览：包含研究目标、模型定义、主要结论、报告入口、复现命令与维护规则。
如果你只会把一个文件交给 ChatGPT Pro，请直接给它本文件即可。
注意：如果 ChatGPT Pro 只拿到本文件，请默认它**无法访问仓库**；路径与命令仅用于说明研究来源与可复现性。

## 一句话总览（给 AI 的上下文入口）
我在研究环网络上的随机游走首达时间分布，重点是单条有向 shortcut 如何引发双峰/谷结构，以及不同模型构造（lazy vs non-lazy、selfloop vs renormalize vs equal4）对这一现象的影响与机制解释。

## 当前研究关注（手动维护）
（请在这里写“正在做/接下来要做”的问题，帮助 AI 快速进入你的工作流）
- 当前问题: 1D ring 双 walker encounter 在有向 shortcut 下，如何稳定实现并解释双峰（含 A1/A8 生成函数乘积验证与时域首遇分布分解）。
- 近期目标: 扩展 1D encounter 的参数相图（N, q, g1, g2, src/dst, beta）并评估双峰区间的稳健性与阈值敏感性。
- 需要 AI 帮助: 自动化参数扫描与相图可视化；对峰谷判据、通道分解与质量守恒诊断给出统一审计流程。

## 最新进展（手动追加）
（请在这里用日期追加最新结果/想法，便于对方快速理解“当前进度”）
- 2026-03-04: 按“持续优化 `reports/ring_two_walker_encounter_shortcut/`（每轮重跑 codegen + 双语构建 + consistency + pytest，优先修复峰比定义/多峰选峰/fixed-site parity 一致性）”完成本轮本地闭环。核心修复：`code/two_walker_ring_encounter_report.py` 将 timescale 选峰器统一为“候选峰对需满足 `tau-t1>=2`”（保证 `t_v(\tau)=\arg\min_{t_1<t<\tau}g_t` 在严格内区间有定义），并同步写入 detector contract（新增 `valley_interior_rule=require_tau_minus_t1>=2_for_strict_interior_valley`）；中英文正文 `ring_two_walker_encounter_shortcut_{cn,en}.tex` 与自动片段 `tables/fixedsite_parity_note_{cn,en}.tex` 同步补充该约束；`code/check_encounter_consistency.py` 与 `tests/test_ring_two_walker_encounter_shortcut.py` 新增对应守护，且新增回归 `test_select_timescale_t2_rejects_adjacent_peak_without_interior_valley`。执行链路均通过：`../../.venv/bin/python code/two_walker_ring_encounter_report.py`（`real 10.75s`）、中文 `latexmk -xelatex ...`（`real 2.73s`）、英文 `latexmk -pdf ...`（`real 0.91s`）、`../../.venv/bin/python code/check_encounter_consistency.py`（`real 0.05s`，`[ok]`）、`../../.venv/bin/python -m pytest -q ../../tests/test_ring_two_walker_encounter_shortcut.py`（`8 passed`，`real 1.21s`）、`../../.venv/bin/python ../../scripts/update_research_summary.py`（`real 0.05s`）。按分流策略本轮继续本地执行（单轮明显低于 >20 分钟阈值），未触发 Isambard 远端流程（`JOB_ID: N/A`, `REMOTE_DIR: N/A`；关键产物：`reports/ring_two_walker_encounter_shortcut/data/{case_summary,fixedsite_summary}.json`、`reports/ring_two_walker_encounter_shortcut/tables/fixedsite_parity_note_{cn,en}.tex`、`reports/ring_two_walker_encounter_shortcut/ring_two_walker_encounter_shortcut_{cn,en}.pdf`；下一步：继续本地闭环，若转大规模并行或预计单轮 >20 分钟再切 `isbard doctor/auth -> submit/status/fetch`）。
- 2026-03-03: 按“持续优化 `reports/ring_two_walker_encounter_shortcut/`、每轮重跑 codegen + 双语构建 + consistency + pytest，优先修复峰比定义/多峰选峰/fixed-site parity 一致性”完成本轮本地闭环。核心修复为：`code/two_walker_ring_encounter_report.py` 新增并统一 detector contract 字段（`peak_prominence_rel=0.01`、`tie_tol=1e-12`、`valley_ratio_def`、`directed_ratio_def`、`directed_ratio_role`、`selection_rule`），并在 fixed-site 自动说明 `tables/fixedsite_parity_note_{cn,en}.tex` 明确 `R_{dir}=g_{t2}/g_{t1}` 仅方向性诊断（可大于 1，不参与 phase 阈值）；中英文正文 `ring_two_walker_encounter_shortcut_{cn,en}.tex` 同步补入该口径说明。`code/check_encounter_consistency.py` 与 `tests/test_ring_two_walker_encounter_shortcut.py` 已新增对应守护并通过。执行链路：`.venv/bin/python reports/ring_two_walker_encounter_shortcut/code/two_walker_ring_encounter_report.py`（`real 10.79s`）、`.venv/bin/python reports/ring_two_walker_encounter_shortcut/code/check_encounter_consistency.py`（`real 0.08s`，`[ok]`）、`python3 scripts/reportctl.py build --report ring_two_walker_encounter_shortcut --lang en/cn`（`real 4.09s`，双语通过）、`.venv/bin/python -m pytest -q`（`18 passed`, `real 4.60s`）均通过。按分流策略本轮继续本地执行（显著低于 >20 分钟阈值，无大规模并行），未触发 Isambard 远端流程（`JOB_ID: N/A`, `REMOTE_DIR: N/A`；关键产物：`reports/ring_two_walker_encounter_shortcut/data/{case_summary,fixedsite_summary}.json`、`reports/ring_two_walker_encounter_shortcut/tables/fixedsite_parity_note_{cn,en}.tex`、`reports/ring_two_walker_encounter_shortcut/ring_two_walker_encounter_shortcut_{cn,en}.pdf`；下一步：继续本地闭环，若单轮预计 >20 分钟或转大规模并行再切 `isbard doctor/auth -> submit/status/fetch`）。
- 2026-03-03: 按“持续优化 `reports/ring_two_walker_encounter_shortcut/`，每轮重跑 codegen + 双语构建 + consistency + pytest，并优先修复峰比定义/多峰选峰/fixed-site parity 一致性”完成本轮本地闭环：`code/two_walker_ring_encounter_report.py` 将 detector 元数据 `peak_ratio_def` 统一为 `R_peak=min(g_t1,g_t2)/max(g_t1,g_t2)`（与正文检测轨迹口径一致），并在自动片段 `tables/fixedsite_parity_note_{cn,en}.tex` 显式补入候选评分公式 `R_{\mathrm{peak}}(\tau)` 到最终指标 `R_{\mathrm{peak}}(t_2)` 的衔接；中英文正文 `ring_two_walker_encounter_shortcut_{cn,en}.tex` 的“Unified Notation/符号与判据定义”同步补入“候选评分 -> 最终回写”说明，避免峰比定义与多峰选峰叙述漂移。`code/check_encounter_consistency.py` 与 `tests/test_ring_two_walker_encounter_shortcut.py` 已同步更新 `peak_ratio_def` 锚点并通过回归。执行链路：`.venv/bin/python reports/ring_two_walker_encounter_shortcut/code/two_walker_ring_encounter_report.py`（`real 7.62s`）、`python3 scripts/reportctl.py build --report ring_two_walker_encounter_shortcut --lang en`（`real 0.85s`）、`--lang cn`（`real 1.41s`）、`.venv/bin/python .../check_encounter_consistency.py`（`real 0.09s`）、`.venv/bin/python -m pytest -q tests/test_ring_two_walker_encounter_shortcut.py`（`7 passed`, `real 0.73s`）、`python3 scripts/update_research_summary.py`（`real 0.05s`）均通过。按分流策略本轮继续本地执行（显著低于 >20 分钟阈值），未触发 Isambard 远端流程（`JOB_ID: N/A`, `REMOTE_DIR: N/A`；关键产物：`reports/ring_two_walker_encounter_shortcut/data/{case_summary,fixedsite_summary}.json`、`reports/ring_two_walker_encounter_shortcut/tables/fixedsite_parity_note_{cn,en}.tex`、`reports/ring_two_walker_encounter_shortcut/ring_two_walker_encounter_shortcut_{cn,en}.pdf`）。
- 2026-03-03: 按“持续优化 `reports/ring_two_walker_encounter_shortcut/` 并优先修复峰比定义/多峰选峰/fixed-site parity 一致性”完成本轮本地闭环：`code/two_walker_ring_encounter_report.py` 将关键口径字符串常量化（`PEAK_RATIO_DEF`、`FIXEDSITE_COARSE_RULE`、`FIXEDSITE_TIME_MAP`），并在自动片段 `tables/fixedsite_parity_note_{cn,en}.tex` 明确补入 `f(0)=0 \Rightarrow \widetilde f(0)=0`（诊断从 `m>=1` 开始）以对齐 fixed-site parity 说明，同时修正中文片段结尾标点；`code/check_encounter_consistency.py` 与 `tests/test_ring_two_walker_encounter_shortcut.py` 同步新增该锚点守护，防止后续漂移。执行 `../../.venv/bin/python code/continuous_optimize_loop.py --rounds 1 --python ../../.venv/bin/python` 全通过（`codegen 9.99s`、`build_cn 1.99s`、`build_en 1.50s`、`py_compile 0.09s`、`consistency 0.05s`、`pytest 1.16s`、`summary 0.09s`，单轮 `14.88s`）；按分流策略本轮继续本地执行（明显低于 >20 分钟阈值），未触发 Isambard 远端流程（`JOB_ID: N/A`, `REMOTE_DIR: N/A`；关键产物：`reports/ring_two_walker_encounter_shortcut/tables/fixedsite_parity_note_{cn,en}.tex`、`reports/ring_two_walker_encounter_shortcut/outputs/loop/summary.json`）。
- 2026-03-03: 按“持续优化 `reports/ring_two_walker_encounter_shortcut/`，每轮重跑 codegen + 双语构建 + consistency + pytest，并优先修复峰比定义/多峰选峰/fixed-site parity 一致性”完成本轮闭环：`code/two_walker_ring_encounter_report.py` 的 `write_fixedsite_parity_note_snippets` 现显式写入 `g_m=\bar{\widetilde f}(m)`、score 公式 `\mathrm{score}(\tau)=((\tau-t_1)R_{\mathrm{peak}})/(R_{\mathrm{valley}}+10^{-12})` 与并列容差 `|\Delta\mathrm{score}|\le10^{-12}`；`code/check_encounter_consistency.py` 与 `tests/test_ring_two_walker_encounter_shortcut.py` 同步新增锚点守护。执行 `../../.venv/bin/python code/continuous_optimize_loop.py --rounds 1 --python ../../.venv/bin/python` 全通过（`codegen 10.12s`、`build_cn 4.87s`、`build_en 0.99s`、`py_compile 0.09s`、`consistency 0.08s`、`pytest 1.32s`、`summary 0.09s`，单轮 `17.56s`）；并复跑 `check_encounter_consistency.py` 与 `pytest -q tests/test_ring_two_walker_encounter_shortcut.py` 均通过。按分流策略本轮继续本地执行（低于 >20 分钟阈值），未触发 Isambard 远端流程（`JOB_ID: N/A`, `REMOTE_DIR: N/A`；关键产物：`reports/ring_two_walker_encounter_shortcut/tables/fixedsite_parity_note_{cn,en}.tex`、`reports/ring_two_walker_encounter_shortcut/outputs/loop/summary.json`）。
- 2026-03-03: 按“持续优化 `reports/ring_two_walker_encounter_shortcut/` 并优先修复峰比定义/多峰选峰/fixed-site parity 一致性”完成本轮新增强一致性闭环：`code/two_walker_ring_encounter_report.py` 为 anywhere/fixed-site 两条检测分支统一写出 detector 元数据（`peak_ratio_def`、`score_formula=score=(tau-t1)*R_peak/(R_valley+1e-12)`、`tie_break=larger_tau -> smaller_R_valley -> larger_R_peak`，fixed-site 额外含 `t_end_policy=no_extra_cutoff`）；自动片段 `tables/fixedsite_parity_note_{cn,en}.tex` 现显式写明 `R_peak=min/max`、并列选峰顺序与“无额外 `t_end` 截断”；`code/check_encounter_consistency.py` 与 `tests/test_ring_two_walker_encounter_shortcut.py` 同步新增守护并通过。执行 `../../.venv/bin/python code/continuous_optimize_loop.py --rounds 1` 全通过（`codegen 7.68s`、`build_cn 1.21s`、`build_en 0.65s`、`consistency 0.04s`、`pytest 0.48s`，单轮 `10.19s`）。按分流策略本轮继续本地执行（明显低于 >20 分钟阈值），未触发 Isambard 远端流程（`JOB_ID: N/A`, `REMOTE_DIR: N/A`；关键产物：`reports/ring_two_walker_encounter_shortcut/data/{case_summary,fixedsite_summary}.json`、`reports/ring_two_walker_encounter_shortcut/outputs/loop/summary.json`）。
- 2026-03-03: 按“持续优化 `reports/ring_two_walker_encounter_shortcut/` 并优先修复峰比定义/多峰选峰/fixed-site parity 一致性”完成新一轮本地闭环：中英文正文 `ring_two_walker_encounter_shortcut_{cn,en}.tex` 在 Phase 数学定义段补入与代码一致的并列打分 tie-break（`|\Delta score|<=10^{-12}` 时按“更晚 `\tau` → 更小 `R_valley` → 更大 `R_peak`”），并把机理段中 `R_dir` 统一表述为“仅方向性诊断，不参与 phase 阈值判别”；`code/check_encounter_consistency.py` 与 `tests/test_ring_two_walker_encounter_shortcut.py` 同步新增守护（新锚点必含、旧“consistent directed ratio/与晚峰方向一致”表述禁用）。执行 `../../.venv/bin/python code/continuous_optimize_loop.py --rounds 1` 全通过：`codegen 7.68s`、`build_cn 1.23s`、`build_en 0.63s`、`consistency 0.04s`、`pytest 0.51s`、`summary update 0.05s`，单轮 `10.21s`。按分流策略本轮继续本地执行（明显低于 >20 分钟阈值），未触发 Isambard 远端流程（`JOB_ID: N/A`, `REMOTE_DIR: N/A`，关键产物：`reports/ring_two_walker_encounter_shortcut/outputs/loop/summary.json`）。
- 2026-03-03: 继续按“每轮 codegen + 双语构建 + consistency + pytest”做 `reports/ring_two_walker_encounter_shortcut/` 一轮一致性修订：中英文正文 `ring_two_walker_encounter_shortcut_{cn,en}.tex` 在 **Phase 数学定义**中补入 fixed-site K=2 的显式约束 `\tau-t_1\ge\mathrm{min\_sep\_pair}`，并明确该分支在 parity 索引上选峰后按 `t=2m` 回映；`code/two_walker_ring_encounter_report.py` 的自动片段 `tables/fixedsite_parity_note_{cn,en}.tex` 同步写入“沿用主文同一 timescale 选峰口径（首峰 + score 选 `t_2`）”说明，避免“峰比定义/多峰选峰/fixed-site parity”三处文案漂移。`code/check_encounter_consistency.py` 与 `tests/test_ring_two_walker_encounter_shortcut.py` 新增对应守护锚点。执行链路全部通过：`.venv/bin/python reports/ring_two_walker_encounter_shortcut/code/two_walker_ring_encounter_report.py`（`real 7.75s`）、`python3 scripts/reportctl.py build --report ring_two_walker_encounter_shortcut --lang en/cn`（通过）、`.venv/bin/python reports/ring_two_walker_encounter_shortcut/code/check_encounter_consistency.py`（通过）、`.venv/bin/python -m pytest -q tests/test_ring_two_walker_encounter_shortcut.py`（`7 passed`）。按分流策略本轮继续本地执行（明显低于 >20 分钟阈值），未触发 Isambard 远端流程（`JOB_ID: N/A`, `REMOTE_DIR: N/A`；关键产物：`reports/ring_two_walker_encounter_shortcut/ring_two_walker_encounter_shortcut_{cn,en}.pdf`、`reports/ring_two_walker_encounter_shortcut/tables/fixedsite_parity_note_{cn,en}.tex`）。
- 2026-03-03: 按“持续优化 `reports/ring_two_walker_encounter_shortcut/`，每轮重跑 codegen + 双语构建 + consistency + pytest，并优先修复峰比定义/多峰选峰/fixed-site parity 一致性”完成新一轮本地闭环：`code/two_walker_ring_encounter_report.py` 将主扫描表 `encounter_scan_table.tex` 的“未检出第二峰”行改为 `peak/valley=--`（不再输出占位 `0/1`）；中英文正文 `ring_two_walker_encounter_shortcut_{cn,en}.tex` 在“符号总览”中把 `anywhere` 与 `fixed-site K=2` 的选峰窗口径并列写明（`anywhere` 使用 `[t_ignore,t_end]`，`fixed-site` 在 parity 索引上仅施加 `t_ignore_pair/min_sep_pair` 且不额外截断 `t_end`，最终统一按 `t=2m` 回映）；`code/check_encounter_consistency.py` 与 `tests/test_ring_two_walker_encounter_shortcut.py` 同步新增守护（扫描表缺峰对必须 `--`、定义段新锚点必须存在）。执行 `../../.venv/bin/python code/continuous_optimize_loop.py --rounds 1 --python ../../.venv/bin/python` 全通过（`codegen 7.61s`、`build_cn 1.16s`、`build_en 0.63s`、`consistency 0.04s`、`pytest 0.52s`，单轮 `10.07s`）；按分流策略继续本地执行（明显低于 >20 分钟阈值），未触发 Isambard 远端流程（`JOB_ID: N/A`, `REMOTE_DIR: N/A`）。
- 2026-03-03: 按“持续优化 `reports/ring_two_walker_encounter_shortcut/` 并优先修复峰比定义/多峰选峰/fixed-site parity 一致性”完成本轮闭环：`code/two_walker_ring_encounter_report.py` 新增自动片段 `tables/fixedsite_parity_note_{cn,en}.tex`，fixed-site clear 占比改为由 `fixedsite_summary.json` 实时回填（不再硬编码 `157/169=0.929`）；`encounter_key_metrics.tex` 与自动摘要统一把 `R_dir` 标记为“diagnostic only/仅方向性诊断”，与 phase/onset 主判据 `R_peak(min/max)+R_valley` 对齐。中英文正文 `ring_two_walker_encounter_shortcut_{cn,en}.tex` 已改为 `\\input{\\TabDir/fixedsite_parity_note_{cn,en}.tex}`；`code/check_encounter_consistency.py` 与 `tests/test_ring_two_walker_encounter_shortcut.py` 同步新增守护（新片段存在、主文输入锚点、旧硬编码禁用、clear 比例与 JSON 一致）。执行链路：codegen `real 11.54s`、CN `latexmk -xelatex` `real 2.63s`、EN `latexmk -pdf` `real 0.77s`、consistency `real 0.08s`、报告专测 `pytest` `real 1.29s`、仓库级 `pytest -q` `real 3.26s` 均通过。按分流策略本轮继续本地执行（无大规模并行且远低于 >20 分钟阈值），未触发 Isambard 远端流程（`JOB_ID: N/A`, `REMOTE_DIR: N/A`）；下一步继续该本地闭环，若转大规模参数扫描或预计单轮 >20 分钟再切换 `isbard doctor/auth + submit/status/fetch`。
- 2026-03-03: 按“持续优化 `reports/ring_two_walker_encounter_shortcut/`（每轮重跑 codegen + 双语构建 + consistency check + pytest）并优先修复峰比定义/多峰选峰/fixed-site parity 一致性”完成本轮闭环：中英文正文 `ring_two_walker_encounter_shortcut_{cn,en}.tex` 的多峰选峰规则现显式区分 `anywhere` 与 `fixed-site K=2` 分支（`anywhere` 使用 `[t_{ignore},t_{end}]`，`fixed-site` 仅用 `t_{ignore,pair}/min_sep_pair` 且不额外施加 `t_{end}` 截断，最终统一按 `t=2m` 回映）；并把并列分数容差写明为 `|\Delta score|<=10^{-12}`。`code/check_encounter_consistency.py` 同步新增/更新锚点守护（含上述容差与 fixed-site 无 `t_{end}` 截断语句）。执行链路：`.venv/bin/python reports/ring_two_walker_encounter_shortcut/code/two_walker_ring_encounter_report.py` 通过、`.venv/bin/python .../check_encounter_consistency.py` 通过、中文 `latexmk -xelatex` 与英文 `latexmk -pdf` 构建通过、仓库级 `pytest -q` 全通过。按分流策略本轮继续本地执行（单轮明显 <10 分钟），未触发 Isambard 远端流程（`JOB_ID: N/A`, `REMOTE_DIR: N/A`）；下一步继续该本地闭环，若转大规模并行或预计单轮 >20 分钟再切换 `isbard doctor/auth + submit/status/fetch`。
- 2026-03-03: 按“持续优化 `reports/ring_two_walker_encounter_shortcut/`，每轮重跑 codegen + 双语构建 + consistency + pytest，并优先修复峰比定义/多峰选峰/fixed-site parity 一致性”完成本轮增强：`code/check_encounter_consistency.py` 新增数值口径守护（代表点强校验 `peak_ratio=min(h1,h2)/max(h1,h2)`、`peak_ratio_dir=h2/h1`）及 fixed-site parity 守护（`examples/scan` 中非空 `t1/t2/tv` 必须为偶数并满足时序约束）；`tests/test_ring_two_walker_encounter_shortcut.py` 新增/加强回归（同口径比值断言、fixed-site 偶数映射断言、timescale 检测器 ratio contract、`select_timescale_t2` 并列打分晚时标优先 tie-break）。执行 `../../.venv/bin/python code/continuous_optimize_loop.py --rounds 1 --python ../../.venv/bin/python` 全通过（`codegen 7.60s`、`build_cn 1.19s`、`build_en 0.65s`、`consistency 0.04s`、`pytest 0.49s`、单轮 `10.08s`）；按分流策略继续本地执行（明显低于 >20 分钟阈值），未触发 Isambard 远端流程（`JOB_ID: N/A`, `REMOTE_DIR: N/A`）。下一步继续该闭环，若转大规模并行或单轮预计超阈值再切换 `isbard doctor/auth + submit/status/fetch`。
- 2026-03-03: 按“持续优化 `reports/ring_two_walker_encounter_shortcut/`，每轮重跑 codegen + 双语构建 + consistency check + pytest，并优先修复峰比定义/多峰选峰/fixed-site parity 一致性”完成本轮本地闭环：`.venv/bin/python reports/ring_two_walker_encounter_shortcut/code/two_walker_ring_encounter_report.py` 重跑通过（`real 7.82s`），英文报告构建通过（`latexmk -pdf ... ring_two_walker_encounter_shortcut_en.tex`），中文报告按 `xeCJK` 要求使用 `latexmk -xelatex ... ring_two_walker_encounter_shortcut_cn.tex` 构建通过；`code/check_encounter_consistency.py` 与 `pytest`（报告专测 + 仓库级）均通过。三类一致性复核结果：`R_{\mathrm{peak}}` 继续保持 min/max 主口径且 `R_{\mathrm{dir}}` 仅作方向性诊断；multi-peak `t_2` 继续使用 timescale score + tie-break（晚时标优先，再比较 valley/peak）；fixed-site K=2 继续保持 `g=\bar{\widetilde f}` 检测与 `t=2m` 时间映射。按分流策略本轮继续本地执行（明显低于 >20 分钟阈值），未触发 Isambard 远端流程（`JOB_ID: N/A`, `REMOTE_DIR: N/A`）；下一步保持同节奏迭代，若转大规模并行或单轮预计超阈值再走 `isbard doctor/auth + submit/status/fetch`。
- 2026-03-03: 按“持续优化 `reports/ring_two_walker_encounter_shortcut/`，优先修复峰比定义/多峰选峰/fixed-site parity 一致性”完成本轮修复并闭环回归：中英文正文 `ring_two_walker_encounter_shortcut_{cn,en}.tex` 将前置定义里的谷时刻统一为检测轨迹口径 `t_v=\arg\min_{t_1<t<t_2} g_t`（不再混用 `\bar f`），与 `R_{\mathrm{peak}}/R_{\mathrm{valley}}` 的 `g` 口径保持一致；`code/two_walker_ring_encounter_report.py` 把 `detect_two_peak_metrics_k2_coarse` 的默认 `min_ratio` 调整为 `0.10`，与 fixed-site K=2 文稿阈值和 summary 配置对齐；`code/check_encounter_consistency.py` 与 `tests/test_ring_two_walker_encounter_shortcut.py` 新增 `t_v` 新写法必含/旧写法禁用守护。执行链路：`code/two_walker_ring_encounter_report.py`（`real 9.68s`）+ 中英文构建 + consistency check + pytest（`5 passed`）均通过；随后 `code/continuous_optimize_loop.py --rounds 1` 单轮全绿（`duration=10.33s`，含 codegen/build/py_compile/consistency/pytest/summary update）。按分流策略本轮继续本地执行（明显低于 >20 分钟阈值），未触发 Isambard 远端流程（`JOB_ID: N/A`, `REMOTE_DIR: N/A`）；下一步继续本地轮询，若转大规模并行或预计超阈值则先 `isbard doctor/auth` 再 `submit/status/fetch`。
- 2026-03-03: 按“持续优化 `reports/ring_two_walker_encounter_shortcut/`，并优先修复峰比定义/多峰选峰/fixed-site parity 一致性”完成新一轮本地闭环：中英文正文 `ring_two_walker_encounter_shortcut_{cn,en}.tex` 把峰谷指标与 multi-peak 打分公式统一改写为检测轨迹 `g` 口径（`R_{\mathrm{peak}}(\tau),R_{\mathrm{dir}},R_{\mathrm{valley}}` 全部用 `g` 表达），并在选峰规则段显式声明 `anywhere: g=\bar f`、`fixed-site K=2: g=\bar{\widetilde f}`（按 `t=2m` 回映）；`code/check_encounter_consistency.py` 新增“应包含 `g` 公式/不应回退到 `\bar f` 旧公式”的双向守护；`tests/test_ring_two_walker_encounter_shortcut.py` 同步增加回归断言。执行链路：`code/two_walker_ring_encounter_report.py`（`real 7.89s`）+ CN/EN 构建（`real 1.23s/0.77s`）+ consistency check（`real 0.07s`）+ pytest（`5 passed`, `real 0.58s`）+ `scripts/update_research_summary.py`（`real 0.07s`）均通过。按分流策略本轮继续本地快测（显著低于 >20 分钟阈值），未触发 Isambard 远端 `submit/status/fetch`（`JOB_ID: N/A`, `REMOTE_DIR: N/A`）；关键产物路径：`reports/ring_two_walker_encounter_shortcut/ring_two_walker_encounter_shortcut_cn.tex`、`reports/ring_two_walker_encounter_shortcut/ring_two_walker_encounter_shortcut_en.tex`、`reports/ring_two_walker_encounter_shortcut/code/check_encounter_consistency.py`、`tests/test_ring_two_walker_encounter_shortcut.py`；下一步动作：继续本地轮询，若单轮预计 >20 分钟或转大规模并行扫描则先 `isbard doctor/auth` 再 `submit/status/fetch`。
- 2026-03-03: 按“持续自动优化 `reports/grid2d_membrane_near_target`（clear-double 实例图 + committor 机理 + 总结后续 + codegen/双语构建巡检）”完成新一轮闭环：`code/membrane_near_target_report.py` 新增 no-corridor clear-instance 的强 gate 审计（`primary_clear_gate`、`primary_gate_audit`、`primary_gate_pass`、`primary_gate_min_slack`）并写入 `data/summary.json`，`tables/two_target_no_corridor_clear_instance.tex` 同步新增 `gate-pass/gate-slack` 列；当前 clear-instance 仍为 `spec=adaptive_refine, (b_x,d,\Delta y)=(0.12,4,1)`，`gate-pass=yes`，`gate-slack≈0.070`，图文件 `figures/two_target_no_corridor_clear_instance.pdf` 存在且 `size_bytes=25640`。中英文文稿 `grid2d_membrane_near_target_{cn,en}.tex` 新增 committor 谱分解双时标说明（`Q^{t-1}` 模态展开）并把后续自动质检项扩展为 `min-margin/gate-slack`。本轮本地执行耗时：codegen `real 69.79s`，CN/EN 构建 `real 1.43s/1.05s`，继续满足“本地 <10 分钟优先”；未触发 Isambard 远端提交流程（`JOB_ID: N/A`, `REMOTE_DIR: N/A`, 关键产物路径：`reports/grid2d_membrane_near_target/data/summary.json`、`reports/grid2d_membrane_near_target/tables/two_target_no_corridor_clear_instance.tex`、`reports/grid2d_membrane_near_target/grid2d_membrane_near_target_{cn,en}.pdf`，下一步动作：继续本地轮询，若预计单轮 >20 分钟则先 `isbard doctor/auth` 后走 `submit/status/fetch`）。同时发现 keepalive round-3 因 OneDrive 权限报错失败（`Operation not permitted`），已用 `./scripts/ka start-as-local optimize grid2d_membrane_near_target_autoopt ...` 重启，当前 `local_runner_alive: yes`。
- 2026-03-03: 按“持续自动优化 `reports/grid2d_membrane_near_target/`（clear-double 实例图、committor 机理、总结后续、codegen+双语构建巡检）”完成本轮执行与持续任务重启：本地完整回归 `code/membrane_near_target_report.py` `real 68.51s`，随后 `latexmk` 中英构建均通过（CN `real 2.19s`，EN `real 0.78s`），满足“本地 <10 分钟优先”条件。新 keepalive 任务已统一为 `./scripts/ka start-as-local optimize grid2d_membrane_near_target_opt ...`，当前状态 `local_runner_alive: yes`（为规避 OneDrive 路径下 launchd 的 `Operation not permitted` 限制，已从 launchd 模式切换为 local runner）。按分流策略本轮未触发 Isambard 远端提交（`JOB_ID: N/A`, `REMOTE_DIR: N/A`）；下一步由 keepalive 持续执行并在出现大规模扫描（预计单轮 >20 分钟）时自动转入 `isbard doctor/auth + submit/status/fetch` 路径。
- 2026-03-03: 按“持续优化 `reports/ring_two_walker_encounter_shortcut/`，每轮重跑 codegen + 双语构建 + consistency + pytest，并优先修复峰比定义/多峰选峰/fixed-site parity 一致性”完成新一轮本地闭环：`code/two_walker_ring_encounter_report.py` 将 fixed-site K=2 检测参数显式化并写入 `data/fixedsite_summary.json`（`mode=timescale`, `smooth_window=9`, `t_ignore_pair=18`, `min_sep_pair=8`, `min_ratio=0.10`, `max_valley_ratio=0.90`, `time_map=t=2m`），同时把 `detect_two_peak_metrics_k2_coarse` 默认 `t_ignore_pair` 与正文口径统一为 `18`；中英文文稿 `ring_two_walker_encounter_shortcut_{cn,en}.tex` 新增两条一致性说明：fixed-site 在 `g_m=\bar{\widetilde f}(m)` 上执行同一检测器并按 `t=2m` 回映，且 phase/onset 与多峰 score 只使用 `R_peak(min/max)` + `R_valley`，`R_dir` 仅作方向性诊断；`code/check_encounter_consistency.py` 与 `tests/test_ring_two_walker_encounter_shortcut.py` 同步新增守护以锁定以上口径。执行 `../../.venv/bin/python code/continuous_optimize_loop.py --rounds 1 --python ../../.venv/bin/python` 全通过（单轮 `12.03s`，步骤全绿）。按分流策略本轮继续本地快测（远低于 10 分钟），未触发 Isambard `submit/status/fetch`（`JOB_ID: N/A`, `REMOTE_DIR: N/A`）。
- 2026-03-03: 按“持续自动优化 `reports/grid2d_membrane_near_target/`（no-corridor clear-double 图 + committor 机理 + 总结后续 + 持续构建巡检）”完成本轮增强：`code/membrane_near_target_report.py` 新增 clear-instance 图完整性硬校验（`two_target_no_corridor_clear_instance.pdf` 必须存在且文件大小 `>2KB`，否则直接失败），并把图路径/存在性/文件大小写入 `data/summary.json`（当前 `path=figures/two_target_no_corridor_clear_instance.pdf`，`size_bytes=25640`）；中英文文稿 `grid2d_membrane_near_target_{cn,en}.tex` 的 splitting committor 段补充“有界鞅 + 可选停时”闭环推导（`q_far(x_s)=P_far`）并同步更新总结条目。执行链路：本地 codegen `real 66.69s`，CN/EN `latexmk` 分别 `real 1.48s/1.36s` 全通过，继续满足“本地 <10 分钟优先”；未触发 Isambard `submit/status/fetch`（无 `JOB_ID`、无 `REMOTE_DIR`），现有 keepalive 任务 `grid2d_membrane_near_target` 保持 `local_runner_alive: yes`。
- 2026-03-03: 按“持续自动优化 `reports/grid2d_membrane_near_target/`（clear-double 图、committor 机理、总结后续、codegen+双语构建巡检）”完成本轮闭环：`code/membrane_near_target_report.py` 的 `plot_two_target_doublepeak_example` 增强 no-corridor clear-instance 图注（新增 `peak-ratio` 与 `selection_gate` 展示，并下移 `p1 clipped` 注释避免遮挡），当前 clear 图稳定展示 `spec=adaptive_refine, (b_x,d,\Delta y)=(0.12,4,1)` 且 gate 为 `peak>=0.07,min>=0.07,valley<=0.10`；中英文文稿同步更新 headline 数值、committor Neumann 展开（把 `(I-P_{UU})^{-1}` 与 renewal 失败-重试图景直接对齐）以及总结/后续段落。执行链路：本地 codegen（约 `68s`）+ CN/EN `latexmk` 全通过；期间 EN 构建曾遇到 `build/*.aux` 断裂行导致的 `Missing \begin{document}`，已通过重置 `build/grid2d_membrane_near_target_en.aux` 并重编修复。按分流策略本轮继续本地执行（明显 <10 分钟），未触发 Isambard 远端 `submit/status/fetch`（无 `JOB_ID`、无 `REMOTE_DIR`）。
- 2026-03-03: 按“持续优化 `reports/ring_two_walker_encounter_shortcut/` 且优先修复峰比定义/多峰选峰/fixed-site parity 一致性”完成新一轮本地闭环：`two_walker_ring_encounter_report.py` 将 fixed-site 示例表中“未检出第二峰”的比值从数值占位改为 `--`（避免把未定义误读成 `0/1`）；中英文文稿 `ring_two_walker_encounter_shortcut_{cn,en}.tex` 同步补充该约定（并保留 `t=2m` parity 映射说明）；`check_encounter_consistency.py` 与 `tests/test_ring_two_walker_encounter_shortcut.py` 新增守护，强制“`t_1/t_2` 缺失行必须输出 `--` 比值”。本轮执行：codegen（`real 8.28s`）、双语构建、consistency check、pytest（`5 passed`）均通过；按分流策略继续本地快测，未触发 Isambard 远端 `submit/status/fetch`（无 `JOB_ID` / `REMOTE_DIR`）。
- 2026-03-03: 按“持续优化 `reports/ring_two_walker_encounter_shortcut/`，每轮重跑 codegen + 双语构建 + consistency + pytest，并优先修复峰比定义/多峰选峰/fixed-site parity 一致性”完成本轮闭环：`two_walker_ring_encounter_report.py` 将 fixed-site 指标表头统一为 `peak balance ratio (\bar{\tilde f}, min/max)`；中英文文稿 `ring_two_walker_encounter_shortcut_{cn,en}.tex` 将统一定义改为函数式 `R_{\mathrm{peak}}(\tau)` 并显式写出 `R_{\mathrm{peak}}=R_{\mathrm{peak}}(t_2)`，fixed-site 段统一为“peak-balance/峰平衡比”表述；`check_encounter_consistency.py` 新增对应锚点守护（含 `R_{\mathrm{valley}}(\tau)+10^{-12}` 与 `t=2m` 右端点映射片段）。执行 `../../.venv/bin/python code/continuous_optimize_loop.py --rounds 1 --python ../../.venv/bin/python` 全通过（单轮 `10.34s`；codegen/build_cn/build_en/py_compile/consistency/pytest/summary update 全绿）。按策略继续本地快测，未触发 Isambard 远端 `submit/status/fetch`（无 `JOB_ID` / `REMOTE_DIR`）。
- 2026-03-03: 按“持续自动优化 `reports/grid2d_membrane_near_target/`（clear-double 图、committor 机理、总结后续、codegen+双语构建巡检）”完成本轮闭环：`code/membrane_near_target_report.py` 新增 no-corridor 两目标 `adaptive_refine` 自适应局部细化扫描（围绕高分候选做 `bx/near_dx/near_dy` 微调）并并入 clear-instance 自动选点；clear-instance 更新为 `spec=adaptive_refine, (b_x,d,\Delta y)=(0.12,4,1)`，`sep≈2.38`、`valley/max≈0.007`、`peak-margin≈0.070`、`min-margin≈0.070`、`showcase≈1.92`。中英文方法段进一步补充 Doob 变换条件化核（把边值问题、首达核与峰谷转移机制闭环到同一动力学框架）。同时修复 `two_target_no_corridor_clear_instance.tex` 中 `spec` 下划线未转义导致的 CN/EN LaTeX 失败，现 codegen 与双语构建均通过（本地 codegen `real 67.43s`，EN/CN `latexmk` 均 `RC=0`）。本轮按分流策略继续本地执行（单轮明显 <10 分钟），未触发 Isambard 远端 `submit/status/fetch`（无 `JOB_ID`、无 `REMOTE_DIR`）。
- 2026-03-03: 按“持续自动优化 `reports/grid2d_membrane_near_target/`（no-corridor clear double 图 + committor 机理 + 总结后续 + 持续构建巡检）”完成新一轮闭环：本地先跑 `../../.venv/bin/python code/membrane_near_target_report.py`（`real 57.19s`），再跑 `latexmk` 中英构建（CN `real 2.21s`，EN `real 1.36s`）均通过，满足“本地 <10 分钟优先”分流条件，因此未触发 Isambard `submit/status/fetch`（无 `JOB_ID` / `REMOTE_DIR`）。本轮脚本 `code/membrane_near_target_report.py` 新增 `two_target_splitting_committor_qc.tex` 自动质检表（代表点 + clear-instance 同报 `q_far(x_s)`、`P_far`、`\varepsilon_split` 与残差范数），并将 clear-instance 选点门槛升级为“`peak/min margin` + 深谷优先（`valley<=0.12`）”；中英文文稿新增“线性系统 $\leftrightarrow$ 首达核”闭环公式链与新质检表引用，运行时叙述更新为“约 60s/轮”。持续任务维持 `./scripts/ka start-as-local optimize grid2d_membrane_near_target_autoopt ...`（`gpt-5.3-codex`, `xhigh`）并由 local runner 持续执行。 
- 2026-03-03: 按“持续优化 `reports/ring_two_walker_encounter_shortcut/`，优先修复峰比定义/多峰选峰/fixed-site parity 说明一致性”完成新一轮闭环：`code/two_walker_ring_encounter_report.py` 将 fixed-site 表头时间映射从 `t\approx2m` 明确为 `t=2m`，并把有向峰比标签统一成检测轨迹口径 `\bar f(t_2)/\bar f(t_1)`；中英文文稿 `ring_two_walker_encounter_shortcut_{cn,en}.tex` 将 multi-peak 并列打分 tie-break 说明补齐为“先更晚 `t_2`，再更小 valley ratio，再更大 peak ratio”；`code/check_encounter_consistency.py` 同步新增对应锚点校验。执行 `../../.venv/bin/python code/continuous_optimize_loop.py --rounds 1` 全通过（codegen/build_cn/build_en/py_compile/consistency/pytest/update summary，单轮 `10.60s`）；按策略继续本地快测，未触发 Isambard 远端 `submit/status/fetch`（无 JOB_ID/REMOTE_DIR）。
- 2026-03-03: 按“持续优化 `reports/ring_two_walker_encounter_shortcut/` 且优先修复峰比定义/多峰选峰/fixed-site parity 一致性”完成新一轮闭环：`code/two_walker_ring_encounter_report.py` 的 timescale 选峰新增并列打分 tie-break（分数容差内优先更晚 `t_2`，再比较 valley/peak 比），并把 fixed-site 指标表头显式改为 `\bar{\tilde f}` 口径；中英文文稿 `ring_two_walker_encounter_shortcut_{cn,en}.tex` 统一声明“峰谷指标基于平滑检测轨迹 `\bar f` / `\bar{\tilde f}` 计算”、multi-peak 公式同步改为 `\bar f` 形式，并补充 tie-break 文案与 fixed-site 时间映射 `t=2m`；`code/check_encounter_consistency.py` 同步升级锚点校验。执行 `../../.venv/bin/python code/continuous_optimize_loop.py --rounds 1` 全通过（codegen/build_cn/build_en/py_compile/consistency/pytest/update summary，单轮 `10.72s`）；本轮按策略走本地快测，未触发 Isambard 远端 `submit/status/fetch`（无 JOB_ID/REMOTE_DIR）。
- 2026-03-03: 按“持续自动优化 `reports/grid2d_membrane_near_target/` 并按阈值分流 Isambard”完成一轮端到端增强：先执行 `isbard doctor`（`SSH_OK`）与别名检查（`b35cz.3.isambard` 可用），再实测本地单轮 codegen `57.26s`（明显 <10 分钟），因此按策略继续本地而未触发 `isbard submit/status/fetch`（无 JOB_ID / REMOTE_DIR）。本轮把 no-corridor splitting committor 质检从“仅代表点”扩展到“代表点 + clear-instance”双路径：`summary.json` 新增 `two_target_no_corridor.splitting_committor_rep` 与 `splitting_committor_clear_instance`，并将 clear-instance 的闭环误差 `\varepsilon_split` 写入 `tables/two_target_no_corridor_clear_instance.tex`（当前 `1.14×10^-9`，代表点约 `1.97×10^-8`）。中英文文稿同步更新机理段与总结/后续方向（强调双路径闭环与自动 QC），`latexmk` EN/CN 构建均通过。持续任务已重启为 `./scripts/ka start-as-local optimize grid2d-membrane-near-target-opt-v2 ...`，当前 `local_runner_alive: yes`，持续执行 codegen + 双语构建巡检。
- 2026-03-03: 按“持续优化 `reports/ring_two_walker_encounter_shortcut/`，每轮重跑 codegen + 双语构建 + consistency + pytest，并优先修复峰比定义/多峰选峰/fixed-site parity 一致性”完成新一轮本地闭环：`two_walker_ring_encounter_report.py` 统一将扫描表头与曲线标签显式写为 `peak balance ratio (min/max)`；中英文正文的多峰选峰规则补成符号化定义 `R_\mathrm{peak}(\tau)=\min/\max` 并写入 score 公式（与代码 `score=(\tau-t_1)R_\mathrm{peak}/(R_\mathrm{valley}+1e-12)` 一致）；fixed-site parity 段补充“峰谷指标均在粗粒化轨迹 `\tilde f(m)` 上计算，避免奇偶微振荡直驱相位”。一致性守护 `check_encounter_consistency.py` 与回归测试 `tests/test_ring_two_walker_encounter_shortcut.py` 新增对应片段检查；`code/continuous_optimize_loop.py` 每轮新增 `scripts/update_research_summary.py` 自动刷新步骤。执行 `.venv/bin/python reports/ring_two_walker_encounter_shortcut/code/two_walker_ring_encounter_report.py`（`real 7.68s`）、`latexmk` 中英双语构建（`real 3.49s/1.28s`）、`code/check_encounter_consistency.py`（`real 0.22s`）、`pytest -q tests/test_ring_two_walker_encounter_shortcut.py`（`5 passed`, `real 2.99s`）均通过；未触发 Isambard 远端分支（无 JOB_ID / REMOTE_DIR）。
- 2026-03-03: 对 `reports/grid2d_membrane_near_target/` 完成新一轮“no-corridor clear-double + committor 机理质检”优化：`code/membrane_near_target_report.py` 新增 committor 残差诊断（内点 Bellman 残差与边界残差）并写入 `data/summary.json`；no-corridor clear-instance 选点升级为“先稳健门槛筛选（`peak-margin>=0.05` 且 `min-margin>=0.05`，若不足再逐级放宽）再按 showcase-score 排序”，当前 clear-instance 更新为 `spec=baseline, (b_x,d,\Delta y)=(0.12,3,2)`，`sep≈2.41`、`valley/max≈0.005`、`peak_ratio≈0.166`、`min-margin≈0.066`。清晰实例表升级为含 `peak-margin/min-margin/showcase`，中英文正文“总结与后续方向”同步补充 residual 质检与持续构建策略，`grid2d_membrane_near_target_{cn,en}.pdf` 已重编通过。按路由策略本轮走本地（单轮 codegen `56.68s`），未触发 Isambard `submit/status/fetch`（无 JOB_ID/REMOTE_DIR）。
- 2026-03-03: 按“持续优化 `reports/ring_two_walker_encounter_shortcut/` 且优先修复峰比定义/多峰选峰/fixed-site parity 一致性”完成新一轮闭环：`two_walker_ring_encounter_report.py` 将 ring-size `N` 扫描统一切换为 `timescale` 主检测器（与正文主口径一致，含按 `N` 比例缩放的 `t_end`），并把 fixed-site `K=2` parity 粗粒化检测改为同一“首峰 + score 选 `t_2`”规则；`R_peak=min/max`、`R_dir=f(t_2)/f(t_1)`、`R_valley` 口径保持统一。自动摘要 `encounter_nscan_summary_{cn,en}.tex` 已显式注明该同口径规则；全链路执行 `.venv/bin/python reports/ring_two_walker_encounter_shortcut/code/continuous_optimize_loop.py --rounds 1` 通过（codegen/build_cn/build_en/py_compile/consistency/pytest，单轮 `10.56s`）。按策略本轮继续本地执行，未触发 Isambard `submit/status/fetch`（无 JOB_ID/REMOTE_DIR）。
## 仓库速览（结构 + 入口）
```
valley-k-small/
  research/
    reports/        # 报告、文稿、研究资产
    docs/           # 研究总览、日志、提交材料
    archives/       # 历史 runs 与归档
  platform/
    web/            # Next.js 站点与预计算数据
    tools/          # repo/web/automation 实现
    schemas/        # 数据契约
    skills/         # continuation skill
    agent/          # agent 引导文档
    runtime/        # 本地日志与运行时产物
  packages/
    vkcore/src/vkcore/  # 共享 Python 核心库
  scripts/          # 兼容脚本入口
```

## 研究核心
- 主题: 环网络（ring / lazy ring）+ 单条**有向 shortcut**下的首达时间（first-passage time, FPT）分布与双峰/谷结构（bimodality/valley）。
- 目标: 在不同模型构造（lazy vs non-lazy、selfloop vs renormalize vs equal4）与参数扫描（N, K, beta, dst）下，识别双峰出现的条件，并解释其机制。
- 方法: 解析生成函数 + Abate--Whitt (AW) 反演、time-domain flux/master equation 校验、MC 轨迹分类与统计。

## 模型与术语统一（便于统一提问）
- Ring: N 个节点，K=2k 邻居（±1...±k）。
- Lazy: 每步以概率 q 做 ring move，以 1-q 停留（self-loop）。
- Shortcut 构造:
  - selfloop 规则: 从 self-loop 概率中取出 p 并赋给 shortcut，p=beta(1-q)。
  - renormalize 规则: 在源节点新增 shortcut，并将所有出边重归一到 1/(K+1)（non-lazy 报告常用）。
  - equal4 规则: 源节点四动作（stay/left/right/shortcut）各 1/4。
- 吸收: 目标节点为吸收态；rho=1 为严格首达。
- 双峰判据（paper-style）: 严格局部峰 + 峰高阈值 h_min(默认 1e-7)；次峰高度 ≥ 主峰 1%；可选宏观判据 t2/t1 ≥ 10。
- Jump-over: K>=4 时，ring move 可跨过 target 而不落在其上；作为延迟机制被单独统计。

## 关键符号速查
- n0: 起点；target: 吸收点；src/dst: shortcut 起点/终点。
- f(t): 首达时间 pmf；S(t): survival；t1,t2: 前两峰；t_valley: 两峰间谷底。
- R = A(t2)/A(t1): 第二峰相对高度（valley_dst 常用）。
- 对 `reports/ring_two_walker_encounter_shortcut/`：主口径使用检测轨迹通式 `R_\mathrm{peak}=\min(g_{t_1},g_{t_2})/\max(g_{t_1},g_{t_2})` 与 `R_\mathrm{dir}=g_{t_2}/g_{t_1}` 并行汇报；其中 anywhere 取 `g=\bar f`，fixed-site K=2 取 `g=\bar{\widetilde f}`（并按 `t=2m` 回映），避免“峰平衡”与“方向性”混淆。
- hv_over_max: 谷底/峰值比例（lazy_jump_ext 用于筛选代表性 beta）。
- gamma: 尾部衰减率（log S(t) 线性斜率；lazy_jump_ext 讨论）。

## 快速复现（关键命令）
这些命令足以复现主要结果；都在各报告目录内运行。

valley（non-lazy + renormalize）:
```
cd reports/ring_valley
python3 code/valley_study.py
latexmk -pdf -interaction=nonstopmode -halt-on-error -auxdir=build -emulate-aux-dir ring_valley.tex
```

valley_dst（dst 扫描）:
```
cd reports/ring_valley_dst
python3 code/dst_shortcut_usage_mc.py --help
python3 code/bimodality_flux_scan.py --help
latexmk -xelatex -interaction=nonstopmode -halt-on-error -auxdir=build -emulate-aux-dir ring_valley_dst_cn.tex
```

lazy_flux（K=2 lazy + Chebyshev + AW + flux）:
```
cd reports/ring_lazy_flux
python3 code/lazy_ring_flux_bimodality.py --help
latexmk -xelatex -interaction=nonstopmode -halt-on-error -auxdir=build -emulate-aux-dir ring_lazy_flux_cn.tex
```

lazy_jump（K=2 vs K=4 jump-over）:
```
cd reports/ring_lazy_jump
python3 code/jumpover_bimodality_pipeline.py --help
latexmk -xelatex -interaction=nonstopmode -halt-on-error -auxdir=build -emulate-aux-dir ring_lazy_jump_cn.tex
```

lazy_jump_ext（beta/N sweep + tail）:
```
cd reports/ring_lazy_jump_ext
python3 code/beta_sweep_peaks_tail.py --help
python3 code/N_sweep_peaks_tail.py --help
latexmk -xelatex -interaction=nonstopmode -halt-on-error -auxdir=build -emulate-aux-dir ring_lazy_jump_ext_cn.tex
```

2d_bimodality（2D lattice biased/lazy FPT 双峰）:
```
cd reports/grid2d_bimodality
python3 code/bimodality_2d_pipeline.py --help
latexmk -xelatex -interaction=nonstopmode -halt-on-error -auxdir=build -emulate-aux-dir grid2d_bimodality_cn.tex
```

2d_reflecting_bimodality（2D lattice reflecting-boundary FPT 双峰）:
```
cd reports/grid2d_reflecting_bimodality
python3 code/reflecting_bimodality_pipeline.py
latexmk -xelatex -interaction=nonstopmode -halt-on-error -auxdir=build -emulate-aux-dir grid2d_reflecting_bimodality_cn.tex
```

2d_blackboard_bimodality（黑板图反射边界双峰）:
```
cd reports/grid2d_blackboard_bimodality
python3 code/blackboard_bimodality_pipeline.py --cases Z,S
python3 code/z_scan.py
latexmk -xelatex -interaction=nonstopmode -halt-on-error -auxdir=build -emulate-aux-dir grid2d_blackboard_bimodality_cn.tex
```

2d_two_target_double_peak（2D 双 target double peak 条件）:
```
cd reports/grid2d_two_target_double_peak
python3 code/two_target_2d_report.py
latexmk -xelatex -interaction=nonstopmode -halt-on-error -auxdir=build -emulate-aux-dir grid2d_two_target_double_peak_cn.tex
```

lazy_jump_ext_rev2（同轴叠加 + 敏感性分析）:
```
cd reports/ring_lazy_jump_ext_rev2
make fig2
make sensitivity
latexmk -xelatex -interaction=nonstopmode -halt-on-error -auxdir=build -emulate-aux-dir ring_lazy_jump_ext_rev2_cn.tex
latexmk -pdf -interaction=nonstopmode -halt-on-error -auxdir=build -emulate-aux-dir ring_lazy_jump_ext_rev2_en.tex
```

## 维护与清理（给后续 agent）
- 自动刷新汇总: `python3 scripts/update_research_summary.py`（更新时间 + 报告索引）
- 本地清理: `python3 scripts/cleanup_local.py`（清理 .DS_Store、__pycache__、build 等）
- venv 仅在明确需要时删除: `python3 scripts/cleanup_local.py --include-venv`

## 报告索引与关键结论

### reports/ring_valley/（non-lazy + renormalize）
- 主题: Valley regime study notes（单向 shortcut）。
- 方法: AW 反演（主）、MC 校验；按 Fig.3 规则找双峰与 valley；轨迹四类（direct/valley/intermediate/indirect）。
- 关键结果:
  - 扫描 (N,K): K=2 无双峰；K=4: N=48..52；K=6: N=68..104；K=8: N=14, 88..160（详见 `reports/ring_valley/data/bimodality_scan.json`）。
  - 单例 N=100,K=6: t1=14, t2=101, t_valley=74；并给出 shortcut 使用率与热图。
- 关键输出: `reports/ring_valley/ring_valley.pdf`, `reports/ring_valley/figures/`, `reports/ring_valley/data/`.
- 入口脚本: `reports/ring_valley/code/valley_study.py`.

### reports/ring_valley_dst/（dst 扫描; non-lazy + renormalize）
- 主题: 固定 N=100,K=6，扫描 shortcut 终点 dst 对第二峰的调制。
- 方法: AW 反演 + flux 验证；MC 条件统计 P(C>=1 | T in window)。
- 关键结果:
  - Case A (src=6): bimodal dst=43..57（15 个），late-second-peak 为主；dst=target 为特殊早峰点。
  - Case B (src=1): bimodal dst=36..64（18 个）；dst 靠近 target 时出现 t2 很早的 2-step 吸收路径。
  - 经验上 P(C>=1 | T in W) 随 R=A(t2)/A(t1) 增大而下降（排除 dst=target），A(t2) 与 P(C>=1 | T in W) 正相关但动态范围小。
- 关键输出: `reports/ring_valley_dst/ring_valley_dst_en.pdf`, `reports/ring_valley_dst/ring_valley_dst_cn.pdf`, `reports/ring_valley_dst/figures/`, `reports/ring_valley_dst/data/`.
- 入口脚本: `reports/ring_valley_dst/code/dst_shortcut_usage_mc.py`, `reports/ring_valley_dst/code/bimodality_flux_scan.py`.

### reports/ring_lazy_flux/（K=2 lazy ring; Chebyshev + AW + flux）
- 主题: k=1(K=2) lazy ring + directed shortcut 的双峰判据与解析/数值交叉验证。
- 方法: Chebyshev 闭式生成函数 + AW 反演；flux 递推验证。
- 关键结果（equal-prob baseline q=2/3）:
  - selfloop 规则在小 p 时可双峰（最小干净例: N=10, p=0.006666...）。
  - equal4 规则在 paper-like 几何下无双峰（N=10..200 扫描为 0）。
  - beta 增大抑制双峰（N=100, u=6->v=51 时 beta≈0.07 以后不再 bimodal）。
  - macro-bimodality 在 N=10 开始出现（N=3..60 全扫描）。
  - 与 `valley` 的 K=2 构造对比: valley 模型经 2-step coarse-grain 后仅单峰。
- 关键输出: `reports/ring_lazy_flux/ring_lazy_flux_en.pdf`, `reports/ring_lazy_flux/ring_lazy_flux_cn.pdf`, `reports/ring_lazy_flux/figures/lazy_ring_flux_bimodality/`.
- 入口脚本: `reports/ring_lazy_flux/code/lazy_ring_flux_bimodality.py`, `reports/ring_lazy_flux/code/lazy_ring_aw_chebyshev.py`.

### reports/ring_lazy_jump/（K=2 vs K=4; jump-over 机制）
- 主题: lazy ring + selfloop shortcut 下，K=4 的 jump-over 机制与双峰成因对比。
- 方法: AW 反演 + MC；轨迹按 (C>=1, J>=1) 划分 A/B/C/D；time-domain 扫描。
- 关键结果:
  - 峰1: shortcut 主导；谷: 类别权重过渡；峰2: 非 shortcut 主导。
  - K=4 的慢峰中 jump-over 子类占显著比例，证明“跳过吸收点”是实质延迟机制。
  - 反事实控制（jump-over 即吸收）显著改变慢峰结构。
  - N=100, q=2/3 下 beta 扫描: K=2 的双峰在 beta≈0.07 后消失；K=4 可持续到 beta≈0.15。
- 关键输出: `reports/ring_lazy_jump/ring_lazy_jump_en.pdf`, `reports/ring_lazy_jump/ring_lazy_jump_cn.pdf`, `reports/ring_lazy_jump/figures/`, `reports/ring_lazy_jump/data/`, `reports/ring_lazy_jump/tables/`.
- 入口脚本: `reports/ring_lazy_jump/code/jumpover_bimodality_pipeline.py`.

### reports/ring_lazy_jump_ext/（beta/N 扫描 + tail 机制）
- 主题: 扩展版 beta sweep / tail / N sweep（与 lazy_jump 共享模型/符号）。
- 关键结论:
  - 固定 N=100,q=2/3 仅扫 beta: 两个峰整体向早期移动，tail rate gamma 随 beta 增大；K=4 有更深 valley 与更宽双峰窗口。
  - beta=0.01 时 valley 指标 hv_over_max: K=2≈0.34，K=4≈0.15（K=4 分离更清晰）。
  - 基于 t2/t1、hv_over_max、h2/h1 选出代表性 beta*: 0.01。
  - 固定 beta* 扫 N: t2 右移、h2 下降、gamma 下降（尾更重）；K=4 的 jump-over 类别在峰1/谷/峰2 中比例稳定。
- 关键输出: `reports/ring_lazy_jump_ext/ring_lazy_jump_ext_en.pdf`, `reports/ring_lazy_jump_ext/ring_lazy_jump_ext_cn.pdf`, `reports/ring_lazy_jump_ext/outputs/`.
- 入口脚本: `reports/ring_lazy_jump_ext/code/beta_sweep_peaks_tail.py`, `reports/ring_lazy_jump_ext/code/N_sweep_peaks_tail.py`, `reports/ring_lazy_jump_ext/code/mc_sweep_beta_classes.py`, `reports/ring_lazy_jump_ext/code/mc_sweep_N_classes.py`.
- 复现实操: `reports/ring_lazy_jump_ext/notes/readme_ext.md`.

### reports/ring_lazy_jump_ext_rev2/（同轴叠加 + 敏感性分析）
- 主题: 在 lazy_jump_ext 基础上加入图1同轴叠加与敏感性分析，统一 JSON/CSV 输入与可复现表格。
- 新增内容:
  - 图1改为上下两幅（$K=2$ / $K=4$），每幅在同一主轴上叠加 $f(t)$ 与窗内比例栈叠条（替代窗口底色，支持 MC 误差条）。
  - 窗口定义改为按 $K$ 分别检测 $(t_1,t_v,t_2)$ 并用固定规则宽度 $\Delta$ 构造，保证柱条对齐各自峰谷。
  - 窗口参数与样本量表（中心/区间/宽度、$f(t_c)$ 与 $n_{K}$）。
  - 阈值敏感性、窗口边界敏感性、MC 不确定性三类分析与可视化。
  - Makefile 固化 fig2/sensitivity/pdf/check 流程。
- 关键输出: `reports/ring_lazy_jump_ext_rev2/figures/fig2_overlap_binbars_beta0.01_x1350.pdf`, `reports/ring_lazy_jump_ext_rev2/outputs/sensitivity/`, `reports/ring_lazy_jump_ext_rev2/ring_lazy_jump_ext_rev2_en.pdf`.
- 入口脚本: `reports/ring_lazy_jump_ext_rev2/code/export_fig2_inputs.py`, `reports/ring_lazy_jump_ext_rev2/code/plot_fig2_overlap_binbars.py`, `reports/ring_lazy_jump_ext_rev2/code/export_window_table.py`.

### reports/ring_two_target/（双目标 lazy ring）
- 主题: 双目标首达分布的多峰机制；对比无 shortcut/有 shortcut（selfloop 规则）并给出三峰示例。
- 方法: exact time-domain 递推（两目标吸收），结合 Giuggioli 多目标生成函数框架给出机理解释；输出 $f(t)$、splitting 分布与 $(N,\\beta)$ 双峰相图。
- 关键结果:
  - 无 shortcut 但有漂移时出现稳定双峰：逆漂移快峰 + 顺漂移慢峰。
  - 有 shortcut 时出现明显快/慢通道叠加，并在 $(N,\\beta)$ 平面上形成双峰窗口。
  - 强漂移 + $K=4$ 可产生三峰（按圈数分层的多峰列）。
- 关键输出: `reports/ring_two_target/ring_two_target_cn.pdf`, `reports/ring_two_target/ring_two_target_en.pdf`, `reports/ring_two_target/outputs/*_fpt.csv`, `reports/ring_two_target/data/scan_bimodality_K{2,4}.csv`.
- 入口脚本: `reports/ring_two_target/code/two_target_report.py`.

### reports/grid2d_two_target_double_peak/（2D 双目标双峰）
- 主题: 回答“两个 target 的 2D 何时有机会出现 double peak”，并把 splitting 分解与反射边界局部 bias 构造合并到同一可复现实验框架。
- 方法: 精确马尔可夫时间迭代（非 MC），直接计算
  $F_{n_0\to(m_1;m_2)}(t)$ 与两条 splitting
  $F_{n_0\to(m_1|m_2)}(t),F_{n_0\to(m_2|m_1)}(t)$；案例通过 $(w_2,\\texttt{skip2})$ 调控慢通道宽度与入口竞争。
- 关键结果:
  - C1 (`w2=3, skip2=2`): 双峰较平衡，峰位约 $(35,284)$，$P(m_1)\\approx0.363, P(m_2)\\approx0.488$（截断 $t\\le6000$）。
  - C2 (`w2=2, skip2=1`) 与 C3 (`w2=2, skip2=0`): 慢通道更主导，晚峰高于早峰，$P(m_2)$ 升至约 $0.71$ 与 $0.77$。
  - C4 (`w2=1, skip2=1`): 慢通道更窄导致有效速度下降，晚峰显著右移（约 $t\\approx426$），峰间分离最大。
- 新增诊断: `(w2, skip2)` 参数相图（single / weak-double / clear-double）与分离度热图；clear-double 判据为 `sep>=1`、`min(p1,p2)>=0.15`、`valley/max<=0.35`。
- 数值方法对比（同场景 C1）: sparse exact 与 dense 递推在分布上机器精度一致；AW/Cauchy 在 `t<=800` 与 exact 误差约 `1e-9`（L1），但全时域 MFPT 仍受截断窗影响；线性方程给出稳健 MFPT（约 `3011.21`）并直接揭示长尾主导效应。
- 关键输出: `reports/grid2d_two_target_double_peak/grid2d_two_target_double_peak_cn.pdf`, `reports/grid2d_two_target_double_peak/method_comparison_{cn,en}.{md,tex,pdf}`, `reports/grid2d_two_target_double_peak/data/case_summary.json`, `reports/grid2d_two_target_double_peak/data/scan_w2_skip2.{csv,json}`, `reports/grid2d_two_target_double_peak/data/method_comparison_c1.{json}`, `reports/grid2d_two_target_double_peak/data/method_comparison_c1_truncation.csv`, `reports/grid2d_two_target_double_peak/outputs/C*_fpt.csv`, `reports/grid2d_two_target_double_peak/figures/{fpt_grid,hazard_grid,phase_w2_skip2,phase_sep_w2_skip2,method_compare_c1_fpt_overlay,method_compare_c1_runtime}.pdf`.
- 入口脚本: `reports/grid2d_two_target_double_peak/code/two_target_2d_report.py`, `reports/grid2d_two_target_double_peak/code/compare_numeric_methods.py`；方法比较 PDF 入口：`reports/grid2d_two_target_double_peak/method_comparison_{cn,en}.tex`。

### reports/cross_luca_regime_map/（Luca defect 速度分区）
- 主题: 在跨报告混合案例上回答“Luca defect-reduced inversion 何时更快、何时 sparse exact recursion 更快”，并使用统一 full-FPT 公平口径做可复现实证。
- 公平协议: 固定时间窗 `T` 比较 full-FPT 运行时；主竞品仅 `Sparse exact` vs `Luca defect`；`Linear MFPT` 仅参考；`Full AW` 与 `Dense recursion` 仅作为附录锚点 sanity。
- 数据设计: two-target `40` 几何 × `T={300,600,1200}`（`120` workload）+ reflecting `20` 几何 × `T={300,1200}`（`40` workload），总计 `160` workload。
- 关键结果:
  - 全池速度比 `R=sparse/luca` 的中位数为 `4.665e-4`，`P(R>1)=0`，结论为“固定-T full-FPT 公平口径下未观察到 Luca 赢家区域”。
  - 分族统计同向：reflecting `median(R)=4.010e-4`，two-target `median(R)=5.280e-4`，均为 `P(R>1)=0`。
  - Luca 模式统计：`full=50`、`estimate=110`；估算锚点验证 `n=8`，中位相对误差 `12.65%`（通过 `<=25%` 验收）。
  - 附录锚点显示：低缺陷样例中 AW 明显最慢；高缺陷样例中 Luca 与 AW 均远慢于 sparse。
- 关键输出: `reports/cross_luca_regime_map/luca_regime_map_{cn,en}.pdf`, `reports/cross_luca_regime_map/data/{manifest,runtime_raw,runtime_summary}.csv/json`, `reports/cross_luca_regime_map/figures/regime_*.pdf`, `reports/cross_luca_regime_map/tables/{regime_summary_by_bin,regime_anchor_baselines}.tex`。
- 入口脚本: `reports/cross_luca_regime_map/code/build_manifest.py`, `reports/cross_luca_regime_map/code/run_regime_scan.py`, `reports/cross_luca_regime_map/code/plot_regime_figures.py`, `reports/cross_luca_regime_map/code/write_regime_report.py`。

### reports/ring_deriv_k2/（解析推导）
- 主题: lazy K=2 环上单向 shortcut 的生成函数与 FPT 解析推导。
- 内容: selfloop vs rewiring 两种 defect 构造；Sherman--Morrison 更新与 Giuggioli 缺陷法；Chebyshev 闭式；与数值矩阵求逆对照。
- 关键输出: `reports/ring_deriv_k2/ring_deriv_k2.pdf`, `reports/ring_deriv_k2/note_k2.pdf`.

### reports/grid2d_bimodality/（2D N×N lattice biased/lazy FPT）
- 主题: 2D lattice 上 global bias + local heterogeneities 的双峰构造与最小局部 bias 扫描。
- 方法: 无缺陷谱分解 + defects determinant 公式 + AW 反演（解析）叠加；exact time-domain 递推与 MC 轨迹分类作交叉验证。
- 关键结果:
  - 候选 A: 周期边界 + bias 产生 wrap-around 通道；paper-style 下双峰（对数轴可见晚峰），AW 与 exact/MC 叠加一致。
  - 候选 B: 贴边走廊 + mixed 边界（x 周期, y 反射），自动调参选取 `g_x=-0.25,g_y=0.40,delta=0.70,L=8,band_rows={59,60}`，满足 peak_ratio≈0.989、valley_ratio≈0.060、P_fast≈0.041（t_p1=33, t_v=220, t_p2=473）。
  - 候选 C: door + sticky + wrap-around（x 周期边界保留绕行通道），最少 local bias sites `n_min=0` 即双峰；诊断图采用窗口化两峰判别（early:[1,200], late:[200,1200]）并统一 valley ratio 阈值 0.07。
- 关键输出: `reports/grid2d_bimodality/grid2d_bimodality_cn.pdf`, `reports/grid2d_bimodality/grid2d_bimodality_en.pdf`, `reports/grid2d_bimodality/figures/`, `reports/grid2d_bimodality/outputs/`, `reports/grid2d_bimodality/data/candidate_*_metrics.json`.
- 入口脚本: `reports/grid2d_bimodality/code/bimodality_2d_pipeline.py`（支持 main/v2/v3/v4/v5/v6/v7/v8/v9/v10/v11/v12 图形输出）。
- 复现命令（main）:
  ```
  MPLCONFIGDIR=reports/grid2d_bimodality/.mplcache \
  python3 reports/grid2d_bimodality/code/bimodality_2d_pipeline.py \
    --cases-json reports/grid2d_bimodality/config/cases.json \
    --mc-samples 30000 \
    --t-max 3000 --t-max-aw 3000 --t-max-scan 1500 \
    --fpt-method both \
    --fig-version main \
    --plot-style fig3v5 \
    --png-dpi 800 \
    --mc-bin-width 2 \
    --mc-smooth-window 5 \
    --peak-smooth-window 9 \
    --log-eps 1e-14 \
    --tune_B 1
  ```
- 配置与测试: `reports/grid2d_bimodality/config/cases_v1.json`, `reports/grid2d_bimodality/config/cases_v3.json`, `reports/grid2d_bimodality/code/tests/test_aw_pgf.py`.

### reports/grid2d_reflecting_bimodality/（2D 全反射边界双峰）
- 主题: 在全反射外边界下构造双峰 FPT，强调几何慢通道与动力学慢通道的混合机制。
- 方法: exact recursion + AW 反演 + MC 叠加，输出环境示意、$P(n,t)$ 切片、路径密度、峰谷诊断与通道分解；滑动平均与峰谷检测给出 $(t_{p1},t_v,t_{p2})$、peak\\_ratio 与 valley\\_ratio。
- 关键结果:
  - 正文代表：R1（几何绕行）与 R6（door 阵列）形成明显双峰；NB4 仅改外边界（sticky + 顺时针 bias）即可得到深谷双峰（无内部 barrier/door）。
  - MB1--MB3：双车道几何 + sticky/door 减速元件即可形成双峰，无需 local bias。
  - NB1--NB3：无内部墙/门的 sticky strip 变体，展示动力学慢通道的“弱隔离”双峰；NB4 则为外边界顺时针“传送带”模板。
- 关键输出: `reports/grid2d_reflecting_bimodality/grid2d_reflecting_bimodality_cn.tex`, `reports/grid2d_reflecting_bimodality/grid2d_reflecting_bimodality_en.tex`, `reports/grid2d_reflecting_bimodality/data/*_metrics.json`, `reports/grid2d_reflecting_bimodality/figures/env/`, `reports/grid2d_reflecting_bimodality/figures/fig3_panels/`, `reports/grid2d_reflecting_bimodality/figures/paths/`, `reports/grid2d_reflecting_bimodality/figures/fpt/case_*_fpt.pdf`, `reports/grid2d_reflecting_bimodality/figures/fpt/case_*_proof.pdf`, `reports/grid2d_reflecting_bimodality/figures/fpt/case_*_diagnostic.pdf`, `reports/grid2d_reflecting_bimodality/figures/channel_decomp/case_*_channel_decomp.pdf`, `reports/grid2d_reflecting_bimodality/config/cases_reflecting_summary.json`。
- 入口脚本: `reports/grid2d_reflecting_bimodality/code/reflecting_bimodality_pipeline.py`。

### reports/grid2d_blackboard_bimodality/（黑板图 A/B/C 配置）
- 主题: 复刻黑板风格的三套配置（A 几何绕行、B door 阵列、C 墙面回路传送带），在反射边界下形成双峰 FPT。
- 方法: exact recursion + AW 反演 + MC 叠加；输出环境示意、热图三帧、路径密度、FPT 曲线、峰谷诊断与通道分解。
- 关键结果:
  - A（U 绕行）: $(t_{p1},t_v,t_{p2})=(142,303,422)$，valley ratio≈0.210。
  - B（door 阵列）: $(t_{p1},t_v,t_{p2})=(149,356,673)$，valley ratio≈0.045。
  - C（墙面回路）: $(t_{p1},t_v,t_{p2})=(182,549,907)$，valley ratio≈0.011。
- 关键输出: `reports/grid2d_blackboard_bimodality/grid2d_blackboard_bimodality_cn.pdf`, `reports/grid2d_blackboard_bimodality/data/{A,B,C}_metrics.json`, `reports/grid2d_blackboard_bimodality/figures/env/`, `reports/grid2d_blackboard_bimodality/figures/fig3_panels/`, `reports/grid2d_blackboard_bimodality/figures/paths/`, `reports/grid2d_blackboard_bimodality/figures/fpt/`, `reports/grid2d_blackboard_bimodality/figures/channel_decomp/`。
- 入口脚本: `reports/grid2d_blackboard_bimodality/code/blackboard_bimodality_pipeline.py`。

## 重要文件与位置速查（自包含定位）
- 报告入口: `reports/<name>/<name>_cn.tex`, `reports/<name>/<name>_en.tex`（pdf 同名）。
- 图/数据/表: `reports/<name>/figures`, `reports/<name>/data`, `reports/<name>/tables`, `reports/<name>/outputs`.
- 扩展章节: `reports/ring_lazy_jump_ext/sections/`.
- 说明文档: `docs/README.md`, `docs/agentreport.md`.
- 维护脚本: `scripts/update_research_summary.py`, `scripts/cleanup_local.py`.
- 项目延续 skill: `skills/valley-k-small-continuation/SKILL.md`.

## 给 ChatGPT Pro 的建议使用方式
- 若要对比模型差异，请优先说明使用的是 selfloop 规则还是 renormalize/equal4 规则，以及是否为 lazy（q<1）或 non-lazy（q=1）。
- 提问时给出 (N, K, q, beta, src, dst, target, rho) 与双峰判据（h_min、second_frac、t2/t1）即可复现。
 - 若问“为什么某报告有/无双峰”，先确认模型规则与是否做了 K=2 的 2-step coarse-grain。

## 自动索引（由脚本生成）
<!-- AUTO-INDEX:START -->
| report | pdfs | tex |
| --- | --- | --- |
| `research/reports/grid2d_bimodality` | `research/reports/grid2d_bimodality/manuscript/grid2d_bimodality_cn.pdf`, `research/reports/grid2d_bimodality/manuscript/grid2d_bimodality_en.pdf` | `research/reports/grid2d_bimodality/manuscript/grid2d_bimodality_cn.tex`, `research/reports/grid2d_bimodality/manuscript/grid2d_bimodality_en.tex` |
| `research/reports/grid2d_blackboard_bimodality` | `research/reports/grid2d_blackboard_bimodality/manuscript/grid2d_blackboard_bimodality_cn.pdf`, `research/reports/grid2d_blackboard_bimodality/manuscript/grid2d_blackboard_bimodality_en.pdf` | `research/reports/grid2d_blackboard_bimodality/manuscript/grid2d_blackboard_bimodality_cn.tex`, `research/reports/grid2d_blackboard_bimodality/manuscript/grid2d_blackboard_bimodality_en.tex` |
| `research/reports/grid2d_rect_bimodality` | `research/reports/grid2d_rect_bimodality/manuscript/grid2d_rect_bimodality_cn.pdf`, `research/reports/grid2d_rect_bimodality/manuscript/grid2d_rect_bimodality_en.pdf` | `research/reports/grid2d_rect_bimodality/manuscript/grid2d_rect_bimodality_cn.tex`, `research/reports/grid2d_rect_bimodality/manuscript/grid2d_rect_bimodality_en.tex` |
| `research/reports/grid2d_membrane_near_target` | `research/reports/grid2d_membrane_near_target/manuscript/grid2d_membrane_near_target_cn.pdf`, `research/reports/grid2d_membrane_near_target/manuscript/grid2d_membrane_near_target_en.pdf` | `research/reports/grid2d_membrane_near_target/manuscript/grid2d_membrane_near_target_cn.tex`, `research/reports/grid2d_membrane_near_target/manuscript/grid2d_membrane_near_target_en.tex` |
| `research/reports/grid2d_reflecting_bimodality` | `research/reports/grid2d_reflecting_bimodality/manuscript/grid2d_reflecting_bimodality_cn.pdf`, `research/reports/grid2d_reflecting_bimodality/manuscript/grid2d_reflecting_bimodality_en.pdf` | `research/reports/grid2d_reflecting_bimodality/manuscript/grid2d_reflecting_bimodality_cn.tex`, `research/reports/grid2d_reflecting_bimodality/manuscript/grid2d_reflecting_bimodality_en.tex` |
| `research/reports/grid2d_two_target_double_peak` | `research/reports/grid2d_two_target_double_peak/manuscript/grid2d_two_target_double_peak_cn.pdf`, `research/reports/grid2d_two_target_double_peak/manuscript/grid2d_two_target_double_peak_en.pdf`, `research/reports/grid2d_two_target_double_peak/manuscript/extras/method_comparison_cn.pdf`, `research/reports/grid2d_two_target_double_peak/manuscript/extras/method_comparison_en.pdf` | `research/reports/grid2d_two_target_double_peak/manuscript/grid2d_two_target_double_peak_cn.tex`, `research/reports/grid2d_two_target_double_peak/manuscript/grid2d_two_target_double_peak_en.tex`, `research/reports/grid2d_two_target_double_peak/manuscript/extras/method_comparison_cn.tex`, `research/reports/grid2d_two_target_double_peak/manuscript/extras/method_comparison_en.tex` |
| `research/reports/grid2d_two_walker_encounter_shortcut` | `research/reports/grid2d_two_walker_encounter_shortcut/manuscript/grid2d_two_walker_encounter_shortcut_cn.pdf`, `research/reports/grid2d_two_walker_encounter_shortcut/manuscript/grid2d_two_walker_encounter_shortcut_en.pdf` | `research/reports/grid2d_two_walker_encounter_shortcut/manuscript/grid2d_two_walker_encounter_shortcut_cn.tex`, `research/reports/grid2d_two_walker_encounter_shortcut/manuscript/grid2d_two_walker_encounter_shortcut_en.tex` |
| `research/reports/ring_two_walker_encounter_shortcut` | `research/reports/ring_two_walker_encounter_shortcut/manuscript/ring_two_walker_encounter_shortcut_cn.pdf`, `research/reports/ring_two_walker_encounter_shortcut/manuscript/ring_two_walker_encounter_shortcut_en.pdf` | `research/reports/ring_two_walker_encounter_shortcut/manuscript/ring_two_walker_encounter_shortcut_cn.tex`, `research/reports/ring_two_walker_encounter_shortcut/manuscript/ring_two_walker_encounter_shortcut_en.tex` |
| `research/reports/ring_deriv_k2` | `research/reports/ring_deriv_k2/manuscript/ring_deriv_k2.pdf`, `research/reports/ring_deriv_k2/manuscript/extras/note_k2.pdf`, `research/reports/ring_deriv_k2/manuscript/extras/note_rewire_lazy.pdf` | `research/reports/ring_deriv_k2/manuscript/ring_deriv_k2.tex`, `research/reports/ring_deriv_k2/manuscript/extras/note_k2.tex`, `research/reports/ring_deriv_k2/manuscript/extras/note_rewire_lazy.tex` |
| `research/reports/ring_lazy_flux` | `research/reports/ring_lazy_flux/manuscript/ring_lazy_flux_cn.pdf`, `research/reports/ring_lazy_flux/manuscript/ring_lazy_flux_en.pdf` | `research/reports/ring_lazy_flux/manuscript/ring_lazy_flux_cn.tex`, `research/reports/ring_lazy_flux/manuscript/ring_lazy_flux_en.tex` |
| `research/reports/ring_lazy_jump` | `research/reports/ring_lazy_jump/manuscript/ring_lazy_jump_cn.pdf`, `research/reports/ring_lazy_jump/manuscript/ring_lazy_jump_en.pdf` | `research/reports/ring_lazy_jump/manuscript/ring_lazy_jump_cn.tex`, `research/reports/ring_lazy_jump/manuscript/ring_lazy_jump_en.tex` |
| `research/reports/ring_lazy_jump_ext` | `research/reports/ring_lazy_jump_ext/manuscript/ring_lazy_jump_ext_cn.pdf`, `research/reports/ring_lazy_jump_ext/manuscript/ring_lazy_jump_ext_en.pdf` | `research/reports/ring_lazy_jump_ext/manuscript/ring_lazy_jump_ext_cn.tex`, `research/reports/ring_lazy_jump_ext/manuscript/ring_lazy_jump_ext_en.tex` |
| `research/reports/ring_lazy_jump_ext_rev2` | `research/reports/ring_lazy_jump_ext_rev2/manuscript/ring_lazy_jump_ext_rev2_cn.pdf`, `research/reports/ring_lazy_jump_ext_rev2/manuscript/ring_lazy_jump_ext_rev2_en.pdf`, `research/reports/ring_lazy_jump_ext_rev2/manuscript/extras/fig2_overlap_binbars_beta0.01_x1350_description_en.pdf` | `research/reports/ring_lazy_jump_ext_rev2/manuscript/ring_lazy_jump_ext_rev2_cn.tex`, `research/reports/ring_lazy_jump_ext_rev2/manuscript/ring_lazy_jump_ext_rev2_en.tex` |
| `research/reports/cross_luca_regime_map` | `research/reports/cross_luca_regime_map/manuscript/cross_luca_regime_map_cn.pdf`, `research/reports/cross_luca_regime_map/manuscript/cross_luca_regime_map_en.pdf`, `research/reports/cross_luca_regime_map/manuscript/extras/cross_luca_regime_map_cn_smoke.pdf`, `research/reports/cross_luca_regime_map/manuscript/extras/cross_luca_regime_map_en_smoke.pdf` | `research/reports/cross_luca_regime_map/manuscript/cross_luca_regime_map_cn.tex`, `research/reports/cross_luca_regime_map/manuscript/cross_luca_regime_map_en.tex`, `research/reports/cross_luca_regime_map/manuscript/extras/cross_luca_regime_map_cn_smoke.tex`, `research/reports/cross_luca_regime_map/manuscript/extras/cross_luca_regime_map_en_smoke.tex` |
| `research/reports/ring_two_target` | `research/reports/ring_two_target/manuscript/ring_two_target_cn.pdf`, `research/reports/ring_two_target/manuscript/ring_two_target_en.pdf` | `research/reports/ring_two_target/manuscript/ring_two_target_cn.tex`, `research/reports/ring_two_target/manuscript/ring_two_target_en.tex` |
| `research/reports/ring_valley` | `research/reports/ring_valley/manuscript/ring_valley.pdf` | `research/reports/ring_valley/manuscript/ring_valley.tex` |
| `research/reports/ring_valley_dst` | `research/reports/ring_valley_dst/manuscript/ring_valley_dst_cn.pdf`, `research/reports/ring_valley_dst/manuscript/ring_valley_dst_en.pdf` | `research/reports/ring_valley_dst/manuscript/ring_valley_dst_cn.tex`, `research/reports/ring_valley_dst/manuscript/ring_valley_dst_en.tex` |
<!-- AUTO-INDEX:END -->
