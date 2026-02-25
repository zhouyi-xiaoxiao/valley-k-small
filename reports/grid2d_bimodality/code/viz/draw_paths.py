#!/usr/bin/env python3
"""Representative trajectory drawing utilities."""

from __future__ import annotations

from typing import Iterable, Tuple

import numpy as np
from matplotlib.axes import Axes
from matplotlib.patches import FancyArrowPatch


def plot_trajectory(
    ax: Axes,
    traj: np.ndarray,
    *,
    color: str = "#fdae61",
    lw: float = 2.2,
    alpha: float = 0.9,
    arrow_every: int = 20,
    label: str | None = None,
) -> None:
    if traj.size == 0:
        return
    xs = traj[:, 0]
    ys = traj[:, 1]
    ax.plot(xs, ys, color=color, lw=lw, alpha=alpha, label=label, zorder=4)

    if arrow_every > 0:
        for i in range(0, len(xs) - 1, arrow_every):
            x0, y0 = xs[i], ys[i]
            x1, y1 = xs[i + 1], ys[i + 1]
            if x0 == x1 and y0 == y1:
                continue
            arrow = FancyArrowPatch(
                (x0, y0),
                (x1, y1),
                arrowstyle="-|>",
                mutation_scale=10,
                lw=lw * 0.6,
                color=color,
                alpha=alpha,
                zorder=5,
            )
            ax.add_patch(arrow)
