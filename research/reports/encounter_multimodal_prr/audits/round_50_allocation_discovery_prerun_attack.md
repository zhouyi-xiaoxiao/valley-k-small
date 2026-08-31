# Round 50: allocation-cusp discovery result-blind pre-run attack

Date: 2026-07-14  
Role: independent, result-blind pre-execution attack on the Round-47 mesh-65/97 freeze  
Verdict: **HOLD-PREEXECUTION / NO-GO-65-97**

## 1. Scope and non-execution boundary

This round audited, without changing them,

- `code/positive_b_allocation_cusp_discovery.py`;
- `code/test_positive_b_allocation_cusp_discovery.py`;
- `notes/positive_b_allocation_cusp_discovery_protocol.md`;
- `artifacts/data/positive_b_allocation_cusp_discovery_manifest.json`;
- the pinned Stage-A scaffold, promotion design, and Round-36/Round-44 audits; and
- the frozen positive-`B` point **manifest/protocol/source hashes only**, solely to
  compare the family definition.

No allocation-cusp calculation on mesh 65 or 97 was started.  No cusp, fold,
remote-pair, candidate-control, or representative value on either scientific
mesh was read or produced.  The only numerical runner execution was the
explicit seven-cell algebra dry run.  At the end of the attack, all four
allocation-discovery output/replica paths were absent.

The Round-50 file
`code/test_positive_b_allocation_cusp_discovery_round50.py` contains three
passing boundary checks and ten strict `xfail` red-team contracts.  The strict
xfails document the open defects while keeping the ordinary test suite green;
after repair, each must be converted to a normal passing regression before a
new manifest is frozen.

## 2. Audited hashes and intact pins

| role | SHA-256 |
|---|---|
| Round-47 manifest / external anchor | `9863c2d08fecad4c56c52d9b4bf6978c18614e150269149bc0a2cce141981e58` |
| Round-47 runner | `9825d35e0a116ff0bcf83abcaba5d4f237e0e4d7875b64ceb87ccd2806fee0b2` |
| Round-47 focused tests | `7285d9d1ccaf58cc43174bec48860085f5bc441e23449eeb67fe3be22361b217` |
| Round-47 protocol | `40ac57ca84f1d37010f12f75b7cd0d4c02ac5e35133f23ccf202f9eb7733033b` |
| Round-50 attack tests | `8a76765e0ca1ece5586581c4c03b9ffa6c306a04b375d599a500f7ca0fac5795` |
| Stage-A scaffold | `a76773b61f1f2f11802d265d3e69ec632de0b4b0ccbada40a49180454d4981cf` |
| Stage-A tests | `c2370dfc69e1e775b486a8a9653f1877d2a28a5003999507ce65017bfcecc065` |
| promotion design | `ad072e83004ea3e3b5c3d01a58a872b5aedca74d13400fa04d6f917d4a06d1f5` |

All 13 manifest pins matched their regular-file SHA-256 values.  The
positive-`B` point v2 chain remained unchanged:

| frozen-v2 role | SHA-256 |
|---|---|
| manifest | `955e59bf333b5fd70e415a53dc26becae9c7a34c5d40f1230c96b1dab8f5677c` |
| producer | `adb9434daeccca721ab9c1014f194e0cf9c5c6d0bf092d31e050c040b4b94da8` |
| tests | `d60e837c949333d29f7287b17c5e24c6db742067a655bac5050b5966dc821329` |
| protocol | `f25a8107d7a975342a3b1cbbf84c29df26654a8f6310f0429cba5ffdf7bcda00` |

## 3. What passed the independent attack

### 3.1 Same physical family and budget

The allocation manifest and positive-`B` point v2 manifest have byte-equivalent
JSON values for every physical parameter and for the finite-volume box/scheme.
The target budget is exactly `0.01` in both.  The allocation weights are
supposed to vary and therefore are not required to equal the fixed point's
control.

### 3.2 Fixed-budget tangent plane and isometric chart

An independent SVD reconstruction from the pinned `B=0` full-simplex response

```text
[[  3.07036526, -2.09946043, -4.00539310],
 [-11.35829709, 26.40000057, -6.05167654]]
```

reproduced singular values `29.4584764696`, `4.96688503058` and the printed
four-by-two matrix `P` after the stated order/sign convention.  It also gave
`1^T P=0` and `P^T P=I` at floating-point tolerance.  Thus the chart preserves
the unit total budget and uses an orthonormal Euclidean allocation metric.

