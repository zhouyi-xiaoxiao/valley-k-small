#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from pathlib import Path
import sys
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from lazy_ring_flux_bimodality import bimodality_macro, bimodality_paper, fpt_pmf_flux_ring


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=(
            "Scan the 'paper-like geometry' for k=1 (K=2) lazy ring under the equal-4 rule at the shortcut source.\n"
            "Geometry per N:\n"
            "  start=n0=1, target=floor(N/2), u=start+5, v=target+1.\n"
            "Model:\n"
            "  baseline is lazy ring with parameter q; at u we override to equal probs 1/4 on {stay,left,right,shortcut}."
        )
    )
    p.add_argument("--N-min", type=int, default=10)
    p.add_argument("--N-max", type=int, default=200)
    p.add_argument("--q", type=float, default=2.0 / 3.0, help="equal-prob baseline for non-shortcut nodes is q=2/3")
    p.add_argument("--start", type=int, default=1)
    p.add_argument("--u-offset", type=int, default=5)
    p.add_argument("--v-offset", type=int, default=1)
    p.add_argument("--Tmax", type=int, default=200_000)
    p.add_argument("--eps-surv", type=float, default=1e-14)
    p.add_argument("--thresh", type=float, default=1e-7, help="peak threshold h_min for paper/macro criteria")
    p.add_argument("--second-frac", type=float, default=0.01)
    p.add_argument("--time-ratio", type=float, default=10.0)
    p.add_argument("--summary-only", action="store_true", help="only compute the representative N list")
    return p.parse_args()


def top_two_peaks_str(peaks: tuple[tuple[int, float], ...]) -> str:
    if len(peaks) == 0:
        return ""
    top2 = sorted(peaks, key=lambda x: -x[1])[:2]
    top2 = sorted(top2, key=lambda x: x[0])
    return ";".join([f"({t},{h:.3e})" for t, h in top2])


def write_summary_table_tex(
    *,
    outpath: Path,
    caption: str,
    label: str,
    rows: list[dict[str, str]],
) -> None:
    lines: list[str] = []
    lines.append("\\begin{table}[!htbp]\n")
    lines.append("\\centering\n")
    lines.append("\\small\n")
    lines.append("\\begin{tabular}{rrrrrr}\n")
    lines.append("\\toprule\n")
    lines.append("$N$ & $u$ & $v$ & paper & macro & $t_\\mathrm{peak}$\\\\\n")
    lines.append("\\midrule\n")
    for r in rows:
        lines.append(
            f"{r['N']} & {r['u']} & {r['v']} & {r['paper']} & {r['macro']} & {r['tpeak']}\\\\\n"
        )
    lines.append("\\bottomrule\n")
    lines.append("\\end{tabular}\n")
    lines.append(f"\\caption{{{caption}}}\n")
    lines.append(f"\\label{{{label}}}\n")
    lines.append("\\end{table}\n")
    outpath.parent.mkdir(parents=True, exist_ok=True)
    outpath.write_text("".join(lines), encoding="utf-8")


