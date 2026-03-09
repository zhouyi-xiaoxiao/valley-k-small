#!/usr/bin/env python3
"""Load case geometry for v4 figures from cases_v3.json."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import json

from model_core import ConfigSpec, Coord, Edge, edge_key, scale_coord


@dataclass(frozen=True)
class CaseGeometry:
    case_id: str
    name: str
    N: int
    boundary_x: str
    boundary_y: str
    g_x: float
    g_y: float
    q: float
    start: Coord
    target: Coord
    local_bias: List[dict]
    local_bias_delta: float
    sticky: List[dict]
    barriers_reflect: List[Edge]
    barriers_perm: List[Tuple[Edge, float]]
    corridor: Optional[dict]
    classification_rule: Optional[dict]


def _as_edge(edge_raw) -> Edge:
    (a, b) = edge_raw
    a_t = (int(a[0]), int(a[1]))
    b_t = (int(b[0]), int(b[1]))
    return edge_key(a_t, b_t)


def load_cases_v3(path: Path) -> Dict[str, CaseGeometry]:
    data = json.loads(path.read_text(encoding="utf-8"))
    cases: Dict[str, CaseGeometry] = {}
    for case in data.get("cases", []):
        corridor = case.get("corridor")
        delta = 0.2
        if corridor and "delta" in corridor:
            delta = float(corridor["delta"])
        case_id = str(case["id"])
        barriers_reflect = [_as_edge(e) for e in case.get("barriers_reflect", [])]
        barriers_perm = []
        for item in case.get("barriers_perm", []):
            edge = _as_edge(item["edge"])
            barriers_perm.append((edge, float(item["p_pass"])))
        cases[case_id] = CaseGeometry(
            case_id=case_id,
            name=str(case.get("name", case_id)),
            N=int(case["N"]),
            boundary_x=str(case["boundary"]["x"]),
            boundary_y=str(case["boundary"]["y"]),
            g_x=float(case["global_bias"]["gx"]),
            g_y=float(case["global_bias"]["gy"]),
            q=float(case["q"]),
            start=(int(case["start"][0]), int(case["start"][1])),
            target=(int(case["target"][0]), int(case["target"][1])),
            local_bias=list(case.get("local_bias", [])),
            local_bias_delta=float(delta),
            sticky=list(case.get("sticky", [])),
            barriers_reflect=barriers_reflect,
            barriers_perm=barriers_perm,
            corridor=corridor,
            classification_rule=case.get("classification_rule"),
        )
    return cases


def scale_case_geometry(case: CaseGeometry, N_new: int) -> CaseGeometry:
    if case.N == N_new:
        return case
    scale = float(N_new) / float(case.N)

    def scale_list(items, *, has_dir: bool = False, has_factor: bool = False):
        out = []
        for item in items:
            x = int(item["x"])
            y = int(item["y"])
            x_s, y_s = scale_coord((x, y), scale, N_new)
            record = {"x": x_s, "y": y_s}
            if has_dir:
                record["dir"] = item["dir"]
            if has_factor:
                record["factor"] = float(item["factor"])
            out.append(record)
        return out

    barriers_reflect = []
    for a, b in case.barriers_reflect:
        a_s = scale_coord(a, scale, N_new)
        b_s = scale_coord(b, scale, N_new)
        barriers_reflect.append(edge_key(a_s, b_s))

    barriers_perm = []
    for (a, b), p in case.barriers_perm:
        a_s = scale_coord(a, scale, N_new)
        b_s = scale_coord(b, scale, N_new)
        barriers_perm.append((edge_key(a_s, b_s), float(p)))

    corridor = None
    if case.corridor:
        corr = case.corridor.copy()
        x0 = corr.get("x_start")
        x1 = corr.get("x_end")
        y = corr.get("y")
        if x0 is not None and x1 is not None and y is not None:
            x0_s, _ = scale_coord((int(x0), int(y)), scale, N_new)
            x1_s, _ = scale_coord((int(x1), int(y)), scale, N_new)
            _, y_s = scale_coord((int(x0), int(y)), scale, N_new)
            corr["x_start"] = x0_s
            corr["x_end"] = x1_s
            corr["y"] = y_s
        corridor = corr

    return CaseGeometry(
        case_id=case.case_id,
        name=case.name,
        N=N_new,
        boundary_x=case.boundary_x,
        boundary_y=case.boundary_y,
        g_x=case.g_x,
        g_y=case.g_y,
        q=case.q,
        start=scale_coord(case.start, scale, N_new),
        target=scale_coord(case.target, scale, N_new),
        local_bias=scale_list(case.local_bias, has_dir=True),
        local_bias_delta=case.local_bias_delta,
        sticky=scale_list(case.sticky, has_factor=True),
        barriers_reflect=barriers_reflect,
        barriers_perm=barriers_perm,
        corridor=corridor,
        classification_rule=case.classification_rule,
    )


def case_to_spec(case: CaseGeometry) -> ConfigSpec:
    local_bias = {(int(it["x"]), int(it["y"])): str(it["dir"]) for it in case.local_bias}
    sticky = {(int(it["x"]), int(it["y"])): float(it["factor"]) for it in case.sticky}
    barriers_reflect = set(case.barriers_reflect)
    barriers_perm = {edge: float(p) for edge, p in case.barriers_perm}
    return ConfigSpec(
        N=case.N,
        q=case.q,
        g_x=case.g_x,
        g_y=case.g_y,
        boundary_x=case.boundary_x,
        boundary_y=case.boundary_y,
        start=case.start,
        target=case.target,
        local_bias_arrows=local_bias,
        local_bias_delta=case.local_bias_delta,
        sticky_sites=sticky,
        barriers_reflect=barriers_reflect,
        barriers_perm=barriers_perm,
    )
