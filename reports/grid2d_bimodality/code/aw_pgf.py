#!/usr/bin/env python3
"""
FFT-based Cauchy/Abate-Whitt inversion for discrete-time PGF coefficients.

Given a generating function F(z) = sum_{t>=0} f(t) z^t, we extract
  f(t) = [z^t] F(z)
      = (1 / 2πi) ∮_{|z|=r} F(z) / z^{t+1} dz
      = (r^{-t} / 2π) ∫_{-π}^{π} F(r e^{iθ}) e^{-itθ} dθ
  ≈ (r^{-t} / m) Σ_{k=0}^{m-1} F(r e^{i2πk/m}) e^{-i2πkt/m}.

With z_k = r e^{i2πk/m} and Fvals[k] = F(z_k), a single FFT gives
  c = FFT(Fvals) / m,   f(t) ≈ Re(c[t]) * r^{-t}.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional, Tuple

import numpy as np


@dataclass(frozen=True)
class AWParams:
    m: int
    r: float
    oversample: int
    r_pow10: Optional[float]
    a: Optional[float]


def next_pow2(n: int) -> int:
    if n <= 1:
        return 1
    return 1 << (n - 1).bit_length()


def choose_aw_params(
    t_max: int,
    *,
    oversample: int = 4,
    r_pow10: Optional[float] = 12.0,
    a: Optional[float] = None,
) -> AWParams:
    if t_max <= 0:
        raise ValueError("t_max must be positive")
    if oversample <= 1:
        raise ValueError("oversample must be >= 2")

    m = next_pow2(int(oversample * (t_max + 1)))
    if a is not None:
        r = float(np.exp(-float(a) / float(t_max + 1)))
    else:
        if r_pow10 is None:
            raise ValueError("r_pow10 must be provided when a is None")
        r = float(10.0 ** (-float(r_pow10) / float(m)))
    return AWParams(m=m, r=r, oversample=oversample, r_pow10=r_pow10, a=a)


def invert_pgf_fft(
    F_tilde: Callable[[np.ndarray], np.ndarray],
    *,
    t_max: int,
    oversample: int = 4,
    r_pow10: Optional[float] = 12.0,
    a: Optional[float] = None,
    m: Optional[int] = None,
    r: Optional[float] = None,
    start_at_one: bool = True,
) -> Tuple[np.ndarray, AWParams]:
    params = choose_aw_params(t_max, oversample=oversample, r_pow10=r_pow10, a=a)
    if m is None:
        m = params.m
    if r is None:
        r = params.r
    params = AWParams(m=int(m), r=float(r), oversample=oversample, r_pow10=r_pow10, a=a)

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

    c = np.fft.fft(Fz) / float(params.m)
    t = np.arange(params.m, dtype=np.float64)
    coeffs = (params.r ** (-t)) * c

    if start_at_one:
        f = coeffs[1 : (t_max + 1)].real.astype(np.float64, copy=False)
    else:
        f = coeffs[: (t_max + 1)].real.astype(np.float64, copy=False)
    return f, params
