from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def _resolve(path_str: str, *, report_root: Path) -> Path:
    p = Path(path_str).expanduser()
    if not p.is_absolute():
        p = (report_root / p).resolve()
    return p


def main_make_beta_scan_table(*, report_root: Path, argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Convert a beta-scan CSV into a LaTeX table (paper/macro + peak times).")
    parser.add_argument("--csv", type=str, required=True, help="Input CSV from jumpover_bimodality_pipeline.py scan-beta")
    parser.add_argument("--out", type=str, required=True, help="Output .tex path (table environment)")
    parser.add_argument("--caption", type=str, required=True)
    parser.add_argument("--label", type=str, required=True)
    args = parser.parse_args(list(argv) if argv is not None else None)

    csv_path = _resolve(args.csv, report_root=report_root)
    if not csv_path.exists():
        raise FileNotFoundError(csv_path)

    with csv_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        raw = list(reader)

    rows: List[Dict[str, str]] = []
    for r in raw:
        beta = float(r["beta"])
        p = float(r["p_shortcut"])
        paper = 1 if str(r["paper_bimodal"]) == "True" else 0
        macro = 1 if str(r["macro_bimodal"]) == "True" else 0
        t1 = r.get("t1", "") or "--"
        t2 = r.get("t2", "") or "--"
        if paper == 0:
            t1, t2 = "--", "--"
        rows.append(
            {
                "beta": f"{beta:.4g}",
                "p": f"{p:.6g}",
                "paper": str(paper),
                "macro": str(macro),
                "t1": t1,
                "t2": t2,
            }
        )

    outpath = _resolve(args.out, report_root=report_root)
    lines: List[str] = []
    lines.append("\\begin{table}[!htbp]\n")
    lines.append("\\centering\n")
    lines.append("\\small\n")
    lines.append("\\begin{tabular}{rrrrrr}\n")
    lines.append("\\toprule\n")
    lines.append("$\\beta$ & $p$ & paper & macro & $t_1$ & $t_2$\\\\\n")
    lines.append("\\midrule\n")
    for r in rows:
        lines.append(f"{r['beta']} & {r['p']} & {r['paper']} & {r['macro']} & {r['t1']} & {r['t2']}\\\\\n")
    lines.append("\\bottomrule\n")
    lines.append("\\end{tabular}\n")
    lines.append(f"\\caption{{{args.caption}}}\n")
    lines.append(f"\\label{{{args.label}}}\n")
    lines.append("\\end{table}\n")
    outpath.parent.mkdir(parents=True, exist_ok=True)
    outpath.write_text("".join(lines), encoding="utf-8")
    print(f"wrote {outpath}")
    return 0


def main_make_case_window_table(*, report_root: Path, argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Generate a LaTeX table (window-conditional stats) from a case summary JSON "
            "produced by jumpover_bimodality_pipeline.py analyze."
        )
    )
    parser.add_argument("--summary", type=str, required=True, help="Input .summary.json path")
    parser.add_argument("--out", type=str, required=True, help="Output .tex path (table environment)")
    parser.add_argument("--caption", type=str, required=True)
    parser.add_argument("--label", type=str, required=True)
    parser.add_argument("--digits", type=int, default=3, help="Decimal digits for probabilities (default: 3).")
    args = parser.parse_args(list(argv) if argv is not None else None)

    summary_path = _resolve(args.summary, report_root=report_root)
    outpath = _resolve(args.out, report_root=report_root)
    digits = int(args.digits)

    data: Dict[str, Any] = json.loads(summary_path.read_text(encoding="utf-8"))
    peaks_valley = data["peaks_valley"]
    delta = int(peaks_valley["delta"])

    centers = {
        "peak1": int(peaks_valley.get("t1", -1)),
        "valley": int(peaks_valley.get("tv", -1)),
        "peak2": int(peaks_valley.get("t2", -1)),
    }

    summaries: List[Dict[str, Any]] = list(data["summaries"])
    by_window = {str(s["window"]): s for s in summaries}

    def fmt(x: float, *, digits: int) -> str:
        return f"{float(x):.{int(digits)}f}"

    rows: List[Dict[str, Any]] = []
    for w in ("peak1", "valley", "peak2"):
        if w not in by_window:
            continue
        s = by_window[w]
        rows.append(
            {
                "window": w,
                "t_c": int(centers[w]),
                "n": int(s["n"]),
                "frac": float(s["frac"]),
                "P_sc": float(s.get("P_sc_ge1", 0.0)),
                "P_jo": float(s.get("P_jo_ge1", 0.0)),
                "A": float(s.get("class_C0J0", 0.0)),
                "B": float(s.get("class_C1pJ0", 0.0)),
                "C": float(s.get("class_C0J1p", 0.0)),
                "D": float(s.get("class_C1pJ1p", 0.0)),
            }
        )

    lines: List[str] = []
    lines.append("\\begin{table}[!htbp]\n")
    lines.append("\\centering\n")
    lines.append("\\scriptsize\n")
    lines.append("\\setlength{\\tabcolsep}{4pt}\n")
    lines.append("\\begin{tabular}{lrrrrrrrrr}\n")
    lines.append("\\toprule\n")
    lines.append(
        "window & $t_c$ & $n$ & $\\Pr(T\\in W)$ & $\\Pr(C\\ge 1\\mid W)$ & $\\Pr(J\\ge 1\\mid W)$ & A & B & C & D\\\\\n"
    )
    lines.append("\\midrule\n")
    for r in rows:
        lines.append(
            f"{r['window']} & {r['t_c']} & {r['n']} & {fmt(r['frac'], digits=digits)} & "
            f"{fmt(r['P_sc'], digits=digits)} & {fmt(r['P_jo'], digits=digits)} & "
            f"{fmt(r['A'], digits=digits)} & {fmt(r['B'], digits=digits)} & "
            f"{fmt(r['C'], digits=digits)} & {fmt(r['D'], digits=digits)}\\\\\n"
        )
    lines.append("\\bottomrule\n")
    lines.append("\\end{tabular}\n")
    lines.append(
        f"\\caption{{{str(args.caption)} ($\\Delta={delta}$). A/B/C/D: A=$(C=0,J=0)$, B=$(C\\ge 1,J=0)$, C=$(C=0,J\\ge 1)$, D=$(C\\ge 1,J\\ge 1)$.}}\n"
    )
    lines.append(f"\\label{{{str(args.label)}}}\n")
    lines.append("\\end{table}\n")

    outpath.parent.mkdir(parents=True, exist_ok=True)
    outpath.write_text("".join(lines), encoding="utf-8")
    print(f"wrote {outpath}")
    return 0


