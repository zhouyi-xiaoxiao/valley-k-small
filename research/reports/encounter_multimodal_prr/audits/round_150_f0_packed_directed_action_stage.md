# Round 150: packed F0 directed interval-action stage

Date: 2026-07-14

Decision: **ACCEPT BOUNDED DIRECTED-ACTION IMPLEMENTATION / HOLD F0 / NO F1**

This round adds a separate, science-free interval-action module on top of the
packed stage-1 centre kernel.  It does not edit the frozen stage-1 module.  It
does not read or execute a selector, a prospective control, a positive budget,
an F1/F2/F3 row, or any physical/scientific output.  The largest exercised grid
was the synthetic `(2,3,4) = 24`-state oracle case.  The `7,165,305`-state
production target was not allocated or run.

This is an implementation-stage acceptance with exact small-grid oracles.  It
is not the still-required separate-implementation verifier and does not promote
F0.

## Byte identities

| Object | SHA-256 |
| --- | --- |
| frozen stage 1 `code/rate_defined_tensor_f0_packed.py` | `8f96bf30e9a4398fd98232bf846f81b4a4e18fe2469b6fd2203126697f3ce86b` |
| new `code/rate_defined_tensor_f0_packed_interval_action.py` | `a302d03c90ced1446cbc648b8af47d3f35f5afb536132a6c560a4646d4b51387` |
| new `code/test_rate_defined_tensor_f0_packed_interval_action.py` | `c19dbb89848b8e93ae68cfa5c5ada115a44ce95688244c839af174a778b68b87` |

The stage-1 file above was inspected and hash-bound but not modified in this
round.  Every directed-action contract records and rechecks both source hashes,
the stage-1 construction/backend strings, the stage-1 nominal action backend,
the stage-1 action-contract digest, the directed operation-model digest, the
runtime, the tensor shape, the block size, the scratch cap, and the frozen
summation order.

For the diagnostic contract `(shape=(3,4,2), block_size=5,
maximum_scratch_bytes=2,000,000)` under
`python-3.12|numpy-2.5.1`, the bindings were:

```text
operation_model_sha256       7a433c05a430784a25c35a83432f2b5eac77413c784f8f01aec461962441a52f
stage1_action_contract       2665ad011417bc0278a977345c5fb42edcdf15c79995ca900676ef79ff95e5f3
backend_binding              af1ea46d84094f9342ebc8e93e847d79d1aee46587bb952572fe416047513c0e
summation_order              self,
                             axis_0_forward_incoming,
                             axis_0_backward_incoming,
                             axis_1_forward_incoming,
                             axis_1_backward_incoming,
                             axis_2_forward_incoming,
                             axis_2_backward_incoming
```

Those last two digests are deliberately contract-specific, not universal
release identifiers.

## Enclosed mathematical object

The new stage encloses the action of the saved **centre** matrix coefficients,
each treated as the exact real value of its stored binary64 bit pattern, on an
input interval vector whose endpoints are likewise exact stored binary64
values.  It supports:

- `P.T` on a canonical nonnegative input interval vector; and
- signed `Q.T` on an arbitrary canonical interval vector, including intervals
  that cross zero.

The output is one exact-type NumPy `(N,2)` native-binary64 array with
`C_CONTIGUOUS`, `ALIGNED`, `OWNDATA=True`, `base is None`, and
`WRITEABLE=False`.  Its raw bytes, input raw hash, actual kernel replay hash,
action-contract hash, backend-binding hash, block count, operation counts, and
memory ledger are revalidated after the action.  Writable arrays, views,
ndarray subclasses, nonnative-endian arrays, post-hash mutation, falsified
input/kernel hashes, kernel mutation, and ledger mutation all fail closed.

This stage does **not** claim that a centre action alone encloses the original
rate intervals.  The stage-1 `delta_Q`/`delta_P` witnesses remain separate from
this arithmetic enclosure and must be composed explicitly by a later
uniformization proof.

## Directed-roundoff argument

Before and after an action, the contract validator probes that the live runtime
has 8-byte IEEE-like binary64, 52 stored fraction bits, round-to-nearest with
ties to even, and gradual subnormal underflow.  It binds the exact Python/NumPy
runtime and source bytes.  The accepted action then uses the following frozen
rules.

