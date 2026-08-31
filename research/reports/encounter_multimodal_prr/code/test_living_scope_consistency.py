from __future__ import annotations

from pathlib import Path

REPORT = Path(__file__).resolve().parents[1]


def _read(relative: str) -> str:
    return (REPORT / relative).read_text(encoding="utf-8")


def _flat(source: str) -> str:
    return " ".join(source.split())


def test_living_documents_agree_on_the_terminal_cusp_and_active_route() -> None:
    documents = {
        "README": _read("README.md"),
        "contract": _read("notes/research_contract.md"),
        "theorem program": _read("notes/theorem_program.md"),
        "rewrite blueprint": _read("notes/prr_focused_spine_rewrite_blueprint.md"),
    }

    for label, source in documents.items():
        assert "B=0.01" in source, f"{label} lost the fixed positive-budget value"
        assert "allocation-v6" in source.lower(), f"{label} lost the terminal cusp branch"
        assert "terminal" in source.lower(), f"{label} no longer marks allocation-v6 terminal"
        assert "one-/two-/three" in source.lower(), f"{label} lost the active fixed-control route"
        assert "off-lattice" in source.lower(), f"{label} lost the independent event-law route"
        assert "independent" in source.lower(), f"{label} lost the independent-method boundary"

    assert "ACCEPT-THEOREM-SPINE" in documents["README"]
    assert "Rounds 118 and 120" in documents["contract"]
    assert "Rounds 118 and 120" in documents["theorem program"]
    assert "Rounds 118 and 120" in documents["rewrite blueprint"]

    assert "N=113,129" in documents["contract"]
    assert "N=113,129" in documents["theorem program"]
    assert "one fixed box" in documents["contract"]
    assert "one box and one solver family" in _flat(documents["theorem program"])
    stale_claims = (
        "None of these results supplies positive-budget three-mode event mass",
        "does not prejudge the pending positive-`B` calculation",
        "Wait for the positive-`B` result and its independent numerical audit",
        "do not substitute for an allocation cusp with both folds",
        "decisive remaining PRR gates are the positive-budget allocation cusp",
        "allocation cusp, convergence, and independent-solver gates.",
        "exact-`m` complete-topology theorem is on `HOLD`",
        "exact-`m` proof repair (or an explicitly weaker theorem claim)",
        "stronger exact-$m$ theorem candidate is `HOLD`",
        "Finish and independently accept the exact-`m` repair",
    )
    for stale in stale_claims:
        assert all(stale not in source for source in documents.values())

    literature = _read("notes/literature_gap_20260713.md")
    literature_flat = _flat(literature)
    assert "terminal allocation-v6" in literature
    assert "exact-`m`" in literature
    assert "Rounds 118 and 120" in literature
    assert "one-/two-/three-mode" in literature
    assert "off-lattice event-law" in literature
    assert "a numerical cusp is no longer a conjunct" in literature
    assert "Positive-budget physical `d=3`" in literature
    assert "neither is required for this focused route" in literature_flat
    for stale in (
        "only if Chain C is completed",
        "one certified continuum fold and one well-conditioned continuum cusp",
        "an independent physical 3D realization demonstrating the same organizing principle",
        "dynamics in both physical dimensions two and three",
    ):
        assert stale not in literature


def test_main_manuscript_keeps_the_fixed_point_out_of_cusp_and_continuum_scope() -> None:
    source = _read("manuscript/encounter_multimodal_prr.tex")
    flattened = _flat(source)
    assert "Internal Physical Review Research working draft -- NOT FOR SUBMISSION" in source
    assert r"\input{inputs/positive_b_results.tex}" in source
    assert r"\subsection{A fixed positive-budget multimodal point}" in source
    assert "one control cannot establish a cusp" in flattened
    assert "two odd meshes in one box cannot establish an unbounded or continuum limit" in flattened
    assert "not an interval-global result, allocation cusp, or continuum limit" in flattened
    assert r"saved root screen $t\leq35$" in flattened
    assert "tail checks extend through $t=100$" in flattened
    assert "does not exclude additional extrema after $t=35$" in flattened
    assert "PASS: FIXED CONTROL/TWO MESHES ONLY" in source
    assert "positive-$B$ four-slab cusp" in source
    assert "NOT RUN" in source


def test_current_theory_selector_and_f0_boundaries_are_synchronized() -> None:
    documents = {
        "README": _read("README.md"),
        "contract": _read("notes/research_contract.md"),
        "theorem program": _read("notes/theorem_program.md"),
        "continuum path": _read("notes/continuum_next_stage_path.md"),
    }
    for label, source in documents.items():
        flattened = _flat(source)
        assert "Round 149" in flattened or "Round-149" in flattened, (
            f"{label} lost the accepted theorem-first proof boundary"
        )
        assert "Round 154" in flattened or "Round-154" in flattened, (
            f"{label} lost the packed-action repair boundary"
        )
        assert "Round 155" in flattened or "Round-155" in flattened, (
            f"{label} lost the independent packed-action re-audit"
        )
        assert "bounded implementation primitive" in flattened, (
            f"{label} promoted the packed action beyond its accepted role"
        )
        assert "F0" in flattened and any(
            token in flattened
            for token in (
                "F0 therefore remains open",
                "F0 (currently open)",
                "open F0",
                "F0, and all 36 F1 rows remain open",
            )
        ), f"{label} lost the open F0 boundary"
        for stale in (
            "blocked post-Round-152",
            "BLOCKED ON STAGE-1 VALIDATOR REPAIR AND RE-AUDIT",
            "Round 152 rejects its current bytes",
        ):
            assert stale not in flattened, f"{label} retained stale F0 status: {stale}"

    design = _read("notes/f0_rate_interval_composition_next_stage.md")
    design_flat = _flat(design)
    assert "ROUND-155 PRECONDITION CLEARED / HOLD F0" in design
    assert "do not authorize F0" in design
    assert "authentication or as a fresh verifier" in design
    assert "reconstruct the kernel and state" in design_flat
    assert "inside a fresh process" in design_flat
    assert "same-process producer API" in design_flat
    assert "explicitly non-authoritative" in design_flat
    assert "initial-state receipt" in design_flat
    assert "immediately preceding accepted rate-action receipt" in design_flat
    assert "cannot prove that the incoming uncertainty was not understated" in design_flat
    assert "point_lift_binding_sha256" in design
    assert "lift[i, 0] == lift[i, 1] == canonicalize_zero(c[i])" in design
    assert "both endpoint sign bits must be false" in design_flat
    assert "a `-0.0` source endpoint is a fail-closed mutation" in design_flat
    assert "Nominal inputs containing either sign of zero" in design_flat
    assert "raw `16N`" in design_flat
    assert "array copy may not disappear from the ledger" in design_flat
    assert "40N + max(81C, 2C, 2048)" in design
    assert "48N + 65C" in design
    assert "farthest-point" in design_flat
    assert "ordinary distance from `d` to the set `Y`" in design_flat
    assert "unsafely erase the centre-action roundoff" in design_flat
    assert "blocked post-Round-152" not in design
    assert "BLOCKED ON STAGE-1 VALIDATOR REPAIR AND RE-AUDIT" not in design

    checklist = _read("manuscript/SUBMISSION_METADATA_REQUIRED.md")
    assert "- [x] Theory package" in checklist
    assert "Round-149 mathematical audit" in checklist
    assert "- [x] Common observables" in checklist
    assert "- [ ] F0" in checklist
    assert "- [ ] F1" in checklist
    assert "- [ ] F2/F3" in checklist
    assert "PRR submission claim" in checklist
    assert "remain\nprohibited" in checklist
