# Round 94: Stage-B-v5 T0 transient-wrapper race repair freeze

Date: 2026-07-14  
Status: **REPAIR CANDIDATE / HOLD-INDEPENDENT-ATTACK**  
Self-audit open findings: **P0 = 0, P1 = 0, P2 = 0**  
Scientific object/value/result status: **NOT READ / NOT RUN / NOT CREATED**  
Authorization: **AUTHORIZED-SCIENTIFIC-COMMAND: NONE**

## 1. Exact repair decision

Round 93 demonstrated that the old loader descriptor-hashed an authentic
`gmpy2/__init__.py`, then let a pathname-backed `SourceFileLoader` reopen and
execute a transient hostile replacement. The hostile wrapper restored the
authentic pathname before later checks, changed `exp_rn` to `42`, and returned
selected index `999` while the synthetic output still appeared verified.

This allocation removes that Python-wrapper pathname-execution gap. The
loader now retains the descriptor-read wrapper bytes, prepares the `gmpy2`
package and its already verified native submodule, and uses captured
`compile`/`exec` identities on the retained wrapper bytes in that package
namespace. The `SourceFileLoader` stored on the package spec is metadata only;
its `exec_module` is never called. The selector source is likewise compiled
and executed from its retained verified bytes under a fresh private name.

This is a bounded scientific-integrity repair, not an absolute security
claim. The native extension and its transitive libraries remain loaded by
absolute path. Their safe use relies on the explicit external trust contract
below.

## 2. Exact external trust contract

Every accepted v3 external record and every selector/radius output must carry
this exact mapping:

| field | exact value |
|---|---|
| `schema` | `positive-b-stage-b-t0-execution-trust-contract-v1` |
| `bootstrap_trust_base` | `CPYTHON-STDLIB-IMPORT-MACHINERY-OS-LOADER-SYSTEM-LIBRARIES` |
| `runtime_tree_concurrency` | `NO-HOSTILE-SAME-UID-WRITER-DURING-LOAD-AND-PUBLIC-CALLS` |
| `wrapper_execution` | `VERIFIED-DESCRIPTOR-SNAPSHOT-COMPILE-EXEC` |
| `native_image_execution` | `PATH-LOADED-UNDER-NO-HOSTILE-SAME-UID-WRITER-CONTRACT` |
| `protection_claim` | `DEFENSE-IN-DEPTH-NOT-CRYPTOGRAPHIC-IMMUTABILITY` |

The invoked CPython executable, builtins, standard library/import machinery,
OS loader and system libraries, plus absence of a hostile same-UID writer to
the attested runtime tree from verification through every public call, are
external assumptions. This freeze does **not** claim cryptographic
immutability, universal TOCTOU resistance, arbitrary same-process mutation
resistance, root-compromise resistance, or safety with a hostile concurrent
same-UID runtime-tree writer. If those assumptions are unacceptable, a future
consumer must HOLD or place the complete runtime behind an OS-enforced
read-only/different-UID boundary.

## 3. Repaired execution and identity-guard boundary

The isolated runner descriptor-reads and hash-matches the loader, then
executes the captured loader bytes with bootstrap-captured `compile` and
`exec`. Under `python -I -S`, the loader then performs:

```text
canonical external-record snapshot and exact role verification
  -> verified selector-source snapshot
  -> exact runtime-tree enumeration and descriptor snapshots
  -> retain authentic gmpy2/__init__.py bytes
  -> absolute-path load verified gmpy2.gmpy2 native extension
  -> compile+exec retained wrapper bytes in prepared package namespace
  -> compile+exec retained selector bytes under fresh private name
  -> startup/runtime/native-image attestation
  -> guarded public selector or role-radius call
```

Before wrapper execution, the guard captures and later rechecks:

- the `builtins` module plus `compile`, `exec`, `__import__`, and
  `__build_class__`;
- `_imp`, `importlib`, `importlib.machinery`, `importlib.util`,
  `_frozen_importlib`, and `_frozen_importlib_external`;
- `SourceFileLoader`, `ExtensionFileLoader`, `ModuleSpec`,
  `spec_from_file_location`, `module_from_spec`, `create_dynamic`, and
  `exec_dynamic`; and
- ordered `sys.meta_path`, `sys.path_hooks`, and `sys.path`.

Checks occur after record consumption and source/runtime snapshots, before and
after native/wrapper execution, before selector compile/exec, after selector
execution and post-load attestation, on every public byte-call entry,
immediately before output-byte construction, and before return. Identity drift
is HOLD; the mid-call regression proves no bytes are returned after a drift
detected between selection and output construction.

## 4. Mode, schema, and non-promotion closure

The exact record combinations are:

| record schema | status | output mode | `production_eligible` |
|---|---|---|---:|
| `positive-b-stage-b-t0-synthetic-test-attestation-v2` | `NON-PROMOTABLE-SYNTHETIC-TEST` | `VERIFIED-ISOLATED-SYNTHETIC-TEST` | `false` |
| `positive-b-stage-b-t0-external-attestation-v2` | `INDEPENDENT-ATTACK-PASS` | `VERIFIED-ISOLATED` | `true` |

