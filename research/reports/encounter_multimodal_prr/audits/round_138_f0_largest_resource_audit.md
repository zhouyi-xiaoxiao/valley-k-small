# Round 138: largest-shape F0 resource and replay audit

Date: 2026-07-14  
Reviewer: fresh method-only resource auditor  
Decision: **REJECT CURRENT LARGEST-SHAPE PATH / HOLD F0 RESOURCE GATE / NO F1**  
Open findings: **P0 = 1, P1 = 2, P2 = 1**

## 1. Scope and science boundary

This audit quantifies the resource feasibility of the frozen
`7,165,305`-state tensor shape `(207, 215, 161)` and one complete
absolute-time propagation/jet/topology path.  It is deliberately science-free.
It did not read a selector file, a positive-control/design note, a prospective
control value, or a positive installed budget, and it did not evaluate a
positive `B`, a primary row, an F1 observable, or a publication claim.

The reviewed inputs were limited to:

- `code/rate_defined_tensor_f0.py`;
- `code/benchmark_rate_defined_tensor_f0.py`;
- `code/benchmark_physical_geometry_f0.py`;
- `artifacts/data/f0_control_blind_geometry_replay_20260714.json`;
- audit Rounds 125, 128, 133, 134; and
- Round 136, added after its independent exact-type attack was frozen.

The new probe is
`code/benchmark_f0_largest_resource_probe.py`.  Its allocation modes use only
synthetic neutral axes, a shared exact killing interval `1/256`, a shared exact
uniform initial interval, or an analytic one-root polynomial.  Hard caps are
`300,000` build states, `1,000,000` action-only states, and `100,000` full-oracle
states.  Static target accounting never allocates a target-size object.

No frozen core byte was edited.  In particular, this audit did **not** attempt
the full target allocation because the preflight below did not provide a safe
headroom margin.

## 2. Frozen hashes

| object | SHA-256 |
|---|---|
| `code/rate_defined_tensor_f0.py` | `321f12aa8a5df44ca9c9162704cccd0f2c526abf9577832b4824538b0afdb8e5` |
| `code/benchmark_rate_defined_tensor_f0.py` | `15e264826c1e77c2f62e1290f28dd981f62bfcb2b03625cc603fffe8afd485d4` |
| `code/benchmark_physical_geometry_f0.py` | `b19a0bfe21d3a2e8a43fbc615255e24af6076016a50210ad3b86fece0d38d988` |
| `artifacts/data/f0_control_blind_geometry_replay_20260714.json` | `5d4de445b3f21444f44e6123f04b70c67259b3b9d1529e1ba8c2aa63c6d8b1b6` |
| `audits/round_125_f0_core_independent_attack.md` | `a49bb35834d39ac5d7e0aa2698667ad043335ecb5dc2a9c0df79b19650874a21` |
| `audits/round_128_root_f0_candidate_replay.md` | `b213e35eaff1df27101b875c3d349b1212ceee276372f96e3a6d396efa8d4fd9` |
| `audits/round_133_f0_saved_certificate_repair.md` | `1e0d19182e382c367e6cba1b83459ad72ccb85dbbb0c849770829568fa8cb9a4` |
| `audits/round_134_f0_repair_design_precheck.md` | `245a0632d24332fe0e8ef465855c18cb45f7d11b4fe990726582f801c92d174b` |
| `audits/round_136_f0_frozen_blackbox_attack.md` | `76fe1b336e7ff28e4ad98c36b6704f950e82367015a9a95fb625ecd33cc8b6a3` |
| `code/benchmark_f0_largest_resource_probe.py` | `90031a5ed580cc710a82defb980f3f902845865b7a091241dba7830a92717c81` |

## 3. Current dataflow and why the target is dangerous

### 3.1 Builder object lifetime

For `N` states, the frozen kernel retains three full `float64` arrays:
`killing_center`, `diagonal_center`, and `p_self_center`.  Axis forward/backward
arrays are only `O(sum(shape))` and are negligible at the target.

