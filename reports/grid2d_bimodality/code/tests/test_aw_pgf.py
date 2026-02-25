#!/usr/bin/env python3
"""Lightweight AW inversion sanity check (geometric distribution)."""

from __future__ import annotations

import numpy as np
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from aw_pgf import invert_pgf_fft


def test_geometric() -> None:
    p = 0.3
    t_max = 60

    def F(z: np.ndarray) -> np.ndarray:
        return (p * z) / (1.0 - (1.0 - p) * z)

    f_hat, _ = invert_pgf_fft(F, t_max=t_max, oversample=4, r_pow10=12.0)
    t = np.arange(1, t_max + 1, dtype=np.float64)
    f_true = p * (1.0 - p) ** (t - 1)

    err = float(np.max(np.abs(f_hat - f_true)))
    assert err < 1e-8, f"AW inversion error too large: {err}"


if __name__ == "__main__":
    test_geometric()
    print("test_aw_pgf: ok")
