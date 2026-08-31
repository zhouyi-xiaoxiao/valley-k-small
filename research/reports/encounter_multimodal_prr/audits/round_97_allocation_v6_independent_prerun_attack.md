# Round 97: allocation-cusp v6 independent result-blind pre-run attack

Date: 2026-07-14  
Role: fresh independent adversarial pre-execution reviewer  
Verdict: **GO-FORMAL-SEQUENTIAL-65-THEN-97**  
Open findings: **P0 = 0, P1 = 0, P2 = 0**

## 1. Boundary and frozen anchors

I attacked the exact Round-85 allocation without editing any frozen byte. I
did not invoke `--execute-frozen`, `--execute-replica`, either scientific
`run_formal` path, or the producer/auditor scientific `main`; I did not build
or evaluate mesh 65 or 97. Adversarial fixtures existed only under
`/private/tmp`. The only workspace file added by this review is this report.

| role | independently recomputed SHA-256 |
|---|---|
| Round-85 repair freeze | `b05e9660ad99d273eca7e9b05538fa68da993bdf0f6d40148bfb058fd65ae1ee` |
| v6 manifest | `2e1223f6206c6ebc4adc5c11ed67672afdc55f68e90f725cf8b6930bb67b9948` |
| discovery runner | `b32260ad18abd3f159b7cac1dcd600be2507ff2a89cf60712c5c6f66ccbd70da` |
| independent auditor | `38b7822efce5ddd3b0220549a94a259f393c44150f66a61140f9b58029bf23f0` |
| discovery protocol v6 | `3c56b307bed70c52152c31764aa84020b7c45770ea656e00fe1d54d47b51ab2b` |
| no-cycle post-result protocol | `393b648c9ba36acc47b9c9acfbc86a82946df495fb36928f6ded91e826ca03b7` |
| Round-85 regressions | `60665c7edaa3cd5a85213415529c43ccd38c69a6390186075bff3c109bc341a9` |

The manifest is canonical JSON. Its 27 role paths are unique, canonical,
report-relative regular files; all 27 independently rehashed exactly. The
manifest has no self-pin or backward hash edge. The forward auditor/protocol
chain points to the manifest digest without entering the manifest.

## 2. Exact clean regression and an audit-method ordering diagnostic

The exact disclosed single-process file order was rerun in a fresh external
process:

```text
ordinary -> Round50 -> Round61 -> Round74 -> Round80 -> Round85
         -> auditor -> Stage-A
```

Collection was exactly `14 + 15 + 9 + 15 + 25 + 9 + 8 + 11 = 106`; the run
returned **106/106 PASS**, exit 0.

As an adversarial diagnostic, I also placed the Stage-A tests first. That
unsupported order returned 102/106 because a permitted small-grid Stage-A
fixture left `continuum_g1_smoke` in `sys.modules`; the later discovery
dry-run correctly rejected a preloaded runtime module. The two-node minimum
reproduction was:

```text
Stage-A test_basis_trust_box_and_dry_run_boundary_are_fail_closed = PASS
discovery test_dry_run_never_executes_scientific_meshes = fail-closed RuntimeError
```

This is an audit-harness ordering limitation, not a frozen production defect:
it is a safe false-negative, the protocol discloses the passing exact order,
and every formal parent/replica is a fresh `-I -S -B` process rather than a
shared pytest process. No scientific or output path was touched in either run.

## 3. Hash randomization, ordering, and two seven-cell replicas

Six real `-I -S -B` processes were launched with different externally claimed
`PYTHONHASHSEED` values. All reported `ignore_environment=1` and
`hash_randomization=1`; all six observed `hash("encounter")` values differed.
Thus the result does not rely on an ignored fixed seed.

The runner bytes were descriptor-read, independently hash-matched, and the
literal `ISOLATED_RUNNER_BOOTSTRAP` was extracted by AST. Two sequential fresh
processes then ran only `--algebra-dry-run --cells 7`. Their canonical stdout
was byte-identical:

```text
bootstrap SHA-256 = 19e3f2013a5a0af31c9a43dcb23e54ad15f7d41ef80adcb6f33ea9707fcce6c5
replica bytes       = 1061
replica SHA-256     = 9fe5c7c2cbab521080af5a3878925b96f5dd8bf3659f067f2734b3049711f366
status              = PASS_ALGEBRA_DRY_RUN_HOLD_SCIENCE
CSR maximum error   = 2.220446049250313e-16
scientific meshes   = []
```

Independent insertion/set-order mutations and the frozen ordering regressions
also returned identical canonical mappings. Sorting boundaries cover gate
maps, candidate/representative ranks, tie breaks, native rows, and canonical
JSON keys. No full formal replica was run because that would execute the
prohibited meshes.

## 4. Native and Python runtime provenance attack

