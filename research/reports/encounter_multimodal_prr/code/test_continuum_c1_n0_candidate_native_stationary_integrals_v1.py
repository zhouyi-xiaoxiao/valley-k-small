"""Functional tests for candidate-native stationary physical integrals."""

from __future__ import annotations

import ast
import concurrent.futures
import hashlib
import importlib.util
import json
import os
import stat
import sys
from decimal import Decimal, localcontext
from fractions import Fraction
from pathlib import Path
from typing import Any

import pytest

CODE = Path(__file__).resolve().parent
REPORT = CODE.parent
PRODUCER_PATH = CODE / "build_continuum_c1_n0_candidate_native_stationary_integrals_v1.py"
VERIFIER_PATH = CODE / "validate_continuum_c1_n0_candidate_native_stationary_integrals_v1.py"
CONFIGURATION_RELATIVE = Path("artifacts/data/physical_configuration_family_control_free_v1.json")
CONFIGURATION_DESIGN_RELATIVE = Path("notes/positive_b_fixed_control_robustness_design_v2.md")
CONFIGURATION_IMPLEMENTATION_RELATIVE = Path("code/rate_defined_tensor_f0.py")
CONFIGURATION_INITIAL_GEOMETRY_RELATIVE = Path(
    "artifacts/data/physical_initial_analytic_source_v1.json"
)
CONFIGURATION_TEST_RELATIVE = Path("code/test_rate_defined_tensor_f0.py")
FACTORIZATION_RELATIVE = Path("artifacts/data/continuum_c1_factorization_source_v2_candidate.json")
FACTORIZATION_INITIAL_PARTITION_RELATIVE = Path(
    "artifacts/data/physical_production_initial_stream_v1/bundle.json"
)
FACTORIZATION_KILLING_GEOMETRY_RELATIVE = Path(
    "artifacts/data/physical_killing_geometry_source_v1.json"
)
FORMULA_RELATIVE = Path("artifacts/data/continuum_c1_ideal_formula_source_v1.json")
MEMBER_RELATIVE = Path(
    "artifacts/data/continuum_c1_c2_n0_predecessor_authority_candidate_v1/"
    "continuum_c1_c2_n0_member_spec_v3_candidate.json"
)
METHOD_RELATIVE = Path(
    "artifacts/data/continuum_c1_c2_n0_method_parameter_registry_v3_candidate.json"
)
REFERENCE_RELATIVE = Path("artifacts/data/continuum_c1_reference_density_source_v1.json")


def _load(name: str, path: Path) -> Any:
    specification = importlib.util.spec_from_file_location(name, path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


producer = _load("candidate_stationary_producer_tests", PRODUCER_PATH)
verifier = _load("candidate_stationary_verifier_tests", VERIFIER_PATH)


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def canonical(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True) + "\n").encode("ascii")


def digest(domain: str, value: Any) -> str:
    return sha256(domain.encode("ascii") + b"\0" + canonical(value))


def immutable_write(path: Path, value: Any) -> bytes:
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = value if type(value) is bytes else canonical(value)
    path.write_bytes(raw)
    path.chmod(0o400)
    return raw


def replace_immutable(path: Path, value: Any) -> bytes:
    path.chmod(0o600)
    raw = value if type(value) is bytes else canonical(value)
    path.write_bytes(raw)
    path.chmod(0o400)
    return raw


def file_pin(path: Path) -> dict[str, str]:
    return {"path": str(path), "sha256": sha256(path.read_bytes())}


def _parameter_entry(identifier: str, parameters: dict[str, Any]) -> dict[str, Any]:
    return {
        "method_parameter_sha256": digest(producer.PARAMETER_DIGEST_DOMAIN, parameters),
        "parameter_id": identifier,
        "parameters": parameters,
    }


