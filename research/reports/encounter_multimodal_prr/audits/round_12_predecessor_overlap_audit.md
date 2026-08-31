# Round 12 predecessor-overlap and duplicate-packaging audit

Date: 2026-07-13  
Auditor task: compare the new PRR project against the DPMA manuscript, the
finite encounter manuscript, and Luca's shortcut calculation source/correction
history; map model, control, theorem, numerical object, figure, claim, code,
and data overlap.

Primary output:
`notes/predecessor_overlap_map.md`.

## 1. Verdict

### Deliverable verdict

**PASS.**  The requested predecessor map now exists and covers the three
internal lineages at theorem/equation, numerical-object, figure, code/data,
and claim level.

### Publication non-overlap verdict

**FAIL CLOSED for PRR submission in the current state.**

The failure is scientific, not documentary.  The current completed layers are
still dominated by extensions of predecessor ingredients: a stronger reduced
GIG construction/theorem, a reduced cusp, a multi-output version of the
predecessor's budget projection, and a new continuum-solver foundation.  The
physical-2D cusp manifold, model-specific PDE jet persistence/rank theorem,
independent continuum validation, and controlled physical-3D transition have
not yet been completed.  Those are the results that make the paper
non-overlapping at PRR scale.

### Current internal claim-discipline verdict

**PASS with one structural warning.**  The working manuscript explicitly
withholds a continuum fold/cusp and does not claim first multimodality, first
fixed-resource reactivity optimization, first fold, or first cusp.  However,
the new G1 slab/OU quotient is a different physical model from the finite
encounter M2D-E/F/T families.  The final narrative must not call it their
continuum limit or imply that it converges the old fold coordinates.

## 2. Snapshot inspected

| File | SHA-256 |
|---|---|
| `encounter_multimodal_prr/manuscript/encounter_multimodal_prr.tex` | `d5688d354ee882e4560cb31d2e2d0d410f316e965ab2536f93b670b79839fcbd` |
| `encounter_multimodal_prr/notes/literature_gap_20260713.md` | `df4a758ce024a271c57c6ad6d43fa12a117e118a1dc272831bf2e101bbafe194` |
| `encounter_multimodal_prr/notes/theorem_program.md` | `5c289556ff1f7211fba479304b96d1c8e0a55806d5254f146012996780709976` |
| `encounter_multimodal_prr/notes/research_contract.md` | `eec9dcfc64c7d6711bcc670399a7b09f09f639325e53d81b29d26d1fc66b9652` |
| `ring_lazy_jump_ext_rev2/manuscript/dpma_prr_manuscript.tex` | `548b333585621e9545bc0b67ef7a5fdeb6950151200d751571573a52486abe54` |
| `encounter_heterogeneous_catalytic/manuscript/encounter_modality_jcp.tex` | `118616157a5d4674abb1a4444add91108e102f9c348fee08f9de4c93bf51c293` |
| Luca updated `Calculations.tex` | `11468a3023dbbdd4b1bcf1018f6802390a5eb182080d1c73229d98fdb6450bc7` |
| Audited `Calculations_corrected_complete_v3.tex` | `b6cc4164b87666bcc3ec094ae2334fa388efd59da907ca858255621d26bf9b17` |

The audit also inspected the relevant predecessor code families:
`validate_multid_gig_design.py`, `validate_gig_fold.py`,
`validate_modality_susceptibility.py`, `validate_2d_matched_fold.py`, the
DPMA fold/cusp/network scripts, and the Luca correction/sign-test notes.

## 3. Adversarial tests performed

1. **Model identity test:** compared state space, boundary conditions,
   diffusivities, drifts, catalytic coordinate, contact set, patch shapes,
   and budget measure rather than matching only the words “2D encounter.”
2. **Control identity test:** checked whether a control changes total killing,
   transport, geometry, initial law, or only redistributes one physical
   reaction budget.
3. **Theorem collision test:** matched each current theorem/equation against
   the closest predecessor statement, including standard identities that are
   not suitable novelty claims.
4. **Numerical-object test:** matched folds, cusps, endpoint contrasts,
   trimodal examples, capacity curves, roots, and normal-form fits.
5. **Figure/data test:** enumerated current scientific figures and compared
   their role with predecessor panels/artifacts.
6. **Code-lineage test:** compared the current report-owned scripts with the
   closest predecessor scripts at formula, parameter, and workflow level.
7. **Claim substitution test:** asked whether the current PRR story would
   remain publishably distinct if the uncompleted continuum cusp, PDE rank
   theorem, independent solver, and 3D transition were removed.  It would not.
