# Round 78: independent attack on the Stage-B v5 T0 selector package

Date: 2026-07-14  
Role: independent, result-blind package, arithmetic, selector, and provenance
attacker; distinct from the Round-75 implementation author  
Verdict: **HOLD-PACKAGE / HOLD-EXECUTION**  
Authorization: **AUTHORIZED-SCIENTIFIC-COMMAND: NONE**

## 1. Scope and hard result-blind boundary

This round independently attacked only the frozen v4/v5 design texts, Round
73, Round 75, the T0 implementation, v5 filename shim, package tests,
dependency lock, and the two selector protocols.  It used hand-built
synthetic payloads and temporary import environments only.

It did **not** open, import, inspect, execute, or create any Stage-A or Stage-B
scientific object, canonical/hidden scientific value, producer, scientific
manifest, result, evidence, FV/off-lattice path, mesh-65/97 computation, or
manuscript object.  No scientific command is authorized by this audit.

The attacked snapshots were independently rehashed:

| role | repository path | SHA-256 |
| --- | --- | --- |
| imported v4 design | `notes/positive_b_stage_b_validation_design_v4.md` | `e5ca55c8a63d72b8f1bb0ded4d6ebba29a75d94e96ce07a6b7ebf15dcf100691` |
| accepted v5 design | `notes/positive_b_stage_b_validation_design_v5.md` | `136085075ad23fc22a40cf03725c9151f11ff356cff4f6f39e5c5fbb24317ddd` |
| independent v5 design audit | `audits/round_73_stageb_v5_independent_attack.md` | `36c0f502b90cb98e8cdeedd5a1621b0ffa1e3bcc5bc49b5490d1eccde9e7dcf8` |
| Round-75 self-audit | `audits/round_75_stageb_t0_selector_build.md` | `66dff9711b9d3a19734884cc8a60eb323801fb9b480bc39980bc268f8e332952` |
| substantive implementation | `code/positive_b_stage_b_t0_selector.py` | `6de92be01d1cc1b15cefc45ca640678e4e44d9eee4ccad11fedc73f38c9b03d8` |
| v5-frozen filename shim | `code/positive_b_stage_b_t1_selector_v5.py` | `aeb3094be3b0466a9cf75d68f1d6e4cca7df129575ca14ef09cf7371e109c9ec` |
| Round-75 synthetic tests | `code/test_positive_b_stage_b_t1_selector_v5.py` | `4d4d5bacc7484fdf75e7eb76c85f1d77454b92bf0b141837e7918a729bae978c` |
| dependency lock | `code/positive_b_stage_b_t0_requirements.lock` | `52f905ed765f2fa9422dd28e082b3abeb9e46c0b391b9fd6a9b32a5f2fc0a2a2` |
| substantive T0 protocol | `notes/positive_b_stage_b_t0_selector_protocol_v1.md` | `fedf5d77629f8764a970222421fc53b4b5392ae8be5df027c258fa120fd9eb34` |
| v5 protocol-name bridge | `notes/positive_b_stage_b_t1_selector_protocol_v5.md` | `eda4193f026993a2a93b21ac08a61561ff86db4a45e16e2f8e51acb0c72612a4` |
| new Round-78 synthetic attacks | `code/test_stageb_t0_selector_round78.py` | `b20b08ec11d5730ef134b04840792f767fc4faaa60330d4549b781e1688f6866` |

All attacked files matched the Round-75 table.  The HOLD is caused by live
contract bypasses in those exact bytes, not stale-file drift.

## 2. Executive decision

The authentic substantive implementation is strong when it is imported
directly in the clean repository environment.  Its exact-rational operation
order, Round-73 half-ulp odd gate, source join, frame/orientation, complete
pair rank, no-fallback collision behavior, role radii, strict JSON/types, and
authorization literal survived direct replay.

The frozen package boundary does not survive import/provenance attack:

1. the exact filename frozen by v5 is a two-line unqualified re-export, not
   the source that implements v5 Sections 3--5;
2. an earlier `PYTHONPATH` entry can supply an arbitrary module named
   `positive_b_stage_b_t0_selector`, and the authentic frozen shim executes it
   without any hash or path check;
3. `verify_mpfr_runtime()` hashes a sibling native extension but executes the
   unpinned `gmpy2/__init__.py` package namespace and unpinned dependent
   libraries; and
4. the public calls never bind the implementation, shim, tests, lock, or
   protocols whose hashes are only documentary.

The first bypass returned arbitrary synthetic selector bytes through the
authentic shim.  The second passed `verify_mpfr_runtime()` with the expected
native-extension hash while an unpinned synthetic wrapper changed
`expRN(1)` from
`0x1.5bf0a8b145769p+1` to `0x1.0000000000000p+0`.

