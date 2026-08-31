# Round 105: fixed-control F0 design self-audit

Date: 2026-07-14  
Object audited: `notes/positive_b_fixed_control_robustness_design_v1.md`  
Object SHA-256: `891b49a3b9efbfa93c27c09e4f585a088b40f079c3ff5642536764f1523698d7`  
Audit type: static scientific/mathematical design attack  
Positive-budget science executed: **NONE**

## 0. Decision

```text
F0 scientific design       = PASS-CONDITIONAL
F0 implementation          = HOLD-NOT-BUILT
F1 manifest                = NOT AUTHORIZED
F1 positive-budget science = NOT AUTHORIZED
F2 planning                = NOT AUTHORIZED
```

The design successfully breaks the invalid old Stage-B dependency and freezes
a genuinely new three-control campaign. Its exact-control, topology,
configuration, interval-certificate, uncertainty-envelope, no-refit, and
append-only requirements are coherent enough to implement.

It does **not** authorize science. The rigorous time-exclusion path and the
half-cell SG grids are unimplemented. Until they pass science-free fixtures
and an independent F0 acceptance, the correct project status is
`GO-DESIGN / HOLD-IMPLEMENTATION / HOLD-SCIENCE`.

Priority counts: **P0 = 1, P1 = 2, P2 = 2**.

## 1. Scope and evidence

This audit read and cross-checked:

| artifact | SHA-256 |
|---|---|
| `notes/positive_b_fixed_control_robustness_design_v1.md` | `891b49a3b9efbfa93c27c09e4f585a088b40f079c3ff5642536764f1523698d7` |
| `audits/round_102_prr_posthold_strategy_attack.md` | `08ddd608de8b5431653d6f91f89f4869ca0f3a92bb6c4970d4eb9e406480b602` |
| `notes/modal_certificate_theory_and_prr_redirect.md` | `38dde114552d0cea69f714d7493d3cb6715e1b4ed436431045a50a57360326be` |
| `scratch/modal_certificate_lp_poc_result.json` | `6f04ef4c618677d6d26b80cd04e3d4f8c9918fd50a649cfc0dd0bf064ccce604` |
| `artifacts/data/positive_b_broad_four_slab_result.json` | `51e8eb4bdb652124865d0c39e6f36b99d13ed61578b161e0f75b142cada49401` |
| `notes/positive_b_stage_b_validation_design_v4.md` | `e5ca55c8a63d72b8f1bb0ded4d6ebba29a75d94e96ce07a6b7ebf15dcf100691` |
| `notes/positive_b_stage_b_validation_design_v5.md` | `136085075ad23fc22a40cf03725c9151f11ff356cff4f6f39e5c5fbb24317ddd` |

No producer, manifest, result, executable command, or frozen manuscript surface
was written or changed. Static arithmetic and exact-float checks did not
evaluate a positive-budget grid.

## 2. Static checks performed

### 2.1 Controls and exact normalization

The three raw `float.hex()` tuples in the design match the LP POC bytes. Their
exact dyadic sums were independently reconstructed:

| control | exact raw sum | POC normalized margin |
|---|---|---:|
| `lp_m1` | `36028797018963973/36028797018963968` | `0.8809904119598448` |
| `lp_m2` | `9007199254740991/9007199254740992` | `0.32540424848060423` |
| `lp_m3` | `36028797018963967/36028797018963968` | `0.13616273641487345` |

Defining the mathematical control as `raw/S_c` is necessary: none of the raw
tuples has exact real sum one, despite ordinary or compensated floating sums
sometimes rounding to one. Common positive rescaling preserves component
ratios and every strict alternating-sign inequality. It is therefore a
legitimate pre-science canonicalization rather than a new optimization.

The design correctly avoids claiming that the normalized mathematical
components retain an exact `0.03` floor. Strict positivity and exact rational
unit sum are the future F1 requirements.

### 2.2 Configuration and workload arithmetic

The 12 state counts recompute to:

```text
sum(configurations)          = 34,787,462
3 controls x configurations = 104,362,386 base-state cells
2 replicas                   = 208,724,772 base-state cells
logical F1 rows              = 36.
```

