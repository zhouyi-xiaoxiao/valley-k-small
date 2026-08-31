# Round 40 independent positive-B post-result auditor attack

Attack snapshot: 2026-07-13T22:53:52Z  
Scope: `code/audit_positive_b_broad_four_slab_result.py`, its original four
tests, and `notes/positive_b_postresult_audit_protocol.md`.  The frozen
positive-B producer, numerical manifest, and numerical protocol were read only.

## Decision

**NO-GO for the independent-audit artifact. P0: 2. P1: 4. P2: 2.**

Do not run or cite the current auditor as an independent PASS/HOLD
reconstruction.  This verdict does **not** invalidate or alter the still-running
two-process held-out numerical calculation: the frozen producer, its manifest,
and its result namespace were not modified.  At this snapshot the canonical
result, two-process reproducibility record, and independent-audit JSON were all
absent.

The original freeze anchors were unchanged during this attack:

| Role | SHA-256 |
|---|---|
| auditor | `eed476815960005271a3a5dce11f1054862bc1ba1d4b80df71b9862486639aa2` |
| original four tests | `d408006873b6130df7f644beec9ad9c50bacc02955ede915e5ed9bbbf67cb2d8` |
| post-result protocol | `349b8b766b8fbf771cf3c08297efde3d3fc1591ccf0d802da391c9e5140b1c08` |
| numerical manifest | `01b435c834cec9e7bfde2069b19fcdcaa4e06178ccfe0d4b6082f0705dfd5805` |

The attack cases are preserved separately at
`code/test_audit_positive_b_broad_four_slab_result_round40.py`, SHA-256
`4d81932ab193eec77659d8262120cf49183528ac7e37501bc65c22b0d90e1b2a`.
They deliberately specify the rejection behavior required for closure without
rewriting the original frozen test file.

## Findings

### P0 — Internally contradictory stationary, trace, and tangent data receive an independent PASS

The auditor derives the root-residual and curvature gates from the reported
`scaled_*` summaries (`audit_positive_b_broad_four_slab_result.py:221-229`) but
does not reconstruct

```text
abs(t f_t / f)             and             t^2 f_tt / f
```

from the simultaneously saved root time, density, `f_t`, and `f_tt`.  It checks
only the sign of raw `f_tt` (`:184-187`).  It also treats the two tangent
summary maxima as sufficient and checks only that there are five rows
(`:280-285`); the row times, direct time jets, per-row differences, and the
relationship to the five root records are not checked.  Saved scan and tail
traces are not schema-checked or reconciled with their endpoint and extremum
summaries.

The preserved attack at
`test_audit_positive_b_broad_four_slab_result_round40.py:26-41` set the first
purported stationary root to `f_t=123` and `f_tt=-1e-300`, retained forged
passing scaled summaries, inserted a saved trace with negative density,
negative derivative and survival two, and replaced the five tangent rows by
`{"time":"garbage"}`.  After updating the separate evidence record to the
new canonical result hash, the auditor returned:

```text
PASS_INDEPENDENT_RECONSTRUCTION
scientific_result_passed = true
```

This is a scientific fail-open: the accepted JSON does not even describe five
stationary points, yet the audit labels it an independent reconstruction.

Required closure:

1. use strict finite-number helpers that reject booleans and numeric strings;
2. require the exact nested producer schema, not only the top-level key set;
3. reconstruct both scaled root quantities from the raw root jets and density;
4. require topology to equal the sign-derived topology;
5. require each control-row time to equal its root time, its four time jets to
   match the root's `f,f_t,f_tt,f_ttt`, and both reported maxima to equal the
   maxima of the five row-level differences; and
6. reconcile every recoverable scan, tail, diagnostic, and mass duplicate as
   listed in the acceptance criteria below.

### P0 — The auditor can validate one byte string and certify the hash of a different live result

`load_canonical_object()` returns only a parsed object (`:97-104`).  The audit
later reopens the result path to compute `result_hash` (`:389`) and reopens the
evidence path again for its output hash (`:414`).  There is no identity or
unchanged-byte check between these operations.

