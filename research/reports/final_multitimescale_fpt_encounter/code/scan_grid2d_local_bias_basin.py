#!/usr/bin/env python3
"""Exploratory 2D two-target scan with a local near-target bias basin.

This is report-local experiment code. It does not change the shared scientific
model. The goal is to test whether a plain reflecting 2D rectangle, without a
corridor geometry, can produce a more readable near/far double-peak curve by
adding a gentle local bias basin around the near target.

Scientific labels are computed on the raw exact discrete-time PMF. Readability
plots use binned probability mass only as a display transform.
"""

from __future__ import annotations

import csv
import math
import sys
from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[4]
FINAL_REPORT = ROOT / "research" / "reports" / "final_multitimescale_fpt_encounter"
FIGURE_DIR = FINAL_REPORT / "artifacts" / "figures"
DATA_DIR = FINAL_REPORT / "artifacts" / "data"

VKCORE_SRC = ROOT / "packages" / "vkcore" / "src"
sys.path.insert(0, str(VKCORE_SRC))

from vkcore.grid2d.two_target_bias_radius import (  # type: ignore  # noqa: E402
    DIR_VEC,
    TransitionKernel,
    exact_near_far_decomposition,
    validation_errors,
)
from vkcore.peaks import classify_distribution_shape  # type: ignore  # noqa: E402

Coord = tuple[int, int]

BIN_WIDTH = 4


@dataclass(frozen=True)
class LocalBiasCase:
    case_id: str
    near: Coord
    basin_radius: float
    global_bias: float
    local_bias: float
    hold_strength: float


def _idx(xy: Coord, Lx: int) -> int:
    return xy[1] * Lx + xy[0]


def _distance(a: Coord, b: Coord) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def _best_step_toward(xy: Coord, target: Coord, Lx: int, Ly: int) -> str:
    """Choose the cardinal move that most reduces distance to target."""

    current = _distance(xy, target)
    best: tuple[float, str] | None = None
    for direction, (dx, dy) in DIR_VEC.items():
        nxt = (xy[0] + dx, xy[1] + dy)
        if not (0 <= nxt[0] < Lx and 0 <= nxt[1] < Ly):
            continue
        gain = current - _distance(nxt, target)
        key = (gain, direction)
        if best is None or key > best:
            best = key
    if best is None or best[0] <= 0.0:
        return "E"
    return best[1]


def build_local_bias_basin_kernel(
    *,
    Lx: int,
    Ly: int,
    q: float,
    global_bias: float,
    local_bias: float,
    hold_strength: float,
    near_target: Coord,
    far_target: Coord,
    basin_radius: float,
) -> TransitionKernel:
    """Build a reflecting rectangle with global east bias and local near basin.

    Base rule:
    - outside the basin: four nearest-neighbour probabilities q/4 plus global
      east shift from stay probability;
    - inside the basin: movement is gently slowed by hold_strength, and a local
      inward bias points toward the near target.

    The local inward bias is weaker on cells adjacent to the target. This avoids
    turning the near channel into a one-step spike while still creating a basin
    of attraction.
    """

    absorbing = frozenset({near_target, far_target})
    src: list[int] = []
    dst: list[int] = []
    prob: list[float] = []

    for y in range(Ly):
        for x in range(Lx):
            xy = (x, y)
            i = _idx(xy, Lx)
            if xy in absorbing:
                src.append(i)
                dst.append(i)
                prob.append(1.0)
                continue

            d_near = _distance(xy, near_target)
            in_basin = d_near <= basin_radius
            hold_taper = max(0.0, 1.0 - d_near / max(basin_radius, 1e-12)) if in_basin else 0.0
            q_eff = q * (1.0 - hold_strength * hold_taper)
            stay = 1.0 - q_eff - global_bias
            if stay < -1e-14:
                raise ValueError("invalid q/global_bias combination")

            moves = {direction: q_eff / 4.0 for direction in DIR_VEC}
            moves["E"] += global_bias

            if in_basin and d_near > 1.0:
                # Zero next to the target, strongest at the basin edge.
                inward_taper = min(1.0, max(0.0, (d_near - 1.0) / max(basin_radius - 1.0, 1e-12)))
                local_shift = local_bias * inward_taper
                if local_shift > stay + 1e-14:
                    raise ValueError("invalid local_bias combination")
                stay -= local_shift
                moves[_best_step_toward(xy, near_target, Lx, Ly)] += local_shift

            row: dict[int, float] = {i: stay}
            for direction, p_move in moves.items():
                dx, dy = DIR_VEC[direction]
                nxt = (x + dx, y + dy)
                if not (0 <= nxt[0] < Lx and 0 <= nxt[1] < Ly):
                    row[i] = row.get(i, 0.0) + p_move
                else:
                    row[_idx(nxt, Lx)] = row.get(_idx(nxt, Lx), 0.0) + p_move

            row_sum = float(sum(row.values()))
            if abs(row_sum - 1.0) > 1e-12:
                raise ValueError(f"row sum != 1 at {xy}: {row_sum}")
            if min(row.values()) < -1e-14:
                raise ValueError(f"negative probability at {xy}")
            for j, p in row.items():
                src.append(i)
                dst.append(j)
                prob.append(float(p))

    return TransitionKernel(
        Lx=Lx,
        Ly=Ly,
        src=np.asarray(src, dtype=np.int64),
        dst=np.asarray(dst, dtype=np.int64),
        prob=np.asarray(prob, dtype=np.float64),
        absorbing=absorbing,
        q=float(q),
        bias_strength=float(global_bias),
        bias_direction="E",
        bias_rule=(
            "global east stay-to-direction shift plus local inward near-target "
            "bias basin with tapered local hold"
        ),
    )


