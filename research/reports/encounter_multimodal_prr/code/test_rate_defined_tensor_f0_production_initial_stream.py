from __future__ import annotations

import ast
import copy
import hashlib
import json
import shutil
import struct
import subprocess
import sys
from dataclasses import replace
from fractions import Fraction
from pathlib import Path

import pytest
import rate_defined_tensor_f0 as f0
import rate_defined_tensor_f0_geometry_bound_packed_axes as geometry_bound
import rate_defined_tensor_f0_production_initial_clean_replay as clean_replay
import rate_defined_tensor_f0_production_initial_independent as independent
import rate_defined_tensor_f0_production_initial_rebuild as rebuild
import rate_defined_tensor_f0_production_initial_stream as stream

REPORT_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def production_bundle(tmp_path_factory: pytest.TempPathFactory) -> Path:
    output = tmp_path_factory.mktemp("production-initial-stream") / "bundle"
    manifest = stream.produce_bundle(REPORT_ROOT, output)
    assert manifest["status"] == stream.STATUS
    return output


@pytest.fixture(scope="module")
def relational_receipt(production_bundle: Path) -> dict[str, object]:
    return rebuild.rebuild_bundle(production_bundle)


@pytest.fixture(scope="module")
def geometry_bound_rows(
    production_bundle: Path,
) -> tuple[geometry_bound.GeometryBoundPackedAxes, ...]:
    return geometry_bound.build_all_geometry_bound_packed_axes(production_bundle)


def _bundle_manifest(root: Path) -> dict[str, object]:
    return json.loads((root / "bundle.json").read_text("ascii"))


def _row_manifest(root: Path, label: str) -> dict[str, object]:
    bundle = _bundle_manifest(root)
    summary = next(row for row in bundle["rows"] if row["configuration_label"] == label)
    return json.loads((root / summary["row_manifest"]["path"]).read_text("ascii"))


def test_configuration_family_has_permanent_fail_closed_loader() -> None:
    family, source = stream.load_configuration_family(REPORT_ROOT)
    assert hashlib.sha256(source).hexdigest() == stream.ACCEPTED_CONFIGURATION_SHA256
    assert family["configuration_order"] == list(f0.PHYSICAL_CONFIGURATION_ORDER_V2)
    assert family["configuration_count"] == 12
    assert family["total_state_workload"] == 34_787_462
    assert family["contains_control_values"] is False
    assert family["contains_budget_value"] is False
    assert family["authorizes_scientific_execution"] is False


def test_configuration_mutations_and_duplicate_keys_fail_closed() -> None:
    family, _ = stream.load_configuration_family(REPORT_ROOT)
    shifted = copy.deepcopy(family)
    shifted["configurations"][10]["relative_perpendicular"]["periodic_shift_exact"] = "0/1"
    with pytest.raises(stream.ProductionInitialStreamFailure, match="row drifted"):
        stream._validate_configuration_semantics(REPORT_ROOT, shifted)

    reordered = copy.deepcopy(family)
    reordered["configurations"][0], reordered["configurations"][1] = (
        reordered["configurations"][1],
        reordered["configurations"][0],
    )
    with pytest.raises(stream.ProductionInitialStreamFailure, match="row drifted"):
        stream._validate_configuration_semantics(REPORT_ROOT, reordered)

    with pytest.raises(stream.ProductionInitialStreamFailure, match="duplicate"):
        stream._parse_strict_json(b'{"a": 1, "a": 2}\n', label="attacker JSON")
    with pytest.raises(stream.ProductionInitialStreamFailure, match="floating literal"):
        stream._parse_strict_json(b'{"a": 1.0}\n', label="attacker JSON")


def test_full_twelve_row_bundle_is_small_file_backed_and_nonpromoting(
    production_bundle: Path,
) -> None:
    manifest = stream.verify_bundle(production_bundle)
    assert manifest["configuration_count"] == 12
    assert manifest["total_state_workload"] == 34_787_462
    assert manifest["total_dense_expansion_byte_length"] == 556_599_392
    assert len(manifest["file_inventory"]) == 206
    assert (
        sum(path.stat().st_size for path in production_bundle.rglob("*") if path.is_file())
        < 2_000_000
    )
    assert not any("dense" in entry["path"] for entry in manifest["file_inventory"])
    assert manifest["flags"] == {
        "analytic_source_to_sparse_box_producer_consistent_all_rows": True,
        "authorizes_scientific_execution": False,
        "clean_process_replay_complete": False,
        "contains_budget_value": False,
        "contains_control_values": False,
        "free_axis_geometry_rate_producer_consistent_all_rows": True,
        "full_operator_bound": False,
        "independent_geometry_relation_replay_complete": False,
        "independent_source_box_replay_complete": False,
        "killing_contact_geometry_bound": False,
        "positive_budget_executed": False,
        "production_resource_gate": False,
        "science_executed": False,
        "topology_complete": False,
    }


