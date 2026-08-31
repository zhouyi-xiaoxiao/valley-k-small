# Round 95: independent attack on the Round-94 Stage-B-v5 T0 repair

Date: 2026-07-14  
Reviewer: independent result-blind attacker (not the Round-94 implementer)  
Decision: **ACCEPT / INDEPENDENT-ATTACK-PASS**  
Open findings: **P0 = 0, P1 = 0, P2 = 0**  
Scientific object/value/result status: **NOT READ / NOT RUN / NOT CREATED**  
Authorization: **AUTHORIZED-SCIENTIFIC-COMMAND: NONE**

## 1. Frozen allocation and independence

I attacked only the exact Round-94 repair allocation. I did not edit the
loader, selector, runner, tests, protocols, locks, historical evidence, or any
scientific object. All adversarial files and runtime copies lived under
`/private/tmp`; no production attestation was created.

| role | path | independently recomputed SHA-256 |
|---|---|---|
| repair freeze | `audits/round_94_stageb_t0_selector_race_repair_freeze.md` | `72ae06c1e048a01e8724721b28830965599c60c0165c5dbbcce218932e85bd27` |
| verified loader | `code/positive_b_stage_b_t0_verified_loader.py` | `9a3cd379f4a19c5b0cf6317d9e3bfbfd39bf6914714de7fb014754a4d0ca4cad` |
| unique selector | `code/positive_b_stage_b_t1_selector_v5.py` | `c7344bb8d6818f609c57614dd0d500c75fcc2229606865b1d9a4d05bc94cecfc` |
| old-name tombstone | `code/positive_b_stage_b_t0_selector.py` | `53d624310d808a82b52bb1c9f7b14405c2324c4c457e727739b1e1a92462d032` |
| isolated runner | `code/run_stageb_t0_selector_tests_isolated.py` | `2bd61c2e2cbe8b4f04ccb535a18fa56e6b1b37b0ed4c5eed3044c569a9add319` |
| primary tests | `code/test_positive_b_stage_b_t1_selector_v5.py` | `8ac8a27c603e64af3467ed1784b947fe3bfbb117b6ea0ca3dad2f533eb901aa8` |
| Round-78 regressions | `code/test_stageb_t0_selector_round78.py` | `0df1a964d226933165d7346b5b1b2bc8be0dc96a0f55630fceba99e2469bd3fe` |
| Round-94 regressions | `code/test_stageb_t0_selector_round94.py` | `e6f81b8d4de11d0d0d4f7401d6412c51ea82c21d2465ec2f29668b4144db4563` |
| synthetic v2 record | `code/positive_b_stage_b_t0_synthetic_test_attestation_v2.json` | `a7978c22d7ee39111d042edc918c1149f4a985d995fb24491cc6dcb2497e5c80` |
| protocol v3 | `notes/positive_b_stage_b_t0_selector_protocol_v3.md` | `8c60e6ec3254df0abdbc1644e5ed765e644f79b1e2a72ac1d2d1a15dc0a1b13b` |
| v5 bridge | `notes/positive_b_stage_b_t1_selector_protocol_v5.md` | `3f2c884db3fbb96741a12e19b49b7c5df7034dc0b8d9ef9c42e04aa736350132` |
| requirements lock | `code/positive_b_stage_b_t0_requirements.lock` | `52f905ed765f2fa9422dd28e082b3abeb9e46c0b391b9fd6a9b32a5f2fc0a2a2` |
| runtime lock | `code/positive_b_stage_b_t0_runtime_lock_v2.json` | `7321fb3ce442276f4b2ff1b7c6f58c844926fba63bcca2270e10e53fb5f44ecf` |
| design v4 | `notes/positive_b_stage_b_validation_design_v4.md` | `e5ca55c8a63d72b8f1bb0ded4d6ebba29a75d94e96ce07a6b7ebf15dcf100691` |
| design v5 | `notes/positive_b_stage_b_validation_design_v5.md` | `136085075ad23fc22a40cf03725c9151f11ff356cff4f6f39e5c5fbb24317ddd` |
| Round-73 attack | `audits/round_73_stageb_v5_independent_attack.md` | `36c0f502b90cb98e8cdeedd5a1621b0ffa1e3bcc5bc49b5490d1eccde9e7dcf8` |
| Round-75 build | `audits/round_75_stageb_t0_selector_build.md` | `66dff9711b9d3a19734884cc8a60eb323801fb9b480bc39980bc268f8e332952` |
| Round-78 attack | `audits/round_78_stageb_t0_selector_independent_attack.md` | `d8cb0a69739839fefe5a6a5a4c5226465dacf57cdabe3a820981ca44ade7c94f` |
| Round-81 repair | `audits/round_81_stageb_t0_selector_repair_freeze.md` | `a59794fca10f1c0c8a5ef8e5d01c1e650cd66a4e825ecd55d96de8037af1f947` |
| Round-93 rejection | `audits/round_93_stageb_t0_selector_independent_attack.md` | `52e3cb4249ff85b6634aa509a4a1431cadf3ed9e4fa3b6a5b7f2de04d8a16e20` |
| protocol v1, historical | `notes/positive_b_stage_b_t0_selector_protocol_v1.md` | `fedf5d77629f8764a970222421fc53b4b5392ae8be5df027c258fa120fd9eb34` |
| protocol v2, historical | `notes/positive_b_stage_b_t0_selector_protocol_v2.md` | `5046f9a3cceae5afd787962f81da70776f015f04f2607027befce1135dd0a57f` |

