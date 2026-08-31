# Round 06 independent G1a re-audit

Date: 2026-07-13  
Scope: hardened `G1a_pre_fold_foundations` only.  This audit did not run the
207,025-state discovery calculation, fold continuation, mesh/box convergence,
or any PRR release action.  No source, manuscript, registry, or stored evidence
artifact was modified.

## Executive verdict

**G1a internal foundation: FAIL CLOSED / NEEDS ONE MORE HARDENING ROUND.**

The default implementation itself survives static inspection and every
requested reproduction check.  The stored 25-cubed payload regenerates
byte-for-byte, all 26 named gates are true, all 11 tests pass, Ruff passes, the
two Round-03 mutations now fail closed, the full installed-budget convention is
correct at both `W=1` and `W=2`, and the contact reference is genuinely
algorithmically separate from the production quadrature.

The advertised foundation PASS is nevertheless not yet discriminating.  Two
new physically material mutations retain `status: PASS` and all 26 gates:

1. translating every catalyst patch by two longitudinal cells while preserving
   every patch integral; and
2. making one endpoint control weight negative while preserving unit weight
   sum, both endpoint budgets, and positivity at the sole solved midpoint
   control.

The first defeats the claimed catalyst geometry; the second admits a negative
endpoint killing field.  Neither is a cosmetic test gap.  The default
25-cubed translated-patch mutation changes the maximum reaction-time density by
22.8 percent and final survival by 7.59 percent.  The negative-weight mutation
produces `min(kappa) = min(killing) = -0.2106302432` at `theta=0` while still
emitting PASS.

**Full G1 / scientific PRR: FAIL CLOSED.**  Independently of the two G1a
blockers, `continuum_verified` is correctly false and G1b discovery,
odd/even-plus-box convergence, the complete fold jet, G3 independent
validation, G4 transfer theorem, and G5 3D realization remain open.

There is no evidence in this round that the checked-in default operator is
mathematically wrong.  The failure is evidential: the current gate set cannot
yet certify the geometry and positivity advertised for G1a.

## 1. Requested reproduction matrix

All commands used the repository-owned `.venv`, disabled bytecode and pytest
cache writes, and directed the default smoke output to `/tmp`.

| Check | Result | Independent observation |
|---|---|---|
| Default 25 x 25 x 25 smoke | **PASS** | Exit 0; 26/26 gates true; regenerated SHA-256 `8162bf2a50ecb10af755084cf838b3e20c848f4e0d50c818b451ff03eeb6b11d`. |
| Stored-artifact linkage | **PASS** | The regenerated file and `artifacts/data/continuum_g1_smoke.json` have the same SHA-256 and an empty byte diff. |
| Continuum smoke tests | **PASS** | `11 passed`. |
| Ruff check | **PASS** | `All checks passed!`. |
| Ruff format check | **PASS** | `2 files already formatted`. |
| Round-03 translated-contact mutation | **PASS AS A NEGATIVE TEST** | Payload status is `FAIL`; failed gates are `contact_reference_per_cell`, `contact_reference_l1`, `contact_centroid`, and `contact_reflections`. |
| Round-03 cancelling-budget mutation | **PASS AS A NEGATIVE TEST** | Payload status is `FAIL`; failed gates are `patchwise_integrals`, `endpoint_physical_budgets`, and `budget_derivative_zero`; the cancelling midpoint budget intentionally remains true. |

The default saved diagnostics are internally consistent:

- schema version: `2`;
- stage: `G1a_pre_fold_foundations`;
- status: `PASS`;
- continuum verified: `false`;
- failed named gates: none; and
- claim scope explicitly excludes a continuum fold, mesh convergence, cusp,
  trimodality, and a PRR claim.

This schema separation is a real release-safety improvement.  Consumers must
still check `stage` and `continuum_verified`, rather than interpreting the
generic word PASS as a continuum result.

## 2. Full installed-budget convention at W=1 and W=2