def build_method_registry() -> dict[str, Any]:
    primary = {
        "aggregation": "exact_Fraction_endpoint_sums_and_nonnegative_products",
        "dense_tensor_materialized": False,
        "precision_bits": 320,
        "rounding_mode": "directed_RoundDown_RoundUp",
        "source_role_scope": ["role9_stationary_physical_integral"],
    }
    sentinel = {
        "containment_relation": producer.GENERIC_CONTAINMENT,
        "independent_backend": False,
        "precision_bits": 640,
        "rounding_mode": "directed_RoundDown_RoundUp",
        "source_role_scope": ["role9_stationary_physical_integral"],
    }
    exact = {
        "arithmetic": "Python_Fraction_exact_reduced_rationals",
        "precision_bits": "unbounded_integer_fraction",
        "rounding_mode": "exact",
        "source_role_scope": [
            "role8_raw_axis_formula_primitive",
            "role9_stationary_physical_integral",
            "same_member_mass_flux_composition",
            "symbolic_killing_composition",
        ],
    }
    entries = [
        _parameter_entry(producer.PRIMARY_PARAMETER_ID, primary),
        _parameter_entry(producer.SENTINEL_PARAMETER_ID, sentinel),
        _parameter_entry(
            "raw_flux_directed_mpfr_320_v2",
            {
                "aggregation": "exact_Fraction_endpoint_algebra",
                "common_kappa_rule": "intersection_after_formula_witness",
                "precision_bits": 320,
                "rounding_mode": "directed_RoundDown_RoundUp",
                "source_role_scope": ["role8_raw_axis_formula_primitive"],
            },
        ),
        _parameter_entry(
            "raw_flux_directed_mpfr_640_sentinel_v2",
            {
                "containment_relation": producer.GENERIC_CONTAINMENT,
                "independent_backend": False,
                "precision_bits": 640,
                "rounding_mode": "directed_RoundDown_RoundUp",
                "source_role_scope": ["role8_raw_axis_formula_primitive"],
            },
        ),
        _parameter_entry(
            "raw_flux_binary64_decode_v2",
            {
                "decode": "exact_binary64_endpoint_to_reduced_dyadic_fraction",
                "precision_bits": 53,
                "rounding_mode": "stored_outward_endpoints",
                "source_role_scope": ["role8_raw_axis_formula_primitive"],
            },
        ),
        _parameter_entry(producer.EXACT_PARAMETER_ID, exact),
        _parameter_entry(
            "killing_contact_profile_mpfr_192_v2",
            {
                "contact_fraction_record_format": ">dd",
                "panels_per_unit": 16384,
                "precision_bits": 192,
                "rounding_mode": "directed_RoundDown_RoundUp",
                "source_role_scope": ["role10_killing_factor_geometry"],
                "support_density_record_format": ">dd",
            },
        ),
        _parameter_entry(
            "killing_analytic_disk_area_mpfr_256_v2",
            {
                "analytic_area_precision_bits": 256,
                "formula": "pi_times_radius_squared",
                "rounding_mode": "directed_RoundDown_RoundUp",
                "source_role_scope": ["role10_killing_factor_geometry"],
            },
        ),
        _parameter_entry(
            "killing_independent_simpson_remainder_v2",
            {
                "independent_backend": False,
                "maximum_panel_count": 4194304,
                "primary_precision_bits": 384,
                "remainder_rule": "rigorous_fourth_derivative_simpson_remainder",
                "sentinel_precision_bits": 512,
                "source_role_scope": ["role10_killing_factor_geometry"],
            },
        ),
        _parameter_entry(
            "killing_exact_full_cell_classification_v2",
            {
                "classification": (
                    "every_corner_of_every_exact_partition_segment_inside_or_on_contact_disk"
                ),
                "full_cell_serialization": "exact_[1,1]",
                "precision_bits": "exact_rational",
                "rounding_mode": "exact",
                "source_role_scope": ["role10_killing_factor_geometry"],
            },
        ),
    ]
    return {
        "claim_boundary": {key: False for key in sorted(producer._PARAMETER_CLAIM_KEYS)},
        "parameter_count": len(entries),
        "parameters": entries,
        "schema": producer.PARAMETER_SCHEMA,
        "status": producer.PARAMETER_STATUS,
    }


