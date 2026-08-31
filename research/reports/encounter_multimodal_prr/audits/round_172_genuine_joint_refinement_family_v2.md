# Round 172: genuine joint refinement family v2

Date: 2026-07-17

Status: **PASS TWELVE CONTROL-FREE IDEAL GEOMETRIC REFINEMENT SEQUENCES /
HOLD PRODUCTION LEVEL-ZERO CORRELATED CONTAINMENT / HOLD COMPLETE C1--C3 /
HOLD F0--F1 / HOLD RELEASE**

## Exact reviewed bytes

| role | report-relative path | SHA-256 |
|---|---|---|
| mathematical note | `notes/continuum_c1_genuine_joint_refinement_family_v2.md` | `c312ca42d57af451ffef30c69aed7275ba8d9065eb4d1ae80f8439bd2320a142` |
| builder | `code/build_continuum_c1_genuine_joint_refinement_family_v2.py` | `0683b9cf1e1942dbecce94ebde49254c3deb972a3c45c6d0ba44bd28f5fe144b` |
| canonical artifact | `artifacts/data/continuum_c1_genuine_joint_refinement_family_v2.json` | `1f7bc61ac37444c0fdb2c0b74924a4b81ed8e6d6ab70c794ebe3401156b5bee9` |
| independent validator | `code/validate_continuum_c1_genuine_joint_refinement_family_v2.py` | `46553fb9b0a9def3f998e859b2a675c95243f502231dd4d33c501292fbd184ef` |
| static/currentness tests | `code/test_continuum_c1_genuine_joint_refinement_family_v2.py` | `de5a7195a895f398498cfad5e3ca20a9e9370971f9b277d38cb3c18c63c6f2c5` |
| mutation tests | `code/test_continuum_c1_genuine_joint_refinement_family_mutations_v2.py` | `f41eed72c580db799b5643e2c48a7e1ce9c63c41a008e7994ccac46c36de02f2` |

The source inventory pins the control-free configuration family, global
reference density, ideal formula source, factorization source, Round-4 and
Round-5 theorem/audit pairs, and the historically unsealed fixed-row
anti-vacuity/member files.  No control values, budget, production raw interval
payload, topology result, or positive-budget science enters the construction.

## Mathematical result

Each of the twelve finite source rows now has an explicit sequence indexed by
\(n\in\mathbb N_0\).  Cell-centred and periodic sizes are multiplied by
\(2^n\); a vertex-centred axis uses

\[
 N(n)=(s_0-1)2^n,\qquad s(n)=N(n)+1.
\]

The box and alignment remain fixed.  A periodic half shift is
\(\sigma(n)=h(n)/2\), so it reproduces the source shift at \(n=0\) while
shrinking with the mesh.  The exact common envelope is

\[
 \max_f h_f(n)
 =\frac{8106479329266893}{254453378946433024}\,2^{-n}
 \longrightarrow0.
\]

The exact inventory contains 20 cell-centred reflecting axes, four
vertex-centred reflecting-dual axes, ten periodic-base axes, and two
periodic-half-shift axes.  Endpoint dual cells have half axis volume, and the
minimum tensor-volume factor is therefore \(1/4\).  Wrapped periodic storage
segments are treated as one connected torus cell.  These facts establish
vanishing mesh and shape regularity uniformly over this finite set of twelve
fixed-box families.

The ideal global gauge, product map, and physical-volume killing-average route
are defined at every level.  This is a geometric and qualitative averaging
result.  It does not yet prove source-uniform edge-form, map-defect, resolvent,
Mosco, or evaluator constants.

## Independent and adversarial checks

The exact frozen bytes were rerun as follows:

```text
.venv/bin/python -m ruff check \
  research/reports/encounter_multimodal_prr/code/build_continuum_c1_genuine_joint_refinement_family_v2.py \
  research/reports/encounter_multimodal_prr/code/validate_continuum_c1_genuine_joint_refinement_family_v2.py \
  research/reports/encounter_multimodal_prr/code/test_continuum_c1_genuine_joint_refinement_family_v2.py \
  research/reports/encounter_multimodal_prr/code/test_continuum_c1_genuine_joint_refinement_family_mutations_v2.py
All checks passed!

.venv/bin/python -m ruff format --check <the same four files>
4 files already formatted

.venv/bin/python \
  research/reports/encounter_multimodal_prr/code/build_continuum_c1_genuine_joint_refinement_family_v2.py \
  --check
PASS_C1_REFINEMENT_V2_BUILD ... sequences=12 ... complete_C1=false ...

.venv/bin/python \
  research/reports/encounter_multimodal_prr/code/validate_continuum_c1_genuine_joint_refinement_family_v2.py
PASS_C1_REFINEMENT_V2_VERIFY ... sequences=12 ... release_eligible=false

.venv/bin/python -m pytest -q \
  research/reports/encounter_multimodal_prr/code/test_continuum_c1_genuine_joint_refinement_family_v2.py \
  research/reports/encounter_multimodal_prr/code/test_continuum_c1_genuine_joint_refinement_family_mutations_v2.py
............................                                             [100%]
28 passed
```

The attack suite rejects changed sequence cardinality/order, incorrect
cell/vertex size laws, altered half shifts, nonvanishing mesh claims, weakened
shape factors, source-pin drift, source-row digest drift, unknown fields,
promotion flags, and malformed numeric or Boolean types.  The standalone
validator reconstructs all twelve sequences from the pinned sources rather
than importing the builder.

## Anti-vacuity and exact acceptance boundary

The historical anti-vacuity authority explicitly records
`policy_predecessor_order_independently_sealed=false`; the fixed-row member
specification records `genuine_refinement_sequence_present=false` and
`production_bridge_accepted=false`.  Round 172 does not mutate either file or
retroactively seal its predecessor ordering.

At \(n=0\), equality is established only for configuration geometry: sizes,
boxes, alignments, and periodic shifts.  It is not evidence that one common
ideal mass/rate/flux/gauge/map/killing member lies inside the saved production
intervals.  Such a claim still requires a separately ordered correlated
same-member receipt.

The following remain false:

```text
production_n0_correlated_containment_receipt_present = false
production_raw_acceptance                            = false
production_same_member_bridge_accepted               = false
concrete_control_specific_killing_constructed        = false
uniform_operator_or_mosco_constants_proved           = false
complete_C0 / complete_C1 / complete_C2 / complete_C3 = false
F0_complete / F1_complete                            = false
release_eligible / submission_eligible               = false
```

Round 172 therefore repairs the previously missing **genuine-sequence
geometry** only.  It is admissible input to a source-bound ideal theorem, not
to a production continuum or PRR science claim.