def bin_mass(t: np.ndarray, values: np.ndarray, width: int, max_t: int) -> tuple[np.ndarray, np.ndarray]:
    centers: list[float] = []
    masses: list[float] = []
    for start in range(0, max_t + 1, width):
        stop = start + width
        mask = (t >= start) & (t < stop)
        if np.any(mask):
            centers.append(start + (width - 1) / 2)
            masses.append(float(np.sum(values[mask])))
    return np.asarray(centers), np.asarray(masses)


def roughness_index(y: np.ndarray) -> float:
    if len(y) < 3:
        return 0.0
    return float(np.sum(np.abs(np.diff(y, n=2))) / max(np.sum(y), 1e-15))


def run_case(case: LocalBiasCase) -> dict[str, object]:
    Lx, Ly = 23, 13
    start = (3, 6)
    far = (19, 6)
    q = 0.62
    kernel = build_local_bias_basin_kernel(
        Lx=Lx,
        Ly=Ly,
        q=q,
        global_bias=case.global_bias,
        local_bias=case.local_bias,
        hold_strength=case.hold_strength,
        near_target=case.near,
        far_target=far,
        basin_radius=case.basin_radius,
    )
    decomp = exact_near_far_decomposition(
        kernel=kernel,
        start=start,
        near_target=case.near,
        far_target=far,
        t_max=420,
    )
    shape = classify_distribution_shape(decomp.f_total)
    centers, binned = bin_mass(decomp.t, decomp.f_total, BIN_WIDTH, 180)
    _, binned_near = bin_mass(decomp.t, decomp.f_near, BIN_WIDTH, 180)
    _, binned_far = bin_mass(decomp.t, decomp.f_far, BIN_WIDTH, 180)
    errors = validation_errors(kernel, decomp)

    metrics = shape.metrics
    t1 = metrics.get("t1")
    t2 = metrics.get("t2")
    if t1 is None or t2 is None:
        early_near_fraction = 0.0
        late_far_fraction = 0.0
    else:
        t1i = int(t1)
        t2i = int(t2)
        early_total = float(decomp.f_total[t1i])
        late_total = float(decomp.f_total[t2i])
        early_near_fraction = float(decomp.f_near[t1i] / early_total) if early_total > 0 else 0.0
        late_far_fraction = float(decomp.f_far[t2i] / late_total) if late_total > 0 else 0.0

    return {
        "case": case,
        "Lx": Lx,
        "Ly": Ly,
        "q": q,
        "start": start,
        "far": far,
        "decomp": decomp,
        "centers": centers,
        "binned": binned,
        "binned_near": binned_near,
        "binned_far": binned_far,
        "classification": shape.classification,
        "metrics": metrics,
        "roughness": roughness_index(binned),
        "p_near": float(np.sum(decomp.f_near)),
        "p_far": float(np.sum(decomp.f_far)),
        "tail": float(decomp.survival[-1]),
        "early_near_fraction": early_near_fraction,
        "late_far_fraction": late_far_fraction,
        "errors": errors,
    }


def candidate_cases() -> list[LocalBiasCase]:
    near_positions = [(5, 9), (7, 9), (5, 3), (7, 3)]
    basin_radii = [2.5, 3.5, 4.5]
    global_biases = [0.08, 0.12, 0.16, 0.20]
    local_biases = [0.00, 0.04, 0.08, 0.12]
    hold_strengths = [0.00, 0.25, 0.45]

    out: list[LocalBiasCase] = []
    for near in near_positions:
        for basin_radius in basin_radii:
            for global_bias in global_biases:
                for local_bias in local_biases:
                    for hold_strength in hold_strengths:
                        out.append(
                            LocalBiasCase(
                                case_id=(
                                    f"near{near[0]}_{near[1]}_R{basin_radius:g}"
                                    f"_g{global_bias:.2f}_l{local_bias:.2f}_h{hold_strength:.2f}"
                                ).replace(".", "p"),
                                near=near,
                                basin_radius=basin_radius,
                                global_bias=global_bias,
                                local_bias=local_bias,
                                hold_strength=hold_strength,
                            )
                        )
    return out


