# Round 02, reviewer A: Green, Woodbury, and resolvent audit

Date: 2026-07-11  
Verdict: **needs revision; no B0, two B1 findings**  
Audited working-tree base: `3531353a515160b09899199a9257e7455a654b22`

The encounter report, `vkcore.encounter`, Green tests, and encounter Lean
modules were untracked in the audited working tree.  The hash above is a base
commit, not a complete frozen commit.  Line anchors refer to the current
working tree on the date above.

Severity follows `audits/README.md`: B0 is a submission blocker, B1 a material
revision, B2 a bounded correction or required caveat, and B3 optional polish.

## Executive assessment

The finite-matrix implementation is substantially sound.  Independent checks
confirmed the Woodbury orientation, channel transform, determinant lemma,
Laplace signs, zero-frequency moments, reaction-rate Jacobian, and direct
semigroup flux.  The manuscript's warnings about dark modes and vanishing
observable residues are also mathematically necessary; explicit finite CTMC
counterexamples realize both phenomena.

Two central scope gaps remain:

1. the displayed continuum reduction is written with `K^{-1}`, although the
   stated model permits nonnegative fields with zeros and the implementation
   deliberately supports zero reaction rates through an inverse-free renewal
   matrix; and
2. the paper defines the Green operator in the pole-free right half-plane but
   then calls its determinant secular and discusses spectral poles, while the
   implemented API rejects every negative-real argument where finite killed
   CTMC poles actually lie.

These do not invalidate the time-domain CTMC fold, which is computed directly
from matrix exponentials.  They do prevent the Green/pole layer from shipping
as a single exact result without separating the inverse-free response identity
from the additional finite spectral or continuum meromorphic-continuation
hypotheses.

## Findings

### F1 — B1: the central operator formula assumes an invertible reactivity operator that the stated model and implementation do not require

The physical model permits intrinsic rates
`kappa_j(C_eta) >= 0` and multiplies them by patch indicators
(`manuscript/encounter_modality_jcp.tex:256-270`).  Thus the total multiplication
operator can have a nontrivial kernel: it is zero away from active patches and
may also vanish within a declared patch.  Nevertheless, the displayed
Woodbury and support-density formulas use

```text
(K^{-1} + G)^{-1}
```

(`manuscript/encounter_modality_jcp.tex:394-420`; identically in
`notes/continuum_multid_theory.md:271-324`).  “Whenever the stated inverses
exist” protects the algebra from being literally false, but it means the
central formula is not an identity for the full nonnegative model class stated
immediately beforehand unless the reaction support is redefined and `K` is
assumed bounded below there.

The finite implementation already avoids this restriction.  It forms

```text
M = I + G K,
R = R0 - R0 U K M^{-1} U^T R0
```

(`packages/vkcore/src/vkcore/encounter.py:831-851,911-929`) and the constructor
allows zero rates (`packages/vkcore/src/vkcore/encounter.py:471-503`).  The
zero-rate regression explicitly verifies this case
(`tests/test_encounter_green_ctmc.py:144-166`).  In my independent zero-rate
reconstruction, rates `(0,0.7)` gave channel transform
`(0, 0.1494660163)` and full-resolvent error `4.44e-16`, while `K^{-1}` did not
exist.

The two determinant conventions are likewise only proportional for nonzero
rates:

\[
\det(I+GK)=\det K\,\det(K^{-1}+G)
=\kappa_1\kappa_2\,\mathcal D(s).
\]

The code and Lean theorem use `det(I+GK)`
(`encounter.py:913-925`;
`FormalLean/Encounter.lean:203-238`), whereas the manuscript prints
`det(K^{-1}+G)` (`encounter_modality_jcp.tex:450-455`).  Their zeros agree only
when both rates are nonzero; their normalization, rate derivatives, and
zero-rate limits do not.

**Required resolution.**  State the inverse-free operator identity as the
primary result.  With `u=Gamma R0 q0`, a suitable bounded-volume formulation is

