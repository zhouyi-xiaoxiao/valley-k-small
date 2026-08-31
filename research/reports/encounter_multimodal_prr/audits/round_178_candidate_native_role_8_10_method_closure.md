# Round 178 candidate-native role-8--10 method closure audit

Date: 2026-07-18

Status: **HOLD / REPAIRS AND INDEPENDENT REAUDITS IN PROGRESS / NO EXTERNAL COMMITMENT / NO ROLE-10 REPLAY / B06 FALSE**

## 1. Scope and nonclaim boundary

This round replaces the legacy executable order `role 9 -> role 8 -> role 10`
with the mathematical dependency graph

```text
frozen predecessor authorities and methods
                  |
         external commitment
          /       |       \
      role 8    role 9    role 10
          \       /
      mass/flux composition
              \
 role 10 + role 11 + composition
                  |
         symbolic candidate
                  |
   independent acceptance receipt.
```

The external commitment does not yet exist.  Roles 8--10 have not been
executed under such a commitment.  There is no same-member acceptance,
complete C1/C2/C3, F0--F3 transfer, release, or submission authorization.
Every new source and artifact in this round retains an all-false stronger
claim boundary.

## 2. Legacy dependency audit

The old stationary and raw launchers were authenticated `--check` paths bound
to current artifacts, not fresh result-blind producers.  The old raw source
also consumed the current stationary result, creating the misleading
`role 9 -> role 8` executable order.  The old killing producer imported the
broad F0/initial-stream implementation, and the old verifier pinned current
result, tree, policy, and relation digests.  None of those closures is
eligible unchanged for a new predecessor commitment.

Only small numerical algorithms may be extracted into source-separated
candidate-native implementations.  Role 8 produces raw `mu`, directed `q`,
and four common-flux witnesses; role 9 independently produces physical cell
masses and `M_L`; role 10 will produce only `C_ab` and `Phi_jm`.

## 3. Exact expression-DAG chronology

The first implementation passed 25 focused tests but conflated exact identity
with singleton numerical witnesses and admitted a scalar tautology.  The
second implementation passed 37 tests but still imposed the wrong interval
shape, omitted direct common-flux lanes, and treated arbitrary rational
selectors as physical `exp`/`erf` values.

The third implementation separated:

- an outward interval lane with 24 interval-only inputs, four common-`kappa`
  lanes, four containments, 20 nodes, six assertions, and 12 outputs; and
- a fixed value-free formal lane with 21 authority-bound atoms, 24 normalized
  sparse rational Laurent-polynomial nodes, six exact identities, and 16
  outputs, including all four profile terms.

Its first independent re-audit found no mathematical defect but found a
parent-component path replacement window, non-atomic direct publication, and
a symmetric/common-mode profile oracle.  The repaired implementation passed
46 tests and added component-anchored reads, staged no-replace publication,
and an independently specified asymmetric four-profile oracle.

The next read-only audit found `P0=0/P1=0/P2=2`: cancellation was outside the
publication rollback's `Exception` handler, and deeply nested JSON raised an
uncaught `RecursionError`.  The author repair now uses BaseException-aware,
inode-identity-guarded rollback, normalizes deep-JSON failures, and adds
KeyboardInterrupt, foreign-replacement, and three real deep-JSON regressions.
Its 53 focused tests, lint, formatting, and compilation checks pass; the
artifact bytes remain unchanged at
`f5a6badc5b3a5c5d640e21025c1c1c9bb34f8d8d2e04fb10e9e25a3a58a6fbc7`.
A fresh read-only auditor again accepted the mathematical core but reported
`P0=0/P1=0/P2=2`: an interrupt immediately after a successful stage-open or
final-link system call can precede the corresponding Python bookkeeping
assignment, and an interrupt during final descriptor release can occur after
the last successful parent fsync but outside the rollback region.  Either
window can leave owned bytes without a successful return or PASS.  A second
publication-acknowledgement repair now journals the stage capability and link
attempt before their system calls, discovers only eligible owned residues,
revalidates the full anchored directory chain, and keeps descriptor release
inside the rollback boundary.  Its 61 focused tests pass and the artifact
bytes remain unchanged.  A fresh read-only re-audit is in progress; until it
accepts the repair, the exact-DAG method remains on HOLD despite its audited
mathematical core.

