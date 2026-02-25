#!/usr/bin/env python3
from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import List, Optional, Sequence, Tuple

import numpy as np


def fpt_pmf_flux_ring(
    N: int,
    q: float,
    start: int,
    target: int,
    *,
    model: str = "selfloop",  # "selfloop", "rewire", or "equal4"
    u: Optional[int] = None,
    v: Optional[int] = None,
    p: float = 0.0,  # only for "selfloop"
    which: str = "right",  # only for "rewire": "right" or "left"
    Tmax: int = 200_000,
    eps_surv: float = 1e-14,
) -> Tuple[np.ndarray, float]:
    """
    Time-domain (forward) flux algorithm for first-passage PMF on a lazy ring.

    Ring states: {0,...,N-1}. Base transition (lazy random walk):
      P(i->i)    = 1-q
      P(i->i+1)  = q/2
      P(i->i-1)  = q/2

    Add ONE directed shortcut from u -> v via one of:
      - model="selfloop": take probability p from the self-loop at u and add to u->v.
          Requires 0 <= p <= 1-q.
      - model="rewire": rewire one neighbour edge (q/2) from u->(u±1) to u->v.
          Keeps outgoing distribution at u normalized.
      - model="equal4": override the outgoing distribution at u to be uniform over
          {stay at u, left, right, shortcut to v} i.e. each with probability 1/4.
          (The baseline q still applies at all other nodes.)

    Absorption:
      target is absorbing and removed from transient distribution; f(t) is the flux into target.

    Returns:
      f: array length T where f[t-1]=P(T=t), t>=1
      surv: remaining transient mass after final step (upper bound on truncated tail mass)
    """
    if N <= 1:
        raise ValueError("N must be >= 2.")
    if not (0.0 < q < 1.0):
        raise ValueError("q must be in (0,1).")
    if Tmax <= 0:
        raise ValueError("Tmax must be positive.")
    if eps_surv <= 0:
        raise ValueError("eps_surv must be positive.")

    start %= N
    target %= N
    if u is not None:
        u %= N
    if v is not None:
        v %= N

    if start == target:
        return np.zeros(0, dtype=np.float64), 0.0

    if model not in ("selfloop", "rewire", "equal4"):
        raise ValueError("model must be 'selfloop', 'rewire', or 'equal4'.")
    if u is None or v is None:
        raise ValueError("u and v must be provided.")
    if model == "selfloop":
        if not (0.0 <= p <= (1.0 - q) + 1e-15):
            raise ValueError("selfloop model requires 0 <= p <= 1-q.")
    elif model == "rewire":
        if which not in ("right", "left"):
            raise ValueError("which must be 'right' or 'left'.")

    halfq = 0.5 * q
    stay = 1.0 - q

    dist = np.zeros(N, dtype=np.float64)
    dist[start] = 1.0
    dist[target] = 0.0

    f = np.zeros(int(Tmax), dtype=np.float64)
    steps = 0

    for t in range(int(Tmax)):
        # Baseline lazy ring arrivals:
        # nxt[j] = (1-q)*dist[j] + (q/2)*dist[j-1] + (q/2)*dist[j+1]
        nxt = stay * dist + halfq * np.roll(dist, 1) + halfq * np.roll(dist, -1)

        flux = float(nxt[target])
        nxt[target] = 0.0

        # Defect correction: only row u differs from baseline (unless u is absorbing)
        if u != target:
            mu = float(dist[u])
            if mu != 0.0:
                if model == "selfloop":
                    # baseline u->u has prob (1-q); actual u->u is (1-q-p), u->v adds p
                    nxt[u] -= mu * p
                    if v == target:
                        flux += mu * p
                    else:
                        nxt[v] += mu * p
                elif model == "rewire":
                    w = halfq
                    old = (u + 1) % N if which == "right" else (u - 1) % N
                    if old == target:
                        flux -= mu * w
                    else:
                        nxt[old] -= mu * w

                    if v == target:
                        flux += mu * w
                    else:
                        nxt[v] += mu * w
                else:
                    # model == "equal4": at u, choose uniformly among {stay,left,right,shortcut}
                    base: dict[int, float] = {
                        u: stay,
                        (u + 1) % N: halfq,
                        (u - 1) % N: halfq,
                    }
                    new: dict[int, float] = {}
                    for dest, prob in [
                        (u, 0.25),
                        ((u + 1) % N, 0.25),
                        ((u - 1) % N, 0.25),
                        (v, 0.25),
                    ]:
                        new[dest] = new.get(dest, 0.0) + prob

                    # deltas = (B - A) for the u row (row-stochastic view).
                    deltas: dict[int, float] = dict(base)
                    for dest, prob in new.items():
                        deltas[dest] = deltas.get(dest, 0.0) - prob

                    # We already advanced with baseline B; correct the next arrivals by adding mu*(A-B).
                    for dest, b_minus_a in deltas.items():
                        delta = -b_minus_a
                        if delta == 0.0:
                            continue
                        if dest == target:
                            flux += mu * delta
                        else:
                            nxt[dest] += mu * delta

        # Numerical hygiene: extremely small negative values can appear from roundoff.
        if np.min(nxt) < 0.0:
            nxt = np.maximum(nxt, 0.0)

        f[t] = flux
        dist = nxt
        steps = t + 1
        if float(dist.sum()) < eps_surv:
            break

    f = f[:steps].copy()
    return f, float(dist.sum())


