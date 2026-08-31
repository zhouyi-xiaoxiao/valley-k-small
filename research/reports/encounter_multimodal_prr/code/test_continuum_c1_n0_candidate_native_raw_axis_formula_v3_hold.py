"""Adversarial tests for the fail-closed role-8 v3 entrypoint boundary."""

import ast
import hashlib
import importlib.util
import os
import pathlib
import subprocess
import sys

import pytest

CODE_DIR = pathlib.Path(__file__).resolve().parent
PRODUCER = CODE_DIR / "build_continuum_c1_n0_candidate_native_raw_axis_formula_v3.py"
VERIFIER = CODE_DIR / "validate_continuum_c1_n0_candidate_native_raw_axis_formula_v3.py"
HOLD = "HOLD_CANDIDATE_RAW_AXIS_NUMERICAL_IMPLEMENTATION_INCOMPLETE"
METHOD_PARAMETER_IDS = (
    "raw_flux_directed_mpfr_320_v2",
    "raw_flux_directed_mpfr_640_sentinel_v2",
    "raw_flux_binary64_decode_v2",
    "exact_fraction_expression_dag_v2",
)


def _load(path, name):
    specification = importlib.util.spec_from_file_location(name, path)
    assert specification is not None
    assert specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def _run(path, *arguments):
    environment = {
        "HOME": os.environ.get("HOME", "/tmp"),
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "PYTHONPYCACHEPREFIX": "/tmp/round181-role8-v3-pycache",
    }
    return subprocess.run(
        [sys.executable, "-I", "-B", str(path), *map(str, arguments)],
        check=False,
        capture_output=True,
        env=environment,
        text=True,
    )


def _assert_exact_hold(completed):
    assert completed.returncode == 2
    assert completed.stdout == ""
    assert completed.stderr == f"{HOLD}\n"


def _assert_source_profile(path):
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))
    imports = set()
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
            pytest.fail(f"from-import is outside the Round-180 profile: {node.module}")
        elif isinstance(node, ast.Name):
            assert node.id not in forbidden_dynamic
        elif isinstance(node, ast.Attribute):
            assert node.attr not in forbidden_dynamic
    assert imports == {"argparse", "os", "sys"}
    assert "numpy" not in source
    assert "scipy" not in source
    assert "rate_defined_tensor_f0" not in source
    assert "candidate_native_raw_axis_formula_v2" not in source
    assert all(parameter_id in source for parameter_id in METHOD_PARAMETER_IDS)


def test_source_basenames_and_source_separation():
    assert PRODUCER.name == "build_continuum_c1_n0_candidate_native_raw_axis_formula_v3.py"
    assert VERIFIER.name == "validate_continuum_c1_n0_candidate_native_raw_axis_formula_v3.py"
    assert PRODUCER.read_bytes() != VERIFIER.read_bytes()
    assert (
        hashlib.sha256(PRODUCER.read_bytes()).digest()
        != hashlib.sha256(VERIFIER.read_bytes()).digest()
    )
    _assert_source_profile(PRODUCER)
    _assert_source_profile(VERIFIER)


def test_import_has_no_publication_side_effect(tmp_path):
    before = set(tmp_path.iterdir())
    producer = _load(PRODUCER, "role8_v3_hold_producer")
    verifier = _load(VERIFIER, "role8_v3_hold_verifier")
    assert set(tmp_path.iterdir()) == before
    assert producer.ROLE_ID == verifier.ROLE_ID == 8
    assert producer.ROLE_NAME == verifier.ROLE_NAME == "role8_raw_axis_formula_primitive"
    assert producer.REQUEST_SCHEMA == verifier.REQUEST_SCHEMA
    assert producer.METHOD_PARAMETER_IDS == verifier.METHOD_PARAMETER_IDS == METHOD_PARAMETER_IDS
    assert producer.HOLD == verifier.HOLD == HOLD


def test_producer_exact_contract_cli_holds_without_output(tmp_path):
    request = tmp_path / "role8-request.json"
    output = tmp_path / "role8-artifact.json"
    completed = _run(PRODUCER, "--request", request, "--output", output)
    _assert_exact_hold(completed)
    assert not request.exists()
    assert not output.exists()
    assert list(tmp_path.iterdir()) == []


def test_verifier_exact_contract_cli_holds_without_receipt(tmp_path):
    request = tmp_path / "role8-request.json"
    output = tmp_path / "role8-artifact.json"
    receipt = tmp_path / "role8-receipt.json"
    completed = _run(
        VERIFIER,
        "--request",
        request,
        "--output",
        output,
        "--receipt",
        receipt,
    )
    _assert_exact_hold(completed)
    assert not request.exists()
    assert not output.exists()
    assert not receipt.exists()
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize(
    ("entrypoint", "arguments", "uncreated"),
    [
        (PRODUCER, (), ()),
        (PRODUCER, ("--help",), ()),
        (PRODUCER, ("--request", "relative", "--output", "/tmp/role8-out"), ()),
        (VERIFIER, ("-h",), ()),
        (
            VERIFIER,
            (
                "--request",
                "/tmp/role8-request",
                "--output",
                "/tmp/role8-output",
                "--receipt",
                "relative",
            ),
            (),
        ),
        (
            VERIFIER,
            (
                "--request",
                "/tmp/role8-same",
                "--output",
                "/tmp/role8-same",
                "--receipt",
                "/tmp/role8-receipt",
            ),
            (),
        ),
    ],
)
def test_invalid_cli_also_exposes_only_exact_hold(entrypoint, arguments, uncreated):
    completed = _run(entrypoint, *arguments)
    _assert_exact_hold(completed)
    for path in uncreated:
        assert not pathlib.Path(path).exists()


def test_existing_inputs_are_never_opened_or_modified(tmp_path):
    request = tmp_path / "role8-request.json"
    output = tmp_path / "role8-artifact.json"
    receipt = tmp_path / "role8-receipt.json"
    request.write_bytes(b"not canonical JSON and deliberately unread")
    output.write_bytes(b"preexisting artifact bytes")
    request.chmod(0)
    output.chmod(0)
    before_request = request.stat()
    before_output = output.stat()
    try:
        producer_run = _run(PRODUCER, "--request", request, "--output", output)
        verifier_run = _run(
            VERIFIER,
            "--request",
            request,
            "--output",
            output,
            "--receipt",
            receipt,
        )
        _assert_exact_hold(producer_run)
        _assert_exact_hold(verifier_run)
        assert request.stat() == before_request
        assert output.stat() == before_output
        assert not receipt.exists()
    finally:
        request.chmod(0o600)
        output.chmod(0o600)


def test_direct_main_calls_hold_and_publish_nothing(tmp_path, capsys):
    producer = _load(PRODUCER, "role8_v3_direct_producer")
    verifier = _load(VERIFIER, "role8_v3_direct_verifier")
    request = tmp_path / "request.json"
    output = tmp_path / "artifact.json"
    receipt = tmp_path / "receipt.json"
    assert producer.main(["--request", str(request), "--output", str(output)]) == 2
    producer_capture = capsys.readouterr()
    assert producer_capture.out == ""
    assert producer_capture.err == f"{HOLD}\n"
    assert (
        verifier.main(
            [
                "--request",
                str(request),
                "--output",
                str(output),
                "--receipt",
                str(receipt),
            ]
        )
        == 2
    )
    verifier_capture = capsys.readouterr()
    assert verifier_capture.out == ""
    assert verifier_capture.err == f"{HOLD}\n"
    assert not request.exists()
    assert not output.exists()
    assert not receipt.exists()
