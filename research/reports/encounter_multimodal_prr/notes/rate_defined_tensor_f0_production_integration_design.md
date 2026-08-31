# Rate-defined tensor F0 production-integration design

Date: 2026-07-14  
Stage: **SCIENCE-FREE F0 CORE IMPLEMENTATION**  
Decision: **PASS RATE-DEFINED TENSOR CORE + 12 CONTROL-BLIND PHYSICAL CONSTRUCTORS + FULL-WINDOW TOPOLOGY ENGINE / HOLD INDEPENDENT F0 ACCEPTANCE / NO F1 AUTHORIZATION**

## 0. Purpose and hard boundary

This note freezes the implemented production-integration core required by the
Round-107 verified-uniformization design.  The implementation is:

```text
code/rate_defined_tensor_f0.py
```

with tests and a neutral-only benchmark:

```text
code/test_rate_defined_tensor_f0.py
code/benchmark_rate_defined_tensor_f0.py
code/benchmark_physical_geometry_f0.py.
```

The implementation has exact physical configuration defaults but no physical
production-control default.  It did not
load the exact `lp_m1`, `lp_m2`, or `lp_m3` weights, evaluate a positive-budget
primary FV row, inspect a prospective root/time/jet value, create an F1
manifest, or alter v2 or the manuscript.  Its executable evidence uses only
synthetic rational controls, small analytic chains, and generic neutral tensor
grids.  The physical execution built only control-blind axes, support/contact
geometry, and initial marginals; it never formed a positive-budget primary
killing row or propagated a primary state.

This object is append-only method evidence.  A successful test process means
only that the generic rate-defined core passed its science-free fixtures.  It
does not authorize any scientific command.

## 1. Pinned inputs and implementation bytes

| object | SHA-256 | role |
|---|---|---|
| `notes/verified_semigroup_enclosure_design.md` | `860abf6f1f3b1d3466c8c1c8310266c65b7f9311438383983831243bb37b470e` | Round-107 rate-defined/uniformization contract |
| `code/verified_uniformization_enclosure.py` | `a4646f946b891133c972f62cd36a1cb177516793050c2b6e520cffceb57782ed` | directed Poisson, scalar reduction, and small-CSR reference layer |
| `code/test_verified_uniformization_enclosure.py` | `6b842112f71bf88d8447a88ccba21ef1d9cbe89676912e80789e7ce964acbe34` | reference-method fixtures |
| `notes/positive_b_fixed_control_robustness_design_v2.md` | `264cf2d2ef17feedcb3c1a5469e18b5c57ba5981b57dc6201147955df3684dcd` | current F0/F1 dependency and no-refit contract |
| `audits/round_111_exact_selector_independent_attack.md` | `719c450c99bbca9aa5ca97875d65fabc4687f2852ff9c4889808cb4f3d0f7ad4` | exact rational selector acceptance and raw-`S_c` rejection requirement |
| `code/rate_defined_tensor_f0.py` | `98ae6d219359ad676243786f03441e30d32891847da4bf0fde263af2e084b007` | rate-defined tensor, 12-row geometry, and topology implementation |
| `code/test_rate_defined_tensor_f0.py` | `0e454e4fbb81765f46673bb47f009830163332f200a5885d505c36bfcc4b9122` | science-free tests and mutations |
| `code/benchmark_rate_defined_tensor_f0.py` | `15e264826c1e77c2f62e1290f28dd981f62bfcb2b03625cc603fffe8afd485d4` | neutral-only matrix-free/CSR benchmark |
| `code/benchmark_physical_geometry_f0.py` | `b19a0bfe21d3a2e8a43fbc615255e24af6076016a50210ad3b86fece0d38d988` | control-blind 12-row physical-geometry benchmark |

The implementation/test hashes above are normative for this design.  Any code
change requires a new design version and audit; a later positive-budget value
may not motivate an in-place repair.

## 2. Exact input boundary

### 2.1 Outward scalar intervals

