# Round 08 — Reproducibility and submission artifacts, Reviewer B

**Review date:** 2026-07-11  
**Snapshot audited:** branch `dpma-audit-20260630`, Git
`3531353a515160b09899199a9257e7455a654b22`, plus the live uncommitted encounter
report state through the final publication-source inventory repair at 09:29 BST  
**Reviewer role:** independent Reviewer B  
**Only repository write made by this review:** this file

## 1. Executive verdict

**Round-08 research/artifact verdict: PASS.** I found no B0 scientific-data,
formal, notebook, figure, reference, or PDF defect, and no open B1/B2 defect in
the single-process reproducibility path after the remediations made during this
review. The numerical artifacts support the manuscript's deliberately bounded
claims; the Lean evidence is complete within its stated algebraic boundary; the
executed notebook is internally consistent; all twelve publication figures are
vector PDFs with embedded fonts and readable final-size type; and the current
23-page RevTeX PDF independently rebuilds without undefined citations,
undefined references, overfull boxes, or missing files.

Five material workflow falsifiers found across the audit are now closed:

1. every stage receives a fixed `SOURCE_DATE_EPOCH`, `FORCE_SOURCE_DATE=1`, and
   `TZ=UTC`; independent duplicate figure builds produced byte-identical PDF
   and PNG files; and
2. a process that loses the global artifact-workspace lock now exits with code
   75 before it can write a failed attempt or aggregate manifest. My independent
   held-lock subprocess produced no `publication_pipeline*.json` write;
3. a failed notebook schema traversal stopped `full` at 14/16 rather than
   publishing a false success; the reader now consumes the nested JSON artifact
   and its 4/4 tests pass;
4. failed/incomplete attempts are immutable and never overwrite the success-only
   canonical proof; and
5. the final source inventory now covers the complete direct `vkcore` import
   closure, including `__init__.py` and `fpt.py`, plus their direct tests.

The current checkout is nevertheless **not the final execution-proof snapshot**.
A frozen post-notebook-fix `full` run completed all 16 stages, but its source
inventory was then strengthened from 85 to 90 rows. The final 90-source `full`
proof is therefore regenerated after this reviewer file is frozen. A canonical
`verify` proof cannot exist until the root writes the Round-08/Round-10 resolutions
and ten-round ledger: the pre-resolution verify attempt passed 124/125 tests and
failed only that deliberate self-reference gate. This is a required post-audit
closure action, not evidence against the scientific result.

**External submission-release verdict: HOLD / FAIL.** The author-owned metadata
checklist is intentionally unresolved, the public data/code DOI and license are
absent, the report is untracked in a dirty working tree, and `HEAD` has no exact
tag. These gates are separate from the research/reproducibility PASS and must not
be represented as completed.

### Severity summary

| Level | Open count | Verdict |
|---|---:|---|
| B0 | 0 | No invalid numerical claim, broken formal proof, missing evidence layer, or unusable submission artifact found. |
| B1 | 0 | Determinism, success-only proofs, lock exclusion, notebook schema traversal, and executable-source coverage were independently retested and closed. |
| B2 | 0 | No bounded correction remains in the audited scientific or artifact claims; final proof regeneration is a procedural closure action. |
| B3 | 3 | Optional PDF accessibility/font polish and local-filesystem diagnostic hardening. |
| External release | 2 categories | Author metadata/archive facts and the staged clean exact-tag proof chain remain incomplete. |

## 2. Independence and audit scope

I did not open or use
`audits/round_08_reproducibility/reviewer_a.md`. A directory listing exposed only
that filename. Every conclusion below comes from the README, pipeline/checker
source, tests, numerical data/NPZ files, notebook, Lean source/build/axiom
outputs, manuscript source, independently compiled PDF, figure PDFs, bibliography,
alt-text file, manifests, logs, and live Git state.

I tried to falsify the following:

1. whether `full`/`verify` stage contracts can pass on a prefix, stale proof,
   missing log, runtime mismatch, failed retry, or lock collision;
2. whether the machine-readable 1D/2D/3D/multidimensional results actually
   support the modality and capacity language in the manuscript;
3. whether the notebook silently recomputes or contradicts archived evidence;
4. whether Lean coverage depends on project axioms or is claimed beyond the
   theorem types;
5. whether the twelve figures survive conservative final-size checks, contain
   raster fallbacks, or have unembedded fonts;
6. whether the manuscript has stale references, uncited bibliography entries,
   missing callouts/alt text, compile warnings, or text/PDF drift; and
7. whether a clean-tag release can be executed without the build itself making
   the starting tag dirty.

## 3. Audit matrix