I rebuilt the same 17 x 19 x 17 model at `theta=0.5` with only the transverse
width changed.  The implementation uses

```text
kappa = (B/W) sum_j w_j phi_j,
full installed amount = W integral kappa dz.
```

The independent observations were:

| Width | Full installed amount | Per-transverse integral | Endpoint full amounts | Full-budget derivative |
|---:|---:|---:|---:|---:|
| 1 | 0.6000000000000001 | 0.6000000000000001 | (0.6000000000000001, 0.6000000000000001) | 0 |
| 2 | 0.6000000000000001 | 0.30000000000000004 | (0.6000000000000001, 0.6000000000000001) | 0 |

The maximum individual patch-normalization error was
`4.440892098500626e-16` in both checks.  The full-installed-resource semantics
therefore pass for physical `d=2`; widening the transverse torus does not
silently double the installed material.

## 3. Contact reference independence

**Verdict: PASS at the G1a local-geometry level.**

The production path integrates vertical circle chords with split adaptive
QUADPACK.  The reference path independently integrates horizontal chords with
fixed order-128 Gauss--Legendre quadrature after the substitution
`y = a sin(angle)`.  `circle_rectangle_area_reference` does not call
`circle_rectangle_area` or `contact_cell_fractions`.

As a direct call-separation test, I replaced the production
`circle_rectangle_area` by a function that raises immediately.  The reference
routine still returned `0.03948982404970145` for an asymmetric rectangle.
The full translated-contact mutation also demonstrates separation: changing
only the production contact matrix leaves the reference fixed and trips four
independent gates.

On the stored 25-cubed case:

- maximum per-cell fraction difference: `2.886579864025407e-15`;
- relative L1 area difference: `1.3744717359777687e-15`;
- maximum centroid magnitude: `5.963540027744093e-17`; and
- maximum reflection discrepancy: `3.1086244689504383e-15`.

This is an independent local quadrature/reference implementation, not the
off-lattice or Robin/FEM validation required by G3.  The artifact and README do
not currently confuse those roles.

## 4. Initial-moment tolerance and its proper scope

**Verdict: PASS within the explicitly coarse G1a scope.**

The saved reconstructed errors and tolerances are:

| Coordinate | Error | Half-cell tolerance | Error/tolerance |
|---|---:|---:|---:|
| midpoint | -0.0120000000 | 0.0420000000 | 0.286 |
| relative parallel | +0.0442927112 | 0.0720000000 | 0.615 |
| wrapped relative perpendicular | 0 | 0.0200000000 | 0 |

For a cell-mass reconstruction, assigning mass within each cell to its centre
changes a linear first moment by at most half a cell width.  The tolerance is
therefore a registration/localization invariant, not evidence that the coarse
initial law is continuum accurate.  The JSON reports the nonzero errors, calls
the mesh deliberately too coarse, and the design requires convergence on the
later frozen odd/even sequence.  That scope is honest.

The wrapped-cut unit test also recovers a bump centred at `0.495` to roundoff,
and the saved circular resultant is effectively one.  No stronger continuum
claim should be attached to this gate.

## 5. Dense exponential and finite-difference time-jet gate

**Verdict: PASS for the stated time-generator foundation.**

The frozen asymmetric 4 x 5 x 6 reference gives:

| Check | Relative error |
|---|---:|
| sparse `expm_multiply` versus dense `expm` | `4.413687082037008e-15` |
| one full step versus two half steps | `5.634494147281299e-16` |
| analytic versus nine-point FD `f_t` | `1.4177838970740861e-12` |
| analytic versus nine-point FD `f_tt` | `2.724909542870826e-11` |
| analytic versus nine-point FD `f_ttt` | `1.7436844548511666e-08` |

The asymmetric six-neighbour tensor-order sentinel also passes.  This is a
genuine check of `p^T A^n k` orientation and sparse/dense semigroup action on a
small operator.  It is not a validation of theta sensitivities, a continuum
fold jet, or the main-grid reported jet ranges point by point.  Those stronger
objects correctly remain outside G1a and must be gated in G1b.

