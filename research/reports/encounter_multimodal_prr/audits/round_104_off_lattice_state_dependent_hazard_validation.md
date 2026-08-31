# Round 104 — off-lattice state-dependent hazard validation

Date: 2026-07-14

Scope: method-only compiled substrate; no scientific event ensemble was run

Verdict: **ACCEPT for bounded method fixtures; HOLD for scientific production and claims**

## 1. Claim boundary

This round extends the isolated compiled off-lattice Doi core from its
constant-hazard validation channel to a physical broad-four-slab,
state-dependent hazard. The implementation, parser, resumability metadata,
and independent scalar replay pass the bounded validation described below.

This is not a scientific result. No scientific estimand, comparison protocol,
window, run size, or randomization schedule has been frozen; no scientific
event ensemble has been executed; no modality, mass, survival, or journal
claim has been released. The runtime operational JSON keeps every scientific
and production claim flag false.

## 2. Frozen method geometry and hazard

The two-particle geometry is the same two-dimensional quotient used by the
off-lattice model: the longitudinal coordinate is unbounded and the transverse
coordinate is periodic with width \(W=1\). In midpoint/relative coordinates,

\[
z=(M,R_{\parallel},R_{\perp}), \qquad
\bar R_{\perp}=R_{\perp}-\left\lfloor R_{\perp}+\tfrac12\right\rfloor .
\]

Disk contact is the strict indicator

\[
\chi_a(z)=\mathbf 1\!\left\{R_{\parallel}^2+\bar R_{\perp}^2<a^2\right\},
\qquad a=0.16.
\]

Let

\[
b(u)=
\begin{cases}
\exp[-1/(1-u^2)], & |u|<1,\\
0, & |u|\ge 1,
\end{cases}
\qquad
I_b=0.4439938161680794,
\]

and

\[
\phi_s(x)=\frac{b(x/s)}{s I_b}, \qquad s=0.04.
\]

The four slab centres are \(m=(0.35,0.60,0.75,0.90)\). For any accepted input
weight vector with four finite nonnegative entries and binary64 sequential sum
within \(2\times10^{-14}\) of one, the implemented hazard is

\[
K(z)=\frac{B}{W}\,\chi_a(z)\sum_{j=1}^{4} w_j\phi_s(M-m_j),
\qquad B=0.01.
\]

The broad mode requires the exact binary64 value \(\Lambda=0.35\), and the
otherwise-unused constant-hazard field must be exact positive zero. The four
weights, hazard-mode tag, and all other method metadata are serialized into raw
schema 2 and attested through the resume plan and ledger.

## 3. Pointwise domination proof and runtime guard

The supports are pairwise disjoint because every centre separation is greater
than \(2s\). Also,

\[
I_b\ge \int_{-1/2}^{1/2} b(u)\,du \ge e^{-4/3},
\qquad \max_{|u|<1} b(u)=e^{-1}.
\]

Therefore at most one slab contributes at any midpoint and

\[
K(z)
\le \frac{B\max_j w_j}{sW}\frac{e^{-1}}{I_b}
\le \frac{B\max_j w_j}{sW}e^{1/3}.
\]

The implementation computes the final max-weight bound for every supplied
weight vector. Across the nonnegative unit simplex its worst case is

\[
K(z)\le 0.3489031062715224 < 0.35=\Lambda,
\]

with analytic margin \(0.0010968937284775993\). Using the independently checked
pinned normalizer, the actual unit-weight peak is
\(0.20714220996727628\), which is smaller still. A 10,000-subinterval composite
Simpson calculation, independent of the runtime normalizer, agreed within
\(5.6\times10^{-17}\), against a test tolerance of \(2\times10^{-15}\).

This analytic gate is not the sole protection. Every evaluated candidate also
passes through a pointwise runtime check. Nonfinite or negative rates abort;
any \(K>\Lambda\) aborts; no clipping or saturation is permitted. A dedicated
fixture at the next binary64 value above \(\Lambda\) exits with status 2 and
does not create an estimate or raw output.

## 4. Independent reference and adversarial fixtures

The Python harness contains a scalar implementation of the geometry, compact
bump, physical hazard, domination check, exact free transition, and full path
replay. It does not import or call the compiled implementation. The following
checks passed:

- strict disk-contact interior, exact edge, and exterior;
- transverse minimum-image equivalence across the periodic seam;
- exact compact-bump support edge, positive near-edge value, and zero region;
- all four centre rates and arbitrary admissible simplex weights;
- value immediately below \(\Lambda\) and explicit violation immediately above
  \(\Lambda\);
- full broad-path candidate count, reaction flag, and event-time replay against
  the scalar path, with the stated ULP tolerance for transcendental operations;
