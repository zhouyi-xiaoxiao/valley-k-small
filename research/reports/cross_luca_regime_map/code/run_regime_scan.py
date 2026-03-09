#!/usr/bin/env python3
"""Run cross-report Luca regime benchmark under fixed full-FPT fairness."""

from __future__ import annotations

import argparse
import csv
import json
import os
import platform
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Tuple

# Keep BLAS single-threaded for stable timing.
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
TT_CODE = ROOT / "reports" / "2d_two_target_double_peak" / "code"
REF_CODE = ROOT / "reports" / "2d_reflecting_bimodality" / "code"
BIMOD_CODE = ROOT / "reports" / "grid2d_bimodality" / "code"

# Order aligned with existing reflecting benchmark stack.
sys.path.insert(0, str(REF_CODE))
sys.path.insert(1, str(BIMOD_CODE))
sys.path.insert(2, str(TT_CODE))

from compare_numeric_methods import (  # noqa: E402
    build_transient_system,
    choose_aw_grid,
    run_aw_defect_giuggioli,
    run_aw_fft,
    run_dense_recursion,
    run_linear_mfpt,
)
from fpt_aw_inversion import fpt_pmf_aw  # noqa: E402
from fpt_exact_mc import exact_fpt  # noqa: E402
from heterogeneity_determinant import defect_pairs_from_config  # noqa: E402
from model_core import ConfigSpec, LatticeConfig, build_exact_arrays, edge_key, spec_to_internal  # noqa: E402
from propagator_z_analytic import defect_free_propagator_from_config  # noqa: E402
from two_target_2d_report import build_transition_arrays, run_exact_two_target  # noqa: E402

Coord = Tuple[int, int]


@dataclass(frozen=True)
class Workload:
    workload_id: str
    family: str
    geometry_id: str
    geometry_kind: str
    t_max: int
    aw_oversample: int
    aw_r_pow10: float
    defect_threshold: int
    defect_pairs: int
    local_bias_sites: int
    seed: int
    config_json: str


def _to_tuple2(v: Iterable[Any]) -> Coord:
    arr = list(v)
    return (int(arr[0]), int(arr[1]))


def _median(vals: List[float]) -> float:
    if not vals:
        return 0.0
    return float(np.median(np.asarray(vals, dtype=np.float64)))


def _defect_bin(n_defects: int) -> str:
    d = int(n_defects)
    if d <= 20:
        return "[0,20]"
    if d <= 60:
        return "[21,60]"
    if d <= 120:
        return "[61,120]"
    if d <= 300:
        return "[121,300]"
    if d <= 700:
        return "[301,700]"
    return "[701,+inf)"


