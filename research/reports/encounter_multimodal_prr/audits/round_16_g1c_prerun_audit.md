# Round 16: G1c full-simplex pre-run audit

Date: 2026-07-13  
Scope: independent adversarial audit of the prospectively frozen G1c
full-simplex runner; no formal `65 x 65 x 49` control was evaluated during
this audit  
Verdict: **PASS and authorized to execute the exact frozen formal G1c run.**

This authorization applies only to the byte-pinned manifest, runner, protocol,
and prerequisite artifacts recorded below. It authorizes a finite-grid
discovery screen over 66 controls. It does not authorize a fold claim, choose
a confirmation segment, verify a continuum result, or pass the project gate.

## Severity ledger

| Severity | Open findings | Disposition |
|---|---:|---|
| P0 | 0 | no claim-gate escape, evidence substitution, or destructive path alias |
| P1 | 0 | initial runner/protocol drift now fails before the first writable action |
| P2 | 0 | whole-edge-zero classification and path/symlink hardening are resolved |

Three defects were found in the first audited draft and fixed before this
verdict: the initial formal run did not independently pin the G1c runner and
protocol; a double-exact-zero matched edge was also mislabelled as a boundary
diagnostic; and custom output paths could collide with the checkpoint or
protected-input namespaces. The final runner was re-audited from the beginning
after all three repairs. None remains open.

## 1. Frozen byte-level scope

The final files reproduce these SHA-256 values:

| Object | SHA-256 |
|---|---|
| G1c manifest | `543ee21928cf009867bd194d3bb2f6929a3557458733c50ff613c2f664f1d593` |
| G1c runner | `0625212963c85d2068fa209924bfa7086f7b192edbbbbde6ffc6f9109cfb63a5` |
| G1c tests | `9a9457afde3db68a67840a37e3e22d42c71ee337bdef011b7b9d3cc2a73a5232` |
| G1c protocol note | `af337ba273a1b12be4317c7f6e40caf219855f240f56fa9411cfa1edde9e2f99` |
| pinned G1a artifact | `a0a1894dbe6dd37bad6973ca6f3dd29b651441f7b911a5406186bb86a18fd3c3` |
| pinned G1a producer | `e0322b212e466b1b640f5adcf30d67d119d2f6fe4cc622eb532082b6cd251701` |
| pinned G1b formal result | `2052c1d26211661995d6048b2cd3ca909f04ce48efb9a96c32bd153c7c63d40d` |
| pinned G1b producer | `1411384398ed4e476dba15371cdfd662e94ed3a53cffdc02a1562201cfa7b52e` |
| pinned manual-review result | `6f869fb4e961297a9ba4784c394fa56fbb083f1a89091aa0c27738331127de65` |
| pinned manual-review producer | `4453444abd878d771b59185aaee5371ae5d9c786fdb0da9222f25c0605035451` |

The manifest's `frozen_implementation.runner_sha256` and
`protocol_note_sha256` equal the reproduced G1c runner and protocol hashes.
The loader rejects a mutation to either pin before model assembly, lock-file
creation, or checkpoint creation. The prerequisite hashes and semantic fields
also reproduce: the 42-gate G1a certificate is all true; G1b is the completed
formal line with zero near-zero extrema, zero adjacent sign brackets, and its
manual-review flag; and the post-result diagnostic remains explicitly outside
predeclared discovery evidence and leaves both project claim flags false.

The final formal output and checkpoint directory were absent at the end of
this pre-run audit. Default-path validation passed.

## 2. Frozen design and independent combinatorics

The formal configuration reconstructed from the manifest is exactly:

```text
state mesh             65 x 65 x 49 = 207025 states
simplex denominator    10
controls               all (i,j,k)/10 with i+j+k=10: 66
enumeration            increasing (i,j)
adjacency               integer L1 distance 2
undirected edges        165
time grid               0, 0.25, ..., 80: 321 points
maximum chunk rows      41
```

The 66 controls and 165 edges were recomputed independently. The dry-run path
uses all the same controls and edges while replacing only the state mesh by
`7 x 9 x 5 = 315` and the time grid by five implementation-only samples. A
formal configuration differing from the manifest is rejected before a
checkpoint directory is created. The formal CLI also requires the explicit
`--execute-frozen` flag and the repository `.venv`.

## 3. Arbitrary-weight model construction

The arbitrary control is assembled directly as

```text
kappa = (installed_budget / transverse_width)
        * (weights @ patch_cell_averages)
killing = kron(kappa, contact_fraction_relative)
Q_killed = Q_free - diag(killing)
```

It is not reconstructed through the legacy one-dimensional `theta` line.
`theta=0` and the zero derivative fields are inert implementation sentinels;
the observable evaluator reads the newly assembled killed generator and
killing vector.

Across all 66 dry-run controls, every one of the 17 arbitrary-weight gates was
true. The physical installed budget ranged only from
`0.6000000000000001` to `0.6000000000000004`; the maximum relative error was
`7.401486830834377e-16`. Every stored weight vector equalled the direct
triplet-to-simplex conversion, all generator actions were finite, all
off-diagonal and killed-mass gates passed, and no full state history was
stored.

