#!/usr/bin/env python3
"""High-precision audit of the t*alpha^t ("log correction") dispute.

Model: lazy ring of N sites (stay 1-q, hop q/2 each way), absorbing target
v=0, antipodal shortcut source u=N/2.  The shortcut moves lambda=beta(1-q)
from the u->u self-loop to the directed edge u->v.  Start site n0=rho.

Claim A (Luca, 2026-06-09): the long-time PMF carries a t*alpha_1^t factor
("log correction"); its coefficient vanishes only by miracle.
Claim B (corrected notes): F(t) = sum_j B_j s_j^{t-1} exactly (t>=1), where
s_j=1-q+q*y_j and D(y_j)=0 with D(y)=a*T_L(y)+U_{L-1}(y), a=q/(beta(1-q));
no alpha modes and no secular terms survive.

All computations in mpmath with mp.dps=50.
"""

import json
import os

from mpmath import mp, mpf, cos, pi, sin, chebyt, chebyu, diff, findroot, fabs, mpmathify

mp.dps = 50

REPORT = []


def say(line=""):
    print(line)
    REPORT.append(line)


def cheb_T(n, x):
    return chebyt(n, x)


def cheb_U(n, x):
    if n < 0:
        return mp.zero
    return chebyu(n, x)


# ----------------------------------------------------------------------
# model pieces
# ----------------------------------------------------------------------

def build_model(N, q, beta, rho):
    q, beta = mpmathify(q), mpmathify(beta)
    L = N // 2
    m = dict(N=N, L=L, q=q, beta=beta, rho=rho, v=0, u=L, n0=rho)
    m["lam"] = beta * (1 - q)
    m["a"] = q / m["lam"]
    m["h0"] = 1 / m["a"]
    m["alpha"] = [1 - q + q * cos((2 * l - 1) * pi / N) for l in range(1, L + 1)]
    m["gamma"] = [1 - q + q * cos(2 * pi * r / N) for r in range(1, L)]
    return m


def transition_matrix(m, with_shortcut=True):
    N, q = m["N"], m["q"]
    T = [[mp.zero] * N for _ in range(N)]
    for i in range(N):
        T[i][i] += 1 - q
        T[i][(i + 1) % N] += q / 2
        T[i][(i - 1) % N] += q / 2
    if with_shortcut:
        T[m["u"]][m["u"]] -= m["lam"]
        T[m["u"]][m["v"]] += m["lam"]
    return T


def transient_block(m, with_shortcut=True):
    T = transition_matrix(m, with_shortcut)
    idx = [i for i in range(m["N"]) if i != m["v"]]
    A = [[T[i][j] for j in idx] for i in idx]
    b = [T[i][m["v"]] for i in idx]
    return A, b, idx


def exact_F(m, tmax, with_shortcut=True):
    """F(t) for t=0..tmax from the finite matrix."""
    A, b, idx = transient_block(m, with_shortcut)
    n = len(idx)
    pos = {s: k for k, s in enumerate(idx)}
    p = [mp.zero] * n
    p[pos[m["n0"]]] = mp.one
    out = [mp.zero]
    for _ in range(tmax):
        out.append(sum(p[k] * b[k] for k in range(n)))
        p = [sum(p[k] * A[k][j] for k in range(n)) for j in range(n)]
    return out


def occupation_u(m, tmax):
    """(W_{n0}(u,t), W_u(u,t)) for t=0..tmax, beta=0 chain killed at v."""
    A, b, idx = transient_block(m, with_shortcut=False)
    n = len(idx)
    pos = {s: k for k, s in enumerate(idx)}
    res = {}
    for start in sorted({m["n0"], m["u"]}):
        p = [mp.zero] * n
        p[pos[start]] = mp.one
        seq = []
        for _ in range(tmax + 1):
            seq.append(p[pos[m["u"]]])
            p = [sum(p[k] * A[k][j] for k in range(n)) for j in range(n)]
        res[start] = seq
    return res[m["n0"]], res[m["u"]]


