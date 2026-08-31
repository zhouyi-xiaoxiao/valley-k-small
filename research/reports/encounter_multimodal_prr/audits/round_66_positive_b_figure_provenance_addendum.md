# Round 66: positive-budget figure provenance addendum

Date: 2026-07-14  
Role: compiler-compatible sidecar closure and paired-publication fault audit  
Verdict: **PASS-FIGURE-PROVENANCE / READY-FOR-COMPILER-INCLUSION / HOLD-PRR-PROJECT**

## 1. Scope and protected-file boundary

This round adds a deterministic provenance sidecar to the Round-63
positive-`B` fixed-control figure. It does not change the scientific figure,
canonical result, reproducibility evidence, independent audit, manifest, any
pinned producer/auditor file, the existing multi-family figure builders, the
manuscript compiler, the main manuscript, or a README.

No producer, semigroup, finite-volume solver, or canonical auditor was run.

The protected canonical hashes remain:

| Role | SHA-256 |
|---|---|
| manifest | `955e59bf333b5fd70e415a53dc26becae9c7a34c5d40f1230c96b1dab8f5677c` |
| result | `51e8eb4bdb652124865d0c39e6f36b99d13ed61578b161e0f75b142cada49401` |
| two-process evidence | `6c0eccaae09ef95923843ddd7a141a27311e1575ee68d3301b4757b785ee9890` |
| independent audit | `60c541a6f0decd5431cefa5c203311176e61006586ce69043d5fcf5380ed517d` |

## 2. Compiler provenance contract

The existing `compile_manuscript._figure_provenance` implementation requires:

1. a sidecar named `<figure_stem>_metadata.json` beside the included figure;
2. top-level `outputs.pdf_sha256` equal to the current PDF bytes;
3. a nonempty top-level `source_pins` mapping; and
4. for every source role, a report-relative path plus a matching `<role>_sha256`.

The new sidecar satisfies that contract without changing the compiler.
Independent invocation of `_figure_provenance` on a synthetic include of this
figure returned:

```text
figure_sha256=3904dbdddd50f7efc1bd66ed5b2274025b08c79bdd044a1efbdfb5a45156fe09
metadata_sha256=caa9753debbd3802dda29d03495d04a117d8d2ada47ef16b3fd0506d82ada56d
verified_roles=canonical_result,independent_audit,plotter,reproducibility_evidence,test
```

## 3. Sidecar schema and non-self-referential pin design

Added output:

`artifacts/figures/positive_b_broad_four_slab_metadata.json`  
SHA-256: `caa9753debbd3802dda29d03495d04a117d8d2ada47ef16b3fd0506d82ada56d`  
Size: `5,616` bytes

The sidecar is canonical `json.dumps(..., indent=2, sort_keys=True,
allow_nan=False, ensure_ascii=True)` output with one terminal newline. It has no
generation time, random identifier, working directory, temporary path, or
runtime output path.

Its top-level contract includes:

- `outputs.pdf`, `outputs.pdf_sha256`, and `outputs.pdf_bytes`;
- compiler-verifiable `source_pins` for the canonical result, reproducibility
  evidence, independent audit, plotter, and plotter test;
- exact evidence timing and canonical claim scope;
- the eight false promotion flags for preregistration, allocation cusp,
  interval/continuum, unbounded finite-volume limit, independent solver,
  physical `d=3`, project gate, and publication gate;
- explicit positive scope constraints: one fixed reflected box, two held-out
  odd meshes `[113,129]`, the same solver family only, unchanged weights,
  `B=0.01`, saved trace through `t=35`, and finite gate time `t=100`;
- the analytical question, bounded takeaway, panel descriptions, palette and
  non-colour distinctions;
- exact plotted root times and basin masses; and
- deterministic renderer and vector-PDF QA fields.

### Self-pin handling

The plotter does **not** contain a hard-coded hash of itself or its test. At
runtime it opens both as regular nonsymlink files, computes their current SHA,
writes those values into the sidecar, and verifies them again immediately before
the paired publication. The metadata does not contain its own SHA. This avoids
both a source self-hash cycle and a metadata self-hash cycle while allowing the
compiler to verify the resulting source chain.

The sidecar currently pins:

```text
plotter_sha256 = 95af097547ab3a40b38bd779d493f1898297b40e7c3899a73a971e3ae3be4999
test_sha256    = 8d53ec95a85f8ae865ae4e1c067d61b8d130dfcfa28a54660a1ad1df2ae6572f
```

## 4. Paired atomic publication and rollback

