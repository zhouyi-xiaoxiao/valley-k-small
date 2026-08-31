# Round 81 Stage-B-v5 T0 selector repair freeze

Date: 2026-07-14  
Status: **REPAIR-CANDIDATE / HOLD-INDEPENDENT-ATTACK**  
Scientific object/value/result: **NOT READ / NOT RUN / NOT CREATED**  
Authorization: **AUTHORIZED-SCIENTIFIC-COMMAND: NONE**

## 1. Decision

All Round-78 P0/P1/P2 findings are repaired in the science-free T0 package.
Five additional adversarial passes found and closed the unbounded runtime-root
shadowing path, critical-stdlib preload/replacement path, and production-record
path-alias path.  The repaired candidate has no open self-audit P0, P1, or P2.

This is not an independent acceptance and it is not a scientific GO.  The
candidate remains HOLD until a later result-blind attack accepts these exact
bytes and creates a distinct production external attestation with status
`INDEPENDENT-ATTACK-PASS`.

## 2. Frozen repair bytes

| role | path | SHA-256 |
|---|---|---|
| unique selector implementation | `code/positive_b_stage_b_t1_selector_v5.py` | `a4d6e933cdcb3e244afceaca8baece044f38ebf072e8f75c7c01fbf818bdde1a` |
| descriptor-first loader | `code/positive_b_stage_b_t0_verified_loader.py` | `66168e15ede42a6126280dea9f165e31a76529d74c17209cc2d1232322e507e0` |
| retired-name tombstone | `code/positive_b_stage_b_t0_selector.py` | `53d624310d808a82b52bb1c9f7b14405c2324c4c457e727739b1e1a92462d032` |
| isolated test runner | `code/run_stageb_t0_selector_tests_isolated.py` | `f1c498265452876d297ede317536ed9afae821efc0527470391bbedff1d5adb2` |
| primary synthetic tests | `code/test_positive_b_stage_b_t1_selector_v5.py` | `358cdb556794c85f08e08dd8c7d6f5ca9fdd650444c1de54db7f20496cc31035` |
| exploit regressions | `code/test_stageb_t0_selector_round78.py` | `4869aaad243f7f79b26e2a3d0ed406b12506a68b0cfb27b9ee4756213bf544bc` |
| wheel lock | `code/positive_b_stage_b_t0_requirements.lock` | `52f905ed765f2fa9422dd28e082b3abeb9e46c0b391b9fd6a9b32a5f2fc0a2a2` |
| runtime lock v2 | `code/positive_b_stage_b_t0_runtime_lock_v2.json` | `7321fb3ce442276f4b2ff1b7c6f58c844926fba63bcca2270e10e53fb5f44ecf` |
| non-promotable synthetic attestation | `code/positive_b_stage_b_t0_synthetic_test_attestation_v1.json` | `d478d9e4f2e249efec2dc554be3f98b9d460167f70d434dee8e2c638e0976018` |
| historical protocol v1 | `notes/positive_b_stage_b_t0_selector_protocol_v1.md` | `fedf5d77629f8764a970222421fc53b4b5392ae8be5df027c258fa120fd9eb34` |
| normative repair protocol v2 | `notes/positive_b_stage_b_t0_selector_protocol_v2.md` | `5046f9a3cceae5afd787962f81da70776f015f04f2607027befce1135dd0a57f` |
| v5 frozen-name bridge | `notes/positive_b_stage_b_t1_selector_protocol_v5.md` | `7232d5c9c0dc9f6bcd9e48a405004383f445d68905555b44ae7d9d38fb9091a6` |
| historical Round-75 record | `audits/round_75_stageb_t0_selector_build.md` | `66dff9711b9d3a19734884cc8a60eb323801fb9b480bc39980bc268f8e332952` |
| Round-78 attack | `audits/round_78_stageb_t0_selector_independent_attack.md` | `d8cb0a69739839fefe5a6a5a4c5226465dacf57cdabe3a820981ca44ade7c94f` |

The synthetic attestation is canonical ASCII JSON with a terminal LF.  Its
complete role set and every listed file hash were independently recomputed
after the final edits.  Its status is permanently
`NON-PROMOTABLE-SYNTHETIC-TEST`.

## 3. Round-78 issue closure

