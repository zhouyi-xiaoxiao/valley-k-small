# Round 49: independent mathematical re-audit of the analytical supplement

Date: 2026-07-14 (Europe/London)

## Scope and independence

This is a fresh, read-only audit of
`manuscript/encounter_multimodal_prr_supplement.tex`.  I did not use the
conclusions of Round 46 or Round 48.  I checked the displayed hypotheses and
formulae directly, inspected the actual companion Lean modules only to verify
the claimed formalization boundary, and built the TeX source in an isolated
temporary directory for layout review.  I did not modify the supplement, the
main manuscript, or any positive-B producer, auditor, manifest, result, or
evidence file.

Audited source SHA-256:

```text
de75e5a37adb83175f27ce8e1e78846c54781a858c4ff5411daab7b12e222278
```

Independent TeX Live build:

```text
12 pages; exit 0
PDF SHA-256: 5112bc8ed97b08a98b93769f7e6d6c91473c6a32615ffaedfb93fd30d95747ca
undefined references/citations: 0
overfull/underfull boxes: 0
```

The only build warnings were the RevTeX default 10-point-size notice and the
standard `nameref` label-definition notice.

## Verdict

- **P0: none found.**
- **Theorem-breaking P1: none found.**  Under the displayed hypotheses, the
  bounded/unbounded semigroup realization, compact-positive-time mixed-jet
  estimate, differentiated contact-tail lemma, and fixed-finite-m lower-bound
  theorem are internally consistent.
- **Release P1: two.**  One headline phrase overstates an at-least-m theorem as
  an exact mode-count realization, and the Lean files named by the supplement
  are not resolvable from this report or the repository root.
- **P2: two.**  The narrow-noise instantiation should state the identification
  `D = epsilon^2 D_0` explicitly, and the evidence-boundary table floats behind
  the bibliography with a large blank region.

This is a pass of the analytical core under its stated, narrow scope.  It is
not a proof of a global mode count, a finite-parameter positive-budget result,
a cusp, a mass floor, a numerical discretization, or the overall PRR claim.

## P1 findings

### P1-1: headline language says “mode count is realized,” but the theorem proves only a lower bound

**Evidence.**  The abstract says that “every prescribed fixed finite mode
count is realized” (source lines 65--69), and the theorem title repeats “Every
prescribed fixed finite mode count” (line 978).  The formal statement instead
certifies exactly one maximum in each of m named intervals and therefore **at
least** m maxima, while explicitly declining an exact global root count (lines
994--998).  The limitations also allow extra early, late, and interstitial
extrema (lines 1110--1114).

**Assessment.**  The proof is not wrong.  The headline is stronger than the
proved proposition in the ordinary reading of “mode count.”  A PRR reader can
reasonably interpret “count m is realized” as “there are exactly m modes.”

**Release condition.**  Before submission, replace the headline wording by an
unambiguous lower-bound claim, for example “every prescribed fixed finite
number of certified modes” or “at least m modes for every fixed finite m.”  Keep
the no-global-count sentence prominent.

### P1-2: the named Lean paths are not self-contained or pinned in this report

**Evidence.**  Lines 1124--1129 name
`FormalLean/Encounter.lean`, `FormalLean/EncounterDesign.lean`, and
`FormalLean/EncounterContinuum.lean`.  None exists at that path relative to
the report or repository root.  The only live copies located by a repository
scan are under
`research/reports/ring_lazy_jump_ext_rev2/code/formal_lean/FormalLean/`:

```text
Encounter.lean          d2c11759c831228eb6641f3944d1d860c34615982d15b883e6d029f0a670e754
EncounterDesign.lean    fa45ceb3c40e7c9769d4f7d6ab5aa1495e89a361c675b89f362dfc11798b8330
EncounterContinuum.lean ae23060be3166c392eab2d8a0a5af5dcd1d3a4adf2a8b912fd8a0c2161e538b4
```

The module headers and existing axiom reports do support the supplement's
scientific boundary: they cover finite/exact algebra only, explicitly exclude
the semigroup, wrapped-Gaussian, root-count, persistence, and catastrophe
bridges, and contain no `sorry` or project-defined postulate.

**Assessment.**  The Lean boundary is honest, but a standalone PRR evidence
package cannot resolve or reproduce the cited modules from the displayed
paths.  This is a provenance/release defect, not a theorem defect.

**Release condition.**  Copy the pinned modules plus their Lean toolchain,
manifest, and regenerated axiom reports into the encounter supplement archive,
or cite the exact repository-relative location and hashes.  Do not describe
Sections S3 or S4 as Lean-verified.

