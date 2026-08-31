# Round 04 revised claim-safety and cross-document consistency gate

Date: 2026-07-13  
Audit action: claim and evidence audit only; no manuscript, theory, code, or
data artifact was modified.  
Primary comparison set:

- `manuscript/encounter_multimodal_prr.tex`;
- `notes/theorem_program.md`;
- `notes/research_contract.md`;
- `README.md`;
- `artifacts/data/gig_constructive_pilot.json`;
- `artifacts/data/continuum_g1_smoke.json`;
- `artifacts/data/manuscript_compile.json`; and
- `audits/round_02_manuscript_claims.md`.

The current G1 label was also checked against the already stored adversarial
evidence in `audits/round_03_g1_smoke_attack.md`; otherwise this audit would
knowingly consume a machine-readable `PASS` after a documented false-positive
test.

## Executive verdict

**Internal milestone: FAIL CLOSED as presently labelled.**  The reduced GIG G0
certificate, reduced cusp, theorem-status boundaries, normalized bridge target,
and exact fold/cusp jet lists are now claim-safe.  However, the report currently
records G1a as `PASS` while the stored G1 adversarial audit shows that important
physically wrong implementations can still pass all current gates.  In addition,
the symbol $B$ still denotes two different installed-material quantities
between the general continuum model and the slab quotient.  A narrower
milestone called “G0 passed; G1 quotient implementation scaffold assembled”
would be supportable after the G1a downgrade and budget renaming.

**Submission: FAIL CLOSED.**  Besides the two unresolved issues above, the
analytical realization theorem, continuum fold, independent validation,
physical-3D realization, author-confirmed metadata, companion identifiers, and
archival data/code identifiers remain explicitly open.  The compile artifact
correctly records `release_eligible: false`; a clean PDF build is not a
scientific release gate.

Severity below follows Round 02:

- **P0**: publication or central scientific claim is unsafe;
- **P1**: a major scientific/evidence correction is needed before the stated
  internal gate can pass; and
- **P2**: precision or governance cleanup that is not independently fatal.

## Round 02 closure matrix

