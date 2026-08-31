# Round 106: independent re-audit of the repaired modal-certificate route

Date: 2026-07-14  
Role: independent theorem, numerical-evidence, and release-boundary reviewer  
Decision: **HOLD AS A THEOREM-READY OR POSITIVE-B ARTEFACT / GO TWO TEXT REPAIRS AND FORMAL SELECTOR-CERTIFICATE FREEZE**  
Open findings: **P0 = 0, P1 = 3, P2 = 0**

## 1. Scope, reviewed bytes, and execution boundary

This audit reviewed but did not edit
`notes/modal_certificate_theory_and_prr_redirect.md`, whose SHA-256 was

```text
84b818ff4c3757d92eb32e6a1ab64c4e916ca42e52fdcfc725ba5b5c05bd5726
```

It compared the repaired note line by line with
`audits/round_103_modal_certificate_theory_independent_attack.md`, SHA-256

```text
62c12b4d99b4d7b2e03fbabaefce03514892f67565069a79588350f3c288b5bc
```

and inspected the current exploratory producer
`code/modal_certificate_lp_poc.py`, SHA-256

```text
4920411d65f85653cdec16da206a19d7a8eb42610b6d01936ceae41ec3a6ae6e
```

No positive-budget generator, killed semigroup, finite-volume allocation
grid, allocation-v6 row, Monte Carlo trajectory, or positive-budget output was
opened or run.  The only scientific computation was a read-only rerun of the
already established `B=0` free-exposure kernel.  The only workspace write is
this audit report.

## 2. Executive result

The repaired note closes the two Round-103 stop-ship scientific errors in
substance:

1. The new Theorem 3.1 supplies the previously missing full
   box-and-complement derivative certificate, and Corollary 5.2 now explicitly
   rejects partial at-least/local-box certificates.
2. The off-lattice process is now restricted to positive window contrasts,
   survival, and event-basin probabilities.  Exact topology and absence of
   extra roots remain deterministic interval claims.

The core mathematics is now sound: Theorems 2.1, 2.2, 3.1, the monotone
`B_cert` transfer, and Theorem 5.1 all survive adversarial checking.  The fold
Jacobian and its determinant are algebraically correct.

It is nevertheless premature to say that every Round-103 issue is closed.
Two theorem-level wording defects remain, and the publication-grade selector
and full-window interval artefact still do not exist.  These do not require a
new scientific idea or any positive-budget run.  They require two small note
repairs followed by the already proposed fail-closed freeze.

## 3. Round-103 closure ledger

| Round-103 finding | Round-106 status | Reason |
|---|---|---|
| P0.1 partial certificate used for discriminant crossing | **CLOSED IN SUBSTANCE; residual P1 wording below** | Theorem 3.1 covers every box and every complement gap; Corollary 5.2 excludes partial certificates. |
| P0.2 Monte Carlo assigned exact topology | **CLOSED** | Sections 7 and 9 restrict off-lattice claims to positive estimands and explicitly prohibit exact topology/absence claims. |
| P1.1 Theorem 2.1 implied an isolated/strict mode | **CLOSED** | It now states non-strict extrema and explicitly allows degeneracy, nonisolation, and flat platforms. |
| P1.2 Theorem 5.1 domain and compactness proof | **CLOSED** | The relative-open/extension hypothesis, accumulation proof, endpoint neighborhoods, IFT boxes, and compact-complement exclusion are present. |
| P1.3 `B_cert` and transfer margins underspecified | **CLOSED** | Raw box, gap, and uniform curvature margins plus monotone bounds on `[0,B_max]` are used; local-only fallback is explicit. |
| P1.4 selector and interval evidence not frozen | **OPEN BY DESIGN** | The note correctly makes this a pre-positive-budget gate, but no compliant implementation/result/audit chain yet exists. |
| P1.5 PRR significance conditional | **OPEN BY DESIGN** | The note correctly conditions the PRR claim on prospective same-budget finite-`B` and independent-method evidence. |
| P2.1 malformed LP LaTeX | **CLOSED** | The malformed token is gone and `rho` is no longer constrained nonnegative in the mathematical LP. |
| P2.2 exploratory reporting incomplete/ambiguous | **CLOSED** | Raw margins, the bimodal valley ratio, grid/configurations, and the non-independent/non-interval limitations are now stated. |

Thus six findings are fully closed, one central repair is correct in substance
but needs a terminology fix, and two evidence/publication gates remain
deliberately open.  The correct status is not “all solved”; it is “theory core
repaired, formal evidence chain not yet built.”

## 4. Requested theorem checks

### 4.1 Theorem 2.1: PASS

For an odd--even interval `[a,b]`, `G'(a)>0` excludes `a` as a maximizer and
`G'(b)<0` excludes `b`.  The extreme-value theorem therefore gives an interior
non-strict maximizer.  The negative--positive case gives an interior
non-strict minimizer.  Disjoint open intervals make the selected extrema
distinct.  The revised statement no longer promotes this to isolation,
strictness, nondegeneracy, robustness, or exact topology.

