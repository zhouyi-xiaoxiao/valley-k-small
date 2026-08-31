# Continuum C0 model-contract candidate: result-blind pre-audit

Date: 2026-07-16

Status: **C0 CONTRACT CANDIDATE CONSTRUCTED / SELF-CHECK PASS / HOLD INDEPENDENT THEORY AND HASH AUDIT / C1--C3 OPEN**

## Exact candidate

- model-contract candidate SHA-256:
  `5bbe7d3c265736f98f0025a8aad80d83a53e464a5349d6b6be57a096ba9cdf66`;
- mechanical test SHA-256:
  `673da175232fa7496a151aa19d06fd45d33843dd9cf68635082f741af6b7b681`.

The contract is
`artifacts/data/continuum_c0_model_contract_candidate_v1.json`.  It binds the
already frozen model inputs without reading a positive-budget scientific
output.

## Bound mathematical object

The candidate fixes, in one machine-readable object:

1. physical `d=2` and the three-coordinate quotient
   `R_z x R_r_parallel x T_W`;
2. exact dyadic `D`, `gamma`, `zbar`, `W`, contact radius and installed budget,
   with explicit units;
3. `Dmat=diag(D/2,2D,2D)`, the anisotropic reversible density and the
   coefficient identity `Dmat grad(log pi)=b`;
4. the natural-decay target realization versus artificial reflecting finite
   boxes;
5. the unit-mass compact initial source, sharp minimum-image contact disk and
   four unit-integral compact support profiles;
6. the three exact controls through the already frozen opaque selector hash,
   without copying result fields into the contract;
7. all 12 finite-volume configurations, their four alignment classes and the
   declared midpoint/relative box-nesting relations;
8. the stationary-mass gauge, piecewise-constant `J_h`, weighted-cell-average
   `P_h`, initial projection and physical-volume killing projection; and
9. the complete equation list (2.0)--(2.17) and all downstream nonclaims.

## Reproduced checks

The first implementation-side test run passed 6/6 checks.  It verifies exact
source hashes, parameter hex-to-rational equality, dimensions and units,
`2a<W`, the reversible drift identity, initial mass, result-blind killing
flags, configuration order, alignment classes, box nesting and the strict
natural-decay/reflecting-approximant distinction.  Ruff and `py_compile` pass.

The combined continuum/general-dimension/living/theorem-first scope run first
exposed five stale-baseline failures predating this candidate: one test still
called the pre-C0-A continuum hash current, the general-dimension freeze still
called Round-167 README/contract bytes current, and the living README test did
not recognize its explicit sentence that F0 and all 36 F1 rows remain open.
Those tests now preserve the old hashes through the immutable Round-167 audit,
freeze the living successor candidates separately, and retain exact-byte
mutation rejection.  The repaired combined scope run passes 29/29 tests.

## Adversarial obligations before C0 acceptance

An independent review must still attack:

- whether the opaque selector hash and exact weight-location rule uniquely
  determine all three controls without importing any result-dependent choice;
- dimensional consistency of the `W^{-1}` convention and installed-budget
  unit under the omitted common transverse centre coordinate;
- whether the stated `J_h/P_h` maps are sufficiently explicit at half-volume
  vertices and wrapped periodic cut cells;
- whether the stationary-mass gauge can be computed and enclosed for every
  declared box without circular use of a prospective result;
- completeness of the equation/source inventory and absence of an undeclared
  parameter default;
- one-byte, role-swap, unit-swap, decimal-for-dyadic, boundary-condition and
  box-order mutations.

Until those attacks pass, `complete_c0_independently_accepted=false`.  This
candidate does not establish C1 Mosco convergence, C2/C3 quantitative errors,
finite-volume root transfer, F0, any positive-budget modality, or release.