\[
x=\Gamma(s-T)^{-1}q_0=(I+GK)^{-1}u,
\qquad y=Kx=K(I+GK)^{-1}u,
\]

\[
(s-T)^{-1}=R_0-R_0\Gamma^*K(I+GK)^{-1}\Gamma R_0.
\]

Then give the `K^{-1}+G` form only as a corollary under an explicit bounded
invertibility hypothesis.  Define whether `Gamma` restricts to the contact
tube, the essential support of total killing, or a channel-stacked support;
state boundedness/domain assumptions accordingly.  Record the determinant
scale factor before comparing the manuscript, code, and Lean objects.

### F2 — B1: the stated Green domain contains no killed CTMC poles, and no continuation/pole-residue certificate bridges that gap

The manuscript defines
`R0(s)=(s-L0)^{-1}` only for `Re(s)` above the free spectral bound
(`manuscript/encounter_modality_jcp.tex:394-407`).  For a conservative finite
CTMC that means `Re(s)>0`.  The killed spectrum, and hence poles of
`(s-T)^{-1}`, lie in the negative half-plane.  The next subsection nevertheless
calls the two-hotspot determinant “secular” and says it controls reactive
poles (`manuscript/encounter_modality_jcp.tex:445-460`) without first extending
`G(s)` to other components of the free resolvent set or stating a meromorphic
continuation theorem.

The implementation enforces the same right-half-plane boundary:
`ctmc_green_resolvent` rejects `Re(s)<=0`
(`packages/vkcore/src/vkcore/encounter.py:876-897`).  Existing Woodbury tests
use `0.03`, `0.4`, `2.0`, and `0.55+0.2i`
(`tests/test_encounter_green_ctmc.py:39-65`).  They validate Laplace response,
not poles, numerator cancellation, or residues.

An independent symmetric `3x3` two-walker CTMC produced a genuinely coupled
killed eigenvalue

```text
lambda_T = -1.235725942267004
distance to free spectrum = 0.235725942267004
det(I + G(lambda_T) K) = -1.46e-15
```

so the finite determinant behaves as expected at the pole, but the public API
rejects that argument as negative.  The finite determinant lemma

\[
\det(sI-T)=\det(sI-L_0)\det(I+G(s)K)
\]

was independently reproduced at `s=0.37+0.19i` and `s=-0.23+0.11i` with
absolute errors `0` and `2.95e-16`, respectively.  This is a finite-matrix
result on `s` in the free resolvent set; it is not supplied by the current
right-half-plane API and does not establish a continuum continuation.

**Required resolution.**  Split the claim into two layers.

1. For finite matrices, define `G(s)` for every `s` outside `sigma(L0)`, state
   the determinant lemma, distinguish shared free/dark eigenvalues, and audit
   left/right eigenvectors plus channel-specific and total residues.
2. For the continuum operator, retain only the right-half-plane Laplace
   response unless compactness/Fredholm and meromorphic-continuation hypotheses
   are actually stated and proved or cited in a model-applicable form.

If no finite pole/residue artifact is added, change “secular determinant” and
“controls poles” to an explicitly formal candidate-pole statement and place
all pole/residue conclusions in the not-certified boundary.  The direct
matrix-exponential modality claims may remain unchanged.

### F3 — B2: the zero-frequency inverse needs the full-chain transience condition at the point where it is used

The main Green subsection writes

\[
\pi=\alpha(-T)^{-1}UK
\]

without a local hypothesis (`manuscript/encounter_modality_jcp.tex:462-470`).
The appendix later supplies the correct condition, “If the killed chain is
transient” (`manuscript/encounter_modality_jcp.tex:1405-1427`), and the code
requires `-T` to be nonsingular on the full live state space
(`packages/vkcore/src/vkcore/encounter.py:787-828,997-1028`).

