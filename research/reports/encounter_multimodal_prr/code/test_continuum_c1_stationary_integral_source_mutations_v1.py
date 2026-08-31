#!/usr/bin/env python3
"""Fail-closed mutation gate for the stationary-integral validator CLI."""

from __future__ import annotations

import copy
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any, Callable

import pytest

HERE = Path(__file__).resolve()
REPORT = HERE.parents[1]
VALIDATOR = REPORT / "code/validate_continuum_c1_stationary_integral_source_v1.py"
ARTIFACT = REPORT / "artifacts/data/continuum_c1_stationary_integral_source_v1.json"
PYTHON = Path("/Users/ae23069/.local-build/valley-k-small/.venv/bin/python")
LAUNCHER = REPORT / "code/run_continuum_c1_mpfr_authenticated_v1.py"
LAUNCHER_SHA256 = "f73f61f40ad658c00bb40f27c6676998763d84383b5c86deff7e3bac48a12df4"
SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")
BOOTSTRAP = """\
import hashlib, os, stat, sys, types
path = os.path.abspath(sys.argv[1])
expected = sys.argv[2]
fd = os.open(path, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW)
try:
    before = os.fstat(fd)
    chunks = []
    while True:
        chunk = os.read(fd, 65536)
        if not chunk:
            break
        chunks.append(chunk)
    after = os.fstat(fd)
finally:
    os.close(fd)
payload = b"".join(chunks)
identity = lambda value: (
    value.st_dev,
    value.st_ino,
    value.st_mode,
    value.st_size,
    value.st_mtime_ns,
    value.st_ctime_ns,
)
assert stat.S_ISREG(before.st_mode) and identity(before) == identity(after)
lexical = os.lstat(path)
assert (lexical.st_dev, lexical.st_ino) == (before.st_dev, before.st_ino)
actual = hashlib.sha256(payload).hexdigest()
assert actual == expected, (actual, expected)
module = types.ModuleType("_operator_pinned_continuum_c1_launcher")
module.__name__ = "__main__"
module.__file__ = path
module.__package__ = ""
module.__loader__ = None
module.__spec__ = None
module.__dict__["_OUTER_AUTHENTICATED_LAUNCHER_BYTES"] = payload
module.__dict__["_OUTER_AUTHENTICATED_LAUNCHER_SHA256"] = actual
sys.argv = [path, *sys.argv[3:]]
exec(compile(payload, path, "exec", dont_inherit=True), module.__dict__)
"""


def _canonical(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            allow_nan=False,
            ensure_ascii=True,
            indent=2,
            sort_keys=True,
        )
        + "\n"
    ).encode("ascii")


def _artifact() -> dict[str, Any]:
    value = json.loads(ARTIFACT.read_text(encoding="ascii"))
    assert type(value) is dict
    return value


def _validator(path: Path) -> subprocess.CompletedProcess[str]:
    environment = dict(os.environ)
    for name in tuple(environment):
        if name.startswith("DYLD_") or name in {
            "LD_LIBRARY_PATH",
            "LD_PRELOAD",
            "PYTHONHOME",
            "PYTHONINSPECT",
            "PYTHONPATH",
            "PYTHONSTARTUP",
        }:
            environment.pop(name)
    command = [
        str(PYTHON),
        "-I",
        "-S",
        "-c",
        BOOTSTRAP,
        str(LAUNCHER),
        LAUNCHER_SHA256,
        "--target",
        "stationary_validator",
    ]
    if path != ARTIFACT:
        command.extend(("--artifact-probe", str(path.resolve())))
    return subprocess.run(
        command,
        cwd=path.parent,
        env=environment,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        timeout=60,
        check=False,
    )


def _complete_c1_true(value: dict[str, Any]) -> None:
    value["claim_boundary"]["complete_C1"] = True


def _cell_mass_endpoint(value: dict[str, Any]) -> None:
    value["rows"][0]["axes"][0]["cell_mass_intervals"][0]["lower_exact_p_over_q"] = "0"


