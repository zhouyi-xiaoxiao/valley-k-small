#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

WINDOWS = ["peak1", "valley", "peak2"]
CLASSES = ["C0J0", "C1pJ0", "C0J1p", "C1pJ1p"]
BIN_COLORS = {"peak1": "#F4A261", "valley": "#2A9D8F", "peak2": "#2B6CB0"}
CLASS_COLORS = {
    "C0J0": "#264653",
    "C1pJ0": "#D62828",
    "C0J1p": "#2A9D8F",
    "C1pJ1p": "#F2C14E",
}


@dataclass
class CasePaths:
    case_dir: Path
    summary_json: Path
    cond_by_t: Optional[Path]
    exact_npz: Optional[Path]


QUIET = False


def _warn(msg: str) -> None:
    if QUIET:
        return
    print(f"[export_fig2_inputs] {msg}", file=sys.stderr)


def _find_case(root: Path, beta: float, K: int, N: Optional[int]) -> Optional[CasePaths]:
    cases_dir = root / "outputs" / "mc_beta_sweep_N100" / "cases"
    if not cases_dir.exists():
        return None

    candidates = sorted(cases_dir.glob("**/*.summary.json"))
    best: Optional[CasePaths] = None
    for summary_path in candidates:
        try:
            data = json.loads(summary_path.read_text())
        except json.JSONDecodeError:
            continue
        params = data.get("params", {})
        if int(params.get("K", -1)) != int(K):
            continue
        if N is not None and int(params.get("N", -1)) != int(N):
            continue
        if not math.isclose(float(params.get("beta", -999)), beta, rel_tol=1e-6, abs_tol=1e-6):
            continue
        case_dir = summary_path.parent
        cond_by_t = next(iter(case_dir.glob("*.cond_by_t.csv")), None)
        exact_npz = next(iter(case_dir.glob("*.exact.npz")), None)
        best = CasePaths(case_dir=case_dir, summary_json=summary_path, cond_by_t=cond_by_t, exact_npz=exact_npz)
        break
    return best


def _load_windows(summary_data: dict) -> Tuple[Dict[str, int], int]:
    peaks_valley = summary_data.get("peaks_valley")
    if not peaks_valley:
        raise ValueError("summary.json missing peaks_valley")
    centers = {
        "peak1": int(peaks_valley.get("t1", -1)),
        "valley": int(peaks_valley.get("tv", -1)),
        "peak2": int(peaks_valley.get("t2", -1)),
    }
    delta = int(peaks_valley.get("delta", 0))
    return centers, delta


def _compute_bin_intervals(centers: Dict[str, int], delta: int, t_max: int) -> Dict[str, List[int]]:
    intervals: Dict[str, List[int]] = {}
    for name in WINDOWS:
        c = int(centers.get(name, -1))
        if c < 0:
            raise ValueError(f"missing center for window {name}")
        tL = max(1, c - delta)
        tR = min(int(t_max), c + delta)
        if tL >= tR:
            raise ValueError(f"invalid interval for {name}: {tL}, {tR}")
        intervals[name] = [int(tL), int(tR)]
    return intervals


def _summaries_to_props(summary_data: dict) -> Tuple[
    Dict[str, Dict[str, float]], Dict[str, Dict[str, int]], Dict[str, int]
]:
    props: Dict[str, Dict[str, float]] = {w: {c: 0.0 for c in CLASSES} for w in WINDOWS}
    counts: Dict[str, Dict[str, int]] = {w: {c: 0 for c in CLASSES} for w in WINDOWS}
    totals: Dict[str, int] = {w: 0 for w in WINDOWS}
    summaries = summary_data.get("summaries", [])
    for row in summaries:
        window = row.get("window")
        if window not in WINDOWS:
            continue
        n = int(row.get("n", 0))
        totals[window] = n
        for cls in CLASSES:
            key = f"class_{cls}"
            val = row.get(key)
            if val is None:
                continue
            props[window][cls] = float(val)
            counts[window][cls] = int(round(float(val) * n))
    return props, counts, totals


def _compute_props_from_cond_by_t(cond_path: Path, bin_intervals: Dict[str, List[int]]) -> Tuple[
    Dict[str, Dict[str, float]], Dict[str, Dict[str, int]], Dict[str, int]
]:
    df = pd.read_csv(cond_path)
    if "t" not in df.columns or "n" not in df.columns:
        raise ValueError("cond_by_t.csv missing required columns: t, n")
    for cls in CLASSES:
        col = f"class_{cls}"
        if col not in df.columns:
            raise ValueError(f"cond_by_t.csv missing column: {col}")
    df = df.copy()
    df["n"] = df["n"].fillna(0)
    for cls in CLASSES:
        df[f"class_{cls}"] = df[f"class_{cls}"].fillna(0)

    proportions: Dict[str, Dict[str, float]] = {w: {} for w in WINDOWS}
    counts: Dict[str, Dict[str, int]] = {w: {} for w in WINDOWS}
    totals: Dict[str, int] = {}
    for window, (tL, tR) in bin_intervals.items():
        wdf = df[(df["t"] >= tL) & (df["t"] <= tR)]
        total_n = int(wdf["n"].sum())
        totals[window] = total_n
        for cls in CLASSES:
            vals = (wdf["n"] * wdf[f"class_{cls}"]).sum()
            counts[window][cls] = int(round(float(vals)))
        if total_n <= 0:
            proportions[window] = {cls: 0.0 for cls in CLASSES}
        else:
            proportions[window] = {cls: counts[window][cls] / float(total_n) for cls in CLASSES}
    return proportions, counts, totals


