#!/usr/bin/env python3
# wrapper-report-id: ring_lazy_jump_ext_rev2
"""Non-antipodal shortcut u != N/2: mode-selective laws and peak structure.

Generalized laws (path representation; transient block = Dirichlet path
1..N-1 with extra killing lam = beta(1-q) at site u, flux to v from sites
1 and N-1 plus the shortcut edge):

  G1  delta s_k = -beta(1-q) * (2/N) * sin^2(k pi u / N) + O(beta^2)
      (first-order rank-one perturbation; antipodal case: sin^2 = 1 for odd
       k, 0 for even k -> the uniform-shift/frozen split)
  G2  pi_sc = lam*G0(j0,u) / (1 + lam*G0(u,u)),
      G0(i,j) = (2/q) * min(i,j) * (N - max(i,j)) / N
      (Dirichlet-path Green function at z=1; antipodal: rho/(a+L))

Exploration: start near a non-antipodal u creates THREE routes (capture,
short arc, long arc) -> possible triple-peak F(t).
Writes artifacts/tables/dpma_general_u.txt (+ example curve CSV).
"""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

from shortcut_double_peak_mode_attribution import Q_DEFAULT, detect_peaks

q = Q_DEFAULT
OUT = []


def say(s=""):
    print(s, flush=True)
    OUT.append(s)


def general_block(N: int, beta: float, u: int):
    n = N - 1
    lam = beta * (1.0 - q)
    A = np.zeros((n, n))
    b = np.zeros(n)
    for i in range(1, N):
        k = i - 1
        stay = 1.0 - q
        if i == u:
            stay = (1.0 - beta) * (1.0 - q)
            b[k] += lam
        A[k, k] = stay
        for j in (i - 1, i + 1):
            if j % N == 0:
                b[k] += q / 2.0
            else:
                A[k, (j % N) - 1] += q / 2.0
    return A, b


def F_of(N, beta, u, j0, tmax=None):
    A, b = general_block(N, beta, u)
    w, V = np.linalg.eigh(A)
    order = np.argsort(w)[::-1]
    w, V = w[order], V[:, order]
    kap = V[j0 - 1, :] * (V.T @ b)
    s1 = float(w.max())
    tmax = tmax or int(min(2_000_000, max(2000, 40 / (1 - s1))))
    ts = np.arange(1, tmax + 1, dtype=float)
    sign = np.sign(w); sign[sign == 0] = 1.0
    loga = np.minimum(np.log(np.maximum(np.abs(w), 1e-300)), 0.0)
    F = np.zeros(tmax)
    for lo in range(0, tmax, 200000):
        hi = min(lo + 200000, tmax)
        tt = ts[lo:hi] - 1.0
        mag = np.exp(np.outer(tt, loga))
        sgn = np.where((tt[:, None].astype(int) % 2 == 0), 1.0, sign[None, :])
        F[lo:hi] = (mag * sgn) @ kap
    csum = np.cumsum(F)
    idx = int(np.searchsorted(csum, 1.0 - 1e-13))
    return (w, kap, F[: idx + 1] if idx + 1 < tmax else F)


