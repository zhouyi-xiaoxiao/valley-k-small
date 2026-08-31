# Round 33: PRR promotion strategy audit

Date: 2026-07-13  
Role: independent, read-only promotion audit  
Execution boundary: no manuscript, theory note, code, result, figure, or
metadata file was edited; the positive-`B` held-out meshes were not run by this
audit. This audit file is the only file added.

## 1. Question and conditional snapshot

This audit asks a deliberately stronger question than whether the current
files are internally reproducible:

> If the frozen broad-four-slab calculation at `B=0.01` passes on both held-out
> meshes, what would still prevent the work from being a defensible Physical
> Review Research submission?

The answer is assessed against PRResearch's published criteria that a paper
make a high-quality, significant, authoritative, and substantive addition to
the literature, not merely against a successful software pipeline:
<https://journals.aps.org/prresearch/about>.

The conditional premise is narrow. A pass of
`notes/positive_b_broad_four_slab_protocol.md` would establish one
result-informed, fixed-control, positive-event-mass, trimodal **semidiscrete
point** on two odd meshes in one reflected box. The protocol itself correctly
keeps `unbounded_domain_FV_limit_verified`, `independent_solver_verified`, and
`project_gate_passed` false. This audit does not anticipate or prejudge the
held-out numerical values.

Snapshot read:

| File | SHA-256 |
| --- | --- |
| `manuscript/encounter_multimodal_prr.tex` | `ed29b1613572de107e321ac4f7bde5826d5929cd22431f572fae6ac366a725c0` |
| `notes/direct_physical_multimode_theorem.md` | `7493499883ba41ce043c3535e1ca3d6c7a4c5de0cce9e575e261b4f8da9c2974` |
| `notes/pde_mixed_jet_theorem.md` | `3fc37bafc6320556322e80daa2c56bad9fd4b19e1856100caa8adf92341a8007` |
| `notes/positive_b_broad_four_slab_protocol.md` | `a6811b21b5a66f765cad03f35f170997266d833ac94cf2a9b0e2686e8c9e16ec` |
| `artifacts/data/positive_b_broad_four_slab_manifest.json` | `128f9663b688993fab67a2c73d9bfd4c53997bd08a5f110a969eebb1af587a8a` |
| `code/positive_b_broad_four_slab.py` | `0792a4e218e0529e294a149adfc51a339a818f61bff85fa814480f83252dd42e` |
| `code/test_positive_b_broad_four_slab.py` | `06d5526c23908d1c296cf4417d6de4d5b9c31c2a455c3acd5e3b307e721f628f` |

Round 30 already closes the prior local theorem, bibliography, and figure-
language findings. I found no reason to reopen those repairs. The issues below
are **promotion obligations**, not regressions in the accepted Round 30
snapshot.

## 2. Executive verdict

### Decision after the hypothetical held-out pass: **HOLD**

The positive-`B` pass would be a major advance: it would close the present gap
between a normalized `B=0` shape and a finite-budget reaction-time law with
nonzero basin masses. It would not, by itself, make the paper PRR-ready.

Four scientific facts would still be missing from the preferred PRR story:

1. a finite-`B`, fixed-budget **allocation-control** cusp and its two fold
   branches in the same broad four-slab family;
2. continuum and unbounded-domain evidence, rather than two odd meshes in one
   fixed reflected box;
3. a genuinely independent killed-process calculation without parameter
   refitting; and
4. numerical uncertainty small enough that the topology, valley, event-mass,
   and jet conclusions are separated from their decision thresholds.

The manuscript also needs a substantial narrative contraction. At present it
contains the reduced GIG lineage, a narrow exact-kernel family, a different
broad-patch bridge, the G1 negative/discovery history, a separate `B=0.6`
three-slab fold, and a `d=3` free-kernel analogue. These objects are honestly
labeled, but their coexistence makes the central result look like a research
ledger rather than one authoritative physical argument.

### Recommended PRR spine

The work can constitute one unified contribution if it is organized as:

1. **Constructive generality:** under one conserved centre-space reactivity
   integral, every prescribed fixed finite mode count is realizable in an
   `m`-dependent physical `d=2,3` Doi slab family after the declared sequential
   `epsilon` then `B` limits.
2. **Analytical glue:** the compact-positive-time mixed-jet theorem transfers
   free-exposure modes, folds, cusps, and budget-projected rank to weak positive
   reactivity.
