#!/usr/bin/env python3
"""Matplotlib styling for v4 figures."""

from __future__ import annotations

import matplotlib as mpl


def set_style(style: str = "fig3") -> None:
    """Set a consistent paper style for v4 figures."""
    base = {
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "axes.edgecolor": "0.2",
        "axes.linewidth": 1.0,
        "axes.labelsize": 10,
        "axes.titlesize": 11,
        "xtick.labelsize": 8,
        "ytick.labelsize": 8,
        "legend.fontsize": 8,
        "font.size": 10,
        "lines.linewidth": 1.6,
        "lines.markersize": 4.0,
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.02,
        "savefig.facecolor": "white",
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    }

    if style == "fig3":
        base.update(
            {
                "font.family": "DejaVu Sans",
                "figure.figsize": (11.5, 6.8),
            }
        )
    elif style == "paper":
        base.update(
            {
                "font.family": "DejaVu Serif",
                "figure.figsize": (10.5, 6.2),
            }
        )
    else:
        base.update({"font.family": "DejaVu Sans"})

    mpl.rcParams.update(base)
