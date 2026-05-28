#!/usr/bin/env python3
"""Generate aligned shortcut-ring geometry figures for related reports.

The final brief and the earlier fixed-shortcut meeting report use slightly
different shortcut conventions. This script keeps the conventions separate but
uses one visual style for both ring schematics.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch

ROOT = Path(__file__).resolve().parents[4]
FINAL_FIGURES = (
    ROOT / "research" / "reports" / "final_multitimescale_fpt_encounter" / "artifacts" / "figures"
)
REV2_FIGURES = ROOT / "research" / "reports" / "ring_lazy_jump_ext_rev2" / "artifacts" / "figures"


def plot_shortcut_ring_geometry(
    *,
    out_pdf: Path,
    out_png: Path | None = None,
    title: str,
    N: int,
    start_sites: list[int],
    source: int,
    destination: int,
    target: int,
    show_start_sweep: bool,
    show_probability_rule: bool,
) -> None:
    theta = np.linspace(0.0, 2.0 * np.pi, int(N), endpoint=False)
    x = np.cos(theta)
    y = np.sin(theta)

    def xy(site: int) -> tuple[float, float]:
        idx = (int(site) - 1) % int(N)
        return float(x[idx]), float(y[idx])

    fig, ax = plt.subplots(figsize=(6.4, 6.4), dpi=180)
    ax.plot(np.r_[x, x[0]], np.r_[y, y[0]], color="#c9c9c9", linewidth=1.2, zorder=1)
    ax.scatter(x, y, s=12, color="#d9d9d9", edgecolor="white", linewidth=0.25, zorder=2)

    starts = np.asarray([xy(site) for site in start_sites], dtype=float)
    start_label = (
        rf"$n_0={start_sites[0]}$"
        if len(start_sites) == 1
        else rf"$n_0={start_sites[0]},\ldots,{start_sites[-1]}$"
    )
    ax.scatter(
        starts[:, 0],
        starts[:, 1],
        s=72,
        facecolor="#fff7bc",
        edgecolor="#d89c00",
        linewidth=1.2,
        zorder=4,
        label=start_label,
    )

    ux, uy = xy(source)
    vx, vy = xy(destination)
    tx, ty = xy(target)

    ax.scatter(
        [ux],
        [uy],
        s=130,
        color="#264653",
        edgecolor="white",
        linewidth=0.9,
        zorder=7,
        label=rf"$u={source}$",
    )
    ax.scatter(
        [vx],
        [vy],
        s=145,
        marker="*",
        color="#e76f51",
        edgecolor="white",
        linewidth=0.7,
        zorder=8,
        label=rf"$v={destination}$",
    )
    if target != destination:
        ax.scatter(
            [tx],
            [ty],
            s=120,
            marker="s",
            color="#2a9d8f",
            edgecolor="white",
            linewidth=0.8,
            zorder=8,
            label=rf"target={target}",
        )

    shortcut_arrow = FancyArrowPatch(
        (ux, uy),
        (vx, vy),
        connectionstyle="arc3,rad=0.28",
        arrowstyle="-|>",
        mutation_scale=18,
        linewidth=2.1,
        color="#b00020",
        shrinkA=13,
        shrinkB=13,
        zorder=6,
    )
    ax.add_patch(shortcut_arrow)

    ax.text(0.02, 0.25, "directed shortcut", ha="center", va="bottom", color="#b00020", fontsize=10)
    if show_probability_rule:
        ax.text(0.02, 0.13, r"$P(u\to v)=\beta(1-q)$", ha="center", va="top", color="#b00020", fontsize=10)
    else:
        ax.text(0.02, 0.13, rf"$u={source}\to v={destination}$", ha="center", va="top", color="#b00020", fontsize=10)

    if target == destination:
        central_note = rf"$v={destination}$ is absorbing target"
    else:
        central_note = rf"target={target}, shortcut endpoint $v={destination}$"
    ax.text(
        -0.05,
        -0.18,
        central_note,
        ha="center",
        va="center",
        color="#b00020",
        fontsize=10,
        bbox={"boxstyle": "round,pad=0.2", "facecolor": "white", "edgecolor": "none", "alpha": 0.82},
    )

    if show_start_sweep:
        labels = [
            (start_sites[0], str(start_sites[0]), (0.10, 0.08)),
            (source, rf"u={source}", (0.10, 0.09)),
            (destination, rf"v={destination} / target", (-0.48, -0.02)),
        ]
    else:
        labels = [
            (start_sites[0], rf"$n_0={start_sites[0]}$", (0.11, 0.08)),
            (source, rf"u={source}", (0.10, 0.09)),
            (target, rf"target={target}", (-0.54, -0.06)),
            (destination, rf"v={destination}", (-0.08, -0.16)),
        ]

    for site, label, offset in labels:
        px, py = xy(site)
        ax.text(px + offset[0], py + offset[1], label, fontsize=9, weight="bold")

    ax.set_title(title, fontsize=12)
    ax.set_aspect("equal")
    ax.set_axis_off()
    ax.set_xlim(-1.22, 1.22)
    ax.set_ylim(-1.22, 1.22)
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.04), ncol=3, frameon=False, fontsize=8)
    fig.tight_layout()

    out_pdf.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_pdf, bbox_inches="tight")
    if out_png is not None:
        fig.savefig(out_png, dpi=220, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    plot_shortcut_ring_geometry(
        out_pdf=FINAL_FIGURES / "shortcut_ring_geometry_reference_6to52.pdf",
        out_png=FINAL_FIGURES / "shortcut_ring_geometry_reference_6to52.png",
        title="N=100 shortcut ring: u=6 -> v=52, target=51",
        N=100,
        start_sites=[1],
        source=6,
        destination=52,
        target=51,
        show_start_sweep=False,
        show_probability_rule=False,
    )

    # Keep the earlier report's convention but align the style with the final brief.
    plot_shortcut_ring_geometry(
        out_pdf=REV2_FIGURES / "luca_k2_fixed_shortcut_ring_geometry.pdf",
        out_png=REV2_FIGURES / "luca_k2_fixed_shortcut_ring_geometry.png",
        title="N=100, K=2 ring: u=6 -> v=56",
        N=100,
        start_sites=[1, 2, 3, 4, 5, 6],
        source=6,
        destination=56,
        target=56,
        show_start_sweep=True,
        show_probability_rule=True,
    )

    print((FINAL_FIGURES / "shortcut_ring_geometry_reference_6to52.pdf").relative_to(ROOT))
    print((REV2_FIGURES / "luca_k2_fixed_shortcut_ring_geometry.pdf").relative_to(ROOT))


if __name__ == "__main__":
    main()