| finding | severity | repair | regression/evidence | state |
|---|---:|---|---|---|
| old T0 shim performed an unqualified import and allowed `PYTHONPATH`/`sys.modules` substitution | P0 | the v5 file is now the only substantive implementation; the old name is an `ImportError` tombstone; T1 must consume exact bytes through the authenticated loader | forged old-name module, fake v5 search path, occupied names, direct-import HOLD | CLOSED |
| fake gmpy2 wrapper could execute before provenance validation | P0 | loader hashes the exact complete package/library tree before absolute-spec import; source entry gate precedes gmpy2 and critical-stdlib imports | fake wrapper sentinel has zero execution; wrapper-export identity mutations HOLD | CLOSED |
| future T1 was not byte-bound to one implementation | P1 | future T1 pins the external record, authenticates exact loader bytes, and lets the loader derive the sole source hash from that record; output copies source/runtime/record provenance | wrong external pin, role/path swap, incomplete closure, duplicate path, source hash drift HOLD | CLOSED |
| executed native runtime was not recursively bound | P1 | package files, extension, all bundled dylibs, dependency lock, wrapper/native identities, and dyld's actual image set are exact-closed | extra package/library, fake export, empty dyld set, hash/version/origin drift HOLD | CLOSED |
| `exp_up64` could HOLD after extreme negative underflow | P1 | exact `x <= -1000` proof fixes endpoints to down=0, RN=0, up=`2^-1074` | `-1000`, `-1e20`, and negative max-finite pass all three directions | CLOSED |
| saved node IDs were incorrectly required to be consecutive | P2 | IDs are opaque unique uint64 identities; predecessor/successor are ordered-array neighbors | sparse `(10,20,30)` succeeds; duplicate/missing/end nodes still HOLD | CLOSED |
| Section-6 implementation scope was overstated | P2 | protocol now claims only the scalar/vector numerical predicate; object-level diagnostic/grid/topology/coverage compilation is explicitly separate and unfrozen | v2 Section 6 and v5 bridge | CLOSED |
| historical source-inspection wording was too absolute | P2 | Round-75 broad-search disclosure is retained; no absolute source-noninspection claim remains | v2 Section 7 | CLOSED |

## 4. Import, runtime, and trust boundary

The mandatory future-consumer chain is one-way:

```text
python -I -S
  -> descriptor/hash external production T0 record against the T1-frozen hash
  -> descriptor/hash the exact absolute loader bytes named by that record
  -> loader reconsumes canonical record and verifies full unique role/path closure
  -> descriptor/hash unique source and exact gmpy2 package/library closure
  -> absolute-spec gmpy2 import; runtime-site root is never added to sys.path
  -> private-name source execution
  -> wrapper/native identities, origins, exports, versions and dyld images
  -> output copies implementation/runtime/external-record attestation
```

Every nonempty `DYLD_*`, `LD_LIBRARY_PATH`, or `LD_PRELOAD` is rejected.
Preloaded `_ctypes`, `ctypes`, `ctypes._endian`, `platform`, or `sysconfig` is
rejected before record or runtime consumption.  Startup and every public byte
operation recheck the captured critical-module `sys.modules` identities,
canonical stdlib origins, and source/extension loader classes.  Tests also
place hostile top-level `platform.py`, `sysconfig.py`, `ctypes.py`, and a
sibling package in the declared runtime root; none executes because that root
is never inserted into `sys.path`.

Threat boundary: the invoked CPython executable, its standard library/import
machinery, and the OS loader/system libraries are an external bootstrap trust
base.  The T0 package does not claim universal `sys.modules` substitution
resistance or hash closure of that entire base.  It discloses the observed
executable, resolved executable, stdlib root, and five critical-module origins
in every output.  The observed candidate paths were:

```text
executable = /Users/ae23069/.local-build/valley-k-small/.venv/bin/python
resolved   = /opt/homebrew/Cellar/python@3.12/3.12.13/Frameworks/Python.framework/Versions/3.12/bin/python3.12
stdlib     = /opt/homebrew/Cellar/python@3.12/3.12.13/Frameworks/Python.framework/Versions/3.12/lib/python3.12
```

The exact runtime bytes include:

| item | SHA-256 |
|---|---|
| `gmpy2/__init__.py` | `3d4f21a0e9d6d32c935e3d39ef4be23a9a7d0ea56344ebbb0b8dca4f5651e8a2` |
| `gmpy2/gmpy2.cpython-312-darwin.so` | `9586b7c4b887704b57576f52b73a8c45437946d2b172095d82c20fa0871a415b` |
| `gmpy2.libs/libgmp.10.dylib` | `22cec4689e503d590cfbf3373ae7f442ef6d40c3e6c93a3612bbd1b7e2bce049` |
| `gmpy2.libs/libmpfr.6.dylib` | `d314a427a901f8ece38b67966cd2fbf5642ceb7d1c2e5136f8282ca7ab859aed` |
| `gmpy2.libs/libmpc.3.dylib` | `d3c10c39234c095f5c1938ad607c87a0633152f51271d9ed1c494724430c2b0c` |

The runtime lock also pins the complete package file set, including the one
`__pycache__` file and shipped headers.  `otool -L` recomputation gave the
frozen non-system graph:

```text
gmpy2 extension -> libmpc, libmpfr, libgmp
libmpc          -> libmpfr, libgmp
libmpfr         -> libgmp
libgmp          -> no bundled dependency
```

`/usr/lib/libSystem.B.dylib` is the explicit OS leaf.  Direct dyld enumeration
during every runtime attestation observed exactly the extension plus those
three bundled dylibs, with no extra numerical native image.

## 5. Arithmetic, IDs, and exact scope

For finite binary64 `x <= -1000`, the positive Taylor lower sum proves
`exp(0.7)>2`, so `ln(2)<0.7` and `exp(x)<2^-1075`.  Positivity and the
binary64 midpoint then prove, without an out-of-range MPFR call:

```text
exp_down64(x) = 0
exp_rn(x)     = 0
exp_up64(x)   = 2^-1074
```

Saved `acceptance_index` values are unique opaque uint64 identities.  Array
order, not integer arithmetic, defines the two adjacent saved nodes.

The package implements the object-free selector and role-radius algebra plus
the scalar/vector numerical odd-grid predicate.  It does not implement or
authorize the object-level diagnostic/grid/topology/coverage compiler, any
scientific producer, or any Stage-A/Stage-B execution.

Canonical normalized fixtures (only the copied external-record digest is
replaced by 64 zeroes) are:

| fixture | bytes | SHA-256 |
|---|---:|---|
| selector output v2 | 5517 | `429d6f9b0556644742a83c3368c01d8b61739126dbb3fe189f0acc897305ece2` |
| role-radius output v2 | 3879 | `11a1fb13134e314533dbf18c35f3ed69c9abf98b4e0d2a8030e401cea2f18e33` |

## 6. Verification ledger

No scientific object, saved scientific result, producer, manifest, mesh,
FV/off-lattice output, or manuscript evidence was opened or executed.
Synthetic payloads were hand-built in the test files.

1. Exact isolated package suite:

   ```text
   /Users/ae23069/.local-build/valley-k-small/.venv/bin/python -I -S \
     code/run_stageb_t0_selector_tests_isolated.py
   result: 49/49 PASS
   ```

2. Unchanged historical science-free design tests:

   ```text
   python -m pytest -q \
     code/test_stageb_v3_design_round67.py \
     code/test_stageb_v4_design_resolution.py \
     code/test_stageb_v4_design_round70.py \
     code/test_stageb_v5_design_resolution.py \
     code/test_stageb_v5_design_round73.py
   result: 33/33 PASS
   ```

3. Repaired-package quality checks:

   ```text
   ruff format --check [implementation loader tombstone runner primary exploit]
   result: 6 files already formatted
   ruff check [same six files]
   result: All checks passed
   python3 -m py_compile [same six files plus five historical tests]
   result: PASS
   ```

   The five historical test files remain byte-preserved evidence.  They were
   not mechanically reformatted; their tests and bytecode compilation pass.

4. Static source boundary check:

   ```text
   implementation: forbidden scientific imports = [] ; command main guard = false
   loader:         forbidden scientific imports = [] ; command main guard = false
   runner:         forbidden scientific imports = [] ; test-only main guard = true
   ```

Total science-free tests: **82/82 PASS**.

## 7. Five-pass adversarial self-audit

| pass | attack surface | outcome |
|---:|---|---|
| 1 | old-name, fake v5 path, `PYTHONPATH`, `sitecustomize`, occupied module names | no open P0/P1/P2 |
| 2 | wrapper, complete package, extension, recursive dylibs, dyld loaded images | no open P0/P1/P2 |
| 3 | hostile runtime-root modules, preloaded/post-start critical stdlib substitution, trust-base wording | no open P0/P1/P2 |
| 4 | extreme underflow, sparse IDs, JSON/schema and one-ULP mutations | no open P0/P1/P2 |
| 5 | external-record roles/unique paths/status, hash cycles, normalized fixtures, docs and scope claims | no open P0/P1/P2 |

Final self-audit ledger:

```text
P0 open = 0
P1 open = 0
P2 open = 0
release = HOLD-INDEPENDENT-ATTACK
scientific execution = NOT AUTHORIZED
AUTHORIZED-SCIENTIFIC-COMMAND: NONE
```

## 8. Required next action

A separate result-blind reviewer must attack these exact bytes.  Only after
acceptance may it create a distinct
`audits/round_*_stageb_t0_selector_independent_attack.md` and the canonical
production record `positive-b-stage-b-t0-external-attestation-v1` with status
`INDEPENDENT-ATTACK-PASS`.  That record must include this repair report as the
`round81_repair` role and the later report as the distinct
`independent_attack` role.  A future T1 must freeze the production-record hash
before consuming it.

Nothing in this report authorizes Stage A, Stage B, mesh-65/97, FV,
off-lattice, scientific manifest/result creation, release, or claim promotion.
