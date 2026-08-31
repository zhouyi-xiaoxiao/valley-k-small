# Round 11 G1b discovery adversarial gate

Date: 2026-07-13  
Stage: `G1b_discovery_not_continuum_confirmation`  
Scope: independent pre-execution attack; no formal control was assembled or
propagated

## Audit state

**Initial verdict: FAIL (P1, fail-closed action and resume integrity).**

**Final remediation verdict: PASS for launching the frozen discovery run.**
This document deliberately preserves the pre-fix failures; the final section
records the disposition of every attack against one stable remediated version.
This is an implementation launch gate only, not a continuum or fold result.

There is no P0 scientific-result defect because no formal G1b result exists.
The P1 defects are nevertheless launch blockers: they can accept an altered
checkpoint or turn an unresolved topology screen into an action-bearing
`line_empty` or `freeze_candidate` decision.

The attacked pre-fix identities were:

```text
discovery runner SHA-256:
f746285a9f44ab34903d3c33052b20fa985eb4e5ebdd0da82c120efd0a8d6c9b
frozen manifest SHA-256:
0b4f2252b14bd48ec77192fdecb2646f963911e298358e56295b529bae4167db
G1a certificate SHA-256:
a0a1894dbe6dd37bad6973ca6f3dd29b651441f7b911a5406186bb86a18fd3c3
G1a smoke code SHA-256:
e0322b212e466b1b640f5adcf30d67d119d2f6fe4cc622eb532082b6cd251701
```

## Confirmed P1 failures

### P1-1. Resume accepted altered frozen fields and fake gate schemas

A valid one-control dry-run checkpoint was copied in a temporary directory.
Each of the following single mutations was then replayed through the complete
`run_discovery(..., resume=True)` path:

| Mutation | Pre-fix result |
| --- | --- |
| `parameters.diffusion = 999.0` | **ACCEPTED**, 1/1 controls resumed |
| `claim_scope = "continuum fold verified"` | **ACCEPTED**, 1/1 resumed |
| `chunk_diagnostics.maximum_chunk_state_rows = 999999` | **ACCEPTED**, 1/1 resumed |
| replace model diagnostics by `{"gates":{"fake_gate":"truthy"},"diagnostics":{}}` | **ACCEPTED**, 1/1 resumed |

The required top-level key set did not validate the values it claimed to
freeze.  In particular, `all(gates.values())` accepted a truthy string and did
not require the hardened gate names, count, Boolean types, or freshly
reconstructed diagnostics.

### P1-2. The strict manifest comparison was not type-strict

Python structural equality equates integers, floats, and Booleans in cases
that JSON schema validation must distinguish.  Three independently written
manifests all passed `load_and_validate_manifest`:

```text
schema_version: 1.0                         ACCEPTED
candidate_rules.adjacent_theta_sign_change: 1  ACCEPTED
time_grid.start: 0                          ACCEPTED
```

The Boolean-as-integer case would fail only when line analysis begins, after
all formal controls had already been propagated.  This contradicted the
preflight claim that mistyped manifest values fail before assembly.

### P1-3. The pinned G1a artifact did not pin the model actually assembled

The certificate hash and 42 artifact gates were valid, but the discovery
preflight did not compare the current `PilotParameters`, endpoint weights, or
smoke-code identity with the artifact's frozen model contract.  In an
executable mutation, current defaults were changed at runtime to

```text
diffusion = 0.0055
ou_mean = 1.05
```

while the pinned G1a JSON remained byte-for-byte unchanged.  The runner
reported the pinned certificate `PASS`, all 38 current per-control foundation
gates passed self-consistently, and the drifted parameters were used and
stored.  Recording the current smoke-code hash in provenance is not a
pre-execution authorization check: an audited smoke-code digest or equivalent
model contract must be pinned and compared before assembly.

### P1-4. Resume accepted physically impossible stored curves

Two further single-field mutations of a valid checkpoint were accepted by the
full resume path without changing candidate analysis:

```text
curves.survival[1] = 2.0   ACCEPTED
curves.f_ttt[1] = 999.0    ACCEPTED
```

