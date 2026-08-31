# F1-to-F2 common-observable selector v1

Date: 2026-07-14  
Stage: **SCIENCE-FREE PRE-F1 MECHANICAL DESIGN**  
Decision: **GO-DESIGN / HOLD-IMPLEMENTATION / HOLD-F1 / HOLD-F2 / HOLD-MC**  
Authorized scientific command: **NONE**

## 0. Purpose and non-execution boundary

This note closes the selector and common-estimand gaps identified by Round
108.  It defines, before any new-control positive-budget value is evaluated,
one byte-unique operation that will:

1. consume only a fully certified internal F1-A topology result;
2. construct one common physical cut for each valley role and one common set
   of fixed time windows for each control;
3. require F1-B to evaluate all 12 finite-volume configurations on those exact
   same cuts and windows;
4. carry root-location/cut uncertainty and the complete 12-grid uncertainty
   into conservative common-observable intervals;
5. mechanically determine confidence-family allocations, a conditional power
   certificate, a capped two-pool trajectory count, and seed/chunk domains for
   a later F2 plan; and
6. fail closed on every missing, tied, nonfinite, nonrobust, infeasible, or
   dependency-mismatched case.

This is a design, not a selector implementation, F1 result, F2 plan, F3
manifest, Monte Carlo command, or scientific evidence.  It does not evaluate
`lp_m1`, `lp_m2`, or `lp_m3` at positive budget and must not be used to infer
their topology.  No manuscript, F0 design, F1 producer, schema, result, or
off-lattice code is changed by this note.

## 1. Required upstream identity

The future implementation must pin exact SHA-256 values for:

- the independently accepted fixed-control design replacing held v1;
- the accepted formal B0 selector/certificate or the explicitly accepted
  fixed-pilot branch;
- the accepted science-free F0 implementation and independent F0 audit;
- the F1 manifest and sealed two-stage orchestrator;
- this selector design, implementation, tests, runtime, and canonical schema;
- every control, physical parameter, configuration, threshold, and role; and
- the independent F1-A verifier used before the transition to F1-B.

The control order is fixed:

```text
0 = lp_m1
1 = lp_m2
2 = lp_m3.
```

The configuration order is fixed:

```text
0  O113/Base
1  E128/Base
2  O129/Base
3  O161/Base
4  M+
5  R+
6  MR+
7  MR+F
8  A_M
9  A_R
10 A_Y
11 A_MRY.
```

`MR+F` is the reference only after all 12 rows have passed.  Missing rows,
duplicate IDs, alternative order, a held row, a stale hash, or a reference
substitution is `HOLD_SELECTOR_INPUT`.

## 2. Exact arithmetic and canonical bytes

### 2.1 Numeric leaves

Every finite binary64 input is parsed from lowercase `float.hex()` and treated
as its exact dyadic rational.  JSON decimal parsing is forbidden.  NaN,
infinity, subnormal flush-to-zero, negative zero, locale-sensitive text, and
an unpinned floating environment are `HOLD_NUMERIC_LEAF`.

Define:

```text
RN64(x)   = binary64 round-to-nearest, ties-to-even of exact real x
down64(x) = greatest binary64 <= exact real x
up64(x)   = least binary64 >= exact real x.
```

All midpoint and lattice tie decisions use exact rationals before rounding.
Every interval operation is outward.  A native round-to-nearest helper may
not stand in for `down64` or `up64`.

### 2.2 Canonical serialization

Selector records use UTF-8 JSON with keys sorted by raw UTF-8 byte order, no
insignificant whitespace, one terminal newline, and fixed-order arrays.
Integers are base-10 JSON integers.  Binary64 values are lowercase
`float.hex()` strings, not JSON numbers.  Exact rationals are reduced strings
`numerator/positive_denominator`.  Null and empty arrays have distinct
meanings declared below.  Volatile wall time, host paths, process IDs, and log
timestamps are excluded from the hashed scientific payload.

