# Round 164: target-aware uniformization, semantic replay, and tiny-Q jets

Date: 2026-07-14

Decision: **TINY METHOD-SCOPE PASS / P0 = 0 / P1 = 0 / P2 = 0 ON FINAL
REVIEWED BYTES / PHYSICAL INITIAL SOURCE OPEN / CLEAN AUTHORITY OPEN /
TOPOLOGY OPEN / PRODUCTION RESOURCE OPEN / F0 HOLD / NO F1 / HOLD PRR**

This round closes three bounded integration defects in the science-free,
at-most-64-state method chain:

1. sparse unit-mass targets and repeated time chunks no longer have to place
   an entire symmetric l1 ball inside the nonnegative simplex;
2. a second code path reconstructs the component box, unit-mass witness,
   dense uniformized action, and Poisson enclosure without consuming the
   producer rate-action or Poisson ledgers; and
3. fixed-operator generator states through order four now feed exact-Fraction
   killing-observable intervals and modulus bounds.

It does not bind a physical initial law to the component box, create a
fresh-process authority, replay the complete serialized result chain, certify
full-window topology, or pass the production-size resource gate.  No positive
budget, prospective control, F1 row, or publication result was evaluated.

## Final reviewed bytes

| Object | SHA-256 |
| --- | --- |
| code/rate_defined_tensor_f0_packed_target_uniformization.py | 5acd20fc227defc7573f4a54b2ab543f192719b3bd7be65de5620c2ef4491323 |
| code/test_rate_defined_tensor_f0_packed_target_uniformization.py | 72d50b1a1fe711ef95b451238050ccea3f291f7dca98a779ca3887b3380e5878 |
| code/rate_defined_tensor_f0_tiny_semantic_replay.py | df22f3882c2457de8e1ee3428c70679220148d6f43ad725b21fe49230ed3de3f |
| code/test_rate_defined_tensor_f0_tiny_semantic_replay.py | 47dadfbfbf2138830f803b65dd18ca55287aeb7a7c8123c986720b07419ddc3c |
| code/rate_defined_tensor_f0_packed_tiny_jets.py | b3fc573bb17c3201019665433fb06121001e1b05810fa524e808909427dcf1b1 |
| code/test_rate_defined_tensor_f0_packed_tiny_jets.py | c8c2e040abbd0731e27e2f18ce8e3b0a6af4a95e965a32b08d0a8133af83b670 |

The jets layer additionally rechecks the accepted packed, directed-action,
rate-action, rate-action-test, target-adapter, and target-adapter-test bytes at
entry and exit.  The target adapter itself pins the accepted Round-162
uniformization implementation and test.

## Sparse target and chunk argument

Let a canonical nonnegative component box contain at least one exact
unit-mass vector \(p\), and let \(\ell\) be its componentwise lower endpoint.
The adapter constructs a deterministic lexicographic unit-mass witness only
to prove that the box intersects the unit simplex.  It does not call that
witness the physical initial law.  For every intended unit-mass target in the
box,

\[
  \|p-\ell\|_1
  =\sum_i(p_i-\ell_i)
  =1-\sum_i\ell_i.
\]

The lower endpoint is a nonnegative subprobability anchor.  The frozen
uniformization producer is run on that anchor with zero input radius, and the
complete target-to-anchor distance is added to its output radius.  For the
killed Markov semigroup \(T_t\), sub-Markov l1 contraction gives

\[
 \|T_t p-\widehat T_t\ell\|_1
 \le \|p-\ell\|_1+e_{\rm frozen}.
\]

Repeated chunks carry the complete preceding radius without amplification and
bind the same kernel replay digest, rate-action contract digest, cumulative
time, and chunk count.  A continuation under a different kernel is rejected.

## Independent semantic replay within tiny scope

The replay does not use the producer action, power, Poisson, or mass ledgers.
It independently:

- validates raw component-box endpoints and their manifest;
- reconstructs the lexicographic exact unit-mass witness;
- checks the lower anchor and exact initial l1 radius;
- builds dense \(P^{\mathsf T}\) from raw interval centres and deviations;
- encloses \(\exp(-\mu)\) by an exact alternating Fraction series;
- advances the Poisson recurrence and tail; and
- requires the producer point-plus-ball output to contain the independent
  reconstruction.

The review found no under-enclosure on the honest tiny cases.  An earlier
wording issue was repaired before this freeze: the target field now says only
canonical_unit_mass_witness_proved, and the module states explicitly that
binding the intended physical law to the analytic source of the component box
remains open.

The replay is still same-process and uses the packed kernel validator.  It
does not consume a clean serialized TargetUniformizationResult with the whole
contract and cumulative chunk history, so it is not a clean independent
authority.

## Generator jets and scalar reductions

For one operator-bound target, the successor constructs

\[
 z_r=(Q^{\mathsf T})^r p,\qquad r=0,\ldots,4,
\]

by four applications of the accepted signed point-plus-l1-ball action.
The zeroth nominal is nonnegative; every later nominal is explicitly allowed
to be signed.  If \(z_r\in c_r+B_1(e_r)\), the already accepted rate-action
recurrence supplies a conservative next radius.

For the killing vector \(k\), let \(\widehat k\) be the stored binary64 centre,
\(K_\infty\) the exact maximum killing upper witness, and \(\delta_k\) the
exact maximum componentwise centre uncertainty.  The scalar centre is computed
as an exact Fraction dot product of the stored binary64 values.  Therefore

\[
 |k^{\mathsf T}z_r-\widehat k^{\mathsf T}c_r|
 \le K_\infty e_r+\delta_k\|c_r\|_1.
\]

The layer returns \(J_0,\ldots,J_3\) from this interval and

\[
 M_r=K_\infty(\|c_r\|_1+e_r),\qquad r=2,3,4.
\]

The independent test reconstructs dense exact-Fraction generators.  It checks
a degenerate-rate two-state chain and a periodic size-two interval-rate chain,
where forward and backward rates can land on the same neighbour and therefore
must be added.  Each global primitive rate is selected once and reused across
all tensor rows and all powers of the same sampled generator.

The lower/mid/upper parameter grid is deliberately called a stress grid, not
an exhaustive proof for the continuous rate box: for \(r\ge2\), repeated
generator powers are not multi-affine in the primitive rates.  Full-box
enclosure comes from the operator-norm recurrence, while the exact grid is an
independent numerical check.

## Independent review and executed validation

The final tiny-jet bytes received an independent local read-only review:

~~~text
P0 = 0
P1 = 0
P2 = 0
tiny-jets tests                              5 / 5 passed
rate-action + target + tiny-jets tests      71 / 71 passed
Ruff check                                  PASS
Ruff format --check                         PASS
~~~

The target-adapter plus semantic-replay focused suite independently passed
14/14 after the final witness-field wording repair.  No network was used.

## Exact remaining boundary

~~~text
sparse target / repeated tiny chunks              = METHOD PASS
component-box and unit-simplex intersection        = METHOD PASS
independent dense/Poisson semantic replay          = TINY SAME-PROCESS PASS
tiny z0..z4, J0..J3, M2..M4                       = METHOD PASS
physical or analytic source -> component box       = OPEN
clean serialized whole-result replay               = OPEN
fresh-process independent implementation           = OPEN
full-window interval topology                      = OPEN
7,165,305-state production resource gate           = OPEN
F0                                                 = HOLD
F1 / positive-budget campaign                      = NOT AUTHORIZED / NOT RUN
PRR release                                        = HOLD
~~~