The much larger cost is temporary Python exact arithmetic.  The first state
loop appends one `Fraction` to `delta_q_rows` and one two-`Fraction` tuple to
`diagonal_target_bounds` per state.  After the uniformization rate is chosen,
the second loop appends one `Fraction` to each of `delta_p_direct_rows` and
`p_rounding_rows`.  All four containers remain live when the builder constructs
the kernel and calls the complete validator.  The validator then makes fresh
full-size centre/self arrays and performs another exact-rational state loop.

This is not a theoretical Python-object concern: capped RSS grows at about
`826--919` bytes per state even when every killing entry points to one shared
`OutwardInterval` object.

### 3.2 Matrix-free action lifetime

One 3D `P.T` or `Q.T` action constructs seven full incoming-term arrays.  The
first pairwise-reduction level allocates three more full arrays while the seven
inputs are still live.  The action-internal peak is therefore about ten
full-state arrays.  During propagation, kernel arrays, initial/saved state,
`vector`, `power`, and `accumulator` coexist with that tree.  During jets, five
full `nominal_action` copies are retained.

### 3.3 Three complete propagation passes per time sample

One `MatrixFreeAbsoluteTimeJetOracle(time)` currently does all of the following:

1. `propagate_matrix_free_absolute` validates kernel and initial state and
   computes the uniformization recurrence;
2. the producer calls `audit_matrix_free_propagation`, which validates both
   inputs again and recomputes the complete recurrence;
3. `enclose_matrix_free_jets` calls the full propagation audit again, including
   a third input validation and a third complete recurrence; and
4. the jet stage performs four additional `Q.T` actions and saves five full
   action vectors.

The three passes are sequential, not three simultaneous copies, but they triple
the dominant recurrence and exact-validation work.  Python allocator retention
also means that a freed builder peak cannot be assumed to return to the OS before
the action peak.

### 3.4 Topology multiplies absolute-time samples

Every time tile calls the absolute-time oracle at its lower endpoint.  Interval
Newton calls it at every midpoint and through every curvature tile.  The final
topology audit calls the oracle afresh for every saved tile, Newton midpoint,
Newton input interval, and final root interval.

For the frozen `[1/2,35]` window and quarter-grid width there are `138` initial
tiles.  Even if no tile were refined, construction plus saved-tile audit makes
at least `276` full absolute-time oracle calls.  If `R` roots are required, the
`1/40` candidate-width condition forces at least four splits per root from a
quarter tile, and producer/auditor Newton each add `25` calls per root.  Hence

```text
full oracle calls >= 276 + 62 R.
```

The corresponding method branches with one, three, or five roots therefore
have lower bounds `338`, `462`, and `586` calls.  These are algorithmic counts;
no control value was read or evaluated.

## 4. Static target accounting

At `N = 7,165,305`, one full `float64` state array is `57,322,440` bytes
(`54.667 MiB`).

| object or simultaneous set | target bytes | target binary size | status |
|---|---:|---:|---|
| one full `float64` array | 57,322,440 | 54.667 MiB | exact |
| three persistent kernel state arrays | 171,967,320 | 164.001 MiB | exact |
| one tuple pointer vector | 57,322,480 | 54.667 MiB | exact CPython-3.12 layout |
| ten action-internal arrays | 573,224,400 | 546.669 MiB | exact array payload estimate |
| five saved jet action arrays | 286,612,200 | 273.335 MiB | exact array payload estimate |
| twenty-array propagation/jet working set | 1,146,448,800 | 1.068 GiB | conservative numeric working estimate |
| one distinct interval tuple at measured bulk deep size `192 B/entry` | 1,375,738,560 | 1.281 GiB | `sys.getsizeof` decomposition |
| distinct initial plus killing interval tuples | 2,751,477,120 | 2.563 GiB | `sys.getsizeof` decomposition |
| retained builder Python headers, excluding all `Fraction` integer payloads | 2,350,220,040 | 2.189 GiB | rigorous header floor |

