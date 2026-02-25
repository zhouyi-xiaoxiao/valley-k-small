#!/usr/bin/env python3
"""Generating-function helpers for FPT from transient matrix Q."""

from __future__ import annotations

from typing import Tuple

import numpy as np

from model_core import LatticeConfig, build_exact_arrays


def build_transient_system(cfg: LatticeConfig) -> Tuple[np.ndarray, np.ndarray]:
    """Return (Q, r) for the transient system (dense)."""
    src_idx, dst_idx, probs, r, _ = build_exact_arrays(cfg)
    n = len(r)
    Q = np.zeros((n, n), dtype=np.float64)
    np.add.at(Q, (src_idx, dst_idx), probs)
    return Q, r


def fpt_pgf_from_Q(z: complex, *, Q: np.ndarray, p0: np.ndarray, r: np.ndarray) -> complex:
    """
    F~(z) = z * p0 * (I - z Q)^{-1} * r.
    Solve (I - z Q) x = r and return z * p0 @ x.
    """
    n = Q.shape[0]
    A = np.eye(n, dtype=np.complex128) - z * Q.astype(np.complex128)
    x = np.linalg.solve(A, r.astype(np.complex128))
    return z * np.dot(p0.astype(np.complex128), x)
