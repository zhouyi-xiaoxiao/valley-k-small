# Round 08 data, figures, notebook, manifests, workflow, and PDF audit — Reviewer A

Date: 2026-07-11  
Reviewer: A (independent reproducibility, provenance, notebook, and PDF audit)  
Verdict: **no scientific B0 or B1 was found, but the package is not release-ready: two B0 mechanical/submission gates, one B1 provenance-freshness defect, and two B2 generated-output/audit-inventory gates remain open; the numerical notebook and the source-level remediations otherwise pass this round**

## Scope and independence

I audited the live publication package rather than trusting prior pass summaries.
The scope comprised:

- all 13 child manifests, the legacy `artifacts/manifest.json`, the aggregate
  manifest, and the intended full/verify profile proofs;
- child/legacy output ownership, every listed SHA-256, model/classifier content
  hashes, generator lineage, and direct local Python dependencies;
- the full/verify stage plans, partial-failure behavior, immutable stage-log
  pinning, runtime locks, Lean-cache serialization, and legacy refresh order;
- the executed reader notebook, including all cells, saved outputs, narrative
  numbers, claim ledger, and source-notebook reconstruction hash;
- the 21-page manuscript PDF and all 12 figure PDFs, including visual rendering,
  captions/callouts, bibliography resolution, clipping, embedded fonts, raster
  content, effective type size, and line-weight safeguards; and
- the ten-round audit contract and the final machine-readable release evidence.

I did not edit any scientific source, test, generator, artifact, notebook,
manuscript, manifest, or pipeline. This report is my only repository file
write. I did not read a Round-08 Reviewer-B report. Severity follows
`audits/README.md`: B0 blocks submission, B1 materially changes evidence or
framing, B2 is a bounded correction or required caveat, and B3 is optional
hardening.

The core scientific numbers survived the audit. The current non-release state
is caused by deliberately deferred regeneration after source remediation, not
by a newly discovered numerical contradiction.

## Findings

### F1 — B0 mechanical release gate: the current artifacts are pre-remediation and neither canonical profile proof exists

At the audited snapshot, only
`artifacts/data/publication_pipeline.manifest.json` exists. The required
`publication_pipeline.full.manifest.json` and
`publication_pipeline.verify.manifest.json` are absent, as are full/verify
attempt records. This is correctly not being represented as a pass.

The live hash audit gives the precise reason that an incremental aggregate
cannot substitute for those proofs:

- there are 13 child manifests plus one legacy manifest;
- all 80 child/legacy output paths still exist, their output hashes match, and
  no output has two owners;
- every model/classifier content hash is internally correct;
- all 14 manifests currently record `git.dirty=true`;
- 13 listed input/source hashes are stale after the Round-08 fixes: 12 source
  rows and the manuscript-TeX input row;
- the old aggregate is the explicitly non-execution profile
  `incremental-audit-snapshot`, with zero stages and zero profile runs;
- 18 rows listed by that aggregate no longer match current bytes;
- its old output set omits the legacy manifest and the new accessibility
  alt-text file, and retains three legacy fixed-name log rows that the corrected
  release inventory now excludes; and
- the saved notebook is still a valid 18-code-cell execution, but its stored
  source hash `370ddb...` differs from the remediated builder's current source
  hash `ad6f78...`.

The manuscript compile manifest is likewise tied to the old TeX/PDF snapshot.
The present PDF SHA-256 is
`1e159b85a6a4f91e03201d9726353be8bf6c9fd5325e7488688bef6f04438cde`;
it is not evidence that the new figure-size, typography, citation, vector-art,
and formal-boundary edits have been compiled.

This gate is expected to remain open until all ten audit rounds are frozen. It
must then close mechanically, not by editorial assertion:

1. start from the intended clean, exactly tagged source snapshot;
2. run the documented frozen-environment `full` command;
3. inspect the newly generated figures and compiled manuscript;
4. run the documented `verify` command; and
5. require complete canonical full/verify proofs, exact expected stage lists,
   current output/source hashes, matching immutable log hashes, and a final
   aggregate that hashes both proofs and the completed audit ledger.

