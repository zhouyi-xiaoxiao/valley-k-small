# 研究汇总（供 ChatGPT Pro）

最后更新: 2026-02-25

## 使用说明（只给这一份文件即可）
这份文件设计为**自包含**的项目总览：包含研究目标、模型定义、主要结论、报告入口、复现命令与维护规则。
如果你只会把一个文件交给 ChatGPT Pro，请直接给它本文件即可。
注意：如果 ChatGPT Pro 只拿到本文件，请默认它**无法访问仓库**；路径与命令仅用于说明研究来源与可复现性。

## 一句话总览（给 AI 的上下文入口）
我在研究环网络上的随机游走首达时间分布，重点是单条有向 shortcut 如何引发双峰/谷结构，以及不同模型构造（lazy vs non-lazy、selfloop vs renormalize vs equal4）对这一现象的影响与机制解释。

## 当前研究关注（手动维护）
（请在这里写“正在做/接下来要做”的问题，帮助 AI 快速进入你的工作流）
- 当前问题: 2D 非正方形长方形域中，双 target/单 target（走廊反射墙）在何种几何与偏置参数下能出现稳定双峰（double peak）。
- 近期目标: 细化单 target 走廊构造（墙跨度/走廊厚度/开口偏置强度/外域 slow 机制），找到至少一组 clear-double 配置并形成可解释的相图。
- 需要 AI 帮助: 自动化参数扫描设计与筛选指标；从“通道分解/flux 分解”角度给出可检验的机理判据与更强的构造建议。

