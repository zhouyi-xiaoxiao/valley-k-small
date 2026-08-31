"""Fail-closed and source-separation tests for role-9 v3 entrypoints."""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import pathlib
import subprocess
import sys
import typing

import pytest

CODE = pathlib.Path(__file__).resolve().parent
PRODUCER_PATH = CODE / "build_continuum_c1_n0_candidate_native_stationary_integrals_v3.py"
VERIFIER_PATH = CODE / "validate_continuum_c1_n0_candidate_native_stationary_integrals_v3.py"
EXACT_HOLD = "HOLD_CANDIDATE_STATIONARY_NUMERICAL_IMPLEMENTATION_INCOMPLETE"


def _load(name: str, path: pathlib.Path) -> typing.Any:
    specification = importlib.util.spec_from_file_location(name, path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


producer = _load("role9_v3_producer_tests", PRODUCER_PATH)
verifier = _load("role9_v3_verifier_tests", VERIFIER_PATH)


def _sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _direct_imports(path: pathlib.Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    imports: set[str] = set()
    forbidden_dynamic = {
        "__import__",
        "compile",
        "eval",
        "exec",
        "getattr",
        "import_module",
    }
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.module == "__future__" and node.level == 0:
                continue
            if node.module == "typing" and node.level == 0:
                imports.add("typing")
                continue
            pytest.fail(f"from-import is outside the Round-180 profile: {node.module}")
        elif isinstance(node, ast.Name):
            assert node.id not in forbidden_dynamic
        elif isinstance(node, ast.Attribute):
            assert node.attr not in forbidden_dynamic
    return imports


def test_frozen_role9_v3_protocol_identities() -> None:
    expected_methods = (
        "stationary_directed_mpfr_320_v2",
        "stationary_directed_mpfr_640_sentinel_v2",
        "exact_fraction_expression_dag_v2",
    )
    expected_digests = (
        "1226335c739734613508bacbaba3d8fb7f6c0607557d11190fe846ba08000da7",
        "67d76049763a982144e2b41fc1722ce6e4663bccb8bdcec9e2af398d7c1511f9",
        "c1e11de7305a3035973e98d1913e14075f0ba3b2a32180a73689aee4c9b4b851",
    )
    expected_authorities = (
        "anti_vacuity_policy",
        "configuration",
        "ideal_formula",
        "member_spec",
        "method_parameter_registry",
        "reference_density",
        "sealed_authentication_mirror",
    )
    for module in (producer, verifier):
        assert (module.ROLE_ID, module.ROLE_NAME) == (
            9,
            "role9_stationary_physical_integral",
        )
        assert module.REQUEST_SCHEMA == (
            "encounter_continuum_c1_n0_stationary_integrals_request_v4"
        )
        assert module.PLAN_SCHEMA == "encounter_continuum_c1_n0_roles_8_10_replay_plan_v2"
        assert module.BUNDLE_SCHEMA == ("encounter_continuum_c1_n0_precommit_candidate_bundle_v2")
        assert module.RUNTIME_CLOSURE_SCHEMA == (
            "encounter_continuum_c1_n0_roles_8_10_implementation_runtime_closure_v1"
        )
        assert module.DIRECT_AUTHORITY_KEYS == expected_authorities
        assert module.METHOD_PARAMETER_IDS == expected_methods
        assert module.METHOD_PARAMETER_SHA256S == expected_digests
        assert module.PLANNED_NUMERICAL_BACKEND_MODULE == "gmpy2"
        assert module.HOLD_NUMERICAL_INCOMPLETE == EXACT_HOLD


def test_v3_sources_are_disjoint_and_static_profile_compatible() -> None:
    assert PRODUCER_PATH != VERIFIER_PATH
    assert _sha256(PRODUCER_PATH) != _sha256(VERIFIER_PATH)
    producer_imports = _direct_imports(PRODUCER_PATH)
    verifier_imports = _direct_imports(VERIFIER_PATH)
    assert VERIFIER_PATH.stem not in producer_imports
    assert PRODUCER_PATH.stem not in verifier_imports
    for imports in (producer_imports, verifier_imports):
        assert {"numpy", "scipy", "rate_defined_tensor_f0"}.isdisjoint(imports)
        assert "gmpy2" not in imports
    for path in (PRODUCER_PATH, VERIFIER_PATH):
        source = path.read_text(encoding="utf-8")
        assert "roles_8_10_replay_plan_v1" not in source
        assert "stationary_integrals_request_v3" not in source
        assert "precommit_candidate_bundle_v1" not in source


def test_producer_api_reaches_exact_hold_without_creating_output(
    tmp_path: pathlib.Path,
) -> None:
    request = tmp_path / "role9-request.json"
    output = tmp_path / "role9-artifact.json"
    with pytest.raises(producer.CandidateStationaryV3Failure) as error:
        producer.build_from_request(request, output)
    assert error.value.code == EXACT_HOLD
    assert str(error.value) == EXACT_HOLD
    assert not request.exists()
    assert not output.exists()


def test_verifier_api_reaches_exact_hold_without_creating_receipt(
    tmp_path: pathlib.Path,
) -> None:
    request = tmp_path / "role9-request.json"
    output = tmp_path / "role9-artifact.json"
    receipt = tmp_path / "role9-validation-receipt.json"
    with pytest.raises(verifier.CandidateStationaryV3VerificationFailure) as error:
        verifier.validate(request, output, receipt)
    assert error.value.code == EXACT_HOLD
    assert str(error.value) == EXACT_HOLD
    assert not request.exists()
    assert not output.exists()
    assert not receipt.exists()


def test_invalid_direct_apis_also_expose_one_hold(tmp_path: pathlib.Path) -> None:
    same = tmp_path / "same.json"
    with pytest.raises(producer.CandidateStationaryV3Failure) as producer_error:
        producer.build_from_request(same, same)
    assert producer_error.value.code == EXACT_HOLD
    assert str(producer_error.value) == EXACT_HOLD

    with pytest.raises(verifier.CandidateStationaryV3VerificationFailure) as verifier_error:
        verifier.validate(same, same, same)
    assert verifier_error.value.code == EXACT_HOLD
    assert str(verifier_error.value) == EXACT_HOLD
    assert not same.exists()


@pytest.mark.parametrize(
    ("entrypoint", "extra_arguments", "protected_names"),
    [
        (PRODUCER_PATH, (), ("role9-artifact.json",)),
        (
            VERIFIER_PATH,
            ("--receipt", "role9-validation-receipt.json"),
            ("role9-artifact.json", "role9-validation-receipt.json"),
        ),
    ],
)
def test_cli_emits_only_exact_hold_and_never_publishes(
    tmp_path: pathlib.Path,
    entrypoint: pathlib.Path,
    extra_arguments: tuple[str, ...],
    protected_names: tuple[str, ...],
) -> None:
    request = tmp_path / "role9-request.json"
    output = tmp_path / "role9-artifact.json"
    arguments = [
        sys.executable,
        "-I",
        "-B",
        str(entrypoint),
        "--request",
        str(request),
        "--output",
        str(output),
    ]
    if extra_arguments:
        arguments.extend(
            (
                extra_arguments[0],
                str(tmp_path / extra_arguments[1]),
            )
        )
    completed = subprocess.run(
        arguments,
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert completed.returncode == 2
    assert completed.stdout == ""
    assert completed.stderr == EXACT_HOLD + "\n"
    assert not request.exists()
    for name in protected_names:
        assert not (tmp_path / name).exists()


def test_existing_destinations_are_never_read_or_modified(tmp_path: pathlib.Path) -> None:
    request = tmp_path / "role9-request.json"
    output = tmp_path / "role9-artifact.json"
    receipt = tmp_path / "role9-validation-receipt.json"
    output.write_bytes(b"foreign-artifact-sentinel")
    receipt.write_bytes(b"foreign-receipt-sentinel")
    with pytest.raises(producer.CandidateStationaryV3Failure):
        producer.build_from_request(request, output)
    with pytest.raises(verifier.CandidateStationaryV3VerificationFailure):
        verifier.validate(request, output, receipt)
    assert output.read_bytes() == b"foreign-artifact-sentinel"
    assert receipt.read_bytes() == b"foreign-receipt-sentinel"


@pytest.mark.parametrize(
    ("entrypoint", "arguments"),
    [
        (PRODUCER_PATH, ()),
        (PRODUCER_PATH, ("--help",)),
        (PRODUCER_PATH, ("--request", "relative", "--output", "/tmp/role9-output")),
        (VERIFIER_PATH, ("-h",)),
        (
            VERIFIER_PATH,
            (
                "--request",
                "/tmp/role9-request",
                "--output",
                "/tmp/role9-output",
                "--receipt",
                "relative",
            ),
        ),
    ],
)
def test_every_invalid_cli_exposes_only_exact_hold(
    entrypoint: pathlib.Path,
    arguments: tuple[str, ...],
) -> None:
    completed = subprocess.run(
        [sys.executable, "-I", "-B", str(entrypoint), *arguments],
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert completed.returncode == 2
    assert completed.stdout == ""
    assert completed.stderr == EXACT_HOLD + "\n"