Two independent processes must produce byte-identical canonical payloads.
Any canonical disagreement is `HOLD_SELECTOR_REPLICA_MISMATCH`.

## 3. Sealed two-stage F1 operation

The F1 manifest must authorize one noninteractive orchestrator with the fixed
dependency graph

```text
F1-A topology producer replicas
  -> independent F1-A verifier
  -> selector operation in Sections 4--7
  -> F1-B common-observable producer replicas
  -> independent F1-B verifier
  -> one complete F1 result
  -> independent final F1 audit.
```

There is no manual choice edge.

### 3.1 F1-A

F1-A must complete all 36 control-configuration topology rows and provide for
every stationary role:

- a nonempty outward root interval strictly inside its frozen role band;
- the typed interval-Newton inclusion and full-window exclusion ledger;
- content-addressed direct-from-zero state/action certificates supporting the
  root interval; and
- byte-identical producer replicas plus an independent verifier pass.

The internal transition status is exactly
`PASS_F1A_TO_COMMON_OBSERVABLE_SELECTOR`.  It is not a final accepted F1
scientific result.  Any other status stops the orchestrator, writes mandatory
not-run F1-B stubs, and returns `HOLD_F1A`; the selector is not called.

### 3.2 F1-B

After the selector emits one canonical cut/window payload, F1-B must evaluate
every control on every one of the 12 configurations at every selected cut,
cut-hull endpoint, window endpoint, and survival time.  Each evaluation is a
new validated direct-from-zero semigroup action under the already accepted F0
method; sequential unvalidated propagation is forbidden.

F1-B must save content-addressed state/action blobs and scalar projection
enclosures sufficient to reconstruct every survival, basin probability,
window probability, and contrast without another deterministic solve.  The
final accepted F1 result includes those blob hashes and the selector payload
hash.  F2 may only read them; F2 cannot ask for an extra FV state after seeing
F1 or MC output.

The orchestrator may expose diagnostic logs, but no person or process may
replace a cut, width, role, estimand, precision, or failed row.  Retrying a
technical failure is allowed only with the exact same bytes and output path
policy; a scientifically held operation is never retried with changed input.

## 4. Twelve-grid stationary-role hulls

For control `c`, let its ordered role list be

```text
lp_m1: P1
lp_m2: P1,Q1,P2
lp_m3: P1,Q1,P2,Q2,P3.
```

For role `r`, configuration `g` supplies

```text
X_c,r,g = [L_c,r,g,U_c,r,g].
```

Construct the exact outward 12-grid hull

```text
H_c,r = [ min_g L_c,r,g, max_g U_c,r,g ].
```

Require:

1. every leaf interval is finite, ordered, nonempty, and strictly inside its
   frozen role band;
2. every role has the same type and index in all 12 configurations;
3. the global role hulls are strictly ordered,
   `upper(H_c,r) < lower(H_c,r+1)`; and
4. the first/last hull is strictly inside `[0.5,35]`.

Touching or overlapping global role hulls, even when every single grid is
ordered, is `HOLD_ROLE_HULL_OVERLAP`.  A point estimate cannot break the tie.

## 5. One common physical valley cut

For each valley role `Qj` with hull `H=[L,U]`, define

```text
v_exact  = (exact(L)+exact(U))/2
v        = RN64(v_exact)
delta_v  = up64(max(exact(v)-exact(L),exact(U)-exact(v))).
```

Because `v` is the nearest binary64 to a midpoint of two finite ordered
binary64 endpoints, it must lie in `[L,U]`; this condition is nevertheless
checked.  The exact midpoint and tie-to-even result are serialized.

Require all cuts to be finite, strictly ordered, strictly inside their valley
role bands, and separated from every neighboring global role hull.  Otherwise
return `HOLD_COMMON_CUT`.

The common basin cuts are:

```text
lp_m1: []
lp_m2: [v_1]
lp_m3: [v_1,v_2].
```

An empty array for `lp_m1` is required.  `null`, a dummy cut, or omission is a
schema HOLD.

