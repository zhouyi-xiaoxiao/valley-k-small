# Round 31 integrated numerical, figure, and reproducibility attack

Audit snapshot: 2026-07-13T21:03:13Z  
Scope: physical-\(d=2\) exact disk kernel, physical-\(d=3\) exact sphere kernel, broad-patch
\(B=0\) finite-volume bridge, the two four-patch figures, all generated
manuscript numbers, and the numerical-input/manuscript build chain.  This was
a read-only scientific attack: no source, result, figure, or manuscript file
was changed.  All destructive and mutation checks were run in isolated
directories under `/tmp`.

## Technical summary

**The scoped numerical results pass, but the integrated publication evidence
gate is on HOLD.**  Independent recomputation found no numerical discrepancy
in the physical-\(d=2\), physical-\(d=3\), or broad-patch \(B=0\) results.  All
three frozen producers replayed byte-for-byte; both figures and the clean PDF
replayed byte-for-byte; all 75 generated numerical macros agree with their
five source JSON objects.

The HOLD is not caused by a failed kernel or mesh calculation.  It is caused
by one publication-relevant provenance defect: `build_manuscript_inputs.py`
accepts altered non-figure JSON and `compile_manuscript.py` checks only figure
source pins, after it has already copied a newly built PDF into place.  An
altered broad-bridge cusp and an altered G1c control count both compiled with
status `PASS` in isolated attacks.  A pinned d2 alteration was rejected, but
only after the failed run had overwritten the PDF and numerical input.  Three
lower-severity semantic/traceability issues remain in the observable figure
and supporting text.

The PRR promotion gate remains separately on **HOLD** for the already declared
scientific reasons: positive-\(B\) four-slab event mass, mesh and box
convergence of the complete jets, and an independent killed-process solver in
both dimensions have not been supplied.

| Gate | Verdict | Meaning |
|---|---:|---|
| Physical-\(d=2\) exact \(B=0\) kernel | **PASS** | Exact free-exposure relative shape only |
| Physical-\(d=3\) exact \(B=0\) sphere kernel | **PASS** | Exact free-exposure relative shape; small robustness margin |
| Broad-patch four-mesh \(B=0\) bridge | **PASS** | One fixed reflected box; no unbounded-box or positive-\(B\) claim |
| Numerical/figure replay | **PASS** | Three JSONs and two figure bundles replay byte-identically |
| JSON-to-TeX number reconciliation | **PASS** | 75/75 macros agree; one additional literal is not JSON-pinned |
| Clean manuscript build | **PASS** | Two clean builds reproduce the canonical PDF exactly |
| Integrated provenance and failure atomicity | **HOLD** | One P1 defect admits altered macro sources and leaves outputs after a failed pin check |
| Figure semantic/traceability gate | **HOLD** | Three P2 items |
| PRR submission/promotion | **HOLD** | Positive-\(B\), event-mass, convergence, and independent-solver gates remain open |

Severity count: **P0 = 0, P1 = 1, P2 = 3**.

## Findings, ordered by publication risk

### P1 — The numerical macro chain is neither fully fail-closed nor fail-atomic

The current files are internally consistent, but the builder does not enforce
that consistency for every numerical source.

1. `build_manuscript_inputs.py` loads five live JSON objects and checks selected
   statuses/flags, then writes the hashes it just observed into comments
   (`build_manuscript_inputs.py:49-101,344-352`).  Those comments are provenance
   receipts, not expected pins.
2. `compile_manuscript.py` verifies the `source_pins` of included figures only
   (`compile_manuscript.py:98-188,304`).  The broad-bridge result has no included
   figure, and G1c is only an upstream dependency recorded inside the G1d result.
3. Figure provenance is checked after numerical-input generation, two LaTeX
   builds, log writes, and `shutil.copy2(..., FINAL_PDF)`
   (`compile_manuscript.py:191-277,304`).  A rejected pin can therefore leave a
   new untrusted PDF and numerical input beside an old compile manifest.

