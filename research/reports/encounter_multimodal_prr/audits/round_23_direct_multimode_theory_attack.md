# Round 23 direct physical multimode theorem attack

Date: 2026-07-13  
Scope: `notes/direct_physical_multimode_theorem.md`  
Method: equation-by-equation adversarial audit, followed by a repair restricted
to that note

## 1. Final verdict

### Mathematical verdict

**PASS after repair.**  The original 307-line draft had the right mechanism
but was still a proof sketch: it did not define the relative stochastic
process whose contact-tail derivatives it used, it invoked a dimension range
larger than the existing Doi theorem, and several dominance and mass claims
were asserted without their exact hypotheses.

The repaired note, SHA256
`7493499883ba41ce043c3535e1ca3d6c7a4c5de0cce9e575e261b4f8da9c2974`,
now proves the following bounded result:

> For every prescribed fixed finite mode count and target-time set satisfying
> the declared contact-interior condition, there is a mode-count-dependent,
> epsilon-dependent normalized OU slab family.  For sufficiently small fixed
> epsilon, and then sufficiently small positive budget, its exact physical-2D
> or physical-3D quotient Doi density has at least the prescribed number of
> nondegenerate local maxima.

It does not prove arbitrary mode count in one fixed configuration, exactly the
global number of modes, a general localized-patch theorem, or observable
finite-budget modes.

### Severity ledger

Before repair:

| Severity | Count | Main issue |
|---|---:|---|
| P0 | 2 | Undefined relative process/contact derivative theorem; unsupported `d >= 2` Doi-transfer range |
| P1 | 7 | Missing cut-locus, weighted-law, C2, dominance, weight-set, peak, and mass hypotheses |
| P2 | 4 | Ambiguous arbitrary-mode title, dependencies, notation, and exposure-vs-mass wording |

After repair:

| Severity | Open count |
|---|---:|
| P0 | 0 |
| P1 | 0 |
| P2 | 0 |

The remaining finite-budget, observability, cusp, localized-geometry, and 3D
numerical obligations are scientific promotion gates, not defects in the
bounded existence theorem.

## 2. Gaussian OU and resource normalization

### 2.1 Midpoint variance: PASS

For

```text
dZ = -gamma (Z-zbar) dt + epsilon sqrt(D0) dW,
Var(Z0) = epsilon^2 s0^2,
```

the exact variance is

```text
epsilon^2 [s0^2 exp(-2 gamma t)
 + D0/(2 gamma) (1-exp(-2 gamma t))].
```

Equations (2.1)--(2.3) have the correct factor `D0/(2 gamma)`.

### 2.2 Catalyst and convolution: PASS

The Gaussian catalyst in (2.7) integrates to one on the longitudinal line.
Multiplication by `W^(-(d-1))` makes its full centre-space integral one.
Consequently the simplex mixture in (2.8) has installed centre-space amount
exactly `B` for every weight vector.

Convolving a catalyst variance `epsilon^2 rho^2` with the midpoint variance
`epsilon^2 s^2(t)` gives `epsilon^2 S^2(t)` with
`S^2=s^2+rho^2`.  The prefactor and exponential in (2.11) are therefore exact;
no square root, factor two, or transverse-volume factor is missing.

The quotient killing is now written explicitly as the product of the true
contact indicator and the centre-space catalyst.  This closes the original
ambiguity between an installed catalyst field and the Doi killing operator.

## 3. Weighted-space initial-law audit

The repair defines the relative quotient SDE rather than referring to an
unspecified deterministic trajectory.  Its longitudinal stationary variance
is

```text
2 epsilon^2 D0/gamma,
```

while the midpoint stationary variance is

```text
epsilon^2 D0/(2 gamma).
```

For a one-dimensional Gaussian initial density with variance `v0`, the
integral of `q0^2/pi` is finite exactly when `v0` is smaller than twice the
stationary variance.  This gives

```text
s0^2 < D0/gamma,
u0^2 < 4 D0/gamma,
```