3. **Finite-parameter control geometry:** one frozen broad four-slab physical-
   `d=2` family realizes a positive-`B`, event-mass-qualified cusp, both fold
   branches, and a robust trimodal region.
4. **Physical validation:** mesh/parity and box convergence plus an independent
   unbounded killed-process calculation preserve the selected topology and
   observable masses without refitting.
5. **Dimension statement:** the `d=3` theorem and exact sphere kernel establish
   dimension-correct analytical generality; a positive-`B` `d=3` calculation is
   required only if the title or abstract claims a finite-budget realization
   in both dimensions.

This is a coherent progression from existence, to local control, to a resolved
physical realization. Without item 3, the catastrophe material is mostly
shared normal-form infrastructure. Without item 4, the finite-parameter result
remains a solver/box diagnostic. Without both, the arbitrary-mode theorem risks
being read as a narrow-channel weak-killing construction disconnected from the
numerical example.

## 3. Do the present ingredients form a unified contribution?

### 3.1 Fixed-finite-`m` theorem: **yes, but as the generality pillar**

The theorem is mathematically scoped correctly. It proves at least `m`
nondegenerate maxima for each prescribed fixed finite `m`; the geometry,
number of slabs, and admissible small parameters may depend on `m`; it does
not assert a single configuration with arbitrarily many modes, exclude extra
extrema, or supply a uniform event-mass floor. Those restrictions must remain.

Its publication value is not “many peaks exist.” The literature and the
repository's overlap map rule out that novelty. Its value is that the peaks
are constructed in an exact two-particle Doi quotient while only a static
reactivity allocation under one physical integral budget is controlled, and
that the nonlinear killed law is reached through the weak-`B` theorem.

The theorem should not carry the paper alone. The construction deliberately
keeps the deterministic relative path inside contact near all designed peaks,
uses narrow slabs/noise, takes `B` small after `epsilon`, and allows the event
mass to vanish with `B`. A referee can reasonably regard the separated-clock
mechanism as expected unless it is paired with the finite-parameter control
geometry and validation above.

### 3.2 Weak-`B` mixed-jet theorem: **yes; this is the logical connector**

This is the cleanest bridge between the two halves of the paper. It supplies
the exact state/control sensitivities, direct observable terms, full positive-
time cusp jet, an explicit `O(B)` mixed-jet bound, contraction conditions, and
a Weyl rank transfer in the physical budget metric. It explains why the
free-exposure singularity is not merely a heuristic proxy.

Its current limitation is application, not correctness. The manuscript does
not evaluate a usable persistence radius for the broad finite-parameter
family, and the conservative analytic bound need not certify `B=0.01`.
Therefore the paper must either:

- compute a quantitative overlap between the analytical persistence bound and
  the finite-parameter event-mass lower bound; or
- make the theorem an existence result and close the actual `B=0.01` case by
  continuation, convergence, and independent numerical validation.

The second route is more practical and is sufficient for PRR if the logical
separation is explicit.

### 3.3 Fold/cusp control: **not yet a completed new contribution**

The exact cusp determinant identity and budget-projected rank criterion are
model-specific and useful. Generic folds, cusps, and catastrophe exponents are
shared ancestry and cannot be sold again.

The current positive-`B` protocol varies the scalar installed budget and
reports `f_B`, `f_{tB}`, and `f_{ttB}` at one frozen allocation. Those are not
the two independent simplex-tangent **allocation** derivatives required by
the fixed-budget cusp jet in the manuscript. Even a perfect five-root pass
therefore confirms one trimodal point, not a finite-`B` cusp, projected rank,
or two fold branches.

This is the most important conceptual promotion gap. If “control” and
“cusp-organized” remain central, the same broad family must be continued at
fixed `B` in two allocation coordinates, with

`f_t=f_tt=f_ttt=0`, nonzero `f_tttt`, rank-two projected allocation response,
both outgoing fold branches, and a persistent remote max--min pair.

### 3.4 `d=2`/`d=3` exact kernels: **useful but not one finite-budget result**

The exact disk and sphere calculations show that the design principle and
cusp topology survive the dimension change at `B=0`. The sphere-coordinate
versus Fourier--Bessel cross-check is a genuine representation check. It is
not an independent killed-Doi solver.

The displayed `d=2` and `d=3` allocations are separately selected. The figure
therefore supports two dimension-specific designs under the same resource
principle, not robustness of one weight vector across dimensions. This is
already stated honestly and should remain so.

