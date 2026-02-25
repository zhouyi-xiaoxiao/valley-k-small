#!/usr/bin/env python3
"""Build the fixed benchmark manifest for Luca regime mapping."""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import numpy as np

# Keep BLAS single-threaded for reproducible timing side effects in later steps.
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

ROOT = Path(__file__).resolve().parents[3]
TT_CODE = ROOT / "reports" / "2d_two_target_double_peak" / "code"
REF_CODE = ROOT / "reports" / "2d_reflecting_bimodality" / "code"
BIMOD_CODE = ROOT / "reports" / "grid2d_bimodality" / "code"

# Path order mirrors existing benchmark script for reflecting + heterogeneity tools.
sys.path.insert(0, str(REF_CODE))
sys.path.insert(1, str(BIMOD_CODE))
sys.path.insert(2, str(TT_CODE))

import reflecting_bimodality_pipeline as rbp  # noqa: E402
from heterogeneity_determinant import defect_pairs_from_config  # noqa: E402
from model_core import ConfigSpec, LatticeConfig, edge_key, spec_to_internal  # noqa: E402
from two_target_2d_report import build_case_layout, polyline_points, to0  # noqa: E402

Coord = Tuple[int, int]


@dataclass(frozen=True)
class Geometry:
    family: str
    geometry_id: str
    geometry_kind: str
    config_json: str
    defect_pairs: int
    local_bias_sites: int
    seed: int


def _ensure_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _two_target_base_geometry() -> tuple[int, float, float, Coord, Coord, Coord, List[Coord], List[Coord]]:
    N = 31
    q = 0.2
    delta = 0.2
    start = to0((15, 15))
    m1 = to0((22, 15))
    m2 = to0((7, 7))
    fast_nodes = [to0((15, 15)), to0((22, 15))]
    slow_nodes = [to0((15, 15)), to0((15, 27)), to0((3, 27)), to0((3, 7)), to0((7, 7))]
    return N, q, delta, start, m1, m2, fast_nodes, slow_nodes


def _arrow_map_to_json_list(arrow_map: Dict[Coord, str]) -> List[List[object]]:
    rows = [[int(x), int(y), str(d)] for (x, y), d in sorted(arrow_map.items())]
    return rows


def _two_target_defect_pairs(*, N: int, q: float, delta: float, start: Coord, m1: Coord, arrow_map: Dict[Coord, str]) -> int:
    map_dir = {"E": "right", "W": "left", "N": "down", "S": "up"}
    local_bias_arrows = {xy: map_dir[d] for xy, d in arrow_map.items()}
    cfg = LatticeConfig(
        N=N,
        q=q,
        g_x=0.0,
        g_y=0.0,
        boundary_x="reflecting",
        boundary_y="reflecting",
        start=start,
        target=m1,
        local_bias_arrows=local_bias_arrows,
        local_bias_delta=float(delta),
        sticky_sites={},
        barriers_reflect=set(),
        barriers_perm={},
    )
    defects = defect_pairs_from_config(cfg)
    return int(len(defects))


def _sparse_synthetic_arrow_map(
    *,
    N: int,
    n_sites: int,
    seed: int,
    start: Coord,
    m1: Coord,
    m2: Coord,
) -> Dict[Coord, str]:
    rng = np.random.default_rng(seed)
    dirs = np.asarray(["E", "W", "N", "S"], dtype=object)
    candidates: List[Coord] = []
    for x in range(N):
        for y in range(N):
            c = (x, y)
            if c in {m1, m2}:
                continue
            candidates.append(c)
    if n_sites > len(candidates):
        raise ValueError("n_sites exceeds available coordinates")
    chosen_idx = rng.choice(len(candidates), size=n_sites, replace=False)
    chosen_dirs = rng.choice(dirs, size=n_sites, replace=True)

    arrow_map: Dict[Coord, str] = {}
    for i, d in zip(chosen_idx, chosen_dirs):
        arrow_map[candidates[int(i)]] = str(d)

    # Keep one deterministic directional bias near start when possible for stability.
    near = (max(0, start[0] - 1), start[1])
    if near not in {m1, m2}:
        arrow_map[near] = "E"
    return arrow_map


