# Budget-projected modality susceptibility

## Scope

This note upgrades the finite encounter result from a one-parameter
continuation to a local inverse-design statement.  It asks which infinitesimal
redistribution of a fixed killing budget changes the derivative of the
reaction-time density most strongly at a declared time.  The result is exact
for a finite killed continuous-time Markov chain.  The corresponding
continuum formula is a theorem target requiring the usual semigroup-domain and
bounded-multiplication hypotheses; no continuum optimal-control claim is made.

## Finite-state identity

Let (L) be a conservative live-state row generator, let (k>0) be the total
killing vector, and set

\[
T(k)=L-\operatorname{diag}k,
\qquad
f(t;k)=\alpha e^{T(k)t}k.
\]

For an additive perturbation (k_\varepsilon=k+\varepsilon h), write
(H=-\operatorname{diag}h).  The Fréchet/Duhamel identity gives

\[
D e^{Tt}[H]
=\int_0^t e^{T(t-s)}H e^{Ts}\,ds .
\]

Since (f_t=\alpha e^{Tt}Tk), differentiation gives the exact finite-state
formula

\[
D f_t(t;k)[h]
=\alpha D e^{Tt}[H]Tk
 +\alpha e^{Tt}(Hk+Th).
\tag{1}
\]

It is linear in (h).  Thus (D f_t[h]=g(t;k)^T h), where the componentwise
modality-susceptibility kernel is

\[
g_i=(\alpha e^{Tt}T)_i-k_i(\alpha e^{Tt})_i
-\int_0^t
  (\alpha e^{T(t-s)})_i(e^{Ts}Tk)_i\,ds .
\tag{2}
\]

The three terms have distinct meanings: change of the terminal time
derivative, direct change of the killing observable, and the accumulated loss
of paths caused by the perturbed hazard.  Omitting the observable term is an
error whenever the varied field is itself the reaction flux being measured.

## Fixed-budget optimum

Let (c>0) encode the discrete quadrature used for the fixed total killing
budget, so admissible local redistributions obey (c^Th=0).  Let (M\succ0)
specify the local design norm (h^TMh=1).  Define

\[
\lambda=\frac{c^TM^{-1}g}{c^TM^{-1}c},
\qquad
\widetilde g=g-\lambda c.
\]

If (widetilde g\ne0), Cauchy--Schwarz on the budget tangent space gives the
unique maximizing direction

\[
h_*=
\frac{M^{-1}\widetilde g}
{\sqrt{\widetilde g^TM^{-1}\widetilde g}},
\qquad
\max Df_t[h]
=\sqrt{\widetilde g^TM^{-1}\widetilde g}.
\tag{3}
\]

The negative direction minimizes the response.  At a density fold,
(f_t=f_{tt}=0), this quantity is the transversality coefficient for the
chosen redistribution direction.  A nonzero value identifies a locally
effective way to unfold the critical-point pair.  It does **not** guarantee
that a finite step preserves nonnegative killing, realizes a prescribed patch
geometry, or creates a detector-resolved second peak.  Zeros in (k), box
constraints, binary masks, and finite patch motion require a constrained
quadratic or mixed-integer design problem.

For two equally weighted reactive states, every unit fixed-budget direction is
one of

\[
h=\pm(1,-1)/\sqrt2,
\]

and the response is controlled by the susceptibility contrast
((g_1-g_2)/\sqrt2).  This makes precise the statement that modality is
controlled by *where* the reaction budget is placed, not only by its total.

## Numerical falsification contract

`validate_modality_susceptibility.py` tests Eqs. (1)--(3) in two independent
settings.

1. On an eleven-state irreducible killed CTMC it compares the basis Fréchet
   gradient with the Duhamel kernel, 256 held-out budget-zero five-point
   derivatives, a state permutation, and 20,000 random feasible directions.
2. At the saved two-site encounter fold it reconstructs the published
   log-rate transversality by the chain rule and evaluates the orthogonal
   fixed-state-sum redistribution direction.

The artifact fails closed if any cross-check exceeds its declared tolerance.
This validates a finite-state computational identity and its local optimizer;
it does not establish literature priority or a continuum spatial optimum.
