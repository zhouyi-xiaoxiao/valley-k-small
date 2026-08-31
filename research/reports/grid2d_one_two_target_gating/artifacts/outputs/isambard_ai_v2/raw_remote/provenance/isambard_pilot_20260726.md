# Isambard execution ledger — 2026-07-26

## Accounts and live campaign boundary

- Isambard 3 CPU account/project: `ae23069.b35cz` / `brics.b35cz`
- Isambard-AI GPU account/project: `ae23069.b5dj` / `brics.b5dj`
- Isambard 3 staging root: `/lfs1i3/home/b35cz/ae23069.b35cz/valley-gating`
- Isambard-AI staging root: `~/valley-gating`

The 12-hour Clifton SSH certificate controls new logins only.  The official
login policy uses this as a security boundary so that interactive access must
be re-authenticated rather than kept alive indefinitely.  SLURM owns an
accepted batch job, so logout or certificate expiry does not stop it; long
computations belong in batch jobs rather than persistent login-node sessions.

At the live 2026-07-26 check, `sshare` reported account cap
`cpu=8,640,000` TRES minutes.  With 144 cores per Grace node, this is exactly
1,000 node-hour equivalents.  `RawUsage=409,176` CPU-seconds corresponds to
about `0.7893` node-hour equivalents, leaving about `999.21` under this CPU cap
at that instant.  This is a live account reading and will change with later
jobs.  Isambard-AI `brics.b5dj` is a separate GPU allocation/capacity pool.

The Bristol mail titled **“Isambard-AI: 25,000 node hours available before 31
July”**, received from Sanne Terry on 2026-07-24, was read through Microsoft
Graph in full.  It asks users to submit large Isambard-AI jobs directly before
31 July because July utilisation is low.  A helpdesk ticket is offered only
for technical support, and the linked request form is only for additional
NHR.  The message therefore does not define a special QoS, reservation, or
pre-approval route for this campaign.  The live `Priority` wait below is a
scheduler queue state, not evidence of missing allocation or permission.

## Job ledger

### Completed on Isambard 3

| Job | Purpose | State | Elapsed |
|---|---|---|---:|
| `5553781` | v1 small validation | `COMPLETED 0:0` | 5 s |
| `5553782` | v1 60-cell pilot | `COMPLETED 0:0` | 8 s |
| `5553785` | v1 precision scan, 2M walkers/cell | `COMPLETED 0:0` | 10 m 30 s |
| `5553790` | fixed-mean v2 validation, 100 cells | `COMPLETED 0:0` | 7 s |
| `5553791` | fixed-mean v2, 1,000 steps, 800 cells | `COMPLETED 0:0` | 1 m 51 s |
| `5553792` | fixed-mean v2, 2,500 steps, 800 cells | `COMPLETED 0:0` | 4 m 36 s |
| `5553793` | fixed-mean v2, 5,000 steps, 800 cells | `COMPLETED 0:0` | 9 m 12 s |
| `5553794` | fixed-mean v2, 10,000 steps, 800 cells | `COMPLETED 0:0` | 17 m 35 s |

The formal v2 jobs allocated one 144-core Grace node and used 120 workers.  All
result JSONs parse and pass the mass, fixed-mean-field, and paired-outcome
invariants.

### Isambard-AI GH200

| Job | Purpose | State |
|---|---|---|
| `5780228` | interactive hardware/CUDA smoke | `COMPLETED 0:0` |
| `5780232` | v1 interactive scientific validation | `COMPLETED 0:0` |
| `5780425` | fixed-mean v2 interactive validation | `COMPLETED 0:0` |
| `5780428_[0]` | regular fixed-mean v2 check | `PENDING (Priority)` at last live check |
| `5780429_[0-31%4]` | dependent fixed-mean v2 main array | `PENDING (Dependency)` at last live check |

`5780228` identified an NVIDIA GH200 with 120 GB HBM, PyTorch `2.8.0+cu129`,
CUDA `12.9`, and compute capability `9.0`.  The fixed-mean interactive result
`5780425` passed mass and paired-outcome checks using the frozen field pack.
After the interactive check completed in about 25 seconds, pending regular
check `5780428_0` was safely reduced from an eight-minute to a two-minute
time limit to improve backfill eligibility.  Its workload, source, field pack,
and main-array dependency were not changed.

