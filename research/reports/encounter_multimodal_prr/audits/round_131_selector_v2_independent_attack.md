# Round 131: independent adversarial audit of selector v2

Date: 2026-07-14  
Role: independent special-function, canonical-byte, dependency, state-law,
seed, HOLD, and resource attacker  
Numerical-tail decision: **ACCEPT THE ROUND-127 LOG-GAMMA / RECURRENCE /
GEOMETRIC-REMAINDER REPAIR**  
Whole-selector decision: **HOLD SELECTOR V2 / HOLD F1 / HOLD POSITIVE \(B\)**  
Findings: **P0 = 1, P1 = 3, P2 = 0**

## 1. Frozen bytes and execution boundary

The selector implementation and Round-127 repair were treated as untrusted at
the following hashes:

```text
code/f1_to_f2_common_observable_selector_v2.py
b6be1efa755659fac62143779690ae2cf67f06c8ea7c4eacfaf90db971862bc8

code/test_f1_to_f2_common_observable_selector_v2.py
f31b145525759f3ce59a4d29412e2021dcc4ee328c325e8f9e3d384f050fc2f0

audits/round_127_selector_large_n_tail_repair.md
1057818e550e6af4a803a73cb9e1734745dc3359ae57c3be81bf3ab25e3726eb

code/f1_to_f2_common_observable_selector_v2.schema.json
f631c72463f4f7d2e92d58b6b5cab7174de770a3c5a995a9d946bc359720f69c

code/f1_to_f2_common_observable_selector_v2_runtime.json
3ddd0fda64a6cb739776b78056050089dfb20662735356189ac0237fe18ba86c

code/f1_to_f2_central_projection_v1.json
ca55da389ac6b72b3359d5000249b52cd836db4ab8eacf19397a3b5d73f4c5d5

code/f1_to_f2_philox4x32_10_spec_v1.json
822a8aa14973227516669372a65ad55e12e63b84151bc51e593b61a2ef45a8d5

code/f1_to_f2_selector_test_keys_v1.json
cb273018dbca49cf09399e1504ffe5282eec84513891e2ddc4e79d3995dc185d
```

I added one independent attack module:

```text
code/test_f1_to_f2_common_observable_selector_v2_round131_independent.py
903b5364b13d60d5ce6e89b83c948a9def4cbad14ded432f86db25b53426f00e
```

The selector source, schema, runtime lock, projection spec, Philox spec,
test-key set, and Round-127 audit were not edited.  No F0/F1 artifact,
prospective control, positive-budget semigroup, trajectory, or Monte Carlo
sample was read or produced.  All probability fixtures are synthetic and
science-free.

## 2. Executive verdict

Round 127 repaired the large-\(N\) binomial arithmetic correctly.  An
independent derivation and independent exact/high-precision oracles found no
counterexample to

- the directed integer log-gamma boundary PMF;
- either outward PMF ratio;
- the monotone geometric remainder;
- any of the lower-tail, upper-tail, same-side-difference, or
  mode-straddling decompositions;
- precision nesting; or
- the strict Clopper--Pearson threshold
  \((40646,118891)\) at \(N=8{,}000{,}000\).

The one-call timing claim is also reproduced: the certified acceptance set is
returned in well below one second on this machine.

The whole selector cannot be accepted, however, for four independent reasons.

1. The envelope validator accepts both JSON integer `2` and JSON number
   `2.0` as `schema_version`, and the state-registry loader analogously accepts
   `1` and `1.0`.  The byte strings and SHA-256 digests differ.  This violates
   the selector's central byte-uniqueness invariant and can change every
   downstream content address and seed.  This is P0.
2. Repeated \(N=8{,}000{,}000\) calls in one process increase live RSS by
   about 100 MiB per call.  The candidate/power search necessarily calls the
   routine repeatedly, so a fast single call does not establish production
   feasibility.  This is P1.
3. `derive_pool_keys` consumes the test-key file without checking its pinned
   SHA at the point of use.  A drifted canonical file can change collision
   exclusion while the seed still names the old expected hash.  This is P1.
4. Malformed state-registry and seed dependency types can escape as raw
   `TypeError` rather than a canonical `SelectorError`/HOLD reason.  This
   breaks total deterministic HOLD output.  This is P1.

