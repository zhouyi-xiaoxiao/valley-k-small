# Round 61: allocation-cusp v2 independent result-blind pre-run attack

Date: 2026-07-14  
Role: independent adversarial pre-execution audit of the Round-56 v2 freeze  
Verdict: **HOLD-PREEXECUTION / NO-GO-65-97**

## 1. Scope and non-execution boundary

This round attacked the complete Round-56 allocation-cusp v2 package before
its first scientific execution.  It read the runner, ordinary and Round-50
tests, manifest, discovery protocol, independent post-result auditor and
tests, and the no-cycle protocol.  It did not open a hidden positive-`B`
replica, run mesh 65 or 97, construct any model with more than seven cells, or
modify a scientific threshold, runner, manifest, protocol, auditor, or
manuscript.

The only repository additions are this report and a result-blind mutation-test
file.  Five strict xfails in that file reproduce the open contracts.  They
must become ordinary passing regressions in a newly hashed package before any
scientific launch.

## 2. Audited anchors

| role | repository path | SHA-256 |
|---|---|---|
| implementer freeze record | `audits/round_56_allocation_v2_repair_freeze.md` | `1a0007b00f2739873e5b50942b4c8c023843db2eb9ae7d88f5d14b0755c29906` |
| v2 external manifest anchor | `artifacts/data/positive_b_allocation_cusp_discovery_manifest.json` | `492922112d14ee62f610cfc3508f7286ff7d64ab28e5b7ea7b3fdff041ad78eb` |
| v2 runner | `code/positive_b_allocation_cusp_discovery.py` | `2e2f4aacfe105a0bb7d61872ead8f189de6380e193209b7034de34c9ded35ada` |
| ordinary runner tests | `code/test_positive_b_allocation_cusp_discovery.py` | `1833b07fdefaf8740da45f914dd118b2b59d0abed713c802cbfd1eb8b450ea3b` |
| converted Round-50 regressions | `code/test_positive_b_allocation_cusp_discovery_round50.py` | `23318afd8fef7c8a31a408dfaf4c51c328604cf371458727be9dad698f76c6a7` |
| Round-61 mutation contracts | `code/test_positive_b_allocation_cusp_discovery_round61.py` | `98090c0138fdc554d19e8778df57d5ab31e6b46c185d62161bfcdb3c7bc380d1` |
| discovery protocol v2 | `notes/positive_b_allocation_cusp_discovery_protocol.md` | `fa26995c0af9824dbba7231ace4fc08cef9664cb3bd09021a5cb90c1eed393e0` |
| independent post-result auditor | `code/audit_positive_b_allocation_cusp_discovery_result.py` | `c398dec6216ac734ebcd89ffc77b12225f22ef87a4afedcc01bb5f219ad35107` |
| independent auditor tests | `code/test_audit_positive_b_allocation_cusp_discovery_result.py` | `697d8f7dea5cc5ac8d797730299f0c4026edcab54e6e7d03d61b4596acc7bbbd` |
| no-cycle audit protocol | `notes/positive_b_allocation_cusp_postresult_audit_protocol_v1.md` | `98edbadf0fa78afbe8e88d44f1377ac1f68f3ce348756153ce0fecd5025f1ebe` |
| attacked Round-50 report | `audits/round_50_allocation_discovery_prerun_attack.md` | `059e3f33b9a8e32cfe2e4ca26d1916dceac61b9fb53d89c77cdfdeb4a568829d` |

The manifest hash recomputed exactly to `492922...78eb`.  All 18 pinned roles
were present as ordinary regular files at audit time and every SHA-256 matched.
The manifest, runner, tests, and discovery protocol hashes match the Round-56
record.

## 3. Required absence boundary

The following five paths were checked without reading scientific content and
were absent both before and after all tests:

```text
artifacts/data/positive_b_allocation_cusp_discovery_result.json
artifacts/data/positive_b_allocation_cusp_discovery_reproducibility.json
artifacts/data/.positive_b_allocation_cusp_discovery_result.replica_1.json
artifacts/data/.positive_b_allocation_cusp_discovery_result.replica_2.json
artifacts/data/positive_b_allocation_cusp_discovery_independent_audit.json
```

No scientific mesh or Monte Carlo computation was run.

## 4. Executive decision and open count

Round 56 materially improves the v1 package: the preflight abort, complete
phase-evaluation stop, nonfinite HOLD conversion, exact score terms, full
boundary pin rehashes, post-replace byte check, rollback, and positive-`B`
family pins are real repairs.  The current package is nevertheless still
fail-open.

Open count for first scientific authorization:

