# Round 80: allocation-cusp v4 independent result-blind pre-run attack

Date: 2026-07-14  
Role: independent adversarial pre-execution audit of the Round-76 v4 repair  
Verdict: **HOLD-PREEXECUTION / NO-GO-65-97**

## 1. Boundary

This audit read only the Round-74 and Round-76 records, the external v4
manifest and frozen protocols, the named producer/auditor sources and unit
tests, and synthetic fixtures.  It did **not** open, create, delete, or execute
any mesh-65/97 result; did not invoke the producer's scientific mode, either
replica mode, or the auditor `main`; and did not edit the manifest, producer,
auditor, protocol, README, or manuscript.

The only numerical execution was the permitted seven-cell explicit-CSR dry
run.  All result/audit attacks used synthetic dictionaries.  The independent
addition is
`code/test_positive_b_allocation_cusp_discovery_round80.py`; its strict
xfails are executable repair contracts, not accepted behavior.

Before and after every audit action, these seven lexical paths were absent:

```text
artifacts/data/positive_b_allocation_cusp_discovery_result.json
artifacts/data/positive_b_allocation_cusp_discovery_reproducibility.json
artifacts/data/.positive_b_allocation_cusp_discovery_result.replica_1.json
artifacts/data/.positive_b_allocation_cusp_discovery_result.replica_2.json
artifacts/data/positive_b_allocation_cusp_discovery_independent_audit.json
artifacts/data/.positive_b_allocation_cusp_discovery_result.json.staging
artifacts/data/.positive_b_allocation_cusp_discovery_reproducibility.json.staging
```

No scientific result existed to inspect.

## 2. Recomputed anchors

| role | repository path | SHA-256 |
|---|---|---|
| external v4 manifest | `artifacts/data/positive_b_allocation_cusp_discovery_manifest.json` | `203b03b3f87656269760dd9283376195c56f9170b400b464c6cdd7b95e2e751f` |
| v4 runner | `code/positive_b_allocation_cusp_discovery.py` | `6c6af2cbec48297179381078a0da59a4ff4312b253ae496bb9b716df07e71a9a` |
| ordinary tests | `code/test_positive_b_allocation_cusp_discovery.py` | `69ff2b7b781977786fed91769c02037b8ccae2868784f221d5c50530e4baafbc` |
| Round-50 tests | `code/test_positive_b_allocation_cusp_discovery_round50.py` | `30ecf71b426705efa2b6728048093d2da5b96d507c89edc43883579dc4847dbb` |
| Round-61 tests | `code/test_positive_b_allocation_cusp_discovery_round61.py` | `90b106485ced34865426d572b01ea59ef98df8c627cf2cf9f77d98a809fb84a3` |
| Round-74 regressions | `code/test_positive_b_allocation_cusp_discovery_round74.py` | `b593da1f93465469f50aacf7f6adc1b68a77a63df95547e9a1b0663c4d1427eb` |
| v4 discovery protocol | `notes/positive_b_allocation_cusp_discovery_protocol.md` | `947db90dca645ce481b1aa2217002500933a8e34ec382c816b5099ec3bc80b64` |
| independent v4 auditor | `code/audit_positive_b_allocation_cusp_discovery_result.py` | `df07fd53b711bb3a2f87d8cb05d0baace3c0cbf3d905aac5c29097b359027b37` |
| auditor tests | `code/test_audit_positive_b_allocation_cusp_discovery_result.py` | `5f4bf7230ca0adb6d42ed2928b643e45860353cf9afd0ebc311fc4ca2819fed8` |
| no-cycle protocol | `notes/positive_b_allocation_cusp_postresult_audit_protocol_v1.md` | `8ccd04f2d8abdfad90ff32998c014faf264d98f09014acb116074523f9d49b39` |
| direct continuum runtime source | `code/continuum_observable_four_patch.py` | `a553092f3d8bbf50fdf0124a3ea36ba32947c3b339cfcc0265a1cd7f6bc2d4da` |
| Round-74 audit | `audits/round_74_allocation_v3_independent_prerun_attack.md` | `ad70a82f8e406e9dae265283ead98d5e33355a3a27a0966d09f2fef7b766c96e` |
| Round-76 repair record | `audits/round_76_allocation_v4_repair_freeze.md` | `29e8e22e9bf673d07d0d8a02061d8d12b411c0085dd1025cbd147256391dbd79` |
| Round-80 attack suite | `code/test_positive_b_allocation_cusp_discovery_round80.py` | `c8609808f483495456c7d1d61be90aed109fe50cffaf794b11a662952a76153e` |