Updated source:

`code/plot_positive_b_broad_four_slab.py`  
SHA-256: `95af097547ab3a40b38bd779d493f1898297b40e7c3899a73a971e3ae3be4999`

The build now completes these steps before any canonical output changes:

1. hard-pin and semantically validate the three canonical JSON inputs;
2. render the PDF completely in memory;
3. verify PDF completeness, font type, transparency, and raster-XObject gates;
4. build and validate the sidecar in memory;
5. serialize canonical sorted JSON;
6. recheck all scientific inputs plus plotter/test source pins; and
7. prepare both same-directory incoming files and both prior-output backups.

It then replaces the PDF and metadata as one ordered transaction, verifies the
published bytes, and fsyncs the output directory. If either replace, byte check,
or directory fsync fails, every already-published target is restored in reverse
order. Existing file modes are also retained by rollback backups.

The transaction registers a target before invoking `replace`, so a pathological
`replace-then-raise` fault remains inside the rollback set.

## 5. Test expansion and attacks

Updated test:

`code/test_plot_positive_b_broad_four_slab.py`  
SHA-256: `8d53ec95a85f8ae865ae4e1c067d61b8d130dfcfa28a54660a1ad1df2ae6572f`

All original 12 Round-63 tests remain. The suite now contains 21 tests,
including new attacks for:

1. canonical sorted metadata and absence of volatile paths/timestamps;
2. mutated `outputs.pdf_sha256`;
3. mutated plotter source pin;
4. metadata-validation failure preserving both prior PDF and prior metadata;
5. injected failure on the second paired replace, with complete rollback;
6. injected directory-fsync failure after both replaces, with complete
   rollback;
7. two complete paired builds having identical PDF and metadata bytes;
8. committed metadata exactly matching a fresh in-memory payload; and
9. direct compatibility with `compile_manuscript._figure_provenance`, including
   all five verified source roles.

Validation results:

```text
py_compile: PASS
Ruff: All checks passed
plotter/provenance pytest: 21 passed
compile-manuscript tests excluding the known live stale-manifest assertion: 4 passed
validate-science-rules: PASS
```

## 6. Double-run deterministic closure

Two separate CLI processes wrote two distinct temporary PDF/metadata pairs.
Both temporary pairs and the canonical pair had exactly these hashes and sizes:

```text
PDF SHA-256      3904dbdddd50f7efc1bd66ed5b2274025b08c79bdd044a1efbdfb5a45156fe09
PDF bytes        98,227
metadata SHA-256 caa9753debbd3802dda29d03495d04a117d8d2ada47ef16b3fd0506d82ada56d
metadata bytes   5,616
```

Both PDF comparisons and both metadata comparisons passed byte-for-byte `cmp`.

The PDF SHA is exactly the Round-63 SHA. Therefore the sidecar work caused no
figure-content, figure-metadata, layout, font, or rendering change. The existing
Round-63 two-pass rendered-page QA remains applicable.

## 7. External shared-worktree state

An exploratory run of the entire `test_compile_manuscript.py` file encountered
one unrelated assertion: the existing `manuscript_compile.json` still recorded
TeX SHA `f3bf7cb11b7657bc65cdcbb3b9f7fcc15e3b799c072177d2daaeb738401c89ed`,
while the concurrently edited live manuscript had SHA
`a4842808c66c4f9813c024324ca38d18f6406a9db127742093a63edc6fb6613b`
at that instant. The root manuscript task confirmed this stale compile manifest
was expected while it was updating the manuscript.

This round did not repair or suppress that external state because changing the
manuscript, compiler, or compile manifest was explicitly outside scope. The four
other compiler tests passed, and direct provenance parsing of the new figure and
sidecar passed.

## 8. Final decision

```text
Sidecar schema: PASS
PDF hash closure: PASS
Five source pins: PASS
Negative claim boundary: PASS
Fixed-box/same-solver/finite-window scope: PASS
Canonical sorted JSON: PASS
No timestamp or temporary path: PASS
Paired atomic publish: PASS
Second-replace rollback attack: PASS
Directory-fsync rollback attack: PASS
Double-run PDF bytes: PASS
Double-run metadata bytes: PASS
Compiler provenance parser: PASS
Figure scientific/layout content changed: NO
Ready for later manuscript inclusion: YES
Overall PRR project: HOLD
```

This closes figure provenance only. It does not authorize a stronger scientific
claim or close allocation-cusp, continuum/box/parity, independent-solver, or
physical-`d=3` gates.
