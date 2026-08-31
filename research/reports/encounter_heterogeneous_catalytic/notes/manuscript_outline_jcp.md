# JCP manuscript architecture: patterned encounter channels and modality folds

Status: **historical writing blueprint, superseded by
`manuscript/encounter_modality_jcp.tex`**. The promoted manuscript, current
artifact notes, and audit resolutions are authoritative. This file retains the
architecture that led to the paper and must not override later model-convention
or finite-grid trimodality results. In particular, its five-grid matched and
four-grid trimodality wording predates the contact-safe initial-law repair and
is retained only as historical drafting context; current classifications are
in the promoted manuscript and
`notes/contact_safe_initial_distribution_audit.md`.

## 1. Answer-first paper identity

### Preferred title

**Channel selection and modality folds in spatially patterned encounter
reactions**

### More explicit alternative

**From catalytic encounter channels to modality folds: Green-function theory
and finite-radius validation**

The preferred title is shorter and keeps the result, rather than the method, in
the foreground.  Neither title claims that patterned reactivity is necessary
for bimodality, that the fold has already been proved in the continuum, or that
the work is the first study of multimodal first-passage distributions.

### One-sentence answer

For two mobile reactants, spatially separated reaction opportunities select
distinct encounter streams whose channel weights and shapes can cross a
computable modality fold; the repository establishes that statement exactly
for a finite killed CTMC and realizes the mechanism on finite-radius,
obstacle-free two-dimensional grids, while leaving uniform continuum fold
persistence as an explicit open obligation.

### Abstract architecture

The abstract should make seven moves, in this order.

1. **Problem.**  First-encounter laws and heterogeneous partial reactions are
   well developed separately, but they do not by themselves determine when a
   reaction-time density changes modality.
2. **Model.**  Introduce two independently moving particles that react inside a
   finite contact tube only where a declared affine coordinate
   (C_\eta=\eta X_1+(1-\eta)X_2) lies in a catalytic patch. The promoted
   bounded 2D model uses the midpoint; the diffusivity-weighted coordinate is
   the special free-space GIG screening convention.
3. **Exact structure.**  State the reaction-support Green reduction, the
   channel-resolved flux/splitting representation, and the exact two-channel
   fold and generic square-root normal form.
4. **Finite CTMC result.**  Say that direct matrix-exponential derivatives and
   an augmented sensitivity equation locate a nondegenerate fold in a physical
   reactivity ratio; quote the derivative residuals and the held-out exponents,
   not only a sampled curve.
5. **Two-dimensional result.**  Say that finite-radius Doi simulations retain
   resolved early/late modes across grid families, including a strictly
   interior far patch, and that an equal-integrated-killing homogeneous control
   is resolved-unimodal for the selected matched family while retaining a
   strict subthreshold secondary maximum.
6. **Dimensional calibration.**  Report the translation-invariant 2D
   logarithmic-capacity and 3D effective-radius benchmarks as discretization
   calibration, not as a proof of the patterned fold in those limits.
7. **Boundary.**  End by calling patterned reactivity a controllable modality
   mechanism, not a universal necessary condition; explicitly label the GIG
   channel law as a screening asymptotic without a uniform remainder.

### Provisional abstract (claim-safe draft)

First-encounter distributions and imperfect reactions in confinement are well
studied, yet a predictive boundary between uni- and multimodal reaction times
is generally unavailable when reactivity is spatially patterned.  We consider
two mobile reactants that can react within a finite contact radius only at
selected positions of a declared affine encounter location.  A
reaction-support Green operator gives channel-resolved fluxes and
sensitivities, while elimination of the channel weight yields an exact
two-channel modality-fold condition and its generic square-root normal form.
For a finite independent-clock killed Markov chain, exact matrix-exponential
derivatives locate a nondegenerate fold under variation of a physical
reactivity ratio; held-out continuation points recover critical-point
separation and prominence exponents \(0.501\) and \(1.509\), respectively.
Obstacle-free two-dimensional Doi calculations exhibit resolved early and late
reaction channels over multiple grids, including an interior far catalyst.  In
a five-grid ablation with the same discrete integrated killing measure, the
patterned model is resolved-bimodal whereas the homogeneous model is
resolved-unimodal; a strict subthreshold homogeneous secondary maximum is
retained. Separate
translation-invariant calculations reproduce logarithmic-capacity scaling in
two dimensions and the Doi effective-radius law in three dimensions.  These
results identify spatial reaction-channel selection as a computable route to
modality changes; they do not assert that heterogeneous reactivity is necessary
for bimodality or that the finite-state fold is already a proved continuum
limit.

