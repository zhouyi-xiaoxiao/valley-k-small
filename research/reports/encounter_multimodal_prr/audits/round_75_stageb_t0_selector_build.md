# Round 75: Stage-B v5 T0 selector package build and adversarial self-audit

Date: 2026-07-14  
Role: result-blind implementation author and first-party adversarial tester  
Verdict: **GO-PACKAGE-SELF / HOLD-INDEPENDENT-AUDIT**  
Authorization: **AUTHORIZED-SCIENTIFIC-COMMAND: NONE**

## 1. Scope and immutable snapshot

This round implemented and self-attacked the science-free v5 T0 selector,
directed arithmetic, odd-grid Boolean, and saved-field role radii.  It did not
substitute a Stage-A result, evaluate mesh 65/97, run Stage-B FV, solve a
cusp/fold, run off-lattice trajectories, create a scientific manifest/result,
or promote a manuscript claim.

The audited bytes are:

| role | path | SHA-256 |
|---|---|---|
| accepted v5 design | `notes/positive_b_stage_b_validation_design_v5.md` | `136085075ad23fc22a40cf03725c9151f11ff356cff4f6f39e5c5fbb24317ddd` |
| imported v4 design | `notes/positive_b_stage_b_validation_design_v4.md` | `e5ca55c8a63d72b8f1bb0ded4d6ebba29a75d94e96ce07a6b7ebf15dcf100691` |
| independent Round-73 acceptance | `audits/round_73_stageb_v5_independent_attack.md` | `36c0f502b90cb98e8cdeedd5a1621b0ffa1e3bcc5bc49b5490d1eccde9e7dcf8` |
| substantive implementation | `code/positive_b_stage_b_t0_selector.py` | `6de92be01d1cc1b15cefc45ca640678e4e44d9eee4ccad11fedc73f38c9b03d8` |
| v5-frozen source-name shim | `code/positive_b_stage_b_t1_selector_v5.py` | `aeb3094be3b0466a9cf75d68f1d6e4cca7df129575ca14ef09cf7371e109c9ec` |
| synthetic mutation suite | `code/test_positive_b_stage_b_t1_selector_v5.py` | `4d4d5bacc7484fdf75e7eb76c85f1d77454b92bf0b141837e7918a729bae978c` |
| MPFR dependency lock | `code/positive_b_stage_b_t0_requirements.lock` | `52f905ed765f2fa9422dd28e082b3abeb9e46c0b391b9fd6a9b32a5f2fc0a2a2` |
| substantive T0 protocol | `notes/positive_b_stage_b_t0_selector_protocol_v1.md` | `fedf5d77629f8764a970222421fc53b4b5392ae8be5df027c258fa120fd9eb34` |
| required v5 protocol-name bridge | `notes/positive_b_stage_b_t1_selector_protocol_v5.md` | `eda4193f026993a2a93b21ac08a61561ff86db4a45e16e2f8e51acb0c72612a4` |

The v5-named source is deliberately a logic-free re-export of the substantive
T0 module, not a competing implementation.  The bridge pins the complete
mapping and substantive protocol.  The future independent audit must pin this
Round-75 report as a separate downstream byte; no self-hash cycle is created.

## 2. Executive result and open ledger

The package survived all implemented Round-67/70/73 mutations and the added
schema, runtime, TOCTOU, and transcendental attacks.  The self-audit found and
repaired during construction:

1. a node-adjacency `zip(strict=True)` programming error;
2. an initially cached MPFR-byte verification that could miss post-call file
   drift;
3. an in-memory mapping entry that bypassed canonical-byte verification;
4. missing `log`/`exp` implementations despite their presence in the v5
   arithmetic vocabulary; and
5. MPFR contexts that were not initially explicit against caller-global
   precision/rounding mutation.

All five were repaired before this snapshot and have executable regressions.
The current ledger is:

```text
open package-self P0 = 0
open package-self P1 = 0
open package-self P2 = 0

closed construction findings = 5
closed process observation    = 1

package verdict = GO-PACKAGE-SELF
next verdict    = HOLD-INDEPENDENT-AUDIT
scientific object/value/result status = NOT READ / NOT RUN / NOT CREATED

AUTHORIZED-SCIENTIFIC-COMMAND: NONE
```

This is a first-party verdict.  It cannot substitute for the independent
package audit required by v5/Round 73.

## 3. Exact arithmetic and MPFR attack

### 3.1 Algebraic binary64 trace