def test_stream_verifier_pins_the_imported_f0_core(
    production_bundle: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    original_sha256_file = stream._sha256_file
    imported_f0_path = Path(stream.f0.__file__).resolve()

    def report_core_drift(path: Path) -> str:
        if Path(path).resolve() == imported_f0_path:
            return "0" * 64
        return original_sha256_file(path)

    monkeypatch.setattr(stream, "_sha256_file", report_core_drift)
    with pytest.raises(stream.ProductionInitialStreamFailure, match="imported F0 core"):
        stream.verify_bundle(production_bundle)


def test_same_shape_and_same_count_substitutions_have_distinct_geometry_bindings(
    production_bundle: Path,
) -> None:
    even = _row_manifest(production_bundle, "E128/Base")
    shifted = _row_manifest(production_bundle, "A_Y")
    even_y = next(axis for axis in even["axes"] if axis["coordinate"] == "relative_perpendicular")
    shifted_y = next(
        axis for axis in shifted["axes"] if axis["coordinate"] == "relative_perpendicular"
    )
    assert even["sparse_component_box"]["shape"] == shifted["sparse_component_box"]["shape"]
    assert (
        even_y["rates"]["forward"]["file"]["sha256"]
        == shifted_y["rates"]["forward"]["file"]["sha256"]
    )
    assert even_y["partition_file"]["sha256"] != shifted_y["partition_file"]["sha256"]
    assert even_y["axis_relation_sha256"] != shifted_y["axis_relation_sha256"]
    assert even["source_box_relation_sha256"] != shifted["source_box_relation_sha256"]

    midpoint_shift = _row_manifest(production_bundle, "A_M")
    relative_shift = _row_manifest(production_bundle, "A_R")
    assert midpoint_shift["expected_states"] == relative_shift["expected_states"]
    assert midpoint_shift["sparse_component_box"]["shape"] == [129, 128, 128]
    assert relative_shift["sparse_component_box"]["shape"] == [128, 129, 128]
    assert midpoint_shift["row_relation_sha256"] != relative_shift["row_relation_sha256"]


def test_virtual_dense_digest_matches_naive_dense_bytes() -> None:
    first = f0.OutwardInterval.from_fraction_bounds(Fraction(1, 3), Fraction(1, 2))
    second = f0.OutwardInterval.from_fraction_bounds(Fraction(1, 4), Fraction(1, 3))
    records = ((1, first), (4, second))
    naive = bytearray(stream.ZERO_INTERVAL_RECORD * 6)
    struct.pack_into(">dd", naive, 16, first.lower, first.upper)
    struct.pack_into(">dd", naive, 64, second.lower, second.upper)
    assert stream._dense_be_digest(6, records) == hashlib.sha256(naive).hexdigest()


def test_separate_relational_rebuild_reconstructs_every_file_without_promotion(
    relational_receipt: dict[str, object],
) -> None:
    assert relational_receipt["status"] == rebuild.RECEIPT_STATUS
    assert relational_receipt["file_count_reconstructed"] == 206
    assert relational_receipt["total_state_workload"] == 34_787_462
    assert len(relational_receipt["rows"]) == 12
    flags = relational_receipt["flags"]
    assert flags["artifact_parser_implementation_separate"] is True
    assert flags["deterministic_relational_rebuild_complete"] is True
    assert flags["exact_bundle_bytes_reconstructed"] is True
    assert flags["free_axis_geometry_rate_relational_rebuild_complete"] is True
    assert flags["source_box_relational_rebuild_complete"] is True
    assert flags["independent_numerical_implementation"] is False
    assert flags["independent_semantic_replay_complete"] is False
    assert flags["fresh_process"] is False
    for forbidden in (
        "authorizes_scientific_execution",
        "full_operator_bound",
        "killing_contact_geometry_bound",
        "positive_budget_executed",
        "production_resource_gate",
        "science_executed",
        "topology_complete",
    ):
        assert flags[forbidden] is False


def test_rebuild_module_has_static_import_boundary() -> None:
    source_path = Path(rebuild.__file__).resolve()
    tree = ast.parse(source_path.read_text("utf-8"))
    imports = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }
    assert "rate_defined_tensor_f0_production_initial_stream" not in imports
    assert "rate_defined_tensor_f0_physical_initial_source" not in imports
    assert "rate_defined_tensor_f0_packed" not in imports