### 4.2 Theorems 2.2 and 3.1: PASS

Uniform strict curvature makes `G'` strictly monotone in every root box;
opposite endpoint signs then give one and only one nondegenerate typed root.
The ordered closed gaps cover the remainder of the declared window, including
both time endpoints.  A strict signed derivative margin on each gap excludes
all additional roots, including even-multiplicity and boundary roots.  The
box and gap endpoint signs are compatible for an alternating peak/valley
list.  Nonnegative weights make both box-curvature and gap-derivative interval
bounds affine in the allocation.

### 4.3 LP formulation: PASS AS MATHEMATICS, HOLD AS AN ARTEFACT

After certification that every row scale is positive, the displayed primary
LP is feasible with `rho` free and has a finite optimum over the compact
simplex.  A positive exact optimum gives the stated at-least certificate; a
nonpositive optimum does not.  Lexicographic minimization over the compact
primary-optimal face is a valid deterministic tie-break in principle.

The current exploratory producer is not that future selector.  In particular,
it still imposes `rho >= 0`, maps every solver failure to one generic reason,
uses the solver-native primary optimizer, and carries no lexicographic
secondary LPs, certified primal/dual positivity enclosure, or outward-rounded
box-and-complement certificate.  This is consistent with the note's explicit
“exploratory only” label, but it means Round-103 P1.4 remains an actual release
gate rather than a completed repair.

Before any positive-budget output, the formal selector must freeze at least:

- the exact scale/checkpoint/floor bytes and solver/environment/options;
- unrestricted-`rho` failure semantics distinguishing interval infeasibility,
  nonpositive optimum, and rigorously positive optimum;
- the exact sequential secondary-LP tie-break, including how the certified
  primary optimum is fixed in each secondary problem;
- independently reconstructed primal/dual residuals and a positivity
  certificate robust to binary64 tolerance; and
- outward-rounded simultaneous box-curvature and full-complement derivative
  enclosures, with append-only result and independent audit.

### 4.4 Positive-budget transfer and `B_cert`: PASS

The revised transfer uses raw physical derivative units, not the normalized LP
objective, and uniform interval curvature rather than curvature sampled at a
floating-point root.  Exact topology requires the complement margin; without
it the note explicitly falls back to local box persistence.  Defining
`B_cert` through every `beta` below `b` is valid for arbitrary registered upper
bounds, and endpoint checking is valid for the declared monotone bounds.  The
strict conclusion only for `0 < B < B_cert` correctly avoids making an
unsupported endpoint claim.

### 4.5 Theorem 5.1: PASS, with one terminology repair needed downstream

The revised relative-open/extension hypothesis is adequate for the implicit
function theorem.  Outside the interior discriminant and endpoint set,
infinitely many stationary roots would accumulate in compact `I`; an endpoint
accumulation enters `E_B`, while an interior accumulation enters `D_B`.
Therefore the list is finite.  Endpoint neighborhoods, simple-root IFT boxes,
and a positive minimum of `|F_t|` on their compact complement exclude births,
deaths, and boundary crossings locally.  Pullback along a path then preserves
the discrete number/type signature.

### 4.6 Fold Jacobian: algebra PASS, regularity hypothesis FAIL

With scalar coordinate `lambda` along an allowed tangent `h`, the Jacobian is

```text
[[F_tt,  D_h F_t ],
 [F_ttt, D_h F_tt]],
```

so at `F_t=F_tt=0` its determinant is indeed
`-D_h F_t * F_ttt`.  The stated nonzero factors are the standard transverse
fold conditions for roots of `F_t`.

However, Section 5 assumes only joint `C^2` regularity.  That does not supply
`F_ttt` or the mixed derivative in the displayed Jacobian.  Immediately before
the fold paragraph, add an explicit local `C^3` hypothesis (or the precise
existence and continuity of `F_ttt`, `D_h F_t`, and `D_h F_tt`).  This is P1.2
below: the formula is right, but it is undefined under the section's current
hypotheses.

### 4.7 Off-lattice claim boundary: PASS

The proposed campaign freezes positive contrast, survival, and event-basin
probability estimands and explicitly says “never an absence or exact-root
estimand.”  The maximum future claim assigns exact finite-window topology to
deterministic interval calculations and only positive event-law compatibility
to the unbounded off-lattice process.  The prohibited-promotion list separately
forbids off-lattice derivative, singularity, extra-root-absence, and exact-
topology claims.  Round-103 P0.2 is therefore fully closed.

## 5. Remaining findings

### P1.1 — “stationary list” is not the invariant proved by Theorem 5.1