def rebuild_member_digests(member: dict[str, Any], configuration: dict[str, Any]) -> None:
    reference_parameters = member.pop("_test_reference_parameters")
    parameter_digest = digest("encounter-physical-parameter-bundle-v1", reference_parameters)
    for index, (binding, row) in enumerate(
        zip(member["n0_sequence_bindings"], configuration["configurations"], strict=True)
    ):
        binding["sequence_source_row_canonical_sha256"] = sha256(canonical(row))
        binding["physical_parameter_bundle_sha256"] = parameter_digest
        binding["configuration_geometry_sha256"] = digest(
            "encounter-configuration-geometry-v1",
            {
                "configuration_index": index,
                "configuration_row": row,
                "n0_partition_sha256s": [axis["partition_sha256"] for axis in binding["n0_axes"]],
            },
        )
    member["member_identity_sha256"] = digest(
        "encounter-continuum-c1-c2-n0-member-identity-v3",
        {
            "configuration_order": member["configuration_order"],
            "configuration_semantic_ids": member["configuration_semantic_ids"],
            "coordinate_order": list(producer.COORDINATES),
            "n0_sequence_bindings": member["n0_sequence_bindings"],
            "role_bindings_1_through_4": member["role_bindings"],
            "scalar_convention": member["member_semantics"]["scalar_convention"],
        },
    )


def clone_relative(root: Path, relative: Path) -> Path:
    source = REPORT / relative
    destination = root / relative
    immutable_write(destination, source.read_bytes())
    return destination


def make_fixture(tmp_path: Path) -> dict[str, Any]:
    root = tmp_path / "fixture"
    root.mkdir(mode=0o700, parents=True)
    output_dir = tmp_path / "output"
    output_dir.mkdir(mode=0o700)
    paths = {
        "configuration": clone_relative(root, CONFIGURATION_RELATIVE),
        "configuration_design": clone_relative(root, CONFIGURATION_DESIGN_RELATIVE),
        "configuration_implementation": clone_relative(root, CONFIGURATION_IMPLEMENTATION_RELATIVE),
        "configuration_initial_geometry": clone_relative(
            root, CONFIGURATION_INITIAL_GEOMETRY_RELATIVE
        ),
        "configuration_test": clone_relative(root, CONFIGURATION_TEST_RELATIVE),
        "factorization": clone_relative(root, FACTORIZATION_RELATIVE),
        "factorization_initial_partition_bundle": clone_relative(
            root, FACTORIZATION_INITIAL_PARTITION_RELATIVE
        ),
        "factorization_killing_geometry": clone_relative(
            root, FACTORIZATION_KILLING_GEOMETRY_RELATIVE
        ),
        "ideal_formula": clone_relative(root, FORMULA_RELATIVE),
        "member_spec": root / MEMBER_RELATIVE,
        "method_parameters": clone_relative(root, METHOD_RELATIVE),
        "reference_density": clone_relative(root, REFERENCE_RELATIVE),
    }
    configuration = json.loads(paths["configuration"].read_text("ascii"))
    factorization = json.loads(paths["factorization"].read_text("ascii"))
    formula = json.loads(paths["ideal_formula"].read_text("ascii"))
    reference = json.loads(paths["reference_density"].read_text("ascii"))
    member = json.loads((REPORT / MEMBER_RELATIVE).read_text("ascii"))
    member["role_bindings"]["factorization_source"] = {
        "path": FACTORIZATION_RELATIVE.as_posix(),
        "sha256": producer.FACTORIZATION_SHA256,
    }
    member["_test_reference_parameters"] = reference["physical_parameter_bundle"]
    rebuild_member_digests(member, configuration)
    immutable_write(paths["member_spec"], member)
    assert paths["method_parameters"].read_bytes() == canonical(build_method_registry())
    assert sha256(paths["method_parameters"].read_bytes()) == (
        "6c1879edaefe5f99da4fffcb76e12466862577376c305e14c857b880067e3b32"
    )
    partition_paths: dict[tuple[int, str], Path] = {}
    partitions: list[dict[str, Any]] = []
    for index, binding in enumerate(member["n0_sequence_bindings"]):
        for axis in binding["n0_axes"]:
            coordinate = axis["coordinate"]
            relative = Path(axis["partition_report_relative_path"])
            path = clone_relative(root, relative)
            partition_paths[(index, coordinate)] = path
            partitions.append(
                {
                    "configuration_index": index,
                    "coordinate": coordinate,
                    "member_report_relative_path": relative.as_posix(),
                    **file_pin(path),
                }
            )
    objects = {
        "configuration": configuration,
        "factorization": factorization,
        "formula": formula,
        "member": member,
        "reference": reference,
    }
    output_path = output_dir / "stationary.json"
    request_path = root / "request.json"
    request = {
        "code_inputs": {
            "producer": file_pin(PRODUCER_PATH),
            "verifier": file_pin(VERIFIER_PATH),
        },
        "input_authorities": {role: file_pin(path) for role, path in paths.items()},
        "method_selection": {
            "exact_parameter_id": producer.EXACT_PARAMETER_ID,
            "primary_parameter_id": producer.PRIMARY_PARAMETER_ID,
            "sentinel_parameter_id": producer.SENTINEL_PARAMETER_ID,
        },
        "output": {
            "path": str(output_path),
            "schema": producer.OUTPUT_SCHEMA,
        },
        "partitions": partitions,
        "runtime_requirements": producer._runtime_versions(),
        "schema": producer.REQUEST_SCHEMA,
        "status": "RESULT_BLIND_REQUEST_NOT_EXECUTION_RESULT",
    }
    immutable_write(request_path, request)
    return {
        "member_path": paths["member_spec"],
        "method_path": paths["method_parameters"],
        "objects": objects,
        "output_path": output_path,
        "partition_paths": partition_paths,
        "paths": paths,
        "request": request,
        "request_path": request_path,
        "root": root,
    }


