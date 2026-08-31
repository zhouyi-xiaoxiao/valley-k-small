#!/usr/bin/env python3
"""Build the validated heterogeneous catalytic encounter research report."""

from __future__ import annotations

import csv
import json
from dataclasses import asdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import expm_multiply
from vkcore.encounter import (
    reflecting_biased_ctmc_generator,
    reflecting_biased_discrete_kernel,
)
from vkcore.fpt import DiscreteFPTResult, propagate_discrete_fpt
from vkcore.morphology import (
    MorphologyConfig,
    MorphologyResult,
    analyze_fpt_morphology,
    poissonize_pmf,
)
from vkcore.plotting import enforce_publication_graphics
from vkcore.provenance import build_artifact_manifest, write_manifest

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[2]
DATA = ROOT / "artifacts" / "data"
FIG = ROOT / "artifacts" / "figures"
for directory in (DATA, FIG):
    directory.mkdir(parents=True, exist_ok=True)

Q1 = 0.7
Q2 = 0.2
BIAS1 = 0.3
BIAS2 = 0.3
RHO = (0.6, 0.6)
KAPPA = tuple(float(-np.log(1.0 - value)) for value in RHO)
SIZES = (31, 41, 61, 81)
LEGACY_FIGURE_STEMS = (
    "catalytic_encounter_family",
    "catalytic_encounter_clock_check",
    "catalytic_encounter_robustness",
)

FULL_MORPHOLOGY = MorphologyConfig(
    smoothing_windows=(1, 3, 5, 9, 15),
    bin_widths=(1, 2, 4, 8, 16),
    bin_offsets=(),
    min_peak_height_rel=0.03,
    min_prominence_rel=0.015,
    min_lobe_mass_rel=0.025,
    min_r_peak=0.05,
    max_r_valley=0.80,
    min_peak_separation_widths=1.0,
    expected_total_mass=1.0,
    mass_tolerance=2e-11,
)

PERTURB_MORPHOLOGY = MorphologyConfig(
    smoothing_windows=(1, 5, 15),
    bin_widths=(1, 4, 16),
    bin_offsets=(),
    min_peak_height_rel=0.03,
    min_prominence_rel=0.015,
    min_lobe_mass_rel=0.025,
    min_r_peak=0.05,
    max_r_valley=0.80,
    min_peak_separation_widths=1.0,
    expected_total_mass=1.0,
    mass_tolerance=2e-11,
)


def geometry(size: int) -> tuple[tuple[int, int], tuple[int, int]]:
    near = (size - 1) // 2 - 2
    return (near - 10, near + 2), (near, size - 1)


def write_current_legacy_manifest(
    *, generator: Path | None = None, command: list[str] | None = None
) -> Path:
    """Hash the current report outputs without regenerating numerical data."""

    generator_path = Path(__file__) if generator is None else generator
    generator_path = generator_path.resolve()
    summary = json.loads((DATA / "summary.json").read_text(encoding="utf-8"))
    dependencies = [
        REPO / "packages" / "vkcore" / "src" / "vkcore" / "encounter.py",
        REPO / "packages" / "vkcore" / "src" / "vkcore" / "fpt.py",
        REPO / "packages" / "vkcore" / "src" / "vkcore" / "morphology.py",
        REPO / "packages" / "vkcore" / "src" / "vkcore" / "plotting.py",
        REPO / "packages" / "vkcore" / "src" / "vkcore" / "provenance.py",
    ]
    build_source = Path(__file__).resolve()
    if generator_path != build_source:
        dependencies.append(build_source)
    relative_generator = str(generator_path.relative_to(REPO))
    manifest = build_artifact_manifest(
        repo_root=REPO,
        generator=relative_generator,
        command=command or ["python", relative_generator],
        model_spec=summary["model"],
        classifier_spec=asdict(FULL_MORPHOLOGY),
        inputs=[generator_path, ROOT / "notes" / "theory.md"],
        dependencies=dependencies,
        outputs=[
            DATA / "summary.json",
            DATA / "series.npz",
            DATA / "finite_size.csv",
            DATA / "perturbation_audit.csv",
            DATA / "continuous_time.csv",
            *[
                FIG / f"{stem}.{suffix}"
                for stem in LEGACY_FIGURE_STEMS
                for suffix in ("pdf", "png")
            ],
        ],
        horizon={
            "discrete_tail_tolerance": 1e-12,
            "ctmc_shape_tmax": 1200.0,
            "ctmc_tail_check_time": 5000.0,
        },
    )
    path = ROOT / "artifacts" / "manifest.json"
    write_manifest(path, manifest)
    return path


