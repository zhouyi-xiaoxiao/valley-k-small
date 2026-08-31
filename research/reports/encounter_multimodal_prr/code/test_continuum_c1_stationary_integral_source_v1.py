#!/usr/bin/env python3
"""Independent structural and process gates for the stationary-integral source."""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import tempfile
from fractions import Fraction
from pathlib import Path, PurePosixPath
from typing import Any, Iterator

HERE = Path(__file__).resolve()
REPORT = HERE.parents[1]
BUILDER = REPORT / "code/build_continuum_c1_stationary_integral_source_v1.py"
VALIDATOR = REPORT / "code/validate_continuum_c1_stationary_integral_source_v1.py"
ARTIFACT = REPORT / "artifacts/data/continuum_c1_stationary_integral_source_v1.json"
BUNDLE_ROOT = REPORT / "artifacts/data/physical_production_initial_stream_v1"
PYTHON = Path("/Users/ae23069/.local-build/valley-k-small/.venv/bin/python")
LAUNCHER = REPORT / "code/run_continuum_c1_mpfr_authenticated_v1.py"
LAUNCHER_SHA256 = "f73f61f40ad658c00bb40f27c6676998763d84383b5c86deff7e3bac48a12df4"
AUTHORITY = REPORT / "code/continuum_c1_mpfr_execution_authority_v1.json"
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

EXPECTED_CLAIMS = {
    "backend_independence_claimed",
    "box_conditionally_renormalized",
    "complete_C0",
    "complete_C1",
    "complete_C2",
    "complete_C3",
    "formal_production_bridge_accepted",
    "genuine_refinement_sequence_present",
    "one_correlated_distinguished_ideal_member_is_contained",
    "release_eligible",
}
EXPECTED_SOURCE_PINS = {
    "builder_source",
    "configuration_source",
    "ideal_formula_source",
    "member_spec",
    "method_registry",
    "production_partition_bundle",
    "raw_axis_binding",
    "reference_density_source",
}
EXPECTED_COORDINATES = {
    "midpoint",
    "relative_parallel",
    "relative_perpendicular",
}
SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")


def _reject_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise AssertionError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(
        path.read_text(encoding="ascii"),
        object_pairs_hook=_reject_duplicates,
        parse_constant=lambda token: (_ for _ in ()).throw(
            AssertionError(f"non-finite JSON literal: {token}")
        ),
    )
    assert type(value) is dict
    return value


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


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _report_path(value: object) -> Path:
    assert type(value) is str
    relative = PurePosixPath(value)
    assert not relative.is_absolute()
    assert relative.parts
    assert "." not in relative.parts
    assert ".." not in relative.parts
    path = REPORT.joinpath(*relative.parts)
    assert path.is_file()
    return path


def _fraction(value: object) -> Fraction:
    assert type(value) is str
    assert value.strip() == value
    assert value.count("/") == 1
    numerator, denominator = value.split("/")
    result = Fraction(int(numerator), int(denominator))
    assert f"{result.numerator}/{result.denominator}" == value
    return result


def _walk(value: Any) -> Iterator[Any]:
    yield value
    if type(value) is dict:
        for child in value.values():
            yield from _walk(child)
    elif type(value) is list:
        for child in value:
            yield from _walk(child)


def _interval(value: object) -> tuple[Fraction, Fraction]:
    assert type(value) is dict
    assert set(value) == {
        "lower_exact_p_over_q",
        "upper_exact_p_over_q",
    }
    lower = _fraction(value["lower_exact_p_over_q"])
    upper = _fraction(value["upper_exact_p_over_q"])
    assert lower <= upper
    return lower, upper


def _run(
    program: Path,
    *arguments: str,
    cwd: Path = REPORT,
) -> subprocess.CompletedProcess[str]:
    target = {
        BUILDER: "stationary_builder",
        VALIDATOR: "stationary_validator",
    }[program]
    if target == "stationary_builder":
        assert set(arguments).issubset({"--check", "--output", str(ARTIFACT)})
    else:
        assert set(arguments).issubset({"--artifact", str(ARTIFACT)})
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
    return subprocess.run(
        [
            str(PYTHON),
            "-I",
            "-S",
            "-c",
            BOOTSTRAP,
            str(LAUNCHER),
            LAUNCHER_SHA256,
            "--target",
            target,
        ],
        cwd=cwd,
        env=environment,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        timeout=60,
        check=False,
    )


def _run_with_hostile_mpfr_context(
    program: Path,
    arguments: list[str],
    cwd: Path,
) -> subprocess.CompletedProcess[str]:
    return _run(program, *arguments, cwd=cwd)


