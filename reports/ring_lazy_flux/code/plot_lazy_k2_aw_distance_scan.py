#!/usr/bin/env python3
from __future__ import annotations

import argparse
from dataclasses import dataclass
import math
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from lazy_ring_aw_chebyshev import fpt_pmf_aw, ring_distance


def paper_modes(f: np.ndarray, *, thresh: float) -> list[tuple[int, float]]:
    modes: list[tuple[int, float]] = []
    T = int(f.size)
    for i in range(T):
        left = float(f[i - 1]) if i - 1 >= 0 else 0.0
        right = float(f[i + 1]) if i + 1 < T else 0.0
        if float(f[i]) > left and float(f[i]) > right and float(f[i]) > thresh:
            modes.append((i + 1, float(f[i])))
    return modes


def is_bimodal_macro(
    f: np.ndarray, *, time_ratio: float, thresh: float, second_frac: float
) -> tuple[bool, list[tuple[int, float]]]:
    modes = paper_modes(f, thresh=thresh)
    if len(modes) < 2:
        return False, modes
    top2 = sorted(modes, key=lambda x: -x[1])[:2]
    (t1, h1), (t2, h2) = sorted(top2, key=lambda x: x[0])
    if min(h1, h2) < second_frac * max(h1, h2):
        return False, modes
    if t2 / t1 < time_ratio:
        return False, modes
    return True, modes


@dataclass(frozen=True)
class Params:
    N_min: int
    N_max: int
    q: float
    beta: float
    start: int
    t_max: int
    thresh: float
    second_frac: float
    time_ratio: float


def parse_args() -> Params:
    p = argparse.ArgumentParser(
        description="Scan k=1 (K=2) lazy ring: macro-bimodality vs ring distance (AW analytic)."
    )
    p.add_argument("--N-min", type=int, default=6)
    p.add_argument("--N-max", type=int, default=20)
    p.add_argument("--q", type=float, default=2.0 / 3.0, help="equal-prob baseline is 2/3")
    p.add_argument("--beta", type=float, default=0.02, help="p = beta*(1-q)")
    p.add_argument("--start", type=int, default=1)
    p.add_argument("--t-max", type=int, default=200, help="AW coefficient horizon")
    p.add_argument("--thresh", type=float, default=1e-7)
    p.add_argument("--second-frac", type=float, default=0.01)
    p.add_argument("--time-ratio", type=float, default=10.0)
    args = p.parse_args()
    return Params(
        N_min=int(args.N_min),
        N_max=int(args.N_max),
        q=float(args.q),
        beta=float(args.beta),
        start=int(args.start),
        t_max=int(args.t_max),
        thresh=float(args.thresh),
        second_frac=float(args.second_frac),
        time_ratio=float(args.time_ratio),
    )


def main() -> None:
    params = parse_args()
    if params.N_min < 3 or params.N_max < params.N_min:
        raise ValueError("Require 3 <= N_min <= N_max.")

    p_sc = params.beta * (1.0 - params.q)
    max_d = int(params.N_max // 2)

    Ns = list(range(params.N_min, params.N_max + 1))
    t2_grid = np.full((len(Ns), max_d), np.nan, dtype=np.float64)

    for i, N in enumerate(Ns):
        start = params.start % N
        u = start
        for d in range(1, int(N // 2) + 1):
            target = (start + d) % N
            v = target
            f_aw, _ = fpt_pmf_aw(
                N=N,
                q=params.q,
                p=p_sc,
                start=start,
                target=target,
                u=u,
                v=v,
                t_max=params.t_max,
                oversample=16,
                r_pow10=18.0,
            )
            ok, modes = is_bimodal_macro(
                f_aw, time_ratio=params.time_ratio, thresh=params.thresh, second_frac=params.second_frac
            )
            if not ok:
                continue
            top2 = sorted(modes, key=lambda x: -x[1])[:2]
            t1, t2 = sorted([top2[0][0], top2[1][0]])
            # sanity: reflect symmetry check (depends only on distance)
            if ring_distance(start, target, N) != d:
                raise RuntimeError("distance mismatch")
            t2_grid[i, d - 1] = float(t2)

    outdir = REPO_ROOT / "figures" / "lazy_ring_flux_bimodality"
    outdir.mkdir(parents=True, exist_ok=True)
    outpath = outdir / f"lazy_K2_equalprob_macro_scan_N{params.N_min}_{params.N_max}.pdf"

    fig, ax = plt.subplots(figsize=(7.6, 4.2))
    data = np.ma.masked_invalid(t2_grid)
    cmap = plt.get_cmap("viridis").copy()
    cmap.set_bad(color="#f0f0f0")
    im = ax.imshow(data, aspect="auto", origin="lower", cmap=cmap)
    ax.set_title(
        f"macro-bimodal (AW analytic): q={params.q:.3g}, beta={params.beta:.3g} (p={p_sc:.3g}), "
        f"thresh={params.thresh:.0e}, t2/t1>={params.time_ratio:g}"
    )
    ax.set_xlabel("ring distance d = dist(start, target)")
    ax.set_ylabel("N")
    # Reduce tick-label density so they don't overlap for larger scans.
    max_x_labels = 16
    max_y_labels = 14
    x_step = max(1, int(math.ceil(max_d / max_x_labels)))
    y_step = max(1, int(math.ceil(len(Ns) / max_y_labels)))

    x_pos = np.arange(0, max_d, x_step)
    ax.set_xticks(x_pos)
    ax.set_xticklabels([str(int(p + 1)) for p in x_pos])

    y_pos = np.arange(0, len(Ns), y_step)
    ax.set_yticks(y_pos)
    ax.set_yticklabels([str(Ns[int(p)]) for p in y_pos])
    ax.tick_params(axis="both", labelsize=8)
    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("t2 (later dominant peak time)")
    fig.tight_layout()
    fig.savefig(outpath)
    plt.close(fig)

    print(f"wrote {outpath}")


if __name__ == "__main__":
    main()
