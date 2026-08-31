# Round 53: supplement release-closure audit

Date: 2026-07-14 (Europe/London)

## Scope

This is a narrow, read-only closure check of the Round 52 supplement source
against the two release-P1 and two P2 findings from Round 49.  It does not
re-open the full mathematical proof audit.  No source, main-manuscript,
positive-budget producer/auditor/manifest, result, or evidence file was
modified.

Target source:

```text
manuscript/encounter_multimodal_prr_supplement.tex
SHA-256 1d7631faaeff3c6688cee8e138c5f92e3efcd180268ce5f1125bb01f23e1face
```

The observed SHA exactly matches the requested Round 52 anchor.

## Closure verdict

- **P0: 0 open.**
- **P1: 0 open.**  Both Round 49 release-P1 findings are closed.
- **P2: 0 open.**  Both Round 49 P2 findings are closed.
- **Analytical-supplement release closure: PASS**, subject to the already
  stated theorem scope.
- **Overall numerical PRR release: HOLD.**  This closure does not supply or
  validate a finite-parameter positive-budget topology, cusp, event-mass
  floor, mesh convergence, or independent-solver result.

## Round 49 finding-by-finding closure

| Round 49 item | Round 53 evidence | Status |
|---|---|---|
| P1-1: “mode count is realized” could imply globally exactly m modes | Abstract lines 65--69 now say that for each fixed finite m the m-dependent family has **at least m** nondegenerate local maxima.  The theorem title at line 982 is “At least m modes for every prescribed fixed finite m”; lines 998--1002 retain the named-interval statement and “No exact global root count is asserted.” | CLOSED |
| P1-2: Lean paths/hashes were not self-contained | Lines 1128--1138 now give the exact repository-relative directory and all three SHA-256 anchors.  Every path resolves from the repository root and every recomputed hash matches. | CLOSED |
| P2-1: Section S4 did not explicitly identify the generic diffusion parameter | Lines 695--698 now state `D = epsilon^2 D_0` and connect it to both midpoint and relative-coordinate noise amplitudes. | CLOSED |
| P2-2: formal-boundary table floated behind the bibliography | The source uses `[t]`; visual inspection shows the table at the top of page 12, followed by Section S6 and then the bibliography.  It no longer appears after the references or leaves the former detached-table layout. | CLOSED |

## Lean path and hash re-computation

Repository root used for resolution:

```text
/Users/ae23069/Library/CloudStorage/OneDrive-UniversityofBristol/Desktop/valley-k-small
```

All three source files exist at the displayed directory and re-hash as:

```text
research/reports/ring_lazy_jump_ext_rev2/code/formal_lean/FormalLean/Encounter.lean
d2c11759c831228eb6641f3944d1d860c34615982d15b883e6d029f0a670e754

research/reports/ring_lazy_jump_ext_rev2/code/formal_lean/FormalLean/EncounterDesign.lean
fa45ceb3c40e7c9769d4f7d6ab5aa1495e89a361c675b89f362dfc11798b8330

research/reports/ring_lazy_jump_ext_rev2/code/formal_lean/FormalLean/EncounterContinuum.lean
ae23060be3166c392eab2d8a0a5af5dcd1d3a4adf2a8b912fd8a0c2161e538b4
```

These are byte-for-byte identical to the hashes printed in the supplement.
The accompanying text remains conservative: the files certify finite
algebraic fragments only, and a successful axiom report is explicitly denied
as evidence for either analytical theorem.

## Independent clean build and visual check

The source was compiled into a newly created empty temporary directory using
TeX Live 2025 through `latexmk`:

```text
exit code: 0
pages: 12
PDF SHA-256: 6a7e94c0acba01f679bb351c0bf0353e6d93a460305f9e1d2378faff4b8d2be0
undefined references/citations: 0
overfull/underfull boxes: 0
```

The only log warnings are the RevTeX default 10-point-size notice and the
standard `nameref` label-definition notice.

Visual inspection of pages 11--12 confirms:

- page 11 contains the event-mass limitation, the m-dependent-geometry
  limitation, and the formal-verification boundary;
- the repository-relative Lean path and all three hashes are legible;
- page 12 starts with the analytical-evidence table;
- Section S6 and the bibliography follow the table in reading order;
- the old post-bibliography table displacement is gone;
- there is no clipping, collision, or unreadable formula/table text.

## Over-claim regression scan

A source and rendered-text scan found no positive claim of global exactly-m
modality and no positive claim that the analytical theorems are Lean-verified.
The remaining occurrences are correctly negative or scoped:

- at least m certified local maxima are claimed;
- exactly one maximum is claimed only inside each named certified interval;
- no exact global root count is asserted;
- one fixed geometry is explicitly not claimed to realize arbitrary m;
- the proofs are called conventional human-audited proofs and explicitly “not
  Lean-verified”;
- “Lean verified” and “formally verified” are declared inadmissible labels;
- finite-parameter cusp, event-mass floor, and solver convergence remain in the
  “not claimed” row and numerical-evidence placeholder.

No claim regression was introduced by the Round 52 repair.

## Release boundary

Round 53 closes the four Round 49 supplement defects.  The admissible theorem
headline remains:

> For every fixed finite m, an m-dependent narrow-noise slab family has at
> least m certified local maxima for sufficiently small epsilon and, after
> fixing epsilon, sufficiently small positive reaction budget B, under the
> displayed hypotheses.

This closure does not establish globally exactly m modes, a single geometry
for arbitrary m, a practical finite B, a positive event-mass floor, a physical
cusp, discretization convergence, or independent numerical confirmation.
Consequently the analytical supplement itself passes this release-closure
gate, while the **overall numerical PRR release remains HOLD** pending its
separate frozen evidence chain and independent audit.
