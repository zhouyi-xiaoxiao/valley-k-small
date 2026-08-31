# Round 71: positive-budget main-integration closure

Date: 2026-07-14  
Role: independent build-contract re-attack, frozen-source consistency audit, and
canonical-PDF closure review  
Verdict: **ACCEPT-MAIN-INTEGRATION / HOLD-PRR-SCIENTIFIC-PROMOTION**

## 1. Scope and non-execution boundary

This round closes the integration defects reported by Round 68. It inspected
and adversarially tested:

- `code/build_positive_b_manuscript_input.py` and its test suite;
- `code/build_manuscript_inputs.py` and its test suite;
- `code/compile_manuscript.py` and its test suite;
- the positive-`B` result, evidence, independent-audit, manifest, all 14
  manifest pins, figure, and figure metadata;
- the four manuscript figure contracts and their source-role pins;
- `manuscript/encounter_multimodal_prr.tex`, both generated TeX inputs,
  `manuscript/references.bib`, and the compile manifest; and
- the final canonical 13-page PDF, including rendered pages 1 and 7--11.

This round did **not** run or import the positive-`B` scientific producer,
execute a semigroup or finite-volume solve, invoke the canonical scientific
auditor, rerun an allocation search, or change any scientific result. Mutation
attacks used isolated temporary copies. The only repository write made by this
round is this audit report.

## 2. Decision and severity count

The Round-68 integration findings are closed. The builders and compiler now
bind verification, parsing, rendering, and staging to immutable verified byte
snapshots; their claim contracts fail closed under the tested schema,
promotion, repinning, symlink, nonfinite-value, and concurrent-replacement
attacks. The canonical PDF and compile manifest are mutually consistent and
the reader-facing time boundaries are explicit.

Final open finding count:

```text
P0 = 0
P1 = 0
P2 = 0
```

The acceptance is deliberately narrow:

```text
ACCEPT-MAIN-INTEGRATION
ACCEPT-CURRENT-FROZEN-FIXED-POINT-PIPELINE
HOLD-PRR-SCIENTIFIC-PROMOTION
HOLD-SUBMISSION / HOLD-RELEASE
```

It is **not** an acceptance of an allocation cusp, both folds, an
interval-global or post-`35` root census, parity/alignment/box convergence, an
unbounded-domain or continuum limit, an independent killed-process method, or
positive-budget physical `d=3`.

## 3. Exact frozen state

### 3.1 Build sources and tests

| Artifact | SHA-256 | Status |
|---|---|---|
| numerical input builder | `4643cee4831dd08595b30739cc60bb4849f70f25fda1870ff1962b7c9f384ed5` | CURRENT |
| numerical builder tests | `9dac0195cdc7aefcba780b7f7a4b7eafc06e28a4e67186113242fd3b5050b8cc` | 19/19 PASS |
| positive-`B` input builder | `fbea10829a4dd9aa2ed797788fab6ad7a0ef57c27d523d6d436caa6a6426fdb7` | CURRENT |
| positive-`B` builder tests | `04b4d22e022de7863b4e02b7b7a6e7a813e87bab5f682c9472d751dcb162bf7b` | 43/43 PASS |
| manuscript compiler | `675b7ff8aa367924ff1d9c32870977bf2d657d5f54a6b5449afda8d993cc0737` | CURRENT |
| compiler tests | `6a09d25f8087494b8b07caa7b14711729153582b8e0322fe49428ad3385f8dc9` | 12/12 PASS |

### 3.2 Manuscript transaction

| Artifact | SHA-256 | Status |
|---|---|---|
| main TeX | `07b40f2e4366e453684219f16a293e6afb561cd323d863f12a39db57dbc46ec1` | MATCH COMPILE MANIFEST |
| bibliography | `f9564d51d9453e215ff3dc92744f325a7b3329603d99cfe06437963bd61b4fde` | MATCH COMPILE MANIFEST |
| numerical TeX input | `62fe4306fc1bfa6a75757031ba23de38f9fabe490ac7be8c0b05e14c543a1530` | MATCH COMPILE MANIFEST |
| positive-`B` TeX input | `2eb08d12a5585afa17b8bedfb3d79232a25e328a30439cb0cb0678b13631fabf` | MATCH COMPILE MANIFEST |
| compile manifest | `9465cd290afac4ba65c007106a9d89cbcb2124d0b084d0d6db1d0e9d0def512e` | CURRENT |
| canonical PDF | `33dda9271133bbff2e5ecedb85e72b690c0dce7ddb779f8268c3c5e9f82fb96d` | MATCH COMPILE MANIFEST |

