# Positive-`B` Stage-B-v5 T0 selector repair protocol v2

Date: 2026-07-14  
Status: **ROUND-81 REPAIR CANDIDATE / HOLD-INDEPENDENT-ATTACK**  
Scientific object/value/result status: **NOT READ / NOT RUN / NOT CREATED**  
Authorization: **AUTHORIZED-SCIENTIFIC-COMMAND: NONE**

## 1. Authority, scope, and supersession

This is the normative repair protocol for the science-free Stage-B-v5 T0
selector package.  It supersedes
`notes/positive_b_stage_b_t0_selector_protocol_v1.md`, which remains only a
historical Round-75 byte record.  The v1 implementation/shim architecture and
its claim to implement all of Sections 3--6 must not be used by T1.

The repaired package implements the object-free selector and role-radius
algebra, plus the scalar/vector numerical odd-grid predicate.  It does not
read or create a Stage-A/Stage-B object, manifest, scientific value, result,
FV/off-lattice output, or manuscript evidence.  It has no scientific CLI or
producer import.  Every accepted byte input and emitted byte output carries:

```text
AUTHORIZED-SCIENTIFIC-COMMAND: NONE
```

## 2. One implementation, no compatibility import

There is exactly one executable selector source:

| role | path | SHA-256 |
|---|---|---|
| unique substantive implementation | `code/positive_b_stage_b_t1_selector_v5.py` | `a4d6e933cdcb3e244afceaca8baece044f38ebf072e8f75c7c01fbf818bdde1a` |
| descriptor-first loader | `code/positive_b_stage_b_t0_verified_loader.py` | `66168e15ede42a6126280dea9f165e31a76529d74c17209cc2d1232322e507e0` |
| retired-name fail-closed tombstone | `code/positive_b_stage_b_t0_selector.py` | `53d624310d808a82b52bb1c9f7b14405c2324c4c457e727739b1e1a92462d032` |
| primary synthetic suite | `code/test_positive_b_stage_b_t1_selector_v5.py` | `358cdb556794c85f08e08dd8c7d6f5ca9fdd650444c1de54db7f20496cc31035` |
| Round-78 exploit regressions | `code/test_stageb_t0_selector_round78.py` | `4869aaad243f7f79b26e2a3d0ed406b12506a68b0cfb27b9ee4756213bf544bc` |
| wheel lock | `code/positive_b_stage_b_t0_requirements.lock` | `52f905ed765f2fa9422dd28e082b3abeb9e46c0b391b9fd6a9b32a5f2fc0a2a2` |
| executed-runtime lock | `code/positive_b_stage_b_t0_runtime_lock_v2.json` | `7321fb3ce442276f4b2ff1b7c6f58c844926fba63bcca2270e10e53fb5f44ecf` |

`positive_b_stage_b_t0_selector` is not a shim and exports nothing: importing
it raises `ImportError`.  The substantive v5 source contains no local selector
import.  Thus an earlier `PYTHONPATH` entry or a preloaded `sys.modules` object
under the retired name cannot affect the implementation.

### Mandatory future-T1 consumption rule

A future T1 is forbidden to import either selector name through normal module
search.  Its frozen bootstrap must start CPython with both `-I` and `-S`; the
loader itself checks those flags and HOLDs every non-isolated entry.  Before
any selector or gmpy2 package code is executed, that bootstrap must:

1. descriptor-read the external T0 attestation record and match its SHA-256
   to the hash already frozen in the T1 manifest;
2. obtain all package pins only from that authenticated record, then
   descriptor-read and SHA-256 verify the exact absolute loader path before
   executing its bytes;
3. call that exact loader with only the absolute record path and the T1-frozen
   record SHA-256; the loader itself parses the canonical record, requires the
   complete role closure, and re-verifies every listed package byte;
4. let the loader obtain the source hash and runtime-site root only from that
   authenticated record, then descriptor-verify the unique sibling source and
   the exact complete gmpy2 package, extension, and bundled-library trees
   before their first import; import only that verified package by its absolute
   spec without adding the runtime-site root to `sys.path`; execute the source
   under a fresh private name; and compare its post-load attestation;
5. reject `sitecustomize`, user site, `PYTHONPATH`, an occupied private module
   name, a preloaded `gmpy2`, any symlink or file replacement observed by the
   descriptor/lexical identity checks, preloaded critical selector modules
   (`platform`, `sysconfig`, `ctypes`, `ctypes._endian`, `_ctypes`), any
   old-name import, and any digest mismatch; and
6. copy the implementation/runtime attestation and external T0 attestation
   hash into the T1 output.

