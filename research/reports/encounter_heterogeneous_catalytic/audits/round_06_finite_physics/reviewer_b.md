# Round 06 Reviewer B: finite-radius 2D/3D physics

Date: 2026-07-11  
Reviewer role: independent Reviewer B  
Scope: reflecting finite-state 2D Doi models, catalytic-coordinate convention,
M2D-E/M2D-C controls, 2D logarithmic capacity, 3D Doi effective radius,
fixed-\(\kappa\) and fixed-\(\chi\) limits, and the associated publication
provenance gates.

## Independence and verdict

I did **not** read `reviewer_a.md`. I inspected the model code, theory notes,
manuscript, machine-readable artifacts, tests, child manifests, legacy
manifest, and publication-pipeline implementation directly. I also performed
read-only calculations that do not rely on the serialized conclusions.

**Final verdict: PASS for the Round-06 finite-physics claim boundary.** There
are no open B0, B1, or B2 scientific findings. The bounded reflecting results
are correctly presented as finite-state mechanism evidence; the torus capacity
calculations are correctly presented as translation-invariant calibrations;
and neither is promoted to a continuum theorem for the centre-patterned model.

One operational postcondition remains outside what this report can certify by
itself: after this file is added, the root agent must refresh
`publication_pipeline.manifest.json`, and before submission it must execute the
real `full` and `verify` profiles so that the two profile-specific execution
proofs exist. The README now explicitly says that an incremental aggregate is
only an inventory snapshot, so no current claim relies on absent execution
proof.

## Severity summary

| Severity | Open | Resolved during review | Disposition |
|---|---:|---:|---|
| B0 | 0 | 1 transient TeX blocker | Missing `\end{equation}` introduced during remediation was fixed; the 21-page manuscript then compiled successfully. |
| B1 | 0 | 1 workflow defect | The legacy manifest previously cross-owned every report figure and was necessarily invalidated by later pipeline stages. It now owns only the three `build_report.py` figure families, and a final refresh stage is present. |
| B2 | 0 | 4 | Strict/resolved wording, finite-\(a\) matching derivation, stale manifest hashes, and full/verify execution-record design were corrected. |
| B3 | 0 | 3 | M2D-C rejection wording, dimensional convention, and hashed gate/environment inventory were corrected. |

## 1. Reflecting CTMC convention and units

### Source audit

The convention is internally consistent:

- `packages/vkcore/src/vkcore/encounter2d.py:13-16` declares a row generator,
  product-state order, and omitted outward jumps.
- `encounter2d.py:341-405` implements
  \[
  q_{x,x+e}=D/h_e^2+\max(v_e,0)/h_e,
  \qquad q_{xx}=-\sum_{y\ne x}q_{xy},
  \]
  with outward moves omitted. This is the continuous-time version of an
  attempted outward step becoming a null event; it is a legitimate discrete
  reflecting walk, not a finite-volume Neumann stencil.
- `encounter2d.py:449-537` constructs
  \(Q_0=Q_1\otimes I+I\otimes Q_2\), subtracts the statewise Doi rate from
  the diagonal, and checks row mass balance.
- `encounter2d.py:564-613` evolves the column probability by
  \(\exp(Q^{\mathsf T}t)p_0\), then computes channel fluxes as the state
  probabilities times the channel-rate matrix. This matches the declared row
  convention.

The manuscript now states the dimensional convention at
`manuscript/encounter_modality_jcp.tex:848-867`: physical
\(D,v,\gamma,\kappa\) have dimensions
\(L^2/T,L/T,T^{-1},T^{-1}\), and the reported numbers are the dimensionless
groups \(DT/L^2,vT/L,\gamma T,\kappa T\). Thus every generator entry has
units \(T^{-1}\), a reaction-time density has units \(T^{-1}\), and the
discrete derivative observables have the expected successive inverse-time
powers.

### Independent numerical checks

