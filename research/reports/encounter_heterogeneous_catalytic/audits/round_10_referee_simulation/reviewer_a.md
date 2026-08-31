# Round 10 independent PRE referee simulation — Reviewer A

**Recommendation: major revision; not acceptable for publication in its present scientific scope.**

**Severity summary:** B0: none. B1: one central scientific-scope blocker. B2:
two substantive but repairable issues. B3: one terminology issue. I found no
evidence of fabricated data, an invalid central finite-matrix calculation, or a
hidden numerical failure.

## Independence and review basis

I read the complete manuscript source and compiled PDF, the relevant analytical
notes, the finite CTMC, Green, 2D, 3D, morphology, provenance, notebook, test,
and Lean sources, and the machine-readable artifacts. I rendered and visually
inspected every page of the final PDF. I did not read the content of the other
Round 10 referee report.

This report is based on the final scientific-source freeze and the canonical
full run `20260711T083125522558Z-62483`:

- TeX SHA-256: `3f831c337ef1fb1764a1a88be62595c79300920d3f069c88d0fbe18c3f9e1269`
- PDF SHA-256: `7800bdeb9f182b8d30eeb50d3f1b0b995370536bc684cce4e313313c0a112022`
- canonical full profile: 16/16 stages returned zero, 90 source files, 100
  outputs, four formal-evidence files, `execution.complete=true`
- PDF: 23 Letter pages, 12 figures, zero missing files, overfull boxes,
  undefined citations, or undefined references in the final compile summary

I use the following severities.

- **B0:** fatal correctness or integrity defect that invalidates the central
  result.
- **B1:** major scientific blocker requiring new analysis or a material change
  of the paper's central claim.
- **B2:** substantive, local, or release-level issue that must be repaired but
  does not by itself invalidate the finite calculations.
- **B3:** editorial, terminology, or presentation issue.

## Referee assessment

The manuscript is unusually careful about its own boundaries. The coordinate
algebra, mass balance, inverse-free Green reduction, finite-matrix identities,
GIG calculus, generic fold normal form, capacity formulas, and finite CTMC
derivatives are correct under the hypotheses stated. The numerical artifacts
are much stronger than a collection of sampled peak plots: they retain channel
fluxes, tails, exact-semigroup derivatives, parameter sensitivities, root
residuals, nondegeneracy, held-out fold sides, and manifests. The Lean package
also correctly presents itself as an algebra-only certificate.

The central difficulty is not a false finite-state calculation. It is the gap
between the paper's spatial/fixed-budget fold narrative and the strongest
evidence that survives changes of grid and budget measure.

## Findings

### B0 — none

I tried to falsify the sign conventions, coordinate transform, Green identity,
splitting solve, fold derivatives, normal-form coefficients, capacity
coefficients, and saved roots. I found no B0 defect. In particular, the final
finite CTMC and finite-lattice roots satisfy the equations and the reported
nondegeneracy conditions at numerical precision.

### B1 — the central spatial fold is not yet discretization-robust, while the robust endpoint result is only an operational resolution transition

The most robust bounded-2D result is M2D-E. It is real and has now survived a
useful budget-measure control:

- all five patterned endpoints have two strict maxima with secondary/primary
  ratios `0.04581–0.08147`;
- state-sum-matched homogeneous endpoints also have two strict maxima, but with
  ratios `0.01023–0.01810`;
- product-control-volume-matched homogeneous endpoints have ratios
  `0.00675–0.01217`, zero two-peak classifier views, and raw canonical labels
  `unimodal/shoulder/unimodal/unimodal/unimodal`;
- therefore every peak-height cutoff in
  `(0.01809905, 0.04580679)` separates all five patterned curves from both
  homogeneous controls.

This establishes a finite-lattice **promotion of an already existing strict
transport maximum into a declared resolved mode**. It does not establish the
creation of a second mathematical maximum, and the manuscript now says so.

The derivative-certified 2D fold is instead supplied by the different M2D-F
family. Each saved odd grid has a genuine nondegenerate finite-state fold, but
the topology and location are not stable:

| budget measure | 9x5 | 11x7 | 13x9 | range |
|---|---:|---:|---:|---:|
| state count, `theta_c` | 0.275373 | 0.013810 | 0.255892 | 0.261563 |
| product control volume, `theta_c` | 0.624441 | 0.240769 | 0.459345 | 0.383672 |

