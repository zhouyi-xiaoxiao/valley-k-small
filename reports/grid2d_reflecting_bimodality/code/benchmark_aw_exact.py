#!/usr/bin/env python3
"""Benchmark exact recursion vs AW evaluation/inversion for selected cases."""

from __future__ import annotations

import argparse
import json
import os
import platform
import sys
import time
from pathlib import Path
from typing import Callable, Dict, List

# Keep BLAS single-threaded for more stable timings.
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
SRC_ROOT = ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from vkcore.grid2d.bimod_legacy_imports import choose_aw_params, exact_fpt
from vkcore.grid2d.model_core_reflecting import ConfigSpec, LatticeConfig, edge_key, spec_to_internal
from vkcore.grid2d.reflecting_blackboard import _reflecting_pipeline as rbp

from fpt_aw_inversion import fpt_pmf_aw
from heterogeneity_determinant import DefectSystem, defect_pairs_from_config
from propagator_z_analytic import defect_free_propagator_from_config

CaseBuilder = Callable[[], rbp.CaseDef]


def _case_builders() -> Dict[str, CaseBuilder]:
    return {
        "R1": rbp.build_r1,
        "R2": rbp.build_r2,
        "R3": rbp.build_r3,
        "R4": rbp.build_r4,
        "R5": rbp.build_r5,
        "R6": rbp.build_r6,
        "R7": rbp.build_r7,
        "C3": rbp.build_c3,
        "MB1": rbp.build_mb1,
        "MB2": rbp.build_mb2,
        "MB3": rbp.build_mb3,
        "NB1": rbp.build_nb1,
        "NB2": rbp.build_nb2,
        "NB3": rbp.build_nb3,
        "NB4": rbp.build_nb4,
        "NB5": rbp.build_nb5,
    }


def _low_defect_case() -> tuple[LatticeConfig, int]:
    spec = ConfigSpec(
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
    )
    cfg = spec_to_internal(spec)
    return cfg, 5000


def _time_once(func: Callable[[], None]) -> float:
    t0 = time.perf_counter()
    func()
    return time.perf_counter() - t0


def _time_repeat(func: Callable[[], None], repeats: int) -> List[float]:
    times: List[float] = []
    for _ in range(repeats):
        times.append(_time_once(func))
    return times


def _median(values: List[float]) -> float:
    if not values:
        return 0.0
    return float(np.median(np.asarray(values, dtype=np.float64)))


def _exact_time(cfg: LatticeConfig, *, t_max: int, repeats: int) -> tuple[np.ndarray, float, List[float]]:
    last_f = np.array([], dtype=np.float64)
    last_p = 0.0

    def _run() -> None:
        nonlocal last_f, last_p
        last_f, last_p = exact_fpt(cfg, t_max=t_max)

    times = _time_repeat(_run, repeats=repeats)
    return last_f, last_p, times


def _aw_inversion_time(
    f_exact: np.ndarray,
    *,
    t_max: int,
    oversample: int,
    r_pow10: float,
    repeats: int,
) -> List[float]:
    def _run() -> None:
        rbp._aw_from_exact(f_exact, t_max=t_max, oversample=oversample, r_pow10=r_pow10)

    return _time_repeat(_run, repeats=repeats)


def _aw_eval_time(
    cfg: LatticeConfig,
    *,
    t_max: int,
    oversample: int,
    r_pow10: float,
    n_z: int,
    repeats: int,
) -> tuple[float, float, int, int, int]:
    t0 = time.perf_counter()
    base = defect_free_propagator_from_config(cfg)
    defects = defect_pairs_from_config(cfg)
    system = DefectSystem(base=base, defects=defects, start=cfg.start, target=cfg.target)
    t_setup = time.perf_counter() - t0

    params = choose_aw_params(t_max, oversample=oversample, r_pow10=r_pow10)
    m = params.m
    if n_z > m:
        n_z = m
    idx = np.linspace(0, m - 1, n_z, endpoint=False).astype(np.int64)
    z_grid = params.r * np.exp(1j * 2.0 * np.pi * idx / float(m))

    def _eval_once() -> None:
        for z in z_grid:
            system.propagators(z)

    times = _time_repeat(_eval_once, repeats=repeats)
    t_eval = _median(times)
    return t_setup, t_eval, int(n_z), int(m), len(defects)


def _fft_time(m: int, repeats: int) -> float:
    rng = np.random.default_rng(0)
    data = rng.standard_normal(m) + 1j * rng.standard_normal(m)

    def _run() -> None:
        np.fft.fft(data)

    return _median(_time_repeat(_run, repeats=repeats))


