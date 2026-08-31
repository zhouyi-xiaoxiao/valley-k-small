import json, csv
import matplotlib
matplotlib.use("Agg")
matplotlib.rcParams["pdf.fonttype"] = 42
matplotlib.rcParams["ps.fonttype"] = 42
import matplotlib.pyplot as plt
import numpy as np

SP = "/private/tmp/claude-502/-Users-ae23069/ee6961d1-72d8-4f2a-ad47-6ff021038957/scratchpad"
OLD = "/private/tmp/claude-502/-Users-ae23069/ee6961d1-72d8-4f2a-ad47-6ff021038957/scratchpad/data_final"
rows = list(csv.DictReader(open(f"{SP}/merge/refined_fold_ladder_merged.csv")))
fig, axes = plt.subplots(1, 2, figsize=(9.6, 3.7))

ax = axes[0]
for disc, color, marker, label in (("upwind", "#1f77b4", "o", "upwind"), ("scharfetter_gummel", "#c1121f", "s", "Scharfetter--Gummel")):
    pts = sorted((1.0/(int(r["n"])-1), float(r["fold_theta"]), int(r["n"])) for r in rows if r["discretization"] == disc)
    h_main = [p[0] for p in pts if p[2] >= 17]; th_main = [p[1] for p in pts if p[2] >= 17]
    h_pre  = [p[0] for p in pts if p[2] < 17];  th_pre  = [p[1] for p in pts if p[2] < 17]
    ax.plot(h_main, th_main, marker=marker, color=color, lw=1.6, ms=5, label=label)
    ax.plot(h_pre, th_pre, marker=marker, color=color, lw=0, ms=5, mfc="none", alpha=0.55)
    (h2, t2, _), (h1, t1, _) = pts[0], pts[1]
    C = (t1 - t2) / (h1 - h2); th_star = t2 - C * h2
    ax.plot(0, th_star, marker="*", color=color, ms=12, zorder=5)
ax.axhline(-0.1764851, color="k", ls="--", lw=1.0)
ax.text(0.0705, -0.208, r"$\theta_{\rm adm}=-0.17648$", fontsize=8.5, va="bottom")
ax.axhspan(0, 0.25, color="0.92", zorder=0)
ax.text(0.058, 0.08, r"physical path $\theta\in[0,1]$", fontsize=8.5, color="0.35")
ax.set_xlim(-0.006, 0.135); ax.set_ylim(-0.24, 0.25)
ax.set_xlabel(r"grid spacing $h=1/(n-1)$"); ax.set_ylabel(r"located fold control $\theta_c(h)$")
ax.legend(frameon=False, fontsize=8.5, loc="upper right")
ax.set_title("(a) refinement ladder: fold outside the physical path", fontsize=9.5)

ax = axes[1]
files = [("0.05", f"{OLD}/offlattice_fold_theta0.05_20000000.json"),
         ("0.12", f"{OLD}/offlattice_fold_theta0.12_20000000.json"),
         ("0.30", f"{OLD}/offlattice_fold_theta0.3_20000000.json"),
         ("0.60", f"{OLD}/offlattice_fold_theta0.6_20000000.json"),
         ("0.85", f"{OLD}/offlattice_fold_theta0.85_20000000.json")]
cmap = plt.cm.viridis
plotted = 0
for i, (th, f) in enumerate(files):
    d = json.loads(open(f).read())
    h = d["results"]["histograms"]["linear_window_5_60_total"]
    ek = "edges" if "edges" in h else ("bin_edges" if "bin_edges" in h else None)
    ck = "counts" if "counts" in h else ("density" if "density" in h else None)
    if ek is None or ck is None:
        print("HIST KEYS:", list(h.keys())); raise SystemExit(1)
    edges = np.asarray(h[ek], dtype=float); counts = np.asarray(h[ck], dtype=float)
    centers = 0.5 * (edges[:-1] + edges[1:])
    dens = counts / counts.sum() / np.diff(edges)
    ax.semilogy(centers, dens, lw=1.5, color=cmap(0.10 + 0.20 * i), label=fr"$\theta={th}$")
    plotted += 1
ax.set_xlim(5, 60); ax.set_xlabel(r"reaction time $t$")
ax.set_ylabel("conditional density in window")
ax.legend(frameon=False, fontsize=8.5)
ax.set_title("(b) off-lattice realization: late maximum on the path", fontsize=9.5)

fig.tight_layout()
fig.savefig("/private/tmp/claude-502/-Users-ae23069/ee6961d1-72d8-4f2a-ad47-6ff021038957/scratchpad/work/figs/encounter_continuum_bridge.pdf")
print("figure written,", plotted, "BD curves")
