# Round 68: positive-budget main-integration independent attack

Date: 2026-07-14  
Role: independent scalar reconstruction, claim-boundary review, build-chain
attack, and canonical-PDF visual QA  
Verdict: **ACCEPT-CURRENT-FIXED-POINT-SCIENCE / HOLD-MAIN-INTEGRATION / HOLD-PRR-PROJECT**

## 1. Scope and non-execution boundary

This round independently audited the current positive-`B` insertion into the
main encounter manuscript.  It inspected:

- `manuscript/encounter_multimodal_prr.tex`;
- `manuscript/inputs/positive_b_results.tex`;
- `code/build_positive_b_manuscript_input.py` and its tests;
- `code/compile_manuscript.py` and its tests;
- `artifacts/data/manuscript_compile.json`;
- the positive-`B` figure, sidecar, canonical result, two-process evidence,
  independent-audit JSON, frozen manifest, and all 14 manifest pins; and
- the rendered canonical 13-page manuscript PDF, with specific full-resolution
  inspection of pages 7--11.

This round did **not** run or import the scientific producer, execute a
semigroup or finite-volume solve, rerun the canonical scientific auditor, or
modify the manuscript, builder, compiler, figure, canonical JSON, manifest, or
any pinned file.  Mutation attacks used isolated temporary copies only.  The
only repository write is this audit report.

## 2. Decision and open findings

The current frozen scientific snapshot is numerically correct and the main
text does not promote it beyond its evidence.  It supports exactly this claim:

```text
B = 0.01
one unchanged result-informed broad four-slab control
one fixed reflected box
same finite-volume solver family
held-out odd meshes N = 113 and N = 129
five retained alternating roots on the t <= 35 root screen
three valley-partitioned event basins through t = 100
all six basin masses >= 0.005
at least three event-mass-qualified modes in this finite-window sense
```

It does **not** support an allocation cusp, both folds, an interval-global root
census, parity/alignment/box convergence, an unbounded-domain or continuum
limit, an independent solver, positive-`B` physical `d=3`, or a publication
gate.

However, the new manuscript-input and compiler provenance paths are not yet
fail-closed under repinning or concurrent file replacement.  Therefore the
current PDF may remain a truthful internal working draft, but this integration
must not be treated as release-grade until the three P1 findings below are
repaired and independently re-attacked.

Open finding count:

```text
P0 = 0
P1 = 3
P2 = 1
```

## 3. Frozen snapshot and hash closure

The following current hashes were observed independently:

| Artifact | SHA-256 | Current check |
|---|---|---|
| positive-`B` manifest | `955e59bf333b5fd70e415a53dc26becae9c7a34c5d40f1230c96b1dab8f5677c` | MATCH |
| canonical result | `51e8eb4bdb652124865d0c39e6f36b99d13ed61578b161e0f75b142cada49401` | MATCH |
| two-process evidence | `6c0eccaae09ef95923843ddd7a141a27311e1575ee68d3301b4757b785ee9890` | MATCH |
| independent audit | `60c541a6f0decd5431cefa5c203311176e61006586ce69043d5fcf5380ed517d` | MATCH |
| positive-`B` input builder | `43bc511b221611182a8cf7cd1bdf029c43eaf05a007b1d56cf39dfd727e73e7f` | CURRENT |
| generated positive-`B` TeX input | `2eb08d12a5585afa17b8bedfb3d79232a25e328a30439cb0cb0678b13631fabf` | CURRENT |
| main TeX | `a4842808c66c4f9813c024324ca38d18f6406a9db127742093a63edc6fb6613b` | CURRENT |
| manuscript compiler | `34a609661d8aafbe1fe1e15fdb82bd366602b8094c881060a0b133c58b03a192` | CURRENT |
| positive-`B` figure | `3904dbdddd50f7efc1bd66ed5b2274025b08c79bdd044a1efbdfb5a45156fe09` | MATCH SIDECAR |
| positive-`B` figure sidecar | `caa9753debbd3802dda29d03495d04a117d8d2ada47ef16b3fd0506d82ada56d` | CURRENT |
| compile manifest | `6a01fe2e98dd1cf08e4eb75d07f19d306146933d68c4bcc96848e243651b75e3` | CURRENT |
| canonical manuscript PDF | `cbf933008352816b4f52b2e9ad223f469d077d7476fec2426a27d341e8b293ef` | MATCH COMPILE MANIFEST |

