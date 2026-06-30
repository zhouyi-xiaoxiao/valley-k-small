#!/usr/bin/env python3
# wrapper-report-id: ring_lazy_jump_ext_rev2
"""(N, beta) phase scan of the C.2 clear-double-peak classifier per start
offset d = ring distance from the shortcut source u.  Writes a tidy CSV of
classifier flags plus continuous diagnostics for every cell.

Usage:
  dpma_phase_scan.py --out artifacts/data/dpma_phase_scan.csv \
      [--pilot] [--ds 3 4 5] [--q 0.6666666666666666]
"""

from __future__ import annotations

import argparse
import csv
import json
import time
from pathlib import Path

import numpy as np

from shortcut_double_peak_mode_attribution import (
    Q_DEFAULT, Spectral, classify, pmf_from_modes, tmax_for,
    transient_block, SURVIVAL_EPS,
)


def scan(Ns, betas, ds, q, out_csv: Path):
    rows = []
    t0 = time.time()
    for N in Ns:
        A, b = None, None
        for beta in betas:
            A, b = transient_block(N, q, beta)
            w, V = np.linalg.eigh(A)
            order = np.argsort(w)[::-1]
            w, V = w[order], V[:, order]
            Vb = V.T @ b
            tmax = tmax_for(w)
            ku = N // 2 - 1
            for d in ds:
                n0 = (N // 2 + d) % N
                k0 = n0 - 1
                occ = V[k0, :] * V[ku, :]
                spec = Spectral(w, V[k0, :] * Vb, occ, N, q, beta, n0)
                F = pmf_from_modes(spec.lams, spec.kappas, tmax)
                csum = np.cumsum(F)
                idx = int(np.searchsorted(csum, 1.0 - SURVIVAL_EPS))
                if idx + 1 < len(F):
                    F = F[: idx + 1]
                feats = classify(F, spec)
                rows.append(dict(N=N, beta=beta, d=d, q=q,
                                 clear=int(feats.clear_double),
                                 n_peaks=feats.n_peaks,
                                 t1=feats.t1, h1=feats.h1,
                                 t2=feats.t2, h2=feats.h2,
                                 t_valley=feats.t_valley, h_valley=feats.h_valley,
                                 ratio_secondary=feats.ratio_secondary,
                                 hratio=feats.hratio, valley_frac=feats.valley_frac,
                                 s1=feats.s1, B1=feats.B1,
                                 tail_tstar=feats.tail_tstar,
                                 capture_prob=feats.capture_prob))
        print(f"N={N} done ({time.time()-t0:.1f}s, {len(rows)} rows)", flush=True)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="") as fh:
        wcsv = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        wcsv.writeheader()
        wcsv.writerows(rows)
    manifest = dict(Ns=list(map(int, Ns)), betas=[float(b) for b in betas],
                    ds=list(map(int, ds)), q=q,
                    classifier="C.2 clear-double-peak (first-two-peaks-in-time, t=1 boundary candidate, h_min=1e-12, min_ratio=0.01 vs largest, sep>=10, hratio in [0.1,10], valley<=0.8*min)",
                    survival_eps=SURVIVAL_EPS, generated_by=__file__)
    out_csv.with_suffix(".manifest.json").write_text(json.dumps(manifest, indent=2))
    print(f"wrote {out_csv} ({len(rows)} rows)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path,
                    default=Path(__file__).resolve().parents[1] / "artifacts" / "data" / "dpma_phase_scan.csv")
    ap.add_argument("--pilot", action="store_true")
    ap.add_argument("--ds", type=int, nargs="+", default=[3, 4, 5])
    ap.add_argument("--q", type=float, default=Q_DEFAULT)
    args = ap.parse_args()
    if args.pilot:
        Ns = [20, 40, 60, 100, 140, 200]
        betas = sorted(set(np.round(np.logspace(-4, -1, 16), 6).tolist()))
    else:
        Ns = [16, 20, 24, 30, 36, 44, 52, 60, 70, 80, 100, 120, 140, 170, 200, 240]
        betas = sorted(set(np.round(np.logspace(-4.0, -0.7, 34), 6).tolist()))
    scan(Ns, betas, args.ds, args.q, args.out)


if __name__ == "__main__":
    main()