Every rate, killing value, control weight, support density, contact fraction,
and initial mass enters as finite binary64 endpoints `[l,u]`.  The endpoints
are interpreted as exact dyadic rationals.  Interval addition and
nonnegative multiplication are performed on exact `Fraction` endpoint values
before conversion outward to binary64.  An invalid, reversed, nonfinite, or
negative rate/killing interval fails closed.

### 2.2 Exact rational selector ingestion

The only accepted control source kind is:

```text
selector_json_numerator_denominator.
```

The parser first verifies the complete input byte hash and the method-only
top-level stage/HOLD status.  It then reads only:

```text
selector_results[control_id].selected.weights[j]
  .numerator
  .denominator
  .exact.
```

The three strings must agree exactly, every weight must be positive, and the
exact sum must be one.  Each rational is enclosed by adjacent binary64
endpoints.  Historical `raw/S_c`, raw-hex, or any alternative `source_kind`
is a frozen `HOLD_F0_CONTROL_SOURCE_FORBIDDEN` outcome.  Comparison-only raw
fields elsewhere in the selector artifact cannot reach the production-control
return path.

The tests use a synthetic neutral JSON fixture.  They do not load or display
the three prospective amended weights.

### 2.3 Initial law

The initial-state constructor accepts component intervals plus the bytes and
expected SHA-256 of their source object.  It requires:

```text
sum_i lower_i <= 1 <= sum_i upper_i,
exact_mass_cap = 1,
sum_i max(|centre_i-lower_i|,|upper_i-centre_i|) <= 1e-12.
```

It never silently normalizes the nominal vector.  The exact mass cap and its
source hash propagate into the uniformization ledger.

## 3. SG, half-volume, and periodic axes

### 3.1 Reflecting Scharfetter--Gummel axis

For exact vertices `x_i`, cell volumes `V_i`, exact potential samples `U_i`,
and diffusion `D`, the implemented edge rates are enclosed from

```text
r_(i,i+1) = D/(V_i (x_(i+1)-x_i)) B(U_(i+1)-U_i),
r_(i+1,i) = D/(V_(i+1) (x_(i+1)-x_i)) B(U_i-U_(i+1)),
B(z)       = z/(exp(z)-1).
```

`B` and `exp` are evaluated with directed MPFR at at least 96 bits; the
executed path uses 192 bits.  The first and last vertex-centred control
volumes are the exact half volumes.  The stationary mass is enclosed from

```text
pi_i = V_i exp(-U_i).
```

The identity `B(-z)=exp(z)B(z)` gives

```text
pi_i r_(i,i+1) = pi_(i+1) r_(i+1,i)
```

by construction.  The implementation also requires overlap of independently
formed outward conductance intervals on every edge.  Physical cell volumes,
including boundary halves, are therefore present in both `pi` and the rates.

The production layer also implements the baseline cell-centred reflecting
axis.  Its exact cell centres are `L+(i+1/2)(U-L)/N`, all volumes are
`(U-L)/N`, and the same SG/detailed-balance construction is used.  The exact
quadratic OU potentials correspond to diffusion `D/2` and mean `0.95` on the
midpoint axis, and diffusion `2D` and mean zero on the relative-parallel
axis.  Thus the exact potential difference equals the face-drift Peclet
quantity with the required sign; no sampled or rounded face drift is an
input.

### 3.2 Periodic axis and half-cell shift

The periodic constructor uses exactly `N` equal cells and never duplicates an
endpoint.  Rates are the exact-rational interval for `D/h^2` in both
directions.  The optional shifted grid translates every cell by exactly
`h/2`, wraps its exact segments, and stores the exact shift rational.

The exact `cell_overlap_fractions` routine recomputes overlap fractions on the
shifted/wrapped cell segments.  Tests demonstrate that the base and half-cell
shifted grids produce different local fractions while their physical-volume
integrals equal the same exact arc length.

### 3.3 Tensor reversibility and Dirichlet sign

The tensor stationary mass is the product of strictly positive axis masses.
Every free edge inherits the axis detailed-balance identity.  Nonnegative
Doi killing changes only the diagonal.  Consequently the tensor construction
has the discrete form