def _formula_id_without_w(value: dict[str, Any]) -> None:
    axis = next(
        candidate
        for candidate in value["rows"][0]["axes"]
        if candidate["coordinate"] == "relative_perpendicular"
    )
    assert "_W_" in axis["formula_id"]
    axis["formula_id"] = axis["formula_id"].replace("_W_", "__")


def _box_mass_one(value: dict[str, Any]) -> None:
    value["rows"][0]["factorized_box_mass_interval"] = {
        "lower_exact_p_over_q": "1",
        "upper_exact_p_over_q": "1",
    }


def _row_reorder(value: dict[str, Any]) -> None:
    value["rows"] = list(reversed(value["rows"]))


def _member_digest(value: dict[str, Any]) -> None:
    value["rows"][0]["member_digest_sha256"] = "0" * 64


def _source_hash(value: dict[str, Any]) -> None:
    value["source_pins"]["reference_density_source"]["sha256"] = "f" * 64


def _missing_key(value: dict[str, Any]) -> None:
    value.pop("status")


def _unknown_key(value: dict[str, Any]) -> None:
    value["invented_field"] = False


def _float_literal(value: dict[str, Any]) -> None:
    value["summary"]["configuration_count"] = 12.0


def _bool_for_int(value: dict[str, Any]) -> None:
    value["summary"]["configuration_count"] = True


def _int_for_bool(value: dict[str, Any]) -> None:
    value["claim_boundary"]["complete_C1"] = 0


def _row_cardinality(value: dict[str, Any]) -> None:
    value["rows"].pop()


def _cell_cardinality(value: dict[str, Any]) -> None:
    value["rows"][0]["axes"][0]["cell_mass_intervals"].pop()


def _noncanonical_p_over_q(value: dict[str, Any]) -> None:
    value["rows"][0]["axes"][0]["cell_mass_intervals"][0]["lower_exact_p_over_q"] = "2/2"


MUTATIONS: tuple[tuple[str, Callable[[dict[str, Any]], None]], ...] = (
    ("complete_C1_true", _complete_c1_true),
    ("cell_mass_endpoint", _cell_mass_endpoint),
    ("formula_id_W_removal", _formula_id_without_w),
    ("box_mass_equals_one", _box_mass_one),
    ("row_reorder", _row_reorder),
    ("member_digest", _member_digest),
    ("source_hash", _source_hash),
    ("missing_key", _missing_key),
    ("unknown_key", _unknown_key),
    ("float_literal", _float_literal),
    ("bool_for_int", _bool_for_int),
    ("int_for_bool", _int_for_bool),
    ("row_cardinality", _row_cardinality),
    ("cell_cardinality", _cell_cardinality),
    ("noncanonical_p_over_q", _noncanonical_p_over_q),
)


@pytest.fixture(scope="module", autouse=True)
def _baseline_is_accepted_before_mutation_tests() -> None:
    result = _validator(ARTIFACT)
    assert result.returncode == 0, result.stdout
    assert SHA256_RE.fullmatch(result.stdout.strip())


@pytest.mark.parametrize(("name", "mutate"), MUTATIONS, ids=[name for name, _ in MUTATIONS])
def test_validator_rejects_semantic_mutation(
    tmp_path: Path,
    name: str,
    mutate: Callable[[dict[str, Any]], None],
) -> None:
    candidate = copy.deepcopy(_artifact())
    mutate(candidate)
    path = tmp_path / f"{name}.json"
    path.write_bytes(_canonical(candidate))
    result = _validator(path)
    assert result.returncode == 1, result.stdout
    assert result.stdout.startswith("HOLD"), result.stdout


def test_validator_rejects_duplicate_key(tmp_path: Path) -> None:
    raw = ARTIFACT.read_text(encoding="ascii")
    marker = '{\n  "claim_boundary"'
    assert raw.count(marker) == 1
    duplicate = raw.replace(
        marker,
        '{\n  "schema": "duplicate-top-level-schema",\n  "claim_boundary"',
        1,
    )
    path = tmp_path / "duplicate_key.json"
    path.write_text(duplicate, encoding="ascii")
    result = _validator(path)
    assert result.returncode == 1, result.stdout
    assert result.stdout.startswith("HOLD"), result.stdout
