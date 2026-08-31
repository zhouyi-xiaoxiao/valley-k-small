# Round 101: off-lattice compiled-core validation

Date: 2026-07-14
Verdict: **ACCEPT -- method-only compiled core; HOLD -- state-dependent or scientific run**

## 1. Question and frozen boundary

This round asks whether a compiled, transition-exact off-lattice Doi-thinning
kernel is ready to replace the scalar Python proof of principle at the
*method-validation* layer.  It does not ask whether the independent scientific
Monte Carlo has passed.

The accepted executable surface is deliberately narrow:

- one fixed free process on the unbounded longitudinal quotient and periodic
  transverse relative coordinate;
- exact OU / wrapped-Brownian transitions at homogeneous Poisson candidate
  times;
- a constant, nonnegative hazard dominated by the declared `Lambda`;
- path-keyed Philox4x32-10 streams, raw integer records, deterministic chunks,
  and a sequential resume ledger; and
- synthetic basin cuts and windows used only to test integer closure.

The C++ core contains no broad-four-slab hazard, physical catalyst weights,
contact indicator, scientific Stage-B windows, power calculation, or
production trajectory count.  Every chunk advertises
`METHOD_ONLY_CONSTANT_HAZARD_COMPILED_CORE`, sets all scientific claim flags to
false, and releases no statistical estimate on stdout.  Therefore this round
does **not** set `independent_solver_verified`, `modality_confirmed`, or any
manuscript evidence gate to true.

Reference design inputs were read but not modified:

| artifact | SHA-256 |
|---|---|
| `notes/off_lattice_doi_thinning_design.md` | `349541a954e665d0a68b3989e6f38f5edc725b00f77e4811147c1de262fc7961` |
| `code/off_lattice_doi_thinning_poc.py` | `90466d074d3b6d302143919d4160beb36109e9686312e3a33670321e4f297e9d` |
| `code/test_off_lattice_doi_thinning_poc.py` | `986e839ebaa7f5b56d328826312fcce1f1305a2493108e5da8d7558992cc365d` |

## 2. Repairs made in this round

The interrupted prototype initially compiled, but its validation layer was
not internally consistent.  Five issues were repaired.

1. The C++ command intentionally withheld per-chunk estimates, while four
   tests and the benchmark expected those estimates in the operational JSON.
   They failed with missing `reaction_count`, `basin_counts`, or
   `candidate_count_sum`.  Counts are now derived only by independently parsing
   a completed raw chunk; the operational command remains estimate-free.
2. The explicit method-boundary marker expected by the test was absent.  The
   marker is now emitted by both fixture and chunk commands and checked by the
   harness together with the exact all-false claim-flag map.
3. The raw parser previously accepted some corrupted evidence: a censored
   record could use negative infinity, and a reacted record could contain NaN,
   an out-of-horizon time, no candidate, or a changed trajectory ID.  The
   parser now requires the exact positive-infinity censor sentinel, finite
   reacted times in `(0,T]`, at least one evaluated candidate for reactions,
   exact ordered IDs, valid header rates, and valid cuts/windows.
4. Frozen-plan and final-ledger checks did not fully validate integer domains,
   overflow, nonfinite rates, malformed chunk entries, or unexpected top-level
   ledger fields.  These cases now fail closed before an estimate is released.
5. The independent reference was extended from primitive fixtures to complete
   synthetic trajectories.  It replays compact-bump sampling, Poisson
   increments, three-normal exact transitions, and thinning decisions using a
   separate pure-Python Philox implementation.

No allocation result, allocation audit, manuscript claim surface, Stage-B
artifact, existing POC, package environment, or virtual environment was
changed or executed.

## 3. Methodology and deterministic checks

The build is pinned to `/usr/bin/clang++` with SHA-256
`179301dcb41ea78accc3fa0048a7e6f6710d891945a751a34addd622020c1818`
(`Apple clang 21.0.0`, arm64) and uses C++20, `-Wall -Wextra -Werror
-pedantic`, `-fno-fast-math`, `-ffp-contract=off`, and
`-fno-associative-math`.

The final unit run was

```text
cd code
/usr/bin/python3 -m py_compile \
  off_lattice_doi_compiled_core_harness.py \
  test_off_lattice_doi_compiled_core.py
/usr/bin/python3 -m unittest -v test_off_lattice_doi_compiled_core.py
```

Result: **16/16 PASS in 3.804 s**.  The tests establish:

- the published Philox zero vector and four further counter blocks match an
  independent integer implementation exactly;
- open-uniform, exponential, Box--Muller, compact-bump, SHA-256, and fixed
  exact-transition fixtures match independent references;
- O0 and O3 fixture JSON and synthetic raw trajectories are byte-identical;
- an exact rerun of the same IDs has the same raw bytes and SHA-256;
- whole-range, split-range, reverse-order, and missing-chunk resume executions
  preserve every trajectory;
