# Positive-budget broad four-slab confirmation protocol

Date frozen: 2026-07-13  
Evidence class: **result-informed confirmation with held-out fine meshes**

## Fixed scientific input

The geometry and absolute catalyst weights are inherited without refitting
from the deterministic \(B=0\) bridge:

\[
 D=0.002,\quad \gamma=0.1,\quad \bar m=0.95,\quad W=1,
 \quad a=0.16,
\]

with midpoint start \(0.14\), relative start \((-0.35,0)\), compact initial
half-width \(0.02\), patch half-width \(0.04\), centres
\((0.35,0.60,0.75,0.90)\), and

\[
w=(0.28,0.27736690132708747,0.0857172266153233,
    0.3569158720575891).
\]

These are the bridge-selected \(s=0.13\) weights.  Neither weights nor patch
geometry may be adjusted in the positive-budget study.

## Disclosed feasibility and budget selection

Before this formal protocol was frozen, the declared low-mesh feasibility
stage evaluated all of \(B=0.01,0.02,0.04,0.08\) on mesh 65.  All four kept
five alternating roots and passed the three event-mass floors, but all failed
at least one \(0.85\) valley ceiling, consistent with the already known coarse
\(B=0\) valley defect.  Their valley pairs were respectively

\[
 (0.88855,0.87102),\ (0.88191,0.89882),\
 (0.86904,0.94255),\ (0.84488,0.99268).
\]

The predeclared escalation evaluated only the two smallest budgets on mesh
97.  At \(B=0.01\), the valleys were \((0.80148,0.85157)\), the event masses
were \((0.005307,0.016721,0.148196)\), and every gate except the second valley
passed.  At \(B=0.02\), the second valley worsened to \(0.87969\).

The frozen budget rule requires five alternating roots, all three event masses
at least \(0.005\), mass balance, and then minimizes the worst valley excess
on mesh 97, with smaller budget as tie-break.  It selects \(B=0.01\).  No
other budget may be run on the held-out meshes.

The feasibility traces are spacing-\(0.05\) PCHIP diagnostics, not formal
point-refined evidence.  They remain pinned and disclosed.

## Killed-Doi model and deterministic solver

On the fixed reflecting box

\[
 m\in[-0.25,1.85],\qquad r_\parallel\in[-1.8,1.8],
\]

let \(Q_0\) be the cell-centred Scharfetter--Gummel/periodic free generator.
With cell-averaged patch field \(k_0\) per unit installed budget and disk
contact cell fractions, the killed row generator is

\[
 Q_B=Q_0-B\operatorname{diag}(k_0),\qquad B=0.01.
\]

The producer uses a matrix-free Kronecker `LinearOperator`; it never forms the
full \(N^3\) generator.  It streams the killed forward law on
\([0,35]\) at spacing \(0.02\), saves only trace projections and the left
state of each sign-changing \(f_t\) bracket, and refines each root by a local
matrix exponential from that checkpoint.  It then propagates the scan-end
state to \(T=100\).

The tail propagation is split at the frozen checkpoints
\(t=(35,50,75,100)\).  At every checkpoint the producer records density,
survival, the minimum state component, and differential mass balance.  The
reported tail gates cover the maximum adjacent-checkpoint survival increase,
minimum checkpoint density, minimum tail state component, final-state minimum,
and \(S(35)-S(100)\).  Together with the spacing-\(0.02\) scan, strict sampled
density positivity starts at \(t=0.5\), not at \(t=0\).  These are sampled
semidiscrete checks; they are not continuous-time interval certification.