def test_geometry_bound_packed_axes_retain_join_keys_without_full_operator_promotion(
    geometry_bound_rows: tuple[geometry_bound.GeometryBoundPackedAxes, ...],
) -> None:
    assert len(geometry_bound_rows) == 12
    assert tuple(row.configuration_label for row in geometry_bound_rows) == tuple(
        f0.PHYSICAL_CONFIGURATION_ORDER_V2
    )
    for row in geometry_bound_rows:
        geometry_bound.validate_geometry_bound_packed_axes_structure_only(row)
        assert row.relational_rebuild_receipt_retained is True
        relational = geometry_bound._parse_canonical(
            row.relational_rebuild_receipt_bytes, label="test relational receipt"
        )
        assert relational["receipt_sha256"] == (row.relational_rebuild_receipt_sha256)
        assert row.independent_semantic_receipt_retained is True
        semantic = geometry_bound._parse_canonical(
            row.independent_semantic_receipt_bytes, label="test semantic receipt"
        )
        assert semantic["receipt_sha256"] == (row.independent_semantic_receipt_sha256)
        assert row.canonical_to_native_conversion_bound is True
        assert row.free_axis_operator_geometry_bound is True
        assert row.independent_source_partition_free_axis_semantic_replay_complete is True
        assert row.independent_semantic_replay_complete is False
        assert row.killing_contact_geometry_bound is False
        assert row.full_operator_bound is False
        assert row.propagation_executed is False
        assert row.positive_budget_executed is False
        assert row.production_resource_gate is False
        assert row.f0_pass is False

    even = next(row for row in geometry_bound_rows if row.configuration_label == "E128/Base")
    shifted = next(row for row in geometry_bound_rows if row.configuration_label == "A_Y")
    assert even.tensor_shape == shifted.tensor_shape == (128, 128, 128)
    assert even.axes[2].forward.raw_bytes == shifted.axes[2].forward.raw_bytes
    assert even.partition_sha256s[2] != shifted.partition_sha256s[2]
    assert even.wrapper_binding_sha256 != shifted.wrapper_binding_sha256


def test_geometry_bound_conversion_and_promotion_mutations_fail_closed(
    geometry_bound_rows: tuple[geometry_bound.GeometryBoundPackedAxes, ...],
) -> None:
    row = geometry_bound_rows[2]
    with pytest.raises(geometry_bound.GeometryBoundPackedAxesFailure, match="scope flags"):
        geometry_bound.validate_geometry_bound_packed_axes_structure_only(
            replace(row, independent_semantic_replay_complete=True)
        )
    receipts = list(row.conversion_receipts)
    receipts[0] = {**receipts[0], "native_roundtrip_to_canonical_be": False}
    with pytest.raises(geometry_bound.GeometryBoundPackedAxesFailure, match="receipt relation"):
        geometry_bound.validate_geometry_bound_packed_axes_structure_only(
            replace(row, conversion_receipts=tuple(receipts))
        )
    with pytest.raises(geometry_bound.GeometryBoundPackedAxesFailure, match="wrong exact type"):
        geometry_bound.validate_geometry_bound_packed_axes_structure_only(row.axes)

    replacement_payload = geometry_bound.packed.create_packed_interval_payload(
        tuple((0.0, 0.0) for _ in range(row.axes[0].size)),
        role="science_free_axis_midpoint_forward",
        logical_shape=(row.axes[0].size,),
        nonnegative=True,
        block_size=geometry_bound.VALIDATION_BLOCK_SIZE,
        maximum_working_bytes=geometry_bound.MAXIMUM_WORKING_BYTES,
    )
    swapped_axes = list(row.axes)
    swapped_axes[0] = replace(swapped_axes[0], forward=replacement_payload)
    coherent_receipts = list(row.conversion_receipts)
    changed = dict(coherent_receipts[0])
    changed["destination_native_raw_sha256"] = hashlib.sha256(
        replacement_payload.raw_bytes
    ).hexdigest()
    changed["destination_native_raw_byte_length"] = len(replacement_payload.raw_bytes)
    changed["destination_packed_manifest_sha256"] = geometry_bound._digest(
        b"geometry-bound-packed-destination-manifest-v1\0",
        geometry_bound._packed_manifest_payload(replacement_payload.manifest),
    )
    changed_core = {
        key: value for key, value in changed.items() if key != "conversion_receipt_sha256"
    }
    changed["conversion_receipt_sha256"] = geometry_bound._digest(
        b"geometry-bound-packed-conversion-receipt-v1\0", changed_core
    )
    coherent_receipts[0] = changed
    provisional = replace(
        row,
        axes=tuple(swapped_axes),
        conversion_receipts=tuple(coherent_receipts),
        wrapper_binding_sha256="0" * 64,
    )
    coherent_substitution = replace(
        provisional,
        wrapper_binding_sha256=geometry_bound._digest(
            b"geometry-bound-packed-axes-wrapper-v1\0",
            geometry_bound._wrapper_binding_payload(provisional),
        ),
    )
    with pytest.raises(geometry_bound.GeometryBoundPackedAxesFailure, match="receipt relation"):
        geometry_bound.validate_geometry_bound_packed_axes_structure_only(coherent_substitution)

    even = geometry_bound_rows[1]
    shifted = geometry_bound_rows[10]
    substituted_receipts = list(even.conversion_receipts)
    for receipt_index in (4, 5):
        updated = dict(substituted_receipts[receipt_index])
        updated["partition_sha256"] = shifted.partition_sha256s[2]
        updated["axis_relation_sha256"] = shifted.axis_relation_sha256s[2]
        updated_core = {
            key: value for key, value in updated.items() if key != "conversion_receipt_sha256"
        }
        updated["conversion_receipt_sha256"] = geometry_bound._digest(
            b"geometry-bound-packed-conversion-receipt-v1\0", updated_core
        )
        substituted_receipts[receipt_index] = updated
    provisional = replace(
        even,
        partition_sha256s=(*even.partition_sha256s[:2], shifted.partition_sha256s[2]),
        axis_relation_sha256s=(
            *even.axis_relation_sha256s[:2],
            shifted.axis_relation_sha256s[2],
        ),
        stationary_mass_raw_sha256s=(
            *even.stationary_mass_raw_sha256s[:2],
            shifted.stationary_mass_raw_sha256s[2],
        ),
        conversion_receipts=tuple(substituted_receipts),
        wrapper_binding_sha256="0" * 64,
    )
    same_shape_cut_substitution = replace(
        provisional,
        wrapper_binding_sha256=geometry_bound._digest(
            b"geometry-bound-packed-axes-wrapper-v1\0",
            geometry_bound._wrapper_binding_payload(provisional),
        ),
    )
    with pytest.raises(geometry_bound.GeometryBoundPackedAxesFailure, match="row relation"):
        geometry_bound.validate_geometry_bound_packed_axes_structure_only(
            same_shape_cut_substitution
        )

    midpoint_shift = geometry_bound_rows[8]
    relative_shift = geometry_bound_rows[9]
    whole_row_substitution = replace(
        midpoint_shift,
        configuration_label=relative_shift.configuration_label,
        tensor_shape=relative_shift.tensor_shape,
        row_relation_sha256=relative_shift.row_relation_sha256,
        source_box_relation_sha256=relative_shift.source_box_relation_sha256,
        partition_sha256s=relative_shift.partition_sha256s,
        axis_relation_sha256s=relative_shift.axis_relation_sha256s,
        stationary_mass_raw_sha256s=relative_shift.stationary_mass_raw_sha256s,
        axes=relative_shift.axes,
        conversion_receipts=relative_shift.conversion_receipts,
        wrapper_binding_sha256=relative_shift.wrapper_binding_sha256,
    )
    with pytest.raises(geometry_bound.GeometryBoundPackedAxesFailure, match="row/rebuild join"):
        geometry_bound.validate_geometry_bound_packed_axes_structure_only(whole_row_substitution)


