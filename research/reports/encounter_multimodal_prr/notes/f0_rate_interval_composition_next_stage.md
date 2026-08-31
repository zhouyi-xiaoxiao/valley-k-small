# F0 rate-interval composition after the directed centre action

Date: 2026-07-14  
Status: **DESIGN ONLY / ROUND-155 PRECONDITION CLEARED / HOLD F0**  
Scope: science-free operator enclosure only.  This note does not authorize a
production propagation, a scientific row, or any release-gate change.

## 1. Completed precondition and remaining boundary

Round 152 found that the first stage-1 canonical interval validator passed a
strided Boolean output column to `numpy.signbit`.  Under the pinned NumPy 2.5.1
runtime, that stride-2 `out` path corrupted zero-sign flags for blocks of at
least 16 entries, so the Round-150 bytes were correctly rejected.

Round 154 replaced every affected validation path by contiguous owned Boolean
scratch, bound the repaired stage-1 hash into the directed-action contract,
added vectorized signed-zero/runtime probes, and saved exact heterogeneous
off-diagonal-rate and heterogeneous-killing oracles.  Round 155 independently
replayed blocks `1,...,99`, 320 heterogeneous exact rows, mutation attacks, and
the combined test surface on the exact repaired bytes.  It found no new P0/P1
and accepts those bytes **only as a bounded implementation primitive**.

Those four preconditions now unblock implementation of the rate-composition
module proposed here.  They do not authorize F0, a production propagation, a
scientific row, or any interpretation of the public consistency digest as
authentication or as a fresh verifier.  The new module and every later stage
still require their own independent acceptance.

## 2. What must be composed

Let the exact rate-defined target operators be `Q` and

\[
  P=I+Q/\lambda,
\]

and let the stored binary64 centre operators be `Qhat` and `Phat`.  Stage 1
provides exact-rational witnesses

\[
 \delta_Q\ge \|(Q-\widehat Q)^T\|_1,
 \qquad
 \delta_P\ge \|(P-\widehat P)^T\|_1.
\]

The selected `delta_P` must be the stage-1 witness
`delta_p_selected = min(delta_p_direct, delta_p_via_q)`, after the complete
witness ledger has been recomputed from the privately owned source and kernel
bytes.  It must never be supplied by a caller.

The directed-action stage encloses the exact-real action of the stored centre
coefficients.  For a point input `c`, it returns a componentwise box

\[
  \widehat A^T c\in [L,U], \qquad A\in\{P,Q\},
\]

where every stored endpoint and coefficient is interpreted as its exact
binary64 dyadic value.  This box does **not** include the rate-interval
uncertainty measured by `delta_P` or `delta_Q`.

The composition must retain an induced-`l1` error, not add the same operator
radius to every coordinate and then sum it.  The latter introduces a false
factor equal to the state count.

## 3. Smallest next module

With the validator repair independently accepted on the Round-154 hashes, add
one separate module, provisionally

```text
code/rate_defined_tensor_f0_packed_rate_action.py
```

with one responsibility: map a privately owned point-plus-ball enclosure

\[
  x\in c+B_1(e)
\]

to a new point-plus-ball enclosure of `P.T x` or `Q.T x`.  It must not generate
Poisson weights, choose chunks, propagate a time horizon, form observables, or
evaluate topology.

The minimal **worker-internal** operations should be conceptually

```text
_rate_defined_p_transpose(private_kernel, private_state, contracts)
    -> InternalRateActionState
_rate_defined_q_transpose(private_kernel, private_state, contracts)
    -> InternalRateActionState
```

where `InternalRateActionState` contains a canonical owned read-only nominal
vector, an outward binary64 `l1_radius_upper`, a complete derivation ledger,
and only non-promotion flags.  It is not an authoritative public result:
NumPy ownership and a read-only flag do not prevent a caller that retained the
object from toggling writeability or attempting mutate-use-restore races.

The later independent verifier must therefore reconstruct the kernel and
state from immutable source payloads and manifests inside a fresh process,
retain sole ownership of every numerical array, and return only a
`RateActionReceipt` containing hashes, exact/scalar ledger fields, status, and
non-promotion flags.  No numerical array, buffer view, or object that can
restore writeability may cross that process boundary.  A same-process producer
API may exist for method tests, but its returned state is explicitly
non-authoritative and cannot satisfy independent replay.

