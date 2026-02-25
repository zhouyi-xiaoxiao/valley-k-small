#!/usr/bin/env python3
from __future__ import annotations

import argparse
from typing import List, Tuple

import numpy as np


# -------------------------
# 1) Mode detection (paper criterion)
# -------------------------
def paper_modes(f: np.ndarray, thresh: float = 1e-7) -> List[Tuple[int, float]]:
    """f[t-1] = P(T=t), t>=1"""
    modes: List[Tuple[int, float]] = []
    T = len(f)
    for i in range(T):
        left = float(f[i - 1]) if i - 1 >= 0 else 0.0
        right = float(f[i + 1]) if i + 1 < T else 0.0
        if float(f[i]) > left and float(f[i]) > right and float(f[i]) > thresh:
            modes.append((i + 1, float(f[i])))
    return modes


def is_bimodal_paper(
    f: np.ndarray, *, thresh: float = 1e-7, second_frac: float = 0.01
) -> Tuple[bool, List[Tuple[int, float]]]:
    modes = paper_modes(f, thresh=thresh)
    if len(modes) < 2:
        return False, modes
    heights = sorted([h for _, h in modes], reverse=True)
    ok = heights[1] >= second_frac * heights[0]
    return ok, modes


def is_bimodal_macro(
    f: np.ndarray,
    *,
    time_ratio: float = 10.0,
    thresh: float = 1e-7,
    second_frac: float = 0.01,
) -> Tuple[bool, List[Tuple[int, float]]]:
    """Optional: require top-2 peaks separated by at least a factor time_ratio."""
    ok, modes = is_bimodal_paper(f, thresh=thresh, second_frac=second_frac)
    if not ok:
        return False, modes
    top2 = sorted(modes, key=lambda x: -x[1])[:2]
    t1, t2 = sorted([top2[0][0], top2[1][0]])
    if t2 / t1 < time_ratio:
        return False, modes
    return True, modes


# -------------------------
# 2) Build transition matrices
# -------------------------
def build_lazy_ring_from_selfloop(N: int, q: float) -> np.ndarray:
    """Row-stochastic M[i,j]=P(X_{t+1}=j|X_t=i) for lazy NN ring."""
    M = np.zeros((N, N), float)
    for i in range(N):
        M[i, (i - 1) % N] += q / 2
        M[i, (i + 1) % N] += q / 2
        M[i, i] += 1 - q
    return M


def add_directed_shortcut_from_selfloop(M: np.ndarray, u: int, v: int, p: float) -> np.ndarray:
    """
    Your LaTeX model:
      at u: self-loop reduced by p, add p to v.
    Need 0 <= p <= (self-loop at u) initially.
    """
    if p < 0 or p > float(M[u, u]) + 1e-15:
        raise ValueError("p out of range for 'from self-loop' model.")
    M2 = M.copy()
    M2[u, u] -= p
    M2[u, v] += p
    return M2


def rewire_one_edge_degree_preserving(M: np.ndarray, u: int, v: int, which: str = "right") -> np.ndarray:
    """
    Degree-preserving K=2 case:
    Take probability q/2 from one neighbor edge at u and redirect to v.
    (Self-loop 1-q unchanged.)
    """
    N = M.shape[0]
    M2 = M.copy()
    old = (u + 1) % N if which == "right" else (u - 1) % N
    w = float(M2[u, old])
    M2[u, old] -= w
    M2[u, v] += w
    return M2


# -------------------------
# 3) Exact FPT pmf via absorbing-chain propagation
# -------------------------
def fpt_pmf_exact(
    M: np.ndarray,
    start: int,
    target: int,
    *,
    eps: float = 1e-14,
    Tmax: int = 500_000,
    renormalize: bool = True,
) -> np.ndarray:
    """
    Compute P(T=t) for t>=1 by evolving the transient distribution on an
    absorbing Markov chain (dense Q update).

    Note: if `renormalize=True`, the output is normalized to sum to 1 even if truncated.
    """
    N = M.shape[0]
    A = M.copy()
    A[target, :] = 0.0
    A[target, target] = 1.0

    if start == target:
        return np.array([1.0])

    trans = [s for s in range(N) if s != target]
    idx = {s: i for i, s in enumerate(trans)}

    Q = A[np.ix_(trans, trans)]
    r = A[np.ix_(trans, [target])].reshape(-1)

    pi = np.zeros(len(trans))
    pi[idx[start]] = 1.0

    f: List[float] = []
    surv = 1.0
    t = 0
    while t < Tmax and surv > eps:
        f.append(float(pi @ r))  # flux to target at step t+1
        pi = pi @ Q
        surv = float(pi.sum())
        t += 1

    f_arr = np.asarray(f, dtype=float)
    if renormalize and float(f_arr.sum()) > 0.0:
        f_arr = f_arr / float(f_arr.sum())
    return f_arr


