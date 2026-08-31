# Fresh-process, separate-implementation verifier for the F0 rate action

Date: 2026-07-14  
Status: **DESIGN ONLY / HOLD F0 / NO SCIENCE AUTHORIZED**  
Scope: science-free verification of one packed point-plus-`l1`-ball `P.T` or
`Q.T` action.  This note does not authorize Poisson propagation, generator
jets, topology evaluation, a positive-budget row, F1/F2/F3, a production-size
run, or any release-gate change.

## 1. Decision and trust boundary

The existing stage-1 `ProducerActionArtifact` / `VerifierReplayReceipt`
mechanism is a useful **process-isolation and binding pattern**, but its
numerical body is not a separate implementation.  The spawn child rebuilds
the kernel and then calls the same `block_p_transpose` implementation used by
the producer.  That establishes fresh-process reconstruction and deterministic
agreement on the tested bytes; it does not establish producer-independent
composition correctness.

The next verifier must therefore use a second numerical source file and must
independently implement the composition layer.  It may call the already
audited stage-1 packed kernel/action and directed centre-action primitives as
subordinate operations.  Its claim is consequently
`separate_composition_implementation=true`, not a claim that the stage-1 or
directed numerical kernels have themselves been reimplemented a second time.

The verifier remains method-only.  A successful receipt has status no stronger
than

```text
PASS_RATE_ACTION_METHOD_ONLY_NOT_F0
```

and retains `science_executed=false` and `f0_pass=false`.

## 2. Existing replay elements that may and may not be reused

The following patterns may be reused:

- `multiprocessing.get_context("spawn")`, an actual `Process.pid` check, a
  bounded deadline, and terminate/join/pipe-close cleanup on every failure;
- a freshly generated 32-byte launch capability, domain-separated hashes, and
  canonical JSON request and artifact bodies;
- immutable source `bytes` and exact manifests crossing the process boundary,
  followed by verifier-owned reconstruction of all numerical arrays;
- exact dataclass and nested-type checks, science-free roles, source/contract
  hashes, kernel replay hashes, and exact witness rebinding;
- blockwise `hmac.compare_digest` for immutable raw output bytes;
- a direct-call entry point that fails closed and forces callers through the
  spawn launcher; and
- a receipt containing only hashes, canonical scalar values, counts, flags,
  and resource observations.

The following are not reusable as verification authority:

- the existing `_verify_action_artifact_owned` numerical body, because it
  invokes the producer's action implementation;
- the existing `VerifierReplayReceipt` schema, which has no input-radius
  provenance, composition source/contract binding, scalar derivation trace,
  memory phases, array-exposure flag, or separate-implementation evidence;
- the existing request construction order, because the request is formed
  before its capability and therefore does not bind that capability;
- a public consistency digest, a naked receipt digest, or a caller-supplied
  `authoritative=true` flag; and
- a one-phase child invocation in which producer output bytes are available
  before the verifier has committed to its independent result.

## 3. Three-file architecture and exact wire boundary

A two-file producer/verifier split is insufficient.  The verifier cannot both
forbid importing the producer composition module and require exact instances
of artifact dataclasses defined by that module.  The implementation boundary
is therefore frozen as three files:

```text
code/rate_defined_tensor_f0_packed_rate_action_wire.py
code/rate_defined_tensor_f0_packed_rate_action_artifact_adapter.py
code/rate_defined_tensor_f0_packed_rate_action_verifier.py
```

The wire file is protocol-only.  It may use built-in scalar types,
`hashlib`, `hmac`, `json`, and `struct`; it must not import NumPy, the stage-1
module, the directed module, the producer composition module, or the artifact
adapter.  It defines domain separators, exact field orders, strict canonical
ASCII encoders/decoders, bounded frame codecs, and frozen HOLD codes.  It does
not define or execute a numerical formula.

The artifact adapter is the only new file allowed to import
`rate_defined_tensor_f0_packed_rate_action.py`.  It exact-type validates the
producer's private `InternalRateActionState`, copies its nominal output to
immutable built-in `bytes` while preserving every binary64 bit, builds the
canonical artifact body, and records its own serialization lifetime.  The
adapter produces wire data; it is not part of the independent verifier.

The verifier may import only the pure wire file, the frozen stage-1 packed
module, and the repaired directed-action module.  It must not import the
producer composition module or the artifact adapter, even for type hints,
constants, schemas, validators, exceptions, or test fixtures.  It independently
implements:

- blockwise point lifting and canonicalization of both point-lift zero signs to
  `+0.0`;
- the increasing-flat-index reductions for `m` and `a`;
- exact-`Fraction` to least binary64 upper-bound conversion;
- its own `add_up` and `mul_up` scalar primitives;
- the frozen P and Q formula traces;
- verifier-local exact schema objects after wire parsing;
- verifier-local phase and resource identities; and
- post-commit artifact comparison and scalar-only receipt construction.

The allowed subordinate numerical calls are conceptually limited to:

```text
packed.build_packed_tensor_kernel
packed.block_p_transpose
packed.block_q_transpose
directed.directed_p_transpose
directed.directed_q_transpose
```