The numerical values in this draft must be regenerated from a clean tagged
commit immediately before submission.  If the physical fold is replaced by a
fold with appreciably larger minority-channel weight, update the abstract
rather than preserving the current numbers.

## 2. Main-text logical contract

The paper should have one main theorem-and-evidence chain:

1. spatial geometry defines reaction channels;
2. the restricted Green operator computes their weights, time transforms, and
   sensitivities;
3. the channel mixture changes modality at a fold satisfying exact derivative
   conditions;
4. a physical reactivity parameter crosses such a fold in the finite CTMC;
5. finite-radius 2D models realize the same early/late selection mechanism and
   pass targeted spatial-pattern controls;
6. capacity calculations calibrate the finite-radius discretization in 2D and
   3D without being used as a substitute for a continuum fold proof.

The main text should not become a catalogue of all repository calculations.
The synchronous discrete chain is the robust discovery family; the
independent-clock CTMC is the exact fold model; the finite-radius Doi model is
the physical-dimensional realization.  Their time and rate parameters are not
interchangeable, and the manuscript must not describe the CTMC as a calibrated
continuous-time limit of the synchronous chain.

## 3. Section map

### I. Introduction: the missing modality boundary

- Motivate reaction time, rather than first contact alone, as the chemical
  observable.
- Separate established ingredients: confined encounter laws, imperfect
  reaction, heterogeneous patches, two-channel FPTs, and multimodal FPTs.
- State the narrower contribution: a physical-control continuation of the
  modality fold plus channel-resolved finite-radius validation.
- End with a bullet-free contribution paragraph whose claims match the ledger
  in Section 6 below.

### II. Patterned finite-radius encounter model

- Define \(X_i(t)\), the joint Fokker--Planck equation, reflecting boundary
  currents, and the Doi sink in the declared (C_\eta)-coordinate.
- Derive the relative coordinate
  \(r=X_1-X_2\) and the diffusivity-weighted centre
  \(R=(D_2X_1+D_1X_2)/(D_1+D_2)\).
- State (C_\eta=R+(\eta-D_2/(D_1+D_2))r), the midpoint contact-radius
  bound, and the distinction between the physical midpoint model and the
  diffusion-decoupling GIG coordinate.
- State exactly where diffusion decouples and where domain boundaries or
  nonconstant drift re-couple the coordinates.
- Define channel fluxes \(f_j(t)\), survival \(S(t)\), splitting probabilities,
  and the mass-balance identity.
- Give the Robin alternative only to define the future matching obligation;
  do not imply that it has already been numerically solved here.

### III. Reaction-support Green reduction and sensitivities

- Present \(\mathcal T=\mathcal L_0-\Gamma^*\mathsf K\Gamma\) and the restricted
  Green operator
  \(\mathcal G(s)=\Gamma(s-\mathcal L_0)^{-1}\Gamma^*\).
- Derive the volume-reaction resolvent identity and the finite-hotspot
  Woodbury specialization.
- Explain zero-mode cancellation versus the stable killed solve for splitting
  probabilities.
- State the exact finite-matrix parameter sensitivity and time derivatives.
- Add an explicit pole/numerator/residue warning: a zero of the restricted
  determinant is not automatically an observable time-domain mode, and dark
  modes must be checked in the full generator.

### IV. Geometry-to-channel laws and modality calculus

- Derive the free-motion relative/centre GIG screening law
  \(g(t)\propto t^{-p}\exp(-A/t-Bt)\), its normalization, and its mode.
- State the patch-localization dependence of \(p\); do not present
  \(p=(d+3)/2\) as universal.
- Derive the fixed-shape fold determinant and admissible weight.
- Move immediately to the physically relevant conditions
  \(f_t=f_{tt}=0\), \(f_{ttt}\ne0\), and \(f_{t\theta}\ne0\).
- Derive the \(1/2\) critical-point-separation and \(3/2\) prominence laws.
- Keep cusp/trimodality out of the headline.  A short outlook sentence can
  point to the three-channel simplex conditions in the Supplement.

### V. Exact physical fold in the finite CTMC

