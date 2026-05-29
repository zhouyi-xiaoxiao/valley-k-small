from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from encounter_search.shape import jensen_shannon_divergence
from encounter_search.shape import score_distribution
from encounter_search.shape import smooth_signal
from encounter_search.shape import window_bounds
from encounter_search.solver import EncounterChain
from encounter_search.solver import absorbing_pgf_total
from encounter_search.solver import build_chain
from encounter_search.solver import determinant_pgf_total
from encounter_search.solver import exact_distribution
from encounter_search.solver import fundamental_moments
from encounter_search.solver import min_entry
from encounter_search.solver import row_stochastic_error


Q_GRID = (0.02, 0.05, 0.1, 0.2, 0.4, 0.7, 0.9)
SMOOTH_WINDOWS = (7, 11, 21)
REPORT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RESULTS_DIR = REPORT_ROOT / "artifacts" / "encounter_search" / "results"


@dataclass(frozen=True)
class RatioScan:
    scan_id: str
    N: int
    start: tuple[int, int]
    ratios: np.ndarray
    mobility: Callable[[float], tuple[float, float]]
    description: str


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_RESULTS_DIR)
    parser.add_argument("--pilot", action="store_true", help="run validation plus pilot scans")
    parser.add_argument("--survival-tol", type=float, default=1e-12)
    parser.add_argument("--max-t", type=int, default=200_000)
    parser.add_argument(
        "--shape-max-t",
        type=int,
        default=6_000,
        help="maximum propagation horizon used in the broad shape scan",
    )
    parser.add_argument("--top-n", type=int, default=30)
    args = parser.parse_args(argv)

    out = args.out
    out.mkdir(parents=True, exist_ok=True)

    print(f"writing outputs under {out}")
    validation_mean = run_validation_mean(out, survival_tol=args.survival_tol, max_t=args.max_t)
    validation_gf = run_validation_gf(out)
    mean_ratio = pd.DataFrame()
    top_cases = pd.DataFrame()
    if args.pilot:
        mean_ratio = run_mean_ratio_pilot(out)
        top_cases = run_shape_pilot(
            out,
            survival_tol=args.survival_tol,
            shape_max_t=args.shape_max_t,
            dist_max_t=args.max_t,
            top_n=args.top_n,
        )
    write_report(out, validation_mean, validation_gf, mean_ratio, top_cases)


def run_validation_mean(out: Path, *, survival_tol: float, max_t: int) -> pd.DataFrame:
    cases = [
        {"case_id": "L5_edge_q04_q09", "N": 5, "start": (1, 5), "q1": 0.4, "q2": 0.9},
        {"case_id": "L6_inner_q07_q03", "N": 6, "start": (5, 2), "q1": 0.7, "q2": 0.3},
        {"case_id": "L7_asym_q02_q08", "N": 7, "start": (2, 6), "q1": 0.2, "q2": 0.8},
    ]
    rows: list[dict[str, object]] = []
    for case in cases:
        chain = build_chain(int(case["N"]), float(case["q1"]), float(case["q2"]))
        start = case["start"]
        assert isinstance(start, tuple)
        dist = exact_distribution(chain, start, survival_tol=survival_tol, max_t=max_t)
        moments = fundamental_moments(chain, start)
        rows.append(
            {
                "case_id": case["case_id"],
                "N": chain.N,
                "start_a": start[0],
                "start_b": start[1],
                "q1": chain.q1,
                "q2": chain.q2,
                "p1_row_error": row_stochastic_error(chain.P1),
                "p2_row_error": row_stochastic_error(chain.P2),
                "p1_min_entry": min_entry(chain.P1),
                "p2_min_entry": min_entry(chain.P2),
                "sum_t_f": dist.mass,
                "tail_mass": dist.tail_mass,
                "sum_t_t_f": dist.mean,
                "mean_formula": moments.mean,
                "mean_abs_error": abs(dist.mean - moments.mean),
                "sum_k_p_k": moments.p_sum,
                "sum_k_p_k_abs_error": abs(moments.p_sum - 1.0),
                "sum_k_p_k_tau_k": moments.p_tau_sum,
                "p_tau_mean_abs_error": abs(moments.p_tau_sum - moments.mean),
                "mass_balance_error": dist.max_mass_balance_error,
                "decomposition_error": _decomposition_error(dist.f, dist.f_by_k),
                "reached_tol": dist.reached_tol,
                "steps": int(dist.times[-1]) if dist.times.size else 0,
            }
        )
    df = pd.DataFrame(rows)
    df.to_csv(out / "validation_mean.csv", index=False)
    print(f"wrote {out / 'validation_mean.csv'}")
    return df


