# Round 20: continuum free-exposure exploration self-audit

## Verdict

**PASS as result-informed exploratory evidence; FAIL CLOSED for formal
continuum, finite-\(B\), or project-gate claims.**

This audit fixes the evidence boundary and reproducibility state before an
independent agent attack. It is not an independent scientific audit because
the calculation author performed it.

## Frozen files

| file | SHA-256 |
| --- | --- |
| scratch/continuum_free_exposure_exploration.py | 3eae6d3216f58d669554450e13b2720c6fed56de7d8b1dc8698f2b5b6e98f3a0 |
| scratch/continuum_free_exposure_exploration_result.json | 1b23fc6f91f002fb3f1396708c96e9e0056e4df66e0120928bd386da95e3c1f7 |

The result embeds the same producer hash. Its status is
RESULT_INFORMED_EXPLORATION_NOT_FORMAL_EVIDENCE and all four claim flags
(preregistered discovery, continuum verified, finite-\(B\) Doi verified, and
project gate passed) are false.

## Checks performed

1. A clean full execution completed in 107 seconds and regenerated the JSON.
2. Ruff lint and format checks pass.
3. JSON serialization uses allow_nan=false; a full parse succeeds.
4. Compact initial and patch probability quadratures sum to
   \(1+2.7\times10^{-15}\).
5. The half-chord/Fourier disk-contact formula agrees with an independently
   parameterized polar disk quadrature at \(t=1,5,9,20\); maximum relative
   difference \(1.63\times10^{-14}\).
6. Direct product Cauchy jets and factorwise Leibniz jets agree at order
   \(10^{-13}\).
7. Coarse/primary/fine continuum quadratures move each cusp time by at most
   \(4.6\times10^{-10}\) and its weights by at most \(2.2\times10^{-11}\).
8. The 65-grid current-geometry cusp reproduces the pinned weak-budget result
   to displayed precision.
9. Four exploratory finite-volume meshes show the cusp coordinates trending
   toward the direct kernel values, while also exposing nonmonotone
   interface-alignment effects.
10. Free-law mass outside the old finite box is below \(3.79\times10^{-9}\)
    for the midpoint and \(2.26\times10^{-9}\) for the relative-parallel
    coordinate over the screened interval. This is explicitly labeled a
    zero-order tail diagnostic, not a mixed-jet boundary theorem.

## Adversarial interpretation checks

- The current centres have a direct continuum cusp but the selected branch
  contains only two maxima. They do not support a trimodality claim.
- The redesigned centres have a direct continuum five-root branch, but these
  centres and the approximate structure were known before the script was
  frozen.
- The same absolute catalyst weights are not stable between the 65-grid and
  the direct continuum because the cusp shift exceeds the thinnest wedge.
- The valid object to refine is the cusp plus both neighboring fold sheets,
  not one selected control.
- No positive installed budget, killed-Doi persistence radius, interval
  certificate, independent continuum implementation, or physical-\(d=3\)
  calculation is supplied here.

## Severity ledger

| severity | count | disposition |
| --- | ---: | --- |
| P0 | 0 | no false formal claim remains |
| P1 | 0 | formula and evidence labels are internally consistent |
| P2 | 0 | reproducibility and provenance checks pass |
| open scientific gates | 5 | prospective freeze; certified error; fold-sheet convergence; positive-\(B\) transfer; independent solver / \(d=3\) |

The independent kernel audit should recompute the OU variance conventions,
wrapped-Brownian Fourier normalization, disk Jacobian, Cauchy jet signs,
positive null weights, and five-root topology from the frozen files above.
