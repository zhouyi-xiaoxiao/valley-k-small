# v4-r2 H10 live-accounting and transaction amendment

H10 is append-only over H9 SHA-256 `a00f515ab15bd25c2c6a028420ca4339d69ce13d3abf07ce78eff688eb470bfa`. H7, H8, H9, and the externally pinned H9 controller are immutable.

Live Isambard-AI exposes `JobID` and `JobIDRaw`, but not `ArrayJobID` or `ArrayTaskID`, in `sacct --helpformat`. H10 therefore fixes the production accounting query to `JobIDRaw,JobID,State,ExitCode,ElapsedRaw`. Production admission requires exactly 480 canonical rows whose `JobID` values are `<parent>_0` through `<parent>_479`; their allocation-unique decimal `JobIDRaw` values bind the corresponding runtime receipts.

Every accounting decision persists the exact argv, raw stdout, raw stdout SHA-256, canonical parsed rows, and H10/H9/H8/H7 anchors. Non-array runtime job identity, terminal accounting identity, submitted script bytes, phase inputs, and outputs are replayed rather than trusted.

Output export is a recoverable transaction. Immutable staged outputs and an O_EXCL authority-false plan are written before promotion. Promotion is idempotent, a committed marker is O_EXCL, and a missing runtime receipt can be recreated only from the content-bound plan after every target is verified.

Submission creates an O_EXCL authority-false intent and exact script archive before `sbatch --hold --comment=H10:<intent_sha>`. A unique held job is recovered by comment, the submission receipt is durably written before release, and an O_EXCL release receipt records release/readback. The job script verifies its own normalized embedded binding and reports its exact on-node script digest; it does not trust an exported digest.

`status=H10_CANDIDATE_NO_SUBMISSION`

`authorizes_execution=false`

`authorizes_scientific_release=false`
