from __future__ import annotations

import copy
import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
CODE_DIR = (
    ROOT / "research" / "reports" / "grid2d_one_two_target_gating" / "code"
)
if str(CODE_DIR) not in sys.path:
    sys.path.insert(0, str(CODE_DIR))

import build_gating_campaign_manifest_v3 as builder  # noqa: E402
import generate_disorder_field_pack_v3 as generator  # noqa: E402
import validate_gating_campaign_manifest_v3 as validator  # noqa: E402


def _tiny_frozen_inputs(tmp_path: Path) -> tuple[Path, Path, Path]:
    pack = tmp_path / "disorder_field_pack_v3.npz"
    sidecar = tmp_path / "disorder_field_pack_v3.manifest.json"
    generator.generate_field_pack(
        output_pack=pack,
        output_manifest=sidecar,
        field_count=2,
        width=64,
        height=48,
        sigma=4.0,
        overwrite=False,
        argv=["pytest-field-pack"],
    )
    return pack, sidecar, CODE_DIR / "gpu_gating_mc_v3.py"


def _build_tiny_manifests(
    tmp_path: Path,
) -> tuple[Path, Path, Path, Path, Path, Path]:
    pack, sidecar, runner = _tiny_frozen_inputs(tmp_path)
    canary = tmp_path / "gating_v3_canary_manifest.json"
    production = tmp_path / "gating_v3_production_manifest.json"
    tail = tmp_path / "gating_v3_tail160k_manifest.json"
    builder.build_manifests(
        field_pack=pack,
        field_pack_manifest=sidecar,
        runner_source=runner,
        container_reference=(
            "oras://registry.example.invalid/gating@sha256:" + ("ab" * 32)
        ),
        container_sha256="ab" * 32,
        output_canary=canary,
        output_production=production,
        output_tail=tail,
    )
    return pack, sidecar, runner, canary, production, tail


def test_field_pack_is_byte_deterministic_and_has_exact_invariants(tmp_path: Path) -> None:
    first_pack = tmp_path / "first.npz"
    first_manifest = tmp_path / "first.json"
    second_pack = tmp_path / "second.npz"
    second_manifest = tmp_path / "second.json"
    common = {
        "field_count": 2,
        "width": 64,
        "height": 48,
        "sigma": 4.0,
        "seed_base": generator.DEFAULT_SEED_BASE,
        "seed_stride": generator.DEFAULT_SEED_STRIDE,
        "argv": ["pytest-field-pack"],
    }
    first = generator.generate_field_pack(
        output_pack=first_pack,
        output_manifest=first_manifest,
        **common,
    )
    second = generator.generate_field_pack(
        output_pack=second_pack,
        output_manifest=second_manifest,
        **common,
    )

    assert first_pack.read_bytes() == second_pack.read_bytes()
    assert first["pack"]["sha256"] == second["pack"]["sha256"]
    assert first["definition"]["white_noise"].startswith(
        "numpy.random.Generator(PCG64)"
    )
    assert first["definition"]["smoothing"] == {
        "implementation": "scipy.ndimage.gaussian_filter",
        "sigma": 4.0,
        "order": 0,
        "mode": "reflect",
        "truncate": 4.0,
    }

    with np.load(first_pack, allow_pickle=False) as payload:
        contrasts = np.asarray(payload["contrasts"], dtype="<f8")
        seeds = np.asarray(payload["seeds"], dtype="<i8")
    assert contrasts.shape == (2, 48, 64)
    assert seeds.tolist() == [20_260_726, 20_268_645]
    for index, contrast in enumerate(contrasts):
        assert math.fsum(float(value) for value in contrast.reshape(-1)) == 0.0
        assert float(np.max(np.abs(contrast))) == 1.0
        assert abs(float(contrast.mean(dtype=np.float64))) < 1.0e-15
        assert hashlib.sha256(contrast.tobytes(order="C")).hexdigest() == first[
            "fields"
        ][index]["sha256_float64_le"]


