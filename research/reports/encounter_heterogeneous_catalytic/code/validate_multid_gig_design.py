#!/usr/bin/env python3
"""Construct and validate multi-peak GIG encounter-channel designs in d=1..4.

This is a geometry-to-channel *screening* calculation.  It does not replace a
bounded-domain Doi solve.  For equal diffusivities D1=D2=1/2, an initial gap
ell=1, zero relative drift u=0, centre diffusivity Dc=1/4, and centre drift
speed 0.1, the free-space narrow-patch channel law has

    g_j(t) = Z_j^-1 t^-p exp(-a_j/t-bt),  p=(d+3)/2, b=0.01.

Choosing a_j=b*m_j^2+p*m_j makes the isolated channel mode exactly m_j.
The catalyst centre can then be placed on the drift ray at distance
sqrt(a_j-1/4), provided a_j>=1/4.  Weights proportional to the inverse isolated
peak height make the separated clocks observable without a numerical optimizer.
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import brentq
from scipy.special import gammaln, kve, logsumexp
from vkcore.plotting import enforce_publication_graphics
from vkcore.provenance import build_artifact_manifest, write_manifest

HERE = Path(__file__).resolve()
REPORT = HERE.parents[1]
REPO = HERE.parents[4]
DATA = REPORT / "artifacts" / "data"
FIGURES = REPORT / "artifacts" / "figures"
DATA.mkdir(parents=True, exist_ok=True)
FIGURES.mkdir(parents=True, exist_ok=True)

DIMENSIONS = (1, 2, 3, 4)
MODE_FAMILIES = {2: (1.0, 10.0), 3: (1.0, 10.0, 100.0), 4: (1.0, 10.0, 100.0, 1000.0)}
B = 0.01
RELATIVE_ACTION = 0.25  # ell^2/(4 Dr), ell=Dr=1
GRID_POINTS = 240_000
BLUE = "#2F6B9A"
ORANGE = "#D7812A"
INK = "#20252B"
GREY = "#7A828A"
PALETTE = ("#2F6B9A", "#D7812A", "#8A6F3D", "#8A4F7D")
LARGE_BESSEL_ARGUMENT = 1e5


def _log_scaled_bessel_k(order: float, argument: np.ndarray) -> np.ndarray:
    """Vectorized ``log(exp(x) K_order(x))`` with a large-x branch."""

    x = np.asarray(argument, dtype=float)
    if np.any(x <= 0.0):
        raise ValueError("Bessel arguments must be positive")
    result = np.full_like(x, np.nan)
    large = x >= LARGE_BESSEL_ARGUMENT
    if np.any(large):
        mu = 4.0 * float(order) ** 2
        term = np.ones_like(x[large])
        series = np.ones_like(x[large])
        for index in range(1, 5):
            term *= (mu - float((2 * index - 1) ** 2)) / (
                index * 8.0 * x[large]
            )
            series += term
        if np.any(series <= 0.0):
            raise FloatingPointError("large-argument Bessel asymptotic lost positivity")
        result[large] = 0.5 * (np.log(np.pi) - np.log(2.0 * x[large])) + np.log(
            series
        )
    regular = ~large
    if np.any(regular):
        scaled = np.asarray(kve(order, x[regular]), dtype=float)
        valid = np.isfinite(scaled) & (scaled > 0.0)
        local = np.full_like(scaled, np.nan)
        local[valid] = np.log(scaled[valid])
        result[regular] = local
    return result


def log_normalization(a: np.ndarray, b: float, p: float) -> np.ndarray:
    """Vectorized stable logarithm of the GIG normalizer."""

    action = np.asarray(a, dtype=float)
    if np.any(action <= 0.0):
        raise ValueError("all actions must be positive")
    if b < 0.0:
        raise ValueError("b must be non-negative")
    if b == 0.0:
        if not p > 1.0:
            raise ValueError("b=0 requires p>1 for normalization")
        return (1.0 - p) * np.log(action) + gammaln(p - 1.0)

    argument = 2.0 * np.sqrt(action * b)
    log_scaled = _log_scaled_bessel_k(1.0 - p, argument)
    result = (
        np.log(2.0)
        + ((1.0 - p) / 2.0) * (np.log(action) - np.log(b))
        + log_scaled
        - argument
    )
    failed = ~np.isfinite(result)
    if np.any(failed):
        small = failed & (argument < 1e-6) & (p > 1.0)
        if np.any(small):
            # Leading small-argument limit after scaled kve overflows.
            result[small] = (1.0 - p) * np.log(action[small]) + gammaln(p - 1.0)
        unresolved = ~np.isfinite(result)
        if np.any(unresolved):
            raise FloatingPointError(
                "scaled Bessel evaluation failed outside certified small/large-argument branches"
            )
    return result


def normalization(a: np.ndarray, b: float, p: float) -> np.ndarray:
    """Conventional normalizer when representable; calculations use log Z."""

    return np.exp(log_normalization(a, b, p))


def construction(dimension: int, target_modes: tuple[float, ...]) -> dict[str, np.ndarray | float]:
    p = (dimension + 3.0) / 2.0
    modes = np.asarray(target_modes, dtype=float)
    if np.any(modes <= 0.0):
        raise ValueError("all target modes must be positive")
    a = B * modes**2 + p * modes
    infeasible = a < RELATIVE_ACTION
    if np.any(infeasible):
        failed = ", ".join(f"{value:.12g}" for value in modes[infeasible])
        raise ValueError(
            "target mode has no real catalyst distance: require "
            f"B*m^2+p*m >= {RELATIVE_ACTION:g}; failed modes: {failed}"
        )
    log_z = log_normalization(a, B, p)
    log_isolated_heights = -p * np.log(modes) - a / modes - B * modes - log_z
    log_inverse_heights = -log_isolated_heights
    log_weights = log_inverse_heights - logsumexp(log_inverse_heights)
    weights = np.exp(log_weights)
    z = np.exp(log_z)
    isolated_heights = np.exp(log_isolated_heights)
    distances = np.sqrt(np.maximum(a - RELATIVE_ACTION, 0.0))
    return {
        "p": p,
        "modes": modes,
        "a": a,
        "z": z,
        "log_z": log_z,
        "weights": weights,
        "log_weights": log_weights,
        "distances": distances,
        "isolated_heights": isolated_heights,
        "log_isolated_heights": log_isolated_heights,
    }


def component_arrays(t: np.ndarray, spec: dict[str, Any]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    p = float(spec["p"])
    a = np.asarray(spec["a"], dtype=float)[:, None]
    log_z = np.asarray(spec["log_z"], dtype=float)[:, None]
    tt = np.asarray(t, dtype=float)[None, :]
    log_density = -p * np.log(tt) - a / tt - B * tt - log_z
    density = np.exp(log_density)
    log_first = a / tt**2 - p / tt - B
    log_second = -2.0 * a / tt**3 + p / tt**2
    first = density * log_first
    second = density * (log_first**2 + log_second)
    return density, first, second


def mixture_profile(
    t: np.ndarray, spec: dict[str, Any]
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return log density, f'/f, and f''/f via stable log-sum-exp."""

    values = np.asarray(t, dtype=float)
    if np.any(values <= 0.0):
        raise ValueError("mixture times must be positive")
    p = float(spec["p"])
    action = np.asarray(spec["a"], dtype=float)[:, None]
    log_z = np.asarray(spec["log_z"], dtype=float)[:, None]
    log_weights = np.asarray(spec["log_weights"], dtype=float)[:, None]
    tt = values[None, :]
    log_components = (
        log_weights - p * np.log(tt) - action / tt - B * tt - log_z
    )
    log_total = logsumexp(log_components, axis=0)
    fractions = np.exp(log_components - log_total[None, :])
    log_first = action / tt**2 - p / tt - B
    log_second = -2.0 * action / tt**3 + p / tt**2
    score = np.sum(fractions * log_first, axis=0)
    second_ratio = np.sum(fractions * (log_first**2 + log_second), axis=0)
    return log_total, score, second_ratio


