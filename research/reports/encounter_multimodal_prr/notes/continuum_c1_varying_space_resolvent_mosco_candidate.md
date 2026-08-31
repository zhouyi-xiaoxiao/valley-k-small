# Varying-space strong-resolvent-to-Mosco theorem candidate

Date: 2026-07-17

Status: **RESULT-BLIND SELF-CONTAINED PROOF CANDIDATE / FREE-TENSOR MOSCO IMPLICATION CLOSED SUBJECT TO AUDIT / COMPLETE C1 FALSE**

## 0. Purpose and nonclaim boundary

The Round-4 successor note
`continuum_c1_free_form_and_functional_bridge_candidate.md` (SHA-256
`17b987d5090618e5346f81217afed7e57daccf878d4b93b8402724b3e002a562`)
constructs a direct free-tensor reconstructed strong-resolvent route, but it
deliberately does not cite an unchecked varying-space theorem to relabel that
conclusion as generalized Mosco convergence.  This note supplies the missing
self-contained implication.

The proof is abstract and result-blind.  It reads no control, result,
positive-budget, production-centre, scratch, root-margin, or box-exhaustion
data.  It does not establish the one-axis geometric premises, an accepted
refinement source, exact production killing averages, a gauge/application
enclosure, or a quantitative rate.  It therefore cannot promote complete C1,
C2, C3, root transfer, release, or submission.

The already verified Round-4 handoff archive predates this note and remains an
immutable milestone.  Any later transfer of this proof must use a new delta,
not overwrite the Round-4 archive.

All Hilbert spaces below may be real.  In the complex case inner products are
sesquilinear and every variational pairing is replaced by its real part.

## 1. Setting and theorem

For each refinement index `h`, let `H_h` and `H` be Hilbert spaces.  Let
`a_h` and `a` be densely defined, closed, nonnegative symmetric forms with
nonnegative self-adjoint operators `L_h` and `L`.  Let

\[
 J_h:H_h\longrightarrow H,
 \qquad
 P_h:H\longrightarrow H_h
\]

be bounded maps such that

\[
 P_h=J_h^*,
 \qquad
 \sup_h(\|J_h\|+\|P_h\|)<\infty,
 \qquad
 \delta_h:=\|P_hJ_h-I_{H_h}\|\longrightarrow0.
 \tag{1.1}
\]

Assume that, for one `eta>0`,

\[
 J_h(L_h+\eta)^{-1}P_hu
 \longrightarrow
 (L+\eta)^{-1}u
 \quad\hbox{strongly in }H
 \quad(u\in H).
 \tag{1.2}
\]

Use the same varying-space convention as the fixed-1D note:

- `v_h -> v` strongly means `J_hv_h -> v` strongly in `H`;
- `v_h -> v` weakly means `J_hv_h -> v` weakly in `H`.

### Theorem 1.1

Under (1.1)--(1.2), `a_h` generalized-Mosco converges to `a` in this
varying-space sense.  Explicitly:

1. whenever `J_hv_h` converges weakly to `v`,
   `a(v,v)<=liminf_h a_h(v_h,v_h)`; and
2. for every `v in H`, there is `v_h in H_h` with `J_hv_h -> v` strongly and
   `limsup_h a_h(v_h,v_h)<=a(v,v)`, where the continuum form is extended by
   `+infinity` outside its form domain.

No external Mosco/semigroup equivalence is invoked in the proof.

## 2. Near-isometry and exact unitarization

Put

\[
 G_h=P_hJ_h=J_h^*J_h.
 \tag{2.1}
\]

For all sufficiently small `h`, `delta_h<1`, and spectral calculus gives

\[
 (1-\delta_h)I\le G_h\le(1+\delta_h)I,
 \qquad
 \|G_h^{\pm1/2}-I\|\longrightarrow0.
 \tag{2.2}
\]

Define

\[
 U_h:=J_hG_h^{-1/2}:H_h\longrightarrow H.
 \tag{2.3}
\]

Then

\[
 U_h^*U_h=I_{H_h},
 \qquad
 J_h=U_hG_h^{1/2}.
 \tag{2.4}
\]

Thus `U_h` is an exact isometry onto the closed subspace
`K_h=Ran(U_h)`.  If either `J_hv_h` or `U_hv_h` is weakly or strongly
convergent, the corresponding sequence `v_h` is bounded, and (2.2)--(2.4)
give

\[
 \|(J_h-U_h)v_h\|
 \le\|G_h^{1/2}-I\|\,\|v_h\|_h
 \longrightarrow0.
 \tag{2.5}
\]

Consequently `J_h` and `U_h` define exactly the same varying strong and weak
convergence.  This step avoids treating a merely near-isometric map as an
exact unitary identification.

For `beta>0`, write

