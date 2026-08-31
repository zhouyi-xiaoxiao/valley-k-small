from __future__ import annotations

import hashlib
import json
import os
from collections import Counter
from pathlib import Path

import build_continuum_c0_model_contract_candidate_v2 as c0_builder
import build_continuum_c1_ideal_refinement_contract_candidate_v1 as producer
import pytest
import validate_continuum_c0_model_contract_candidate_v2 as c0_verifier
import validate_continuum_c1_ideal_refinement_contract_candidate_v1 as verifier
from continuum_c1_ideal_refinement_contract_v1_note_pin import (
    THEOREM_NOTE_RELATIVE,
    THEOREM_NOTE_SHA256,
)

REPORT = Path(__file__).resolve().parents[1]
CONTRACT_RELATIVE = Path(
    "artifacts/data/continuum_c1_ideal_refinement_contract_candidate_v1.json"
)


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _read(relative: Path) -> bytes:
    return c0_builder.read_relative_snapshot(REPORT, relative)


def test_single_note_pin_matches_current_theorem_note_bytes() -> None:
    note = _read(THEOREM_NOTE_RELATIVE)
    assert _sha256(note) == THEOREM_NOTE_SHA256
    assert producer.THEOREM_NOTE_SHA256 == THEOREM_NOTE_SHA256
    assert verifier.THEOREM_NOTE_SHA256 == THEOREM_NOTE_SHA256


def test_all_three_declared_sources_match_current_exact_bytes() -> None:
    expected = {
        "configuration_family": (
            producer.CONFIGURATION_SOURCE_RELATIVE,
            producer.CONFIGURATION_SOURCE_SHA256,
        ),
        "mathematical_source": (
            producer.MATHEMATICAL_SOURCE_RELATIVE,
            producer.MATHEMATICAL_SOURCE_SHA256,
        ),
        "theorem_note": (THEOREM_NOTE_RELATIVE, THEOREM_NOTE_SHA256),
    }
    for role, (relative, digest) in expected.items():
        assert _sha256(_read(relative)) == digest, role


def test_candidate_source_descriptors_match_single_currentness_registry() -> None:
    candidate = json.loads(_read(CONTRACT_RELATIVE).decode("ascii"))
    assert candidate["frozen_sources"] == producer.FROZEN_SOURCES
    assert candidate["frozen_sources"] == verifier.EXPECTED_FROZEN_SOURCES
    assert candidate["frozen_sources"]["theorem_note"]["sha256"] == (
        THEOREM_NOTE_SHA256
    )


def test_candidate_is_current_with_builder_and_standalone_verifier() -> None:
    candidate = _read(CONTRACT_RELATIVE)
    assert producer.build_bytes() == candidate
    receipt = verifier.verify_contract_bytes(candidate)
    assert receipt["contract_sha256"] == verifier.EXPECTED_CONTRACT_SHA256
    assert receipt["status"] == verifier.PASS_STATUS


def test_source_open_receipts_use_full_relative_paths_exactly_once(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    expected_paths = producer.OPENED_SOURCE_PATHS
    expected_counts = Counter({path: 1 for path in expected_paths})
    real_open = os.open

    def audited_call(action):
        descriptor_paths: dict[int, Path] = {}
        observed: list[tuple[str, int]] = []

        def audited_open(path, flags, *args, **kwargs):
            raw = Path(os.fspath(path))
            directory_fd = kwargs.get("dir_fd")
            if raw.is_absolute():
                full_path = raw
            elif type(directory_fd) is int and directory_fd in descriptor_paths:
                full_path = descriptor_paths[directory_fd] / raw
            else:
                full_path = raw
            descriptor = real_open(path, flags, *args, **kwargs)
            descriptor_paths[descriptor] = full_path
            try:
                relative_path = full_path.relative_to(REPORT)
            except ValueError:
                pass
            else:
                if relative_path.suffix in {".json", ".md"}:
                    observed.append((relative_path.as_posix(), flags))
            return descriptor

        monkeypatch.setattr(os, "open", audited_open)
        try:
            result = action()
        finally:
            monkeypatch.setattr(os, "open", real_open)
        return result, Counter(path for path, _flags in observed), observed

    builder_payload, builder_counts, builder_observed = audited_call(
        producer.build_bytes
    )
    builder_receipt = producer._receipt(builder_payload, "check")
    candidate = _read(CONTRACT_RELATIVE)
    verifier_receipt, verifier_counts, verifier_observed = audited_call(
        lambda: verifier.verify_contract_bytes(candidate)
    )

    def build_with_extra_candidate_open() -> bytes:
        payload = producer.build_bytes()
        _read(CONTRACT_RELATIVE)
        return payload

    _, sentinel_counts, sentinel_observed = audited_call(
        build_with_extra_candidate_open
    )
    expected_with_sentinel = expected_counts.copy()
    expected_with_sentinel[CONTRACT_RELATIVE.as_posix()] = 1

    for receipt in (builder_receipt, verifier_receipt):
        assert receipt["opened_source_paths"] == expected_paths
        assert receipt["opened_source_counts"] == dict(expected_counts)
        assert all("/" in path for path in receipt["opened_source_paths"])
    assert builder_counts == expected_counts
    assert verifier_counts == expected_counts
    assert sentinel_counts == expected_with_sentinel
    assert sentinel_counts != expected_counts
    write_mask = os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC
    assert all(
        flags & write_mask == 0
        for _path, flags in (
            builder_observed + verifier_observed + sentinel_observed
        )
    )


def _copy_authorized_sources(target: Path, *, mutate_note: bool) -> None:
    for relative in (
        producer.CONFIGURATION_SOURCE_RELATIVE,
        producer.MATHEMATICAL_SOURCE_RELATIVE,
        THEOREM_NOTE_RELATIVE,
    ):
        destination = target / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        payload = _read(relative)
        if relative == THEOREM_NOTE_RELATIVE and mutate_note:
            payload += b"\n"
        destination.write_bytes(payload)


def test_theorem_note_byte_drift_fails_closed_in_builder_and_verifier(
    tmp_path: Path,
) -> None:
    _copy_authorized_sources(tmp_path, mutate_note=True)
    with pytest.raises(producer.BuildHold, match="theorem note hash mismatch"):
        producer.build_bytes(report=tmp_path)
    with pytest.raises(verifier.C1RefinementHold) as caught:
        verifier.verify_contract_bytes(_read(CONTRACT_RELATIVE), report=tmp_path)
    assert caught.value.code == verifier.HOLD_SOURCES


def test_configuration_source_byte_drift_fails_before_semantic_use(
    tmp_path: Path,
) -> None:
    _copy_authorized_sources(tmp_path, mutate_note=False)
    configuration = tmp_path / producer.CONFIGURATION_SOURCE_RELATIVE
    configuration.write_bytes(configuration.read_bytes().replace(b'"configuration_count": 12', b'"configuration_count": 11', 1))
    with pytest.raises(producer.BuildHold, match="configuration_family hash mismatch"):
        producer.build_bytes(report=tmp_path)
    with pytest.raises(verifier.C1RefinementHold) as caught:
        verifier.verify_contract_bytes(_read(CONTRACT_RELATIVE), report=tmp_path)
    assert caught.value.code == verifier.HOLD_SOURCES


def test_source_read_helpers_keep_descriptor_safe_semantics() -> None:
    note = c0_verifier.read_relative_snapshot(
        REPORT,
        THEOREM_NOTE_RELATIVE,
        code=verifier.HOLD_SOURCES,
    )
    assert _sha256(note) == THEOREM_NOTE_SHA256