Therefore the package is not a T0-frozen executable transform and cannot be
accepted for future Stage-A/T1 consumption.

```text
P0 = 2
P1 = 2
P2 = 3

package verdict   = HOLD-PACKAGE
execution verdict = HOLD-EXECUTION
science status    = NOT RUN / NOT INSPECTED

AUTHORIZED-SCIENTIFIC-COMMAND: NONE
```

## 3. Severity ledger

| ID | Severity | Finding | Consequence |
| --- | --- | --- | --- |
| R78-P0-1 | P0 | The v5-frozen source is an unqualified shim.  `PYTHONPATH`/`sys.modules` substitution can execute an arbitrary same-name substantive module while the authentic shim bytes remain unchanged.  The shim therefore does not “implement Sections 3--5 literally” and does not re-export a byte-pinned implementation as its docstring claims. | Arbitrary saved controls/output can be substituted after the supposed T0 freeze. |
| R78-P0-2 | P0 | MPFR attestation hashes only a sibling `gmpy2.cpython-312-darwin.so`.  The imported object is the unpinned package wrapper `gmpy2/__init__.py`; its bundled dependent libraries are also not descriptor-pinned.  A synthetic wrapper with the authentic sibling extension passed every version/hash check and changed a certified transcendental result. | Arithmetic decisions can be changed while `verify_mpfr_runtime()` reports PASS. |
| R78-P1-1 | P1 | `select_saved_controls_bytes`, `compute_role_radii_bytes`, and the odd-gate calls verify only v5, v4, Round 73, and sometimes the sibling extension.  They do not snapshot or bind the substantive source, shim, tests, lock, either protocol, Round 75, this independent audit, or a future external T0 attestation; selector output records only the three normative-document hashes. | Even after import repair, future T1 has no implemented package-identity consumption contract. |
| R78-P1-2 | P1 | `exp_up64(-1e20)` returns HOLD although the exact result is positive and below the minimum subnormal, so the unique finite upper endpoint is exactly `0x0.0000000000001p-1022`.  The fixed MPFR exponent range underflows before endpoint certification. | The claimed exact valid-domain `exp` vocabulary is incomplete; a valid finite input can receive operational HOLD rather than its defined endpoint. |
| R78-P2-1 | P2 | The node parser requires every adjacent saved acceptance index to differ numerically by one.  V5 specifies the immediately preceding/succeeding elements of the saved ordered array but does not print this integer-consecutivity equation. | A valid sparse-ID saved array can receive an extra false HOLD unless the design is clarified. |
| R78-P2-2 | P2 | The T0 protocol says the package freezes Sections 3--6, but Section 6 is exposed only as bare in-memory scalar/vector functions.  No canonical byte object binds `O113/O129/O161` roles, topology equality, or complete promoted-diagnostic coverage. | The primitive is correct, but it is not yet the complete production Section-6 enforcement claimed by the protocol. |
| R78-P2-3 | P2 | Round 75's broad `rg` command did read and display a few producer-source symbol lines. | This is a disclosed procedural scope deviation, not evidence of scientific-value/result exposure; absolute “producer not inspected/read” wording is inadmissible. |

R78-P0-1 and R78-P1-1 are related but not duplicates: the first is a live
code-substitution exploit; the second is the missing downstream package-byte
attestation even if the import is repaired.

## 4. P0-1 reproduction: authentic shim, arbitrary implementation

The frozen v5 file contains only

```python
from positive_b_stage_b_t0_selector import *
from positive_b_stage_b_t0_selector import __all__ as _T0_ALL
```

It neither uses a package-relative import nor checks the imported module path
or bytes.  The independent fixture created only this temporary synthetic
module earlier on `PYTHONPATH`:

```python
__all__ = ["select_saved_controls_bytes"]
def select_saved_controls_bytes(_payload):
    return b"synthetic-forged-output"
```

Then a fresh interpreter imported the authentic
`positive_b_stage_b_t1_selector_v5.py`.  It exited successfully and returned

```text
synthetic-forged-output
```

No design hash, authorization literal, JSON schema, selector rule, or package
hash was consulted.  Pre-populating `sys.modules` provides the same class of
bypass.  This is not a hypothetical source drift: it succeeds against the
exact frozen shim hash in Sec. 1.

The Round-75 assertion

```python
frozen_name.select_saved_controls_bytes is selector.select_saved_controls_bytes
```

only proves identity after both names have already resolved in one clean
interpreter.  It does not bind either resolution to repository bytes.

## 5. P0-2 reproduction: verified extension, unverified executable wrapper

