# Round 125: independent black-box attack on the rate-defined tensor F0 core

Date: 2026-07-14  
Reviewer: independent science-blind attacker; not the core implementer  
Decision: **REJECT / HOLD-F0-REPAIR / NO F1 AUTHORIZATION**  
Open findings: **P0 = 1, P1 = 1, P2 = 0**

## 1. Scope and result boundary

This audit inspected and executed only the science-free rate-defined tensor
core, its tests, and neutral/control-blind benchmarks.  It did **not** read a
prospective selector weight, construct a positive-control killing field,
propagate a positive-budget primary row, inspect an F1 observable, or authorize
an F1 command.

The positive result is narrow but real: the current constructors, exact rate
ledgers, matrix-free action, directed geometry, and synthetic full-window
topology algorithm passed their unmutated method tests.  That result is not an
independent F0 acceptance because two public `audit_*` paths accept forged
saved objects.  The P0 alone requires new core bytes and a fresh independent
attack before any F1 execution.

## 2. Frozen pre-repair bytes

| object | independently recomputed SHA-256 |
|---|---|
| `code/rate_defined_tensor_f0.py` | `98ae6d219359ad676243786f03441e30d32891847da4bf0fde263af2e084b007` |
| `code/test_rate_defined_tensor_f0.py` | `0e454e4fbb81765f46673bb47f009830163332f200a5885d505c36bfcc4b9122` |
| `code/benchmark_rate_defined_tensor_f0.py` | `15e264826c1e77c2f62e1290f28dd981f62bfcb2b03625cc603fffe8afd485d4` |
| `code/benchmark_physical_geometry_f0.py` | `b19a0bfe21d3a2e8a43fbc615255e24af6076016a50210ad3b86fece0d38d988` |
| `code/verified_uniformization_enclosure.py` | `a4646f946b891133c972f62cd36a1cb177516793050c2b6e520cffceb57782ed` |
| `code/test_verified_uniformization_enclosure.py` | `6b842112f71bf88d8447a88ccba21ef1d9cbe89676912e80789e7ce964acbe34` |
| `code/test_rate_defined_tensor_f0_round125_adversarial.py` | `82796761350874413d1369997209047fe10cc9d62624d06d8f891595efce80d9` |

The last hash is the first Round-125 test byte after its local adjacent-grid
test typo was corrected and before any core repair.  Any core change invalidates
this acceptance attempt and requires a re-run against the new hashes.

## 3. Baseline and independent positive checks

Executed from `research/reports/encounter_multimodal_prr/code` with the pinned
repository virtual environment:

```text
python -m pytest -q test_rate_defined_tensor_f0.py
  23/23 PASS

python -m pytest -q test_verified_uniformization_enclosure.py
  12/12 PASS

ruff check rate_defined_tensor_f0.py test_rate_defined_tensor_f0.py \
  benchmark_rate_defined_tensor_f0.py benchmark_physical_geometry_f0.py \
  test_rate_defined_tensor_f0_round125_adversarial.py
  PASS

python -m pytest -q test_rate_defined_tensor_f0_round125_adversarial.py \
  -k 'delta_p or disk_geometry or alignment_geometry'
  3/3 PASS
```

The independent passing probes covered:

1. 24 seeded periodic rate boxes, every exact endpoint corner of every row,
   and both independent `delta_P` branches;
2. a 100-rectangle rational partition of a disk, reflection symmetry, and a
   256-bit directed-MPFR enclosure of the total disk area; and
3. two independent 192-bit builds of the `A_MRY` control-blind alignment
   geometry, which were dataclass-equal down to all binary64 interval
   endpoints and exact rational metadata.

## 4. Independent derivation of the `delta_P = min(...)` rule

Let the admissible target generator be `Q`, let the rate-derived centre be
`Qhat`, and let

```text
P       = I + Q/lambda,
Ptilde  = I + Qhat/lambda,
Phat    = stored downward-binary64 coefficients.
```

For row `i`, the direct constructor encloses each component of `P_i` and sums
the maximum distance of that component interval from `Phat_i`.  Every
correlated physical row lies in this Cartesian hull, so