The first violates probability range and survival monotonicity; the second
breaks the claimed stored generator jet.  Candidate recomputation used only
`f`, `f_t`, and `f_tt`, while generic curve validation checked only shape,
finiteness, and time order.  Resume therefore needs checkpoint byte integrity
plus fresh-model/curve/chunk invariants; merely recomputing the candidate label
is insufficient.

### P1-5. Greedy branch matching could cross branches and report false empty

For two adjacent interior controls, use two same-kind extrema at each control:

```text
theta = 0.4: times [1.0, 2.0], f_t heights [+0.2, -0.2]
theta = 0.5: times [1.6, 3.0], f_t heights [-0.2, +0.2]
time-match tolerance = 2.0
```

The greedy matcher selected `(left 1, right 0)` and `(left 0, right 1)`, a
crossing assignment.  Both selected pairs had equal signs, so it emitted zero
sign brackets and
`line_empty_only_predeclared_simplex_followup_is_allowed`.  The
order-preserving pairs both change sign.  Branch matching must be
order-preserving and must block line action when an optimal assignment is
ambiguous.

### P1-6. A zero plateau spanning the analysis boundary could authorize a candidate

The filter was applied to the midpoint of a collapsed exact-zero run rather
than its interval.  In a synthetic boundary attack, an exact-zero `f_tt` run
spanning `t=0` through `t=1` collapsed to `t=0.5`, passed the declared
`minimum_analysis_time=0.5`, and at an interior control emitted
`freeze_candidate_only_then_implement_sensitivity_before_continuation`.

This is a candidate-analyzer fail-closed defect: a maximal zero run touching
the excluded pre-analysis interval cannot be promoted merely because its
midpoint lies on the threshold.  It must be explicitly excluded or truncated
under a frozen, tested interval rule.  Stored-curve physical invariants remain
a separate required defence.

### P1-7. Root-count changes and unmatched extrema could still report false empty

After replacing greedy matching by an order-preserving prototype, four
additional synthetic action attacks still produced `line_empty`:

| Adjacent-control evidence | Pre-fix/prototype action |
| --- | --- |
| retained `f_t` root count changes `1 -> 3` | `line_empty` |
| one same-kind `f_tt` extremum at `t=1`, one at `t=4` with tolerance 2 | both unmatched, then `line_empty` |
| one retained `f_tt` extremum versus none | unmatched, then `line_empty` |
| equal root count but a changed ordered maximum/minimum/degenerate signature | not inspected |

A retained root-count or topology-signature change is topology-or-boundary
evidence.  An unmatched extremum means branch tracking is incomplete.  These
observations do not by themselves authorize a fold-candidate freeze because a
root or extremum can enter through the time window or density filter.  They do
require a manual-review action and must block both `line_empty` and candidate
freezing.  Excluded-bracket reasons should be retained to distinguish a
minimum-time/density-floor exit from interior topology evidence.

## Checks that passed on the attacked version

The failures above do not invalidate the following independently checked
parts of the runner:

1. The manifest has the intended `65 x 65 x 49 = 207025` states, 11 controls,
   and 321 times from 0 to 80 at spacing 0.25.
2. A 41-row overlapping chunk advances 40 new times, so the formal line uses
   eight state chunks per control and never serializes the full state history.
3. On an asymmetric two-state row generator, the runner agreed with the
   independent dense formula
   `p0 @ exp(A*t) @ A^j @ k` for `j=0,1,2,3` to between
   `4.5e-16` and `3.6e-15`; the deliberately wrong orientation differed by
   `1.1e-1`.
4. The existing asymmetric-grid chunk/full-history test passed for all five
   stored observables.
5. Duplicate-key and non-finite JSON inputs were rejected.
6. Raw G1a artifact tampering, a failed status, and a failed gate were rejected
   by the pinned artifact check.
7. A simulated non-repository virtual environment was rejected before a
   checkpoint directory was created.
8. `continuum_verified` and `project_gate_passed` remained false in newly
   computed dry-run outputs.

Baseline commands on the attacked version gave:

```text
pytest test_continuum_g1_discovery.py: 12 passed
ruff check: All checks passed
isolated CLI --dry-run: DRY_RUN_COMPLETE
```

Those green baseline checks were real but incomplete: none exercised the P1
mutations above.

## Required remediation gate

Before changing this audit to PASS, one stable version must demonstrate all
of the following through complete-path executable tests:

1. recursive exact-type manifest validation before model assembly;
2. a pinned G1a model/code contract matching current parameters and endpoints;
3. exact nested checkpoint schemas, Boolean hardened gates, and fresh model
   diagnostics;
4. an atomic integrity ledger that rejects a missing ledger, checkpoint
   orphans, ledger orphans, hash mismatch, rewritten metadata, duplicate or
   non-finite JSON, and incomplete temporary writes;
5. stored-curve and chunk invariants, including survival, density, all four
   generator-action observables, expected dimensions, and the no-full-history
   promise;
6. order-preserving matching with explicit ambiguity, unmatched-extremum,
   retained-root-count, and topology-signature action blockers;
7. interval-safe initial-zero handling and the existing control-endpoint
   exact-zero rules;
8. repository-`.venv` rejection and exact formal configuration guards; and
9. full tests, ruff, format check, and an isolated dry-run/resume with no
   formal artifact created.

Until that re-audit is appended, Round 09's runner PASS is superseded by this
Round 11 launch-blocking FAIL.

## Final remediation re-audit

### Stable identities

The complete replay below was performed against one final version:

```text
discovery runner SHA-256:
1411384398ed4e476dba15371cdfd662e94ed3a53cffdc02a1562201cfa7b52e
frozen manifest SHA-256:
193c0fc1b7281dee2dd38b6c1152b73591dc0e0b82f5d3510edcd1e7e2dc7390
protocol SHA-256:
8cbf2469fab0c18982028450f5c3f0c1ff188c3105ae280c5448fcf1cf23125d
discovery tests SHA-256:
70d6aec2b8155961f170c7a791ea8fd3c57286110cd12810cbc9a8f684d4d71b
G1a producer SHA-256:
e0322b212e466b1b640f5adcf30d67d119d2f6fe4cc622eb532082b6cd251701
G1a artifact SHA-256:
a0a1894dbe6dd37bad6973ca6f3dd29b651441f7b911a5406186bb86a18fd3c3
```

The formal result and checkpoint paths were both absent before and after this
audit. No formal model was assembled or propagated.

### P1 disposition matrix

| Initial failure | Final independent replay |
| --- | --- |
| altered parameters, claim, chunk metadata, or fake truthy gates | raw edit rejected by ledger SHA; edit plus deliberately resealed ledger rejected by exact semantic validation |
| manifest Boolean/integer/float coercion | all three rejected during manifest load, before assembly |
| model, endpoint, or producer-code drift | each rejected against the pinned G1a contract/hash |
| impossible survival or altered `f_ttt` | raw edit rejected by ledger; resealed edit rejected by mass/monotonicity or generator-action bounds |
| crossing greedy branch assignment | order-preserving pairs `(0,0)` and `(1,1)` recovered both sign changes |
| preanalysis zero run promoted by its midpoint | retained extrema `0`; run persisted as excluded with `exact_zero_run_starts_before_minimum_analysis_time` |
| root-count/topology change reported empty | manual-review action; simplex fallback blocked |
| unmatched or ambiguous extrema reported empty | manual-review action; candidate freeze and simplex fallback both blocked |
| excluded-filter transition reported empty | manual-review action with `analysis_filter_signature_changed` |

The action precedence was also attacked. A control pair containing an
interior sign candidate plus unmatched or ambiguous extrema emitted manual
review, not candidate freezing. Clean, stable controls with no flag remained
the only case that emitted
`line_empty_only_predeclared_simplex_followup_is_allowed`. Exact zeros at
control endpoints `0` and `1` remained diagnostic only, while exact zeros at
sampled interior controls `0.1` and `0.9` retained interior-candidate status.

### Checkpoint and ledger replay

A fresh one-control checkpoint was mutated in temporary directories. All six
named edits were tried twice: first without changing the ledger and then after
deliberately recomputing the ledger entry SHA-256.