The compile manifest records `status=PASS`, `release_eligible=false`, and two
byte-identical clean builds with the exact PDF pair

```text
33dda9271133bbff2e5ecedb85e72b690c0dce7ddb779f8268c3c5e9f82fb96d
33dda9271133bbff2e5ecedb85e72b690c0dce7ddb779f8268c3c5e9f82fb96d
```

Its release blocker remains: scientific continuum gates and author-confirmed
submission metadata are open.

### 3.3 Positive-`B` frozen evidence chain

| Artifact | SHA-256 | Status |
|---|---|---|
| frozen manifest | `955e59bf333b5fd70e415a53dc26becae9c7a34c5d40f1230c96b1dab8f5677c` | MATCH |
| canonical result | `51e8eb4bdb652124865d0c39e6f36b99d13ed61578b161e0f75b142cada49401` | MATCH |
| two-process evidence | `6c0eccaae09ef95923843ddd7a141a27311e1575ee68d3301b4757b785ee9890` | MATCH |
| independent audit | `60c541a6f0decd5431cefa5c203311176e61006586ce69043d5fcf5380ed517d` | MATCH |
| canonical auditor source | `8e84d8930393e4ba60a906519eef7f1734c713a273791153a55d1f6f16ec3985` | MATCH |
| positive-`B` figure | `a55531cb9bd0f21f4bd0ee7ff0e6ddc6cdfe9bf73aa632542d7ba345bbb2e871` | MATCH SIDECAR |
| positive-`B` metadata | `0ad8214b6ae80c420321a24a5188f3e62cb3accebc520c8ac0be1153231a3821` | CURRENT |

All 14 manifest pins are distinct ordinary nonsymlink files, are current, and
match their recorded hashes. A separate live-source consistency pass checked
80/80 expected equalities across the builders, compiler, TeX, bibliography,
generated inputs, PDF, 38 numerical source pins, four figure PDFs and
metadata/source pin sets, and the four positive-`B` core artifacts. No mismatch
was found.

## 4. Round-68 closure matrix

| Round-68 finding | Repair now present | Independent re-attack | Closure |
|---|---|---|---|
| P1-1: positive builder did not reconstruct every frozen gate | exact manifest/result/evidence/audit contracts; 24 per-mesh and five agreement gates reconstructed; weights, physical parameters, timing, topology, ratios, masses, survival, and negative flags cross-checked | all five original repin attacks rejected; 24/24 saved mesh-gate flips and 5/5 agreement-gate flips rejected | CLOSED |
| P1-2: builder hash-then-load TOCTOU | one-descriptor, nonsymlink, regular-file snapshots; hash and strict JSON parse use the same payload; macros render from verified snapshots | live-path replacement cannot change rendered values; a forged snapshot with an original hash and attacker payload is rejected | CLOSED |
| P1-3: compiler could attest one figure and stage another | strict sidecar schemas; exact claim scopes/flags/source-role cardinalities; immutable figure, TeX, and BIB snapshots staged from verified bytes | duplicate key, symlink pin, promoted flags/scope, nested flag, duplicate role, and verify/copy/restore swaps rejected | CLOSED |
| P2-1: root and mass windows could be read as one interval | fixed wording distinguishes saved roots through `35`, mass/tail checks through `100`, and absence of post-`35` exclusion | main text, caption, gate ledger, sidecar, and visible figure text agree | CLOSED |

## 5. Positive-`B` builder semantic closure

The current builder no longer trusts aggregate PASS Booleans. It reconstructs
the claim-bearing quantities from the frozen scalar records and requires the
exact gate sets:

```text
24 / 24 per-mesh saved gates reconstructed and required
 5 /  5 cross-mesh agreement gates reconstructed and required
```

The five concrete Round-68 attacks are now rejected:

1. peak ratios below the frozen floor;
2. inconsistent root residual or curvature/topology;
3. a changed event-mass final time;
4. result weights inconsistent with the frozen control; and
5. a paired-root difference beyond its ceiling with a false agreement gate.

The re-attack also closed contradictions in the saved density trace and tail
records, including negative densities, invalid boundary/survival values,
survival increases, missing root sign brackets, roots outside saved time
brackets, negative tangent norms, invalid mass residuals, and a broken
scan/tail junction.

Strict type and claim validation rejects, among other cases:

- integer aliases for Boolean fields;
- noninteger mesh/process counts;
- promoted publication, continuum, cusp, independent-solver, or physical-`d=3`
  claims;
- missing or nonfinite software/evidence/audit fields;
- inconsistent independent-audit extrema and gate reconstructions; and
- extra or omitted result, evidence, reproducibility, or audit keys.

### 5.1 Fixed-geometry and finite-volume re-attack

Nineteen targeted fixed-geometry/finite-volume mutations were applied to
isolated snapshots. Twelve claim-bearing/invariant mutations were rejected,
including changed mesh identities, zero base or augmented trace, inconsistent
contact area, excessive generator-row error, invalid initial mass,
inconsistent spacing, nonunit rebalanced patch integrals, and inconsistent
root time-jet values.

Seven deliberately non-gating diagnostic fields remained accepted: three
producer-reported error estimates, maximum killing, two saved trace high-order
derivatives, and the reported budget derivative. These values are not used by
any of the 24 per-mesh or five agreement gates and cannot promote a manuscript
claim. Their acceptance is therefore a bounded schema decision, not an open
P1/P2 defect.

The exact finite-volume invariants used by the builder remain source-backed:
grid spacing and mesh size follow the frozen grid construction; contact area
uses the exact disk expression; generator/normalization diagnostics retain
their frozen tolerance; and the augmented trace retains the declared
two-channel relation to the base trace.

## 6. Numerical-input builder closure and newly found race

During this closure audit, the general numerical-input builder was found to
have a related P1 hash-then-load race that Round 68 had not enumerated. In the
isolated reproducer, a `d2` cusp time was changed to `99.123456789` after hash
verification, then restored before the later provenance check. The old builder
retained the original pre/post hash while rendering the attacker value.

This transient finding was repaired and re-attacked before this report. The
current builder now:

- opens ordinary nonsymlink sources as descriptor-backed snapshots;
- rejects duplicate JSON keys and nonfinite values;
- requires the exact release, family-role, result-schema, stage, status,
  timing, scope, limitation, and claim-flag contracts;
- uses strict Boolean types and recursively scans nested claim-bearing data;
- reparses the immutable `FileSnapshot` payload before rendering;
- requires payload hash, snapshot hash, and manifest pin to agree; and
- reruns the relevant family contract on the snapshot used for macro output.

The repaired builder rejects duplicate manifest/result keys, `NaN`, static
symlinks, `0`/`1` Boolean aliases, promoted broad-family scope or limitations,
and a full dependency-chain nested G1c continuum promotion. A live-path swap
now renders the originally verified value (`13.3280319895` in the regression),
while a forged snapshot pairing an original hash with attacker bytes is
rejected.

Because the race was both discovered and closed inside this round, it does not
remain in the final severity count.

## 7. Compiler and transaction closure

The compiler now requires:

- strict duplicate-key/nonfinite rejection for figure metadata;
- ordinary nonsymlink files for figures, metadata, and source pins;
- the exact metadata hash and contract for all four figures;
- exact evidence timing, claim scope, scope constraints, and negative flags;
- exact nested positive-`B` `d=2`/`d=3` claim flags and source-role
  cardinalities; and
- staging of figures, TeX, and bibliography directly from the attested byte
  snapshots.

The explicit compiler regressions reject:

```text
duplicate metadata key
symlink source pin
positive publication or continuum flag
promoted positive-B figure scope
nested d=3 positive claim flag
duplicate flat plus nested source role
verify/copy/restore figure swap
```

Additional attacks reject `NaN` metadata. Deterministic TeX and bibliography
replacement after snapshot acquisition stages the original verified bytes and
hashes, not the replacement bytes. Thus preflight, compilation inputs,
postflight, and the manifest are bound to one transaction snapshot.