8. **Luca independence test:** checked whether the `Calculations` packet is an
   independent model/result or analytical source history for DPMA.  It is the
   latter.

## 4. P0 findings

### P0.1 The finite encounter paper already contains most of the finite and reduced story

The predecessor already contains:

- the killed two-particle encounter model and relative/centre coordinate
  transform;
- reaction-support Green/Woodbury reduction;
- a finite reversible spectral sign-variation necessary condition;
- exact Fréchet--Duhamel response and scalar fixed-budget projection;
- projected `f_t`/`f_tt` independence as the cusp-unfolding condition;
- normalized GIG screening, mode-placement algebra, and inverse-height
  weights;
- a finite CTMC fold and three finite-grid M2D-F folds;
- equal-discrete-budget patterned/homogeneous endpoints;
- a three-patch finite-grid trimodal mechanism certificate; and
- 2D/3D capacity calibrations and the explicit future target of continuum
  fold transfer.

Therefore another paper centered on “GIG channels + Duhamel + finite folds +
2D three patches” would be duplicate packaging even if every calculation were
rerun in a new folder.

**Resolution condition:** the eventual abstract and first two figures must be
led by the physical continuum budget, the 2D cusp phase manifold, continuum
multi-jet rank/persistence, and the controlled 3D transition.

### P0.2 DPMA already owns the generic fold/cusp and localized-killing catastrophe story

DPMA contains an exact 1D continuum phase diagram, a nondegenerate off-gate
cusp pair, fold powers, signed-mode constraints, arbitrary finite-CTMC
localized-killing response, graph tests, Monte Carlo, and Brownian process
validation.  It also explicitly distinguishes density morphology from smooth
means and spectra.

Consequently, “localized killing creates a fold/cusp,” “signed cancellation
organizes multimodality,” or “generic `1/2,3/2` scaling” cannot be the new
PRR headline.

**Resolution condition:** catastrophe theory must be used as a diagnostic for
the new conserved-budget continuum manifold, not as the claimed discovery.

### P0.3 The current GIG result has direct parameter and formula ancestry

The predecessor's multidimensional GIG script already uses
`A_j=b m_j^2+p m_j`, inverse isolated peak heights, `b=0.01`, decade-separated
target modes, normalized Bessel-`K` constants, and derivative root isolation.
The current script improves this to fourth derivatives, fail-closed cusp
invariants, a canonical reduced cusp, and tests through `m=6`; the manuscript
adds a proof for every fixed finite `m` at sufficiently large separation.

Within the internal predecessors inspected here, the proof is genuine new
analytical content.  The construction and pilot are still direct extensions,
not independent discovery.  A final external finite-mixture/GIG literature
search remains necessary before any priority wording.

**Resolution condition:** retain the arbitrary-`m` theorem as a reduced-family
design lemma with all limitations.  Do not claim arbitrary physical encounter
modes without the resource-normalized mixed-jet realization and nonvanishing
observability bounds.

### P0.4 The multi-jet formula is an enabling extension, not the missing theorem

The finite encounter paper already derives the scalar budget-projected
gradient and states that projected `f_t` and `f_tt` directions must be
independent for a cusp.  Stacking outputs and writing the metric minimum-norm
pseudoinverse is useful exact linear algebra, but not enough to distinguish a
PRR paper.

**Resolution condition:** prove the actual continuum Doi operator's mixed
time/control differentiability and a continuum-stable quantitative lower
bound on the projected smallest singular value over a declared physical
patch region.

### P0.5 The new G1 family is not a continuum refinement of M2D-F

The models differ materially:

- current G1: equal diffusivities, longitudinal OU confinement,
  `R x T_W`, cell-centred Scharfetter--Gummel/periodic quotient, smooth
  centre slabs, full centre-space integral budget;
- M2D-F: unequal diffusivities, reflecting unit square, boundary-node CTMC,
  upwind drift, binary midpoint disks, per-grid state-sum budget.

This distinction protects the new project from merely converging an old
finite grid, but it also blocks any statement that current G1 confirms the old
M2D-F fold.

**Resolution condition:** call G1 a new, exactly symmetry-reduced continuum
testbed.  If a direct continuum promotion of M2D-F is desired, it requires a
separate cell-averaged version of that same physical model.

### P0.6 Luca's calculation packet is the DPMA analytical lineage, not independent evidence

The packet corrects the shortcut-to-absorbing-target resolvent sign, exact
generating function, dominant-pole law, and invalid proposed threshold.  The
corrected model is the same local-killing mechanism that DPMA develops into a
full fold/cusp paper.

