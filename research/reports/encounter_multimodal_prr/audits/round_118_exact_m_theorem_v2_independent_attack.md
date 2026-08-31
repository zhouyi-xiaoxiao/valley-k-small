# Round 118: independent adversarial audit of the exact-\(m\) theorem v2

Date: 2026-07-14  
Role: independent theorem, transfer, and claim-boundary attacker  
Decision: **PASS THE DECLARED MATHEMATICAL CORE / HOLD CURRENT BYTES FOR
MANUSCRIPT POLISH / HOLD PRR PROMOTION AND ALL POSITIVE-\(B\) SCIENCE**  
Theorem-byte findings: **P0 = 0, P1 = 0, P2 = 3**  
External PRR-program gates: **P0 = 0, P1 = 2**

## 1. Independence, frozen inputs, and execution boundary

I treated the version-2 proof and its self-audit as untrusted.  The frozen
bytes independently checked were

```text
notes/exact_m_mode_encounter_theorem_v2.md
635cbb8224133271179c995aca1fb8027fc1c0426e8f15e9cb850020a9fe2887

notes/exact_m_mode_encounter_theorem_candidate.md
014d370ae6aebc2090585cb59b390b9eb4cb081246323d43404cb3c8d3b9d460

audits/round_112_exact_m_theorem_candidate_attack.md
f78dc7c704e8b3c49af7041023e274737696ca093d60cf36e1389e5f53fc6ae5

audits/round_115_exact_m_theorem_v2_self_audit.md
a4886936392d8fe54562a1b61f6608d5337f405debaf8a51cd1ec760f5afe93c
```

The two results invoked by the Doi transfer were checked at

```text
notes/direct_physical_multimode_theorem.md
2b35d1b1053045220b29975d30f8b3c842d33273ca46de86b8cf7798c26a9c3d

notes/pde_mixed_jet_theorem.md
ac0e6cbb34d446d2b9ae2b52c22684ee72da7cadb04d864aacba085dff75f095
```

The pre-existing zero-budget producer and tests remained byte-identical:

```text
code/exact_m_zero_budget_slow_factor_stress.py
f86ca49b6d36e88d321319015fded8ebfe2dc82609b760b0a2e5ddab1775380d

code/test_exact_m_zero_budget_slow_factor_stress.py
32f2c67fb72f04999922b672d16e6d715dfcffba3a4ff6a8ee4b99a414a9271b
```

I added an independent mutation/adversarial test module:

```text
code/test_exact_m_zero_budget_round118_adversarial.py
205ce6dcc351b6a55654dbc9fb4824076bd434588605ac0313960398f099e035
```

No killed generator, positive-budget semigroup, finite-volume science row,
off-lattice trajectory, or Monte Carlo event law was constructed or run.
The theorem note was not edited.  The only writes from this attack are the
independent test module and this audit.

## 2. Executive verdict

The Round-112 P0 is closed.  I found no missing sector and no counterexample
to the declared fixed-finite, sequential theorem.

The repair succeeds because it no longer asks for false exponential
single-component dominance at a fixed \(O(\sigma^2)\) crossover edge.  It
uses the exact weighted adjacent odds \(1/9\) and \(9\), keeps both adjacent
posterior masses uniformly positive in the crossover, and treats the two
outer gap sectors separately.  Together with the global \(2m-1\) zero bound,
this proves the complete pure topology.  Peak boxes of width
\(O(\sigma^2)\), valley boxes of width \(O(\sigma^4)\), and a full complement
sign certificate then give the complete topology after multiplication by a
positive slow factor.

The fixed-\(\varepsilon\), weak-budget Doi transfer also survives.  The
Gaussian catalysts are bounded for each fixed positive \(\varepsilon\), the
pinned covariance inequalities put the initial density in the required
weighted space, and the existing mixed-jet theorem supplies uniform
\(C^2(I)\) convergence over the compact allocation family.  Compact disjoint
root tubes with signed curvature and complement margins are therefore stable
for some existential \(B_0(\varepsilon)>0\).

