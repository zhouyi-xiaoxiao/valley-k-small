# Round 98: allocation-cusp v6 launch-shell erratum

Date: 2026-07-14  
Scope: shell-contract repair only; no frozen scientific byte changed  
Verdict: **ROUND-97-LAUNCH-CLAIM-ERRONEOUS; P1 CLOSED; GO UNDER EXPLICIT BASH CONTRACT**  
Final open findings: **P0 = 0, P1 = 0, P2 = 0**

## 1. Erratum and severity

Round 97 says that its final block can be run “exactly once from any shell.”
That statement is erroneous. In the user's default zsh, `status` is a special
read-only parameter, so the command substitution assignment
`status=$?` fails before the clean-environment formal parent can start:

```text
exit code   = 1
stdout      = 0 bytes
stderr      = /tmp/round98_failure_repro.zsh:20: read-only variable: status
```

This is a **P1 operational/reproducibility finding**: the frozen science was
not wrong, but the sole authorized launch block was not executable in the
documented shell-agnostic manner. It is not a P0 scientific finding. The
failure reproduction contained no formal or replica terminal, and all seven
publication paths were absent both before and after it.

The repair is an explicit interpreter contract: paste the unique block in
Section 4 into the current zsh; its first token invokes `/bin/bash`, and Bash
alone interprets the original inner launch block. Therefore `status=$?` is
valid without changing the descriptor capture, runner pin, AST extraction,
bootstrap bytes, clean environment, or frozen terminal.

## 2. Frozen anchors and non-science boundary

The following bytes were independently rehashed and not edited:

| role | SHA-256 |
|---|---|
| Round-97 report containing the faulty shell claim | `c91337bcd72c6bc56674c2b3c220941c840aa19d7ef1b2f7139d6e3c614c7973` |
| Round-85 repair freeze | `b05e9660ad99d273eca7e9b05538fa68da993bdf0f6d40148bfb058fd65ae1ee` |
| v6 manifest | `2e1223f6206c6ebc4adc5c11ed67672afdc55f68e90f725cf8b6930bb67b9948` |
| discovery runner | `b32260ad18abd3f159b7cac1dcd600be2507ff2a89cf60712c5c6f66ccbd70da` |
| extracted bootstrap literal | `19e3f2013a5a0af31c9a43dcb23e54ad15f7d41ef80adcb6f33ea9707fcce6c5` |

No `--execute-frozen`, `--execute-replica`, formal `run_formal`, or scientific
mesh was invoked in this erratum. No Round-97, manifest, runner, protocol, or
other workspace byte was edited; this erratum is the only added workspace
file.

## 3. Verification of the repaired shell contract

The exact Section-4 wrapper was checked without executing it:

```text
zsh -n outer wrapper                 PASS
bash -n original inner launch block PASS
--execute-frozen token count         1
Section-4 command SHA-256            c5b8515a60b4a7c6beecef7caf433182b62d930cc05667c63c6a2ad52fd6647e
inner block SHA-256                  688eb629860a945dcfdb19e80ade3fe613ad5c8b2a5e92d7893185e59a12ebe3
```

For an executable no-science rehearsal, a verifier extracted the same inner
block, required exactly one `--execute-frozen`, replaced only that final token
in memory with `--algebra-dry-run --cells 7`, and ran the result under
`/bin/bash`. Thus this exercised the repaired Bash interpretation, descriptor
plus before/after `fstat` capture, runner SHA-256 match, unique AST bootstrap
extraction, bootstrap hash check, clean `env -i`, and pinned `-I -S -B`
interpreter, but no scientific mesh:

```text
return code              = 0
status                   = PASS_ALGEBRA_DRY_RUN_HOLD_SCIENCE
explicit CSR preflight   = PASS
maximum error            = 2.220446049250313e-16
scientific meshes        = []
canonical stdout bytes   = 1061
canonical stdout SHA-256 = 9fe5c7c2cbab521080af5a3878925b96f5dd8bf3659f067f2734b3049711f366
```

