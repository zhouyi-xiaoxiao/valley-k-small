# Round 110: self-audit of the F1-to-F2 common-observable selector v1

Date: 2026-07-14  
Audited object: `notes/f1_to_f2_common_observable_selector_v1.md`  
Object SHA-256:
`9ab69dbd9662577aa72760bf003240ef0cd1edba167f03ceb72cd8335045c1af`  
Audit mode: science-free mathematical, statistical, byte-uniqueness, and
dependency attack  
Positive-budget/new-control execution: **NONE**

## 0. Decision

```text
static selector design         = PASS-CONDITIONAL
selector implementation        = HOLD-NOT-BUILT
repaired upstream F0           = HOLD-NOT-ACCEPTED
F1 two-stage manifest          = NOT AUTHORIZED
F1 positive-budget execution   = NOT AUTHORIZED
F2 plan                        = NOT BUILT
F3 Monte Carlo                 = NOT AUTHORIZED
```

Open dependency findings: **P0 = 0, P1 = 2, P2 = 1**.

No surviving ambiguity was found in the mathematical selection operation
itself.  The design now fixes one 12-grid valley-hull midpoint, one exact
lattice window construction, common probability estimands, cut uncertainty,
complete deterministic envelopes, confidence families, conditional power,
trajectory caps, and seed/chunk derivation before F1.  It cannot be called an
implementation or an F2 plan until the open dependencies close.

## 1. Scope and evidence boundary

This audit read:

- the complete selector design at the hash above;
- `audits/round_108_fixed_control_f0_independent_attack.md`, SHA-256
  `07bb0a843d752541887d3ec56b5755d1406045140883661dccd174a2219876b8`;
- `notes/positive_b_fixed_control_robustness_design_v1.md`, SHA-256
  `891b49a3b9efbfa93c27c09e4f585a088b40f079c3ff5642536764f1523698d7`;
  and
- the older off-lattice estimator/power design as method provenance only.

It did not read or run any new-control positive-budget row, finite-volume
state, F1 root, F2 output, trajectory, MC count, or scientific result.  Static
checks used only exact fractions and symbolic interval/window relations.  The
only workspace writes are the selector design and this audit.

## 2. Adversarial checks

### 2.1 The two-stage F1 dependency is one-way

The future manifest must pin one orchestrator:

```text
complete F1-A -> independent verifier -> selector -> complete F1-B
-> final result -> independent final audit.
```

The selector has no input edge from F1-B or MC.  A held/missing F1-A row
creates not-run F1-B stubs; it cannot select from the passing subset.  F1-B
must save direct-from-zero state/action certificates at every mechanically
selected time, so F2 cannot request an extra deterministic state after seeing
the result.  This closes Round-108 P1-2's post-F1 discretion at design level.

The internal F1-A verifier is not mislabelled as a final accepted F1 result.
Final F1 acceptance still occurs only after F1-B and an independent audit.

### 2.2 The common cut is total and byte-unique

For finite binary64 hull endpoints `L<=U`, the exact midpoint lies in
`[L,U]`.  Rounding that midpoint to the nearest representable binary64 cannot
jump outside an interval whose endpoints are themselves representable; the
explicit containment check catches any implementation error.  Exact
ties-to-even removes the only midpoint tie.

The design constructs the hull from all 12 interval endpoints, not from
points or `MR+F` alone.  It requires strict global ordering of the complete
role hulls before taking a cut.  Consequently no cross-grid role swap,
touching valley/peak hull, or favorable-reference cut can pass.

The cut uncertainty

```text
delta_v=max(v-L,U-v)
```

is outwardly serialized.  Monotonicity of `F=1-S` gives the stated basin
extrema over every cut hull:

- the first basin grows with its cut;
- an interior basin grows with its upper cut and shrinks with its lower cut;
  and
- the last basin shrinks with its lower cut.

Thus the robust formulas cover all cut choices without a corner scan.  For
`lp_m1`, the final object correctly uses empty cut arrays and the single
interval `1-S(100)` rather than a dummy valley.

### 2.3 The window geometry cannot overlap silently

All centres and widths are exact multiples of `q_time=2^-10`.  Since

```text
h <= (c_(r+1)-c_r)/4,
```

two role-window centres are at least `4h` apart while each window has
half-width `h`; their closures have a gap of at least `2h`.  The boundary
terms similarly keep every ordinary role window inside `[0.5,35]`.

For `lp_m1`, normalized coordinates relative to its peak centre give

```text
left shoulder = [-4h,-2h]
peak          = [-h,+h]
right shoulder= [+2h,+4h],
```

so the two gaps are exactly at least `h`.  The factor-four boundary terms in
`h_raw` keep the shoulders inside the window.  Strict role-hull containment
and explicit closure-disjointness remain mandatory checks, so a wide root
hull returns HOLD rather than causing a wider post-result window.