The `328 B/state` builder-header floor includes list slots, the per-state
two-`Fraction` tuple, and five `Fraction` object headers.  It excludes every
numerator/denominator integer payload and allocator fragmentation, so it is not
a peak estimate.

A separate subprocess slope over `100,000`, `300,000`, and `600,000` distinct
interval objects was `157.7 B/entry` in RSS.  That gives a lower empirical
increment of about `1.053 GiB` for each target-size distinct interval tuple.
The difference from the `192 B/entry` deep decomposition is expected from
allocator/page accounting; both estimates are reported rather than conflated.

## 5. Safe measurements

### 5.1 Host snapshot and prior control-blind geometry replay

At `2026-07-14T10:32:58Z`, the host reported `25,769,803,776` bytes (`24 GiB`)
of physical memory and `memory_pressure -Q` reported `55%` free.  This is only a
snapshot, not a reservation.

The allowed saved geometry replay measured all 12 control-blind geometries in
`51.98 s` internal time.  Its separately reported conservative process peak was
`2,032,338,792` bytes.  The largest row was `(207,215,161)` with `7,165,305`
states, but that benchmark deliberately stopped before expanding a full initial
tuple, a full killing tuple, or a kernel.

A fresh safe axis-only preflight for that largest shape completed in `0.78 s`
real time at `51,593,216` bytes RSS.  With the neutral synthetic `1/256` killing
interval, the exact maximum-exit construction gives

```text
lambda = 1084423928311304797 / 4503599627370496
       ~= 240.79048273313416.
```

This allocated only the three axes, never a target state vector.

### 5.2 Capped builder probes

Each builder probe used one shared killing interval, so it measures the frozen
exact builder and validator without paying for millions of distinct physical
interval objects.

| shape | states | measured CPU seconds | measured maximum RSS |
|---|---:|---:|---:|
| `(17,16,16)` | 4,352 | 0.854 | 54,362,112 B |
| `(33,32,32)` | 33,792 | 6.668 | 78,577,664 B |
| `(40,42,31)` | 52,080 | 10.569 | 93,683,712 B |
| `(50,52,39)` | 101,400 | wall 109.53 under heavy contention | 139,001,856 B |

The first three stable CPU probes give `196--203 microseconds/state`.  A linear
target extrapolation is `23.4--24.2 CPU minutes` for the builder alone.  The two
largest RSS slopes give `826--919 B/state`, or `5.51--6.13 GiB` for a target
process with shared killing.

Replacing the shared killing with distinct objects adds about `1.00 GiB` beyond
the already-counted tuple slots.  Holding a distinct initial tuple and its
nominal array adds about `1.11 GiB`.  Thus the physical live builder estimate is
about `7.62--8.24 GiB` before geometry residue and allocator fragmentation.  If
the builder arenas remain resident when the `1.068 GiB` numeric propagation/jet
working set is requested, the process high-water estimate becomes roughly
`8.69--9.31 GiB`.

These are extrapolations, not allocations.  Against a fluctuating `~13.2 GiB`
free snapshot they do not provide a conservative twofold headroom margin.  The
target allocation was therefore withheld.

### 5.3 Capped action and exact-validation probes

An action-only synthetic periodic kernel at `811,200` states completed 20
actions at observed rates from `0.00420` to `0.02223 s/action` across an idle and
a loaded run.  Maximum RSS was about `143 MB`.  Linear target extrapolation is
`0.0371--0.1964 s/action`.  The wide timing band is retained because the host
was actively contended; the faster value is used for the optimistic lower
bound below.

The exact validator was far more expensive and extremely linear:

| states | one kernel + initial validation CPU time | CPU time/state |
|---:|---:|---:|
| 4,352 | 0.445826 s | 102.442 microseconds |
| 33,792 | 3.462007 s | 102.450 microseconds |

Therefore one target kernel+initial validation extrapolates to `734.06 s`
(`12.234 min`).  Each absolute-time oracle performs this pair three times, so
validation alone extrapolates to `36.70 min/time sample`, before a Poisson
power, weighted accumulation, or jet action.