The existing eight-grid subtotal remains `26,333,190`; the four explicit
alignment grids add `8,454,272`. No row is implicitly deduplicated.

### 2.3 Full-window topology coverage

The frozen pieces cover `[0.5,35]` without a gap:

- `lp_m1`: positive prefix, one maximum band, negative suffix;
- `lp_m2`: positive prefix plus maximum/minimum/maximum bands; and
- `lp_m3`: positive prefix plus maximum/minimum/maximum/minimum/maximum bands.

All shared endpoints are existing LP checkpoints on the exact quarter grid.
The role counts are respectively `1`, `3`, and `5` stationary roots. The
design forbids a root on a role-band boundary and therefore does not double
count shared endpoints.

### 2.4 Markdown/static completeness

The design contains:

- three exact controls and historical-anchor exclusion;
- fixed `B`, geometry, supports, initial law, and finite window;
- odd, even, four explicit alignment, and four box configurations;
- root, curvature, peak, valley, prominence, basin, survival, mass-balance,
  positivity, boundary, envelope, refinement, parity, alignment, and box
  gates;
- a finite-dimensional continuous-time exclusion construction;
- F0→F1→F2 dependencies and append-only schemas;
- no-refit and hard-stop laws; and
- an explicit `AUTHORIZED SCIENTIFIC COMMAND: NONE` boundary.

No unfinished placeholder marker, permissive dense-scan fallback, or hidden
Stage-A/T1 dependency was found.

## 3. Mathematical attack on the continuous-time certificate

### 3.1 The local sub-Markov derivation is valid

For a killed row generator with outwardly proved

```text
Q_ij>=0 (i!=j),       Q 1=-k<=0,
```

the positive matrix `exp(Qs)` has row sums at most one. Hence
`exp(Q^T s)` is an induced-`l1` contraction, including on signed vectors. With
the column state `p(t)=exp(Q^T t)p0`, commutation gives, for every `t>=t_i`,

```text
f^(r)(t)
 = k^T exp(Q^T(t-t_i))(Q^T)^r p(t_i),
|f^(r)(t)|
 <= ||k||_infinity ||(Q^T)^r p(t_i)||_1 = M_r(t_i).
```

This proves the proposed local `M_2`, `M_3`, and `M_4` bounds without a
reversibility condition factor. It also proves the defect estimate for any
approximate path `z`:

```text
||z(t_i)-exp(Q^T t_i)p0||_1
 <= ||z(0)-p0||_1
    + integral_0^t_i ||z'(s)-Q^T z(s)||_1 ds.
```

The design's Lipschitz and Taylor intervals are two valid enclosures of the
same complete tile ranges; their outward intersection remains valid. Strict
sign exclusion plus one interval-Newton inclusion per frozen role band then
gives the required exact finite-dimensional root census on `[0.5,35]`.

### 3.2 The global self-adjoint route is rejected as the primary bound

Detailed balance still correctly implies

```text
H=D^(1/2) Q D^(-1/2)=H^T<=0
```

and the spectral estimate for `H^r exp(tH)` is mathematically sound. It is not
operationally sound as the v1 interval remainder. A separate old-control
diagnostic found condition factors `||D^(-1/2)p0||_2 ||D^(1/2)k||_2` of about
`4.3e8`, `9.3e8`, and `1.9e9` on `N33`, `N65`, and `N113`, respectively.
Those factors make the universal bound unusably wide even before interval
padding.

The design therefore keeps detailed balance, the Dirichlet-form proof, and
the self-adjoint global estimate as independent generator/cross-check fields,
but explicitly forbids that estimate from closing a time tile. This is a
correction to an otherwise valid but practically non-executable proof route,
not a relaxation to sampled evidence.

### 3.3 Local feasibility remains unproved and must fail closed

Context-only old-control diagnostics are substantially narrower: for `N65`,
the local `M_2(t_i)` values at `t_i=0.5,1,2,3,5` were approximately
`52.6,19.9,7.95,4.61,2.21`; for `N113`, values at `0.5,1` were approximately
`69.9,25.9`. These are neither new-control F1 evidence nor an implementation
certificate. They do not establish that the frozen depth 20 will resolve all
36 production rows.

