# Round 01, reviewer A: model definitions and conventions

Date: 2026-07-11  
Verdict: **fail; one B0 submission blocker**  
Audited working-tree base: `3531353a515160b09899199a9257e7455a654b22`

The encounter report and the new `vkcore.encounter*` modules were untracked in
the audited working tree, and the wider tree was already heavily dirty.  The
hash above is therefore a base commit, not a complete immutable snapshot.  All
line anchors below refer to the working tree inspected on the stated date.

Severity follows `audits/README.md`: B0 blocks the affected submission claim or
artifact; B1 requires a material revision; B2 is a bounded correction or
required caveat; B3 is optional polish.

## Executive result

The continuum coordinate algebra, generator drift signs, row/column
propagation, and mass/flux identities are internally consistent.  The main 2D
evidence, however, is not generated for the model stated in the abstract and
equations.  The paper defines catalytic patches in the diffusivity-weighted
centre

\[
R=(D_2X_1+D_1X_2)/(D_1+D_2),
\]

whereas the shared 2D builder hard-codes the arithmetic midpoint
`0.5 * (X1 + X2)`.  The 2D experiments use `D1 != D2`, so these are different
reaction fields.  An independent reconstruction with the stated weighted
centre changes the `9x5` patterned endpoint from the reported **bimodal** class
to **shoulder** under the same morphology configuration.  Consequently the
five-grid endpoint statement, the 2D fold artifacts, the notebook, figures,
and manuscript cannot ship as evidence for the stated weighted-centre model
without regeneration.

## Findings

### F1 — B0: every centre-patterned 2D calculation uses the wrong centre coordinate

**Claim and implementation anchors**

- The abstract says reaction occurs at selected positions of the
  diffusivity-weighted encounter centre
  (`manuscript/encounter_modality_jcp.tex:48-54`).
- The Doi field is explicitly `K_{a,j}(R,r)`
  (`manuscript/encounter_modality_jcp.tex:250-257`), and the paper defines
  `R=(D2 X1 + D1 X2)/(D1+D2)`
  (`manuscript/encounter_modality_jcp.tex:280-303`).  The conceptual schematic
  repeats the same definition (`code/plot_model_schematic.py:50-56`).
- The principal 2D family uses unequal diffusivities `D1=0.0025` and
  `D2=0.0008` (`manuscript/encounter_modality_jcp.tex:721-736`; also
  `code/validate_2d_matched_homogeneous.py:51-68`).
- The only centre used by the shared builder is instead
  `centre = 0.5 * (first_position + coordinates[second_state])`
  (`packages/vkcore/src/vkcore/encounter2d.py:471-486`).  Its API accepts two
  generators but no diffusivities or centre weights
  (`packages/vkcore/src/vkcore/encounter2d.py:440-447`), so callers cannot
  request the manuscript coordinate.
- The patterned endpoint, fold, original finite-radius family, and mechanism
  controls all route through this builder
  (`code/validate_2d_matched_homogeneous.py:140-180`,
  `code/validate_2d_matched_fold.py:133-188`,
  `code/validate_2d_finite_radius.py:74-90`, and
  `code/validate_2d_mechanisms.py:97-109`).

**Independent counterexample and scale of the mismatch**

For the main start `(X1,X2)=((0.10,0.50),(0.35,0.50))`, the implemented
midpoint is `(0.225,0.50)`, while the stated weighted centre is
`(0.2893939394,0.50)`, a displacement of `0.0643939394`.  For the fold-family
start `((0,0.5),(0.28,0.5))`, the displacement is `0.0721212121`.

Reconstructing the patch masks with the stated weighted centre gave:

| family/grid | channel | midpoint states | weighted states | symmetric difference | Jaccard |
|---|---:|---:|---:|---:|---:|
| endpoint `9x5` | near | 7 | 9 | 2 | 0.778 |
| endpoint `9x5` | far | 9 | 10 | 1 | 0.900 |
| endpoint `11x7` | near | 18 | 20 | 2 | 0.900 |
| endpoint `11x7` | far | 24 | 26 | 2 | 0.923 |
| endpoint `13x9` | near | 55 | 53 | 14 | 0.770 |
| endpoint `13x9` | far | 63 | 61 | 10 | 0.851 |
| fold `11x7` | near/far | 34 / 40 | 32 / 40 | 6 / 4 | 0.833 / 0.905 |
| fold `13x9` | near/far | 109 / 137 | 117 / 131 | 28 / 36 | 0.780 / 0.763 |

