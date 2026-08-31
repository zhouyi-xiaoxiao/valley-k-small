# Round 177: n=0 predecessor-authority structural candidate

Date: 2026-07-18

Status: **ACCEPTED_WITH_P2 FOR A NON-PROMOTING PREPRODUCTION STRUCTURAL
CANDIDATE ONLY / P0=0 / P1=0 / P2=3 / B04 REMEDY PREPARED BUT NOT CLEARED /
B06 OPEN / HOLD EXTERNAL COMMITMENT / HOLD ROLES 8--10 REPLAY / HOLD
SAME-MEMBER / HOLD C1--C3 / HOLD F0--F3 / HOLD RELEASE**

```text
verdict: ACCEPTED_WITH_P2
accepted_layer: non_promoting_preproduction_predecessor_authority_structural_candidate_only
P0: 0
P1: 0
P2: 3
bundle_sha256: 34079e6c060fac062b14742ad5eafa6725e71bb6471c194c8c1c31979aab7099
B04_structural_remedy_prepared: true
B04_cleared: false
B06_structural_remedy_prepared: false
blockers_cleared: 0
external_predecessor_commitment_present: false
ordered_roles_8_10_replay_executed: false
production_same_member_bridge_accepted: false
release_eligible: false
```

## Purpose and authority boundary

Round 177 asks whether the current source prefix can be frozen as one
machine-auditable proposal before any successor production replay.  It does
not ask whether the proposal can authorize itself.

The accepted result is a seven-file predecessor-authority candidate.  It is
published through a whole-directory no-replace step under an explicit
no-hostile-writer contract.  The candidate reconstructs the current
level-`n=0` member, parameter registry, legacy-kernel inventory, policy, and
predecessor-prefix DAG.  It also emits a request for later external review.
That request is not an external commitment.

This audit is a local, read-only review record.  The candidate explicitly
states that same-process, child-process, or subagent review does not count as
external authentication.  Therefore this audit cannot clear a blocker,
authorize roles 8--10, materialize the reserved formal candidate or
acceptance receipt, or promote any scientific or release claim.

## Reviewed bytes

| role | report-relative path | SHA-256 |
|---|---|---|
| package bundle | `artifacts/data/continuum_c1_c2_n0_predecessor_authority_candidate_v1/bundle.json` | `34079e6c060fac062b14742ad5eafa6725e71bb6471c194c8c1c31979aab7099` |
| candidate member | `artifacts/data/continuum_c1_c2_n0_predecessor_authority_candidate_v1/continuum_c1_c2_n0_member_spec_v3_candidate.json` | `b5eea6553d329bcbc4a1eb301dd3d5fb5b5acd387b80bfee5094286d3ca8ab71` |
| parameter registry | `artifacts/data/continuum_c1_c2_n0_predecessor_authority_candidate_v1/continuum_c1_c2_n0_method_parameter_registry_v2_candidate.json` | `3fc83a81046f92f24e3adc51645462aa68953cc5991573fe63e6f0e941ed6961` |
| method registry | `artifacts/data/continuum_c1_c2_n0_predecessor_authority_candidate_v1/continuum_c1_c2_n0_outward_method_registry_v2_candidate.json` | `2a455a3bb4808fb722a83b815a7c8cf8995669360394ee6f8adc73c87cc280fb` |
| candidate policy | `artifacts/data/continuum_c1_c2_n0_predecessor_authority_candidate_v1/continuum_c1_c2_n0_anti_vacuity_policy_v3_candidate.json` | `e0b3a649b45494881a534ecd84fe6f98f73012f0e5e6d7ca14b90fddffbccac8` |
| predecessor-prefix manifest | `artifacts/data/continuum_c1_c2_n0_predecessor_authority_candidate_v1/continuum_c1_c2_n0_predecessor_authority_candidate_manifest_v1.json` | `4c2ed0723711e537c6c188016ab9ec3e3a3c0d7966eb1c257f868c48116ef245` |
| external-review request | `artifacts/data/continuum_c1_c2_n0_predecessor_authority_candidate_v1/continuum_c1_c2_n0_external_commitment_review_request_v1.json` | `138872e31707afd8692ef87c03785bdc4c68a49e6ed6d9394c6a4ee3828300d8` |
| builder | `code/build_continuum_c1_n0_predecessor_authority_candidate_v1.py` | `79ff0d533ee549d62add35c4a1ae3ff9f27e9e7e30eec66a97b957ba444f1e5d` |
| independent validator | `code/validate_continuum_c1_n0_predecessor_authority_candidate_v1.py` | `70e461170316e15561354072c12fda5a6534fb5ad0366b9a5ebe0a1913b7d629` |
| static/currentness tests | `code/test_continuum_c1_n0_predecessor_authority_candidate_v1.py` | `98b3e933104f10810b4cd3e17561a84cbbca2d8c96a62243378ef81c3b3e496b` |
| mutation tests | `code/test_continuum_c1_n0_predecessor_authority_candidate_mutations_v1.py` | `b067d3a4074047fb698f28c13719bc219b99289fb108be6b030d8f302485b51f` |
| current-spine verifier | `code/verify_current_continuum_spine.py` | `d5942f33332d10b1395694b8e2b36eed7a38de8a113ca85affa01a5a97e21106` |
| current-spine verifier tests | `code/test_verify_current_continuum_spine.py` | `107d06c014afe9332ca2a7f49690f9b615401d46c70e1f0539aa0caec8337017` |

