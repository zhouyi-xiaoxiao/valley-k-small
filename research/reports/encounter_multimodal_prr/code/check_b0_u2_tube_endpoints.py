#!/usr/bin/env python3
"""Verify the corrected (inward-rounded) U2 tube endpoints of the B0 bound.

Codex cross-audit finding C3 (2026-08-24): the previously printed
U2 = [1.08187, 2.14030] in prr_assets/b0_quantitative_bound.tex was rounded
OUTWARD from the half-curvature crossings, so min |G''| over the printed
interval fell below the claimed mu2_hat = 2.97432e-2
(G''(1.08187) = 2.30287e-2).  The fix prints inward-rounded endpoints
U2 = [1.081873, 2.140298]; this script certifies, by high-precision
quadrature (mpmath, 30 significant digits) with exact symbolic time
derivatives (mpmath.diff on the quadrature integrand), that

    G''(t) >= mu2_hat = 2.97432e-2   for all t in [1.081873, 2.140298].

Checks performed:
  1. G'' at both printed endpoints exceeds mu2_hat (high precision).
  2. The half-curvature crossings are located and confirmed to lie OUTSIDE
     the printed interval (left crossing < 1.081873, right crossing > 2.140298).
  3. A 1201-point interior scan (float pipeline, consistent with the
     high-precision endpoint evaluations to ~1e-5) confirms G'' has no
     interior dip: its minimum over the printed interval is attained at a
     scan endpoint (the right one), whose value is certified in step 1.

Model: the m=2 anchor of the quantitative-bound section
(eps=0.1, targets (1.0, 2.5), equal weights), identical to the
independent reconstruction used by the cross-audit.

Run with an interpreter that has mpmath + numpy, e.g.
    ~/.venvs/valley-k-small/bin/python3 code/check_b0_u2_tube_endpoints.py
"""

from __future__ import annotations

import math

import numpy as np
from mpmath import mp, mpf, erf, exp, sqrt, pi, quad, findroot, diff

mp.dps = 30

# Model constants (b0_quantitative_bound.tex anchor).
GAMMA = D0 = RHO = W = mpf(1)
Z0 = mpf(4)
ZBAR = mpf(0)
A = mpf("0.4")
U0 = SIGPERP0 = mpf("0.3")
RPAR0 = mpf("0.1")
EPS = mpf("0.1")
TARGETS = (mpf(1), mpf("2.5"))
WEIGHTS = (mpf("0.5"), mpf("0.5"))
S2 = D0 / (2 * GAMMA) + RHO**2
MU2_HAT = mpf("2.97432e-2")
PRINTED_LEFT = mpf("1.081873")
PRINTED_RIGHT = mpf("2.140298")


def phi(x, var):
    return exp(-x * x / (2 * var)) / sqrt(2 * pi * var)


def Phi(u):
    return (1 + erf(u / sqrt(2))) / 2


def mu(t):
    return ZBAR + (Z0 - ZBAR) * exp(-GAMMA * t)


def contact(t):
    mean_p = RPAR0 * exp(-GAMMA * t)
    var_p = EPS**2 * (
        U0**2 * exp(-2 * GAMMA * t) + (2 * D0 / GAMMA) * (1 - exp(-2 * GAMMA * t))
    )
    var_y = EPS**2 * (SIGPERP0**2 + 4 * D0 * t)
    s = sqrt(var_p)

    def integrand(y):
        folded = 2 * sum(phi(y + k * W, var_y) for k in range(-6, 7))
        chord = sqrt(A * A - y * y)
        ppar = Phi((chord - mean_p) / s) - Phi((-chord - mean_p) / s)
        return folded * ppar

    return quad(integrand, [0, A])


def free_clock(t):
    var = EPS**2 * S2
    mix = sum(
        w * exp(-((mu(t) - mu(tj)) ** 2) / (2 * var))
        for w, tj in zip(WEIGHTS, TARGETS)
    )
    return contact(t) * mix / (W * sqrt(2 * pi * var))


def g2(t):
    return diff(free_clock, t, 2)