```text
P0 = 2
P1 = 3
P2 = 1
```

Both P0 defects were reproduced by executable mutations.  The current
manifest hash is therefore permanently **not authorized** for scientific
execution.  A repaired runner/tests/auditor/protocol set needs a new external
manifest hash and another independent pre-run closure.

## 5. Round-50 closure matrix

| Round-50 item | Round-61 decision | evidence |
|---|---|---|
| P0-1 positivity/conservation | **OPEN, partially repaired** | tail/final-state, identities, and mass closure were added, but full scan minima and comparison/all-root rows are not all gated |
| P0-2 signed branch/pair identity | **OPEN, partially repaired** | signed reach, distinct indices, and mismatch are fixed; local pair ordinal still collides across different root pairs |
| P0-3 complete phase evaluation | **CLOSED in producer** | every missing eligible 65 or selected 97 evaluation makes `phase_complete=false` and clears representatives |
| P1-1 preflight leakage | **CLOSED** | a failed seven-cell preflight constructs only `(7,false)` and emits two fixed not-run rows |
| P1-2 full pin revalidation | **OPEN at TOCTOU/lexical layer** | all 18 contents are rehashed at boundaries, but symlinks are followed and no lexical snapshot/immutable-writer contract exists |
| P1-3 weak replica validator | **OPEN** | exact top-level/mesh shells were added, but nested PASS/HOLD/control/phase contracts and exact claim scope remain unchecked |
| P1-4 post-replace drift | **CLOSED** | final bytes are reread; final pin drift and byte drift roll back and sync both outputs |
| P1-5 ranking score | **CLOSED in producer/manifest** | exact four terms/formulas are frozen; root residual is eligibility-only |
| P1-6 nonfinite failures | **CLOSED at producer evaluation boundaries tested** | nonfinite control evaluation becomes a finite `HOLD_CONTROL_EVALUATION`; operational failures publish nothing |
| P2-1 family provenance | **CLOSED** | positive-`B` v2 manifest/protocol/producer are pins and match |
| P2-2 independent auditability | **OPEN and escalated to P1** | traces exist and auditor is independent, but its exact schema/algebra/claim reconstruction is insufficient |

## 6. Source-level trigger map

The line references below identify the exact frozen-v2 trigger sites.  They are
not proposed edits to the current hash; they define the minimum repair surface
for its successor.

| finding | exact trigger in frozen source | executable witness |
|---|---|---|
| P0-1 full-scan physical fail-open | producer `stationary_scan`, lines 1456--1475, serializes complete minima and `all_bracketed_roots`; `evaluate_control_law`, lines 1996--2059, gates `saved_trace`, retained `roots`, and tails but omits full density/survival minima and rejected bracket roots; `discover_mesh`, lines 2289--2343, repeats the sparse gate; `continue_branch`, lines 1792--1815 and 1819--1867, serializes comparison scans but gates only remote-pair presence/string identity | Round-61 test lines 24--108 |
| P0-2 remote-lineage collision | producer `assess_remote_pair`, lines 1479--1508, resets the side ordinal on every call and forms identity at line 1496; `continue_branch`, lines 1819 and 1863--1867, compares only those strings; auditor `reconstruct_branch`, lines 266--291, repeats the same criterion | Round-61 test lines 115--134 |
| P1-1 replica contract fail-open | producer `validate_result_contract`, lines 2457--2496, accepts any nonempty scope; lines 2549--2587 inspect selected PASS flags only; lines 2588--2593 accept HOLD by status; lines 2608--2682 check phase cardinalities and representative shells without exact row schemas, membership, or ranking | Round-61 test lines 141--149 |
| P1-2 auditor contract fail-open | auditor `reconstruct_control`, lines 136--260, has no exact control key set, derives final-state gate from trace/root minima at line 232, and checks only total mass closure at lines 248--260; `audit_payload`, lines 323--380, omits exact scope/limitations; lines 402--433 and 435--478 validate mesh/phase shells without recursive schemas or representative ranking | Round-61 tests lines 156--167 and 174--183 |
| P1-3 lexical/TOCTOU gap | producer `validate_manifest`, lines 510--553, resolves paths then follows them with `is_file`; `revalidate_complete_pin_snapshot`, lines 2791--2808, repeats content snapshots; `run_replica_commands`, lines 2811--2887, checks only at boundaries; auditor pin loop, lines 330--357, also resolves/follows; auditor `main`, lines 589--599, hashes and parses manifest/result/evidence in separate reads and canonical-checks only result bytes | static source attack; current paths were regular files at the observed instant |
| P2-1 incomplete absence boundary | producer `validate_manifest`, lines 510--553, checks only the two canonical outputs; `run_replica_commands`, lines 2826--2829, silently unlinks hidden replica paths | Round-61 test lines 186--190 proves only the observed absence, not enforcement |