## P2 findings

### P2-1: make the Section S4 diffusion-parameter identification explicit

Section S1 writes the generic free operator with diffusion parameter `D`
(lines 88--96 and invariant density lines 179--195).  Section S4 defines
noise amplitudes `epsilon sqrt(D_0)` and `2 epsilon sqrt(D_0)` (lines 688--713)
and then applies the unbounded theorem at fixed epsilon (lines 1037--1044).
The coefficients agree exactly with the generic operator when

```text
D = epsilon^2 D_0.
```

The displayed invariant variances (lines 727--736) confirm this
identification, so there is no mathematical mismatch.  Stating it in one
sentence would remove a needless inference at the theorem bridge.

### P2-2: evidence-boundary table is visually detached from its discussion

The table declared with `[b]` at lines 1137--1156 is deferred to the bottom of
page 12, after the bibliography, while its explanatory text remains on page
11.  The resulting page has a large blank region and makes the formal boundary
harder to read as a unit.  The mathematics and references render cleanly, but
the final supplement should keep this table near Section S5 and before the
reserved modules/bibliography.

## Formula-by-formula checks

### 1. Bounded/unbounded states, domains, and pairings: pass

- From the displayed invariant density,
  `D_matrix grad(log pi) = (-gamma(z-zbar), -gamma r_parallel, 0, ...)`, so
  the similarity `q = pi u` gives the weighted symmetric generator claimed in
  Eqs. S31--S32.
- On the bounded quotient, the truncated Gaussian is bounded above and below,
  so weighted and unweighted `L^2` are equivalent with condition number at
  most `sqrt(pi_max/pi_min)`.
- On the unbounded quotient, `u -> pi u` is unitary from `L^2(pi dx)` to
  `X_pi = L^2(pi^{-1} dx)`.  The observable pairing is continuous because
  `|integral V q| <= ||V||_{L^2(pi)} ||q||_{X_pi}`.  The survival pairing is
  also continuous because `1` belongs to `L^2(pi)`.
- Bounded multiplication by the catalyst preserves the generator domain.
  Positivity/mass decrease is claimed only on the real nonnegative slice, not
  for the complex Cauchy auxiliaries.  The source correctly restricts all time
  jets to `[tau,T]` with `tau > 0`.
- For the Section S4 Gaussian initial law, direct exponent comparison gives
  precisely `s_0^2 < D_0/gamma` and `u_0^2 < 4 D_0/gamma`; equality still
  diverges.  The wrapped factor is square-integrable for each fixed epsilon.

### 2. Sensitivity and Dyson/Cauchy mixed jets: pass

- The multi-index state recursion has the required multiplicity `beta_i`, and
  the observable recursion includes the direct derivative of the affine
  catalyst.  The first- and second-control formulae therefore do not omit the
  observable terms.
- The ordered Dyson simplex has volume `1/n!`.  On `Re z > 0`, every free
  factor is contractive; the bounded-space similarity contributes one
  condition-number factor because multiplication by `V` commutes with
  multiplication by `pi`.
- For `t in [tau,T]`, the radius-`tau/2` disk lies in `Re z > 0` and satisfies
  `|z| <= 3T/2`.  The radius-`delta` control polydiscs lie in the declared
  `2 delta` tube.  Cauchy therefore supplies exactly the factors
  `r! (2/tau)^r` and `alpha! delta^{-|alpha|}` in Eq. S37.
- The linear constant follows from
  `exp(Bx)-1 <= B x exp(B_max x)`.  Removing the `n=0,1` Dyson terms gives the
  stated `B^2 x^2 exp(x)/2` remainder.  The constants are not claimed uniform
  as epsilon tends to zero or on times of order `1/B`.

### 3. Fold tangent, cusp plane, Jacobian, and Weyl dimensions: pass

- A fold uses one frozen unit tangent and the square map from `(t,lambda)` to
  `(F_t,F_tt)` in `R^2`.
- A cusp uses a frozen `E in R^{(J-1) x 2}` with `E^T E=I_2`; hence it requires
  at least two independent budget tangents, which the text states.  The map
  from `(t,xi_1,xi_2)` to `(F_t,F_tt,F_ttt)` is square in `R^3`.
- At a cusp root, the first column of the Jacobian is
  `(0,0,F_tttt)^T`.  Expansion along that column gives
  `det DH = F_tttt det(R^E)` with the positive sign shown in Eq. S56.
