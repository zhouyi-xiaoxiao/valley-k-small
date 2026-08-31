from __future__ import annotations

import ast
import copy
import inspect
import json
import math
import os
import shutil
import struct
import sys
import types
from dataclasses import replace
from fractions import Fraction
from pathlib import Path

import pytest
import rate_defined_tensor_f0_production_killing_geometry_independent as verifier

REPORT_ROOT = Path(__file__).resolve().parents[1]
BUNDLE_ROOT = REPORT_ROOT / "artifacts/data/physical_production_killing_geometry_v1"


@pytest.fixture(scope="module")
def parsed_candidate() -> verifier.ParsedCandidate:
    return verifier.parse_candidate_bundle(REPORT_ROOT, BUNDLE_ROOT)


@pytest.fixture(scope="module")
def semantic_evidence(
    parsed_candidate: verifier.ParsedCandidate,
) -> tuple[dict[str, object], dict[str, object]]:
    authority = verifier.load_frozen_geometry_authority(REPORT_ROOT)
    contact = verifier.verify_contact_rows(parsed_candidate, authority)
    support, _ = verifier.verify_support_rows(parsed_candidate, authority)
    return contact, support


def test_frozen_hashes_runtime_and_forbidden_import_boundary_are_exact() -> None:
    assert verifier.sha256_bytes((REPORT_ROOT / verifier.AUTHORITY_PATH).read_bytes()) == (
        verifier.AUTHORITY_SHA256
    )
    assert verifier.sha256_bytes((REPORT_ROOT / verifier.CONFIGURATION_PATH).read_bytes()) == (
        verifier.CONFIGURATION_SHA256
    )
    assert verifier.sha256_bytes((REPORT_ROOT / verifier.PRODUCER_PATH).read_bytes()) == (
        verifier.PRODUCER_SHA256
    )
    assert verifier.sha256_bytes((REPORT_ROOT / verifier.PRODUCER_TEST_PATH).read_bytes()) == (
        verifier.PRODUCER_TEST_SHA256
    )
    assert verifier.sha256_bytes((REPORT_ROOT / verifier.OPERATION_MODEL_PATH).read_bytes()) == (
        verifier.OPERATION_MODEL_SHA256
    )
    assert verifier._runtime_versions() == {
        "gmp": "6.3.0",
        "gmpy2": "2.2.1",
        "mpc": "1.3.1",
        "mpfr": "4.2.1",
        "python": "3.12.13",
    }
    verifier.assert_import_boundary()
    source = Path(verifier.__file__).read_text("utf-8")
    tree = ast.parse(source)
    imported = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    } | {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module is not None
    }
    assert not imported & verifier._FORBIDDEN_IMPORTS


def test_tree_inventory_manifest_graph_and_all_partition_reconstructions_are_exact(
    parsed_candidate: verifier.ParsedCandidate,
) -> None:
    assert parsed_candidate.tree.digest == verifier.CANDIDATE_TREE_SHA256
    assert len(parsed_candidate.tree.files) == 76
    assert len(parsed_candidate.tree.directories) == 14
    assert parsed_candidate.tree.total_bytes <= verifier.MAX_TREE_BYTES
    assert parsed_candidate.partition_tree.digest == verifier.PARTITION_TREE_SHA256
    assert len(parsed_candidate.partition_tree.files) == verifier.EXPECTED_PARTITION_TREE_FILES
    assert len(parsed_candidate.partition_tree.directories) == (
        verifier.EXPECTED_PARTITION_TREE_DIRECTORIES
    )
    assert parsed_candidate.partition_tree.total_bytes == verifier.EXPECTED_PARTITION_TREE_BYTES
    assert len(parsed_candidate.rows) == 12
    assert sum(len(row) for row in parsed_candidate.contacts) == 233_139
    assert sum(len(profile) for row in parsed_candidate.supports for profile in row) == 6_852
    alignments = [axis.construction for axes in parsed_candidate.axes for axis in axes]
    assert "cell_centred_reflecting_scharfetter_gummel" in alignments
    assert "vertex_centred_reflecting_scharfetter_gummel" in alignments
    assert "cell_centred_periodic_diffusion" in alignments
    assert "cell_centred_periodic_diffusion_half_shift" in alignments
    for axes, semantic_hashes in zip(
        parsed_candidate.axes, parsed_candidate.independent_partition_sha256s, strict=True
    ):
        assert tuple(axis.semantic_sha256 for axis in axes) == semantic_hashes
        for axis in axes:
            assert sum(axis.volumes, Fraction(0)) == axis.domain_width


def test_directed_contact_oracle_pi_identity_and_exact_cell_canonicalization(
    parsed_candidate: verifier.ParsedCandidate,
    semantic_evidence: tuple[dict[str, object], dict[str, object]],
) -> None:
    contact, _ = semantic_evidence
    assert contact["active_cell_count"] == 5_446
    assert contact["full_cell_count"] == 4_142
    assert contact["partial_oracle_count"] == 1_304
    assert contact["sentinel_partial_count"] == 12
    assert (
        verifier.parse_reduced_fraction(
            contact["maximum_oracle_interval_width_exact"], label="test oracle width"
        )
        <= verifier.CONTACT_ORACLE_MAX_WIDTH
    )
    radius = verifier.load_frozen_geometry_authority(REPORT_ROOT).radius
    quadrant = verifier.disk_quadrant_prefix_enclosure(radius, radius, radius).exact()
    quarter_disk = verifier.ExactInterval(
        verifier._pi_radius_squared(radius, verifier.PRIMARY_BITS).lower / 4,
        verifier._pi_radius_squared(radius, verifier.PRIMARY_BITS).upper / 4,
    )
    assert quadrant.contains(quarter_disk)


def test_coherent_summary_and_row_contact_count_mutation_is_recomputed(
    parsed_candidate: verifier.ParsedCandidate,
) -> None:
    manifest = copy.deepcopy(parsed_candidate.manifest)
    rows = copy.deepcopy(parsed_candidate.rows)
    manifest["rows"][0]["active_contact_cell_count"] += 1
    rows[0]["contact_fraction_relative"]["active_cell_count"] += 1
    mutated = replace(parsed_candidate, manifest=manifest, rows=rows)
    authority = verifier.load_frozen_geometry_authority(REPORT_ROOT)
    with pytest.raises(verifier.IndependentVerificationFailure, match="aggregate ledger"):
        verifier.verify_contact_rows(mutated, authority)


