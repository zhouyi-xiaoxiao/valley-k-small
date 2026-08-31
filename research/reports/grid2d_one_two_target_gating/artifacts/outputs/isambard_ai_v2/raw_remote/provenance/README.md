# Grid2D One vs Two Target — Gating

**Status (2026-07-26): fixed-mean CPU v2 complete and verified on Isambard 3; GH200 v2 interactive validation complete; regular Isambard-AI v2 jobs queued.** Tracking: [#8](https://github.com/zhouyi-xiaoxiao/valley-k-small/issues/8).

## Scientific scope

This report compares one-target and two-target first-passage outcomes on a
reflecting 2D grid.  The primary paired statistic is

`P(target 1 first | one target) - P(target 1 first | two targets)`.

The fixed-mean v2 design changes the amplitude of quenched spatial
heterogeneity while holding the mean site holding probability at `0.30`.
Target-2 vertical fractions are `0.20, 0.35, 0.50, 0.65, 0.80`; the formal CPU
scan uses 16 disorder replicates and two walk replicates per cell with common
random numbers.

The original v1 scan remains useful as migration and numerical evidence, but
not as a causal disorder experiment: its formula
`hold = 0.08 + amplitude * sigmoid(field)` changes the mean hold and the spatial
heterogeneity simultaneously.

## Layout

- `code/cpu_gating_phase_scan.py` — original v1 multiprocess NumPy scan
- `code/cpu_gating_phase_scan_v2.py` — hardened fixed-mean CPU implementation
- `code/gpu_gating_mc.py` — original v1 batched PyTorch implementation
- `code/gpu_gating_mc_v2.py` — hardened fixed-mean GPU implementation
- `code/generate_disorder_field_pack_v2.py` — generator for future field packs
- `code/exact_homogeneous_oracle.py` — independent finite Markov-chain oracle
- `code/summarize_fixed_mean_v2.py` — cross-horizon integrity audit and block-paired statistical summary
- `code/isambard3_gating_scan{,_v2}.sbatch` — Grace CPU launchers
- `code/isambard_ai_gating{,_v2}.sbatch` — GH200 launchers
- `code/isambard_continue.sh` — status and checksum-verified fetch helper
- `notes/isambard_pilot_20260726.md` — execution ledger, hashes, and caveats
- `artifacts/outputs/` — fetched results, logs, frozen field pack, and executed-source snapshots

## Verified execution handles

### Isambard 3 CPU

- v1: `5553781`, `5553782`, `5553785` — `COMPLETED`, exit `0:0`
- fixed-mean v2: `5553790` through `5553794` — `COMPLETED`, exit `0:0`
- v2 horizons: 1,000, 2,500, 5,000, and 10,000 steps, with 800 cells per formal horizon

Canonical v2 result hashes are recorded in
`notes/isambard_pilot_20260726.md`.  Every fetched JSON parses, every remote and
local SHA-256 matched, and all mass, fixed-mean, and paired-outcome invariants
passed.

The persisted horizon summary is
`artifacts/outputs/gating_fixed_mean_v2_horizon_summary.{json,csv}`.  It treats
the 16 disorder seeds as independent blocks, averages the two walk replicates
inside each block, and pairs amplitude contrasts by seed.  The four horizon
files are verified prefixes of the same common-random-number trajectories, not
four independent experiments.

### Isambard-AI GH200

- hardware smoke `5780228` — `COMPLETED`, NVIDIA GH200 120 GB
- v1 scientific interactive validation `5780232` — `COMPLETED`
- fixed-mean v2 interactive validation `5780425` — `COMPLETED`
- regular v2 check `5780428_[0]` — queued at `Priority`
- dependent main array `5780429_[0-31%4]` — queued at `Dependency`

The regular check's request is valid (`1 GPU, 8 CPUs, 32 GiB`, normal QOS,
active `brics.b5dj` association).  A live 2026-07-26 scheduler snapshot showed
the only three nominally idle workq nodes as `IDLE+PLANNED`; priority 1 and an
unknown start time therefore reflect genuine queue ordering, not a bad GPU
shape or failed program.  Do not resubmit merely to change the pending reason.

The earlier v1 jobs `5779939`, `5780005`, `5780006`, and `5780186` were
deliberately cancelled at elapsed time zero after the v1 causal confound was
identified.  They are not pending science results.

## Reproducibility boundary

Executed source snapshots, rather than the subsequently hardened files in
`code/`, are authoritative for completed/queued jobs:

- CPU v2 executed source: `artifacts/outputs/cpu_gating_phase_scan_v2_32686ef6.py`, SHA-256 `32686ef6a2e48b27cf30195b1ca775fffcf281ea17b24bd09e3f2215361050d1`
- GPU v2 queued/executed source: `artifacts/outputs/gpu_gating_mc_v2_85e1b293.py`, SHA-256 `85e1b293f03669f2d1e533129d407aad34a0205380c0a84de289052d64f3b745`
- frozen field generator: `artifacts/outputs/generate_disorder_field_pack_v2_frozen.py`, SHA-256 `44233c41bee16f9606fafdb2ff22c2261803629172873cd030469f9b151be83b`
- authoritative field pack: `artifacts/outputs/disorder_field_pack_v2.npz`, SHA-256 `28d8879690a8ca307b5db03823aa39110d9734c2ec5ea68243facda9fe83cc8f`

Do not regenerate or overwrite the authoritative field pack: tiny SciPy-version
differences change its bytes and hash.  The current local CPU, GPU, and
generator sources contain later validation hardening and therefore have
different hashes.

## Continuation

The Isambard 3 staging directory is
`/lfs1i3/home/b35cz/ae23069.b35cz/valley-gating`.  Submit only from that
directory.  A fresh staging directory must contain `logs/` and `results/`
before `sbatch`; Slurm opens `#SBATCH --output` before the script body can run
`mkdir`.

Use:

```bash
bash code/isambard_continue.sh status
bash code/isambard_continue.sh fetch
```

Next scientific work is to fetch and audit `5780428/5780429`, make figures
from the verified block-paired summary, extend the horizon before making
asymptotic claims, and only then draft manuscript text.