The seven result, evidence, replica, independent-audit, and staging paths were
lexically absent immediately before the failure reproduction and after the
successful no-science rehearsal. The formal science remains unexecuted.

Closure ledger:

```text
P0 = 0
P1 = 0  (the Round-97 shell-portability P1 is closed by explicit /bin/bash)
P2 = 0
decision = GO-FORMAL-SEQUENTIAL-65-THEN-97 UNDER EXPLICIT BASH CONTRACT
mesh 97 rule = run only if mesh 65 and every intervening gate do not HOLD
separate/manual mesh commands = NOT AUTHORIZED
```

## 4. Unique corrected formal command — not executed in this round

This supersedes only Round 97's “any shell” launch wording and command
wrapper. From the current zsh, paste this block exactly once. Do not run the
unwrapped Round-97 block. The expected atomic paths and rollback semantics
remain exactly those frozen and audited in Rounds 85 and 97.

```bash
/bin/bash <<'ROUND98_FORMAL_BASH'
set -euo pipefail
cd '/Users/ae23069/Library/CloudStorage/OneDrive-UniversityofBristol/Desktop/valley-k-small'
ROOT=$(pwd -P)
PY="$ROOT/.venv/bin/python"
RUNNER="$ROOT/research/reports/encounter_multimodal_prr/code/positive_b_allocation_cusp_discovery.py"
SITE="$ROOT/.venv/lib/python3.12/site-packages"
RUNNER_SHA256='b32260ad18abd3f159b7cac1dcd600be2507ff2a89cf60712c5c6f66ccbd70da'
BOOTSTRAP_X="$("$PY" -I -S -B -c '
import ast, hashlib, os, stat, sys
path, expected = sys.argv[1:]
if not os.path.isabs(path):
    raise SystemExit("runner path is not absolute")
fd = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
try:
    before = os.fstat(fd)
    chunks = []
    while True:
        block = os.read(fd, 1024 * 1024)
        if not block:
            break
        chunks.append(block)
    after = os.fstat(fd)
finally:
    os.close(fd)
source = b"".join(chunks)
identity = lambda item: (item.st_dev, item.st_ino, item.st_size, item.st_mtime_ns)
if not stat.S_ISREG(before.st_mode) or identity(before) != identity(after):
    raise SystemExit("runner descriptor changed during capture")
if hashlib.sha256(source).hexdigest() != expected:
    raise SystemExit("runner SHA-256 mismatch")
tree = ast.parse(source, filename=path)
values = [
    ast.literal_eval(node.value)
    for node in tree.body
    if isinstance(node, ast.Assign)
    and any(
        isinstance(target, ast.Name) and target.id == "ISOLATED_RUNNER_BOOTSTRAP"
        for target in node.targets
    )
]
if len(values) != 1 or not isinstance(values[0], str):
    raise SystemExit("frozen bootstrap literal is not unique")
sys.stdout.write(values[0])
' "$RUNNER" "$RUNNER_SHA256"; status=$?; printf x; exit "$status")"
BOOTSTRAP="${BOOTSTRAP_X%x}"
test "$(printf %s "$BOOTSTRAP" | shasum -a 256 | awk '{print $1}')" = \
  '19e3f2013a5a0af31c9a43dcb23e54ad15f7d41ef80adcb6f33ea9707fcce6c5'
env -i HOME="$HOME" PATH='/usr/bin:/bin' LANG=C LC_ALL=C TMPDIR=/private/tmp \
  OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  VECLIB_MAXIMUM_THREADS=1 NUMEXPR_NUM_THREADS=1 \
  "$PY" -I -S -B -c "$BOOTSTRAP" "$RUNNER" "$SITE" \
  --execute-frozen \
  --expected-manifest-sha256 2e1223f6206c6ebc4adc5c11ed67672afdc55f68e90f725cf8b6930bb67b9948
ROUND98_FORMAL_BASH
```
