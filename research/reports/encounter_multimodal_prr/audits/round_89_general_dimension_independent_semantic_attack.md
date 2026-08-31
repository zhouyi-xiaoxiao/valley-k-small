# Round 89: independent general-dimension semantic-guard attack

Date: 2026-07-14  
Predecessor: `audits/round_88_general_dimension_semantic_guard_repair.md`  
Status: **HOLD-SEMANTIC-GUARD**

## 1. Boundary and decision

This was a read-only independent attack on the exact Round 88 test byte.  No
test, scientific source, numerical source/result, compile manifest, or
canonical PDF was edited.  No producer or compile command was run.  All
mutations existed only in memory: the eight living surfaces were loaded once,
one copy was changed per case, and the test module's `_read` function was
redirected to that copy.

The exact Round 87 corpus is repaired: **15/15 mutations were CAUGHT**.
However, an independent 50-case extension produced only **10 CAUGHT / 40
MISSED**, and 3 of 10 legitimate controls were false positives.  The result is:

| P0 | P1 | P2 | Decision |
| ---: | ---: | ---: | --- |
| 0 | 0 | 1 | **HOLD-SEMANTIC-GUARD; ACCEPT NOT AUTHORIZED** |

The P2 is confined to the test-level release guard.  The exact current
scientific sources remain correct and unchanged; this audit found no P1
scientific-claim defect.

## 2. Frozen objects verified before attack

Both frozen inputs matched the requested hashes exactly:

| File | SHA-256 |
| --- | --- |
| `code/test_general_dimension_scope_consistency.py` | `551350544c689873aca5ca897a8458b81a9df417199e9f091df466ec17b680bb` |
| `audits/round_88_general_dimension_semantic_guard_repair.md` | `3fb37415bafdbd6b6dddcc5b0f693206d2d9085151959d0e599485b5676d50f4` |

For every mutation, all four tests in the frozen scope module were called.  A
case was **CAUGHT** when any test raised and **MISSED** only when all four
returned normally.  Thus an internal mutation test could not be mistaken for
coverage merely because the baseline test file contained the target string.

## 3. Round 87 corpus replay: 15/15 CAUGHT

| # | Replayed mutation | Result |
| ---: | --- | --- |
| 1 | Direct-note uniform/cross-dimension reversal | **CAUGHT** |
| 2 | Mixed-note common-numerical-budget reversal | **CAUGHT** |
| 3 | `Physical-$d=4$ positive-budget numerical evidence is complete` | **CAUGHT** |
| 4 | Direct-note dimension-independent positive synonym | **CAUGHT** |
| 5 | Mixed-note shared-budget positive synonym | **CAUGHT** |
| 6 | Reverse the boxed epsilon-then-`B` quantifier order | **CAUGHT** |
| 7 | `Physical-\(d=4\) finite-budget numerical evidence is complete` | **CAUGHT** |
| 8 | `For $d=4$, positive-$B$ numerics are verified` | **CAUGHT** |
| 9 | `physical dimension $d=4$` with verified finite-`B` numerics | **CAUGHT** |
| 10 | Standalone TeX `\(d=4\)` with verified positive-`B` numerics | **CAUGHT** |
| 11 | `Physical $d=4$` without a hyphen | **CAUGHT** |
| 12 | Range form `Physical-$d\ge4$` | **CAUGHT** |
| 13 | `Physical-$d=4$ finite-$B$ numerics are verified` | **CAUGHT** |
| 14 | Preserve the negative sentence, then inject common-`B` comparability | **CAUGHT** |
| 15 | Preserve the negative sentence, then inject dimension-uniform constants | **CAUGHT** |

This confirms the narrow claim made by Round 88: every demonstrated Round 87
bypass is now executable and rejected.

## 4. Independent Round 89 mutations: 10/50 CAUGHT

### 4.1 Dimension, budget, evidence, and clause-format attacks

