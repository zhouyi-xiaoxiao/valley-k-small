# Round 96: independent validation of the Stage-B-v5 T0 production attestation

Date: 2026-07-14  
Reviewer: independent result-blind validator  
Decision: **ACCEPT / PRODUCTION-ATTESTATION-VALID**  
Open findings: **P0 = 0, P1 = 0, P2 = 0**  
Scientific object/value/result status: **NOT READ / NOT RUN / NOT CREATED**  
Authorization: **AUTHORIZED-SCIENTIFIC-COMMAND: NONE**

## 1. Frozen input

I validated, but did not edit, the exact record:

| path | bytes | independently recomputed SHA-256 |
|---|---:|---|
| `code/positive_b_stage_b_t0_external_attestation_v2.json` | 4567 | `2572938fad9fdb74e4a0d8053651601af7359fa7df2ce47747ffd4fbb57fbb43` |

The bytes are ASCII, terminate in exactly one newline, and equal
`json.dumps(record, sort_keys=True, indent=2).encode("ascii") + b"\n"`.
The six top-level fields, schema
`positive-b-stage-b-t0-external-attestation-v2`, status
`INDEPENDENT-ATTACK-PASS`, and authorization `NONE` are exact.

## 2. Role, path, hash, and DAG validation

The record contains exactly the loader's 19 `COMMON_ATTESTED_PATHS` plus the
distinct `round94_repair` and `independent_attack` roles: **21/21 exact roles**.
For every role I independently checked entry closure, exact role/path mapping,
canonical relative path, canonical SHA-256 syntax, regular-file status,
absence of symlinks in every relative component, and actual content digest.
All **147/147 per-role checks passed**.

The two promotion roles are exact and distinct:

| role | exact path | independently recomputed SHA-256 |
|---|---|---|
| `round94_repair` | `audits/round_94_stageb_t0_selector_race_repair_freeze.md` | `72ae06c1e048a01e8724721b28830965599c60c0165c5dbbcce218932e85bd27` |
| `independent_attack` | `audits/round_95_stageb_t0_selector_independent_attack.md` | `8ee8129422206de5597524f379d88b12269ad20d210cf8b03a151fa19ccecc0e` |

All 21 paths are unique, relative, canonical, and contain neither `..` nor an
absolute component. The record does not pin itself or this Round-96 report.
Its digest is absent from all 21 attested files; its path and digest are absent
from Round 94 and Round 95. The dependency graph is therefore one-way:

```text
Round 94 repair -> Round 95 independent PASS -> production-v2 record
production-v2 record -> this Round-96 validation -> possible future T1 pin
```

There is no record/report back-edge or self-pin.

## 3. Trust contract and runtime root

The exact record and loader mapping is:

```text
schema                   positive-b-stage-b-t0-execution-trust-contract-v1
bootstrap_trust_base     CPYTHON-STDLIB-IMPORT-MACHINERY-OS-LOADER-SYSTEM-LIBRARIES
runtime_tree_concurrency NO-HOSTILE-SAME-UID-WRITER-DURING-LOAD-AND-PUBLIC-CALLS
wrapper_execution        VERIFIED-DESCRIPTOR-SNAPSHOT-COMPILE-EXEC
native_image_execution   PATH-LOADED-UNDER-NO-HOSTILE-SAME-UID-WRITER-CONTRACT
protection_claim         DEFENSE-IN-DEPTH-NOT-CRYPTOGRAPHIC-IMMUTABILITY
```

The runtime root is exactly
`/Users/ae23069/.local-build/valley-k-small/.venv/lib/python3.12/site-packages`:
absolute, canonical, present as a directory, and free of symlink components.
Acceptance retains the stated same-UID-writer assumption and does not claim
cryptographic immutability of path-loaded native images.

## 4. Independent production consumption

In a fresh pinned CPython `-I -S` child, I descriptor-read and independently
hash-matched the loader at
`9a3cd379f4a19c5b0cf6317d9e3bfbfd39bf6914714de7fb014754a4d0ca4cad`,
then compiled and executed only those retained loader bytes with
bootstrap-captured `compile` and `exec`. The loader was never path-imported.

Before the accepted load, four minimal negative cases failed closed:

| mutation | observed HOLD |
|---|---|
| wrong expected record digest | external-attestation SHA mismatch |
| changed trust contract | trust-contract drift |
| missing `round94_repair` | package-role closure drift |
| wrong Round-95 digest | independent-attack content SHA mismatch |

The exact production record then loaded successfully. I descriptor-captured,
hash-matched, compiled, and executed only the pinned hand-built primary fixture
(`8ac8a27c603e64af3467ed1784b947fe3bfbb117b6ea0ca3dad2f533eb901aa8`).
No Stage-A/Stage-B object, mesh, FV/off-lattice input, producer, saved result,
manifest, evidence object, or manuscript was opened or run.

Two public calls returned identical canonical bytes. The production output was:

```text
fixture payload SHA-256 = 887ae07babcbb8365525634da98d5104b4ff7aeca03ebd7e5e46982bb67477a9
selected index          = 10
output bytes            = 6660
output SHA-256          = 76ba91c011ebb09206dabc12011bc7ff7ab598b95b6e3f1ce9d1858301bbf8fb
output schema           = positive-b-stage-b-t0-selector-output-v3
external schema         = positive-b-stage-b-t0-external-attestation-v2
external record digest  = 2572938fad9fdb74e4a0d8053651601af7359fa7df2ce47747ffd4fbb57fbb43
external status         = INDEPENDENT-ATTACK-PASS
mode                    = VERIFIED-ISOLATED
production_eligible     = true
authorization           = AUTHORIZED-SCIENTIFIC-COMMAND: NONE
wrapper marker          = VERIFIED-DESCRIPTOR-SNAPSHOT-COMPILE-EXEC
```

The embedded trust mapping was exact. The live `gmpy2` module carried the same
captured-wrapper marker, and the loaded native-image set was exactly the
extension plus `libgmp.10.dylib`, `libmpc.3.dylib`, and `libmpfr.6.dylib`.

## 5. Command, count, and final ledger

```text
python3 /tmp/stageb_round96_validate.py
result: 203/203 PASS
harness SHA-256: 409df317120da39250678486d86a31fc179705fd9f24daa9a92073366ee3a019
```

The 203 checks comprise 174 independent canonical/role/path/hash/runtime/DAG
assertions and 29 isolated loader, negative-HOLD, fixture, output, marker, and
native-set assertions.

```text
P0 open = 0
P1 open = 0
P2 open = 0
production-v2 record = INDEPENDENTLY VALIDATED
production synthetic output pin = 76ba91c011ebb09206dabc12011bc7ff7ab598b95b6e3f1ce9d1858301bbf8fb
future T1 = NOT BUILT / NOT AUTHORIZED BY THIS ROUND
scientific execution = NOT AUTHORIZED
AUTHORIZED-SCIENTIFIC-COMMAND: NONE
```
