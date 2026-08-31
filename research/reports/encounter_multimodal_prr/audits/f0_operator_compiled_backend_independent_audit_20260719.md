# F0 operator and compiled power-stream independent audit

Date: 2026-07-19  
Role: independent read-only numerical-method reviewer  
Decision: **ACCEPT METHOD LAYERS / P0=0 / P1=0 / P2=0 / NOT AN F0 ACCEPTANCE**

## Exact reviewed bytes

| Object | SHA-256 |
| --- | --- |
| compiled Python wrapper | `13c7fabd4118c3858b03d839dcfea037eb15eb6b64b08f7fb69f0757342eae55` |
| compiled C source | `9db8c672a04732b23dedb332854c4f4259911cfac32ec130d1d16b64db274917` |
| compiled focused tests | `513c0ce06b4424c4a8c3cf6cfea3bb21cd588fc389af8a9e760e451fb9b6dd51` |
| compiled benchmark | `b58fa1213913e6042be87010e974bb450f4a76913adc078b423e4552950d28b3` |
| production-operator source | `dc46bbf39c72df547e7bd9f5364969b0b39293f84db19509353a712221bb5908` |
| production-operator focused tests | `b22c446aa747449a486818d5ce14af46a8a9bc3c6a55da84bababbd7f4ecfe1c` |
| current arm64 compiled binary | `74eaa6adcc903993ed48716b9d76b56c2993d3facabcaa5842512147d76aea0f` |

The compiler binary hash was
`179301dcb41ea78accc3fa0048a7e6f6710d891945a751a34addd622020c1818`;
the compiler-identity hash was
`ea3037e0630fa16798079372fdc24f6542d021dadda4915cc979799682d78295`;
and the normalized command hash was
`7be63a3dc99dc9253924a380b138e38692e75242b63eaa9929472bc3ac26e930`.

## Rebuild and runtime checks

- The focused method suites returned `39/39 PASS`; Ruff also passed.
- Apple clang 21 on arm64 rebuilt the dynamic library in two independent
  temporary directories and in multiple fresh processes.  Every rebuilt
  binary had the exact hash shown above.
- The compiler command contained
  `-ffp-contract=off`, `-fno-fast-math`, `-fno-associative-math`,
  `-fno-unsafe-math-optimizations`, and `-frounding-math`.
- Runtime probes confirmed binary64 arithmetic, `FLT_EVAL_METHOD=0`,
  `FE_TONEAREST`, and preservation of subnormals.  Disassembly contained no
  fused multiply-add or pairwise-reduction instruction in the audited loops.

## Independent numerical replay

Independent dense and exact-`Fraction` fixtures covered one, two, and three
dimensions and all fourteen reflecting/periodic combinations, including the
size-two periodic case in which the two directed neighbours coincide.  They
replayed the indexing and the declared operation order rather than importing
the producer's action helper.

The audit also used two exact underflow witnesses:

- an action term with exact value `2^-1075` and binary64 nominal value zero;
- a killing-dot term with exact value `2^-2096` and binary64 nominal value
  zero.

Both exact values were contained by the declared roundoff/underflow
enclosures.  Ordinary mass and killing-dot `Fraction` values were also
contained.

All native inputs are private, owned, C-contiguous, and read-only copies.
Mutating the caller's original arrays did not alter the backend.  All returned
arrays own their bytes, have `base is None`, are read-only, and reproduce
byte-for-byte.

## Operator boundary

The fixed neutral and fixed heterogeneous templates were reconstructed from
their literals.  The heterogeneous two-state generator is

```text
Q = [[-5/8, 1/2],
     [ 1/4,-3/4]]
```

with stationary masses `(1,2)` and killing `(1/8,1/2)`.  Its detailed-balance
identity is `1*(1/2)=2*(1/4)`.

Caller-supplied endpoints return only `OpaqueCallerOperatorAnalysis`; no
kernel or stationary-mass object is exposed.  Same-process source hashes are
explicitly non-authoritative and require an external exact-byte audit.
Seventeen receipt-consistency mutations were rejected.

## Acceptance boundary

This audit accepts the compiled action/reduction method and the two closed
operator fixtures at the exact bytes above.  The generic compiled backend,
stream result, fixed operator, and opaque caller analysis all retain
`science_executed=false`, `resource_pass=false`, and `f0_pass=false`.

The Linux build branch was not executed on this macOS host and is outside this
host-specific F0 route.  This record does not certify scalar uniformization,
topology, the largest-shape resource schedule, a canonical F0 candidate, or
any positive-budget row.
