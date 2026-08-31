# Round 113: independent adversarial attack of the F1-to-F2 selector v1

Date: 2026-07-14  
Audited design: `notes/f1_to_f2_common_observable_selector_v1.md`  
Audited design SHA-256:
`9ab69dbd9662577aa72760bf003240ef0cd1edba167f03ceb72cd8335045c1af`  
Self-audit read as an adversarial input, not accepted as evidence:
`audits/round_110_f1_to_f2_selector_self_audit.md`  
Self-audit SHA-256:
`73306603dfa88a23bb9eff1514551640e811b1d1b55582790e55c04cf899915b`  
Audit boundary: static, science-free, no positive-budget row, no Monte Carlo,
no manuscript edit.

## 0. Independent verdict

```text
12-grid hull/cut/window mathematics       = PASS
cut-uncertainty and E_det containment      = PASS
CP/DKW family arithmetic and 68 count      = PASS, subject to P1 repairs
50,000,000 whole-campaign cap              = PASS
two-pool counter/chunk domain structure    = PASS, conditional on RNG repair
F1-A -> selector -> F1-B direction         = PASS, conditional on point-law repair
complete byte-unique selector specification= FAIL
pinning into repaired F0 v2                = HOLD

open findings: P0 = 3, P1 = 5, P2 = 1
```

**FINAL ROUND-113 VERDICT: HOLD FOR PINNING INTO F0 v2.**  Round 110's
`PASS-CONDITIONAL STATIC SELECTOR DESIGN` is too strong.  The mechanical
geometry and conservative statistical arithmetic survive, but three pairs of
conforming implementations can still produce different planning laws,
payload bytes, or production random streams.  Those are no-refit and
reproducibility failures, not missing polish.

Severity in this audit is:

- **P0:** two implementations can obey the printed text on the same accepted
  upstream evidence yet change a scientific gate, hashed payload, or random
  stream; the design cannot be pinned;
- **P1:** must be closed in the science-free implementation/schema package
  before F1 authorization; and
- **P2:** does not change acceptance, but should be made explicit or removed.

No finding authorizes a positive-budget F1 row, an F2 run, MC, or a manuscript
claim.

## 1. Evidence and attack method

The complete 925-line design and complete 360-line self-audit were read.  The
two object hashes above were recomputed before this audit.  The attacks used
only exact integer/fraction arithmetic, binary64 adjacency/tie examples, small
synthetic intervals, and SHA-256 domain constructions.  Existing off-lattice
code was read only to determine whether an unmentioned Philox variant could be
inherited; it cannot be inherited without an explicit hash edge.

The static calculations below are deliberately separated from the blocking
findings.  A correct formula does not repair a non-unique source value or hash
domain.

## 2. Recomputed portions that pass

### 2.1 All-12-grid hulls, midpoint cuts, and common windows

The role hull is genuinely the hull of all 12 certified intervals.  The
following mutation is rejected as required even though every individual grid
is ordered:

```text
grid 1: P=[1,1.9], Q=[2,3]
grid 2: P=[1,2.5], Q=[2.6,3]

global P hull=[1,2.5]
global Q hull=[2,3]
```

The global hulls overlap, so the strict test `upper(P)<lower(Q)` fails.  A
reference-only or point-only implementation would false-pass this fixture and
must be killed by mutation testing.

The binary64 midpoint rule is total.  For adjacent finite binary64 endpoints,
the exact midpoint rounds to one of the two endpoints and therefore remains in
the closed interval.  Exact tie fixtures around one are:

```text
[0x1.0000000000000p+0,0x1.0000000000001p+0] -> lower endpoint
[0x1.0000000000001p+0,0x1.0000000000002p+0] -> upper endpoint
```

The first lower significand is even; the second is odd.  The lattice analogue
also behaves as printed: `1024.5 -> 1024` and `1025.5 -> 1026` under ties to
even.  Serializing the exact midpoint, tie branch, and rounded result is enough
once the canonical-byte findings below are repaired.

