# Round 182: runtime-helper prototype rejection and static-closure repair

Date: 2026-07-19

Status: **BOTH INITIAL RUNTIME-TRUTH PROTOTYPES REJECTED / V1 ORIGIN PROBE
CONVERTED TO A FROZEN INERT HOLD SENTINEL / AUTHENTICATED-BYTE STATIC
RESOLVER FROZEN AT ITS AST-ONLY COMPONENT SCOPE, NOT AS RUNTIME AUTHORITY /
REAL GMPY2 WRAPPER TO NESTED-EXTENSION TOPOLOGY REPRESENTABLE / INTEGRATED
P0=0/P1=2/P2=4 / NO RUNTIME CLOSURE, PLAN,
BUNDLE, REQUEST, COMMITMENT, EXECUTION, OUTPUT, RECEIPT, REPLAY, B06,
SAME-MEMBER, C1--C3, F0--F3, ROOT, RELEASE, OR SUBMISSION PROMOTION**

## 1. Scope and nonclaim boundary

Round 182 tested two mutable helpers intended to repair the live-runtime
limitations found in Round 181:

1. a static Python import-closure resolver; and
2. a CPython/gmpy2 runtime-origin probe.

Independent reviews found that neither initial draft could be admitted as
`runtime_closure_v1` authority.  The origin probe could emit a PASS after
running a caller-selected executable, used the wrong process environment,
buffered child output before enforcing its cap, did not clean descendant
processes, modeled only a flat top-level extension, and repeatedly timed out
on a legitimate child at its fixed 12-second limit.  The resolver omitted
parent packages, used declaration-circular `from`-import reasoning, read
unauthenticated paths, lacked SHA-bearing records, and admitted several forms
of indirect loading syntax.

This round therefore makes no runtime-truth, implementation, numerical,
replay, or scientific claim.  It records the rejected bytes, removes the
unsafe PASS surface from v1, and freezes one repaired resolver only as a
caller-authenticated, AST-only component for a future adapter.

## 2. Rejected initial prototype bytes

The independently reviewed initial bytes were:

| Object | SHA-256 | Size / disposition |
| --- | --- | --- |
| initial static resolver | `7b3029b7b521ed0b14bab4b0bdeb9d9335f692013f2559542f1e9e589f8b6252` | 14,828 bytes; rejected and superseded in place |
| initial resolver tests | `ffc1aa78ba7cbd2e0b12b1fce143a8c3b5f647b7aaba6833f84cfd7494a2e32c` | 7,965 bytes; insufficient mutation coverage |
| initial runtime-origin probe | `9ddf82812863a41451310b9a141d12e305870b97dc28e1467206537daffed8f8` | 25,600 bytes; rejected and disabled in place |
| initial probe tests | `73025e59f6f6dc3b019879882786b16f8396461b526ef36f66e637fc4642ff39` | 8,781 bytes; flaky and incomplete |

The integrated initial-draft review was `P0=0/P1=6/P2=3`; the more detailed
component ledgers were `P0=0/P1=5/P2=3` for the resolver and
`P0=0/P1=7/P2=2` for the origin probe.  These counts overlap and must not be
summed.

## 3. Why the initial origin probe was rejected

The decisive findings were:

1. the specification selected the executable and supplied its matching hash,
   so a non-CPython executable could self-report the expected snapshot;
2. the child environment injected `PATH` and `__CF_USER_TEXT_ENCODING`,
   omitted `HOME`, `TMPDIR`, and `TZ`, and used `/` rather than fresh mode-0700
   invocation directories;
3. `communicate()` buffered unbounded output before checking the cap, and a
   timeout killed only the direct child rather than its process group;
4. authenticated path bytes were later executed or loaded again by pathname,
   without an authority-bound sealed root or mutation monitoring;
5. the only numerical topology was a direct top-level `gmpy2` extension,
   whereas the observed installation is a Python wrapper plus the nested
   `gmpy2.gmpy2` extension;
6. extra or transitive Mach-O dependencies were not closed; and
7. two byte-identical self-reported snapshots had no nonce, run ordinal, or
   independent freshness binding.

The root rerun reproduced a semantic test being replaced by
`trusted child timeout after 12s`.  A passing first run therefore did not make
the suite repeatable or freeze-ready.

## 4. V1 origin-probe repair: an inert rejected-draft sentinel

