#!/usr/bin/env python3
"""Generate defect-free/defected propagator PGFs and FPT PGFs for 2D walks."""

from __future__ import annotations

from typing import Callable

import numpy as np

from heterogeneity_determinant import DefectSystem, defect_pairs_from_config
from model_core import Coord, LatticeConfig
from propagator_z_analytic import defect_free_propagator_from_config


def _vectorize_complex(func: Callable[[complex], complex]) -> Callable[[np.ndarray], np.ndarray]:
    def wrapped(z: np.ndarray) -> np.ndarray:
        z = np.asarray(z, dtype=np.complex128)
        out = np.zeros_like(z, dtype=np.complex128)
        for i, zi in enumerate(z):
            out[i] = func(complex(zi))
        return out

    return wrapped


def build_defectfree_propagator_gf(cfg: LatticeConfig) -> Callable[[Coord, Coord, np.ndarray], np.ndarray]:
    base = defect_free_propagator_from_config(cfg)

    def P0(src: Coord, dst: Coord, z: np.ndarray) -> np.ndarray:
        if np.ndim(z) == 0:
            return np.array([base.propagator(src, dst, complex(z))])
        return np.array([base.propagator(src, dst, complex(zi)) for zi in z], dtype=np.complex128)

    return P0


def build_defected_propagator_gf(cfg: LatticeConfig) -> Callable[[Coord, Coord, np.ndarray], np.ndarray]:
    base = defect_free_propagator_from_config(cfg)
    defects = defect_pairs_from_config(cfg)

    def P(src: Coord, dst: Coord, z: np.ndarray) -> np.ndarray:
        def eval_scalar(zi: complex) -> complex:
            system = DefectSystem(base=base, defects=defects, start=src, target=dst)
            p_src, _ = system.propagators(zi)
            return p_src

        return _vectorize_complex(eval_scalar)(z)

    return P


def build_fpt_gf(cfg: LatticeConfig) -> Callable[[np.ndarray], np.ndarray]:
    base = defect_free_propagator_from_config(cfg)
    defects = defect_pairs_from_config(cfg)
    system = DefectSystem(base=base, defects=defects, start=cfg.start, target=cfg.target)

    def F_tilde(z: np.ndarray) -> np.ndarray:
        z = np.asarray(z, dtype=np.complex128)
        out = np.zeros_like(z, dtype=np.complex128)
        for i, zi in enumerate(z):
            p_start, p_target = system.propagators(zi)
            if abs(p_target) < 1e-18:
                p_target = p_target + (1e-18 + 0j)
            out[i] = p_start / p_target
        return out

    return F_tilde
