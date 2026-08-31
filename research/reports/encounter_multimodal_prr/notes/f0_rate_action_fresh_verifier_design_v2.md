# Fresh-process rate-action verifier v2: integrated design after Round 159

Date: 2026-07-15

Status: **LIVING DESIGN ONLY / UNIMPLEMENTED / UNAUDITED / HOLD F0 / NO
SCIENCE AUTHORIZED / NO RESOURCE PROMOTION**

Scope: science-free, one-step verification of one packed point-plus-`l1`-ball
`P.T` or `Q.T` action. This note replaces no immutable audit and does not
modify the v1 design. It records a proposed v2 contract for a future source
candidate.

Nothing in this note authorizes Poisson propagation, generator jets, topology
evaluation, selector execution, a positive budget, F1/F2/F3, a production
allocation, a continuum claim, or a PRR release-gate change.

## 1. Decision and exact boundary

Round 159 accepted the broad wire / producer-adapter / fresh-verifier
direction but found five coupled P1 gaps:

1. the output provenance could not represent its creating transition without
   a cycle or a mismatched request/receipt pair;
2. the first receive cap was learned from the unreceived request;
3. blocking `Connection.send_bytes` could outlive the promised deadline;
4. the resource identities omitted retained metadata, preflight work, and a
   producer-adapter phase algebra; and
5. the verifier import rule was both literally impossible and too weak
   against reflective independence escapes.

The corrections cannot be made independently. In particular, adding a
transition object that binds the old complete request would create a second
cycle because that request binds `artifact_body_sha256` and the artifact
contains output provenance:

~~~text
artifact
  -> launch request
  -> transition
  -> output provenance
  -> artifact
~~~

V2 therefore separates:

- a capability-free and artifact-free numerical request core;
- an acyclic semantic transition core;
- output provenance and manifest bodies;
- a producer artifact;
- a launch/resource envelope constructed after the artifact exists; and
- an external receipt that is never inserted into state lineage.

The process boundary is also split into a pure numerical implementation and an
OS/protocol harness. The proposed implementation has four files:

~~~text
code/rate_defined_tensor_f0_packed_rate_action_wire.py
code/rate_defined_tensor_f0_packed_rate_action_artifact_adapter.py
code/rate_defined_tensor_f0_packed_rate_action_verifier_numeric.py
code/rate_defined_tensor_f0_packed_rate_action_verifier_harness.py
~~~

No such v2 source file is claimed to exist. The filenames are design targets.

The strongest eventual one-step success status remains exactly:

~~~text
PASS_RATE_ACTION_METHOD_ONLY_NOT_F0
~~~

It means separate composition evidence only. It does not mean that the reused
stage-1 or directed numerical implementations were independently
reimplemented, that an input radius is authoritative, that a production
resource gate passed, or that F0 passed.

## 2. Canonical wire rules

Every semantic body is exact built-in ASCII `bytes` produced by one canonical
encoder. The future wire source must freeze:

- exact schema names and versions;
- exact key sets and key ordering;
- `allow_nan=false`;
- one integer grammar and explicit integer ranges;
- one frozen null representation;
- one canonical `float.hex()` representation for every binary64 scalar;
- a SHA-256 of the canonical big-endian eight-byte representation wherever a
  binary64 scalar is semantically bound;
- rejection of NaN, infinity, negative radii, negative-zero radii, duplicate
  keys, unknown keys, non-ASCII input, subclasses, and alternate spellings;
  and
- a distinct domain separator for every body and HMAC.

Large numerical bytes are never embedded in JSON. Each raw section is bound by
an exact name, length, SHA-256, dtype/order declaration, and ordered section
position. A body hash is over the complete canonical body bytes, not a
reconstructed subset.

The receiver exact-type checks every leaf, re-encodes the parsed value, and
requires byte-for-byte identity before using it. Public API tuples are
launcher-side containers only and never enter `Process.args` as payload.

The two zero policies remain separate:

~~~text
CANONICAL_POINT_LIFT_ZERO_TO_POSITIVE_ZERO
PRESERVE_SUBORDINATE_NOMINAL_OUTPUT_BITS
~~~

The first applies only to the constructed point interval. The second preserves
every subordinate nominal output bit, including `-0.0`.

## 3. Acyclic semantic and launch DAG

### 3.1 State core

The state core describes one numerical state and no lineage:

~~~text
schema
role
logical_shape
state_count
raw_byte_length
raw_sha256
dtype_and_order
runtime
nonnegative
nominal_zero_policy
l1_radius_upper_hex
l1_radius_upper_be_sha256
producing_operator_or_frozen_null
producing_composition_contract_sha256_or_frozen_null
~~~

Its hash is:

~~~text
state_core_sha256 =
    H(state_core_domain, state_core_body_bytes)
~~~

A root state uses the frozen null operator/contract representation. An output
state binds the exact operator and composition contract that produced it.

### 3.2 Numerical request core

The numerical request core contains only inputs that may affect numerical
semantics:

~~~text
schema
operator

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
verifier_numeric_source_sha256
verifier_numeric_operation_model_sha256

runtime
byteorder
tensor_shape
state_count
block_size
summation_order
point_lift_zero_policy
nominal_output_zero_policy

ordered_initial_section_names
ordered_initial_section_lengths
ordered_initial_section_sha256
~~~

It must not contain:

- a capability or capability hash;
- a PID, session identifier, socket, deadline, or resource cap;
- an artifact, artifact digest, producer output digest, producer witness, or
  producer resource value;
- producer/adapter source or operation-model hashes;
- an output core, output provenance, output manifest, transition, commitment,
  or receipt; or
- any selector, budget, production observable, continuum, F1, F2, or F3 field.

Its hash is:

~~~text
numerical_request_core_sha256 =
    H(numerical_request_core_domain,
      numerical_request_core_body_bytes)
~~~

Producer and verifier receive the same complete numerical request core. It is
the only request object that a semantic transition may bind.

### 3.3 Transition core

The transition core identifies the action that creates the output core:

~~~text
schema
numerical_request_core_sha256

root_initial_state_core_sha256
input_state_core_sha256
input_provenance_body_sha256
input_state_manifest_sha256

previous_transition_core_sha256_or_root_null
output_state_core_sha256
shared_semantic_ledger_sha256

operator
composition_contract_sha256
from_action_index
to_action_index
~~~

