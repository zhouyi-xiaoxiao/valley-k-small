#!/usr/bin/env python3
from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import sys
from typing import List, Optional, Sequence, Tuple

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from lazy_ring_aw_chebyshev import fpt_pmf_aw


def strict_local_modes(f: np.ndarray, *, thresh: float) -> List[Tuple[int, float]]:
    modes: List[Tuple[int, float]] = []
    T = int(f.size)
    for i in range(T):
        left = float(f[i - 1]) if i - 1 >= 0 else 0.0
        right = float(f[i + 1]) if i + 1 < T else 0.0
        fi = float(f[i])
        if fi > left and fi > right and fi >= thresh:
            modes.append((i + 1, fi))
    return modes


@dataclass(frozen=True)
class PeakSummary:
    n_modes: int
    paper_bimodal: bool
    macro_bimodal: bool
    t1: Optional[int]
    t2: Optional[int]


def summarize_peaks(
    f: np.ndarray, *, thresh: float, second_frac: float, time_ratio: float
) -> PeakSummary:
    modes = strict_local_modes(f, thresh=thresh)
    if len(modes) < 2:
        return PeakSummary(n_modes=len(modes), paper_bimodal=False, macro_bimodal=False, t1=None, t2=None)
    top2 = sorted(modes, key=lambda x: -x[1])[:2]
    (t_a, h_a), (t_b, h_b) = top2
    paper = min(h_a, h_b) >= second_frac * max(h_a, h_b)
    t1, t2 = sorted([t_a, t_b])
    macro = bool(paper and (t2 / t1 >= time_ratio))
    return PeakSummary(n_modes=len(modes), paper_bimodal=paper, macro_bimodal=macro, t1=t1, t2=t2)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Generate multi-panel AW-inversion plots for k=1 (K=2) lazy ring examples.")
    p.add_argument("--q", type=float, default=2.0 / 3.0)
    p.add_argument("--beta", type=float, default=0.02)
    p.add_argument("--start", type=int, default=1)
    p.add_argument("--t-factor", type=float, default=4.0, help="plot horizon: t_max = ceil(t_factor * N^2)")
    p.add_argument("--oversample", type=int, default=4)
    p.add_argument("--r-pow10", type=float, default=18.0)
    p.add_argument("--thresh", type=float, default=1e-7)
    p.add_argument("--second-frac", type=float, default=0.01)
    p.add_argument("--time-ratio", type=float, default=10.0)
    p.add_argument(
        "--group",
        choices=["even_small", "odd_small", "even_medium"],
        default="even_small",
        help="which built-in N-set to plot",
    )
    return p.parse_args()


def group_Ns(name: str) -> Sequence[int]:
    if name == "even_small":
        return [4, 6, 8, 10, 12, 14, 16, 18, 20]
    if name == "odd_small":
        return [5, 7, 9, 11, 13, 15, 17, 19, 21]
    if name == "even_medium":
        return [24, 28, 32, 36, 40, 44, 48, 52, 56, 60]
    raise ValueError(f"unknown group: {name}")


def subplot_grid(n: int) -> Tuple[int, int]:
    if n <= 9:
        return 3, 3
    if n <= 12:
        return 3, 4
    return 4, 4


def main() -> None:
    args = parse_args()
    q = float(args.q)
    beta = float(args.beta)
    start = int(args.start)
    p_sc = beta * (1.0 - q)

    Ns = list(group_Ns(str(args.group)))
    nrows, ncols = subplot_grid(len(Ns))

    outdir = REPO_ROOT / "figures" / "lazy_ring_flux_bimodality"
    outdir.mkdir(parents=True, exist_ok=True)
    outpath = outdir / f"lazy_K2_aw_antipodal_{args.group}.pdf"

    fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(3.6 * ncols, 2.6 * nrows), squeeze=False)
    for ax in axes.flat:
        ax.axis("off")

    for idx, N in enumerate(Ns):
        ax = axes.flat[idx]
        ax.axis("on")
        n0 = start % N
        d = int(N // 2)
        target = (n0 + d) % N
        u = n0
        v = target
        t_max = int(np.ceil(float(args.t_factor) * float(N * N)))

        f, aw_params = fpt_pmf_aw(
            N=N,
            q=q,
            p=p_sc,
            start=n0,
            target=target,
            u=u,
            v=v,
            t_max=t_max,
            oversample=int(args.oversample),
            r_pow10=float(args.r_pow10),
        )
        f = np.maximum(f, 0.0)
        summ = summarize_peaks(
            f, thresh=float(args.thresh), second_frac=float(args.second_frac), time_ratio=float(args.time_ratio)
        )

        x = np.arange(1, f.size + 1, dtype=int)
        ax.plot(x, f, ls="none", marker=".", ms=1.3, color="C0")
        ax.set_xlim(1, int(f.size))
        ax.grid(True, alpha=0.18)
        ax.set_title(
            f"N={N}, d={d}, paper={int(summ.paper_bimodal)}, macro={int(summ.macro_bimodal)}"
            + (f", (t1,t2)=({summ.t1},{summ.t2})" if summ.t1 is not None else ""),
            fontsize=9,
        )
        ax.set_xlabel("t", fontsize=9)
        ax.set_ylabel("f(t)", fontsize=9)

    fig.suptitle(
        f"AW inversion (analytic): q={q:.6g}, beta={beta:.6g} (p={p_sc:.6g}), start=n0={start} (antipodal target)",
        fontsize=11,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    fig.savefig(outpath)
    plt.close(fig)

    print(f"wrote {outpath}")


if __name__ == "__main__":
    main()
