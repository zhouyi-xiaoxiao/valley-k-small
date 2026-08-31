# Round 27: broad-patch \(B=0\) numerical-bridge self-audit

Date: 2026-07-13  
Evidence timing: **result-informed numerical bridge; not preregistered discovery**

## Verdict

**PASS FOR THE DECLARED EXACT-CONTINUUM/FINITE-VOLUME \(B=0\) BRIDGE; HOLD
FOR POSITIVE \(B\), INTERVAL CERTIFICATION, UNBOUNDED-DOMAIN FV CONVERGENCE,
AND THE PROJECT/PRR GATE.**

The broader half-width-\(0.04\) geometry has a relative-shape-qualified
exact-continuum three-peak free-exposure curve.  A cell-centred
Scharfetter--Gummel sequence preserves all
five alternating stationary points and converges toward the continuum cusp
and root times.  The separately frozen bridge-control rule selects
\(s=0.13\), for which meshes 129 and 193 satisfy the quantitative peak/valley
gates.  Within this scope, this audit finds no P0, P1, or P2 defect.

## Evidence-timing attack

The geometry, approximate continuum cusp, passing continuum inward steps, and
the \(s=0.11\) finite-volume trend on meshes 65, 97, and 129 were known before
freeze.  They are therefore confirmation evidence only.  Before any
finite-volume evaluation at \(s=0.12\) or \(0.13\), and before any mesh-193
evaluation, the protocol froze:

- candidate steps \(0.11,0.12,0.13\);
- required meshes 129 and 193;
- exact-continuum and mesh relative-shape gates; and
- the lexicographic robustness priority.

The resulting choice \(s=0.13\) is legitimately determined by that frozen
rule, but the overall study remains labelled result-informed.  It does not
retroactively replace the narrow-chain \(s=0.11\) or the broad
exact-continuum rule's \(s=0.11\).

Frozen hashes are:

| component | SHA-256 |
| --- | --- |
| producer | `d1d68667f5cbb9c8363a94f2f9ea22540f841065e02696f669beca9758e3a233` |
| tests | `0d683f8ed7cfd8fee2cef992078962a05c2cb8074629c8947cb233300c8b4490` |
| protocol | `56937590efc0ea90841cd7ff32b3386c5d81469ec51034329d7e0e13133bee35` |
| manifest | `263d4bd5e95f4cf477916948f2e4bbf3cd99066ac9dc9a9ab5726f2030a6f1e8` |
| result | `6a18e668401ae5776eebd7bd58c7bd553838db21998efdba2865cea094ae207b` |

## Exact-continuum claims tested

The direct analytic-kernel arm gives

\[
 t_c=13.30724696053485,
 \qquad
 w_c=(0.28,0.2311524026006418,0.2072253337829660,
      0.2816222636163921),
\]

scaled fourth derivative \(-44.68164505099193\), and unfolding ratio
\(0.2649031196329416\).  Primary/fine time and weight differences are
\(8.43\times10^{-12}\) and \(1.05\times10^{-14}\), respectively.

The exact selection rule chooses \(s=0.11\), with three maxima, two minima,
peak ratio \(0.8388190731\), and valleys \(0.7037011678,0.8440058184\).
The independent bridge rule selects \(s=0.13\); at the same exact continuum it
has weights

\[
 (0.28,0.2773669013270875,0.0857172266153233,
  0.3569158720575891),
\]

peak ratio \(0.8348824919\), and valleys
\(0.7102792574,0.8025887957\).  Thus the robustness gain is not obtained by
changing geometry or violating weight positivity.

## Finite-volume claims tested

At the bridge control, all four meshes have five alternating roots.  The
cusp-time errors are

\[
 0.5091766,\ 0.2706445,\ 0.1518766,\ 0.0666234,
\]

and the maximum root-time errors are

\[
 0.5336764,\ 0.2642529,\ 0.1562289,\ 0.0668532.
\]

Both sequences decrease strictly.  On meshes 129 and 193 the valley pairs
are \((0.7712800,0.8179314)\) and
\((0.7375754,0.8069509)\), so both pass the frozen \(0.85\) ceiling.  Mesh 65
does not pass the quantitative valley gate and is reported only as coarse
topological/convergence evidence.

