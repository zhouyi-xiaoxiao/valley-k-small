#!/usr/bin/env python3
"""Generate the claim-safe model-and-fold schematic used in the main text."""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, FancyArrowPatch, Rectangle
from vkcore.plotting import enforce_publication_graphics
from vkcore.provenance import build_artifact_manifest, write_manifest

HERE = Path(__file__).resolve()
REPORT = HERE.parents[1]
REPO = HERE.parents[4]
FIGURES = REPORT / "artifacts" / "figures"
DATA = REPORT / "artifacts" / "data"
FIGURES.mkdir(parents=True, exist_ok=True)
DATA.mkdir(parents=True, exist_ok=True)

BLUE = "#2F6B9A"
ORANGE = "#D7812A"
INK = "#20252B"
GREY = "#7A828A"
LIGHT_BLUE = "#DCEAF3"
LIGHT_ORANGE = "#F6E4D0"


def _panel_a(ax: plt.Axes) -> None:
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.add_patch(Rectangle((0.06, 0.13), 0.88, 0.52, fill=False, ec=GREY, lw=1.2))
    x1 = np.array([0.66, 0.55])
    x2 = np.array([0.49, 0.43])
    a = 0.19
    ax.add_patch(Circle(x1, 0.035, fc=BLUE, ec=INK, lw=0.8))
    ax.add_patch(Circle(x2, 0.035, fc=ORANGE, ec=INK, lw=0.8))
    ax.add_patch(Circle(x2, a, fill=False, ec=ORANGE, ls=(0, (4, 3)), lw=1.3))
    ax.plot([x2[0], x1[0]], [x2[1], x1[1]], color=INK, lw=1.0)
    ax.text(x1[0] + 0.045, x1[1] + 0.015, r"$X_1(t)$", color=BLUE, fontsize=9)
    ax.text(x2[0] - 0.17, x2[1] - 0.02, r"$X_2(t)$", color=ORANGE, fontsize=9)
    ax.text(0.70, 0.50, r"$|r|<a$", color=INK, fontsize=9)
    # Use full-size Unicode indices here: at journal width, nested MathText
    # scripts in this dense schematic would otherwise fall below 5 pt.
    ax.text(0.08, 0.88, "r = X₁ − X₂", color=INK, fontsize=8.5)
    ax.text(
        0.08,
        0.79,
        "R = (D₂X₁ + D₁X₂)/(D₁ + D₂)",
        color=INK,
        fontsize=8.5,
    )
    ax.text(
        0.08,
        0.70,
        "C(η) = ηX₁ + (1 − η)X₂; bounded 2D: η = 1/2",
        color=INK,
        fontsize=7.4,
    )
    ax.text(
        0.08,
        0.04,
        "Reflecting domain; contact + catalyst required",
        color=GREY,
        fontsize=7.5,
    )
    ax.set_title("(a) Finite-radius encounter", loc="left", fontsize=10, fontweight="bold")


def _panel_b(ax: plt.Axes) -> None:
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.add_patch(Rectangle((0.08, 0.19), 0.84, 0.55, fill=False, ec=GREY, lw=1.2))
    near = Circle((0.28, 0.48), 0.105, fc=LIGHT_BLUE, ec=BLUE, lw=1.5)
    far = Circle((0.73, 0.48), 0.12, fc=LIGHT_ORANGE, ec=ORANGE, lw=1.5)
    ax.add_patch(near)
    ax.add_patch(far)
    ax.text(0.28, 0.48, r"$C_{\rm near}$", ha="center", va="center", color=BLUE, fontsize=9)
    ax.text(0.73, 0.48, r"$C_{\rm far}$", ha="center", va="center", color=ORANGE, fontsize=9)
    for y, rad in ((0.39, 0.035), (0.57, 0.035)):
        ax.add_patch(Circle((0.12, y), rad, fc=INK, ec=INK, lw=0.9))
    ax.add_patch(FancyArrowPatch((0.15, 0.51), (0.25, 0.51), arrowstyle="->", mutation_scale=9, color=BLUE, lw=1.2))
    ax.add_patch(FancyArrowPatch((0.16, 0.39), (0.68, 0.42), connectionstyle="arc3,rad=-0.25", arrowstyle="->", mutation_scale=9, color=ORANGE, lw=1.2))
    ax.text(0.20, 0.63, "early channel", color=BLUE, fontsize=8)
    ax.text(0.47, 0.28, "late channel", color=ORANGE, fontsize=8)
    ax.text(
        0.08,
        0.08,
        "Kₐ(η) = Σⱼ κⱼ 1[Cⱼ](C(η)) 1[|r| < a]",
        color=INK,
        fontsize=8.5,
    )
    ax.set_title("(b) Pattern selects streams", loc="left", fontsize=10, fontweight="bold")


def _gig_shape(t: np.ndarray, a: float, b: float, p: float) -> np.ndarray:
    y = t ** (-p) * np.exp(-a / t - b * t)
    return y / np.trapezoid(y, t)