- changing either master seed or replicate ID changes the path streams;
- 128 complete C++ paths agree with the independent Python replay in candidate
  count and reaction flag exactly, with reacted times within 12 ULP;
- integer event/censor/basin/window closure holds;
- bound violations, ID overflow, NaN inputs, overlapping windows, overwrite
  attempts, incomplete plans, malformed ledgers, corrupt raw fields, and
  unledgered/partial evidence fail closed; and
- a complete frozen plan is required before the harness releases even the
  synthetic integer estimates.

A separate ASan+UBSan build (`-O1 -fsanitize=address,undefined`) passed the
fixture command and a 1,000-trajectory constant-hazard chunk with no sanitizer
diagnostic.  Its fixture bytes had SHA-256
`9e14fcb020164a831ec9223dca525ccb8711350b82813e10e17e8b99db82e273`.

## 4. Statistical sanity checks

For `N=50,000`, `k=0.05`, `Lambda=0.13`, and `T=100`, the empirical survival
at `t=(10,30,100)` was

```text
(0.60502, 0.22416, 0.00634)
```

against the analytic exponential survival

```text
(0.6065306597, 0.2231301601, 0.0067379470).
```

The maximum error on these points was `0.00151066`.  More strongly, the full
finite-horizon Kolmogorov--Smirnov discrepancy over all 49,683 reacted event
times was `0.00321381`, below the predeclared DKW half-width `0.01204519` at
`alpha=1e-6` (26.7% of the bound).

For a zero-hazard candidate process, the test checks both the mean and sample
variance against the Poisson value `Lambda T`.  The 20,000-path timing fixture
at `Lambda=0.13` observed `12.99055` candidates per path against the analytic
value `13`.

These checks validate the constant-hazard thinning skeleton and free-transition
RNG consumption.  They do not validate the absent state-dependent catalyst.

## 5. Small performance baseline

One method-only 20,000-trajectory timing pass produced:

| fixture | candidates/path | trajectories/s | linear 6M engine projection |
|---|---:|---:|---:|
| `k=0.05`, `Lambda=0.13` | `2.5753` | `195,979` | `30.62 s` |
| `k=0`, `Lambda=0.13` | `12.99055` | `176,917` | `33.91 s` |
| `k=0`, `Lambda=0.35` | `34.9863` | `134,613` | `44.57 s` |

The streaming raw-size projection is `144,000,144` bytes for six million
records.  These are single-run feasibility timings, not a performance promise:
the physical hazard lookup is absent, the Python parser is not production
streaming, and no broad or scientific calculation was run.  The benchmark
JSON explicitly keeps `scientific_run_authorized=false`.

## 6. Final artifacts

| artifact | lines | SHA-256 |
|---|---:|---|
| `code/off_lattice_doi_compiled_core.cpp` | 1,075 | `4f6810bf82445f85339cbe87d3e7bbf8e4144bdd1b8ddbe3c68daa273414d895` |
| `code/off_lattice_doi_compiled_core_harness.py` | 1,048 | `4bc1b797ae450a4a46f127120cc7bcad6d579e410aa895e468443f1ba680386b` |
| `code/test_off_lattice_doi_compiled_core.py` | 451 | `66a552f5dd32288eb596b05e23dc62a59e6383d3ccad04b9a8a1ffbc38c9e226` |

The O3 benchmark build reported source SHA-256
`4f6810bf82445f85339cbe87d3e7bbf8e4144bdd1b8ddbe3c68daa273414d895`.
On macOS, the linked executable hash also depends on the output basename through
the ad-hoc code-signing identifier; production reproducibility must therefore
freeze the executable basename as well as compiler, flags, source, and target.
Scientific evidence must continue to be based on attested raw output, not on a
binary hash alone.

## 7. Remaining production blockers

The method-only core is accepted, but production remains on HOLD until all of
the following are completed and frozen before inspecting scientific event
times:

1. implement the continuous broad-four-slab state-dependent hazard, exact
   contact convention, pinned bump normalization, and a pointwise strict
   `K<=Lambda` abort; then independently test the analytic domination margin;
2. freeze Stage-B-derived survival times, valley cuts, contrast windows,
   tolerances, power, seeds, replicate ranges, chunk plan, and the decision rule
   without fitting anything to Monte Carlo output;
3. cross-check the compiled physical hazard and small aggregate ensembles
   against the scalar POC or another independent implementation; the present
   exact path replay covers only the constant-hazard channel;
4. replace the current in-memory Python raw parser/finalizer with a streaming
   production auditor, and provide a single-writer or locked ledger protocol
   for concurrent workers;
5. run two disjoint powered scientific replicate pools, the frozen
   replicate-consistency gate, exact-ID reproducibility, DKW/Clopper--Pearson
   inference, and window-contrast gates exactly once; and
6. perform an independent post-result audit before any manuscript integration.

Until those gates pass, the only justified claim is: **the compiled RNG,
exact-free-transition, constant-hazard thinning, raw-record, and deterministic
resume substrate passed its bounded method validation.**