The individual dimensionless fold residuals are below `5e-12`, and all six
Jacobians are nonzero, so this is not a root-accuracy complaint. It is a model
resolution complaint. The budget-measure shifts are `0.203–0.349`. On `12x8`
the continued root is at `theta=-0.061584`, outside the physical path. On
`10x6`, the declared curvature scan and four bounded least-squares starts find
only a positive near miss, `f_t=3.8721e-6`; the source appropriately does not
claim a global no-root proof.

The resolution diagnostics explain the behavior. The M2D-F longitudinal cell
Péclet number of walker 1 is still `3.83–5.75`; the upwind effective diffusion
is therefore roughly `2.92–3.88` times the declared physical diffusion. The
binary contact and catalyst masks span only a few cells and change
nonmonotonically. M2D-E is no closer to a controlled SDE refinement: its walker
1 longitudinal Péclet number decreases only from `9.0` to `4.5`, while the
finest one-cell transverse Péclet numbers are `4.17` and `13.02`.

M2D-T is a valid and attractive **finite-lattice** trimodality example, but it
cannot close this gap. Every patch radius is below the longitudinal grid
spacing, and the channel support counts are `3/3/2`, `5/5/3`, `4/4/3`, and
`18/5/5`. The exact five-root alternation and channel attribution are genuine;
the sequence is nevertheless binary-mask aliasing rather than continuum
refinement. Likewise, the 2D/3D capacity calculations concern separate
translation-invariant mean-time models, and the multidimensional GIG designs
are free-space screening mixtures. Neither transfers the M2D-F fold to a
resolved bounded Doi continuum problem.

This matters for novelty. A targeted primary-literature check found prior work
on static fixed-total-reactivity design, heterogeneous reactive regions,
full first-passage distributions, history-dependent reactivity-induced
bimodality, internal-state gating, and Giuggioli's transport-generated multiple
peaks. I did not find a direct duplicate of the exact phrase “static spatial
fixed-transport, fixed-budget Doi density fold,” so the narrow novelty claim is
plausible. But the novelty then rests almost entirely on M2D-F, precisely the
piece that is parity-, grid-, and measure-sensitive.

Before PRE publication, the authors should choose one of two scientifically
honest routes.

1. **Keep the spatial-Doi fold as the headline.** Add a cell-averaged
   finite-volume/FEM or other controlled discretization of one single physical
   matched family. Refine until the cell Péclet numbers and mask quadrature are
   controlled, include both parity sequences, and show persistence and
   convergence of fold topology, `t_c`, `theta_c`, `f_ttt`, and `f_ttheta`.
   The same family should carry both the endpoint contrast and the derivative
   fold. An independent Robin/radiation calculation would strengthen this
   route but is secondary to obtaining a controlled Doi sequence.
2. **Keep the present evidence.** Retitle and reframe the paper consistently as
   a finite-state/boundary-node lattice mechanism study. Make the finite CTMC
   and finite-lattice theorem-like statements the headline, and present
   capacity and multidimensional GIG results as calibration and design outlook,
   not as support for a general bounded spatial fold.

The current manuscript already contains many of the necessary caveats, which
is commendable, but caveats do not by themselves turn a nonconverged central
construction into a general spatial result.

### B2 — “resolved” labels need a compact threshold-sensitivity presentation distinct from strict extrema

The paper now does a good job of retaining all strict stationary points and of
showing the nonempty M2D-E peak-height interval. That should remain. A referee
or experimental reader still needs one consolidated sensitivity table or
panel for the other classifier coordinates.

My direct reclassification of the archived exact-semigroup series found:

- M2D-E `9x5` has canonical `R_peak=0.05067` against the threshold `0.05`; a
  threshold of `0.06` changes that grid from bimodal to shoulder.
- M2D-F `9x5` at the patterned endpoint has secondary ratio `0.03533` and
  valley ratio `0.92525`, close to the declared `0.03/0.95` boundary; the
  `13x9` secondary ratio is `0.03551`.
- M2D-T remains mathematically three-maxima on all four grids, with minimum raw
  adjacent prominence `0.128` of the primary peak. However, changing only
  `max_r_valley` from `0.80` to `0.79` changes `9x5` from trimodal to bimodal;
  changing only minimum separation widths from `1.00` to `1.05` changes
  `15x11`; changing only minimum lobe mass from `0.01` to `0.025` changes
  `13x9`.

These are not reasons to discard the raw maxima. They are reasons to separate
three statements cleanly: “three simple local maxima,” “three channel-attributed
maxima,” and “three modes resolved by this operational detector.” The first two
are substantially more robust than the third. A small threshold-sensitivity
matrix would make the paper stronger and prevent the 3% choice from carrying
more physical meaning than it has.