The independent tests include explicit current-behaviour reproducers for the
four findings.  Their green status means that each defect was reproduced as
described; it is not an acceptance signal.  Those tests must be inverted into
rejection/bounded-resource assertions after repair.

## 3. Independent derivation of the binomial DAG

### 3.1 Directed log-gamma boundary PMF: PASS

For \(X\sim\operatorname{Bin}(N,p)\), the boundary atom is

\[
 T_k=\Pr(X=k)
 =\exp\!\left[
 \log\Gamma(N+1)-\log\Gamma(k+1)-\log\Gamma(N-k+1)
 +k\log p+(N-k)\log(1-p)
 \right].
\]

All three gamma inputs are positive integers.  Under the production cap they
are exactly representable at 256 bits.  Directed `lngamma`, directed
subtraction/addition, directed logarithms, multiplication by the exact integer
counts, and directed exponential therefore form a valid outward DAG.

I checked `lngamma(j)` independently against a 2048-bit evaluation of
\(\log((j-1)!)\) using an exact integer factorial for

```text
j = 1, 2, 3, 4, 7, 17, 64, 127, 200, 1000.
```

Every alternate value was contained.  I then compared the complete boundary
PMF interval with exact `Fraction` values constructed from
\(\binom Nk p^k(1-p)^{N-k}\) at asymmetric central and extreme fixtures up to
\(N=2000\).  Every exact atom was contained, including a value of order
\(10^{-24}\).  An integer wider than the declared precision fails with
`HOLD_SPECIAL_FUNCTION_DAG`.

### 3.2 Ratio directions and monotonicity: PASS

Moving down from \(k\) in a lower tail uses

\[
 r_k=\frac{T_{k-1}}{T_k}
 =\frac{k(1-p)}{(N-k+1)p}.
\]

As the recurrence moves toward zero,

\[
 \frac{r_{k-1}}{r_k}
 =\frac{k-1}{k}\frac{N-k+1}{N-k+2}<1.
\]

Moving up from \(k\) in an upper tail uses

\[
 s_k=\frac{T_{k+1}}{T_k}
 =\frac{(N-k)p}{(k+1)(1-p)},
\]

and

\[
 \frac{s_{k+1}}{s_k}
 =\frac{N-k-1}{N-k}\frac{k+1}{k+2}<1.
\]

Thus once the applicable outward ratio is below one, every subsequent ratio
is no larger.  The unsummed finite tail \(R\) obeys

\[
 0\le R\le T_k\frac{r_k}{1-r_k}
 \quad\text{or}\quad
 0\le R\le T_k\frac{s_k}{1-s_k}.
\]

Four independent exact fixtures attacked both directions and both very
skewed/moderately skewed probabilities:

```text
(N,p,boundary,side)
(1000, 1/200,   40, upper)
(1000,199/200, 960, lower)
( 600, 1/20,    85, upper)
( 600,19/20,   515, lower)
```

For each fixture the independent test reconstructed all exact PMF numerators
over a common denominator, proved the ratio sequence decreased, computed the
exact omitted finite remainder, and checked both

```text
exact remainder <= independent infinite-geometric bound
exact remainder <= serialized MPFR remainder upper endpoint.
```

All four passed.  The two \(N=1000\) remainder examples were approximately
\(2.50361\times10^{-73}\), below their approximately
\(2.50553\times10^{-73}\) geometric bounds.

### 3.3 Range decomposition: PASS

Let \(F(k)=\Pr(X\le k)\) and \(S(k)=\Pr(X\ge k)\).  The code's three
nontrivial decompositions are exact:

```text
range left of a mode:       F(upper) - F(lower-1)
range right of a mode:      S(lower) - S(upper+1)
range straddling a mode:    1 - F(lower-1) - S(upper+1).
```

The eligibility inequalities are precisely the inequalities that make the
corresponding first outward ratio at most one.  Subtraction and intersection
with the exact probability interval \([0,1]\) are outward and cannot discard
the true probability.

The independent exhaustive oracle covered

```text
N = 0,...,19
p in {1/17,1/7,2/5,1/2,6/7,16/17}
every 0 <= lower <= upper <= N
total ranges = 9,240.
```

All 9,240 exact rational probabilities were contained.  Every one of the six
routes was reached:

```text
full_support
lower_tail
upper_tail
difference_of_lower_tails
difference_of_upper_tails
complement_of_two_tails.
```