- `R^E` is `2 x 2`, so `sigma_2` is the correct smallest singular value.
  Weyl gives `sigma_2(R_B^E) >= sigma_2(R_0^E)-||R_B^E-R_0^E||_2` on the same
  frozen ball.  The text correctly distinguishes normalized response from the
  raw response `B R_B^E`.

### 4. Wrapped-Gaussian contact tail: pass under the contact-interior hypothesis

- The covariance coefficients in Eqs. S73--S74 follow from the stated OU and
  Brownian SDEs and are uniformly positive and smooth on the compact positive
  time set.
- The reverse triangle inequality gives a geodesic distance at least `eta`
  between the deterministic mean and the contact complement.  Because
  `a < W/2`, the contact boundary avoids the torus cut locus.
- Every lattice lift is at least the minimum geodesic distance from the mean.
  Differentiating a Gaussian image introduces only polynomial powers of
  `epsilon^{-1}` and displacement; uniform covariance bounds retain a Gaussian
  exponent.  Summation over the wrapped images is uniformly Gaussian-summable.
- Normalization gives zero integral for each positive time derivative of the
  density, so derivatives of contact probability can be converted into tail
  integrals.  The polynomial prefactor is absorbed into
  `C_r epsilon^{-N_r} exp(-q/epsilon^2)`.  No tail statement is made without
  the fixed contact-interior margin.

### 5. Fixed-finite-m construction, uniformity, and quantifier order: pass as an at-least-m theorem

- On `t=t_j+epsilon y`, the own channel is `epsilon^{-1} A_j(y)` through two
  scaled time derivatives.  Endpoint slopes are bounded below at order
  `epsilon^{-2}` and curvature is bounded above by a negative constant of
  order `epsilon^{-3}`.
- Distinct target centers have a fixed separation.  Cross-channel derivatives
  are therefore a polynomial in `epsilon^{-1}` times
  `exp(-q_ij/epsilon^2)`, which is negligible against every own-channel
  polynomial margin.
- Fixed m and `w_j >= w_min` make the same small-epsilon choice uniform over
  all intervals and all weights in the compact set.  Strict concavity plus
  endpoint slope signs gives exactly one nondegenerate maximum in each named
  interval.  Endpoint derivative signs on each intervening closed gap force
  at least one interior local minimum, not necessarily a nondegenerate one.
- The quantifier order is correctly nested:
  `exists epsilon_0; for each fixed epsilon, exists B_0(epsilon); for all
  smaller positive B and all w`.  The weak-reaction constants may depend on
  that fixed epsilon, and the text explicitly forbids exchanging the limits.
- The theorem is mode-dependent and geometry-dependent and only guarantees at
  least m global maxima.  It neither excludes other extrema nor proves one
  fixed geometry supports arbitrary m.

### 6. Peak balance and event mass: pass without a mass-floor claim

- `H_j` is the limiting isolated peak height and choosing
  `w_j proportional to S(t_j)` makes `w_j H_j` independent of j.  This is an
  asymptotic leading-height equality, not an exact finite-epsilon equality.
- Changing variables `t=t_j+epsilon y` gives the positive limiting
  free-exposure area on each certified interval.
- Only after epsilon is fixed, the first Dyson expansion integrates to
  `integral f_B = B integral G + O_epsilon(B^2)`.  Hence the physical event
  mass tends to zero with B; no positive absolute floor or coupled
  `(epsilon,B)` limit is inferred.

### 7. Lean claim boundary: scientifically accurate, provenance fix required

The text explicitly says the two analytical theorems are conventional
human-audited proofs, lists the missing continuum ingredients, and forbids the
phrases “Lean verified” and “formally verified.”  Inspection of the actual
module headers and axiom reports agrees.  The only defect is the unresolved
path/pinning issue in P1-2.

## PRR release boundary

The supplement's analytical core can support a PRR submission only with the
following exact claim:

> For each fixed finite m, an m-dependent narrow-noise longitudinal-slab
> family in physical dimension two or three has at least m certified local
> maxima for sufficiently small epsilon and, after fixing epsilon, sufficiently
> small positive reaction budget B, uniformly on the stated compact interior
> weight set.

It cannot support “exactly m modes globally,” “one geometry realizes all m,”
“finite practical B,” “positive event-mass floor,” “cusp established,”
“solver convergence,” or “Lean verified.”  Overall PRR release therefore
remains **HOLD** until the two P1 release findings above are closed and the
separate frozen positive-budget numerical/topological evidence chain required
by the main paper has passed its own independent audit.  Fixing the P2 items
will improve clarity but will not expand the theorem.
