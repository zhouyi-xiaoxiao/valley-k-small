# Round 157: preimplementation attack on rate-action composition

Date: 2026-07-14

Decision: **DESIGN FORMULAS ACCEPTABLE SUBJECT TO FOUR OPEN P1 CONTROLS / NO IMPLEMENTATION ACCEPTED / HOLD F0 / NO F1 / HOLD PRR**

This is an independent, read-only **preimplementation design audit** of the
proposed `rate_defined_tensor_f0_packed_rate_action.py` stage.  It reviewed the
Round-155-accepted stage-1 and directed-action APIs and tests together with
`notes/f0_rate_interval_composition_next_stage.md`.  It did not review any
rate-action implementation because no such implementation was presented for
acceptance.  It did not run a selector, prospective control, positive budget,
F1/F2/F3 row, physical observable, Poisson propagation, topology calculation,
or the `7,165,305`-state target.

The two proposed one-step bounds are mathematically sound under their stated
preconditions.  That statement is a design judgment only.  Four concrete P1
controls below must be implemented and independently attacked before the
resulting bytes can be accepted even as a bounded method primitive.  A green
producer suite, a self-declared consistency digest, or a fresh process that
calls the same composition implementation would not close them.

## Findings

### P0

No theorem-level defect was found in the two proposed point-plus-`l1`-ball
formulas, provided that the exact target family, witnesses, centre actions, and
input-radius provenance satisfy every condition in this audit.

### P1 design risk 1: source vertices must retain diagonal coupling and global parameter reuse

An endpoint vertex is chosen on the original rate and killing sources.  For
one source state `s`, with tensor coordinate `x`, the exact row must be rebuilt
as

\[
 Q_{ss}=-\kappa_s-\sum_k(f_{k,x_k}+b_{k,x_k}),
\]

with the same selected rate endpoint used both in its off-diagonal entry and
in this coupled diagonal.  A rate parameter is indexed by
`(axis, direction, position)` and is reused globally by every tensor row with
that coordinate.  It may not be selected independently for each row.  Killing
is selected once per state.

Treating the diagonal interval as independent, or choosing a separate copy of
the same axis-position rate in each tensor row, changes the target operator
family.  It can make an apparently exhaustive oracle irrelevant to the actual
model and can understate an operator witness.  The independent oracle must
therefore enumerate the original source variables and construct the diagonal
from those same choices.

### P1 design risk 2: the uniformization rate is fixed across the whole source box

The exact rational `lambda` is reconstructed once from the complete source
box and kernel-build contract.  If the contract supplies no explicit rate, the
oracle must independently compute the full-box maximum exit requirement and
the least binary64 upper value.  That single exact dyadic rate is then used for
every vertex:

\[
 P=I+Q/\lambda.
\]

Selecting a new `lambda(v)` at each vertex changes the family being bounded,
invalidates comparison with the stored centre `Phat`, and can conceal an
unsafe `delta_P`.  The oracle must also reject a rate one ulp below the exact
full-box exit bound.

### P1 design risk 3: periodic axes of size two contain parallel directed edges

On a periodic axis of size two, the forward and backward moves from a source
state arrive at the same destination.  Both contributions remain distinct
source coefficients but occupy one matrix cell.  Every exact target and
centre matrix builder must therefore use `+=`; assigning the second term
overwrites a real edge and changes `Q`, `P`, their actions, and their norms.

This case also separates coefficientwise witnesses from actual matrix norms.
The stage-1 `delta_Q`, direct `delta_P`, and coefficient-rounding witness sum
the separately stored coefficient allowances.  When parallel edges combine,
the actual full-matrix norm may be strictly smaller.  The correct independent
test is

```text
actual vertex matrix norm <= saved exact witness,
```

not unconditional equality.

### P1 design risk 4: a previous public receipt is not recurrence authority

A plain dataclass receipt, public SHA-256 consistency digest, or saved launch-
capability digest can be recreated by a caller after the original launcher has
returned.  It therefore cannot by itself prove that an incoming radius was
previously accepted.  An authoritative recurrence needs one of the following
explicit authorities:

1. one fresh verifier worker retains the private state for the whole
   recurrence;
2. every step replays the complete chain from an immutable initial payload; or
3. a launcher-controlled, unforgeable capability/MAC registry authenticates
   each preceding receipt.

The method artifact may carry immutable `output_nominal_bytes` plus a manifest
and hash; it must not carry a NumPy array or view.  The receipt binds that
artifact hash.  Without an immutable output payload there is no state from
which the next worker can reconstruct the nominal vector; without one of the
three authorities above, a caller can pair arbitrary bytes with a forged
previous-radius claim.

## Formula judgment