That re-audit closed both prior P2s but found one sole new `P2`: when a stage
open commits before its descriptor/identity is returned, metadata-only
recovery cannot distinguish the owned empty read-only inode from a same-UID,
same-metadata foreign replacement at the capability name.  The present
cleanup can therefore delete the foreign inode.  A third repair must retain
an authenticated ownership handle/identity across creation rather than infer
ownership from live metadata.  Exact-DAG remains on HOLD.

The third repair removes metadata inference entirely.  A stage-creation
transaction owns a worker that stores the live descriptor and `(dev,ino)`
before signalling readiness; the main thread settles and joins that
transaction on interruption, and a two-phase transfer guarantees one
recoverable descriptor owner.  Its 61 focused tests pass, including the
same-metadata foreign replacement and FD/thread-leak regressions, with
unchanged artifact bytes.  The final independent acceptance audit returned
`P0=0/P1=0/P2=0`: the authenticated worker transaction, two-phase descriptor
ownership, foreign-inode preservation, all prior cleanup paths, and the
mathematical/formal/interval lanes passed.  Exact-DAG is independently
accepted as an internal method component; this is not an external predecessor
commitment or B06 clearance.

## 4. Role-8 chronology

The first candidate-native raw-axis implementation passed 24 focused tests and
a 12-row smoke:

```text
axis cells                         5,037
axis edges                         5,013
periodic seams                        12
reflecting boundary zero rates        48
virtual tensor states        34,787,462
```

Its first audit accepted the Scharfetter--Gummel formula, reflecting and
periodic conventions, raw periodic `mu=h`, `q=D/h^2`, `kappa=D/h`, and four
common-flux enclosures, but held the closure for partial authority scanning,
registry v2, loose producer semantics, a `W=1`-only test, and no independent
SG oracle.

The first repair moved to the exact v3 ten-record registry, added nested
authority checks, nonblocking reads, staged publication, a nonunit-period
regression, an independent high-precision Decimal SG oracle, and a full
12-row replay.  It passed 37 focused tests.

The next read-only audit found `P0=0/P1=2/P2=2`:

- factorization and nested configuration authority pins were not opened and
  authenticated as current bytes;
- input reads still used a component prewalk followed by pathname open;
- booleans could alias integer member indices and refinement ids lacked exact
  string typing; and
- oversized binary64 hex input escaped the stable HOLD interface.

The numerical 12-row replay and all 5,013 four-witness intersections passed.
The second repair now uses request schema v2 with an exact eleven-authority
closure, authenticates factorization v2 and the configuration
design/implementation/test bytes, uses component-anchored reads, enforces
exact scalar types, normalizes oversized hex input, and adds
identity-guarded rollback for the publication acknowledgement windows.  Its
50 role-8 tests, the 30 registry-v3 tests, static checks, and full 12-row
replay pass.  A fresh read-only final audit is in progress.

That audit returned `P0=0/P1=3/P2=0`, with all mathematics and replay evidence
accepted.  It found the same metadata-equivalent foreign-stage/descriptor
ownership failure; factorization v2 was not hard-bound as a complete
normative byte authority; and the six unselected registry-v3 records were not
fully normatively bound, allowing a coherently re-digested role-10 record.
The second repair is porting the authenticated stage transaction and
hard-binding the exact factorization-v2 and full ten-record registry-v3
authorities in both implementations.  Role 8 remains on HOLD.

## 5. Role-9 chronology

The first candidate-native stationary-integral implementation passed 15 tests
and reproduced all legacy 12-row physical masses:

```text
configurations                         12
axes                                   36
axis cells                          5,037
virtual tensor states          34,787,462
dense tensor materialized           false
```