### 5.1 Basin convention

For a continuous event time `T` right-censored at `100`, the common point-cut
basins are

```text
M1 = P(T <= v1)
Mj = P(v_(j-1) < T <= vj)
Mm = P(v_(m-1) < T <= 100).
```

For `lp_m1`, `M1=P(T<=100)`.  Exact equality at a cut has probability zero
for the continuous off-lattice law, but the half-open convention is still
fixed for integer classification.

### 5.2 Cut-uncertainty envelope

The point cut `v_j` is the single future MC estimand.  In addition, F1-B must
propagate the complete root-location uncertainty by allowing each cut to vary
over its global hull.  With `F(t)=1-S(t)`, monotonicity gives:

```text
M1 robust range:
  [ F(L1), F(U1) ]

interior Mj robust range:
  [ F(Lj)-F(U_(j-1)), F(Uj)-F(L_(j-1)) ]

last Mm robust range:
  [ S(U_(m-1))-S(100), S(L_(m-1))-S(100) ].
```

Every scalar `F` or `S` in these formulas is itself an outward F1-B interval;
all subtraction is directed and the result is intersected with `[0,1]`.
An empty intersection is `HOLD_CUT_UNCERTAINTY`.

For `lp_m1`, which has no cut, the point and robust intervals are both the
same validated interval for `P(T<=100)=1-S(100)`.

For each grid, serialize both the exact-point-cut basin interval and the
cut-robust interval.  Their outward hull is the promoted per-grid basin
interval.  Thus all methods still use one point cut, while the deterministic
uncertainty honestly includes the 12-grid ambiguity in locating the valley.

## 6. Common finite-resolution windows

### 6.1 Fixed lattice and role centres

Use the exact time quantum and cap

```text
q_time = 2^-10
h_cap  = 0.4.
```

For every stationary role hull `[L_r,U_r]`, form its exact midpoint and round
to the nearest `q_time` lattice point, ties to the even lattice integer:

```text
n_r = roundTiesToEven( ((L_r+U_r)/2) / q_time )
c_r = n_r q_time.
```

The role centres must remain strictly ordered.  Define

```text
h_raw = min(
  h_cap,
  (c_1-0.5)/4,
  (35-c_last)/4,
  min_r (c_(r+1)-c_r)/4
),
```

where the final minimum is omitted for `lp_m1`.  Then

```text
n_h = floor(exact(h_raw)/q_time)
h   = n_h q_time.
```

Require `n_h>=1`.  Every operation above is exact-rational until the integer
round/floor.  No “nice” alternative width may be tried if this one fails.

### 6.2 Role windows

For each stationary role define the exact lattice window

```text
W_r=[c_r-h,c_r+h).
```

Every role hull must lie strictly inside its window, every window must lie
inside `[0.5,35]`, and the closures of distinct role windows must be disjoint.
Failure is `HOLD_ROLE_WINDOW`.

For `lp_m1`, additionally define equal-width shoulder windows

```text
W_L=[c_P1-4h,c_P1-2h)
W_R=[c_P1+2h,c_P1+4h).
```

They must lie inside `[0.5,35]` and be closure-disjoint from `W_P1` and one
another.  The factor-four boundary clearance in `h_raw` guarantees this in
exact arithmetic; the checks remain mandatory.

The window order is fixed:

```text
lp_m1: L,P1,R
lp_m2: P1,Q1,P2
lp_m3: P1,Q1,P2,Q2,P3.
```

All windows for one control have common width `w=2h`.  Different controls may
have different mechanically selected widths.  “Common” means identical
physical windows across all 12 FV configurations and the later off-lattice
process, not identical times across different controls.

### 6.3 Positive contrast pairs

The exact ordered contrast pairs are

```text
lp_m1: (P1,L), (P1,R)
lp_m2: (P1,Q1), (P2,Q1)
lp_m3: (P1,Q1), (P2,Q1), (P2,Q2), (P3,Q2).
```