| Round 02 item | Revised status | Evidence and decision |
|---|---|---|
| P0.1 one physical budget | **NOT CLOSED** | The general model and contract now agree on a centre-space installed-catalyst integral, but the slab quotient reuses $B$ for a per-transverse-measure quantity and calls the full amount $WB$.  This is analyzed as remaining P0-A below. |
| P0.2 bridge scaling and budget | **CLOSED as a theorem target** | Manuscript Eqs. (bridge), lines 289--326, now use $m_0A_\epsilon^{-1}f_\epsilon(m_0\tau;u_\epsilon(\vartheta))-F(\tau;\pi(\vartheta))$, declare $B_\epsilon$, $A_\epsilon$, the interior budget-preserving map, a compact window, the exact jet, and $E_q(\epsilon)\to0$.  This matches theorem-program Eq. (6.1), lines 769--827.  Both sources label it conjectural and distinguish weak-budget from fixed-budget results. |
| P0.3 numerical testing versus theorem | **CLOSED** | The abstract, lines 56--65, explicitly says the uniform bounds remain unproved and makes analytical jet realization and independently converged numerics separate submission gates.  Lines 322--326 repeat that mesh/solver checks do not prove the remainder. |
| P0.4 overlap and novelty | **CLOSED for internal use; OPEN for submission metadata** | Manuscript lines 90--105 disclose both companion working manuscripts, enumerate inherited results, prohibit first-response/fold/cusp claims, and identify the non-overlapping chain.  Public identifiers and author-approved wording are still absent, but that absence is declared at lines 96 and 428--431 and in the hard release checklist. |
| P0.5 prospectus and metadata | **HOLD IMPLEMENTED, NOT CLEARED** | The title, source header, and abstract identify an internal working program; the compile artifact records `release_eligible: false` and a release blocker.  Author order, corresponding-author status, funding, contributions, disclosures, and archival identifiers remain unconfirmed, so this item still blocks submission but no longer masquerades as cleared. |
| P1.1 arbitrary $m,d$ | **CLOSED** | Manuscript lines 109--112 restrict arbitrary prescribed finite $m$ to the reduced family, continuum transfer to a fixed finite design, and resolved evidence to physical $d=2,3$; it explicitly disclaims arbitrary-$d$ continuum theory. |
| P1.2 GIG theorem status/minima/observability | **CLOSED** | Manuscript lines 196--218 and theorem-program lines 414--568 now label arbitrary-$m$ as conjectural, list the missing uniform estimates, treat $M=1$ separately, impose $\delta<1/\sqrt{2\beta}$, remove nondegenerate-minimum and computed-$R_{\rm sep}$ claims, and expose the loss of observability.  The finite $m=2,\ldots,6$ and cusp statements are separately numerical and reduced-only. |
| P1.3 projected multi-jet control | **CLOSED as abstract local algebra** | Manuscript lines 220--255 define the cost covector, $M\succ0$, projected matrix, rank condition, interior assumption, minimum-$M$-norm formula, and model-rank limitation.  It no longer calls the old scalar direction a physical/global optimum. |
| P1.4 fold jet | **CLOSED** | Manuscript Eq. (foldjet), lines 257--268, includes $f_t,f_{tt},f_{ttt},f_{t\theta},f_{tt\theta}$, and lines 382--385 require convergence of the entire jet. |
| P1.5 cusp jet | **CLOSED** | Manuscript Eq. (cuspjet), lines 269--287, includes $f_{ttt\theta_i}$, rank two, $f_{tttt}\ne0$, and the remote-pair requirement.  Continuum and reduced cusps remain separate labels. |
| P1.6 exact quotient scope | **SCOPE CLOSED; G1 EVIDENCE LABEL OPEN** | Manuscript lines 328--359 specify the integrated common transverse translation, retained longitudinal midpoint, circular/spherical contact geometry, and slab restriction.  It does not call slabs localized patches.  The implementation-level `PASS` is nevertheless too strong; see P1-B. |
| P1.7 reduced versus physical simplex | **CLOSED for claim safety; realization theorem OPEN** | Manuscript lines 169--171 use $\pi$ for GIG probabilities and $w$ for physical catalyst weights.  Lines 291--320 require an interior nonsingular budget-preserving realization map with transport and cost factors.  Since this map is explicitly conjectural and no transfer is claimed, the present wording is safe, but submission still requires the theorem. |

## Remaining/new P0

### P0-A: $B$ is still not one physical resource in the general model and quotient

The contract defines

\[
  \kappa_w(c)=B\sum_jw_j\phi_j(c),
  \qquad \int_{\mathcal C}\phi_j(c)\,dc=1,
  \qquad \int_{\mathcal C}\kappa_w(c)\,dc=B,
\]

at contract lines 32--45.  The manuscript repeats this full centre-space
definition at lines 114--139 and explicitly says $B$ is the conserved
installed-catalyst functional.

In the physical-$d=2$ slab quotient, however, the catalyst depends only on the
longitudinal midpoint $z$, is uniform over the omitted transverse coordinate
of width $W$, and the manuscript states at lines 354--356

\[
  \text{total installed amount}
  =W\int\kappa_w(z)\,dz=WB.
\]

Thus the quotient's $B$ is the longitudinal integral, or installed amount per
unit omitted transverse measure, whereas the general model's $B$ is the full
physical centre-space integral.  The saved smoke has $W=1$,
`integrated_budget = 0.6`, and `physical_budget = 0.6000000000000001`
(`continuum_g1_smoke.json`, lines 18--28 and 54--83), so this fixture cannot
detect the factor-of-$W$ inconsistency.  The same issue becomes
$W^{d-1}$ in physical dimension $d$, directly affecting any 2D/3D budget
comparison.