Its first audit found five P1 and five P2 closure/validation defects.  The
first repair introduced registry v3, exact source/formula/config/member
cross-binding, nonblocking reads, staged publication, shape/product/count
checks, and a source-separated verifier.  It passed 27 tests and a full
production-form replay.

The next read-only audit verified all 12 physical `M_L` intervals against an
independent 180-digit Decimal closed form and found the numerical method
sound, but reported `P0=0/P1=4/P2=1`:

- only selected role-9 registry records were semantically exact;
- unexpected nested control/outcome metadata could bypass blacklist scanning;
- factorization/member status and false claims were underbound;
- the declared 12-row cardinality was not enforced; and
- the real 12-row replay was not a committed focused regression.

The second repair now validates all ten registry records exactly, uses the
standalone v3 registry bytes, binds the outcome-free factorization v2
candidate, validates exact nested schemas/member status/18 false claims,
enforces 12 rows and all production totals, and includes a full real-family
regression.  Its final read-only audit retained the numerical result but
exposed stable-interface and publication-acknowledgement gaps.  A closure
repair now normalizes oversized hex and deep JSON, uses anchored publication
with identity-guarded BaseException rollback, and adds the corresponding
parent, interruption, replacement, and concurrency regressions.  All 47
focused tests, static checks, Decimal closed-form containment, and the full
12-row replay pass.  A fresh read-only final audit is in progress.

That audit returned `P0=0/P1=2/P2=0`, with the mathematics accepted.  Ordinary
authority snapshots still used a pathname open after a metadata prewalk, and
the configuration design/implementation/test/initial-geometry plus the two
nested factorization sources were checked only as embedded pins rather than
opened authenticated bytes.  A second closure repair is expanding the exact
request authority set and moving every request/input/partition/code/output
snapshot to component-anchored descriptor traversal.  Role 9 remains on HOLD.

The second repair now uses request schema v2 with exactly twelve opened
authorities, full post-read directory-chain and leaf revalidation, and the
authenticated worker stage transaction.  Its expanded 57-test suite, static
checks, Decimal closed-form check, and full 12-row replay pass with 5,037
cells, 5,013 edges, 34,787,462 virtual states, mode `0400`, one link, and no
owned stage residue.  A fresh read-only acceptance audit is running.

That audit returned `P0=0/P1=0/P2=1`.  The authority-byte closure, anchored
reads, stage transaction, full replay, and Decimal mathematics passed, but
coherently re-digested boolean refinement identifiers and boolean
configuration/sequence indices were accepted through Python's bool/int
aliasing.  The exact-type repair now requires nonempty exact strings for both
refinement identifiers and exact, range-checked, cross-equal integers for
configuration and sequence indices throughout member, semantic-id,
sequence-binding, and axis-binding records.  Seven coherent-redigest
regressions were added.  Ruff, byte compilation, all 64 focused tests, and a
fresh full 12-row replay pass with 5,037 cells, 5,013 edges and 34,787,462
virtual states.  Registry v3 is explicitly retained only behind one
transitional contract binding; role 9 remains on HOLD pending the v4 swap and
a fresh independent acceptance audit.

## 6. Role-3 and parameter-source correction

The old `continuum_c1_factorization_source_v1.json` was labelled standalone
but bound the current production killing bundle's embedded factorization
object and a two-repeat output receipt.  It is outcome-bound and ineligible
for a new predecessor commitment.

The replacement candidate is:

```text
artifacts/data/continuum_c1_factorization_source_v2_candidate.json
SHA-256 1cf32a65081dc4f381daae45a556e0e26dc9411eb248cd99e555b754ffad3e26
```

It freezes only the control-free configuration/partition/geometry lineage,
unit longitudinal Jacobian, periodic Haar `W^-1` normalization,
`V_jmab=W^-1 C_ab Phi_jm`, profile order, and storage order.  It binds no
role-10 enclosure, control, budget, production killing tensor, or receipt.
Its builder and independent validator currently pass 29 focused tests,
including parent-replacement and partial-write cleanup cases.  Independent
read-only re-audit is still required.

