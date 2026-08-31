# Round 135: selector-v2 repair of the Round-131 findings

Date: 2026-07-14  
Role: implementer, canonical-byte and resource repair  
Repair decision: **CANDIDATE PASS FOR ALL FOUR ROUND-131 FINDINGS**  
Release decision: **HOLD F1 / HOLD POSITIVE B PENDING A NEW INDEPENDENT ATTACK**

## 1. Frozen pre-repair evidence and scope

Round 131 attacked these exact pre-repair bytes:

```text
code/f1_to_f2_common_observable_selector_v2.py
b6be1efa755659fac62143779690ae2cf67f06c8ea7c4eacfaf90db971862bc8

code/test_f1_to_f2_common_observable_selector_v2.py
f31b145525759f3ce59a4d29412e2021dcc4ee328c325e8f9e3d384f050fc2f0

code/test_f1_to_f2_common_observable_selector_v2_round131_independent.py
903b5364b13d60d5ce6e89b83c948a9def4cbad14ded432f86db25b53426f00e
```

Before inverting the five finding reproducers, I copied the third file byte
for byte to the non-pytest path

```text
audits/frozen_tests/round131_selector_pre_repair_reproducer.py.txt
903b5364b13d60d5ce6e89b83c948a9def4cbad14ded432f86db25b53426f00e
```

`cmp` returned zero.  Thus the old green defect reproducers remain executable
historical evidence even though the live Round-131 file now asserts repaired
behaviour.

This repair used only synthetic, science-free probability fixtures.  It did
not read a prospective control, read or produce an F0/F1 result, evaluate a
positive budget, run a semigroup, generate a trajectory, or run Monte Carlo.

## 2. P0 canonical-number alias repair

`strict_load_canonical_json` now supplies an explicit `parse_float` rejection
hook.  Every JSON floating-point token is rejected recursively with
`HOLD_CANONICAL_JSON`; this includes `2.0`, `2e0`, `1.0`, `0.0`, and `-0.0`
at any depth.  The existing canonical-byte round trip separately rejects the
integer spelling `-0`, while `+0` is invalid JSON.  Physical noninteger leaves
remain canonical rational or binary64 strings.

The selector core additionally requires `type(schema_version) is int` and
value 2.  The pinned state registry requires the exact integer 1.  Therefore
the old byte-distinct pairs 2 versus 2.0 and 1 versus 1.0 cannot both enter an
accepted semantic object.

The inverse tests cover top-level and nested float tokens, exponent notation,
both signed-zero alternatives, the selector envelope, and the state registry.

## 3. P1 repeated large-N memory repair

### 3.1 Root cause boundary

The pinned macOS gmpy2/MPFR runtime retains allocator pages after many
immutable MPFR operations.  The growth is not repaired by Python garbage
collection, `gmpy2.free_cache`, or by reusing one directed context.  Before
the repair, each direct N=8,000,000 Clopper--Pearson acceptance-set call added
roughly 100 MiB to the long-lived process, exactly reproducing Round 131.

Because in-place mutation is incompatible with the existing outward interval
DAG and the pinned runtime does not return the retained pages, the robust
resource boundary is process termination, one of the closures explicitly
allowed by Round 131.

### 3.2 Mandatory worker contract

Every distinct public `cp_acceptance_set` request now runs in a fresh
interpreter.  There is no in-process fallback.  The parent and worker exchange
only sorted, indented canonical JSON over stdin/stdout; no pickle is used.
The request binds

- the exact rational inputs and integer N;
- the SHA-256 of the loaded selector source;
- the SHA-256 of the resolved Python executable; and
- the frozen runtime-spec SHA-256.

The worker rehashes all three identities before evaluation and echoes them in
the response.  The parent verifies the request digest, exact response shape,
types, identities, result range, and a worker-reported peak-RSS value.  It
rehashes the identities again after worker exit, closing a source/runtime
time-of-check/time-of-use mutation.

The fixed fail-closed boundaries are

```text
timeout                         30 seconds
maximum canonical response     4096 bytes
maximum worker peak RSS         268435456 bytes
nonzero exit                    HOLD_SPECIAL_FUNCTION_DAG
any stderr                      HOLD_SPECIAL_FUNCTION_DAG
timeout or start failure        HOLD_SPECIAL_FUNCTION_DAG
source/runtime binding failure  HOLD_DEPENDENCY_HASH
```

A 128-entry LRU avoids rerunning identical deterministic requests.  Its key
contains every exact input and all three identities.  This cache is only an
optimization: the forced-cache-clear gate below proves that worker termination,
not cache reuse, closes the memory defect.

### 3.3 Resource measurements

The repaired threshold and independent neighbouring-tail oracle remain

```text
N                              8000000
strict CP acceptance set       (40646, 118891)
selector elapsed               0.910646 seconds
independent oracle elapsed     0.435169 seconds
```

One ordinary gate made 100 identical public calls and four distinct nearby-N
calls.  It measured parent RSS

```text
30224, 30272, 30384, 30384, 30384, 30384 KiB
```

