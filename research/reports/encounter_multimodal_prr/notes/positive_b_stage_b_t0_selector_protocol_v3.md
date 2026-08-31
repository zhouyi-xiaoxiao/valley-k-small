# Stage-B-v5 T0 selector protocol v3: captured-wrapper execution boundary

Date: 2026-07-14  
Status: **ROUND-94 REPAIR CANDIDATE / HOLD-INDEPENDENT-ATTACK**  
Authorization: **AUTHORIZED-SCIENTIFIC-COMMAND: NONE**

## 1. Reason for v3 and exact nonclaim

Round 93 demonstrated a real same-UID race in v2: the loader descriptor-hashed
the authentic `gmpy2/__init__.py`, later let a `SourceFileLoader` reopen that
pathname, and then accepted a restored authentic path after hostile wrapper
code had executed. The reproduced code changed `exp_rn` to `42` and returned
selected index `999` under a verified synthetic output.

V3 removes that Python-wrapper pathname reopen. It does not pretend to build
an impossible same-UID security boundary around a user-owned Python runtime.
The native extension and its transitive dynamic libraries remain path-loaded.
Their safety depends on the exact external trust contract in Section 2.

No claim of cryptographic executed-byte immutability, universal TOCTOU
resistance, arbitrary same-process mutation resistance, root compromise
resistance, or hostile same-UID concurrent-writer resistance is made.

## 2. Executable trust contract, pinned as data

Every accepted external record and every selector/radius output carries this
exact mapping:

```text
schema =
  positive-b-stage-b-t0-execution-trust-contract-v1
bootstrap_trust_base =
  CPYTHON-STDLIB-IMPORT-MACHINERY-OS-LOADER-SYSTEM-LIBRARIES
runtime_tree_concurrency =
  NO-HOSTILE-SAME-UID-WRITER-DURING-LOAD-AND-PUBLIC-CALLS
wrapper_execution =
  VERIFIED-DESCRIPTOR-SNAPSHOT-COMPILE-EXEC
native_image_execution =
  PATH-LOADED-UNDER-NO-HOSTILE-SAME-UID-WRITER-CONTRACT
protection_claim =
  DEFENSE-IN-DEPTH-NOT-CRYPTOGRAPHIC-IMMUTABILITY
```

The loader rejects any missing, additional, or changed trust-contract field.
The selector independently compares the injected contract with the same exact
mapping. The output copies it as `package_runtime.trust_contract`. A future T1
must compare that output field, not merely cite this protocol.

The invoked CPython executable, its builtins, standard library and import
machinery, the OS loader/system libraries, and absence of a malicious same-UID
writer for the attested runtime tree from initial verification through every
public selector/radius call are therefore external scientific-integrity
assumptions. If that assumption is not operationally acceptable, T1 must HOLD
or move the complete runtime to an OS-enforced immutable/different-UID
boundary; additional pathname hashes are not a substitute.

## 3. Mandatory captured-byte load order

Future T1 must execute the already descriptor-read and hash-matched loader
bytes with captured `compile` and `exec`; it must not hash a loader path and
then ask a pathname-backed loader to reopen it. Under `python -I -S`, the
loader performs exactly:

```text
consume descriptor-captured loader bytes
  -> capture critical builtins/import-machinery identities
  -> descriptor/hash canonical external record and all attested roles
  -> descriptor/hash unique selector source
  -> enumerate and descriptor/hash complete gmpy2/package/library tree
  -> retain the verified gmpy2/__init__.py bytes
  -> establish gmpy2.gmpy2 from the absolute native-extension path
  -> compile+exec retained wrapper bytes in the prepared package namespace
  -> compile+exec retained selector source under a fresh private name
  -> selector startup/runtime/loaded-image attestation
  -> guarded public selector/radius call
```

The `SourceFileLoader` object on the package spec is metadata only. Its
`exec_module` is never called. Relative imports in the authentic wrapper bind
to the already established `gmpy2.gmpy2` native module.

The guard captures identities for:

- the `builtins` module and `compile`, `exec`, `__import__`, and
  `__build_class__`;
- `importlib`, `importlib.machinery`, `importlib.util`,
  `_frozen_importlib`, `_frozen_importlib_external`, and `_imp`;