The row/column action, fixed-budget tangent sign, direct observable derivative,
mixed jets, complete `H=(F_t,F_tt,F_ttt)` Jacobian, fourth derivative, projected
rank, full rank, and determinant factorization are algebraically consistent.
The existing five-/seven-cell checks support this conclusion.  Round 50 found
no new algebraic error in these formulas.

### 3.3 Bounded NO-CANDIDATE/HOLD is legitimate

When all 32 controls are geometrically ineligible, `phase_discovery` returns
all three representatives as `null`, advances no mesh-97 control, leaves
`search_expanded=false`, and gives `all_three_regions_found=false`.  Likewise,
the existing mesh-65 structural-HOLD test prevents construction of mesh 97.
Those are valid fail-closed paths.

### 3.4 Honest role of mesh 97

Mesh 97 is **not held out** in this Stage-A package.  Its positive-`B` cusp is
used as the centre of the 32-control chart, and selected controls are evaluated
on it.  Therefore 65 and 97 are both discovery meshes; at most, 97 is a
same-family low-mesh discovery confirmation.  The current negative held-out
claim flag and forbidden-claim list are honest.

A true held-out claim begins only after a no-refit Stage-B manifest freezes the
Stage-A result hash, physical representative weights, branch identities, and
comparison nodes.  Meshes 113/128/129/161, parity, and enlarged boxes belong to
that later package.

## 4. Severity convention and open count

- **P0:** can make a scientific PASS false or select a representative/branch
  that the pinned design does not authorize.
- **P1:** can leak scientific work after a gate failure, permit drift or
  malformed promotion, or violate a frozen deterministic/failure contract.
- **P2:** provenance or auditability weakness that does not by itself create a
  scientific PASS.

Open count:

```text
P0 = 3
P1 = 6
P2 = 2
```

This invalidates Round 47's pre-run `P0=P1=P2=0` conclusion.  It does not
invalidate the small-grid algebra scaffold, because the defects are in the
formal scientific gates, branch/selection logic, and promotion boundary.

## 5. P0 findings

### P0-1 — frozen positivity and conservation gates are absent

The pinned promotion design, Section 7.3, requires positive density and
survival, sampled survival monotonicity, state negativity no worse than
`1e-12`, `S_t=-f`, `Q1=-B*kappa`, differential mass balance, and event
partition closure within `1e-9`.

The Round-47 manifest freezes only peak/valley, curvature, root residual,
event-mass, sampled-state, and survival-increase thresholds.  The runner does
not gate

- final survival positivity;
- final-state or tail-state nonnegativity;
- positive density through the tail to `T=100`;
- `Q 1 = -B kappa`;
- differential `S_t+f=0` on the scan, roots, folds, cusp, or tail;
- event-partition closure;
- initial mass, physical installed budget, or factor diagnostics.

This is demonstrably fail-open, not merely missing metadata.  A Round-50 mock
with one legitimate-looking retained maximum and final state sum `-0.5`
produced

```text
final_survival = -0.5
event_basin_masses = [1.5]
all_gates_passed = true
```

The negative final survival artificially enlarges the last event basin.  Thus
the current runner can certify a representative that violates the pinned
killed-law contract.

**Required disposition:** P0 open; do not execute 65/97.

### P0-2 — fold branch side, comparison nodes, and remote-pair identity fail open

The current branch gate uses `abs(t-t_c)>=0.75`.  Comparison-node selection
minimizes mismatch against a signed target over *all* accepted nodes, but it
does not require

- signed reach `s(t-t_c)>=0.75` for branch sign `s`;
- a comparison node to be on the declared side;
- a maximum allowed time-offset mismatch;
- three distinct acceptance indices; or
- the remote max--min pair to be the same topological pair across nodes.

At each comparison node the runner accepts any newly found
`remote_pair_present=true`.  There is no persistent pair identity or
order-preserving matching rule.

The strict Round-50 probe supplied a nominal positive branch that turned
through the cusp and reached `t_c-0.8`; all three positive comparison targets
collapsed onto the same early node, and three unrelated remote pairs were
returned.  The current code reported `PASS_BRANCH_DISCOVERY`.

**Required disposition:** P0 open; a cusp plus two purported folds cannot be
claimed from this runner.

### P0-3 — incomplete finite phase evaluation can still produce PASS

The protocol says every geometrically eligible control is screened on mesh 65
before ranking, and every selected top-three control is evaluated on mesh 97.
The runner catches an eligible-control exception, records
`HOLD_CONTROL_EVALUATION`, and continues.  The overall PASS checks only whether
one passing representative exists for each of counts 1, 2, and 3.

