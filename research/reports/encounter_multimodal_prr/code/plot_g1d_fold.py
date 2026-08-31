#!/usr/bin/env python3
"""Render the bounded G1d finite-grid fold diagnostic.

The figure is a deterministic visualization of the pinned G1d result and
manifest.  It recomputes only the displayed finite-volume curves and never
changes the frozen G1d evidence.  The allowed claim is one 65x65x49 finite-
grid fold at B=0.6; continuum, project-gate, and observable-trimodality claims
remain false.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

import continuum_g1d_fold_confirmation as fold
import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from scipy.sparse.linalg import expm_multiply  # noqa: E402

HERE = Path(__file__).resolve()
REPORT = HERE.parents[1]
DATA = REPORT / "artifacts" / "data"
FIGURES = REPORT / "artifacts" / "figures"
RESULT = DATA / "continuum_g1d_fold_confirmation_result.json"
MANIFEST = DATA / "continuum_g1d_fold_confirmation_manifest.json"
OUTPUT_PDF = FIGURES / "finite_grid_fold.pdf"
OUTPUT_PNG = FIGURES / "finite_grid_fold.png"
OUTPUT_METADATA = FIGURES / "finite_grid_fold_metadata.json"

EXPECTED_RESULT_SHA256 = "268e3f988330a2f28ad79b22cdf1f7e53a0142dc007d2a2a7cbfe40d18f91f92"
EXPECTED_MANIFEST_SHA256 = "2efb66fd4a924b036217368de9429df74872808de45375817b78c79635fad439"
EXPECTED_RUNNER_SHA256 = "5fa43e9482e5ee60cd5fb5c19427b1e749b750116f0861f5277e9fe1be46f3ec"

WINDOW_START = 3.0
WINDOW_STOP = 12.5
WINDOW_SPACING = 0.02
WINDOW_CHUNK_POINTS = 51
EXPECTED_MESH = (65, 65, 49)
EXPECTED_STATE_COUNT = 207_025
EXPECTED_BUDGET = 0.6
NORM_ESTIMATOR_SEED = 20_260_713


@dataclass(frozen=True)
class FigureData:
    times: np.ndarray
    controls: np.ndarray
    weights: np.ndarray
    densities: np.ndarray
    derivatives: np.ndarray
    strict_sign_change_brackets: tuple[tuple[tuple[float, float], ...], ...]
    chunk_diagnostics: tuple[dict[str, Any], ...]
    curve_digest_sha256: str
    installed_budget: float


def _require_hash(path: Path, expected: str, label: str) -> None:
    observed = fold.sha256(path)
    if observed != expected:
        raise ValueError(f"pinned {label} hash mismatch: expected {expected}, observed {observed}")


def preflight_sources(
    *,
    result_path: Path = RESULT,
    manifest_path: Path = MANIFEST,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Fail closed unless the pinned bounded result and manifest are intact."""

    _require_hash(result_path, EXPECTED_RESULT_SHA256, "result")
    _require_hash(manifest_path, EXPECTED_MANIFEST_SHA256, "manifest")
    result = fold.load_json(result_path)
    manifest = fold.load_json(manifest_path)

    if result["status"] != fold.PASS_STATUS:
        raise ValueError("frozen G1d result is not the bounded PASS artifact")
    if result["evidence_timing"] != "POST_RESULT_CONFIRMATION_NOT_PREREGISTERED_DISCOVERY":
        raise ValueError("G1d evidence-timing label changed")
    required_flags = {
        "finite_grid_fold_confirmed": True,
        "finite_B_Doi_fold": True,
        "continuum_verified": False,
        "project_gate_passed": False,
    }
    for flag, expected in required_flags.items():
        if result.get(flag) is not expected:
            raise ValueError(f"result flag {flag} must remain {expected}")
    if not all(result["checks"].values()):
        raise ValueError("one or more frozen G1d acceptance checks are false")
    if result["provenance"]["manifest_sha256"] != EXPECTED_MANIFEST_SHA256:
        raise ValueError("result does not pin the expected G1d manifest")
    if result["provenance"]["runner_sha256"] != EXPECTED_RUNNER_SHA256:
        raise ValueError("result does not pin the expected G1d runner")
    if manifest["pinned_inputs"]["runner_sha256"] != EXPECTED_RUNNER_SHA256:
        raise ValueError("manifest does not pin the expected G1d runner")
    if result["selected_segment"] != manifest["selected_segment"]:
        raise ValueError("result and manifest selected segments disagree")
    mesh = result["configuration"]["mesh"]
    observed_mesh = (
        int(mesh["midpoint_cells"]),
        int(mesh["relative_parallel_cells"]),
        int(mesh["relative_perp_cells"]),
    )
    if observed_mesh != EXPECTED_MESH or int(mesh["state_count"]) != EXPECTED_STATE_COUNT:
        raise ValueError("G1d figure is restricted to the pinned 65x65x49 mesh")
    if [row["root_count"] for row in result["side_topology"]] != [3, 1]:
        raise ValueError("frozen one-versus-three side topology changed")
    if result["side_topology"][0]["topology"] != ["maximum", "minimum", "maximum"]:
        raise ValueError("frozen lower-side max-min-max topology changed")
    fold.validate_pins(manifest)
    return result, manifest