```text
x^T D Q x
 = -1/2 sum_edges conductance_ij (x_i-x_j)^2
   - sum_i pi_i k_i x_i^2 <= 0.
```

The method summary serializes the axis construction, half-volume axes,
periodic shifts, positive stationary masses, edge conductance proof, and
Dirichlet-form conclusion.  It does not use a floating near-zero eigenvalue as
this structural proof.

## 4. Doi killing intervals

For exact budget `B`, exact-selector weight intervals `W_j`, midpoint support
density intervals `Phi_(jm)`, and tensor contact-fraction intervals `C_i`, the
generic builder forms outward intervals for

```text
k_i = B C_i sum_j W_j Phi_(j,m(i)).
```

Each support density must enclose unit physical-volume integral over the
midpoint cells.  Each contact fraction lies in `[0,1]`.  No point sampling,
last-component repair, weight renormalization, or cell-count normalization is
performed.

The physical layer wires this path to all 12 v2 configurations in the
normative order.  It provides:

- exact binary64-dyadic physical parameters and boxes;
- cell-centred SG axes for the eight refinement/box rows;
- exact half-volume vertex axes for `A_M`, `A_R`, and `A_MRY`;
- exact `h/2` wrapped periodic shifts for `A_Y` and `A_MRY`;
- validated composite-Simpson compact-bump cell integrals, with a proved
  rational global fourth-derivative bound and directed MPFR values;
- directed analytic disk--rectangle intersections for the Doi contact
  fraction, including wrapped shifted cells; and
- analytically unit-normalized support and initial marginals.

The installed-budget functional is exactly `B_*`: all four support profiles
have analytical integral one, accepted selector weights must sum exactly to
one, and the transverse period is one.  Its dependency-aware relative radius
is therefore zero, rather than the width of a sum of independently rounded
cells.  The constructor remains control-blind until a separately pinned
exact-selector object is supplied; the 12-row execution below supplied none.

## 5. Rate-defined generator and outward operator radii

For each target off-diagonal interval

```text
r_ij in [l_ij,u_ij]
```

choose a binary64 centre `rhat_ij` inside that interval.  Choose `khat_i`
inside the killing interval and define, rather than import,

```text
qhat_ii = down(-sum_(j!=i) rhat_ij - khat_i).
```

The API accepts an optional `stored_diagonal` argument only to reject it with
`HOLD_F0_STORED_DIAGONAL_FORBIDDEN`.  No tolerant row-sum repair exists.

Let

```text
epsilon_ij   = max(rhat_ij-l_ij, u_ij-rhat_ij),
[dlo_i,du_i] = [-sum_j u_ij-k_i^u, -sum_j l_ij-k_i^l],
epsilon_ii   = max(qhat_ii-dlo_i, du_i-qhat_ii).
```

The exact rational ledger is

```text
delta_Q = max_i (epsilon_ii + sum_(j!=i) epsilon_ij)
        >= ||(Q-Qhat)^T||_1.
```

The validator independently recomputes every centre, diagonal, row error,
maximum target exit, maximum absolute `Qhat` row sum, and killing infinity
uncertainty from the input intervals.  Understating a saved `delta_Q` fails.

## 6. Uniformized centre and `delta_P`

The exact dyadic uniformization rate satisfies both

```text
lambda >= max target exit upper,
lambda >= max centre exit.
```

Every `Phat` coefficient is a downward binary64 rounding of the exact-dyadic
coefficient in `I+Qhat/lambda`.  Hence every coefficient is nonnegative and
every exact-dyadic centre row sum is at most one.  The implementation computes
two independent rational bounds:

```text
delta_P_direct = max row sum of coefficient distances from target P intervals,

delta_P_via_Q  = delta_Q/lambda
                 + max row sum of rounding distances between
                   I+Qhat/lambda and Phat.
```

Both are checked, and the smaller valid upper bound is the propagated
`delta_P`.  The validator recomputes both branches and rejects a changed
coefficient, super-stochastic row, low rate, or understated radius.

## 7. Matrix-free deterministic actions