def _load_manifest(path: Path) -> List[Workload]:
    rows: List[Workload] = []
    with path.open("r", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for r in reader:
            rows.append(
                Workload(
                    workload_id=str(r["workload_id"]),
                    family=str(r["family"]),
                    geometry_id=str(r["geometry_id"]),
                    geometry_kind=str(r["geometry_kind"]),
                    t_max=int(r["t_max"]),
                    aw_oversample=int(r["aw_oversample"]),
                    aw_r_pow10=float(r["aw_r_pow10"]),
                    defect_threshold=int(r["defect_threshold"]),
                    defect_pairs=int(r["defect_pairs"]),
                    local_bias_sites=int(r["local_bias_sites"]),
                    seed=int(r["seed"]),
                    config_json=str(r["config_json"]),
                )
            )
    return rows


def _deserialize_two_target(config_json: str) -> Dict[str, Any]:
    obj = json.loads(config_json)
    arrow_map = {(int(x), int(y)): str(d) for x, y, d in obj["arrow_sites"]}
    return {
        "N": int(obj["N"]),
        "q": float(obj["q"]),
        "delta": float(obj["delta"]),
        "start": _to_tuple2(obj["start_0_based"]),
        "m1": _to_tuple2(obj["m1_0_based"]),
        "m2": _to_tuple2(obj["m2_0_based"]),
        "arrow_map": arrow_map,
        "meta": obj.get("meta", {}),
    }


def _deserialize_reflecting_spec(config_json: str) -> ConfigSpec:
    obj = json.loads(config_json)
    local_bias_arrows = {(int(x), int(y)): str(d) for x, y, d in obj["local_bias_arrows"]}
    local_bias_deltas = {(int(x), int(y)): float(v) for x, y, v in obj["local_bias_deltas"]}
    sticky_sites = {(int(x), int(y)): float(v) for x, y, v in obj["sticky_sites"]}
    barriers_reflect = {
        edge_key((int(x1), int(y1)), (int(x2), int(y2))) for x1, y1, x2, y2 in obj["barriers_reflect"]
    }
    barriers_perm = {
        edge_key((int(x1), int(y1)), (int(x2), int(y2))): float(p)
        for x1, y1, x2, y2, p in obj["barriers_perm"]
    }

    return ConfigSpec(
        N=int(obj["N"]),
        q=float(obj["q"]),
        g_x=float(obj["g_x"]),
        g_y=float(obj["g_y"]),
        boundary_x=str(obj["boundary_x"]),
        boundary_y=str(obj["boundary_y"]),
        start=_to_tuple2(obj["start_1_based"]),
        target=_to_tuple2(obj["target_1_based"]),
        local_bias_arrows=local_bias_arrows,
        local_bias_delta=float(obj["local_bias_delta"]),
        local_bias_deltas=local_bias_deltas,
        sticky_sites=sticky_sites,
        barriers_reflect=barriers_reflect,
        barriers_perm=barriers_perm,
    )


def _time_repeated(
    fn: Callable[[], Dict[str, Any]],
    *,
    warmup: int,
    repeats: int,
) -> tuple[List[float], List[float], Dict[str, Any]]:
    for _ in range(max(0, warmup)):
        fn()

    reported: List[float] = []
    wall: List[float] = []
    last_payload: Dict[str, Any] = {}

    for _ in range(max(1, repeats)):
        t0 = time.perf_counter()
        payload = fn()
        elapsed = time.perf_counter() - t0
        wall.append(float(elapsed))
        reported.append(float(payload.get("reported_seconds", elapsed)))
        last_payload = payload

    return reported, wall, last_payload


def _two_target_prepare(cfg_obj: Dict[str, Any]) -> Dict[str, Any]:
    N = int(cfg_obj["N"])
    q = float(cfg_obj["q"])
    delta = float(cfg_obj["delta"])
    start = cfg_obj["start"]
    m1 = cfg_obj["m1"]
    m2 = cfg_obj["m2"]
    arrow_map = dict(cfg_obj["arrow_map"])

    src_idx, dst_idx, probs = build_transition_arrays(
        N=N,
        q=q,
        delta=delta,
        arrow_map=arrow_map,
    )
    sys_data = build_transient_system(
        N=N,
        src_idx=src_idx,
        dst_idx=dst_idx,
        probs=probs,
        start=start,
        m1=m1,
        m2=m2,
    )

    return {
        "N": N,
        "q": q,
        "delta": delta,
        "start": start,
        "m1": m1,
        "m2": m2,
        "arrow_map": arrow_map,
        "src_idx": src_idx,
        "dst_idx": dst_idx,
        "probs": probs,
        "Q": sys_data["Q"],
        "r1": sys_data["r1"],
        "r2": sys_data["r2"],
        "alpha": sys_data["alpha"],
        "i_start_t": int(sys_data["i_start_t"][0]),
    }


def _reflecting_prepare(spec: ConfigSpec) -> Dict[str, Any]:
    cfg = spec_to_internal(spec)
    return {"spec": spec, "cfg": cfg}


def _two_target_sparse_once(prep: Dict[str, Any], t_max: int) -> Dict[str, Any]:
    f_any, _f1, _f2, _surv = run_exact_two_target(
        N=prep["N"],
        start=prep["start"],
        target1=prep["m1"],
        target2=prep["m2"],
        src_idx=prep["src_idx"],
        dst_idx=prep["dst_idx"],
        probs=prep["probs"],
        t_max=t_max,
        surv_tol=0.0,
    )
    return {
        "reported_seconds": 0.0,
        "f_any": f_any.astype(np.float64, copy=False),
    }


def _two_target_linear_once(prep: Dict[str, Any]) -> Dict[str, Any]:
    out = run_linear_mfpt(
        Q=prep["Q"],
        r1=prep["r1"],
        r2=prep["r2"],
        i_start_t=prep["i_start_t"],
    )
    return {
        "reported_seconds": 0.0,
        "linear": out,
    }


def _two_target_luca_full_once(prep: Dict[str, Any], t_max: int, oversample: int, r_pow10: float) -> Dict[str, Any]:
    out = run_aw_defect_giuggioli(
        N=prep["N"],
        q=prep["q"],
        start=prep["start"],
        m1=prep["m1"],
        m2=prep["m2"],
        arrow_map=prep["arrow_map"],
        delta=prep["delta"],
        t_max_aw=t_max,
        oversample=oversample,
        r_pow10=r_pow10,
    )
    f_any = np.concatenate([[0.0], out["f_any"]]).astype(np.float64, copy=False)
    return {
        "reported_seconds": 0.0,
        "f_any": f_any,
        "defect_pairs": int(out["defect_pairs"]),
        "defect_nodes": int(out["defect_nodes"]),
    }


def _two_target_luca_estimate_once(
    prep: Dict[str, Any],
    *,
    t_max: int,
    oversample: int,
    r_pow10: float,
    eval_nz: int,
) -> Dict[str, Any]:
    # Imported locally to avoid unnecessary startup cost in sparse-only sections.
    from heterogeneity_determinant import defect_pairs_from_config  # type: ignore
    from model_core import LatticeConfig  # type: ignore
    from propagator_z_analytic import defect_free_propagator_from_config  # type: ignore

    map_dir = {"E": "right", "W": "left", "N": "down", "S": "up"}
    local_bias_arrows = {xy: map_dir[d] for xy, d in prep["arrow_map"].items()}

    t0 = time.perf_counter()
    cfg = LatticeConfig(
        N=prep["N"],
        q=prep["q"],
        g_x=0.0,
        g_y=0.0,
        boundary_x="reflecting",
        boundary_y="reflecting",
        start=prep["start"],
        target=prep["m1"],
        local_bias_arrows=local_bias_arrows,
        local_bias_delta=float(prep["delta"]),
        sticky_sites={},
        barriers_reflect=set(),
        barriers_perm={},
    )
    base = defect_free_propagator_from_config(cfg)
    defects = defect_pairs_from_config(cfg)
    nodes = {prep["start"], prep["m1"], prep["m2"]}
    for d in defects:
        nodes.add(d.u)
        nodes.add(d.v)
    nodes_list = sorted(nodes)
    node_index = {n: i for i, n in enumerate(nodes_list)}

    pair_eval = base.prepare_pair_evaluator(nodes_list, nodes_list)
    U = np.array([node_index[d.u] for d in defects], dtype=np.int64)
    V = np.array([node_index[d.v] for d in defects], dtype=np.int64)
    delta_vec = np.array([-d.eta_uv for d in defects], dtype=np.complex128)
    src_idx = np.array([node_index[prep["start"]], node_index[prep["m1"]], node_index[prep["m2"]]], dtype=np.int64)
    dst_idx = np.array([node_index[prep["m1"]], node_index[prep["m2"]]], dtype=np.int64)

    grid = choose_aw_grid(t_max=t_max, oversample=oversample, r_pow10=r_pow10)
    m = int(grid.m)
    t_setup = time.perf_counter() - t0

    nz = min(max(1, int(eval_nz)), m)
    idx = np.linspace(0, m - 1, num=nz, endpoint=False).astype(np.int64)
    z = grid.r * np.exp(1j * 2.0 * np.pi * idx / float(m))

    if len(defects) > 0:
        eye = np.eye(len(defects), dtype=np.complex128)
    else:
        eye = np.zeros((0, 0), dtype=np.complex128)

    t0 = time.perf_counter()
    for zi in z:
        P = pair_eval.evaluate(zi)
        if len(defects) > 0:
            P_vu = P[np.ix_(V, U)]
            A = eye - zi * (P_vu * delta_vec[None, :])
            B = P[np.ix_(V, dst_idx)]
            X = np.linalg.solve(A + 1e-12 * eye, B)
            P_su = P[np.ix_(src_idx, U)]
            ST = P[np.ix_(src_idx, dst_idx)] + zi * ((P_su * delta_vec[None, :]) @ X)
        else:
            ST = P[np.ix_(src_idx, dst_idx)]

        Ps1, Ps2 = ST[0, 0], ST[0, 1]
        P11, P12 = ST[1, 0], ST[1, 1]
        P21, P22 = ST[2, 0], ST[2, 1]
        G = np.array([[P11, P21], [P12, P22]], dtype=np.complex128)
        b = np.array([Ps1, Ps2], dtype=np.complex128)
        _ = np.linalg.solve(G + 1e-12 * np.eye(2, dtype=np.complex128), b)
    t_eval = time.perf_counter() - t0

    rng = np.random.default_rng(0)
    arr = rng.standard_normal(m) + 1j * rng.standard_normal(m)
    t0 = time.perf_counter()
    _ = np.fft.fft(arr)
    t_fft = time.perf_counter() - t0

    est_total = float(t_setup + (t_eval / float(nz)) * float(m) + t_fft)
    return {
        "reported_seconds": est_total,
        "estimate_components": {
            "setup_seconds": float(t_setup),
            "eval_seconds_sampled": float(t_eval),
            "eval_nz": int(nz),
            "m": int(m),
            "fft_seconds": float(t_fft),
            "estimated_total_seconds": est_total,
            "defect_pairs": int(len(defects)),
            "defect_nodes": int(len(nodes_list)),
        },
    }


def _reflecting_sparse_once(prep: Dict[str, Any], t_max: int) -> Dict[str, Any]:
    f, _p_abs = exact_fpt(prep["cfg"], t_max=t_max)
    f = np.concatenate([[0.0], f]).astype(np.float64, copy=False)
    return {
        "reported_seconds": 0.0,
        "f_any": f,
    }


def _reflecting_linear_once(prep: Dict[str, Any]) -> Dict[str, Any]:
    src_idx, dst_idx, probs, r, index = build_exact_arrays(prep["cfg"])
    n_t = int(len(r))
    Q = np.zeros((n_t, n_t), dtype=np.float64)
    np.add.at(Q, (src_idx, dst_idx), probs)
    A = np.eye(n_t, dtype=np.float64) - Q
    one = np.ones(n_t, dtype=np.float64)
    m = np.linalg.solve(A, one)
    i_start = int(index[prep["cfg"].start])
    return {
        "reported_seconds": 0.0,
        "linear": {
            "mfpt_exact": float(m[i_start]),
            "n_transient": n_t,
        },
    }


def _reflecting_luca_full_once(prep: Dict[str, Any], t_max: int, oversample: int, r_pow10: float) -> Dict[str, Any]:
    f_aw, params = fpt_pmf_aw(prep["cfg"], t_max=t_max, oversample=oversample, r_pow10=r_pow10)
    f_any = np.concatenate([[0.0], f_aw]).astype(np.float64, copy=False)
    defects = defect_pairs_from_config(prep["cfg"])
    return {
        "reported_seconds": 0.0,
        "f_any": f_any,
        "aw_grid": {"m": int(params.m), "r": float(params.r)},
        "defect_pairs": int(len(defects)),
    }


def _reflecting_luca_estimate_once(
    prep: Dict[str, Any],
    *,
    t_max: int,
    oversample: int,
    r_pow10: float,
    eval_nz: int,
) -> Dict[str, Any]:
    from aw_pgf import choose_aw_params  # type: ignore

    t0 = time.perf_counter()
    base = defect_free_propagator_from_config(prep["cfg"])
    defects = defect_pairs_from_config(prep["cfg"])

    from heterogeneity_determinant import DefectSystem  # type: ignore

    system = DefectSystem(base=base, defects=defects, start=prep["cfg"].start, target=prep["cfg"].target)
    params = choose_aw_params(t_max, oversample=oversample, r_pow10=r_pow10)
    m = int(params.m)
    t_setup = time.perf_counter() - t0

    nz = min(max(1, int(eval_nz)), m)
    idx = np.linspace(0, m - 1, num=nz, endpoint=False).astype(np.int64)
    z_grid = params.r * np.exp(1j * 2.0 * np.pi * idx / float(m))

    t0 = time.perf_counter()
    for z in z_grid:
        _ = system.propagators(z)
    t_eval = time.perf_counter() - t0

    rng = np.random.default_rng(0)
    arr = rng.standard_normal(m) + 1j * rng.standard_normal(m)
    t0 = time.perf_counter()
    _ = np.fft.fft(arr)
    t_fft = time.perf_counter() - t0

    est_total = float(t_setup + (t_eval / float(nz)) * float(m) + t_fft)
    return {
        "reported_seconds": est_total,
        "estimate_components": {
            "setup_seconds": float(t_setup),
            "eval_seconds_sampled": float(t_eval),
            "eval_nz": int(nz),
            "m": int(m),
            "fft_seconds": float(t_fft),
            "estimated_total_seconds": est_total,
            "defect_pairs": int(len(defects)),
        },
    }


def _l1_linf(a: np.ndarray, b: np.ndarray) -> Dict[str, float]:
    n = min(len(a), len(b))
    if n <= 0:
        return {"l1": 0.0, "linf": 0.0}
    d = np.abs(a[:n] - b[:n])
    return {"l1": float(d.sum()), "linf": float(d.max())}


def _run_main_workload(
    w: Workload,
    *,
    prep_cache_tt: Dict[str, Dict[str, Any]],
    prep_cache_rf: Dict[str, Dict[str, Any]],
    warmup: int,
    repeats: int,
    eval_nz: int,
) -> Dict[str, Any]:
    if w.family == "two_target":
        if w.geometry_id not in prep_cache_tt:
            prep_cache_tt[w.geometry_id] = _two_target_prepare(_deserialize_two_target(w.config_json))
        prep = prep_cache_tt[w.geometry_id]

        sparse_rep, sparse_wall, sparse_payload = _time_repeated(
            lambda: _two_target_sparse_once(prep, w.t_max),
            warmup=warmup,
            repeats=repeats,
        )
        sparse_time = _median(sparse_wall)
        f_sparse = sparse_payload["f_any"]

        linear_rep, linear_wall, linear_payload = _time_repeated(
            lambda: _two_target_linear_once(prep),
            warmup=warmup,
            repeats=repeats,
        )
        linear_time = _median(linear_wall)

        if w.defect_pairs <= w.defect_threshold:
            luca_mode = "full"
            luca_rep, luca_wall, luca_payload = _time_repeated(
                lambda: _two_target_luca_full_once(prep, w.t_max, w.aw_oversample, w.aw_r_pow10),
                warmup=warmup,
                repeats=repeats,
            )
            luca_time = _median(luca_wall)
            f_luca = luca_payload["f_any"]
            err = _l1_linf(f_luca, f_sparse)
            est_components = None
        else:
            luca_mode = "estimate"
            luca_rep, luca_wall, luca_payload = _time_repeated(
                lambda: _two_target_luca_estimate_once(
                    prep,
                    t_max=w.t_max,
                    oversample=w.aw_oversample,
                    r_pow10=w.aw_r_pow10,
                    eval_nz=eval_nz,
                ),
                warmup=warmup,
                repeats=repeats,
            )
            luca_time = _median(luca_rep)
            err = None
            est_components = luca_payload.get("estimate_components")

    elif w.family == "reflecting":
        if w.geometry_id not in prep_cache_rf:
            prep_cache_rf[w.geometry_id] = _reflecting_prepare(_deserialize_reflecting_spec(w.config_json))
        prep = prep_cache_rf[w.geometry_id]

        sparse_rep, sparse_wall, sparse_payload = _time_repeated(
            lambda: _reflecting_sparse_once(prep, w.t_max),
            warmup=warmup,
            repeats=repeats,
        )
        sparse_time = _median(sparse_wall)
        f_sparse = sparse_payload["f_any"]

        linear_rep, linear_wall, linear_payload = _time_repeated(
            lambda: _reflecting_linear_once(prep),
            warmup=warmup,
            repeats=repeats,
        )
        linear_time = _median(linear_wall)

        if w.defect_pairs <= w.defect_threshold:
            luca_mode = "full"
            luca_rep, luca_wall, luca_payload = _time_repeated(
                lambda: _reflecting_luca_full_once(prep, w.t_max, w.aw_oversample, w.aw_r_pow10),
                warmup=warmup,
                repeats=repeats,
            )
            luca_time = _median(luca_wall)
            f_luca = luca_payload["f_any"]
            err = _l1_linf(f_luca, f_sparse)
            est_components = None
        else:
            luca_mode = "estimate"
            luca_rep, luca_wall, luca_payload = _time_repeated(
                lambda: _reflecting_luca_estimate_once(
                    prep,
                    t_max=w.t_max,
                    oversample=w.aw_oversample,
                    r_pow10=w.aw_r_pow10,
                    eval_nz=eval_nz,
                ),
                warmup=warmup,
                repeats=repeats,
            )
            luca_time = _median(luca_rep)
            err = None
            est_components = luca_payload.get("estimate_components")
    else:
        raise ValueError(f"unknown family: {w.family}")

    speedup = float(sparse_time / luca_time) if luca_time > 0 else float("inf")
    winner = "luca" if luca_time < sparse_time else "sparse"

    return {
        "workload_id": w.workload_id,
        "family": w.family,
        "geometry_id": w.geometry_id,
        "geometry_kind": w.geometry_kind,
        "t_max": int(w.t_max),
        "defect_pairs": int(w.defect_pairs),
        "local_bias_sites": int(w.local_bias_sites),
        "defect_bin": _defect_bin(w.defect_pairs),
        "sparse_seconds": float(sparse_time),
        "luca_seconds": float(luca_time),
        "linear_mfpt_seconds": float(linear_time),
        "luca_mode": luca_mode,
        "speedup_sparse_over_luca": float(speedup),
        "winner_fullfpt": winner,
        "sparse_wall_samples": json.dumps([float(x) for x in sparse_wall]),
        "luca_reported_samples": json.dumps([float(x) for x in luca_rep]),
        "luca_wall_samples": json.dumps([float(x) for x in luca_wall]),
        "linear_wall_samples": json.dumps([float(x) for x in linear_wall]),
        "l1_error": None if err is None else float(err["l1"]),
        "linf_error": None if err is None else float(err["linf"]),
        "estimation_components_json": None if est_components is None else json.dumps(est_components, ensure_ascii=False),
    }


def _write_runtime_raw(rows: List[Dict[str, Any]], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "workload_id",
        "family",
        "geometry_id",
        "geometry_kind",
        "t_max",
        "defect_pairs",
        "local_bias_sites",
        "defect_bin",
        "sparse_seconds",
        "luca_seconds",
        "linear_mfpt_seconds",
        "luca_mode",
        "speedup_sparse_over_luca",
        "winner_fullfpt",
        "sparse_wall_samples",
        "luca_reported_samples",
        "luca_wall_samples",
        "linear_wall_samples",
        "l1_error",
        "linf_error",
        "estimation_components_json",
    ]
    with out_path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        for row in rows:
            w.writerow(row)


def _aggregate_by(rows: List[Dict[str, Any]], key_fn: Callable[[Dict[str, Any]], Tuple[Any, ...]]) -> List[Dict[str, Any]]:
    groups: Dict[Tuple[Any, ...], List[Dict[str, Any]]] = {}
    for r in rows:
        key = key_fn(r)
        groups.setdefault(key, []).append(r)

    out: List[Dict[str, Any]] = []
    for key in sorted(groups):
        arr = groups[key]
        R = np.asarray([float(r["speedup_sparse_over_luca"]) for r in arr], dtype=np.float64)
        out.append(
            {
                "key": list(key),
                "count": int(len(arr)),
                "median_R": float(np.median(R)),
                "mean_R": float(np.mean(R)),
                "p_luca_faster": float(np.mean(R > 1.0)),
                "n_luca_faster": int(np.sum(R > 1.0)),
            }
        )
    return out


def _estimation_validation(
    rows: List[Dict[str, Any]],
    workloads_by_id: Dict[str, Workload],
    *,
    prep_cache_tt: Dict[str, Dict[str, Any]],
    prep_cache_rf: Dict[str, Dict[str, Any]],
    anchors_required: int,
    warmup: int,
    repeats: int,
    eval_nz: int,
) -> Dict[str, Any]:
    candidates = [
        r
        for r in rows
        if int(r["defect_pairs"]) <= int(workloads_by_id[str(r["workload_id"])].defect_threshold)
    ]
    # Prefer medium bin + low bin coverage.
    candidates.sort(key=lambda r: (str(r["defect_bin"]), str(r["family"]), str(r["workload_id"])))
    anchors = candidates[: max(0, anchors_required)]

    checks: List[Dict[str, Any]] = []
    for base in anchors:
        w = workloads_by_id[str(base["workload_id"])]
        if w.family == "two_target":
            prep = prep_cache_tt[w.geometry_id]
            full_rep, full_wall, _ = _time_repeated(
                lambda: _two_target_luca_full_once(prep, w.t_max, w.aw_oversample, w.aw_r_pow10),
                warmup=warmup,
                repeats=repeats,
            )
            est_rep, est_wall, _ = _time_repeated(
                lambda: _two_target_luca_estimate_once(
                    prep,
                    t_max=w.t_max,
                    oversample=w.aw_oversample,
                    r_pow10=w.aw_r_pow10,
                    eval_nz=eval_nz,
                ),
                warmup=warmup,
                repeats=repeats,
            )
            full_t = _median(full_wall)
            est_t = _median(est_rep)
        else:
            prep = prep_cache_rf[w.geometry_id]
            full_rep, full_wall, _ = _time_repeated(
                lambda: _reflecting_luca_full_once(prep, w.t_max, w.aw_oversample, w.aw_r_pow10),
                warmup=warmup,
                repeats=repeats,
            )
            est_rep, est_wall, _ = _time_repeated(
                lambda: _reflecting_luca_estimate_once(
                    prep,
                    t_max=w.t_max,
                    oversample=w.aw_oversample,
                    r_pow10=w.aw_r_pow10,
                    eval_nz=eval_nz,
                ),
                warmup=warmup,
                repeats=repeats,
            )
            full_t = _median(full_wall)
            est_t = _median(est_rep)

        rel = abs(est_t - full_t) / full_t if full_t > 0 else 0.0
        checks.append(
            {
                "workload_id": w.workload_id,
                "family": w.family,
                "defect_pairs": int(w.defect_pairs),
                "t_max": int(w.t_max),
                "full_seconds": float(full_t),
                "estimate_seconds": float(est_t),
                "relative_error": float(rel),
            }
        )

    med_rel = float(np.median(np.asarray([c["relative_error"] for c in checks], dtype=np.float64))) if checks else 0.0
    return {
        "n_anchors": int(len(checks)),
        "target_anchors": int(anchors_required),
        "median_relative_error": med_rel,
        "pass_threshold_25pct": bool(med_rel <= 0.25),
        "checks": checks,
    }


def _consistency_checks(rows: List[Dict[str, Any]], *, n_checks: int = 12) -> Dict[str, Any]:
    cand = [r for r in rows if r["l1_error"] is not None]
    # Prefer low+medium defect samples.
    cand.sort(key=lambda r: (int(r["defect_pairs"]), int(r["t_max"]), str(r["workload_id"])))
    chosen = cand[: max(0, n_checks)]
    out = [
        {
            "workload_id": str(r["workload_id"]),
            "family": str(r["family"]),
            "defect_pairs": int(r["defect_pairs"]),
            "t_max": int(r["t_max"]),
            "l1_error": float(r["l1_error"]),
            "linf_error": float(r["linf_error"]),
        }
        for r in chosen
    ]
    return {
        "n_checks": int(len(out)),
        "checks": out,
    }


def _two_target_anchor_baselines(
    workloads_by_id: Dict[str, Workload],
    prep_cache_tt: Dict[str, Dict[str, Any]],
) -> List[Dict[str, Any]]:
    anchors = [
        ("low_defect", "TT_SYN_B1_K1_T300"),
        ("high_defect", "TT_CORR_W23_S2_T300"),
    ]

    rows: List[Dict[str, Any]] = []
    for label, wid in anchors:
        w = workloads_by_id.get(wid)
        if w is None:
            continue
        prep = prep_cache_tt[w.geometry_id]

        t0 = time.perf_counter()
        f_sparse, _f1, _f2, _surv = run_exact_two_target(
            N=prep["N"],
            start=prep["start"],
            target1=prep["m1"],
            target2=prep["m2"],
            src_idx=prep["src_idx"],
            dst_idx=prep["dst_idx"],
            probs=prep["probs"],
            t_max=w.t_max,
            surv_tol=0.0,
        )
        t_sparse = time.perf_counter() - t0

        t0 = time.perf_counter()
        f_dense, _fd1, _fd2, _sd = run_dense_recursion(
            Q=prep["Q"],
            r1=prep["r1"],
            r2=prep["r2"],
            alpha=prep["alpha"],
            t_max=w.t_max,
            surv_tol=0.0,
        )
        t_dense = time.perf_counter() - t0

        t0 = time.perf_counter()
        aw = run_aw_fft(
            Q=prep["Q"],
            r1=prep["r1"],
            r2=prep["r2"],
            alpha=prep["alpha"],
            t_max_aw=w.t_max,
            oversample=w.aw_oversample,
            r_pow10=w.aw_r_pow10,
        )
        t_aw = time.perf_counter() - t0

        t0 = time.perf_counter()
        luca = run_aw_defect_giuggioli(
            N=prep["N"],
            q=prep["q"],
            start=prep["start"],
            m1=prep["m1"],
            m2=prep["m2"],
            arrow_map=prep["arrow_map"],
            delta=prep["delta"],
            t_max_aw=w.t_max,
            oversample=w.aw_oversample,
            r_pow10=w.aw_r_pow10,
        )
        t_luca = time.perf_counter() - t0

        t0 = time.perf_counter()
        linear = run_linear_mfpt(Q=prep["Q"], r1=prep["r1"], r2=prep["r2"], i_start_t=prep["i_start_t"])
        t_linear = time.perf_counter() - t0

        f_aw = np.concatenate([[0.0], aw["f_any"]])
        f_luca = np.concatenate([[0.0], luca["f_any"]])

        rows.append(
            {
                "anchor_label": label,
                "workload_id": wid,
                "defect_pairs": int(w.defect_pairs),
                "t_max": int(w.t_max),
                "sparse_seconds": float(t_sparse),
                "dense_seconds": float(t_dense),
                "full_aw_seconds": float(t_aw),
                "luca_seconds": float(t_luca),
                "linear_seconds": float(t_linear),
                "dense_vs_sparse_l1": float(np.abs(f_dense[: len(f_sparse)] - f_sparse).sum()),
                "aw_vs_sparse_l1": float(np.abs(f_aw[: len(f_sparse)] - f_sparse).sum()),
                "luca_vs_sparse_l1": float(np.abs(f_luca[: len(f_sparse)] - f_sparse).sum()),
                "linear_mfpt": float(linear["mfpt_exact"]),
            }
        )
    return rows


def _summary_payload(
    rows: List[Dict[str, Any]],
    *,
    manifest_path: Path,
    runtime_raw_path: Path,
    workloads_by_id: Dict[str, Workload],
    prep_cache_tt: Dict[str, Dict[str, Any]],
    prep_cache_rf: Dict[str, Dict[str, Any]],
    estimation_validation: Dict[str, Any],
    consistency: Dict[str, Any],
) -> Dict[str, Any]:
    R = np.asarray([float(r["speedup_sparse_over_luca"]) for r in rows], dtype=np.float64)
    pooled_luca_win = bool(np.any(R > 1.0))

    by_family = _aggregate_by(rows, key_fn=lambda r: (str(r["family"]),))
    by_family_t = _aggregate_by(rows, key_fn=lambda r: (str(r["family"]), int(r["t_max"])))
    by_family_bin_t = _aggregate_by(rows, key_fn=lambda r: (str(r["family"]), str(r["defect_bin"]), int(r["t_max"])))
    pooled_bin_t = _aggregate_by(rows, key_fn=lambda r: ("pooled", str(r["defect_bin"]), int(r["t_max"])))

    n_est = int(sum(1 for r in rows if r["luca_mode"] == "estimate"))
    n_full = int(sum(1 for r in rows if r["luca_mode"] == "full"))

    anchor_baselines = _two_target_anchor_baselines(workloads_by_id, prep_cache_tt)

    return {
        "meta": {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "python": sys.version.split()[0],
            "numpy": np.__version__,
            "platform": platform.platform(),
            "manifest": str(manifest_path),
            "runtime_raw": str(runtime_raw_path),
            "thread_env": {
                "OMP_NUM_THREADS": os.environ.get("OMP_NUM_THREADS"),
                "OPENBLAS_NUM_THREADS": os.environ.get("OPENBLAS_NUM_THREADS"),
                "MKL_NUM_THREADS": os.environ.get("MKL_NUM_THREADS"),
            },
        },
        "policy": {
            "fairness": "fixed_t_full_fpt",
            "winner_metric": "argmin(sparse_seconds, luca_seconds)",
            "speedup_ratio": "R=sparse_seconds/luca_seconds",
            "no_mixed_absolute_seconds_for_cross_family_claims": True,
            "luca_mode_threshold_defect_pairs": int(next(iter(workloads_by_id.values())).defect_threshold if workloads_by_id else 120),
        },
        "counts": {
            "workloads": int(len(rows)),
            "families": {
                "two_target": int(sum(1 for r in rows if r["family"] == "two_target")),
                "reflecting": int(sum(1 for r in rows if r["family"] == "reflecting")),
            },
            "luca_mode": {"full": n_full, "estimate": n_est},
        },
        "pooled": {
            "median_R": float(np.median(R)) if len(R) else 0.0,
            "mean_R": float(np.mean(R)) if len(R) else 0.0,
            "p_luca_faster": float(np.mean(R > 1.0)) if len(R) else 0.0,
            "n_luca_faster": int(np.sum(R > 1.0)) if len(R) else 0,
            "has_luca_win_region": pooled_luca_win,
            "no_win_statement": (
                "No Luca winning region under fixed-T full-FPT fairness."
                if not pooled_luca_win
                else "Luca has winning regions under fixed-T full-FPT fairness."
            ),
        },
        "aggregates": {
            "by_family": by_family,
            "by_family_t": by_family_t,
            "by_family_bin_t": by_family_bin_t,
            "pooled_bin_t": pooled_bin_t,
        },
        "estimation_validation": estimation_validation,
        "consistency_checks": consistency,
        "anchor_baselines": anchor_baselines,
    }


def _write_summary(payload: Dict[str, Any], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    p = argparse.ArgumentParser(description="Run Luca regime scan on manifest workloads.")
    p.add_argument(
        "--manifest",
        type=str,
        default=str(ROOT / "reports" / "luca_regime_map" / "data" / "manifest.csv"),
    )
    p.add_argument(
        "--runtime-raw",
        type=str,
        default=str(ROOT / "reports" / "luca_regime_map" / "data" / "runtime_raw.csv"),
    )
    p.add_argument(
        "--runtime-summary",
        type=str,
        default=str(ROOT / "reports" / "luca_regime_map" / "data" / "runtime_summary.json"),
    )
    p.add_argument("--warmup", type=int, default=1)
    p.add_argument("--repeats", type=int, default=3)
    p.add_argument("--eval-nz", type=int, default=32)
    p.add_argument("--limit", type=int, default=0, help="Optional workload limit for smoke runs.")
    p.add_argument("--families", type=str, default="", help="Optional CSV filter: two_target,reflecting")
    p.add_argument("--estimation-anchors", type=int, default=8)
    args = p.parse_args()

    manifest_path = Path(args.manifest)
    raw_path = Path(args.runtime_raw)
    summary_path = Path(args.runtime_summary)

    workloads = _load_manifest(manifest_path)
    if args.families.strip():
        allow = {x.strip() for x in args.families.split(",") if x.strip()}
        workloads = [w for w in workloads if w.family in allow]
    if args.limit and args.limit > 0:
        workloads = workloads[: args.limit]

    prep_cache_tt: Dict[str, Dict[str, Any]] = {}
    prep_cache_rf: Dict[str, Dict[str, Any]] = {}

    rows: List[Dict[str, Any]] = []
    t0_all = time.perf_counter()
    for i, w in enumerate(workloads, start=1):
        row = _run_main_workload(
            w,
            prep_cache_tt=prep_cache_tt,
            prep_cache_rf=prep_cache_rf,
            warmup=args.warmup,
            repeats=args.repeats,
            eval_nz=args.eval_nz,
        )
        rows.append(row)
        if i % 5 == 0 or i == len(workloads):
            elapsed = time.perf_counter() - t0_all
            print(f"[progress] {i}/{len(workloads)} workloads, elapsed={elapsed:.1f}s")

    _write_runtime_raw(rows, raw_path)

    workloads_by_id = {w.workload_id: w for w in workloads}
    estimation_validation = _estimation_validation(
        rows,
        workloads_by_id,
        prep_cache_tt=prep_cache_tt,
        prep_cache_rf=prep_cache_rf,
        anchors_required=args.estimation_anchors,
        warmup=max(0, args.warmup - 1),
        repeats=max(1, min(2, args.repeats)),
        eval_nz=args.eval_nz,
    )
    consistency = _consistency_checks(rows, n_checks=12)

    summary = _summary_payload(
        rows,
        manifest_path=manifest_path,
        runtime_raw_path=raw_path,
        workloads_by_id=workloads_by_id,
        prep_cache_tt=prep_cache_tt,
        prep_cache_rf=prep_cache_rf,
        estimation_validation=estimation_validation,
        consistency=consistency,
    )
    _write_summary(summary, summary_path)

    print(
        json.dumps(
            {
                "runtime_raw": str(raw_path),
                "runtime_summary": str(summary_path),
                "workloads": len(rows),
                "median_R": summary["pooled"]["median_R"],
                "p_luca_faster": summary["pooled"]["p_luca_faster"],
                "has_luca_win_region": summary["pooled"]["has_luca_win_region"],
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
