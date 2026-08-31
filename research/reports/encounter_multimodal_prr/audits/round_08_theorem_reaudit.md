# Round 08 independent re-audit of Theorem 4.1

Date: 2026-07-13  
Audited source: `notes/theorem_program.md`, especially Lemma 3.1 and
Section 4.1, lines 300--689.  
Audit action: proof review and independent numerical falsification attempts
only. No theorem, manuscript, code, or data artifact was modified.  
Independence rule: this audit did not read or rely on the Round 07 verdict.

## Verdict

**PASS: the label `PROVED within the GIG mixture class` can be maintained.**

I found no P0 or P1 gap in the existence proof. The exact shape identity,
compact expansion, fixed first-channel treatment, cross-channel exponent
constants, polynomial derivative bounds, unified envelope, all-larger-$R$
quantifier, Lemma 3.1 margins, and mixture normalization close consistently.
The proof establishes precisely what Theorem 4.1 states: for each fixed finite
$m\geq1$, fixed $p>1$, and fixed $\beta>0$, all sufficiently large geometric
separations produce at least $m$ nondegenerate local maxima and at least
$m-1$ intervening local minima in the normalized ideal GIG mixture.

Three P2 clarifications are recommended before journal circulation:

1. state $m\in\{1,2,\ldots\}$ rather than relying on a convention for
   $\mathbb N$;
2. in the cross-channel paragraph, write
   $N(\tau/N+N/\tau-2)=(\tau-N)^2/\tau$; the bracket alone has an additional
   factor $1/N$; and
3. add one sentence that $0<Z_j<\infty$, hence $w_j>0$ and
   $\sum_jw_j=1$.

None changes the proof or requires downgrading `PROVED`.

## Resolution

All three P2 clarifications were applied to `notes/theorem_program.md` after
this independent review: the positive-integer convention is explicit,
\(0<Z_j<\infty\) and weight normalization are stated, and the cross-channel
identity now includes the required prefactor \(N\). No scientific claim or
evidence label changed.

## 1. Claim and quantifiers actually audited

Theorem 4.1 fixes

\[
 m\geq1,\qquad p>1,\qquad \beta>0,
 \qquad \mu_j=R^{j-1},
 \qquad \mathcal A_j=\beta\mu_j^2+p\mu_j,
\]

and defines normalized densities

\[
 \gamma_j(\tau)=Z_j^{-1}\tau^{-p}
 e^{-\mathcal A_j/\tau-\beta\tau}
\]

with inverse-height weights. The theorem is an eventual statement:

\[
 \exists R_{\rm sep}(m,p,\beta)<\infty\quad
 \forall R\geq R_{\rm sep},
\]

not a claim for every $R>1$, not a computed smallest threshold, and not a
bound uniform in $m,p,$ or $\beta$.

## 2. Exact single-channel identities

### 2.1 Mode and normalized shape

For a channel with prescribed mode $M$,
$\mathcal A_M=\beta M^2+pM$. Its logarithmic derivative factors as

\[
 L_M'(\tau)
 =\frac{\mathcal A_M}{\tau^2}-\frac p\tau-\beta
 =\frac{(M-\tau)[\beta(M+\tau)+p]}{\tau^2}.
\]

The second factor is positive for $\tau>0$, so $M$ is the unique positive
mode, with the correct derivative signs on either side.

Taking the log ratio at $\tau=Mx$ gives

\[
\begin{aligned}
 \log\frac{\gamma_M(Mx)}{\gamma_M(M)}
 &=-p\log x-(\beta M+p)(x^{-1}-1)-\beta M(x-1)\\
 &=-\beta M(x+x^{-1}-2)
   -p(\log x+x^{-1}-1).
\end{aligned}
\]

Thus Eq. (4.9) is exact. Both shape functions are nonnegative for $x>0$ and
vanish only at $x=1$:

- $x+x^{-1}-2=(x-1)^2/x\geq0$;
- $\log x+x^{-1}-1$ has derivative $(x-1)/x^2$ and its unique minimum zero
  at $x=1$.

