# Round 07 Lean-formal audit — Reviewer A

Date: 2026-07-11  
Reviewer: A (independent statement-fidelity, build, axiom, and workflow audit)  
Verdict: **PASS for current formal correctness and statement fidelity: no B0 or B1; one B2 workflow defect was resolved during the audit, one B2 clean-snapshot release gate remains open, and two B3 hardening/documentation items do not affect the proofs**

## Scope and independence

I audited the current Lean 4/mathlib package used by the encounter manuscript,
with special attention to statement strength rather than merely whether tactics
elaborate.  I inspected every new definition and theorem in
`FormalLean/Encounter.lean`, `FormalLean/EncounterContinuum.lean`, and
`FormalLean/EncounterDesign.lean`; compared all theorem declarations with all
four `#print axioms` drivers and saved reports; independently reproduced the
100/54 counts; inspected the manuscript, package README, theory-to-Lean bridge,
and publication verification pipeline; and searched all formal modules for
proof placeholders and project postulates.  I did not edit any Lean source,
scientific source, test, numerical artifact, manuscript, or pipeline.  This
report is my only repository write.

I did not read a Round-07 Reviewer-B report.  Severity follows
`audits/README.md`: B0 blocks submission, B1 materially changes a derivation,
evidence, or framing, B2 is a bounded correction or required caveat, and B3 is
optional hardening.

The current theorem statements are sound and unusually explicit about their
limits.  In particular, Lean proves exact finite algebra and derivative
identities; it does not prove the encounter PDE, Green-operator domains,
continuum convergence, GIG approximation accuracy, numerical roots, or the
existence/persistence of the reported multimodal mixtures.  No contradiction,
vacuous physical hypothesis, hidden project axiom, `sorry`, `admit`, or
`native_decide` was found.

## Findings

### F1 — B2, resolved during this audit: the original verify workflow did not fail closed on the 100-theorem axiom claim

The manuscript states that the package contains 100 sorry-free theorems,
including 54 encounter-specific statements, and that theorem-by-theorem axiom
reports contain only `propext`, `Classical.choice`, and `Quot.sound`
(`manuscript/encounter_modality_jcp.tex:1585-1596`).  Those statements are true
of the current source, but at the start of this audit the publication pipeline
did not mechanically protect the full claim:

- it ran only the three encounter axiom drivers and omitted
  `AxiomsReport.lean`, which covers the legacy 46 theorems;
- it treated a zero process return code as success without parsing `#print
  axioms` output, even though `sorryAx` and nonstandard axioms do not
  necessarily make Lean exit nonzero;
- it had no executable assertion of the partition `100 = 46 + 54`; and
- its formal source inventory omitted the seven legacy modules and the legacy
  axiom report.

This was a workflow/evidence defect, not a theorem defect.  The main thread
closed it in the live snapshot.  The new static integrity gate now strips
nested Lean comments, rejects `sorry`, `admit`, `axiom`, and `native_decide`,
counts every theorem in all ten modules, enforces the exact 46/54 partition,
checks one-to-one coverage by all four drivers, parses every saved axiom row,
and rejects any dependency outside the three-item allowlist
(`code/run_publication_pipeline.py:117-203,206-312`).  Fresh Lean-stage output
is independently parsed and can turn an otherwise zero return code into a
failed stage (`code/run_publication_pipeline.py:450-490`).  The verify profile
now runs the legacy driver as well as all three encounter drivers
(`code/run_publication_pipeline.py:493-562`), and the source inventory now
hashes the complete formal package (`code/run_publication_pipeline.py:379-435`).

The regression test asserts 46/54/100, four reports totaling 100 theorem rows,
all ten source modules, and rejection of poisoned `sorryAx` output
(`tests/test_encounter_publication_pipeline.py:96-140`).  I independently ran

```bash
PYTHONDONTWRITEBYTECODE=1 uv run --no-sync pytest -q -p no:cacheprovider \
  tests/test_encounter_publication_pipeline.py -k formal_integrity
```

and obtained `1 passed`.  The generated
`artifacts/data/lean_formal_integrity.json` records the source/driver/report
hashes and the exact counts.  This closes F1 in the current workspace.

### F2 — B2, open release gate: the encounter formal extension is not yet frozen in version control

The three encounter modules, three encounter axiom drivers, and three saved
encounter axiom reports are currently untracked by Git; `FormalLean.lean` and
the formal README are modified.  The aggregate manifest and the new formal
integrity artifact do hash the live files, so the present workspace snapshot
is internally tied together.  It is nevertheless not reproducible from the
manifest's recorded commit alone.

This is consistent with the manuscript's own explicit pre-submission gate that
all manifests be regenerated from a clean tagged commit
(`manuscript/encounter_modality_jcp.tex:1579-1583`).  It must remain an open B2
until the formal extension, drivers, reports, integrity artifact, tests, and
documentation are committed together and a clean verify manifest records the
successful Lean stages.  No change to a mathematical claim is required.

