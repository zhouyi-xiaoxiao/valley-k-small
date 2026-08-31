# Round 28: PRR manuscript resolution and adversarial re-audit

Date: 2026-07-13  
Scope: resolution of all 14 findings in
`audits/round_27_prr_manuscript_attack.md`, plus integration of the formal
broad-patch `B=0` bridge and the G1d finite-grid figure.  Frozen narrow
four-slab, G1c, and G1d scientific result artifacts were not edited.

## Verdict

**All 14 Round 27 manuscript/provenance findings are resolved in the current
source and build chain.  The manuscript remains `release_eligible=false` and
is not submission-ready because the declared scientific release gates remain
open.**

This resolution is deliberately narrower than a publication PASS.  In
particular, it does not promote the narrow or broad `B=0` four-slab results to
positive-event-mass Doi evidence, the G1d bounded-grid fold to a continuum
result, or any unrun physical-`d=3` calculation to evidence.

## Finding-by-finding closure

| Round 27 finding | Status | Resolution in the current manuscript/build |
|---|---|---|
| P0.1 unbounded transfer used the wrong norm | **RESOLVED** | The weak-budget section now distinguishes a generic bounded reflected quotient from the unbounded physical cylinder.  It formally states `X_pi=L^2(pi^{-1} dx)`, the weighted dual observable norm, the unitary map `q=pi u`, `kappa_pi=1`, and the replacements in the mixed-jet estimate.  The direct theorem and Appendix now invoke this unbounded weighted-space corollary explicitly. |
| P0.2 exact/global mode-count overclaim | **RESOLVED** | Abstract, direct theorem commentary, gate ledger, and Discussion uniformly say **at least** `m`, preserve the `m`- and epsilon-dependent family, the sequential epsilon-then-`B` limits, the contact-interior construction, and the non-exclusion of extra extrema.  The Discussion no longer says that one fixed transport/geometry realizes every exact finite mode count. |
| P1.1 abstract omitted decisive assumptions and mislabeled epsilon | **RESOLVED** | The abstract states the monotone-path/contact-interior hypotheses and that epsilon jointly scales OU noise, initial variances, and slab width.  It also states that only weights vary within each fixed comparison. |
| P1.2 `observable` language for a `B=0` shape result | **RESOLVED** | The subsection is now “Relative-prominence-qualified four-slab `B=0` design”; it defines `G=lim_{B downarrow 0} f_B/B`, denies positive event mass, and uses relative-shape language in the text, table, and Discussion.  The caption explicitly states that the frozen figure's legacy panel word “observability” denotes only relative peak/valley ratios. |
| P1.3 G1c/G1d global-root and timing overstatement | **RESOLVED** | G1c is identified as G1b-informed but prospectively frozen, with retained sign-changing roots on the frozen screen.  G1d is identified as result-informed, post-G1c, and not preregistered, although its numerical choices were frozen before execution.  Its side topology is explicitly restricted to the `t in [3,18]`, `Delta t=0.02` sign-changing-root screen and is not called a global census. |
| P1.4 unbounded physical cylinder conflated with bounded grid | **RESOLVED** | The unbounded OU-cylinder quotient and the G1 reflected truncation are separate objects.  The actual G1 bounds `z in [-0.25,1.85]`, `r_parallel in [-1.8,1.8]`, and periodic `r_perp in [-0.5,0.5)` are displayed, and the absence of a box-to-unbounded limit is explicit.  The distinct G1 and four-slab parameter sets are also stated. |
| P1.5 quantitative persistence asserted but not stated | **RESOLVED** | A quantitative proposition now defines the fold/cusp maps, an interior closed ball, inverse-Jacobian contraction conditions, the displacement bound, invertibility persistence, and the Weyl rank bound `sigma_2(R_B) >= sigma_2(R_0)-||R_B-R_0||_2`.  The text explains how the finite entrywise mixed-jet bounds assemble into the required matrix norms. |
| P1.6 novelty claim and primary-source gaps | **RESOLVED** | The absence claim is replaced by a bounded targeted-search statement that is explicitly not proof of absence.  Primary citations were added at the points of use for area reactivity/occupancy, Brownian functionals, nonuniform partial absorption, residence/multiple local times, and mixture modality: Prüstel--Meier-Schellersheim (2014), Bressloff (2022), Ryu (2009), Ryu--Johnson (2009), Grebenkov (2007, 2020), and Ray--Lindsay (2005).  Their DOI metadata was checked against primary/publisher records. |
| P1.7 title too strong and inherited GIG over-weighted | **RESOLVED** | The working title is now “Conserved-reactivity control of encounter-time modality: weak-reaction theory and continuum-kernel designs.”  The two long inherited GIG blocks were compressed to one explicitly ancestral supporting lemma and a short boundary paragraph; no physical conclusion depends on GIG realization. |
| P1.8 Luca/companion ancestry incomplete | **RESOLVED FOR INTERNAL DRAFT** | The foundational Giuggioli--Pérez-Becker--Sanders PRL (2013) and Giuggioli PRX (2020) primary citations were added.  The related-manuscript statement requires public identifiers, editor-facing copies, and an author-approved equation/code/data/figure overlap map before release, and forbids treating the companions as independent validation. |
| P2.1 undefined unsubscripted `F` in four-slab section | **RESOLVED** | The four-slab cusp and fourth derivative are written consistently in terms of the previously defined free-exposure limit `G`. |
| P2.2 variance and peak-floor wording | **RESOLVED** | The text states `S^2(t)=s^2(t)+rho^2` and physical convolved variance `epsilon^2 S^2(t)`.  The peak criterion is stated exactly as `min(P_i)/max(P_i) >= 0.10`, distinct from the valley ratios. |
| P2.3 compressed/ambiguous gate table | **RESOLVED** | The rebuilt table exposes the contact-interior and sequential-limit scope, result-informed `B=0` scope, one-fixed-box G1d scope, and the distinction between a proved bridge and applications requiring margins.  A ragged-cell layout was visually audited. |
| P2.4 incomplete source-to-PDF hash chain | **RESOLVED BY THE PARALLEL BUILD-PROVENANCE REPAIR** | The current compile driver fail-closes on TeX, bibliography, generated macros, both included figures, figure metadata, and verified source pins.  The manifest records byte-identical clean builds and `release_eligible=false`.  This manuscript task did not edit the generator. |