## 7. P0 findings

### P0-1 — full-scan positivity can be negative while a control passes

`stationary_scan` computes and serializes

```text
minimum_sampled_density
minimum_sampled_survival
minimum_sampled_state
maximum_sampled_survival_increase
maximum_sampled_differential_mass_balance_error
```

over the complete spacing-`0.05` scan.  `evaluate_control_law` gates the last
three, but constructs `positive_density_and_survival` only from the coarser
spacing-`0.5` `saved_trace`, eligible roots, and tail checkpoints.  It never
uses `minimum_sampled_density` or `minimum_sampled_survival`.

The Round-61 mutation supplied a complete scan with

```text
minimum_sampled_density  = -1.0
minimum_sampled_survival = -0.1
```

while leaving the sparse saved trace and tail positive.  The unmodified runner
returned

```text
status                         PASS_CONTROL_EVALUATION
all_gates_passed               true
positive_density_and_survival  true
```

Thus the original Round-50 physical-law P0 is not closed.  This is not merely
an auditor omission: the scientific producer itself can select a
representative whose serialized full scan violates the frozen positivity
contract.

Two related gaps have the same disposition:

1. mesh-level scan physical gates also use only `saved_trace` and eligible
   roots, not the serialized full-scan density/survival minima or every
   bracket-refined root; and
2. the three comparison-node stationary scans are serialized but the branch
   gate uses them only for remote-pair presence/identity, not their full
   positivity, state, survival-monotonicity, or mass-balance diagnostics.

**Required repair:** in both the producer and independent auditor, gate the
complete-scan density/survival/state minima and monotonicity/mass-balance
maxima on every mesh and control; gate physical diagnostics for every entry of
`all_bracketed_roots`, not only retained roots; and recursively reconstruct and
gate every comparison-node scan under the identical frozen physical-law
contract.  Every expected array/object needs exact keys, native types, finite
values, fixed cardinality where frozen, and internal consistency.  A missing,
extra, malformed, or failed field is a false gate.  Do not change any
threshold.

### P0-2 — remote-pair identity is local and permits pair replacement

`assess_remote_pair` names a pair only by

```text
<side>:ordered_maximum_minimum_pair_<local ordinal>
```

The ordinal is recomputed independently at every comparison control.  It is
not anchored to the cusp pair, its root-order indices, or a continuation
matching path.  Two completely different negative-side pairs were evaluated:

```text
pair A: times 2.0, 2.5; bracket indices 4, 5
pair B: times 8.0, 8.5; bracket indices 40, 41
```

Both received exactly

```text
negative_time:ordered_maximum_minimum_pair_0
```

and the branch gate compares only this colliding string.  A disappearing
remote pair can therefore be replaced by a different pair while
`stable_remote_pair_identity=true`.

Signed reach, signed-side comparisons, index uniqueness, and offset mismatch
are now correctly gated; those subrepairs stand.  The topological identity
obligation does not.

**Required repair:** freeze a genuine order-preserving root-continuation rule
from the cusp-anchor scan through each ordered comparison node.  It must
serialize and check the full eligible-root order, global root ordinals,
selected root indices, originating bracket lineage, pair type, side, and an
unambiguous predecessor/successor match.  Freeze an explicit maximum allowed
root/pair drift between adjacent comparison nodes and check it in both the
producer and auditor.  Birth, death, crossing, excess drift, or an unmatched
pair is HOLD.  A per-control side/local ordinal alone is forbidden.

## 8. P1 findings

### P1-1 — replica validation is exact only at the outer shell

`validate_result_contract` checks exact top-level and mesh-row key sets, but
for nested homotopy, cusp, diagnostics, scan, branch, control, phase, and HOLD
objects it checks only selected flags or non-nullness.  It also requires only
a nonempty `claim_scope`, not equality with the frozen manifest scope.

The Round-61 mutation changed

```text
claim_scope = "continuum cusp verified"
preflight-HOLD mesh homotopy = {"unexpected": true}
```

and the unmodified validator accepted the result.  It likewise does not prove
that representatives are entries of the advanced set, that advanced controls
are the exact top-ranked rows, or that every nested PASS/HOLD object has its
fixed schema and algebraic implications.

This leaves Round-50 P1-3 open and permits two byte-identical malformed
replicas to be canonically promoted.