This is a PASS of the analytical backbone, not a PRR significance PASS.  The
contact factor tends to one in \(C^2\) on the theorem window, \(B_0\) is
nonconstructive and potentially extremely small, and no positive-budget
event mass has been evaluated.  Version 2 itself states these limits
correctly.

The current bytes contain three repair-only P2 defects: one raw control byte
corrupting \(\varepsilon\), one unit-budget naming ambiguity for \(G\), and
one local citation used where a direct convex-hull tail inequality is needed.
None changes the theorem, but all should be patched before copying the result
into a manuscript.

## 3. Independent zero-count and pure-mixture attack

### 3.1 Finiteness and the \(2m-1\) multiplicity bound: PASS

After multiplication by a positive Gaussian factor,

\[
 \sigma^2e^{x^2/(2\sigma^2)}H'(x)
 =\sum_{j=1}^m w_j(c_j-x)e^{-c_j^2/(2\sigma^2)}
   e^{c_jx/\sigma^2}.
\]

This is

\[
 P_m(x)=\sum_{j=1}^m(a_j+b_jx)e^{\lambda_jx},
 \qquad \lambda_1<\cdots<\lambda_m,
\]

with every \(b_j\ne0\).  Multiplying by \(e^{-\lambda_1x}\), the first
affine term has a fixed sign for all sufficiently negative \(x\), and the
last affine-exponential term has a fixed sign for all sufficiently positive
\(x\).  Hence all real zeros lie in a compact interval; real analyticity then
makes the zero set finite.

Two derivatives remove the first affine term.  For every \(j\ge2\),

\[
 \frac{d^2}{dx^2}
 [(a_j+b_jx)e^{(\lambda_j-\lambda_1)x}]
\]

is again a nonzero affine polynomial times a distinct exponential.  If
\(N(Q)\) counts finite real zeros with multiplicity, generalized Rolle gives
\(N(Q)-2\le N(Q'')\).  Induction therefore gives

\[
 N(P_m)\le 2(m-1)-1+2=2m-1.
\]

The positive multiplier preserves multiplicities.  The v1 omission at
infinity has been repaired without importing an unstated scale-space result.

### 3.2 Uniform adjacent-pair isolation: PASS

For \(x\in[c_j,c_{j+1}]\) and \(k<j\),

\[
 (x-c_k)^2-(x-c_j)^2
 =(c_j-c_k)(2x-c_j-c_k)\ge(c_j-c_k)^2.
\]

The symmetric comparison with \(c_{j+1}\) handles \(k>j+1\).  Since the
centre set is fixed and finite and \(w_k/w_j\le1/w_*\), the nonadjacent/pair
ratio is uniformly \(O(e^{-q/\sigma^2})\).  Bounded centres then give the same
order for the difference between the full and adjacent-pair posterior means
and variances.  No hidden uniformity in \(m\) is used.

### 3.3 Weighted crossover and exact odds: PASS

Let \(\Delta_j=c_{j+1}-c_j\) and

\[
 s_j=\frac{c_j+c_{j+1}}2
 +\frac{\sigma^2}{\Delta_j}\log\frac{w_j}{w_{j+1}}.
\]

Direct subtraction of the two Gaussian exponents gives

\[
 \frac{q_{j+1}(x)}{q_j(x)}
 =\exp\!\left[\frac{\Delta_j(x-s_j)}{\sigma^2}\right].
\]

Thus at
\(s_j\mp(\log9/\Delta_j)\sigma^2\) the odds are exactly \(1/9\) and
\(9\).  They are constants, not \(e^{-q/\sigma^2}\).  On the entire interval
between those edges, both adjacent full-posterior masses have a positive
uniform lower bound after the exponentially small nonadjacent correction.
Consequently

\[
 L'=\frac{\operatorname{Var}_\pi(c)}{\sigma^4}
     -\frac1{\sigma^2}\ge\kappa\sigma^{-4}>0
\]

for sufficiently small \(\sigma\), uniformly over the compact weights.

At \(s_j\), the adjacent mean is the midpoint and

\[
 L(s_j)=-\frac1{\Delta_j}\log\frac{w_j}{w_{j+1}}
        +O(\sigma^{-2}e^{-q/\sigma^2})=O(1).
\]

