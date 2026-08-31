# Round 03 resolution — GIG asymptotics and multidimensional screening

Date: 2026-07-11  
Status: **PASS within the declared free-space narrow-patch screening scope**

Two independent reviewers found no B0 or B1.  Their original reports identified
bounded defects in the sampled CTMC comparison, the `B=0` domain, the spatial
distance domain, numerical stability, and root-count wording.  Both reviewers
then rechecked the remediated snapshot independently and returned PASS.

## Remediation decisions

1. Canonical finite-CTMC channel modes are now Brent roots of
   `alpha exp(T t) T b_j`, not sampled-grid argmaxes.  The saved roots are
   `32.1534061543059` and `196.145870006967`, have negative curvature, and give
   GIG errors `17.5920%` and `8.1348%`.
2. The `B=0` normalizer is stated and enforced only for `nu>1`; the stationary
   point `A/nu` is distinguished from the mode of a normalizable density.
3. The catalyst map now requires
   `A_j >= ell^2/(4 Dr)` and fails before taking a square root outside that
   physical domain.  All 12 validated cases satisfy the condition.
4. The time-independent drift cross factor is explicit.  It cancels from one
   normalized conditional shape but contributes to physical splitting
   amplitudes.
5. The stable mode uses the rationalized expression.  Normalizers are computed
   in log space; inverse-height weights use log-sum-exp; mixture roots use the
   stable score `f'/f` and curvature ratio `f''/f`.
6. Scaled Bessel evaluation has disjoint small-, intermediate-, and
   large-argument behavior.  A four-term DLMF 10.40.2 large-argument expansion
   handles `x>=1e5`; only unresolved `x<1e-6` may use the normalizable
   `B -> 0` limit; unresolved intermediate failures raise.  Exact
   half-integer regressions cover `K_{1/2}` and `K_{5/2}` at arguments near the
   branch and at `2e9`.
7. The paper and design note say that the finite scan *found* the expected
   sign-changing simple roots.  They do not claim interval-certified absence
   of tangential or even-multiplicity roots.
8. The multidimensional child manifest directly hashes its design note, and
   all affected summaries, figures, notebook data, TeX, PDF, child manifests,
   and aggregate inventory were regenerated or rechecked.

## Revalidation evidence

- Reviewer A compared five Bessel orders at `x=99999`, `100000`, `100001`, and
  `2e9` against 100-digit `mpmath`; the maximum scaled-log error was
  `1.34e-15`.
- Reviewer A independently rooted the two CTMC channel derivatives and
  reconstructed all 12 multidimensional scans.
- Reviewer B independently swept CTMC horizons and scan spacings, reconstructed
  the 60 saved critical points in log space, checked the feasibility boundary
  from both sides, executed all 18 notebook cells, and verified every declared
  manifest hash.
- The final focused GIG/multidimensional suite completed `12 passed`; the wider
  GIG/multidimensional/manuscript suite completed `14 passed` in Reviewer A's
  recheck.

## Retained claim boundary

This round certifies the exact GIG-family algebra, stable implementation,
continuous finite-CTMC comparison, and the declared 12-case free-space
screening family.  It does not certify a finite-patch reflected remainder, a
bounded-domain three- or four-mode theorem, physical realization of abstract
mixture weights, a universal exponent after tangential integration, or an
interval proof excluding additional tangential roots.

Required Round-03 findings are closed; the retained items are explicit
scientific scope boundaries rather than unresolved audit defects.
