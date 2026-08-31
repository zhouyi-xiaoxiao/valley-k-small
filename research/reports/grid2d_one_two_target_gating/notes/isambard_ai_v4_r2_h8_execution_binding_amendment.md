# v4-r2 H8 execution-binding amendment

H8 is an append-only execution overlay over fixed H7 SHA-256 `7cb7c5d0d6e34e9133ce74d81da69c4814ebd9db5af30081ae1a426abefcceee`. It changes no H7 member.

Execution uses distinct immutable `PACKAGE_ROOT` and writable `RUN_ROOT`. Before any import or submission, H8 verifies the externally anchored closed-world manifest. Every phase gets a private read-only snapshot, embeds H8/H7/package/run/snapshot anchors in argv and environment, verifies pre-run and post-run bytes, and emits a required exact runtime receipt. Downstream submission rejects a missing or forged prior receipt. The verified generated sbatch byte string is passed to `sbatch` on stdin, eliminating path re-open between verification and submission. All eight phases are dependency chained and fail closed.

`status=H8_EXECUTION_BINDING_CANDIDATE_NO_SUBMISSION`

No remote sync or Slurm submission is authorized until independent review.