```text
parameters.diffusion = 999                 REJECT / REJECT after reseal
claim_scope = "fold verified"              REJECT / REJECT after reseal
maximum_chunk_state_rows = 999999          REJECT / REJECT after reseal
fake string-valued gate schema             REJECT / REJECT after reseal
survival[1] = 2                            REJECT / REJECT after reseal
f_ttt[1] = 999                             REJECT / REJECT after reseal
```

The final runner also rejected, through the complete resume path:

- a missing ledger with a checkpoint present;
- a missing checkpoint with a ledger entry present;
- an extra checkpoint, a missing entry, and mistyped entry metadata;
- a raw checkpoint hash mismatch;
- rewritten top-level ledger metadata;
- `.theta_*.json.tmp` and `.integrity_ledger.json.tmp` interrupted writes;
- duplicate-key and non-finite ledger JSON; and
- duplicate-key and non-finite checkpoint JSON after fixture resealing.

The unmodified checkpoint resumed successfully. Ledger validation occurs
before checkpoint JSON is trusted; fresh model assembly then reproduces the
exact parameters, grid, weights, gate names and Boolean values, foundation
diagnostics, curve bounds, chunk metadata, and candidate analysis.

The ledger is an integrity mechanism for this trusted local research
workspace, not a keyed cryptographic signature against an actor allowed to
rewrite every file and external version record. The stable hashes above and
the repository/audit history are the external identity boundary.

### Single-writer replay

An additional operational P2 was found during remediation: two simultaneous
dry-run writers originally shared the same temporary filename, causing one to
fail late with `FileNotFoundError`. The final runner holds a non-blocking
`fcntl.flock` on `.run.lock` for the complete run.

Five independent two-process collisions were replayed. In every trial:

- exactly one process completed three controls;
- the second failed before computation with
  `checkpoint directory already has an active writer`;
- the integrity ledger contained exactly three entries;
- the result reported `3` computed and `0` resumed controls; and
- the persisted owner record ended with `status=RELEASED`.

No shared-temporary-file error or silent checkpoint divergence remained.

### Independent numerical and resource checks

On an asymmetric two-state row generator, the final runner was compared with
the independent dense expression

```text
p0 @ exp(A*t) @ A^j @ k,  j = 0,1,2,3.
```

The maximum absolute errors for `f`, `f_t`, `f_tt`, and `f_ttt` were

```text
4.44e-16, 4.44e-16, 1.78e-15, 3.55e-15.
```

The deliberately wrong orientation differed by `1.106e-1`, and survival
agreed to `1.11e-16`. The test chunk retained two state rows. The frozen
formal configuration independently reconstructed as:

```text
states = 65 * 65 * 49 = 207025
times = 321
chunk row limit = 41
theta controls = 11
chunks per control = 8
```

Only the five complete projected curves are serialized; the full state
history is neither returned nor checkpointed.

A simulated formal launch outside the repository `.venv` raised
`formal discovery must run inside the repository .venv` before creating the
requested checkpoint directory. A non-manifest formal configuration was also
rejected before propagation.

### Final test evidence

```text
pytest test_continuum_g1_discovery.py: 48 passed
ruff check: All checks passed
ruff format --check: 2 files already formatted
isolated CLI --dry-run: DRY_RUN_COMPLETE
dry-run continuum_verified: false
dry-run project_gate_passed: false
```

The dry-run conservatively emitted a manual-review diagnostic for an unmatched
transition; it did not emit an interior fold candidate. That implementation
smoke has no scientific bearing on the frozen formal line.

## Final binary verdict

**Round 11 implementation launch gate: PASS.**

**Unresolved P0: none. Unresolved P1: none. Launch-blocking P2: none.**

This PASS authorizes only the exact explicit
`--execute-frozen` topology-discovery calculation. It does not establish a
continuum fold, bimodality, a project-gate pass, or PRR readiness. Every formal
result must retain `continuum_verified=false` and `project_gate_passed=false`;
candidate confirmation, sensitivity, odd/even convergence, box/tail tests,
and an independent numerical method remain separate gates.