def test_bundle_aware_geometry_verifier_reconstructs_authority(
    production_bundle: Path,
    geometry_bound_rows: tuple[geometry_bound.GeometryBoundPackedAxes, ...],
) -> None:
    assert (
        geometry_bound.verify_geometry_bound_packed_axes(production_bundle, geometry_bound_rows[10])
        == geometry_bound_rows[10]
    )


def test_geometry_bound_module_never_constructs_killing_or_full_kernel() -> None:
    source_path = Path(geometry_bound.__file__).resolve()
    tree = ast.parse(source_path.read_text("utf-8"))
    called_names = {
        node.func.attr if isinstance(node.func, ast.Attribute) else node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, (ast.Attribute, ast.Name))
    }
    assert "build_packed_tensor_kernel" not in called_names
    assert "PackedKernelInputs" not in called_names
    assert "build_physical_killing_intervals_v2" not in called_names


def test_independent_semantic_receipt_has_static_import_boundary_and_scoped_claim(
    geometry_bound_rows: tuple[geometry_bound.GeometryBoundPackedAxes, ...],
) -> None:
    source_path = Path(independent.__file__).resolve()
    tree = ast.parse(source_path.read_text("utf-8"))
    imported_roots = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }
    assert not any(name.startswith("rate_defined_tensor_f0") for name in imported_roots)
    receipt = geometry_bound._parse_canonical(
        geometry_bound_rows[0].independent_semantic_receipt_bytes,
        label="test independent receipt",
    )
    assert receipt["status"] == independent.STATUS
    assert receipt["flags"]["independent_numerical_implementation"] is True
    assert receipt["flags"]["independent_semantic_replay_complete_for_declared_scope"] is True
    assert receipt["flags"]["fresh_process"] is False
    assert receipt["flags"]["full_operator_bound"] is False
    assert receipt["flags"]["killing_contact_geometry_bound"] is False
    assert receipt["flags"]["propagation_executed"] is False
    assert receipt["flags"]["producer_nonpromotion_flags_fail_closed"] is True
    assert receipt["flags"]["producer_positive_semantic_claims_used_as_authority"] is False
    assert sum(row["free_rate_containment_count"] for row in receipt["rows"]) == 10_074
    assert sum(row["initial_marginal_containment_count"] for row in receipt["rows"]) == 5_037
    assert sum(row["active_component_containment_count"] for row in receipt["rows"]) == 722


