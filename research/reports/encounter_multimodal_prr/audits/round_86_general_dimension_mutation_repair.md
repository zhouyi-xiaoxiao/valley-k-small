# Round 86: general-dimension semantic mutation-guard repair

Date: 2026-07-14  
Predecessor: `audits/round_85_general_dimension_independent_recheck.md`  
Status: **SELF-REPAIR PASS / HOLD-INDEPENDENT-RECHECK**

## Boundary

Round 85 accepted every scientific source, the canonical PDF, and the explicit
dimensional normalization, but found one P2 in test coverage. This round edits
only `code/test_general_dimension_scope_consistency.py`. No manuscript,
Supplement, theorem note, numerical source/result, scientific producer, or
auditor was changed or run.

## Repair

The scope guard now enforces explicit negative contracts separately in the
main article, Supplement, direct theorem note, and mixed-jet note. In
particular it requires:

- the direct note's statement that dimensional budget, amplitudes, event
  masses, and \(B_0\) are **not** uniform or compared across dimensions;
- the mixed-jet note's statement that the theorem makes **no**
  cross-dimensional comparison at a common numerical dimensional budget;
- the Supplement's no-common-numerical-budget and no-uniformity statements;
  and
- absence, across all eight living scope surfaces, of any physical-\(d>3\)
  positive-/finite-budget numerical-evidence promotion.

Three executable mutations reproduce the exact Round 85 misses: reversing the
direct-note statement, reversing the mixed-note statement, and injecting a
false physical-\(d=4\) positive-budget numerical-evidence claim. All three now
raise, in addition to the earlier four main-theorem mutations.

## Verification and frozen byte

- General-dimension plus living-scope tests: **6/6 PASS**.
- Ruff: **PASS**.
- Repaired test SHA-256:
  `c7b89b9f451573df7e517e77efc7309e038ce251ae862461753c0b8c2475e157`.
- Self-audit: `P0=0, P1=0, P2=0`.

Only an independent test-level recheck is authorized. The project-level
scientific HOLD remains unchanged.

