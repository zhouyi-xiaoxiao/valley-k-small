# Round 65: Stage-B v3 result-blind design repair and adversarial self-audit

Date: 2026-07-14  
Role: design repairer, distinct from the Round-62 independent attacker  
Verdict: **GO-DESIGN / HOLD-EXECUTION**

## 1. Scope and non-execution boundary

This round creates a new Stage-B design version; it does not overwrite v2.
It used exactly the four requested result-blind inputs and wrote only the v3
design and this repair report.  It did not open a hidden/canonical scientific
result, evaluate a Stage-A candidate, construct mesh 65/97, run an FV solve or
Monte Carlo path, or modify a producer, manifest, main entry point, result,
auditor, or manuscript.

The input/output snapshot is:

| role | repository path | SHA-256 |
|---|---|---|
| Stage-B v2 design | `notes/positive_b_stage_b_validation_design_v2.md` | `8d64c54c2d4727583dc9ee513fc3fc58af57835283b68111a648f6ef33f63f84` |
| Round-57 re-audit | `audits/round_57_stageb_independent_reaudit.md` | `953bb602c29bb0ef2556e1a3ce63c0a309a4f298701c4ec7e6da9937194f0ab3` |
| Round-58 v2 resolution | `audits/round_58_stageb_v2_design_resolution.md` | `7f05c922a1835face49d58f0dfe06196e5a303b2909a4fc3f55fc2cd3d760d43` |
| Round-62 independent attack | `audits/round_62_stageb_v2_independent_attack.md` | `b72472e721a12c6d19e007273d6dd347430643f737d0168c2022010891a531b1` |
| new Stage-B v3 design | `notes/positive_b_stage_b_validation_design_v3.md` | `0c7119870e173bfbe5042b3f1c19c7c5851061940cab66e7e0dab98f54becd58` |

All four input hashes were recomputed before drafting.  The v3 hash above was
computed after the final residual-to-output certificate was added.

## 2. Executive resolution

V3 preserves every Round-62 pass that remains scientifically relevant:

- the same eight odd/even/refinement/box/`MR+F` configurations;
- physical partial-cell strip integration and the `1e-6` union-mass gate;
- a complete `MR+F`-centred empirical FV envelope rather than edge increments;
- universal off-lattice domination rate `Lambda=0.35`;
- a single global `alpha=0.05` union-bound architecture;
- a dependence-agnostic joint-GO power target at least `0.90`; and
- the narrow finite-volume numerical-cusp/event-law claim boundary.

It makes four structural changes:

1. eight fixed physical controls and seven grid-specific implicit solutions
   now have different schemas and different byte-identity semantics;
2. all seven cusp/fold implicit roles are solved on `MR+F`, giving each a real
   common reference and increasing the matrix to 120 rows;
3. off-lattice production is narrowed to the unchanged anchor and three phase
   representatives, with no fold-transition or lower-mode-absence claim; and
4. the four off-fold controls are selected only from future audited canonical
   Stage-A saved objects, without a new discovery evaluation.

After a finding-by-finding and newly introduced-risk attack, the design ledger
is:

```text
open design P0 = 0
open design P1 = 0
open design P2 = 0
```

This is a design GO only.  Execution remains held.

## 3. Round-62 finding-by-finding closure

### P0-1 — fixed controls versus grid-specific implicit outputs: CLOSED

V3 reserves `control` for eight exact physical inputs.  Their `theta`, weights,
budget, geometry, initial law, and horizon bytes remain unchanged on all grids.

The cusp and six fold roles are instead `implicit estimands`.  For every grid,
the cusp solves the fixed first/second/third time-derivative system and each
fold role solves the fixed fold system plus exact signed cusp-relative time
offset.  `T1` freezes saved seed ID, chart, equation, orientation, solver,
trust/match ball, and failure semantics; output `(t,theta,w)` is explicitly
grid-specific.

Correspondence is fail-closed: disjoint saved-role balls, exact branch IDs,
signed offsets, order/orientation checks, and no cross-grid warm start or root
reselection.  V3 therefore freezes the **map and solve**, not fictitious
future solution bytes.

### P0-2 — nonexistent off-lattice fold-side predicate: CLOSED BY DELETION

The off-lattice control set is exactly:

```text
anchor_m3, representative_m1, representative_m2, representative_m3.
```

No off-fold control is promoted.  There is no off-lattice cusp/fold locator,
fold-side topology change, unimodal-side absence, or global mode-count claim.

At expected mode counts `(3,1,2,3)`, the exact primitive statement counts are:

```text
basins                  3+1+2+3 = 9
windows                 5+1+3+5 = 14
positive local contrasts 4+0+2+4 = 10
```