| ID | Injected affirmative claim or format | Result |
| --- | --- | --- |
| N01 | `For dimension $d = 10$, positive $B$ calculations are accepted.` | **CAUGHT** |
| N02 | `At $d=12$, finite budget solver evidence is established.` | **CAUGHT** |
| N03 | `For $d>2$, positive budget computations are numerically established.` | **CAUGHT** |
| N04 | `For $d>=1$, finite $B$ simulations are confirmed.` | **CAUGHT** |
| N05 | Unicode/spaced `d ≥ 4` with accepted positive-`B` calculations | **MISSED** |
| N06 | Unicode/spaced `d ≥ 10` with established finite-volume solver evidence | **MISSED** |
| N07 | Set form `$d\in\{4,5,6\}$` with accepted positive-`B` calculations | **MISSED** |
| N08 | English range `d at least 4` with established finite-`B` solver evidence | **MISSED** |
| N09 | `four-dimensional` with accepted positive-`B` calculations | **MISSED** |
| N10 | `dimensions above three` with established finite-`B` solver evidence | **MISSED** |
| N11 | `all fixed dimensions` with accepted positive-`B` calculations | **MISSED** |
| N12 | `d=10` with accepted `nonzero B` calculations | **MISSED** |
| N13 | `d=10` with accepted `B>0` calculations | **MISSED** |
| N14 | `d=10` with `positive-B calculations are reproducible` | **MISSED** |
| N15 | `d=10` with `positive-B calculations agree with the solver` | **MISSED** |
| N16 | Evidence first, then separate sentence `This result applies at d=10` | **MISSED** |
| N17 | Dimension first, then separate sentence `Positive-B calculations are accepted` | **MISSED** |
| N18 | `For d=4 at B=0.01, positive-B numerics are verified.` | **MISSED** |
| N19 | `For d=4 at B=10^{-2}, positive-B numerics are verified.` | **CAUGHT** |
| N20 | `For d=4, e.g., positive-B numerics are verified.` | **MISSED** |
| N21 | A newline between `d=4` and `positive-B numerics are verified` | **CAUGHT** |
| N22 | Table cells `\| d=4 \| positive-B numerics are verified \|` | **MISSED** |
| N23 | `For d=4 at B=.01, positive-B numerics are verified.` | **MISSED** |
| N24 | `For d=4, Dr. Lee verified the positive-B numerics.` | **MISSED** |

The decimal contrast N18/N19 is decisive.  The TeX power is caught, but the
ordinary value `0.01` is missed because `_local_clause` treats the
decimal point as the end of the clause before reaching the evidence predicate.
The same structural error explains leading decimals and abbreviations.  A
newline is normalized to whitespace and is caught, whereas a Markdown table
cell boundary fragments the claim and is missed.

### 4.2 Common/shared/equal budget-comparison attacks

| ID | Injected affirmative claim | Result |
| --- | --- | --- |
| C01 | Same nondimensionalized budget is compared across physical dimensions | **CAUGHT** |
| C02 | A common dimensional budget can be compared between dimensions | **CAUGHT** |
| C03 | Equal nondimensionalized budgets are comparable across dimensions | **CAUGHT** |
| C04 | All dimensions use one shared nondimensionalized budget | **MISSED** |
| C05 | The common dimensional budget is portable across dimensions | **MISSED** |
| C06 | Equal numerical values are identified between physical dimensions | **MISSED** |
| C07 | One shared reaction budget is benchmarked between dimensions | **MISSED** |
| C08 | No restriction prevents comparing the same dimensional budget across dimensions | **MISSED** |
| C09 | It is not only possible but valid to compare a common budget across dimensions | **MISSED** |
| C10 | Comparison of a shared dimensional budget across dimensions is allowed | **CAUGHT** |
| C11 | Common budget in one sentence; values compared across dimensions in the next | **MISSED** |
| C12 | Across dimensions, one common dimensional budget applies unchanged | **MISSED** |
| C13 | Nondimensionalization makes equal budgets commensurate across dimensions | **MISSED** |
| C14 | The theorem permits use of equal dimensional budgets between dimensions | **MISSED** |

The comparison guard is lexical rather than semantic.  It recognizes forms of
`compare`, but not `use`, `portable`, `identified`,
`benchmarked`, `applies unchanged`, `commensurate`, or
`permits use`.  Its prefix-only negation heuristic also treats `No
restriction prevents ...` and `not only possible ...` as negative,
although both sentences affirm the forbidden comparison.

### 4.3 Uniform-in-d constants, thresholds, amplitudes, and masses

| ID | Injected affirmative claim | Result |
| --- | --- | --- |
| U01 | Constants are `uniform-in-d` | **MISSED** |
| U02 | `B_0` is uniform in `d` | **MISSED** |
| U03 | Amplitudes are uniform across `d` | **MISSED** |
| U04 | Event masses are `uniform-in-d` | **MISSED** |
| U05 | Constants are `d-independent` | **MISSED** |
| U06 | One `B_0` exists for every physical dimension | **MISSED** |
| U07 | One set of amplitudes works in all dimensions | **MISSED** |
| U08 | Event masses do not depend on physical dimension | **MISSED** |
| U09 | Physical dimension does not affect the threshold | **MISSED** |
| U10 | No limitation prevents constants from being uniform across dimensions | **MISSED** |
| U11 | Double negation: `not true that B_0 is not uniform across dimensions` | **MISSED** |
| U12 | `The constants are uniform.` followed by a sentence applying it across dimensions | **MISSED** |

All 12 uniformity variants were missed.  In particular, the guard requires a
literal form of `dimension` in the same clause as its uniformity match,
so the central editorial forms `uniform-in-d`, `uniform in d`,
`uniform across d`, and `d-independent` all bypass it.  The other
cases demonstrate predicate synonyms, cross-sentence assembly, and negation
scope that a finite regular-expression list does not safely resolve.

