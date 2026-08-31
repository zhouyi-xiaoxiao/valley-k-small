# Round 05 reproducibility and artifact-integrity gate

Date: 2026-07-13  
Audit type: clean-room reproduction, artifact linkage, registry/layout, and
release-boundary audit  
Mutation policy: audit only; no source, manuscript, registry, or existing
artifact was modified by this round

## Executive verdict

**Round-05 reproducibility gate: FAIL CLOSED, with the numerical core partly
passing.**  Both report-owned numerical JSON files regenerate byte-for-byte in
a clean temporary copy when the repository virtual environment is used.  The
two supplied test modules each pass five tests, Ruff passes, the registry and
report layout validate, and the stored PDF hash agrees with its compile
manifest.  Those are real internal engineering successes.

The complete reproducibility gate nevertheless fails for two independent
reasons:

1. four of the five commands printed in `README.md` fail exactly as written on
   this machine because the selected `python3` has neither SciPy nor pytest;
   and
2. repeated clean manuscript builds produce different PDF SHA-256 values.  The
   PDF payload is otherwise identical: the only changed bytes are the random
   trailer `/ID`.  Thus the current compile record is internally linked to the
   checked-in PDF, but its byte-level hash is not reproducible.

There is also ignored runtime debris (`code/__pycache__/`) from mixed Python
3.12 and 3.14 runs, and the whole new report remains untracked while
`report_registry.yaml` is modified.  These are packaging/handoff issues, not
evidence that the two stored numerical calculations are wrong.

**Internal scientific milestone: FAIL CLOSED as currently labelled.**  G0 is
a reproducible reduced-family numerical milestone.  The G1a JSON is
reproducible as a deterministic self-consistency smoke, but Round 03 already
demonstrated physically wrong mutations that retain every current G1a gate,
and Round 04 therefore rejected the ledger's unqualified `G1a PASS`.  This
audit does not convert deterministic reproduction of a weak test into
scientific validation.

**Scientific PRR submission: FAIL CLOSED.**  The compile artifact correctly
sets `release_eligible: false`.  G1b, G2, G3, the constructive/remainder part of
G4, G5, author-confirmed metadata, and archival identifiers remain open.  A
clean PDF, reproducible reduced GIG fixture, or reproducible operator smoke is
not a PRR submission pass.

## 1. Gate matrix

| Gate | Result | Evidence |
|---|---|---|
| Stored GIG JSON integrity | **PASS** | All gates true; parameters agree with code constants; clean temporary regeneration has the same SHA-256. |
| Stored continuum-smoke JSON integrity | **PASS as self-consistency smoke only** | All twelve booleans true; parameters agree with code defaults; clean temporary regeneration has the same SHA-256.  Round-03 mutation failures still prohibit a project-level G1a pass. |
| Supplied pytest suites | **PASS under repository `.venv`** | `5 passed` for GIG and `5 passed` for continuum smoke in a temporary report copy. |
| Ruff | **PASS** | `ruff check` and `ruff format --check` pass for all five report-local Python files. |
| README commands as printed | **FAIL** | Four numerical/test commands fail under the machine's `python3`; only manuscript compilation succeeds. |
| Current PDF-to-manifest linkage | **PASS** | Stored PDF SHA equals `manuscript_compile.json:pdf_sha256`; metadata, fonts, and final-log gates pass. |
| Clean PDF byte reproducibility | **FAIL** | Two rebuilds give different SHA-256 values; only the trailer `/ID` differs. |
| Release hold | **PASS** | Compile JSON says `release_eligible: false` and names the open scientific/metadata blocker. |
| Report registry | **PASS** | Registry schema validates; report resolves; main TeX and all three registered entry scripts exist. |
| Report directory contract | **PASS** | Only the required directories plus optional `audits/` occur at report top level; no loose TeX/PDF is at the report root. |
| Auxiliary/runtime hygiene | **FAIL / cleanup required** | Five ignored `.pyc` files from two Python versions remain; the new report is not yet committed. |
| Internal milestone as currently advertised | **FAIL CLOSED** | G0 passes; G1a is only a reproducible scaffold/self-consistency smoke, not a discriminating project gate. |
| PRR submission | **FAIL CLOSED** | Required analytical, continuum, independent-validation, 3D, metadata, and archive gates are open. |

