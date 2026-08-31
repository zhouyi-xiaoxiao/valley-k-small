# Round 01 adversarial theory audit

**Target:** notes/theorem_program.md  
**Scope:** Theorem 2.1, Lemma 3.1, Theorem 4.1, and the GIG normalization/weight asymptotics used by Theorem 4.1  
**Overall verdict:** **MAJOR**

The main construction is plausible and, in my assessment, probably true for every fixed finite $m$. However, the current argument does not prove the uniform estimates that turn the large-separation heuristic into Theorem 4.1, and it does not justify the claim that a computable (let alone smallest) $R_{\mathrm{sep}}$ has been obtained. Theorem 4.1 must therefore not be labelled **PROVED** in its present form. Theorem 2.1 passes; Lemma 3.1 passes in its literal, weak form, with a proof-language correction.

## 1. Verdict matrix

| Item | Verdict | Reason |
|---|---|---|
| Theorem 2.1, projected minimum-norm formula | **PASS** | The displayed operator is the correct $M$-orthogonal tangent projection, and the formula satisfies both constraints and the KKT minimum-norm condition. |
| Lemma 3.1, one maximum per channel interval | **PASS** | Endpoint derivative dominance and uniform negative curvature give exactly one nondegenerate maximum in each $I_j$. |
| Lemma 3.1, intervening minima | **PASS / MINOR wording** | No tail estimate is needed for the stated local-minimum conclusion. Analyticity is not part of the lemma and is not needed. The lemma does not imply isolated or nondegenerate minima. |
| Theorem 4.1, existence for sufficiently large $R$ | **MAJOR proof gap** | The conclusion is credible, but uniform own-channel curvature and cross-channel derivative estimates are asserted rather than bounded with constants. |
| “Computable $R_{\mathrm{sep}}$” and “smallest number” | **MAJOR / unsupported** | Closed-form functions do not by themselves give a certified threshold valid for every larger $R$; no monotone envelope, interval certificate, or explicit inequalities are supplied. |
| GIG normalization, unique mode, peak-height asymptotic | **PASS** | All are correct, subject to making clear that the peak asymptotic is an $M\to\infty$ statement. |
| Weight asymptotics | **PASS / MINOR qualification** | The order statements are correct for fixed $m,p,\beta$, but the $j=1$ prefactor is not given by the large-$M$ formula because $\mu_1=1$. |
| Evidence label for Theorem 4.1 | **MAJOR** | Downgrade from **PROVED** to **PROOF SKETCH / CONJECTURAL** until the quantified estimates below are supplied. |

## 2. Theorem 2.1 survives the attack

Put

$$
d=c^\top M^{-1}c,
\qquad
P=I-\frac{M^{-1}cc^\top}{d}.
$$

Then $P$ is the $M$-orthogonal projector onto

$$
T=\{h:c^\top h=0\},
$$

and the theorem's projected jet matrix is exactly

$$
\widetilde G=GP.
$$

Although $P$ is generally not Euclidean-symmetric, it has the identities needed here:

$$
c^\top P=0,
\qquad
\widetilde G M^{-1}c=0,
\qquad
Gh=\widetilde Gh \quad(h\in T).
$$

For

$$
h^*=M^{-1}\widetilde G^\top
  (\widetilde G M^{-1}\widetilde G^\top)^{-1}y,
$$

one obtains directly

$$
c^\top h^*=0,
\qquad
Gh^*=\widetilde Gh^*=y.
$$

If $\operatorname{rank}\widetilde G=q$, the Gram matrix
$\widetilde G M^{-1}\widetilde G^\top$ is positive definite. The usual
Lagrange-multiplier/KKT calculation on $T$ then gives $h^*$ as the unique
minimizer of $\frac12h^\top Mh$. Thus neither the projection nor the
minimum-norm formula needs correction.

Two scope qualifications should remain visible:

1. This is an infinitesimal theorem. For arbitrary finite-amplitude $y$, the update $u+h^*$ need not remain in the positive simplex; the text should not silently promote it to a global finite-control theorem.
2. The natural conditioning diagnostic is $\sigma_{\min}(\widetilde G M^{-1/2})$, not just algebraic rank. The note already points in this direction.

There is also a modelling issue separate from the algebra: if
$c_j=\int_{\mathcal D}\Psi_j$ is used, it measures integrated exposure in
configuration space, not automatically the physical amount of catalyst on a
centre-space patch. Boundary clipping and the contact coordinate map can make
the two differ. For physical claims, the cost vector must be reconciled with
the centre-space material budget used elsewhere in the programme. This does
not invalidate Theorem 2.1 as linear algebra.

## 3. Lemma 3.1 is valid only in the literal form stated

### 3.1 Maxima inside the channel intervals

At the left and right endpoints of $I_j$, the hypotheses give

$$
F'(\ell_j)\ge 2\eta_j-\eta_j=\eta_j>0,
\qquad
F'(r_j)\le -2\eta_j+\eta_j=-\eta_j<0.
$$

On the whole interval,

$$
F''\le -2\kappa_j+\kappa_j=-\kappa_j<0.
$$