Mass and geometry checks pass by large margins.  Patch and initial masses are
within \(7.4\times10^{-14}\) of one, contact area is within
\(8.9\times10^{-16}\) of \(\pi a^2\), and generator row sums are within
\(3.1\times10^{-14}\) of zero.

## Independent factorization attack

An audit-only calculation formed the full 729-state Kronecker generator on a
mesh-9 model.  It constructed full-generator observable actions through order
four, propagated the full initial law, and compared against the producer's
factorized midpoint/contact jets at \(t=0,0.7,4,13\).  The maximum absolute
difference was \(3.33\times10^{-16}\), and the maximum scaled difference was
\(2.78\times10^{-16}\).  This directly attacks incorrect Kronecker ordering,
action-column reshaping, and Leibniz assembly.

An additional audit-only dense scan of the exact one-time Gaussian transition
laws over \(0<t\le100\), including both endpoints of each compact initial
support, found maximum mass outside the finite-volume intervals of
\(2.23\times10^{-18}\) for the midpoint factor and
\(6.39\times10^{-19}\) for the relative-parallel factor.  This is useful box
evidence, but it is not substituted for a pathwise exit estimate or a
two-box convergence test.

Nine focused tests pass.  Ruff lint and format checks pass.  The frozen
producer verifies its own code, tests, protocol, and three dependency hashes
before execution.

## Reproducibility attack and resolution

A second complete formal run was scientifically invariant but not
byte-identical.  It reproduced the PASS status, \(s=0.13\) selection, all
Boolean gates, all categorical fields, and the four-mesh topology.  Exactly 40
floating fields differed.  The largest absolute difference was
\(6.70\times10^{-11}\) in one scaled curvature, the largest root-time
difference was \(1.29\times10^{-12}\), and the largest valley-ratio difference
was \(1.33\times10^{-12}\).  These are many orders below the frozen gates and
do not change their truth values.

Inspection of the local SciPy path showed that its sparse one-norm estimator
resamples sign vectors from the global NumPy random state.  The producer was
therefore deterministically refrozen after all scientific results were known.
It pins seed 1729 before any sparse-exponential path and restores the caller's
complete RNG state in a `finally` block.  Geometry, controls, selection,
meshes, gates, and claim flags are unchanged.  Two independent complete
formal processes now write byte-identical JSON with SHA-256
`6a18e668401ae5776eebd7bd58c7bd553838db21998efdba2865cea094ae207b`.
Focused tests separately enforce RNG restoration and bitwise equality of a
repeated seeded sparse-exponential probe.  The P2 is closed, with the original
failed byte audit retained as historical evidence rather than erased.

## Unresolved proof and model boundaries

The following are limitations, not hidden pass claims:

1. The finite-volume root census uses a spacing-\(0.02\) sign screen followed
   by pointwise refinement.  It is not an interval proof against an unresolved
   tangential root between samples.
2. The SG meshes converge on one fixed reflecting box.  No two-box or analytic
   tail argument proves the unbounded-domain FV limit.
3. The calculation is the \(B=0\) free-exposure derivative.  It does not solve
   the killed-Doi equation at any positive installed budget and supplies no
   numerical value of a persistence radius \(B_*\).
4. It does not address physical \(d=3\), reaction-model robustness, or the
   full project/publication gate.

Accordingly all interval, finite-\(B\), unbounded-domain-limit, and project
flags remain false.

## Severity ledger

| severity | count | disposition |
| --- | ---: | --- |
| P0 | 0 | no positive-\(B\), interval, unbounded-limit, or PRR/project claim is made |
| P1 | 0 | evidence timing and the separate bridge-control rule are explicit |
| P2 | 1 closed | deterministic refreeze plus two byte-identical full runs; original failed audit retained |
| open promotion gate | 4 | positive \(B\), interval roots, unbounded-domain FV limit, and physical \(d=3\)/general theory |

No main manuscript TeX file was edited.
