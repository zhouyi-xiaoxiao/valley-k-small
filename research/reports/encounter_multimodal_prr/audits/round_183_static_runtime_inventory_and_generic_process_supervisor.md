# Round 183: static runtime inventory and generic process supervisor

Date: 2026-07-19

Status: **STATIC RUNTIME BYTE-PIN INVENTORY AND GENERIC PROCESS SUPERVISOR
FROZEN AT COMPONENT SCOPE / RECOMMENDED AUTHORITY ROOT AND PERSISTENT JSON
ABSENT / NO AUTHENTICATED RUNTIME PROBE OR RUNTIME CLOSURE / INTEGRATED
P0=0/P1=2/P2=4 / NO MATERIALIZATION, PLAN, BUNDLE, REQUEST, COMMITMENT,
EXECUTION, OUTPUT, RECEIPT, REPLAY, B06, SAME-MEMBER, C1--C3, F0--F3, ROOT,
RELEASE, OR SUBMISSION PROMOTION**

## 1. Scope and nonclaim boundary

Round 183 separates three objects that must not be conflated:

1. **A: static byte-pin inventory** -- a pure authenticated-bytes component
   that checks the proposed six-file runtime layout, five Mach-O images, and
   thirteen dependency edges without opening, importing, executing, or
   publishing the serialized paths;
2. **B: future authenticated runtime probe** -- an authority-bound,
   result-blind child that must later execute from a materialized sealed root
   under the generic supervisor and observe imports, origins, metadata, and
   loaded numerical images in two fresh runs; and
3. **final `runtime_closure`** -- a later precommit object that must join A and
   B to the Round-182 AST resolver, a trusted origin classifier/adapter, and
   the actual six role-v3 sources plus global runner.

Only A and the generic process-mechanics component are frozen here.  B and the
final closure do not exist.

## 2. Recommended external layout; no persistent root

The exact recommended root is

```text
/Users/ae23069/.local-build/valley-k-small/runtime-authorities/encounter-c1-n0-cpython-3.12.13-gmpy2-2.2.1-arm64-v1
```

with this exact tree:

```text
ROOT/                                      0555
  bin/                                     0555
    python3.12                             0555
  site-packages/                           0555
    gmpy2/                                 0555
      __init__.py                          0444
      gmpy2.cpython-312-darwin.so          0444
    gmpy2.libs/                            0555
      libgmp.10.dylib                      0444
      libmpfr.6.dylib                     0444
      libmpc.3.dylib                       0444
```

This is five directories and six regular files totaling 1,716,156 bytes.
Future materialization must require uid 502, gid 20, link count one for every
file, no symlink, ACL, extended attribute, BSD flag, or extra entry, and the
exact modes above.  No `pyvenv.cfg`, `.pth`, `dist-info`, manifest, or other
file belongs inside the root.

The six proposed file hashes are:

| File | SHA-256 | Bytes |
| --- | --- | ---: |
| `bin/python3.12` | `31b9c9a8d50289f3a13f014b3efd8ea3534fc3eea7ca7d9809e166139910b805` | 52,448 |
| `site-packages/gmpy2/__init__.py` | `3d4f21a0e9d6d32c935e3d39ef4be23a9a7d0ea56344ebbb0b8dca4f5651e8a2` | 412 |
| `site-packages/gmpy2/gmpy2.cpython-312-darwin.so` | `9586b7c4b887704b57576f52b73a8c45437946d2b172095d82c20fa0871a415b` | 573,056 |
| `site-packages/gmpy2.libs/libgmp.10.dylib` | `22cec4689e503d590cfbf3373ae7f442ef6d40c3e6c93a3612bbd1b7e2bce049` | 468,768 |
| `site-packages/gmpy2.libs/libmpfr.6.dylib` | `d314a427a901f8ece38b67966cd2fbf5642ceb7d1c2e5136f8282ca7ab859aed` | 469,360 |
| `site-packages/gmpy2.libs/libmpc.3.dylib` | `d3c10c39234c095f5c1938ad607c87a0633152f51271d9ed1c494724430c2b0c` | 152,112 |

A disposable `/tmp` copy showed that the copied launcher plus the exact
site-packages prefix can import the wrapper and nested extension.  That copy
was removed.  The launcher still loads the external Homebrew framework Python
at SHA-256
`81e88e84a74017ba097c0775aef09f9583617923757f7ed3e16c3203a0106337`
and uses the external Homebrew standard library.  The framework, dyld,
`libSystem`, CoreFoundation, standard library, and macOS remain explicit host
boundaries, not sealed bytes.

The recommended root is absent.  No persistent authority/inventory JSON was
written.

## 3. Initial authority prototype: HOLD

The first mutable prototype bytes were:

| Object | SHA-256 | Bytes |
| --- | --- | ---: |
| builder | `02f758ee711270d7f8f8e2856b7328e6a23011fa764ea95a6dc01cb933e6efce` | 29,575 |
| validator | `f2a70e3fdaa5b31a842903a1a00f7aaae97f4e932f362530229383779e0d682e` | 29,401 |
| tests | `2bb8eb05f149b0af25aefc2c76eda78fe8427671fd00f0e9bfedccd169bc2cb7` | 27,108 |

Their 100/100 synthetic tests did not make them freeze-ready.  The contract
audit returned `P0=0/P1=3/P2=3`:

1. version, ABI, and Darwin/build labels were caller-formatted rather than
   observed, so forged labels could pass;
2. six unique paths anywhere below a caller-selected root could be relabeled
   as the Python, wrapper, extension, and libraries while hard-coded import
   names survived; and
3. host boundaries were not required to lie outside the proposed authority
   root.

Its P2 findings were incomplete nonclaims, near-copy builder/validator logic,
and a generic `Mapping` read repeatedly rather than snapshotted once.

A separate Mach-O audit returned `P0=0/P1=4/P2=2`.  It found set-based
collapse of aliased numerical targets; incomplete endian, architecture,
subtype, and reserved-field closure; incomplete rejection and
placement/multiplicity checks for unknown, weak, reexport, lazy, upward,
dyld-environment, rpath, and dylinker commands; and common-mode parsing whose
malformed tests mainly attacked only the builder.  The two P2 gaps were thin
`lc_str`/padding/ASCII/endian coverage and thin fat-header/count/size coverage.
These ledgers overlap and must not be summed.

## 4. Frozen static inventory component

The repaired component hard-pins the operation-model-v2 SHA and schema, the
process-contract section SHA, the one exact external root, all six destination
paths and hashes, the five Mach-O image kinds, the exact command sequences,
and all thirteen classified edges.  It treats `LC_ID_DYLIB` as image identity,
not a dependency edge; rejects unpinned internal edges and unexpected external
edges; and records only three explicit host-boundary paths.

Unobserved Python/gmpy2/GMP/MPFR/MPC and platform strings are now labeled
`DECLARED_EXPECTATIONS_NOT_OBSERVED_BY_THIS_STATIC_INVENTORY`.  The claim
boundary explicitly keeps root materialization, path identity, imports,
runtime metadata, runtime probing, complete host bytes, runtime closure,
candidate execution, and science false.

The frozen files are:

| Object | SHA-256 | Bytes | Mode / links |
| --- | --- | ---: | --- |
| builder | `a41e68012f66c5e9e71cdd780caad7ee64ea3425e39aa72e031d4f58a7e98390` | 31,510 | `0444` / 1 |
| source-separated validator | `b68b42fced8e28f9b2584295aba1937d147222e4e61d0fcf808e74c142d501e4` | 31,132 | `0444` / 1 |
| tests | `2625757a1e49ed3863f293afc4af859fbea3a1432fd0986fbb8d3ce5f1e82ffc` | 26,376 | `0444` / 1 |

The focused suite passes **92/92**.  Against the currently authenticated input
bytes, the canonical inventory exists only in memory: it is 11,715 bytes with
SHA-256
`13b70ec6194bbad62e19cea2538f19a8351e6f6ad820ac7a09d0adf25433b8c6`.
It contains five Mach-O images and thirteen edges.

The final static-component ledger is `P0=0/P1=0/P2=1`.  The sole P2 is
common-mode risk: although validator source is separate, its parser,
classifier, constants, and oracle remain highly isomorphic to the builder.
External `otool` comparison and exact hard hashes keep this from P1, but it is
not formal independence.

## 5. Generic process-supervisor chronology

### 5.1 Initial HOLD

The initial supervisor and tests had SHA-256 values
`6531ae4f06056ca829d2b9d83887a6c351438873bc4a9a9a7047478048379acb`
(23,203 bytes) and
`0f054cb0e24893d2fc4a23478ed4380b022e55a6a30ab547ac51970f89d09ae4`
(10,427 bytes).  Its 18/18 tests missed three P1 defects.  Independent review
returned `P0=0/P1=3/P2=4`: clean child success preceded deadline checking;
each cleanup phase received a fresh relative deadline and could exceed the
global bound; and the code assumed pid as process-group identity without
observing PGID/SID.  P2 covered cap-overflow discard behavior, capture-failure
cleanup, the pathname/Popen race, and missing negative tests.

### 5.2 First repair and second HOLD

The first repair produced supervisor SHA-256
`62c7ef1dbaef5baf172dfbdf18b00cb197ad46dae494b8551b93b08e47298ecc`
(28,021 bytes) and test SHA-256
`f970eb7ed1f32ad98779260429c73717b1e67dbde31460b9e61eb5396acfd247`
(16,473 bytes), with 26/26 tests.