def test_published_artifact_is_canonical_and_has_exact_nonpromotion_boundary() -> None:
    artifact = _load(ARTIFACT)
    assert ARTIFACT.read_bytes() == _canonical(artifact)
    assert artifact["schema"] == "encounter_continuum_c1_stationary_integral_source_v1"
    assert artifact["status"] == (
        "PASS_FIXED_12_ROW_FACTORIZED_PHYSICAL_STATIONARY_INTEGRALS_"
        "SAME_MPFR_BACKEND_SENTINEL_ONLY_NO_REFINEMENT_NO_COMPLETE_C1_C2"
    )

    claims = artifact["claim_boundary"]
    assert set(claims) == EXPECTED_CLAIMS
    assert all(type(claims[key]) is bool and claims[key] is False for key in claims)

    method = artifact["method"]
    assert method["primary_precision_bits"] == 320
    assert type(method["primary_precision_bits"]) is int
    assert method["sentinel_precision_bits"] == 640
    assert type(method["sentinel_precision_bits"]) is int
    assert method["dense_tensor_materialized"] is False
    assert method["sentinel_semantics"] == (
        "same_backend_higher_precision_containment_not_backend_independence"
    )

    for node in _walk(artifact):
        assert not isinstance(node, float)


def test_exact_counts_and_every_mass_endpoint_use_canonical_reduced_p_over_q() -> None:
    artifact = _load(ARTIFACT)
    summary = artifact["summary"]
    assert summary == {
        "all_primary_intervals_contain_640_bit_sentinels": True,
        "configuration_count": 12,
        "factorized_axis_cell_count": 5_037,
        "gaussian_axis_cell_count": 3_446,
        "maximum_primary_cell_relative_width_exact": (
            summary["maximum_primary_cell_relative_width_exact"]
        ),
        "minimum_positive_primary_cell_lower_exact": (
            summary["minimum_positive_primary_cell_lower_exact"]
        ),
        "periodic_axis_cell_count": 1_591,
        "total_virtual_tensor_state_count": 34_787_462,
    }
    assert _fraction(summary["maximum_primary_cell_relative_width_exact"]) > 0
    assert _fraction(summary["minimum_positive_primary_cell_lower_exact"]) > 0

    rows = artifact["rows"]
    assert type(rows) is list and len(rows) == 12
    assert [row["configuration_index"] for row in rows] == list(range(12))
    assert len({row["configuration_label"] for row in rows}) == 12

    gaussian = 0
    periodic = 0
    tensor_states = 0
    for row in rows:
        axes = row["axes"]
        assert type(axes) is list and len(axes) == 3
        assert {axis["coordinate"] for axis in axes} == EXPECTED_COORDINATES
        dimensions: list[int] = []
        for axis in axes:
            count = axis["cell_count"]
            assert type(count) is int and count >= 2
            masses = axis["cell_mass_intervals"]
            assert type(masses) is list and len(masses) == count
            assert [mass["cell_index"] for mass in masses] == list(range(count))
            for mass in masses:
                lower = _fraction(mass["lower_exact_p_over_q"])
                upper = _fraction(mass["upper_exact_p_over_q"])
                assert 0 < lower <= upper
            for name in (
                "direct_domain_mass_interval",
                "joint_domain_mass_interval",
                "sum_of_cells_mass_interval",
            ):
                lower, upper = _interval(axis[name])
                assert 0 < lower <= upper <= 1
            dimensions.append(count)
            if axis["coordinate"] == "relative_perpendicular":
                periodic += count
            else:
                gaussian += count

        expected_tensor_states = dimensions[0] * dimensions[1] * dimensions[2]
        assert row["tensor_state_count"] == expected_tensor_states
        tensor_states += expected_tensor_states
        for name in (
            "factorized_box_mass_interval",
            "joint_box_mass_interval",
            "single_domain_box_mass_interval",
        ):
            lower, upper = _interval(row[name])
            assert 0 < lower <= upper < 1

    assert gaussian == 3_446
    assert periodic == 1_591
    assert gaussian + periodic == 5_037
    assert tensor_states == 34_787_462