def F0_series(m, tmax, n0=None, target=None):
    """No-shortcut first-passage PMF to v from n0, t=0..tmax (exact chain)."""
    n0 = m["n0"] if n0 is None else n0
    A, b, idx = transient_block(m, with_shortcut=False)
    n = len(idx)
    pos = {s: k for k, s in enumerate(idx)}
    p = [mp.zero] * n
    p[pos[n0]] = mp.one
    out = [mp.zero]
    for _ in range(tmax):
        out.append(sum(p[k] * b[k] for k in range(n)))
        p = [sum(p[k] * A[k][j] for k in range(n)) for j in range(n)]
    return out


# ----------------------------------------------------------------------
# closed form: D roots, residues
# ----------------------------------------------------------------------

def D_func(m):
    a, L = m["a"], m["L"]
    return lambda y: a * cheb_T(L, y) + cheb_U(L - 1, y)


def N_rho_func(m, rho=None):
    a, L = m["a"], m["L"]
    rho = m["rho"] if rho is None else rho
    return lambda y: a * cheb_T(L - rho, y) + cheb_U(rho - 1, y) + cheb_U(L - rho - 1, y)


def D_roots(m):
    L = m["L"]
    D = D_func(m)
    eta = [cos((2 * l - 1) * pi / (2 * L)) for l in range(1, L + 1)]  # T_L zeros, descending
    brackets = [(eta[l + 1], eta[l]) for l in range(L - 1)]
    lo = eta[-1] - mpf(1) / 100
    while D(lo) * D(eta[-1] - mpf(10) ** (-30)) > 0:
        lo -= mpf(1) / 20
        if lo < -1 - 5 / m["q"]:
            raise RuntimeError("no bracket for lowest root")
    brackets.append((lo, eta[-1]))
    ys = []
    for (ya, yb) in brackets:
        ya2, yb2 = ya + mpf(10) ** (-35), yb - mpf(10) ** (-35)
        fa, fb = D(ya2), D(yb2)
        if fa * fb > 0:
            raise RuntimeError("bracket failure")
        # robust bisection to ~1e-46, then one Newton polish
        for _ in range(180):
            ym = (ya2 + yb2) / 2
            fm = D(ym)
            if fm == 0:
                break
            if fa * fm < 0:
                yb2, fb = ym, fm
            else:
                ya2, fa = ym, fm
        ym = (ya2 + yb2) / 2
        try:
            ym = findroot(D, ym, tol=mpf(10) ** (-45))
        except Exception:
            pass
        ys.append(ym)
    ys.sort(reverse=True)
    return ys


def residues(m, ys):
    D = D_func(m)
    Nr = N_rho_func(m)
    q = m["q"]
    cs, Bs, ss = [], [], []
    for y in ys:
        dD = diff(D, y)
        cs.append(q * cheb_T(m["L"], y) / dD)
        Bs.append(q * Nr(y) / dD)
        ss.append(1 - q + q * y)
    return cs, Bs, ss


# ----------------------------------------------------------------------
# modal coefficients
# ----------------------------------------------------------------------

def f_modes(m, n0, target):
    d = abs(target - n0)
    N, q, L = m["N"], m["q"], m["L"]
    return [(2 * q / N) * sin(d * pi * (2 * l - 1) / N) * sin(pi * (2 * l - 1) / N)
            for l in range(1, L + 1)]


def g2_modes(m, n0):
    """g^{(2)}_l(n0,u,v): residue coefficients of W_{n0}(u,t) alpha-modes."""
    N, L = m["N"], m["L"]
    d0, du = abs(n0 - m["v"]), abs(m["u"] - m["v"])
    return [(mpf(2) / N) * sin(pi * (2 * l - 1) * d0 / N) * sin(pi * (2 * l - 1) * du / N)
            for l in range(1, L + 1)]


