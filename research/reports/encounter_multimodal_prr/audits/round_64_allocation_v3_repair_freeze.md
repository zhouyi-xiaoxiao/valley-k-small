# Round 64: allocation-cusp v3 fail-closed repair and freeze

Date: 2026-07-14  
Role: implementer repair closure against the mandatory Round-61 contract  
Verdict: **HOLD-INDEPENDENT-PRERUN / NO-GO-65-97**

## 1. Non-execution boundary

This round repaired and froze the allocation-cusp package without running,
opening, generating, or deleting any mesh-65/97 scientific result.  It did not
run the post-result auditor.  The only model execution was the permitted
seven-cell explicit-CSR algebra dry run, twice.

The following five lexical paths were absent before and after the work and
were checked only for existence:

```text
artifacts/data/positive_b_allocation_cusp_discovery_result.json
artifacts/data/positive_b_allocation_cusp_discovery_reproducibility.json
artifacts/data/.positive_b_allocation_cusp_discovery_result.replica_1.json
artifacts/data/.positive_b_allocation_cusp_discovery_result.replica_2.json
artifacts/data/positive_b_allocation_cusp_discovery_independent_audit.json
```

This implementer record is not an independent authorization.  The new v3
manifest must receive a fresh result-blind independent pre-run attack before
the first scientific launch.

## 2. Frozen v3 anchors

| role | repository path | SHA-256 |
|---|---|---|
| external v3 manifest | `artifacts/data/positive_b_allocation_cusp_discovery_manifest.json` | `ef65491f9d169b672ffaf509399728dd21385aa73c85b8c9ba931b64a9dfd98f` |
| discovery runner | `code/positive_b_allocation_cusp_discovery.py` | `cef4d616520caefeba7ff437275500bdb3387cd9d79e38d9876a386d11c98bc4` |
| ordinary runner tests | `code/test_positive_b_allocation_cusp_discovery.py` | `69ff2b7b781977786fed91769c02037b8ccae2868784f221d5c50530e4baafbc` |
| Round-50 regressions | `code/test_positive_b_allocation_cusp_discovery_round50.py` | `30ecf71b426705efa2b6728048093d2da5b96d507c89edc43883579dc4847dbb` |
| Round-61 regressions | `code/test_positive_b_allocation_cusp_discovery_round61.py` | `90b106485ced34865426d572b01ea59ef98df8c627cf2cf9f77d98a809fb84a3` |
| discovery protocol v3 | `notes/positive_b_allocation_cusp_discovery_protocol.md` | `5f852cfd3d5342e60e8401cb486d26f8424a367f13a0dd2dd9d0b0e2ef80eee1` |
| Round-50 attack | `audits/round_50_allocation_discovery_prerun_attack.md` | `059e3f33b9a8e32cfe2e4ca26d1916dceac61b9fb53d89c77cdfdeb4a568829d` |
| mandatory Round-61 attack | `audits/round_61_allocation_v2_independent_prerun_attack.md` | `db1137c980113e09c5dba54efdad65903febb4c0c8b81e532743f890b11b48e0` |
| independent v3 auditor | `code/audit_positive_b_allocation_cusp_discovery_result.py` | `6b1cf7b8ca996161a59219b1f5f5be9cfc9c538ea09683a715084e017d057f4b` |
| independent auditor tests | `code/test_audit_positive_b_allocation_cusp_discovery_result.py` | `b8103510902ef2b5cb8558ff329ead8a811dc1bcfc5596d685a3dc0a2b783d3e` |
| no-cycle post-result protocol | `notes/positive_b_allocation_cusp_postresult_audit_protocol_v1.md` | `ad184fc3c8f586e5ce44d65a5bf6b5dc77bfdccaf471895280783d31a9837bc6` |

The canonical manifest contains 20 report-relative pins.  It pins both the
Round-61 report and its now-ordinary regression suite.  It intentionally does
not pin the independent auditor, auditor tests, or no-cycle protocol; the
auditor hard-codes the external manifest hash and the protocol records the
forward chain.

## 3. Round-61 closure matrix

| Round-61 finding | v3 disposition |
|---|---|
| P0-1 complete-scan physical fail-open | **closed**: full density/survival/state minima, survival-increase and mass-error maxima, saved rows, every bracketed root including ineligible roots, tails, and all six comparison scans share recursively reconstructed law gates |
| P0-2 local remote-pair collision | **closed**: cusp-anchor identity contains side, type, global ordinals, and origin brackets; every root carries global order, origin/current/previous bracket lineage, predecessor/successor, and adjacent drift; birth/death/crossing/replacement/unmatched/excess drift is HOLD |
| P1-1 weak replica validator | **closed**: exact v3 native schemas cover every homotopy, cusp, diagnostic, mesh, branch, control, phase, PASS, HOLD, and fixed not-run variant; terminal budget, trust-box, chart-weight, model-error, density-law, scope/timing/software/limitations, and all PASS implications are exact |
| P1-2 weak independent auditor | **closed in implementer package**: auditor independently reconstructs the same budget/trust/model/density identities, recursive schemas, cusp algebra, full scan laws, branch selection/lineage, individual basin masses, top-three advancement and representative membership; its suite includes a complete synthetic PASS plus budget/trust/density/model mutations |
| P1-3 lexical/TOCTOU gap | **closed under the explicit frozen assumption**: lexical `lstat`, `O_NOFOLLOW`, stable descriptors, metadata plus exact-byte snapshots, lazy FV import after validation, and complete initial/final comparisons are enforced; no-concurrent-writer and no-OneDrive-replacement are explicit |
| P2-1 incomplete absence boundary | **closed**: the parent requires the exact five-path absence set before either child, children permit only the already-declared earlier replica, evidence records the boundary, and pre-existing canonical/audit/staging paths are never silently deleted |

No scientific threshold was changed.  The only new numerical interface is the
result-blind `maximum_adjacent_root_time_drift = 1.0` required by Round 61;
all earlier physical, root, cusp, fold, and representative thresholds remain
unchanged.

## 4. Adversarial and reproducibility verification

The final frozen files passed:

```text
ruff format --check: 6 files already formatted
ruff check:            all checks passed
py_compile:            passed
pytest:                57 passed
```

The pytest set was exactly the ordinary discovery suite, converted Round-50
suite, expanded Round-61 suite, Stage-A algebra suite, and independent-auditor
suite.  It used unit fixtures/mocks and no scientific mesh above nine cells.

Two independent CLI invocations of the permitted `--algebra-dry-run --cells 7`
under manifest `ef6549...d98f` produced byte-identical stdout:

```text
bytes per run: 1061
SHA-256:       599faf2dacf08b13f4817bed70996f43553d048189e4fcd97d856fa3e8f8d69d
```

The regression suite now explicitly rejects full-scan and rejected-root law
violations, remote-root birth and excess drift, false scope, malformed nested
HOLD/PASS objects, inconsistent event basins/final state, duplicate JSON keys,
noncanonical evidence, symlink inputs, representative/ranking corruption, and
pre-existing staging deletion.

## 5. Implementer open count and release decision

Against the enumerated Round-61 repair contract, the implementer self-audit is

```text
P0 = 0
P1 = 0
P2 = 0
```

That count does not substitute for independent review.  The current release
state remains exactly:

```text
HOLD-INDEPENDENT-PRERUN
NO-GO-65-97
NO POST-RESULT AUDIT
NO MANUSCRIPT OR PUBLICATION CLAIM
```

Only a later independent result-blind audit may change the first-science launch
decision for external manifest SHA-256
`ef65491f9d169b672ffaf509399728dd21385aa73c85b8c9ba931b64a9dfd98f`.