The final transaction publishes six outputs only after all checks pass:

```text
manuscript/inputs/numerical_results.tex
manuscript/inputs/positive_b_results.tex
manuscript/encounter_multimodal_prr.pdf
artifacts/logs/manuscript_tex.log
artifacts/logs/manuscript_latexmk.log
artifacts/data/manuscript_compile.json
```

The compile manifest remains the last commit marker, with same-directory
atomic replacement and rollback recorded for all canonical outputs.

## 8. Test and static-analysis closure

The final scoped test suite passed:

```text
code/test_build_manuscript_inputs.py                 19 passed
code/test_build_positive_b_manuscript_input.py       43 passed
code/test_compile_manuscript.py                      12 passed
code/test_plot_positive_b_broad_four_slab.py         21 passed
code/test_living_scope_consistency.py                 2 passed
                                                    ---------
                                                     97 passed
```

Ruff passed on the three builders/compilers, the positive-`B` plotter, their
four principal test modules, and the living-scope consistency test. No test or
static-analysis failure remains in this integration scope.

## 9. Reader-facing claim boundary

The final manuscript consistently supports only the following positive-`B`
statement:

```text
B = 0.01
one unchanged result-informed broad four-slab allocation
one fixed reflected box
one finite-volume solver family
held-out odd meshes N = 113 and N = 129
five alternating retained roots on the saved root screen t <= 35
valley-partitioned basin masses and tail checks through t = 100
all six basin masses >= 0.005
at least three event-mass-qualified modes in this finite-window sense
```

The time distinction appears in the abstract, the fixed-positive-budget
subsection, Figure 3's visible text and caption, the gate ledger, the
discussion, and the figure metadata. Each says, in substance:

```text
five retained roots on the saved screen t <= 35;
valley-partitioned basin-mass and tail checks through t = 100;
no interval-global or post-35 root exclusion.
```

No reader-facing location was found that converts the saved five roots into a
global root census through `100`, claims exactly three global modes, or
promotes the fixed point to a cusp or continuum result.

## 10. PDF, log, and visual closure

The final PDF has:

```text
SHA-256:             33dda9271133bbff2e5ecedb85e72b690c0dce7ddb779f8268c3c5e9f82fb96d
pages:               13
bytes:               795828
font rows:           45
Type 3 fonts:        0
unembedded fonts:    0
missing files:       0
overfull boxes:      0
undefined citations: 0 in final TeX log
undefined references:0 in final TeX log
```

`artifacts/logs/manuscript_tex.log` is the final-pass log and has zero
undefined references, zero undefined citations, zero overfull boxes, and zero
missing files. `artifacts/logs/manuscript_latexmk.log` retains normal early-pass
convergence history (four undefined-reference and 56 undefined-citation
messages in intermediate passes); those historical messages are not defects
in the final TeX log or canonical PDF.

Rendered inspection found:

- page 1: clear abstract, with the `35`/`100` distinction explicit;
- pages 7--8: legible positive-`B` subsection and retained-root limitations;
- page 9: clear Figure 3, including the root, mass, and no-post-`35` notes;
- page 10: intact continuation and layout; and
- page 11: complete gate ledger and explicit project hold.

No clipped text, figure/text overlap, broken glyph, black box, or incorrect
reading order was observed. The final clean rebuild retained the exact PDF hash
that was visually inspected, so the visual result transfers byte-for-byte to
the canonical artifact.

## 11. Scientific gates that remain open

Integration closure does not close the scientific PRR program. Promotion and
submission remain on hold until the manuscript has affirmative evidence for:

1. a finite-`B` allocation cusp and both folds in the same broad family;
2. persistence of the cusp/fold jets and representative event-law features
   under parity, alignment, and box continuation;
3. an independent killed-process calculation preserving the positive-budget
   event-law features within quantified uncertainty;
4. positive-budget physical `d=3` evidence if a joint two-/three-dimensional
   headline is retained; and
5. author-confirmed submission metadata, disclosures, and archival details.

The correct final interpretation is therefore:

```text
The repaired main-manuscript integration is reproducible and fail-closed for
the current frozen fixed-control evidence. It is ready to serve as the stable
base for the next scientific campaign. It is not yet a PRR-promotable or
submission-ready scientific result.
```

