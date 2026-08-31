# Round 38: focused PRR editorial-spine attack

Date: 2026-07-13  
Role: independent editorial adversary for the focused physical-`d=2` route  
Boundary: read-only with respect to the manuscript, code, frozen protocols,
results, and figures. This audit and
`notes/prr_focused_spine_rewrite_blueprint.md` are the only files added. The
pending positive-`B` outcome is neither inspected as a final result nor
prejudged here.

## Snapshot

- TeX: `manuscript/encounter_multimodal_prr.tex`, 1079 lines,
  `f3bf7cb11b7657bc65cdcbb3b9f7fcc15e3b799c072177d2daaeb738401c89ed`.
- PDF: `manuscript/encounter_multimodal_prr.pdf`, 12 pages,
  `13986921d2f8c5f478845bfd1abeaa9161e173d0b8030430757b9f65694ab94b`.
- Promotion premise: `audits/round_33_prr_promotion_strategy.md`,
  `4c2037ebcbeb2f6cc2a38ac56919d513120683a294249432cca1f615b85d4f56`.

## Editorial verdict

**Current manuscript: HOLD as a submission document.**

The scientific ingredients can support a strong focused paper, but the present
12-page version is a project ledger. It devotes the abstract and main figures to
several nonidentical families, exposes internal QA terminology to the reader,
and never lets one finite-parameter physical result carry the narrative from
design through validation. Adding a positive-`B` subsection to the current
structure would worsen, not solve, that problem.

The correct repair is a post-result rebuild around the broad four-slab family.
The exact line-by-line disposition and conditional abstract/title language are
specified in `notes/prr_focused_spine_rewrite_blueprint.md`.

## P0 editorial findings

### P0.1 — the finite-parameter headline has no single-family evidentiary chain

The main text currently alternates among:

- a GIG reduced-clock lemma (lines 189--210);
- a narrow four-slab exact `d=2` free-exposure design (641--720);
- a separately selected narrow `d=3` free-exposure design (722--792);
- a broader-patch `B=0` finite-volume bridge (794--810);
- three-slab negative/discovery history (812--860); and
- an unrelated three-slab bounded-grid fold at `B=0.6` (861--926).

None supplies the missing links of another. A submission claim about
finite-budget cusp control must use the same broad family for the exact seed,
positive-`B` cusp, both folds, representative modes, convergence, and
independent validation.

**Closure:** make the broad four-slab family the sole main numerical family.
If its finite-`B` cusp or independent topology fails, remove cusp-control from
the headline rather than borrowing evidence from G1d or the narrow kernels.

### P0.2 — the current abstract is an audit summary, not an outcome abstract

Lines 54--80 lead with `Internal status`, enumerate evidence provenance, name a
post-G1c grid, and end with work not yet done. The abstract forces a referee to
reconstruct the paper's result from caveats. It also treats finite-parameter
`d=2` and `d=3` as parallel ambitions even though the focused route resolves
finite `B` only in `d=2`.

**Closure:** replace the abstract in full using the conditional template in the
blueprint. The first sentence must state the physical outcome. `d=3` appears
only in the theorem sentence unless a positive-`B` independently validated
`d=3` result is completed.

### P0.3 — a cusp-centered title is conditional on a finite-`B` allocation cusp

The current exact cusp is a `B\downarrow0` normalized free-exposure result. The
current finite-`B` fold is in a different three-slab family and uses one control
direction. Neither licenses a finite-budget cusp-control title.

**Closure:** require, in the broad family at fixed positive `B`, the complete
cusp jet, two independent simplex-tangent allocation directions, rank two,
both fold branches, a remote pair, and representative modality regions. Until
then use a theorem-first working title.

### P0.4 — independent physical validation is part of the narrative, not a footnote

The current manuscript repeatedly says that an independent killed-process
solver is missing, but its proposed structure has no results section into which
that solver can naturally enter. A late caveat cannot turn same-operator checks
into physical validation.

**Closure:** reserve a full main section and one main figure for mesh/alignment/
box convergence and a physically distinct unbounded killed-process method at
unchanged parameters. Report uncertainty and cross-method agreement, not a
Boolean status.

## P1 editorial findings

### P1.1 — the strongest theorem is buried behind reduced ancestry

The physical fixed-finite-mode theorem begins only at line 455, after a full GIG
section, projected linear algebra, and lengthy weak-space machinery. Its
constructive physical meaning is harder to find than the inherited screens.

**Closure:** move GIG to the supplement; state the physical theorem immediately
after the model; follow it with the weak-`B` transfer that closes the Doi link.

### P1.2 — current figures advertise secondary or unrelated families