The public boundary does not pass a producer-defined dataclass.  It passes
fixed exact built-in tuples whose leaves are exact built-in `bytes`:

```text
kernel_wire = (kernel_header_body_bytes, kernel_raw_section_bytes_tuple)
input_state_wire = (
    state_core_body_bytes,
    provenance_body_bytes,
    state_manifest_body_bytes,
    nominal_raw_bytes,
)
producer_artifact_wire = (artifact_body_bytes, output_nominal_raw_bytes)

spawn_verify_rate_action_artifact(
    kernel_wire,
    input_state_wire,
    composition_contract_body_bytes,
    producer_artifact_wire,
) -> RateActionVerifierReceipt
```

These tuples are launcher-side API containers only.  They never enter
`Process(..., args=...)`; Section 6 streams their byte leaves after spawn.  An
`ndarray`, dataclass from another module, `memoryview`, `bytearray`, mutable
nested container, user buffer, or subclass of `bytes`/`tuple` fails before
process creation.  The child parses canonical bytes into verifier-local exact
types.  Thus producer exact-type checks remain in the adapter, verifier
exact-type checks remain in the verifier, and no numerical implementation is
imported merely to share a schema.

The child reconstructs the nominal block-action and directed-action contracts
from the single composition-contract body and requires

```text
reconstructed_stage1_action_contract_sha256
    == reconstructed_directed_contract.stage1_action_contract_sha256
```

as well as exact agreement of shape, block size, runtime, byte order, source
hashes, summation order, and subordinate backend bindings.  Producer and
verifier composition operation-model hashes are each frozen and bound, but
they are deliberately **not required to be equal**: separate implementations
may have different internal operation models while producing the same frozen
semantic result.

A static import-graph and AST test covers all three files.  For the verifier it
rejects producer/adapter imports, producer helper names, dynamic imports,
`exec`, `eval`, `sys.modules` indirection, `pickle`/`dill`/`cloudpickle`,
`Connection.send`/`recv`, queues, `fork`, and direct `frombuffer` views.  For
the wire file it additionally rejects every numerical-module import.  A source
split and AST check establish a code boundary, not mathematical correctness;
exact oracles and an independent adversarial audit are still required.

## 4. Canonical state wire and acyclic provenance DAG

### 4.1 Canonical wire rules

Every semantic body is exact built-in ASCII `bytes` produced by one canonical
encoder with `allow_nan=false`, sorted keys, fixed separators, and no optional
spellings.  A receiver parses, exact-type checks every leaf, re-encodes, and
requires byte-for-byte identity before using a field.  Integers are JSON
integers with frozen ranges; binary64 scalars are canonical `float.hex()`
strings plus the SHA-256 of their canonical big-endian eight-byte encoding.
NaN, infinity, negative radius, negative-zero radius, duplicate keys, unknown
keys, non-ASCII input, or a second textual representation fails closed.

Large numerical bytes are never embedded in JSON.  Each body carries the exact
section name, length, and SHA-256, and the raw built-in `bytes` travel as a
separate framed section.  A body digest is over the complete canonical body,
not a hand-reconstructed subset of fields.

### 4.2 State core

The state core contains all current-state semantics but no lineage reference:

```text
schema
role                               # exact science_free_* role
logical_shape
state_count
raw_byte_length                    # exactly 8 N
raw_sha256
dtype_and_order                    # frozen native binary64 C order
runtime
nonnegative
nominal_zero_policy
l1_radius_upper_hex
l1_radius_upper_be_sha256
producing_operator                 # frozen null or exact P/Q
producing_composition_contract_sha256  # frozen null or exact hash
```

The complete canonical state-core body is hashed with its own domain:

```text
state_core_sha256 = H(state_core_domain, state_core_body_bytes)
```

### 4.3 Complete provenance body

The payload carries the **complete canonical provenance body**, not merely its
hash.  Its fields are:

```text
schema
kind
lineage_mode
action_index
current_state_core_sha256
root_initial_state_core_sha256
root_initial_nominal_sha256
root_initial_l1_radius_upper_hex
predecessor_state_core_sha256
predecessor_request_sha256
predecessor_receipt_body_sha256
predecessor_output_nominal_sha256
predecessor_output_l1_radius_upper_hex
private_lineage_mac_hex_or_frozen_null
authoritative_input_radius
```

For a declared one-step input, `current_state_core_sha256` and
`root_initial_state_core_sha256` agree, `action_index=0`, every predecessor
field has one frozen null representation, and
`authoritative_input_radius=false`.  For an output or replayed input, the root
and immediate predecessor core hashes, request, receipt, nominal hash, radius,
and exact action index must all agree with the reconstructed chain.  Fields
that do not apply use the one frozen null form; empty strings and caller-chosen
alternatives are forbidden.

The hash graph is explicitly acyclic:

```text
nominal raw bytes --> state core body --> state_core_sha256

root/predecessor/current core hashes
    --> complete provenance body --> provenance_body_sha256

state_core_sha256 + provenance_body_sha256
    --> state manifest body --> state_manifest_sha256
```

The provenance body may reference the current, root, and predecessor **core**
hashes.  It must never reference the current full manifest hash.  The manifest
therefore cannot be made self-referential by a provenance field.