The Round-50 probe injected one missing eligible mesh-65 evaluation while
providing passing controls for the three counts.  The current runner returned
`all_three_regions_found=true`.  The missing control could have had the largest
score, so neither the bounded exhaustive screen nor the declared maximizer is
known.

**Required disposition:** P0 open; any missing eligible mesh-65 row or selected
mesh-97 row must force the whole phase selection to HOLD.

## 6. P1 findings

### P1-1 — explicit-CSR preflight does not abort scientific construction

`run_formal` records `preflight["passed"]` only in its final Boolean.  The
65/97 loop runs regardless.  The Round-50 probe forced a failed preflight and
observed builds `(7,dry)`, `(65,formal)`, and `(97,formal)`.

This leaks both scientific meshes after the declared algebra boundary has
already failed.  A preflight HOLD must serialize two fixed-shape
`NOT_RUN_AFTER_PREFLIGHT_HOLD` rows without building either scientific model.

### P1-2 — full pin set is checked only before each replica calculation

`validate_manifest` hashes all 13 pins at the beginning of `run_formal`.
After the long calculation, `execute_replica` and the outer harness recheck
only the manifest file bytes.  A dependency, runner, protocol, or test can
change while the manifest remains byte-identical; the result would still cite
the old start-of-run hash map.

The repair must compare a complete role-to-hash snapshot before and after each
replica and again before promotion.  Manifest-byte equality alone is not a pin
snapshot.

### P1-3 — replica promotion validates only three top-level facts

Before canonical promotion, the harness checks canonical JSON, the top-level
Boolean `all_discovery_gates_passed`, status/exit code, and manifest hash.  It
does not validate exact result keys/types, two mesh rows, mesh identities,
fixed-shape HOLD rows, preflight status, phase completeness, negative claim
flags, forbidden claims, or pinned-file hashes.

The Round-50 probe produced two byte-identical `PASS` payloads with no mesh
rows and with held-out/publication flags set true.  The current harness promoted
them.  Two-process identity is reproducibility evidence only after the full
scientific and claim schema is validated.

### P1-4 — post-replace drift is not detected

Staging writes, file `fsync`, `replace`, directory `fsync`, append-only checks,
and rollback on raised exceptions are present.  However, after the last
directory sync the code does not re-read and hash the canonical result and
evidence.  A Round-50 injected mutation during the final sync returned
successfully with corrupted canonical bytes.

The transaction must verify exact expected bytes/hashes after both replaces
and the final directory sync; any mismatch or final pin drift must remove both
destinations and sync the rollback.

### P1-5 — the ranking score is not an exact frozen contract

The pinned promotion design defines the Stage-A ranking score over exactly
peak ratio, valley ratio, curvature, and event-basin mass.  The runner also
includes scaled root residual in the numeric minimum.  The manifest stores
only the prose string `minimum signed threshold-normalized margin`; it does not
serialize exact term order or lower-/upper-bound formulas.

This can change which three controls reach mesh 97 even if all root residuals
pass their eligibility threshold.  Freeze the exact term list and formulas in
JSON.  The root residual should remain an eligibility gate unless a new,
pre-run design explicitly changes the ranking rule.

### P1-6 — nonfinite scientific failures are not uniformly finite HOLD rows

Some arithmetic exceptions become structural HOLD, but other nonfinite values
can flow into a control row and are rejected only by final canonical JSON
serialization.  The Round-50 NaN-density probe returned a nonfinite row rather
than a finite structural HOLD.  A formal process would then fail operationally
and publish nothing, contrary to the frozen scientific-failure contract.

Every numerical scientific evaluation boundary must validate finiteness and
return the fixed finite-HOLD schema with `null` for unavailable quantities.
True environment/I/O/process failures should continue to publish nothing.

## 7. P2 findings

### P2-1 — same-family equality is checked but not pinned to the point chain

The physical parameters, finite-volume box, scheme, and `B=0.01` agree exactly
with the positive-`B` point v2 manifest.  However, the allocation manifest does
not pin that manifest/protocol/producer.  It pins the `B=0` bridge chain only.

A repaired result-blind allocation freeze should add the already frozen
positive-`B` v2 manifest/protocol/producer as provenance pins.  This need not
import or condition on the point result.

### P2-2 — output lacks enough diagnostics for a cheap independent audit

The runner computes useful factor diagnostics in the pinned bridge dependency,
but does not serialize them.  It also drops the full cusp/branch stationary
scans and retains only a chosen remote pair.  A later auditor cannot establish
root-screen completeness, factor normalization, generator row sums, or remote
pair identity from the canonical result without rerunning the expensive
scientific meshes.

