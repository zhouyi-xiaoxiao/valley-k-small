# Round 159: independent attack on the fresh rate-action verifier design

Date: 2026-07-14

Decision: **ARCHITECTURE DIRECTION SOUND, BUT FIVE P1 DESIGN GAPS REMAIN / EXACT DESIGN NOT READY TO FREEZE / NO VERIFIER IMPLEMENTATION ACCEPTED / HOLD F0 / NO F1 / HOLD PRR**

Severity count: **P0 = 0, P1 = 5, P2 = 3**.

## Scope and exact inputs

This was an independent, read-only design attack on:

```text
notes/f0_rate_action_fresh_verifier_design.md
SHA-256 a0848270c678cdaa93b28452acf8256b68e50449a785416379d90f92f9dc71df
```

The design was compared with the exact frozen subordinate sources and the
Round-157 preimplementation boundary:

```text
code/rate_defined_tensor_f0_packed.py
SHA-256 447aa3bc224685ea1cc556d9d322dafba05ef148945d4ae41291f83e29f3deb4

code/rate_defined_tensor_f0_packed_interval_action.py
SHA-256 2f3201a9eb1b6fbe577b43c3b046ad5f7f369816a7d4a32f4381506e63494f2a

audits/round_157_rate_action_composition_preimplementation_attack.md
SHA-256 bd68ad9db20ac1f79e997be8a6bb070469a65058fc4e166e917fc1d7ed3b4e0d
```

The current producer composition source was inspected only to determine what
an adapter would have to serialize; it was not accepted by this audit:

```text
code/rate_defined_tensor_f0_packed_rate_action.py
SHA-256 d47c37fa263663129ead0153b42ce2e8b77ba98f3ddc03116c38d32c1c9b3875
```

No selector, positive budget, Poisson propagation, generator jet, topology
calculation, physical observable, production-size allocation, F1/F2/F3 row, or
science run was executed.  No wire, adapter, verifier, receipt, or protocol
implementation was presented for acceptance.

## What survived the attack

Several design choices are correct and should be retained after the P1 issues
below are repaired.

1. The wire / producer-adapter / verifier split correctly prevents the
   verifier from importing a producer-defined artifact dataclass merely to
   parse a schema.  Reusing the frozen stage-1 and directed primitives while
   independently reimplementing only the composition layer supports exactly
   the limited claim `separate_composition_implementation=true`.
2. The numerical request and artifact are separated.  The child computes from
   reconstructed kernel, state, and contract bytes before receiving the
   producer body or output bytes.  The distinction between a numerical-
   semantic commitment and a request-bound outer commitment is sound.
3. The capability is generated before the request digest, the request binds
   its capability digest and hidden artifact digest, and frames are intended
   to carry capability-keyed HMACs.  This is suitable for launch/session
   binding.  The note correctly does not promote that public launch evidence
   into recurrence authority.
4. One-outstanding-chunk flow control, exact sequence/cumulative-length/
   rolling-hash ACKs, and private spooling are a viable way to avoid an
   unbounded retained chunk list or `b''.join` copy.
5. The core -> provenance -> manifest graph is locally acyclic because the
   provenance references the current core rather than the current manifest.
   This local property is distinct from the broken transition-lineage rule in
   P1-1 below.
6. The two zero policies are correctly separated.  Source nominal `-0.0` is
   preserved by its source hash, both point-lift endpoints are canonical
   `+0.0`, and subordinate nominal output bits, including `-0.0`, remain
   unchanged.
7. The required witness order exactly matches the frozen stage-1
   `EXPECTED_WITNESS_NAMES`: all eleven exact fractions, indices, and least
   binary64 upper values are required.  The design does not regress to the
   earlier three-witness subset.
8. The frozen subordinate payload identities support
   `Kraw = 16N + 32S` and `Knum = 40N + 64S`.  The four composition-phase
   identities also agree with Round 157 before protocol metadata is added:

   ```text
   point lift       24N + 2C
   directed action  40N + max(81C, 2C, 2048, F)
   nominal action   48N + 65C
   final recheck    48N + max(2C, F, J)
   ```

9. The note correctly states that a standalone one-step radius is declared and
   non-authoritative, that a naked public receipt cannot create authority, and
   that largest-shape promotion is blocked by unknown resource overhead.

These positives do not close the P1 findings.

## P0 findings

No P0 theorem or science-boundary defect was found.  The note remains
method-only, keeps `science_executed=false` and `f0_pass=false`, and does not
authorize a positive-budget or production computation.

## P1-1: the output provenance rule cannot represent the transition that creates the output

The provenance schema requires an output or replayed input to bind an immediate
predecessor core, request, receipt, output nominal hash, radius, and action
index.  The same section then says that `predecessor_request_sha256` and
`predecessor_receipt_body_sha256` describe only an already closed transition
that established the **input** lineage and must never refer to the receipt
currently being constructed.  The current receipt binds the output manifest
externally.

