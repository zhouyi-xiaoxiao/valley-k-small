# Round 07 adversarial audit: arbitrary-finite-m GIG proof

Date: 2026-07-13  
Target: `notes/theorem_program.md`, Theorem 4.1  
Audit mode: construct the proof, attack every uniformity step independently,
and promote the evidence label only if the attack closes.

## Verdict

**PASS within the explicit GIG mixture class.**  The gap identified in Round 01
can be closed.  Theorem 4.1 may be labelled **PROVED** for every fixed finite
`m`, fixed `p>1`, and fixed `beta>0`.

The proof is an existence proof for a finite separation threshold
`R_sep(m,p,beta)`.  It does not produce or claim a smallest threshold, does not
claim a threshold uniform in `m`, does not prove nondegenerate separator
minima, and does not provide an observability floor.  It is not a continuum Doi
theorem.

## Closed proof chain

### 1. Peak normalization removes the Bessel constants

With `M_j=R^(j-1)` and inverse-height weights,

\[
 F_R(\tau)=
 \frac{\sum_j h_{M_j}(\tau)}
      {\sum_k\gamma_k(M_k)^{-1}},
 \qquad
 h_M(\tau)=\frac{\gamma_M(\tau)}{\gamma_M(M)}.
\]

The denominator is positive and independent of time.  It is therefore enough
to prove Lemma 3.1 for `sum_j h_{M_j}`.

### 2. Exact shape and the necessary curvature restriction

The normalized channel has the exact identity

\[
 \log h_M(Mx)
 =-\beta M(x+x^{-1}-2)
  -p(\log x+x^{-1}-1).
\]

On `tau=M+y sqrt(M)`, all rescaled expressions are smooth functions of
`(y,M^(-1/2))` on compact `|y|<=delta`.  Uniformly there,

\[
 h_M(M+y\sqrt M)\to e^{-\beta y^2},
 \quad
 \sqrt M L_M'\to-2\beta y,
 \quad
 M\frac{h_M''}{h_M}\to4\beta^2y^2-2\beta.
\]

Thus the interval family
`I_M=[M-delta sqrt(M),M+delta sqrt(M)]` must use

\[
 0<\delta<1/\sqrt{2\beta}.
\]

With a strict margin, the compact convergence supplies explicit eventual
constants

\[
 c_1=\tfrac12\beta\delta e^{-\beta\delta^2},
 \qquad
 c_2=\tfrac14(2\beta-4\beta^2\delta^2)e^{-\beta\delta^2},
\]

such that the own-channel endpoint derivatives are at least
`c_1 M^(-1/2)` in magnitude and the curvature is at most `-c_2 M^(-1)`
throughout `I_M`, for every sufficiently large `M`.

### 3. The fixed first channel is handled separately

The mode `M_1=1` never enters the large-`M` regime.  Since

\[
 h_1''(1)=-(2\beta+p)<0,
\]

continuity permits a further reduction of `delta`, after which the exact
compact margins

\[
 a_1=\min\{h_1'(1-\delta),-h_1'(1+\delta)\}>0,
 \qquad
 b_1=-\sup_{I_1}h_1''>0
\]

replace every asymptotic bound for `j=1`.

### 4. Earlier channels are exponentially small uniformly on the target interval

For a target mode `M` and an earlier mode `N<=M/R`, every
`tau in I_M` lies in `[M/2,3M/2]`.  The exact nonnegative exponent obeys

\[
 Q_N(\tau)
 \ge\beta\left(\tau+N^2/\tau-2N\right)
 \ge\beta M/4
\]

for every `R>=8`.  Hence `h_N<=exp(-beta M/4)` uniformly.  The exact
log-derivative factors are bounded independently of `M` in this case, so both
the first and second cross derivatives have the same exponential envelope.

### 5. Later channels remain exponentially small after differentiation

For `N>=MR`,

\[
 Q_N(\tau)
 \ge\beta\frac{(N-\tau)^2}{\tau}
 \ge\beta MR^2/6.
\]

Writing `q=N/M`, the derivative prefactors satisfy

