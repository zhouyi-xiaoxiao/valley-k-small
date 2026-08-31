# Spectral sign variation as a necessary modality diagnostic

## Finite reversible statement

For a finite killed generator with a real diagonalizable spectrum, group
repeated decay rates and remove zero observable residues.  The reaction-time
density can then be written

\[
f(t)=\sum_{j=1}^n a_j e^{-\lambda_jt},
\qquad 0<\lambda_1<\cdots<\lambda_n.
\]

Reversibility is a convenient sufficient condition: a detailed-balance
similarity makes the killed generator symmetric, so all decay rates are real
and the residues are obtained from orthogonal spectral projections.  The
derivative is

\[
f'(t)=-\sum_{j=1}^n\lambda_j a_j e^{-\lambda_jt}.
\]

Set (x=e^{-t}\).  This is a generalized polynomial in (x\in(0,1)).
Applying the classical generalized Descartes rule shows that the number of
zeros of (f') on (t>0), counted with multiplicity, cannot exceed the number
(V(a_1,\ldots,a_n)) of sign changes in the ordered residue sequence.  The
positive factors (\lambda_j) do not change that sign count.

Consequently, (m) nondegenerate interior maxima separated by (m-1) minima
require

\[
V(a_1,\ldots,a_n)\ge 2m-1,
\qquad
m\le \left\lfloor\frac{V+1}{2}\right\rfloor.
\]

Thus a bimodal finite reversible density needs at least three ordered residue
sign changes and a trimodal density needs at least five.  This is a
dimension-independent **necessary diagnostic**, not a sufficient design rule.
The generalized Descartes theorem is classical; the manuscript must not call
this corollary a new mathematical theorem.

## Physical interpretation

Spatial configuration affects modality through two spectral objects, not by
patch count alone:

1. the decay rates (\lambda_j), which encode transport plus killing; and
2. the residues (a_j), which encode the initial condition, reaction
   observable, and the spatial overlap of both with each eigenmode.

An eigenvalue can therefore be dynamically present but dark in the reaction
observable.  Conversely, a single reactive state can receive several
time-separated transport streams.  The sign-variation count is best viewed as
an available *spectral oscillation budget*: too few sign changes rule out a
requested mode count, but many sign changes do not force their zeros to lie on
positive time or to form resolved peaks.

## Adversarial boundaries

### Not sufficient

The four-stage hypoexponential density

\[
f(t)=4e^{-t}-12e^{-2t}+12e^{-3t}-4e^{-4t}
=4e^{-t}(1-e^{-t})^3
\]

has three ordered residue sign changes but only one positive critical point,
(t=\log4), a maximum.  Hence the bimodal necessary count is not sufficient.

### Not a channel- or rank-count bound

Two 12-stage Erlang transport branches with rates 12 and 1.2, initialized with
equal probability, can feed a single live reactive state killed at rate 100.
The resulting rank-one killing model has a maximum--minimum--maximum pattern.
The saved validation locates the roots directly from matrix-exponential
derivatives.  Therefore neither the number of labelled channels nor the rank
of the killing support bounds the possible number of modes.

### Not automatically a nonreversible or continuum theorem

Nonreversible phase-type generators can have complex eigenvalues or Jordan
blocks, producing oscillatory or polynomial-times-exponential terms.  The
simple residue-sign corollary does not cover them.  A continuum extension also
requires a self-adjoint compact-resolvent setting and convergence that
justifies differentiation and zero counting of the infinite expansion.

## Production validation

`validate_spectral_modality.py` performs full reversible
symmetrization/eigendecomposition for two frozen production generators.

- The supercritical finite encounter CTMC has three direct critical points and
  retains at least three residue sign changes across four coefficient cutoffs.
- The (9\times5) M2D-T generator has five direct alternating critical points
  and retains at least five sign changes across the same cutoff sweep.

The script checks detailed balance, symmetric similarity, eigenpair residuals,
contact-safe initial flux, density reconstruction, and derivative residuals at
every saved critical point.  Large observed sign counts are not interpreted as
predicted mode counts; only the necessary lower bounds are used.