def test_builder_emits_runner_contract_and_validates_both_campaigns(tmp_path: Path) -> None:
    pack, sidecar, runner, canary_path, production_path, tail_path = (
        _build_tiny_manifests(tmp_path)
    )
    canary = json.loads(canary_path.read_text())
    production = json.loads(production_path.read_text())
    tail = json.loads(tail_path.read_text())

    required_top_level = {
        "schema",
        "defaults",
        "profiles",
        "cells",
        "field_pack_sha256",
    }
    assert required_top_level <= set(canary)
    assert required_top_level <= set(production)
    assert [cell["cell_id"] for cell in canary["cells"]] == list(range(8))
    assert [cell["cell_id"] for cell in production["cells"]] == list(range(360))
    assert [cell["cell_id"] for cell in tail["cells"]] == list(range(24))
    assert {cell["profile"] for cell in tail["cells"]} == {"tail_160k"}
    assert tail["campaign"]["activation_gate"].endswith("tail gate is FAIL")
    assert production["defaults"]["checkpoints"] == [
        5_000,
        10_000,
        20_000,
        40_000,
        80_000,
    ]
    assert production["profiles"]["tail_160k"]["steps"] == 160_000
    assert production["field_pack_sha256"] == hashlib.sha256(pack.read_bytes()).hexdigest()

    canary_summary = validator.validate_manifest_file(
        canary_path,
        field_pack=pack,
        field_pack_manifest=sidecar,
        runner_source=runner,
    )
    production_summary = validator.validate_manifest_file(
        production_path,
        field_pack=pack,
        field_pack_manifest=sidecar,
        runner_source=runner,
    )
    tail_summary = validator.validate_manifest_file(
        tail_path,
        field_pack=pack,
        field_pack_manifest=sidecar,
        runner_source=runner,
    )
    assert canary_summary["cell_count"] == 8
    assert canary_summary["crn_pair_count"] == 4
    assert production_summary["cell_count"] == 360
    assert production_summary["crn_pair_count"] == 4
    assert production_summary["task_mapping"] == "valid"
    assert production_summary["rope"] == "valid"
    assert production_summary["gates"] == "valid"
    assert tail_summary["cell_count"] == 24
    assert tail_summary["crn_pair_count"] == 4


@pytest.mark.parametrize("field_count,last_cell_id", [(32, 5_759), (128, 23_039)])
def test_production_task_mapping_round_trips_to_128_fields(
    field_count: int, last_cell_id: int
) -> None:
    assert builder.encode_production_cell_id(
        geometry_index_value=14,
        amplitude_index=5,
        field_index=field_count - 1,
        stream_index=1,
        field_count=field_count,
    ) == last_cell_id
    for cell_id in (0, 1, field_count * 2 - 1, last_cell_id // 2, last_cell_id):
        decoded = builder.decode_production_cell_id(cell_id, field_count=field_count)
        assert builder.encode_production_cell_id(
            geometry_index_value=decoded["geometry_index"],
            amplitude_index=decoded["amplitude_index"],
            field_index=decoded["field_index"],
            stream_index=decoded["stream_index"],
            field_count=field_count,
        ) == cell_id


def test_default_32_field_stage_counts_rope_and_gates_are_frozen() -> None:
    preregistration = builder._preregistration(32)
    assert preregistration["production_task_count"] == 5_760
    tail_cells = builder._tail_cells(32)
    assert len(tail_cells) == 384
    assert [cell["cell_id"] for cell in tail_cells] == list(range(384))
    assert {cell["profile"] for cell in tail_cells} == {"tail_160k"}
    assert {
        stage["stage_id"]: stage["task_count"]
        for stage in preregistration["stages"]
    } == {
        "G0": 8,
        "A": 384,
        "A2": 384,
        "B1": 1_536,
        "B2": 1_280,
        "B3": 2_560,
    }
    inference = preregistration["primary_inference"]
    assert inference["primary_geometry"] == {"target2_x": 32, "target2_y": 24}
    assert inference["primary_amplitude_contrast"] == {
        "high": 0.20,
        "low": 0.0,
        "contrast": "high - low",
    }
    assert inference["rope_absolute_probability"] == 0.002
    tail = preregistration["gates"]["tail"]
    assert tail["one_target_unresolved_upper_max"] == 0.005
    assert tail["two_target_unresolved_upper_max"] == 0.005
    assert tail["horizon_drift_abs_plus_tcrit_se_max"] == 0.002
    assert preregistration["budget"]["campaign_hard_cap"] == 950.0
    assert preregistration["budget"]["unallocated_margin"] == 28.0


@pytest.mark.parametrize(
    "mutator,match",
    [
        (
            lambda payload: payload["cells"][0].__setitem__("cell_id", 1),
            "task mapping",
        ),
        (
            lambda payload: payload["preregistration"]["primary_inference"].__setitem__(
                "rope_absolute_probability", 0.003
            ),
            "ROPE",
        ),
        (
            lambda payload: payload["preregistration"]["gates"]["integrity"].__setitem__(
                "mass_balance_absolute_error_max", 1.0e-8
            ),
            "gates",
        ),
        (
            lambda payload: payload["artifacts"]["container"].__setitem__(
                "reference", "PLACEHOLDER"
            ),
            "placeholder",
        ),
    ],
)
def test_validator_rejects_mapping_rope_gate_and_placeholder_mutations(
    tmp_path: Path, mutator, match: str
) -> None:
    pack, sidecar, runner, _canary_path, production_path, _tail_path = (
        _build_tiny_manifests(tmp_path)
    )
    payload = json.loads(production_path.read_text())
    corrupted = copy.deepcopy(payload)
    mutator(corrupted)
    with pytest.raises(ValueError, match=match):
        validator.validate_manifest(
            corrupted,
            field_pack=pack,
            field_pack_manifest=sidecar,
            runner_source=runner,
        )