| Layer | Evidence checked | Result |
|---|---|---|
| README and one-command contract | `README.md:70-101`; full/verify stage lists; deterministic environment; staged release description | PASS |
| Failure semantics | exact expected/observed stages, zero failures/return codes, success-only canonical proofs, immutable attempts, latest-attempt check | PASS |
| Locks and logs | per-stage byte/SHA pins; global workspace lock; separate Lean lock; independent held-lock subprocess | PASS after closure |
| Runtime/provenance | `uv.lock` hash and installed versions; source/formal/output/log inventories | PASS for audited runs; final manifests must be regenerated |
| Numerical evidence | matched control, fold, trimodality, multidimensional GIG construction, 2D/3D capacity, raw NPZ series | PASS within stated finite-grid/screening scope |
| Lean | fresh off-OneDrive `lake build`; four axiom drivers; theorem inventory and forbidden-marker scan | PASS within declared algebraic boundary |
| Notebook | 36 cells, 18 executed code cells, no errors, five PNG outputs, ten passing validation claims | PASS |
| Manuscript/PDF | independent TeX Live build, text comparison, 23 pages, references, figures/tables, fonts, vector-art and visual QA | PASS |
| Submission metadata/archive | author/funding/conflict/CRediT/DOI/license/PRE form checklist | HOLD |
| Exact-tag release | dirty untracked report; no exact tag; final full/verify/aggregate proof chain absent | HOLD |

## 4. Closed workflow findings

### Closed B1-01 — creation-time metadata made regenerated figures drift

The live pipeline now defines `REPRODUCIBLE_STAGE_ENV` at
`code/run_publication_pipeline.py:70-74`, merges it into every stage environment
at `:106-112`, and uses that environment from `main()` at `:1138`. The README
states the same contract at `README.md:82-84`.

I copied `plot_model_schematic.py` into two independent temporary report trees,
ran both with the declared environment, and obtained:

```text
PDF  167f6497b93fdb3b657d80bb6ffded7ba21844199a1bb293081e5a4f4ed86e8e  (both)
PNG  f6b303ebd84855b611156503cf63ff006edee3bb408442a906bf6c11f62b3c47  (both)
```

The two child manifests differed only in the intended microsecond-resolution
`generated_at_utc` provenance field. Thus the scientific/visual output is
bitwise stable while the run record remains an honest per-execution record.

### Closed B1-02 — failed attempts and incomplete prefixes could contaminate proof semantics

The current code makes `execution.complete` require a nonempty exact ordered
stage list, no failures, and all zero return codes
(`run_publication_pipeline.py:846-855`). It validates all live source, formal,
output and log hashes at `:875-931`; requires the latest immutable attempt to be
complete and to match the canonical success at `:934-968`; writes every attempt
under a run-id-qualified pathname; and replaces the canonical profile proof only
after a complete run (`:971-1048`). The aggregate separately exposes canonical
profile proofs and latest attempts (`:1060-1097`).

Focused tests independently passed for preflight failure, failed-attempt retry,
partial execution, runtime lock matching, deterministic environment, and release
ancestry. The earlier process-level failure probe also confirmed that a failed
attempt leaves the previous canonical success byte-for-byte unchanged and is
still visible as the latest nonpassing attempt.

### Closed B1-03 — a lock loser still wrote into the locked artifact workspace

The first audited implementation detected a held global lock but continued into
`_write_manifest`, so a later-starting loser could rewrite the aggregate while a
winning run was modifying artifacts and could remain lexicographically the
latest failed attempt after the winner completed.

The current source closes that race. `_acquire_workspace_lock` at
`run_publication_pipeline.py:116-129` raises a dedicated exception. `main()` at
`:1155-1169` catches it and exits with code 75 before runtime inspection, stage
execution, or manifest publication. The regression test is
`tests/test_encounter_publication_pipeline.py:141-164`.

My independent subprocess held a lock below a temporary `HOME`, invoked the
current pipeline, and found:

```text
returncode 75
stderr another publication pipeline owns the artifact workspace lock (...)
publication_manifest_writes []
```

This is the correct fail-closed behavior: only the lock owner can mutate the
artifact tree.

### Closed B1-04 — the reader notebook traversed a nested CSV field as a dictionary

The first frozen full attempt after the three-grid fold extension stopped at
`reader_notebook` (14/16 observed stages). The CSV representation of
`resolution_diagnostics` is a string, but the notebook cell indexed each iterated
value as a nested dictionary and raised `TypeError: string indices must be
integers`. The pipeline wrote an immutable incomplete attempt, retained the older
canonical success unchanged, and did not run the manuscript/legacy-manifest tail
stages.