All four claim-bearing canonical JSON files are ordinary nonsymlink files.  The
result, evidence, audit, sidecar, and compile manifest are duplicate-free,
finite, canonical sorted JSON.  The historical manifest is duplicate-free and
fixed by its exact byte hash, although it is not serialized in sorted-key
order.  All 14 manifest pins are ordinary nonsymlink files and independently
match their frozen hashes.  The result pin map, fixed weights, physical
parameters, selected budget, evidence timing, and claim scope agree with the
manifest exactly.

## 4. Independent reconstruction of the current numerical claim

### 4.1 Fixed control and root topology

The current fixed weights are

```text
(0.28,
 0.27736690132708747,
 0.0857172266153233,
 0.3569158720575891)
```

They are strictly positive, agree between manifest and result, and sum to
`0.9999999999999999` in binary64.  `weights_refit=false` and `B=0.01` are
consistent across the manifest, result, generated macros, figure sidecar,
abstract, positive-`B` subsection, caption, gate ledger, and discussion.

The saved roots are strictly ordered and the signs of `f_tt` independently
recover `maximum--minimum--maximum--minimum--maximum` on both meshes:

| Quantity | `N=113` | `N=129` |
|---|---:|---:|
| root 1 | `3.3367649300617077` | `3.3066991730834485` |
| root 2 | `5.094308494728989` | `5.085151669158436` |
| root 3 | `8.622283801381938` | `8.588476632538264` |
| root 4 | `13.561466700696581` | `13.529173700011155` |
| root 5 | `22.54889593965799` | `22.51481807006199` |
| peak min/max ratio | `0.8333934839503558` | `0.8391414832973296` |
| valley ratios | `0.7823931607402063`, `0.8467280181266086` | `0.7646777489256341`, `0.8437520432151757` |

The independently reconstructed largest scaled root residual remains below
`1e-8`, the smallest absolute scaled curvature remains above `0.05`, both peak
ratios exceed `0.1`, all valley ratios remain below `0.85`, the declared
endpoint derivative signs hold, and the saved scan/tail positivity,
mass-balance, tangent, and survival gates are true.  No discrepancy was found
in the current canonical result or canonical independent-audit JSON.

### 4.2 Basin-mass definition and the phrase “event-mass-qualified modes”

For retained valley times `v1` and `v2`, the three displayed masses were
reconstructed without reading the saved mass array:

```text
M1 = 1 - S(v1)
M2 = S(v1) - S(v2)
M3 = S(v2) - S(100).
```

This gives:

| Basin mass | `N=113` | `N=129` |
|---|---:|---:|
| `M1` | `0.0052114278399768565` | `0.005227839493313069` |
| `M2` | `0.01662828849270659` | `0.01659738181932957` |
| `M3` | `0.14837901353866123` | `0.14848157030018083` |
| `S(100)` | `0.8297812701286553` | `0.8296932083871765` |

Each interval contains one of the three retained maxima.  The sums equal
`1-S(100)` at saved precision, and all six masses exceed the frozen `0.005`
floor.  Therefore “at least three event-mass-qualified modes” is consistent
with the declared **valley-partitioned, finite-window operational definition**.
It must not be read as a globally exclusive per-mode probability
decomposition: the third interval is truncated at `100`, and no
interval-global exclusion of additional late extrema has been established.

The tightest current margins also reconstruct exactly:

```text
minimum mass relative excess over 0.005 = 4.228556799537131 percent
largest valley ratio                    = 0.8467280181266086
absolute clearance below 0.85           = 0.003271981873391394
```

The manuscript's rounded `4.23%` and `0.84673` statements are correct.

### 4.3 Two-mesh agreement

