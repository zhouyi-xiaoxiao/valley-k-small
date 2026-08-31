# Round 108: independent adversarial attack on the fixed-control F0 design

Date: 2026-07-14  
Role: independent result-blind scientific, numerical-analysis, provenance, and
dependency reviewer  
Decision: **HOLD-DESIGN-AS-WRITTEN / GO-REPAIR-ONLY / HOLD-IMPLEMENTATION /
NO POSITIVE-B SCIENCE**  
Priority counts: **P0 = 1, P1 = 6, P2 = 3**

## 0. Scope and non-execution boundary

This audit independently attacked the complete bytes of
`notes/positive_b_fixed_control_robustness_design_v1.md`, SHA-256

```text
891b49a3b9efbfa93c27c09e4f585a088b40f079c3ff5642536764f1523698d7
```

and compared them with its self-audit
`audits/round_105_fixed_control_f0_design_self_audit.md`, SHA-256

```text
0631d6b71d58349a75c1695aa02bea66ae3e1d27cc587e3fefb1904b0f77fef0
```

and the pinned repaired theory
`notes/modal_certificate_theory_and_prr_redirect.md`, SHA-256

```text
38dde114552d0cea69f714d7493d3cb6715e1b4ed436431045a50a57360326be
```

The relevant exploratory input was
`scratch/modal_certificate_lp_poc_result.json`, SHA-256

```text
6f04ef4c618677d6d26b80cd04e3d4f8c9918fd50a649cfc0dd0bf064ccce604.
```

This audit did **not** evaluate any of the three new controls at positive
budget, did not build a production grid, did not run an exponential action,
did not open a held-out F1 value, and did not modify the design, manuscript,
producer, schema, or scientific result.  The only computation was static
exact-rational/state-count arithmetic and a repository text/provenance search.
This report is the only workspace write.

## 1. Executive decision

The design contains a real stop-ship logic regression.  Section 10.3 restores
the already falsified Stage-B-v4 odd-grid Boolean: a zero coarse difference
alone activates its roundoff-floor branch, even if the fine-grid value jumps.
That admits a false `mesh-stable` F1 pass.  The corrected two-difference v5
gate already exists in the repository and must be ported exactly.

Two further chains are not closed:

1. the fixed weights are copied from an explicitly exploratory LP POC that is
   not the repaired theory's unrestricted-`rho`, lexicographically tied,
   outward-certified selector; and
2. the supposed F1-to-F2 mechanical selector is neither mathematically
   specified nor cryptographically pinned before F1, while the present basin
   envelope compares configuration-specific cuts rather than one common
   physical estimand.

The sub-Markov contraction, defect estimate, Taylor enclosures, and interval-
Newton logic are mathematically sufficient **if** their exact generator and
outward numerical hypotheses are implemented.  They are not currently an
implementation.  The half-cell grids also have coherent same-physics prose,
but no accepted constructor/certificate.

The correct disposition is therefore:

```text
static design v1                   = HOLD
Round-105 PASS-CONDITIONAL         = OVERTURNED BY ROUND-108 P0
repair/version-bump                = AUTHORIZED
F0 implementation build           = NOT AUTHORIZED FROM THESE BYTES
F1 manifest                        = NOT AUTHORIZED
positive-B evaluation              = NOT AUTHORIZED
F2/F3                              = NOT AUTHORIZED
manuscript promotion               = NOT AUTHORIZED
```

## 2. Independent static checks that pass

### 2.1 Exact controls and budget ratios

The four `float.hex()` entries for each control reproduce the displayed raw
binary64 values.  Their exact dyadic sums are:

```text
lp_m1 = 36028797018963973 / 36028797018963968
lp_m2 =  9007199254740991 /  9007199254740992
lp_m3 = 36028797018963967 / 36028797018963968.
```

Dividing each component by its own exact positive sum produces a strictly
positive exact rational vector with exact unit sum and preserves all component
ratios.  This part of the design is mathematically sound.  Silent binary64
summation, clipping, projection, or last-component repair would not be sound.

### 2.2 Configuration and workload arithmetic

The 12 displayed state counts recompute exactly to

```text
one-control sum          = 34,787,462
3 controls x 12 grids   = 104,362,386 base-state cells
two complete replicas   = 208,724,772 base-state cells
logical rows            = 36.
```