def selection_key(result: dict[str, object]) -> tuple[float, float, float, float]:
    metrics = result["metrics"]
    score = float(metrics.get("score") or 0.0)
    channel_score = min(float(result["early_near_fraction"]), float(result["late_far_fraction"]))
    balance = min(float(result["p_near"]), float(result["p_far"])) / max(
        max(float(result["p_near"]), float(result["p_far"])), 1e-15
    )
    smooth_bonus = 1.0 / (1.0 + 40.0 * float(result["roughness"]))
    return (score * channel_score * smooth_bonus, balance, channel_score, -float(result["roughness"]))


def write_scan_csv(results: list[dict[str, object]], out_csv: Path) -> None:
    with out_csv.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(
            [
                "case_id",
                "near",
                "basin_radius",
                "global_bias",
                "local_bias",
                "hold_strength",
                "classification",
                "score",
                "t1",
                "tv",
                "t2",
                "R_peak",
                "R_valley",
                "p_near",
                "p_far",
                "survival_tail",
                "early_near_fraction",
                "late_far_fraction",
                "binned_roughness",
                "row_stochasticity_error",
                "mass_balance_error",
                "decomposition_error",
            ]
        )
        for result in results:
            case = result["case"]
            metrics = result["metrics"]
            errors = result["errors"]
            writer.writerow(
                [
                    case.case_id,
                    case.near,
                    f"{case.basin_radius:.3g}",
                    f"{case.global_bias:.3g}",
                    f"{case.local_bias:.3g}",
                    f"{case.hold_strength:.3g}",
                    result["classification"],
                    f"{float(metrics.get('score') or 0.0):.6g}",
                    metrics.get("t1"),
                    metrics.get("tv"),
                    metrics.get("t2"),
                    f"{float(metrics.get('R_peak') or 0.0):.6g}",
                    f"{float(metrics.get('R_valley') or 0.0):.6g}",
                    f"{float(result['p_near']):.6g}",
                    f"{float(result['p_far']):.6g}",
                    f"{float(result['tail']):.6g}",
                    f"{float(result['early_near_fraction']):.6g}",
                    f"{float(result['late_far_fraction']):.6g}",
                    f"{float(result['roughness']):.6g}",
                    f"{errors['row_stochasticity_error']:.6g}",
                    f"{errors['mass_balance_error']:.6g}",
                    f"{errors['decomposition_error']:.6g}",
                ]
            )


def plot_best(
    results: list[dict[str, object]],
    out_pdf: Path,
    out_png: Path,
    *,
    title: str = "2D two-target local-bias basin: smoother candidate curves",
    require_local_bias: bool = False,
) -> None:
    pool = [r for r in results if r["classification"] == "double_peak"]
    if require_local_bias:
        pool = [r for r in pool if r["case"].local_bias > 0.0]
    selected = sorted(
        pool,
        key=selection_key,
        reverse=True,
    )[:2]
    if not selected:
        selected = sorted(results, key=selection_key, reverse=True)[:2]

    fig, axes = plt.subplots(len(selected), 1, figsize=(7.6, 4.2 * len(selected)), squeeze=False)
    for ax, result in zip(axes[:, 0], selected, strict=True):
        case = result["case"]
        centers = result["centers"]
        ax.plot(centers, result["binned"], color="#111111", lw=2.6, marker="o", ms=4.2, label="total binned")
        ax.plot(centers, result["binned_near"], color="#1f77b4", lw=2.1, marker="o", ms=3.4, label="near binned")
        ax.plot(centers, result["binned_far"], color="#d95f02", lw=2.1, marker="o", ms=3.4, label="far binned")

        metrics = result["metrics"]
        for raw_t, label in ((metrics.get("t1"), "early raw peak"), (metrics.get("t2"), "late raw peak")):
            if raw_t is None:
                continue
            x = (int(raw_t) // BIN_WIDTH) * BIN_WIDTH + (BIN_WIDTH - 1) / 2
            ax.axvline(x, color="#333333", lw=1.0, ls="--", alpha=0.75)
            ax.text(x, ax.get_ylim()[1] * 0.93, label, rotation=90, ha="center", va="top", fontsize=9)

        ax.set_title(
            (
                f"{case.case_id}: {result['classification']}; "
                f"near={case.near}, R={case.basin_radius:g}, "
                f"g={case.global_bias:.2f}, local={case.local_bias:.2f}, hold={case.hold_strength:.2f}"
            ),
            fontsize=10.5,
        )
        ax.set_xlabel("time step t", fontsize=11)
        ax.set_ylabel(f"PMF mass per {BIN_WIDTH}-step bin", fontsize=11)
        ax.tick_params(axis="both", labelsize=10)
        ax.grid(True, alpha=0.22)
        ax.text(
            0.98,
            0.96,
            (
                f"p_near={float(result['p_near']):.3f}, p_far={float(result['p_far']):.3f}\n"
                f"raw t1={metrics.get('t1')}, tv={metrics.get('tv')}, t2={metrics.get('t2')}\n"
                f"R_peak={float(metrics.get('R_peak') or 0.0):.2f}, "
                f"R_valley={float(metrics.get('R_valley') or 0.0):.2f}\n"
                f"roughness={float(result['roughness']):.4f}"
            ),
            transform=ax.transAxes,
            ha="right",
            va="top",
            fontsize=9.0,
            bbox={"boxstyle": "round,pad=0.25", "facecolor": "white", "edgecolor": "#cccccc", "alpha": 0.92},
        )

    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=3, frameon=False, fontsize=10)
    fig.suptitle(title, fontsize=14)
    fig.tight_layout(rect=(0, 0.08, 1, 0.95), h_pad=2.0)
    fig.savefig(out_pdf, bbox_inches="tight")
    fig.savefig(out_png, dpi=220, bbox_inches="tight")
    plt.close(fig)