@pytest.fixture
def fixture(tmp_path: Path) -> dict[str, Any]:
    return make_fixture(tmp_path)


def test_production_form_twelve_row_current_family_regression(
    fixture: dict[str, Any],
) -> None:
    request_path = fixture["request_path"]
    output_path = fixture["output_path"]
    assert producer.main(["--request", str(request_path), "--output", str(output_path)]) == 0
    assert stat.S_IMODE(output_path.stat().st_mode) == 0o400
    assert output_path.stat().st_nlink == 1
    artifact = json.loads(output_path.read_text("ascii"))
    assert artifact["schema"] == producer.OUTPUT_SCHEMA
    assert artifact["summary"]["configuration_count"] == 12
    assert artifact["summary"]["factorized_axis_cell_count"] == 5037
    assert artifact["summary"]["total_virtual_tensor_state_count"] == 34787462
    assert set(artifact["source_pins"]["input_authorities"]) == producer._INPUT_AUTHORITY_ROLES
    assert len(artifact["source_pins"]["input_authorities"]) == 12
    assert len(fixture["request"]["partitions"]) == 36
    assert fixture["objects"]["member"]["reconstruction_counts"] == {
        "axis_cell_count": 5037,
        "axis_count": 36,
        "axis_edge_count": 5013,
        "configuration_count": 12,
        "periodic_seam_count": 12,
        "profile_index_count": 48,
        "total_virtual_tensor_state_count": 34787462,
    }
    alignments = {
        row[coordinate]["alignment"]
        for row in fixture["objects"]["configuration"]["configurations"]
        for coordinate in producer.COORDINATES
    }
    assert "vertex_centred_reflecting_dual" in alignments
    assert "cell_centred_periodic_half_shift" in alignments
    assert len(artifact["rows"][0]["axes"]) == 3
    assert (
        sum(len(axis["M_x_pi_cell_intervals"]) for row in artifact["rows"] for axis in row["axes"])
        == 5037
    )
    lower = Fraction(artifact["rows"][0]["M_L_joint_interval"]["lower_exact_p_over_q"])
    upper = Fraction(artifact["rows"][0]["M_L_joint_interval"]["upper_exact_p_over_q"])
    assert 0 < lower <= upper <= 1
    assert (
        producer.main(["--request", str(request_path), "--output", str(output_path), "--check"])
        == 0
    )
    receipt = verifier.validate(request_path, output_path)
    assert receipt["status"] == "PASS_INDEPENDENT_COMPLETE_RECOMPUTATION"


