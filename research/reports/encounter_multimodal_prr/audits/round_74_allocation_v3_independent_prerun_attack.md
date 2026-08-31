# Round 74: allocation-cusp v3 independent result-blind pre-run attack

Date: 2026-07-14  
Role: independent adversarial pre-execution audit of the Round-64 v3 freeze  
Verdict: **HOLD-PREEXECUTION / NO-GO-65-97**

## 1. Scope and non-execution boundary

This round independently attacked the complete Round-64 allocation-cusp v3
package before its first scientific execution.  It read the external manifest,
runner, ordinary/Round-50/Round-61 tests, discovery protocol, independent
post-result auditor and tests, no-cycle protocol, and the runtime-local import
closure reached by the finite-volume bridge.

It did **not** run, open, generate, or delete any mesh-65/97 scientific result,
did not construct any numerical model above seven cells, and did not invoke the
post-result auditor entrypoint.  The only numerical execution was the permitted
seven-cell explicit-CSR algebra smoke test.  No v3 producer, manifest, protocol,
auditor, threshold, or design file was edited.

The only repository additions from this independent round are this report and
the result-blind mutation suite
`code/test_positive_b_allocation_cusp_discovery_round74.py`.  Seven strict
xfails in that suite are executable open contracts.  They are not accepted
behaviour and must become ordinary passing regressions in a newly hashed v4
package before any scientific launch.

## 2. Audited anchors

| role | repository path | SHA-256 |
|---|---|---|
| v3 external manifest | `artifacts/data/positive_b_allocation_cusp_discovery_manifest.json` | `ef65491f9d169b672ffaf509399728dd21385aa73c85b8c9ba931b64a9dfd98f` |
| v3 discovery runner | `code/positive_b_allocation_cusp_discovery.py` | `cef4d616520caefeba7ff437275500bdb3387cd9d79e38d9876a386d11c98bc4` |
| ordinary runner tests | `code/test_positive_b_allocation_cusp_discovery.py` | `69ff2b7b781977786fed91769c02037b8ccae2868784f221d5c50530e4baafbc` |
| Round-50 regressions | `code/test_positive_b_allocation_cusp_discovery_round50.py` | `30ecf71b426705efa2b6728048093d2da5b96d507c89edc43883579dc4847dbb` |
| Round-61 regressions | `code/test_positive_b_allocation_cusp_discovery_round61.py` | `90b106485ced34865426d572b01ea59ef98df8c627cf2cf9f77d98a809fb84a3` |
| discovery protocol v3 | `notes/positive_b_allocation_cusp_discovery_protocol.md` | `5f852cfd3d5342e60e8401cb486d26f8424a367f13a0dd2dd9d0b0e2ef80eee1` |
| mandatory Round-61 attack | `audits/round_61_allocation_v2_independent_prerun_attack.md` | `db1137c980113e09c5dba54efdad65903febb4c0c8b81e532743f890b11b48e0` |
| Round-64 v3 freeze record | `audits/round_64_allocation_v3_repair_freeze.md` | `49ab0958f94b37696a167c3fb18ae64c737c95ab03a17c559029cda4a6d75be8` |
| independent v3 auditor | `code/audit_positive_b_allocation_cusp_discovery_result.py` | `6b1cf7b8ca996161a59219b1f5f5be9cfc9c538ea09683a715084e017d057f4b` |
| independent auditor tests | `code/test_audit_positive_b_allocation_cusp_discovery_result.py` | `b8103510902ef2b5cb8558ff329ead8a811dc1bcfc5596d685a3dc0a2b783d3e` |
| no-cycle post-result protocol | `notes/positive_b_allocation_cusp_postresult_audit_protocol_v1.md` | `ad184fc3c8f586e5ce44d65a5bf6b5dc77bfdccaf471895280783d31a9837bc6` |
| B=0 bridge manifest | `artifacts/data/continuum_broad_patch_b0_bridge_manifest.json` | `263d4bd5e95f4cf477916948f2e4bbf3cd99066ac9dc9a9ab5726f2030a6f1e8` |
| runtime-local continuum dependency | `code/continuum_observable_four_patch.py` | `a553092f3d8bbf50fdf0124a3ea36ba32947c3b339cfcc0265a1cd7f6bc2d4da` |
| Round-74 independent mutation suite | `code/test_positive_b_allocation_cusp_discovery_round74.py` | `cd22d25ddfb613ba67f86830eb086f02620efc1ff93de9e85fee9973526ade1d` |