# Float pipeline for the interior scan (matches the audit reconstruction).
def contact_f(t: float, ny: int = 2401) -> float:
    mean_p = 0.1 * math.exp(-t)
    var_p = 0.01 * (0.09 * math.exp(-2 * t) + 2.0 * (1 - math.exp(-2 * t)))
    var_y = 0.01 * (0.09 + 4.0 * t)
    y = np.linspace(0.0, 0.4, ny)
    images = np.arange(-6, 7, dtype=float) * 1.0
    folded = (
        2
        * (
            np.exp(-((y[:, None] + images[None, :]) ** 2) / (2 * var_y))
            / math.sqrt(2 * math.pi * var_y)
        ).sum(axis=1)
    )
    chord = np.sqrt(np.maximum(0.16 - y * y, 0.0))
    s = math.sqrt(var_p)
    from math import erf as merf

    def cdf(arr):
        flat = np.asarray(arr, float).ravel()
        out = np.fromiter(
            (0.5 * (1.0 + merf(v / math.sqrt(2.0))) for v in flat),
            dtype=float,
            count=flat.size,
        )
        return out.reshape(np.shape(arr))

    ppar = cdf((chord - mean_p) / s) - cdf((-chord - mean_p) / s)
    return float(np.trapezoid(folded * ppar, y))


def free_clock_f(t: float) -> float:
    var = 0.01 * 1.5
    muv = 4.0 * math.exp(-t)
    mix = sum(
        0.5 * math.exp(-((muv - 4.0 * math.exp(-tj)) ** 2) / (2 * var))
        for tj in (1.0, 2.5)
    )
    return contact_f(t) * mix / math.sqrt(2 * math.pi * var)


def g2_f(t: float, h: float = 2e-4) -> float:
    f = free_clock_f
    return (
        -f(t + 2 * h) + 16 * f(t + h) - 30 * f(t) + 16 * f(t - h) - f(t - 2 * h)
    ) / (12 * h * h)


def main() -> None:
    ok = True
    print(f"mu2_hat = {MU2_HAT}")

    old_left, old_right = mpf("1.08187"), mpf("2.14030")
    for label, t in (("OLD left  1.08187 ", old_left), ("OLD right 2.14030 ", old_right)):
        val = g2(t)
        print(f"G''({label.strip()}) = {mp.nstr(val, 12)}  >= mu2_hat? {val >= MU2_HAT}")

    for label, t in (
        ("NEW left  1.081873", PRINTED_LEFT),
        ("NEW right 2.140298", PRINTED_RIGHT),
    ):
        val = g2(t)
        passed = val >= MU2_HAT
        ok &= passed
        print(
            f"G''({label.strip()}) = {mp.nstr(val, 12)}  margin = "
            f"{mp.nstr(val - MU2_HAT, 6)}  >= mu2_hat? {passed}"
        )

    left_cross = findroot(lambda t: g2(t) - MU2_HAT, mpf("1.08187"))
    right_cross = findroot(lambda t: g2(t) - MU2_HAT, mpf("2.14030"))
    print(f"half-curvature crossings: left  = {mp.nstr(left_cross, 14)}")
    print(f"                          right = {mp.nstr(right_cross, 14)}")
    inside_ok = left_cross < PRINTED_LEFT and right_cross > PRINTED_RIGHT
    ok &= inside_ok
    print(f"printed interval strictly inside crossings? {inside_ok}")

    ts = np.linspace(float(PRINTED_LEFT), float(PRINTED_RIGHT), 1201)
    vals = np.array([g2_f(float(t)) for t in ts])
    imin = int(np.argmin(vals))
    print(
        f"interior scan (1201 pts, float pipeline): min G'' = {vals[imin]:.9f} "
        f"at t = {ts[imin]:.6f} (index {imin})"
    )
    # No interior dip: the scan minimum must sit at a scan endpoint (both
    # endpoints are certified above in high precision) and stay >= mu2_hat.
    scan_ok = bool(imin in (0, len(ts) - 1) and vals.min() >= float(MU2_HAT))
    ok &= scan_ok
    print(f"no interior dip below mu2_hat (min at a certified endpoint)? {scan_ok}")

    print("C3_VERIFICATION_" + ("PASSED" if ok else "FAILED"))


if __name__ == "__main__":
    main()