@dataclass(frozen=True)
class ScanRow:
    x: float
    paper: bool
    macro: bool
    t1: Optional[int]
    t2: Optional[int]


def _read_scan_csv(path: Path, *, x_col: str) -> List[ScanRow]:
    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows: List[ScanRow] = []
        for r in reader:
            x = float(r[x_col])
            paper = str(r["paper_bimodal"]) == "True"
            macro = str(r["macro_bimodal"]) == "True"
            t1 = None if (r.get("t1") in (None, "", "None")) else int(float(r["t1"]))
            t2 = None if (r.get("t2") in (None, "", "None")) else int(float(r["t2"]))
            rows.append(ScanRow(x=x, paper=paper, macro=macro, t1=t1, t2=t2))
    return rows


def _plot_bimodality_map(*, rows_k2: Sequence[ScanRow], rows_k4: Sequence[ScanRow], xlabel: str, title: str, outpath: Path) -> None:
    fig, ax = plt.subplots(figsize=(8.2, 2.8), dpi=180)

    def draw(rows: Sequence[ScanRow], y: float) -> None:
        if not rows:
            return
        xs = np.array([r.x for r in rows], dtype=float)
        paper = np.array([r.paper for r in rows], dtype=bool)
        macro = np.array([r.macro for r in rows], dtype=bool)
        y_paper = y - 0.12
        y_macro = y + 0.12
        if np.any(paper):
            ax.scatter(
                xs[paper],
                np.full(np.sum(paper), y_paper),
                s=24,
                facecolors="none",
                edgecolors="tab:blue",
                linewidths=1.0,
                zorder=2,
            )
        if np.any(macro):
            ax.scatter(xs[macro], np.full(np.sum(macro), y_macro), s=24, color="tab:blue", zorder=3)

    draw(rows_k2, y=2.0)
    draw(rows_k4, y=4.0)

    ax.set_ylim(1.5, 4.5)
    ax.set_yticks([2, 4], ["K=2", "K=4"])
    ax.set_xlabel(xlabel)
    ax.set_title(title)
    ax.grid(True, axis="x", alpha=0.25)

    handle_paper = ax.scatter([], [], s=24, facecolors="none", edgecolors="tab:blue", linewidths=1.0)
    handle_macro = ax.scatter([], [], s=24, color="tab:blue")
    fig.legend(
        handles=[handle_paper, handle_macro],
        labels=["paper bimodal", "macro bimodal"],
        frameon=False,
        loc="upper center",
        bbox_to_anchor=(0.5, 0.98),
        ncol=2,
        fontsize=8,
    )

    fig.tight_layout(rect=[0.0, 0.0, 1.0, 0.9])
    outpath.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(outpath)
    plt.close(fig)


