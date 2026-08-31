# Round 149: exact-\(m\) supplement migration independent attack

Date: 2026-07-14  
Reviewer: independent post-migration adversarial auditor  
Decision: **INDEPENDENT HASH-SPECIFIC PASS FOR THE EXACT-\(m\) PAPER PROOF / PRR HOLD / F0 HOLD / F1 HOLD**  
Open findings in the audited theorem boundary: **P0 = 0, P1 = 0, P2 = 0**

## 1. Authority and claim boundary

This round is the independent acceptance audit required by Round 148.  It
attacks the frozen reader-facing exact-\(m\) proof, its use by the integrated
Supplement, the theorem-first main-paper narrative, and the dedicated
reproducible build chain.  The reviewer did not author or repair the proof.
No proof, theorem statement, main-paper statement, Supplement statement, Lean
module, bibliography entry, or positive-budget scientific artifact was changed
in this round.

The pass is deliberately narrow.  It accepts the conventional paper proof that
the stated constructed family has exactly \(m\) nondegenerate finite-window
maxima and \(m-1\) nondegenerate finite-window minima after taking the limits in
the declared order.  It does not accept a useful common positive budget,
nontrivial contact dynamics, an event-mass floor, same-support mode switching,
a finite-parameter continuum realization, a discretization, or a PRR
submission package.

## 2. Frozen bytes audited

| Object | SHA-256 |
| --- | --- |
| `manuscript/exact_m_theorem_full_proof.tex` | `a372b5a33d2203b8f3214a153f4aaf1e81497bf146c0ac1db1cfda97919c1c7b` |
| `manuscript/encounter_multimodal_prr_supplement.tex` | `566b752f2d5c2c8fabdf0a421f16599317a697dd46f7d41b6b16475495cb2e65` |
| `manuscript/encounter_multimodal_prr_theorem_first_working.tex` | `6e7393e44bb1da9bb196b839534fdf43e18dd90d0829d941ad7e155f4afcbc67` |
| `manuscript/exact_m_theorem_spine.tex` | `79b0a4467a67999f605b8a5d8ec07e41a88c07edc8cdf1639ad6b8d4ce70658e` |
| `manuscript/references.bib` | `2f90b6735993c6d2fa8bb8f1a6c35c334706d02585361d4ee9238ac020ce9c76` |
| `code/compile_theorem_first_working.py` | `15098db6e731e23a31967077b79ace723849b5e8383169bb497fa57f9b92725e` |
| `code/test_compile_theorem_first_working.py` | `c48ecffdd4222ef7987151e20037c950c324eec867a814d1b806751ebb43aa7c` |
| `artifacts/data/theorem_first_working_compile.json` | `797d536e16016a0ba80d44d7be265197a12be47ecfdb4e20da67e46248008646` |
| theorem-first main PDF | `c766de16ca3a70eda63397d4d78ccb9f44415982afa4d4b6e0a295197488984b` |
| theorem-first Supplemental PDF | `3bf770bd28d577aaac54057601e315745d240d29246fa3831a1d39fc82f7dbea` |

The Supplement contains exactly one
`\input{exact_m_theorem_full_proof.tex}`.  The main source contains exactly one
`\input{exact_m_theorem_spine.tex}`.  The accepted proof is therefore not only
hashed beside the paper: it is actually consumed by the integrated build.

## 3. Independent mathematical attack

### 3.1 Stationary midpoint variance and oriented centres

For

\[
 dZ_t=-\gamma(Z_t-\bar z)\,dt+\varepsilon\sqrt{D_0}\,dW_t,
\]

