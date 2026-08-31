# Round 77: fixed-finite-dimension theory attack

Date: 2026-07-14  
Scope: direct fixed-finite-mode theorem, unbounded weak-reaction semigroup
bridge, quotient/contact geometry, and their admissible dimension range  
Mutation boundary: no manuscript, supplement, theorem note, core theory,
numerical source, result, manifest, or figure was changed.  This audit is the
only added file.  No scientific or numerical producer was run.

## 1. Executive verdict

### Mathematical verdict

**PASS for extension to every fixed finite integer physical dimension
\(d\ge 2\), with constants and geometry fixed separately for each \(d\).**
There is no dimension-specific step in the analytic-semigroup or
fixed-finite-mode proof once the quotient is written as

\[
 \mathcal Q_d^\infty
 =\mathbb R_Z\times\mathbb R_{R_\parallel}
  \times\mathbb T_W^{d-1}.
\]

The direct construction also extends to **\(d=1\)** after a separate,
explicit zero-transverse convention: omit \(R_\perp\) and
\(\Sigma_{\perp,0}\), replace \(\mathbb T_W^0\) by a singleton, set
\(W^0=1\), and require only \(a>0\).  This one-dimensional corollary is
mathematically valid, but it should not be smuggled into a formula that still
contains a positive-definite \(0\times0\) covariance or the irrelevant
condition \(a<W/2\).

The admissible claim is pointwise in dimension.  It is **not** a
uniform-in-\(d\) theorem, a \(d\to\infty\) limit, a comparison at one
dimension-independent numerical value of the dimensional budget \(B\), or a
theorem for arbitrary localized catalysts.

### Release verdict

**HOLD for changing the manuscript claim now.**  The current authoritative
article, Supplement, and theorem notes deliberately state \(d\in\{2,3\}\).
An all-fixed-finite-\(d\) claim is valid only after the proof package is
rewritten with the outer dimension quantifier, the dimension-dependent
covariance and constants, and a chart-independent lattice-image tail proof.
The changes are finite and do not require new numerical evidence, but a
search-and-replace of “\(d=2,3\)” is not sufficient.

### PRR significance verdict

This is a **real but secondary analytical generality upgrade**, not a new PRR
physics headline.  It establishes that the conserved-slab construction has no
fixed finite upper-dimensional obstruction: after contact saturation, the
leading clock shape is dimension-independent up to the common factor
\(W^{-(d-1)}\).  However, dimensions above three have no accompanying
finite-parameter or positive-budget evidence here, and the theorem deliberately
makes the encounter factor tend to one near every designed peak.  Therefore
the extension does not close the finite-\(B\) allocation-cusp, continuation,
independent-solver, or physical-\(d=3\) gates.  Used as a concise robustness
corollary it strengthens the theory; used as the main novelty claim it would
read as mostly formal generalization.

## 2. Severity ledger

| ID | Severity | Finding | Required disposition |
| --- | --- | --- | --- |
| G77-1 | P1 | The source package proves and claims only \(d=2,3\); no current theorem has the outer quantifier over every fixed finite \(d\). | Add a general-fixed-\(d\) proposition/theorem and propagate only its exact scoped wording. |
| G77-2 | P1 | The compressed main-text/note phrasing that the complement is in a minimum-image chart and that “nonzero images have an additional separation” is not representation-invariant.  \(a<W/2\) keeps the **contact ball/boundary**, not its complement, away from the cut locus; the nearest image can have nonzero lattice index. | Use the Supplement's geodesic-separation strategy, strengthened to an explicit all-images lattice bound, and remove the compressed wording from the promoted proof. |
| G77-3 | P2 | \(d=1\) needs an empty-transverse convention and cannot literally retain \(\Sigma_{\perp,0}\succ0\) and \(a<W/2\). | State it as a separate corollary or omit it from the article. |
| G77-4 | P2 | \(W^{-(d-1)}\), the dual norm, peak amplitude, event mass, and the physical units of \(B\) depend on \(d\). | State that no cross-dimensional amplitude, budget, event-mass, or \(B_0\) comparison is made. |
| G77-5 | P2 | “all dimensions” could be misread as uniform in \(d\), noninteger \(d\), one geometry for every \(d\), or arbitrary localized patches. | Use “for every **fixed finite integer** \(d\)” everywhere and repeat the slab/sequential-limit caveats. |