`predecessor_request_sha256` and `predecessor_receipt_body_sha256` describe
only an already closed transition, if any, that established the input lineage.
They never refer to the receipt currently being constructed.  The current
receipt binds the output manifest externally; it is not inserted back into the
output provenance body.  This also prevents a receipt/manifest cycle.

### 4.4 Manifest and payload

The canonical manifest body is small and complete:

```text
schema
state_core_sha256
provenance_body_sha256
manifest_binding_domain
```

The input wire bundle contains all four exact byte leaves:

```text
state_core_body_bytes
provenance_body_bytes
state_manifest_body_bytes
nominal_raw_bytes
```

Validation recomputes the raw hash, core hash, provenance hash, manifest hash,
radius binary encoding, lengths, and every cross-reference before numerical
allocation.  The receiver then reconstructs a new owned native read-only
array, rechecks the source raw hash after reconstruction and after the action,
and never treats the caller's bytes as an array view.

### 4.5 Two distinct zero policies

The point-lift policy remains:

```text
CANONICAL_POINT_LIFT_ZERO_TO_POSITIVE_ZERO
```

Both `-0.0` and `+0.0` in the source nominal become `+0.0` at both interval
endpoints.  This policy applies only to the constructed point lift.

The nominal output policy is instead:

```text
PRESERVE_SUBORDINATE_NOMINAL_OUTPUT_BITS
```

Neither the adapter nor verifier may canonicalize, normalize, or rewrite an
output zero.  Any subordinate `-0.0` output bit is preserved in immutable raw
bytes and must compare exactly.  Tests must exercise a source `-0.0`, a
canonical `+0.0` point lift, and preserved signed-zero output independently.

## 5. Producer artifact and separated ledgers

### 5.1 Canonical artifact wire

The adapter emits `(artifact_body_bytes, output_nominal_raw_bytes)`.  The body
is explicitly non-authoritative method evidence and contains:

```text
schema
status = PRODUCER_RATE_ACTION_METHOD_ARTIFACT_NOT_AUTHORITY
producer_pid                         # informational only
producer_runtime
operator                             # exact P or Q
wire_source_sha256
adapter_source_sha256
producer_composition_source_sha256
producer_operation_model_sha256

kernel_inputs_sha256
kernel_contract_sha256
kernel_replay_sha256
kernel_ledger_sha256
witness_binding_sha256
stage1_action_contract_sha256
directed_action_contract_sha256
composition_contract_sha256

input_state_core_sha256
input_provenance_body_sha256
input_state_manifest_sha256
input_nominal_sha256
input_nominal_byte_length
input_l1_radius_upper_hex

point_lift_raw_sha256
point_lift_binding_sha256
directed_output_raw_sha256
directed_output_byte_length

shared_semantic_ledger_body
shared_semantic_ledger_sha256
producer_resource_ledger_body
producer_resource_ledger_sha256

output_state_core_body
output_state_core_sha256
output_provenance_body
output_provenance_body_sha256
output_state_manifest_body
output_state_manifest_sha256
output_nominal_sha256
output_nominal_byte_length
output_l1_radius_upper_hex
output_l1_radius_upper_be_sha256
output_nominal_zero_policy = PRESERVE_SUBORDINATE_NOMINAL_OUTPUT_BITS

producer_internal_state_arrays_exposed = true
artifact_arrays_exposed = false
artifact_contains_immutable_numeric_bytes = true
science_executed = false
f0_pass = false
```

The three nested state bodies and the two nested ledgers above are canonical
scalar JSON subobjects, not base64 strings or a second JSON encoding of their
body bytes.  Hashing each subobject uses its own domain and canonical encoding;
hashing the artifact uses the one complete canonical artifact body.  Unknown
or omitted nested fields therefore cannot hide behind a retained sub-hash.

The body digest is the domain-separated SHA-256 of these complete canonical
body bytes.  The raw output is not duplicated inside the body.  Validation
requires

```text
type(output_nominal_raw_bytes) is bytes
sha256(output_nominal_raw_bytes) == output_nominal_sha256
output_nominal_sha256 == output_state_core.raw_sha256
len(output_nominal_raw_bytes) == output_nominal_byte_length == 8 N
```

The adapter hashes the producer ndarray before copying, copies with C-order
bit preservation, hashes the immutable bytes, rehashes the producer ndarray,
and fails if any value or bit changed.  Its producer resource ledger counts the
period when the `8N` producer ndarray and `8N` immutable output bytes coexist.
The immutable bytes are data payload, not array or lineage authority.

### 5.2 Complete ordered witness and scalar semantics

The shared semantic ledger contains the exact ordered eleven-entry witness
tuple from the reconstructed stage-1 kernel:

```text
maximum_target_exit_upper
maximum_center_exit
delta_q
delta_p_direct
p_coefficient_rounding
delta_p_via_q
delta_p_selected
maximum_center_row_sum
maximum_qhat_abs_row_sum
maximum_killing_upper
maximum_killing_uncertainty
```

Every entry contains exactly

```text
name, numerator, denominator, flat_index, least_upper_binary64_hex
```