def barycentric_xy(weights: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Map (w1,w2,w3) to an equilateral simplex with w3 at the apex."""

    values = np.asarray(weights, dtype=float)
    if values.ndim != 2 or values.shape[1] != 3:
        raise ValueError("barycentric weights must have shape (n,3)")
    if not np.allclose(np.sum(values, axis=1), 1.0, atol=2.0e-14, rtol=0.0):
        raise ValueError("barycentric weights must sum to one")
    if float(np.min(values)) < -2.0e-14:
        raise ValueError("barycentric weights must be nonnegative")
    x = values[:, 1] + 0.5 * values[:, 2]
    y = (np.sqrt(3.0) / 2.0) * values[:, 2]
    return x, y


def strict_sign_change_brackets(
    times: np.ndarray,
    derivative: np.ndarray,
) -> tuple[tuple[float, float], ...]:
    """Return only adjacent strict sign-change brackets, exactly as advertised."""

    values = np.asarray(derivative, dtype=float)
    if values.shape != times.shape or not np.isfinite(values).all():
        raise ValueError("invalid derivative curve")
    return tuple(
        (float(times[index]), float(times[index + 1]))
        for index in range(len(times) - 1)
        if values[index] * values[index + 1] < 0.0
    )


def _curve_digest(
    times: np.ndarray,
    controls: np.ndarray,
    densities: np.ndarray,
    derivatives: np.ndarray,
) -> str:
    digest = hashlib.sha256()
    for array in (times, controls, densities, derivatives):
        values = np.ascontiguousarray(np.asarray(array, dtype="<f8"))
        digest.update(str(values.shape).encode("ascii"))
        digest.update(values.tobytes(order="C"))
    return digest.hexdigest()


def _evaluate_control_window(
    config: Any,
    control: float,
    times: np.ndarray,
    *,
    chunk_points: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, dict[str, Any]]:
    """Evaluate f and f_t in bounded-memory chunks on one display window."""

    spacings = np.diff(times)
    if (
        len(times) < 2
        or chunk_points < 2
        or not np.allclose(spacings, WINDOW_SPACING, rtol=0.0, atol=2.0e-15)
    ):
        raise ValueError("display grid must use the frozen 0.02 spacing")
    model, weights, generator_derivative = fold.assemble_float_model(config, control)
    budget = float(model.parameters.installed_budget)
    if not np.isclose(budget, EXPECTED_BUDGET, rtol=0.0, atol=1.0e-15):
        raise ValueError("G1d figure is restricted to B=0.6")

    generator = model.killed_generator.tocsr()
    operator = generator.T.tocsr()
    trace = float(np.sum(generator.diagonal()))
    values, _derivatives = fold.action_jets(
        model,
        generator_derivative,
        maximum_order=1,
    )
    actions = np.column_stack(values)
    start = float(times[0])
    current = np.asarray(
        expm_multiply(operator * start, model.initial, traceA=start * trace),
        dtype=float,
    )
    initial_observables = current @ actions
    density = [float(initial_observables[0])]
    derivative = [float(initial_observables[1])]
    survival = [float(np.sum(current))]
    minimum_state_mass = float(np.min(current))
    cursor = 0
    chunks = 0
    maximum_rows = 1
    while cursor < len(times) - 1:
        end = min(cursor + chunk_points - 1, len(times) - 1)
        steps = end - cursor
        rows = steps + 1
        states = np.asarray(
            expm_multiply(
                operator,
                current,
                start=0.0,
                stop=WINDOW_SPACING * steps,
                num=rows,
                endpoint=True,
                traceA=trace,
            ),
            dtype=float,
        )
        minimum_state_mass = min(minimum_state_mass, float(np.min(states)))
        new_states = states[1:]
        observables = new_states @ actions
        density.extend(float(value) for value in observables[:, 0])
        derivative.extend(float(value) for value in observables[:, 1])
        survival.extend(float(value) for value in np.sum(new_states, axis=1))
        current = states[-1].copy()
        cursor = end
        chunks += 1
        maximum_rows = max(maximum_rows, rows)

    density_array = np.asarray(density, dtype=float)
    derivative_array = np.asarray(derivative, dtype=float)
    survival_array = np.asarray(survival, dtype=float)
    if (
        density_array.shape != times.shape
        or derivative_array.shape != times.shape
        or survival_array.shape != times.shape
        or not np.isfinite(density_array).all()
        or not np.isfinite(derivative_array).all()
    ):
        raise FloatingPointError("invalid finite-grid display curve")
    maximum_survival_increase = float(np.max(np.diff(survival_array)))
    if minimum_state_mass < -1.0e-11 or float(np.min(density_array)) < -1.0e-11:
        raise RuntimeError("display semigroup produced negative mass or density")
    if maximum_survival_increase > 1.0e-10:
        raise RuntimeError("display-window survival is not monotone")
    return (
        density_array,
        derivative_array,
        weights,
        {
            "control": float(control),
            "state_dimension": int(model.grid.state_count),
            "installed_budget": budget,
            "chunk_count": chunks,
            "chunk_points_limit": chunk_points,
            "maximum_chunk_state_rows": maximum_rows,
            "full_state_history_stored": False,
            "minimum_state_mass": minimum_state_mass,
            "minimum_density": float(np.min(density_array)),
            "maximum_survival_increase": maximum_survival_increase,
            "window_start": float(times[0]),
            "window_stop": float(times[-1]),
            "spacing": WINDOW_SPACING,
        },
    )


def _root_is_in_bracket(root: float, bracket: tuple[float, float]) -> bool:
    return bracket[0] <= root <= bracket[1]


def recompute_figure_data(
    result: dict[str, Any],
    manifest: dict[str, Any],
) -> FigureData:
    """Recompute only the three displayed finite-grid curves."""

    fold.require_repository_venv()
    # SciPy's sparse 1-norm estimator uses NumPy's legacy global RNG when it
    # chooses exponential-action parameters.  Reset it here so that repeated
    # figure builds use the same numerical path and export identical curves.
    np.random.seed(NORM_ESTIMATOR_SEED)
    side = manifest["side_topology"]
    if (
        float(side["analysis_start"]) != WINDOW_START
        or float(side["spacing"]) != WINDOW_SPACING
        or WINDOW_STOP > float(side["stop"])
    ):
        raise ValueError("display window is not contained in the frozen side scan")
    ticks = int(round((WINDOW_STOP - WINDOW_START) / WINDOW_SPACING))
    times = WINDOW_START + WINDOW_SPACING * np.arange(ticks + 1, dtype=float)
    if not np.isclose(times[-1], WINDOW_STOP, rtol=0.0, atol=2.0e-15):
        raise ValueError("display-window integer ticks are inconsistent")

    fold_control = float(result["fold"]["control"])
    offset = float(side["control_offset"])
    controls = np.asarray((fold_control - offset, fold_control, fold_control + offset))
    config = fold.configuration()
    density_rows = []
    derivative_rows = []
    weight_rows = []
    brackets = []
    diagnostics = []
    for control in controls:
        print(f"recomputing display curve at control={control:.15g}")
        density, derivative, weights, diagnostic = _evaluate_control_window(
            config,
            float(control),
            times,
            chunk_points=WINDOW_CHUNK_POINTS,
        )
        density_rows.append(density)
        derivative_rows.append(derivative)
        weight_rows.append(weights)
        brackets.append(strict_sign_change_brackets(times, derivative))
        diagnostics.append(diagnostic)

    densities = np.vstack(density_rows)
    derivatives = np.vstack(derivative_rows)
    weights = np.vstack(weight_rows)
    expected_weights = np.asarray(
        (
            result["side_topology"][0]["weights"],
            result["fold"]["weights"],
            result["side_topology"][1]["weights"],
        ),
        dtype=float,
    )
    if not np.allclose(weights, expected_weights, rtol=0.0, atol=2.0e-15):
        raise RuntimeError("recomputed display weights disagree with the frozen artifact")

    for curve_index, side_row in ((0, result["side_topology"][0]), (2, result["side_topology"][1])):
        curve_brackets = brackets[curve_index]
        retained_roots = side_row["roots"]
        if len(curve_brackets) != len(retained_roots):
            raise RuntimeError("recomputed strict sign-change count disagrees with G1d")
        for bracket, root in zip(curve_brackets, retained_roots, strict=True):
            if not _root_is_in_bracket(float(root["time"]), bracket):
                raise RuntimeError("a retained G1d root left its recomputed sign bracket")

    nearest_fold_index = int(np.argmin(np.abs(times - float(result["fold"]["time"]))))
    scaled_near_fold = abs(
        float(result["fold"]["time"])
        * derivatives[1, nearest_fold_index]
        / float(result["fold"]["density"])
    )
    if scaled_near_fold > 1.0e-4:
        raise RuntimeError("recomputed fold-control curve misses the stored fold")

    digest = _curve_digest(times, controls, densities, derivatives)
    return FigureData(
        times=times,
        controls=controls,
        weights=weights,
        densities=densities,
        derivatives=derivatives,
        strict_sign_change_brackets=tuple(brackets),
        chunk_diagnostics=tuple(diagnostics),
        curve_digest_sha256=digest,
        installed_budget=float(diagnostics[0]["installed_budget"]),
    )


def normal_form_control_offsets(
    result: dict[str, Any],
    time_offsets: np.ndarray,
) -> np.ndarray:
    """Return the local quadratic stationary branch from the exact fold jets."""

    f_tlambda = float(result["fold"]["control_jets_orders_0_to_3"][1])
    f_ttt = float(result["fold"]["time_jets_orders_0_to_3"][3])
    if f_tlambda == 0.0 or f_ttt == 0.0:
        raise ValueError("degenerate fold jet")
    offsets = np.asarray(time_offsets, dtype=float)
    return -0.5 * f_ttt / f_tlambda * offsets**2


def predicted_time_offset_magnitude(
    result: dict[str, Any],
    control_offset: float,
) -> float:
    """Solve the quadratic fold jet for |t-t*| at a control offset."""

    f_tlambda = float(result["fold"]["control_jets_orders_0_to_3"][1])
    f_ttt = float(result["fold"]["time_jets_orders_0_to_3"][3])
    square = -2.0 * f_tlambda * float(control_offset) / f_ttt
    if square <= 0.0:
        raise ValueError("the local normal form has no real stationary pair on this side")
    return float(np.sqrt(square))


def _plot_selected_segment(
    ax: plt.Axes,
    data: FigureData,
    result: dict[str, Any],
    manifest: dict[str, Any],
) -> None:
    segment = manifest["selected_segment"]
    endpoints = np.asarray((segment["left_weights"], segment["right_weights"]), dtype=float)
    fold_weights = np.asarray([result["fold"]["weights"]], dtype=float)
    seed_weights = np.asarray([segment["g1c_seed_weights"]], dtype=float)
    endpoint_x, endpoint_y = barycentric_xy(endpoints)
    fold_x, fold_y = barycentric_xy(fold_weights)
    seed_x, seed_y = barycentric_xy(seed_weights)

    ax.grid(False)
    ax.plot(endpoint_x, endpoint_y, color="#2F6B9A", linewidth=2.2, solid_capstyle="round")
    ax.annotate(
        "",
        xy=(endpoint_x[1], endpoint_y[1]),
        xytext=(endpoint_x[0], endpoint_y[0]),
        arrowprops={"arrowstyle": "->", "color": "#2F6B9A", "linewidth": 1.2},
    )
    ax.plot(
        endpoint_x,
        endpoint_y,
        linestyle="none",
        marker="o",
        markersize=4.5,
        markerfacecolor="white",
        markeredgecolor="#2F6B9A",
        markeredgewidth=1.0,
    )
    ax.plot(
        fold_x,
        fold_y,
        linestyle="none",
        marker="D",
        markersize=6.0,
        markerfacecolor="#C46A2B",
        markeredgecolor="#8D431F",
        markeredgewidth=0.8,
        zorder=5,
    )
    ax.plot(
        seed_x,
        seed_y,
        linestyle="none",
        marker="o",
        markersize=7.0,
        markerfacecolor="white",
        markeredgecolor="#22252A",
        markeredgewidth=1.0,
        zorder=4,
    )
    ax.annotate(
        "λ=0\n(0.20, 0, 0.80)",
        xy=(endpoint_x[0], endpoint_y[0]),
        xytext=(-4, 9),
        textcoords="offset points",
        ha="right",
        va="bottom",
        fontsize=6.6,
    )
    ax.annotate(
        "λ=1\n(0.20, 0.10, 0.70)",
        xy=(endpoint_x[1], endpoint_y[1]),
        xytext=(5, -16),
        textcoords="offset points",
        ha="left",
        va="top",
        fontsize=6.6,
    )
    ax.annotate(
        f"fold λ*={float(result['fold']['control']):.4f}",
        xy=(fold_x[0], fold_y[0]),
        xytext=(-10, 25),
        textcoords="offset points",
        ha="right",
        va="bottom",
        fontsize=7.0,
        color="#75391D",
        arrowprops={"arrowstyle": "-", "color": "#8D431F", "linewidth": 0.7},
    )
    ax.annotate(
        f"G1c seed {float(segment['g1c_seed_control']):.4f}",
        xy=(seed_x[0], seed_y[0]),
        xytext=(25, 14),
        textcoords="offset points",
        ha="left",
        va="bottom",
        fontsize=6.8,
        arrowprops={"arrowstyle": "-", "color": "#555A62", "linewidth": 0.7},
    )
    x_pad = 0.042
    y_pad = 0.050
    ax.set_xlim(float(np.min(endpoint_x)) - x_pad, float(np.max(endpoint_x)) + x_pad)
    ax.set_ylim(float(np.min(endpoint_y)) - y_pad, float(np.max(endpoint_y)) + y_pad)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(
        "(a) Frozen simplex segment\nw(λ)=(0.2, 0.1λ, 0.8−0.1λ)",
        loc="left",
        pad=3.0,
    )
    ax.text(
        0.01,
        0.02,
        f"first weight = 0.20  •  B={data.installed_budget:.1f}",
        transform=ax.transAxes,
        ha="left",
        va="bottom",
        fontsize=6.8,
        color="#444950",
    )

    inset = ax.inset_axes([0.68, 0.63, 0.28, 0.29])
    height = np.sqrt(3.0) / 2.0
    inset.plot((0.0, 1.0, 0.5, 0.0), (0.0, 0.0, height, 0.0), color="#777C84", lw=0.7)
    inset.plot(endpoint_x, endpoint_y, color="#2F6B9A", linewidth=2.0)
    inset.plot(
        fold_x,
        fold_y,
        linestyle="none",
        marker="D",
        markersize=3.2,
        color="#C46A2B",
    )
    inset.set_xlim(-0.05, 1.05)
    inset.set_ylim(-0.04, height + 0.05)
    inset.set_aspect("equal")
    inset.axis("off")
    inset.set_title("full simplex", fontsize=6.0, pad=0.5, color="#555A62")


def _plot_derivative_window(
    ax: plt.Axes,
    data: FigureData,
    result: dict[str, Any],
) -> None:
    fold_time = float(result["fold"]["time"])
    fold_density = float(result["fold"]["density"])
    scale = fold_time / fold_density
    scaled = scale * data.derivatives
    colours = ("#2F6B9A", "#22252A", "#C46A2B")
    styles = ("-", "--", "-.")
    labels = (
        "λ*−0.02  (3 retained roots)",
        "λ*  (fold)",
        "λ*+0.02  (1 retained root)",
    )
    local_start = 9.55
    local_stop = 11.45
    local_keep = (data.times >= local_start) & (data.times <= local_stop)
    ax.axhline(0.0, color="#777C84", linewidth=0.8)
    for index, (colour, style, label) in enumerate(zip(colours, styles, labels, strict=True)):
        ax.plot(
            data.times,
            scaled[index],
            color=colour,
            linestyle=style,
            linewidth=1.55 if index != 1 else 1.35,
            label=label,
        )
    ax.plot(
        fold_time,
        0.0,
        linestyle="none",
        marker="D",
        markersize=4.8,
        markerfacecolor="#22252A",
        markeredgecolor="#22252A",
        zorder=5,
    )

    side_styles = (
        (result["side_topology"][0], colours[0], True),
        (result["side_topology"][1], colours[2], False),
    )
    for side_row, colour, filled in side_styles:
        for root in side_row["roots"]:
            marker = "v" if root["topology"] == "maximum" else "^"
            root_time = float(root["time"])
            if local_start <= root_time <= local_stop:
                ax.plot(
                    root_time,
                    0.0,
                    linestyle="none",
                    marker=marker,
                    markersize=5.2,
                    markerfacecolor=colour if filled else "white",
                    markeredgecolor=colour,
                    markeredgewidth=0.9,
                    zorder=6,
                )
    ax.set_xlim(local_start, local_stop)
    lower = float(np.min(scaled[:, local_keep]))
    upper = float(np.max(scaled[:, local_keep]))
    span = upper - lower
    ax.set_ylim(lower - 0.14 * span, upper + 0.14 * span)
    ax.set_xlabel("Dimensionless time, t")
    ax.set_ylabel("Scaled derivative, t* f_t / f*")
    ax.set_title(
        "(b) Finite-grid stationary-point unfolding\n"
        "Fold window at λ* and λ*±0.02; early maxima inset",
        loc="left",
    )
    ax.legend(loc="upper right", frameon=False, fontsize=6.6, handlelength=2.5)
    ax.text(
        0.018,
        0.025,
        "Markers: retained strict sign-change roots\n"
        "on the frozen Δt=0.02 scan; not an\n"
        "interval-global exclusion of additional roots.",
        transform=ax.transAxes,
        ha="left",
        va="bottom",
        fontsize=5.95,
        color="#444950",
        bbox={"boxstyle": "square,pad=0.18", "facecolor": "white", "edgecolor": "#D6DCE3"},
    )

    inset = ax.inset_axes([0.055, 0.57, 0.34, 0.31])
    inset.set_zorder(10)
    inset.patch.set_facecolor("white")
    inset.patch.set_edgecolor("white")
    inset.patch.set_linewidth(0.0)
    for spine in inset.spines.values():
        spine.set_color("#777C84")
        spine.set_linewidth(0.55)
    inset.axhline(0.0, color="#777C84", linewidth=0.55)
    for index, (colour, style) in enumerate(zip(colours, styles, strict=True)):
        inset.plot(
            data.times,
            scaled[index],
            color=colour,
            linestyle=style,
            linewidth=1.0,
        )
    for side_row, colour, filled in side_styles:
        early_roots = [row for row in side_row["roots"] if float(row["time"]) < 7.0]
        for root in early_roots:
            inset.plot(
                float(root["time"]),
                0.0,
                linestyle="none",
                marker="v",
                markersize=4.0,
                markerfacecolor=colour if filled else "white",
                markeredgecolor=colour,
                markeredgewidth=0.7,
                zorder=5,
            )
    inset.set_xlim(4.75, 5.30)
    early_keep = (data.times >= 4.75) & (data.times <= 5.30)
    early_lower = float(np.min(scaled[:, early_keep]))
    early_upper = float(np.max(scaled[:, early_keep]))
    early_span = early_upper - early_lower
    inset.set_ylim(early_lower - 0.12 * early_span, early_upper + 0.12 * early_span)
    inset.set_title("early max roots", fontsize=5.9, pad=1.0, color="#444950")
    inset.tick_params(axis="both", labelsize=5.6, length=2.2, pad=1.0)
    inset.set_xticks((4.8, 5.0, 5.2))
    inset.set_yticks(())


def _plot_normal_form(ax: plt.Axes, result: dict[str, Any]) -> None:
    fold_time = float(result["fold"]["time"])
    time_offsets = np.linspace(-0.58, 0.58, 301)
    control_offsets = normal_form_control_offsets(result, time_offsets)
    keep = control_offsets >= -0.032
    ax.axhline(0.0, color="#777C84", linewidth=0.75)
    ax.axvline(0.0, color="#B4B8BE", linewidth=0.65)
    ax.axhline(-0.02, color="#B4B8BE", linewidth=0.65, linestyle=":")
    ax.plot(
        time_offsets[keep],
        control_offsets[keep],
        color="#2F6B9A",
        linewidth=1.65,
        label="quadratic fold jet",
    )
    lower_side = result["side_topology"][0]
    local_roots = [row for row in lower_side["roots"] if abs(float(row["time"]) - fold_time) <= 2.0]
    if [row["topology"] for row in local_roots] != ["minimum", "maximum"]:
        raise RuntimeError("stored lower-side local root pair changed")
    for row in local_roots:
        marker = "^" if row["topology"] == "minimum" else "v"
        ax.plot(
            float(row["time"]) - fold_time,
            float(lower_side["control"]) - float(result["fold"]["control"]),
            linestyle="none",
            marker=marker,
            markersize=6.0,
            markerfacecolor="#C46A2B",
            markeredgecolor="#8D431F",
            markeredgewidth=0.8,
            zorder=5,
        )
    ax.plot(
        0.0,
        0.0,
        linestyle="none",
        marker="D",
        markersize=5.2,
        markerfacecolor="#22252A",
        markeredgecolor="#22252A",
        label="confirmed fold",
        zorder=6,
    )
    ax.text(
        0.97,
        0.91,
        "λ*+0.02: local fold pair absent",
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=6.7,
        color="#75391D",
    )
    scaled = result["fold"]["scaled_fold_jet"]
    determinant = float(result["fold"]["dimensionless_jacobian_determinant"])
    ax.text(
        0.025,
        0.055,
        f"scaled f_ttt = {float(scaled['f_ttt']):.3f}\n"
        f"scaled f_tλ = {float(scaled['f_tlambda']):.3f}\n"
        f"det(J_scaled) = {determinant:.3f}",
        transform=ax.transAxes,
        ha="left",
        va="bottom",
        fontsize=6.8,
        color="#33363B",
    )
    root_handle = Line2D(
        [],
        [],
        linestyle="none",
        marker="^",
        markersize=5.0,
        markerfacecolor="#C46A2B",
        markeredgecolor="#8D431F",
        label="retained λ*−0.02 local roots",
    )
    handles, labels = ax.get_legend_handles_labels()
    handles.append(root_handle)
    labels.append(root_handle.get_label())
    ax.legend(handles, labels, loc="lower right", frameon=False, fontsize=6.5, handlelength=2.2)
    ax.set_xlim(-0.62, 0.62)
    ax.set_ylim(-0.033, 0.006)
    ax.set_xlabel("Time offset, t − t*")
    ax.set_ylabel("Control offset, λ − λ*")
    ax.set_title(
        "(c) Local fold jet and stationary-time branch\n"
        "Line is a local quadratic diagnostic, not global continuation",
        loc="left",
    )


def render_figure(
    data: FigureData,
    result: dict[str, Any],
    manifest: dict[str, Any],
    pdf_path: Path,
    png_path: Path,
) -> None:
    """Render deterministic vector and preview outputs without transparency."""

    rc = {
        "font.family": "DejaVu Sans",
        "font.size": 8.0,
        "axes.titlesize": 9.0,
        "axes.titleweight": "normal",
        "axes.labelsize": 7.7,
        "axes.edgecolor": "#4E535A",
        "axes.linewidth": 0.75,
        "axes.grid": True,
        "axes.axisbelow": True,
        "grid.color": "#E3E6EA",
        "grid.linewidth": 0.55,
        "grid.alpha": 1.0,
        "xtick.labelsize": 7.0,
        "ytick.labelsize": 7.0,
        "xtick.color": "#4E535A",
        "ytick.color": "#4E535A",
        "text.color": "#22252A",
        "axes.labelcolor": "#33363B",
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "savefig.facecolor": "white",
        "savefig.transparent": False,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    }
    with plt.rc_context(rc):
        figure = plt.figure(figsize=(7.2, 5.8))
        grid = figure.add_gridspec(
            2,
            2,
            width_ratios=(0.88, 1.42),
            height_ratios=(1.02, 0.92),
        )
        panel_a = figure.add_subplot(grid[0, 0])
        panel_b = figure.add_subplot(grid[0, 1])
        panel_c = figure.add_subplot(grid[1, :])
        for panel in (panel_a, panel_b, panel_c):
            panel.patch.set_edgecolor("white")
            panel.patch.set_linewidth(0.0)
        _plot_selected_segment(panel_a, data, result, manifest)
        _plot_derivative_window(panel_b, data, result)
        _plot_normal_form(panel_c, result)
        figure.subplots_adjust(
            left=0.085,
            right=0.985,
            bottom=0.125,
            top=0.945,
            wspace=0.27,
            hspace=0.42,
        )
        figure.text(
            0.5,
            0.026,
            "One 65×65×49 finite-grid B=0.6 fold only  •  continuum=false  •  "
            "project gate=false  •  no observable-trimodality claim",
            ha="center",
            va="bottom",
            fontsize=6.8,
            color="#444950",
        )
        pdf_path.parent.mkdir(parents=True, exist_ok=True)
        png_path.parent.mkdir(parents=True, exist_ok=True)
        fixed_date = datetime(2026, 7, 13, tzinfo=timezone.utc)
        pdf_metadata = {
            "Title": "G1d finite-grid fold diagnostic",
            "Author": "Encounter multimodality project",
            "Subject": "One 65x65x49 finite-grid B=0.6 fold only",
            "Keywords": "encounter time, fold, finite grid, Doi model, B=0.6",
            "Creator": "plot_g1d_fold.py",
            "CreationDate": fixed_date,
            "ModDate": fixed_date,
        }
        figure.savefig(
            pdf_path,
            format="pdf",
            dpi=300,
            facecolor="white",
            edgecolor="white",
            metadata=pdf_metadata,
        )
        figure.savefig(
            png_path,
            format="png",
            dpi=240,
            facecolor="white",
            edgecolor="white",
            metadata={"Software": "plot_g1d_fold.py"},
        )
        plt.close(figure)


def verify_vector_pdf(path: Path) -> dict[str, int]:
    """Reject Type 3 fonts, transparency states, and raster image XObjects."""

    payload = path.read_bytes()
    if not payload.startswith(b"%PDF-"):
        raise RuntimeError("figure output is not a PDF")
    type3_tokens = len(re.findall(rb"/Type3\b", payload))
    transparency_tokens = len(re.findall(rb"/(?:ca|CA|SMask|BM)\b", payload))
    raster_image_tokens = len(re.findall(rb"/Subtype\s*/Image\b", payload))
    if type3_tokens:
        raise RuntimeError("figure PDF contains a Type 3 font")
    if transparency_tokens:
        raise RuntimeError("figure PDF contains a transparency graphics-state token")
    if raster_image_tokens:
        raise RuntimeError("figure PDF contains a raster image XObject")
    return {
        "type3_font_tokens": type3_tokens,
        "transparency_graphics_state_tokens": transparency_tokens,
        "raster_image_xobject_tokens": raster_image_tokens,
    }


def _display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPORT.resolve()))
    except ValueError:
        return str(path)


def build_metadata(
    data: FigureData,
    result: dict[str, Any],
    manifest: dict[str, Any],
    *,
    pdf_path: Path,
    png_path: Path,
    pdf_qa: dict[str, int],
) -> dict[str, Any]:
    fold_control = float(result["fold"]["control"])
    lower_control = float(result["side_topology"][0]["control"])
    local_roots = [
        row
        for row in result["side_topology"][0]["roots"]
        if abs(float(row["time"]) - float(result["fold"]["time"])) <= 2.0
    ]
    predicted = predicted_time_offset_magnitude(result, lower_control - fold_control)
    caption = (
        "Finite-grid G1d fold diagnostic. (a) The frozen catalyst-weight simplex segment and "
        "the confirmed control. (b) Recomputed finite-volume f_t curves at lambda*, "
        "lambda*-0.02, and lambda*+0.02, with the artifact's retained sign-changing roots "
        "marked. (c) The local quadratic fold jet and the retained lower-side local pair. "
        "This is one 65x65x49 finite-grid B=0.6 fold only. The side roots are retained "
        "sign-changing roots from the frozen 0.02 scan, not an interval-global root proof. "
        "The continuum_verified and project_gate_passed flags are false, and the figure is "
        "not evidence of observable trimodality."
    )
    return {
        "schema_version": 1,
        "stage": "G1d_finite_grid_fold_figure",
        "status": "PASS_BOUNDED_FIGURE_REPRODUCTION",
        "evidence_timing": result["evidence_timing"],
        "claim_scope": "one 65x65x49 finite-grid B=0.6 fold only",
        "finite_grid_fold_confirmed": True,
        "finite_B_Doi_fold": True,
        "continuum_verified": False,
        "project_gate_passed": False,
        "observable_trimodality_verified": False,
        "interval_global_root_proof": False,
        "side_root_semantics": (
            "retained strict sign-changing roots on the frozen spacing-0.02 side scan"
        ),
        "source_pins": {
            "result": str(RESULT.relative_to(REPORT)),
            "result_sha256": EXPECTED_RESULT_SHA256,
            "manifest": str(MANIFEST.relative_to(REPORT)),
            "manifest_sha256": EXPECTED_MANIFEST_SHA256,
            "runner": result["provenance"]["runner"],
            "runner_sha256": EXPECTED_RUNNER_SHA256,
        },
        "recomputation": {
            "mesh": list(EXPECTED_MESH),
            "state_count": EXPECTED_STATE_COUNT,
            "installed_budget": data.installed_budget,
            "time_window": {
                "start": float(data.times[0]),
                "stop": float(data.times[-1]),
                "spacing": WINDOW_SPACING,
                "points": int(len(data.times)),
            },
            "controls": data.controls.tolist(),
            "weights": data.weights.tolist(),
            "strict_sign_change_bracket_counts_all_three_controls": [
                len(row) for row in data.strict_sign_change_brackets
            ],
            "strict_sign_change_brackets_all_three_controls": [
                [list(bracket) for bracket in row] for row in data.strict_sign_change_brackets
            ],
            "retained_side_root_counts": [
                int(row["root_count"]) for row in result["side_topology"]
            ],
            "curve_digest_sha256": data.curve_digest_sha256,
            "sparse_norm_estimator_seed": NORM_ESTIMATOR_SEED,
            "chunk_diagnostics": list(data.chunk_diagnostics),
        },
        "normal_form": {
            "definition": "f_t approximately f_tlambda*delta_lambda + 0.5*f_ttt*delta_t^2",
            "f_tlambda": float(result["fold"]["control_jets_orders_0_to_3"][1]),
            "f_ttt": float(result["fold"]["time_jets_orders_0_to_3"][3]),
            "predicted_abs_time_offset_at_lambda_minus_0p02": predicted,
            "retained_local_time_offsets_at_lambda_minus_0p02": [
                float(row["time"]) - float(result["fold"]["time"]) for row in local_roots
            ],
            "dimensionless_jacobian_determinant": float(
                result["fold"]["dimensionless_jacobian_determinant"]
            ),
            "scope": "local quadratic jet diagnostic, not global continuation",
        },
        "chart_contract": {
            "analytical_question": (
                "Where is the frozen G1d fold on its simplex segment, how do the retained "
                "stationary roots unfold at lambda* plus or minus 0.02, and do the exact "
                "local jets have the expected nondegenerate fold geometry?"
            ),
            "takeaway": (
                "The pinned 65x65x49 B=0.6 model has one nondegenerate finite-grid fold; "
                "the lower side retains a local min-max pair while the upper side does not."
            ),
            "panels": {
                "a": "selected catalyst-weight simplex segment, G1c seed, and fold control",
                "b": "recomputed scaled f_t curves with retained strict sign-change roots",
                "c": "local quadratic fold branch and exact lower-side local root pair",
            },
            "palette_policy": (
                "hard two-root cap: blue and orange plus neutrals; line style, marker shape, "
                "and open fill provide non-colour distinctions"
            ),
            "renderer": "Matplotlib static PDF and PNG",
        },
        "render_policy": {
            "figure_inches": [7.2, 5.8],
            "pdf_fonttype": 42,
            "transparent_background": False,
            "font_family": "DejaVu Sans",
            "fixed_pdf_metadata_date": "2026-07-13T00:00:00Z",
        },
        "pdf_qa": pdf_qa,
        "outputs": {
            "pdf": _display_path(pdf_path),
            "pdf_sha256": fold.sha256(pdf_path),
            "png": _display_path(png_path),
            "png_sha256": fold.sha256(png_path),
        },
        "provenance": {
            "plot_script": str(HERE.relative_to(REPORT)),
            "plot_script_sha256": fold.sha256(HERE),
            "source_result_generated_utc": result["provenance"]["generated_utc"],
            "python": platform.python_version(),
            "python_executable": sys.executable,
            "numpy": np.__version__,
            "matplotlib": matplotlib.__version__,
        },
        "limitations": list(result["limitations"]),
        "caption": caption,
        "manifest_stage": manifest["stage"],
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf", type=Path, default=OUTPUT_PDF)
    parser.add_argument("--png", type=Path, default=OUTPUT_PNG)
    parser.add_argument("--metadata", type=Path, default=OUTPUT_METADATA)
    args = parser.parse_args(argv)
    result, manifest = preflight_sources()
    figure_data = recompute_figure_data(result, manifest)
    render_figure(figure_data, result, manifest, args.pdf, args.png)
    pdf_qa = verify_vector_pdf(args.pdf)
    metadata = build_metadata(
        figure_data,
        result,
        manifest,
        pdf_path=args.pdf,
        png_path=args.png,
        pdf_qa=pdf_qa,
    )
    write_json(args.metadata, metadata)
    print(f"status={metadata['status']}")
    print(f"side_root_counts={metadata['recomputation']['retained_side_root_counts']}")
    print(f"curve_digest_sha256={figure_data.curve_digest_sha256}")
    print(f"pdf={args.pdf}")
    print(f"png={args.png}")
    print(f"metadata={args.metadata}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