The loader's exact operational order is: isolation/native-environment check;
external-record descriptor/hash; canonical-schema and full-package descriptor
closure; source descriptor/hash; exact runtime-tree enumeration and
descriptor/hash closure; absolute-spec gmpy2 import with no runtime-root
`sys.path` insertion; source execution; loaded-image postcheck; post-load
attestation.  Thus a hash performed after an ordinary import is never a valid
entry.  The v5 source independently checks the injected context before its
`gmpy2` or critical-stdlib imports; an ordinary import HOLDs before any fake
wrapper or fake critical module can execute.  At startup and before every
public byte operation it also requires the captured critical modules to retain
their `sys.modules` identities, canonical stdlib origins, and source/extension
loader classes.

The production external T0 record has an exact `files` role set.  It must pin
the v4/v5/Round-73 design chain, this source, loader, tombstone, both test
suites, both dependency locks, historical v1, this v2 protocol, the v5
bridge, Round 75, Round 78, the Round-81 repair report, and its later
independent attack.  The loader accepts production mode only for status
`INDEPENDENT-ATTACK-PASS`; no two roles may reuse a path, and the independent
attack must use a distinct `round_*_stageb_t0_selector_independent_attack.md`
path.  Until that later record exists, T1 remains HOLD.

## 3. Executed-runtime provenance and fail-closed startup

The wheel hash alone is not accepted as runtime provenance.  Import startup
and every public byte call attest the code that is actually executing:

| executed item | SHA-256 |
|---|---|
| `gmpy2/__init__.py` | `3d4f21a0e9d6d32c935e3d39ef4be23a9a7d0ea56344ebbb0b8dca4f5651e8a2` |
| `gmpy2/gmpy2.cpython-312-darwin.so` | `9586b7c4b887704b57576f52b73a8c45437946d2b172095d82c20fa0871a415b` |
| `gmpy2.libs/libgmp.10.dylib` | `22cec4689e503d590cfbf3373ae7f442ef6d40c3e6c93a3612bbd1b7e2bce049` |
| `gmpy2.libs/libmpc.3.dylib` | `d3c10c39234c095f5c1938ad607c87a0633152f51271d9ed1c494724430c2b0c` |
| `gmpy2.libs/libmpfr.6.dylib` | `d314a427a901f8ece38b67966cd2fbf5642ceb7d1c2e5136f8282ca7ab859aed` |

The runtime lock additionally freezes every other file in the imported
`gmpy2` package, including its one bytecode cache and all shipped headers.
The loader requires exact directory-name closure for `gmpy2`, its
`__pycache__`, and `gmpy2.libs`; an unlisted sibling inside any of those
directories is HOLD before package execution.  Files elsewhere in the
declared site root are unreachable because that root is never inserted into
`sys.path`.  Regressions place hostile `platform.py`, `sysconfig.py`,
`ctypes.py`, and a sibling package there and prove zero sentinel execution.

The non-system recursive load graph, frozen by the runtime-lock bytes, is:

```text
gmpy2 extension -> libmpc, libmpfr, libgmp
libmpc          -> libmpfr, libgmp
libmpfr         -> libgmp
libgmp          -> no bundled dependency
```

`/usr/lib/libSystem.B.dylib` is the explicit OS trust-base leaf.  All bundled
recursive dependencies are exact-set and byte verified.  The verifier also
requires the actual wrapper and extension `sys.modules` identities, matching
file/spec origins, source/extension loader classes, the single package search
path, and identity of every numerical wrapper export with its native-extension
export.  A fake wrapper that redefines `exp`, even beside a byte-authentic
extension, is HOLD.  Before the source's first runtime import, both loader and
source reject every nonempty `DYLD_*`, `LD_LIBRARY_PATH`, and `LD_PRELOAD`
injection variable.  After import, the source queries dyld directly and
requires the actually loaded numerical image set to be exactly the one frozen
extension plus the three frozen bundled dylibs at their attested paths.  A
pre-hashed file that was not the loaded image therefore cannot pass.

The ABI/version/compiler freeze remains CPython 3.12, Darwin arm64, `clang`,
the exact `PY_CFLAGS` recorded in source, gmpy2 2.2.1, MPFR 4.2.1, GMP 6.3.0,
and MPC 1.3.1.  File reads use `O_NOFOLLOW`, descriptor identity checks,
post-read lexical inode checks, exact size caps, and SHA-256.

Threat boundary: the invoked CPython executable, its standard library and
import machinery, and the operating-system loader/system libraries are the
external bootstrap trust base.  This T0 package does not hash-close that whole
base and does not claim to defeat arbitrary substitution of modules already
used to execute the bootstrap itself.  It does close the selector, gmpy2
package, extension, and non-system GMP/MPFR/MPC images, and it rejects
pre-start and post-start substitution of the five critical stdlib module names
the selector consumes.  Each output discloses the observed CPython executable,
resolved executable, stdlib root, and critical-module origins.

Every canonical selector/radius output now contains `package_runtime`, whose
`implementation_sha256`, wrapper/extension/library hashes, runtime-lock hash,
and ABI metadata describe the bytes used for that call.  The output schemas
are `positive-b-stage-b-t0-selector-output-v2` and
`positive-b-stage-b-t0-role-radii-v2`.

