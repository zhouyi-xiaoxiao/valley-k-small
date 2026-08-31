"""Clean-process replay for the scoped twelve-row production-initial evidence.

Each repeat starts five separate ``python -I`` processes.  They produce the
serialized bundle, verify it from disk, rebuild every canonical byte with the
same frozen numerical core, rederive the declared source/partition/free-axis
semantics with the separate higher-precision implementation, and bind the
forward/backward rate files to native packed payloads.  Two complete repeats
must give identical serialized evidence.

This orchestration proves process separation and deterministic replay only for
that declared scope.  It does not construct killing, a full operator,
propagation, topology, continuum convergence, F0, or F1.
"""

from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import stat
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Final

SCHEMA: Final = "encounter_production_initial_clean_process_replay_v1"
STATUS: Final = (
    "PASS_TWO_REPEAT_CLEAN_PROCESS_SERIALIZED_SOURCE_PARTITION_FREE_AXIS_"
    "PACKING_REPLAY_ONLY_NOT_FULL_OPERATOR_NOT_F0_NOT_F1"
)

CONFIGURATION_SHA256: Final = "063913c7fbc2b706ba85a0e3f06005bad23a2292749817294cbf41f5cdce4084"
ANALYTIC_SOURCE_SHA256: Final = "0b2efec5dc1abea1380ab862e46825e7b79658fe9bfa0ac6637e1426ed9f7f5f"
F0_SOURCE_SHA256: Final = "321f12aa8a5df44ca9c9162704cccd0f2c526abf9577832b4824538b0afdb8e5"
PACKED_SOURCE_SHA256: Final = "447aa3bc224685ea1cc556d9d322dafba05ef148945d4ae41291f83e29f3deb4"
STREAM_SOURCE_SHA256: Final = "2871976855a0c598b26b8d83b33f4ea3a027a2c826ccdb2ad9b678761093e6cb"
REBUILD_SOURCE_SHA256: Final = "1ed8ea255df01fca10e294994557b1efc8660f933683477a5a289593da7c1c14"
INDEPENDENT_SOURCE_SHA256: Final = (
    "e0121dd2f90bbebc5f973f4e80f7b43dea5ec2d0ac04e1f253a6618b35cf0a96"
)
GEOMETRY_SOURCE_SHA256: Final = "baa4c12032174f179f1aed6ed9bde78dc6f1fb163e262980897ba3e893af8cc6"

BUNDLE_SCHEMA: Final = "encounter_control_free_production_initial_stream_v1"
BUNDLE_STATUS: Final = (
    "PASS_CONTROL_FREE_12_ROW_FILE_BACKED_PRODUCER_CONSISTENCY_ONLY_NOT_INDEPENDENT_NOT_F0_NOT_F1"
)
REBUILD_SCHEMA: Final = "encounter_control_free_production_initial_relational_rebuild_v1"
REBUILD_STATUS: Final = (
    "PASS_12_ROW_DETERMINISTIC_RELATIONAL_REBUILD_SAME_NUMERICAL_CORE_"
    "NOT_INDEPENDENT_SEMANTIC_NOT_F0_NOT_F1"
)
INDEPENDENT_SCHEMA: Final = "encounter_control_free_production_initial_independent_semantic_v1"
INDEPENDENT_STATUS: Final = (
    "PASS_12_ROW_INDEPENDENT_SOURCE_PARTITION_FREE_AXIS_SEMANTICS_"
    "ONLY_NOT_FULL_OPERATOR_NOT_F0_NOT_F1"
)
GEOMETRY_SCHEMA: Final = "encounter_geometry_bound_packed_axes_receipt_v1"
GEOMETRY_STATUS: Final = (
    "PASS_12_ROW_FREE_AXIS_GEOMETRY_PACKED_BINDING_ONLY_NOT_FULL_OPERATOR_NOT_F0_NOT_F1"
)

PROCESS_TIMEOUT_SECONDS: Final = 900
REPEAT_COUNT: Final = 2

