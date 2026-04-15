# RESEARCH Progress Archive

## Archived on 2026-02-16
- 2026-02-16: 再次核查并修正 `reports/grid2d_rect_bimodality/`：图9/10改为更有区分度的 two-target 代表热图（A=`TT_W05_X10`，B=`TT_W06_X12`）；图12首峰/峰点与平滑曲线对齐并复核为无锯齿假峰；图20/21确认对应 one-target 代表案例（A=`OT_W16_bxm0p080`，B=`OT_W28_bxm0p080`）。新增 one-target “先选位置后扫宽度”的锚点预扫描（选得 `x_s=7, x_t=58`），在此锚点下 `b_x=-0.08` 于 `W_y=8..16` 出现 phase=2；同时修复环境热图标注越界/色条遮挡与中英文 LaTeX overfull，PDF 已重编译通过。
- 2026-02-16: 对 `reports/grid2d_rect_bimodality/` 做了整体验证与修正：two-target 双峰判据改为“平滑包络 + 峰平衡 + 谷降幅”鲁棒检测（抑制早时刻锯齿假峰），图6示例统一为 clear-double 直线 stream 案例，图11固定分支改为显式展示 `phase=2 -> phase=0` 跃迁（`x_0=10` 上 `W_y=5,8` clear，`W_y>=9` 不再通过鲁棒双峰）；临界表最终为 `x_0=8:5-9(10失稳), x_0=10:5-8(9失稳), x_0=12:5-6(7失稳)`。同步清理绘图布局 warning 与中英文 LaTeX 日志（含 overfull/hyperref 书签警告）并重编译 PDF。
- 2026-02-16: 进一步按“结论支撑度”重选 `reports/grid2d_rect_bimodality/` 双-target示范案例：图6（代表案例）改为 `TT_W05_X06/TT_W05_X10/TT_W05_X12/TT_W08_X10/TT_W09_X10/TT_W14_X10`，同时保留直线单股 local bias；图11（固定分支宽度演化）改为 `x_0=10` 下 `W_y={5,8,9,10,14,24}`，显式覆盖 `8→9→10` 的峰时窗突变区间。对应图表、指标表与中英文 PDF 已重生成。
- 2026-02-16: 修复 `reports/grid2d_rect_bimodality/` 中英文报告的 LaTeX overfull：图示说明表改为去两侧间距并重配列宽（`@{}...@{}`），复现命令块中的超长行改为续行写法；重编译后 `build/2d_rect_bimodality_{cn,en}.log` 中已无 `Overfull \hbox` 警告。
- 2026-02-16: 按图20可视化反馈优化 `reports/grid2d_rect_bimodality/` 的单-target 环境热图排版：`ot_repA_env_heatmap` 与 `ot_repB_env_heatmap` 改为紧凑横向布局（环境 + 三时刻热图 + 独立 colorbar 轴），去除大面积留白并统一子图尺度；同时保留目标/边界标记与时刻标注，重编译中英文 PDF。
- 2026-02-16: 按图号反馈细化 `reports/grid2d_rect_bimodality/` 的单-target展示：图17（`ot_representative_geometry_grid`）新增每个子图的 `b_x` 数值与方向箭头，并打上 `double-peak/single-peak` 标签；图18（`ot_representative_fpt_grid`）在所有双峰子图上显式标注两峰位置 `p1/p2`（竖虚线+峰点），谷底时刻用灰色点线补充。中英文报告的对应图注与正文解释同步更新。
- 2026-02-16: （历史记录，后续已被“鲁棒双峰判据”结果覆盖）再次更新 `reports/grid2d_rect_bimodality/` 的 two-target 展示与临界分析。(i) 代表双 target 图组改为\textbf{强双峰样例优先}（`TT_W05_X06`, `TT_W05_X10`, `TT_W05_X12`, `TT_W06_X10`, `TT_W07_X10`, `TT_W08_X10`），全部保持\textbf{直线 stream、无拐弯、一格厚 local bias}；FPT 面板统一为归一化 + 峰谷标注 + 第二峰 inset，hazard 分解同步扩展到 6 图并覆盖第二峰时间尺度。(ii) 为避免扫描截断造成的假性失稳，将 two-target splitting 权重改为按已吸收质量归一化；并对关键分支 `x0=8,10,12` 扩展宽度到 `Wy=60` 做临界估计，更新为：`x0=8` clear 到 `Wy=36`（`37` 首次失稳）、`x0=10` clear 到 `Wy=52`（`53` 首次失稳）、`x0=12` 在 `Wy<=60` 未见 clear 失稳（区间 `5-6,14-60`）。(iii) 宽度对比图改为固定分支 `x0=10` 的演化组（`Wy={5,8,10,14,20,24}`），用于展示“晚时窗第二峰 -> 早时窗弱分离”的连续变化；中英文 PDF 与相关图表已重编译。
- 2026-02-11: 新增 `reports/cross_luca_regime_map/` 跨报告速度分区研究并完成全量实跑（固定 full-FPT 时间窗公平口径）：`160` 个 workload（two-target `120` + reflecting `40`）在统一线程与 `warmup+3次取中位` 协议下比较 `sparse_exact_fullfpt` 与 `luca_defect_fullfpt_or_est`；主结论为 `median(R=sparse/luca)=4.665e-4`、`P(R>1)=0`，即在本次公平口径下无 Luca 赢家区域；估算模式验证锚点 `8` 组中位相对误差 `12.65%`（通过 `<=25%` 门槛）。同步产出中英文报告、6 张图、2 张表及 `manifest/runtime_raw/runtime_summary` 数据契约。
- 2026-02-10: 按用户要求在 `reports/grid2d_two_target_double_peak/method_comparison_{cn,en}.tex` 将 Method C 显式替换为 Luca/Giuggioli 路线，并补上可读数学流程：`Q=Q0+UΔV^T` 缺陷分解、Woodbury 选定传播子恢复、两目标 `2x2` renewal 闭合、Cauchy-FFT 反演；Full AW 改为 Method C0 对照基线并重编译中英文 PDF。
- 2026-02-10: 在 `reports/grid2d_two_target_double_peak/code/compare_numeric_methods.py` 实装并实跑 Giuggioli defect-reduced AW（Woodbury + 两目标 renewal + FFT 反演），C1 实测：`AW=47.2622s`、`AW defect-reduced=78.0223s`、同窗分布误差与 AW 一致（`L1≈9.912e-10`）；本实现采用 pair 维度 `M=632`（`n_T=959`），求解核估算降幅约 `3.2x~3.5x`，但被基底 Green 求值与装配开销抵消。
- 2026-02-10: 同步重写并重编译 `reports/grid2d_two_target_double_peak/method_comparison_en.{md,tex,pdf}` 与 `method_comparison_cn.{md,tex,pdf}`：统一为五方法口径（含 Giuggioli defect-reduced AW）、更新运行时间/误差/缺陷规模表，并把“未实测 defect 方法”改为“已实现且已基准”。
- 2026-02-10: 为 `reports/grid2d_two_target_double_peak/` 新增英文主报告 `grid2d_two_target_double_peak_en.tex` 并编译 `grid2d_two_target_double_peak_en.pdf`；英文版覆盖当前中文报告的核心推导、主结果、外部 sparse testset 双峰配置（S02/S03）及全箭头附录图。
- 2026-02-10: 为 `reports/grid2d_two_target_double_peak/` 新增英文方法比较报告 `method_comparison_en.{md,tex,pdf}`，与中文版同场景（C1）对齐，完整覆盖 sparse exact / dense recursion / AW inversion / linear MFPT 的公式、复杂度与实测对比。
- 2026-02-10: 按用户要求在 `reports/grid2d_two_target_double_peak/` 的外部 sparse testset 结果中仅保留双峰配置（S02 clear double, S03 weak double），并新增两组“详细配置图 + 配置/热图四联图”产物：`figures/sparse_S02_{config_detailed,env_heatmap}.pdf` 与 `figures/sparse_S03_{config_detailed,env_heatmap}.pdf`；中文报告同步重排外部配置章节。
- 2026-02-10: `reports/grid2d_two_target_double_peak/` 接入外部配置集 `/Users/ae23069/Desktop/sparse_double_peak_testset.json`，新增 11 组 sparse 配置自动批跑（支持 local bias / sticky / barrier / long-range / global bias），并在中文报告中加入“外部 Sparse Testset 配置补充”章节、配置统计表、指标表和总览曲线图。
- 2026-02-10: `reports/grid2d_two_target_double_peak/` 文末新增“红箭头全分布大图”附录（C1--C4 四张大图），每个偏置格点均绘制红箭头，直接展示局部 bias 的空间分布；同时修复图例色块命令，去除“色块中间黑块”误导。
- 2026-02-07: 进一步澄清慢通道可视化：在配置图中新增慢通道拐点黑色圆点标记，并在正文明确“米黄色区域整体有偏置、红箭头仅为中心线抽样显示”；重编译 `grid2d_two_target_double_peak_cn.pdf`。
- 2026-02-07: 修复 `reports/grid2d_two_target_double_peak/` 第 8 页图5/图6显示不完整问题：将两图拆分为单独浮动页并放大版面宽度，同时调整 `fpt_grid/hazard_grid` 导出画布比例与图例布局以提升可读性；重编译中文 PDF（页数由 10 页变为 12 页）。
- 2026-02-07: 在 `reports/grid2d_two_target_double_peak/` 新增数值方法对比研究：实现 `code/compare_numeric_methods.py`，同场景比较 sparse exact、dense recursion、AW/Cauchy-FFT 反演与线性方程 MFPT；输出 `method_comparison_cn.md`、`data/method_comparison_c1.json`、`data/method_comparison_c1_truncation.csv` 与两张对比图。
- 2026-02-07: 为 `reports/grid2d_two_target_double_peak/` 新增可直接阅读的 PDF 版方法比较报告 `method_comparison_cn.pdf`（源文件 `method_comparison_cn.tex`）；补充各方法详细数学原理、统一复杂度推导与 C1 场景量级代入。
- 2026-02-07: 修复 `reports/grid2d_two_target_double_peak/` 图符不一致：统一所有图中 `m1/m2` 标记（`m1` 蓝菱形、`m2` 深蓝圆形），并新增脚本直接生成的 `figures/symbol_legend_panel.pdf` 作为“符号基准图”；同步更新图例表与正文说明。
- 2026-02-07: 继续优化 `reports/grid2d_two_target_double_peak/`：将“图示元素逐项说明”升级为带实际颜色块/线型/标记的可视化图例表；新增“数学符号-图件映射总表”和 hazard 分解图（`h=h_1+h_2`），并补充 `(w2, skip2)` 参数相图判据说明。
- 2026-02-07: 继续优化 `reports/grid2d_two_target_double_peak/`：重写“数学机理推导”章节（从马尔可夫链定义到 splitting 分解、生成函数与可检验双峰判据），并将配置图升级为工程化示意 + 真实条件占据概率热图四联图（按各案例峰/谷时刻自动选时）。
- 2026-02-07: 新增 `reports/grid2d_two_target_double_peak/`，系统分析“2D 双 target 在何种配置下出现 double peak”；采用反射边界 + 局部 bias 双走廊模型，给出 C1--C4 四组可复现实验（含总首达 + splitting 曲线、峰位/分流概率表、中文 PDF）。
- 2026-02-02: `reports/grid2d_blackboard_bimodality/` 追加小 $N$ 竖向矩形案例 S（$18\times30$，起止点在墙端点），结果仍为单峰 + 长尾；中英文 PDF 已更新。
- 2026-02-02: `reports/grid2d_blackboard_bimodality/` 仅保留起止点位于内墙端点的案例 Z；新增 `code/z_scan.py` 与 `data/Z_scan.json` 记录参数扫描（Z0--Z4 仍单峰 + 长尾，仅在外圈 sticky + 顺时针偏置时出现迟滞峰）；中英文 PDF 已更新。
- 2026-02-02: 再次调整 `reports/ring_two_target/` Case C/D 标签位置（t1/dst 改为相对偏移 + 引导线），避免重叠。
- 2026-02-02: 重排 `reports/ring_two_target/`：每个 case 几何与 FPT 合并展示，并改为线性坐标 + 峰标注以增强双峰可读性。
- 2026-02-02: 为 `reports/ring_two_target/` 增加参数定义段落，并在每个 case 图旁加入配置卡便于对照。
- 2026-02-02: 优化 `reports/ring_two_target/` 配置卡样式（灰底卡片）与 FPT 线型风格；英文正文将 “we” 改为 “I”。
- 2026-02-02: 在 `reports/ring_two_target/` 各 case FPT 图中标注峰位置 $t_1,t_2$（三峰例追加 $t_3$）。
- 2026-02-02: 在 `reports/ring_two_target/` 图中直接标注峰值数值（如 $t_1=2,t_2=20$ 等）。
- 2026-02-02: `reports/grid2d_blackboard_bimodality/` 暂时只保留截图失败案例 X/D/E，补齐英文版 `grid2d_blackboard_bimodality_en.pdf`，并在正文明确矩形域可行。
- 2026-02-02: 在截图失败系列中新增小 $N$ 竖向矩形域案例 R（$20\\times30$）并输出图组；结果仍为单峰 + 长尾。
- 2026-02-02: 报告 `2d_blackboard_bimodality` 现在仅保留“起止点位于内墙端点”的案例 Z；结果仍为单峰 + 长尾。
- 2026-02-02: 扩展 `reports/grid2d_blackboard_bimodality/`，加入截图直译失败案例 X 及外边界 sticky 通道 D/E，补充热图/路径/FPT/诊断全套图与失败机理分析；新增截图参数扫描脚本与结果。
- 2026-02-02: 更新 `reports/ring_two_target/` 双目标 lazy ring 报告（无 shortcut/有 shortcut、多峰机制、N-β 相图与三峰示例），英文版完善；重做图1示意与双峰图风格，并扩展两目标吸收机理说明。
- 2026-02-02: 新增 `reports/grid2d_blackboard_bimodality/`，基于黑板图 A/B/C 三套配置输出全套图组（环境/热图/路径/FPT/峰谷/通道分解）与中文报告 `grid2d_blackboard_bimodality_cn.pdf`。
- 2026-01-21: 图说明 PDF 增补四类轨迹标签释义（C0J0/C1pJ0/C0J1p/C1pJ1p）。
- 2026-01-21: 将图说明 PDF 改为单段英文说明文本：`reports/ring_lazy_jump_ext_rev2/fig2_overlap_binbars_beta0.01_x1350_description_en.pdf`。
- 2026-01-21: 新增英文图说明 PDF：`reports/ring_lazy_jump_ext_rev2/fig2_overlap_binbars_beta0.01_x1350_description_en.pdf`。
- 2026-01-21: 调整窗口范围文字为两行并在相邻窗口间交错，避免 K=4 前两窗文字重叠；已重输出图1 PDF。
- 2026-01-21: 进一步改进峰谷标注防重叠算法（基于标签宽度估计与二次纵向错开），并重输出图1 PDF。
- 2026-01-21: 进一步调整峰/谷标注位置（加入横向错开与对齐）以避免 K=4 标签重叠，并重输出图1 PDF。
- 2026-01-21: 调整图1标注避免 K=4 峰/谷标签重叠，并重生成各版本图1 PDF。
- 2026-01-21: 生成更短横轴版本图1（xlim=1..1350）并清理旧版本，仅保留 `reports/ring_lazy_jump_ext_rev2/fig2_overlap_binbars_beta0.01_x1350.pdf`。
- 2026-01-20: 图1窗口改为按 $K$ 分别检测峰谷并重绘，对齐 $K=2$ 的峰/谷；更新图1数据、PDF 与英文说明 docx。
- 2026-01-20: 新增图1英文说明 Word 文件 `reports/ring_lazy_jump_ext_rev2/fig1_explanation_en.docx`。
- 2026-01-20: 重编译 `reports/ring_lazy_jump_ext_rev2/` 中英文 PDF，并输出单独图文件到报告目录。
- 2026-01-20: `reports/ring_lazy_jump_ext_rev2/` 的图1改为上下两幅（K=2/K=4），更新绘图脚本与中英文说明。
- 2026-01-20: 细化 2d_reflecting_bimodality 各代表案例配置卡（走廊几何与通道判据更明确），同步更新中英文 PDF。
- 2026-01-20: 更新 2d_reflecting_bimodality 表~4 的 AW vs exact 速度基准（新增 R7/C3 并刷新数值），重跑基准脚本与中英文 PDF。
- 2026-01-20: 将 2d_reflecting_bimodality 的 AW/Exact 说明与配置卡改写为更叙述性的段落表述，减少分点并重编 PDF。
- 2026-01-20: 新增 S1/S2（无内部 barrier/door 的软通道双轨）并纳入参数/指标/误差表、正文图组与通道判据说明，更新中英文 PDF 与配置汇总。
- 2026-01-20: 新增 NB4 外边界顺时针“传送带”构造（无内部 barrier/door，valley_ratio≈0.062），替换正文代表案例并更新中英文 PDF；加入 NB5（全反射 + global bias + 边界传送带）并纳入正文与配置汇总；同时引入分段 bin + tail smoothing 的 MC 直方图，使 R1/R6/NB4 的 MC 与 Exact/AW 对齐且更平滑；补充 FPT 入门段落与 AW/Exact/MC 的直观对比说明。
- 2026-01-20: 更新 AW vs exact 速度基准（加入 NB5、n_z=32），刷新 CN/EN 速度表与结论措辞；S0 参数拆分为列表以缓解排版警告；英文 PDF 已重编译（中文 PDF 在当前环境缺少 fandol 字体导致编译失败）。
- 2026-01-20: 新增 R7（半透门孔道 + 长绕行）作为“更接近真实”的反射边界示例，补齐 R1/R6/NB4/NB5 的代表案例体系，并更新中英文 PDF、参数/指标表与通道解释。
- 2026-01-20: 修正 2d_reflecting_bimodality 的参考文献作者与年份（PRE 102, 062124 与 arXiv:2311.00464v2），补充 DOI 与 v2 日期。
- 2026-01-20: 在 2d_reflecting_bimodality 中恢复 AW vs exact recursion 的验证说明（摘要与误差表后说明），并重新编译中英文 PDF。
- 2026-01-20: 新增 C3（主动运输轨道 vs 长 detour 回路）构造，加入配置汇总与中英文正文（含参数/指标/通道解释与图组），并更新 PDF。
- 2026-01-19: 在 `reports/grid2d_reflecting_bimodality/` 增补 AW vs exact recursion 速度对比小节，加入低缺陷对照 S0（full AW 实测）；更新基准脚本 `reports/grid2d_reflecting_bimodality/code/benchmark_aw_exact.py` 与结果 `reports/grid2d_reflecting_bimodality/data/aw_exact_speed.json`。
- 2026-01-19: 精简 `reports/grid2d_reflecting_bimodality/` 正文，只保留代表性案例 R1/R6/NB4（其余案例从正文移除），并同步中英文 PDF；新增无内部 barrier/door 的 NB1--NB3 构造与输出。
- 2026-01-18: 扩展 `reports/grid2d_reflecting_bimodality/` 为对标 2d_bimodality 的完整流程（Exact/AW/MC + 环境/热图/路径/通道分解/峰谷诊断），更新中英文报告与图表。
- 2026-01-18: 提升反射边界热图的层次感：掩蔽走廊外区域、限定热图区视野、并用分位数/下限比例调节 LogNorm 颜色范围。
- 2026-01-18: 新增 MB1--MB3 极简双车道构造（local bias=0），分别用 sticky 全段、door 阵列、短 sticky 段实现双峰。
- 2026-01-04: 新增 `reports/ring_lazy_jump_ext_rev2/`，加入同轴叠加与阈值/窗口/不确定性敏感性分析管线，并补充英文版。
- 2026-01-06: 更新 `reports/grid2d_bimodality/` 至 v8，新增 Fig.3 风格图形与 bimodality proof 图，输出 `build/2d_bimodality_cn_v8.pdf` 与 `figures_v8/`。
- 2026-01-06: 更新 `reports/grid2d_bimodality/` 至 v9，新增 B_v2 自动调参与 mixed 边界版本，输出 `build/2d_bimodality_cn_v9.pdf`、`figures/v9/` 与 `outputs/v9/`。
- 2026-01-07: 更新 `reports/grid2d_bimodality/` 至 v10，新增 B_v10 自动调参与 Fig.3 风格图形修订，输出 `2d_bimodality_cn_v10.pdf`、`figures/v10/` 与 `outputs/v10/`。
- 2026-01-07: 更新 `reports/grid2d_bimodality/` 至 v11，新增 fig3v4 风格与 B_v11 调参版，输出 `2d_bimodality_cn_v11.pdf`、`figures/v11/` 与 `outputs/v11/`。
- 2026-01-07: 更新 `reports/grid2d_bimodality/`，新增 fig3v5 风格、C 诊断图与代表性路径标注，输出 `grid2d_bimodality_cn.pdf`、`figures/` 与 `outputs/`。
- 2026-01-08: 继续优化 v12 图形：候选 B strip view 视野收紧、Fig.3 panel 重排（减少留白），路径密度图去除线团并改为代表轨迹+ROI，unwrapped 图 Dx_short/Dx_wrap 标签避让重叠；清理旧版输出与数据，仅保留 v12。
- 2026-01-08: 修复 v12 图10/11/12/27：候选 B strip/heatmap 视野重设、路径密度代表轨迹进一步简化、unwrapped 标签避让重叠；复现命令段落与 schema 说明重排，避免行溢出。
- 2026-01-12: 补全 `reports/grid2d_bimodality/grid2d_bimodality_en.tex` 英文版，与中文版内容对齐。
- 2026-01-12: 重新编译 `reports/grid2d_bimodality/grid2d_bimodality_en.pdf`，页数与中文一致（20 页）。
- 2026-01-12: 统一 `reports/grid2d_bimodality/` 中候选 C 表述（door + sticky + wrap-around，fast/slow 通道说明对齐）。
- 2026-01-12: 修正 `reports/grid2d_bimodality/` 候选 C 通道描述，统一为“早穿门为 fast，晚穿门（含 wrap-around 与 sticky/door 延迟）为 slow”。
- 2026-01-12: 校正文档一致性：明确列随机约定、修正 defect $\eta$ 号、区分 $\tilde F/\tilde f$ 记号、标注候选 C 严格阈值诊断为失败示例，并去除重复 exact recursion 公式。
- 2026-01-12: 修复 v12 诊断一致性：B/C 统一 valley ratio 阈值 0.07，C 使用窗口化两峰判别输出 $(t_{p1},t_v,t_{p2})=(88,279,500)$ 并更新 PDF。
- 2026-01-12: 清理 `2d_bimodality_en` 排版 underfull hbox 警告，调整文本换行与 metrics 路径显示并更新英文 PDF。
- 2026-01-12: 增加收口说明：解释 Fig.1(b) 的 $v_{\max}$ 与正文 valley ratio 关系，并明确 $g_x>0$ 为向左偏置；更新中英文 PDF。
- 2026-01-12: 移除 2d_bimodality 报告内版本标识与 fig3 风格表述，调整为更正式的报告语气并简化“数据与代码可得性”段落，更新中英文 PDF。
- 2026-01-12: 精简表~\ref{tab:aw-errors} 误差指标，移除与 $L^\infty$ 重复的 max abs error 列并同步中英文 PDF。
- 2026-01-12: 2d_bimodality 输出统一为无版本命名（cases.json、figures/、outputs/、candidate_*_metrics.json、2d_bimodality_{cn,en}.pdf），并同步更新复现命令。
- 2026-01-12: 调整 MC 直方图为分段 bin 宽度 + tail smoothing（从 $t_v+30$ 起），改善大 $t$ 噪声与候选 C MC 一致性，并更新图与 PDF。

