#!/usr/bin/env python3
# wrapper-report-id: ring_lazy_jump_ext_rev2
"""Fixed-x (= d/N) family scan: is the clear-double-peak window N-invariant
in b = beta(1-q)N/q?  Writes artifacts/data/dpma_rhoN_family_scan.csv
(+ manifest)."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np

from shortcut_double_peak_mode_attribution import Q_DEFAULT, evaluate

q = Q_DEFAULT


def main():
    rows = []
    xs = (0.05, 0.1, 0.2)
    Ns = (60, 80, 120, 160, 240)
    bs = np.logspace(np.log10(0.02), np.log10(2.5), 18)
    for x in xs:
        for N in Ns:
            d = max(1, round(x * N))
            clear_bs = []
            for b in bs:
                beta = q * b / ((1 - q) * N)
                _, F, f = evaluate(N, q, beta, (N // 2 + d) % N)
                rows.append(dict(x=x, N=N, d=d, b=round(float(b), 5), beta=beta,
                                 clear=int(f.clear_double), label=f.label))
                if f.clear_double:
                    clear_bs.append(b)
            win = (f"[{min(clear_bs):.3f}, {max(clear_bs):.3f}] ({len(clear_bs)} pts)"
                   if clear_bs else "none")
            print(f"x={x} N={N} (d={d}): clear b-window {win}", flush=True)
    out = Path(__file__).resolve().parents[1] / "artifacts" / "data" / "dpma_rhoN_family_scan.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    out.with_suffix(".manifest.json").write_text(json.dumps(dict(
        xs=list(xs), Ns=list(Ns), b_grid=[float(b) for b in bs], q=q,
        classifier="C.2 clear-double-peak (first-two-peaks-in-time, t=1 boundary candidate)",
        generated_by=__file__), indent=2))
    print("wrote", out)


if __name__ == "__main__":
    main()
