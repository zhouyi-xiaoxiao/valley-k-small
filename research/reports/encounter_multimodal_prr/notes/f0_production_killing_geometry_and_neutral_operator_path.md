# F0 production killing-geometry and science-free full-operator path

Date: 2026-07-15  
Status: **LIVING DESIGN V1 / CONTROL-FREE GEOMETRY FIRST / SCIENCE-FREE OPERATOR
ONLY AFTER INDEPENDENT GEOMETRY ACCEPTANCE / RESOURCE GATE BEFORE
PROPAGATION / HOLD F0 / NO F1**

## 1. Purpose and inherited boundary

Round 167 accepts the 12-row production partitions, free-axis rate payloads,
analytic initial source boxes, native packed free-axis joins, and a two-repeat
serialized replay.  It does not contain contact geometry, catalyst supports,
killing, a full generator, propagation, topology, or a production resource
gate.

This note separates the next work into objects that cannot be confused:

```text
control-free contact/support factors
-> independent factor replay
-> literal-zero conservative full-operator baseline
-> explicitly nonphysical synthetic contact-shaped killing fixture
-> four explicitly nonphysical synthetic support-factor killing fixtures
-> packed full-operator structural receipts for all three fixture classes
-> isolated largest-row resource receipt
-> later production action/absolute-time/topology stages
```

No selector, prospective weight, installed budget, positive-budget row, root,
or scientific time trace may be read while implementing these stages.

## 2. Frozen control-free authority

The source object is

```text
artifacts/data/physical_killing_geometry_source_v1.json
SHA-256 5543f76031d731cb5bcf3e4cdf3bdabaffacb2053400e3015d6ab57906a27669
```

It binds:

- the accepted 12-row configuration bytes
  `063913c7fbc2b706ba85a0e3f06005bad23a2292749817294cbf41f5cdce4084`;
- the accepted production partition bundle
  `5d81d1c02ec2484f0b3d5fab3a825cf6f6331f7d3e4cc8dae224266201dfbd9e`;
- physical dimension two and quotient coordinate order
  `(midpoint, relative_parallel, relative_perpendicular)`;
- the exact binary64 contact radius and periodic cut-locus condition; and
- four analytically unit-normalized compact-bump support basis functions.

The object contains neither a budget nor control weights.  It authorizes no
scientific execution.

## 3. Killing geometry is a factorization, not a concrete operator

For each production row, let

\[
 C_{ab}\supset
 \frac{\left|\{(r_\parallel,r_\perp)\in
     R_a\times Y_b:\ r_\parallel^2+d_{\mathbb T}(r_\perp,0)^2\le a^2\}\right|}
      {|R_a|\,|Y_b|}
\]

be the relative-cell contact-fraction interval.  Let

\[
 \Phi_{jm}\supset \frac{1}{|M_m|}\int_{M_m}\phi_j(M)\,dM,
 \qquad j=1,\ldots,4,
\]

be the four midpoint support-density intervals.  Each basis function has
analytic physical-volume integral one.

For a later physical budget `B` and exact weights `w_j`, the killing field
would be

\[
 k_{mab}=B\,C_{ab}\sum_{j=1}^4w_j\Phi_{jm}.
\]

The factor bundle saves only `C` and `Phi`.  Since `B` and `w` are absent, it
must state

```text
killing_geometry_bound                  = true
concrete_killing_constructed             = false
single_physical_operator_bound           = false
full_operator_bound                      = false
```

Calling these factors a physical generator would be a promotion error.

## 4. Canonical killing-geometry bundle

The intended producer is

```text
code/rate_defined_tensor_f0_production_killing_geometry.py
```

with schema

```text
encounter_control_free_production_killing_geometry_v1.
```

For each row it writes:

1. one canonical big-endian binary64 interval file of relative contact
   fractions with logical shape `(n_parallel,n_perpendicular)`;
2. four canonical big-endian binary64 support-density files, each with logical
   shape `(n_midpoint,)`;
3. exact references to the midpoint, relative-parallel, and
   relative-perpendicular partition bytes and their axis-relation hashes;
4. exact volume-weighted contact-area lower/upper sums;
5. exact volume-weighted support-integral lower/upper sums;
6. raw byte lengths/hashes, active/full-cell counts, and a domain-separated row
   relation digest; and