| Metric | Reconstructed | Frozen ceiling | Verdict |
|---|---:|---:|---|
| maximum paired-root-time difference | `0.0340778695959969` | `0.10` | PASS |
| peak-ratio difference | `0.005747999346973787` | `0.03` | PASS |
| maximum valley-ratio difference | `0.017715411814572146` | `0.03` | PASS |
| maximum basin-mass difference | `0.00010255676151960103` | `0.01` | PASS |
| final-survival difference | `0.00008806174147879542` | `0.02` | PASS |

Every value agrees with the result, independent-audit JSON, generated TeX
macros, main text, and plotted sidecar values.

## 5. Main-text and figure claim-boundary audit

The positive-`B` scope is consistent in all reader-facing locations:

- the abstract says fixed control, same solver, one fixed reflected box, two
  odd meshes, and a finite-window point, and explicitly withholds cusp,
  continuum, independent killed-process, and positive-`B` `d=3` claims;
- the introduction calls allocation cusp, parity/alignment/box continuation,
  and an independent killed-process method separate publication gates;
- the positive-`B` subsection reports only the reconstructed scalar ranges and
  says that two odd meshes in one box cannot establish a continuum or
  unbounded limit and one control cannot establish a cusp;
- Figure 3's caption separately identifies the `t<=35` saved roots and the
  `t<=100` basin masses, then excludes parity, box, continuum, allocation cusp,
  independent solver, and physical `d=3`;
- the gate ledger says `PASS: FIXED CONTROL/TWO MESHES ONLY` and leaves the
  four-slab cusp `NOT RUN`; and
- the discussion again says the first-basin and valley margins are tight and
  that both meshes use the same solver.

No promotion to cusp, continuum, independent solver, physical positive-`B`
`d=3`, submission readiness, or publication readiness was found.

## 6. P1 findings

### P1-1 — The manuscript-input builder does not semantically reconstruct all frozen gates

`_validate_mesh_row` reconstructs topology, peak/valley ratios, and basin
masses, but its only explicit absolute scientific threshold test is

```python
if min(masses) < 0.005 or max(valleys) > 0.85:
    raise RuntimeError(...)
```

It does not require the reconstructed peak ratio to exceed the manifest's
`0.1` floor.  It also does not reconstruct or enforce the saved root residual,
curvature, endpoint-sign, positivity, survival, mass-balance, tangent, or
physical-budget gates.  It checks an aggregate `all_mesh_gates_passed=true`
Boolean but not the exact 24-entry gate map.  At the two-mesh level it
reconstructs the five differences, but does not compare them with the manifest
ceilings or require every reported agreement gate to be true.

The builder also does not require the result weights and physical parameters
to equal the manifest, and it hard-codes `PositiveBFinalTime=100` rather than
verifying and rendering `event_mass.final_time`.

Isolated full-chain repin attacks were accepted in all of these cases:

| Mutated condition | Frozen rule | Observed builder behavior |
|---|---:|---|
| both peak ratios changed below the floor while preserving their cross-mesh difference | peak ratio `>=0.1` | **ACCEPTED** |
| a declared maximum changed to positive curvature with unit scaled residual | negative curvature; residual `<=1e-8` | **ACCEPTED** |
| both result event final times changed from `100` to `50` | final time `100` | **ACCEPTED**, then rendered `PositiveBFinalTime=100` |
| result weights changed to `(0.25,0.25,0.25,0.25)` while manifest weights stayed frozen | exact fixed-control match | **ACCEPTED** |
| paired-root difference changed to `0.3367649300617077` and the reported gate set false | ceiling `0.1`; gate true | **ACCEPTED** |

The hard-coded current result hash protects the present bytes from ordinary
accidental drift, so this does not invalidate the current numerical snapshot.
It is nevertheless not a sufficient semantic contract for the next legitimate
repin, and it defeats the intended fail-closed role of this builder.

Required repair:

1. Strictly validate the manifest and result schemas and cross-check exact
   evidence timing, claim scope, budget, physical parameters, fixed weights,
   mesh identities, scan bounds, tail checkpoints, and final time.