I then rebuilt the principal patterned and separately budget-matched
homogeneous operators using the weighted mask, without changing transport,
starts, time grid, or morphology thresholds.  Results were:

| grid | convention | patterned class / peaks | homogeneous class / peak | patterned tail at `t=80` |
|---|---|---|---|---:|
| `9x5` | midpoint (production) | bimodal / `1.1, 17.9` | unimodal / `0.9` | 0.04117 |
| `9x5` | weighted reconstruction | **shoulder / `1.2`** | unimodal / `0.5` | 0.00312 |
| `11x7` | weighted reconstruction | bimodal / `1.4, 19.5` | unimodal / `1.0` | 0.02336 |
| `13x9` | weighted reconstruction | bimodal / `1.5, 20.7` | unimodal / `1.1` | 0.01352 |

The weighted `9x5` tail is below the classifier's 1% lobe-mass threshold, so
unpropagated mass after `t=80` cannot supply a qualifying second lobe.  This is
already a counterexample to “all five patterned grids are classified bimodal”
for the stated model (`manuscript/encounter_modality_jcp.tex:760-777`).  The
audit reconstruction is diagnostic, not a replacement publication artifact;
the weighted-centre fold itself was not recomputed.

**Required resolution**

1. Make the centre convention an explicit, tested model parameter.  For this
   manuscript, pass `D1,D2` (or normalized weights) to the builder and compute
   the stated weighted centre.  Add an unequal-diffusivity unit test that would
   fail under the midpoint.
2. Regenerate every centre-patterned 2D artifact, matched budget, fold,
   mechanism control, notebook result, figure, manifest, and PDF.  Record the
   coordinate convention and weights in each model manifest.
3. Re-audit all five endpoint classifications and the fold continuation.  The
   current fold coordinates and cross-grid shift are properties of the
   midpoint model, not yet of the stated model.
4. The alternative is to declare the arithmetic centre as the physical model,
   but then Eqs. (coordinates)--(diffusion-decoupling), the abstract, schematic,
   and GIG interpretation must be changed; with `D1 != D2`, arithmetic-centre
   and relative diffusion contain a mixed second-order term.  A text-only
   substitution is therefore not a valid fix.

### F2 — B1: the main reflecting 2D grid is a boundary-node lattice CTMC, not the stated cell-centred finite-volume scheme

The manuscript calls each one-particle operator a “conservative finite-volume
CTMC” (`manuscript/encounter_modality_jcp.tex:712-719`).  The implementation's
docstring calls `RectangularGrid2D` a “Cell-centre grid including both physical
boundaries” (`packages/vkcore/src/vkcore/encounter2d.py:26-29`), but its nodes
are `0,h,...,L`, with `h=L/(n-1)`
(`packages/vkcore/src/vkcore/encounter2d.py:45-75`).  These are boundary nodes,
not ordinary cell centres.

The generator uses equal state masses, rates `D/h^2`, and simply omits outward
jumps (`packages/vkcore/src/vkcore/encounter2d.py:333-398`).  This is an
internally valid conservative reflecting **lattice CTMC**.  It is not the
standard half-control-volume finite-volume discretization: if boundary nodes
represented half cells, the inward diffusive rate would be `2D/h^2` and the
physical mass weights would differ at edges/corners.  In an executed `5x5`
check with `D=0.0025`, the implemented boundary diffusive rate was `0.04 =
D/h^2`; the corresponding half-cell FV rate is `0.08`.

The same main builder applies binary node masks for both contact and patches
(`packages/vkcore/src/vkcore/encounter2d.py:471-491`).  By contrast, the
translation-invariant 2D capacity solver explicitly uses true cell centres and
cell-averaged disk fractions to avoid staircase changes
(`packages/vkcore/src/vkcore/encounter2d.py:85-137,181-225`), and the 3D solver
does the same (`packages/vkcore/src/vkcore/encounter3d.py:40-89,160-220`).