7. an exact row schema with no optional promotion fields.

Across the family, the contact payload has exactly 233,139 interval records or
3,730,224 raw bytes.  The largest relative grid is `215 x 161 = 34,615`
records.  These are compact factors; no `N`-state killing file is written.

The producer may use the currently pinned F0 analytic disk/rectangle and bump
primitives, but this makes the first bundle same-core producer evidence only.
Its positive flag must therefore be named

```text
producer_consistent_control_free_killing_geometry_all_rows = true
```

and not `independent_*`.

## 5. Independent factor replay

A separately coded verifier must not trust producer row summaries or
quadrature ledgers.  It must:

- parse the authority, configuration, initial partition bundle, new bundle,
  row manifests, and raw intervals with exact schemas and types;
- reconstruct all 12 exact partitions from their formulas;
- rederive disk/rectangle intersections at higher precision from a separate
  source implementation;
- rederive all four normalized support-density cell averages from a separate
  source implementation;
- require every independently derived interval to be contained in the saved
  producer envelope;
- independently recompute contact-area and support-integral enclosures;
- bind every path, length, hash, row order, shape, coordinate role, and
  relation digest; and
- reject missing, duplicate, aliased, unreferenced, reordered, rehashed, or
  promoted files.

Using a second source at higher precision while retaining `gmpy2`/MPFR and the
same Simpson remainder lemma is acceptable only if the receipt says exactly

```text
separate_source_implementation = true
independent_backend             = false
```

Backend independence may not be inferred.

## 6. Science-free concrete killing fixtures

Only after the factor bundle and its independent replay are accepted may a
concrete method fixture be built.  The first fixture is the literal-zero field

```text
science_free_zero_killing_v1:
k_zero(m,a,b) = 0.
```

This is the exact conservative baseline.  It tests the accepted free-axis
join, derived diagonal, `Q 1 = 0`, stochastic `P`, uniformization witnesses,
and packed tensor plumbing without reading any contact factor into the
operator.  It must state `contact_geometry_used=false` and cannot validate the
contact tensor order, a killed row deficit, or any catalyst support.
Its maximum method status is

```text
PASS_ZERO_KILLING_CONSERVATIVE_OPERATOR_METHOD_ONLY_NOT_PHYSICAL_NOT_F0
```

The second and primary nonzero diagnostic fixture is

```text
science_free_synthetic_contact_shaped_killing_v1:
k_fixture(m,a,b) = (1/256) C_ab.
```

The factor `1/256` is an exact synthetic death coefficient.  It is not the
physical installed budget, does not use the catalyst supports, and is not one
of the prospective controls.  Replication along the midpoint coordinate is
deliberate: it exercises the true contact mask, zeros, partial cells, full
cells, tensor indexing, diagonal construction, and largest dense payload while
remaining unambiguously nonphysical.

The receipt must state

```text
killing_assembly_mode                 = science_free_synthetic_contact_shaped_killing_v1
synthetic_contact_shaped_killing_rate = 1/256
physical_contact_geometry_bound       = true
synthetic_killing_bound                = true
midpoint_broadcast                     = true
support_density_used                   = false
installed_budget_used                  = false
prospective_control_used               = false
physical_control_operator              = false
physical_killing_bound                 = false
authorizes_scientific_execution        = false
f0_pass                                = false
```

No field named `physical_killing_pass` is admissible for this fixture.  Its
maximum admissible method status is

```text
PASS_SYNTHETIC_CONTACT_SHAPED_KILLED_OPERATOR_METHOD_ONLY
```

Because this fixture is constant along midpoint and does not use any
`Phi_j`, it cannot verify midpoint support ordering, the factorized
`Phi_j(M) C_ab` product, selector/weight semantics, or a physical Doi killing
field.  A later exact synthetic `c Phi_j C` fixture is required to exercise
that support-factor path before any authorized physical budget and selector
can be combined.

The third fixture class is therefore the four-member diagnostic family

```text
science_free_synthetic_support_factor_killing_v1:
k_fixture_i(m,a,b) = (1/256) Phi_(i+1),m C_ab,  profile_index i = 0,1,2,3.
```