A live scheduler diagnosis at 2026-07-26 07:45 CST confirmed that this is a
real queue wait rather than a malformed request.  The `ae23069.b5dj` user has
an active `brics.b5dj` association with `normal` QOS, raw share 1 and reported
FairShare about `0.468`.  Job `5780428` requests one node, one GPU, eight CPUs
and 32 GiB, is eligible, has no dependency, and remains at scheduler priority
1 with no predicted start time.  Although `sinfo` displayed three nominally
idle GH200 nodes, all three were `IDLE+PLANNED`; the visible workq snapshot had
1,034 allocated nodes, 190 mixed nodes, and no unplanned idle node.  Therefore
the short check is correctly waiting behind other planned work.  Resubmission
or a different resource shape would discard queue age without fixing the
underlying priority and is not justified.

The earlier jobs `5779939`, `5780005`, `5780006`, and `5780186` were cancelled
at elapsed time zero once the v1 causal confound and redundancy were
identified.  They must not be described as waiting or failed science runs.

## v1 numerical result and causal limitation

The v1 pilot has four amplitudes, five target-2 vertical positions, and three
independent seeds (60 cells).  Cells within a seed share fields/random streams
and are not 60 independent observations.  The precision job used 2,000,000
walkers per cell and 5,000 steps; its artifact hash is:

`1d0decd1a11a226dcb84e7a27e16f37dc7d63c79dad9e1033f195f79860a4bf7`

For the homogeneous vertically aligned cell, the three-seed mean target-1
probability changed from `0.37922367` to `0.13717467`, an absolute gating drop
of `0.24204900`; target 2 absorbed `0.64024500` within the horizon.  These are
valid descriptive Monte Carlo results.

They are not evidence that heterogeneity causes the trend.  The v1 rule

`hold = 0.08 + amplitude * sigmoid(field)`

increases both the mean hold and heterogeneity as amplitude rises.  Any v1
amplitude trend is therefore confounded.  In v2, the mean hold is fixed at
`0.30`; `target2_first_probability` is used instead of the stronger and
potentially misleading phrase “redirected mass”.

## Fixed-mean v2 design

- heterogeneity amplitudes: `0.00, 0.05, 0.10, 0.15, 0.20`
- target-2 vertical fractions: `0.20, 0.35, 0.50, 0.65, 0.80`
- 16 disorder replicates x two walk replicates
- common random numbers for one-target/two-target paired outcomes
- cumulative counts at 10%, 25%, 50%, 75%, and 100% of each horizon
- enforced identities: total mass equals one; target-1 hits in the two-target
  condition are a subset of one-target target-1 hits; paired categories exhaust
  all walkers

Canonical fixed-mean result hashes:

| Job | SHA-256 |
|---|---|
| `5553790` | `c0bf5c6dd7793074d7407e56c11fd947d2624540b765d9b2c1e2d5e544ba78ee` |
| `5553791` | `f0b649a81b67e3c45ead5c03e1c0447c2b336d81fd887c5faa9deaad989532ff` |
| `5553792` | `2594cad863a2fe43349e5dd671218c38a7ead973928fd6b59e49f84d183f6882` |
| `5553793` | `8ccf746d9961b40e20dbd386c2e25ea02c5a5549e0da698a5ff69ed50e385745` |
| `5553794` | `17b7af4875068615530566397187b2f440e27da5da3b2ae47bf4ccd51d589d54` |

## Independent homogeneous oracle

`code/exact_homogeneous_oracle.py` uses a finite Markov chain rather than the
Monte Carlo implementation.  The persisted 10,000-step artifact is
`artifacts/outputs/exact_homogeneous_oracle_basehold030_steps10000.json`,
SHA-256
`8700fe537874ba6da4faf5c15629d3506ffcf6b6dfd1ebb51bfc3478a9f16746`.

For the one-target homogeneous case, exact target-1 probability is
`0.5705167146835269`; the `5553794` Monte Carlo estimate is `0.570598500`
(about `0.47` standard errors away).  For the vertically aligned two-target
case, exact probabilities are target 1 `0.174284260`, target 2 `0.738086337`,
and gating `0.396232454`; the Monte Carlo values are within about one standard
error.

## Frozen field and executed-source hashes