### B2 — the scientific full run passes, but the release proof and author-owned metadata are not complete

The fresh canonical full profile passes all 16 stages. The first verify attempt
ran the publication pytest suite and reached 124/125 tests; its sole failure was
the audit-structure gate because Round 8 and Round 10 resolution/report files
had not yet been created. This was not a scientific-test failure, but the
canonical verify profile is therefore not complete at the time of this report,
and its Lean stages did not run in that attempt. The audit structure must be
completed and `verify` rerun to a seven-stage canonical pass.

Separately, the successful full manifest records `dirty=true`, no exact tag,
and `release.start_gate_passed=false`. The manuscript also correctly retains
submission TODOs for a clean tagged transitive rebuild, archival DOI/license,
funding, conflicts, CRediT contributions, and final author metadata. These are
hard submission gates even though they are not scientific counterexamples.

### B3 — preserve the classifier's shoulder category

For the product-control-volume M2D-E homogeneous controls, the canonical labels
are `U/S/U/U/U`, yet the artifact adds the manual umbrella label
`resolved_unimodal` to every row. The TeX discloses that one case is a shoulder,
so there is no hidden result. Still, the clean wording is “no resolved second
peak on any grid (four unimodal, one shoulder),” not “the same
resolved-unimodal call.” This preserves the classifier's own four-category
taxonomy.

## Claim-versus-evidence matrix

| Claim | Evidence I checked | Referee status |
|---|---|---|
| Coordinate transform, diffusion decoupling, midpoint shift, and mass balance | Direct algebra; row-generator checks | Supported under the stated joint-domain qualifications |
| Inverse-free reaction-support Green reduction | Operator algebra; exact finite dark-mode/pole/residue fixture | Supported conditionally; no continuum meromorphic theorem, as stated |
| Fixed-shape two-channel fold and generic `1/2`, `3/2` laws | Independent differentiation and Taylor expansion | Supported |
| Physical fold in the `L=31` CTMC | Exact matrix actions, augmented sensitivity, mass/tail and finite-difference spot checks | Supported for one finite CTMC; minority splitting `8.95e-6` |
| M2D-E fixed-budget endpoint promotion | Five grids; two budget measures; strict roots; tails; common cutoff interval | Supported as an operational finite-lattice resolution transition, not creation of a strict mode |
| M2D-F spatial matched-budget fold | Six accurate odd-grid/measure roots plus even-grid diagnostics | Supported pointwise for the declared finite lattices; not discretization-robust |
| M2D-T bounded trimodality | Five alternating roots, curvature, channel shares, tail checks on four grids | Supported as a finite-lattice example; patches are underresolved and the resolved label is threshold-sensitive |
| 2D logarithmic and 3D Doi-capacity laws | Independent recomputation of saved slopes and reaction-limited controls | Supported for the translation-invariant mean-time solvers only |
| Two-, three-, and four-mode designs in `d=1..4` | Independent wider log scan; `2m-1` alternating roots in all 12 GIG cases | Supported for the declared normalized GIG mixtures; physical bounded-Doi realization is absent |
| Lean formal certificate | Clean temporary `lake build`; four axiom drivers | Supported for 100 algebraic theorems only; not PDE, roots, or convergence |
| Release-ready reproducibility | canonical full passes; release git/metadata gates and canonical verify remain incomplete | Not yet supported |

## Falsification attempts and numerical spot checks