The intended commands are correctly documented at `README.md:62-84`. The full
stage contract has 16 stages (`code/run_publication_pipeline.py:97-125`), and
the verify contract has seven stages (`:61-69,633-703`). No full run was launched
in this audit because the main thread explicitly reserved it for the ten-round
freeze.

### F2 — B1 provenance defect: a clean, exactly tagged *start* is not yet machine-certified

The revised attempt/canonical design is now fail-closed and fresh-byte aware.
Preflight failures preserve the full seven-stage expectation, failed attempts
are written under `publication_pipeline_attempts/`, and only complete attempts
replace the canonical profile. The new postflight validator checks the exact
current stage contract, every source/formal/output row, every byte count and
SHA-256, and every stage log. A verify success additionally requires that the
latest full attempt is complete, matches the canonical full run id, and still
matches live bytes (`code/run_publication_pipeline.py:832-931,934-985`). This
closes the earlier partial-run, stale-canonical, and failed-verify retry defects.
Runtime-lock parsing is also total and fail-closed (`:528-574`), and tests cover
preflight failure plus failed-attempt/retry behavior
(`tests/test_encounter_publication_pipeline.py:178-273`).

One material provenance condition remains. `_manifest_base` records Git status
only after the generators have run (`code/run_publication_pipeline.py:785-822`).
A full run normally changes tracked artifacts/manifests, so end-of-run
`dirty=true` neither proves nor disproves that generation started from a clean
tagged commit. The manuscript nevertheless requires regeneration from a clean
tagged commit (`manuscript/encounter_modality_jcp.tex:1637-1641`). The pipeline
must capture immutable start-of-run HEAD, exact tag, and clean status before the
first stage, then carry that start snapshot into every attempt/canonical proof.
This cannot be reconstructed reliably from the post-run worktree.

The aggregate regression test validates canonical stage logs and exact
output-set equality (`tests/test_encounter_publication_pipeline.py:137-175`).
Together with the new profile postflight, it closes current-byte freshness; F2
now concerns only the missing clean/exact-tag start certificate.

### F3 — B0 author/submission gate: required declarations and archival identifier are unresolved

The TeX source still contains explicit funding and conflict-of-interest TODOs
and a placeholder archival DOI (`manuscript/encounter_modality_jcp.tex:1660-1668`).
The compiled PDF therefore has no verified Acknowledgments/Author Declarations
section. This is not something an automated reviewer may invent.