The public method artifact and independent receipt must contain no arrays.  At
minimum the receipt binds the request, artifact, reconstructed kernel,
composition and subordinate action contracts, input state, output nominal,
derivation trace, and output-radius hashes; it records the output radius by
`float.hex`, process/capability evidence, and the fixed flags
`fresh_process=true`, `verifier_owned_reconstruction=true`,
`separate_composition_implementation=true`, `producer_arrays_accepted=false`,
`arrays_exposed=false`, `science_executed=false`, and `f0_pass=false`.  Its
status is no stronger than `PASS_RATE_ACTION_METHOD_ONLY_NOT_F0`.

The composition contract must reconstruct the nominal block-action contract
internally and require its digest to equal
`DirectedActionContract.stage1_action_contract_sha256`.  A caller may not pass
an interchangeable tuple of nominal, directed, and composition contracts.  In
addition to that equality, the composition contract binds the directed
contract digest, shape, block size, runtime, all three source hashes, and the
scalar operation-model hash.

For method-only tests, an input radius may be a declared scalar precondition.
For an authoritative recurrence, however, `input_l1_radius_upper` must be
derived from an initial-state receipt or the immediately preceding accepted
rate-action receipt and bound into the request hash.  A caller-supplied scalar
or public consistency digest alone cannot prove that the incoming uncertainty
was not understated.

### 3.1 Point lift

The directed centre action currently consumes a canonical `(N,2)` interval
array.  Lift the nominal point `c` to `[c,c]` in blocks, using one owned native
read-only destination and bounded scratch, with no tuple of per-state Python
objects.  The existing `create_packed_interval_payload` convenience path is
not admissible here: it materializes per-state Python tuples and a raw byte
payload before the final NumPy copy.  Either add a blockwise internal loader
that constructs the final canonical array directly, or count every raw byte
buffer, view, and copy in the simultaneous-lifetime ledger.  Canonicalize both
signs of zero to exact `+0.0`; this changes no real value and is required by the
current interval schema.  Record both the source-vector raw hash and the
point-lift raw hash.

The point lift is an implementation adapter, not an additional uncertainty.
It must be included in the memory ledger and must be revalidated after both
actions.  For any same-process method helper, deep-copy into private storage,
hash before use and after the last action, and label the result
non-authoritative; only the fresh-process reconstruction above closes the
caller-mutation authority gap.

Validation of the lift itself is not sufficient.  Before either action and
again after both actions, verify blockwise at every flat index that

```text
lift[i, 0] == lift[i, 1] == canonicalize_zero(c[i]).
```

Whenever `c[i] == 0`, both endpoint sign bits must be false.  Recheck the
source-nominal and point-lift raw hashes before and after use, and bind

```text
point_lift_binding_sha256 =
    H(schema, source_nominal_raw_sha256, point_lift_raw_sha256,
      zero_policy, shape, block_size).
```

Otherwise a wrong but internally canonical lift could survive its own hash
checks and accidentally enclose the nominal output.

### 3.2 Centre nominal and centre-action roundoff

Run, on the same input and under contracts with identical shape, block size,
kernel replay hash, backend binding, and summation order:

1. the repaired directed centre action, producing `[L,U]`; and
2. the stage-1 nominal block action, producing the binary64 point `d`.

Require, at every flat index,

\[
  L_i\le d_i\le U_i.
\]

This is a binding check as well as a useful proof condition.  Define the
centre-action arithmetic radius

\[
  a=\sum_i\max(d_i-L_i,\ U_i-d_i),
\]

with every subtraction and addition rounded upward in the frozen order below.
Then

\[
  \|\widehat A^T c-d\|_1\le a.
\]

Do not add the older `gamma` sparse-action allowance on top of `a`: the
directed box already encloses all centre-action multiplication and addition
roundoff.  Adding both would be safe but would obscure which proof is active
and could hide a missing binding.

## 4. One-step proof formulas

Let

\[
  m=\|c\|_1
\]

be enclosed by the deterministic outward reduction in Section 5.

### 4.1 Uniformized action