The second audit still returned `P0=0/P1=3/P2=3`: selector construction could
cross both deadlines yet still reach `Popen` without deadline issues;
`set_blocking` failure could enter cleanup and perform blocking reads beyond
the cleanup deadline; and a session mismatch still used pid as PGID while
reporting cleanup complete.  Remaining P2 items were environment-surrogate
normalization, absence of the exact production deadline adapter, and the
instantaneous PGID-reuse boundary.

### 5.3 Frozen generic component

The second repair gates selector construction and `Popen` against both
absolute deadlines, checks deadlines before success, clips every TERM, KILL,
reap, group-absence, and pipe-EOF wait to one caller-supplied cleanup deadline,
and immediately enters cleanup on cap+1 or capture failure.  It observes PGID
and SID and owns the group only when both equal the child pid.  An unowned
group is not signalled and cannot yield a complete cleanup receipt.

The supervisor remains semantics-free: return codes, stdout, and stderr are
raw observations for a future caller.  It requires an exact five-key
environment, absolute argv, private mode-0700 cwd/HOME/TMPDIR, a new session,
bounded nonblocking capture, and structured cleanup evidence.  It normalizes
argv/environment surrogate failures to input rejection.

The frozen files are:

| Object | SHA-256 | Bytes | Mode / links |
| --- | --- | ---: | --- |
| supervisor | `8714c0646f394f30b1fea8e4ffb9cc1760513897f010c67058b21800aa58b45b` | 32,287 | `0444` / 1 |
| tests | `7bc21953779b45147f34740d938336dde6e15ca2cedb009e21b83d12ffdcdb52` | 26,551 | `0444` / 1 |

The focused suite passes **32/32**, followed by five consecutive root-level
repeat loops.  The final generic-component audit is
`P0=0/P1=0/P2=2`.  The two P2 limitations are:

1. the caller must still authenticate executable/path bytes and directory
   freshness, close the path-validation-to-`Popen` race, and accept that a
   malicious descendant can escape the observed session/process group; and
2. a future production adapter must bind the operation model's exact phase
   limits and `global_deadline = phase_end - 10`,
   `cleanup_deadline = phase_end <= D_outer`.

This generic component is not the future probe and does not interpret a
gmpy2 payload.

## 6. Required next runtime layer

The required order remains:

```text
materialize and independently verify exact sealed root
  -> publish and independently validate the static inventory JSON
  -> freeze a small result-blind wrapper-import child
  -> run two fresh authority-bound observations under the generic supervisor
  -> freeze the parent probe and trusted origin classifier/adapter
  -> join the Round-182 AST resolver
  -> close actual six role-v3 sources plus the global runner
  -> create the final runtime_closure
```

Each future observation must bind a distinct nonce, run ordinal, pid, PGID,
SID, private stage, exact environment, import origins, wrapper and nested
extension, loaded-image delta, runtime metadata, exit state, pipe EOFs,
descendant absence, and cleanup receipt.  Static inventory A cannot substitute
for dynamic observation B, and A+B still cannot substitute for the final
source/runner closure.

## 7. Integrated ledger

At replay-readiness scope the ledger remains:

```text
P0 = 0
P1 = 2
P2 = 4
```

The two P1 blockers are:

1. no materialized sealed root, published authority receipt, result-blind
   child, authenticated runtime probe, or trusted origin classifier/adapter
   exists; and
2. no v3 precommit adapter or end-to-end actual closure over the six
   numerical role-v3 sources plus global runner exists.

The four P2 items remain the absent role-8 numerical pair, absent role-9
numerical pair, absent role-10 numerical pair/global runner, and absent
replay/acceptance/later-continuum evidence.

Final gate state:

```text
recommended external authority root              = ABSENT
persistent static inventory JSON                  = ABSENT
static inventory builder/validator                = FROZEN COMPONENT / 92 TESTS
generic process supervisor                        = FROZEN COMPONENT / 32 TESTS + 5 LOOPS
result-blind runtime child / authenticated probe  = ABSENT / ABSENT
trusted origin classifier/adapter                 = ABSENT
actual six-source-plus-runner runtime closure     = ABSENT
role-8/9 numerical implementations                = 0/4
all role-v3 numerical implementations             = 0/6
global runner                                     = ABSENT
plan / bundle / request / commitment              = ABSENT / ABSENT / ABSENT / ABSENT
execution / output / receipt / replay             = NONE / ABSENT / ABSENT / NOT PERFORMED
B06 structural remedy prepared / cleared          = FALSE / FALSE
same-member acceptance                            = FALSE
C1--C3 / F0--F3 / root transfer                   = FALSE
release / submission                              = FALSE
```