def test_clean_replay_orchestrator_is_stdlib_only_and_source_pinned() -> None:
    source_path = Path(clean_replay.__file__).resolve()
    tree = ast.parse(source_path.read_text("utf-8"))
    imported_roots = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }
    assert not any(name.startswith("rate_defined_tensor_f0") for name in imported_roots)
    assert clean_replay._verify_sources(REPORT_ROOT) == {
        name: accepted for name, (_, accepted) in clean_replay._source_paths(REPORT_ROOT).items()
    }
    assert clean_replay._OUTER_FLAGS["clean_process_replay_complete_for_declared_scope"] is True
    assert clean_replay._OUTER_FLAGS["independent_backend"] is False
    assert clean_replay._OUTER_FLAGS["full_operator_bound"] is False
    assert clean_replay._OUTER_FLAGS["f0_pass"] is False
    completed = subprocess.run(
        [sys.executable, "-I", str(source_path), "--help"],
        check=False,
        capture_output=True,
        timeout=30,
    )
    assert completed.returncode == 0, completed.stderr.decode("utf-8", errors="replace")


def test_retained_clean_replay_receipt_requires_explicit_pinned_authority() -> None:
    receipt_path = (
        REPORT_ROOT / "artifacts/data/physical_production_initial_clean_process_replay_v1.json"
    )
    assert hashlib.sha256(Path(clean_replay.__file__).read_bytes()).hexdigest() == (
        "d8d6793519e64e662e612dddcf7f97074249850029423056e073ff3c11a76a38"
    )
    receipt_bytes = receipt_path.read_bytes()
    assert hashlib.sha256(receipt_bytes).hexdigest() == (
        "e1b25ab5221434e26749e9b2103c04c36e27539a810e2a15c236c1806b333891"
    )
    receipt = json.loads(receipt_bytes)
    accepted = "f33dd0b2695464370e29a2896d3753e753525d9cf5d38b5917a616181096bf9b"
    clean_replay.validate_clean_process_replay_receipt(
        REPORT_ROOT,
        receipt,
        expected_receipt_sha256=accepted,
    )
    rewritten = copy.deepcopy(receipt)
    rewritten["evidence"]["rows"][0]["wrapper_binding_sha256"] = "0" * 64
    evidence_sha = clean_replay._digest(
        b"production-initial-clean-replay-evidence-v1\0", rewritten["evidence"]
    )
    rewritten["repeat_evidence_sha256s"] = [evidence_sha] * clean_replay.REPEAT_COUNT
    core = {key: value for key, value in rewritten.items() if key != "receipt_sha256"}
    rewritten["receipt_sha256"] = clean_replay._digest(
        b"production-initial-clean-process-replay-v1\0", core
    )
    with pytest.raises(clean_replay.CleanProcessReplayFailure, match="not the pinned result"):
        clean_replay.validate_clean_process_replay_receipt(
            REPORT_ROOT,
            rewritten,
            expected_receipt_sha256=accepted,
        )


def test_isolated_process_rebuild_writes_same_deterministic_receipt(
    production_bundle: Path,
    relational_receipt: dict[str, object],
    tmp_path: Path,
) -> None:
    receipt_path = tmp_path / "receipt.json"
    script = Path(rebuild.__file__).resolve()
    completed = subprocess.run(
        [
            sys.executable,
            "-I",
            str(script),
            "--bundle",
            str(production_bundle),
            "--receipt",
            str(receipt_path),
        ],
        check=False,
        capture_output=True,
        text=True,
        timeout=90,
    )
    assert completed.returncode == 0, completed.stderr
    observed = receipt_path.read_bytes()
    assert observed == stream._canonical_json_bytes(relational_receipt)
    assert relational_receipt["receipt_sha256"] in completed.stdout


def test_one_byte_endian_and_symlink_mutations_fail_closed(
    production_bundle: Path, tmp_path: Path
) -> None:
    mutated = tmp_path / "mutated"
    shutil.copytree(production_bundle, mutated)
    manifest = _bundle_manifest(mutated)
    raw_entry = next(
        entry for entry in manifest["file_inventory"] if entry["path"].endswith(".be64")
    )
    raw_path = mutated / raw_entry["path"]
    original = raw_path.read_bytes()
    raw_path.write_bytes(bytes([original[0] ^ 1]) + original[1:])
    with pytest.raises(stream.ProductionInitialStreamFailure, match="file bytes changed"):
        stream.verify_bundle(mutated)

    linked = tmp_path / "linked"
    shutil.copytree(production_bundle, linked)
    linked_manifest = _bundle_manifest(linked)
    first_raw = next(
        entry for entry in linked_manifest["file_inventory"] if entry["path"].endswith(".be64")
    )
    second_raw = next(
        entry
        for entry in linked_manifest["file_inventory"]
        if entry["path"].endswith(".be64") and entry["path"] != first_raw["path"]
    )
    link_path = linked / first_raw["path"]
    link_path.unlink()
    link_path.symlink_to(linked / second_raw["path"])
    with pytest.raises(stream.ProductionInitialStreamFailure, match="symlink"):
        stream.verify_bundle(linked)


