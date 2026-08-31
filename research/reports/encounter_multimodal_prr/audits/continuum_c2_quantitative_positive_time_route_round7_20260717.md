# Round 7 audit: quantitative positive-time route and neutral cut layer

Date: 2026-07-17

Status: **CONDITIONAL ROUTE AUDITED / NEUTRAL CUT-LAYER FIXTURE PASS /
SOURCE-BOUND C2 ESTIMATE OPEN / COMPLETE C2 FALSE**

## 1. Audited theory object

The mathematical candidate is

- `notes/continuum_c2_quantitative_positive_time_route_candidate.md`;
- 539 lines, 17,567 bytes;
- SHA-256
  `25119e492cc8714e0804dded9bd4921070062309f441a96b3e0878c87ffa0314`.

It selects a conservative fixed-box route

```text
quantitative form defect
  -> complex-sector reconstructed resolvent estimate
  -> positive-time Dunford transfer
  -> fixed-box observable error for r=0,1,2 and tau>0.
```

The target `E_space,r <= C_r(tau,T,L) h^(1/2)` is conditional.  It is not a
proved C2 estimate.  In particular, QF1--QF2, the uniform complex-sector
resolvent estimate, source-bound constants, and production ideal-member
binding remain open.

## 2. Mathematical boundary checked

For a transverse contact disk of radius `a`, every cut cell lies in a
two-sided annulus of thickness `d_h`.  Under

```text
d_h < min(a, W/2-a),
```

the annulus has exact area `4*pi*a*d_h`.  Thus a shape-regular mesh with
`d_h <= C_shape h` gives an `O(h)` cut-layer measure and an `O(h^(1/2))`
weighted-L2 indicator error.  Smooth profile averages and the reconstruction
map contribute only `O(h)` under the stated regularity premises, so the
candidate keeps

```text
||K_h - V||_2 <= C_cut h^(1/2) + C_map h.
```

The form-defect step uses `L2 x L4 x L4 -> L1`; it does not differentiate the
sharp indicator.  The free SG/H2, discrete Sobolev, reconstruction, and
sectorial-resolvent bounds needed to justify this step are labelled as open
premises rather than imported from qualitative Mosco convergence.

For `A_sigma=A+sigma I`, the positive-time transfer uses the shifted Dunford
factor

```text
e^(sigma t) (z-sigma)^r e^(-t z).
```

Both independent exact-byte mathematical audits found the signs, shifts,
range-complement treatment, contour decay, and `tau>0` restriction correct:

```text
theory audit line A: P0=0 / P1=0 / P2=0
theory audit line B: P0=0 / P1=0 / P2=0
```

These verdicts apply only to the conditional route on the frozen SHA above.

## 3. Final neutral fixture bytes

The result-blind cut-layer fixture freezes only a unit-torus disk of radius
`1/4`, five dyadic refinements, and four face alignments.  Its final eight
files are:

| role | path | SHA-256 |
|---|---|---|
| source | `artifacts/data/continuum_c2_cut_layer_neutral_source_v1.json` | `6d512f1a03e7259c8342b248755cd7a1f33e500f12ebe83e6177505e0a417b6e` |
| fixture | `artifacts/data/continuum_c2_cut_layer_neutral_fixture_v1.json` | `4b09d65fe5092face47f30a43e7f5ad793dd03cf5368b441b332a1d611a59f2c` |
| builder | `code/build_continuum_c2_cut_layer_neutral_fixture_v1.py` | `817642704714de27374b437eac60f238795612a77874b29f84c027cc5acf3db0` |
| independent integer validator | `code/validate_continuum_c2_cut_layer_neutral_fixture_v1.py` | `0b5c517310228a1d3b1312c632e48a5af626414f1301d0890001e0d58b75b032` |
| static/two-build test | `code/test_continuum_c2_cut_layer_neutral_fixture_v1.py` | `4cb7d58a01dcaaf8c2ad30f7f1e789cf4495c31882a42858d0e85f112d6c8338` |
| mutation test | `code/test_continuum_c2_cut_layer_neutral_fixture_mutations_v1.py` | `0f3f177b194c8a2643e651c4b3e40e07186e6212f489b3410559fb144072ff2b` |
| currentness manifest | `artifacts/data/continuum_c2_cut_layer_neutral_fixture_currentness_v1.json` | `96981ac1abf0d40e9eb3a0f9d2fe9ab2f588e2cd901d6ffe26a0d2923704fbdd` |
| currentness gate | `code/test_continuum_c2_cut_layer_neutral_fixture_currentness_v1.py` | `9b3f366649c02c4df77568c84d38471e57b8c14231c01c1f685426c0975f233b` |