\[
 R_h^\beta=(L_h+\beta)^{-1},
 \qquad
 R^\beta=(L+\beta)^{-1},
 \qquad
 T_h^\beta=U_hR_h^\beta U_h^*.
 \tag{2.6}
\]

Because `G_h^{-1/2}->I` in operator norm, the difference

\[
 T_h^\eta-J_hR_h^\eta P_h
 =J_h\left[
 (G_h^{-1/2}-I)R_h^\eta G_h^{-1/2}
 +R_h^\eta(G_h^{-1/2}-I)
 \right]P_h
 \tag{2.7}
\]

tends to zero in operator norm.  Hence (1.2) implies

\[
 T_h^\eta u\longrightarrow R^\eta u
 \quad(u\in H).
 \tag{2.8}
\]

The operators `T_h^eta` vanish on `K_h^perp`; no density of `K_h` is assumed
at this stage.

## 3. One resolvent shift gives every shift

For any `beta>0`, define on `[0,eta^{-1}]`

\[
 g_\beta(x)=\frac{x}{1+(\beta-\eta)x}.
 \tag{3.1}
\]

The denominator is strictly positive on this interval: its minimum is `1` if
`beta>=eta` and `beta/eta` if `beta<eta`.  Since `g_beta(0)=0`, spectral
calculus on `K_h` and `K_h^perp` gives the exact identities

\[
 g_\beta(T_h^\eta)=T_h^\beta,
 \qquad
 g_\beta(R^\eta)=R^\beta.
 \tag{3.2}
\]

Strong convergence (2.8), uniform operator bounds, polynomial approximation,
and continuity of `g_beta` imply

\[
 T_h^\beta u\longrightarrow R^\beta u
 \quad\hbox{for every }\beta>0\hbox{ and }u\in H.
 \tag{3.3}
\]

Thus the rest of the proof may choose the resolvent shift independently of
the single shift in (1.2).

## 4. Liminf inequality

Suppose `U_hv_h` converges weakly to `v`.  If the form liminf is infinite,
there is nothing to prove.  Otherwise pass to a subsequence realizing a finite
liminf.  Weak convergence and the isometry of `U_h` give

\[
 M:=\sup_h\|v_h\|_h<\infty.
 \tag{4.1}
\]

Fix `w in D(L)` and `beta>0`, and put

\[
 f=(L+\beta)w\in H.
 \tag{4.2}
\]

The unique minimizer over `z in D(a_h)` of

\[
 a_h(z,z)+\beta\|z\|_h^2
 -2\operatorname{Re}\langle U_h^*f,z\rangle_h
 \tag{4.3}
\]

is `R_h^beta U_h^*f`, and the minimum is

\[
 -\langle f,T_h^\beta f\rangle_H.
 \tag{4.4}
\]

Substituting `v_h` into (4.3), using (3.3), and taking the liminf gives

\[
 \begin{split}
 \liminf_h a_h(v_h,v_h)
 &\ge
 2\operatorname{Re}\langle f,v\rangle
 -\beta M^2-\langle f,R^\beta f\rangle\\
 &=2\operatorname{Re}\langle Lw,v\rangle-a(w,w)\\
 &\quad+\beta\left(
 2\operatorname{Re}\langle w,v\rangle
 -\|w\|^2-M^2
 \right).
 \end{split}
 \tag{4.5}
\]

Letting `beta` decrease to zero yields

\[
 \liminf_h a_h(v_h,v_h)
 \ge
 2\operatorname{Re}\langle Lw,v\rangle-a(w,w).
 \tag{4.6}
\]

The required dual identity is

\[
 a(v,v)=
 \sup_{w\in D(L)}
 \left[
 2\operatorname{Re}\langle Lw,v\rangle-a(w,w)
 \right],
 \tag{4.7}
\]

with value `+infinity` outside `D(a)`.  This identity is also
self-contained.  The spectral theorem and the choice
`w_n=1_[1/n,n](L)v` give the lower bound by monotone convergence:

\[
 2\operatorname{Re}\langle Lw_n,v\rangle-a(w_n,w_n)
 =\int_{[1/n,n]}\lambda\,d\|E_\lambda v\|^2
 \uparrow a(v,v).
 \tag{4.8}
\]

For `v in D(a)`, Cauchy--Schwarz after applying `L^{1/2}` gives the reverse
bound; outside `D(a)`, (4.8) diverges.  Taking the supremum in (4.6) proves the
liminf condition, including the infinite-energy case.

## 5. Resolvent-core recovery

Fix `v in H` and `beta>0`.  Define

\[
 v_h^\beta=\beta R_h^\beta U_h^*v,
 \qquad
 v^\beta=\beta R^\beta v.
 \tag{5.1}
\]

Equation (3.3) gives