def G1_modes(m, n0):
    """G^{(1)}_r(n0,u,v), r=1..N-1 (vanishes identically when u,v antipodal)."""
    N, u, v = m["N"], m["u"], m["v"]
    return [(cos(2 * pi * r * (u - n0) / N)
             - cos(2 * pi * r * (u - v) / N) * cos(2 * pi * r * (n0 - v) / N)) / N
            for r in range(1, N)]


# ----------------------------------------------------------------------
# convolution routes
# ----------------------------------------------------------------------

def conv(x, y, tmax):
    """(x*y)(t) for t=0..tmax."""
    out = []
    for t in range(tmax + 1):
        out.append(sum(x[s] * y[t - s] for s in range(t + 1)))
    return out


def H_series_recursion(m, Wuu, tmax):
    """H(t) from (1 + z lam Wuu~) H~ = h0, i.e. exact renewal recursion."""
    lam, h0 = m["lam"], m["h0"]
    H = [h0]
    for t in range(1, tmax + 1):
        H.append(-lam * sum(Wuu[s] * H[t - 1 - s] for s in range(t)))
    return H


def route_convolution(m, W, F0u, H, tmax):
    """F(t) = F0_{n0}(t) + q * [W*(delta-F0u)*H](t-1)  for t>=1."""
    q = m["q"]
    F0n0 = None  # filled by caller
    raise NotImplementedError


def five_group_F(m, cs, ss, tmax):
    """Literal evaluation of the corrected five-group expansion (Eq. 57)."""
    q, h0, L = m["q"], m["h0"], m["L"]
    alpha, gamma = m["alpha"], m["gamma"]
    f_n0v = f_modes(m, m["n0"], m["v"])
    f_uv = f_modes(m, m["u"], m["v"])
    g2 = g2_modes(m, m["n0"])
    G1 = G1_modes(m, m["n0"])
    gam_full = [1 - m["q"] + m["q"] * cos(2 * pi * r / m["N"]) for r in range(1, m["N"])]

    out = [mp.zero] * (tmax + 1)
    for t in range(1, tmax + 1):
        # group 1: baseline (target v)
        g1v = sum(f_n0v[l] * alpha[l] ** (t - 1) for l in range(L))
        # group 2: q h0 W(t-1)
        g2v = q * h0 * (sum(G1[r] * gam_full[r] ** (t - 1) for r in range(len(gam_full)))
                        + sum(g2[l] * alpha[l] ** (t - 1) for l in range(L)))
        # group 3: q sum_j c_j [W-modes vs s_j difference quotients]
        g3v = mp.zero
        for j, (c, s) in enumerate(zip(cs, ss)):
            acc = sum(G1[r] * (s ** (t - 1) - gam_full[r] ** (t - 1)) / (s - gam_full[r])
                      for r in range(len(gam_full)))
            acc += sum(g2[l] * (s ** (t - 1) - alpha[l] ** (t - 1)) / (s - alpha[l])
                       for l in range(L))
            g3v += q * c * acc
        # group 4: -q h0 sum_l f_uv[l] [two-mode quotients + diagonal]
        g4v = mp.zero
        for l in range(L):
            acc = sum(G1[r] * (gam_full[r] ** (t - 1) - alpha[l] ** (t - 1)) / (gam_full[r] - alpha[l])
                      for r in range(len(gam_full)))
            acc += sum(g2[r] * (alpha[r] ** (t - 1) - alpha[l] ** (t - 1)) / (alpha[r] - alpha[l])
                       for r in range(L) if r != l)
            acc += g2[l] * (t - 1) * alpha[l] ** (t - 2)
            g4v += -q * h0 * f_uv[l] * acc
        # group 5: -q sum_j c_j sum_l f_uv[l] [three-mode partial fractions]
        g5v = mp.zero
        for j, (c, s) in enumerate(zip(cs, ss)):
            for l in range(L):
                al = alpha[l]
                acc = mp.zero
                for r in range(len(gam_full)):
                    gr = gam_full[r]
                    acc += G1[r] * (gr ** (t - 1) / ((gr - al) * (gr - s))
                                    + al ** (t - 1) / ((al - gr) * (al - s))
                                    + s ** (t - 1) / ((s - gr) * (s - al)))
                for r in range(L):
                    if r == l:
                        continue
                    ar = alpha[r]
                    acc += g2[r] * (ar ** (t - 1) / ((ar - al) * (ar - s))
                                    + al ** (t - 1) / ((al - ar) * (al - s))
                                    + s ** (t - 1) / ((s - ar) * (s - al)))
                acc += g2[l] * ((s ** (t - 1) - al ** (t - 1)) / (s - al) ** 2
                                - (t - 1) * al ** (t - 2) / (s - al))
                g5v += -q * c * f_uv[l] * acc
        out[t] = g1v + g2v + g3v + g4v + g5v
    return out


