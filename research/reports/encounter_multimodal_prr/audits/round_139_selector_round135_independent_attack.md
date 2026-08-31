# Round 139: independent attack on the Round-135 selector candidate

Date: 2026-07-14  
Role: independent canonical-byte, worker-boundary, runtime, resource, state,
seed, and large-\(N\) attacker  
Decision: **HOLD SELECTOR V2 / HOLD F1 / HOLD POSITIVE \(B\)**  
Findings: **P0 = 1, P1 = 2, P2 = 0**

## 1. Frozen candidate and scope

I audited these exact candidate bytes:

```text
code/f1_to_f2_common_observable_selector_v2.py
118d33446c986c1ca07c129886000a0812550a3976e0d7c7879b9f833fdda5b1

code/test_f1_to_f2_common_observable_selector_v2.py
abe863ee3ce745940f723da95705f26a62b675f7f7fb64548a83937d9eeda208

code/test_f1_to_f2_common_observable_selector_v2_round131_independent.py
a4a404dae43ad9900b207754e9f36e75cab516dcce3af340901c5439c6afcf95

audits/round_135_selector_round131_repair.md
727fd6746d74133d3753682eae84ee302f95b4081f6b0dd03e43797a5e2de17c
```

I read Round 131, Round 135, and the byte-frozen pre-repair reproducer in
full.  The historical reproducer remains

```text
audits/frozen_tests/round131_selector_pre_repair_reproducer.py.txt
903b5364b13d60d5ce6e89b83c948a9def4cbad14ded432f86db25b53426f00e.
```

I added one independent attack module and did not edit the candidate source or
either frozen candidate test:

```text
code/test_f1_to_f2_common_observable_selector_v2_round139_independent.py
dc5c1b1aee821853bf9f8f84874bd1fac8195f09834ea2e001a04a3f4aa03b95
```

All fixtures are synthetic and science-free.  I did not read a prospective
control, run F1, evaluate positive \(B\), run a semigroup, generate a
trajectory, or run Monte Carlo.

## 2. Executive result

The Round-135 repair genuinely closes three of the four non-resource defects
from Round 131 and closes the repeated-memory defect for the narrow public
`cp_acceptance_set` primitive:

- every JSON floating token is rejected recursively;
- state-registry and seed malformed types return `SelectorError`;
- test keys are hash-, order-, identity-, and point-of-use bound;
- canonical worker request/response binding, timeout, exit, stderr, source,
  Python-binary, runtime-spec-file, peak-RSS, and result-shape checks work;
- repeated or distinct isolated CP workers leave parent RSS bounded; and
- the certified \(N=8{,}000{,}000\) threshold remains `(40646, 118891)`.

The whole selector is nevertheless held for three independent reasons.

1. **P0:** the worker hashes the runtime-spec file but never checks that the
   numerical runtime loaded in that worker actually equals the spec.  A worker
   can therefore issue a scientific PASS under an unverified gmpy2/MPFR/GMP/MPC
   runtime.
2. **P1:** process isolation covers `cp_acceptance_set` only.  The public
   binomial-power helper required by the 68-assertion schedule still evaluates
   in the long-lived parent and retains about 11 MiB per representative
   \(N=8\)m call.  The complete 68-assertion implementation and resource gate
   do not yet exist.
3. **P1:** there is no aggregate worker-concurrency bound.  Four distinct
   concurrent calls enter four worker launches simultaneously; the per-child
   256 MiB limit is not an aggregate cap.

A currently matching runtime and a successful science-free self-check do not
close P0, because neither is a mandatory predecessor inside the numerical
worker call edge.  Similarly, a bounded isolated CP primitive does not close
the resource contract of the absent full selector workload.

## 3. P0 — runtime spec is named, not verified, at numerical point of use

### 3.1 Code path

`_cp_worker_identity` binds only three file digests:

```text
selector source file
resolved Python executable
runtime-spec JSON file
```

The internal worker then performs

```text
_parse_cp_worker_request(raw)
_cp_acceptance_set_in_process(...)
```

without calling `verify_runtime_spec`.  The latter is the function that
actually hashes and compares the loaded gmpy2 extension, package initializer,
MPFR/GMP/MPC libraries, versions, MPFR exponent/context settings, jsonschema
version, and Python runtime against the pinned spec.

Thus the SHA of a declaration is checked, but the declared runtime is not.
An installed extension or shared library can drift while the runtime-spec
file and Python binary remain unchanged.  The CP worker would still compute
and serialize a PASS.

### 3.2 Independent reproducer

The Round-139 test replaces `verify_runtime_spec` with a function that must
raise `HOLD_DEPENDENCY_HASH` if called.  It then supplies a valid canonical
worker request to `_run_internal_cp_worker`.

Observed:

```text
verify_runtime_spec calls = 0
worker response status    = PASS
```

This is a call-edge test, not a claim that the current installed runtime is
already wrong.  The explicit self-check currently reports