Open counts for immediate manuscript promotion:

| P0 | P1 | P2 |
| ---: | ---: | ---: |
| 0 | 2 | 3 |

Expected counts after the proof and wording changes in Sec. 6: \(0/0/0\).
No counterexample to the proposed fixed-\(d\) theorem was found.

## 3. Evidence inspected

The audit read the complete current article, complete current analytical
Supplement, direct-theorem note, Round 23 repair audit, and Round 39 theorem
stress audit.  The underlying mixed-jet theorem note was also inspected
because the earlier dimension restriction arose there.

| Source | SHA-256 at audit time |
| --- | --- |
| `manuscript/encounter_multimodal_prr.tex` | `07b40f2e4366e453684219f16a293e6afb561cd323d863f12a39db57dbc46ec1` |
| `manuscript/encounter_multimodal_prr_supplement.tex` | `1d7631faaeff3c6688cee8e138c5f92e3efcd180268ce5f1125bb01f23e1face` |
| `notes/direct_physical_multimode_theorem.md` | `732e3d9a1d395fbbe2e31dbbdb4d532f20b927525b32cbd1852f4704af467c66` |
| `notes/pde_mixed_jet_theorem.md` | `3fc37bafc6320556322e80daa2c56bad9fd4b19e1856100caa8adf92341a8007` |
| `audits/round_23_direct_multimode_theory_attack.md` | `8e176af5220f5e233c0390abcd9d9f5890790227ad7710ba3d789addbe9ffd84` |
| `audits/round_39_theorem_proof_stress.md` | `c023559691167ec2f343a89d34df534e7581df3562d6a2e622d9128edfc839b7` |

Round 23 correctly treated the then-unstated \(d\ge2\) transfer as
unsupported because the available semigroup theorem had been stated only for
\(d=2,3\).  The present audit does not reverse that finding retroactively.  It
checks the stronger proposition directly and identifies the proof additions
needed to make it source-supported.

## 4. Adversarial mathematical audit

### 4.1 Exact quotient geometry: PASS for every fixed finite \(d\)

For two walkers on
\(\mathbb R\times\mathbb T_W^{d-1}\), diagonal transverse translation is a
compact symmetry group.  The quotient of
\(\mathbb T_W^{d-1}\times\mathbb T_W^{d-1}\) by this diagonal action is the
relative torus \(\mathbb T_W^{d-1}\).  The exact Haar identity

\[
 \int_{\mathbb T_W^{d-1}}\!\int_{\mathbb T_W^{d-1}}
 h(y_1-y_2)\,\mathrm dy_1\mathrm dy_2
 =W^{d-1}\int_{\mathbb T_W^{d-1}}h(r_\perp)\,\mathrm dr_\perp
\]

holds for every fixed finite integer \(d\).  It avoids introducing a global
torus midpoint, which can otherwise create coordinate-covering ambiguity.
The longitudinal linear transformation gives the already used midpoint and
relative diffusion coefficients.  Adding another physical dimension merely
adds one periodic relative Brownian coordinate and one diagonal-translation
coordinate that is integrated out.  No step invokes a property unique to a
disk or a sphere.

The quotient dimension is \(d+1\), but that is not a restriction: every
argument uses a fixed finite-dimensional Hilbert space and bounded
multiplication, not a low-dimensional embedding theorem.

### 4.2 Minimum-image contact ball and cut locus: PASS after wording repair

Let

\[
 \mathcal R_d=\mathbb R\times\mathbb T_W^{d-1},\qquad
 C_a=\{r:d_{\rm cyl}(r,0)<a\}.
\]