No direct source import is permitted, including in tests: it HOLDs before
`gmpy2`.  The isolated suite uses a complete synthetic record whose status is
`NON-PROMOTABLE-SYNTHETIC-TEST`; outputs are marked
`VERIFIED-ISOLATED-SYNTHETIC-TEST`.  A future T1 must instead require exact
mode `VERIFIED-ISOLATED`, status `INDEPENDENT-ATTACK-PASS`, and the external
record hash frozen in T1.  The synthetic record can never be promoted.

## 4. Arithmetic repairs

Algebra remains exact-`Fraction` syntax followed by explicit binary64 RN,
downward, or upward conversion.  The MPFR interval/tie rules for `sqrt`, `log`,
and ordinary `exp` are unchanged.

For every finite binary64 `x <= -1000`, exact positivity and
`exp(x) < 2^-1075` prove:

```text
exp_down64(x) = 0
exp_rn(x)     = 0
exp_up64(x)   = 2^-1074
```

The bound is elementary: the positive Taylor lower sum gives
`exp(0.7) > 2`, hence `ln(2) < 0.7`, and `1075*0.7 < 1000`.  This repairs the
old upward-underflow HOLD without relying on MPFR to represent an exponent
outside its configured range.  Synthetic regressions cover `-1000`, `-1e20`,
and negative maximum finite binary64.

## 5. Saved-node semantics

`acceptance_index` is an opaque unique uint64 identity, not an arithmetic mesh
coordinate.  Once the chosen record has a unique matching node, `p` and `n`
are the immediately preceding and succeeding elements of the saved ordered
node array.  The chosen element must have both array neighbors; duplicate or
missing identities HOLD.  The numeric IDs need not be consecutive or
monotone.  This is the literal meaning of adjacent saved nodes in the v5
design.  Regressions accept `(10,20,30)` while preserving all frame and pair
selection checks.

## 6. Exact Section-6 scope limit

The package provides only the numerical scalar/vector odd-grid Boolean for
three already supplied interval grids, including exact `Dplus`, `Dminus`, and
the frozen threshold logic.  It does **not** provide the object-level compiler
needed to prove:

- diagnostic inventory completeness;
- canonical grid identities and order;
- topology/coverage conservation across all promoted diagnostics; or
- provenance joining those diagnostics to a future scientific object.

Therefore this protocol does not claim full implementation of Section 6 or of
all Sections 3--6.  A separately frozen, independently attacked pre-Stage-A
compiler must enforce those object-level obligations before any scientific
execution.  The present numerical primitives cannot authorize or substitute
for that compiler.

## 7. Canonical fixtures and verification

| synthetic object | bytes | SHA-256 |
|---|---:|---|
| selector input | 4186 | `887ae07babcbb8365525634da98d5104b4ff7aeca03ebd7e5e46982bb67477a9` |
| selector output v2, external-record hash normalized to 64 zeros | 5517 | `429d6f9b0556644742a83c3368c01d8b61739126dbb3fe189f0acc897305ece2` |
| role-radius input | 759 | `60064e54fb75afdb8449ef8bafc8a8f5e6f406d5d62bf95bd765b2064d195abb` |
| role-radius output v2, external-record hash normalized to 64 zeros | 3879 | `11a1fb13134e314533dbf18c35f3ed69c9abf98b4e0d2a8030e401cea2f18e33` |

The full output hash intentionally depends on the authenticated external
record.  The normalized pins above replace only that copied 64-hex digest and
therefore avoid a provenance cycle while still pinning every decision field.

The joint science-free suite contains 82 tests: 30 primary implementation
tests, 19 Round-78 exploit regressions, and 33 unchanged historical design
tests.  It covers wrong external-record pins, fake old-name `PYTHONPATH` and
`sys.modules`, fake v5 module search, fake gmpy2 wrapper overrides, in-memory
native-export overrides, non-isolated-entry HOLD, `sitecustomize` suppression,
native-loader injection, actual dyld-image drift, bundled-library set drift,
hostile top-level runtime-root modules, extra package files, source/descriptor races,
critical-stdlib preloads and post-start identity replacement,
underflow directions, sparse IDs, schema/JSON attacks, and all earlier
arithmetic/selector/odd-gate/radius mutations.

Round 75 disclosed that one broad construction search printed a few producer
source symbol lines.  That historical process observation is retained; this
protocol makes no claim of absolute producer-source noninspection.  It did
not expose a scientific object, value, or result, and Round 81 performed no
new broad producer scan.

## 8. Boundary

```text
Round-81 repair self-status = CANDIDATE
next status                 = HOLD-INDEPENDENT-ATTACK
scientific object/value/result = NOT READ / NOT RUN / NOT CREATED
AUTHORIZED-SCIENTIFIC-COMMAND: NONE
```

No Stage-A substitution, mesh-65/97 evaluation, FV/off-lattice run,
scientific manifest/result creation, release, or claim promotion is authorized.
