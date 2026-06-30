#!/usr/bin/env python3
# wrapper-report-id: ring_lazy_jump_ext_rev2
"""Identify which C.2 condition binds at each refined window edge.

For each (N, d) edge in dpma_boundary_refined.csv, evaluate the five C.2
conditions just OUTSIDE the window (1.5% beyond the edge in beta) and
report which condition(s) fail there.  Writes
artifacts/tables/dpma_binding_conditions.csv
"""

from __future__ import annotations

import csv
from pathlib import Path

from shortcut_double_peak_mode_attribution import (
    Q_DEFAULT, MIN_RATIO, MIN_SEP, HRATIO_LO, HRATIO_HI, VALLEY_FRAC,
    evaluate,
)


def conditions(N, q, beta, d):
    n0 = (N // 2 + d) % N
    _, F, f = evaluate(N, q, beta, n0)
    if f.t2 is None:
        return f, {"two_peaks": False, "ratio_1pct": False, "separation": False,
                   "height_balance": False, "valley_depth": False}
    return f, {
        "two_peaks": True,
        "ratio_1pct": f.ratio_secondary >= MIN_RATIO,
        "separation": (f.t2 - f.t1) >= MIN_SEP,
        "height_balance": HRATIO_LO <= f.hratio <= HRATIO_HI,
        "valley_depth": f.valley_frac <= VALLEY_FRAC,
    }


def main():
    q = Q_DEFAULT
    art = Path(__file__).resolve().parents[1] / "artifacts"
    rows_in = list(csv.DictReader((art / "data" / "dpma_boundary_refined.csv").open()))
    out = []
    for r in rows_in:
        if r["window"] != "1":
            continue
        N, d = int(r["N"]), int(r["d"])
        for edge, mul in (("lower", 1 / 1.015), ("upper", 1.015)):
            beta = float(r[f"beta_{'lo' if edge == 'lower' else 'hi'}"]) * mul
            f, cond = conditions(N, q, beta, d)
            failed = [k for k, v in cond.items() if not v]
            out.append(dict(N=N, d=d, edge=edge, beta_outside=round(beta, 7),
                            failed=";".join(failed) or "none",
                            hratio=round(f.hratio, 4),
                            valley_frac=round(f.valley_frac, 4),
                            ratio_secondary=round(f.ratio_secondary, 5),
                            n_peaks=f.n_peaks))
            print(f"N={N} d={d} {edge}: fails -> {';'.join(failed) or 'none'} "
                  f"(hratio={f.hratio:.3f} vfrac={f.valley_frac:.3f})", flush=True)
    p = art / "tables" / "dpma_binding_conditions.csv"
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0].keys()))
        w.writeheader(); w.writerows(out)
    print("wrote", p)


if __name__ == "__main__":
    main()