including the frozen `flat_index=-1` convention for derived witnesses.  The
adapter and verifier reject omission, duplication, reordering, renamed fields,
a changed sign, a non-reduced fraction, a changed index, or a one-ulp-lower
upper value.  A three-witness subset is insufficient.

The same ledger binds `e`, `m`, `a`, the formula identifier, increasing-flat-
index coverage, reduction and scalar-operation counts, and every frozen trace
intermediate:

```text
P: delta_p_selected*m, e+coefficient, output
Q: qhat+delta_q, q_norm*e, delta_q*m,
   propagated+coefficient, output
```

The verifier reconstructs all eleven witnesses from immutable kernel inputs,
then independently proves that the reported output radius is at least the
exact rational P or Q expression.  Producer/verifier byte equality is a
reproducibility gate, not a substitute for containment.

### 5.3 Three non-interchangeable hashes

The design separates:

```text
shared_semantic_ledger_sha256
producer_resource_ledger_sha256
verifier_resource_ledger_sha256
```

The shared semantic ledger must agree exactly.  The producer resource ledger
is validated against the producer operation model and adapter lifetime.  The
verifier resource ledger is validated against the separate verifier operation
model and contains parent, child, aggregate, IPC, and observation subledgers.
The two resource hashes and the two composition operation-model hashes are not
required to equal one another.  Requiring equality would either be false or
would pressure the verifier into copying the producer implementation.

## 6. Capability-bound chunk protocol

### 6.1 Computation request body

The canonical request body contains at minimum:

```text
schema
operator
launch_parent_pid
spawn_start_method = spawn
launch_capability_sha256
artifact_body_sha256                 # digest only before commitment

kernel_header_body_sha256
kernel_raw_section_manifest_sha256
kernel_inputs_sha256
kernel_contract_sha256
input_state_core_sha256
input_provenance_body_sha256
input_state_manifest_sha256
input_nominal_sha256
composition_contract_sha256
reconstructed_stage1_action_contract_sha256
reconstructed_directed_action_contract_sha256

stage1_source_sha256
directed_source_sha256
wire_source_sha256
producer_adapter_source_sha256
producer_composition_source_sha256
verifier_composition_source_sha256
producer_operation_model_sha256
verifier_operation_model_sha256
runtime
byteorder
tensor_shape
state_count
block_size

declared_initial_section_lengths
declared_reveal_section_lengths
maximum_header_bytes
maximum_chunk_bytes
maximum_spawn_bootstrap_bytes
maximum_private_spool_bytes
maximum_numeric_payload_bytes
maximum_total_child_payload_bytes
maximum_parent_payload_bytes
maximum_aggregate_payload_bytes
deadline_seconds_hex
```

The parent first generates an exact 32-byte capability and only then computes:

```text
request_sha256 = H(request_domain, complete_request_body_bytes)

request_capability_hmac =
    HMAC-SHA256(
        capability,
        request_hmac_domain || request_sha256 || artifact_body_sha256
    )
```

The capability itself enters only the fixed small spawn bootstrap and child
private state.  It never enters the artifact, receipt, log, HOLD detail, or
error text.  The receipt may contain only its SHA-256.  The child recomputes
the canonical request, capability digest, and HMAC before numerical
allocation.  Parent and child PIDs are checked against `os.getpid()`,
`os.getppid()`, and the launcher's actual `Process.pid`; `producer_pid` is
never process provenance.

### 6.2 Small spawn bootstrap

`Process(..., args=...)` contains only:

```text
exact parent PID integer
exact 32-byte capability
one parent-to-child Connection endpoint
one child-to-parent Connection endpoint
```

No request body, kernel bytes, nominal bytes, contract, provenance, artifact
body, output bytes, radius, witness, trace, or resource ledger may be a spawn
argument.  This exact shape is validated before `Process.start()`.  The
runtime's unavoidable small spawn serialization is separately capped and
observed; the implementation must not import or call `pickle` itself.  If its
payload cannot be bounded on the tested runtime, the observation is frozen as
unknown and blocks largest-shape promotion.  No full-size buffer may be
allocated as a side effect of spawning.

### 6.3 Header preflight, chunks, and ACKs

Use two one-way pipes.  Only `Connection.send_bytes` and bounded
`Connection.recv_bytes(maxlength=...)` are permitted; `send`, `recv`, queues,
and implicit user-payload pickle paths are forbidden.  Every frame has a fixed
binary header containing phase, section identifier, monotonically increasing
sequence number, declared total length, chunk length, rolling byte count,
payload SHA-256, request hash, and a capability-keyed frame HMAC.

The frozen state machine is:

1. `BOOTSTRAP`: spawn with only the small arguments above.
2. `REQUEST_HEADER`: parent sends a canonical bounded request header.  The
   child uses `recv_bytes(maxlength=maximum_header_bytes+1)`, validates exact
   types, all section lengths, integer overflow, contract-derived `N`, every
   parent/child/aggregate resource cap, source hashes, and the request HMAC
   **before** accepting any large section.
3. `READY_INITIAL`: child returns a capability-bound READY frame.  Only then
   may the parent stream kernel, input state core, complete provenance body,
   manifest, nominal raw bytes, and the composition contract.
