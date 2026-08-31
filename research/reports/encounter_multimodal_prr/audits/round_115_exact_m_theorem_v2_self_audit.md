# Round 115: self-audit of the exact-\(m\) theorem version-2 repair

Date: 2026-07-14  
Decision: **PASS SELF-AUDIT OF THE ROUND-112 MATHEMATICAL REPAIR / HOLD
MANUSCRIPT PROMOTION AND ALL POSITIVE-B SCIENCE**  
Self-assessed theorem findings: **P0 = 0, P1 = 0, P2 = 0**  
Remaining program/publication gates: **P0 = 0, P1 = 2**

## 1. Scope, bytes, and execution boundary

This audit reviewed the newly versioned theorem note

```text
notes/exact_m_mode_encounter_theorem_v2.md
635cbb8224133271179c995aca1fb8027fc1c0426e8f15e9cb850020a9fe2887
```

against the independent attack

```text
audits/round_112_exact_m_theorem_candidate_attack.md
f78dc7c704e8b3c49af7041023e274737696ca093d60cf36e1389e5f53fc6ae5
```

and the preserved version-1 candidate

```text
notes/exact_m_mode_encounter_theorem_candidate.md
014d370ae6aebc2090585cb59b390b9eb4cb081246323d43404cb3c8d3b9d460
```

The version-1 SHA is unchanged from Round 112.  No version-1 byte, manuscript
byte, F0-design byte, killed generator, finite-volume positive-budget row,
off-lattice trajectory, or Monte Carlo science result was edited or executed.

The only numerical work was a fail-closed zero-budget sanity artifact:

```text
code/exact_m_zero_budget_slow_factor_stress.py
f86ca49b6d36e88d321319015fded8ebfe2dc82609b760b0a2e5ddab1775380d

code/test_exact_m_zero_budget_slow_factor_stress.py
32f2c67fb72f04999922b672d16e6d715dfcffba3a4ff6a8ee4b99a414a9271b
```

The producer explicitly serializes
`positive_budget_evaluated = false`, constructs no killed generator, and says
that its dense sign scan is not an interval or topology certificate.

## 2. Executive result

Version 2 closes the sole Round-112 P0 in substance.  It no longer claims
that one component is exponentially dominant at a fixed
\(C\sigma^2\) crossover boundary.  Instead it uses the exact adjacent odds,
which are \(1/9\) and \(9\) at the chosen edges, obtains a posterior-variance
lower bound in the crossover, and proves signed log-slope bounds separately on
the two outer sectors.  Peak boxes, valley boxes, tails, both outer sectors,
and crossover-minus-valley sectors form an exhaustive cover of the declared
window.

The pure-mixture zero proof now establishes finiteness before invoking
generalized Rolle counting.  Weighted crossover locations, peak and valley
shift scales, \(m=1\), coordinate orientation, dimensional logarithms,
weighted-space hypotheses, endpoint signs, and the meaning of \(f_B/B\) are
all repaired.

The self-audit found no remaining internal theorem blocker.  This is not an
independent PASS: the file retains **INDEPENDENT RE-AUDIT REQUIRED**.  It also
does not promote the result into a PRR claim.  The theorem's physical contact
factor still tends to one on the whole window, and no useful positive budget
or nontrivial-contact event law has been validated.

## 3. Round-112 closure ledger

| Round-112 finding | Version-2 result | Self-audit evidence |
|---|---|---|
| P0.1 false exponential dominance and missing complement exclusion | **CLOSED IN SUBSTANCE** | Lemma 4.1 uses exact logistic adjacent odds, pair isolation, two explicit outer-sector splits, crossover integration, and tail bounds. |
| P1.1 zero count did not first establish finite roots | **CLOSED** | Lemma 3.1 proves affine-exponential tail dominance, compact containment of zeros, analyticity, then multiplicity-aware Rolle induction. |
| P1.2 Doi and weighted-space hypotheses implicit | **CLOSED** | Section 2 and Theorem 5.1 pin \(0<a<W/2\), independence, covariance positivity, \(u_0^2<4D_0/\gamma\), compact positive time, and bounded Gaussian catalysts. |
| P1.3 encounter significance overread | **CLOSED AS WORDING; EXTERNAL EVIDENCE GATE REMAINS** | Section 6 states that contact is asymptotically saturated and labels the theorem an analytical backbone. |
| P2.1 coordinate reversal ambiguity | **CLOSED** | One orientation sign transforms the mean and every catalyst centre together. |
| P2.2 \(m=1\) empty separation minimum | **CLOSED** | Every crossover definition is conditional on \(m\ge2\); the one-component proof is separate. |
| P2.3 dimensional \(\log\sigma\) | **CLOSED** | Proof coordinates and \(\sigma\) are explicitly nondimensionalized; the old logarithmic layer is not used. |
| P2.4 “normalized” density wording | **CLOSED** | \(f_B/B\) is called budget-rescaled and is not claimed to integrate to one. |

