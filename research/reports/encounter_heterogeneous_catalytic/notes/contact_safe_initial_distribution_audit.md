# Contact-safe initial-distribution audit

## Problem and claim boundary

A tensor product of the two walkers' bilinear point approximations preserves
each physical start, but on a coarse product grid it can assign positive mass
to pairs whose discrete separation is already inside the closed Doi contact
tube. That mass is a discretization artifact: the declared deterministic
starts are physically separated. Starting a killed chain from such a law can
change early flux, valley depth, and therefore the operational morphology
label.

All bounded centre-patterned 2D generators now use
`vkcore.encounter2d.contact_safe_initial_distribution_2d`. The original
bilinear product is returned byte-for-byte whenever it has zero contact mass.
Otherwise the constructor finds a joint grid law that is nonnegative, has unit
mass, preserves both two-component position means, and assigns zero mass to
the closed contact tube (and hence to its active catalytic subset). Physical
starts already in the closed contact region are rejected.

## Canonical hierarchical selector

On the smallest feasible expanding local stencil, the primary linear
programme minimizes the sum of the walkers' squared physical displacements.
The objective uses one common domain-length scale, so a rectangular domain
does not distort physical Euclidean distance. The primary optimum can be
degenerate. A second, strictly convex quadratic programme therefore selects,
on that optimal face, the unique law closest in Euclidean norm to the original
bilinear product. This removes dependence on an LP solver's arbitrary optimal
basis.

The constraints and objectives are nondimensionalized before solution.
Contact and physical-start tests use a length-scale-aware roundoff guard rather
than a fixed squared-distance tolerance. Infeasibility is reported only for
the optimizer's infeasible status; numerical failures fail closed as runtime
errors.

Every saved result includes total mass, minimum probability, support size,
both position means and errors, contact and active-sink mass, and RMS/maximum
support displacement for each walker and jointly.

## Independent validation

The adversarial audit covered state ordering, boundary and corner starts,
anisotropic rectangular domains, and physical rescalings from `1e-8` to
`1e12`. Independent global LP feasibility checks agreed with the local-stencil
implementation. The committed focused tests also exercise feasible and
infeasible starts, deterministic selection under degeneracy, invariant mass
and moments, exact product return when safe, and fail-closed numerical status
handling. The focused encounter-2D test suite has 17 passing tests, and Ruff
and byte compilation pass. No additional unpublished random-stress counts or
residual extrema are used as paper evidence.

## Scientific consequence

The correction is not merely cosmetic. With the contact-safe law:

- M2D-E retains two strict maxima on all five grids, but its `9x5` patterned
  endpoint is a classifier shoulder; the four finer patterned endpoints remain
  bimodal and all matched homogeneous endpoints remain classifier-resolved-unimodal.
- The midpoint and diffusion-weighted M2D-E coordinates now have the same
  three tested labels (`9x5` shoulder; `11x7` and `13x9` bimodal), although
  their masks and quantitative densities remain different.
- M2D-T retains five detected sign-changing derivative roots of alternating
  type and three strict,
  channel-attributed maxima on all four grids; the three finer grids are
  classifier-resolved trimodal and `9x5` is a shoulder.
- Families whose bilinear product was already contact-safe are returned
  unchanged and serve as exact-return controls.

These are corrections to declared finite-state certificates. They do not
promote any result to a continuum convergence theorem.

## Reproduction handles

- implementation: `packages/vkcore/src/vkcore/encounter2d.py`;
- focused tests: `tests/test_encounter_2d.py` and the 2D artifact tests;
- persisted diagnostics: each affected `finite_radius_2d*.json` file;
- generators: `code/validate_2d_finite_radius.py`,
  `validate_2d_mechanisms.py`, `validate_2d_centre_coordinate.py`,
  `validate_2d_matched_homogeneous.py`, `validate_2d_trimodal.py`, and
  `validate_2d_matched_fold.py`.