All 20 direct v3 pin contents matched the external manifest at audit time.
The manifest and all Round-64 anchors above recomputed exactly.  That observed
snapshot does not repair the incomplete transitive runtime pin closure described
in P1-5 below.

## 3. Required absence boundary

The following five lexical paths were checked only for existence and were
absent before and after every audit action:

```text
artifacts/data/positive_b_allocation_cusp_discovery_result.json
artifacts/data/positive_b_allocation_cusp_discovery_reproducibility.json
artifacts/data/.positive_b_allocation_cusp_discovery_result.replica_1.json
artifacts/data/.positive_b_allocation_cusp_discovery_result.replica_2.json
artifacts/data/positive_b_allocation_cusp_discovery_independent_audit.json
```

No scientific result content was available to, or inspected by, this audit.

## 4. Executive decision and open count

Round 64 closes the enumerated Round-61 defects substantially: complete scan
law rows, remote-root lineage, recursive schemas, canonical promotion,
lexical stable reads, two-process reproducibility, and once-only independent
audit output all survived direct attacks.  The v3 package is nevertheless not
safe for its first mesh-65/97 execution.

Open count:

```text
P0 = 1
P1 = 6
P2 = 0
```

The P0 is a scientific fail-open: arbitrarily invalid finite-volume factor
diagnostics can still satisfy every factor gate in both producer and auditor.
The P1 items can either certify semantically false scan/phase records, reject an
honest nonzero phase centre after the expensive run, admit Python numeric type
aliases, leave executable local code outside the direct execution snapshot, or
delay a stale-staging abort until both replicas have run.

Therefore external manifest SHA-256 `ef6549...d98f` is permanently
**not authorized** for mesh 65 or 97.  Repair requires a v4 manifest and a new
independent result-blind pre-run audit.  No scientific threshold may be tuned
from a mesh-65/97 outcome because no such outcome is authorized yet.

## 5. Round-61 replay and v3 closure matrix

| obligation | Round-74 disposition |
|---|---|
| full-scan positivity, survival, state, monotonicity, mass balance, and all-root coverage | **closed for serialized rows**; negative/full-scan and rejected-root mutations fail in the ordinary Round-61 suite |
| signed remote-pair identity and continuation lineage | **closed for the frozen lineage contract**; birth, replacement, crossing, and excessive drift regressions pass |
| exact recursive PASS/HOLD/control/phase schemas | **materially closed but reopened at semantic/type edges**; seven newly isolated contracts remain below |
| complete phase evaluation before representative claims | **closed**; missing eligible evaluations clear representatives and force HOLD |
| result/evidence canonical two-replica promotion | **closed after replica completion**; byte mismatch, status/exit mismatch, rollback, and post-replace checks pass |
| lexical symlink and read-time TOCTOU resistance | **closed for directly snapshotted paths**; symlink input and replace-after-open mutations fail closed |
| exact claim scope, limitations, evidence timing, software, and negative flags | **closed in tested schemas** |
| independent no-cycle auditor and append-only output | **closed at the tested boundary**; the audit writer rejects a second write without changing first bytes |
| complete executable dependency freeze | **open**; one runtime-local import is only transitively described by a nested manifest |
| factor/model validation claimed by Round 64 | **open and P0**; finiteness is not scientific validity |

## 6. P0 finding

### P0-1 — the finite-volume factor/model gate is constant true

