# Fixed-budget allocation-cusp promotion design

Date: 2026-07-13  
Status: **design and algebra preflight only; no positive-`B` held-out result was
read or generated**

## 0. Purpose and evidence boundary

Round 33 identifies the shortest same-family promotion after the frozen
positive-`B` point: find a finite-`B`, fixed-total-budget allocation cusp in
the broad four-slab family, continue both fold branches, and validate
representative modality regions with mesh/alignment and box evidence.  This
note makes that step finite and auditable.

The present work did **not** edit or execute the frozen positive-`B` producer,
test, protocol, or manifest and did not inspect a held-out result.  It adds
only an independent small-CSR algebra prototype, its tests, this design, and
its adversarial audit.  Accordingly, none of the following is claimed here:

- existence of the positive-`B` cusp;
- convergence of a cusp or fold branch;
- one-, two-, or three-mode phase representatives;
- an unbounded-domain or continuum certificate;
- independent-solver validation; or
- a project or publication gate pass.

The design is result-informed.  It is allowed to use the already disclosed
`B=0` broad-family cusp to choose a well-conditioned two-dimensional
allocation plane.  Any future discovery output must remain labelled as such.

## 1. Fixed family and allocation coordinates

The physical family is unchanged:

\[
 D=0.002,\quad \gamma=0.1,\quad \bar m=0.95,\quad W=1,
 \quad a=0.16,
\]

with midpoint start `0.14`, relative start `(-0.35,0)`, compact initial
half-width `0.02`, patch half-width `0.04`, and slab centres

\[
 (0.35,0.60,0.75,0.90).
\]

The target installed budget is fixed at

\[
 B=0.01.
\]

Only the four nonnegative allocation weights may move, subject to
\(\mathbf 1^Tw=1\).  Transport, initial law, contact radius, slab supports,
box faces, and budget may not be adjusted to rescue a failed cusp.

### 1.1 Canonical two-plane from the pinned `B=0` response

The exact-continuum broad-family cusp already in the repository is

\[
 t_c^{(0)}=13.30724696053485,
\]

\[
 w_c^{(0)}=(0.28,\ 0.23115240260064182,\
 0.20722533378296604,\ 0.28162226361639210).
\]

Start from the Euclidean-orthonormal Helmert basis of the full allocation
tangent space,

\[
 T=\begin{pmatrix}
  1/\sqrt2&1/\sqrt6&1/\sqrt{12}\\
 -1/\sqrt2&1/\sqrt6&1/\sqrt{12}\\
 0&-2/\sqrt6&1/\sqrt{12}\\
 0&0&-3/\sqrt{12}
 \end{pmatrix},
 \qquad \mathbf1^TT=0,\quad T^TT=I_3.
\]

At the pinned `B=0` cusp, form the dimensionless full-tangent response

\[
 R_{\rm full}^{(0)}=
 \begin{pmatrix}
  (t_c^{(0)}/f_c^{(0)})\,\nabla_\xi G_t\\
  ((t_c^{(0)})^2/f_c^{(0)})\,\nabla_\xi G_{tt}
 \end{pmatrix},\qquad w=w_c^{(0)}+T\xi.
\]

The pinned channel jets give

\[
 R_{\rm full}^{(0)}\simeq
 \begin{pmatrix}
 3.07036526&-2.09946043&-4.00539310\\
 -11.35829709&26.40000057&-6.05167654
 \end{pmatrix},
\]

with nonzero singular values `29.4584764696` and `4.96688503058`.
Choose the two right-singular directions associated with those nonzero
singular values, map them through \(T\), order them by decreasing singular
value, and fix each sign by requiring its largest-magnitude component to be
positive.  This freezes

\[
 P=\begin{pmatrix}
 -0.0333951724537727& 0.0474675452740631\\
 -0.588571155923409&-0.569871639404847\\
  0.790069638665939&-0.256745888525331\\
 -0.168103310288757& 0.779149982656115
 \end{pmatrix},
\]

\[
 \mathbf1^TP=0,\qquad P^TP=I_2.
\]

The target control chart is therefore

\[
 w(\theta)=w_c^{(0)}+P\theta,
 \qquad \theta=(\theta_1,\theta_2)^T.
 \tag{1.1}
\]

