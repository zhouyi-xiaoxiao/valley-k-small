# Isambard-AI v3 Slurm array revision r2

Live pre-submission inspection of `scontrol show config` reported
`MaxArraySize = 1001`.  The former production request `0-5759` therefore
cannot be submitted as one Slurm array and is forbidden by this revision.

The frozen r2 production map uses six arrays.  Every array has local task IDs
`0-959`, throttle `%64`, and one of these global cell offsets:

```text
0, 960, 1920, 2880, 3840, 4800
```

Each cell computes `cell_id = offset + SLURM_ARRAY_TASK_ID`.  The six segments
cover global cell IDs `0-5759` exactly once, with no gap or overlap.  All six
depend `afterok` on the canary inventory reducer.  Their combined requested
concurrency is at most `6 * 64 = 384` GPUs.

Every cell in one phase writes below a shared run-token directory.  Revision
r2 uses the environment job ID as the numeric run token.  The production full
reducer depends `afterok` on all six array job IDs, builds one combined `sacct`
receipt, and scans that shared production result directory.

The conditional 160k tail manifest remains frozen and is not submitted by the
automatic chain.
