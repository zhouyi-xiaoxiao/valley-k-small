# Round 07 resolution — Lean statement fidelity and proof workflow

Date: 2026-07-11  
Status: **PASS for formal correctness and workflow; clean-tag release gate remains explicit**

## Decision

Two independent audits agree that the package builds and contains exactly
`100 = 46 + 54` theorems, with encounter modules split `14/28/12`.  Every
theorem is covered once by one of four axiom drivers, and all 100 live rows use
only `propext`, `Classical.choice`, and `Quot.sound`.  No `sorry`, `admit`,
project `axiom`, `native_decide`, or numerical/PDE theorem overclaim was found.

Lean certifies finite algebra, derivative identities, coordinate identities,
capacity-power algebra, and conditional design identities.  It does not certify
PDE well-posedness, Green-operator domains, floating-point roots, grid limits,
continuum modality, or physical applicability of assumptions.

## Remediation ledger

1. **Axiom coverage and fail-closed output parsing (B2, closed).**  The verify
   profile runs all four drivers, statically enforces the exact theorem
   partition and forbidden-token policy, and converts unexpected live axiom
   output into a nonzero stage result.
2. **Partial-run false pass (B2, closed).**  `execution.complete` now requires
   the exact ordered expected stage list, no setup/runtime failures, and zero
   return codes.
3. **Failed-attempt retry deadlock (B1, closed).**  Immutable run-ID attempt
   manifests retain failures, while canonical profile proofs are replaced only
   by complete successes.  A regression executes pass--fail--pass and verifies
   that the failed attempt remains auditable without poisoning the retry.
4. **Preflight and concurrency gaps (B1/B2, closed).**  Missing `lake`, missing
   cache, malformed runtime locks, and artifact-lock collisions are recorded as
   incomplete attempts with the full expected-stage contract.  A global
   artifact lock prevents full/quick/verify races; a second lock protects the
   shared mathlib cache during Lean stages.
5. **Statement fidelity (B2, closed).**  README and manuscript now describe the
   affine results as scalar/componentwise, capacity as pure `a^(d-2)` power
   algebra without a capacity theorem or constant, and prescribed GIG action as
   stationarity rather than formal uniqueness/maximality.
6. **Clean-tag provenance (release gate, open by design).**  The current research
   workspace is dirty and contains untracked encounter files.  It can support a
   hashed working-tree proof, but it must not be labeled a clean-tag submission
   release until the user freezes the repository and reruns the release profile.

## Revalidation

Reviewer B completed a fresh isolated `3109/3109` Lean build and four live axiom
reports (`46/14/28/12`).  Reviewer A independently reproduced the source/driver
inventory.  Targeted pipeline regressions for formal integrity, partial runs,
preflight failure, immutable logs, and fail--retry semantics pass in the current
snapshot.  The final verify profile will rerun the same live build after all ten
audit rounds are frozen.