This is preferable to retaining the historical `w_1=0.28` chart.  It uses
both independent unfolding directions with maximal conditioning in the
known `B=0` response and allows the early-slab weight to move, which is
important because the first event-basin mass is currently the tightest
observability margin.  It is not an after-the-fact positive-`B` optimization:
the plane is determined entirely by pinned `B=0` data.

The Euclidean metric is physically natural here.  All four slabs have the
same normalized shape and width, have disjoint supports, and share the same
relative-contact factor; their catalyst-field Gram matrix is therefore a
common scalar multiple of the identity.  If a later family changes patch
shapes, the basis must instead be whitened in its frozen physical Gram metric.

## 2. Exact fixed-`B` allocation sensitivities

### 2.1 Row/column convention

Let \(Q_0\) be the free **row** generator of one fixed semidiscrete model and
let \(\kappa_j\ge0\) be the cell-averaged killing field of slab \(j\) per unit
installed budget.  Put

\[
 \kappa(\theta)=\sum_{j=1}^4w_j(\theta)\kappa_j,
 \qquad
 u_i=\partial_{\theta_i}\kappa
     =\sum_{j=1}^4P_{ji}\kappa_j,
 \tag{2.1}
\]

\[
 Q(\theta)=Q_0-BD_{\kappa(\theta)},
 \qquad A(\theta)=Q(\theta)^T,
 \tag{2.2}
\]

where \(D_v=\operatorname{diag}(v)\).  The probability **column** state is

\[
 p_t=Ap,\qquad p(0)=p_0.
 \tag{2.3}
\]

Because the allocation chart is affine,

\[
 Q_i:=\partial_{\theta_i}Q=-BD_{u_i},
 \qquad A_i=Q_i^T=-BD_{u_i},
 \qquad Q_{ij}=A_{ij}=0.
 \tag{2.4}
\]

### 2.2 First and second state tangents

For the two frozen directions, \(s_i=\partial_{\theta_i}p\) satisfies

\[
 (s_i)_t=As_i-BD_{u_i}p,
 \qquad s_i(0)=0,
 \qquad i=1,2.
 \tag{2.5}
\]

Equivalently, \((p,s_1,s_2)^T\) is propagated by the exact block-column
generator

\[
 \mathcal A_1=
 \begin{pmatrix}
  A&0&0\\
  -BD_{u_1}&A&0\\
  -BD_{u_2}&0&A
 \end{pmatrix}.
 \tag{2.6}
\]

The optional second tangents needed for Hessian and branch-curvature audits
are

\[
 (s_{ij})_t=As_{ij}-BD_{u_i}s_j-BD_{u_j}s_i,
 \qquad s_{ij}(0)=0.
 \tag{2.7}
\]

These are allocation derivatives at **fixed** \(B\).  They are not the
budget derivative in the current positive-`B` producer.

### 2.3 Direct observable terms and all time jets

The reaction-time density is

\[
 f(t,\theta)=B\,\kappa(\theta)^Tp(t,\theta).
 \tag{2.8}
\]

Define row-side observable recurrences

\[
 a_0=\kappa,\qquad a_{r+1}=Qa_r,
 \tag{2.9}
\]

and their allocation tangents

\[
 b_{0i}=u_i,
 \qquad b_{r+1,i}=Q_i a_r+Qb_{ri}
                 =-BD_{u_i}a_r+Qb_{ri}.
 \tag{2.10}
\]

Then, for every required order,

\[
 f^{(r)}=B\,p^Ta_r,
 \tag{2.11}
\]

\[
 f^{(r)}_{\theta_i}
 =B\left(s_i^Ta_r+p^Tb_{ri}\right).
 \tag{2.12}
\]

The second term in (2.12) is the direct derivative of the reaction
observable and of its generator iterates.  Keeping only the state tangent
\(s_i\) is wrong.  Equations (2.9)--(2.12) provide
\(f_t,f_{tt},f_{ttt},f_{tttt}\) and
\(f_{t\theta_i},f_{tt\theta_i},f_{ttt\theta_i}\) without finite-differencing
time.

The survival checks must differentiate consistently:

\[
 S=\mathbf1^Tp,\qquad S_{\theta_i}=\mathbf1^Ts_i,
 \qquad S_t=-f,\qquad (S_{\theta_i})_t=-f_{\theta_i}.
 \tag{2.13}
\]

## 3. Complete cusp map, Jacobian, and projected rank

Use

\[
 H(t,\theta)=
 \begin{pmatrix}f_t\\f_{tt}\\f_{ttt}\end{pmatrix}.
 \tag{3.1}
\]

The exact Newton Jacobian in coordinates \(x=(t,\theta_1,\theta_2)\) is

\[
 DH=
 \begin{pmatrix}
 f_{tt}&f_{t\theta_1}&f_{t\theta_2}\\
 f_{ttt}&f_{tt\theta_1}&f_{tt\theta_2}\\
 f_{tttt}&f_{ttt\theta_1}&f_{ttt\theta_2}
 \end{pmatrix}.
 \tag{3.2}
\]

At a cusp, its determinant factorizes exactly:

\[
 \det DH
 =f_{tttt}\det R,
 \qquad
 R=\begin{pmatrix}
 f_{t\theta_1}&f_{t\theta_2}\\
 f_{tt\theta_1}&f_{tt\theta_2}
 \end{pmatrix}.
 \tag{3.3}
\]

Thus the nondegeneracy obligations are separately visible:

1. \(f_{tttt}\ne0\), so the stationary point is quartically nondegenerate;
2. \(R\) has rank two in the frozen physical allocation metric; and
3. the cusp lies in the strict simplex interior.

For comparison across meshes, let \(t_c,f_c\) denote the cusp values and
scale time by \(\widehat t=t/t_c\).  The dimensionless Jacobian is

\[
 \widehat J=
 \begin{pmatrix}
 t_c^2f_{tt}/f_c&t_cf_{t\theta_1}/f_c&t_cf_{t\theta_2}/f_c\\
 t_c^3f_{ttt}/f_c&t_c^2f_{tt\theta_1}/f_c&t_c^2f_{tt\theta_2}/f_c\\
 t_c^4f_{tttt}/f_c&t_c^3f_{ttt\theta_1}/f_c&t_c^3f_{ttt\theta_2}/f_c
 \end{pmatrix}.
 \tag{3.4}
\]

The projected allocation response is

\[
 \widehat R=
 \begin{pmatrix}
 t_cf_{t\theta_1}/f_c&t_cf_{t\theta_2}/f_c\\
 t_c^2f_{tt\theta_1}/f_c&t_c^2f_{tt\theta_2}/f_c
 \end{pmatrix},
 \tag{3.5}
\]

and

\[
 \det\widehat J=
 \left(t_c^4f_{tttt}/f_c\right)\det\widehat R.
 \tag{3.6}
\]

Report both singular values of \(\widehat R\), their ratio, the smallest
singular value of \(\widehat J\), and the determinant identity residual.  A
raw singular value for \(f\) scales like \(B\); the dimensionless quantities
above do not confuse vanishing absolute event rate with loss of normalized
allocation conditioning.

## 4. Fold continuation from the cusp

The fold map is

\[
 \Phi(t,\theta)=\begin{pmatrix}f_t\\f_{tt}\end{pmatrix},
 \tag{4.1}
\]

with Jacobian

\[
 D\Phi=
 \begin{pmatrix}
 f_{tt}&f_{t\theta_1}&f_{t\theta_2}\\
 f_{ttt}&f_{tt\theta_1}&f_{tt\theta_2}
 \end{pmatrix}.
 \tag{4.2}
\]

At the cusp, \(D\Phi=[0_{2\times1}\mid R]\) and has rank two.  The
fold curve is locally parameterized by \(t\), but its projection into the
allocation plane has a cusp.  Let \(\tau=t-t_c\),
\(\eta=\theta-\theta_c\), and write the two rows of \(R\) as
\(R_1,R_2\).  The stationary equation has the weighted leading expansion

\[
 f_t=R_1\eta+(R_2\eta)\tau+\frac{f_{tttt}}6\tau^3
 +O(|\eta|^2+|\eta|\tau^2+|\tau|^4).
 \tag{4.3}
\]

Solving \(f_t=f_{tt}=0\) gives the branch predictor

