# Round 10 independent novelty and positioning audit

Date: 2026-07-13  
Scope: PRR-level novelty, positioning, and non-overlap only.  This audit does
not re-prove the GIG theorem, certify the numerical implementation, or edit the
manuscript/code.

Snapshot SHA-256:

- `encounter_multimodal_prr.tex`:
  `4d201ede1f0276582a432f91189010f5f718fd75510dbdccc001044e7717b259`
- `literature_gap_20260713.md`:
  `df4a758ce024a271c57c6ad6d43fa12a117e118a1dc272831bf2e101bbafe194`
- preceding finite encounter manuscript `encounter_modality_jcp.tex`:
  `118616157a5d4674abb1a4444add91108e102f9c348fee08f9de4c93bf51c293`
- preceding DPMA manuscript `dpma_prr_manuscript.tex`:
  `548b333585621e9545bc0b67ef7a5fdeb6950151200d751571573a52486abe54`

## Verdict

**FAIL CLOSED for a PRR submission in the present state.**

The underlying positioning hypothesis receives a **conditional PASS**:

> The defensible novelty is the intersection of (i) fixed transport, geometry,
> contact law, and initial distribution; (ii) redistribution of only a static,
> nonnegative Doi encounter-reactivity field under one resolution-independent
> full centre-space integral budget; (iii) model-specific budget-projected
> multi-jet control and fold/cusp discriminants; and (iv) independently
> validated continuum realizations in physical dimensions two and three.

That intersection is stated clearly in the literature note (lines 32--50) and
is mostly respected by the manuscript (lines 80--131).  I found no sentence in
the current manuscript that falsely claims the first multimodal FPT, first
heterogeneous reaction law, first fixed-resource reactivity optimization,
first fold, or first cusp.

The submission verdict is nevertheless FAIL because the current evidence does
not yet instantiate the intersection.  The reduced GIG theorem, reduced cusp,
projected linear algebra, and quotient smoke are useful foundations, but the
model-specific continuum rank/conditioning theorem, physical 2D fold/cusp,
independent continuum validation, and controlled 3D realization remain open.
Moreover, the current release gate can be passed without a continuum cusp,
even though a cusp-level two-parameter modality manifold is the cleanest way
to separate this paper from the two preceding manuscripts.

Severity convention:

- **P0:** submission/release blocker or a collision that destroys the claimed
  PRR increment;
- **P1:** major positioning or evidence weakness likely to trigger rejection
  or a substantial revision;
- **P2:** framing, citation, or presentation issue that should be repaired
  before release but does not by itself destroy the project.

## Central novelty test

| Required limb of the combined claim | What is already established elsewhere | Current manuscript evidence | PRR release threshold |
|---|---|---|---|
| Frozen transport, geometry, contact, and initial law | Many prior FPT studies fix a stochastic process while changing another parameter; the preceding DPMA paper also studies localized killing at fixed transport on individual slices | Correctly declared at lines 92--100 and 168--170 | Persist the same operator, supports, contact radius, and initial-law hashes through every control continuation; perturb them only in separately labelled robustness families |
| One physical full centre-space budget | Fixed-total reactivity optimization is already known for other objectives; the preceding encounter paper uses per-grid discrete state-sum budgets | A resolution-independent centre-space integral is defined at lines 133--170 and specialized consistently to the 2D slab at lines 379--386 | Demonstrate the same continuum functional at every mesh and in the independent solver; no state count or configuration-volume surrogate |
| Exact projected multi-jet/fold-cusp framework | Duhamel response, a scalar fixed-budget gradient, generic folds, fold powers, and a cusp already occur in the preceding manuscripts; generic projection/pseudoinverse algebra is standard | The local multi-output minimum-norm formula and exact persistence jets are stated at lines 242--309 | Prove model-specific differentiability and a continuum-stable lower bound for the projected smallest singular value on the actual 2D/3D patch manifold; abstract full rank is not enough |
| Robust constructive multi-peak design | The preceding encounter paper already contains finite-grid folds, finite-grid trimodality, and GIG screening; multimodal FPTs are widespread externally | Arbitrary finite `m` is proved only in the separated GIG mixture; a reduced cusp is numerically certified | Use the reduced result as a design lemma unless an explicit observable continuum transfer is proved; certify actual physical roots, curvatures, prominence, mass, and tail margins |
| Continuum 2D/3D control realization | Continuum 2D multimodal capture and continuum 2D/3D two-particle encounter laws already exist | Exact 2D slab quotient and implementation smoke only; continuum fold/cusp and 3D are not run | A continuum 2D cusp with a remote max--min pair, plus a controlled 3D fold or equivalent modality transition under the same budget principle, both independently validated |

