# Round 93: independent attack on the repaired Stage-B-v5 T0 selector

Date: 2026-07-14  
Reviewer: independent result-blind attacker (not the Round-81 implementer)  
Decision: **REJECT / HOLD-REPAIR**  
Open findings: **P0 = 1, P1 = 0, P2 = 0**  
Scientific object/value/result status: **NOT READ / NOT RUN / NOT CREATED**  
Authorization: **AUTHORIZED-SCIENTIFIC-COMMAND: NONE**

## 1. Frozen allocation and independence

I waited for the explicit Round-81 freeze and attacked only the following
bytes.  I did not edit any implementation, loader, test, protocol, runtime
lock, or scientific object.

| role | path | independently recomputed SHA-256 |
|---|---|---|
| repair freeze | `audits/round_81_stageb_t0_selector_repair_freeze.md` | `a59794fca10f1c0c8a5ef8e5d01c1e650cd66a4e825ecd55d96de8037af1f947` |
| unique selector | `code/positive_b_stage_b_t1_selector_v5.py` | `a4d6e933cdcb3e244afceaca8baece044f38ebf072e8f75c7c01fbf818bdde1a` |
| verified loader | `code/positive_b_stage_b_t0_verified_loader.py` | `66168e15ede42a6126280dea9f165e31a76529d74c17209cc2d1232322e507e0` |
| old-name tombstone | `code/positive_b_stage_b_t0_selector.py` | `53d624310d808a82b52bb1c9f7b14405c2324c4c457e727739b1e1a92462d032` |
| isolated runner | `code/run_stageb_t0_selector_tests_isolated.py` | `f1c498265452876d297ede317536ed9afae821efc0527470391bbedff1d5adb2` |
| primary tests | `code/test_positive_b_stage_b_t1_selector_v5.py` | `358cdb556794c85f08e08dd8c7d6f5ca9fdd650444c1de54db7f20496cc31035` |
| exploit tests | `code/test_stageb_t0_selector_round78.py` | `4869aaad243f7f79b26e2a3d0ed406b12506a68b0cfb27b9ee4756213bf544bc` |
| synthetic record | `code/positive_b_stage_b_t0_synthetic_test_attestation_v1.json` | `d478d9e4f2e249efec2dc554be3f98b9d460167f70d434dee8e2c638e0976018` |
| protocol v2 | `notes/positive_b_stage_b_t0_selector_protocol_v2.md` | `5046f9a3cceae5afd787962f81da70776f015f04f2607027befce1135dd0a57f` |
| v5 bridge | `notes/positive_b_stage_b_t1_selector_protocol_v5.md` | `7232d5c9c0dc9f6bcd9e48a405004383f445d68905555b44ae7d9d38fb9091a6` |

The exact isolated suite still reports **49/49 PASS**, and the five historical
science-free design suites still report **33/33 PASS**.  Those green results
are real, but they do not exercise an active writer between path hashing and
path reopening.

## 2. [P0] A same-UID transient writer can execute an unverified wrapper,
pass every post-load attestation, and change selector output

### 2.1 Root cause

The loader verifies `gmpy2/__init__.py` by descriptor at
`positive_b_stage_b_t0_verified_loader.py:273-278`, then verifies the remaining
package files and bundled libraries.  It later constructs a path-backed
`SourceFileLoader` and reopens the wrapper by pathname at lines 293-304.  The
verified descriptor/bytes are neither retained nor used for execution.

This leaves a real hash-to-execution time-of-check/time-of-use interval:

```text
descriptor read authentic wrapper -> SHA PASS
  ... verify other package files and dylibs ...
pathname reopen by SourceFileLoader -> execute whatever occupies that path now
```

The source's startup rehash at
`positive_b_stage_b_t1_selector_v5.py:599-757` occurs only after wrapper code
has executed.  Restoring the authentic pathname before that rehash makes the
postcheck observe authentic bytes.  Dyld's exact image set does not reveal
Python wrapper code that already ran, and wrapper/native export identity checks
do not undo arbitrary Python execution.

The declared runtime is not immutable: its package and library directories are
owned and writable by `ae23069` (`drwxr-xr-x`, owner `ae23069`).  Therefore a
second process under the same UID can atomically replace directory entries.

### 2.2 Real external race, no loader monkeypatch

I copied only the authentic frozen `gmpy2` and `gmpy2.libs` trees into a
canonical `/private/tmp` runtime and created a canonical synthetic record for
that absolute root.  The attack used a separate external process; it did not
patch the loader, source, import machinery, or scientific data.

The attack sequence was:

1. start the exact loader under the pinned CPython with `-I -S`;
2. leave the authentic wrapper in place through its descriptor hash;
3. atomically replace only `gmpy2/__init__.py` during the later verification
   window;
4. let the hostile wrapper write a sentinel, import the authentic extension,
   and temporarily intercept `builtins.exec`;
5. on seeing the sentinel, immediately restore the authentic wrapper inode;
6. after the exact selector source finishes, replace two public functions in
   the in-memory selector module; and
7. call both post-load attestation and the hand-built selector fixture.

The first two timing probes, at 1 ms and 2 ms, were correctly rejected as
early static drift.  The third probe, at 4 ms, hit the post-hash/pre-import
window and produced:

```text
LOAD_SUCCESS 901897167
EXP_RN 42.0
POST_ATTEST VERIFIED-ISOLATED-SYNTHETIC-TEST
SELECTED_INDEX 999
OUTPUT_MODE VERIFIED-ISOLATED-SYNTHETIC-TEST
ACCEPTED_TAMPERED_SELECTOR_OUTPUT
```

`999` is absent from the hand-built selector input; the authentic result is
index `10`.  The malicious wrapper first called the authentic public selector,
which repeated the package/runtime checks and created a valid embedded
`package_runtime`, and only then changed the selected index and re-canonicalized
the JSON.  Thus this is not merely code execution followed by a final HOLD.  A
wrong public selector result was returned after successful post-attestation,
while the output still carried the verified entry mode and exact external
record digest.

The temporary result-blind harness SHA-256 was
`fbcb07592faf244a186897af6c87c8bcc2b812e2dfd6aa86325a678d2520d5d8`.
It created and mutated only temporary synthetic fixtures.  No production
attestation and no scientific object were used.

### 2.3 Production impact and exact threat distinction

The demonstrated record was deliberately synthetic, so the experiment itself
did **not** claim or simulate a production acceptance.  Nevertheless the race
is after `_consume_external_attestation` and inside the same
`_verify_runtime_tree` call for both entry modes.  There is no production-only
immutable-runtime step.  Therefore a future production record would enter the
same vulnerable path; only the injected mode string would differ.

The implementation does successfully defeat:

- persistent/static file mutation;
- a replacement that overlaps a descriptor read;
- ordinary `PYTHONPATH`, `sitecustomize`, and `sys.modules` substitution;
- unlisted package, pycache, or library entries; and
- symlinks and post-start substitutions that remain visible at recheck time.

It does **not** defeat a hostile same-UID writer that replaces a pathname only
after its hash and restores it before the postcheck.  Round 81 discloses CPython,
stdlib/import machinery, and OS-loader trust, but it does not exclude an active
writer for the attested runtime tree.  Its stronger statements that the
executed runtime bytes are closed, that a fake wrapper has zero execution, and
that a pre-hashed file which was not loaded cannot pass are therefore false
under the stated boundary.

### 2.4 Required repair boundary

Adding another before/after hash is not a complete repair.  An active writer
can race any finite sequence of pathname checks and restore the authentic
entry for the final observation.  Advisory locks are also insufficient against
a hostile writer that ignores them.

A real defense must bind execution to immutable/authenticated bytes for the
entire load and use interval.  At minimum:

- execute the Python wrapper from the already verified byte snapshot, not by
  reopening its path;
- recognize that the native extension and its transitive dylibs are still
  path-loaded and require an OS-enforced immutable namespace;
- run from a root-owned read-only/immutable mount, sealed snapshot, codesigned
  artifact with enforcement, or a different-UID/sandbox boundary that prevents
  rename/write/link operations for the complete lifetime; and
- make the future T1 bootstrap execute the verified loader bytes directly or
  place the loader itself under the same immutable boundary.  Hashing a loader
  path and then reopening it repeats this defect one level earlier.

If the project instead chooses to exclude hostile same-UID concurrent writers,
that exclusion must be explicit in every provenance and zero-execution claim,
and the writable user-owned venv cannot be described as cryptographically
closing the bytes actually executed.  Such wording would narrow the claim; it
would not supply the stronger protection currently asserted.

## 3. Remaining independent attack matrix

A separate temporary matrix harness
(`954232a9258670b1208f66e5f787dc272877bb5f3991e9c030792b609aa4c74b`)
ran **57/57 PASS** synthetic/static checks in fresh `-I -S` children:

| surface | independent result |
|---|---|
| external record | wrong pin, noncanonical bytes, authorization/status drift, missing/extra roles, role/path swap, duplicate path, absolute/`..` path all HOLD |
| production shape | missing `round81_repair`/`independent_attack`, invalid independent-report pattern, and reused historical report path HOLD |
| non-promotion | synthetic status promotion HOLD; output copies exact synthetic record digest and mode `VERIFIED-ISOLATED-SYNTHETIC-TEST` |
| imports | direct source import HOLDs before `gmpy2`; fake `PYTHONPATH` loader and hostile runtime-root top-level modules have zero execution |
| module state | occupied old/v5/private names and preloaded `gmpy2`/`gmpy2.*` HOLD |
| critical stdlib | all five names (`_ctypes`, `ctypes`, `ctypes._endian`, `platform`, `sysconfig`) HOLD both pre-start and after substitution |
| runtime closure | extra/deleted/mutated package, pycache, extension, header, library entries HOLD |
| symlinks | runtime component, package root, pycache, wrapper, extension, library root, and individual library HOLD |
| actual dyld set | exactly extension plus `libgmp.10.dylib`, `libmpc.3.dylib`, and `libmpfr.6.dylib` |
| extreme `exp` | `-1000`, adjacent binary64 values, `-1e20`, and negative max finite give down/RN `0`, up `2^-1074`; NaN/`-inf` HOLD |
| sparse IDs | nonmonotone `(2^63, 2^64-1, 0)` uses array neighbors; negative, overflow, and Boolean IDs HOLD |
| Section 6 | implementation remains scalar/vector odd-grid only; object-level compiler remains explicitly unfrozen |
| no-science boundary | implementation/loader have no scientific imports or command main; no production record or future T1 consumer exists |

The broader hostile runtime root contained `hashlib.py`, `json.py`,
`pathlib.py`, `fractions.py`, `math.py`, `_ctypes.py`, `ctypes.py`, `platform.py`,
and `sysconfig.py`; all nine sentinels remained absent.  This confirms that the
runtime root is not inserted into `sys.path`.  It does not mitigate the P0,
which attacks the one wrapper path the loader intentionally reopens.

## 4. Production record, role completeness, and hash-cycle audit

The production schema correctly requires the 15 common roles plus distinct
`round81_repair` and `independent_attack` roles, exact common paths, the exact
Round-81 path, a constrained later independent-report filename, unique paths,
canonical bytes, status `INDEPENDENT-ATTACK-PASS`, and authorization `NONE`.
Malformed production-shaped records failed closed in the matrix.

No canonical production record exists, and none was created in this round.
That is the only valid state after a P0 rejection.  In particular, this report
must **not** be cited by a record whose status says `INDEPENDENT-ATTACK-PASS`.

The intended graph is acyclic:

```text
Round-81 repair -> frozen package bytes
this independent report -> Round-81 frozen bytes and attack result
later production record -> Round-81 report + accepted independent report
future T1 -> exact production-record hash
```

The independent report need not and must not pin the later record hash.  A
future T1 can freeze that hash after record creation.  The normalized fixture's
replacement of only the copied record digest is likewise non-cyclic.  The
cycle design is sound, but the record cannot be created until a repaired byte
allocation receives a new independent PASS.

The future-T1 loader-hash rule is currently protocol text only: no future T1
consumer exists to execute it.  That absence is not counted as a new defect at
this pre-T1 stage, but the eventual consumer must avoid a hash-then-path-exec
race for the loader itself.

## 5. Verification commands and final ledger

```text
/Users/ae23069/.local-build/valley-k-small/.venv/bin/python -I -S \
  code/run_stageb_t0_selector_tests_isolated.py
result: 49/49 PASS

../../../.venv/bin/python -m pytest -q \
  code/test_stageb_v3_design_round67.py \
  code/test_stageb_v4_design_resolution.py \
  code/test_stageb_v4_design_round70.py \
  code/test_stageb_v5_design_resolution.py \
  code/test_stageb_v5_design_round73.py
result: 33/33 PASS

python3 /tmp/stageb_independent_matrix.py
result: 57/57 PASS

python3 /tmp/stageb_timed_race_attack.py
result: accepted tampered selector output on third probe
```

Final independent ledger:

```text
P0 open = 1  (active-writer hash-to-import TOCTOU)
P1 open = 0
P2 open = 0
independent acceptance = REJECT
production external attestation = MUST NOT BE CREATED
future T1 promotion = HOLD
scientific execution = NOT AUTHORIZED
AUTHORIZED-SCIENTIFIC-COMMAND: NONE
```

This report is evidence of a failed independent attack gate, not an acceptance
artifact.  A repaired loader/runtime boundary requires a new freeze and a new
independent attack against the exact replacement bytes.