The read-only audit accepted the factorization artifact's mathematics, units,
storage order, exact source pins, and outcome-free bytes, so no content
version bump is required.  It found `P0=0/P1=2/P2=1` on the surrounding line:
publication lacks authenticated stage ownership, writable authorities are
accepted, and the field named `dependency_closure` is ambiguous if read as
complete transitive provenance.  The existing three nodes are sufficient
only as the direct normative role-3 data-source closure; configuration
producer/test and downstream partition provenance remain method-level
authorities and are not claimed by this artifact.  Code-only P1 repairs and
this explicit scope correction are in progress; the factorization bytes and
SHA remain unchanged.

The standalone method-parameter candidate is:

```text
artifacts/data/continuum_c1_c2_n0_method_parameter_registry_v3_candidate.json
SHA-256 6c1879edaefe5f99da4fffcb76e12466862577376c305e14c857b880067e3b32
```

It contains exactly five top-level keys, ten ordered records, exact
candidate-native scopes, v3 domain-separated record digests, generic
same-backend sentinel relations, and 18 false claims.  Its builder and
independent validator currently pass 30 focused tests, including coherent
redigests of each record, parent replacement, and partial-write cleanup.
Independent read-only re-audit is still required.

That audit found registry v3 scientifically under-specified for role 10 and
therefore nonterminal.  In addition to the shared publication and writable-
authority P1s, it omits the 192-to-384 and 384-to-512 containment relations,
contact-versus-Simpson applicability, exact zero classification, numeric
width/mass gates, and the frozen Simpson/resource caps.  Registry v3 and its
SHA are preserved as historical candidate bytes.  A new v4 registry with a
new schema, digest domain, complete role-10 records, authenticated stage
ownership, and strict immutable validation is being built before any role-10
implementation.

Registry v4 passed through several rejected author-side revisions.  The
initial `d1ad73...` bytes omitted exact resource and policy closure.  The
`3f0487...` repair added those fields, but later review found an inaccurate
512-bit contact-sentinel scope.  Transient `b285f3...`, `9f0a01...`, and
`c9b577...` bytes record the repair/regression chronology only; in particular,
`9f0a01...` and `c9b577...` falsely said that all 1,304 partial contact cells
were recomputed at 512 bits and were rejected.

The independently accepted result-blind registry is now

```text
artifacts/data/continuum_c1_c2_n0_method_parameter_registry_v4_candidate.json
SHA-256 e403a9576abb08d3ada884cd283cce29ce8f877b0e9843cc8d5b911c8c0b0ac5
byte length 14,164
mode 0444
link count 1
```

Its first six records retain the stationary, raw-formula, binary64, and
exact-DAG scopes under the v4 digest domain.  Its final four records freeze
the 192-bit directed contact/profile producer, 256-bit analytic disk-area
anchor, same-backend 384/512 verifier, and exact wrapped contact classifier.
The verifier record now states the implemented boundary exactly: all 1,304
partial contact cells are independently recomputed at 384 bits, while the
first partial cell in each of the 12 rows is also used as a 512-bit sentinel.
All 6,852 support cells and all 48 support aggregates use paired 384/512
checks.  Published 192-bit values are read as candidate enclosures for
containment, but are not used to reconstruct the oracle.

Independent review recomputed all ten record digests, both policy-preimage
digests, 30 precision/resource/deadline fields, every contact-area aggregate,
and every unit-mass profile aggregate.  Builder `--check`, source-separated
validation, 122 focused cases, Ruff checks, and final no-drift rehashing pass.
The registry verdict is `P0=0/P1=0/P2=0`, strictly as an internal result-blind
precommit authority.  It is not an external commitment or B06 clearance.

The outcome-free factorization-v2 artifact remains byte-stable at
`1cf32a65081dc4f381daae45a556e0e26dc9411eb248cd99e555b754ffad3e26`;
its check, source-separated validator, and 44 focused cases pass.

