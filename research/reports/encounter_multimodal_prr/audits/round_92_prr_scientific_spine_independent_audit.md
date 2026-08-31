# Round 92: independent PRR scientific-spine audit

Date: 2026-07-14  
Role: read-only scientific strategy audit after a hypothetical low-grid
allocation-cusp pass  
Decision: **CURRENT HOLD; CONDITIONAL SEND-2D; CHOOSE UNBOUNDED OFF-LATTICE
DOI THINNING AS THE INDEPENDENT METHOD**

## 1. Question, boundary, and source snapshot

This audit asks one deliberately narrow question:

> If the frozen low-grid allocation-cusp experiment returns a scientifically
> valid pass, what is the shortest remaining evidence chain that can support a
> focused physical-`d=2` Physical Review Research paper?

It does **not** audit allocation code, manifests, selectors, bytes, or results;
it assumes a future independently accepted low-grid pass only to identify the
next decision. It ran no allocation, finite-volume, PDE, Monte Carlo, plotting,
or manuscript-production calculation. It changed no frozen source or claim
surface. The sole new object is this strategy report.

The scientific reading used the following current snapshots:

| role | path | SHA-256 |
|---|---|---|
| working article | `manuscript/encounter_multimodal_prr.tex` | `1c17be4ac1223fa769166cc13c4b551a1cf7925ae59a61a81021657421305c5b` |
| project status | `README.md` | `024c5d45da89b2e630fe8cbbeb7acf895f7710035da5b9d7152270b940ca07c3` |
| research contract | `notes/research_contract.md` | `fd0340efd28e97142565840c0f32b362f233ae44bf39b500a508ac62f4f9be77` |
| focused SEND-2D blueprint | `notes/prr_focused_spine_rewrite_blueprint.md` | `585ea39754c133afd99c13e552c0ee5bbae2ebb0fc2a5809f15bef4d0ab02009` |
| direct fixed-finite-`d,m` theorem | `notes/direct_physical_multimode_theorem.md` | `2b35d1b1053045220b29975d30f8b3c842d33273ca46de86b8cf7798c26a9c3d` |
| accepted theorem claim-surface attack | `audits/round_91_general_dimension_exact_freeze_independent_attack.md` | `fe6b9e40e6cbb808ca0d4907fa9b0e6eb7e70db383d64ab7b7312ddb9988bded` |
| positive-`B` fixed-control closure | `audits/round_59_positive_b_canonical_result_closure.md` | `c7825396ed44ac50017b599a6a4b1a43f8f0f531db5173f1b88a67fa9011a72f` |
| independent closure re-audit | `audits/round_60_positive_b_closure_independent_reaudit.md` | `ab344365828fa4a7196d36177e84b976225f36753aa82082978df10587f3d557` |
| result-blind Stage-B design | `notes/positive_b_stage_b_validation_design_v5.md` | `136085075ad23fc22a40cf03725c9151f11ff356cff4f6f39e5c5fbb24317ddd` |

