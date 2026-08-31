# Spatially patterned encounter reactions

This report is the submission-facing workspace for the post-PRR encounter
project.  Its central question is not whether first-passage densities can ever
have more than one peak.  The narrower question is when spatially separated
reaction opportunities change the modality of the *reaction-time* density,
and which parts of that change can be predicted analytically.

## Current result

The repository now supports the following claim chain.

1. A reaction-support Green/Woodbury reduction resolves catalytic channels and
   their Laplace transforms and sensitivities exactly for a finite killed CTMC.
2. An exact finite `4x4` spectral fixture verifies a shared dark mode, a
   coupled negative killed pole of `det(I+GK)`, and two nonzero channel residues
   that cancel in the total flux. It is not a continuum continuation theorem.
3. Applying the classical generalized Descartes rule to a finite reversible
   killed-generator expansion gives a necessary spectral diagnostic: `m`
   interior modes require at least `2m-1` ordered residue sign changes. Full
   decompositions of the 961-state encounter and 2025-state M2D-T production
   generators pass the bimodal/trimodal lower bounds. An exact
   hypoexponential counterexample shows the condition is not sufficient, and
   a rank-one killing model is explicitly bimodal, so channel/support count is
   not a mode bound.
4. The exact Fr\'echet--Duhamel derivative of `f_t` with respect to every
   killing rate is projected onto the fixed-budget tangent space. The resulting
   closed form is the locally optimal infinitesimal redistribution. It agrees
   with an independent convolution kernel, 256 held-out finite differences,
   20,000 random feasible directions, permutation tests, and the saved finite
   encounter-fold transversality.
5. A modality fold is defined in the physical model by
   `f_t = f_tt = 0`, with `f_ttt != 0` and `f_ttheta != 0`; its local critical
   point separation and prominence obey the generic `1/2` and `3/2` laws.
6. The four-grid base artifact is the M2D-C `separated_boundary` branch and is
   classified bimodal on the four declared
   `9x5`--`15x11` grids. The `9x5` case remains `conditional`, rather than
   verified, because its survival at `t=240` is `1.0044e-7`, just above the
   strict `1e-7` tail gate. These are repeated finite-grid evaluations, not a
   controlled continuum-refinement sequence. Its `11x7` arrays are exactly the
   same curve reused by the mechanism-control artifact, not an independent
   replication or a fifth 2D family.
7. In the M2D-E five-grid family, all matched homogeneous sinks
   are resolved-unimodal; the four finer patterned sinks are resolved-bimodal,
   while the coarsest patterned sink is a shoulder.  Both model classes have
   two strict maxima on every grid: the
   homogeneous late maximum is only `1.02%`--`1.81%` of the primary maximum,
   whereas the patterned ratio is `4.43%`--`8.15%`. Thus patterning amplifies a
   transport clock rather than creating a new mathematical extremum. A
   101-cutoff full-classifier sweep preserves these five calls on its recorded
   finite sample. A product-control-volume budget match retains non-bimodal
   homogeneous controls.
8. The separate M2D-F fixed-budget continuation has physical nondegenerate folds on
   the `9x5`, `11x7`, and `13x9` finite lattices and reproduces the local
   `1/2` and `3/2` laws. Their control values are nonmonotone and span `0.262`;
   product-control-volume matching retains all three folds but moves them over
   a `0.384` range. The `12x8` root lies at negative control, and a bounded
   `10x6` search finds only a positive near miss. Its separately reported five-grid
   endpoint audit gives homogeneous resolved-unimodal and patterned
   resolved-bimodal calls on all five grids. No continuum critical value is
   claimed.
9. In the remaining M2D-C controls, a separate uniform-reactivity example is
   bimodal. Therefore spatial
   patterning is a controllable modality mechanism, not a necessary condition.
   Single-far and co-located controls are resolved-unimodal despite shallow
   strict secondary maxima, while four interior two-patch grids are bimodal.
   The `11x7` separated-boundary row here is the shared item-4 branch and is not
   counted again as independent evidence. A descriptive domain-length fit is
   consistent with a first-pass/boundary-return interpretation. Every sweep row
   passes a separate `t=480` tail gate and a sampled analytic-derivative audit
   with no detected late stationary point; the finite scan is not
   interval-exhaustive. Its `Lx=1` row is the same uniform control with a longer
   sampling window, not independent model evidence.