**Required repair:** require `claim_scope` to equal the frozen manifest value,
not merely be nonempty, and implement exact native-type/key schemas recursively
for every nested control, homotopy, cusp, diagnostic, scan, branch, PASS, HOLD,
and fixed not-run variant.  Require exact evidence timing, software, and
limitations.  Reconstruct candidate generation, geometry, top-three selection,
advanced membership, score order, representative membership, and every
PASS/HOLD implication.  Unknown keys and missing fields are failures.  Add the
Round-61 mutations as pinned ordinary tests.

### P1-2 — the independent auditor can certify malformed or false payloads

The auditor satisfies two important design requirements:

- its source contains neither producer import spelling; and
- the manifest does not pin the auditor/protocol, while the auditor hard-codes
  the manifest hash and the protocol records all three hashes.  The stated
  hash graph has no cycle.

Its result contract is nevertheless not closed.  Independently reproduced
examples show:

1. `reconstruct_control` accepts an extra unknown key, a reported
   `minimum_final_state_component=-9`, and a one-mode control with two event
   basins, provided the independently chosen masses sum to the total event
   probability and the score is edited consistently;
2. it does not reconstruct individual basin masses from the ordered minimum
   survivals or require the basin count to equal the retained maximum count;
3. phase auditing does not prove representatives belong to the advanced set
   or maximize the declared two-mesh score;
4. PASS branch reconstruction trusts arbitrary true gate names and the same
   colliding remote-pair string;
5. malformed nested scientific HOLD content is accepted as audit-integrity
   valid; and
6. a result with `claim_scope="continuum cusp verified"`,
   `limitations=["none"]`, and malformed nested HOLD content returned
   `audit_integrity_passed=true` with no failed checks.

The auditor also canonicalizes and checks result bytes but not the raw
reproducibility-evidence bytes.  It therefore does not enforce the promised
canonical evidence representation or reject duplicate-key/noncanonical
evidence at the byte boundary.

**Required repair:** give the auditor an independent exact schema for every
variant, including an exact control key set and recursive PASS/HOLD schemas;
reconstruct every basin mass from successive ordered-minimum survivals, require
basin cardinality to equal retained-maximum count, and verify the separately
serialized final-state component.  Independently reconstruct all complete-scan,
`all_bracketed_roots`, and comparison-node gates; phase ranking/membership;
cusp-anchored branch lineage and drift; and exact scope/limitations.  Parse
result and evidence from their captured raw bytes, reject duplicate-key JSON,
and require both raw payloads to equal their canonical encodings.  Its
adversarial suite must include a complete synthetic PASS, not only an honest
preflight HOLD and isolated control helper.

### P1-3 — content rehashing does not close lexical/TOCTOU identity

The current package correctly rehashes all 18 pin contents before and after
long calculations, after hidden replica writes, between children, and around
promotion.  Atomic rollback tests pass.  However:

- `validate_manifest` resolves each path and then calls `is_file`, so a
  symlink to a regular file is accepted despite the “regular-file pin” claim;
- the manifest path itself has no lexical `lstat` snapshot;
- imported pinned Python modules are loaded before the first formal pin check,
  so a transient replace/restore can make loaded code differ from the bytes
  later hashed; and
- the post-result auditor hashes/loads manifest, result, and evidence in
  separate reads and performs no complete initial/final lexical-byte snapshot.

No hash-at-boundaries scheme can exclude an adversarial writer that changes
and restores a file between checks.  The protocol currently does not state the
required immutable/no-concurrent-writer assumption.

**Required repair:** reject symlinks and non-regular lexical paths with
`lstat`; open pinned inputs with `O_NOFOLLOW` (and stable descriptors where
available); and freeze lexical path identity, metadata, and exact bytes in a
complete initial/final snapshot.  State and enforce an explicit
no-concurrent-writer/no-OneDrive-replacement contract for both scientific and
audit windows.  The auditor must capture manifest, result, and evidence bytes
once, parse those captured bytes, verify canonical result/evidence bytes, and
recheck the complete snapshot after audit promotion.  A lexical identity or
byte change is operational failure with no publication.

## 9. P2 finding

### P2-1 — the complete five-path absence boundary is not in the executable contract

The five paths are currently absent, but the manifest and `validate_manifest`
enforce only canonical result/reproducibility absence.  The independent-audit
path is not checked, and hidden replicas are silently unlinked by the parent.
An old append-only audit output would make the later required audit impossible
after scientific compute had already been spent.

**Required repair:** before starting either replica, require all five lexical
paths to be absent or apply a separately frozen, logged stale-staging policy
that never deletes a canonical/audit artifact.  Record the five-way absence in
the pre-run result and independent audit.