## P0 findings

### P0.1 The combined novelty is still a target, not a completed result

The abstract is commendably explicit: it withholds a continuum fold, cusp,
arbitrary-dimensional realization, and model-to-GIG remainder (lines 52--73).
The gate ledger likewise records the continuum fold as `NOT RUN`, the bridge as
`OPEN`, and physical 3D as `NOT RUN` (lines 420--439).

This honesty prevents an overclaim but does not create a PRR result.  The
currently completed non-overlapping pieces are:

1. an arbitrary-fixed-finite-`m` existence theorem inside an explicit GIG
   mixture family;
2. one well-conditioned numerical cusp inside that reduced family;
3. a multi-output extension of the predecessor's scalar budget-projected
   sensitivity, expressed as constrained linear algebra; and
4. an exact symmetry reduction and heavily gated implementation foundation.

None of these alone establishes conserved-reactivity control of modality in a
continuum two-body encounter law.  The central claim must remain future tense
until at least one physical modality boundary survives continuum and
independent-method gates.

**Release condition:** retain `release_eligible=false`.  Do not promote the
working title or abstract to an outcome claim until the physical continuum
components in P0.3 are complete.

### P0.2 Direct overlap with the two preceding manuscripts is not yet mapped at publication standard

The manuscript now discloses two companion working manuscripts and correctly
denies novelty for Duhamel, normal forms, fold powers, a first fold, and a first
cusp (lines 109--126).  This is a substantial improvement, but it is not yet an
adequate final disclosure: there are no identifiers/citations, and no
theorem--equation--figure--code overlap table.

The collision with the preceding finite encounter manuscript is especially
close.  That manuscript already contains:

- exact Fréchet--Duhamel response and a fixed-budget projected optimum
  (`encounter_modality_jcp.tex`, lines 725--794);
- projected `f_t`/`f_tt` independence as the condition for a
  budget-constrained cusp unfolding (lines 776--782);
- relative--centre GIG screening and exact GIG mode algebra (lines 799--872);
- fold discriminants, normal-form powers, and the joint-`C^3` continuum
  transfer requirement (lines 874--954);
- three finite-grid fixed-discrete-budget 2D folds (lines 1357--1456);
- a three-patch finite-grid trimodal construction (lines 1561 onward); and
- the explicit future target of a continuum fold and independent Robin or
  Brownian validation (lines 1993--2006 and 2040--2048).

The DPMA manuscript already contains localized-killing rank-one response,
geometry-resolved folds, a nondegenerate cusp, generic fold powers, finite
network extensions, and process-level validation (`dpma_prr_manuscript.tex`,
especially lines 31--50, 103--161, and 486--559).

The clean distinctions are real but narrower than the new manuscript currently
makes visually prominent:

| Predecessor | Old control/result | Result that must be unique to this paper |
|---|---|---|
| DPMA | One localized delivery/killing gate; its strength changes total loss, and some diagrams use gate/start geometry as controls; 1D continuum plus finite networks; fold/cusp already established | Multiple fixed supports with amplitude redistribution on a conserved physical centre-space budget; two-mobile Doi encounter; model-specific continuum multi-jet controllability and physical 2D/3D modality manifolds |
| Finite encounter paper | Fixed **discrete** killing-budget gradients; finite CTMC/grid folds and trimodality; GIG screening; no continuum modality theorem | Resolution-independent **physical** centre-space budget; quantitative continuum jet rank/conditioning; certified 2D cusp and 3D transition; an analytical or validated PDE-level persistence route |
| Luca's published lattice/network corpus | Multipeak laws produced by transport bias, persistence, competing routes, or disorder; exact confined-walk and multi-target tools | Freeze transport and geometry and use only conserved reaction-operator allocation as the causal control in a continuum two-body law |

**Release condition:** before submission, add an approved overlap table covering
every reused theorem, displayed equation, figure, dataset, and code path.  Cite
both public predecessors.  If either is still unpublished, disclose it as a
related manuscript and supply it to the journal.  The abstract should describe
this paper as promoting the finite-budget encounter program to a physical
continuum control theory, not as newly formulating the broad inverse problem.

### P0.3 The manuscript's PRR gate is weaker than its own novelty audit

The literature note's proposed strong package requires a certified 2D fold,
a well-conditioned 2D continuum cusp, an independent physical 3D realization,
dimension-correct transfer, and observable constructive margins (lines
481--496).  By contrast, the manuscript says that the strong title returns
after the analytical bridge, a resolved 2D continuum **fold**, independent
validation, and a physical 3D realization (lines 441--446).  Its ledger has a
row for a continuum fold but no row for a continuum cusp.

This mismatch matters because:

- a fold and generic fold powers already anchor DPMA;
- finite fixed-budget encounter folds already anchor the preceding encounter
  paper; and
- a single 2D fold plus one 3D bimodal curve may look like refinement of that
  paper rather than a new PRR-scale organizing result.

The two-parameter cusp/manifold is the strongest non-overlapping object: it
uses the genuinely new multi-jet rank structure, demonstrates creation of a
new max--min pair, and supports a control phase diagram rather than one
continued threshold.

**Release condition:** add separate hard gates for:

1. a physical 2D continuum fold with the complete fold jet;
2. a physical 2D continuum cusp with the complete cusp jet, a quantitative
   projected rank/conditioning floor, and a remote persistent max--min pair if
   trimodality is claimed; and
3. a 3D fixed-budget control transition, preferably a fold, rather than only a
   fixed multimodal example.

If no feasible, observable 2D cusp exists, re-evaluate journal positioning
rather than silently lowering the gate.

### P0.4 Abstract multi-jet algebra is not, by itself, the new theorem

Equations (projected `G`) and (multijet) are correct in scope and are explicitly
labelled constrained linear algebra (manuscript lines 253--277).  That label is
honest.  The non-overlap chain at lines 121--123 can nevertheless be read as if
the pseudoinverse formula were the first main result.

The predecessor already states the scalar projected optimum and the need for
linearly independent projected `f_t`/`f_tt` gradients at a cusp.  Stacking
outputs and writing the metric pseudoinverse is a natural extension, not a
PRR headline.  The publishable theorem is instead:

> For the specified continuum Doi operator and fixed patch manifold, the
> mixed time/control derivatives exist in the required topology, the projected
> jet map is quantitatively onto on a declared physical parameter region, and
> this conditioning persists under the continuum limit and supports a physical
> fold/cusp realization.

**Release condition:** prove or rigorously validate the model-specific rank and
conditioning statement.  Do not count the finite-dimensional pseudoinverse
identity as closing that gate.

## P1 findings

### P1.1 The current novelty sentence is slightly too categorical

The phrase “their unestablished intersection” (manuscript lines 98--100) reads
as a literature-absence assertion.  The literature note correctly calls the
same conclusion a search-based inference, not proof of absence (lines 32--46).

**Repair:** use “the intersection not located in our literature audit” or an
equivalent qualified sentence.  Reserve “to our knowledge” for the entire
combined, completed claim and refresh the search immediately before
submission.