## 6. New P1 false positive: catalyst placement is not certified

The gate set verifies the integral of each normalized catalyst patch but never
verifies its declared centre, width, or per-cell profile.  I changed only the
three catalyst calls to `bump_cell_masses`, rolling each width-0.08 patch by two
longitudinal cells.  Initial-condition bumps were left unchanged.

On the full default 25-cubed smoke:

```text
status              PASS
failed gates        []
patch integrals     [1.0, 1.0000000000000002, 1.0000000000000004]
maximum density     0.0411323498 -> 0.0317567593  (-22.8%)
final survival      0.2672798862 -> 0.2469971833  (-7.59%)
```

The mutation preserves every resource identity but implements the wrong
physical slab locations.  This directly contradicts the README claim that the
exact operator geometry has passed.

Required repair:

1. persist and gate every patch's reconstructed zeroth and first moment against
   its declared unit integral and centre;
2. compare every patch cell average with an independently implemented local
   bump reference, using a maximum-cell and relative-L1 tolerance; and
3. add the translated-patch mutation as a fail-closed regression test.

The first moment alone catches this attack but not a symmetric wrong-width or
wrong-shape mutation; a local profile reference is needed for the advertised
geometry foundation.

## 7. New P1 false positive: endpoint positivity is not gated

Round 03 required endpoint weight normalization and nonnegativity.  Endpoint
budgets are now gated, but endpoint nonnegativity is not.  I replaced only the
lower endpoint weights by

```text
(-0.04, 0.34, 0.70)
```

Their sum remains one, and the solved midpoint weights remain positive:

```text
theta=0.5 weights = (0.005, 0.295, 0.70).
```

On the full default smoke the mutation gives:

```text
status                  PASS
failed gates            []
endpoint full budgets   (0.6000000000000002, 0.6000000000000002)
theta=0 min(kappa)       -0.21063024322253257
theta=0 min(killing)     -0.21063024322253257
```

Thus budget conservation and the midpoint positivity samples do not imply a
valid killed process along the frozen control line.

Required repair:

1. persist and gate endpoint weight sums and componentwise nonnegativity;
2. persist and gate minimum endpoint `kappa` and killing values; and
3. add a negative-but-unit-sum endpoint mutation test.

Because the control is affine, endpoint componentwise nonnegativity proves
weight nonnegativity for every `theta` in `[0,1]`.  Direct endpoint field
checks additionally protect the patch assembly.

## 8. P2 wording discrepancy

`round_03_resolution.md` says the individual patch quadrature error estimates
are both persisted and gated.  They are persisted (the current values are
approximately `1.33e-14`, `3.92e-14`, and `7.62e-14`) but no named gate uses
them; `patchwise_integrals` gates only the observed unit-integral discrepancies.
This is not evidence of a present numerical failure because the estimates are
tiny.  Either add an explicit finite/error-estimate gate or narrow the audit
wording.

Likewise, `26 mutation-hardened gates` is factually a count, not an exhaustive
certificate.  The stronger README/manuscript wording that G1a geometry and
positivity have passed must be downgraded until Sections 6 and 7 are closed.

## 9. Final decisions and next gate

### G1a internal foundation

**FAIL CLOSED.**  Retain the implementation as the development scaffold, but
do not treat the current JSON PASS as authorization to consume a costly G1b
run.  Add the patch-profile/placement and endpoint-positivity gates and their
two mutation tests, regenerate the artifact, and re-audit.

### Full G1 and PRR

**FAIL CLOSED / NOT YET ELIGIBLE.**  Even after the two G1a fixes, a PRR-level
continuum claim still requires the predeclared G1b fold discovery and full
odd/even, box, tail, observability, and fold-jet confirmation, followed by G3,
G4, and G5.  `continuum_verified: false` is correct and must remain false.