as stated in (2.6).  Means affect only linear terms and do not change these
strict quadratic integrability conditions.  The wrapped transverse Gaussian
is in `L2` relative to the uniform torus invariant density for every fixed
positive epsilon.

The note correctly warns that these facts are pointwise in epsilon.  No
uniform weighted-space norm is used when epsilon tends to zero.

## 4. Contact-factor audit

### Original defect

The draft claimed differentiated Gaussian-tail estimates without defining the
relative SDE, its covariance, the torus convention, or the distance from the
cut locus.  That was a P0 completeness failure: many different relative
processes share the same informal deterministic path but not the same time
derivative bounds.

### Repaired result: PASS

The note now fixes the exact equal-diffusivity quotient, a wrapped Gaussian
initial law, `0 < a < W/2`, and the minimum-image contact ball.  On the fixed
positive-time neighborhoods, the relative law has mean `r_*(t)` and covariance
`epsilon^2 Sigma_R(t)`, with explicitly stated longitudinal and transverse
coefficients.

The contact-interior margin makes the complement of the contact ball at least
distance `eta` from the Gaussian mean.  Differentiating the Gaussian image
series in time produces only polynomial epsilon factors, while integration on
that separated complement produces `exp(-q/epsilon^2)`.  Uniform Gaussian
summability justifies termwise differentiation.  Thus Lemma 3.1 supports every
fixed derivative order and, in particular, the required C2 convergence to
one.

The note also repairs the earlier overgeneralization: if the contact factor
instead converges to a positive nonconstant function, that value must multiply
the local peak coefficient and enter the balancing weights.

## 5. Local C2 asymptotics

Define the rescaled functions

```text
h_epsilon(y) = [c_j-mu(t_j+epsilon y)]/epsilon,
S_epsilon(y) = S(t_j+epsilon y).
```

The OU mean is smooth and has nonzero derivative because `z0 != zbar`.
Taylor expansion gives C2 convergence

```text
h_epsilon -> -mu'(t_j) y,
S_epsilon -> S(t_j) > 0.
```

Smooth composition with the exact Gaussian formula proves

```text
epsilon^(r+1) partial_t^r a_j(t_j+epsilon y)
 -> A_j^(r)(y),  r=0,1,2.
```

The product rule and Lemma 3.1 prove the same limit for the full exposure
clock.  Because the mode count is fixed and finite, one common local radius
can be chosen so every limiting Gaussian has negative curvature there.  The
repaired note makes this common-radius and interval-containment step explicit.

This is a genuine local C2 asymptotic, not merely pointwise convergence.

## 6. Cross-channel and dominance audit

Distinct target times map to distinct catalyst centres under the monotone OU
mean.  On the shrinking window about target `j`, every other centre remains a
fixed positive distance away.  Two time derivatives of the exact Gaussian
clock add only a fixed polynomial in `epsilon^(-1)`, so the cross-channel
terms are exponentially smaller than the own-channel slope and curvature
margins.

The repaired proof no longer invokes an unnamed channel-dominance lemma.  It
writes the three strict inequalities for each mode interval:

- positive derivative at the left endpoint;
- negative derivative at the right endpoint; and
- negative second derivative throughout.

Strict curvature makes the derivative strictly decreasing, so there is
exactly one critical point and it is a nondegenerate maximum.  On each compact
gap, the derivative signs exclude both endpoints as minimizers; the extreme
value theorem therefore gives at least one interior local minimum.  Its
nondegeneracy is not claimed.

The lower-weight set is now explicitly required to be nonempty.  The
dominance constants are uniform over that compact set but not in the mode
count.

## 7. Weak-budget transfer

For each fixed positive epsilon:

- the Gaussian catalysts are bounded multiplication operators;
- the initial law lies in the declared weighted density space;
- the weight set is compact and finite dimensional; and
- all certified windows lie inside one fixed positive-time interval.