An additional 72 fixed-seed random cases used \(75\le N\le2500\), varied
rational denominators, and independently constructed exact common-denominator
PMFs.  All exact probabilities were contained at both 256 and 512 bits, and
every 512-bit interval was nested in its 256-bit counterpart.

## 4. Production-scale threshold and resource attack

### 4.1 Strict threshold: PASS

For

\[
 N=8{,}000{,}000,\quad
 p_{\rm low}=1/200,\quad
 p_{\rm high}=3/200,\quad
 \alpha=1/800,
\]

the selector returns

```text
strict CP acceptance set = (40646, 118891).
```

An independent 512-bit oracle started from an exact integer binomial
coefficient and used direct power/PMF recurrence.  It did not call the
selector's log-gamma boundary PMF, interval operations, range decomposition,
or geometric-remainder routine.  At the strict contact
\(\alpha/2=1/1600=0.000625\), it obtained

```text
P_{1/200}(X >= 40645) = 0.0006346386783950603... > 1/1600
P_{1/200}(X >= 40646) = 0.0006236805198005712... < 1/1600

P_{3/200}(X <= 118891) = 0.0006218291991130698... < 1/1600
P_{3/200}(X <= 118892) = 0.0006282023578529866... > 1/1600.
```

This independently fixes both strict transition integers.

### 4.2 One-call elapsed time: PASS

The combined current-byte suite recorded

```text
existing Round-127 benchmark = 0.759846 s
Round-131 selector call      = 0.665008 s
independent neighbour oracle = 0.444354 s.
```

Five additional selector repetitions in one process took

```text
0.748421 0.776900 0.730723 0.832168 0.787353 s
median = 0.776900 s
maximum = 0.832168 s.
```

Thus Round 127's time improvement is real.

### 4.3 Repeated-call live-memory growth: P1

The same repetitions expose a resource defect that a one-call benchmark
cannot see.  A fresh subprocess measured current RSS after garbage collection:

```text
before any call  =  30,192 KiB
after call 1     = 130,848 KiB
after call 2     = 230,416 KiB
after call 3     = 330,256 KiB.
```

An eight-call diagnostic reached approximately 848 MiB.  `gmpy2.free_cache()`
and Python garbage collection did not stop the growth.  Isolated tail calls
showed the same monotone increase; the implementation creates directed MPFR
contexts at many recurrence nodes.  Whether the retained RSS is ultimately a
library cache, allocator retention, or a context lifetime defect does not
change the production consequence.

The intended candidate schedule evaluates many powered assertions over many
candidate \(N\) values.  A roughly 100 MiB increase per CP acceptance-set call
will exhaust memory long before that search completes.  Round 127 therefore
passes one-call latency but not the actual repeated-workload resource gate.

Required closure:

1. reuse or safely scope the directed MPFR contexts, or isolate evaluations in
   bounded workers whose termination releases memory;
2. demonstrate bounded live RSS over at least 100 identical \(N=8\)m calls;
3. run the complete 68-assertion candidate workload, not one acceptance set;
4. pin a peak-RSS ceiling in addition to the elapsed-time ceiling.

Disposition: **P1 / HOLD SELECTOR EXECUTION**.

## 5. Canonical schema and dependency attack

### P0.1 — JSON integer/float aliases break canonical byte uniqueness

The schema declares

```json
"schema_version": {"const": 2}
```

but neither the strict JSON loader nor the semantic validator requires the
decoded Python type to be exactly `int`.  JSON Schema numerical equality
treats `2` and `2.0` as equal for this `const`.  Consequently both of the
following envelopes validate:

```json
"schema_version": 2
"schema_version": 2.0
```

They have different canonical JSON bytes and different
`canonical_payload_sha256` values.  The independent reproducer builds both,
checks their bytes/digests differ, and confirms that the validator returns the
second value as a Python `float` while accepting it as version 2.

The pinned state-registry loader has the same defect for
`"schema_version": 1` versus `1.0`; both byte-distinct registries are
accepted when their respective hashes are supplied.

This is not harmless syntax.  The selector payload hash is echoed into F1-B,
enters the accepted F1 result, and can change downstream seed material.  Two
replicas can therefore encode the same declared semantic object into different
accepted content addresses.