- `SourceFileLoader`, `ExtensionFileLoader`, `ModuleSpec`,
  `spec_from_file_location`, `module_from_spec`, `create_dynamic`, and
  `exec_dynamic`; and
- ordered `sys.meta_path`, `sys.path_hooks`, and `sys.path`.

It checks after record consumption, after source/runtime snapshots, before and
after native/wrapper execution, before selector compile, before and after
selector execution, after post-load attestation, at entry to each public byte
operation, immediately before output-byte construction, and before return.
Any drift is HOLD and no verified output is returned.

## 4. External record modes cannot be confused

The two v3 record schemas are:

```text
positive-b-stage-b-t0-synthetic-test-attestation-v2
  status = NON-PROMOTABLE-SYNTHETIC-TEST
  mode = VERIFIED-ISOLATED-SYNTHETIC-TEST
  production_eligible = false

positive-b-stage-b-t0-external-attestation-v2
  status = INDEPENDENT-ATTACK-PASS
  mode = VERIFIED-ISOLATED
  production_eligible = true
```

Schema, status, mode, eligibility, record digest, and trust contract are
copied together into every output. Cross-combinations HOLD before runtime
use. The synthetic record can never authorize T1 or science.

The common exact role closure includes the v4/v5/Round-73 design chain,
implementation, loader, tombstone, primary/Round-78/Round-94 tests, wheel and
runtime locks, v1/v2 historical protocols, this v3 protocol, the v5 bridge,
Rounds 75/78/81, and the rejecting Round-93 report. A later production record
must additionally pin:

```text
round94_repair =
  audits/round_94_stageb_t0_selector_race_repair_freeze.md
independent_attack =
  a distinct later round_*_stageb_t0_selector_independent_attack.md
```

No production record exists at this repair-candidate stage.

## 5. Runtime provenance without an absolute closure claim

Static replacement, symlink, exact-set, digest, ABI/version, wrapper/native
export identity, and dyld loaded-image checks remain mandatory. The Python
wrapper digest describes the retained bytes actually compiled and executed.
The native-extension and bundled-library digests describe paths checked before
and after loading under the Section-2 no-hostile-writer contract.

The reader-facing provenance statement is therefore:

> The Python wrapper was executed from its verified descriptor snapshot.
> Native images were absolute-path loaded and re-attested under an explicit
> no-hostile-same-UID-writer execution-window assumption.

It must not be shortened to “all executed bytes are cryptographically closed.”

## 6. Output and regression contract

The output schemas are:

```text
positive-b-stage-b-t0-selector-output-v3
positive-b-stage-b-t0-role-radii-v3
```

`package_runtime` includes the exact entry schema/status/mode/eligibility,
external-record SHA-256, exact trust contract, source digest, captured-wrapper
digest/execution mode, package/library digests, native loaded-image names,
ABI/version metadata, and observed CPython/stdlib origins.

The deterministic Round-93 replay must:

1. capture and hash an authentic copied wrapper;
2. replace its pathname with a wrapper that writes a sentinel, hijacks
   `builtins.exec`, sets `exp_rn=42`, and changes an output index to `999`;
3. load the native extension and execute only the captured authentic wrapper;
4. restore the authentic pathname before source/runtime postchecks;
5. produce a normal guarded synthetic output; and
6. prove sentinel absent, `exp_rn != 42`, selected index `10`, not `999`, and
   exact non-promotable synthetic mode.

A separate deterministic mid-call regression replaces `builtins.exec` after
selection but before final output construction and requires HOLD with no
returned bytes.

All 49 earlier package tests and 33 historical design tests remain mandatory.
The five Round-94 regressions are additional; total expected science-free
tests are 87.

## 7. Scope and authorization

This package still implements only the object-free selector/radius arithmetic
and scalar/vector numerical odd-grid predicate. It does not implement the
separately frozen object-level Stage-B compiler and does not read or authorize
Stage-A, Stage-B, mesh, FV, off-lattice, manifest, result, evidence, or
manuscript objects.

```text
repair self-status = CANDIDATE
next gate          = HOLD-INDEPENDENT-ATTACK
scientific object/value/result = NOT READ / NOT RUN / NOT CREATED
AUTHORIZED-SCIENTIFIC-COMMAND: NONE
```
