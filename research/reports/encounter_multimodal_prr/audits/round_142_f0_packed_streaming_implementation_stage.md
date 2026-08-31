# Round 142: F0 packed/streaming implementation stage

Date: 2026-07-14

Decision: **ACCEPT FIRST IMPLEMENTATION STAGE ONLY / HOLD F0 / NO F1**

This is an implementation record, not an independent acceptance audit.  It
addresses a bounded first stage of the combined Round-136 exact-type repair and
Round-138 resource redesign.  It does not release F0, a selector, an
attestation, F1, or any positive-budget computation.

## Science boundary

The implementation and tests are science-free.  They use only synthetic
neutral rate axes, a synthetic exact killing interval, synthetic point-mass or
uniform initial intervals, and old small-grid method oracles.  No prospective
control, selector result, F1/F2/F3 result, positive installed budget, physical
semigroup row, or topology result was read or evaluated.  The largest exercised
new shape was `(17,18,19) = 5,814` states.  The `7,165,305`-state target was not
allocated.

## New implementation objects

| Object | SHA-256 |
| --- | --- |
| `code/rate_defined_tensor_f0_packed.py` | `b787029d93d9b9f14651816af92a2ab3332811b7d613385e2a833298c5ba122f` |
| `code/test_rate_defined_tensor_f0_packed.py` | `030ff2f81ed91200323ec528c7398d5134baef14dd2e6ea77a88befa55518b16` |

The frozen `rate_defined_tensor_f0.py` and its frozen tests were not edited.

## Implemented stage

### 1. Canonical packed interval bytes

- External manifests bind the exact science-free role, logical shape,
  `(N,2)` interval-array shape, state count, raw byte length, raw SHA-256,
  endpoint order, nonnegativity flag, block size, and working-byte cap.
- The loader accepts exact built-in `bytes`, verifies length/hash before NumPy,
  copies once into a plain native `float64` array, and requires C-contiguous,
  aligned, `OWNDATA=True`, `base is None`, and `WRITEABLE=False`.
- Endpoint validation is blocked and rejects nonfinite values, reversed bounds,
  negative lower endpoints when required, and signed zero.
- Validation uses no `isinstance`, `np.asarray`, `np.array_equal`, or other
  equality-dispatch boundary.  Exact dataclass/built-in types are required at
  every accepted nested record.

### 2. Streaming exact ledger

- Kernel construction uses two canonical passes per authority: exact
  exit/centre-exit reduction and rate selection, then array fill plus immediate
  exact ledger reduction.
- No per-state `Fraction` list or tuple is retained.  The saved exact state is a
  fixed set of 11 global witnesses plus one exact rate, independent of `N`.
- The ledger records exact values and lowest-index witnesses, canonical block
  coverage, per-block source/derived raw digests, backend, pass count, block
  size, and working-byte cap.
- Small-grid exact values match the old implementation for the rate,
  `delta_Q`, both `delta_P` branches, selected `delta_P`, coefficient rounding,
  `Qhat` absolute row norm, killing uncertainty, and all saved centre arrays.

The current reducer uses scalar Python `Fraction` objects as ephemeral row
scratch.  This closes the retained-object memory defect but is not yet a target-
shape timing acceptance.  A pinned GMP/Rust/C reducer remains a possible later
optimization if target timing requires it.

### 3. Fixed-payload block/halo action

- `P.T` and `Q.T` allocate one full output and a fixed numeric workspace of
  `65 * min(block_size,N)` bytes: five `int64` index buffers, three `float64`
  buffers, and one Boolean mask.
- Incoming periodic and reflecting faces are gathered explicitly in a frozen
  self/forward/backward order.  The implementation never uses `np.roll` and
  never retains full-state directional term arrays.
- Small 1D/2D/3D boundary impulses and deterministic random states agree with
  the old explicit CSR oracle to the test tolerance.  Output bytes are
  identical for block sizes `1`, `7`, and greater than the full small state
  count.

The `65 B/state-in-block` number is a NumPy payload accounting identity, not a
measured RSS peak.  NumPy allocator overhead and the new sequential summation
roundoff proof remain open.

### 4. Producer versus verifier ownership

- The producer returns no ndarray.  Its method artifact contains immutable
  canonical raw action bytes, byte length/hash, kernel/source/contract hashes,
  exact ledger hash, resource fields, and producer PID.
- Same-PID verification fails closed.
- The test verifier starts through Python's `spawn` context, reconstructs all
  arrays from immutable source bytes, performs one verifier-owned build/action,
  checks every digest/ledger field, and compares the saved raw output bytes in
  bounded blocks without NumPy equality dispatch.
