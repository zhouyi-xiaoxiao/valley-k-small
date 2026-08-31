# Round 84: allocation-cusp v5 independent result-blind pre-run attack

Date: 2026-07-14  
Role: independent adversarial pre-execution audit of the Round-83 v5 freeze  
Verdict: **HOLD-PREEXECUTION / NO-GO-65-97**

## 1. Boundary

This audit was independent of the Round-83 implementation. It rehashed and
read the frozen package, ran the permitted test/lint/compile checks, exercised
only the seven-cell algebra dry-run bootstrap, and used read-only native-image
inspection. It did **not** invoke `--execute-frozen`, `--execute-replica`,
`run_formal`, or either producer/auditor scientific `main`; it did not build or
evaluate mesh 65 or 97; and it did not inspect any scientific result.

No frozen candidate byte was edited. The only new file is this independent
report. Before and after the attack, all seven result/evidence/replica/audit
and promotion-stage paths were lexically absent:

```text
artifacts/data/positive_b_allocation_cusp_discovery_result.json
artifacts/data/positive_b_allocation_cusp_discovery_reproducibility.json
artifacts/data/.positive_b_allocation_cusp_discovery_result.replica_1.json
artifacts/data/.positive_b_allocation_cusp_discovery_result.replica_2.json
artifacts/data/positive_b_allocation_cusp_discovery_independent_audit.json
artifacts/data/.positive_b_allocation_cusp_discovery_result.json.staging
artifacts/data/.positive_b_allocation_cusp_discovery_reproducibility.json.staging
```

## 2. Recomputed freeze anchors

| role | SHA-256 |
|---|---|
| v5 manifest | `a28ae5c17d3a93139a122dbfc1d6890d74fae69bad9bbac950e42c74a20b31d0` |
| v5 runner | `8b80898f02b132d6a8e07aec8e8ce6c54fe8930f989d93bb68410dc8eb2d6662` |
| v5 protocol | `834e382c901d1fb060168ac388641d347a86b4293f346b437bdb0f659850165d` |
| independent auditor | `3baac627078ca3f43b25d108df2b089775fdc51ddebe5193310567249b4076ab` |
| no-cycle post-result protocol | `34a30fc3cd1a17074cc4b7286218527a79dc9ca8c1d7734f841ae9e9ed866791` |
| Round-83 implementer freeze | `104e6c23803fc80d6cffcd131e846b06295106748e7345685baffcfa5dbf0f67` |

All 25 manifest roles were unique report-relative paths, every lexical target
was a regular file, and every independently recomputed file hash matched. The
manifest and auditor's externally frozen manifest hash agree exactly.

## 3. Decision and open count

```text
P0 = 0
P1 = 2
P2 = 0
```

The scientific validators, complete-scan evidence, replica transaction, and
independent auditor are materially stronger than v4. Neither open P1 is a
demonstrated scientific false positive. Both are nevertheless launch-blocking
reproducibility/provenance contradictions in the frozen execution contract.
Publishing bytes under a condition that CPython did not apply, or calling an
incomplete native-image witness a frozen runtime closure, is not acceptable
for a publication-grade first run.

```text
HOLD-PREEXECUTION
NO-GO-MESH-65
NO-GO-MESH-97
NO PRODUCER/AUDITOR SCIENTIFIC MAIN
AUTHORIZED SCIENTIFIC COMMAND: NONE
```

The manifest hash `a28ae5...b31d0` must not be used for mesh 65 or 97. Repair
requires new candidate bytes, a new manifest/hash, and another independent
result-blind pre-run audit.

## 4. P1 findings

### P1-1 - `-I` makes the claimed fixed `PYTHONHASHSEED=0` false

The manifest records `reproducibility.subprocess_environment.PYTHONHASHSEED =
"0"`; the protocol says the two replicas run under fixed
`PYTHONHASHSEED=0`; and the parent does put that variable in the child's
environment. The same formal command necessarily starts CPython with `-I`.
In CPython 3.12, `-I` implies `ignore_environment=1`, so the interpreter has
already ignored `PYTHONHASHSEED` before the bootstrap can run.

