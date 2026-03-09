from __future__ import annotations

from typing import Callable, Sequence

import numpy as np

from vkcore.grid2d.bimod_legacy_imports import CaseGeometry, ViewBox
from vkcore.grid2d.model_core_reflecting import ConfigSpec

from .types import Coord, Edge


def as_case_geometry(
    case,
    *,
    dir_map: dict[str, str],
    build_barriers: Callable[[set[Coord], int], Sequence[Edge]],
    include_extra_barriers: bool = False,
) -> CaseGeometry:
    barriers = set(build_barriers(case.allowed, case.N))
    if include_extra_barriers:
        barriers.update(getattr(case, "extra_barriers", set()))

    local_bias_list = [
        {"x": x, "y": y, "dir": dir_map[d]}
        for (x, y), (d, _) in case.local_bias.items()
    ]
    local_bias_list.sort(key=lambda item: (item["y"], item["x"]))

    sticky_list = [{"x": x, "y": y, "factor": float(f)} for (x, y), f in case.sticky.items()]
    sticky_list.sort(key=lambda item: (item["y"], item["x"]))

    barriers_perm = [(edge, float(p)) for edge, p in case.doors.items()]

    return CaseGeometry(
        case_id=case.case_id,
        name=case.name,
        N=case.N,
        boundary_x="reflecting",
        boundary_y="reflecting",
        g_x=float(case.gx),
        g_y=float(case.gy),
        q=float(case.q),
        start=case.start,
        target=case.target,
        local_bias=local_bias_list,
        local_bias_delta=0.0,
        sticky=sticky_list,
        barriers_reflect=barriers,
        barriers_perm=barriers_perm,
        corridor=None,
        classification_rule=None,
    )


def case_to_spec(
    case,
    *,
    dir_map: dict[str, str],
    build_barriers: Callable[[set[Coord], int], Sequence[Edge]],
    include_extra_barriers: bool = False,
) -> ConfigSpec:
    local_bias_arrows = {xy: dir_map[d] for xy, (d, _) in case.local_bias.items()}
    local_bias_deltas = {xy: float(delta) for xy, (_, delta) in case.local_bias.items()}
    sticky = {xy: float(f) for xy, f in case.sticky.items()}

    barriers_reflect = set(build_barriers(case.allowed, case.N))
    if include_extra_barriers:
        barriers_reflect.update(getattr(case, "extra_barriers", set()))

    barriers_perm = {edge: float(p) for edge, p in case.doors.items()}

    return ConfigSpec(
        N=case.N,
        q=case.q,
        g_x=case.gx,
        g_y=case.gy,
        boundary_x="reflecting",
        boundary_y="reflecting",
        start=case.start,
        target=case.target,
        local_bias_arrows=local_bias_arrows,
        local_bias_delta=0.0,
        local_bias_deltas=local_bias_deltas,
        sticky_sites=sticky,
        barriers_reflect=barriers_reflect,
        barriers_perm=barriers_perm,
    )


def coord_to_index(xy: Coord, n: int) -> int:
    return (xy[0] - 1) * n + (xy[1] - 1)


def slow_mask(case) -> np.ndarray:
    mask = np.zeros(case.N * case.N, dtype=bool)
    for xy in case.slow_set:
        mask[coord_to_index(xy, case.N)] = True
    mask[coord_to_index(case.start, case.N)] = False
    mask[coord_to_index(case.target, case.N)] = False
    return mask


def heat_view_for_case(case, *, pad: int = 2) -> ViewBox:
    xs = [x for (x, _) in case.allowed]
    ys = [y for (_, y) in case.allowed]
    x0 = max(1, min(xs) - pad)
    x1 = min(case.N, max(xs) + pad)
    y0 = max(1, min(ys) - pad)
    y1 = min(case.N, max(ys) + pad)
    return ViewBox(x0, x1, y0, y1)


def heat_mask_for_case(case) -> np.ndarray:
    mask = np.zeros((case.N, case.N), dtype=bool)
    for x, y in case.allowed:
        mask[x - 1, y - 1] = True
    return mask


__all__ = [
    "Coord",
    "Edge",
    "ConfigSpec",
    "as_case_geometry",
    "case_to_spec",
    "coord_to_index",
    "heat_mask_for_case",
    "heat_view_for_case",
    "slow_mask",
]
