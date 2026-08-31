# Weak-budget figure contract and caption

## Scope

The figure asks whether the **frozen current geometry** reproduces a
result-informed cusp of the (B=0) free-exposure diagnostic, its local
max--min--max unfolding, and a sampled two-mode region on the complete 0.01
catalyst-weight simplex.  It does not test positive finite (B), mesh
convergence, the continuum limit, trimodality, or the project-level claim.

The one-sentence supported takeaway is: the discrete diagnostic reproduces the
cusp and its local two-mode unfolding; 455 of 5151 sampled controls are
bimodal, while no sampled control is trimodal in the current geometry.

## Caption

**Weak-budget/free-exposure design diagnostic for the frozen current
geometry.** (a) The three (B=0) free-exposure clocks and their reproduced cusp
mixture on one 207,025-state finite-volume quotient. (b) The cusp derivative
and the frozen inward perturbation, whose three stationary roots have
max--min--max topology. (c) The complete 0.01 catalyst-weight simplex screen:
4696 controls have one sampled mode and 455 have two. This result-informed
finite-grid diagnostic is neither a finite-(B) or continuum verification nor
a trimodality claim.

## Frozen provenance

- Result:
  `artifacts/data/continuum_weak_budget_design_result.json`, SHA-256
  `dcbfb9c9ccee4378a8ceeebe00be01de0bf5c5db7914b83032333e066439369f`.
- Manifest:
  `artifacts/data/continuum_weak_budget_design_manifest.json`, SHA-256
  `b912aa5d9d6cd21601bab8ec847670b28934a20887319872571ed014622d5949`.
- Numerical producer: `code/continuum_weak_budget_design.py`, SHA-256
  `7fa9ea6114328736c89739459c293aefa9311514764ec3cfe4f0ceb5a1875201`.
- Plot producer: `code/plot_weak_budget_design.py`, SHA-256
  `3be729f1f7e045cf1cba40654e5edd7625641cdda2738b615c824960f74de5c5`.
- Plot tests: `code/test_plot_weak_budget_design.py`, SHA-256
  `063bfe61566c8b7854d9901886997210de58e7c4bbca6731c19bead04e049579`.

The plot producer checks all three input hashes before calculation, rebuilds
the 8001-point channel curves, verifies their frozen digest, reproduces the
cusp and inward roots, and recounts all 5151 simplex controls. It rejects any
change that turns `continuum_verified`, `project_gate_passed`, or
`finite_B_Doi_cusp_verified` true. The unfrozen redesigned geometry is excluded.

## Outputs and QA

- Vector figure: `artifacts/figures/weak_budget_design.pdf`, SHA-256
  `29f12a5debce35339c74b7d6260455f4fc1cce118751296e572cbaa9c17bca7e`.
- PNG preview: `artifacts/figures/weak_budget_design.png`, SHA-256
  `312fcb38273395bc26bc5450804946811ff5f0361b92c3c769f9a484483028d7`.
- Machine-readable caption and provenance:
  `artifacts/figures/weak_budget_design_metadata.json`, SHA-256
  `8087713835364aa5340410082737773946fc3f0641fc0bfa70b175853d0dea43`.

Reproduction command, from the repository root:

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python \
  research/reports/encounter_multimodal_prr/code/plot_weak_budget_design.py
```

The final run passed Ruff, eight focused weak-budget/figure tests, and two
independent render runs produced byte-identical PDF, PNG, and metadata hashes.
`pdffonts` reports only embedded/subset CID TrueType DejaVu Sans fonts and no
Type 3 font. `pdfimages -list` reports no raster image. The producer's strict
PDF scan reports zero Type 3, transparency-graphics-state, and raster-image
tokens. A Poppler render and the PNG were visually inspected after the layout
was revised to remove initial title clipping and simplex-label collisions.
