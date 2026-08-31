from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

REPORT = Path(__file__).resolve().parents[1]

THEORY_SURFACE_PATHS = {
    "main": "manuscript/encounter_multimodal_prr.tex",
    "supplement": "manuscript/encounter_multimodal_prr_supplement.tex",
    "direct note": "notes/direct_physical_multimode_theorem.md",
    "mixed-jet note": "notes/pde_mixed_jet_theorem.md",
    "README": "README.md",
    "contract": "notes/research_contract.md",
    "theorem program": "notes/theorem_program.md",
    "rewrite blueprint": "notes/prr_focused_spine_rewrite_blueprint.md",
}
CLAIM_SURFACE_PATHS = {
    **THEORY_SURFACE_PATHS,
    "generated numerical input": "manuscript/inputs/numerical_results.tex",
    "generated positive-B input": "manuscript/inputs/positive_b_results.tex",
}
# Round 167 is the living successor freeze.  The replaced pre-Round-167 hashes
# and the reason for each byte change remain preserved in that immutable audit;
# mathematical-core sources that did not need the production-boundary update
# retain their earlier hashes here.
CLAIM_SURFACE_SHA256 = {
    "main": "1c17be4ac1223fa769166cc13c4b551a1cf7925ae59a61a81021657421305c5b",
    "supplement": "b8182df7e269a90c81e504121db99ae0867c7c5cab8e093be3d32e6a86a58b86",
    "direct note": "2b35d1b1053045220b29975d30f8b3c842d33273ca46de86b8cf7798c26a9c3d",
    "mixed-jet note": "ac0e6cbb34d446d2b9ae2b52c22684ee72da7cadb04d864aacba085dff75f095",
    "README": "2a318c9b17df74b8f6709697bcddb044f71e8979eaea00cd1d6949f758748572",
    "contract": "9dc8f028ebc97bf81f5d0a9e775e246ecddce838abd4d0fc0029f45fdeeec697",
    "theorem program": "0c382f8018174cbf46f1ae4bab53fa08af0cf9b8da2c817b8f634ccbcbe67b92",
    # Post-Round-167 living candidate; exact-frozen here pending the next
    # independent whole-surface audit rather than mislabelled as Round-167.
    "rewrite blueprint": "72573b26564db93d0b64e8dbdb5a62932c059615385af6b2911b908948235661",
    "generated numerical input": (
        "62fe4306fc1bfa6a75757031ba23de38f9fabe490ac7be8c0b05e14c543a1530"
    ),
    "generated positive-B input": (
        "2eb08d12a5585afa17b8bedfb3d79232a25e328a30439cb0cb0678b13631fabf"
    ),
}
ROUND167_LIVING_SUCCESSORS = {
    "README",
    "contract",
}
LIVING_SUCCESSOR_SHA256 = {
    "README": "c7d09b8e9d195bae22492875c5e35666f5a8b1c5dc26e221329a0c83fdbd0270",
    "contract": "2753e3d315a808e08a912f5813488be44e3f8b64e5d543e9956fd48c913d6446",
}
ROUND167_AUDIT = REPORT / "audits/round_167_production_initial_stream_clean_replay_and_continuum_erratum.md"


def _read(relative: str) -> str:
    # read_bytes avoids universal-newline normalization: this is an exact-byte
    # claim-surface freeze, not a best-effort semantic classifier.
    return (REPORT / relative).read_bytes().decode("utf-8")


def _flat(source: str) -> str:
    return " ".join(source.split())


def _claim_surfaces() -> dict[str, str]:
    return {label: _read(path) for label, path in CLAIM_SURFACE_PATHS.items()}


def _assert_claim_surface_freeze(sources: dict[str, str]) -> None:
    """Freeze Round-167 bytes or retain superseded living hashes in its audit."""
    assert set(sources) == set(CLAIM_SURFACE_SHA256)
    audit = ROUND167_AUDIT.read_text(encoding="utf-8")
    for label, expected in CLAIM_SURFACE_SHA256.items():
        observed = hashlib.sha256(sources[label].encode("utf-8")).hexdigest()
        if label in ROUND167_LIVING_SUCCESSORS:
            assert expected in audit, f"{label} lost its Round-167 historical hash"
            assert observed == LIVING_SUCCESSOR_SHA256[label], (
                f"{label} left the current candidate exact-byte claim surface"
            )
        else:
            assert observed == expected, (
                f"{label} left the independently reviewed exact-byte claim surface"
            )


