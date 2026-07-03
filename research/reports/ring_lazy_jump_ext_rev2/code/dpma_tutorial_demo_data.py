#!/usr/bin/env python3
# wrapper-report-id: ring_lazy_jump_ext_rev2
"""Precompute data for the tutorial interactive page (manuscript/extras/tutorial/).

Emits dpma_demo_data.js with:
  fold : continuum Phi(tau; b) at theta=xi=1/2 for a slider of b values (station 6 intuition)
  modes: lattice F(t) partial sums at N=100, beta=0.01, C.2 start u+4 (stations 4-5 intuition)
Deterministic; rerun any time. The interactive page reads this file from the same directory.
"""
from __future__ import annotations
import json
import math
from pathlib import Path
import numpy as np
from dpma_saddle_node_bc_theta import phi_vals
from dpma_luca_pack import modes_lattice

OUT = Path(__file__).resolve().parents[1] / "manuscript" / "extras" / "tutorial" / "dpma_demo_data.js"

# ---- fold slider: continuum antipodal master curve across b_c ----------------------------
taus = np.exp(np.linspace(math.log(1.3e-3), math.log(0.5), 320))
bs = [2.0, 2.4, 2.8, 3.0, 3.05, 3.076, 3.1, 3.2, 3.4, 3.8]
curves = [[round(float(v), 5) for v in phi_vals(taus, 0.5, 0.5, b)] for b in bs]

# ---- mode toggles: lattice partial sums (attribution geometry) ---------------------------
N, beta, r0 = 100, 0.01, 54
s, B = modes_lattice(N, beta, r0)
ts = np.unique(np.round(np.geomspace(2, 4000, 260)).astype(int))
ls = np.log(np.clip(s, 1e-300, None))
def curve(kmax):
    return [round(float(v), 9) for v in (np.exp(np.outer(ts - 1.0, ls[:kmax])) * B[:kmax]).sum(axis=1)]
full = [round(float(v), 9) for v in (np.exp(np.outer(ts - 1.0, ls)) * B).sum(axis=1)]

data = {
    "fold": {"tau": [round(float(t), 6) for t in taus], "bs": bs, "curves": curves,
             "bc": 3.0764323604},
    "modes": {"t": [int(t) for t in ts], "full": full,
              "parts": {"1": curve(1), "3": curve(3), "9": curve(9), "31": curve(31)},
              "marks": {"t1": 24, "tv": 239, "t2": 1091}},
}
OUT.write_text("const DPMA = " + json.dumps(data) + ";\n")
print("wrote", OUT, f"({OUT.stat().st_size/1024:.0f} KB)")