## Archived on 2026-02-17
- 2026-02-16: 对 `reports/grid2d_rect_bimodality/` 再做一次全量代码/文案/逻辑审计并修正显示层风险点：`phase` 相图色条标签改短（`single/weak/clear`，避免窄版导出时裁切）；one-target 的 FPT 与 hazard 图统一为“淡色原始曲线 + 平滑主曲线”并使峰标记对齐平滑曲线，减少离散锯齿造成的误读。补充扫描诊断字段 `absorbed_mass/survival_tail`，并在 `tt_scan_width_xstart.json`、`ot_scan_width_globalbias.json`、`case_summary.json` 的 `meta` 中写入 `scan_t_max/scan_surv_tol/t_max/surv_tol`；同时将默认时间窗上调为 `scan_t_max=5000`、`t_max=20000`。关键相图结论不变，扫描尾部截断风险显著下降（TT `max tail` 约 `0.404→0.141`，OT `0.257→0.111`）。脚本全量重跑、CSV/表格一致性复核、CN/EN PDF 重新编译通过且无 LaTeX warning。

## Archived on 2026-02-25
- 2026-02-16: 再次做 `reports/grid2d_rect_bimodality/` 全量回归审计并修复一个显示层隐患：one-target 的 FPT/ hazard 图在“未检测到第二峰”时原先会把横轴拉到整段长尾（可到上万步），导致首峰被压扁；现已加入自适应时间窗函数 `suggest_ot_fpt_xmax(...)`，在保留足够尾部信息的前提下避免主峰失真。已同步应用到 `plot_ot_fpt`、`plot_ot_hazard`、`plot_ot_rep_fpt_grid`、`plot_ot_rep_hazard_grid` 并全量重跑/重编译；中英文图注也补充了“子图横轴为自适应窗口”的解释。关键结论保持不变：TT 分支临界宽度仍为 `x0=8:5-9, x0=10:5-8, x0=12:5-6`；OT 在锚点 `x_s=7,x_t=58` 下 `b_x=-0.08` 的 clear 区间仍为 `W_y=8..16`；CN/EN LaTeX 日志无 warning/overfull。