In the frozen environment, `gmpy2.__file__` names
`gmpy2/__init__.py`, not the native extension whose hash is checked.
`verify_mpfr_runtime()` takes the parent of that unverified path and hashes a
sibling named `gmpy2.cpython-312-darwin.so`; it never proves that the imported
namespace came from or remained identical to the wheel bytes.

The independent fixture made a temporary synthetic `gmpy2` package, copied
the authentic pinned extension and its runtime libraries without changing
their bytes, imported every authentic extension symbol, and overrode only
`exp`:

```python
from .gmpy2 import *
def exp(x):
    return mpfr(1)
```

With that directory first on `PYTHONPATH`, the authentic substantive selector
reported

```text
verified extension SHA-256
  9586b7c4b887704b57576f52b73a8c45437946d2b172095d82c20fa0871a415b

expRN(1)
  0x1.0000000000000p+0
```

instead of the frozen correct value
`0x1.5bf0a8b145769p+1`.  All runtime version functions still came from the
authentic extension, so version comparison did not detect the wrapper.

The exact rational postcheck makes `sqrtRN` harder to corrupt silently, but
that does not close this finding.  The unpinned wrapper executes arbitrary
Python at import time, and the package explicitly exports `log` and `exp` as
certified operations.  The requirements lock pins a wheel download hash only;
the current public calls neither read that lock nor verify the installed
wrapper/dependent-library bytes against the wheel.

## 6. Authentic-module arithmetic audit

### 6.1 Exact algebraic operation order: PASS

Under a direct authentic import:

- every binary64 algebraic leaf becomes `Fraction.from_float`;
- multiply, add, subtract, and divide each have a separate RN conversion;
- `dot2RN` is multiply, multiply, add in the printed coordinate order;
- `norm2RN` is square, square, add, then certified square root;
- no FMA, `hypot`, compensated sum, reassociation, or host-libm
  transcendental decides these primitives; and
- nonfinite/overflowed binary64 intermediates HOLD.

The fixed FMA-sensitive fixture retained the declared one-bit distinction.
Minimum-subnormal multiplication and dot products retained the subnormal;
maximum-by-maximum multiplication held rather than emitting infinity.

### 6.2 Directed rational endpoints and odd half-ulp gate: PASS

The rational `down64`/`up64` definitions correctly enclose positive and
negative half-minimum-subnormal inputs, canonicalize zero only after direction
selection, and handle ties to even.  `Dplus` and `Dminus` evaluate exact
rational endpoint differences rather than native RN subtraction.

The implementation rejects both:

- the Round-70 `0.300,0.300,0.304` jump; and
- the Round-73 half-ulp fixture for which native RN reports `ODD_FLOOR` but
  exact outward rounding reports `nextUp(ODD_FLOOR)`.

Both-at-floor and strict certified-contraction controls pass, and one bad
vector coordinate is not hidden by the infinity-norm aggregation.

### 6.3 MPFR contexts and ordinary-range endpoints: PASS, scoped

For the authentic installed wrapper, local contexts explicitly freeze
rounding, precision, exponent limits, traps, subnormal policy, complex policy,
rational-division policy, and GIL release.  Caller-global precision/rounding
mutation did not change ordinary `sqrt(2)`, `log(2)`, or `exp(1)` results.
Square-root candidates receive exact rational square and midpoint/tie checks.

This scoped numerical PASS does not cure R78-P0-2 because those context and
function objects come from the unpinned wrapper.  It also does not cure
R78-P1-2 at extreme negative exponential inputs.

### 6.4 Extreme exponential underflow: incomplete

For \(x=-10^{20}\), positivity gives \(e^x>0\), while
\(e^x<2^{-1075}\); therefore

```text
exp_down64(x) = +0
exp_rn(x)     = +0
exp_up64(x)   = minimum positive binary64 subnormal.
```

The first two current calls return zero, but `exp_up64` exhausts its fixed
precision list and returns HOLD.  This is fail-closed, so it is not a P0 false
GO.  It is nevertheless outside the v5 exact endpoint definition for a valid
finite input.

## 7. Authentic-module selector audit

### 7.1 Source join and schema: PASS

The byte entry point enforces canonical ASCII JSON, rejects duplicate keys,
JSON floats/nonfinite constants, alternate float-hex spellings, signed zero,
whitespace, missing/extra fields, bool-as-index, and uint64 overflow.  It
requires one exact index set across generation, mesh 65, and mesh 97;
byte-identical theta/weights; `EVALUATED`; exact boolean all-gates PASS; and
identical saved topology/count.  Distinct indices with identical control bytes
HOLD.