The tensor storage contains per-axis forward/backward coefficient vectors and
one tensor self array; it stores no production CSR matrix.  For `d` dimensions
every output receives the frozen ordered term list

```text
self,
axis-0 forward incoming, axis-0 backward incoming,
...,
axis-(d-1) forward incoming, axis-(d-1) backward incoming.
```

Reflecting boundaries contribute explicit zeros; periodic boundaries use exact
rolls.  A deterministic pairwise array tree combines the terms.  Thus

```text
maximum incoming terms             = 1+2d,
maximum multiply/add operations    = 2(1+2d)-1,
3D frozen values                   = 7 terms, 13 operations,
roundoff gamma index               = 2(1+2d)=14 in 3D.
```

`Phat^T` is nonnegative.  For nonnegative `x`, its action error uses

```text
gamma_14 max_i sum_j Phat_ij ||x||_1 + N*15*eta.
```

The signed `Qhat^T` action uses the same tree and replaces the row-sum factor
by the maximum exact-dyadic absolute `Qhat` row sum.  Small-grid explicit CSR
matrices are constructed only as test oracles.

## 8. Directed uniformization, exact time, jets, and local M_r

The matrix-free propagation path reuses the pinned Round-107 directed-MPFR
Poisson enclosure and tail.  It validates the kernel once, partitions an exact
rational target time into exact equal rational chunks, and applies the
matrix-free `Phat^T` recurrence.  Per chunk it stores:

- exact duration and Poisson mean;
- allocated exact tail tolerance, directed tail upper, term count, term cap,
  and MPFR precision;
- frozen action gamma index and `delta_P` used;
- propagated power, Poisson-weight, accumulation, and final state radii.

The propagation record pins the initial source hash/error, exact mass cap,
kernel construction, exact rate, target time, elapsed time, and observed
round-to-nearest mode.  The audit rejects a tail, time, rate, initial hash,
rounding, or final-radius mutation.

From the validated state, the matrix-free signed action encloses

```text
z_r = (Q^T)^r p,
J_r = k^T z_r,
M_r = ||k||_infinity ||z_r||_1,
```

through order four.  The recurrence carries `delta_Q`, signed sparse-action
roundoff, killing infinity uncertainty, deterministic pairwise dot/norm error,
and the incoming state radius.  Thus the core supplies the state/jet/`M_2`,
`M_3`, and `M_4` ingredients needed by v2's interval-time tiles.

The science-free topology layer is now connected.  It freezes the exact
quarter grid, left-first bisection to depth 20, the local Lipschitz/Taylor
formulae for `[f']` and `[f'']`, and the outward intersection of those two
independent consequences.  A noncandidate tile must have strict derivative
sign.  One connected candidate cluster per role must be strictly inside its
frozen band and have the required curvature sign.  The layer then executes
all 12 interval-Newton steps with a ties-to-even binary64 midpoint, requires
at least one strict interior inclusion, and caps the final width at `0.05`.
Every saved tile must close the complete window without a gap or overlap.

`physical_root_bands_v2` and
`certify_physical_full_window_topology_v2` wire the immutable one-/three-/five-
root role bands and `[0.5,35]` window without a path to selector weights.  The
`MatrixFreeAbsoluteTimeJetOracle` adapter evaluates every requested time
directly from the pinned initial enclosure through validated uniformization,
then maps its `J_0,...,J_3` and `M_2,M_3,M_4` intervals into the tile engine.
It never advances from a previous tile.  A small-chain regression exercises
this adapter-to-tile connection.  The
in-module replay recomputes interval intersections, candidate components,
Newton images, step chaining, inclusion flags, final widths, and coverage.
The synthetic three-root test exercises maximum--minimum--maximum topology;
the physical-window wrapper is exercised with a neutral analytic oracle only.

## 9. Stable mutation outcomes

The module defines fail-closed codes for:

- invalid or negative intervals/rates;
- forbidden stored diagonal;
- forbidden raw-`S_c`/raw-hex control source;
- selector parse/hash/unit-sum failure;
- support normalization or initial mass/source failure;
- low uniformization rate;
- Q/Phat row or coefficient mutation;
- understated `delta_Q`/`delta_P`/killing/action ledger;
- malformed matrix-free action;
- corrupt Poisson tail;
- failed exact-time closure;
- malformed quarter-grid/full-window coverage;
- unresolved or disconnected topology tiles;
- corrupted interval-Newton arithmetic/trace;
- runtime rounding/subnormal failure; and
- resource-cap exhaustion.

The tests exercise stored-diagonal, raw-`S_c`, sign, row, `delta_Q`,
`delta_P`, rate, tail, time, rounding, initial-source, support, action,
Poisson-term, frozen-limit, coverage, Newton-step, and direct-from-initial
mutations.  The Round-111 one-ulp `t=5.5` values are kept distinct unless an
explicit outward interval encloses both.

## 10. Executed science-free evidence

Runtime:

```text
Python   3.12.13
macOS    26.5.2 arm64
NumPy    2.5.1
SciPy    1.18.0
gmpy2    2.2.1
```

The combined Round-107 reference and new integration suite returned:

```text
PYTHONMALLOC=debug
python -X dev -W error -m pytest -q -p no:cacheprovider \
  code/test_verified_uniformization_enclosure.py \
  code/test_rate_defined_tensor_f0.py

35 passed
```

Static checks returned:

```text
ruff check:        All checks passed
ruff format check: 3 files already formatted
py_compile/compileall: PASS
```

The test evidence includes:

- exact SG half-volume rates and conductances;
- all 12 exact physical axis shapes, parities, boxes, half-volume flags,
  periodic shifts, state counts, and the `34,787,462`-state workload identity;
- control-blind physical compact-bump/contact/initial geometry;
- nonzero-potential MPFR SG balance enclosures;
- shifted periodic overlap reconstruction;
- selector/control and initial-state source hashes;
- all small-row interval corners inside exact `delta_Q`/`delta_P`;
- deterministic matrix-free `P^T` and signed `Q^T` actions versus explicit
  CSR;
- matrix-free uniformization versus an independent dense exponential;
- scalar jets and `M_r` versus the same dense target; and
- a three-root full-window synthetic topology plus the exact v2 physical
  `[0.5,35]` wrapper; and
- all required corruption classes.

All 12 control-blind physical geometries were also constructed by the pinned
benchmark at the default
192-bit/16,384-panels-per-unit settings in one fresh science-free process.
The final run took `52.6171 s` total (`3.96--4.69 s` per row).  Across the 12 rows:

```text
maximum summed support-mass interval width   4.482e-13
maximum summed initial-marginal width        4.482e-13
contact-area interval width range            4.959e-16 -- 6.959e-16
installed-budget dependency radius           0 exactly
prospective selector values read             false
positive-B primary row evaluated             false
```

The contact-area intervals contained the independent scalar oracle
`pi*contact_radius^2` for every row.  This run constructed axes, support and
initial marginals, and relative contact fractions only; it did not allocate a
million-state killing vector or run a semigroup action.

## 11. Neutral `33^3` benchmark

The benchmark profile is a generic zero-potential tensor with one reflecting
half-volume axis, two periodic axes (one shifted by half a cell), and an exact
synthetic death coefficient `1/256`.  It is not a physical installed budget
and has no selector control.

The executed `33*33*33 = 35,937` state, 10-action result was:

```text
states                         35,937
explicit CSR nonzeros         249,381
kernel build                  7.6744 s
10 matrix-free P^T actions    0.00311 s
10 explicit CSR P^T actions   0.00172 s
explicit CSR construction     4.2532 s
matrix-free/CSR l1 distance   1.13971e-16
tensor numeric storage        865,656 bytes
explicit CSR storage          3,136,324 bytes
maximum incoming terms        7
maximum floating operations   13
```

This benchmark supports implementation feasibility and the intended storage
scaling only.  It does not establish a ceiling for the 36-row campaign or the
`7,165,305`-state `MR+F` configuration, and its action timing excludes the
one-time exact-Fraction construction audit.

The benchmark refuses to run without the explicit flag:

```text
--science-free-neutral.
```