The attack at
`test_audit_positive_b_broad_four_slab_result_round40.py:61-85` loaded a safe
result, replaced the path immediately afterward by canonical JSON with
`independent_solver_verified=true`, and prepared the evidence hash for the
unsafe bytes.  The auditor validated the old in-memory object, then returned a
PASS bound to the new unsafe result hash.  The live result at that hash had the
forbidden flag enabled.

Required closure: read each input once into immutable raw bytes; validate and
hash exactly that byte snapshot; then, immediately before publishing the audit,
rehash every live input, the manifest, and all thirteen source pins and reject
any change.  The output must never identify a hash computed from bytes other
than the bytes whose parsed object was audited.

### P1 — The producer's legitimate structural HOLD schema cannot be audited

`reconstruct_row()` unconditionally requires five roots and the exact
maximum-minimum-maximum-minimum-maximum topology
(`audit_positive_b_broad_four_slab_result.py:170-175`).  Therefore it raises
before reconstructing a legitimate structural HOLD.  A direct zero-root/null-
metric probe raised:

```text
ValueError: mesh 113 does not have five roots
```

This contradicts the protocol's statement that a scientifically legitimate
HOLD writes an independent audit JSON
(`positive_b_postresult_audit_protocol.md:52-54`).

The actual frozen producer contract is conditional, not five-root-only:

- `stationary_root_count` equals the length of `roots`, and `topology` is the
  topology of however many roots were retained;
- unless topology is exactly the expected five-entry sequence, peak ratio,
  valley ratios, event-basin masses, basin-mass sum, and basin-mass difference
  are JSON `null` (`positive_b_broad_four_slab.py:905-929,1007-1024`);
- the topology/ratio/event gates are then explicitly false, while all other
  gates retain their independently computed Boolean values (`:933-1002`);
- tangent rows have the same count as roots; the two tangent gates are false
  unless there are exactly five rows (`:996-1001`);
- cross-mesh root, peak, valley, and event-mass agreement metrics are `null`
  when the two topologies are not comparable, with those gates false; final-
  survival agreement may remain numeric and independently true or false
  (`:1106-1201`); and
- the top-level status is
  `HOLD_RESULT_INFORMED_POSITIVE_B_CONFIRMATION`, the positive-B confirmation
  and overall gate are false, all forbidden claim flags remain false, and the
  two evidence exit codes are `[2,2]` (`:1204-1255,1345-1377`).

Required closure: implement exactly this nullable conditional schema.  A
zero-root pair, a nonalternating five-root pair, a one-mesh structural HOLD,
and an otherwise well-formed five-root threshold HOLD must all produce
`HOLD_REPRODUCED` and exit 2, not raise.  Any null outside the producer's
conditional nullable fields must still be rejected.

### P1 — Nested result, claim-boundary, agreement, and evidence schemas are fail-open

Only the result's top-level key set is exact (`audit...py:352`).  The auditor
does not require the manifest-pinned `evidence_timing`, `claim_scope`, or
`numerical_reproducibility`; it ignores the producer's exact
`reproducibility_evidence` record and exact five limitations; and it does not
check `mesh_agreement.mesh_pair`.  The baseline supposedly valid test fixture
already omits almost all producer nested fields, supplies tangent rows
containing only a time, sets `reproducibility_evidence={}`, `software={}` and
`limitations=[]`, and is accepted (`test_audit_positive_b_broad_four_slab_result.py:70-115,128-181,188-193`).

The evidence object itself has no exact key set and its `stage` is not checked
(`audit...py:389-405`).  Numeric fields are widely coerced with `float()`, so
numeric strings and booleans are not rejected by a producer-type contract.

The attack at
`test_audit_positive_b_broad_four_slab_result_round40.py:44-58` changed the
result claim scope to `continuum and independent solver verified`, emptied its
nested evidence record, changed the mesh pair to `N=1/N=2`, changed the
evidence stage, and added an unknown promotion key.  It still received PASS.

