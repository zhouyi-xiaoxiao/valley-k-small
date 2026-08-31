# Round 126: independent attack on the reader-facing exact-\(m\) spine

Date: 2026-07-14  
Role: independent theorem-equivalence, manuscript-claim, compile, and visual
attacker  
Mathematical-core decision: **ACCEPT THE READER SPINE AS A FAITHFUL SUMMARY OF
THE ACCEPTED EXACT-\(m\) CORE**  
Current reader-byte decision: **HOLD FOR TWO P1 CLAIM-CLOSURE REPAIRS**  
Findings: **P0 = 0, P1 = 2, P2 = 3**  
Positive-budget science: **NOT RUN / NOT AUTHORIZED / NOT CLAIMED AS
VALIDATED BY THIS AUDIT**

## 1. Frozen inputs and independence boundary

I treated the reader fragment as untrusted and checked it directly against the
full theorem and the independent theorem audit/closure.  The input bytes were

```text
manuscript/exact_m_theorem_spine.tex
f29b0df2a0ff079d117a82f07311dfb63e2c254681e07fa6a2fe1fab8b4e920d

manuscript/exact_m_theorem_spine_harness.tex
ebf18006252e5d16b384ecf117174774fb29a66f580e49565d4e32c489a07641

notes/exact_m_mode_encounter_theorem_v2.md
e78a0d77959d50214d56ef4708a20ac465232883fbbdd4ee42fe488c0b95c85d

audits/round_118_exact_m_theorem_v2_independent_attack.md
d78c0364c6c63e3b9d360fd104d1b52ca59795deb7b39e64d04c7cf707ff5a06

audits/round_120_exact_m_theorem_v2_p2_closure.md
dfc0381ddbc87a7c338978f80f5a9c9219536409b06905a03f5cdcd2fafbb10e
```

I did not edit either TeX source.  I did not inspect or evaluate a positive
budget, construct a killed generator, run a finite-volume science row, or run
Monte Carlo.  The only repository write from this attack is this audit.

## 2. Executive verdict

The reader fragment preserves every essential mathematical conclusion and
every important limitation of the accepted theorem:

1. fixed finite \(d\ge2\) and fixed finite \(m\ge1\);
2. a compact positive time window and target times strictly inside it;
3. a compact simplex-interior weight family with conserved installed budget;
4. a common-variance Gaussian mixture with the correct dimensionless width;
5. the weighted, rather than unweighted, adjacent crossover;
6. exactly \(m\) maxima and \(m-1\) minima, with complete zero exhaustion;
7. slow-factor peak shifts of \(O(\sigma^2)\) and valley shifts of
   \(O(\sigma^4)\);
8. first small \(\varepsilon\), then existential
   \(0<B<B_0(\varepsilon)\); and
9. no useful \(B_0\), event-mass floor, growing-\(m\), growing-\(d\), or
   outside-window conclusion.

I found no altered sign, missing factor, incorrect asymptotic scale, reversed
quantifier, or new mathematical overclaim inside that analytical chain.

The current bytes are nevertheless not ready to paste into a PRR manuscript.
The theorem statement does not locally pin several hypotheses needed for the
Doi transfer, and the closing sentence asserts that a finite-parameter
two-dimensional calculation already addresses the three external gates even
though no such positive-budget result was authorized or validated here.  The
first is a theorem-statement closure defect; the second is an evidence-boundary
defect.  Both are P1 and require textual repair before integration.

## 3. Independent mathematical equivalence check

### 3.1 Orientation, variance, and mixture scale: PASS

The fragment uses

