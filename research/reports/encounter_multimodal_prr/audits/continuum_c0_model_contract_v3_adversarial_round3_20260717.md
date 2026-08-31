# Continuum C0 model contract v3: adversarial round 3

Date: 2026-07-17

Status: **LOCAL HASH-SPECIFIC SEMANTIC/WELL-DEFINEDNESS PASS / P0=0 / P1=0 / ONE NONBLOCKING P2 / COMPLETE C0 HOLD / COMPLETE C1 HOLD / PRR RELEASE HOLD**

## Decision

The immutable C0-v2 semantic candidate and the versioned C0-v3
well-definedness wrapper pass their final local producer, verifier, geometry,
currentness, open-set, and mutation checks.  This is an implementation and
mathematical-contract result only.  It is not external referee acceptance and
does not establish complete C0.

The exact control values still require a separately sealed, result-blind,
independently reviewed source.  The production raw-mass/rate intervals have
not been mapped through an outward-enclosed global gauge, so the production
raw-to-gauged bridge remains open.  Complete C1, quantitative C2, box C3,
topology transfer, release, and submission therefore remain on HOLD.

## Exact final bytes

Frozen source and artifact bytes:

- configuration-family source:
  `063913c7fbc2b706ba85a0e3f06005bad23a2292749817294cbf41f5cdce4084`;
- control-method commitment v2:
  `288ad85d5992446a8f3b58416e445a88f1c15a4c71114ba008939d8fbd9a4a97`;
- physical initial source:
  `0b2efec5dc1abea1380ab862e46825e7b79658fe9bfa0ac6637e1426ed9f7f5f`;
- killing-geometry source:
  `5543f76031d731cb5bcf3e4cdf3bdabaffacb2053400e3015d6ab57906a27669`;
- mathematical source v2:
  `522bd667e5f6fd6a4d12f270f0c2f4b9e86be9b207d471961d4f67db972df559`;
- measure/partition preconditions v1:
  `652e0b1a1528eebff2f78ae4aae7854412da03ad8d5ad33887c77a072d439d15`;
- immutable historical C0-v1 artifact:
  `5bbe7d3c265736f98f0025a8aad80d83a53e464a5349d6b6be57a096ba9cdf66`;
- immutable C0-v2 artifact:
  `688ec0416e414737705631852bb5ecf44530c5fe93e3ca95f3dfdbe8807ead7e`;
- immutable C0-v3 artifact:
  `5457f391ccfb59c5415302a4776219641305914b63c6933b222541cae746f239`;
- current C0-v1 staleness sentinel:
  `e8388fca8888c35d18a154bcba555117366b4adee3e74eb9908a8108ee8799e9`;
- current strict-continuum program note:
  `15d49113c7cca0f0b69b5bc918d3b4565752ef2ef32de5c3f92d09a927a4b1c6`.

Final implementation bytes:

- v2 producer:
  `a369c2f2a85cf30fe6e5ec572501fe4f77b6225a993cb8e861553a4ec614adbb`;
- v2 verifier:
  `d62ff81c23a6cd6673f434220a4b1b249f824c6ffe90b2d5a519ba7b8c4d39c3`;
- v2 static tests:
  `461e14ac8ebac9f02fcd77512734c69b920d9a07b27850307efc2de018fb7528`;
- v2 currentness tests:
  `8db63638520eff8f8a5cd2b454eb5a1c51f78dca01387507e7716c520865ce0a`;
- v2 adversarial tests:
  `63e004d8237f73690c9b124a93ace7ac6f265957a96183e5651487f3c1af0287`;
- v3 producer:
  `ce6138f2acf8343c3b31cc506679966789e230c7894ad46b5847242049812f9b`;
- v3 verifier:
  `3f43da56bfe580e27b124ee3bcb6a6cb8326c5d0fe0901d73e6caac10dd9e2c0`;
- v3 static/open-set tests:
  `91d93c2b976adacb05031a549b7e8e79f301ba020c42d9d30656c554beec11e5`;
- v3 adversarial tests:
  `0c3329d72eab4aa4823e14d9a747446f8f81e9484e0e081f2291e4c5ec943dc5`.

The active manuscript bytes remain unchanged:

- main TeX:
  `10d62404f15e306072e093aaa6fa5abbf5f6bdb0ecb42a341e3740dcf77aac2c`;