### P1.2 The manuscript bibliography is too thin for the claimed ancestry

The manuscript cites the 2024 Giuggioli chapter and the 2025 network preprint,
but it does not yet cite the foundational Giuggioli two-walker encounter paper
or the arbitrary-dimensional confined-walk paper that the literature note
uses to establish ancestry.  It also omits several close comparator classes
already identified in the preceding encounter manuscript, including static
heterogeneous bulk killing/fixed-strength placement and fixed-absorbance
network placement.

Before release, the comparison should include, where directly relevant:

- Giuggioli--Pérez-Becker--Sanders (2013) for two-walker encounter ancestry;
- Giuggioli (2020) for confined arbitrary-dimensional walk tools;
- the specific biased/persistent/multi-target papers responsible for the
  multipeak mechanisms, rather than relying only on one broad chapter;
- Nguyen--Grebenkov and Scott et al. as already flagged in the preceding
  manuscript's fixed-strength/fixed-absorbance discussion; and
- Grebenkov--Ward's dimension-specific patch/capacity work if a new 2D/3D
  asymptotic bridge is presented.

This audit did not perform a new live bibliographic search.  It used primary
sources already recorded in the literature note and the repository's
predecessor bibliographies.

### P1.3 Two missing search lanes should be closed before a priority sentence

The literature note is strong on FPT, heterogeneous reaction, and narrow
capture, but it is comparatively light on:

1. multimodality and discriminant geometry of finite mixtures, including GIG
   or phase-type families; and
2. bilinear/static-potential control and PDE-constrained optimization for
   parabolic semigroups under an `L^1`-type resource constraint.

The project wisely does not claim generic mixture catastrophes or Duhamel
projection as new.  Even so, these lanes should be searched before calling the
multi-jet or arbitrary-`m` pieces novel.  The search outcome may change the
citations and emphasis even if it does not change the combined continuum
encounter claim.

### P1.4 The GIG arbitrary-`m` theorem should support, not carry, the PRR story

The reduced theorem is carefully scoped and is a genuine improvement over the
predecessor's finite screening.  However, it has no computed `R_sep`, no
separator-minimum nondegeneracy, no exclusion of extra critical points, and no
uniform observability floor.  The manuscript also records the earliest-channel
weight decay `O(R^{-(m-1)/2})` (lines 236--240).

That makes the theorem a strong design/existence lemma but a weak physical
headline.  Keep it in the main theory or an appendix as the source of candidate
clocks, while making the continuum cusp/manifold and physical budget the first
result seen by an editor.  Promote arbitrary physical mode count only after a
resource-normalized jet remainder and nonvanishing event-mass/prominence
bounds are proved.

### P1.5 The analytical bridge is currently broader and harder than the minimum PRR need

The proposed bridge asks a continuum Doi family to converge in full mixed jets
to the reduced GIG family (manuscript lines 311--351).  This would be powerful,
especially for an arbitrary-`m` continuum claim, but it may be an unnecessarily
hard critical path for the core PRR paper.

A more efficient two-tier route is:

1. **Required core theorem:** for the fixed smooth Doi PDE and patch family,
   establish time/control differentiability, the exact projected response, and
   a quantitative persistence/certification theorem for a numerically located
   fold/cusp.  Combine a justified `C^3`/`C^4` discretization error or
   Newton--Kantorovich/interval certificate with an independent solver.
2. **Optional stronger bridge:** prove GIG-to-Doi asymptotic transfer if the
   paper wants arbitrary finite physical mode count or geometry-predictive
   catalyst placement.

This separation keeps analytical content central while preventing failure of
the global reduced-clock approximation from blocking a strong finite-mode
continuum control result.  If the manuscript retains arbitrary-`m` continuum
language, the stronger bridge remains mandatory.

### P1.6 The 3D gate needs a specified controlled transition