def _serialize_two_target_config(
    *,
    N: int,
    q: float,
    delta: float,
    start: Coord,
    m1: Coord,
    m2: Coord,
    arrow_map: Dict[Coord, str],
    geometry_kind: str,
    meta: Dict[str, object],
) -> str:
    payload = {
        "N": int(N),
        "q": float(q),
        "delta": float(delta),
        "start_0_based": [int(start[0]), int(start[1])],
        "m1_0_based": [int(m1[0]), int(m1[1])],
        "m2_0_based": [int(m2[0]), int(m2[1])],
        "arrow_sites": _arrow_map_to_json_list(arrow_map),
        "geometry_kind": geometry_kind,
        "meta": meta,
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _canonical_reflecting_specs() -> List[tuple[str, ConfigSpec]]:
    case_ids = [
        "R1",
        "R2",
        "R3",
        "R4",
        "R5",
        "R6",
        "R7",
        "C3",
        "MB1",
        "MB2",
        "MB3",
        "NB1",
        "NB2",
        "NB3",
        "NB4",
        "NB5",
    ]
    out: List[tuple[str, ConfigSpec]] = []
    for cid in case_ids:
        builder = getattr(rbp, f"build_{cid.lower()}")
        case = builder()
        spec = rbp._case_to_spec(case)
        out.append((cid, spec))
    return out


def _s0_controls() -> List[tuple[str, ConfigSpec]]:
    controls: List[tuple[str, ConfigSpec]] = []

    controls.append(
        (
            "S0a",
            ConfigSpec(
                N=30,
                q=0.8,
                g_x=-0.4,
                g_y=0.0,
                boundary_x="reflecting",
                boundary_y="reflecting",
                start=(1, 15),
                target=(30, 15),
                local_bias_arrows={},
                local_bias_delta=0.0,
                local_bias_deltas={},
                sticky_sites={(15, 15): 0.1},
                barriers_reflect=set(),
                barriers_perm={edge_key((20, 15), (21, 15)): 0.05},
            ),
        )
    )
    controls.append(
        (
            "S0b",
            ConfigSpec(
                N=30,
                q=0.8,
                g_x=-0.2,
                g_y=0.0,
                boundary_x="reflecting",
                boundary_y="reflecting",
                start=(1, 15),
                target=(30, 15),
                local_bias_arrows={},
                local_bias_delta=0.0,
                local_bias_deltas={},
                sticky_sites={(15, 15): 0.2},
                barriers_reflect=set(),
                barriers_perm={edge_key((20, 15), (21, 15)): 0.10},
            ),
        )
    )
    controls.append(
        (
            "S0c",
            ConfigSpec(
                N=30,
                q=0.6,
                g_x=-0.4,
                g_y=0.0,
                boundary_x="reflecting",
                boundary_y="reflecting",
                start=(1, 15),
                target=(30, 15),
                local_bias_arrows={},
                local_bias_delta=0.0,
                local_bias_deltas={},
                sticky_sites={(15, 15): 0.1, (16, 15): 0.2},
                barriers_reflect=set(),
                barriers_perm={edge_key((20, 15), (21, 15)): 0.08},
            ),
        )
    )
    controls.append(
        (
            "S0d",
            ConfigSpec(
                N=30,
                q=0.8,
                g_x=-0.4,
                g_y=0.0,
                boundary_x="reflecting",
                boundary_y="reflecting",
                start=(1, 15),
                target=(30, 15),
                local_bias_arrows={},
                local_bias_delta=0.0,
                local_bias_deltas={},
                sticky_sites={(10, 15): 0.2, (15, 15): 0.1},
                barriers_reflect=set(),
                barriers_perm={
                    edge_key((20, 15), (21, 15)): 0.20,
                    edge_key((22, 15), (23, 15)): 0.20,
                },
            ),
        )
    )
    return controls


def _serialize_spec(spec: ConfigSpec, *, geometry_kind: str, geometry_id: str) -> str:
    payload = {
        "geometry_id": geometry_id,
        "geometry_kind": geometry_kind,
        "N": int(spec.N),
        "q": float(spec.q),
        "g_x": float(spec.g_x),
        "g_y": float(spec.g_y),
        "boundary_x": spec.boundary_x,
        "boundary_y": spec.boundary_y,
        "start_1_based": [int(spec.start[0]), int(spec.start[1])],
        "target_1_based": [int(spec.target[0]), int(spec.target[1])],
        "local_bias_delta": float(spec.local_bias_delta),
        "local_bias_arrows": [[int(x), int(y), d] for (x, y), d in sorted(spec.local_bias_arrows.items())],
        "local_bias_deltas": [[int(x), int(y), float(v)] for (x, y), v in sorted(spec.local_bias_deltas.items())],
        "sticky_sites": [[int(x), int(y), float(v)] for (x, y), v in sorted(spec.sticky_sites.items())],
        "barriers_reflect": [
            [int(a[0]), int(a[1]), int(b[0]), int(b[1])] for (a, b) in sorted(spec.barriers_reflect)
        ],
        "barriers_perm": [
            [int(a[0]), int(a[1]), int(b[0]), int(b[1]), float(p)]
            for (a, b), p in sorted(spec.barriers_perm.items())
        ],
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _reflecting_defect_pairs(spec: ConfigSpec) -> int:
    cfg = spec_to_internal(spec)
    defects = defect_pairs_from_config(cfg)
    return int(len(defects))


def _build_two_target_geometries() -> List[Geometry]:
    N, q, delta, start, m1, m2, fast_nodes, slow_nodes = _two_target_base_geometry()
    fast_path = polyline_points(fast_nodes)
    slow_path = polyline_points(slow_nodes)

    geoms: List[Geometry] = []

    # 24 corridor geometries.
    for w2 in range(0, 6):
        for skip2 in range(0, 4):
            arrow_map, _fast_cells, _slow_cells = build_case_layout(
                N=N,
                fast_path=fast_path,
                slow_path=slow_path,
                w1=1,
                w2=w2,
                skip2=skip2,
            )
            gid = f"TT_CORR_W2{w2}_S{skip2}"
            config_json = _serialize_two_target_config(
                N=N,
                q=q,
                delta=delta,
                start=start,
                m1=m1,
                m2=m2,
                arrow_map=arrow_map,
                geometry_kind="corridor",
                meta={"w1": 1, "w2": w2, "skip2": skip2},
            )
            geoms.append(
                Geometry(
                    family="two_target",
                    geometry_id=gid,
                    geometry_kind="corridor",
                    config_json=config_json,
                    defect_pairs=_two_target_defect_pairs(N=N, q=q, delta=delta, start=start, m1=m1, arrow_map=arrow_map),
                    local_bias_sites=int(len(arrow_map)),
                    seed=-1,
                )
            )

    # 16 sparse synthetic geometries (8 budgets x 2 fixed seeds).
    budgets = [1, 2, 4, 8, 16, 32, 64, 128]
    seeds = [11, 29]
    for budget in budgets:
        for sid, seed in enumerate(seeds, start=1):
            arrow_map = _sparse_synthetic_arrow_map(
                N=N,
                n_sites=budget,
                seed=seed,
                start=start,
                m1=m1,
                m2=m2,
            )
            gid = f"TT_SYN_B{budget}_K{sid}"
            config_json = _serialize_two_target_config(
                N=N,
                q=q,
                delta=delta,
                start=start,
                m1=m1,
                m2=m2,
                arrow_map=arrow_map,
                geometry_kind="synthetic",
                meta={"budget": budget, "seed": seed},
            )
            geoms.append(
                Geometry(
                    family="two_target",
                    geometry_id=gid,
                    geometry_kind="synthetic",
                    config_json=config_json,
                    defect_pairs=_two_target_defect_pairs(N=N, q=q, delta=delta, start=start, m1=m1, arrow_map=arrow_map),
                    local_bias_sites=int(len(arrow_map)),
                    seed=seed,
                )
            )

    if len(geoms) != 40:
        raise RuntimeError(f"two_target geometry count mismatch: expected 40, got {len(geoms)}")
    return geoms


def _build_reflecting_geometries() -> List[Geometry]:
    geoms: List[Geometry] = []

    for cid, spec in _canonical_reflecting_specs():
        geoms.append(
            Geometry(
                family="reflecting",
                geometry_id=f"RF_{cid}",
                geometry_kind="canonical",
                config_json=_serialize_spec(spec, geometry_kind="canonical", geometry_id=f"RF_{cid}"),
                defect_pairs=_reflecting_defect_pairs(spec),
                local_bias_sites=int(len(spec.local_bias_arrows)),
                seed=-1,
            )
        )

    for sid, spec in _s0_controls():
        geoms.append(
            Geometry(
                family="reflecting",
                geometry_id=f"RF_{sid}",
                geometry_kind="low_defect_control",
                config_json=_serialize_spec(spec, geometry_kind="low_defect_control", geometry_id=f"RF_{sid}"),
                defect_pairs=_reflecting_defect_pairs(spec),
                local_bias_sites=int(len(spec.local_bias_arrows)),
                seed=-1,
            )
        )

    if len(geoms) != 20:
        raise RuntimeError(f"reflecting geometry count mismatch: expected 20, got {len(geoms)}")
    return geoms


def build_manifest_rows(*, aw_oversample: int, aw_r_pow10: float, defect_threshold: int) -> List[Dict[str, object]]:
    two_target_geoms = _build_two_target_geometries()
    reflecting_geoms = _build_reflecting_geometries()

    rows: List[Dict[str, object]] = []

    t_two = [300, 600, 1200]
    t_ref = [300, 1200]

    for g in two_target_geoms:
        for t_max in t_two:
            workload_id = f"{g.geometry_id}_T{t_max}"
            rows.append(
                {
                    "workload_id": workload_id,
                    "family": g.family,
                    "geometry_id": g.geometry_id,
                    "geometry_kind": g.geometry_kind,
                    "t_max": int(t_max),
                    "aw_oversample": int(aw_oversample),
                    "aw_r_pow10": float(aw_r_pow10),
                    "defect_threshold": int(defect_threshold),
                    "defect_pairs": int(g.defect_pairs),
                    "local_bias_sites": int(g.local_bias_sites),
                    "seed": int(g.seed),
                    "config_json": g.config_json,
                }
            )

    for g in reflecting_geoms:
        for t_max in t_ref:
            workload_id = f"{g.geometry_id}_T{t_max}"
            rows.append(
                {
                    "workload_id": workload_id,
                    "family": g.family,
                    "geometry_id": g.geometry_id,
                    "geometry_kind": g.geometry_kind,
                    "t_max": int(t_max),
                    "aw_oversample": int(aw_oversample),
                    "aw_r_pow10": float(aw_r_pow10),
                    "defect_threshold": int(defect_threshold),
                    "defect_pairs": int(g.defect_pairs),
                    "local_bias_sites": int(g.local_bias_sites),
                    "seed": int(g.seed),
                    "config_json": g.config_json,
                }
            )

    rows.sort(key=lambda r: (str(r["family"]), str(r["geometry_id"]), int(r["t_max"])))

    if len(rows) != 160:
        raise RuntimeError(f"workload count mismatch: expected 160, got {len(rows)}")
    return rows


def write_manifest(rows: Iterable[Dict[str, object]], out_path: Path) -> None:
    _ensure_dir(out_path)
    fields = [
        "workload_id",
        "family",
        "geometry_id",
        "geometry_kind",
        "t_max",
        "aw_oversample",
        "aw_r_pow10",
        "defect_threshold",
        "defect_pairs",
        "local_bias_sites",
        "seed",
        "config_json",
    ]
    with out_path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        for row in rows:
            w.writerow(row)


def main() -> None:
    p = argparse.ArgumentParser(description="Build fixed manifest for Luca regime map study.")
    p.add_argument(
        "--output",
        type=str,
        default=str(ROOT / "reports" / "luca_regime_map" / "data" / "manifest.csv"),
    )
    p.add_argument("--aw-oversample", type=int, default=2)
    p.add_argument("--aw-r-pow10", type=float, default=8.0)
    p.add_argument("--defect-threshold", type=int, default=120)
    args = p.parse_args()

    rows = build_manifest_rows(
        aw_oversample=args.aw_oversample,
        aw_r_pow10=args.aw_r_pow10,
        defect_threshold=args.defect_threshold,
    )

    out_path = Path(args.output)
    write_manifest(rows, out_path)

    n_two = sum(1 for r in rows if r["family"] == "two_target")
    n_ref = sum(1 for r in rows if r["family"] == "reflecting")
    g_two = len({str(r["geometry_id"]) for r in rows if r["family"] == "two_target"})
    g_ref = len({str(r["geometry_id"]) for r in rows if r["family"] == "reflecting"})
    print(
        json.dumps(
            {
                "output": str(out_path),
                "workloads": len(rows),
                "two_target_workloads": n_two,
                "reflecting_workloads": n_ref,
                "two_target_geometries": g_two,
                "reflecting_geometries": g_ref,
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