\[
 |L_N'|\le4\beta q^2+4pq+2p+\beta,
 \qquad
 |L_N''|\le16\beta q^2+16pq+4p.
\]

Consequently `|h_N'|` is bounded by a constant times
`q^2 exp(-beta M R^2/6)`, and `|h_N''|` by a constant times
`q^4 exp(-beta M R^2/6)`.  Since fixed finite `m` gives
`q<=R^(m-1)`, these polynomial factors cannot overcome the exponential.

### 6. One envelope closes the “for every larger R” quantifier

After summing the finite set of cross channels and inserting the own-channel
scales, the theorem note obtains

\[
 \max_j\left\{
 \sqrt{M_j}\sup_{I_{M_j}}\sum_{i\ne j}|h_{M_i}'|,
 M_j\sup_{I_{M_j}}\sum_{i\ne j}|h_{M_i}''|
 \right\}
 \le E_R,
\]

with

\[
 E_R=C_mR^{5(m-1)}
 \left(e^{-\beta R/4}+e^{-\beta R^2/6}\right)\to0.
\]

This is the decisive repair relative to Round 01.  The bound holds for all
sufficiently large real `R`, not just scanned values.  The definition of the
limit therefore supplies one `R_sep` such that all Lemma 3.1 inequalities hold
for every `R>=R_sep`.  No monotonicity of the raw numerical extrema is assumed.

## Independent attacks and disposition

| Attack | Result | Disposition |
| --- | --- | --- |
| Choose `delta` above the curvature threshold | The endpoint curvature becomes positive asymptotically | Blocked explicitly by `delta<1/sqrt(2 beta)` with strict margin |
| Hide `M_1=1` in a large-mode expansion | Invalid because `M_1` is fixed | Replaced by exact compact margins `a_1,b_1` |
| Prove density tails but ignore derivative prefactors | Would leave the Lemma 3.1 hypotheses unproved | Explicit polynomial bounds for `L_N'` and `L_N''` are included |
| Check only adjacent channels | Insufficient for arbitrary fixed finite `m` | Bounds use `q<=R^(m-1)` and sum all `m-1` cross channels |
| Establish the result along a subsequence of `R` | Does not imply every `R>=R_sep` | A single explicit envelope `E_R->0` closes the full quantifier |
| Assume the peak normalizers are harmless | Could alter derivatives if time-dependent | The inverse-height formula is reduced exactly to one positive constant times `sum h_M` |
| Infer isolated or nondegenerate separator minima | Not supplied by Lemma 3.1 | The theorem claims only intervening local minima |
| Infer observable arbitrary mode counts | Refuted by the inverse-height mass asymptotics | The observability mathematical no-go remains in force |
| Transfer the theorem directly to bounded Doi dynamics | No continuum remainder has been proved | The continuum realization remains **CONJECTURAL** |

## Numerical falsification aid

As a non-proof sanity check, 200,000 randomized parameter/scale samples covering
`beta` from `1e-6` to `1e3`, `p` just above one through order `1e2`, and
`R>=8` were tested against the analytical cross-channel inequalities.  The
smallest observed ratio of the exact exponent to the claimed lower bound was
`3.206` for earlier channels and `5.043` for later channels.  The largest
observed ratios of exact `|L'|` and `|L''|` to their polynomial upper bounds
were `0.219` and `0.142`.  These checks found no sign or constant error; the
proof rests on the displayed inequalities, not on this scan.

## Promotion decision and retained boundaries

Promotion to **PROVED** is justified only with all of the following scope
language retained:

1. `m`, `p`, and `beta` are fixed before `R` tends to infinity.
2. `R_sep` is asserted to exist; it is not advertised as smallest or computed.
3. The maxima are nondegenerate, while the intervening minima may be degenerate
   or nonisolated.
4. Additional critical points outside the certified channel intervals are not
   excluded.
5. Peak visibility, channel mass, and event-count observability are not uniform
   in `m` or `R`.
6. The result concerns the normalized GIG mixture only.  Physical catalyst
   realization and continuum jet transfer remain separate gates.

With these restrictions, no unresolved mathematical gap remains in Theorem
4.1 at the level stated in `notes/theorem_program.md`.