This does not invalidate the finite lattice CTMC as a discrete model: row sums,
drift signs, and killing balance all pass.  It does mean that the continuum/FV
interpretation, boundary accuracy, and refinement order asserted for the main
2D evidence are not established, especially on the moderate grids for which
the fold is already non-converged.

**Required resolution:** either (a) rename the method throughout as a
boundary-node upwind lattice/finite-difference CTMC and state that no spatial
order is claimed, or (b) implement a documented FV scheme with cell-centred or
vertex-centred control volumes, boundary volume weights, consistent no-flux
rates, and cell-averaged contact/patch intersections.  In either case, add a
manufactured-solution or weak-generator convergence test and regenerate the
affected results if the operator or masks change.

### F3 — B1: the advertised interior control changes parameter family and is not a one-factor control of the principal model

The interior-control paragraph specifies only that the far patch is moved to
`(0.75,0.50)` with radius `0.18`
(`manuscript/encounter_modality_jcp.tex:859-870`).  The associated script
actually uses a separate family with near patch `(0.28,0.50)`, radius `0.12`,
rate `0.20`, and far rate `4.00`
(`code/validate_2d_mechanisms.py:52-68`).  Those are not the principal matched
family's near patch `(0.25,0.50)`, radius `0.18`, rate `0.50`, and far rate
`15.00` (`code/validate_2d_matched_homogeneous.py:51-68`).

“Moving the far patch” is accurate only relative to the earlier boundary-far
pilot, whose hidden baseline uses the same near patch and a far patch at
`(0.90,0.50)`, radius `0.20`, rate `4.00`
(`code/validate_2d_finite_radius.py:38-55`).  A reader of the manuscript cannot
recover that reference family and can easily read the paragraph as an ablation
of the principal family.  Relative to the principal paper-facing family, the
near-patch centre, near radius, both reaction rates, and far-patch geometry all
change.  The resulting positive example therefore cannot be used as a
one-factor test that moving the principal far patch into the interior preserves
bimodality.

**Required resolution:** give a compact table for the endpoint, fold, and
mechanism-control families, explicitly call the interior result a third
positive-example family, and remove one-factor/transfer language.  If the
intended causal claim is that the principal result survives removal of boundary
contact, rerun a genuine control that keeps transport, starts, contact radius,
near patch, rates, and far radius fixed and changes only the far-patch centre.

### F4 — B2: the multidimensional GIG spatial mapping silently requires zero relative drift

The general formula is

\[
B=u^2/(4D_r)+|v_c|^2/(4D_c)
\]

(`manuscript/encounter_modality_jcp.tex:458-490`).  The reference construction
then sets `D1=D2=1/2`, `ell=1`, and `|v_c|=0.1` and states “one has `B=0.01`”
without specifying `u` (`manuscript/encounter_modality_jcp.tex:1048-1064`).
The validator likewise fixes `B=0.01` but has no relative-drift parameter
(`code/validate_multid_gig_design.py:1-14,44-48`).

For those diffusivities, `Dr=1` and `Dc=1/4`, hence
`B=u^2/4 + 0.01`.  The stated mapping is true only when `u=0`.  The remaining
units are consistent: `A` has units of time, `B` inverse time, the prescribed
`m_j` is a time, and `|z_j-R0|=sqrt(A_j-1/4)` follows numerically because
`4Dc=1` in the chosen units.

**Required resolution:** add `u=0` (equivalently equal particle drifts) to the
reference mapping, script model specification, figure caption or parameter
table, and artifact manifest.  If nonzero relative drift is intended, replace
`B` and all derived distances and weights accordingly.

### F5 — B2: the synchronous model omits its time-zero conditioning convention

The manuscript correctly gives the arrival-then-react operators and first
reported flux `f_j(n+1)=alpha Q^n B e_j`
(`manuscript/encounter_modality_jcp.tex:590-608`), but it does not say what
happens when the initial state is already catalytic.  The reference module
does: the supplied initial law is live **after** a time-zero reaction check and
the first reported flux is at step one
(`packages/vkcore/src/vkcore/encounter.py:3-20,565-577`).

