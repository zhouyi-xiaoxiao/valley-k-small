from __future__ import annotations

import hashlib
from pathlib import Path

REPORT = Path(__file__).resolve().parents[1]

ROUND164_SHA256 = {
    "code/rate_defined_tensor_f0_packed_target_uniformization.py": (
        "5acd20fc227defc7573f4a54b2ab543f192719b3bd7be65de5620c2ef4491323"
    ),
    "code/test_rate_defined_tensor_f0_packed_target_uniformization.py": (
        "72d50b1a1fe711ef95b451238050ccea3f291f7dca98a779ca3887b3380e5878"
    ),
    "code/rate_defined_tensor_f0_tiny_semantic_replay.py": (
        "df22f3882c2457de8e1ee3428c70679220148d6f43ad725b21fe49230ed3de3f"
    ),
    "code/test_rate_defined_tensor_f0_tiny_semantic_replay.py": (
        "47dadfbfbf2138830f803b65dd18ca55287aeb7a7c8123c986720b07419ddc3c"
    ),
    "code/rate_defined_tensor_f0_packed_tiny_jets.py": (
        "b3fc573bb17c3201019665433fb06121001e1b05810fa524e808909427dcf1b1"
    ),
    "code/test_rate_defined_tensor_f0_packed_tiny_jets.py": (
        "c8c2e040abbd0731e27e2f18ce8e3b0a6af4a95e965a32b08d0a8133af83b670"
    ),
    "audits/round_164_target_uniformization_semantic_replay_tiny_jets_independent_review.md": (
        "0c46acd88112568ea546b8b9210d90f4cb5e297da70089849e488775e08487b7"
    ),
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_round164_final_reviewed_bytes_are_frozen() -> None:
    for relative, expected in ROUND164_SHA256.items():
        assert _sha256(REPORT / relative) == expected, relative


def test_round164_accepts_only_the_tiny_method_scope() -> None:
    audit = (
        REPORT
        / "audits/round_164_target_uniformization_semantic_replay_tiny_jets_independent_review.md"
    ).read_text(encoding="utf-8")
    compact = " ".join(audit.split()).lower()
    for phrase in (
        "p0 = 0 / p1 = 0 / p2 = 0",
        "physical or analytic source -> component box = open",
        "clean serialized whole-result replay = open",
        "fresh-process independent implementation = open",
        "full-window interval topology = open",
        "7,165,305-state production resource gate = open",
        "f0 = hold",
        "f1 / positive-budget campaign = not authorized / not run",
        "prr release = hold",
    ):
        assert phrase in compact


def test_round164_does_not_overstate_the_parameter_stress_grid() -> None:
    audit = (
        REPORT
        / "audits/round_164_target_uniformization_semantic_replay_tiny_jets_independent_review.md"
    ).read_text(encoding="utf-8")
    compact = " ".join(audit.split()).lower()
    assert "stress grid, not an exhaustive proof for the continuous rate box" in compact
    assert "full-box enclosure comes from the operator-norm recurrence" in compact