def run_validation_gf(out: Path) -> pd.DataFrame:
    N = 5
    start = (1, 5)
    q1 = 0.4
    q2 = 0.9
    z_values = (0.2, 0.5, 0.8, 0.95)
    chain = build_chain(N, q1, q2)
    rows: list[dict[str, object]] = []
    for z in z_values:
        absorbing = absorbing_pgf_total(chain, start, z)
        determinant = determinant_pgf_total(N, q1, q2, start, z)
        rows.append(
            {
                "N": N,
                "start_a": start[0],
                "start_b": start[1],
                "q1": q1,
                "q2": q2,
                "z": z,
                "absorbing_re": float(np.real(absorbing)),
                "absorbing_im": float(np.imag(absorbing)),
                "determinant_re": float(np.real(determinant)),
                "determinant_im": float(np.imag(determinant)),
                "abs_error": float(abs(absorbing - determinant)),
                "rel_error": float(abs(absorbing - determinant) / max(1.0, abs(determinant))),
            }
        )
    df = pd.DataFrame(rows)
    df.to_csv(out / "validation_gf.csv", index=False)
    print(f"wrote {out / 'validation_gf.csv'}")
    return df


def run_mean_ratio_pilot(out: Path) -> pd.DataFrame:
    scans = [
        RatioScan(
            scan_id="A_fixed_q2_start_5_1",
            N=15,
            start=(5, 1),
            ratios=np.logspace(-2.0, np.log10(2.0), 80),
            mobility=lambda r: (0.5 * float(r), 0.5),
            description="start=(5,1), q2=0.5, r=q1/q2",
        ),
        RatioScan(
            scan_id="B_fixed_sum_start_7_9",
            N=15,
            start=(7, 9),
            ratios=np.logspace(-2.0, 2.0, 80),
            mobility=lambda r: (float(r) / (1.0 + float(r)), 1.0 / (1.0 + float(r))),
            description="start=(7,9), q1+q2=1, r=q1/q2",
        ),
        RatioScan(
            scan_id="C_fixed_sum_start_1_15",
            N=15,
            start=(1, 15),
            ratios=np.logspace(-2.0, 2.0, 80),
            mobility=lambda r: (float(r) / (1.0 + float(r)), 1.0 / (1.0 + float(r))),
            description="start=(1,15), q1+q2=1, r=q1/q2",
        ),
    ]

    rows: list[dict[str, object]] = []
    grouped_indices: dict[str, list[int]] = {}
    for scan in scans:
        grouped_indices[scan.scan_id] = []
        for r in scan.ratios:
            q1, q2 = scan.mobility(float(r))
            chain = build_chain(scan.N, q1, q2)
            moments = fundamental_moments(chain, scan.start)
            row: dict[str, object] = {
                "scan_id": scan.scan_id,
                "description": scan.description,
                "N": scan.N,
                "start_a": scan.start[0],
                "start_b": scan.start[1],
                "r": float(r),
                "q1": q1,
                "q2": q2,
                "mean": moments.mean,
                "extremum_kind": "",
                "near_extremum": False,
                "sum_k_p_tau": moments.p_tau_sum,
                "p_tau_mean_abs_error": abs(moments.p_tau_sum - moments.mean),
                "top_p_tau": _top_entries(moments.p_tau_by_k, n=5),
            }
            for k in range(scan.N):
                row[f"p_k{k + 1:02d}"] = moments.p_by_k[k]
                row[f"tau_k{k + 1:02d}"] = moments.tau_by_k[k]
                row[f"p_tau_k{k + 1:02d}"] = moments.p_tau_by_k[k]
            grouped_indices[scan.scan_id].append(len(rows))
            rows.append(row)

    for indices in grouped_indices.values():
        means = np.array([float(rows[i]["mean"]) for i in indices], dtype=float)
        local_extrema = _local_extrema(means)
        global_min = int(np.argmin(means))
        global_max = int(np.argmax(means))
        extrema = {global_min: "global_min", global_max: "global_max"}
        for idx, kind in local_extrema.items():
            extrema[idx] = f"{extrema[idx]};{kind}" if idx in extrema else kind
        near = set()
        for idx in extrema:
            near.update(j for j in range(max(0, idx - 2), min(len(indices), idx + 3)))
        for rel_idx, kind in extrema.items():
            rows[indices[rel_idx]]["extremum_kind"] = kind
        for rel_idx in near:
            rows[indices[rel_idx]]["near_extremum"] = True

    df = pd.DataFrame(rows)
    df.to_csv(out / "mean_ratio_pilot.csv", index=False)
    print(f"wrote {out / 'mean_ratio_pilot.csv'}")
    return df


