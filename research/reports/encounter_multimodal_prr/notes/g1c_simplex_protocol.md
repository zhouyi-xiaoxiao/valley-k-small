# G1c result-informed full-simplex discovery protocol

Status: **frozen before any G1c control value is computed**. This is a new
sequential-design stage, not a retrospective amendment of G1b.

## Why a new stage is required

The formal G1b line returned neither a near-zero extremum nor a matched
adjacent-control sign bracket. It also returned an unmatched-extrema review
flag near `theta=0.7`. The later, explicitly post-result diagnostic reproduced
the extra pair on a finer time grid and showed that both extrema remain
strictly below `f_t=0`. That diagnosis rules out a fold at the reviewed
control, but it does **not** authorize the old G1b `line empty` branch. G1c is
therefore frozen prospectively, with the G1b result and its diagnostic named
as inputs.

## Fixed family and control set

No physical parameter, domain, contact geometry, transport coefficient,
catalyst location, catalyst width, initial law, installed budget, spatial
mesh, or time mesh changes from G1b. Only the three nonnegative catalyst
weights vary. Write

\[
  w=(i,j,k)/10,\qquad i,j,k\in\mathbb Z_{\ge 0},\qquad i+j+k=10.
\]

The complete `0.1` triangular lattice contains 66 controls. Enumeration is
fixed as `i=0,...,10`, then `j=0,...,10-i`, with `k=10-i-j`. The state mesh is
`65 x 65 x 49` (207,025 states). The sampled times are `0,0.25,...,80`, and
semigroup output is retained in overlapping chunks of at most 41 state rows.
Only observable curves are stored; a full state history is forbidden.

Each arbitrary weight vector is assembled directly. It is never represented
as a point on the old one-dimensional `theta` line. The shared G1a physical
foundation gates and new simplex-specific weight, budget, tensor-killing, and
generator gates must all pass at every control.

## Observable jets and per-control screen

For killed row generator `Q`, initial row law `p_0`, and killing vector `q`,
the stored curves are computed from generator actions:

\[
 f^{(r)}(t)=p_0 e^{tQ}Q^r q,\qquad r=0,1,2,3.
\]

The predeclared per-control screen is inherited unchanged from G1b:

- exclude brackets starting before `t=0.5` and density below `10^-12` of the
  sampled peak;
- call an `f_tt=0` extremum near zero only if
  `abs(t f_t/f) <= 0.05`;
- use sampled sign brackets and linear interpolation only. These are discovery
  diagnostics, not root certificates.

## Simplex edges and three distinct outcomes

Two controls are adjacent exactly when their integer triplets have L1
distance two. There are 165 such undirected edges. Same-kind `f_t` extrema are
matched across an edge by the G1b order-preserving,
maximum-cardinality/minimum-time-separation rule with tolerance 2.0.

The result keeps three categories separate:

1. `near_zero`: an extremum at one sampled control satisfies the fixed
   dimensionless threshold;
2. `sign_edge`: a matched same-kind extremum has opposite nonzero `f_t` signs,
   or an exactly zero endpoint, across one simplex edge;
3. `unmatched_topology`: root count, retained topology, filter signature,
   matching cardinality, or matching uniqueness changes across an edge.

Only strictly interior occurrences of categories 1 and 2 are candidate seeds.
For a near-zero control, all three sampled weights must be positive. For a
strict opposite-sign edge, the runner linearly interpolates the zero crossing
of the matched extremum height in weight space; the crossing is eligible when
all three interpolated weights are positive, even if an edge endpoint is on
the boundary. Exact-zero evidence occurs at its endpoint and uses that
endpoint's weight. A crossing that lies on a simplex face is retained as a
boundary diagnostic but does not pass the family discovery gate. Category 3
is not silently promoted to a candidate; it requires manual review.

If the same matched extremum is exactly zero at both edge endpoints, no unique
crossing location is identified. The runner records it separately as an
`unresolved_whole_edge_zero` manual-review case; it is neither an interior
candidate nor a boundary diagnostic.

## Decision rule and claim boundary

If no eligible interior near-zero control and no eligible interior sign
crossing exists **and** no topology review is required, the discovery gate for
this fixed physical family fails. If no eligible candidate exists but an
unmatched, ambiguous, root-count, retained-topology, or filter-signature change
exists, the result is `INCONCLUSIVE_MANUAL_REVIEW`, not a failed gate. Boundary
diagnostics and umbrella topology flags cannot select a segment. G1c does not
retune the family in either branch.

If one or more candidate seeds exist, G1c still does not select or confirm a
fold. A later stage may choose at most one segment, must freeze a new manifest
before evaluating confirmation values, and must add control sensitivities,
root residuals, mesh/time convergence, tail checks, and an independent
numerical method.

Every G1c checkpoint and final result must state
`continuum_verified=false` and `project_gate_passed=false`. A G1c candidate is
not evidence of a continuum fold, cusp, PDE persistence theorem, or PRR-level
project gate.

## Reproducibility and interruption policy

The manifest strictly pins the G1a certificate and producer, the formal G1b
line result and producer, and the post-result manual-review artifact and
producer. It also pins the audited G1c runner and this protocol note by
SHA-256 before any formal control is evaluated. Formal execution is permitted
only in the repository `.venv`.

The output path, checkpoint namespace, lock, ledger, manifest, pinned inputs,
runner, and protocol note must remain disjoint. Symlinked output, checkpoint,
or lock targets fail before the first control is evaluated.

Every control has an atomic checkpoint. A SHA-256 integrity ledger binds each
filename to its control index, integer triplet, weights, and content. Resume
rebuilds the arbitrary-weight model, re-runs all gates, validates curve bounds
and generator-action identities, and recomputes candidate analysis. A
nonblocking advisory lock permits only one writer. Orphan checkpoints,
temporary files, hash mismatches, configuration drift, producer drift, and
claim-flag changes fail closed.
