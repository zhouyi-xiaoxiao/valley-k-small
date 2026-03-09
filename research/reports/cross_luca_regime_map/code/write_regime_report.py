#!/usr/bin/env python3
"""Write bilingual TeX reports and README for Luca regime map study."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[3]
REPORT_DIR = ROOT / "reports" / "luca_regime_map"


def _fmt(v: float, nd: int = 4) -> str:
    return f"{float(v):.{nd}f}"


def _load_summary(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _section_pooled(summary: Dict[str, Any]) -> Dict[str, Any]:
    pooled = summary["pooled"]
    est = summary["estimation_validation"]
    return {
        "median_R": _fmt(pooled["median_R"], 4),
        "mean_R": _fmt(pooled["mean_R"], 4),
        "p_luca": _fmt(pooled["p_luca_faster"], 3),
        "has_luca": bool(pooled["has_luca_win_region"]),
        "no_win_statement": str(pooled["no_win_statement"]),
        "est_n": int(est["n_anchors"]),
        "est_med": _fmt(est["median_relative_error"], 3),
        "est_pass": bool(est["pass_threshold_25pct"]),
    }


def _recommendation_matrix_en() -> str:
    lines = [
        "\\begin{tabular}{lp{0.72\\linewidth}}",
        "\\toprule",
        "Task Type & Recommended Method \\\\",
        "\\midrule",
        "Full FPT under fixed finite horizon & Sparse exact recursion as default baseline; Luca only when defect support is very small and validated on anchors. \\\\",
        "MFPT/splitting only & Linear systems (do not use as full-FPT winner metric). \\\\",
        "Transform-domain analysis with sparse defects & Luca defect-reduced AW, but keep estimation/full calibration checks. \\\\",
        "High-defect corridor-like regimes & Prefer sparse recursion; Luca often loses after setup/evaluation overhead is counted. \\\\",
        "\\bottomrule",
        "\\end{tabular}",
    ]
    return "\n".join(lines)


def _recommendation_matrix_cn() -> str:
    lines = [
        "\\begin{tabular}{lp{0.72\\linewidth}}",
        "\\toprule",
        "任务类型 & 推荐方法 \\\\",
        "\\midrule",
        "固定有限时窗下的完整 FPT 曲线 & 默认采用 sparse exact recursion；仅在缺陷极稀疏且锚点校验通过时考虑 Luca。 \\\\",
        "只关心 MFPT/splitting & 线性方程法（不参与 full-FPT 胜负判定）。 \\\\",
        "需要变换域并且缺陷稀疏 & 可用 Luca defect-reduced AW，但需保留 estimate/full 校验。 \\\\",
        "高缺陷走廊类配置 & 优先 sparse recursion；计入 setup/eval 后 Luca 常不占优。 \\\\",
        "\\bottomrule",
        "\\end{tabular}",
    ]
    return "\n".join(lines)


def _build_tex_en(summary: Dict[str, Any]) -> str:
    S = _section_pooled(summary)
    est_label = "PASS" if S["est_pass"] else "FAIL"
    lines: List[str] = []
    lines.extend(
        [
            "\\documentclass[11pt]{article}",
            "\\usepackage[margin=1in]{geometry}",
            "\\usepackage{amsmath,amssymb,booktabs,graphicx,hyperref,float}",
            "\\title{Luca Defect Regime Map (Cross-Report, Fixed Full-FPT Fairness)}",
            "\\author{Automated benchmark in valley-k-small}",
            "\\date{\\today}",
            "\\begin{document}",
            "\\maketitle",
            "\\section{Scope and Fairness}",
            "Main winner metric compares only full-FPT competitors: sparse exact recursion vs Luca defect-reduced route.",
            "Linear systems are recorded as MFPT reference only.",
            "All claims use fixed-horizon fairness and ratio metric $R=\\text{sparse}/\\text{luca}$.",
            "Cross-family claims do not mix absolute seconds.",
            "\\section{Methods}",
            "Timing protocol: warm-up 1 run, then 3 measured runs with median.",
            "Luca mode rule: full when defect pairs $\\le 120$, otherwise sampled-$z$ extrapolated estimate.",
            "Estimator form: $t_{\\mathrm{est}}=t_{\\mathrm{setup}}+(t_{\\mathrm{eval}}/n_z)\\,m+t_{\\mathrm{fft}}$.",
            "\\section{Main Findings}",
            f"Pooled median $R$: {S['median_R']} (mean {S['mean_R']}); Luca-win probability $P(R>1)$: {S['p_luca']}.",
            f"Global regime decision: {S['no_win_statement']}",
            f"Estimation anchors: n={S['est_n']}, median relative error={S['est_med']} ({est_label} against 25\\% threshold).",
            "\\section{Figures}",
            "\\begin{figure}[H]\\centering",
            "\\includegraphics[width=0.9\\linewidth]{figures/regime_winner_heatmap_two_target.pdf}",
            "\\caption{Winner heatmap on two-target workloads.}",
            "\\end{figure}",
            "\\begin{figure}[H]\\centering",
            "\\includegraphics[width=0.9\\linewidth]{figures/regime_winner_heatmap_reflecting.pdf}",
            "\\caption{Winner heatmap on reflecting workloads.}",
            "\\end{figure}",
            "\\begin{figure}[H]\\centering",
            "\\includegraphics[width=0.9\\linewidth]{figures/regime_speedup_scatter_all.pdf}",
            "\\caption{Speedup ratio scatter with full/estimate mode markers.}",
            "\\end{figure}",
            "\\begin{figure}[H]\\centering",
            "\\includegraphics[width=0.8\\linewidth]{figures/regime_speedup_box_by_T.pdf}",
            "\\caption{Distribution of $R$ by fixed horizon $T$.}",
            "\\end{figure}",
            "\\begin{figure}[H]\\centering",
            "\\includegraphics[width=0.8\\linewidth]{figures/regime_estimation_error_anchor.pdf}",
            "\\caption{Full vs estimate relative error on anchor workloads.}",
            "\\end{figure}",
            "\\begin{figure}[H]\\centering",
            "\\includegraphics[width=0.98\\linewidth]{figures/regime_config_examples.pdf}",
            "\\caption{Representative low/medium/high-defect configuration examples.}",
            "\\end{figure}",
            "\\section{Tables}",
            "\\input{tables/regime_summary_by_bin.tex}",
            "\\bigskip",
            "\\input{tables/regime_anchor_baselines.tex}",
            "\\section{Practical Recommendation Matrix}",
            _recommendation_matrix_en(),
            "\\section{Reproducibility}",
            "Core data files: \\texttt{data/manifest.csv}, \\texttt{data/runtime\\_raw.csv}, \\texttt{data/runtime\\_summary.json}.",
            "\\end{document}",
        ]
    )
    return "\n".join(lines) + "\n"


def _build_tex_cn(summary: Dict[str, Any]) -> str:
    S = _section_pooled(summary)
    est_label = "通过" if S["est_pass"] else "未通过"
    lines: List[str] = []
    lines.extend(
        [
            "\\documentclass[11pt]{ctexart}",
            "\\usepackage[margin=1in]{geometry}",
            "\\usepackage{amsmath,amssymb,booktabs,graphicx,hyperref,float}",
            "\\title{Luca 缺陷技术速度分区图（跨报告、固定 full-FPT 公平口径）}",
            "\\author{valley-k-small 自动化基准}",
            "\\date{\\today}",
            "\\begin{document}",
            "\\maketitle",
            "\\section{研究范围与公平口径}",
            "主胜负指标仅比较完整 FPT 竞争者：sparse exact recursion 与 Luca defect-reduced 路线。",
            "线性方程法仅作为 MFPT 参考，不参与完整 FPT 胜负判定。",
            "统一使用固定时窗口径与比例指标 $R=\\text{sparse}/\\text{luca}$，跨 family 结论不混合绝对秒数。",
            "\\section{方法与计时协议}",
            "计时采用 warm-up 1 次 + 实测 3 次取中位数。",
            "Luca 模式规则：defect pairs $\\le 120$ 用 full；否则用 sampled-$z$ 外推估计。",
            "估计式：$t_{\\mathrm{est}}=t_{\\mathrm{setup}}+(t_{\\mathrm{eval}}/n_z)\\,m+t_{\\mathrm{fft}}$。",
            "\\section{主结果}",
            f"汇总中位数 $R={S['median_R']}$（均值 {S['mean_R']}），Luca 胜率 $P(R>1)={S['p_luca']}$。",
            f"全局判定：{S['no_win_statement']}",
            f"估计校验：n={S['est_n']}，中位相对误差={S['est_med']}（25\\% 阈值判定：{est_label}）。",
            "\\section{图件}",
            "\\begin{figure}[H]\\centering",
            "\\includegraphics[width=0.9\\linewidth]{figures/regime_winner_heatmap_two_target.pdf}",
            "\\caption{two-target 样本上的 winner heatmap。}",
            "\\end{figure}",
            "\\begin{figure}[H]\\centering",
            "\\includegraphics[width=0.9\\linewidth]{figures/regime_winner_heatmap_reflecting.pdf}",
            "\\caption{reflecting 样本上的 winner heatmap。}",
            "\\end{figure}",
            "\\begin{figure}[H]\\centering",
            "\\includegraphics[width=0.9\\linewidth]{figures/regime_speedup_scatter_all.pdf}",
            "\\caption{全样本速度比散点图（区分 full/estimate 模式）。}",
            "\\end{figure}",
            "\\begin{figure}[H]\\centering",
            "\\includegraphics[width=0.8\\linewidth]{figures/regime_speedup_box_by_T.pdf}",
            "\\caption{按固定时窗 $T$ 的 $R$ 分布。}",
            "\\end{figure}",
            "\\begin{figure}[H]\\centering",
            "\\includegraphics[width=0.8\\linewidth]{figures/regime_estimation_error_anchor.pdf}",
            "\\caption{锚点 workload 上 full 与 estimate 的相对误差。}",
            "\\end{figure}",
            "\\begin{figure}[H]\\centering",
            "\\includegraphics[width=0.98\\linewidth]{figures/regime_config_examples.pdf}",
            "\\caption{低/中/高缺陷代表性配置图（复用现有风格工具）。}",
            "\\end{figure}",
            "\\section{表格}",
            "\\input{tables/regime_summary_by_bin.tex}",
            "\\bigskip",
            "\\input{tables/regime_anchor_baselines.tex}",
            "\\section{实务建议矩阵}",
            _recommendation_matrix_cn(),
            "\\section{复现信息}",
            "核心数据文件：\\texttt{data/manifest.csv}、\\texttt{data/runtime\\_raw.csv}、\\texttt{data/runtime\\_summary.json}。",
            "\\end{document}",
        ]
    )
    return "\n".join(lines) + "\n"


def _build_readme(summary: Dict[str, Any]) -> str:
    S = _section_pooled(summary)
    lines: List[str] = []
    lines.append("# Luca Regime Map")
    lines.append("")
    lines.append("Standalone cross-report benchmark for fixed-horizon full-FPT fairness.")
    lines.append("")
    lines.append("## Key policy")
    lines.append("- Main full-FPT winner metric: `Sparse exact` vs `Luca defect-reduced`.")
    lines.append("- `Linear MFPT` is reference only.")
    lines.append("- `Full AW` and `Dense recursion` are appendix sanity anchors only.")
    lines.append("- Cross-family claims use ratio metric `R=sparse/luca`; do not mix absolute seconds.")
    lines.append("")
    lines.append("## Current snapshot")
    lines.append(f"- Median `R`: `{S['median_R']}`")
    lines.append(f"- Luca-win probability `P(R>1)`: `{S['p_luca']}`")
    lines.append(f"- Regime statement: {S['no_win_statement']}")
    lines.append("")
    lines.append("## Outputs")
    lines.append("- Data: `data/manifest.csv`, `data/runtime_raw.csv`, `data/runtime_summary.json`")
    lines.append("- Figures:")
    lines.append("  - `figures/regime_winner_heatmap_two_target.pdf`")
    lines.append("  - `figures/regime_winner_heatmap_reflecting.pdf`")
    lines.append("  - `figures/regime_speedup_scatter_all.pdf`")
    lines.append("  - `figures/regime_speedup_box_by_T.pdf`")
    lines.append("  - `figures/regime_estimation_error_anchor.pdf`")
    lines.append("  - `figures/regime_config_examples.pdf`")
    lines.append("- Tables: `tables/regime_summary_by_bin.tex`, `tables/regime_anchor_baselines.tex`")
    lines.append("- Reports: `cross_luca_regime_map_en.tex`, `cross_luca_regime_map_cn.tex` (+ compiled PDFs)")
    lines.append("")
    lines.append("## Reproduce")
    lines.append("```bash")
    lines.append(".venv/bin/python reports/cross_luca_regime_map/code/build_manifest.py")
    lines.append(".venv/bin/python reports/cross_luca_regime_map/code/run_regime_scan.py")
    lines.append(".venv/bin/python reports/cross_luca_regime_map/code/plot_regime_figures.py")
    lines.append(".venv/bin/python reports/cross_luca_regime_map/code/write_regime_report.py")
    lines.append("")
    lines.append("cd reports/cross_luca_regime_map")
    lines.append("latexmk -pdf -interaction=nonstopmode -halt-on-error -auxdir=build -emulate-aux-dir cross_luca_regime_map_en.tex")
    lines.append("latexmk -xelatex -interaction=nonstopmode -halt-on-error -auxdir=build -emulate-aux-dir cross_luca_regime_map_cn.tex")
    lines.append("```")
    return "\n".join(lines) + "\n"


def main() -> None:
    p = argparse.ArgumentParser(description="Write bilingual regime-map report sources.")
    p.add_argument(
        "--summary",
        type=str,
        default=str(REPORT_DIR / "data" / "runtime_summary.json"),
    )
    p.add_argument(
        "--out-en",
        type=str,
        default=str(REPORT_DIR / "cross_luca_regime_map_en.tex"),
    )
    p.add_argument(
        "--out-cn",
        type=str,
        default=str(REPORT_DIR / "cross_luca_regime_map_cn.tex"),
    )
    p.add_argument(
        "--out-readme",
        type=str,
        default=str(REPORT_DIR / "README.md"),
    )
    args = p.parse_args()

    summary = _load_summary(Path(args.summary))

    out_en = Path(args.out_en)
    out_cn = Path(args.out_cn)
    out_readme = Path(args.out_readme)
    out_en.write_text(_build_tex_en(summary), encoding="utf-8")
    out_cn.write_text(_build_tex_cn(summary), encoding="utf-8")
    out_readme.write_text(_build_readme(summary), encoding="utf-8")

    print(
        json.dumps(
            {
                "tex_en": str(out_en),
                "tex_cn": str(out_cn),
                "readme": str(out_readme),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