The four half-cell rows have the displayed tensor sizes.  The reflecting
vertex-centred dual-volume description, including half boundary volumes, and
the shifted periodic partition describe discretizations of the same
continuous physical geometry rather than shifted supports.  This is a design-
level pass only; the volume-aware SG/contact/profile constructors remain
unimplemented.

### 2.3 Full-window topology partition

`[0.5,35]` contains exactly 138 dyadic quarter-width tiles.  The stated prefix,
search bands, and suffix cover it without a temporal gap for all three
controls.  If every tile is outwardly strict-sign excluded except one unique
typed interval-Newton root in every declared band, then the resulting
semidiscrete stationary lists are exactly

```text
lp_m1: max
lp_m2: max, min, max
lp_m3: max, min, max, min, max.
```

Thus the design correctly separates the exact finite-window F1 claim from the
general theorem's at-least-`m` claim and from off-lattice positive-event
estimands.  It does not assign absence or an exact root count to Monte Carlo.

### 2.4 Continuous-time certificate mathematics

For an exact killed row generator satisfying

```text
Q_ij >= 0 (i != j),     Q 1 = -k <= 0,
```

`exp(Q^T s)` is an induced-`l1` contraction on signed vectors.  Consequently

```text
|f^(r)(t_i+s)|
 <= ||k||_infinity ||(Q^T)^r p(t_i)||_1 = M_r(t_i)
```

is valid.  The direct-from-zero path-defect estimate is also valid by
variation of constants.  With genuinely outward `J_0,...,J_3` and
`M_2,...,M_4`, both displayed Lipschitz/Taylor ranges enclose the full tile,
and their intersection remains an enclosure.  An empty intersection must
therefore be a hard inconsistency, as the design says.

With `0` excluded from `[f''](X)`, an outward interval Newton step

```text
c - J_1(c)/[f''](X) subset interior(X)
```

is a sufficient unique-root inclusion.  Together with strict signs on every
other tile, it excludes missed sign-preserving/even-multiplicity roots.  The
global reversible spectral estimate is correctly demoted to a diagnostic;
its very large stationary-weight condition factor must not close a tile.

This is a proof-contract pass, not an implementation pass.  Binary64
`expm_multiply`, replica agreement, or a dense scan still does not meet it.

## 3. Priority findings

### R108-P0-1 — the known false-pass odd-grid floor branch was reintroduced

Section 10.3 literally requires, for each promoted scalar, either

```text
Dplus(I_O129,I_O113) <= 5e-8
```

or

```text
Dplus(I_O161,I_O129) < Dminus(I_O129,I_O113).
```

This is the Stage-B-v4 Boolean rejected in
`audits/round_70_stageb_v4_independent_attack.md`, SHA-256
`0fa94a3d94db356e81f62746f267743bbc3f431dc82959894d00b88a9bea9c62`.
The defect is not hypothetical.  For point root-time intervals

```text
O113 = [8.300,8.300]
O129 = [8.300,8.300]
O161 = [8.304,8.304]
ref  = [8.302,8.302],
```

the printed v1 gate gives

```text
Dplus(O129,O113)  = 0       <= 5e-8,
Dplus(O161,O129)  = 0.004,
Dminus(O129,O113) = 0.
```

The coarse floor branch therefore returns true even though the fine
difference is nonzero and cannot satisfy strict contraction.  The complete
reference envelope is only `0.002`, below the root-time absolute cap `0.05`;
identical topology and all unrelated grids can also be supplied.  Hence the
P0 can survive the other printed gates and promote a noncontracting sequence.

The already audited v5 repair is

```text
max(Dplus(I_O129,I_O113),Dplus(I_O161,I_O129)) <= 5e-8
or
Dplus(I_O161,I_O129) < Dminus(I_O129,I_O113).
```

Required repair:

1. version-bump the F0 design and port the complete v5 Boolean;
2. define `Dplus`/`Dminus` by exact-real endpoint expressions followed by
   directed binary64 rounding, not native round-to-nearest helpers;
3. require the Round-70 finite counterexample, the v5 both-at-floor positive
   fixture, a strict-contraction positive fixture, vector-coordinate failure,
   and the Round-73 half-ulp directed-rounding fixture in the mutation suite;
4. apply the corrected operation to every role-specific promoted scalar; and
5. prohibit a complete-envelope pass from overriding an odd-gate failure.

The fact that `Dminus=0` when coarse intervals overlap is not itself a bug.
Overlap means strict contraction is not certified; only the corrected
**both-adjacent-differences-at-floor** branch may then pass.  If this proves too
strong operationally, v1 must remain `HOLD`; it cannot be weakened after F1.

