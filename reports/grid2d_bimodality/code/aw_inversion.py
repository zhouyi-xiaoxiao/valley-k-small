#!/usr/bin/env python3
"""Discrete-time AW inversion for PGF coefficients (FFT form)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional, Tuple

import numpy as np


@dataclass(frozen=True)
class AWParams:
    m: int
    r: float
    oversample: int
    r_pow10: float


def next_pow2(n: int) -> int:
    if n <= 1:
        return 1
    return 1 << (n - 1).bit_length()


def choose_aw_params(t_max_aw: int, oversample: int, r_pow10: float) -> AWParams:
    if t_max_aw <= 0:
        raise ValueError("t_max_aw must be positive")
    if oversample <= 1:
        raise ValueError("oversample must be >= 2")
    m = next_pow2(int(oversample * (t_max_aw + 1)))
    r = float(10.0 ** (-float(r_pow10) / float(m)))
    return AWParams(m=m, r=r, oversample=oversample, r_pow10=r_pow10)


def aw_invert(
    F_tilde: Callable[[np.ndarray], np.ndarray],
    *,
    t_max_aw: int,
    oversample: int = 8,
    r_pow10: float = 10.0,
) -> Tuple[np.ndarray, AWParams]:
    params = choose_aw_params(t_max_aw, oversample, r_pow10)
    k = np.arange(params.m, dtype=np.float64)
    z = params.r * np.exp(1j * 2.0 * np.pi * k / float(params.m))

    try:
        Fz = F_tilde(z)
    except Exception:
        Fz = np.zeros_like(z, dtype=np.complex128)
        for i, zi in enumerate(z):
            Fz[i] = F_tilde(np.array([zi]))[0]

    Fz = np.asarray(Fz, dtype=np.complex128)
    if Fz.shape != z.shape:
        raise ValueError("F_tilde must return array of shape (m,)")

    fft = np.fft.fft(Fz) / float(params.m)
    t = np.arange(params.m, dtype=np.float64)
    coeffs = (params.r ** (-t)) * fft
    f = coeffs[1 : (t_max_aw + 1)].real.astype(np.float64, copy=False)
    return f, params
