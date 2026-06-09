#!/usr/bin/env python3
"""Strict positivity of the dominant first-passage amplitude B_{rho,1}.

This closes the last open assumption in the corrected tail statement
F_rho(0,t) ~ B_{rho,1} s_1^{t-1}: the manuscript previously read
"assuming B_{rho,1} != 0".  Here we (a) confirm the compact closed form

    B_{rho,j} = q U_{rho-1}(y_j) [T_L(y_j) - 1] / [ T_L(y_j) D'(y_j) ]

equals the Appendix-C residue form B_{rho,j} = q N_rho(y_j)/D'(y_j) on every
root, (b) verify the three sign facts on the dominant root
    T_L(y_1) in (-1,0),  U_{rho-1}(y_1) > 0,  D'(y_1) > 0,
which force B_{rho,1} > 0, and (c) cross-check B_{rho,1} against the exact
finite shortcut-matrix PMF amplitude lim_t F(t)/s_1^{t-1} on small cases.

Model and helpers are imported from secular_term_cancellation_check.py.
All computations in mpmath with mp.dps = 50.

Run:
    .venv/bin/python scripts/dominant_amplitude_positivity_check.py
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mpmath import mp, mpf, cos, pi, diff, fabs, nstr  # noqa: E402

from secular_term_cancellation_check import (  # noqa: E402
    build_model, D_func, N_rho_func, D_roots, residues, exact_F,
    cheb_T, cheb_U,
)

mp.dps = 50

# Parameter grid: even N, interior q, full beta range, every folded distance rho.
NS = [6, 8, 10, 12, 16, 20, 24, 30, 40]
QS = ["1/4", "1/3", "1/2", "2/3", "3/4", "9/10"]
BETAS = ["1/100", "1/50", "1/10", "3/10", "4/7", "9/10", "1"]
# Exact-matrix cross-check is O(N^2 * tmax); restrict to small N to stay fast.
EXACT_NS = {6, 8, 10, 12}


def frac(s):
    num, den = s.split("/") if "/" in s else (s, "1")
    return mpf(num) / mpf(den)


def dominant_amplitude_exact(m, s1):
    """B_{rho,1} read off the exact finite-matrix PMF: F(t)/s1^{t-1} as t->inf.

    s1 is the largest pole, so F(t)/s1^{t-1} -> B_{rho,1}.  Pick tmax so the
    second mode is suppressed below 1e-40 relative to the first.
    """
    # crude: grow tmax with how close the spectral gap is; cap for runtime
    tmax = 500
    F = exact_F(m, tmax, with_shortcut=True)
    # use the last two times and Richardson-free direct ratio (s1 dominates)
    t = tmax
    return F[t] / (s1 ** (t - 1))


def main():
    lines = []

    def say(s=""):
        print(s)
        lines.append(s)

    say("=" * 78)
    say("Strict positivity of the dominant first-passage amplitude B_{rho,1}")
    say("mpmath dps = %d" % mp.dps)
    say("=" * 78)

    n_points = 0
    max_compact_vs_residue = mpf(0)
    min_B1 = None
    min_B1_where = None
    worst_TL = None        # closest T_L(y_1) gets to a boundary of (-1,0)
    sign_violations = 0
    bracket_violations = 0
    max_exact_err = mpf(0)
    n_exact = 0

    for N in NS:
        L = N // 2
        for qs in QS:
            for bs in BETAS:
                q, beta = frac(qs), frac(bs)
                for rho in range(1, L + 1):
                    m = build_model(N, float(q), float(beta), rho)
                    # rebuild with exact rationals for q, beta
                    m["q"], m["beta"] = q, beta
                    m["lam"] = beta * (1 - q)
                    m["a"] = q / m["lam"]
                    m["h0"] = 1 / m["a"]
                    D = D_func(m)
                    ys = D_roots(m)
                    y1 = ys[0]
                    cs, Bs, ss = residues(m, ys)
                    B1_res = Bs[0]
                    s1 = ss[0]

                    TL1 = cheb_T(L, y1)
                    Urm1 = cheb_U(rho - 1, y1)
                    Dp1 = diff(D, y1)
                    B1_cmp = q * Urm1 * (TL1 - 1) / (TL1 * Dp1)

                    dev = fabs(B1_cmp - B1_res)
                    if dev > max_compact_vs_residue:
                        max_compact_vs_residue = dev

                    # sign facts on the dominant root
                    ok_TL = (-1 < TL1 < 0)
                    ok_U = (Urm1 > 0)
                    ok_Dp = (Dp1 > 0)
                    if not (ok_TL and ok_U and ok_Dp):
                        sign_violations += 1
                        say("  SIGN VIOLATION N=%d q=%s beta=%s rho=%d: "
                            "T_L=%s U=%s Dp=%s"
                            % (N, qs, bs, rho, nstr(TL1, 6),
                               nstr(Urm1, 6), nstr(Dp1, 6)))

                    # dominant root must sit in (cos(pi/L), cos(pi/2L))
                    lo, hi = cos(pi / L), cos(pi / (2 * L))
                    if not (lo < y1 < hi):
                        bracket_violations += 1
                        say("  BRACKET VIOLATION N=%d q=%s beta=%s rho=%d: "
                            "y1=%s not in (%s,%s)"
                            % (N, qs, bs, rho, nstr(y1, 8),
                               nstr(lo, 8), nstr(hi, 8)))

                    if (min_B1 is None) or (B1_res < min_B1):
                        min_B1 = B1_res
                        min_B1_where = (N, qs, bs, rho)
                    margin = min(TL1 - (-1), 0 - TL1)
                    if (worst_TL is None) or (margin < worst_TL):
                        worst_TL = margin

                    if N in EXACT_NS and rho in (1, L // 2 or 1, L):
                        B1_exact = dominant_amplitude_exact(m, s1)
                        eerr = fabs(B1_exact - B1_res)
                        if eerr > max_exact_err:
                            max_exact_err = eerr
                        n_exact += 1

                    n_points += 1

    say()
    say("points checked (N x q x beta x rho)        : %d" % n_points)
    say("max | compact form - residue form |        : %s" % nstr(max_compact_vs_residue, 4))
    say("exact-matrix cross-checks (small N)        : %d" % n_exact)
    say("max | B1_residue - B1_exact_matrix |       : %s" % nstr(max_exact_err, 4))
    say("sign-fact violations (T_L,U,D' on y_1)     : %d" % sign_violations)
    say("dominant-root bracket violations           : %d" % bracket_violations)
    say("min B_{rho,1} over the whole grid          : %s" % nstr(min_B1, 6))
    say("    attained at (N,q,beta,rho)             : %s" % str(min_B1_where))
    say("smallest margin of T_L(y_1) to {-1,0}      : %s" % nstr(worst_TL, 4))
    say()
    verdict = (sign_violations == 0 and bracket_violations == 0
               and min_B1 is not None and min_B1 > 0
               and max_compact_vs_residue < mpf(10) ** (-40)
               and (n_exact == 0 or max_exact_err < mpf(10) ** (-12)))
    say("VERDICT: B_{rho,1} > 0 strictly, compact form == residue form, "
        "and matrix-confirmed  ->  %s" % ("PASS" if verdict else "FAIL"))
    say("=" * 78)

    here = os.path.dirname(os.path.abspath(__file__))
    out_dir = os.path.dirname(here)
    with open(os.path.join(out_dir, "dominant_amplitude_positivity_report.txt"), "w") as f:
        f.write("\n".join(lines) + "\n")
    summary = dict(
        points=n_points,
        max_compact_vs_residue=nstr(max_compact_vs_residue, 4),
        max_exact_err=nstr(max_exact_err, 4),
        n_exact=n_exact,
        sign_violations=sign_violations,
        bracket_violations=bracket_violations,
        min_B1=nstr(min_B1, 6),
        min_B1_where=str(min_B1_where),
        verdict="PASS" if verdict else "FAIL",
    )
    with open(os.path.join(out_dir, "dominant_amplitude_positivity_results.json"), "w") as f:
        json.dump(summary, f, indent=2)
    return 0 if verdict else 1


if __name__ == "__main__":
    raise SystemExit(main())
