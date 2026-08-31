# Round 106b: closure of the two theory-text repairs

Date: 2026-07-14  
Decision: **PASS TEXT REPAIRS / POSITIVE-B HOLD UNCHANGED**  
New findings in this closure scope: **P0 = 0, P1 = 0, P2 = 0**

## Reviewed bytes and boundary

This addendum reviewed but did not edit
`notes/modal_certificate_theory_and_prr_redirect.md`, SHA-256

```text
38dde114552d0cea69f714d7493d3cb6715e1b4ed436431045a50a57360326be
```

No positive-budget calculation, allocation grid, killed generator, or Monte
Carlo process was run.  The only workspace write is this addendum.

## Closure result

### 1. Discrete topology signature: PASS

Theorem 5.1 now defines

```text
Sigma_B(w) = (N(w); sign F_tt(t_1(w),w), ..., sign F_tt(t_N(w),w))
```

for allocations outside the interior discriminant and endpoint-crossing set.
Every listed curvature sign is nonzero there.  The text explicitly excludes
the numerical root times from the signature and allows those times to move
continuously.  The proof now says the root family moves continuously while
only `Sigma_B` is locally constant.  Corollary 5.2 assumes
`Sigma_B(w_0) != Sigma_B(w_1)`, so the former counterexample consisting only
of shifted root locations no longer satisfies its hypothesis.  The
corollary's discriminant-or-boundary conclusion is therefore literal and
correct.

### 2. Fold regularity: PASS

The fold paragraph now adds local joint `C^3` regularity in time and the scalar
allocation coordinate along the allowed tangent `h`, with an equivalent
derivative-level option.  This supplies `F_ttt`, `D_h F_t`, and the mixed
derivative needed to define the Jacobian of `(F_t,F_tt)`.  At `F_tt=0`, its
determinant remains

```text
-D_h F_t * F_ttt,
```

so the two stated nonzero conditions give full rank and the standard
transverse fold condition.  The previous regularity gap is closed.

## Ledger

```text
Round-106 P1.1 topology terminology     = CLOSED
Round-106 P1.2 fold regularity           = CLOSED
new P0                                   = 0
new P1                                   = 0
new P2                                   = 0
target-note text-repair decision         = PASS
positive-budget execution                = NOT AUTHORIZED
```

The cumulative project release gate is unchanged: the separate formal
selector and full-window outward-rounded interval-certificate artefact from
Round-106 P1.3 still has to be built and independently audited.  This addendum
closes the two note-text defects only; it does not promote the exploratory
`B=0` result or authorize positive-budget work.