The flat product torus has injectivity radius \(W/2\), independent of its
finite dimension.  Hence \(0<a<W/2\) makes \(C_a\) an embedded Euclidean
\(d\)-ball with a smooth boundary, away from the cut locus.  If the
deterministic mean satisfies

\[
 \sup_{t\in I_*}d_{\rm cyl}(r_*(t),0)\le a-\eta,
\]

then for every \(R\in C_a^c\), the reverse triangle inequality gives

\[
 d_{\rm cyl}(R,r_*(t))\ge\eta.                 \tag{G77.1}
\]

This is the correct chart-independent fact.  The complement \(C_a^c\) does
contain cut-locus points, so it should not be described as lying in one
minimum-image chart.  Choose any fundamental representative and write the
wrapped density as a sum over \(n\in\mathbb Z^{d-1}\).  Equation (G77.1)
means the minimum over all lifts is at least \(\eta\), and therefore every
lift is at least \(\eta\); which lift is nearest is irrelevant.  A standard
lattice-shell Gaussian majorant then sums all images.  This repairs G77-2 and
works in every fixed finite \(d\).

### 4.3 Installed-resource normalization: PASS

The factor \(W^{-(d-1)}\) normalizes the omitted transverse
**common-centre** directions, not the relative contact volume.  For every
normalized longitudinal profile,

\[
 \int_{\mathbb R\times\mathbb T_W^{d-1}}
 \frac{\phi_j(z)}{W^{d-1}}\,\mathrm dz\,\mathrm dc_\perp=1.
\]

Thus \(\sum_jw_j=1\) gives installed centre-space amount exactly \(B\) for
every fixed \(d\).  The same factor appears in all channels, so it changes
their common leading amplitude but not endpoint-slope signs, strict
concavity, root count, or the balancing weights
\(w_j\propto S(t_j)\).

This normalization does not make amplitudes comparable across dimensions.
The centre-space volume unit and therefore the dimensional units of \(B\)
change with \(d\).  Any all-\(d\) statement must remain qualitative unless a
separate nondimensional cross-dimensional convention is declared.

### 4.4 Reversible weighted space: PASS for every fixed finite \(d\)

For fixed \(d\), the invariant density is the product of two Gaussians and
the normalized Haar density on \(\mathbb T_W^{d-1}\):

\[
 \pi_{d,\epsilon}(Z,R)=pi_Z(Z)\pi_\parallel(R_\parallel)W^{-(d-1)}.
\]

The map \(u\mapsto q=\pi_{d,\epsilon}u\) is unitary from
\(L^2(\pi_{d,\epsilon}\,\mathrm dx)\) to
\(X_{\pi_{d,\epsilon}}=L^2(\pi_{d,\epsilon}^{-1}\,\mathrm dx)\) in every
finite dimension.  Gaussian exponent comparison in the two unbounded
coordinates gives exactly the existing conditions

\[
 s_0^2<D_0/\gamma,\qquad u_0^2<4D_0/\gamma.
\]

For fixed \(\epsilon>0\), a wrapped Gaussian with any positive-definite
\((d-1)\times(d-1)\) covariance is smooth and square integrable against the
uniform torus density.  Its norm can deteriorate with \(d\) and
\(\epsilon\); the proposed theorem neither needs nor may claim uniformity in
either.

### 4.5 Analytic semigroup and mixed-jet bridge: PASS for every fixed finite \(d\)

On
\(H_d=L^2(\pi_d\,\mathrm dx)\), use the closed form

\[
 \mathfrak a_d(u,v)=
 \int (\nabla u)^{\mathsf T}\bm D_d\nabla\overline v\,
 \pi_d\,\mathrm dx,
\]

with weighted \(H^1\) form domain and the periodic transverse convention.
For every fixed finite \(d\), this densely defined nonnegative closed form
produces a nonpositive self-adjoint generator \(\mathcal G_d\).  Its
semigroup is a contraction for complex time with nonnegative real part.
The unitary density transform gives the forward realization on \(X_{\pi_d}\).