The required index relation is exact:

~~~text
to_action_index == from_action_index + 1
~~~

The transition must not contain the output provenance or manifest hash, an
artifact or launch-envelope hash, a capability, a resource observation, or a
receipt. Its hash is:

~~~text
transition_core_sha256 =
    H(transition_core_domain, transition_core_body_bytes)
~~~

### 3.4 Output provenance

The output provenance body contains:

~~~text
schema
kind = TRANSITION_OUTPUT
lineage_mode
action_index

current_state_core_sha256
root_initial_state_core_sha256
root_initial_nominal_sha256
root_initial_l1_radius_upper_hex

predecessor_state_core_sha256
predecessor_state_manifest_sha256
producing_transition_core_sha256

private_lineage_mac_hex_or_frozen_null
authoritative_input_radius
~~~

For the one-step public route in this design:

~~~text
lineage_mode = PUBLIC_ONE_STEP_NONAUTHORITATIVE
private_lineage_mac_hex_or_frozen_null = null
authoritative_input_radius = false
~~~

The provenance body has no request or receipt field. The transition already
binds the numerical request and input/output cores. No caller may set
`authoritative_input_radius=true`.

### 3.5 Output manifest

The output state manifest is:

~~~text
schema
state_core_sha256
provenance_body_sha256
manifest_binding_domain
~~~

Its hash is over the complete canonical body. It cannot be referenced by the
provenance body that it contains.

### 3.6 Producer artifact

The adapter produces:

~~~text
(artifact_body_bytes, output_nominal_raw_bytes)
~~~

The canonical artifact body contains, at minimum:

~~~text
schema
status = PRODUCER_RATE_ACTION_METHOD_ARTIFACT_NOT_AUTHORITY
producer_pid
producer_runtime
operator

numerical_request_core_body
numerical_request_core_sha256

wire_source_sha256
adapter_source_sha256
producer_composition_source_sha256
producer_operation_model_sha256

kernel and contract bindings
input core, provenance, manifest, nominal and radius bindings

point_lift and directed-output bindings
shared_semantic_ledger_body
shared_semantic_ledger_sha256
producer_resource_ledger_body
producer_resource_ledger_sha256

output_state_core_body
output_state_core_sha256
transition_core_body
transition_core_sha256
output_provenance_body
output_provenance_body_sha256
output_state_manifest_body
output_state_manifest_sha256

output_nominal_sha256
output_nominal_byte_length
output_l1_radius_upper_hex
output_l1_radius_upper_be_sha256
output_nominal_zero_policy

artifact_arrays_exposed = false
artifact_contains_immutable_numeric_bytes = true
science_executed = false
f0_pass = false
~~~

Nested semantic objects are canonical subobjects, not caller-chosen encoded
strings. The raw output is not duplicated inside the artifact body.

The artifact contains no capability, launch-envelope hash, verifier PID,
commitment, receipt, or post-launch observation.

### 3.7 Launch envelope

The launch envelope is nonsemantic session/resource control. It is constructed
after the artifact digest and capability exist:

~~~text
schema
launch_parent_pid
spawn_start_method = spawn
launch_capability_sha256

numerical_request_core_sha256
artifact_body_sha256
artifact_body_byte_length
producer_output_sha256
producer_output_byte_length

wire_policy_sha256
import_policy_sha256
wire_source_sha256
adapter_source_sha256
producer_composition_source_sha256
producer_operation_model_sha256
verifier_numeric_source_sha256
verifier_numeric_operation_model_sha256
verifier_harness_source_sha256

ordered_initial_section_lengths
ordered_reveal_section_lengths
declared_chunk_body_max
declared_private_spool_max
declared_logical_child_payload_max
declared_logical_parent_payload_max
declared_logical_aggregate_payload_max
declared_disk_payload_max

launch_created_monotonic_ns
absolute_deadline_monotonic_ns
cleanup_grace_ns
runtime
byteorder
~~~

Every declared wire size is bounded by a verifier-source-frozen hard maximum.
The absolute deadline must be later than creation and no later than the frozen
maximum session duration.

The launch-envelope hash is:

~~~text
launch_envelope_sha256 =
    H(launch_envelope_domain, launch_envelope_body_bytes)
~~~

The request HMAC is:

~~~text
request_capability_hmac =
    HMAC-SHA256(
        capability,
        request_hmac_domain
        || launch_envelope_sha256
        || numerical_request_core_sha256
        || artifact_body_sha256
    )
~~~

The first request frame contains the complete canonical numerical request core,
complete launch envelope, and request HMAC. It contains no large raw section
and no artifact or producer output body.

### 3.8 Commitment and receipt

Before any producer body is revealed, the verifier child freezes a commitment
containing:

~~~text
schema
verifier_pid
launch_capability_sha256
launch_envelope_sha256
numerical_request_core_sha256

verifier_numeric_semantic_sha256
verifier_computation_sha256
computed_output_nominal_sha256
computed_output_state_core_sha256
computed_transition_core_sha256
computed_output_provenance_body_sha256
computed_output_state_manifest_sha256
verifier_pre_reveal_resource_ledger_sha256
~~~

The numerical-semantic hash depends only on reconstructed numerical arguments,
the verifier-local contracts, and the computed result. The outer computation
hash additionally binds the launch envelope and pre-reveal resource ledger.

The final external receipt binds:

- numerical request and launch envelope;
- capability digest and actual parent/child PIDs;
- verifier commitment;
- producer artifact;
- computed and producer transition/output state objects;
- exact semantic comparison and radius-containment result;
- producer, verifier, parent, child and aggregate resource ledgers; and
- cleanup and child-exit observations.

No state core, provenance, manifest, transition, numerical request, or artifact
references the receipt.

### 3.9 Complete construction order

The only allowed object construction order is:

~~~text
1.  root/input nominal bytes
2.  input state core
3.  input provenance
4.  input state manifest
5.  numerical request core
6.  producer output core and shared semantic ledger
7.  producer transition core
8.  producer output provenance
9.  producer output manifest
10. producer artifact body and raw output
11. fresh launch capability
12. launch envelope and request HMAC
13. spawn bootstrap
14. verifier reconstruction and independent numerical result
15. verifier output core and shared semantic ledger
16. verifier transition core
17. verifier output provenance
18. verifier output manifest
19. verifier pre-reveal resource ledger
20. verifier commitment
21. producer artifact reveal
22. producer raw output reveal
23. post-reveal resource ledger
24. external receipt
25. child join and cleanup confirmation
~~~

