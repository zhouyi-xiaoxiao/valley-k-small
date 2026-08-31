#!/usr/bin/env python3
"""Authenticated end-to-end adversarial probes for the raw-flux validator.

This harness never imports gmpy2.  It operator-pins and descriptor-snapshots
the unified launcher, which in turn authenticates the sole MPFR runtime before
executing the independently pinned validator.  Mutation probes are temporary
files and cannot overwrite the canonical raw-flux artifact.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Callable

HERE = Path(__file__).resolve()
REPORT = HERE.parents[1]
LAUNCHER = REPORT / "code/run_continuum_c1_mpfr_authenticated_v1.py"
VALIDATOR = REPORT / "code/validate_continuum_c1_fixed_row_raw_flux_source_v1.py"
ARTIFACT = REPORT / "artifacts/data/continuum_c1_fixed_row_raw_flux_source_v1.json"
RECEIPT = REPORT / (
    "artifacts/data/continuum_c1_fixed_row_raw_flux_validator_authenticated_outer_receipt_v1.json"
)
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


class ProbeFailure(RuntimeError):
    """The authentication or rejection behavior differed from the fixed gate."""


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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


def _run_launcher(
    launcher_sha256: str,
    *,
    artifact_probe: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    arguments = [
        sys.executable,
        "-I",
        "-S",
        "-c",
        BOOTSTRAP,
        str(LAUNCHER),
        launcher_sha256,
        "--target",
        "raw_flux_validator",
    ]
    if artifact_probe is not None:
        arguments.extend(("--artifact-probe", str(artifact_probe)))
    return subprocess.run(
        arguments,
        cwd=REPORT,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=90,
        check=False,
    )


def _require_hold(
    result: subprocess.CompletedProcess[str],
    label: str,
    expected_fragment: str | None = None,
) -> None:
    combined = result.stdout + result.stderr
    if (
        result.returncode == 0
        or "HOLD" not in combined
        or (expected_fragment is not None and expected_fragment not in combined)
    ):
        raise ProbeFailure(
            f"{label} was not rejected with HOLD: "
            f"returncode={result.returncode}, output={combined!r}"
        )


def _same_member_smuggling(value: dict[str, Any]) -> None:
    value["claim_boundary"]["same_member_acceptance_receipt_present"] = True


def _periodic_seam_reorientation(value: dict[str, Any]) -> None:
    for row in value["rows"]:
        for axis in row["axes"]:
            if axis["periodic"]:
                seam = axis["edge_records"][-1]
                if seam["right_cell_index"] != 0:
                    raise ProbeFailure("canonical periodic seam is not last-to-zero")
                seam["right_cell_index"] = 1
                return
    raise ProbeFailure("canonical artifact has no periodic axis")


def _source_pin_substitution(value: dict[str, Any]) -> None:
    value["source_pins"]["production_bundle"]["sha256"] = "0" * 64


def _run_mutation(
    launcher_sha256: str,
    canonical: dict[str, Any],
    label: str,
    mutate: Callable[[dict[str, Any]], None],
) -> None:
    candidate = copy.deepcopy(canonical)
    mutate(candidate)
    with tempfile.TemporaryDirectory(prefix="raw-flux-validator-probe-") as directory:
        # macOS exposes /var as a symlink to /private/var; resolve only the
        # newly created temporary directory before the launcher's no-symlink
        # probe-path gate examines every component.
        path = Path(directory).resolve(strict=True) / f"{label}.json"
        path.write_bytes(_canonical(candidate))
        _require_hold(
            _run_launcher(launcher_sha256, artifact_probe=path),
            label,
            "HOLD_PROBE HOLD: selected raw-flux artifact differs from independent reconstruction",
        )


def _main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--launcher-sha256", required=True)
    parser.add_argument("--receipt-sha256", required=True)
    arguments = parser.parse_args()
    if (
        SHA256_RE.fullmatch(arguments.launcher_sha256) is None
        or SHA256_RE.fullmatch(arguments.receipt_sha256) is None
    ):
        raise ProbeFailure("expected launcher and receipt digests must be lowercase SHA-256")
    if _sha256(LAUNCHER) != arguments.launcher_sha256:
        raise ProbeFailure("operator-frozen launcher digest differs from live bytes")

    direct = subprocess.run(
        [sys.executable, "-I", "-S", str(VALIDATOR)],
        cwd=REPORT,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=10,
        check=False,
    )
    _require_hold(direct, "unauthenticated direct validator entry")

    canonical_result = _run_launcher(arguments.launcher_sha256)
    if (
        canonical_result.returncode != 0
        or canonical_result.stderr
        or canonical_result.stdout.strip() != arguments.receipt_sha256
        or _sha256(RECEIPT) != arguments.receipt_sha256
    ):
        raise ProbeFailure(
            "canonical authenticated validation did not reproduce its receipt: "
            f"returncode={canonical_result.returncode}, "
            f"stdout={canonical_result.stdout!r}, stderr={canonical_result.stderr!r}"
        )

    canonical = json.loads(ARTIFACT.read_bytes())
    if ARTIFACT.read_bytes() != _canonical(canonical):
        raise ProbeFailure("canonical artifact bytes are not canonical JSON")
    for label, mutation in (
        ("same-member-smuggling", _same_member_smuggling),
        ("periodic-seam-reorientation", _periodic_seam_reorientation),
        ("source-pin-substitution", _source_pin_substitution),
    ):
        _run_mutation(
            arguments.launcher_sha256,
            canonical,
            label,
            mutation,
        )

    print(
        json.dumps(
            {
                "canonical_authenticated_validation": "PASS",
                "direct_unauthenticated_entry": "HOLD",
                "mutation_probes_rejected": 3,
                "receipt_sha256": arguments.receipt_sha256,
                "status": "PASS_RAW_FLUX_AUTHENTICATED_ADVERSARIAL_V1",
            },
            sort_keys=True,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