- seven-page main PDF:
  `577d2d4b494633a3e009f13fbd581a9c889d7c84fd11c18e5b3367a6e4b1a42e`;
- 23-page Supplemental PDF:
  `70de25968298d58222bbab10639a2253067f5c01d4d6462d743e3e6eca5790fb`;
- fail-closed compile manifest:
  `704c96f173c51423457ef8b03fa8ee914ec10bedebc3e6aa435965991d34a6ea`.

## Version chronology

### C0-v1: immutable historical HOLD

C0-v1 predates the exact denominator decision for the weighted cell map and
pins a living program-note hash that has since changed.  Its original verifier
also included a scratch result file in its source-hash surface.  The v1 bytes
were not edited or re-signed.  The current staleness sentinel correctly expects
`HOLD_C0_CONTRACT_SOURCES`.

### C0-v2: result-blind semantic repair

C0-v2 was built from five explicit C0-only source roles and one immutable v1
auxiliary artifact.  It does not open the living continuum note, the
positive-budget design note, or a scratch/result payload.  It freezes:

- actual control volumes `C_i`, including endpoint half volumes and wrapped
  periodic pieces;
- `J_h` as piecewise-constant reconstruction;
- `P_h=J_h^*` with denominator `pi_h_i`;
- `A_h` as the literal `pi`-weighted cell average with denominator `M_i^pi`;
- `S_h` only on a smooth or continuous recovery core;
- `rho_i=M_i^pi/pi_h_i` and the exact identities
  `P_h=diag(rho_i)A_h`, `A_hJ_h=I`, `P_hJ_h=diag(rho_i)`,
  `J_hA_h=E_h`, and `J_hP_h=rho_h^pc E_h`;
- the absence of operator-norm convergence for `J_hP_h`;
- the global box-mass gauge
  `g_h,L=M_L/sum_i tilde_pi_h_i`, without cellwise mass equality or
  normalization to one;
- row-generator, forward-probability, density-ratio, and undirected-edge
  conventions; and
- exact initial physical cell masses with no meshwise renormalization.

The v2 verifier checks the initial support closure strictly inside all 12
declared nonperiodic boxes: 24 nonperiodic axes, 12 periodic axes, 48 strict
side inequalities, and exact minimum clearance
`106645239176133349/288230376151711744`.

### C0-v3: versioned well-definedness repair

A separate mathematical review found a P1 in the v2 contract surface:
measurable partition, positive physical cell volume, and positive mass/
denominator assumptions were implicit rather than machine-readable.  The v2
artifact was retained unchanged.  C0-v3 wraps that exact v2 hash and a new
canonical precondition source which states:

- measurable, pairwise-disjoint-up-to-null-sets control volumes covering the
  fixed box;
- positive finite physical volume for every declared cell;
- finite positive `M_L` and positive `M_i^pi`;
- finite positive raw masses and their sum;
- finite positive `g_h,L` and `pi_h_i`; and
- the resulting well-definedness of `A_h`, `P_h`, `E_h`, `rho_i`, the adjoint
  identity, and the positive-weight Hilbert space.

The independent geometry computation accounts for:

- 12 configurations;
- 36 axis partitions;
- four vertex-dual axes with positive endpoint half volumes;
- two half-shift periodic rows with explicit wrapped cells; and
- 34,787,462 tensor cells, matching every shape, per-row state count, and total
  workload.

These conditions are ideal-model preconditions.  They are not a production
interval proof.

## Robustness-review chronology

Successive local reviews first returned HOLD and then verified the repairs.
The final implementation closes all blocking findings found in this round:

1. deep JSON and over-wide JSON integers now become stable encoding HOLDs
   instead of raw `RecursionError` or `ValueError`;
2. both direct-byte parsers and file readers enforce the 32 MiB limit, and the
   read loop stops immediately if a concurrently growing file crosses it;
3. the path scanner rejects directory components and bare or suffixed
   `result.json`, `results.json`, `control.json`, and `controls.json` forms;
4. frozen-source SHA comparison occurs before JSON parsing or semantic scans;
5. source reads traverse every relative component descriptor-wise with
   `O_NOFOLLOW` and `O_DIRECTORY`;
6. one-shot publication traverses the absolute parent chain descriptor-wise,
   creates a mode-`O_EXCL` temporary file, hard-links without overwriting, and
   never follows a symlinked parent;