The manifest contains 23 unique report-relative direct pins.  Every pin was
rehash-checked independently and matched.  The manifest is canonical JSON and
its hard-coded hash in the independent auditor matches exactly.

## 3. Decision and exact open count

```text
P0 = 2
P1 = 3
P2 = 1
```

The v4 repair closes much of Round 74, but it is not safe for its first
scientific launch.  Two attacks can put unphysical or unpinned executable
behavior behind a nominal scientific PASS; three more leave central scan
evidence or the expensive replica boundary under-specified.  Therefore:

```text
HOLD-PREEXECUTION
NO-GO-MESH-65
NO-GO-MESH-97
NO PRODUCER/AUDITOR MAIN
AUTHORIZED SCIENTIFIC COMMAND: NONE
```

The manifest hash `203b03...751f` must never be used for mesh 65 or 97.  The
repair requires a new manifest/hash and another independent result-blind audit.

## 4. P0 findings

### P0-1 — outer killed-generator diagnostics remain a physical fail-open

The new finite-volume *factor* contract is real and rejects the original
Round-74 absurd spacings, masses, patch integrals, contact area, quadrature
estimates, and row errors in both producer and auditor.  The surrounding model
contract, however, still checks several killed-generator quantities only for
native `float` type.  Producer lines 3352--3410 and auditor lines 520--581 do
not reconstruct or even require physically necessary signs/order for
`minimum_killing_per_budget`, `maximum_killing_per_budget`,
`analytic_column_operator_trace`, and
`generator_killing_identity_error`.  The law gate at producer lines
1083--1085 and its auditor analogue accept any negative identity "error".

Starting from a complete synthetic PASS control, Round 80 set

```text
minimum_killing_per_budget       = -1e200
maximum_killing_per_budget       = +1e200
analytic_column_operator_trace   = +1e200
generator_killing_identity_error = -1e200
```

while leaving the now-valid factor diagnostics untouched.  Both
`validate_control_contract` and the independent `reconstruct_control` return
`True`; the impossible negative norm also makes the generator-identity gate
pass.  Such a control can enter phase advancement and representative
selection.

Required repair: apply one comprehensive primitive model contract in both
paths.  At minimum require every norm/error to be nonnegative, require
`0 <= minimum_killing_per_budget <= maximum_killing_per_budget`, require the
killed-generator trace sign and independently reconstructable trace/action
identities, and make one failure clear every dependent cusp/fold/scan/control
PASS.  Add finite absurd-value mutations outside `factor_diagnostics`, not
only inside it.

### P0-2 — direct source pins do not bind the Python module that is executed

The direct `continuum_observable_four_patch.py` pin and byte/metadata snapshot
are present and correct.  But `bridge_module`, producer lines 474--480, trusts
`importlib.import_module("continuum_broad_patch_b0_bridge")` and the cached
`sys.modules` object without attesting its resolved `__file__` or bytes.
`subprocess_environment`, lines 5395--5398, copies the entire parent
environment, including `PYTHONPATH`; the frozen keys merely overwrite thread
and seed variables.

