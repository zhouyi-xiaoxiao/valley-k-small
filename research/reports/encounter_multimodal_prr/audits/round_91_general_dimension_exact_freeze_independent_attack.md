# Round 91: independent exact-byte claim-surface attack

Date: 2026-07-14  
Predecessor: `audits/round_90_general_dimension_exact_claim_surface_freeze.md`  
Status: **ACCEPT — EXACT-BYTE GENERAL-DIMENSION GATE**

## 1. Boundary and decision

This was a read-only independent attack on the Round 90 exact-byte
claim-surface freeze.  No existing file, test, scientific source, generated
input, numerical source/result, compile manifest, or canonical PDF was edited.
No producer or compiler was run.  All adversarial changes existed only in
memory.  The sole new file is this audit report.

The frozen test and Round 90 report matched their requested SHA-256 values.
All 65 prior semantic mutations, all 80 systematic per-surface byte mutations,
all 8 generated-input-specific mutations, and all 21 source-set/metadata
mutations failed closed.  The decision is:

| P0 | P1 | P2 | General-dimension gate |
| ---: | ---: | ---: | --- |
| 0 | 0 | 0 | **ACCEPT** |

This ACCEPT closes the independent exact-byte general-dimension scope gate.  It
does not change the separate project-level HOLD for allocation-cusp
continuation, independent-solver evidence, or positive-budget physical-`d=3`
validation.

## 2. Frozen root of trust

| Object | Required SHA-256 | Observed | Result |
| --- | --- | --- | --- |
| `code/test_general_dimension_scope_consistency.py` | `965d0fc91e7a2ab14c9ab0eca2d28c6ce3f3043b2d74d18eab3c1c05c7cecdcf` | same | **PASS** |
| `audits/round_90_general_dimension_exact_claim_surface_freeze.md` | `6f8fefe18602ae244db30a8d8ef10351961734d08bce5b9e4a34b781b80e11d4` | same | **PASS** |

The test's `CLAIM_SURFACE_PATHS` and
`CLAIM_SURFACE_SHA256` dictionaries were independently compared with a
separate hardcoded 10-entry map.  Labels, paths, digests, set cardinality, and
path uniqueness matched exactly.

The article contains exactly two `\input{...}` directives:
`inputs/numerical_results.tex` and
`inputs/positive_b_results.tex`.  The Supplement contains no additional
`\input` or `\include` directive, and `manuscript/inputs/`
contains exactly those two files.  Therefore no included generated TeX
claim surface is omitted from the 10-entry freeze.

## 3. Original-byte and `_read` audit

For each surface, the file was read independently with `Path.read_bytes()`,
decoded as UTF-8, compared byte-for-byte with the module's `_read` return
after re-encoding, hashed independently, and compared with the hardcoded
digest:

| Label | Path | Bytes | SHA-256 |
| --- | --- | ---: | --- |
| main | `manuscript/encounter_multimodal_prr.tex` | 58,610 | `1c17be4ac1223fa769166cc13c4b551a1cf7925ae59a61a81021657421305c5b` |
| supplement | `manuscript/encounter_multimodal_prr_supplement.tex` | 48,441 | `4a5b3073d346fd50528d8c5a8fd51b914d94730c8d5b82def641627bfd168f07` |
| direct note | `notes/direct_physical_multimode_theorem.md` | 21,388 | `2b35d1b1053045220b29975d30f8b3c842d33273ca46de86b8cf7798c26a9c3d` |
| mixed-jet note | `notes/pde_mixed_jet_theorem.md` | 33,284 | `ac0e6cbb34d446d2b9ae2b52c22684ee72da7cadb04d864aacba085dff75f095` |
| README | `README.md` | 21,872 | `024c5d45da89b2e630fe8cbbeb7acf895f7710035da5b9d7152270b940ca07c3` |
| contract | `notes/research_contract.md` | 7,234 | `fd0340efd28e97142565840c0f32b362f233ae44bf39b500a508ac62f4f9be77` |
| theorem program | `notes/theorem_program.md` | 38,786 | `ce23ecf940e5864facafea563588aecbd75555b23a16a0b4bf6178a2138e422e` |
| rewrite blueprint | `notes/prr_focused_spine_rewrite_blueprint.md` | 27,105 | `585ea39754c133afd99c13e552c0ee5bbae2ebb0fc2a5809f15bef4d0ab02009` |
| generated numerical input | `manuscript/inputs/numerical_results.tex` | 4,561 | `62fe4306fc1bfa6a75757031ba23de38f9fabe490ac7be8c0b05e14c543a1530` |
| generated positive-B input | `manuscript/inputs/positive_b_results.tex` | 2,286 | `2eb08d12a5585afa17b8bedfb3d79232a25e328a30439cb0cb0678b13631fabf` |