Hence $F'$ is strictly decreasing and crosses zero exactly once. The
critical point is a nondegenerate local maximum. This part is complete.

### 3.2 A minimum between adjacent intervals needs no tail bound

On the compact gap $[r_j,\ell_{j+1}]$, $F$ attains a minimum. Because
$F'(r_j)<0$, the left endpoint cannot minimize the gap; because
$F'(\ell_{j+1})>0$, the right endpoint cannot minimize it. Therefore at
least one minimizer lies in the interior and is a local minimum of $F$.

No estimate as $\tau\downarrow0$ or $\tau\to\infty$ is required for this
statement. Tail bounds become necessary only for stronger conclusions such
as:

- exactly $m$ maxima on the entire positive axis;
- no additional tail critical points;
- one isolated or nondegenerate minimum in every separator.

The proof's appeal to “analytic channel laws” should be removed from the
general $C^2$ lemma. A $C^2$ function may be flat on a subinterval of the
separator while satisfying the endpoint signs; every point of that flat piece
is then a local minimum, so the stated conclusion remains true. Even
analyticity does not imply nondegeneracy: $F(x)=x^4$ has an analytic,
isolated, degenerate minimum. Any later use of simple alternating critical
points needs an additional transversality or positive-curvature hypothesis.

## 4. Exact GIG identities: what is correct

For one channel, write its prescribed mode as $M>0$,

$$
A_M=\beta M^2+pM,
\qquad
\gamma_M(\tau)=Z_M^{-1}\tau^{-p}
  e^{-A_M/\tau-\beta\tau}.
$$

The normalization is finite (indeed for every real $p$, not only $p>1$) and
has the exact Bessel representation

$$
Z_M=2\left(\frac{A_M}{\beta}\right)^{(1-p)/2}
K_{1-p}\!\left(2\sqrt{\beta A_M}\right).
$$

The log derivative factors exactly as

$$
(\log\gamma_M)'(\tau)
=\frac{A_M-p\tau-\beta\tau^2}{\tau^2}
=\frac{(M-\tau)[\beta(M+\tau)+p]}{\tau^2}.
$$

Thus $M$ is the unique positive mode. Defining the peak-normalized channel
$h_M(\tau)=\gamma_M(\tau)/\gamma_M(M)$, and setting $x=\tau/M$, gives the
particularly useful exact identity

$$
\boxed{
\log h_M(Mx)
=-\beta M\left(x+x^{-1}-2\right)
-p\left(\log x+x^{-1}-1\right).
}
$$

Both bracketed functions are nonnegative and vanish only at $x=1$. This is
the right starting point for a rigorous separation proof; it controls both
tails without informal Taylor notation.

The peak-height asymptotic

$$
\gamma_M(M)=\sqrt{\frac{\beta}{\pi M}}
\left[1+O(M^{-1})\right]
$$

is correct as $M\to\infty$, by either the Bessel expansion or Laplace's
method. Consequently, if $a_j=1/\gamma_{\mu_j}(\mu_j)$, then for $j\ge2$

$$
a_j\sim\sqrt{\frac{\pi\mu_j}{\beta}}
\qquad(R\to\infty),
$$

whereas $a_1=1/\gamma_1(1)$ is an exact fixed constant. In particular,

$$
w_1\sim
\frac{1}{\gamma_1(1)}
\sqrt{\frac{\beta}{\pi\mu_m}}
=C_{p,\beta}R^{-(m-1)/2},
$$

and the order assertion in the note is correct. What is not justified is a
uniform ratio-$1$ replacement of every $a_j$ by
$\sqrt{\pi\mu_j/\beta}$, because $\mu_1$ never tends to infinity. The use
of $\asymp$, rather than $\sim$, avoids this error.

## 5. The decisive gap in Theorem 4.1

### 5.1 “Small fixed δ” is not enough without an explicit restriction

Let $L_M=\log h_M$. The exact derivatives are

$$
L_M'(\tau)
=\frac{(M-\tau)[\beta(M+\tau)+p]}{\tau^2},
\qquad
L_M''(\tau)
=-\frac{2A_M}{\tau^3}+\frac{p}{\tau^2},
$$

and

