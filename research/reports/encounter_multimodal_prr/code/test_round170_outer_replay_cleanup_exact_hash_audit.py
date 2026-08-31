from __future__ import annotations

import errno
import hashlib
import inspect
import os
import stat
from pathlib import Path

import pytest
import run_rate_defined_tensor_f0_production_killing_geometry_independent_replay as replay

REPORT_ROOT = Path(__file__).resolve().parents[1]
RUNNER = REPORT_ROOT / "code/run_rate_defined_tensor_f0_production_killing_geometry_independent_replay.py"
PRIMARY_TESTS = REPORT_ROOT / "code/test_run_rate_defined_tensor_f0_production_killing_geometry_independent_replay.py"
EXPECTED_RUNNER_SHA256 = "1a3cecc0ca323b4744f6056a82c322bb71b75e703aab4cf5b418e515357e9e84"
EXPECTED_PRIMARY_TESTS_SHA256 = "84aa1427881343e59471f6609d6c76fbea5830924aa3bd2147a8845e4044b401"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _target(path: Path) -> replay.ReceiptTarget:
    return replay.ReceiptTarget(path, replay._directory_identity(os.lstat(path.parent)))


def test_exact_candidate_hashes_are_frozen() -> None:
    assert _sha256(RUNNER) == EXPECTED_RUNNER_SHA256
    assert _sha256(PRIMARY_TESTS) == EXPECTED_PRIMARY_TESTS_SHA256


def test_final_reread_uses_the_shared_confirmed_close_primitive() -> None:
    source = inspect.getsource(replay._read_published_at)
    assert "_close_descriptor_confirmed(descriptor)" in source
    assert "raise ReplayHold(HOLD_CLEANUP)" in source
    assert "finally:" in source
    assert "os.close(descriptor)" not in source


@pytest.mark.parametrize("failure_after_close", [False, True])
def test_final_reread_single_close_fault_has_no_fd_leak(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    failure_after_close: bool,
) -> None:
    path = tmp_path / "receipt.json"
    publication = replay._publish_exclusive(_target(path), b"owned", maximum_bytes=1024)
    real_close = replay.os.close
    real_fstat = replay.os.fstat
    attacked_descriptor: int | None = None
    injected = False

    def attacked_close(descriptor: int) -> None:
        nonlocal attacked_descriptor, injected
        metadata = real_fstat(descriptor)
        if not injected and stat.S_ISREG(metadata.st_mode):
            injected = True
            attacked_descriptor = descriptor
            if failure_after_close:
                real_close(descriptor)
            raise OSError(errno.EIO, "round170 injected final-reread close fault")
        real_close(descriptor)

    monkeypatch.setattr(replay.os, "close", attacked_close)
    assert replay._close_publication(publication) is True
    assert injected is True
    assert attacked_descriptor is not None
    assert path.read_bytes() == b"owned"
    with pytest.raises(OSError) as caught:
        real_fstat(attacked_descriptor)
    assert caught.value.errno == errno.EBADF


def test_reopened_parent_fd_number_reuse_is_attacked_by_phase(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    path = tmp_path / "receipt.json"
    publication = replay._publish_exclusive(_target(path), b"owned", maximum_bytes=1024)
    original_descriptor = publication.directory_descriptor
    real_close = replay.os.close
    real_fstat = replay.os.fstat
    original_close_reported_after_effect = False
    reopened_close_attacked = False
    reopened_descriptor: int | None = None

    def attacked_close(descriptor: int) -> None:
        nonlocal original_close_reported_after_effect
        nonlocal reopened_close_attacked, reopened_descriptor
        metadata = real_fstat(descriptor)
        if descriptor == original_descriptor and not original_close_reported_after_effect:
            original_close_reported_after_effect = True
            real_close(descriptor)
            raise OSError(errno.EIO, "round170 injected post-effect parent close fault")
        if (
            original_close_reported_after_effect
            and stat.S_ISDIR(metadata.st_mode)
            and not reopened_close_attacked
        ):
            reopened_close_attacked = True
            reopened_descriptor = descriptor
            raise OSError(errno.EIO, "round170 injected reopened-parent close fault")
        real_close(descriptor)

    monkeypatch.setattr(replay.os, "close", attacked_close)
    assert replay._close_publication(publication) is False
    assert original_close_reported_after_effect is True
    assert reopened_close_attacked is True
    assert reopened_descriptor == original_descriptor
    assert not path.exists()
    with pytest.raises(OSError) as caught:
        real_fstat(reopened_descriptor)
    assert caught.value.errno == errno.EBADF