- Define the \(L=31\) independent-clock generator and
  \(\theta=\log(\kappa_{\rm near}/\kappa_{\rm far})\).
- Show that changing \(\theta\) changes both the killed dynamics and the
  observable; this is not a freely varied mixture weight.
- Report the fold at \(t_*=37.0749586402\) and
  \(\theta_*=-9.6753635853\), with
  \(\kappa_{\rm far}=0.9162907319\) and
  \(\kappa_{\rm near}=5.755410148\times10^{-5}\).
- Report dimensionless residuals \(7.1\times10^{-15}\) and
  \(6.8\times10^{-13}\), nonzero dimensionless third derivative \(69.94\), and
  transversality \(-0.1962\).
- Report held-out slopes \(0.50095\) and \(1.50877\); state that continuation
  points were not used to locate the root.
- Disclose that the near-channel splitting probability at the current fold is
  only \(8.95\times10^{-6}\).  This makes the fold mathematically valid but
  potentially difficult to observe.  Before submission, search for a second
  physical path with a larger minority-channel weight; otherwise frame this
  fold as a mechanism certificate rather than an experimentally balanced
  two-peak example.
- Use the \(L=31,41,61\) CTMC family and the \(L=31,41,61,81\) synchronous
  family as robustness/scaling context, not as proof of a common continuum
  limit.

### VI. Finite-radius two-dimensional realization and controls

- Introduce the obstacle-free reflecting rectangle, finite Doi contact radius,
  unequal longitudinal transport, and smooth transverse confinement.
- Show the four-grid M2D-C separated-boundary branch: early modes
  \(0.7\)--\(1.2\), late modes \(14.2\)--\(18.6\), and no later extrema on the
  audited horizon. Three grids pass the strict \(10^{-7}\) tail gate at
  \(t=240\); the \(9\times5\) survival is \(1.0044\times10^{-7}\) and remains
  conditional. Its \(11\times7\) curve is reused by the control artifact and
  is not independent evidence.
- Show the four-grid M2D-C interior-patch family.  The patch has positive geometric
  clearance \(0.07\), and all grids are classified bimodal, but paths may still
  feel the reflecting wall; call it a non-touching interior-patch control, not
  a boundary-free theorem.
- Center the M2D-E causal comparison on the five-grid matched endpoint ablation. The
  patterned and homogeneous models have equal sums of statewise killing rates
  on the same discrete encounter tube to \(4.2\times10^{-16}\) relative error.
  four finer patterned cases are resolved-bimodal, the coarse patterned case is
  a shoulder with a retained strict maximum, and homogeneous cases are
  resolved-unimodal on all five grids; strict subthreshold maxima are retained.
  Call this an **equal-integrated-killing finite-grid control**, not a
  universal proof that patterning is necessary or an M2D-E fold.
- Present M2D-F separately: its homogeneous/patterned endpoint classes are
  resolved-unimodal/resolved-bimodal on all five grids, while three finite grids
  contain nondegenerate folds. The nonmonotone \(0.262\) state-sum range and
  budget-measure sensitivity block a continuum critical value.
- Include the apparently adverse M2D-C control: another uniform-reactivity
  choice is itself bimodal. Its domain-length scaling is consistent with a
  first-pass/boundary-return interpretation, not a pathwise decomposition.
  This prevents a false necessity statement.
- Report the domain-length late-clock scaling separately: the fitted late-peak
  slope times the slow drift is \(0.983\), while the early peak remains near
  one. The fit uses the \(0\)--\(160\) shape window; retain the separate
  derivative and tail audit through \(t=480\), and do not call the finite scan
  interval-exhaustive.

### VII. Capacity-calibrated dimensional extension

- For the translation-invariant 2D torus, explain the exact quotient to the
  relative coordinate and the fixed-\(\chi=\kappa a^2/D_r\) logarithmic law.
- Report the finest-grid fitted log-slope ratio \(0.9848\), \(R^2=0.99996\),
  and the fixed-\(\kappa\) reaction-limited scaled means \(1.001\)--\(1.008\).
- For the translation-invariant 3D torus, derive
  \(a_{\rm eff}=a[1-\tanh(\sqrt\chi)/\sqrt\chi]\).
- Report the smallest-four inverse-effective-radius slope error \(0.114\%\),
  the finest-grid pair difference \(0.065\%\), and the smallest-radius
  fixed-\(\kappa\) reaction-limit error \(0.042\%\).