For a focused PRR paper, the theorem in both dimensions plus the exact `B=0`
sphere comparison can be enough dimensional breadth if all finite-budget
claims are explicitly restricted to `d=2`. A title or abstract claiming a
resolved finite-budget transition “in two and three dimensions” would instead
require positive-`B`, converged, independently validated `d=3` evidence.

### 3.5 Overall unity verdict

**Potentially unified, presently over-dispersed.** The four intellectual
objects fit one chain, but the current numerical evidence comes from several
different parameter families. The broad four-slab family should be the sole
finite-parameter spine. The narrow kernels can illustrate dimension effects;
the GIG material can become a short ancestry/design paragraph or appendix;
G1a/G1c negative history and the separate `B=0.6` fold should move to the
supplement/reproducibility record unless they are directly used in the final
claim.

## 4. Promotion severity ledger

Severity here is tied to the recommended cusp-control PRR route:

- **P0:** blocks `SEND` because it changes the truth or independence of the
  central claim.
- **P1:** materially weakens significance, unity, or referee defensibility;
  must be repaired before submission unless the claim is narrowed.
- **P2:** presentation or release hygiene; does not rescue a failed scientific
  gate but must be cleaned for the final package.

### P0 findings

#### P0.1 — no positive-`B` fixed-budget cusp/phase manifold in the main family

The hypothetical held-out pass gives one fixed allocation with five alternating
roots and positive event masses. It does not give the two allocation-control
directions, full cusp jet, projected rank, two fold branches, or a modality
phase map. The separate `B=0.6` G1d fold is a different three-slab parameter
family and cannot close this gap.

**Required for the preferred PRR claim:** freeze a post-confirmation protocol
for the broad four-slab family at `B=0.01`; solve and converge the fixed-budget
cusp in `(t,theta_1,theta_2)`; trace both fold branches; validate one-modal,
bimodal, and trimodal representatives without changing transport, geometry,
initial law, supports, or budget.

**Narrowing alternative:** drop the finite-parameter catastrophe/phase-manifold
headline and present a theorem-first paper with one positive-`B` trimodal
example. That version may be publishable, but it has a materially weaker PRR
case and would require removing most catastrophe-centered language. This audit
does not mark that route `SEND`.

#### P0.2 — no continuum/unbounded-domain validation of the positive-`B` point

Meshes 113 and 129 are both odd, use the same SG operator and contact
quadrature, and live in the same box. Agreement between them is not an
unbounded-domain limit and does not expose alignment parity or shared
discretization bias. The protocol itself makes this explicit.

**Required:** the mesh/parity and box-convergence package in Section 6 below,
covering every claimed root/topology quantity and, for the cusp, the complete
mixed jet and projected singular values.

#### P0.3 — no independent killed-process validation

Alternative quadratures for the `B=0` free kernel, explicit-CSR checks of the
same SG operator, centered finite differences of the same semigroup, and two
byte-identical executions are excellent implementation checks. None is a
physically distinct killed-process solver.

**Required:** at minimum, the unbounded off-lattice Doi/Feynman--Kac thinning
calculation in Section 6, or a genuinely independent FEM/spectral solver. It
must use the same physical inputs and must not refit weights or geometry.

#### P0.4 — threshold pass without a numerical uncertainty margin is not robust

The disclosed mesh-97 feasibility point is close to two boundaries: its second
valley ratio is `0.85157` versus a `0.85` ceiling, and its smallest basin mass
is `0.005307` versus a `0.005` floor. A later mesh can formally pass while
remaining too close to the threshold for a continuum claim.

**Required:** after extrapolation/independent validation, each promoted
quantity must pass with its numerical or statistical error bar contained on
the passing side. A useful fail-closed rule is

> total estimated error <= one quarter of the distance from the promoted value
> to its scientific threshold,

with a separately declared absolute cap. If the distance is essentially zero,
the result is scientifically marginal even if a Boolean gate says `PASS`.

#### P0.5 — companion-work disclosure and archival release are hard submission gates

The manuscript correctly acknowledges two close companion works and shared
Luca/DPMA ancestry. Before submission, authors must approve final identifiers
or editor-facing copies, the equation/code/data/figure overlap map, and exact
priority wording. A stable code/data archive, Data Availability statement,
author order/contributions, funding, and acknowledgments are also required.
These are release P0s, not scientific substitutes.