The producer computes and serializes factor diagnostics including grid
spacings, four patch integrals, midpoint and relative initial masses, contact
area and its exact value, quadrature-error estimates, and generator row-sum
errors.  These quantities are part of the numerical model on which every cusp,
fold, root, basin, and modality conclusion depends.

However:

- producer `law_gate_results`, lines 938--979, sets
  `finite_factor_diagnostics: True` unconditionally;
- producer `validate_model_diagnostic_contract`, lines 3223--3278, checks only
  schemas/types plus selected outer identities, not the factor identities or
  error bounds; and
- auditor `reconstruct_law_gates`, lines 589--620, independently repeats the
  same constant `True` rather than reconstructing factor validity.

The Round-74 mutation replaced a synthetically valid PASS control by:

```text
all three spacings                         = 9.0
all four patch integrals                   = 2.0
midpoint initial mass                      = 2.0
relative initial mass                      = 3.0
contact area                               = 4.0
both quadrature estimates, contact error,
and both generator row errors              = 1.0e9
```

All values are finite and schema-correct.  Both the unmodified producer control
validator and the independent auditor control reconstruction accept them.  A
malformed finite-volume discretization can therefore receive
`PASS_CONTROL_EVALUATION`, propagate into phase selection, and be certified by
the nominally independent audit.

This is P0 rather than P1 because the defect permits a false scientific PASS,
not merely weak provenance.  `finite` does not imply normalized, conservative,
or a discretization of the frozen physical model.

**Required v4 repair:** freeze and independently reconstruct a factor contract.
At minimum it must derive all three spacings from frozen domains and `cells`,
require each patch integral and each initial factor mass to equal one within an
explicit result-blind tolerance, require contact area to agree with
`pi * contact_radius^2`, bound both generator row errors, and require reported
quadrature error estimates to be finite, nonnegative, conservative, and below
frozen tolerances.  Promote the bridge's currently nested
`maximum_mass_or_conservation_error` or a separately justified preregistered
tolerance into the allocation manifest; do not infer a tolerance from the
future mesh-65/97 values.  Producer and auditor must reconstruct the contract
from primitive manifest values, and one failed factor must make every dependent
scientific gate false.

## 7. P1 findings

### P1-1 — scan and root semantics trust self-reported flags

Producer `validate_root_contract`, lines 3293--3336, checks root field types and
defines `eligible` as the conjunction of the root's own booleans.  It does not
reconstruct maximum/minimum type from curvature, density/residual/curvature
eligibility from frozen thresholds, duplicate/separation status from the root
sequence, or the exact reason list.  Producer `validate_scan_contract`, lines
3339--3428, accepts any positive spacing and trusts
`endpoint_signs_passed`; the auditor repeats these omissions in `_root_contract`
and `reconstruct_scan`, lines 623--725.

Both producer and auditor accept each of these independent mutations:

```text
root type = "maximum" with scaled_curvature = +1
endpoint derivatives = [-1,+1] with endpoint_signs_passed = true
scan spacing = 1.0 instead of the frozen 0.05
```

Moreover, relative density eligibility cannot be independently reconstructed
because the full-scan reference maximum density used by the rule is not
serialized.

**Required v4 repair:** freeze exact scan spacing/cardinality/times; reconstruct
endpoint signs; reconstruct root type, all eligibility booleans, reason lists,
duplicates, separation, and topology from primitive fields and neighbouring
roots.  Serialize the full-scan reference maximum density (or sufficient
primitive data to derive it), and require producer/auditor agreement.

### P1-2 — phase-search centre is not linked to the mesh-97 cusp

Producer `validate_phase_contract(phase, cells=65)`, line 4202, receives no
expected cusp theta.  Auditor `reconstruct_phase(phase, manifest)`, line 1816,
also has no mesh-97 cusp argument.  Both prove only that candidates share some
internally consistent centre.

Round 74 shifted the complete synthetic PASS phase centre to
`(2^-8,-2^-8)`, updated every candidate/control theta, physical weight, and
weight diagnostic consistently, but left the serialized mesh-97 cusp theta at
`(0,0)`.  The full producer result validator and independent auditor both
accepted the false PASS.