### F3 — B3, substantially resolved during this audit: serialize the shared mathlib cache

The verification workspace is now process-unique, which prevents two pipeline
runs from overwriting the same project build directory
(`code/run_publication_pipeline.py:565-592`).  It still symlinks runs to the
same dependency package directory (`code/run_publication_pipeline.py:594-615`),
but the main thread added a nonblocking exclusive lock held from `lean4_build`
through all four axiom drivers (`code/run_publication_pipeline.py:672-716`).
Thus two verify profiles now fail explicitly instead of racing on that cache.

The need for the lock was observed directly.  During this audit, two concurrent
manual builds/cache operations against an incompletely restored cache produced a transient

```text
error: no such file or directory
  .../Mathlib/Tactic/Linter/OverlappingInstances.olean
```

even though the file appeared after the competing job completed.  A separate
reviewer observed the analogous missing `.olean.server` sidecar before
`lake exe cache get` restored it.  These were cache-race failures, not theorem
failures.  The implemented lock closes the pipeline race.  Optional remaining
hardening is to make any manual `lake exe cache get` helper honor the same lock,
or to mount a completed dependency cache read-only in CI.

### F4 — B3: make the shared root-module description match its enlarged scope

`FormalLean.lean` imports all three encounter modules
(`FormalLean.lean:13-15`), but its opening comment still describes only the
original directed-shortcut PRR package (`FormalLean.lean:1-5`).  The package
README and encounter README now describe the shared scope correctly, including
`EncounterDesign.lean` and the formal boundary
(`code/formal_lean/README.md:55-85`; encounter report `README.md:95-108`).
Updating the root comment would remove the last small documentation mismatch.

## Reproduced declaration inventory

Textual declaration counting after nested-comment removal, driver coverage,
and the static integrity gate all agree:

| Module | Theorems | Definitions | What is actually certified |
|---|---:|---:|---|
| `Encounter.lean` | 14 | 8 | affine two-channel derivative/fold elimination; exact quadratic-kernel roots, gap, and slopes; scalar 2x2 inverse/Schur/denominator algebra |
| `EncounterContinuum.lean` | 28 | 13 | scalar affine/weighted-centre identities and diffusion coefficients; GIG log-profile stationary equation; capacity-power and fixed-chi 3D scaling; finite exponential-sum derivatives |
| `EncounterDesign.lean` | 12 | 4 | prescribed stationary action; symmetric-distance arithmetic map; positive normalized inverse-height weights and equal isolated weighted heights |
| legacy seven modules | 46 | not part of the encounter extension | the previously audited PRR algebra |
| **Total** | **100** | **25 new definitions** | **46 legacy + 54 encounter-specific theorems** |

The encounter split is independently visible from source anchors:

- `Encounter.lean`: 4 mixture/fold-elimination theorems
  (`:40-88`), 6 exact quadratic-kernel theorems (`:99-163`), and 4 scalar
  2x2/Green-system theorems (`:179-238`);
- `EncounterContinuum.lean`: 14 coordinate/diffusion identities
  (`:59-203`), 6 GIG stationary-equation statements (`:218-302`), 4
  capacity-scaling identities (`:311-344`), and 4 finite-exponential
  derivative statements (`:355-400`); and
- `EncounterDesign.lean`: 3 prescribed-action statements (`:37-56`), 4
  symmetric diffusion/distance identities (`:62-94`), and 5 inverse-height
  weight statements (`:111-162`).

All 25 definitions are transparent encodings.  Merely defining
`doiRadiusFactor`, `diffusiveActionFromSquaredDistances`,
`gigActionForMode`, or `inverseHeightWeight` is not a proof that the
corresponding continuum/Doi/large-deviation/mixture model is physically valid.
The proved theorems establish only the algebra following those definitions.

## Axiom and placeholder audit

The current source theorem order exactly matches the corresponding driver and
saved-report order:

| Driver/report | Source theorems | Driver rows | Saved rows | Result |
|---|---:|---:|---:|---|
| `AxiomsReport.lean` / `axioms_report_20260705.txt` | 46 | 46 | 46 | exact coverage |
| `EncounterAxioms.lean` / `encounter_axioms_report_20260711.txt` | 14 | 14 | 14 | exact coverage |
| `EncounterContinuumAxioms.lean` / `encounter_continuum_axioms_report_20260711.txt` | 28 | 28 | 28 | exact coverage |
| `EncounterDesignAxioms.lean` / `encounter_design_axioms_report_20260711.txt` | 12 | 12 | 12 | exact coverage |

Every saved row lists only `[propext, Classical.choice, Quot.sound]`.  Direct
source searches found no proof-term occurrence of `sorry`, `admit`,
`native_decide`, no `axiom` or `opaque` declaration, and no `unsafe`,
`implemented_by`, or external proof shortcut in any `FormalLean/*.lean`
module.  These three dependencies are Lean/mathlib's standard logical
dependencies, not project postulates.

