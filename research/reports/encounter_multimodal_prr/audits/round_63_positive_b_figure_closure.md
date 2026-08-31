# Round 63: positive-budget fixed-control figure closure

Date: 2026-07-14  
Role: independent downstream figure construction, mutation testing, and rendered-PDF QA  
Verdict: **PASS-FIGURE-CLOSURE / HOLD-PRR-PROJECT**

## 1. Scope and non-execution boundary

This round added one bounded reader-facing figure for the already admitted
positive-`B` fixed-control result. The renderer reads only:

1. `artifacts/data/positive_b_broad_four_slab_result.json`;
2. `artifacts/data/positive_b_broad_four_slab_reproducibility.json`; and
3. `artifacts/data/positive_b_broad_four_slab_independent_audit.json`.

It does not import or execute the numerical producer, canonical auditor,
semigroup, finite-volume solver, or any `vkcore` scientific module. It does not
read the manifest; instead, it requires all three canonical JSON files to cite
the externally frozen manifest SHA exactly. It performs no scientific
recomputation beyond algebraic consistency checks on saved scalars.

No canonical JSON, producer, auditor, manifest, pin, existing multi-family
builder, manuscript, or README was edited.

## 2. Chart contract

### Analytical question

Does the same result-informed fixed control retain three saved density modes
and three event basins above the frozen `0.005` reaction-mass floor on held-out
odd meshes `N=113` and `N=129`?

### Bounded takeaway

On the two held-out odd meshes in one fixed reflected box and the same solver
family, the saved traces retain five alternating stationary roots and all six
event-basin masses exceed `0.005` for the finite gate window ending at `t=100`.

This is a fixed-box, same-solver, two-mesh point result. It is not continuum,
box/parity convergence, independent-solver, physical-`d=3`, allocation-cusp,
or publication-gate evidence.

### Visual design

- **Panel (a):** `N=113` and `N=129` saved encounter-density traces, with
  solid versus dashed lines as a non-colour mesh distinction; filled circles
  mark local maxima and open diamonds mark local minima.
- **Panel (b):** grouped event-basin reaction-mass bars on an explicitly
  labelled logarithmic axis; colour plus hatch distinguishes the two meshes;
  a neutral dashed line marks the frozen `0.005` floor.
- Palette: one blue and one gold root plus neutral ink/grey only.
- Surface: deterministic, single-page, white-background vector PDF.
- Scope text printed in the figure: fixed reflected box, `B=0.01`, unchanged
  result-informed control, two held-out odd finite-volume meshes, same solver
  family, and finite `t<=100` gate window.
- Panel (a) explicitly says that the plotted saved trace stops at `t=35`; the
  event qualification and tail gate extend to `t=100`.

## 3. Hard source pins and claim preflight

The new renderer hard-pins the three public inputs:

| Input | Required and observed SHA-256 |
|---|---|
| canonical result | `51e8eb4bdb652124865d0c39e6f36b99d13ed61578b161e0f75b142cada49401` |
| two-process evidence | `6c0eccaae09ef95923843ddd7a141a27311e1575ee68d3301b4757b785ee9890` |
| independent audit | `60c541a6f0decd5431cefa5c203311176e61006586ce69043d5fcf5380ed517d` |

Every input is opened as a regular nonsymlink file, hashed before parsing, and
decoded as strict UTF-8 JSON with duplicate keys and named nonfinite constants
rejected. Every plotted or claim-bearing numeric value is then required to be
finite. Before any Matplotlib figure exists, the preflight verifies:

- all three declared manifest SHAs equal
  `955e59bf333b5fd70e415a53dc26becae9c7a34c5d40f1230c96b1dab8f5677c`;
- result, evidence, and audit statuses retain their bounded PASS values;
- result/evidence/audit and replica SHA chains are exact;
- the recorded two-process evidence remains sequential, byte-identical,
  exit-zero, and promoted only after comparison;
- the audit still says it did not independently witness subprocess execution;
- all five canonical negative claim flags remain false, the two forbidden
  promotion keys remain absent, and the audit claim boundary remains exact;
- `weights_refit=false`, `B=0.01`, and the four fixed weights are unchanged;
- the result has exactly cubic meshes `[113,113,113]` and `[129,129,129]`;
- each mesh has 351 finite nonnegative saved-trace densities from `t=0` to
  `t=35` with strictly increasing times;
- each mesh has exactly five strictly ordered roots with
  `maximum--minimum--maximum--minimum--maximum` topology and compatible
  curvature signs;
- each mesh has exactly three finite event-basin masses at final time `100`,
  every mass is at least `0.005`, and the masses reconstruct from the two saved
  valley survivals and final survival; and
- the audit root times and basin masses exactly equal the canonical result.

The three source hashes are checked again after in-memory rendering and before
atomic publication, closing the ordinary read-to-publish drift window.