The theorem correctly states that the **number and ordered maximum/minimum
types** are constant.  But its proof says the “complete ordered root list” is
locally constant, and Corollary 5.2 assumes two allocations have different
“complete stationary lists.”  Root locations normally move continuously and
are not locally constant.

The literal reading has a simple counterexample.  On `I=[0,3]`, let

```text
F_w(t) = -(t-w)^2,    1 < w < 2.
```

Then `D_B` and `E_B` are empty, every allocation has one nondegenerate maximum,
and the whole parameter interval is one path component.  Nevertheless the
numerical stationary list is `{t=w}`, so any two allocations have different
root locations without crossing a discriminant.

The heading makes the intended topological meaning clear, so this is not a new
P0 conceptual failure.  It is still a theorem-level ambiguity that should be
removed.  Define the discrete signature, for example

```text
Sigma(w) = (N(w); sign F_tt(t_1(w),w), ..., sign F_tt(t_N(w),w)),
           t_1(w) < ... < t_N(w),
```

say that `Sigma` is locally/pathwise constant, and require
`Sigma(w_0) != Sigma(w_1)` in Corollary 5.2.  Do not call the numerical root
times locally constant.

### P1.2 — fold paragraph lacks its required `C^3` hypothesis

The determinant is correct, but `C^2` does not define `F_ttt`.  Add local joint
`C^3` regularity or explicitly state the necessary third and mixed derivative
hypotheses before the fold conditions.

### P1.3 — the formal selector/full-window interval chain is still missing

This is the surviving Round-103 P1.4 gate, not a contradiction in the revised
note.  The note now specifies what must be built and correctly refuses to treat
the exploratory producer as publication evidence.  Until the unrestricted-
`rho` selector, deterministic tie-break, certified optimum sign, full-window
outward enclosures, canonical result, and independent replay exist, no exact
one-/two-/three-mode control is frozen and no positive-budget execution is
authorized.

Round-103 P1.5 is likewise an evidence condition rather than a further note
defect: PRR significance still depends on the prospective same-budget
finite-parameter realization, independent positive-event validation, and a
current literature/novelty audit.

## 6. Read-only `B=0` reconstruction

Using repository Python `3.12.13`, NumPy `2.5.1`, SciPy `1.18.0`, and only the
free-exposure producer, the rerun returned

```text
PASS_EXPLORATORY_FREE_EXPOSURE_MODAL_CERTIFICATE
positive_budget_evaluated = False
```

The LP weights and normalized margins matched the note:

| target | weights | normalized margin | smallest raw margin |
|---|---|---:|---:|
| m1 | `(0.03, 0.9100000000000001, 0.03, 0.03)` | `0.8809904119598448` | `0.09879189274140476` |
| m2 | `(0.5420243013882049, 0.03, 0.048245050837663034, 0.37973064777413196)` | `0.32540424848060423` | `0.0018180658405830398` |
| m3 | `(0.4016285358628774, 0.2761816314605931, 0.03, 0.2921898326765295)` | `0.13616273641487345` | `0.0014249146622736185` |

The primary-kernel valley ratios were

```text
m1: none
m2: 0.18692660856554522
m3: 0.7623155612510425, 0.7619538984631168
```

Across coarse/primary/fine quadrature, the maximum displayed root-time spread
was `4.654054919228656e-13` and the maximum scaled-curvature spread was
`1.2807532812075806e-12`.  This reconfirms the exploratory arithmetic only.  It
does not exclude even roots, provide interval enclosures, certify a positive
budget, or change any release gate.

## 7. Final decision and next authorized step

```text
Round-103 P0 scientific defects       = CLOSED IN SUBSTANCE
Theorem 2.1 non-strict statement      = PASS
Theorem 3.1 box plus complement       = PASS
LP mathematics                        = PASS
LP frozen implementation              = HOLD
B_cert raw/monotone transfer          = PASS
Theorem 5.1 topology proof            = PASS
Corollary 5.2 terminology              = REPAIR REQUIRED
fold determinant                       = PASS
fold regularity hypothesis             = REPAIR REQUIRED
off-lattice claim boundary             = PASS
B0 exploratory arithmetic              = REPRODUCED
PRR-ready evidence package             = HOLD
positive-budget execution              = NOT AUTHORIZED
P0                                      = 0
P1                                      = 3
P2                                      = 0
```

The next authorized action is narrow and deterministic:

1. replace “root/stationary list is locally constant” by the explicit discrete
   topology signature in Theorem 5.1 and Corollary 5.2;
2. add the local `C^3` fold hypothesis;
3. freeze, test, serialize, and independently audit the exact selector plus
   full-window interval certificate; and
4. only after that audit passes, write a separate positive-budget manifest for
   review.  This report does not authorize executing it.

No cusp revival is needed.  After the two text repairs, this is a credible and
more general PRR route, but PRR quality remains conditional on the prospective
evidence chain rather than on the successful exploratory `B=0` table.