def test_support_shared_simpson_oracle_uses_dimensionless_cell_mass_width(
    parsed_candidate: verifier.ParsedCandidate,
    semantic_evidence: tuple[dict[str, object], dict[str, object]],
) -> None:
    _, support = semantic_evidence
    assert support["breakpoint_count"] <= verifier.MAX_BUMP_BREAKPOINTS
    assert support["sentinel_support_cell_count"] == verifier.EXPECTED_SUPPORT_RECORDS
    metrics = support["paired_simpson_metrics"]
    assert metrics["tree_panel_count"] <= verifier.MAX_SIMPSON_PANELS
    assert (
        metrics["accepted_leaf_partition_sha256"]
        == verifier.EXPECTED_ACCEPTED_LEAF_PARTITION_SHA256
    )
    assert metrics["paired_sample_count"] == metrics["sample_nesting_count"]
    assert metrics["root_m4_nesting_count"] == support["breakpoint_count"] - 1
    assert metrics["accepted_leaf_count"] == metrics["leaf_panel_nesting_count"]
    assert metrics["table_nesting_count"] == support["breakpoint_count"] - 1
    assert metrics["normalizer_nested"] is True
    assert metrics["maximum_dfs_stack"] <= verifier.MAX_SIMPSON_DFS_STACK
    assert metrics["maximum_exact_component_bits"] <= verifier.MAX_SIMPSON_EXACT_COMPONENT_BITS
    assert metrics["maximum_coordinate_component_bits"] <= (
        verifier.MAX_DYADIC_COORDINATE_COMPONENT_BITS
    )
    assert (
        verifier.parse_reduced_fraction(
            support["maximum_candidate_cell_mass_width_exact"], label="candidate mass width"
        )
        <= verifier.SUPPORT_CANDIDATE_CELL_MASS_MAX_WIDTH
    )
    assert (
        verifier.parse_reduced_fraction(
            support["maximum_oracle_cell_mass_width_exact"], label="oracle mass width"
        )
        <= verifier.SUPPORT_CANDIDATE_CELL_MASS_MAX_WIDTH / 8
    )

    density_widths: list[Fraction] = []
    mass_widths: list[Fraction] = []
    for axes, rows in zip(parsed_candidate.axes, parsed_candidate.supports, strict=True):
        volumes = axes[0].volumes
        for profile in rows:
            for interval, volume in zip(profile, volumes, strict=True):
                density_widths.append(interval.width)
                mass_widths.append(volume * interval.width)
    assert max(density_widths) > verifier.CONTACT_CANDIDATE_INTERVAL_MAX_WIDTH
    assert max(mass_widths) <= verifier.SUPPORT_CANDIDATE_CELL_MASS_MAX_WIDTH


def test_semantic_receipt_is_deterministic_child_only_and_not_outer_pass(
    parsed_candidate: verifier.ParsedCandidate,
    semantic_evidence: tuple[dict[str, object], dict[str, object]],
) -> None:
    contact, support = semantic_evidence
    first = verifier._build_semantic_receipt(parsed_candidate, contact, support)
    second = verifier._build_semantic_receipt(parsed_candidate, contact, support)
    assert verifier.canonical_json_bytes(first) == verifier.canonical_json_bytes(second)
    assert first["status"] == verifier.PASS_STATUS
    assert first["status"] != verifier.OUTER_PASS_STATUS
    assert first["flags"]["separate_source_implementation"] is True
    assert first["flags"]["independent_backend"] is False
    assert first["flags"]["shared_simpson_remainder_lemma"] is True
    assert first["flags"]["paired_same_leaf_precision_sentinel"] is True
    assert first["flags"]["sentinel_independent_2^-68_adaptive"] is False
    assert first["schema"].endswith("semantic_receipt_v2")
    assert first["frozen_sources"]["operation_model_sha256"] == verifier.OPERATION_MODEL_SHA256
    assert first["support_policy_digests"] == {
        "flat_tail_bump_upper_sha256": verifier.FLAT_TAIL_BUMP_UPPER_SHA256,
        "flat_tail_M4_upper_sha256": verifier.FLAT_TAIL_M4_UPPER_SHA256,
        "flat_tail_policy_sha256": verifier.FLAT_TAIL_POLICY_SHA256,
        "paired_simpson_policy_sha256": verifier.PAIRED_SIMPSON_POLICY_SHA256,
    }
    assert first["flags"]["verifier_executed_source_attested"] is False
    assert first["flags"]["outer_staged_source_pre_post_required"] is True
    assert "verifier_staged_file_sha256_at_receipt" in first
    assert "verifier_source_sha256" not in first
    assert "clean_process_repeat_count" not in first["flags"]
    assert "semantic_receipt_bytes_identical" not in first["flags"]
    for forbidden in (
        "concrete_killing_constructed",
        "single_physical_operator_bound",
        "full_operator_bound",
        "installed_budget_used",
        "prospective_control_used",
        "positive_budget_executed",
        "science_executed",
        "propagation_executed",
        "topology_complete",
        "production_resource_gate",
        "resource_promotion_eligible",
        "largest_state_tensor_allocated",
        "continuum_verified",
        "f0_pass",
        "f1_authorized",
        "prr_release_authorized",
    ):
        assert first["flags"][forbidden] is False


def test_duplicate_float_fraction_hex_path_and_containment_mutations_fail_closed() -> None:
    with pytest.raises(verifier.IndependentVerificationFailure, match="duplicate"):
        verifier.strict_load_ascii_json(b'{"a": 1, "a": 2}\n', label="duplicate")
    with pytest.raises(verifier.IndependentVerificationFailure, match="float"):
        verifier.strict_load_ascii_json(b'{"a": 1.0}\n', label="float")
    for value in ("1/01", "2/2", "-0/1", "0/-1"):
        with pytest.raises(verifier.IndependentVerificationFailure):
            verifier.parse_reduced_fraction(value, label="mutated fraction")
    for value in (
        "0X1.0p+0",
        "0x1.0p0",
        "-0x0.0000000000000p+0",
        "0x1.0000000000000p+1024",
    ):
        with pytest.raises(verifier.IndependentVerificationFailure):
            verifier.parse_binary64_hex_as_fraction(value, label="mutated hex")
    for path in (
        ".",
        "../escape",
        "/absolute",
        "a\\b",
        "a/../b",
        "a\0b",
        "nonascii-\N{SNOWMAN}",
    ):
        with pytest.raises(verifier.IndependentVerificationFailure):
            verifier.validate_relative_manifest_path(path, label="mutated path")
    with pytest.raises(verifier.IndependentVerificationFailure, match="excludes oracle"):
        verifier.require_exact_containment(
            verifier.ExactInterval(Fraction(0), Fraction(1, 2)),
            verifier.ExactInterval(Fraction(1, 2), Fraction(3, 4)),
            label="one-ulp-style narrowing",
        )


