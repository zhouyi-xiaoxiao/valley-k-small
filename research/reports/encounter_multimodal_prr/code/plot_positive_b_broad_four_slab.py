#!/usr/bin/env python3
"""Plot the pinned positive-B broad-four-slab fixed-control evidence.

This renderer is deliberately downstream-only.  It reads exactly the canonical
result, reproducibility record, and independent-audit JSON; verifies their hard
pins and bounded claim contract; and plots only values already saved there.  It
does not import or call the producer, a semigroup, a finite-volume solver, or the
canonical auditor.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import os
import re
import stat
import tempfile
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

import matplotlib

matplotlib.use("Agg", force=True)
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402

HERE = Path(__file__).resolve()
REPORT = HERE.parents[1]
DATA = REPORT / "artifacts" / "data"
FIGURES = REPORT / "artifacts" / "figures"

RESULT = DATA / "positive_b_broad_four_slab_result.json"
REPRODUCIBILITY = DATA / "positive_b_broad_four_slab_reproducibility.json"
INDEPENDENT_AUDIT = DATA / "positive_b_broad_four_slab_independent_audit.json"
OUTPUT_PDF = FIGURES / "positive_b_broad_four_slab.pdf"
OUTPUT_METADATA = FIGURES / "positive_b_broad_four_slab_metadata.json"
TEST_SOURCE = REPORT / "code" / "test_plot_positive_b_broad_four_slab.py"

EXPECTED_RESULT_SHA256 = "51e8eb4bdb652124865d0c39e6f36b99d13ed61578b161e0f75b142cada49401"
EXPECTED_REPRODUCIBILITY_SHA256 = (
    "6c0eccaae09ef95923843ddd7a141a27311e1575ee68d3301b4757b785ee9890"
)
EXPECTED_INDEPENDENT_AUDIT_SHA256 = (
    "60c541a6f0decd5431cefa5c203311176e61006586ce69043d5fcf5380ed517d"
)
EXPECTED_MANIFEST_SHA256 = "955e59bf333b5fd70e415a53dc26becae9c7a34c5d40f1230c96b1dab8f5677c"

EXPECTED_RESULT_STATUS = "PASS_RESULT_INFORMED_POSITIVE_B_EVENT_MASS_SHAPE_CONFIRMATION"
EXPECTED_AUDIT_STATUS = "PASS_INDEPENDENT_RECONSTRUCTION"
EXPECTED_EVIDENCE_TIMING = "RESULT_INFORMED_FIXED_CONTROL_WITH_HELDOUT_FINE_MESHES"
EXPECTED_CLAIM_SCOPE = (
    "One result-informed broad four-slab geometry with fixed absolute weights and fixed "
    "B=0.01, tested by a matrix-free killed-Doi finite-volume semigroup on two held-out "
    "odd cubic meshes in one fixed reflecting box."
)
EXPECTED_LIMITATIONS = (
    "result-informed fixed control and selected budget",
    "two fixed-box finite-volume meshes, not a PDE or unbounded-domain proof",
    "same solver family on both meshes, not independent-solver verification",
    "floating-point sign-screen and root refinement, not interval certification",
    "no physical d=3 or project/publication gate",
)
EXPECTED_MESHES = (113, 129)
EXPECTED_TOPOLOGY = ("maximum", "minimum", "maximum", "minimum", "maximum")
EXPECTED_WEIGHTS = (
    0.28,
    0.27736690132708747,
    0.0857172266153233,
    0.3569158720575891,
)
EVENT_MASS_FLOOR = 0.005
POSITIVE_BUDGET = 0.01
FINAL_TIME = 100.0
REQUIRED_FALSE_FLAGS = {
    "continuum_interval_verified": False,
    "independent_solver_verified": False,
    "preregistered_discovery": False,
    "project_gate_passed": False,
    "unbounded_domain_FV_limit_verified": False,
}
EXPECTED_AUDIT_CLAIM_BOUNDARY = {
    "allocation_cusp_verified": False,
    "continuum_interval_verified": False,
    "fixed_box_two_mesh_semidiscrete_point_only": True,
    "independent_process_execution_observed_by_auditor": False,
    "independent_solver_verified": False,
    "preregistered_discovery": False,
    "project_gate_passed": False,
    "two_process_evidence_record_consistent": True,
    "unbounded_domain_FV_limit_verified": False,
}
FORBIDDEN_RESULT_KEYS = ("physical_d3_verified", "publication_gate_passed")
METADATA_CLAIM_FLAGS = {
    "allocation_cusp_verified": False,
    "continuum_interval_verified": False,
    "independent_solver_verified": False,
    "physical_d3_verified": False,
    "preregistered_discovery": False,
    "project_gate_passed": False,
    "publication_gate_passed": False,
    "unbounded_domain_FV_limit_verified": False,
}
METADATA_SCOPE_CONSTRAINTS = {
    "finite_gate_time_max": FINAL_TIME,
    "finite_time_window_only": True,
    "fixed_box_two_mesh_semidiscrete_point_only": True,
    "heldout_odd_meshes": list(EXPECTED_MESHES),
    "positive_budget": POSITIVE_BUDGET,
    "same_solver_family_only": True,
    "saved_trace_time_max": 35.0,
    "weights_refit": False,
}

BLUE = "#356A9A"
GOLD = "#C58A24"
INK = "#22252A"
MID_GREY = "#666B73"
LIGHT_GREY = "#E1E4E8"


@dataclass(frozen=True)
class RootPoint:
    """One saved stationary root used by the figure."""

    time: float
    density: float
    topology: str


@dataclass(frozen=True)
class MeshFigureData:
    """Saved trace, roots, and event masses for one held-out mesh."""

    mesh: int
    trace_times: tuple[float, ...]
    trace_density: tuple[float, ...]
    roots: tuple[RootPoint, ...]
    basin_masses: tuple[float, float, float]


@dataclass(frozen=True)
class FigureData:
    """Validated plotting data from the three pinned canonical JSON files."""

    meshes: tuple[MeshFigureData, MeshFigureData]


@dataclass(frozen=True)
class BuildReceipt:
    """Deterministic paired-output details returned after atomic publication."""

    output: Path
    sha256: str
    byte_count: int
    metadata: Path
    metadata_sha256: str
    metadata_byte_count: int
    pdf_qa: dict[str, int]


ReplaceFunction = Callable[[str | os.PathLike[str], str | os.PathLike[str]], None]
DirectorySyncFunction = Callable[[Path], None]


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def _reject_json_constant(token: str) -> None:
    raise ValueError(f"nonfinite JSON constant is forbidden: {token}")


def _unique_json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise ValueError(f"duplicate JSON key is forbidden: {key}")
        value[key] = item
    return value


def _read_regular_file(path: Path, label: str) -> bytes:
    flags = os.O_RDONLY
    if hasattr(os, "O_CLOEXEC"):
        flags |= os.O_CLOEXEC
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(path, flags)
    except OSError as error:
        raise ValueError(f"cannot open pinned {label} as a regular nonsymlink file") from error
    try:
        file_stat = os.fstat(descriptor)
        if not stat.S_ISREG(file_stat.st_mode):
            raise ValueError(f"pinned {label} must be a regular file")
        with os.fdopen(descriptor, "rb", closefd=True) as handle:
            descriptor = -1
            return handle.read()
    finally:
        if descriptor >= 0:
            os.close(descriptor)


def _read_pinned_json(path: Path, expected_sha256: str, label: str) -> dict[str, Any]:
    raw = _read_regular_file(path, label)
    observed = sha256_bytes(raw)
    if observed != expected_sha256:
        raise ValueError(
            f"pinned {label} hash mismatch: expected {expected_sha256}, observed {observed}"
        )
    try:
        payload = json.loads(
            raw.decode("utf-8"),
            parse_constant=_reject_json_constant,
            object_pairs_hook=_unique_json_object,
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError(f"pinned {label} is not strict UTF-8 JSON") from error
    if not isinstance(payload, dict):
        raise ValueError(f"pinned {label} JSON must have an object root")
    return payload


def read_pinned_payloads(
    *,
    result_path: Path = RESULT,
    reproducibility_path: Path = REPRODUCIBILITY,
    audit_path: Path = INDEPENDENT_AUDIT,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    """Read only the three hard-pinned public canonical JSON files."""

    result = _read_pinned_json(result_path, EXPECTED_RESULT_SHA256, "result")
    reproducibility = _read_pinned_json(
        reproducibility_path,
        EXPECTED_REPRODUCIBILITY_SHA256,
        "reproducibility evidence",
    )
    audit = _read_pinned_json(
        audit_path,
        EXPECTED_INDEPENDENT_AUDIT_SHA256,
        "independent audit",
    )
    return result, reproducibility, audit


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be an object")
    return value


def _sequence(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise ValueError(f"{label} must be an array")
    return value


def _finite_float(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label} must be numeric")
    converted = float(value)
    if not math.isfinite(converted):
        raise ValueError(f"{label} must be finite")
    return converted


def _require_close(observed: float, expected: float, label: str, *, atol: float = 5e-15) -> None:
    if not math.isclose(observed, expected, rel_tol=0.0, abs_tol=atol):
        raise ValueError(f"{label} mismatch: expected {expected}, observed {observed}")


def _validate_chain(
    result: dict[str, Any],
    reproducibility: dict[str, Any],
    audit: dict[str, Any],
) -> None:
    for label, payload in (
        ("result", result),
        ("reproducibility evidence", reproducibility),
        ("independent audit", audit),
    ):
        _require(
            payload.get("manifest_sha256") == EXPECTED_MANIFEST_SHA256,
            f"{label} manifest SHA does not match the frozen manifest pin",
        )

    _require(
        reproducibility.get("canonical_result_sha256") == EXPECTED_RESULT_SHA256,
        "reproducibility evidence canonical-result hash chain is broken",
    )
    _require(
        reproducibility.get("replica_result_sha256")
        == [EXPECTED_RESULT_SHA256, EXPECTED_RESULT_SHA256],
        "reproducibility evidence replica-result hash chain is broken",
    )
    _require(
        audit.get("canonical_result_sha256") == EXPECTED_RESULT_SHA256,
        "independent-audit canonical-result hash chain is broken",
    )
    _require(
        audit.get("reproducibility_evidence_sha256") == EXPECTED_REPRODUCIBILITY_SHA256,
        "independent-audit reproducibility-evidence hash chain is broken",
    )

    _require(reproducibility.get("all_gates_passed") is True, "evidence gate must pass")
    _require(reproducibility.get("byte_identical") is True, "replica bytes must be identical")
    _require(
        reproducibility.get("canonical_promotion_after_comparison") is True,
        "canonical promotion must follow byte comparison",
    )
    _require(
        reproducibility.get("independent_process_count") == 2,
        "evidence must record exactly two processes",
    )
    _require(
        reproducibility.get("execution_order") == "sequential",
        "evidence execution order must remain sequential",
    )
    _require(
        reproducibility.get("replica_exit_codes") == [0, 0],
        "both recorded replica exit codes must remain zero",
    )
    _require(
        reproducibility.get("result_status") == EXPECTED_RESULT_STATUS,
        "evidence result status does not match the bounded result",
    )

    _require(audit.get("status") == EXPECTED_AUDIT_STATUS, "independent audit did not pass")
    _require(audit.get("scientific_result_passed") is True, "audit scientific PASS is absent")
    _require(
        audit.get("claim_boundary") == EXPECTED_AUDIT_CLAIM_BOUNDARY,
        "independent-audit claim boundary changed",
    )


def _validate_result_claims(result: dict[str, Any]) -> None:
    _require(result.get("status") == EXPECTED_RESULT_STATUS, "canonical result status changed")
    _require(
        result.get("evidence_timing") == EXPECTED_EVIDENCE_TIMING,
        "canonical evidence timing changed",
    )
    _require(result.get("claim_scope") == EXPECTED_CLAIM_SCOPE, "canonical claim scope changed")
    _require(
        tuple(_sequence(result.get("limitations"), "canonical limitations"))
        == EXPECTED_LIMITATIONS,
        "canonical limitations changed",
    )
    _require(result.get("all_gates_passed") is True, "canonical aggregate gate did not pass")
    _require(
        result.get("positive_B_event_mass_shape_confirmation") is True,
        "bounded positive-B shape confirmation did not pass",
    )
    _require(
        result.get("required_claim_flags") == REQUIRED_FALSE_FLAGS,
        "canonical required negative claim flags changed",
    )
    for name in REQUIRED_FALSE_FLAGS:
        _require(result.get(name) is False, f"negative claim flag {name} must remain false")
    for name in FORBIDDEN_RESULT_KEYS:
        _require(name not in result, f"forbidden promotion key {name} must remain absent")

    _require(result.get("weights_refit") is False, "weights_refit must remain false")
    budget = _finite_float(result.get("positive_budget"), "positive budget")
    _require_close(budget, POSITIVE_BUDGET, "positive budget", atol=0.0)
    weights = tuple(
        _finite_float(value, f"fixed weight {index}")
        for index, value in enumerate(
            _sequence(result.get("fixed_absolute_weights"), "fixed absolute weights")
        )
    )
    _require(weights == EXPECTED_WEIGHTS, "fixed control weights changed")
    _require_close(sum(weights), 1.0, "fixed control weight sum", atol=2e-15)


def _validate_mesh_row(row: dict[str, Any], expected_mesh: int) -> MeshFigureData:
    mesh = _sequence(row.get("mesh"), f"mesh {expected_mesh} identity")
    _require(mesh == [expected_mesh] * 3, f"expected cubic mesh N={expected_mesh}")
    _require(row.get("all_mesh_gates_passed") is True, f"mesh N={expected_mesh} gates failed")
    gates = _mapping(row.get("gates"), f"mesh N={expected_mesh} gates")
    for gate in ("five_alternating_simple_roots", "event_basin_masses"):
        _require(gates.get(gate) is True, f"mesh N={expected_mesh} gate {gate} failed")

    scan = _mapping(row.get("scan"), f"mesh N={expected_mesh} scan")
    trace = _sequence(scan.get("saved_trace"), f"mesh N={expected_mesh} saved trace")
    _require(len(trace) == 351, f"mesh N={expected_mesh} saved trace must have 351 rows")
    trace_times: list[float] = []
    trace_density: list[float] = []
    for index, raw_point in enumerate(trace):
        point = _mapping(raw_point, f"mesh N={expected_mesh} trace row {index}")
        time = _finite_float(point.get("time"), f"mesh N={expected_mesh} trace time {index}")
        density = _finite_float(point.get("f"), f"mesh N={expected_mesh} trace density {index}")
        _require(density >= 0.0, f"mesh N={expected_mesh} trace density must be nonnegative")
        trace_times.append(time)
        trace_density.append(density)
    _require_close(trace_times[0], 0.0, f"mesh N={expected_mesh} trace start", atol=0.0)
    _require_close(trace_times[-1], 35.0, f"mesh N={expected_mesh} trace stop", atol=0.0)
    _require(
        all(right > left for left, right in zip(trace_times, trace_times[1:])),
        f"mesh N={expected_mesh} saved-trace times must be strictly increasing",
    )

    structure = _mapping(row.get("stationary_structure"), f"mesh N={expected_mesh} structure")
    _require(
        structure.get("stationary_root_count") == 5,
        f"mesh N={expected_mesh} must retain exactly five reported roots",
    )
    _require(
        tuple(_sequence(structure.get("topology"), f"mesh N={expected_mesh} topology"))
        == EXPECTED_TOPOLOGY,
        f"mesh N={expected_mesh} topology must remain max-min-max-min-max",
    )
    raw_roots = _sequence(structure.get("roots"), f"mesh N={expected_mesh} roots")
    _require(len(raw_roots) == 5, f"mesh N={expected_mesh} must have five root records")
    roots: list[RootPoint] = []
    for index, expected_topology in enumerate(EXPECTED_TOPOLOGY):
        raw_root = _mapping(raw_roots[index], f"mesh N={expected_mesh} root {index}")
        topology = raw_root.get("topology")
        _require(
            topology == expected_topology,
            f"mesh N={expected_mesh} root topology must remain max-min-max-min-max",
        )
        time = _finite_float(raw_root.get("time"), f"mesh N={expected_mesh} root time {index}")
        density = _finite_float(
            raw_root.get("density"), f"mesh N={expected_mesh} root density {index}"
        )
        curvature = _finite_float(
            raw_root.get("f_tt"), f"mesh N={expected_mesh} root curvature {index}"
        )
        _require(0.0 < time < 35.0, f"mesh N={expected_mesh} root must lie in saved trace")
        _require(density > 0.0, f"mesh N={expected_mesh} root density must be positive")
        expected_sign = -1.0 if topology == "maximum" else 1.0
        _require(
            expected_sign * curvature > 0.0,
            f"mesh N={expected_mesh} root curvature contradicts topology",
        )
        roots.append(RootPoint(time=time, density=density, topology=topology))
    _require(
        all(right.time > left.time for left, right in zip(roots, roots[1:])),
        f"mesh N={expected_mesh} root times must be strictly increasing",
    )

    event = _mapping(
        row.get("survival_and_event_mass"), f"mesh N={expected_mesh} event masses"
    )
    _require_close(
        _finite_float(event.get("final_time"), f"mesh N={expected_mesh} final time"),
        FINAL_TIME,
        f"mesh N={expected_mesh} finite gate window",
        atol=0.0,
    )
    raw_masses = _sequence(
        event.get("basin_reaction_masses"), f"mesh N={expected_mesh} basin masses"
    )
    _require(len(raw_masses) == 3, f"mesh N={expected_mesh} must have three basin masses")
    masses = tuple(
        _finite_float(value, f"mesh N={expected_mesh} basin mass {index}")
        for index, value in enumerate(raw_masses)
    )
    _require(
        all(value >= EVENT_MASS_FLOOR for value in masses),
        f"mesh N={expected_mesh} event mass falls below frozen 0.005 floor",
    )
    final_survival = _finite_float(
        event.get("final_survival"), f"mesh N={expected_mesh} final survival"
    )
    valley_survivals = (
        _finite_float(raw_roots[1].get("survival"), f"mesh N={expected_mesh} first valley"),
        _finite_float(raw_roots[3].get("survival"), f"mesh N={expected_mesh} second valley"),
    )
    reconstructed = (
        1.0 - valley_survivals[0],
        valley_survivals[0] - valley_survivals[1],
        valley_survivals[1] - final_survival,
    )
    for index, (observed, expected) in enumerate(zip(masses, reconstructed, strict=True)):
        _require_close(observed, expected, f"mesh N={expected_mesh} basin mass {index}")
    _require_close(
        _finite_float(event.get("basin_mass_sum"), f"mesh N={expected_mesh} mass sum"),
        sum(masses),
        f"mesh N={expected_mesh} saved mass sum",
    )
    _require_close(
        _finite_float(
            event.get("basin_mass_sum_vs_total_reaction_difference"),
            f"mesh N={expected_mesh} mass closure",
        ),
        0.0,
        f"mesh N={expected_mesh} event-mass closure",
        atol=0.0,
    )

    return MeshFigureData(
        mesh=expected_mesh,
        trace_times=tuple(trace_times),
        trace_density=tuple(trace_density),
        roots=tuple(roots),
        basin_masses=(masses[0], masses[1], masses[2]),
    )


def validate_payloads(
    result: dict[str, Any],
    reproducibility: dict[str, Any],
    audit: dict[str, Any],
) -> FigureData:
    """Validate all claim-bearing inputs before any Matplotlib object is created."""

    _validate_chain(result, reproducibility, audit)
    _validate_result_claims(result)
    rows = _sequence(result.get("heldout_mesh_rows"), "held-out mesh rows")
    _require(len(rows) == 2, "canonical result must contain exactly two held-out meshes")
    meshes = tuple(
        _validate_mesh_row(_mapping(row, f"held-out mesh row {index}"), expected_mesh)
        for index, (row, expected_mesh) in enumerate(zip(rows, EXPECTED_MESHES, strict=True))
    )

    audit_rows = _sequence(audit.get("mesh_reconstructions"), "audit mesh reconstructions")
    _require(len(audit_rows) == 2, "audit must contain exactly two mesh reconstructions")
    for mesh_data, raw_audit_row in zip(meshes, audit_rows, strict=True):
        audit_row = _mapping(raw_audit_row, f"audit mesh N={mesh_data.mesh}")
        _require(audit_row.get("mesh") == mesh_data.mesh, "audit mesh order or identity changed")
        _require(
            audit_row.get("expected_five_root_topology") is True,
            f"audit topology gate failed for N={mesh_data.mesh}",
        )
        _require(
            audit_row.get("all_reported_mesh_gates_passed") is True,
            f"audit aggregate gate failed for N={mesh_data.mesh}",
        )
        _require(
            tuple(audit_row.get("root_times", ()))
            == tuple(root.time for root in mesh_data.roots),
            f"audit root-time reconstruction disagrees for N={mesh_data.mesh}",
        )
        _require(
            tuple(audit_row.get("basin_masses", ())) == mesh_data.basin_masses,
            f"audit basin-mass reconstruction disagrees for N={mesh_data.mesh}",
        )

    return FigureData(meshes=(meshes[0], meshes[1]))


def preflight_sources(
    *,
    result_path: Path = RESULT,
    reproducibility_path: Path = REPRODUCIBILITY,
    audit_path: Path = INDEPENDENT_AUDIT,
) -> FigureData:
    """Fail closed unless all three pinned JSON inputs and bounded claims validate."""

    return validate_payloads(
        *read_pinned_payloads(
            result_path=result_path,
            reproducibility_path=reproducibility_path,
            audit_path=audit_path,
        )
    )


def _plot_trace_panel(axis: Any, data: FigureData) -> None:
    styles = ((BLUE, "-"), (GOLD, (0, (4.0, 2.2))))
    for mesh_data, (color, linestyle) in zip(data.meshes, styles, strict=True):
        axis.plot(
            mesh_data.trace_times,
            [1.0e3 * value for value in mesh_data.trace_density],
            color=color,
            linestyle=linestyle,
            linewidth=1.55,
            label=f"N={mesh_data.mesh}",
            zorder=2,
        )
        maxima = [root for root in mesh_data.roots if root.topology == "maximum"]
        minima = [root for root in mesh_data.roots if root.topology == "minimum"]
        axis.scatter(
            [root.time for root in maxima],
            [1.0e3 * root.density for root in maxima],
            s=27,
            marker="o",
            facecolor=color,
            edgecolor=INK,
            linewidth=0.55,
            zorder=4,
        )
        axis.scatter(
            [root.time for root in minima],
            [1.0e3 * root.density for root in minima],
            s=29,
            marker="D",
            facecolor="white",
            edgecolor=color,
            linewidth=1.05,
            zorder=4,
        )

    handles = [
        Line2D([], [], color=BLUE, linewidth=1.55, linestyle="-", label="N=113"),
        Line2D(
            [],
            [],
            color=GOLD,
            linewidth=1.55,
            linestyle=(0, (4.0, 2.2)),
            label="N=129",
        ),
        Line2D(
            [],
            [],
            marker="o",
            linestyle="none",
            markerfacecolor=MID_GREY,
            markeredgecolor=INK,
            markersize=5.0,
            label="local maximum",
        ),
        Line2D(
            [],
            [],
            marker="D",
            linestyle="none",
            markerfacecolor="white",
            markeredgecolor=MID_GREY,
            markersize=4.7,
            label="local minimum",
        ),
    ]
    axis.legend(handles=handles, loc="lower right", frameon=False, fontsize=6.7, ncol=2)
    axis.set_xlim(0.0, 35.0)
    axis.set_ylim(bottom=0.0)
    axis.set_xlabel("time $t$ (saved trace)")
    axis.set_ylabel("encounter density $f(t)$ ($\\times 10^{-3}$)")
    axis.set_title("(a) Saved density traces and stationary roots", loc="left", pad=19.0)
    axis.text(
        0.0,
        1.015,
        "fixed reflected box; $B=0.01$; same solver family; saved trace $t\\leq35$",
        transform=axis.transAxes,
        ha="left",
        va="bottom",
        fontsize=6.8,
        color=MID_GREY,
    )
    axis.grid(axis="y")


def _plot_mass_panel(axis: Any, data: FigureData) -> None:
    positions = (0.0, 1.0, 2.0)
    width = 0.34
    styles = ((BLUE, ""), (GOLD, "///"))
    for offset_index, (mesh_data, (color, hatch)) in enumerate(
        zip(data.meshes, styles, strict=True)
    ):
        offset = (-0.5 if offset_index == 0 else 0.5) * width
        bars = axis.bar(
            [position + offset for position in positions],
            mesh_data.basin_masses,
            width=width,
            color=color,
            edgecolor=INK,
            linewidth=0.65,
            hatch=hatch,
            label=f"N={mesh_data.mesh}",
            zorder=3,
        )
        for bar, value in zip(bars, mesh_data.basin_masses, strict=True):
            axis.text(
                bar.get_x() + bar.get_width() / 2.0,
                value * 1.07,
                f"{value:.3g}",
                ha="center",
                va="bottom",
                rotation=90,
                fontsize=5.9,
                color=INK,
            )

    axis.axhline(
        EVENT_MASS_FLOOR,
        color=MID_GREY,
        linestyle=(0, (3.0, 2.0)),
        linewidth=1.0,
        zorder=4,
    )
    handles = [
        Patch(facecolor=BLUE, edgecolor=INK, linewidth=0.65, label="N=113"),
        Patch(facecolor=GOLD, edgecolor=INK, linewidth=0.65, hatch="///", label="N=129"),
        Line2D(
            [],
            [],
            color=MID_GREY,
            linestyle=(0, (3.0, 2.0)),
            linewidth=1.0,
            label="frozen floor 0.005",
        ),
    ]
    axis.legend(handles=handles, loc="upper left", frameon=False, fontsize=6.7)
    axis.set_yscale("log")
    axis.set_ylim(0.0044, 0.24)
    axis.set_yticks((0.005, 0.01, 0.05, 0.1, 0.2))
    axis.set_yticklabels(("0.005", "0.01", "0.05", "0.1", "0.2"))
    axis.set_xticks(positions, ("basin 1", "basin 2", "basin 3"))
    axis.set_ylabel("reaction mass (log scale)")
    axis.set_title("(b) Event-basin reaction masses", loc="left", pad=19.0)
    axis.text(
        0.0,
        1.015,
        "odd meshes; basin-mass/tail gate through $t\\leq100$",
        transform=axis.transAxes,
        ha="left",
        va="bottom",
        fontsize=6.8,
        color=MID_GREY,
    )
    axis.grid(axis="y", which="major")
    axis.grid(axis="y", which="minor", visible=False)


def render_pdf_bytes(data: FigureData) -> bytes:
    """Render deterministic vector PDF bytes entirely in memory."""

    rc = {
        "font.family": "DejaVu Sans",
        "font.size": 7.6,
        "axes.titlesize": 8.8,
        "axes.titleweight": "normal",
        "axes.labelsize": 7.4,
        "axes.edgecolor": "#4E535A",
        "axes.linewidth": 0.75,
        "axes.grid": True,
        "axes.axisbelow": True,
        "grid.color": LIGHT_GREY,
        "grid.linewidth": 0.55,
        "grid.alpha": 1.0,
        "xtick.labelsize": 6.8,
        "ytick.labelsize": 6.8,
        "xtick.color": "#4E535A",
        "ytick.color": "#4E535A",
        "text.color": INK,
        "axes.labelcolor": "#33363B",
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "savefig.facecolor": "white",
        "savefig.transparent": False,
        "pdf.fonttype": 42,
        "pdf.compression": 9,
        "ps.fonttype": 42,
    }
    with plt.rc_context(rc):
        figure = plt.figure(figsize=(7.2, 4.15))
        grid = figure.add_gridspec(1, 2, width_ratios=(1.48, 1.0), wspace=0.30)
        trace_axis = figure.add_subplot(grid[0, 0])
        mass_axis = figure.add_subplot(grid[0, 1])
        for axis in (trace_axis, mass_axis):
            axis.patch.set_edgecolor("white")
            axis.patch.set_linewidth(0.0)
        _plot_trace_panel(trace_axis, data)
        _plot_mass_panel(mass_axis, data)
        figure.subplots_adjust(left=0.085, right=0.985, bottom=0.235, top=0.775)
        figure.suptitle(
            "Positive-budget broad-four-slab fixed-control evidence",
            x=0.085,
            y=0.962,
            ha="left",
            va="top",
            fontsize=10.0,
            color=INK,
        )
        figure.text(
            0.085,
            0.907,
            "Pinned canonical result: five alternating roots and three qualified event basins on $N=113,129$.",
            ha="left",
            va="top",
            fontsize=7.2,
            color=MID_GREY,
        )
        figure.text(
            0.5,
            0.085,
            (
                "Fixed box, $B=0.01$, same solver: five retained roots on saved screen "
                "$t\\leq35$; basin-mass/tail checks through $t=100$."
            ),
            ha="center",
            va="bottom",
            fontsize=6.2,
            color="#3F444B",
        )
        figure.text(
            0.5,
            0.045,
            (
                "No interval-global/post-35 root exclusion, continuum/box/parity, "
                "independent-solver, physical-$d=3$, cusp, or publication claim."
            ),
            ha="center",
            va="bottom",
            fontsize=6.2,
            color=MID_GREY,
        )
        fixed_date = datetime(2026, 7, 14, tzinfo=timezone.utc)
        metadata = {
            "Title": "Positive-budget broad-four-slab fixed-control evidence",
            "Author": "Encounter multimodality project",
            "Subject": "Pinned fixed-box same-solver two-mesh finite-window evidence",
            "Keywords": "encounter time, positive budget, fixed control, finite volume",
            "Creator": "plot_positive_b_broad_four_slab.py",
            "CreationDate": fixed_date,
            "ModDate": fixed_date,
        }
        buffer = io.BytesIO()
        figure.savefig(
            buffer,
            format="pdf",
            dpi=300,
            facecolor="white",
            edgecolor="white",
            metadata=metadata,
        )
        plt.close(figure)
    return buffer.getvalue()


def verify_vector_pdf_bytes(payload: bytes) -> dict[str, int]:
    """Reject malformed, rasterized, transparent, or Type-3-font PDF output."""

    if not payload.startswith(b"%PDF-") or b"%%EOF" not in payload[-1024:]:
        raise ValueError("rendered output is not a complete PDF")
    checks = {
        "type3_font_tokens": len(re.findall(rb"/Type3\b", payload)),
        "transparency_graphics_state_tokens": len(
            re.findall(rb"/(?:ca|CA|SMask|BM)\b", payload)
        ),
        "raster_image_xobject_tokens": len(re.findall(rb"/Subtype\s*/Image\b", payload)),
    }
    if any(checks.values()):
        raise ValueError(f"rendered PDF failed vector-safety checks: {checks}")
    return checks


def verify_vector_pdf(path: Path) -> dict[str, int]:
    return verify_vector_pdf_bytes(path.read_bytes())


def _report_relative(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPORT.resolve()))
    except ValueError as error:
        raise ValueError(f"provenance source is outside the report: {path}") from error


def expected_source_pins() -> dict[str, str]:
    """Return compiler-verifiable pins without hard-pinning the plotter to itself."""

    return {
        "canonical_result": _report_relative(RESULT),
        "canonical_result_sha256": EXPECTED_RESULT_SHA256,
        "independent_audit": _report_relative(INDEPENDENT_AUDIT),
        "independent_audit_sha256": EXPECTED_INDEPENDENT_AUDIT_SHA256,
        "plotter": _report_relative(HERE),
        "plotter_sha256": sha256_bytes(_read_regular_file(HERE, "plotter source")),
        "reproducibility_evidence": _report_relative(REPRODUCIBILITY),
        "reproducibility_evidence_sha256": EXPECTED_REPRODUCIBILITY_SHA256,
        "test": _report_relative(TEST_SOURCE),
        "test_sha256": sha256_bytes(_read_regular_file(TEST_SOURCE, "plotter test source")),
    }


def _figure_contract() -> dict[str, Any]:
    return {
        "analytical_question": (
            "Does one unchanged result-informed fixed control retain three saved density "
            "modes and three event basins above the frozen 0.005 reaction-mass floor on "
            "held-out odd meshes N=113 and N=129?"
        ),
        "canonical_family": "two-panel line-and-marker plus grouped-bar comparison",
        "non_colour_distinction": (
            "solid versus dashed mesh lines; filled maximum versus open minimum markers; "
            "solid versus hatched grouped bars"
        ),
        "palette_policy": "hard two-root cap: blue and gold plus neutral ink and grey",
        "panels": {
            "a": (
                "saved encounter-density traces for t<=35 with five alternating stationary "
                "roots on each held-out mesh"
            ),
            "b": (
                "three grouped event-basin reaction masses per mesh on an explicit log scale "
                "with the neutral frozen 0.005 floor"
            ),
        },
        "renderer": "deterministic Matplotlib static vector PDF",
        "takeaway": (
            "Within one fixed reflected box and the same solver family, both held-out odd "
            "meshes retain five alternating roots on the saved t<=35 root screen; all six "
            "valley-partitioned event-basin masses through t=100 exceed 0.005, without "
            "interval-global or post-35 root exclusion."
        ),
        "visible_scope_note": (
            "B=0.01; unchanged result-informed control; fixed box; same solver family; "
            "five retained roots on saved screen t<=35; valley-partitioned basin-mass and "
            "tail checks through t=100; no interval-global or post-35 root exclusion; no "
            "continuum, box/parity, independent-solver, physical-d3, allocation-cusp, or "
            "publication-gate claim"
        ),
    }


def _renderer_metadata() -> dict[str, Any]:
    return {
        "backend": "Agg/PDF",
        "deterministic_fixed_pdf_dates": True,
        "font_family": "DejaVu Sans",
        "matplotlib_version": matplotlib.__version__,
        "pdf_fonttype": 42,
        "raster_layers": False,
        "transparent_background": False,
    }


def _plotted_data(data: FigureData) -> dict[str, Any]:
    return {
        "basin_reaction_masses": {
            str(mesh.mesh): list(mesh.basin_masses) for mesh in data.meshes
        },
        "event_mass_floor": EVENT_MASS_FLOOR,
        "finite_gate_time_max": FINAL_TIME,
        "mesh_order": [mesh.mesh for mesh in data.meshes],
        "root_times": {
            str(mesh.mesh): [root.time for root in mesh.roots] for mesh in data.meshes
        },
        "saved_trace_points_per_mesh": [len(mesh.trace_times) for mesh in data.meshes],
        "saved_trace_time_max": 35.0,
        "stationary_topology": list(EXPECTED_TOPOLOGY),
    }


def build_metadata_payload(
    data: FigureData,
    pdf_bytes: bytes,
    pdf_qa: dict[str, int],
) -> dict[str, Any]:
    """Build a deterministic, compiler-compatible provenance sidecar payload."""

    return {
        "caption": (
            "Positive-budget broad-four-slab fixed-control evidence. Saved density traces "
            "retain max-min-max-min-max topology on N=113 and N=129 on the saved root "
            "screen t<=35. All three valley-partitioned event basins on each mesh exceed "
            "the frozen 0.005 mass floor through t=100. No interval-global or post-35 root "
            "exclusion is claimed; this is a fixed-box, same-solver-family point result."
        ),
        "claim_flags": dict(METADATA_CLAIM_FLAGS),
        "claim_scope": EXPECTED_CLAIM_SCOPE,
        "evidence_timing": EXPECTED_EVIDENCE_TIMING,
        "figure_contract": _figure_contract(),
        "limitations": list(EXPECTED_LIMITATIONS),
        "outputs": {
            "metadata": _report_relative(OUTPUT_METADATA),
            "pdf": _report_relative(OUTPUT_PDF),
            "pdf_bytes": len(pdf_bytes),
            "pdf_sha256": sha256_bytes(pdf_bytes),
        },
        "pdf_qa": dict(pdf_qa),
        "plotted_data": _plotted_data(data),
        "renderer": _renderer_metadata(),
        "schema_version": 1,
        "scope_constraints": dict(METADATA_SCOPE_CONSTRAINTS),
        "source_pins": expected_source_pins(),
        "stage": "positive_B_broad_four_slab_figure_provenance",
        "status": "PASS_PINNED_FIXED_CONTROL_FIGURE_WITH_PROVENANCE",
    }


def validate_metadata_payload(
    payload: dict[str, Any],
    data: FigureData,
    pdf_bytes: bytes,
) -> None:
    """Fail closed on metadata mutation, source drift, or claim promotion."""

    expected_keys = {
        "caption",
        "claim_flags",
        "claim_scope",
        "evidence_timing",
        "figure_contract",
        "limitations",
        "outputs",
        "pdf_qa",
        "plotted_data",
        "renderer",
        "schema_version",
        "scope_constraints",
        "source_pins",
        "stage",
        "status",
    }
    _require(set(payload) == expected_keys, "figure metadata top-level schema changed")
    _require(payload.get("schema_version") == 1, "figure metadata schema version changed")
    _require(
        payload.get("stage") == "positive_B_broad_four_slab_figure_provenance",
        "figure metadata stage changed",
    )
    _require(
        payload.get("status") == "PASS_PINNED_FIXED_CONTROL_FIGURE_WITH_PROVENANCE",
        "figure metadata status changed",
    )
    _require(payload.get("claim_scope") == EXPECTED_CLAIM_SCOPE, "metadata claim scope changed")
    _require(
        payload.get("evidence_timing") == EXPECTED_EVIDENCE_TIMING,
        "metadata evidence timing changed",
    )
    _require(payload.get("claim_flags") == METADATA_CLAIM_FLAGS, "metadata claim flags changed")
    _require(
        payload.get("scope_constraints") == METADATA_SCOPE_CONSTRAINTS,
        "metadata fixed-box/same-solver/finite-window scope changed",
    )
    _require(
        payload.get("limitations") == list(EXPECTED_LIMITATIONS),
        "metadata limitations changed",
    )
    _require(payload.get("figure_contract") == _figure_contract(), "figure contract changed")
    _require(payload.get("renderer") == _renderer_metadata(), "renderer metadata changed")
    _require(payload.get("plotted_data") == _plotted_data(data), "plotted-data record changed")
    _require(
        payload.get("pdf_qa") == verify_vector_pdf_bytes(pdf_bytes),
        "metadata PDF QA record changed",
    )
    expected_outputs = {
        "metadata": _report_relative(OUTPUT_METADATA),
        "pdf": _report_relative(OUTPUT_PDF),
        "pdf_bytes": len(pdf_bytes),
        "pdf_sha256": sha256_bytes(pdf_bytes),
    }
    _require(payload.get("outputs") == expected_outputs, "metadata PDF output pin changed")
    _require(payload.get("source_pins") == expected_source_pins(), "metadata source pin changed")


def canonical_metadata_bytes(payload: dict[str, Any]) -> bytes:
    """Serialize canonical sorted JSON with no timestamp or runtime-path field."""

    return (
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False, ensure_ascii=True) + "\n"
    ).encode("utf-8")


def _default_metadata_path(output_path: Path) -> Path:
    return output_path.with_name(f"{output_path.stem}_metadata.json")


def _ensure_outputs_are_safe(
    output_path: Path,
    metadata_path: Path,
    protected_paths: tuple[Path, ...],
) -> None:
    if output_path.suffix.lower() != ".pdf":
        raise ValueError("figure output must have a .pdf suffix")
    if metadata_path.suffix.lower() != ".json":
        raise ValueError("figure metadata output must have a .json suffix")
    resolved_outputs = {output_path.resolve(strict=False), metadata_path.resolve(strict=False)}
    if len(resolved_outputs) != 2:
        raise ValueError("PDF and metadata outputs must be distinct")
    resolved_protected = {path.resolve(strict=False) for path in protected_paths}
    if resolved_outputs & resolved_protected:
        raise ValueError("figure outputs must not alias a protected source")
    for target in (output_path, metadata_path):
        if target.is_symlink():
            raise ValueError("figure outputs must not be symlinks")
        if target.is_dir():
            raise ValueError("figure outputs must not be directories")


def _fsync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _write_same_directory_temp(target: Path, payload: bytes, role: str, mode: int) -> Path:
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{target.name}.{role}.", suffix=".tmp", dir=target.parent
    )
    temporary = Path(temporary_name)
    try:
        os.fchmod(descriptor, mode)
        with os.fdopen(descriptor, "wb", closefd=True) as handle:
            descriptor = -1
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
    except BaseException:
        if descriptor >= 0:
            os.close(descriptor)
        temporary.unlink(missing_ok=True)
        raise
    return temporary


def _existing_target(target: Path) -> tuple[bytes, int] | None:
    if target.is_symlink():
        raise ValueError(f"publication target must not be a symlink: {target}")
    try:
        target_stat = target.lstat()
    except FileNotFoundError:
        return None
    if not stat.S_ISREG(target_stat.st_mode):
        raise ValueError(f"publication target must be a regular file: {target}")
    return target.read_bytes(), stat.S_IMODE(target_stat.st_mode)


def _publish_transaction(
    outputs: dict[Path, bytes],
    *,
    replace: ReplaceFunction = os.replace,
    sync_directory: DirectorySyncFunction = _fsync_directory,
) -> None:
    """Publish PDF and sidecar together with same-directory rollback safety."""

    if not outputs:
        raise ValueError("publication transaction must contain outputs")
    resolved = [target.resolve(strict=False) for target in outputs]
    if len(resolved) != len(set(resolved)):
        raise ValueError("publication transaction has duplicate output targets")
    if not all(isinstance(payload, bytes) and payload for payload in outputs.values()):
        raise ValueError("publication transaction payloads must be nonempty bytes")

    prepared: dict[Path, Path] = {}
    backups: dict[Path, Path | None] = {}
    existed: dict[Path, bool] = {}
    published: list[Path] = []
    touched_directories: set[Path] = set()
    try:
        for target, payload in outputs.items():
            target.parent.mkdir(parents=True, exist_ok=True)
            touched_directories.add(target.parent)
            prior = _existing_target(target)
            existed[target] = prior is not None
            prepared[target] = _write_same_directory_temp(target, payload, "incoming", 0o644)
            if prior is None:
                backups[target] = None
            else:
                prior_bytes, prior_mode = prior
                backups[target] = _write_same_directory_temp(
                    target, prior_bytes, "backup", prior_mode
                )

        for target in outputs:
            # Register before replace so even a replace-then-raise fault is rolled back.
            published.append(target)
            replace(prepared[target], target)
        for target, expected in outputs.items():
            if target.read_bytes() != expected:
                raise RuntimeError(f"published output failed byte verification: {target}")
        for directory in touched_directories:
            sync_directory(directory)
    except BaseException:
        rollback_errors: list[str] = []
        for target in reversed(published):
            try:
                backup = backups[target]
                if existed[target] and backup is not None:
                    replace(backup, target)
                    backups[target] = None
                else:
                    target.unlink(missing_ok=True)
            except BaseException as error:  # pragma: no cover - catastrophic filesystem error
                rollback_errors.append(f"{target}: {error}")
        for directory in touched_directories:
            try:
                _fsync_directory(directory)
            except OSError as error:  # pragma: no cover - catastrophic filesystem error
                rollback_errors.append(f"fsync {directory}: {error}")
        if rollback_errors:
            raise RuntimeError(
                "paired figure publication failed and rollback was incomplete: "
                + "; ".join(rollback_errors)
            )
        raise
    finally:
        for path in (*prepared.values(), *(item for item in backups.values() if item is not None)):
            path.unlink(missing_ok=True)


def build_figure(
    *,
    result_path: Path = RESULT,
    reproducibility_path: Path = REPRODUCIBILITY,
    audit_path: Path = INDEPENDENT_AUDIT,
    output_path: Path = OUTPUT_PDF,
    metadata_path: Path | None = None,
) -> BuildReceipt:
    """Validate, render, and transactionally publish PDF plus provenance sidecar."""

    resolved_metadata = metadata_path or _default_metadata_path(output_path)
    protected = (result_path, reproducibility_path, audit_path, HERE, TEST_SOURCE)
    _ensure_outputs_are_safe(output_path, resolved_metadata, protected)
    data = preflight_sources(
        result_path=result_path,
        reproducibility_path=reproducibility_path,
        audit_path=audit_path,
    )
    pdf_bytes = render_pdf_bytes(data)
    pdf_qa = verify_vector_pdf_bytes(pdf_bytes)
    metadata_payload = build_metadata_payload(data, pdf_bytes, pdf_qa)
    validate_metadata_payload(metadata_payload, data, pdf_bytes)
    metadata_bytes = canonical_metadata_bytes(metadata_payload)

    # Close the read-to-publish race for both scientific inputs and source pins.
    read_pinned_payloads(
        result_path=result_path,
        reproducibility_path=reproducibility_path,
        audit_path=audit_path,
    )
    validate_metadata_payload(metadata_payload, data, pdf_bytes)
    _publish_transaction({output_path: pdf_bytes, resolved_metadata: metadata_bytes})
    return BuildReceipt(
        output=output_path,
        sha256=sha256_bytes(pdf_bytes),
        byte_count=len(pdf_bytes),
        metadata=resolved_metadata,
        metadata_sha256=sha256_bytes(metadata_bytes),
        metadata_byte_count=len(metadata_bytes),
        pdf_qa=pdf_qa,
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--result", type=Path, default=RESULT)
    parser.add_argument("--reproducibility", type=Path, default=REPRODUCIBILITY)
    parser.add_argument("--audit", type=Path, default=INDEPENDENT_AUDIT)
    parser.add_argument("--output", type=Path, default=OUTPUT_PDF)
    parser.add_argument("--metadata", type=Path)
    args = parser.parse_args(argv)
    receipt = build_figure(
        result_path=args.result,
        reproducibility_path=args.reproducibility,
        audit_path=args.audit,
        output_path=args.output,
        metadata_path=args.metadata,
    )
    print("status=PASS_PINNED_FIXED_CONTROL_FIGURE")
    print(f"output={receipt.output}")
    print(f"sha256={receipt.sha256}")
    print(f"bytes={receipt.byte_count}")
    print(f"metadata={receipt.metadata}")
    print(f"metadata_sha256={receipt.metadata_sha256}")
    print(f"metadata_bytes={receipt.metadata_byte_count}")
    print(f"pdf_qa={receipt.pdf_qa}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