def _write_ft_csv(outpath: Path, f_k2: np.ndarray, f_k4: Optional[np.ndarray]) -> None:
    if f_k4 is None:
        n = f_k2.size
        t = np.arange(1, n + 1, dtype=int)
        df = pd.DataFrame({"t": t, "f_K2": f_k2})
    else:
        n = min(f_k2.size, f_k4.size)
        t = np.arange(1, n + 1, dtype=int)
        df = pd.DataFrame({"t": t, "f_K2": f_k2[:n], "f_K4": f_k4[:n]})
    outpath.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(outpath, index=False)


def _write_json(
    outpath: Path,
    bin_intervals: Dict[str, List[int]],
    bin_intervals_by_k: Optional[Dict[str, Dict[str, List[int]]]],
    proportions: Dict[str, Dict[str, Dict[str, float]]],
    counts: Dict[str, Dict[str, Dict[str, int]]],
    totals: Dict[str, Dict[str, int]],
    meta: Dict[str, str],
) -> None:
    payload = {
        "windows": WINDOWS,
        "bin_colors": BIN_COLORS,
        "classes": CLASSES,
        "class_colors": CLASS_COLORS,
        "bin_intervals": bin_intervals,
        "proportions": proportions,
        "counts": counts,
        "n_windows": totals,
        "meta": meta,
    }
    if bin_intervals_by_k:
        payload["bin_intervals_by_k"] = bin_intervals_by_k
    outpath.parent.mkdir(parents=True, exist_ok=True)
    outpath.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def _generate_example(out_json: Path, out_ft: Path) -> None:
    t = np.arange(1, 401)
    f_k2 = np.exp(-0.5 * ((t - 80) / 18) ** 2) * 0.005 + np.exp(-0.5 * ((t - 210) / 28) ** 2) * 0.006
    f_k4 = np.exp(-0.5 * ((t - 60) / 14) ** 2) * 0.004 + np.exp(-0.5 * ((t - 190) / 22) ** 2) * 0.007
    df = pd.DataFrame({"t": t, "f_K2": f_k2, "f_K4": f_k4})
    out_ft.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_ft, index=False)

    bin_intervals = {"peak1": [60, 90], "valley": [120, 150], "peak2": [180, 220]}
    bin_intervals_by_k = {"K=2": dict(bin_intervals), "K=4": dict(bin_intervals)}
    proportions = {
        "K=2": {
            "peak1": {"C0J0": 0.05, "C1pJ0": 0.92, "C0J1p": 0.01, "C1pJ1p": 0.02},
            "valley": {"C0J0": 0.10, "C1pJ0": 0.85, "C0J1p": 0.02, "C1pJ1p": 0.03},
            "peak2": {"C0J0": 0.62, "C1pJ0": 0.30, "C0J1p": 0.04, "C1pJ1p": 0.04},
        },
        "K=4": {
            "peak1": {"C0J0": 0.02, "C1pJ0": 0.65, "C0J1p": 0.01, "C1pJ1p": 0.32},
            "valley": {"C0J0": 0.08, "C1pJ0": 0.58, "C0J1p": 0.03, "C1pJ1p": 0.31},
            "peak2": {"C0J0": 0.55, "C1pJ0": 0.20, "C0J1p": 0.12, "C1pJ1p": 0.13},
        },
    }
    counts = {
        "K=2": {
            "peak1": {"C0J0": 50, "C1pJ0": 920, "C0J1p": 10, "C1pJ1p": 20},
            "valley": {"C0J0": 80, "C1pJ0": 680, "C0J1p": 16, "C1pJ1p": 24},
            "peak2": {"C0J0": 620, "C1pJ0": 300, "C0J1p": 40, "C1pJ1p": 40},
        },
        "K=4": {
            "peak1": {"C0J0": 20, "C1pJ0": 650, "C0J1p": 10, "C1pJ1p": 320},
            "valley": {"C0J0": 80, "C1pJ0": 580, "C0J1p": 30, "C1pJ1p": 310},
            "peak2": {"C0J0": 550, "C1pJ0": 200, "C0J1p": 120, "C1pJ1p": 130},
        },
    }
    totals = {
        "K=2": {"peak1": 1000, "valley": 800, "peak2": 1000},
        "K=4": {"peak1": 1000, "valley": 1000, "peak2": 1000},
    }
    meta = {"mode": "example"}
    _write_json(out_json, bin_intervals, bin_intervals_by_k, proportions, counts, totals, meta)


