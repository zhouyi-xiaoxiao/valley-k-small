# Isambard-AI v3 preregistered long-horizon protocol

Protocol ID: `grid2d_gating_long_horizon_v3_20260726`

Status at creation: `PREREGISTERED_NOT_YET_ACCEPTED`

## Primary question

At fixed spatial mean holding probability, does quenched heterogeneity change
the eventual target-splitting probability, or does it only delay absorption at
the finite horizons used by the v2 pilot?

The old v1 campaign is excluded from causal heterogeneity claims because its
holding rule changed the spatial mean and the heterogeneity amplitude at the
same time. The v2 CPU and GH200 results remain immutable validation evidence.
No v3 result may overwrite or reinterpret them.

## Model boundary

- Rectangular nearest-neighbour lattice with attempted-outside-stays
  reflecting boundaries.
- One-target reference and two-target intervention are coupled with common
  random numbers.
- Absorption takes precedence over further motion.
- Base holding probability: `0.30`.
- Quenched field: exactly zero spatial mean and maximum absolute contrast one.
- Holding law: `q(x)=0.30 + amplitude * contrast(x)`.
- Primary amplitudes: `0.00, 0.05, 0.10, 0.15, 0.20, 0.25`.
- Start and target-1 coordinates: `(7,24)` and `(54,24)` on the `64 x 48`
  production grid; target radius 3 lattice sites.
- Target-2 coordinates: Cartesian product
  `x in {24,32,40}` and `y in {9,16,24,31,38}`.

All coordinates, horizons, amplitudes, random-stream indices, and numerical
settings are resolved from a content-frozen manifest. The batch command may
select a manifest and a cell ID but may not override a scientific parameter.

## Primary production design

- 32 independent quenched-disorder blocks.
- Two independent walk streams per disorder block.
- 15 target-2 geometries.
- Six amplitudes.
- 1,000,000 walkers per logical cell.
- Maximum horizon 80,000 steps.
- Frozen checkpoints at 5,000, 10,000, 20,000, 40,000, and 80,000 steps.
- Total logical cells: `32 * 2 * 15 * 6 = 5,760`.

The independent inferential unit is a disorder block. Walk streams are first
averaged within a block; they are never counted as independent disorder
replicates. Common random numbers are preserved across amplitude, geometry,
and the one-target/two-target pair by excluding those factors from the walk
seed.

## Estimands

At horizon `T`:

- `diversion_T = P(one=T1 and two=T2 by T)`;
- `acceleration_T = P(one=unresolved and two=T2 by T)`;
- `target2_hit_T = diversion_T + acceleration_T`;
- `finite_gating_T = P(T1 in one-target by T) - P(T1 in two-target by T)`.

The primary cell is target 2 at `(32,24)` and the paired contrast is amplitude
`0.20 - 0.00`. The practical-equivalence region is absolute probability
`[-0.002,+0.002]`.

For the primary paired contrast, use a two-sided 95% Student-t interval over
disorder blocks after averaging walk streams. Classify only as:

- negative change if the upper endpoint is below `-0.002`;
- positive change if the lower endpoint is above `+0.002`;
- practical equivalence if the entire interval is inside the equivalence
  region;
- otherwise inconclusive.

The secondary geometry-amplitude surface uses a field-block max-t bootstrap
with 10,000 resamples and frozen seed `20260726`. There is no sign-based early
stopping.

## Tail gate and conditional extension

Evaluate the tail gate on the primary amplitudes `0.00` and `0.20` and three
anchor geometries `(24,24)`, `(32,24)`, and `(40,24)`.

Pass only if all anchor cells satisfy:

1. the 95% upper confidence bound for one-target unresolved mass is at most
   `0.005`;
2. the 95% upper confidence bound for two-target unresolved mass is at most
   `0.005`;
3. `abs(mean(G_T-G_T/2)) + tcrit * SE <= 0.002`.

If the 80,000-step tail gate fails, run the same anchor cells to 160,000 steps
and require their 80,000-step integer checkpoints to match the first run. If
the 160,000-step gate also fails, stop horizon escalation and restrict the
paper to finite-horizon effects plus explicit tail bounds. An asymptotic
splitting claim remains forbidden.

## Integrity gates

Every cell fails closed on any of:

- missing, duplicate, or unexpected cell identity;
- source, field-pack, manifest, or container provenance mismatch;
- non-finite scalar or count outside its admissible range;
- holding probability outside `[0,1)` or fixed-mean error above `1e-12`;
- mass-balance error above `1e-12`;
- paired target-1 subset violation;
- non-monotone checkpoint counts;
- task-index/parameter mismatch;
- output overwrite attempt.

Retries must preserve the exact cell specification and seed, keep failed
attempts, and add a new attempt rather than replacing a file. A reducer accepts
only one fully verified success for a cell and fails on conflicting verified
successes.

## Slurm gates

1. Full-size GH200 canary array.
2. Independent canary inventory audit.
3. Production array, released only by successful canary audit.
4. Strict production reducer and statistical summary.
5. Independent replay/audit before any manuscript claim is promoted.

The labels `A`, `B1`, `B2`, and `B3` are analysis and budget strata inside
the one 80,000-step production campaign.  After G0 passes they may be
submitted concurrently; they are not sequential release gates.  The full
reducer evaluates their joint integrity before inference.  Only `A2` remains
conditional: it is released solely if the verified 80,000-step tail gate
fails.

The normal Isambard-AI queue accounts one requested GPU as one quarter of a
node. Job walltimes are set close to measured runtime because Slurm reserves
credits from requested resources and walltime. Large production arrays use a
concurrency cap so that they exploit the July capacity without requesting 256
or more whole nodes at once.

## Expansion beyond the first 5,760 cells

The 32-block campaign is the first publication gate, not the total compute
ceiling. After its reducer:

1. expand to 64 or 128 disorder blocks if the primary interval or surface
   uncertainty is field-limited;
2. run the conditional 160,000-step anchor campaign if the tail gate fails;
3. add correlation-length and anisotropy packs at frozen matched amplitudes;
4. add selected finite-size runs with horizons scaled by squared linear size;
5. preserve budget for an independent backend and reviewer-requested checks.

The expansion is selected by preregistered uncertainty and tail diagnostics,
not by whether an effect has a desired sign.

## Publication gate

The work can advance from computation to manuscript claims only after:

- exact homogeneous oracles for all 15 geometries;
- frozen CPU/GPU anchor comparisons within a declared joint-error tolerance;
- the 80,000/160,000-step tail decision or explicit finite-horizon boundary;
- exact result inventory, Slurm accounting receipt, and content hashes;
- block-level statistical tables and reproducible figures;
- an external novelty/literature audit.