def local_peaks_strict(f: np.ndarray, *, thresh: float) -> List[Tuple[int, float]]:
    """
    Strict local maxima above `thresh`.

    Endpoints are allowed (t=1 and t=T): we compare the missing neighbour to 0,
    which is appropriate for PMFs where f(t) >= 0 and endpoints can be true peaks.
    """
    peaks: List[Tuple[int, float]] = []
    T = int(f.size)
    for i in range(T):
        left = float(f[i - 1]) if i - 1 >= 0 else 0.0
        right = float(f[i + 1]) if i + 1 < T else 0.0
        if float(f[i]) > left and float(f[i]) > right and float(f[i]) > thresh:
            peaks.append((i + 1, float(f[i])))
    return peaks


@dataclass(frozen=True)
class BimodalityResult:
    ok: bool
    top2: Optional[Tuple[Tuple[int, float], Tuple[int, float]]]
    valley: Optional[float]
    reason: Optional[str]
    peaks: Tuple[Tuple[int, float], ...]


def bimodality_paper(
    f: np.ndarray, *, thresh: float = 1e-7, second_frac: float = 0.01
) -> Tuple[bool, Tuple[Tuple[int, float], ...]]:
    """
    Paper-style criterion:
      - strict local peaks above `thresh`
      - second-highest peak height >= second_frac * (highest peak height)
    """
    peaks = tuple(local_peaks_strict(f, thresh=thresh))
    if len(peaks) < 2:
        return False, peaks
    heights = sorted((h for _, h in peaks), reverse=True)
    return heights[1] >= second_frac * heights[0], peaks


def bimodality_macro(
    f: np.ndarray, *, time_ratio: float = 10.0, thresh: float = 1e-7, second_frac: float = 0.01
) -> Tuple[bool, Tuple[Tuple[int, float], ...]]:
    """
    Macro-bimodality (optional extra condition):
      - satisfy paper-style bimodality
      - top-2 peaks by height satisfy t2/t1 >= time_ratio
    """
    ok, peaks = bimodality_paper(f, thresh=thresh, second_frac=second_frac)
    if not ok:
        return False, peaks
    top2 = sorted(peaks, key=lambda x: -x[1])[:2]
    t1, t2 = sorted([top2[0][0], top2[1][0]])
    return (t1 > 0) and (t2 / t1 >= time_ratio), peaks


def bimodality_test(
    f: np.ndarray,
    *,
    thresh: float = 1e-12,
    second_frac: float = 0.01,
    require_time_separation: bool = True,
    time_ratio: float = 10.0,
    require_valley: bool = True,
    valley_frac: float = 0.7,
) -> BimodalityResult:
    """
    Robust (but simple) bimodality test:
      1) strict local maxima above thresh
      2) take top-2 peaks by height, enforce second peak >= second_frac * first peak
      3) optional time-scale separation: t2/t1 >= time_ratio
      4) optional valley depth: min_{t1<t<t2} f(t) <= valley_frac * min(h1,h2)
    """
    peaks = local_peaks_strict(f, thresh=thresh)
    if len(peaks) < 2:
        return BimodalityResult(
            ok=False, top2=None, valley=None, reason="fewer than 2 local peaks", peaks=tuple(peaks)
        )

    best_pair: Optional[Tuple[Tuple[int, float], Tuple[int, float]]] = None
    best_valley: Optional[float] = None
    best_score: Optional[Tuple[float, int]] = None  # (hmin, separation)

    for i in range(len(peaks)):
        t1, h1 = peaks[i]
        for j in range(i + 1, len(peaks)):
            t2, h2 = peaks[j]
            if t2 <= t1:
                continue

            hmax = max(h1, h2)
            hmin = min(h1, h2)
            if hmin < second_frac * hmax:
                continue

            if require_time_separation and (t1 <= 0 or (t2 / t1) < time_ratio):
                continue

            valley = None
            if require_valley:
                if t2 - t1 < 2:
                    continue
                interior = f[t1 : (t2 - 1)]
                valley = float(np.min(interior)) if interior.size > 0 else None
                if valley is None or valley > valley_frac * hmin:
                    continue

            score = (hmin, t2 - t1)
            if best_score is None or score > best_score:
                best_score = score
                best_pair = ((t1, h1), (t2, h2))
                best_valley = valley

    if best_pair is None:
        return BimodalityResult(ok=False, top2=None, valley=None, reason="no peak pair passes criteria", peaks=tuple(peaks))

    return BimodalityResult(ok=True, top2=best_pair, valley=best_valley, reason=None, peaks=tuple(peaks))