An independent three-process probe of the frozen interpreter gave three
different values for `hash("encounter")` under

```text
env PYTHONHASHSEED=0 python -I -S -B ...
```

while three non-`-I` processes gave the same value. Thus this is an observed
contract contradiction, not a theoretical edge case.

The present implementation contains important containment:

- canonical JSON uses `sort_keys=True`;
- all order-sensitive scientific candidate/ranking paths inspected here use
  explicit list order or sorting;
- the only direct iterations over set literals/constants found by AST review
  are boolean schema/domain predicates, not output construction; and
- promotion requires two full-process canonical byte streams to be identical.

Therefore random hash secrets should at worst produce an operational HOLD if
an unreviewed order leak remains; the two-replica gate prevents promotion of
two visibly different results. It does not make the claimed fixed seed true,
and two coincidentally equal results cannot certify that nonexistent runtime
condition.

Required repair, without weakening isolation:

1. retain `-I -S -B` and remove `PYTHONHASHSEED=0` from the manifest,
   protocol, and asserted fixed environment;
2. state honestly that isolated replicas use CPython hash randomization and
   require `sys.flags.hash_randomization == 1` and
   `sys.flags.ignore_environment == 1`;
3. sort every set/dict-derived sequence before it can influence numerical
   assembly, tie-breaking, list serialization, or diagnostics;
4. retain complete two-process byte identity and the pinned/restored NumPy
   RNG state; and
5. add regressions proving the fixed-hash claim is absent and synthetic
   insertion/set-order permutations yield identical canonical bytes.

Trying to recover a fixed hash seed by dropping `-I` would be the wrong fix:
it would reopen the import/environment attack that v5 correctly closed.

### P1-2 - the runtime witness omits actually loaded non-system native images

The v5 NumPy/SciPy closure itself survived the attack. Independent `otool`
inspection found 128 native files: 19 under NumPy and 109 under SciPy,
including SciPy's three package-local Fortran runtime dylibs. Their recursive
direct dependencies resolve only to those exact package-local frozen files or
to `/System/Library` and `/usr/lib` leaves covered by the signed dyld cache.
The inactive Homebrew `LC_RPATH` entries in `_fblas` have no `@rpath`
dependency and do not select a Homebrew numerical library.

The wider Python runtime witness is incomplete. The manifest pins the Python
executable, two Python framework images, and the full stdlib tree, including
the stdlib extension modules. It does not pin the non-system dylibs to which
those pinned extensions link. A static scan of 79 stdlib/framework Mach-O
candidates found reachable Homebrew dependencies including OpenSSL, xz,
mpdecimal, SQLite, and SSL. A minimal `-I -S -B`, allowlisted-environment probe
that imported the runner's exact top-level NumPy/SciPy dependency set then
confirmed these non-system images were actually mapped:

| actual image | SHA-256 | present in manifest witness |
|---|---|---|
| Homebrew `libcrypto.3.dylib` 3.6.3 | `34bc039f5c725691e757ef42d26f1709830b18046c3ad6d93985153c83d0bbbc` | no |
| Homebrew `liblzma.5.dylib` 5.8.3 | `3d5bfa2f097c31463642b1daab5e662b44368bb4da368f85e412e7f9adcbaa10` | no |
| Homebrew `libmpdec.4.0.1.dylib` 4.0.1 | `30a40206c5b075e7b92f11aead6e937559e7a418914fd01dc925e92894c1796d` | no |

This finding must keep two trust statements separate. The interpreter, early
stdlib modules, and the hash primitive are already declared as the bootstrap
root of trust; `libcrypto`, used by `_hashlib`, can be made part of that
explicit trust root. That declaration is not a reproducibility witness. The
current stdlib closure cannot detect a replacement of these external native
bytes, and the two replicas would load the same replacement. The signed dyld
cache is also not relevant to these Homebrew files because they are outside
the OS cache.