def _plot_peak_times(*, rows_k2: Sequence[ScanRow], rows_k4: Sequence[ScanRow], xlabel: str, title: str, outpath: Path) -> None:
    fig, axes = plt.subplots(2, 1, figsize=(8.2, 5.2), dpi=180, sharex=True)
    ax1, ax2 = axes

    def draw(rows: Sequence[ScanRow], label: str, color: str) -> None:
        xs = np.array([r.x for r in rows if r.paper and r.t1 is not None and r.t2 is not None], dtype=float)
        t1 = np.array([r.t1 for r in rows if r.paper and r.t1 is not None and r.t2 is not None], dtype=float)
        t2 = np.array([r.t2 for r in rows if r.paper and r.t1 is not None and r.t2 is not None], dtype=float)
        if xs.size == 0:
            return
        order = np.argsort(xs)
        xs = xs[order]
        t1 = t1[order]
        t2 = t2[order]
        ax1.plot(xs, t1, marker="o", ms=3, lw=1.2, color=color, alpha=0.9, label=label)
        ax2.plot(xs, t2, marker="s", ms=3, lw=1.2, color=color, alpha=0.9, label=label)

    draw(rows_k2, label="K=2", color="tab:orange")
    draw(rows_k4, label="K=4", color="tab:green")

    ax1.set_ylabel("t1")
    ax2.set_ylabel("t2")
    ax2.set_xlabel(xlabel)
    for ax in axes:
        ax.set_yscale("log")
        ax.grid(True, alpha=0.25)
    ax1.set_title(title)
    handles, labels = ax1.get_legend_handles_labels()
    if handles:
        fig.legend(
            handles=handles,
            labels=labels,
            frameon=False,
            loc="upper center",
            bbox_to_anchor=(0.5, 0.98),
            ncol=2,
            fontsize=8,
        )
    fig.tight_layout(rect=[0.0, 0.0, 1.0, 0.9])
    outpath.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(outpath)
    plt.close(fig)


def main_plot_scan_summaries(*, report_root: Path, argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Plot scan CSV summaries for the jumpover bimodality report")

    sub = parser.add_subparsers(dest="cmd", required=True)

    pn = sub.add_parser("scan-n", help="plot N-scan bimodality markers + peak times")
    pn.add_argument("--k2", type=str, default=str(report_root / "data" / "scan_N_K2_beta002.csv"))
    pn.add_argument("--k4", type=str, default=str(report_root / "data" / "scan_N_K4_beta002.csv"))
    pn.add_argument("--out-map", type=str, default=str(report_root / "figures" / "scan_N_beta002_bimodality.pdf"))
    pn.add_argument("--out-times", type=str, default=str(report_root / "figures" / "scan_N_beta002_peak_times.pdf"))

    pb = sub.add_parser("scan-beta", help="plot beta-scan bimodality markers + peak times")
    pb.add_argument("--k2", type=str, default=str(report_root / "data" / "scan_beta_N100_K2.csv"))
    pb.add_argument("--k4", type=str, default=str(report_root / "data" / "scan_beta_N100_K4.csv"))
    pb.add_argument("--out-map", type=str, default=str(report_root / "figures" / "scan_beta_N100_bimodality.pdf"))
    pb.add_argument("--out-times", type=str, default=str(report_root / "figures" / "scan_beta_N100_peak_times.pdf"))

    args = parser.parse_args(list(argv) if argv is not None else None)

    if args.cmd == "scan-n":
        r2 = _read_scan_csv(Path(args.k2), x_col="N")
        r4 = _read_scan_csv(Path(args.k4), x_col="N")
        _plot_bimodality_map(
            rows_k2=r2,
            rows_k4=r4,
            xlabel="N",
            title="Bimodality flags (beta=0.02, q=2/3, target=auto antipodal)",
            outpath=Path(args.out_map),
        )
        _plot_peak_times(
            rows_k2=r2,
            rows_k4=r4,
            xlabel="N",
            title="Peak times (paper-bimodal cases only)",
            outpath=Path(args.out_times),
        )
        print(f"wrote {args.out_map}")
        print(f"wrote {args.out_times}")
        return 0

    if args.cmd == "scan-beta":
        r2 = _read_scan_csv(Path(args.k2), x_col="beta")
        r4 = _read_scan_csv(Path(args.k4), x_col="beta")
        _plot_bimodality_map(
            rows_k2=r2,
            rows_k4=r4,
            xlabel="beta",
            title="Bimodality flags (N=100, q=2/3, target=auto antipodal)",
            outpath=Path(args.out_map),
        )
        _plot_peak_times(
            rows_k2=r2,
            rows_k4=r4,
            xlabel="beta",
            title="Peak times (paper-bimodal cases only)",
            outpath=Path(args.out_times),
        )
        print(f"wrote {args.out_map}")
        print(f"wrote {args.out_times}")
        return 0

    raise SystemExit("unknown command")