The journal-fit standard is taken only from the official APS pages. Physical
Review Research welcomes fundamental, applied, theoretical, experimental,
technical, methodological, interdisciplinary, and emerging work connected to
physics; its acceptance criteria require a high-quality, significant,
authoritative, and substantive addition to the literature. APS also asks for a
manuscript understandable to a broad physics readership and properly
contextualized in the literature. See [PRResearch About](https://journals.aps.org/prresearch/about)
and [Information for Authors](https://journals.aps.org/prresearch/authors).

The implication is important: PRR does not require a computer-assisted proof
of a continuum cusp. It does require a coherent new physics result whose
numerical and analytical evidence supports exactly the language used.

## 2. Scientific spine that is already strong enough

The accepted analytical result is a genuine general mechanism, but with a
precise scope. For every **fixed finite** `d>=2` and **fixed finite** `m`, an
`m`- and epsilon-dependent longitudinal-slab family has at least `m` exact
continuum Doi reaction-time modes after the sequential choices

```text
choose sufficiently small fixed epsilon; then choose 0 < B < B0(epsilon).
```

The proof is pointwise in `d,m`; it is not uniform in dimension or mode count,
does not use one fixed geometry for arbitrary `m`, does not give a numerical
`B0` for the broad four-slab example, does not exclude extra extrema, and does
not guarantee observable event mass in the simultaneous narrow-patch/weak-`B`
limit. Those limitations are strengths when stated plainly: the theorem gives
the general constructive mechanism, while the finite-parameter `d=2` cusp
supplies the physically resolved control law.

The current fixed-control result supplies the second necessary ingredient. At
`B=0.01`, one unchanged broad-four-slab allocation has three event-mass-
qualified maxima on meshes 113 and 129 in one reflected box and one solver
family. It is reproducible and independently reconstructed at its admitted
scope. It is also deliberately fragile enough to make the next validation
non-negotiable: the smallest basin mass is only about `0.0002114` above the
`0.005` floor and the largest valley ratio only about `0.003272` below the
`0.85` ceiling.

A valid low-grid allocation cusp would join these ingredients into the right
PRR hypothesis:

```text
constructive fixed-finite-(d,m) mechanism
  -> weak-B mixed-jet persistence
  -> same broad physical-d=2 family at finite B
  -> allocation cusp, two folds, and observable modal regions.
```

But the last arrow is still a **discovery calculation** until it survives a
different grid/box regime and a genuinely different realization of the killed
process.

## 3. Minimum science still missing after a low-grid cusp pass

Exactly two scientific closures remain. Everything else is either manuscript
work or optional expansion.

### 3.1 Deterministic Stage-B: validate the singularity and its phase portrait

Run the already frozen, no-refit Stage-B program once. Its job is to establish
that the low-grid object is not a parity, alignment, contact-cut-cell, or
reflecting-box artifact. It must preserve, under the predeclared eight
finite-volume configurations and 120 role--configuration rows:

1. one interval-certified allocation cusp in the same broad four-slab family;
2. both fold branches, their ordering, and representative points on the
   one-, two-, and three-maximum regions;
3. the full time/allocation mixed-jet system, nonzero fourth-order time jet,
   projected singular values/rank, and cusp/fold unique-root certificates;
4. the remote maximum--minimum pair needed for the three-maximum region;
5. strict root identity and type, prominence/valley thresholds, event-basin
   masses, survival, curvature, and mass balance at unchanged physical
   controls; and
6. stability under parity/alignment, fine--large continuation, directional box
   enlargements, and the combined enlarged box.

The governing numerical decision is the frozen Stage-B v5 design, not a new
tolerance invented after seeing results. In particular, use its centered
interval-hull FV envelope `E_FV`; require every thresholded quantity to remain
on the passing side with `E_FV <= min(E_abs,d/4)`; enforce its absolute caps
for time, weights, ratios, masses, survival, fourth derivative, singular
values, and curvature; and retain the `1e-6` outward upper bound on boundary-
strip killed-state mass. A pass supports the phrase

> mesh-, alignment-, and box-stable finite-volume numerical allocation cusp.

It does **not** support “proved continuum cusp,” “PDE cusp,” or “global exact
mode count.” The existing Stage-B design correctly keeps all three flags
false. The manuscript should promote the finite-resolution statement, not
silently strengthen it.

### 3.2 Independent killed-process evidence: validate the physical event law

After an independently accepted Stage-B result has frozen the controls,
execute one prepowered off-lattice experiment at exactly

```text
C_MC = {anchor_m3, representative_m1,
        representative_m2, representative_m3},
expected FV maximum counts = (3,1,2,3).
```

No control, support, allocation, time window, basin boundary, trajectory
count, seed namespace, or tolerance may be refitted from Monte Carlo output.
The four additional off-fold controls remain deterministic FV challenges; a
Monte Carlo fold scan is unnecessary.

This is the minimum independent evidence because it directly tests whether the
same unbounded physical law preserves the reader-visible event features at the
anchor and across the representative phase regions. It does not waste Monte
Carlo power trying to estimate fourth derivatives at a cusp.

## 4. Independent-method decision: choose off-lattice Feynman--Kac MC

### 4.1 Why it is the better independent method

The primary solver is a finite-volume killed semigroup with cut-cell contact,
Scharfetter--Gummel transport, a reflected finite box, and matrix-exponential
time evolution. A second deterministic FEM, DG, or spectral solver could
recompute cusp derivatives, but it would still carry spatial discretization,
geometry-integration, finite-domain, and time-propagation choices of the same
general kind. It would be expensive precisely where the existing Stage-B
matrix is already strongest.

The unbounded off-lattice construction removes the dominant shared failure
modes:

| primary FV evidence | independent off-lattice evidence |
|---|---|
| spatial mesh and contact fractions | continuous state and exact contact indicator |
| reflecting finite box | unbounded OU coordinates |
| SG/FV generator | exact free transition between candidate times |
| matrix exponential | pathwise hazard thinning |
| deterministic truncation error | sampling uncertainty with simultaneous bounds |

Thus off-lattice Doi thinning gives more independence per unit of work. It is
the preferred PRR check provided the paper keeps the cusp claim at the honest
finite-resolution level.

Choose a genuinely different deterministic PDE solver only under one of two
conditions:

1. the authors insist that the title/abstract say **continuum/PDE cusp**, in
   which case the present FV plus MC package is insufficient; or
2. a referee specifically requires independent cusp/fold derivatives or rank,
   which event-time Monte Carlo cannot estimate efficiently.

Neither condition belongs to the minimum pre-submission SEND-2D route.

### 4.2 Minimal off-lattice process protocol

For each frozen control, use the exact free quotient process on the unbounded
midpoint and relative-longitudinal coordinates and the periodic transverse
relative coordinate. Let `K(x)` be the same bounded Doi killing field and
choose the frozen homogeneous bound `Lambda=0.35`, already shown to dominate
the intended hazards. Then for every trajectory:

1. draw successive candidate increments from `Exp(Lambda)`;
2. propagate every free OU/Brownian coordinate exactly to the candidate time;
3. evaluate the unsmoothed physical contact indicator and catalyst field;
4. accept killing with probability `K(X_t)/Lambda`, with no clipping; and
5. otherwise continue from that exact Markov state until reaction or `T=100`.

Conditional Poisson thinning is the pathwise Feynman--Kac realization of the
same unbounded killed process. Its relevant numerical errors are floating
point/RNG implementation and finite sampling, not the FV mesh or reflected
box. Use the already frozen SHA-256 counter streams, two disjoint pools, exact-
ID retry/replicate rules, and fail closed if `K>Lambda` is ever observed.

### 4.3 Estimands that do not require density smoothing

For reaction time `tau_i`, estimate survival on the frozen time grid by

```text
S_hat(t) = N^(-1) sum_i 1{tau_i > t}.
```

Use a simultaneous Dvoretzky--Kiefer--Wolfowitz band for the entire survival
curve. With the valley cuts frozen from interval-certified Stage-B roots,
estimate each event-basin mass by its empirical indicator average. For every
predeclared peak or valley window `W`, estimate

```text
p_hat(W) = N^(-1) sum_i 1{tau_i in W}.
```

For adjacent equal-width peak/valley windows of half-width `h`, use the local
average-density contrast

```text
Delta_hat = [p_hat(W_peak)-p_hat(W_valley)]/(2h).
```

These estimands are binomial/multinomial functionals of event times. They need
no kernel density estimate, bandwidth, derivative estimate, visual histogram,
or root finder. This is essential: a noisy KDE should never decide a mode.

The contract's older phrase “independent density comparison below 2 percent
in L1” is not literally established by fixed-window MC. Before release, an
explicit claim-surface rebaseline must either replace that editorial phrase by
the already frozen survival/basin/window containment rule or define a
predeclared finite partition and call the result a **binned** total-variation
comparison, not continuous-density `L1`. Do not introduce a post-result KDE to
manufacture the old number.

### 4.4 Convergence, uncertainty, and cross-method gates

Use the existing global familywise `alpha=0.05` ledger. The design already
allocates 290 atoms/tails and derives ten positive local contrasts from the
fourteen window intervals. Select the first predeclared total trajectory count

```text
N = 200,000, 400,000, ..., 50,000,000
```

whose frozen planning calculation gives joint power at least `0.90`. If none
does, return `HOLD-T2`; do not enlarge `N` after inspecting output.

For every promoted survival value, basin, window, or contrast:

1. each pool separately must meet its fixed precision and common FV-target
   containment rule;
2. the pooled MC interval must be contained within the predeclared FV
   acceptance interval built from `E_FV` and the frozen cross tolerance;
3. every promoted basin's simultaneous lower endpoint must exceed `0.005`;
4. every claimed local peak--valley contrast's lower endpoint must exceed
   zero; and
5. the pool-difference interval must contain zero and satisfy the frozen
   regression precision rule, reported only as a same-generator regression
   diagnostic, not as an equivalence test.

This is stricter and clearer than demanding a similar-looking histogram. It
also handles the current narrow mass and valley margins without pretending
they are high margin.

## 5. What the independent MC can and cannot validate

The separation below must remain visible in the article and data record.

| supported by powered off-lattice MC | not supported by off-lattice MC |
|---|---|
| survival curve at frozen controls | cusp or fold location |
| valley-partitioned event masses | `f_tttt` or allocation mixed jets |
| fixed-window probabilities | projected singular values/rank or cusp determinant |
| positive local peak--valley contrasts | independent root positions/curvatures |
| compatibility with the FV event law | exact or global mode count |
| selected positive event-law features for `m=2,3` controls | absence of a pair at `representative_m1` |
| unbounded-domain check without a spatial mesh | a rigorous FV continuum limit |

In particular, the expected `(3,1,2,3)` FV labels are planning metadata. The
MC contrasts can positively preserve selected peaks and valleys for the
multi-maximum controls, but the empty `m=1` contrast array provides no MC
proof of unimodality. The maximum reader-facing synthesis is therefore:

> a finite-volume numerical cusp stable to mesh, alignment, and box changes,
> with predeclared event-law features at unchanged controls independently
> preserved by an unbounded off-lattice Doi process.

That sentence is scientifically substantial and PRR-suitable. Replacing
“finite-volume numerical” by “continuum/PDE,” or “event-law features” by
“cusp independently verified,” would overclaim.

## 6. Physical `d=3`: keep it supplemental for SEND-2D

The general theorem already makes the analytical mechanism dimension-aware:
its pointwise fixed-finite-`d,m` statement can remain in the main text. The
current exact sphere-contact `B=0` shape uses a separate allocation, has no
killed-process event mass, and is not an independent positive-`B` transition.
It should therefore be placed in Supplemental Material as a dimension-correct
comparison, with positive-`B` `d=3` explicitly left for future work.

A focused `d=2` title, abstract, figures, and conclusion do **not** need a new
positive-`B` `d=3` campaign. A joint `d=2/d=3` finite-budget headline would
need a separate frozen, converged, positive-`B`, independently validated
physical-`d=3` transition and should remain on HOLD.

There is a governance inconsistency to repair later, not by editing frozen
surfaces in this round: the older research contract/README phrase positive-
budget `d=3` as a project-wide submission gate, whereas the focused SEND-2D
blueprint and promotion strategy allow it to remain supplemental. The
recommended resolution at the next authorized claim-surface rebaseline is to
make the route explicit:

```text
SEND-2D: no positive-B d3 gate; exact B=0 d3 comparison in Supplement.
SEND-2D/3D: full positive-B, converged, independent d3 gate required.
```

Until that rebaseline is independently reviewed, the living documents should
not be cited as if they already express one unambiguous release policy.

## 7. PRR decision rule

### CONDITIONAL GO / `SEND-2D`

Scientific GO requires all of the following, with no refit:

1. the low-grid allocation result independently passes its frozen cusp, both-
   fold, rank/nondegeneracy, remote-pair, and representative-region rules;
2. every governing Stage-B v5 deterministic row and uncertainty gate passes,
   preserving the same physical controls and branch identities;
3. the frozen off-lattice experiment reaches its precomputed power and passes
   every simultaneous survival, basin, window, contrast, containment, and pool
   diagnostic rule;
4. the paper uses the finite-resolution claim sentence above and keeps all
   continuum/PDE-cusp, global-count, and MC-cusp flags false;
5. `d=3` remains theorem/supplement context unless a separate complete `d=3`
   program is actually run; and
6. the later authorized manuscript rewrite reconciles the contract/blueprint
   and `L1`/window wording, then passes independent scientific,
   reproducibility, overlap, data-availability, and rendered-PDF review.

With those conditions met, the package has a PRR-level spine: a constructive
general mechanism, a finite-parameter conserved-allocation singularity in a
physical encounter model, observable modal regions, and an independent
unbounded-process validation. It is an authoritative substantive advance,
not merely a numerical parameter scan.

### HOLD

Remain on HOLD if any one of the following occurs:

- only the low-grid cusp passes;
- cusp/fold identity, nondegeneracy, rank, remote topology, or a representative
  event-mass/prominence gate fails on any mandatory Stage-B configuration;
- the parity/alignment/fine--large or directional box envelopes consume the
  scientific margin;
- the powered MC plan is infeasible under the frozen `50,000,000` cap;
- any required MC interval misses the FV acceptance envelope, a mass lower
  bound crosses `0.005`, or a required contrast lower bound crosses zero;
- the paper calls the result a continuum/PDE cusp or says MC verified the
  cusp; or
- a `d=2/d=3` finite-budget claim is made without complete positive-`B` `d=3`
  evidence.

## 8. Stop rule: prevent verification work from becoming the paper

The program now needs closure, not more conceptual branches. Apply this rule:

1. **One deterministic campaign.** Run the frozen Stage-B matrix once,
   including both nominal passes already required by its protocol. An
   operational retry may reproduce only the identical failed unit, but no
   weight, geometry, selector, role, mesh, box, tolerance, or branch may be
   retuned.
2. **One independent attempt.** If Stage-B passes, run the frozen two-pool
   off-lattice protocol once at the frozen powered `N`. No sequential top-up,
   optional stopping, new window, KDE bandwidth, seed replacement, or dropped
   control is admissible.
3. **Hard scientific failure means redirect.** If a mandatory deterministic
   topology/nondegeneracy/margin gate fails, or the powered MC result is
   incompatible with the common target, stop the cusp-centered PRR route and
   write the scoped theorem/fixed-control paper for a more specialized venue.
   A diagnostic calculation may explain the failure but cannot rescue the
   frozen claim.
4. **Power infeasibility is a result.** If no allowed `N` reaches the joint
   power target, do not enlarge the protocol indefinitely. Hold the physical-
   validation claim and redirect or weaken the paper.
5. **A complete pass ends the science campaign.** Move immediately to the
   focused manuscript, figures, archive, and independent release audit. Do not
   add a second deterministic solver, a positive-`B` `d=3` phase diagram,
   uniform-in-`d` theorem, arbitrary patch geometry, or a global root census
   before submission.

The only exception is a later referee request tied to a specific indispensable
claim. Until then, building an independent deterministic PDE solver would add
more shared numerical structure than independent physics evidence.

## 9. Final verdict

The project is **not SEND-2D after a low-grid cusp pass alone**. Its shortest
defensible PRR route is now fixed:

```text
accepted fixed-finite-(d,m) theorem
  + accepted positive-B fixed-control anchor
  + independently accepted low-grid allocation cusp
  + one no-refit deterministic Stage-B convergence/box pass
  + one powered unbounded off-lattice Doi pass
  = focused, honestly finite-resolution SEND-2D candidate.
```

Choose off-lattice Feynman--Kac/Doi thinning, keep `d=3` supplemental, and stop
once those two missing scientific closures pass. This is the most general
publishable explanation already supported by the project without diluting the
paper into an open-ended numerical-engineering program.
