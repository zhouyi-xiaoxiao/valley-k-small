#!/usr/bin/env python3
"""Independent audit: does the antipodal-shortcut first-passage tail carry t*alpha^t?

Self-contained re-derivation (no reuse of earlier audit code) for the lazy ring
walk (stay 1-q, hop q/2) with absorbing target v=0 and directed shortcut
u=L -> v of weight beta*(1-q) taken from the lazy self-loop, N=2L.

Checks
  A. exact PMF from the finite chain (rational arithmetic) vs the collected
     closed form  F~ = [a*T_{L-rho} + U_{rho-1} + U_{L-rho-1}] / [a*T_L + U_{L-1}]
  B. spectrum of the (symmetric) transient block = {roots of D} U {gamma_r};
     alpha_l is NOT an eigenvalue for beta>0; all eigenvalues simple
  C. tail: F(t+1)/F(t) -> s_1 (not alpha_1); F(t)/(t*alpha_1^t) -> 0
  D. the two cancellation identities behind the vanishing t*alpha^t term:
       (i)  sum_j c_j/(s_j-alpha_l) = h0   (i.e. H~(1/alpha_l)=0)
       (ii) T_{L-rho}(eta_l)*U_{L-1}(eta_l) - U_{rho-1}(eta_l) = 0
     and the full mode-coefficient bookkeeping of the five-group expansion:
     coef(t*alpha_l)=0, coef(alpha_l)=0, coef(gamma_r)=0, coef(s_j)=B_rho_j
  E. Luca's Eq. (41) evaluated literally (his c_k, his kernels, his signs)
     vs the exact PMF, plus repaired variants isolating each defect
  F. analytic interlacing gamma_1 < s_1 < alpha_1 on a parameter grid

Outputs: CSV + markdown summary in ../independent_audit_20260609/
Deterministic; no randomness.
"""
from __future__ import annotations

import csv
import os
from fractions import Fraction

import mpmath as mp

mp.mp.dps = 60

HERE = os.path.dirname(os.path.abspath(__file__))
OUTDIR = os.path.join(HERE, "..", "independent_audit_20260609")
os.makedirs(OUTDIR, exist_ok=True)

REPORT_LINES = []


def report(line=""):
    print(line)
    REPORT_LINES.append(line)


# ----------------------------------------------------------------------
# Chebyshev polynomials (numeric, mpmath)
# ----------------------------------------------------------------------
def chebT(n, x):
    if n < 0:
        return chebT(-n, x)
    return mp.chebyt(n, x)


def chebU(n, x):
    if n == -1:
        return mp.mpf(0)
    if n < -1:
        return -chebU(-n - 2, x)
    return mp.chebyu(n, x)


def cheb_coeffs(kind, n):
    """Exact integer coefficient list (ascending) of T_n or U_n."""
    if kind == "U" and n == -1:
        return [Fraction(0)]
    a = [Fraction(1)]  # T0/U0
    if n == 0:
        return a
    b = [Fraction(0), Fraction(1 if kind == "T" else 2)]  # T1=x, U1=2x
    if n == 1:
        return b
    for _ in range(n - 1):
        c = [Fraction(0)] + [2 * v for v in b]
        for i, v in enumerate(a):
            c[i] -= v
        a, b = b, c
    return b


def poly_eval(coeffs, x):
    acc = mp.mpf(0)
    for c in reversed(coeffs):
        acc = acc * x + mp.mpf(c.numerator) / mp.mpf(c.denominator)
    return acc


# ----------------------------------------------------------------------
# Model builders
# ----------------------------------------------------------------------
def build_transient(N, q, beta, exact=False):
    """Transient block T (states 1..N-1) and absorption vector h, target v=0,
    shortcut u=N/2 with weight beta*(1-q) moved from the self-loop to u->0."""
    num = Fraction if exact else (lambda x: mp.mpf(x.numerator) / x.denominator if isinstance(x, Fraction) else mp.mpf(x))
    qf = q if exact else mp.mpf(q.numerator) / q.denominator
    bf = beta if exact else mp.mpf(beta.numerator) / beta.denominator
    one = Fraction(1) if exact else mp.mpf(1)
    half = Fraction(1, 2) if exact else mp.mpf("0.5")
    L = N // 2
    n = N - 1
    T = [[Fraction(0) if exact else mp.mpf(0) for _ in range(n)] for _ in range(n)]
    h = [Fraction(0) if exact else mp.mpf(0) for _ in range(n)]
    for i in range(1, N):
        stay = one - qf
        if i == L:
            stay = stay - bf * (one - qf)
            h[i - 1] += bf * (one - qf)
        T[i - 1][i - 1] = stay
        for j in (i - 1, i + 1):
            jj = j % N
            if jj == 0:
                h[i - 1] += qf * half
            else:
                T[i - 1][jj - 1] += qf * half
    return T, h