For role centres, `h <= (c_(r+1)-c_r)/4` implies centre separation at least
`4h`.  Two closed role windows of radius `h` therefore retain a gap of at least
`2h`.  The `lp_m1` normalized windows

```text
left shoulder [-4h,-2h]
peak          [-h,+h]
right shoulder[+2h,+4h]
```

retain gaps of `h`.  The boundary terms in `h_raw`, `n_h>=1`, strict hull
containment, and closure-disjoint checks jointly fail closed.  No overlap or
midpoint-tie counterexample survived.

### 2.2 Cut uncertainty, probability coherence, and deterministic envelope

The cut-uncertainty extrema have the right monotone directions.  With
`F=1-S`, the first basin increases with its upper cut; an interior basin
increases with its upper cut and decreases with its lower cut; the final basin
decreases with its lower cut.  The printed corner formulas therefore enclose
all allowed cut locations.  Intersecting an outward result with `[0,1]` is
conservative, and the no-cut `lp_m1` case is explicit.

For any grid interval `I_g=[L_g,U_g]`, reference interval
`I_ref=[L_ref,U_ref]`, and `x_ref in I_ref`, define

```text
E=max(|L_g-U_ref|,|U_g-L_ref|).
```

Every pair `(z,x_ref)` lies in `I_g x I_ref`; the maximum distance on that
rectangle is attained at an opposite endpoint.  Hence `|z-x_ref|<=E`.  Taking
the maximum over all 12 grids and rounding upward proves the advertised
containment.  An exact enumeration over the 11-point dyadic grid
`{k/16:k=0,...,10}` checked all 18,876 choices of `I_g`, `I_ref`, and
`x_ref in I_ref`; there were zero violations.  Including the reference
self-term makes the construction deliberately conservative, not wrong.

If one coherent survival path is uniquely supplied, exact differences make
all basin/window probabilities coherent: telescoping basin probabilities plus
`s_ref(100)` equal one, disjoint window probabilities are nonnegative and sum
to at most one, and contrasts are differences of the same event law.  The
blocking issue is that the design does not uniquely supply that path; see
R113-P0-1.

The `tau` floor behaves as stated.  Writing `q=q_tau` and assuming the cap is
inactive:

```text
b=4q -> tau_raw=q/2 -> tau=0 -> HOLD
b=8q -> tau_raw=q   -> tau=q -> PASS
b=9q -> tau_raw=9q/8 -> tau=q -> PASS.
```

The basin alternative and contrast construction subtract `E_det` and `tau`
in the conservative direction.  The multinomial check
`pA_low+pB_high<=1` is sufficient for the two disjoint marginal planning
values; the contrast power union bound does not assume independence.

### 2.3 Confidence accounting and conditional power

The familywise alpha arithmetic recomputes exactly:

```text
6*(1/600)  = 1/100
12*(1/800) = 3/200
22*(1/880) = 1/40
sum         = 1/20.
```

There are exactly

```text
6 survival compatibility
+12 basin floor
+12 basin compatibility
+22 window compatibility
+16 contrast
=68 powered assertions.
```

Thus `beta_member=1/680` and a union bound gives total planned failure at most
`68/680=1/10`, hence joint planned power at least `0.90`.  Counting one
contrast assertion is legitimate because its lower bound already subtracts
the two marginal failure probabilities.  No additional confidence alpha is
needed for contrasts because they reuse the simultaneous window intervals.

Monotonicity of the two CP endpoints makes every printed count-acceptance set
contiguous.  The basin-floor and split probabilities are evaluated at the
correct monotone worst cases.  Compatibility power uses the coherent
reference probability.  The DKW expression also has the correct algebra: if
`delta=A_min-eps>0`, a strict empirical sup-error event gives failure at most
`2 exp(-2N delta^2)`.  The strict/contact wording and survivor encoding still
need the P1 repair below.

### 2.4 Candidate cap, counter domains, chunks, and dependency direction