The structural successor member is now

```text
artifacts/data/continuum_c1_c2_n0_member_spec_v4_candidate.json
SHA-256 b2982e4e2b0bac208f80472d0de959fa152a5494c895677d081836c482e5f2d5
member identity 68c8f9eeaca5127e9fb49c4671731990869350b358c67632fb11513f26472193
```

Independent reconstruction matched all 12 configurations, 36 partitions,
5,037 cells, 5,013 edges, 12 periodic seams, and 34,787,462 virtual states.
The mathematical identity includes complete member semantics, sequence
bindings, roles 1--4, and factorization-v2.  It deliberately excludes the
method registry, runtime closure, role-8--10 results, and external commitment.
The first independent audit found one P2 validator-parity gap: the builder
required five joint-refinement `established_scope` flags to be exactly true,
while the source-separated validator did not mirror those gates.  The repair
added the five validator checks and five coherent-repin mutation cases without
changing the artifact or member identity.  Builder check, source-separated
validation, and 94 focused cases (26 main plus 68 mutations) pass.  A fresh
read-only audit independently reproduced the identity, exercised the five
scope mutations and both installed-byte race windows, and returned
`P0=0/P1=0/P2=0` for structural mathematical membership only.

The successor anti-vacuity policy-v4 is now frozen at
`artifacts/data/continuum_c1_c2_n0_anti_vacuity_policy_v4_candidate.json`,
SHA-256
`599252aa1a9fd1d65d9ff3d0faa1e21bb2609da96cca6b6fff1e61a89ebff196`.
It opens only the immutable v3 policy lineage, member-v4, and registry-v4,
copies the exact inherited thresholds, and keeps all 18 promotion claims
false.  Its replay-role field is catalog order only, implies no dependency
edges, and allows roles 8--10 to run in parallel only after commitment.
Builder check, source-separated validation, 88 focused tests, and a fresh
read-only audit pass with `P0=0/P1=0/P2=0`.  This is internal result-blind
policy authority only, not an external commitment or replay authorization.

## 7. Current gate ledger

```text
legacy dependency audit                         COMPLETE
role-3 outcome-free factorization candidate     INDEPENDENTLY ACCEPTED INTERNAL COMPONENT
standalone method-parameter registry v3         HISTORICAL / SUPERSEDED BY V4
standalone method-parameter registry v4         INDEPENDENTLY ACCEPTED INTERNAL PRECOMMIT AUTHORITY
successor structural member v4                  INDEPENDENTLY ACCEPTED STRUCTURAL MEMBER ONLY
successor anti-vacuity policy v4                INDEPENDENTLY ACCEPTED INTERNAL RESULT-BLIND POLICY
exact-DAG mathematical core                     AUDITED
exact-DAG cleanup/interface closure              INDEPENDENTLY ACCEPTED P0/P1/P2 ZERO
candidate-native role 8 v1                      TRANSITIONAL / NOT COMMITTABLE
candidate-native role 8 v2                      COMMITTED-RUN MIGRATION IN PROGRESS
candidate-native role 9 v1                      TRANSITIONAL / NOT COMMITTABLE
candidate-native role 9 v2                      COMMITTED-RUN MIGRATION IN PROGRESS
candidate-native role 10                        COMMITTED-RUN MIGRATION IN PROGRESS
mass/flux composition                           NOT IMPLEMENTED
symbolic killing composition                    NOT IMPLEMENTED
complete method/runtime/transitive registry     NOT IMPLEMENTED
external predecessor commitment                 ABSENT
fresh committed roles 8--10 replay              NOT PERFORMED
B06 structural remedy prepared                  FALSE
B06 cleared                                     FALSE
same-member acceptance                          FALSE
complete C1/C2/C3                               FALSE
F0--F3/root/release/submission                   FALSE
```

No green local test or internal subagent review is an external predecessor
commitment.  No current artifact hash may be written back into a precommit
method, parameter, policy, or threshold source.