\[
 U_hv_h^\beta\longrightarrow v^\beta
 \quad\hbox{strongly in }H.
 \tag{5.2}
\]

Because `U_h^*U_h=I`,

\[
 (T_h^\beta)^2=U_h(R_h^\beta)^2U_h^*.
 \tag{5.3}
\]

Strong convergence and uniform boundedness of `T_h^beta` therefore imply
strong convergence of their squares.  The resolvent equation gives the exact
energy identity

\[
 \begin{split}
 a_h(v_h^\beta,v_h^\beta)
 &=\beta^2\left[
 \langle v,T_h^\beta v\rangle
 -\beta\langle v,(T_h^\beta)^2v\rangle
 \right]\\
 &\longrightarrow
 \beta^2\left[
 \langle v,R^\beta v\rangle
 -\beta\langle v,(R^\beta)^2v\rangle
 \right]\\
 &=a(v^\beta,v^\beta).
 \end{split}
 \tag{5.4}
\]

Moreover, spectral calculus gives

\[
 v^\beta\longrightarrow v
 \quad\hbox{strongly as }\beta\to\infty.
 \tag{5.5}
\]

If `v in D(a)`, then also

\[
 a(v^\beta,v^\beta)
 =\int_0^\infty
 \lambda\left(\frac{\beta}{\lambda+\beta}\right)^2
 d\|E_\lambda v\|^2
 \uparrow a(v,v).
 \tag{5.6}
\]

Choose `beta_n -> infinity`, and for each `n` choose the mesh threshold so
that both (5.2) and (5.4) are within `1/n` of their limits.  A standard
piecewise-constant diagonal `n=n(h)->infinity` yields `U_hv_h -> v` strongly
and

\[
 a_h(v_h,v_h)\longrightarrow a(v,v)
 \quad(v\in D(a)).
 \tag{5.7}
\]

For `v` outside `D(a)`, use the same diagonal with only the strong-convergence
condition; the required inequality has right-hand side `+infinity` and is
automatic.  Equation (2.5) replaces `U_h` by `J_h`, completing the recovery
condition and the proof of Theorem 1.1.

This construction also shows directly that no unproved density of the moving
subspaces `K_h` was used: their asymptotic density is a consequence of the
resolvent-core recovery itself.

## 6. Free finite-tensor corollary

Consider the three fixed-box axes in the Round-4 note.  The refinement index
in this section is the directed multi-index

\[
 \boldsymbol h=(h_z,h_r,h_y),
 \qquad
 \max_{a\in\{z,r,y\}}h_a\longrightarrow0.
 \tag{6.0}
\]

Every limit below is this joint limit; no synchronous equality of the three
spacings is required.  Suppose the accepted one-axis forms provide
reconstructed semigroup convergence for every `t>0`, their map norms are
uniformly bounded over all three directed refinements, and their maps satisfy
(1.1).

Use completed Hilbert tensor products and the **ideal** product-mass/global-
gauge hypotheses (2.5a)--(2.6) of the Round-4 note.  In particular,
`m_ijk=m_i^z m_j^r m_k^y`; this is not an assertion about independently
rounded production masses or gauges.  For the tensor maps,

\[
 J_h=J_{z,h}\otimes J_{r,h}\otimes J_{y,h},
 \qquad
 P_h=P_{z,h}\otimes P_{r,h}\otimes P_{y,h}=J_h^*,
 \tag{6.1}
\]

and

\[
 G_h=P_hJ_h=G_{z,h}\otimes G_{r,h}\otimes G_{y,h}.
 \tag{6.2}
\]

For a finite number of axes,

\[
 \|G_h-I\|
 \le\prod_a(1+\|G_{a,h}-I\|)-1
 \longrightarrow0.
 \tag{6.3}
\]

The free Kronecker-sum semigroup factorizes.  Convergence first on algebraic
simple tensors, followed by the explicit uniform bound

\[
 \sup_{\boldsymbol h}
 \left\|
 \bigotimes_a
 J_{a,h_a}e^{-tL_{a,h_a}}P_{a,h_a}
 \right\|
 \le\prod_a
 \left(
 \sup_{h_a}\|J_{a,h_a}\|
 \sup_{h_a}\|P_{a,h_a}\|
 \right)<\infty,
 \tag{6.3a}
\]

and density in the completed product space, gives

\[
 J_he^{-tL_h^0}P_hu\longrightarrow e^{-tL^0}u
 \quad(t>0).
 \tag{6.4}
\]

The mesh-independent bound

\[
 e^{-\eta t}\|J_he^{-tL_h^0}P_hu\|
 \le C e^{-\eta t}\|u\|
 \tag{6.5}
\]

allows dominated convergence in the Laplace formula and yields (1.2) for the
free tensor operator.  Theorem 1.1 then proves generalized Mosco convergence
of the free tensor forms.  This replaces the unchecked tensorization citation
that the Round-4 note intentionally refused to assume.

