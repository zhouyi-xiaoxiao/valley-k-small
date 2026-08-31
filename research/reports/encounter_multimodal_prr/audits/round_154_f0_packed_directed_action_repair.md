# Round 154: packed directed-action repair after independent rejection

Date: 2026-07-14

Decision: **ACCEPT ROUND-152 REPAIR STAGE / HOLD F0 / NO F1**

Round 152 (`aa3180306aef40cc6ecb04a32e7d29c88aacc5c9168fc8b6d98521756c130410`)
correctly rejected the Round-150 bytes.  This round repairs its demonstrated P1
contiguous-output defect and closes the three saved-coverage gaps it identified.
It is still an implementation-stage record, not an independent acceptance
audit; Round 155 must attack these new hashes.

All work was science-free.  No selector, prospective control, positive budget,
F1/F2/F3 row, physical result, or scientific output was read or executed.  The
largest exercised shape was `(2,3,4) = 24` states.  The `7,165,305`-state target
was not allocated or run.

## Repaired byte set

| Object | SHA-256 |
| --- | --- |
| `code/rate_defined_tensor_f0_packed.py` | `447aa3bc224685ea1cc556d9d322dafba05ef148945d4ae41291f83e29f3deb4` |
| `code/test_rate_defined_tensor_f0_packed.py` | `adf4e7dd316a623ff2248d8876592bd6799045976369211f1f0da1ecd6b80458` |
| `code/rate_defined_tensor_f0_packed_interval_action.py` | `2f3201a9eb1b6fbe577b43c3b046ad5f7f369816a7d4a32f4381506e63494f2a` |
| `code/test_rate_defined_tensor_f0_packed_interval_action.py` | `8ec937f23579d3560cda7a505a7960b14cf297cfa9f7f8b4604eed121e40362d` |

The directed contract/result/memory schemas and backend were bumped to `v2`.
For the diagnostic `(shape=(3,4,2), block_size=5,
maximum_scratch_bytes=2,000,000)` contract:

```text
runtime                         python-3.12.13|numpy-2.5.1|machine-arm64
operation_model_sha256          ae5b6218f8033bbcbb3df8b5d66797e4f85597f8bec13273984e56dfabff27b2
stage1_action_contract_sha256   2665ad011417bc0278a977345c5fb42edcdf15c79995ca900676ef79ff95e5f3
backend_binding_sha256          57cdb366e2b6f2421c900fea37e5ae8b5d918d4004877b1b58c701d56f37f58a
directed_contract_sha256        ef801b83d95567be329a1edce160a9c5604b2accd31c5a6853738d67d8fe7c64
vectorized_probe_lengths        16, 24, 64
```

The stage-1 action-contract digest is unchanged because the nominal action
contract did not change.  The directed backend binding includes the new stage-1
source hash, directed source hash, exact runtime/architecture, vector probe,
operation model, shape, block size, backends, and frozen summation order.

## P1 repair: contiguous canonical Boolean scratch

The stage-1 canonical interval validator now allocates Boolean scratch as
`(2,B)`, where each row is contiguous.  Every endpoint operation writes to
`scratch[0,:count]` or `scratch[1,:count]`; there is no unary/binary ufunc
output with byte stride two.  The directed enclosure validator uses the same
layout.  This preserves the exact canonical validation payload:

```text
two contiguous Boolean rows = 2 B bytes = 2 bytes/state-in-block
```

A static search finds no remaining `out=scratch[:,k]`-style ufunc target in the
stage-1 or directed modules.  Saved tests monitor the actual allocation shape,
strides, and `C_CONTIGUOUS` flag.

The exact 24-endpoint zero sequence now has the following result for every
block size in `1..15, 16, 24, 99`:

```text
ordinary +0.0 in lower and upper positions       PASS
-0.0 in lower/upper positions 0,3,15,16,23       HOLD_F0_PACKED_ENDPOINT_INVALID
```

Four saved `spawn`-process repetitions reproduced the complete matrix.  A
separate 20-process block-99 replay gave `20/20` correct positive-zero accepts
and `20/20` correct negative-zero holds.  This directly reverses the Round-152
`20/20` false rejection of valid block-99 inputs.

## Vectorized rounding-environment gate

The former scalar-only gate is retained and supplemented by contiguous owned
array probes of lengths `16`, `24`, and `64`, covering the observed dispatch
threshold and larger vector loops.  At each length the gate executes real
`out=` calls for:

- positive and negative normal multiplication;
- positive and negative subnormal multiplication, including half-minimum-
  subnormal underflow to signed zero;