\[
 R_1\eta=\frac{f_{tttt}}3\tau^3+O(\tau^4),
 \qquad
 R_2\eta=-\frac{f_{tttt}}2\tau^2+O(\tau^3).
 \tag{4.4}
\]

Equivalently,

\[
 \theta'(t_c)=0,
 \qquad
 R\theta''(t_c)=\binom{0}{-f_{tttt}}.
 \tag{4.5}
\]

Use (4.4) at frozen positive and negative \(\tau\) to seed the two outgoing
branches.  Correct each seed by solving \(\Phi=0\) at fixed \(t\).  Beyond
the initial neighborhood, use pseudo-arclength continuation: if \(v_k\) is
the unit null vector of \(D\Phi(x_k)\), predict
\(x_{k+1}^{\rm p}=x_k+\Delta\ell v_k\), then solve

\[
 \begin{pmatrix}
 \Phi(x)\\v_k^T(x-x_{k+1}^{\rm p})
 \end{pmatrix}=0.
 \tag{4.6}
\]

Orient \(v_k\) continuously by \(v_k^Tv_{k-1}>0\).  Away from the cusp, a
nondegenerate fold additionally requires \(f_{ttt}\ne0\) and rank two of
\(D\Phi\).  Both branches must retain the separately identified remote
simple max--min pair; the cusp theorem transfers only the local pair.

For reader-facing phase coordinates, the leading normal form follows from
(4.3):

\[
 \tau^3+a\tau+b=0,
 \qquad
 a=6R_2\eta/f_{tttt},\quad b=6R_1\eta/f_{tttt}.
 \tag{4.7}
\]

Its local three-root region has \(-4a^3-27b^2>0\).  This discriminant is a
local guide and plotting coordinate, not a substitute for the full killed-law
root and event-mass calculation.

## 5. Algebra preflight already completed

The independent file `code/allocation_cusp_algebra_prototype.py` constructs a
five-state explicit-CSR row generator, four positive patch fields, the two
fixed-budget directions, and the block system (2.6).  It does not import the
current positive-`B` producer.

`code/test_allocation_cusp_algebra_prototype.py` checks:

1. unit-budget and metric-orthonormal basis identities;
2. both state tangents against centred allocation finite differences;
3. direct-plus-state mixed jets through \(f_{ttt\theta_i}\); and
4. the complete cusp Jacobian, including \(f_{tttt}\), against an independent
   centred difference of \(H\), plus the fold null direction.

All four tests pass.  At the deterministic test point, the largest absolute
difference between the analytic and finite-difference cusp Jacobians is
`4.02e-13`.  This validates the algebra and orientation on a small explicit
chain; it does not validate the broad-family matrix-free implementation or
its physical discretization.

## 6. Bounded two-stage numerical protocol

The future formal protocol must be a new producer/manifest/result chain.  It
must not be appended to or silently modify the current positive-`B` point
confirmation.

### Stage A — low-mesh discovery only

Allowed meshes are exactly the baseline-box cubic meshes `65` and `97`.
Meshes `113`, `128`, `129`, `161`, every enlarged box, and every independent
solver are forbidden during Stage A.

1. **Cusp homotopy.**  On each discovery mesh, start from its `B=0`
   semidiscrete cusp in the frozen plane (1.1).  Follow the predeclared budget
   schedule
   \[
   B=(0,0.0025,0.0050,0.0075,0.0100).
   \]
   For \(B>0\), solve \(H=0\) with analytic (3.2).  Normalize the Newton map
   by \(F_B=f/B\), which has the same roots and avoids an artificial factor
   `0.01` in conditioning.
2. **Bounded solver.**  Use at most 12 Newton iterations per budget, at most
   eight deterministic step halvings per iteration, and the fixed trust
   region
   \[
   9\le t\le18,\quad \|\theta\|_\infty\le0.15,
   \quad \min_jw_j\ge0.03.
   \]
   Failure is `HOLD_DISCOVERY`; it is not permission to alter the plane,
   budget schedule, geometry, or trust region.