**Required v4 repair:** serialize a phase-centre theta and pass the actual
mesh-97 cusp theta into both validators.  Reconstruct every candidate as
`theta_cusp_97 + radius * direction`, its four physical weights, eligibility,
and every embedded mesh-65/97 control from that common centre.  A disconnected
phase cloud is HOLD.

### P1-3 — exact centre equality can reject honest nonzero centres

The producer recovers a centre by subtracting `radius * direction` from each
candidate and compares recovered arrays using `np.array_equal`, lines
4264--4268.  This is not roundoff-stable.  For the honest frozen candidate
generator centred at `(0.01,-0.01)`, the 32 recovered centres occupy 14 distinct
floating-point bit patterns, with maximum absolute discrepancy approximately
`8.67e-18`; the unmodified validator rejects the otherwise valid HOLD phase.

The actual positive-`B` cusp centre is unknown and was not computed in this
audit.  If it is nonzero, this defect can waste both expensive replicas and
leave no promotable result even when the producer generated its own candidates
correctly.

**Required v4 repair:** avoid subtraction-based exact equality.  Validate each
candidate directly against the expected mesh-97 cusp-centred formula under one
explicit frozen absolute/relative tolerance, while retaining exact native
schema checks.  Use the same rule independently in the auditor.

### P1-4 — Python bool/int and int/float aliases bypass native schemas

Several fields use value equality without exact native type checks.  Producer
preflight lines 4542--4565 and auditor lines 2168--2187 accept:

```text
mesh        = [7.0, 7.0, 7.0]
state_count = 343.0
```

Both full validators also accept a complete synthetic PASS after every
occurrence of candidate index `1` is changed to boolean `true`, because in
Python `True == 1` and hashes identically in sets/dictionaries.

**Required v4 repair:** use `type(value) is int`, `type(value) is float`, and
`type(value) is bool` consistently for every mesh coordinate, state count,
candidate/root/acceptance index, schema/version/count, replica code, and other
identifier.  Then check value/range/uniqueness.  Mirror the exact contract in
the auditor and add alias mutations across nested PASS and HOLD variants.

### P1-5 — direct execution snapshot omits a runtime-local dependency

The allocation manifest directly pins `continuum_broad_patch_b0_bridge.py`,
`continuum_weak_budget_design.py`, and `continuum_g1_smoke.py`, plus the B=0
bridge manifest.  But the pinned bridge producer imports
`continuum_observable_four_patch.py` at module import time (bridge line 24) and
uses its `PhysicalParameters` in `parameters_from_manifest` (lines 101--123).

`continuum_observable_four_patch.py` is recorded only inside the nested B=0
bridge manifest.  Allocation `capture_complete_freeze_snapshot`, lines
598--612, iterates the allocation manifest's direct `PIN_PATHS`; it does not
recursively parse and snapshot the nested manifest's pins.  The current file
hash does match the nested record (`a55309...d4da`), so this is not an observed
stale file.  It is an execution-boundary defect: drift after this audit but
before import would not be part of the allocation run's complete initial/final
snapshot.

**Required v4 repair:** directly pin
`code/continuum_observable_four_patch.py` in the allocation manifest, or move
the finite-volume runtime interface into a minimal directly pinned module.
Snapshot every runtime-local import actually executed by the lazy bridge load.
A nested manifest hash alone is insufficient unless its pin closure is
recursively captured and revalidated.

### P1-6 — stale promotion staging aborts only after both replicas

The five-path pre-run boundary omits the two deterministic staging names used
by `promote_replica_bytes`: `.canonical.json.staging` and
`.evidence.json.staging` for the selected outputs.  `run_replica_commands`,
lines 4891--5026, launches both replica commands before promotion checks those
staging paths.

In a fake, science-free harness, a foreign pre-existing canonical staging file
was preserved and eventually rejected, which is fail-closed for publication.
However, both fake replica commands had already run (`calls = 2`).  In the real
workflow this can waste both mesh-65/97 executions before an entirely local,
deterministic precondition failure.