2. Independently reconstruct every claim-bearing per-mesh gate from the
   manifest thresholds, require the exact gate-key set and Boolean values, and
   compare the reconstructed gate map with both result and audit.
3. Independently reconstruct every agreement gate against the manifest
   ceilings and require the exact agreement gate map.
4. Cross-check the audit's mesh reconstructions, gate maps, root times, ratios,
   masses, survivals, and agreement reconstruction against the result rather
   than checking only the five audit agreement metrics.
5. Render the final-time macro from the verified manifest/result value, never
   from a disconnected literal.
6. Add explicit rejection tests for every mutation above.

### P1-2 — Exact hashes do not close the builder's hash-then-load TOCTOU window

Each core source is `lstat`-checked and hashed through one pathname open, then
later parsed through a second pathname open.  The parsed bytes are not required
to be the bytes that produced the accepted hash.  The compiler also calls
`verify_sources()` and `render_macros()` separately, creating two independent
source reads.

An isolated deterministic race replaced the result immediately after the
builder returned the correct frozen hash but before `load_object` opened it.
The replacement changed only the unchecked weights.  The same invocation
rendered

```text
\providecommand{\PositiveBWeights}{0.25000000,0.25000000,0.25000000,0.25000000}
```

and the original result was then restored, so a later post-build hash check
again saw the expected canonical hash.  Thus exact pins alone are not enough
under concurrent replacement.

Required repair:

1. Open each source once with `O_NOFOLLOW`, require a regular file with
   `fstat`, read one immutable byte payload, and hash and parse that exact
   payload with duplicate-key/nonfinite rejection.
2. Apply the same descriptor-based read to every manifest pin.
3. Return one immutable verified snapshot and render macros directly from it;
   do not verify and then reopen the sources to render.
4. Retain a post-build drift check as defense in depth, but do not use it as a
   substitute for same-byte hash/parse identity.
5. Add a hash-then-load swap regression test and require rejection or rendering
   from the originally hashed bytes.

### P1-3 — Compiler figure provenance can attest one figure and stage another

The compiler's figure path has four related fail-closed gaps:

1. sidecar JSON uses ordinary `json.loads`, so duplicate keys are accepted;
2. source-pin paths use `is_file()` and ordinary opens, so a symlink to a
   byte-identical file is accepted and recorded as its resolved target;
3. top-level promotion flags are not validated, so a sidecar with
   `publication_gate_passed=true` and `continuum_interval_verified=true` is
   accepted; and
4. after `_figure_provenance` hashes a figure, `_copy_staged_file` reopens it
   without requiring the staged copy's hash to equal the provenance row.

The fourth issue is decisive.  In an isolated attack, preflight observed the
canonical positive-`B` figure hash, the file was replaced with a different
valid PDF only during the staged copy, and the original was restored before
the post-build provenance check.  The pre- and post-provenance rows were
identical, while the staged PDF hash was

```text
edad5a98e4db21519b718e364f3091e21cdc41302a2ec489e8a3b880a00d4bf8
```

instead of the attested

```text
3904dbdddd50f7efc1bd66ed5b2274025b08c79bdd044a1efbdfb5a45156fe09.
```

The same copy-after-hash pattern applies to the bibliography.  Clean double
builds and post-build live-path checks do not detect a swap that is restored
before the postflight.

Required repair:

1. Load figure sidecars with strict duplicate-key/nonfinite rejection and an
   exact schema appropriate to each figure contract.
2. Require figures, metadata, and pinned sources to be ordinary nonsymlink
   files contained under the report root; read hashes and bytes from one
   descriptor.
3. Validate and record claim flags, evidence timing, scope constraints, and
   the required source-role set for the positive-`B` figure.  Any positive
   publication/continuum/independent-solver/cusp flag must fail this internal
   build.
4. Copy from the verified byte snapshot, or at minimum require every staged
   figure and the staged bibliography to hash exactly to the preflight row
   before LaTeX runs.
5. Add duplicate-key, symlink-pin, positive-claim-flag, and
   verify/copy/restore swap tests.

