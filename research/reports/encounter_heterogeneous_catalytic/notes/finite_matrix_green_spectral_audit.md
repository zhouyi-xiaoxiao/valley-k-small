# Finite-matrix Green spectral audit

## Scope

This note certifies identities for one exact `4x4` finite CTMC matrix. It does
**not** assert Fredholm compactness, continuum meromorphic continuation,
Bromwich inversion, or any statement about an unbounded volume/trace operator.
The finite Green function is evaluated only for complex `s` outside the free
matrix spectrum. At a killed pole the renewal solve is singular and the API
fails closed.

## Fixture

Each walker is the symmetric two-site chain

\[
W=\begin{pmatrix}-1&1\\1&-1\end{pmatrix}.
\]

In product order `(0,0),(0,1),(1,0),(1,1)`, the free generator, selector, and
killing matrix are

\[
L_0=\begin{pmatrix}
-2&1&1&0\\1&-2&0&1\\1&0&-2&1\\0&1&1&-2
\end{pmatrix},\quad
U=(e_0,e_3),\quad K=\tfrac12 I_2,
\]

and `T=L0-U K U^T`. The free spectrum is `(-4,-2,-2,0)` and the killed
spectrum is approximately `(-4.26556444,-2.5,-2,-0.23443556)`.

## A shared dark mode

The normalized vector

\[
v_d=(0,1,-1,0)/\sqrt2
\]

satisfies `L0 v_d = T v_d = -2 v_d` and `U^T v_d=0`. It is therefore a pole
of the full free and killed resolvents but is dark to the reaction support.
Because `-2` belongs to the free spectrum, `G(s)=U^T(sI-L0)^{-1}U` is not
defined there; the restricted determinant is not supposed to detect this
shared mode.

## A coupled killed pole

The normalized vector

\[
v_c=(1,0,0,-1)/\sqrt2
\]

is a killed eigenvector with `lambda=-2.5`, while its distance from the free
spectrum is `0.5`. The free resolvent therefore exists at `lambda`. Direct
calculation gives

\[
G(\lambda)=\frac1{15}
\begin{pmatrix}-14&16\\16&-14\end{pmatrix},\qquad
I+G(\lambda)K=\frac8{15}
\begin{pmatrix}1&1\\1&1\end{pmatrix}.
\]

The renewal determinant vanishes and its null vector is `(1,-1)/sqrt(2)`.
The production API consequently accepts the negative parameter as belonging
to the free resolvent set, then rejects the singular renewal solve as a killed
pole. Away from the pole, direct and Green resolvents agree and the finite
determinant lemma

\[
\det(sI-T)=\det(sI-L_0)\det(I+G(s)K)
\]

is checked at one right-half-plane and one left-half-plane complex point.

## Channel residues can cancel

For initial row mass `alpha=e0^T`, the eigenprojector residue in the two
reaction channels is

\[
(\alpha v_c)(v_c^T U K)=(1/4,-1/4).
\]

Both channels therefore see the pole, but the total-flux observable with
channel weights `(1,1)` has residue zero. A near-pole Green evaluation at
`lambda+1e-4` recovers the two residues to better than `4e-6` while passing the
default accuracy gate. This is an explicit numerator/observable cancellation,
not evidence that the killed eigenvalue is absent.

## API and reproduction boundary

`ctmc_green_resolvent` now accepts any finite complex `s` outside the finite
free spectrum, subject also to renewal invertibility and a fail-closed accuracy
gate. `ctmc_channel_laplace` remains restricted to `Re(s)>=0`. The two APIs
serve different mathematical questions and are not aliases.

- generator: `code/validate_finite_green_spectrum.py`;
- artifact: `artifacts/data/finite_matrix_green_spectral_audit.json`;
- provenance: `artifacts/data/finite_matrix_green_spectral_audit.manifest.json`;
- focused tests: `tests/test_encounter_green_ctmc.py` and
  `tests/test_encounter_green_spectral_artifact.py`.

This Round-02 certificate is incorporated into the manuscript, theory note,
reader notebook, and publication pipeline while retaining the finite-matrix
scope above.