| Attempt | Method | Result |
|---|---|---|
| Break the relative/centre transform | Re-derived inverse, unit Jacobian, cross-diffusion cancellation, and `C_eta-R` shift | No sign or factor error |
| Break mass balance and splitting | Checked generator row sums, `b=-T1`, quadrature/tail closure, and `alpha(-T)^{-1}UK` | Pass; finite CTMC closure `4.0e-15` |
| Break the finite Green interpretation | Recomputed the `4x4` fixture at `s=-2.5` and inspected dark/cancelled modes | Channel residues `(+1/4,-1/4)`, total residue zero, dark mode `-2` |
| Break the CTMC fold | Re-evaluated derivatives and central parameter differences at the saved root | Dimensionless residuals `7.1e-15`, `6.8e-13`; nonzero third derivative/transversality; held-out slopes `0.50095`, `1.50877` |
| Accept a false optimizer success | Challenged the 2D root solver with distant starts and inspected the current gates | Current source checks physical domain, dimensionless residual `<1e-8`, and determinant; distant `11x7` start converged to the certified root |
| Find omitted grid topology | Solved `9x5` and `12x8`; scanned `10x6` curvature branches and bounded least squares | Physical odd-grid root at `9x5`; `12x8` root at negative control; no `10x6` root under the declared bounded search |
| Break the M2D-F continuum budget reference | Recomputed the contact-tube integral and both symmetric boundary circular-segment losses | Exact clipped rate `2.2501572220`; factorized counterfactual differs by `2.1267e-5` relatively |
| Break M2D-E budget matching | Independently constructed four-dimensional product trapezoidal weights and rebuilt the `11x7` control | Weight sum one; budget error `1.39e-17`; raw label shoulder, zero two-peak views, strict ratio `0.007828` |
| Turn M2D-T into a sampling artifact | Rebuilt all 20 roots by direct exponentials, checked curvature and signs around each root, then changed one classifier threshold at a time | Roots and channel order survive; operational trimodal labels change on three grids under small threshold changes |
| Break capacity coefficients | Recomputed 2D and 3D validator summaries | Finest 2D slope ratio `0.984829`; 3D smallest-four ratio `0.998856`; stated finite-grid boundaries are accurate |
| Find extra GIG roots | Used a wider `1e-3` to `10*max(mode)` log scan with 60,001 points | Same `2m-1` alternating roots in all 12 cases; maximum root shift `<9.3e-12` |
| Find hidden formal assumptions | Built in a clean temporary copy and ran all four axiom drivers | 3,109 build jobs completed; 100 theorems; only `propext`, `Classical.choice`, `Quot.sound` |
| Find PDF corruption | Rendered all 23 pages and inspected four contact sheets | No clipping, overlap, broken reference, or unreadable panel |

Representative commands actually used were:

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python3 -m pytest -q -p no:cacheprovider \
  tests/test_encounter_2d_matched_fold.py \
  tests/test_encounter_2d_matched_fold_artifacts.py
# 10 passed

PYTHONDONTWRITEBYTECODE=1 .venv/bin/python3 -m pytest -q -p no:cacheprovider \
  tests/test_encounter_2d_trimodal_artifacts.py
# 5 passed

PYTHONDONTWRITEBYTECODE=1 .venv/bin/python3 -m pytest -q -p no:cacheprovider \
  tests/test_encounter_2d_matched_control_artifacts.py
# 3 passed
```

The canonical pipeline command recorded in the passing manifest was:

```bash
uv run --frozen python \
  research/reports/encounter_heterogeneous_catalytic/code/run_publication_pipeline.py \
  --profile full
```

For the formal layer I copied the Lean sources to a temporary non-OneDrive
directory, reused only the package cache, and ran:

```bash
lake build
lake env lean AxiomsReport.lean
lake env lean EncounterAxioms.lean
lake env lean EncounterContinuumAxioms.lean
lake env lean EncounterDesignAxioms.lean
```

## Items corrected during this referee pass

Several falsification attempts produced real, now-resolved improvements:

- a third physical odd-grid M2D-F fold (`9x5`) and explicit `10x6/12x8`
  topology diagnostics were added;
- the root solver now fails closed on scaled residual and nondegeneracy instead
  of trusting an optimizer's success flag alone;
- M2D-F now uses the correctly boundary-clipped continuum budget reference;
- M2D-E now includes a five-grid product-control-volume homogeneous control and
  explicit cell-Péclet diagnostics;
- M2D-T now records its underresolved patch supports and nonmonotone reactive
  counts;
- stale two-grid text, alt text, notebook summaries, and the final PDF were
  updated; a nested-dictionary notebook failure was fixed and the notebook now
  executes all 18 cells without errors;
- the report-wide source inventory now includes the package initializer and
  the directly used finite-FPT module, while the canonical verify selection
  includes the dedicated FPT, morphology, and provenance tests (16/16 pass in
  my independent preflight).

These fixes materially improve the paper and are why I do not recommend
rejection for correctness. They do not remove the B1 scope/evidence mismatch.

## PRE recommendation and minimum blockers

I recommend **major revision**. The paper is technically serious, transparent,
and potentially publishable in PRE, but the editor should not treat the current
package as a general bounded spatial-fold result.

The minimum scientific condition is either a controlled, same-family spatial
fold refinement or a consistent finite-state/lattice reframing. In either
case, add the compact classifier-sensitivity presentation and preserve the
strict-extremum/resolution distinction. Before submission, complete the audit
resolutions and obtain a passing canonical seven-stage verify proof, then
perform the documented clean-tag release rebuild and supply the author-owned
metadata and archival DOI.