Isolated attacks reproduced the defect:

| Attack | Expected secure behavior | Observed behavior |
|---|---|---|
| Change broad exact cusp time `13.30724696` to `99.12345678`, preserving statuses/flags | Builder and compile reject before writing | Builder exits 0; full compile exits 0 with `PASS`; generated `\BroadBZeroCuspTime=99.12345678` |
| Remove one G1c control, changing 66 to 65 while G1d still pins the original G1c hash | Nested G1c→G1d provenance rejects | Builder exits 0; full compile exits 0; generated `\GOneCControlCount=65` |
| Change the included d2 cusp time to `99.123456789` | Reject without changing canonical outputs | Compile exits 1 on the figure hash, but only after writing PDF SHA `d7d16b...` and input SHA `960f83...`; copied compile manifest still claims PDF `48e8e0...` and input `d9991f...` |

The positive control is sound: a one-byte d2-result mutation is rejected with
the expected-versus-observed result hash.  The defect is therefore specifically
the incomplete numerical-source closure and late transactional ordering, not a
complete absence of pin checking.

Impact: a stale or edited non-figure result can be promoted into manuscript
numbers while the build reports `PASS`; a failed figure pin can also leave the
working directory in a misleading mixed state.  This is a reproducibility
blocker even though no current canonical number is wrong.

Required closure:

1. Define one release-level numerical-source manifest that pins all five result
   JSONs and their manifests/producers/tests/protocols/dependencies.
2. Before writing anything, verify each result's nested provenance against both
   its manifest and the current files.  In particular, verify G1d's
   `g1c_result_sha256` against the current G1c result and verify the broad
   result's `pinned_file_hashes` and `manifest_sha256`.
3. Make the build transactional: validate all inputs first, build into a
   temporary tree, complete PDF/provenance checks there, then atomically replace
   the PDF, numerical input, logs, and compile manifest together.
4. Add mutation tests for broad-result values, broad producer/dependency hashes,
   G1c nested provenance, an included result, and post-failure output identity.

### P2 — The observable figure still labels the weak-budget object as \(F\), not \(G\)

The manuscript correctly defines
\(G=\lim_{B\downarrow0} f_B/B\) and explicitly says it is not a normalized
positive-event-mass reaction-time law (`encounter_multimodal_prr.tex:652-656`).
The d2/d3 comparison also uses \(G(t)/\max G\).  The observable figure still
uses `$F_{w_*}(t)$` in its legend and ordinate
(`plot_observable_four_patch.py:409,476`).

The d2 observable result/metadata also lacks explicit
`event_mass_observability_verified=false` and
`independent_PDE_solver_verified=false`, while the d2/d3 comparison metadata
states both negatives.  The broad result uses the potentially ambiguous flag
`exact_continuum_observability_passed=true` for a relative-shape result whose
positive-event-mass flag is false.

Required closure: relabel \(F_{w_*}\) as \(G_{w_*}\), use one explicit negative
flag vocabulary across d2, d3, broad, figures, and builders, and prefer
`relative_shape_gate_passed` over an unqualified `observability_passed` name.

### P2 — One manuscript cross-check is not recoverable from canonical JSON

The literal statement that producer-independent real derivatives recover all
five roots within \(1.1\times10^{-12}\)
(`encounter_multimodal_prr.tex:713-714`) is supported by the Round-25 audit and
`notes/observable_four_patch_result.md:126-128`, but it is absent from the
canonical d2 result JSON and generated macros.  It therefore fails a strict
JSON-only manuscript reconciliation even though the independent check was
reproduced in this audit.

The same note says the largest weight spread is \(1.02\times10^{-14}\)
(`notes/observable_four_patch_result.md:130-136`), whereas the canonical JSON,
including the dependent fourth weight, gives \(1.0547119\times10^{-14}\),
correctly rounded to \(1.05\times10^{-14}\) in the manuscript.

Required closure: persist the independent-root discrepancy in the result JSON,
generate the manuscript value from it, and correct the note's weight spread.