Producer, independent auditor, and a third read-only implementation rebuilt
the complete runtime witness. All three agreed field-for-field with the
manifest:

```text
phase image counts = 13 / 93 / 94 / 98
closure rows       = 98
closure SHA-256    = 5f857bf207eb181ca758e501f394584cb8c2833c5764712133d53f9018295cb0
aliases            = 101 (three multi-alias rows)
install-name rows  = 4
rpath rows         = 31 (34 total rpaths)
dependency edges   = 4 non-system + 140 system-cache leaves
unique system leaves = 8
```

The `93 -> 94` difference contained exactly one `pyexpat` image. A separate
isolated staged probe attributed it uniquely to
`signed_dyld_cache_provenance -> platform.mac_ver()`. No phase comparison was
weakened to a subset.

Actual Mach-O bytes, sizes, hashes, install names, all lexical aliases,
resolved paths, `LC_RPATH`s, recursive dependencies, reachability, system
leaves, loaded phases, and `ctypes/_ctypes` probe images were rechecked. The
real graph has no ambiguous `@rpath` resolution; temporary Mach-O path fixtures
independently covered `@loader_path`, `@executable_path`, `@rpath`, and
unresolved cases in all three implementations.

Eleven mutation families all failed before a minimum runner sentinel:
wrong phase, path, file hash, dependency, alias, transition cause, count,
closure digest, install name, rpath, and loaded-phase membership.

The broader frozen Python witness also matched:

```text
stdlib       2865 entries / 2862 regular / 383 pyc / 3 symlinks
NumPy RECORD 929; import tree 1036; pyc 132; native extensions 19
SciPy RECORD 1431; import tree 1871; pyc 446; native extensions 109
NumPy build configuration = exact manifest value
```

The witness remains reproducibility/drift evidence under the declared
no-concurrent-writer/no-OneDrive-replacement contract. It is not presented as
malicious same-UID prevention.

## 5. Trace, diagnostics, fixed-shape, and v6-auditor matrix

A complete synthetic PASS fixture reconstructed its exact 691-row scan and
70-row saved projection through the v6 auditor. Seventeen independently
constructed mutations all returned `HOLD_AUDIT` or the corresponding
integrity HOLD:

- delete, duplicate, or retime a full-scan row;
- delete or retime a saved-trace row;
- change the grid count or reference maximum;
- make scan, root, model, cusp, or tail diagnostics negative;
- delete an all-bracketed-root row;
- change preflight shape or error-key closure;
- delete one fixed mesh row; and
- assert a forbidden publication claim.

Producer and auditor regressions additionally rebuild extrema, aggregates,
brackets, nonnegative residual/error/mass contracts, physical-law rows,
generator traces, fixed PASS/HOLD schemas, and the two-mesh/branch/control
shape. No self-reported gate alone can promote a result.

## 6. Sequential replicas and atomic publication boundary

Ten focused transaction tests independently passed for byte disagreement,
external manifest binding, first-child staging collision, failed-child owned
replica cleanup, preexisting canonical collision, no-cycle/output collision,
no-replace installation, rollback after directory-sync failure, and
preservation of replaced or otherwise unowned inodes.

The two formal replicas are constrained to execute sequentially. Replica two
cannot start until replica one has returned and the full five-path boundary
and both promotion-stage paths have been rechecked. Promotion is permitted
only after byte identity, complete pin snapshots, lexical snapshots, and
ownership checks. Rollback unlinks only an inode created and still owned by
the current invocation.

Before the audit, after every executable check, and immediately before this
report, all seven paths were lexically absent:

```text
artifacts/data/positive_b_allocation_cusp_discovery_result.json
artifacts/data/positive_b_allocation_cusp_discovery_reproducibility.json
artifacts/data/.positive_b_allocation_cusp_discovery_result.replica_1.json
artifacts/data/.positive_b_allocation_cusp_discovery_result.replica_2.json
artifacts/data/positive_b_allocation_cusp_discovery_independent_audit.json
artifacts/data/.positive_b_allocation_cusp_discovery_result.json.staging
artifacts/data/.positive_b_allocation_cusp_discovery_reproducibility.json.staging
```

## 7. Commands, counts, and decision

```text
exact frozen pytest order                         106/106 PASS
native/static/negative independent submatrix    2034/2034 PASS
real isolated hash probes                           6/6 PASS
sequential exact cells-7 replicas                    2/2 PASS
synthetic 691/70 baseline plus auditor mutations    18/18 PASS/HOLD-as-required
focused replica/publication transactions             10/10 PASS
total independently observed checks/probes         2176/2176
```

Harnesses:

```text
/private/tmp/allocation_v6_native_static_attack.py
SHA-256 b23fe4c5263fc03785aaa99aba9a240b8634ec274470439164031d0630c9aa21

/tmp/v6_isolated_cells7_replicas.py
SHA-256 06ebfa601e581c7549b09a7189f19cd458b3307039b6e9f92ffe4de975d8241f

/tmp/v6_trace_auditor_matrix.py
SHA-256 c906cc50429f8d8cd31b9306f509330af441af368edfd49b4616ce58b133c5eb
```

Final ledger:

```text
P0 = 0
P1 = 0
P2 = 0
decision = GO-FORMAL-SEQUENTIAL-65-THEN-97
mesh 97 rule = run only if mesh 65 and every intervening gate do not HOLD
separate/manual mesh commands = NOT AUTHORIZED
```

Expected atomic paths for the one formal invocation:

```text
replica 1: artifacts/data/.positive_b_allocation_cusp_discovery_result.replica_1.json
replica 2: artifacts/data/.positive_b_allocation_cusp_discovery_result.replica_2.json
result stage: artifacts/data/.positive_b_allocation_cusp_discovery_result.json.staging
evidence stage: artifacts/data/.positive_b_allocation_cusp_discovery_reproducibility.json.staging
canonical result: artifacts/data/positive_b_allocation_cusp_discovery_result.json
canonical evidence: artifacts/data/positive_b_allocation_cusp_discovery_reproducibility.json
later independent audit: artifacts/data/positive_b_allocation_cusp_discovery_independent_audit.json
```

On failure, only still-owned replica/staging inodes may be removed; any
preexisting or replaced unowned inode is preserved, and canonical/evidence
installation remains no-replace.

## 8. The only authorized formal launch command (not executed in this round)

Run this block exactly once from any shell. It changes to the frozen repository
root, descriptor-reads and SHA-matches the runner, AST-extracts the exact
literal bootstrap while preserving trailing newlines, verifies the bootstrap
digest, and launches the sole formal parent under the clean environment:

```bash
cd '/Users/ae23069/Library/CloudStorage/OneDrive-UniversityofBristol/Desktop/valley-k-small' &&
ROOT=$(pwd -P) &&
PY="$ROOT/.venv/bin/python" &&
RUNNER="$ROOT/research/reports/encounter_multimodal_prr/code/positive_b_allocation_cusp_discovery.py" &&
SITE="$ROOT/.venv/lib/python3.12/site-packages" &&
RUNNER_SHA256='b32260ad18abd3f159b7cac1dcd600be2507ff2a89cf60712c5c6f66ccbd70da' &&
BOOTSTRAP_X="$("$PY" -I -S -B -c '
import ast, hashlib, os, stat, sys
path, expected = sys.argv[1:]
if not os.path.isabs(path):
    raise SystemExit("runner path is not absolute")
fd = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
try:
    before = os.fstat(fd)
    chunks = []
    while True:
        block = os.read(fd, 1024 * 1024)
        if not block:
            break
        chunks.append(block)
    after = os.fstat(fd)
finally:
    os.close(fd)
source = b"".join(chunks)
identity = lambda item: (item.st_dev, item.st_ino, item.st_size, item.st_mtime_ns)
if not stat.S_ISREG(before.st_mode) or identity(before) != identity(after):
    raise SystemExit("runner descriptor changed during capture")
if hashlib.sha256(source).hexdigest() != expected:
    raise SystemExit("runner SHA-256 mismatch")
tree = ast.parse(source, filename=path)
values = [
    ast.literal_eval(node.value)
    for node in tree.body
    if isinstance(node, ast.Assign)
    and any(isinstance(target, ast.Name) and target.id == "ISOLATED_RUNNER_BOOTSTRAP" for target in node.targets)
]
if len(values) != 1 or not isinstance(values[0], str):
    raise SystemExit("frozen bootstrap literal is not unique")
sys.stdout.write(values[0])
' "$RUNNER" "$RUNNER_SHA256"; status=$?; printf x; exit "$status")" &&
BOOTSTRAP="${BOOTSTRAP_X%x}" &&
test "$(printf %s "$BOOTSTRAP" | shasum -a 256 | awk '{print $1}')" = '19e3f2013a5a0af31c9a43dcb23e54ad15f7d41ef80adcb6f33ea9707fcce6c5' &&
env -i HOME="$HOME" PATH='/usr/bin:/bin' LANG=C LC_ALL=C TMPDIR=/private/tmp \
  OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  VECLIB_MAXIMUM_THREADS=1 NUMEXPR_NUM_THREADS=1 \
  "$PY" -I -S -B -c "$BOOTSTRAP" "$RUNNER" "$SITE" \
  --execute-frozen \
  --expected-manifest-sha256 2e1223f6206c6ebc4adc5c11ed67672afdc55f68e90f725cf8b6930bb67b9948
```