The repaired schema should serialize factor/model diagnostics, saved scan/tail
traces, every bracketed root with eligibility reasons, and pair identifiers.
An independent post-result auditor should be frozen before the scientific run.

## 8. Minimum repair and re-freeze contract

The following is the minimum acceptable v2 pre-run contract.

1. **Physical-law gates.**  Reuse, independently implement, and freeze the
   positive-`B` point's `35,50,75,100` tail checkpoints; positive density and
   survival; scan/root/tail/final-state negativity tolerance `1e-12`;
   survival-increase tolerance `1e-12`; `Q1=-B*kappa`; differential mass
   balance and event-partition closure `1e-9`; initial mass; installed budget;
   and finite factor diagnostics.  Apply compatible checks at cusp and fold
   nodes as well as representatives.
2. **Signed branches.**  Require signed reach, correct-side comparison nodes,
   three distinct acceptance indices, and a predeclared maximum offset
   mismatch.  Freeze an order-preserving remote-root matching rule so the
   remote maximum and minimum have persistent identities and cannot be
   replaced by a different pair.
3. **Complete phase screen.**  Any missing eligible mesh-65 evaluation or any
   missing selected mesh-97 evaluation makes the entire phase result HOLD.
   Freeze exact score terms/formulas and keep root residual as an eligibility
   gate unless a separately audited design changes that decision.
4. **Preflight stop.**  A failed seven-cell action preflight builds neither 65
   nor 97 and writes fixed-shape not-run rows.
5. **Full pin snapshots.**  Compare all pinned-file hashes before and after
   each replica and immediately before/after promotion.  Add positive-`B` v2
   family-provenance pins.
6. **Exact result validator.**  Before accepting either replica, validate exact
   JSON types/keys, finite values, mesh rows `[65,65,65]` and `[97,97,97]`,
   PASS/HOLD implications, complete phase rows, all mandatory false claims,
   limitations, and the start/end pin snapshots.
7. **Failure-atomic promotion.**  Re-read exact canonical/evidence bytes after
   replacement and directory sync; on any mismatch or pin drift, remove and
   sync both outputs.  Preserve append-only semantics.
8. **Finite HOLD semantics.**  Convert nonfinite scientific evaluations to
   fixed finite-HOLD structures.  Never continue ranking after an unknown
   eligible control.
9. **Independent auditability.**  Serialize the diagnostics and traces needed
   for a result-blind post-result auditor, then freeze that auditor and its
   tests before executing v2.
10. **Re-freeze from zero.**  Update runner, ordinary tests, protocol, and
    manifest together; compute a new external manifest hash; verify all strict
    Round-50 probes as normal passing regressions; and reconfirm that all
    canonical/replica outputs are absent.  Only then may mesh 65 start.

No threshold, radius, chart, time window, mesh, or physical parameter may be
changed in response to any future 65/97 value.

## 9. Executed checks

```text
ruff format --check <runner> <Round47 tests> <Round50 tests> <Stage-A files>
5 files already formatted

ruff check <same files>
All checks passed!

py_compile <same files>
passed

pytest <Round47 tests> <Round50 tests> <Stage-A tests>
25 passed, 10 xfailed

seven-cell --algebra-dry-run
status = PASS_ALGEBRA_DRY_RUN_HOLD_SCIENCE
scientific_meshes_executed = []
maximum explicit-CSR action error = 2.220446049250313e-16
all_discovery_gates_passed = false
dry-run JSON SHA-256 =
94b1b02b6caaf0da779ef33f5c37f60cc2810edfaef9f973c5bbb6b467153d4b
```

Strict `xfail` probes independently reproduced all ten open contracts.  Three
representative failures were also executed with `--runxfail` and showed:

```text
wrong-side/duplicate fold branch -> PASS_BRANCH_DISCOVERY
missing eligible phase control  -> all_three_regions_found = true
malformed false-claim replicas   -> promoted without RuntimeError
```

Final filesystem boundary:

```text
canonical allocation result: absent
allocation reproducibility evidence: absent
hidden replica 1: absent
hidden replica 2: absent
mesh 65 allocation run: not executed
mesh 97 allocation run: not executed
```

## 10. Exact v2 commands required before the first formal mesh

After the v2 runner/tests/protocol/manifest and independent post-result auditor
have been repaired and re-pinned, run the following from the repository root.
`NEW_MANIFEST_SHA256` means the freshly computed external hash; it must not be
copied from this Round-50 report.

