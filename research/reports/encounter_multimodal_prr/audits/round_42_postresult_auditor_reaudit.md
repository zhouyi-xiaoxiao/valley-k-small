# Round 42 independent post-result auditor re-audit

Attack date: 2026-07-14  
Decision snapshot: repaired auditor SHA-256
`abeacd47cacd6455dc4488a8644371e924002973710e5c4749f39f427b864cd8`  
Numerical manifest audited for this round: operational-erratum v2 SHA-256
`955e59bf333b5fd70e415a53dc26becae9c7a34c5d40f1230c96b1dab8f5677c`

## Decision

**NO-GO for running or publishing the independent result audit. P0: 1, P1: 6,
P2: 1.**

The v2 numerical-producer erratum itself is **GO as a serialization-only
operational repair** on the evidence available in the repository.  This does
not turn the numerical experiment into a PASS or HOLD and does not weaken its
scientific freeze.  The independent auditor remains NO-GO until every Round-42
attack passes and a revised audit protocol is frozen.

No canonical formal result or reproducibility-evidence JSON was opened,
parsed, copied, or modified in this review.  Every forged result and evidence
record was generated below `pytest`'s isolated `tmp_path`.  The producer,
numerical tests, numerical manifest, and numerical protocols were not edited.

## Operational-erratum v2 review

The first run's failure mode is credibly operational: the erratum records a
NumPy `bool_` rejected by canonical serialization before either canonical
output existed.  The v2 normalizer accepts exactly native `bool` and
`numpy.bool_`, converts only the latter, rejects integers, floats, strings and
nulls, and is applied to tail, per-mesh and two-mesh gate mappings
(`positive_b_broad_four_slab.py:277-289,893-904,1022,1212`).

Checks supporting the serialization-only classification:

- the complete current numerical focused suite reports **16 passed**;
- Ruff check and Ruff format check pass for the producer and numerical tests;
- manifest-validation tests still compare the held-out meshes, budget,
  weights, physical parameters, scan, root thresholds, tail thresholds,
  event-mass thresholds, agreement thresholds and claim boundaries against
  the same frozen producer constants;
- a pre-repair cached test code object from 2026-07-13 23:06 contains 20 test
  functions, while the v2 source contains those 20 plus exactly the new
  Boolean-normalization regression; among the pre-existing function bodies,
  only the manifest pin-set assertion changes, from the old 13 roles to the
  new 14 roles including `operational_erratum`; and
- current pins agree with the erratum: producer `adb9434d...`, tests
  `d60e837c...`, unchanged numerical protocol `f25a8107...`, and erratum
  `9843b323...`.

The available checkout does not retain the complete v1 producer source, so a
literal source-to-source diff against SHA `0c70ffb4...` cannot be reconstructed
locally.  The unchanged scientific-contract tests plus exact-type normalizer,
call-site inspection, new regression and recorded pre-repair hashes are enough
for a **GO-ERRATUM** decision, but this limitation should remain in the
provenance note.

## Findings

### P0 — An impossible root survival can receive an independent PASS

The repaired auditor checks that root survivals decrease from root to root
(`audit_positive_b_broad_four_slab_result.py:608-616`) and that the saved trace
contains a derivative sign bracket (`:623-637`).  It never checks that a root
survival is in `[0,1]` or, when the reported survival-monotonicity gate passes,
that it lies between the two saved-trace survival values bracketing the same
root time.

Round-42 changes only the first root survival from `0.9895` to `2.0`, leaves its
saved-trace bracket near `0.99`, writes a new canonical result, and consistently
rebinds both evidence hashes.  All reported gates remain true.  The auditor
returns:

```text
PASS_INDEPENDENT_RECONSTRUCTION
scientific_result_passed = true
```

This is a recoverable raw-versus-trace contradiction, not an irreducible
semigroup limitation.  A survival probability of two is impossible, and the
saved values already expose the inconsistency.  It must therefore be rejected
as malformed rather than certified as a scientific PASS.

Required closure:

1. require every saved, root and tail survival to be finite and within a
   documented numerical tolerance of `[0,1]`;
2. when `survival_monotone_through_final_time` is true, require each root
   survival to lie between its saved-trace bracketing survivals, up to a
   tolerance derived explicitly from the frozen numerical tolerance rather
   than an arbitrary loose constant; and