Current [AIP Author Instructions](https://publishing.aip.org/resources/researchers/author-instructions/)
require a conflict-of-interest statement for every article, including a
no-conflict statement, and specify acknowledgments/author declarations before
the data-availability statement and appendices. The corresponding author must
provide and approve funding, contributions, COI, any not-applicable ethics
statement required by the submission form, and the final repository/DOI text.
The manuscript cannot be submitted until that author-owned information replaces
the TODOs and the PDF is rebuilt.

### F4 — B2, source remediation complete but generated-output gate open: current PDF graphics fail final-size AIP checks

The current 21-page PDF is visually coherent, but it predates the graphics
remediation. Independent extraction found final-page minimum text spans on the
12 figure pages of approximately

```text
3.855, 4.491, 5.978, 3.048, 4.491, 3.780,
4.215, 4.411, 4.660, 3.202, 3.278, 4.727 pt.
```

Most full-width figure drawing unions were about `7.057 in`. Figure 12 also
contained two `imshow` raster objects at only `104 PPI`. Those values fail the
current AIP guidance of at least 8-point figure labels/legends, no more than
6.69 inches for a two-column figure, at least 0.5-point final line weight, and
production-resolution raster content.

The main thread closed the source-level causes during this audit:

- every manuscript figure is now centered and capped at `6.65in`
  (`manuscript/encounter_modality_jcp.tex:235-237` and the other eleven
  `\includegraphics` sites);
- `vkcore.plotting.enforce_publication_graphics` enforces conservative
  final-size font and vector-stroke floors across text, lines, markers, patches,
  and collections (`packages/vkcore/src/vkcore/plotting.py:13-91`);
- every manuscript figure generator invokes that helper and hashes
  `plotting.py` as a direct dependency;
- Figure 12's raster `imshow` was replaced by non-rasterized vector
  `pcolormesh` (`code/validate_multid_gig_design.py:352-363`);
- all 12 figure labels and all four table labels now have in-text callouts;
- `figure_table_alt_text.txt` covers Figures 1-12 and Tables I-IV in concise,
  claim-safe language; and
- the manuscript gate now checks callouts/alt text, embedded fonts, absence of
  raster objects, effective type-size distribution, and the generator-level
  font/stroke floors (`tests/test_encounter_manuscript.py:56-153`).

These are strong remediations, but they are not yet represented in any figure
PDF or in the manuscript PDF. F4 closes only after full regeneration, the new
graphics tests pass, and all manuscript pages are rendered and visually
re-inspected for collisions introduced by the larger text and centered 6.65-inch
placement.

### F5 — B2 release gate: the ten-round audit inventory and ledger are not complete

`audits/README.md` requires ten named rounds, each with `reviewer_a.md`,
`reviewer_b.md`, and `resolution.md`, followed by `audit_ledger.json`.
At the snapshot immediately before this report, rounds 01-07 had the required
three files, Round 09 had only Reviewer A, Round 08 and Round 10 were not yet
complete, and `audit_ledger.json` was absent. After this write, Round 08 still
has only Reviewer A by design.

The aggregate source inventory hashes whatever audit Markdown happens to exist
(`code/run_publication_pipeline.py:451-490`), but no release test enforces the
exact R01-R10 matrix or the final ledger. Add an exact inventory assertion before
the final full/verify run; otherwise a missing reviewer/resolution file can be
silently omitted from an otherwise internally consistent aggregate.

### F6 — B3 optional PDF hardening: metadata and Type-3 fonts

All 72 fonts in the current manuscript PDF are embedded, which satisfies the
explicit AIP rule. They comprise 32 Type-1 and 40 embedded Type-3 subsets, and
`pdfinfo` reports blank Title/Author metadata. AIP's current instructions do not
explicitly prohibit embedded Type-3 fonts, so this is not a release failure.
Optional hardening is to set Matplotlib PDF fonts to Type 42/TrueType and add
`pdftitle`/`pdfauthor` metadata in `\hypersetup`.

## Manifest and one-command workflow audit

### Layer ownership and hashes

| Layer | Independently audited state | Release interpretation |
|---|---|---|
| 13 child manifests | all 80 owned output rows and all model/classifier content hashes valid; zero duplicate owners; 12 source rows stale after fixes | source design passes; regenerate in final full |
| legacy `artifacts/manifest.json` | 2 inputs, 6 pre-fix source rows, 11 outputs; output hashes valid; source now stale | full-stage refresh must run last and be hashed |
| aggregate | old `incremental-audit-snapshot`, 0 stages, 0 profile runs, stale/missing rows | inventory only, never execution proof |
| full profile | absent | mandatory mechanical gate |
| verify profile | absent | mandatory mechanical gate |

The corrected pipeline now explicitly includes the legacy manifest in tracked
outputs, excludes recursive profile/attempt JSON, includes only logs declared by
profile/attempt records plus `manuscript_latexmk.log`, and hashes `plotting.py`
in the top-level source inventory (`code/run_publication_pipeline.py:367-490`).
The strengthened child test checks the exact 13+legacy set, all input/source/
output hashes, content hashes, generator lineage, plotting lineage, and unique
ownership (`tests/test_encounter_publication_pipeline.py:76-134`).

### Full/verify separation and fail-closed behavior

The separation is conceptually correct:

- `full` regenerates the 16 numerical/figure/notebook/manuscript/legacy stages;
- `verify` runs the publication test list, static formal integrity, a Lean build,
  and all four axiom drivers;
- profile proofs exclude mutable audit reports and global log inventory, while
  the aggregate includes audits and linked logs;
- each stage has a run-scoped log path, byte count, and SHA-256; and
- nonzero returns, formal-output poisoning, runtime-lock mismatches, Lean
  preflight errors, and shared-cache lock collisions produce incomplete attempts.

The verify list now includes `tests/test_encounter_manuscript.py`
(`code/run_publication_pipeline.py:633-661`). Legacy refresh follows manuscript
compile at the end of full (`:97-125`). The nonblocking shared-cache lock is held
from `lean4_build` through all axiom drivers (`:949-993`).

### Environment and Lean locks

The live frozen Python environment matches `uv.lock` for every package currently
enforced by the pipeline:

```text
Python 3.12.13
numpy 2.5.1
scipy 1.18.0
matplotlib 3.11.0
pandas 3.0.3
nbclient 0.11.0
nbformat 5.10.4 (independently inspected)
```

The official commands use `uv run --frozen`, the profile records the lock hash
and installed/locked versions, and a mismatch prevents stage execution.

The Lean toolchain is `leanprover/lean4:v4.32.0-rc1`. I independently compared
the shared local package cache against all nine `lake-manifest.json` revisions:
mathlib, plausible, LeanSearchClient, importGraph, proofwidgets, aesop, Qq,
batteries, and Cli all matched the locked commits and all nine worktrees were
clean. The per-process source copy plus exclusive build/driver lock therefore
passes the Round-08 concurrency audit. No full Lean build was rerun here.

## Notebook audit

The saved notebook
`notebooks/encounter_publication_validation.ipynb` is structurally valid and
scientifically consistent with its saved artifacts:

- 36 cells total: 18 Markdown and 18 code;
- execution counts exactly `1,2,...,18`;
- zero error outputs and five bounded PNG displays;
- metadata says `saved_artifacts_only`, and code contains no solver subprocess;
- the ten-row claim ledger reports every row as `PASS`; and
- the notebook tests that do not require the newly regenerated source hash pass
  (`3 passed`).

The independently extracted narrative summary is:

| Claim family | Saved/recomputed value |
|---|---|
| finite CTMC fold | max dimensionless residual `6.77505e-13`; slopes `0.500954`, `1.508770` |
| finite Green fixture | dark eigenvalue `-2`; killed pole `-2.5`; residues `[0.25,-0.25]`; total residue `0` |
| finite-radius 2D folds | 2 grids; max residual `1.73472e-17`; separation `[0.493314,0.499325]`; prominence `[1.484297,1.503854]` |
| 2D fold limitation | `theta_c` drift `0.242081657`; grid-converged flag false |
| matched endpoints | 5 grids; patterned resolved-bimodal and homogeneous resolved-unimodal; max budget error `4.10422e-16` |
| coordinate sensitivity | 3 grids; coarse label changes; patch Jaccard range `0.0769231`-`0.229508`; no equivalence/continuum claim |
| bounded trimodality | 4 grids; max tail `4.21838e-11`; min classifier margin `0.00568489`; min channel share `0.718214` |
| trimodal last-two-grid drift | peak-time differences `[0.0596457,0.316233,0.604274]`; no phase-boundary/exhaustive-root claim |
| multidimensional GIG screen | 12 cases, dimensions 1-4, channels 2-4; modes match channels; no bounded realization claim |
| capacity calibration | 2D ratio `0.984828836`; 3D ratio `0.998856130`; no certified continuum patterned coefficient |

The source builder now uses proper Jupyter inline mathematics rather than raw
parenthetical TeX (`code/build_publication_notebook.py:49-105,1047-1089`). The
saved notebook has not yet been rebuilt, so its source-reconstruction test is
correctly a final-full gate rather than a current pass.

## PDF, citation, font, and clipping audit

I rendered every page at 120 DPI and inspected six contact sheets plus individual
figure-heavy pages. The current PDF has:

- 21 Letter-sized pages and 12 figures on pages 4, 8-11, and 13-19;
- four tables, all readable;
- all figures present in order, with no blank panels, missing glyphs, or visible
  clipping;
- no PDF objects or text boxes outside the page box;
- text margins of approximately 54 pt left, 50 pt right, and at least 28 pt top
  on body pages;
- zero compile-record counts for undefined references, undefined citations,
  overfull boxes, and missing files;
- 21 bibliography entries, all 21 cited, with no missing citation key; and
- 72/72 embedded fonts.

The source now calls all 12 figures and all four tables. The old PDF predates
those added callouts, which is another reason the final compile/render gate is
mandatory. The alt-text file has sequential entries for every visual object;
figure descriptions are 34-47 words and table descriptions 23-33 words, with
claim boundaries consistent with the manuscript.

## Checks actually executed

The following scoped, non-mutating tests were run after the live source
remediations:

```bash
PYTHONDONTWRITEBYTECODE=1 uv run --frozen python -m pytest -q \
  -p no:cacheprovider tests/test_encounter_publication_pipeline.py \
  -k 'not child_manifests and not aggregate_manifest and not stage_results_pin'
# 7 passed

PYTHONDONTWRITEBYTECODE=1 uv run --frozen python -m pytest -q \
  -p no:cacheprovider tests/test_encounter_manuscript.py \
  -k 'claim_boundary or called_out or graphics_helper'
# 3 passed after correcting a floating-point boundary assertion

PYTHONDONTWRITEBYTECODE=1 uv run --frozen python -m pytest -q \
  -p no:cacheprovider tests/test_encounter_publication_notebook.py \
  -k 'not source_notebook_reconstruction'
# 3 passed
```

The excluded tests are precisely those expected to fail before regeneration:
child/aggregate hashes, the new figure-PDF typography/vector checks, and the
new notebook source hash. The stage-log probe was excluded because it writes an
adhoc log; I audited the run-scoped log implementation statically instead.

PDF commands used included:

```bash
pdfinfo -box research/reports/encounter_heterogeneous_catalytic/manuscript/encounter_modality_jcp.pdf
pdffonts research/reports/encounter_heterogeneous_catalytic/manuscript/encounter_modality_jcp.pdf
pdfimages -list research/reports/encounter_heterogeneous_catalytic/manuscript/encounter_modality_jcp.pdf
pdftotext research/reports/encounter_heterogeneous_catalytic/manuscript/encounter_modality_jcp.pdf -
pdftoppm -png -r 120 research/reports/encounter_heterogeneous_catalytic/manuscript/encounter_modality_jcp.pdf /tmp/round08_pdfqa/page
```

I also independently recomputed every listed manifest hash, model/classifier
content hash, owner map, notebook execution summary, figure/table callout set,
bibliography key set, PDF page/object bounds, effective font sizes, raster PPI,
runtime-lock versions, and Lean dependency-cache revisions.

## Mandatory final release sequence

Round 08 should be resolved only after the following sequence is evidenced:

```bash
# 1. Freeze all R01-R10 reviewer/resolution files and audit_ledger.json.
# 2. From the clean, exactly tagged source worktree:
uv run --frozen python \
  research/reports/encounter_heterogeneous_catalytic/code/run_publication_pipeline.py \
  --profile full

# 3. Render and inspect every new manuscript page; run PDF/font/raster checks.

uv run --frozen python \
  research/reports/encounter_heterogeneous_catalytic/code/run_publication_pipeline.py \
  --profile verify
```

Acceptance requires all of the following, with no waiver by prose:

- full canonical proof: 16 expected/observed stages, all return code zero;
- verify canonical proof: seven expected/observed stages, all return code zero;
- latest full/verify attempt ids equal their canonical proof ids and are complete;
- every profile output/source/formal/log byte count and SHA-256 matches;
- the legacy manifest is present in the profile/aggregate output inventory;
- the regenerated notebook has 18 executed code cells, zero errors, and the
  current source reconstruction hash;
- the regenerated manuscript/figure tests pass, all pages are visually clean,
  and no raster object or undersized/cropped label remains;
- the aggregate contains the exact completed R01-R10 audit inventory and
  `audit_ledger.json`; and
- author-approved funding, COI/declarations, contributions, and archival DOI
  text replace all submission TODOs.

Subject to those mechanical and author-owned gates, the current scientific
artifact design is suitable for a strong JCP submission: the finite-state,
finite-grid, free-space-screening, and formal boundaries are explicit, and the
reader notebook reproduces the paper-facing quantitative conclusions without
silently rerunning the expensive solvers.