### P2 — The two comparison figures use inconsistent time-unit wording

`observable_four_patch` labels the horizontal axis “dimensionless time \(t\)”;
`d2_d3_four_patch` labels the same parameterization “time \(t\)”.  Choose one
definition and use it in both figures and captions.  This does not alter a
number, but it is publication-facing ambiguity.

## Independent kernel and normalization checks

### Physical \(d=2\): exact disk kernel passes

- Full frozen replay is byte-identical to the canonical JSON:
  `4a929cdaf915a9b6180acc0c272a16ae77087d097f2d078b6483c6c9b320a9fc`.
- An independent polar disk integral agrees with the stored half-chord contact
  values to `1.52e-15` relative.
- Independent ordinates at all five roots agree to `1.02e-14` relative;
  finite-difference scaled curvatures agree within `1.65e-6` and reproduce
  max–min–max–min–max.
- The primary normalized bump and patch quadrature weights sum to
  `1.0000000000000024`.  At long time, the computed contact probability is
  `0.1485521966034462`, versus the independently integrated stationary value
  `0.14855219660344687` (`4.48e-15` relative).
- Reproduced selected step and weights are
  \(s=0.11\) and
  \((0.28,0.26950477032608894,0.1065877491928744,0.3439074804810367)\).
  The peak ratio is `0.8541266674`; valley ratios are `0.6667854375` and
  `0.8375426941`.  The worst-valley headroom is `0.0124573059`.

This passes an exact floating-point free-exposure shape gate, not interval root
completeness or positive-\(B\) event-mass observability.

### Physical \(d=3\): exact sphere kernel passes with a real robustness warning

- Full frozen replay is byte-identical to the canonical JSON:
  `125234df2817287c30699d80e30af0e711c036193f0a64a404c8f3e98f98f984`.
- Independent direct spherical integration, using a separately implemented
  pointwise periodic kernel rather than the Fourier–Bessel disk tensor, agrees
  to `4.12e-13` relative.  This is an independent integral representation, not
  an independent PDE solver.
- Root ordinates agree to `6.77e-13`; scaled curvatures agree within `1.00e-6`
  and retain max–min–max–min–max.
- Normalized bump/patch weights sum to `0.9999999999998361`.  The long-time
  contact value is `0.03217523331971377`, versus independent stationary
  integration `0.03217523331971918` (`1.68e-13` relative).
- The selected step and weights are
  \(s=0.10\) and
  \((0.28,0.2113497668133628,0.11201163825953668,0.3966385949271005)\).
  The peak ratio is `0.6338081056`; valley ratios are `0.7692448116` and
  `0.8448001279`.

The second d3 valley is only `0.0051998721` below the `0.85` ceiling.  The
result passes the frozen gate, but this small margin must remain visible in any
positive-\(B\), mesh, or solver continuation.

### Broad-patch \(B=0\) bridge passes its fixed-box scope

- The four-mesh producer replay is byte-identical to the canonical JSON:
  `6a18e668401ae5776eebd7bd58c7bd553838db21998efdba2865cea094ae207b`.
- Independent continuum polar integration at the selected \(s=0.13\) roots
  agrees to `1.14e-14` relative.
- A producer-independent 729-state full Kronecker generator agrees with the
  factorized midpoint/contact jets to `3.33e-16` maximum absolute error.
- Current manifest pins, result pins, and all current producer/dependency files
  agree.  The former sparse-exponential nondeterminism is a closed historical
  P2; the repaired seed-controlled full replay is byte-identical.

| Cubic mesh | max normalization/conservation error | cusp-time error | max root-time error | peak ratio | valley ratios |
|---:|---:|---:|---:|---:|---|
| 65 | `3.77e-15` | `0.5091766` | `0.5336764` | `0.81740` | `0.89522, 0.85721` |
| 97 | `7.55e-15` | `0.2706445` | `0.2642529` | `0.80789` | `0.80815, 0.83166` |
| 129 | `1.51e-14` | `0.1518766` | `0.1562289` | `0.81479` | `0.77128, 0.81793` |
| 193 | `3.02e-14` | `0.0666234` | `0.0668532` | `0.83078` | `0.73758, 0.80695` |