3. add both a gross `S=2` attack and small just-outside-bracket attacks, while
   preserving valid structural and threshold HOLD fixtures.

### P1 — The auditor still points at the obsolete v1 manifest

`EXPECTED_MANIFEST_SHA256` remains `01b435c8...`
(`audit_positive_b_broad_four_slab_result.py:28`) while the documented v2
manifest is `955e59bf...`.  Consequently the five original auditor tests all
stop at `manifest hash changed`; the four Round-40 rejection tests pass only
vacuously or through their own early rejection paths.  No real v2 result can be
audited by this file.

Round-42 monkeypatches only the in-memory expected hash to the explicit v2
anchor so that downstream logic can be attacked.  This is test scaffolding,
not a proposed production workaround.

Required closure: update the embedded anchor deliberately only as part of the
post-Round-42 repaired auditor freeze, then record the repaired auditor, all
three auditor test files and the revised audit protocol under new hashes.

### P1 — Nested reproducibility fields accept Boolean/integer type aliases

The nested reproducibility declaration is compared as a Python dictionary
(`audit...py:1080-1087`).  Python equality treats `2.0 == 2` and `1 == True`.
Round-42 replaces

```json
{
  "independent_full_processes_required": 2,
  "canonical_result_requires_external_byte_comparison": true
}
```

by the type-invalid values `2.0` and `1`.  After the evidence hashes are
rebound, the auditor still returns PASS.

Required closure: exact-key validation followed by `require_int(...)=2` and
identity validation `value is True`.  Apply the same exact JSON type contract
recursively to every result copy of manifest data; never use ordinary Python
container equality as a type validator.

### P1 — Unstructured factor diagnostics accept a forbidden promotion alias

All diagnostics have an exact outer key set, but `factor_diagnostics` is
required only to be a dictionary (`audit...py:442-451`).  Round-42 inserts

```json
"factor_diagnostics": {"independent_solver_verified": true}
```

into one mesh.  The top-level claim flag remains false, the evidence is
consistently rehashed, and the auditor returns PASS.  A downstream recursive
consumer can now see contradictory claim-bearing aliases inside an
auditor-accepted result.

Required closure: enforce the frozen factor-diagnostic schema if it is stable,
and independently reject recursively nested aliases of every forbidden
promotion/claim key outside their one authorized exact location.  This check
must include dictionaries nested inside lists and must use exact spelling and
type checks, not truthiness.

### P1 — The final commit still has an input-identity TOCTOU window

`atomic_publish()` rehashes snapshots and then calls `os.replace()`
(`audit...py:1237-1238`).  Round-42 injects an input replacement inside the
replace boundary, after the final precheck but before publication.  The audit
is published and no error is raised even though the live input no longer has
the audited hash.

Required closure: define commit-time input identity rather than merely a
pre-commit check.  Keep audited descriptors/inode identities or a cooperative
publication lock, check content identities immediately before and immediately
after replacement, and roll back the audit on any mismatch.  The post-commit
check and rollback path must be exercised by an injected swap test.  The
protocol must state the residual assumption if non-cooperating writers cannot
be locked out completely.

### P1 — Directory-fsync failure destroys the prior audit despite raising

The new audit replaces the target before the directory is fsynced
(`audit...py:1238-1243`).  If directory `fsync` raises, the function propagates
an operational error, but the old audit has already been lost and the new bytes
remain visible.  The staging cleanup in `finally` cannot restore the prior
target.

Round-42 starts with `prior audit`, injects failure on the second `fsync`, and
observes the target containing the new canonical payload after the exception.
This contradicts the Round-40 closure requirement and the audit protocol's
claim that an operational failure writes no replacement.

Required closure: use a same-directory backup/rollback transaction.  Preserve
whether the target was absent and its prior bytes/inode; on any exception after
replacement, atomically restore the old target or remove the newly created
one, fsync the directory, and only then propagate the error.  Add tests for
file-fsync failure, replace failure, directory-fsync failure with a prior
target, and directory-fsync failure with no prior target.

### P1 — The frozen post-result protocol is stale and still overstates independence