The uniform \(\Theta(\sigma^{-4})\) slope therefore places the pure valley
root at \(s_j+O(\sigma^4)\).  At that root the adjacent masses are
\(1/2+O(\sigma^2)\), yielding

\[
 L'(r_j)=\frac{\Delta_j^2}{4\sigma^4}+O(\sigma^{-2})>0.
\]

### 3.4 Existence, uniqueness, simplicity, and exhaustion: PASS

In a fixed \(A\sigma^2\) neighbourhood of \(c_j\), its own component is
exponentially dominant, so

\[
 L(x)=\frac{c_j-x}{\sigma^2}
      +O(\sigma^{-2}e^{-q/\sigma^2}),
 \qquad
 L'(x)=-\sigma^{-2}+O(\sigma^{-4}e^{-q/\sigma^2}).
\]

The two sides of the box have opposite signs and \(L'<0\), giving one simple
maximum near each centre.  Section 3.3 gives one simple minimum in each gap.
For small \(\sigma\), these \(m+(m-1)=2m-1\) roots lie in disjoint boxes.
The global multiplicity bound leaves no capacity for an additional real root
or a multiple constructed root.  Thus the pure mixture has exactly the
declared alternating signature on all of \(\mathbb R\), hence on \(J\), with
nonzero endpoint slopes.

For \(m=1\), no gap or minimum separation is used:
\(L=(c_1-x)/\sigma^2\) gives the unique simple maximum directly.

## 4. Independent full-sector attack

I checked the complement in its spatial order rather than accepting the
self-audit's coverage list.

### 4.1 Peak boxes and the two tails: PASS, with one citation repair

On
\(P_j=[c_j-A_{\rm p}\sigma^2,c_j+A_{\rm p}\sigma^2]\), the local expansion
above gives bounded \(|L|\), \(L'\le-\kappa\sigma^{-2}\), and the required
opposite boundary signs once \(A_{\rm p}\) is fixed above the slow-factor
threshold.

The actual outer-tail claim is even simpler than the note says.  Since every
posterior mean is in the convex hull \([c_1,c_m]\),

\[
 x\le c_1-A_{\rm p}\sigma^2
 \quad\Longrightarrow\quad
 L(x)=\frac{\bar c(x)-x}{\sigma^2}\ge A_{\rm p},
\]

and symmetrically \(L(x)\le-A_{\rm p}\) for
\(x\ge c_m+A_{\rm p}\sigma^2\).  Version 2 instead says that the local
formula (3.15) proves the same bound on the whole tails, although (3.15) was
only stated on a fixed scaled neighbourhood of a centre.  This is P2.3 below:
the claim is true, but the cited line is not the proof of the full tail.

### 4.2 Left and right outer sectors in every gap: PASS

On the left outer sector, split at \(c_j+\Delta_j/4\).  Between the peak box
and this fixed split, component \(j\) is exponentially dominant, so

\[
 \bar c-x\le-\tfrac12A_{\rm p}\sigma^2
\]

for sufficiently small \(\sigma\).  From the fixed split to the left
crossover edge, the adjacent right-component mass is at most \(1/10\), so

\[
 (c_j+\Delta_jp)-x
 \le\frac{\Delta_j}{10}-\frac{\Delta_j}{4}
 =-\frac{3\Delta_j}{20}.
\]

The nonadjacent posterior correction is exponentially small, preserving a
negative margin.  Division by \(\sigma^2\) makes \(|L|\) diverge there.
Reflecting this argument around the gap gives the positive right-sector
margin.  Compact weight ratios keep \(s_j\) within \(O(\sigma^2)\) of the
midpoint, so both fixed-quarter splits are ordered correctly for one uniform
small-\(\sigma\) threshold.

### 4.3 Crossover minus the valley box: PASS

The pure root satisfies \(L(r_j)=0\).  On the full crossover interval,
\(\kappa\sigma^{-4}\le L'\le C\sigma^{-4}\).  Hence a valley box

\[
 V_j=[r_j-A_{\rm v}\sigma^4,r_j+A_{\rm v}\sigma^4]
\]

has bounded \(|L|\), positive \(\Theta(\sigma^{-4})\) derivative, and
opposite boundary signs of any prescribed fixed magnitude after choosing
\(A_{\rm v}\) once.  Since \(\sigma^4=o(\sigma^2)\), this box is strictly
inside the crossover for all sufficiently small \(\sigma\).  Integrating
\(L'\) from \(r_j\) gives the signed lower bound on both remaining pieces of
the crossover.  No point here uses single-component dominance.

### 4.4 Coverage conclusion: PASS

The ordered union of left tail, peak boxes, both outer sectors of each gap,
crossover-minus-valley pieces, valley boxes, and right tail covers \(J\).
The boxes shrink while all centre, endpoint, and quarter-gap separations are
fixed.  Finiteness of \(m\), the positive minimum centre separation, and the
weight floor let one take every constant and the final \(\sigma_0\) uniformly
over the declared allocation family.  I found no overlap ambiguity, reversed
edge, or uncovered interval.

## 5. Slow-factor theorem and location scales

For

\[
 F(t)=a_\sigma(t)H_{\sigma,w}(x(t)),\qquad
 D=\partial_t\log F=b+x'L,
\]

one has

\[
 D'=b'+x''L+(x')^2L'.
\]

Choose the sector threshold \(K\) above
\(\|b\|_\infty/\inf x'\).  The complement sign of \(x'L\) cannot then be
cancelled by \(b\), so no complement zero exists.  Inside a peak box,
bounded \(L\) and \(L'\le-\kappa\sigma^{-2}\) make \(D'<0\); inside a
valley box, bounded \(L\) and \(L'\ge\kappa\sigma^{-4}\) make \(D'>0\).
Boundary signs therefore give exactly one simple typed root in every box.
At a root, \(F''=FD'\), so all extrema are nondegenerate.

At a slow peak root, \(L=-b/x'=O(1)\).  Integrating the
\(\Theta(\sigma^{-2})\) peak slope from the pure root gives displacement
\(O(\sigma^2)\).  The same argument with the
\(\Theta(\sigma^{-4})\) valley slope gives displacement
\(O(\sigma^4)\).  Combining this with the pure weighted-crossover expansion
gives

\[
 x(t_j^{\min})=s_j+O(\sigma^4).
\]

All constants are uniform in weights but are allowed to depend on the fixed
centre set, \(x\), the slow-factor derivative bounds, and fixed finite \(m\).
No uniformity in growing \(m\) or dimension is inferred.

## 6. Orientation, dimensions, and the \(m=1\) boundary

The orientation convention is consistent.  Since
\(\varsigma=\operatorname{sgn}\mu'\),
\(x=\varsigma\mu/\ell_0\) is increasing and
\(c_j=\varsigma\mu(t_j)/\ell_0\) is ordered.  The physical centre is recovered
as \(\varsigma\ell_0c_j=\mu(t_j)\); the trajectory and centres are never
reversed independently.

The proof variables \(x,c,\sigma\) are dimensionless.  Thus
\(\log(w_j/w_{j+1})\), \(\Delta_j(x-s_j)/\sigma^2\), and the crossover widths
are dimensionally valid.  In time variables, \(b\) and \(x'\) both have
units of inverse time, and every term in \(D'\) has units of inverse time
squared.

For \(m=1\), all gap, crossover, valley, and minimum-separation objects are
omitted.  The peak-box and tail argument remains valid without an empty
minimum.  The independent stress suite includes this case.

## 7. Weighted Doi transfer and event-density semantics

### 7.1 Exact reduction: PASS

The stationary midpoint variance
\(\varepsilon^2D_0/(2\gamma)\) convolved with a normalized slab of physical
width \(\varepsilon\rho\) gives common variance
\(\varepsilon^2S_*^2\).  Independence of midpoint and relative motion gives
the product of the Gaussian mixture and contact probability.  The
whole-window contact-interior margin supplies

\[
 c_{d,\varepsilon}=1+O(\varepsilon^{-N}e^{-q/\varepsilon^2})
 \quad\text{in }C^2(I),
\]

so the first two logarithmic time derivatives are uniformly bounded for
sufficiently small \(\varepsilon\).  The slow-factor theorem applies.

### 7.2 Weighted-space hypotheses: PASS

The midpoint initial variance coefficient obeys
\(D_0/(2\gamma)<D_0/\gamma\).  The pinned relative assumptions
\(u_0^2<4D_0/\gamma\) and \(\Sigma_{\perp,0}\succ0\), together with the
independent wrapped Gaussian transverse law, put the fixed-\(\varepsilon\)
initial density in the weighted space of Corollary 2.2.  The sharp contact
indicator and Gaussian slab are bounded multipliers for every fixed
\(\varepsilon>0\).  The positive time window avoids an initial-time
regularity claim across the contact interface.

### 7.3 Uniform fixed-\(\varepsilon\) root tubes: PASS

The existing bridge gives

\[
 \sup_w\|f_{B,\varepsilon,w}/B-G_{\varepsilon,w}\|_{C^2(I)}\to0
 \quad(B\downarrow0)
\]

for each fixed admissible \(\varepsilon\).  Simplicity makes each ordered root
continuous in \(w\).  Its graph over the compact weight family is compact;
the consecutive-root separations, endpoint slopes, root curvatures, and
complement derivative margins therefore have positive uniform minima after
choosing disjoint tubes.  \(C^2\) convergence preserves the curvature sign
throughout each tube and the first-derivative signs at its boundaries and on
the complement.  This yields one unique typed root per tube and none outside.

The argument is sequential:

```text
fix finite d, m, and all geometry
choose 0 < epsilon < epsilon_0
then choose 0 < B < B_0(epsilon)
```

There is no claimed lower bound on \(B_0\), no interchange of limits, and no
uniformity as \(\varepsilon\to0\).

### 7.4 Event-density semantics: PASS after one wording clarification

The physical density is
\(f_{B,\varepsilon,w}=B\langle V_w,q_{B,w}\rangle\).  Therefore
\(f/B\) is budget-rescaled, not probability-normalized, and multiplication by
positive \(B\) preserves stationary points.  Version 2 states this correctly
in Theorem 5.1.

Equation (2.15), however, calls \(G\) the free-exposure clock immediately
after defining the full killing field \(K_{B,w,\varepsilon}=BV_w\), while its
formula omits \(B\).  The formula is the correct bridge limit
\(G=\langle V_w,T_0q_0\rangle=B^{-1}\mathbb E[K_{B,w,\varepsilon}(X_t)]\),
not \(\mathbb E[K]\) itself.  This is a naming ambiguity, not a missing
factor in Theorem 5.1.

## 8. Deterministic stress and mutation results

Commands were run from the report directory with the repository environment:

```text
../../../.venv/bin/python -m pytest -q \
  code/test_exact_m_zero_budget_slow_factor_stress.py \
  code/test_exact_m_zero_budget_round118_adversarial.py

../../../.venv/bin/ruff check \
  code/exact_m_zero_budget_slow_factor_stress.py \
  code/test_exact_m_zero_budget_slow_factor_stress.py \
  code/test_exact_m_zero_budget_round118_adversarial.py

../../../.venv/bin/python \
  code/exact_m_zero_budget_slow_factor_stress.py --execute-b0-stress
```

Results:

```text
12 passed
All checks passed!
status = PASS_DETERMINISTIC_B0_STRESS_NOT_A_TOPOLOGY_CERTIFICATE
positive_budget_evaluated = False
rows = 16
maximum |slow peak - pure peak| / sigma^2 = 0.519992969805936
maximum |slow valley - pure valley| / sigma^4 = 4.901911560785187
```

The independent module adds:

1. exact weighted \(1/9,1,9\) odds for every adjacent pair of an irregular
   four-centre, edge-weight fixture at three scales;
2. a mutation kill showing that the unweighted midpoint has odds
   \(0.97/0.03\), not one, in the declared edge-weight case;
3. a mutation kill showing that a fixed \(C\sigma^2\) edge ratio is
   \(e^{-C}\) at four scales, not \(e^{-q/\sigma^2}\);
4. direct outer-tail sign checks from the posterior convex hull; and
5. 64 seeded cases with \(m=1,\ldots,6\), irregular gaps, weights spanning
   three orders of magnitude, and independently randomized four-harmonic
   positive slow factors.  Every dense scan had exactly \(2m-1\) strict
   alternating crossings and the required endpoint signs.

These are arithmetic and mutation checks only.  Dense scans can miss even
roots and are not used to prove topology.

## 9. Open findings and exact patches

### P2.1 — Raw vertical-tab byte corrupts equation (2.4)

At byte offset 3733, line 112 contains ASCII `0x0B` followed by `arepsilon`:

```text
\text{wrapped }N(r_{\perp,0},<0x0B>arepsilon^2\Sigma_{\perp,0}).
```

Required exact patch: replace `<0x0B>arepsilon` by `\varepsilon`.  Run a
control-character scan after the edit.  The intended covariance is clear and
was audited as \(\varepsilon^2\Sigma_{\perp,0}\), so this does not change the
mathematics.

### P2.2 — Name \(G\) as the unit-budget free exposure

Required exact patch near (2.15): replace “exact free-exposure clock” by
“exact unit-budget free-exposure clock” and add

\[
 G_{\varepsilon,w}
 =B^{-1}\mathbb E[K_{B,w,\varepsilon}(Z_t,R_t)]
 =\langle V_w,T_0(t)q_0\rangle.
\]

This prevents a reader from treating the missing \(B\) in (2.15) as an
algebra error.  Keep the “budget-rescaled, not normalized” sentence in
Theorem 5.1.

### P2.3 — Replace the outer-tail citation by the convex-hull inequality

Required exact patch in Lemma 4.1: do not cite the locally stated (3.15) for
the entire outer tails.  Add

\[
 \bar c(x)\in[c_1,c_m],\quad
 x\le c_1-A_{\rm p}\sigma^2\Rightarrow L\ge A_{\rm p},\quad
 x\ge c_m+A_{\rm p}\sigma^2\Rightarrow L\le-A_{\rm p}.
\]

This closes the citation scope in one line and is uniform without an
isolation estimate.

## 10. PRR boundary and final gate

The frozen theorem is independently accepted under exactly these limits:

- fixed finite \(d\ge2\) and fixed finite \(m\);
- a compact positive time window and compact simplex-interior weights;
- ordered narrow Gaussian slabs with conserved installed allocation;
- whole-window contact interior, hence asymptotically saturated contact;
- first small \(\varepsilon>0\), then an existentially small positive
  \(B<B_0(\varepsilon)\); and
- no statement outside the declared finite window.

It does not show a dimension-driven mechanism, arbitrary-patch universality,
one fixed geometry with unbounded mode count, a useful finite budget, or a
nonnegligible event mass.

The exact disposition is

```text
global 2m-1 zero/multiplicity bound             = PASS INDEPENDENT
weighted crossover and adjacent odds             = PASS INDEPENDENT
pair isolation and all complement sectors        = PASS INDEPENDENT
existence/uniqueness/simplicity and endpoint tails= PASS INDEPENDENT
peak O(sigma^2) and valley O(sigma^4) shifts      = PASS INDEPENDENT
m=1, orientation, and dimensional consistency     = PASS INDEPENDENT
fixed-epsilon weighted Doi C2 transfer             = PASS INDEPENDENT
current theorem bytes for direct manuscript paste = HOLD FOR THREE P2 PATCHES
positive-budget science authorization             = NO
PRR promotion                                      = HOLD
```

After applying only the three exact P2 patches, a checksum/control-character
check and targeted textual verification are sufficient for the theorem note;
the mathematical proof does not require another full redesign.

The two external P1 program gates remain:

1. a fixed finite-parameter, nontrivial-contact result at one usable common
   positive budget with a deterministic full-window root/complement
   certificate; and
2. independent process-level survival and event-basin mass validation under
   the same geometry, transport, initial law, supports, and installed budget.

Round 118 does not authorize either positive-budget run.  Those runs remain
behind the separate F0 method and selector audits.  Passing this theorem
audit only makes the exact-\(m\) result eligible to serve as the analytical
spine once the three P2 text repairs are applied.