Every recomputed digest matched the Round-94 freeze. The exact isolated suite
reported **54/54 PASS**, and the five historical science-free design suites
reported **33/33 PASS** before the independent attacks.

## 2. Round-93 real-race replay against the repaired wrapper boundary

I built a fresh canonical synthetic-v2 record pointing at copied authentic
`gmpy2` and `gmpy2.libs` trees under `/private/tmp`. A separate parent process
atomically replaced only `gmpy2/__init__.py` with the Round-93-style hostile
wrapper for short intervals. The hostile file would:

- write a sentinel immediately if executed;
- intercept `builtins.exec`;
- replace `exp_rn` with a function returning `42`; and
- forge selected index `999` after calling the authentic selector.

The child descriptor-read and hash-matched the exact loader, executed the
captured loader bytes with captured `compile`/`exec`, and invoked the exact
public selector on the hand-built synthetic fixture. I swept delays from
0 to 12 ms and hostile residence times from 0.25 to 3 ms, including a dense
set around the old approximately 4 ms exploit window.

Result over **60 independent process attempts**:

```text
correct successful loads = 40
fail-closed HOLDs        = 20
invalid successes        = 0
hostile sentinel writes  = 0
sentinel bytes            = empty
```

Every successful load returned index `10`, never `999`; `exp_rn(1.0)` was
never `42`; and the output carried exactly:

```text
schema              = positive-b-stage-b-t0-synthetic-test-attestation-v2
status              = NON-PROMOTABLE-SYNTHETIC-TEST
mode                = VERIFIED-ISOLATED-SYNTHETIC-TEST
production_eligible = false
```

The trust-contract mapping was also byte-for-value exact. A swap that was
visible to a verification or public-call recheck HOLDed; a swap after the
authentic wrapper snapshot could not change the retained bytes later compiled
and executed. Thus the specific Round-93 hash-to-path-reopen P0 is closed.

This stronger wrapper result does not convert the path-loaded native extension
or dylibs into immutable bytes. I did not race those native paths because the
accepted contract explicitly excludes a hostile same-UID runtime-tree writer
during load and public calls.

## 3. Captured loader bootstrap and runtime identity guard

### 3.1 Deterministic loader bootstrap replay

In a fresh `-I -S` child I descriptor-captured an exact temporary copy of the
loader, verified SHA-256
`9a3cd379f4a19c5b0cf6317d9e3bfbfd39bf6914714de7fb014754a4d0ca4cad`,
atomically replaced its pathname with a hostile sentinel writer, and then
compiled/executed only the retained bytes with bootstrap-captured
`builtins.compile` and `builtins.exec`.

```text
BOOTSTRAP 9a3cd379f4a19c5b0cf6317d9e3bfbfd39bf6914714de7fb014754a4d0ca4cad False True
```

