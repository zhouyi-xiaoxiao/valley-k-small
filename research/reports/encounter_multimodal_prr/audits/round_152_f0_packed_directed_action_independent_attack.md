# Round 152: independent attack on the Round-150 packed directed action

Date: 2026-07-14

Decision: **REJECT ROUND 150 / HOLD F0 / NO F1**

This was a new, independent, read-only attack on the final Round-150 source
bytes.  I did not read or execute a selector, a prospective control, a positive
budget, an F1/F2/F3 row, or a physical/scientific output.  I did not allocate or
run the `7,165,305`-state target.  The only file written by this attack is this
audit record.

The centre-action arithmetic passed the independent exact attacks I could run:
signed `Q.T`, nonnegative `P.T`, heterogeneous directional coefficients,
reflecting and periodic boundaries, block crossings, and exact binary64
`Fraction` containment.  There is no P0 mathematical counterexample to the
one-multiply/one-add-then-`nextafter` argument on a correctly rounded gradual-
underflow binary64 runtime.

Round 150 nevertheless cannot be accepted.  Its action calls the hash-bound
stage-1 canonical interval validator before and after every action.  On the
exact bound runtime, that validator uses a NumPy `signbit` ufunc with a
stride-two Boolean `out` view that does not write correct results once the
block reaches the vectorized loop.  Valid positive-zero endpoints are then
reported as negative zero.  The same valid 24-state payload passes at block
sizes `1..15` and fails at every tested block size `16..99`; twenty fresh
processes failed twenty times.  This is a deterministic P1 availability and
production-applicability defect in the accepted byte set, even though it fails
closed rather than publishing a wrong enclosure.

The correct scope remains **implementation primitive only / F0 HOLD**.

## Frozen byte identities

| Object | SHA-256 |
| --- | --- |
| stage 1 `code/rate_defined_tensor_f0_packed.py` | `8f96bf30e9a4398fd98232bf846f81b4a4e18fe2469b6fd2203126697f3ce86b` |
| directed action `code/rate_defined_tensor_f0_packed_interval_action.py` | `a302d03c90ced1446cbc648b8af47d3f35f5afb536132a6c560a4646d4b51387` |
| directed tests `code/test_rate_defined_tensor_f0_packed_interval_action.py` | `c19dbb89848b8e93ae68cfa5c5ada115a44ce95688244c839af174a778b68b87` |
| Round-150 implementation record | `d2ed546096fb32270c8970c471be9351918aada9c90a33d91bca27b708b8a9ff` |

The diagnostic `(3,4,2)`, block-5 contract independently reproduced:

```text
operation_model_sha256        7a433c05a430784a25c35a83432f2b5eac77413c784f8f01aec461962441a52f
stage1_action_contract_sha256  2665ad011417bc0278a977345c5fb42edcdf15c79995ca900676ef79ff95e5f3
backend_binding_sha256         af1ea46d84094f9342ebc8e93e847d79d1aee46587bb952572fe416047513c0e
directed_action_contract_sha256 5b00c82948a32240211cb5f65688b028450df9b049d54e7ee885e1b3a06c55c0
```

The attacked runtime was `python-3.12.13|numpy-2.5.1|arm64`.

## Findings

### P0

None found within the explicitly bounded centre-matrix arithmetic object.

### P1 — the bound stage-1 endpoint validator rejects valid large-block input

The stage-1 validator allocates a `(B,2)` Boolean scratch array and calls

```python
np.signbit(block[:, endpoint], out=scratch[:, 1])
```

at `code/rate_defined_tensor_f0_packed.py:352-356`.  `scratch[:,1]` has byte
stride two.  On the runtime recorded in the Round-150 contract, the vectorized
`signbit` loop leaves incorrect true entries for ordinary `+0.0` inputs.  This
is not speculation about a future platform: it occurs on the exact runtime to
which the action contract binds itself.

Round 150 depends on this validator at
`code/rate_defined_tensor_f0_packed_interval_action.py:594-596`, again at
`841-843`, and through result validation at `880-882`.  Consequently a valid
canonical source can be rejected before the directed arithmetic is entered.
Reflecting rate arrays and interval propagation naturally contain exact zero
endpoints, so excluding zero is not an admissible production precondition.

