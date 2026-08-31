# Round 05 resolution — roots, conditioning, tails, and convergence

Date: 2026-07-11  
Status: **PASS; no open B0, B1, or B2 scientific finding**

## Decision

Both reviewers independently recovered the reported GIG, finite-CTMC, 2D-fold,
and four-grid trimodal roots.  Reviewer B additionally proved with an exact
rational Sturm chain that the canonical fixed-shape GIG determinant has exactly
two positive roots.  The finite-grid roots, local exponents, capacity fits, and
tail values are reproducible.  The accepted claim remains deliberately bounded:
finite sign-change scans certify the displayed simple roots, not exhaustive
positive-time root counts, and the 3D shrinking-radius result is a coupled
radius/grid path rather than a separated double limit.

## Remediation ledger

1. **Strict versus resolved morphology (B2, closed).**  All five homogeneous
   M2D-E controls retain their small strict second maxima.  The paper and data
   distinguish those roots from the declared 3% resolved-mode threshold.
2. **Finite-scan completeness language (B2, closed).**  Manuscript, notes, and
   validators say “detected sign-changing roots” and explicitly exclude an
   interval-exhaustive or global-root-count interpretation.
3. **3D double-limit wording (B2, closed by downgrade).**  The 0.114% coefficient
   agreement is reported as continuum-compatible finite-grid evidence along
   `a/h≈7.4--7.65`, not as a certified continuum coefficient.
4. **Underflow pseudo-root guard (B3, implemented).**  The physical CTMC fold
   now requires admissible time/control coordinates, positive non-underflow
   density, dimensionless residuals below `1e-8`, and nonzero dimensionless
   third derivative and transversality before a nonlinear-solver result is
   accepted.
5. **Optional numerical archive hardening (B3, retained).**  Persisting every
   scaled Jacobian condition number, additional fit-window rows, and a fully
   interval-certified tail would improve diagnostics but is not required by any
   promoted existence or convergence claim.

## Revalidation

Reviewer A's focused recheck passed all 57 selected tests.  Reviewer B's
independent ten-file suite passed 43 tests and reproduced the two 2D fold
condition numbers, all four five-root trimodal patterns, and both capacity
fits.  The final unified profile will regenerate the guarded physical fold and
hash its source, data, figure, and log after the audit files freeze.
