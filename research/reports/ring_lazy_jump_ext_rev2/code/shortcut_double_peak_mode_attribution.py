#!/usr/bin/env python3
# wrapper-report-id: ring_lazy_jump_ext_rev2
"""Mode attribution for the antipodal shortcut-to-target double peak.

Model (0-indexed): lazy ring of N sites (stay 1-q, hop q/2 each way),
absorbing target v=0, antipodal shortcut source u=N/2 moving beta*(1-q)
from the u self-loop onto the directed edge u->v.  Start site n0.

The C.2 geometry of the corrected notes (paper sites: target 56, shortcut
6->56, starts 1..6, N=100) maps to: start at ring distance d from u on the
far side of the target, i.e. n0 = u + d (mod N) with d = u_paper - n0_paper,
so the start-to-target ring distance is rho = L - d.

Exact decomposition: F(t) = sum_i kappa_i lambda_i^{t-1}, from eigh of the
symmetric transient block; cross-checked against the Chebyshev closed form
s_j = 1-q+q*y_j (D(y_j)=0, D=a T_L + U_{L-1}, a=q/(beta(1-q))) and
B_rho_j = q (a T_{L-rho} + U_{rho-1} + U_{L-rho-1})(y_j) / D'(y_j).

Classifier: the C.2 "clear double peak" rule, verbatim:
  >=2 strict local peaks of F(t) above 1e-12; secondary peak >= 1% of the
  largest; peak separation >= 10 steps; h2/h1 in [0.1, 10]; valley <= 0.8 of
  the smaller peak.  (h1 = earlier peak, h2 = later peak.)
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import dataclass, asdict
from pathlib import Path

import numpy as np

_VKCORE_SRC = Path(__file__).resolve().parents[3].parent / "packages" / "vkcore" / "src"
if str(_VKCORE_SRC) not in sys.path:
    sys.path.insert(0, str(_VKCORE_SRC))
try:
    from vkcore.common.fpt_metrics import paper_style_bimodality  # noqa: E402
except Exception:                                                  # pragma: no cover
    paper_style_bimodality = None

Q_DEFAULT = 2.0 / 3.0
H_MIN = 1e-12
MIN_RATIO = 0.01
MIN_SEP = 10
HRATIO_LO, HRATIO_HI = 0.1, 10.0
VALLEY_FRAC = 0.8
SURVIVAL_EPS = 1e-13
TMAX_CAP = 2_000_000


# ----------------------------------------------------------------------
# exact chain and spectral decomposition
# ----------------------------------------------------------------------

def transient_block(N: int, q: float, beta: float):
    """Symmetric transient block A ((N-1)x(N-1), site order 1..N-1) and
    absorption vector b (one-step probability into v=0)."""
    n = N - 1
    lam = beta * (1.0 - q)
    A = np.zeros((n, n))
    b = np.zeros(n)
    for i in range(1, N):
        k = i - 1
        stay = 1.0 - q
        if i == N // 2:
            stay = (1.0 - beta) * (1.0 - q)
            b[k] += lam
        A[k, k] = stay
        for j in (i - 1, i + 1):
            jj = j % N
            if jj == 0:
                b[k] += q / 2.0
            else:
                A[k, jj - 1] += q / 2.0
    return A, b


@dataclass
class Spectral:
    lams: np.ndarray          # eigenvalues, descending
    kappas: np.ndarray        # per-mode amplitudes for the chosen start
    occup_u: np.ndarray       # per-mode V[start,i]*V[u,i] (for capture split)
    N: int
    q: float
    beta: float
    n0: int                   # 0-indexed start site


def spectral(N: int, q: float, beta: float, n0: int) -> Spectral:
    A, b = transient_block(N, q, beta)
    w, V = np.linalg.eigh(A)
    order = np.argsort(w)[::-1]
    w, V = w[order], V[:, order]
    k0 = n0 - 1
    ku = N // 2 - 1
    kappas = V[k0, :] * (V.T @ b)
    occup_u = V[k0, :] * V[ku, :]
    return Spectral(w, kappas, occup_u, N, q, beta, n0)


def pmf_from_modes(lams: np.ndarray, kappas: np.ndarray, tmax: int,
                   chunk: int = 200_000) -> np.ndarray:
    """F(t) for t=1..tmax via sum_i kappa_i lambda_i^{t-1}, chunked in t."""
    out = np.empty(tmax)
    keep = np.abs(kappas) > 0.0
    lam = lams[keep]
    kap = kappas[keep]
    sign = np.sign(lam)
    sign[sign == 0.0] = 1.0
    loga = np.minimum(np.log(np.maximum(np.abs(lam), 1e-300)), 0.0)
    for lo in range(0, tmax, chunk):
        hi = min(lo + chunk, tmax)
        ts = np.arange(lo, hi, dtype=float)  # exponent t-1
        mag = np.exp(np.outer(ts, loga))
        sgn = np.where((ts[:, None].astype(int) % 2 == 0), 1.0, sign[None, :])
        # sign^{t-1}: even exponent -> +1, odd -> sign
        out[lo:hi] = (mag * sgn) @ kap
    return out


def tmax_for(lams: np.ndarray) -> int:
    s1 = float(np.max(lams))
    if s1 >= 1.0:
        return TMAX_CAP
    t = int(min(TMAX_CAP, max(2_000, 40.0 / (1.0 - s1))))
    # loud guard: the evaluated window must comfortably contain the slow-mode
    # hump t* = -1/ln(s1), otherwise the classifier would silently truncate
    # the second peak (spurious single_peak at very large N / small beta).
    tstar = -1.0 / math.log(s1)
    if t < 4.0 * tstar:
        raise RuntimeError(
            f"t-window too short: tmax={t} < 4*t*={4*tstar:.0f} "
            f"(s1={s1!r}); raise TMAX_CAP or reduce N/beta range")
    return t


# ----------------------------------------------------------------------
# Chebyshev closed form (cross-check)
# ----------------------------------------------------------------------

def chebyshev_modes(N: int, q: float, beta: float, rho: int):
    """(s_j, B_rho_j) from the closed form, via numpy polynomial tooling."""
    L = N // 2
    a = q / (beta * (1.0 - q))
    cheb = np.polynomial.chebyshev
    TL = np.zeros(L + 1); TL[L] = 1.0
    UL1 = np.zeros(L); UL1[L - 1] = 1.0
    # U_n in T-basis: U_n = 2*sum_{k odd parity} T_k ... use chebu via chebmul?
    # numpy has no U directly; build from recurrence in T-basis.
    def U_in_T(n: int) -> np.ndarray:
        if n < 0:
            return np.zeros(1)
        # U_n(x) coefficients in Chebyshev T basis via recurrence U_n = 2x U_{n-1} - U_{n-2}
        prev = np.array([1.0])               # U_0
        if n == 0:
            return prev
        cur = np.array([0.0, 2.0])           # U_1 = 2x -> in T basis: 2*T_1
        for _ in range(2, n + 1):
            nxt = 2.0 * cheb.chebmulx(cur)
            m = max(len(nxt), len(prev))
            nxt = np.pad(nxt, (0, m - len(nxt)))
            nxt[: len(prev)] -= prev
            prev, cur = cur, nxt
        return cur

    D = a * np.pad(np.eye(1, L + 1, L).ravel(), (0, 0)) + np.pad(U_in_T(L - 1), (0, L + 1 - L))
    ys = cheb.chebroots(D)
    ys = np.sort(np.real(ys[np.abs(np.imag(ys)) < 1e-9]))[::-1]
    Dprime = cheb.chebder(D)
    num = (a * np.pad(U_in_T(0) * 0 + 0, (0, 0)))  # placeholder, built below
    TLr = np.zeros(L - rho + 1); TLr[L - rho] = 1.0
    Ur1 = U_in_T(rho - 1)
    ULr1 = U_in_T(L - rho - 1)
    m = L + 1
    numc = np.zeros(m)
    numc[: len(TLr)] += a * TLr
    numc[: len(Ur1)] += Ur1
    numc[: len(ULr1)] += ULr1
    s = 1.0 - q + q * ys
    B = q * cheb.chebval(ys, numc) / cheb.chebval(ys, Dprime)
    return s, B


# ----------------------------------------------------------------------
# classifier (C.2 verbatim) and features
# ----------------------------------------------------------------------

def detect_peaks(x: np.ndarray, h_min: float = H_MIN) -> np.ndarray:
    """Strict local maxima of F(t); t=1 is a peak candidate via F(0)=0."""
    xp = np.concatenate(([0.0], x))
    left = xp[1:-1] > xp[:-2]
    right = xp[1:-1] > xp[2:]
    mask = left & right & (xp[1:-1] >= h_min)
    return np.where(mask)[0]


@dataclass
class Features:
    n_peaks: int
    clear_double: bool           # C.2 five-condition rule (this report's anchor)
    paper_bimodal: bool          # vkcore paper_style_bimodality (h_min=1e-12, 1%)
    macro_bimodal: bool          # jumpover convention: + t2/t1 >= 10 (h_min=1e-7)
    label: str                   # repo vocabulary: double_peak|shoulder|local_bump|single_peak
    t1: int | None
    h1: float | None
    t2: int | None
    h2: float | None
    t_valley: int | None
    h_valley: float | None
    ratio_secondary: float       # secondary/largest peak height
    hratio: float                # h2/h1 (later/earlier)
    valley_frac: float           # valley / min(h1,h2)
    t_ratio: float               # t2/t1 timescale separation
    s1: float
    B1: float
    tail_tstar: float            # -1/ln(s1), exact hump-time scale
    capture_prob: float          # absorbed-via-shortcut mass
    survival_left: float


def classify(F: np.ndarray, spec: Spectral) -> Features:
    peaks = detect_peaks(F)
    s1 = float(np.max(spec.lams))
    B1 = float(spec.kappas[int(np.argmax(spec.lams))])
    lam = beta_lam(spec)
    cap = float(lam * np.sum(spec.occup_u / (1.0 - spec.lams)))
    surv = float(max(0.0, 1.0 - F.sum()))
    base = dict(s1=s1, B1=B1, tail_tstar=-1.0 / math.log(s1),
                capture_prob=cap, survival_left=surv)
    # vkcore canonical classifier (core repo definition)
    pb_vk = bool(paper_style_bimodality(F).is_bimodal) if paper_style_bimodality else False
    # jumpover-pipeline macro_bimodal: peaks above h_min=1e-7 filtered at 1%
    # of the max, then top-2 by height in time order must have t2/t1 >= 10.
    pk7 = detect_peaks(F, h_min=1e-7)
    macro = False
    if pk7.size >= 2:
        keep = pk7[F[pk7] >= 0.01 * float(F[pk7].max())]
        if keep.size >= 2:
            top2 = keep[np.argsort(F[keep])[::-1][:2]]
            ta, tb = sorted(int(x) + 1 for x in top2)
            macro = (tb / ta) >= 10.0
    if peaks.size < 2:
        t1 = int(peaks[0]) + 1 if peaks.size else None
        h1 = float(F[peaks[0]]) if peaks.size else None
        return Features(int(peaks.size), False, pb_vk, macro, "single_peak",
                        t1, h1, None, None, None, None,
                        0.0, 0.0, 0.0, 0.0, **base)
    # C.2 rule: the tested pair is the FIRST TWO local peaks in time order
    # ("their first two peaks are only two time steps apart ... fail the
    # separation criterion"); the 1% condition compares the second peak of
    # the pair against the LARGEST peak anywhere.
    pa, pb = int(peaks[0]), int(peaks[1])
    h_max = float(F[peaks].max())
    ratio = float(F[pb] / max(h_max, 1e-300))
    lo, hi = sorted((pa, pb))
    valley = int(lo + np.argmin(F[lo:hi + 1]))
    h_early, h_late = float(F[lo]), float(F[hi])
    hratio = h_late / max(h_early, 1e-300)
    vfrac = float(F[valley] / max(min(h_early, h_late), 1e-300))
    t_ratio = float((hi + 1) / (lo + 1))
    clear = (ratio >= MIN_RATIO and (hi - lo) >= MIN_SEP
             and HRATIO_LO <= hratio <= HRATIO_HI and vfrac <= VALLEY_FRAC)
    # repo vocabulary (research-conventions.md): double_peak only via the
    # declared classifier; weaker visible structure -> shoulder (no real dip)
    # or local_bump (dip present but secondary too small / ratio out of range)
    if clear:
        label = "double_peak"
    elif vfrac > VALLEY_FRAC:
        label = "shoulder"
    else:
        label = "local_bump"
    return Features(int(peaks.size), bool(clear), pb_vk, macro, label,
                    lo + 1, h_early, hi + 1,
                    h_late, valley + 1, float(F[valley]), ratio, hratio,
                    vfrac, t_ratio, **base)


def beta_lam(spec: Spectral) -> float:
    return spec.beta * (1.0 - spec.q)


def evaluate(N: int, q: float, beta: float, n0: int):
    spec = spectral(N, q, beta, n0)
    tmax = tmax_for(spec.lams)
    F = pmf_from_modes(spec.lams, spec.kappas, tmax)
    # truncate where survival < eps to mirror C.2
    csum = np.cumsum(F)
    idx = np.searchsorted(csum, 1.0 - SURVIVAL_EPS)
    if idx + 1 < tmax:
        F = F[: idx + 1]
    return spec, F, classify(F, spec)


# ----------------------------------------------------------------------
# attribution metrics
# ----------------------------------------------------------------------

def n_needed(F: np.ndarray, spec: Spectral, times: list[int], tol: float = 0.01):
    """Modes (in |kappa|*lam-ordering at each time? use fixed descending-lam
    order) needed for tol relative accuracy at the given times."""
    out = {}
    order = np.argsort(spec.lams)[::-1]
    lam = spec.lams[order]
    kap = spec.kappas[order]
    for t in times:
        if t < 1 or t > len(F):
            out[t] = None
            continue
        target = F[t - 1]
        acc = 0.0
        n = None
        for k in range(len(lam)):
            acc += kap[k] * lam[k] ** (t - 1)
            if abs(acc - target) <= tol * abs(target):
                n = k + 1
                break
        out[t] = n
    return out


def leave_one_out(F: np.ndarray, spec: Spectral, feats: Features, top: int = 12):
    """Feature deltas when deleting one mode (descending-lam order)."""
    order = np.argsort(spec.lams)[::-1]
    res = []
    base = (feats.h1 or 0.0, feats.h_valley or 0.0, feats.h2 or 0.0)
    tmax = len(F)
    for rank in range(min(top, len(order))):
        i = order[rank]
        kap2 = spec.kappas.copy()
        kap2[i] = 0.0
        F2 = pmf_from_modes(spec.lams, kap2, tmax)
        d1 = (F2[feats.t1 - 1] - base[0]) if feats.t1 else float("nan")
        dv = (F2[feats.t_valley - 1] - base[1]) if feats.t_valley else float("nan")
        d2 = (F2[feats.t2 - 1] - base[2]) if feats.t2 else float("nan")
        res.append(dict(rank=rank + 1, lam=float(spec.lams[i]),
                        kappa=float(spec.kappas[i]),
                        d_peak1=float(d1), d_valley=float(dv), d_peak2=float(d2)))
    return res


# ----------------------------------------------------------------------
# validation suite
# ----------------------------------------------------------------------

def validate_c2(out_dir: Path):
    """Reproduce the C.2 sampled-beta-bounds table (N=100, q=2/3)."""
    N, q = 100, Q_DEFAULT
    betas = sorted(set([round(0.002 * k, 3) for k in range(0, 41)] + [0.001, 0.005]))
    rows = []
    for n0_paper in range(1, 7):
        d = 6 - n0_paper            # distance from shortcut source u
        n0 = (N // 2 + d) % N       # 0-indexed frame: v=0, u=N/2
        clear_flags = []
        for beta in betas:
            if beta == 0.0:
                clear_flags.append((beta, False))
                continue
            _, F, feats = evaluate(N, q, beta, n0)
            clear_flags.append((beta, feats.clear_double))
        clears = [b for b, c in clear_flags if c]
        first_clear = min(clears) if clears else None
        last_clear = max(clears) if clears else None
        before = max([b for b, c in clear_flags if not c and first_clear is not None and b < first_clear], default=None)
        after = min([b for b, c in clear_flags if not c and last_clear is not None and b > last_clear], default=None)
        rows.append(dict(n0_paper=n0_paper, d=d,
                         no_before=before, first_clear=first_clear,
                         last_clear=last_clear, no_after=after))
        print(f"n0={n0_paper} (d={d}): no_before={before} first={first_clear} "
              f"last={last_clear} no_after={after}")
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "dpma_c2_reproduction.json").write_text(json.dumps(rows, indent=2))
    expected = {1: (0.001, 0.002, 0.030, 0.032), 2: (0.001, 0.002, 0.030, 0.032),
                3: (0.000, 0.001, 0.030, 0.032), 4: (None, None, None, None),
                5: (None, None, None, None), 6: (None, None, None, None)}
    ok = True
    for r in rows:
        exp = expected[r["n0_paper"]]
        got = (r["no_before"], r["first_clear"], r["last_clear"], r["no_after"])
        match = all((a is None and b is None) or (a is not None and b is not None and abs(a - b) < 1e-12)
                    for a, b in zip(exp, got))
        if not match:
            ok = False
            print(f"  MISMATCH n0={r['n0_paper']}: expected {exp} got {got}")
    print("C.2 table reproduction:", "PASS" if ok else "FAIL")
    return ok


def validate_basics():
    """Mass balance, nonnegativity, eigh-vs-Chebyshev closed form."""
    cases = [(100, 0.01, 55), (100, 0.002, 54), (10, 4.0 / 7.0, 2), (12, 0.3, 7)]
    ok = True
    for N, beta, n0 in cases:
        q = Q_DEFAULT if N != 10 and N != 12 else (2.0 / 3.0 if N == 10 else 0.5)
        spec, F, feats = evaluate(N, q, beta, n0)
        neg = float(F.min())
        mass = float(F.sum() + feats.survival_left)
        rho = min(n0 % N, N - (n0 % N))
        s_cf, B_cf = chebyshev_modes(N, q, beta, rho)
        L = N // 2
        top = np.sort(spec.lams)[::-1][:L]
        # the L Chebyshev modes interlace with gamma modes; compare the sets
        s_match = np.max(np.abs(np.sort(s_cf) - np.sort(
            np.array([l for l in spec.lams if min(abs(np.sort(s_cf) - l)) < 1e-8]))[: len(s_cf)])) if len(s_cf) else 0.0
        kap_by_lam = {}
        for l, k in zip(spec.lams, spec.kappas):
            kap_by_lam[round(float(l), 10)] = kap_by_lam.get(round(float(l), 10), 0.0) + float(k)
        B_err = 0.0
        for s_val, B_val in zip(s_cf, B_cf):
            close = min(kap_by_lam, key=lambda L_: abs(L_ - s_val))
            B_err = max(B_err, abs(kap_by_lam[close] - B_val))
        print(f"N={N} beta={beta} n0={n0}: min F={neg:.1e}, mass={mass:.12f}, "
              f"max|B_eigh-B_cheb|={B_err:.2e}")
        ok = ok and neg > -1e-12 and abs(mass - 1.0) < 1e-9 and B_err < 1e-8
    print("basic validation:", "PASS" if ok else "FAIL")
    return ok


# ----------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("validate")
    p = sub.add_parser("case")
    p.add_argument("--N", type=int, default=100)
    p.add_argument("--q", type=float, default=Q_DEFAULT)
    p.add_argument("--beta", type=float, required=True)
    p.add_argument("--d", type=int, default=4, help="start distance from u")
    args = ap.parse_args()
    art = Path(__file__).resolve().parents[1] / "artifacts" / "outputs"
    if args.cmd == "validate":
        ok1 = validate_basics()
        ok2 = validate_c2(art)
        raise SystemExit(0 if (ok1 and ok2) else 1)
    if args.cmd == "case":
        n0 = (args.N // 2 + args.d) % args.N
        spec, F, feats = evaluate(args.N, args.q, args.beta, n0)
        print(json.dumps(asdict(feats), indent=2, default=float))


if __name__ == "__main__":
    main()