def test_independent_analytic_and_reflection_symmetry_oracle(
    fixture: dict[str, Any],
) -> None:
    payload = producer.build_from_request(fixture["request_path"], fixture["output_path"])
    artifact = json.loads(payload)
    row = artifact["rows"][0]
    axes = {axis["coordinate"]: axis for axis in row["axes"]}
    cells = axes["relative_parallel"]["M_x_pi_cell_intervals"]
    assert {key: cells[0][key] for key in ("lower_exact_p_over_q", "upper_exact_p_over_q")} == {
        key: cells[-1][key] for key in ("lower_exact_p_over_q", "upper_exact_p_over_q")
    }
    periodic_cells = axes["relative_perpendicular"]["M_x_pi_cell_intervals"]
    periodic_size = fixture["objects"]["configuration"]["configurations"][0][
        "relative_perpendicular"
    ]["size"]
    assert {
        (cell["lower_exact_p_over_q"], cell["upper_exact_p_over_q"]) for cell in periodic_cells
    } == {(f"1/{periodic_size}", f"1/{periodic_size}")}
    joint = row["M_L_joint_interval"]
    configuration = fixture["objects"]["configuration"]
    parameters = fixture["objects"]["reference"]["physical_parameter_bundle"]
    first_row = configuration["configurations"][0]

    def decimal_pi() -> Decimal:
        one = Decimal(1)
        a = one
        b = one / Decimal(2).sqrt()
        total = Decimal("0.25")
        power = one
        for _ in range(10):
            next_a = (a + b) / 2
            b = (a * b).sqrt()
            total -= power * (a - next_a) ** 2
            a = next_a
            power *= 2
        return (a + b) ** 2 / (4 * total)

    def decimal_erf(value: Decimal, pi: Decimal) -> Decimal:
        term = value
        total = value
        square = value * value
        threshold = Decimal(1).scaleb(-170)
        for index in range(1, 2_000):
            term *= -square / index
            increment = term / (2 * index + 1)
            total += increment
            if abs(increment) < threshold:
                return 2 * total / pi.sqrt()
        raise AssertionError("Decimal erf series did not converge")

    def as_decimal(hexadecimal: str) -> Decimal:
        exact = Fraction.from_float(float.fromhex(hexadecimal))
        return Decimal(exact.numerator) / Decimal(exact.denominator)

    def gaussian_mass(
        axis: dict[str, Any], coefficient: Decimal, centre: Decimal, pi: Decimal
    ) -> Decimal:
        lower = as_decimal(axis["lower_binary64_hex"])
        upper = as_decimal(axis["upper_binary64_hex"])
        root = coefficient.sqrt()
        return (
            decimal_erf(root * (upper - centre), pi) - decimal_erf(root * (lower - centre), pi)
        ) / 2

    with localcontext() as context:
        context.prec = 190
        stiffness = as_decimal(parameters["ou_stiffness_binary64_hex"])
        diffusion = as_decimal(parameters["particle_diffusion_binary64_hex"])
        mean = as_decimal(parameters["ou_mean_binary64_hex"])
        pi = decimal_pi()
        independent_closed_form = gaussian_mass(
            first_row["midpoint"], stiffness / diffusion, mean, pi
        ) * gaussian_mass(
            first_row["relative_parallel"],
            stiffness / (4 * diffusion),
            Decimal(0),
            pi,
        )
        lower = Fraction(joint["lower_exact_p_over_q"])
        upper = Fraction(joint["upper_exact_p_over_q"])
        decimal_lower = Decimal(lower.numerator) / Decimal(lower.denominator)
        decimal_upper = Decimal(upper.numerator) / Decimal(upper.denominator)
        assert decimal_lower <= independent_closed_form <= decimal_upper


def test_request_contains_no_result_or_observed_output_digest(
    fixture: dict[str, Any],
) -> None:
    request = fixture["request"]
    assert request["schema"].endswith("_request_v2")
    assert set(request["input_authorities"]) == producer._INPUT_AUTHORITY_ROLES
    keys = producer._walk_keys(request)
    assert not any(
        fragment in key.lower()
        for key in keys
        for fragment in (
            "artifact_sha",
            "expected_output",
            "expected_result",
            "observed",
            "output_sha",
            "production_result",
            "result_sha",
            "role9_result",
            "role10_result",
        )
    )
    serialized = canonical(request).decode("ascii")
    assert "continuum_c1_stationary_integral_source_v1.json" not in serialized
    assert "continuum_c1_fixed_row_raw_flux_source_v1.json" not in serialized
    assert "physical_production_killing_geometry_v1" not in serialized