10. The M2D-T obstacle-free reflecting-rectangle Doi model has three strict
   modes on the `9x5`, `11x7`, `13x9`, and `15x11` grids. The classifier
   resolves all three on the three finer grids and calls `9x5` a shoulder.
   Its five detected sign-changing derivative roots alternate
   max/min/max/min/max, and the three
   maxima are respectively dominated by the near, middle, and far patches.
   Every patch radius is below the longitudinal spacing and its reactive-state
   counts are nonmonotone. This is a bounded finite-grid mechanism certificate,
   not an interval-exhaustive root certificate, continuum trimodality theorem,
   or phase boundary.
11. A centre-coordinate sensitivity audit shows that midpoint and
   diffusivity-weighted catalyst locations are different physical sink models.
   Their masks and quantitative densities differ, although both give a
   shoulder on `9x5` and bimodality on the two finer tested grids.
12. Translation-invariant relative-coordinate benchmarks are consistent with the 2D
   logarithmic-capacity and 3D Doi effective-radius laws.  They test the
   reaction-radius discretization; they do not prove a patterned continuum
   fold.
13. A constructive GIG screening law maps prescribed clocks to catalyst
   distances and inverse-peak-height weights.  Analytic-derivative root
   isolation realizes two, three, and four modes in every tested dimension
   `d=1,2,3,4`; this is a multidimensional design result, not yet a bounded
   finite-radius PDE result.

All centre-patterned 2D results above evaluate their declared saved finite
CTMCs using exact finite-state identities and propagation/root solves verified
to reported numerical tolerances. Their deterministic starts are represented by an audited contact-safe
joint law: the original bilinear product is retained when safe; otherwise a
minimum-spread LP followed by a unique closest-product strictly convex QP
preserves both position means while assigning zero initial contact mass.
Persisted cell-Péclet and support-to-spacing diagnostics explicitly
prevent reinterpreting the moderate upwind lattices as a controlled continuum
SDE refinement.

The exact claim boundary and theorem/numerics ledger are in
[`notes/continuum_multid_theory.md`](notes/continuum_multid_theory.md) and the
promoted manuscript. [`notes/manuscript_outline_jcp.md`](notes/manuscript_outline_jcp.md)
is retained as a superseded architecture record.
The bounded finite-grid trimodality certificate and its continuum limitations
are recorded separately in
[`notes/finite_radius_2d_trimodality.md`](notes/finite_radius_2d_trimodality.md).
The midpoint-versus-weighted sensitivity result is in
[`notes/finite_radius_2d_centre_coordinate_sensitivity.md`](notes/finite_radius_2d_centre_coordinate_sensitivity.md).
The initial-law defect, canonical LP/QP repair, adversarial validation, and
resulting claim changes are recorded in
[`notes/contact_safe_initial_distribution_audit.md`](notes/contact_safe_initial_distribution_audit.md).
The finite-only dark-mode/pole/residue certificate is in
[`notes/finite_matrix_green_spectral_audit.md`](notes/finite_matrix_green_spectral_audit.md).
The fixed-budget gradient and spectral zero-count diagnostics, including their
counterexamples, are in
[`notes/modality_susceptibility.md`](notes/modality_susceptibility.md) and
[`notes/spectral_modality_bound.md`](notes/spectral_modality_bound.md).
The refreshed priority search, Luca/Giuggioli boundary, recent Robin/capacity
frontier, and higher-journal gates are in
[`notes/literature_priority_20260713.md`](notes/literature_priority_20260713.md).

## Reproduce

From the repository root, with the project environment activated:

```bash
uv run --frozen python research/reports/encounter_heterogeneous_catalytic/code/run_publication_pipeline.py --profile full
uv run --frozen python research/reports/encounter_heterogeneous_catalytic/code/run_publication_pipeline.py --profile verify
```