The audit document is not included in its own table and is not a
self-authenticating receipt.

## Independent reconstruction

The mathematical/provenance review independently regenerated all 36
level-`n=0` partitions from the 12 Round-172 sequence definitions using exact
`Fraction` arithmetic.  The generated canonical JSON matched the current
partition files object-for-object and byte-for-byte.

The independently recovered ledger is:

```text
configurations                 = 12
partitions                     = 36
axis cells                     = 5,037
oriented axis edges            = 5,013
periodic seams                 = 12
killing profile indices        = 48
virtual tensor states          = 34,787,462
cell_centred_reflecting        = 20
vertex_centred_reflecting_dual = 4
cell_centred_periodic_base     = 10
cell_centred_periodic_half_shift = 2
```

The configuration order is `O113/Base`, `E128/Base`, `O129/Base`,
`O161/Base`, `M+`, `R+`, `MR+`, `MR+F`, `A_M`, `A_R`, `A_Y`, `A_MRY`.
All indices, labels, tensor shapes, sequence identifiers, refinement semantic
identities, and row/partition hashes agree.

The independently recomputed member identity is
`90f4be333a70797792d7b7ba74b7bec213db304360569b349edf92ae7aaee229`.
The physical-parameter bundle digest is
`a8ef22e8d7a46175df4944659741683a77656cc4bca0e6393411e184bb5d26c2`.

## B04 is prepared, not cleared

The v3 member does more than copy partition paths.  It independently
reconstructs and binds all 36 partition SHA-256 values, the 12 configuration
row bytes, each three-axis semantic identity, and the physical-parameter
digest into one member identity.  This supports exactly:

```text
B04_structural_remedy_prepared = true
```

It does not support `B04_cleared=true`.  Round 172 itself still lacks those
partition hashes, the candidate has not been externally committed, and no
fresh roles 8--10 output binds this candidate.

## B06 remains open

The parameter registry contains 10 specifications.  The method registry
contains nine methods and correctly binds their parameter, producer, verifier,
and top-level code SHA-256 values.  Those nine methods are nevertheless legacy
kernels that emit legacy schemas and bind legacy member/method/current-source
artifacts.

The candidate-native `exact_fraction_expression_dag_v2` method is absent.
The registry truthfully records:

```text
B06_structural_remedy_prepared = false
legacy_kernel_hash_inventory_draft_prepared = true
all_report_local_dependency_closures_bound = false
transitive_report_local_dependency_closure_complete = false
parameterized_successor_native_producers_and_verifiers_frozen = false
```

Thus the inventory is a useful migration map, not replay authority.

The legacy raw-flux producer also consumes the stationary artifact, so the
current executable dependency begins with stationary role 9 before raw role
8.  A successor must either split a result-blind raw primitive from that
dependency or explicitly freeze and verify the true DAG.  Renumbering the
legacy calls would not create a valid predecessor order.

## Policy and DAG checks

The candidate policy preserves the complete legacy `requirements` object
without threshold loosening.  The three relative-width caps remain
`1/1099511627776`, the two anchor caps remain `1000000/1`, and the minimum
configuration count remains 12.  No role-8, role-9, or role-10 result artifact
is selected as a builder input.  The policy permanently excludes current
enclosures from acceptance, forbids retroactive acceptance, and requires a
future replay.

The predecessor-prefix DAG has:

```text
nodes = 74 = 8 role catalog + 9 supporting + 48 subordinate + 9 code
edges = 109 = 16 base + 9 code-to-registry + 84 subordinate
```

The 48 subordinate entries are exactly 12 row manifests and 36 partition
files.  Paths and roles are unique, hashes are current, every edge endpoint
exists, no edge is duplicated, and the graph is acyclic.  Each row has
`bundle -> row`; each partition has `row -> partition -> candidate member`.

This proves `predecessor_prefix_dag_complete=true` only at its declared
prefix scope.  Roles 8--10, their formal operation model, their complete
transitive code/data closure, and interval replay are absent, so
`formal_selected_source_dag_complete=false` remains correct.

## Adversarial repair chronology

The first apparent 66/66 test result was not accepted.  Independent code
review found that the mutation helper copied candidate files as writable
`0644`.  The validator rejected all 51 negative cases at its immutable-file
gate, while the tests checked only a generic error prefix.  Those mutation
results were false-positive coverage and were classified P1.