def test_absolute_cli_and_previously_absent_output_are_enforced(
    fixture: dict[str, Any],
) -> None:
    assert producer.main(["--request", "relative.json", "--output", "relative.out"]) == 2
    output_path = fixture["output_path"]
    output_path.write_text("occupied", encoding="ascii")
    output_path.chmod(0o400)
    with pytest.raises(producer.CandidateStationaryFailure) as captured:
        producer._publish(output_path, b"{}\n")
    assert captured.value.code == producer.HOLD_OUTPUT
    assert "already exists" in str(captured.value)


def test_interrupted_stage_never_exposes_partial_final(
    fixture: dict[str, Any], monkeypatch: pytest.MonkeyPatch
) -> None:
    output_path = fixture["output_path"]

    def fail_link(*args: Any, **kwargs: Any) -> None:
        del args, kwargs
        raise OSError("injected no-replace publication failure")

    monkeypatch.setattr(producer.os, "link", fail_link)
    with pytest.raises(producer.CandidateStationaryFailure) as captured:
        producer._publish(output_path, b'{"complete":true}\n')
    assert captured.value.code == producer.HOLD_OUTPUT
    assert not os.path.lexists(output_path)
    assert not list(output_path.parent.glob(f".{output_path.name}.*.stage"))


@pytest.mark.parametrize("interrupt_type", [KeyboardInterrupt, SystemExit])
def test_post_open_interrupt_transaction_removes_owned_stage(
    fixture: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
    interrupt_type: type[BaseException],
) -> None:
    output_path = fixture["output_path"]
    original_await_ready = producer.StageCreationTransaction.await_ready
    transactions: list[Any] = []
    descriptors_before = frozenset(os.listdir("/dev/fd"))

    def ready_then_interrupt(transaction: Any) -> None:
        original_await_ready(transaction)
        transactions.append(transaction)
        raise interrupt_type("injected after successful stage open")

    monkeypatch.setattr(
        producer.StageCreationTransaction,
        "await_ready",
        ready_then_interrupt,
    )
    with pytest.raises(interrupt_type, match="successful stage open"):
        producer._publish(output_path, b'{"complete":true}\n')
    assert len(transactions) == 1
    assert transactions[0].descriptor is None
    assert not transactions[0]._thread.is_alive()
    assert frozenset(os.listdir("/dev/fd")) == descriptors_before
    assert not os.path.lexists(output_path)
    assert not list(output_path.parent.glob(f".{output_path.name}.*.stage"))


def test_post_open_interrupt_preserves_metadata_equivalent_foreign_stage(
    fixture: dict[str, Any], monkeypatch: pytest.MonkeyPatch
) -> None:
    output_path = fixture["output_path"]
    original_await_ready = producer.StageCreationTransaction.await_ready
    original_open = os.open
    original_close = os.close
    foreign_identity: tuple[int, int] | None = None
    transaction_seen: Any = None
    descriptors_before = frozenset(os.listdir("/dev/fd"))

    def replace_then_interrupt(transaction: Any) -> None:
        nonlocal foreign_identity, transaction_seen
        original_await_ready(transaction)
        transaction_seen = transaction
        assert transaction.identity is not None
        os.unlink(transaction.leaf, dir_fd=transaction.parent_descriptor)
        foreign = original_open(
            transaction.leaf,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_CLOEXEC | os.O_NOFOLLOW,
            0o444,
            dir_fd=transaction.parent_descriptor,
        )
        metadata = os.fstat(foreign)
        foreign_identity = metadata.st_dev, metadata.st_ino
        assert foreign_identity != transaction.identity
        assert metadata.st_uid == os.getuid()
        assert metadata.st_nlink == 1
        assert metadata.st_size == 0
        assert stat.S_IMODE(metadata.st_mode) == 0o444
        original_close(foreign)
        raise KeyboardInterrupt("injected after foreign stage replacement")

    monkeypatch.setattr(
        producer.StageCreationTransaction,
        "await_ready",
        replace_then_interrupt,
    )
    with pytest.raises(KeyboardInterrupt, match="foreign stage replacement"):
        producer._publish(output_path, b'{"owned":true}\n')
    assert transaction_seen is not None
    assert transaction_seen.descriptor is None
    assert not transaction_seen._thread.is_alive()
    assert frozenset(os.listdir("/dev/fd")) == descriptors_before
    assert not os.path.lexists(output_path)
    stages = list(output_path.parent.glob(f".{output_path.name}.*.stage"))
    assert len(stages) == 1
    metadata = stages[0].stat()
    assert (metadata.st_dev, metadata.st_ino) == foreign_identity
    assert metadata.st_uid == os.getuid()
    assert metadata.st_nlink == 1
    assert metadata.st_size == 0
    assert stat.S_IMODE(metadata.st_mode) == 0o444