## Archived on 2026-02-25
- 2026-02-16: 对 `reports/grid2d_rect_bimodality/` 做“代码-数据-图表-中英文 LaTeX”全链路复核后，修复一个会影响代表案例排序的隐藏逻辑点：此前若 `valley_over_max=0.0`，排序键里使用 `r.get(... ) or 9.0` 会把 `0.0` 误判为缺失值并错误惩罚最强双峰；现改为显式 `None` 判定（新增 `_opt_float(...)`），并统一用于 two-target/one-target 代表案例排序键。修复后全量重跑脚本与 CN/EN PDF，日志无 warning/overfull，phase 相图与关键结论保持不变（TT clear 分支阈值仍为 `x0=8:5-9, x0=10:5-8, x0=12:5-6`；OT 在锚点 `x_s=7,x_t=58` 下 `b_x=-0.08` 仍为 `W_y=8..16` 的 phase=2）。

## Archived on 2026-02-25
- 2026-02-16: 对 `reports/grid2d_rect_bimodality/` 再做一轮端到端审计（代码逻辑、CSV-表格一致性、代表案例 phase 一致性、`case_summary` 路径完整性、CN/EN `label-ref` 完整性、LaTeX 日志 warning/overfull）。本轮未发现新的数据/逻辑错误；全量重跑 `code/rect_bimodality_report.py` 与中英文 `latexmk` 均通过，关键结论保持不变：TT 仍为分支依赖临界（`x0=8:5-9`, `x0=10:5-8`, `x0=12:5-6`），OT 在锚点 `x_s=7,x_t=58` 下 `b_x=-0.08` 仍在 `W_y=8..16` 为 phase=2。

## Archived on 2026-03-03
- 2026-02-16: 在 `reports/grid2d_rect_bimodality/code/rect_bimodality_report.py` 新增 `purge_case_level_artifacts(...)`，并在 `main()` 开始阶段启用。修复的问题是：历史运行遗留的按 case 命名文件（`outputs/TT_*_fpt.csv`、`outputs/OT_*_fpt.csv` 与对应 `figures/*`）会与当前扫描口径混在一起，造成“同名 case 看起来与当前 phase 相冲突”的假象。现在每次重跑都会先清理旧 case 级产物，再写入当前代表案例，避免报告资产歧义。

## Archived on 2026-03-03
- 2026-02-16: 在 `reports/grid2d_rect_bimodality/code/rect_bimodality_report.py` 新增 `purge_case_level_artifacts(...)`，并在 `main()` 开始阶段启用。修复的问题是：历史运行遗留的按 case 命名文件（`outputs/TT_*_fpt.csv`、`outputs/OT_*_fpt.csv` 与对应 `figures/*`）会与当前扫描口径混在一起，造成“同名 case 看起来与当前 phase 相冲突”的假象。现在每次重跑都会先清理旧 case 级产物，再写入当前代表案例，避免报告资产歧义。

## Archived on 2026-03-03
- 2026-02-16: 对 `reports/grid2d_rect_bimodality/` 再做深度一致性回归并补上 summary 级防护：`case_summary.json` 现在额外记录并校验代表案例的 `outputs/*_fpt.csv`（`rep_series_csv`），且改为“先校验路径再写 summary”以避免异常时落盘不可信 summary。并验证了扩展分支在 `t_max=5000` 与 `t_max=20000` 下 phase 一致（`x0=8/10/12` 无不一致），排除时间窗截断导致的假失稳。
- 2026-02-16: 对 `reports/grid2d_rect_bimodality/` 再次做“代码+语言+逻辑”全链路复核并修复一项流程性隐患：`validate_representative_phase_consistency(...)` 与 `validate_summary_artifact_paths(...)` 之前定义但未接入主流程，现已在 `main()` 中启用；同时将启动清理从 case 级升级为 `purge_generated_artifacts(...)` 全量清理，避免旧扫描表/旧图残留造成的静默污染。已全量重跑脚本与中英文 `latexmk`，相图/代表案例/表格一致，LaTeX 无 overfull/undefined 引用。
- 2026-02-16: 在 `reports/grid2d_rect_bimodality/code/rect_bimodality_report.py` 新增 `purge_case_level_artifacts(...)`，并在 `main()` 开始阶段启用。修复的问题是：历史运行遗留的按 case 命名文件（`outputs/TT_*_fpt.csv`、`outputs/OT_*_fpt.csv` 与对应 `figures/*`）会与当前扫描口径混在一起，造成“同名 case 看起来与当前 phase 相冲突”的假象。现在每次重跑都会先清理旧 case 级产物，再写入当前代表案例，避免报告资产歧义。

## Archived on 2026-03-03
- 2026-02-16: 对 `reports/grid2d_rect_bimodality/` 再做一次“全代码+全图表+中英文文案”复核并完成修正：重新全量跑 `rect_bimodality_report.py`、重编 CN/EN PDF、逐项校验 `case_summary.json`/CSV/表格/图号一致性（含图6/11/17/18/20/21对应资产）、确认 TT 与 OT 阈值结论未漂移。新增一项复现层修订：`2d_rect_bimodality_{cn,en}.tex` 与报告目录 `README.md` 的复现命令补充了 `venv` 创建与依赖安装步骤，避免系统 `python3` 缺包导致无法复现；LaTeX 日志仍无 overfull/undefined/citation 警告。

## Archived on 2026-03-03
- 2026-02-16: 继续对 `reports/grid2d_rect_bimodality/` 做“未提及项”复核后，修正 one-target 代表配置图（图17）的分类标签语义：原先 `phase>=1` 统一写 `double-peak`，现改为 `clear-double / weak-double / single-peak` 三档，避免将 phase=1 与 phase=2 混写；中英文图注同步更新并重跑脚本、重编 CN/EN PDF，图号与数据结论保持一致。

## Archived on 2026-03-03
- 2026-02-16: 对 `reports/grid2d_rect_bimodality/` 做了额外“deep audit”回归：验证 `--quick` 与 full 两条执行路径均能稳定完成；随后恢复 full 产物并对 `case_summary` 引用、图号映射（图6/7/8/9/10/11/12/17/18/19/20/21）与 CSV/表格阈值陈述做自动对账，未发现新增不一致项。最终构建日志仍无 overfull/undefined/citation。

## Archived on 2026-03-03
- 2026-02-16: 对 `reports/grid2d_rect_bimodality/` 做了一次额外“全代码+全图+全文案”复核：重跑 `rect_bimodality_report.py`、强制重编中英文 PDF、逐项核对图号映射（图6/9/10/11/12/20/21）、代表案例相位与表格/CSV 阈值一致性，并对关键图做转 PNG 目检（含双峰标注、时间窗、色条排版）。本轮未发现新增逻辑或文案错误，现有结论保持不变。

## Archived on 2026-03-03
- 2026-02-16: 对 `reports/grid2d_rect_bimodality/` 再做全链路审计并修复两项隐藏问题：(1) `ot_anchor_selection.tex` 的 `first loss` 之前按 `+1` 计算，会落在未扫描宽度（例如 17）；现改为“从真实扫描宽度列表取下一个宽度”，并按扫描步长压缩 clear 区间显示（现为 `8-16`，`first loss=18`）。(2) one-target 代表 FPT/hazard 网格移除淡色原始曲线叠层，仅保留平滑主曲线，避免离散锯齿被误判为“算法峰”。同时统一 two-target 谷深记号为 `$p_v/\\max(p_1,p_2)$`，并在中英文正文补充 splitSep 与总曲线双峰判据的区别说明。已全量重跑脚本并重编 CN/EN PDF，日志无 warning/overfull。

## Archived on 2026-03-03
- 2026-02-16: 对 `reports/grid2d_rect_bimodality/` 再做一轮全链路审计后修复两项一致性问题：(1) `tt_critical_width_by_xstart.tex` 的 `first loss width` 也改为“从真实扫描宽度列表取下一个采样点”（不再固定 `+1`，避免非 1 步长时伪宽度）；(2) 重新全量跑脚本并重编中英文 PDF（中文使用 `latexmk -xelatex`），核对 `phase/峰标注/表格` 逻辑一致，`build/*_{cn,en}.log` 中无 overfull/undefined/citation warning。

## Archived on 2026-03-03
- 2026-02-16: 对 `reports/grid2d_rect_bimodality/` 再次进行“全代码+全图表+中英文文案”深度复核，并修复三项一致性风险：`tt_scan_overview.tex` 的 `best min(p1,p2)` 仅在 `phase>=1` 条件下统计（避免单峰宽度出现误导性高值）；固定分支宽度样本选择去重并在粗步长时自动补齐；`x0=8/10/12` 扩展临界扫描改为沿 `tt_width_step` 采样（避免步长不一致导致伪临界）。已全量重跑脚本和 CN/EN PDF，日志仍无 overfull/undefined/citation 警告。

## Archived on 2026-03-03
- 2026-02-16: 对 `reports/grid2d_rect_bimodality/` 再做一次“全代码 + 全图表 + 中英文文案”深度回归并修正两处未显式写清的问题：其一，在中英文正文的 one-target 部分新增定量结论段，明确锚点 `(x_s,x_t)=(7,58)` 下 `b_x=-0.08` 仅在 `W_y=8,10,12,14,16` 为 clear-double、`W_y>=18` 退化为 weak-double，而 `b_x=-0.12` 为全域 weak、`b_x∈{-0.04,0,0.08}` 为全域 single；其二，复现命令中英文档编译口径统一为 `latexmk -pdf ... grid2d_rect_bimodality_en.tex`（中文仍 `-xelatex`）。已全量重跑脚本、重编 CN/EN PDF，并通过 CSV↔表格↔正文自动核对；日志无 overfull/undefined/citation。

## Archived on 2026-03-03
- 2026-02-16: 对 `reports/grid2d_rect_bimodality/` 再做一轮“代码-数值-图表-中英文文案”深度复核并修复一项数值稳定性边界：在 `run_exact_two_target_rect` 与 `run_exact_one_target_rect` 中引入非负质量投影（`project_mass_nonnegative`），消除极小浮点漂移导致的 `survival>1` 或非单调尾部风险，同时不改变模型机制与参数。修复后全量重跑脚本、重编 CN/EN PDF，并复核 `max_survival_over1=0`、`max_survival_increase=0`、TT/OT 分解恒等误差为 `0`、`case_summary` 路径引用完整、LaTeX 日志无 overfull/undefined/citation。

## Archived on 2026-03-03
- 2026-02-16: 对 `reports/grid2d_rect_bimodality/` 再次深度回顾后新增“运行时一致性硬校验”：在 `rect_bimodality_report.py` 加入 `validate_tt_series_consistency(...)` 与 `validate_ot_series_consistency(...)`，并接入 two-target/one-target 的扫描、扩展分支、代表案例与锚点预扫描流程。校验项包括非负性、`survival<=1`、生存概率单调、通道分解恒等与逐步质量守恒；任一不满足将立即报错，避免“图像正常但底层质量守恒失效”的隐患。已全量重跑脚本与中英文 PDF，结论与相图不变，日志无 overfull/undefined/citation。

## Archived on 2026-03-03
- 2026-02-16: 对 `reports/grid2d_rect_bimodality/` 再做一轮“按你前序指令”的回归复核并补上防回归约束：在 `rect_bimodality_report.py` 新增 `validate_tt_representative_branch_coverage(...)`，强制 two-target 代表案例覆盖关键分支中所有存在 clear-double 的分支（当前为 `x0=8,10,12`）；同时同步更新中英文图注，明确图6类代表图覆盖这三条分支。已全量重跑脚本并重编 CN/EN PDF，当前代表集已恢复为 `TT_W05_X08/TT_W08_X08/TT_W05_X10/TT_W08_X10/TT_W05_X12/TT_W06_X12`，无 overfull/undefined/citation warning。