The v1 source was not repaired into a runtime authority.  Instead it was
replaced by a fail-closed sentinel so that the rejected basename cannot later
be mistaken for a working validator.

| Object | SHA-256 / properties |
| --- | --- |
| rejected-draft sentinel | `432d8d83e3e691033b091037a216adb46199ff891aea1bb02696670397b42ffa`; 1,449 bytes; `0444`; nlink 1 |
| sentinel tests | `10430990964d7a12b5220ca6dce5371d14d1a5456f659dd06ae6359ce2280012`; 4,327 bytes; `0444`; nlink 1 |

The direct API immediately raises one `ProbeFailure` without observing its
argument.  Every CLI invocation, including valid-looking arguments, missing
arguments, unknown arguments, `-h`, and `--help`, returns integer `2`, writes
nothing to stdout, and writes exactly one rejection line to stderr.  No PASS
constant, child program, filesystem inspection, path resolution, import
probe, subprocess launch, or gmpy2 execution remains.

Focused verification is **19/19 PASS**, with monkeypatched filesystem, import,
and subprocess hooks proving that no hidden validation path is reachable.
Ruff check, Ruff format check, and `py_compile` also pass.

The sentinel-only ledger is `P0=0/P1=0/P2=0` for its negative behavior.  It
is not a runtime validator.

## 5. Static resolver repair

The resolver was rewritten around an explicit authenticated-by-caller
boundary:

- it receives immutable source/native bytes and never opens, stats, resolves,
  imports, or executes a supplied path;
- every file-backed dependency has the exact operation-model fields
  `import_name`, `origin_kind`, `path`, and `sha256`, and the SHA is checked
  against the exact supplied bytes;
- all dotted parent packages are mandatory;
- report-local `.py`, runtime-prefix `.py`, opaque runtime-prefix `.so`, the
  one numerical-native `.so` class, builtin, and frozen origins are distinct;
- candidate/report-local sources use a conservative restricted syntax
  profile, while pinned runtime-prefix sources allow ordinary CPython
  reflection and code generation but still reject import-loading machinery;
- runtime package-member imports require a transient independently supplied
  `module`/`attribute` classification, and strict candidate sources cannot use
  ambiguous package-member imports;
- runtime wildcard imports are allowed only from a declared non-package
  module, which admits `from .gmpy2 import *` without treating a package
  attribute as a submodule;
- the alias analysis is monotone and terminating; parser/scanner
  `ValueError`, `RecursionError`, and `MemoryError` paths are normalized to the
  resolver HOLD; and
- returned records are deterministic and lexicographically ordered.

The frozen component bytes are:

| Object | SHA-256 / properties |
| --- | --- |
| authenticated-byte resolver | `9b59af9bcbaab9159cbfc8a468c7b9aeb7fd576734fb451728fa2dafec57cbe9`; 32,156 bytes; `0444`; nlink 1 |
| resolver mutation tests | `99974d01b16818fc44713cd9e52c246e902d898241f26dc3f5015c6606efc306`; 32,248 bytes; `0444`; nlink 1 |

Focused verification is **93/93 PASS**, with Ruff check, Ruff format check,
`py_compile`, and whitespace checks passing.  The mutation suite covers
omitted parents, ambiguous package imports, package attribute/module
collisions, noncanonical paths, report-root reclassification, SHA mismatch,
oversized and pathological sources, alias nontermination, loading/reflection
syntax, runtime `.so` terminals, the wrapper-to-native wildcard form,
shuffled-input determinism, missing bytes, shared path ownership, and
non-lowercase SHA rejection.

The final combined sentinel-plus-resolver run is **112/112 PASS**.  All four
reviewed files are mode `0444`, one-link files, and their generated
module-specific bytecode was removed from the report tree after verification.

A separate read-only live-topology check used the observed bytes

```text
gmpy2 wrapper SHA-256             = 3d4f21a0e9d6d32c935e3d39ef4be23a9a7d0ea56344ebbb0b8dca4f5651e8a2
gmpy2.gmpy2 extension SHA-256     = 9586b7c4b887704b57576f52b73a8c45437946d2b172095d82c20fa0871a415b
```

and resolved the exact two-record closure

```text
gmpy2          -> file_runtime_prefix
gmpy2.gmpy2    -> numerical_native_extension
```

without report-local output or result artifacts.