Every admissible target `P` is nonnegative and row-substochastic because the
uniformization rate is at least the exact maximum target exit witness.  Hence
`P.T` is an `l1` contraction even on signed differences.  Decompose

\[
 P^Tx-d=P^T(x-c)+(P-\widehat P)^Tc+(\widehat P^Tc-d).
\]

Therefore the required output radius is

\[
  e_P^+=e+\delta_P m+a.
\]

This is sharper and simpler than propagating the input ball with the centre
row sum and then adding `delta_P e`.  The contraction belongs to the exact
target `P`, so the latter term is not needed.

### 4.2 Generator action

Stage 1 also supplies

\[
 q_{\rm hat}=\|\widehat Q^T\|_1
 =\|\widehat Q\|_\infty
\]

as the exact-rational witness `maximum_qhat_abs_row_sum`.  Thus

\[
  \|Q^T\|_1\le q_{\rm hat}+\delta_Q.
\]

Using the same decomposition gives

\[
  e_Q^+=(q_{\rm hat}+\delta_Q)e+\delta_Qm+a.
\]

This formula, rather than a positivity argument, is the one used for signed
generator jets.

### 4.3 Equivalent box-plus-ball statement

For audit purposes, the underlying set result may also be recorded.  If
`x` belongs to a box `X` plus `B_1(e)`, and `M_X` bounds
`sup_{u in X} ||u||_1`, the repaired directed action produces a centre box
`Y`, and

\[
 P^Tx\in Y+B_1(e+\delta_PM_X),
\]

\[
 Q^Tx\in Y+B_1((q_{\rm hat}+\delta_Q)e+\delta_QM_X).
\]

This identity is the independent mathematical oracle for the point-plus-ball
implementation.  A coordinate box obtained by adding the ball radius to every
endpoint may be used only for display or containment, never as an `l1` radius
of `N` times that value.

## 5. Frozen scalar operation order

All scalar bounds are nonnegative finite binary64 upper bounds.  The new module
must use its own source-bound directed scalar primitives and must fail if an
intermediate becomes nonfinite.

1. Convert each exact `Fraction` witness to the least binary64 upper bound by
   comparing `Fraction.from_float(candidate)` with the exact witness.  Do not
   call `float(witness)` and assume its direction.
2. Compute `m` in increasing flat-index order.  For each exact stored dyadic
   `c_i`, take `abs(c_i)` and update
   `m = nextafter(m + abs(c_i), +inf)`.
3. In the same increasing flat-index order, require `L_i <= d_i <= U_i`, form
   `lo = nextafter(d_i - L_i, +inf)` and
   `hi = nextafter(U_i - d_i, +inf)`, then update
   `a = nextafter(a + max(lo, hi), +inf)`.
4. For `P`, freeze the trace

   ```text
   coefficient = mul_up(delta_p_selected, m)
   temporary   = add_up(e, coefficient)
   output      = add_up(temporary, a)
   ```

5. For `Q`, freeze the trace

   ```text
   q_norm      = add_up(maximum_qhat_abs_row_sum, delta_q)
   propagated  = mul_up(q_norm, e)
   coefficient = mul_up(delta_q, m)
   temporary   = add_up(propagated, coefficient)
   output      = add_up(temporary, a)
   ```

The exact formula identifier and every intermediate above belong in the
result digest.  Algebraically equivalent reassociation is not accepted without
a new operation-model hash and audit.  Outward rounding is applied after each
primitive, not once at the end of a long expression.

The increasing-index reductions deliberately trade a small amount of width for
constant scratch and an unambiguous proof.  A future pairwise or compiled
reducer is an optimization requiring its own frozen tree and error proof.

## 6. Required ledger and memory identity

At minimum, bind and save:

- repaired stage-1, repaired directed-action, and new composition source
  hashes;
- runtime, operation-model hash, exact tensor shape, block size, and all three
  contract hashes;
- kernel replay, source-chain, array-digest, and witness-binding hashes;
- input nominal raw hash, point-lift raw hash, point-lift binding hash,
  directed output raw hash, and nominal output raw hash;
- exact numerator/denominator and outward binary64 value for
  `delta_q`, `delta_p_selected`, and `maximum_qhat_abs_row_sum`;
