# Round 88: general-dimension semantic-guard repair freeze

Date: 2026-07-14  
Predecessor: `audits/round_87_general_dimension_final_independent_recheck.md`  
Status: **SELF-REPAIR-FROZEN; INDEPENDENT RECHECK REQUIRED**

## 1. Repair boundary

Round 87 found no defect in the frozen scientific sources, but demonstrated
eight editorially nearby ways to bypass the scope test.  This round changes
only `code/test_general_dimension_scope_consistency.py`.  It does not edit a
theorem, manuscript source, numerical source, result, figure, compile
manifest, or canonical PDF, and it does not run a scientific producer.

The repair is deliberately conservative.  It normalizes common TeX and
Markdown spellings, recognizes equality and lower-bounded dimension forms,
requires a positive/finite-budget marker together with a numerical marker and
an affirmative evidence predicate in the same prose or table clause, and
rejects affirmative common-budget or dimension-uniform assertions even when a
canonical negative sentence remains elsewhere.  Clause-local matching avoids
misclassifying the blueprint's explicitly prohibited-claim column or the
legitimate physical-2D/3D shape comparison.

## 2. Mutation closure added to the living test

The committed mutation corpus now includes all eight Round 87 misses:

- `For $d=4$, positive-$B$ numerics are verified`;
- `physical dimension $d=4$` with finite-`B` verified numerics;
- standalone TeX `\(d=4\)` and positive-`B` verified numerics;
- `Physical $d=4$` without the old hyphen;
- `d\ge4`;
- finite-`B` numerics with a synonymous affirmative predicate;
- an affirmative equal/common-budget comparison inserted while preserving
  every required negative sentence; and
- dimension-independent constants/thresholds inserted while preserving every
  required negative sentence.

Two additional range/synonym mutations are frozen as regressions:
`d\ge2` with validated positive-budget computations and `d>3` with passing
finite-`B` simulations.  Additional common/shared-budget and
dimension-independent-threshold paraphrases are also frozen.

## 3. Verification and frozen bytes

Focused verification after the repair:

- `pytest -q code/test_general_dimension_scope_consistency.py code/test_living_scope_consistency.py code/test_compile_manuscript.py`: **18/18 PASS**;
- `uv run ruff check code/test_general_dimension_scope_consistency.py`: **PASS**.

The repaired guard is frozen at:

| File | SHA-256 |
| --- | --- |
| `code/test_general_dimension_scope_consistency.py` | `551350544c689873aca5ca897a8458b81a9df417199e9f091df466ec17b680bb` |

The authoritative science and canonical compiled artifact remain byte-identical
to Rounds 84--87:

| File | SHA-256 |
| --- | --- |
| `manuscript/encounter_multimodal_prr.tex` | `1c17be4ac1223fa769166cc13c4b551a1cf7925ae59a61a81021657421305c5b` |
| `manuscript/encounter_multimodal_prr_supplement.tex` | `4a5b3073d346fd50528d8c5a8fd51b914d94730c8d5b82def641627bfd168f07` |
| `notes/direct_physical_multimode_theorem.md` | `2b35d1b1053045220b29975d30f8b3c842d33273ca46de86b8cf7798c26a9c3d` |
| `notes/pde_mixed_jet_theorem.md` | `ac0e6cbb34d446d2b9ae2b52c22684ee72da7cadb04d864aacba085dff75f095` |
| `artifacts/data/manuscript_compile.json` | `795f8c2bdaced87414c4d87adbaf2a2ea813fb07dbee710669e9b42035b3f493` |
| `manuscript/encounter_multimodal_prr.pdf` | `fa4debf25af63f3c1d58cbc68b44d08b4c6add223e92207c18f7264bbf0774c6` |

## 4. Decision

The self-repair closes the demonstrated bypasses locally, but it does not
authorize **ACCEPT**.  A fresh independent in-memory mutation attack must use
the exact repaired test byte, include the Round 87 corpus, and add unseen
nearby paraphrases.  Until that independent gate returns P0/P1/P2 = 0/0/0,
the general-dimension scope remains on test-level HOLD.