This is not a harmless notation change: the title, budget tangent, catalyst
cost covector, bridge realization map, and dimensional comparison all depend on
which amount is held fixed.

**Required closure.**  Choose exactly one of the following and propagate it
through the contract, theorem program, manuscript, code keys, and artifacts:

1. keep $B_{\rm tot}$ as the full physical installed amount and use
   \(\kappa_w(z)=B_{\rm tot}W^{-(d-1)}\sum_jw_j\phi_j(z)\); or
2. define a distinct per-transverse-measure quantity
   \(\mathcal B_\parallel=\int\kappa_w(z)\,dz\) and always report
   \(B_{\rm tot}=W^{d-1}\mathcal B_\parallel\).

Do not call both quantities `B`, `integrated_budget`, or `physical_budget`.
Add a non-unit-$W$ artifact gate after the notation is frozen.

## Remaining/new P1

### P1-B: the current G1a `PASS` is not discriminating evidence

The README ledger calls G1a `PASS` (lines 26--30), the abstract says its
geometry/budget/positivity/mass-balance smoke gates passed (lines 60--62), the
body labels discrete identities proved and the implementation numerically
verified at reduced resolution (lines 361--376), and the final ledger again
records `G1 operator smoke ... PASS` (lines 389--405).  The JSON has twelve true
booleans and top-level `status: PASS` (`continuum_g1_smoke.json`, lines 2--15 and
115).

Those labels remain stronger than the stored adversarial evidence.  Round 03
demonstrated that a translated contact sink can preserve total area and every
current gate while changing the density, and that opposite patch-normalization
errors can cancel at the only gated midpoint control.  The current JSON still
contains no gate for:

- local contact-mask position, centroid, symmetry, or selected cell fractions;
- independent contact quadrature refinement (the SciPy `quad` estimate is
  stored under the stronger name `contact_area_error_bound`);
- each patch integral, endpoint budgets, or zero budget derivative;
- reconstructed initial first moments;
- a dense-exponential/time-difference check of the reported time jets; or
- an asymmetric tensor-order sentinel.

The claim-scope warning in JSON line 2 is excellent and prevents this from
becoming a continuum-fold P0.  It does not make `G1a PASS` true: a generic
consumer sees `status: PASS`, and the manuscript/README have already promoted
that status to a project gate.

**Required closure.**  Until the P1 mutation tests are rejected, change the
gate to `INCOMPLETE` or, at most, a machine-readable
`SELF_CONSISTENCY_SMOKE_PASS` with `project_gate_passed: false`.  Replace
“proved for the discrete identities” by a narrower algebraic-invariant
statement unless an actual proof and independent implementation checks are
stored.  Restore G1a `PASS` only after the local geometry, patchwise budget,
initial-moment, tensor-order, and independent semigroup/jet gates pass.

### P1-C: evidence ontology and release routing still disagree

The theorem program defines `NO-GO` only as a mathematical counterexample or
regularity obstruction (lines 9--20).  The research contract defines `NO-GO`
as a failed project falsification gate that removes a headline (lines 47--59).
The manuscript correctly distinguishes `mathematical no-go` from
`project gate failed` (lines 84--88), but the source-of-truth notes have not
adopted that split.  The manuscript additionally uses the undefined label
`numerically verified---reduced-resolution` for the G1 smoke.

The release routing has a related ambiguity: the README splits G1 into G1a and
G1b, but line 37 says PRR is a GO after “G1, G3, G4, and G5.”  The hard release
checklist correctly requires G1b.  A release bot or later reader should not
have to infer whether `G1` means the already marked G1a smoke or the unrun G1b
continuum fold.

**Required closure.**  Adopt the manuscript's six-way ontology in both notes,
give the smoke a distinct non-continuum self-consistency label, and replace the
README release condition by `G1b + G3 + G4 + G5` (plus metadata/overlap gates).

## Numerical and formula spot checks that pass

