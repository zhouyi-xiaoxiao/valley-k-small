#!/usr/bin/env python3
"""Generate the corrected pole-geometry figure for Luca's audit note."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
FIG_DIR = ROOT / "figures"


def cheb_t(n: int, x: np.ndarray) -> np.ndarray:
    if n == 0:
        return np.ones_like(x)
    if n == 1:
        return x.copy()
    t0 = np.ones_like(x)
    t1 = x.copy()
    for _ in range(2, n + 1):
        t0, t1 = t1, 2 * x * t1 - t0
    return t1


def cheb_u(n: int, x: np.ndarray) -> np.ndarray:
    if n == 0:
        return np.ones_like(x)
    if n == 1:
        return 2 * x
    u0 = np.ones_like(x)
    u1 = 2 * x
    for _ in range(2, n + 1):
        u0, u1 = u1, 2 * x * u1 - u0
    return u1


def transient_matrix(n_sites: int, q: float, beta: float) -> np.ndarray:
    """Transient matrix for an absorbing target at 0 and shortcut u=N/2 -> 0."""
    if n_sites % 2 != 0:
        raise ValueError("Use an even ring size for the symmetric shortcut case.")
    target = 0
    shortcut_from = n_sites // 2
    transient = [n for n in range(n_sites) if n != target]
    index = {n: i for i, n in enumerate(transient)}
    p = np.zeros((len(transient), len(transient)))
    for n in transient:
        row = index[n]
        stay_mass = 1.0 - q
        if n == shortcut_from:
            stay_mass *= 1.0 - beta
        p[row, row] += stay_mass
        for nbr in ((n - 1) % n_sites, (n + 1) % n_sites):
            if nbr != target:
                p[row, index[nbr]] += q / 2.0
    return p


def perron_root(n_sites: int, q: float, beta: float) -> float:
    eigvals = np.linalg.eigvals(transient_matrix(n_sites, q, beta))
    return float(np.max(np.real(eigvals)))


def main() -> None:
    n_sites = 40
    half = n_sites // 2
    q = 0.5
    beta_example = 0.50
    a = q / (beta_example * (1.0 - q))

    s = np.linspace(0.0, 1.0, 1600)
    y = (s - 1.0 + q) / q
    phi = cheb_t(half, y) * cheb_u(half - 1, y)

    betas = np.linspace(0.0, 1.0, 121)
    roots = np.array([perron_root(n_sites, q, beta) for beta in betas])
    gaps = 1.0 - roots
    invalid_threshold = 2.0 * q / ((1.0 - q) * n_sites)

    plt.rcParams.update(
        {
            "font.size": 9,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "figure.dpi": 160,
        }
    )
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.2), constrained_layout=True)

    ax = axes[0]
    ax.axhline(0.0, color="black", lw=0.8, alpha=0.35)
    ax.plot(s, phi, color="#1f5fbf", lw=1.5, label=r"$\Phi_L(s)=T_L(y)U_{L-1}(y)$")
    ax.axhline(-a, color="#236b3b", lw=1.4, label=r"correct poles: $\Phi_L(s)=-a$")
    ax.axhline(a, color="#9b3a34", lw=1.2, ls="--", label=r"old poles: $\Phi_L(s)=+a$")
    ax.set_xlim(0, 1)
    ax.set_ylim(-22, 22)
    ax.set_xlabel(r"spectral variable $s=1/z$")
    ax.set_ylabel(r"pole geometry function $\Phi_L(s)$")
    ax.set_title("Corrected pole condition")
    ax.text(0.02, 0.93, rf"$N={n_sites}$, $q={q}$, $\beta={beta_example}$", transform=ax.transAxes)
    ax.legend(frameon=False, loc="lower left", fontsize=8)

    ax = axes[1]
    ax.plot(betas, gaps, color="#236b3b", lw=1.8)
    ax.axvline(invalid_threshold, color="#9b3a34", lw=1.2, ls="--")
    ax.text(
        invalid_threshold + 0.015,
        gaps.max() * 0.82,
        r"old threshold",
        color="#9b3a34",
        fontsize=8,
        rotation=90,
        va="top",
    )
    ax.set_xlim(0, 1)
    ax.set_ylim(0, gaps.max() * 1.08)
    ax.set_xlabel(r"shortcut strength $\beta$")
    ax.set_ylabel(r"tail gap $1-\rho(P_\beta)$")
    ax.set_title("Correct killed-chain tail rate")
    ax.text(0.03, 0.93, r"$P_\beta=P_0-\beta(1-q)|u\rangle\langle u|$", transform=ax.transAxes)

    for ext in ("pdf", "png"):
        fig.savefig(FIG_DIR / f"corrected_pole_geometry.{ext}", bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