### R108-P1-1 — the design freezes exploratory weights, not the repaired formal selector

The design correctly labels the POC exploratory, result-informed, noninterval,
and not a publication gate.  It nevertheless copies that POC's solver-native
weights into the primary controls and describes them as LP-derived/selected.
The current POC producer:

- constrains `rho >= 0` rather than leaving it free;
- uses solver-native primary tie breaking;
- has no lexicographic secondary LP chain;
- has no certified primal/dual optimality or positive-optimum enclosure;
- has no outward simultaneous box-curvature certificate; and
- has no full-window complement-derivative certificate.

Those are exactly the formal-selector conditions retained by the repaired
theory and its Round-106 re-audit.  Positive-B F1 could independently prove
the three fixed controls' topology, but without this missing B0 chain the
paper cannot claim that the repaired convex selector/certificate selected
them, and the analytical-design and physical-realization layers remain only
loosely joined.

Required repair, before any F1 manifest, must choose one explicit branch:

1. **formal-selector branch:** build a new append-only B0 selector design,
   unrestricted-`rho`/lexicographic implementation, exact failure semantics,
   outward primal/dual and full box-plus-complement result, and independent
   audit.  If its output bytes differ, create fixed-control design v2 with the
   new controls; do not mutate v1; or
2. **fixed-pilot branch:** call the three tuples pilot-derived fixed constants,
   make no claim that they are outputs of the formal selector, and separately
   certify full-window B0 inequalities for these exact rational weights.  A
   formal convex-selector result would then remain a separate missing PRR
   component.

A dense B0 root scan or the present POC `all_gates_passed=true` cannot close
this finding.

### R108-P1-2 — the F1-to-F2 selector is prose, not a pre-F1 no-refit object

Section 11 says that a “mechanical selector fixed at F0” will map accepted
`MR+F` roots and envelopes to cuts, windows, contrasts, tolerances, alpha,
power, `N`, seed domain, chunks, and pools.  It supplies none of those mapping
operations.  The F0 schema has no explicit selector hash; the F1 manifest has
no accepted-selector or accepted-F0-audit hash; only the later F2 plan mentions
`selector_hash`.

As written, an implementation can wait for F1, then choose among many
reasonable window widths, rounding rules, contrasts, effect sizes,
multiplicity allocations, power models, sample caps, and seeds while still
claiming that some selector was “fixed at F0.”  The no-refit sentence does not
make an unspecified operation byte-unique.

Required repair:

1. write the exact F1-to-F2 operation trace before F1, including all failure
   and boundary/tie cases;
2. define common cuts, window endpoints and outward rounding, contrast signs,
   deterministic FV uncertainty subtraction, tolerance, family membership,
   alpha allocation, effect-size lower bound, power formula, ceiling, `N`
   rounding, pool/seed/chunk derivation, and infeasibility `HOLD`;
3. content-hash the selector implementation and tests in the F0 record;
4. pin the accepted independent F0 audit and selector hash in the F1 manifest
   and result; and
5. require F2 to reject any mismatch rather than selecting a replacement.

### R108-P1-3 — the basin envelope does not yet compare one common physical estimand

Section 9.3 defines each configuration's basin mass using that
configuration's own certified valley roots.  Section 10 then envelopes those
numbers, while Section 11 proposes to use `MR+F` roots plus the envelope for
off-lattice planning.  These are different observables: changing the cut
changes the event whose probability is measured.  An envelope of
configuration-specific valley-cut probabilities is not automatically an
uncertainty bound for the single fixed-cut probability later estimated by an
off-lattice process.

Topology-adaptive valley masses are useful shape diagnostics, but they must be
named separately from cross-method physical estimands.

Required repair:

1. retain per-configuration valley-cut masses only as explicitly adaptive
   diagnostics;
2. have the pre-F1 selector generate one common set of physical cuts/windows;
3. evaluate every one of the 12 FV configurations on exactly those same sets,
   with outward cut uncertainty included;
4. form `E_FV` for those common-observable probabilities/contrasts; and
5. permit F2/F3 to consume only that common-observable envelope.

If the common cuts are mechanically derived from F1 roots, the design needs a
predeclared locked two-stage F1 operation or sufficient saved certified states
to evaluate the selected times without discretionary new science.  This must
be specified before the first F1 value is read.