the frozen initial variance \(\varepsilon^2D_0/(2\gamma)\) is exactly the OU
stationary variance.  The mean remains
\(\mu(t)=\bar z+(z_0-\bar z)e^{-\gamma t}\), so \(z_0\ne\bar z\) makes its
derivative nonzero with one fixed sign on the whole window.  Consequently
\(x=\operatorname{sgn}(\mu')\mu/\ell_0\) is strictly increasing and has a
positive minimum derivative on compact \(I\).  The physical centres transform
with the same orientation, so \(\operatorname{sgn}(\mu')\ell_0c_j=\mu(t_j)\);
there is no hidden reversal in which the trajectory changes sign but the slabs
do not.

The weighted-state-space inequalities are also in the correct direction.  The
midpoint initial variance is strictly below twice its reversible variance, the
relative longitudinal condition is
\(u_0^2<4D_0/\gamma\), and the wrapped Gaussian is square integrable against
the uniform transverse equilibrium.  These facts are sufficient for the later
fixed-\(\varepsilon\) unbounded-space bridge.

**Attack result: PASS.**  No time-dependent mixture width is smuggled into the
common-variance argument.

### 3.2 Whole-window contact factor

The deterministic relative path is required to lie at least \(\eta\) inside
the contact ball on every point of \(I\), not only near the target clocks.  The
relative covariance divided by \(\varepsilon^2\) has a positive, uniformly
bounded longitudinal block and a positive, uniformly bounded transverse block
on compact positive time.  Its first two time derivatives are bounded as well.
The reverse triangle inequality therefore separates the whole noncontact set
from the deterministic path by \(\eta\).

Because \(a<W/2\), the geodesic contact ball does not meet the transverse cut
locus.  Differentiating the wrapped-Gaussian image sum through order two only
adds polynomial factors in the scaled displacement and powers of
\(\varepsilon^{-1}\).  The fixed separation leaves the same
\(e^{-q/\varepsilon^2}\) tail after those factors and after the lattice sum.
The resulting \(C^2(I)\) bound gives \(c_{d,\varepsilon}\ge1/2\) and controls
both logarithmic derivatives without dividing by a vanishing contact
probability.

**Attack result: PASS.**  The proof does not replace a whole-window condition
by a target-neighbourhood condition.

### 3.3 Exact factorization, common width, and conserved allocation budget

Independence of midpoint and relative coordinates factors the free exposure.
Convolving a normalized slab of variance \(\varepsilon^2\rho^2\) with the
stationary midpoint variance gives the common variance

\[
 \varepsilon^2S_*^2=\varepsilon^2\left(D_0/(2\gamma)+\rho^2\right)
\]

for every component.  The orientation identity converts its physical-centre
displacement to \(\ell_0(x-c_j)\), yielding the stated common-variance mixture
with \(\sigma=\varepsilon S_*/\ell_0\).  Each longitudinal slab integrates to
one and the positive weights sum to one, so allocations preserve the installed
centre-space budget.

**Attack result: PASS.**  The exact-\(m\) topology is not inferred from an
approximate factorization or unequal hidden widths.

### 3.4 Global \(2m-1\) multiplicity bound

Multiplication of \(H'\) by the nowhere-zero Gaussian factor preserves every
zero and its multiplicity and produces

\[
 \sum_{j=1}^m (a_j+b_jx)e^{\lambda_jx},\qquad
 \lambda_1<\cdots<\lambda_m.
\]

The proof closes both parts needed for a global count.  After removing the
lowest exponential, the first affine term dominates at minus infinity and the
last affine-exponential term dominates at plus infinity, so the real zeros are
confined to a compact interval and analyticity makes their number finite.  Two
derivatives annihilate the first affine term while leaving a nonzero affine
coefficient at every remaining distinct exponent.  Generalized Rolle counting
with multiplicity gives \(N(Q)-2\le N(Q'')\), and induction gives
\(N(H')\le2m-1\).  In the actual mixture every affine slope is nonzero, so no
summand silently disappears.

**Attack result: PASS.**  The cap counts multiple roots and all real roots, not
only sign changes on the declared window.

### 3.5 Adjacent isolation and pure-mixture roots

For \(x\in[c_j,c_{j+1}]\), comparison with component \(j\) on the left and
component \(j+1\) on the right gives a fixed positive difference of squares
for every nonadjacent component.  The lower weight bound converts this to a
uniform exponentially small ratio.  The same calculation works on both outer
tails.  Thus posterior means and variances may be replaced by their adjacent
pair with a uniformly exponentially small error.

Near each centre, the logarithmic slope is
\((c_j-x)/\sigma^2\) plus an exponentially small error and is strictly
decreasing, producing one simple maximum.  In each gap the weighted equality
point remains in the gap because the weight-log shift is only \(O(\sigma^2)\).
At the two declared crossover edges the adjacent odds are exactly \(1/9\) and
\(9\), giving the required opposite slope signs and a region with
\(L'=\Theta(\sigma^{-4})>0\).  This yields one simple minimum at
\(r_j=s_j+O(\sigma^4)\) with the stated curvature.  The construction already
exhibits \(2m-1\) simple roots; the global cap then excludes every other real
root, including a multiple one.  Tail isolation supplies nonzero endpoint
slopes.

**Attack result: PASS.**  Extreme admissible weight ratios cannot move a
crossover out of its fixed gap for sufficiently small \(\sigma\).

### 3.6 Exhaustive posterior-sector certificate

The proof does not make the false claim that one adjacent component dominates
exponentially at the \(1/9\)- or \(9\)-odds crossover edge.  It separately
covers:

1. the two outer tails by the convex-hull bound on the posterior mean;
2. peak boxes of width \(O(\sigma^2)\), with negative curvature and fixed
   boundary signs;
3. valley boxes of width \(O(\sigma^4)\), with positive curvature and fixed
   boundary signs;
4. crossover-minus-valley sectors by integrating the
   \(\Theta(\sigma^{-4})\) lower curvature bound; and
5. both remaining sides of every gap by splitting at one-quarter of the gap,
   using one-component isolation on the near-peak side and the exact logistic
   posterior bound on the near-crossover side.

Those regions exhaust the complement of the open boxes.  Their alternating
sign order gives a uniform nonzero margin there.

**Attack result: PASS.**  No uncovered interstitial sector remains in which a
slow factor could create an extra root.

### 3.7 Slow positive factor

For \(F=a_\sigma H_\sigma(x(t))\), stationarity is equivalent to

\[
 D=\partial_t\log F=b_\sigma+x'L.
\]

On the certified complement, \(x'L\) dominates the uniformly bounded
\(b_\sigma\) with the required sign.  On peak and valley boxes,

\[
 D'=b_\sigma'+x''L+(x')^2L'
\]

is strictly negative and strictly positive, respectively, because the bounded
terms are dominated by the \(\sigma^{-2}\) peak curvature or the
\(\sigma^{-4}\) valley curvature.  Boundary signs and monotonicity give one and
only one root per box.  The same estimates imply \(O(\sigma^2)\) peak shifts
and \(O(\sigma^4)\) valley shifts.

The contact factor satisfies the slow-factor hypotheses through the preceding
whole-window differentiated tail lemma.  Its time-independent normalization
does not enter either logarithmic derivative.

**Attack result: PASS.**  Positivity alone is not used as a topology argument;
the proof supplies the derivative and complement margins positivity by itself
would lack.

### 3.8 Fixed-\(\varepsilon\) \(C^2\) Doi transfer

The order of limits is respected.  After fixing one admissible positive
\(\varepsilon\), the Gaussian killing profile is bounded, the initial density
belongs to the reversible weighted state space, and the compact allocation
polytope lies strictly inside the simplex.  It therefore admits the affine
chart and bounded complex tube used by Supplemental Theorem `thm:mixed-jet`.
The singleton equal-weight case is explicitly reduced to a pointwise argument.

The simple free-exposure roots vary continuously over the compact allocation
set.  Ordered root graphs are compact and remain disjoint; continuity supplies
uniform curvature, tube-boundary, complement, and endpoint margins.  Uniform
\(C^2(I)\) convergence of \(f_B/B\) to the free exposure then preserves
opposite derivative signs at tube boundaries, the sign of the second
derivative inside each tube, and the nonzero complement and endpoint margins.
Hence every tube has exactly one root of the same type and there are no others.

**Attack result: PASS.**  The proof obtains \(B_0(\varepsilon)\) only after
fixing \(\varepsilon\), and never asserts a lower bound uniform as
\(\varepsilon\downarrow0\).

### 3.9 Edge cases and scope attacks

- **\(m=1\):** the proof uses no empty gap minimum, no valley, and no
  \(\Delta_*\).  The exact slope \((c_1-x)/\sigma^2\) gives one maximum and
  both endpoint signs.
- **Endpoints:** all target times are strictly interior and their fixed
  separation from the endpoints survives the shrinking boxes.  Slow-factor and
  Doi transfers both retain explicit endpoint derivative margins.
- **Weights:** \(w_j\ge w_*>0\) makes the allocation family compact and keeps
  all log-ratios uniformly bounded.  The theorem does not extend its uniform
  conclusion to weights approaching zero.
- **Saturation:** the paper openly states
  \(c_{d,\varepsilon}=1+O(\varepsilon^{-N}e^{-q/\varepsilon^2})\) in
  \(C^2(I)\).  It does not misdescribe this as nontrivial encounter gating or
  pathwise Brownian confinement.
- **Finite window:** the count is only on \(I=[\tau,T]\subset(0,\infty)\).
  The paper explicitly declines to exclude earlier, later, or remote extrema.
- **Support versus allocation:** the support design may depend on the fixed
  prescribed \(m\), and every admissible interior allocation in that design has
  the same mode count.  The main text explicitly says this is not same-support
  switching of the mode count by reallocation.

**Attack result: PASS.**  None of these edge cases is promoted beyond the
proved quantifiers.

### 3.10 Lean boundary

The three Lean hashes printed in the Supplement were independently recomputed
and match the current files exactly:

```text
Encounter.lean          d2c11759c831228eb6641f3944d1d860c34615982d15b883e6d029f0a670e754
EncounterDesign.lean    fa45ceb3c40e7c9769d4f7d6ab5aa1495e89a361c675b89f362dfc11798b8330
EncounterContinuum.lean ae23060be3166c392eab2d8a0a5af5dcd1d3a4adf2a8b912fd8a0c2161e538b4
```

Their source comments and theorem inventory cover finite algebraic fragments,
not the continuum semigroup, wrapped-Gaussian tail, global interval root count,
posterior-sector certificate, or fixed-\(\varepsilon\) transfer.  The
Supplement says the analytic theorem is not Lean verified and forbids the
phrases “Lean verified” and “formally verified” for it.

**Attack result: PASS.**  The formal-evidence boundary is accurate and the
printed anchors are current.

## 4. Reproducible build and publication attack

The dedicated driver was run from both `/tmp` and `/`, not from the repository
working directory.  Each invocation created four separate temporary source and
output trees: two main-paper builds and two Supplemental builds.  It used
`SOURCE_DATE_EPOCH=1783987200`, required byte-identical rebuilds for each PDF,
checked final logs for undefined references, undefined citations, TeX errors,
and overfull boxes, and audited every PDF for parsing, page count, every-page
MediaBox, encryption, JavaScript, font embedding, Type 3 fonts, and extracted
NUL/replacement characters.

The first whole-driver replay attack found a build-evidence defect outside the
mathematical proof: TeX can hard-wrap the random temporary-directory basename,
so a direct byte replacement did not remove every run-specific path from the
published logs.  The PDFs remained byte-identical, but four log hashes and the
manifest hash changed.  The driver was repaired to normalize both ordinary and
TeX-line-wrapped temporary roots, and a regression test now compares two
distinct wrapped random roots.  No theorem or manuscript source changed.

After that repair, two complete consecutive publisher invocations produced
identical hashes for all seven published objects: the two PDFs, four evidence
logs, and manifest.  The final focused test result was:

```text
13 passed
ruff check: all checks passed
ruff format --check: both files already formatted
```

The final manifest is schema 3, records all six required source hashes,
contains `release_eligible=false`, and pins all six non-self-referential
published files.  Its source allowlist contains only the theorem-first main,
Supplement, theorem spine, full proof, bibliography, and dedicated driver.  It
does not invoke or import the historical `compile_manuscript.py` or any
positive-budget numerical producer.

## 5. PDF and visual inspection

The final main PDF has 5 pages and the final Supplement has 20 pages.  Every
page has MediaBox `(0,0,612,792)` points, both PDFs are unencrypted and contain
no JavaScript, Ghostscript parses both, all 28 main-paper fonts and all 31
Supplemental fonts are embedded, and no Type 3 font is present.  Extracted text
contains no NUL or replacement character.

All 25 pages were rendered to PNG and inspected as contact sheets; the newly
integrated proof pages and the formal-boundary table were also inspected at
page resolution.  No clipping, overlap, missing glyph, black box, unreadable
formula, broken reference, or broken page transition was observed.  The narrow
formal-boundary table has ordinary aggressive word hyphenation but remains
fully legible; this is not a mathematical or build defect.

## 6. Narrative consistency

The main abstract, introduction, theorem spine, evidence-boundary section,
discussion, Supplemental abstract, exact proof, and formal-boundary table agree
on the following limits:

- fixed finite \(d\) and fixed finite \(m\), with constants allowed to depend on
  both;
- an \(m\)-dependent support construction, not one geometry with arbitrarily
  many modes;
- conserved installed centre-space budget across allocations, not a full
  configuration-space integral;
- small \(\varepsilon\) first, then small \(B<B_0(\varepsilon)\);
- a compact positive-time window only;
- saturated relative contact in the theorem family;
- no useful common positive budget, event-mass floor, solver convergence,
  finite-parameter continuum realization, or Lean verification; and
- no promotion of the separate prospective one-/two-/three-mode numerical
  controls.

Table I still says that a hash-specific re-audit is required.  This Round 149
artifact is the external satisfaction of that requirement for the frozen
bytes; changing the sentence inside the audited Supplement merely to announce
the audit would create new bytes requiring another audit.  A later editorial
revision may update that bookkeeping together with its own new hash-specific
check.

## 7. Final disposition

```text
stationary midpoint/common variance             PASS
whole-window differentiated contact tail        PASS
global 2m-1 multiplicity count                  PASS
uniform adjacent isolation                      PASS
pure exact topology, m=1, and endpoints         PASS
full posterior-sector complement                PASS
slow-factor topology preservation               PASS
fixed-epsilon C2 Doi transfer                    PASS
weights, saturation, and quantifier boundary    PASS
Lean and finite-window boundary                  PASS
dedicated reproducible build                     PASS
independent exact-byte proof acceptance          PASS
useful finite positive budget                    NOT PROVED
nontrivial-contact continuum realization         NOT PROVED
event mass / survival / solver convergence       NOT PROVED
F0                                               HOLD
F1                                               HOLD
PRR submission                                   HOLD
```

The exact-\(m\) paper-proof chain is independently accepted for the frozen
hashes listed in Section 2.  That acceptance closes the Round-148 migration
audit requirement and nothing beyond it.  The manifest remains correctly
fail-closed with `release_eligible=false`.
