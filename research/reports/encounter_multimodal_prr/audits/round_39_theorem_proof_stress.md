# Round 39: independent theorem-proof stress audit

Date: 2026-07-13  
Scope: fixed-finite-mode theorem, weak-(B) mixed-jet theorem, persistence
criteria, Appendix proof, theorem notes, and available Lean evidence  
Mutation boundary: no TeX, theorem source, Lean source, numerical source,
manifest, protocol, result, figure, or frozen positive-(B) file was changed.
The only additions are this audit and
`notes/theorem_proof_stress_report.md`.

## Verdict

**PASS for conventional mathematical correctness of the two scoped
theorems; HOLD for formal-verification and PRR scientific release.**

| Layer | P0 | P1 | P2 | Decision |
| --- | ---: | ---: | ---: | --- |
| theorem truth/proof | 0 | 0 | 0 | maintain `PROVED (SCOPED)` |
| formal evidence | 0 | 1 | 0 | not Lean-verified |
| manuscript theorem precision | 0 | 0 | 2 | repair in focused rewrite |
| PRR scientific release | not encoded as proof-defect counts |  |  | HOLD |

No attack found a reversed quantifier, illegal epsilon/(B) interchange,
missing contact condition, wrong OU variance, invalid weighted-space pairing,
incorrect Dyson factor, insufficient cusp jet, or false nondegeneracy transfer.
The detailed reconstruction is in
`notes/theorem_proof_stress_report.md`.

## P1-E1: available Lean evidence does not cover the manuscript spine

This is the only high-priority finding.

- `FormalLean/EncounterDesign.lean` explicitly excludes root count,
  nondegeneracy, and persistence under finite width, boundaries,
  discretization, and overlap.
- `FormalLean/EncounterContinuum.lean` explicitly excludes PDE well-posedness,
  error bounds, and cusp root counts.
- `FormalLean/Encounter.lean` explicitly excludes the continuum analytic
  bridge and implicit-function/catastrophe reduction.
- Their axiom reports pass only for the algebraic statements they contain.

Therefore the main fixed-finite-(m) and weak-budget results are human-audited
mathematical proofs, not Lean proofs.  This does not invalidate the manuscript's
current `PROVED` label because the manuscript does not claim Lean coverage.
It does fail any stronger project requirement that all main theory be
Lean-verified.

Required resolution before any formal-verification claim:

1. create a report-owned formal-scope ledger;
2. formalize interval mode uniqueness and (C^2)-perturbation persistence;
3. formalize the nested epsilon-then-(B) quantifier wrapper, cusp determinant,
   contraction, and Weyl finite-dimensional lemmas; and
4. keep the semigroup and wrapped-Gaussian tail parts explicitly human-proved
   until they too have precise imported/formal theorems.

## P2-T1: make the direct theorem self-contained

The detailed note has all required assumptions.  The manuscript places some of
them in preceding prose rather than the theorem paragraph itself.  The focused
rewrite should quantify
(r_{\parallel,0},r_{\perp,0},\Sigma_{\perp,0}), state
(s_0^2<D_0/\gamma) and (u_0^2<4D_0/\gamma) as theorem hypotheses, and
display

\[
 \exists\epsilon_0\;\forall\epsilon<\epsilon_0\;
 \exists B_0(\epsilon)\;\forall B<B_0(\epsilon).
\]

This is a precision repair, not a change to the theorem.

## P2-T2: consolidate the submission proof package

The integrated statement, detailed Markdown proof, and adjacent Lean algebra
currently live in three locations, including another report tree.  Before
submission, the full theorem and proof should live in the article/Supplement;
Markdown and Lean artifacts should be cited as reproducibility/provenance, not
as hidden dependencies of the proof.

## Quantifier and boundary audit

| Attack | Result |
| --- | --- |
| one geometry supports all (m) | explicitly denied; family depends on (m) |
| exact global count equals (m) | explicitly denied; conclusion is at least (m) |
| epsilon and (B) limits commute | explicitly denied; epsilon is fixed first |
| (B_0) uniform as epsilon tends to zero | not claimed |
| arbitrary target times without monotonicity/contact | not claimed |
| arbitrary simplex boundary weights | excluded by (w_j\ge w_{\min}>0) |
| (t=0) time jets | excluded by (t\ge\tau>0) |
| long-time (t=O(B^{-1})) control | explicitly excluded |
| finite event-mass floor from weak-(B) theory | explicitly excluded |
| arbitrary localized patches or arbitrary (d) | explicitly excluded |
| nondegenerate intervening minima | not claimed by the direct theorem |
| positive-(B) global absence of extra roots | not claimed |

## Independent formula checks

1. The midpoint invariant variance is
   (\epsilon^2D_0/(2\gamma)); the relative longitudinal invariant variance is
   (2\epsilon^2D_0/\gamma).
2. Gaussian (L^2(\pi^{-1})) integrability gives exactly the two strict
   variance thresholds printed in the manuscript.
3. The own-clock slope and curvature scale as
   (\epsilon^{-2}) and (\epsilon^{-3}); cross clocks are exponentially
   smaller for every fixed finite target set.
4. The unbounded pairing uses
   (\|V\|_{L^2(\pi dx)}\), and (q=\pi u) is unitary into
   (L^2(\pi^{-1}dx)).
5. The complex-time Cauchy disk has radius (\tau/2) and
   (|z|\le3T/2), giving the stated time-derivative factor.
6. The first and second state sensitivities and all direct observable terms
   have the correct signs and multiplicities.
7. The cusp Jacobian uses time orders through four and first control
   derivatives through time order three; the mixed-jet theorem supplies them.
8. The contraction criterion maps the closed ball into itself and gives one
   local zero; Weyl compares response matrices on the same region.

## PRR decision

The mathematical spine is strong enough to retain in a PRR-directed paper,
but it does not close the journal gate.  The direct construction suppresses
nontrivial encounter dynamics near the designed peaks by taking the contact
factor to one, and the weak-budget theorem supplies no demonstrated overlap
between its small-(B) regime and a positive event-mass floor.  The shortest
promotion route remains a finite-parameter physical-(d=2) allocation cusp and
two fold sheets, an event-mass-qualified trimodal region, parity/box
continuation, and one independent unbounded off-lattice killed-process
validation without refitting.

Final decisions:

- direct fixed-finite-mode theorem: **PASS, scoped**;
- weak-(B) mixed-jet/persistence theorem: **PASS, scoped**;
- Lean verification of those theorems: **FAIL/NOT PRESENT**;
- PRR release: **HOLD**;
- permission to continue the positive-(B) and allocation-cusp program:
  **YES**.