def main() -> None:
    parser = argparse.ArgumentParser(description="Export fig2 inputs from existing outputs.")
    parser.add_argument("--beta", type=float, default=0.01)
    parser.add_argument("--N", type=int, default=100)
    parser.add_argument("--ref-k", type=int, default=4)
    parser.add_argument("--out-json", type=Path, default=None)
    parser.add_argument("--out-ft", type=Path, default=None)
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()
    global QUIET
    QUIET = bool(args.quiet)

    root = Path(__file__).resolve().parents[1]
    out_json = args.out_json or (root / "data" / f"fig2_bins_bars_beta{args.beta:.2f}.json")
    out_ft = args.out_ft or (root / "data" / f"ft_beta{args.beta:.2f}.csv")

    case_k2 = _find_case(root, args.beta, K=2, N=args.N)
    case_k4 = _find_case(root, args.beta, K=4, N=args.N)

    if case_k2 is None and case_k4 is None:
        _warn("No matching cases found; generating example inputs.")
        _generate_example(out_json, out_ft)
        return

    if case_k2 is None or case_k4 is None:
        _warn("Missing one of K=2/K=4 cases; generating example inputs.")
        _generate_example(out_json, out_ft)
        return

    summary_k2 = json.loads(case_k2.summary_json.read_text())
    summary_k4 = json.loads(case_k4.summary_json.read_text())

    ref_case = case_k4 if args.ref_k == 4 else case_k2
    ref_summary = summary_k4 if args.ref_k == 4 else summary_k2

    if ref_case.exact_npz is None:
        _warn("Missing exact.npz; generating example inputs.")
        _generate_example(out_json, out_ft)
        return

    f_k2 = np.load(case_k2.exact_npz)["f"] if case_k2.exact_npz is not None else None
    f_k4 = np.load(case_k4.exact_npz)["f"] if case_k4.exact_npz is not None else None
    if f_k2 is None or f_k4 is None:
        _warn("Missing f(t) arrays; generating example inputs.")
        _generate_example(out_json, out_ft)
        return
    t_max_k2 = int(f_k2.size)
    t_max_k4 = int(f_k4.size)
    centers_k2, delta_k2 = _load_windows(summary_k2)
    centers_k4, delta_k4 = _load_windows(summary_k4)
    bin_intervals_by_k = {
        "K=2": _compute_bin_intervals(centers_k2, delta_k2, t_max_k2),
        "K=4": _compute_bin_intervals(centers_k4, delta_k4, t_max_k4),
    }

    exact_ref = np.load(ref_case.exact_npz)
    t_max_ref = int(exact_ref["f"].size)
    centers_ref, delta_ref = _load_windows(ref_summary)
    bin_intervals = _compute_bin_intervals(centers_ref, delta_ref, t_max_ref)
    _write_ft_csv(out_ft, f_k2=f_k2, f_k4=f_k4)

    proportions: Dict[str, Dict[str, Dict[str, float]]] = {}
    counts: Dict[str, Dict[str, Dict[str, int]]] = {}
    totals: Dict[str, Dict[str, int]] = {}
    prop_source: Dict[str, Dict[str, str]] = {}

    for label, case, summary in [("K=2", case_k2, summary_k2), ("K=4", case_k4, summary_k4)]:
        summary_props, summary_counts, summary_totals = _summaries_to_props(summary)
        prop_source[label] = {w: "summary" for w in WINDOWS}
        intervals_for_label = bin_intervals_by_k.get(label, bin_intervals)
        if case.cond_by_t is not None:
            props, cnts, tots = _compute_props_from_cond_by_t(case.cond_by_t, intervals_for_label)
            for window in WINDOWS:
                if tots.get(window, 0) > 0 and sum(cnts[window].values()) == 0:
                    _warn(f"{label}/{window} cond_by_t has NaN class probs; fallback to summary.")
                    props[window] = summary_props[window]
                    cnts[window] = summary_counts[window]
                    tots[window] = summary_totals[window]
                    prop_source[label][window] = "summary"
                else:
                    prop_source[label][window] = "cond_by_t"
            proportions[label] = props
            counts[label] = cnts
            totals[label] = tots
        else:
            _warn(f"Missing cond_by_t for {label}; falling back to summary proportions.")
            proportions[label] = summary_props
            counts[label] = summary_counts
            totals[label] = summary_totals
            prop_source[label] = {w: "summary" for w in WINDOWS}

    meta = {
        "beta": f"{args.beta}",
        "N": f"{args.N}",
        "reference_K": f"{args.ref_k}",
        "case_k2": str(case_k2.case_dir),
        "case_k4": str(case_k4.case_dir),
        "cond_by_t_k2": str(case_k2.cond_by_t) if case_k2.cond_by_t else "",
        "cond_by_t_k4": str(case_k4.cond_by_t) if case_k4.cond_by_t else "",
    }

    meta["proportion_source"] = prop_source
    _write_json(out_json, bin_intervals, bin_intervals_by_k, proportions, counts, totals, meta)


if __name__ == "__main__":
    main()
