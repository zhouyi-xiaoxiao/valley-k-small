from __future__ import annotations

import re
from pathlib import Path

REPORT = Path(__file__).resolve().parents[1]


def _read(relative: str) -> str:
    return (REPORT / relative).read_bytes().decode("utf-8")


def _flat(source: str) -> str:
    return " ".join(source.split())


def _between(source: str, start: str, end: str) -> str:
    assert start in source
    tail = source.split(start, 1)[1]
    assert end in tail
    return tail.split(end, 1)[0]


def test_theorem_first_headline_matches_the_proved_support_design() -> None:
    main = _read("manuscript/encounter_multimodal_prr_theorem_first_working.tex")
    abstract = _flat(_between(main, r"\begin{abstract}", r"\end{abstract}"))

    assert (
        r"\title{Prescribed finite-window reaction-time modality by "
        "conserved-budget support design}"
    ) in main
    assert r"$w_j\ge w_*>0$" in abstract
    assert "$m$-dependent support design" in abstract
    assert "asymptotically saturated on the design window" in abstract
    assert "no useful budget threshold, event-mass floor" in abstract
    assert "allocation-control realization is therefore a separate numerical question" in abstract
    assert "Redistributing a fixed amount" not in abstract

    introduction = _flat(_between(main, r"\section{Introduction}", r"\section{Conserved"))
    assert "same alternating signature" in introduction
    assert "not a proof that one fixed support family selects different mode counts" in introduction
    assert "We do not claim that upper bound as new" in introduction


def test_physics_text_excludes_internal_pipeline_jargon() -> None:
    main = _read("manuscript/encounter_multimodal_prr_theorem_first_working.tex")
    for forbidden in (
        "selector bytes",
        "F0 objects",
        "deterministic F1",
        "F2/F3",
        "strict native array ownership",
        "verifier-owned replay",
    ):
        assert forbidden not in main
    assert "implementation-level provenance and memory-isolation controls" in main
    assert "belong to the reproducibility record rather than to the physical claim" in _flat(main)


def test_supplement_separates_the_general_lower_bound_from_exact_topology() -> None:
    supplement = _read("manuscript/encounter_multimodal_prr_supplement.tex")
    assert supplement.count(r"\input{exact_m_theorem_full_proof.tex}") == 1
    assert "Section S4 retains an earlier, more general" in supplement
    assert "time-varying-variance construction" in supplement
    assert r"Section S5 gives the complete exact-\(m\) proof" in supplement
    assert "stationary-midpoint, common-variance" in supplement
    assert "whole-window contact-interior" in supplement
    assert "not same-support mode-count" in supplement
    assert (
        "complete reader-facing proof; frozen mathematical migration passed Round~149"
        in supplement
    )
    assert "finite-parameter F0--F3 evidence" in supplement
    assert "hash-specific independent mathematical audit" not in supplement
    assert "technical proof accepted; migration open" not in supplement


def test_reader_proof_contains_every_exact_m_boundary() -> None:
    proof = _read("manuscript/exact_m_theorem_full_proof.tex")
    flattened = _flat(proof)
    controls = re.findall(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", proof)
    assert not controls

    required_tokens = (
        r"\operatorname{Var}Z_t=\varepsilon^2\frac{D_0}{2\gamma}",
        r"\sup_{t\in I}|r_*(t)|_{\rm mi}\le a-\eta",
        r"\begin{lemma}[Global extended-Chebyshev zero bound]",
        r"\begin{lemma}[Uniform adjacent isolation]",
        r"\begin{theorem}[Exact topology of the pure mixture]",
        r"\begin{lemma}[Posterior-sector certificate]",
        r"\begin{theorem}[Slow positive factors preserve the exact topology]",
        r"\begin{theorem}[Exact \(m\) Doi modes for fixed finite \((d,m)\)]",
        r"\|\mathcal F_{B,\varepsilon,w}-G_{\varepsilon,w}\|_{C^2(I)}",
        "There is no asserted lower bound",
        r"does not count stationary points outside \(I\)",
        "gives no process-level event-mass floor",
        "asymptotically saturated on the theorem window",
        "not arbitrary localized catalyst patches",
    )
    for token in required_tokens:
        assert token in proof

    ordered = (
        "Global extended-Chebyshev zero bound",
        "Uniform adjacent isolation",
        "Exact topology of the pure mixture",
        "Posterior-sector certificate",
        "Slow positive factors preserve the exact topology",
        r"Exact \(m\) Doi modes",
        "Quantifiers, saturation, and scope",
    )
    positions = [proof.index(token) for token in ordered]
    assert positions == sorted(positions)
    assert "one first fixes a sufficiently small" not in flattened


def test_theorem_first_package_does_not_promote_lean_or_numerical_science() -> None:
    package = "\n".join(
        (
            _read("manuscript/encounter_multimodal_prr_theorem_first_working.tex"),
            _read("manuscript/encounter_multimodal_prr_supplement.tex"),
            _read("manuscript/exact_m_theorem_full_proof.tex"),
        )
    )
    flattened = _flat(package)
    assert "not Lean-verified" in package
    assert "positive-budget values have not been evaluated or read" in flattened
    assert "continuum-consistent numerical evidence" not in package
    assert "continuum verified" not in package.lower()
    assert "release_eligible=true" not in package


def test_classical_gaussian_mode_bound_is_credited_not_claimed() -> None:
    main = _read("manuscript/encounter_multimodal_prr_theorem_first_working.tex")
    proof = _read("manuscript/exact_m_theorem_full_proof.tex")
    bibliography = _read("manuscript/references.bib")
    for key in (
        "carreiraPerpinanWilliams2003modes",
        "amendolaEngstromHaase2020modes",
    ):
        assert key in main
        assert key in proof
        assert f"{{{key}," in bibliography
    assert "The mode cap for univariate Gaussian mixtures is classical" in proof
