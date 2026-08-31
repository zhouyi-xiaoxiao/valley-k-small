# Round 120: targeted P2 closure for the exact-\(m\) theorem v2

Date: 2026-07-14  
Scope: only the three exact Round-118 P2 repairs  
Decision: **ACCEPT-THEOREM-SPINE**  
Open findings in this targeted closure: **P0 = 0, P1 = 0, P2 = 0**  
Positive-budget science: **NOT RUN / NOT AUTHORIZED BY THIS CLOSURE**

## 1. Frozen bytes and non-expansion boundary

The repaired theorem note has the expected SHA-256:

```text
notes/exact_m_mode_encounter_theorem_v2.md
e78a0d77959d50214d56ef4708a20ac465232883fbbdd4ee42fe488c0b95c85d
```

The independent attack being closed is

```text
audits/round_118_exact_m_theorem_v2_independent_attack.md
d78c0364c6c63e3b9d360fd104d1b52ca59795deb7b39e64d04c7cf707ff5a06
```

This was a targeted textual, symbolic, and regression closure.  I did not
re-open the theorem's scope, add a new claim, construct a killed generator,
or evaluate any positive reaction budget.

## 2. P2.1 control-byte and covariance repair: CLOSED

The former ASCII `0x0B` at old byte offset 3733 is absent.  Equation (2.4)
now reads

\[
 R_{\perp,0}\sim
 \text{wrapped }N(r_{\perp,0},\varepsilon^2\Sigma_{\perp,0}),
\]

with an ordinary backslash before `varepsilon`.  A full forbidden-control-byte
scan over the repaired note returned PASS; it checked
`0x00--0x08`, `0x0B`, `0x0C`, `0x0E--0x1F`, and `0x7F`.

Disposition: **CLOSED EXACTLY AS REQUESTED**.

## 3. P2.2 unit-budget free-exposure semantics: CLOSED

The note now defines

\[
 K_{B,w,\varepsilon}=B V_{w,\varepsilon}
\]

and explicitly identifies

\[
 \begin{aligned}
 G_{\varepsilon,w}(t)
 &=B^{-1}\mathbb E[K_{B,w,\varepsilon}(Z_t,R_t)]\\
 &=\langle V_{w,\varepsilon},T_0(t)q_0\rangle\\
 &=\frac{c_{d,\varepsilon}(t)}
 {W^{d-1}\sqrt{2\pi}\,\varepsilon S_*}
 H_{\sigma,w}(x(t)).
 \end{aligned}
\]

The surrounding text calls this the **exact unit-budget free-exposure
clock** and declares \(T_0(t)\) to be the unkilled semigroup and \(q_0\) the
initial law.  The symbols are therefore closed locally: \(V\) is the
budget-independent killing profile, the expectation is under free dynamics,
and the pairing is the same free observable used in the weak-budget bridge.

For \(B>0\), the first equality is literal.  The \(B\)-independent right-hand
side is the continuous \(B=0\) extension used later by
\(f_{B,\varepsilon,w}/B\to G_{\varepsilon,w}\).  No probability-normalization
claim has been introduced.

Disposition: **CLOSED EXACTLY AS REQUESTED**.

## 4. P2.3 posterior-convex-hull outer tails: CLOSED

Lemma 4.1 no longer extends the local peak expansion (3.15) to the full
outer tails.  It now uses the global posterior convex-hull fact

\[
 \bar c(x)\in[c_1,c_m]
\]

and therefore derives directly

\[
 x\le c_1-A_{\rm p}\sigma^2\Rightarrow L(x)\ge A_{\rm p},
 \qquad
 x\ge c_m+A_{\rm p}\sigma^2\Rightarrow L(x)\le-A_{\rm p}.
\]

This proves the complete two-tail sign margin uniformly and leaves (3.15)
restricted to the peak neighbourhood where it was established.

The added display is intentionally unnumbered.  The subsequent equation tags
remain unique and consecutive:

```text
(4.9), (4.10), (4.11), (4.12), (4.13), (4.14),
(4.15), (4.16), (4.17), (4.18), (4.19), (4.20),
(4.21), (4.22), (4.23), (4.24)
```

References to (4.9), (4.12)--(4.14), (4.15)--(4.24), (4.17), and (4.18)
still resolve to their original logistic, sector, slow-factor, and shift
equations.  The note-wide duplicate-tag scan returned no duplicate.

Disposition: **CLOSED EXACTLY AS REQUESTED**.

## 5. Reproduction record

The targeted commands were equivalent to

```text
shasum -a 256 notes/exact_m_mode_encounter_theorem_v2.md

LC_ALL=C perl -ne \
  'print "$.:$_" if /[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/' \
  notes/exact_m_mode_encounter_theorem_v2.md

rg -o '\\tag\{[^}]+\}' notes/exact_m_mode_encounter_theorem_v2.md \
  | sort | uniq -d

../../../.venv/bin/python -m pytest -q \
  code/test_exact_m_zero_budget_slow_factor_stress.py \
  code/test_exact_m_zero_budget_round118_adversarial.py

../../../.venv/bin/ruff check \
  code/exact_m_zero_budget_slow_factor_stress.py \
  code/test_exact_m_zero_budget_slow_factor_stress.py \
  code/test_exact_m_zero_budget_round118_adversarial.py
```

Results:

```text
theorem SHA-256       = e78a0d77959d50214d56ef4708a20ac465232883fbbdd4ee42fe488c0b95c85d
control-char scan     = PASS
duplicate-tag scan    = PASS
pytest                = 12 passed
Ruff                  = All checks passed!
positive B evaluated  = False
```

## 6. Final disposition

All three Round-118 P2 findings are closed without changing the audited
mathematical scope.  The repaired theorem may now serve as the accepted
analytical spine under its declared fixed-finite and sequential
\(\varepsilon\)-then-\(B\) quantifiers.

```text
0x0B / epsilon repair                  = PASS
unit-budget G definition               = PASS
posterior-convex-hull outer tails      = PASS
equation tags and references           = PASS
zero-budget theorem stress regression  = PASS
theorem-spine acceptance               = ACCEPT
positive-budget science authorization  = NO
PRR finite-parameter evidence gate     = STILL EXTERNAL
```

Decision: **ACCEPT-THEOREM-SPINE**.