- `input_l1_radius_upper`, `input_nominal_l1_upper`,
  `centre_action_roundoff_upper`, every intermediate in Section 5, and the
  final radius, together with the initial-state or previous-receipt provenance
  for an authoritative input radius;
- flat-index coverage and the exact scalar reduction count;
- exact NumPy payload identities for the point lift, directed output, nominal
  output, each block workspace, and validation scratch; and
- `science_executed=false`, `f0_pass=false`, and a status no stronger than
  `PASS_RATE_ACTION_METHOD_ONLY_NOT_F0`.

The target memory formula must reflect simultaneous lifetimes.  In particular,
it cannot quote only the Round-150 `16N + 81B` identity: the source nominal,
point lift, directed output, and nominal output overlap while `a` is reduced.
Any immutable raw payload, `frombuffer` view, deep copy, or serialization
buffer also belongs to the phase in which it remains live; a raw `16N` point-
lift payload followed by a `16N` array copy may not disappear from the ledger.
The implementation must either publish the exact maximum of each lifetime
phase or free and hash-bind an object before allocating the next one.
Allocator/RSS headroom remains a separate later gate.

For the payload-only implementation, let `C=min(N,block_size)`, count the
source nominal as `8N`, exclude the pre-owned kernel, and release any raw state
payload only after hashing it.  The minimum declared phase identities are

```text
point-lift build/validate:                         24N + 2C
directed action:            40N + max(81C, 2C, 2048)
nominal action with lift and directed output live: 48N + 65C
final binding/revalidation:                        48N + 2C
declared peak:                     maximum of all four phases
```

After the lift and directed enclosure are released, an internal method result
retains only the `8N` nominal output.  Any still-live raw bytes, `frombuffer`
view, deep copy, or serialization buffer is added by its actual length to the
corresponding phase; the identities above are not a license to omit it.

## 7. Independent exact oracle

The composition tests need an oracle that does not call the new directed
scalar helpers, the stage-1 witness lookup, or the Round-150 interval oracle.

For tiny 1D, 2D, and 3D tensor shapes:

1. decode every stored endpoint with `Fraction.from_float`;
2. independently construct exact target `Q` rows from off-diagonal rates and
   killing, including the coupled diagonal;
3. construct exact `P = I + Q/lambda` using the same exact rational rate;
4. independently reconstruct the stored centre matrices from their raw
   coefficient bytes;
5. recompute exact max-row `delta_Q`, both exact `delta_P` branches, selected
   `delta_P`, and the centre `Q` absolute-row norm;
6. enumerate all rate/killing endpoint vertices on very small cases, all point
   inputs in the chosen exact test set, and the extreme points `+/- e e_i` of
   the input `l1` ball; and
7. check with exact rational arithmetic that

   \[
     \|A^T(c+b)-d\|_1\le e_A^+
   \]

   for every enumerated target and ball extreme.

Heterogeneous forward/backward rates and heterogeneous killing are mandatory.
Include reflecting and periodic boundaries, signed `Q` inputs, nonnegative `P`
inputs, intervals crossing zero for the `Q` path, subnormal products, and block
sizes `1`, an interior non-divisor, and larger than the state count.  Rate and
killing source endpoints use canonical `+0.0` only; a `-0.0` source endpoint is
a fail-closed mutation.  Nominal inputs containing either sign of zero must
produce the same canonical `+0.0` point lift.

The test oracle should also compare the full result against the more general
box-plus-ball statement in Section 4.3.  For a point output `d` contained in a
centre box `Y=[L,U]`, the required covering radius is the **farthest-point**
quantity

\[
  \sup_{y\in Y}\|y-d\|_1
  =\sum_i\max(d_i-L_i,\ U_i-d_i).
\]

It is not the ordinary distance from `d` to the set `Y`, which is zero when
`d` lies in the box and would unsafely erase the centre-action roundoff.  No
interval library or implementation helper is required to evaluate this exact
oracle.

## 8. Fail-closed mutation suite

At least the following mutations must return a frozen HOLD code:

- reinstate a strided Boolean ufunc `out` buffer or mutate the contiguous
  validator scratch contract;
- understate, rename, duplicate, or swap `delta_q`, `delta_p_selected`, or the
  `Qhat` norm witness;