4. `INITIAL_CHUNKS`: the parent sends one fixed-size-or-final-short chunk and
   waits for an exact capability-bound ACK containing phase, section, sequence,
   cumulative length, and rolling hash before sending the next chunk.  A new
   section begins only after an exact section-complete ACK.  At most one chunk
   is outstanding.
5. `INPUT_COMPLETE`: child reconstructs and rehashes all input bodies and raw
   sections, rechecks caps, then acknowledges input completion.  Fixed chunks
   are written sequentially to capped private anonymous spools; a growing
   `bytes` concatenation or retained chunk list is forbidden.  After a section
   is complete and its rolling hash agrees, it is read exactly once as the
   built-in `bytes` required by the subordinate packed API.  Every spool is
   closed on success or failure.
6. `COMPUTE`: child runs the independent implementation without reading a
   producer body, output byte, output radius, witness tuple, scalar trace, or
   producer resource ledger.  The numerical entry point accepts only the
   reconstructed kernel, input state, and verifier-local contract; artifact
   digest, producer source/model hashes, capability, and protocol state are not
   parameters and are not visible through module globals.
7. `COMPUTED_COMMITMENT`: child freezes its output raw hash, output radius,
   full eleven-witness semantic ledger, output state DAG, completed pre-reveal
   resource ledger, and declared post-reveal caps.  Later observations chain
   to this pre-reveal ledger; they cannot retroactively alter the computation.
   The child then sends only a small capability-bound commitment frame:

   ```text
   phase = COMPUTED_RATE_ACTION_V1
   verifier_pid
   launch_capability_sha256
   request_sha256
   verifier_numeric_semantic_sha256
   verifier_computation_sha256
   computed_output_nominal_sha256
   verifier_pre_reveal_resource_ledger_sha256
   ```

   `verifier_numeric_semantic_sha256` depends only on reconstructed numerical
   inputs, verifier-local contracts, and the computed result.  The outer
   `verifier_computation_sha256` additionally binds the request and pre-reveal
   resource ledger.  Thus two launches with identical numerical inputs but
   different hidden artifact digests must have identical numerical-semantic
   hashes even though their request-bound outer commitments differ.

8. `REVEAL_HEADER`: after validating that commitment against the actual child
   PID, the parent sends the canonical producer artifact body for the first
   time.  The child checks its already request-bound digest and declared reveal
   lengths, then returns `READY_REVEAL`.
9. `REVEAL_CHUNKS`: only after `READY_REVEAL` may the parent stream producer
   output bytes with the same per-chunk ACK discipline.  The child compares
   against its frozen result; producer data is never a computational input.
10. `RECEIPT`: child finalizes a verifier resource ledger whose hash chains to
    the committed pre-reveal ledger, then sends canonical receipt-body bytes or
    one frozen HOLD frame.  The launcher parses the bytes into a verifier-local
    scalar-only receipt, validates it, joins the exact child, and closes every
    endpoint.  Timeout, wrong phase, oversized frame, missing/duplicate ACK,
    disconnect, malformed body, nonzero exit, or cleanup failure terminates
    and joins the child before returning HOLD.

The parent must not write reveal data early even if an OS pipe could buffer it.
Tests instrument parent sends and child state transitions; merely delaying the
child's read is not compute-before-reveal.

## 7. Independent comparison and receipt

After commitment and reveal, the child requires exact agreement, without
tolerances, on:

- output byte length, core, provenance, and manifest bodies and hashes;
- blockwise nominal raw bytes, including signed-zero bits, and raw SHA-256;
- canonical output-radius hex and big-endian binary64 digest;
- all eleven ordered exact witnesses and every scalar-trace intermediate;
- point-lift, directed-output, contract, kernel, input-state, and provenance
  bindings; and
- the shared semantic ledger hash.

It does **not** require equality of producer/verifier operation-model or
resource-ledger hashes.  It independently validates each against its bound
source and model, and the receipt carries all three ledger hashes from Section
5.3.  The verifier also independently proves mathematical radius containment.

The receipt contains no `bytes`, ndarray, view, mutable object, or imported
producer schema.  Its minimum verifier-local schema is:

```text
schema
status = PASS_RATE_ACTION_METHOD_ONLY_NOT_F0
launch_parent_pid
verifier_pid
spawn_start_method = spawn

fresh_process = true
verifier_owned_reconstruction = true
separate_composition_implementation = true
separate_composition_only = true
subordinate_stage1_implementation_reused = true
subordinate_directed_implementation_reused = true
producer_arrays_accepted = false
producer_immutable_bytes_postcompute_only = true
producer_output_used_for_computation = false
arrays_exposed = false

launch_capability_sha256
request_sha256
request_capability_hmac
artifact_body_sha256
verifier_numeric_semantic_sha256
verifier_computation_sha256
verifier_pre_reveal_resource_ledger_sha256

stage1_source_sha256
directed_source_sha256
wire_source_sha256
producer_adapter_source_sha256
producer_composition_source_sha256
verifier_composition_source_sha256
producer_operation_model_sha256
verifier_operation_model_sha256

kernel_inputs_sha256
kernel_contract_sha256
kernel_replay_sha256
witness_binding_sha256
stage1_action_contract_sha256
directed_action_contract_sha256
composition_contract_sha256

input_state_core_sha256
input_provenance_body_sha256
input_state_manifest_sha256
point_lift_binding_sha256
directed_output_raw_sha256
output_state_core_sha256
output_provenance_body_sha256
output_state_manifest_sha256
output_nominal_sha256
output_nominal_byte_length
output_l1_radius_upper_hex
output_l1_radius_upper_be_sha256
output_nominal_zero_policy

ordered_witness_tuple                 # all eleven complete scalar entries
ordered_witness_tuple_sha256
shared_semantic_ledger_body
shared_semantic_ledger_sha256
producer_resource_ledger_sha256
verifier_resource_ledger_body
verifier_resource_ledger_sha256
parent_resource_ledger_body
parent_resource_ledger_sha256
child_resource_ledger_body
child_resource_ledger_sha256
aggregate_resource_ledger_body
aggregate_resource_ledger_sha256

science_executed = false
f0_pass = false
```

The validator recursively permits only exact built-in scalar types, fixed
tuples of scalars, and verifier-local frozen schema objects whose fields are
themselves scalar.  `arrays_exposed=false` is necessary but not sufficient;
structural inspection independently establishes the absence of numeric
payloads.

## 8. Authoritative radius lineage

An unkeyed public receipt, receipt digest, artifact digest, consistency digest,
or state manifest is forgeable by a caller who can recompute public hashes.
None can prove that an incoming radius was not understated.  The verifier
never accepts a caller-selected `authoritative_input_radius=true`.

There are exactly three defensible authoritative lineage designs:

1. **Same private worker.**  One verifier-owned worker retains the numerical
   state and radius internally across consecutive actions.  No public
   predecessor receipt recreates authority.  Only scalar/hash commitments
   leave the worker.
2. **Full-chain replay.**  A fresh verifier starts from an immutable initial
   payload and replays the complete ordered request chain, recomputing every
   state core, nominal vector, and radius.  It rejects skipped, reordered,
   duplicated, or altered steps.
3. **Private launcher MAC registry.**  A launcher retains a secret that never
   enters a public artifact or receipt and binds each accepted core by a
   chained HMAC such as

   ```text
   lineage_mac = HMAC(
       private_session_secret,
       predecessor_mac || receipt_body_sha256 || output_state_core_sha256
   )
   ```

   Loss of the registry or secret invalidates continuation authority; recovery
   requires full-chain replay.

This route selects same-private-worker continuation for an active recurrence
and full-chain replay from the immutable initial payload for restartable,
externally reproducible verification.  The private MAC registry is optional
later engineering and is not selected for the one-step patch.

Consequently, a standalone call uses only

```text
kind = DECLARED_METHOD_PRECONDITION
lineage_mode = PUBLIC_ONE_STEP_NONAUTHORITATIVE
authoritative_input_radius = false
```

and can produce only the method-only status.  Its output bytes, core,
provenance, and manifest support later reconstruction, but a subsequent call
that merely presents them with a public receipt remains non-authoritative.

## 9. Producer, parent, child, and aggregate resources

### 9.1 Frozen symbols and child numerical identities

Let

```text
N = product(tensor_shape)
S = sum(tensor_shape)
C = min(N, block_size)
Kraw = 16N + 32S
Knum = 40N + 64S
F = max(full source-read payload required by subordinate validators)
W = maximum wire chunk bytes including its fixed frame payload
J = maximum canonical metadata/hash scratch bytes
G = kernel builder working-payload cap
Dspool = Kraw + 8N
```

`Kraw` is the immutable interval-source payload: killing contributes `16N`
and forward/backward axis intervals contribute `32S`.  `Knum` is the child
kernel numerical payload after reconstruction: canonical killing intervals
and three retained state-centre arrays contribute `16N+24N`, while canonical
axis intervals and four axis-centre arrays contribute `32S+32S`.  `F` is
nonzero while the frozen directed validator still materializes a subordinate
source file; a new streaming verifier hash does not erase that subordinate
lifetime.  `Dspool` is the largest initial disk payload; the later reveal spool
is only `8N` and does not coexist with the initial spool.

After raw inputs are reconstructed and released, the required child
composition phases are:

```text
point lift:       Knum + 24N + 2C
directed action:  Knum + 40N + max(81C, 2C, 2048, F)
nominal action:   Knum + 48N + 65C
final recheck:    Knum + 48N + max(2C, F, J)
```

The complete child identity also includes phases omitted by a composition-only
ledger:

```text
initial receive/preflight:
    Kraw + 8N + J + W

kernel build/reconstruction, conservatively:
    Kraw + 8N + Knum + G + J + W

output-byte freeze while final arrays may remain live:
    Knum + 56N + max(2C, F, J)

post-release comparison:
    16N + J + W

scalar-only receipt construction:
    J + receipt_serialized_bytes
```