def test_write_interrupt_rolls_back_owned_stage(
    fixture: dict[str, Any], monkeypatch: pytest.MonkeyPatch
) -> None:
    output_path = fixture["output_path"]
    real_write = producer.os.write
    interrupted = False

    def interrupting_write(descriptor: int, data: Any) -> int:
        nonlocal interrupted
        if not interrupted:
            interrupted = True
            real_write(descriptor, data[:1])
            raise KeyboardInterrupt("injected after partial stage write")
        return real_write(descriptor, data)

    monkeypatch.setattr(producer.os, "write", interrupting_write)
    with pytest.raises(KeyboardInterrupt, match="partial stage write"):
        producer._publish(output_path, b'{"complete":true}\n')
    assert interrupted
    assert not os.path.lexists(output_path)
    assert not list(output_path.parent.glob(f".{output_path.name}.*.stage"))


def test_post_link_interrupt_rolls_back_unacknowledged_final(
    fixture: dict[str, Any], monkeypatch: pytest.MonkeyPatch
) -> None:
    output_path = fixture["output_path"]
    real_link = producer.os.link

    def interrupting_link(*args: Any, **kwargs: Any) -> None:
        real_link(*args, **kwargs)
        raise KeyboardInterrupt("injected after successful no-replace link")

    monkeypatch.setattr(producer.os, "link", interrupting_link)
    with pytest.raises(KeyboardInterrupt, match="successful no-replace link"):
        producer._publish(output_path, b'{"complete":true}\n')
    assert not os.path.lexists(output_path)
    assert not list(output_path.parent.glob(f".{output_path.name}.*.stage"))


def test_parent_descriptor_close_interrupt_rolls_back_final(
    fixture: dict[str, Any], monkeypatch: pytest.MonkeyPatch
) -> None:
    output_path = fixture["output_path"]
    real_read_installed = producer._read_installed_output
    real_close = producer.os.close
    target_descriptor: int | None = None
    interrupted = False

    def tracking_read(
        parent_descriptor: int,
        name: str,
        expected_identity: tuple[int, int],
        payload_size: int,
    ) -> bytes:
        nonlocal target_descriptor
        raw = real_read_installed(
            parent_descriptor,
            name,
            expected_identity,
            payload_size,
        )
        target_descriptor = parent_descriptor
        return raw

    def interrupting_close(descriptor: int) -> None:
        nonlocal interrupted
        if descriptor == target_descriptor and not interrupted:
            interrupted = True
            real_close(descriptor)
            raise KeyboardInterrupt("injected after final directory fsync")
        real_close(descriptor)

    monkeypatch.setattr(producer, "_read_installed_output", tracking_read)
    monkeypatch.setattr(producer.os, "close", interrupting_close)
    with pytest.raises(KeyboardInterrupt, match="final directory fsync"):
        producer._publish(output_path, b'{"complete":true}\n')
    assert interrupted
    assert not os.path.lexists(output_path)
    assert not list(output_path.parent.glob(f".{output_path.name}.*.stage"))