def folded_F(m, cs, ss, tmax):
    """Same route but with H(0) folded into the pole expansion, i.e. the
    old Eq.(41)-style kernels (s^t - x^t)/(s(s-x)) and their three-mode
    analogues.  Algebraically equivalent to replacing the true H(0)=h0 by
    sum_j c_j/s_j inside the convolution."""
    q, L = m["q"], m["L"]
    alpha = m["alpha"]
    f_n0v = f_modes(m, m["n0"], m["v"])
    f_uv = f_modes(m, m["u"], m["v"])
    g2 = g2_modes(m, m["n0"])
    G1 = G1_modes(m, m["n0"])
    gam_full = [1 - m["q"] + m["q"] * cos(2 * pi * r / m["N"]) for r in range(1, m["N"])]

    h0_fold = sum(c / s for c, s in zip(cs, ss))  # replaces true h0

    out = [mp.zero] * (tmax + 1)
    for t in range(1, tmax + 1):
        g1v = sum(f_n0v[l] * alpha[l] ** (t - 1) for l in range(L))
        g2v = q * h0_fold * (sum(G1[r] * gam_full[r] ** (t - 1) for r in range(len(gam_full)))
                             + sum(g2[l] * alpha[l] ** (t - 1) for l in range(L)))
        g3v = mp.zero
        for c, s in zip(cs, ss):
            acc = sum(G1[r] * (s ** (t - 1) - gam_full[r] ** (t - 1)) / (s - gam_full[r])
                      for r in range(len(gam_full)))
            acc += sum(g2[l] * (s ** (t - 1) - alpha[l] ** (t - 1)) / (s - alpha[l])
                       for l in range(L))
            g3v += q * c * acc
        g4v = mp.zero
        for l in range(L):
            acc = sum(G1[r] * (gam_full[r] ** (t - 1) - alpha[l] ** (t - 1)) / (gam_full[r] - alpha[l])
                      for r in range(len(gam_full)))
            acc += sum(g2[r] * (alpha[r] ** (t - 1) - alpha[l] ** (t - 1)) / (alpha[r] - alpha[l])
                       for r in range(L) if r != l)
            acc += g2[l] * (t - 1) * alpha[l] ** (t - 2)
            g4v += -q * h0_fold * f_uv[l] * acc
        g5v = mp.zero
        for c, s in zip(cs, ss):
            for l in range(L):
                al = alpha[l]
                acc = mp.zero
                for r in range(len(gam_full)):
                    gr = gam_full[r]
                    acc += G1[r] * (gr ** (t - 1) / ((gr - al) * (gr - s))
                                    + al ** (t - 1) / ((al - gr) * (al - s))
                                    + s ** (t - 1) / ((s - gr) * (s - al)))
                for r in range(L):
                    if r == l:
                        continue
                    ar = alpha[r]
                    acc += g2[r] * (ar ** (t - 1) / ((ar - al) * (ar - s))
                                    + al ** (t - 1) / ((al - ar) * (al - s))
                                    + s ** (t - 1) / ((s - ar) * (s - al)))
                acc += g2[l] * ((s ** (t - 1) - al ** (t - 1)) / (s - al) ** 2
                                - (t - 1) * al ** (t - 2) / (s - al))
                g5v += -q * c * f_uv[l] * acc
        out[t] = g1v + g2v + g3v + g4v + g5v
    return out