## Archived on 2026-03-03
- 2026-02-16: 按“所有报告逐个检查”的要求，完成 `reports/*/*.tex` 全量主文档审计（共 33 份，逐一 `latexmk` 回归）与 `reports/**/code/*.py` 语法检查（129 文件 `py_compile` 全通过）。本轮修复两项真实构建问题：`cross_luca_regime_map_en_smoke.tex` 的 `\\texttt` 下划线转义错误（导致 Missing `$`），以及 `cross_luca_regime_map_cn_smoke.tex` 的引擎匹配问题（审计流程改为文件名含 `_cn` 一律用 `xelatex`）。同时对 overfull 较多的旧报告导言区补充/增强 `\\emergencystretch`（blackboard/deriv/lazy_flux/two_target_ring/valley 等）。最终结果：33/33 主文档可构建，0 missing file、0 undefined reference/citation、0 undefined control sequence；仍有部分历史 overfull（不影响结论与可复现性）已记录待后续精修。

## Archived on 2026-03-03
- 2026-02-16: 再次按“所有报告逐个检查并修复”的要求完成全仓回归：逐一复核 `reports/*/*.tex`（33 份主文档）与 `reports/**/code/*.py`（116 份脚本）。本轮重点修复了跨报告排版与复现块问题（`two_target_ring` 的并排图 overfull、`deriv_k2` 长公式行溢出、`2d_blackboard_bimodality/lazy_flux/valley_dst/method_comparison` 的超长命令行、`luca_regime_map` 的宽表格与推荐矩阵）。最终状态：`py_compile` 全通过；33/33 TeX 构建成功；`undefined reference/citation/control sequence/missing file` 全为 0；`Overfull \\hbox` 全为 0（全报告清零）。

## Archived on 2026-03-03
- 2026-02-16: 按“所有报告逐个检查”再次完成全仓深度回归（33 份主 TeX + 116 份 `code/*.py`）：`latexmk` 全通过、`overfull/undefined reference/citation/control sequence/missing file/duplicate destination` 全为 0。除已完成的构建与排版修复外，本轮新增修正两类潜在问题：`luca_regime_map` 与 `2d_two_target_double_peak/method_comparison` 的 PDF 锚点冲突（`hypertexnames=false`），以及 `reports/README.md`/`docs/README.md` 中过时描述、重复命令和编译口径不一致（已统一为可直接复现的当前口径，补齐 `2d_rect_bimodality` 与 `lazy_jump_ext_rev2` 入口）。

## Archived on 2026-03-03
- 2026-02-16: 按“检查所有报告、逐个修潜在问题”的要求完成第三轮全仓审计：新增修复 `luca_regime_map_{cn,en,cn_smoke,en_smoke}` 与 `2d_two_target_double_peak/method_comparison_{cn,en}` 的超链接锚点冲突风险（`hypertexnames=false`），并更新 `reports/README.md` 与 `docs/README.md` 的索引与复现命令口径（去重、补齐 `2d_rect_bimodality` 与 `lazy_jump_ext_rev2`）。回归结果：33/33 TeX 成功，`overfull/undefined/duplicate-destination` 均为 0；`reports/**/code/*.py` 共 116 文件 `py_compile` 全通过。

## Archived on 2026-03-03
- 2026-02-16: 完成“所有报告逐个审计”回归：新增统一脚本 `scripts/audit_reports.py`（修复 `_cn_smoke` 引擎识别为 `xelatex`），全量检查 `reports/*/*.tex` 共 33 份与 `reports/**/code/*.py` 共 116 份，结果为 `33/33` 构建成功、`py_compile` 全通过、`overfull/underfull/undefined/missing/duplicate destination` 全为 0。并修复两处版式潜在问题（`method_comparison_en.tex` 摘要坏行、`valley_dst/inputs/flux_validation_cn.tex` 英文长串导致 underfull）及复现命令口径错误：中文统一 `*_cn.tex -> latexmk -xelatex`，英文统一 `*_en.tex -> latexmk -pdf`（已修 `two_target_ring/README.md`、`lazy_jump_ext/README_ext.md`、`lazy_jump_ext/sections/repro_{cn,en}.tex`、`2d_rect_bimodality/README.md`、`2d_blackboard_bimodality/README.md`、`2d_reflecting_bimodality/README.md`、`2d_blackboard_bimodality_{cn,en}.tex` 与本汇总文档）。

## Archived on 2026-03-03
- 2026-02-16: 按“图6格点不够清楚 + 想确认更宽 double peak 与临界含义”的反馈，更新 `reports/grid2d_rect_bimodality/`：在 `rect_bimodality_report.py` 的 two-target/one-target 几何绘图中加入逐格晶格线并每 5 格加粗参考线（图6及同类配置图更易读）；中英文正文补充“临界=宽度阈值（非单一时间阈值）”说明，并给出 near-critical 峰时刻示例（`x0=10` 分支 `Wy=6: t_{p1},t_{p2}=72,851`；`Wy=7: 78,881`）。全量重跑脚本并重编 CN/EN PDF，结论保持：two-target clear 仅到 `Wy=6`（`x0=10`），one-target 在锚点 `(x_s,x_t)=(7,58)`、`b_x=-0.08` 下 clear 区间仍为 `Wy=8..16`，首失稳 `Wy=18`。

## Archived on 2026-03-03
- 2026-02-16: 按“所有格点格子更清楚 + 图9/图10不要拉伸”的新要求再次更新 `reports/grid2d_rect_bimodality/`：进一步加重几何图逐格网格线与每 5 格参考线（`_draw_lattice_grid`），并把同类网格叠加到条件占据热图面板（`_draw_heatmap_panel`）以统一“每个格子可读”。同时把 `plot_tt_env_heatmaps` 的画布高度策略改为显式非拉伸导向，保留 `equal` 几何比例并提高细长矩形可读性；图9/10对应图注保持“geometry-preserving / 不做拉伸”。全量重跑脚本并重编 CN/EN PDF，日志无 overfull/undefined/citation 警告。

## Archived on 2026-03-03
- 2026-02-16: 按“固定起点后扫宽度 + phase=1 可见性 + 图1/图17可读性 + 运行缓存复用”的要求更新 `reports/grid2d_rect_bimodality/`：`rect_bimodality_report.py` 新增 `--tt-width-sweep-xstart` 与 `--tt-width-sweep-target-widths`（默认 `5,6,7,8,14,24`，显式纳入 phase=1 过渡宽度），且 `pick_clear_width_sweep_tt` 在指定分支不在扫描网格时自动回退到最近 `x_start`；图1符号面板增大画布并用 `bbox_inches='tight'` 避免边缘裁切；图17（one-target 代表配置）进一步加清晰格点与右下角配置卡（`size,(x_s,x_t),corr_h,wall_m,delta_c,delta_o`）；新增扫描结果复用机制（默认开启 `--reuse-scan-data`，可用 `--no-reuse-scan-data` 关闭），复跑时优先读取 `tt_scan_width_xstart.{csv,json}` 与 `ot_scan_width_globalbias.{csv,json}`，减少重复全扫描。

## Archived on 2026-03-03
- 2026-02-16: 按“复现命令放在文末 + 新增一组通道厚度实验”的要求更新 `reports/grid2d_rect_bimodality/`：在 `rect_bimodality_report.py` 正式接入 one-target 走廊厚度敏感性扫描（`--ot-corridor-halfwidth-values`，默认 `0,1,2,3`，对应通道宽度 `1/3/5/7` 格），新增数据与缓存复用 `data/ot_scan_corridor_halfwidth.{csv,json}`，并输出 `figures/ot_corridor_phase_vs_width.pdf`、`figures/ot_corridor_sep_vs_width.pdf`、`tables/ot_corridor_width_summary.tex`。默认参数下结果显示：1 格宽通道（`h=0`）在焦点偏置分支仅 weak-double；加厚到 `3/5/7` 格后 clear-double 区间显著扩展。中英文 TeX 同步新增该小节，并保持复现命令段落位于文档最后；脚本复跑已验证三套扫描均可复用缓存（TT/OT/OT-corridor）。
- 2026-02-16: 新增 one-target 走廊厚度敏感性扫描（固定锚点 `(x_s,x_t)=(7,58)`，`W_y=8..28`、`b_x∈{-0.12,-0.08,-0.04,0,0.08}`，比较 `corridor_halfwidth=0,1,2,3`）：结果写入 `reports/grid2d_rect_bimodality/data/ot_scan_corridor_halfwidth.csv` 与 `ot_scan_corridor_halfwidth_summary.json`。关键结论：`halfwidth=0`（真 1 格宽通道）在 `b_x=-0.08` 下仅 weak-double、无 clear-double；`halfwidth=1` 出现 clear 区间 `W_y=8..16`；`halfwidth=2` clear 扩展到 `8..26`；`halfwidth=3` 在 `b_x=-0.08` 下 `W_y>=10` 基本全为 clear（`W_y=8` 反而单峰），说明适度加厚通道会显著增强双峰稳健性，但过窄通道难形成清晰双峰。

## Archived on 2026-03-03
- 2026-02-16: 修复 `reports/grid2d_rect_bimodality/` 图22右侧显示不全问题，并同步排查同类 phase 相图：问题来自色条文字靠右边界被裁切。已在 `rect_bimodality_report.py` 的 `plot_phase_map(...)` 与 `plot_ot_corridor_phase_vs_width(...)` 统一增加右侧留白并启用 `bbox_inches='tight'` 导出，重新生成图件后确认图22（`ot_corridor_phase_vs_width.pdf`）及其他 phase 图（如 `ot_phase_width_bx.pdf`、`tt_phase_width_xstart.pdf`）右侧标签显示完整；中英文 PDF 已重编译通过。

## Archived on 2026-03-03
- 2026-02-16: 按“对偏置也扫描一组”的要求，在 `reports/grid2d_rect_bimodality/` 新增 one-target 全局偏置向量二维扫描（固定锚点 `x_s=7,x_t=58`、固定宽度 `W_y=12`，扫描 `b_x∈{-0.12,-0.08,-0.04,0,0.08}` 与 `b_y∈{-0.08,-0.04,0,0.04,0.08}`）：`rect_bimodality_report.py` 新增 `--ot-global-by-values`、`--ot-bias-scan-width`，并接入缓存复用 `data/ot_scan_bias2d.{csv,json}`，输出 `figures/ot_bias2d_phase_bx_by.pdf`、`figures/ot_bias2d_sep_bx_by.pdf` 与 `tables/ot_bias2d_phase_overview.tex`。结果显示 clear-double 主要集中在 `b_x=-0.08` 且 `b_y∈[-0.04,0.04]`，`b_x>=-0.04` 基本退化为 single；同时中英文文档新增“Global-bias vector scan”小节并重编通过。

## Archived on 2026-03-03
- 2026-02-17: 完成 P1 深拆分第二部分（`ring_valley_dst` + `grid2d_reflecting/blackboard`）的工程化落地：新增 `src/vkcore/ring/valley_dst/` 与 `src/vkcore/grid2d/reflecting_blackboard/` 模块层（`cli/model/cases/pipeline/plots/io/types`），6 个主入口脚本全部改为 `<60` 行薄封装；新增 `src/vkcore/grid2d/bimod_legacy_imports.py` 统一管理 `aw_pgf/fpt_exact_mc/plot_*` 导入桥接并移除旧 `2d_bimodality/code` 路径注入。`ring_valley_dst` 注册表入口补全 `second_peak_scan.py` 与 `second_peak_shortcut_usage_mc.py`，并完成 `--help` / smoke / `py_compile` / `reportctl audit --fast` / `pytest` / `check_docs_paths` 回归全通过。

## Archived on 2026-03-03
- 2026-02-24: 完成仓库级 Web 上线工程化主链路：新增 `site/`（Next.js 静态导出 + 双语路由 `/`,`/en`,`/cn` + 报告详情交互图 + theory MDX/KaTeX + agent-sync 页面），新增 `scripts/build_web_data.py`（14 报告预计算数据与资产映射到 `site/public/data/v1` + `site/public/artifacts`）、`scripts/build_agent_sync.py`（`manifest.json`/`reports.jsonl`/`events.jsonl` + `artifacts/checks/*.json` + `crosscheck_report.json`）、`scripts/validate_web_data.py`（schema 校验）；新增 schema `schemas/web_report.schema.json` 与 `schemas/agent_sync_v1.schema.json`，扩展 `scripts/reportctl.py` 子命令 `web-data`/`agent-sync`/`web-build`/`web-preview`，并新增 GitHub Pages 工作流 `.github/workflows/site-pages.yml`。已完成 `web-data -> agent-sync -> validate -> next build` 全链路验证与 `pytest` 回归通过。