The `floor(h_raw/q_time)` operation and `n_h>=1` rule make the width unique.
There is no ordered list of fallback widths.

### 2.4 Every FV/MC comparison is now the same physical observable

F1-B integrates all 12 configurations on the exact selected cuts and window
endpoints.  Window probability is `S(a)-S(b)`, not point density times width.
All methods therefore estimate the same event-time set.

The power reference is not a collection of unrelated interval midpoints.
`MR+F` supplies one pinned central survival sequence, required to be an exact
nonincreasing sequence inside all certified intervals.  Exact differences of
that same sequence define every basin/window reference probability.  It
therefore supplies one coherent point law with exact basin closure and
disjoint-window total at most one.  Any incoherent central sequence is HOLD,
not permission to normalize selected probabilities independently.

For basin masses, the common point cut remains the actual future MC estimand;
the broader cut-robust interval is included only as conservative deterministic
uncertainty.  This may double-count some root-location variation, but it
cannot create a false positive.  The result separately serializes point-cut
and cut-robust values, so the conservatism is visible.

For every scalar interval `I_g`, the cross-endpoint definition of `E_det`
contains both the reference self-width and every configuration-to-reference
difference.  Because `x_ref` lies in the reference interval,
`[x_ref-E_det,x_ref+E_det]` contains all 12 promoted intervals.  Thus neither
point differences nor disjoint error budgets can understate the common-
observable envelope.

### 2.5 Deterministic subtraction precedes every positive claim

The selector does not use `MR+F` point values as MC alternatives.  It first
subtracts the complete `E_det` and a mechanically quantized compatibility
allowance.  Basin planning requires

```text
p_alt=x_ref-E_det-tau>0.005.
```

For a peak/valley window pair it requires

```text
pA_low = pA_ref-E_A-tau_A
pB_high= pB_ref+E_B+tau_B
d_low  = pA_low-pB_high>0.
```

The two windows are disjoint and the final design explicitly requires
`pA_low+pB_high<=1`; hence the two planning marginals can belong to one
multinomial law.  The unique midpoint split satisfies
`pB_high<theta<pA_low` or the selector holds.  This is a strictly positive,
finite-resolution event-law effect, not an MC topology claim.

### 2.6 Familywise alpha arithmetic is exact

The member allocations recompute as

```text
6  * (1/600) = 1/100
12 * (1/800) = 3/200
22 * (1/880) = 1/40
sum           = 1/20 = 0.05.
```

The 22 simultaneous window-probability intervals already cover every
probability entering all 16 pool-specific contrast assertions.  Deriving a
contrast from two covered intervals introduces no new coverage event, so no
second alpha charge is required.  DKW supplies one simultaneous survival band
per control/pool over the entire selected time set; it is not a collection of
uncorrected pointwise bands.

Both pools are inside the family count and must pass separately.  A pooled
diagnostic has no rescue edge.

### 2.7 Conditional power arithmetic and exact-test discreteness are handled

The single joint planning alternative is that coherent reference point law.
The subtracted basin/peak/valley values are monotone worst cases under it, not
different incompatible alternatives: the reference basin/peak probability is
at least its subtracted lower value, while the reference valley probability
is at most its padded upper value.

The powered assertion count is

```text
6 + 12 + 12 + 22 + 16 = 68,
```

so `68*(1/680)=0.10`; the union bound gives at least `0.90` joint power when
every assertion has lower power at least `1-1/680` under its declared planning
alternative.

Clopper--Pearson endpoints are monotone in the count.  Therefore:

- a lower-floor or lower-split pass set is a suffix;
- an upper-split pass set is a prefix; and
- an interval-containment compatibility set is contiguous.

Integer binary search is therefore legitimate.  For a contrast, the peak and
valley marginal counts are dependent, but the union bound on their two
failure events is valid without independence.  Using `pA_low` for the peak
and `pB_high` for the valley is conservative by binomial stochastic
monotonicity.

The candidate grid is finite and explicitly inspected.  The selector does
not assume exact CP power is monotone in every integer `N`; it chooses the
first passing **allowed chunk multiple**, not a globally minimal sample size.
Each control has its own two-equal-pool `N_c`, and the final check

```text
2*(N_m1+N_m2+N_m3)<=50,000,000
```

applies the historical ceiling to the complete campaign, not independently
to each control.  A cap failure is terminal.

Compatibility power is explicitly conditional on equality to the reference
planning probability/curve.  The note does not misrepresent that conditional
calculation as a guarantee under every alternative inside the tolerance band.
Actual off-lattice disagreement can and must fail.

### 2.8 Special-function and seed operations are non-discretionary

Directed special-function evaluation uses the first decisive precision in
the fixed sequence `256,512,1024,2048,4096`; failure at 4096 bits is HOLD.
This blocks library-native last-bit decisions and an output-dependent
precision increase without an upper cap.

