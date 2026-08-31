# Result-informed broad-patch \(B=0\) numerical-bridge protocol

Date frozen: 2026-07-13  
Evidence class: **result-informed numerical bridge, not preregistered discovery**

Deterministic refreeze: 2026-07-13, after the complete first result and a
non-bitwise-identical rerun were known.  The refreeze changes only RNG control,
tests, hashes, and reproducibility metadata.  Geometry, candidate controls,
selection priority, meshes, thresholds, and claim flags are unchanged.

## Purpose and separation from the narrow study

This calculation asks whether a more mesh-resolvable four-patch geometry
retains the exact-continuum three-peak mechanism and whether a separately
assembled cell-centred Scharfetter--Gummel finite-volume discretization tends
toward it at zero installed budget.  It does not change, replace, or append to
the frozen half-width-\(0.008\) evidence chain.

The physical parameters are \(D=0.002\), \(\gamma=0.1\), OU mean \(0.95\),
period \(W=1\), contact radius \(0.16\), midpoint start \(0.14\), relative
start \((-0.35,0)\), compact initial half-width \(0.02\), patch half-width
\(0.04\), centres \((0.35,0.60,0.75,0.90)\), and fixed \(w_0=0.28\).

The geometry, approximate exact-continuum cusp, the fact that the inward grid
contains passing controls, and the \(65/97/129\) trend at \(s=0.11\) were
observed before the original scientific protocol was frozen.  Steps
\(s=0.12,0.13\) were not evaluated on any finite-volume mesh, and the
\(193^3\) factorized-mesh outcome was not evaluated, before that original
freeze.  All outcomes were known before the later deterministic refreeze.
The entire calculation remains labelled result-informed; neither the held-out
evaluations nor the reproducibility repair is promoted to an independent
discovery.

## Exact-continuum arm

The producer imports the already frozen analytic-kernel implementation only
as a pinned dependency and instantiates a new parameter object.  It evaluates
the unbounded longitudinal OU kernel, periodic transverse heat kernel, smooth
compact initial laws and patches, and disk contact integral directly.  The
cusp is solved on \([13.2,13.4]\).  The strict inward normal and candidate
steps \(0.02,0.03,\ldots,0.20\) use the same definitions as the narrow study.

Eligibility is frozen as:

- all four weights are strictly positive and sum to one;
- exactly three maxima and two minima in alternating order;
- minimum/maximum peak ratio at least \(0.10\);
- each valley divided by its smaller adjacent peak at most \(0.85\);
- scaled curvature magnitude at least \(0.05\);
- scaled root residual at most \(10^{-8}\);
- positive derivative at \(t=0.1\), negative derivative at \(t=100\), and no
  retained sampled zero plateau.

Among eligible steps, maximize minimum weight, then worst-valley margin, then
peak ratio, then prefer the smaller step.  The time screen is
\([0.1,100]\) at spacing \(0.002\).  Primary and fine quadrature/Cauchy
configurations must agree within the frozen tolerances.

## Finite-volume arm

The finite-volume arm fixes reflecting boxes

\[
 m\in[-0.25,1.85],\qquad r_\parallel\in[-1.8,1.8],
\]

and the periodic transverse interval of width one.  It uses cell-centred
Scharfetter--Gummel generators for the two OU coordinates, a conservative
periodic diffusion generator transversely, cell-integrated compact bumps,
and cell-area fractions for the disk contact observable.  The zero-budget
free generator factorizes, so no full \(N^3\) matrix is formed.

The frozen odd cubic meshes are \(N=65,97,129,193\).  Odd meshes keep zero at
a transverse cell centre and refine every coordinate together.  On every
mesh the producer:

1. solves the affine cusp in \([12.5,14.5]\);
2. evaluates the three absolute controls at exact-continuum inward steps
   \(s=0.11,0.12,0.13\);
3. screens \([0,100]\) at spacing \(0.02\) for all derivative sign changes;
4. refines each root with pointwise matrix-exponential jets; and
5. reports topology, densities, curvatures, peak ratio, valley ratios, mass
   normalization, contact area, and generator conservation.

The bridge-control rule is separate from the exact-continuum selection rule.
A candidate must pass the exact-continuum gates and the peak/valley/topology
gates on both \(N=129\) and \(N=193\).  Among those candidates, select by:

1. maximum worst valley margin across the two meshes;
2. maximum worst peak ratio across the two meshes;
3. maximum catalyst minimum weight; and
4. deterministic smaller-step tie-break.

This result-informed robustness rule is frozen before evaluating either new
step and before evaluating \(N=193\).  It does not retroactively alter the
narrow-chain or broad exact-continuum selection of \(s=0.11\).

The bridge passes only if all four meshes retain five alternating roots at
the bridge-selected absolute control, the cusp-time and maximum root-time
errors decrease strictly across the mesh sequence, the finest cusp-time error
and maximum root-time error are at most \(0.10\), and both \(N=129\) and
\(N=193\) meet the continuum observability thresholds.

The sampled root census is not an interval-exhaustive proof.  Mesh convergence
on a fixed reflecting box is not a proof of the unbounded-domain limit.

## Deterministic execution contract

The first full rerun preserved all scientific gates but differed in last-bit
floating values because SciPy's sparse one-norm estimation samples sign
vectors from NumPy's legacy global RNG.  The deterministic refreeze therefore
pins `numpy_global_seed=1729` in the manifest.  The producer saves the caller's
complete NumPy global RNG state, sets the pinned seed before any exact or
finite-volume calculation can reach `expm_multiply`, and restores the saved
state in a `finally` block.  Tests require both RNG-state restoration and
bitwise equality of two independently seeded sparse-exponential probes.

Two complete formal executions of the refrozen producer must write
byte-identical JSON before the official result is accepted.  This repair is
computational only and occurs after all scientific results were known.

## Mandatory negative claims

Regardless of the numerical outcome, the result must retain:

- `preregistered_discovery=false`;
- `continuum_interval_verified=false`;
- `finite_B_Doi_verified=false`;
- `unbounded_domain_FV_limit_verified=false`; and
- `project_gate_passed=false`.

No main manuscript TeX file may be edited by this calculation.