Before the held-out run, a small-mesh explicit-CSR audit must verify component
by component that the implemented column law is \(p_{col}'=Q_B^T p_{col}\),
while its adjoint is the row action by \(Q_B\).  The audit covers vector and
matrix actions, adjoint dot products, dtype, shape, full and augmented analytic
traces, \(p\), \(f\), all four time jets, and the identity
\(Q_B\mathbf 1=-Bk_0\).  A local checkpoint exponential at an actual
small-mesh stationary root must agree with propagation directly from \(t=0\).

Time jets are exact semidiscrete generator actions:

\[
 f=p(Bk_0),\quad f_t=pQ_B(Bk_0),\quad
 f_{tt}=pQ_B^2(Bk_0),\quad f_{ttt}=pQ_B^3(Bk_0).
\]

Budget-control jets use the tangent law

\[
 q_t=qQ_B+p\,\partial_BQ_B,\qquad q(0)=0,
\]

and report \(f_B,f_{tB},f_{ttB}\) and \(S_B\) at every refined stationary
point.  A separate augmented matrix-free operator propagates \((p,q)\)
sequentially through the five root times and must reproduce the independently
refined \(p\) states.

The augmented block orientation is also frozen before the held-out run.  It
must agree with the explicit column system

\[
 \frac{d}{dt}\binom{p}{q}=
 \begin{pmatrix}Q_B^T&0\\-\operatorname{diag}(k_0)&Q_B^T\end{pmatrix}
 \binom{p}{q},
\]

and its \(q=\partial_Bp\) block and all reported control jets must agree with
an independently assembled central finite difference using \(B\pm h\).

NumPy global seed 271828 is set before any SciPy sparse-exponential path and
the caller's RNG state is restored afterward.  The trace of every
`LinearOperator` is supplied analytically.  Each replica subprocess also
receives frozen single-thread settings for Python hashing, OpenBLAS, OpenMP,
MKL, Accelerate, and NumExpr.

The public `--execute-frozen` entry point requires the externally audited
64-character manifest SHA-256.  It launches exactly two fresh
`sys.executable` replica subprocesses sequentially; each independently reloads
the manifest, checks the external manifest hash, validates the exact pin
contract, and computes both held-out meshes.  A scientific HOLD exits with
code 2 but is a successful replica completion.  The driver compares the two
raw JSON byte streams.  Only byte-identical canonical JSON with consistent
PASS/HOLD status may be promoted.  It writes a deterministic reproducibility
record before making the canonical result the commit marker.  A detected
replica error, mismatch, missing output, manifest change, inconsistent exit
code, or caught publication exception preserves any prior canonical result
and evidence byte for byte.  This two-file publication step is failure-atomic
for caught process and filesystem exceptions; it is not claimed to be
crash-consistent across an uncatchable `SIGKILL`, kernel failure, or power loss
between the two final replacements.  Downstream use must therefore require
that the reproducibility record's canonical-result hash matches the observed
canonical result.

The manifest validator freezes the complete scientific, provenance, claim,
execution, and forbidden-promotion contract.  It requires the exact set of 13
pin roles and their exact report-relative paths, rejects missing or additional
roles, malformed hashes, duplicate paths, absolute paths, parent traversal,
and resolved paths outside the report root.

## Held-out meshes and frozen gates

Meshes 113 and 129 are held out: neither has been evaluated at positive
budget before this freeze.  Each mesh must pass:

- exactly five retained simple sign-changing roots with
  max--min--max--min--max topology;
- minimum/maximum peak ratio at least \(0.10\);
- both valley/smaller-adjacent-peak ratios at most \(0.85\);
- scaled root residual at most \(10^{-8}\);
- absolute scaled curvature at least \(0.05\);
- positive derivative at \(t=0.5\), negative derivative at \(t=35\);
- positive sampled density from \(t=0.5\), positive survival, and sampled
  survival monotonicity through all \(35,50,75,100\) checkpoints;
- killed-generator differential mass-balance error at most \(10^{-9}\);
- \(S'=-f\), \(Q_B\mathbf 1=-Bk_0\), and the final three-basin partition
  \(M_1+M_2+M_3=1-S(100)\), each closed to \(10^{-9}\);
- tangent/direct state relative \(L^1\) discrepancy at roots at most
  \(10^{-9}\); and
- event-basin masses

\[
 M_1=1-S(v_1),\quad M_2=S(v_1)-S(v_2),\quad
 M_3=S(v_2)-S(100)
\]

  each at least \(0.005\).

Between meshes 113 and 129, the maximum paired-root time difference must be
at most \(0.10\), peak-ratio difference at most \(0.03\), maximum valley-ratio
difference at most \(0.03\), maximum event-mass difference at most \(0.01\),
and final-survival difference at most \(0.02\).  These tolerances are frozen
before either held-out calculation.

A legitimate structural failure remains evidence.  If a mesh lacks the
required five-root topology, valley pair, or three event masses, every
unavailable cross-mesh difference is serialized as JSON null, its
corresponding gate is explicitly false, and the canonical finite JSON records
a HOLD.  Undefined peak ratios and event-mass sums are also null; no
NaN or infinity is permitted anywhere in an output.

## Claim boundary

Only if every per-mesh and agreement gate passes may
`positive_B_event_mass_shape_confirmation=true`.  Regardless of outcome, the
following remain false:

- `preregistered_discovery`;
- `continuum_interval_verified`;
- `unbounded_domain_FV_limit_verified`;
- `independent_solver_verified`; and
- `project_gate_passed`.

This is one fixed-box semidiscrete positive-budget confirmation, not a PDE
convergence theorem or a PRR/project gate.  No manuscript TeX file may be
edited in this stage.