`full` regenerates the numerical evidence and figures, including the finite
Green spectral fixture, the four-grid finite-radius multi-clock root/tail audit,
and the centre-coordinate sensitivity control, then independently compiles the
focused main article and the standalone Supplemental Material. `verify` runs the
publication-facing tests and the Lean build.  Both are fail-closed and write
per-stage logs plus
profile-specific execution proofs
`artifacts/data/publication_pipeline.full.manifest.json` and
`publication_pipeline.verify.manifest.json`.  The aggregate
`publication_pipeline.manifest.json` hashes both run records, the current
outputs, formal reports, environment locks, and adversarial-audit ledger.
Each stage records its command, return code, duration, and immutable log hash.
Every stage inherits a fixed `SOURCE_DATE_EPOCH`, `FORCE_SOURCE_DATE=1`, and
`TZ=UTC`, so regenerated vector PDFs do not drift solely through creation-time
metadata.
An `incremental` aggregate is only an inventory snapshot, never execution
proof. `--profile quick` rebuilds the core CTMC, fold, finite 2D, and
matched-control evidence during development.

The exact-tag release protocol is intentionally staged because a successful
build writes generated evidence.  Tag the clean audited source, run `full
--release`, commit/tag its generated artifacts and full proof, run `verify
--release` from that clean artifact tag, then commit/tag the verify proof and
aggregate.  Finally run `code/check_publication_proofs.py --require-clean-tag`
from the clean final tag.  The checker requires the full source tag to be an
ancestor of the verify artifact tag and that tag to be an ancestor of the
final proof tag; all live source/output hashes must still match.

The reader-facing notebook is
`notebooks/encounter_publication_validation.ipynb`.  It reads the archived
artifacts rather than silently recomputing them and checks every number quoted
in its narrative.

## Directory contract

- `code/`: independent generators and the orchestration entry point;
- `notes/`: derivations, scope decisions, literature positioning, and journal
  rationale;
- `artifacts/data/`: machine-readable metrics, series, and child manifests;
- `artifacts/figures/`: vector PDF and review PNG figures;
- `artifacts/logs/`: one-command build logs;
- `manuscript/`: focused PRE-oriented RevTeX main text (the legacy filename is
  retained for artifact continuity), independently compiled standalone
  Supplemental Material, shared bibliography, both PDFs, and the complete
  figure/table accessibility alt-text list required for submission;
- `notebooks/`: executed reader audit;
- `audits/`: the thirteen independent adversarial review rounds and remediation
  ledger.

## Formal verification boundary

The Lean project lives at
`../ring_lazy_jump_ext_rev2/code/formal_lean`.  `FormalLean/Encounter.lean`
formalizes finite-mixture fold and two-hotspot algebra;
`FormalLean/EncounterContinuum.lean` formalizes scalar/componentwise affine
catalytic-coordinate algebra and its one-dimensional contact bound, the scalar
relative/weighted transform, the GIG stationary-point equation, the pure
\(a^{d-2}\) capacity-power algebra (not a capacity theorem or constant), and
finite exponential-mixture derivatives; `FormalLean/EncounterDesign.lean`
formalizes action maps that make the GIG log derivative vanish at a prescribed
time, normalized inverse-height design weights, and the local one-budget
projection/optimal-unit-response theorem in a general real inner-product
design space. It does not formally prove that each prescribed stationary
point is the unique mode. The verify profile checks all four axiom drivers,
the exact theorem partition \(140=80+60\), the
absence of proof placeholders, and the standard-axiom allowlist. Lean does
**not** certify PDE well-posedness, continuum limits,
floating-point roots, grid convergence, or the applicability of the encoded
hypotheses.

## Submission target

For the current finite-state/finite-grid evidence package, the primary target
is *Physical Review E*. *The Journal of Chemical Physics* becomes the preferred
first submission after a converged/independently validated continuum-facing 2D
fold or a sharper chemical-physics application is added. *Physical Review
Research* remains a stretch only after a stronger cross-dimensional theorem or
predictive continuum phase boundary. Current journal metrics and the
unverified status of institution-specific CAS/JCR partitions are recorded in
[`notes/journal_target_20260711.md`](notes/journal_target_20260711.md).