def demo_scan(
    *,
    N: int,
    q_values: Sequence[float],
    betas: Sequence[float],
    Tmax: int,
    eps_surv: float,
) -> None:
    start = 1 % N
    target = (N // 2) % N
    u = start
    v = target

    print(f"Demo setup: N={N} start={start} target={target} u={u} v={v} (direct jump to target)")

    for q in q_values:
        f_rw, surv_rw = fpt_pmf_flux_ring(
            N,
            q,
            start,
            target,
            model="rewire",
            u=u,
            v=v,
            which="right",
            Tmax=Tmax,
            eps_surv=eps_surv,
        )
        res_rw = bimodality_test(f_rw)
        paper_rw, peaks_rw = bimodality_paper(f_rw)
        macro_rw, _ = bimodality_macro(f_rw)
        mass_rw = float(f_rw.sum())
        print(
            f"[rewire]   q={q:.2f}  bimodal_pair={res_rw.ok}  paper={paper_rw}  macro={macro_rw}  "
            f"npeaks={len(peaks_rw)}  mass={mass_rw:.12f}  surv={surv_rw:.2e}  top2={res_rw.top2}"
        )

        for beta in betas:
            p = beta * (1.0 - q)
            f_sl, surv_sl = fpt_pmf_flux_ring(
                N,
                q,
                start,
                target,
                model="selfloop",
                u=u,
                v=v,
                p=p,
                Tmax=Tmax,
                eps_surv=eps_surv,
            )
            res_sl = bimodality_test(f_sl)
            paper_sl, peaks_sl = bimodality_paper(f_sl)
            macro_sl, _ = bimodality_macro(f_sl)
            mass_sl = float(f_sl.sum())
            print(
                f"  [selfloop] beta={beta:>4.2f} p={p:>7.4f}  bimodal_pair={res_sl.ok}  paper={paper_sl}  macro={macro_sl}  "
                f"npeaks={len(peaks_sl)}  mass={mass_sl:.12f}  surv={surv_sl:.2e}  top2={res_sl.top2}"
            )


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Lazy ring + one directed shortcut: FPT PMF via flux + bimodality test.")
    p.add_argument("--N", type=int, default=101)
    p.add_argument("--q", type=float, default=0.8)
    p.add_argument("--start", type=int, default=1)
    p.add_argument("--target", type=int, default=50)
    p.add_argument("--model", choices=("selfloop", "rewire", "equal4"), default="selfloop")
    p.add_argument("--u", type=int, default=1)
    p.add_argument("--v", type=int, default=50)
    p.add_argument("--p", type=float, default=0.02, help="Shortcut prob for selfloop model (absolute, not beta).")
    p.add_argument("--which", choices=("right", "left"), default="right")
    p.add_argument("--Tmax", type=int, default=50_000)
    p.add_argument("--eps-surv", type=float, default=1e-12)
    p.add_argument("--demo", action="store_true", help="Run a small parameter scan demo.")
    return p.parse_args()


def main() -> None:
    args = parse_args()

    if args.demo:
        demo_scan(N=args.N, q_values=[0.6, 0.7, 0.8, 0.9], betas=[0.0, 0.05, 0.1, 0.2, 0.5], Tmax=args.Tmax, eps_surv=args.eps_surv)
        return

    f, surv = fpt_pmf_flux_ring(
        args.N,
        args.q,
        args.start,
        args.target,
        model=args.model,
        u=args.u,
        v=args.v,
        p=args.p,
        which=args.which,
        Tmax=args.Tmax,
        eps_surv=args.eps_surv,
    )

    res = bimodality_test(f)
    paper_ok, paper_peaks = bimodality_paper(f)
    macro_ok, _ = bimodality_macro(f)
    print(f"N={args.N} q={args.q} start={args.start} target={args.target} model={args.model} u={args.u} v={args.v}")
    if args.model == "selfloop":
        print(f"p={args.p}")
    else:
        print(f"which={args.which}")
    print(
        f"computed_steps={len(f)} mass={float(f.sum()):.16f} surv={surv:.3e} "
        f"bimodal_pair={res.ok} paper={paper_ok} macro={macro_ok} npeaks={len(paper_peaks)}"
    )
    print(f"top2_pair={res.top2} valley={res.valley} reason={res.reason}")


if __name__ == "__main__":
    main()
