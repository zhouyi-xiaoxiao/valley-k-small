# Sub-Markov semigroup envelopes for a complete finite-window mode certificate

Date: 2026-07-13  
Status: **method derivation and historical-control feasibility diagnostic only;
GO-DESIGN / HOLD-IMPLEMENTATION / no new-control positive-budget execution**

## 1. Purpose and boundary

The repaired modal-certificate route requires more than a dense sign-changing
root scan.  To claim exactly one, two, or three modes on a declared window, the
deterministic finite-volume calculation must:

1. isolate one simple extremum in every predeclared root box; and
2. exclude every extra stationary point, including an even-multiplicity root,
   on the complement.

This note derives a practical semigroup envelope for those two tasks.  It does
not evaluate any of the three new LP-selected controls at positive budget.  The
only numerical values below use the already published-in-repository historical
positive-budget control as a method diagnostic.  They are not new scientific
evidence and must not be used to choose F1 controls, boxes, or gates.

## 2. Exact contraction inequality

Let (Q) be the finite-volume **row** killed generator.  Thus its off-diagonal
entries are nonnegative and its row sums are nonpositive.  Consequently

\[
 S(t)=e^{tQ}
\]

is entrywise nonnegative and row-substochastic, so

\[
 \|S(t)\|_\infty\le1,
 \qquad
 \|S(t)^T\|_1\le1.
\]