For a pair `(A,B)`, use the probability contrast

```text
d_A,B = P(T in W_A)-P(T in W_B)
```

and report the average-density contrast `d_A,B/w`.  Because the widths are
equal, both have the same sign.  These positive finite-resolution contrasts
are the only MC “modal-pattern” estimands; they do not prove an exact root
count, unimodality, or absence.

## 7. F1-B common-observable evaluation

### 7.1 Required times and saved states

For each control, define the sorted exact set

```text
T_common = {
  0.5,2,5,10,20,35,50,75,100,
  every point cut,
  every cut-hull endpoint,
  every window endpoint
}.
```

Duplicate exact dyadics are removed before sorting.  Every configuration must
save a validated direct-from-zero state/action blob and survival enclosure at
every time in this set.  Missing one time on one grid is global
`HOLD_F1B_STATE_COVERAGE`.

For an exact window `[a,b)`, compute

```text
P(T in [a,b)) = S(a)-S(b)
```

with outward arithmetic and intersection with `[0,1]`.  Compute basin
probabilities from the common cuts in the same way.  The exact state/action
dependency ledger must be serialized; a point subtraction or a density-times-
width approximation is forbidden.

For the `MR+F` reference only, F1-B must also serialize one coherent planning
point law from the central values of the same saved validated state sequence.
Let `s_ref(t)` be the exact dyadic value of the pinned central survival
projection at each sorted `T_common` time, with `s_ref(0)=1`.  Require

```text
1=s_ref(0)>=s_ref(t_1)>=...>=s_ref(100)>=0
```

in exact arithmetic and require every `s_ref(t)` to lie inside its certified
survival interval.  Define every reference basin/window probability by exact
rational differences of this one survival sequence, never by independent
interval midpoints.  Require each resulting probability to lie in its
certified interval; the basin probabilities plus `s_ref(100)` must close
exactly to one, and the disjoint window probabilities must sum to at most one.
Failure is `HOLD_REFERENCE_POINT_LAW`.

This coherent point law is a conditional power alternative only.  The
outward intervals, not the central path, remain the scientific deterministic
certificate.

### 7.2 Complete 12-grid deterministic envelope

For every promoted common scalar `x` and configuration `g`, let its outward
interval be `I_g=[L_g,U_g]`.  With `ref=MR+F`, let `x_ref` be the corresponding
exact rational probability/survival value from the coherent reference point
law in Section 7.1; a contrast reference is the exact difference of its two
window reference probabilities.  Require `x_ref in I_ref`.  Define

```text
E_det(x) = up64 max over all 12 g of
           max(|exact(L_g)-exact(U_ref)|,
               |exact(U_g)-exact(L_ref)|).

C_det(x) = [down64(x_ref-E_det),up64(x_ref+E_det)].
```

The reference self-term is its full interval width.  All pairwise endpoint
differences, the full 12-grid hull, coherent `x_ref`, `E_det`, and `C_det` are
serialized.
`max(point difference,separate errors)`, a grid subset, or a favorable
reference replacement is forbidden.

For basin probabilities, `I_g` is the promoted hull of the exact-point-cut
and cut-robust intervals from Section 5.2.  For windows and fixed-time
survival, it is the common exact-set interval.  Contrasts are formed
outwardly from the corresponding common window-probability intervals before
the 12-grid envelope is applied.

### 7.3 Cross-method allowance and deterministic subtraction

Use the exact allowance caps and quantum

```text
tau_survival_cap = 0.01
tau_basin_cap    = 0.001
tau_window_cap   = 0.001
q_tau            = 2^-40.
```

For a survival or window probability, define

```text
b = min(x_ref-E_det, 1-(x_ref+E_det)).
```

For a basin probability with scientific floor `q0=0.005`, define

```text
b = min(x_ref-E_det-q0, 1-(x_ref+E_det)).
```

Require `b>0`.  For class cap `tau_cap`, set