## Archived on 2026-03-03
- 2026-02-25: 继续推进 Web 端可解释性修复：`site/src/lib/render-pages.tsx` 将 KaTeX 渲染切换为严格模式（`throwOnError:true` + `strict:'error'`），并在公式卡片/逻辑链中显示可折叠的渲染告警（含 source/context 与 parse error 原因）；`site/src/components/ReportPlotPanel.tsx` 新增 log 坐标门控（数据含非正值时禁用 log）、自动回退线性坐标的持久提示文案，避免坐标自动切换造成解释歧义。回归通过：`python3 scripts/validate_web_data.py` 与 `cd site && npm run build`。

## Archived on 2026-03-03
- 2026-02-25: 完成 Web 数据文本质量第二轮收敛：`scripts/build_web_data.py` 新增 `repair_common_math_noise(...)` 并贯通 summary/claim/narrative/section-card 清洗链路，补强 `summary_penalty` 与候选过滤（高噪声短句直接淘汰），并在章节卡片生成中加入去重与 body 级回退文案；`scripts/validate_web_data.py` 新增 malformed token 规则（如 `a p3`、`K 2,3`、`P:0.2`、`, all`）；`scripts/build_book_content.py` 与 `scripts/build_publication_pdf.py` 同步统一清洗规则；`scripts/run_openclaw_review.py` 增加 `--model` 强制模型入口。已回归通过：`python3 scripts/build_web_data.py`、`python3 scripts/validate_web_data.py`、`python3 scripts/build_book_content.py`、`python3 scripts/build_publication_pdf.py`。

## Archived on 2026-03-03
- 2026-03-03: 新增项目延续 skill：`skills/valley-k-small-continuation/SKILL.md`（含 `references/core-checklist.md`、`references/report-map.md`、`references/research-conventions.md`），用于后续 agent 在本仓库统一执行“报告复现→文档维护→校验回归→交付交接”的标准流程。

## Archived on 2026-03-03
- 2026-03-03: 完成本地-远端-网站同步增强：`scripts/build_web_data.py` 新增 `repo_sync.json` 生成（仓库分区、文件索引、SHA256、更新时间、GitHub 链接与预览摘要）；`site/src/lib/render-pages.tsx` 新增 `/repo-sync` 双语页面与导航入口；`scripts/reportctl.py` 新增 `sync-local-remote` 子命令（支持 `--no-site-build/--no-fetch`）用于统一执行数据同步并显示本地与 `origin` ahead/behind 状态。已验证 `python3 scripts/reportctl.py sync-local-remote --mode full` 全链路通过（含 `npm ci` 与 `next build`）。

## Archived on 2026-03-03
- 2026-03-03: 新增通用“持续优化保活”机制（macOS launchd）：`scripts/keepalive_ctl.py` + `scripts/keepalive_runner.py` + `scripts/keepalive`。该机制不预置任务，支持用户传入任意命令进行无限轮询执行；具备 `up/down/status/logs/run-once` 控制接口、`RunAtLoad + KeepAlive` 崩溃自恢复、失败指数退避（上限 3600s）、以及运行观测文件（`artifacts/keepalive/runs/<job>/{heartbeat.json,latest.json,history.jsonl,errors.jsonl,runner.pid}`）。README 与 `scripts/README.md` 已补充推荐调用方式与 Codex 示例命令。

## Archived on 2026-03-03
- 2026-03-03: 完成“脏工作区降噪”优化：新增 `scripts/worktree_hygiene.py`（`summary`/`focus`，将源码改动与生成产物改动分桶统计并输出聚焦状态）；增强 `scripts/cleanup_local.py`，新增 `--include-runtime` 以清理 `.openclaw`、`artifacts/loop`、`artifacts/keepalive`、`artifacts/checks/content_iteration` 等运行时目录；并在 `.gitignore` 补充运行时噪音规则（如 `artifacts/keepalive/`）。目标是减少日常 `git status` 噪音并让迭代聚焦源码改动。

## Archived on 2026-03-03
- 2026-03-03: 完成 keepalive 方案自适应升级：`scripts/keepalive_ctl.py` 新增 `up-codex` 与任务画像（`optimize/review/build/monitor`），可根据任务文本自动推断 profile 并使用对应 interval/timeout；新增 `profiles` 查询默认策略；新增极简入口 `scripts/ka`（`start/start-as/status/logs/stop`）用于一句话触发；并在 `skills/valley-k-small-continuation/SKILL.md` 与 `AGENTS.md` 同步加入 keepalive 自然语言触发映射，降低后续对话调用摩擦。

## Archived on 2026-03-03
- 2026-03-03: 新增报告 `reports/grid2d_membrane_near_target/`（`grid2d_membrane_near_target_{cn,en}.pdf`）：完成两条新研究线并产出相图/分离度图/窗口分解图。线A为 one-target corridor 半透膜（对称与非对称），结果显示在当前锚点参数下 clear-double 主要集中于接近全反射端，低渗透率与非对称膜可保留 weak-double，且 L×R 四类窗口分解显示 valley/第二峰由泄漏+回撤类主导；线B为无 corridor 双-target 且近目标放起点附近，代表案例实现近远目标质量近均衡并得到 clear-double。本报告已补齐典型代表配置几何图（`membrane_rep_sym_geometry.pdf`、`membrane_rep_asym_geometry.pdf`、`two_target_rep_geometry.pdf`），并在中英文文稿新增“committor + 2×2 分类”方法参考段。数据入口：`data/summary.json`、`data/corridor_membrane_symmetric_scan.csv`、`data/corridor_membrane_asymmetric_scan.csv`、`data/two_target_nearstart_scan.csv`。

## Archived on 2026-03-03
- 2026-03-03: 新增报告 `reports/grid2d_two_walker_encounter_shortcut/`（`grid2d_two_walker_encounter_shortcut_{cn,en}.pdf`）：完成“Product of two generating functions”附录中 Eq.(A1) 与 Eq.(A8) 的稳健数值验证流程（轮廓可行性检查 + 自适应离散 + 半径不变性/收敛诊断），并实现 2D 双 walker encounter + directed shortcut 的精确时域算法（联合分布迭代）。在代表配置下观测到 shortcut 强度驱动的单峰→双峰过渡（约 `beta>=0.30` 出现两峰），并给出 shortcut-used / no-shortcut 两类通道分解图。

## Archived on 2026-03-03
- 2026-03-03: 完成自动化优化流程的 Isambard 条件路由增强：`scripts/keepalive_ctl.py` 为 `up-codex` 的 `optimize` profile 注入“按情况使用 `isambard-automation`”策略（大规模/长耗时任务优先 `isbard doctor/auth -> submit/status/fetch`，小规模 smoke 优先本地）；`scripts/ka` 的 `start` 在未给任务文案时改为显式走 optimize 默认策略；`skills/valley-k-small-continuation/SKILL.md` 新增 Isambard 触发条件与回退规则，便于自动化 agent 在每轮优化中稳定选择本地/远端执行路径。

## Archived on 2026-03-03
- 2026-03-03: 对 `reports/ring_two_walker_encounter_shortcut/` 完成一轮稳健性增强：新增 onset 细扫描 `data/encounter_onset_refine.csv` 与判据敏感性扫描 `data/encounter_onset_sensitivity.csv`，并产出 `figures/encounter_onset_sensitivity.pdf`。当前结果为 coarse onset `beta≈0.16`、细扫名义 onset `beta≈0.15`，在检测参数扰动下首次 onset 区间约 `[0.11,0.16]`（中位数约 `0.14`）。同时修复 FPT overlay 的时域截断复用问题（覆盖曲线统一按 `t_max_case` 生成）。

## Archived on 2026-03-03
- 2026-03-03: 新增报告 `reports/ring_two_walker_encounter_shortcut/`（`ring_two_walker_encounter_shortcut_{cn,en}.pdf`）：按 1D ring encounter 目标完成 Eq.(A1)$\\Leftrightarrow$Eq.(A8) 稳健数值例程（轮廓可行性检查 + 自适应离散 + 半径不变性 + sanity cases），并实现双 walker 首次相遇精确时域算法 `J_{t+1}=P_1^\\top J_t P_2`（对角线吸收）。在代表配置 `N=101,q=0.70,g1=0.70,g2=-0.40,n0=5,m0=55,src=5,dst=70` 下，shortcut 扫描显示约从 `beta≈0.16` 进入 clear bimodal；`beta=0.20` 时两峰约在 `t1=108,t2=321`，峰比 `0.306`、谷比 `0.126`，并通过 shortcut-used / no-shortcut 通道分解解释早晚峰来源。

## Archived on 2026-03-03
- 2026-03-03: keepalive 新增本地后台模式（不依赖 launchd）：`scripts/keepalive_ctl.py` 增加 `up-local` 与 `up-codex-local`，`scripts/ka` 增加 `start-local/start-as-local`；`status` 新增 `local_runner_pid/local_runner_alive` 诊断，`down` 现在会同时尝试停止本地 runner。用于修复 macOS 受保护目录（Desktop/OneDrive）下 launchd 的 `Operation not permitted` 阻塞场景。

## Archived on 2026-03-03
- 2026-03-03: 针对 `reports/ring_two_walker_encounter_shortcut/` 做文档一致性修复：补齐 README 的 fixed-site 产物索引（`fixedsite_drift_scan.csv`、`fixedsite_summary.json`、`encounter_fixedsite_examples.pdf`、`encounter_fixedsite_gphase.pdf`、`fixedsite_example_table.tex`），并完成脚本重跑与中英文 PDF 重编译验证（当前 `ring_two_walker_encounter_shortcut_{cn,en}.pdf` 均可稳定构建）。

## Archived on 2026-03-03
- 2026-03-03: 对 `reports/ring_two_walker_encounter_shortcut/` 完成一轮 `<10 分钟` 本地快速验证与自动修复：执行 `.venv/bin/python reports/ring_two_walker_encounter_shortcut/code/two_walker_ring_encounter_report.py` 与 `python3 scripts/reportctl.py build --report ring_two_walker_encounter_shortcut --lang en/cn` 均通过；修复文稿中的 `hyperref` 数学标题告警（`\\texorpdfstring`）与中文 `xeCJK` 等宽字体告警（补充 `\\setCJKmonofont`），并为 `scripts/reportctl.py` 的 `build` 子命令增加 `--lang en/cn` / `cn/en` 直通双语构建支持，当前双语 PDF 可稳定无该类告警构建。

## Archived on 2026-03-03
- 2026-03-03: 持续优化 `reports/ring_two_walker_encounter_shortcut/` 的 1D ring encounter 报告呈现：将已生成但未入文稿的 `figures/encounter_onset_refine.pdf` 正式并入中英文主文（`ring_two_walker_encounter_shortcut_{en,cn}.tex`），并完成你要求的本地快测链路复跑（`.venv/bin/python .../two_walker_ring_encounter_report.py` + `python3 scripts/reportctl.py build --report ring_two_walker_encounter_shortcut --lang en/cn`）。当前双语 PDF 均可稳定构建，且 onset 细扫图与敏感性图已同时在正文展示。

## Archived on 2026-03-03
- 2026-03-03: keepalive 的 Codex 执行模型默认切换为 `gpt-5.3-codex` + `xhigh` 推理强度：`scripts/keepalive_ctl.py` 的 `up-codex`/`up-codex-local` 现默认注入 `-m gpt-5.3-codex -c model_reasoning_effort=\"xhigh\"`，并新增 `--reasoning-effort` 显式覆盖入口；`README.md`、`scripts/README.md`、`AGENTS.md`、`skills/valley-k-small-continuation/SKILL.md` 同步更新。

## Archived on 2026-03-03
- 2026-03-03: 对 `reports/ring_two_walker_encounter_shortcut/code/two_walker_ring_encounter_report.py` 完成一轮性能优化与回归：`run_ring_encounter` 新增按 `beta` 复用缓存（长时窗切片复用 + overlay betas 全时窗预取 + `P1` 缓存），`run_fixedsite_drift_study` 新增 drift 转移矩阵按需缓存（含非网格 `g` 的懒构建），并修复回归中的 `KeyError(g=0.7)`。复测 `.venv/bin/python .../two_walker_ring_encounter_report.py` 与 `python3 scripts/reportctl.py build --report ring_two_walker_encounter_shortcut --lang en/cn` 均通过；`cProfile` 下 `first_encounter_any` 调用由 `37 -> 32`，总耗时约 `4.01s -> 3.84s`（约 4%）。