$$
\frac{h_M''}{h_M}=(L_M')^2+L_M''.
$$

At an endpoint $\tau=M+\delta\sqrt M$, for fixed $\delta$,

$$
M\frac{h_M''(M+\delta\sqrt M)}
        {h_M(M+\delta\sqrt M)}
\longrightarrow 4\beta^2\delta^2-2\beta.
$$

Therefore curvature is eventually negative at that endpoint only if

$$
\delta<\frac{1}{\sqrt{2\beta}}
$$

(with a strict safety margin needed for a uniform infimum). This is a concrete
failure mode for an unquantified choice: for example, $\beta=100$ and
$\delta=0.1$ give the positive limiting value $200$, so $h_M''>0$ near
the proposed endpoint for all sufficiently large $M$. The theorem says
“sufficiently small”, so this does not refute the intended theorem, but it does
show that the missing condition is essential and depends on $\beta$.

Likewise,

$$
\sqrt M\,|h_M'(M\pm\delta\sqrt M)|
\longrightarrow 2\beta\delta e^{-\beta\delta^2},
$$

while, under a strict curvature restriction,

$$
\inf_{|\tau-M|\le\delta\sqrt M}|h_M''(\tau)|
\asymp M^{-1}.
$$

These scales are exactly the denominators needed in (4.12), but the note does
not establish uniform lower bounds with constants. The fixed channel
$M=\mu_1=1$ must also be checked separately on its compact interval; it is
not covered by a large-$M$ expansion.

### 5.2 Cross-channel smallness is plausible but is not yet a proof

For channel $i$, put $x=\tau/\mu_i$ in the boxed identity above. On an
interval around $\mu_j$:

- if $i<j$, then $x\asymp R^{j-i}$ and the exponent contains a negative
  term of order $-\beta\tau$;
- if $i>j$, then $x\asymp R^{-(i-j)}$ and the exponent contains a negative
  term of order $-\beta\mu_i^2/\tau$.

The derivative prefactors are only rational/polynomial in the scale ratio, so
the exponential suppression should dominate the own-channel margins
$\mu_j^{-1/2}$ and $\mu_j^{-1}$. For fixed finite $m$, this should yield the
required ratios tending to zero.

But (4.12) currently jumps from that asymptotic picture to simultaneous,
uniform inequalities over every $I_j(R)$. A publishable proof must provide,
for all $R\ge R_0$, explicit bounds of the form

$$
\sup_{\tau\in I_j}|h_i^{(k)}(\tau)|
\le P_{ijk}(R)\,e^{-Q_{ij}(R)},
\qquad k=1,2,
$$

with $Q_{ij}(R)>0$ increasing and explicit lower bounds

$$
|h_j'(\ell_j)|,|h_j'(r_j)|\ge c_1\mu_j^{-1/2},
\qquad
-h_j''(\tau)\ge c_2\mu_j^{-1}
\quad(\tau\in I_j).
$$

The constants must be uniform over the finite index set and must include the
$j=1$ compact case. Until those inequalities appear, Lemma 3.1 cannot be
invoked as a completed proof.

### 5.3 “Computable” and “smallest” are overclaimed

Evaluating closed expressions on a finite collection of $R$-dependent
intervals does not certify that the inequalities hold for every larger
$R$. It also does not produce the smallest such threshold. Possible
non-monotonicity of the raw suprema/infima must be controlled, and strict
inequalities need a certified margin.

A valid computability claim would require one of the following:

1. an analytic monotone envelope in $R$, followed by solving a finite list of
   scalar sufficient inequalities; or
2. interval-arithmetic certification on a finite $R$-range, plus an analytic
   tail bound proving the inequalities for all larger $R$.

Even then, the output is naturally **an explicit sufficient threshold**, not
the smallest threshold. The latter should be deleted unless a separate global
optimization and monotonicity argument is supplied.

## 6. Required repair before the theorem can be labelled PROVED

Theorem 4.1 can be promoted back to **PROVED** after all of the following are in
the manuscript or a theorem-bearing appendix:

1. Choose $\delta=\delta(p,\beta)>0$ explicitly, with a strict margin below
   $1/\sqrt{2\beta}$, and prove own-channel derivative and curvature lower
   bounds on every $I_j$.
2. Treat $\mu_1=1$ by a direct compact estimate; do not hide it in a
   $M\to\infty$ expansion.
3. Starting from the exact normalized-shape identity, derive explicit
   first- and second-derivative cross-channel envelopes for $i<j$ and
   $i>j$.
4. Take maxima/minima over the finite index set and exhibit a finite sufficient
   $R_{\mathrm{sep}}(m,p,\beta)$.
5. If “computable” is retained, provide the actual certified algorithm or an
   explicit formula and prove that it covers every $R\ge R_{\mathrm{sep}}$.
   Replace “smallest” by “a sufficient”.
6. State the peak asymptotic only for channels whose modes tend to infinity,
   and keep the $j=1$ constant exact.
7. Keep the minimum conclusion at its current weak level, or add a genuine
   transversality/positive-curvature condition before claiming isolated or
   nondegenerate separator minima.

## 7. Final adversarial decision

- **Theorem 2.1:** retain **PROVED**.
- **Lemma 3.1:** retain **PROVED** for exactly the stated conclusions; revise
  the proof language about analyticity and do not infer nondegenerate minima.
- **Theorem 4.1:** downgrade to **PROOF SKETCH / CONJECTURAL**. No explicit
  counterexample was found to the intended sufficiently-small-$\delta$,
  sufficiently-large-$R$ theorem, but the current text does not contain the
  uniform estimates needed to prove it.
- **GIG normalization, mode, and leading peak asymptotic:** retain as correct,
  with the $M\to\infty$ and $\mu_1=1$ qualifications above.

This is a proof-completeness failure, not evidence that the core GIG
construction is wrong. The exact scale-free identity for $h_M$ makes the
repair tractable and should replace the present informal Taylor/separation
paragraphs.
