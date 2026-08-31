# Round 09 G1b discovery-runner preflight

Date: 2026-07-13  
Stage: `G1b_discovery_not_continuum_confirmation`  
Scope: implementation and small dry-run only

## Binary verdict

**Runner implementation preflight: PASS.**

**Formal frozen discovery run: NOT STARTED.  Pinned G1a start gate: PASS.**  No
`65 x 65 x 49` model was assembled, no 207,025-state control was propagated,
and no formal discovery checkpoint or result exists.  The independently
reconstructed schema-3 G1a artifact, its producing model assembler, and its
canonical physical/control contract are now pinned and validated fail-closed;
the formal command remains deliberately unexecuted.

This preflight is not a continuum verification, fold result, project-gate
pass, or PRR submission result.

## Implemented files

- `code/continuum_g1_discovery.py`;
- `code/test_continuum_g1_discovery.py`;
- result-blind candidate-rule amendment and finalized G1a certificate pin in
  `artifacts/data/continuum_g1_discovery_manifest.json`; and
- matching explanation in `notes/discovery_protocol.md`.

The runner reuses the public hardened interfaces
`continuum_g1_smoke.build_model`, `foundation_diagnostics`, and
`foundation_gates`.  It does not maintain a forked subset of G1a foundation
checks.

## Formal-run safety boundary

The command-line interface requires exactly one explicit mode:

```text
--dry-run
--execute-frozen
```

There is no implicit default that can launch the formal line.  In formal mode:

- the run configuration must equal the strict frozen manifest exactly;
- the process must be running inside the repository `.venv`;
- any unknown, missing, duplicated, mistyped, or non-finite manifest value is
  rejected;
- checkpoint provenance, code hash, manifest hash, run mode, grid, time curve,
  weights, and candidate analysis must reproduce before resume; and
- the exact schema-3 G1a artifact pin must pass before any checkpoint is read
  or any control is assembled.

The manifest does not store its own hash.  Its raw SHA-256 is computed at run
time and recorded in result/checkpoint provenance.  Therefore the G1a artifact
hash pin does not create a manifest self-reference cycle.

The pinned certificate is:

```text
artifact: artifacts/data/continuum_g1_smoke.json
schema/stage/status: 3 / G1a_pre_fold_foundations / PASS
continuum_verified: false
gates: 42/42 true
SHA-256: a0a1894dbe6dd37bad6973ca6f3dd29b651441f7b911a5406186bb86a18fd3c3
producer code: code/continuum_g1_smoke.py
producer SHA-256: e0322b212e466b1b640f5adcf30d67d119d2f6fe4cc622eb532082b6cd251701
model-contract SHA-256: d434d127f7f2fb28c37c749f55fda35bd71535fdd378d438fcc759d89ef09020
```

The validator rejects a missing or escaping path, mistyped requirement,
duplicate/non-finite JSON, raw hash mismatch, schema/stage/status mismatch,
false continuum flag, non-Boolean gate, gate-count mismatch, or any failed
gate.  The deterministic PASS record is embedded in aggregate output and
checkpoint provenance.

## Chunked semigroup implementation

For each control, the runner forms generator-action observable vectors

```text
k, A k, A^2 k, A^3 k
```

and computes:

```text
f, f_t, f_tt, f_ttt, survival
```

Consecutive `expm_multiply` chunks overlap at one state.  Each call returns no
more than the frozen `chunk_points` state rows.  After projecting a chunk onto
the five stored observables, only its last state is retained for propagation;
the chunk state array is discarded.  The result and every checkpoint state:

```json
"full_state_history_stored": false
```

The complete five observable curves and time grid are retained for every
theta.  No full state history is serialized into a checkpoint or aggregate
result.

The formal manifest has 321 time points and `chunk_points=41`, so the overlap
scheme would require eight chunks per control.  That statement is a static
configuration consequence only; the formal calculation was not run.

## Candidate logic and result-blind amendment

The first small dry-run exposed a protocol-level issue before any formal
result existed: the contact-safe initial condition can give exact zeros in
`f(0)` and its generator-action jets.  Treating each adjacent pair containing
zero as a separate sign bracket would multiply one exact-zero plateau into
several false roots.

The frozen protocol and manifest were amended, still result-blind, with:

```text
minimum_analysis_time = 0.5
relative_density_floor = 1e-12
```

The implementation now:

1. retains the complete raw curves;
2. collapses each maximal exact-zero run to one sampled bracket;
3. records brackets excluded by the time/density rules, including exclusion
   reasons;
4. retains every remaining sampled `f_t` sign bracket;
5. linearly interpolates every remaining sampled `f_tt` sign bracket to
   estimate an extremum of `f_t`;