The schedule tests only multiples of 100,000, chooses the first per-control
pass, and then applies the whole-campaign constraint.  Boundary fixtures are:

```text
(N_m1,N_m2,N_m3)=(8.0m,8.0m,9.0m)
2*sum=50.0m -> allowed

(8.1m,8.0m,9.0m)
2*sum=50.2m -> HOLD_N_CAP.
```

Given six distinct keys, `(control,pool,trajectory_id,draw_block)` is
injective: the key separates control/pool, the high 64 counter bits separate
trajectories, and the low 64 bits separate draw blocks.  The exhaustion stop
prevents wraparound.  Chunk intervals are disjoint, exhaustive, and ordered.
For the synthetic `seed_basis=bytes(0,...,31)`, three chunks for each of three
controls and two pools produced 18 distinct IDs; the first and last were

```text
6385caf6aca4a53961e2a8eecdd7ac51692c8db302f9abb2df4bf75d8e4e12ad
260383b6b2ba221d7123615c948585afca296da2ac1de6a5544cb6805a28555c.
```

This validates the printed chunk-message layout, not the incomplete Philox
transform specification in R113-P0-3.

The declared dependency graph is one-way:

```text
complete F1-A -> verifier -> selector -> complete F1-B -> final F1 audit.
```

The cut/window selection reads only F1-A, F1-B evaluates all 12 rows at the
mechanically selected times, and F2 cannot request a new deterministic state.
No favorable-grid deletion, F1-B-to-selector feedback edge, or MC top-up is
printed.  Once the central-point source is uniquely frozen, this part satisfies
the no-refit requirement.

## 3. Blocking findings

### R113-P0-1 — the coherent reference point law is constrained but not selected uniquely

**Location.**  Sections 3.2 and 7.1, especially the phrases “central values of
the same saved validated state sequence” and “pinned central survival
projection.”

F1-B is required to save state/action blobs and scalar enclosures, but the
design never names the exact central-state field, projection expression,
rounding operation, or pre-F1 algorithm that turns those bytes into
`s_ref(t)`.  Monotonicity, interval membership, closure, and window checks are
constraints, not a selector.

An exact dyadic counterexample uses certified survival intervals

```text
I(t1)  =[13/16,15/16]
I(t2)  =[ 9/16,11/16]
I(100) =[ 1/16, 3/16],  with 0<t1<t2<100.
```

Both paths satisfy every printed point-law constraint:

```text
path A: (s(t1),s(t2),s(100))=(28/32,20/32,4/32)
path B: (s(t1),s(t2),s(100))=(29/32,19/32,3/32).
```

Yet the same window probability is `1/4` under A and `5/16` under B, while
`P(T<=100)` is `7/8` under A and `29/32` under B.  Certified probability
intervals can contain both.  The paths then change `x_ref`, `E_det`, `tau`, CP
acceptance sets, `N`, the F1 result hash, and all downstream seeds.  Calling
both “central” is not prevented because “central” has no normative byte rule.
Choosing one feasible monotone path, projecting interval midpoints
isotonically, or using a solver's incidental point approximation after F1
would be a hidden F1-value-dependent refit.

**Required closure.**  Before F1, pin one canonical point-state field in every
validated blob, its binary format, the exact survival projection expression,
all arithmetic/rounding, and its dependency hash.  Define `s_ref` only as that
projection.  If the resulting predeclared sequence fails monotonicity,
interval membership, or probability coherence, return
`HOLD_REFERENCE_POINT_LAW`; no isotonic repair, feasible-path search, midpoint
substitution, or alternate centre is allowed.  Add a mutation with the two
paths above and prove that only the pinned source bytes can be read.

### R113-P0-2 — `canonical_payload_sha256` has no non-circular hash domain

**Location.**  Section 12 lists `canonical_payload_sha256` inside the “F1
internal selector payload,” while Section 2 requires one canonical hashed
payload.