def main():
    say("=" * 76)
    say("G1: mode-selective first-order shift, u = N/4 (N=160, k = 1..6)")
    say("=" * 76)
    N, u = 160, 40
    A0, _ = general_block(N, 0.0, u)
    w0 = np.sort(np.linalg.eigvalsh(A0))[::-1]
    for beta in (1e-5, 1e-4):
        A1, _ = general_block(N, beta, u)
        w1 = np.sort(np.linalg.eigvalsh(A1))[::-1]
        ks = np.arange(1, 7)
        pred = -beta * (1 - q) * (2.0 / N) * np.sin(ks * np.pi * u / N) ** 2
        got = w1[:6] - w0[:6]
        ratio = got / np.where(np.abs(pred) != 0, pred, np.nan)
        items = []
        for g, r, pp in zip(got, ratio, pred):
            items.append(f"frozen(|shift|={abs(g):.1e})" if pp == 0 else f"{r:.6f}")
        say(f"  beta={beta:.0e}: shift ratios got/pred = " + ", ".join(items))
        say(f"    (sin^2(k pi u/N) = "
            + ", ".join(f"{np.sin(k*np.pi*u/N)**2:.3f}" for k in ks) + ")")

    say(); say("=" * 76)
    say("G2: general capture law pi_sc = lam G0(j0,u)/(1+lam G0(u,u))")
    say("=" * 76)
    for (N2, u2, j02, beta2) in ((160, 40, 45, 0.01), (160, 40, 35, 0.02),
                                 (200, 130, 137, 0.005), (100, 25, 28, 0.05)):
        A, b = general_block(N2, beta2, u2)
        lam = beta2 * (1 - q)
        # exact: solve (I-A)^T occupation, or directly: pi = lam * [(I-A)^{-1}]_{j0,u}
        Ginv = np.linalg.solve(np.eye(N2 - 1) - A, np.eye(N2 - 1))
        pi_exact = lam * Ginv[j02 - 1, u2 - 1]
        G0 = lambda i, j: (2.0 / q) * min(i, j) * (N2 - max(i, j)) / N2
        pi_pred = lam * G0(j02, u2) / (1 + lam * G0(u2, u2))
        say(f"  N={N2} u={u2} j0={j02} beta={beta2}: exact={pi_exact:.10f} "
            f"closed-form={pi_pred:.10f}  |diff|={abs(pi_exact-pi_pred):.2e}")

    say(); say("=" * 76)
    say("Triple-peak exploration: u = N/4, start j0 = u + d")
    say("=" * 76)
    found = []
    # twelve three-timescale configurations: u = N/4, N/8, N/12, N/16
    configs = [
        (200, 4, 3, 0.004), (200, 4, 3, 0.01), (200, 4, 3, 0.02),
        (200, 4, 4, 0.01), (300, 4, 3, 0.006), (300, 4, 4, 0.003),
        (320, 8, 3, 0.003), (320, 8, 3, 0.01), (320, 8, 3, 0.03),
        (480, 8, 3, 0.005), (320, 16, 3, 0.01), (480, 12, 4, 0.008),
    ]
    for (N3, ufrac, d3, beta3) in configs:
        u3 = N3 // ufrac
        w, kap, F = F_of(N3, beta3, u3, u3 + d3)
        peaks = detect_peaks(F)
        # significant peaks: above 1% of global max
        sig = [int(p) + 1 for p in peaks if F[p] >= 0.01 * F[peaks].max()]
        tsr = f"1:{sig[1]//max(sig[0],1)}" if len(sig) >= 2 else "-"
        say(f"  N={N3} u=N/{ufrac}={u3} d={d3} beta={beta3}: {len(peaks)} strict peaks, "
            f"significant (>=1% of max): {sig[:6]}  (peak-time ratio {tsr})")
        if len(sig) >= 3:
            found.append((N3, u3, d3, beta3, sig, F))
    if found:
        N3, u3, d3, beta3, sig, F = found[0]
        say(f"  TRIPLE-PEAK candidate: N={N3}, u={u3}, d={d3}, beta={beta3}, peaks at t={sig[:3]}")
        p = Path(__file__).resolve().parents[1] / "artifacts" / "data" / "dpma_triple_peak_example.csv"
        ts = np.arange(1, len(F) + 1)
        keep = np.unique(np.round(np.logspace(0, np.log10(len(F)), 2500)).astype(int)) - 1
        with p.open("w", newline="") as fh:
            wcsv = csv.writer(fh); wcsv.writerow(["t", "F"])
            for i in keep:
                wcsv.writerow([int(ts[i]), float(F[i])])
        say(f"  example curve written to {p}")

    out = Path(__file__).resolve().parents[1] / "artifacts" / "tables" / "dpma_general_u.txt"
    out.write_text("\n".join(OUT) + "\n")
    say(f"wrote {out}")


if __name__ == "__main__":
    main()