- tie-to-even and above-half-ulp additions;
- preservation of positive and negative minimum subnormals; and
- lower/upper `nextafter` after every vector multiply and add.

Every vector result is checked against exact `Fraction.from_float` arithmetic.
The runtime identity now binds Python micro version, NumPy version, and machine
architecture.  The probe owns four `float64[64]` arrays at peak, exactly `2048`
NumPy payload bytes.

The fixed directed payload ledger is therefore now:

```text
output                         16 N bytes
action workspace               81 B bytes
canonical endpoint scratch      2 B bytes
vector runtime probe          2048 bytes
maximum simultaneous new NumPy payload
             = 16 N + max(81 B, 2 B, 2048)
```

Here `B=min(N,block_size)`.  The action workspace is released before the
post-action contract/runtime gate.  Python-object and allocator/RSS overhead
remain excluded, as before.  This is not a largest-shape memory acceptance.

## Saved heterogeneous exact oracle

The Round-150 test suite now saves the formerly independent heterogeneous
attack instead of using only constant axis rates and killing.  It uses:

- direction-asymmetric, position-dependent dyadic forward/backward rates;
- state-dependent dyadic killing;
- `(4,)`, `(3,4)`, and `(2,3,4)` shapes;
- reflecting, periodic, and mixed boundary combinations;
- nonnegative `P.T` and signed `Q.T` inputs; and
- block sizes `1`, `3`, `7`, and `99`.

The oracle computes row-major strides locally, reconstructs every source index
and rate index, forms exact binary64 rational products/sums with `Fraction`, and
checks both saved endpoints.  It covers `320` exact output rows in `24` actions.
All six shape/operator groups are byte-identical across the four block sizes.
The heterogeneous killing makes a wrong state-dependent self mapping visible;
the directional/positional rate variation makes a wrong `rate_index` visible.

## Result consistency digest

`DirectedActionResult` now stores a canonical SHA-256 consistency digest over:

- operator and result schema;
- actual kernel replay hash and input raw hash;
- action-contract and backend-binding hashes;
- enclosure shape, raw hash, input binding, and nonnegative-action flag;
- block and operation counts;
- every memory-ledger field; and
- the explicit `science_executed=false` and `f0_pass=false` flags.

Validation first binds the enclosure bytes, kernel, input, contract, and ledger,
then recomputes this digest.  The exact Round-152 arbitrary-array replacement
with a freshly recomputed enclosure raw hash now fails, as does a simple
`P`-to-`Q` relabel with the matching flag changed.

This digest is **not authentication, provenance, a fresh-process receipt, or an
independent recomputation**.  It has no secret or external authority; an actor
who deliberately rewrites every field can recompute it.  Its bounded purpose is
to prevent accidental/simple partial relabelling and replacement.  The separate
implementation/fresh verifier remains open.

## Commands and outcomes

Run from `research/reports/encounter_multimodal_prr`:

```text
../../../.venv/bin/python -m py_compile \
  code/rate_defined_tensor_f0_packed.py \
  code/rate_defined_tensor_f0_packed_interval_action.py \
  code/test_rate_defined_tensor_f0_packed.py \
  code/test_rate_defined_tensor_f0_packed_interval_action.py

../../../.venv/bin/ruff check \
  code/rate_defined_tensor_f0_packed.py \
  code/rate_defined_tensor_f0_packed_interval_action.py \
  code/test_rate_defined_tensor_f0_packed.py \
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
py_compile                                      PASS
ruff                                            PASS
directed focused                               39 passed
stage1 packed + directed                       64 passed
saved heterogeneous exact oracle               320 rows / 24 actions PASS
saved fresh zero-sequence repeats               4/4 PASS
standalone fresh block-99 repeats              20/20 PASS
largest state count exercised                  24
```

## Remaining gate boundary

```text
Round-152 contiguous-output P1                  REPAIRED / SAVED REGRESSION
vectorized binary64 runtime gate                IMPLEMENTED / TESTED SMALL
heterogeneous rate-index/self oracle            IMPLEMENTED / 320 ROWS
result relationship consistency                 IMPLEMENTED / NOT AUTHENTICATION
centre-to-rate-interval error composition       OPEN
production uniformization, Poisson, and jets    OPEN
batched scalar topology                         OPEN
separate implementation / fresh verifier        OPEN
7,165,305-state RSS, swap, and timing gate      NOT RUN
F0                                               HOLD
F1 / positive-budget science                     NOT AUTHORIZED / NOT RUN
```

No release decision changes in this round.  Round 155 must independently attack
the new source hashes before even this bounded implementation primitive is
accepted.