- Put most 3D data in the Supplement unless the full centre-patterned 3D model
  is added.  These benchmarks are consistent with the dimensional
  reaction-radius scaling;
  they do not establish a 3D patterned modality fold.

### VIII. Discussion: mechanism, scope, and next theorem

- State that transport supplies candidate clocks and patterned reactivity selects and
  reweights them; either ingredient can sometimes produce multiple time
  scales.
- Explain why the physical fold is a stronger object than observing two peaks:
  it supplies a codimension-one boundary, transversality, and local scaling.
- State the continuum theorem still needed: channel approximations and their
  first two derivatives must be uniform in a parameter neighborhood containing
  the fold.
- End with the general program: restricted Green operators turn geometry into
  channel laws, and catastrophe conditions turn channel laws into modality
  boundaries.

## 4. Main figures and tables

### Figure 1 — Model and channel mechanism (new composite)

Panels: (a) two walkers, contact tube, relative/centre coordinates; (b) near
and far centre patches; (c) early chase and late transport paths; (d) schematic
fold showing one critical point versus three.  This is the only wholly new main
figure required.

### Figure 2 — Discovery family and clock decomposition

Source:
`artifacts/figures/catalytic_encounter_family.pdf` and
`artifacts/figures/catalytic_encounter_clock_check.pdf`.

Show channel-resolved densities, fixed-local-geometry size scaling, and the
separate synchronous/Poissonized/independent-clock labels.  Do not overlay them
as if they shared calibrated time units.

### Figure 3 — GIG screening and exact physical fold

Source: `artifacts/figures/gig_fold_validation.pdf`.

Required panels: GIG versus exact channel modes; fold root and local critical
points; held-out \(1/2\) separation slope; held-out \(3/2\) prominence slope.
Add the minority-channel splitting weight to the caption.

### Figure 4 — Two-dimensional finite-radius mechanism and ablation

Sources:
`artifacts/figures/finite_radius_2d_validation.pdf`,
`finite_radius_2d_mechanism_controls.pdf`, and
`finite_radius_2d_matched_homogeneous.pdf`.

The main composite should prioritize: a fine-grid channel decomposition, the
non-touching interior far patch, and patterned versus matched homogeneous
density on several grids.  Move the remaining control curves to the
Supplement.

### Figure 5 — Dimensional capacity calibration

Sources:
`artifacts/figures/finite_radius_2d_capacity_scaling.pdf` and
`finite_radius_3d_capacity_validation.pdf`.

Show theoretical slope lines and convergence residuals.  Caption the exact
translation-invariant relative-coordinate quotient and the fact that these are
mean-time benchmarks, not modality calculations.

### Table I — Statement/evidence taxonomy

Columns: statement; exact identity/theorem; finite numerical evidence;
continuum conjecture; formalization status.  This table should prevent the
reader from needing to infer which layer a sentence belongs to.

### Table II — Mechanism controls

Rows: separated boundary patches, single far patch, coalesced patches,
uniform-reactivity adverse control, non-touching interior patch, and matched
homogeneous ablation.  Columns: spatial rule, transport rule, grid family,
classification, positive scale views, tail certificate, allowed inference.

## 5. Exact novelty paragraph and prior-art relationship

### Paste-ready novelty paragraph

Exact lattice propagators, encounter observables, heterogeneous transmission
locations, and multi-target reductions in bounded environments are established
in the work of Giuggioli and co-workers
\cite{giuggioli2013encounter,giuggioli2020exact,giuggioliSarvaharman2022transmission,sarvaharmanGiuggioli2023particle,giuggioliEtAl2024multitarget};
the present study should therefore be read as an extension of that encounter
program, not as a new Green-function or multi-target formalism.  Le Vot
*et al.* derived full first-encounter laws for two diffusing particles in one-,
two-, and three-dimensional confinement
\cite{levot2020firstencounter,levot2022firstencounter}, while Grebenkov and
co-workers developed spectral, capacity, and matched-asymptotic descriptions
of imperfect and spatially heterogeneous reactivity
\cite{grebenkov2019spectral,grebenkovWard2026planar,grebenkovWard2026spherical}.
Disorder-induced bimodal first-passage distributions are also known
\cite{holehouseRedner2024disordered}.  Our narrower contribution is to connect
these ingredients at the level of **reaction-time modality**: a
reaction-support Green reduction resolves spatial encounter channels; exact
time and physical-parameter derivatives continue a nondegenerate modality fold
in a killed CTMC; and finite-radius two-dimensional calculations test the same
channel-selection mechanism with interior-patch and equal-integrated-killing
controls.  We make no claim that bimodality, heterogeneous reactivity,
Green-function reduction, or higher-dimensional encounter distributions are
new, and the finite-grid calculations are not presented as a proof of a
continuum fold.

