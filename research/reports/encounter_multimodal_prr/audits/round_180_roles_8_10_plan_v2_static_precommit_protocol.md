# Round 180: roles 8--10 plan-v2 static precommit protocol

Date: 2026-07-19

Status: **STATIC RESULT-BLIND PROTOCOL BYTES FROZEN / SYNTHETIC PACKAGE
VALIDATION ONLY / P0=0/P1=0/P2=4 / NO REAL RUNTIME CLOSURE, PLAN,
BUNDLE, REQUEST, COMMITMENT, OUTPUT, OR RECEIPT / NO B06, SAME-MEMBER,
C1--C3, F0--F3, ROOT, RELEASE, OR SUBMISSION PROMOTION**

## 1. Scope and nonclaim boundary

Round 180 freezes the pure plan-v2 vocabulary, an independent static package
validator, and its synthetic positive/adversarial test suite.  The validator
authenticates the frozen Round-179 operation-model-v2 bytes and checks the
static joins of a hypothetical runtime-closure-v1, replay-plan-v2, and
candidate-bundle-v2 package.  Every package used by the tests is created only
below `pytest` temporary directories.

This round does **not** instantiate any report-local runtime closure, replay
plan, candidate bundle, request-v4 file, external predecessor commitment,
role output, or receipt.  It does not create the six role-v3 entrypoints or the
global runner.  Its success ACK is deliberately

```text
PASS_RESULT_BLIND_PRECOMMIT_PACKAGE_V2_STATIC_STRUCTURE_ONLY_NO_EXECUTION_RESULTS
```

and is not runtime truth, replay readiness, numerical correctness, scientific
acceptance, or release evidence.

## 2. Frozen reviewed bytes

| Role | Report-relative path | SHA-256 / properties |
| --- | --- | --- |
| pure protocol constants | `code/continuum_c1_n0_roles_8_10_protocol_constants_v2.py` | `4f0dbf1a243a9157f11176b89a3b27833cf6ccc76230cf976a1a985cbb178b15`; 18,710 bytes; `0444`; nlink 1 |
| independent static validator | `code/validate_continuum_c1_n0_roles_8_10_precommit_package_v2.py` | `e1ab7c1eb4d8d1f8a9f3f2e0298513727d04c1dc93628fa2886bf9d4a81c991a`; 92,350 bytes; `0444`; nlink 1 |
| synthetic positive/adversarial tests | `code/test_continuum_c1_n0_roles_8_10_precommit_package_v2.py` | `7d02c09c165b0dcbce5eef5fb85cda02b74db054162adff6d59ec87decbf4443`; 41,954 bytes; `0444`; nlink 1 |

The validator opens the sibling constants file only after exact `0444`,
single-link, stable-identity, and SHA-256 authentication.  It then joins every
used plan, entry, slot, runtime, request, bundle, role, method, authority,
digest-domain, runner, and resource-cap constant back to the authenticated
operation-model-v2 contract.  The operation-model root remains
`ac0c2b185be75f0ecef3e331fdfd47fc674ca151fa6b26600aff9f789a2f8a6b`.

## 3. Static protocol properties established

The frozen validator establishes only the following static properties for a
candidate package presented to it:

- canonical ASCII JSON, duplicate-key rejection, strict recursive JSON type
  equality, exact keys, exact `0444` JSON/source/dependency/native modes, and
  exact `0555` Python-executable mode;
- authenticated operation-model, authority, member-v4, registry-v4, sealed
  mirror, runtime-manifest, plan, and bundle byte pins;
- exact plan-v2 role order `[8,9,10]`, ten ordered slots, three request slots,
  seven output slots, role-specific methods, authorities, invocation argv, and
  entry projection digests;
- recomputation of the member identity plus the configuration-row and
  partition inventory digests from authenticated source authorities;
- authentication of all 40 sealed-mirror entries and rejection of every
  missing or extra file/directory, with the mirror root and all directories
  included in output/input path disjointness;
- producer/verifier report-local source separation within each role and across
  the global producer-side/verifier-side unions;
- a non-side-effecting, root-reachable import-graph fixed point that rejects
  missing records and disconnected dependency components while permitting a
  reachable cycle;
- a strict source profile that forbids dynamic execution/import primitives,
  aliased dynamic imports, ambiguous general `from ... import ...` forms,
  legacy scientific imports, result paths, and result payload vocabulary;
