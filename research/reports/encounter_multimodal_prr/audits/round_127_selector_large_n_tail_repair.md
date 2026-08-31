# Round 127: selector large-(N) certified binomial-tail repair

Date: 2026-07-14  
Decision: **PASS LARGE-(N) SPECIAL-FUNCTION REPAIR / NO POSITIVE-(B) AUTHORITY / NO F1**  
Findings after repair: **P0 = 0, P1 = 0, P2 = 0 within this bounded tail subproblem**

## Frozen repaired bytes

```text
code/f1_to_f2_common_observable_selector_v2.py
b6be1efa755659fac62143779690ae2cf67f06c8ea7c4eacfaf90db971862bc8

code/test_f1_to_f2_common_observable_selector_v2.py
f31b145525759f3ce59a4d29412e2021dcc4ee328c325e8f9e3d384f050fc2f0
```

No F0 file, prospective control, positive-budget generator, production state,
Monte Carlo sample, or F1 artifact was read or produced by this repair.

## Defect and repair

The prior certified binomial DAG initialized at (k=0) or (k=N) and
advanced to the requested boundary.  Its work was therefore (O(N)) for a
central tail, which made the production-scale Clopper--Pearson search
unusable.

The repaired DAG starts from the requested tail boundary.  For
(X\sim\operatorname{Bin}(N,p)), it encloses

\[
 \log \Pr(X=k)=
 \log\Gamma(N+1)-\log\Gamma(k+1)-\log\Gamma(N-k+1)
 +k\log p+(N-k)\log(1-p)
\]

with directed MPFR rounding.  All three gamma arguments are positive
integers supplied exactly; nonrepresentable integer inputs, nonfinite values,
reversed intervals, and MPFR underflow fail closed.  The (k=0,N) atoms use
directed integer powers and (p=0,1) use exact atoms.

For a lower tail the outward ratio is

\[
 r_k=\frac{\Pr(X=k-1)}{\Pr(X=k)}
 =\frac{k(1-p)}{(N-k+1)p};
\]

for an upper tail it is

\[
 s_k=\frac{\Pr(X=k+1)}{\Pr(X=k)}
 =\frac{(N-k)p}{(k+1)(1-p)}.
\]

Moving away from a mode makes the applicable ratio monotonically smaller.
Once its outward upper endpoint is below one, the uncomputed finite tail is
rigorously enclosed by

\[
 0\le R\le T_k\frac{r_k}{1-r_k}
 \quad\hbox{or}\quad
 0\le R\le T_k\frac{s_k}{1-s_k}.
\]

The recurrence stops only after that upper enclosure is at most
(2^{-P+16}) at precision (P).  Increasing the existing precision ladder
therefore tightens both MPFR roundoff and the explicit truncation remainder.
Ranges lying left or right of the mode are formed from one tail or a
difference of two same-side tails; mode-straddling ranges use the complement
of two outward tails.  Every subtraction is outward rounded and intersected
only with the exact probability range ([0,1]).

`NormalDist` remains solely a noncertifying search hint.  Every candidate and
the returned strict threshold are decided again by the MPFR enclosure.  No
SciPy, binary64 probability, normal approximation, or ordinary-double value
enters a certificate.

## Verification

From the report root:

```text
../../../.venv/bin/ruff format --check \
  code/f1_to_f2_common_observable_selector_v2.py \
  code/test_f1_to_f2_common_observable_selector_v2.py
2 files already formatted

../../../.venv/bin/ruff check \
  code/f1_to_f2_common_observable_selector_v2.py \
  code/test_f1_to_f2_common_observable_selector_v2.py
All checks passed!

../../../.venv/bin/python -m pytest -q -rP \
  code/test_f1_to_f2_common_observable_selector_v2.py
45 passed
```

The tests include:

1. exact rational containment for all 3,872 ranges with
   (1\le N\le16) and (p\in\{1/7,2/5,1/2,6/7\}), covering every tail/
   difference/complement route;
2. moderate-(N) exact-Fraction checks of both geometrically truncated tail
   orientations;
3. exact (p=0,1), (N=0), endpoint, strict-contact, and small-(N)
   Clopper--Pearson checks;
4. invalid type, probability, precision, reversed-bound, reversed-interval,
   and nonfinite mutations, all fail closed;
5. 256-to-512-bit enclosure nesting; and
6. a probability below binary64 range that remains positive and enclosed in
   MPFR.

The representative production-scale benchmark is part of the test suite:

```text
N = 8,000,000
lower boundary = 1/200
upper boundary = 3/200
alpha = 1/800
strict CP acceptance set = (40646, 118891)
elapsed = 0.759098 s
regression ceiling = 20 s
```

The 20-second assertion is deliberately broad; the observed time is recorded
for regression evidence rather than treated as a fragile microbenchmark.

## Boundary of this PASS

This round closes only the large-(N) binomial/Clopper--Pearson performance
and enclosure defect in the science-free common-observable selector.  It does
not independently accept the entire selector contract, an F0 attestation, a
positive-budget numerical row, a common-observable scientific result, or an
F1-to-F2 promotion.  Those gates remain separate.