The builder counts with exact `Fraction` geometry.  The validator independently
rescales every coordinate by `2N` and repeats the closed-rectangle test with
integer min/max squares; it does not call the builder's counting routine.

## 4. Exact fixture facts

For `N=16,32,64,128,256`, the final 20 rows satisfy:

| face shift | cut | strict | tangent |
|---|---:|---:|---:|
| `(0,0)` | `2N+4` | `2N-4` | `8` |
| exactly one half-cell shift | `2N` | `2N-2` | `2` |
| two half-cell shifts | `2N` | `2N` | `0` |

The source carries a rational certificate for the strict chain

```text
pi < 5277328977275528/1679825970703125 < 355/113.
```

The first inequality follows from the Machin identity with a five-term upper
alternating sum for `atan(1/5)` and a two-term lower alternating sum for
`atan(1/239)`.  Builder and validator reconstruct the certificate separately.
The second gap is exactly

```text
45167474711/189820334689453125 > 0.
```

Together with `sqrt(2)<3/2`, the declared analytic rational cap is

```text
4 * (355/113) * (1/4) * (3/2) = 1065/226.
```

The observed finite maximum `cut_area/h=9/4` is recorded only as a frozen
fixture diagnostic and is explicitly forbidden from becoming a theorem or
production constant.

## 5. Executable verification

The final frozen bytes pass:

```text
builder --check                 PASS
independent integer validator  PASS
static and two-build suite      55/55 PASS
adversarial mutation suite      36/36 PASS
six-file currentness gate        6/6 PASS
```

Thus the counted assertion total is `97/97`, plus the two direct entry-point
passes.  The mutation suite rejects false pi bounds, malformed or extra
schema keys, changed methods/refinements/constants, strict/tangent changes,
duplicate JSON keys, stale bindings, and Python numeric aliases such as
`false -> 0`, `true -> 1`, `5 -> 5.0`, and `16 -> 16.0`.

Two independent final exact-byte audits, each run without edits, network, or
result/control payload reads, report:

```text
fixture audit line A: P0=0 / P1=0 / P2=0
fixture audit line B: P0=0 / P1=0 / P2=0
```

## 6. Adversarial repair chronology

The first six-file draft was not accepted.  A code audit found one P1 and two
P2 findings: the declared `355/113` value was not machine-proved to be above
pi, the source schema was not fully fail-closed, and currentness coverage was
incomplete.  The repair added the rational Machin certificate, strict source
schema, broader mutations, and a separate currentness manifest/gate.

A subsequent exact-byte audit then found a residual P2: Python dictionary
equality treats booleans, integers, and equal-valued floats as aliases.  The
final repair introduced recursive type-exact JSON comparison in both builder
and validator, type-exact term/refinement checks, type-exact artifact
reconstruction, explicit boolean checks in the currentness gate, and the
numeric-alias attacks listed above.  Only the final hashes in Section 3 carry
the clean verdicts.

## 7. Honest decision and next proof obligations

The neutral fixture establishes exact finite cut-cell counts and one analytic
geometry cap for the frozen toy geometry.  It does not evaluate contact
fractions, controls, budgets, semigroups, production centres, or observables.
The following remain false:

```text
source_bound_cut_layer_constant                  = false
QF1_uniform_discrete_Sobolev_control             = false
QF2_quantitative_free_SG_defect                  = false
complex_sector_reconstructed_resolvent_rate      = false
positive_time_r0_r1_r2_C2_rate                   = false
production_ideal_member_bound_to_C2              = false
complete_C2                                      = false
complete_C3                                      = false
release_submission_science_execution             = false
```

The next theorem task is to prove QF1--QF2 and the complex-sector estimate on
accepted refinement families.  In parallel, the Round-6 production design
must first become a symbolic control-free false-flag machine contract and an
independent acceptance receipt before any same-member production application
can contribute constants to C2.  `E_space`, `E_eval`, and `E_box` remain
separate ledgers throughout.