3. **Independent derivative audit.**  At each `B=0.01` discovery cusp, compare
   both state tangents and all entries of (3.2) with centred allocation/time
   finite differences using allocation steps `2e-5, 1e-5` and relative time
   steps `2e-5*t_c, 1e-5*t_c`.  The two errors must display the expected
   decrease (up to a frozen roundoff floor), and maximum normalized
   disagreement must be at most `1e-6`.
4. **Remote pair.**  On `[0.5,35]`, isolate sign-changing stationary roots
   outside a frozen cusp neighborhood and require at least one ordered remote
   max--min pair with simple curvature and density above the declared relative
   floor.
5. **Both folds.**  Seed at \(\tau=\pm0.10\) with (4.4), correct at fixed
   time, and continue each branch with initial arclength `0.05`, bounded in
   `[0.025,0.20]`.  Stop at `|t-t_c|=2`, `min(w)=0.03`, or 24 accepted nodes,
   whichever occurs first.  Both branches must reach `|t-t_c|>=0.75` with at
   least six accepted noncusp nodes.
6. **Bounded phase discovery.**  Around the mesh-97 cusp, evaluate only the
   32 predeclared physical controls
   \[
   \theta=\theta_c+r(\cos(k\pi/4),\sin(k\pi/4)),
   \quad r\in\{0.02,0.05,0.09,0.13\},\quad k=0,\ldots,7,
   \]
   discarding points with `min(w)<0.03`.  Screen all retained controls on mesh
   65 with time spacing `0.05`.  For each retained-window maximum count
   `1,2,3`, advance at most the three controls with the largest deterministic
   robustness score to mesh 97 and point-refined roots.  Controls with wrong
   endpoint signs are ineligible.  For the remaining controls, the score is
   the minimum threshold-normalized signed margin over peak ratio, valley
   ratio, curvature, and event-basin mass, using the thresholds in Section 7;
   lexicographic weight order is the final tie-break.  If a count is absent,
   the preferred three-region phase claim fails; do not enlarge the radius
   set.
7. **Discovery representatives.**  Freeze exactly one physical weight vector
   for each available count by maximizing the worst score across meshes 65
   and 97.  These fixed controls, not mesh-specific retuned controls, are the
   only representatives allowed in Stage B.

The retained-window patterns are respectively `max`, `max-min-max`, and
`max-min-max-min-max` on `[0.5,35]`.  They are not exact global modal counts.
For a representative with \(m\) retained maxima, the `m` reaction-basin
masses are partitioned by the `m-1` retained valleys and final survival at
`T=100`.

### The no-refit freeze between stages

Before any Stage-B calculation, create and independently audit a new manifest
that pins:

- every physical input and the exact `B=0.01` budget;
- \(w_c^{(0)}\), the Helmert convention, and all digits of \(P\);
- discovery code, tests, low-mesh results, and evidence timing;
- the cusp trust box, time window, root definition, and density floor;
- exact Stage-A representative weights;
- the two branch orientations and six comparison nodes, chosen as the node
  nearest each signed offset `|t-t_c|=0.25,0.50,0.75` on each branch (ties:
  smaller normalized residual, then earlier acceptance index);
- every Stage-B mesh, box, threshold, error rule, and claim flag; and
- two-process deterministic execution and failure-atomic publication rules.

After that hash is frozen, no weight, geometry, budget, support, time window,
root filter, fold node, threshold, or solver tolerance may change in response
to Stage-B values.  Re-solving the **same equations** for mesh-dependent cusp
and fold coordinates is numerical convergence, not physical refitting.

### Stage B — held-out mesh, parity, and box confirmation

The baseline-box alignment sequence is

| label | cells `(midpoint, relative-parallel, transverse)` | role |
|---|---:|---|
| `O113` | `(113,113,113)` | odd coarse confirmation |
| `E128` | `(128,128,128)` | even/alignment challenge |
| `O129` | `(129,129,129)` | odd reference |
| `O161` | `(161,161,161)` | finer odd level |

The baseline faces remain midpoint `[-0.25,1.85]` and relative-parallel
`[-1.8,1.8]`.  At least the three odd levels must enter a visibly convergent
regime; `E128` must not cross any topology or scientific threshold.

The box matrix holds cell widths approximately fixed relative to `O129` and
requires an anisotropic implementation:

| label | midpoint box/cells | relative box/cells | transverse cells |
|---|---|---|---:|
| `Base` | `[-0.25,1.85] / 129` | `[-1.8,1.8] / 129` | 129 |
| `M+` | `[-0.55,2.15] / 166` | `[-1.8,1.8] / 129` | 129 |
| `R+` | `[-0.25,1.85] / 129` | `[-2.4,2.4] / 172` | 129 |
| `MR+` | `[-0.55,2.15] / 166` | `[-2.4,2.4] / 172` | 129 |

For every baseline mesh and every box row:

1. solve the cusp within the frozen trust region;
2. report the complete raw and dimensionless jet (3.4), both allocation
   state tangents, \(\widehat R\), \(\widehat J\), determinant identity, and
   survival derivative identities;
3. correct the six frozen fold comparison nodes and retain their branch
   identity without changing their physical continuation rule;
4. evaluate the exact same one-/two-/three-mode representative weights;
5. report every retained root/type, peak and valley ratio, dimensionless
   curvature, event-basin mass, final survival, and boundary-strip mass; and
6. serialize a structural failure as finite JSON `null` plus a false gate,
   never as `NaN`, an omitted value, or a changed selection.

The box matrix is empirical truncation evidence.  Even if it passes, the
flags `continuum_interval_verified`, `unbounded_domain_FV_limit_verified`,
and `independent_solver_verified` remain false until their separate programs
are completed.

## 7. Frozen scientific and numerical gates

The following are the proposed confirmation thresholds and are a
**pre-discovery design commitment**.  They must be copied unchanged into the
new manifest before Stage B.  Any revision requires a separately numbered
design and independent audit completed before the first Stage-A allocation
run; low-mesh discovery may select representatives but may not relax these
thresholds.

### 7.1 Cusp gates

- maximum of the three dimensionless residuals
  \(t_c^r|f^{(r)}|/f_c\), `r=1,2,3`: `1e-8`;
- minimum simplex weight: `0.03`;
- minimum \(|t_c^4f_{tttt}/f_c|\): `5.0`;
- minimum \(\sigma_2(\widehat R)\): `0.5`;
- minimum \(\sigma_2/\sigma_1\) of \(\widehat R\): `0.05`;
- minimum \(\sigma_{\min}(\widehat J)\): `0.25`;
- maximum relative determinant-factorization residual: `1e-9`;
- maximum explicit-CSR/action-orientation residual: `1e-11`; and
- maximum two-step finite-difference mixed-jet discrepancy: `1e-6`.

These floors are deliberately well below the pinned `B=0` margins
(`|scaled fourth derivative|=44.68` and full-plane
`sigma_2=4.97`) but far enough from zero to support a numerical error budget.

### 7.2 Fold and remote-pair gates

- both branches reach `|t-t_c|>=0.75` with at least six noncusp nodes;
- normalized fold residuals at every comparison node: `<=1e-8`;
- for nodes with `|t-t_c|>=0.25`,
  \(t^3|f_{ttt}|/f\ge0.10\);
- dimensionless smallest nonzero singular value of \(D\Phi\): `>=0.05`;
- continuous branch orientation and no simplex weight below `0.03`;
- at least one remote max--min pair at the cusp, separated from the cusp
  neighborhood and from each other by at least `0.25` in time; and
- every remote root has absolute dimensionless curvature at least `0.05`.

### 7.3 Representative-law gates

For every frozen representative:

- the declared retained-window alternating topology on `[0.5,35]`;
- maximum scaled stationary-root residual `1e-8`;
- minimum absolute scaled curvature `0.05`;
- minimum smallest/largest peak ratio `0.10`;
- maximum valley/smaller-adjacent-peak ratio `0.85`;
- every valley-partitioned event-basin mass at least `0.005` by `T=100`;
- positive density and survival, monotone sampled survival, and state
  negativity no worse than `1e-12`;
- `S_t=-f`, `Q1=-B*kappa`, differential mass balance, and event partition
  closure each within `1e-9`; and
- no promoted global exact-count wording.

The `0.005` value remains a declared robustness floor, not a universal
experimental observability threshold.

### 7.4 Margin-aware uncertainty rule