## 10. Items that independently passed

The following repairs were independently exercised and remain valid:

- manifest SHA `492922...78eb` and all 18 current pins match;
- the positive-`B` v2 family manifest/protocol/producer pins match;
- failed preflight returns two `NOT_RUN_AFTER_PREFLIGHT_HOLD` rows before any
  scientific model construction;
- mesh 97 is not built after mesh 65 HOLD;
- every missing eligible mesh-65 or selected mesh-97 phase evaluation makes
  the phase incomplete and clears representatives;
- exact four-term ranking formulas are frozen and root residual is not a score
  term;
- nonfinite control evaluation becomes finite HOLD;
- post-replace byte mutation, directory-sync failure, and final pin drift
  remove both canonical outputs;
- the auditor does not import the producer; and
- the manifest/auditor/protocol hash graph has no direct or indirect hash
  cycle.

These passes do not compensate for either open P0.

## 11. Executed checks

Only static checks, unit/mutation tests, and cells-7 algebra dry runs were
executed:

```text
ruff format --check: 8 files already formatted
ruff check: All checks passed
py_compile: passed

pytest ordinary + Round50 + Round61 + Stage-A + auditor:
46 passed, 5 strict xfailed
```

The five strict xfails correspond exactly to:

```text
full-scan density/survival positivity fail-open
remote-pair identity collision
replica nested-schema/false-scope acceptance
auditor control-schema/final-state/basin acceptance
auditor false-scope/limitations/HOLD-schema acceptance
```

Two independent seven-cell stdout runs were byte-identical:

```text
status                             PASS_ALGEBRA_DRY_RUN_HOLD_SCIENCE
scientific_meshes_executed         []
explicit-CSR preflight passed      true
maximum explicit action error      2.220446049250313e-16
all_discovery_gates_passed         false
canonical dry-run SHA-256          6eec8b475dbbeace0bc5d4c82b7fdf30083bd61a92ddca7b4acd12ecebd13631
```

The five scientific/evidence/audit paths remained absent afterward.

## 12. Minimum repair and re-freeze

Before another independent authorization round:

1. gate complete scan minima, every `all_bracketed_roots` entry, and every
   comparison-node scan under the unchanged physical-law thresholds in both
   producer and auditor;
2. replace local remote-pair ordinals with a cusp-anchored, bracket-lineage,
   order-preserving continuation identity plus a frozen adjacent-node drift
   limit;
3. make producer-side result validation exact recursively at every
   control/PASS/HOLD/not-run variant, require exact scope, and reconstruct phase
   selection/membership/ranking;
4. rebuild the independent auditor with exact control and nested schemas,
   basin cardinality/successive-survival masses, final state, scope/limitations,
   complete physical gates, phase, and branch-lineage checks;
5. add lexical `lstat`/`O_NOFOLLOW`, complete initial/final byte snapshots,
   canonical result/evidence checks, and a no-concurrent-writer assumption;
6. enforce the complete five-path absence boundary;
7. convert all five Round-61 strict xfails to ordinary passing regressions;
8. pin the Round-61 regression file in a new manifest; and
9. issue a new no-cycle post-result protocol and new external manifest hash.

No threshold, radius, chart, time window, mesh, or physical parameter may be
changed during this repair.

## 13. Authorization and command boundary

Current authorization is exactly:

```text
PASS-ALGEBRA-DRY-RUN
HOLD-ALLOCATION-SCIENCE
NO-GO-MESH-65
NO-GO-MESH-97
AUTHORIZED-SCIENTIFIC-COMMAND: NONE
```

In particular, the Round-56 command containing manifest hash
`492922112d14ee62f610cfc3508f7286ff7d64ab28e5b7ea7b3fdff041ad78eb`
must **not** be executed.

After the repairs above produce a new manifest hash and an independent audit
reports `P0=P1=P2=0`, the only admissible command shape will be:

```bash
cd /Users/ae23069/Library/CloudStorage/OneDrive-UniversityofBristol/Desktop/valley-k-small
caffeinate -dimsu .venv/bin/python \
  research/reports/encounter_multimodal_prr/code/positive_b_allocation_cusp_discovery.py \
  --execute-frozen \
  --expected-manifest-sha256 <NEW-INDEPENDENTLY-AUDITED-MANIFEST-SHA256>
```

That future command is recorded only as a shape, not authorized here.  The
formal runner must execute mesh 65 first and build/run mesh 97 only if every
earlier gate passes.  Both remain discovery meshes and authorize no held-out,
continuum, manuscript, or PRR claim.
