# Round 56: allocation-cusp v2 result-blind repair and re-freeze

Date: 2026-07-14  
Role: implementing repair of the Round-50 pre-run findings  
Decision: **GO-CODE / GO-RESULT-BLIND-PROTOCOL / HOLD-INDEPENDENT-PRE-RUN / NO-GO-65-97**

## 1. Non-execution and evidence boundary

This round did not execute meshes 65 or 97 and did not run any model with more
than seven cells.  It did not open or condition on any hidden or canonical
positive-`B` point result.  At completion, all allocation-discovery artifacts
were absent:

```text
positive_b_allocation_cusp_discovery_result.json                  absent
positive_b_allocation_cusp_discovery_reproducibility.json         absent
.positive_b_allocation_cusp_discovery_result.replica_1.json       absent
.positive_b_allocation_cusp_discovery_result.replica_2.json       absent
positive_b_allocation_cusp_discovery_independent_audit.json       absent
```

The only numerical execution was the fixed seven-cell explicit-CSR algebra dry
run.  This report is the implementer's repair/freeze record, **not** an
independent pre-run closure.  A separate adversarial round must authorize any
formal scientific launch.

## 2. Old and new external anchors

| role | SHA-256 |
|---|---|
| superseded Round-47 manifest | `9863c2d08fecad4c56c52d9b4bf6978c18614e150269149bc0a2cce141981e58` |
| v2 manifest / new external anchor | `492922112d14ee62f610cfc3508f7286ff7d64ab28e5b7ea7b3fdff041ad78eb` |
| v2 runner | `2e2f4aacfe105a0bb7d61872ead8f189de6380e193209b7034de34c9ded35ada` |
| ordinary v2 tests | `1833b07fdefaf8740da45f914dd118b2b59d0abed713c802cbfd1eb8b450ea3b` |
| converted Round-50 regressions | `23318afd8fef7c8a31a408dfaf4c51c328604cf371458727be9dad698f76c6a7` |
| v2 discovery protocol | `fa26995c0af9824dbba7231ace4fc08cef9664cb3bd09021a5cb90c1eed393e0` |
| Round-50 attack report | `059e3f33b9a8e32cfe2e4ca26d1916dceac61b9fb53d89c77cdfdeb4a568829d` |
| Stage-A algebra scaffold | `a76773b61f1f2f11802d265d3e69ec632de0b4b0ccbada40a49180454d4981cf` |
| Stage-A tests | `c2370dfc69e1e775b486a8a9653f1877d2a28a5003999507ce65017bfcecc065` |
| independent post-result auditor | `c398dec6216ac734ebcd89ffc77b12225f22ef87a4afedcc01bb5f219ad35107` |
| independent auditor tests | `697d8f7dea5cc5ac8d797730299f0c4026edcab54e6e7d03d61b4596acc7bbbd` |
| no-cycle post-result audit protocol | `98edbadf0fa78afbe8e88d44f1377ac1f68f3ce348756153ce0fecd5025f1ebe` |

The manifest now has 18 regular-file pins.  It adds the Round-50 report/tests
and the already frozen positive-`B` family anchors:

```text
positive-B v2 manifest  955e59bf333b5fd70e415a53dc26becae9c7a34c5d40f1230c96b1dab8f5677c
positive-B v2 protocol  f25a8107d7a975342a3b1cbbf84c29df26654a8f6310f0429cba5ffdf7bcda00
positive-B v2 producer  adb9434daeccca721ab9c1014f194e0cf9c5c6d0bf092d31e050c040b4b94da8
```

The post-result auditor is deliberately not a manifest pin because it
hard-codes the new manifest hash.  Its separate protocol records the manifest,
auditor, and auditor-test hashes, so there is no hash cycle.

## 3. Round-50 finding closure matrix

### P0-1 — positivity and conservation gates

Closed in code and schema.  The v2 contract evaluates and serializes

- positive density and survival;
- state nonnegativity through scan, roots, tail, and final time;
- sampled survival monotonicity;
- `S_t=-f` and differential mass balance;
- `Q 1=-B kappa`;
- initial mass and physical installed budget;
- event-partition closure; and
- finite factor diagnostics.

The frozen tail checkpoints are `35,50,75,100`.  Thresholds are `1e-12` for
state/survival-increase/initial-mass/installed-budget errors and `1e-9` for
survival identity, generator identity, differential mass balance, and event
closure.  Compatible checks apply at cusps and every accepted fold node.

### P0-2 — branch orientation, comparison nodes, and pair identity

Closed.  Required reach is now signed, `s(t-t_c)>=0.75`.  Comparison nodes are
selected on the declared side without replacement, must have three distinct
acceptance indices, and must miss signed targets `0.25,0.50,0.75` by at most
`0.125`.  The remote pair carries a persistent identity consisting of side and
order-preserving max--min pair ordinal; the same non-null identity must be
present at all three comparison nodes.

### P0-3 — incomplete phase evaluation

Closed.  Any missing/nonfinite geometrically eligible mesh-65 evaluation or
any missing selected mesh-97 evaluation sets `phase_complete=false`, clears all
representatives, and forces global HOLD.  Successful controls cannot mask an
unknown eligible row.

