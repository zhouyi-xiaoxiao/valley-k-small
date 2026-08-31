from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

import pytest
from test_continuum_c1_n0_candidate_native_raw_axis_formula_v2 import (
    NeutralFixture,
    create_production_shaped_v4_fixture,
    domain_hash,
    immutable_json,
    load_isolated_module,
    sha256_file,
)

REQUEST_STATUS = "EXTERNAL_PREDECESSOR_COMMITMENT_BOUND_RESULT_BLIND_REQUEST_NO_EXECUTION_RESULT"
REPLAY_CONTEXT_DOMAIN = "encounter-continuum-c1-n0-shared-replay-context-v1"
ROLE_NAMES = {
    8: "role8_raw_axis_formula_primitive",
    9: "role9_stationary_physical_integral",
    10: "role10_killing_factor_geometry",
}
NUMERICAL_HOLD = "HOLD_CANDIDATE_KILLING_NUMERICAL_IMPLEMENTATION_INCOMPLETE"


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="ascii"))
    assert type(value) is dict
    return value


def _materialize_peer_request(
    fixture: NeutralFixture,
    plan: dict[str, Any],
    role: int,
) -> tuple[Path, Path, Path]:
    entry = plan["entries"][role - 8]
    request_path = Path(entry["request"]["path"])
    artifact_path = Path(entry["outputs"]["artifact"]["path"])
    receipt_path = Path(entry["outputs"]["validation_receipt"]["path"])
    shared_digest = plan["shared_precommit_context_sha256"]
    replay_digest = domain_hash(
        REPLAY_CONTEXT_DOMAIN,
        {
            "external_predecessor_commitment_sha256": sha256_file(fixture.commitment),
            "replay_plan_sha256": sha256_file(fixture.plan),
            "shared_precommit_context_sha256": shared_digest,
        },
    )
    immutable_json(
        request_path,
        {
            "external_predecessor_commitment": {
                "path": str(fixture.commitment),
                "sha256": sha256_file(fixture.commitment),
            },
            "plan": {
                "path": str(fixture.plan),
                "sha256": sha256_file(fixture.plan),
            },
            "plan_entry_id": ROLE_NAMES[role],
            "role": {"role_id": role, "role_name": ROLE_NAMES[role]},
            "schema": entry["request"]["schema"],
            "shared_precommit_context_sha256": shared_digest,
            "shared_replay_context_sha256": replay_digest,
            "status": REQUEST_STATUS,
        },
    )
    return request_path, artifact_path, receipt_path


def _run_invocation(invocation: dict[str, Any]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        invocation["argv"],
        check=False,
        capture_output=True,
        text=True,
        cwd=invocation["cwd"],
    )


def test_one_plan_is_accepted_by_all_six_protocol_loaders(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = create_production_shaped_v4_fixture(tmp_path)
    monkeypatch.chdir(fixture.report)
    plan = _load(fixture.plan)
    role9_request, role9_artifact, role9_receipt = _materialize_peer_request(fixture, plan, 9)
    role10_request, role10_artifact, role10_receipt = _materialize_peer_request(fixture, plan, 10)

    role8_producer = load_isolated_module(fixture.producer, "shared_plan_role8_producer")
    role8_verifier = load_isolated_module(fixture.verifier, "shared_plan_role8_verifier")
    role8_producer._load_request(fixture.request, fixture.output, checking=True)
    role8_verifier._load_request(fixture.request, fixture.output)

    role9_entry = plan["entries"][1]
    role9_producer_path = Path(role9_entry["implementation_runtime_closure"]["producer"]["path"])
    role9_producer = load_isolated_module(role9_producer_path, "shared_plan_role9_producer")
    role9_producer._load_request(role9_request, role9_artifact)

    role10_entry = plan["entries"][2]
    for invocation_role in ("producer", "verifier"):
        completed = _run_invocation(role10_entry["invocations"][invocation_role])
        assert completed.returncode == 2, (completed.stdout, completed.stderr)
        assert completed.stdout == ""
        assert completed.stderr.strip() == NUMERICAL_HOLD

    role9_produced = _run_invocation(role9_entry["invocations"]["producer"])
    assert role9_produced.returncode == 0, (
        role9_produced.stdout,
        role9_produced.stderr,
    )
    role9_verified = _run_invocation(role9_entry["invocations"]["verifier"])
    assert role9_verified.returncode == 0, (
        role9_verified.stdout,
        role9_verified.stderr,
    )

    assert not fixture.output.exists()
    assert not fixture.receipt.exists()
    assert role9_artifact.is_file()
    assert role9_receipt.is_file()
    assert not role10_artifact.exists()
    assert not role10_receipt.exists()