The `56N` freeze phase counts the `48N` final live composition payload plus
the new `8N` immutable computed-output bytes.  It may be lowered only by a
tested earlier release with exact weak-reference/lifetime evidence; it may not
be silently omitted.  Before `COMPUTED_COMMITMENT`, the child converts its
output to exact bytes, freezes all semantic bodies, then releases the kernel
and every numerical array.  The comparison phase therefore has computed and
producer output bytes (`16N`) but no numerical array.  If an implementation
retains an array or kernel, its bytes are added to that phase.

The child deterministic peak is the maximum of every displayed child phase,
not merely the four composition phases.

`Dspool` is a disk/resource cap, not a claim of zero system-memory cost.  The
chosen transport writes chunks into private anonymous temporary files, never
retains a chunk list, and reads each complete kernel section once into the
exact built-in `bytes` required by the packed API.  Consequently the
deterministic Python payload has one `Kraw` raw copy, one owned `8N` input
array, and `W`, as displayed, rather than an unreported second raw
concatenation.  If an implementation instead uses a `bytearray`, `BytesIO`,
`b''.join`, mmap, or another assembly strategy,
its simultaneous assembly/freeze bytes replace these formulas and must be
audited.  Spool allocation, peak disk bytes, cleanup, and page-cache/RSS
observations are separately recorded.

The verified input-nominal spool is decoded through an audited file-to-owned-
array path; the resulting native C-order ndarray must own its storage and have
no base object.  Direct `frombuffer`, an mmap-backed view, or a caller-buffer
view is forbidden.  Kernel raw sections are read once as exact built-in
`bytes` because that is the frozen stage-1 payload boundary.  These different
paths are why `Kraw` and the owned input-array `8N` coexist in the conservative
kernel-build phase without an additional unreported input-raw copy.

### 9.2 Producer adapter and parent launcher

The producer resource ledger covers the existing producer method plus the
adapter.  It records the exact producer method peak, source/hash and canonical
serialization scratch, the `8N` producer output ndarray, the new `8N` immutable
output bytes, complete artifact metadata bytes, and the period in which each
pair coexists.  The adapter cannot claim that a caller-owned producer array has
been freed.

At the launcher wire boundary, let `Mparent` be the exact total retained
canonical metadata bodies and `Bspawn` the bounded small spawn-bootstrap
serialization.  Before reveal the parent retains kernel raw bytes, the input
nominal, and the hidden producer output.  A conservative parent payload is:

```text
parent_base = Kraw + 16N + Mparent
parent_send_phase = parent_base + W
parent_spawn_phase = parent_base + Bspawn
parent_peak = max(parent_send_phase, parent_spawn_phase)
```

The first `8N` is the input nominal and the second is the hidden producer
output.  If the parent also retains an adapter input ndarray or an extra joined
serialization, those bytes are added; they are not covered by `Mparent`.

### 9.3 Aggregate and observed resources

The verifier resource ledger contains separately hashed parent, child, and
aggregate subledgers.  For every protocol phase `t` it records

```text
aggregate_user_payload(t) = parent_live(t) + child_live(t)
aggregate_peak = max_t aggregate_user_payload(t)
```

Per-chunk ACK flow limits user-space frame copies to the exact parent and child
frame allocations already counted (at most `W` in each process).  OS pipe
buffers, allocator arenas, interpreter state, and the runtime's spawn
serialization overhead are not falsely folded into a deterministic byte
identity.  They are separately observed or frozen unknown.

The ledgers record at least:

```text
state_count, axis_size_sum, block_size, block_capacity, block_count
flat_covered_count, input_norm_reduction_count, centre_radius_reduction_count
Kraw, Knum, F, W, J, G, Dspool, Bspawn
every producer-adapter phase
every parent phase
every child phase
every aggregate phase
declared producer, parent, child, and aggregate peaks
all corresponding caps
input/computed/producer immutable byte counts
point-lift, directed, nominal, validation, and workspace byte counts
header, frame, ACK, commitment, receipt, and serialization byte counts
spool declared/observed bytes, section count, close/unlink completion
returned_numeric_payload_bytes = 0
```

Observed fields include parent, child, and aggregate wall time/peak RSS; the
measurement source and units; swap availability/value; pipe-buffer and spawn-
serialization measurement availability/value; and one frozen unknown form.
Any unknown overhead blocks largest-shape resource promotion.  Small-shape RSS
or timing cannot predict acceptance of the `7,165,305`-state target.  That
target remains unallocated and unrun at this stage.

## 10. Fail-closed tests and mutation matrix

Every mutation must return one stable HOLD code, no partial receipt, no live
child, and closed endpoints.