Every algebraic leaf is a finite exact binary64 converted to `Fraction`.
Every printed operation has its own `rn_fraction`, `down64`, or `up64`; no
native multiply-add, FMA, reassociation, `hypot`, extended intermediate, or
host-libm transcendental decides a selector/gate.  `nextUp`/`nextDown` operate
on IEEE bits.  Negative zero is canonicalized only after endpoint direction is
decided.

The tests demonstrate:

- `Fraction(1,10)` lower/upper enclosure and adjacency;
- positive/negative half-minimum-subnormal endpoints;
- ties-to-even at both even-lower and odd-lower midpoints;
- exact sqrt-midpoint parity selection;
- `NaN`, infinities, invalid domains, and overflow HOLD; and
- a fixed FMA-sensitive two-vector where separate RN yields
  `-0x1.0c00010c00000p-22` and fused evaluation would yield
  `-0x1.0c00010c40000p-22`.

### 3.2 MPFR executable freeze and exercised endpoints

The installed vehicle is `gmpy2 2.2.1`, MPFR `4.2.1`, GMP `6.3.0`, MPC
`1.3.1`.  The macOS arm64 wheel SHA-256 is
`bd09dd43d199908c1d1d501c5de842b3bf754f99b94af5b5ef0e26e3b716d2d5`;
the loaded extension SHA-256 is
`9586b7c4b887704b57576f52b73a8c45437946d2b172095d82c20fa0871a415b`.
The module verifies the extension from a non-symlink stable descriptor on each
call path rather than trusting only package metadata.

Every local MPFR context fixes `RoundDown`/`RoundUp`, precision, extreme
exponent bounds, traps, subnormal policy, complex policy, rational division,
and GIL-release policy.  A test mutates the caller-global precision to 17 and
rounding to `RoundUp`; the pinned local `log(2)` and `exp(1)` results remain
unchanged.

The test suite actually calls and checks all directed/RN exports:

```text
sqrt_down64(2) = 0x1.6a09e667f3bccp+0
sqrt_rn(2)     = 0x1.6a09e667f3bcdp+0
sqrt_up64(2)   = 0x1.6a09e667f3bcdp+0

log_down64(2)  = 0x1.62e42fefa39efp-1
log_rn(2)      = 0x1.62e42fefa39efp-1
log_up64(2)    = 0x1.62e42fefa39f0p-1

exp_down64(1)  = 0x1.5bf0a8b145769p+1
exp_rn(1)      = 0x1.5bf0a8b145769p+1
exp_up64(1)    = 0x1.5bf0a8b14576ap+1
```

It separately calls the exact `log(1)=0`, `exp(0)=1`, minimum-subnormal sqrt,
negative-log/sqrt domain HOLD, and exponential overflow HOLD.  `sqrt` uses
exact rational square/midpoint resolution.  Non-special `log`/`exp` double
outward precision until both bounds identify one endpoint; non-separation is
HOLD rather than a numerical tolerance.

## 4. Selector adversarial replay

The source join requires identical index sets across generation, mesh-65, and
mesh-97; unique indices and physical-control bytes; canonical theta/weight
bytes; `EVALUATED` and all-gates-pass rows; and identical saved topology/count.
No collection-order or branch-order side label is accepted.

The self-audit exercised the literal record and frame trace:

- exact target bytes, offset/residual/index rank, unique adjacent saved nodes;
- central `theta_n-theta_p`, exact `t_n-t_p`, `sigma`, zero-omega HOLD, and
  required negative-omega flip;
- fixed multiply/multiply/add/sqrt normalization and rotation;
- exact previous/base and next/base `ell` operands;
- displacement only from the comparison node;
- all eligibility comparisons and sign-derived side labels;
- complete pair rank with no duplicate/tie/later-pair fallback; and
- independent second branch, cross-branch collision HOLD, exact count-pair
  set `{(1,2),(2,3)}`.

Synthetic mutations from predecessor, successor, fold, cusp, and origin each
change eligibility/HOLD.  Reversed/one-sided secants and omitted orientation
flip change frame/labels.  A zero orientation holds.  A one-ulp `ell` mutation
changes an eligibility boundary.  Duplicate records, indices, controls,
nonadjacent nodes, noncanonical target/zero, nonfinite values, and source-join
drift all hold.  The collision fixture deliberately contains an eligible later
pair and still holds instead of falling back.

The frozen canonical selector input/output are byte deterministic:

```text
input  4186 bytes  887ae07babcbb8365525634da98d5104b4ff7aeca03ebd7e5e46982bb67477a9
output 2513 bytes  262eeb8907dea3a4ff8ac66f850fb2ff408c1c01a40c52131c380649873859ed
```

The output contains copied exact control bytes, frame/ranks, branch-side
labels, counts/topology, per-control hashes, all normative hashes, and only
authorization `NONE`.