There is no selector and no weight vector: every accepted support profile is
tested separately in the frozen centre order.  The mathematical basis label
is `j=i+1`, so the source notation `j=1,...,4` maps exactly to the zero-based
manifest field `profile_index=i`.  For the nonnegative interval inputs
`Phi_(i+1),m=[p_lo,p_hi]` and `C_ab=[c_lo,c_hi]`, the payload is formed by two
sequential directed binary64 multiplications in the exact order

```text
t_lo  = mul_down(1/256, p_lo)
lower = mul_down(t_lo, c_lo)
t_hi  = mul_up(1/256, p_hi)
upper = mul_up(t_hi, c_hi)
```

with midpoint outer, relative-parallel middle, and transverse inner.  Each of
the four payloads has its own canonical big-endian interval manifest, profile
index, centre/source hashes, factor hashes, multiplication-contract hash, and
row relation digest.  Its maximum method status is

```text
PASS_SYNTHETIC_SUPPORT_FACTOR_KILLED_OPERATOR_METHOD_ONLY
```

The exact fixture matrix is:

| Fixture class | Contact used | Support used | Concrete coefficient | What it tests |
| --- | --- | --- | --- | --- |
| `science_free_zero_killing_v1` | no | no | zero | conservative `Q 1=0`, stochastic `P` |
| `science_free_synthetic_contact_shaped_killing_v1` | yes | no | exact `1/256` | contact order, killed deficit, midpoint broadcast |
| `science_free_synthetic_support_factor_killing_v1` | yes | one `j` at a time | exact `1/256` | full `Phi_j C` tensor order and interval product |

Every fixture receipt, including the zero baseline, must carry the following
common nonpromotion block:

```text
installed_budget_used             = false
prospective_control_used          = false
physical_control_operator         = false
physical_killing_bound            = false
positive_budget_executed          = false
authorizes_scientific_execution   = false
science_executed                  = false
production_resource_gate          = false
resource_promotion_eligible       = false
largest_shape_allocated           = false
largest_shape_run                 = false
propagation_executed              = false
topology_complete                 = false
f0_pass                           = false
continuum_verified                = false
prr_release_authorized            = false
```

The fixture-specific fields are exact: zero uses
`contact_geometry_used=false`, `support_density_used=false`, and
`synthetic_killing_bound=false`; contact-shaped uses
`contact_geometry_used=true`, `support_density_used=false`, and
`synthetic_contact_shaped_killing_bound=true`; support-factor uses
`contact_geometry_used=true`, `support_density_used=true`,
`synthetic_support_factor_killing_bound=true`, and one exact
`synthetic_support_profile_index` in `0,1,2,3`.

## 7. Packed full-operator bridge

The planned bridge is

```text
code/rate_defined_tensor_f0_production_full_operator.py
```

For every mode the bridge reloads and bundle-validates the complete
`GeometryBoundPackedAxes` row; a detached in-memory object is not accepted.
The zero mode then consumes literal zero only.  The contact-shaped mode also
consumes the accepted `C` row and exact `1/256`.  Each support-factor mode
additionally consumes exactly one accepted `Phi_j` row and its profile index.
No mode reads a selector, weight vector, budget, initial target, or time.

The accepted packed-core boundary is kept explicit:

- `KernelBuildContract` controls the packed builder's declared working-byte
  allowance only; it is not a RAM, spool, output, parent, child, aggregate,
  wall-time, or cleanup contract;
- all outer logical, spool, framing, timing, and observation limits belong to
  a separate resource harness; and
- `PackedKernelInputs.killing` must be an exact `PackedIntervalPayload` with
  role `science_free_killing`, complete native binary64 endpoint bytes, the
  exact tensor shape/block size, and its canonical manifest.

For either nonzero diagnostic it expands the applicable factors blockwise
into a canonical `science_free_killing` packed interval source of logical shape
`(n_midpoint,n_parallel,n_perpendicular)`.  For the `MR+F` row,

```text
N                         = 7,165,305
packed killing endpoints  = 16 N = 114,644,880 bytes
```

The expansion must stream to a private spool and hash, never retain a tuple of
per-state interval objects, and reject a pre-existing output.  Streaming does
not itself satisfy `PackedIntervalPayload`: before construction, the complete
spool is revalidated and frozen as exact built-in native-endian `bytes` under
the declared payload cap.  The resource ledger counts coexistence of the
spool, immutable endpoint bytes, and every owned array created while the
packed kernel is built.  The adapter then constructs exactly