**Required v4 repair:** derive both promotion staging paths before any child is
spawned and require them lexically absent together with replica, canonical, and
evidence paths.  Preserve the current no-delete rule for foreign paths.  Add a
regression requiring zero child calls when either staging path exists.

## 8. Attacks that passed

The following attacks closed correctly and are not findings:

- terminal homotopy budget, time trust box, allocation-chart weights, physical
  family, representative gate, and direct-pin hash mutations are rejected by
  manifest validation;
- full result validation rejects a wrong terminal budget, cusp outside the
  trust box, physical weights inconsistent with theta, and a tail row violating
  `density = B * density_per_budget`;
- recursive nonfinite checks reject `NaN`, `+Inf`, and `-Inf` in producer and
  auditor; signed negative zero cannot satisfy a strict positive-density gate;
- lexical symlink inputs are rejected by producer and auditor;
- a simulated replace-after-open race is detected by stable descriptor and
  lexical metadata comparison;
- an undeclared pre-existing output is not deleted by the absence helper;
- the independent audit append-only writer rejects a second write and leaves
  the first bytes unchanged; the auditor `main` entrypoint was never called;
- the seven-cell algebra smoke is deterministic and declares no scientific
  mesh, no discovery PASS, and explicit HOLD-SCIENCE; and
- every existing Round-50 and Round-61 regression remains green.

## 9. Verification executed

The final result-blind code checks were:

```text
ruff format --check: 9 files already formatted
ruff check:           all checks passed
py_compile:           runner, auditor, and Round-74 suite passed
pytest collection:    71 tests
pytest result:        64 passed, 7 strict xfailed
```

The seven strict xfails correspond one-to-one to P0-1 and P1-1 through P1-6.
No unexpected failure or xpass occurred.

Two permitted `--algebra-dry-run --cells 7` CLI executions produced
byte-identical output:

```text
return code:     0, 0
stdout bytes:    1061 per run
stdout SHA-256:  599faf2dacf08b13f4817bed70996f43553d048189e4fcd97d856fa3e8f8d69d
stderr bytes:    0, 0
scientific mesh: none
```

The five forbidden scientific paths remained lexically absent afterward.

## 10. Minimum v4 repair and refreeze sequence

Before any mesh-65/97 command, the implementer must:

1. add a frozen, independently reconstructable factor/model-validity contract
   and convert the P0 xfail to an ordinary passing regression;
2. reconstruct exact scan/root semantics, including the frozen scan grid and
   the reference density needed for eligibility;
3. cross-link phase generation to the mesh-97 cusp and use a frozen
   roundoff-stable direct formula;
4. close all exact native numeric types in producer and auditor;
5. directly snapshot the complete runtime-local import graph;
6. reject both promotion staging paths before the first child process;
7. convert all seven Round-74 xfails into pinned ordinary regressions;
8. update protocol and no-cycle audit contract without changing scientific
   thresholds from results;
9. issue a new external manifest hash pinning the repaired runner, tests,
   protocol, Round-74 report, Round-74 regressions, and complete runtime closure;
   and
10. obtain another independent result-blind pre-run attack of that exact hash.

Only after all ten items close with `P0 = P1 = 0` may an independent auditor
consider authorizing the two frozen discovery replicas.  Such authorization
would still cover bounded finite-window discovery only; it would not establish
continuum convergence, uniqueness, structural stability, an unbounded-domain
limit, or a manuscript-level claim.

## 11. Authorization state

```text
HOLD-ALLOCATION-SCIENCE
NO-GO-MESH-65
NO-GO-MESH-97
NO POST-RESULT AUDIT
AUTHORIZED-SCIENTIFIC-COMMAND: NONE
```

This verdict is result-blind.  It preserves the scientific value of the planned
allocation-cusp discovery by preventing an invalid model, disconnected phase
cloud, semantically false root record, or incompletely frozen runtime from
becoming manuscript evidence.