Required closure:

- exact nested key/type contracts for result rows, diagnostics, scan,
  stationary roots, mass, tail, controls, agreement, software, limitations,
  and both evidence objects;
- exact equality to the manifest for `evidence_timing`, `claim_scope`,
  `numerical_reproducibility`, physical inputs, weights, budget and negative
  flags;
- exact producer values for the result's nested reproducibility declaration
  and five limitations;
- exact agreement mesh pair equal to the two row meshes; and
- exact twelve-key evidence schema and exact stage
  `positive_B_broad_four_slab_two_process_reproducibility`.

### P1 — `--output` can overwrite a protected input and publication is not atomic

The CLI accepts arbitrary output paths and calls `write_bytes()` directly
(`audit...py:426-442`).  The attack at
`test_audit_positive_b_broad_four_slab_result_round40.py:88-103` passed the
result itself as `--output`.  The auditor returned zero and replaced the
canonical numerical result by the audit payload.  A crash during `write_bytes`
can also leave a partial audit file.

Required closure:

- the CLI output must be the canonical audit path, or at minimum resolve to a
  regular non-symlink path distinct from result, reproducibility, manifest,
  auditor, and every pinned source;
- refuse any existing symlink and any same-file/input alias;
- write a same-directory temporary file, flush and `fsync` it, atomically
  `os.replace` it, then `fsync` the directory;
- remove staging debris on caught failure and preserve any prior audit bytes;
  and
- recheck all input hashes immediately before replacement.

### P1 — Some declared gate independence is impossible from the frozen result payload

The protocol correctly discloses that the auditor cannot recompute the finite-
volume semigroup (`positive_b_postresult_audit_protocol.md:9-10`), but then says
it reconstructs every reported mesh gate and rejects every scalar inconsistent
with underlying saved values (`:10-24`).  The frozen result saves only every
fifth time point in the scan (`saved_trace_spacing=0.1` versus scan spacing
`0.02`) and does not save state components at each scan point.  Consequently an
external auditor cannot independently recompute the full-scan minimum density,
minimum state, maximum adjacent survival increase, or maximum differential
mass-balance residual from the JSON alone.  It can only recompute the Boolean
decision from producer-reported extrema and test necessary consistency against
the coarser saved trace.

Because the numerical producer is already frozen and running, do not alter it
to enlarge the result.  Required closure is an honest boundary in the revised
post-result protocol and audit output:

- call these gates **re-evaluated from producer-reported certified extrema**,
  not independently recomputed from raw evolution states;
- separately label the root, mass, tangent, tail, agreement, and duplicate
  quantities that are independently algebraically reconstructed from JSON; and
- state that the frozen producer hash plus two-process byte-identity record is
  the provenance support for nonrecoverable scan extrema.

### P2 — The two-process execution is not independently observed by this auditor

The auditor checks that the evidence record contains two equal copies of the
canonical result hash, `[0,0]` or `[2,2]`, and several true declarations
(`audit...py:389-405`).  The hidden replica files are intentionally deleted by
the producer after comparison, so the auditor cannot independently establish
that two processes ran or that promotion occurred after comparison.  It can
only establish that an exact-schema evidence record emitted by the frozen
producer is internally consistent with the canonical result.

Required wording: `two_process_evidence_record_consistent=true`; do not say the
auditor independently verified process execution or raw replica identity.

### P2 — The post-result freeze table is not yet an executable release anchor

The protocol records auditor and test hashes, but the auditor does not verify
the post-result protocol or its own expected version, and the numerical
manifest intentionally cannot pin a later independent auditor.  This is
acceptable for a pre-result human freeze record but not yet sufficient for the
sixth-family manuscript/release chain.

Required closure: after repairing the auditor, preserve this failed Round 40
snapshot, issue a deliberate revised post-result freeze with the repaired
auditor plus original and Round-40 test hashes, and later pin the resulting
result/evidence/audit/protocol/auditor/tests as the sixth numerical family.