### 7.2 Comparison record, frame, and orientation: PASS

The authentic implementation follows the printed trace:

- exact `TARGET` byte filtering;
- RN offset error, absolute residual, unsigned acceptance-index rank;
- one unique comparison node with predecessor and successor;
- central `theta_n-theta_p`, `t_n-t_p`, integer `sigma`, and zero-omega HOLD;
- negative-omega secant flip before normalization;
- multiply/multiply/add/sqrt norm, fixed rotation, and exact two local `ell`
  operands; and
- displacement from comparison node `b`, never another base.

Reversed/one-sided secants, omitted orientation flip, zero omega, wrong bases,
and the one-ulp `ell` mutation behaved as required.

### 7.3 Pair enumeration, rank, and no fallback: PASS

Side labels come only from computed `s`; all eligible distinct-index
opposite-side pairs with a one-count difference are enumerated.  The five
rank fields use the printed RN order.  Duplicate full ranks HOLD.  Each branch
selects its first rank independently, after which a cross-branch collision
HOLDs even when an eligible later pair exists.  The unordered count-pair set
must be exactly `{(1,2),(2,3)}`.

No selector-math bypass was found under the authentic module.

### 7.4 Sparse acceptance-index ambiguity: false-HOLD risk

The source additionally requires

```python
right_acceptance_index == left_acceptance_index + 1
```

for every adjacent array element.  A synthetic ordered array with IDs
`10,20,30`, the comparison record pointing to `20`, and valid immediate array
neighbors is rejected.  V5 prints “immediately preceding and succeeding saved
nodes” in the ordered array but no `+1` equation.  Either the design must add
this literal requirement result-blind, or the implementation must remove it.

## 8. Role radii, descriptors, and Section-6 boundary

### 8.1 Role radii: PASS under authentic source

For seven unique ascending role IDs, the source downward-evaluates all four
boundary components, every three-coordinate pair separation, and the final
minimum of `RHO_CAP`, `b/4`, and `s/4`.  It rejects nonpositive or nonfinite
values, then independently outward-checks all six global-box faces and all 21
pairwise strict separation inequalities.  One-ulp face/pair-touch fixtures
fail.

### 8.2 Snapshot helper: PASS for the files it actually checks

`snapshot_regular_file` rejects final and tested component symlinks, opens the
final path with `O_NOFOLLOW`, uses one regular-file descriptor, enforces a byte
cap, compares pre/post descriptor identity, compares the post-read lexical
inode, and hashes the read bytes.  Descriptor replace/restore tests HOLD.

This is not a package provenance PASS: the helper is never applied to most of
the package bytes, and both Python modules/dependencies have already executed
before the checks relevant to them.

### 8.3 Section 6: numerical primitive PASS, complete enforcement absent

The scalar/vector odd Boolean is correct.  Its API accepts three anonymous
Python interval objects; it has no canonical schema containing grid role,
topology, diagnostic identity, or coverage inventory.  Therefore it cannot by
itself enforce the rest of v5 Section 6.  The future result-blind compiler may
add that object-level layer, but the current protocol must not describe this
package alone as freezing all of Section 6.

## 9. Package-byte and no-cycle audit

### 9.1 What is currently bound

The substantive selector's public byte calls verify only:

```text
v5 design
v4 design
Round-73 design acceptance
```

and selector/MPFR paths additionally hash the named sibling extension.  A
recording descriptor test confirmed that none of the following is opened by a
high-level selector call:

```text
substantive implementation
v5 filename shim
package tests
dependency lock
substantive protocol
v5 protocol bridge.
```

The selector output repeats only the v5/v4/Round-73 hashes.

### 9.2 Documentary graph: no cycle found, executable consumption missing

The T0 protocol lists implementation/shim/test/lock hashes; the v5 protocol
bridge then pins the T0 protocol; Round 75 records both.  None contains a
self-hash, and a future external record is intended to pin the independent
audit.  That documentary direction is acyclic.

However, the external record does not yet exist and no frozen future-T1
loader consumes it before resolving imports.  Hashes written in Markdown do
not constrain Python's module resolution.  Thus the no-cycle graph is
conceptually sound but not executable provenance.

## 10. Round-75 broad-search disclosure

The disclosed command searched `code notes audits` and displayed a few
matching producer-source symbol lines.  This technically violates an absolute
claim that no producer source was read or inspected.  It did not display a
canonical/hidden Stage-A object, candidate/control value, mesh result,
scientific numerical output, manifest, or result/evidence object.  No evidence
shows that package choices were adapted to a scientific value; the choices
are reconstructible from v5/Round 73 and synthetic fixtures.

Independent classification:

```text
process class = P2 disclosed source-symbol exposure
scientific-value/result contamination = NOT ESTABLISHED
rebuild solely for this observation = NOT REQUIRED
absolute producer-noninspection wording = FORBIDDEN
```

Because R78-P0-1 and R78-P0-2 already require a clean result-blind package
repair, the repair round should avoid broad repository searches and retain
this historical disclosure rather than erase it.

## 11. Executed synthetic evidence

All commands used the report-owned Python environment and only the allowed
package/design tests.

```text
pytest -q \
  code/test_stageb_v5_design_round73.py \
  code/test_positive_b_stage_b_t1_selector_v5.py \
  code/test_stageb_t0_selector_round78.py

47 passed
```

The count consists of 10 Round-73 design tests, 29 Round-75 package tests, and
8 new independent package attacks.  A passing Round-78 exploit test means the
vulnerability was successfully reproduced; it is not package acceptance.

```text
ruff check implementation + shim + Round-75 tests + Round-78 tests
  PASS

py_compile implementation + shim + Round-75 tests + Round-78 tests
  PASS
```

Direct synthetic reproductions also returned:

```text
authentic shim + earlier fake substantive module
  return code 0
  synthetic-forged-output

authentic substantive module + fake wrapper + authentic extension bytes
  verify_mpfr_runtime: PASS
  expRN(1): 0x1.0000000000000p+0  [incorrect]

extreme exp directed endpoint
  expDown(-1e20): +0
  expRN(-1e20):   +0
  expUp(-1e20):   HOLD             [should be minsub]
```

No scientific producer or object was involved in any command.

## 12. Required repair before another independent audit

1. **Make the exact v5-frozen source substantive.**  Put the full implementation
   in `positive_b_stage_b_t1_selector_v5.py`, or amend the result-blind design
   to an exact package-relative layout with a descriptor-verified loader.  An
   unqualified same-name import is forbidden.
2. **Test import substitution.**  Add clean subprocess tests for earlier
   `PYTHONPATH`, pre-populated `sys.modules`, wrong module `__file__`, and a
   changed auxiliary source.  Every case must HOLD before processing payload
   bytes.
3. **Freeze the actual MPFR execution tree.**  At minimum bind and verify the
   imported `gmpy2/__init__.py`, native extension, and every loaded bundled
   GMP/MPFR/MPC library, or execute from a complete installed tree verified
   against the pinned wheel/RECORD in an isolated interpreter.  Hashing an
   unused sibling is insufficient.
4. **Sanitize resolution before import.**  Use an isolated interpreter/path
   policy and verify package files before loading executable wrapper code.
   Checking `__file__` only after arbitrary wrapper code ran is not enough for
   the stated freeze boundary.
5. **Create one acyclic T0 package inventory/attestation.**  It must bind v5,
   v4, Round 73, substantive source, any shim/loader, tests, dependency lock,
   both protocols, the repair audit, and the next independent audit/external
   record in the already declared forward direction.  Future T1 must verify
   this record before import and copy its hash into the T1 object/output.
6. **Fix exact exponential underflow.**  Correctly return `down=0`, `RN=0`,
   and `up=minsub` throughout the sufficiently negative finite binary64
   regime; add threshold-neighbor tests as well as `-1e20` and `-maxfloat`.
7. **Resolve sparse node IDs result-blind.**  Either print the exact `+1`
   acceptance-index invariant in a new design version and schema tests, or
   accept any unique ordered array whose chosen element has immediate array
   neighbors.
8. **Scope Section 6 honestly.**  Either add a canonical byte-level odd-grid
   object that binds grid labels, topology, diagnostic identity, scalar/vector
   shape, and complete coverage, or state that this package provides only the
   arithmetic primitive and leave full enforcement to a separately frozen
   pre-Stage-A compiler.
9. **Re-run the full synthetic matrix and a new independent package attack.**
   No Stage-A object or scientific command may be used to repair or test these
   findings.

## 13. Final decision and next permitted action

```text
P0 = 2
P1 = 2
P2 = 3

HOLD-PACKAGE
HOLD-EXECUTION
SCIENTIFIC OBJECT/VALUE/RESULT: NOT READ / NOT RUN / NOT CREATED

AUTHORIZED-SCIENTIFIC-COMMAND: NONE
```

The next permitted action is only a result-blind package/design repair that
closes R78-P0-1 through R78-P2-3, followed by a distinct independent audit of
the new exact bytes.  This report does not authorize Stage-A substitution,
mesh-65/97 evaluation, Stage-B FV or off-lattice execution, scientific
manifest/result creation, future-T1 consumption, or manuscript promotion.