Production seed material is derived only after the final F1 result and audit
exist.  The seed basis includes their hashes and the preaccepted selector
implementation hash, so there is no circular dependency on an F2 result or
MC count.  Domain-separated control/pool keys, injective trajectory/counter
coordinates, fixed chunks, collision HOLD, and no top-up close manual seed,
schedule, and partial-count selection.

The exact Philox4x32 word map and unsigned key-word map are printed, and every
chunk-index/endpoint integer is `uint64_be` inside a domain-separated hash.
Host-endian casting or a different word order cannot silently reproduce the
same logical seed record with different trajectories.

### 2.9 Claim boundary survives the selector

The selector produces only common event sets, deterministic probability
envelopes, positive contrast lower bounds, and planning inputs.  It neither
relabels the F1 finite-window root census as a continuum theorem nor asks MC
to prove absence, exact topology, a fold, or a cusp.  The general analytical
at-least-`m` theorem, semidiscrete F1 exact topology, and off-lattice positive
event-law evidence remain separate layers.

## 3. Repairs made during the self-attack

Six issues were found and closed before the audited SHA was frozen:

1. A preliminary cap was interpretable as 50 million trajectories **per
   control**.  The final bytes impose 50 million across all controls and both
   pools.
2. The peak/valley robust marginals were not explicitly required to satisfy
   `pA_low+pB_high<=1`.  The final bytes add this multinomial-coherence gate.
3. The no-cut `lp_m1` robust basin interval was inferable but not explicit.
   The final bytes define it as the same `1-S(100)` interval.
4. Precision escalation did not explicitly say which successful precision is
   canonical.  The final bytes serialize the first decisive precision.
5. Independently taking every interval midpoint could produce planning
   probabilities that did not belong to one event-time law, invalidating the
   advertised joint-power union bound.  The final bytes require one coherent
   central `MR+F` survival sequence and exact probability differences.
6. The RNG counter/chunk prose lacked a complete endian/word operation trace.
   The final bytes fix Philox4x32 words and big-endian chunk-hash integers.

No physical input, F1 value, positive-budget row, trajectory, threshold, or
result was used to make these repairs.

## 4. Open dependency findings

### R110-P1-1 — no byte-accepted implementation or independent verifier exists

The design specifies exact arithmetic, canonical JSON, role/window logic,
Clopper--Pearson thresholds, binomial tails, DKW power, SHA domains, and HOLD
semantics.  No implementation, schema, synthetic fixtures, mutation suite,
special-function interval engine, or independently coded verifier currently
instantiates those rules.

Required closure is science-free: build the package, include midpoint ties,
overlapping hulls, zero width, shoulder boundaries, cut corners, invalid
probability intervals, alpha/beta counts, CP equality boundaries, sawtooth
power, N-cap, seed collision, nullability, replica mismatch, and every HOLD
mutation, then obtain an independent PASS.  No F1 manifest may precede it.

### R110-P1-2 — the required repaired upstream F0/F1 chain is not accepted

Round 108 held fixed-control F0 design v1 because of the odd-grid false-pass
gate and other dependency gaps.  This selector cannot cure or bypass that
HOLD.  It also depends on a formal B0 selector/fixed-pilot disposition, an
accepted interval-semigroup implementation, an accepted half-cell FV
constructor, and a sealed two-stage F1 manifest/verifier that do not yet
exist.

Required closure is the upstream order printed in Round 108.  The selector
implementation must pin the accepted replacement hashes; substituting held v1
or a partial F1-A grid set is a dependency HOLD.

### R110-P2-1 — scientific/operational feasibility is intentionally unknown

No current data establish that future 12-grid role hulls will be globally
disjoint, fit inside the fixed windows, preserve a robust common-cut basin
floor, yield `d_low>0`, produce a positive quantized tau, or meet 90% joint
power under the 50-million whole-campaign cap.  This is not a license to add
fallback widths or relax the cap.

When F1 eventually runs, any failure is a scientific selector HOLD.  A new
result-informed design could be developed later, but the failed F1/selector
output would not remain held out.

## 5. Authorized next step and final verdict

The selector design closes the logical freedom identified in Round 108:

- one cut per valley from all 12 certified intervals;
- one common window family per control;
- all 12 FV rows evaluated on the same physical sets;
- explicit cut uncertainty and deterministic subtraction;
- exact familywise alpha and conditional power;
- a whole-campaign N cap and derived two-pool RNG/chunk domain; and
- no human choice between F1-A and F1-B.

Its remaining findings are implementation and upstream-dependency gates.  No
positive-budget or MC action is authorized.

```text
FINAL ROUND-110 VERDICT = PASS-CONDITIONAL STATIC SELECTOR DESIGN
NEXT AUTHORIZED ACTION   = SCIENCE-FREE IMPLEMENTATION AND INDEPENDENT ATTACK
F1 AUTHORIZATION         = NONE
F2 PLAN STATUS           = NOT BUILT
MC AUTHORIZATION         = NONE
```