Those requirements cannot all hold for the first output transition:

- using the input's older receipt does not establish the newly computed output
  core and does not justify incrementing the output action index;
- using the current request but the older receipt creates a mismatched
  transition pair;
- using the current receipt is impossible while the output provenance and
  manifest are being frozen and also creates the receipt/manifest cycle that
  the design is trying to avoid; and
- copying the input provenance into the output changes
  `current_state_core_sha256` without recording the immediate transition that
  produced it.

The artifact and public receipt can externally compare input and output for one
non-authoritative call, but that does not make the output provenance body a
valid lineage node for same-worker continuation or full-chain replay.  The
design needs one acyclic transition object with an unambiguous construction
order—for example a pre-receipt transition core that binds request, input core,
output core, operator, and contract, followed by an external receipt that binds
that transition and output manifest.  The exact remedy is outside this audit;
the current design is held.

## P1-2: the first request-header receive cap is circular

The exact spawn bootstrap contains only the parent PID, capability, and two
connection endpoints.  It contains no trusted header-size cap.  The next phase
requires the child to call conceptually

```text
recv_bytes(maxlength=maximum_header_bytes + 1)
```

but `maximum_header_bytes` is itself a field inside the not-yet-received,
caller-formed request body.  The child cannot safely obtain that value before
performing the receive that it is supposed to bound.  A limit learned from the
untrusted frame is not cap-first validation.

The wire protocol needs a verifier-source-frozen first-frame constant, known
before any receive, and the request field must subsequently equal or be no
larger than that constant.  The same distinction is needed between a compiled
bootstrap bound and the later request-declared resource caps.  As written, the
claimed preallocation/header gate is not implementable.

## P1-3: blocking `send_bytes` does not provide the promised end-to-end deadline

The note requires a bounded deadline and says every timeout, disconnect, child
crash, or wrong phase terminates and joins the child.  The transport is limited
to blocking `Connection.send_bytes` and bounded `recv_bytes`, with the sender
writing a chunk before waiting for its ACK.

A stalled child can stop reading while the parent is inside `send_bytes`.
`Connection.poll()` can bound a later receive, but it does not interrupt an
already blocking write.  The note also treats the OS pipe-buffer size as an
observation that may be unknown, so it cannot assume every `W`-byte frame is
guaranteed to fit without blocking.  The symmetric child-to-parent write has
the same issue if the launcher stops reading.

Therefore the deadline and guaranteed cleanup cannot be derived from the
stated primitives.  The design must freeze a bounded-write mechanism—such as
an audited nonblocking framed transport, a separately supervised writer whose
failure can be terminated, or another mechanism with a proved write timeout—
and include its payload/lifetime cost.  Per-chunk ACK discipline limits queued
user data; it does not by itself bound the preceding write call.

## P1-4: the child and producer-adapter payload identities omit simultaneously live metadata and preflight work

The numerical `N`/`S`/`C` terms are sound, but the complete protocol identities
are not yet exact.

First, `J` is defined as the maximum canonical metadata/hash **scratch** bytes.
Before `COMPUTED_COMMITMENT`, however, the child must retain its computed state
core, provenance, manifest, eleven-witness/shared semantic ledger, resource
ledger, commitment bodies, and their hashes while serializing another body.
After reveal it additionally retains the producer artifact body and both
computed and producer output bytes.  Retained canonical bodies are not scratch
and cannot be represented by `max(..., J)` unless `J` is redefined and tested as
the maximum **total simultaneously live metadata plus scratch**.  The displayed

```text
output-byte freeze:       Knum + 56N + max(2C, F, J)
post-release comparison:  16N + J + W
receipt construction:     J + receipt_serialized_bytes
```

therefore lack an exact retained-metadata term under the note's own definition
of `J`.

Second, request-header preflight validates local source hashes and reconstructed
contracts before accepting a large section.  The frozen directed validator
uses `Path.read_bytes()` for source hashing and its runtime probe allocates
2048 bytes.  The initial receive/preflight phase shown as

```text
Kraw + 8N + J + W
```

does not include the applicable `F` source-read payload or runtime-probe
payload at that phase.  Later inclusion of `F` in a directed-action maximum
does not make every published phase identity true, especially for the required
one-byte-lower phase attacks.

Third, the producer-adapter section says that every coexistence period will be
recorded but gives no frozen phase algebra for producer state, immutable output
copy, artifact nested bodies, old/new serialization buffers, source reads, and
adapter result.  This is not enough to derive the promised producer cap or the
aggregate one-byte boundary from the design alone.

The fix must distinguish retained metadata from transient encoder chunks,
include header-preflight source/probe work where it actually lives, and freeze
producer-adapter phases before an implementation can claim an exact payload
ledger.