## Statement-fidelity boundary

The following distinctions are essential and are correctly retained by the
current package:

| Encoded Lean result | Not proved by that result |
|---|---|
| Two-channel determinant, quotient weight, and converse | `0<w<1`, third-derivative nondegeneracy, unfolding transversality, or existence of a physical fold |
| Exact kernel `B x^2-A delta` roots and gap | Taylor-remainder control or an IFT/catastrophe reduction of the full density to that kernel |
| Scalar 2x2 system solve and denominator | Existence/regularity of a continuum Green operator, Bromwich inversion, operator domains, or a multi-target PDE theorem |
| Scalar relative/weighted-centre algebra | A vector-valued PDE change-of-variables theorem, transformed no-flux boundary regularity, or bounded-domain stochastic independence |
| GIG log-profile derivative and positive stationary root | Probability normalization, uniqueness/global maximality, a uniform channel approximation, or any CTMC/PDE error bound; at `b=0`, normalizability additionally requires the analytic tail condition outside Lean |
| Capacity power and defined fixed-chi Doi factor | The geometric capacity constant, 2D logarithmic capacity, derivation of the Doi factor, separated grid/radius limits, or continuum convergence |
| Finite exponential-sum derivatives | A complete spectral representation, exhaustive root isolation, exclusion of tangencies, or multimodal persistence |
| Prescribed GIG action and inverse-height weights | `2m-1` derivative roots, separated/nondegenerate mixture peaks, finite-patch realizability, or robustness under overlap/boundaries/discretization |

These limitations are stated directly in the three module headers
(`Encounter.lean:14-19`; `EncounterContinuum.lean:18-21`;
`EncounterDesign.lean:15-19`), in the formal README
(`code/formal_lean/README.md:64-85`), in the encounter README
(`README.md:95-108`), and in the manuscript (`:1593-1596`).

The theory-to-Lean bridge is also honest when read as a roadmap rather than a
completed-proof table.  D1-D12 distinguish finite algebra from PDE/operator
obligations and explicitly say that a successful Lean build does not verify
the PDE model, asymptotic remainder, numerical continuation, or continuum
convergence (`notes/continuum_multid_theory.md:1006-1028`).  Several rows (for
example D2 mass balance, D5 Doi/Robin matching, D9 cusp machinery, and D10
sign-preservation) are proposed bridges, not current Lean declarations; the
actual implemented coverage is the package README and inventory above.

## Reproduction commands and final build evidence

Toolchain and dependency lock:

```text
Lean 4.32.0-rc1 (commit b4812ae53...)
mathlib v4.32.0-rc1, commit 360da6fa66c1273b76b6b2d8c5666fd5ac2e3b56
```

Commands used or required for the final serial check:

```bash
cd /Users/ae23069/.local-build/valley-k-small/formal_lean
lake build
lake env lean AxiomsReport.lean
lake env lean EncounterAxioms.lean
lake env lean EncounterContinuumAxioms.lean
lake env lean EncounterDesignAxioms.lean

rg -n -i '\b(sorry|admit|native_decide)\b' FormalLean/*.lean
rg -n '^\s*(axiom|opaque|unsafe)\b' FormalLean/*.lean
```

The initial cold rebuild overlapped with cache restoration and another build.
It reached the `FormalLean` target but exited 1 because several mathlib output
files/sidecars transiently disappeared.  After the competing process ended, a
single warm rebuild completed successfully with `3109/3109` jobs.  I then
independently confirmed that all 18 relevant repository/local-copy Lean,
driver, manifest, and toolchain files were byte-identical and ran a separate
no-concurrency build:

```text
Build completed successfully (3109 jobs).
```

The only build diagnostic was a legacy, non-proof linter warning for an unused
variable `hv` in `FormalLean/HalfLine.lean:158`; there was no error and no
`sorry` warning.  My four subsequent live drivers all exited zero, and the
pipeline parser compared their results with the saved reports as follows:

| Live driver | Live rows | Parser errors | Saved semantic match |
|---|---:|---:|---|
| `AxiomsReport.lean` | 46 | 0 | yes |
| `EncounterAxioms.lean` | 14 | 0 | yes |
| `EncounterContinuumAxioms.lean` | 28 | 0 | yes |
| `EncounterDesignAxioms.lean` | 12 | 0 | yes |

The final source searches for `sorry`, `admit`, `native_decide`,
`axiom`, `opaque`, `unsafe`, `implemented_by`, `extern`, and `run_tac` were
empty.

## Final verdict

**PASS for the current formal layer.**  The byte-matched serial build and all
four live axiom drivers pass; the 100 = 46 + 54 count is reproducible; every
audited theorem is placeholder-free and has only standard Lean/mathlib logical
dependencies; and no scientific result is misrepresented as Lean-proved.  F1
was resolved during the audit.  F2 remains an explicit clean-commit
release/provenance gate, not a proof failure.  F3 is substantially resolved by
the new cache lock, and F4 is documentation polish.
