# Round 186: manuscript-completion contract independent attack

Date: 2026-07-19  
Reviewer role: independent read-only claim/state-machine attacker  
Final decision: **ACCEPT EXACT BYTES / PRE-F0 CONTRACT ONLY / NO SCIENCE AUTHORIZED**  
Final findings: **P0 = 0, P1 = 0, P2 = 0**

## Scope

The review attacked:

- `notes/manuscript_completion_contract_v1.md`;
- `artifacts/data/manuscript_completion_contract_v1.json`;
- `code/validate_manuscript_completion_contract_v1.py`;
- `code/test_manuscript_completion_contract_v1.py`; and
- the current 36-row authority
  `notes/positive_b_fixed_control_robustness_design_v2.md`.

It checked the paper-level claim ceiling, the conditional strict-continuum
gate, exact control and configuration order, no-refit coverage, F0
capabilities, terminal branch completeness, source pins, canonical JSON, and
fail-closed claim mutations.  It did not inspect a positive-budget numerical
result and did not authorize F1.

## Findings and repair loop

The first attack returned `P0=0, P1=4, P2=2`.  It found:

1. no terminal branch for `PASS_F1_ALL_ROWS` followed by `HOLD_F2`;
2. no machine predicates tying branches to exact F0--F3 statuses and failure
   classes;
3. a no-refit list weaker than the living design; and
4. tests that allowed exact-control permutation and deletion or mutation of
   claim-bearing fields.

The repaired contract added a distinct F2 hold, separated F3 science from
method/resource holds, encoded exact upstream statuses and failure classes,
expanded the no-refit and F0 capability sets, and added a reusable validator
plus mutation tests.

The second attack returned one remaining P1.  The validator checked each
self-declared source hash against its self-declared path but did not freeze the
complete label-to-path-to-hash mapping, root-key set, or limitations.  It
therefore allowed source deletion or redirection, an extra authorization
field, and deletion of limitations.

The final repair froze all three sets exactly and added the corresponding
mutations.  The final reviewer replay found no open issue.

## Final accepted bytes

| Object | SHA-256 |
| --- | --- |
| human-readable contract | `cf60bad1680d487e610811c60e5d9e37fa27a87b935f94adcf83a5b8b6ec716d` |
| machine-readable contract | `f32fee61edb48fad4e0da0ad5e747db8c417fd25c3acb18da74354c60ec68ee0` |
| fail-closed validator | `f7eb328ecfa2b57eec17bdad5586bff1162972d44c48949d77a1b55ee7865890` |
| focused test | `8f09cee41494a5427cbcb2f306422b2a8d8b5e18280e95eaf9a4a2f0cffa173e` |
| current 36-row design | `264cf2d2ef17feedcb3c1a5469e18b5c57ba5981b57dc6201147955df3684dcd` |

## Independent checks

The final read-only review reported:

```text
focused mutation/contract cases     18 passed
validator CLI                       PASS_CONTRACT_V1_VALIDATION
strict duplicate-key parsing        PASS
canonical sorted JSON bytes          PASS
py_compile                           PASS
P0 / P1 / P2                         0 / 0 / 0
```

The accepted mutation surface rejects:

- exact-control permutation;
- theorem or forbidden-claim deletion;
- no-refit or F0-capability weakening;
- PASS-branch permission/action changes;
- F2 predicate promotion;
- immutable-source deletion or redirection;
- limitation deletion; and
- an extra top-level scientific-authorization field.

## Exact acceptance boundary

This is acceptance of a pre-F0 claim and terminal-branch contract only.  The
contract itself records:

```text
authorized_scientific_command = null
f0_independently_accepted      = false
f1_authorized                  = false
submission_eligible            = false
```

It permits the focused manuscript to use the accepted exact-`m` theorem and,
only after the relevant future gates pass, finite-window,
continuum-consistent physical-`d=2` evidence.  It does not accept F0, create an
F1 manifest, inspect any of the three production controls, establish C0--C3,
or release a manuscript.