## Archived on 2026-03-03
- 2026-03-03: 执行“全仓持续优化 + 1D encounter 优先”一轮闭环：本地基准运行 `reports/ring_two_walker_encounter_shortcut/code/two_walker_ring_encounter_report.py` 用时约 `2.93s`（按策略判定为本地快测，不触发 Isambard 提交）；修复 `README.md`、`scripts/README.md`、`docs/RESEARCH_SUMMARY.md` 的文档路径校验问题，补齐 `reports/grid2d_two_walker_encounter_shortcut/notes/` 与 `reports/ring_two_walker_encounter_shortcut/notes/`；新增 `tests/test_ring_two_walker_encounter_shortcut.py` 做关键产物与指标回归守护；`pytest` 全通过，`site` 经 `npm ci` 后 `npm run build` 通过；已启动 keepalive 本地优化任务 `ring-encounter-opt`（profile=`optimize`，模型 `gpt-5.3-codex`，`xhigh`）。

## Archived on 2026-03-03
- 2026-03-03: 按“本地 <10 分钟优先、超长任务再转 Isambard”策略，对 `reports/ring_two_walker_encounter_shortcut/` 完成新一轮闭环：`.venv/bin/python .../two_walker_ring_encounter_report.py` 运行约 `2.69s`，`python3 scripts/reportctl.py build --report ring_two_walker_encounter_shortcut --lang en/cn` 全通过，`pytest -q tests/test_ring_two_walker_encounter_shortcut.py` 全通过，因此本轮未触发 `isambard-automation` 远端提交流程。同步对 `two_walker_ring_encounter_report.py` 做小幅性能/维护性优化：首遇传播循环预缓存转置矩阵（`P^T`），并统一“空峰值指标”返回结构（`empty_peak_metrics`）以降低判据分支维护成本。

## Archived on 2026-03-03
- 2026-03-03: 持续优化 `reports/grid2d_membrane_near_target/`（按“本地快速优先”策略执行，单轮脚本重跑约分钟级，未触发 Isambard 远端提交流程）：`code/membrane_near_target_report.py` 将 corridor 基线更新为 `h=2, delta_core=1.00, delta_open=0.55`，并把膜渗透率扫描在近零区加密（对称 `kappa` 扩展至 `0,0.002,0.005,0.01,0.015,...`；非对称 `kappa_up/kappa_down` 同步扩展）。clear-double 覆盖提升为：对称扫描 `14/84`（其中 `kappa>0` 为 `7`），非对称扫描 `8/100`（非对称 clear 为 `6`，且 `kappa>0` 为 `7`）；代表案例更新为对称 `kappa=0.002` 与非对称 `(kappa_up,kappa_down)=(0.002,0)`，并通过脚本内一致性断言保证代表案例在对应表格中必然出现。同步修复 `membrane_asymmetric_topcases.tex` 的语义一致性（仅保留非对称样本），重生成图表/CSV/summary 并重编 `grid2d_membrane_near_target_{cn,en}.pdf`。

## Archived on 2026-03-03
- 2026-03-03: 按“持续自动优化 `grid2d_membrane_near_target`”新指令启动 keepalive 任务 `grid2d_membrane_near_target`（`profile=optimize`，模型 `gpt-5.3-codex`，`xhigh`），并将任务优先级固化为：优先提升 clear-double 覆盖、补全代表图与表格/正文一致性、每轮必须执行 `python3 scripts/update_research_summary.py`。在本机 Desktop/OneDrive 路径下 `launchd` 触发 `Operation not permitted`（无法打开 `scripts/keepalive_runner.py`）后，已自动切换 `start-local` 本地后台 runner 并进入 round 1。任务内已明确 Isambard 路由：若单轮预计 `>20` 分钟或需大规模并行，按 `isbard doctor/auth -> submit -> status -> fetch`；远端失败则回退本地 smoke 并记录原因与结果。

## Archived on 2026-03-03
- 2026-03-03: 针对 `reports/ring_two_walker_encounter_shortcut/` 执行你指定的本地 `<10` 分钟快速闭环：`.venv/bin/python reports/ring_two_walker_encounter_shortcut/code/two_walker_ring_encounter_report.py` 约 `2.93s` 完成，`python3 scripts/reportctl.py build --report ring_two_walker_encounter_shortcut --lang en/cn` 双语构建通过；按策略未触发远端提交流程。已启动本地 keepalive 任务 `ring-two-walker-encounter-opt`（`profile=optimize`，`gpt-5.3-codex`，`xhigh`），任务指令内已固化“>20 分钟/大规模并行时走 `isbard doctor/auth -> submit/status/fetch`，远端失败回退本地 smoke 并继续循环”；本机 `isbard doctor` 预检为 `SSH_OK`。

## Archived on 2026-03-03
- 2026-03-03: 按“先本地 `<10` 分钟快测、超长再走 Isambard”执行 `reports/ring_two_walker_encounter_shortcut/` 新一轮闭环：`.venv/bin/python reports/ring_two_walker_encounter_shortcut/code/two_walker_ring_encounter_report.py`（约 `2.67s`）、`python3 scripts/reportctl.py build --report ring_two_walker_encounter_shortcut --lang en/cn`（双语通过）、`pytest -q tests/test_ring_two_walker_encounter_shortcut.py`（`3 passed`）均完成。同步修复 onset 细扫潜在漏检：当 coarse 扫描未检出双峰时，细扫网格改为覆盖完整 `beta_scan_min~beta_scan_max`（新增 `build_refine_beta_grid`），避免仅围绕中点细扫造成边界 onset 漏检；并新增单测 `test_refine_grid_falls_back_to_full_range_when_coarse_onset_missing` 守护该逻辑。本轮未触发 `isambard-automation` 远端提交流程。

## Archived on 2026-03-03
- 2026-03-03: 按你指定流程完成 `reports/ring_two_walker_encounter_shortcut/` 新一轮本地 `<10` 分钟闭环并持续优化（未触发 Isambard）：`.venv/bin/python reports/ring_two_walker_encounter_shortcut/code/two_walker_ring_encounter_report.py`（约 `2.8s`）、`python3 scripts/reportctl.py build --report ring_two_walker_encounter_shortcut --lang en/cn`（双语通过）、`.venv/bin/python -m pytest -q tests/test_ring_two_walker_encounter_shortcut.py`（`3 passed`）。本轮新增 onset 一致性分析产物：`data/encounter_onset_agreement.csv` 与 `figures/encounter_onset_agreement.pdf`，并将 detector-agreement 阈值写入 `data/case_summary.json`（`beta_agreement_50=0.14`、`beta_agreement_75=0.15`）；中英文文稿已同步加入新图与阈值解读，README 与测试清单已更新。

## Archived on 2026-03-03
- 2026-03-03: 按你要求对 `reports/ring_two_walker_encounter_shortcut/` 执行新一轮“本地 `<10` 分钟优先”的持续优化闭环：`.venv/bin/python reports/ring_two_walker_encounter_shortcut/code/two_walker_ring_encounter_report.py`（`real 2.84s`）与 `python3 scripts/reportctl.py build --report ring_two_walker_encounter_shortcut --lang en/cn`（`real 2.86s`）均完成；期间自动捕获并修复一处 LaTeX 生成转义错误（`encounter_key_metrics.tex` 中误写 `\\beta` 导致英文构建失败），修复后双语 PDF 均通过，且 `pytest -q tests/test_ring_two_walker_encounter_shortcut.py`（`real 0.60s`）继续 `3 passed`。本轮新增“关键指标自动入表”能力：脚本现在输出 `tables/encounter_key_metrics.tex`（coarse/refined onset、agreement@50/75、代表峰位与质量守恒），中英文正文均已引用该表，减少持续迭代时手填数字漂移风险；未触发 Isambard 远端分支。

## Archived on 2026-03-03
- 2026-03-03: 继续按你指定节奏优化 `reports/ring_two_walker_encounter_shortcut/`：本地快测链路 `.venv/bin/python reports/ring_two_walker_encounter_shortcut/code/two_walker_ring_encounter_report.py`（`real 2.81s`）与 `python3 scripts/reportctl.py build --report ring_two_walker_encounter_shortcut --lang en/cn`（`real 1.90s`）均通过，未触发 Isambard 远端分支。新增“转移矩阵自动修复”稳健性增强：`build_ring_transition` 现在会对 `q/g/beta` 做有限值+区间钳制，并对每行概率执行随机矩阵修复（负值/非有限值清理与按需归一化），降低越界参数导致传播异常的风险；同步补充两条单测（越界参数自愈、非有限参数拒绝），`pytest -q tests/test_ring_two_walker_encounter_shortcut.py` 现为 `5 passed`。

## Archived on 2026-03-03
- 2026-03-03: 按你要求继续对 `reports/ring_two_walker_encounter_shortcut/` 做本地 `<10` 分钟闭环优化：先后执行 `.venv/bin/python reports/ring_two_walker_encounter_shortcut/code/two_walker_ring_encounter_report.py` 与 `python3 scripts/reportctl.py build --report ring_two_walker_encounter_shortcut --lang en/cn` 均通过，未触发 Isambard 远端分支；本轮新增“shortcut 通道占比”定量诊断链路：脚本现输出 `figures/encounter_shortcut_share.pdf`，并在 `data/case_summary.json` 的 `representative.shortcut_share` 与 `tables/encounter_key_metrics.tex` 中自动写入占比指标（如 `share_t1_window≈0.734`、`share_t2_window≈0.071`、`t_switch_share50=155`、`cum_share_tmax≈0.121`），中英文文稿已同步纳入新图与解释；`.venv/bin/python -m pytest -q tests/test_ring_two_walker_encounter_shortcut.py` 结果为 `5 passed`。

## Archived on 2026-03-03
- 2026-03-03: 按你指定闭环对 `reports/ring_two_walker_encounter_shortcut/` 完成本地 `<10` 分钟一轮持续优化：`.venv/bin/python reports/ring_two_walker_encounter_shortcut/code/two_walker_ring_encounter_report.py` 与 `python3 scripts/reportctl.py build --report ring_two_walker_encounter_shortcut --lang en/cn` 均通过，未触发 Isambard 分支。本轮新增 fixed-site 相图占比自动汇总：脚本输出 `tables/fixedsite_phase_summary.tex`，并在 `data/fixedsite_summary.json` 增加 `phase_summary`（single/weak/clear 的点数与占比）；中英文文稿均已纳入该表（`ring_two_walker_encounter_shortcut_{en,cn}.tex`），便于后续迭代直接比较全局相位分布而非仅看代表案例。

## Archived on 2026-03-03
- 2026-03-03: 按“`reports/ring_two_walker_encounter_shortcut` 持续优化”指令完成新一轮本地 `<10` 分钟闭环：`.venv/bin/python reports/ring_two_walker_encounter_shortcut/code/two_walker_ring_encounter_report.py`（`real 3.69s`）与 `python3 scripts/reportctl.py build --report ring_two_walker_encounter_shortcut --lang en/cn`（`real 1.53s`）均通过，且 `pytest -q tests/test_ring_two_walker_encounter_shortcut.py` 为 `5 passed`；本轮未触发 Isambard 分支。新增优化为 fixed-site 漂移相图分辨率加密（`g_grid` 从 `7x7` 提升到 `13x13`，扫描点 `49 -> 169`），并在 `outputs/run_summary.json` 增补 fixed-site 的 single/weak/clear 点数与占比，便于后续 keepalive 各轮快速对比相位覆盖变化。

## Archived on 2026-03-03
- 2026-03-03: 按你指定流程对 `reports/ring_two_walker_encounter_shortcut/` 完成新一轮本地 `<10` 分钟闭环：`.venv/bin/python reports/ring_two_walker_encounter_shortcut/code/two_walker_ring_encounter_report.py` 与 `python3 scripts/reportctl.py build --report ring_two_walker_encounter_shortcut --lang en/cn` 均通过，且 `.venv/bin/python -m pytest -q tests/test_ring_two_walker_encounter_shortcut.py` 为 `5 passed`；本轮未触发 Isambard 远端分支。新增优化为 ring-size onset 稳健性扫描（`N={81,101,121,141}`）：脚本新增产物 `data/encounter_onset_n_scan.csv`、`figures/encounter_onset_n_scan.pdf`、`tables/encounter_n_scan_table.tex`，并把 `n_scan_summary/n_scan_rows` 写入 `data/case_summary.json` 与 `outputs/run_summary.json`；中英文报告已同步纳入该图表与文字解读。