### R108-P1-4 — “selected before positive-budget evaluation” overstates the evidence timing

A repository search for the three exact tuple bytes found them only in the B0
POC/theory/tests/audits and this F0 design, not in a positive-B result.  It is
therefore reasonable to say that **these three specific controls** are being
frozen before their first recorded positive-B evaluation.

It is not a blind family-level prospective discovery.  The same broad
four-support family, geometry, budget `B=0.01`, many thresholds, and challenge
ideas were informed by the historical positive-B anchor and the failed
allocation-v6 program.  The design itself pins those result-informed inputs.

Required repair is an explicit evidence-timing record such as

```text
RESULT_INFORMED_FAMILY_PILOT / SPECIFIC_CONTROL_POSITIVE_B_HELD_OUT
```

plus a `known_before_freeze` ledger.  The result and manuscript may say

> After positive-budget pilot work in the same family, the three specific
> allocation tuples were frozen before their first positive-budget evaluation.

They may not call F1 a blind family discovery or omit the prior family pilot.
Any unrecorded prior evaluation of one of the exact tuples would require
disclosure and relabelling, not deletion.

### R108-P1-5 — three local box comparisons have an undefined `Base`

Section 10.4 requires `Base--M+`, `Base--R+`, and `Base--MR+`, but the
configuration set contains four different base rows:
`O113/Base`, `E128/Base`, `O129/Base`, and `O161/Base`.  The box grids' other
coordinates strongly suggest `O129/Base`, but “suggest” is not a byte-unique
gate.  An implementation could select whichever base gives the most favorable
comparison.

Required repair is to name the exact pairs, prospectively, for example

```text
O129/Base -- M+
O129/Base -- R+
O129/Base -- MR+
MR+       -- MR+F.
```

The repair must also record the actual cell spacings: the midpoint enlargement
uses 166 cells and is close to, but not exactly at, the O129 midpoint spacing.
That is acceptable as a combined box/small-spacing challenge if disclosed; it
must not be described as an exact same-spacing box-only difference.

### R108-P1-6 — the append-only status/dependency schemas do not close HOLD paths

The schema sketch cannot yet enforce the prose dependency chain:

- the F1 manifest does not explicitly pin an **accepted independent F0 audit**;
- neither F0 nor F1 explicitly pins the F1-to-F2 selector identified above;
- F1 requires 36 rows, while the hard-stop policy may stop early, but there is
  no row enum or `NOT_RUN_AFTER_HOLD` stub contract;
- allowed global/row statuses, reason codes, required-null versus forbidden-
  null fields, row order, and first-failure semantics are absent;
- no rule says which volatile environment/timing/path fields are excluded from
  the byte-identical canonical payload; and
- an F0 record can syntactically say `PASS_F0_IMPLEMENTATION` without a schema
  edge to the independent acceptance that is supposed to authorize F1.

Required repair is a science-free schema package with enumerated states,
reason precedence, 36 ordered row records or mandatory not-run stubs, exact
nullability, canonicalization, blob ownership, audit hashes, selector hashes,
and negative mutations for every hard stop.  F1 creation must fail unless the
accepted independent F0 audit and all dependency hashes match exactly.

### R108-P2-1 — exact scalar and hazard conventions should be made literal

The parameter table says “decimal binary64 input” and supplies hex bytes, but
later text says “exact `B=0.01`.”  The future parser must state whether the
mathematical scalar is the exact dyadic represented by
`0x1.47ae147ae147bp-7` or the decimal rational `1/100`; the current evidence
strongly indicates the former.  The same convention should cover every other
hex-pinned parameter.

Section 8 should also distinguish, by separate symbols, the physical killing
vector `k_B=B k_0(w)` from the per-unit-budget field `k_0(w)`.  The killed
identity, density, derivative bounds, and installed-budget integral must all
use the same choice.  This is a clarity repair, but leaving two exact targets
available is unsafe for interval code.

Required repair: freeze the exact dyadic scalar semantics, print the exact
installed-budget functional including physical cell volumes, define
`Q_B 1=-k_B`, `f=k_B^T p`, and state how exact rational weights enter `k_0`.

### R108-P2-2 — several root-time interval observables need exact enclosure rules

The design correctly demands interval quantities, but it does not yet give an
operation trace for:

- boundary-layer mass over an uncertain root interval, which is not monotone
  in time and cannot be bounded from root endpoints alone;
- the exact “differential mass-balance interval” expression and dependency-
  aware radius computation;