def luca_printed_F(m, cs, ss, tmax):
    """Luca's updated-document Eq. (41)-style formula, transcribed literally:

    F(t) = sum_l f_l(n0,u) alpha_l^{t-1}
         - q sum_k { sum_r c_k G1_r /(s_k(s_k-gamma_r)) (s_k^t-gamma_r^t)
                   + sum_l c_k g2_l /(s_k(s_k-alpha_l)) (s_k^t-alpha_l^t) }
         + q sum_k sum_r sum_l c_k G1_r f_l(u,v)/(s_k-alpha_l)
              [ (s_k^t-gamma_r^t)/(alpha_l(s_k-gamma_r))
              - (alpha_l^t-gamma_r^t)/(s_k(alpha_l-gamma_r)) ]
         - q sum_k sum_l c_k g2_l f_l(u,v)/(s_k alpha_l (s_k-alpha_l)) alpha_l^t t
         + q sum_k sum_{r!=l} c_k g2_r f_l(u,v)/(s_k alpha_l (s_k-alpha_l))
              [ s_k (s_k^t-gamma_r^t)/(s_k-gamma_r)
              - alpha_l (alpha_l^t-gamma_r^t)/(alpha_l-gamma_r) ]
    """
    q, L = m["q"], m["L"]
    alpha = m["alpha"]
    f_n0u = f_modes(m, m["n0"], m["u"])
    f_uv = f_modes(m, m["u"], m["v"])
    g2 = g2_modes(m, m["n0"])
    G1 = G1_modes(m, m["n0"])
    gam_full = [1 - m["q"] + m["q"] * cos(2 * pi * r / m["N"]) for r in range(1, m["N"])]

    out = [mp.zero] * (tmax + 1)
    for t in range(1, tmax + 1):
        v1 = sum(f_n0u[l] * alpha[l] ** (t - 1) for l in range(L))
        v2 = mp.zero
        for c, s in zip(cs, ss):
            v2 += sum(c * G1[r] / (s * (s - gam_full[r])) * (s ** t - gam_full[r] ** t)
                      for r in range(len(gam_full)))
            v2 += sum(c * g2[l] / (s * (s - alpha[l])) * (s ** t - alpha[l] ** t)
                      for l in range(L))
        v3 = mp.zero
        for c, s in zip(cs, ss):
            for r in range(len(gam_full)):
                gr = gam_full[r]
                for l in range(L):
                    al = alpha[l]
                    v3 += (c * G1[r] * f_uv[l] / (s - al)
                           * ((s ** t - gr ** t) / (al * (s - gr))
                              - (al ** t - gr ** t) / (s * (al - gr))))
        v4 = mp.zero
        for c, s in zip(cs, ss):
            for l in range(L):
                al = alpha[l]
                v4 += c * g2[l] * f_uv[l] / (s * al * (s - al)) * al ** t * t
        v5 = mp.zero
        for c, s in zip(cs, ss):
            for r in range(L):
                if r >= len(gam_full):
                    continue  # gamma_r pairing as printed; r runs with g2 index
                gr = gam_full[r]
                for l in range(L):
                    if l == r:
                        continue
                    al = alpha[l]
                    v5 += (c * g2[r] * f_uv[l] / (s * al * (s - al))
                           * (s * (s ** t - gr ** t) / (s - gr)
                              - al * (al ** t - gr ** t) / (al - gr)))
        out[t] = v1 - q * v2 + q * v3 - q * v4 + q * v5
    return out


# ----------------------------------------------------------------------
# main audit
# ----------------------------------------------------------------------