Required repair, bounded to the publication threat model:

1. freeze every non-system native image actually reachable/loaded by the
   authorized bootstrap and runner imports, recording install name, lexical
   path, resolved path, size, and SHA-256;
2. recursively close their Mach-O dependencies, resolving
   `@loader_path`, `@executable_path`, and `@rpath`, and reject unresolved or
   newly introduced non-system leaves;
3. revalidate the exact external-image bytes/metadata in every formal process
   and in the independent auditor;
4. keep signed dyld-cache CodeDirectory hashes as the OS/system leaves; and
5. add a regression in which a synthetic external dylib hash/path is changed
   while the pinned stdlib extension is unchanged.

This does not require expanding the threat model to a malicious same-UID
writer. The existing no-concurrent-writer/no-OneDrive-replacement contract can
remain. It requires only that the claimed reproducibility witness cover the
non-system native bytes the process actually executes.

## 5. Attacks that did close

The following independent review/replay found no additional open defect:

- exact bootstrap: the absolute frozen interpreter with `-I -S -B`, absolute
  runner/site paths, and the external manifest hash completed only the
  permitted seven-cell dry run; removing any of `-I`, `-S`, or `-B`, changing
  the external hash, or using a relative runner failed closed;
- import/loader isolation: the allowlisted child environment removes
  `PYTHONPATH`, customization-module injection, and all `DYLD_*`/`LD_*`
  variables; the four local runtime modules are descriptor-bound and
  preloaded substitutions are rejected;
- complete scan: producer and auditor reconstruct all 691 times from 0.5 to
  35 at spacing 0.05, the exact 70-row 0.5-spaced projection, extrema and law
  aggregates, every grid bracket, and every eligible or ineligible refined
  root; deletion or mutation of either trace fails both paths;
- diagnostics: negative and nonfinite residual/error/norm/mismatch/drift/mass
  mutations in the synthetic contracts fail closed;
- replica publication: a first-child foreign stage/canonical/audit collision
  stops child two, failed owned replicas are removed, and rollback preserves
  a replaced unowned inode;
- independent auditor: its source does not import the producer, it binds the
  external manifest hash, writes append-only, preserves unowned output, and
  the forward manifest/producer/auditor/protocol chain contains no hash cycle;
  and
- scientific claim boundary: even a future valid result remains
  `PASS_DISCOVERY_LOW_MESH_ONLY`, with no held-out, parity, box, continuum,
  independent-solver, or publication claim.

## 6. Executed validation

| check | result |
|---|---|
| exact combined collection | **97/97 PASS**, exit 0 |
| collection cardinalities | `8 + 14 + 15 + 9 + 15 + 25 + 11 = 97` |
| Ruff format | 10 files already formatted |
| Ruff lint | all checks passed |
| Python compile | all 10 targets compiled into a temporary cache |
| manifest pins | 25/25 matched |
| final frozen anchor hashes | unchanged from Round 83 |
| final output/staging boundary | all seven paths absent |
| mesh 65/97 execution | **not run** |

The 97-test pass is evidence that v5 closes the prior algebra/schema,
complete-scan, transaction, and auditor attacks. It cannot override either
new provenance contradiction because no frozen regression presently asserts
the effective hash mode or the recursively loaded non-system stdlib native
images.

## 7. Repair acceptance gate

A successor freeze may return to independent pre-run review only if it:

1. removes the false fixed-hash condition while retaining isolated execution,
   explicit ordering, and two-process byte identity;
2. adds a recursively closed, independently auditable witness for actual
   non-system native images while retaining signed OS-cache leaves;
3. rebuilds the manifest and forward no-cycle chain from the repaired bytes;
4. passes the existing 97 tests plus new regressions for both P1 findings; and
5. still begins and ends with all seven scientific/evidence paths absent.

Until then the decision remains **NO-GO-65-97**.