The exact symmetry argument suggests a four-variable quotient in physical 3D
(manuscript lines 384--386), but the gate ledger only says “independent resolved
realization.”  A fixed two-hump 3D density is not enough because Le Vot et al.
already rule out novelty of that phenomenon.

Specify in advance:

- the 3D full centre-space budget normalization (for slabs, the transverse
  factor is `W^2` rather than `W`);
- which patch amplitudes vary while all other inputs remain frozen;
- whether the target is a fold, cusp, or at minimum a predeclared two-sided
  modality change along a budget line;
- the complete relevant jet and observability floors; and
- the physically distinct validation method.

### P1.7 The causal claim needs a machine-checkable frozen-baseline table

The central distinction from Luca's transport-generated peaks and from
initial-geometry-generated peaks is causal: only the reaction allocation may
change.  Prose alone will not be enough in a paper with several numerical
families.

For each headline continuation, store and report hashes or exact values for:

- the free transport operator and boundary conditions;
- contact radius/profile;
- patch centres, widths, and shapes;
- initial law;
- domain and coordinate convention;
- installed budget and quadrature; and
- only then the changing simplex coordinates.

Patch-width, patch-location, contact-radius, and initial-law variations should
be separate robustness panels with no re-fitting of the headline control
point.  They must not be mixed into the primary causal continuation.

### P1.8 The physical meaning of centre-space reactivity should be made concrete

The mathematical centre-field budget is clear.  For broad PRR impact, the
paper should also explain what physical intervention realizes
`K(x_1,x_2)=chi_a(x_1-x_2) kappa(c)`: for example, contact is chemically active
only when the encounter occurs in a patterned catalytic region of laboratory
space.  State the dimensionless control groups and a plausible scale regime.

Without this interpretation, a referee may view `kappa(c)` as an abstract
configuration-space killing potential rather than conserved installed
catalyst.  This is a positioning risk, not a mathematical defect.

## P2 findings

### P2.1 “Inverse first-passage” should remain secondary terminology

The abstract's “inverse problem” wording is not false, but inverse FPT is an
established field and the preceding encounter paper already poses the broad
design question.  Prefer “resource-constrained reaction-time modality control”
as the headline phrase.  Use inverse-design language only after stating the
static-field, nonnegativity, fixed-budget, and frozen-dynamics restrictions.

### P2.2 The external Luca relationship is correct but incomplete without the internal relationship

The literature note correctly frames Luca's published work as direct ancestry
plus a different control question (lines 178--218).  Because Luca is also an
author on the DPMA and finite encounter drafts, the final paper needs a second,
explicit layer: “what this paper reuses from our companion papers and what it
adds.”  Do not frame the relationship as competition over priority.

### P2.3 The eventual abstract should become outcome-first

The present status-heavy abstract is appropriate for an internal fail-closed
draft.  It is not an eventual PRR abstract.  Once gates pass, lead with the
physical continuum result and its control principle; move reduced pilots,
software smoke, and release caveats to methods/status material.  Do not retain
cell counts as a headline achievement.

### P2.4 A phase diagram and overlap map are part of the editorial case

The final PRR package should make two relationships immediately visible:

1. a two-parameter physical simplex with fold curves, the cusp, and regions of
   one/two/three observable modes; and
2. a compact predecessor-overlap table distinguishing DPMA, the finite
   encounter paper, and this continuum paper.

These are editorial aids, but they materially reduce the chance of a novelty
desk rejection.

## What is proved now versus what remains required

### Already proved or exactly established within the stated scope

- The centre-space integral budget and fixed-support amplitude-control model
  are precisely defined.  This is a model definition, not a novelty theorem.
- The Duhamel directional response is exact shared background.
- The metric projected multi-output minimum-norm formula is exact constrained
  linear algebra for an interior finite patch-amplitude space.
- For each fixed finite `m,p,beta`, sufficiently separated normalized GIG
  channels have at least `m` nondegenerate maxima and `m-1` intervening local
  minima.  This is a reduced-family theorem only.