## Algebraic and schema acceptance criteria

The repaired auditor must, without importing the producer, enforce at least the
following recoverable equalities.

### Per root and control row

- strict finite numeric type for every numeric field, with exact integer fields
  where the producer emits integers;
- increasing root times and `stationary_root_count == len(roots)`;
- `topology == ("maximum" if f_tt < 0 else "minimum")` for every root;
- `scaled_first_derivative_residual == abs(time*f_t/density)`;
- `scaled_second_derivative == time**2*f_tt/density`;
- control-row times equal root times in order;
- each row's direct-versus-tangent time-jet difference equals the maximum
  absolute difference between its four stored time jets and the root's
  `density,f_t,f_tt,f_ttt`;
- both control summary maxima equal the maxima of their row-level values; and
- row count equals root count, while the two tangent gates additionally require
  five rows as the producer does.

### Diagnostic, scan, tail and event-mass duplicates

- diagnostics mesh equals the row mesh; `state_count == cells**3`;
- diagnostics minimum weight and unit-sum error equal values reconstructed from
  the manifest-pinned weights;
- `physical_budget_absolute_error == abs(physical_budget-positive_budget)`;
- scan time-grid fields equal the manifest; saved trace times are the exact
  declared `0.1` subsequence including both endpoints;
- scan checkpoint and stop derivative/survival copies equal their saved-trace
  counterparts;
- tail checkpoints and trace times exactly equal `[35,50,75,100]`;
- tail trace at 35 agrees with the scan endpoint; tail summary extrema and
  adjacent survival-increase maximum are reconstructed exactly from all four
  saved tail checkpoints;
- mass `final_time` equals 100 and final survival equals the tail final value;
- total reaction mass, basin sum, and basin-sum difference are reconstructed;
- for exact five-root topology, the two ratios and all three basin masses are
  reconstructed from root densities/survivals and final survival; otherwise
  all conditionally unavailable ratio/mass fields are exactly null; and
- all recoverable summary-versus-trace inequalities are enforced for the
  coarser scan, while unrecoverable full-scan extrema are explicitly labeled
  as producer-reported.

### PASS/HOLD and evidence

- every one of the 24 mesh gates equals a fresh reconstruction using the
  producer's exact conditional logic;
- all five agreement metrics and gates use the producer's nullable logic;
- overall gate, positive-B flag, status, and evidence exit codes are derived
  only from those reconstructed Booleans;
- all forbidden claim flags remain false in every copy;
- exact evidence schema/stage/hash/status/exit-code checks pass on the same
  immutable byte snapshots; and
- PASS returns zero, legitimate scientific HOLD writes `HOLD_REPRODUCED` and
  returns two, while any malformed/operational inconsistency writes nothing and
  raises or returns a distinct non-scientific failure.

## Safe checks performed

- Original frozen focused suite: **4 passed**.
- Ruff on the original auditor and test: **passed**.
- Round-40 closure suite: **4 failed as intended**, one for each preserved
  fail-open/destructive acceptance case.
- Ruff on the Round-40 test file: **passed**.
- Direct structural-HOLD probe: rejected incorrectly with the five-root error.
- Direct output-alias probe: canonical result bytes were overwritten in an
  isolated temporary directory.
- Direct result-swap probe: PASS was bound to a different unsafe live result.
- No formal execution command, held-out mesh, canonical result, reproducibility
  record, or numerical pin was invoked or modified by this audit.

## Closure gate

A subsequent resolution may change this NO-GO only when all Round-40 tests and
the original four tests pass, dedicated structural-HOLD fixtures cover the
producer's nullable schema, output alias/atomicity and snapshot TOCTOU attacks
are rejected, Ruff passes, and the revised protocol narrows the irreducible
independence claim.  The repaired audit chain must then be frozen under new
hashes before it reads the eventual formal result.