The design does not say whether the digest field is omitted, empty, null, or
included while computing that digest.  Hashing the complete object literally
creates a self-referential fixed-point equation.  Hashing the object with the
field omitted and hashing it with an empty placeholder are two common,
text-compatible implementations and produce different bytes and digests.
Nothing tells the independent replica which one is canonical.

**Required closure.**  Define, for example, a `selector_payload_core` whose
schema excludes every digest of itself; compute

```text
canonical_payload_sha256 =
  SHA256(canonical_UTF8_with_terminal_newline(selector_payload_core)).
```

Then place the core and digest in a separately specified envelope and, if the
envelope itself is content addressed, give that hash a different name outside
the envelope.  Pin omission/placeholder behavior, terminal-newline inclusion,
and verifier recomputation.  Add omit/null/empty/literal-self mutations.  Until
this is fixed, even a PASS or HOLD selector payload is not byte-unique.

### R113-P0-3 — “Philox4x32” plus a word map does not specify a random transform

**Location.**  Section 10 fixes key/counter word placement but not the Philox
round count, constants/version, known-answer vectors, or a normative RNG-core
hash.

Random123 exposes `Philox4x32_R<ROUNDS>`; the round count is part of the
algorithm, not an implementation detail.  With the standard Philox4x32
constants, the all-zero counter/key gives:

```text
7 rounds : 5f6fb709 0d893f64 4f121f81 4f730a48
8 rounds : 618f177a 9920c1d7 1ec12dc0 c43b6eeb
10 rounds: 6627e8d5 e169c58d bc57ac4c 9b00dbd8.
```

All three use the printed word map.  Therefore the same `seed_basis`, pool key,
trajectory ID, and draw block can produce different trajectories while
passing Section 10 as written.  The official class documentation makes the
round parameter explicit:
<https://www.thesalmons.org/john/random123/releases/latest/docs/structr123_1_1Philox4x32__R.html>.

The repository happens to contain a 10-round implementation and independent
Python reference:

```text
code/off_lattice_doi_compiled_core.cpp
  SHA-256 b4c673bafbc4c7f07d0a7520b5a7c9dad64b9e8123573f17da8c076ffa494938

code/off_lattice_doi_compiled_core_harness.py
  SHA-256 e47edaba9f1fac602358cda6788e37d7896903f61f690e56f86f9d7c8ebff431

audits/round_101_off_lattice_compiled_core_validation.md
  SHA-256 62cf5bb97a3ee46d01ab9de7b4c91ecdd64f895a8c3b6a7c98494d99fc49986f
```

Those hashes are absent from the selector dependency graph, so the selector
cannot silently inherit them.

**Required closure.**  Freeze `Philox4x32-10`, all four constants, unsigned
32-bit multiply/high-low semantics, key bump timing, output word order, and
known-answer vectors, and pin either the accepted core/spec hash or an exact
normative algorithm in the pre-F1 implementation package.  The later F2 plan
must also pin conversion of output words to every random variate and the
draw-consumption state machine.  Include 7-versus-10-round and word-consumption
mutations.  Do not add the F2 plan hash to its own seed basis; use a preaccepted
RNG/kernel-spec hash or a separately content-addressed run envelope.

## 4. P1 findings that must close before implementation acceptance

### R113-P1-1 — decimal constants and `float.hex()` acceptance need exact canonical grammars

The text correctly requires binary64 leaves to arrive as lowercase
`float.hex()` strings, but it does not require parse-then-canonicalize equality.
All of

```text
0x1p+0
0x1.0p+0
0x1.0000000000000p+0
```

are lowercase and parse to the same binary64 value, while only the final form
is Python's canonical `float.hex()` output.  A permissive parser can therefore
accept multiple upstream hashes for one semantic value.  Duplicate JSON keys,
UTF-8 rejection, string escaping, and enum/key character sets also need
normative schema rules; “keys sorted” alone does not define input acceptance.