## 最新进展（手动追加）
（请在这里用日期追加最新结果/想法，便于对方快速理解“当前进度”）
- 2026-02-25: 完成 Web 数据文本质量第二轮收敛：`scripts/build_web_data.py` 新增 `repair_common_math_noise(...)` 并贯通 summary/claim/narrative/section-card 清洗链路，补强 `summary_penalty` 与候选过滤（高噪声短句直接淘汰），并在章节卡片生成中加入去重与 body 级回退文案；`scripts/validate_web_data.py` 新增 malformed token 规则（如 `a p3`、`K 2,3`、`P:0.2`、`, all`）；`scripts/build_book_content.py` 与 `scripts/build_publication_pdf.py` 同步统一清洗规则；`scripts/run_openclaw_review.py` 增加 `--model` 强制模型入口。已回归通过：`python3 scripts/build_web_data.py`、`python3 scripts/validate_web_data.py`、`python3 scripts/build_book_content.py`、`python3 scripts/build_publication_pdf.py`。
- 2026-02-25: 继续推进 Web 端可解释性修复：`site/src/lib/render-pages.tsx` 将 KaTeX 渲染切换为严格模式（`throwOnError:true` + `strict:'error'`），并在公式卡片/逻辑链中显示可折叠的渲染告警（含 source/context 与 parse error 原因）；`site/src/components/ReportPlotPanel.tsx` 新增 log 坐标门控（数据含非正值时禁用 log）、自动回退线性坐标的持久提示文案，避免坐标自动切换造成解释歧义。回归通过：`python3 scripts/validate_web_data.py` 与 `cd site && npm run build`。
- 2026-02-24: 完成仓库级 Web 上线工程化主链路：新增 `site/`（Next.js 静态导出 + 双语路由 `/`,`/en`,`/cn` + 报告详情交互图 + theory MDX/KaTeX + agent-sync 页面），新增 `scripts/build_web_data.py`（14 报告预计算数据与资产映射到 `site/public/data/v1` + `site/public/artifacts`）、`scripts/build_agent_sync.py`（`manifest.json`/`reports.jsonl`/`events.jsonl` + `artifacts/checks/*.json` + `crosscheck_report.json`）、`scripts/validate_web_data.py`（schema 校验）；新增 schema `schemas/web_report.schema.json` 与 `schemas/agent_sync_v1.schema.json`，扩展 `scripts/reportctl.py` 子命令 `web-data`/`agent-sync`/`web-build`/`web-preview`，并新增 GitHub Pages 工作流 `.github/workflows/site-pages.yml`。已完成 `web-data -> agent-sync -> validate -> next build` 全链路验证与 `pytest` 回归通过。
- 2026-02-17: 完成 P1 深拆分第二部分（`ring_valley_dst` + `grid2d_reflecting/blackboard`）的工程化落地：新增 `src/vkcore/ring/valley_dst/` 与 `src/vkcore/grid2d/reflecting_blackboard/` 模块层（`cli/model/cases/pipeline/plots/io/types`），6 个主入口脚本全部改为 `<60` 行薄封装；新增 `src/vkcore/grid2d/bimod_legacy_imports.py` 统一管理 `aw_pgf/fpt_exact_mc/plot_*` 导入桥接并移除旧 `2d_bimodality/code` 路径注入。`ring_valley_dst` 注册表入口补全 `second_peak_scan.py` 与 `second_peak_shortcut_usage_mc.py`，并完成 `--help` / smoke / `py_compile` / `reportctl audit --fast` / `pytest` / `check_docs_paths` 回归全通过。
- 2026-02-16: 按“对偏置也扫描一组”的要求，在 `reports/grid2d_rect_bimodality/` 新增 one-target 全局偏置向量二维扫描（固定锚点 `x_s=7,x_t=58`、固定宽度 `W_y=12`，扫描 `b_x∈{-0.12,-0.08,-0.04,0,0.08}` 与 `b_y∈{-0.08,-0.04,0,0.04,0.08}`）：`rect_bimodality_report.py` 新增 `--ot-global-by-values`、`--ot-bias-scan-width`，并接入缓存复用 `data/ot_scan_bias2d.{csv,json}`，输出 `figures/ot_bias2d_phase_bx_by.pdf`、`figures/ot_bias2d_sep_bx_by.pdf` 与 `tables/ot_bias2d_phase_overview.tex`。结果显示 clear-double 主要集中在 `b_x=-0.08` 且 `b_y∈[-0.04,0.04]`，`b_x>=-0.04` 基本退化为 single；同时中英文文档新增“Global-bias vector scan”小节并重编通过。
- 2026-02-16: 修复 `reports/grid2d_rect_bimodality/` 图22右侧显示不全问题，并同步排查同类 phase 相图：问题来自色条文字靠右边界被裁切。已在 `rect_bimodality_report.py` 的 `plot_phase_map(...)` 与 `plot_ot_corridor_phase_vs_width(...)` 统一增加右侧留白并启用 `bbox_inches='tight'` 导出，重新生成图件后确认图22（`ot_corridor_phase_vs_width.pdf`）及其他 phase 图（如 `ot_phase_width_bx.pdf`、`tt_phase_width_xstart.pdf`）右侧标签显示完整；中英文 PDF 已重编译通过。
- 2026-02-16: 按“复现命令放在文末 + 新增一组通道厚度实验”的要求更新 `reports/grid2d_rect_bimodality/`：在 `rect_bimodality_report.py` 正式接入 one-target 走廊厚度敏感性扫描（`--ot-corridor-halfwidth-values`，默认 `0,1,2,3`，对应通道宽度 `1/3/5/7` 格），新增数据与缓存复用 `data/ot_scan_corridor_halfwidth.{csv,json}`，并输出 `figures/ot_corridor_phase_vs_width.pdf`、`figures/ot_corridor_sep_vs_width.pdf`、`tables/ot_corridor_width_summary.tex`。默认参数下结果显示：1 格宽通道（`h=0`）在焦点偏置分支仅 weak-double；加厚到 `3/5/7` 格后 clear-double 区间显著扩展。中英文 TeX 同步新增该小节，并保持复现命令段落位于文档最后；脚本复跑已验证三套扫描均可复用缓存（TT/OT/OT-corridor）。
- 2026-02-16: 新增 one-target 走廊厚度敏感性扫描（固定锚点 `(x_s,x_t)=(7,58)`，`W_y=8..28`、`b_x∈{-0.12,-0.08,-0.04,0,0.08}`，比较 `corridor_halfwidth=0,1,2,3`）：结果写入 `reports/grid2d_rect_bimodality/data/ot_scan_corridor_halfwidth.csv` 与 `ot_scan_corridor_halfwidth_summary.json`。关键结论：`halfwidth=0`（真 1 格宽通道）在 `b_x=-0.08` 下仅 weak-double、无 clear-double；`halfwidth=1` 出现 clear 区间 `W_y=8..16`；`halfwidth=2` clear 扩展到 `8..26`；`halfwidth=3` 在 `b_x=-0.08` 下 `W_y>=10` 基本全为 clear（`W_y=8` 反而单峰），说明适度加厚通道会显著增强双峰稳健性，但过窄通道难形成清晰双峰。
- 2026-02-16: 按“固定起点后扫宽度 + phase=1 可见性 + 图1/图17可读性 + 运行缓存复用”的要求更新 `reports/grid2d_rect_bimodality/`：`rect_bimodality_report.py` 新增 `--tt-width-sweep-xstart` 与 `--tt-width-sweep-target-widths`（默认 `5,6,7,8,14,24`，显式纳入 phase=1 过渡宽度），且 `pick_clear_width_sweep_tt` 在指定分支不在扫描网格时自动回退到最近 `x_start`；图1符号面板增大画布并用 `bbox_inches='tight'` 避免边缘裁切；图17（one-target 代表配置）进一步加清晰格点与右下角配置卡（`size,(x_s,x_t),corr_h,wall_m,delta_c,delta_o`）；新增扫描结果复用机制（默认开启 `--reuse-scan-data`，可用 `--no-reuse-scan-data` 关闭），复跑时优先读取 `tt_scan_width_xstart.{csv,json}` 与 `ot_scan_width_globalbias.{csv,json}`，减少重复全扫描。
- 2026-02-16: 按“所有格点格子更清楚 + 图9/图10不要拉伸”的新要求再次更新 `reports/grid2d_rect_bimodality/`：进一步加重几何图逐格网格线与每 5 格参考线（`_draw_lattice_grid`），并把同类网格叠加到条件占据热图面板（`_draw_heatmap_panel`）以统一“每个格子可读”。同时把 `plot_tt_env_heatmaps` 的画布高度策略改为显式非拉伸导向，保留 `equal` 几何比例并提高细长矩形可读性；图9/10对应图注保持“geometry-preserving / 不做拉伸”。全量重跑脚本并重编 CN/EN PDF，日志无 overfull/undefined/citation 警告。
- 2026-02-16: 按“图6格点不够清楚 + 想确认更宽 double peak 与临界含义”的反馈，更新 `reports/grid2d_rect_bimodality/`：在 `rect_bimodality_report.py` 的 two-target/one-target 几何绘图中加入逐格晶格线并每 5 格加粗参考线（图6及同类配置图更易读）；中英文正文补充“临界=宽度阈值（非单一时间阈值）”说明，并给出 near-critical 峰时刻示例（`x0=10` 分支 `Wy=6: t_{p1},t_{p2}=72,851`；`Wy=7: 78,881`）。全量重跑脚本并重编 CN/EN PDF，结论保持：two-target clear 仅到 `Wy=6`（`x0=10`），one-target 在锚点 `(x_s,x_t)=(7,58)`、`b_x=-0.08` 下 clear 区间仍为 `Wy=8..16`，首失稳 `Wy=18`。
- 2026-02-16: 完成“所有报告逐个审计”回归：新增统一脚本 `scripts/audit_reports.py`（修复 `_cn_smoke` 引擎识别为 `xelatex`），全量检查 `reports/*/*.tex` 共 33 份与 `reports/**/code/*.py` 共 116 份，结果为 `33/33` 构建成功、`py_compile` 全通过、`overfull/underfull/undefined/missing/duplicate destination` 全为 0。并修复两处版式潜在问题（`method_comparison_en.tex` 摘要坏行、`valley_dst/inputs/flux_validation_cn.tex` 英文长串导致 underfull）及复现命令口径错误：中文统一 `*_cn.tex -> latexmk -xelatex`，英文统一 `*_en.tex -> latexmk -pdf`（已修 `two_target_ring/README.md`、`lazy_jump_ext/README_ext.md`、`lazy_jump_ext/sections/repro_{cn,en}.tex`、`2d_rect_bimodality/README.md`、`2d_blackboard_bimodality/README.md`、`2d_reflecting_bimodality/README.md`、`2d_blackboard_bimodality_{cn,en}.tex` 与本汇总文档）。
- 2026-02-16: 按“检查所有报告、逐个修潜在问题”的要求完成第三轮全仓审计：新增修复 `luca_regime_map_{cn,en,cn_smoke,en_smoke}` 与 `2d_two_target_double_peak/method_comparison_{cn,en}` 的超链接锚点冲突风险（`hypertexnames=false`），并更新 `reports/README.md` 与 `docs/README.md` 的索引与复现命令口径（去重、补齐 `2d_rect_bimodality` 与 `lazy_jump_ext_rev2`）。回归结果：33/33 TeX 成功，`overfull/undefined/duplicate-destination` 均为 0；`reports/**/code/*.py` 共 116 文件 `py_compile` 全通过。
- 2026-02-16: 按“所有报告逐个检查”再次完成全仓深度回归（33 份主 TeX + 116 份 `code/*.py`）：`latexmk` 全通过、`overfull/undefined reference/citation/control sequence/missing file/duplicate destination` 全为 0。除已完成的构建与排版修复外，本轮新增修正两类潜在问题：`luca_regime_map` 与 `2d_two_target_double_peak/method_comparison` 的 PDF 锚点冲突（`hypertexnames=false`），以及 `reports/README.md`/`docs/README.md` 中过时描述、重复命令和编译口径不一致（已统一为可直接复现的当前口径，补齐 `2d_rect_bimodality` 与 `lazy_jump_ext_rev2` 入口）。
- 2026-02-16: 再次按“所有报告逐个检查并修复”的要求完成全仓回归：逐一复核 `reports/*/*.tex`（33 份主文档）与 `reports/**/code/*.py`（116 份脚本）。本轮重点修复了跨报告排版与复现块问题（`two_target_ring` 的并排图 overfull、`deriv_k2` 长公式行溢出、`2d_blackboard_bimodality/lazy_flux/valley_dst/method_comparison` 的超长命令行、`luca_regime_map` 的宽表格与推荐矩阵）。最终状态：`py_compile` 全通过；33/33 TeX 构建成功；`undefined reference/citation/control sequence/missing file` 全为 0；`Overfull \\hbox` 全为 0（全报告清零）。
- 2026-02-16: 按“所有报告逐个检查”的要求，完成 `reports/*/*.tex` 全量主文档审计（共 33 份，逐一 `latexmk` 回归）与 `reports/**/code/*.py` 语法检查（129 文件 `py_compile` 全通过）。本轮修复两项真实构建问题：`cross_luca_regime_map_en_smoke.tex` 的 `\\texttt` 下划线转义错误（导致 Missing `$`），以及 `cross_luca_regime_map_cn_smoke.tex` 的引擎匹配问题（审计流程改为文件名含 `_cn` 一律用 `xelatex`）。同时对 overfull 较多的旧报告导言区补充/增强 `\\emergencystretch`（blackboard/deriv/lazy_flux/two_target_ring/valley 等）。最终结果：33/33 主文档可构建，0 missing file、0 undefined reference/citation、0 undefined control sequence；仍有部分历史 overfull（不影响结论与可复现性）已记录待后续精修。
- 2026-02-16: 对 `reports/grid2d_rect_bimodality/` 再做一轮“按你前序指令”的回归复核并补上防回归约束：在 `rect_bimodality_report.py` 新增 `validate_tt_representative_branch_coverage(...)`，强制 two-target 代表案例覆盖关键分支中所有存在 clear-double 的分支（当前为 `x0=8,10,12`）；同时同步更新中英文图注，明确图6类代表图覆盖这三条分支。已全量重跑脚本并重编 CN/EN PDF，当前代表集已恢复为 `TT_W05_X08/TT_W08_X08/TT_W05_X10/TT_W08_X10/TT_W05_X12/TT_W06_X12`，无 overfull/undefined/citation warning。
- 2026-02-16: 对 `reports/grid2d_rect_bimodality/` 再次深度回顾后新增“运行时一致性硬校验”：在 `rect_bimodality_report.py` 加入 `validate_tt_series_consistency(...)` 与 `validate_ot_series_consistency(...)`，并接入 two-target/one-target 的扫描、扩展分支、代表案例与锚点预扫描流程。校验项包括非负性、`survival<=1`、生存概率单调、通道分解恒等与逐步质量守恒；任一不满足将立即报错，避免“图像正常但底层质量守恒失效”的隐患。已全量重跑脚本与中英文 PDF，结论与相图不变，日志无 overfull/undefined/citation。
- 2026-02-16: 对 `reports/grid2d_rect_bimodality/` 再做一轮“代码-数值-图表-中英文文案”深度复核并修复一项数值稳定性边界：在 `run_exact_two_target_rect` 与 `run_exact_one_target_rect` 中引入非负质量投影（`project_mass_nonnegative`），消除极小浮点漂移导致的 `survival>1` 或非单调尾部风险，同时不改变模型机制与参数。修复后全量重跑脚本、重编 CN/EN PDF，并复核 `max_survival_over1=0`、`max_survival_increase=0`、TT/OT 分解恒等误差为 `0`、`case_summary` 路径引用完整、LaTeX 日志无 overfull/undefined/citation。
- 2026-02-16: 对 `reports/grid2d_rect_bimodality/` 再做一次“全代码 + 全图表 + 中英文文案”深度回归并修正两处未显式写清的问题：其一，在中英文正文的 one-target 部分新增定量结论段，明确锚点 `(x_s,x_t)=(7,58)` 下 `b_x=-0.08` 仅在 `W_y=8,10,12,14,16` 为 clear-double、`W_y>=18` 退化为 weak-double，而 `b_x=-0.12` 为全域 weak、`b_x∈{-0.04,0,0.08}` 为全域 single；其二，复现命令中英文档编译口径统一为 `latexmk -pdf ... grid2d_rect_bimodality_en.tex`（中文仍 `-xelatex`）。已全量重跑脚本、重编 CN/EN PDF，并通过 CSV↔表格↔正文自动核对；日志无 overfull/undefined/citation。
- 2026-02-16: 对 `reports/grid2d_rect_bimodality/` 再次进行“全代码+全图表+中英文文案”深度复核，并修复三项一致性风险：`tt_scan_overview.tex` 的 `best min(p1,p2)` 仅在 `phase>=1` 条件下统计（避免单峰宽度出现误导性高值）；固定分支宽度样本选择去重并在粗步长时自动补齐；`x0=8/10/12` 扩展临界扫描改为沿 `tt_width_step` 采样（避免步长不一致导致伪临界）。已全量重跑脚本和 CN/EN PDF，日志仍无 overfull/undefined/citation 警告。
- 2026-02-16: 对 `reports/grid2d_rect_bimodality/` 再做一轮全链路审计后修复两项一致性问题：(1) `tt_critical_width_by_xstart.tex` 的 `first loss width` 也改为“从真实扫描宽度列表取下一个采样点”（不再固定 `+1`，避免非 1 步长时伪宽度）；(2) 重新全量跑脚本并重编中英文 PDF（中文使用 `latexmk -xelatex`），核对 `phase/峰标注/表格` 逻辑一致，`build/*_{cn,en}.log` 中无 overfull/undefined/citation warning。
- 2026-02-16: 对 `reports/grid2d_rect_bimodality/` 再做全链路审计并修复两项隐藏问题：(1) `ot_anchor_selection.tex` 的 `first loss` 之前按 `+1` 计算，会落在未扫描宽度（例如 17）；现改为“从真实扫描宽度列表取下一个宽度”，并按扫描步长压缩 clear 区间显示（现为 `8-16`，`first loss=18`）。(2) one-target 代表 FPT/hazard 网格移除淡色原始曲线叠层，仅保留平滑主曲线，避免离散锯齿被误判为“算法峰”。同时统一 two-target 谷深记号为 `$p_v/\\max(p_1,p_2)$`，并在中英文正文补充 splitSep 与总曲线双峰判据的区别说明。已全量重跑脚本并重编 CN/EN PDF，日志无 warning/overfull。
- 2026-02-16: 对 `reports/grid2d_rect_bimodality/` 做了一次额外“全代码+全图+全文案”复核：重跑 `rect_bimodality_report.py`、强制重编中英文 PDF、逐项核对图号映射（图6/9/10/11/12/20/21）、代表案例相位与表格/CSV 阈值一致性，并对关键图做转 PNG 目检（含双峰标注、时间窗、色条排版）。本轮未发现新增逻辑或文案错误，现有结论保持不变。
- 2026-02-16: 对 `reports/grid2d_rect_bimodality/` 做了额外“deep audit”回归：验证 `--quick` 与 full 两条执行路径均能稳定完成；随后恢复 full 产物并对 `case_summary` 引用、图号映射（图6/7/8/9/10/11/12/17/18/19/20/21）与 CSV/表格阈值陈述做自动对账，未发现新增不一致项。最终构建日志仍无 overfull/undefined/citation。
- 2026-02-16: 继续对 `reports/grid2d_rect_bimodality/` 做“未提及项”复核后，修正 one-target 代表配置图（图17）的分类标签语义：原先 `phase>=1` 统一写 `double-peak`，现改为 `clear-double / weak-double / single-peak` 三档，避免将 phase=1 与 phase=2 混写；中英文图注同步更新并重跑脚本、重编 CN/EN PDF，图号与数据结论保持一致。
- 2026-02-16: 对 `reports/grid2d_rect_bimodality/` 再做一次“全代码+全图表+中英文文案”复核并完成修正：重新全量跑 `rect_bimodality_report.py`、重编 CN/EN PDF、逐项校验 `case_summary.json`/CSV/表格/图号一致性（含图6/11/17/18/20/21对应资产）、确认 TT 与 OT 阈值结论未漂移。新增一项复现层修订：`2d_rect_bimodality_{cn,en}.tex` 与报告目录 `README.md` 的复现命令补充了 `venv` 创建与依赖安装步骤，避免系统 `python3` 缺包导致无法复现；LaTeX 日志仍无 overfull/undefined/citation 警告。
- 2026-02-16: 对 `reports/grid2d_rect_bimodality/` 再做深度一致性回归并补上 summary 级防护：`case_summary.json` 现在额外记录并校验代表案例的 `outputs/*_fpt.csv`（`rep_series_csv`），且改为“先校验路径再写 summary”以避免异常时落盘不可信 summary。并验证了扩展分支在 `t_max=5000` 与 `t_max=20000` 下 phase 一致（`x0=8/10/12` 无不一致），排除时间窗截断导致的假失稳。
- 2026-02-16: 对 `reports/grid2d_rect_bimodality/` 再次做“代码+语言+逻辑”全链路复核并修复一项流程性隐患：`validate_representative_phase_consistency(...)` 与 `validate_summary_artifact_paths(...)` 之前定义但未接入主流程，现已在 `main()` 中启用；同时将启动清理从 case 级升级为 `purge_generated_artifacts(...)` 全量清理，避免旧扫描表/旧图残留造成的静默污染。已全量重跑脚本与中英文 `latexmk`，相图/代表案例/表格一致，LaTeX 无 overfull/undefined 引用。
- 2026-02-16: 在 `reports/grid2d_rect_bimodality/code/rect_bimodality_report.py` 新增 `purge_case_level_artifacts(...)`，并在 `main()` 开始阶段启用。修复的问题是：历史运行遗留的按 case 命名文件（`outputs/TT_*_fpt.csv`、`outputs/OT_*_fpt.csv` 与对应 `figures/*`）会与当前扫描口径混在一起，造成“同名 case 看起来与当前 phase 相冲突”的假象。现在每次重跑都会先清理旧 case 级产物，再写入当前代表案例，避免报告资产歧义。
- 2026-02-16: 对 `reports/grid2d_rect_bimodality/` 再做一轮端到端审计（代码逻辑、CSV-表格一致性、代表案例 phase 一致性、`case_summary` 路径完整性、CN/EN `label-ref` 完整性、LaTeX 日志 warning/overfull）。本轮未发现新的数据/逻辑错误；全量重跑 `code/rect_bimodality_report.py` 与中英文 `latexmk` 均通过，关键结论保持不变：TT 仍为分支依赖临界（`x0=8:5-9`, `x0=10:5-8`, `x0=12:5-6`），OT 在锚点 `x_s=7,x_t=58` 下 `b_x=-0.08` 仍在 `W_y=8..16` 为 phase=2。
## 仓库速览（结构 + 入口）
```
valley-k-small/
  reports/          # 各报告自包含
  docs/             # 说明文档与提交材料
  scripts/          # 自动化维护脚本
  requirements.txt  # Python 依赖
  AGENTS.md         # 协作规则（维护要求）
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

## 给 ChatGPT Pro 的建议使用方式
- 若要对比模型差异，请优先说明使用的是 selfloop 规则还是 renormalize/equal4 规则，以及是否为 lazy（q<1）或 non-lazy（q=1）。
- 提问时给出 (N, K, q, beta, src, dst, target, rho) 与双峰判据（h_min、second_frac、t2/t1）即可复现。
 - 若问“为什么某报告有/无双峰”，先确认模型规则与是否做了 K=2 的 2-step coarse-grain。

## 自动索引（由脚本生成）
<!-- AUTO-INDEX:START -->
| report | pdfs | tex |
| --- | --- | --- |
| `reports/grid2d_bimodality` | `reports/grid2d_bimodality/grid2d_bimodality_cn.pdf`, `reports/grid2d_bimodality/grid2d_bimodality_en.pdf` | `reports/grid2d_bimodality/grid2d_bimodality_cn.tex`, `reports/grid2d_bimodality/grid2d_bimodality_en.tex` |
| `reports/grid2d_blackboard_bimodality` | `reports/grid2d_blackboard_bimodality/grid2d_blackboard_bimodality_cn.pdf`, `reports/grid2d_blackboard_bimodality/grid2d_blackboard_bimodality_en.pdf` | `reports/grid2d_blackboard_bimodality/grid2d_blackboard_bimodality_cn.tex`, `reports/grid2d_blackboard_bimodality/grid2d_blackboard_bimodality_en.tex` |
| `reports/grid2d_rect_bimodality` | `reports/grid2d_rect_bimodality/grid2d_rect_bimodality_cn.pdf`, `reports/grid2d_rect_bimodality/grid2d_rect_bimodality_en.pdf` | `reports/grid2d_rect_bimodality/grid2d_rect_bimodality_cn.tex`, `reports/grid2d_rect_bimodality/grid2d_rect_bimodality_en.tex` |
| `reports/grid2d_reflecting_bimodality` | `reports/grid2d_reflecting_bimodality/grid2d_reflecting_bimodality_cn.pdf`, `reports/grid2d_reflecting_bimodality/grid2d_reflecting_bimodality_en.pdf` | `reports/grid2d_reflecting_bimodality/grid2d_reflecting_bimodality_cn.tex`, `reports/grid2d_reflecting_bimodality/grid2d_reflecting_bimodality_en.tex` |
| `reports/grid2d_two_target_double_peak` | `reports/grid2d_two_target_double_peak/grid2d_two_target_double_peak_cn.pdf`, `reports/grid2d_two_target_double_peak/grid2d_two_target_double_peak_en.pdf`, `reports/grid2d_two_target_double_peak/method_comparison_cn.pdf`, `reports/grid2d_two_target_double_peak/method_comparison_en.pdf` | `reports/grid2d_two_target_double_peak/grid2d_two_target_double_peak_cn.tex`, `reports/grid2d_two_target_double_peak/grid2d_two_target_double_peak_en.tex`, `reports/grid2d_two_target_double_peak/method_comparison_cn.tex`, `reports/grid2d_two_target_double_peak/method_comparison_en.tex` |
| `reports/ring_deriv_k2` | `reports/ring_deriv_k2/ring_deriv_k2.pdf`, `reports/ring_deriv_k2/note_k2.pdf`, `reports/ring_deriv_k2/note_rewire_lazy.pdf` | `reports/ring_deriv_k2/ring_deriv_k2.tex`, `reports/ring_deriv_k2/note_k2.tex`, `reports/ring_deriv_k2/note_rewire_lazy.tex` |
| `reports/ring_lazy_flux` | `reports/ring_lazy_flux/ring_lazy_flux_cn.pdf`, `reports/ring_lazy_flux/ring_lazy_flux_en.pdf` | `reports/ring_lazy_flux/ring_lazy_flux_cn.tex`, `reports/ring_lazy_flux/ring_lazy_flux_en.tex` |
| `reports/ring_lazy_jump` | `reports/ring_lazy_jump/ring_lazy_jump_cn.pdf`, `reports/ring_lazy_jump/ring_lazy_jump_en.pdf` | `reports/ring_lazy_jump/ring_lazy_jump_cn.tex`, `reports/ring_lazy_jump/ring_lazy_jump_en.tex` |
| `reports/ring_lazy_jump_ext` | `reports/ring_lazy_jump_ext/ring_lazy_jump_ext_cn.pdf`, `reports/ring_lazy_jump_ext/ring_lazy_jump_ext_en.pdf` | `reports/ring_lazy_jump_ext/ring_lazy_jump_ext_cn.tex`, `reports/ring_lazy_jump_ext/ring_lazy_jump_ext_en.tex` |
| `reports/ring_lazy_jump_ext_rev2` | `reports/ring_lazy_jump_ext_rev2/ring_lazy_jump_ext_rev2_cn.pdf`, `reports/ring_lazy_jump_ext_rev2/ring_lazy_jump_ext_rev2_en.pdf`, `reports/ring_lazy_jump_ext_rev2/fig2_overlap_binbars_beta0.01_x1350_description_en.pdf` | `reports/ring_lazy_jump_ext_rev2/ring_lazy_jump_ext_rev2_cn.tex`, `reports/ring_lazy_jump_ext_rev2/ring_lazy_jump_ext_rev2_en.tex` |
| `reports/cross_luca_regime_map` | `reports/cross_luca_regime_map/cross_luca_regime_map_cn.pdf`, `reports/cross_luca_regime_map/cross_luca_regime_map_cn_smoke.pdf`, `reports/cross_luca_regime_map/cross_luca_regime_map_en.pdf`, `reports/cross_luca_regime_map/cross_luca_regime_map_en_smoke.pdf` | `reports/cross_luca_regime_map/cross_luca_regime_map_cn.tex`, `reports/cross_luca_regime_map/cross_luca_regime_map_cn_smoke.tex`, `reports/cross_luca_regime_map/cross_luca_regime_map_en.tex`, `reports/cross_luca_regime_map/cross_luca_regime_map_en_smoke.tex` |
| `reports/ring_two_target` | `reports/ring_two_target/ring_two_target_cn.pdf`, `reports/ring_two_target/ring_two_target_en.pdf` | `reports/ring_two_target/ring_two_target_cn.tex`, `reports/ring_two_target/ring_two_target_en.tex` |
| `reports/ring_valley` | `reports/ring_valley/ring_valley.pdf` | `reports/ring_valley/ring_valley.tex` |
| `reports/ring_valley_dst` | `reports/ring_valley_dst/ring_valley_dst_cn.pdf`, `reports/ring_valley_dst/ring_valley_dst_en.pdf` | `reports/ring_valley_dst/ring_valley_dst_cn.tex`, `reports/ring_valley_dst/ring_valley_dst_en.tex` |
<!-- AUTO-INDEX:END -->
