#!/usr/bin/env python3
from __future__ import annotations

import argparse
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
from lazy_ring_flux_bimodality import bimodality_paper, fpt_pmf_flux_ring, local_peaks_strict


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=(
            "Collect small-p bimodal curves (AW inversion + flux overlay) for the selfloop shortcut model.\n"
            "Geometry per N: start=n0, target=floor(N/2), u=n0+u_offset, v=target+v_offset.\n"
            "Shortcut probability p = beta*(1-q) taken from self-loop at u."
        )
    )
    p.add_argument("--q", type=float, default=2.0 / 3.0)
    p.add_argument("--beta", type=float, default=0.02)
    p.add_argument("--start", type=int, default=1)
    p.add_argument("--u-offset", type=int, default=5)
    p.add_argument("--v-offset", type=int, default=1)
    p.add_argument("--N-list", type=str, default="70,80,90,100,110,120,130,140,150,160,170,180,190,200")
    p.add_argument("--thresh", type=float, default=1e-7)
    p.add_argument("--tplot", type=int, default=5000, help="AW/plot horizon; should cover the 2nd peak")
    p.add_argument("--oversample", type=int, default=8)
    p.add_argument("--r-pow10", type=float, default=18.0)
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
    if len(Ns) == 0:
        raise ValueError("Empty --N-list.")

    outdir = REPO_ROOT / "figures" / "lazy_ring_flux_bimodality"
    outdir.mkdir(parents=True, exist_ok=True)
    if str(args.out).strip():
        outpath = Path(str(args.out))
    else:
        outpath = outdir / f"lazy_K2_selfloop_smallp_gallery_beta{beta:.4g}.pdf"

    tplot = int(args.tplot)
    thresh = float(args.thresh)

    with PdfPages(outpath) as pdf:
        for N in Ns:
            if N < 3:
                continue

            start = int(args.start) % N
            target = (N // 2) % N
            u = (start + int(args.u_offset)) % N
            v = (target + int(args.v_offset)) % N

            f_flux, surv = fpt_pmf_flux_ring(
                N,
                q,
                start,
                target,
                model="selfloop",
                u=u,
                v=v,
                p=p_sc,
                Tmax=200_000,
                eps_surv=1e-14,
            )

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

            peaks = local_peaks_strict(f_aw, thresh=thresh)
            top2 = top2_by_height(peaks)
            paper_ok, _ = bimodality_paper(f_aw, thresh=thresh, second_frac=0.01)

            x = np.arange(1, tplot + 1, dtype=int)
            y_aw = f_aw[:tplot]
            y_flux = f_flux[:tplot] if f_flux.size >= tplot else np.pad(f_flux, (0, tplot - f_flux.size))

            fig, ax = plt.subplots(figsize=(7.4, 3.6))
            ax.bar(x, y_aw, width=0.8, color="C1", alpha=0.35, label="AW (analytic)")
            ax.plot(x, y_flux, ls="none", marker=".", ms=2.2, color="C0", label="flux")
            ax.set_xlabel("t")
            ax.set_ylabel("f(t)")
            ax.grid(True, alpha=0.22)

            title_lines = [
                f"selfloop small-p: N={N}, q={q:.3g}, beta={beta:.3g} (p={p_sc:.4g}), start={start}, target={target}",
                f"u={u}->v={v} | paper={int(paper_ok)} | AW(m={aw_params.m}, r={aw_params.r:.6f}) | surv={surv:.1e}",
            ]
            ax.set_title("\n".join(title_lines), fontsize=10)
            ax.legend(frameon=False, fontsize=9, ncol=2, loc="upper right")

            if top2 is not None:
                for t, h in top2:
                    ax.scatter([t], [h], s=44, color="C3", zorder=4)
                    ax.axvline(t, color="C3", ls="--", lw=1.1, alpha=0.75)
                    ax.text(t, h, f" t={t}", va="bottom", ha="left", color="C3", fontsize=9)

            fig.tight_layout()
            pdf.savefig(fig)
            plt.close(fig)

    print(f"wrote {outpath}")


if __name__ == "__main__":
    main()
