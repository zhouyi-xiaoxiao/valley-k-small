# Post-result manual-review protocol

Date frozen: 2026-07-13, after the formal control-line result was read and
before the diagnostic calculation below was run.

## Question and evidence boundary

The formal (65\times65\times49) line calculation contains four retained
zeros of (f_{tt}) at (\theta=0.7), whereas the adjacent controls contain two.
The extra maximum--minimum pair of (f_t) is sampled entirely below zero.  This
triggered the predeclared unmatched-extremum manual-review guard.

This diagnostic asks only whether finer time sampling at the same mesh,
physical parameters, control, and generator-action observables reproduces the
extra pair while retaining exactly one maximum of (f).  Because the control
and diagnostic were selected after reading the formal result, the output is
post-result evidence.  It cannot be cited as predeclared fold discovery,
continuum verification, a passed project gate, or permission to relabel the
formal line as empty.

## Frozen calculation

- Reuse the formal mesh and the control (\theta=0.7), with weights
  ((0.245,0.25,0.505)).
- Reuse the model assembler, foundation gates, and generator actions
  (f,f_t,f_{tt},f_{ttt}).
- Sample (t\in[0,20]) at spacing (0.05), five times finer than the formal
  discovery grid, retaining at most 41 state rows.
- Apply the formal per-control filter and near-zero threshold unchanged.
- At common (0.25)-spaced times, compare all five stored observables against
  the immutable formal result.  Any maximum absolute difference above
  (5\times10^{-11}) fails the diagnostic.

## Frozen classification

The local flag is classified as a reproduced negative derivative wiggle, not
a fold at the reviewed control, only if all of the following hold:

1. exactly one retained root of (f_t), classified as a maximum of (f);
2. zero near-zero extrema under the original dimensionless threshold;
3. every additional retained extremum of (f_t), beyond the first
   maximum--minimum pair present at adjacent controls, has interpolated
   (f_t)<-10^{-4}; and
4. the common-time reproducibility check passes.

Passing those tests resolves the semantic question at (\theta=0.7) but does
not satisfy the frozen protocol's stable-extremum-matching condition.  The
formal line action therefore remains inconclusive under the original
protocol.  Any simplex calculation must be frozen prospectively as a new G1c
study, with the result-informed provenance stated explicitly.