An apparent large residual occurs if the two unnormalized log densities are
subtracted directly in double precision at extreme $M$ and $x$; that is
catastrophic cancellation, not a failure of Eq. (4.9). A separate 80-digit
`Decimal` check over 10,000 random cases spanning
$\beta\sim10^{-8}$--$10^5$, $M\sim1$--$10^{12}$, and
$x\sim10^{-6}$--$10^6$ gave maximum relative discrepancy
$2.66\times10^{-75}$.

### 2.2 Exact compact rescaling

Put $\tau=M+y\sqrt M$ and $s=y/\sqrt M$. Direct substitution gives

\[
 M(x+x^{-1}-2)=\frac{y^2}{1+s},
\]

and hence the first identity in Eq. (4.10). The derivative identities also
check exactly:

\[
 \sqrt M L_M'
 =-y\frac{2\beta+\beta y/\sqrt M+p/M}{(1+s)^2},
\]

\[
 ML_M''
 =-\frac{2(\beta+p/M)}{(1+s)^3}
  +\frac{p/M}{(1+s)^2},
\]

with $Mh_M''/h_M=(\sqrt M L_M')^2+ML_M''$.

For fixed $|y|\leq\delta$, the right-hand sides are smooth in
$(y,M^{-1/2})$ on a compact set containing $M^{-1/2}=0$. Since
$\delta<1/4$ and $M\geq1$, one even has $1+s\geq3/4$, stronger than the
displayed $1/2$ bound. Taylor's theorem on this compact set therefore gives all
four $O(M^{-1/2})$ remainders uniformly in $y$. No pointwise-to-uniform gap is
present.

## 3. Curvature interval and the fixed $M=1$ channel

At the mode,

\[
 h_1''(1)=L_1''(1)=-(2\beta+p)<0.
\]

Continuity gives a positive $\delta_c$ on which $h_1''<0$. Choosing

\[
 0<\delta<\min\left\{\frac14,\frac1{\sqrt{2\beta}},\delta_c\right\}
\]

keeps the interval positive, preserves the exact first-channel derivative
signs, and makes the compact margins $a_1,b_1$ strictly positive. This is a
complete separate treatment of $M=1$; no large-$M$ statement is applied to it.

For large $M$, the uniform limit on $|y|\leq\delta$ is

\[
 M\frac{h_M''}{h_M}
 \longrightarrow 4\beta^2y^2-2\beta
 \leq-\kappa_0,
 \qquad
 \kappa_0=2\beta-4\beta^2\delta^2>0.
\]

Uniform convergence permits one $M_*$ such that, simultaneously over the full
interval,

- $h_M\geq\tfrac12e^{-\beta\delta^2}$;
- the endpoint values of $\sqrt M L_M'$ have the correct signs and magnitude
  at least $\beta\delta$; and
- $Mh_M''/h_M\leq-\kappa_0/2$.

Multiplication gives exactly

\[
 c_1=\tfrac12\beta\delta e^{-\beta\delta^2},
 \qquad
 c_2=\tfrac14\kappa_0e^{-\beta\delta^2},
\]

and Eq. (4.12). The strict condition
$\delta<1/\sqrt{2\beta}$ is sufficient and genuinely needed for this
particular $\sqrt M$-width concavity construction because the endpoint limit is
$4\beta^2\delta^2-2\beta$.

## 4. Interval ordering

The intervals $I_M=[M-\delta\sqrt M,M+\delta\sqrt M]$ are positive. For
successive centres $M$ and $MR$, their gap factors as

\[
 M(R-1)-\delta\sqrt M(\sqrt R+1)
 =(\sqrt R+1)\sqrt M\,[\sqrt M(\sqrt R-1)-\delta].
\]

Because $M\geq1$, this is positive whenever $\sqrt R>1+\delta$. The later
choice $R\geq8$ automatically satisfies this. Thus the intervals are ordered
and disjoint uniformly over the finite channel index set.

## 5. Cross-channel exponential bounds

For a cross-channel centre $N$,

\[
 Q_N(\tau)=\beta\frac{(\tau-N)^2}{\tau}
 +p\left(\log\frac\tau N+\frac N\tau-1\right),
 \qquad h_N=e^{-Q_N}.
\]

The second term is nonnegative. Since
$I_M\subset[M/2,3M/2]$, the two claimed constants follow.

### 5.1 Earlier channel

If $N\leq M/R$ and $R\geq8$,

\[
 \frac{(\tau-N)^2}{\tau}
 =\tau-2N+\frac{N^2}{\tau}
 \geq\tau-2N
 \geq\frac M2-\frac{2M}{R}
 \geq\frac M4.
\]

Therefore $Q_N\geq\beta M/4$.

### 5.2 Later channel

If $N\geq MR$ and $R\geq3$, then $N>\tau$. The function
$(N-\tau)^2/\tau$ increases with $N$ and decreases with $\tau$ in this range,
so

\[
 \frac{(N-\tau)^2}{\tau}
 \geq\frac{(MR-3M/2)^2}{3M/2}
 =\frac{2M}{3}(R-3/2)^2
 \geq\frac{MR^2}{6}.
\]

The last inequality is equivalent to $2(R-3/2)\geq R$ and is valid for
$R\geq3$. Therefore $Q_N\geq\beta MR^2/6$. Both exponent constants in the
proof are valid.

The sentence preceding these bounds should be made dimensionally exact:
the bracket $\tau/N+N/\tau-2$ equals $(\tau-N)^2/(N\tau)$, whereas
$N$ times that bracket equals $(\tau-N)^2/\tau$. The subsequent equations use
the correct expression, so this is P2 wording only.

## 6. Polynomial bounds for $L_N'$ and $L_N''$

Let $q=N/M$ and $u=\tau/M$. On $I_M$, $u\in[1/2,3/2]$. The exact formulas are

\[
 L_N'=\frac{\beta q^2}{u^2}
 +\frac{pq}{Mu^2}-\frac p{Mu}-\beta,
\]

\[
 L_N''=-\frac{2\beta q^2}{Mu^3}
 -\frac{2pq}{M^2u^3}+\frac p{M^2u^2}.
\]

Using $M\geq1$ and $u^{-1}\leq2$ gives

\[
 |L_N'|\leq4\beta q^2+4pq+2p+\beta,
\]

\[
 |L_N''|\leq16\beta q^2+16pq+4p,
\]

exactly as claimed.

For earlier channels $q\leq1/R<1$, these are bounded by
$D_1=5\beta+6p$ and $D_2=16\beta+20p$. For later channels $q\geq R>1$,
they are bounded by $D_1q^2$ and $D_2q^2$. Consequently

\[
 |h_N'|=h_N|L_N'|,
 \qquad
 |h_N''|\leq h_N(|L_N'|^2+|L_N''|)
\]

gives the stated $D$, $Dq^2$, and $Dq^4$ prefactors. There is no hidden
exponential dependence in these factors.

## 7. One envelope for all channels and derivatives

Fix finite $m$. For target $M_j=R^{j-1}$,
$1\leq M_j\leq R^{m-1}$, while every later ratio obeys
$q\leq R^{m-1}$.

- Earlier-channel first derivatives acquire at most $\sqrt{M_j}$ and second
  derivatives at most $M_j$ after the scaling in Eq. (4.13). For $j\geq2$,
  $M_j\geq R$, so their exponent is bounded by $e^{-\beta R/4}$.
- Later-channel first derivatives carry $\sqrt{M_j}q^2$; second derivatives
  carry $M_jq^4$. The worst latter power is
  $R^{m-1}R^{4(m-1)}=R^{5(m-1)}$, and the exponent is at most
  $e^{-\beta R^2/6}$.
- There are at most $m-1$ cross channels.

Therefore

\[
 E_R=(m-1)D R^{5(m-1)}
 \left(e^{-\beta R/4}+e^{-\beta R^2/6}\right)
\]

simultaneously bounds both scaled derivative sums for every target channel.
For $j=1$ there is no earlier channel; for $j\geq2$ the earlier exponential
uses $M_j\geq R$. Thus there is no missing first-channel term.

For fixed finite $m$ and fixed $\beta>0$, exponential decay dominates the fixed
polynomial, so $E_R\to0$. Monotonicity of $E_R$ is not required: the definition
of convergence supplies a threshold after which the displayed smallness bound
holds for every real $R$ beyond it. Choosing

\[
 R_{\rm sep}\geq\max\{8,M_*\}
\]

also puts every nonfirst mode $M_j$ in the large-$M$ regime and ensures interval
separation. The `for every $R\geq R_{\rm sep}$` quantifier is therefore valid,
not inferred from a finite scan.

## 8. Lemma 3.1 margins

For $j=1$, set $\eta_1=a_1/4$ and $\kappa_1=b_1/4$.

- Own endpoint slopes have magnitude at least $a_1>2\eta_1$.
- Own curvature satisfies $h_1''\leq-b_1<-2\kappa_1$.
- The envelope gives cross slopes at most $a_1/4=\eta_1$ and cross curvature
  at most $b_1/4=\kappa_1$.

For $j\geq2$, set
$\eta_j=c_1/(4\sqrt{M_j})$ and $\kappa_j=c_2/(4M_j)$.

- Eq. (4.12) gives own endpoint slope magnitude at least
  $c_1/\sqrt{M_j}>2\eta_j$.
- It gives own curvature at most $-c_2/M_j<-2\kappa_j$.
- The scaled envelope gives cross slopes at most
  $E_R/\sqrt{M_j}\leq\eta_j$ and cross curvature at most
  $E_R/M_j\leq\kappa_j$.

Thus every hypothesis (3.2)--(3.5) is met simultaneously. Lemma 3.1 then gives
one unique nondegenerate maximum in each $I_{M_j}$ and at least one interior
local minimum in each separator. The separator minima are not proved isolated
or nondegenerate, and the theorem correctly does not say so.

## 9. Mixture normalization and preservation of critical points

For $\beta>0$ and
$\mathcal A_j=\beta\mu_j^2+p\mu_j>0$, the integrand defining $Z_j$ is positive
and integrable:

- $e^{-\mathcal A_j/\tau}$ dominates every power as $\tau\downarrow0$;
- $e^{-\beta\tau}$ dominates every power as $\tau\to\infty$.

Hence $0<Z_j<\infty$, each $\gamma_j$ is a probability density, and

\[
 w_j=\frac{\gamma_j(\mu_j)^{-1}}
 {\sum_k\gamma_k(\mu_k)^{-1}}>0,
 \qquad \sum_jw_j=1.
\]

Moreover,

\[
 \sum_jw_j\gamma_j(\tau)
 =\frac{\sum_j\gamma_j(\tau)/\gamma_j(\mu_j)}
 {\sum_k\gamma_k(\mu_k)^{-1}}
 =\frac{H_R(\tau)}{\sum_k\gamma_k(\mu_k)^{-1}}.
\]

The multiplier is a finite positive constant, so all critical locations,
derivative signs, and nondegeneracy are preserved. The final normalization step
is correct.

## 10. Adversarial parameter search

I tried to falsify the inequalities independently rather than testing only the
canonical pilot.

1. **Random exact-bound search.** With seed 4101, 200,000 random tuples covered
   $\beta\in[10^{-5},10^3]$, $p-1\in[10^{-4},10^3]$,
   $M\in[1,10^8]$, $R\in[8,100]$, both earlier and later channel ratios, and
   $|y|\leq\min\{0.249,0.999/\sqrt{2\beta}\}$. No violation was found in the
   exact rescaled identities, either exponent lower bound, or either polynomial
   derivative bound.
2. **Unified-envelope search.** For $m=2,\ldots,8$,
   $\beta\in\{10^{-4},10^{-2},0.1,1,10,100\}$,
   $p\in\{1.0001,2.5,10,1000\}$,
   $R\in\{8,8.01,10,30\}$, and 101 points across every channel interval, the
   exact cross-derivative sums never exceeded $E_R$. The largest observed
   left-side/$E_R$ ratio was $8.75\times10^{-8}$, confirming that the envelope
   is conservative rather than marginal.
3. **Boundary attacks.** Taking $\beta\downarrow0$, $\beta\uparrow\infty$,
   $p$ large, $\delta$ arbitrarily close to $1/\sqrt{2\beta}$, or $m$ large
   makes the existence threshold potentially enormous, but does not invalidate
   it while those parameters remain fixed and $\beta>0$. At
   $\delta=1/\sqrt{2\beta}$ the limiting endpoint curvature becomes zero, so
   the proof correctly requires a strict inequality.
4. **Excluded counterexamples.** $\beta=0$, an infinite or $R$-dependent mode
   count, arbitrary nongeometric target times, arbitrary mixture weights, and
   small $R$ are outside the theorem. They cannot be used as counterexamples to
   the stated quantifiers.

No in-scope parameter counterexample was found.

## 11. Mandatory scope limits on `PROVED`

The theorem may be cited as proved only with all of the following visible:

- $m$ is a prescribed fixed finite integer, $m\geq1$; there is no threshold
  uniform as $m\to\infty$ or when $m=m(R)$;
- $p>1$ and $\beta>0$ are fixed; no threshold uniform as $\beta\downarrow0$,
  $p\to\infty$, or over an unbounded parameter family is proved;
- modal targets are the geometric sequence $\mu_j=R^{j-1}$ and weights are the
  inverse-height weights (4.5), not arbitrary targets or controls;
- the conclusion is at least $m$ nondegenerate maxima and at least $m-1$
  intervening local minima; extra critical points are not excluded and the
  minima need not be isolated or nondegenerate;
- no explicit, computed, optimal, or practically small $R_{\rm sep}$ is
  supplied;
- no peak-height, prominence, channel-mass, or event-probability floor uniform
  in $m$ or $R$ follows; the observability no-go in Section 4.3 remains active;
- the result concerns the normalized ideal GIG mixture only. It is not a
  bounded-domain, finite-radius, Doi, Robin, reflected-path, physical-budget,
  spatial-realizability, 2D/3D continuum, fold, or cusp theorem; and
- transferring these modes to an encounter process still requires the separate
  model-to-continuum theorem and physical realization map.

## 12. Supplemental independent check of Theorem 2.1

The projected minimum-$M$-norm formula requested in the final audit check also
passes. Let $M\succ0$, let $c$ be the nonzero budget covector, and define

\[
 \widetilde G
 =G-\frac{(GM^{-1}c)c^T}{c^TM^{-1}c}.
\]

Then

\[
 \widetilde GM^{-1}c=0,
 \qquad
 Gh=\widetilde Gh\quad\text{whenever }c^Th=0.
\]

If $\operatorname{rank}\widetilde G=q$, the Gram matrix
$\widetilde GM^{-1}\widetilde G^T$ is positive definite. The proposed vector

\[
 h_*=M^{-1}\widetilde G^T
 (\widetilde GM^{-1}\widetilde G^T)^{-1}y
\]

satisfies

\[
 c^Th_*=0,
 \qquad
 Gh_*=\widetilde Gh_*=y.
\]

For any other feasible $h=h_*+z$, one has
$c^Tz=0$, $Gz=\widetilde Gz=0$, and

\[
 h_*^TMz
 =y^T(\widetilde GM^{-1}\widetilde G^T)^{-1}\widetilde Gz=0.
\]

Therefore

\[
 \|h\|_M^2=\|h_*\|_M^2+\|z\|_M^2,
\]

with equality only for $z=0$. This proves feasibility, minimum norm, and
uniqueness directly, independently of the abbreviated Lagrange-multiplier
argument in the source.

The scope restriction is essential: Theorem 2.1 is infinitesimal constrained
linear algebra at an interior control. It neither proves the model-specific
rank condition nor guarantees a finite perturbation remains in the positive
simplex. The current theorem note states both limitations correctly.

## Final decision

- **Mathematical status of Theorem 4.1:** **PROVED -- MAINTAIN**.
- **Mathematical status of Theorem 2.1 formula:** **PROVED -- MAINTAIN**.
- **P0/P1 proof defects:** none found.
- **Required before circulation:** the three P2 clarifications at the start of
  this audit and preservation of every scope limit in Section 11.
