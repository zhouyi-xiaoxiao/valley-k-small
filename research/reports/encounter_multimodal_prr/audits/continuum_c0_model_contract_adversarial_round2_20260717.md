# Continuum C0 model-contract candidate: adversarial verifier round 2

Date: 2026-07-17

Status: **FAIL-CLOSED VERIFIER PASS / 12 ADVERSARIAL TESTS PASS / HOLD INDEPENDENT REVIEW / COMPLETE C0 NOT YET ACCEPTED**

## Exact reviewed candidate

- contract candidate SHA-256:
  `5bbe7d3c265736f98f0025a8aad80d83a53e464a5349d6b6be57a096ba9cdf66`;
- verifier SHA-256:
  `14983779200b19081ff1219524e3a9db9261319fa8a7a1a43ffcb51dec03baea`;
- adversarial tests SHA-256:
  `213adc5f2092b51a54c29761280ed37df5bd5b0a70a463fba6e0df02259241b6`.

This is an implementation-side attack round.  It does not count as an
independent C0 review.

## Verifier boundary

`code/validate_continuum_c0_model_contract_candidate.py` accepts arbitrary
candidate bytes and fails closed with a stable HOLD code.  It does not accept
the candidate merely by comparing its whole-file digest.  It separately
checks:

- strict UTF-8 JSON, a final newline, no duplicate keys and no nonfinite JSON
  numbers;
- the complete schema/key set and every nonpromotion flag;
- each exact binary64 word against its exact rational and physical unit;
- continuum object, boundary conditions, equation inventory and
  identification maps;
- frozen source roles, paths, hashes and selected source semantics;
- the opaque exact-control source hash and order;
- initial mass/dimension/scope;
- sharp-contact/support geometry and `2a<W`;
- all 12 configurations, four alignment classes and the declared box nesting;
- absence of result-bearing tokens.

The emitted PASS receipt remains narrow:
`PASS_C0_CONTRACT_CANDIDATE_SEMANTIC_VERIFICATION_ONLY`, with
`positive_budget_scientific_values_read=false` and `release_eligible=false`.

## Attacks reproduced

The 12-test attack file verifies the valid candidate and rejects:

1. duplicate JSON keys;
2. nonfinite JSON numbers;
3. decimal `1/100` substituted for the frozen dyadic budget;
4. budget/diffusion unit swaps;
5. initial-source/killing-source role swaps;
6. reflecting-boundary promotion of the natural-decay target;
7. removal of the `W^{-1}` factor;
8. replacement of sharp contact by a non-sharp declaration;
9. configuration-order and alignment-role swaps;
10. unweighted `P_h` and unit stationary-mass gauge substitutions;
11. equation omission and complete-C0 claim promotion; and
12. opaque-control hash/order mutation and injection of a result-bearing key.

All 12 tests pass.

## Verifier defect found and repaired

The first run rejected the valid candidate because it compared the source
string `"1/1"` to Python's canonical string for `Fraction(1,1)`, namely
`"1"`.  This was a verifier P1: formatting was being mistaken for mathematical
inequality.  The repaired verifier parses the source strings as exact
rationals and compares rational values.  The candidate bytes were not changed.

## Remaining independent obligations

This round still does not independently establish that the chosen `J_h/P_h`
maps satisfy the C1 norm/adjoint axioms, that the stationary gauge is enclosed
for every box, or that the opaque selector path is the best editorial form of
a complete mathematical definition.  Those are theory-review questions, not
schema tests.  Complete C0, C1--C3, root transfer, F0 and release remain HOLD.

