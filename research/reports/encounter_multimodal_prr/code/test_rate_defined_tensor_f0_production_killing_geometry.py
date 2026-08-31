from __future__ import annotations

import ast
import copy
import hashlib
import json
import math
import os
import shutil
import struct
from pathlib import Path

import pytest
import rate_defined_tensor_f0_production_killing_geometry as geometry

REPORT_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def deterministic_bundles(
    tmp_path_factory: pytest.TempPathFactory,
) -> tuple[Path, Path]:
    root = tmp_path_factory.mktemp("production-killing-geometry")
    first = root / "first"
    second = root / "second"
    first_manifest = geometry.produce_bundle(REPORT_ROOT, first)
    second_manifest = geometry.produce_bundle(REPORT_ROOT, second)
    assert first_manifest["status"] == geometry.STATUS
    assert second_manifest == first_manifest
    return first, second


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text("ascii"))


def _bundle_manifest(root: Path) -> dict[str, object]:
    return _load_json(root / "bundle.json")


def _row_manifests(root: Path) -> list[dict[str, object]]:
    manifest = _bundle_manifest(root)
    return [_load_json(root / summary["row_manifest"]["path"]) for summary in manifest["rows"]]


def _tree_payloads(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def _fraction(value: str) -> geometry.Fraction:
    return geometry._parse_fraction_text(value, label="test exact fraction")


def _replace_inventory_entry(manifest: dict[str, object], entry: dict[str, object]) -> None:
    matches = [
        index
        for index, current in enumerate(manifest["file_inventory"])
        if current["path"] == entry["path"]
    ]
    assert len(matches) == 1
    manifest["file_inventory"][matches[0]] = entry


def _rewrite_row_manifest(
    root: Path,
    manifest: dict[str, object],
    row_index: int,
    row: dict[str, object],
) -> dict[str, object]:
    summary = manifest["rows"][row_index]
    relative = summary["row_manifest"]["path"]
    payload = geometry._canonical_json_bytes(row)
    (root / relative).write_bytes(payload)
    entry = geometry._file_entry(relative, payload)
    summary["row_manifest"] = entry
    _replace_inventory_entry(manifest, entry)
    return entry


def test_canonical_source_and_all_runtime_dependencies_are_exactly_pinned() -> None:
    source_path = REPORT_ROOT / geometry.KILLING_SOURCE_RELATIVE_PATH
    source_bytes = source_path.read_bytes()
    assert hashlib.sha256(source_bytes).hexdigest() == geometry.ACCEPTED_KILLING_SOURCE_SHA256
    source_payload = geometry._parse_canonical_json(source_bytes, label="test source")
    source = geometry._validate_source(source_payload)
    assert source.radius == _fraction("5764607523034235/36028797018963968")
    assert source.support_half_width == _fraction("5764607523034235/144115188075855872")
    assert len(source.support_centres) == 4
    assert geometry._SOURCE_PINS == {
        "configuration": {
            "path": "artifacts/data/physical_configuration_family_control_free_v1.json",
            "sha256": "063913c7fbc2b706ba85a0e3f06005bad23a2292749817294cbf41f5cdce4084",
        },
        "f0_core": {
            "path": "code/rate_defined_tensor_f0.py",
            "sha256": "321f12aa8a5df44ca9c9162704cccd0f2c526abf9577832b4824538b0afdb8e5",
        },
        "killing_geometry_source": {
            "path": "artifacts/data/physical_killing_geometry_source_v1.json",
            "sha256": "5543f76031d731cb5bcf3e4cdf3bdabaffacb2053400e3015d6ab57906a27669",
        },
        "partition_bundle_manifest": {
            "path": "artifacts/data/physical_production_initial_stream_v1/bundle.json",
            "sha256": "5d81d1c02ec2484f0b3d5fab3a825cf6f6331f7d3e4cc8dae224266201dfbd9e",
        },
        "production_initial_stream": {
            "path": "code/rate_defined_tensor_f0_production_initial_stream.py",
            "sha256": "2871976855a0c598b26b8d83b33f4ea3a027a2c826ccdb2ad9b678761093e6cb",
        },
    }
    geometry._verify_runtime_source_pins(REPORT_ROOT)


def test_full_bundle_has_exact_counts_inventory_graph_and_nonpromotion_flags(
    deterministic_bundles: tuple[Path, Path],
) -> None:
    first, _ = deterministic_bundles
    manifest = geometry.verify_bundle(REPORT_ROOT, first)
    assert manifest["configuration_count"] == 12
    assert len(manifest["rows"]) == 12
    assert len(manifest["file_inventory"]) == 75
    assert manifest["method"]["contact_active_cell_count_definition"] == (
        "saved_interval_upper_endpoint_strictly_positive"
    )
    assert manifest["method"]["contact_full_cell_count_definition"] == (
        "every_corner_of_every_exact_partition_segment_inside_or_on_contact_disk"
    )
    assert manifest["method"]["contact_full_cell_serialization"] == (
        "exact_[1,1]_after_exact_rational_corner_classification"
    )
    assert manifest["factorization_contract"] == geometry._FACTORIZATION_CONTRACT
    assert manifest["factorization_contract_sha256"] == (geometry.FACTORIZATION_CONTRACT_SHA256)
    assert manifest["method"]["factorization_contract_sha256"] == (
        geometry.FACTORIZATION_CONTRACT_SHA256
    )
    assert manifest["method"]["same_mpfr_backend_anchor_is_independent"] is False
    contract = manifest["factorization_contract"]
    assert contract["full_flat_index_formula"] == "i=(i_M*n_R+i_R)*n_Y+i_Y"
    assert contract["contact_flat_index_formula"] == "a*n_Y+b"
    assert contract["factorized_basis_formula"] == "H_j[i_M,a,b]=Phi_j[i_M]*C[a,b]"
    assert contract["budget_and_weights_present"] is False
    assert [entry["profile_index"] for entry in contract["ordered_profile_mapping"]] == [
        0,
        1,
        2,
        3,
    ]
    totals = manifest["totals"]
    assert totals["contact_fraction_records"] == 233_139
    assert totals["contact_fraction_raw_bytes"] == 3_730_224
    assert totals["midpoint_cells"] == 1_713
    assert totals["raw_interval_bytes"] == 3_839_856
    assert totals["raw_interval_records"] == 239_991
    assert totals["support_density_records"] == 6_852
    assert totals["support_density_raw_bytes"] == 109_632
    assert totals["support_profile_count"] == 48
    assert totals["active_contact_cell_count"] == 5_446
    assert totals["full_contact_cell_count"] == 4_142
    assert sum(row["contact_fraction_records"] for row in manifest["rows"]) == 233_139
    assert sum(row["midpoint_cells"] for row in manifest["rows"]) == 1_713
    assert sum(row["support_density_records"] for row in manifest["rows"]) == 6_852
    assert (
        sum(row["active_contact_cell_count"] for row in manifest["rows"])
        == totals["active_contact_cell_count"]
    )
    assert (
        sum(row["full_contact_cell_count"] for row in manifest["rows"])
        == totals["full_contact_cell_count"]
    )
    assert manifest["flags"] == geometry._BUNDLE_FLAGS
    assert manifest["flags"]["producer_consistent_control_free_killing_geometry_all_rows"]
    assert manifest["source_pins"]["producer"] == {
        "path": "code/rate_defined_tensor_f0_production_killing_geometry.py",
        "sha256": hashlib.sha256(Path(geometry.__file__).read_bytes()).hexdigest(),
    }
    assert manifest["flags"]["same_core_producer_consistency_only"] is True
    for forbidden in (
        "authorizes_scientific_execution",
        "concrete_killing_constructed",
        "continuum_verified",
        "f0_pass",
        "full_operator_bound",
        "independent_killing_geometry_replay_complete",
        "positive_budget_executed",
        "production_resource_gate",
        "propagation_executed",
        "science_executed",
        "single_physical_operator_bound",
        "topology_complete",
    ):
        assert manifest["flags"][forbidden] is False
    actual_files = {
        path.relative_to(first).as_posix() for path in first.rglob("*") if path.is_file()
    }
    inventory_files = {entry["path"] for entry in manifest["file_inventory"]}
    assert actual_files == inventory_files | {"bundle.json"}
    assert all(row["support_profile_count"] == 4 for row in manifest["rows"])


def test_every_contact_and_support_interval_range_and_mass_gate(
    deterministic_bundles: tuple[Path, Path],
) -> None:
    first, _ = deterministic_bundles
    contact_records = 0
    support_records = 0
    periodic_split_contact_cells = 0
    for row in _row_manifests(first):
        assert row["flags"] == geometry._ROW_FLAGS
        assert row["gates"] == geometry._ROW_GATES
        assert row["status"] == geometry.ROW_STATUS
        assert row["factorization_contract_sha256"] == (geometry.FACTORIZATION_CONTRACT_SHA256)
        for forbidden in (
            "authorizes_scientific_execution",
            "concrete_killing_constructed",
            "contains_budget_value",
            "contains_control_values",
            "continuum_verified",
            "f0_pass",
            "full_operator_bound",
            "independent_killing_geometry_replay",
            "positive_budget_executed",
            "production_resource_gate",
            "propagation_executed",
            "science_executed",
            "single_physical_operator_bound",
            "topology_complete",
        ):
            assert row["flags"][forbidden] is False
        assert row["partition_source"]["bundle_manifest_sha256"] == (
            geometry.ACCEPTED_PARTITION_BUNDLE_SHA256
        )
        assert len(row["partition_source"]["partitions"]) == 3
        assert [entry["coordinate"] for entry in row["partition_source"]["partitions"]] == [
            "midpoint",
            "relative_parallel",
            "relative_perpendicular",
        ]

        contact = row["contact_fraction_relative"]
        raw = (first / contact["file"]["path"]).read_bytes()
        assert contact["manifest"]["record_format"] == ">dd"
        assert contact["manifest"]["logical_shape"] == row["shape"][1:]
        assert len(raw) == 16 * math.prod(row["shape"][1:])
        decoded_contact = [
            struct.unpack_from(">dd", raw, offset) for offset in range(0, len(raw), 16)
        ]
        assert all(
            math.isfinite(lower)
            and math.isfinite(upper)
            and not (lower == 0.0 and math.copysign(1.0, lower) < 0)
            and not (upper == 0.0 and math.copysign(1.0, upper) < 0)
            and 0.0 <= lower <= upper <= 1.0
            for lower, upper in decoded_contact
        )
        assert any(upper == 0.0 for _, upper in decoded_contact)
        assert any(upper > 0.0 for _, upper in decoded_contact)
        assert any(0.0 < upper < 1.0 for _, upper in decoded_contact)
        assert 0 < contact["full_cell_count"] < contact["active_cell_count"] < len(decoded_contact)
        assert sum(pair == (1.0, 1.0) for pair in decoded_contact) == contact["full_cell_count"]
        assert row["gates"]["geometrically_full_contact_cells_are_exact_unit_intervals"]
        transverse_binding = next(
            entry
            for entry in row["partition_source"]["partitions"]
            if entry["coordinate"] == "relative_perpendicular"
        )
        transverse_partition = _load_json(
            REPORT_ROOT
            / geometry.PARTITION_BUNDLE_DIRECTORY_RELATIVE_PATH
            / transverse_binding["file"]["path"]
        )
        split_indices = [
            index
            for index, segments in enumerate(transverse_partition["cell_segments_exact"])
            if len(segments) == 2
        ]
        for parallel_index in range(row["shape"][1]):
            for transverse_index in split_indices:
                flat = parallel_index * row["shape"][2] + transverse_index
                assert decoded_contact[flat] == (0.0, 0.0)
                periodic_split_contact_cells += 1
        area = contact["area_enclosure_exact"]
        area_lower = _fraction(area["lower_exact"])
        area_upper = _fraction(area["upper_exact"])
        assert 0 < area_lower <= area_upper < 1
        contact_quality = contact["quality_ledger"]
        analytic_area = contact_quality["analytic_area_enclosure_exact"]
        assert area_lower <= _fraction(analytic_area["lower_exact"])
        assert _fraction(analytic_area["upper_exact"]) <= area_upper
        assert contact_quality["aggregate_contains_analytic_enclosure"] is True
        assert contact_quality["independent_backend"] is False
        assert _fraction(contact_quality["aggregate_width_over_radius_squared_exact"]) <= _fraction(
            contact_quality["aggregate_width_over_radius_squared_cap_exact"]
        )
        assert _fraction(contact_quality["analytic_width_over_radius_squared_exact"]) <= _fraction(
            contact_quality["analytic_width_over_radius_squared_cap_exact"]
        )
        contact_records += len(decoded_contact)

        assert len(row["support_densities"]) == 4
        for profile_index, support in enumerate(row["support_densities"]):
            assert support["profile_index"] == profile_index
            support_raw = (first / support["file"]["path"]).read_bytes()
            assert support["manifest"]["record_format"] == ">dd"
            assert support["manifest"]["logical_shape"] == [row["shape"][0]]
            decoded_support = [
                struct.unpack_from(">dd", support_raw, offset)
                for offset in range(0, len(support_raw), 16)
            ]
            assert len(decoded_support) == row["shape"][0]
            assert all(
                math.isfinite(lower)
                and math.isfinite(upper)
                and not (lower == 0.0 and math.copysign(1.0, lower) < 0)
                and not (upper == 0.0 and math.copysign(1.0, upper) < 0)
                and 0.0 <= lower <= upper
                for lower, upper in decoded_support
            )
            assert any(upper == 0.0 for _, upper in decoded_support)
            assert any(upper > 0.0 for _, upper in decoded_support)
            integral = support["integral_enclosure_exact"]
            assert _fraction(integral["lower_exact"]) <= 1 <= _fraction(integral["upper_exact"])
            quality = support["quality_ledger"]
            assert quality["analytic_mass_exact"] == "1/1"
            assert quality["support_strictly_inside_midpoint_domain"] is True
            assert _fraction(quality["midpoint_domain_lower_exact"]) < _fraction(
                quality["support_lower_exact"]
            )
            assert _fraction(quality["support_upper_exact"]) < _fraction(
                quality["midpoint_domain_upper_exact"]
            )
            assert _fraction(quality["integral_width_exact"]) <= _fraction(
                quality["integral_width_cap_exact"]
            )
            support_records += len(decoded_support)
    assert contact_records == 233_139
    assert support_records == 6_852
    assert periodic_split_contact_cells == 257


def test_exact_full_canonicalization_handles_equality_split_and_volume_closure() -> None:
    f0 = geometry.f0
    zero = f0.ZERO_INTERVAL
    one = f0.ONE_INTERVAL

    parallel = f0.TensorAxis(
        name="relative_parallel",
        size=2,
        periodic=False,
        positions=(geometry.Fraction(3, 10), geometry.Fraction(9, 10)),
        cell_volumes=(geometry.Fraction(3, 5), geometry.Fraction(3, 5)),
        cell_segments=(
            ((geometry.Fraction(0), geometry.Fraction(3, 5)),),
            ((geometry.Fraction(3, 5), geometry.Fraction(6, 5)),),
        ),
        forward_rates=(one, zero),
        backward_rates=(zero, one),
        stationary_masses=(one, one),
        domain_start=geometry.Fraction(0),
        domain_width=geometry.Fraction(6, 5),
        periodic_shift=geometry.Fraction(0),
        construction="synthetic_reflecting_for_exact_full_test",
    )
    perpendicular = f0.TensorAxis(
        name="relative_perpendicular",
        size=2,
        periodic=True,
        positions=(geometry.Fraction(2, 5), geometry.Fraction(6, 5)),
        cell_volumes=(geometry.Fraction(4, 5), geometry.Fraction(4, 5)),
        cell_segments=(
            ((geometry.Fraction(0), geometry.Fraction(4, 5)),),
            ((geometry.Fraction(4, 5), geometry.Fraction(8, 5)),),
        ),
        forward_rates=(one, one),
        backward_rates=(one, one),
        stationary_masses=(one, one),
        domain_start=geometry.Fraction(0),
        domain_width=geometry.Fraction(8, 5),
        periodic_shift=geometry.Fraction(0),
        construction="synthetic_periodic_for_exact_full_test",
    )
    padded_one = f0.OutwardInterval(float.fromhex("0x1.fffffffffffffp-1"), 1.0)
    canonical = geometry._canonicalize_full_contact_intervals(
        (padded_one, zero, zero, zero),
        parallel,
        perpendicular,
        geometry.Fraction(1),
    )
    assert canonical[0] == one
    assert canonical[1:] == (zero, zero, zero)

    split_perpendicular = f0.TensorAxis(
        name="relative_perpendicular",
        size=2,
        periodic=True,
        positions=(geometry.Fraction(0), geometry.Fraction(1, 2)),
        cell_volumes=(geometry.Fraction(2, 5), geometry.Fraction(3, 5)),
        cell_segments=(
            (
                (geometry.Fraction(0), geometry.Fraction(1, 5)),
                (geometry.Fraction(4, 5), geometry.Fraction(1)),
            ),
            ((geometry.Fraction(1, 5), geometry.Fraction(4, 5)),),
        ),
        forward_rates=(one, one),
        backward_rates=(one, one),
        stationary_masses=(one, one),
        domain_start=geometry.Fraction(0),
        domain_width=geometry.Fraction(1),
        periodic_shift=geometry.Fraction(0),
        construction="synthetic_split_periodic_for_exact_full_test",
    )
    partial = f0.OutwardInterval(0.5, 1.0)
    split_canonical = geometry._canonicalize_full_contact_intervals(
        (partial, padded_one, zero, zero),
        parallel,
        split_perpendicular,
        geometry.Fraction(1),
    )
    assert split_canonical[0] is partial
    assert split_canonical[1] == one

    broken_volume = f0.TensorAxis(
        name=split_perpendicular.name,
        size=split_perpendicular.size,
        periodic=split_perpendicular.periodic,
        positions=split_perpendicular.positions,
        cell_volumes=(geometry.Fraction(1, 3), geometry.Fraction(3, 5)),
        cell_segments=split_perpendicular.cell_segments,
        forward_rates=split_perpendicular.forward_rates,
        backward_rates=split_perpendicular.backward_rates,
        stationary_masses=split_perpendicular.stationary_masses,
        domain_start=split_perpendicular.domain_start,
        domain_width=split_perpendicular.domain_width,
        periodic_shift=split_perpendicular.periodic_shift,
        construction=split_perpendicular.construction,
    )
    with pytest.raises(geometry.ProductionKillingGeometryFailure, match="volume closure"):
        geometry._canonicalize_full_contact_intervals(
            (partial, padded_one, zero, zero),
            parallel,
            broken_volume,
            geometry.Fraction(1),
        )


def test_two_complete_rebuilds_are_byte_identical(
    deterministic_bundles: tuple[Path, Path],
) -> None:
    first, second = deterministic_bundles
    first_payloads = _tree_payloads(first)
    second_payloads = _tree_payloads(second)
    assert first_payloads == second_payloads
    assert (
        hashlib.sha256(first_payloads["bundle.json"]).hexdigest()
        == hashlib.sha256(second_payloads["bundle.json"]).hexdigest()
    )


def test_existing_output_is_never_overwritten(
    deterministic_bundles: tuple[Path, Path], tmp_path: Path
) -> None:
    first, _ = deterministic_bundles
    before = hashlib.sha256((first / "bundle.json").read_bytes()).hexdigest()
    with pytest.raises(geometry.ProductionKillingGeometryFailure, match="already exists"):
        geometry.produce_bundle(REPORT_ROOT, first)
    assert hashlib.sha256((first / "bundle.json").read_bytes()).hexdigest() == before

    occupied = tmp_path / "occupied"
    occupied.mkdir()
    marker = occupied / "user-owned"
    marker.write_bytes(b"preserve\n")
    with pytest.raises(geometry.ProductionKillingGeometryFailure, match="already exists"):
        geometry.produce_bundle(REPORT_ROOT, occupied)
    assert marker.read_bytes() == b"preserve\n"

    dangling = tmp_path / "dangling-output-link"
    dangling.symlink_to(tmp_path / "absent-target", target_is_directory=True)
    with pytest.raises(geometry.ProductionKillingGeometryFailure, match="already exists"):
        geometry.produce_bundle(REPORT_ROOT, dangling)
    assert dangling.is_symlink()


def test_duplicate_nonfinite_float_signed_zero_and_source_schema_mutations_fail_closed() -> None:
    with pytest.raises(geometry.ProductionKillingGeometryFailure, match="duplicate"):
        geometry._parse_strict_json(b'{"a": 1, "a": 2}\n', label="duplicate")
    for payload in (b'{"a": 1.0}\n', b'{"a": NaN}\n', b'{"a": Infinity}\n'):
        with pytest.raises(geometry.ProductionKillingGeometryFailure, match="floating literal"):
            geometry._parse_strict_json(payload, label="floating attacker")
    with pytest.raises(geometry.ProductionKillingGeometryFailure, match="canonical"):
        geometry._parse_canonical_json(b'{"b": 1, "a": 2}\n', label="unsorted")

    signed_zero_raw = struct.pack(">dd", -0.0, 0.0)
    signed_zero_manifest = geometry._raw_manifest(
        signed_zero_raw, role="signed_zero_probe", shape=(1,)
    )
    with pytest.raises(geometry.ProductionKillingGeometryFailure, match="signed-zero"):
        geometry._parse_interval_raw(
            signed_zero_raw,
            signed_zero_manifest,
            expected_role="signed_zero_probe",
            expected_shape=(1,),
        )
    nonfinite_raw = struct.pack(">dd", 0.0, math.inf)
    nonfinite_manifest = geometry._raw_manifest(nonfinite_raw, role="nonfinite_probe", shape=(1,))
    with pytest.raises(geometry.ProductionKillingGeometryFailure, match="valid finite"):
        geometry._parse_interval_raw(
            nonfinite_raw,
            nonfinite_manifest,
            expected_role="nonfinite_probe",
            expected_shape=(1,),
        )

    source_payload = _load_json(REPORT_ROOT / geometry.KILLING_SOURCE_RELATIVE_PATH)
    changed_schema = copy.deepcopy(source_payload)
    changed_schema["schema"] = "promoted_schema"
    with pytest.raises(geometry.ProductionKillingGeometryFailure, match="boundary"):
        geometry._validate_source(changed_schema)
    changed_profile_count = copy.deepcopy(source_payload)
    changed_profile_count["support_basis"]["profile_count"] = 5
    with pytest.raises(geometry.ProductionKillingGeometryFailure, match="definitions"):
        geometry._validate_source(changed_profile_count)
    duplicate_centre = copy.deepcopy(source_payload)
    duplicate_centre["support_basis"]["centres_binary64_hex"][1] = duplicate_centre[
        "support_basis"
    ]["centres_binary64_hex"][0]
    duplicate_centre["support_basis"]["centres_exact"][1] = duplicate_centre["support_basis"][
        "centres_exact"
    ][0]
    with pytest.raises(geometry.ProductionKillingGeometryFailure, match="exact/hex"):
        geometry._validate_source(duplicate_centre)
    signed_zero_hex = copy.deepcopy(source_payload)
    signed_zero_hex["support_basis"]["half_width_binary64_hex"] = "-0x0.0p+0"
    with pytest.raises(geometry.ProductionKillingGeometryFailure, match="negative zero"):
        geometry._validate_source(signed_zero_hex)


def test_coherently_repinned_contact_mutation_still_fails_same_core_reconstruction(
    deterministic_bundles: tuple[Path, Path], tmp_path: Path
) -> None:
    first, _ = deterministic_bundles
    attacked = tmp_path / "coherently-repinned"
    shutil.copytree(first, attacked)
    manifest = _bundle_manifest(attacked)
    summary = manifest["rows"][0]
    row_path = attacked / summary["row_manifest"]["path"]
    row = _load_json(row_path)
    contact = row["contact_fraction_relative"]
    raw_path = attacked / contact["file"]["path"]
    raw = bytearray(raw_path.read_bytes())
    changed = False
    for offset in range(0, len(raw), 16):
        _, upper = struct.unpack_from(">dd", raw, offset)
        if upper > 0.0:
            struct.pack_into(">dd", raw, offset, 0.0, 0.0)
            changed = True
            break
    assert changed
    raw_path.write_bytes(raw)
    raw_entry = geometry._file_entry(contact["file"]["path"], bytes(raw))
    contact["file"] = raw_entry
    contact["manifest"]["raw_sha256"] = raw_entry["sha256"]
    decoded = [struct.unpack_from(">dd", raw, offset) for offset in range(0, len(raw), 16)]
    old_active = contact["active_cell_count"]
    old_full = contact["full_cell_count"]
    contact["active_cell_count"] = sum(upper > 0.0 for _, upper in decoded)
    contact["full_cell_count"] = old_full
    summary["active_contact_cell_count"] = contact["active_cell_count"]
    summary["full_contact_cell_count"] = contact["full_cell_count"]
    manifest["totals"]["active_contact_cell_count"] += contact["active_cell_count"] - old_active
    manifest["totals"]["full_contact_cell_count"] += contact["full_cell_count"] - old_full
    snapshot = geometry._load_input_snapshot(REPORT_ROOT)
    contact["relation_sha256"] = geometry._domain_digest(
        b"production-killing-contact-relation-v1\0",
        geometry._contact_relation_payload(
            active_cell_count=contact["active_cell_count"],
            full_cell_count=contact["full_cell_count"],
            row_index=row["configuration_index"],
            row_label=row["configuration_label"],
            shape=tuple(contact["manifest"]["logical_shape"]),
            raw_sha256=raw_entry["sha256"],
            area_enclosure=contact["area_enclosure_exact"],
            partition_source=row["partition_source"],
            producer_sha256=snapshot.producer_sha256,
            quality_ledger=contact["quality_ledger"],
            source=snapshot.source,
        ),
    )
    support_relations = [entry["relation_sha256"] for entry in row["support_densities"]]
    row["row_relation_sha256"] = geometry._domain_digest(
        b"production-killing-row-relation-v1\0",
        geometry._row_relation_payload(
            row_index=row["configuration_index"],
            row_label=row["configuration_label"],
            shape=tuple(row["shape"]),
            contact_relation_sha256=contact["relation_sha256"],
            support_relation_sha256s=support_relations,
            partition_source=row["partition_source"],
            producer_sha256=snapshot.producer_sha256,
        ),
    )
    row_bytes = geometry._canonical_json_bytes(row)
    row_path.write_bytes(row_bytes)
    row_entry = geometry._file_entry(summary["row_manifest"]["path"], row_bytes)
    summary["row_manifest"] = row_entry
    summary["row_relation_sha256"] = row["row_relation_sha256"]
    for index, entry in enumerate(manifest["file_inventory"]):
        if entry["path"] == raw_entry["path"]:
            manifest["file_inventory"][index] = raw_entry
        elif entry["path"] == row_entry["path"]:
            manifest["file_inventory"][index] = row_entry
    manifest["family_relation_sha256"] = geometry._domain_digest(
        b"production-killing-family-relation-v1\0",
        geometry._family_relation_payload(
            rows=manifest["rows"],
            partition_reference_graph_sha256=manifest["partition_reference_graph_sha256"],
            producer_sha256=snapshot.producer_sha256,
        ),
    )
    (attacked / "bundle.json").write_bytes(geometry._canonical_json_bytes(manifest))
    with pytest.raises(
        geometry.ProductionKillingGeometryFailure,
        match="differs from same-core source reconstruction",
    ):
        geometry.verify_bundle(REPORT_ROOT, attacked)


def test_exact_lstat_tree_rejects_empty_fifo_symlink_hardlink_and_node_overflow(
    deterministic_bundles: tuple[Path, Path], tmp_path: Path
) -> None:
    first, _ = deterministic_bundles

    empty_attack = tmp_path / "empty-directory"
    shutil.copytree(first, empty_attack)
    (empty_attack / "unexpected-empty").mkdir()
    with pytest.raises(
        geometry.ProductionKillingGeometryFailure,
        match="missing, empty, or unexpected directories",
    ):
        geometry.verify_bundle(REPORT_ROOT, empty_attack)

    if hasattr(os, "mkfifo"):
        fifo_attack = tmp_path / "fifo"
        shutil.copytree(first, fifo_attack)
        os.mkfifo(fifo_attack / "unexpected-fifo")
        with pytest.raises(geometry.ProductionKillingGeometryFailure, match="non-regular node"):
            geometry.verify_bundle(REPORT_ROOT, fifo_attack)

    symlink_attack = tmp_path / "internal-symlink"
    shutil.copytree(first, symlink_attack)
    symlink_manifest = _bundle_manifest(symlink_attack)
    contact_relative = symlink_manifest["rows"][0]["row_manifest"]["path"]
    row = _load_json(symlink_attack / contact_relative)
    raw_path = symlink_attack / row["contact_fraction_relative"]["file"]["path"]
    raw_path.unlink()
    raw_path.symlink_to(symlink_attack / "bundle.json")
    with pytest.raises(geometry.ProductionKillingGeometryFailure, match="symlink"):
        geometry.verify_bundle(REPORT_ROOT, symlink_attack)

    hardlink_attack = tmp_path / "internal-hardlink"
    shutil.copytree(first, hardlink_attack)
    hardlink_manifest = _bundle_manifest(hardlink_attack)
    contact_relative = hardlink_manifest["rows"][0]["row_manifest"]["path"]
    row = _load_json(hardlink_attack / contact_relative)
    raw_path = hardlink_attack / row["contact_fraction_relative"]["file"]["path"]
    os.link(raw_path, hardlink_attack / "unexpected-hardlink")
    with pytest.raises(
        geometry.ProductionKillingGeometryFailure,
        match="hard-link|multiple hard links|inode alias",
    ):
        geometry.verify_bundle(REPORT_ROOT, hardlink_attack)

    node_cap_attack = tmp_path / "node-cap"
    shutil.copytree(first, node_cap_attack)
    expected_nodes = (
        geometry.EXPECTED_INVENTORY_FILES
        + 1  # bundle.json
        + geometry.EXPECTED_INVENTORY_DIRECTORIES
    )
    assert expected_nodes < geometry.MAXIMUM_BUNDLE_TREE_NODES
    additions = geometry.MAXIMUM_BUNDLE_TREE_NODES - expected_nodes + 1
    for index in range(additions):
        (node_cap_attack / f"overflow-{index:03d}").write_bytes(b"")
    with pytest.raises(geometry.ProductionKillingGeometryFailure, match="node cap exceeded"):
        geometry.verify_bundle(REPORT_ROOT, node_cap_attack)


def test_unsupported_no_replace_platform_fails_closed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = tmp_path / "unpublished"
    destination = tmp_path / "destination"
    source.mkdir()
    monkeypatch.setattr(geometry.sys, "platform", "unsupported-test-platform")
    with pytest.raises(geometry.ProductionKillingGeometryFailure, match="unsupported"):
        geometry._rename_directory_no_replace(source, destination)
    assert source.is_dir()
    assert not destination.exists()


def test_contract_order_flags_alias_and_source_snapshot_mutations_fail_closed(
    deterministic_bundles: tuple[Path, Path], tmp_path: Path
) -> None:
    first, _ = deterministic_bundles

    contract_attack = tmp_path / "contract"
    shutil.copytree(first, contract_attack)
    manifest = _bundle_manifest(contract_attack)
    contract = copy.deepcopy(manifest["factorization_contract"])
    contract["full_flat_index_formula"] = "i=(i_M*n_Y+i_Y)*n_R+i_R"
    changed_contract_sha256 = geometry._domain_digest(
        b"production-killing-factorization-flatten-contract-v1\0", contract
    )
    manifest["factorization_contract"] = contract
    manifest["factorization_contract_sha256"] = changed_contract_sha256
    manifest["method"]["factorization_contract_sha256"] = changed_contract_sha256
    (contract_attack / "bundle.json").write_bytes(geometry._canonical_json_bytes(manifest))
    with pytest.raises(geometry.ProductionKillingGeometryFailure, match="boundary metadata"):
        geometry.verify_bundle(REPORT_ROOT, contract_attack)

    row_order_attack = tmp_path / "row-order"
    shutil.copytree(first, row_order_attack)
    manifest = _bundle_manifest(row_order_attack)
    manifest["rows"][0], manifest["rows"][1] = manifest["rows"][1], manifest["rows"][0]
    (row_order_attack / "bundle.json").write_bytes(geometry._canonical_json_bytes(manifest))
    with pytest.raises(
        geometry.ProductionKillingGeometryFailure, match="row summary scalar binding"
    ):
        geometry.verify_bundle(REPORT_ROOT, row_order_attack)

    profile_order_attack = tmp_path / "profile-order"
    shutil.copytree(first, profile_order_attack)
    manifest = _bundle_manifest(profile_order_attack)
    summary = manifest["rows"][0]
    row = _load_json(profile_order_attack / summary["row_manifest"]["path"])
    row["support_densities"][0], row["support_densities"][1] = (
        row["support_densities"][1],
        row["support_densities"][0],
    )
    _rewrite_row_manifest(profile_order_attack, manifest, 0, row)
    (profile_order_attack / "bundle.json").write_bytes(geometry._canonical_json_bytes(manifest))
    with pytest.raises(geometry.ProductionKillingGeometryFailure, match="source binding"):
        geometry.verify_bundle(REPORT_ROOT, profile_order_attack)

    promoted_attack = tmp_path / "promoted-row-flag"
    shutil.copytree(first, promoted_attack)
    manifest = _bundle_manifest(promoted_attack)
    summary = manifest["rows"][0]
    row = _load_json(promoted_attack / summary["row_manifest"]["path"])
    row["flags"]["f0_pass"] = True
    _rewrite_row_manifest(promoted_attack, manifest, 0, row)
    (promoted_attack / "bundle.json").write_bytes(geometry._canonical_json_bytes(manifest))
    with pytest.raises(geometry.ProductionKillingGeometryFailure, match="boundary metadata"):
        geometry.verify_bundle(REPORT_ROOT, promoted_attack)

    alias_attack = tmp_path / "alias-and-unreferenced"
    shutil.copytree(first, alias_attack)
    manifest = _bundle_manifest(alias_attack)
    manifest["request_snapshots"]["killing_geometry_source"] = manifest["request_snapshots"][
        "configuration"
    ]
    (alias_attack / "bundle.json").write_bytes(geometry._canonical_json_bytes(manifest))
    with pytest.raises(geometry.ProductionKillingGeometryFailure, match="duplicate file"):
        geometry.verify_bundle(REPORT_ROOT, alias_attack)

    snapshot_attack = tmp_path / "source-snapshot"
    shutil.copytree(first, snapshot_attack)
    manifest = _bundle_manifest(snapshot_attack)
    source_entry = manifest["request_snapshots"]["killing_geometry_source"]
    source_path = snapshot_attack / source_entry["path"]
    changed_source = source_path.read_bytes().replace(
        b'"physical_dimension": 2', b'"physical_dimension": 3', 1
    )
    assert changed_source != source_path.read_bytes()
    source_path.write_bytes(changed_source)
    changed_entry = geometry._file_entry(source_entry["path"], changed_source)
    manifest["request_snapshots"]["killing_geometry_source"] = changed_entry
    _replace_inventory_entry(manifest, changed_entry)
    (snapshot_attack / "bundle.json").write_bytes(geometry._canonical_json_bytes(manifest))
    with pytest.raises(geometry.ProductionKillingGeometryFailure, match="snapshot drifted"):
        geometry.verify_bundle(REPORT_ROOT, snapshot_attack)


def test_coherently_repinned_support_one_ulp_mutation_fails_same_core_reconstruction(
    deterministic_bundles: tuple[Path, Path], tmp_path: Path
) -> None:
    first, _ = deterministic_bundles
    attacked = tmp_path / "support-one-ulp"
    shutil.copytree(first, attacked)
    manifest = _bundle_manifest(attacked)
    summary = manifest["rows"][0]
    row_path = attacked / summary["row_manifest"]["path"]
    row = _load_json(row_path)
    support = row["support_densities"][0]
    raw_path = attacked / support["file"]["path"]
    raw = bytearray(raw_path.read_bytes())
    changed = False
    for offset in range(0, len(raw), 16):
        lower, upper = struct.unpack_from(">dd", raw, offset)
        if upper > 0.0:
            struct.pack_into(">dd", raw, offset, lower, math.nextafter(upper, math.inf))
            changed = True
            break
    assert changed
    raw_path.write_bytes(raw)
    raw_entry = geometry._file_entry(support["file"]["path"], bytes(raw))
    support["file"] = raw_entry
    support["manifest"]["raw_sha256"] = raw_entry["sha256"]
    _replace_inventory_entry(manifest, raw_entry)
    _rewrite_row_manifest(attacked, manifest, 0, row)
    (attacked / "bundle.json").write_bytes(geometry._canonical_json_bytes(manifest))
    with pytest.raises(
        geometry.ProductionKillingGeometryFailure,
        match="differs from same-core source reconstruction",
    ):
        geometry.verify_bundle(REPORT_ROOT, attacked)


def test_module_has_static_nonpromotion_boundary() -> None:
    source = Path(geometry.__file__).read_text("utf-8")
    assert "list(os.scandir" not in source
    tree = ast.parse(source)
    called_names = {
        node.func.attr if isinstance(node.func, ast.Attribute) else node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, (ast.Attribute, ast.Name))
    }
    assert "build_contact_fraction_intervals_v2" in called_names
    assert "build_normalized_bump_profile" in called_names
    for forbidden_call in (
        "PackedKernelInputs",
        "build_packed_tensor_kernel",
        "build_physical_killing_intervals_v2",
        "propagate_uniformization",
        "run_f0",
    ):
        assert forbidden_call not in called_names