def pmf_exact(N, q, beta, n0, tmax):
    """F(t) for t=1..tmax via exact rational iteration  F(t)=e_{n0}^T T^{t-1} h."""
    T, h = build_transient(N, q, beta, exact=True)
    n = N - 1
    row = [Fraction(0)] * n
    row[n0 - 1] = Fraction(1)
    out = []
    for _ in range(tmax):
        out.append(sum(row[i] * h[i] for i in range(n)))
        row = [sum(row[i] * T[i][j] for i in range(n)) for j in range(n)]
    return out


def pmf_mp(N, q, beta, n0, tmax):
    T, h = build_transient(N, q, beta, exact=False)
    n = N - 1
    row = [mp.mpf(0)] * n
    row[n0 - 1] = mp.mpf(1)
    out = []
    for _ in range(tmax):
        out.append(mp.fsum(row[i] * h[i] for i in range(n)))
        row = [mp.fsum(row[i] * T[i][j] for i in range(n)) for j in range(n)]
    return out


# ----------------------------------------------------------------------
# Spectral / closed-form ingredients
# ----------------------------------------------------------------------
def model_quantities(N, q, beta):
    """alpha, gamma, D-roots s_j, residues, h0, a; all mpmath."""
    L = N // 2
    qm = mp.mpf(q.numerator) / q.denominator
    bm = mp.mpf(beta.numerator) / beta.denominator
    a = qm / (bm * (1 - qm))
    h0 = 1 / a
    alpha = [1 - qm + qm * mp.cos((2 * k - 1) * mp.pi / N) for k in range(1, L + 1)]
    gamma = [1 - qm + qm * mp.cos(2 * mp.pi * r / N) for r in range(1, L)]
    # D(y) = a*T_L(y) + U_{L-1}(y) as exact-coefficient poly in y (a rational)
    af = q / (beta * (1 - q))
    TL = cheb_coeffs("T", L)
    UL1 = cheb_coeffs("U", L - 1) + [Fraction(0)]
    D = [af * TL[i] + UL1[i] for i in range(L + 1)]
    roots = mp.polyroots([mp.mpf(c.numerator) / c.denominator for c in reversed(D)],
                         maxsteps=200, extraprec=200)
    yroots = sorted([mp.re(r) for r in roots], reverse=True)
    s = [1 - qm + qm * y for y in yroots]
    # derivative D'(y)
    Dp = [i * D[i] for i in range(1, L + 1)]
    cj = [qm * poly_eval(TL, y) / poly_eval(Dp, y) for y in yroots]  # H residues
    return dict(L=L, q=qm, beta=bm, a=a, h0=h0, alpha=alpha, gamma=gamma,
                yroots=yroots, s=s, cj=cj, Dcoeffs=D, Dpcoeffs=Dp)


def closed_form_pmf(N, q, beta, n0, tmax, mq=None):
    """F(t) = sum_j B_rho_j s_j^{t-1},  B = q*N_rho(y_j)/D'(y_j)."""
    mq = mq or model_quantities(N, q, beta)
    L, qm = mq["L"], mq["q"]
    rho = min(n0 % N, N - (n0 % N))
    TLr = cheb_coeffs("T", L - rho)
    Ur1 = cheb_coeffs("U", rho - 1) if rho >= 1 else [Fraction(0)]
    ULr1 = cheb_coeffs("U", L - rho - 1) if L - rho - 1 >= 0 else [Fraction(0)]
    af = q / (beta * (1 - q))
    B = []
    for y in mq["yroots"]:
        Nrho = (mp.mpf(af.numerator) / af.denominator) * poly_eval(TLr, y) \
            + poly_eval(Ur1, y) + poly_eval(ULr1, y)
        B.append(qm * Nrho / poly_eval(mq["Dpcoeffs"], y))
    return [mp.fsum(B[j] * mq["s"][j] ** (t - 1) for j in range(L))
            for t in range(1, tmax + 1)], B


def mode_functions(N, q, beta, n0, mq):
    """f_l(n0,v), g_l(n0,u,v), G_r(n0,u,v), f_l(u,v) for v=0, u=L."""
    L, qm = mq["L"], mq["q"]
    u, v = L, 0
    dn0 = abs(n0 - v)
    f_n0 = [2 * qm / N * mp.sin(dn0 * mp.pi * (2 * k - 1) / N) * mp.sin(mp.pi * (2 * k - 1) / N)
            for k in range(1, L + 1)]
    du = abs(u - v)
    f_u = [2 * qm / N * mp.sin(du * mp.pi * (2 * k - 1) / N) * mp.sin(mp.pi * (2 * k - 1) / N)
           for k in range(1, L + 1)]
    g = [mp.mpf(2) / N * mp.sin(mp.pi * (2 * k - 1) * abs(n0 - v) / N)
         * mp.sin(mp.pi * (2 * k - 1) * abs(u - v) / N) for k in range(1, L + 1)]
    G = [(mp.cos(2 * mp.pi * r * (u - n0) / N)
          - mp.cos(2 * mp.pi * r * (u - v) / N) * mp.cos(2 * mp.pi * r * (n0 - v) / N)) / N
         for r in range(1, N)]
    return f_n0, f_u, g, G