## P1-5: the verifier import/AST policy is both incomplete and literally unsatisfiable

The note says that the verifier "may import only" the wire, frozen stage-1, and
directed modules.  Taken literally, that forbids the standard-library and
NumPy imports required for `spawn`, PID checks, pipes, temporary spools,
deadlines, exact `Fraction` arithmetic, hashing/HMAC, binary64 handling,
resource observations, and verifier-owned arrays.  Accessing `packed.np`,
`packed.Fraction`, or other subordinate module globals to evade the literal
rule would weaken the claimed independent implementation.

If the sentence was intended to restrict only project numerical modules, the
actual standard-library/NumPy allow-list is not frozen.  An unrestricted
stdlib surface also leaves obvious independence escapes beyond the listed AST
tokens, including subprocess/runpy execution, `compile` plus constructed
functions, `ctypes`, `marshal`, frame inspection, and reflective access to the
protocol caller's locals.  This matters because the request, hidden artifact
digest, and producer source/model hashes exist in the same child process before
the supposedly artifact-blind numerical call.

The design must state an exact project-module and external-module allow-list,
freeze forbidden calls/attributes as well as import names, and require the
numerical entry to receive only reconstructed numerical arguments without
closure, caller-frame, module-global, filesystem-execution, or subprocess
access.  Static checks still would not prove mathematical correctness, but the
present rule cannot yet be implemented or audited consistently.

## P2 findings and explicit non-claims

### P2-1: several canonical wire schemas remain placeholders

The state core/provenance/manifest fields are enumerated, but the complete
kernel header, ordered raw-section manifest, composition-contract body,
artifact-adapter callable boundary, frame binary layout, and exact HOLD mapping
are deferred to future source files.  That is acceptable for a planning note
only.  It means the exact wire cannot be accepted until those source bytes and
mutation tests exist; no implementation may infer authority from the current
note alone.

### P2-2: authoritative recurrence is an honest future boundary, not a delivered protocol

The one-shot spawn API exits after one action and implements neither a retained
same-private-worker session nor a full-chain request/replay wire.  The note is
correct to keep standalone output non-authoritative.  The two selected future
routes must receive their own state machine, restart/failure semantics,
resource ledger, and adversarial replay tests before any input radius can carry
`authoritative_input_radius=true`.

### P2-3: the mutation plan must vary every nonnumerical precommit field, not only the artifact digest

Invariance of `verifier_numeric_semantic_sha256` under a changed hidden artifact
digest is necessary.  The same test should vary every precommit field excluded
from the numerical function, including producer/adapter source hashes,
producer operation-model hash, outer request-only resource caps where
semantically admissible, and capability/session identifiers.  Otherwise an
accidental dependency can remain undetected even while the one named digest
test passes.

## Acceptance matrix

```text
three-file separation direction                    ACCEPTABLE IN PRINCIPLE
separate composition claim                         CORRECTLY SCOPED ONLY
canonical state body encoding                      ACCEPTABLE IN PRINCIPLE
output transition provenance                       P1 / NOT CONSTRUCTIBLE AS WRITTEN
capability-before-request HMAC                      ACCEPTABLE IN PRINCIPLE
first-frame cap-first receive                       P1 / CIRCULAR
compute-before-reveal ordering                      ACCEPTABLE IN PRINCIPLE
chunk ACK and private spool direction               ACCEPTABLE IN PRINCIPLE
bounded deadline and guaranteed cleanup             P1 / NOT DERIVED
Kraw, Knum, and base composition identities         ACCEPTABLE
full producer/parent/child/aggregate identity        P1 / INCOMPLETE
signed-zero policy                                  ACCEPTABLE
all eleven frozen witnesses                         ACCEPTABLE
naked public receipt as recurrence authority         REJECTED CORRECTLY
same-worker or full-chain recurrence                 NOT IMPLEMENTED
AST/import gate                                     P1 / NOT YET COHERENT
fresh verifier source bytes                         NOT PRESENTED
production target                                   NOT ALLOCATED OR RUN
F0                                                  HOLD
F1/F2/F3                                            NOT AUTHORIZED / NOT RUN
PRR release                                         HOLD
```

## Verdict

The exact design at SHA
`a0848270c678cdaa93b28452acf8256b68e50449a785416379d90f92f9dc71df`
is materially stronger than a same-implementation spawn replay and preserves
the correct theorem/science boundary.  It is not yet self-consistent enough to
freeze as the implementation contract.  The transition DAG, trusted first-
frame cap, bounded-write deadline, complete resource identities, and exact
import/AST boundary must be resolved and independently re-attacked first.

No verifier implementation, fresh-process authority, F0 pass, recurrence
authority, scientific result, continuum result, or PRR release is accepted by
Round 159.
