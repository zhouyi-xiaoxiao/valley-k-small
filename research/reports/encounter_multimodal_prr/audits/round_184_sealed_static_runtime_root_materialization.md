# Round 184: sealed static runtime-root materialization

Date: 2026-07-19

Status: **EXACT STATIC ROOT, PERSISTENT INVENTORY, AND CURRENT-TREE RECEIPT
MATERIALIZED AND INDEPENDENTLY ACCEPTED AT COMPONENT SCOPE /
P0=0/P1=0/P2=0 FOR THIS COMPONENT / NO IMPORT, RUNTIME PROBE, CANDIDATE
NUMERICAL EXECUTION, RUNTIME CLOSURE, SAME-MEMBER, C1--C3, F0--F3, ROOT
TRANSFER, RELEASE, OR SUBMISSION PROMOTION / INTEGRATED P0=0/P1=2/P2=4**

## 1. Scope and nonclaim boundary

Round 184 performs exactly the first two steps recommended by Round 183:

1. materialize and independently verify the exact six-file static root; and
2. persist and independently validate the exact static inventory and a
   current-tree receipt.

It does **not** execute or import the copied launcher, wrapper, extension, or
numerical libraries.  It does not run the future result-blind child or
authenticated runtime probe.  It does not observe import resolution, ABI
truth, loaded images, or the external Homebrew framework/standard-library and
macOS host boundaries.  It does not close the actual six role-v3 source files
plus global runner.  The receipt therefore cannot substitute for a runtime
probe, replay plan, external commitment, same-member receipt, continuum
estimate, or scientific result.

## 2. Recovered interruption point and prepublication audit

The interrupted implementation had three independent P1 defects:

1. live Darwin/APFS retained the OS-managed `com.apple.provenance` extended
   attribute after successful removal calls, while the prototype required an
   empty xattr list;
2. stage and nested object creation could precede ownership recording, so a
   restrictive caller umask or an error between create/open/stat/metadata
   steps could leave residue; and
3. the authenticated inventory bytes were checked for hash and schema but
   were not semantically joined to the configured authority root and six
   destination path/hash pairs.

The final repair:

- permits only the **name** `com.apple.provenance`, records the observed name
  list for every entry, rejects every other xattr name, and explicitly states
  that xattr values are neither read nor claimed;
- records create-time parent/name ownership bindings before stat, chmod,
  open, fstat, or metadata preparation can fail, normalizes directory modes
  independently of caller umask, and uses identity-checked rollback;
- requires exact equality between inventory `authority_root` plus the six
  primary path/hash pairs and the configured tree in both materializer and
  independent validator; and
- bounds JSON integer parsing before integer conversion and normalizes a
  missing validation parent into the component's fail-closed exception.

The final focused suite has **96/96** cases.  It includes real Darwin
materialize/reopen validation, required provenance-name observation,
unexpected-xattr rejection, `umask 0777`, stage and nested directory/file
faults, zero-residue checks, inventory root/path/digest/library mutations, and
receipt overclaim mutations.

The final prepublication read-only audit returned
`P0=0/P1=0/P2=0` against the exact frozen bytes below.

## 3. Frozen implementation bytes

| Object | SHA-256 | Bytes | Mode / links |
| --- | --- | ---: | --- |
| `code/materialize_continuum_c1_n0_sealed_runtime_root_v1.py` | `4a4210105c68ec7b4f5eb6354d657bc26e33992f07a54c80512f780415fea1ae` | 58,437 | `0444` / 1 |
| `code/validate_continuum_c1_n0_sealed_runtime_root_receipt_v1.py` | `737e8fdbb895680e6b6ed16ce53a95da493a1d29b5a3fecc0e37a5736e37c35f` | 35,341 | `0444` / 1 |
| `code/test_continuum_c1_n0_sealed_runtime_root_v1.py` | `d0365b45fb04c62b0ea20aa4fe191d49006d6fe38ac820f8fc3cbe11d13a5e06` | 52,942 | `0444` / 1 |

The materializer exposes only one public production API accepting the
authenticated inventory bytes.  It accepts no caller-selected root, source
layout, or syscall implementation and has no executable materialization CLI.
The independent validator likewise reopens only the one literal root.

## 4. Materialized root and persistent artifacts

The publication parent is current-user-owned mode `0700`:

```text
/Users/ae23069/.local-build/valley-k-small/runtime-authorities
```

The sealed root is:

```text
/Users/ae23069/.local-build/valley-k-small/runtime-authorities/
  encounter-c1-n0-cpython-3.12.13-gmpy2-2.2.1-arm64-v1
```

The independently walked tree contains exactly five directories and six
regular files, no symlink or other object, and 1,716,156 total file bytes:

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
      libmpfr.6.dylib                      0444
      libmpc.3.dylib                       0444