| Surface | Required attacks |
| --- | --- |
| Import boundary | verifier imports producer or adapter directly/indirectly; wire imports a numerical module; producer helper name appears; dynamic import, `exec`, `eval`, `sys.modules`, `pickle`, queue, `fork`, or direct `frombuffer` path; source or AST hash changed |
| Exact wire types | producer dataclass passed to verifier; bytes/tuple subclass; ndarray, ndarray subclass, `memoryview`, `bytearray`, mutable nested container, user buffer, duplicate/unknown JSON key, noncanonical re-encoding |
| Spawn bootstrap | any full payload in `Process.args`; wrong capability type/length; bootstrap shape changed; bootstrap cap one byte low; implicit user-payload pickle; allocation before header preflight |
| Chunk protocol | oversized header/chunk; declared-length overflow; wrong section, sequence, cumulative length, rolling hash, frame HMAC, ACK, or phase; duplicate/missing ACK; second chunk sent before ACK; retained chunk list or `b''.join`; spool cap/length/hash mismatch; spool leak; disconnect, timeout, child crash, wrong PID, orphan or endpoint leak |
| Compute before reveal | artifact body, output bytes, radius, witnesses, trace, or producer resource ledger sent in bootstrap/initial phase; numerical-semantic hash changes when only the hidden artifact digest changes; reveal header sent before valid commitment; output chunk sent before `READY_REVEAL`; child computation changed after commitment |
| Capability/request | one-bit capability change; capability/request/frame swap between concurrent launches; artifact digest swap; stale commitment; request HMAC formed before or without capability |
| State DAG | raw/core/provenance/manifest byte flip; missing full provenance body; current provenance references current full manifest; root/predecessor/current core mismatch; action index skip/reorder/duplicate; radius changed without core change; coherent public rehash marked authoritative |
| Signed zero | point lift retains `-0.0`; nominal output zero is canonicalized instead of bit-preserved; zero policies swapped; output sign bit changed with or without public rehash |
| Eleven witnesses | any of eleven omitted, duplicated, reordered, renamed, sign-changed, non-reduced, wrong numerator/denominator/flat index, or lowered upper hex; three-witness subset accepted |
| Scalar proof | P/Q swap; column norm substituted for maximum absolute row sum; omitted `e` in P; omitted `delta_Q e` in Q; reassociated trace; `m`, `a`, intermediate, or final radius lowered by one ulp; final radius preserved while an intermediate changes |
| Centre binding | nominal output outside directed box; directed hash replacement; point lift, nominal action, and directed action use different contracts, kernels, inputs, block sizes, runtimes, byte orders, or summation orders |
| Ledger separation | shared semantic mismatch; producer/verifier operation models incorrectly required equal; producer resource body relabelled verifier; one resource hash substituted for another; legitimate unequal resource ledgers rejected |
| Resource formulas | `Kraw`, `Knum`, `N`, `S`, `C`, `F`, `W`, `J`, `G`, `Dspool`, or `Bspawn` changed; parent/child/aggregate phase lowered by one byte; output-freeze `8N` omitted; extra assembly/serialization live buffer omitted; pre-reveal ledger replaced after commitment; cap exactly sufficient and one byte insufficient |
| Runtime observations | impossible wall time/RSS/swap; parent/child/aggregate units or sources changed; unavailable metric represented as zero rather than frozen unknown; unknown overhead used to promote largest shape |
| Science boundary | selector, prospective control, positive budget, F1/F2/F3 artifact, production observable, or non-`science_free_*` role supplied; `science_executed` or `f0_pass` changed to true |

Positive tests cover 1D/2D/3D, reflecting/periodic axes including periodic
size two, heterogeneous rate/killing boxes, P and Q, block size one,
nondivisor blocks, block size above `N`, subnormal values, Q-ball crossing zero,
all signed-zero cases, and independent exact-`Fraction` endpoint/ball oracles.
Resource tests recompute every parent, child, and aggregate formula from source
inputs for multiple `(N,S,C)` cases and inspect actual object lifetimes.

Concurrency tests launch at least two distinct requests simultaneously and
prove that capabilities, READY/ACK frames, commitments, reveal chunks, and
receipts cannot cross.  Timeout and injected-crash tests exercise every state
transition and prove zero surviving child processes and closed endpoints.

## 11. Acceptance and stop conditions

The verifier candidate remains rejected if any of the following is absent:

- the three-file wire/adapter/verifier split, frozen hashes, and static import-
  graph/forbidden-AST checks;
- exact built-in-byte wire bodies and raw sections, including the complete
  provenance body and acyclic core/provenance/manifest DAG;
- a small spawn bootstrap followed by cap-first header validation and fixed
  chunk-plus-ACK transport using only `send_bytes`/bounded `recv_bytes`;
- a child commitment before any producer body, output bytes, radius, witness,
  trace, or producer resource ledger is revealed;
- exact signed-zero policies, immutable output bytes, and all eleven ordered
  witnesses in artifact and receipt bindings;
- an exact shared semantic ledger plus distinct producer and verifier resource
  ledgers with separately bound operation models;
- complete producer-adapter, parent, child, aggregate, serialization, IPC,
  RSS, and swap accounting with honest unknowns;
- explicit non-authoritative treatment of a naked prior receipt, artifact, or
  manifest and same-worker/full-chain proof for any authoritative recurrence;
  and
- an independent exact oracle, full mutation/concurrency attack, and fresh
  audit on the exact source hashes.

This note resolves design choices only; it does not claim that any wire,
adapter, verifier, receipt, or resource gate has been implemented or audited.
Even when every one-step method test passes, F0 remains on HOLD until directed
Poisson propagation, weighted accumulation, generator jets, scalar reductions,
neutral largest-shape resource gates, and their own independent attacks are
complete.  Nothing in this design authorizes a scientific computation.
