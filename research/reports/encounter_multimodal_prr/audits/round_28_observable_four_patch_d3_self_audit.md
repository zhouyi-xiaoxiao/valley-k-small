# Round 28: physical-d=3 relative-shape four-slab self-audit

Date: 2026-07-13  
Assessment: **PASS for the narrowly scoped, result-informed exact-kernel
confirmation of relative-prominence-qualified maxima in the B=0
budget-normalized free-exposure shape; this is not event-mass observability,
and publication/project release remains HOLD.**

Final unresolved issue counts: **P0 = 0, P1 = 0, P2 = 0.**

## 1. Audited claim and evidence boundary

The audited question is whether one fixed four-slab design on
`R longitudinal x T_W^2 transverse`, with the true three-dimensional spherical
contact set, has five alternating stationary points and therefore three
relative-prominence-qualified maxima in the B=0 budget-normalized
free-exposure shape. No absolute event-mass observability claim is made.

The calculation is explicitly result-informed. Geometry, approximate cusp,
and the existence of passing inward steps were known from scratch exploration
before the protocol and manifest were frozen. The only positive claim flag is
`observable_d3_free_exposure_confirmation_passed=true`.

The following flags remain false and were checked exactly in both the manifest
and result:

- `preregistered_discovery`;
- `continuum_verified` (no interval certificate);
- `finite_B_Doi_verified`;
- `independent_PDE_solver_verified`; and
- `project_gate_passed`.

The direct spherical calculation is an independent integral representation of
the same truncated free kernel. It is not an independent PDE solver.

## 2. Model-contract correction before final freeze

The first protocol wording could be read as applying the half-width `0.004`
compact bump only to the longitudinal initial coordinates while starting the
two transverse relative coordinates as point masses. This conflicted with the
physical-d=2 baseline, scratch implementation, and the smooth initial-law
assumption used by the weighted-space theorem.

Before the final execution, the protocol and producer were corrected to state
and enforce the intended law: midpoint, longitudinal relative coordinate, and
both transverse relative coordinates are independently averaged against the
same normalized compact bump around starts `(0.14, -0.35, 0, 0)`. A focused
test now distinguishes this law from transverse point masses. The earlier
output with SHA
`027cb049de85f1d4113817b8b726ef822708e150b9f2a2fcb474e0f5331707d2`
is recorded in the manifest as pre-final and is not part of the frozen final
evidence.

After that correction, Ruff formatting was applied and the files were
refrozen before execution. The intermediate output with SHA
`522c6eaf6b36529a5c9331b3688c10c85540825c75f649bf5c6980a4855eaeda`
is likewise recorded as pre-final and excluded. This resolved the only P1
(model-contract ambiguity) and P2 (format freeze) findings before finalization.

## 3. Final frozen provenance

The manifest predates the final result (`21:13:03+0100` versus
`21:15:18+0100`). Recomputed SHA-256 values are:

| artifact | SHA-256 |
| --- | --- |
| manifest | `a11e1c4a7842ae69efc76e21a4b6587981d612a457070d601e7001810f16b8cb` |
| final result | `125234df2817287c30699d80e30af0e711c036193f0a64a404c8f3e98f98f984` |
| producer | `f8fde83ecdf435acf28a32fb0dec6a22f216bf9f5a817d954f165e62811bf885` |
| focused test | `bcb0b4264d0d89f140017004b083cb16ad7bf8f8ac7a8ab7b59f48ff9cef3a56` |
| protocol | `280a99653077e7d3ab4f7106d9f078a3588cd7f2ff3ae154f550d99dc47851f9` |
| frozen physical-d=2 base dependency | `a553092f3d8bbf50fdf0124a3ea36ba32947c3b339cfcc0265a1cd7f6bc2d4da` |

The manifest hashes, result provenance hashes, and independently recomputed
file hashes agree for the producer, test, protocol, and base dependency. A
second complete formal execution produced the identical result SHA
`125234df...f98f984`.

## 4. Cusp and unfolding checks

The primary calculation gives:

- cusp time: `12.80973996048009`;
- cusp weights:
  `(0.28, 0.18220392800878843, 0.20766998907313670,
  0.33012608291807490)`;
- maximum scaled residual through order three: `2.86743e-12` against the
  `1e-8` ceiling;
- scaled fourth derivative: `-39.87226393940038` against the absolute floor
  `0.5`;
- dimensionless unfolding SVD ratio: `0.24029975690147132` against the `0.10`
  floor; and
- unfolding rank: two, with the frozen signed inward-normal checks passing.

All cusp weights are strictly positive and the fixed first weight remains
`0.28`.

## 5. Frozen inward-step scan and stationary structure

All 19 frozen steps `0.02, 0.03, ..., 0.20` were evaluated on the frozen
`0.002` time grid. Eleven steps, `0.10` through `0.20`, independently
recompute as eligible. Reapplying the four-level lexicographic selection rule
to the saved candidate rows selects `s=0.10`, exactly as the producer reports.

Selected weights are

`(0.28, 0.2113497668133628, 0.11201163825953668,
0.3966385949271005)`.

The five roots are:

| time | topology | density | scaled curvature |
| ---: | --- | ---: | ---: |
| `3.0747145946679315` | maximum | `0.09741380388755955` | `-8.108066821040596` |
| `5.501277641837092` | minimum | `0.048322447291742315` | `11.590147840343956` |
| `8.267049036576434` | maximum | `0.06281803472778126` | `-5.428196839553885` |
| `12.809739960480089` | minimum | `0.052159361005507096` | `4.313958679891428` |
| `21.464180167449786` | maximum | `0.061741658505870545` | `-2.184800342097896` |

The minimum-to-maximum peak ratio is `0.6338081056472881`. The two
valley-to-smaller-neighbour ratios are `0.7692448116396059` and
`0.8448001279484201`, both below the frozen `0.85` ceiling. The worst margin
is positive but modest (`0.005199872051579901`); this is a real robustness
caveat, not a failed gate. All scaled root residuals are below `1e-9`, all
scaled curvatures exceed `1e-4` in magnitude, endpoint derivative signs are
correct, and no above-floor zero plateau remains.

An independent JSON-only recomputation reproduced every candidate gate, every
eligibility value, and the selected row without calling the producer's gate or
selection functions.

## 6. Numerical convergence and independent representation

Fine-minus-primary absolute differences are:

| quantity | observed | frozen ceiling |
| --- | ---: | ---: |
| cusp time | `1.28040e-11` | `2e-8` |
| cusp weight max norm | `1.49880e-14` | `2e-8` |
| scaled fourth derivative | `4.04718e-10` | `2e-5` |
| maximum selected-root time | `6.18172e-13` | `2e-6` |

For the independent representation, the production calculation uses the
Fourier--Bessel transverse-disk integral. The reference directly integrates
the pointwise product of one OU kernel and two periodic heat kernels in
spherical coordinates with 36 radial, 40 polar, and 256 azimuthal nodes. It
does not read the Bessel disk tensor; this is enforced by source inspection
and by a test that poisons that tensor with `NaN` while the direct integral
remains finite.

At times `1, 5, 13, 25`, the maximum relative difference is
`1.0843920736943767e-14`, below the frozen `5e-11` ceiling. Recomputing each
relative difference directly from the saved values reproduces the reported
maximum.

## 7. Executed QA

- focused pytest: `9 passed`;
- Ruff lint: pass;
- Ruff format check: `2 files already formatted`;
- manifest hash validation: pass;
- all saved floating-point values finite: pass;
- all 18 final result gates true: pass; and
- two complete final executions byte-identical: pass.

## 8. Remaining release blockers (not defects in this scoped result)

This result does not supply an interval certificate, an explicit positive-
`B` persistence radius, killed-Doi event mass, bounded-domain convergence, or
an independent PDE solver. It confirms one fixed physical-d=3 four-slab
geometry and does not establish a global phase map or arbitrary-geometry
claim. These limitations keep the project/publication release gate on HOLD
even though the scoped free-exposure confirmation passes.