All four meshes retain five alternating sign-changing roots; the frozen bridge
selection requires the 129 and 193 meshes to pass the relative-shape gates,
which they do.  Both error sequences decrease strictly.  Independent one-time
box-tail estimates are `2.22603e-18` for the midpoint and `6.38543e-19` for the
relative-parallel coordinate.  These estimates are useful diagnostics, not a
pathwise exit bound or an unbounded-box convergence proof.

## Why free exposure, event mass, positive \(B\), continuum certification, and solver independence are not interchangeable

Independent stationary integration gives positive long-time limits

\[
G_\infty^{d=2}=0.188708848943992,\qquad
G_\infty^{d=3}=0.0469217905523214,\qquad
G_{\infty,\mathrm{broad}}^{d=2}=0.192459004817885.
\]

Therefore \(G=\lim_{B\downarrow0}f_B/B\) is not integrable over all time and
cannot itself be a normalized reaction-time probability density.  The current
manuscript's “relative shape only; no event-mass claim” restriction is
mathematically necessary.

| Evidence family | What is supported | What is not supported |
|---|---|---|
| Narrow d2 exact kernel | Result-informed \(B=0\) cusp and relative three-peak shape | Positive event mass, finite \(B\), interval root census, independent killed PDE, project gate |
| Narrow d3 exact sphere kernel | Same relative-shape statement in physical d3; direct spherical representation | Independent PDE solver, positive event mass, finite \(B\), interval/project gate |
| Broad d2 bridge | Exact-kernel-to-four-mesh \(B=0\) trend on one fixed box; required meshes pass | Positive \(B\), unbounded-box limit, physical d3, independent solver |
| G1d finite-budget result | One \(B=0.6\), one-box, one-grid nondegenerate fold | Mesh/box-converged fold, cusp, trimodality, independent solver |

The manuscript text and d2/d3 comparison figure respect these boundaries.
The observable-figure notation and machine-readable flag vocabulary need the
P2 cleanup above so that the same firewall is unambiguous everywhere.

## Manuscript-number and figure reconciliation

An independent field-by-field formatter reconstructed every generated macro
from the five source JSON objects:

| Macro family | Count | Mismatches |
|---|---:|---:|
| `FourPatch*` | 20 | 0 |
| `DThree*` | 28 | 0 |
| `GOneC*` | 4 | 0 |
| `GOneD*` | 13 | 0 |
| `BroadBZero*` | 10 | 0 |
| **Total** | **75** | **0** |

The rebuilt `numerical_results.tex` is byte-identical to the canonical file,
SHA-256 `d9991fb91110eaf88c378d8adc25ad4a5b950442175727b1537efe3faabd1915`.
The one exception to JSON-only reconciliation is the literal independent-root
cross-check described in the P2 finding.

Both figure bundles replay byte-identically.  Visual and PDF-object inspection
found no clipping, collisions, raster image XObjects, transparency graphics
states, or Type-3 fonts.  The d2/d3 figure correctly states shape normalization,
separate dimension-specific allocations, \(B=0\), and all mandatory negative
claims.  Its displayed values match JSON after rounding.

The isolated clean manuscript build produced two identical PDFs, both
`48e8e048e8e6272ae3a0b5aba54525204ea127d968b664a08de9a6f1a106f063`,
matching the canonical 12-page PDF.  All fonts are embedded; warning counts for
missing files, overfull boxes, undefined references, and undefined citations
are zero.  This is a build/hygiene PASS, not a scientific release PASS.

## Snapshot hashes