### P1-1 — preflight leakage

Closed.  A failed seven-cell preflight returns two fixed
`NOT_RUN_AFTER_PREFLIGHT_HOLD` rows before either scientific model is built.
The regression observes only `(7,false)` construction.

### P1-2 — incomplete pin revalidation

Closed.  The child and parent compare the complete 18-role hash snapshot before
and after each long calculation, after each hidden replica write, before
promotion, and after canonical promotion.  Manifest-byte equality alone is no
longer treated as a pin snapshot.

### P1-3 — weak replica validator

Closed.  The exact v2 validator checks native finite JSON, exact top-level and
mesh-row key sets, mesh identities, preflight shape/values, sequential HOLD
implications, phase cardinalities/completeness, representative implications,
all mandatory false claims, limitations, software fields, and start/end pin
snapshots before promotion.

### P1-4 — post-replace drift

Closed.  After both replacements and directory `fsync`, exact result/evidence
bytes are reread and the full pin callback is rerun.  Any mismatch deletes and
syncs both outputs.  Regression tests cover both post-replace byte mutation and
final pin drift.

### P1-5 — unfrozen ranking score

Closed.  JSON freezes exactly four ordered terms:

```text
peak_ratio
valley_ratio
absolute_scaled_curvature
event_basin_mass
```

Lower-bound margin is `value/lower_bound-1`; upper-bound margin is
`(upper_bound-value)/(1-upper_bound)`; the score is their minimum.  Root
residual remains an eligibility gate only.

### P1-6 — nonfinite failures

Closed.  Nonfinite scientific control evaluation becomes a fixed finite
`HOLD_CONTROL_EVALUATION` structure with `null` unavailable quantities and all
gates false.  Such a row cannot enter ranking.  Operational I/O/process errors
still publish nothing.

### P2-1 — family provenance

Closed by the three positive-`B` family pins above, without importing or
reading the point result.

### P2-2 — cheap independent auditability

Closed at the contract level.  The result now retains finite-volume factor and
model diagnostics, saved stationary-scan and tail traces, every bracketed root
with eligibility reasons, root law diagnostics, complete comparison-node
scans, and persistent pair identities.

The independent auditor does not import the producer.  It algebraically
reconstructs provenance, score, reported physical-law gates, branch rules, and
PASS/claim implications.  It explicitly does not recompute the semigroup,
root completeness between saved points, cusp/fold solves, or generator
construction; those remain producer-reported and require later solver/held-out
work for stronger claims.

Implementer-side open count after repair:

```text
P0 = 0
P1 = 0
P2 = 0
```

This count is subject to the required independent pre-run attack.

## 4. Executed checks

```text
ruff format --check: 7 files already formatted
ruff check: All checks passed
py_compile: passed
pytest: 45 passed
Round-50 strict xfail markers remaining: 0
```

Two independent seven-cell stdout dry runs were byte-identical:

```text
status                                  PASS_ALGEBRA_DRY_RUN_HOLD_SCIENCE
scientific_meshes_executed              []
explicit-CSR maximum action error       2.220446049250313e-16
all_discovery_gates_passed              false
dry-run canonical JSON SHA-256          6eec8b475dbbeace0bc5d4c82b7fdf30083bd61a92ddca7b4acd12ecebd13631
```

The independent-auditor suite includes valid scientific-HOLD, false-claim,
evidence-tamper, score/root-residual separation, malformed-structure,
producer-import, and no-hash-cycle regressions.

## 5. Frozen commands, not executed in this round

Formal discovery command:

```bash
cd /Users/ae23069/Library/CloudStorage/OneDrive-UniversityofBristol/Desktop/valley-k-small
caffeinate -dimsu .venv/bin/python \
  research/reports/encounter_multimodal_prr/code/positive_b_allocation_cusp_discovery.py \
  --execute-frozen \
  --expected-manifest-sha256 492922112d14ee62f610cfc3508f7286ff7d64ab28e5b7ea7b3fdff041ad78eb
```

Canonical post-result audit invocation, exactly once after promotion:

```bash
cd /Users/ae23069/Library/CloudStorage/OneDrive-UniversityofBristol/Desktop/valley-k-small
.venv/bin/python \
  research/reports/encounter_multimodal_prr/code/audit_positive_b_allocation_cusp_discovery_result.py
```

These commands are recorded for the next authorized stage.  Round 56 did not
execute either command.

## 6. Authorization

```text
GO-CODE
GO-RESULT-BLIND-V2-PROTOCOL
GO-POSTRESULT-AUDITOR-UNIT-CONTRACT
HOLD-INDEPENDENT-PRE-RUN-ATTACK
NO-GO-MESH-65
NO-GO-MESH-97
```

After a separate independent pre-run audit reports no new P0/P1/P2 finding,
mesh 65 may start, followed by mesh 97 only if all earlier gates pass.  Both
remain discovery meshes; mesh 97 is a same-family low-mesh discovery
confirmation, not held out.  A successful Stage A would authorize only a
separate no-refit Stage-B freeze, not a continuum, held-out, manuscript, or PRR
claim.