# ----------------------------------------------------------------------
# A. closed form vs exact chain
# ----------------------------------------------------------------------
def check_closed_form():
    report("## A. Collected closed form vs exact finite chain (exact rationals)")
    rows = []
    for (N, q, beta) in [(10, Fraction(2, 3), Fraction(4, 7)),
                         (8, Fraction(1, 2), Fraction(1, 3)),
                         (14, Fraction(3, 5), Fraction(9, 10))]:
        mq = model_quantities(N, q, beta)
        for n0 in range(1, N // 2 + 1):
            tmax = 60
            ex = pmf_exact(N, q, beta, n0, tmax)
            cf, _ = closed_form_pmf(N, q, beta, n0, tmax, mq)
            err = max(abs(mp.mpf(e.numerator) / e.denominator - c) for e, c in zip(ex, cf))
            rows.append((N, str(q), str(beta), n0, mp.nstr(err, 3)))
        report(f"  N={N} q={q} beta={beta}: max |exact - closed form| over n0, t<=60 : "
               f"{max(mp.mpf(r[4]) for r in rows if r[0] == N)}")
    with open(os.path.join(OUTDIR, "closed_form_vs_exact.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["N", "q", "beta", "n0", "max_abs_err_t1_60"])
        w.writerows(rows)
    report("")


# ----------------------------------------------------------------------
# B. spectrum of the transient block
# ----------------------------------------------------------------------
def check_spectrum():
    report("## B. Spectrum of the transient block (symmetric => diagonalizable)")
    N, q, beta = 10, Fraction(2, 3), Fraction(4, 7)
    T, h = build_transient(N, q, beta, exact=False)
    n = N - 1
    asym = max(abs(T[i][j] - T[j][i]) for i in range(n) for j in range(n))
    report(f"  max |T - T^t| = {mp.nstr(asym, 3)}   (transient block is exactly symmetric)")
    M = mp.matrix(n, n)
    for i in range(n):
        for j in range(n):
            M[i, j] = T[i][j]
    eigs = sorted([mp.re(e) for e in mp.eig(M, left=False, right=False)], reverse=True)
    mq = model_quantities(N, q, beta)
    pred = sorted(mq["s"] + mq["gamma"], reverse=True)
    err = max(abs(e - p) for e, p in zip(eigs, pred))
    report(f"  spectrum == {{roots of D}} U {{gamma_r}} : max err = {mp.nstr(err, 3)}")
    gaps = min(abs(eigs[i] - eigs[i + 1]) for i in range(n - 1))
    report(f"  minimal eigenvalue gap = {mp.nstr(gaps, 3)} (all simple; no Jordan block possible)")
    dal = min(min(abs(e - alpha) for e in eigs) for alpha in mq["alpha"])
    report(f"  min distance spectrum <-> alpha_l = {mp.nstr(dal, 3)}  (alpha_l NOT an eigenvalue)")
    report("")


# ----------------------------------------------------------------------
# C. tail diagnostics
# ----------------------------------------------------------------------
def check_tail():
    report("## C. Tail diagnostics (mp dps=60)")
    N, q, beta, n0 = 10, Fraction(2, 3), Fraction(4, 7), 3
    mq = model_quantities(N, q, beta)
    tmax = 3000
    F = pmf_mp(N, q, beta, n0, tmax)
    s1, a1, g1 = mq["s"][0], mq["alpha"][0], mq["gamma"][0]
    cf, B = closed_form_pmf(N, q, beta, n0, tmax, mq)
    report(f"  alpha_1 = {mp.nstr(a1, 12)}, s_1 = {mp.nstr(s1, 12)}, gamma_1 = {mp.nstr(g1, 12)}")
    rows = []
    for t in (50, 200, 800, 2000, 2999):
        ratio = F[t - 1] / F[t - 2]
        norm_s = F[t - 1] / (B[0] * s1 ** (t - 1))
        norm_ta = F[t - 1] / (t * a1 ** (t - 1))
        rows.append((t, mp.nstr(ratio, 15), mp.nstr(norm_s, 10), mp.nstr(norm_ta, 4)))
        report(f"  t={t:5d}  F(t)/F(t-1)={mp.nstr(ratio, 15)}   F/(B1 s1^(t-1))={mp.nstr(norm_s, 10)}   F/(t alpha1^(t-1))={mp.nstr(norm_ta, 4)}")
    with open(os.path.join(OUTDIR, "tail_diagnostics.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["t", "F_ratio", "F_over_B1_s1", "F_over_t_alpha1"])
        w.writerows(rows)
    report(f"  => geometric decay at s_1; the t*alpha_1^t normalisation diverges from any constant: ratio -> 0")
    report("")


# ----------------------------------------------------------------------
# D. the cancellation identities + five-group coefficient bookkeeping
# ----------------------------------------------------------------------
def five_group_coefficients(N, q, beta, n0):
    """Collect, mode by mode, the coefficients of the corrected five-group
    expansion (Eq. 57 of the corrected note):
      group1 = F_{n0}(v,.)                 -> alpha_l^{t-1}
      group2 = q W * delta * h0 delta_0    -> gamma_r^{t-1}, alpha_r^{t-1}
      group3 = q W * delta * H_+           -> s_j^{t-1}, gamma_r^{t-1}, alpha_r^{t-1}
      group4 = -q W * F_u * h0 delta_0     -> gamma/alpha pairs + (t-1)alpha^{t-2}
      group5 = -q W * F_u * H_+            -> triple partial fractions + diagonal
    Returns dict with per-mode totals."""
    mq = model_quantities(N, q, beta)
    L, qm, h0 = mq["L"], mq["q"], mq["h0"]
    alpha, gamma, s, cj = mq["alpha"], mq["gamma"], mq["s"], mq["cj"]
    f_n0, f_u, g, G = mode_functions(N, q, beta, n0, mq)
    # gamma_r in the W sum runs r=1..N-1 (values repeat); keep full list
    gamma_full = [1 - qm + qm * mp.cos(2 * mp.pi * r / N) for r in range(1, N)]

    coef_t_alpha = [mp.mpf(0)] * L      # coefficient of (t-1) alpha_l^{t-2}
    coef_alpha = [mp.mpf(0)] * L        # coefficient of alpha_l^{t-1}
    coef_gamma = [mp.mpf(0)] * (N - 1)  # coefficient of gamma_r^{t-1} (full set)
    coef_s = [mp.mpf(0)] * L            # coefficient of s_j^{t-1}

    # group 1
    for l in range(L):
        coef_alpha[l] += f_n0[l]
    # group 2: q h0 [ sum_r G_r gamma_r^{t-1} + sum_r g_r alpha_r^{t-1} ]
    for r in range(N - 1):
        coef_gamma[r] += qm * h0 * G[r]
    for r in range(L):
        coef_alpha[r] += qm * h0 * g[r]
    # group 3: q sum_j c_j [ G_r (s_j^{t-1}-gamma_r^{t-1})/(s_j-gamma_r) + g_r (...alpha...) ]
    for j in range(L):
        for r in range(N - 1):
            k = qm * cj[j] * G[r] / (s[j] - gamma_full[r])
            coef_s[j] += k
            coef_gamma[r] -= k
        for r in range(L):
            k = qm * cj[j] * g[r] / (s[j] - alpha[r])
            coef_s[j] += k
            coef_alpha[r] -= k
    # group 4: -q h0 sum_l f_u[l] [ G_r (gamma_r^{t-1}-alpha_l^{t-1})/(gamma_r-alpha_l)
    #          + sum_{r!=l} g_r (alpha_r^{t-1}-alpha_l^{t-1})/(alpha_r-alpha_l)
    #          + g_l (t-1) alpha_l^{t-2} ]
    for l in range(L):
        for r in range(N - 1):
            k = qm * h0 * f_u[l] * G[r] / (gamma_full[r] - alpha[l])
            coef_gamma[r] -= k
            coef_alpha[l] += k
        for r in range(L):
            if r == l:
                continue
            k = qm * h0 * f_u[l] * g[r] / (alpha[r] - alpha[l])
            coef_alpha[r] -= k
            coef_alpha[l] += k
        coef_t_alpha[l] -= qm * h0 * f_u[l] * g[l]
    # group 5: -q sum_j c_j sum_l f_u[l] [ G_r triple(gamma_r, alpha_l, s_j)
    #          + sum_{r!=l} g_r triple(alpha_r, alpha_l, s_j)
    #          + g_l ((s_j^{t-1}-alpha_l^{t-1})/(s_j-alpha_l)^2 - (t-1)alpha_l^{t-2}/(s_j-alpha_l)) ]
    for j in range(L):
        for l in range(L):
            for r in range(N - 1):
                x, y2, sj = gamma_full[r], alpha[l], s[j]
                c = qm * cj[j] * f_u[l] * G[r]
                coef_gamma[r] -= c / ((x - y2) * (x - sj))
                coef_alpha[l] -= c / ((y2 - x) * (y2 - sj))
                coef_s[j] -= c / ((sj - x) * (sj - y2))
            for r in range(L):
                if r == l:
                    continue
                x, y2, sj = alpha[r], alpha[l], s[j]
                c = qm * cj[j] * f_u[l] * g[r]
                coef_alpha[r] -= c / ((x - y2) * (x - sj))
                coef_alpha[l] -= c / ((y2 - x) * (y2 - sj))
                coef_s[j] -= c / ((sj - x) * (sj - y2))
            c = qm * cj[j] * f_u[l] * g[l]
            coef_s[j] -= c / (s[j] - alpha[l]) ** 2
            coef_alpha[l] += c / (s[j] - alpha[l]) ** 2
            coef_t_alpha[l] += c / (s[j] - alpha[l])
    return mq, coef_t_alpha, coef_alpha, coef_gamma, coef_s


def check_cancellations():
    report("## D. Cancellation identities and five-group mode bookkeeping")
    N, q, beta, n0 = 10, Fraction(2, 3), Fraction(4, 7), 3
    mq, ct, ca, cg, cs = five_group_coefficients(N, q, beta, n0)
    L = mq["L"]
    # identity (i): sum_j c_j/(s_j - alpha_l) = h0  <=>  H~(1/alpha_l) = 0
    rows = []
    for l in range(L):
        lhs = mp.fsum(mq["cj"][j] / (mq["s"][j] - mq["alpha"][l]) for j in range(L))
        rows.append((l + 1, mp.nstr(lhs, 20), mp.nstr(mq["h0"], 20), mp.nstr(lhs - mq["h0"], 3)))
    err_i = max(abs(mp.mpf(r[3])) for r in rows)
    report(f"  (i)  sum_j c_j/(s_j-alpha_l) - h0 : max |.| over l = {mp.nstr(err_i, 3)}   [H~(1/alpha_l)=0]")
    # identity (i'): sum_j c_j/(gamma_r - s_j) = 0  <=>  H~(1/gamma_r) = h0
    err_ip = mp.mpf(0)
    for r in range(L - 1):
        v = mp.fsum(mq["cj"][j] / (mq["gamma"][r] - mq["s"][j]) for j in range(L))
        err_ip = max(err_ip, abs(v))
    report(f"  (i') sum_j c_j/(gamma_r-s_j) : max |.| = {mp.nstr(err_ip, 3)}   [H~(1/gamma_r)=h0]")
    # identity (ii): Chebyshev at T_L zeros
    err_ii = mp.mpf(0)
    for l in range(1, L + 1):
        eta = mp.cos((2 * l - 1) * mp.pi / (2 * L))
        for rho in range(1, L + 1):
            v = chebT(L - rho, eta) * chebU(L - 1, eta) - chebU(rho - 1, eta)
            err_ii = max(err_ii, abs(v))
    report(f"  (ii) T_(L-rho)(eta_l)U_(L-1)(eta_l)-U_(rho-1)(eta_l) : max |.| = {mp.nstr(err_ii, 3)}")
    # bookkeeping totals
    _, B = closed_form_pmf(N, q, beta, n0, 1, mq)
    max_ta = max(abs(v) for v in ct)
    max_a = max(abs(v) for v in ca)
    max_g = max(abs(v) for v in cg)
    max_s = max(abs(cs[j] - B[j]) for j in range(L))
    report(f"  five-group totals (N={N}, q={q}, beta={beta}, n0={n0}):")
    report(f"    coefficient of (t-1)*alpha_l^(t-2): max |.| = {mp.nstr(max_ta, 3)}  -> 0")
    report(f"    coefficient of alpha_l^(t-1)      : max |.| = {mp.nstr(max_a, 3)}  -> 0")
    report(f"    coefficient of gamma_r^(t-1)      : max |.| = {mp.nstr(max_g, 3)}  -> 0")
    report(f"    coefficient of s_j^(t-1) - B_rho_j: max |.| = {mp.nstr(max_s, 3)}  -> B matches")
    with open(os.path.join(OUTDIR, "mode_coefficient_bookkeeping.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["mode", "index", "coefficient_total"])
        for l in range(L):
            w.writerow(["t_alpha", l + 1, mp.nstr(ct[l], 20)])
        for l in range(L):
            w.writerow(["alpha", l + 1, mp.nstr(ca[l], 20)])
        for r in range(N - 1):
            w.writerow(["gamma", r + 1, mp.nstr(cg[r], 20)])
        for j in range(L):
            w.writerow(["s", j + 1, mp.nstr(cs[j], 20)])
            w.writerow(["B_closed_form", j + 1, mp.nstr(B[j], 20)])
    # antipodal degeneracy: G_r(n0, u=L, v=0) = 0
    for n0b in (1, 2, 3, 4, 5):
        _, _, _, G = mode_functions(N, q, beta, n0b, mq)
        gmax = max(abs(v) for v in G)
        if n0b == n0:
            report(f"    G1_r(n0={n0b}, u=L, v=0): max |.| = {mp.nstr(gmax, 3)}  (gamma modes absent at antipodal u)")
    # robustness of (i) over parameters: not a tuned coincidence
    worst = mp.mpf(0)
    for (NN, qq, bb) in [(8, Fraction(1, 5), Fraction(1, 100)), (12, Fraction(9, 10), Fraction(1, 1)),
                         (20, Fraction(2, 7), Fraction(3, 11)), (16, Fraction(1, 2), Fraction(99, 100))]:
        m2 = model_quantities(NN, qq, bb)
        for l in range(m2["L"]):
            v = mp.fsum(m2["cj"][j] / (m2["s"][j] - m2["alpha"][l]) for j in range(m2["L"])) - m2["h0"]
            worst = max(worst, abs(v))
    report(f"  (i) across N=8..20, q=0.2..0.9, beta=0.01..1: max deviation = {mp.nstr(worst, 3)} (identity, not tuning)")
    report("")


# ----------------------------------------------------------------------
# E. Luca's Eq. (41) literal evaluation
# ----------------------------------------------------------------------
def luca_ck_literal(N, mq):
    """His Eq. (ck): c_k = -(N/2q) * [(1+1/N)(y)U_{N-1}(y) - T_N(y) - U_{N-2}(y) - 1]
                          / [ (y^2-1) T_{N/2}(y)^2 ],  y = 1+(s_k-1)/q."""
    out = []
    qm = mq["q"]
    for y in mq["yroots"]:
        num = (1 + mp.mpf(1) / N) * y * chebU(N - 1, y) - chebT(N, y) - chebU(N - 2, y) - 1
        den = (y ** 2 - 1) * chebT(N // 2, y) ** 2
        out.append(-(N / (2 * qm)) * num / den)
    return out


def luca_eq41(N, q, beta, n0, tmax, sign=-1, ck_mode="luca", baseline="u"):
    """Evaluate his Eq. (41) (eq:fp_time_2 of Calculations.tex) literally.
    sign: -1 as written (second line subtracted ... his global -q), +1 repaired.
    ck_mode: 'luca' = his eq:ck, 'true' = q*T_L(y_k)/D'(y_k).
    baseline: 'u' = his f_l(n0,u) baseline, 'v' = repaired f_l(n0,v)."""
    mq = model_quantities(N, q, beta)
    L, qm = mq["L"], mq["q"]
    alpha, s = mq["alpha"], mq["s"]
    gamma_full = [1 - qm + qm * mp.cos(2 * mp.pi * r / N) for r in range(1, N)]
    f_n0v, f_u, g, G = mode_functions(N, q, beta, n0, mq)
    # f_l(n0, u): distance |u - n0|
    du = abs(N // 2 - n0)
    f_n0u = [2 * qm / N * mp.sin(du * mp.pi * (2 * k - 1) / N) * mp.sin(mp.pi * (2 * k - 1) / N)
             for k in range(1, L + 1)]
    fbase = f_n0u if baseline == "u" else f_n0v
    ck = luca_ck_literal(N, mq) if ck_mode == "luca" else mq["cj"]
    out = []
    for t in range(1, tmax + 1):
        val = mp.fsum(fbase[l] * alpha[l] ** (t - 1) for l in range(L))
        term = mp.mpf(0)
        for k in range(L):
            for r in range(N - 1):
                term += ck[k] * G[r] / (s[k] * (s[k] - gamma_full[r])) * (s[k] ** t - gamma_full[r] ** t)
            for l in range(L):
                term += ck[k] * g[l] / (s[k] * (s[k] - alpha[l])) * (s[k] ** t - alpha[l] ** t)
        val += sign * qm * term
        t3 = mp.mpf(0)
        for k in range(L):
            for r in range(N - 1):
                for l in range(L):
                    t3 += ck[k] * G[r] * f_u[l] / (s[k] - alpha[l]) * (
                        (s[k] ** t - gamma_full[r] ** t) / (alpha[l] * (s[k] - gamma_full[r]))
                        - (alpha[l] ** t - gamma_full[r] ** t) / (s[k] * (alpha[l] - gamma_full[r])))
        val += -sign * qm * t3
        t4 = mp.mpf(0)
        for k in range(L):
            for l in range(L):
                t4 += ck[k] * g[l] * f_u[l] / (s[k] * alpha[l] * (s[k] - alpha[l])) * alpha[l] ** t * t
        val += sign * qm * t4
        t5 = mp.mpf(0)
        for k in range(L):
            for r in range(L):
                for l in range(L):
                    if r == l:
                        continue
                    t5 += ck[k] * g[r] * f_u[l] / (s[k] * alpha[l] * (s[k] - alpha[l])) * (
                        s[k] * (s[k] ** t - gamma_full[r] ** t) / (s[k] - gamma_full[r])
                        - alpha[l] * (alpha[l] ** t - gamma_full[r] ** t) / (alpha[l] - gamma_full[r]))
        val += -sign * qm * t5
        out.append(val)
    return out, ck, mq


def check_luca_eq41():
    report("## E. Luca's Eq. (41) evaluated literally vs the exact PMF")
    N, q, beta, n0 = 10, Fraction(2, 3), Fraction(4, 7), 3
    tmax = 40
    ex = [mp.mpf(v.numerator) / v.denominator for v in pmf_exact(N, q, beta, n0, tmax)]
    lit, ck_l, mq = luca_eq41(N, q, beta, n0, tmax, sign=-1, ck_mode="luca", baseline="u")
    err_lit = max(abs(a - b) for a, b in zip(lit, ex))
    mass = mp.fsum(lit)
    report(f"  as written (his c_k, his signs, baseline f(n0,u)):   max|err| = {mp.nstr(err_lit, 3)}, sum_t F = {mp.nstr(mass, 6)} (should -> 1)")
    rep1, _, _ = luca_eq41(N, q, beta, n0, tmax, sign=+1, ck_mode="luca", baseline="v")
    err1 = max(abs(a - b) for a, b in zip(rep1, ex))
    report(f"  sign repaired + baseline f(n0,v), his c_k:           max|err| = {mp.nstr(err1, 3)}")
    rep2, _, _ = luca_eq41(N, q, beta, n0, tmax, sign=+1, ck_mode="true", baseline="v")
    err2 = max(abs(a - b) for a, b in zip(rep2, ex))
    report(f"  sign repaired + baseline f(n0,v) + true residues c_j: max|err| = {mp.nstr(err2, 3)}")
    report(f"    (remaining error = the H(0) boundary term + gamma-pairing of the g-modes;")
    report(f"     his kernels use (s^t-x^t)/(s(s-x)), i.e. they extend H(t)=sum c_k s_k^(t-1) down to t=0)")
    # the H(0) mismatch that manufactures his t*alpha^t coefficient
    h0_true = mq["h0"]
    h0_impl = mp.fsum(mq["cj"][k] / mq["s"][k] for k in range(mq["L"]))
    report(f"  H(0) true = beta(1-q)/q = {mp.nstr(h0_true, 12)}")
    report(f"  H(0) implied by extending the pole sum = sum_k c_k/s_k = {mp.nstr(h0_impl, 12)}")
    report(f"  mismatch = {mp.nstr(h0_true - h0_impl, 12)}  (nonzero: the spurious t*alpha^t source)")
    # his t*alpha_l^t coefficient equals -q g f (h0_true - h0_implied)/alpha^2 ... verify l=1
    l = 0
    f_n0v, f_u, g, G = mode_functions(N, q, beta, n0, mq)
    his_coef = -mp.fsum(mq["q"] * mq["cj"][k] * g[l] * f_u[l]
                        / (mq["s"][k] * mq["alpha"][l] * (mq["s"][k] - mq["alpha"][l]))
                        for k in range(mq["L"]))
    pred = -mq["q"] * g[l] * f_u[l] * (h0_true - h0_impl) / mq["alpha"][l] ** 2
    report(f"  his t*alpha_1^t coefficient (true c_j) = {mp.nstr(his_coef, 12)}")
    report(f"  -q g_1 f_1 (h0_true - h0_implied)/alpha_1^2 = {mp.nstr(pred, 12)}   diff = {mp.nstr(his_coef - pred, 3)}")
    report(f"  => his coefficient is exactly proportional to the H(0) mishandling; with H(0) correct it is 0.")
    rows = [(t, mp.nstr(ex[t - 1], 17), mp.nstr(lit[t - 1], 17), mp.nstr(rep1[t - 1], 17), mp.nstr(rep2[t - 1], 17))
            for t in range(1, tmax + 1)]
    with open(os.path.join(OUTDIR, "luca_eq41_vs_exact.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["t", "exact", "eq41_as_written", "eq41_sign_baseline_fixed", "eq41_also_true_ck"])
        w.writerows(rows)
    report("")


# ----------------------------------------------------------------------
# F. interlacing gamma_1 < s_1 < alpha_1 on a grid
# ----------------------------------------------------------------------
def check_interlacing():
    report("## F. gamma_1 < s_1 < alpha_1 on a parameter grid (and D at gamma/alpha points)")
    bad = 0
    tested = 0
    for N in (6, 10, 14, 20, 40):
        for qn in (1, 3, 5, 7, 9):
            for bn in (1, 25, 50, 75, 100):
                q, b = Fraction(qn, 10), Fraction(bn, 100)
                mq = model_quantities(N, q, b)
                s1, a1, g1 = mq["s"][0], mq["alpha"][0], mq["gamma"][0]
                tested += 1
                if not (g1 < s1 < a1):
                    bad += 1
    report(f"  grids tested: {tested}, violations of gamma_1 < s_1 < alpha_1: {bad}")
    # sign facts: D(eta(alpha_l)) = U_(L-1)(eta_l) != 0; D(y(gamma_r)) = a(-1)^r
    N, q, b = 10, Fraction(2, 3), Fraction(4, 7)
    mq = model_quantities(N, q, b)
    L, a = mq["L"], mq["a"]
    worst = mp.mpf(0)
    for r in range(1, L):
        y = mp.cos(2 * mp.pi * r / N)
        Dv = a * chebT(L, y) + chebU(L - 1, y)
        worst = max(worst, abs(Dv - a * (-1) ** r))
    report(f"  D at gamma_r points minus a(-1)^r: max|.| = {mp.nstr(worst, 3)}  (so s_k = gamma_r crossing impossible for beta>0)")
    worst = mp.mpf(0)
    for l in range(1, L + 1):
        y = mp.cos((2 * l - 1) * mp.pi / N)
        Dv = a * chebT(L, y) + chebU(L - 1, y)
        Uv = chebU(L - 1, y)
        worst = max(worst, abs(Dv - Uv))
    report(f"  D at alpha_l points minus U_(L-1): max|.| = {mp.nstr(worst, 3)}  (alpha_l never a root of D)")
    report("")


def check_amplitudes():
    """Compact amplitude form B_rho_j = q U_(rho-1)(y_j)[T_L(y_j)-1]/[T_L(y_j) D'(y_j)]
    and strict positivity of the dominant amplitude B_rho_1."""
    report("## G. Compact amplitude form and strict positivity of B_rho_1")

    def Upoly(n, x):
        return poly_eval(cheb_coeffs("U", n) if n >= 0 else [Fraction(0)], x)

    def Tpoly(n, x):
        return poly_eval(cheb_coeffs("T", n), x)

    worst, minB1, tlbad, npts = mp.mpf(0), mp.inf, 0, 0
    for N in (4, 6, 10, 14, 20, 40):
        for qn in (1, 3, 5, 7, 9):
            for bn in (1, 25, 50, 75, 100):
                q, b = Fraction(qn, 10), Fraction(bn, 100)
                mq = model_quantities(N, q, b)
                L = mq["L"]
                npts += 1
                if not (Tpoly(L, mq["yroots"][0]) < 0):
                    tlbad += 1
                for rho in range(1, L + 1):
                    _, B = closed_form_pmf(N, q, b, rho, 1, mq)
                    for j, y in enumerate(mq["yroots"]):
                        comp = mq["q"] * Upoly(rho - 1, y) * (Tpoly(L, y) - 1) \
                            / (Tpoly(L, y) * poly_eval(mq["Dpcoeffs"], y))
                        worst = max(worst, abs(comp - B[j]))
                    minB1 = min(minB1, B[0])
    report(f"  grid points: {npts} (N up to 40, all rho)")
    report(f"  compact form vs residue form: max|diff| = {mp.nstr(worst, 3)}")
    report(f"  min B_rho_1 over grid = {mp.nstr(minB1, 6)}  (strictly positive: dominant mode never drops out)")
    report(f"  T_L(y_1) in (-1,0) violations: {tlbad}")
    report("")


def main():
    report("# Independent audit: long-time tail of the antipodal-shortcut first passage")
    report("")
    report("Model: lazy ring N=2L, stay 1-q, hop q/2; absorbing v=0; directed shortcut")
    report("u=L->v with weight beta(1-q) moved from the self-loop. All checks deterministic.")
    report("")
    check_closed_form()
    check_spectrum()
    check_tail()
    check_cancellations()
    check_luca_eq41()
    check_interlacing()
    check_amplitudes()
    with open(os.path.join(OUTDIR, "independent_audit_summary.md"), "w") as fh:
        fh.write("\n".join(REPORT_LINES) + "\n")
    print(f"[written] {os.path.join(OUTDIR, 'independent_audit_summary.md')}")


if __name__ == "__main__":
    main()
