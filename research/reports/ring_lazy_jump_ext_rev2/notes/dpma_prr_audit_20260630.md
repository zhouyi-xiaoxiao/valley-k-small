# Triangulated PRR-readiness audit (whole package) — 2026-06-30

Run with the reusable `triangulated-audit` skill (TANA): Claude dynamic fan-out +
ChatGPT gpt-5-5-pro PRR-referee + numerical arbiter. Target = the complete DPMA package
as a Physical Review Research submission candidate (acceptance-focused, not just correctness).

## Reconciled verdict
**Math core bulletproof; one real over-claim found AND FIXED; the remaining PRR gap is
significance/universality, not correctness.** Both brains agree the work is real and the
self-assessment is honest; they found *different* gaps (complementary):
- Claude (repo access) caught a **technical over-claim** (general-θ master *curve* not actually
  assembled — node modes skipped). FIXED below.
- ChatGPT Pro (no repo, high-context) caught the **significance/universality** gap for PRR.

## Claude fan-out (5 findings, all confirmed; independent reimplementation, not via repo scripts)
1. **b_c saddle-node — CONFIRMED, STRENGTHENED.** Reproduced from scratch: double root
   Φ'(τ_c)=Φ''(τ_c)=0 at b_c=3.076432, x_c=0.038363; **normal-form scaling gap∼(b_c−b)^0.50,
   prominence∼(b_c−b)^1.50** (textbook fold, not a crossover); signed amplitudes (~100±/100∓)
   refute pro's "completely monotone" objection at its root; exact chain N=200/400/800
   N-independent. → added the scaling exponents to `code/dpma_saddle_node_certification.py`.
2. **General-θ master CURVE — was OVER-CLAIMED (major), now FIXED.** The committed
   `dpma_general_u_master_amplitudes.py` verified only AFFECTED-mode amplitudes (skips
   sin(2θw)=0 node modes). Node modes carry ~33% weight at θ=1/3; affected-only curve is
   wrong by 83% @τ=0.01. **FIX delivered (not downgraded):** node-mode amplitude
   `G_n^node = nπ[1−(−1)ⁿ]sin(nπξ)` (unperturbed Dirichlet residue) added; full curve
   (affected + node) now reproduces exact (N²/q)F to **rel-err ~1e-5 @N=1200, O(1/N)** across
   τ∈[0.01,0.2], θ=1/3, 2/5, 1/2. New: `code/dpma_general_u_master_curve.py`.
3. Law 1 channel-mass — CONFIRMED exact (splitting probability; ~1e-14 over 1225 configs).
4. Law 3 q-reduction — CONFIRMED exact (roots q-invariant ~1e-15; pro's "REFUTED" over-claimed).
5. Honesty self-assessment — CONFIRMED high/calibrated (records the stronger model overruled
   twice; demotes classifier quantities; self-downgraded an unbacked 3.5e-6 to measured 2.1e-4).
   Caught: §八 "two technical blockers cleared, rest is framing" was PREMATURE (b_c was cleared,
   G was not) — now BOTH are cleared after fix #2.

## ChatGPT gpt-5-5-pro PRR-referee — VERDICT: MAJOR REVISION (borderline PRR / JPA-downgrade risk)
- **Significance (borderline PRR):** the strong, rare hook = a saddle-node birth of a second peak
  in an OBSERVABLE (time-domain FPT density), not spectral/asymptotic; from a minimal rank-one
  **non-Hermitian** directed defect. PRR-strong ONLY if framed as a GENERIC mechanism for
  dynamical bimodality via localized non-Hermitian rank-one perturbations.
- **Novelty (above J.Phys.A, conditional):** net increment over Giuggioli = a dynamical
  *classification* of FPT distributions via catastrophe (saddle-node) in observable space.
  Defensible sentence: "a rare case where a minimal non-Hermitian defect produces a topology
  change in the time-domain observable, not only in spectral properties."
- **Headline:** lead with topology change / saddle-node + interior δ-sink, framed as observable
  dynamics (not solvability/lattice). Title e.g. "Saddle-node bifurcation of first-passage-time
  distributions induced by a directed shortcut in stochastic transport networks."

## PRR roadmap (the genuine remaining work — gating, mostly research not framing)
1. **General saddle-node EXISTENCE THEOREM** (pro's "biggest theoretical gap"): a criterion for
   when a rank-one defect produces a saddle-node in the FPT density, in terms of resolvent-
   derivative structure — replace "we compute b_c" with "condition for existence". (The
   normal-form scaling now in the cert is a step toward this.)
2. **Universality / robustness:** 2D or multiple-shortcut (defect competition) or random-ensemble
   analogue; robustness of b_c under perturbed (β, q, θ) so it isn't seen as fine-tuned.
3. **Physical embedding:** ≥1 real mapping (reset/search, small-world transport, biochemical
   active-transport shortcut, neuronal/ecological directed jumps); clarify the non-Hermitian
   operator form Q+|u⟩λ⟨u| and PT-like analogy.
4. **Figures (PRR-grade):** phase diagram b-vs-N (saddle-node region); peak-valley annihilation
   with **scaling collapse** (the δ^{1/2}/δ^{3/2} laws); spectral-vs-time-domain comparison
   (prove "not just eigenvalue crossing"); robustness panels.
5. **Framing/prior-art pass:** b_c/δ-sink headline; demote A(d)/b_pl/N* to classifier corollaries;
   cite Giuggioli PRX 2020; correct Mattos 2012 (P(ω)); π_sc = splitting probability.

## Recalibrated odds (reconciled)
- **J.Phys.A: ~55–65% now** (after framing pass) — exact defect-resolvent study carries it.
- **PRE: ~60–70%** after restructuring.
- **PRR: ~50–60%** — BOTH technical blockers now cleared (b_c certified w/ scaling; full general-θ
  curve landed); remaining gap = significance/universality (existence theorem + one universality
  result + physical embedding + figures) + framing. No correctness blockers remain.
Recommendation: target J.Phys.A first (fastest); pursue the existence theorem + one universality
result to make a genuine PRR run; take this roadmap to Luca for the venue decision.

Records: Claude fan-out `wf_0481fe29-490`; ChatGPT Pro chat 6a43f5cd (referee) + 6a43b8d7 (b_c).
