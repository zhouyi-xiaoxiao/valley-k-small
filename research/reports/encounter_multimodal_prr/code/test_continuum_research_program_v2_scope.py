from __future__ import annotations

import hashlib
from pathlib import Path

REPORT = Path(__file__).resolve().parents[1]
PROGRAM = REPORT / "notes/continuum_research_program_v2.md"
SUPPLEMENT = REPORT / "manuscript/encounter_multimodal_prr_supplement.tex"
PROGRAM_SHA256 = "c639dc2b6fbe636c1f24340ea2ea96003487b3613bdd616399c3cd7cb984284c"
ROUND167_AUDIT = REPORT / "audits/round_167_production_initial_stream_clean_replay_and_continuum_erratum.md"


def test_continuum_v2_historical_round167_bytes_remain_auditable() -> None:
    assert PROGRAM_SHA256 in ROUND167_AUDIT.read_text(encoding="utf-8")
    assert hashlib.sha256(PROGRAM.read_bytes()).hexdigest() != PROGRAM_SHA256


def test_continuum_v2_is_a_hold_program_not_a_result() -> None:
    text = PROGRAM.read_text(encoding="utf-8")
    compact = " ".join(text.split()).lower()

    assert "hold-continuum-claim" in compact
    assert "no positive-budget execution" in compact
    assert "strict-continuum scientific sentence" in compact
    assert "fixed-l mosco/strong-resolvent theorem = open c1" in compact
    assert "computable positive-time c2 spatial error = open c2" in compact
    assert "first/second derivative box truncation = open c3" in compact
    assert "broad-family continuum stationary signature = hold" in compact
    assert "positive-b/f1 execution = not performed / not authorized" in compact


def test_continuum_v2_keeps_the_dangerous_box_derivative_bridge_open() -> None:
    text = PROGRAM.read_text(encoding="utf-8")
    compact = " ".join(text.split()).lower()

    assert "formula (6.4) is not a bound for the first or second time derivative" in compact
    assert "positive-time truncation lemma" in compact
    assert "exit probability reused as a derivative bound without proof" in compact
    assert "e_{{\\rm box},r}(l;\\tau,t),\\qquad r=0,1,2" in compact


def test_continuum_v2_retains_componentwise_root_transfer() -> None:
    text = PROGRAM.read_text(encoding="utf-8")
    compact = " ".join(text.split()).lower()

    assert "three physical unit bounds" in compact
    assert "\\varepsilon_1<\\min\\{\\eta_*,\\zeta_*\\}" in compact
    assert "\\varepsilon_2<\\kappa_*" in compact
    assert "no additional stationary point exists" in compact
    assert "basin probabilities and survival require their own" in compact


def test_continuum_v2_closes_the_model_and_identification_hypotheses() -> None:
    text = PROGRAM.read_text(encoding="utf-8")
    compact = " ".join(text.split()).lower()

    assert "d>0,\\qquad \\gamma>0,\\qquad w>0" in compact
    assert "w_j^{(c)}\\ge0,\\qquad \\sum_jw_j^{(c)}=1" in compact
    assert "q_0\\ge0" in compact
    assert "\\int_{\\omega_\\infty}q_0\\,dx=1" in compact
    assert "\\|p_hj_hv_h-v_h\\|_{h_h}" in compact
    assert "moving-pairing condition" in compact
    assert "finite time net" in compact
    assert "f_{r,t}(\\lambda)=\\lambda^r e^{-t\\lambda}" in compact


def test_continuum_v2_proves_only_the_natural_decay_c0a_sublemma() -> None:
    text = PROGRAM.read_text(encoding="utf-8")
    compact = " ".join(text.split()).lower()
    supplement = " ".join(SUPPLEMENT.read_text(encoding="utf-8").split()).lower()

    assert "proposition c0-a (proved operator-realization sublemma)" in compact
    assert "z=\\frac{2\\pi d w}{\\gamma}" in compact
    assert "\\mathbf d\\nabla\\log\\pi=b" in compact
    assert "c_r(\\tau)=\\left(\\frac{r}{e\\tau}\\right)^r" in compact
    assert "+b\\int_0^tf_{\\infty,c}(s)\\,ds=1" in compact
    assert "natural-decay c0-a form/semigroup sublemma = proved" in compact
    assert "form-associated natural-decay realization" in compact
    assert "no separate essential-self-adjointness claim" in compact
    assert "does **not** freeze the concrete model bytes" in compact
    assert "concrete hash-bound c0 model contract = open" in compact
    assert "fixed-l mosco/strong-resolvent theorem = open c1" in compact

    assert r"\label{cor:physical-natural-decay}" in supplement
    assert r"\label{eq:physical-spectral-bound}" in supplement
    assert r"\label{eq:physical-integrated-mass}" in supplement
    assert "form-associated realization" in supplement
    assert "no separate essential-self-adjointness assertion" in supplement
    assert "does not prove finite-volume mosco convergence" in supplement


def test_continuum_v2_ou_margins_and_units_fail_closed() -> None:
    text = PROGRAM.read_text(encoding="utf-8")
    compact = " ".join(text.split()).lower()

    assert "[f]=l^{-2}" in compact
    assert "[\\partial_t^rf]=l^{-2}t^{-r}" in compact
    assert "r_x>r_{0,x}" in compact
    assert "m_{x,-}>0" in compact
    assert "m_{x,+}>0" in compact
    assert "define `delta_x^asym=1`" in compact
    assert "a nonpositive margin is never squared" in compact


def test_continuum_v2_root_displacement_uses_the_continuum_floor() -> None:
    text = PROGRAM.read_text(encoding="utf-8")
    compact = " ".join(text.split()).lower()

    assert "canonical half-open serialization" in compact
    assert "\\kappa_*-\\varepsilon_2" in compact
    assert "\\frac{\\varepsilon_1+\\rho_h}{\\kappa_*-\\varepsilon_2}" in compact
    assert "concrete hash-bound c0 model contract = open" in compact


def test_continuum_v2_does_not_embed_historical_or_prospective_values() -> None:
    text = PROGRAM.read_text(encoding="utf-8")

    assert "B=0.01" not in text
    assert "B=0.6" not in text
    assert "No positive-`B` propagation is needed" in text
    assert "This note does not record their values" in text
