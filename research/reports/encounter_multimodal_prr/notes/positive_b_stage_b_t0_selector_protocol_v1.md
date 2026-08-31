# Positive-`B` Stage-B v5 T0 selector package protocol v1

Date: 2026-07-14  
Package self-status: **GO-PACKAGE-SELF**  
Next boundary: **HOLD-INDEPENDENT-AUDIT**  
Scientific object/value/result status: **NOT READ / NOT RUN / NOT CREATED**  
Authorization: **AUTHORIZED-SCIENTIFIC-COMMAND: NONE**

## 1. Purpose and hard boundary

This protocol freezes the result-blind implementation of Sections 3--6 and
the mandatory Section-10 mutation fixtures in
`notes/positive_b_stage_b_validation_design_v5.md`.  It is a byte-to-byte
library package only.  It does not locate a cusp/fold, evaluate a mesh, load a
Stage-A object, create a Stage-B manifest, run FV/off-lattice science, or
promote a manuscript claim.

The only scientific authorization literal accepted by either canonical input
schema and copied into every output is

```text
AUTHORIZED-SCIENTIFIC-COMMAND: NONE
```

The status line above is specifically about Stage-A/Stage-B scientific
objects, values, results, evidence, manifests, and executions.  A construction
search emitted a few producer-source symbol lines; the exact command and scope
are disclosed in the Round-75 self-audit.  No producer was imported or run and
no canonical/hidden scientific value or object was exposed.  The independent
package audit must judge this process observation explicitly.

Any other literal, missing hash, noncanonical byte representation, schema
drift, nonfinite value, duplicate/tie, symlink, descriptor race, runtime drift,
or failed numerical gate is HOLD.  This self-status cannot open T1 or any
scientific boundary.  A distinct independent attack on the exact package bytes
is mandatory next.

## 2. Frozen inputs and package bytes

### 2.1 Normative inputs verified by every byte-level selector/radius call

| role | path | SHA-256 |
|---|---|---|
| accepted v5 design | `notes/positive_b_stage_b_validation_design_v5.md` | `136085075ad23fc22a40cf03725c9151f11ff356cff4f6f39e5c5fbb24317ddd` |
| imported v4 snapshot | `notes/positive_b_stage_b_validation_design_v4.md` | `e5ca55c8a63d72b8f1bb0ded4d6ebba29a75d94e96ce07a6b7ebf15dcf100691` |
| independent v5 acceptance | `audits/round_73_stageb_v5_independent_attack.md` | `36c0f502b90cb98e8cdeedd5a1621b0ffa1e3bcc5bc49b5490d1eccde9e7dcf8` |

### 2.2 T0 implementation package

| role | path | SHA-256 |
|---|---|---|
| substantive T0 implementation | `code/positive_b_stage_b_t0_selector.py` | `6de92be01d1cc1b15cefc45ca640678e4e44d9eee4ccad11fedc73f38c9b03d8` |
| v5-frozen filename shim | `code/positive_b_stage_b_t1_selector_v5.py` | `aeb3094be3b0466a9cf75d68f1d6e4cca7df129575ca14ef09cf7371e109c9ec` |
| complete synthetic mutation suite | `code/test_positive_b_stage_b_t1_selector_v5.py` | `4d4d5bacc7484fdf75e7eb76c85f1d77454b92bf0b141837e7918a729bae978c` |
| MPFR dependency lock | `code/positive_b_stage_b_t0_requirements.lock` | `52f905ed765f2fa9422dd28e082b3abeb9e46c0b391b9fd6a9b32a5f2fc0a2a2` |

V5 froze the three names containing `t1_selector_v5`; the implementation task
standardized the semantic name as `t0_selector`.  The required v5 source name
therefore exists as a no-entry-point shim that re-exports only the substantive
module's explicit `__all__`.  No alternative implementation lives in the
shim.  The v5-named protocol file is a hash-closed bridge to this protocol and
the bytes above; neither document changes the v5 design.

## 3. Arithmetic/runtime freeze

The module uses exact `Fraction` syntax trees for every algebraic operation.
Each `RN`, `down64`, and `up64` is a separate explicit operation; `nextUp` and
`nextDown` are bit-adjacency operations.  Signed zero is canonicalized only
after the directed comparison; nonfinite inputs and intermediates HOLD.

The executable transcendental vehicle is frozen as follows:

| item | frozen value |
|---|---|
| Python ABI | CPython 3.12, Darwin arm64 |
| Python compiler | `clang` |
| Python `PY_CFLAGS` | `-fno-strict-overflow -Wsign-compare -Wunreachable-code -fno-common -dynamic -DNDEBUG -g -O3 -Wall` |
| wheel | `gmpy2-2.2.1-cp312-cp312-macosx_11_0_arm64.whl` |
| wheel SHA-256 | `bd09dd43d199908c1d1d501c5de842b3bf754f99b94af5b5ef0e26e3b716d2d5` |
| loaded extension | `gmpy2.cpython-312-darwin.so` |
| extension SHA-256 | `9586b7c4b887704b57576f52b73a8c45437946d2b172095d82c20fa0871a415b` |
| gmpy2 / MPFR / GMP / MPC | `2.2.1` / `4.2.1` / `6.3.0` / `1.3.1` |
| directed contexts | explicit `RoundDown`/`RoundUp`, `emin=-1073741823`, `emax=1073741823`, traps/subnormalize/complex/GIL release disabled; 128, 256, 512, 1024, 2048, 4096 bits; 8192 also permitted for `log`/`exp` separation |

The selector source is Python and has no native multiply-add expression to
contract: binary64 products/additions are exact rational expressions followed
by one explicit RN conversion.  The prebuilt MPFR extension is frozen by its
complete executable byte hash rather than rebuilt locally.  Thus an upstream
compiler metadata omission cannot select a different executable.  Any ABI,
version, compiler/flag, extension-byte, or rounding-context drift is HOLD.

`sqrtRN` uses an MPFR outward interval plus exact rational square/midpoint and
ties-to-even checks.  `sqrt_down64`/`sqrt_up64` use exact square comparison.
`log(1)=0` and `exp(0)=1` are exact special cases.  Other `log`/`exp` RN and
directed endpoints double precision until both outward MPFR bounds identify
one binary64 endpoint; failure to separate is HOLD, never a tolerance.
The tests actually exercise all nine operations:

```text
sqrt_down64, sqrt_rn, sqrt_up64
log_down64,  log_rn,  log_up64
exp_down64,  exp_rn,  exp_up64
```

They pin `sqrt(2)`, `log(2)`, `exp(1)`, exact `log(1)`/`exp(0)`, directed
adjacency, negative-domain HOLD, overflow HOLD, and the minimum-subnormal
square-root result.  Host `math.sqrt`, `math.log`, `math.exp`, FMA, `hypot`,
extended intermediates, and reassociation are absent from decisions.

## 4. Descriptor, JSON, schema, and authorization contract

The frozen design/audit inputs and MPFR extension are opened with
`O_NOFOLLOW` from lexically checked non-symlink components.  One descriptor
supplies the bytes used for size, hash, and verification.  Pre/post `fstat`,
post-read lexical inode, full-byte SHA-256, and a fixed byte cap close
copy/replace/restore and path races.

`select_saved_controls_bytes(payload)` and
`compute_role_radii_bytes(payload)` are the only byte-level package entry
points.  They accept duplicate-key-rejecting, ASCII canonical JSON only:

```text
sort_keys=true, separators=(",",":"), ensure_ascii=true, no JSON floats
```

Every binary64 datum is a unique lowercase Python `float.hex()` string.
Alternate zero, abbreviated hex, decimal JSON float, `NaN`, infinity,
whitespace, trailing newline, duplicate key, bool-as-index, out-of-range index,
missing/extra field, wrong schema, or changed authorization HOLD.

The selector input schema has exactly the generation, evaluated mesh-65,
evaluated mesh-97, and two saved-branch collections printed in the tests.  It
requires a one-to-one index join; byte-identical `theta`/weights; evaluated,
all-gates-pass rows; identical topology/count; unique physical-control bytes;
exact comparison-record/node schemas; and two unique branch IDs.  The module
accepts bytes supplied by a caller but has no file/path/CLI adapter for a
Stage-A object.

The synthetic canonical byte pins are:

| object | bytes | SHA-256 |
|---|---:|---|
| selector input fixture | 4186 | `887ae07babcbb8365525634da98d5104b4ff7aeca03ebd7e5e46982bb67477a9` |
| selector output fixture | 2513 | `262eeb8907dea3a4ff8ac66f850fb2ff408c1c01a40c52131c380649873859ed` |
| seven-role input fixture | 759 | `60064e54fb75afdb8449ef8bafc8a8f5e6f406d5d62bf95bd765b2064d195abb` |
| seven-role output fixture | 875 | `88bfb423328fb4271cc9ec9867c06c6b1774643ed71ccd344991cd130844a80a` |

## 5. Literal selector/gate implementation

For each branch the source implements, in the printed order:

1. target-byte filtering and `(offset_error,residual_key,acceptance_index)`;
2. unique adjacent predecessor/base/successor nodes;
3. central `theta_n-theta_p`, `t_n-t_p`, integer `sigma`, zero-omega HOLD,
   and the required negative-omega flip;
4. multiply/multiply/add/sqrt normalization and fixed rotation;
5. the two local `ell` vectors and numeric minimum;
6. comparison-node displacement `theta_i-theta_b`;
7. RN `s,q,r`, all four eligibility conditions, sign-derived labels;
8. complete five-field pair rank, no duplicate/tie or later-pair fallback;
9. independent second-branch selection, cross-branch collision HOLD; and
10. exact unordered count pairs `{(1,2),(2,3)}`.

The output copies the selected control hex bytes and records side labels,
counts, topology, comparison/frame/pair ranks, per-control SHA-256, the three
normative hashes, and authorization `NONE` in deterministic canonical JSON.

The scalar and vector odd-grid functions use exact-rational `Dplus`/`Dminus`
and the literal complete Boolean

```text
max(D_coarse_plus,D_fine_plus) <= ODD_FLOOR
or D_fine_plus < D_coarse_minus.
```

The role-radius entry reconstructs seven ascending role IDs, every downward
box/separation component and `rho`, then separately outward-checks all six box
faces and all 21 pairwise strict inequalities.

## 6. Executed synthetic attack matrix

The 29 package tests include:

- Round-70 `0.300/0.300/0.304` rejection, both-floor and strict-contraction
  controls, a bad vector coordinate, swapped/omitted-grid mutations;
- Round-73 exact half-ulp floor attack where native RN accepts and outward
  `nextUp(ODD_FLOOR)` rejects;
- `Fraction(1,10)` directed adjacency, signed zero, minimum subnormal,
  binary64 halfway/ties-to-even, nonfinite and overflow HOLD;
- FMA-sensitive dot data whose separate-RN and fused values differ;
- predecessor/successor/fold/cusp/origin displacement mutations;
- reversed and one-sided secants, omitted negative-omega flip, zero omega;
- exact `ell` operands and a one-ulp eligibility flip;
- duplicate index/control/record/rank routes, nonadjacent nodes, target-byte
  drift, cross-branch collision with an eligible later pair, and no fallback;
- source-join, status, gate, topology, count, schema, JSON, and authorization
  mutations;
- seven role radii, one-ulp box-face and pair-touch failures, order,
  nonfinite, and coincident-seed HOLD;
- final/component symlinks, wrong hash, descriptor replace, MPFR version drift;
  and
- static absence of scientific imports and executable/CLI entry points.

The unchanged historical Round-67, Round-69, Round-70, Round-72, and Round-73
science-free tests are run jointly with this suite.

## 7. Reproduction commands and current result

From this report directory, using the report's `../../../.venv`:

```text
python -m ruff check \
  code/positive_b_stage_b_t0_selector.py \
  code/positive_b_stage_b_t1_selector_v5.py \
  code/test_positive_b_stage_b_t1_selector_v5.py

python -m py_compile \
  code/positive_b_stage_b_t0_selector.py \
  code/positive_b_stage_b_t1_selector_v5.py \
  code/test_positive_b_stage_b_t1_selector_v5.py

python -m pytest -q code/test_positive_b_stage_b_t1_selector_v5.py
# 29 passed

python -m pytest -q \
  code/test_stageb_v3_design_round67.py \
  code/test_stageb_v4_design_resolution.py \
  code/test_stageb_v4_design_round70.py \
  code/test_stageb_v5_design_resolution.py \
  code/test_stageb_v5_design_round73.py \
  code/test_positive_b_stage_b_t1_selector_v5.py
# 62 passed
```

Ruff: PASS.  `py_compile`: PASS.  Package tests: 29/29 PASS.  Historical plus
package tests: 62/62 PASS.

## 8. Self-audit ledger and next action

```text
open package-self P0 = 0
open package-self P1 = 0
open package-self P2 = 0

package self-status = GO-PACKAGE-SELF
next status         = HOLD-INDEPENDENT-AUDIT
scientific object/value/result status = NOT READ / NOT RUN / NOT CREATED

AUTHORIZED-SCIENTIFIC-COMMAND: NONE
```

The only permitted next action is an independent, result-blind attack on the
exact v5 design, implementation, shim, tests, dependency lock, both protocol
files, and self-audit bytes.  No Stage-A substitution, mesh-65/97 evaluation,
Stage-B FV/off-lattice run, scientific manifest/result creation, or claim
promotion is authorized.