| Artifact | SHA-256 |
|---|---|
| d2 producer | `a553092f3d8bbf50fdf0124a3ea36ba32947c3b339cfcc0265a1cd7f6bc2d4da` |
| d2 test | `c3a2c11c71daf9fcb04e1db9e7c4e489a515d7dfbbb51bc470d310d0c3f76243` |
| d2 protocol | `cbfb6fbe7b69fb66f3b25f7bcde404929a53cf1e8d2045c5fa037fe0fa8432a1` |
| d2 manifest | `1c79fcb31abbc622cee20e915d60f55337376d7555c1c25dab210b3cc5976a69` |
| d2 result | `4a929cdaf915a9b6180acc0c272a16ae77087d097f2d078b6483c6c9b320a9fc` |
| d3 producer | `f8fde83ecdf435acf28a32fb0dec6a22f216bf9f5a817d954f165e62811bf885` |
| d3 test | `bcb0b4264d0d89f140017004b083cb16ad7bf8f8ac7a8ab7b59f48ff9cef3a56` |
| d3 protocol | `280a99653077e7d3ab4f7106d9f078a3588cd7f2ff3ae154f550d99dc47851f9` |
| d3 manifest | `a11e1c4a7842ae69efc76e21a4b6587981d612a457070d601e7001810f16b8cb` |
| d3 result | `125234df2817287c30699d80e30af0e711c036193f0a64a404c8f3e98f98f984` |
| broad producer | `d1d68667f5cbb9c8363a94f2f9ea22540f841065e02696f669beca9758e3a233` |
| broad test | `0d683f8ed7cfd8fee2cef992078962a05c2cb8074629c8947cb233300c8b4490` |
| broad protocol | `56937590efc0ea90841cd7ff32b3386c5d81469ec51034329d7e0e13133bee35` |
| broad manifest | `263d4bd5e95f4cf477916948f2e4bbf3cd99066ac9dc9a9ab5726f2030a6f1e8` |
| broad result | `6a18e668401ae5776eebd7bd58c7bd553838db21998efdba2865cea094ae207b` |
| broad FV dependency | `7fa9ea6114328736c89739459c293aefa9311514764ec3cfe4f0ceb5a1875201` |
| broad grid dependency | `e0322b212e466b1b640f5adcf30d67d119d2f6fe4cc622eb532082b6cd251701` |
| observable plotter | `398f19541423f560846a8b68b48b4acbde69b188d1e2ed199aa0cc6bb73ca3bb` |
| observable metadata | `5efb61e03d6a266e1714fdf49311ddb8054a5bb28b735910f7648e4cfeccfa0e` |
| observable PDF | `2e88f9278236f273c67901316a1cad9a4d92472ec9ea7f5ef64e0f4232641ad8` |
| d2/d3 plotter | `f390315ea42486fe4341730e00039225f5c2c087cee5ce817eec59173f3f93aa` |
| d2/d3 metadata | `dcb43fff821442df9e4ec32de398b06cce175c5f2afd42bbdb8a433bf2a18aa9` |
| d2/d3 PDF | `c5419173faf0626b3c97af5d20e7477739771a11d142f661ed22857cdac93ac6` |
| numerical-input builder | `b65684882424c677082bad02f738242b8ae56aecbff660154484f30ee2acee0e` |
| numerical-input tests | `61f6ffd24895fbb5153f828d51ba8c11b2ede97bebe133b00df47ee7bf74d244` |
| manuscript compiler | `a121629ebf2fdc76f434211c2acf0ef17a999d0b29fe026a1dd3c008f8b478e4` |
| compiler tests | `95f1ec9494232ac4051e71671496998d001e382f5ddd8babb34ffb84dd04fb07` |
| numerical input | `d9991fb91110eaf88c378d8adc25ad4a5b950442175727b1537efe3faabd1915` |
| manuscript TeX | `ed29b1613572de107e321ac4f7bde5826d5929cd22431f572fae6ac366a725c0` |
| manuscript PDF | `48e8e048e8e6272ae3a0b5aba54525204ea127d968b664a08de9a6f1a106f063` |
| compile manifest | `8db37ba75ab3014132da23a0aaa2bcb156648775ccaf1dec08939c10c958b5b0` |