### 5.4 Complete capped oracle and topology probes

The probe executed the real frozen three-pass oracle end to end on capped
neutral kernels:

| shape | states | time | chunks | terms/chunk | three-pass `P.T` actions | wall seconds | RSS |
|---|---:|---:|---:|---:|---:|---:|---:|
| `(17,16,16)` | 4,352 | `1/2` | 1 | 16 | 45 | 8.71 | 56.4 MB |
| `(33,32,32)` | 33,792 | `1/2` | 1 | 25 | 72 | 99.49 under load | 79.4 MB |

Both returned four scalar jet intervals after the third replay and four `Q.T`
actions.  They are method probes, not physical results.

The analytic one-root topology probe covered `[0,2]`, saved 16 tiles and one
root, and made exactly `90` oracle calls including the complete fresh topology
audit.  The count matches the static formula: eight base tiles, eight splits,
and 50 producer/auditor Newton calls.

## 6. Largest-shape recurrence and topology extrapolation

At the largest neutral/control-blind axes and default `mean_cap=500`, directed
Poisson construction gives:

| target time | chunks | terms/chunk | three-pass `P.T` actions | four jet `Q.T` actions |
|---:|---:|---:|---:|---:|
| `1/2` | 1 | 229 | 684 | 4 |
| `1` | 1 | 390 | 1,167 | 4 |
| `35` | 17 | 712 | 36,261 | 4 |

For only the 138 quarter-tile lower endpoints, once in construction and once in
audit, exact term counting gives:

```text
oracle calls                              276
three-pass P.T actions              5,069,160
three-pass weighted terms           5,076,606
jet Q.T actions                          1,104
```

This ignores every adaptive-refinement call and all Newton calls.

Using the fastest measured action slope, the `P.T` actions alone require an
optimistic `2.18 CPU days`; the loaded-run slope gives `11.52 days`.  The three
exact input validations for 276 calls add `7.03 CPU days`.  Consequently the
current topology path has an optimistic extrapolated floor of about **9.21 CPU
days** and an observed-slope extrapolation of about **18.56 CPU days**, before weighted
accumulations, Poisson/MPFR work, adaptive refinements, Newton calls, geometry
expansion, serialization, or an independent implementation replica.

The target is therefore not merely unmeasured.  Under the frozen call graph it
is operationally infeasible for this gate.

## 7. Findings

### [P0] Exact-type and audit/consume ownership boundary remains open

Round 136 demonstrated on the same frozen core hash that an `np.ndarray`
subclass with altered equality dispatch can carry an all-zero saved nominal
state through `audit_matrix_free_propagation`; jets then consume the zero state.
That audit's measured genuine mass was about `0.9950124792`, while the accepted
substituted mass was zero.

This resource redesign cannot merely replace tuples by arrays.  Any packed
array accepted through `isinstance`, any dispatched equality, any writable
alias, or any audit-then-recoerce path would preserve or recreate the P0.

Required closure is listed in Section 8.  Until a new hash passes subtype,
layout, alias, nested-subtype, and TOCTOU attacks, F0 remains rejected
independently of resource performance.

### [P1] Frozen per-state Python exact representation is not safe at target

The measured shared-killing builder slope predicts `5.51--6.13 GiB`; distinct
killing plus initial objects raise the live estimate to `7.62--8.24 GiB`; and
allocator retention plus propagation/jet arrays can plausibly raise the
high-water mark to `8.69--9.31 GiB`.  This is too close to a nonreserved,
fluctuating free-memory snapshot to justify a target allocation.

The cause is precise: retained per-state `Fraction` lists plus millions of
dataclass intervals.  More host RAM would hide, not repair, the representation.

### [P1] Three-pass absolute time inside per-tile fresh replay is computationally infeasible

The frozen call graph makes at least 276 full time samples before any root
overhead.  Exact target extrapolation gives a 9.21-day optimistic CPU floor and
an 18.56-day observed-slope floor.  Root refinement, Newton, and the independent
replica only increase it.