def compute_one(
    *,
    N: int,
    q: float,
    start: int,
    u_offset: int,
    v_offset: int,
    Tmax: int,
    eps_surv: float,
    thresh: float,
    second_frac: float,
    time_ratio: float,
) -> dict[str, object]:
    start = int(start) % N
    target = int(N // 2) % N
    u = int(start + u_offset) % N
    v = int(target + v_offset) % N

    f, surv = fpt_pmf_flux_ring(
        N,
        q,
        start,
        target,
        model="equal4",
        u=u,
        v=v,
        Tmax=Tmax,
        eps_surv=eps_surv,
    )
    paper_ok, peaks = bimodality_paper(f, thresh=thresh, second_frac=second_frac)
    macro_ok, _ = bimodality_macro(f, time_ratio=time_ratio, thresh=thresh, second_frac=second_frac)

    tpeak = int(f.argmax() + 1) if f.size > 0 else 0

    return {
        "N": N,
        "start": start,
        "target": target,
        "u": u,
        "v": v,
        "paper": bool(paper_ok),
        "macro": bool(macro_ok),
        "npeaks": int(len(peaks)),
        "tpeak": tpeak,
        "top2": top_two_peaks_str(peaks),
        "mass": float(f.sum()),
        "surv": float(surv),
        "steps": int(len(f)),
    }


def main() -> None:
    args = parse_args()

    N_min = int(args.N_min)
    N_max = int(args.N_max)
    if N_min < 3 or N_max < N_min:
        raise ValueError("Need 3 <= N_min <= N_max.")

    q = float(args.q)
    start = int(args.start)
    u_offset = int(args.u_offset)
    v_offset = int(args.v_offset)

    outdir = REPO_ROOT / "build" / "lazy_k2_equal4_paper_geometry"
    outdir.mkdir(parents=True, exist_ok=True)
    csv_path = outdir / "scan_equal4_paper_geometry.csv"
    meta_path = outdir / "scan_equal4_paper_geometry_meta.txt"

    representative_Ns = [20, 50, 100, 160, 200]
    rep_rows: list[dict[str, str]] = []

    if args.summary_only:
        Ns = representative_Ns
    else:
        Ns = list(range(N_min, N_max + 1))

    rows: list[dict[str, object]] = []
    for N in Ns:
        row = compute_one(
            N=N,
            q=q,
            start=start,
            u_offset=u_offset,
            v_offset=v_offset,
            Tmax=int(args.Tmax),
            eps_surv=float(args.eps_surv),
            thresh=float(args.thresh),
            second_frac=float(args.second_frac),
            time_ratio=float(args.time_ratio),
        )
        rows.append(row)

        if N in representative_Ns:
            rep_rows.append(
                {
                    "N": str(row["N"]),
                    "u": str(row["u"]),
                    "v": str(row["v"]),
                    "paper": "1" if row["paper"] else "0",
                    "macro": "1" if row["macro"] else "0",
                    "tpeak": str(row["tpeak"]),
                }
            )

    # Write meta
    meta_path.write_text(
        "\n".join(
            [
                "k=1 (K=2) lazy ring, equal-4 at shortcut source",
                "Geometry: start=n0, target=floor(N/2), u=start+u_offset, v=target+v_offset",
                f"N_range = [{N_min}, {N_max}]",
                f"q = {q}",
                f"start = {start}",
                f"u_offset = {u_offset}",
                f"v_offset = {v_offset}",
                f"Tmax = {int(args.Tmax)}",
                f"eps_surv = {float(args.eps_surv)}",
                f"peak criterion: thresh={float(args.thresh)}, second_frac={float(args.second_frac)}, time_ratio={float(args.time_ratio)}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    # Write CSV
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "N",
                "start",
                "target",
                "u",
                "v",
                "paper",
                "macro",
                "npeaks",
                "tpeak",
                "top2",
                "mass",
                "surv",
                "steps",
            ],
        )
        w.writeheader()
        for r in rows:
            w.writerow(r)

    # Write short TeX tables (CN/EN use the same numeric content)
    tex_cn = REPO_ROOT / "tables" / "lazy_K2_equal4_paper_geometry_summary_cn.tex"
    tex_en = REPO_ROOT / "tables" / "lazy_K2_equal4_paper_geometry_summary_en.tex"
    write_summary_table_tex(
        outpath=tex_cn,
        caption=(
            "equal4 概率规则下（在 $u$ 处四个动作各 $1/4$），采用 paper-like 几何 "
            "$n_0=1$, $\\mathrm{target}=\\lfloor N/2\\rfloor$, $u=n_0+5$, $v=\\mathrm{target}+1$ 的代表性结果。"
        ),
        label="tab:equal4-paper-geom-cn",
        rows=rep_rows,
    )
    write_summary_table_tex(
        outpath=tex_en,
        caption=(
            "Representative results under the equal-4 rule at the shortcut source "
            "(at $u$: stay/left/right/shortcut each $1/4$), using the paper-like geometry "
            "$n_0=1$, $\\mathrm{target}=\\lfloor N/2\\rfloor$, $u=n_0+5$, $v=\\mathrm{target}+1$."
        ),
        label="tab:equal4-paper-geom-en",
        rows=rep_rows,
    )

    n_paper = sum(1 for r in rows if bool(r["paper"]))
    n_macro = sum(1 for r in rows if bool(r["macro"]))
    print(f"wrote {csv_path}")
    print(f"wrote {tex_cn} and {tex_en}")
    print(f"paper_bimodal_count={n_paper} macro_bimodal_count={n_macro} over {len(rows)} cases")


if __name__ == "__main__":
    main()