```text
tau_raw = min(tau_cap,b/8)
tau     = q_tau floor(exact(tau_raw)/q_tau).
```

Require `tau>0`; no upward rounding or replacement cap is allowed.  The
future MC confidence interval for the scalar must lie strictly inside

```text
B_compat(x)=
[down64(x_ref-E_det-tau),up64(x_ref+E_det+tau)].
```

For a basin lower gate, the deterministic planning alternative is

```text
p_alt=down64(x_ref-E_det-tau)>0.005.
```

This is the required deterministic FV-uncertainty subtraction.  `x_ref`
alone is never a power alternative.

For every contrast pair `(A,B)`, first use the separately enveloped window
probabilities to define

```text
pA_low  = down64(pA_ref-E_A-tau_A)
pB_high = up64(pB_ref+E_B+tau_B)
d_low   = down64(pA_low-pB_high)
D_low   = down64(d_low/w).
```

Require `0<=pA_low<=1`, `0<=pB_high<=1`, `d_low>0`, and `D_low>0`.
Also require `pA_low+pB_high<=1`, because the two windows are disjoint and the
two marginal planning values must belong to one coherent multinomial law.
The values `d_low,D_low` are the promoted positive contrast lower bounds.
Define the exact planning split

```text
theta=RN64((exact(pA_low)+exact(pB_high))/2)
```

and require `pB_high<theta<pA_low`.  A tie is `HOLD_CONTRAST_SPLIT`; another
split may not be tried.

## 8. Confidence families

The later two-pool experiment has exact familywise error budget

```text
alpha_total = 1/20 = 0.05.
```

It is allocated before F1 as follows:

| family | total alpha | members across both pools | member alpha |
|---|---:|---:|---:|
| survival simultaneous bands | `1/100` | `3 controls * 2 pools = 6` | `1/600` |
| basin-probability intervals | `3/200` | `(1+2+3) * 2 = 12` | `1/800` |
| common-window probability intervals | `1/40` | `(3+3+5) * 2 = 22` | `1/880` |

The totals sum exactly to `1/20`.  No separate alpha is charged for a
contrast: every contrast is a deterministic difference of two already
simultaneous window-probability intervals.  Reusing those intervals does not
create a new coverage event.

For survival, use one Dvoretzky--Kiefer--Wolfowitz band per control/pool,
simultaneous over its entire selected `T_common` set.  For basin and window
probabilities, use two-sided equal-tail Clopper--Pearson intervals with the
exact member alpha.  The contrast gate is

```text
L_CP(A)>theta and U_CP(B)<theta,
```

which implies `L_CP(A)-U_CP(B)>0`.  Clopper--Pearson endpoint conventions are

```text
x=0: L=0
x=N: U=1
otherwise:
L=BetaInv(alpha/2; x,N-x+1)
U=BetaInv(1-alpha/2; x+1,N-x).
```

All beta quantiles and binomial probabilities require directed interval
evaluation under Section 9.3.  Wald, uncorrected pointwise intervals,
postselected KDE bands, and normal approximations are non-gating diagnostics.

Both pools must separately pass every member.  A pooled estimate is optional
and non-gating; one pool cannot rescue the other.

## 9. Conditional power and trajectory count

### 9.1 Declared scope

Power is conditional on the deterministic planning alternatives.  It does
not assert that the future off-lattice law equals the FV reference.  A failed
off-lattice gate remains a scientific failure, not a reason to top up or
replace the alternative.

The single joint planning law is the coherent `MR+F` reference point law from
Section 7.1.  Basin-floor and contrast calculations use the lower/higher
subtracted probabilities only as monotone worst-case bounds under that same
law: `p_ref>=p_alt`, `pA_ref>=pA_low`, and `pB_ref<=pB_high`.  They are not
different incompatible joint alternatives.

The desired joint power is at least `0.90`.  There are exactly 68 powered
assertions across both pools:

```text
6  survival compatibility assertions
12 basin-floor assertions
12 basin-compatibility assertions
22 window-compatibility assertions
16 positive-contrast assertions
--
68 total.
```