- explicit HOLD for any non-null `allowed_shared_protocol` until an exact
  frozen semantics-free byte allowlist exists;
- absence of all ten future request/output slot paths at static validation
  time; and
- claim wording limited to static joins under the explicitly non-byte-complete
  host boundary.  The plan and bundle execution, release, and same-member
  claims remain false.

## 4. Adversarial repair chronology and tests

Successive red-team passes found and repaired:

1. ancestor-directory timestamp false positives in descriptor-anchored reads;
2. `False == 0` / `True == 1` acceptance in claims, slots, and partition rows;
3. cross-role producer/verifier byte reuse;
4. an unreachable cyclic dependency component accepted as a fixed point;
5. ambient `find_spec` resolution and possible parent-package execution;
6. inventory digests compared only with constants rather than recomputed;
7. sealed-mirror sibling files and output descendants not covered by the
   authenticated input tree;
8. dynamic-import aliases and ambiguous from-import submodule loading;
9. an unrestricted shared protocol capable of carrying numerical/result
   constants; and
10. non-exact immutable modes and an unsealed constants import surface.

The final focused command was

```bash
PYTHONPYCACHEPREFIX=/tmp/round180-pycache \
  .venv/bin/python -m pytest -q \
  research/reports/encounter_multimodal_prr/code/test_continuum_c1_n0_roles_8_10_precommit_package_v2.py
```

Observed results:

- focused tests: **42/42 PASS**;
- Ruff: **PASS**;
- `py_compile`: **PASS**, with cache redirected outside the report tree;
- direct Python API and separate CLI synthetic positives: **PASS**; and
- no test-created artifact outside `pytest` temporary directories.

The mutations cover plan-v1 downgrade, every Boolean/integer alias class,
slot reordering, inventory drift, mirror-tree extension, dynamic-import
aliases, shared-protocol insertion, mirror-descendant output, transitive
runner numerical import, opposing-side source reuse, unreachable/reachable
cycles, forbidden result fields/values, role-10 invocation and method drift,
partition drift, all ten pre-existing future slots, and exact-mode drift.

## 5. Residual P2 boundaries

The final static-protocol ledger is

```text
P0 = 0
P1 = 0
P2 = 4
```

The four P2 items are mandatory pre-replay HOLD boundaries:

1. **Actual runtime truth is absent.**  The synthetic fixture does not prove
   that a pinned file is the claimed CPython interpreter, that ABI/version
   strings were observed from it, or that `gmpy2` links the pinned
   GMP/MPFR/MPC images.  Builtin/frozen and host carrier bytes remain inside
   the operation model's explicit non-byte-complete trust boundary.
2. **The role-v3 implementations are absent.**  Static source/dependency
   separation does not prove numerical completeness, independent algorithms,
   role-10 verifier-to-producer internal staging, or scientific correctness.
3. **The global runner is absent.**  Therefore the single descriptor-anchored
   all-seven-output preflight, exact role launch graph, request/commitment
   authentication, launch-time freshness, and post-run output authentication
   have not occurred.
4. **The optional shared protocol is intentionally unsupported.**  A future
   non-null shared protocol requires a separately frozen exact byte allowlist
   and fresh adversarial review; until then every such package is rejected.

The Round-179 host-runtime and cleanup/recovery limitations also remain in
force.  None of these items may be relabeled as a result or scientific gate.

## 6. Final gate ledger

```text
operation-model-v2                              = FROZEN PROSPECTIVE CONTRACT
plan-v2 constants / static validator            = FROZEN; STATIC SCOPE ONLY
synthetic package tests                         = 42/42 PASS
real role-v3 numerical entrypoints              = ABSENT
real global runner v2                           = ABSENT
real runtime-closure-v1                         = ABSENT
real replay-plan-v2 / candidate-bundle-v2       = ABSENT / ABSENT
external predecessor commitment                 = ABSENT
request-v4 files / role outputs / receipts      = ABSENT
B06 structural remedy prepared / cleared        = FALSE / FALSE
fresh roles 8--10 replay                         = NOT PERFORMED
same-member acceptance                          = FALSE
C1--C3 / F0--F3 / root transfer                 = FALSE
release / submission                            = FALSE
```

The next valid step is to implement and independently audit the future role-8
and role-9 v3 source-separated entrypoints, then the role-10 v3 transaction
and global runner, before any real runtime closure or plan-v2 package can be
materialized.
