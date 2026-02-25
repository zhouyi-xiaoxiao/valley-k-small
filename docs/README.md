# Docs

本目录用于放置跨报告的说明文档与提交材料。

- `docs/RESEARCH_SUMMARY.md`: 研究汇总（供 ChatGPT Pro 直接使用）。
- `scripts/update_research_summary.py`: 自动刷新研究汇总（更新时间 + 报告索引）。
- `scripts/check_legacy_usage.py`: 统计历史命名残留引用频率（清理后持续监控）。
- `scripts/check_docs_paths.py`: 检查活跃文档中的失效路径与绝对路径引用。
- `scripts/prune_legacy_artifacts.py`: 将旧命名顶层 PDF 迁入归档并记录 manifest。
- `scripts/cleanup_local.py`: 清理本地杂项（.DS_Store、__pycache__、build/ 等）。
- `docs/research_log/`: 研究过程日志与阶段性基线快照（含 P1 函数级拆分基线记录）。
- `docs/agentreport.md`: 过程记录与阶段性日志。
- `docs/AGENT_REPORT_2025-12-14.md`: 早期阶段日志。
- `docs/submission/Submission.pdf`: 提交材料（主文档）。
- `docs/submission/Sup.pdf`: 提交材料（补充）。
- `reports/grid2d_reflecting_bimodality/`: 新增 2D 全反射边界双峰报告（中英文）。
- `reports/grid2d_blackboard_bimodality/`: 黑板图风格反射边界报告，当前聚焦走廊端点起止案例 Z/S（中英文）。
- `reports/ring_two_target/`: 双目标 lazy ring 多峰报告（中英文）。
- `reports/grid2d_two_target_double_peak/`: 2D 双目标配置下 double peak 条件报告（中英文）。
- `reports/grid2d_rect_bimodality/`: 2D 非正方形长方形域双峰研究：双 target 宽度-起点扫描 + 单 target 走廊反射墙构造（中英文）。
- `reports/cross_luca_regime_map/`: 跨报告 Luca defect 技术速度分区报告（固定 full-FPT 公平口径，中英文）。