def _aw_full_time(
    cfg: LatticeConfig,
    *,
    t_max: int,
    oversample: int,
    r_pow10: float,
    repeats: int,
) -> List[float]:
    def _run() -> None:
        fpt_pmf_aw(cfg, t_max=t_max, oversample=oversample, r_pow10=r_pow10)

    return _time_repeat(_run, repeats=repeats)


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark AW vs exact recursion timings.")
    parser.add_argument("--cases", type=str, default="R1,R6,NB4,NB5,S0", help="Comma-separated case IDs.")
    parser.add_argument("--exact-repeats", type=int, default=1)
    parser.add_argument("--aw-repeats", type=int, default=1)
    parser.add_argument("--aw-oversample", type=int, default=4)
    parser.add_argument("--aw-rpow10", type=float, default=12.0)
    parser.add_argument("--aw-nz", type=int, default=32, help="Number of z samples for AW eval timing.")
    parser.add_argument(
        "--output",
        type=str,
        default=str(ROOT / "reports" / "grid2d_reflecting_bimodality" / "data" / "aw_exact_speed.json"),
    )
    args = parser.parse_args()

    builders = _case_builders()
    case_ids = [c.strip() for c in args.cases.split(",") if c.strip()]

    results = {}
    for case_id in case_ids:
        is_low_defect = case_id == "S0"
        if is_low_defect:
            cfg, t_max = _low_defect_case()
        else:
            if case_id not in builders:
                raise ValueError(f"Unknown case id: {case_id}")
            case = builders[case_id]()
            spec = rbp._case_to_spec(case)
            cfg = spec_to_internal(spec)
            t_max = case.t_max

        f_exact, p_abs, exact_times = _exact_time(cfg, t_max=t_max, repeats=args.exact_repeats)
        aw_inv_times = _aw_inversion_time(
            f_exact,
            t_max=len(f_exact),
            oversample=args.aw_oversample,
            r_pow10=args.aw_rpow10,
            repeats=args.aw_repeats,
        )

        t_setup, t_eval, n_z, m, n_defects = _aw_eval_time(
            cfg,
            t_max=t_max,
            oversample=args.aw_oversample,
            r_pow10=args.aw_rpow10,
            n_z=args.aw_nz,
            repeats=args.aw_repeats,
        )

        t_fft = _fft_time(m, repeats=max(1, args.aw_repeats))
        t_eval_per_z = t_eval / float(n_z)
        t_eval_est = t_eval_per_z * float(m)
        t_aw_est = t_setup + t_eval_est + t_fft

        aw_full = None
        if is_low_defect:
            aw_full = _aw_full_time(
                cfg,
                t_max=len(f_exact),
                oversample=args.aw_oversample,
                r_pow10=args.aw_rpow10,
                repeats=max(1, args.aw_repeats),
            )

        results[case_id] = {
            "t_max": int(t_max),
            "m": int(m),
            "defects": int(n_defects),
            "p_abs": float(p_abs),
            "exact_seconds": {
                "median": _median(exact_times),
                "samples": exact_times,
            },
            "aw_inversion_seconds": {
                "median": _median(aw_inv_times),
                "samples": aw_inv_times,
            },
            "aw_setup_seconds": float(t_setup),
            "aw_eval_seconds": float(t_eval),
            "aw_eval_per_z_seconds": float(t_eval_per_z),
            "aw_eval_nz": int(n_z),
            "aw_fft_seconds": float(t_fft),
            "aw_estimated_total_seconds": float(t_aw_est),
            "aw_full_seconds": None if aw_full is None else {"median": _median(aw_full), "samples": aw_full},
        }

    payload = {
        "meta": {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "python": sys.version.split()[0],
            "numpy": np.__version__,
            "platform": platform.platform(),
            "aw_oversample": int(args.aw_oversample),
            "aw_rpow10": float(args.aw_rpow10),
            "aw_nz": int(args.aw_nz),
            "exact_repeats": int(args.exact_repeats),
            "aw_repeats": int(args.aw_repeats),
            "thread_env": {
                "OMP_NUM_THREADS": os.environ.get("OMP_NUM_THREADS"),
                "OPENBLAS_NUM_THREADS": os.environ.get("OPENBLAS_NUM_THREADS"),
                "MKL_NUM_THREADS": os.environ.get("MKL_NUM_THREADS"),
            },
        },
        "cases": results,
    }

    out_path = Path(args.output)
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