On the M2D-E \(11\times7\) grid, \(h_x=0.1\) and \(h_y=1/6\). For walker 1,
an interior midpoint has right/left/up/down rates
\(2.05,0.25,0.09,0.09\), exactly
\(D/h_x^2+v/h_x,D/h_x^2,D/h_y^2,D/h_y^2\). The two single-walker maximum row
errors were \(4.44\times10^{-16}\) and \(3.61\times10^{-16}\). The patterned,
matched-homogeneous, single-far, and coalesced killed models had operator mass
errors between \(2.22\times10^{-15}\) and \(3.55\times10^{-15}\).

No stationary-measure claim is being smuggled into the control. The manuscript
explicitly says that equal node weights define a geometric state sum and, with
drift, are not the CTMC invariant distribution. The equal-budget comparison is
therefore an unweighted geometric counterfactual, not a stationary-exposure
match.

## 2. Midpoint versus diffusivity-weighted coordinate

The theory and implementation agree. With
\[
r=X_1-X_2,
\qquad
R=\frac{D_2X_1+D_1X_2}{D_1+D_2},
\qquad
C_\eta=\eta X_1+(1-\eta)X_2,
\]
one obtains
\[
C_\eta=R+\left(\eta-\frac{D_2}{D_1+D_2}\right)r.
\]
In \((r,C_\eta)\), the mixed second-order coefficient is
\(2[\eta D_1-(1-\eta)D_2]\), so the unique noise-decoupling choice is
\(\eta=D_2/(D_1+D_2)\). For M2D-E this is \(8/33=0.242424\ldots\), whereas
the declared physical catalyst coordinate is the midpoint \(\eta=1/2\).

Anchors are `notes/continuum_multid_theory.md:66-180`,
`encounter2d.py:449-464`, and
`code/validate_2d_centre_coordinate.py:56-81,404-538`.

The artifact correctly reports a finite-grid sensitivity rather than an
equivalence claim:

- patterned labels change `bimodal -> shoulder` on \(9\times5\);
- both coordinates are patterned-bimodal on \(11\times7\) and
  \(13\times9\);
- all six separately rematched homogeneous endpoints are resolved-unimodal;
- every homogeneous endpoint nevertheless has two strict maxima, with the
  secondary/primary ratio between 1.257% and 1.905%;
- principal patch-mask Jaccard distances range from 0.0769 to 0.2295.

This supports only the stated conclusion: the catalytic coordinate is an
observable model choice, and agreement on two finer finite grids is not a
continuum invariance theorem.

## 3. M2D-E: strict roots versus the resolved 3% classification

The central causal statement is now correct: patterning **promotes** a
subthreshold transport clock; it does not create the mathematical existence of
the second maximum. Both endpoints have a strict max-min-max pattern on all
five grids.

The exact-semigroup sign-changing root audit on \(0\le t\le80\) gives:

| Grid | homogeneous strict secondary/primary | patterned strict secondary/primary | multiplicative uplift | patterned valley/weaker peak |
|---|---:|---:|---:|---:|
| 9x5 | 0.017532 | 0.045807 | 2.61 | 0.6783 |
| 11x7 | 0.014372 | 0.063851 | 4.44 | 0.4583 |
| 13x9 | 0.018099 | 0.081475 | 4.50 | 0.3082 |
| 15x11 | 0.017157 | 0.075435 | 4.40 | 0.2440 |
| 17x13 | 0.010229 | 0.076260 | 7.46 | 0.2304 |

The canonical morphology classifier is more than a naked root counter. Its
gates include 3% relative height, 1.5% relative prominence, 1% lobe mass, 5%
\(R_{\rm peak}\), \(R_{\rm valley}\le0.80\), separation, and 50%
scale persistence (`packages/vkcore/src/vkcore/morphology.py:28-69,807-871`).
Every homogeneous strict secondary maximum already fails the 3% height gate.
Every patterned endpoint passes the full multiscale classifier; its canonical
\(R_{\rm peak}\) ranges from 0.05067 to 0.09057, and 128--155 of 155 views
contain two accepted peaks.

