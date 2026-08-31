# Isambard-AI v3 Slurm/QoS revision r3

Live pre-submission checks reported these effective limits:

```text
MaxArraySize = 1001
workq_qos MaxJobsPU = 256
workq_qos MaxSubmitPU = 512
expanded live jobs before cancelling v2 gating = 15
cancelled v2 gating jobs = 10
remaining live baseline = 5
```

The r2 six-array plan is retained as historical evidence but is superseded by
this r3 bundled plan.  The automatic production stage is one Slurm array with
local task IDs `0-479` and throttle `%240`.  Each GH200 allocation runs exactly
twelve manifest cells in sequence:

```text
cell_id = local_task_id + 480 * bundle_index
bundle_index = 0,1,...,11
```

The 480 allocations therefore cover global cell IDs `0-5759` exactly once.
Each allocation produces twelve independent atomic JSON/NPZ pairs below the
shared `production-${RUN_TOKEN}` result root.  Failure of any cell makes that
allocation fail, and the `afterok` production reducer cannot start.

The complete r3 chain expands to `1 + 8 + 1 + 480 + 1 = 491` jobs.  Adding the
remaining non-v2 live baseline of 5 gives a conservative submitted-job upper
bound of 496, leaving 16 below `MaxSubmitPU=512`.  At most 240 production GPU
allocations run concurrently, leaving headroom below `MaxJobsPU=256`.

The production reducer validates 5,760 cell artifacts against exactly 480
successful Slurm allocations.  Every allocation must map to the twelve cells
`task_id + 480*k`, and its receipt row must be `COMPLETED` with exit code
`0:0`.  The conditional 160k tail manifest remains frozen and is not submitted
by the automatic chain.