```text
runtime_verified = true
status           = PASS_SCIENCE_FREE_SELF_CHECK.
```

The defect is that scientific evaluation does not require or echo that
verification.

### 3.3 Required closure

Before any special-function evaluation, the fresh worker must verify the
actual loaded runtime against the pinned runtime spec.  The canonical response
must bind the verified runtime identity, and the parent must validate that
binding.  A runtime mismatch must return `HOLD_DEPENDENCY_HASH` before a
threshold or probability is evaluated.  Add an inverse test in which the
worker's runtime verifier is forced to HOLD and no numerical evaluator is
called.

Disposition: **P0 / scientific certificate can be produced without its
declared runtime precondition**.

## 4. P1 — the 68-assertion resource path remains in process

### 4.1 Isolation boundary is narrower than the selector contract

Round 135 correctly routes public `cp_acceptance_set` through a fresh process.
However,

```text
binomial_precision_ladder_decision
dkw_power_interval
precision_ladder_decision
```

remain public in-process functions.  The design's powered assertions require
CP count sets followed by outward binomial pass probabilities, plus DKW power.
`validate_family_ledger` checks only that family counts sum to 68; no function
currently executes and serializes the complete 68-assertion candidate
workload.

This is not merely a private-helper bypass.  The required binomial pass
probability enters through the public `binomial_precision_ladder_decision`,
which directly calls the MPFR DAG in the caller process.

### 4.2 Independent live-RSS reproducer

A fresh subprocess made six identical representative calls:

```text
binomial_precision_ladder_decision(
    N=8000000,
    p=1/200,
    range=[40646,8000000],
    boundary=1/1600,
    relation="lt",
)
```

Every decision was `PASS`.  Garbage collection ran after every call.  Parent
RSS in KiB was

```text
30544, 42496, 53424, 64480, 75520, 86656, 97712.
```

The total increase was 67,168 KiB, with every increment above 10,900 KiB.
An earlier eight-call probe gave

```text
30320, 42240, 53168, 64224, 75280,
86400, 97472, 108496, 119536 KiB.
```

Process termination solves the retention defect for operations that actually
cross that boundary; it does not solve the in-process power evaluator.

### 4.3 Full-workload boundary

The true 68-assertion workload depends on later accepted planning inputs and
was correctly not fabricated.  Its absence, however, means there is no basis
for a whole-selector resource PASS.  The repair report's narrow statement
that the CP primitive no longer has a long-lived-process edge is supported;
its broader “all four Round-131 findings” candidate PASS is not.

Required closure:

1. move every special-function operation used by a powered assertion behind
   a mandatory fresh-process boundary, or evaluate one complete powered
   assertion in a bounded terminating worker;
2. remove or make unmistakably internal every in-process production bypass;
3. run a cache-disabled synthetic 68-assertion resource fixture without
   prospective controls; and
4. retain the true accepted-input 68-assertion workload as a mandatory pre-F1
   gate once those inputs legally exist.

Disposition: **P1 / Round-131 production-workload memory finding remains
open**.

## 5. P1 — no aggregate worker-concurrency limit

The LRU bounds completed cache entries but neither coalesces in-flight misses
nor limits distinct concurrent subprocesses.  A four-thread independent
attack used four distinct canonical inputs and a barrier inside a synthetic
`subprocess.run`.  The observed simultaneous launch count was

```text
maximum active worker calls = 4.
```

Two real, resource-controlled workers at \(N=1{,}000{,}000\) and
\(1{,}000{,}001\) confirmed that actual subprocesses can run concurrently.
Their child peaks were

```text
68,714,496 bytes
68,583,424 bytes
```

while parent RSS stayed between 30,880 and 31,088 KiB.  This is good evidence
that process termination bounds the parent.  It also confirms that each
concurrent child contributes a separate resource load.

At the production \(N=8\)m fixture, the combined suite measured one child at
141,836,288 bytes.  Therefore the 256 MiB per-child check cannot be treated as
an aggregate cap.  I did not launch many production-scale workers; the
four-call barrier proves the missing concurrency control without imposing
that avoidable load.

Required closure: pin the production orchestrator to a fixed aggregate
concurrency (preferably one during certification), enforce it in the worker
launcher rather than by convention, and add a concurrent inverse test whose
maximum active worker count is the pinned value.  If multiple parent processes
are allowed, the bound must also cross process boundaries.

Disposition: **P1 / unbounded aggregate worker count**.

## 6. Repairs that survive the independent attack

### 6.1 Recursive canonical-number aliases: PASS

The `parse_float` rejection hook applies recursively.  Independent mutations
covered top-level and nested `2.0`, `2e0`, `0.0`, and `-0.0`.  Integer `-0`
fails the canonical round trip.  Exact integer schema versions are checked at
the selector and registry semantic boundaries.  Boolean, string, null,
container, and malformed registry versions all fail with `SelectorError`.

### 6.2 Registry and seed totality: PASS

Independent registry fuzzing covered wrong types in