Required closure: reject every JSON floating-point token in
`strict_load_canonical_json` (all physical nonintegers are already strings),
or enforce `type(schema_version) is int` at every unpinned semantic boundary.
Adding only JSON Schema `"type": "integer"` is insufficient in validators
that regard mathematically integral `2.0` as an integer.  Add inverse
mutations for `2.0`, `2e0`, registry `1.0`, and negative/positive zero forms.

Disposition: **P0 / HOLD BYTE PINNING, REPLICAS, AND ALL DOWNSTREAM SEEDS**.

### Dependency and envelope semantics that survive: PASS

The nonrecursive hash domain is correct: the digest is SHA-256 of canonical
`selector_payload_core` bytes, and the digest field is outside the core.
Changing an upstream dependency while keeping the independently supplied
expected map fixed gives `HOLD_DEPENDENCY_HASH`.  Even if an untrusted caller
changes both its payload and expected map, the hard-coded projection, Philox,
runtime, and test-key package edges reject a mismatch.  Schema validation runs
before dependency semantics; dependency validation runs before a lying HOLD
row.  Those precedence checks passed.

### P1.2 — Test-key dependency is not verified where it affects pool keys

`verify_rng_specs()` checks the test-key file SHA.  But
`derive_pool_keys()` calls `load_test_keys()` directly, and
`load_test_keys()` does not check
`EXPECTED_TEST_KEY_SET_SHA256` or enforce the frozen eight-entry shape.

The independent reproducer replaced `TEST_KEY_SET_PATH` with a canonical
empty-key document whose SHA differs from the expected hash.  With the seed
basis still naming the old expected test-key SHA, `derive_pool_keys()` returned
all six pool keys successfully.  A drifted file containing one derived pool
key instead changes the result to `HOLD_SEED_COLLISION`, still without first
reporting `HOLD_TEST_KEY_SET`.

Thus file drift changes collision semantics without a dependency HOLD unless
the caller happened to run a separate self-check first.  No sealed call edge
currently makes that ordering mandatory.

Required closure: verify the pinned SHA and exact schema/format/count at the
start of `load_test_keys`, or make `derive_pool_keys` call a verifier that does
so before reading the set.  Add empty, reordered, malformed-width, and
collision-injected file mutations.

Disposition: **P1 / HOLD RNG-SEED PACKAGE ACCEPTANCE**.

## 6. State registry, seed derivation, and HOLD attack

### 6.1 Pinned state and central projection: PASS apart from P0.1/P1.3

An independently encoded multi-component state path was accepted only when

- the registry bytes matched their externally supplied SHA;
- every state blob matched the hash bound to its exact time;
- times were strictly increasing and complete;
- the exact sum of component midpoint-roundings lay in both the state
  projection hull and scalar survival interval; and
- the resulting path was nonincreasing.

Swapping two blobs while retaining the registry failed with
`HOLD_DEPENDENCY_HASH`.  Adding a caller-supplied self-reported blob hash failed
with `HOLD_REFERENCE_POINT_LAW`.  A reversed binary interval failed, and a
duplicate registry time failed with `HOLD_F1B_STATE_COVERAGE`.  The Round-113
alternate-point-law defect is therefore genuinely closed for well-typed input.

### 6.2 Seed basis and pool domains: PASS apart from P1.2/P1.3

The seed basis exactly equals

```text
SHA256(
  "encounter-f2-common-observable-v2\\0"
  || accepted F1 manifest hash
  || accepted F1 result hash
  || accepted F1 audit hash
  || Philox spec hash
  || test-key-set hash
  || central-projection spec hash
  || runtime spec hash
).
```

All fields are decoded as 32-byte hashes before concatenation.  The six pool
keys independently recomputed as the first eight bytes of

```text
SHA256("philox-pool-v2\\0" || seed_basis || control_byte || pool_byte)
```

matched exactly, were unique, and avoided the current frozen eight test keys.
An injected collision gives `HOLD_SEED_COLLISION`.  Runtime hashes, the four
Philox known-answer vectors, and the science-free/no-authority flags all pass.

### P1.3 — Some malformed semantic types escape the canonical HOLD algebra

The registry loader applies `re.fullmatch` directly to
`state_blob_sha256`.  If a canonical JSON registry supplies an integer there,
Python raises

