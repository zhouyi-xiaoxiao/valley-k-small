# Round 112: independent adversarial attack on the exact-\(m\) theorem candidate

Date: 2026-07-14  
Role: independent theorem, transfer, and manuscript-promotion reviewer  
Decision: **HOLD FOR MANUSCRIPT PROMOTION**  
Open findings: **P0 = 1, P1 = 3, P2 = 4**

## 1. Scope, reviewed bytes, and execution boundary

This audit treated every exact-mode statement in
`notes/exact_m_mode_encounter_theorem_candidate.md` as untrusted.  The audited
candidate had SHA-256

```text
014d370ae6aebc2090585cb59b390b9eb4cb081246323d43404cb3c8d3b9d460
```

The two theorem notes invoked by the candidate were also read:

```text
notes/direct_physical_multimode_theorem.md
2b35d1b1053045220b29975d30f8b3c842d33273ca46de86b8cf7798c26a9c3d

notes/pde_mixed_jet_theorem.md
ac0e6cbb34d446d2b9ae2b52c22684ee72da7cadb04d864aacba085dff75f095
```

I checked the exponential-polynomial induction, multiplicity bookkeeping,
boundary behaviour, the posterior-mean and posterior-variance identities, all
three proposed singular layers, uniformity in the compact weight set, the
contact-factor reduction, the stationary-variance OU embedding, the
finite-window endpoint claim, the sequential \(\varepsilon\)-then-\(B\) order,
and the mixed-jet transfer hypotheses.  I also compared the novelty language
with the repository's primary-literature collision map and spot-checked
Silverman's primary 1981 paper metadata and scope (DOI
`10.1111/j.2517-6161.1981.tb01155.x`).

No positive-budget generator, killed semigroup, finite-volume result,
off-lattice trajectory, or Monte Carlo science run was opened or executed.
The only calculation was a disposable \(B=0\) NumPy sanity test described in
Section 8.  The theorem note and manuscript were not edited.  The only
workspace write is this audit.

## 2. Executive verdict

The proposed result is **plausible but not proved by the current note**.

The stationary-variance OU reduction is correct, the contact factor does
satisfy the advertised slow-log-derivative hypothesis under the stronger
whole-window contact-interior assumption, and the weak-budget theorem is in
principle strong enough to transfer a *proved* simple complete stationary
signature after \(\varepsilon>0\) is fixed.  The exponential-polynomial
zero-count argument is also correct in substance after one missing
finite-zero step is supplied.

The central exactness step nevertheless fails its present proof audit.  At a
fixed \(C_{\rm v}\sigma^2\) distance from a crossover, one Gaussian component
is not exponentially dominant in \(1/\sigma^2\); its competitor has a fixed
nonzero ratio.  The note therefore has not established the asserted uniform
signed lower bound for the log derivative on the *entire* complement.  That
bound is precisely what excludes extra roots after multiplication by a slow
positive factor.  A quantitative posterior-mean sector lemma can likely
repair this, but it is not currently present.

Even after that repair, this theorem alone is not a PRR-level encounter
mechanism.  The whole-window contact-interior scaling makes
\(c_{d,\varepsilon}\to1\) in \(C^2\), so the exact-\(m\) construction is, at
leading order, a well-separated equal-variance Gaussian location mixture
traversed by a monotone mean.  Dimension and relative encounter dynamics enter
only through a common asymptotically saturated factor.  The theorem can be a
valuable analytical backbone, but PRR promotion still requires the separately
promised finite-parameter, nontrivial-contact, positive-event validation.

Final decision:

```text
mathematical idea                         = PLAUSIBLE
current proof of complete topology        = FAIL
weak-B transfer conditional on repair     = PLAUSIBLE/PASS IN PRINCIPLE
standalone encounter significance         = INSUFFICIENT
manuscript promotion                      = HOLD
kill the research direction               = NO
```

## 3. Checks that survive the attack

### 3.1 Stationary midpoint variance and the common-scale clock: PASS

For the midpoint OU process,

\[
s^2(t)=s_0^2e^{-2\gamma t}
       +\frac{D_0}{2\gamma}(1-e^{-2\gamma t}).
\]

Thus \(s_0^2=D_0/(2\gamma)\) makes \(s^2(t)\) constant.  Convolution with a
Gaussian slab of width \(\varepsilon\rho\) gives the common variance
\(\varepsilon^2S_*^2\), where
\(S_*^2=D_0/(2\gamma)+\rho^2\).  The longitudinal free-exposure formula is
therefore an exact equal-scale Gaussian location mixture on the unbounded
longitudinal coordinate used by the direct theorem; no torus-image correction
is missing in this coordinate.

