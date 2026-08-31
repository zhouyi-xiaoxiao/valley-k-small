# Rate-defined tensor F0 candidate v1 freeze

Date frozen: 2026-07-19  
Pre-execution resource-cap repair: 2026-07-19  
Pre-execution tail-horizon repair: 2026-07-19  
Status: **PRE-EXECUTION METHOD AND TWICE-REPAIRED RESOURCE FREEZE / NO F1 AUTHORIZATION**

## 1. Scope and authority boundary

This freeze implements the minimum credible F0 required by
`manuscript_completion_contract_v1`.  F0 is science-free.  It may parse and
bind the three exact selector vertices, but it may not combine any of them
with a positive-budget production configuration.

The candidate has no public numerical, role, control, budget, root-band,
threshold, tolerance, precision, or resource-cap argument.  Output-path
selection is not scientific input.  Every numerical fixture below is an
internal literal selected before execution.

The candidate itself can report only
`PASS_F0_IMPLEMENTATION_AWAITING_INDEPENDENT_AUDIT`.  It must keep
`independent_audit_complete=false`, `f0_accepted=false`, and
`f1_authorized=false`.  A separately coded exact-byte replay, which does not
import the producer numerical modules, is the only component permitted to
write a later `PASS_F0_ACCEPTED` receipt.

## 2. Fixed semantic fixtures

### 2.1 Selector boundary

The producer reads the pinned exact-selector JSON only to:

- reconstruct the three unit-sum rational vertices from the normative
  numerator and denominator strings;
- prove that the historical `raw/S_c` and raw-hex branch is not an accepted
  v2 source; and
- retain the distinct repeated-checkpoint values
  `0.2674801474024188` and `0.2674801474024189` as adjacent binary64 values
  enclosed by one outward interval.

It performs no production killing, propagation, or topology calculation with
those controls.

### 2.2 Operator fixtures

The closed neutral fixture uses exact directed rates `1/16`, stationary masses
one, and killing `1/64`.

The closed heterogeneous two-state fixture is

```text
Q = [[-5/8, 1/2],
     [ 1/4,-3/4]],
pi = (1,2),
k  = (1/8,1/2),
p0 = (1,0).
```

It supplies the integrated operator-to-compiled-stream-to-scalar-series-to-
topology method check on the fixed window `[1/2,2]`.  It is not a physical
control.

### 2.3 Fixed analytic topology fixtures

For a root tuple `(r_1,...,r_n)`, define

```text
f'(t) = - product_i (t-r_i).
```

`f` is the zero-constant exact rational antiderivative.  The producer encloses
`f'` by adding exactly `1/10^9` on each side and keeps `f''` and `f'''`
exactly outward rounded.  At a query time `t`, each local `M_2`, `M_3`, or
`M_4` is the exact Taylor absolute-sum bound for the corresponding derivative
over `[t,t+1/4]`.

The fixed roots are:

| role family | roots |
| --- | --- |
| `lp_m1` | `(8)` |
| `lp_m2` | `(4,9,24)` |
| `lp_m3` | `(3,6,9,14,24)` |

They exercise the immutable physical `[1/2,35]` role bands without evaluating
a selector weight.  The frozen expected ledgers are:

| family | tiles | oracle calls | unique calls | maximum depth |
| --- | ---: | ---: | ---: | ---: |
| `lp_m1` | 146 | 350 | 147 | 4 |
| `lp_m2` | 162 | 498 | 168 | 4 |
| `lp_m3` | 178 | 646 | 188 | 4 |

The union contains exactly 211 unique times.  Every root must have twelve
serialized interval-Newton steps, a strict interior inclusion, the prescribed
curvature type, and final width at most `1/20`.

The legacy topology engine may be called only behind a private exact-type,
zero-argument fixture adapter.  No caller-supplied oracle or legacy
science-free Boolean is an authority.  The producer immediately converts the
result to explicit built-in fields.  The independent replay reconstructs all
tile, intersection, sign, cluster, Newton, role, and coverage semantics from
those fields.

## 3. Twelve control-free configuration constructors

The producer binds
`physical_configuration_family_control_free_v1.json` and constructs the
twelve axis triples in the exact order frozen by the completion contract.  It
records their shapes, state counts, reflecting or periodic semantics,
half-boundary-volume flags, and exact periodic shifts.

This step builds axes only.  It does not allocate a production killing vector
and does not evaluate a control.

## 4. Frozen largest-shape resource execution

The resource fixture has the actual largest tensor shape and production
boundary pattern:

```text
shape       = (207,215,161)
states      = 7,165,305
periodic    = (false,false,true)
P           = identity
killing     = 1/64 at every state
initial     = unit mass at flat index zero
```

The identity kernel is synthetic and control-free, while the dimensions,
indexing loops, reductions, output arrays, and action count exercise the
actual largest-shape compiled schedule.

The exact resource constants are:

```text
uniformization rate        = 256
series horizon             = 100
Poisson tail tolerance     = 1/10^18
MPFR precision             = 192 bits
maximum Poisson terms      = 200,000
reduction block size       = 65,536
expected Poisson mode      = 25,600
expected right index       = 27,014
expected maximum power     = 27,018
maximum topology queries   = 512
mandatory tail times       = (35,50,75,100)
maximum distinct queries   = 515
maximum wall time          = 3,600 seconds
maximum RSS                = 4,294,967,296 bytes
maximum peak footprint     = 8,589,934,592 bytes
maximum process swaps      = 0
maximum state-radius upper = 1/100,000,000
```

The rate is not fitted to an output.  From the control-free `MR+F` physical
axes, the independently formed maximum free exit upper is exactly

```text
1084406336125260381 / 4503599627370496
  = 240.78657648313416... < 256.
```

The resource process must execute one compiled power stream through power
27,018.  It then evaluates a fixed batch of 512 unique exact topology-window
times that contains every analytic and integrated topology-query time and
deterministic padding to the declared maximum.  It separately evaluates the
mandatory direct-from-initial tail checkpoints at `35,50,75,100`; because 35
is already in the topology batch, the combined union contains at most 515
times.  Reevaluation may use the retained canonical scalar records but must
perform zero additional full-state `P` actions.

The process records wall time, `ru_maxrss`, peak memory footprint where the
host exposes it, `ru_nswap` before and after, compiler/build receipt hashes,
scalar-series bytes, evaluation bytes, and the final-state/mass/killing stream
hashes.  Pre-existing host-wide swap usage is diagnostic only because
unrelated processes share it; the fail-closed no-swap gate is zero process
`ru_nswap` increase.  Any cap violation yields
`HOLD_F0_METHOD_OR_RESOURCE`; it cannot reduce the action count, time count,
shape, precision, or tolerance.

### 4.1 Pre-execution resource-cap repair

Before the formal largest-shape execution and before any F0 acceptance, a
science-free two-state preflight constructed the complete 9,807-record scalar
series at the frozen rate, horizon, tail, and precision, then reevaluated the
full 512-time batch.  It returned:

```text
maximum power             = 9,806
series construction       = 1.7453 seconds
512-time reevaluation     = 35.1893 seconds
process ru_maxrss         = 3,059,712,000 bytes
host peak footprint       = 6,179,836,608 bytes
process swaps             = 0
```

This exposed that the initial 1.5-GiB draft cap counted the scalar records but
underestimated the simultaneously live MPFR evaluation states.  No control,
production killing, scientific row, or prospective topology value was
evaluated.  The cap was therefore repaired pre-execution to 4 GiB RSS and
8 GiB host peak footprint, with the time, action, query, precision, tail, and
zero-swap requirements unchanged.  This repair is part of the frozen F0
method specification and is not available after F0 acceptance.

### 4.2 Pre-execution tail-horizon repair

A read-only F1 implementation map then found that the 35-time draft resource
series covered the complete topology window but not the already frozen
event-basin and survival rules.  Those rules require direct-from-initial
absolute-time evaluations at `35,50,75,100`, with final event mass defined
using `S(100)`.  A 35-time resource gate therefore did not exercise the
complete downstream schedule.

Before a production resource run, F0 acceptance, F1 manifest, or scientific
row existed, the same fixed rate and tolerance were replanned at horizon 100:

```text
Poisson mean             = 25,600
Poisson mode             = 25,600
right index              = 27,014
maximum power            = 27,018
right-tail planning steps = 1,415
```

The formal resource run is repaired to this horizon and to the mandatory
tail checkpoints.  The wall cap is correspondingly 3,600 seconds.  Shape,
rate, tail tolerance, precision, term cap, memory caps, and zero-swap
requirement are unchanged.  The earlier 35-time preflight remains only a
memory calibration for the 512 simultaneous MPFR evaluation states; it is
not the formal resource result.

## 5. Canonical replicas and independent replay

After the measured resource receipt exists, two clean `python -I` processes
must construct byte-identical canonical candidate JSON.  The JSON parser and
replay reject duplicate keys, non-ASCII payloads, nonfinite values, signed
zero where forbidden, unknown fields, wrong exact types, source drift,
reordered controls/configurations/roles, narrowed intervals, missing Newton
steps, altered resource constants, and every false claim promotion.

The independent replay must, without importing the producer numerical
modules:

- reconstruct the neutral and heterogeneous dense generators from literals;
- replay detailed balance, sub-Markov rows, derived diagonals, and exact
  scalar powers;
- independently check compiled scalar enclosures and high-precision
  absolute-time jets;
- recompute the fixed polynomial jets and all topology certificates;
- reconstruct the twelve configuration/alignment rows from immutable JSON;
- verify the complete resource series for the fixed identity kernel;
- verify both clean replica hashes; and
- bind the exact producer, test, resource, candidate, and replay bytes.

Only a zero-finding exact-byte audit of that replay may create the F1
authorization receipt.