1. **Reduced GIG $m=2,\ldots,6$.**  The artifact declares the reduced-only
   scope, the five mode counts, $R=10$, $p=2.5$, $b=0.01$, and the
   non-exhaustive-scan limitation.  Its summary values
   `minimum_prominence_ratio = 2.695647755849697` and
   `minimum_curvature_margin = 2.5199868714442872` agree with manuscript
   lines 173--180.
2. **Canonical reduced cusp.**  Artifact and manuscript agree on
   $t_*=0.5728883706366283$, the three weights, scaled fourth derivative
   $-13.61053628261525$, row-angle sine $0.9632674238749189$, raw
   dimensionless SVD ratio $0.7478993752870627$, and rank two.  The artifact
   stores normalization and an independent Cauchy-integral derivative
   cross-check.  The manuscript does not promote this reduced cusp to
   trimodality or a continuum cusp.
3. **GIG theorem status.**  The exact shape identity, strict
   $\delta<1/\sqrt{2\beta}$ restriction, separate $M=1$ treatment, and
   missing uniform envelopes agree across manuscript and theorem program.  No
   certified $R_{\rm sep}$ is claimed.
4. **Fold and cusp jets.**  The manuscript and theorem program list the same
   minimal fold jet and the same fourth-order cusp jet, including
   $f_{ttt\theta_i}$.
5. **Bridge normalization.**  The density Jacobian $m_0$, independent
   amplitude $A_\epsilon$, budget-preserving physical map, compact jet norm,
   and vanishing error agree between manuscript Eq. (bridge) and theorem-program
   Eq. (6.1).
6. **Release hold.**  `manuscript_compile.json` says its scope is PDF hygiene
   only, records no missing references/citations or font defects, and sets
   `release_eligible: false`.  This is internally consistent with the qualified
   title, abstract warning, acknowledgments, and metadata checklist.

## P2 residuals

1. The theorem program still describes the numerical GIG evidence as “legacy”
   selected two-, three-, and four-mode cases (lines 585--587), while the
   report-owned G0 artifact now covers $m=2,\ldots,6$.  This is stale rather
   than contradictory, but the theorem ledger should point to the current
   artifact.
2. “Root isolation” in manuscript line 175 is acceptable as a numerical
   statement only because the artifact explicitly says the finite scans are not
   interval-exhaustive.  Preserve that limitation near any future figure or
   table; do not change “finds $2m-1$” into “has exactly $2m-1$” without an
   interval proof and tail exclusion.
3. The one-sentence research target is written in the present tense (“persist”)
   even though the remainder and continuum realizations remain conjectural.
   The section heading makes it a target, but future stand-alone extracts should
   use “aims to establish” until G4 and the continuum gates pass.

## Mandatory repair order

1. Freeze the full physical budget versus per-transverse-measure budget and
   regenerate the smoke artifact with unambiguous keys.
2. Downgrade G1a to `INCOMPLETE` and make its machine-readable status impossible
   to consume as a continuum/project PASS.
3. Implement the Round 03 local-geometry, patchwise-budget, initial-moment,
   tensor-order, and independent semigroup/jet mutation gates; only then restore
   G1a.
4. Unify evidence vocabulary and write the release condition explicitly as
   G1b + G3 + G4 + G5 plus author/overlap/archive gates.
5. Keep the current reduced GIG, bridge, arbitrary-$m$, dimension, overlap,
   and exact-jet wording unchanged except for the small P2 synchronizations.

## Final binary decisions

- **Internal milestone:** **FAIL CLOSED** for the currently stated ledger.  G0
  is claim-safe, but G1a must not remain `PASS`, and the physical budget symbol
  must be made dimensionally unique.
- **Submission:** **FAIL CLOSED**.  The document itself correctly acknowledges
  that G1b, G3, G4, G5, companion identifiers, author-confirmed metadata, and
  archival release material are all open; the remaining P0/P1 findings above
  add independent blockers.
