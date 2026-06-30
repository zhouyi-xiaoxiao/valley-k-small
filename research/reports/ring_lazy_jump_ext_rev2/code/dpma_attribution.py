#!/usr/bin/env python3
# wrapper-report-id: ring_lazy_jump_ext_rev2
"""Feature-resolved mode attribution for representative double-peak cases.

For each representative (N, beta, d):
  - truncation certificates k_eps(feature): minimal top-K modes (descending
    s ordering) reproducing F at the feature times to 1% / 0.1%
  - mode-1 vs rest split of F at (t1, t_valley, t2)
  - two-route mass split: cumulative mass before/after the valley vs the
    closed form pi_sc = rho/(a+L)
Writes artifacts/tables/dpma_attribution.csv and prints a summary.
"""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

from shortcut_double_peak_mode_attribution import Q_DEFAULT, evaluate


def kmin(F, spec, t, tol):
    order = np.argsort(spec.lams)[::-1]
    lam, kap = spec.lams[order], spec.kappas[order]
    target = F[t - 1]
    acc = 0.0
    for k in range(len(lam)):
        acc += kap[k] * lam[k] ** (t - 1)
        if abs(acc - target) <= tol * abs(target):
            return k + 1
    return len(lam)


def main():
    q = Q_DEFAULT
    cases = [
        (100, 0.002, 4), (100, 0.01, 4), (100, 0.025, 4),
        (200, 0.001, 4), (200, 0.005, 4),
        (100, 0.01, 3), (100, 0.01, 5),
    ]
    rows = []
    for N, beta, d in cases:
        L = N // 2
        rho = L - d
        n0 = (L + d) % N
        spec, F, f = evaluate(N, q, beta, n0)
        if f.t2 is None:
            print(f"N={N} beta={beta} d={d}: not double-peaked, skipping")
            continue
        order = np.argsort(spec.lams)[::-1]
        lam, kap = spec.lams[order], spec.kappas[order]
        mode1 = lambda t: kap[0] * lam[0] ** (t - 1)
        a = q / (beta * (1 - q))
        pi = rho / (a + L)
        mass_before = float(F[: f.t_valley].sum())
        mass_after = float(F[f.t_valley:].sum()) + f.survival_left
        row = dict(
            N=N, beta=beta, d=d, t1=f.t1, tv=f.t_valley, t2=f.t2,
            k1pct_t1=kmin(F, spec, f.t1, 0.01),
            k1pct_tv=kmin(F, spec, f.t_valley, 0.01),
            k1pct_t2=kmin(F, spec, f.t2, 0.01),
            k01pct_t2=kmin(F, spec, f.t2, 0.001),
            mode1_share_t1=mode1(f.t1) / F[f.t1 - 1],
            mode1_share_tv=mode1(f.t_valley) / F[f.t_valley - 1],
            mode1_share_t2=mode1(f.t2) / F[f.t2 - 1],
            mass_before_valley=mass_before,
            pi_sc=pi,
            mass_after_valley=mass_after,
            one_minus_pi=1 - pi,
        )
        rows.append(row)
        print(f"N={N} beta={beta} d={d}: t1={f.t1} tv={f.t_valley} t2={f.t2} | "
              f"k_1%: t1={row['k1pct_t1']} tv={row['k1pct_tv']} t2={row['k1pct_t2']} | "
              f"mode1 share: t1={row['mode1_share_t1']:.3f} tv={row['mode1_share_tv']:.3f} "
              f"t2={row['mode1_share_t2']:.3f} | mass<valley={mass_before:.4f} vs pi_sc={pi:.4f}",
              flush=True)
    p = Path(__file__).resolve().parents[1] / "artifacts" / "tables" / "dpma_attribution.csv"
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    print("wrote", p)


if __name__ == "__main__":
    main()