The capability may be generated earlier, but it cannot enter objects 1--10.
The receipt is always last and never feeds back into lineage.

## 4. Source-frozen first-frame and wire caps

The future wire source must define exact hard constants. This design selects:

~~~text
FIRST_REQUEST_BODY_HARD_MAX = 65_536
CONTROL_BODY_HARD_MAX = 65_536
DATA_CHUNK_BODY_HARD_MAX = 1_048_576
CAPABILITY_BYTES = 32
SHA256_BYTES = 32
HMAC_BYTES = 32
FRAME_HEADER_BYTES = FRAME_HEADER_STRUCT.size
~~~

The concrete `FRAME_HEADER_STRUCT` format remains source work, but its fields
are frozen conceptually:

~~~text
magic
wire_version
message_type
section_identifier
flags
sequence_number
declared_section_total
cumulative_before
cumulative_after
payload_length
payload_sha256
launch_envelope_sha256
frame_hmac
~~~

Every integer has an exact unsigned width. Every enum has a closed numeric
range. No variable-length header is permitted.

Before the first receive, the child already knows
`FRAME_HEADER_BYTES` and `FIRST_REQUEST_BODY_HARD_MAX` from its imported,
source-hashed wire module. It:

1. reads exactly the fixed header into a fixed-size buffer;
2. rejects wrong magic, version, phase, enum, arithmetic, or body length;
3. rejects a first body larger than `FIRST_REQUEST_BODY_HARD_MAX` without
   allocating that body;
4. allocates exactly the accepted body length;
5. reads it under the absolute deadline;
6. verifies its SHA-256 and capability HMAC;
7. canonical-parses the numerical request and launch envelope; and
8. checks every later size/resource declaration before accepting a large
   section.

The request does not choose the first-frame maximum. A declared chunk body cap
must satisfy:

~~~text
0 < declared_chunk_body_max <= DATA_CHUNK_BODY_HARD_MAX
~~~

The effective data-body cap is the declared value. The complete live transport
payload includes the fixed header as well as the body.

The logical spawn bootstrap has exactly:

~~~text
exact parent PID integer
exact 32-byte capability
one AF_UNIX socket endpoint
~~~

No request, contract, kernel, state, artifact, output, witness, ledger, radius,
or full-size buffer may enter `Process.args`.

Only that logical bootstrap shape is enforceable. Python/macOS spawn reduction,
descriptor transfer, interpreter startup and unavoidable internal
serialization are physical runtime observations. They are not a deterministic
payload identity unless a future audited runtime-specific mechanism proves
otherwise.

## 5. Nonblocking macOS transport and deadline

### 5.1 Transport primitive

V2 replaces both blocking `multiprocessing.Connection` pipes with one
full-duplex:

~~~text
socket.socketpair(AF_UNIX, SOCK_STREAM)
~~~

Both endpoints are put into nonblocking mode before `Process.start()`. The
child verifies that its endpoint is nonblocking. Parent and child use
`selectors.DefaultSelector`; on the target macOS runtime this is expected to
resolve to kqueue, but the actual selector class is recorded.

No correctness or deadline argument relies on `SO_SNDBUF`, `SO_RCVBUF`, pipe
capacity, or the assumption that one frame fits in a kernel buffer.

### 5.2 Framed send and receive

The only permitted transport operations are audited loops equivalent to:

~~~text
send_frame_until_deadline(socket, header, body, absolute_deadline_ns)
recv_frame_until_deadline(socket, hard_body_cap, absolute_deadline_ns)
~~~

The send loop:

- retains separate header and body buffers; it does not join them;
- calls nonblocking `socket.send` with the unsent suffix;
- advances only by the returned byte count;
- handles `BlockingIOError` and `InterruptedError`;
- waits for write readiness only until the remaining absolute deadline; and
- rechecks `time.monotonic_ns()` before and after every wait and syscall.

The receive loop:

- receives the fixed header first;
- validates the length against its source-frozen phase cap;
- allocates only the exact accepted body length;
- uses `recv_into` or an equivalently audited exact buffer;
- handles partial reads, EOF, interruption and readiness; and
- rechecks the same absolute deadline.

The HMAC is over a frozen domain, every header field except the HMAC field, and
the exact payload bytes. Authentication occurs after the bounded body is
received; length validation occurs before body allocation.

### 5.3 Chunk discipline

At most one data chunk is outstanding in either direction. Each ACK binds:

~~~text
phase
section_identifier
sequence_number
cumulative_length
rolling_sha256
launch_envelope_sha256
capability-keyed HMAC
~~~

A second chunk before the exact ACK is a protocol failure. A section completes
only after its declared total length and rolling hash agree. No chunk list,
growing `bytes` concatenation, `BytesIO` accumulation, or `b''.join` is
allowed.

Internal transport may use a short-lived `memoryview` of immutable bytes to
avoid a copy. This permission is confined to the harness and does not permit a
buffer-backed numerical array.

### 5.4 State machine

The exact protocol order is:

~~~text
PRELAUNCH
BOOTSTRAP
REQUEST_V2
READY_INITIAL
INITIAL_SECTIONS
INPUT_COMPLETE
COMPUTE
COMPUTED_COMMITMENT
READY_ARTIFACT_REVEAL
ARTIFACT_BODY_SECTIONS
ARTIFACT_ACCEPTED_READY_OUTPUT
PRODUCER_OUTPUT_SECTIONS
RECEIPT
JOIN
CLEANUP_CONFIRMED
~~~

`REQUEST_V2` is the first bounded control frame. It contains the numerical
request core, launch envelope and request HMAC.

Initial sections contain only kernel, input-state and composition-contract
data. The artifact body, producer output, producer radius, producer witnesses,
producer trace and producer resource ledger are forbidden before a valid
`COMPUTED_COMMITMENT`.

After the commitment:

1. the child emits `READY_ARTIFACT_REVEAL`;
2. the parent streams and the child validates the artifact body;
3. the child emits `ARTIFACT_ACCEPTED_READY_OUTPUT`; and
4. only then does the parent stream producer output bytes.