`False` is the hostile sentinel state; `True` confirms the captured module
exposed the authentic `load_frozen_selector`. This closes the loader-level
hash-then-path-exec replay for the isolated runner and matches the future-T1
bootstrap rule in the v5 bridge.

### 3.2 Identity attacks

I changed one guarded identity at a time, restored it, and proved the restored
baseline still passed. The 21 mutation classes were:

- seven `sys.modules` identities: `builtins`, `_imp`, `importlib`,
  `importlib.machinery`, `importlib.util`, `_frozen_importlib`, and
  `_frozen_importlib_external`;
- four builtins: `__build_class__`, `__import__`, `compile`, and `exec`;
- seven import functions/classes: `_imp.create_dynamic`, `_imp.exec_dynamic`,
  `ExtensionFileLoader`, `ModuleSpec`, `SourceFileLoader`,
  `module_from_spec`, and `spec_from_file_location`; and
- ordered `sys.meta_path`, `sys.path_hooks`, and `sys.path`.

All **21/21** direct guard attacks HOLDed and all **21/21** attacks through the
public byte-output entry HOLDed before output. Every restored identity then
passed. A separate mid-call attack changed `builtins.exec` only after authentic
selection; the pre-output guard HOLDed, returned no bytes, and the restored
selector again returned index `10`.

These checks establish the exact identities claimed by the implementation.
They do not claim protection against arbitrary mutation of internal objects or
methods while preserving the guarded top-level identities; arbitrary
same-process mutation is outside the disclosed trust boundary.

## 4. Independent 66-check static and synthetic matrix

A separate matrix ran **66/66 PASS** checks in fresh `-I -S` children:

| surface | independent result |
|---|---|
| external record | wrong external pin, noncanonical bytes, authorization/status/schema drift, missing/extra roles, duplicate paths, role/path swap, absolute paths, and `..` paths all HOLD |
| production shape | missing `round94_repair`/`independent_attack`, wrong Round-94 path, invalid independent-report filename, and reuse of Round-93/historical paths all HOLD |
| trust contract | missing/extra fields and one-at-a-time drift of all six exact fields HOLD before runtime use |
| non-promotion | synthetic promotion HOLDs; accepted synthetic output copies the exact v2 schema, status, mode, eligibility, digest, and trust mapping |
| import boundary | direct source import, occupied public/private names, preloaded `gmpy2`/`gmpy2.*`, and all five critical stdlib preloads HOLD |
| hostile search roots | runtime-root and `PYTHONPATH` sentinels execute zero code |
| package/native closure | extra/deleted/mutated package, pycache, wrapper, extension, header, library entries, and all tested symlinks HOLD |
| post-start identities | substitutions for `_ctypes`, `ctypes`, `ctypes._endian`, `platform`, and `sysconfig` all HOLD |
| actual dyld set | exactly `gmpy2.cpython-312-darwin.so`, `libgmp.10.dylib`, `libmpc.3.dylib`, and `libmpfr.6.dylib` |
| extreme `exp` | directed endpoints at `-1000` and its neighbors, `-1e20`, and negative max finite are correct; NaN and `-inf` HOLD |
| sparse IDs | nonmonotone `(2^63, 2^64-1, 0)` uses array neighbors; negative, overflow, and Boolean IDs HOLD |
| Section 6 | implementation remains scalar/vector odd-grid only; object-level compiler remains explicitly excluded |
| no-science/history | loader and selector have no scientific imports or command main; no production record or future-T1 consumer exists |

The exact output trust mapping was:

```text
schema                 = positive-b-stage-b-t0-execution-trust-contract-v1
bootstrap_trust_base   = CPYTHON-STDLIB-IMPORT-MACHINERY-OS-LOADER-SYSTEM-LIBRARIES
runtime_tree_concurrency = NO-HOSTILE-SAME-UID-WRITER-DURING-LOAD-AND-PUBLIC-CALLS
wrapper_execution      = VERIFIED-DESCRIPTOR-SNAPSHOT-COMPILE-EXEC
native_image_execution = PATH-LOADED-UNDER-NO-HOSTILE-SAME-UID-WRITER-CONTRACT
protection_claim       = DEFENSE-IN-DEPTH-NOT-CRYPTOGRAPHIC-IMMUTABILITY
```