- use a column maximum instead of the required max absolute row sum;
- omit the target diagonal's shared-rate/killing dependence;
- omit `e` from the `P` formula, omit `delta_Q e` from the `Q` formula, or
  reassociate the frozen scalar trace;
- reduce only centre coefficients and silently ignore their source intervals;
- move the nominal point outside `[L,U]` by one ulp;
- lower `a`, `m`, an intermediate, or the final radius by one ulp;
- change the point-lift zero canonicalization, input hash, kernel hash,
  backend/order binding, runtime, block count, or memory ledger;
- make the lift differ from canonicalized `c` at one endpoint, change its
  binding digest, accept a `-0.0` rate/killing endpoint, or retain a negative
  zero in the point lift;
- omit a simultaneously live raw byte buffer/copy, expose an internal array in
  a purported verifier receipt, or accept a same-process result as independent
  replay;
- pass a signed nominal vector to `P`, a writable/view/subclass/non-native
  array, a nonfinite endpoint, or an overflowed scalar; and
- mutate source, kernel, input, directed output, or nominal output bytes after
  their first hash check.

## 9. Route from the one-step action to uniformization

Uniformization is a later module, not part of the next patch.  Once the
one-step action has passed an independent attack, the reference recurrence is:

\[
 (c_{j+1},e_{j+1})=
 \operatorname{rate\_defined\_p\_transpose}(c_j,e_j).
\]

For directed Poisson weights with midpoint `what_j`, radius `r_j`, and upper
endpoint `wbar_j`, accumulate one nominal vector in the frozen order
`j=0,...,K`.  The final `l1` ledger must separately include:

\[
 \sum_{j=0}^K \overline w_j e_j
 \quad\text{(power/action enclosure)},
\]

\[
 \sum_{j=0}^K r_j\,\|c_j\|_1^+
 \quad\text{(weight enclosure)},
\]

the directed scale/add accumulation enclosure, and

\[
 \tau M
 \quad\text{(Poisson tail using an independently sourced exact mass cap)}.
\]

Do not reuse `delta_P` as a Poisson-weight error, do not count the directed
centre-action width twice, and do not infer `M=1` from a normalized-looking
binary64 array.  The initial-law mass cap needs its own source hash and proof.

Across time chunks, exact sub-Markov contraction carries the previous output
radius without amplification.  Generator jets then use the `Q` action formula
of Section 4.2, with the same repaired and hash-bound rate witnesses.

## 10. Stop conditions

Stop the composition stage and keep F0 on HOLD if any of the following occurs:

- the contiguous-scratch validator repair or heterogeneous-rate/killing
  re-audit is absent;
- a source, runtime, contract, kernel, input, or result hash differs;
- a witness cannot be recomputed exactly from the owned bytes;
- the uniformization-rate witness does not dominate the exact target exit;
- a nominal centre result is outside the directed box;
- an outward scalar intermediate, output radius, or payload count is
  nonfinite, negative, or exceeds a predeclared cap;
- an exact small-grid oracle or any mutation does not fail/pass as prescribed;
- producer and verifier share authority or the verifier exposes its numerical
  arrays; or
- an implementation tries to proceed to Poisson propagation before a
  separate-implementation, fresh-process attack accepts the exact one-step
  bytes.

For the later uniformization stage, additionally stop on a Poisson mean, term
count, tail, chunk count, state radius, wall-time, payload, RSS, or swap value
outside its frozen preflight limit.  No tolerance, chunking choice, or resource
cap may be relaxed after observing an output.

The largest-shape build/action/propagation resource acceptance remains a
separate gate.  This design neither allocates that target nor predicts its
acceptance from small cases.

## 11. Implementation order

```text
R152 validator repair
  -> fresh stage-1 and directed-action re-audit with heterogeneous exact oracles
  -> point-lift + one-step P/Q point-plus-l1-ball composition
  -> exact independent composition oracle and mutation attack
  -> fresh-process/separate-implementation replay of frozen bytes
  -> directed Poisson and weighted-accumulation integration
  -> generator jets and scalar reductions
  -> neutral scaled resource gates
  -> only then reassess F0
```

Nothing in this sequence by itself changes the current HOLD decision.