For fixed \(\epsilon\), the sharp contact indicator times every Gaussian
slab lies in \(L^\infty\cap X_{\pi_d}^*\).  Bounded perturbation therefore
preserves analyticity and the domain, and the finite-control Dyson series is
entire.  The Cauchy disks used for time and control derivatives do not depend
on a spatial Sobolev embedding.  Consequently the complete compact-positive-
time weak-\(B\) mixed-jet estimate extends unchanged in form to every fixed
finite \(d\), with constants

\[
 C_{r,\alpha}=C_{r,\alpha}(d,\epsilon,\tau,T,W,a,
 \text{profiles},q_0,\Theta,\delta).
\]

No bound in the current proof is uniform in \(d\).  This is harmless because
\(d\) must be frozen before \(\epsilon\) and \(B\).

### 4.6 Differentiated Gaussian tail: PASS for every fixed finite \(d\)

The relative density has one unbounded Gaussian factor and a wrapped
\((d-1)\)-dimensional Gaussian factor.  On the fixed positive-time set, the
covariance and its time derivatives are bounded and

\[
 0<\lambda_{-,d}I\preceq\Sigma_R(t)
 \preceq\lambda_{+,d}I<\infty.
\]

For each fixed derivative order \(r\), differentiating one lattice image
produces that Gaussian times a polynomial and a finite power of
\(\epsilon^{-1}\).  Combining Eq. (G77.1), fixed-dimensional Gaussian tail
bounds, and lattice-shell summability gives

\[
 \sup_{t\in I_*}
 \left|\partial_t^r(c_{d,\epsilon}(t)-1)\right|
 \le C_{r,d}\epsilon^{-N_{r,d}}e^{-q_d/\epsilon^2}. \tag{G77.2}
\]

The constants may depend on \(d\), the covariance, and the frozen geometry.
The direct mode theorem needs only \(r=0,1,2\).  Equation (G77.2) supplies
exactly the required \(C^2\) convergence for every fixed finite \(d\).

### 4.7 Local clocks, cross-channel dominance, and modes: PASS

After multiplying by the contact probability, the exact channel remains

\[
 g_{j,\epsilon}^{(d)}(t)=
 \frac{c_{d,\epsilon}(t)}
 {W^{d-1}\sqrt{2\pi}\epsilon S(t)}
 \exp\!\left[-\frac{(c_j-\mu(t))^2}
 {2\epsilon^2S^2(t)}\right].
\]

The midpoint Gaussian is one-dimensional for every \(d\).  Equation (G77.2)
makes the contact factor \(1+o_{C^2}(1)\).  Hence the own-channel slopes and
curvature retain orders \(\epsilon^{-2}\) and \(\epsilon^{-3}\), while
strict midpoint monotonicity makes every cross channel exponentially small.
The factor \(W^{-(d-1)}>0\) is common and does not alter any sign argument.
Because \(m\) and \(d\) are both fixed before \(\epsilon\), the finite sums
remain dominated.  The weak-\(B\) bridge then transfers the strict local
inequalities after \(\epsilon\) is frozen.

This proves fixed-\(d\) robustness, not a uniform high-dimensional result.
In particular, \(C_{r,d}\), \(\epsilon_0\), the weighted initial norm,
the peak amplitude, the event mass, and \(B_0\) may all deteriorate as
\(d\) increases.

### 4.8 One-dimensional endpoint: valid but best separated

For \(d=1\), the relative space is \(\mathbb R\), contact is the interval
\((-a,a)\), and the quotient is \(\mathbb R_Z\times\mathbb R_{R_\parallel}\).
The image sum is a single term, the invariant law is the product of two
Gaussians, and every semigroup and local-clock step above simplifies.  Thus
the theorem is valid.  The clean presentation is a one-sentence corollary
after the \(d\ge2\) theorem.  Folding \(d=1\) into the main notation is not
worth the resulting empty-covariance and dummy-period qualifications unless
one-dimensional encounter physics is part of the article's narrative.

