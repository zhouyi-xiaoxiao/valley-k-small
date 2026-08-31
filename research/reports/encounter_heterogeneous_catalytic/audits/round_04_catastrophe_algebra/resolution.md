# Round 04 resolution — catastrophe algebra and transversality

Date: 2026-07-11  
Status: **PASS; no open B0, B1, B2, or B3**

## Decision

The independent reviewers agree that the two-channel elimination, physical
fold Jacobians, cusp derivative order, and local normal-form constants are
correct.  The physical 1D and finite-grid 2D folds are nondegenerate under
their declared controls.  No cusp has been claimed as found, and neither a
fold nor a cusp is used by itself to infer trimodality.

## Closed findings

1. **Three-channel simplex overclaim.**  The normalized system containing
   `f_t=f_tt=0` now locates only a candidate double stationary point.  A fold
   additionally requires nonzero third time derivative and a transverse
   declared control.  An executable positive-weight, invertible-matrix
   counterexample with zero third-derivative jet prevents regression to the
   old sufficient-condition wording.
2. **Weight admissibility.**  The Lean claim map now calls the result an
   “algebraic weight formula and converse.”  Strict convex feasibility
   `0<w<1`, equivalent to opposite nonzero channel slopes in the two-channel
   case, remains an explicit physical gate rather than a Lean theorem.
3. **Normal-form constants.**  One- and two-dimensional continuations store
   and gate measured/predicted separation and prominence ratios, not only the
   `1/2` and `3/2` fitted exponents.  The smallest-step ratios are within about
   `0.2%` of the local predictions.
4. **Derivative naming.**  The mixed derivative JSON key is the unambiguous
   `f_tt_theta`; tests reject the former `f_tttheta` spelling.
5. **Trimodality logic.**  Five certified alternating simple roots, positive
   margins, and tail control establish existence of at least three resolved
   modes.  Interval-exhaustive isolation is required only for an exact global
   root or mode count; M2D-T explicitly withholds that stronger theorem.
6. **Formal and notation hygiene.**  Inline mathematics and the formal claim
   boundary were corrected.  The final independent Lean checks found 100
   theorems (`46+54`), four standard-axiom reports, and no proof placeholder.

## Revalidation

- Reviewer B: `19/19` focused tests passed.
- Two serial/warm Lean builds completed `3109/3109` jobs with exit code zero.
- Live encounter axiom drivers emitted `14/28/12` theorem rows, all within
  `propext`, `Classical.choice`, and `Quot.sound` and semantically equal to the
  saved reports.
- The manuscript and theory note distinguish existence of three modes from an
  exact global root count.

The round therefore closes without a remaining catastrophe-algebra or
transversality defect.