def plot_heatmap(results: list[dict[str, object]], out_pdf: Path, out_png: Path) -> None:
    global_biases = sorted({result["case"].global_bias for result in results})
    local_biases = sorted({result["case"].local_bias for result in results})
    counts = np.zeros((len(local_biases), len(global_biases)), dtype=float)
    best_scores = np.zeros_like(counts)

    for i, local_bias in enumerate(local_biases):
        for j, global_bias in enumerate(global_biases):
            bucket = [
                r
                for r in results
                if r["case"].local_bias == local_bias and r["case"].global_bias == global_bias
            ]
            positives = [r for r in bucket if r["classification"] == "double_peak"]
            counts[i, j] = len(positives)
            best_scores[i, j] = max((selection_key(r)[0] for r in bucket), default=0.0)

    fig, axes = plt.subplots(1, 2, figsize=(9.6, 3.8), constrained_layout=True)
    for ax, matrix, title, fmt in (
        (axes[0], counts, "number of raw double_peak cases", ".0f"),
        (axes[1], best_scores, "best smooth-channel score", ".1f"),
    ):
        image = ax.imshow(matrix, origin="lower", aspect="auto", cmap="viridis")
        ax.set_xticks(range(len(global_biases)), [f"{x:.2f}" for x in global_biases])
        ax.set_yticks(range(len(local_biases)), [f"{x:.2f}" for x in local_biases])
        ax.set_xlabel("global east bias")
        ax.set_ylabel("local inward bias")
        ax.set_title(title)
        for i in range(matrix.shape[0]):
            for j in range(matrix.shape[1]):
                ax.text(j, i, format(matrix[i, j], fmt), ha="center", va="center", color="white", fontsize=9)
        fig.colorbar(image, ax=ax, shrink=0.88)

    fig.savefig(out_pdf, bbox_inches="tight")
    fig.savefig(out_png, dpi=220, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    results = [run_case(case) for case in candidate_cases()]
    out_csv = DATA_DIR / "grid2d_local_bias_basin_scan.csv"
    write_scan_csv(results, out_csv)

    plot_best(
        results,
        FIGURE_DIR / "grid2d_local_bias_basin_best.pdf",
        FIGURE_DIR / "grid2d_local_bias_basin_best.png",
    )
    plot_best(
        results,
        FIGURE_DIR / "grid2d_local_bias_basin_local_positive_best.pdf",
        FIGURE_DIR / "grid2d_local_bias_basin_local_positive_best.png",
        title="2D two-target local-bias basin: best cases with local bias > 0",
        require_local_bias=True,
    )
    plot_heatmap(
        results,
        FIGURE_DIR / "grid2d_local_bias_basin_heatmap.pdf",
        FIGURE_DIR / "grid2d_local_bias_basin_heatmap.png",
    )

    n_double = sum(1 for result in results if result["classification"] == "double_peak")
    print(f"cases={len(results)} double_peak={n_double}")
    print(out_csv.relative_to(ROOT))
    print((FIGURE_DIR / "grid2d_local_bias_basin_best.pdf").relative_to(ROOT))
    print((FIGURE_DIR / "grid2d_local_bias_basin_local_positive_best.pdf").relative_to(ROOT))
    print((FIGURE_DIR / "grid2d_local_bias_basin_heatmap.pdf").relative_to(ROOT))


if __name__ == "__main__":
    main()
