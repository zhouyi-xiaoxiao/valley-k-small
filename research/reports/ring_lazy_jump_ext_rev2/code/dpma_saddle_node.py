#!/usr/bin/env python3
# wrapper-report-id: ring_lazy_jump_ext_rev2
"""Threshold-free existence boundary of the second (around-wave) peak.

The C.2 classifier window is convention-laden.  The INTRINSIC boundary is the
saddle-node bifurcation b_c at which the second interior maximum of the
first-passage density coalesces with the valley and disappears: the double
peak exists (topologically, no thresholds) iff b < b_c.

Computed two independent ways:
  (1) from the exact N->inf master function Phi(x;b)=q sum_j G_j e^{-2 w_j^2 x}
      (tan w=-2w/b): largest b with a (valley, peak) pair on x>0;
  (2) from the EXACT finite-N chain: largest b for which F(t) still has a
      late interior maximum (t>N) preceded by a valley -- pure topology.

Result: b_c(Phi)=3.0764; exact chain brackets [3.05,3.10] for N=400,800,1200
(N-independent), straddling it.  The C.2 plateau b_pl=1.5733 sits at ~51% of
b_c, i.e. the classifier "clear" window is a thresholded sub-interval of the
intrinsic existence region (0, b_c).

Writes artifacts/tables/dpma_saddle_node.txt
"""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np

from dpma_master_function import phi
from shortcut_double_peak_mode_attribution import evaluate, Q_DEFAULT

q = Q_DEFAULT
OUT = []


def say(s=""):
    print(s, flush=True)
    OUT.append(s)


def phi_has_pair(b, xlo=1e-3, xhi=3.0, n=60000):
    xs = np.exp(np.linspace(math.log(xlo), math.log(xhi), n))
    v = phi(xs, b)
    d1 = np.diff(v)
    mx = np.where((d1[:-1] > 0) & (d1[1:] <= 0))[0] + 1
    mn = np.where((d1[:-1] < 0) & (d1[1:] >= 0))[0] + 1
    return (len(mx) > 0 and len(mn) > 0 and mn[0] < mx[-1]), xs, v, mx, mn


def bc_from_phi():
    lo, hi = 1.0, 4.0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if phi_has_pair(mid)[0]:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def exact_has_second_peak(N, b, d=3):
    beta = q * b / ((1 - q) * N)
    _, F, _ = evaluate(N, q, beta, (N // 2 + d) % N)
    F = np.asarray(F, float)
    d1 = np.diff(F)
    mx = [t for t in np.where((d1[:-1] > 0) & (d1[1:] <= 0))[0] + 1 if t > 2 and F[t] > 1e-14]
    mn = [t for t in np.where((d1[:-1] < 0) & (d1[1:] >= 0))[0] + 1 if t > 2]
    late = [t for t in mx if t > N and any(m < t for m in mn)]
    return len(late) >= 1


def main():
    say("=" * 76)
    say("Threshold-free saddle-node boundary b_c of the second peak")
    say("=" * 76)
    b_c = bc_from_phi()
    say(f"  (1) from master function Phi:  b_c = {b_c:.5f}")
    ok, xs, v, mx, mn = phi_has_pair(b_c - 2e-3)
    if len(mx) and len(mn):
        say(f"      coalescence just below b_c: valley x={xs[mn[-1]]:.4f}, "
            f"peak x={xs[mx[-1]]:.4f}  (merge -> saddle-node)")
    say()
    say("  (2) exact finite-N chain (classifier-free; 2nd peak present up to / "
        "gone from):")
    for N in (400, 800, 1200):
        bs = np.arange(2.80, 3.41, 0.05)
        flags = [(b, exact_has_second_peak(N, b)) for b in bs]
        yes = [b for b, t in flags if t]
        no = [b for b, t in flags if not t]
        say(f"      N={N:4d}:  present up to b={max(yes):.2f}, gone from b={min(no):.2f}")
    say()
    say(f"  C.2 plateau b_pl = 1.5733 sits at {100*1.5733/b_c:.1f}% of b_c -> the")
    say("  classifier 'clear' window is a thresholded sub-interval of (0, b_c).")
    say()
    say("  Interpretation: b_c is the intrinsic, convention-free upper boundary;")
    say("  the second peak exists iff b < b_c, dying by a saddle-node where the")
    say("  around-wave maximum annihilates the valley.")

    p = Path(__file__).resolve().parents[1] / "artifacts" / "tables" / "dpma_saddle_node.txt"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("\n".join(OUT) + "\n")
    say(f"\nwrote {p}")


if __name__ == "__main__":
    main()