The loader, selector, synthetic record, protocol v3, Round-94 freeze, and
observed public output agree on this mapping. The v5 bridge carries the same
boundary and requires a future T1 to execute retained verified loader bytes.

## 5. Native-load and nonclaim boundary

The native extension and three bundled dylibs are still loaded by verified
absolute paths. The package closure, file hashes, symlink rejection, loaded
image set, MPFR runtime checks, and before/after identity guards provide
defense in depth. They do not make those path-loaded images cryptographically
immutable against a hostile concurrent writer.

Acceptance therefore means exactly:

```text
Python wrapper: retained authenticated descriptor bytes are compiled/executed
native images: verified path load under the no-hostile-same-UID-writer contract
bootstrap: trusted CPython/builtins/stdlib/import machinery/OS loader/system libs
protection level: defense in depth, not cryptographic immutability
```

The documents explicitly exclude arbitrary same-process mutation, root
compromise, a hostile same-UID native-path writer, and an OS-enforced
immutability claim. I found no place where the loader, protocol, output, or
future-T1 bridge silently upgrades this boundary.

## 6. Production shape, pin DAG, and next gate

The production-v2 schema requires the exact 19 common roles plus distinct
`round94_repair` and `independent_attack` roles, canonical unique paths and
bytes, status `INDEPENDENT-ATTACK-PASS`, authorization `NONE`, and the exact
trust mapping. This report's path satisfies the constrained later-independent
filename rule. No production record exists, and this review did not create
one.

The graph remains acyclic:

```text
Round-94 frozen allocation
  -> this Round-95 independent PASS report
  -> later production-v2 record pinning both exact report hashes
  -> future T1 pinning the exact production-record hash
```

The synthetic record does not pin itself or the isolated runner; normalized
fixtures zero only the copied external-record digest. No back-edge from this
report to a later production record is required.

With this independent PASS frozen, a later builder is now eligible to create
the canonical production attestation that pins the exact Round-94 and Round-95
hashes. That record must still pass its own exact loader consumption before
any future T1 promotion. This report is not itself a production record and
does not authorize scientific execution.

## 7. Verification commands and final ledger

```text
/Users/ae23069/.local-build/valley-k-small/.venv/bin/python -I -S \
  code/run_stageb_t0_selector_tests_isolated.py
result: 54/54 PASS

/Users/ae23069/.local-build/valley-k-small/.venv/bin/python -m pytest -q \
  code/test_stageb_v3_design_round67.py \
  code/test_stageb_v4_design_resolution.py \
  code/test_stageb_v4_design_round70.py \
  code/test_stageb_v5_design_resolution.py \
  code/test_stageb_v5_design_round73.py
result: 33/33 PASS

python3 /tmp/stageb_independent_matrix.py
result: 66/66 PASS
harness SHA-256: 61c437609a144fe6cee3c2dbf8761967825d99d555e16da1f6e6fec34ca34c17

python3 /tmp/stageb_round94_real_race.py
result: 60/60 safe outcomes; 40 correct success, 20 HOLD, sentinel 0
harness SHA-256: 574a69964ab9bd91e85f4ea70e724a5accb518499b6286343fabca7a661d5a3a

python3 /tmp/stageb_round94_guard_attack.py
result: captured-loader 1/1; identity 42/42; mid-call 1/1 PASS
harness SHA-256: 5b4e087afc93de0a1cc62239a8313570cdfb26ff37a7b2b32385fdb5625c41a5
```

Total independently observed science-free checks/probes:

```text
isolated package suite       54
historical design suites     33
independent matrix           66
real timed race attempts     60
identity mutations           42
captured-loader replay        1
mid-call no-output attack     1
total                       257
```

Final independent ledger:

```text
P0 open = 0
P1 open = 0
P2 open = 0
Round-93 wrapper P0 = CLOSED under and beyond the wrapper-specific contract
independent acceptance = INDEPENDENT-ATTACK-PASS
production external attestation = ELIGIBLE FOR LATER CREATION; NOT CREATED HERE
future T1 promotion = WAIT FOR EXACT PRODUCTION-RECORD PIN
scientific execution = NOT AUTHORIZED
AUTHORIZED-SCIENTIFIC-COMMAND: NONE
```