### Additional nearest-neighbor positioning

- Godec and Metzler already establish direct/indirect two-channel FPT kinetics
  \cite{godecMetzler2016proximity,godecMetzler2017twochannel}; novelty cannot be
  “two time scales” or “two-channel diffusion.”
- Lindsay, Spoonmore, and Tzou compute full 2D narrow-capture densities and
  short-time peaks for multiple traps
  \cite{lindsaySpoonmoreTzou2016hybrid}; novelty cannot be “full 2D FPT
  density” or “multiple small traps.”
- Woods and Wales connect rare-event FPT structure to competing kinetic traps
  in transition networks \cite{woodsWales2024rare}; the distinction here is a
  mobile-reactant encounter manifold, a spatial reaction pattern, and a
  continued physical modality boundary.
- Guérin *et al.* establish universal kinetics of imperfect reactions in
  confinement \cite{guerinEtAl2021universal}; the present claim is a modality
  boundary generated by resolved spatial channels, not a new universal
  imperfect-reaction law.
- Doi, Isaacson, and Chapman--Erban--Isaacson supply the volume-reaction,
  convergent discretization, generalized small-target, and reactive-boundary
  foundations
  \cite{doi1976stochastic,isaacson2009rdme,isaacson2013convergent,isaacsonMauroNewby2016uniform,chapmanErbanIsaacson2016reactive};
  none of those model correspondences should be described as new here.

## 6. Claim-to-artifact ledger

| ID | Proposed manuscript statement | Evidence and exact source | Allowed wording now | Promotion blocker |
|---|---|---|---|---|
| C1 | Relative/centre diffusion decouples for scalar diffusivities with the weighted centre | `notes/continuum_multid_theory.md`, Sec. 2 | Exact coordinate identity under stated hypotheses | Write transformed no-flux boundary carefully; do not infer bounded-domain independence |
| C2 | Doi channel fluxes obey mass balance | `notes/continuum_multid_theory.md`, Sec. 3; operator errors in all 2D JSON files | Exact PDE identity plus finite-grid row-balance validation | Add a manuscript derivation and distinguish exact semigroup mass from trapezoidal time quadrature |
| C3 | Reaction-support Green/Woodbury reduction computes hotspot response | `notes/theory.md`; `notes/continuum_multid_theory.md`, Sec. 4; shared CTMC implementation | Exact finite-matrix identity; conditional continuum volume-operator identity | Publish full-resolvent, derivative, zero-mode, dark-mode, and residue audit |
| C4 | The two-channel fold equation and square-root normal form are exact | `notes/gig_fold_derivation.md`; `gig_fold_summary.json` | Exact algebra/normal-form implication under listed nondegeneracy assumptions | Keep model-specific existence numerical unless separately proved |
| C5 | A physical reactivity path crosses a nondegenerate finite CTMC fold | `gig_fold_summary.json`; `gig_fold_continuation.csv`; `gig_fold_convergence.csv`; `gig_fold_validation.pdf` | Validated finite-state result with exact matrix-exponential derivatives | Seek a fold with larger minority weight; complete precision/root-isolation audit |
| C6 | The synchronous discovery family has robust, resolved bimodality and large-distance trends | `summary.json`; `finite_size.csv`; `perturbation_audit.csv`; `catalytic_encounter_family.pdf` | Four finite sizes and 37/40 perturbations; descriptive fits | No asymptotic theorem; three perturbations are shoulder/unimodal; do not merge clocks with CTMC |
| C7 | The M2D-C separated-boundary branch has finite-grid bimodality | `finite_radius_2d_metrics.json`; `finite_radius_2d_validation.pdf` | Four-grid obstacle-free Doi evidence; three grids pass the tail gate and 9x5 is conditional | The 11x7 control curve is the same model, not independent evidence; more refinement and an independent discretization are needed |
| C8 | The M2D-C far patch need not touch the wall in the selected finite model | `finite_radius_2d_interior_metrics.json`; `finite_radius_2d_mechanism_controls.pdf` | Non-touching interior-patch positive on four grids | Clearance is only 0.07; add enlarged/periodic or farther-interior controls before “boundary independent” wording |
| C9-E | M2D-E patterning amplifies resolved modality relative to a matched homogeneous endpoint | `finite_radius_2d_matched_control.json`; `finite_radius_2d_matched_homogeneous.pdf` | Four finer patterned endpoints are resolved-bimodal, the coarse one is a shoulder, and all five homogeneous endpoints are resolved-unimodal; strict subthreshold maxima are retained | Endpoint audit only; no M2D-E fold or continuum boundary; matching is not every trajectory-level hazard |
| C9-F | M2D-F has finite-grid matched-budget folds and endpoint contrasts | `finite_radius_2d_fold_metrics.json`; `finite_radius_2d_fold_validation.pdf` | Three nondegenerate folds plus five homogeneous-resolved-unimodal/patterned-resolved-bimodal endpoint contrasts | Critical controls are nonmonotone and budget-measure-sensitive; no continuum critical value |
| C10 | Patterning is not necessary for every bimodal case | `finite_radius_2d_control_metrics.json`, `uniform_reactivity` row; `finite_radius_2d_domain_scaling.json` | The unit-domain uniform-rate M2D-C control is bimodal; domain scaling is consistent with a first-pass/boundary-return interpretation | Scaling is descriptive and not a pathwise decomposition or interval-exhaustive root proof |
| C11 | 2D finite-radius discretization is consistent with logarithmic-capacity scaling | `finite_radius_2d_capacity_metrics.json`; child manifest; capacity figure | Translation-invariant relative-coordinate mean-time benchmark; finest slope ratio 0.9848 | Not a centre-patterned fold; no Doi--Robin matching yet |
| C12 | 3D finite-radius discretization is consistent with the Doi effective-radius law | `finite_radius_3d_capacity_metrics.json`; `notes/finite_radius_3d_capacity.md`; child manifest; 3D figure | Translation-invariant relative-coordinate mean-time benchmark with stated errors | No full six-dimensional centre-patterned calculation or 3D modality result |
| C13 | GIG laws predict channel clocks | `gig_fold_summary.json`; `gig_channel_parameters.csv`; `notes/gig_fold_derivation.md` | Screening approximation; continuous derivative-root mode errors 17.6% early and 8.1% late in the canonical comparison | Derive a mode-window remainder and derivative errors before calling it an asymptotic theorem |