Thus even a large artifact body is data-framed and does not enlarge the
control-frame cap.

### 5.5 Parent supervision and cleanup

The parent selector supervises both the socket and `Process.sentinel`. The one
absolute monotonic deadline covers request transfer, input transfer,
computation, commitment, reveal, receipt and normal join.

On timeout, disconnect, wrong phase, malformed frame, child crash, nonzero
exit, or any other failure, the parent performs:

~~~text
1. close the parent socket endpoint
2. request Process.terminate()
3. join for the frozen cleanup grace
4. if still alive, request Process.kill()
5. join for the frozen cleanup grace
6. verify exitcode is available and Process.is_alive() is false
7. close all local descriptors
8. close and unlink every private spool
9. remove the private run directory
~~~

A normal HOLD may be returned only after steps 1--9 are confirmed. If child
death or cleanup cannot be confirmed, no receipt or ordinary HOLD is returned;
the harness raises the exact fatal condition:

~~~text
FATAL_RATE_ACTION_V2_CLEANUP_UNCONFIRMED
~~~

This design bounds verifier-owned socket waits and provides kill escalation.
It is not a hard-real-time claim. Scheduler suspension, signal-delivery
latency, kernel reaping latency and catastrophic OS failure remain observed
runtime behaviour.

## 6. Independent numerical boundary

The numerical entry point is a top-level function in
`..._verifier_numeric.py`. Its exact future signature must contain only:

~~~text
reconstructed verifier-owned kernel
reconstructed verifier-owned input state
verifier-local numerical composition contract
~~~

It receives no launch envelope, capability, artifact digest, producer source
hash, producer operation model, deadline, resource cap, socket, file path,
protocol object, callback, logger, or caller-owned object.

The harness imports the numerical module and invokes the entry point only after
full input reconstruction. It does not pass a closure. Required runtime checks
include:

~~~text
entry.__code__.co_freevars == ()
entry.__closure__ is None
~~~

Allowed module globals are limited to:

- exact allowlisted imported numerical symbols;
- immutable literal constants;
- verifier-local frozen schema classes; and
- source-hashed local helper functions.

No request-specific, session-specific, artifact-specific or mutable global is
allowed.

The numerical implementation independently performs the composition layer:

- blockwise point lifting and point-lift signed-zero canonicalization;
- increasing-flat-index reductions for `m` and `a`;
- exact `Fraction` traces and least binary64 upper conversion;
- verifier-local `add_up` and `mul_up`;
- frozen P and Q scalar formula traces;
- output state, transition, provenance and manifest construction; and
- exact radius-containment proof.

The only permitted subordinate project calls are:

~~~text
packed.build_packed_tensor_kernel
packed.block_p_transpose
packed.block_q_transpose
directed.directed_p_transpose
directed.directed_q_transpose
~~~

This supports only:

~~~text
separate_composition_implementation = true
subordinate_stage1_implementation_reused = true
subordinate_directed_implementation_reused = true
~~~

It does not support a claim that the subordinate numerical methods were
independently reimplemented.

## 7. Four-file import and AST policy

### 7.1 Direct project-import roots

The direct project-import roots are:

| File | Allowed project imports |
| --- | --- |
| wire | none |
| artifact adapter | wire; producer composition |
| verifier numeric | frozen stage-1 packed; repaired directed action |
| verifier harness | wire; verifier numeric |

The complete transitive project import graph must be generated and frozen. No
transitive path from the harness or numeric module may reach the producer
composition or artifact adapter.

### 7.2 Direct external imports

The direct external allowlist is:

| File | Allowed direct external modules |
| --- | --- |
| wire | `hashlib`, `hmac`, `json`, `struct` |
| artifact adapter | `hashlib`, `math`, `numpy`, `os`, `resource`, `struct`, `time` |
| verifier numeric | `fractions`, `hashlib`, `math`, `numpy`, `struct` |
| verifier harness | `hashlib`, `hmac`, `multiprocessing`, `os`, `resource`, `selectors`, `socket`, `struct`, `sys`, `tempfile`, `time` |

If implementation requires another direct import, this living design and the
policy hash must be revised and independently attacked before source freeze.
Accessing `packed.np`, `packed.Fraction`, or another subordinate module global
to evade this allowlist is forbidden.

The exact runtime, NumPy build and external transitive module/file manifest
must also be recorded. A clean import test freezes module names, origins and
available file hashes. During compute, the harness rejects new imports outside
the frozen runtime manifest.

### 7.3 Numeric-module forbidden surface

The numerical module and its local helper call graph forbid:

~~~text
__import__
importlib
runpy
subprocess
ctypes
cffi
marshal
pickle
dill
cloudpickle
inspect
traceback
gc
types
pathlib
tempfile
socket
multiprocessing
resource

open
input
breakpoint
exec
eval
compile
globals
locals
vars
getattr
setattr
delattr

sys.modules
sys._getframe
currentframe
f_locals
f_globals
f_back
__globals__
__closure__
__code__
__dict__
__loader__
__spec__
__file__
__subclasses__
__mro__

os.system
os.popen
os.exec*
os.spawn*
~~~

Every dunder attribute access is forbidden unless an exact source-audit
exception is added for a nonreflective language operation. No wildcard
exception is permitted.

The NumPy attribute policy is allowlist-based, not blacklist-only. The future
source must freeze the exact small set it uses. Candidate permitted numerical
operations include owned-array construction, `empty`, `zeros`, `array`,
`isfinite`, `nextafter`, `float64` and `uint64`.

Array attributes are limited to exact structural operations required by the
operation model, such as `shape`, `dtype`, `flags`, `nbytes`, `base`, `copy`,
`reshape`, `ravel`, `setflags` and `tobytes`. A raw input
`frombuffer`/mmap/caller-buffer view is forbidden.

### 7.4 What the policy establishes

Source parsing, import-graph checks, exact call/attribute allowlists, source
hashes, closure checks and runtime import denial establish an auditable code
boundary.

They do not prove:

- mathematical correctness;
- a hostile-Python sandbox;
- absence of every covert or reflective channel;
- native-extension noninterference; or
- independence of reused subordinate operations.

Independent exact oracles, mutation tests and adversarial source review remain
mandatory.

## 8. Phase-indexed logical resource ledger

### 8.1 Two different resource claims

V2 separates:

1. **declared logical payload upper bytes**, derived from named objects and
   checked before verifier-owned allocations; and
2. **observed physical resources**, including RSS, allocator/native overhead,
   kernel buffers, page cache, swap, wall time and cleanup latency.

The first is enforceable under the frozen operation model. The second is
measurement evidence. The design must never relabel the first as resident
memory.

### 8.2 Base numerical symbols

Retain the independently accepted numerical identities:

~~~text
N = product(tensor_shape)
S = sum(tensor_shape)
C = min(N, block_size)

Kraw = 16N + 32S
Knum = 40N + 64S

F_preflight = largest full source-read payload during request preflight
F_action = largest full source-read payload during numerical action/recheck
F_producer = largest full source-read payload during producer/adapter work
Rprobe = 2048
G = kernel-builder working-payload upper bound

Wbody = effective declared chunk-body maximum
Wframe = FRAME_HEADER_BYTES + Wbody
Dspool_initial = Kraw + 8N
Dspool_reveal = artifact_body_byte_length + 8N
~~~

Disk spools and RAM payload are separate ledgers. A disk spool is not zero
physical memory because page-cache effects remain observed.

### 8.3 Named live objects

Every future operation model must define a closed ordered table:

~~~text
object_id
owner
storage_class
exact_logical_size_expression
creation_event
last_use_event
release_event
backing_object_id_or_none
~~~

Storage classes include:

~~~text
NUMERIC_OWNED_RAM
IMMUTABLE_BYTES_RAM
CANONICAL_BODY_RAM
DIGEST_BUFFER_RAM
ENCODER_BUFFER_RAM
TRANSPORT_BUFFER_RAM
DISK_SPOOL
OBSERVED_ONLY
~~~

Aliases to the same backing object count once. Copies count separately. A
view is not accepted as owned numerical storage. Every retained canonical body
is a separate named object; it cannot disappear into a generic scratch maximum.

For phase `p`:

~~~text
logical_live_bytes(p) =
    sum(exact size of every distinct RAM payload object live in p)

disk_live_bytes(p) =
    sum(exact logical file size of every live spool in p)
~~~

A `max(...)` is allowed only when source control flow and lifetime tests prove
the candidates cannot coexist. Otherwise their sizes are summed in the
preallocation upper bound.

### 8.4 Retained metadata and encoders

Delete the v1 scalar `J`. Replace it by phase-specific exact sums:

~~~text
M_request(p)
M_input(p)
M_computed(p)
M_artifact(p)
M_resource(p)
M_receipt(p)
E_encoder(p)
H_digest(p)
TX_frame(p)
RX_frame(p)
~~~

`M_computed` includes, when live:

- output state core;
- transition core;
- output provenance;
- output manifest;
- eleven-witness shared semantic ledger;
- pre-reveal resource ledger;
- commitment body; and
- each separately retained digest body or byte buffer.

`M_artifact` includes the complete producer artifact body and any separately
retained canonical nested body. `E_encoder` includes old and new serialization
buffers that coexist. If canonical serialization creates an ASCII string and
then a bytes copy, both logical lengths are counted during that phase.

Python object headers, Unicode representation overhead and native hash context
storage are not assigned invented exact sizes; they remain physical
observations.

### 8.5 Child phase upper bounds

The future source must instantiate the following phase table. Metadata symbols
mean the exact named-object sum for that phase, not a global maximum.

~~~text
child_bootstrap:
    M_request(bootstrap)
    + socket/header bootstrap buffers

child_request_preflight:
    M_request(preflight)
    + RX_frame(preflight)
    + F_preflight
    + Rprobe

child_initial_spooling:
    M_request(initial)
    + M_input(initial)
    + RX_frame(initial)
    disk <= Dspool_initial

child_kernel_reconstruction:
    M_request(reconstruct)
    + M_input(reconstruct)
    + Kraw
    + 8N
    + Knum
    + G
    + applicable source/probe payload
    + TX_frame(reconstruct)
    + RX_frame(reconstruct)

child_point_lift:
    M_request(point_lift)
    + M_input(point_lift)
    + Knum
    + 24N
    + 2C
    + phase transport/encoder buffers

child_directed_action:
    M_request(directed)
    + M_input(directed)
    + Knum
    + 40N
    + max(81C, 2C, Rprobe, F_action)
    + phase transport/encoder buffers

child_nominal_action:
    M_request(nominal)
    + M_input(nominal)
    + Knum
    + 48N
    + 65C
    + phase transport/encoder buffers

child_final_recheck:
    M_request(recheck)
    + M_input(recheck)
    + Knum
    + 48N
    + max(2C, F_action)
    + M_computed(recheck)
    + E_encoder(recheck)
    + phase transport buffers

child_output_freeze:
    M_request(freeze)
    + Knum
    + 56N
    + applicable max(2C, F_action)
    + M_computed(freeze)
    + M_resource(freeze)
    + E_encoder(freeze)
    + TX_frame(freeze)

child_artifact_reveal:
    8N
    + M_request(reveal)
    + M_computed(reveal)
    + M_artifact(reveal)
    + M_resource(reveal)
    + E_encoder(reveal)
    + RX_frame(reveal)
    disk <= Dspool_reveal

child_output_comparison:
    16N
    + M_request(compare)
    + M_computed(compare)
    + M_artifact(compare)
    + M_resource(compare)
    + comparison scratch
    + RX_frame(compare)

child_receipt:
    M_request(receipt)
    + M_computed(receipt)
    + M_artifact(receipt)
    + M_resource(receipt)
    + M_receipt(receipt)
    + E_encoder(receipt)
    + TX_frame(receipt)
~~~

The `56N` freeze term retains the existing `48N` final numerical payload plus
the new immutable computed-output `8N`. The comparison term includes both
computed and producer output bytes.

If the implementation releases artifact bodies, output bytes, kernels, or
arrays before receipt construction, the exact release event must be frozen and
tested. Until then, the conservative terms remain.

The child logical peak is the maximum of every instantiated phase. A one-byte
smaller declared cap must be rejected during request preflight, before the
corresponding allocation.

### 8.6 Producer-adapter phases

Let `P_live(p)` be the exact named producer-method payload still live during
adapter phase `p`. The adapter cannot claim caller-owned producer state was
freed.

The producer ledger must instantiate:

~~~text
producer_source_validation:
    P_live(validate)
    + F_producer
    + exact validation metadata/encoder buffers

producer_output_copy:
    P_live(copy)
    + immutable_output_bytes(8N)
    + exact hash/copy buffers

producer_nested_body_freeze:
    P_live(nested)
    + immutable_output_bytes(8N)
    + all separately retained nested canonical bodies
    + their digest buffers

producer_outer_artifact_encode:
    P_live(encode)
    + immutable_output_bytes(8N)
    + retained nested bodies
    + old/new outer serialization buffers
    + complete artifact body when created

producer_adapter_return:
    P_live(return)
    + immutable_output_bytes(8N)
    + complete artifact body
    + any nested body not explicitly released
~~~

If `P_live(return)` remains in the same process during verifier launch, it is
also a parent live object and is counted in every overlapping parent and
aggregate phase.

### 8.7 Parent and aggregate phases

At minimum, the parent retains:

~~~text
Kraw
input nominal bytes = 8N
hidden producer output bytes = 8N
complete retained canonical request/artifact metadata
any caller-owned producer state still live
one transmit or receive frame buffer where applicable
the logical small spawn-bootstrap objects
~~~

Define:

~~~text
parent_live(p) =
    exact sum of named parent RAM payload objects live in p

child_live(p) =
    exact sum of named child RAM payload objects live in p

aggregate_logical_live(p) =
    parent_live(p) + child_live(p)

aggregate_logical_peak =
    max over protocol phases p of aggregate_logical_live(p)
~~~

The sender and receiver may each hold one frame at the same time. Aggregate
accounting therefore includes both, rather than one global `Wframe`.

The logical bootstrap object sizes are recorded. The internal
multiprocessing/socket reducer allocation is observed or unknown, not inserted
as a fictitious deterministic constant.

### 8.8 Enforceable versus observed

| Surface | Enforceable by v2 source/protocol | Observed or unknown |
| --- | --- | --- |
| Raw/canonical bytes | exact lengths, hashes, caps, ownership | Python object headers |
| NumPy arrays | dtype/order, ownership, `nbytes`, no base | allocator padding, native temporaries |
| Phase model | named logical objects and preallocation upper bounds | physical deallocation timing |
| Transport | hard frame/chunk sizes, one outstanding chunk | kernel socket-buffer occupancy |
| Spools | bytes written, `fstat` size, close/unlink | page-cache residence |
| Spawn | exact logical argument shape | reducer/pickle/interpreter overhead |
| Deadline | no verifier-owned blocking socket call; kill escalation | scheduling and signal latency |
| Memory | logical payload cap | RSS, arenas, fragmentation |
| Swap | no semantic dependence | availability and system-wide value |
| Cleanup | calls and postcondition checks | catastrophic OS failure |

The receipt must name every observation source and unit. Unavailable values use
one frozen unknown form, never zero.

For macOS resource qualification, parent and child should be fresh processes so
`resource.getrusage` high-water marks are run-local. The platform, Python
runtime, selector class and `ru_maxrss` unit must be recorded. Summing
separately observed parent and child high-water marks is a conservative bound,
not an exact simultaneous aggregate RSS measurement.

No Python-only v2 statement claims a hard physical-memory limit on macOS.
Unknown allocator, spawn, page-cache, or aggregate-RSS overhead blocks
production resource promotion.

## 9. Exact fail-closed statuses

### 9.1 Success and fatal condition

The only success status is:

~~~text
PASS_RATE_ACTION_METHOD_ONLY_NOT_F0
~~~

The only non-HOLD fatal harness condition is:

~~~text
FATAL_RATE_ACTION_V2_CLEANUP_UNCONFIRMED
~~~

The fatal condition carries no receipt and cannot be converted into PASS by a
caller.

### 9.2 Ordered HOLD enum

The future wire source must freeze this ordered enum exactly:

~~~text
HOLD_RATE_ACTION_V2_API_TYPE
HOLD_RATE_ACTION_V2_SCIENCE_BOUNDARY
HOLD_RATE_ACTION_V2_IMPORT_POLICY
HOLD_RATE_ACTION_V2_SOURCE_BINDING
HOLD_RATE_ACTION_V2_WIRE_POLICY
HOLD_RATE_ACTION_V2_NUMERICAL_REQUEST
HOLD_RATE_ACTION_V2_STATE_DAG
HOLD_RATE_ACTION_V2_RESOURCE_PLAN
HOLD_RATE_ACTION_V2_BOOTSTRAP
HOLD_RATE_ACTION_V2_FIRST_FRAME
HOLD_RATE_ACTION_V2_CAPABILITY
HOLD_RATE_ACTION_V2_FRAME
HOLD_RATE_ACTION_V2_PHASE
HOLD_RATE_ACTION_V2_TIMEOUT
HOLD_RATE_ACTION_V2_DISCONNECT
HOLD_RATE_ACTION_V2_SPOOL
HOLD_RATE_ACTION_V2_INPUT_RECONSTRUCTION
HOLD_RATE_ACTION_V2_COMPUTE_BOUNDARY
HOLD_RATE_ACTION_V2_NUMERICAL
HOLD_RATE_ACTION_V2_COMMITMENT
HOLD_RATE_ACTION_V2_REVEAL
HOLD_RATE_ACTION_V2_ARTIFACT
HOLD_RATE_ACTION_V2_OUTPUT_MISMATCH
HOLD_RATE_ACTION_V2_SEMANTIC_MISMATCH
HOLD_RATE_ACTION_V2_RADIUS_PROOF
HOLD_RATE_ACTION_V2_RESOURCE_OBSERVATION
HOLD_RATE_ACTION_V2_RECEIPT
HOLD_RATE_ACTION_V2_CHILD_EXIT
HOLD_RATE_ACTION_V2_CLEANUP
~~~

### 9.3 Status meanings