## 4. Independent re-derivation inside the self-audit

### 4.1 Finite zero count and multiplicities: PASS

The transformed derivative is

\[
 P_m(x)=\sum_{j=1}^m(a_j+b_jx)e^{\lambda_jx},
 \qquad \lambda_1<\cdots<\lambda_m,
\]

with every Gaussian coefficient \(b_j\ne0\).  After multiplication by
\(e^{-\lambda_1x}\), the first affine term controls \(-\infty\) and the last
affine-exponential term controls \(+\infty\).  Thus the real zero set is
bounded; analyticity makes it finite.  Two derivatives remove the first term
and preserve one nonzero affine factor for every other distinct exponent.
Generalized Rolle counting with multiplicity gives

\[
 N(P_m)\le N(P_m^{\rm reduced\;second\;derivative})+2
 \le 2(m-1)-1+2=2m-1.
\]

The version-1 gap at infinity is closed.

### 4.2 Adjacent-pair isolation: PASS

For \(x\in[c_j,c_{j+1}]\) and \(k<j\),

\[
 (x-c_k)^2-(x-c_j)^2
 \ge(c_j-c_k)^2>0,
\]

and the symmetric inequality holds for \(k>j+1\).  Finite centres and
\(w_k/w_j\le1/w_*\) give a uniform
\(Ce^{-q/\sigma^2}\) nonadjacent/pair ratio.  This justifies replacing the
full posterior mean and variance by the adjacent-pair quantities with an
exponentially small error on each entire gap.

### 4.3 Weighted crossover and valley scale: PASS

At

\[
 s_j=v_j+\frac{\sigma^2}{\Delta_j}log\frac{w_j}{w_{j+1}},
\]

the two adjacent posterior masses are equal.  At
\(s_j\pm(\log9/\Delta_j)\sigma^2\), their odds are exactly \(1/9\) and
\(9\).  Hence both masses are uniformly nonzero in that crossover, while

\[
 L'\ge\kappa\sigma^{-4}.
\]

At \(s_j\), \(L=-\log(w_j/w_{j+1})/\Delta_j+o(1)=O(1)\).  The pure root is
therefore \(s_j+O(\sigma^4)\).  At that root the posterior masses are
\(1/2+O(\sigma^2)\), giving

\[
 L'=\frac{\Delta_j^2}{4\sigma^4}+O(\sigma^{-2}).
\]

A bounded logarithmic time factor requires \(L=O(1)\) at its perturbed root,
so it changes the valley by another \(O(\sigma^4)\), not by an unqualified
\(O(\sigma^2)\).

### 4.4 Exhaustive complement coverage: PASS

For every gap, version 2 covers, in order:

```text
right edge of peak j
left outer sector
left crossover-minus-valley sector
valley box
right crossover-minus-valley sector
right outer sector
left edge of peak j+1
```

The near-centre part of an outer sector has single-centre exponential
dominance because it stops at the fixed quarter-gap point.  On the remaining
part, the adjacent ratio is merely \(O(1)\), but the posterior mean is still
quantitatively separated from \(x\):

\[
 c_j+\Delta_j/10-x
 \le\Delta_j/10-\Delta_j/4
 =-3\Delta_j/20
\]

on the left, with the symmetric positive bound on the right.  Inside the
crossover, integrating the \(\kappa\sigma^{-4}\) slope from the pure valley
root gives the boundary and complement margins.  Tail and peak bounds close
the two ends.  No point of \(J\) relies on the false claim that a component is
exponentially dominant a fixed \(O(\sigma^2)\) distance from a crossover.

### 4.5 Slow-factor root uniqueness and types: PASS

For