1. For a nonnegative coefficient, the input lower endpoint supplies the lower
   product and the input upper endpoint supplies the upper product.  For the
   nonpositive `Q` diagonal, those endpoint roles are reversed.  Coefficient
   signs are checked in the already-declared block workspace.
2. Every lower product is one binary64 multiply followed immediately by
   `nextafter(-infinity)`; every upper product is followed by
   `nextafter(+infinity)`.
3. Missing reflecting-halo contributions are reset to exact zero.  They still
   occupy their frozen place in the addition sequence.
4. Every lower addition is one binary64 add followed immediately by
   `nextafter(-infinity)`; every upper addition is followed by
   `nextafter(+infinity)`.
5. The sequence is exactly `self`, then forward incoming and backward incoming
   for each dimension in increasing order.  It is identical to the stage-1
   nominal action contract.
6. Any nonfinite or reversed final interval fails closed.  Thus a finite
   accepted interval never silently relies on an overflowed intermediate.

For a finite exact real operation `z`, one adjacent representable value below
the round-to-nearest result is no greater than `z`, and one adjacent value above
is no less than `z`.  Induction over the frozen additions therefore encloses the
exact centre-matrix interval action.  The subnormal tests exercise cases where
the ordinary binary64 product is zero although the exact `Fraction` product is
strictly nonzero; the outward endpoints still contain it.

## Fixed NumPy payload ledger

For `N` states and `B = min(N, block_size)`, the action owns:

| payload | exact bytes |
| --- | ---: |
| output interval array | `16 N` |
| five `int64` index/coordinate arrays | `40 B` |
| one Boolean halo/sign mask | `1 B` |
| two accumulator, two term, and one coefficient `float64` arrays | `40 B` |
| total simultaneous action workspace | `81 B` |
| endpoint-validation scratch after action workspace release | `2 B` |
| maximum new numeric payload | `16 N + max(81 B, 2 B) = 16 N + 81 B` |

The implementation sums the actual `.nbytes` of every workspace allocation and
checks the output `.nbytes` before acting; any drift from the contract fails
closed.  The ledger deliberately excludes the already-owned kernel and input
buffers and does not claim an RSS value or allocator-overhead bound.  Therefore
it is an exact NumPy payload identity, not a largest-shape resource acceptance.

## Oracle and adversarial coverage

The 33 focused tests cover:

- exact `Fraction` containment of both `P.T` and `Q.T` on synthetic 1D, 2D,
  and 3D grids;
- reflecting and periodic axes, including a periodic wrap and a reflecting
  no-wrap impulse across a block boundary;
- signed `Q.T` inputs whose intervals cross zero;
- gradual-underflow and subnormal products for which the ordinary binary64
  product is zero but the exact rational product is nonzero;
- byte-identical outputs for block sizes `1`, `5`, and larger than the small
  state count;
- native/owned/read-only output structure and fixed memory-ledger arithmetic;
- writable, alias/view, ndarray-subclass, nonnative-endian, post-hash mutation,
  falsified binding, backend/order/block, kernel, and ledger attacks; and
- fail-closed signed-input misuse for `P.T` and nonfinite overflow for `Q.T`.

The oracle reconstructs every incoming edge and coefficient from the privately
owned centre kernel, converts every stored endpoint and coefficient with
`Fraction.from_float`, forms exact rational interval products and sums, and
checks inclusion state by state.  It does not use the implementation's
rounding helpers.

## Commands and observed results

Run from `research/reports/encounter_multimodal_prr`:

```text
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
largest state count exercised      24
```

## Remaining boundary

```text
centre P.T/Q.T directed arithmetic enclosure       IMPLEMENTED / SMALL EXACT ORACLES
frozen order and block/backend/source binding       IMPLEMENTED / TESTED
owned native readonly interval output               IMPLEMENTED / TESTED
fixed NumPy payload ledger                          IMPLEMENTED / TESTED
centre-to-rate-interval error composition           OPEN
production uniformization and Poisson enclosure     OPEN
verifier-owned propagation and time jets            OPEN
batched scalar topology and unique-time cache       OPEN
separate implementation / fresh-process verifier    OPEN
7,165,305-state RSS, swap, and timing gate          NOT RUN
F0                                                  HOLD
F1 or positive-budget science                       NOT AUTHORIZED / NOT RUN
```

The field `directed_roundoff_stage_complete=true` belongs only to this bounded
centre-action contract.  The stage-1 kernel's full-F0
`action_roundoff_proof_complete` remains false, and no release gate is changed.