```text
||P_i - Phat_i||_1 <= D_i,
delta_P_direct = max_i D_i.
```

Independently, the triangle inequality gives

```text
||P_i - Phat_i||_1
 <= ||Q_i-Qhat_i||_1/lambda + ||Ptilde_i-Phat_i||_1
 <= delta_Q/lambda + rho_round
 = delta_P_via_Q.
```

Both quantities are therefore upper bounds on the same induced norm.  Their
minimum remains an upper bound.  The independent exact-corner probe used
`Fraction` target rows and exact dyadic interpretations of every stored
binary64 coefficient; all corners lay below **both** branches in all 24
adversarial boxes.

The independent neutral `33^3` run additionally returned

```text
delta_P_direct =
  35309024162450437288525415030315 /
  96593982970800325605834980147417990360196972544
                ~= 3.655406172983270e-16

delta_P_via_Q =
  36725045165323460221507481869867 /
  96593982970800325605834980147417990360196972544
                ~= 3.802001329257246e-16

direct < via_Q; gap ~= 1.465951562739758e-17.
```

Thus the `min` choice and the observed `n33` branch ordering are not findings.

## 5. Exact construction, geometry, determinism, and workload evidence

### 5.1 Twelve control-blind physical geometries

I independently executed:

```text
python benchmark_physical_geometry_f0.py \
  --science-free-control-blind --panels-per-unit 16384 --precision-bits 192
```

The independent process completed in `real 52.68 s` (`payload total_seconds =
51.1210 s`) and returned:

```text
status                              PASS_F0_CONTROL_BLIND_GEOMETRY_METHOD_ONLY
configuration_count                 12
configuration_order                 exact frozen v2 order
one_control_base_state_workload     34787462
prospective_control_values_read     false
positive_budget_primary_evaluated   false
```

All 12 disk-area oracles were contained.  Across the 12 rows, the largest
observed support-mass interval width was about `4.482e-13`, the largest initial
marginal width about `4.482e-13`, and the contact-area widths ranged from about
`4.96e-16` to `6.96e-16`.  Shapes and state products matched each frozen row,
including the `7,165,305`-state `MR+F` row and the vertex/periodic half-cell
alignment rows.

The separately saved root-run artifact is

```text
/private/tmp/f0_physical_geometry_12.json
SHA-256 5d4de445b3f21444f44e6123f04b70c67259b3b9d1529e1ba8c2aa63c6d8b1b6
```

Its deterministic scientific fields agree with the independent run; elapsed
seconds are intentionally not byte-deterministic.

### 5.2 Directed geometry and SG checks

The compact-bump fourth-derivative triangle was independently rederived as

```text
24 t^3 + 300 t^4 + 672 t^5 + 624 t^6
       + 192 t^7 + 16 t^8,  t >= 1,
```

before the factor `exp(-t)`.  The same exact 40-term positive exponential
lower sums give `321990.4299... < 322000`, so the frozen Simpson bound is not an
unsupported numerical constant.  The independent disk partition and
reflection probe passed at 256 bits.  Original tests also checked SG
detailed-balance overlap, exact half boundary volumes, periodic half shifts,
and shifted overlap recomputation.

### 5.3 Matrix-free determinism and neutral resource diagnostic

The neutral `33^3` benchmark produced a bitwise deterministic tensor action
for a fixed input and an L1 distance of `1.2942e-16` from the explicit CSR
oracle after 20 actions.  It reported `865,656` tensor numeric bytes versus
`3,136,324` explicit-CSR bytes.  The smaller neutral benchmark similarly
returned an L1 distance of `8.2874e-17`.

These are method diagnostics, not a production resource certificate.  The
12-row benchmark never expands the full tensor initial law, killing tuple, or
kernel and never performs a physical propagation.  A naive CPython
`sys.getsizeof` decomposition for one newly created `OutwardInterval` plus its
instance dictionary, two distinct floats, and tuple reference was 368 bytes;
linear extrapolation is roughly 2.46 GiB for one `7,165,305`-entry interval
tuple.  Initial and killing tuples may coexist before other arrays.  This is a
warning estimate rather than an allocator measurement, but it confirms that
the largest full expansion and absolute-time topology workload remain
unmeasured.  Full production and science therefore remain on HOLD even after
the verifier defects below are repaired.