The column probability state obeys (p'(t)=Q^Tp(t)).  For the normalized
positive-budget density write

\[
 F(t)=p(t)^Tk,
\]

where (k\ge0) is the killing field per unit installed budget.  The physical
density is (f(t)=BF(t)).  For every integer (r\ge0),

\[
 F^{(r)}(t)=p(t)^TQ^rk.
\]

Fix an anchor time (a\), put

\[
 z_r(a)=(Q^T)^rp(a),
 \qquad
 M_r(a)=\|k\|_\infty\,\|z_r(a)\|_1.
\]

Because (Q^T) commutes with its semigroup, for every (s\ge0),

\[
 F^{(r)}(a+s)=k^TS(s)^Tz_r(a).
\]

The sub-Markov contraction therefore gives the exact bound

\[
 \boxed{\ |F^{(r)}(a+s)|\le M_r(a)\quad(s\ge0).\ }
\]

No detailed balance, eigendecomposition, continuum assumption, or root scan is
used.  Moreover (M_r(a)) is nonincreasing in the anchor time in exact
arithmetic because (z_r(a+s)=S(s)^Tz_r(a)).

## 3. Interval sign and curvature enclosures

Suppose a numerical evaluator supplies certified scalar enclosures

\[
 F^{(r)}(a)\in
 [\widehat F^{(r)}(a)-\varepsilon_r(a),
  \widehat F^{(r)}(a)+\varepsilon_r(a)]
\]

and a certified upper bound (widehat M_{r+1}(a)\ge M_{r+1}(a)).  The mean
value theorem gives, for (0\le s\le h\),

\[
 F^{(r)}(a+s)\in
 [\widehat F^{(r)}(a)-\varepsilon_r(a)-h\widehat M_{r+1}(a),
  \widehat F^{(r)}(a)+\varepsilon_r(a)+h\widehat M_{r+1}(a)].
\]

This yields two fail-closed tests:

- **complement sign:** for a declared sign (q\in\{-1,+1\}), certify
  (qF'(t)>0) throughout ([a,a+h]) if
  
  \[
  q\widehat F'(a)-\varepsilon_1(a)-h\widehat M_2(a)>0;
  \]

- **root-box curvature:** certify a peak box by
  
  \[
  \widehat F''(a)+\varepsilon_2(a)+h\widehat M_3(a)<0,
  \]
  
  and a valley box by the corresponding strictly positive lower bound.

Together with separately enclosed derivative signs at both endpoints of every
root box, these tests implement the full box-and-complement theorem.  They
exclude even roots because the derivative is bounded strictly away from zero
on every complement interval.

Higher-order Taylor enclosures may reduce the number of anchors, but they are
optional.  The first-order bounds above should be the reference implementation
because their proof depends only on semigroup contraction.

## 4. Why the tempting reversible spectral bound is rejected

The cell-centred Scharfetter--Gummel birth-death factors satisfy detailed
balance.  For the linear OU drift, the face-rate ratio reproduces the exact
cell-centre Gaussian stationary ratio; periodic transverse diffusion is
uniform, tensor products remain reversible, and diagonal killing preserves
self-adjointness after the detailed-balance similarity transform.

This formally gives

\[
 |F^{(r)}(t)|
 \le
 \|D_\pi^{1/2}k\|_2
 \|D_\pi^{-1/2}p_0\|_2
 \left(\frac{r}{et}\right)^r.
\]

It is unusably conservative for the current reflected boxes because the
localized initial law lies far into the stationary OU tail.  A read-only
diagnostic using the already known historical control returned the following
prefactors:

| cubic cells | spectral prefactor |
|---:|---:|
| 33 | `4.264993225682382e8` |
| 65 | `9.329658806883446e8` |
| 113 | `1.909283247781957e9` |

The midpoint detailed-balance residuals were below (2.3\times10^{-15}), so
the failure is conditioning, not a broken symmetry identity.  F0 must not
advertise this global spectral estimate as a usable interval certificate.

## 5. Historical-control magnitude check for the local bound

For the same already known historical control, with (F=f/B), the diagnostic
computed

\[
 M_r(a)=\|k\|_\infty\|(Q^T)^rp(a)\|_1
\]

without changing any scientific output.  Representative values were:

| mesh | anchor (a) | (M_1(a)) | (M_2(a)) | (M_3(a)) |
|---:|---:|---:|---:|---:|
| 33 | 0.5 | 7.370 | 22.442 | 105.892 |
| 33 | 1 | 4.565 | 8.203 | 20.824 |
| 33 | 2 | 2.915 | 3.161 | 4.695 |
| 33 | 3 | 2.228 | 1.821 | 1.991 |
| 33 | 5 | 1.564 | 0.885 | 0.664 |
| 65 | 0.5 | 14.608 | 52.578 | 264.022 |
| 65 | 1 | 9.230 | 19.944 | 58.607 |
| 65 | 2 | 5.921 | 7.947 | 14.127 |
| 65 | 3 | 4.535 | 4.608 | 6.177 |
| 65 | 5 | 3.152 | 2.213 | 2.058 |
| 113 | 0.5 | 16.982 | 69.878 | 407.456 |
| 113 | 1 | 10.572 | 25.852 | 86.143 |

These numbers do not prove that the future F1 matrix is affordable, but they
show that adaptive local intervals are many orders of magnitude sharper than
the rejected stationary-weight spectral bound.  The early window is the
costliest region; F0 must estimate worst-case anchor counts before execution.

## 6. Required numerical enclosure layer

The algebraic contraction is exact, but a binary64 call to `expm_multiply` is
not automatically an interval computation.  A publication certificate needs
an additive error ledger covering:

1. the propagated state (p(a));
2. sparse actions producing (z_1,z_2,z_3);
3. scalar dot products and (L^1/L^\infty) norms;
4. time anchoring and any interpolation; and
5. accumulated error across sequential propagation chunks.

The reference F0 design must choose and independently attack one of these
routes before any F1 run:

- an a posteriori Krylov-residual bound integrated in the contractive
  (L^1) norm, with outward rounding and a separately reproduced scalar
  ledger;
- a uniformization/Fox--Glynn calculation with an explicit Poisson-tail and
  floating-roundoff bound, if its cost is demonstrated feasible; or
- another solver with a mathematically explicit state/observable error
  envelope at least as strong.

Comparing two binary64 meshes, two chunk sizes, or two replicas is a valuable
reproducibility test but is not, by itself, a certified enclosure.  A large ad
hoc safety factor with no derived roundoff/truncation bound is also
insufficient.

For every interval, the machine-readable output must store the anchor, width,
intended sign class, scalar derivative enclosure, (widehat M_2) or
(widehat M_3), final signed margin, and the hashes of the state-error method
and its parameters.  Any uncovered subinterval, nonpositive final margin,
nonfinite value, or error-bound failure returns `HOLD_INTERVAL_CERTIFICATE`.

## 7. Prospective adaptive algorithm

The following order is compatible with a no-refit F0--F1 chain:

1. F0 fixes the time window, root boxes, complement signs, maximum/minimum
   anchor width, minimum interval margin, and error solver **from B=0 and
   method-only evidence**.
2. F1 propagates each frozen control sequentially and attempts the largest
   permitted interval whose signed contraction bound passes.
3. Failed intervals are bisected deterministically down to a frozen minimum
   width; failure there is a scientific HOLD, not permission to move a root
   box or increase a tolerance.
4. Root boxes require enclosed endpoint derivative signs and one curvature
   sign over their full width.  Complement intervals require one strict
   derivative sign over their full width.
5. The union of root boxes and complement intervals is checked exactly against
   the declared window endpoints with no floating gap or overlap.
6. Only after every configuration and every promoted control passes may the
   result be called an exact finite-window deterministic topology.

## 8. Current decision

```text
sub-Markov contraction derivation                 = PASS
orientation for row Q / column p                   = PASS
detailed-balance identity                          = PASS BUT NUMERICALLY USELESS
historical-control local-bound feasibility signal  = PASS AS METHOD DIAGNOSTIC
binary64/Krylov or uniformization error enclosure  = OPEN P0
future-control computational feasibility           = OPEN P1
new-control positive-budget execution               = NOT AUTHORIZED
```

The local contraction route is presently the strongest candidate for the F0
full-window certificate.  It becomes an execution method only after the
numerical enclosure and cost gates receive an independent PASS.