An executed zero-motion example starting on a catalytic state with `rho=0.6`
reports mass `0.6` at `n=1`; an unconditioned initial law would instead also
require a `0.6` atom at `n=0`.  The production discovery starts away from both
catalytic states (`code/build_report.py:78-115`), so this omission does not
change the saved discovery curves.

**Required resolution:** add one sentence after Eq. (discrete-channels):
“`alpha` denotes live mass conditioned on surviving any time-zero reaction
check; no `n=0` atom is included.”

## Checks that passed or were explicitly qualified

| Topic | Falsification attempt and result |
|---|---|
| Coordinate inverse/Jacobian | Random 2D vectors with `D1=0.0025,D2=0.0008` gave maximum inverse error `5.55e-16`, determinant `1.0`, `Dr=0.0033`, `Dc=0.000606060606...`, and transformed diffusion error `1.08e-19`.  The algebra in `notes/continuum_multid_theory.md:68-143` and the manuscript is correct. |
| Drift signs | On an interior `5x5` state, applying the row generator to coordinate observables gave `Gx=+0.1800000000000001` and `Gy=-0.3749999999999998`, matching the specified physical drifts `+0.18` and `-0.375`.  The upwind signs in `encounter2d.py:333-389` are correct. |
| Row/column convention | For a random law on a small killed product chain, `p exp(Tt)` and `expm_multiply(T.T*t,p)` agreed to `1.73e-17`.  Dense row propagation (`encounter.py:675-733`), sparse column-state propagation (`encounter2d.py:544-580`), and fold observable actions (`code/validate_gig_fold.py:298-303`) are consistent. |
| Fold sensitivity orientation | The augmented system `[T.T,0; T_theta.T,T.T]` in `code/validate_gig_fold.py:335-350` and `code/validate_2d_matched_fold.py:231-250` is the correct column-state sensitivity system.  The splitting solve `(-T).T occupation = initial` at `validate_gig_fold.py:355-357` is also consistent with the row convention. |
| Mass and flux | A random-state check gave `dS/dt + f = 0.0`; the product operator balance error was `2.78e-16`.  The construction identity in `encounter2d.py:427-431,493-516` and flux evaluation in `encounter2d.py:570-592` are correct. |
| Reflection convention | The code consistently uses null outward attempts / omitted outward jumps (`encounter.py:176-207`; `encounter2d.py:10-13,379-389`).  This is a valid discrete reflecting convention, distinct from bounce reflection.  The continuum-discretization naming issue is F2, not a row-sum failure. |
| Discrete versus CTMC clock | The paper explicitly says Poissonized synchronous and independent-clock CTMC models are robustness checks, not a calibrated limit, and forbids exchanging rates and times (`manuscript/encounter_modality_jcp.tex:636-647`).  `build_report.py:83-115,151-196` keeps their operators and clocks separate. |
| Doi support boundary | The continuum uses `|r|<a` (`manuscript/encounter_modality_jcp.tex:250-256`; `notes/continuum_multid_theory.md:151-164`), while node/subcell code uses `<= radius^2` with a tolerance (`encounter2d.py:476-486`; `encounter3d.py:197-220`).  Enumeration found zero exactly-on-contact-radius pairs for the tested principal and fold grids, so `<` versus `<=` does not alter those current masks.  One `11x7` interior-control state lies on the near patch boundary; patch-boundary inclusion should be recorded, but it is not a separate material failure. |
| Distinct main 2D families | The manuscript does explicitly distinguish the principal `a=0.13` endpoint family from the `a=0.17`, slower-drift fold family (`manuscript/encounter_modality_jcp.tex:798-813`), and their scripts match those declared parameters.  F3 concerns the additional mechanism-control family. |
| 2D/3D relative capacity quotients | `validate_2d_capacity.py:1-19,47-56` and `validate_3d_capacity.py:1-16,51-72` use `D_relative=D1+D2` for translation-invariant relative observables.  This agrees with `encounter3d.py:1-28,92-104`; no centre coordinate is needed in those quotient calculations. |