Let the privately reconstructed input set be

\[
 x\in c+B_1(e),\qquad m=\lVert c\rVert_1,
\]

and let the nominal action return binary64 point `d`.  Let the independently
bound directed centre action return `Y=[L,U]`, with exact dyadic comparisons

\[
 L_i\le d_i\le U_i.
\]

The centre-action covering radius around `d` is the farthest-point quantity

\[
 a_* = \sup_{y\in Y}\lVert y-d\rVert_1
     = \sum_i\max(d_i-L_i,U_i-d_i).
\]

It is not `dist(d,Y)`, which is zero, and it is not a half-width, maximum
coordinate width, or per-coordinate radius later summed with an extra factor
of the state count.

For the exact target `P`, nonnegative row-substochasticity gives signed-`l1`
contraction.  The valid decomposition is

\[
 P^Tx-d=P^T(x-c)+(P-\widehat P)^Tc+(\widehat P^Tc-d),
\]

so the proposed radius is

\[
 e_P^+=e+\delta_Pm+a_*.
\]

There is no additional `delta_P e` term because the exact target `P`, rather
than the centre matrix, propagates the input ball.

For the generator,

\[
 \lVert Q^T\rVert_1\le q_{\rm hat}+\delta_Q,
 \qquad q_{\rm hat}=\lVert\widehat Q\rVert_\infty,
\]

and therefore

\[
 e_Q^+=(q_{\rm hat}+\delta_Q)e+\delta_Qm+a_*.
\]

The `qhat` witness is a maximum absolute **row** sum.  A column maximum is the
wrong induced norm for this transpose action.

The independent oracle should make two distinct checks for every exact target
and input-ball extreme.  With `z=A.T(c+b)` and `Y=[L,U]`, first check the
box-plus-ball statement

\[
 \operatorname{dist}_1(z,Y)
 =\sum_i\max(L_i-z_i,0,z_i-U_i)\le r_{\rm base},
\]

where

\[
 r_{\rm base}^P=e+\delta_Pm,
 \qquad
 r_{\rm base}^Q=(q_{\rm hat}+\delta_Q)e+\delta_Qm.
\]

Then check

\[
 \lVert z-d\rVert_1\le r_{\rm base}+a_*\le e_A^+.
\]

## Independent exact oracle construction

The test oracle must not call producer scalar helpers, stage-1 witness lookup,
the saved directed-action oracle, or a result-digest helper.  It should:

1. validate immutable byte lengths and SHA-256 values locally;
2. decode each binary64 value with `struct.unpack` and
   `Fraction.from_float`;
3. reject nonfinite, reversed, negative, or negative-zero rate/killing
   endpoints;
4. construct C-order strides locally;
5. enumerate each nondegenerate source endpoint once, preserving the global
   reuse and coupled diagonal described above;
6. construct exact target `Q` and `P` matrices with local `Fraction` code;
7. reconstruct `Qhat` and `Phat` from raw coefficient bytes, and separately
   derive their expected coefficients from source bytes and the fixed rate;
8. recompute the coefficientwise exact `delta_Q`, both `delta_P` branches,
   selected `delta_P`, `qhat`, and their flat-index witnesses without reading
   the saved witness tuple as expected data;
9. compare every exact vertex matrix norm with those witnesses; and
10. enumerate the input-ball extremes and check both containments above.

For `e>0`, the `l1` ball is the convex hull of

\[
 \{+e e_i,-e e_i:0\le i<N\};
\]

for `e=0`, the only input is `b=0`.  For fixed target parameters the action
norm is convex in `b`; for fixed `b` it is convex in the affine source
parameters.  Thus the endpoint-vertex by ball-extreme product covers the full
tiny source box and ball.

The oracle must maintain two scalar calculations:

- exact mathematical `m_*`, `a_*`, and proof radii in `Fraction`; and
- an independently coded binary64 trace using local `math.nextafter` after
  every frozen addition, subtraction, and multiplication.

The producer trace must match the local trace exactly by `float.hex`, and its
dyadic value must not be below the exact mathematical bound.

## Tiny Fraction oracle matrix

The following is the minimum heterogeneous matrix recommended for the first
implementation attack.  Degenerate endpoints are not vertex bits.

| ID | Shape and boundaries | Nondegenerate variables | Vertices | Required attack |
| --- | --- | ---: | ---: | --- |
| `Z` | `(2,)`, reflecting | 0 | 1 | `P=I`, `Q=0`, zero radius, both nominal zero signs |
| `R` | `(3,)`, reflecting | 7 | 128 | interior position, source/rate index, heterogeneous directions and killing |
| `C` | `(2,)`, periodic | 6 | 64 | parallel forward/backward edge accumulation |
| `M2` | `(2,2)`, reflecting/periodic | 10 | 1024 | C-order strides and global reuse across tensor rows |
| `M3` | `(2,2,2)`, reflecting/periodic/reflecting | 4 | 16 | all three dimensions with heterogeneous point rates elsewhere |
| `S` | `(2,)`, periodic | small selective set | small | minimum-subnormal and half-subnormal underflow, automatic-rate ceiling |

