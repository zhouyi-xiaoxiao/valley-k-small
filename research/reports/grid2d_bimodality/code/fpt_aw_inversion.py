#!/usr/bin/env python3
"""Abate-Whitt inversion utilities for discrete-time FPT generating functions."""

from __future__ import annotations

from typing import Callable, Tuple

import numpy as np

from aw_pgf import AWParams, choose_aw_params, invert_pgf_fft
from heterogeneity_determinant import DefectSystem, defect_pairs_from_config
from model_core import LatticeConfig
from propagator_z_analytic import defect_free_propagator_from_config


def invert_pgf_aw(
    F_tilde: Callable[[np.ndarray], np.ndarray],
    *,
    t_max: int,
    oversample: int = 4,
    r_pow10: float = 12.0,
) -> Tuple[np.ndarray, AWParams]:
    return invert_pgf_fft(
        F_tilde,
        t_max=t_max,
        oversample=oversample,
        r_pow10=r_pow10,
        start_at_one=True,
    )


def fpt_pmf_aw(
    cfg: LatticeConfig,
    *,
    t_max: int,
    oversample: int = 4,
    r_pow10: float = 12.0,
) -> Tuple[np.ndarray, AWParams]:
    base = defect_free_propagator_from_config(cfg)
    defects = defect_pairs_from_config(cfg)
    system = DefectSystem(base=base, defects=defects, start=cfg.start, target=cfg.target)

    def F_tilde(z: np.ndarray) -> np.ndarray:
        out = np.zeros_like(z, dtype=np.complex128)
        for i, zi in enumerate(z):
            p_start, p_target = system.propagators(zi)
            if abs(p_target) < 1e-18:
                p_target = p_target + (1e-18 + 0j)
            out[i] = p_start / p_target
        return out

    return invert_pgf_aw(F_tilde, t_max=t_max, oversample=oversample, r_pow10=r_pow10)


def fpt_pmf_aw_with_grid(
    cfg: LatticeConfig,
    *,
    t_max: int,
    oversample: int = 4,
    r_pow10: float = 12.0,
) -> Tuple[np.ndarray, AWParams, np.ndarray, np.ndarray]:
    """Return AW coefficients plus the z-grid and F(z) samples for reproducibility."""
    base = defect_free_propagator_from_config(cfg)
    defects = defect_pairs_from_config(cfg)
    system = DefectSystem(base=base, defects=defects, start=cfg.start, target=cfg.target)

    params = choose_aw_params(t_max, oversample=oversample, r_pow10=r_pow10)
    k = np.arange(params.m, dtype=np.float64)
    z_grid = params.r * np.exp(1j * 2.0 * np.pi * k / float(params.m))

    Fz = np.zeros_like(z_grid, dtype=np.complex128)
    for i, zi in enumerate(z_grid):
        p_start, p_target = system.propagators(zi)
        if abs(p_target) < 1e-18:
            p_target = p_target + (1e-18 + 0j)
        Fz[i] = p_start / p_target

    c = np.fft.fft(Fz) / float(params.m)
    t = np.arange(params.m, dtype=np.float64)
    coeffs = (params.r ** (-t)) * c
    f_aw = coeffs[1 : (t_max + 1)].real.astype(np.float64, copy=False)
    return f_aw, params, z_grid, Fz