At \(11\times7\), I independently reconstructed both killed generators and
reevaluated \(f,f_t,f_{tt}\) at all six stored roots. The root residuals were
at roundoff; curvature signs alternated max/min/max. Patterned and homogeneous
state-sum killing were both 369.0, with relative mismatch
\(3.08\times10^{-16}\). Across all grids the stored relative mismatch is at
most \(4.11\times10^{-16}\); no post-window maxima were found and the reported
tails are below the declared limits.

The root scan is correctly described as detection of sign-changing roots. It
is not presented as an interval certificate excluding tangencies or arbitrarily
narrow even root pairs.

## 4. M2D-C shallow-valley and adverse controls

The single-far and coalesced-far controls are not strictly unimodal. Independent
reconstruction confirms:

| Control | strict secondary/primary | valley/weaker peak | depth relative to weaker peak | two-peak scale views |
|---|---:|---:|---:|---:|
| single_far | 0.480321 | 0.959679 | 0.040321 | 26/155 |
| coalesced_far | 0.483706 | 0.956994 | 0.043006 | 34/155 |

They are nevertheless **resolved-unimodal**: the shallow valley exceeds the
allowed 0.80 ratio and the second peak lacks 50% scale persistence. Its
standalone relative-global prominence is not the failing gate. The manuscript
now says exactly this at `encounter_modality_jcp.tex:1110-1124`, and the focused
artifact test gates the distinction.

The separated-boundary and uniform-reactivity examples are resolved-bimodal.
The latter is the necessary adverse control: transport alone supplies a
first-pass and a boundary-return clock. Therefore the evidence rules out both
"two labels are sufficient" and "spatial patterning is necessary". The
supported statement is the narrower M2D-E result about resolution-class
promotion at fixed discrete geometric budget.

## 5. Exact finite-\(a\) midpoint tube match

For the unit square and midpoint coordinate, set
\(C=(x_1+x_2)/2\) and \(r=x_1-x_2\). The absolute Jacobian is one and, for
\(0\le a\le1\), the admissible centre area at fixed
\(r=(r_x,r_y)\) is \((1-|r_x|)(1-|r_y|)\). Hence
\[
V_T(a)
=\int_{|r|\le a}(1-|r_x|)(1-|r_y|)\,dr
=\pi a^2-\frac83a^3+\frac12a^4.
\]

If every catalyst disk has clearance at least \(a/2\) from every square side,
its centre section is untruncated for all admissible \(r\). The continuum
geometric-budget match is therefore
\[
\bar\kappa_h(a)
=\frac{\pi a^2\,[\pi\sum_j\kappa_j\rho_j^2]}{V_T(a)}.
\]
For M2D-E, the smallest patch clearance is 0.07, which exceeds
\(a/2=0.065\), and the formula gives
\(\bar\kappa_h=2.169402270805009\).

I independently enumerated ordered boundary-node pairs by relative lattice
displacement, without building the pair generator. The state-sum rates were:

| Grid | matched rate |
|---|---:|
| 9x5 | 1.108000 |
| 11x7 | 1.700461 |
| 13x9 | 1.797597 |
| 15x11 | 1.838710 |
| 17x13 | 1.849069 |
| 25x19 | 1.958583 |
| 49x37 | 2.065418 |
| 81x61 | 2.090229 |
| 161x121 | 2.132693 |

The independent refinement tends toward 2.169402. The five dynamics grids are
thus exact within-grid counterfactuals but are not a converged continuum
budget. This derivation and boundary are now explicit in
`encounter_modality_jcp.tex:923-943` and
`notes/continuum_multid_theory.md:910-930`.

## 6. Two-dimensional logarithmic-capacity calibration

`code/validate_2d_capacity.py` uses an exact translation-invariant pair-to-
relative quotient on a flat two-torus, a cell-centred periodic Laplacian, and a
subcell-averaged Doi disk. This is not the reflecting M2D-E model.

At fixed \(\kappa=1\), the reaction-limited products
\(\kappa\pi a^2\langle T\rangle\) decrease from 1.008313 at \(a=0.12\) to
1.001246 at \(a=0.02\), consistent with
\(\langle T\rangle\sim A/(\kappa\pi a^2)\).