The constants `0.4`, `0.01`, `0.001`, and `0.005` must also be serialized as
reduced exact rationals, not host binary64 literals.  Their nearest binary64
values are all strictly above the exact decimal rationals.  In particular,
choosing `p_alt` equal to binary64 `0.005` passes `p_alt>1/200` but fails
`p_alt>binary64(0.005)`.  That is a real basin-gate divergence.

Require exact canonical spellings by round-trip equality, reject duplicate
keys before object construction, restrict hashed strings to pinned ASCII where
possible, and freeze constants as `2/5`, `1/100`, `1/1000`, and `1/200` (or
other explicitly intended reduced rationals).  Add alternate-spelling and
rational-versus-binary64 boundary mutations.

### R113-P1-2 — primary HOLD precedence and secondary ordering are not a total order

Section 11 says “the first failure in the fixed operation order” but never
defines a total validator/stage order, and the enum list is only “at minimum.”
For one payload containing a stale dependency hash, a negative-zero leaf, and
`null` where `lp_m1` requires `[]`, plausible implementations can emit
`HOLD_DEPENDENCY_HASH`, `HOLD_NUMERIC_LEAF`, or
`HOLD_SCHEMA_NULLABILITY` as primary.  They can also discover and sort
secondaries differently.  This violates the explicit requirement that HOLD
payloads be byte-identical.

Freeze a numbered total order covering decode, duplicate-key rejection,
schema, dependency hashes, numeric leaves, F1-A status, each scientific stage,
seed checks, and append-only checks.  Freeze whether validation continues
after each class, the complete enum set, secondary-reason sort order, and every
`NOT_RUN_AFTER_HOLD` stub.  Exhaust all pairwise and selected three-way fault
mutations.

### R113-P1-3 — the excluded Philox test-key set has no pinned identity edge

Section 10 requires six production keys to lie outside a “separately pinned
test-key set,” but no hash or provenance for that set appears in the required
upstream identity, `seed_basis`, or future implementation record.  Selecting
or changing the set after the six keys are known can manufacture or remove a
`HOLD_SEED_COLLISION`.

Pin the ordered test-key set and its canonical SHA-256 before F1, include its
hash in the implementation/manifest dependency graph, and define exact
comparison width/endian semantics.  A post-F1 change must be
`HOLD_DEPENDENCY_HASH`, never a salt or new test set.

### R113-P1-4 — strict DKW containment and administrative censoring need a byte-level convention

The compatibility gate is strict, but Section 9.2 says containment follows
when empirical sup error is “at most” `A_min-eps`.  At equality a band can
touch a compatibility boundary, so the sufficient event must be strict:
`D_N < A_min-eps`.  The same numerical DKW lower bound remains available by
taking the increasing limit in the standard inequality, but the comparison
and serialized event must not use `<=`.

Also pin the raw outcome convention at the administrative horizon.  A
trajectory with no event by 100 must be encoded as right-censored/
`T>100` (for example a tagged survivor), not as an event at `T=100`; otherwise
`S_n(100)` and the last basin change.  Pin equality classification at every cut
and window endpoint and derive every count from the one tagged outcome record.
Add DKW-contact, event-at-100, survivor-at-100, and endpoint-equality
mutations.

### R113-P1-5 — the special-function verifier contract is not canonical yet

Pinning MPFR precision alone does not make a beta inverse, binomial tail, or
DKW expression byte-unique.  Two rigorous expression DAGs at the same
precision can return different outward intervals while making the same strict
decision.  Requiring an “independently coded verifier” to agree byte-for-byte
on every directed interval either rejects valid independent enclosures or
quietly forces it to copy the producer.

The implementation package must freeze the producer's expression DAG,
rounding direction at every operation, MPFR/MPFI version/build/runtime hashes,
and canonical interval bytes.  The independent verifier should be required to
prove containment and the same integer threshold/strict decision; if exact
producer-interval equality remains required, it needs a separately specified
canonical reference algorithm.  Boundary fixtures must cover every precision
step through 4096 and the `HOLD_SPECIAL_FUNCTION_AMBIGUOUS` branch.

