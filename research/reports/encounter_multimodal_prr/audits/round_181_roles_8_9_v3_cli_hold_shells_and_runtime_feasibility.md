# Round 181: role-8/9 v3 CLI HOLD shells and runtime-feasibility audit

Date: 2026-07-19

Status: **FOUR FAIL-CLOSED CLI HOLD SHELLS ONLY / ZERO OF SIX NUMERICAL
ENTRYPOINTS IMPLEMENTED / LIVE RUNTIME-CLOSURE-V1 NOT MATERIALIZABLE WITH
THE FROZEN ROUND-180 VALIDATOR / INTEGRATED P0=0/P1=2/P2=4 / NO REAL PLAN,
BUNDLE, REQUEST, COMMITMENT, OUTPUT, RECEIPT, REPLAY, B06, SAME-MEMBER,
C1--C3, F0--F3, ROOT, RELEASE, OR SUBMISSION PROMOTION**

## 1. Scope and nonclaim boundary

Round 181 occupies four operation-model-v2 role-v3 basenames with immutable,
source-separated CLI HOLD shells: the role-8 producer/verifier and role-9
producer/verifier.  The shells freeze the public argv surface and one exact
implementation-incomplete failure outcome.  They do not authenticate a
request, import a numerical backend, perform numerical work, open any supplied
path, or publish an artifact or receipt.

The precise count is therefore

```text
required role-v3 basenames occupied by CLI HOLD shells = 4/6
role-v3 numerical entrypoints implemented              = 0/6
```

This round also probes the live CPython/gmpy2 environment against the frozen
Round-180 runtime-closure validator.  The probe is read-only except for
ephemeral files below `/tmp`; it creates no report-local runtime closure,
plan, bundle, request, commitment, result, or receipt.

## 2. Frozen reviewed shell bytes

| Role | Report-relative path | SHA-256 / properties |
| --- | --- | --- |
| role-8 producer HOLD shell | `code/build_continuum_c1_n0_candidate_native_raw_axis_formula_v3.py` | `61a23da6ff9ea416f55db3698449cbefb77bfeb21e570d604adee0ded7615e69`; 2,867 bytes; `0444`; nlink 1 |
| role-8 verifier HOLD shell | `code/validate_continuum_c1_n0_candidate_native_raw_axis_formula_v3.py` | `efb02c33f1779d3cb501451e9f7d72a1c31f2f1795cedcb0c83d0a23c788605e`; 3,167 bytes; `0444`; nlink 1 |
| role-8 adversarial tests | `code/test_continuum_c1_n0_candidate_native_raw_axis_formula_v3_hold.py` | `38f88dda858d680a82d0e6ffe4d4f4ecf6c5d5b6bc156ef709a8a3a5c8a2314f`; 7,736 bytes; `0444`; nlink 1 |
| role-9 producer HOLD shell | `code/build_continuum_c1_n0_candidate_native_stationary_integrals_v3.py` | `1b76e1463d5a388f15669d86922db86154011f78913528b9efa2ad98bd376e22`; 5,852 bytes; `0444`; nlink 1 |
| role-9 verifier HOLD shell | `code/validate_continuum_c1_n0_candidate_native_stationary_integrals_v3.py` | `ee6ecb5f1a2db3c21114ddad3faf89fa8fa2aac334d50cfc254592b8eac35283`; 6,262 bytes; `0444`; nlink 1 |
| role-9 adversarial tests | `code/test_continuum_c1_n0_candidate_native_stationary_integrals_v3.py` | `f6db47dce3cc6d7e060fbc34e9f1aebd8d0b63b524870b6639a5d358f1b75d83`; 9,367 bytes; `0444`; nlink 1 |

The role-8 shells terminate only with

```text
HOLD_CANDIDATE_RAW_AXIS_NUMERICAL_IMPLEMENTATION_INCOMPLETE
```

and the role-9 shells terminate only with

```text
HOLD_CANDIDATE_STATIONARY_NUMERICAL_IMPLEMENTATION_INCOMPLETE
```

For every tested invocation, the exit code is integer `2`, stdout is empty,
and stderr is exactly the corresponding HOLD plus one trailing LF.

## 3. Shell properties established

The final shell-byte review establishes only that:

- all four exact operation-model-v2 basenames and producer/verifier argv
  shapes are present;
- producer and verifier paths and bytes are distinct within and across roles;
- `--help`, `-h`, missing arguments, noncanonical paths, duplicate paths,
  pre-existing input/output sentinels, direct APIs, and valid frozen argv all
  fail through the same role-specific HOLD;
- the four sources contain no `gmpy2`, GMP, MPFR, MPC, NumPy, SciPy, legacy
  backend, report-local numerical, dynamic-import, or dynamic-execution import;
- no supplied request, artifact, or receipt path is opened, statted, created,
  replaced, truncated, removed, or modified; and
- the frozen Round-180 `_source_imports` gate accepts all four source files.

The shell-only six-file ledger after repair is

```text
P0 = 0
P1 = 0
P2 = 0
```

That zero ledger applies only to the negative CLI sentinel behavior.  It is
not a numerical, runtime, replay, or scientific acceptance ledger.

## 4. Adversarial repair chronology and receipts

The first independent shell audit found three concrete defects:

1. default argparse help allowed all four `-h`/`--help` paths to exit zero;
2. role 9 exposed default argparse usage and alternate request-error messages
   rather than one exact HOLD; and
3. role 9 imported `gmpy2` at module load, so native-loader failure could
   escape before the intended HOLD.

The repaired bytes disable the help action, route every parser/API rejection
through the one implementation-incomplete exception, remove the role-9 native
import, and retain only a literal planned-backend identity.  A final red-team
pass also strengthened the role-9 test-side AST oracle so future general
from-imports and dynamic import/execution primitives cannot evade the same
profile used for role 8.

Final observed receipts:

- focused tests: **25/25 PASS** (`12` role-8 cases and `13` role-9 cases);
- independent subprocess matrix: **36/36 exact HOLD outcomes**;
- Ruff check and format check: **PASS**;
- `py_compile`: **PASS**, with cache outside the report tree;
- frozen Round-180 source-profile scan: **PASS** for all four sources; and
- clean-environment `-I -B` help probes: exact exit `2`, empty stdout, and one
  exact HOLD line for every entrypoint.

No role-8/9 request-v4 file, output, validation receipt, runtime closure, plan,
bundle, or commitment exists in the report tree after the tests.

## 5. Numerical implementation boundary

Role 8 still lacks request-v4 authentication, directed MPFR 320-bit
production, 640-bit containment sentinel, exact binary64 endpoint decoding,
exact-Fraction expression-DAG evaluation, source-v2 materialization, atomic
publication, and an independently reconstructed validation receipt.

Role 9 still lacks request-v4 authentication, directed stationary-integral
production, 640-bit containment sentinel, exact-Fraction aggregation,
source-v2 materialization, atomic publication, and an independently
reconstructed validation receipt.

The shells must not be entered into a runtime closure whose claim boundary
says `complete_report_local_and_declared_numerical_runtime_closure=true`.
They are sentinels proving that the mandated public paths fail closed while
the implementations are absent.

## 6. Live runtime-feasibility findings

The observed runtime identity is:

```text
Python version       = 3.12.13
Python ABI           = cpython-312-darwin
machine              = arm64
Darwin release       = 25.5.0
macOS build          = 25F84
gmpy2                = 2.2.1
GMP / MPFR / MPC     = 6.3.0 / 4.2.1 / 1.3.1
```

The canonical CPython executable is a regular mode-`0755` file with SHA-256
`31b9c9a8d50289f3a13f014b3efd8ea3534fc3eea7ca7d9809e166139910b805`.
The working `.venv/bin/python` path traverses symlinks.  The actual `gmpy2`
import is a mode-`0644` Python wrapper with SHA-256
`3d4f21a0e9d6d32c935e3d39ef4be23a9a7d0ea56344ebbb0b8dca4f5651e8a2`
plus the nested mode-`0755` extension
`gmpy2.gmpy2`, SHA-256
`9586b7c4b887704b57576f52b73a8c45437946d2b172095d82c20fa0871a415b`.
Its ordered bundled libraries are:

| Native image | SHA-256 |
| --- | --- |
| `libgmp.10.dylib` | `22cec4689e503d590cfbf3373ae7f442ef6d40c3e6c93a3612bbd1b7e2bce049` |
| `libmpfr.6.dylib` | `d314a427a901f8ece38b67966cd2fbf5642ceb7d1c2e5136f8282ca7ab859aed` |
| `libmpc.3.dylib` | `d3c10c39234c095f5c1938ad607c87a0633152f51271d9ed1c494724430c2b0c` |

`otool -L` confirms the extension resolves those three images through
`@loader_path/../gmpy2.libs` and also uses `/usr/lib/libSystem.B.dylib`, which
remains inside the required non-byte-complete host boundary.

An ephemeral `/tmp` probe copied the exact CPython and four numerical native
images, changed only their permissions to the validator's `0555`/`0444`
requirements, exposed the extension directly as top-level `gmpy2`, and
successfully imported it under `-I -B`.  This proves a custom sealed layout is
technically possible; it does not authenticate the live venv layout, pin the
stdlib/import closure, establish the exact process origin, or create a valid
runtime-closure document.

## 7. Integrated severity ledger

At replay-readiness scope, the ledger is

```text
P0 = 0
P1 = 2
P2 = 4
```

The two P1 items are frozen-validator feasibility blockers:

1. **The Round-180 validator does not represent the observed gmpy2 import
   topology.**  It hard-codes import name `gmpy2` as the native extension,
   whereas the live installation uses a wrapper plus `gmpy2.gmpy2`.  The
   operation-model-v2 dependency vocabulary is broader than this validator
   restriction, so the next step is a versioned validator repair, not a false
   live-origin record.
2. **The Round-180 runtime-prefix profile cannot accept the observed CPython
   environment.**  It applies the candidate-source general-from-import ban to
   ordinary stdlib files and requires exact read-only modes for every pinned
   dependency.  The current shells already reach `argparse`/`pathlib` stdlib
   sources that violate that profile, while the live interpreter/native files
   also have different modes and a symlinked venv entry path.  A truthful
   origin probe and dependency-closure validator must be versioned and
   independently tested before any runtime document is materialized.

The four P2 items are:

1. role-8 numerical producer/verifier implementation is absent behind two
   HOLD shells;
2. role-9 numerical producer/verifier implementation is absent behind two
   HOLD shells;
3. the role-10 v3 implementation pair and global runner v2 are absent; and
4. no real runtime closure, replay plan, candidate bundle, request-v4 set,
   external predecessor commitment, non-null shared-protocol allowlist, or
   replay exists; the Round-179 cleanup/recovery limitations also remain.

The Round-180 `P0=0/P1=0/P2=4` result remains valid at its explicitly
synthetic static-structure scope.  Round 181 adds a broader live-feasibility
finding and does not relabel synthetic success as runtime truth.

## 8. Final gate ledger

```text
operation-model-v2                               = FROZEN PROSPECTIVE CONTRACT
role-8 v3 basename/CLI shells                    = 2/2 FROZEN HOLD SENTINELS
role-9 v3 basename/CLI shells                    = 2/2 FROZEN HOLD SENTINELS
role-8/9 numerical implementations               = 0/4
all role-v3 numerical implementations            = 0/6
Round-180 static validator                       = FROZEN; SYNTHETIC SCOPE ONLY
live runtime-closure feasibility                  = P1 HOLD; VERSIONED VALIDATOR REPAIR REQUIRED
role-10 v3 pair / global runner                   = ABSENT / ABSENT
runtime-closure-v1 / replay-plan-v2 / bundle-v2  = ABSENT / ABSENT / ABSENT
external predecessor commitment                  = ABSENT
request-v4 files / role outputs / receipts       = ABSENT
B06 structural remedy prepared / cleared         = FALSE / FALSE
fresh roles 8--10 replay                          = NOT PERFORMED
same-member acceptance                           = FALSE
C1--C3 / F0--F3 / root transfer                  = FALSE
release / submission                             = FALSE
```

The next valid step is to supersede the frozen Round-180 validator with a
result-blind runtime-truth version that remains joined to operation-model-v2,
probes dependency origins without executing candidate numerical source, and
is itself mutation-audited.  No runtime, plan, bundle, request, or commitment
may be created before that repair is frozen.