## Additional evidence integrated without scope promotion

1. A short broad-patch paragraph records the result-informed `B=0` bridge:
   exact cusp time `13.30724696`, scaled fourth derivative `-44.6816`,
   unfolding SVD ratio `0.2649`, a separate mesh-qualified `s=0.13` control,
   four odd cubic fixed-box meshes, and strictly decreasing cusp/root-time
   errors.  The paragraph retains every mandatory negative claim: no
   preregistered discovery, interval certificate, positive-`B` Doi solve,
   unbounded-box limit, physical-`d=3` result, or project gate.
2. `artifacts/figures/finite_grid_fold.pdf` is included with a caption scoped
   to one bounded reflected `65 x 65 x 49` Doi grid at `B=0.6`, post-G1c
   result-informed timing, and the frozen sign-changing-root screen.  It is
   explicitly not continuum, trimodality, interval-global, or an independent
   solver.

## Build, provenance, and visual checks

- Final TeX SHA-256:
  `42660a2a55805c1f0e40437eaac63140793206c7dd91e5569b4443a0cffe877f`
- Bibliography SHA-256:
  `3a2f85a5c62e9dca55f32be567df8aea15be721312e6ef7c99dada780a633340`
- Final PDF SHA-256:
  `2d9a88067744dd117d3b0ca3f0daf6ac850ab9bf9089298a29c1ebcf1793d1c9`
- Compile-manifest SHA-256:
  `dd10a9e93c1343e1a0f665407299ac8fc1ce32c6c26a8c1e2a130e3fea4dccfe`
- Ten pages; two clean builds are byte-identical.
- Warning gate: zero missing files, overfull boxes, undefined citations, and
  undefined references.
- Font gate: 39 font rows, zero Type-3 and zero unembedded fonts.
- Included-figure hashes and metadata/source-pin chains pass for both the
  narrow four-slab and G1d figures.
- Visual QA inspected the title/abstract, weighted-space theorem,
  four-slab figure/caption, G1d figure/caption, and gate-table pages.  No
  clipping, overlap, unreadable text, or claim/caption mismatch remains after
  the explicit legacy-label clarification.
- A forbidden-phrase scan of extracted PDF text found no residual “realize
  every,” “unestablished intersection,” “observable trimodal,” “geometry
  parameter,” undefined four-slab `F`, or unqualified global-root language.

The targeted test set currently reports **19 passed, one temporary failure**.
The sole failure is outside the manuscript source: the broad-patch official
JSON present at this snapshot lacks the newly required
`numerical_reproducibility.numpy_global_seed` field.  The parallel evidence
agent is regenerating that deterministic official JSON; this audit does not
edit the frozen result.  The compile/provenance tests themselves pass.

## Remaining scientific and release gates

The Round 27 textual/provenance findings are closed, but the following are not
paper-level passes:

- positive-`B` four-slab killed-Doi persistence with an absolute event-mass
  floor;
- full G1d fold-jet convergence under odd/even mesh and box enlargement;
- independent-solver preservation of topology;
- controlled physical-`d=3` numerical evidence;
- author-approved companion disclosure, archival identifiers, funding,
  author order, and data/code availability.

Therefore the correct current decision is **continue the PRR research route,
but HOLD release/submission**.