For a promoted lower-bound quantity \(q\ge q_0\), use the most conservative
value over the confirmation matrix,

\[
 q_{\rm cons}=\min q,
 \qquad d=q_{\rm cons}-q_0.
\]

For an upper-bound quantity \(q\le q_0\), use

\[
 q_{\rm cons}=\max q,
 \qquad d=q_0-q_{\rm cons}.
\]

Define \(E_q\) as the maximum of:

1. the `O129`--`O161` difference;
2. the `E128`--`O129` parity difference;
3. the largest `Base`--enlarged-box difference; and
4. the independent algebra/root residual converted to the units of \(q\).

Require

\[
 d>0,
 \qquad E_q\le\min(E_q^{\rm abs},d/4).
 \tag{7.1}
\]

Use these absolute caps:

| quantity | `E_abs` |
|---|---:|
| cusp or stationary-root time | `0.05` |
| allocation weight (`L_inf`) | `0.005` |
| peak/valley ratio | `0.02` |
| event-basin mass | `0.001` |
| final survival | `0.01` |
| scaled fourth derivative | `0.50` |
| singular value or singular-value ratio | `0.01` |
| dimensionless curvature | `0.02` |

Coordinates without a scientific inequality, such as cusp time and weight,
must satisfy the absolute cap directly.  No convergence order is inferred
from two levels across the discontinuous contact quadrature.  Raw values and
differences remain primary; an extrapolation is secondary and may be reported
only if at least three levels show a stable trend.

For every scalar coordinate and jet used in a claim, the odd-mesh sequence
must also satisfy

\[
 |q_{161}-q_{129}|<|q_{129}-q_{113}|,
 \tag{7.2}
\]

unless the coarser difference is already below the frozen numerical roundoff
floor.  Topology must be identical.  Failure of (7.2) is nonconvergence, not
permission to infer an order from another subset.

The event-mass rule is the likeliest fail-closed boundary.  For example, a
mass only slightly above `0.005` cannot be promoted merely because its point
estimate passes.  Stage A should therefore prefer controls with visible mass
headroom, but Stage B may not retune them.

## 8. Claim ladder and stopping rules

### `PASS-ALGEBRA`

The small explicit-CSR tests pass and the future broad-family implementation
passes the same orientation and finite-difference checks.  This says nothing
about a physical cusp.

### `PASS-DISCOVERY`

Both low meshes locate the same-family `B=0.01` cusp, both folds, a remote
pair, and the requested representative regions within the bounded search.
This authorizes a frozen Stage-B run, not a manuscript claim.

### `PASS-FV-ALLOCATION-CUSP`

All cusp, fold, representative, parity, box, and margin-aware gates pass
without refitting.  This supports a finite-box numerical allocation-cusp
claim with empirical mesh/alignment and truncation evidence.  It still does
not set the project gate because the independent unbounded killed-process
calculation remains separate.

### `HOLD`

Stop without expanding the search when any of the following occurs:

- the cusp leaves the trust box or simplex interior;
- either response rank or fourth derivative loses its margin;
- only one fold branch continues;
- the remote pair disappears;
- a required modality representative is absent from the bounded discovery;
- a held-out topology differs;
- parity or box changes cross a scientific threshold;
- event-mass or valley uncertainty consumes the margin; or
- a derivative/algebra audit fails.

If the cusp and two/three-mode transition pass but no robust one-mode
representative exists in the bounded plane, narrow the phase-language claim
rather than searching a new plane after confirmation.  If the same-family
cusp itself fails after the frozen test, follow Round 33's redirect route; do
not substitute the unrelated three-slab fold.

## 9. What this stage would and would not add to the PRR case

A successful Stage B would close the most important current conceptual gap:
the broad four-slab physical-`d=2` family would connect its exact `B=0` cusp,
weak-`B` theorem, positive-event-mass killed law, allocation-projected rank,
and both fold branches under one fixed total reactivity budget.

It would not, alone, close the PRR release gate.  The next independent step
would still be the predeclared unbounded off-lattice Doi/Feynman--Kac thinning
validation of the frozen representative controls and fold-side modality
changes, followed by the manuscript contraction and final release audit in
Round 33.  Keeping that boundary explicit prevents this finite-volume stage
from being oversold.