Schema, status, mode, eligibility, external-record digest, and the exact trust
contract travel together into `package_runtime`. Missing/extra contract
fields and synthetic/production cross-products HOLD before runtime use. The
public output schemas are:

```text
positive-b-stage-b-t0-selector-output-v3
positive-b-stage-b-t0-role-radii-v3
```

No production record exists. A later production record must pin this Round-94
freeze and a distinct later independent PASS report. This repair candidate
cannot promote itself.

## 5. Frozen candidate allocation

| role | path | SHA-256 |
|---|---|---|
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

The historical synthetic v1 record remains byte-preserved evidence at
`d478d9e4f2e249efec2dc554be3f98b9d460167f70d434dee8e2c638e0976018`;
it is not accepted by the v3 loader.

## 6. Pin DAG and absence of a hash back-edge

The final cascade is one-way:

```text
selector source
  |---> normalized selector/radius fixture hashes ---> primary-test bytes
  `---> Round-78 expected implementation pin --------> Round-78-test bytes

loader + selector + tests + protocols + historical evidence + locks
  ---> synthetic v2 record
  ---> isolated-runner expected record digest

this Round-94 freeze
  ---> later independent attack report
  ---> later production record
  ---> future T1 exact production-record pin
```

The synthetic record does not pin itself or the isolated runner. The two
normalized fixtures replace only the copied external-record digest with 64
zeroes before hashing, so changing the record digest does not change the
fixture hashes. A second calculation after the final record/runner cascade
confirmed the same normalized bytes:

| normalized output | bytes | SHA-256 |
|---|---:|---|
| selector output v3 | 6688 | `ab4f95fec4ea085b91098604ca00c06d382e6b66913e183a7d7a9a14b1a236b6` |
| role-radius output v3 | 5050 | `44152197d5e0fd16b4d95778169126b00489587c2c5022fb5030a20015d848f9` |

## 7. Deterministic Round-93 replay result

The Round-94 regression copies the authentic runtime into a temporary root,
captures the authentic wrapper snapshot, then atomically replaces the wrapper
pathname with a hostile file that writes a sentinel, hijacks `builtins.exec`,
sets `exp_rn=42`, and forges selected index `999`. It loads through the
repaired path, restores the authentic pathname, executes the selector, and
calls the hand-built synthetic fixture.

The exact regression passed and proved:

```text
hostile-wrapper sentinel = ABSENT
exp_rn                    != 42
selected index            = 10 (not 999)
mode                      = VERIFIED-ISOLATED-SYNTHETIC-TEST
status                    = NON-PROMOTABLE-SYNTHETIC-TEST
production_eligible       = false
trust contract            = exact v1 mapping
```

A separate mid-call test changes `builtins.exec` after selection and before
output-byte construction. It receives guard HOLD and returns no bytes. These
are deterministic repair regressions under the declared external contract;
they do not claim protection against a hostile same-UID writer racing the
path-loaded native images.

## 8. Verification ledger

No scientific source, producer, saved object, manifest, mesh, FV/off-lattice
result, evidence object, or manuscript object was opened or executed. All
new executions used hand-built synthetic inputs or copied attested runtime
bytes.

1. Exact isolated package suite:

   ```text
   /Users/ae23069/.local-build/valley-k-small/.venv/bin/python -I -S \
     code/run_stageb_t0_selector_tests_isolated.py
   result: 54/54 PASS
   ```

2. Unchanged historical science-free design suites:

   ```text
   /Users/ae23069/.local-build/valley-k-small/.venv/bin/python -m pytest -q \
     code/test_stageb_v3_design_round67.py \
     code/test_stageb_v4_design_resolution.py \
     code/test_stageb_v4_design_round70.py \
     code/test_stageb_v5_design_resolution.py \
     code/test_stageb_v5_design_round73.py
   result: 33/33 PASS
   ```

3. Quality gates:

   ```text
   ruff format --check [7 package/runner/test Python files]
   result: 7 files already formatted

   ruff check [same 7 files]
   result: All checks passed

   python -m py_compile [same 7 files plus 5 historical design tests]
   result: PASS

   git diff --check [Round-94 allocation paths]
   result: PASS
   ```

Total science-free regression result: **87/87 PASS**.

## 9. Freeze boundary and next gate

The Round-93 Python-wrapper P0 is repaired in this candidate allocation. This
is an implementer self-audit, not independent acceptance. The independent
reviewer must attack the exact hashes above, including a real transient
wrapper swap/restore, builtins/import identity drift, schema-mode cross
products, native/package closure, and the stated trust/nonclaim boundary.

Until that distinct result-blind review reports PASS:

```text
repair self-status          = CANDIDATE
independent acceptance      = HOLD
production external record = MUST NOT BE CREATED
future T1 promotion         = HOLD
scientific execution        = NOT AUTHORIZED
AUTHORIZED-SCIENTIFIC-COMMAND: NONE
```