## 12. Remaining gates

### Closed implementation gate — 12-row physical construction

The 12-row configuration/geometry implementation and mutations now exist and
the default control-blind construction passed on every row.  The exact real
selector artifact was intentionally not read in this F0 construction run.
Its already implemented hash/path/numerator/denominator parser remains the
only control entry point, and production expansion remains downstream of that
entry point.  Closing this implementation gate does not close independent F0
acceptance and does not authorize an F1 value.

### P0-2 — no append-only production schema/independent verifier exists

This note is not the v2 F0 attestation.  A future schema must content-hash all
coefficient arrays, exact times, runtime/dependencies, state/action blobs,
per-anchor ledgers, and HOLD/null branches.  A separately coded verifier must
recompute the diagonal, `delta_Q`, both `delta_P` branches, Poisson/tail,
matrix-free actions, reductions, state radius, jets, and `M_r`.  Two complete
process replicas must agree on canonical bytes.  The validator in this module
is intentionally strong but is not implementation-independent.

### Closed implementation gate — interval-time topology

The v2 quarter-grid, local/Taylor intersections, complement signs, connected
root boxes, 12-step interval Newton, curvature, exact role bands, and
complete-window coverage are implemented and pass synthetic/mutation tests.
The remaining P0 is independent serialization/replay and acceptance of these
objects; an in-module replay is not its own independent audit.

### P1-1 — scaled resource ceiling is open

The neutral `33^3` result cannot be extrapolated as a production promise.
The 52.75-second all-geometry run closes constructor feasibility only; it did
not allocate the `7,165,305`-state killing/diagonal/state arrays or execute a
Poisson recurrence.
Before F1, science-free/historical method-only benchmarks must freeze maximum
wall time, memory, chunk count, Poisson terms, output radius, and failure
policy for at least one substantially larger matrix-free row and the expected
largest configuration.  Failure must remain HOLD; it may not relax a
tolerance, delete a configuration, or select a different algorithm after
prospective output is visible.

### P1-2 — continuum/full-window analytical certificate is external

This finite-dimensional core does not supply outward continuum coefficient
enclosures, B0 box/complement bounds, or the mixed-jet analytical transfer to
`B=0.01`.  Those remain separate scientific gates even after F0 implementation
passes.

## 13. Current ledger

```text
rate-defined generic tensor kernel          = PASS
SG/periodic/half-volume constructors         = PASS ON SYNTHETIC + ALL 12 PHYSICAL GRIDS
exact-selector rational ingestion            = PASS ON SYNTHETIC PINNED JSON
old raw-S_c/stored diagonal rejection         = PASS
derived diagonal and delta_Q/delta_P          = PASS, EXACT LEDGERS
matrix-free nonnegative Phat^T action         = PASS AGAINST CSR
matrix-free signed Qhat^T jets/M_2/M_3/M_4    = PASS AGAINST DENSE/CSR
initial-state mass/source enclosure           = PASS
directed Poisson/exact-time propagation        = PASS THROUGH ROUND-107 CORE
mutation suite                                = PASS
neutral 33^3 feasibility benchmark            = PASS, NOT A PRODUCTION CEILING
all 12 physical v2 constructors               = PASS CONTROL-BLIND DEFAULT BUILD
append-only schema and independent verifier    = NOT BUILT / P0
adaptive full-window topology layer            = PASS SYNTHETIC + V2 ROLE/WINDOW WIRING
largest-row/36-row resource ceiling            = OPEN / P1
continuum analytical certificate               = EXTERNAL HOLD / P1
prospective positive-B control evaluated       = NO
F1 authorized                                 = NO
authorized scientific command                  = NONE
```

**Decision:** the Round-107 rate-defined tensor core, control-blind physical
12-configuration layer, and complete-window topology engine now exist and pass
their science-free checks.  The repository must still report global
`HOLD_F0`: no append-only full attestation, implementation-independent replay,
or two-replica canonical acceptance exists yet, and the largest-state resource
ceiling remains open.  No positive-budget LP-control evaluation is authorized
from these bytes.
