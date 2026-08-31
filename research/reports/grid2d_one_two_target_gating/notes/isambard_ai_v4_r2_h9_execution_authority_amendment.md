# v4-r2 H9 execution-authority amendment

H9 is an append-only successor to H8. It fixes H8 SHA-256 `bb815db83632e67bf5b6c2d6f527bed2b3f9eaae4e1ac5c668a761b38065297a` and H7 SHA-256 `7cb7c5d0d6e34e9133ce74d81da69c4814ebd9db5af30081ae1a426abefcceee`; no H8 or H7 byte is changed.

The audited H9 manifest digest is pinned in a controller outside the closed-world execution payload. The controller verifies the entire package, captures and directly hashes the manifest-bound science sbatch bytes, derives one submission byte string, and supplies exactly that string to `sbatch` on standard input. Runtime never executes from the queued shared package. Each job, including every array task, creates a fresh closed-world source snapshot below `$SLURM_TMPDIR`, imports only explicitly content-bound upstream artifact inputs, executes the captured science bytes with the frozen root redirected to that snapshot, proves all source and imported inputs unchanged, then atomically exports only new regular output files to the writable run root.

Runtime receipts bind H9/H8/H7, job and array identities, task index, submitted-script digest, captured and derived science digests, exact phase arguments, inputs, outputs, and terminal accounting identity. Reducer admission requires exactly task indices 0 through 479 with no duplicate. Finalization replays receipts and terminal `sacct` evidence and emits an H9-rooted candidate with no scientific authority.

`status=H9_EXECUTION_AUTHORITY_CANDIDATE_NO_SUBMISSION`

`authorizes_execution=false`

`authorizes_scientific_release=false`