and one child peak of 140869632 bytes.

A stronger manual gate cleared the cache before every call, so 100 identical
N=8,000,000 requests launched and terminated 100 real workers.  It completed
in 89.747957 seconds.  Parent RSS sampled after every ten calls was

```text
30272, 30448, 30464, 30464, 30464, 30480,
30496, 30496, 30496, 30496, 30496 KiB.
```

The total parent increase was 224 KiB rather than approximately 10 GiB.  The
100 child peaks lay in

```text
140902400 <= peak RSS <= 141967360 bytes,
```

well below the enforced 256 MiB cap.

The true 68-assertion candidate workload still depends on future accepted F1
planning inputs and was deliberately not fabricated or read in this repair.
It remains a pre-F1 execution gate.  The repaired CP primitive no longer has a
long-lived-process memory edge, but this report does not convert an absent F1
workload into a scientific or release PASS.

## 4. P1 test-key point-of-use binding

`load_test_keys`, which is called directly by `derive_pool_keys`, now first
hashes the bytes at `TEST_KEY_SET_PATH` and requires the frozen digest

```text
cb273018dbca49cf09399e1504ffe5282eec84513891e2ddc4e79d3995dc185d.
```

It then verifies the exact four-field shape, integer schema version, declared
encoding, purpose string, eight-entry count, lowercase 16-hex-digit grammar,
uniqueness, order, and the frozen eight integer identities.  Empty, reordered,
malformed-width, purpose-drifted, and collision-injected mutations return
`HOLD_TEST_KEY_SET` before they can alter pool collision semantics.

## 5. P1 total malformed-input HOLD algebra

The registry path now type-checks immutable bytes, externally supplied hashes,
the exact integer schema version, row configuration and hash leaves, interval
container shape, interval endpoint strings, reference records, and state-ball
bytes before regex, indexing, hashing, or decoding.

`derive_seed_basis` now requires every dependency to be an exact lowercase
64-hex-digit string before `bytes.fromhex`.  `derive_pool_keys` requires exactly
32 immutable bytes.  None, integers, bytes in a hash field, uppercase or short
hashes, bytearray/memoryview seed aliases, non-sequence intervals, and malformed
registry hashes now return declared `SelectorError` HOLD reasons rather than a
raw `TypeError`.

## 6. Numerical algorithm preservation

The Round-127 integer log-gamma boundary PMF, outward recurrence, monotone
geometric remainder, range decomposition, and precision ladder were not
changed.  All independent Round-131 exact/high-precision oracles remain live.
They still pass the 9240 exhaustive small-N ranges, 72 random medium-N cases,
precision nesting, skew-tail remainder bounds, N=8,000,000 strict neighbours,
and the exact acceptance set `(40646, 118891)`.

The pinned package bytes remain unchanged:

```text
schema
f631c72463f4f7d2e92d58b6b5cab7174de770a3c5a995a9d946bc359720f69c

runtime spec
3ddd0fda64a6cb739776b78056050089dfb20662735356189ac0237fe18ba86c

test-key set
cb273018dbca49cf09399e1504ffe5282eec84513891e2ddc4e79d3995dc185d
```

## 7. Verification record and repaired candidate hashes

```text
../../../.venv/bin/python -m pytest -q \
  code/test_f1_to_f2_common_observable_selector_v2.py \
  code/test_f1_to_f2_common_observable_selector_v2_round131_independent.py

84 passed; exit 0; wall 20.374915 seconds

../../../.venv/bin/ruff check \
  code/f1_to_f2_common_observable_selector_v2.py \
  code/test_f1_to_f2_common_observable_selector_v2.py \
  code/test_f1_to_f2_common_observable_selector_v2_round131_independent.py

All checks passed

../../../.venv/bin/ruff format --check [the same three files]

3 files already formatted

../../../.venv/bin/python -I \
  code/f1_to_f2_common_observable_selector_v2.py --self-check

status                         PASS_SCIENCE_FREE_SELF_CHECK
positive_budget_evaluated      false
f1_executed                    false
monte_carlo_executed           false
```

The repaired candidate hashes are

```text
code/f1_to_f2_common_observable_selector_v2.py
118d33446c986c1ca07c129886000a0812550a3976e0d7c7879b9f833fdda5b1

code/test_f1_to_f2_common_observable_selector_v2.py
abe863ee3ce745940f723da95705f26a62b675f7f7fb64548a83937d9eeda208

code/test_f1_to_f2_common_observable_selector_v2_round131_independent.py
a4a404dae43ad9900b207754e9f36e75cab516dcce3af340901c5439c6afcf95
```

## 8. Disposition

The four Round-131 findings have no open implementer-side P0 or P1 in these
candidate bytes.  This is not an independent acceptance, an authorization to
read prospective controls, an F1 PASS, or an authorization for positive B.
Freeze the three repaired hashes above and subject them to a fresh independent
canonical-byte, worker-protocol, memory, malformed-input, and numerical attack
before changing the selector or F1 HOLD state.
