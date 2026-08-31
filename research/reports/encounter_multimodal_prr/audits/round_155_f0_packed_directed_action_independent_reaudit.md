# Round 155: independent re-audit of the repaired packed directed action

Date: 2026-07-14

Decision: **ACCEPT ROUND-154 REPAIR AS A BOUNDED IMPLEMENTATION PRIMITIVE / HOLD F0 / NO F1**

This was an independent, read-only attack on the frozen Round-154 stage-1 and
directed-action bytes.  I did not read or execute a selector, prospective
control, positive budget, F1/F2/F3 row, or physical/scientific output.  I did
not allocate or run the `7,165,305`-state target.  The largest object exercised
had `24` states.  The only file written by this re-audit is this audit record.

The Round-152 P1 is closed on the repaired hashes.  Ninety-nine separate Python
processes exercised the real canonical validator at every block size `1..99`:
the same valid `+0.0` endpoint bytes were accepted in every process, while the
same payload with selected endpoints changed to `-0.0` failed closed in every
process with `HOLD_F0_PACKED_ENDPOINT_INVALID`.  Thus both sides of the former
dispatch boundary, blocks `1..15` and `16..99`, now behave correctly.

An independently constructed heterogeneous `Fraction` oracle also passed all
`320` exact rows in `24` actions: `P.T` and signed `Q.T`, one through three
dimensions, reflecting/periodic/mixed boundaries, direction- and
position-dependent rates, state-dependent killing, and blocks `1,3,7,99`.
Every one of the six shape/operator groups was byte-identical across block
sizes.  No P0 or P1 was found in the bounded centre-action primitive.

This decision does **not** accept F0.  It does not establish a largest-shape RSS
or timing gate, centre-to-rate-interval composition, production
uniformization/Poisson/jets, batched scalar topology, or an independently
implemented fresh verifier.

## Frozen byte identities

The following hashes were recomputed before and after the attacks and did not
move:

| Object | SHA-256 |
| --- | --- |
| stage 1 `code/rate_defined_tensor_f0_packed.py` | `447aa3bc224685ea1cc556d9d322dafba05ef148945d4ae41291f83e29f3deb4` |
| stage-1 tests `code/test_rate_defined_tensor_f0_packed.py` | `adf4e7dd316a623ff2248d8876592bd6799045976369211f1f0da1ecd6b80458` |
| directed action `code/rate_defined_tensor_f0_packed_interval_action.py` | `2f3201a9eb1b6fbe577b43c3b046ad5f7f369816a7d4a32f4381506e63494f2a` |
| directed tests `code/test_rate_defined_tensor_f0_packed_interval_action.py` | `8ec937f23579d3560cda7a505a7960b14cf297cfa9f7f8b4604eed121e40362d` |
| Round-154 implementation record | `eba413a7cfe57061196c2a5cead79007d1ae27e8da1966d5ddb16d907716aff7` |

## Findings

### P0

None found within the explicitly bounded centre-matrix interval-action object.

### P1

None found on the frozen repaired byte set.

### Boundary retained: the result digest is not authentication

The new consistency digest closes the exact simple mutations from Round 152.
Replacing the enclosure with a different finite ordered owned array and
updating only its raw hash is rejected.  Relabelling `P` as `Q` while changing
the nonnegative flag is also rejected.  Both failures returned the directed
binding hold.

The digest is intentionally public and unkeyed.  I then recomputed it after
each coherent mutation; both mutated objects passed the same-process result
validator.  This confirms the documented boundary precisely: the digest
detects accidental or partial relationship drift, but it is not
authentication, provenance, producer-independent recomputation, or a fresh
verifier receipt.  No downstream stage may upgrade it to any of those roles.

## Round-152 P1 replay

The independent payload had shape `(2,3,4)` and the same 24 endpoint rows for
every block size.  Its valid form contained ordinary `+0.0` in both lower and
upper positions.  Its invalid form changed endpoints at flat positions
`0,3,15,16,23` to `-0.0`, crossing the old vector-dispatch threshold and block
boundaries.

Each block size was run by a new OS Python process.  The aggregate result was:

```text
fresh processes                 99
block sizes                     1..99
valid +0 payload                99/99 PASS
selected -0 payload             99/99 HOLD_F0_PACKED_ENDPOINT_INVALID
positive raw SHA-256            4c640e8dd627e6310aedaca34058cd5e3bdbc0ba342216c86f9fe03d360aa9f5
negative raw SHA-256            20c8dd6e464e51d9b5d371e522d7ecc9612a3d66a78355878163d87adb431581
raw hashes across block sizes   stable
```

This directly attacks the previous `1..15` pass / `16..99` false-rejection
split rather than merely replaying a single saved block.

## Contiguous `out=` audit and the 2B ledger

I statically traversed every NumPy `out=` site in both implementation files.
The canonical stage-1 validator allocates exactly
`bool[(2,B)]`, with C strides `(B,1)`, then writes only to the contiguous rows
`scratch[0,:count]` and `scratch[1,:count]`.  The directed enclosure validator
uses the same layout.  There is no remaining `scratch[:,k]` output target.