def discrete_case(
    size: int,
    *,
    q1: float = Q1,
    q2: float = Q2,
    bias1: float = BIAS1,
    bias2: float = BIAS2,
    rho: tuple[float, float] = RHO,
    tail_tolerance: float = 1e-12,
) -> tuple[DiscreteFPTResult, MorphologyResult, tuple[int, int], tuple[int, int]]:
    start, sites = geometry(size)
    p1 = reflecting_biased_discrete_kernel(size, q1, bias1)
    p2 = reflecting_biased_discrete_kernel(size, q2, bias2)
    # Pin the sparse-matrix return contract across SciPy's spmatrix-to-sparray
    # migration; downstream column slicing intentionally uses ``.toarray()``.
    free = sparse.kron(
        sparse.csc_matrix(p1),
        sparse.csc_matrix(p2),
        format="csc",
    )
    catalytic_indices = [site * size + site for site in sites]
    survival_factors = np.ones(size * size)
    survival_factors[catalytic_indices] = 1.0 - np.asarray(rho)
    transient = free @ sparse.diags(survival_factors, format="csc")
    channels = np.vstack(
        [
            free[:, index].toarray().reshape(-1) * probability
            for index, probability in zip(catalytic_indices, rho, strict=True)
        ]
    )
    initial = np.zeros(size * size)
    initial[start[0] * size + start[1]] = 1.0
    result = propagate_discrete_fpt(
        transient,
        channels,
        initial,
        max_steps=12_000,
        tail_tolerance=tail_tolerance,
    )
    config = FULL_MORPHOLOGY if tail_tolerance <= 1e-12 else PERTURB_MORPHOLOGY
    morphology = analyze_fpt_morphology(
        result.total_flux,
        times=result.times,
        config=config,
        tail_mass_upper_bound=result.tail_mass,
    )
    return result, morphology, start, sites


def morphology_row(size: int, result: DiscreteFPTResult, morphology: MorphologyResult) -> dict:
    valley = morphology.qualifying_valleys[0]
    return {
        "L": size,
        "classification": morphology.classification,
        "peak_1": morphology.modal_peaks[0].time,
        "peak_2": morphology.modal_peaks[1].time,
        "peak_1_persistence": morphology.modal_peaks[0].persistence,
        "peak_2_persistence": morphology.modal_peaks[1].persistence,
        "valley_time": valley.valley_time,
        "R_peak": valley.r_peak,
        "R_valley": valley.r_valley,
        "separation_widths": valley.separation_widths,
        "channel_1_weight": result.channel_weights_at_horizon[0],
        "channel_2_weight": result.channel_weights_at_horizon[1],
        "tail_mass": result.tail_mass,
        "steps": int(result.times[-1]),
        "mass_balance_error": result.mass_balance_error,
        "scale_views": len(morphology.scale_views),
        "all_views_have_two_peaks": all(
            len(view.accepted_peak_indices) >= 2 for view in morphology.scale_views
        ),
    }


def continuous_case(size: int, t_max: float = 1200.0, dt: float = 0.5) -> dict:
    start, sites = geometry(size)
    g1 = sparse.csr_matrix(reflecting_biased_ctmc_generator(size, Q1, BIAS1))
    g2 = sparse.csr_matrix(reflecting_biased_ctmc_generator(size, Q2, BIAS2))
    generator = (
        sparse.kron(g1, sparse.eye(size), format="csr")
        + sparse.kron(sparse.eye(size), g2, format="csr")
    ).tolil()
    channel_rates = np.zeros((size * size, 2))
    for channel, (site, rate) in enumerate(zip(sites, KAPPA, strict=True)):
        index = site * size + site
        generator[index, index] -= rate
        channel_rates[index, channel] = rate
    generator = generator.tocsr()
    initial = np.zeros(size * size)
    initial[start[0] * size + start[1]] = 1.0
    times = np.arange(0.0, t_max + 0.5 * dt, dt)
    states = expm_multiply(
        generator.T,
        initial,
        start=0.0,
        stop=t_max,
        num=times.size,
        endpoint=True,
    )
    density_channels = np.einsum("ti,ic->tc", states, channel_rates)
    density = density_channels.sum(axis=1)
    survival = states.sum(axis=1)
    probability_mass = density * dt
    probability_mass[[0, -1]] *= 0.5
    quadrature_error = abs(float(probability_mass.sum() + survival[-1] - 1.0))
    config = MorphologyConfig(
        smoothing_windows=(1, 3, 5, 9),
        bin_widths=(1, 2, 4, 8),
        bin_offsets=(),
        min_peak_separation_widths=1.0,
        expected_total_mass=1.0,
        mass_tolerance=max(2e-8, 1.1 * quadrature_error),
    )
    morphology = analyze_fpt_morphology(
        probability_mass,
        times=times,
        config=config,
        tail_mass_upper_bound=float(survival[-1] + quadrature_error),
    )
    far_tail = float(expm_multiply(generator.T * 5000.0, initial).sum())
    valley = morphology.qualifying_valleys[0]
    return {
        "L": size,
        "times": times,
        "density": density,
        "channel_density": density_channels,
        "survival_at_tmax": float(survival[-1]),
        "tail_at_5000": far_tail,
        "quadrature_error": quadrature_error,
        "classification": morphology.classification,
        "peak_1": morphology.modal_peaks[0].time,
        "peak_2": morphology.modal_peaks[1].time,
        "R_peak": valley.r_peak,
        "R_valley": valley.r_valley,
        "separation_widths": valley.separation_widths,
    }