The full independent tally is therefore:

| Family | CAUGHT | MISSED | Total |
| --- | ---: | ---: | ---: |
| Dimension/budget/evidence/clause formats | 6 | 18 | 24 |
| Cross-dimensional budget comparisons | 4 | 10 | 14 |
| Dimension-uniform objects | 0 | 12 | 12 |
| **Total** | **10** | **40** | **50** |

## 5. False-positive controls: 7/10 PASS

Each control was intended to be legal and was passed directly through both
semantic helpers.  **PASS** means no helper raised; **FALSE POSITIVE** means a
legal control was rejected.

| ID | Legal control | Result |
| --- | --- | --- |
| F01 | The exact current eight living surfaces | **PASS** |
| F02 | The exact current blueprint, including its prohibited-claim table | **PASS** |
| F03 | `A shared dimensional budget is not compared across dimensions.` | **PASS** |
| F04 | `For d=10, positive-B numerical evidence is not established.` | **FALSE POSITIVE** |
| F05 | `No positive-B computations have been run for d=10.` | **PASS** |
| F06 | `A comparison of a shared dimensional budget across dimensions is not permitted.` | **FALSE POSITIVE** |
| F07 | `The B=0 shapes are compared between physical dimensions d=2 and d=3.` | **PASS** |
| F08 | `The zero dimensional budget B=0 is compared between physical dimensions d=2 and d=3.` | **FALSE POSITIVE** |
| F09 | `For d=3, positive-B numerical calculations are accepted.` | **PASS** |
| F10 | `For d=2 at B=0, the finite-volume shape comparison is established.` | **PASS** |

The current forbidden-item table and the exact living sources are not
misclassified, which explains the green baseline.  That success is not
general.  The numerical helper does not apply negation scope to its affirmative
tokens, so F04 is killed merely because `evidence` and
`established` occur.  The comparison helper looks only for negation
before the comparison token, so the postposed `is not permitted` in F06
is ignored.  F08 shows that spelling out `zero dimensional budget` turns
a legitimate physical-`d=2/d=3`, `B=0` shape comparison into a
false positive.

## 6. Baseline verification and unchanged science

The requested focused commands pass on the exact frozen byte:

- `pytest -q code/test_general_dimension_scope_consistency.py code/test_living_scope_consistency.py code/test_compile_manuscript.py`: **18/18 PASS**;
- `python -m ruff check code/test_general_dimension_scope_consistency.py`: **PASS**.

The baseline PASS cannot override the adversarial results above.  The exact
scientific objects and canonical artifact remain byte-identical to Rounds
84--88:

| File | SHA-256 |
| --- | --- |
| `manuscript/encounter_multimodal_prr.tex` | `1c17be4ac1223fa769166cc13c4b551a1cf7925ae59a61a81021657421305c5b` |
| `manuscript/encounter_multimodal_prr_supplement.tex` | `4a5b3073d346fd50528d8c5a8fd51b914d94730c8d5b82def641627bfd168f07` |
| `notes/direct_physical_multimode_theorem.md` | `2b35d1b1053045220b29975d30f8b3c842d33273ca46de86b8cf7798c26a9c3d` |
| `notes/pde_mixed_jet_theorem.md` | `ac0e6cbb34d446d2b9ae2b52c22684ee72da7cadb04d864aacba085dff75f095` |
| `artifacts/data/manuscript_compile.json` | `795f8c2bdaced87414c4d87adbaf2a2ea813fb07dbee710669e9b42035b3f493` |
| `manuscript/encounter_multimodal_prr.pdf` | `fa4debf25af63f3c1d58cbc68b44d08b4c6add223e92207c18f7264bbf0774c6` |

No current source promotes positive-budget physical numerical evidence above
`d=3`, claims common dimensional budgets are comparable across
dimensions, or asserts dimension-uniform constants, `B_0`, amplitudes,
or event masses.

## 7. Closure recommendation

Adding more natural-language regular expressions is not a general closure.
The 40 false negatives and 3 false positives arise from syntax, punctuation,
clause assembly, and negation scope, not merely from eight missing words.

The defensible release boundary is an **exact-byte claim-surface freeze**:

1. hash all eight audited living surfaces as one scope contract;
2. fail closed on any byte change until that new surface set receives an
   explicit independent scientific re-audit; and
3. retain semantic assertions as diagnostics, not as proof that arbitrary
   future prose is safe.

That architecture closes unknown synonyms, Unicode forms, cross-sentence and
cross-table composition, decimal/abbreviation punctuation, and negation-scope
ambiguity uniformly.  It must itself be independently tested for all eight
surfaces and for fail-closed behavior before ACCEPT.  On the present frozen
guard, the final Round 89 decision remains **P0/P1/P2 = 0/0/1,
HOLD-SEMANTIC-GUARD**.