def run_shape_pilot(
    out: Path,
    *,
    survival_tol: float,
    shape_max_t: int,
    dist_max_t: int,
    top_n: int,
) -> pd.DataFrame:
    candidates: list[dict[str, object]] = []
    for N in (15, 21):
        for q1 in Q_GRID:
            for q2 in Q_GRID:
                print(f"shape scan N={N} q1={q1:g} q2={q2:g}")
                chain = build_chain(N, q1, q2)
                curves, tails, reached = all_start_total_curves(
                    chain,
                    survival_tol=survival_tol,
                    max_t=shape_max_t,
                )
                for start_idx, start in enumerate(chain.transient_states):
                    f = curves[:, start_idx]
                    score = score_distribution(f, smooth_windows=SMOOTH_WINDOWS)
                    tail = float(tails[start_idx])
                    adjusted = score.score * _tail_score_factor(tail)
                    candidates.append(
                        {
                            "N": N,
                            "start_a": start[0],
                            "start_b": start[1],
                            "q1": q1,
                            "q2": q2,
                            "score": adjusted,
                            "raw_score": score.score,
                            "label": score.label,
                            "raw_label": score.raw.label,
                            "persistence": score.persistence,
                            "parity_penalty": score.parity_penalty,
                            "smoothing_penalty": score.smoothing_penalty,
                            "t_main": score.raw.t_main_index + 1,
                            "t_late": "" if score.raw.t_late_index is None else score.raw.t_late_index + 1,
                            "r_peak": score.raw.r_peak,
                            "r_valley": score.raw.r_valley,
                            "peak_separation": score.raw.separation,
                            "tail_mass_scan": tail,
                            "reached_tol_scan": bool(reached),
                            "scan_steps": curves.shape[0],
                        }
                    )

    top = sorted(candidates, key=lambda row: float(row["score"]), reverse=True)[: int(top_n)]
    rows: list[dict[str, object]] = []
    figures_dir = out / "figures" / "top10"
    figures_dir.mkdir(parents=True, exist_ok=True)

    for rank, row in enumerate(top, start=1):
        chain = build_chain(int(row["N"]), float(row["q1"]), float(row["q2"]))
        start = (int(row["start_a"]), int(row["start_b"]))
        dist = exact_distribution(chain, start, survival_tol=survival_tol, max_t=dist_max_t)
        analysis = analyse_distribution_channels(dist)
        score = score_distribution(dist.f, smooth_windows=SMOOTH_WINDOWS)
        result_row = {
            "rank": rank,
            **row,
            "score_recomputed": score.score,
            "label_recomputed": score.label,
            "mass": dist.mass,
            "tail_mass": dist.tail_mass,
            "reached_tol": dist.reached_tol,
            "mean_truncated": dist.mean,
            "mass_balance_error": dist.max_mass_balance_error,
            "decomposition_error": _decomposition_error(dist.f, dist.f_by_k),
            **analysis,
        }
        rows.append({key: value for key, value in result_row.items() if not key.startswith("_")})
        if rank <= 10:
            case_prefix = f"case{rank:02d}_N{dist.N}_a{start[0]}_b{start[1]}_q1{_q_label(dist.q1)}_q2{_q_label(dist.q2)}"
            plot_top_case(dist, figures_dir, case_prefix, score, analysis)

    df = pd.DataFrame(rows)
    df.to_csv(out / "top_shape_cases.csv", index=False)
    print(f"wrote {out / 'top_shape_cases.csv'}")
    return df