def _between(source: str, start: str, end: str) -> str:
    assert start in source
    tail = source.split(start, 1)[1]
    assert end in tail
    return tail.split(end, 1)[0]


def _assert_main_general_dimension_contract(source: str) -> None:
    theorem = _flat(
        _between(
            source,
            r"\subsection{Direct fixed-finite-mode theorem",
            r"\paragraph{Boundary of the reduced analogy.}",
        )
    )
    lowered = theorem.lower()
    assert "disk or sphere" not in lowered
    assert "embedded minimum-image $d$-ball" in theorem
    assert r"$\sup_{t\in I_*}|r_*(t)|_{\mathrm{mi}}\le a-\eta$" in theorem
    assert r"$[B]=L^dT^{-1}$" in theorem
    assert r"\frac{B}{W^{d-1}}" in theorem
    assert r"first fix a sufficiently small $\epsilon$, then take $B<B_0(\epsilon)$" in theorem
    assert (
        "No constant, dimensional budget, value of $B_0$, amplitude, or "
        "event mass is uniform or compared across dimensions"
    ) in theorem
    assert r"no $d\to\infty$ limit is claimed" in theorem


def _assert_core_negative_dimension_contracts(
    main: str,
    supplement: str,
    direct: str,
    mixed: str,
) -> None:
    main_flat = _flat(main)
    supplement_flat = _flat(supplement)
    direct_flat = _flat(direct)
    mixed_flat = _flat(mixed)

    _assert_main_general_dimension_contract(main)
    assert (
        "dimensional budgets cannot be compared across dimensions by assigning "
        "them the same numerical value"
    ) in supplement_flat
    assert (
        "No constant, dimensional budget, amplitude, event mass, or value of "
        r"\(B_0\) is uniform or compared across dimensions"
    ) in supplement_flat
    assert (
        "equal numerical values of this dimensional budget are not compared across dimensions"
    ) in direct_flat
    assert (
        r"its constants, dimensional budget, amplitudes, event masses, and \(B_0\) "
        "are not uniform or compared across dimensions"
    ) in direct_flat
    assert (
        "the theorem makes no cross-dimensional comparison at a common numerical "
        "value of this dimensional budget"
    ) in mixed_flat
    assert r"It is pointwise, not uniform, in \(d\)" in mixed_flat
    assert "No constant, dimensional budget" in main_flat


def test_authoritative_theory_sources_state_the_fixed_dimension_quantifier() -> None:
    sources = {label: _read(path) for label, path in THEORY_SURFACE_PATHS.items()}
    _assert_claim_surface_freeze(_claim_surfaces())

    stale_theory_phrases = (
        "the theorem is proved only for $d=2,3$",
        "physical dimensions beyond \\(d=2,3\\)",
        "direct physical $d=2,3$ fixed-finite-$m$ theorem",
        "fixed-finite-`m`/`d=2,3` theorem scope",
        "exact physical `d=2,3` Doi quotient after sequential limits",
        "current Doi transfer is claimed only for physical \\(d=2,3\\)",
    )
    for label, source in sources.items():
        lowered = source.lower()
        assert "fixed finite" in lowered, f"{label} lost the fixed-finite scope"
        assert any(token in source for token in ("d\\ge2", "d>=2")), (
            f"{label} lost the d>=2 outer scope"
        )
        for stale in stale_theory_phrases:
            assert stale not in lowered, f"{label} retained stale theory phrase: {stale}"


