# Round 160: theorem-first status correction and environment rebaseline

Date: 2026-07-14

Decision: **STATUS-PROSE CORRECTION PASS / ROUND-149 MATHEMATICAL CORE
UNCHANGED / LOCAL DIRECT ENVIRONMENT REPRODUCIBLE / CLEAN EXTERNAL INSTALL OPEN /
HOLD F0 / NO F1 / HOLD PRR**

Severity within this round's editorial and local-environment scope:
**P0 = 0, P1 = 0, P2 = 2**.

## 1. Trigger and scope

An independent editorial read found that the Supplemental wrapper still said a
hash-specific audit was required even though the same integrated mathematical
package had already passed Round 149 with `P0=P1=P2=0`.  The stale sentence was
a status-reporting contradiction, not a defect in the exact-`m` proof.

This round changed only the two status statements in the Supplemental wrapper,
added a human-facing pointer that distinguishes the active theorem-first files
from the archived 13-page working set, and recorded the exact direct Python
environment used by the report.  It did not change the reader theorem spine,
the complete proof, the theorem-first main text, the bibliography, or the
compiler.  It did not evaluate any positive budget, prospective control,
F1/F2/F3 row, production-size state space, or continuum result.

## 2. Preserved Round-149 mathematical bytes

| Object | SHA-256 |
| --- | --- |
| `manuscript/encounter_multimodal_prr_theorem_first_working.tex` | `6e7393e44bb1da9bb196b839534fdf43e18dd90d0829d941ad7e155f4afcbc67` |
| `manuscript/exact_m_theorem_spine.tex` | `79b0a4467a67999f605b8a5d8ec07e41a88c07edc8cdf1639ad6b8d4ce70658e` |
| `manuscript/exact_m_theorem_full_proof.tex` | `a372b5a33d2203b8f3214a153f4aaf1e81497bf146c0ac1db1cfda97919c1c7b` |
| `manuscript/references.bib` | `2f90b6735993c6d2fa8bb8f1a6c35c334706d02585361d4ee9238ac020ce9c76` |
| `code/compile_theorem_first_working.py` | `15098db6e731e23a31967077b79ace723849b5e8383169bb497fa57f9b92725e` |

Round 149 remains the mathematical authority for these bytes.  This round does
not claim to repeat or widen that proof audit.

## 3. Corrected wrapper and rebuilt outputs

The wrapper now states that the frozen mathematical migration passed Round 149
while the finite-parameter F0--F3, strict-continuum, overlap, metadata, and
release gates remain open.  It no longer says that the already completed audit
is still required.

| Object | SHA-256 |
| --- | --- |
| `manuscript/encounter_multimodal_prr_supplement.tex` | `f89135e25b35cff16a5e7d39305b94f3615f776f9d2322dc2dc5d90bde64c183` |
| main PDF | `c766de16ca3a70eda63397d4d78ccb9f44415982afa4d4b6e0a295197488984b` |
| Supplemental PDF | `3831626dd565aa21abd32c407db609125737f5a3de130e1e0f853bcb2f202ae2` |
| `artifacts/data/theorem_first_working_compile.json` | `b3923de0615fbe2e6399aa9196a92b86f10331ceb80da38d8a182a4d41b9bef0` |
| `manuscript/README.md` | `b426ecd016c4487c531cd1ab2b47a088c6745148091da596fce45e81e72dd6d0` |

The report-owned compiler again performed two isolated builds of each document.
The main PDF remained byte-identical to the Round-149 output.  The expected
Supplemental PDF change is attributable to the corrected status prose.  The
manifest reports five main pages, twenty Supplemental pages, embedded fonts,
zero Type-3 fonts, zero overfull boxes, and no unresolved references or
citations.  All 25 pages were rendered; the corrected page 20 is readable and
has no clipping or overlap.

## 4. Direct environment baseline

The current local numerical baseline is CPython 3.12.13 with NumPy 2.5.1,
SciPy 1.18.0, Matplotlib 3.11.0, pytest 9.0.3, and gmpy2 2.2.1.  Before this
round, `gmpy2` was required by the directed MPFR bounds but was absent from the
repository dependency declarations.  The report now owns:

| Object | SHA-256 |
| --- | --- |
| `code/check_reproducibility_environment.py` | `c592a78ed0f2ac07afde518d8fb2426f1f14a93f034e784d73b291dfeaf90fe1` |
| `code/requirements-reproducibility.txt` | `373f9cc7f054a4ffd858a463ec5da50666e1c0a3d2607202f5b05c202c94774e` |
| `code/test_check_reproducibility_environment.py` | `091d1f2ca4a02aa9940f7a685d15cb502af9f49a123c7c7474f7db1fab104f59` |
| `notes/reproducibility_environment.md` | `a203bccef6f329afbdac258356f94b438aa547fa9cec7cff7b7c73fe9ffa4941` |

The environment check passed without executing science.  The direct-version
file is not a transitive wheel/hash lock, and a clean installation was not run
because this continuation deliberately used no network.  That boundary is P2
for the present internal working set and remains a release blocker.

## 5. Commands and observed results

From the repository root:

```text
.venv/bin/python research/reports/encounter_multimodal_prr/code/compile_theorem_first_working.py
  PASS; main c766de16...; supplement 3831626d...

.venv/bin/python research/reports/encounter_multimodal_prr/code/check_reproducibility_environment.py
  PASS; match=true; science_executed=false

.venv/bin/python -m pytest -q \
  code/test_check_reproducibility_environment.py \
  code/test_round149_exact_m_hash_freeze.py \
  code/test_compile_theorem_first_working.py \
  code/test_theorem_first_scope_consistency.py \
  code/test_general_dimension_scope_consistency.py \
  code/test_living_scope_consistency.py \
  code/test_text_control_character_hygiene.py
  PASS; 33 tests
```

The abbreviated `code/...` paths above are relative to the report directory;
the executed commands used full report-relative paths from the repository root.

## 6. Remaining findings

### P2-160-1: no clean external environment replay

The current machine matches the recorded direct baseline, but no from-zero
installation and focused-suite replay has been performed on a clean environment
or second platform.  Do not describe the package as externally reproduced.

### P2-160-2: submission identity and overlap remain open

The predecessor identifiers, author-approved overlap disclosure, submission
metadata, and canonical upload manifest remain incomplete.  The new
`manuscript/README.md` prevents accidental use of the archived PDF but does not
close those author/editor gates.

## 7. Final boundary

The active 5+20-page package is a clean, internally reproducible working set.
The exact-`m` mathematical migration remains accepted only at the Round-149
scope.  No finite practical budget, same-support mode switching, event-mass
floor, strict continuum result, F0/F1/F2/F3 pass, or PRR release follows from
this round.