\[
 x(t)=\operatorname{sgn}(\mu')\mu(t)/\ell_0
\]

and explicitly requires \(x'\) to be bounded away from zero.  This is the same
joint trajectory/centre orientation used in the accepted theorem.  The stated
OU midpoint variance and physical slab width give

\[
 \sigma=\frac{\varepsilon}{\ell_0}
 \sqrt{\frac{D_0}{2\gamma}+\rho^2},
\]

which matches Eq. (2.8) of the full theorem.  No dimensional logarithm has
been reintroduced.

### 3.2 Log-slope identities and weighted crossover: PASS

For

\[
 H_{\sigma,\bm w}(x)
 =\sum_jw_j\exp[-(x-c_j)^2/(2\sigma^2)],
\]

the fragment gives exactly

\[
 L=(\bar c-x)/\sigma^2,
 \qquad
 L'=\operatorname{Var}_{\pi}(c)/\sigma^4-1/\sigma^2.
\]

Its crossover

\[
 s_j=\frac{c_j+c_{j+1}}2
 +\frac{\sigma^2}{c_{j+1}-c_j}\log\frac{w_j}{w_{j+1}}
\]

is the accepted weighted equality point.  Direct subtraction of exponents
again gives adjacent odds \(1/9\) and \(9\) at the displayed
\(O(\sigma^2)\) edges.  The resulting pure valley formula

\[
 r_j=s_j+O(\sigma^4),\qquad
 L'(r_j)=\frac{(c_{j+1}-c_j)^2}{4\sigma^4}
 +O(\sigma^{-2})
\]

is unchanged.

### 3.3 Peak construction and zero exhaustion: PASS

The peak location and curvature scales agree with the full theorem:

\[
 p_j=c_j+O(e^{-q/\sigma^2}),
 \qquad L'(p_j)=-\sigma^{-2}+o(\sigma^{-2}).
\]

The fragment then invokes the same extended-Chebyshev representation

\[
 e^{x^2/(2\sigma^2)}H'(x)
 \propto\sum_{j=1}^m(a_j+b_jx)e^{\lambda_jx},
 \qquad\lambda_1<\cdots<\lambda_m,
\]

and the same generalized-Rolle \(2m-1\) multiplicity bound.  The already
constructed \(m+(m-1)\) simple roots therefore exhaust the real zero budget.
The reader text does not accidentally turn this into a growing-\(m\) result.

### 3.4 Slow-factor topology: PASS

The fragment retains the decisive repair rather than reverting to false
single-component dominance at a crossover edge.  It identifies

- peak boxes of width \(O(\sigma^2)\);
- valley boxes of width \(O(\sigma^4)\);
- uniform first and second logarithmic derivative bounds for the positive
  contact factor; and
- a full complement sign certificate.

Those ingredients are exactly what is needed to make the logarithmic
derivative strictly decreasing in every peak box, strictly increasing in
every valley box, and nonzero on the complement.  The declared peak and
valley displacement scales are therefore faithful to Theorem 4.2 of the full
note.

### 3.5 Weak-budget Doi transfer and quantifier order: PASS

The displayed convergence

\[
 \sup_{\bm w\in\mathcal W_{w_*}}
 \left\|f_{B,\varepsilon,\bm w}/B-G_{\varepsilon,\bm w}
 \right\|_{C^2(I)}\to0
 \quad(B\downarrow0)
\]

has the correct norm, allocation uniformity, and fixed-positive-
\(\varepsilon\) meaning.  The prose correctly uses it to preserve root tubes,
curvature signs, complement margins, and endpoint slopes.  It explicitly
keeps the sequential order

```text
fix finite d, m and all data
choose sufficiently small positive epsilon
then choose 0 < B < B_0(epsilon)
```

and explicitly withholds a useful lower bound for \(B_0\), an event-mass
floor, uniformity in \(d\) or \(m\), and an outside-window count.

### 3.6 Encounter-significance ceiling: PASS, except P1.2 below

The fragment states that the whole-window contact-interior condition becomes
asymptotically saturated contact.  It therefore does not recast the analytical
construction as a dimension-driven or approach/separation mechanism.  This is
consistent with Sections 6--7 of the full theorem.  The only violation is the
unsupported final present-tense numerical sentence isolated as P1.2.

## 4. Open findings

### P1.1 — The reader theorem does not pin the Doi-transfer hypotheses or its observables

Lines 14--42 give a useful verbal model sketch, but “the data above” in the
theorem statement does not include several hypotheses that Theorem 5.1 of the
accepted note actually needs:

- the transverse period \(W>0\), contact radius \(0<a<W/2\), and
  minimum-image convention;
- the relative initial law and the weighted-space conditions
  \(u_0>0\), \(u_0^2<4D_0/\gamma\), and
  \(\Sigma_{\perp,0}\succ0\);
- the full independence/covariance specification; and
- a local definition of the killing field, unit-budget exposure
  \(G_{\varepsilon,\bm w}\), and physical density
  \(f_{B,\varepsilon,\bm w}\).

These are not cosmetic assumptions: the covariance inequalities and bounded
fixed-\(\varepsilon\) catalyst are what make the invoked mixed-jet theorem
applicable.  In the standalone harness, a reader cannot reconstruct the
domain of Theorem 1 or distinguish “unit-budget exposure” from evaluation at
\(B=1\).

Required repair: before the theorem, either give the compact model equations
and hypothesis list, including

\[
 K_{B,\bm w,\varepsilon}=B V_{\bm w,\varepsilon},
 \qquad
 G_{\varepsilon,\bm w}
 =B^{-1}\mathbb E_0[K_{B,\bm w,\varepsilon}]
 =\langle V_{\bm w,\varepsilon},T_0q_0\rangle,
\]

or point to exact preceding model equations and an appendix proposition that
contains every listed condition.  “The data above” alone is not sufficient.

Disposition: **P1 / HOLD READER BYTES**.  This does not reopen the accepted
mathematics; it closes the manuscript theorem's declared domain.

### P1.2 — The final sentence asserts finite-parameter evidence that is not yet validated

Lines 152--154 say:

> The finite-parameter two-dimensional calculation below addresses
> nontrivial contact, physical observability, and robustness separately.

That is a present-tense scientific claim.  It conflicts with the fragment's
own header (“no finite-parameter numerical claim”), with the Round-118/120
boundary, and with this audit's explicit prohibition on positive-\(B\)
science.  A planned calculation is not evidence that the three gates are
already addressed.

Required repair now: replace the sentence by a gate statement, for example:

> Nontrivial contact, observability at a common positive budget, and
> finite-parameter robustness remain separate numerical validation gates.

The present-tense “addresses” wording may be restored only after the fixed
geometry/common-budget deterministic certificate and independent
survival/event-mass validation both pass and are actually present below.

Disposition: **P1 / HOLD READER BYTES AND PRR CLAIM PROMOTION**.

### P2.1 — Nonemptiness of the allocation family is only implicit

Equation (2) writes \(w_j\ge w_*>0\) but does not state that
\(\mathcal W_{w_*}\) is nonempty.  The full theorem explicitly assumes a
nonempty compact simplex-interior set.  Add “nonempty” or pin
\(0<w_*\le1/m\).  This prevents a vacuous uniform-allocation theorem.

### P2.2 — The zero-count sketch omits the finiteness-at-infinity step repaired in v2

Lines 121--123 mention only the twice-differentiated Rolle induction.  The v2
proof first establishes that the real zero set is finite by dominance of the
extreme affine-exponential terms in the two tails.  That step was a named
repair in Round 118.  Add one sentence stating tail domination/real-analytic
finiteness before invoking generalized Rolle, or point to the complete
appendix lemma.  The source theorem is sound; the current main-text proof
sketch is merely too compressed at precisely a previously audited seam.

### P2.3 — “The two posterior odds” should identify the adjacent ratio and orientation

Lines 94--98 should say explicitly

\[
 q_{j+1}/q_j=1/9
 \quad\text{at}\quad
 s_j-\sigma^2\log9/(c_{j+1}-c_j),
\]

and \(q_{j+1}/q_j=9\) at the plus edge.  “The two posterior odds” is
understandable, but it can be misread as full-posterior masses or as two
different odds definitions.  The exact adjacent ratio is the critical
Round-112 repair and should be named without ambiguity.

## 5. Compile, regression, and visual evidence

### 5.1 Clean independent build

The harness was compiled in a fresh temporary output directory with TeX Live
2025 through the bundled compile workflow.  The effective command was

```text
/Library/TeX/texbin/latexmk -norc -pdf -interaction=nonstopmode
  -halt-on-error -synctex=1
  -outdir=/private/tmp/round126-reader-spine.PhXRxy
  manuscript/exact_m_theorem_spine_harness.tex
```

Result:

```text
exit code                    = 0
pages                        = 2
page size                    = 612 x 792 pt (US Letter)
PDF bytes                    = 247265
undefined references         = 0
multiply defined labels      = 0
LaTeX/package errors         = 0
overfull boxes               = 0
underfull boxes              = 0
missing glyphs               = 0
nameref compatibility warning= 1
```

The lone `nameref` warning reports that RevTeX changed `\label` and `nameref`
restored the kernel definition.  It did not produce an unresolved reference,
duplicate destination, or visible defect.  It is not counted as a finding.

Fresh build hash:

```text
/private/tmp/round126-reader-spine.PhXRxy/exact_m_theorem_spine_harness.pdf
b0bc82f3adc1fd3695990c78270c837d9535cb8d0b7c5de030499c1e690265ba
```

The repository's earlier harness PDF is

```text
manuscript/exact_m_theorem_spine_harness.pdf
86428cf18eb9a84e831588cefae2ff7c9782ea3675b0f105cb156eab6673f582
```

The PDF byte hashes differ only because the generated PDFs carry different
creation/modification timestamps.  Pixel rendering at 180 dpi was
byte-identical for both pages:

```text
page 1 PNG
97a6abb492e6fd72404830d8e59f0fd63c34b0dbde36700653b61f05b0c7e0ac

page 2 PNG
912a368e77c6844b406e093c8afafa242d0f8c857ad4d55c4357a93003c993cc
```

### 5.2 Visual inspection

Both 180-dpi page renderings were inspected at original detail.  Equations,
subscripts, superscripts, calligraphic symbols, the theorem heading, and the
two-column transitions are legible.  There is no clipping, overlap, broken
glyph, black rectangle, missing equation number, or margin intrusion.

Page 2 is mostly blank because the standalone harness ends immediately after
the fragment.  This is not a source-layout failure and is not counted as a
finding, but pagination must be rechecked after integration into the complete
manuscript; the harness does not prove final-paper page balance.

### 5.3 Targeted theorem regression

The independent zero-budget regression and mutation checks were rerun:

```text
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
pytest                       = 12 passed
Ruff                         = All checks passed!
reader control-character scan= PASS
reader duplicate-label scan = PASS
positive budget evaluated    = False
```

These checks support the algebra and mutation resistance of the zero-budget
spine.  They do not certify a positive-budget physical calculation.

## 6. Final disposition

```text
orientation and dimensionless scale             = PASS INDEPENDENT
weighted crossover and valley asymptotics        = PASS INDEPENDENT
peak asymptotics and 2m-1 zero exhaustion        = PASS INDEPENDENT
slow-factor full-window topology summary         = PASS INDEPENDENT
fixed-epsilon weak-budget transfer summary       = PASS INDEPENDENT
quantifier order and analytical scope limits     = PASS INDEPENDENT
standalone theorem-domain closure                 = HOLD P1.1
finite-parameter evidence wording                = HOLD P1.2
compile and visible rendering                     = PASS INDEPENDENT
positive-budget science authorization            = NO
PRR claim promotion                               = HOLD
```

Decision: **the analytical content is faithfully translated, but the current
reader bytes remain on HOLD until P1.1 and P1.2 are repaired.**  After those
repairs, the three P2 edits are targeted prose closures; none requires a new
theorem or a positive-budget run.  Recompile and visually inspect the
integrated manuscript rather than relying on the sparse standalone harness.