Allocate the exact failure probability

```text
beta_member=(1-0.90)/68=1/680
```

to every assertion.  A union bound then gives joint power at least `0.90` if
all 68 lower power bounds pass.

### 9.2 Exact admissible-count sets

For candidate per-pool size `N`, define count acceptance sets using the exact
Clopper--Pearson interval at the relevant member alpha:

```text
A_floor(N,q0) = {x: L_CP(x,N)>q0}

A_compat(N,[a,b]) =
  {x: a<L_CP(x,N) and U_CP(x,N)<b}

A_low_split(N,theta)  = {x: L_CP(x,N)>theta}
A_high_split(N,theta) = {x: U_CP(x,N)<theta}.
```

Strict inequalities are normative.  The sets are found by monotone integer
binary searches; an interval comparison that straddles equality is not
guessed and returns `HOLD_POWER_BOUNDARY`.

At planning Bernoulli probability `p`, the pass probability of a contiguous
count set `[x_min,x_max]` is the outward binomial probability

```text
P_p(x_min <= X <= x_max),  X~Binomial(N,p).
```

The powered assertions are:

1. **basin floor:** use `p=p_alt` and `A_floor(N,0.005)`;
2. **basin/window compatibility:** use `p=x_ref` and
   `A_compat(N,B_compat)`;
3. **positive contrast:** use `p=pA_low` for
   `A_low_split(N,theta)` and `p=pB_high` for
   `A_high_split(N,theta)`; the joint pass lower bound is

   ```text
   1-P_peak_failure-P_valley_failure
   ```

   by the union bound, regardless of multinomial dependence; and
4. **survival compatibility:** let `A_min` be the smallest distance from the
   reference survival curve to either boundary of its compatibility interval
   over `T_common`.  With

   ```text
   eps(alpha,N)=sqrt(log(2/alpha)/(2N)),
   ```

   the DKW confidence band lies inside the compatibility intervals whenever
   its empirical sup error is at most `A_min-eps(alpha,N)`.  The lower power
   bound is

   ```text
   1-2 exp(-2N(A_min-eps(alpha,N))^2)
   ```

   when `A_min>eps`, and zero otherwise.

Every lower bound must be at least `1-beta_member`.  No monotonicity of exact
Clopper--Pearson power in every integer `N` is assumed.

### 9.3 Byte-unique special-function evaluation

Exact rational inputs and integer counts are evaluated with an independently
pinned MPFR/MPFI-style directed interval implementation.  Start at 256-bit
precision and double through `512,1024,2048,4096`.  A comparison is accepted
at the first precision in that sequence for which its outward interval lies
strictly on one side of the required boundary; that first successful
precision and interval are serialized.  If 4096 bits cannot decide it, return
`HOLD_SPECIAL_FUNCTION_AMBIGUOUS`.  Library-native binary64 beta inverses,
binomial CDFs, or logarithms are not normative.

The implementation and an independently coded verifier must agree on every
integer threshold and directed probability interval.  This rule applies to
Clopper--Pearson beta quantiles, binomial tails, `log`, `sqrt`, and `exp` in
the DKW calculation.

### 9.4 Candidate schedule, rounding, and cap

Freeze

```text
chunk_size          = 100000 trajectories per control/pool/chunk
per_pool_cap        = 25000000 trajectories per control
whole_campaign_cap  = 50000000 trajectories across all controls and pools.
```

Test only the exact increasing candidate grid

```text
N_k=k*chunk_size,  k=1,...,250.
```

Choose for each control the first candidate for which all of that control's
powered assertions and both identical-size pools pass.  This is the first
passing allowed chunk schedule, not a claim of a globally minimal integer
sample size.  Let the three values be `N_m1,N_m2,N_m3`; different controls may
have different values, but their two pools must match exactly.

Require

```text
2*(N_m1+N_m2+N_m3) <= 50000000.
```