def _panel_c(ax: plt.Axes) -> None:
    t = np.linspace(0.08, 22.0, 1600)
    early = _gig_shape(t, 0.9, 0.42, 2.0)
    late = _gig_shape(t, 21.0, 0.08, 1.5)
    early_weight = 0.14
    late_weight = 1.0 - early_weight
    total = early_weight * early + late_weight * late
    ax.plot(t, total, color=INK, lw=1.8, label=r"$f=f_{\rm near}+f_{\rm far}$")
    ax.plot(t, early_weight * early, color=BLUE, lw=1.3, ls="--", label=r"$f_{\rm near}$")
    ax.plot(t, late_weight * late, color=ORANGE, lw=1.3, ls="-.", label=r"$f_{\rm far}$")
    ax.set_xlim(0, 22)
    ax.set_ylim(bottom=0)
    ax.set_xticks([0, 5, 10, 15, 20])
    ax.set_xlabel("reaction time $t$", fontsize=8)
    ax.set_ylabel("density (schematic)", fontsize=8)
    ax.tick_params(labelsize=7)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, fontsize=7, loc="upper right")
    ax.text(0.02, 0.03, "not fitted data", transform=ax.transAxes, color=GREY, fontsize=6.8)
    ax.set_title("(c) Channel mixture", loc="left", fontsize=10, fontweight="bold")


def _panel_d(ax: plt.Axes) -> None:
    theta = np.linspace(-1.25, 1.25, 400)
    t0 = 0.78 * np.ones_like(theta)
    branch = np.sqrt(np.clip(theta, 0, None))
    ax.plot(theta, t0, color=INK, lw=1.5)
    positive = theta >= 0
    ax.plot(theta[positive], t0[positive] + 0.45 * branch[positive], color=BLUE, lw=1.6)
    ax.plot(theta[positive], t0[positive] - 0.45 * branch[positive], color=ORANGE, lw=1.6)
    ax.scatter([0], [0.78], s=28, facecolor="white", edgecolor=INK, zorder=3)
    ax.axvline(0, color=GREY, lw=0.8, ls=":")
    ax.text(0.02, 0.82, r"$f_t=f_{tt}=0$", transform=ax.transAxes, fontsize=8.5, color=INK)
    ax.text(0.52, 0.16, r"$\Delta t\propto|\theta-\theta_*|^{1/2}$", transform=ax.transAxes, fontsize=8, color=INK)
    ax.text(
        0.04,
        0.55,
        "one critical point",
        transform=ax.transAxes,
        color=GREY,
        fontsize=7.5,
        ha="left",
    )
    ax.text(0.82, 1.18, "max", color=BLUE, fontsize=7.5)
    ax.text(0.82, 0.37, "min", color=ORANGE, fontsize=7.5)
    ax.set_xlabel(r"physical control $\theta-\theta_*$", fontsize=8)
    ax.set_ylabel("critical-point time", fontsize=8)
    ax.set_yticks([])
    ax.tick_params(axis="x", labelsize=7)
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_title("(d) Generic modality fold", loc="left", fontsize=10, fontweight="bold")


def main() -> None:
    plt.rcParams.update({"font.family": "DejaVu Sans", "mathtext.fontset": "dejavusans"})
    fig, axes = plt.subplots(2, 2, figsize=(7.2, 5.8))
    _panel_a(axes[0, 0])
    _panel_b(axes[0, 1])
    _panel_c(axes[1, 0])
    _panel_d(axes[1, 1])
    fig.suptitle("Spatial encounter channels and their modality boundary", fontsize=12, color=INK)
    fig.subplots_adjust(
        left=0.10,
        right=0.97,
        bottom=0.09,
        top=0.88,
        wspace=0.34,
        hspace=0.46,
    )
    pdf = FIGURES / "encounter_model_and_fold.pdf"
    png = FIGURES / "encounter_model_and_fold.png"
    enforce_publication_graphics(fig)
    fig.savefig(pdf)
    fig.savefig(png, dpi=240)
    plt.close(fig)

    manifest = build_artifact_manifest(
        repo_root=REPO,
        generator=str(HERE.relative_to(REPO)),
        command=[sys.executable, str(HERE.relative_to(REPO))],
        model_spec={
            "figure_role": "claim-safe conceptual schematic",
            "data_status": "panels c-d are schematic and are labelled as such",
            "coordinate_definition": "declared affine C_eta; schematic notes bounded 2D midpoint eta=1/2",
        },
        dependencies=[
            REPO / "packages" / "vkcore" / "src" / "vkcore" / "plotting.py",
            REPO / "packages" / "vkcore" / "src" / "vkcore" / "provenance.py",
        ],
        outputs=[pdf, png],
    )
    write_manifest(DATA / "encounter_model_and_fold.manifest.json", manifest)


if __name__ == "__main__":
    main()