7. read-time `OSError` and malformed exact witnesses become stable HOLDs;
8. v3 claim, base, precondition, geometry, result-blindness, and encoding
   failures have distinct categories; and
9. the v3 actual unique JSON dependency set equals the paths declared in its
   receipt, with all observed JSON opens read-only.

The physical initial source is not rewritten merely to sort its historical
keys.  It is the single explicit legacy-ordering exception: its exact bytes are
SHA-pinned, the same snapshot is hashed and parsed, and duplicate keys,
nonfinite values, floats, BOMs, schema drift, and result-bearing paths remain
rejected.  The other five current source roles are canonical JSON.

One nonblocking P2 remains: `read_regular_snapshot` applies `O_NOFOLLOW` to the
final component of an arbitrary user-supplied CLI candidate path rather than
walking that parent path descriptor-wise.  The default path is derived from a
resolved module location, and every accepted candidate must still match exact
hash and full semantic schema, so this does not provide a claim-promotion or
byte-integrity bypass.  Frozen source paths and publication paths already use
the stronger component-wise traversal.  This may be hardened in a future code
version without altering the frozen v2/v3 artifacts.

## Executed checks

- v2 producer `--check`: PASS, complete C0 false;
- v2 independent verifier: PASS, production bridge false;
- v3 producer `--check`: PASS, complete C0 false;
- v3 independent verifier: PASS, geometry receipt exactly as listed above;
- focused C0-v2/v3 suite: 86/86 PASS;
- current C0-v1 staleness sentinel: 1/1 PASS;
- C1 static and adversarial suite: 23/23 PASS;
- theorem-first plus living scope guards: 9/9 PASS;
- combined strict-continuum regression: 119/119 PASS;
- Ruff on all v2/v3 producer, verifier, and test modules: PASS;
- `py_compile` on all four v2/v3 producer/verifier modules: PASS;
- independent LaTeX skill smoke build: PASS, seven-page main PDF in an isolated
  temporary directory;
- project fail-closed compiler: PASS, reproducing the exact seven-page main and
  23-page Supplemental hashes above;
- compile/status/historical-freeze regression: 29/29 PASS; and
- report registry, archive manifests, documentation paths, scientific
  guardrail wiring, and summary refresh: PASS.

The 29-test freeze regression initially exposed two historical tests that
still treated living scope-test files as immutable Round-166/167 bytes.  Their
old hashes were already preserved in the immutable audits.  Only the living-
successor sets were corrected; no historical audit, frozen stage artifact, or
manuscript source was rewritten.

## Audit provenance and contamination boundary

The accepted final review used explicit file paths only, no directory globs,
no embedded-path following, and no network calls.  It independently repeated
the 86 tests and four CLI checks on the final hashes without editing them.

A separate helper review accidentally invoked a byte-count command with a
directory wildcard.  That command opened result-bearing paths and printed only
filenames and byte counts; it displayed, parsed, and used no scientific values.
Because its process was no longer cleanly result-blind, none of its open-set
evidence is used for this decision.  The accepted open-set evidence comes from
the explicit-path clean review and the instrumented v2/v3 regression tests.

## Retained nonclaims and next route

This round does not establish:

- exact control values or complete C0 acceptance;
- outward interval enclosure of the global gauge, gauged masses, or common
  conductances for every production configuration;
- a production-centre convergence theorem;
- relative/periodic/tensor/vertex free-form Mosco convergence;
- sharp-contact killing consistency;
- the positive-time functional-calculus bridge;
- quantitative C2 spatial error, C3 box error, or continuum root transfer;
- F0, F1, F3, positive-budget science, release eligibility, or submission.

The next strict-continuum sequence is:

1. create and independently review a sealed exact-control source without
   opening prospective outputs;
2. close the remaining C0 acceptance obligations over the immutable v3
   candidate;
3. freeze the C1 data-approximation contract;
4. prove the relative OU, periodic, tensor, and vertex-dual free-form
   extensions;
5. add sharp-contact killing consistency;
6. prove the positive-time functional-calculus bridge; and only then
7. construct quantitative C2/C3 ledgers and a componentwise root-transfer
   certificate.

The active theorem-first main text remains seven pages because the complete
derivations and auditing material live in the 23-page Supplemental document.
The 7+23 split is normal for this working architecture and is not evidence of
missing content.