All directed arithmetic destinations are owned one-dimensional work arrays or
their unit-stride prefixes.  Inputs such as `values[:, endpoint]` may be
strided, but no ufunc writes into them.  The single in-place
`logical_and(..., out=first)` in stage 1 also targets the same contiguous first
row.

As an independent dynamic check, I wrapped the action-relevant NumPy calls and
observed `2542` real `out=` writes while loading, contract-probing, validating,
and applying both `P.T` and `Q.T` on a 24-state mixed-boundary problem.  Every
observed output was C-contiguous.  The allocation trace saw the expected
`((2,5), strides=(5,1), nbytes=10)` Boolean validation buffer.

For `N=24`, `B=5`, both results independently satisfied:

```text
output payload                  16 N = 384 bytes
action workspace                81 B = 405 bytes
canonical validation scratch     2 B =  10 bytes
vector runtime probe                     2048 bytes
maximum new NumPy payload       16 N + max(81 B, 2 B, 2048) = 2432 bytes
```

This is an exact visible NumPy-payload identity only.  It excludes pre-owned
kernel/input storage and Python-object, allocator, RSS, and swap overhead; it
is not a production memory acceptance.

## Independent heterogeneous exact oracle

The independent oracle did not import the saved test helpers or the directed
rounding helpers.  It used different dyadic rate and killing patterns from the
saved suite, reconstructed row-major coordinates and incoming source/rate
indices locally, derived the exact uniformization rate and centre
coefficients, and formed every interval product and sum using
`Fraction.from_float`.

Coverage was:

| Shape | Boundaries | Operators | Blocks | Exact rows |
| --- | --- | --- | --- | ---: |
| `(4,)` | reflecting | `P.T`, signed `Q.T` | `1,3,7,99` | 32 |
| `(3,4)` | reflecting, periodic | `P.T`, signed `Q.T` | `1,3,7,99` | 96 |
| `(2,3,4)` | periodic, reflecting, periodic | `P.T`, signed `Q.T` | `1,3,7,99` | 192 |
| **Total** | one through three dimensions | 24 actions | four block sizes | **320** |

The independently derived `Q` diagonals, `P` self coefficients, directional
off-diagonal coefficients, and uniformization rate matched the owned kernel
bytes.  Every exact rational lower/upper action value lay inside the published
binary64 enclosure, and all six shape/operator byte groups were invariant over
the four block sizes.

## Vectorized rounding and subnormal gate

The repaired runtime gate was independently invoked at lengths `16`, `24`,
`64`, and the additional length `99`.  A separate contiguous-array attack
checked `203` vectorized products against exact `Fraction` products after lower
and upper `nextafter`.  It included positive and negative minimum subnormals,
half-minimum-subnormal products that round to signed zero, preserved minimum
subnormals, and ordinary nonexact products.  All enclosures and signed-zero
checks passed.

This supports the frozen runtime only; the binding remains
`python-3.12.13|numpy-2.5.1|machine-arm64` and must fail closed on drift.

## Reproduced project suites

Run from `research/reports/encounter_multimodal_prr`:

```bash
../../../.venv/bin/ruff check \
  code/rate_defined_tensor_f0_packed.py \
  code/rate_defined_tensor_f0_packed_interval_action.py \
  code/test_rate_defined_tensor_f0_packed.py \
  code/test_rate_defined_tensor_f0_packed_interval_action.py

PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=code \
  ../../../.venv/bin/python -m pytest -q -p no:cacheprovider \
  code/test_rate_defined_tensor_f0_packed.py \
  code/test_rate_defined_tensor_f0_packed_interval_action.py
```

Observed:

```text
ruff                                             PASS
stage1 packed + directed suites                  64 passed
fresh real-validator processes                   99/99 correct
independent heterogeneous Fraction oracle        320 rows / 24 actions PASS
independent vector/subnormal products             203 PASS
largest state count exercised                     24
```

## Acceptance boundary

```text
Round-152 contiguous-output P1                  CLOSED ON FROZEN HASHES
all action/validator ufunc outputs              CONTIGUOUS IN STATIC + DYNAMIC ATTACK
2 B canonical validation ledger                CONFIRMED
heterogeneous direction/position/killing action 320 EXACT ROWS PASS
vectorized binary64/subnormal runtime gate      PASS ON BOUND RUNTIME
result relationship consistency                PASS / NOT AUTHENTICATION
separate implementation / fresh verifier       OPEN
centre-to-rate-interval error composition       OPEN
production uniformization, Poisson, and jets    OPEN
batched scalar topology                         OPEN
7,165,305-state RSS, swap, and timing gate      NOT RUN
F0                                               HOLD
F1 / positive-budget science                    NOT AUTHORIZED / NOT RUN
```

Round 154 is therefore independently accepted only as a small, science-free,
bounded implementation primitive.  No release, F0, F1, or PRR evidentiary
decision follows from this re-audit.