The current FV code still uses ordinary floating actions and does not
serialize:

- outward Metzler, killed-row-sum, SG detailed-balance, and Dirichlet-form
  proofs on every required grid;
- direct-from-zero validated states at adaptive dyadic endpoints;
- independently verified `l1` defect integrals with binary64, projected-expm,
  sparse-action, parameter, and reduction error padding;
- outward `J_0...J_3`, `M_2...M_4`, and local interval intersections; or
- interval tilings and interval-Newton inclusions with replica identity.

Consequently no current `expm_multiply` value can satisfy Section 8. Adaptive
subdivision may help, but the fixed depth/Newton/resource limits must return
`HOLD` if any interval remains unresolved. If the local certificate is still
infeasible on production grids, it requires a pre-science design v2 and new
audit; an unaudited replacement may not be introduced after F1 values exist.

## 4. Adversarial findings

| ID | priority | open finding | impact | closure required |
|---|---:|---|---|---|
| R105-P0-1 | P0 | no validated finite-dimensional sub-Markov state/action/time-interval implementation exists | exact full-window topology—the key improvement over the historical anchor—cannot presently be evaluated | implement and independently validate Metzler/killed-row-sum structure, direct-from-zero defect-bounded `l1` actions, local `M_2/M_3/M_4`, interval intersections, and interval Newton on synthetic and small explicit matrices before any F1 manifest; keep detailed balance/self-adjoint similarity as an independent structural check only |
| R105-P1-1 | P1 | the four half-cell alignment grids are newly specified but no volume-aware SG/contact/profile implementation or proof exists | dropping them would remove the explicit alignment attack; naïve endpoint duplication or point sampling would change the model | implement dual half-volume reflecting grids and wrapped periodic shifts; prove conservation, normalization, positivity, detailed balance, and exact same-physics semantics |
| R105-P1-2 | P1 | no append-only F0 record, exact schema validator, canonical serializer, mutation suite, or independent implementation audit exists | the design cannot yet guarantee that future code consumed the frozen bytes or stopped on every mutation | build only science-free infrastructure, then write an immutable F0 attestation and obtain an independent acceptance; do not create F1 first |
| R105-P2-1 | P2 | interval precision, adaptive depth, memory, and time cost for 36 rows/two replicas are not benchmarked | the local bounds are much narrower than the rejected global self-adjoint bound, but the rigorous route may still be operationally infeasible | benchmark the certificate only on analytic/synthetic and scaled explicit matrices; freeze precision/resource limits before F1 and fail closed if any local tile/action cannot be certified |
| R105-P2-2 | P2 | F2 window/power/alpha/seed bytes are intentionally not built | a deterministic F1 pass alone is insufficient for the revised PRR spine | after—and only after—an independently accepted F1 result, apply the frozen selector and independently audit F2 before any off-lattice trajectories |

These are implementation/dependency findings, not permission to weaken the
scientific contract.

## 5. Specific failure attacks

### 5.1 Old Stage-B contamination

**Attack:** Could the existing accepted T0 or Stage-B selectors be reused to
avoid new infrastructure?

**Result:** No. The design names three LP fixed controls directly and has no
Stage-A cusp/fold roles. Its 36 rows, topology bands, exact-rational controls,
and 12-grid envelope are structurally different. Reusing old T1 output would
be a schema and dependency error.

### 5.2 Historical-anchor rescue

**Attack:** Could the known `B=0.01` three-mode anchor replace `lp_m3` if the
new control fails?

**Result:** No. The anchor is explicitly outside the primary envelope, F1
decision, and F2 selector. Any later context annex is append-only and has no
back edge. This closes the main selection-bias escape route.

### 5.3 “Same budget” ambiguity

**Attack:** The raw LP bytes do not sum exactly to one. Could different
floating summation order give three slightly different installed budgets?