def audit_case(N, q, beta, rho, tmax=600, tprobe=(50, 150, 300, 600)):
    m = build_model(N, q, beta, rho)
    L = m["L"]
    say("=" * 78)
    say(f"CASE N={N}, q={q}, beta={beta}, rho={rho}  (v=0, u={m['u']}, n0={m['n0']})")
    say("=" * 78)

    # exact PMF
    Fex = exact_F(m, tmax)

    # closed form
    ys = D_roots(m)
    cs, Bs, ss = residues(m, ys)
    alpha, gamma = m["alpha"], m["gamma"]
    say(f"[roots] L={L} real roots of D(y) found; s_1={mp.nstr(ss[0], 20)}")
    say(f"        alpha_1={mp.nstr(alpha[0], 20)}  gamma_1={mp.nstr(gamma[0], 20) if gamma else 'n/a'}")

    # CHECK 1: closed form vs exact
    err1 = max(fabs(Fex[t] - sum(B * s ** (t - 1) for B, s in zip(Bs, ss)))
               for t in range(1, tmax + 1))
    say(f"[1] closed form F(t)=sum_j B_j s_j^(t-1) vs exact matrix:  max|diff| = {mp.nstr(err1, 3)}")

    # CHECK 2: spectrum of transient block
    import numpy as np
    A, b, idx = transient_block(m)
    Anp = np.array([[float(x) for x in row] for row in A])
    sym_err = float(np.abs(Anp - Anp.T).max())
    evals = np.linalg.eigvalsh(Anp)
    target = sorted([float(x) for x in ss] + [float(x) for x in gamma])
    spec_err = max(abs(a - b2) for a, b2 in zip(sorted(evals), target))
    min_alpha_dist = min(min(abs(float(al) - e) for e in evals) for al in alpha)
    say(f"[2] transient matrix symmetric (max asym {sym_err:.1e}); "
        f"spec == {{gamma_r}} U {{s_j}} (max err {spec_err:.2e}); "
        f"min_l dist(alpha_l, spec) = {min_alpha_dist:.6f}  (>0)")

    # CHECK 3: sum rule
    sr = [fabs(sum(c / (s - al) for c, s in zip(cs, ss)) - m["h0"]) for al in alpha]
    say(f"[3] sum rule  sum_j c_j/(s_j-alpha_l) = h0 :  max_l |dev| = {mp.nstr(max(sr), 3)}")

    # CHECK 4: H recursion vs pole expansion; c_inf
    Wn0u, Wuu = occupation_u(m, tmax)
    H = H_series_recursion(m, Wuu, min(tmax, 250))
    errH = max(fabs(H[t] - sum(c * s ** (t - 1) for c, s in zip(cs, ss)))
               for t in range(1, len(H)))
    y_inf = 1 - 1 / m["q"]
    c_inf_formula = cheb_T(L, y_inf) / D_func(m)(y_inf)
    c_inf_sum = m["h0"] - sum(c / s for c, s in zip(cs, ss))
    say(f"[4] H(t) recursion vs sum_j c_j s_j^(t-1) (t>=1): max|diff| = {mp.nstr(errH, 3)}")
    say(f"    H(0)=h0={mp.nstr(m['h0'], 12)};  sum_j c_j/s_j = {mp.nstr(sum(c / s for c, s in zip(cs, ss)), 12)}")
    say(f"    c_inf = h0 - sum_j c_j/s_j = {mp.nstr(c_inf_sum, 12)}  vs  T_L(1-1/q)/D(1-1/q) = {mp.nstr(c_inf_formula, 12)}"
        f"   |diff| = {mp.nstr(fabs(c_inf_sum - c_inf_formula), 3)}")

    # CHECK 5: secular coefficients
    f_uv = f_modes(m, m["u"], m["v"])
    g2 = g2_modes(m, m["n0"])
    say("[5] coefficient of (t-1)*alpha_l^(t-2):")
    for l in range(L):
        exact_coef = m["q"] * f_uv[l] * g2[l] * (sum(c / (s - alpha[l]) for c, s in zip(cs, ss)) - m["h0"])
        folded_coef = m["q"] * f_uv[l] * g2[l] * (sum(c / (s - alpha[l]) for c, s in zip(cs, ss))
                                                  - sum(c / s for c, s in zip(cs, ss)))
        pred_folded = m["q"] * f_uv[l] * g2[l] * c_inf_formula
        say(f"    l={l + 1}: exact-H(0) treatment: {mp.nstr(exact_coef, 3)}   "
            f"folded: {mp.nstr(folded_coef, 8)} (= q f g c_inf? |diff|={mp.nstr(fabs(folded_coef - pred_folded), 3)})")

    # CHECK 6: five-group corrected route vs exact
    t6 = min(tmax, 200)
    F5 = five_group_F(m, cs, ss, t6)
    err6 = max(fabs(F5[t] - Fex[t]) for t in range(1, t6 + 1))
    say(f"[6] corrected five-group expansion vs exact (t<= {t6}): max|diff| = {mp.nstr(err6, 3)}")

    # CHECK 7: folded route vs exact -> spurious secular term
    Ffold = folded_F(m, cs, ss, t6)
    say("[7] folded (old-kernel) route minus exact, normalised by (t-1)alpha_1^(t-2):")
    pred = m["q"] * f_uv[0] * g2[0] * c_inf_formula
    for t in tprobe:
        if t > t6:
            continue
        dev = Ffold[t] - Fex[t]
        norm = dev / ((t - 1) * alpha[0] ** (t - 2))
        say(f"    t={t:4d}:  F_fold-F_exact = {mp.nstr(dev, 6)}   /( (t-1)a1^(t-2) ) = {mp.nstr(norm, 12)}")
    say(f"    predicted limit q*f_1(u,v)*g2_1*c_inf = {mp.nstr(pred, 12)}")

    # CHECK 8: Luca's printed formula vs exact
    FL = luca_printed_F(m, cs, ss, t6)
    err8_probe = [(t, FL[t] - Fex[t]) for t in tprobe if t <= t6]
    say("[8] Luca's printed Eq.(41)-style formula minus exact:")
    for t, d in err8_probe:
        say(f"    t={t:4d}:  diff = {mp.nstr(d, 6)}   (F_exact={mp.nstr(Fex[t], 6)})")

    # CHECK 10: tail ratios
    say("[10] tail diagnostics:")
    for t in tprobe:
        if t > tmax:
            continue
        r1 = Fex[t] / (Bs[0] * ss[0] ** (t - 1))
        r2 = Fex[t] / (t * alpha[0] ** t)
        say(f"    t={t:4d}:  F/(B_1 s_1^(t-1)) = {mp.nstr(r1, 12)}    F/(t alpha_1^t) = {mp.nstr(r2, 6)}")

    # CHECK 11: residue identity
    f_n0v = f_modes(m, m["n0"], m["v"])
    g2_uu = g2_modes(m, m["u"])
    f_n0u_g = g2_modes(m, m["n0"])
    err11 = max(fabs(f_n0v[l] * g2_uu[l] - f_n0u_g[l] * f_uv[l]) for l in range(L))
    say(f"[11] residue identity f_l(n0,v) g_l(u,u) = g_l(n0,u) f_l(u,v): max|dev| = {mp.nstr(err11, 3)}")

    # CHECK 12: complete plain-alpha cancellation (value rule + derivative rule)
    # derivative sum rule: sum_j c_j/(s_j-alpha_l)^2 = -L/q for every l (beta-independent)
    err12a = max(fabs(sum(c / (s - al) ** 2 for c, s in zip(cs, ss)) + mpf(L) / m["q"])
                 for al in alpha)
    # W-mode plain-alpha coefficient (groups 2+3): q h0 g_l - q g_l sum_j c_j/(s_j-alpha_l)
    err12b = max(fabs(m["q"] * m["h0"] * g2[l]
                      - m["q"] * g2[l] * sum(c / (s - alpha[l]) for c, s in zip(cs, ss)))
                 for l in range(L))
    # total plain alpha_l^{t-1} coefficient across all five groups:
    #   f_l(n0,v) + q f_l(u,v) g_l sum_j c_j/(s_j-alpha_l)^2   (off-diagonals cancel by value rule)
    err12c = max(fabs(f_n0v[l] + m["q"] * f_uv[l] * g2[l]
                      * sum(c / (s - alpha[l]) ** 2 for c, s in zip(cs, ss)))
                 for l in range(L))
    say(f"[12] derivative sum rule sum_j c_j/(s_j-alpha_l)^2 = -L/q: max|dev| = {mp.nstr(err12a, 3)}")
    say(f"     W-mode plain-alpha cancellation (groups 2+3): max|dev| = {mp.nstr(err12b, 3)}")
    say(f"     total plain alpha_l^(t-1) coefficient (all five groups): max|dev| = {mp.nstr(err12c, 3)}")

    say()
    return dict(err_closed=float(err1), spec_err=spec_err,
                min_alpha_dist=min_alpha_dist,
                sumrule=float(max(sr)), errH=float(errH),
                c_inf=float(c_inf_formula), err5group=float(err6))