Minimal ufunc reproducer:

```bash
../../../.venv/bin/python - <<'PY'
import numpy as np
x = np.zeros(24, dtype=np.float64)
s = np.empty((24, 2), dtype=np.bool_)
np.signbit(x, out=s[:, 1])
print(np.flatnonzero(s[:, 1]).tolist())
assert not np.any(s[:, 1])
PY
```

The assertion fails.  One recorded run returned false-positive true entries
`[2,3,4,5,6,7,8,9,10,11,12,13,14,15]`; the exact stale positions need not be
stable because the omitted writes expose prior `empty` bytes.

Canonical-boundary reproducer (run from the report directory):

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=code ../../../.venv/bin/python - <<'PY'
import math
import rate_defined_tensor_f0_packed as p

shape = (2, 3, 4)
rows = []
for i in range(math.prod(shape)):
    lo = ((i * 11) % 19 - 9) / 128
    hi = lo + ((i % 5) + 1) / 256
    rows.append((float(lo), float(hi)))

for block in (1, 15, 16, 99):
    payload = p.create_packed_interval_payload(
        tuple(rows),
        role="science_free_reproducer",
        logical_shape=shape,
        nonnegative=False,
        block_size=block,
        maximum_working_bytes=2_000_000,
    )
    try:
        p.load_canonical_packed_intervals(payload)
        status = "PASS"
    except p.PackedF0Failure as exc:
        status = exc.code
    print(block, payload.manifest.raw_sha256, status)
PY
```

Observed, with identical raw bytes in every row:

```text
1  df9df2b6fffa7ddafec9f82d56ef01b786b67be6e618e7fa612870a0abb24c5d  PASS
15 df9df2b6fffa7ddafec9f82d56ef01b786b67be6e618e7fa612870a0abb24c5d  PASS
16 df9df2b6fffa7ddafec9f82d56ef01b786b67be6e618e7fa612870a0abb24c5d  HOLD_F0_PACKED_ENDPOINT_INVALID
99 df9df2b6fffa7ddafec9f82d56ef01b786b67be6e618e7fa612870a0abb24c5d  HOLD_F0_PACKED_ENDPOINT_INVALID
```

Exhaustive threshold replay gave `PASS` for block sizes `1..15` and the same
hold for every block size `16..99`.  Repeating the block-99 load in twenty
fresh Python processes produced `20/20` failures.

Required repair: remove stride-two Boolean ufunc outputs from every canonical
validator used by the action (for example, use a `(2,B)` layout with contiguous
rows), preserve the exact payload ledger, add a vectorized-runtime probe at an
action-relevant block length, and rerun both the stage-1 and directed-action
attacks on the new hashes.

### P2 — the saved oracle suite masks coefficient-index bugs

Every saved axis constructed by `_axis_payload` in the Round-150 test file uses
one constant rate for all positions of that axis.  The killing field is also
constant.  The input vector varies, so those tests detect source-index errors,
but a wrong `rate_index`, swapped heterogeneous coefficient, or wrong
state-dependent self coefficient can survive the saved exact oracle.

I ran a separate exact oracle with direction-asymmetric, position-dependent
dyadic forward/backward rates and state-dependent killing.  It did not call the
directed rounding helpers and computed row-major strides locally.  Across
`(4,)`, `(3,4)`, and `(2,3,4)`, mixed reflecting/periodic axes, both `P.T` and
signed `Q.T`, and block sizes `1,3,7,99`, it checked `320` exact rational output
rows in `24` actions.  All rows were enclosed and all six shape/operator groups
were byte-identical across block sizes.  Thus this is a regression-coverage
gap, not a counterexample to the current arithmetic bytes.  The heterogeneous
oracle must become a saved test in the repair round.

### P2 — result hashes are consistency metadata, not provenance

`validate_directed_action_result` checks that the output's self-declared raw
hash matches its bytes, but it neither recomputes the action nor authenticates
an output digest containing operator, kernel, input, contract, and enclosure.
An arbitrary finite ordered array with a freshly computed `raw_sha256` passes;
a `P` result can also be relabelled as `Q` by changing `operator` and
`exact_action_nonnegative` together.

Reproducer:

```python
from dataclasses import replace
import hashlib
import numpy as np