```text
PackedKernelInputs(axes=<three accepted packed axes>, killing=<synthetic payload>).
```

The packed core derives the diagonal, `P` self coefficient, uniformization
rate, `delta_Q`, both `delta_P` branches, and exact global witnesses.  A stored
or caller-supplied diagonal is forbidden.

The structural receipt must distinguish

```text
free_axis_geometry_bound            = true
contact_geometry_bound              = true
science_free_killing_bound          = true
fixture_mode                         = <one exact mode from the three-class matrix>
neutral_full_operator_bound         = false
science_free_full_operator_bound    = true
single_physical_operator_bound      = false
production_resource_gate            = false
resource_promotion_eligible         = false
authorizes_scientific_execution     = false
science_executed                    = false
positive_budget_executed            = false
propagation_executed                 = false
topology_complete                    = false
f0_pass                              = false
continuum_verified                   = false
prr_release_authorized               = false
```

## 8. Mathematical receipt versus resource receipt

The full-operator structural receipt and the resource receipt are separate
artifacts.  A correct operator does not prove that the target path fits the
machine; a fast allocation does not prove operator semantics.

The mathematical receipt binds at least:

```text
configuration and partition bundle hashes
Round-167 free-axis geometry receipt
killing-geometry source/bundle/independent receipt
packed-core and full-operator source hashes
tensor shape and exact state count
killing raw manifest and digest
kernel build contract and canonical-source digest
exact uniformization rate and witness ledger
off-diagonal signs and killing signs
diagonal-derived-not-supplied identity
Q 1 = -k and P substochasticity
free detailed balance and Dirichlet-form sign
all nonpromotion flags
```

The resource receipt binds those mathematical bytes but has its own runtime,
process, cap, measurement, cleanup, and failure fields.

## 9. Largest-row resource path (gate not yet authorized)

The target row is `MR+F`, shape `(207,215,161)`, with `N=7,165,305` and
`S=207+215+161=583` axis cells.  Deterministic visible payload floors include:

| quantity | bytes |
| --- | ---: |
| one binary64 state vector `8N` | 57,322,440 |
| packed killing source `16N` | 114,644,880 |
| packed kernel numerical payload `40N+64S` | 286,649,512 |
| illustrative raw numerical coexistence floor | 917,215,008 |

The last row is exactly

```text
parent: (16N+32S) + 16N = 229,308,416
child:  (40N+64S) + 56N = 687,906,592
sum:                           917,215,008.
```

It is an illustrative raw numerical coexistence floor, not a complete phase
identity and not peak-RSS acceptance.  It excludes every canonical body,
frame header/body, interpreter, allocator retention, native temporary, socket
buffer, spool window, page cache, spawn overhead, and unmodeled copy.  No
single aggregate byte cap may be published until a separate harness design
instantiates all named live objects and frame/metadata sizes.

The gate proceeds in nonpromoting stages.

### R0. Keep the two verifier problems separate

`f0_rate_action_fresh_verifier_design_v2.md` records a corrected design for a
future one-step `P.T`/`Q.T` action verifier.  It is unimplemented, has the sole
success status `PASS_RATE_ACTION_METHOD_ONLY_NOT_F0`, and fixes
`resource_promotion_eligible=false`.  It is not the resource authority for a
kernel-only target build.

A separate kernel-only resource-harness design, source, test suite, and
independent audit must be completed before R2--R5 can promote anything.  It
may reuse audited framing ideas, but it needs its own smaller state machine,
live-object algebra, exact statuses, and operation model.  The action-verifier
v2 remains a later prerequisite for R6.

### R1. Static receipt only

Freeze `N`, `S`, block size, source sizes, built-in-bytes freeze, spool cap,
frame/chunk caps, parent, child, aggregate logical payload, runtime, and
cleanup formulas.  Distinguish exact logical-payload gates from observed
physical resources.  Any physical unknown remains unknown and keeps
`resource_promotion_eligible=false`.

### R2. Harness self-tests