Child manifests remain the authoritative generator-level provenance for each
numerical family. The publication pipeline now builds transitive source/output
inventories, immutable attempt manifests, and an aggregate proof across the
GIG, 2D, 3D, notebook, manuscript, and formal layers. A submission release must
still run from a clean commit at an exact tag, refresh both full and verify
proofs, and supply the author-owned submission metadata.

## 7. Limitations that must appear in the paper

1. The current GIG law has no uniform remainder over a mode-containing time
   window and is not a global reflected-path expansion.
2. Continuum Green identities require operator-domain hypotheses; the exact
   implementation evidence is finite-dimensional.
3. The physical fold is exact for one finite CTMC, not yet uniform in lattice
   spacing, reaction radius, or domain size.
4. The current fold's minority splitting probability is \(8.95\times10^{-6}\),
   limiting practical observability and making a larger-weight fold highly
   desirable.
5. The reflecting 2D solver is a boundary-node, nearest-neighbour upwind lattice
   CTMC with binary masks, not a cell-centred finite-volume method. Grid
   families are moderate and no independent Robin solver has yet been matched.
6. A non-touching interior catalyst does not prove that reflecting boundaries
   are dynamically irrelevant; the late stream may still visit the wall.
7. Equal integrated killing is one defensible homogeneous match, not the only
   one.  A second uniform-reactivity choice is bimodal, so heterogeneous
   reactivity is not universally necessary.
8. The 2D and 3D capacity calculations exploit translation invariance and
   validate mean reaction times.  They do not establish full
   centre-heterogeneous channel densities or folds.
9. The four-size synchronous fits are descriptive; they do not prove the
   proposed \(O(L)\), \(O(\sqrt L)\), or exponential-valley asymptotics.
10. One bounded midpoint-Doi family has finite-grid trimodality on four grids,
    but no cell-averaged continuum trimodal region, converged cusp, or
    general-(d) modality theorem is established.