def test_recursive_exact_json_equality_rejects_bool_integer_aliases() -> None:
    frozen = {
        "flags": {"accepted": True, "executed": False},
        "method": {"powers": [3, 1, 5], "schema": "probe"},
        "source_pins": {"source": {"path": "code/probe.py", "sha256": "0" * 64}},
        "totals": {"records": 1},
    }
    assert verifier.exact_json_equal(frozen, copy.deepcopy(frozen))
    for path, replacement in (
        (("flags", "accepted"), 1),
        (("flags", "executed"), 0),
        (("method", "powers"), [3, True, 5]),
        (("totals", "records"), True),
    ):
        mutated = copy.deepcopy(frozen)
        if len(path) == 2:
            mutated[path[0]][path[1]] = replacement
        assert mutated == frozen
        assert not verifier.exact_json_equal(mutated, frozen)
    assert not verifier.exact_json_equal({"value": 0}, {"value": False})
    assert not verifier.exact_json_equal({"value": 1}, {"value": True})


def test_raw_endian_signed_zero_and_tree_alias_mutations_fail_closed(tmp_path: Path) -> None:
    signed_zero = struct.pack(">dd", -0.0, 0.0)
    manifest = {
        "byte_order": "big",
        "logical_shape": [1],
        "raw_byte_length": 16,
        "raw_sha256": verifier.sha256_bytes(signed_zero),
        "record_count": 1,
        "record_format": ">dd",
        "role": "probe",
        "schema": verifier.RAW_SCHEMA,
    }
    with pytest.raises(verifier.IndependentVerificationFailure, match="noncanonical"):
        verifier.stream_be64_intervals(signed_zero, manifest, role="probe", shape=(1,))

    little_endian = struct.pack("<dd", 0.25, 0.5)
    manifest["raw_sha256"] = verifier.sha256_bytes(little_endian)
    decoded = verifier.stream_be64_intervals(little_endian, manifest, role="probe", shape=(1,))
    with pytest.raises(verifier.IndependentVerificationFailure):
        verifier.require_exact_containment(
            decoded[0],
            verifier.ExactInterval(Fraction(1, 4), Fraction(1, 2)),
            label="endian mutation",
        )
    for field, mutated in (
        ("record_count", True),
        ("raw_byte_length", True),
        ("logical_shape", [True]),
    ):
        original = manifest[field]
        manifest[field] = mutated
        with pytest.raises(verifier.IndependentVerificationFailure):
            verifier.stream_be64_intervals(little_endian, manifest, role="probe", shape=(1,))
        manifest[field] = original
    with pytest.raises(verifier.IndependentVerificationFailure):
        verifier.stream_be64_intervals(little_endian, manifest, role="probe", shape=(True,))

    copied = tmp_path / "tree"
    shutil.copytree(BUNDLE_ROOT, copied)
    target = copied / "rows/00_o113_base/contact_fraction_relative.be64"
    os.link(target, copied / "unexpected-hardlink")
    with pytest.raises(verifier.IndependentVerificationFailure, match="hard-link|hard links"):
        verifier.inventory_candidate_tree(copied)


def test_directory_replacement_between_enqueue_and_open_fails_closed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    copied = tmp_path / "tree"
    shutil.copytree(BUNDLE_ROOT, copied)
    real_open = os.open
    swapped = False

    def racing_open(
        path: str | bytes | os.PathLike[str] | os.PathLike[bytes],
        flags: int,
        mode: int = 0o777,
        *,
        dir_fd: int | None = None,
    ) -> int:
        nonlocal swapped
        if path == "rows" and dir_fd is not None and not swapped:
            swapped = True
            (copied / "rows").rename(copied / "rows-before-race")
            (copied / "rows").mkdir()
        return real_open(path, flags, mode, dir_fd=dir_fd)

    monkeypatch.setattr(os, "open", racing_open)
    with pytest.raises(verifier.IndependentVerificationFailure, match="directory changed"):
        verifier.inventory_candidate_tree(copied)
    assert swapped is True