- field pack: `28d8879690a8ca307b5db03823aa39110d9734c2ec5ea68243facda9fe83cc8f`
- field-pack manifest: `5ec581a3f5c526aa2ec33ade7bdf8e0ee7037291831c5b7c631fb18fdc4ea331`
- frozen generator source: `44233c41bee16f9606fafdb2ff22c2261803629172873cd030469f9b151be83b`
- completed CPU v2 source: `32686ef6a2e48b27cf30195b1ca775fffcf281ea17b24bd09e3f2215361050d1`
- queued/executed GPU v2 source: `85e1b293f03669f2d1e533129d407aad34a0205380c0a84de289052d64f3b745`
- `5780425` interactive GPU result: `74410d25f36a5b08ed14f92c5d714540120ccef0d7961f29de006699ed3cb01f`

The field pack was created with the Isambard 3 runtime (Python `3.11.7`,
NumPy `1.24.4`, SciPy `1.10.1`).  It is authoritative and must not be
regenerated in place.  The exact source files used by completed/queued jobs are
the hash-suffixed snapshots under `artifacts/outputs/`; current files in
`code/` contain later input-validation and integer-width hardening.

## Exact submit boundary

For a fresh Isambard 3 staging directory:

```bash
cd /lfs1i3/home/b35cz/ae23069.b35cz/valley-gating
mkdir -p logs results
```

The v2 validation was submitted as job `5553790`.  Jobs `5553791` through
`5553794` used `--dependency=afterok:5553790`, `WALKERS=250000`,
`DISORDER_REPLICATES=16`, `WALK_REPLICATES=2`, and horizons/timelimits of
`1000/20`, `2500/30`, `5000/45`, and `10000/60` minutes respectively.

Always submit from the staging root.  Slurm opens `logs/...` before the script
body runs, so the directories must exist before `sbatch`.

## Block-paired horizon summary

`code/summarize_fixed_mean_v2.py` audits all 3,200 cells and writes:

- `artifacts/outputs/gating_fixed_mean_v2_horizon_summary.json`, SHA-256
  `a49c4db40a5697eab9df6620d55fb8e0c3b3828b6790f3c776b5eb90a813c724`;
- `artifacts/outputs/gating_fixed_mean_v2_horizon_summary.csv`, SHA-256
  `e9de8bd46a5000bfe10943c1d4922d9d5de7917a7c1df76f28861627cf94440b`;
- summary source SHA-256
  `7afe235252439b718ab6b523b7ebc87575492aac017a3226af9e693ce9362d6e`.

The audit found zero mass/subset/field-mean failures, zero field/seed
mismatches, and zero prefix-count mismatches.  The 1,000-, 2,500-, and
5,000-step results are exact checkpoints of the same trajectories represented
by the 10,000-step run; they are not independent repetitions.

The independent interval unit is one disorder-seed block (`n=16`), after
averaging two walk replicates inside the block.  At 10,000 steps, the
geometry-averaged gating drop is `0.3580734` for amplitude zero and `0.3514482`
for amplitude `0.20`.  Their paired difference is `-0.0066253`, with 95%
Student-t interval `[-0.0101198, -0.0031307]`.  At 1,000 steps the corresponding
contrast includes zero; the negative contrast emerges with horizon.

Geometry is the stronger effect: the vertically aligned target-2 position is
the maximum-gating geometry in every one of 320 horizon/amplitude/block checks.
At 10,000 steps the complete nearest-to-farthest ordering also holds in all 80
amplitude/block checks.  The aligned-minus-mean-extremes contrast is about
`0.07383` at amplitude zero and `0.07303` at amplitude `0.20`.

This remains a finite-horizon result.  The largest mean two-target unresolved
probability at 10,000 steps is about `0.133`, and the homogeneous one-target
unresolved probability is about `0.429`.  The safe claim is that fixed-mean
heterogeneity modestly lowers observed interception mass at long tested
horizons while leaving the geometry ordering intact; it is not yet an
asymptotic splitting-probability claim.

## Continuation

Run `bash code/isambard_continue.sh status` no more often than once per minute.
When `5780428` completes successfully, `5780429` can enter the regular GPU
queue automatically.  Fetch by verified SHA-256, aggregate uncertainty across
the two replicate levels, and retain the frozen source/field hashes in every
figure or manuscript provenance block.
