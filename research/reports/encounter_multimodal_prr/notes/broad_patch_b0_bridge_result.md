# Broad-patch \(B=0\) numerical-bridge result

## Evidence boundary

**Status: PASS as a result-informed exact-continuum/finite-volume \(B=0\)
bridge; not preregistered discovery and not a positive-budget result.**

This chain is separate from the frozen half-width-\(0.008\) study.  The
half-width-\(0.04\), initial-half-width-\(0.02\) geometry, its approximate
continuum cusp, and the \(s=0.11\) trend through mesh 129 were known before
freeze.  The \(s=0.12,0.13\) finite-volume calculations and mesh 193 were
held out until after the protocol, producer, tests, and manifest were hashed.
The calculation remains labelled result-informed throughout.

Frozen chain:

| component | SHA-256 |
| --- | --- |
| producer | `d1d68667f5cbb9c8363a94f2f9ea22540f841065e02696f669beca9758e3a233` |
| tests | `0d683f8ed7cfd8fee2cef992078962a05c2cb8074629c8947cb233300c8b4490` |
| protocol | `56937590efc0ea90841cd7ff32b3386c5d81469ec51034329d7e0e13133bee35` |
| manifest | `263d4bd5e95f4cf477916948f2e4bbf3cd99066ac9dc9a9ab5726f2030a6f1e8` |
| result | `6a18e668401ae5776eebd7bd58c7bd553838db21998efdba2865cea094ae207b` |

The manifest also pins the exact-continuum, finite-volume, and grid
dependencies by hash.

## Exact-continuum result

For \(D=0.002\), \(\gamma=0.1\), OU mean \(0.95\), \(W=1\), contact radius
\(0.16\), compact initial half-width \(0.02\), patch half-width \(0.04\),
centres \((0.35,0.60,0.75,0.90)\), and fixed \(w_0=0.28\), the direct
continuum cusp is

\[
 t_c=13.30724696053485,
\]

\[
 w_c=(0.28,0.2311524026006418,0.2072253337829660,
      0.2816222636163921).
\]

The scaled fourth derivative is \(-44.68164505099193\), and the dimensionless
unfolding singular-value ratio is \(0.2649031196329416\).  Primary/fine cusp
times differ by \(8.43\times10^{-12}\), weights by
\(1.05\times10^{-14}\), and scaled fourth derivatives by
\(3.25\times10^{-9}\).

The original exact-continuum selection rule chooses \(s=0.11\), with weights

\[
 (0.28,0.2702569784460959,0.1044107815641914,
  0.3453322399897127).
\]

It has three maxima and two minima, peak ratio \(0.8388190731\), and valley
ratios \(0.7037011678\) and \(0.8440058184\).  Thus it passes the direct
continuum gate but has only \(0.005994\) headroom at the second valley.

## Separately frozen bridge-control selection

The bridge rule evaluates \(s=0.11,0.12,0.13\), requires exact-continuum
eligibility and finite-volume observability on both meshes 129 and 193, then
maximizes the worst valley margin across those two meshes.  It selects
\(s=0.13\):

| step | passes meshes 129 and 193 | worst valley margin | worst peak ratio |
| ---: | :---: | ---: | ---: |
| 0.11 | no | -0.00712161 | 0.81843648 |
| 0.12 | yes | 0.01230141 | 0.81682491 |
| 0.13 | yes | 0.03206856 | 0.81479156 |

This does not alter the narrow-chain or broad exact-continuum selection of
\(s=0.11\).  It identifies a more discretization-robust absolute control for
the next positive-budget calculation.

At \(s=0.13\), the exact-continuum weights are

\[
 (0.28,0.2773669013270875,0.0857172266153233,
  0.3569158720575891).
\]

The exact roots are approximately
\(3.22955,5.04475,8.54382,13.30725,23.29910\), the peak ratio is
\(0.8348824919\), and the valley ratios are \(0.7102792574\) and
\(0.8025887957\).

## Finite-volume convergence at the bridge control

The cell-centred Scharfetter--Gummel calculation uses odd cubic meshes on one
fixed reflecting box and never forms the full \(N^3\) generator.  Every mesh
retains max--min--max--min--max topology.

| \(N\) | cusp time | cusp-time error | maximum root-time error | peak ratio | valley ratios |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 65 | 13.816424 | 0.509177 | 0.533676 | 0.817403 | 0.895225, 0.857214 |
| 97 | 13.577891 | 0.270644 | 0.264253 | 0.807891 | 0.808147, 0.831663 |
| 129 | 13.459124 | 0.151877 | 0.156229 | 0.814792 | 0.771280, 0.817931 |
| 193 | 13.373870 | 0.066623 | 0.066853 | 0.830775 | 0.737575, 0.806951 |

Both error sequences decrease strictly.  Meshes 129 and 193 pass the frozen
peak/valley gates.  Coarser meshes are retained as convergence evidence, not
misreported as quantitatively observable: mesh 65 fails both valley ceilings.

Patch and initial masses agree with one within \(7.4\times10^{-14}\), the disk
area agrees with \(\pi a^2\) within \(8.9\times10^{-16}\), and the largest
generator row-sum residual is \(3.1\times10^{-14}\).  An audit-only full
729-state Kronecker calculation at mesh 9 agrees with the factorized jets
through order four at \(t=0,0.7,4,13\); the maximum scaled discrepancy is
\(2.78\times10^{-16}\).

As a post-result box diagnostic, a dense scan of the exact free Gaussian
transition laws over \(0<t\le100\) and the endpoints of the compact initial
supports found maximum one-time mass outside the reflecting intervals of
\(2.23\times10^{-18}\) for the midpoint factor and
\(6.39\times10^{-19}\) for the relative-parallel factor.  This supports the
chosen box but is not a pathwise exit bound or an unbounded-domain FV proof.

The first pre-refreeze rerun exposed last-digit non-determinism: 40 floating
fields differed, with maximum absolute difference
\(6.70\times10^{-11}\).  That P2 was fixed directly.  The deterministic
refreeze pins NumPy global seed 1729 before any SciPy sparse-exponential call
and restores the caller's full RNG state afterward.  It changes no geometry,
control, mesh, threshold, or claim flag.  Two independent complete formal
processes now produce byte-identical JSON with SHA-256
`6a18e668401ae5776eebd7bd58c7bd553838db21998efdba2865cea094ae207b`.
All nine focused tests, including RNG restoration and a bitwise repeated
sparse-exponential probe, pass.

## Claim boundary

The result correctly leaves all of the following false:

- `preregistered_discovery`;
- `continuum_interval_verified`;
- `finite_B_Doi_verified`;
- `unbounded_domain_FV_limit_verified`; and
- `project_gate_passed`.

The next scientific promotion step is a separately frozen positive-\(B\)
killed-Doi continuation at the bridge-selected absolute control, with mesh
convergence and survival/mass-balance checks.  This \(B=0\) bridge does not by
itself justify any positive budget.