The existing unbounded mixed-jet theorem therefore gives uniform C2
convergence of `f_B/B` to the free exposure mixture as `B` tends to zero.
The strict slope and curvature margins persist for a positive
`B_0(epsilon)`, uniformly over the weight set.

The order of limits is essential and is now repeated in the theorem and its
scope section:

```text
fix finite m and target times
-> choose sufficiently small epsilon
-> freeze that geometry
-> choose 0 < B < B0(epsilon).
```

The catalyst supremum norm and weak-budget constants deteriorate as epsilon
shrinks.  No interchange or joint uniform limit is claimed.

## 8. Dimension and geometry scope

The original statement said every fixed `d >= 2` while invoking a PDE theorem
stated for physical dimensions 2 and 3.  That transfer range was unsupported
as written.

The repaired theorem is restricted to physical `d=2,3`, exactly matching the
available unbounded semigroup theorem.  It also states that the construction
uses a longitudinal catalyst slab uniform in transverse common-centre
coordinates.  It is not a theorem for localized disks/spheres or arbitrary
spatial arrangements.

The direct free-clock algebra is dimension-stable, but extending the formal
Doi theorem beyond dimensions 2 and 3 would be a separate statement and is
not needed for this manuscript.

## 9. Peak weights and local event mass

Under the proved contact limit `c_d,epsilon -> 1`, the limiting peak
coefficient is

```text
H_j = 1/[W^(d-1) sqrt(2 pi) S(t_j)].
```

The normalized weights `w_j = S(t_j)/sum_i S(t_i)` therefore make every
leading product `w_j H_j` equal.  Strict local concavity and exponential
cross-channel suppression imply both the rescaled peak-location limit and the
actual certified-peak height limit in (5.6); the result is not based only on
evaluating the clock at the nominal target time.

Changing variables `t=t_j+epsilon y` proves the exact exposure-area limit in
(5.7).  The note now calls this an exposure area, not probability mass.  Only
after multiplication by the Doi budget does it become event mass:

```text
integral f_B = B integral G + O(B^2)
```

for each fixed epsilon.  The remainder and the observability conclusion are
not uniform in epsilon, as required.

## 10. Claim and novelty boundary

The title and theorem have been changed from an ambiguous “physical
arbitrary-mode theorem” to an any-fixed-finite-mode theorem for
epsilon-dependent slab families.  The following claims are now explicit:

- geometry and epsilon threshold depend on the prescribed finite mode count
  and target times;
- at least the prescribed local maxima are certified, but extra extrema are
  not excluded;
- the relative path is deliberately kept inside contact near the peaks;
- the theorem proves conserved-budget realizability, not an allocation-driven
  fold or cusp; and
- an observable overlap between a lower budget floor and `B_0(epsilon)` is
  not proved.

This matches the Round 20 novelty boundary and avoids claiming a fixed
configuration with arbitrary mode count.

## 11. Manuscript decision

**YES, as a supporting analytical theorem after using the repaired wording.**

Safe manuscript statement:

> Within the exact OU slab quotient in physical dimensions two and three,
> every prescribed fixed finite mode count admits a mode-count-dependent,
> epsilon-dependent family of normalized static catalyst slabs.  For
> sufficiently small fixed epsilon and then sufficiently small positive
> installed budget, the exact Doi reaction-time density has at least that many
> nondegenerate local maxima on the prescribed positive-time interval.

Required adjacent caveats:

1. slab symmetry, not arbitrary localized configurations;
2. sequential epsilon-then-budget limits;
3. no uniformity in the mode count or epsilon;
4. no exact global mode count;
5. no finite-budget observability threshold;
6. no implication that one frozen configuration supports arbitrary mode
   count; and
7. no replacement for the finite-parameter 2D cusp and 3D numerical gates.

With those boundaries, the theorem is stronger than a reduced-clock design
lemma because it reaches a positive-budget continuum Doi operator.  It should
not replace the finite-parameter spatial bifurcation result as the PRR physics
headline.