The `m=1` schema has an empty contrast array.  It does not contain a
contract-zero, dummy, zero-alpha, or post-result-deleted contrast.  The method
claims only positively bounded local contrasts where a predeclared valley
exists.

### P0-3 — forbidden new mesh-65/97 selection: CLOSED

The v3 `T1` selector uses membership-consistent objects already serialized in
the future audited Stage-A canonical `candidate_generation`,
`screened_mesh_65`, `advanced_mesh_97`, and mesh-97 branch arrays.

It freezes:

- exact candidate-index membership and byte consistency;
- a central-secant tangent and explicit `+pi/2` normal;
- a local scale from saved adjacent branch nodes;
- a nonzero normal-distance floor and finite local capsule;
- a lexicographic pair rank and cross-branch no-reuse rule; and
- the required saved count-pair set `{(1,2),(2,3)}`.

Selected controls are verbatim saved candidate bytes.  No normal offset,
interpolation, renormalization, refit, or new model evaluation is permitted.
Insufficient saved coverage is `HOLD-T1`.

### P1-1 — no implicit-solution envelope/margin rule: CLOSED

All seven implicit roles now run on all eight configurations.  Every scalar
field and the scaled coordinate vector has an `MR+F`-centred envelope over all
grids.  A Newton--Kantorovich residual-to-coordinate certificate and interval
gradient conversion prevent raw residuals from masquerading as output error.

Location envelopes must consume no more than one quarter of the frozen match
radius.  Each lower/upper cusp/fold nondegeneracy or rank gate must pass on
every grid and retain three quarters of its scientific margin after the
reference-centred envelope.  Missing conversion, unmatched role, branch swap,
or overlap is HOLD.

### P1-2 — selectable `E_MC`, tolerances, intervals, and atomization: CLOSED

V3 fixes all previously free choices:

- basin, window, contrast, and survival time/bin definitions;
- half-open endpoints and exact `T=100` handling;
- `down64/up64` and 256-bit directed transcendental evaluation;
- outward one-sided Hoeffding probability intervals and two-sided DKW bands;
- exact probability/contrast `E_MC` formulas;
- equality formulas for `tau_M`, `tau_D`, `tau_p`, and exact-hex `tau_S`;
- interval-containment FV agreement and realized-precision gates;
- one 290-entry rational alpha atom/tail universe; and
- one 62-atom gate-to-power implication algorithm with no alternative
  atomization.

The power calculation uses exact binomial outside-interval probabilities or
outward DKW bounds, sums without independence, scans a fixed `200,000` grid to
`N_max=50,000,000`, and selects the first `N` with
`1-beta_all>=0.90`.  A nonpositive cap or infeasible `N` is `HOLD-T2`.

### P1-3 — auditor hash-cycle ambiguity: CLOSED

V3 states two explicit directed graphs.  Each scientific manifest pins its
upstream audited substitution, design/protocol, producer, and tests, but not
its independent auditor or no-cycle protocol.  The independent auditor
hard-codes the scientific-manifest hash and imports no producer.  A separate
pre-result audit protocol records manifest/auditor/auditor-test hashes and is
not pinned back by the manifest.  The same pattern is required for Stage B and
off-lattice production.

### P2-1 — branch frame and allocation serialization ambiguity: CLOSED

The saved node, predecessor/successor, central-secant tangent, orientation,
`+pi/2` normal, local scale, operation order, eligibility inequalities, and
tie-break tuple are explicit.  Both `theta` and weight binary64 hex strings are
stored and must reproduce byte-for-byte from the pinned chart.

The finite unit-sum condition is now exact:

```text
abs(fsum(weights)-1) <= 2^-48.
```

Even at its upper edge, the analytic rate bound is

```text
(0.01/0.04)*(1+2^-48)*exp(1/3)
  = 0.3489031062715236... < 0.35.
```

### P2-2 — base-cell count presented as total work: CLOSED

V3 calls its number only “base-state cells per one complete row pass.”  It
separately requires pre-run caps for augmented vectors, Newton/fold/root
iterations, Krylov actions, resident/scratch bytes, and wall time.  A cap hit
is an operational HOLD and cannot delete a row.

## 4. Recomputed matrix and workload

The eight state counts remain:

```text
1,442,897  2,097,152  2,146,689  4,173,281
2,762,406  2,862,252  3,683,208  7,165,305
```

They sum to `26,333,190`.  Every configuration now carries eight fixed and
seven implicit roles:

```text
logical roles                           = 8+7 = 15
configurations                          = 8
logical role--configuration rows        = 15*8 = 120
base-state cells per complete row pass  = 15*26,333,190
                                          = 394,997,850
two nominal deterministic executions   = 789,995,700
```

