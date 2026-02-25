#!/usr/bin/env python3
"""AW inversion sanity check on a small 2D lattice (v5)."""

from __future__ import annotations

import numpy as np
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from configs_candidates import candidate_A_spec
from fpt_exact_mc import exact_fpt
from fpt_generating import fpt_pgf_from_Q
from aw_inversion import aw_invert
from model_core import build_exact_arrays, scale_spec, spec_to_internal


def main() -> None:
    spec = scale_spec(candidate_A_spec(N=60), 8)
    cfg = spec_to_internal(spec)

    t_max = 200
    f_exact, _ = exact_fpt(cfg, t_max=t_max)

    src_idx, dst_idx, probs, r, index = build_exact_arrays(cfg)
    n = len(r)
    Q = np.zeros((n, n), dtype=np.float64)
    np.add.at(Q, (src_idx, dst_idx), probs)

    p0 = np.zeros(n, dtype=np.float64)
    p0[index[cfg.start]] = 1.0

    def F_tilde(z: np.ndarray) -> np.ndarray:
        out = np.zeros_like(z, dtype=np.complex128)
        for i, zi in enumerate(z):
            out[i] = fpt_pgf_from_Q(zi, Q=Q, p0=p0, r=r)
        return out

    f_aw, params = aw_invert(F_tilde, t_max_aw=t_max, oversample=8, r_pow10=12.0)
    err = float(np.max(np.abs(f_aw - f_exact[:t_max])))
    if err > 1e-10:
        raise AssertionError(f"AW toy error too large: {err:.3e}")
    print(f"AW toy check: max|aw-exact|={err:.3e} (m={params.m}, r={params.r:.6f})")


if __name__ == "__main__":
    main()
