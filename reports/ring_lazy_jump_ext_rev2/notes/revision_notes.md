# REVISION_NOTES (v2)

1) 问题：图2将 f(t) 与分类柱状拆成不同面板，窗口与比例没有在同一坐标系对齐 → 影响：读者难以判断窗内比例与峰谷位置的对应关系 → 修正：在同一主轴上用三段全宽栈叠条替代 bin 底色，并用混合变换绘制 → 验证：`figures/fig2_overlap_binbars_beta0.01_x1350.pdf` 三段 bar 覆盖各自窗口且无 inset/twin 轴。
2) 问题：窗口定义依赖隐式 delta 与峰位选择，缺少显式区间 → 影响：复现与对比困难 → 修正：JSON 输出显式 `bin_intervals`，并在图2与数据表中统一引用 → 验证：`data/fig2_bins_bars_beta0.01.json` 含 peak1/valley/peak2 区间且 plot 脚本对范围做校验。
3) 问题：beta* 选择过程不易审计（阈值组合未集中记录） → 影响：审稿难确认选择是否稳健 → 修正：新增阈值敏感性网格扫描与热图 → 验证：`outputs/sensitivity/threshold_sweep.csv` 与 `threshold_sweep_heatmap.pdf`。
4) 问题：复现步骤分散在正文后段 → 影响：读者无法快速复现关键图 → 修正：在 v2 前置最短命令链与输出路径约定 → 验证：`ring_lazy_jump_ext_rev2_cn.tex` 的“复现说明”小节。
5) 问题：关键图脚本/输入/输出未形成可追踪表 → 影响：数据来源不透明 → 修正：新增“数据来源表”列出脚本、输入与输出 → 验证：v2 tex 中的表格明确列出 fig2 与敏感性图。
6) 问题：图2柱状比例没有不确定性尺度 → 影响：MC 采样误差无法评估 → 修正：新增 MC 不确定性脚本输出 CI，并在图2中可选显示误差条 → 验证：`outputs/sensitivity/mc_uncertainty.csv` 与 `plot_fig2_overlap_binbars.py --show-ci`。
7) 问题：窗口边界/宽度改变是否影响结论未检查 → 影响：结论稳健性存疑 → 修正：新增 shift+width 两种扰动的窗口敏感性分析与可视化 → 验证：`outputs/sensitivity/bin_shift_summary.csv` 与 `bin_shift_plot.pdf`。
8) 问题：输出命名与 schema 未规范化 → 影响：后续自动化难以复用 → 修正：制定 fig2 JSON schema、示例输入、标准 ft-csv，并在 Makefile 固化命名 → 验证：`data/fig2_bins_bars.schema.json` + `data/ft_schema.example.csv` + Makefile。
9) 问题：结论段缺少模型/符号速查 → 影响：读者需要在正文中回溯定义 → 修正：新增 K=2/4、jump-over、C/J 四类的速查段 → 验证：v2 tex 前置“模型与符号速查”。
10) 问题：敏感性分析未成为正式章节 → 影响：对稳健性的陈述不足 → 修正：在正文增加“敏感性分析”章节并引用三类敏感性图 → 验证：v2 tex 正文包含三张图与结论句。