def all_start_total_curves(
    chain: EncounterChain,
    *,
    survival_tol: float,
    max_t: int,
) -> tuple[np.ndarray, np.ndarray, bool]:
    """Compute f(t) for every ordered start using one sparse vector recurrence."""

    h = np.asarray(chain.R.sum(axis=1)).reshape(-1)
    values = h.copy()
    survival = np.ones(chain.Q.shape[0], dtype=float)
    curves = np.empty((int(max_t), chain.Q.shape[0]), dtype=float)
    reached = False
    steps = 0
    for idx in range(int(max_t)):
        curves[idx, :] = values
        survival = np.asarray(chain.Q @ survival).reshape(-1)
        steps = idx + 1
        if float(np.max(survival)) <= float(survival_tol):
            reached = True
            break
        values = np.asarray(chain.Q @ values).reshape(-1)
    return curves[:steps, :], survival, reached


def analyse_distribution_channels(dist) -> dict[str, object]:
    score = score_distribution(dist.f, smooth_windows=SMOOTH_WINDOWS)
    radius = max(3, min(21, int(max(score.raw.separation, 1) // 6 or 3)))
    early_lo, early_hi = window_bounds(score.raw.t_main_index, dist.f.size, radius=radius)
    if score.raw.t_late_index is None:
        late_center = min(dist.f.size - 1, score.raw.t_main_index + max(8, radius * 2))
    else:
        late_center = score.raw.t_late_index
    late_lo, late_hi = window_bounds(late_center, dist.f.size, radius=radius)

    early_by_k = np.sum(dist.f_by_k[early_lo : early_hi + 1, :], axis=0)
    late_by_k = np.sum(dist.f_by_k[late_lo : late_hi + 1, :], axis=0)
    early_total = float(np.sum(dist.f[early_lo : early_hi + 1]))
    late_total = float(np.sum(dist.f[late_lo : late_hi + 1]))
    C_early = _normalise_or_zero(early_by_k)
    C_late = _normalise_or_zero(late_by_k)
    delta = C_late - C_early
    jsd = jensen_shannon_divergence(C_early, C_late)
    mechanism = label_mechanism(dist.N, C_early, C_late, score)
    max_delta_idx = int(np.argmax(np.abs(delta))) if delta.size else 0

    return {
        "early_window": f"{int(dist.times[early_lo])}-{int(dist.times[early_hi])}",
        "late_window": f"{int(dist.times[late_lo])}-{int(dist.times[late_hi])}",
        "early_window_mass": early_total,
        "late_window_mass": late_total,
        "top_k_early": _top_entries(C_early, n=5),
        "top_k_late": _top_entries(C_late, n=5),
        "top_delta_k": _top_entries(delta, n=5, by_abs=True),
        "max_delta_k": max_delta_idx + 1,
        "max_delta": float(delta[max_delta_idx]) if delta.size else 0.0,
        "jsd_early_late_bits": jsd,
        "mechanism_label": mechanism,
        "_C_early": C_early,
        "_C_late": C_late,
        "_early_bounds": (early_lo, early_hi),
        "_late_bounds": (late_lo, late_hi),
    }


def label_mechanism(N: int, C_early: np.ndarray, C_late: np.ndarray, score) -> str:
    if score.label == "artifact" or score.parity_penalty > 0.45:
        return "artifact"
    boundary = [0, int(N) - 1]
    boundary_delta = float(np.sum(C_late[boundary]) - np.sum(C_early[boundary]))
    jsd = jensen_shannon_divergence(C_early, C_late)
    top_early = int(np.argmax(C_early)) if C_early.size else -1
    top_late = int(np.argmax(C_late)) if C_late.size else -1
    if boundary_delta > 0.15 and top_late in boundary:
        return "boundary_reflection_channel"
    if jsd > 0.08 and top_early != top_late:
        return "target_mixture"
    if top_early == top_late and jsd <= 0.06:
        return "same_target_multi_path"
    if top_late not in boundary:
        return "bulk_mixing_channel"
    return "target_mixture"


def plot_top_case(dist, figures_dir: Path, prefix: str, score, analysis: dict[str, object]) -> None:
    times = dist.times
    f = dist.f

    fig, ax = plt.subplots(figsize=(7.2, 4.0), constrained_layout=True)
    ax.plot(times, f, lw=1.5)
    ax.axvline(times[score.raw.t_main_index], color="C2", ls="--", lw=1.0, label="main")
    if score.raw.t_late_index is not None:
        ax.axvline(times[score.raw.t_late_index], color="C3", ls="--", lw=1.0, label="late")
    ax.set_xlabel("time t")
    ax.set_ylabel("f_E(t)")
    ax.set_title(_case_title(dist, score.label))
    ax.grid(alpha=0.25)
    ax.legend(fontsize=8)
    fig.savefig(figures_dir / f"{prefix}_f_total.pdf")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7.2, 4.0), constrained_layout=True)
    ax.plot(times, f, color="0.65", lw=1.0, label="raw")
    for window in SMOOTH_WINDOWS:
        smoothed = smooth_signal(f, window)
        if smoothed is not None:
            ax.plot(times, smoothed, lw=1.2, label=f"savgol {window}")
    ax.set_xlabel("time t")
    ax.set_ylabel("f_E(t)")
    ax.set_title(_case_title(dist, f"smoothed {score.label}"))
    ax.grid(alpha=0.25)
    ax.legend(fontsize=8)
    fig.savefig(figures_dir / f"{prefix}_smoothed.pdf")
    plt.close(fig)

    C_early = analysis["_C_early"]
    C_late = analysis["_C_late"]
    top_channels = sorted(
        set(np.argsort(C_early)[-3:].tolist() + np.argsort(C_late)[-3:].tolist())
    )
    fig, ax = plt.subplots(figsize=(7.2, 4.0), constrained_layout=True)
    for k in top_channels:
        ax.plot(times, dist.f_by_k[:, k], lw=1.15, label=f"k={k + 1}")
    ax.set_xlabel("time t")
    ax.set_ylabel("f_k(t)")
    ax.set_title(_case_title(dist, "top channels"))
    ax.grid(alpha=0.25)
    ax.legend(fontsize=8)
    fig.savefig(figures_dir / f"{prefix}_top_fk.pdf")
    plt.close(fig)

    crop_hi = _figure_time_crop(f, score)
    fig, ax = plt.subplots(figsize=(7.4, 4.1), constrained_layout=True)
    mesh = ax.imshow(
        dist.f_by_k[:crop_hi, :].T,
        origin="lower",
        aspect="auto",
        interpolation="nearest",
        extent=[float(times[0]), float(times[crop_hi - 1]), 0.5, dist.N + 0.5],
        cmap="magma",
    )
    ax.set_xlabel("time t")
    ax.set_ylabel("encounter site k")
    ax.set_title(_case_title(dist, "k-time heatmap"))
    fig.colorbar(mesh, ax=ax, label="f_k(t)")
    fig.savefig(figures_dir / f"{prefix}_heatmap.pdf")
    plt.close(fig)

    x = np.arange(1, dist.N + 1)
    fig, ax = plt.subplots(figsize=(7.2, 4.0), constrained_layout=True)
    width = 0.42
    ax.bar(x - width / 2, C_early, width=width, label="early")
    ax.bar(x + width / 2, C_late, width=width, label="late")
    ax.set_xlabel("encounter site k")
    ax.set_ylabel("C_k(W)")
    ax.set_title(_case_title(dist, "early vs late channels"))
    ax.legend(fontsize=8)
    fig.savefig(figures_dir / f"{prefix}_channel_bars.pdf")
    plt.close(fig)


def write_report(
    out: Path,
    validation_mean: pd.DataFrame,
    validation_gf: pd.DataFrame,
    mean_ratio: pd.DataFrame,
    top_cases: pd.DataFrame,
) -> None:
    lines = [
        "# 1D Reflecting Lazy Encounter Exact Pilot",
        "",
        "Model: two synchronous independent lazy walkers on sites `1..N`, with",
        "attempted-outside-stays reflecting boundaries and co-location encounter",
        "set `D={(k,k)}`. Computation uses sparse absorbing-chain blocks",
        "`Q=P_joint[O,O]` and `R=P_joint[O,D]`; no Monte Carlo is used.",
        "",
        "## Validation",
        "",
        f"- mean/formula cases: {len(validation_mean)}",
        f"- max `|sum_t t f(t)-mean|`: {_max_or_nan(validation_mean, 'mean_abs_error'):.3e}",
        f"- max `|sum_k p_k tau_k-mean|`: {_max_or_nan(validation_mean, 'p_tau_mean_abs_error'):.3e}",
        f"- max mass-balance error: {_max_or_nan(validation_mean, 'mass_balance_error'):.3e}",
        f"- GF determinant rows: {len(validation_gf)}",
        f"- max GF absolute error: {_max_or_nan(validation_gf, 'abs_error'):.3e}",
        "",
    ]
    if not mean_ratio.empty:
        lines.extend(["## Mean-Ratio Pilot", ""])
        for scan_id, scan_df in mean_ratio.groupby("scan_id", sort=False):
            extrema = scan_df[scan_df["extremum_kind"].astype(str) != ""]
            lines.append(f"- `{scan_id}`: {len(scan_df)} ratios; extrema rows: {len(extrema)}")
            if not extrema.empty:
                for _, row in extrema.iterrows():
                    lines.append(
                        f"  - {row['extremum_kind']}: r={float(row['r']):.5g}, "
                        f"mean={float(row['mean']):.6g}, top p_k tau_k={row['top_p_tau']}"
                    )
        lines.append("")
    if not top_cases.empty:
        lines.extend(
            [
                "## Shape Pilot",
                "",
                f"- top cases retained: {len(top_cases)}",
                "- figures for the first 10 cases are under `artifacts/encounter_search/results/figures/top10/`.",
                "",
                "| rank | label | N | start | q1 | q2 | score | t_main | t_late | JSD | mechanism |",
                "|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---|",
            ]
        )
        for _, row in top_cases.head(10).iterrows():
            t_late = row["t_late"] if str(row["t_late"]) != "" else ""
            lines.append(
                f"| {int(row['rank'])} | {row['label_recomputed']} | {int(row['N'])} | "
                f"({int(row['start_a'])},{int(row['start_b'])}) | "
                f"{float(row['q1']):.3g} | {float(row['q2']):.3g} | "
                f"{float(row['score_recomputed']):.3g} | {int(row['t_main'])} | {t_late} | "
                f"{float(row['jsd_early_late_bits']):.3g} | {row['mechanism_label']} |"
            )
        lines.extend(
            [
                "",
                "The shape labels are pilot-screening labels. `double_peak` is retained",
                "only when the raw feature persists through all Savitzky-Golay windows",
                "and is not dominated by parity contrast; otherwise weaker candidates",
                "are reported as `local_bump`, `shoulder`, or `artifact`.",
                "",
            ]
        )
    lines.extend(
        [
            "## Outputs",
            "",
            "- `validation_mean.csv`",
            "- `validation_gf.csv`",
            "- `mean_ratio_pilot.csv`",
            "- `top_shape_cases.csv`",
            "- `report.md`",
            "- `artifacts/encounter_search/results/figures/top10/*.pdf`",
            "",
        ]
    )
    (out / "report.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {out / 'report.md'}")


def _local_extrema(values: np.ndarray) -> dict[int, str]:
    extrema: dict[int, str] = {}
    for idx in range(1, values.size - 1):
        if values[idx] <= values[idx - 1] and values[idx] <= values[idx + 1]:
            if values[idx] < values[idx - 1] or values[idx] < values[idx + 1]:
                extrema[idx] = "local_min"
        if values[idx] >= values[idx - 1] and values[idx] >= values[idx + 1]:
            if values[idx] > values[idx - 1] or values[idx] > values[idx + 1]:
                extrema[idx] = "local_max"
    return extrema


def _top_entries(values: np.ndarray, *, n: int, by_abs: bool = False) -> str:
    arr = np.asarray(values, dtype=float).reshape(-1)
    if arr.size == 0:
        return ""
    key = np.abs(arr) if by_abs else arr
    order = np.argsort(key)[::-1]
    parts = []
    for idx in order[: int(n)]:
        if not by_abs and arr[idx] <= 0.0:
            continue
        parts.append(f"k={idx + 1}:{arr[idx]:.6g}")
    return ";".join(parts)


def _tail_score_factor(tail: float) -> float:
    if tail <= 1e-8:
        return 1.0
    if tail <= 1e-4:
        return 0.75
    if tail <= 1e-2:
        return 0.5
    return 0.2


def _normalise_or_zero(values: np.ndarray) -> np.ndarray:
    arr = np.asarray(values, dtype=float)
    total = float(np.sum(arr))
    if total <= 0.0:
        return np.zeros_like(arr)
    return arr / total


def _decomposition_error(f: np.ndarray, f_by_k: np.ndarray) -> float:
    if f.size == 0:
        return 0.0
    return float(np.max(np.abs(f - np.sum(f_by_k, axis=1))))


def _q_label(q: float) -> str:
    return f"{float(q):.3g}".replace(".", "p")


def _case_title(dist, label: str) -> str:
    return (
        f"{label}: N={dist.N}, start={dist.start}, "
        f"q1={dist.q1:g}, q2={dist.q2:g}"
    )


def _figure_time_crop(f: np.ndarray, score) -> int:
    if f.size == 0:
        return 0
    mass = np.cumsum(f)
    threshold_idx = int(np.searchsorted(mass, 0.999 * max(float(mass[-1]), 1e-300)))
    candidates = [threshold_idx + 1, min(f.size, score.raw.t_main_index + 50)]
    if score.raw.t_late_index is not None:
        candidates.append(min(f.size, score.raw.t_late_index + 50))
    return max(5, min(f.size, max(candidates)))


def _max_or_nan(df: pd.DataFrame, column: str) -> float:
    if df.empty or column not in df:
        return float("nan")
    return float(pd.to_numeric(df[column]).max())


if __name__ == "__main__":
    main()