- survival monotonicity when independently evaluated direct-from-zero state
  intervals overlap; and
- the stopping rule for interval Newton inside the allowed maximum of 12
  steps, which can materially change interval widths and the odd gate.

Required repair: define the state representation (for example, centre plus a
certified `l1` ball), outward linear-functional/time remainder for every
root-interval diagnostic, exact mass-balance expression, analytical versus
numerical monotonicity proof, and deterministic Newton stopping/serialization
rule before science.

### R108-P2-3 — operational feasibility remains an explicit pre-science gate

The corrected odd rule is intentionally strict: if O113/O129 intervals
overlap, `Dminus=0`, so strict contraction cannot pass and both adjacent
`Dplus` values must be at the `5e-8` floor.  Root intervals are otherwise
allowed to be as wide as `0.05`, and the full direct-from-zero certificate can
require many high-dimensional actions.  Nothing presently demonstrates that
the interval radii, 20 bisection levels, 12 Newton steps, precision, memory,
and resource limits can close all 36 rows.

Required repair is a science-free benchmark on analytic/synthetic and scaled
explicit matrices using the **corrected complete odd Boolean**, outward
arithmetic, and the actual stop policy.  If it is infeasible, version-bump the
design before positive-B output or kill the route.  Interval overlap after F1
is not permission to replace `Dminus`, enlarge the floor, or use point
differences.

## 4. Cross-check against the repaired modal theory

The v1 design agrees with SHA `38dde...` on several important boundaries:

- exact finite-window topology requires complete root boxes plus complement
  exclusion;
- local alternating signs alone prove only an at-least/non-strict statement;
- off-lattice evidence never proves exact topology or absence;
- a cusp/fold is not required; and
- the general dimension/mode theorem remains fixed-finite-`(d,m)`, not uniform.

It does not yet instantiate the theory's formal selector/certificate chain.
The POC weights are promising pilot inputs, not an outwardly certified exact
selector result.  A successful F1 could prove the semidiscrete physical
topologies of fixed weights, but it would not retroactively certify LP
optimality, lexicographic selection, the B0 full complement, or a quantitative
`B_cert` reaching `0.01`.

The eventual paper must therefore keep these statements distinct:

```text
general theorem: at least m certified modes in its sequential weak regime
B0 formal selector: exact scope to be supplied by a new accepted artefact
F1 finite-volume: exact stationary topology only on [0.5,35]
F3 off-lattice: positive common-window/event-law compatibility only.
```

## 5. Required repair order

No current issue requires positive-B evaluation.  The safe order is:

1. version-bump the design and repair the P0 odd Boolean with all old
   counterexamples and directed-rounding fixtures;
2. decide and freeze the formal-selector versus fixed-pilot branch;
3. write the exact common-observable F1-to-F2 selector and pin its hashes;
4. make evidence timing and the exact box-comparison pairs explicit;
5. freeze exact dyadic/hazard conventions and the interval-observable
   operation traces;
6. build canonical schemas, dependency/audit edges, row HOLD/not-run states,
   and mutation tests;
7. benchmark the corrected certificate only on synthetic/scaled fixtures;
8. obtain a new independent static-design PASS;
9. only then build and independently accept the science-free F0
   implementation; and
10. only after that acceptance create a separately reviewed F1 manifest.

If a formal B0 selector returns different control bytes, the current tuples
must not be silently replaced.  If the corrected odd gate or rigorous
semigroup enclosure is infeasible, no dense scan, point estimate, tolerance
change, or historical-anchor rescue may promote v1.

## 6. Final verdict

The scientific idea remains strong: three same-support allocations under one
conserved budget, a complete semidiscrete finite-window root certificate, and
an independent unbounded process test would materially improve the PRR case.
The exact-control normalization, topology/claim separation, sub-Markov
contraction, and same-physics alignment intent survive this attack.

The current static design nevertheless cannot be accepted because its odd
refinement gate can return a false scientific pass, and the B0-selector and
F1-to-F2 no-refit chains are not yet byte-closed.

```text
FINAL ROUND-108 DECISION = HOLD-DESIGN-AS-WRITTEN
NEXT AUTHORIZED ACTION    = REPAIR AND INDEPENDENTLY RE-AUDIT DESIGN V2
AUTHORIZED F0 BUILD       = NONE FROM V1
AUTHORIZED F1 COMMAND     = NONE
AUTHORIZED POSITIVE-B RUN = NONE
```