# -------------------------
# 4) Scan runner (odd/even N)
# -------------------------
def run_scan(
    *,
    N_list=(100, 101),
    q_list=(0.6, 0.7, 0.8, 0.9),
    u_offset: int = 5,
    v_offset: int = 1,
    eps: float = 1e-14,
    Tmax: int = 500_000,
    thresh: float = 1e-7,
    second_frac: float = 0.01,
    time_ratio: float = 10.0,
    renormalize: bool = True,
) -> None:
    """
    Geometry similar to your paper figure:
      start n0=1
      target n=floor(N/2) (for even it is N/2)
      u = n0 + u_offset
      v = target + v_offset
    """
    for N in N_list:
        n0 = 1 % N
        target = (N // 2) % N
        u = (n0 + u_offset) % N
        v = (target + v_offset) % N

        print(f"\n=== N={N} (target={target}), n0={n0}, u={u}, v={v} ===")

        for q in q_list:
            base = build_lazy_ring_from_selfloop(N, q)

            M_rewire = rewire_one_edge_degree_preserving(base, u=u, v=v, which="right")
            f_rewire = fpt_pmf_exact(M_rewire, start=n0, target=target, eps=eps, Tmax=Tmax, renormalize=renormalize)
            bim_paper, modes_paper = is_bimodal_paper(f_rewire, thresh=thresh, second_frac=second_frac)
            bim_macro, _ = is_bimodal_macro(f_rewire, time_ratio=time_ratio, thresh=thresh, second_frac=second_frac)

            top2 = sorted(modes_paper, key=lambda x: -x[1])[:2]
            print(
                f"[rewire] q={q:.2f}  paper_bimodal={bim_paper}  macro_bimodal={bim_macro}  "
                f"#modes={len(modes_paper)}  top2={top2}"
            )

            for beta in [0.0, 0.05, 0.1, 0.2, 1.0]:
                p = beta * (1 - q)
                M_p = add_directed_shortcut_from_selfloop(base, u=u, v=v, p=p)
                f_p = fpt_pmf_exact(M_p, start=n0, target=target, eps=eps, Tmax=Tmax, renormalize=renormalize)
                bim_paper_p, modes_p = is_bimodal_paper(f_p, thresh=thresh, second_frac=second_frac)
                bim_macro_p, _ = is_bimodal_macro(f_p, time_ratio=time_ratio, thresh=thresh, second_frac=second_frac)
                top2p = sorted(modes_p, key=lambda x: -x[1])[:2]
                print(
                    f"   [selfloop] beta={beta:>4.2f}, p={p:>7.4f}  paper={bim_paper_p}  macro={bim_macro_p} "
                    f"#modes={len(modes_p)}  top2={top2p}"
                )


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="User-provided dense exact scan (lazy K=2) with paper criterion.")
    p.add_argument("--Tmax", type=int, default=50_000)
    p.add_argument("--eps", type=float, default=1e-12)
    p.add_argument("--thresh", type=float, default=1e-7)
    p.add_argument("--second-frac", type=float, default=0.01)
    p.add_argument("--time-ratio", type=float, default=10.0)
    p.add_argument("--no-renorm", action="store_true", help="Disable renormalization of truncated f(t).")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    run_scan(
        eps=args.eps,
        Tmax=args.Tmax,
        thresh=args.thresh,
        second_frac=args.second_frac,
        time_ratio=args.time_ratio,
        renormalize=not args.no_renorm,
    )


if __name__ == "__main__":
    main()

