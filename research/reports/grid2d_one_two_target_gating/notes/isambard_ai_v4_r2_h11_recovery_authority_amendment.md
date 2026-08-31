# v4-r2 H11 recovery-authority amendment

H11 is an append-only successor to immutable H10 SHA-256 `d4affecd4816e7f432f1c1799392e358c4585b880ae21665c9b9908c374a5fcf`. H7 through H10 are byte-for-byte frozen.

H11 separates the four fields observable while a task is running (`JobIDRaw`, canonical `JobID`, array parent, and array task) from the three fields available only after terminal accounting (`State`, `ExitCode`, and `ElapsedRaw`). Admission joins the runtime identity to the exact five-field live `sacct` row; a runtime receipt never claims terminal knowledge.

Every submission first freezes exact science and wrapper bytes, then writes an O_EXCL authority-false intent. All dispatch attempts use `sbatch --hold --comment=H11:<intent_sha256>`. Recovery discovers every logical parent with exact `squeue` comment matching, fails closed on duplicate parents, parses exact `scontrol` fields, verifies the requested dependency, and writes one immutable submission receipt before release. Release has its own durable intent and exact pre/post readback. A completed submission receipt is replayed, never regenerated from a later scheduler state.

Each task executes from its own `$SLURM_TMPDIR` snapshot. Output staging is a complete, fsynced, content-bound transaction published before any run-root promotion. Staged files are mode `0400`, link count one, and never hardlinked to targets. Promotion uses an independent temporary inode and a no-overwrite hardlink commit; recovery handles crashes before dispatch, after scheduler acceptance, before release, after release, during promotion, and after transaction commit.

Live accounting persists exact argv, raw stdout, raw stdout SHA-256, canonical rows, and H11/H10/H9/H8/H7 anchors. Production requires exactly 480 rows with canonical `JobID=<parent>_<task>`, unique decimal `JobIDRaw`, and task set `0..479`.

`status=H11_RECOVERY_AUTHORITY_CANDIDATE_NO_SUBMISSION`

`authorizes_execution=false`

`authorizes_scientific_release=false`