def beta_sweep(N, q, betas):
    say("=" * 78)
    say(f"BETA SWEEP N={N}, q={q}: check gamma_1 < s_1 < alpha_1")
    say("=" * 78)
    ok = True
    worst = None
    for beta in betas:
        m = build_model(N, q, beta, 1)
        ys = D_roots(m)
        s1 = 1 - m["q"] + m["q"] * ys[0]
        g1, a1 = m["gamma"][0], m["alpha"][0]
        cond = g1 < s1 < a1
        ok = ok and cond
        margin = float(min(s1 - g1, a1 - s1))
        if worst is None or margin < worst[1]:
            worst = (beta, margin)
        if not cond:
            say(f"  VIOLATION at beta={beta}: gamma_1={mp.nstr(g1,12)} s_1={mp.nstr(s1,12)} alpha_1={mp.nstr(a1,12)}")
    say(f"  all {len(betas)} sampled beta in (0,1]: gamma_1 < s_1 < alpha_1 holds: {ok}")
    say(f"  smallest margin min(s1-gamma1, alpha1-s1) = {worst[1]:.3e} at beta={worst[0]}")
    say()
    return ok


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    results = {}

    # Luca's figure parameters
    results["N10"] = audit_case(10, "2/3", "4/7", rho=2, tmax=600)
    # a second geometry / parameters
    results["N12"] = audit_case(12, "1/2", "3/10", rho=5, tmax=400, tprobe=(50, 120, 250, 400))
    # small beta (double-peak regime)
    results["N10small"] = audit_case(10, "2/3", "1/50", rho=1, tmax=400, tprobe=(50, 120, 250, 400))

    betas = [mpf(b) / 1000 for b in [1, 2, 5, 10, 20, 40, 80, 160, 320, 500, 640, 800, 900, 990, 1000]]
    results["sweep_N10"] = beta_sweep(10, "2/3", betas)
    results["sweep_N100"] = beta_sweep(100, "2/3", betas)
    results["sweep_N12"] = beta_sweep(12, "1/2", betas)

    with open(os.path.join(here, "..", "secular_term_cancellation_results.json"), "w") as fh:
        json.dump({k: v for k, v in results.items() if not isinstance(v, dict)}, fh, indent=2, default=str)
    with open(os.path.join(here, "..", "secular_term_cancellation_report.txt"), "w") as fh:
        fh.write("\n".join(REPORT) + "\n")
    say("Report written to secular_term_cancellation_report.txt")


if __name__ == "__main__":
    main()
