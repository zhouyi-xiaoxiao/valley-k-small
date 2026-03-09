#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
from pathlib import Path
import sys
from typing import Iterable, Optional

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages

from lazy_ring_aw_chebyshev import fpt_pmf_aw
from lazy_ring_flux_bimodality import bimodality_macro, bimodality_paper, local_peaks_strict


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=(
            "Compact multi-panel gallery for small-p selfloop bimodal curves (AW analytic).\n"
            "Geometry per N: start=n0, target=floor(N/2), u=n0+u_offset, v=target+v_offset.\n"
            "Shortcut probability p = beta*(1-q) taken from the self-loop at u.\n"
            "Output is a multi-page PDF with multiple N cases per page (multi-panel)."
        )
    )
    p.add_argument("--q", type=float, default=2.0 / 3.0)
    p.add_argument("--beta", type=float, default=0.02)
    p.add_argument("--start", type=int, default=1)
    p.add_argument("--u-offset", type=int, default=5)
    p.add_argument("--v-offset", type=int, default=1)
    p.add_argument("--N-list", type=str, default="70,80,90,100,110,120,130,140,150,160,170,180,190,200")
    p.add_argument("--thresh", type=float, default=1e-7)
    p.add_argument("--second-frac", type=float, default=0.01)
    p.add_argument("--time-ratio", type=float, default=10.0)
    p.add_argument("--tplot", type=int, default=5000, help="AW/plot horizon; should cover the 2nd peak")
    p.add_argument("--oversample", type=int, default=8)
    p.add_argument("--r-pow10", type=float, default=18.0)
    p.add_argument("--ncols", type=int, default=3)
    p.add_argument("--nrows", type=int, default=2)
    p.add_argument("--out", type=str, default="")
    return p.parse_args()


def parse_int_list(s: str) -> list[int]:
    out: list[int] = []
    for part in s.split(","):
        part = part.strip()
        if not part:
            continue
        out.append(int(part))
    return out


def top2_by_height(peaks: Iterable[tuple[int, float]]) -> Optional[list[tuple[int, float]]]:
    peaks_list = list(peaks)
    if len(peaks_list) < 2:
        return None
    top2 = sorted(peaks_list, key=lambda x: -x[1])[:2]
    return sorted(top2, key=lambda x: x[0])


def main() -> None:
    args = parse_args()
    q = float(args.q)
    beta = float(args.beta)
    p_sc = beta * (1.0 - q)
    if p_sc < 0.0 or p_sc > (1.0 - q) + 1e-15:
        raise ValueError("beta yields p outside [0, 1-q].")

    Ns = parse_int_list(str(args.N_list))
    Ns = [N for N in Ns if N >= 3]
    if len(Ns) == 0:
        raise ValueError("Empty --N-list (after filtering N>=3).")

    ncols = int(args.ncols)
    nrows = int(args.nrows)
    if ncols <= 0 or nrows <= 0:
        raise ValueError("--ncols and --nrows must be positive.")
    per_page = ncols * nrows

    outdir = REPO_ROOT / "figures" / "lazy_ring_flux_bimodality"
    outdir.mkdir(parents=True, exist_ok=True)
    if str(args.out).strip():
        outpath = Path(str(args.out))
    else:
        outpath = outdir / f"lazy_K2_selfloop_smallp_gallery_compact_beta{beta:.4g}.pdf"

    tplot = int(args.tplot)
    thresh = float(args.thresh)
    second_frac = float(args.second_frac)
    time_ratio = float(args.time_ratio)

    with PdfPages(outpath) as pdf:
        for page_idx in range(int(math.ceil(len(Ns) / float(per_page)))):
            page_cases = Ns[page_idx * per_page : (page_idx + 1) * per_page]

            fig_w = 3.9 * ncols
            fig_h = 2.75 * nrows
            fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(fig_w, fig_h))
            axes_flat = np.atleast_1d(axes).ravel()

            for ax in axes_flat[len(page_cases) :]:
                ax.axis("off")

            for idx, N in enumerate(page_cases):
                ax = axes_flat[idx]
                start = int(args.start) % N
                target = (N // 2) % N
                u = (start + int(args.u_offset)) % N
                v = (target + int(args.v_offset)) % N

                f_aw, aw_params = fpt_pmf_aw(
                    N=N,
                    q=q,
                    p=p_sc,
                    start=start,
                    target=target,
                    u=u,
                    v=v,
                    t_max=tplot,
                    oversample=int(args.oversample),
                    r_pow10=float(args.r_pow10),
                )
                f_aw = np.maximum(f_aw, 0.0)

                paper_ok, peaks = bimodality_paper(f_aw, thresh=thresh, second_frac=second_frac)
                macro_ok, _ = bimodality_macro(
                    f_aw, time_ratio=time_ratio, thresh=thresh, second_frac=second_frac
                )
                top2 = top2_by_height(peaks)
                t1 = top2[0][0] if top2 is not None else None
                t2 = top2[1][0] if top2 is not None else None

                x = np.arange(1, tplot + 1, dtype=int)
                y = f_aw[:tplot]
                ax.plot(x, y, color="C1", lw=1.1)
                ax.grid(True, alpha=0.18)

                if top2 is not None:
                    for t, h in top2:
                        ax.scatter([t], [h], s=18, color="C3", zorder=4)
                        ax.axvline(t, color="C3", ls="--", lw=0.9, alpha=0.65)

                ymax = float(np.max(y)) if y.size else 0.0
                if ymax > 0.0:
                    ax.set_ylim(0.0, 1.05 * ymax)
                ax.set_xlim(1, tplot)

                title = f"N={N} paper={int(paper_ok)} macro={int(macro_ok)}"
                if t1 is not None and t2 is not None:
                    title += f"  (t1,t2)=({t1},{t2})"
                ax.set_title(title, fontsize=9)
                ax.text(0.02, 0.96, f"u={u}→v={v}", transform=ax.transAxes, va="top", fontsize=8)
                ax.text(
                    0.02,
                    0.84,
                    f"m={aw_params.m}, r={aw_params.r:.5f}",
                    transform=ax.transAxes,
                    va="top",
                    fontsize=8,
                )

                row = idx // ncols
                col = idx % ncols
                if row == nrows - 1:
                    ax.set_xlabel("t", fontsize=8)
                else:
                    ax.set_xlabel("")
                if col == 0:
                    ax.set_ylabel("f(t)", fontsize=8)
                else:
                    ax.set_ylabel("")
                ax.tick_params(axis="both", labelsize=7)

            fig.suptitle(
                "selfloop small-p (compact, AW analytic): "
                f"q={q:.6g}, beta={beta:.4g} (p={p_sc:.4g}), "
                f"start={int(args.start)}, u_offset={int(args.u_offset)}, v_offset={int(args.v_offset)}, "
                f"h_min={thresh:.0e}, second_frac={second_frac:g}, t2/t1>={time_ratio:g}",
                fontsize=11,
            )
            fig.tight_layout(rect=(0, 0, 1, 0.92))
            pdf.savefig(fig)
            plt.close(fig)

    print(f"wrote {outpath}")


if __name__ == "__main__":
    main()