def test_dimension_extension_retains_nonuniformity_and_geometry_boundaries() -> None:
    main_source = _read("manuscript/encounter_multimodal_prr.tex")
    supplement_source = _read("manuscript/encounter_multimodal_prr_supplement.tex")
    direct_source = _read("notes/direct_physical_multimode_theorem.md")
    mixed_source = _read("notes/pde_mixed_jet_theorem.md")
    main = _flat(main_source)
    supplement = _flat(supplement_source)
    direct = _flat(direct_source)
    mixed = _flat(mixed_source)

    _assert_core_negative_dimension_contracts(
        main_source,
        supplement_source,
        direct_source,
        mixed_source,
    )

    for label, source in {
        "main": main,
        "supplement": supplement,
        "direct note": direct,
        "mixed-jet note": mixed,
    }.items():
        assert "uniform" in source.lower(), f"{label} lost nonuniformity boundary"
        assert "localized" in source.lower(), f"{label} lost slab/localized boundary"

    assert "$d\\to\\infty$" in main
    assert "\\(d\\to\\infty\\)" in supplement
    assert "\\(d\\to\\infty\\)" in direct
    assert "\\(d\\to\\infty\\)" in mixed
    assert "lattice" in main.lower()
    assert "lattice" in supplement.lower()
    assert "lattice" in direct.lower()
    assert "no single chart" in direct.lower()

    for label, source in {
        "main": main,
        "supplement": supplement,
        "direct note": direct,
        "mixed-jet note": mixed,
    }.items():
        assert "[B]=L^dT^{-1}" in source, f"{label} lost the dimensional B unit"

    assert "embedded minimum-image \\(d\\)-ball" in supplement
    assert "every Euclidean lift" in supplement
    assert "summing the images" in supplement
    assert "W^{-(d-1)}" in supplement
    assert "diagonal-haar-quotient" in supplement

    quantifier_block = _between(
        _read("manuscript/encounter_multimodal_prr_supplement.tex"),
        r"\boxed{",
        r"\label{eq:nested-quantifiers}",
    )
    ordered_tokens = (
        r"\exists\epsilon_0",
        r"\forall\epsilon\in(0,\epsilon_0)",
        r"\exists B_0",
        r"\forall B\in(0,B_0)",
    )
    positions = [quantifier_block.index(token) for token in ordered_tokens]
    assert positions == sorted(positions)


def test_general_dimension_contract_rejects_scope_mutations() -> None:
    source = _read("manuscript/encounter_multimodal_prr.tex")
    mutations = (
        (
            "embedded minimum-image $d$-ball",
            "true disk or sphere of contact",
        ),
        (
            r"$\sup_{t\in I_*}|r_*(t)|_{\mathrm{mi}}\le a-\eta$",
            r"$|r_*(t)|<a$ near the targets",
        ),
        (
            r"sufficiently small $\epsilon$, then take $B<B_0(\epsilon)$",
            r"take $B$ and $\epsilon$ small together",
        ),
        (r"$[B]=L^dT^{-1}$", "a dimensional budget $B$"),
    )
    for old, new in mutations:
        assert old in source
        with pytest.raises(AssertionError):
            _assert_main_general_dimension_contract(source.replace(old, new, 1))

    supplement = _read("manuscript/encounter_multimodal_prr_supplement.tex")
    direct = _read("notes/direct_physical_multimode_theorem.md")
    mixed = _read("notes/pde_mixed_jet_theorem.md")
    direct_old = "are not uniform or compared across dimensions"
    assert direct_old in direct
    with pytest.raises(AssertionError):
        _assert_core_negative_dimension_contracts(
            source,
            supplement,
            direct.replace(direct_old, "are uniform and compared across dimensions", 1),
            mixed,
        )

    mixed_old = (
        "the theorem makes no\n"
        "cross-dimensional comparison at a common numerical value of this dimensional\n"
        "budget"
    )
    assert mixed_old in mixed
    with pytest.raises(AssertionError):
        _assert_core_negative_dimension_contracts(
            source,
            supplement,
            direct,
            mixed.replace(
                mixed_old,
                "the theorem compares dimensions at one common numerical budget",
                1,
            ),
        )


def test_exact_byte_freeze_rejects_every_claim_surface_mutation() -> None:
    sources = _claim_surfaces()
    _assert_claim_surface_freeze(sources)
    for label, source in sources.items():
        for mutation in (source + " ", source + "\u200b", source + "\r"):
            changed = dict(sources)
            changed[label] = mutation
            with pytest.raises(AssertionError):
                _assert_claim_surface_freeze(changed)


def test_numerical_dimension_claims_are_not_promoted_by_the_theorem() -> None:
    living_sources = {label: _read(path) for label, path in THEORY_SURFACE_PATHS.items()}
    _assert_claim_surface_freeze(_claim_surfaces())

    main = _flat(living_sources["main"])
    contract = _flat(living_sources["contract"])
    blueprint = _flat(living_sources["rewrite blueprint"])

    assert "positive-$B$ physical-$d=3$ evidence is also required" in main
    assert "positive-budget physical-`d=3` result" in contract
    assert "finite-budget `d=3` modality" in blueprint
    assert "one allocation robust across dimensions" in blueprint.lower()