These values intentionally replace `114/352,006,020`.  Six fold roles gain an
`MR+F` row so the new implicit envelopes exist.  The four off-fold `MR+F` rows
remain deterministic FV challenges even though off-fold controls leave the MC
claim.  No implicit solve is byte-deduplicated before it runs.

## 5. Exact alpha and power arithmetic

The confidence atom/tail counts recompute exactly:

```text
12  * (1/1200)  = 1/100
78  * (1/5200)  = 3/200
84  * (1/5600)  = 3/200
116 * (1/11600) = 1/100
total             1/20 = 0.05.
```

The consistency count is independently decomposed as:

```text
8 pool-specific survival DKW atoms
+ (13 basin/tail + 14 windows)*2 pools*2 tails
= 8+108 = 116.
```

The joint-power primitives are exactly:

```text
2 pools * (4 survival processes + 9 basins + 4 S(100) + 14 windows)
= 62.
```

Pooled values, ten contrasts, and consistency gates are deterministic
functions of those pool atoms.  Hence they must be present in the implication
matrix but must not be double-counted as independent random atoms.

## 6. Newly introduced-risk attack

The repair itself was attacked for likely regressions:

| attack | result |
|---|---|
| Could fixed controls still be confused with solved cusp/fold bytes? | no; schemas, row semantics, deduplication, and GO wording are disjoint |
| Could `T1` silently run an absent offset candidate? | no; constructing/evaluating 65/97 is explicitly forbidden and missing saved membership is HOLD |
| Could the off-lattice result recover a fold/global-mode claim indirectly? | no; controls, flags, statement arrays, and maximum wording all forbid it |
| Could `m=1` acquire a synthetic contrast through alpha/power code? | no; exact schema count is zero and both ledgers omit such an atom |
| Could a fold role switch branches across grids? | no; exact signed equation, disjoint role balls, order/orientation, and audit reconstruction are mandatory |
| Could a small nonlinear residual be treated as a small coordinate error? | no; the Newton--Kantorovich and diagnostic-gradient conversions are mandatory |
| Could `MR+F` be absent for a fold yet an envelope still pass? | no; all 15 roles run on all eight configurations; missing row is HOLD |
| Could interval/atomization/sample-size choices move after FV values appear? | no; methods and transformation are fixed at T0; T2 only substitutes audited values |
| Could the seed or replicate create extra evidence? | no; SHA-256 counter inputs and pool/ID domains are exact; replicate repeats identical IDs with zero alpha/power |
| Could the manifest pin its auditor and create a cycle? | no; explicit external no-cycle protocols forbid the back-edge |
| Could workload be mistaken for a resource bound? | no; label and separate caps are explicit |

No new P0, P1, or P2 survived this attack.

## 7. Preserved physical checks

V3 retains, without weakening:

- all eight FV grids and the odd/even, refinement, separate-box, combined-box,
  and fine/enlarged corner diagnostics;
- the complete `MR+F`-centred formula rather than an edge-increment maximum;
- physical partial-cell overlap and inclusion--exclusion strip union;
- no false reflected-FV versus unbounded-free-OU upper-bound claim;
- `Lambda=0.35` with pre-ID finite/nonnegative/sum/rate checks;
- two disjoint pools, no top-up, exact-range retries, and one exact-ID
  reproducibility duplicate; and
- all continuum/PDE/off-lattice-cusp/global-mode flags remaining false.

## 8. Documentation-only verification

Only path/hash checks, text-contract assertions, and small integer/rational
arithmetic were executed.  The checks established:

```text
four requested input hashes match
v3 path is new; v2 still exists and is unchanged
8 state counts sum to 26,333,190
15*8 = 120
15*26,333,190 = 394,997,850
2*394,997,850 = 789,995,700
alpha atom arithmetic = 1/20 exactly
power primitive count = 62
0.001 and 0.01 binary64 hex literals match Python binary64
required HOLD/nonclaim/no-cycle strings are present
```

No scientific package entry point or scientific auditor was invoked.

## 9. Decision and execution boundary

The design repair is internally closed:

```text
P0 = 0
P1 = 0
P2 = 0

GO-DESIGN
HOLD-EXECUTION
AUTHORIZED-SCIENTIFIC-COMMAND: NONE
```

Execution can proceed only after a future audited Stage-A canonical result has
enough saved objects for `T1`, the v3 implementation/manifest/tests and both
no-cycle auditor chains are built and independently attacked, and every one-way
freeze transition succeeds.  This report is not a scientific result and does
not authorize mesh, Monte Carlo, manuscript, continuum, or PDE claims.