**Resolution condition:** preserve and disclose the analytical ancestry; do
not count the packet as a second solver, independent physical realization, or
third publication establishing the new continuum result.

## 5. P1 findings

### P1.1 Figure duplication is currently absent, but the first future figure is strategically constrained

The inspected new TeX has no scientific `includegraphics`, and the report has
no files under `artifacts/figures`.  No byte-identical figure reuse is therefore
present.  This is a clean starting point, not a completed provenance audit.

The eventual first results figure should be the new physical-2D cusp/simplex
phase diagram.  A GIG root plot, two-peak curve, fold-power plot, or ring-like
schematic first would visually duplicate predecessor narratives.

### P1.2 Current code namespaces are separate, but conceptual ancestry must be recorded

The continuum smoke/discovery runner is report-owned and implements a distinct
model.  The GIG code, however, directly extends predecessor formulas and
parameters.  Separate paths and SHA hashes do not erase intellectual or code
ancestry.

**Resolution condition:** the final artifact manifest must state for each
script and figure whether formulas or code were copied, adapted, or newly
implemented, and point to the ancestral paths.

### P1.3 “Promoting the finite paper to continuum” is only partly accurate

At the theory-program level, the new work promotes the finite-budget design
question to a resolution-independent continuum resource.  At the model level,
the chosen G1 geometry is different.  The manuscript should say it advances
the finite program to a new continuum testbed, not that it proves convergence
of the predecessor's numerical families.

### P1.4 The strongest title must name the resource and the cross-dimensional control

Titles led only by multimodality, folds, cusps, spatial geometry, or localized
absorption collide with external literature and DPMA.  The safe strong title
is of the form:

> Conserved-reactivity control of cusp-organized encounter-time modality in
> two and three dimensions

It remains gated by the actual cusp, rank, independent-solver, and 3D results.

### P1.5 Companion disclosure must be two-layered

The final paper must distinguish:

1. external ancestry from Luca and co-workers' published encounter/lattice
   program; and
2. internal reuse from the two companion manuscripts authored within the same
   program.

A generic related-work paragraph is not enough.  The editor should receive a
theorem/equation/figure/data/code table and any unpublished related manuscript
required by journal policy.

## 6. Prohibited substitutions

The following cannot compensate for a failed continuum gate:

- adding more values of `m` to the reduced GIG scan;
- adding more finite CTMC folds or finite 2D grids;
- repeating generic fold exponents with smaller numerical errors;
- treating a smoke-test pass as continuum verification;
- showing a fixed 3D bimodal density without a controlled two-sided
  transition;
- calling a reduced cusp a physical encounter cusp; or
- relying on companion papers as “independent” validation.

## 7. Release gates created by this audit

The PRR non-overlap verdict changes to PASS only when all of the following are
true:

1. the physical full centre-space budget is identical across meshes and the
   independent solver;
2. an interior physical-2D cusp and both fold branches are continued on a
   frozen three-patch simplex;
3. the full fold/cusp jets, projected rank, and observability/tail margins
   converge under declared parity/refinement gates;
4. a model-specific PDE mixed-jet persistence/rank theorem is proved;
5. a physically distinct solver agrees without parameter refitting;
6. a physical-3D fixed-budget fold or predeclared two-sided modality
   transition is validated under dimension-correct normalization;
7. every reused theorem/equation and adapted code path is disclosed; and
8. no predecessor figure, dataset, threshold, or finite-grid result is
   presented as new.

Until then, keep `release_eligible=false` and retain a working-program title.

## 8. Safe abstract and disclosure decision

The full wording recommendations are in
`notes/predecessor_overlap_map.md`.  In brief:

- lead with conserved centre-space reactivity, not with existence of multiple
  peaks;
- state that transport, geometry, contact, initial law, and supports are
  frozen;
- describe the reduced arbitrary-`m` result as reduced unless the physical
  bridge passes;
- say explicitly that DPMA supplies single-gate catastrophe ancestry and the
  finite encounter paper supplies the finite-budget design foundation; and
- claim as new only the completed continuum resource manifold, quantitative
  multi-jet control/persistence, and cross-dimensional controlled
  realization.

## 9. Final audit decision

- Requested overlap-map artifact: **PASS**.
- Accuracy of the map against the inspected snapshots: **PASS**.
- Current internal no-overclaim discipline: **PASS with the distinct-model
  warning**.
- Current PRR scientific non-overlap: **FAIL CLOSED**.
- Plausible route to PRR non-overlap: **PASS conditionally**, through the
  physical-2D cusp/manifold, direct PDE jet theorem, independent validation,
  and controlled physical-3D transition.