Code inspection found `read_bytes().decode("utf-8")`, not
`read_text` or universal-newline text I/O.  An independent in-memory
fake-path probe returned the exact payload
`A\r\nB\rC\né\u200b`, and re-encoding reproduced every original byte.
Thus CRLF, bare CR, LF, composed Unicode, and a zero-width Unicode character
were neither newline-normalized nor Unicode-normalized.

## 4. Prior semantic corpus replay: 65/65 CAUGHT

The exact in-memory mutation procedures from Rounds 87 and 89 were replayed
against the frozen Round 90 test.  For each case, `_read(relative)` was
redirected to a complete 10-surface in-memory map, and all five tests in
`test_general_dimension_scope_consistency.py` were eligible to run.  A
case counted as CAUGHT when any test raised and as MISSED only when all five
returned normally.

| Corpus | CAUGHT | MISSED | Total |
| --- | ---: | ---: | ---: |
| Round 87 exact corpus | 15 | 0 | 15 |
| Round 89 independent extension | 50 | 0 | 50 |
| **Combined** | **65** | **0** | **65** |

This includes Unicode `≥`, written-out dimensions, set/range forms,
multi-digit `d=10`, `d>2`/`d>=1`, decimal and abbreviation
punctuation, cross-sentence and cross-table claims, budget/evidence synonyms,
common/shared/equal budget assertions, negation-scope traps, and all tested
uniform-in-`d` constants/`B_0`/amplitudes/event-mass forms.  The
exact-byte gate catches them because they change a reviewed surface, not
because it claims to understand arbitrary prose.

## 5. Every-surface byte attack: 80/80 CAUGHT

Each of the ten surfaces was mutated independently in all eight ways below:

1. insert one ASCII byte;
2. replace one ASCII byte without changing length;
3. delete one character;
4. insert Unicode U+200B;
5. replace the first LF by CRLF;
6. replace the first LF by bare CR;
7. append a cross-sentence high-`d` promotion; and
8. append the same promotion split across Markdown table cells.

| Surface | CAUGHT | MISSED |
| --- | ---: | ---: |
| main | 8 | 0 |
| supplement | 8 | 0 |
| direct note | 8 | 0 |
| mixed-jet note | 8 | 0 |
| README | 8 | 0 |
| contract | 8 | 0 |
| theorem program | 8 | 0 |
| rewrite blueprint | 8 | 0 |
| generated numerical input | 8 | 0 |
| generated positive-B input | 8 | 0 |
| **Total** | **80** | **0** |

Consequently ASCII, Unicode, LF/CRLF/CR, deletion, replacement, cross-sentence,
and cross-table drift all fail closed on every surface.

## 6. Generated-input-specific attacks: 8/8 CAUGHT

The generic per-surface attacks were supplemented by value- and
provenance-aware mutations:

| Generated input | Targeted mutation | Result |
| --- | --- | --- |
| numerical | Change the last digit of `\FourPatchCuspTime` | **CAUGHT** |
| numerical | Change one digit of the source-manifest comment SHA | **CAUGHT** |
| numerical | Delete the `\FourPatchRootOne` macro | **CAUGHT** |
| numerical | Append a false physical-`d=4` evidence table row | **CAUGHT** |
| positive-`B` | Change `\PositiveBBudget` from `0.01` to `0.02` | **CAUGHT** |
| positive-`B` | Change `\PositiveBMeshOne` from `113` to `115` | **CAUGHT** |
| positive-`B` | Delete the generated forbidden-scope comment | **CAUGHT** |
| positive-`B` | Append a false `\PositiveBDimension` macro | **CAUGHT** |

Both generated inputs are therefore protected at the numerical value, macro,
scope-comment, provenance-comment, and arbitrary-added-content levels.

## 7. Source-set and metadata attacks: 21/21 CAUGHT

Three independent attack families were exercised:

| Family | Attacks | Result |
| --- | ---: | --- |
| Runtime source dictionary | 8 | **8/8 CAUGHT** |
| Label/path map | 7 | **7/7 CAUGHT** |
| Label/digest map | 6 | **6/6 CAUGHT** |
| **Total** | **21** | **21/21 CAUGHT** |

The cases covered deleting `main`, deleting either generated-input key,
adding an extra key, renaming a label, swapping main/Supplement content,
swapping generated-input content, duplicating a path, a missing path,
main/Supplement path or digest swaps, generated-input path or digest swaps, a
wrong digest, and explicit digest/path mismatch.  Missing files raised before
acceptance; every other attack failed set equality or digest equality.

A coordinated path/digest rebaseline is necessarily an edit to the frozen test
root of trust.  As a direct check, changing only the textual main path to an
equivalent `./manuscript/...` form changed the test SHA from the accepted
`965d0f...` value to
`88aff122509832ba2d2a1b4111fb3504e2f87a3cf7c533b16a1e0d052febe3ac`.
Such a rebaseline is not a hidden runtime bypass: it leaves the accepted test
byte and must undergo the explicit re-audit process.

## 8. Deliberate change-control semantics

A benign spelling correction, comment edit, whitespace change, newline
conversion, or regenerated numerical input is intentionally treated exactly
like a scientific claim edit: it places the project on HOLD until the ten
digests are explicitly rebaselined and independently reviewed.  This is
deliberate change control, not a false positive.  Semantic assertions remain
diagnostics only and are not used to claim classification of unseen natural
language.

## 9. Baseline tests and frozen scientific artifact

The requested focused checks passed on the exact frozen test byte:

- `pytest -q code/test_general_dimension_scope_consistency.py code/test_living_scope_consistency.py code/test_compile_manuscript.py`: **19/19 PASS**;
- `python -m ruff check code/test_general_dimension_scope_consistency.py`: **PASS**.

The authoritative science, compile manifest, and canonical PDF remain at their
previous exact hashes:

| Object | SHA-256 |
| --- | --- |
| `manuscript/encounter_multimodal_prr.tex` | `1c17be4ac1223fa769166cc13c4b551a1cf7925ae59a61a81021657421305c5b` |
| `manuscript/encounter_multimodal_prr_supplement.tex` | `4a5b3073d346fd50528d8c5a8fd51b914d94730c8d5b82def641627bfd168f07` |
| `notes/direct_physical_multimode_theorem.md` | `2b35d1b1053045220b29975d30f8b3c842d33273ca46de86b8cf7798c26a9c3d` |
| `notes/pde_mixed_jet_theorem.md` | `ac0e6cbb34d446d2b9ae2b52c22684ee72da7cadb04d864aacba085dff75f095` |
| `artifacts/data/manuscript_compile.json` | `795f8c2bdaced87414c4d87adbaf2a2ea813fb07dbee710669e9b42035b3f493` |
| `manuscript/encounter_multimodal_prr.pdf` | `fa4debf25af63f3c1d58cbc68b44d08b4c6add223e92207c18f7264bbf0774c6` |

No mutation escaped, no claim surface was omitted, and no normal source change
passed without a digest failure.  The final Round 91 decision is therefore
**P0/P1/P2 = 0/0/0; ACCEPT the exact-byte general-dimension claim-surface
gate**.