```

All entries have uid/gid `502/20`, zero BSD flags, no extended ACL, and exactly
the xattr name `com.apple.provenance`.  Each file has one link.  Directory link
counts for root, `bin`, `site-packages`, `gmpy2`, and `gmpy2.libs` are
`4,3,4,4,5`.

The six file hashes remain the Round-183 pins:

| File | SHA-256 | Bytes |
| --- | --- | ---: |
| `bin/python3.12` | `31b9c9a8d50289f3a13f014b3efd8ea3534fc3eea7ca7d9809e166139910b805` | 52,448 |
| `site-packages/gmpy2/__init__.py` | `3d4f21a0e9d6d32c935e3d39ef4be23a9a7d0ea56344ebbb0b8dca4f5651e8a2` | 412 |
| `site-packages/gmpy2/gmpy2.cpython-312-darwin.so` | `9586b7c4b887704b57576f52b73a8c45437946d2b172095d82c20fa0871a415b` | 573,056 |
| `site-packages/gmpy2.libs/libgmp.10.dylib` | `22cec4689e503d590cfbf3373ae7f442ef6d40c3e6c93a3612bbd1b7e2bce049` | 468,768 |
| `site-packages/gmpy2.libs/libmpfr.6.dylib` | `d314a427a901f8ece38b67966cd2fbf5642ceb7d1c2e5136f8282ca7ab859aed` | 469,360 |
| `site-packages/gmpy2.libs/libmpc.3.dylib` | `d3c10c39234c095f5c1938ad607c87a0633152f51271d9ed1c494724430c2b0c` | 152,112 |

The two persistent report artifacts are:

| Artifact | SHA-256 | Bytes | Mode / links |
| --- | --- | ---: | --- |
| `artifacts/data/continuum_c1_n0_runtime_byte_pin_inventory_v1.json` | `13b70ec6194bbad62e19cea2538f19a8351e6f6ad820ac7a09d0adf25433b8c6` | 11,715 | `0444` / 1 |
| `artifacts/data/continuum_c1_n0_sealed_runtime_root_receipt_v1.json` | `786d60ab405dac537377c162dab0c729292692525daffacaf7623799544ea08e` | 7,020 | `0444` / 1 |

The publication parent contains only the final root.  No materialization lock
or hidden stage residue remains.

## 5. Darwin xattr policy supersedes one Round-183 sentence

Round 183 required "no extended attribute" before live materialization had
tested APFS provenance behavior.  The final Darwin-correct policy deliberately
supersedes only that sentence:

```text
permitted xattr names = ["com.apple.provenance"]
xattr values read     = false
xattr values claimed  = false
every other name      = fail closed
```

The receipt records the observed names for exact current-tree comparison.
Neither materializer nor validator authenticates or interprets the provenance
value.  The same-UID hostile-writer and xattr-value boundaries remain outside
the component claim.

## 6. Independent postpublication acceptance

Two separate processes rebuilt or reopened the persisted objects after the
one-shot publication:

- the static-inventory validator reconstructed the exact 11,715-byte oracle
  from the six authenticated source byte images and frozen operation model;
- the receipt validator reopened the literal root through no-symlink
  descriptors, rehashed all six files, reconstructed all eleven entries, and
  exact-compared the canonical 7,020-byte receipt.

A separate read-only acceptance walk confirmed the counts, hashes, modes,
ownership, link counts, zero flags, zero ACL, provenance-name policy, and
absence of stage/lock residue.  Its component ledger is
`P0=0/P1=0/P2=0`.  Component-specific generated `.pyc` files created during
development were removed before final packaging.

The principal reproducibility commands are:

```bash
env PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B -m pytest -q \
  -p no:cacheprovider \
  research/reports/encounter_multimodal_prr/code/\
test_continuum_c1_n0_sealed_runtime_root_v1.py

env PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B - <<'PY'
from pathlib import Path
import sys
report = Path("research/reports/encounter_multimodal_prr").resolve()
sys.path.insert(0, str(report / "code"))
import validate_continuum_c1_n0_sealed_runtime_root_receipt_v1 as validator
inventory = (report / "artifacts/data/continuum_c1_n0_runtime_byte_pin_inventory_v1.json").read_bytes()
receipt = (report / "artifacts/data/continuum_c1_n0_sealed_runtime_root_receipt_v1.json").read_bytes()
validator.validate_sealed_runtime_root_receipt_v1(receipt, inventory)
PY
```

The materializer is intentionally one-shot: a second call holds because the
fixed root already exists.  Normal continuing validation uses the independent
receipt validator, not rematerialization.

## 7. Integrated ledger and provenance stop rule

At complete replay-readiness scope the ledger remains:

```text
P0 = 0
P1 = 2
P2 = 4
```

The two P1 blockers are still:

1. no result-blind wrapper-import child, two-run authenticated runtime probe,
   or trusted origin classifier/adapter exists; and
2. no v3 precommit adapter or end-to-end actual closure over the six
   numerical role-v3 sources plus global runner exists.

The four P2 items remain the absent role-8 numerical pair, absent role-9
numerical pair, absent role-10 numerical pair/global runner, and absent
replay/acceptance/later-continuum evidence.

Final gate state:

```text
external authority root                          = MATERIALIZED / VALIDATED
persistent static inventory / root receipt       = PRESENT / VALIDATED
sealed-root materializer / independent validator = FROZEN / 96 TESTS
result-blind runtime child / authenticated probe  = ABSENT / ABSENT
trusted origin classifier/adapter                 = ABSENT
actual six-source-plus-runner runtime closure     = ABSENT
role-8/9 numerical implementations                = 0/4
all role-v3 numerical implementations             = 0/6
global runner                                     = ABSENT
plan / bundle / request / commitment              = ABSENT / ABSENT / ABSENT / ABSENT
candidate execution / output / replay             = NONE / ABSENT / NOT PERFORMED
B06 structural remedy prepared / cleared          = FALSE / FALSE
same-member acceptance                            = FALSE
C1--C3 / F0--F3 / root transfer                   = FALSE
release / submission                              = FALSE
```

Round 184 is the provenance stop line for static-root engineering.  A future
runtime step should be the smallest result-blind wrapper-import observation
needed by the existing plan, not a broader hostile-writer, full-OS-byte, or
cryptographic-provenance project.  The scientific priority remains actual
roles 8--10, one correlated production `n=0` same-member receipt, numerical
evaluation of the C2 constants, the positive-time C3 box-truncation bounds,
and then componentwise root transfer.

The report directory is still outside the current Git tracked baseline.
Round 184 therefore has exact internal hashes, frozen modes, persistent
artifacts, and live validator evidence, but no repository commit history.
That project-level provenance limitation is not repaired by the sealed root
and should not be hidden by its component PASS.
