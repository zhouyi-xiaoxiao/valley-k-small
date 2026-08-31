# Round 99: independent validation of the allocation-v6 launch-shell erratum

Date: 2026-07-14  
Role: independent operational reviewer; not the Round-98 command author  
Decision: **ACCEPT / GO ONLY UNDER THE EXPLICIT ROUND-98 BASH CONTRACT**  
Open findings: **P0 = 0, P1 = 0, P2 = 0**

## 1. Frozen allocation and scope

I validated but did not edit the final Round-98 allocation:

| role | bytes / SHA-256 |
|---|---|
| Round-98 shell erratum | 6799 bytes / `bcd13114b3858de54ce4653f305457ae4494a70e3298b35205501bd4e0cd8baa` |
| Round-97 report containing the faulty launch | `c91337bcd72c6bc56674c2b3c220941c840aa19d7ef1b2f7139d6e3c614c7973` |
| Round-85 repair freeze | `b05e9660ad99d273eca7e9b05538fa68da993bdf0f6d40148bfb058fd65ae1ee` |
| v6 manifest | `2e1223f6206c6ebc4adc5c11ed67672afdc55f68e90f725cf8b6930bb67b9948` |
| discovery runner | `b32260ad18abd3f159b7cac1dcd600be2507ff2a89cf60712c5c6f66ccbd70da` |
| extracted bootstrap literal | `19e3f2013a5a0af31c9a43dcb23e54ad15f7d41ef80adcb6f33ea9707fcce6c5` |

This review invoked neither `--execute-frozen` nor `--execute-replica`, did
not call a formal `run_formal` path, and did not construct or evaluate mesh 65
or 97. It wrote no result, evidence, replica, audit, or staging artifact. The
only workspace file added by this round is this report.

## 2. Independent reproduction of the Round-97 zsh failure

Both the live `SHELL` value and the account `UserShell` identify `/bin/zsh`.
In a clean zsh invocation, the minimal Round-97 command-substitution pattern
failed exactly at `status=$?`, because `status` is a zsh read-only special
parameter:

```text
return code                 = 1
stdout bytes                = 0
stderr diagnosis            = read-only variable: status
formal-parent sentinel      = NOT REACHED
```

I then extracted the unique faulty Round-97 block, retained its real
repository setup, descriptor capture, runner SHA check, AST extraction, and
bootstrap-output handling prefix, and replaced the entire formal-parent tail
in memory with a harmless sentinel. Before execution I required the safe
reproducer to contain zero formal, replica, or dry-run mode tokens. It again
returned code 1 with zero stdout and the same read-only-parameter diagnosis;
the formal-parent sentinel was not reached.

Thus the original failure is before the clean-environment formal parent, not a
scientific HOLD or a partially started replica. The Round-97 statement that
the unwrapped block works “from any shell” is false, and the unwrapped
Round-97 block remains superseded.

All seven lexical publication paths were absent before and after both failure
reproductions:

```text
artifacts/data/positive_b_allocation_cusp_discovery_result.json
artifacts/data/positive_b_allocation_cusp_discovery_reproducibility.json
artifacts/data/.positive_b_allocation_cusp_discovery_result.replica_1.json
artifacts/data/.positive_b_allocation_cusp_discovery_result.replica_2.json
artifacts/data/positive_b_allocation_cusp_discovery_independent_audit.json
artifacts/data/.positive_b_allocation_cusp_discovery_result.json.staging
artifacts/data/.positive_b_allocation_cusp_discovery_reproducibility.json.staging
```

## 3. Unique corrected command and shell syntax

Round 98 contains exactly one `bash` fenced block. Independently extracted
with its final newline, its pins are:

| object | bytes | SHA-256 |
|---|---:|---|
| complete Section-4 command | 2284 | `c5b8515a60b4a7c6beecef7caf433182b62d930cc05667c63c6a2ad52fd6647e` |
| heredoc inner Bash block | 2230 | `688eb629860a945dcfdb19e80ade3fe613ad5c8b2a5e92d7893185e59a12ebe3` |

The complete formal block contains exactly one formal-mode token and zero
replica or dry-run mode tokens. Static parsing independently returned:

```text
zsh syntax, complete outer wrapper = PASS
bash syntax, complete outer wrapper = PASS
bash syntax, heredoc inner block    = PASS
```

The first token of the corrected block invokes `/bin/bash`; the heredoc is
therefore interpreted by Bash even when pasted into the user's current zsh.
`status=$?` is valid in that interpreter. No scientific byte, runner byte,
manifest byte, bootstrap byte, flag, or clean-environment field was changed by
the shell repair.

The **only formal launch command authorized by this review** is the exact
Round-98 Section-4 block whose SHA-256 is:

```text
c5b8515a60b4a7c6beecef7caf433182b62d930cc05667c63c6a2ad52fd6647e
```

This report deliberately does not reproduce that block, avoiding a second
copy. The Round-97 block and separate/manual mesh commands are not authorized.

## 4. Full no-science rehearsal of the corrected wrapper

For the sole executable rehearsal, I extracted the exact Round-98 block,
required exactly one formal terminal, and replaced only that final mode token
in memory with `--algebra-dry-run --cells 7`. The executed rehearsal contained
zero formal tokens, zero replica tokens, and exactly one dry-run/cells-7
terminal. It was passed from zsh through the explicit `/bin/bash` wrapper.

This exercised the complete operational prefix:

```text
explicit Bash with set -euo pipefail
  -> frozen repository root and absolute pinned Python/runner/site paths
  -> Python -I -S -B descriptor capture with O_NOFOLLOW
  -> regular-file and before/after fstat identity check
  -> exact runner SHA-256 check
  -> unique AST extraction of ISOLATED_RUNNER_BOOTSTRAP
  -> trailing-newline-safe bootstrap capture and exact bootstrap SHA check
  -> env -i harmless allowlist and fixed one-thread variables
  -> pinned isolated interpreter and exact manifest digest
  -> seven-cell algebra-only terminal
```

The independent rehearsal returned:

```text
return code              = 0
status                   = PASS_ALGEBRA_DRY_RUN_HOLD_SCIENCE
explicit CSR preflight   = PASS
maximum action error     = 2.220446049250313e-16
scientific meshes        = []
canonical stdout bytes   = 1061
canonical stdout SHA-256 = 9fe5c7c2cbab521080af5a3878925b96f5dd8bf3659f067f2734b3049711f366
```

The runner and manifest regular-file identity/hash snapshots were unchanged
across the rehearsal. Their final digests remained respectively
`b32260ad18abd3f159b7cac1dcd600be2507ff2a89cf60712c5c6f66ccbd70da`
and `2e1223f6206c6ebc4adc5c11ed67672afdc55f68e90f725cf8b6930bb67b9948`.
All seven publication paths were again lexically absent before and after the
rehearsal.

## 5. OneDrive and other-writer boundary

The successful rehearsal establishes the corrected shell chain and detects
ordinary visible identity/hash drift. It does not turn a OneDrive-backed,
user-writable checkout into an immutable namespace and does not prove safety
against a malicious same-UID swap/restore writer.

The frozen no-concurrent-writer/no-OneDrive-replacement condition therefore
remains an explicit operational prerequisite for the entire future formal
window. If OneDrive replaces a frozen path, another process writes/relinks a
pin or output path, any initial/final descriptor or lexical snapshot changes,
or any of the seven paths is unexpectedly present, the operator must HOLD and
must not retry by deleting an unowned inode. The command's drift and ownership
checks are defense in depth under that contract, not malicious-writer
prevention.

## 6. Final decision

No new finding was opened. The Round-98 explicit-interpreter repair closes the
Round-97 shell-portability P1 without altering or executing the frozen
science:

```text
P0 = 0
P1 = 0
P2 = 0
decision = GO-FORMAL-SEQUENTIAL-65-THEN-97
interpreter contract = EXACT ROUND-98 /bin/bash WRAPPER ONLY
mesh 97 rule = run only if mesh 65 and every intervening gate do not HOLD
separate/manual mesh commands = NOT AUTHORIZED
formal execution in this round = NOT RUN
scientific meshes in this round = []
```