The repair:

1. restores every cloned or rewritten package file to `0444`;
2. adds an unmutated immutable-clone positive control;
3. requires every negative test to exclude the permission error and match an
   attack-specific semantic or parser error;
4. removes a refresh step that silently repaired the attacked
   `method_parameter_source_sha256`;
5. makes the reserved-basename-specific validation path reachable; and
6. makes builder `--check` reject writable or multiply linked package files,
   with dedicated `0644` and `nlink=2` regression tests.

The repaired suite contains 17 static/build/currentness cases, one immutable
positive control, and 51 effective negative cases: 69 collected cases and 69
JUnit entries.  A second independent code review verified all 51 attacks
reach their intended parser or semantic gate, including the formerly
self-repaired method-parameter-source attack.  The repaired code review
ledger is `P0=0 / P1=0 / P2=1`.

## Executable evidence

The final isolated entry points report:

```text
PASS_PREDECESSOR_AUTHORITY_CANDIDATE_BUILD
bundle_sha256=34079e6c060fac062b14742ad5eafa6725e71bb6471c194c8c1c31979aab7099
files=7 configurations=12 partitions=36 methods=9
B04_structural_remedy_prepared=true
B06_structural_remedy_prepared=false
B06_hash_inventory_draft=true
blockers_cleared=0 external_commitment=false replay=false release=false

PASS_PREDECESSOR_AUTHORITY_CANDIDATE_VALIDATION
bundle_sha256=34079e6c060fac062b14742ad5eafa6725e71bb6471c194c8c1c31979aab7099
files=7 configurations=12 partitions=36 cells=5037 edges=5013 profiles=48
B04_structural_remedy_prepared=true
B06_structural_remedy_prepared=false
B06_hash_inventory_draft=true
blockers_cleared=0 external_commitment=false replay=false release=false
```

Ruff lint, Ruff format, Python compilation, builder currentness, independent
validation, and all 69 focused cases pass.  The explicit current continuum
spine passes:

```text
checks=23
neutral_assertions=1619
pytest_collected_cases=265
pytest_junit_tests=333
failures=0
errors=0
skipped=0
full_report=false
ci_attestation=false
production_complete_C1=false
production_same_member_bridge=false
formal_symbolic_candidate=false
computable_C2=false
complete_C3=false
root_transfer=false
release_eligible=false
```

Its pre/post snapshot covers the 74 manifest-declared Round-177 dependencies
plus all seven package files, for 77 unique Round-177 paths.

## Final severity ledger

The union of the independent mathematical/provenance and repaired code
reviews is:

```text
P0 = 0
P1 = 0
P2 = 3
```

The retained P2 limitations are:

1. **Candidate-native method closure is absent.**  B06 remains a top-level
   legacy-kernel/hash draft without `exact_fraction_expression_dag_v2` or the
   result-blind successor producer/verifier transitive closure.
2. **There is no external trust-domain authentication.**  Builder and
   validator are source-separated, but local exact reconstruction does not
   authenticate the bytes that began executing, constitute a formal proof, or
   create an external predecessor commitment.
3. **Hostile-writer atomicity is not claimed.**  Publication and validation
   are robust under the stated no-hostile-writer contract, but the
   exists/check/rename and snapshot protocol is not a proof against a
   continuously racing adversarial writer.

These limitations are recorded in the candidate and do not invalidate the
accepted local structural scope.  They do prohibit any authority, replay,
same-member, theorem, or release promotion.

## Nine uncleared blockers

All nine machine-readable entries remain `cleared=false`:

1. current roles 8 and 9 bind the legacy member;
2. predecessor policy order is not independently sealed;
3. current enclosures predate a sealed successor policy;
4. Round 172 itself lacks partition SHA-256 values;
5. killing rows lack successor-member-native provenance;
6. candidate-native method/parameter/transitive code closure is absent;
7. the formal outer-open operation model and complete selected-source DAG are
   absent;
8. independent streamed exact-DAG interval replay is absent; and
9. a distinct symbolic acceptance receipt is absent.

## Next admissible path

The next admissible work is:

1. implement result-blind, parameterized, candidate-native producers and
   verifiers for roles 8--10, including complete transitive code/data closure
   and the exact operation DAG;
2. rebuild the predecessor candidate and obtain a genuinely external
   commitment to its member, method, parameter, policy, and predecessor-order
   bytes;
3. only after that commitment, execute fresh ordered roles 8--10;
4. freeze the complete executed outer manifest/operation model/source DAG;
5. independently stream the exact-DAG mass/flux/gauge/map/killing identities;
   and
6. issue a distinct acceptance receipt only if that replay passes.

Only then may the project ask whether one correlated production member is
contained and whether project-level complete C1 is accepted.  Computable C2,
box C3, componentwise root transfer, F0--F3, release, and submission remain
later gates.
