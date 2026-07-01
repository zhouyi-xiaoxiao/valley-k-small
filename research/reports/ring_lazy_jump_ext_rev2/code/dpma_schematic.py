#!/usr/bin/env python3
# wrapper-report-id: ring_lazy_jump_ext_rev2
"""Model schematic (Fig. 1) for the directed-shortcut saddle-node manuscript.

Two data-free panels (pure illustration, no numerics):
  (a) lazy ring of N sites: absorbing target v=0, directed shortcut u->v (rate lambda),
      self-loop 1-q, neighbour hops q/2.
  (b) diffusive limit: Brownian motion on [0,1] with absorbing ends and an interior
      delta-sink of strength b at fractional position theta; start at xi.
Writes artifacts/figures/dpma_schematic.{pdf,png}
"""
from __future__ import annotations
import math
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Circle, Arc

OUT = Path(__file__).resolve().parents[1] / "artifacts" / "figures"
OUT.mkdir(parents=True, exist_ok=True)

plt.rcParams.update({
    "font.size": 11,
    "axes.linewidth": 0.8,
    "mathtext.fontset": "cm",
})

fig, (axA, axB) = plt.subplots(1, 2, figsize=(9.2, 4.3))

# ---------------------------------------------------------------- panel (a) ring
axA.set_aspect("equal")
axA.axis("off")
N = 16
R = 1.0
# site index 0 at top, going clockwise
angles = [math.pi / 2 - 2 * math.pi * i / N for i in range(N)]
xs = [R * math.cos(a) for a in angles]
ys = [R * math.sin(a) for a in angles]

u_idx = N // 2  # antipodal source (bottom)
for i in range(N):
    if i == 0:
        c = Circle((xs[i], ys[i]), 0.10, fc="#c1121f", ec="k", zorder=5, lw=1.0)
        axA.add_patch(c)
    elif i == u_idx:
        c = Circle((xs[i], ys[i]), 0.10, fc="#2a9d8f", ec="k", zorder=5, lw=1.0)
        axA.add_patch(c)
    else:
        c = Circle((xs[i], ys[i]), 0.055, fc="white", ec="k", zorder=4, lw=0.8)
        axA.add_patch(c)

# nearest-neighbour hop bonds (thin ring)
for i in range(N):
    j = (i + 1) % N
    axA.plot([xs[i], xs[j]], [ys[i], ys[j]], color="0.6", lw=0.8, zorder=1)

# directed shortcut u -> v (straight chord with arrowhead)
sc = FancyArrowPatch((xs[u_idx], ys[u_idx] + 0.10), (xs[0], ys[0] - 0.10),
                     arrowstyle="-|>", mutation_scale=16, lw=2.0,
                     color="#2a9d8f", zorder=3, connectionstyle="arc3,rad=0.13")
axA.add_patch(sc)

# labels
axA.annotate(r"$v=0$ (absorbing target)", (xs[0], ys[0]), xytext=(xs[0] + 0.06, ys[0] + 0.24),
             ha="left", fontsize=10, color="#c1121f")
axA.annotate(r"$u$ (shortcut source)", (xs[u_idx], ys[u_idx]),
             xytext=(xs[u_idx] - 0.05, ys[u_idx] - 0.30), ha="center", fontsize=10, color="#2a9d8f")
axA.annotate(r"$\lambda=\beta(1-q)$", (0.10, 0.02), xytext=(0.34, 0.05), fontsize=10,
             color="#2a9d8f", ha="left")

# self-loop + hop annotation on a generic site (upper right)
gi = 3
loop = Arc((xs[gi] + 0.12, ys[gi] + 0.12), 0.22, 0.22, angle=0, theta1=-30, theta2=210,
           color="0.35", lw=1.0, zorder=2)
axA.add_patch(loop)
axA.annotate(r"$1-q$", (xs[gi] + 0.20, ys[gi] + 0.24), fontsize=8.5, color="0.35")
axA.annotate(r"$q/2$", ((xs[gi] + xs[gi + 1]) / 2 + 0.02, (ys[gi] + ys[gi + 1]) / 2 + 0.10),
             fontsize=8.5, color="0.45")

axA.set_xlim(-1.5, 1.7)
axA.set_ylim(-1.65, 1.55)
axA.set_title(r"(a) lazy ring, $N$ sites, directed shortcut", fontsize=11)

# ---------------------------------------------------------------- panel (b) continuum
axB.set_aspect("auto")
theta = 0.5
xi = 0.5
# domain line
axB.plot([0, 1], [0, 0], color="k", lw=1.4, zorder=2)
# absorbing walls
for xw, lab in [(0.0, r"$0$"), (1.0, r"$1$")]:
    axB.plot([xw, xw], [-0.34, 0.34], color="#c1121f", lw=2.4, zorder=3)
    axB.annotate(lab, (xw, -0.5), ha="center", fontsize=10)
axB.annotate("absorbing", (0.0, 0.44), ha="center", fontsize=8.5, color="#c1121f")
axB.annotate("absorbing", (1.0, 0.44), ha="center", fontsize=8.5, color="#c1121f")

# delta-sink at theta (downward spike)
axB.annotate("", xy=(theta, -0.62), xytext=(theta, 0.0),
             arrowprops=dict(arrowstyle="-|>", color="#2a9d8f", lw=2.4))
axB.annotate(r"$-\,b\,\delta(x-\theta)$", (theta + 0.02, -0.40), ha="left", fontsize=10,
             color="#2a9d8f")
axB.annotate(r"$\theta$", (theta, 0.14), ha="center", fontsize=10, color="#2a9d8f")

# start xi (if distinct from theta, offset marker; here xi=theta so mark just above)
axB.plot([xi], [0.0], marker="o", ms=7, mfc="#264653", mec="k", zorder=5)
axB.annotate(r"start $\xi$", (xi - 0.03, 0.22), ha="right", fontsize=9.5, color="#264653")

# diffusion arrows
for x0 in (0.22, 0.78):
    axB.annotate("", xy=(x0 + 0.06, 0.0), xytext=(x0 - 0.06, 0.0),
                 arrowprops=dict(arrowstyle="<->", color="0.5", lw=1.0))
axB.annotate(r"$\partial_\tau p=\frac{1}{2} p_{xx}-b\,\delta(x-\theta)\,p$", (0.5, 0.72),
             ha="center", fontsize=10)

axB.set_xlim(-0.12, 1.12)
axB.set_ylim(-0.8, 0.95)
axB.axis("off")
axB.set_title(r"(b) diffusive limit: interval with interior $\delta$-sink", fontsize=11)

fig.tight_layout()
for ext in ("pdf", "png"):
    fig.savefig(OUT / f"dpma_schematic.{ext}", dpi=200, bbox_inches="tight")
print("wrote", OUT / "dpma_schematic.pdf")
