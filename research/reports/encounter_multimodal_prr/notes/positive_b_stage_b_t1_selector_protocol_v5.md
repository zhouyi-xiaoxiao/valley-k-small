# Stage-B-v5 frozen-name bridge to T0 selector protocol v3

Date: 2026-07-14  
Status: **ROUND-94 REPAIR CANDIDATE / HOLD-INDEPENDENT-ATTACK**  
Authorization: **AUTHORIZED-SCIENTIFIC-COMMAND: NONE**

The accepted Stage-B-v5 design froze this bridge filename and the substantive
source filename `code/positive_b_stage_b_t1_selector_v5.py`. The unique source
remains the implementation; `code/positive_b_stage_b_t0_selector.py` remains a
fail-closed tombstone.

The normative operational protocol is now
`notes/positive_b_stage_b_t0_selector_protocol_v3.md`. Protocols v1 and v2,
Round 81, and its rejecting Round-93 attack are historical evidence only. In
particular, v2's pathname-reopened wrapper and its stronger executed-byte or
zero-execution language are not current claims.

## Mandatory future-T1 consumption

A future T1 must:

1. start the pinned CPython with `-I -S`;
2. descriptor-read and hash the external production attestation against the
   digest already frozen in T1;
3. descriptor-read/hash the exact loader named by that record and
   `compile+exec` those retained loader bytes, never reopen its pathname for
   execution;
4. require the exact `trust_contract` data mapping specified by protocol v3;
5. let the loader capture critical builtins/import-machinery identities,
   descriptor-capture the selector and `gmpy2/__init__.py` bytes, and verify
   the exact static package/native/library closure;
6. load the native extension by its verified absolute path, execute only the
   retained wrapper bytes in the prepared package namespace, and execute only
   the retained selector bytes under a fresh private name;
7. require all pre/post and public-call identity guards, including the guard
   immediately before output-byte construction; and
8. accept only output with exact production schema/status/mode/eligibility,
   external-record digest, and trust-contract mapping.

The exact production tuple is:

```text
record schema       = positive-b-stage-b-t0-external-attestation-v2
record status       = INDEPENDENT-ATTACK-PASS
entry mode          = VERIFIED-ISOLATED
production_eligible = true
```

The synthetic tuple is different in every field and is non-promotable:

```text
record schema       = positive-b-stage-b-t0-synthetic-test-attestation-v2
record status       = NON-PROMOTABLE-SYNTHETIC-TEST
entry mode          = VERIFIED-ISOLATED-SYNTHETIC-TEST
production_eligible = false
```

## Exact scientific-integrity boundary

The invoked CPython executable, builtins, standard library/import machinery,
OS loader/system libraries, and absence of a hostile same-UID writer for the
attested runtime tree throughout load and public calls are an external trust
contract. The Python wrapper is executed from authenticated descriptor bytes.
The native extension and bundled dylibs remain path-loaded under that
contract.

This package provides defense in depth against accidental/static drift. It
does not claim an OS-enforced immutable namespace, cryptographic closure of
every executed byte, universal TOCTOU resistance, or protection from an
adversarial process with the same UID. If the external contract cannot be
accepted, future T1 must HOLD or use a genuinely immutable/different-UID
runtime boundary.

Every output must self-describe that limitation through
`package_runtime.trust_contract`. Documentation alone is not sufficient.

## Current boundary

No production attestation exists. It may be created only after a fresh
independent result-blind attack accepts the exact Round-94 repair bytes. Until
then:

```text
ROUND-94 REPAIR CANDIDATE
HOLD-INDEPENDENT-ATTACK
SCIENTIFIC OBJECT/VALUE/RESULT: NOT READ / NOT RUN / NOT CREATED
AUTHORIZED-SCIENTIFIC-COMMAND: NONE
```