## 5. Round-70/73 odd gate and Round-67 role-radius replay

The exported scalar/vector odd gate uses exact-rational `Dplus`/`Dminus`.  It
rejects the Round-70 `0.300,0.300,0.304` fixture, accepts both-at-floor and
strict-contraction controls, rejects a single bad vector coordinate, and
detects swapped/omitted odd levels.

For the Round-73 half-ulp fixture, a native RN subtraction returns exactly
`ODD_FLOOR`; the implementation returns `nextUp(ODD_FLOOR)` and the complete
Boolean rejects.  Thus the earlier Round-72 helper cannot leak into the
production gate.

The seven-role routine evaluates every downward boundary/separation component
and `rho`, then independently outward-checks all six global-box faces and all
21 pairwise inequalities.  Seven synthetic roles pass; coincident, unordered,
and nonfinite roles hold.  One-ulp pair-touch and box-face mutations flip the
strict decision as intended.  Canonical pins are:

```text
role input   759 bytes  60064e54fb75afdb8449ef8bafc8a8f5e6f406d5d62bf95bd765b2064d195abb
role output  875 bytes  88bfb423328fb4271cc9ec9867c06c6b1774643ed71ccd344991cd130844a80a
```

## 6. Schema, provenance, and authorization attack

Only `select_saved_controls_bytes` and `compute_role_radii_bytes` are public
byte-level transforms.  JSON numbers for binary64 data, alternate whitespace,
trailing newline, duplicate keys, abbreviated/noncanonical hex, signed zero,
nonfinite constants, missing/extra fields, wrong versions, and wrong
authorization all hold.  No input path or CLI/main function exists.

Normative files and the MPFR extension use lexical component `lstat`,
`O_NOFOLLOW`, regular-file descriptor checks, byte caps, pre/post `fstat`,
post-read inode comparison, and SHA-256.  Tests reject final/component
symlinks, wrong hashes, descriptor copy/replace, MPFR version drift, and
noncanonical JSON.  Removing the initial MPFR verification cache closed a
same-process post-call drift path.

Static source inspection finds no import or command entry for NumPy, SciPy,
subprocess, the Stage-A producer, the fixed-`B` producer, FV, or off-lattice
code.  The v5 shim re-exports only the substantive module's explicit public
surface.

## 7. Required construction-process disclosure

At the beginning of this round, while searching for existing snapshot/schema
patterns, the following broad lexical command was run:

```text
rg -n "Stage-A|screened_mesh|candidate_generation|saved comparison|selector|role radii|odd_gate|canonical JSON|snapshot|O_NOFOLLOW|authorization" code notes audits | head -300
```

Because its path set included `code`, its truncated output contained a few
symbol-level matching lines from `code/positive_b_allocation_cusp_stage_a.py`.
This is disclosed rather than described as absolute producer non-inspection.
The producer file was not deliberately opened as a document, imported, or
executed; no canonical/hidden Stage-A object, result, manifest, mesh-65/97
value, control value, or scientific numerical output was displayed or used.
Implementation decisions came from the frozen v5/Round-73 text and synthetic
fixtures only.

The self-audit classifies this as a closed process observation because it
exposed source symbols but no scientific object/value/result.  The required
independent audit must explicitly accept or reclassify it.  Until then the
state remains `HOLD-INDEPENDENT-AUDIT` regardless of the technical PASS.

## 8. Executed evidence

All commands ran from the report directory with `../../../.venv/bin/python`:

```text
ruff check implementation + shim + tests
  All checks passed!

py_compile implementation + shim + tests
  PASS

pytest -q code/test_positive_b_stage_b_t1_selector_v5.py
  29 passed

pytest -q Round67 + Round69 + Round70 + Round72 + Round73 + package tests
  62 passed
```

The joint collection was independently counted by pytest as exactly 62 tests.
No test imports a scientific producer or opens a scientific object/result.

## 9. Final boundary

```text
P0 = 0
P1 = 0
P2 = 0

GO-PACKAGE-SELF
HOLD-INDEPENDENT-AUDIT
SCIENTIFIC OBJECT/VALUE/RESULT: NOT READ / NOT RUN / NOT CREATED

AUTHORIZED-SCIENTIFIC-COMMAND: NONE
```

The next permitted action is only a distinct result-blind attack on the exact
bytes in Section 1, including the process disclosure in Section 7.  It is not
permission to read Stage-A values, instantiate T1, evaluate mesh 65/97, run
Stage-B FV/off-lattice science, create a scientific manifest/result, or change
the manuscript.