#### Conditional P0.6 — positive-`B` `d=3` evidence if both dimensions remain in the headline

There are two legitimate routes:

- **Focused minimum PRR route:** finite-parameter claims are explicitly `d=2`;
  `d=3` is a theorem plus exact free-kernel comparison. Positive-`B` `d=3` is
  then not a P0.
- **Strong two/three-dimensional route:** title/abstract claim finite-budget
  controlled modality in both physical dimensions. A frozen positive-`B`
  `d=3` transition, convergence evidence, event masses, and independent
  validation are then P0 requirements.

PRResearch's criteria do not themselves require two spatial dimensions of
evidence. It is better to submit one authoritative, independently resolved
`d=2` story than to retain an unsupported symmetric `d=2/d=3` headline.

### P1 findings

#### P1.1 — the main line is too fragmented

The manuscript currently reads as six evidence histories. The broad four-slab
family should connect exact `B=0`, weak-`B` theory, finite `B`, cusp/folds,
convergence, and independent validation. GIG screens, G1 negative scans, and
the unrelated `B=0.6` fold should not interrupt that chain.

#### P1.2 — the analytical bridge and `B=0.01` result are not quantitatively joined

The theorem guarantees an unspecified sufficiently small budget, while the
numerical protocol uses `B=0.01`. An explicit analytical `B_*` would be ideal
but may be extremely conservative. The minimum practical repair is a frozen
continuation in `B` from the exact `B=0` broad family to `B=0.01`, tracking all
five roots, curvature/prominence margins, the cusp, and allocation rank. This
does not replace convergence or the independent solver.

#### P1.3 — no reader-facing phase diagram or geometry-first figure

The decisive control result should be visible as a physical geometry/budget
panel and a two-dimensional allocation-simplex phase diagram with cusp, both
fold branches, and validated representative curves. A collection of
individual curves and audit gates is not an equally effective scientific
argument.

#### P1.4 — global-count and tail language must follow the actual certificate

The frozen protocol isolates sign-changing roots only on `[0,35]` and
propagates survival to 100. This is sufficient for “at least three certified
modes on the declared window” if convergence holds; it is not a proof of
exactly three global modes or a global one/two/three-mode phase diagram.

Either retain the at-least/window-qualified claim, or add an interval/tail
certificate (for example, interval root isolation on the finite system plus a
dominant-eigenmode tail sign bound). Do not make global exact-count language a
mandatory burden if the scientific conclusion only needs at least three
robust modes.

#### P1.5 — the event-mass floor needs interpretation and error control

`0.005` is a declared nonzero floor, not an experimentally universal
observability threshold. The paper should describe it as a robustness rule,
report all basin masses with discretization/statistical uncertainty, and show
that the conclusion is stable under a reasonable neighboring threshold.

#### P1.6 — `d=3` currently demonstrates a dimension-specific redesign

The selected `d=2` and `d=3` weights differ. This is acceptable for a design
principle, but the comparison must not be paraphrased as one catalyst
configuration robust to dimension. A same-allocation cross-dimension test
would be a useful limited addition; it is not required for the focused `d=2`
finite-budget route.

### P2 findings

1. The final paper should remove internal labels such as “not a submission
   claim,” the full project-gate ontology, preregistration-style process
   wording, and the internal gate ledger from the reader-facing main text.
   Selection/validation provenance belongs in Methods or the supplement.
2. The inherited GIG calculations should be compressed and explicitly treated
   as design ancestry. They are not an independent physical result.
3. The lengthy G1a/G1c negative-history narrative should move to a supplement
   or reproducibility archive. Its honesty is valuable, but it dilutes the
   central physics.
4. The final abstract must be outcome-first; the title should be upgraded only
   after the corresponding cusp/dimension gates pass.
5. Every figure/table needs a frozen raw-data/producer/manifest/ancestry chain,
   and final source/PDF hashes must be regenerated after the scientific
   rewrite.

## 5. Work that is bounded enough for this paper versus genuine follow-up

### Bounded work that should be done for this paper

These tasks are nontrivial but finite and directly close the PRR claim:

1. finish and independently audit the frozen positive-`B` held-out point;
2. freeze a new, separate protocol for fixed-`B` allocation-cusp continuation
   in the same broad four-slab family;
3. compute the complete allocation cusp jet, both fold branches, and
   representative mode regions;
4. run the mesh/parity and box-convergence matrix below;
5. run an independent unbounded off-lattice killed-process validation at
   predeclared controls;