## 4. Candidate, boundary, and three-valued gate semantics

Synthetic adversarial controls verified the intended branches independently:

| Case | Eligible seed | Manual review | Family gate |
|---|---:|---:|---|
| strict sign crossing between two boundary controls, interpolated weights strictly interior | 1 | no | `true` |
| exact zero at a strictly interior endpoint | 1 | no | `true` |
| exact zero at a boundary endpoint | 0 | no | `false` |
| strict sign crossing confined to a simplex face | 0 | no | `false` |
| double exact zero on an interior--interior edge | 0 | yes | `null` |
| no candidate and stable topology | 0 | no | `false` |
| no candidate with unmatched topology | 0 | yes | `null` |

The double-zero case is now stored only in
`unresolved_whole_edge_zero_matches`; it is not misreported as a
boundary-touching sign diagnostic and cannot select a segment. A candidate
plus a topology flag remains a candidate seed requiring review, never a fold
confirmation. In every branch,
`candidate_automatically_confirms_fold=false`,
`candidate_automatically_selects_segment=false`, and
`confirmation_segment_authorized=false`.

## 5. Complete dry run and deterministic replay

One fresh 66-control dry run completed with:

```text
status                         DRY_RUN_COMPLETE_IMPLEMENTATION_DIAGNOSTIC_ONLY
controls computed/resumed      66 / 0
simplex edges                  165
eligible candidate seeds       0
topology review required       true
family gate                    null (INCONCLUSIVE_MANUAL_REVIEW)
continuum_verified             false
project_gate_passed            false
ledger entries                 66
ledger SHA-256                 b4360b181584af9d77d18bdbdd82194e538b738e5592abf919b27bff5b929e06
```

The dry-run topology result is an implementation diagnostic on a one-unit
time window, not a preview of the formal scientific outcome. A second
invocation resumed all 66 controls and computed none; the ledger hash was
unchanged. A separate fresh directory then recomputed all 66 controls. Its
configuration, shared foundation, control order, every observable curve,
every arbitrary-weight diagnostic, every per-control candidate analysis, and
the complete simplex analysis were exactly equal to the first fresh run.

The ledger contained 66 unique indices and triplets, every checkpoint hash
reproduced, and the run lock ended in `RELEASED` state with the matching
configuration hash.

## 6. Adversarial fail-closed checks

All of the following temporary mutations or path attacks were rejected:

| Attack | Guard that fired |
|---|---|
| mutate a checkpoint without changing its ledger entry | checkpoint SHA-256 mismatch |
| set `continuum_verified=true` and recompute the ledger hash | hard-false checkpoint field check |
| alter the initial density and recompute the ledger hash | fresh-model generator-action check |
| alter the ledger configuration hash | ledger/configuration equality check |
| remove the ledger while retaining checkpoints | orphan-checkpoint check |
| leave an interrupted checkpoint temporary file | interrupted-write check |
| alter the frozen runner pin | runner SHA-256 check |
| alter the frozen protocol pin | protocol SHA-256 check |
| place output inside the checkpoint namespace | namespace-separation check |
| alias output to the manifest | protected-input check |
| make the checkpoint directory contain protected inputs | protected-namespace check |
| use a symlink as output, checkpoint directory, or run lock | symlink checks |
| use a directory as output or a file as checkpoint directory | path-type checks |
| hold the advisory lock in another process | nonblocking single-writer check |
| simulate execution outside the repository `.venv` | formal runtime check before directory creation |

The concurrency attack returned nonzero, reported the existing lock owner,
and created no output. The claim and curve mutations were deliberately
rehashed in the ledger so that the semantic replay checks, not only the first
hash layer, were exercised.

## 7. Regression result

The final focused suite passed:

```text
G1c tests                 22 passed
G1a/G1b/manual/G1c tests  91 passed
ruff check                PASS
ruff format --check       PASS
```

The manifest is valid JSON, the audited text/code files contain no detected
control characters, and rechecking after the tests reproduced all four G1c
hashes in Section 1.

## 8. Formal-run authorization and boundary

**Formal G1c execution is authorized**, provided the exact byte pins in
Section 1 remain unchanged and the default disjoint result/checkpoint paths
are used. The authorized runner invocation is:

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python \
  research/reports/encounter_multimodal_prr/code/continuum_g1c_simplex.py \
  --execute-frozen
```

Wrapping that command with `caffeinate` or a lower process priority does not
change the frozen scientific execution. Resume is permitted through the
default integrity ledger.

After completion, a separate result audit is mandatory. It must reproduce
the manifest/runner/protocol/input hashes, all 66 checkpoint hashes, the
165-edge analysis, and the three-valued family status. Even a returned
candidate is only a seed for at most one separately frozen confirmation
segment. No finite G1c outcome by itself verifies a continuum fold, cusp,
multimodality theorem, or PRR-level project gate.