- exact O0/O3 fixture bytes and exact O0/O3 broad raw bytes;
- malformed mode, missing/invalid weights, nonfinite/negative values, invalid
  sum, altered \(\Lambda\), nonzero or negative-zero constant field, corrupted
  raw mode/bound/weights, and overwrite attempts all fail closed;
- raw schema, length formula, sentinels, ordered IDs, counters, hashes, plan
  identity, weight bits, and resume-ledger closure.

The scalar replay is independent code, but it is not an independent numerical
solver or a second physical model. Accordingly, the runtime flag
`independent_solver_verified` remains false.

## 5. Executed validation

### Complete test suite

Command, executed from `code/`:

```text
python3 -m py_compile off_lattice_doi_compiled_core_harness.py \
  test_off_lattice_doi_compiled_core.py
python3 -m unittest -v test_off_lattice_doi_compiled_core.py
```

Result: **22 tests passed in 5.825 s**.

### Compiler/static analysis

Apple clang 21.0.0 compiled both O0 and O3 with `-Wall -Wextra -Werror
-pedantic`, no fast-math, no floating-point contraction, and no associative
math rewriting. A separate Clang static-analyzer pass added conversion,
sign-conversion, shadow, implicit-fallthrough, and double-promotion warnings;
it returned zero diagnostics.

### Optimization identity and fail-closed check

- fixture O0/O3 canonical JSON: byte-identical;
- fixture SHA-256:
  `adccb5c693cd455ec6fc43780b2b9aa9e379c047e59af0b47a10b3560de4cc84`;
- bounded broad raw O0/O3: byte-identical, 3,256 bytes;
- bounded broad raw SHA-256:
  `661bf6b9641eb8c67ce0900920aee296025d8904fc1d3813d4a77d68d0f704d7`;
- independent scalar hazard fixture: exact match;
- above-bound fixture: exit status 2;
- statistical estimates released: false;
- all operational claim flags: false.

### Sanitizers

An O1 build with AddressSanitizer and UndefinedBehaviorSanitizer ran the full
fixture command, the explicit domination violation, and a bounded 128-path
broad raw/parse/attestation cycle. Compilation produced no diagnostics, the
run produced no sanitizer diagnostics, the raw file was attested, and all
claim flags remained false.

### Small synthetic timing only

A bounded 5,000-path broad fixture completed in 0.2861 s (approximately 17,477
paths/s on this machine), produced an attested 120,184-byte raw file with
SHA-256
`f264381b0d776312bcf1be97f682c865731dc67fa5a78ed8910704f0735d1c9d`,
and released no statistical estimate. No production-size extrapolation was
performed. The older fixed large-run projection fields were removed from the
harness and are now prohibited by a source-boundary test.

## 6. Source attestations

| File | Lines | SHA-256 |
|---|---:|---|
| `code/off_lattice_doi_compiled_core.cpp` | 1,338 | `b4c673bafbc4c7f07d0a7520b5a7c9dad64b9e8123573f17da8c076ffa494938` |
| `code/off_lattice_doi_compiled_core_harness.py` | 1,314 | `e47edaba9f1fac602358cda6788e37d7896903f61f690e56f86f9d7c8ebff431` |
| `code/test_off_lattice_doi_compiled_core.py` | 697 | `c1a917d905c7ce16d407bb763dbb781dec81693f540345ba8d1fc8965dd06ae0` |

## 7. Remaining production blockers

The method-only hazard substrate passes this round, but scientific production
must remain on HOLD until all of the following are closed:

1. Freeze the scientific physical inputs and estimand in a separate reviewed
   protocol. The weights exercised here are explicitly synthetic fixtures.
2. Add a genuinely independent solver or independently derived numerical
   implementation for pre-release cross-validation; the present Python replay
   is an independent code path, not an independent physical solver.
3. Replace the in-memory raw parser/finalizer with a streaming, bounded-memory
   auditor before any large run.
4. Add an interprocess lock or a single-writer job manager around ledger
   updates; the current atomic replacement is crash-safe but does not make
   concurrent writers safe.
5. Bind the exact executable digest, compiler/runtime provenance, frozen method
   manifest, and raw-schema parser digest into the production plan and ledger.
6. Perform a storage-capacity, interruption/restart, corruption-injection, and
   recovery drill on the actual execution platform.
7. Pre-register an independent validation pool and the release rule without
   reusing exploratory output. No values are set in this method-only round.
8. Only after the above gates pass may a scientific ensemble be authorized;
   only a complete independently audited ensemble may support multimodality or
   PRR-level claims.

Until then, the correct overall status is:

> **Method implementation PASS; scientific production HOLD; journal claim
> HOLD.**
