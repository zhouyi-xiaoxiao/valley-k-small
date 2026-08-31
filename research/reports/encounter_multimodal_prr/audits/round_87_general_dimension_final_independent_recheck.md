# Round 87: final independent general-dimension guard recheck

Date: 2026-07-14  
Predecessor: `audits/round_86_general_dimension_mutation_repair.md`  
Status: **HOLD-MUTATION-COVERAGE**

## 1. Boundary and decision

This was a read-only independent recheck of the Round 86 test-only repair.  It
did not edit or run a scientific producer, numerical result, theorem source,
manuscript source, compile manifest, or canonical PDF.  It did not recompile
the article or Supplement.  Every adversarial mutation described below was
held only in memory by monkeypatching the test module's `_read` function.

Round 86 does catch all three exact Round 85 misses.  It also catches a
reversed epsilon-then-budget quantifier order and positive synonymous
replacements of the two protected negative contracts.  It nevertheless
misses eight nearby, scientifically equivalent scope promotions.  Therefore
the independent decision is:

| P0 | P1 | P2 | Decision |
| ---: | ---: | ---: | --- |
| 0 | 0 | 1 | **HOLD-MUTATION-COVERAGE** |

The P2 is a test-coverage defect, not a defect in the current scientific
sources.  **ACCEPT is not authorized.**

## 2. Exact object under test

The Round 86 scope guard was independently hashed before the attack:

| File | SHA-256 |
| --- | --- |
| `code/test_general_dimension_scope_consistency.py` | `c7b89b9f451573df7e517e77efc7309e038ce251ae862461753c0b8c2475e157` |

Focused baseline verification on that byte passed:

- `pytest -q code/test_general_dimension_scope_consistency.py code/test_living_scope_consistency.py code/test_compile_manuscript.py`: **18/18 PASS**;
- `ruff check code/test_general_dimension_scope_consistency.py`: **PASS**.

Passing the baseline suite is not treated as proof that the semantic mutation
space is closed.

## 3. Independent in-memory mutation protocol

The eight living surfaces read by the guard were loaded once.  For each case,
one in-memory copy was modified, `_read(relative)` was redirected to that copy,
and all four tests in `test_general_dimension_scope_consistency.py` were called.
A mutation was classified **CAUGHT** if any test raised and **MISSED** only if
all four returned normally.  No mutated source or temporary source file was
written to disk.

The 15-case result was **7 CAUGHT / 8 MISSED**:

| # | Mutation | Class | Result |
| ---: | --- | --- | --- |
| 1 | Direct note: `are not uniform or compared across dimensions` -> `are uniform and compared across dimensions` | exact Round 85 replay | **CAUGHT** |
| 2 | Mixed note: no common numerical-budget comparison -> dimensions compared at one common numerical budget | exact Round 85 replay | **CAUGHT** |
| 3 | Inject `Physical-$d=4$ positive-budget numerical evidence is complete.` | exact Round 85 replay | **CAUGHT** |
| 4 | Direct note: replace the protected negative clause by `may be chosen dimension-independently and compared from one dimension to another` | positive synonym rewrite | **CAUGHT** |
| 5 | Mixed note: replace the protected negative clause by `permits dimension-to-dimension comparison at one shared numerical budget` | positive synonym rewrite | **CAUGHT** |
| 6 | Swap `\forall\epsilon\in(0,\epsilon_0)` and `\exists B_0(d,m,\text{data},\Wset,\epsilon)>0` in the boxed Supplement statement | reversed quantifier/order | **CAUGHT** |
| 7 | Inject `Physical-\(d=4\) finite-budget numerical evidence is complete.` | nearby TeX dimension format | **CAUGHT** |
| 8 | Inject `For $d=4$, positive-$B$ numerics are verified.` | `for d=4` plus verified-numerics synonym | **MISSED** |
| 9 | Inject `In physical dimension $d=4$, finite-$B$ numerics are verified.` | `physical dimension d=4` plus finite-B synonym | **MISSED** |
| 10 | Inject `The physical case \(d=4\) has verified positive-\(B\) numerics.` | TeX `\(d=4\)` plus verified-numerics synonym | **MISSED** |
| 11 | Inject `Physical $d=4$ positive-budget numerical evidence is complete.` | no hyphen after `Physical` | **MISSED** |
| 12 | Inject `Physical-$d\ge4$ positive-budget numerical evidence is complete.` | range form `d\ge4` | **MISSED** |
| 13 | Inject `Physical-$d=4$ finite-$B$ numerics are verified.` | recognized dimension shell but synonymous promotion predicate | **MISSED** |
| 14 | Preserve every required negative sentence and inject `Equal numerical reaction budgets are directly comparable between physical dimensions.` | contradictory common-B positive assertion | **MISSED** |
| 15 | Preserve every required negative sentence and inject `The theorem's constants and threshold can be selected independently of physical dimension.` | contradictory dimension-uniform positive assertion | **MISSED** |