- One three-clock GIG cusp is numerically certified with fourth-order and
  rank/conditioning diagnostics.  It is a reduced cusp only.
- The 2D slab symmetry quotient is exact under its stated transport, catalyst,
  and initial-law symmetries.
- The current numerical evidence is an implementation/foundation smoke pass,
  not continuum modality verification.

### Required before a defensible PRR claim

- A model-specific continuum response theorem through the full fold/cusp jet,
  including the direct observable derivative and a declared control norm.
- A quantitative lower bound for the projected smallest singular value on the
  actual physical patch manifold, stable under continuum refinement.
- A predeclared physical 2D fixed-budget fold and, for the strongest
  non-overlap, a well-conditioned two-control cusp with all scaled residuals,
  full jet convergence, and a persistent remote pair when trimodality is used.
- Odd/even or otherwise independent refinement, box/contact-quadrature checks,
  and a physically distinct off-lattice, Robin, or validated alternative
  solver with no parameter re-fitting.
- A 3D fixed-budget controlled modality transition under the same causal
  principle and dimension-correct scaling, not merely existence of a two-hump
  density.
- Prominence, valley, event-mass, rate, and tail floors that remain physical
  rather than merely mathematically nonzero.
- A complete companion-paper overlap/citation table, author-approved
  disclosure, and refreshed literature search.
- If arbitrary finite continuum mode count is claimed, the stronger GIG-to-Doi
  mixed-jet remainder and resource-normalized observability bounds.

## Recommended PRR route

The most efficient strong route is **cusp-first, finite-mode continuum
control**, not another broad reduced-family scan:

1. Freeze one physically interpretable 2D Doi slab model with three fixed
   catalyst patches and a two-dimensional budget simplex.
2. Use the reduced cusp only to seed a search; locate a physical interior cusp
   and continue both fold branches to obtain a modality phase diagram.
3. Certify the complete cusp jet, projected rank/conditioning, five alternating
   roots where trimodality is claimed, and all observability/tail margins.
4. Prove the direct PDE-level response/persistence theorem needed for that
   fixed model and pair it with independent continuum validation.  Do not make
   a full global GIG realization theorem a blocker unless arbitrary physical
   `m` is retained in the headline.
5. Reproduce at least a controlled fold in physical 3D under the same full
   budget principle, with dimension-correct normalization and a separate
   solver.
6. Make the non-overlap explicit: DPMA supplies localized-gate catastrophe
   ancestry; the finite encounter paper supplies the finite-budget design
   calculus; this paper supplies the physical continuum resource manifold,
   quantitative multi-jet controllability, cusp phase geometry, and
   cross-dimensional realization.

This route is plausibly PRR-level if all six items pass.  A single converged 2D
fold without a cusp/manifold, or a 3D bimodal curve without a controlled
transition, is likely incremental relative to the two companion manuscripts.

## Fail/redirect rule

Redirect to a focused PRE/JCP-style paper on continuum fixed-budget
reaction-time-shape control if any of the following survives a genuine search
and refinement campaign:

- no interior physical-budget fold/cusp exists in the declared patch family;
- the projected cusp rank collapses or is numerically ill-conditioned;
- the additional mode has vanishing event mass or fails the predeclared
  prominence/valley floor;
- parity/refinement families disagree or the second solver changes the
  modality topology; or
- the 3D control does not reproduce the organizing principle.

Generic catastrophe terminology, the reduced GIG cusp, or additional
finite-grid examples must not be used to compensate for a failed continuum
gate.

## Final decision

- **Current PRR submission:** FAIL.
- **Central novelty formulation:** PASS, conditional on the full intersection.
- **Current manuscript claim discipline:** PASS for an internal working draft.
- **Non-overlap proof:** FAIL until the companion overlap table and continuum
  differentiators are completed.
- **Best promotion path:** physical 2D continuum cusp/manifold + direct
  PDE-level jet persistence + independent validation + controlled 3D fold.