a = np.zeros_like(result.enclosure.intervals)
a[:, 0], a[:, 1] = -123.0, 456.0
a.setflags(write=False)
enclosure = replace(
    result.enclosure,
    intervals=a,
    raw_sha256=hashlib.sha256(memoryview(a).cast("B")).hexdigest(),
)
validate_directed_action_result(
    replace(result, enclosure=enclosure),
    kernel=kernel,
    vector=vector,
    contract=contract,
)  # accepted

validate_directed_action_result(
    replace(
        result,
        operator="Q",
        enclosure=replace(result.enclosure, exact_action_nonnegative=False),
    ),
    kernel=kernel,
    vector=vector,
    contract=contract,
)  # accepted
```

Round 150 already leaves a separate fresh-process verifier open, so this is P2
at the present implementation-primitive boundary rather than an additional P1.
No downstream stage may treat this validator as a producer-independent receipt.

### P2 — the rounding-environment probe is scalar-only

`_validate_binary64_rounding_environment` probes scalar `np.float64` calls,
whereas the action uses length-`B` array ufunc loops.  The P1 above demonstrates
on this exact NumPy runtime that scalar and vectorized ufunc paths cannot be
assumed equivalent merely from a version string.  The repair should probe
contiguous vectorized multiply, add, and `nextafter`, including positive and
negative subnormal products, at and above the dispatch threshold.  Independent
Fraction attacks found no current multiply/add enclosure failure, so this is a
missing runtime gate rather than a demonstrated arithmetic counterexample.

## Attacks that passed

- The stored source hashes and all diagnostic contract digests reproduced.
- `P.T` uses the correct lower/upper roles for nonnegative coefficients.
- Signed `Q.T` reverses endpoints only for the nonpositive diagonal and uses
  ordinary endpoint order for nonnegative off-diagonal coefficients.
- The frozen order is `self`, then forward/backward incoming terms per axis.
- Periodic wraps, reflecting omitted terms, and block-boundary sources matched
  an independent exact heterogeneous oracle.
- One outward `nextafter` after each finite RN product and addition gives the
  stated exact-real enclosure under the declared binary64 assumptions.
- The explicit owned arrays sum to `16 N + 81 B`; the later endpoint scratch is
  `2 B` and is allocated after the named action workspace is deleted.  This is
  an exact visible NumPy payload identity, not an RSS or allocator bound.
- Stage-1 source, directed source, operation-model, action-contract, and kernel
  replay metadata are rechecked against current bytes.  They do not solve the
  independent-verifier boundary noted above.

## Reproduced project commands

Run from `research/reports/encounter_multimodal_prr`:

```bash
../../../.venv/bin/python -m py_compile \
  code/rate_defined_tensor_f0_packed_interval_action.py \
  code/test_rate_defined_tensor_f0_packed_interval_action.py

../../../.venv/bin/ruff check \
  code/rate_defined_tensor_f0_packed_interval_action.py \
  code/test_rate_defined_tensor_f0_packed_interval_action.py

PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=code \
  ../../../.venv/bin/python -m pytest -q -p no:cacheprovider \
  code/test_rate_defined_tensor_f0_packed_interval_action.py

PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=code \
  ../../../.venv/bin/python -m pytest -q -p no:cacheprovider \
  code/test_rate_defined_tensor_f0_packed.py \
  code/test_rate_defined_tensor_f0_packed_interval_action.py
```

Observed:

```text
py_compile                         PASS
ruff                               PASS
directed-action focused tests      33 passed
stage1 packed + directed action    56 passed
independent heterogeneous oracle   320 exact rows passed
valid zero-endpoint threshold      blocks 1..15 PASS; 16..99 FAIL
fresh-process block-99 replay      20/20 FAIL
largest state count exercised      24
```

The green saved suite is therefore insufficient for Round-150 acceptance.  The
action remains an unauthorised implementation primitive, `F0` remains `HOLD`,
and no F1 or positive-budget work is authorised by these bytes.