def test_invalid_cli_is_stdout_only_canonical_unbound_hold(
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = verifier._main(["--invalid", "value"])
    captured = capsys.readouterr()
    assert exit_code == 2
    assert captured.err == ""
    assert json.loads(captured.out) == {
        "schema": verifier.CHILD_UNBOUND_HOLD_ACK_SCHEMA,
        "status": verifier.HOLD_API,
    }
    assert captured.out == verifier.canonical_json_bytes(json.loads(captured.out)).decode("ascii")


def test_acceptance_pins_full_cells_and_runtime_closure_cannot_be_disabled() -> None:
    assert tuple(inspect.signature(verifier.parse_candidate_bundle).parameters) == (
        "report_root",
        "bundle_root",
    )
    assert tuple(inspect.signature(verifier.verify_contact_rows).parameters) == (
        "candidate",
        "authority",
    )
    assert tuple(inspect.signature(verifier.assert_import_boundary).parameters) == ()
    with pytest.raises(TypeError):
        verifier.parse_candidate_bundle(  # type: ignore[call-arg]
            REPORT_ROOT,
            BUNDLE_ROOT,
            require_frozen_hashes=False,
        )
    with pytest.raises(TypeError):
        verifier.verify_contact_rows(  # type: ignore[call-arg]
            None,
            None,
            strict_full_binary64=False,
        )
    with pytest.raises(TypeError):
        verifier.assert_import_boundary(require_clean_runtime=False)  # type: ignore[call-arg]

    forbidden_name = "shadowpkg.rate_defined_tensor_f0"
    assert forbidden_name not in sys.modules
    sys.modules[forbidden_name] = types.ModuleType(forbidden_name)
    try:
        with pytest.raises(verifier.IndependentVerificationFailure, match="runtime module"):
            verifier.assert_import_boundary()
        with pytest.raises(verifier.IndependentVerificationFailure, match="runtime module"):
            verifier._build_semantic_receipt(None, {}, {})  # type: ignore[arg-type]
    finally:
        del sys.modules[forbidden_name]

    source = Path(verifier.__file__).read_text("utf-8")
    assert "require_frozen_hashes" not in source
    assert "strict_full_binary64" not in source


def test_ast_import_boundary_rejects_qualified_aliases_and_dynamic_loaders() -> None:
    for source in (
        b"import shadowpkg.rate_defined_tensor_f0\n",
        b"from shadowpkg import rate_defined_tensor_f0\n",
        b"__import__('rate_defined_tensor_f0')\n",
        b"importlib.import_module('rate_defined_tensor_f0')\n",
        b"loader.exec_module(module)\n",
        b'exec("import rate_defined_tensor_f0")\n',
        b"eval(\"__import__('rate_defined_tensor_f0')\")\n",
        b"compile('import rate_defined_tensor_f0', '<x>', 'exec')\n",
    ):
        with pytest.raises(verifier.IndependentVerificationFailure):
            verifier._assert_source_import_boundary(source, filename="mutation.py")
    verifier._assert_source_import_boundary(
        b"import fractions\nfrom pathlib import Path\n",
        filename="safe.py",
    )


def test_verifier_owned_mpfr_context_isolates_flags_traps_and_exceptions() -> None:
    gmpy2 = verifier.gmpy2
    original = gmpy2.get_context()
    caller = gmpy2.context(original)
    caller.precision = 77
    caller.round = gmpy2.RoundUp
    caller.trap_inexact = True
    caller.inexact = True
    expected = repr(caller)
    gmpy2.set_context(caller)
    try:
        result = verifier._mpfr_fraction(Fraction(1, 3), verifier.PRIMARY_BITS, gmpy2.RoundDown)
        assert result < gmpy2.mpq(1, 3)
        assert gmpy2.get_context() is caller
        assert repr(gmpy2.get_context()) == expected

        for (precision, rounding), cached in verifier._VERIFIER_MPFR_CONTEXTS.items():
            cached.trap_inexact = True
            cached.inexact = True
            cached_expected = repr(cached)
            gmpy2.set_context(cached)
            try:
                nested = verifier._mpfr_fraction(Fraction(1, 3), precision, rounding)
                assert gmpy2.is_finite(nested)
                assert gmpy2.get_context() is cached
                assert repr(gmpy2.get_context()) == cached_expected
                with pytest.raises(
                    verifier.IndependentVerificationFailure,
                    match="unknown MPFR",
                ):
                    verifier._mp_binary(
                        nested,
                        nested,
                        precision,
                        rounding,
                        "nested-mutated-operation",
                    )
                assert gmpy2.get_context() is cached
                assert repr(gmpy2.get_context()) == cached_expected
            finally:
                verifier._configure_verifier_context(cached, precision, rounding)
                gmpy2.set_context(caller)
        with pytest.raises(verifier.IndependentVerificationFailure, match="unknown MPFR"):
            verifier._mp_binary(
                result,
                result,
                verifier.PRIMARY_BITS,
                gmpy2.RoundDown,
                "mutated-operation",
            )
        assert gmpy2.get_context() is caller
        assert repr(gmpy2.get_context()) == expected
    finally:
        gmpy2.set_context(original)


def test_candidate_root_symlink_is_rejected_before_acceptance(tmp_path: Path) -> None:
    linked = tmp_path / "candidate-link"
    linked.symlink_to(BUNDLE_ROOT, target_is_directory=True)
    with pytest.raises(verifier.IndependentVerificationFailure, match="root is a symlink"):
        verifier.parse_candidate_bundle(REPORT_ROOT, linked)

    linked_report = tmp_path / "report-link"
    linked_report.symlink_to(REPORT_ROOT, target_is_directory=True)
    with pytest.raises(verifier.IndependentVerificationFailure, match="report root is a symlink"):
        verifier.parse_candidate_bundle(linked_report, BUNDLE_ROOT)


def test_tree_directory_and_relative_depth_caps_fail_before_traversal(tmp_path: Path) -> None:
    directory_flood = tmp_path / "directory-flood"
    directory_flood.mkdir()
    for index in range(verifier.MAX_TREE_DIRECTORIES + 1):
        (directory_flood / f"d{index:03d}").mkdir()
    with pytest.raises(verifier.IndependentVerificationFailure, match="directory cap"):
        verifier.inventory_candidate_tree(directory_flood)

    depth_flood = tmp_path / "depth-flood"
    depth_flood.mkdir()
    current = depth_flood
    for component in ("a", "b", "c", "d"):
        current /= component
        current.mkdir()
    with pytest.raises(verifier.IndependentVerificationFailure, match="relative-depth cap"):
        verifier.inventory_candidate_tree(depth_flood)


def test_simpson_expired_deadline_holds_even_when_root_would_accept() -> None:
    with pytest.raises(verifier.IndependentVerificationFailure) as captured:
        verifier._paired_root_local_bump_tables(
            (Fraction(0), Fraction(1, 1000)),
            target_width=Fraction(1),
            deadline=0.0,
        )
    assert captured.value.code == verifier.HOLD_TIMEOUT


def test_semantic_core_deadline_is_checked_after_parse_and_contact(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    candidate = object()
    authority = object()
    events: list[str] = []
    monkeypatch.setattr(
        verifier,
        "parse_candidate_bundle",
        lambda *_args: events.append("parse") or candidate,
    )
    monkeypatch.setattr(
        verifier,
        "load_frozen_geometry_authority",
        lambda *_args: events.append("authority") or authority,
    )
    monkeypatch.setattr(
        verifier,
        "verify_contact_rows",
        lambda *_args: events.append("contact") or {},
    )
    monkeypatch.setattr(
        verifier,
        "verify_support_rows",
        lambda *_args, **_kwargs: pytest.fail("support must not run after an expired deadline"),
    )

    clock = iter((0.0, verifier.RUN_DEADLINE_SECONDS + 1.0))
    monkeypatch.setattr(verifier.time, "monotonic", lambda: next(clock))
    with pytest.raises(verifier.IndependentVerificationFailure) as after_parse:
        verifier.verify_semantic_core(REPORT_ROOT, BUNDLE_ROOT)
    assert after_parse.value.code == verifier.HOLD_TIMEOUT
    assert events == ["parse"]

    events.clear()
    clock = iter((0.0, 0.0, verifier.RUN_DEADLINE_SECONDS + 1.0))
    monkeypatch.setattr(verifier.time, "monotonic", lambda: next(clock))
    with pytest.raises(verifier.IndependentVerificationFailure) as after_contact:
        verifier.verify_semantic_core(REPORT_ROOT, BUNDLE_ROOT)
    assert after_contact.value.code == verifier.HOLD_TIMEOUT
    assert events == ["parse", "authority", "contact"]


def test_m4_upper_only_path_is_bit_exact_to_generic_reference_on_frozen_panels(
    parsed_candidate: verifier.ParsedCandidate,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    authority = verifier.load_frozen_geometry_authority(REPORT_ROOT)
    breakpoints = verifier._support_breakpoints(parsed_candidate, authority)
    root_panels = tuple(zip(breakpoints, breakpoints[1:]))
    representatives = (
        (Fraction(-1), Fraction(-255, 256)),
        (Fraction(-3, 4), Fraction(-1, 2)),
        (Fraction(-1, 257), Fraction(0)),
        (Fraction(0), Fraction(1, 257)),
        (Fraction(1, 3), Fraction(7, 16)),
        (Fraction(255, 256), Fraction(1)),
    )
    for lower, upper in root_panels:
        optimized = verifier._bump_fourth_derivative_bound_mpq(lower, upper)
        reference = verifier._bump_fourth_derivative_bound_mpq_reference(lower, upper)
        assert type(optimized) is verifier.gmpy2.mpq
        assert optimized == reference
    for precision in (verifier.PRIMARY_BITS, verifier.SENTINEL_BITS):
        for lower, upper in representatives:
            optimized = verifier._bump_fourth_derivative_bound_mpq(
                lower,
                upper,
                precision=precision,
            )
            reference = verifier._bump_fourth_derivative_bound_mpq_reference(
                lower,
                upper,
                precision=precision,
            )
            assert optimized == reference

    original = verifier._positive_power_exp_uppers_mpq
    calls: list[tuple[Fraction, tuple[int, ...]]] = []

    def traced(
        value: Fraction,
        powers: tuple[int, ...],
        precision: int,
    ) -> dict[int, verifier.gmpy2.mpq]:
        calls.append((value, powers))
        return original(value, powers, precision)

    monkeypatch.setattr(verifier, "_positive_power_exp_uppers_mpq", traced)
    verifier._bump_fourth_derivative_bound_mpq(Fraction(255, 256), Fraction(1))
    assert calls == [(Fraction(65_536, 511), (3, 4, 5, 6, 7, 8))]


def test_simpson_remainder_and_panel_are_bit_exact_to_preoptimization_formula(
    parsed_candidate: verifier.ParsedCandidate,
) -> None:
    authority = verifier.load_frozen_geometry_authority(REPORT_ROOT)
    breakpoints = verifier._support_breakpoints(parsed_candidate, authority)
    roots = tuple(zip(breakpoints, breakpoints[1:]))
    descendant_roots = (roots[0], roots[len(roots) // 2], roots[-1])
    descendants: list[tuple[Fraction, Fraction]] = []
    for lower, upper in descendant_roots:
        span = upper - lower
        descendants.extend(
            (
                (lower, lower + span / 2),
                (lower + span / 4, lower + span / 2),
                (lower + 5 * span / 8, lower + 3 * span / 4),
            )
        )

    def reference(
        lower: Fraction,
        upper: Fraction,
        precision: int,
    ) -> tuple[tuple[verifier.gmpy2.mpq, verifier.gmpy2.mpq], verifier.gmpy2.mpq]:
        midpoint = (lower + upper) / 2
        values = (
            verifier.bump_value_enclosure(lower, precision=precision),
            verifier.bump_value_enclosure(midpoint, precision=precision),
            verifier.bump_value_enclosure(upper, precision=precision),
        )
        weighted = verifier.mp_add(
            values[0],
            verifier.mp_add(
                verifier.mp_mul(
                    verifier.mp_interval_from_fraction(Fraction(4), precision),
                    values[1],
                ),
                values[2],
            ),
        )
        estimate = verifier.mp_mul(
            verifier.mp_interval_from_fraction((upper - lower) / 6, precision),
            weighted,
        )
        remainder = (
            verifier._fraction_exact_mpq((upper - lower) ** 5)
            * verifier._bump_fourth_derivative_bound_mpq(
                lower,
                upper,
                precision=precision,
            )
            / 2880
        )
        return (
            (
                max(verifier.gmpy2.mpq(0), verifier.gmpy2.mpq(estimate.lower) - remainder),
                verifier.gmpy2.mpq(estimate.upper) + remainder,
            ),
            remainder,
        )

    for precision in (verifier.PRIMARY_BITS, verifier.SENTINEL_BITS):
        for lower, upper in roots + tuple(descendants):
            expected_panel, expected_remainder = reference(lower, upper, precision)
            observed_remainder = verifier._simpson_remainder_mpq(
                lower,
                upper,
                precision=precision,
            )
            assert type(observed_remainder) is verifier.gmpy2.mpq
            assert observed_remainder == expected_remainder
            assert verifier._simpson_panel_enclosure_mpq(
                lower,
                upper,
                precision=precision,
            ) == (expected_panel, expected_remainder)
            midpoint = verifier._checked_dyadic_midpoint(
                lower,
                upper,
                label="test midpoint",
            )
            cached_values = (
                verifier.bump_value_enclosure(lower, precision=precision),
                verifier.bump_value_enclosure(midpoint, precision=precision),
                verifier.bump_value_enclosure(upper, precision=precision),
            )
            assert (
                verifier._simpson_panel_from_samples_mpq(
                    lower,
                    upper,
                    cached_values,
                    expected_remainder,
                    four=verifier.mp_interval_from_fraction(Fraction(4), precision),
                    scale=verifier.mp_interval_from_fraction((upper - lower) / 6, precision),
                )
                == expected_panel
            )


def test_simpson_remainder_does_not_evaluate_bump_values(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def forbidden(*_args: object, **_kwargs: object) -> None:
        pytest.fail("remainder-only helper evaluated the Simpson estimate")

    monkeypatch.setattr(verifier, "bump_value_enclosure", forbidden)
    monkeypatch.setattr(verifier, "mp_add", forbidden)
    monkeypatch.setattr(verifier, "_support_nonnegative_interval_mul", forbidden)
    remainder = verifier._simpson_remainder_mpq(
        Fraction(1, 4),
        Fraction(3, 8),
        precision=verifier.PRIMARY_BITS,
    )
    assert type(remainder) is verifier.gmpy2.mpq
    assert remainder > 0


def test_support_nonnegative_multiply_is_bit_exact_to_generic_reference() -> None:
    for precision in (verifier.PRIMARY_BITS, verifier.SENTINEL_BITS):
        zero = verifier.mp_interval_from_fraction(Fraction(0), precision)
        exact_left = verifier.mp_interval_from_fraction(Fraction(3, 8), precision)
        exact_right = verifier.mp_interval_from_fraction(Fraction(5, 16), precision)
        narrow_left = verifier.mp_interval_from_fraction(Fraction(1, 3), precision)
        narrow_right = verifier.mp_interval_from_fraction(Fraction(2, 7), precision)
        for left, right in (
            (zero, narrow_right),
            (exact_left, exact_right),
            (narrow_left, narrow_right),
        ):
            assert verifier._support_nonnegative_interval_mul(left, right) == verifier.mp_mul(
                left,
                right,
            )
        signed = verifier.MPInterval(
            verifier._mpfr_fraction(Fraction(-1), precision, verifier.gmpy2.RoundDown),
            verifier._mpfr_fraction(Fraction(1), precision, verifier.gmpy2.RoundUp),
            precision,
        )
        with pytest.raises(verifier.IndependentVerificationFailure, match="nonnegative"):
            verifier._support_nonnegative_interval_mul(signed, exact_right)


def test_positive_power_request_rejects_bool_before_deduplication() -> None:
    for powers in ((True,), (1, True), (True, 1), (2, False)):
        with pytest.raises(verifier.IndependentVerificationFailure) as failure:
            verifier._positive_power_exp_uppers_mpq(
                Fraction(3, 2),
                powers,
                verifier.PRIMARY_BITS,
            )
        assert failure.value.code == verifier.HOLD_API


def test_paired_left_first_dfs_prefilter_reuse_nesting_and_caps(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target = Fraction(1, 1 << 20)
    primary, sentinel, metrics = verifier._paired_root_local_bump_tables(
        (Fraction(0), Fraction(1)),
        target_width=target,
        deadline=verifier.time.monotonic() + 30,
    )
    assert primary.tree_panel_count == 255
    assert primary.accepted_leaf_count == 128
    assert primary.maximum_dyadic_depth == 7
    assert primary.maximum_dfs_stack == 8
    assert primary.intervals[0].width <= target
    assert primary.intervals[0].contains(sentinel.intervals[0])
    assert primary.normalizer.contains(sentinel.normalizer)
    assert metrics["prefilter_split_count"] == 127
    assert metrics["estimate_split_count"] == 0
    assert metrics["primary_estimate_count"] == primary.accepted_leaf_count
    assert metrics["sentinel_estimate_count"] == primary.accepted_leaf_count
    assert metrics["paired_sample_count"] == 257
    assert metrics["sample_nesting_count"] == metrics["paired_sample_count"]
    assert metrics["leaf_panel_nesting_count"] == primary.accepted_leaf_count
    assert metrics["table_nesting_count"] == 1
    assert metrics["maximum_exact_component_bits"] <= verifier.MAX_SIMPSON_EXACT_COMPONENT_BITS
    assert metrics["maximum_coordinate_component_bits"] == 9
    assert (
        metrics["accepted_leaf_partition_sha256"]
        == "fca7cdcb2928512afc39b4e74d46f4d6e8737fc6a1312cced1c1648799fbcf8a"
    )

    repeated = verifier._paired_root_local_bump_tables(
        (Fraction(0), Fraction(1)),
        target_width=target,
        deadline=verifier.time.monotonic() + 30,
    )
    assert (
        repeated[2]["accepted_leaf_partition_sha256"] == (metrics["accepted_leaf_partition_sha256"])
    )
    assert repeated[2]["primary_table_sha256"] == metrics["primary_table_sha256"]

    monkeypatch.setattr(verifier, "MAX_SIMPSON_DYADIC_DEPTH", 0)
    with pytest.raises(verifier.IndependentVerificationFailure, match="dyadic-depth cap"):
        verifier._paired_root_local_bump_tables(
            (Fraction(0), Fraction(1, 2)),
            target_width=Fraction(1, 1 << 200),
            deadline=verifier.time.monotonic() + 30,
        )


def test_paired_dfs_stack_and_panel_caps_fail_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(verifier, "MAX_SIMPSON_DFS_STACK", 1)
    with pytest.raises(verifier.IndependentVerificationFailure, match="DFS stack cap"):
        verifier._paired_root_local_bump_tables(
            (Fraction(0), Fraction(1)),
            target_width=Fraction(1, 1 << 20),
            deadline=verifier.time.monotonic() + 30,
        )


def test_flat_tail_bounds_digests_and_precision_nesting_are_exact() -> None:
    verifier._verify_support_policy_digests()
    coordinate = Fraction(4_095, 4_096)
    primary, primary_tail = verifier._bump_value_enclosure_with_tail(
        coordinate,
        precision=verifier.PRIMARY_BITS,
    )
    sentinel, sentinel_tail = verifier._bump_value_enclosure_with_tail(
        coordinate,
        precision=verifier.SENTINEL_BITS,
    )
    assert primary_tail is sentinel_tail is True
    assert primary.exact() == verifier.ExactInterval(Fraction(0), verifier.FLAT_TAIL_BUMP_UPPER)
    assert primary.lower <= sentinel.lower <= sentinel.upper <= primary.upper
    for precision in (verifier.PRIMARY_BITS, verifier.SENTINEL_BITS):
        bound, used_tail = verifier._bump_fourth_derivative_bound_with_tail_mpq(
            coordinate,
            Fraction(1),
            precision=precision,
        )
        assert used_tail is True
        assert verifier._mpq_exact_fraction(bound) == verifier.FLAT_TAIL_M4_UPPER


def test_coordinate_exact_component_and_pre_mpq_denominator_caps_fail_closed() -> None:
    over_coordinate_cap = Fraction(1, 1 << verifier.MAX_DYADIC_COORDINATE_COMPONENT_BITS)
    with pytest.raises(verifier.IndependentVerificationFailure, match="coordinate component cap"):
        verifier.bump_value_enclosure(over_coordinate_cap)

    over_exact_cap = Fraction(1, 1 << verifier.MAX_SIMPSON_EXACT_COMPONENT_BITS)
    with pytest.raises(verifier.IndependentVerificationFailure, match="exact component cap"):
        verifier._fraction_exact_mpq(over_exact_cap)

    mpfr_with_large_exact_denominator = verifier._mpfr_fraction(
        Fraction(1, 1 << verifier.MAX_MPFR_TO_MPQ_DENOMINATOR_BITS),
        verifier.PRIMARY_BITS,
        verifier.gmpy2.RoundDown,
    )
    with pytest.raises(
        verifier.IndependentVerificationFailure,
        match="denominator cap exceeded before MPQ conversion",
    ):
        verifier._support_mpfr_exact_mpq(mpfr_with_large_exact_denominator)

    source = Path(verifier.__file__).read_text("utf-8")
    assert source.count("gmpy2.mpq(value)") == 1


def test_semantic_core_drops_contact_arrays_before_support(
    parsed_candidate: verifier.ParsedCandidate,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    authority = verifier.load_frozen_geometry_authority(REPORT_ROOT)
    events: list[str] = []
    monkeypatch.setattr(verifier, "parse_candidate_bundle", lambda *_args: parsed_candidate)
    monkeypatch.setattr(verifier, "load_frozen_geometry_authority", lambda *_args: authority)
    monkeypatch.setattr(verifier, "verify_exact_file", lambda *_args, **_kwargs: b"{}")
    monkeypatch.setattr(
        verifier,
        "verify_contact_rows",
        lambda candidate, _authority: events.append(f"contact:{len(candidate.contacts)}") or {},
    )

    def support(candidate: verifier.ParsedCandidate, *_args: object, **_kwargs: object):
        events.append(f"support:{len(candidate.contacts)}")
        return {}, object()

    monkeypatch.setattr(verifier, "verify_support_rows", support)
    snapshots = iter((parsed_candidate.tree, parsed_candidate.partition_tree))
    monkeypatch.setattr(verifier, "inventory_candidate_tree", lambda *_args: next(snapshots))
    monkeypatch.setattr(verifier, "_validated_root_directory", lambda root, **_kwargs: root)
    monkeypatch.setattr(verifier, "_build_semantic_receipt", lambda *_args: {"status": "probe"})
    assert verifier.verify_semantic_core(REPORT_ROOT, BUNDLE_ROOT) == {"status": "probe"}
    assert events == [f"contact:{len(parsed_candidate.contacts)}", "support:0"]
    monkeypatch.setattr(verifier, "MAX_SIMPSON_DFS_STACK", 65)
    monkeypatch.setattr(verifier, "MAX_SIMPSON_PANELS", 1)
    with pytest.raises(verifier.IndependentVerificationFailure, match="panel cap"):
        verifier._paired_root_local_bump_tables(
            (Fraction(0), Fraction(1)),
            target_width=Fraction(1, 1 << 20),
            deadline=verifier.time.monotonic() + 30,
        )


def test_static_source_never_constructs_forbidden_scientific_objects() -> None:
    source = Path(verifier.__file__).read_text("utf-8")
    tree = ast.parse(source)
    called = {
        node.func.attr if isinstance(node.func, ast.Attribute) else node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, (ast.Attribute, ast.Name))
    }
    for forbidden in (
        "PackedKernelInputs",
        "build_physical_killing_intervals_v2",
        "build_packed_tensor_kernel",
        "propagate_uniformization",
        "run_f0",
    ):
        assert forbidden not in called
    assert not any(name.startswith("rate_defined_tensor_f0") for name in called)
    assert math.prod([113, 113]) == 12_769


def _child_wire_argv(
    report_root: Path,
    bundle_root: Path,
    semantic_path: Path,
    observation_path: Path,
    *,
    nonce: str = "ab" * 32,
    run_index: str = "0",
) -> list[str]:
    return [
        "--report-root",
        str(report_root),
        "--bundle",
        str(bundle_root),
        "--semantic-receipt",
        str(semantic_path),
        "--observation",
        str(observation_path),
        "--launch-nonce",
        nonce,
        "--run-index",
        run_index,
    ]


def _minimal_semantic_success_receipt() -> dict[str, object]:
    return {
        "candidate": {},
        "contact_summary": {},
        "flags": {},
        "frozen_sources": {},
        "independent_partition_semantic_sha256s": [],
        "precision_bits": {},
        "runtime": {},
        "schema": verifier.CHILD_SEMANTIC_SUCCESS_SCHEMA,
        "status": verifier.PASS_STATUS,
        "support_policy_digests": {},
        "support_summary": {},
        "verifier_staged_file_sha256_at_receipt": "0" * 64,
    }


def test_child_file_wire_success_is_exclusive_stable_bound_and_stdout_only(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    semantic_path = tmp_path / "semantic.json"
    observation_path = tmp_path / "observation.json"
    monkeypatch.setattr(
        verifier,
        "verify_semantic_core",
        lambda *_args: _minimal_semantic_success_receipt(),
    )
    exit_code = verifier._main(
        _child_wire_argv(REPORT_ROOT, BUNDLE_ROOT, semantic_path, observation_path)
    )
    captured = capsys.readouterr()
    assert exit_code == 0
    assert captured.err == ""
    semantic_bytes = semantic_path.read_bytes()
    observation_bytes = observation_path.read_bytes()
    semantic = json.loads(semantic_bytes)
    observation = json.loads(observation_bytes)
    acknowledgement = json.loads(captured.out)
    assert semantic == _minimal_semantic_success_receipt()
    assert semantic_bytes == verifier.canonical_json_bytes(semantic)
    assert set(observation) == verifier._CHILD_OBSERVATION_KEYS
    assert observation_bytes == verifier.canonical_json_bytes(observation)
    assert observation["schema"] == verifier.CHILD_OBSERVATION_SCHEMA
    assert observation["launch_nonce"] == "ab" * 32
    assert observation["run_index"] == 0
    assert observation["status"] == verifier.PASS_STATUS
    assert observation["semantic_receipt_byte_length"] == len(semantic_bytes)
    assert observation["semantic_receipt_sha256"] == verifier.sha256_bytes(semantic_bytes)
    assert set(acknowledgement) == verifier._CHILD_BOUND_ACK_KEYS
    assert acknowledgement["schema"] == verifier.CHILD_BOUND_ACK_SCHEMA
    assert acknowledgement["semantic_receipt_sha256"] == verifier.sha256_bytes(semantic_bytes)
    assert acknowledgement["observation_sha256"] == verifier.sha256_bytes(observation_bytes)
    assert captured.out == verifier.canonical_json_bytes(acknowledgement).decode("ascii")


def test_child_file_wire_semantic_hold_still_publishes_two_bound_files(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    semantic_path = tmp_path / "semantic-hold.json"
    observation_path = tmp_path / "observation-hold.json"

    def semantic_hold(*_args: object) -> dict[str, object]:
        raise verifier.IndependentVerificationFailure(verifier.HOLD_SOURCE, "bounded probe")

    monkeypatch.setattr(verifier, "verify_semantic_core", semantic_hold)
    exit_code = verifier._main(
        _child_wire_argv(
            REPORT_ROOT,
            BUNDLE_ROOT,
            semantic_path,
            observation_path,
            run_index="1",
        )
    )
    captured = capsys.readouterr()
    assert exit_code == 2
    assert captured.err == ""
    semantic_bytes = semantic_path.read_bytes()
    observation_bytes = observation_path.read_bytes()
    assert json.loads(semantic_bytes) == {
        "schema": verifier.CHILD_SEMANTIC_HOLD_SCHEMA,
        "status": verifier.HOLD_SOURCE,
    }
    observation = json.loads(observation_bytes)
    acknowledgement = json.loads(captured.out)
    assert observation["status"] == verifier.HOLD_SOURCE
    assert observation["run_index"] == 1
    assert acknowledgement["status"] == verifier.HOLD_SOURCE
    assert acknowledgement["run_index"] == 1
    assert acknowledgement["semantic_receipt_sha256"] == verifier.sha256_bytes(semantic_bytes)
    assert acknowledgement["observation_sha256"] == verifier.sha256_bytes(observation_bytes)


def test_child_publication_failure_emits_only_two_key_unbound_hold(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    semantic_path = tmp_path / "semantic-publication-failure.json"
    observation_path = tmp_path / "observation-publication-failure.json"
    monkeypatch.setattr(
        verifier,
        "verify_semantic_core",
        lambda *_args: _minimal_semantic_success_receipt(),
    )

    def fail_publication(*_args: object, **_kwargs: object) -> bytes:
        raise verifier.IndependentVerificationFailure(verifier.HOLD_API, "publication probe")

    monkeypatch.setattr(verifier, "_publish_exclusive_stable", fail_publication)
    assert (
        verifier._main(_child_wire_argv(REPORT_ROOT, BUNDLE_ROOT, semantic_path, observation_path))
        == 2
    )
    captured = capsys.readouterr()
    assert captured.err == ""
    assert json.loads(captured.out) == verifier._unbound_hold_ack()
    assert set(json.loads(captured.out)) == {"schema", "status"}
    assert not semantic_path.exists()
    assert not observation_path.exists()


def test_child_cli_output_path_and_scalar_mutations_are_unbound_api_holds(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    report_root = tmp_path / "report"
    bundle_root = report_root / "bundle"
    output_root = tmp_path / "output"
    bundle_root.mkdir(parents=True)
    output_root.mkdir()
    semantic_path = output_root / "semantic.json"
    observation_path = output_root / "observation.json"
    base = _child_wire_argv(report_root, bundle_root, semantic_path, observation_path)
    mutations = []
    relative_report = base.copy()
    relative_report[1] = "relative-report"
    mutations.append(relative_report)
    relative_output = base.copy()
    relative_output[5] = "semantic.json"
    mutations.append(relative_output)
    duplicate = base.copy()
    duplicate[8:10] = ["--run-index", "0"]
    mutations.append(duplicate)
    uppercase_nonce = base.copy()
    uppercase_nonce[9] = "AB" * 32
    mutations.append(uppercase_nonce)
    wrong_index = base.copy()
    wrong_index[11] = "2"
    mutations.append(wrong_index)
    same_outputs = base.copy()
    same_outputs[7] = same_outputs[5]
    mutations.append(same_outputs)
    output_in_input = base.copy()
    output_in_input[5] = str(report_root / "semantic.json")
    mutations.append(output_in_input)

    monkeypatch.setattr(
        verifier,
        "verify_semantic_core",
        lambda *_args: pytest.fail("unsafe CLI must fail before semantic execution"),
    )
    expected = verifier.canonical_json_bytes(verifier._unbound_hold_ack()).decode("ascii")
    for mutated in mutations:
        assert verifier._main(mutated) == 2
        captured = capsys.readouterr()
        assert captured.err == ""
        assert captured.out == expected
    assert not semantic_path.exists()
    assert not observation_path.exists()


def test_preexisting_or_symlink_output_is_preserved_and_emits_unbound_hold(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    semantic_path = tmp_path / "semantic.json"
    observation_path = tmp_path / "observation.json"
    semantic_path.write_bytes(b"preexisting")
    monkeypatch.setattr(
        verifier,
        "verify_semantic_core",
        lambda *_args: pytest.fail("pre-existing output must fail before semantic execution"),
    )
    argv = _child_wire_argv(REPORT_ROOT, BUNDLE_ROOT, semantic_path, observation_path)
    assert verifier._main(argv) == 2
    captured = capsys.readouterr()
    assert captured.err == ""
    assert json.loads(captured.out) == verifier._unbound_hold_ack()
    assert semantic_path.read_bytes() == b"preexisting"
    assert not observation_path.exists()

    semantic_path.unlink()
    semantic_path.symlink_to(tmp_path / "missing-target")
    assert verifier._main(argv) == 2
    captured = capsys.readouterr()
    assert captured.err == ""
    assert json.loads(captured.out) == verifier._unbound_hold_ack()
    assert semantic_path.is_symlink()
    assert not observation_path.exists()


def test_exclusive_publication_flags_caps_and_stable_reread_are_enforced(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    real_open = os.open
    create_flags: list[int] = []

    def recording_open(
        path: str | bytes | os.PathLike[str] | os.PathLike[bytes],
        flags: int,
        mode: int = 0o777,
        *,
        dir_fd: int | None = None,
    ) -> int:
        if flags & os.O_CREAT:
            create_flags.append(flags)
        return real_open(path, flags, mode, dir_fd=dir_fd)

    monkeypatch.setattr(os, "open", recording_open)
    path = tmp_path / "exclusive.json"
    assert verifier._publish_exclusive_stable(path, b"abc", maximum_bytes=3) == b"abc"
    assert len(create_flags) == 1
    assert create_flags[0] & os.O_WRONLY
    assert create_flags[0] & os.O_CREAT
    assert create_flags[0] & os.O_EXCL
    assert create_flags[0] & getattr(os, "O_NOFOLLOW", 0)
    with pytest.raises(verifier.IndependentVerificationFailure, match="exclusive"):
        verifier._publish_exclusive_stable(path, b"abc", maximum_bytes=3)
    with pytest.raises(verifier.IndependentVerificationFailure, match="byte cap"):
        verifier._publish_exclusive_stable(tmp_path / "too-large", b"abcd", maximum_bytes=3)

    monkeypatch.setattr(
        verifier,
        "_read_regular_stable_at",
        lambda *_args, **_kwargs: b"mutated",
    )
    with pytest.raises(verifier.IndependentVerificationFailure, match="changed on reread"):
        verifier._publish_exclusive_stable(tmp_path / "mutated.json", b"original", maximum_bytes=8)


def test_peak_rss_is_normalized_for_darwin_and_linux(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        verifier.resource,
        "getrusage",
        lambda *_args: types.SimpleNamespace(ru_maxrss=123),
    )
    monkeypatch.setattr(verifier.sys, "platform", "darwin")
    assert verifier._peak_rss_bytes() == 123
    monkeypatch.setattr(verifier.sys, "platform", "linux")
    assert verifier._peak_rss_bytes() == 123 * 1_024
    monkeypatch.setattr(verifier.sys, "platform", "other")
    with pytest.raises(verifier.IndependentVerificationFailure, match="platform"):
        verifier._peak_rss_bytes()


def test_root_m4_precomputation_checks_deadline_before_first_derivative_bound(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        verifier,
        "_bump_fourth_derivative_bound_with_tail_mpq",
        lambda *_args, **_kwargs: pytest.fail("expired root M4 must not be evaluated"),
    )
    with pytest.raises(verifier.IndependentVerificationFailure) as failure:
        verifier._paired_root_local_bump_tables(
            (Fraction(0), Fraction(1)),
            target_width=Fraction(1),
            deadline=0.0,
        )
    assert failure.value.code == verifier.HOLD_TIMEOUT


def test_root_m4_precomputation_rechecks_deadline_between_precisions(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[int] = []

    def derivative(*_args: object, **_kwargs: object) -> tuple[verifier.gmpy2.mpq, bool]:
        calls.append(1)
        return verifier.gmpy2.mpq(0), False

    clock = iter((0.0, 2.0))
    monkeypatch.setattr(verifier, "_bump_fourth_derivative_bound_with_tail_mpq", derivative)
    monkeypatch.setattr(verifier.time, "monotonic", lambda: next(clock))
    with pytest.raises(verifier.IndependentVerificationFailure) as failure:
        verifier._paired_root_local_bump_tables(
            (Fraction(0), Fraction(1)),
            target_width=Fraction(1),
            deadline=1.0,
        )
    assert failure.value.code == verifier.HOLD_TIMEOUT
    assert calls == [1]