def test_all_source_and_partition_hash_bindings_match_current_bytes() -> None:
    artifact = _load(ARTIFACT)
    pins = artifact["source_pins"]
    assert set(pins) == EXPECTED_SOURCE_PINS
    for binding in pins.values():
        assert type(binding) is dict
        assert set(binding) == {"path", "sha256"}
        assert SHA256_RE.fullmatch(binding["sha256"])
        assert _sha256(_report_path(binding["path"])) == binding["sha256"]

    partition_paths: set[str] = set()
    partition_bindings = 0
    construction_counts: dict[str, int] = {}
    half_shift_wraps = 0
    vertex_partitions = 0
    for row in artifact["rows"]:
        for axis in row["axes"]:
            relative = axis["partition_path"]
            assert type(relative) is str
            assert relative not in partition_paths
            partition_paths.add(relative)
            partition_path = BUNDLE_ROOT.joinpath(*PurePosixPath(relative).parts)
            assert partition_path.is_file()
            assert SHA256_RE.fullmatch(axis["partition_sha256"])
            assert _sha256(partition_path) == axis["partition_sha256"]

            partition = _load(partition_path)
            assert partition_path.read_bytes() == _canonical(partition)
            assert partition["coordinate"] == axis["coordinate"]
            assert partition["size"] == axis["cell_count"]
            assert type(partition["size"]) is int
            construction = partition["construction"]
            construction_counts[construction] = construction_counts.get(construction, 0) + 1

            start = _fraction(partition["domain_start_exact"])
            width = _fraction(partition["domain_width_exact"])
            end = start + width
            assert width > 0
            cells = partition["cell_segments_exact"]
            volumes = [_fraction(value) for value in partition["cell_volumes_exact"]]
            assert len(cells) == len(volumes) == partition["size"]
            flat_segments: list[tuple[Fraction, Fraction]] = []
            for segments, recorded_volume in zip(cells, volumes, strict=True):
                assert type(segments) is list and segments
                parsed = [(_fraction(lower), _fraction(upper)) for lower, upper in segments]
                assert all(start <= lower < upper <= end for lower, upper in parsed)
                assert (
                    sum((upper - lower for lower, upper in parsed), Fraction()) == recorded_volume
                )
                flat_segments.extend(parsed)
            assert sum(volumes, Fraction()) == width
            cursor = start
            for lower, upper in sorted(flat_segments):
                assert lower == cursor
                cursor = upper
            assert cursor == end

            if construction == "cell_centred_periodic_diffusion_half_shift":
                wrapping = [segments for segments in cells if len(segments) == 2]
                assert len(wrapping) == 1
                assert _fraction(wrapping[0][0][1]) == end
                assert _fraction(wrapping[0][1][0]) == start
                half_shift_wraps += 1
            if construction == "vertex_centred_reflecting_scharfetter_gummel":
                assert volumes[0] == volumes[-1]
                assert all(volume == 2 * volumes[0] for volume in volumes[1:-1])
                positions = [_fraction(value) for value in partition["positions_exact"]]
                assert positions[0] == start and positions[-1] == end
                vertex_partitions += 1
            partition_bindings += 1

    assert partition_bindings == len(partition_paths) == 36
    assert construction_counts == {
        "cell_centred_periodic_diffusion": 10,
        "cell_centred_periodic_diffusion_half_shift": 2,
        "cell_centred_reflecting_scharfetter_gummel": 20,
        "vertex_centred_reflecting_scharfetter_gummel": 4,
    }
    assert half_shift_wraps == 2
    assert vertex_partitions == 4


def test_independent_validator_accepts_the_published_artifact_directly() -> None:
    result = _run(VALIDATOR, "--artifact", str(ARTIFACT))
    assert result.returncode == 0, result.stdout
    assert SHA256_RE.fullmatch(result.stdout.strip())
    authority = _load(AUTHORITY)
    outer_receipt_path = REPORT / authority["targets"]["stationary_validator"]["receipt_path"]
    outer_receipt = _load(outer_receipt_path)
    assert _sha256(outer_receipt_path) == result.stdout.strip()
    assert outer_receipt["launcher"]["sha256"] == LAUNCHER_SHA256
    assert outer_receipt["execution"]["ambient_mpfr_precision_bits"] == 53
    assert outer_receipt["execution"]["ambient_mpfr_rounding"] == "RoundToNearest"
    assert outer_receipt["execution"]["target_stderr"] == ""
    assert outer_receipt["execution"]["target_stdout"].startswith("PASS ")
    validation = json.loads(outer_receipt["execution"]["target_stdout"].removeprefix("PASS "))
    assert validation == {
        "artifact_sha256": _sha256(ARTIFACT),
        "configuration_count": 12,
        "factorized_axis_cell_count": 5_037,
        "gaussian_axis_cell_count": 3_446,
        "periodic_axis_cell_count": 1_591,
        "status": "PASS_FIXED_12_ROW_STATIONARY_INTEGRAL_SOURCE_INDEPENDENT_VALIDATION_ONLY",
        "total_virtual_tensor_state_count": 34_787_462,
    }


def test_builder_and_validator_ignore_hostile_cwd_and_53_bit_ambient_context() -> None:
    with tempfile.TemporaryDirectory(prefix="stationary-integral-hostile-cwd-") as directory:
        hostile_cwd = Path(directory)
        builder = _run_with_hostile_mpfr_context(
            BUILDER,
            ["--check", "--output", str(ARTIFACT)],
            hostile_cwd,
        )
        assert builder.returncode == 0, builder.stdout
        assert SHA256_RE.fullmatch(builder.stdout.strip())

        validator = _run_with_hostile_mpfr_context(
            VALIDATOR,
            ["--artifact", str(ARTIFACT)],
            hostile_cwd,
        )
        assert validator.returncode == 0, validator.stdout
        assert SHA256_RE.fullmatch(validator.stdout.strip())
        authority = _load(AUTHORITY)
        for target in ("stationary_builder", "stationary_validator"):
            receipt_path = REPORT / authority["targets"][target]["receipt_path"]
            receipt = _load(receipt_path)
            assert receipt["launcher"]["sha256"] == LAUNCHER_SHA256
            assert receipt["execution"]["ambient_mpfr_precision_bits"] == 53
            assert receipt["execution"]["ambient_mpfr_rounding"] == "RoundToNearest"
            assert receipt["artifact"]["sha256"] == _sha256(ARTIFACT)