This cannot be closed by a faster allocator or by memoizing an unverified saved
state.  It requires a verifier-owned replay boundary and a batched scalar-time
algorithm.

### [P2] Ten-array action tree is avoidable transient pressure

The action itself is vectorized and much faster than Python exact validation,
but its ten-array internal peak costs `546.7 MiB` at target and contributes to a
roughly twenty-array propagation/jet working set.  A fixed block/halo action can
reduce this without weakening interval bounds, provided its new summation order
receives a new roundoff proof and frozen replay hash.

## 8. Required combined redesign

The memory and Round-136 security defects must be repaired together.  A packed
representation that keeps the current live-object trust boundary is not an
acceptable repair.

### 8.1 Canonical packed interval source

Replace `tuple[OutwardInterval, ...]` at artifact and production boundaries by
a canonical packed schema containing owned lower/upper binary64 buffers.  One
`(N,2)` array costs `16N` bytes (`109.33 MiB` at target), so packed initial and
killing intervals together cost about `218.67 MiB`, versus `2.1--2.6 GiB` of
measured/deep Python-object storage.

The parser/verifier must enforce before any NumPy operation:

1. `type(array) is np.ndarray`, never `isinstance`;
2. dtype exactly native `float64`, C-contiguous and aligned;
3. `base is None`, `OWNDATA=True`, and no externally retained writable alias;
4. finite endpoints, `lower <= upper`, and required nonnegativity;
5. a canonical shape and exact byte length from an external manifest;
6. a raw-byte SHA-256 comparison after the exact-type check, never dispatched
   `np.array_equal` on an untrusted object; and
7. `WRITEABLE=False` before replay, with the same owned buffer consumed after
   audit rather than a second coercion.

All container and record boundaries must likewise use `type(value) is ...` for
the exact built-in/dataclass type.  The verifier must run single-threaded in a
fresh process, construct every object itself from canonical bytes, expose no
callback, and retain no untrusted reference.  Subtype/equality dispatch,
writable-view mutation, `setflags`/alias mutation, nonnative dtype/layout,
nested record subclass, and audit/consume race tests are mandatory P0
regressions.

### 8.2 Streaming exact kernel builder

Do not retain any per-state `Fraction` result.  Use fixed canonical blocks and
three bounded-memory passes:

1. validate packed endpoint blocks and compute the exact maximum exit/rate;
2. regenerate each block, fill `killing_center`, `diagonal_center`, and
   `p_self_center`, and reduce `delta_Q`, both `delta_P` branches, row sums, and
   killing maxima immediately to global exact witnesses; and
3. let the independent verifier repeat the block stream from canonical source
   bytes and compare numeric bytes, exact maxima, witness indices, and block
   digests.

Binary64 endpoints are exact dyadics.  The implementation should use a pinned
batch dyadic reducer with reused GMP/integer scratch, or a separately audited
Rust/C exact-dyadic backend.  Python `Fraction` is acceptable for the small set
of final witnesses, not for `O(N)` saved objects.  Block size and working bytes
must be external manifest fields with hard caps.

### 8.3 Fixed-memory matrix-free action

Replace the seven-term list and pairwise temporary tree with a canonical
block/halo action:

- allocate one output and one bounded scratch block;
- multiply/add each incoming direction in a frozen order using `out=` buffers;
- implement periodic faces and reflecting boundaries without `np.roll`; and
- hash the block order/backend/runtime in the replay contract.

This can reduce internal action storage from ten full arrays to one full output
plus bounded scratch.  Because the addition tree changes, the old gamma index
and bitwise nominal result are not inherited.  A new directed-roundoff proof,
dense oracle comparison, mutation suite, and independent hash freeze are
required.

### 8.4 One producer pass plus one independent verifier pass

The current same-process producer replay and jet replay should not both remain.
Use this authority boundary:

1. an untrusted producer writes a canonical propagation artifact;
2. a fresh independent verifier process parses only bytes, reconstructs pinned
   kernel/initial/contract objects, recomputes the propagation once, and compares
   raw state bytes and every ledger field; and