_BUNDLE_FLAGS: Final = {
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

_REBUILD_FLAGS: Final = {
    "all_twelve_rows_rebuilt": True,
    "artifact_parser_implementation_separate": True,
    "authorizes_scientific_execution": False,
    "clean_process_observed": False,
    "deterministic_relational_rebuild_complete": True,
    "exact_bundle_bytes_reconstructed": True,
    "free_axis_geometry_rate_relational_rebuild_complete": True,
    "fresh_process": False,
    "full_operator_bound": False,
    "independent_numerical_implementation": False,
    "independent_semantic_replay_complete": False,
    "killing_contact_geometry_bound": False,
    "positive_budget_executed": False,
    "production_resource_gate": False,
    "science_executed": False,
    "source_box_relational_rebuild_complete": True,
    "topology_complete": False,
}

_INDEPENDENT_FLAGS: Final = {
    "all_twelve_rows_verified": True,
    "artifact_parser_implementation_separate": True,
    "authorizes_scientific_execution": False,
    "clean_process_observed": False,
    "continuum_verified": False,
    "exact_partitions_independently_reconstructed": True,
    "f0_pass": False,
    "free_axis_rate_semantic_containment_complete": True,
    "fresh_process": False,
    "full_operator_bound": False,
    "independent_numerical_implementation": True,
    "independent_semantic_replay_complete": False,
    "independent_semantic_replay_complete_for_declared_scope": True,
    "initial_component_semantic_containment_complete": True,
    "initial_marginal_semantic_containment_complete": True,
    "killing_contact_geometry_bound": False,
    "positive_budget_executed": False,
    "producer_interval_endpoints_consumed_only_as_outer_envelopes": True,
    "producer_nonpromotion_flags_fail_closed": True,
    "producer_positive_semantic_claims_used_as_authority": False,
    "producer_quadrature_ledgers_consumed": False,
    "production_resource_gate": False,
    "propagation_executed": False,
    "science_executed": False,
    "topology_complete": False,
}

_GEOMETRY_FLAGS: Final = {
    "authorizes_scientific_execution": False,
    "canonical_to_native_conversion_bound_all_rows": True,
    "clean_process_observed": False,
    "f0_pass": False,
    "free_axis_operator_geometry_bound_all_rows": True,
    "fresh_process": False,
    "full_operator_bound": False,
    "independent_semantic_replay_complete": False,
    "independent_source_partition_free_axis_semantic_replay_complete": True,
    "killing_contact_geometry_bound": False,
    "positive_budget_executed": False,
    "production_resource_gate": False,
    "propagation_executed": False,
    "science_executed": False,
    "topology_complete": False,
}

_OUTER_FLAGS: Final = {
    "authorizes_scientific_execution": False,
    "clean_process_replay_complete_for_declared_scope": True,
    "continuum_verified": False,
    "deterministic_two_repeat_match": True,
    "f0_pass": False,
    "five_fresh_processes_per_repeat_observed": True,
    "full_operator_bound": False,
    "independent_backend": False,
    "independent_semantic_replay_complete": False,
    "independent_source_partition_free_axis_semantic_replay_complete": True,
    "killing_contact_geometry_bound": False,
    "positive_budget_executed": False,
    "production_resource_gate": False,
    "propagation_executed": False,
    "science_executed": False,
    "serialized_boundary_between_stages": True,
    "topology_complete": False,
}


class CleanProcessReplayFailure(RuntimeError):
    """Fail-closed error for the clean-process replay boundary."""


def _sha(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _canonical(payload: object) -> bytes:
    return (json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=True) + "\n").encode("ascii")


def _digest(domain: bytes, payload: object) -> str:
    if not domain.endswith(b"\0"):
        raise CleanProcessReplayFailure("digest domain is not terminated")
    return _sha(domain + _canonical(payload))


def _strict_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if type(key) is not str or key in result:
            raise CleanProcessReplayFailure("JSON has a duplicate or invalid key")
        result[key] = value
    return result


def _reject_constant(value: str) -> object:
    raise CleanProcessReplayFailure(f"JSON has a non-finite constant: {value}")


def _parse(payload: bytes, *, canonical: bool, label: str) -> dict[str, object]:
    try:
        parsed = json.loads(
            payload.decode("ascii"),
            object_pairs_hook=_strict_object,
            parse_constant=_reject_constant,
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CleanProcessReplayFailure(f"{label} is not strict ASCII JSON") from exc
    if type(parsed) is not dict:
        raise CleanProcessReplayFailure(f"{label} is not a JSON object")
    if canonical and _canonical(parsed) != payload:
        raise CleanProcessReplayFailure(f"{label} is not canonical JSON")
    return parsed


def _read_regular(path: Path, *, maximum: int) -> bytes:
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as exc:
        raise CleanProcessReplayFailure(f"cannot open required file: {path}") from exc
    try:
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode) or before.st_size > maximum:
            raise CleanProcessReplayFailure(f"required file is not bounded regular data: {path}")
        chunks: list[bytes] = []
        observed = 0
        while True:
            chunk = os.read(descriptor, min(1 << 20, maximum + 1 - observed))
            if not chunk:
                break
            chunks.append(chunk)
            observed += len(chunk)
            if observed > maximum:
                raise CleanProcessReplayFailure(f"required file is too large: {path}")
        after = os.fstat(descriptor)
        snapshot_before = (
            before.st_dev,
            before.st_ino,
            before.st_size,
            before.st_mtime_ns,
            before.st_ctime_ns,
        )
        snapshot_after = (
            after.st_dev,
            after.st_ino,
            after.st_size,
            after.st_mtime_ns,
            after.st_ctime_ns,
        )
        if snapshot_before != snapshot_after or observed != before.st_size:
            raise CleanProcessReplayFailure(f"required file changed during read: {path}")
        return b"".join(chunks)
    finally:
        os.close(descriptor)


def _sha_file(path: Path) -> str:
    return _sha(_read_regular(path, maximum=20_000_000))


def _source_paths(report_root: Path) -> dict[str, tuple[Path, str]]:
    return {
        "analytic_source": (
            report_root / "artifacts/data/physical_initial_analytic_source_v1.json",
            ANALYTIC_SOURCE_SHA256,
        ),
        "configuration": (
            report_root / "artifacts/data/physical_configuration_family_control_free_v1.json",
            CONFIGURATION_SHA256,
        ),
        "f0_core": (report_root / "code/rate_defined_tensor_f0.py", F0_SOURCE_SHA256),
        "geometry": (
            report_root / "code/rate_defined_tensor_f0_geometry_bound_packed_axes.py",
            GEOMETRY_SOURCE_SHA256,
        ),
        "independent": (
            report_root / "code/rate_defined_tensor_f0_production_initial_independent.py",
            INDEPENDENT_SOURCE_SHA256,
        ),
        "packed_core": (
            report_root / "code/rate_defined_tensor_f0_packed.py",
            PACKED_SOURCE_SHA256,
        ),
        "rebuild": (
            report_root / "code/rate_defined_tensor_f0_production_initial_rebuild.py",
            REBUILD_SOURCE_SHA256,
        ),
        "stream": (
            report_root / "code/rate_defined_tensor_f0_production_initial_stream.py",
            STREAM_SOURCE_SHA256,
        ),
    }


def _verify_sources(report_root: Path) -> dict[str, str]:
    observed: dict[str, str] = {}
    for name, (path, accepted) in _source_paths(report_root).items():
        digest = _sha_file(path)
        if not hmac.compare_digest(digest, accepted):
            raise CleanProcessReplayFailure(f"accepted {name} bytes changed")
        observed[name] = digest
    return observed


def _verify_receipt_digest(payload: dict[str, object], *, domain: bytes, label: str) -> None:
    claimed = payload.get("receipt_sha256")
    if type(claimed) is not str:
        raise CleanProcessReplayFailure(f"{label} receipt digest is missing")
    core = {key: value for key, value in payload.items() if key != "receipt_sha256"}
    if not hmac.compare_digest(claimed, _digest(domain, core)):
        raise CleanProcessReplayFailure(f"{label} receipt self-digest drifted")


def _is_sha256(value: object) -> bool:
    return (
        type(value) is str
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _expected_rows(report_root: Path) -> tuple[tuple[str, list[int]], ...]:
    configuration_bytes = _read_regular(
        report_root / "artifacts/data/physical_configuration_family_control_free_v1.json",
        maximum=2_000_000,
    )
    if _sha(configuration_bytes) != CONFIGURATION_SHA256:
        raise CleanProcessReplayFailure("accepted configuration bytes changed")
    configuration = _parse(
        configuration_bytes,
        canonical=True,
        label="accepted configuration",
    )
    rows = configuration.get("configurations")
    if type(rows) is not list or len(rows) != 12:
        raise CleanProcessReplayFailure("accepted configuration row registry drifted")
    expected: list[tuple[str, list[int]]] = []
    for row in rows:
        if type(row) is not dict or type(row.get("label")) is not str:
            raise CleanProcessReplayFailure("accepted configuration row is invalid")
        shape = [
            row.get("midpoint", {}).get("size"),
            row.get("relative_parallel", {}).get("size"),
            row.get("relative_perpendicular", {}).get("size"),
        ]
        if any(type(size) is not int or size <= 0 for size in shape):
            raise CleanProcessReplayFailure("accepted configuration shape is invalid")
        expected.append((row["label"], shape))
    return tuple(expected)


def _validate_evidence(report_root: Path, evidence: object) -> None:
    if type(evidence) is not dict or set(evidence) != {
        "bundle_manifest_sha256",
        "family_relation_sha256",
        "geometry_receipt_sha256",
        "independent_receipt_sha256",
        "relational_rebuild_receipt_sha256",
        "rows",
    }:
        raise CleanProcessReplayFailure("clean-process evidence schema drifted")
    for key in (
        "bundle_manifest_sha256",
        "family_relation_sha256",
        "geometry_receipt_sha256",
        "independent_receipt_sha256",
        "relational_rebuild_receipt_sha256",
    ):
        if not _is_sha256(evidence[key]):
            raise CleanProcessReplayFailure(f"clean-process evidence {key} is invalid")
    rows = evidence["rows"]
    expected_rows = _expected_rows(report_root)
    if type(rows) is not list or len(rows) != len(expected_rows):
        raise CleanProcessReplayFailure("clean-process evidence row count drifted")
    wrapper_digests: set[str] = set()
    for index, (row, (label, shape)) in enumerate(zip(rows, expected_rows, strict=True)):
        if type(row) is not dict or set(row) != {
            "configuration_index",
            "configuration_label",
            "conversion_receipt_sha256s",
            "row_relation_sha256",
            "source_box_relation_sha256",
            "tensor_shape",
            "wrapper_binding_sha256",
        }:
            raise CleanProcessReplayFailure(f"clean-process evidence row {index} schema drifted")
        conversions = row["conversion_receipt_sha256s"]
        if (
            row["configuration_index"] != index
            or row["configuration_label"] != label
            or row["tensor_shape"] != shape
            or not _is_sha256(row["row_relation_sha256"])
            or not _is_sha256(row["source_box_relation_sha256"])
            or not _is_sha256(row["wrapper_binding_sha256"])
            or type(conversions) is not list
            or len(conversions) != 6
            or not all(_is_sha256(digest) for digest in conversions)
        ):
            raise CleanProcessReplayFailure(f"clean-process evidence row {index} drifted")
        wrapper_digests.add(row["wrapper_binding_sha256"])
    if len(wrapper_digests) != len(expected_rows):
        raise CleanProcessReplayFailure("clean-process wrapper digests are not row-distinct")


def _run_process(
    command: list[str],
    *,
    cwd: Path,
    seen_pids: set[int],
    label: str,
) -> dict[str, object]:
    environment = os.environ.copy()
    environment.pop("PYTHONPATH", None)
    environment.pop("PYTHONHOME", None)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment["LC_ALL"] = "C"
    environment["LANG"] = "C"
    process = subprocess.Popen(
        command,
        cwd=cwd,
        env=environment,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        start_new_session=True,
    )
    if process.pid in seen_pids:
        process.kill()
        process.wait()
        raise CleanProcessReplayFailure("a fresh process identifier was unexpectedly reused")
    seen_pids.add(process.pid)
    try:
        stdout, stderr = process.communicate(timeout=PROCESS_TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired as exc:
        process.kill()
        process.communicate()
        raise CleanProcessReplayFailure(f"{label} process timed out") from exc
    except BaseException:
        process.kill()
        process.communicate()
        raise
    if process.returncode != 0:
        tail = stderr[-2_000:].decode("utf-8", errors="replace")
        raise CleanProcessReplayFailure(f"{label} process failed: {tail}")
    if stderr:
        raise CleanProcessReplayFailure(f"{label} process wrote unexpected stderr")
    return _parse(stdout, canonical=True, label=f"{label} stdout")


def _require_cli_status(
    payload: dict[str, object],
    *,
    expected_status: str,
    label: str,
    expected_receipt_sha256: str | None = None,
) -> None:
    expected_keys = (
        {"status"}
        if expected_receipt_sha256 is None
        else {
            "receipt_sha256",
            "status",
        }
    )
    if set(payload) != expected_keys or payload.get("status") != expected_status:
        raise CleanProcessReplayFailure(f"{label} CLI acknowledgement drifted")
    if expected_receipt_sha256 is not None and payload.get("receipt_sha256") != (
        expected_receipt_sha256
    ):
        raise CleanProcessReplayFailure(f"{label} CLI receipt digest drifted")


def _run_one_repeat(
    report_root: Path,
    repeat_root: Path,
    *,
    seen_pids: set[int],
) -> dict[str, object]:
    code = report_root / "code"
    bundle = repeat_root / "bundle"
    rebuild_path = repeat_root / "relational_receipt.json"
    independent_path = repeat_root / "independent_receipt.json"
    geometry_path = repeat_root / "geometry_receipt.json"
    stream_script = code / "rate_defined_tensor_f0_production_initial_stream.py"
    rebuild_script = code / "rate_defined_tensor_f0_production_initial_rebuild.py"
    independent_script = code / "rate_defined_tensor_f0_production_initial_independent.py"
    geometry_script = code / "rate_defined_tensor_f0_geometry_bound_packed_axes.py"

    produce_ack = _run_process(
        [
            sys.executable,
            "-I",
            str(stream_script),
            "produce",
            "--report-root",
            str(report_root),
            "--output",
            str(bundle),
        ],
        cwd=repeat_root,
        seen_pids=seen_pids,
        label="bundle producer",
    )
    _require_cli_status(produce_ack, expected_status=BUNDLE_STATUS, label="bundle producer")
    verify_ack = _run_process(
        [sys.executable, "-I", str(stream_script), "verify", "--bundle", str(bundle)],
        cwd=repeat_root,
        seen_pids=seen_pids,
        label="bundle verifier",
    )
    _require_cli_status(verify_ack, expected_status=BUNDLE_STATUS, label="bundle verifier")
    rebuild_ack = _run_process(
        [
            sys.executable,
            "-I",
            str(rebuild_script),
            "--bundle",
            str(bundle),
            "--receipt",
            str(rebuild_path),
        ],
        cwd=repeat_root,
        seen_pids=seen_pids,
        label="relational rebuild",
    )
    independent_ack = _run_process(
        [
            sys.executable,
            "-I",
            str(independent_script),
            "--bundle",
            str(bundle),
            "--receipt",
            str(independent_path),
        ],
        cwd=repeat_root,
        seen_pids=seen_pids,
        label="independent scoped verifier",
    )
    geometry_ack = _run_process(
        [
            sys.executable,
            "-I",
            str(geometry_script),
            "--bundle",
            str(bundle),
            "--receipt",
            str(geometry_path),
        ],
        cwd=repeat_root,
        seen_pids=seen_pids,
        label="packed-axis binder",
    )

    bundle_bytes = _read_regular(bundle / "bundle.json", maximum=2_000_000)
    rebuild_bytes = _read_regular(rebuild_path, maximum=2_000_000)
    independent_bytes = _read_regular(independent_path, maximum=2_000_000)
    geometry_bytes = _read_regular(geometry_path, maximum=2_000_000)
    manifest = _parse(bundle_bytes, canonical=True, label="bundle manifest")
    relational = _parse(rebuild_bytes, canonical=True, label="relational receipt")
    semantic = _parse(independent_bytes, canonical=True, label="independent receipt")
    geometry = _parse(geometry_bytes, canonical=True, label="geometry receipt")

    _verify_receipt_digest(
        relational,
        domain=b"production-initial-relational-rebuild-receipt-v1\0",
        label="relational",
    )
    _verify_receipt_digest(
        semantic,
        domain=b"production-initial-independent-semantic-receipt-v1\0",
        label="independent",
    )
    _verify_receipt_digest(
        geometry,
        domain=b"geometry-bound-packed-axes-receipt-v1\0",
        label="geometry",
    )
    _require_cli_status(
        rebuild_ack,
        expected_status=REBUILD_STATUS,
        expected_receipt_sha256=relational["receipt_sha256"],
        label="relational rebuild",
    )
    _require_cli_status(
        independent_ack,
        expected_status=INDEPENDENT_STATUS,
        expected_receipt_sha256=semantic["receipt_sha256"],
        label="independent scoped verifier",
    )
    _require_cli_status(
        geometry_ack,
        expected_status=GEOMETRY_STATUS,
        expected_receipt_sha256=geometry["receipt_sha256"],
        label="packed-axis binder",
    )

    bundle_sha = _sha(bundle_bytes)
    if (
        manifest.get("schema") != BUNDLE_SCHEMA
        or manifest.get("status") != BUNDLE_STATUS
        or manifest.get("configuration_count") != 12
        or manifest.get("configuration_sha256") != CONFIGURATION_SHA256
        or manifest.get("analytic_source_sha256") != ANALYTIC_SOURCE_SHA256
        or manifest.get("flags") != _BUNDLE_FLAGS
        or type(manifest.get("rows")) is not list
        or len(manifest["rows"]) != 12
    ):
        raise CleanProcessReplayFailure("bundle scope metadata drifted")
    if (
        relational.get("schema") != REBUILD_SCHEMA
        or relational.get("status") != REBUILD_STATUS
        or relational.get("bundle_manifest_sha256") != bundle_sha
        or relational.get("rebuild_source_sha256") != REBUILD_SOURCE_SHA256
        or relational.get("numerical_core_sha256") != F0_SOURCE_SHA256
        or relational.get("flags") != _REBUILD_FLAGS
        or type(relational.get("rows")) is not list
        or len(relational["rows"]) != 12
    ):
        raise CleanProcessReplayFailure("relational receipt scope metadata drifted")
    if (
        semantic.get("schema") != INDEPENDENT_SCHEMA
        or semantic.get("status") != INDEPENDENT_STATUS
        or semantic.get("bundle_manifest_sha256") != bundle_sha
        or semantic.get("verifier_source_sha256") != INDEPENDENT_SOURCE_SHA256
        or semantic.get("flags") != _INDEPENDENT_FLAGS
        or semantic.get("method", {}).get("backend_independence_scope")
        != "separate_source_and_higher_precision_same_gmpy2_mpfr_library"
        or type(semantic.get("rows")) is not list
        or len(semantic["rows"]) != 12
    ):
        raise CleanProcessReplayFailure("independent receipt scope metadata drifted")
    if (
        geometry.get("schema") != GEOMETRY_SCHEMA
        or geometry.get("status") != GEOMETRY_STATUS
        or geometry.get("bundle_manifest_sha256") != bundle_sha
        or geometry.get("geometry_source_sha256") != GEOMETRY_SOURCE_SHA256
        or geometry.get("independent_source_sha256") != INDEPENDENT_SOURCE_SHA256
        or geometry.get("rebuild_source_sha256") != REBUILD_SOURCE_SHA256
        or geometry.get("packed_source_sha256") != PACKED_SOURCE_SHA256
        or geometry.get("flags") != _GEOMETRY_FLAGS
        or type(geometry.get("rows")) is not list
        or len(geometry["rows"]) != 12
    ):
        raise CleanProcessReplayFailure("geometry receipt scope metadata drifted")
    if not (
        manifest["family_relation_sha256"]
        == relational["family_relation_sha256"]
        == semantic["family_relation_sha256"]
    ):
        raise CleanProcessReplayFailure("family relation joins drifted")

    row_evidence: list[dict[str, object]] = []
    for index, (summary, replayed, verified, bound) in enumerate(
        zip(
            manifest["rows"],
            relational["rows"],
            semantic["rows"],
            geometry["rows"],
            strict=True,
        )
    ):
        keys = ("configuration_index", "configuration_label", "row_relation_sha256")
        if any(
            candidate.get(key) != summary.get(key)
            for candidate in (replayed, verified, bound)
            for key in keys
        ):
            raise CleanProcessReplayFailure(f"row {index} registry/relation join drifted")
        if not (
            replayed.get("source_box_relation_sha256")
            == verified.get("source_box_relation_sha256")
            == bound.get("source_box_relation_sha256")
        ):
            raise CleanProcessReplayFailure(f"row {index} source/box join drifted")
        if not (
            replayed.get("tensor_shape")
            == verified.get("tensor_shape")
            == bound.get("tensor_shape")
        ):
            raise CleanProcessReplayFailure(f"row {index} tensor-shape join drifted")
        if (
            bound.get("relational_rebuild_receipt_sha256") != relational["receipt_sha256"]
            or bound.get("independent_semantic_receipt_sha256") != semantic["receipt_sha256"]
            or type(bound.get("wrapper_binding_sha256")) is not str
            or type(bound.get("conversion_receipt_sha256s")) is not list
            or len(bound["conversion_receipt_sha256s"]) != 6
        ):
            raise CleanProcessReplayFailure(f"row {index} packed binding join drifted")
        row_evidence.append(
            {
                "configuration_index": index,
                "configuration_label": summary["configuration_label"],
                "conversion_receipt_sha256s": bound["conversion_receipt_sha256s"],
                "row_relation_sha256": summary["row_relation_sha256"],
                "source_box_relation_sha256": replayed["source_box_relation_sha256"],
                "tensor_shape": replayed["tensor_shape"],
                "wrapper_binding_sha256": bound["wrapper_binding_sha256"],
            }
        )
    return {
        "bundle_manifest_sha256": bundle_sha,
        "family_relation_sha256": manifest["family_relation_sha256"],
        "geometry_receipt_sha256": geometry["receipt_sha256"],
        "independent_receipt_sha256": semantic["receipt_sha256"],
        "relational_rebuild_receipt_sha256": relational["receipt_sha256"],
        "rows": row_evidence,
    }


def build_clean_process_replay_receipt(report_root: Path) -> dict[str, object]:
    """Run two serialized five-process repeats and require exact agreement."""

    if report_root.is_symlink():
        raise CleanProcessReplayFailure("report root is a symlink")
    report_root = report_root.resolve()
    sources = _verify_sources(report_root)
    seen_pids: set[int] = set()
    evidence: list[dict[str, object]] = []
    with tempfile.TemporaryDirectory(prefix="encounter-clean-replay-") as temporary:
        root = Path(temporary)
        for repeat in range(REPEAT_COUNT):
            repeat_root = root / f"repeat-{repeat}"
            repeat_root.mkdir()
            evidence.append(_run_one_repeat(report_root, repeat_root, seen_pids=seen_pids))
    if evidence[0] != evidence[1]:
        raise CleanProcessReplayFailure("the two clean-process repeats disagreed")
    _validate_evidence(report_root, evidence[0])
    evidence_sha = _digest(b"production-initial-clean-replay-evidence-v1\0", evidence[0])
    if len(seen_pids) != 5 * REPEAT_COUNT:
        raise CleanProcessReplayFailure("fresh-process count drifted")
    core = {
        "evidence": evidence[0],
        "flags": _OUTER_FLAGS,
        "orchestrator_source_sha256": _sha_file(Path(__file__).resolve()),
        "repeat_count": REPEAT_COUNT,
        "repeat_evidence_sha256s": [evidence_sha] * REPEAT_COUNT,
        "replay_mode": "five_separate_python_I_processes_per_repeat_with_serialized_files",
        "schema": SCHEMA,
        "sources": sources,
        "status": STATUS,
        "total_fresh_processes_observed": len(seen_pids),
    }
    return {
        **core,
        "receipt_sha256": _digest(b"production-initial-clean-process-replay-v1\0", core),
    }


def validate_clean_process_replay_receipt(
    report_root: Path,
    receipt: dict[str, object],
    *,
    expected_receipt_sha256: str,
) -> None:
    """Validate one explicitly pinned retained receipt and its evidence schema."""

    report_root = report_root.resolve()
    sources = _verify_sources(report_root)
    if not _is_sha256(expected_receipt_sha256) or not hmac.compare_digest(
        receipt.get("receipt_sha256", ""), expected_receipt_sha256
    ):
        raise CleanProcessReplayFailure("retained clean-process receipt is not the pinned result")
    _verify_receipt_digest(
        receipt,
        domain=b"production-initial-clean-process-replay-v1\0",
        label="clean-process replay",
    )
    evidence = receipt.get("evidence")
    repeat_shas = receipt.get("repeat_evidence_sha256s")
    _validate_evidence(report_root, evidence)
    if (
        set(receipt)
        != {
            "evidence",
            "flags",
            "orchestrator_source_sha256",
            "receipt_sha256",
            "repeat_count",
            "repeat_evidence_sha256s",
            "replay_mode",
            "schema",
            "sources",
            "status",
            "total_fresh_processes_observed",
        }
        or receipt.get("schema") != SCHEMA
        or receipt.get("status") != STATUS
        or receipt.get("sources") != sources
        or receipt.get("flags") != _OUTER_FLAGS
        or receipt.get("repeat_count") != REPEAT_COUNT
        or receipt.get("total_fresh_processes_observed") != 5 * REPEAT_COUNT
        or receipt.get("replay_mode")
        != "five_separate_python_I_processes_per_repeat_with_serialized_files"
        or type(repeat_shas) is not list
        or repeat_shas
        != [_digest(b"production-initial-clean-replay-evidence-v1\0", evidence)] * REPEAT_COUNT
        or receipt.get("orchestrator_source_sha256") != _sha_file(Path(__file__).resolve())
    ):
        raise CleanProcessReplayFailure("retained clean-process receipt drifted")


def write_receipt(report_root: Path, output: Path) -> dict[str, object]:
    receipt = build_clean_process_replay_receipt(report_root)
    if output.exists() or output.is_symlink():
        raise CleanProcessReplayFailure("receipt output already exists")
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(f".{output.name}.tmp-{os.getpid()}")
    try:
        with temporary.open("xb") as target:
            target.write(_canonical(receipt))
        os.replace(temporary, output)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise
    return receipt


def _main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report-root", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    arguments = parser.parse_args()
    receipt = write_receipt(arguments.report_root, arguments.receipt)
    print(
        _canonical(
            {"receipt_sha256": receipt["receipt_sha256"], "status": receipt["status"]}
        ).decode("ascii"),
        end="",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