6. consolidate the manuscript around that one family and refresh the
   overlap/release package; and
7. perform a final independent claims, theory, numerical, reproducibility,
   and rendered-PDF audit.

The protocol for items 2--5 must be frozen before looking at the new fine/
independent results. A failed topology or margin is a result, not permission to
retune the geometry inside the confirmation stage.

### Work that should remain outside the minimum PRR paper

None of the following is needed for the focused PRR claim and each would make
the present project less finishable:

- one fixed geometry supporting unboundedly many modes;
- a limit uniform as `m -> infinity` or an arbitrary-`d` theorem;
- arbitrary localized two- or three-dimensional catalyst patches rather than
  the exact slab quotient;
- a global GIG-to-Doi universality theorem;
- a uniform interchange of `epsilon -> 0` and `B -> 0`;
- a rigorous a priori/a posteriori SG `C^1` cusp-jet error theorem;
- an exact global modal count on the full half-line; or
- a full positive-`B` `d=3` phase diagram, **provided** the final title and
  abstract restrict the finite-parameter realization to `d=2`.

These are natural follow-up projects. They should not be used as open loops in
the main PRR narrative.

## 6. Minimum acceptable independent-solver and convergence evidence

### 6.1 Mesh and alignment convergence

The held-out 113/129 pair is a confirmation pair, not a continuum sequence.
For the broad family, the minimum defensible post-confirmation sequence is:

1. retain 113 and 129;
2. add at least one even or deliberately shifted/alignment-perturbed mesh to
   expose contact/patch grid-locking; and
3. add one finer mesh beyond 129.

At least three of these levels must lie in a visibly convergent regime. Do not
infer an order from two points across a discontinuous cut-cell contact
indicator. Report raw differences and, only if stable, a conservative
continuum extrapolation.

For the selected trimodal control, cusp, and fold representatives, converge:

- every retained root and its type;
- peak and valley values/ratios;
- three event-basin masses and final survival;
- root residuals and dimensionless curvatures;
- `f_t,f_tt,f_ttt,f_tttt` at the cusp;
- all two-direction allocation mixed jets in `J_cusp`;
- the projected singular values and cusp Jacobian determinant; and
- the remote max--min pair required for trimodality.

All scientific decisions must be margin-aware: estimated discretization error
must be smaller than both a frozen absolute tolerance and a fixed fraction of
the distance to the applicable topology/prominence/mass/rank threshold.

### 6.2 Box/truncation convergence

The intended physical model is the unbounded OU cylinder, whereas the finite-
volume calculation uses reflecting faces. Holding cell widths approximately
fixed, run at minimum:

1. the baseline box;
2. a longitudinal-midpoint enlargement;
3. a relative-longitudinal enlargement; and
4. a combined enlargement.

This small matrix distinguishes the two truncation mechanisms. It is stronger
than enlarging both directions once and being unable to identify a
cancellation. Record killed-state probability in boundary strips and compare
it with the known free OU/Gaussian tails. The cusp/fold coordinates, full jets,
topology, ratios, masses, and survival must all remain inside their frozen
margin-aware tolerances.

If a mathematical truncation bound is proved that directly controls the same
mixed jets and event masses, it can replace part of this matrix. A free-kernel
tail estimate alone cannot replace positive-`B` cusp-jet box checks.

### 6.3 Preferred minimum independent solver: exact off-lattice Doi thinning

The most efficient physically distinct check is an unbounded off-lattice
simulation of the same Doi law:

1. dominate the bounded killing field by a homogeneous rate
   `Lambda >= ||K||_infinity`;
2. draw Poisson candidate times;
3. propagate the free midpoint/relative OU and periodic Brownian coordinates
   exactly between candidates;
4. accept a reaction with probability `K(X_t)/Lambda`; and
5. otherwise continue from the exact Markov state.

Conditional thinning of the pathwise hazard is an independent Feynman--Kac
realization of the unbounded killed process. It uses neither reflecting faces,
the SG flux, cut-cell contact fractions, nor matrix exponentials.

Freeze at least the following controls before simulation:

- one trimodal interior point;
- one representative on each side of each fold branch; and
- the finite-volume cusp location as a validation target, not a geometry-
  refitting seed.

Monte Carlo is not an acceptable validator of fourth time derivatives or the
cusp Jacobian by itself. Those remain the responsibility of the converged
deterministic calculation. The off-lattice solver must independently validate:

- survival on a frozen time grid;
- the three valley-partitioned event masses;
- density contrasts in predeclared peak and valley neighborhoods; and
- the modality change at representative controls.

Choose the trajectory count by a predeclared power calculation. Use
simultaneous confidence bands or held-out/bootstrap uncertainty, and require
the lower confidence bound of each promoted basin mass to exceed its floor and
the peak--valley contrasts to have the claimed signs. A visually similar noisy
histogram is not a pass.

An independent FEM, discontinuous-Galerkin, or spectral method is an equally
acceptable alternative if it uses a genuinely different spatial/time
discretization and independently integrates the true contact geometry. A
second wrapper around the same SG generator is not.

### 6.4 Minimum cross-method agreement rule

For every promoted scalar `x`, report the FV continuum/box estimate
`x_FV +/- E_FV` and the independent estimate `x_ind +/- E_ind`. Require

`|x_FV-x_ind| <= E_FV+E_ind+tau_cross`,

where `tau_cross` is frozen before the independent result is inspected and is
smaller than one quarter of the distance to the nearest scientific threshold.
For topology, both methods must preserve the same ordered max--min structure;
agreement of only an integrated reaction probability is insufficient.

## 7. SEND, HOLD, and redirect standards

### `SEND-2D` — minimum focused PRR package

Mark the paper `SEND-2D` only if all of the following are true:

1. the frozen positive-`B` held-out result passes twice with byte-identical
   artifacts and survives independent numerical audit;
2. the **same broad family** has a finite-`B` allocation cusp, both fold
   branches, full cusp jet/rank, a remote pair, and event-mass-qualified
   representative modality regions;
3. mesh/parity and the box matrix converge every promoted value with margin;
4. a genuinely independent unbounded killed-process method preserves the
   selected topology, survival, and event masses without refitting;
5. the theorem and numerical claims are joined honestly: analytical existence
   is not mislabeled as a quantitative certificate at `B=0.01`;
6. the manuscript is rewritten around one claim spine, with finite-parameter
   evidence explicitly restricted to physical `d=2`;
7. the companion-overlap, metadata, code/data archive, and author approvals are
   complete; and
8. final independent scientific, reproducibility, and rendered-PDF audits have
   no open P0/P1 findings.

Under this route, the physical-`d=3` theorem and exact sphere kernel may remain
as a dimension-correct analytical comparison, with finite-`B` `d=3` declared
future work.

### `SEND-2D/3D` — stronger headline package

Use a title/abstract claiming controlled finite-budget modality in both
dimensions only after all `SEND-2D` gates plus a frozen, converged, positive-
`B`, independently validated physical-`d=3` transition pass. Separate
dimension-specific allocations are allowed, but they must be described as
separate designs under the same conserved-budget principle.

### `HOLD`

Remain on `HOLD` if any of the following is true:

- only the fixed-box positive-`B` point passes;
- cusp/fold allocation jets are missing or nonconvergent;
- odd/even/alignment or box sequences disagree;
- the independent solver changes the topology or pushes a promoted mass/
  valley/rank result across its threshold;
- numerical uncertainty consumes the scientific margin;
- finite-`B` `d=3` is claimed without corresponding evidence; or
- companion-work disclosure or release metadata remain unresolved.

### `REDIRECT`

If the same-family positive-`B` cusp/branches or independent unbounded
topology fail after a frozen, non-refitted test, redirect to a focused
PRE/JCP-style paper on conserved-reactivity reaction-time shape plus the
scoped fixed-finite-mode theorem. Do not use extra GIG scans, the separate G1d
fold, or generic catastrophe terminology to manufacture a PRR-strength
continuum claim.

## 8. Final promotion recommendation

The work is not yet “already sufficient,” even under the optimistic
positive-`B` held-out outcome. It is, however, close enough that a bounded PRR
promotion program is justified. The decisive next step is not a broader
theorem or more result-informed scans. It is one same-family closure:

> broad four-slab `B=0` cusp -> fixed-`B` allocation cusp and two folds ->
> event-mass-qualified trimodal region -> mesh/parity and box limit ->
> independent unbounded killed process.

Complete that chain in physical `d=2`, keep the fixed-finite-`m` and weak-`B`
theorems as the analytical backbone, and scope `d=3` according to the evidence
actually completed. That is the shortest defensible route from the present
working draft to a PRR submission.