6. applies the frozen `abs(t f_t / f) <= 0.05` discovery flag; and
7. matches same-kind extrema using a non-crossing, order-preserving,
   maximum-cardinality then minimum-total-separation rule within the frozen
   time tolerance `2.0`; and
8. separately records strict opposite signs and exact-zero theta locations for
   the interpolated `f_t` heights.

`line_has_discovery_flag` records both interior and endpoint diagnostics.
However, the action

```text
freeze_candidate_only_then_implement_sensitivity_before_continuation
```

is emitted only when `interior_discovery_flag=true`.  An endpoint-only flag
emits

```text
endpoint_only_flag_does_not_authorize_candidate_freeze
```

and therefore cannot authorize confirmation work.  In particular, a strict
opposite-sign pair brackets an interior control value, but an exact zero is
interior evidence only if its own sampled theta lies strictly inside `(0,1)`.
An exact zero only at theta `0` or `1` cannot authorize candidate freezing.

A bracket or exact-zero run whose left endpoint is before `t=0.5` is excluded
as preanalysis evidence even if midpoint interpolation lands at or after the
threshold.  A `line empty` action is available only when adjacent controls
have stable retained `f_t`-root counts and ordered topology signatures, every
retained `f_tt` extremum is completely and unambiguously matched, and excluded
bracket/extremum reason signatures remain stable.  Crossing ambiguity,
unmatched extrema, root/topology changes, or filter-boundary changes are
persisted and emit a manual-review action; they are not automatically fold
evidence and cannot authorize the simplex fallback.

Every result and theta checkpoint hard-codes:

```json
"continuum_verified": false,
"project_gate_passed": false
```

## Round 11 adversarial correction and resolution

An independent replay found the original resume validator could accept a
checkpoint after changing `parameters.diffusion` to `999.0`, replacing
`claim_scope`, inflating `maximum_chunk_state_rows`, or replacing a Boolean
gate by a merely truthy value.  Single-file changes to `survival` or `f_ttt`
were also not integrity-bound.  Separately, Python equality allowed
manifest numeric-type coercions, nearest-time greedy matching could cross
branches, and several root-count/unmatched/filter-boundary cases could be
misreported as `line empty`.

All findings were corrected before the formal run:

- recursive JSON comparison now preserves exact Boolean/integer/float types;
- the pinned G1a producer code and canonical `PilotParameters`/endpoint
  contract are verified before assembly;
- every checkpoint is atomically entered in `integrity_ledger.json`, whose
  configuration/provenance metadata and file hashes are checked before JSON
  reuse; orphan, missing, interrupted, duplicate-key, and non-finite ledger
  states fail closed;
- a non-blocking `.run.lock` is held for the complete run, so a second process
  fails before any checkpoint/temp write; the wrong-`.venv` formal guard runs
  before lock-directory creation;
- resume freshly assembles the model and exactly recomputes parameters, grid,
  weights, gate names/Boolean values, and full foundation diagnostics, then
  checks runtime, curve, chunk, nonnegativity, initial-mass, survival, killed
  mass-balance, and generator-action bounds; and
- order-preserving matching plus transition signatures block ambiguous false
  `line empty` decisions and persist the reason for manual review.

The integrity ledger makes arbitrary single-checkpoint modification detectable
without repeating the expensive semigroup propagation.  Semantic validation
still rejects the replayed mutations after a test fixture deliberately
recomputes the ledger entry hash.

## Test evidence

Command:

```bash
PYTHONDONTWRITEBYTECODE=1 \
PYTHONPATH=research/reports/encounter_multimodal_prr/code \
.venv/bin/python -m pytest -q -p no:cacheprovider \
  research/reports/encounter_multimodal_prr/code/test_continuum_g1_discovery.py
```

Result:

```text
................................................ [100%]
48 passed
```

Twenty-five test functions, with parametrized attacks and boundary cases,
cover:

1. exact frozen-manifest validation, including rejection of added fields and
   Boolean/integer/float coercions;
2. the pinned 42-gate schema-3 artifact, producer-code hash, physical-parameter
   contract, and control-endpoint contract;
3. rejection of artifact/code/contract drift, status mismatch, and failed
   gates;
4. chunked curves versus one full `expm_multiply` history on the asymmetric
   `7 x 9 x 5` grid;
5. synthetic near-zero, strict adjacent-theta sign brackets, non-crossing
   matching, assignment ambiguity, unmatched extrema, root-count/topology
   changes, and excluded-filter transitions;
6. endpoint-only refusal at theta `0` and `1`, plus interior authorization for
   exact zeros at theta `0.1` and `0.9`;
7. exact-zero-run deduplication and refusal of a preanalysis plateau whose
   midpoint lands at the threshold;
