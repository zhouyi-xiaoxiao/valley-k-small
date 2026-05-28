#!/usr/bin/env python3
"""Generate one exact target-channel decomposition example for ring_two_target."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys


def _ensure_vkcore_on_path() -> None:
    here = Path(__file__).resolve()
    for parent in here.parents:
        candidate = parent / "packages" / "vkcore" / "src"
        if candidate.exists():
            sys.path.insert(0, str(candidate))
            return


_ensure_vkcore_on_path()

from vkcore.peaks import classify_distribution_shape  # noqa: E402
from vkcore.plot_style import apply_research_plot_style  # noqa: E402
from vkcore.ring.two_target import (  # noqa: E402
    RingTwoTargetConfig,
    exact_two_target_fpt,
    save_decomposition_csv,
    validate_result,
)


def _positive_xy(t, y):
    mask = y > 0
    return t[mask], y[mask]


def plot_decomposition(path: Path, result) -> None:
    import matplotlib.pyplot as plt

    apply_research_plot_style()
    path.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(7.0, 4.4))
    for label, values, color in [
        ("total", result.f_total, "black"),
        ("target1 channel", result.f_target1, "#1f77b4"),
        ("target2 channel", result.f_target2, "#d62728"),
    ]:
        x, y = _positive_xy(result.t, values)
        ax.plot(x, y, label=label, color=color)

    shape = classify_distribution_shape(result.f_total).classification
    cfg = result.config
    ax.set_title(f"Exact channel decomposition ({shape})")
    ax.set_xlabel("first-passage time t")
    ax.set_ylabel("probability")
    ax.set_yscale("log")
    ax.legend(frameon=False)
    ax.text(
        0.98,
        0.96,
        f"L={cfg.L}, start={cfg.start}, targets=({cfg.target1},{cfg.target2})",
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=11,
    )
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-steps", type=int, default=3000)
    parser.add_argument("--eps-survival", type=float, default=1e-12)
    parser.add_argument(
        "--csv",
        type=Path,
        default=None,
        help="Output CSV path. Defaults to artifacts/outputs/representative_channel_decomposition.csv.",
    )
    parser.add_argument(
        "--figure",
        type=Path,
        default=None,
        help="Output figure path. Defaults to artifacts/figures/representative_channel_decomposition.pdf.",
    )
    args = parser.parse_args()

    report_dir = Path(__file__).resolve().parents[1]
    csv_path = args.csv or report_dir / "artifacts" / "outputs" / "representative_channel_decomposition.csv"
    figure_path = args.figure or report_dir / "artifacts" / "figures" / "representative_channel_decomposition.pdf"

    cfg = RingTwoTargetConfig(
        L=20,
        K=2,
        q=2.0 / 3.0,
        drift=0.6,
        start=0,
        target1=18,
        target2=10,
        max_steps=args.max_steps,
        eps_survival=args.eps_survival,
    )
    result = exact_two_target_fpt(cfg)
    errors = validate_result(result)
    save_decomposition_csv(csv_path, result)
    plot_decomposition(figure_path, result)

    for key, value in errors.items():
        print(f"{key}={value:.17g}")
    print(f"csv={csv_path}")
    print(f"figure={figure_path}")


if __name__ == "__main__":
    main()