11. Morphology labels depend on a declared multiscale classifier.  The raw
    derivative roots, prominences, tail horizon, and threshold sensitivity must
    accompany each label.
12. Any Lean proof verifies only its encoded algebraic implication.  It does
    not verify PDE regularity, continuum limits, floating-point computation, or
    the scientific applicability of assumptions.

## 8. Supplement map

### Supplement A — Model conventions and exact identities

- arrival/reaction order for the synchronous chain;
- row-versus-column generator conventions;
- relative/centre Jacobian, drifts, diffusion, and transformed boundaries;
- Doi and Robin mass balance.

### Supplement B — Restricted Green operator

- volume-sink resolvent derivation;
- finite hotspot determinant and explicit two-site inverse;
- zero-mode cancellation and stable killed solve;
- pole/numerator/residue and dark-mode audit;
- parameter sensitivity identities and finite-difference cross-check.

### Supplement C — GIG and catastrophe algebra

- GIG normalization, zero-drift limit, modes, and derivatives;
- fixed-shape fold elimination and admissible weights;
- physical fold normal form and held-out exponent fits;
- cusp/simplex formulas clearly marked as future trimodality machinery.

### Supplement D — Discrete and CTMC discovery families

- full \(L=31,41,61,81\) tables;
- 40-point perturbation audit, including the three non-bimodal cases;
- Poissonization quality and independent-clock tail audit;
- explanation of why these are robustness relations rather than a calibrated
  synchronous-to-CTMC limit.

### Supplement E — Two-dimensional finite-radius solver

- stencil, upwinding, reflecting rows, bilinear initialization, and exact
  statewise killing;
- grid geometry and reactive-state counts;
- all boundary, interior, one-patch, coalesced, uniform, and matched-control
  curves;
- classifier sensitivity and post-window root search;
- complete mass/tail table.

### Supplement F — Capacity calibration in 2D and 3D

- cell-averaged targets and subcell quadrature;
- fixed-\(\chi\) and fixed-\(\kappa\) protocols;
- 2D logarithmic fits for every grid;
- 3D effective-radius derivation, PCG/FFT solver, grid/radius convergence, and
  finite-volume correction.

### Supplement G — Formalization coverage

- theorem-to-Lean source map;
- `lake build` command and toolchain hash;
- explicit axiom report;
- a table of analytical claims not formalized.

### Supplement H — Reproducibility and artifact provenance

- clean-commit command ledger;
- environment lock and package versions;
- child and transitive top-level manifests;
- all CSV/JSON schemas, tolerances, random seeds, and SHA-256 hashes;
- notebook or script that regenerates every manuscript number and panel.

## 9. Writing prohibitions and required qualifiers

Do not write:

- “first observation/theory of bimodal encounter times”;
- “heterogeneity is necessary for bimodality”;
- “the Green determinant gives the time-domain modes”;
- “the GIG law is exact for the confined channel”;
- “the 2D/3D continuum limit is proved”;
- “the interior patch removes all boundary effects”;
- “Lean verifies the physical model or numerics.”

Prefer:

- “a physical-control modality fold in the stated finite CTMC”;
- “finite-radius 2D evidence across the stated grid family”;
- “equal-integrated-killing matched control”;
- “non-touching interior-patch control”;
- “capacity-calibrated translation-invariant benchmark”;
- “GIG screening approximation”;
- “conditional continuum identity under the stated operator hypotheses.”

## 10. JCP submission gate

The outline is JCP-shaped because it unifies reaction kinetics, Green-operator
analysis, and finite-radius molecular encounter models.  Promotion to a JCP
submission draft should require all of the following:

1. a clean, transitive, one-command artifact build;
2. exact Green/sensitivity/residue validation in the manuscript model;
3. a tail-wide root-isolation and precision audit of the physical fold;
4. either a larger-minority-weight physical fold or explicit observability
   analysis of the current fold;
5. the matched homogeneous and interior controls retained without selective
   omission of the adverse uniform-reactivity result;
6. a Doi--Robin comparison or a prominently justified Doi-only scope;
7. no continuum-fold wording unless a uniform derivative-level convergence or
   remainder argument has actually been completed;
8. a refreshed bibliography and novelty search at submission time;
9. a theorem/formalization coverage table with no numerical result described as
   formally proved;
10. a final journal-style adversarial review of every headline sentence against
    the claim-to-artifact ledger above.