## Archived on 2026-03-03
- 2026-03-03: 按你指定流程完成 `reports/ring_two_walker_encounter_shortcut/` 新一轮本地 `<10` 分钟闭环：`.venv/bin/python reports/ring_two_walker_encounter_shortcut/code/two_walker_ring_encounter_report.py` 与 `python3 scripts/reportctl.py build --report ring_two_walker_encounter_shortcut --lang en/cn` 均通过，且 `.venv/bin/python -m pytest -q tests/test_ring_two_walker_encounter_shortcut.py` 通过（`5 passed`）；本轮未触发 Isambard 远端分支。新增 onset 一致性“陡峭度”指标链路：脚本自动产出 `beta_agreement_25/50/75` 与过渡宽度 `beta_agreement_width_25_75=0.04`、`beta_agreement_width_50_75=0.01`，并同步写入 `tables/encounter_key_metrics.tex`、`data/case_summary.json`、`outputs/run_summary.json`；中英文报告已补充该指标解释。已启动本地 keepalive 任务 `ring-two-walker-encounter-shortcut-loop`（`optimize`，`gpt-5.3-codex`，`xhigh`），任务提示中已固化“>20 分钟/大规模并行时先 `isbard doctor`（必要时 `isbard auth`）再 `submit/status/fetch`，失败回退本地 smoke 并继续循环”，并已执行 `isbard doctor`（`SSH_OK`）。

## Archived on 2026-03-03
- 2026-03-03: 对 `reports/ring_two_walker_encounter_shortcut/` 完成新一轮本地 `<10` 分钟闭环并自动修复排版：执行 `.venv/bin/python reports/ring_two_walker_encounter_shortcut/code/two_walker_ring_encounter_report.py` + `python3 scripts/reportctl.py build --report ring_two_walker_encounter_shortcut --lang en/cn`（`real 9.29s`）全部通过，未触发 Isambard 分支。新增 ring-size onset 的“窗口外回收”机制：当主窗口 `beta<=0.30` 未检出 clear onset 时，自动扩展到 `beta<=0.50`（步长 `0.02`）寻找首次 clear 点；本轮将 `N=81` 从“空值”解析为扩展 onset `beta≈0.38`。对应产物已同步到 `data/encounter_onset_n_scan.csv`、`tables/encounter_n_scan_table.tex`、`figures/encounter_onset_n_scan.pdf`、`outputs/run_summary.json`（`onset_n_scan_valid=4`, `onset_n_scan_valid_window=3`, `onset_n_scan_extended=1`），并更新中英文正文解释与标注（含 `^*` 扩展标记与 `\beta^\dagger` 解析值说明）。

## Archived on 2026-03-03
- 2026-03-03: 按你本轮指令完成 `reports/ring_two_walker_encounter_shortcut/` 本地快测闭环并补齐回归守护：`.venv/bin/python reports/ring_two_walker_encounter_shortcut/code/two_walker_ring_encounter_report.py`（`real 9.27s`）与 `python3 scripts/reportctl.py build --report ring_two_walker_encounter_shortcut --lang en/cn`（`real 4.04s`）均通过，未触发 Isambard 分支（未达到 `>20` 分钟/大规模并行条件）；修复 `tests/test_ring_two_walker_encounter_shortcut.py` 对 `onset_beta<=0.30` 的过严断言，使其与 `onset_source=extended` 的扩展窗口机制（`beta<=0.50`）一致，并校验 `main/extended/none` 三类来源字段一致性。`pytest -q tests/test_ring_two_walker_encounter_shortcut.py` 已通过。持续循环任务 `ring-two-walker-encounter-loop` 当前处于本地 keepalive 运行中（最新轮次成功）。

## Archived on 2026-03-03
- 2026-03-03: 按“持续优化 `reports/ring_two_walker_encounter_shortcut/` 并不停循环”再完成一轮本地 `<10` 分钟闭环：`.venv/bin/python reports/ring_two_walker_encounter_shortcut/code/two_walker_ring_encounter_report.py` 与 `python3 scripts/reportctl.py build --report ring_two_walker_encounter_shortcut --lang en` / `--lang cn` 均通过，未触发 Isambard 分支（未达到 `>20` 分钟或大规模并行条件）；同时确认 keepalive 任务 `ring-two-walker-encounter-loop` 仍在本地 runner 持续运行（`local_runner_alive: yes`），并同步执行 `python3 scripts/update_research_summary.py` 刷新汇总索引。

## Archived on 2026-03-03
- 2026-03-03: 本轮按“持续优化 `reports/ring_two_walker_encounter_shortcut/` 并不停循环”执行本地 `<10` 分钟快测闭环：`.venv/bin/python reports/ring_two_walker_encounter_shortcut/code/two_walker_ring_encounter_report.py`（`real 9.50s`）与 `python3 scripts/reportctl.py build --report ring_two_walker_encounter_shortcut --lang en/cn`（`real 3.13s`）均通过；未触发 Isambard 分支。`ring-two-walker-encounter-loop` 已以 `start-as-local` 方式持续运行，避免 Desktop/OneDrive 路径下 launchd 的 `Operation not permitted` 干扰；并继续按轮次要求同步 `docs/RESEARCH_SUMMARY.md` + `python3 scripts/update_research_summary.py`。

## Archived on 2026-03-03
- 2026-03-03: 按“全仓持续自动优化（覆盖 reports、docs、site、scripts、src、tests）且优先 `reports/ring_two_walker_encounter_shortcut`”完成一轮本地闭环：`python3 -m py_compile scripts/*.py src/vkcore/**/*.py tests/*.py`、`.venv/bin/python reports/ring_two_walker_encounter_shortcut/code/two_walker_ring_encounter_report.py`、`latexmk` 双语构建、`.venv/bin/pytest -q` 与 `cd site && npm run build` 均通过；`isbard doctor` 预检为 `SSH_OK`（当前无 >20 分钟任务，未触发 submit/status/fetch）。持续循环任务已启动为 `repo-optimize-loop`（`optimize`, `gpt-5.3-codex`, `xhigh`）；因 Desktop/OneDrive 路径下 launchd `Operation not permitted`，已自动回退并切换 `start-as-local` 后台 runner 持续执行。

## Archived on 2026-03-03
- 2026-03-03: 按“全仓持续自动优化，优先 `reports/ring_two_walker_encounter_shortcut`”完成本轮闭环：本地快测链路 `.venv/bin/python reports/ring_two_walker_encounter_shortcut/code/two_walker_ring_encounter_report.py`、`python3 scripts/reportctl.py build --report ring_two_walker_encounter_shortcut --lang en/cn`、`.venv/bin/python -m pytest -q tests` 全通过；修复 `site` 自动化阻塞（新增 `site/.eslintrc.json`，安装 `eslint@8.57.0` 与 `eslint-config-next@14.2.5`），`cd site && npm run lint && npm run build` 通过。已启动本地 keepalive 循环任务 `repo-optimize-full-loop`（`optimize`, `gpt-5.3-codex`, `xhigh`，`interval=600s`）；`isbard doctor` 预检 `SSH_OK`，本轮未触发远端 submit/status/fetch（无 >20 分钟或大规模并行任务）。

## Archived on 2026-03-03
- 2026-03-03: 对 `reports/grid2d_membrane_near_target/` 补充“代表分类图例 + committor 数学机理”说明：新增图 `figures/membrane_class_legend.pdf`（2×2 分类定义与峰谷窗口主导类别转移示意），并在中英文文稿中把 committor 机理写成可引用公式链（离散边值问题、$L/R$ 事件严格定义、renewal 分解与窗口占比公式），使分类标签与峰谷形成机制可一一对应。

## Archived on 2026-03-03
- 2026-03-03: 按“把 1D ring shortcut 的具体图和实例放到报告里”完成 `reports/ring_two_walker_encounter_shortcut/` 的正文增强：新增代表实例表 `tables/encounter_shortcut_rep_case.tex` 与代表实例图 `figures/encounter_shortcut_rep_case.pdf`（在 `beta=0.20` 案例标注 detector `(t1,tv,t2)` 与显著峰 `P1,P2,P3`），并已写入中英文文稿对应章节；随后顺序重编 `ring_two_walker_encounter_shortcut_{cn,en}.pdf`，确认新图表均成功入文。

## Archived on 2026-03-03
- 2026-03-03: 对 `reports/ring_two_walker_encounter_shortcut/` 做“机理与定义”增强，定位为首个完整 encounter 专题稿：新增中英文统一符号/指标定义（`T_any/T_delta`、`f,S`、`t1/t2/tv`、`R_peak/R_valley`、shortcut 占比与质量守恒误差），补充双峰数学机理链 `f_enc=f_sc+f_no` 与“通道接力 + ring 绕行”解释，并新增 Luca（Bristol, Giuggioli）文献对应段与参考文献条目（PRE 2020 + multi-target arXiv 2024）；双语 PDF 已重编通过（17 页版本）。

## Archived on 2026-03-03
- 2026-03-03: 按“持续优化 `reports/ring_two_walker_encounter_shortcut/`，每轮重跑+双语构建+关键测试+自动修复”完成本轮增强：在 `two_walker_ring_encounter_report.py` 新增自动结论片段生成（`tables/encounter_consistency_summary_{cn,en}.tex` 与 `tables/encounter_nscan_summary_{cn,en}.tex`），中英文正文改为 `\input` 自动片段以消除手写数字漂移；新增一致性守护脚本 `code/check_encounter_consistency.py`（图/表存在性、代表峰序与通道占比、n-scan 计数与摘要一致性、双语文稿自动片段引用校验）；新增连续迭代脚本 `code/continuous_optimize_loop.py`（每轮 codegen + CN/EN 构建 + `py_compile` + consistency check，LaTeX 失败自动 `latexmk -C` 重试一次）。本地两轮实跑均通过（单轮约 9 秒级），未触发 Isambard 分支（明显低于 >20 分钟门槛）。

## Archived on 2026-03-03
- 2026-03-03: 按“持续优化 `reports/grid2d_membrane_near_target/`、优先提升 clear-double 覆盖并保持图表/正文一致”完成新一轮本地闭环（单轮约分钟级，未触发 Isambard 分支）：`code/membrane_near_target_report.py` 新增 two-target 多轮候选扫描优化与失败重试机制（`baseline -> dense_bx_near_dy3 -> dense_bx_near_dy4`，失败自动跳过下一轮并记录），自动选择 `dense_bx_near_dy3`；覆盖提升为 two-target `56/81 -> 97/117`（phase2 ratio `0.691 -> 0.829`），对称膜 `54/140 -> 106/196`，非对称膜 `89/225 -> 204/225`。代表 two-target 更新为 `(b_x,d,\Delta y)=(0.04,3,3)`，`P(near)/P(far)\approx 0.444/0.556`，峰位约 `(15,1080)`；中英文正文同步改写并重编 `grid2d_membrane_near_target_{cn,en}.pdf`，确保图、表、文一致。

## Archived on 2026-03-03
- 2026-03-03: 按“持续优化 `reports/ring_two_walker_encounter_shortcut/`，每轮重跑+中英文构建+关键测试，聚焦图表与结论一致性”完成本轮闭环：强化 `code/check_encounter_consistency.py`，新增对 `encounter_key_metrics.tex`、`encounter_consistency_summary_{cn,en}.tex`、`encounter_nscan_summary_{cn,en}.tex` 与 `case_summary.json/run_summary.json/encounter_onset_n_scan.csv` 的片段级一致性核对；`code/continuous_optimize_loop.py` 每轮新增 `pytest -q tests/test_ring_two_walker_encounter_shortcut.py`；`README.md` 同步更新流程说明。执行 `.venv/bin/python reports/ring_two_walker_encounter_shortcut/code/check_encounter_consistency.py`、`.venv/bin/python -m pytest -q tests/test_ring_two_walker_encounter_shortcut.py` 与 `../../.venv/bin/python code/continuous_optimize_loop.py --rounds 3` 全部通过，三轮总是成功（约 `11.53s/9.53s/9.19s`）；本轮未触发 Isambard 远端分支（未达到 >20 分钟或大规模并行条件）。