\[
 D=b+x'L,
 \qquad
 D'=b'+x''L+(x')^2L',
\]

choose the posterior-sector threshold above \((\|b\|_\infty+1)/\inf x'\).
The complement sign cannot be cancelled by \(b\).  On peak boxes,
\(L'\le-\kappa\sigma^{-2}\), so \(D'<0\) for small \(\sigma\); on valley
boxes, \(L'\ge\kappa\sigma^{-4}\), so \(D'>0\).  Opposite endpoint signs
give exactly one root per box.  At a root, \(F''=FD'\), proving its type and
nondegeneracy.  This establishes exactly \(m\) maxima and \(m-1\) minima and
excludes endpoint roots.

### 4.6 Uniformity over weights and weak-\(B\) transfer: PASS as an
existence theorem

The weight floor gives uniform odds, crossover displacement, pair-isolation,
and sector constants.  After \(\varepsilon\) is fixed, the simple ordered
root graphs are continuous over compact \(\mathcal W_{w_*}\).  Consecutive
root separations have a positive minimum.  Disjoint root tubes therefore have
uniform signed-curvature margins, while their compact complement and the two
endpoints have uniform derivative margins.

The pinned weighted-space assumptions place the fixed-\(\varepsilon\) model
under the existing mixed-jet theorem.  Uniform \(C^2(I)\) convergence is
enough to preserve all tubes and their complement.  This proves existence of
\(B_0(\varepsilon)>0\), but supplies no useful value and no uniformity as
\(\varepsilon\downarrow0\).

## 5. Deterministic zero-budget stress evidence

The repository environment used Python `3.12.13`, NumPy `2.5.1`, Pytest, and
Ruff.  The exact commands were

```text
.venv/bin/python -m pytest -q \
  research/reports/encounter_multimodal_prr/code/test_exact_m_zero_budget_slow_factor_stress.py

.venv/bin/ruff check \
  research/reports/encounter_multimodal_prr/code/exact_m_zero_budget_slow_factor_stress.py \
  research/reports/encounter_multimodal_prr/code/test_exact_m_zero_budget_slow_factor_stress.py
```

Results:

```text
5 passed
All checks passed!
status = PASS_DETERMINISTIC_B0_STRESS_NOT_A_TOPOLOGY_CERTIFICATE
positive_budget_evaluated = False
rows = 16
observed root counts = m1:1, m2:3, m3:5, m4:7
maximum |slow peak - pure peak| / sigma^2 = 0.519992969805936
maximum |slow valley - pure valley| / sigma^4 = 4.901911560785187
```

The 16 rows cover four scales for each of \(m=1,2,3,4\), including weights
at the declared `0.03` floor and an irregular four-centre geometry.  Every
observed type list alternated maximum/minimum and both endpoint signs passed.
The exact crossover fixture reproduced \(e^{-1},e^{-4},e^{-8}\), reinforcing
why constant crossover ratios must not be called
\(e^{-q/\sigma^2}\)-dominance.

This evidence only checks arithmetic consistency and the declared shift
scales.  A sign scan can miss even roots and is not used in any proof or
publication claim.

## 6. Remaining P1 program gates

### P1.1 — Independent proof re-audit is still required

This is a self-audit of a new 1006-line theorem note.  Before manuscript use,
an agent that did not write version 2 must recheck the extended-Chebyshev
tail step, every sector endpoint, uniform weight constants, moving root tubes,
and the exact hypotheses of the unbounded mixed-jet theorem.  Version 2 is not
self-promoted to an independently accepted theorem.

### P1.2 — PRR-level finite-parameter encounter evidence remains absent

The analytical model keeps the deterministic relative path inside contact on
the whole window, making \(c_{d,\varepsilon}\to1\).  No nontrivial-contact
finite-parameter case, useful common positive budget, deterministic
finite-window positive-budget certificate, or independent event-basin mass
result was produced in this task.  These are required for PRR significance
and remain separate from theorem validity.

## 7. Final decision

```text
Round-112 P0 complement gap             = CLOSED IN VERSION 2
finite-zero/multiplicity proof           = PASS SELF-AUDIT
weighted crossover and location scales   = PASS SELF-AUDIT
full posterior-sector coverage           = PASS SELF-AUDIT
slow-factor exact topology                = PASS SELF-AUDIT
weighted-space/Doi hypotheses             = PASS SELF-AUDIT
v1 preserved                              = PASS
B=0 deterministic stress                  = 5/5 PASS
positive budget evaluated                 = NO
independent theorem acceptance            = HOLD PENDING RE-AUDIT
manuscript/PRR promotion                   = HOLD
```

The next authorized action is an independent Round-116-or-later theorem
attack on the frozen version-2 SHA.  Positive-budget science is not authorized
by this self-audit.