One fixed `R` source is:

```text
forward = [(1/16,3/32), (1/8,5/32), (0,0)]
backward = [(0,0), (1/32,1/16), (3/32,1/8)]
killing = [(1/64,3/128), (1/32,5/128), (0,1/128)]
lambda = 1
```

`P` point inputs must be nonnegative, non-normalized, and include zeros.  `Q`
inputs must be signed with cancellation, for example
`(-1/4,0,3/8)`.  At least one `Q` coordinate should satisfy `abs(c_i)<e`, so
the point-plus-ball set crosses zero.  The point lift itself remains exactly
`[c,c]`; the existing nondegenerate signed-interval test remains a subordinate
directed-action regression and must not be emulated by widening this lift.

For each case with enough states, use block size `1`, a positive block size
smaller than and not dividing `N`, and `99`.  Nominal bytes, directed enclosure
bytes, scalar trace, and final radius must be invariant over block size.

The fixtures must make every formula term nonzero where its omission is
attacked.  They must also ensure that the `delta_P` branches differ and that
the maximum absolute row and column sums differ; otherwise a swap or wrong-
norm mutation can pass vacuously.

## Signed-zero policy

- Rate and killing endpoints accept canonical `+0.0` only.  Either endpoint
  changed to `-0.0` is a source failure.
- Nominal `c` may contain either sign of zero.
- Both signs produce bitwise `+0.0` at both point-lift endpoints.
- The source-nominal hash preserves and distinguishes the original sign bit.
- The point-lift raw hash is identical for nominal vectors that differ only in
  zero signs, while the binding digest differs because it includes both the
  source and lift hashes.
- Input radius, witness upper values, scalar intermediates, and final radius
  use canonical `+0.0`; negative zero is rejected.
- The nominal output `d` retains the actual stage-1 raw bytes.  Its zero signs
  are not silently rewritten; the next point lift canonicalizes them again.

The present `CanonicalFloat64Vector` accepts negative zero, whereas the packed
interval payload rejects it.  A fresh verifier therefore needs an immutable
nominal-vector byte payload and manifest; the interval-payload schema cannot
be falsely presented as covering this policy.

## Fail-closed mutation matrix

Every mutation below must return a stable rate-action HOLD code.

### Target-family and norm mutations

- choose a diagonal endpoint independently of its rates and killing;
- choose one axis-position rate separately in different tensor rows;
- overwrite rather than add the second periodic size-two edge;
- change one forward/backward source index, rate index, stride, or transpose;
- accept a nonzero reflecting outward rate;
- select `lambda` separately per vertex or lower the fixed rate by one ulp;
- omit the target diagonal from `delta_Q`;
- omit coefficient rounding from the via-`Q` `delta_P` branch;
- understate, rename, duplicate, swap, or use the wrong selected witness;
- use a maximum column sum instead of a maximum absolute row sum; or
- reduce only centre coefficients while ignoring source intervals.

### Scalar and containment mutations

- compute `m` as a signed sum rather than a sum of absolute values;
- omit `e` from the `P` formula or `delta_Q e` from the `Q` formula;
- use `dist(d,Y)`, a half-width, or a single-coordinate maximum for `a`;
- add a per-coordinate ball radius and then reinterpret its sum as the `l1`
  radius;
- reassociate the frozen operation trace;
- move `d` outside `[L,U]` by one ulp; or
- lower `m`, `a`, a witness upper, any intermediate, or the final radius by
  one ulp.

### Type, binding, and zero mutations

- make one lift endpoint differ from canonicalized `c`;
- retain negative zero in the lift or accept it in a rate/killing source;
- accept signed nominal input for `P`;
- accept writable, aliased, viewed, subclassed, nonnative, or nonfinite arrays;
- mutate source, kernel, input, directed output, or nominal output after its
  first hash check;
- alter runtime, source hash, backend, summation order, operation-model hash,
  block count, formula identifier, or point-lift binding; or
- coherently recompute a public consistency digest and treat that as
  authentication.

### Memory and provenance mutations

- omit a simultaneously live raw payload, deep copy, `frombuffer` view,
  immutable output-byte copy, Pipe/pickle buffer, or serialization copy;
