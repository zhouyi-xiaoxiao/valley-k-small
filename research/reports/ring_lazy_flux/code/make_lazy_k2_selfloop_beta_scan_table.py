#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from pathlib import Path

REPORT_ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Convert a selfloop beta-scan CSV into small LaTeX tables (CN/EN).")
    p.add_argument(
        "--csv",
        type=str,
        default=str(
            REPORT_ROOT
            / "build"
            / "lazy_k2_selfloop_paper_geometry"
            / "beta_scan_N100_q0.666667_uoff5_voff1.csv"
        ),
    )
    p.add_argument(
        "--out-cn", type=str, default=str(REPORT_ROOT / "tables" / "lazy_K2_selfloop_beta_scan_N100_cn.tex")
    )
    p.add_argument(
        "--out-en", type=str, default=str(REPORT_ROOT / "tables" / "lazy_K2_selfloop_beta_scan_N100_en.tex")
    )
    return p.parse_args()


def write_table(outpath: Path, *, caption: str, label: str, rows: list[dict[str, str]]) -> None:
    lines: list[str] = []
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
    lines.append(f"\\caption{{{caption}}}\n")
    lines.append(f"\\label{{{label}}}\n")
    lines.append("\\end{table}\n")
    outpath.parent.mkdir(parents=True, exist_ok=True)
    outpath.write_text("".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    csv_path = Path(str(args.csv))
    if not csv_path.exists():
        raise FileNotFoundError(csv_path)

    with csv_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        raw = list(reader)

    # Keep all rows; format numbers for readability.
    rows: list[dict[str, str]] = []
    for r in raw:
        beta = float(r["beta"])
        p = float(r["p"])
        rows.append(
            {
                "beta": f"{beta:.4g}",
                "p": f"{p:.6g}",
                "paper": str(int(float(r["paper"]))),
                "macro": str(int(float(r["macro"]))),
                "t1": r.get("t1", "") or "--",
                "t2": r.get("t2", "") or "--",
            }
        )

    write_table(
        Path(str(args.out_cn)),
        caption="paper-like 几何（$N=100,u=6\\to v=51$）下，selfloop 模型的 $\\beta$ 扫描结果（$p=\\beta(1-q)$）。",
        label="tab:selfloop-beta-scan-cn",
        rows=rows,
    )
    write_table(
        Path(str(args.out_en)),
        caption="Selfloop $\\beta$ scan for the paper-like geometry at $N=100$ ($u=6\\to v=51$), with $p=\\beta(1-q)$. ",
        label="tab:selfloop-beta-scan-en",
        rows=rows,
    )

    print(f"wrote {args.out_cn}")
    print(f"wrote {args.out_en}")


if __name__ == "__main__":
    main()