The Round-80 unit attack placed a `sitecustomize.py` on an inherited
`PYTHONPATH`.  Before the runner imported its lazy bridge, `sitecustomize`
installed an unpinned module under the pinned module name.  A fresh subprocess
then returned that fake object from `bridge_module` with exit 17.  No pinned
file changed.  Both formal replicas would inherit the same substitution, so
byte identity would not detect it.  A fake bridge has arbitrary control of the
scientific model construction.

Required repair: launch replicas in a demonstrably isolated interpreter and
an allowlisted environment, removing at least `PYTHONPATH`, `PYTHONHOME`, user
site, startup, and injection variables.  Before any scientific construction,
fail if runtime modules are preloaded unexpectedly; load through fixed absolute
paths or attest every imported module's resolved path and exact bytes against
the manifest.  Record and validate the isolated-runtime state.  Directly
pinning a file is insufficient if Python can execute a different module object.

## 5. P1 findings

### P1-1 — the 691-point scan maximum and bracket completeness are not reconstructable

The validators now check the declared spacing, window, and 691-point count,
but neither serializes nor receives the 691 primitive projection rows.  For the
saved trace, producer lines 3601--3624 and auditor lines 876--902 require only
a nonempty, increasing, grid-aligned list with the two endpoints.  The
supposed complete synthetic scientific PASS contains **2 rows**, although
`[0.5,35]` at saved spacing `0.5` requires **70**.

The declared `reference_maximum_density_per_budget` is checked only as a lower
bound on the sparse saved/root values (producer lines 3654--3658; auditor lines
927--931).  Replacing the true synthetic serialized maximum `1.0` by `1e7`
leaves both producer and auditor PASS.  More importantly, no validator can
detect a falsely *small* reference maximum at an unsaved scan point, omitted
sign-changing brackets, or false full-scan minima/maxima.  These quantities
control root eligibility and hence the number of modes, the central scientific
claim.

Required repair: serialize exactly all 691 scalar scan rows, or an equally
strong independently replayable primitive artifact, for every discovery,
control, and comparison scan.  Reconstruct exact times/cardinality, full-scan
maximum/minima, endpoint derivatives, every zero/sign-change bracket,
bracket-index completeness, physical aggregates, and saved 70-row projection
from those primitives.  If this evidence is intentionally not serialized,
remove the claim that the independent auditor reconstructs it and keep the
result below publication-grade discovery evidence.

### P1-2 — negative residual/error values satisfy upper-bound gates

Root reconstruction at producer lines 3492--3495 and auditor lines 779--782
tests only `scaled_root_residual <= threshold`; it never requires a residual
to be nonnegative.  Saved/root state-law rows likewise type-check
`differential_mass_balance_error` without a nonnegative domain, while later
gates use maxima against positive upper bounds.

Round 80 changed an otherwise passing root residual and all saved scan mass
errors to `-1e200`.  Both nested producer and auditor contracts still return
`True`.  This is not merely cosmetic: it lets a failed root become eligible
and can alter topology and modal count.

Required repair: audit every derived `error`, `residual`, `norm`, `absolute_*`,
`mismatch`, drift, and singular-value field in every PASS and HOLD schema.
Require its mathematical domain before applying thresholds; reconstruct
derived values where primitives exist.  Add negative finite mutations at cusp,
fold, root, scan, tail, model, comparison, and evidence levels.

### P1-3 — a staging collision after replica one still wastes replica two

The parent checks both deterministic promotion staging paths once before the
loop (producer lines 5261--5262).  After each child it rechecks pinned files and,
for the real freeze, the five science paths (lines 5291--5306), but not the two
promotion staging paths.  `promote_replica_bytes` discovers a newly created
stage only after both replicas finish.

The synthetic attack let child one write its declared valid HOLD result and a
foreign canonical stage.  The parent executed child two and only then failed
at promotion; the foreign stage was preserved.  This is fail-closed for final
publication but violates the required zero/one-child abort boundary and can
waste the second expensive run.

