#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from lazy_ring_flux_bimodality import fpt_pmf_flux_ring
from lazy_ring_aw_chebyshev import fpt_pmf_aw


def local_peaks(f: np.ndarray, *, thresh: float) -> list[tuple[int, float]]:
    peaks: list[tuple[int, float]] = []
    for i in range(int(f.size)):
        left = float(f[i - 1]) if i - 1 >= 0 else 0.0
        right = float(f[i + 1]) if i + 1 < f.size else 0.0
        if float(f[i]) > left and float(f[i]) > right and float(f[i]) > thresh:
            peaks.append((i + 1, float(f[i])))
    return peaks


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Plot k=1 (K=2) lazy ring FPT pmf: AW inversion vs flux validation.")
    p.add_argument("--N", type=int, default=10)
    p.add_argument("--q", type=float, default=2.0 / 3.0, help="total move probability; equal-prob baseline is 2/3")
    p.add_argument("--start", type=int, default=1)
    p.add_argument("--target", type=int, default=5)
    p.add_argument("--u", type=int, default=1)
    p.add_argument("--v", type=int, default=5)
    p.add_argument("--p", dest="p_sc", type=float, default=None, help="shortcut prob taken from self-loop at u")
    p.add_argument(
        "--beta",
        type=float,
        default=0.02,
        help="if --p is omitted, use p = beta*(1-q) (beta=0.02 matches the report example)",
    )
    p.add_argument("--tplot", type=int, default=60, help="plot horizon (t=1..tplot)")
    p.add_argument("--thresh", type=float, default=1e-7, help="peak threshold for reporting top-2 peaks")
    p.add_argument("--eps-surv", type=float, default=1e-14, help="stop flux when survival < eps")
    return p.parse_args()


def main() -> None:
    args = parse_args()

    N = int(args.N)
    q = float(args.q)
    start = int(args.start) % N
    target = int(args.target) % N
    u = int(args.u) % N
    v = int(args.v) % N
    if args.p_sc is None:
        p_sc = float(args.beta) * (1.0 - q)
    else:
        p_sc = float(args.p_sc)

    f, surv = fpt_pmf_flux_ring(
        N,
        q,
        start,
        target,
        model="selfloop",
        u=u,
        v=v,
        p=p_sc,
        Tmax=200_000,
        eps_surv=float(args.eps_surv),
    )
    peaks = local_peaks(f, thresh=float(args.thresh))
    top2 = sorted(peaks, key=lambda x: -x[1])[:2]
    top2_sorted = sorted(top2, key=lambda x: x[0])

    outdir = REPO_ROOT / "figures" / "lazy_ring_flux_bimodality"
    outdir.mkdir(parents=True, exist_ok=True)
    if N == 10 and abs(q - 2.0 / 3.0) < 1e-12 and start == 1 and target == 5 and u == 1 and v == 5:
        outname = "lazy_K2_equalprob_N10_aw_vs_flux.pdf"
    else:
        outname = f"lazy_K2_equalprob_N{N}_target{target}_aw_vs_flux.pdf"
    outpath = outdir / outname

    tplot = int(args.tplot)
    x = np.arange(1, min(tplot, int(f.size)) + 1, dtype=int)
    y_flux = f[: x.size].copy()

    y_aw, aw_params = fpt_pmf_aw(
        N=N, q=q, p=p_sc, start=start, target=target, u=u, v=v, t_max=int(x.size), oversample=16, r_pow10=18.0
    )
    y_aw = np.maximum(y_aw, 0.0)

    fig, ax = plt.subplots(figsize=(7.4, 3.4))
    ax.bar(x, y_aw, width=0.8, color="C1", alpha=0.35, label="AW inversion (analytic $\\~F$)")
    ax.plot(x, y_flux, ls="none", marker="o", ms=3.0, color="C0", label="flux (time-domain)")
    ax.set_xlabel("t")
    ax.set_ylabel("f(t)")
    ax.grid(True, alpha=0.25)
    ax.set_title(
        "\n".join(
            [
                f"equal-prob k=1 (K=2): N={N}, q={q:.3g}, p={p_sc:.3g}, u={u}->v={v}",
                f"AW: m={aw_params.m}, r={aw_params.r:.6f}",
            ]
        ),
        fontsize=10,
    )
    ax.legend(frameon=False, fontsize=9, ncol=2)

    for t, h in top2_sorted:
        if t <= x[-1]:
            ax.scatter([t], [h], s=44, color="C3", zorder=4)
            ax.axvline(t, color="C3", ls="--", lw=1.2, alpha=0.8)
            ax.text(t, h, f" t={t}", va="bottom", ha="left", color="C3")

    fig.tight_layout()
    fig.savefig(outpath)
    plt.close(fig)

    print(f"wrote {outpath}")
    print(f"mass={float(f.sum()):.16f} surv={surv:.3e}")
    print(f"#peaks(thresh={float(args.thresh):.3g})={len(peaks)} top2={top2_sorted}")
    print(f"aw(m={aw_params.m}, r={aw_params.r:.8f}) max|aw-flux|={float(np.max(np.abs(y_aw - y_flux))):.3e}")


if __name__ == "__main__":
    main()