def mixture_scalar(t: float, spec: dict[str, Any], derivative: int) -> float:
    log_total, score, second_ratio = mixture_profile(np.asarray([t]), spec)
    if derivative == 0:
        return float(np.exp(log_total[0]))
    if derivative == 1:
        return float(np.exp(log_total[0]) * score[0])
    if derivative == 2:
        return float(np.exp(log_total[0]) * second_ratio[0])
    raise ValueError("derivative must be 0, 1, or 2")


def isolate_roots(spec: dict[str, Any]) -> list[dict[str, float | str | int]]:
    max_mode = float(np.max(spec["modes"]))
    times = np.geomspace(0.02, 5.0 * max_mode, GRID_POINTS)
    log_total, score, _second_ratio = mixture_profile(times, spec)
    changes = np.flatnonzero(np.signbit(score[:-1]) != np.signbit(score[1:]))
    roots: list[dict[str, float | str | int]] = []
    for root_index, index in enumerate(changes, start=1):
        root = brentq(
            lambda value: float(mixture_profile(np.asarray([value]), spec)[1][0]),
            float(times[index]),
            float(times[index + 1]),
            xtol=2e-14,
            rtol=2e-14,
            maxiter=200,
        )
        root_log_density, root_score, root_second_ratio = mixture_profile(
            np.asarray([root]), spec
        )
        value = float(np.exp(root_log_density[0]))
        second_value = float(value * root_second_ratio[0])
        scaled_residual = abs(float(root_score[0])) * root
        roots.append(
            {
                "root_index": root_index,
                "time": root,
                "kind": "maximum" if second_value < 0 else "minimum",
                "density": value,
                "second_derivative": second_value,
                "scaled_first_derivative_residual": scaled_residual,
            }
        )
    if not (score[0] > 0 and score[-1] < 0):
        raise RuntimeError("the audited interval does not bracket the positive-time tails")
    if np.min(np.abs(score) * times) < 1e-13:
        # Exact roots necessarily make the sampled derivative small.  This
        # diagnostic is deliberately not used as an absence-of-roots proof.
        pass
    return roots


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _plot(all_specs: dict[tuple[int, int], dict[str, Any]], root_rows: list[dict[str, Any]]) -> tuple[Path, Path]:
    fig, axes = plt.subplots(2, 2, figsize=(7.2, 5.6), constrained_layout=True)

    ax = axes[0, 0]
    d3 = all_specs[(3, 4)]
    distances = np.asarray(d3["distances"])
    ax.axhline(0, color=GREY, lw=1.0)
    for index, (distance, mode) in enumerate(zip(distances, d3["modes"], strict=True)):
        ax.scatter(distance, 0, s=120, facecolor=PALETTE[index], edgecolor=INK, zorder=3)
        ax.text(distance, 0.075, rf"$C_{{{index + 1}}}$", ha="center", fontsize=7.5)
    ax.scatter(0, 0, marker="*", s=100, color=INK, zorder=4)
    ax.text(0, -0.11, r"$R_0$", ha="center", fontsize=8)
    ax.text(
        0.48,
        0.82,
        r"target modes: $1,10,100,1000$",
        transform=ax.transAxes,
        ha="center",
        fontsize=7.5,
        color=INK,
    )
    ax.set_xscale("symlog", linthresh=0.5)
    ax.set_xlim(-0.2, distances[-1] * 1.25)
    ax.set_ylim(-0.18, 0.2)
    ax.set_yticks([])
    ax.set_xlabel("catalyst distance (screening units)", fontsize=8)
    ax.spines[["left", "right", "top"]].set_visible(False)
    ax.tick_params(labelsize=7)
    ax.set_title("(a) Designed clocks ($d=3$)", loc="left", fontsize=9, fontweight="bold")

    ax = axes[0, 1]
    offsets = {2: 2.2, 3: 1.1, 4: 0.0}
    for mode_count in (2, 3, 4):
        spec = all_specs[(2, mode_count)]
        times = np.geomspace(0.05, 3000.0, 5000)
        density = np.einsum(
            "i,it->t", np.asarray(spec["weights"]), component_arrays(times, spec)[0]
        )
        scaled = density / np.max(density) + offsets[mode_count]
        ax.plot(times, scaled, lw=1.4, color=PALETTE[mode_count - 2])
        ax.text(0.065, offsets[mode_count] + 0.18, f"{mode_count} channels", color=PALETTE[mode_count - 2], fontsize=7.5)
    ax.set_xscale("log")
    ax.set_xlim(0.05, 3000)
    ax.set_yticks([])
    ax.set_xlabel("reaction time $t$", fontsize=8)
    ax.spines[["left", "right", "top"]].set_visible(False)
    ax.tick_params(labelsize=7)
    ax.set_title(r"(b) Channels $\rightarrow$ modes ($d=2$)", loc="left", fontsize=9, fontweight="bold")

    ax = axes[1, 0]
    spec = all_specs[(3, 4)]
    times = np.geomspace(0.05, 3000.0, 5000)
    components = np.asarray(spec["weights"])[:, None] * component_arrays(times, spec)[0]
    total = components.sum(axis=0)
    ax.plot(times, total / total.max(), color=INK, lw=1.8, label="total")
    for index, component in enumerate(components):
        ax.plot(times, component / total.max(), color=PALETTE[index], lw=1.0, ls="--", label=rf"channel {index + 1}")
    roots = [row for row in root_rows if row["dimension"] == 3 and row["mode_count"] == 4]
    maxima = [row for row in roots if row["kind"] == "maximum"]
    ax.scatter(
        [row["time"] for row in maxima],
        [row["density"] / total.max() for row in maxima],
        facecolor="white",
        edgecolor=INK,
        s=24,
        zorder=4,
    )
    ax.set_xscale("log")
    ax.set_xlim(0.05, 3000)
    ax.set_ylim(bottom=0)
    ax.set_xlabel("reaction time $t$", fontsize=8)
    ax.set_ylabel("scaled density", fontsize=8)
    ax.tick_params(labelsize=7)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, fontsize=6.2, ncol=2, loc="lower left")
    ax.set_title(r"(c) Four-channel decomposition", loc="left", fontsize=9, fontweight="bold")

    ax = axes[1, 1]
    matrix = np.zeros((len(DIMENSIONS), len(MODE_FAMILIES)), dtype=int)
    ratio_matrix = np.zeros_like(matrix, dtype=float)
    for di, dimension in enumerate(DIMENSIONS):
        for mi, mode_count in enumerate(MODE_FAMILIES):
            selected = [row for row in root_rows if row["dimension"] == dimension and row["mode_count"] == mode_count]
            matrix[di, mi] = sum(row["kind"] == "maximum" for row in selected)
            values = [row["density"] for row in selected]
            local_ratios = []
            for k in range(0, len(values) - 2, 2):
                local_ratios.extend((values[k] / values[k + 1], values[k + 2] / values[k + 1]))
            ratio_matrix[di, mi] = min(local_ratios)
    x_edges = np.arange(len(MODE_FAMILIES) + 1, dtype=float) - 0.5
    y_edges = np.arange(len(DIMENSIONS) + 1, dtype=float) - 0.5
    image = ax.pcolormesh(
        x_edges,
        y_edges,
        ratio_matrix,
        cmap="Blues",
        vmin=1.0,
        vmax=float(ratio_matrix.max()),
        shading="flat",
        rasterized=False,
    )
    for di in range(matrix.shape[0]):
        for mi in range(matrix.shape[1]):
            text_color = "white" if ratio_matrix[di, mi] > 3.8 else INK
            ax.text(mi, di, f"{matrix[di, mi]} modes\nR={ratio_matrix[di, mi]:.2f}", ha="center", va="center", fontsize=7, color=text_color)
    ax.set_xticks(range(len(MODE_FAMILIES)), [str(value) for value in MODE_FAMILIES])
    ax.set_yticks(range(len(DIMENSIONS)), [str(value) for value in DIMENSIONS])
    ax.set_ylim(len(DIMENSIONS) - 0.5, -0.5)
    ax.set_xlabel("designed channel count", fontsize=8)
    ax.set_ylabel("physical dimension $d$", fontsize=8)
    ax.tick_params(labelsize=7)
    colorbar = fig.colorbar(image, ax=ax, fraction=0.045, pad=0.03)
    if colorbar.solids is not None:
        colorbar.solids.set_rasterized(False)
    colorbar.set_label("minimum peak/valley ratio", fontsize=8)
    colorbar.ax.tick_params(labelsize=7)
    ax.set_title("(d) Root audit", loc="left", fontsize=9, fontweight="bold")

    fig.suptitle("Constructive multidimensional GIG channel designs", fontsize=11.5, color=INK)
    pdf = FIGURES / "multid_gig_channel_design.pdf"
    png = FIGURES / "multid_gig_channel_design.png"
    enforce_publication_graphics(fig)
    fig.savefig(pdf, bbox_inches="tight")
    fig.savefig(png, dpi=240, bbox_inches="tight")
    plt.close(fig)
    return pdf, png