Thus the exact three Round 85 regressions are genuinely repaired, rather than
merely reported as repaired.  The reversed nested quantifier is also genuinely
protected.  The remaining failure is generality: the numerical guard recognizes
only a narrow lexical product of a `physical-` prefix, an equality to one
integer, and one of five promotion substrings.  It does not recognize `for
d=4`, `physical dimension d=4`, a standalone TeX `\(d=4\)`, `d\ge4`, or
`finite/positive B numerics are verified`.  Separately, presence-only negative
contracts do not reject a contradictory positive sentence when the original
negative sentence remains elsewhere in the source.

These are not remote paraphrases.  They are adjacent editorial forms of the
same forbidden claims and can plausibly enter the abstract, theorem discussion,
caption, README, or notes during revision.  At least one such bypass is enough
to keep the scope guard on HOLD; eight were demonstrated.

## 4. Frozen scientific bytes

The exact Round 84/Round 85 scientific objects and canonical artifact remain
unchanged:

| File | SHA-256 |
| --- | --- |
| `manuscript/encounter_multimodal_prr.tex` | `1c17be4ac1223fa769166cc13c4b551a1cf7925ae59a61a81021657421305c5b` |
| `manuscript/encounter_multimodal_prr_supplement.tex` | `4a5b3073d346fd50528d8c5a8fd51b914d94730c8d5b82def641627bfd168f07` |
| `notes/direct_physical_multimode_theorem.md` | `2b35d1b1053045220b29975d30f8b3c842d33273ca46de86b8cf7798c26a9c3d` |
| `notes/pde_mixed_jet_theorem.md` | `ac0e6cbb34d446d2b9ae2b52c22684ee72da7cadb04d864aacba085dff75f095` |
| `artifacts/data/manuscript_compile.json` | `795f8c2bdaced87414c4d87adbaf2a2ea813fb07dbee710669e9b42035b3f493` |
| `manuscript/encounter_multimodal_prr.pdf` | `fa4debf25af63f3c1d58cbc68b44d08b4c6add223e92207c18f7264bbf0774c6` |

No evidence was found that the current manuscript or theorem notes themselves
make a physical positive-budget numerical claim above $d=3$, compare a
common dimensional $B$ across dimensions, or assert dimension-uniform
constants.  Their analytical fixed-finite-$d$ scope remains acceptable.

## 5. Required closure boundary

The next repair, if authorized, must remain test-only and must close both
demonstrated bypass families:

1. normalize and reject nearby $d>3$ dimension formats and promotion
   predicates, including `for d=4`, `dimension d=4`, TeX `\(d=4\)`, range
   forms, and `finite/positive B numerics verified`; and
2. reject contradictory positive cross-dimensional comparability or uniformity
   assertions even when the canonical negative sentence is still present.

That repair requires a fresh independent mutation recheck.  Until then the
general-dimension scientific wording may remain frozen, but the mutation guard
does not support an **ACCEPT** decision.  This test-level HOLD also does not
alter the separate project-level HOLD for allocation-cusp continuation,
independent solver evidence, or positive-budget physical-$d=3$ validation.