- Current Fig. 1 is the narrow `d=2` `B\downarrow0` family.
- Current Fig. 2 compares separately selected narrow `d=2` and `d=3` designs.
- Current Fig. 3 is the unrelated three-slab `B=0.6` bounded-grid fold.

None is the decisive broad-family positive-`B` control/validation figure.

**Closure:** move current Figs. 1--2 to the supplement and Fig. 3 to the
supplement or archive. The main figures must show (1) broad geometry and exact
seed, (2) finite-`B` allocation cusp/phase diagram, and (3) convergence plus
independent validation.

### P1.3 — process qualifications obscure scientific scope

Lines 115--121 define an evidence ontology. Lines 641--926 repeatedly use
`result-informed`, `frozen`, `not preregistered`, internal calculation names,
and machine flags. Lines 928--964 are a gate ledger. This vocabulary is useful
for internal research governance but makes the submitted paper sound provisional
even where the underlying statement is rigorous.

**Closure:** remove the ontology and ledger. Preserve transparency once in
Methods: how the design was selected, which inputs were then held unchanged,
and which data were used for validation. Elsewhere give numerical estimates,
error bars, and ordinary scope statements.

### P1.4 — theorem, leading-order design, finite-`B` evidence, and dimension are easy to conflate

The current manuscript is honest locally, but the reader must aggregate many
caveats to learn that:

- the theorem is positive-`B` but sequential/asymptotic and `m`-dependent;
- the exact broad cusp is the normalized `B\downarrow0` leading object;
- a positive-`B` point is not a cusp or continuum result; and
- `d=3` has theorem plus separately selected exact free-kernel evidence only.

**Closure:** enforce the claim-scope table in the blueprint. In particular,
never write `B=0 reaction-time density`; use `B\downarrow0 normalized
free-exposure limit`.

### P1.5 — the current Discussion recites evidence history instead of explaining mechanism

Lines 966--996 alternate among theorem limitations, narrow `d=2/d=3` shapes,
G1d, and future calculation branches. The reader leaves with a to-do list, not
with the physical reason spatial allocation controls timing.

**Closure:** rewrite the Discussion around separated exposure clocks, the
conserved-simplex cusp determinant, finite-budget survival depletion, and the
scope of the `d=2` validation. Move open project tasks out of the paper; retain
only genuine scientific limitations and future questions.

### P1.6 — the main article carries proof and reproducibility detail at the expense of the result

The current Appendix (1004--1075), 42-gate smoke paragraph (818--838), negative
search history (839--860), and full functional-analytic constants are valuable
but not all belong in the main article.

**Closure:** use a separate Supplemental Material structure. Keep theorem
statements and proof ideas in main; move derivations, tail estimates, exhaustive
tables, and ancestry there.

## P2 editorial findings

1. Remove the rendered `Internal status---not a submission claim` sentence.
2. Delete the `\status` macro and all bracketed evidence badges from the final
   submission source.
3. Remove G1a/G1b/G1c/G1d names, audit rounds, machine-readable flag names,
   and gate counts from reader-facing text and captions.
4. Replace the gate ledger with, at most, one quantitative same-family table of
   estimates and uncertainty.
5. Fill acknowledgments, contributions, funding, data availability, companion
   identifiers, and archival links; do not publish `pending` placeholders.
6. Synchronize visible title, PDF metadata title, abstract scope, and `d=2`
   wording after the result branch is fixed.
7. Regenerate the figure/manifest/PDF provenance chain after the structural
   rewrite; old hashes cannot certify the new paper.

## Required post-result branch

### If the positive-`B` held-out point fails

- Do not add it to the manuscript as a near-pass.
- Do not substitute the G1d fold for the missing broad-family result.
- Reassess a theorem-first paper or begin a separately frozen redesign.

### If the point passes but the same-family cusp is not yet complete

- It may enter an internal theorem-first draft as one fixed-allocation,
  semidiscrete, event-mass-qualified point.
- It must not produce a cusp/phase-diagram title or conclusion.
- Continue the fixed-budget allocation cusp and validation program before the
  focused SEND-2D rewrite is called complete.

### If cusp, convergence, and independent validation all pass

- Execute the blueprint as one structural rewrite.
- Use the broad family in every main numerical section and figure.
- Restrict finite-parameter claims to physical `d=2`.
- Keep `d=3` as theorem plus supplemental exact-kernel breadth unless its own
  finite-`B` validation is completed.

## Attack conclusion

No additional scan or caveat paragraph can repair the current editorial spine.
The route to a PRR-level document is a subtraction and reconnection exercise:
remove the internal research ledger, elevate the two analytical results, and
make one broad physical-`d=2` family carry the exact design, finite-budget cusp,
event masses, convergence, and independent physical check. The detailed
rewrite can begin only after the pending positive-`B` branch has a resolved,
audited outcome.