## 5. Exact admissible theorem wording

The following is safe after the proof changes in Sec. 6.

> **Theorem (each prescribed fixed finite mode count in each fixed finite
> dimension).**  Let \(d\ge2\) and \(m\ge1\) be fixed integers.  Fix the
> parameters, initial means and variances, a positive-definite
> \((d-1)\times(d-1)\) transverse covariance, a period \(W\), and a contact
> radius \(0<a<W/2\).  Fix distinct positive target times along the strictly
> monotone deterministic midpoint path, disjoint target neighborhoods on
> which the deterministic relative path remains at least \(\eta>0\) inside
> the minimum-image contact ball, and a nonempty compact simplex-interior
> weight set \(\mathcal W\) with \(w_j\ge w_{\min}>0\).  Assume
> \(s_0^2<D_0/\gamma\) and \(u_0^2<4D_0/\gamma\).  For the normalized
> longitudinal slabs of width \(\epsilon\rho\) and the exact quotient Doi
> model on
> \(\mathbb R^2\times\mathbb T_W^{d-1}\), there exists
> \(\epsilon_0=\epsilon_0(d,m,\text{all frozen data},\mathcal W)>0\) such
> that for every \(0<\epsilon<\epsilon_0\) there exists
> \(B_0=B_0(d,m,\text{all frozen data},\mathcal W,\epsilon)>0\) such that,
> for every \(0<B<B_0\) and every \(w\in\mathcal W\), the exact continuum
> reaction-time density has exactly one nondegenerate local maximum in each
> of the \(m\) named target intervals and therefore at least \(m\) local
> maxima, with at least one intervening local minimum between consecutive
> target intervals.

Required immediately adjacent boundary sentence:

> The statement is pointwise in the fixed finite integers \(d\) and \(m\):
> no constant is uniform in either, the geometry and slab family may depend
> on both, \(\epsilon\) is fixed before \(B\), extra extrema are not
> excluded, no absolute event-mass floor is obtained, and the result concerns
> longitudinal slabs rather than arbitrary localized catalyst geometries.

Optional separate corollary:

> With the transverse coordinate and covariance omitted, the same conclusion
> holds in physical \(d=1\), where contact is \(|R_\parallel|<a\) and
> \(W^0=1\).

An equivalent fully explicit quantifier skeleton is

\[
 \forall d\in\mathbb N_{\ge2}\ \forall m\in\mathbb N_{\ge1}\
 \forall\mathscr D_{d,m}\;[\mathsf H(\mathscr D_{d,m})\Rightarrow
 \exists\epsilon_0(d,m,\mathscr D_{d,m})>0\
 \forall\epsilon\in(0,\epsilon_0)\
 \exists B_0(d,m,\mathscr D_{d,m},\epsilon)>0\
 \forall B\in(0,B_0)\ \forall w\in\mathcal W:\mathsf P_m].
\]

The data quantifier precedes \(\epsilon_0\); \(d\) and \(m\) are not
allowed to vary after either smallness threshold has been chosen.

## 6. Required proof and manuscript changes before promotion

1. **Add the outer fixed-dimension theorem.**  State the semigroup proposition,
   differentiated-tail lemma, and direct theorem for each fixed finite integer
   \(d\ge2\).  Index all potentially dimension-dependent constants by \(d\).
2. **Make the quotient proof dimension-general.**  Add the diagonal-Haar
   quotient identity from Sec. 4.1.  This avoids relying on an ill-defined
   global transverse midpoint on the torus.
3. **Make the resource factor explicit.**  Display the common-centre integral
   that produces \(W^{-(d-1)}\), and say that it does not normalize relative
   contact volume.
