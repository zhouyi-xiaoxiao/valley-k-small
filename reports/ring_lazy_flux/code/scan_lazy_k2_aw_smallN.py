#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Sequence, Tuple

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import numpy as np

from lazy_ring_aw_chebyshev import fpt_pmf_aw


def paper_modes(f: np.ndarray, *, thresh: float) -> List[Tuple[int, float]]:
    modes: List[Tuple[int, float]] = []
    T = int(f.size)
    for i in range(T):
        left = float(f[i - 1]) if i - 1 >= 0 else 0.0
        right = float(f[i + 1]) if i + 1 < T else 0.0
        if float(f[i]) > left and float(f[i]) > right and float(f[i]) > thresh:
            modes.append((i + 1, float(f[i])))
    return modes


def is_bimodal_paper(f: np.ndarray, *, thresh: float, second_frac: float) -> Tuple[bool, List[Tuple[int, float]]]:
    modes = paper_modes(f, thresh=thresh)
    if len(modes) < 2:
        return False, modes
    heights = sorted([h for _, h in modes], reverse=True)
    ok = heights[1] >= second_frac * heights[0]
    return ok, modes


def is_bimodal_macro(
    f: np.ndarray, *, time_ratio: float, thresh: float, second_frac: float
) -> Tuple[bool, List[Tuple[int, float]]]:
    ok, modes = is_bimodal_paper(f, thresh=thresh, second_frac=second_frac)
    if not ok:
        return False, modes
    top2 = sorted(modes, key=lambda x: -x[1])[:2]
    t1, t2 = sorted([top2[0][0], top2[1][0]])
    if t2 / t1 < time_ratio:
        return False, modes
    return True, modes


@dataclass(frozen=True)
class ScanHit:
    N: int
    target: int
    beta: float
    p: float
    t1: int
    t2: int


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Small-N scan using AW inversion (analytic Chebyshev generating function).")
    p.add_argument("--N-min", type=int, default=6)
    p.add_argument("--N-max", type=int, default=20)
    p.add_argument("--q", type=float, default=2.0 / 3.0, help="total move probability; equal-prob baseline is 2/3")
    p.add_argument("--start", type=int, default=1)
    p.add_argument("--scan-targets", action="store_true", help="scan all targets for each N (default: target=floor(N/2))")
    p.add_argument("--t-max", type=int, default=200, help="max t for AW inversion coefficients")
    p.add_argument("--beta", type=float, nargs="*", default=[0.005, 0.01, 0.02, 0.05, 0.1])
    p.add_argument("--thresh", type=float, default=1e-7)
    p.add_argument("--second-frac", type=float, default=0.01)
    p.add_argument("--time-ratio", type=float, default=10.0)
    return p.parse_args()


def main() -> None:
    args = parse_args()
    hits: List[ScanHit] = []

    for N in range(int(args.N_min), int(args.N_max) + 1):
        start = int(args.start) % N
        targets: Sequence[int]
        if args.scan_targets:
            targets = [t for t in range(N) if t != start]
        else:
            targets = [int(N // 2) % N]

        for target in targets:
            u = start
            v = target
            for beta in args.beta:
                p_sc = float(beta) * (1.0 - float(args.q))
                if p_sc < 0.0 or p_sc > (1.0 - float(args.q)) + 1e-15:
                    continue
                f_aw, _ = fpt_pmf_aw(
                    N=N,
                    q=float(args.q),
                    p=p_sc,
                    start=start,
                    target=target,
                    u=u,
                    v=v,
                    t_max=int(args.t_max),
                    oversample=16,
                    r_pow10=18.0,
                )
                ok, modes = is_bimodal_macro(
                    f_aw, time_ratio=float(args.time_ratio), thresh=float(args.thresh), second_frac=float(args.second_frac)
                )
                if not ok:
                    continue
                top2 = sorted(modes, key=lambda x: -x[1])[:2]
                t1, t2 = sorted([top2[0][0], top2[1][0]])
                hits.append(ScanHit(N=N, target=target, beta=float(beta), p=p_sc, t1=t1, t2=t2))
                break

    if not hits:
        print("No macro-bimodal cases found in this scan.")
        return

    print("Found macro-bimodal cases (AW analytic):")
    for h in hits:
        print(f"  N={h.N:>3d} target={h.target:>3d} beta={h.beta:>6.3f} p={h.p:.6g} peaks=(t1={h.t1}, t2={h.t2})")


if __name__ == "__main__":
    main()