```text
TypeError: expected string or bytes-like object, got 'int'
```

rather than `SelectorError("HOLD_DEPENDENCY_HASH", ...)`.  Likewise,
`derive_seed_basis(None, ...)`, `derive_seed_basis(7, ...)`, and a bytes-valued
dependency raise raw `TypeError` from `bytes.fromhex` because only
`ValueError` is caught.

A crash is closed with respect to scientific execution, but it is not the
byte-unique canonical HOLD payload required by this selector.  Two replicas
or orchestrators can classify the same malformed edge differently.

Required closure: type-check every state-registry hash/time/interval leaf and
every seed dependency before regex/hex decoding; convert all malformed cases
to the declared dependency, coverage, reference-law, or numeric HOLD.  Harden
`_parse_interval` against non-sequences as part of the same pass.

Disposition: **P1 / HOLD TOTAL FAIL-CLOSED CONTRACT**.

### 6.3 HOLD order and stage rows: PASS for well-typed reasons

The implementation's 33-entry `HOLD_ORDER` is unique and byte-for-byte equal
to the schema enum.  `REASON_STAGE` covers every reason and names only declared
stages.  Reversed/duplicated input reasons are deduplicated and sorted by the
fixed rank; the earliest stage is primary and all later stage rows are
`NOT_RUN_AFTER_HOLD`.  A payload that reverses primary/secondary ordering or
lies about stage rows is rejected with `HOLD_SCHEMA` once dependencies are
valid.

## 7. Reproduction record

The final current-byte checks were

```text
../../../.venv/bin/ruff format --check \
  code/f1_to_f2_common_observable_selector_v2.py \
  code/test_f1_to_f2_common_observable_selector_v2.py \
  code/test_f1_to_f2_common_observable_selector_v2_round131_independent.py

../../../.venv/bin/ruff check \
  code/f1_to_f2_common_observable_selector_v2.py \
  code/test_f1_to_f2_common_observable_selector_v2.py \
  code/test_f1_to_f2_common_observable_selector_v2_round131_independent.py

../../../.venv/bin/python -m pytest -q -rP \
  code/test_f1_to_f2_common_observable_selector_v2.py \
  code/test_f1_to_f2_common_observable_selector_v2_round131_independent.py
```

Results:

```text
Ruff format       = 3 files already formatted
Ruff check        = All checks passed
pytest            = 62 passed
positive B read   = False
F1 executed       = False
Monte Carlo run   = False
```

The 17 Round-131 tests comprise independent correctness tests and explicit
finding reproducers.  In particular, the P0/P1 reproducers assert that the
current implementation exhibits the defect; they are not tests of desired
post-repair behaviour.

## 8. Final disposition

```text
directed log-gamma boundary PMF                 = PASS INDEPENDENT
lower/upper recurrence ratios                   = PASS INDEPENDENT
monotone geometric remainder                    = PASS INDEPENDENT
all range decompositions and endpoints          = PASS INDEPENDENT
9,240 exhaustive exact small-N ranges           = PASS INDEPENDENT
72 random exact medium-N ranges and nesting      = PASS INDEPENDENT
N=8,000,000 strict CP thresholds                = PASS INDEPENDENT
N=8,000,000 one-call elapsed time                = PASS INDEPENDENT
N=8,000,000 repeated-call RSS                    = HOLD P1
nonrecursive envelope digest                    = PASS INDEPENDENT
integer-only canonical JSON                     = HOLD P0
dependency package edges                        = PASS, EXCEPT TEST-KEY USE
test-key point-of-use hash                       = HOLD P1
pinned state registry/blob binding              = PASS INDEPENDENT
central projection and monotone path             = PASS INDEPENDENT
seed basis and six pool domains                  = PASS, EXCEPT TEST-KEY USE
HOLD order and well-typed precedence             = PASS INDEPENDENT
total malformed-input HOLD algebra               = HOLD P1
positive-budget/F1 authorization                 = NO
```

Decision: **HOLD SELECTOR V2**.  Round 127's numerical tail repair should be
preserved, but its bounded-subproblem PASS must not be promoted to a whole
selector or production-performance PASS.  Repair P0.1 and all three P1 items,
invert the finding reproducers, prove bounded repeated-workload RSS, then run a
fresh independent closure before authorizing F1 or any positive-\(B\) work.