## 4. Implementation and mutation hardening

### Added source

`code/plot_positive_b_broad_four_slab.py`  
SHA-256: `5e03cf4c78ad47b61f7d4c3a7480ee5c725be0fde013ade98c0934a3cec3a90e`

The renderer builds the complete PDF in memory, verifies its PDF/vector safety,
rechecks all three source pins, and only then publishes by same-directory atomic
replace. Validation or rendering failure occurs before publication, so an
existing output remains untouched.

### Added test

`code/test_plot_positive_b_broad_four_slab.py`  
SHA-256: `8c9ea0f7daf49181542debf3a6cef4499c6e44427016e636a524229b176124b5`

The 12 tests cover:

1. exact two-mesh bounded preflight;
2. absence of producer, solver, auditor, subprocess, SciPy, or `vkcore` imports;
3. raw-byte hash mutation;
4. false negative-claim flag mutation;
5. five-root topology mutation;
6. event-mass-floor mutation;
7. evidence-to-result hash-chain mutation;
8. audit-to-evidence hash-chain mutation;
9. prior-output preservation after validation failure;
10. prior-output preservation after rendering failure;
11. two independent in-process renders with identical PDF bytes and zero
    vector-safety defects; and
12. exact equality of the committed PDF and a fresh render.

## 5. Output and deterministic-byte closure

Generated output:

`artifacts/figures/positive_b_broad_four_slab.pdf`  
SHA-256: `3904dbdddd50f7efc1bd66ed5b2274025b08c79bdd044a1efbdfb5a45156fe09`  
Size: `98,227` bytes  
Page: `518.4 x 298.8 pt` (`7.2 x 4.15 in`), one page, PDF 1.4

Two separate CLI builds to different output paths both produced exactly:

```text
3904dbdddd50f7efc1bd66ed5b2274025b08c79bdd044a1efbdfb5a45156fe09
98,227 bytes
```

`cmp` confirmed byte identity, and both temporary outputs matched the committed
PDF byte-for-byte.

## 6. Commands and validation results

```bash
.venv/bin/python -m py_compile \
  research/reports/encounter_multimodal_prr/code/plot_positive_b_broad_four_slab.py \
  research/reports/encounter_multimodal_prr/code/test_plot_positive_b_broad_four_slab.py

.venv/bin/python -m ruff check \
  research/reports/encounter_multimodal_prr/code/plot_positive_b_broad_four_slab.py \
  research/reports/encounter_multimodal_prr/code/test_plot_positive_b_broad_four_slab.py

.venv/bin/python -m pytest -q \
  research/reports/encounter_multimodal_prr/code/test_plot_positive_b_broad_four_slab.py

.venv/bin/python scripts/reportctl.py validate-science-rules
```

Results:

```text
py_compile: PASS
Ruff: All checks passed
pytest: 12 passed
validate-science-rules: PASS
```

PDF structural QA:

```text
Type 3 font tokens: 0
transparency graphics-state tokens: 0
raster image XObjects: 0
fonts: embedded CID TrueType, Unicode mapped
JavaScript: none
encryption: none
```

## 7. Rendered-page QA

The PDF was rendered at 180 dpi and inspected as a page image. The first visual
pass found three layout defects: an automatic scientific-notation offset
overlapped panel (a)'s subtitle, panel (b)'s subtitle clipped at the right edge,
and the first scope line at the bottom was too wide. The renderer was repaired
to use an explicit `x 10^-3` density unit, shorter panel-(b) wording, and a
shorter bottom line.

The repaired PDF was regenerated and visually inspected again. Final checks:

```text
title/subtitle hierarchy: PASS
panel title and subtitle clearance: PASS
axes and units: PASS
solid/dashed mesh distinction: PASS
filled/open root distinction: PASS
grouped bars and hatch distinction: PASS
log-scale disclosure: PASS
0.005 reference-line readability: PASS
value-label clearance: PASS
legend clearance: PASS
bottom claim-boundary text: PASS
clipping/overlap/broken glyphs: none observed
```

Poppler text extraction also retained `B=0.01`, `t<=35`, `t<=100`, `fixed
reflected box`, `same solver family`, the log-scale label, and the complete
negative-scope sentence.

## 8. Final decision

```text
Canonical source pins: PASS
Bounded claim preflight: PASS
No producer/solver/auditor execution: PASS
Mutation hardening: PASS (12/12)
Deterministic PDF bytes: PASS
Vector/font/PDF QA: PASS
Rendered layout QA: PASS AFTER REPAIR
Positive-B fixed-control figure: READY
Overall PRR project: HOLD
```

The figure is suitable for a later narrowly qualified manuscript insertion. It
does not itself authorize that insertion, alter the main claim matrix, or close
the remaining allocation-cusp, mesh/box/continuum, independent-solver, or
physical-`d=3` gates.