`code/build_publication_notebook.py:183-214` now declares and reads
`finite_radius_2d_matched_control.json` and constructs the DataFrame from that
nested JSON rather than from a lossy CSV encoding. The regenerated notebook has
all 18 code cells executed, no error output, and passes its tests 4/4. A subsequent
full run completed `reader_notebook` and all 16 stages.

### Closed B1-05 — the publication source proof omitted two directly executed package files

A final dependency-closure audit found that `build_report.py` directly imports
`vkcore.fpt`, while package import semantics also depend on `vkcore/__init__.py`;
neither file was in the top-level profile source inventory. The omission would
have allowed either executable source file to change without invalidating the
publication proof.

The final inventory at `run_publication_pipeline.py:486-514` covers the complete
direct report import closure:
`__init__`, `encounter`, `encounter2d`, `encounter3d`, `fpt`, `morphology`,
`plotting`, and `provenance`. It also includes the direct `test_fpt.py`,
`test_morphology.py`, and `test_provenance.py` gates. Regression assertions in
`tests/test_encounter_publication_pipeline.py:456-458` pin the formerly omitted
paths. The final profile inventory has 90 source rows. I found no remaining
direct local import outside this set.

### Closed B2-01 — exact-tag release was incompatible with generated proof commits

The release protocol is now explicitly staged at `README.md:89-96`:

1. clean audited source tag and `full --release`;
2. commit/tag the full artifacts and proof;
3. run `verify --release` from that clean artifact tag;
4. commit/tag the verify proof and aggregate; and
5. run `check_publication_proofs.py --require-clean-tag` from the clean final
   tag.

`code/check_publication_proofs.py:41-84` requires the full source commit to be an
ancestor of the verify artifact commit and that commit to be an ancestor of the
clean exact-tagged final commit. The positive and negative ancestry tests at
`tests/test_encounter_publication_pipeline.py:100-137` pass. This resolves the
otherwise impossible demand that a generated-output run both start and finish at
one unchanged clean tag.

## 5. Independent evidence checks

### 5.1 Pipeline, manifests, logs, and runtime

The frozen post-notebook-fix proof
`20260711T080604670455Z-44227` recorded exactly 16 expected and 16 observed
successful stages, no failures, 85 source rows, four formal-evidence rows, and
100 output rows. I checked every recorded byte count and SHA-256, including every
stage log, and `_canonical_profile_errors("full")` returned `[]`. The runtime
evidence matched the hashed
`uv.lock` for NumPy 2.5.1, SciPy 1.18.0, Matplotlib 3.11.0, pandas 3.0.3, and
nbclient 0.11.0.

That run is direct evidence that the frozen scientific workload executes, but the
subsequent five-file source-inventory repair correctly requires one final `full`
proof with 90 source rows. The root resolution must cite that final run and then
regenerate `verify` and the aggregate. The pre-resolution verify attempt
`20260711T081827250359Z-52352` ran the complete publication pytest command: 124
of 125 tests passed, and the sole failure was the intentionally impossible
Round-08 resolution/ten-round-ledger self-reference. Lean stages were therefore
not mislabeled as run. Those stages are independently checked below and must be
recorded canonically after the root creates the resolutions and ledger.

Focused final-state checks passed for the fold artifacts (10/10), notebook (4/4),
manuscript/figures (6/6), workspace-lock collision, release ancestry, runtime and
source-coverage repairs. A broader reviewer invocation passed 122 read-only
publication tests; the intentionally excluded cases were the resolution/ledger
self-reference, the audit-sensitive aggregate live-hash test, and the single test
that deliberately writes an adhoc stage log. The unfiltered pipeline run supplies
the stronger 124/125 result above.

### 5.2 Numerical evidence versus manuscript claims

I independently read the JSON/CSV and sampled the archived NPZ series rather
than relying on figure captions.