- use the Round-155 directed-only memory identity as the composition peak;
- expose an ndarray or view in a purported receipt;
- accept a same-process method artifact as independent replay;
- call the same producer composition helper in a fresh process while claiming
  a separate composition implementation;
- accept a caller-declared radius as authoritative;
- accept a previous artifact/receipt whose output nominal hash or output
  radius does not exactly match the current input; or
- reuse a receipt for another operator, kernel, contract, or request.

## Contract, result, and receipt fields

The composition contract must bind at least:

```text
schema, tensor_shape, state_count, block_size, block_capacity
maximum_scratch_bytes, maximum_payload_bytes
stage1_source_sha256
directed_source_sha256
composition_source_sha256
stage1_action_contract_sha256
directed_action_contract_sha256
directed_backend_binding_sha256
composition_operation_model_sha256
runtime, machine, byteorder
summation_order, scalar formula identifiers
point-lift zero policy
single_threaded=true, science_free=true
```

Kernel and witness binding must include:

```text
each source manifest and raw hash plus the aggregate kernel-input hash
kernel-build-contract hash and exact lambda numerator/denominator/float hex
kernel replay, source/derived/combined chains
array-digest set and witness-binding hash
each required witness name, numerator, denominator, upper float hex, and index
```

The internal result and method artifact must bind:

```text
operator and composition-contract hash
input nominal manifest/raw hash and input-radius provenance
point-lift raw and binding hashes
directed raw/result-consistency/action-contract hashes
nominal output raw/action-contract hashes
request, artifact-body, scalar-ledger, and memory-ledger hashes
```

The scalar ledger must save:

```text
input e, input nominal l1 upper m, centre-action upper a
delta_q, delta_p_direct, p_rounding, delta_p_via_q, delta_p_selected, qhat
P: coefficient, temporary, output
Q: q_norm, propagated, coefficient, temporary, output
exact values and/or float.hex according to their role
flat-index order and coverage
subtraction, addition, multiplication, conversion, and reduction counts
```

For authoritative input provenance, record one exact variant:

```text
INITIAL_STATE_RECEIPT:
  initial artifact/manifest hash and accepted radius

PREVIOUS_RATE_ACTION_RECEIPT:
  authenticated previous receipt/artifact hash
  previous output nominal hash == current input nominal hash
  previous output radius bits == current input radius bits

DECLARED_TEST_RADIUS:
  method-only=true, authoritative=false
```

The independent receipt contains no array and fixes:

```text
fresh_process=true
verifier_owned_reconstruction=true
separate_composition_implementation=true
producer_arrays_accepted=false
arrays_exposed=false
science_executed=false
f0_pass=false
status=PASS_RATE_ACTION_METHOD_ONLY_NOT_F0
```

## Memory identity

Let `C=min(N,block_size)`, exclude only the pre-owned kernel, and count the
source nominal as `8N`.  Before extra raw or serialization buffers, the four
minimum simultaneous-lifetime phases are:

```text
point-lift build/validate:                          24N + 2C
directed action:             40N + max(81C, 2C, 2048)
nominal action with prior outputs live:             48N + 65C
final binding/revalidation:                         48N + 2C
declared peak:                       maximum of all four phases
```

The ledger must publish every phase, not only the peak.  It also records dtype,
shape, byte count, ownership/base identity, allocation and release phase for
the source nominal, point lift, directed output, nominal output, each action
workspace, validation scratch, and runtime probe.  Any immutable raw payload,
output-byte artifact, deep copy, view, or serialization buffer is added at its
actual live length.  The payload identity is not an allocator, RSS, swap, or
largest-shape acceptance; those remain later gates.

## Acceptance boundary

```text
one-step P/Q formulas                           DESIGN-CORRECT UNDER STATED PRECONDITIONS
coupled/global endpoint oracle                  REQUIRED / NOT YET ACCEPTED
fixed full-box uniformization rate              REQUIRED / NOT YET ACCEPTED
periodic size-two parallel-edge attack          REQUIRED / NOT YET ACCEPTED
authoritative recurrence provenance             UNSPECIFIED UNTIL ONE AUTHORITY IS IMPLEMENTED
independent scalar/oracle implementation         REQUIRED
fresh separate-composition verifier             REQUIRED
rate-action source bytes                         NOT PRESENTED OR ACCEPTED BY THIS AUDIT
production uniformization, Poisson, and jets     NOT RUN
largest-shape RSS, swap, and timing              NOT RUN
F0                                               HOLD
F1 / positive-budget science                     NOT AUTHORIZED / NOT RUN
PRR release                                      HOLD
```

Round 157 therefore authorizes implementation and adversarial testing of the
bounded one-step method only.  It is not an implementation acceptance, F0
pass, scientific result, continuum result, or publication decision.