## Reproducible commands and observed outcomes

Run from the repository root with the repository environment.

```bash
env PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -q -p no:cacheprovider \
  research/reports/encounter_multimodal_prr/code/test_continuum_observable_four_patch.py \
  research/reports/encounter_multimodal_prr/code/test_continuum_observable_four_patch_d3.py \
  research/reports/encounter_multimodal_prr/code/test_continuum_broad_patch_b0_bridge.py \
  research/reports/encounter_multimodal_prr/code/test_plot_d2_d3_four_patch.py \
  research/reports/encounter_multimodal_prr/code/test_plot_observable_four_patch.py \
  research/reports/encounter_multimodal_prr/code/test_build_manuscript_inputs.py \
  research/reports/encounter_multimodal_prr/code/test_compile_manuscript.py
# 39 passed
```

```bash
.venv/bin/ruff check <the 14 scoped producer, plotter, builder, compiler, and test files>
.venv/bin/ruff format --check <the same 14 files>
# All checks passed; 14 files already formatted
```

```bash
.venv/bin/python research/reports/encounter_multimodal_prr/code/continuum_observable_four_patch.py \
  --execute-frozen --output /tmp/round31_d2.json
.venv/bin/python research/reports/encounter_multimodal_prr/code/continuum_observable_four_patch_d3.py \
  --execute-frozen --output /tmp/round31_d3.json
.venv/bin/python research/reports/encounter_multimodal_prr/code/continuum_broad_patch_b0_bridge.py \
  --execute-frozen --output /tmp/round31_b0_bridge.json
cmp /tmp/round31_d2.json research/reports/encounter_multimodal_prr/artifacts/data/continuum_observable_four_patch_result.json
cmp /tmp/round31_d3.json research/reports/encounter_multimodal_prr/artifacts/data/continuum_observable_four_patch_d3_result.json
cmp /tmp/round31_b0_bridge.json research/reports/encounter_multimodal_prr/artifacts/data/continuum_broad_patch_b0_bridge_result.json
# all three cmp commands exit 0
```

The figure and manuscript replays were run in a `/tmp` mirror preserving the
repository depth and with that mirror's `.venv` symlink resolved to the
repository environment:

```bash
$TMP/.venv/bin/python $TMP/research/reports/encounter_multimodal_prr/code/plot_observable_four_patch.py
$TMP/.venv/bin/python $TMP/research/reports/encounter_multimodal_prr/code/plot_d2_d3_four_patch.py
$TMP/.venv/bin/python $TMP/research/reports/encounter_multimodal_prr/code/build_manuscript_inputs.py
$TMP/.venv/bin/python $TMP/research/reports/encounter_multimodal_prr/code/compile_manuscript.py
# figures, metadata, numerical input, and clean PDF match the snapshot hashes above
```

The P1 attacks used fresh mirrors, changed exactly one JSON value/list, and ran
the same builder/compiler.  Their generated hashes and exit statuses are
recorded in the P1 table so the secure-failure tests can be implemented without
relying on this audit's prose.

## Final disposition and next steps

1. **Keep the scoped d2/d3 exact-kernel and broad \(B=0\) numerical statements.**
   They survived independent mathematics, full producer replay, figure replay,
   and JSON reconciliation.
2. **Do not mark the integrated reproducibility gate PASS** until the P1 source
   closure and transactional build defect is repaired and attacked again.
3. **Close the three P2 items** before treating the figures/manuscript as a
   publication-ready evidence package.
4. **Do not promote the project to PRR submission readiness** on this audit.
   After the pipeline repair, the decisive scientific work remains positive-\(B\)
   event-mass-qualified four-slab continuation, complete mesh/box jet
   convergence, and an independent killed-process solver, first in d2 and then
   in the more fragile d3 design.

No further reduced-clock scan or additional \(B=0\) figure can close those
scientific gates.