The stationary variance choice also satisfies the direct theorem's weighted
midpoint condition
\(s_0^2<D_0/\gamma\).  It does not by itself supply the separate relative-law
weighted-space conditions; that omission is Finding P1.2.

### 3.2 Posterior identities: PASS

Writing

\[
 \pi_j(x)=\frac{w_j\exp[-(x-c_j)^2/(2\sigma^2)]}
                 {H_{\sigma,w}(x)},
 \qquad \bar c_\pi(x)=\sum_j\pi_j(x)c_j,
\]

gives the exact identities

\[
 L_{\sigma,w}(x)=\frac{\bar c_\pi(x)-x}{\sigma^2},
 \qquad
 L_{\sigma,w}'(x)
 =\frac{\operatorname{Var}_\pi(c)}{\sigma^4}
  -\frac1{\sigma^2}.
\]

Near a centre, posterior variance is exponentially small and
\(L'=-\sigma^{-2}+o(\sigma^{-2})\).  In a genuine adjacent-component
crossover layer where both adjacent posterior masses have fixed positive
lower bounds, \(\operatorname{Var}_\pi(c)\) has a fixed positive lower bound,
so \(L'=\Theta(\sigma^{-4})>0\).  These local signs are correct.

For the time log derivative,

\[
 D'=b_\sigma'+x''L+(x')^2L'.
\]

The \((x')^2L'\) term dominates the bounded \(b_\sigma'\) and the displayed
\(x''L\) term inside correctly chosen peak and crossover layers.  The note's
local monotonicity conclusion is therefore credible, but the required
uniform constants and the complement sectors remain unwritten.

### 3.3 Whole-window contact factor: PASS under the stated stronger geometry

Applying the direct theorem's Gaussian-image estimate on all of
\(I=[\tau,T]\), rather than only target neighbourhoods, is legitimate if the
deterministic relative path has a fixed contact-interior margin on all of
\(I\).  If

\[
 E_r(\varepsilon)
 =\|\partial_t^r(c_{d,\varepsilon}-1)\|_\infty
 \le C_r\varepsilon^{-N_r}e^{-q/\varepsilon^2},
\]

then, after \(E_0\le1/2\),

\[
 \|(\log c)'\|_\infty\le2E_1,
 \qquad
 \|(\log c)''\|_\infty\le2E_2+4E_1^2.
\]

Hence the physical contact factor meets Lemma 4.1's uniform log-derivative
hypothesis.  Constants remain pointwise in fixed finite \(d\), as the
candidate correctly states.

### 3.4 Sequential weak-budget logic: PASS in principle, conditional on a
proved free signature

For every *fixed* \(\varepsilon>0\), each Gaussian catalyst is bounded and the
mixed-jet theorem supplies uniform \(C^2(I)\) convergence over a compact
finite-dimensional allocation family.  A finite family of simple roots,
signed-curvature root boxes, nonzero endpoint slopes, and a positive
derivative margin on their compact complement is stable under such a
perturbation.  Therefore an existential \(B_0(\varepsilon)>0\) follows once
those free-clock margins are actually proved.

The order must remain exactly the one stated in the note: fix finite
\((d,m)\), then fix sufficiently small positive \(\varepsilon\), then take
\(0<B<B_0(\varepsilon)\).  Nothing reviewed supports a uniform lower bound on
\(B_0\), an interchange of limits, or the finite budget intended for the
numerical paper.

## 4. P0 finding: the slow-factor complement exclusion is not proved

### P0.1 — The asserted exponential dominance is false at the declared
crossover-layer boundary

Lines 256--265 claim that on the complement of crossover layers of width
\(C_{\rm v}\sigma^2\), one component is exponentially dominant and hence
\(|x'L|\to\infty\) uniformly with the required alternating sign.  The first
assertion is false as written.

Take the allowed two-component example

\[
 c_1=-\tfrac12,\quad c_2=\tfrac12,\quad
 w_1=w_2=\tfrac12,\quad v=0.
\]

At the left boundary \(x=-C_{\rm v}\sigma^2\), the ratio of the right
component to the left component is exactly

\[
 \frac{\exp[-(x-c_2)^2/(2\sigma^2)]}
      {\exp[-(x-c_1)^2/(2\sigma^2)]}
 =e^{-C_{\rm v}},
\]

which is independent of \(\sigma\).  It is not
\(O(e^{-q/\sigma^2})\) for any fixed \(q>0\).  The numerical check in Section
8 reproduced the exact ratios \(e^{-1}\), \(e^{-4}\), and \(e^{-8}\).

Constant-ratio dominance may still be enough.  Indeed, in this example
\(|L|\asymp\sigma^{-2}\) at that boundary.  But that conclusion requires a
different quantitative argument; it does not follow from the exponential-
dominance statement in the note.

There are three missing pieces:

1. The relevant weighted crossover is

   \[
   s_j(\sigma,w)=\frac{c_j+c_{j+1}}2
    +\frac{\sigma^2}{c_{j+1}-c_j}
      \log\frac{w_j}{w_{j+1}},
   \]

   not the unweighted midpoint \(v_j\).  Compact weight ratios place it within
   \(O(\sigma^2)\) of \(v_j\), but the constants must be fixed explicitly.

2. On every sector between a peak layer and a crossover layer, the proof must
   establish a signed posterior-mean separation

   \[
   \operatorname{sgn}(\bar c_\pi-x)
   \quad\hbox{and}\quad
   |\bar c_\pi-x|\ge r_\sigma,
   \qquad r_\sigma/\sigma^2\longrightarrow\infty,
   \]

   uniformly in \(w\).  No such inequality or exhaustive sector covering is
   currently given.  The identity for \(L'\) inside crossover layers does not
   provide it.

3. The time transformation adds \(x'\), \(x''\), and \(b_\sigma\).  The note
   must use common bounds on \(x'\), \(x''\), \(b_\sigma\), and
   \(b_\sigma'\) to prove endpoint signs, monotonicity, and the full
   complement margin with one \(\sigma_0\) uniform over
   \(\mathcal W_{w_*}\).

Until a posterior-sector lemma supplies those estimates, Lemma 4.1's
"exactly" conclusion and Theorem 5.1's no-extra-root conclusion do not follow.
This is P0 because complete topology is the only upgrade over the already
audited at-least-\(m\) theorem.

### Required repair for P0.1

A repair should state and prove a separate quantitative lemma with:

- weighted crossover centres \(s_j(\sigma,w)\);
- explicit uniform weight-ratio, centre-separation, and layer-disjointness
  constants;
- peak posterior bounds, two-component crossover posterior bounds, and
  nonadjacent-component exponential remainders;
- signed lower bounds for \(L\) on every tail and inter-layer sector;
- bounds for \(D\) and \(D'\) after including \(x'\), \(x''\), \(b\), and
  \(b'\); and
- common root boxes on which \(F''\) has a strict sign, plus a positive
  \(|F'|\) margin on the full complement.

Only then can the compactness step used by the mixed-jet transfer be invoked.

## 5. P1 findings

### P1.1 — The exponential-polynomial zero bound is right in substance but
the multiplicity proof is incomplete at infinity

The algebraic reduction is correct:

\[
 \sigma^2e^{x^2/(2\sigma^2)}H'(x)
 =\sum_j(a_j+b_jx)e^{\lambda_jx},
 \qquad \lambda_1<\cdots<\lambda_m.
\]

After multiplication by \(e^{-\lambda_1x}\), differentiating twice removes
the first affine term and leaves at most \(m-1\) affine-exponential terms with
distinct exponents.  For the actual Gaussian coefficients the remaining
linear coefficients do not vanish.  The generalized Rolle inequality
\(N(f)\le N(f'')+2\), with multiplicities, then yields \(2m-1\).

However, the proof applies a finite number \(N\) without first proving that
the real zero set is finite.  Real analyticity excludes accumulation at a
finite point but not, by itself, a sequence escaping to infinity.  Add the
standard asymptotic step: after the exponential normalization, the first
surviving affine-exponential term controls one tail and the last surviving
term controls the other, so there are no roots outside a compact interval;
analyticity then makes the count finite.  Alternatively state and cite the
extended-complete-Chebyshev zero theorem with multiplicities.

The subsequent inference is valid once this is supplied: \(m\) simple peak
roots plus at least one distinct gap root in each of \(m-1\) gaps exhaust a
\(2m-1\) multiplicity budget, so every gap root is simple and there are no
others.  This finding does not falsify Lemma 3.1, but the proof is not yet
publication complete.

### P1.2 — The Doi theorem statement does not pin all inherited weighted-space
and geometric hypotheses

Theorem 5.1 lists four assumptions, then asserts that the weighted-space
initial law and OU quotient satisfy the mixed-jet theorem.  The direct theorem
also requires, among other fixed data,

- \(0<a<W/2\) for the embedded minimum-image contact ball;
- positive-definite wrapped transverse covariance;
- the declared independent midpoint/relative initial law; and
- the relative weighted-space inequality
  \(u_0^2<4D_0/\gamma\) (as well as the midpoint inequality, which the
  stationary choice does satisfy).

"Use ... from the direct theorem" may be intended to import all of them, but a
standalone theorem promoted to a manuscript cannot leave the positive-\(B\)
domain implicit.  State the inherited hypotheses or give an exact assumption
reference.  Also state explicitly that the common root boxes and signed
curvature/complement margins are uniform on the compact allocation set.  Root
simplicity at each individual \(w\) is not by itself the uniform margin used
in lines 313--334.

### P1.3 — The result is not by itself a nontrivial encounter mechanism or a
PRR significance claim

The whole-window contact-interior hypothesis yields

\[
 c_{d,\varepsilon}=1+O(\varepsilon^{-N}e^{-q/\varepsilon^2})
 \quad\hbox{in }C^2(I).
\]

Thus the leading exact-\(m\) mechanism is the classical separated
equal-variance Gaussian mixture.  The physical dimension appears through a
constant \(W^{-(d-1)}\) and an exponentially small common contact correction;
relative approach and separation do not generate the modes.  Section 7
honestly admits this, but Section 6's phrase "exact encounter-process
embedding in every fixed finite \(d\)" can still be read as stronger than the
mechanism delivered.

The primary Gaussian scale-space literature already owns the zero/mode-count
mathematics, and the repository's literature audit shows that multimodal
capture times, heterogeneous reaction-time theory, and fixed-total-reactivity
optimization are also established separately.  The defensible novelty is only
the full conserved-allocation/complete-certificate/positive-Doi/finite-event
chain.  The final two links are prospective, not supplied by this theorem.

For manuscript use, describe this result as an **embedded Doi theorem with
asymptotically saturated contact**, not as evidence that encounter geometry or
dimension causes exact-\(m\) modality.  PRR promotion needs a finite-parameter
case where contact is not numerically indistinguishable from one, at a usable
common positive budget, with nonnegligible event-basin mass and an independent
process-level check.  This is a significance gate, not a reason to kill the
analytical direction.

## 6. P2 findings

### P2.1 — Coordinate reversal reuses \(c_j\) inconsistently

Lines 57--65 first define \(c_j=\mu(t_j)\), then allow \(x=-\mu\), and finally
write \(c_j=x(t_j)\).  If \(\mu\) is decreasing, these are different numbers.
Define one orientation sign \(s=\operatorname{sgn}\mu'\), set
\(x=s\mu\) (or \(-s\mu\), as appropriate), and transform every catalyst
centre by the same sign.  This is a notation defect rather than a failure of
the invariant squared-distance formula.

### P2.2 — The \(m=1\) case uses an undefined minimum separation

The theorem includes \(m=1\), but Lemma 4.1 defines
\(\Delta=\min_j(c_{j+1}-c_j)>0\).  This minimum is over an empty set when
\(m=1\).  Split off the one-component proof or define crossover quantities
only for \(m\ge2\).

### P2.3 — \(|\log\sigma|\) is dimensionally undefined

The physical \(\sigma\) has units of length.  A peak-layer width should use a
dimensionless logarithm such as
\(C_{\rm p}\sigma^2\Delta_*^{-1}|\log(\sigma/\Delta_*)|\), with a fixed
reference separation \(\Delta_*>0\), or work entirely in declared
dimensionless coordinates.

### P2.4 — \(f_B/B\) is budget-rescaled, not probability-normalized

Lines 300--306 call \(F_B=f_B/B\) the "normalized Doi reaction-time density."
Division by \(B\) is the weak-budget rescaling used by the mixed-jet theorem;
it does not normalize total probability mass.  Call it the
**budget-rescaled reaction-time density**.  Its stationary points are the same
as those of \(f_B\), so this wording repair changes no topology.

## 7. Boundary and uniformity ledger

| Requested attack | Result | Evidence / remaining requirement |
|---|---|---|
| Lemma 3.1 multiplicity count | **PASS IN SUBSTANCE / TEXT REPAIR** | Induction works; finiteness and tail dominance must be stated before generalized Rolle. |
| Pure-mixture boundary behaviour | **PASS AFTER SAME REPAIR** | Extreme affine-exponential terms control the two tails. |
| Peak layers | **PLAUSIBLE** | Own component is exponentially dominant; full constants and \(F''\) box signs not written. |
| Crossover layers | **PLAUSIBLE LOCALLY** | Posterior-variance identity is correct; use weighted crossovers and explicit posterior lower bounds. |
| Inter-layer complement | **FAIL** | Exponential dominance is false at fixed \(C_{\rm v}\sigma^2\) boundaries; no full signed bound is proved. |
| Weight uniformity | **UNPROVED GLOBALLY** | Compact ratios are enough in principle, but no single exhaustive constant ledger exists. |
| Contact log derivatives | **PASS** | Whole-window interior margin plus the displayed tail estimate gives the required bounds. |
| Endpoint derivatives | **PLAUSIBLE** | Target times are interior and monotonicity gives fixed endpoint separation; needs inclusion in the quantitative sector lemma. |
| OU common scale | **PASS** | Stationary variance coefficient makes \(S(t)=S_*\) exactly. |
| Fixed-window topology | **HOLD** | Depends on the failed complement exclusion. |
| Sequential \(\varepsilon/B\) limits | **PASS AS STATED** | Pointwise in fixed \(d,m,\varepsilon\); no limit interchange. |
| Mixed-jet positive-\(B\) transfer | **PASS IN PRINCIPLE / HYPOTHESES REPAIR** | \(C^2\) is sufficient once common signed boxes and complement margins exist and all weighted-space assumptions are pinned. |
| Novelty ceiling | **HOLD AS STANDALONE CLAIM** | Classical Gaussian mechanism plus asymptotically saturated contact; broader chain still needs finite-parameter evidence. |

## 8. Disposable numerical sanity check

Using Python `3.14.6` and NumPy `2.4.2`, I tested

\[
 x(t)=t,\quad
 c=(-1.1,-0.25,0.55,1.25),\quad
 w=(0.18,0.31,0.22,0.29),
\]

on \([-1.7,1.75]\), with the allowed slow factor

\[
 a(t)=\exp[0.13\sin(4t)],\quad
 b(t)=0.52\cos(4t),\quad \|b'\|_\infty\le2.08.
\]

A 500001-point sign scan followed by 100 bisection steps per bracket gave:

| \(\sigma\) | number of roots of \(b+L\) | expected \(2m-1\) |
|---:|---:|---:|
| 0.20 | 7 | 7 |
| 0.15 | 7 | 7 |
| 0.10 | 7 | 7 |
| 0.07 | 7 | 7 |
| 0.05 | 7 | 7 |

For \(\sigma=0.05\), the roots were approximately

```text
-1.100398, -0.676605, -0.249295, 0.151072,
 0.549238,  0.899017,  1.250371
```

This found no counterexample to the lemma and supports the claim that a
repair is likely.  It is not proof: sign scans can miss even roots, cover only
one allocation and slow factor, and say nothing about a uniform
\(\sigma_0\), positive \(B\), or event mass.

The same disposable calculation evaluated the exact two-component ratio at
\(x=-C\sigma^2\):

```text
C=1:  0.367879441171 = exp(-1)
C=4:  0.0183156388887 = exp(-4)
C=8:  0.000335462627903 = exp(-8)
```

This is the explicit counterexample to the proof's exponential-dominance
sentence, not a counterexample to the theorem itself.

## 9. Promotion gate and authorized next step

The candidate must remain labelled **NOT A MANUSCRIPT CLAIM**.  Promotion is
authorized only after all of the following occur in order:

1. replace the slow-factor proof structure by the quantitative weighted-
   crossover/posterior-sector lemma specified under P0.1;
2. independently re-audit that lemma, including \(m=1\), multiplicities,
   endpoint sectors, and uniform weight constants;
3. make Theorem 5.1 self-contained with every direct-theorem and weighted-
   space hypothesis, and derive common signed root boxes plus the complete
   complement margin;
4. retain the sequential \(\varepsilon\)-then-\(B\) scope and the
   nonconstructive nature of \(B_0(\varepsilon)\);
5. position the theorem as an asymptotically saturated-contact analytical
   backbone, not the full encounter novelty; and
6. require the separately frozen finite-parameter positive-budget and
   independent event-law evidence before any PRR significance claim.

The correct decision is **HOLD**, not **KILL**: the central missing estimate is
substantial but appears repairable, and the disposable test found behaviour
consistent with the proposed exact-\(m\) topology.