8. all named Round 11 checkpoint mutations after deliberate ledger resealing;
9. raw checkpoint hash mismatch, orphan/missing/metadata ledger attacks,
   interrupted temporary files, and duplicate/non-finite ledger JSON; and
10. an independent-process single-writer collision and wrong-`.venv`
    pre-lock guard; and
11. small dry-run checkpoint creation, strict resume, complete curve storage,
    false stage flags, and rejection of a non-manifest formal configuration.

For the chunk/full-history comparison, all five curves agree within
`rtol=3e-12`, `atol=3e-13`, and the tested chunk held at most three state rows.

An additional five-pair process stress test used one shared checkpoint
directory per pair.  All `5/5` pairs produced exactly one successful dry-run
and one fail-fast `active writer` error; every surviving ledger had three
entries, every lock ended `RELEASED`, and no temporary file remained.

Static checks:

```text
ruff check: All checks passed!
ruff format --check: formatted state confirmed
```

## Executed dry-run

Only the small implementation run and its strict resume were executed:

- mesh: `7 x 9 x 5 = 315` states;
- theta values: `(0.0, 0.5, 1.0)`;
- time grid: `0, 0.25, 0.5, 0.75, 1.0`;
- chunk limit: `3` time rows;
- controls computed: `3`;
- resume check: `0` controls recomputed and `3` checkpoints strictly resumed;
- integrity ledger: `3` entries, all hashes reproduced before resume;
- single-writer metadata: `.run.lock` remained `status=RELEASED` after each
  invocation and no temporary file remained;
- full state history stored: `false`;
- pinned G1a certificate preflight: schema `3`, `42/42` gates true, PASS;
- current per-control hardened model gates: `38`, all true at each dry-run
  control;
- result: `DRY_RUN_COMPLETE`;
- `line_has_discovery_flag=true` only because one unmatched-extremum transition
  correctly triggered `topology_transition_requires_manual_review_before_line_action`;
- `interior_discovery_flag=false`;
- `continuum_verified=false`; and
- `project_gate_passed=false`.

The dry-run output and checkpoints were written under `/tmp`, not into the
report artifact tree.  Its absence from report artifacts is intentional.

The small run had no interior fold-candidate evidence.  Its conservative
manual-review flag demonstrates that an unmatched branch can no longer be
silently converted into `line empty`.  This implementation smoke has no
bearing on the frozen formal line or allowed simplex followup.

## Resume and provenance contract

Each completed theta is atomically written to `theta_<index>.json`, then its
SHA-256 is atomically bound into `integrity_ledger.json`.  Ledger validation
precedes checkpoint parsing.  A resumed checkpoint is rejected unless all of
the following agree:

- checkpoint schema and stage;
- `continuum_verified=false` and `project_gate_passed=false`;
- run mode and configuration hash;
- discovery code, smoke code, protocol, and manifest hashes;
- pinned G1a artifact/producer paths and SHA-256 values, canonical model
  contract, schema, stage, status, and 42/42 gate PASS;
- Python, NumPy, SciPy, platform, and repository-venv identity;
- theta index/value, physical weights, mesh, and exact time curve;
- exact checkpoint claim, parameters, grid, weights, runtime, chunk schema,
  curve types and physical bounds;
- fresh-model gate names, Boolean values, and recomputed diagnostics; and
- candidate analysis recomputed from the stored curves.

The aggregate result records every checkpoint SHA-256 and whether that theta
was computed or resumed during the invocation.

## Formal launch status

The certificate pin, strict preflight, action-rule repair, tests, and small
dry-run are complete.  The frozen manifest SHA-256 is:

```text
193c0fc1b7281dee2dd38b6c1152b73591dc0e0b82f5d3510edcd1e7e2dc7390
```

The final discovery-runner code SHA-256 audited here is:

```text
1411384398ed4e476dba15371cdfd662e94ed3a53cffdc02a1562201cfa7b52e
```

The matching protocol and executable test SHA-256 values are:

```text
protocol: 8cbf2469fab0c18982028450f5c3f0c1ff188c3105ae280c5448fcf1cf23125d
tests:    70d6aec2b8155961f170c7a791ea8fd3c57286110cd12810cbc9a8f684d4d71b
```

The exact formal command, recorded here but **not executed**, is:

```bash
PYTHONDONTWRITEBYTECODE=1 \
PYTHONPATH=research/reports/encounter_multimodal_prr/code \
.venv/bin/python \
  research/reports/encounter_multimodal_prr/code/continuum_g1_discovery.py \
  --execute-frozen
```

Running it will revalidate the pinned G1a artifact and repository `.venv`
before reading a checkpoint or assembling the first formal control.  Until
that explicit command is actually authorized and completes, there is no G1b
discovery result and no scientific conclusion from the formal line.