## 6. Why the frozen resolver is not runtime authority

The repaired component is schema-compatible with the frozen
`resolved_python_dependency` object, but it is not independently sufficient
authority.  The future v3 precommit adapter must still:

1. authenticate the resolver and the retained v2 validator helpers by exact
   byte hash;
2. obtain each source image once through descriptor-anchored file
   authentication and pass those exact bytes to the resolver;
3. reject unsorted/noncanonical runtime JSON before any normalization;
4. derive package names and package-member kinds from a trusted runtime-origin
   classifier rather than candidate input;
5. compare the reconstructed closure field-for-field with serialized
   `python_imports` and `resolved_python_dependencies`;
6. independently join report-local origins to same-side source pins,
   runtime-prefix/builtin/frozen origins to the pinned Python identity, and
   `gmpy2.gmpy2` to the `gmpy2_extension` native-library pin; and
7. reconstruct the exact v2 `RuntimeInfo`, then reuse the unchanged plan and
   bundle validators.

The six numerical v3 entrypoints and global runner do not yet exist, so no
end-to-end actual closure can be admitted.  No combined differential suite
yet joins the old 42 static regressions, the 91 resolver cases, authority and
origin mutations, and the real six-source-plus-runner closure.

The resolver is therefore **FROZEN AS AN AST-ONLY COMPONENT / NOT FROZEN OR
ACCEPTED AS RUNTIME-CLOSURE AUTHORITY**.  Any semantics or origin claim outside
its caller-authenticated byte boundary remains open.

## 7. Required v2 origin architecture

The rejected probe must not be revived.  A new version requires this freeze
order:

```text
persistent external sealed runtime root
  -> frozen runtime-authority pin document
  -> small result-blind wrapper-import child and hardened process supervisor
  -> authority-bound parent probe plus adversarial tests
  -> precommit validator v3 integration
  -> actual six-entrypoint/global-runner runtime closure
```

The authority must pin the operation model and process digest, one accepted
Python executable/path/hash/ABI/version, the gmpy2 wrapper, nested extension,
GMP/MPFR/MPC images and versions, and the exact numerical Mach-O dependency
graph.  The caller must not choose the executable or numerical topology.

Each of two clean observations needs a distinct nonce, run ordinal, PID,
process group, mode-0700 cwd/HOME/TMPDIR stage, and the exact five-key parent
environment `HOME`, `LANG`, `LC_ALL`, `TMPDIR`, `TZ`.  The process supervisor
must use bounded nonblocking capture, one monotonic deadline, session/process-
group TERM--KILL--reap, pipe EOF confirmation, descendant absence, and stage
cleanup.  The child must perform ordinary `import gmpy2`, observe both wrapper
and nested-extension origins, and report an exact numerical dyld delta.

Even that future ACK must retain explicit nonclaims for byte-complete
framework/stdlib/macOS runtime, numerical correctness, candidate execution,
results, replay, release, and malicious concurrent same-UID writers.

## 8. Integrated severity and gate ledger

At replay-readiness scope after the safe repairs:

```text
P0 = 0
P1 = 2
P2 = 4
```

The two P1 blockers are:

1. no authority-bound sealed runtime root, origin classifier, process
   supervisor, child, or v2 origin-probe ACK exists; and
2. no v3 precommit adapter or end-to-end actual six-source-plus-runner closure
   and differential mutation suite exists.

The four P2 items remain:

1. role-8 numerical producer/verifier implementation is absent;
2. role-9 numerical producer/verifier implementation is absent;
3. the role-10 v3 implementation pair and global runner v2 are absent; and
4. no real runtime closure, replay plan, candidate bundle, request-v4 set,
   external predecessor commitment, replay, same-member acceptance, or later
   continuum/root/release evidence exists.

Final gate state:

```text
operation-model-v2                               = FROZEN PROSPECTIVE CONTRACT
Round-180 validator                              = FROZEN; SYNTHETIC SCOPE ONLY
v1 runtime-origin probe                          = INERT REJECTED-DRAFT HOLD SENTINEL
authenticated-byte static resolver               = FROZEN COMPONENT / 93 TESTS / NO AUTHORITY ACCEPTANCE
trusted v2 origin authority/probe                 = ABSENT
role-8/9 numerical implementations               = 0/4
all role-v3 numerical implementations            = 0/6
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