| Status | Exact class of failure |
| --- | --- |
| `...API_TYPE` | public input is not an exact permitted built-in tuple/bytes leaf or contains a mutable/view/subclass payload |
| `...SCIENCE_BOUNDARY` | selector, budget, Poisson, generator, topology, continuum, production, F1/F2/F3 or non-science-free role supplied |
| `...IMPORT_POLICY` | direct/transitive import, AST, call, attribute, closure, global or runtime-module policy fails |
| `...SOURCE_BINDING` | required source, operation-model, runtime or dependency hash differs |
| `...WIRE_POLICY` | hard constant, schema, canonical encoder, integer range, first-frame policy or section manifest fails |
| `...NUMERICAL_REQUEST` | numerical request core is malformed, noncanonical, inconsistent or contains forbidden launch/producer/output data |
| `...STATE_DAG` | core/transition/provenance/manifest edge, action index, root, predecessor or acyclicity check fails |
| `...RESOURCE_PLAN` | phase formula, object table, declared cap, disk cap or checked arithmetic fails before allocation |
| `...BOOTSTRAP` | spawn method, PID, capability type/length, socket endpoint or exact bootstrap shape fails |
| `...FIRST_FRAME` | first fixed header/body is oversized, truncated, malformed or not `REQUEST_V2` |
| `...CAPABILITY` | request/frame HMAC, capability digest or cross-session binding fails |
| `...FRAME` | later frame header, length, sequence, hash, ACK, enum or cumulative count fails |
| `...PHASE` | valid frame appears in the wrong protocol state, including early reveal |
| `...TIMEOUT` | the absolute monotonic deadline expires |
| `...DISCONNECT` | unexpected EOF, broken socket, child sentinel, or peer disappearance occurs |
| `...SPOOL` | private spool create/write/hash/size/read/close/unlink policy fails |
| `...INPUT_RECONSTRUCTION` | kernel/state/contract reconstruction, ownership, source rehash or exact-type check fails |
| `...COMPUTE_BOUNDARY` | numerical function receives or accesses a forbidden nonnumerical input, or excluded-field invariance fails |
| `...NUMERICAL` | independent composition execution, scalar trace or subordinate numerical call fails |
| `...COMMITMENT` | pre-reveal freeze, commitment schema/hash/PID or committed resource ledger fails |
| `...REVEAL` | artifact/output reveal length, order, digest or readiness handshake fails |
| `...ARTIFACT` | producer artifact canonical schema, source/model binding, transition or resource body fails |
| `...OUTPUT_MISMATCH` | output length, immutable bytes, signed-zero bits, core, provenance or manifest differ |
| `...SEMANTIC_MISMATCH` | shared ledger, eleven witnesses, trace, contract or centre binding differs |
| `...RADIUS_PROOF` | exact rational containment or least-upper-binary64 proof fails |
| `...RESOURCE_OBSERVATION` | observation schema/unit/source impossible, unavailable-as-zero, or unknown used for promotion |
| `...RECEIPT` | scalar-only receipt schema, hash chain, flags or returned-payload condition fails |
| `...CHILD_EXIT` | nonzero or missing child exit after an otherwise complete protocol |
| `...CLEANUP` | cleanup initially fails but succeeds within required escalation/grace; run remains HOLD |

Within one parsed object, the earliest entry in the ordered HOLD enum is the
primary reason. Across time, the first detected protocol failure is primary.
A child may attempt one small authenticated HOLD frame, but the parent
independently validates and maps the failure. HOLD detail never contains the
capability, raw numerical bytes, private paths, mutable objects, exception
reprs, or unbounded text.

No partial receipt is returned with a HOLD.

## 10. Required positive tests

Before any source candidate can be accepted, positive tests must cover:

- one-dimensional, two-dimensional and three-dimensional tensors;
- reflecting and periodic axes, including periodic size two;
- P and Q actions;
- block size one, a nondivisor block, and block size above `N`;
- subnormal inputs and outputs;
- Q balls crossing zero;
- source `-0.0`, canonical point-lift `+0.0`, and preserved nominal output
  signed zero as distinct cases;
- all eleven exact witnesses in frozen order;
- independent exact-`Fraction` endpoint and ball oracles;
- root action index zero and at least a two-transition full-chain structural
  replay test, without promoting public authority;
- first body exactly at the accepted canonical size and a much smaller normal
  body;
- control and data bodies at their effective caps;
- short writes and reads at every possible frame boundary;
- concurrent distinct sessions with noncrossing capabilities;
- every child/resource phase with an exactly sufficient logical cap;
- a producer adapter in which caller-owned producer state remains live and is
  counted; and
- successful normal join, endpoint close and spool removal.

Passing these tests would validate a candidate implementation, not F0.

## 11. Required mutation and adversarial tests

Every mutation returns its exact HOLD status only after confirmed cleanup,
unless cleanup itself escalates to the fatal condition.

### 11.1 DAG and request separation

Required attacks include:

- transition binds the full launch envelope rather than numerical request core;
- numerical request contains artifact digest, capability, PID, deadline,
  resource cap, producer output, or receipt;
- artifact contains launch envelope, capability or receipt;
- output provenance references current receipt, output manifest or full launch
  request;
- launch envelope omitted or changed artifact digest;
- transition uses input's old request/receipt pair;
- output provenance copied from input with only current-core replacement;
- predecessor transition skipped, duplicated, reordered or changed;
- `to_action_index` not exactly one above `from_action_index`;
- root/current/predecessor core, manifest, nominal or radius mismatch;
- transition semantic-ledger hash changed;
- coherent public rehash presented as authoritative;
- caller sets authoritative input radius or private MAC; and
- receipt inserted into any semantic object.

Expected primary status is `HOLD_RATE_ACTION_V2_NUMERICAL_REQUEST` or
`HOLD_RATE_ACTION_V2_STATE_DAG` according to the first invalid object.

### 11.2 First-frame and framing

Required attacks include:

- first body length 65,537;
- request-declared cap used before the fixed header is read;
- wrong fixed-header size, magic, version or first phase;
- truncated first header/body;
- body length overflow, negative emulation or width overflow;
- declared chunk cap zero or above 1,048,576;
- control body above 65,536;
- wrong section identifier, sequence, cumulative length or total;
- duplicate, missing, stale or cross-session ACK;
- second chunk sent before ACK;
- payload or rolling hash changed;
- capability/frame HMAC bit flip; and
- concurrent frames swapped between two launches.

### 11.3 Deadline and cleanup

Inject a stall or crash at every state transition and at every partial
header/body offset. Required attacks include:

- parent stalls reading a child send;
- child stalls reading a parent send;
- peer stops after a partial fixed header;
- peer stops after a partial body;
- computation exceeds deadline;
- selector returns readiness but syscall yields `EAGAIN`;
- interrupted syscall;
- disconnect, broken pipe and child nonzero exit;
- terminate succeeds;
- terminate fails and kill succeeds;
- first spool close/unlink attempt fails and retry succeeds; and
- cleanup cannot confirm child death, producing the fatal condition and no
  HOLD/receipt.

Tests must show that no verifier-owned blocking `send_bytes`/`recv_bytes` path
exists.

### 11.4 Resource algebra

Required attacks include:

- omit one retained core, transition, provenance, manifest, semantic ledger,
  resource ledger or commitment body;
- replace a sum by `max` for objects that coexist;
- omit old/new serialization coexistence;
- omit `F_preflight` or `Rprobe` from header preflight;
- omit the computed-output `8N` from freeze;
- omit either output `8N` from comparison;
- omit sender or receiver frame from aggregate;
- omit caller-owned producer state after adapter return;
- omit artifact nested bodies or adapter result;
- relabel disk spool bytes as zero RAM/page-cache cost;
- count the same copy as an alias or the same alias as two copies;
- phase cap exactly sufficient and one byte insufficient;
- spool disk cap exactly sufficient and one byte insufficient;
- unknown spawn/RSS/swap value represented as zero;
- parent lifetime high-water presented as run-local without a fresh process;
  and
- unknown physical overhead used to promote the largest shape.

One-byte-insufficient tests exercise the preallocation formula gate. They do
not claim the OS would physically fail at that byte.

### 11.5 Import, AST and compute boundary

Required attacks include:

- direct or transitive producer/adapter import from numeric or harness;
- harness object, launch envelope or artifact digest passed to numeric entry;
- closure or mutable/request-specific module global;
- dynamic import, `exec`, `eval` or `compile`;
- `runpy`, subprocess, ctypes/cffi, marshal or pickle family;
- frame/caller inspection;
- `sys.modules` or `__builtins__` indirection;
- `getattr`-based forbidden call;
- constructed code/function object;
- filesystem, mmap or NumPy file-loading path;
- access through `packed.np` or another subordinate alias;
- producer helper name or schema used for verifier parsing;
- runtime module imported after the compute gate closes;
- direct input `frombuffer`/mmap/caller-buffer array;
- entry source, AST, call graph or import-policy hash changed; and
- numerical-semantic hash changes when varying, one at a time, every excluded
  precommit field: artifact digest, producer/adapter source hashes, producer
  operation-model hash, capability, parent PID, deadline and semantically
  admissible resource caps.

Static-policy success is not accepted as mathematical correctness.

### 11.6 Existing semantic and science boundaries

Retain attacks on:

- any omitted, duplicated, reordered, renamed, sign-changed or non-reduced
  witness;
- wrong witness index or one-ulp-lower least upper binary64 value;
- P/Q swap;
- column norm substituted for maximum absolute row sum;
- omitted `e` in P or omitted `delta_Q e` in Q;
- reassociated scalar trace;
- lowered `m`, `a`, intermediate or final radius;
- nominal output outside directed box;
- point lift, nominal action and directed action using different contracts,
  kernels, inputs, block sizes, runtimes, byte orders or summation orders;
- point lift preserving `-0.0`;
- nominal output zero canonicalized rather than bit-preserved;
- producer and verifier resource/operation-model hashes incorrectly required
  equal; and
- selector, positive budget, production observable, continuum, F1/F2/F3 or
  `science_executed=true` / `f0_pass=true` supplied.

## 12. Receipt minimum nonclaims

Any eventual success receipt must include exact false/nonclaim fields:

~~~text
status = PASS_RATE_ACTION_METHOD_ONLY_NOT_F0
separate_composition_implementation = true
separate_composition_only = true
subordinate_stage1_implementation_reused = true
subordinate_directed_implementation_reused = true

fresh_process = true
verifier_owned_reconstruction = true
producer_arrays_accepted = false
producer_output_used_for_computation = false
arrays_exposed = false
returned_numeric_payload_bytes = 0

standalone_public_lineage_authoritative = false
authoritative_input_radius = false
resource_promotion_eligible = false
largest_shape_allocated = false
largest_shape_run = false
science_executed = false
f0_pass = false
continuum_claim = false
prr_release_authorized = false
~~~

The current design fixes `resource_promotion_eligible=false`. A later exact
implementation, runtime-qualified resource protocol and independent audit
would require a separate amendment before that field could change.

The receipt contains only exact built-in scalar values, fixed tuples of
scalars and verifier-local frozen scalar schema objects. It contains no bytes,
ndarray, view, mutable container, producer dataclass, private path, capability,
socket, file descriptor or exception object.

## 13. Authority and recurrence remain future work

The acyclic transition graph makes output lineage structurally representable.
It does not make a public radius authoritative.

Authoritative recurrence still requires one of:

1. a same-private-worker session that retains state/radius internally; or
2. full-chain replay from the immutable root, recomputing every numerical
   request, transition, state and radius in order.

Neither recurrence protocol is implemented here. Each needs its own state
machine, restart/failure semantics, resource ledger and adversarial tests.

A naked artifact, transition, manifest, receipt or coherent public rehash
cannot establish authority.

## 14. Acceptance and stop conditions

This v2 design is not ready to promote until all of the following exist on
exact source hashes:

- the four proposed files and frozen import policy;
- complete canonical schemas and frame struct;
- acyclic numerical-request/transition/output/artifact/launch-envelope source;
- nonblocking socketpair transport with absolute-deadline tests;
- complete producer, parent, child and aggregate logical resource models;
- honest macOS physical observations with unknown handling;
- the exact HOLD enum and fatal cleanup path;
- independent exact numerical oracles;
- the full positive, mutation, concurrency, timeout and cleanup suite; and
- a new independent adversarial audit.

Even after those one-step tests pass, F0 remains HOLD until all separate F0
method components and gates pass on their own exact evidence. Nothing in this
document allocates or runs the `7,165,305`-state target.

Current conclusion:

~~~text
V2 DESIGN DIRECTION RECORDED
IMPLEMENTATION ABSENT
INDEPENDENT SOURCE AUDIT ABSENT
RESOURCE PROMOTION ABSENT
F0 HOLD
F1/F2/F3 NOT AUTHORIZED
SCIENCE NOT EXECUTED
CONTINUUM PATH NOT CLAIMED
PRR RELEASE HOLD
~~~