If one control has no passing candidate through 25,000,000 per pool, or the
whole-campaign sum exceeds 50,000,000, return `HOLD_N_CAP`.  No larger run,
sequential top-up, changed chunk size, or dropped control is authorized.

## 10. Seed, pool, and chunk derivation

The later F2 plan must derive, not choose, production randomness.  Define

```text
seed_basis = SHA256(
  ASCII("encounter-f2-common-observable-v1\0") ||
  bytes.fromhex(accepted_F1_manifest_sha256) ||
  bytes.fromhex(accepted_F1_result_sha256) ||
  bytes.fromhex(accepted_F1_audit_sha256) ||
  bytes.fromhex(selector_implementation_sha256)
).
```

For control index `c in {0,1,2}` and pool index `p in {0,1}`, define

```text
pool_digest(c,p)=SHA256(
  ASCII("philox-pool-v1\0") || seed_basis || uint8(c) || uint8(p)
)

pool_key64(c,p)=unsigned_big_endian(first 8 bytes of pool_digest(c,p)).
```

All six keys must be distinct and outside the separately pinned test-key set;
a collision is `HOLD_SEED_COLLISION`, not permission to add a salt.

Within one control/pool, trajectory ID `i=0,...,N_pool-1` occupies the high
64 bits of a Philox 128-bit counter domain and its draw-block counter occupies
the low 64 bits starting at zero.  Exhausting `2^64` draw blocks aborts that
trajectory and the complete run.  No two trajectories share a counter domain.
For Philox4x32, the exact word map is

```text
counter_word_0 = low32(draw_block)
counter_word_1 = high32(draw_block)
counter_word_2 = low32(trajectory_id)
counter_word_3 = high32(trajectory_id)
key_word_0     = low32(pool_key64)
key_word_1     = high32(pool_key64),
```

with unsigned arithmetic.  Changing word order or host-endian byte casting is
forbidden.

Chunk `j=0,...,N_pool/chunk_size-1` contains exactly

```text
[j*chunk_size,(j+1)*chunk_size)
```

in ascending trajectory-ID order.  Its ID is the lowercase hex SHA-256 of

```text
ASCII("philox-chunk-v1\0") || seed_basis || uint8(control) || uint8(pool) ||
uint64_be(chunk_index) || uint64_be(first_trajectory_id) ||
uint64_be(exclusive_last_trajectory_id).
```

Raw counts, candidate totals, failure flags, and payload SHA-256 are
append-only.

A technical restart reruns exactly the same incomplete IDs.  It may not rerun
only statistically inconvenient completed chunks.  Partial scientific counts
are not evaluated by the gating code.  There is one run at the frozen `N` and
no sequential top-up.

## 11. Required null, empty, and HOLD semantics

### 11.1 Required structural values

| field | `lp_m1` | `lp_m2` | `lp_m3` |
|---|---|---|---|
| valley-role array | `[]` | `[Q1]` | `[Q1,Q2]` |
| common-cut array | `[]` | one value | two values |
| cut-uncertainty array | `[]` | one value | two values |
| basin array | one value | two values | three values |
| role/shoulder windows | three values | three values | five values |
| contrast array | two values | two values | four values |

An empty array is semantic.  `null`, missing, a dummy zero, or a dummy one is
`HOLD_SCHEMA_NULLABILITY`.  A numerical field is `null` only for a row whose
enumerated status explicitly requires `NOT_RUN_AFTER_HOLD`; it can never mean
“not checked but pass.”

### 11.2 Enumerated hard stops

At minimum, the future schema must distinguish:

```text
HOLD_SELECTOR_INPUT
HOLD_NUMERIC_LEAF
HOLD_SELECTOR_REPLICA_MISMATCH
HOLD_F1A
HOLD_ROLE_HULL_OVERLAP
HOLD_COMMON_CUT
HOLD_CUT_UNCERTAINTY
HOLD_ROLE_WINDOW
HOLD_F1B_STATE_COVERAGE
HOLD_REFERENCE_POINT_LAW
HOLD_COMMON_OBSERVABLE
HOLD_DETERMINISTIC_ENVELOPE
HOLD_TAU_ZERO
HOLD_BASIN_FLOOR
HOLD_CONTRAST_NONPOSITIVE
HOLD_CONTRAST_PLANNING_INCOHERENT
HOLD_CONTRAST_SPLIT
HOLD_POWER_BOUNDARY
HOLD_SPECIAL_FUNCTION_AMBIGUOUS
HOLD_N_CAP
HOLD_SEED_COLLISION
HOLD_SCHEMA_NULLABILITY
HOLD_DEPENDENCY_HASH
HOLD_NO_REFIT_VIOLATION.
```

The first failure in the fixed operation order is the primary reason; all
already-known failures are serialized as secondary reasons.  Downstream rows
are mandatory `NOT_RUN_AFTER_HOLD` stubs.  A HOLD payload is still canonical,
append-only, and independently reproducible.

## 12. Future append-only artifacts

No artifact below is created by this design.  A future accepted package needs:

### Selector implementation record

```text
stage = f1_to_f2_common_observable_selector_f0
status = PASS_IMPLEMENTATION | HOLD_IMPLEMENTATION
design_sha256
implementation_sha256
test_sha256
runtime_hashes
canonical_schema_sha256
synthetic_and_mutation_ledger
authorized_scientific_command = null.
```

### F1 internal selector payload

```text
stage = f1_common_observable_selection
status = PASS_TO_F1B | HOLD_SELECTION
f1_manifest_sha256
f1a_result_sha256
f1a_verifier_sha256
role_hulls
common_cuts_and_uncertainties
common_windows
contrast_pairs
required_times
canonical_payload_sha256.
```

### Final accepted F1 additions

```text
selector_payload_sha256
all_12_grid_common_observable_intervals
content_addressed_state_action_blobs
cut_robust_basin_intervals
complete_E_det_envelopes
compatibility_allowances
positive_contrast_lower_bounds
power_planning_inputs
limitations.
```

### Later F2 plan

Only after an independent final F1 audit may a separate F2 plan apply Sections
8--10 and serialize actual alpha members, power checks, `N`, seeds, pools, and
chunks.  That plan needs its own independent audit.  This note is not that
plan and authorizes no F3 command.

## 13. No-refit law

After this design and its implementation are independently accepted, none of
the following may change in response to F1 or MC output:

- role-hull operation, midpoint/tie rule, cut uncertainty, or basin convention;
- time quantum, width cap, window centre/width operation, shoulders, or
  contrast pairs;
- required survival times, common-observable formulas, reference grid, or
  12-grid envelope;
- tau caps/quantum, deterministic subtraction, basin floor, or split rule;
- family membership, alpha/beta allocation, confidence method, power
  computation, special-function precision escalation, candidate schedule, or
  trajectory cap;
- seed basis, pool keys, counter domain, chunk size, or two-pool requirement;
  or
- any HOLD, null, canonicalization, hash, or stop rule.

Changing one item requires a new explicitly result-informed version and new
confirmation data.  Old F1/MC values cannot be reused as held out.  A failed
control, basin, window, contrast, power calculation, or pool cannot be removed
from the family.

## 14. Current decision

```text
selector mathematics/design          = WRITTEN
selector implementation               = NOT BUILT
synthetic/mutation suite               = NOT BUILT
independent selector audit             = NOT ESTABLISHED
accepted repaired F0 dependency        = NOT ESTABLISHED
F1-A positive-budget topology result   = NOT AUTHORIZED / NOT RUN
F1-B common-observable result           = NOT AUTHORIZED / NOT RUN
F2 plan                                 = NOT BUILT
F3 Monte Carlo                          = NOT AUTHORIZED
```

The only authorized next action is science-free implementation, synthetic
testing, and independent attack of this selector after the repaired upstream
designs are accepted.  No positive-budget or Monte Carlo command is
authorized by these bytes.