Reaction being certain from a particular initial law is not by itself enough
for the displayed full inverse.  The repository's own singular example has
zero motion, killing only at `(0,0)`, and initial mass at `(0,0)`: that initial
mass reacts with probability one, but other unreachable live states make
`-T` singular, so the full solve is rejected
(`tests/test_encounter_green_ctmc.py:215-232`).

**Required resolution.**  Add “provided the full killed live operator is
transient/invertible” beside Eq. (splitting-killed), with the appendix
cross-reference.  If initial-class transience is intended instead, formulate
the solve on the reachable transient subspace (or specify the appropriate
Poisson/Drazin construction) rather than writing the full inverse.

## Checks that passed

| Topic | Falsification attempt and result |
|---|---|
| Finite Woodbury orientation | For biased, nonsymmetric two-walker generators, the Green-built full resolvent and direct killed inverse agree in the repository tests to `<2e-13` at three positive real frequencies and one complex frequency (`tests/test_encounter_green_ctmc.py:39-65`).  My determinant-lemma checks also passed in both right and left half-planes where the free inverse exists. |
| Channel-transform orientation | The implemented row formula `(alpha R0 U) K (I+GK)^{-1}` (`encounter.py:922-929`) matched the direct killed solve.  Independent semigroup quadrature gave maximum errors `3.33e-16` at `s=0.37` and `1.87e-16` at `s=0.55+0.2i`; this verifies the sign in `sI-T` and the placement of `UK`. |
| Laplace derivatives and moments | `F'=-alpha R^2B` and `F''=2alpha R^3B` in `encounter.py:962-1064` have the correct signs.  Repository finite-difference tests pass (`tests/test_encounter_green_ctmc.py:68-103`), and zero-frequency quadrature confirms splitting, first, and second unconditional channel moments (`tests/test_encounter_green_ctmc.py:169-212`). |
| Rate sensitivity | From `T=L0-U K U^T`, `dR/dk_j=-R u_j u_j^T R`; including `dB/dk_j` gives the code's Jacobian formula (`encounter.py:1009-1054`).  Central rebuilds agree to the declared `2e-9` relative tolerance (`tests/test_encounter_green_ctmc.py:106-141`).  The manuscript's general sign `R_theta=R T_theta R` is correct (`encounter_modality_jcp.tex:475-482`). |
| Time-domain channel flux | Uniformization, augmented dense exponentials, `pB`, `pTB`, and `pT^2B` agree to approximately `1e-13`; differential mass balance and Poisson-tail closure pass (`tests/test_encounter_green_uniformization.py:28-81`). |
| Zero-mode handling | The free Green condition number grows as expected when `s` approaches zero.  In the independent audit, Woodbury/full-resolvent error grew from `4.88e-15` at `s=1e-2` to `5.97e-5` at `s=1e-12`, while channel-transform error grew to `6.34e-7`.  This supports, rather than falsifies, the instruction to use the direct killed solve at zero (`encounter.py:883-897`; manuscript lines 462-470). |
| Dark modes | With identical symmetric walkers, an antisymmetric product eigenvector had `lambda=-2`, `||U^T v||_inf=0`, and both free and killed eigen-residuals `6.66e-16`.  It is a full-resolvent pole shared with the free generator and is invisible to the restricted determinant.  The manuscript warning at lines 457-460 is correct. |
| Observable/numerator cancellation | A reflection-odd killed eigenmode at `lambda=-2.3141428429` had hotspot components `(+0.533860,-0.533860)`.  For initial state `(0,0)`, the two channel residues were `+0.199505` and `-0.199505`, so the total reaction-flux residue was exactly zero although each channel was coupled.  An even initial law also annihilated the same odd sector.  This confirms that a determinant root is not automatically a mode of the chosen observable. |
| Finite 2x2 Lean algebra | `FormalLean/Encounter.lean:165-238` proves the scalar inverse, Schur factorization, `det(I+GK)` expansion, and two-hotspot solve without project axioms; `EncounterAxioms.lean:19-22` and `encounter_axioms_report_20260711.txt:17-23` report only standard Lean/mathlib dependencies.  This is an algebra certificate, not an operator, pole, or residue certificate. |
| Discrete Green/PGF orientation | The separate finite discrete Green comparison passed at real and complex `z`, with total and channel errors below `1e-12` (`tests/test_encounter_green_formula_comparison.py:19-42`). |

