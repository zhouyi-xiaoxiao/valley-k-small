#!/usr/bin/env python3
"""Analytic (spectral) defect-free propagator in z-domain for 2D biased/lazy walks."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Sequence, Tuple

import numpy as np

from model_core import Coord, LatticeConfig


@dataclass(frozen=True)
class OneDimSpectrum:
    eigenvalues: np.ndarray
    h: np.ndarray
    boundary: str
    p_left: float
    p_right: float
    pi: np.ndarray


@dataclass(frozen=True)
class PairEvaluator:
    starts: List[Coord]
    dests: List[Coord]
    hx_vecs: np.ndarray
    hy_vecs: np.ndarray
    lambda_2d: np.ndarray
    shape: Tuple[int, int]

    def evaluate(self, z: complex) -> np.ndarray:
        denom = 1.0 - z * self.lambda_2d
        denom = np.where(np.abs(denom) < 1e-14, 1e-14 + 0j, denom)
        inv_denom = 1.0 / denom
        temp = np.dot(inv_denom, self.hy_vecs)
        vals = np.sum(self.hx_vecs * temp, axis=0)
        return vals.reshape(self.shape)


class DefectFreePropagator2D:
    def __init__(
        self,
        *,
        N: int,
        q: float,
        g_x: float,
        g_y: float,
        boundary_x: str,
        boundary_y: str,
    ) -> None:
        self.N = int(N)
        self.q = float(q)
        self.g_x = float(g_x)
        self.g_y = float(g_y)
        self.boundary_x = boundary_x
        self.boundary_y = boundary_y

        p_left_x = 0.5 * (1.0 + self.g_x)
        p_right_x = 0.5 * (1.0 - self.g_x)
        # y-axis is defined positive downward, so p_right_y corresponds to down moves.
        p_left_y = 0.5 * (1.0 - self.g_y)
        p_right_y = 0.5 * (1.0 + self.g_y)

        self.spec_x = compute_1d_spectrum(self.N, p_left_x, p_right_x, boundary_x)
        self.spec_y = compute_1d_spectrum(self.N, p_left_y, p_right_y, boundary_y)

        lam_x = self.spec_x.eigenvalues
        lam_y = self.spec_y.eigenvalues
        self.lambda_2d = (1.0 - self.q) + 0.5 * self.q * (lam_x[:, None] + lam_y[None, :])

    def prepare_pair_evaluator(self, starts: Sequence[Coord], dests: Sequence[Coord]) -> PairEvaluator:
        starts = list(starts)
        dests = list(dests)
        if not starts or not dests:
            raise ValueError("starts and dests must be non-empty")

        start_x = np.array([s[0] for s in starts for _ in dests], dtype=np.int64)
        start_y = np.array([s[1] for s in starts for _ in dests], dtype=np.int64)
        dest_x = np.array([d[0] for _ in starts for d in dests], dtype=np.int64)
        dest_y = np.array([d[1] for _ in starts for d in dests], dtype=np.int64)

        # Note: use h[:, start, dest] to match row-stochastic indexing in 2D.
        hx_vecs = self.spec_x.h[:, start_x, dest_x]
        hy_vecs = self.spec_y.h[:, start_y, dest_y]
        shape = (len(starts), len(dests))
        return PairEvaluator(
            starts=starts,
            dests=dests,
            hx_vecs=hx_vecs,
            hy_vecs=hy_vecs,
            lambda_2d=self.lambda_2d,
            shape=shape,
        )

    def propagator(self, start: Coord, dest: Coord, z: complex) -> complex:
        hx = self.spec_x.h[:, start[0], dest[0]]
        hy = self.spec_y.h[:, start[1], dest[1]]
        denom = 1.0 - z * self.lambda_2d
        denom = np.where(np.abs(denom) < 1e-14, 1e-14 + 0j, denom)
        inv_denom = 1.0 / denom
        return np.sum((hx[:, None] * hy[None, :]) * inv_denom)


def compute_1d_spectrum(
    N: int,
    p_left: float,
    p_right: float,
    boundary: str,
) -> OneDimSpectrum:
    if boundary not in ("periodic", "reflecting"):
        raise ValueError("boundary must be periodic or reflecting")
    if p_left < 0 or p_right < 0:
        raise ValueError("p_left and p_right must be nonnegative")
    if abs((p_left + p_right) - 1.0) > 1e-9:
        raise ValueError("p_left + p_right must be 1 for the 1D step operator")

    if boundary == "periodic":
        k = np.arange(N, dtype=np.float64)
        theta = 2.0 * np.pi * k / float(N)
        eigenvalues = p_left * np.exp(-1j * theta) + p_right * np.exp(1j * theta)
        x = np.arange(N, dtype=np.float64)
        diff = x[:, None] - x[None, :]
        h = np.exp(1j * theta[:, None, None] * diff[None, :, :]) / float(N)
        pi = np.full(N, 1.0 / float(N), dtype=np.float64)
        return OneDimSpectrum(
            eigenvalues=eigenvalues.astype(np.complex128),
            h=h.astype(np.complex128),
            boundary=boundary,
            p_left=p_left,
            p_right=p_right,
            pi=pi,
        )

    # reflecting
    if p_left == 0.0 or p_right == 0.0:
        raise ValueError("reflecting spectrum requires p_left and p_right > 0")

    r = p_right / p_left
    pi = r ** np.arange(N, dtype=np.float64)
    pi = pi / pi.sum()

    B = np.zeros((N, N), dtype=np.float64)
    for x in range(N):
        if x > 0:
            B[x, x - 1] = p_left
        else:
            B[x, x] += p_left
        if x < N - 1:
            B[x, x + 1] = p_right
        else:
            B[x, x] += p_right

    sqrt_pi = np.sqrt(pi)
    S = (sqrt_pi[:, None] * B) / sqrt_pi[None, :]
    eigvals, eigvecs = np.linalg.eigh(S)
    order = np.argsort(eigvals)[::-1]
    eigvals = eigvals[order]
    eigvecs = eigvecs[:, order]

    ratio = np.sqrt(pi[None, :] / pi[:, None])
    h = np.zeros((N, N, N), dtype=np.float64)
    for k in range(N):
        u = eigvecs[:, k]
        h[k] = np.outer(u, u) * ratio

    return OneDimSpectrum(
        eigenvalues=eigvals.astype(np.complex128),
        h=h.astype(np.complex128),
        boundary=boundary,
        p_left=p_left,
        p_right=p_right,
        pi=pi,
    )


def defect_free_propagator_from_config(cfg: LatticeConfig) -> DefectFreePropagator2D:
    return DefectFreePropagator2D(
        N=cfg.N,
        q=cfg.q,
        g_x=cfg.g_x,
        g_y=cfg.g_y,
        boundary_x=cfg.boundary_x,
        boundary_y=cfg.boundary_y,
    )