## 6. [P0] Saved propagation audit accepts a fabricated state and zero error

### Reproducer

The independent test constructs a three-state neutral chain and a valid
direct-from-initial propagation at `t=1/2`.  It then changes only the returned
object:

```text
nominal                       -> all zeros
l1_error                      -> 0
each poisson_tail_upper       -> 0
each propagated_power_error   -> 0
each weight_error             -> 0
each accumulation_roundoff    -> 0
each output_l1_error          -> 0
```

The unmodified saved state has mass about `0.9950124792`; the forged state has
mass zero.  Nevertheless,

```text
audit_matrix_free_propagation(kernel, initial, forged)
```

returns normally.  The Round-125 fail-closed regression therefore reports
`DID NOT RAISE`.

### Cause and severity

The audit checks shapes, signs, a few metadata equalities, and the equality of
the final self-reported error to the last self-reported chunk error.  It does
not replay Poisson weights, matrix-free powers, state accumulation, tail
bounds, or the error recurrence.  The forged fields are mutually
self-consistent but numerically false.  `enclose_matrix_free_jets` also does
not invoke a strong propagation replay before consuming the state and radius.

This is P0 if `audit_matrix_free_propagation` is used as its documented
saved-object verifier: an understated radius and arbitrary state can enter all
subsequent jet and topology claims.  The same-process producer path still
passed its dense-oracle fixture; this finding attacks verification, not the
unmutated small-chain propagation formula.

### Required closure

A repair must do one of the following and state the boundary explicitly:

1. independently replay the complete propagation from pinned kernel, initial
   law, time, Poisson parameters, and canonical runtime, then compare every
   state/error field; or
2. remove saved-verifier authority from this function and require a separate
   independent canonical verifier that performs that replay before jets or a
   scientific artifact can be accepted.

Checking more self-reported scalar fields is not sufficient.  Initial-state
provenance and the exact producer bytes must also be bound.

## 7. [P1] Saved topology audit does not bind extrema semantics

The unmodified synthetic three-root certificate has alternating
`maximum/minimum/maximum` roots and passes.  Two independent one-field
mutations also pass the saved audit:

```text
certificate.initial_derivative_sign = 0
first_root.kind = "minimum"    # curvature trace still certifies a maximum
```

Changing the first root's role string was also accepted.  In contrast,
changing its required curvature sign was caught by the Newton-chain replay.
The arithmetic trace is therefore checked, but the user-facing extrema
semantics are not bound to it.

The repair must at minimum require an initial sign in `{-1,+1}`, bind each
`kind` to its required curvature sign, replay the alternating complement sign
sequence, and bind the ordered role/band specification through an external
immutable input or digest.  Candidate-component curvature must be associated
with the corresponding root.  A saved scientific certificate additionally
needs fresh oracle replay or a separately pinned canonical verifier; coherent
mutation of self-reported tile intervals cannot be authenticated by local
arithmetic alone.

## 8. Adversarial test outcome and final gate

Full independent file:

```text
python -m pytest -q test_rate_defined_tensor_f0_round125_adversarial.py

3 PASS
3 FAIL as fail-closed regressions:
  1 x forged saved propagation accepted       [P0]
  1 x invalid initial topology sign accepted  [P1]
  1 x kind/curvature mismatch accepted         [P1 reproducer]
```

Final ledger:

```text
rate-defined construction and delta ledgers        METHOD EVIDENCE PASS
12 control-blind geometries                        METHOD EVIDENCE PASS
directed MPFR/Simpson geometry diagnostics         METHOD EVIDENCE PASS
saved propagation verification                     P0 OPEN
saved topology semantic verification               P1 OPEN
largest full kernel/propagation/topology resource  UNRUN / HOLD
positive-control or F1 execution                    NOT AUTHORIZED
independent F0 acceptance                           REJECT / HOLD-REPAIR
```

No result in this report is an F1 manifest, a continuum certificate, or a
scientific modality result.  New core bytes must make all Round-125 regressions
fail closed, pass the original suites and resource diagnostics, and then be
attacked by a different independent reviewer before F1 can begin.