**Result:** The design avoids this by defining exact dyadic ratios divided by
their exact rational sum. Future point approximations must enclose that target,
and the physical-volume budget error must pass `1e-12`. Silent `np.sum`,
clipping, or last-component repair is forbidden.

### 5.4 Alignment as changed physics

**Attack:** Does “half-cell shift” move the supports or OU potential?

**Result:** The design fixes domain and physical functions and changes only the
dual control-volume partition. Reflecting directions use half boundary
volumes; the periodic direction wraps translated cells without endpoint
duplication. If a future implementation instead shifts physical parameters,
the row is invalid and F1 holds.

### 5.5 Sampled root exclusion

**Attack:** Could the producer use the exploratory dense scan to declare no
extra roots?

**Result:** No. Every time tile must be strict-sign excluded or belong to one
unique interval-Newton root. Standard floating scans and raw residuals are
non-certifying diagnostics only.

### 5.6 Envelope cancellation

**Attack:** Could a combined alignment/box result look close while one
direction fails?

**Result:** No. `A_M`, `A_R`, `A_Y`, `A_MRY`, `M+`, `R+`, `MR+`, and `MR+F`
all have separate topology and pairwise gates in addition to the complete
12-grid reference envelope.

## 6. Go/no-go/kill decisions

### GO now

- freeze the design SHA;
- commission an independent design attack;
- build the science-free exact parser, schemas, synthetic fixtures, half-cell
  generators, sub-Markov/detailed-balance proofs, and validated local-`l1`
  time certificate; and
- benchmark only on synthetic/small explicit matrices.

### NO-GO now

- no F1 producer execution or manifest;
- no primary positive-budget grid;
- no historical-anchor substitution;
- no F2 windows/power and no off-lattice trajectories; and
- no manuscript promotion of 1/2/3 positive-budget control.

### Kill or version-bump criteria

The v1 F1 route must not start if any of the following persists:

1. Metzler/killed-row-sum, detailed balance, or negative semidefiniteness
   cannot be outwardly proved;
2. the direct-from-zero validated action defect or local
   `M_2/M_3/M_4` bounds cannot be bounded with all numeric errors padded;
3. the half-cell grids cannot preserve the same physical finite-volume model;
4. synthetic extra-root, unresolved-tile, wrong-volume, mutation, or null/HOLD
   fixtures do not fail exactly as specified;
5. resource limits make the certificate infeasible at the frozen depth and
   precision; or
6. an independent F0 audit finds a schema or logical ambiguity.

Resolution requires a new design version before any positive-budget output.
Removing a gate or falling back to a scan within v1 is forbidden.

## 7. Remaining implementation gates in order

1. exact design parser and canonical rational controls;
2. ordinary-grid and half-cell-grid FV constructors with physical-volume
   profile/contact integration;
3. edgewise sub-Markov and detailed-balance/Dirichlet-form certificates;
4. validated direct-from-zero semigroup states, independent `l1` defect
   verification, local derivative/remainder bounds, and diagnostic-only
   self-adjoint cross-checks;
5. dyadic time tiler, root-cluster logic, and interval Newton;
6. shape/mass/survival interval metrics and complete 12-grid envelope;
7. append-only schemas, canonical serializer, negative mutation suite, and
   two-process byte-identity harness;
8. independent F0 implementation audit and immutable attestation;
9. only then, a separately frozen F1 manifest; and
10. only after accepted F1, F2 off-lattice planning.

## 8. Final self-audit status

The design answers the Round-102 redirect with a cleaner and more general
scientific test: three prospectively frozen same-budget allocations and an
exact finite-window semidiscrete topology certificate across refinement,
parity, explicit alignment, and box challenges. It also prevents the
historical anchor or failed cusp route from becoming an escape hatch.

The principal unresolved risk is implementation and production feasibility,
not design intent. In particular, the local contraction formula is a proof
contract, not a statement that current SG actions already have outward error
bounds; the self-adjoint global estimate is deliberately diagnostic because
its condition factor makes it unusable as the primary enclosure.

**Final decision: `PASS-CONDITIONAL F0 DESIGN / HOLD IMPLEMENTATION / NO
SCIENTIFIC AUTHORIZATION`.**
