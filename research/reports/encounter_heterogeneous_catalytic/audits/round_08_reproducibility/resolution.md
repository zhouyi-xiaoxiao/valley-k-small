# Round 08 resolution — reproducibility and submission artifacts

Date: 2026-07-11  
Status: **PASS for research reproducibility; external submission release remains HOLD**

## Decision

The two independent reports describe different snapshots of the same repair
cycle. Reviewer A correctly found that the first generated package did not yet
contain fresh canonical `full` and `verify` proofs, a complete ten-round audit
inventory, or an author-owned release record. Reviewer B then independently
challenged the remediated workflow and closed the implementation-level B1 and
B2 findings. The research package now passes this round as a deterministic,
fail-closed, single-workspace reproduction system. It is not being certified as
an externally released submission archive.

## Closed reproducibility findings

1. **Deterministic stages.** Every pipeline stage is executed with the frozen
   `SOURCE_DATE_EPOCH`, `FORCE_SOURCE_DATE=1`, and `TZ=UTC` environment. The
   final scientific run is `20260711T083125522558Z-62483`: all 16 expected
   stages returned zero, `execution.complete=true`, `failures=[]`, and the
   manifest records 90 source files, 100 outputs, and four formal-evidence
   artifacts.
2. **Success-only proof semantics.** Every attempt has an immutable run-id
   manifest. A failed or partial attempt remains visible but cannot replace a
   canonical passing profile. The canonical profile is published only after
   the complete ordered stage set, live hashes, logs, and output inventory have
   passed.
3. **Lock exclusion.** A process that loses the workspace lock exits with code
   75 before inspecting stages or writing a manifest. It cannot contaminate a
   concurrent successful run or its aggregate proof.
4. **Notebook fail-closed behavior.** The reader notebook consumes the matched
   JSON representation of nested diagnostics, executes 18 code cells without
   errors, and is guarded by notebook-content and execution tests.
5. **Transitive source evidence.** The publication inventory follows the direct
   `vkcore` dependency closure used by the report, including `__init__.py`,
   finite-FPT, morphology, plotting, and provenance modules. The verify profile
   directly includes the corresponding FPT, morphology, and provenance test
   suites.
6. **Formal boundary.** The Lean layer contains 100 algebraic theorems and a
   clean 3,109-job build. Its four axiom reports expose only `propext`,
   `Classical.choice`, and `Quot.sound`; the package makes no claim to have
   formalized PDE convergence or numerical root existence.
7. **Staged release ancestry.** The release checker requires an ordered
   source-tag, artifact-tag, and final-tag ancestry chain. A dirty untagged
   development run cannot satisfy that gate.

Reviewer B's sealed report has SHA-256
`7532b14063f542eeeef68e4a984048c5d286ee17084006aafdd7d802b731b080`.
Reviewer A's earlier mechanical concerns are retained as historical evidence;
they are not silently deleted or reclassified as scientific failures.

## Retained release hold

The current checkout is intentionally not labelled submission-ready. It is
dirty, has no exact release tag, and still requires author names/order,
affiliations, corresponding-author details, ORCIDs, funding, conflict and CRediT
statements, a public archive DOI and license, and final PRE data/code wording.
Those facts cannot be inferred by the pipeline. After they are supplied, the
documented clean-tag `full --release` / artifact-tag / `verify --release` /
final-tag chain must be run and checked with
`check_publication_proofs.py --require-clean-tag`.

The canonical seven-stage development `verify` run is deliberately performed
only after Round 08 and Round 10 resolutions and the final audit ledger are
frozen, so its aggregate proof hashes the complete audit record.