## Commands and executable checks

Commands were run from the repository root.

```text
git rev-parse HEAD
git status --short
find research/reports/encounter_heterogeneous_catalytic -maxdepth 3 -type f -print | sort
rg -n "(D1|D2|Dr|Dc|relative|centre|midpoint|reaction_radius|row|column|expm|generator|reflect|mass|flux|clock)" research/reports/encounter_heterogeneous_catalytic/code/*.py
nl -ba <each cited manuscript, note, core-module, validator, and orchestration file> | sed -n '<cited range>p'
PYTHONPATH=packages/vkcore/src .venv/bin/python - <<'PY'
  # Random coordinate-transform check; midpoint/weighted mask enumeration;
  # generator drift/boundary-rate check; row-vs-column exponential check;
  # instantaneous mass/flux check; time-zero counterexample.
PY
PYTHONPATH=packages/vkcore/src .venv/bin/python - <<'PY'
  # Rebuilt weighted-centre endpoint and budget-matched homogeneous operators
  # on 9x5, 11x7, and 13x9 grids; applied the production morphology settings.
PY
.venv/bin/pytest -q tests/test_encounter.py tests/test_encounter_2d.py \
  tests/test_encounter_gig_fold.py tests/test_encounter_multid_gig_design.py
```

The focused test command passed all 19 tests.  This does not clear F1: the
existing 2D tests exercise finite radius, row sums, flux, and morphology but do
not assert the diffusivity-weighted centre for unequal diffusivities
(`tests/test_encounter_2d.py:54-86,139-187`).  The first attempts with `python`
and the system `python3` failed because `python` was absent and system Python
lacked SciPy; all reported numerical checks were rerun successfully with the
repository `.venv/bin/python`.

## Files inspected for this round

- `manuscript/encounter_modality_jcp.tex`
- `notes/continuum_multid_theory.md`
- `packages/vkcore/src/vkcore/encounter.py`
- `packages/vkcore/src/vkcore/encounter2d.py`
- `packages/vkcore/src/vkcore/encounter3d.py`
- `packages/vkcore/src/vkcore/fpt.py` (needed to verify the sparse discrete
  column-state implementation behind `build_report.py`)
- Every scientific validator under the report's `code/` directory:
  `build_report.py`, `validate_gig_fold.py`, `validate_multid_gig_design.py`,
  `validate_2d_finite_radius.py`, `validate_2d_mechanisms.py`,
  `validate_2d_matched_homogeneous.py`, `validate_2d_matched_fold.py`,
  `validate_2d_capacity.py`, and `validate_3d_capacity.py`.
- `plot_model_schematic.py`, `build_publication_notebook.py`,
  `run_publication_pipeline.py`, and `compile_manuscript.py` were inspected for
  model restatement or convention-changing orchestration.  They do not repair
  or override the midpoint used by the shared builder.
- Focused encounter tests listed in the command block.

## Not reviewed or not recomputed

- I did not regenerate the full five-grid weighted-centre artifact family or
  its long-tail files.  The `9x5` reconstruction is already a sufficient
  counterexample to the stated all-five endpoint claim.
- I did not locate the weighted-centre 2D fold or recompute its exponents,
  splitting weights, tail certificate, or grid drift.  Those current values
  must be treated as midpoint-model values until regenerated.
- Root isolation, morphology thresholds, tail exhaustion, and conditioning
  were checked only as needed for the model-convention counterexample; they
  belong primarily to round 05.
- The Green/Woodbury proof, full GIG approximation error, catastrophe algebra,
  capacity asymptotics, formal Lean statements, bibliography/novelty, figure
  visual QA, and complete provenance chain are outside this round and are not
  cleared by this report.

## Release gate

Do not close round 01 or submit the affected paper/artifact package until F1 is
resolved and the regenerated weighted-centre results are independently
re-audited.  F2 must be resolved by either a method/framing correction or a new
discretization.  F3 requires either a genuine one-factor rerun or material
reframing as a distinct positive-example family.  F4--F5 can close with
explicit bounded manuscript and manifest corrections, provided no regenerated
result contradicts them.