## 2. Numerical artifact audit

### 2.1 Reduced GIG construction

Stored artifact:
`artifacts/data/gig_constructive_pilot.json`

SHA-256:

```text
70318ebd6e895a0c5f63eb88294ada46abad191f2345e55101db295d5e34977b
```

A clean temporary regeneration using the repository virtual environment
produced exactly the same SHA-256.  The saved parameters match the code
constants:

- canonical reduced cusp: physical label `d=2`, `p=2.5`, `b=0.01`, isolated
  channel modes `(0.35, 1.0, 1.5)`;
- canonical cusp time:
  `0.5728883706366283`;
- weights:
  `(0.2769343322238388, 0.32005881414021176,
  0.40300685363594946)`;
- scaled fourth derivative:
  `-13.61053628261525`;
- row-angle sine:
  `0.9632674238749189`;
- raw dimensionless-matrix SVD ratio:
  `0.7478993752870627`;
- unfolding rank: `2`;
- independent Cauchy-versus-analytic derivative error:
  `1.3326532998187722e-13`, below the declared `2e-10` threshold;
- well-separated cases: `m=2,3,4,5,6`, all status `PASS`;
- maximum scaled root residual:
  `5.106975414370374e-09`, below `1e-07`;
- minimum curvature margin:
  `2.5199868714442872`, above `0.1`; and
- minimum peak-to-adjacent-valley ratio:
  `2.695647755849697`, above `1.5`.

The JSON's scope is correctly limited to normalized free-space GIG screening.
It explicitly excludes bounded-domain, finite-radius, continuum Doi/Robin, and
physical catalyst-realizability evidence.  Its finite sign-change scan is also
explicitly not an interval-exhaustive root proof.  The byte-reproduction pass
must retain those limitations.

### 2.2 G1a continuum operator smoke

Stored artifact:
`artifacts/data/continuum_g1_smoke.json`

SHA-256:

```text
c144b1c4c581f001ae532e40a43f4a9432d109507f800fa28341a2b4f32811dd
```

A clean temporary regeneration produced exactly the same SHA-256.  The JSON
parameters equal `PilotParameters()` and the `build_payload` defaults:

- grid: `25 x 25 x 25 = 15,625` states;
- `theta=0.5`, `time_stop=40.0`, `time_points=161`;
- diffusion `0.0045`, OU stiffness `0.1`, OU mean `0.95`;
- contact radius `0.16`;
- integrated budget `0.6`;
- expected and integrated contact area:
  `0.0804247719318987`;
- physical budget:
  `0.6000000000000001`, relative error
  `1.8503717077085943e-16`;
- free row-sum and killed mass-balance errors:
  `2.6922908347160046e-15`; and
- differential mass-balance error:
  `3.585657140951296e-16`.

All twelve stored booleans are true.  This proves that the current code and
current artifact agree and that the declared algebraic smoke checks are
deterministic.  It does **not** close Round-03 findings: translated contact
masks and cancelling patch-normalization errors can still emit `PASS`.
Consequently the supportable interpretation is
`SELF_CONSISTENCY_SMOKE_PASS`, not a physical continuum or project G1a pass.

## 3. README command audit

The five commands in `README.md` were run from the report root in a temporary
copy.  With the machine's default `python3`
(`/opt/homebrew/opt/python@3.14/bin/python3.14`), the exact results were:

```text
python3 code/validate_gig_constructive.py                 exit 1
  ModuleNotFoundError: No module named 'scipy'

python3 -m pytest -q code/test_gig_constructive.py        exit 1
  No module named pytest

python3 code/continuum_g1_smoke.py                        exit 1
  ModuleNotFoundError: No module named 'scipy'

python3 -m pytest -q code/test_continuum_g1_smoke.py      exit 1
  No module named pytest

python3 code/compile_manuscript.py                        exit 0
```

Using the repository-root environment instead gives:

```text
${REPO_ROOT}/.venv/bin/python: Python 3.12 environment
numpy 2.5.1
scipy 1.18.0
pytest 9.0.3

GIG tests:       5 passed in 2.32s
continuum tests: 5 passed in 0.79s
```

This is a README reproducibility failure, not a numerical-test failure.  The
README needs an explicit repository-root setup/activation step or commands
that use the supported `.venv/bin/python` path.  It should also name the
dependency installation/lock source so a new machine is not expected to guess
the environment.

There is a second documentation mismatch.  The sentence “The scripts write
only report-owned data under `artifacts/data/`” is false for
`compile_manuscript.py`: it also replaces
`manuscript/encounter_multimodal_prr.pdf` and writes two files under
`artifacts/logs/`.  All writes remain report-owned, but their destinations must
be stated accurately.

## 4. Tests and static checks

The clean temporary run used bytecode and pytest-cache suppression so it did
not contaminate the source tree:

```bash
PYTHONDONTWRITEBYTECODE=1 "${REPO_ROOT}/.venv/bin/python" -m pytest -q \
  -p no:cacheprovider code/test_gig_constructive.py

PYTHONDONTWRITEBYTECODE=1 "${REPO_ROOT}/.venv/bin/python" -m pytest -q \
  -p no:cacheprovider code/test_continuum_g1_smoke.py
```

Both suites passed five tests.  Ruff also passed on:

- `code/validate_gig_constructive.py`;
- `code/test_gig_constructive.py`;
- `code/continuum_g1_smoke.py`;
- `code/test_continuum_g1_smoke.py`; and
- `code/compile_manuscript.py`.

Results:

```text
ruff check:         All checks passed!
ruff format --check: 5 files already formatted
```

These results establish implementation consistency only.  In particular,
passing the current continuum unit tests does not override the mutation gaps
catalogued in Round 03.

## 5. Manuscript build and PDF integrity

The stored compile record has SHA-256:

```text
70ce6c5ffb6aca150bd49b77cac8c9ad40a46422574d279baf5af800ccfa25c3
```

It records:

- status `PASS` for working-draft build/PDF hygiene;
- `release_eligible: false`;
- blocker: scientific continuum gates and author-confirmed submission metadata
  remain open;
- 4 pages and 366,112 bytes;
- 31 embedded font rows, zero Type-3 rows, zero unembedded rows;
- zero final-log missing-file, overfull-box, undefined-citation, and
  undefined-reference counts; and
- a PDF SHA of
  `c530631f184473edb4af479015f281bc5bdfb610dea79b6a5c51e53cdf37f3c0`.

The current PDF has that exact SHA, so the stored pair is internally intact.
Its title, author, subject, keywords, page count, and font audit agree with the
compile JSON.  `manuscript_latexmk.log` contains expected transient
first-pass citation/reference warnings; the final TeX log is clean.

Byte-for-byte rebuild reproducibility fails:

| Build | PDF SHA-256 |
|---|---|
| stored PDF | `c530631f184473edb4af479015f281bc5bdfb610dea79b6a5c51e53cdf37f3c0` |
| clean temporary build 1 | `7fa87ac092a75960ecd7b178e0b30f32bcd955210bad5d23a480acb091740527` |
| repeat in the same temporary copy | `7d71c0d1426e8fb09feba6b11871ecf8f0b059368a79913fad2ac99a06b02f7f` |

The files have equal length.  Comparing the stored PDF with the repeat build
finds 62 changed bytes, all within the trailer `/ID` field.  Replacing only
that field by a fixed token makes the PDF bytes identical, with normalized
SHA-256:

```text
6ae4b7c88b3fad148054e6161b434cb0d8cee4ee063339efbe8fba8526472780
```

Thus the rendered document is deterministic, but the cryptographic artifact
is not.  `SOURCE_DATE_EPOCH` fixes timestamps but not the trailer ID.  The
compiler must set or post-process a deterministic PDF identifier, followed by
two independent exact-SHA builds.  Until then, the stored `pdf_sha256` is a
valid snapshot-integrity checksum, not a reproducible-build checksum.

## 6. Registry and directory-contract audit

The following repository checks pass:

```text
python3 scripts/reportctl.py validate-registry
  OK: report registry is valid

python3 scripts/reportctl.py check-docs-paths
  OK: documentation paths are valid

python3 scripts/reportctl.py validate-science-rules
  OK: scientific guardrails are wired into agent docs and CLI checks
```

`report_registry.yaml` contains one active `encounter_multimodal_prr` entry
with:

- path `research/reports/encounter_multimodal_prr`;
- manuscript directory `manuscript`;
- artifact directory `artifacts`;
- main TeX `encounter_multimodal_prr.tex`; and
- entry scripts for GIG validation, continuum smoke, and manuscript compile.

All referenced paths exist, and `reportctl resolve --report
encounter_multimodal_prr` resolves correctly.  The entry scripts are invoked
through Python and therefore need not have executable bits.

The report root contains only:

```text
README.md
artifacts/
audits/
code/
manuscript/
notes/
```

This satisfies the required four-directory contract plus the permitted
publication-report `audits/` directory.  No report-root TeX/PDF, symlink,
`.DS_Store`, `.tmp`, `.pytest_cache`, `.ruff_cache`, or loose LaTeX auxiliary
file was found.

## 7. Untracked and auxiliary-artifact audit

The standard Apple `/usr/bin/git` is blocked on this machine by the unaccepted
Xcode license, so status was independently read with the bundled fallback Git.
At the audit snapshot:

- `research/reports/report_registry.yaml` is modified;
- before adding this Round-05 record, 19 report files were untracked; and
- the report therefore has not yet crossed a reviewable commit boundary.

The new report being untracked is expected during construction, but a release
or collaborator handoff must intentionally include the registry entry, source,
tests, notes, audits, numerical JSON, manuscript sources, and selected PDF.
It must not silently omit ignored evidence or accidentally include runtime
state.

Ignored auxiliary state found under the report:

```text
code/__pycache__/                                  184 KiB
  continuum_g1_smoke.cpython-312.pyc
  continuum_g1_smoke.cpython-314.pyc
  test_continuum_g1_smoke.cpython-312-pytest-9.0.3.pyc
  test_gig_constructive.cpython-312-pytest-9.0.3.pyc
  validate_gig_constructive.cpython-312.pyc

artifacts/logs/                                     68 KiB
  manuscript_latexmk.log
  manuscript_tex.log
```

The two logs have current build timestamps and are not stale TeX auxiliary
files.  They are ignored by the repository's generic `*.log` rule, so a clean
clone will regenerate rather than receive them.  The mixed-version bytecode is
pure runtime debris and must be removed before handoff; it also explains why
future audit commands should use `PYTHONDONTWRITEBYTECODE=1`.

## 8. Required closure order

1. Make the README commands executable on a clean machine: declare the
   supported Python environment and dependency installation/lock source, and
   use that interpreter consistently.
2. Correct the README output-location statement for the PDF and build logs.
3. Make the PDF trailer ID deterministic and require two clean builds with
   identical full-file SHA-256 values.
4. Remove `code/__pycache__/`; keep test/cache suppression in audit commands.
5. Add an intentional artifact manifest or release ledger containing the two
   JSON hashes, PDF hash, source/environment identity, and claim scope.
6. Stage and review the complete report plus registry change as one deliberate
   handoff boundary.
7. Independently of reproducibility, close the Round-03 G1 mutation gaps and
   Round-04 budget/evidence-label conflict before restoring any internal G1a
   project-gate pass.
8. Keep `release_eligible: false` until G1b, G2 where a cusp is claimed, G3,
   G4, G5, metadata, overlap, and archive gates have actually passed.

## Final binary decisions

- **G0 reduced numerical artifact:** **PASS**, within its stated reduced-only
  and finite-scan scope.
- **G1a artifact regeneration:** **PASS as deterministic self-consistency
  smoke only**; **FAIL** as a discriminating physical/project gate.
- **Current stored PDF/manifest linkage:** **PASS**.
- **Clean-room report reproduction:** **FAIL CLOSED** until README environment
  and deterministic-PDF issues are repaired.
- **Internal milestone as currently labelled:** **FAIL CLOSED**.
- **Scientific PRR submission:** **FAIL CLOSED**.