4. **Consolidate the cut-locus proof.**  Replace the compressed
   minimum-image/nonzero-image wording in the article appendix and theorem note
   by Eq. (G77.1), an all-lifts bound, and a fixed-dimensional lattice-shell
   summability statement.  The current Supplement already contains most of
   this proof and should become the authoritative version.
5. **Close the semigroup form statement.**  Specify the weighted periodic
   \(H^1\) form domain for arbitrary fixed \(d\), the normalized torus factor
   in \(\pi_d\), and that bounded perturbation uses no dimension-restricted
   Sobolev estimate.
6. **Size the transverse data.**  Declare
   \(r_{\perp,0}\in\mathbb T_W^{d-1}\) and
   \(\Sigma_{\perp,0}\in\mathbb R^{(d-1)\times(d-1)}\) positive definite.
   State explicitly that its wrapped density is in the invariant weighted
   space only pointwise in fixed \(d,\epsilon\).
7. **Propagate the exact quantifiers.**  Update the abstract, introduction,
   theorem heading, proof appendix, Supplement abstract/heading/theorem, gate
   ledger, and discussion consistently.  Do not leave one occurrence saying
   “only \(d=2,3\)” after promoting the theorem.
8. **Preserve the physical evidence boundary.**  Keep every finite-parameter
   and positive-budget numerical claim restricted to the dimensions actually
   computed.  The general theorem must not turn the current \(d=2,3\)
   numerical evidence into an all-dimensional numerical claim.
9. **Add the non-uniformity/units sentence.**  Explicitly deny uniformity in
   \(d\), \(d\to\infty\), and cross-dimensional comparison of dimensional
   \(B\), \(B_0\), amplitudes, or event masses.
10. **Treat \(d=1\) separately or omit it.**  If retained, use the exact
    corollary wording above; do not force empty transverse objects into the
    main theorem.

No new scientific producer, high-dimensional numerical example, or formal
verification is required to establish this fixed-\(d\) analytical extension.
The revised proof should nevertheless receive one independent post-edit
line-by-line audit because G77-2 is a genuine proof-presentation trap.

## 7. What the extension does and does not buy scientifically

The useful structural conclusion is

\[
 \text{fixed finite }d
 \quad\Longrightarrow\quad
 \text{same local Gaussian channel mechanism, with }d
 \text{ entering only constants/contact corrections}.
\]

This supports a clean statement that the constructive multimode mechanism is
not peculiar to disks or spheres.  It also explains why the leading balancing
weights are independent of \(d\): contact is asymptotically saturated and
\(W^{-(d-1)}\) is common to all channels.

The same observation limits the novelty gain.  The result does not reveal a
new high-dimensional encounter transition; it suppresses nontrivial
approach/separation dynamics at the designed peaks.  It gives no
dimension-uniform observability window, and higher-dimensional event mass can
become small through dimension-dependent constants even though local modes
exist.  Therefore the best PRR use is:

- main theorem or corollary: “every fixed finite integer dimension,” with the
  complete scope sentence;
- physical headline and figures: retain the actually evaluated \(d=2,3\)
  systems; and
- promotion priority: continue to place finite-\(B\) same-family catastrophe
  structure and independent killed-process validation ahead of any
  high-dimensional numerical scan.

## 8. Final decision

- General fixed-finite-\(d\ge2\) semigroup bridge: **MATHEMATICALLY PASS**.
- General fixed-finite-\(d\ge2\) direct mode theorem: **MATHEMATICALLY PASS**.
- Separate physical-\(d=1\) corollary: **MATHEMATICALLY PASS, OPTIONAL**.
- Uniform-in-\(d\), \(d\to\infty\), or dimension-independent \(B_0\):
  **NOT PROVED / NOT ADMISSIBLE**.
- Current manuscript promotion to the all-fixed-finite-\(d\) wording:
  **HOLD pending G77-1--G77-5 repair and independent post-edit audit**.
- Effect on overall PRR scientific release: **NO CHANGE; HOLD remains for the
  existing finite-parameter positive-budget gates**.