| Claim family | Independent observation |
|---|---|
| Matched patterned versus homogeneous | Five patterned grids are resolved-bimodal; both the state-count- and product-control-volume-matched homogeneous controls are resolved-unimodal on all five. Patterned strict secondary/primary ratios span 4.5807%–8.1475%; state-count controls span 1.0229%–1.8099%, and control-volume controls remain below 1.2168%. Therefore every cutoff in `(1.8099%, 4.5807%)` separates the patterned family from both controls, not only the displayed 3% choice. Maximum budget error across the two matching definitions is `4.1043e-16`. |
| Three-patch bounded 2D | Each of `9x5`, `11x7`, `13x9`, and `15x11` has five detected simple derivative roots in max–min–max–min–max order and three resolved maxima dominated in order by near/middle/far channels. Maximum `|f_t|` is about `1.87e-15`; survival at `t=2000` is at most `4.22e-11`. |
| Multidimensional GIG screening | Twelve cases cover dimensions 1–4 and 2/3/4 channels. Root counts are 3/5/7 and maximum counts 2/3/4 in every dimension; maximum scaled derivative residual is `1.75e-13`. The manuscript correctly labels this a free-space narrow-patch screening construction, not a bounded-Doi theorem. |
| Fold | Three physical finite-grid folds occur on `9x5`, `11x7`, and `13x9`, with maximum dimensionless residual `3.98e-12`, nonzero third derivative/transversality, and held-out separation/prominence exponents `0.493–0.499` and `1.484–1.504`. State-count-matched controls span `0.262` in `theta_c`; product-control-volume matching preserves all three nondegenerate folds but spans `0.384`. A `12x8` continuation root lies at negative `theta`, while the bounded `10x6` search reports only a positive near miss and explicitly does not prove absence. The maximum omitted endpoint tail mass is below `1.9e-6`, four orders below the 3% resolution scale. These diagnostics support the finite-grid mechanism certificate and rule out a continuum fold-location claim. |
| Capacity | The 2D logarithmic ratios approach one across the grid sequence; the 3D mean/leading-order ratio improves from about `0.886` to `0.969`. The claims remain calibration evidence rather than a continuum convergence theorem. |

I found no hidden upgrade from detected sign-changing roots to interval-certified
root exhaustion, from finite-grid persistence to a continuum phase boundary, or
from the pure `a^(d-2)` power law to a formally proved capacity constant.

### 5.3 Lean boundary

A fresh build in a local temporary workspace completed `3109/3109` jobs. The
independent theorem inventory was exactly
`100 = 46 legacy + 54 encounter-specific`, with the encounter split
`14 + 28 + 12`. Fresh axiom drivers returned `46/14/28/12` rows; every theorem
depended only on `propext`, `Classical.choice`, and `Quot.sound`. No `sorry`,
`admit`, project `axiom`, `native_decide`, or `sorryAx` was found.

The README and manuscript accurately limit formal coverage to finite-mixture and
scalar/componentwise algebra, the one-dimensional contact bound, pure capacity-
power algebra, stationary-point design, and finite exponential derivatives. They
do not claim Lean proofs of the PDE, continuum limit, floating-point roots,
numerical mode uniqueness, or model applicability.

### 5.4 Notebook

The reader notebook has 36 cells, including 18 code cells with execution counts,
no error outputs, and five PNG outputs. Its terminal
`VALIDATION_SUMMARY_JSON` reports ten claims and `all_claims_pass=true`. The
notebook reads archived evidence rather than silently regenerating a different
model; focused notebook tests passed 4/4.

### 5.5 Manuscript, references, figures, and PDF

An independent TeX Live 2025/RevTeX 4.2f build produced 23 pages and 826,687
bytes. The final log
has zero undefined references, zero undefined citations, zero overfull boxes,
and no missing files. `pdftotext -layout` from the current repository PDF is
byte-identical to the independent build's extracted text (SHA-256
`8094a1c80c4842731e9fa2781817a4981d477a85ad402570160e29c56838088e`).
All fonts in the main PDF are embedded. I re-rendered and visually inspected the
revised matched-control/fold/coordinate/mechanism pages 12--15; the new three-grid
fold curves, legends, table, captions, and two-column continuation are legible and
do not overlap.

The manuscript contains exactly twelve figure callouts and four table callouts.
All 135 labels are unique; all 37 explicit cross-reference commands resolve; all
36 bibliography entries are cited; and the separate accessibility file contains substantive descriptions
for Figures 1–12 and Tables I–IV.