Use a private local `0700` directory outside synchronized storage and an
isolated `python -I` child.  Before numerical work, demonstrate exact-cap pass
and one-byte-low preallocation failure only for the source-defined logical
payload, spool/file, frame/chunk, and scalar-output byte formulas.  CPU/wall
deadlines, descriptor counts, RSS, allocator high-water, swap, pageout, page
cache, and scheduler behaviour are not one-byte identities.  Inject timeout,
crash, malformed/oversized frames, logical-payload refusal, disk exhaustion,
and parent/child death.  Every ordinary HOLD must leave no receipt, spool, or
live child; unconfirmed death/cleanup is fatal rather than PASS.

### R3. Calibration ladder

Run at least two clean-process repetitions at increasing science-free shapes.
Save parent and child process-local high-water observations, their
conservative sum, declared logical payload versus observed overhead, spool
high-water, wall/CPU time, disk-free delta, available swap/pageout observations,
cleanup, and PID/process-group evidence.  Do not call the conservative sum an
exact simultaneous aggregate RSS.  No result may relax a frozen logical cap
or change the algorithm.

### R4. Target synthetic killing spool only

Materialize and validate the `MR+F` synthetic contact-shaped killing source,
then delete it.
Do not build a kernel.  Report the predeclared logical-payload margin and all
available physical observations, exact disk accounting, and complete cleanup.
No informal "twofold headroom" rule is an acceptance criterion until the
separate resource-harness design defines its numerator, denominator, and
unknown handling.

### R5. Target synthetic killed kernel only

Build and validate one packed kernel in an isolated child, return only scalar
and hash ledgers, and repeat in a second clean process.  Kernel construction
may derive its uniformization rate and `P` coefficients, but it must not apply
`P` or `Q`, execute a uniformization series/semigroup propagation, or compute
a topology.  Until a separate resource-harness implementation and audit
exist, the maximum success wording is

```text
PASS_SYNTHETIC_CONTACT_SHAPED_KERNEL_METHOD_AND_OBSERVATION_ONLY_NOT_RESOURCE_PROMOTION_NOT_PHYSICAL_NOT_F0
```

The kernel-harness design must freeze an exact ordered enum rather than a
wildcard.  At minimum it has distinct exact statuses for API type, science
boundary, source binding, logical-resource plan, harness self-test, spool,
kernel build, physical-resource observation, child exit, and cleanup.  Until
that enum exists, R4/R5 are design stages and may not be run as accepted
resource gates.  An unknown observation, timeout, signal, stderr, hash
mismatch, logical/disk breach, malformed receipt, cleanup failure, or survivor
may not trigger a retry with relaxed caps.

### R6 and later. Actions and absolute time

Only after an independently accepted kernel-only harness may the separate
fresh rate-action verifier v2 be implemented and audited.  Then one target
point action, one directed interval action, and earliest/latest absolute-time
samples may be proposed under separate receipts.  The batched scalar topology
redesign is later work and cannot be smuggled into the kernel resource gate.

## 10. Mandatory mutations

At minimum, tests must reject:

- any source, configuration, partition, axis, row, or implementation hash
  change;
- duplicate JSON keys, floats, nonfinite endpoints, signed zero, reversed or
  negative intervals;
- contact radius, period, support centre, support width, or coordinate-role
  mutation;
- shifted-periodic cut substitution and vertex/half-volume substitution;
- missing, duplicate, aliased, reordered, or unreferenced files;
- contact/support shape or tensor-order change;
- contact coefficient substitution, support-profile substitution, R/Y swap,
  midpoint broadcast-stride mutation, or one-ulp factor-product mutation;
- a basis/hull or science-free fixture relabeled as one physical operator;
- a supplied diagonal or under-reported kernel witness;
- one-byte-low declared logical-payload, spool, frame, or scalar-output cap;
- timeout, crash, memory/disk exhaustion, malformed message, orphan, and
  incomplete cleanup; and
- any `science_executed`, `positive_budget_executed`, `topology_complete`,
  `f0_pass`, or release flag changed to true.

## 11. Ordered implementation products