Required repair: recheck both promotion stages and the exact five-path set
after every child and immediately before launching the next child, parsing
replicas, and promotion.  Preserve all unowned collisions.  Add separate
zero-call and one-call canonical/evidence-stage regressions for the real and
unit paths.

## 6. P2 finding

### P2-1 — auditor-main rollback is not ownership-scoped under an output race

The append-only writer itself tracks `created_output` and deletes only an
output it owns (auditor lines 2698--2740).  The surrounding `main`, however,
has a broader exception handler at lines 2797--2804 that unlinks `OUTPUT`
whenever it exists.  If an unowned audit output appears after the initial
absence check but before `write_append_only`, the writer raises correctly and
`main` then deletes the foreign file.

This attack requires a concurrent writer, which the protocol forbids, so it is
P2 rather than an additional launch-blocking P1.  It still contradicts the
claimed ownership discipline and is relevant on a synchronized filesystem.
The auditor main was not executed in this round; this is a source-level TOCTOU
finding.

Required hardening: carry an explicit ownership token/flag across the whole
publish transaction and roll back only an inode created and still owned by
that invocation.  Add a unit-level collision injection without invoking the
scientific auditor path.

## 7. Round-74 replay matrix

| Round-74 obligation | Round-80 result |
|---|---|
| finite-volume spacing/normalization/contact/error factors | **closed for the exact Round-74 mutation**; reopened outside the factor subobject by P0-1 |
| scan spacing, window, point count, endpoints | **closed** |
| root type, flags, ordered reasons, duplicates, separation, eligible subset | **closed for serialized roots**; negative norms and full-scan completeness remain open |
| mesh-97 cusp to phase-centre cross-link | **closed in producer and auditor** |
| honest nonzero centre under `5e-13` tolerance | **closed in producer and auditor** |
| exact native bool/int/float identities | **closed for tested top-level, preflight, candidate, root, count, and flag aliases** |
| direct runtime source included in snapshot | **closed as a file snapshot**; executable import binding remains open in P0-2 |
| stale promotion stages before first child | **closed with zero calls**; after-child boundary remains open in P1-3 |
| five-path collision and append-only helper | **closed for preexisting collisions and declared no-concurrent-writer boundary** |
| no-cycle architecture | **closed**; auditor does not import producer and hard-coded manifest hash matches |
| negative claim flags and low-mesh-only release implication | **closed in tested schemas**; no claim escalation mutation passed |

## 8. Permitted verification

The complete result-blind unit command covered the ordinary, Round-50,
Round-61, Stage-A, independent-auditor, converted Round-74, and new Round-80
suites:

```text
collected:      88
passed:         83
strict xfailed: 5 (the five P0/P1 executable open contracts above)
XPASS:          0
```

The new test file passed Ruff format, Ruff lint, and `py_compile` checks.

Two independent CLI calls used only:

```text
--algebra-dry-run --cells 7
--expected-manifest-sha256 203b03b3f87656269760dd9283376195c56f9170b400b464c6cdd7b95e2e751f
```

Both returned zero with empty stderr and byte-identical stdout:

```text
stdout bytes:   1061
stdout SHA-256: 2165a4bf79bb74e62197cdb0978aa00b47063514eed04b8415d422585a97eca4
```

No mesh-65/97 model, producer main, replica mode, auditor main, result, evidence,
or audit artifact was executed or read.

## 9. Repair order and release boundary

The minimum v5 sequence is:

1. isolate and attest the actual Python import graph and subprocess environment;
2. close outer model and every nonnegative norm/error domain in both validators;
3. serialize/reconstruct complete 691-point scan primitives and exact bracket set;
4. recheck promotion stages after child one and ownership-scope auditor rollback;
5. freeze a new external manifest/hash, convert all five xfails to ordinary
   regressions, and commission a fresh independent result-blind audit.

Until all five strict xfails become ordinary passes under a new hash, neither
mesh 65 nor mesh 97 is authorized.  No outcome-informed tuning is permitted.
