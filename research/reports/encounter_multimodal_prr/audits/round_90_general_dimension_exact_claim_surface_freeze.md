# Round 90: exact-byte general-dimension claim-surface freeze

Date: 2026-07-14  
Predecessor: `audits/round_89_general_dimension_independent_semantic_attack.md`  
Status: **SELF-REPAIR-FROZEN; INDEPENDENT RECHECK REQUIRED**

## 1. Why the guard architecture changed

Round 89 independently replayed the Round 87 corpus at 15/15 CAUGHT, but an
unseen 50-case extension yielded 10 CAUGHT / 40 MISSED and three false
positives.  Unicode relations, written-out dimensions, cross-sentence and
table composition, decimal points, abbreviations, predicate synonyms, and
negation scope show that adding more natural-language regular expressions is
not a defensible release boundary.

Round 90 therefore removes the semantic regex classifier.  The release gate is
now exact change control: every claim-bearing source byte already reviewed in
Rounds 77--89 is SHA-256 frozen.  Any change, whether scientific or harmless,
must first HOLD and then receive an explicit rebaseline plus independent
scientific review.  This intentional conservatism has no semantic
false-positive/false-negative distinction: unreviewed prose is simply outside
the accepted byte surface.

## 2. Frozen claim surface

The guard expands the eight living theory/editorial surfaces by the two TeX
inputs actually included by the main manuscript:

| Surface | SHA-256 |
| --- | --- |
| `manuscript/encounter_multimodal_prr.tex` | `1c17be4ac1223fa769166cc13c4b551a1cf7925ae59a61a81021657421305c5b` |
| `manuscript/encounter_multimodal_prr_supplement.tex` | `4a5b3073d346fd50528d8c5a8fd51b914d94730c8d5b82def641627bfd168f07` |
| `notes/direct_physical_multimode_theorem.md` | `2b35d1b1053045220b29975d30f8b3c842d33273ca46de86b8cf7798c26a9c3d` |
| `notes/pde_mixed_jet_theorem.md` | `ac0e6cbb34d446d2b9ae2b52c22684ee72da7cadb04d864aacba085dff75f095` |
| `README.md` | `024c5d45da89b2e630fe8cbbeb7acf895f7710035da5b9d7152270b940ca07c3` |
| `notes/research_contract.md` | `fd0340efd28e97142565840c0f32b362f233ae44bf39b500a508ac62f4f9be77` |
| `notes/theorem_program.md` | `ce23ecf940e5864facafea563588aecbd75555b23a16a0b4bf6178a2138e422e` |
| `notes/prr_focused_spine_rewrite_blueprint.md` | `585ea39754c133afd99c13e552c0ee5bbae2ebb0fc2a5809f15bef4d0ab02009` |
| `manuscript/inputs/numerical_results.tex` | `62fe4306fc1bfa6a75757031ba23de38f9fabe490ac7be8c0b05e14c543a1530` |
| `manuscript/inputs/positive_b_results.tex` | `2eb08d12a5585afa17b8bedfb3d79232a25e328a30439cb0cb0678b13631fabf` |

`_read` now uses `read_bytes().decode("utf-8")`, rather than universal-newline
text I/O, so CR/LF-only byte drift is not normalized away.  The same source
strings remain available to an independent in-memory monkeypatch attack.

## 3. Test contract

The exact source set and the exact digest map must agree.  Every source is
hashed from its UTF-8 bytes.  The living test mutates each of the ten surfaces
in turn with an ASCII space, a zero-width Unicode character, and a carriage
return; all 30 changes are required to fail.  The earlier structural checks
remain as useful diagnostics for:

- the embedded minimum-image `d`-ball and contact-interior margin;
- the dimensional unit `[B]=L^dT^{-1}`;
- epsilon-before-budget quantifier order;
- pointwise rather than uniform fixed-finite-`d` scope; and
- explicit no-common-budget and no-`d -> infinity` boundaries.

Those diagnostics are no longer claimed to classify arbitrary English.

## 4. Verification and frozen bytes

Only `code/test_general_dimension_scope_consistency.py` changed.  No theorem,
manuscript, generated input, numerical source/result, compile manifest, or PDF
was edited; no producer or compiler was run.

Focused verification:

- `pytest -q code/test_general_dimension_scope_consistency.py code/test_living_scope_consistency.py code/test_compile_manuscript.py`: **19/19 PASS**;
- `uv run ruff check code/test_general_dimension_scope_consistency.py`: **PASS**.

| Repaired object | SHA-256 |
| --- | --- |
| `code/test_general_dimension_scope_consistency.py` | `965d0fc91e7a2ab14c9ab0eca2d28c6ce3f3043b2d74d18eab3c1c05c7cecdcf` |
| Round 89 report consumed | `aaa7b2d400132146afd2ba0ecef7c382c90a1fddc09d55bc206b6cba8a6cdfd3` |
| `artifacts/data/manuscript_compile.json` | `795f8c2bdaced87414c4d87adbaf2a2ea813fb07dbee710669e9b42035b3f493` |
| `manuscript/encounter_multimodal_prr.pdf` | `fa4debf25af63f3c1d58cbc68b44d08b4c6add223e92207c18f7264bbf0774c6` |

## 5. Decision boundary

This is a self-repair freeze, not an ACCEPT.  A fresh independent attack must
verify the exact test hash, replay all 65 earlier semantic mutations, mutate
each of the ten surfaces including the two generated inputs, exercise Unicode
and CR/LF byte changes, and verify that safe baseline bytes still pass.  It
must also confirm that a future legitimate edit can proceed only by an
explicit digest rebaseline and new review, rather than by a hidden normalizer.
Until that audit returns P0/P1/P2 = 0/0/0, the general-dimension gate remains
on HOLD.