def test_sparse_record_reordering_and_endian_substitution_fail_closed(
    production_bundle: Path,
) -> None:
    row = _row_manifest(production_bundle, "O129/Base")
    sparse_manifest = row["sparse_component_box"]
    raw = (production_bundle / sparse_manifest["file"]["path"]).read_bytes()
    header = raw[: stream.SPARSE_HEADER.size]
    records = [
        raw[offset : offset + stream.SPARSE_RECORD.size]
        for offset in range(stream.SPARSE_HEADER.size, len(raw), stream.SPARSE_RECORD.size)
    ]
    assert len(records) >= 2
    reordered = header + records[1] + records[0] + b"".join(records[2:])
    attacker_manifest = copy.deepcopy(sparse_manifest)
    attacker_manifest["file"]["byte_length"] = len(reordered)
    attacker_manifest["file"]["sha256"] = hashlib.sha256(reordered).hexdigest()
    with pytest.raises(stream.ProductionInitialStreamFailure, match="record is invalid"):
        stream._parse_sparse_raw(reordered, attacker_manifest)

    endian = bytearray(raw)
    start = stream.SPARSE_HEADER.size
    endian[start : start + 8] = reversed(endian[start : start + 8])
    attacker_manifest = copy.deepcopy(sparse_manifest)
    attacker_manifest["file"]["sha256"] = hashlib.sha256(endian).hexdigest()
    with pytest.raises(stream.ProductionInitialStreamFailure):
        stream._parse_sparse_raw(bytes(endian), attacker_manifest)


def test_coherently_rehashed_row_promotion_is_rejected_by_both_verifiers(
    production_bundle: Path, tmp_path: Path
) -> None:
    attacker = tmp_path / "promoted"
    shutil.copytree(production_bundle, attacker)
    bundle = _bundle_manifest(attacker)
    summary = next(row for row in bundle["rows"] if row["configuration_label"] == "O129/Base")
    row_path = attacker / summary["row_manifest"]["path"]
    row = json.loads(row_path.read_text("ascii"))
    row["flags"]["independent_source_box_replay"] = True
    row_bytes = stream._canonical_json_bytes(row)
    row_path.write_bytes(row_bytes)
    row_sha = hashlib.sha256(row_bytes).hexdigest()
    summary["row_manifest"]["byte_length"] = len(row_bytes)
    summary["row_manifest"]["sha256"] = row_sha
    inventory_entry = next(
        entry
        for entry in bundle["file_inventory"]
        if entry["path"] == summary["row_manifest"]["path"]
    )
    inventory_entry["byte_length"] = len(row_bytes)
    inventory_entry["sha256"] = row_sha
    (attacker / "bundle.json").write_bytes(stream._canonical_json_bytes(bundle))
    with pytest.raises(stream.ProductionInitialStreamFailure, match="summary binding"):
        stream.verify_bundle(attacker)
    with pytest.raises(rebuild.ProductionInitialRebuildFailure, match="byte mismatch"):
        rebuild.rebuild_bundle(attacker)


def test_unknown_root_promotion_flag_fails_before_scientific_reconstruction(
    production_bundle: Path, tmp_path: Path
) -> None:
    attacker = tmp_path / "root-promoted"
    shutil.copytree(production_bundle, attacker)
    bundle = _bundle_manifest(attacker)
    bundle["f0_pass"] = True
    (attacker / "bundle.json").write_bytes(stream._canonical_json_bytes(bundle))
    with pytest.raises(stream.ProductionInitialStreamFailure, match="bundle manifest key set"):
        stream.verify_bundle(attacker)
    with pytest.raises(independent.IndependentSemanticFailure, match="bundle manifest key set"):
        independent.verify_bundle_independently(attacker)


def test_unknown_row_promotion_key_fails_all_three_readers(
    production_bundle: Path, tmp_path: Path
) -> None:
    attacker = tmp_path / "row-extra-key"
    shutil.copytree(production_bundle, attacker)
    bundle = _bundle_manifest(attacker)
    summary = bundle["rows"][0]
    row_path = attacker / summary["row_manifest"]["path"]
    row = json.loads(row_path.read_text("ascii"))
    row["f0_pass"] = True
    row_bytes = stream._canonical_json_bytes(row)
    row_path.write_bytes(row_bytes)
    row_sha = hashlib.sha256(row_bytes).hexdigest()
    summary["row_manifest"]["byte_length"] = len(row_bytes)
    summary["row_manifest"]["sha256"] = row_sha
    inventory_entry = next(
        entry
        for entry in bundle["file_inventory"]
        if entry["path"] == summary["row_manifest"]["path"]
    )
    inventory_entry["byte_length"] = len(row_bytes)
    inventory_entry["sha256"] = row_sha
    (attacker / "bundle.json").write_bytes(stream._canonical_json_bytes(bundle))
    with pytest.raises(stream.ProductionInitialStreamFailure, match="row manifest key set"):
        stream.verify_bundle(attacker)
    with pytest.raises(rebuild.ProductionInitialRebuildFailure, match="byte mismatch"):
        rebuild.rebuild_bundle(attacker)
    with pytest.raises(independent.IndependentSemanticFailure, match="row manifest key set"):
        independent.verify_bundle_independently(attacker)