For each of the twelve source figure PDFs I checked `pdffonts`, `pdfimages`, and
text geometry at a conservative 6.2-inch target width even though the manuscript
uses 6.65 inches. Every font is embedded, none of the figure PDFs contains a
raster image object, the smallest extracted script glyph is at least 5 pt, and
each median extracted text size is at least 9.2 pt. The generator-level helper
also enforces an 8.5 pt effective base-font floor and a 0.65 pt effective stroke
floor. These checks satisfy the practical final-size readability requirements in
the official [APS Style Basics](https://journals.aps.org/authors/style-basics).

The current PDF is a valid single initial-submission artifact under the official
[Physical Review web-submission guidance](https://journals.aps.org/authors/web-submission-guidelines-physical-review),
subject to the metadata/archive gates below.

## 6. B3 optional hardening

### B3-01 — PDF-native accessibility and Type 3 production polish

`pdfinfo` reports `Tagged: no`. The separate figure/table alt-text file is complete,
but the PDF itself does not carry a tagged structure tree. The embedded
Matplotlib MathText fonts are Type 3, while all body fonts are embedded Type 1.
Neither condition blocks the audited PDF or APS initial submission, and the vector
art is readable. For acceptance-stage production, tagged-PDF export and Type
42/TrueType figure fonts would improve accessibility and downstream editing.

### B3-02 — cross-directory TeX PDF identity is path-dependent only in `/ID`

Two fixed-environment builds in different output directories had identical size,
text, pages, fonts, and content streams but different PDF trailer `/ID` values.
A forced rebuild in the same output directory was byte-identical. The pipeline's
same-path artifact regeneration is therefore deterministic, and scientific
content is checkout-independent; an optional normalization step could remove the
path-dependent trailer identifier if cross-directory byte identity is desired.

### B3-03 — improve diagnostics for transient cloud-file reads

One live proof-checker invocation on the OneDrive checkout failed closed with a
macOS `TimeoutError` while hashing a hydrated file. It did not produce a false
PASS, but the exception did not identify the candidate path. The release run
should use a fully hydrated local checkout. Optionally, `_sha256`/proof validation
could catch `OSError` and report the exact path so transient provider failures are
actionable rather than opaque.

## 7. Separate submission-release gates

`manuscript/SUBMISSION_METADATA_REQUIRED.md:7-22` still has seven unchecked
items. Six require author or repository facts that cannot be inferred safely:

1. final names/order/affiliations/corresponding author/emails/ORCIDs;
2. funding and grant identifiers;
3. conflict-of-interest declaration;
4. CRediT contributions for Xiaoxiao Zhouyi and Luca Giuggioli;
5. public archival data/code DOI and license; and
6. PRE data/code availability form wording.

APS requires an appropriate data-availability statement and citation of public
data/software where applicable; see the official
[APS Data Availability Statements policy](https://journals.aps.org/authors/data-availability-statements).

The seventh item is the release execution itself. At this review snapshot:

```text
branch  dpma-audit-20260630
HEAD    3531353a515160b09899199a9257e7455a654b22
exact tag  none
report/tests  untracked; working tree dirty
canonical full  final 90-source regeneration begins after this reviewer freeze
canonical verify  absent until Round-08/Round-10 resolutions and ledger exist
```

Required final sequence:

1. resolve all audit findings and author-owned manuscript facts that are needed
   for the submission artifact;
2. commit a clean audited source snapshot and create the source tag;
3. run `full --release` and require all 16 stages to pass;
4. commit/tag the generated artifacts and full proof;
5. run `verify --release`, including the now-complete Round-08/ten-round ledger
   tests;
6. commit/tag the verify proof and aggregate;
7. run `check_publication_proofs.py --require-clean-tag` from the clean final
   exact tag; and
8. archive/cite the data and code and insert the DOI/license.

## 8. Representative commands actually executed

```text
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  .venv/bin/python -m pytest -q -p no:cacheprovider \
  tests/test_encounter_publication_pipeline.py::<focused tests>

PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  .venv/bin/python -m pytest -q -p no:cacheprovider \
  tests/test_encounter_publication_notebook.py

PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  .venv/bin/python -m pytest -q -p no:cacheprovider \
  tests/test_encounter_manuscript.py

SOURCE_DATE_EPOCH=1783728000 FORCE_SOURCE_DATE=1 TZ=UTC \
  latexmk -pdf -interaction=nonstopmode -halt-on-error \
  -outdir=/tmp/round08_b_recheck.../latex encounter_modality_jcp.tex

pdftotext -layout <repository.pdf> <text>
pdftotext -layout <independent.pdf> <text>
pdfinfo <independent.pdf>
pdffonts <independent.pdf>
```

The fresh Lean build and four axiom-driver commands were executed in a temporary
off-OneDrive copy. All temporary numerical, lock, and TeX probes were outside the
repository.

## 9. Final recommendation

**PASS Round 08 for the research evidence and single-process reproducibility
implementation.** There are no open B0, B1, or B2 findings after the deterministic
environment, staged release, success-only proof, and lock-exclusion remediations.

**Do not label the current checkout submission-ready.** The root agent must still
regenerate the final `full`/`verify`/aggregate proofs after audit resolution, and
the authors must complete metadata, archival DOI/license, and the clean exact-tag
release chain. Until those external/procedural gates pass, the correct package
status is **HOLD / FAIL for release**, not a failure of the scientific result.