```bash
cd /Users/ae23069/Library/CloudStorage/OneDrive-UniversityofBristol/Desktop/valley-k-small

REPORT=research/reports/encounter_multimodal_prr
RUNNER=$REPORT/code/positive_b_allocation_cusp_discovery.py
TEST47=$REPORT/code/test_positive_b_allocation_cusp_discovery.py
TEST50=$REPORT/code/test_positive_b_allocation_cusp_discovery_round50.py
STAGEA=$REPORT/code/positive_b_allocation_cusp_stage_a.py
STAGEA_TEST=$REPORT/code/test_positive_b_allocation_cusp_stage_a.py
MANIFEST=$REPORT/artifacts/data/positive_b_allocation_cusp_discovery_manifest.json

! rg -n 'pytest\.mark\.xfail' "$TEST50"

.venv/bin/python -m ruff format --check \
  "$RUNNER" "$TEST47" "$TEST50" "$STAGEA" "$STAGEA_TEST"
.venv/bin/python -m ruff check \
  "$RUNNER" "$TEST47" "$TEST50" "$STAGEA" "$STAGEA_TEST"
.venv/bin/python -m py_compile \
  "$RUNNER" "$TEST47" "$TEST50" "$STAGEA" "$STAGEA_TEST"
.venv/bin/python -m pytest -q \
  "$TEST47" "$TEST50" "$STAGEA_TEST"

NEW_MANIFEST_SHA256=$(sha256sum "$MANIFEST" | awk '{print $1}')
test "${#NEW_MANIFEST_SHA256}" -eq 64

test ! -e "$REPORT/artifacts/data/positive_b_allocation_cusp_discovery_result.json"
test ! -e "$REPORT/artifacts/data/positive_b_allocation_cusp_discovery_reproducibility.json"
test ! -e "$REPORT/artifacts/data/.positive_b_allocation_cusp_discovery_result.replica_1.json"
test ! -e "$REPORT/artifacts/data/.positive_b_allocation_cusp_discovery_result.replica_2.json"

.venv/bin/python "$RUNNER" \
  --algebra-dry-run --cells 7 \
  --expected-manifest-sha256 "$NEW_MANIFEST_SHA256" \
  > /tmp/allocation_cusp_v2_dry_1.json
.venv/bin/python "$RUNNER" \
  --algebra-dry-run --cells 7 \
  --expected-manifest-sha256 "$NEW_MANIFEST_SHA256" \
  > /tmp/allocation_cusp_v2_dry_2.json
cmp /tmp/allocation_cusp_v2_dry_1.json /tmp/allocation_cusp_v2_dry_2.json

.venv/bin/python - <<'PY'
import json
from pathlib import Path

rows = [
    json.loads(Path(path).read_text(encoding="utf-8"))
    for path in (
        "/tmp/allocation_cusp_v2_dry_1.json",
        "/tmp/allocation_cusp_v2_dry_2.json",
    )
]
for row in rows:
    assert row["status"] == "PASS_ALGEBRA_DRY_RUN_HOLD_SCIENCE"
    assert row["scientific_meshes_executed"] == []
    assert row["explicit_csr_preflight"]["passed"] is True
    assert row["all_discovery_gates_passed"] is False
PY
```

The repaired independent post-result auditor and its tests must also pass their
own exact frozen command before launch.  Since those v2 filenames/hashes do not
yet exist, inventing that command here would be false provenance.

Only after every command above succeeds and a new independent pre-run audit
reports `P0=P1=P2=0` may the operator launch exactly:

```bash
cd /Users/ae23069/Library/CloudStorage/OneDrive-UniversityofBristol/Desktop/valley-k-small
caffeinate -dimsu .venv/bin/python \
  research/reports/encounter_multimodal_prr/code/positive_b_allocation_cusp_discovery.py \
  --execute-frozen \
  --expected-manifest-sha256 "$NEW_MANIFEST_SHA256"
```

The launch command is recorded for the future v2 package; Round 50 did not run
it.

## 11. Authorization decision

The algebraic direction remains promising and the low-mesh discovery plan is
scientifically sensible.  The present Round-47 formal package is nevertheless
**NO-GO** because three defects can create a false scientific PASS and six
more violate fail-closed execution or promotion.

Authorization remains:

```text
PASS-ALGEBRA-DRY-RUN
HOLD-ALLOCATION-SCIENCE
NO-GO-MESH-65
NO-GO-MESH-97
```

After the complete v2 repair/re-freeze passes an independent pre-run attack,
Stage A may run 65 then 97 as **discovery only**.  A successful Stage A still
does not authorize a held-out, continuum, box, independent-solver, manuscript,
or PRR claim.
