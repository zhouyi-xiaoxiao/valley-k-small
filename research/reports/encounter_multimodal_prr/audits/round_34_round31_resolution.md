# Round 34 resolution of the Round 31 integrated numerical attack

Resolution snapshot: 2026-07-13T21:31:00Z  
Parent finding: `audits/round_31_integrated_numerical_attack.md`  
Scope: numerical-source closure, manuscript-build failure atomicity, observable-
figure semantics, recoverable manuscript literals, and common time units.

## Verdict

**All one P1 and three P2 findings in Round 31 are closed.**  The repaired
publication-evidence gate is **PASS**, with **P0 = 0, P1 = 0, P2 = 0** in this
resolution scope.  This is not a scientific-promotion verdict: the manuscript
compile manifest still has `release_eligible=false`, and the independent-solver,
continuum/box, and any still-open positive-budget promotion gates remain separate.

The positive-B frozen chain was not modified.  Its current manifest contains 13
pins, all 13 observed hashes match, and its manifest SHA-256 at this snapshot is
`128f9663b688993fab67a2c73d9bfd4c53997bd08a5f110a969eebb1af587a8a`.

## Finding-by-finding closure

| Round 31 finding | Repair | Verification | Status |
|---|---|---|---:|
| P1: macro sources not fully fail-closed | Added one hard-pinned release source manifest covering the five current result families and 38 role pins. The builder verifies every result, manifest, producer, test, protocol, and declared dependency before reading values for macros. | Current closure passes; mutations of d2 result, broad result, broad producer, and broad FV dependency are rejected. | **CLOSED** |
| P1: G1d did not close over current G1c | Builder checks the G1d result and manifest pins against the current G1c result and manifest hashes, as well as the release manifest's duplicate dependency pins. | An isolated G1c mutation was deliberately re-pinned in the outer release manifest; verification still rejected it at the unchanged nested G1d-to-G1c hash. | **CLOSED** |
| P1: failed late pin check left mixed canonical outputs | Compiler now finishes numerical and figure preflight before any canonical write, builds from a temporary report snapshot, verifies two deterministic builds and PDF gates there, rechecks source provenance to close the TOCTOU window, and only then publishes five outputs through same-directory atomic replacements with backups and rollback. | Injected failure on the second replace restored every previous byte and removed a newly introduced target. Injected numerical-preflight failure left all five output sentinels unchanged. | **CLOSED** |
| P2: observable figure used `F` for the zero-budget object | Observable figure now uses `G_{w_*}(t)` and describes the ordinate as a free-exposure response. Its publication metadata uses `relative_shape_gate_passed=true`, `event_mass_observability_verified=false`, and `independent_PDE_solver_verified=false` without rewriting frozen result flags. | Figure replay and tests pass; vector PDF/PNG/metadata are byte-identical across two replays and were inspected visually. | **CLOSED** |
| P2: independent root discrepancy was not in canonical JSON | The unpinned literal `1.1e-12` was removed from the manuscript. The sentence now reports the canonical primary/fine root-time discrepancy through generated macro `\FourPatchRootDifference`. The frozen d2 producer and result were deliberately not rewritten. | Generated macro is source-manifest pinned; manuscript compiles with zero forbidden warnings. | **CLOSED** |
| P2: note rounded dependent-weight spread incorrectly | Result note now says `1.05e-14`, explicitly including the dependent fourth weight. | Direct comparison with the canonical convergence rows. | **CLOSED** |
| P2: figures disagreed on time units | Both figures now label the shared coordinate `dimensionless time t`; both manuscript captions say the same. | Replayed figures and focused figure tests pass. | **CLOSED** |

## Numerical-source closure

`artifacts/data/manuscript_numerical_sources_manifest.json` has SHA-256
`6ea29628e1cba423d37588b72a78dd3f5934f5e77b9c83df70394739375c88e7`.
That hash is compiled into `build_manuscript_inputs.py`; editing the manifest is
therefore itself rejected unless the release closure is deliberately refrozen.
The manifest contains exactly these five result families:

1. physical-d2 exact disk-kernel four-slab result;
2. physical-d3 exact sphere-kernel four-slab result;
3. G1c simplex candidate result and its G1a/G1b/manual-review dependencies;
4. G1d finite-grid fold result and its G1c/topology-review dependencies; and
5. broad-patch B=0 bridge result and all six pins already frozen by its manifest.

The verifier rejects absolute paths, report-root escapes, missing paths, malformed
SHA-256 values, extra/missing families, and any observed hash mismatch.  It also
reconciles the heterogeneous nested provenance layouts rather than treating the
outer release manifest as sufficient:

- d2/d3 result provenance against each frozen manifest's file records;
- d3 against its d2 base dependency;
- G1c result and manifest against all three input result/producer pairs;
- G1d result and manifest against current G1c result/manifest, runner, protocol,
  and topology review; and
- broad result `manifest_sha256` and `pinned_file_hashes` against the broad
  manifest and current files.

The generated TeX input now carries the release-manifest receipt plus all five
result hashes.  Current input SHA-256 is
`62fe4306fc1bfa6a75757031ba23de38f9fabe490ac7be8c0b05e14c543a1530`.

## Transaction and failure-atomicity model

The canonical output set is:

1. `manuscript/inputs/numerical_results.tex`;
2. `manuscript/encounter_multimodal_prr.pdf`;
3. `artifacts/logs/manuscript_tex.log`;
4. `artifacts/logs/manuscript_latexmk.log`; and
5. `artifacts/data/manuscript_compile.json`.

Before any of these paths is touched, the compiler validates the numerical source
manifest and all nested pins, TeX and bibliography, every included figure PDF,
every figure metadata object, and every recursively nested figure source pin.  It
then creates a temporary report-shaped source tree containing the staged numerical
input and checked figures.  Both LaTeX replicas are built from that snapshot.  PDF
metadata, fonts, warnings, and byte identity are checked on temporary outputs.
Immediately before publication, numerical, figure, TeX, and bibliography
provenance are re-read and required to equal their preflight snapshots.

Publication prepares fsynced incoming files and fsynced backups in each target's
own directory, applies `os.replace` to the complete checked set, fsyncs the touched
directories, and removes backups only after success.  Because POSIX does not offer
one cross-directory rename transaction, visibility is sequential for a very short
replace window; the implemented guarantee is **failure atomicity**: any exception
rolls every already-replaced target back to its prior bytes and removes targets
that did not previously exist.  The mutation test attacks exactly that boundary.

## Mutation and replay evidence

Focused suite:

```text
21 passed
Ruff lint: PASS
Ruff format check: PASS (7 files already formatted)
```

Mutation cases exercised in isolated temporary trees:

| Attack | Expected | Observed |
|---|---:|---:|
| Append a byte to included d2 result | reject before output write | rejected on release hash |
| Append a byte to broad result | reject before output write | rejected on release hash |
| Mutate broad producer | reject | rejected on release hash |
| Mutate broad finite-volume dependency | reject | rejected on release hash |
| Mutate G1c, then update both outer G1c pins | nested G1d closure still rejects | rejected on G1d-to-G1c hash |
| Builder preflight throws with existing output sentinel | output unchanged | exact old bytes retained |
| Compiler numerical preflight throws with five sentinels | all outputs unchanged | exact old bytes retained |
| Second publication replace throws after first succeeded | rollback complete | old bytes restored; absent third target remains absent; no incoming/backup debris |

The two observable figure bundles were rendered twice after the notation/time-unit
repairs; all six files were byte-identical.  Current key hashes are:

| Artifact | SHA-256 |
|---|---|
| observable PDF | `703241a81e8c8be7d22d58aeacd68fd0b8d8953b3c69589213a826d87ee1128f` |
| observable metadata | `881ce1e3809466821226b32ff71cf5bd71b583dc3df399b670586ffab7ff57fe` |
| d2/d3 PDF | `1581aac239e77f17a837d24bd9b38a0fb4ef3eb2286bea3ee7889b446d0c5b0f` |
| d2/d3 metadata | `67d923386dafc1b01b4430f6ee369b4bdff660d6a626ade8c780ccae0234f8c7` |

## Manuscript build evidence

The specialized compiler produced two byte-identical clean PDFs:

```text
PDF SHA-256 pair:
13986921d2f8c5f478845bfd1abeaa9161e173d0b8030430757b9f65694ab94b
13986921d2f8c5f478845bfd1abeaa9161e173d0b8030430757b9f65694ab94b
pages: 12
missing files: 0
overfull boxes: 0
undefined references: 0
undefined citations: 0
font rows: 42
Type 3 fonts: 0
unembedded fonts: 0
```

The independent TeX Live skill compile also exited zero in a separate temporary
output directory.  The canonical compile manifest SHA-256 is
`2c6ba511c1665d000d59873c23b54a720be0e66f5d93832bcc12182b2c552820`.

## Scope boundary

This repair proves that the current five-family numerical-to-manuscript chain is
closed and that failed builds do not leave a mixed canonical output set.  It does
not make a frozen numerical result more general, turn B=0 relative shape into
positive event-mass observability, provide an independent PDE solver, or pass the
PRR scientific release gate.  If a positive-B result is later promoted into
manuscript macros, it must be added as a deliberate sixth family and the hard-
pinned release manifest must be refrozen and mutation-tested again.
