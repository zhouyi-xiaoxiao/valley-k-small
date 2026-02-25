# Reports

本目录下每个子文件夹对应一个报告（自包含）：
- `*.tex` / `*.pdf`：报告源码与编译产物
- `code/`：生成该报告所需的脚本/模块
- `figures/`、`data/`、`tables/`、`inputs/`、`outputs/`、`sections/`：报告引用的图与数据（按需存在）

命名建议：
- 主报告文件统一与目录名一致：单语 `<folder>.tex`，双语 `<folder>_cn.tex` / `<folder>_en.tex`（PDF 同名）。
- 额外说明文档统一为 `note_<slug>.tex`（`<slug>` 1-2 个短词）。

## 报告索引
- `reports/ring_lazy_jump/`: lazy ring + shortcut 的 jump-over 机制主报告（`ring_lazy_jump_{cn,en}.pdf`）。
- `reports/ring_lazy_jump_ext/`: jump-over 扩展（beta/N sweep + tail 机制，`ring_lazy_jump_ext_{cn,en}.pdf`）。
- `reports/ring_lazy_jump_ext_rev2/`: jump-over 扩展 v2 修订版（新增图2同轴叠加与敏感性分析，`ring_lazy_jump_ext_rev2_{cn,en}.pdf`）。
- `reports/ring_lazy_flux/`: K=2 lazy ring 的解析/数值双峰研究（`ring_lazy_flux_{cn,en}.pdf`）。
- `reports/ring_valley/`: non-lazy valley regime notes（`ring_valley.pdf`）。
- `reports/ring_valley_dst/`: 固定 N,K 扫 dst 的 second-peak 调制（`ring_valley_dst_{cn,en}.pdf`）。
- `reports/ring_deriv_k2/`: K=2 解析推导与补充笔记（`ring_deriv_k2.pdf`, `note_k2.pdf`, `note_rewire_lazy.pdf`）。
- `reports/grid2d_bimodality/`: 2D N×N lattice biased/lazy random walk 双峰构造（`grid2d_bimodality_cn.pdf`, `grid2d_bimodality_en.pdf`）。
- `reports/grid2d_reflecting_bimodality/`: 2D N×N lattice 全反射边界双峰构造（`grid2d_reflecting_bimodality_cn.pdf`, `grid2d_reflecting_bimodality_en.pdf`）。
- `reports/grid2d_blackboard_bimodality/`: 黑板图风格配置报告，当前聚焦走廊端点起止案例 Z/S（`grid2d_blackboard_bimodality_{cn,en}.pdf`）。
- `reports/ring_two_target/`: 双目标 lazy ring（无 shortcut/有 shortcut）多峰报告（`ring_two_target_{cn,en}.pdf`）。
- `reports/grid2d_two_target_double_peak/`: 2D 双目标（反射边界 + 局部 bias）double peak 条件报告（`grid2d_two_target_double_peak_{cn,en}.pdf`）。
- `reports/grid2d_rect_bimodality/`: 2D 非正方形长方形域双峰研究：双 target 宽度-起点扫描 + 单 target 走廊反射墙构造（`grid2d_rect_bimodality_{cn,en}.pdf`）。
- `reports/cross_luca_regime_map/`: 跨报告 Luca defect 技术速度分区研究（固定 full-FPT 公平口径，`cross_luca_regime_map_{cn,en}.pdf`）。

建议用法（统一入口）：
- `python3 scripts/reportctl.py list`
- `python3 scripts/reportctl.py resolve --report ring_valley_dst`
- `python3 scripts/reportctl.py run --report ring_valley -- python3 code/valley_study.py`
- `python3 scripts/reportctl.py run --report ring_valley_dst -- python3 code/bimodality_flux_scan.py --help`
- `python3 scripts/reportctl.py build --report ring_valley --lang en`
- `python3 scripts/reportctl.py build --report ring_valley_dst --lang cn`