3. jets consume the verifier's own read-only replay buffer immediately in the
   same private process.

There is no public `VerifiedPropagation` object accepted from a caller and no
second coercion after audit.  The producer pass plus independent verifier pass
preserves two genuinely separate computations while removing the third
same-module recurrence and closing the Round-136 audit/consume gap.

### 8.5 Batched direct scalar uniformization for topology

Caching whole propagated state vectors per time is not viable, and trusting a
producer cache would weaken fresh replay.  The topology consumer needs only
scalar observable jets, not an `N`-vector for every time.

For fixed `P` and initial state, stream

```text
v_k = (P.T)^k v_0,
a_k = killing_center dot v_k.
```

Evaluate directed Poisson sums for all requested exact times in bounded batches
of scalar accumulators.  Since `Q = lambda(P-I)`, scalar jets can be derived from
finite differences of `a_k`:

```text
killing dot Q^r P^k v_0
  = lambda^r sum_{j=0}^r (-1)^(r-j) binom(r,j) a_{k+j}.
```

This shares the expensive `P.T` power stream across all tile times while keeping
each time direct from the original initial state.  It must use a new centered,
directed MPFR Poisson enclosure for total means up to the measured
`lambda*35 ~= 8427.67`; silently chaining approximate time states is not an
acceptable substitute for the absolute-time guarantee.

The new proof must also provide rigorous local derivative/curvature bounds
through order four, including coefficient, action-roundoff, weight, tail, and
accumulation errors.  If the finite-difference scalar bound is not sharp enough,
the fallback is a bounded multi-time batch, not an unauthenticated state cache.

Topology construction and verification may deduplicate an exact time within
their own private process by a content key containing kernel, initial, contract,
time, core/verifier, and runtime digests.  Producer and verifier caches must be
separate.  The independent verifier must recompute every **unique** requested
time from pinned inputs and compare all certificate references to it.  A saved
producer sample never becomes authority by cache hit.

At this largest neutral rate, a centered direct stream should require on the
order of the `~8,428` mean plus a rigorous tail margin per independent pass,
rather than the measured `5,069,160` base-tile actions.  That is a redesign
target, not a performance claim; it requires executable interval and replay
tests before acceptance.

### 8.6 Resource and replay acceptance gates

Before any target allocation or positive-budget run, the new hashes must pass:

1. static byte accounting from manifest dimensions and caps;
2. an isolated child-process preflight with a hard byte limit and at least a
   twofold live-headroom margin;
3. target-shape neutral packed-source construction with measured peak RSS,
   allocator high-water, wall/CPU time, and no swap-pressure excursion;
4. one largest-shape absolute-time scalar/jet sample at the earliest and latest
   window times;
5. a complete method-only topology schedule, including independent verifier
   replay, with unique-time/action counts recorded;
6. exact interval-ledger mutation tests and a separate implementation replay;
7. every Round-125/133/134 saved-field mutation; and
8. every Round-136 exact-type, dispatch, alias, and TOCTOU mutation.

Any compact-array, block-size, summation-order, caching, or scalar-jet change is
a new implementation object.  It requires new core, test, producer, verifier,
schema, and runtime hashes; no previous bitwise replay acceptance transfers
silently.

## 9. Final gate

```text
largest control-blind geometry only              MEASURED PASS
largest physical initial/killing expansion       NOT RUN: UNSAFE PREFLIGHT
largest frozen kernel build                      NOT RUN: UNSAFE PREFLIGHT
one largest frozen absolute-time oracle           EXTRAPOLATED INFEASIBLE
full frozen topology producer+audit               optimistic extrapolated floor 9.21 CPU days
Round-136 exact-type/TOCTOU boundary              P0 OPEN
packed/streaming/independent redesign             REQUIRED
positive-control or F1 execution                  NOT AUTHORIZED
```

The correct decision is to hold the current F0 resource path, implement the
combined packed/owned/streaming verifier design under new hashes, and repeat a
fresh black-box and largest-shape resource audit before any F1 action.
