# Theory note: chase channel versus boundary channel

## Exact operators

For independent one-step kernels $P_1,P_2$, let

\[
P=P_1\otimes P_2,
\]

and let $U$ select the catalytic co-location states.  With reaction
probabilities $D_\rho=\operatorname{diag}(\rho_i)$, arrival-then-react gives

\[
Q=P(I-UD_\rho U^\top),\qquad B=PUD_\rho,
\]

\[
f_i(t+1)=\alpha Q^t B e_i.
\]

The initial row law \(\alpha\) denotes live mass after conditioning on survival
of any time-zero reaction check. Accordingly, no \(t=0\) atom is included and
the first reported flux is at step one.

The generating function is

\[
\widehat f(z)=z\alpha(I-zQ)^{-1}B\mathbf1.
\]

For continuous-time generators $L_1,L_2$,

\[
L_0=L_1\oplus L_2,\qquad
T=L_0-UD_\kappa U^\top,
\]

\[
f_i(t)=\alpha e^{Tt}UD_\kappa e_i.
\]

Woodbury reduces the resolvent to the hotspot Green matrix

\[
G_D(s)=U^\top(sI-L_0)^{-1}U.
\]

For two sites the secular determinant is

\[
\mathcal D(s)=
(\kappa_1^{-1}+g_{11})(\kappa_2^{-1}+g_{22})-g_{12}g_{21}.
\]

This determinant controls modes coupled to the catalytic subspace and visible
with nonzero residue in the reaction observable; uncoupled dark modes are not
removed by the reduction and must be checked separately.

## Channel-mixture fold

Writing $f=p g_1+(1-p)g_2$ for differentiable continuous channel densities, a
generic modality fold obeys

\[
g_1'g_2''-g_2'g_1''=0,
\qquad
p_*=-\frac{g_2'}{g_1'-g_2'},
\]

with $g_1'\ne g_2'$, $0<p_*<1$, $f'''\ne0$, and parameter transversality along
a physically realizable parameter path.  For the discrete PMF these derivative
conditions apply only after an explicit continuous embedding such as
Poissonization; a direct discrete boundary requires finite differences.

## Scaling prediction for the biased family

In the implemented family, the near catalyst and both starting positions remain
at fixed offsets from one another while the cluster translates with $L$; both
boundary distances therefore change.  The data suggest that the early chase
channel approaches an $L$-independent shape and splitting probability.  The slow
leading walker has drift

\[
v_2=q_2 b_2>0.
\]

The late boundary-channel time is approximately an inverse-Gaussian travel
time over a distance proportional to $L$:

\[
E[T_2]\sim \frac{d_L}{v_2},\qquad
\operatorname{sd}(T_2)\sim
\sqrt{\frac{\sigma_2^2 d_L}{v_2^3}}.
\]

This motivates the hypotheses that the peak separation is $O(L)$, the late
width is $O(\sqrt L)$, and the resolution ratio grows as $O(\sqrt L)$.  The
inverse-Gaussian approximation does not yet control conditioning on missing the
near catalyst, the joint return of both walkers to the boundary catalyst, or
the finite reaction waiting time.  The exact discrete data show an
approximately constant early peak, a linearly moving late peak, increasing
width resolution, and a rapidly deepening valley for $L=31,41,61,81$.

This scaling is the first analytic target.  It should be derived for the
conditional channel densities and then connected to the exact Green-matrix
fold rather than fitted only at the level of peak locations.