The corollary remains conditional on accepted one-axis refinement families
and their geometric estimates.  The twelve current finite anchors are not an
`h -> 0` sequence and cannot instantiate the corollary by themselves.

## 7. Bounded-killing corollary

Assume the free tensor conclusion of Section 6 on the fixed finite measure
space

\[
 (\Omega_L,\mu),\qquad d\mu=\pi(x)\,dx.
 \tag{7.0}
\]

Suppose nonnegative reconstructed multipliers satisfy

\[
 K_h^{pc}\longrightarrow V
 \quad\hbox{in measure},
 \qquad
 \sup_h\|K_h^{pc}\|_\infty<\infty.
 \tag{7.1}
\]

Put `M=sup_h||K_h^{pc}||_infinity`.  After changing a null set if needed,
convergence in measure and the common bound give `0<=V<=M` almost
everywhere.  For every fixed `phi in L2(mu)`,

\[
 \|(\sqrt{K_h^{pc}}-\sqrt V)\phi\|_{L^2(\mu)}^2
 =\int
 |\sqrt{K_h^{pc}}-\sqrt V|^2|\phi|^2\,d\mu
 \longrightarrow0.
 \tag{7.1a}
\]

Indeed, the integrand converges in measure and is dominated in the finite
measure `|phi|^2 dmu` by `4M|phi|^2`; equivalently, use bounded convergence in
measure plus uniform integrability.

In the physical-volume convention of the Round-4 note,
`K_h^{pc}=V_h/rho_h` and

\[
 \sum_i m_iV_{h,i}|v_i|^2
 =\int K_h^{pc}|J_hv|^2\pi dx.
 \tag{7.2}
\]

If `J_hv_h` converges weakly to `v`, then
`sqrt(K_h^{pc})J_hv_h` converges weakly to `sqrt(V)v`: multiplication by
`sqrt(K_h^{pc})` converges strongly on each fixed `L2` test function by
(7.1a), and explicitly

\[
 \langle\phi,\sqrt{K_h^{pc}}J_hv_h\rangle
 =\langle\sqrt{K_h^{pc}}\phi,J_hv_h\rangle
 \longrightarrow
 \langle\sqrt V\phi,v\rangle.
 \tag{7.2a}
\]

Weak lower semicontinuity gives the killing liminf.

If `J_hv_h -> v` strongly, then

\[
 \begin{split}
 &\left|\int K_h^{pc}|J_hv_h|^2\pi
 -\int V|v|^2\pi\right|\\
 &\quad\le
 C\|J_hv_h-v\|_2(\|J_hv_h\|_2+\|v\|_2)
 +\left|\int(K_h^{pc}-V)|v|^2\pi\right|
 \longrightarrow0.
 \end{split}
 \tag{7.3}
\]

For the last term, `|K_h^{pc}-V|` converges in measure to zero, is bounded by
`2M`, and is integrated against the finite measure `|v|^2 dmu`; bounded
convergence in measure plus uniform integrability therefore makes it tend to
zero.  Thus the free Mosco recovery sequence is also a recovery sequence for
the killed form, and the two nonnegative liminf inequalities add.

This proves the qualitative bounded-killing perturbation **only after** (7.1)
and the free tensor premises have been accepted.  It gives no cut-cell rate,
no production interval enclosure, and no result about an unbounded killing
field.

## 8. Honest current decision and next obligations

Subject to fresh same-byte mathematical audit, this note closes the abstract
gap left in Round 4:

```text
one reconstructed resolvent -> all shifts             = PROVED HERE
near-isometric maps -> exact moving isometries         = PROVED HERE
reconstructed strong resolvent -> generalized Mosco   = PROVED HERE
free finite-tensor Mosco implication                   = PROVED HERE, AXIS PREMISES OPEN
bounded physical-volume killing perturbation          = PROVED HERE, DATA PREMISES OPEN
accepted refinement source                            = HOLD
production gauge/application and killing averages     = HOLD
quantitative C2 and box C3                             = HOLD
complete C0/C1, root transfer, release, submission    = HOLD
```

Before any manuscript promotion, the exact bytes of this theorem require at
least two independent attacks:

1. a line-by-line check of unitarization, all-shift functional calculus, the
   dual liminf identity, and the resolvent-core diagonal; and
2. a separate tensor/killing attack covering multi-index refinements,
   non-dense moving ranges, kernels, complex conventions, and the distinction
   between qualitative convergence and a C2 rate.

After that audit, the next model-specific work is to bind genuine refinement
sequences and exact physical-volume killing averages to a result-blind source,
then close the production global-gauge/application enclosure.  Quantitative
C2 should begin only after those qualitative premises are sealed.