def write_csv(path: Path, rows: list[dict], fieldnames: list[str] | None = None) -> None:
    columns = fieldnames or list(rows[0])
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows({key: row[key] for key in columns} for row in rows)


def json_default(value):
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, np.ndarray):
        return value.tolist()
    raise TypeError(f"not JSON serializable: {type(value).__name__}")


def linear_fit(x: np.ndarray, y: np.ndarray) -> dict[str, float]:
    slope, intercept = np.polyfit(x, y, 1)
    fitted = slope * x + intercept
    denominator = float(np.sum((y - np.mean(y)) ** 2))
    r_squared = 1.0 - float(np.sum((y - fitted) ** 2)) / max(denominator, 1e-300)
    return {"slope": float(slope), "intercept": float(intercept), "r_squared": r_squared}


def main() -> None:
    finite_rows: list[dict] = []
    discrete_results: dict[int, DiscreteFPTResult] = {}
    geometries: dict[int, tuple[tuple[int, int], tuple[int, int]]] = {}
    for size in SIZES:
        result, morphology, start, sites = discrete_case(size)
        if morphology.classification != "bimodal":
            raise RuntimeError(f"L={size} failed the canonical bimodality gate")
        finite_rows.append(morphology_row(size, result, morphology))
        discrete_results[size] = result
        geometries[size] = (start, sites)
    write_csv(DATA / "finite_size.csv", finite_rows)
    fit_sizes = np.asarray([row["L"] for row in finite_rows], dtype=float)
    scaling_fits = {
        "late_peak_vs_L": linear_fit(
            fit_sizes, np.asarray([row["peak_2"] for row in finite_rows], dtype=float)
        ),
        "log_R_valley_vs_L": linear_fit(
            fit_sizes,
            np.log(np.asarray([row["R_valley"] for row in finite_rows], dtype=float)),
        ),
        "separation_vs_sqrt_L": linear_fit(
            np.sqrt(fit_sizes),
            np.asarray([row["separation_widths"] for row in finite_rows], dtype=float),
        ),
    }

    # Fixed-seed local robustness audit at L=41.
    rng = np.random.default_rng(20260710)
    perturbation_rows: list[dict] = []
    for sample in range(40):
        parameters = {
            "q1": float(rng.uniform(0.63, 0.77)),
            "q2": float(rng.uniform(0.16, 0.24)),
            "bias1": float(rng.uniform(0.25, 0.35)),
            "bias2": float(rng.uniform(0.25, 0.35)),
            "rho": (float(rng.uniform(0.5, 0.7)), float(rng.uniform(0.5, 0.7))),
        }
        result, morphology, _, _ = discrete_case(
            41, **parameters, tail_tolerance=1e-11
        )
        valley = morphology.valleys[0] if morphology.valleys else None
        perturbation_rows.append(
            {
                "sample": sample,
                "q1": parameters["q1"],
                "q2": parameters["q2"],
                "bias1": parameters["bias1"],
                "bias2": parameters["bias2"],
                "rho1": parameters["rho"][0],
                "rho2": parameters["rho"][1],
                "classification": morphology.classification,
                "R_peak": "" if valley is None else valley.r_peak,
                "R_valley": "" if valley is None else valley.r_valley,
                "separation_widths": "" if valley is None else valley.separation_widths,
                "tail_mass": result.tail_mass,
            }
        )
    write_csv(DATA / "perturbation_audit.csv", perturbation_rows)

    continuous_rows = [continuous_case(size) for size in (31, 41, 61)]
    write_csv(
        DATA / "continuous_time.csv",
        continuous_rows,
        [
            "L",
            "classification",
            "peak_1",
            "peak_2",
            "R_peak",
            "R_valley",
            "separation_widths",
            "survival_at_tmax",
            "tail_at_5000",
            "quadrature_error",
        ],
    )

    # Discrete family figure.
    representative_size = 41
    representative = discrete_results[representative_size]
    start, sites = geometries[representative_size]
    fig, axes = plt.subplots(2, 2, figsize=(11.0, 7.8))
    ax = axes[0, 0]
    ax.plot([0, representative_size - 1], [0, 0], color="0.2", lw=2)
    ax.scatter(start, [0, 0], marker="o", s=90, c=["#2166ac", "#67a9cf"], zorder=3)
    ax.scatter(sites, [0, 0], marker="*", s=180, c=["#d73027", "#7f0000"], zorder=4)
    ax.annotate("fast walker", (start[0], 0.035), ha="center", fontsize=8)
    ax.annotate("slow walker", (start[1], -0.045), ha="center", fontsize=8)
    ax.annotate("near patch", (sites[0], 0.065), ha="center", fontsize=8)
    ax.annotate("boundary patch", (sites[1], 0.095), ha="right", fontsize=8)
    ax.arrow(2, -0.10, 12, 0, width=0.003, head_width=0.025, color="#2166ac")
    ax.arrow(16, -0.10, 7, 0, width=0.003, head_width=0.025, color="#67a9cf")
    ax.set_xlim(-1, representative_size)
    ax.set_ylim(-0.16, 0.13)
    ax.set_yticks([])
    ax.set_xlabel("physical site")
    ax.set_title("(a) chase and boundary-return channels")

    ax = axes[0, 1]
    visible = representative.times <= 900
    ax.plot(representative.times[visible], representative.total_flux[visible], "k", lw=2, label="total")
    ax.plot(representative.times[visible], representative.channel_flux[0, visible], color="#d73027", label="near")
    ax.plot(representative.times[visible], representative.channel_flux[1, visible], color="#7f0000", label="boundary")
    ax.set_xlabel("time step")
    ax.set_ylabel("reaction probability")
    ax.set_title(r"(b) site-resolved channels ($L=41$)")
    ax.legend(frameon=False, fontsize=8)

    ax = axes[1, 0]
    for row in finite_rows:
        result = discrete_results[row["L"]]
        visible = result.times <= 850
        ax.plot(result.times[visible], result.total_flux[visible], lw=1.5, label=f"L={row['L']}")
    ax.set_xlabel("time step")
    ax.set_ylabel("reaction probability")
    ax.set_title("(c) domain-size continuation")
    ax.legend(frameon=False, fontsize=8)

    ax = axes[1, 1]
    sizes = np.asarray([row["L"] for row in finite_rows])
    separation = np.asarray([row["separation_widths"] for row in finite_rows])
    valley = np.asarray([row["R_valley"] for row in finite_rows])
    ax.plot(sizes, separation, "o-", color="#2166ac", label="separation / characteristic width")
    ax.set_xlabel("L")
    ax.set_ylabel("width-normalized separation", color="#2166ac")
    ax.tick_params(axis="y", labelcolor="#2166ac")
    twin = ax.twinx()
    twin.semilogy(sizes, valley, "s--", color="#b2182b", label="valley / minor peak")
    twin.set_ylabel("valley / minor peak", color="#b2182b")
    twin.tick_params(axis="y", labelcolor="#b2182b")
    ax.set_title(r"(d) mode resolution versus $L$")
    enforce_publication_graphics(fig)
    fig.tight_layout()
    for suffix in ("pdf", "png"):
        fig.savefig(FIG / f"catalytic_encounter_family.{suffix}", dpi=300)
    plt.close(fig)

    # Clock/parity cross-check at L=31.
    discrete = discrete_results[31]
    poissonized = poissonize_pmf(
        discrete.total_flux,
        rate=1.0,
        grid_points=4097,
        t_max=1200.0,
    )
    continuous = continuous_rows[0]
    fig, ax = plt.subplots(figsize=(8.0, 4.8))
    mask_d = discrete.times <= 700
    ax.plot(discrete.times[mask_d], discrete.total_flux[mask_d], color="0.55", lw=1.0, label="discrete raw")
    mask_p = poissonized.times <= 700
    ax.plot(poissonized.times[mask_p], poissonized.density[mask_p], color="#2166ac", lw=2, label="Poissonized discrete")
    mask_c = continuous["times"] <= 700
    ax.plot(continuous["times"][mask_c], continuous["density"][mask_c], color="#b2182b", lw=1.6, ls="--", label="CTMC")
    ax.set_xlabel("time")
    ax.set_ylabel("reaction-time density")
    ax.set_title("Clock check: the resolved double peak is not a parity artifact")
    ax.legend(frameon=False)
    ax.grid(alpha=0.2)
    enforce_publication_graphics(fig)
    fig.tight_layout()
    for suffix in ("pdf", "png"):
        fig.savefig(FIG / f"catalytic_encounter_clock_check.{suffix}", dpi=300)
    plt.close(fig)

    # Local robustness basin.
    accepted = [row for row in perturbation_rows if row["classification"] == "bimodal"]
    rejected = [row for row in perturbation_rows if row["classification"] != "bimodal"]
    rejected_with_valley = [row for row in rejected if row["R_valley"] != ""]
    fig, ax = plt.subplots(figsize=(7.0, 5.0))
    scatter = ax.scatter(
        [row["separation_widths"] for row in accepted],
        [row["R_valley"] for row in accepted],
        c=[row["R_peak"] for row in accepted],
        cmap="viridis",
        s=44,
        edgecolor="white",
        linewidth=0.9,
        label="canonical bimodal",
    )
    if rejected_with_valley:
        ax.scatter(
            [row["separation_widths"] for row in rejected_with_valley],
            [row["R_valley"] for row in rejected_with_valley],
            marker="x",
            c="#b2182b",
            s=55,
            label="shoulder at boundary of audit box",
        )
    ax.axvline(1.0, color="0.4", ls=":")
    ax.axhline(0.8, color="0.4", ls=":")
    ax.set_xlabel("width-normalized peak separation")
    ax.set_ylabel("valley / minor peak")
    ax.set_title(f"Local perturbation audit: {len(accepted)}/40 remain bimodal")
    ax.legend(frameon=False, fontsize=8)
    colorbar = fig.colorbar(scatter, ax=ax)
    colorbar.set_label("minor / major peak")
    enforce_publication_graphics(fig)
    fig.tight_layout()
    for suffix in ("pdf", "png"):
        fig.savefig(FIG / f"catalytic_encounter_robustness.{suffix}", dpi=300)
    plt.close(fig)

    np.savez_compressed(
        DATA / "series.npz",
        **{
            f"L{size}_{name}": array
            for size, result in discrete_results.items()
            for name, array in (
                ("times", result.times),
                ("total", result.total_flux),
                ("near", result.channel_flux[0]),
                ("boundary", result.channel_flux[1]),
                ("survival", result.survival),
            )
        },
    )

    summary = {
        "model": {
            "q": [Q1, Q2],
            "right_bias": [BIAS1, BIAS2],
            "rho": RHO,
            "kappa": KAPPA,
            "boundary": "reflect_attempted_step_stay",
            "reaction_order": "arrival_then_react",
            "geometry_rule": "near=(L-1)//2-2; start=(near-10,near+2); far=L-1",
        },
        "finite_size": finite_rows,
        "scaling_fits_descriptive_four_sizes": scaling_fits,
        "continuous_time": [
            {key: value for key, value in row.items() if not isinstance(value, np.ndarray)}
            for row in continuous_rows
        ],
        "perturbation": {
            "seed": 20260710,
            "samples": 40,
            "bimodal": len(accepted),
            "shoulder_or_unimodal": len(rejected),
            "box": {
                "q1": [0.63, 0.77],
                "q2": [0.16, 0.24],
                "bias1": [0.25, 0.35],
                "bias2": [0.25, 0.35],
                "rho1": [0.5, 0.7],
                "rho2": [0.5, 0.7],
            },
        },
        "poissonization": {
            "mass_error": poissonized.mass_error,
            "quality_ok": poissonized.quality_ok,
        },
    }
    (DATA / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True, default=json_default) + "\n",
        encoding="utf-8",
    )
    write_current_legacy_manifest()
    print(json.dumps(summary, indent=2, default=json_default))


if __name__ == "__main__":
    main()