## Archived on 2026-03-03
- 2026-03-03: 按“持续自动优化全仓并优先加固 `reports/ring_two_walker_encounter_shortcut`”完成本轮可落地改动：在 `two_walker_ring_encounter_report.py` 新增代表案例质量守恒审计图 `figures/encounter_mass_balance.pdf`（累计首遇质量、survival 与残差 `|1-\sum_{\tau\le t}f(\tau)-S(t)|`），并接入主生成流水线；中英文正文同步加入该图与解释（`ring_two_walker_encounter_shortcut_{cn,en}.tex`），`README.md` 同步补全产物清单；一致性守护同步扩展到新图（`code/check_encounter_consistency.py` 与 `tests/test_ring_two_walker_encounter_shortcut.py`）。期间首次重跑触发一次 codegen 报错（matplotlib 数学文本 `\le` 解析），已修复为 `\leq` 并复跑 `../../.venv/bin/python code/continuous_optimize_loop.py --rounds 1` 全通过（codegen + CN/EN PDF + py_compile + consistency + pytest，约 `10.26s`），未触发 Isambard 远端分支（本轮明显低于 >20 分钟门槛）。

## Archived on 2026-03-03
- 2026-03-03: 按“全仓持续自动优化且优先加固 `reports/ring_two_walker_encounter_shortcut`”完成新一轮可落地增强：在 `code/two_walker_ring_encounter_report.py` 新增 ring-size onset 来源/搜索窗口诊断图 `figures/encounter_onset_source_window.pdf`（显式区分 `main/extended/none` 并叠加每个 `N` 的 `onset_search_max_beta`）；中英文正文 `ring_two_walker_encounter_shortcut_{en,cn}.tex` 新增该图与“窗口效应 vs 物理缺失”解释；`README.md`、`code/check_encounter_consistency.py`、`tests/test_ring_two_walker_encounter_shortcut.py` 同步纳入新图守护。已执行 `../../.venv/bin/python code/continuous_optimize_loop.py --rounds 1` 全通过（codegen + CN/EN PDF + py_compile + consistency + pytest，约 `10.64s`），并用 `.venv/bin/pytest` 跑仓库级 smoke（report/docs/registry/web payload + target report）通过；本轮未触发 Isambard 分支（未达 >20 分钟或大规模并行门槛）。

## Archived on 2026-03-03
- 2026-03-03: 按“持续自动优化全仓并优先加固 `reports/ring_two_walker_encounter_shortcut`”完成新一轮落地修改：`code/two_walker_ring_encounter_report.py` 的 ring-size onset 表 `tables/encounter_n_scan_table.tex` 新增显式列 `onset source` 与 `\beta_{max}`（不再只靠 `^*`/`>x` 注记），并将来源标签标准化为 `\texttt{main|extended|none}`；中英文正文 `ring_two_walker_encounter_shortcut_{en,cn}.tex` 同步补充“窗口效应审计”说明与表注；`tests/test_ring_two_walker_encounter_shortcut.py` 新增对上述表头与扩展标签的回归守护。已执行 `../../.venv/bin/python code/two_walker_ring_encounter_report.py`、`../../.venv/bin/python code/check_encounter_consistency.py`、`.venv/bin/python -m pytest -q tests/test_ring_two_walker_encounter_shortcut.py`、`latexmk` 双语重编，均通过；本轮未触发 Isambard 分支（本地单轮分钟级，未达 >20 分钟/大规模并行门槛）。

## Archived on 2026-03-03
- 2026-03-03: 按“把 phase 定义详细写入报告”完成方法段升级：`reports/grid2d_membrane_near_target/grid2d_membrane_near_target_{cn,en}.tex` 的“phase/sep-score 可复现定义”已扩展为代码同款数学规则，显式给出 `find_two_peaks` 条件（平滑窗口、相对峰高、最小峰距、谷深/主导性阈值）、`has_double` 定义、one-target 与 two-target 的分段分类公式（`phase=0/1/2`），并明确 `phase=1` 的含义为“检测到双峰但未达 clear-double 阈值”。

## Archived on 2026-03-03
- 2026-03-03: 针对 no-corridor 双峰示例图可读性再优化：`two_target_rep_doublepeak_example` 左图改为尾部增强线性坐标（首峰裁剪并标注真实峰值 `p1*`），右图对数坐标下限固定为 `10^{-6}` 以避免超低量级视觉噪声并突出 valley→peak2 结构；中英文图注同步更新。对应实现位于 `reports/grid2d_membrane_near_target/code/membrane_near_target_report.py` 的 `plot_two_target_doublepeak_example`。

## Archived on 2026-03-03
- 2026-03-03: 对 `reports/grid2d_membrane_near_target/` 进一步完成投稿向修订闭环：`L×R` 分类从 MC 计数升级为扩展状态空间精确分解（`augmented_state_exact`），新增 `q*={0.4,0.5,0.6}` 鲁棒性表 `tables/membrane_qstar_sensitivity.tex` 与 `data/membrane_qstar_sensitivity.csv`，并把代表窗口分类结果写入 `tables/membrane_window_classes.tex`（`peak1` 主导 `L0R0`、`peak2` 主导 `L0R1`）；修复并增强配置示意图可视化（箭头/标注防遮挡，所有 PDF 同步导出 PNG），确认 no-corridor clear-double 代表案例仍为 `(b_x,d,\Delta y)=(0.04,3,3)`、`(t_{p1},t_v,t_{p2})=(15,498,1080)`、`P_{near}/P_{far}\approx0.444/0.556`。自动化任务 `membrane-near-target-opt` 已改为本地 keepalive（`gpt-5.3-codex`, `xhigh`, `local_runner_alive: yes`）以规避 OneDrive/launchd 权限限制。

## Archived on 2026-03-03
- 2026-03-03: 对 `reports/grid2d_membrane_near_target/` 完成 committor 机理“详细版”落地：中英文方法段新增 hitting-time 定义、离散 Dirichlet 问题的线性系统形式 `(I-P_UU)q_U=P_UB 1`、`N_mem/N_ret` 计数定义、renewal 展开与峰谷窗口分量关系；同时新增“committor 实现细节”小节（A/B 集合取法、固定点求解阈值、`q*=0.5`、MC 样本量）及“committor 导向总结/后续方向”（扩展状态空间精确分解、`q*` 鲁棒性、splitting committor 与对称性破缺对照）。双语 PDF 已重编通过（CN 13 页，EN 12 页）。

## Archived on 2026-03-03
- 2026-03-03: 对 `reports/ring_two_walker_encounter_shortcut/` 按审稿意见完成一轮“定义-算法-图表”同步增强并重编双语 PDF：统一峰指标口径为 `R_peak=min/max` 并显式补充有向比 `R_dir=f(t2)/f(t1)`；新增多峰 `t2` 选择规则（timescale score，写入中英文正文）；补充 selfloop 模式 shortcut 注入公式 `p_sc=beta(1-q)`（src 自环扣减、src->dst 注入）；加入 fixed-site 的 parity 解释图 `encounter_fixedsite_parity_compare.pdf` 与 clear 占比解释（`157/169=0.929`）；新增并入报告三张诊断图 `encounter_peakcount_vs_beta.pdf`、`encounter_t2_old_vs_new.pdf`、`encounter_onset_scaling.pdf`；代码侧新增 `beta=0` 相对坐标降维精确校验（max diff 机器精度）与 `timescale` 检测器输出 CSV（`encounter_beta_scan_timescale.csv`、`encounter_beta_scan_compare_detectors.csv`）。已执行 `.venv/bin/python reports/ring_two_walker_encounter_shortcut/code/two_walker_ring_encounter_report.py`、`latexmk` 中英文编译、`python3 -m py_compile .../two_walker_ring_encounter_report.py` 全通过。keepalive 任务 `ring-two-walker-encounter-shortcut-loop` 已重启为 `start-as-local optimize`（`gpt-5.3-codex`, `xhigh`，`local_runner_alive: yes`）以规避 OneDrive 路径下 launchd 权限拦截。

## Archived on 2026-03-03
- 2026-03-03: 按“持续优化 `reports/ring_two_walker_encounter_shortcut/` 且优先修复峰比定义/多峰选峰/fixed-site parity 一致性”完成新一轮本地闭环：`two_walker_ring_encounter_report.py` 现将 `timescale detector` 设为主口径（`case_summary.json` 新增 `scan_detector_mode=timescale`，并保留 `scan_legacy` 与 `encounter_beta_scan_compare_detectors.csv` 供对照）；自动摘要文本把峰比明确为 `R_peak=min/max`，与有向比 `R_dir=f(t2)/f(t1)` 分离；fixed-site parity 说明同步为与代码一致的形式 `\tilde f(0)=f(0), \tilde f(m)=f(2m-1)+f(2m)`（并注明首遇场景 `f(0)=0` 与 `t≈2m` 映射）。中英文正文 `ring_two_walker_encounter_shortcut_{cn,en}.tex` 与一致性脚本 `check_encounter_consistency.py` 已同步更新。执行 `.venv/bin/python reports/ring_two_walker_encounter_shortcut/code/continuous_optimize_loop.py --rounds 1` 全通过（codegen/build_cn/build_en/py_compile/consistency/pytest，单轮约 `11.46s`）；本轮按策略未触发 Isambard 远端分支（不属于 >20 分钟或大规模并行任务）。

## Archived on 2026-03-03
- 2026-03-03: 按“持续自动优化 `reports/grid2d_membrane_near_target/`，并按阈值路由 Isambard”完成一轮闭环：先执行 `isbard doctor` 与 `isbard auth`（均成功，SSH 与证书有效），随后因本地单轮实测仅 `~55.9s`（明显低于 10 分钟）按策略走本地快速验证而未触发 `submit/status/fetch`。`code/membrane_near_target_report.py` 新增 no-corridor clear-score 代表点选择（`clear_score = sep_mode * (1-valley/max) * (0.30 + min(Pnear,Pfar))`）与 splitting committor 统计闭环；代表 two-target 已更新为 `(b_x,d,\Delta y)=(0.07,2,3)`，`Pnear/Pfar≈0.326/0.674`，`(t_{p1},t_v,t_{p2})=(11,307,739)`，`sep≈2.22`，`valley/max≈0.019`，`clear-score≈1.36`。新增一致性结果：`q_far(x_s)=0.674289` 与 `P_far=0.674289` 的差仅 `~2e-8`。中英文文稿已同步补充 splitting committor 机理段，并重编通过 `grid2d_membrane_near_target_{cn,en}.pdf`；同时重新拉起 keepalive 任务（`./scripts/ka start-as optimize ...` + `./scripts/ka start-as-local optimize ...`），当前状态 `launchd_loaded: yes`、`local_runner_alive: yes`、`round: 2 running`。

## Archived on 2026-03-03
- 2026-03-03: 按“持续优化 `reports/ring_two_walker_encounter_shortcut/`、优先修复峰比定义/多峰选峰/fixed-site parity 一致性”完成本轮闭环：`two_walker_ring_encounter_report.py` 新增严格区间 valley 提取（`t_v` 在 `(t_1,t_2)` 内优先选取，并统一到 legacy/timescale/K=2 coarse 三个检测器），自动摘要 `encounter_consistency_summary_{cn,en}.tex` 现同步报告 `R_peak=min/max` 与 `R_dir=f(t_2)/f(t_1)`，fixed-site 表头与正文补充“粗粒化指标在 `\tilde f(m)` 上计算、时间映射 `t\approx2m`”说明；`check_encounter_consistency.py` 同步加入 `scan_detector_mode=timescale` 与 parity 文案守护。执行 `../../.venv/bin/python code/continuous_optimize_loop.py --rounds 1` 全通过（codegen/build_cn/build_en/py_compile/consistency/pytest，单轮 `13.26s`，`real 13.36s`），按策略未触发 Isambard（明显低于 >20 分钟阈值，无大规模并行作业）。

## Archived on 2026-03-04
- 2026-03-03: 对 `reports/grid2d_membrane_near_target/` 完成新一轮“no-corridor clear-instance + committor 质检”增强：`code/membrane_near_target_report.py` 新增跨候选扫描汇总 `data/two_target_candidate_scans.csv`（本轮候选总计 `315` 点、clear `248` 点），并把 clear 实例从“selected grid 内代表点”扩展为“全候选中 showcase-score 最大点”；当前 clear-instance 为 `spec=baseline, (b_x,d,\Delta y)=(0.12,2,2)`，`sep≈2.49`、`valley/max≈0.003`、`peak_ratio≈0.114`、`min-margin≈0.014`。新增产物 `figures/two_target_no_corridor_clear_instance.pdf` 与 `tables/two_target_no_corridor_clear_instance.tex`，中英文正文同步加入并解释 phase=2 五阈值裕量与 `\varepsilon_split=|q_far(x_s)-P_far|` 自动质检；双语 PDF 已重编通过。按策略本轮继续本地执行（单轮 codegen 约 `56s`，未达 >20 分钟），未触发 Isambard `submit/status/fetch`。