## 5. P2 finding

### R113-P2-1 — the two largest per-control candidates can never pass the global cap

Every other control has minimum candidate 100,000 per pool.  Therefore one
control can be at most

```text
25,000,000 - 100,000 - 100,000 = 24,800,000
```

per pool in any globally admissible campaign.  Testing 24.9m and 25.0m for a
single control cannot change the final verdict; the later global check always
holds them.  This is not a correctness bug.  The implementation may retain the
printed 250-candidate scan for literal reproducibility, or a future revision
may stop at 248 only if that change is frozen before F1 and tested as
equivalent.  It must not prune candidates using observed MC counts.

## 6. Mutation ledger

| mutation | required outcome | independent result |
|---|---|---|
| remove one of 12 grids or substitute `MR+F` early | `HOLD_SELECTOR_INPUT` | PASS |
| per-grid ordered but global role hulls overlap | `HOLD_ROLE_HULL_OVERLAP` | PASS |
| adjacent binary64 midpoint, even lower | lower endpoint | PASS |
| adjacent binary64 midpoint, odd lower | upper endpoint | PASS |
| lattice half-index 1024.5 / 1025.5 | 1024 / 1026 | PASS |
| force role-window or shoulder closure contact | `HOLD_ROLE_WINDOW` | PASS |
| omit cut-hull corner in robust basin interval | verifier mismatch/HOLD | PASS |
| omit reference self-width or one grid from `E_det` | verifier mismatch/HOLD | PASS |
| `b=4q_tau`, `8q_tau`, `9q_tau` | HOLD, `q_tau`, `q_tau` | PASS |
| delete one family member | alpha/beta count mismatch | PASS |
| count contrast marginals as independent assertions | not the frozen 68 | PASS |
| `(8.0m,8.0m,9.0m)` / `(8.1m,8.0m,9.0m)` | PASS / `HOLD_N_CAP` | PASS |
| change control, pool, trajectory, block, or chunk index | distinct domain/ID | PASS |
| allow F1-B to alter F1-A-selected window | `HOLD_NO_REFIT_VIOLATION` | PASS |
| choose point path A versus B in R113-P0-1 | must be unique | **FAILS SPEC** |
| omit versus placeholder self-digest field | must be unique | **FAILS SPEC** |
| Philox4x32-7 versus Philox4x32-10 | must be unique | **FAILS SPEC** |
| alternate lowercase hex spelling | reject noncanonical spelling | **UNSPECIFIED** |
| stale hash + negative zero + null array | one fixed primary/order | **UNSPECIFIED** |
| DKW equality contact | strict HOLD/failure | **WORDING CONFLICT** |

## 7. Closure gate for a revised selector

Pinning into F0 v2 may be reconsidered only after all of the following are
frozen without reading positive-budget F1 or MC values:

1. one byte-addressed central point-state/projection rule with fail-closed
   coherence and no repair search;
2. a non-circular payload-core/envelope hash domain;
3. a complete Philox4x32-10 transform, known-answer tests, kernel/spec identity,
   and later draw-consumption contract;
4. exact rational constants, canonical float/string/JSON acceptance, and a
   total HOLD/secondary/stub order;
5. a pre-F1 test-key-set hash;
6. strict DKW contact and tagged right-censor conventions;
7. a canonical producer special-function algorithm plus a sound independent
   verifier contract; and
8. an implementation, schema, synthetic/mutation ledger, byte-identical
   replica result, and independent PASS at pinned hashes.

The repaired upstream F0/F1 dependencies from Round 108 remain separate hard
gates.  Closing this audit does not accept them and does not authorize F1.

```text
PIN INTO F0 v2       = HOLD
AUTHORIZED NEXT STEP = science-free selector v2 repair and implementation only
F1-A / F1-B          = NOT AUTHORIZED
F2 / MONTE CARLO     = NOT AUTHORIZED
MANUSCRIPT CHANGE    = NONE
```
