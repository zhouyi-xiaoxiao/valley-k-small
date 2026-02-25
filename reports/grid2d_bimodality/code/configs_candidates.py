#!/usr/bin/env python3
"""Candidate configurations and scan helpers for the 2D bimodality report."""

from __future__ import annotations

from typing import List, Tuple

from model_core import ConfigSpec, Edge, edge_key, scale_spec, spec_to_internal
from model_core import coord_to0


def candidate_A_spec(N: int = 60) -> ConfigSpec:
    return ConfigSpec(
        N=N,
        q=0.8,
        g_x=0.6,
        g_y=0.0,
        boundary_x="periodic",
        boundary_y="reflecting",
        start=(10, 30),
        target=(12, 30),
    )


def candidate_B_spec(L: int, N: int = 60, delta: float = 0.6) -> ConfigSpec:
    corridor = {(x, 55): "left" for x in range(50 - L + 1, 51)}
    return ConfigSpec(
        N=N,
        q=0.8,
        g_x=0.35,
        g_y=0.35,
        boundary_x="reflecting",
        boundary_y="reflecting",
        start=(50, 55),
        target=(40, 55),
        local_bias_arrows=corridor,
        local_bias_delta=delta,
    )


def candidate_C_spec(n_bias: int, N: int = 60) -> ConfigSpec:
    arrows_all = [(25, 30), (26, 30), (27, 30)]
    arrows = {arrows_all[i]: "right" for i in range(min(n_bias, len(arrows_all)))}
    sticky = {(x, y): 0.2 for x in range(27, 30) for y in range(29, 32)}

    barriers_reflect: set[Edge] = set()
    barriers_perm: dict[Edge, float] = {}
    for y in range(1, N + 1):
        a = (30, y)
        b = (31, y)
        if y == 30:
            barriers_perm[edge_key(a, b)] = 0.2
        else:
            barriers_reflect.add(edge_key(a, b))

    return ConfigSpec(
        N=N,
        q=0.8,
        g_x=0.5,
        g_y=0.0,
        boundary_x="periodic",
        boundary_y="reflecting",
        start=(10, 30),
        target=(50, 30),
        local_bias_arrows=arrows,
        local_bias_delta=0.2,
        sticky_sites=sticky,
        barriers_reflect=barriers_reflect,
        barriers_perm=barriers_perm,
    )


def corridor_set_from_spec(spec: ConfigSpec) -> set[Tuple[int, int]]:
    return set(coord_to0(xy) for xy in spec.local_bias_arrows)


def sticky_set_from_spec(spec: ConfigSpec) -> set[Tuple[int, int]]:
    return set(coord_to0(xy) for xy in spec.sticky_sites)


def scan_corridor_lengths(
    *,
    exact_solver,
    t_max: int,
    N: int,
    quick: bool,
    seed: int,
) -> Tuple[List[dict], int]:
    results: List[dict] = []
    L_values = list(range(1, 16))

    for L in L_values:
        spec = candidate_B_spec(L=L, N=60)
        if quick:
            spec = scale_spec(spec, N)
        cfg = spec_to_internal(spec)
        f, mass = exact_solver(cfg, t_max=t_max, stop_tol=1e-8)
        peaks = find_bimodality(f)
        row = {
            "L": int(L),
            "mass": float(mass),
            **{k: v for k, v in peaks.items() if k != "peaks"},
            "peaks": peaks.get("peaks", []),
        }
        if quick:
            row["L_scaled"] = int(len(spec.local_bias_arrows))
        results.append(row)

    L_min = -1
    for row in results:
        if row.get("paper_bimodal"):
            L_min = int(row["L"])
            break

    return results, L_min


def scan_bias_sites(
    *,
    exact_solver,
    t_max: int,
    N: int,
    quick: bool,
    seed: int,
) -> Tuple[List[dict], int]:
    results: List[dict] = []
    for n_bias in range(0, 4):
        spec = candidate_C_spec(n_bias=n_bias, N=60)
        if quick:
            spec = scale_spec(spec, N)
        cfg = spec_to_internal(spec)
        f, mass = exact_solver(cfg, t_max=t_max, stop_tol=1e-8)
        peaks = find_bimodality(f)
        results.append(
            {
                "n_bias": int(n_bias),
                "mass": float(mass),
                **{k: v for k, v in peaks.items() if k != "peaks"},
                "peaks": peaks.get("peaks", []),
            }
        )

    n_min = -1
    for row in results:
        if row.get("paper_bimodal"):
            n_min = int(row["n_bias"])
            break

    return results, n_min


# -------------------------
# Bimodality detection (shared)
# -------------------------


def strict_local_peaks(f, h_min: float) -> List[Tuple[int, float]]:
    peaks: List[Tuple[int, float]] = []
    if len(f) == 0:
        return peaks
    for i in range(len(f)):
        left = f[i - 1] if i > 0 else 0.0
        right = f[i + 1] if i + 1 < len(f) else 0.0
        if f[i] > left and f[i] > right and f[i] >= h_min:
            peaks.append((i + 1, float(f[i])))
    return peaks


def find_bimodality(
    f,
    h_min: float = 1e-7,
    second_frac: float = 0.01,
    macro_ratio: float = 10.0,
) -> dict:
    peaks = strict_local_peaks(f, h_min=h_min)
    if not peaks:
        return {
            "paper_bimodal": False,
            "macro_bimodal": False,
            "peaks": [],
        }

    hmax = max(h for _, h in peaks)
    peaks_f = [(t, h) for t, h in peaks if h >= second_frac * hmax]
    peaks_f.sort(key=lambda x: x[0])

    paper_bimodal = len(peaks_f) >= 2
    t1 = t2 = tv = None
    h1 = h2 = hv = None
    if paper_bimodal:
        t1, h1 = peaks_f[0]
        t2, h2 = peaks_f[1]
        if t2 > t1 + 1:
            seg = f[t1 : t2 - 1]
            idx_min = int(seg.argmin())
            tv = t1 + idx_min + 1
            hv = float(f[tv - 1])

    macro_bimodal = False
    if len(peaks_f) >= 2:
        top2 = sorted(peaks_f, key=lambda x: -x[1])[:2]
        t_small, t_large = sorted([top2[0][0], top2[1][0]])
        if t_small > 0 and t_large / t_small >= macro_ratio:
            macro_bimodal = True

    out = {
        "paper_bimodal": paper_bimodal,
        "macro_bimodal": macro_bimodal,
        "peaks": peaks_f,
        "t1": t1,
        "t2": t2,
        "tv": tv,
        "h1": h1,
        "h2": h2,
        "hv": hv,
    }
    if paper_bimodal and h1 is not None and h2 is not None:
        out["h2_over_h1"] = float(h2 / h1)
        out["t2_over_t1"] = float(t2 / t1)
        if hv is not None:
            out["hv_over_max"] = float(hv / max(h1, h2))
    return out