## 7. P2 finding

### P2-1 — The two different time windows should be stated in one fixed phrase everywhere

The current figure panels and caption correctly distinguish the `t<=35` root
screen from the `t<=100` event-mass/tail window, so no present numerical claim
is false.  The figure's bottom scope line says only “finite `t<=100`”, however,
and the body later says “on the declared finite window.”  A quick reader could
misread those shorter phrases as a five-root census through `100`.

Required wording repair:

```text
five retained roots on the saved/root screen t <= 35;
valley-partitioned basin mass and tail checks through t = 100;
no interval-global or post-35 root exclusion.
```

Use this exact distinction in the abstract or its nearest positive-`B`
sentence, Figure 3's visible scope line and caption, the positive-`B`
subsection, gate ledger, and sidecar.  Continue to say **at least** three modes,
not exactly three globally.

## 8. Tests and transaction attacks

The existing scoped tests passed:

```text
test_build_positive_b_manuscript_input.py
test_compile_manuscript.py
test_plot_positive_b_broad_four_slab.py

34 passed
Ruff check: PASS
```

Publication-transaction exception attacks were also repeated independently:

```text
failure on forward replace 1: exact rollback PASS
failure on forward replace 2: exact rollback PASS
failure on forward replace 3: exact rollback PASS
one directory-fsync failure: exact rollback PASS
temporary incoming/backup cleanup: PASS
```

Therefore no catchable-exception rollback defect was found in
`_publish_transaction`.  This pass does not make a sequence of replacements
power-loss atomic; the compile manifest should remain the last commit marker.

## 9. Canonical PDF visual and structural QA

The canonical PDF has 13 Letter-size pages and hash
`cbf933008352816b4f52b2e9ad223f469d077d7476fec2426a27d341e8b293ef`.
`pdfinfo`, `pdffonts`, text extraction, and rendered-page inspection gave:

```text
pages: 13
font rows: 45
Type 3 fonts: 0
unembedded fonts: 0
missing files: 0
overfull boxes: 0
undefined citations in final TeX log: 0
undefined references in final TeX log: 0
clipped text: none observed
overlapping text/figures: none observed
broken glyphs or black boxes: none observed
```

Pages 7--8 contain the positive-`B` prose, page 9 contains Figure 3, page 10
contains the finite-grid fold and the start of the gate discussion, and page 11
contains the complete gate ledger and continuation of the discussion.  The
float placement splits the positive-`B` prose across pages 7--8 before placing
its figure on page 9, but the reading order is intact.  Figure 3's axes, mesh
line styles, maximum/minimum markers, log-scale basin masses, `0.005` floor,
value labels, and negative scope note are legible.  The gate table wraps some
status cells but has no overlap or clipping.

The figure still uses audit-facing phrases such as “Pinned canonical result”
and a long negative-scope footer.  This is appropriate for the current internal
working draft.  A later submission-facing redraw may move those caveats into a
concise scientific caption, but that editorial pass must preserve the exact
data and scope and is not a substitute for the P1 repairs.

## 10. Required closure criteria

Round 68 can be closed only after all of the following are true:

```text
P1-1 full semantic gate reconstruction: PASS
P1-1 repin mutation regressions: PASS
P1-2 same-byte hash/parse snapshot: PASS
P1-2 hash/load race regression: PASS
P1-3 strict figure metadata and ordinary-file policy: PASS
P1-3 staged figure/BIB hash identity: PASS
P1-3 verify/copy/restore race regression: PASS
P2-1 t<=35 roots versus t<=100 masses wording: explicit everywhere
full scoped tests: PASS
clean double manuscript compile: byte-identical PASS
canonical PDF and compile manifest: transactionally refreshed
rendered pages 7--11: visually rechecked
independent re-attack: P0=0, P1=0
```

Even after those integration repairs, the overall PRR project remains on hold
for the already declared scientific gates: same-family finite-`B` allocation
cusp and both folds, parity/alignment/box continuation, an independent killed
process, and positive-`B` physical `d=3` if a two-/three-dimensional headline
is retained.
