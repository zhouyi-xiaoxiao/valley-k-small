# F0 batched scalar uniformization independent reaudit

Date: 2026-07-19  
Role: independent read-only numerical-method reviewer  
Decision: **ACCEPT METHOD LAYER / P0=0 / P1=0 / P2=3 / NOT AN F0 ACCEPTANCE**

## Exact reviewed bytes

| Object | SHA-256 |
| --- | --- |
| batched scalar implementation | `56b783f073528146e6cdd3321f078a89978b5e5453b8fdfcabfe35412614b280` |
| focused tests | `ddddb839f3b50c1dc2ca05fbce2ddad1b5e025d08f549665585b7a866159dac1` |

The focused suite returned `12/12 PASS`; the related packed, rate-action,
uniformization, and batch suites returned `148/148 PASS`; Ruff passed.

## Independent numerical checks

- 2,024 exact-`Fraction` signed-interval products covered negative, positive,
  zero-crossing, zero-factor, and near-two cases with zero misses.
- 5,000 exact-`Fraction` finite-difference checks covered orders zero through
  four with zero misses.
- Sixty independent 2,048-bit MPFR Poisson plans covered subnormal, near-one,
  near-two, random, boundary, and mean-8,428 cases.  The mode probability,
  backward recurrence, forward weights, and exact right tail were all
  contained.
- Eleven random or boundary dyadic two-state generators at five times were
  compared with an independent 1,024-bit closed-form matrix exponential.
  All 385 `J0`--`J3` and `M2`--`M4` checks were contained.
- At precision 128 with a near-two binary64 rate, the direct and canonical
  reevaluation paths agreed in all 32 checked endpoints.

The former P1 was closed.  The common finalizer now multiplies a signed
accumulator interval by the nonnegative rate-power interval with the endpoint
choice determined by sign.  Negative odd jets use the factor upper endpoint
for the lower bound; positive values use the factor lower endpoint.  Both
direct evaluation and reevaluation call this same implementation.

## Poisson, exact-type, and resource checks

- `mode >= maximum_terms` is rejected before MPFR planning.
- The recorded counts are exact: `p0_back=mode`,
  `right_plan=right_index-mode+1` for nonzero means, and
  `forward=right_index`.  Resource totals include both requested evaluations
  and the horizon plan.
- Invalid precision, a tail tolerance outside `(0,1)`, Boolean-as-integer
  substitutions, and non-exact `Fraction` or integer values fail closed.
- For capacity `C`, the measured explicit workspace is exactly `40C` integer
  bytes, `24C` float bytes, and `C` Boolean bytes.  The audited action path
  uses explicit `out=` buffers and introduced no untracked explicit NumPy
  array.
- Thirteen receipt, series, resource, or permission promotions were rejected.
  Generic results remain caller-unclassified with all control, science,
  resource, and F0 promotion fields false.

## Nonblocking P2 boundaries

1. `initial_mass_cap` is deliberately a declared precondition at this layer.
   It is not proved from the nominal initial law.  A closed F0 fixture must
   reconstruct the cap independently; it may not inherit the declaration.
2. Same-process hashes are content bindings, not an independent authority.
   A fresh exact-byte replay must reconstruct the persisted scalar records.
3. The inner receipt validator does not fully replay Poisson semantics after
   arbitrary rebinding.  In isolation it can accept a positive-mean
   `tail_upper=0` or a right index inconsistent with the saved series length.
   The F0 integration verifier must independently recompute every plan and
   enforce `right_index+4 <= maximum_power_index`.

These P2 items are explicit layer boundaries because this module never
authorizes a control, resource gate, F0 result, or scientific run.  The F0
candidate and independent replay must close them before acceptance.