The protocol still pins the v1 manifest and pre-Round-40 auditor/tests, says
there are thirteen source pins, and says the auditor reconstructs every mesh
gate and the two-process byte-identity evidence
(`positive_b_postresult_audit_protocol.md:9-24,31-41`).  The repaired audit
output narrows four full-scan extrema, but other gates still rely on
producer-reported scalars without underlying states in the JSON, including the
direct-versus-tangent state norm, generator identity residual, root mass-
balance residuals and root minimum-state components.  The two subprocesses
also remain evidence-record claims rather than executions observed by this
auditor.

Required closure: issue a v2 post-result audit protocol that separates:

- exact schema/provenance checks;
- quantities algebraically reconstructed from multiple saved JSON fields;
- Boolean decisions re-evaluated from producer-reported certified extrema or
  residuals whose underlying state vectors are absent; and
- the internally consistent two-process evidence record, explicitly not
  independently observed execution.

It must cite the v2 numerical manifest and 14 pins, state the rollback and
commit-time identity semantics, and contain the new repaired auditor/test
hashes.

### P2 — The auditor self-hash is not part of the publication snapshot

The payload computes `auditor_sha256` from `HERE`, but the returned snapshot
map contains the result, evidence, manifest and manifest pins, not `HERE`.
`atomic_publish()` puts `HERE` only in the path-alias set.  A concurrent source
change can therefore make the recorded self-hash describe bytes different from
the code whose execution produced the payload.

Required closure: include the auditor source hash in immutable publication
snapshots and exercise a source-swap rejection test.  The external revised
protocol hash remains the stronger release anchor.

## Defences that survived Round 42

- A structurally legitimate HOLD on only one of the two meshes returns
  `HOLD_REPRODUCED`; it is not rejected by a five-root-only schema.
- `NaN`, `Infinity` and `-Infinity` inserted directly into otherwise JSON-like
  bytes are rejected before scientific reconstruction.
- Direct raw-versus-scaled root-jet contradictions from Round 40 are rejected.
- Unknown top-level and evidence fields, forged replica hashes and unsafe
  top-level claim flags are rejected.
- A canonical output path that aliases a protected input is rejected without
  modifying the input.
- Exact conditional nulls for structural HOLD, root/control row relationships,
  tail summaries and algebraic event-mass partitions remain materially
  stronger than the pre-Round-40 auditor.

## Reproducible checks

New attack file:

```text
code/test_audit_positive_b_broad_four_slab_result_round42.py
SHA-256 603aee3b506f1fcf348a06f8f784be4144eb65965e891861c498697743af237f
```

Commands and results:

```bash
.venv/bin/python -m pytest -q \
  research/reports/encounter_multimodal_prr/code/test_positive_b_broad_four_slab.py
# 16 passed

.venv/bin/python -m pytest -q \
  research/reports/encounter_multimodal_prr/code/test_audit_positive_b_broad_four_slab_result.py \
  research/reports/encounter_multimodal_prr/code/test_audit_positive_b_broad_four_slab_result_round40.py
# 5 failed at obsolete manifest pin, 4 passed through rejection paths

.venv/bin/python -m pytest -q \
  research/reports/encounter_multimodal_prr/code/test_audit_positive_b_broad_four_slab_result_round42.py
# 5 failed, 6 passed
```

The five Round-42 failures are exactly the nested type-alias acceptance,
recursive claim-alias acceptance, impossible root-survival acceptance,
directory-fsync rollback failure and final input-swap acceptance.  Ruff check
and Ruff format check pass for the new attack file after formatting; the
numerical producer and tests also pass both checks.

## Closure gate

A later resolution may change this NO-GO only when:

1. all original, Round-40 and Round-42 tests run against the actual v2 anchor
   without monkeypatching and pass;
2. the five demonstrated fail-open/transaction attacks are rejected;
3. source and input identities are protected through the publication commit,
   with tested rollback for every caught post-replace failure;
4. valid zero-root, one-mesh structural, nonalternating, and threshold HOLD
   fixtures still return `HOLD_REPRODUCED`;
5. the honest independence boundary is frozen in a revised protocol; and
6. the repaired auditor, all test files and revised protocol are rehashed
   before any canonical formal output is opened by the auditor.

Until then, do not create or cite
`positive_b_broad_four_slab_independent_audit.json`.  This NO-GO applies to the
independent-audit artifact, not to the scientific status of the numerical run,
which this review intentionally did not inspect.