At fixed \(\chi=\kappa a^2/D_r=1\), I independently refit the stored means
against \(\log(1/a)\). The slope ratios to \(A/(2\pi D_r)\) are
0.949695, 0.978987, 0.983883, and 0.984829 on grids
161, 241, 321, and 401; the finest \(R^2\) is 0.9999607. The finest smallest
radius is resolved by 8.02 cells. This is strong numerical calibration of the
universal logarithmic slope, with a remaining 1.52% finite-grid/finite-radius
slope discrepancy; it is not an exact coefficient measurement or a proof for
the heterogeneous reflecting problem.

## 7. Three-dimensional Doi capacity

The exact quotient is valid because both the periodic geometry and the reaction
rule are translation invariant. It reduces two walkers to a relative process
with \(D_r=D_1+D_2=1\). The continuum Doi sphere has
\[
a_{\rm eff}
=a\left(1-\frac{\tanh\sqrt\chi}{\sqrt\chi}\right),
\qquad \chi=\frac{\kappa a^2}{D_r},
\]
and capture rate \(4\pi D_r a_{\rm eff}\). The weak-reaction expansion
\(a_{\rm eff}=\kappa a^3/(3D_r)+O(a^5)\) gives the fixed-\(\kappa\)
reaction-volume law
\[
\langle T\rangle\sim\frac{V}{\kappa(4\pi a^3/3)}.
\]

I independently recomputed every \(\chi\), every effective radius, and the
smallest-four linear fit against \(1/a_{\rm eff}\). The fit gives
\[
\frac{\widehat{\text{slope}}}{V/(4\pi D_r)}
=0.998856129859,
\quad R^2=0.999999777,
\quad \max|\text{residual}|=0.001027.
\]
The fixed-\(\kappa\) scaled means decrease from 1.007862 to 1.000423.
At fixed radius \(a=0.09\), the two finest grid means differ by 0.0651% and
the finest sphere-volume error is \(1.09\times10^{-5}\).

Crucially, the shrinking-radius sequence uses
\(a/h=7.38,7.41,7.505,7.63,7.645,7.605\). It couples the radius and grid
limits. The artifact, note, figure caption, tests, and manuscript all now say
that 0.114% slope agreement is **continuum-compatible finite-grid evidence**, not
a separated or certified double-limit coefficient. The separately refined
fixed-radius series does not remove that limitation for the shrinking-radius
fit.

## 8. Evidence-layer separation

| Statement | Correct evidence layer | What is not established |
|---|---|---|
| M2D-E and M2D-C modality labels, strict roots, tails, and channel fluxes | finite-state reflecting boundary-node CTMC | cell-averaged continuum persistence or a unique continuum fold |
| Midpoint versus weighted masks | finite-grid one-factor sensitivity | equivalence or inequivalence of continuum modality classes |
| \(D_1+D_2\) torus quotient | exact translation-invariant identity | quotient with centre-dependent patches or reflecting product boundaries |
| 2D log slope and 3D effective-radius slope | translation-invariant numerical calibration | full centre-patterned density or modality convergence |
| 2D logarithmic and 3D Newtonian/Doi formulas | continuum local/matched-asymptotic benchmark under their stated hypotheses | a theorem uniform near the bounded heterogeneous fold |

This separation is present in the abstract, results, capacity section, and
limitations (`encounter_modality_jcp.tex:48-80,145-185,1211-1335,1477-1480`).

## 9. Provenance and workflow audit

### Final non-aggregate state

I recomputed SHA-256 values for `inputs`, `source_files`, and `outputs` in the
legacy manifest plus all 13 non-aggregate child manifests. Result:

- 14 manifests checked;
- 0 missing paths;
- 0 hash mismatches.

The manuscript compile record reports 21 pages, 12 figures, 836,308 bytes, and
zero missing files, overfull boxes, undefined citations, or undefined
references. `pdftotext` confirms that the unit convention, finite-\(a\) formula,
2.169402271 reference, strict/resolved caveat, and M2D-C persistence/valley
wording are present in the compiled PDF.

