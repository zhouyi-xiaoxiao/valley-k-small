# Round 174: twelve-family ideal fixed-box C1 composition

Date: 2026-07-17

Status: **PASS IDEAL FIXED-BOX THEOREM-LAYER C1 COMPOSITION /
TWELVE SOURCE-DEFINED DYADIC FAMILIES / EVERY REAL SIMPLEX CONTROL /
EVERY BUDGET IN AN ARBITRARY FIXED FINITE INTERVAL /
P0=0 / P1=0 / P2=2 DOCUMENTED /
HOLD PRODUCTION SAME-MEMBER / HOLD PROJECT AND PRODUCTION COMPLETE C1 /
HOLD COMPUTABLE C2--C3 AND ROOT TRANSFER / HOLD F0--F3 / HOLD RELEASE**

## Final exact bytes

| role | report-relative path | SHA-256 |
|---|---|---|
| mathematical note | `notes/continuum_c1_twelve_family_ideal_fixed_box_C1_composition_v1.md` | `13da61f8a41a6d659800595bb73d6ea717530a3c6b33244f0c39703351a80660` |
| canonical contract | `artifacts/data/continuum_c1_twelve_family_ideal_fixed_box_C1_composition_v1.json` | `ffbd822e8a3649405f27d9d22f21688049df6a7cc045b0899ac5b38540b4cb70` |
| builder | `code/build_continuum_c1_twelve_family_ideal_fixed_box_c1_composition_v1.py` | `3b1739af644bf710c3e1830b4978e2d7010a0c8f93d3e2d3483f5ded95d967fd` |
| source/geometry validator | `code/validate_continuum_c1_twelve_family_ideal_fixed_box_c1_composition_v1.py` | `d067eeb854b5d9d8ca0669ea99b0bdd9c50c02a236faccc0e0a3513c669e1a90` |
| static/currentness tests | `code/test_continuum_c1_twelve_family_ideal_fixed_box_c1_composition_v1.py` | `be44611c7957140c72348bbaa8f66ee90e7c3c27556143aee07e042929cfa8bd` |
| mutation tests | `code/test_continuum_c1_twelve_family_ideal_fixed_box_c1_composition_mutations_v1.py` | `6a67565b1881763086070fde3841cf0cd8b875d737c52118ac3be784f5d0c048` |

The artifact pins 20 regular-file source snapshots, including the Round-172
genuine refinement authority, the Round-173 source-bound map/cut/killing
contract, and the accepted one-axis, varying-space, tensor, bounded-killing,
positive-time, and quantitative ideal theorem/audit pairs.  Every live pin
matched its recorded SHA-256 in the final independent replay.

## Exact accepted theorem layer

For each \(f\) in the twelve source-defined fixed boxes, every
\(w\in\Delta_3\), and every \(B\in[0,B_*]\), where \(B_*<\infty\) is arbitrary
but fixed, use the genuine dyadic family \(h_f(n)=h_f(0)2^{-n}\).  The same
ideal density, conductances, physical cell volumes, exact-adjoint maps,
bounded reconstructed killing, and killed operator are retained throughout
the composition.

The independent referee rederived the density ratio

\[
 \frac{\pi_h^{\rm pc}(x)}{\pi(x)}
 =
 \bar r_M\,\bar r_R\,
 \exp\{\Phi(x)-\Phi(x_C^{\rm rep})\}.
\]

Each weighted axis-cell integral ratio and each representative displacement
contributes an \(\exp(\pm\eta/2)\) factor, so
\(\exp(-\eta)\le\pi_h^{\rm pc}/\pi\le\exp(\eta)\), including vertex half cells
and wrapped periodic cells.  The 36 declared axes consist of 20
cell-reflecting, four vertex-dual, ten periodic-base, and two half-shift axes:
exactly three axes for each of the twelve tensors.

The actual compact-bump initial density has support strictly inside all twelve
boxes; the exact minimum support margin is

\[
 \frac{106645239176133349}{288230376151711744}>0.
\]

The periodic image bump is smooth and the continuum weight is positive and
smooth, hence \(u_0=q_0/\pi\in H^2\subset H^1\).  With
\(u_{0,h}=P_hu_0\), the cell identity
\(\pi_{h,C}u_{0,h,C}=\int_Cq_0\) is exact.

The accepted one-axis, tensor, and bounded-killing premises therefore compose
to generalized Mosco convergence and reconstructed strong-resolvent
convergence for the ideal fixed-box families.  Functional calculus and the
moving-pairing argument then give, uniformly on every compact positive-time
interval, convergence of the state, the unit-field contact observable, and
the reaction density for time orders \(r=0,1,2\).  The budget factor is
retained:

\[
 g_{B,w}^{(r)}=B\,F_{B,w}^{(r)},
\]

so the reaction density and its derivatives vanish at \(B=0\).

Round-10, Round-173, and Round-11 estimates additionally compose to an ideal
existence-constant \(O(\sqrt{h_f(n)})\) resolvent/operator/observable
corollary.  Its constants are proved finite for each declared fixed box,
finite budget cap, positive-time window, and derivative order, but are not
numerically evaluated.  It is therefore not computable C2 evidence.

## Adversarial chronology

The first mathematical attack rejected the initial freeze with four P1
findings:

1. two displayed continuum-form terms had missing plus signs;
2. \(F\) was called the reaction density although the physical density is
   \(g=BF\);
3. the continuum form domain was not stated; and
4. two distinct half-width conventions were conflated.

The repaired freeze restores the signs and form domain, distinguishes
budget-normalized \(F\) from \(g=BF\), and separates the half-width
conventions.  It also makes the density ratio, moving pairing, and contour
boundary explicit.

A separate read-only referee then audited the repaired exact bytes.  It
recomputed the density/gauge algebra, support margin, 12-family/36-axis
enumeration, initial projection, same-operator composition, budget factor,
and ideal half-order implication.  It found no remaining blocking defect:

```text
P0 = 0
P1 = 0
P2 = 2
```

The two retained P2 items are explicit limitations:

- the local replay does not authenticate the interpreter or executed source
  bytes, and the builder's source snapshot set is not atomic against a hostile
  concurrent writer; and
- the validator enforces an exact-string/source-geometry contract backed by
  pinned audits.  It is not an independent numerical backend, a formal proof,
  or a machine proof.  The separate read-only mathematical referee supplies
  human analytical review only.

Neither limitation is promoted away in the note, artifact, manuscript, or
release state.

## Independent reproduction

The repaired bytes were independently rerun from the repository root:

```text
.venv/bin/python -m ruff check <builder> <validator> <two test files>
All checks passed!

.venv/bin/python -m ruff format --check <the same four files>
4 files already formatted

.venv/bin/python -B \
  research/reports/encounter_multimodal_prr/code/build_continuum_c1_twelve_family_ideal_fixed_box_c1_composition_v1.py \
  --check
PASS ... sha256=ffbd822e...

.venv/bin/python -B \
  research/reports/encounter_multimodal_prr/code/validate_continuum_c1_twelve_family_ideal_fixed_box_c1_composition_v1.py
PASS ... validated_snapshot_sha256=ffbd822e...

.venv/bin/python -B -m pytest -q -p no:cacheprovider \
  research/reports/encounter_multimodal_prr/code/test_continuum_c1_twelve_family_ideal_fixed_box_c1_composition_v1.py \
  research/reports/encounter_multimodal_prr/code/test_continuum_c1_twelve_family_ideal_fixed_box_c1_composition_mutations_v1.py
..........................                                               [100%]
26 passed
```

The suite contains 18 static/currentness tests and eight fail-closed mutation
tests.  The six frozen SHA-256 values were unchanged after replay, all 20 live
source pins matched, and no target `.pyc` existed before or after the
bytecode-disabled run.

## Exact acceptance boundary

Round 174 closes only the **ideal, formula-defined, fixed-box theorem-layer C1
composition**.  It neither identifies level \(n=0\) with one correlated
production enclosure member nor evaluates a production error constant.

The following remain false:

```text
production_n0_correlated_containment_receipt_present = false
production_same_member_bridge_accepted               = false
project_complete_C1 / production_complete_C1          = false
computable_C2 / C3_box_exhaustion / root_transfer     = false
F0_complete / F1_complete / F2_complete / F3_complete = false
release_eligible / submission_eligible                = false
```

The strongest admissible statement is:

> For each of the twelve source-defined fixed boxes, every real simplex
> control and every budget in an arbitrary fixed finite interval, the genuine
> dyadic ideal Scharfetter--Gummel families converge by generalized Mosco and
> reconstructed strong resolvent to the stated killed continuum operator;
> their positive-time state, unit-field contact observable, and reaction
> density, including the first two time derivatives, converge uniformly on
> compact positive-time intervals, with an ideal \(O(h^{1/2})\) corollary whose
> constants are proved finite but not evaluated.  This neither identifies a
> member of the production enclosure nor establishes project/production
> complete C1, computable C2, C3/root transfer, F0--F3, release, or submission.
