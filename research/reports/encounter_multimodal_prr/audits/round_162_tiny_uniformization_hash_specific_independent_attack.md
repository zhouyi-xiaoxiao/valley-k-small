# Round 162: hash-specific independent attack on tiny packed uniformization

Date: 2026-07-14

Decision: **ACCEPT EXACT PRODUCER BYTES AS A BOUNDED, SAME-PROCESS,
NON-AUTHORITATIVE, SCIENCE-FREE METHOD PRIMITIVE / P0 = 0 / P1 = 0 /
P2 = 2 / HOLD F0 / NO F1 / HOLD PRR**

Two independent readers attacked the frozen producer and test bytes below.
One used exact `Fraction` and dense-matrix oracles over hostile tiny tensor
fixtures; the other independently rederived the Poisson and point-ball
inequalities and repeated a disjoint high-precision smoke.  Neither reader
edited the implementation.  No network, positive-budget input, F1 row,
production-size state space, Monte Carlo calculation, generator jet, or
topology calculation was used.

This decision accepts only the numerical path executed directly by the exact
producer bytes.  It does not accept an externally supplied result or ledger,
does not establish independent replay authority, and does not close F0.

## Exact byte identities

| Object | SHA-256 |
| --- | --- |
| `code/rate_defined_tensor_f0_packed_uniformization.py` | `20c95975b5e43fcd5ed2ccd91c578c32524f6a3b2cc4ab5133da36fc3eddb72c` |
| `code/test_rate_defined_tensor_f0_packed_uniformization.py` | `dcd3d1c6ae36059a13f98fc9ee9e7409b512ac72e59a25274a3df0e4bdcbd4cd` |
| `code/rate_defined_tensor_f0_packed.py` | `447aa3bc224685ea1cc556d9d322dafba05ef148945d4ae41291f83e29f3deb4` |
| `code/rate_defined_tensor_f0_packed_interval_action.py` | `2f3201a9eb1b6fbe577b43c3b046ad5f7f369816a7d4a32f4381506e63494f2a` |
| `code/rate_defined_tensor_f0_packed_rate_action.py` | `7c1586e54bac2008ac910d5c2b910cee5206dab8c19948f5b5857db6563813c9` |
| `code/test_rate_defined_tensor_f0_packed_rate_action.py` | `b5127aa26ab3179986b5ad5cafbcae55c3dd6768217a2b500ea496f1f833939f` |

The producer checks all four dependency identities before the method and
again after it.  Mutating each pinned constant independently failed before
the first recurrence action.

## Accepted mathematical path

The tiny contract fixes a whole-rate-box uniformization rate and restricts

```text
state count <= 64
Poisson mean mu <= 1
retained Poisson terms <= 64
exact numerator/denominator bit length <= 4096
```

For `mu >= 0`, the producer encloses `exp(mu)` with an exact positive Taylor
partial sum and a geometric remainder.  Reciprocation gives an interval for
`exp(-mu)`, and exact rational multiplication gives every retained Poisson
weight.  With `T` retained weights, the first omitted upper weight is

```text
weights[T - 1].upper * mu / T
```

and the largest later ratio is `mu / (T + 1)`.  The producer takes the smaller
of the normalization remainder and this valid geometric-tail upper bound.
Independent attacks over 260 dyadic mean/tolerance combinations, including
means `0, 1/16, 1/2, 3/4, 1` and tolerance down to `2^-80`, enclosed a separate
alternating-series oracle.  Direct mutations of both tail indices failed.

Let the accepted rate-action layer enclose the `j`th power state by
`x_j in c_j + B_1(e_j)`, and let the exact weight lie in `[l_j,u_j]`.  The
producer accumulates `sum l_j c_j` exactly as rational numbers and books

```text
sum u_j e_j
+ sum (u_j - l_j) ||c_j||_1
+ omitted_tail_upper * input_mass_upper
+ final binary64 conversion error
```

as an outward `l1` radius.  Reapplying the accepted rate action may enlarge
the set by allowing a different admissible box point at each power, but it
still contains the required repeated action of every one fixed admissible
`P`; this is conservative, not an under-enclosure.

The initial precondition `radius <= min(center_i)` makes the entire input ball
nonnegative, while `sum(center) + radius <= 1` gives a subprobability mass cap.
The fixed target `P` is nonnegative and row-substochastic, so the tail cap and
the final intersection with `[0,input_mass_upper]` are valid.  The public
ledger correctly calls this conclusion conditional on the declared input
radius and keeps authoritative target nonnegativity false.

## Executed attacks

The saved tests passed:

```text
13 tiny-uniformization tests + 59 rate-action tests = 72 passed
packed + directed + rate-action + tiny uniformization = 136 passed
ruff check = PASS
ruff format --check = PASS
```

Additional read-only attacks covered:

- periodic size two, including coincident forward/backward neighbors;
- a mixed two-dimensional tensor and block sizes `1,2,4,5,11`;
- 64 globally coupled rate-box vertices crossed with input-ball extreme
  points, all enclosed and byte-consistent across block choices;
- a killed dense-exponential oracle for nonnegativity and mass loss;
- `N=64` acceptance and `N=65` rejection;
- mean, term, and NumPy-payload caps before the first `P` action;
- the packed-kernel payload identity `40N + 64 sum_d n_d`;
- 13 mutations of authority, science, topology, jet, and resource flags.

No actual producer-path P0 or P1 was found.

## P2-162-1: the power hash chain is not an action replay

The saved power ledger binds each generated action's hashes and prevents an
ordinary skipped or reset predecessor during the producer call.  Its public
validator is nevertheless only a recomputable structural chain.  An auditor
coherently changed one output radius to zero, changed the next input radius,
and recomputed every downstream digest; both the power-ledger and whole-result
validators accepted the altered object.

Therefore the chain detects accidental or partial drift but is not proof that
an external ledger was produced by the action.  No downstream stage may use a
deserialized or modified power ledger as numerical evidence.

## P2-162-2: the Poisson validator is not an exponential replay

The producer path correctly constructs its base weight from the saved Taylor
endpoints.  The standalone ledger validator, however, checks recurrence and
mass relationships without recomputing that base-weight binding.  An auditor
coherently replaced the finite recurrence by a normalized finite sequence,
set the tail to zero, and recomputed the dependent fields.  The validators
accepted even though the forged base weight lay above an independent strict
upper bound for `exp(-mu)`.

Therefore the Poisson ledger validator is an internal consistency check, not
an independently replayed exponential certificate.  Only the direct return
of the frozen producer in the same call lies inside this round's acceptance.

These two findings are P2, rather than P1, only because every accepted output
is forced to state

```text
non_authoritative = true
science_free = true
fresh_process = false
science_executed = false
jets_complete = false
topology_complete = false
production_resource_gate = false
f0_pass = false
```

Promoting either validator to authority would immediately raise both findings
to P1.

## Resource and scientific boundary

The NumPy ledger includes the bridge and reports the pre-owned packed kernel
separately from the subordinate action peak.  It explicitly does not measure
Python `Fraction` objects, allocator overhead, RSS, swap, or wall time, and it
sets exact-memory and production-resource flags false.  Tiny fixtures cannot
substitute for the `7,165,305`-state resource gate.

Generator jets, full-window interval coverage, stationary topology, a clean
independent implementation replay, production resources, positive budget,
all 36 F1 rows, and the off-lattice event-law comparison remain open.  The
present result is a useful recurrence oracle for the next science-free F0
layer; it is not F0 acceptance or a manuscript result.