### Workflow defects found and remediated

1. **Legacy cross-ownership (B1, resolved).** `build_report.py` formerly globbed
   all report figures into `artifacts/manifest.json`, so later full-profile
   stages necessarily invalidated it. It now hashes only its three owned figure
   stems, and `legacy_manifest_refresh` is the last full-profile stage.
2. **Profile overwrite (B2, resolved).** Full and verify execution records now
   go to `publication_pipeline.full.manifest.json` and
   `publication_pipeline.verify.manifest.json`; the aggregate hashes both rather
   than erasing the full record during verification.
3. **Mutable log evidence (B2, resolved).** Every stage result records log size
   and SHA-256. The aggregate may track the current logs, while the profile run
   retains the immutable per-stage log digest.
4. **Coverage gaps (B2/B3, resolved).** The source inventory now includes audit
   Markdown, `pyproject.toml`, `uv.lock`, and
   `tests/test_research_audit_artifacts.py` in addition to the scientific
   sources and Lean files.
5. **Formal fail-closed gate (checked, no fresh Lean build claimed here).** The
   static integrity payload reports 100 theorems (46 legacy + 54 encounter), no
   forbidden proof tokens, four complete axiom reports, and only
   `propext`, `Classical.choice`, and `Quot.sound`. Pipeline code treats
   `sorryAx`, `declaration uses 'sorry'`, missing theorem rows, extra theorem
   rows, and non-allowlisted axioms as failures. I did not start another live
   Lean build while a separate Round-07 build was using the shared cache; the
   fresh live build belongs to the verify-profile/final gate.

The current incremental aggregate is expected to become stale when this report
is written. It must be refreshed after this file; this is deliberate ordering,
not a passed hash claim.

## 10. Commands actually executed

Focused read-only scientific and provenance tests:

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -q -p no:cacheprovider \
  tests/test_encounter_2d.py \
  tests/test_encounter_2d_artifacts.py \
  tests/test_encounter_2d_mechanisms_artifacts.py \
  tests/test_encounter_2d_matched_control_artifacts.py \
  tests/test_encounter_2d_centre_coordinate_artifacts.py \
  tests/test_encounter_2d_capacity_artifacts.py \
  tests/test_encounter_3d.py \
  tests/test_encounter_3d_artifacts.py \
  tests/test_research_audit_artifacts.py::test_publication_artifact_manifests_hash_sources_data_and_vector_figures \
  tests/test_encounter_publication_pipeline.py::test_publication_pipeline_has_unique_core_and_full_stages \
  tests/test_encounter_publication_pipeline.py::test_formal_integrity_gate_is_complete_and_fail_closed
```

Result: **37 passed**.

Earlier in the same independent audit, before workflow remediation, the
nine-file focused suite returned **38 passed**. The difference is only the
selected test-node list, not a regression.

Manuscript/PDF checks:

```bash
jq '.' research/reports/encounter_heterogeneous_catalytic/artifacts/data/manuscript_compile.json
pdfinfo research/reports/encounter_heterogeneous_catalytic/manuscript/encounter_modality_jcp.pdf
pdftotext research/reports/encounter_heterogeneous_catalytic/manuscript/encounter_modality_jcp.pdf - | \
  rg -n '2\.169402271|dimensionless groups|resolved-unimodal|valley-depth'
```

The independent scientific recomputations used current source operators and
the archived JSON values, not manuscript table transcription. In particular,
the capacity slopes were refit with `numpy.linalg.lstsq`, and the finite-\(a\)
grid sequence was obtained by enumerating every admissible ordered relative
lattice displacement and counting midpoint-patch membership.

## Required root-agent handoff

After this report exists:

1. refresh `publication_pipeline.manifest.json` and verify every listed source,
   formal report, profile run, and output hash;
2. retain the present finite-state/translation-invariant/continuum distinction
   in the Round-06 resolution;
3. before submission, execute the real `full` followed by `verify` profiles and
   require both profile-run records to have nonzero stage counts and zero return
   codes.

Subject to those mechanical postconditions, Round 06 is closed **PASS**.