- The verifier returns only a metadata receipt.  It never returns its private
  numerical array, and the receipt states
  `PASS_METHOD_REPLAY_ONLY_NOT_F0`, `producer_arrays_accepted=false`,
  `science_executed=false`, and `f0_pass=false`.

This is a producer/verifier authority boundary using the same implementation
module.  It is not the still-required separate-implementation replay or a fresh
black-box acceptance audit.

## Tests and checks

The new focused module has 20 deterministic tests covering:

- exact manifest/bytes/shape/length/hash binding;
- ndarray subtype/equality/ufunc/function dispatch attacks with zero dispatch;
- writable, view/base alias, Fortran, nonnative-endian, nested-subclass, signed-
  zero, nonfinite, role-swap, and post-validation mutation attacks;
- exact legacy-ledger agreement, block-size invariance, lowest-index ties, and
  fixed retained-Fraction count at 60 versus 5,814 states;
- fixed-payload `P.T`/`Q.T`, reflecting/periodic halo impulses, `np.roll`
  prohibition, deterministic block-size bytes, and kernel/action mutations;
- same-PID rejection, spawn-process reconstruction, raw-byte replay, artifact
  mutation, source-byte mutation, and explicit non-promotion flags.

Commands run from the repository root:

```text
.venv/bin/ruff format research/reports/encounter_multimodal_prr/code/rate_defined_tensor_f0_packed.py research/reports/encounter_multimodal_prr/code/test_rate_defined_tensor_f0_packed.py
.venv/bin/ruff check research/reports/encounter_multimodal_prr/code/rate_defined_tensor_f0_packed.py research/reports/encounter_multimodal_prr/code/test_rate_defined_tensor_f0_packed.py
.venv/bin/python -m pytest -q research/reports/encounter_multimodal_prr/code/test_rate_defined_tensor_f0_packed.py
.venv/bin/python -m pytest -q research/reports/encounter_multimodal_prr/code/test_rate_defined_tensor_f0.py research/reports/encounter_multimodal_prr/code/test_rate_defined_tensor_f0_round125_adversarial.py research/reports/encounter_multimodal_prr/code/test_rate_defined_tensor_f0_packed.py
python3 scripts/reportctl.py validate-science-rules
```

Observed outcomes:

```text
Ruff                                        PASS
new packed tests                            20 passed
old core + Round-125 adversarial + packed   52 passed
scientific guardrail wiring                 PASS
```

## Round-136/138 closure boundary

| Finding | This stage | Still required |
| --- | --- | --- |
| Round-136 subtype/equality dispatch | Closed for the new canonical byte loader and verifier-owned action path by exact types, ownership, hashes, and mutation tests | Fresh frozen-hash black-box audit of the complete replacement path |
| Round-136 alias/TOCTOU | New authoritative path owns arrays privately, checks hashes before/after public inspection actions, rejects aliases/writeability, and returns no verifier array | Complete propagation/jets must remain in the same private verifier process; no public caller-constructible verified state |
| Round-138 retained per-state exact objects | Closed at the saved representation level; retained exact witness count is fixed | Target-shape CPU/RSS measurement and possible compiled exact reducer |
| Round-138 ten-array action | Replaced in this stage by one output plus bounded block workspace | Directed roundoff/underflow proof, allocator/RSS measurement, independent replay hash |
| Round-138 three recurrence passes | Not implemented in this stage | One producer propagation plus one verifier propagation, with jets consuming verifier-owned state immediately |
| Round-138 per-time topology cost | Not implemented in this stage | Batched direct scalar uniformization, MPFR Poisson enclosure, derivative bounds through order four, and unique-time private verifier cache |
| Largest-shape resource gate | Not run | Safe preflight, twofold headroom, neutral target build/action/absolute-time samples, complete schedule, RSS/swap/time evidence |

## Final boundary

```text
canonical packed source                         IMPLEMENTED / TESTED SMALL-MEDIUM
strict nested types and dispatch rejection      IMPLEMENTED / TESTED
streaming exact ledger without O(N) Fractions   IMPLEMENTED / TESTED SMALL-MEDIUM
fixed-payload block/halo P.T and Q.T             IMPLEMENTED / TESTED SMALL
spawned verifier-owned raw-byte replay           IMPLEMENTED / TESTED METHOD-ONLY
new directed action-roundoff proof               OPEN
production uniformization and verifier jets      OPEN
batched scalar topology                          OPEN
separate implementation replay                   OPEN
7,165,305-state resource acceptance              NOT RUN
F0                                               HOLD
F1 or positive-budget science                    NOT AUTHORIZED / NOT RUN
```