def test_foreign_final_replacement_is_preserved_during_rollback(
    fixture: dict[str, Any], monkeypatch: pytest.MonkeyPatch
) -> None:
    output_path = fixture["output_path"]
    real_link = producer.os.link
    foreign = b'{"foreign":true}\n'

    def replace_after_link(*args: Any, **kwargs: Any) -> None:
        real_link(*args, **kwargs)
        output_path.unlink()
        output_path.write_bytes(foreign)
        output_path.chmod(0o400)
        raise KeyboardInterrupt("injected after foreign replacement")

    monkeypatch.setattr(producer.os, "link", replace_after_link)
    with pytest.raises(KeyboardInterrupt, match="foreign replacement"):
        producer._publish(output_path, b'{"owned":true}\n')
    assert output_path.read_bytes() == foreign
    assert stat.S_IMODE(output_path.stat().st_mode) == 0o400
    assert output_path.stat().st_nlink == 1
    assert not list(output_path.parent.glob(f".{output_path.name}.*.stage"))


def test_parent_component_replacement_is_detected_and_old_parent_is_cleaned(
    fixture: dict[str, Any], monkeypatch: pytest.MonkeyPatch
) -> None:
    output_path = fixture["output_path"]
    original_parent = output_path.parent
    displaced_parent = original_parent.with_name(f"{original_parent.name}-displaced")
    real_link = producer.os.link
    replaced = False

    def replace_parent_then_link(*args: Any, **kwargs: Any) -> None:
        nonlocal replaced
        original_parent.rename(displaced_parent)
        original_parent.mkdir(mode=0o700)
        replaced = True
        real_link(*args, **kwargs)

    monkeypatch.setattr(producer.os, "link", replace_parent_then_link)
    with pytest.raises(producer.CandidateStationaryFailure) as captured:
        producer._publish(output_path, b'{"complete":true}\n')
    assert captured.value.code == producer.HOLD_OUTPUT
    assert "parent identity changed" in str(captured.value)
    assert replaced
    assert not os.path.lexists(output_path)
    assert not os.path.lexists(displaced_parent / output_path.name)
    assert not list(displaced_parent.glob(f".{output_path.name}.*.stage"))


def test_concurrent_no_replace_publication_has_one_winner_and_one_loser(
    fixture: dict[str, Any],
) -> None:
    output_path = fixture["output_path"]
    payloads = (b'{"contender":1}\n', b'{"contender":2}\n')

    def contender(payload: bytes) -> str:
        try:
            producer._publish(output_path, payload)
        except producer.CandidateStationaryFailure as error:
            assert error.code == producer.HOLD_OUTPUT
            return "loser"
        return "winner"

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        outcomes = list(executor.map(contender, payloads))
    assert sorted(outcomes) == ["loser", "winner"]
    assert output_path.read_bytes() in payloads
    assert stat.S_IMODE(output_path.stat().st_mode) == 0o400
    assert output_path.stat().st_nlink == 1
    assert not list(output_path.parent.glob(f".{output_path.name}.*.stage"))


def test_source_separation_and_no_legacy_scientific_imports() -> None:
    forbidden = {
        "build_continuum_c1_stationary_integral_source_v1",
        "rate_defined_tensor_f0",
        "rate_defined_tensor_f0_production_initial_stream",
        "validate_continuum_c1_stationary_integral_source_v1",
    }
    for path in (PRODUCER_PATH, VERIFIER_PATH):
        tree = ast.parse(path.read_text("utf-8"))
        imported = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".")[0])
        assert imported.isdisjoint(forbidden)
    verifier_source = VERIFIER_PATH.read_text("utf-8")
    assert PRODUCER_PATH.stem not in verifier_source
    for source in (PRODUCER_PATH.read_text("utf-8"), verifier_source):
        assert "os.O_NONBLOCK" in source
        assert "continuum_c1_stationary_integral_source_v1.json" not in source
        assert "continuum_c1_fixed_row_raw_flux_source_v1.json" not in source
        assert "physical_production_killing_geometry_v1" not in source


def test_verifier_is_read_only(fixture: dict[str, Any]) -> None:
    request_path = fixture["request_path"]
    output_path = fixture["output_path"]
    payload = producer.build_from_request(request_path, output_path)
    producer._publish(output_path, payload)
    before = {
        path: (path.stat().st_mtime_ns, sha256(path.read_bytes()))
        for path in [request_path, output_path, *fixture["paths"].values()]
    }
    verifier.validate(request_path, output_path)
    after = {path: (path.stat().st_mtime_ns, sha256(path.read_bytes())) for path in before}
    assert before == after