def main() -> None:
    parameter_rows: list[dict[str, Any]] = []
    root_rows: list[dict[str, Any]] = []
    all_specs: dict[tuple[int, int], dict[str, Any]] = {}
    case_rows: list[dict[str, Any]] = []
    for dimension in DIMENSIONS:
        for mode_count, target_modes in MODE_FAMILIES.items():
            spec = construction(dimension, target_modes)
            all_specs[(dimension, mode_count)] = spec
            roots = isolate_roots(spec)
            expected_kinds = ["maximum" if index % 2 == 0 else "minimum" for index in range(2 * mode_count - 1)]
            if len(roots) != 2 * mode_count - 1 or [row["kind"] for row in roots] != expected_kinds:
                raise RuntimeError(f"d={dimension}, m={mode_count} did not realize the designed modality")
            if max(float(row["scaled_first_derivative_residual"]) for row in roots) > 2e-10:
                raise RuntimeError("root residual gate failed")
            for channel, values in enumerate(
                zip(
                    spec["modes"],
                    spec["a"],
                    spec["distances"],
                    spec["weights"],
                    spec["isolated_heights"],
                    strict=True,
                ),
                start=1,
            ):
                mode, a_value, distance, weight, isolated_height = values
                parameter_rows.append(
                    {
                        "dimension": dimension,
                        "mode_count": mode_count,
                        "channel": channel,
                        "p": spec["p"],
                        "b": B,
                        "target_isolated_mode": mode,
                        "a": a_value,
                        "log_normalization": np.asarray(spec["log_z"])[channel - 1],
                        "catalyst_distance": distance,
                        "mixture_weight": weight,
                        "isolated_peak_height": isolated_height,
                    }
                )
            for row in roots:
                root_rows.append({"dimension": dimension, "mode_count": mode_count, **row})
            values = [float(row["density"]) for row in roots]
            ratios = []
            for index in range(0, len(values) - 2, 2):
                ratios.extend((values[index] / values[index + 1], values[index + 2] / values[index + 1]))
            case_rows.append(
                {
                    "dimension": dimension,
                    "channel_count": mode_count,
                    "isolated_root_count": len(roots),
                    "resolved_mode_count": mode_count,
                    "minimum_peak_to_valley_ratio": min(ratios),
                    "max_scaled_derivative_residual": max(float(row["scaled_first_derivative_residual"]) for row in roots),
                }
            )

    parameters_path = DATA / "multid_gig_design_parameters.csv"
    roots_path = DATA / "multid_gig_design_roots.csv"
    cases_path = DATA / "multid_gig_design_cases.csv"
    _write_csv(parameters_path, parameter_rows)
    _write_csv(roots_path, root_rows)
    _write_csv(cases_path, case_rows)
    summary_path = DATA / "multid_gig_design_summary.json"
    summary = {
        "evidence_level": "free-space narrow-patch GIG screening construction",
        "not_claimed": [
            "bounded-domain PDE theorem",
            "finite-radius centre-patterned continuum fold",
            "physical realization of the designed mixture weights",
            "interval-certified absence of tangential derivative roots",
        ],
        "dimensions": list(DIMENSIONS),
        "channel_counts": list(MODE_FAMILIES),
        "case_count": len(case_rows),
        "all_cases_have_one_detected_mode_per_channel": all(row["resolved_mode_count"] == row["channel_count"] for row in case_rows),
        "minimum_peak_to_valley_ratio": min(row["minimum_peak_to_valley_ratio"] for row in case_rows),
        "maximum_scaled_derivative_residual": max(row["max_scaled_derivative_residual"] for row in case_rows),
        "construction": {
            "D1": 0.5,
            "D2": 0.5,
            "Dr": 1.0,
            "Dc": 0.25,
            "initial_gap": 1.0,
            "relative_drift": 0.0,
            "centre_drift_speed": 0.1,
            "catalytic_coordinate": "diffusivity-weighted eta=D2/(D1+D2), hence C_eta=R",
            "b": B,
            "target_modes": {str(key): list(value) for key, value in MODE_FAMILIES.items()},
            "a_rule": "a_j=b*m_j^2+p*m_j",
            "distance_rule": "|z_j-R0|=sqrt(a_j-1/4)",
            "distance_feasibility": "a_j>=ell^2/(4*Dr), here b*m_j^2+p*m_j>=1/4",
            "minimum_feasible_mode_by_dimension": {
                str(dimension): (
                    -((dimension + 3.0) / 2.0)
                    + np.sqrt(((dimension + 3.0) / 2.0) ** 2 + 4.0 * B * RELATIVE_ACTION)
                )
                / (2.0 * B)
                for dimension in DIMENSIONS
            },
            "weight_rule": "w_j proportional to inverse isolated peak height",
        },
        "cases": case_rows,
    }
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    pdf, png = _plot(all_specs, root_rows)
    manifest = build_artifact_manifest(
        repo_root=REPO,
        generator=str(HERE.relative_to(REPO)),
        command=[sys.executable, str(HERE.relative_to(REPO))],
        model_spec=summary["construction"],
        classifier_spec={
            "analytic_derivatives": True,
            "root_bracketing": "Brent on 240000-point logarithmic sign scan",
            "expected_simple_roots": "2m-1 alternating maxima/minima",
            "claim_boundary": summary["evidence_level"],
        },
        dependencies=[
            REPO / "packages" / "vkcore" / "src" / "vkcore" / "plotting.py",
            REPO / "packages" / "vkcore" / "src" / "vkcore" / "provenance.py",
            REPORT / "notes" / "continuum_multid_theory.md",
            REPORT / "notes" / "multid_gig_channel_design.md",
        ],
        outputs=[parameters_path, roots_path, cases_path, summary_path, pdf, png],
        horizon={"time_min": 0.02, "time_max_factor_over_last_mode": 5.0, "grid_points": GRID_POINTS},
    )
    write_manifest(DATA / "multid_gig_design.manifest.json", manifest)


if __name__ == "__main__":
    main()