def test_unreferenced_inventory_sidecar_is_rejected(
    production_bundle: Path, tmp_path: Path
) -> None:
    attacker = tmp_path / "inventory-sidecar"
    shutil.copytree(production_bundle, attacker)
    bundle = _bundle_manifest(attacker)
    sidecar = b"not part of the canonical evidence graph\n"
    (attacker / "zzz-unreferenced.bin").write_bytes(sidecar)
    bundle["file_inventory"].append(
        {
            "byte_length": len(sidecar),
            "path": "zzz-unreferenced.bin",
            "sha256": hashlib.sha256(sidecar).hexdigest(),
        }
    )
    (attacker / "bundle.json").write_bytes(stream._canonical_json_bytes(bundle))
    with pytest.raises(stream.ProductionInitialStreamFailure, match="file inventory"):
        stream.verify_bundle(attacker)
    with pytest.raises(independent.IndependentSemanticFailure, match="bundle inventory"):
        independent.verify_bundle_independently(attacker)


def test_duplicate_same_byte_pointer_cannot_hide_unreferenced_sidecar(
    production_bundle: Path, tmp_path: Path
) -> None:
    attacker = tmp_path / "duplicate-pointer-sidecar"
    shutil.copytree(production_bundle, attacker)
    bundle = _bundle_manifest(attacker)
    source_summary = next(
        row for row in bundle["rows"] if row["configuration_label"] == "E128/Base"
    )
    target_summary = next(row for row in bundle["rows"] if row["configuration_label"] == "A_Y")
    source_row = json.loads((attacker / source_summary["row_manifest"]["path"]).read_text("ascii"))
    target_row_path = attacker / target_summary["row_manifest"]["path"]
    target_row = json.loads(target_row_path.read_text("ascii"))
    source_axis = next(
        axis for axis in source_row["axes"] if axis["coordinate"] == "relative_perpendicular"
    )
    target_axis = next(
        axis for axis in target_row["axes"] if axis["coordinate"] == "relative_perpendicular"
    )
    source_file = copy.deepcopy(source_axis["rates"]["forward"]["file"])
    target_file = target_axis["rates"]["forward"]["file"]
    assert source_file["sha256"] == target_file["sha256"]
    assert (attacker / source_file["path"]).read_bytes() == (
        attacker / target_file["path"]
    ).read_bytes()
    target_axis["rates"]["forward"]["file"] = source_file
    target_row_bytes = stream._canonical_json_bytes(target_row)
    target_row_path.write_bytes(target_row_bytes)
    target_row_sha = hashlib.sha256(target_row_bytes).hexdigest()
    target_summary["row_manifest"]["byte_length"] = len(target_row_bytes)
    target_summary["row_manifest"]["sha256"] = target_row_sha
    row_inventory = next(
        entry
        for entry in bundle["file_inventory"]
        if entry["path"] == target_summary["row_manifest"]["path"]
    )
    row_inventory["byte_length"] = len(target_row_bytes)
    row_inventory["sha256"] = target_row_sha
    (attacker / target_file["path"]).unlink()
    bundle["file_inventory"] = [
        entry for entry in bundle["file_inventory"] if entry["path"] != target_file["path"]
    ]
    sidecar = b"unreferenced replacement preserving the inventory count\n"
    sidecar_path = "zzz-unreferenced-replacement.bin"
    (attacker / sidecar_path).write_bytes(sidecar)
    bundle["file_inventory"].append(
        {
            "byte_length": len(sidecar),
            "path": sidecar_path,
            "sha256": hashlib.sha256(sidecar).hexdigest(),
        }
    )
    bundle["file_inventory"].sort(key=lambda entry: entry["path"])
    assert len(bundle["file_inventory"]) == 206
    (attacker / "bundle.json").write_bytes(stream._canonical_json_bytes(bundle))
    with pytest.raises(stream.ProductionInitialStreamFailure, match="duplicate bound file"):
        stream.verify_bundle(attacker)
    with pytest.raises(independent.IndependentSemanticFailure, match="duplicate bound file"):
        independent.verify_bundle_independently(attacker)


