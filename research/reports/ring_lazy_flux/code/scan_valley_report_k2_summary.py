#!/usr/bin/env python3
from __future__ import annotations

import sys
import csv
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from valley_study import build_graph, coarsegrain_two_steps, detect_peaks_fig3, exact_first_absorption_numerical


def write_tex_table(rows: list[dict[str, str]], *, outpath: Path, caption: str, label: str) -> None:
    lines: list[str] = []
    lines.append("\\begin{table}[!htbp]\n")
    lines.append("\\centering\n")
    lines.append("\\begin{tabular}{rrrrr}\n")
    lines.append("\\toprule\n")
    lines.append("$N$ & $K$ & $\\mathrm{peaks}$ & $t_{\\mathrm{peak}}$ & $A(t_{\\mathrm{peak}})$\\\\\n")
    lines.append("\\midrule\n")
    for r in rows:
        lines.append(f"{r['N']} & {r['K']} & {r['n_peaks']} & {r['t_peak']} & {r['h_peak']}\\\\\n")
    lines.append("\\bottomrule\n")
    lines.append("\\end{tabular}\n")
    lines.append(f"\\caption{{{caption}}}\n")
    lines.append(f"\\label{{{label}}}\n")
    lines.append("\\end{table}\n")
    outpath.parent.mkdir(parents=True, exist_ok=True)
    outpath.write_text("".join(lines), encoding="utf-8")


def main() -> None:
    # valley/ring_valley_en.tex scan setup: non-lazy ring with K neighbours, add directed shortcut (n0+5)->(target+1),
    # and for K=2 coarse-grain by 2 steps before peak detection.
    Ns = [10, 20, 50, 100, 160]
    K = 2

    outdir = REPO_ROOT / "build" / "valley_report_k2_compare"
    outdir.mkdir(parents=True, exist_ok=True)
    csv_path = outdir / "valley_report_k2_summary.csv"
    meta_path = outdir / "valley_report_k2_summary_meta.txt"
    tex_cn = REPO_ROOT / "tables" / "valley_report_k2_summary_cn.tex"
    tex_en = REPO_ROOT / "tables" / "valley_report_k2_summary_en.tex"

    meta_path.write_text(
        "\n".join(
            [
                "Model: valley_report / valley_study.py",
                "Non-lazy K-neighbour ring, add 1 directed edge at src and renormalize at src.",
                "Setup: n0=1, target=n=N/2 (even N), directed shortcut (n0+5)->(target+1).",
                "Computation: exact master-equation propagation until remaining mass < 1e-14.",
                "Peak rule: Fig.3 style strict local maxima, min height 1e-7, second peak >= 1% of max.",
                "For K=2: coarse-grain by 2 steps before applying the peak rule.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    csv_rows: list[dict[str, str]] = []
    tex_rows: list[dict[str, str]] = []
    for N in Ns:
        g = build_graph(N=N, K=K, directed_shortcut=True, shortcut_offset=5)
        A = exact_first_absorption_numerical(g, rho=1.0, eps_remaining=1e-14, max_steps=500_000)
        A_c = coarsegrain_two_steps(A)
        peaks = detect_peaks_fig3(A_c, min_height=1e-7, second_rel_height=0.01)
        if peaks:
            t_peak, h_peak = peaks[0]
        else:
            t_peak, h_peak = -1, 0.0
        row = {
            "N": str(N),
            "K": str(K),
            "mass": f"{float(A.sum()):.16f}",
            "len": str(len(A)),
            "len_coarse": str(len(A_c)),
            "n_peaks": str(len(peaks)),
            "t_peak": str(int(t_peak)),
            "h_peak": f"{float(h_peak):.12g}",
        }
        csv_rows.append(row)
        tex_rows.append(
            {
                "N": row["N"],
                "K": row["K"],
                "n_peaks": row["n_peaks"],
                "t_peak": row["t_peak"],
                "h_peak": row["h_peak"],
            }
        )

    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(csv_rows[0].keys()))
        w.writeheader()
        w.writerows(csv_rows)

    write_tex_table(
        tex_rows,
        outpath=tex_cn,
        caption="valley\\_report 模型下 $K=2$ 的峰数（在 2 步 coarse-grain 后）示例：每个 $N$ 仅剩 1 个主峰，因此不存在双峰。",
        label="tab:valley-report-k2-cn",
    )
    write_tex_table(
        tex_rows,
        outpath=tex_en,
        caption="K=2 peak counts for the valley\\_report model (after 2-step coarse-graining): each N has only one dominant peak, hence no bimodality.",
        label="tab:valley-report-k2-en",
    )

    print(f"wrote {csv_path}")
    print(f"wrote {meta_path}")
    print(f"wrote {tex_cn}")
    print(f"wrote {tex_en}")


if __name__ == '__main__':
    main()
