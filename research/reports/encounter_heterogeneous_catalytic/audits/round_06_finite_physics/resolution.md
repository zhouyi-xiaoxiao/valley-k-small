# Round 06 resolution — finite-radius 2D/3D physics

Date: 2026-07-11  
Status: **PASS; no open B0, B1, or B2 scientific finding**

## Decision

Both reviewers independently reproduced the finite-state transport, reaction
masks, strict derivative roots, matched budgets, and capacity calculations.
Reviewer A found one material framing error and three bounded provenance or
limit issues in the pre-regeneration snapshot.  Reviewer B audited the
regenerated snapshot and found no remaining scientific blocker.  The promoted
claim is now deliberately narrower and more accurate:

- in M2D-E, patterned and homogeneous endpoints both have strict
  max--min--max structure; spatial patterning raises the secondary/primary
  peak ratio from `1.02%--1.81%` to `4.58%--8.15%`, producing a
  resolved-unimodal to resolved-bimodal class change rather than creating a
  previously absent extremum;
- M2D-C single-patch and co-located controls are resolved-unimodal because
  they fail scale-persistence and valley-depth gates, although their shallow
  strict extrema are retained;
- the finite-grid fold family remains a genuine nondegenerate pair-creation
  certificate, but its critical parameter is not grid-converged;
- 2D and 3D capacity calculations are calibration results, not proofs of a
  bounded patterned continuum fold.

## Remediation ledger

1. **Strict versus resolved modality (B1, closed).**  Exact-semigroup roots,
   strict mode counts, peak ratios, and classifier semantics are persisted for
   matched, mechanism-control, and coordinate-sensitivity families.  The
   manuscript, figures, README, notebook, and tests now say “promotes a
   subthreshold clock.”
2. **Finite-radius homogeneous reference (B2, closed).**  The exact unit-square
   midpoint contact-tube volume
   `V_T(a)=pi*a^2-(8/3)*a^3+a^4/2` for `0<=a<=1`, the patch-clearance gate, and
   the resulting `kappa_bar=2.169402271` are derived in the manuscript and
   theory note.  The current finest dynamics grid is explicitly reported as
   `14.8%` below that quadrature target.
3. **3D double-limit language (B2, closed by downgrade).**  The shrinking
   radius path keeps `a/h` near `7.4--7.65`; the `0.114%` slope agreement is
   described only as continuum-compatible coupled-path evidence.  The JSON
   records that radius and grid limits were not separated and that no
   continuum coefficient is certified.
4. **Stale 2D capacity provenance (B2, closed).**  The current solver and all
   outputs were regenerated and re-hashed.
5. **Units and geometric quadrature (B3, closed).**  The paper states the
   dimensions of `D,v,gamma,kappa`, the nondimensional groups, and that the
   equal-node budget is a geometric state sum rather than a stationary
   exposure match.
6. **Optional hardening retained.**  A longer persisted tail extension for the
   largest uniform-domain control remains useful but is not needed for the
   already located late peak; it is not used for an exact global root-count
   claim.

## Revalidation

The final focused recheck reported:

- `31 passed` across mechanism, matched, coordinate, 2D capacity, 3D,
  multidimensional design, manuscript, and manifest gates;
- `14` non-aggregate manifests with zero missing files and zero hash mismatch;
- a 21-page, 12-figure manuscript with zero missing files, undefined
  references/citations, or overfull boxes.

The profile-specific `full` and `verify` execution proofs remain a mechanical
final-package postcondition after all ten audit reports and resolutions stop
changing.  This does not weaken any scientific conclusion; it prevents an
intermediate dirty snapshot from being mislabeled as a submission build.