```text
raw bytes
external registry hash
schema_version
states container
row object
configuration
state_blob_sha256
survival_interval container and endpoints
time.
```

Seed fuzzing covered null, boolean, integer, bytes, bytearray, memoryview,
containers, uppercase, short, and nonhex dependency strings, plus wrong seed
basis types and lengths.  Every case returned `SelectorError` with a declared
HOLD reason; no raw `TypeError`, `IndexError`, or regex error escaped.

### 6.3 Test-key point-of-use identity: PASS

`derive_pool_keys` reaches `load_test_keys`, which reads one immutable byte
string, hashes that exact string before parsing, then checks exact shape,
version, format, purpose, count, lowercase width, order, identities, and
uniqueness.  Independent stale-hash and coherently rehashed mutations covered
empty, seven- and nine-entry, reversed, duplicate, uppercase, malformed-width,
null-entry, purpose, format, boolean-version, and float-version cases.  Every
mutation held before changing accepted pool-collision semantics.

### 6.4 Worker protocol and local TOCTOU checks: PASS within their scope

The request and response are canonical JSON.  Existing plus Round-139 attacks
cover request digest, response shape/types, source/runtime-file echoes,
timeout, start failure, exit status, stderr, output size, result range, worker
peak, and a post-worker identity mutation.  The public CP path has no silent
in-process fallback.  Cache keys include all exact rational components and
the three declared identities.

The local parent/worker source, Python-binary, and runtime-spec-file checks are
therefore accepted.  This PASS expressly excludes P0's missing verification
of the runtime described by that file and P1's aggregate concurrency.

### 6.5 Large-\(N\) numerical repair: PASS / no drift found

The Round-127 log-gamma boundary PMF, rational recurrence, monotone geometric
remainder, range decomposition, and precision ladder remain accepted.  The
live Round-131 exact and high-precision oracles still cover 9,240 exhaustive
small-\(N\) ranges, 72 random medium-\(N\) ranges, precision nesting, skew-tail
remainders, and both production threshold neighbours.

Current combined measurements were

```text
N=8,000,000 selector CP elapsed       0.939968 s
independent neighbouring-tail oracle  0.433982 s
strict CP acceptance set              (40646, 118891)
```

No normal approximation is used for a certified probability or final
threshold.  This numerical PASS does not override the runtime and resource
HOLDs.

## 7. Verification record

Commands:

```text
../../../.venv/bin/ruff format --check \
  code/f1_to_f2_common_observable_selector_v2.py \
  code/test_f1_to_f2_common_observable_selector_v2.py \
  code/test_f1_to_f2_common_observable_selector_v2_round131_independent.py \
  code/test_f1_to_f2_common_observable_selector_v2_round139_independent.py

../../../.venv/bin/ruff check [the same four files]

../../../.venv/bin/python -m pytest -q -rP \
  code/test_f1_to_f2_common_observable_selector_v2.py \
  code/test_f1_to_f2_common_observable_selector_v2_round131_independent.py \
  code/test_f1_to_f2_common_observable_selector_v2_round139_independent.py

../../../.venv/bin/python -I \
  code/f1_to_f2_common_observable_selector_v2.py --self-check
```

Results:

```text
Ruff format                 4 files already formatted
Ruff check                  All checks passed
pytest                      99 passed; exit 0
science-free self-check     PASS_SCIENCE_FREE_SELF_CHECK
positive B read             false
F1 executed                 false
semigroup/Monte Carlo       false
```

Finding reproducers are intentionally green: the runtime-verification,
in-process RSS, and concurrency tests assert that the frozen candidate exhibits
the reported defects.

## 8. Final disposition

```text
recursive float/integer JSON aliases          PASS INDEPENDENT
schema and registry exact-version types       PASS INDEPENDENT
registry malformed-input HOLD totality        PASS INDEPENDENT
seed malformed-input HOLD totality            PASS INDEPENDENT
test-key point-of-use hash/order/identity      PASS INDEPENDENT
canonical worker stdin/stdout                  PASS INDEPENDENT
source/Python/spec-file pre/post binding       PASS INDEPENDENT
timeout/exit/stderr/peak/result checks         PASS INDEPENDENT
actual numerical runtime point-of-use          HOLD P0
isolated CP parent RSS                         PASS INDEPENDENT
public full-power helper RSS                   HOLD P1
aggregate worker concurrency                   HOLD P1
complete 68-assertion workload                 NOT IMPLEMENTED / HOLD P1
large-N tail arithmetic and threshold          PASS INDEPENDENT
positive-budget/F1 authorization               NO
```

Decision: **HOLD SELECTOR V2**.  Preserve the canonical, state, seed,
test-key, worker-protocol, and large-\(N\) repairs.  Add mandatory actual-runtime
verification inside every numerical worker, isolate the full powered-assertion
path, enforce aggregate concurrency, and pass a fresh independent attack
before authorizing F1 or positive \(B\).