def test_coherently_rehashed_noncanonical_source_bytes_fail_closed(
    production_bundle: Path, tmp_path: Path
) -> None:
    attacker = tmp_path / "noncanonical-source"
    shutil.copytree(production_bundle, attacker)
    bundle = _bundle_manifest(attacker)
    source_relative = "request/analytic_source.json"
    source_path = attacker / source_relative
    replacement = source_path.read_bytes() + b"\n"
    source_path.write_bytes(replacement)
    inventory_entry = next(
        entry for entry in bundle["file_inventory"] if entry["path"] == source_relative
    )
    inventory_entry["byte_length"] = len(replacement)
    inventory_entry["sha256"] = hashlib.sha256(replacement).hexdigest()
    (attacker / "bundle.json").write_bytes(stream._canonical_json_bytes(bundle))
    with pytest.raises(stream.ProductionInitialStreamFailure, match="request-only source"):
        stream.verify_bundle(attacker)
    with pytest.raises(rebuild.ProductionInitialRebuildFailure, match="request-only root bytes"):
        rebuild.rebuild_bundle(attacker)


def test_coherently_rehashed_same_shape_periodic_cut_substitution_fails_rederivation(
    production_bundle: Path, tmp_path: Path
) -> None:
    attacker = tmp_path / "cut-substitution"
    shutil.copytree(production_bundle, attacker)
    bundle = _bundle_manifest(attacker)
    even_summary = next(row for row in bundle["rows"] if row["configuration_label"] == "E128/Base")
    shifted_summary = next(row for row in bundle["rows"] if row["configuration_label"] == "A_Y")
    even_row_path = attacker / even_summary["row_manifest"]["path"]
    shifted_row_path = attacker / shifted_summary["row_manifest"]["path"]
    even_row = json.loads(even_row_path.read_text("ascii"))
    shifted_row = json.loads(shifted_row_path.read_text("ascii"))
    even_axis = next(
        axis for axis in even_row["axes"] if axis["coordinate"] == "relative_perpendicular"
    )
    shifted_axis = next(
        axis for axis in shifted_row["axes"] if axis["coordinate"] == "relative_perpendicular"
    )
    target_partition = attacker / even_axis["partition_file"]["path"]
    source_partition = attacker / shifted_axis["partition_file"]["path"]
    replacement = source_partition.read_bytes()
    target_partition.write_bytes(replacement)
    replacement_sha = hashlib.sha256(replacement).hexdigest()
    even_axis["partition_file"]["byte_length"] = len(replacement)
    even_axis["partition_file"]["sha256"] = replacement_sha
    partition_inventory = next(
        entry
        for entry in bundle["file_inventory"]
        if entry["path"] == even_axis["partition_file"]["path"]
    )
    partition_inventory["byte_length"] = len(replacement)
    partition_inventory["sha256"] = replacement_sha
    even_axis["axis_relation_sha256"] = stream._domain_digest(
        b"production-initial-axis-geometry-rate-relation-v1\0",
        {
            "coordinate": "relative_perpendicular",
            "partition_sha256": replacement_sha,
            "rate_raw_sha256s": {
                name: even_axis["rates"][name]["file"]["sha256"]
                for name in sorted(even_axis["rates"])
            },
        },
    )
    even_row["row_relation_sha256"] = stream._domain_digest(
        b"production-initial-row-relation-v1\0",
        {
            "axis_relation_sha256s": [axis["axis_relation_sha256"] for axis in even_row["axes"]],
            "configuration_index": even_row["configuration_index"],
            "configuration_label": even_row["configuration_label"],
            "source_box_relation_sha256": even_row["source_box_relation_sha256"],
        },
    )
    even_row_bytes = stream._canonical_json_bytes(even_row)
    even_row_path.write_bytes(even_row_bytes)
    even_row_sha = hashlib.sha256(even_row_bytes).hexdigest()
    even_summary["row_manifest"]["byte_length"] = len(even_row_bytes)
    even_summary["row_manifest"]["sha256"] = even_row_sha
    even_summary["row_relation_sha256"] = even_row["row_relation_sha256"]
    row_inventory = next(
        entry
        for entry in bundle["file_inventory"]
        if entry["path"] == even_summary["row_manifest"]["path"]
    )
    row_inventory["byte_length"] = len(even_row_bytes)
    row_inventory["sha256"] = even_row_sha
    bundle["family_relation_sha256"] = stream._domain_digest(
        b"production-initial-family-relation-v1\0",
        {
            "analytic_source_sha256": stream.ACCEPTED_ANALYTIC_SOURCE_SHA256,
            "configuration_sha256": stream.ACCEPTED_CONFIGURATION_SHA256,
            "ordered_row_relation_sha256s": [row["row_relation_sha256"] for row in bundle["rows"]],
        },
    )
    (attacker / "bundle.json").write_bytes(stream._canonical_json_bytes(bundle))
    with pytest.raises(stream.ProductionInitialStreamFailure, match="accepted row"):
        stream.verify_bundle(attacker)
    with pytest.raises(rebuild.ProductionInitialRebuildFailure, match="byte mismatch"):
        rebuild.rebuild_bundle(attacker)