```text
1. rate_defined_tensor_f0_production_killing_geometry.py
2. test_rate_defined_tensor_f0_production_killing_geometry.py
3. rate_defined_tensor_f0_production_killing_geometry_independent.py
4. independent tests and two-repeat serialized factor replay
5. freeze the three-fixture packed full-operator contract and schemas
6. literal-zero packed conservative baseline
7. synthetic `(1/256) C` packed killed-operator diagnostic
8. four exact synthetic `(1/256) Phi_j C` support-factor diagnostics
9. rate_defined_tensor_f0_production_full_operator_independent.py
10. separate kernel-only resource-harness design and exact status enum
11. kernel-only harness source, tests, calibration, target runs, and audit
12. implement, test, and audit the already recorded fresh rate-action verifier v2
13. sparse production initial-target adapter
14. production point/directed actions and absolute-time method
15. production jets and full-window topology
16. complete independent F0 acceptance
```

Only item 16 can authorize the sealed 36-row F1 campaign.

## 12. Continuum separation

This finite-volume path does not change the continuum program.  The continuum
route still requires the hash-bound C0 model/maps, fixed-box C1 convergence,
computable positive-time C2 errors, and C3 derivative box-truncation errors.
Even a passed science-free full-operator resource gate is not continuum
evidence.

## 13. Present boundary

The same-core producer freeze generated on 2026-07-15 is:

```text
producer source SHA-256
  2cada45143914edf1142daf6a5b7a8b5367757c664855dd6d836e7f43935dd9b
producer test SHA-256
  887a19536e2f81d4c99dda198cb4f7d488c9ccfff52673c843cec47bf8a2852c
canonical bundle
  artifacts/data/physical_production_killing_geometry_v1
bundle.json SHA-256
  f29c29360f3d7db58694aeaeddc7cae8e1eaaac25d8ce6d5792a9ebacf455684
relative-path-sorted file-SHA tree digest
  b05dd83f3756528c0fd09f78f3a79eb4b1894e2bb423e45e1af55f6cce928568
factorization contract SHA-256
  de42fefbfc163fdcffd573d49d1156d761341c78b3756903755579dc8e9b23af
independent-verifier design SHA-256
  84546ee439ff49503b29abfcc7c557e58091c82209c23705617e6227a44975fe
```

The tree digest is SHA-256 over `shasum -a 256` lines for all 76 files, emitted
in lexicographic **relative-path order** and using bundle-relative `./...`
paths.  The hash-first lines themselves are not resorted by complete line.
The exact tree has 75 inventoried internal files, `bundle.json`, and 14
non-root directories.
This freeze records same-core producer provenance only.  It is not an
independent acceptance receipt and cannot be consumed by a synthetic or
physical operator before the separate-source replay is accepted.

The freeze was regenerated twice in distinct fresh directories and the two
complete trees were byte-identical.  Exact rational corner classification now
serializes all 4,142 geometrically full contact cells as `[1,1]`; this removed
only spurious outward binary64 padding from 2,559 cells.  All 227,693 exact
zero cells remain `[0,0]`, and all 257 current periodic split-cell products
remain exact zero.  The accepted F0 core was not modified.

The frozen independent-verifier design applies the `2^-40` pointwise gate to
each contact-fraction candidate interval and to each support **cell-mass**
interval (exact midpoint-cell volume times the support-density interval).  It
does not apply that dimensioned gate directly to a raw support-density
interval.  Exact oracle containment has zero tolerance; no implementation may
weaken either rule without a new design hash and adversarial review.

```text
Round-167 partitions/free axes/initial stream       = ACCEPTED
control-free killing-geometry source                = FROZEN
12-row killing-geometry producer                    = GENERATED / VERIFIED SAME-CORE ONLY
independent killing-geometry verifier               = IMPLEMENTATION IN PROGRESS / NOT ACCEPTED
science-free literal-zero baseline                  = NOT BUILT
synthetic contact-shaped killing payload            = NOT BUILT
synthetic support-factor killing payload            = NOT BUILT
science-free packed full operator                   = NOT BUILT
fresh rate-action verifier v2 design                = RECORDED / UNIMPLEMENTED / UNAUDITED
separate kernel-only resource-harness design        = ABSENT
MR+F killing-spool resource gate                    = NOT AUTHORIZED / NOT RUN
MR+F synthetic-kernel resource gate                 = NOT AUTHORIZED / NOT RUN
production actions/absolute time/topology           = NOT AUTHORIZED
F0                                                   = HOLD
F1 positive-budget campaign                         = NOT AUTHORIZED / NOT RUN
PRR release                                          = HOLD
```
