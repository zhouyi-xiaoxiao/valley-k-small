# Advisor reply readiness check

This file records the minimum standard for a suitable reply to Luca's
2026-06-06 updated-version email, and the current evidence for each item.

## Required questions to answer

1. Is the updated TeX/PDF all correct now?
2. If not, where is the first hard remaining issue?
3. Why do the numerical checks support that diagnosis?
4. For `N=100`, `q=2/3`, what beta range shows finite-time double peaks?
5. Does the proposed `s_1 = 1-q+q cos(2 pi/N)` transition criterion hold?

## Current answers

- The updated version is not all correct yet.
- The first hard shortcut issue is Eq. (32): the numerator correction has the
  corrected plus direction, but the denominator still has the old minus sign.
- Eq. (33) then inherits the inconsistency: with the plus-denominator definition
  of `H`, the shortcut term should have a plus prefactor, not a minus prefactor.
- Eq. (40), Eq. (41), and the final tail paragraph are downstream of this
  unresolved first-passage sign propagation.
- For `N=100`, `q=2/3`, the finite-time scan reports clear double peaks up to
  about `beta = 0.03` for `n0 = 1,2,3`, and no clear double peak at
  `beta = 0.04` under the visual criterion used in the note.
- In the corrected pole equation, the finite crossing
  `s_1 = gamma_1 = 1-q+q cos(2 pi/N)` does not occur for finite positive beta;
  the corrected relation is `gamma_1 < s_1 < alpha_1`.

## Evidence checked

- Latest Outlook request checked:
  `Re: Minimal sign issue in the shortcut-to-absorbing-site calculation`,
  received `2026-06-06T09:17:17Z`, with updated `Calculations.tex` and
  `Calculations.pdf` attachments.
- Updated source inspected:
  `source/20260606_luca_updated/Calculations.tex`, lines 398, 403, 408, and
  413.
- Re-run pre-shortcut checker:
  `python3 scripts/pre_shortcut_formula_checks.py --csv pre_shortcut_formula_check_results.csv --md pre_shortcut_formula_check_report.md`.
- Re-run shortcut sign checker:
  `python3 scripts/quick_sign_test.py --csv quick_sign_test_results.csv --md quick_sign_test_report.md`.
- The key shortcut check remains:
  corrected plus/plus Eq. (32) vs finite stochastic matrix, max error
  `2.775558e-16`; updated/original Eq. (32) sign vs finite stochastic matrix,
  max error `3.669746e-01`.
- The hard-route packet reports:
  corrected plus/plus first-passage formula error `2.08e-17`, updated Eq. (32)
  denominator-sign error `3.29e-3`, updated Eq. (33) minus-prefactor error
  `6.34e-2`, and corrected hard-route / closed-form errors at roundoff.

## Send-ready files

- `draft_reply_updated_calculation_remaining_issues.txt`
- `updated_calculation_remaining_issues_audit.pdf`
- `luca_updated_hard_route_delivery_packet.pdf`

Status: ready for user review; not sent.