## Commands and executable checks

Commands were run from the repository root unless noted.

```text
git rev-parse HEAD
git status --short -- <Round-02 source set>
rg -n "Green|Woodbury|resolvent|pole|residue|dark|zero mode|splitting|sensitivity" \
  <manuscript, notes, encounter.py, Lean module, tests>
nl -ba <each cited file> | sed -n '<cited range>p'

.venv/bin/pytest -q \
  tests/test_encounter_green_ctmc.py \
  tests/test_encounter_green_uniformization.py \
  tests/test_encounter_green_formula_comparison.py \
  tests/test_encounter_search.py
# Result: 26 passed.

PYTHONPATH=packages/vkcore/src .venv/bin/python - <<'PY'
# Constructed a symmetric two-walker CTMC; checked an explicit U-dark
# antisymmetric eigenmode, reflection-odd channel-residue cancellation,
# determinant lemma at complex positive/negative s, one coupled negative pole,
# zero-rate K, and conditioning/errors as s downarrow 0.
PY

PYTHONPATH=packages/vkcore/src .venv/bin/python - <<'PY'
# Integrated exp(-s t) alpha exp(T t) B on [0,infinity) for real and complex s
# and compared it with ctmc_channel_laplace.
PY
```

The saved `artifacts/logs/pytest_publication_gates.log` is not used as a clean
certificate: its current final test fails because the aggregate manifest hash
is stale (`pytest_publication_gates.log:1-43`).  That failure is provenance,
not Green algebra; the focused Round-02 tests above were rerun independently.

## Inspected evidence

- `manuscript/encounter_modality_jcp.tex`, especially the model, Green section,
  evidence boundary, limitations, and finite-state appendix;
- `notes/continuum_multid_theory.md` and `notes/theory.md`;
- `packages/vkcore/src/vkcore/encounter.py`, including construction, dense
  semigroup, Green reduction, direct Laplace solve, sensitivities, and
  uniformization;
- `tests/test_encounter_green_ctmc.py`,
  `tests/test_encounter_green_uniformization.py`,
  `tests/test_encounter_green_formula_comparison.py`, and the determinant tests
  in `tests/test_encounter_search.py`;
- `FormalLean/Encounter.lean`, its axiom driver/report, and the formal README;
- publication-pipeline test selection, manifest inventory, and saved pytest log.

## Not-certified boundary

This review does **not** certify:

- closedness/generation/domain hypotheses for the reflecting forward operator,
  boundedness of every declared `Gamma`/`K`, or applicability of Woodbury to a
  Robin trace space;
- continuum Fredholm compactness, meromorphic continuation, Bromwich inversion,
  or differentiation under the inverse transform;
- poles, Jordan structure, left/right eigenvector conditioning, numerators, or
  residues of the production `L=31` fold model; the adversarial examples above
  are small exact diagnostics, not a production spectral artifact;
- a negative-half-plane Green API or certified root isolation around free
  eigenvalues;
- sensitivities when the parameter moves hotspot support `U`, changes the free
  generator `L0`, or changes an operator domain; the implemented Jacobian is
  specifically for reaction-rate parameters at fixed support and transport;
- zero-frequency splitting for globally singular killed operators outside a
  reachable-transient-subspace formulation;
- continuum-capacity Green asymptotics, which belong primarily to Round 06.

## Release gate

No B0 was found in the finite time-domain calculations.  Round 02 should not
close until F1 is repaired with an inverse-free primary identity and explicit
operator hypotheses, and F2 is resolved by a strict finite/continuum spectral
scope split.  F3 is a local but required transience clarification.  After
remediation, rerun the focused Green tests and add at least one saved finite
dark-mode/residue/pole audit if pole language remains in the paper.
