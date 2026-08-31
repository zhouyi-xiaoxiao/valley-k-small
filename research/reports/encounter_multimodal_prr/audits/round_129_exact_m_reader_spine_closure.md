# Round 129: independent closure audit of the repaired reader-facing exact-\(m\) spine

Date: 2026-07-14  
Role: independent theorem-domain, claim-boundary, compile, and visual closer  
Decision: **HOLD FOR ONE RESIDUAL P1 DOMAIN REPAIR**  
Findings: **P0 = 0, P1 = 1, P2 = 0**  
Positive-budget science: **NOT RUN / NOT AUTHORIZED / NOT USED**

## 1. Frozen inputs and independence boundary

I audited the repaired reader fragment directly rather than accepting the
repair description.  The frozen inputs were

```text
manuscript/exact_m_theorem_spine.tex
95cc86fe9ac6b5bc2de7b4e63f3ad877d7be920219d62a89b81ef21a5687551d

manuscript/exact_m_theorem_spine_harness.tex
ebf18006252e5d16b384ecf117174774fb29a66f580e49565d4e32c489a07641

notes/exact_m_mode_encounter_theorem_v2.md
e78a0d77959d50214d56ef4708a20ac465232883fbbdd4ee42fe488c0b95c85d

audits/round_118_exact_m_theorem_v2_independent_attack.md
d78c0364c6c63e3b9d360fd104d1b52ca59795deb7b39e64d04c7cf707ff5a06

audits/round_120_exact_m_theorem_v2_p2_closure.md
dfc0381ddbc87a7c338978f80f5a9c9219536409b06905a03f5cdcd2fafbb10e

audits/round_126_exact_m_reader_spine_independent_attack.md
cafeefd8f5f19547f171ed0f1b131806ea5948b13c16a1df5757180f0bb06c9c
```

I did not edit either TeX source.  I did not inspect a prospective positive
budget, construct or evaluate a positive-budget generator, or run Monte Carlo.
The only repository write made by this audit is this file.

## 2. Executive result

The repair closes Round 126 P1.2 and P2.1--P2.3 exactly as requested.  It also
closes almost all of P1.1: the stochastic quotient, covariance and
weighted-space assumptions, independence, minimum-image contact geometry,
killing field, conserved budget, free exposure, and physical Doi density are
now local to the theorem fragment.

One part of the theorem domain is still open.  The fragment uses
\(\ell_0\) in a denominator and \(\rho\) in a Gaussian normalization,
variance, and slab width, but it never says locally that these are fixed
positive scales.  The accepted source theorem explicitly fixes
\(\ell_0>0\) and \(\rho>0\).  Without those declarations, “the data above” is
not a closed admissible parameter set, \(\ell_0=0\) makes the displayed
coordinate undefined, and \(\rho=0\) makes the catalyst singular.  This is a
residual part of Round 126 P1.1, not a new mathematical objection.

The minimal repair is to include, before the process/theorem, an explicit
clause such as

```text
fix positive longitudinal reference and slab scales ell_0,rho>0
```

and then rehash and rebuild.  No positive-budget science is needed to close
this item.

## 3. Round-126 closure replay

### P1.1 -- Doi-transfer hypotheses and observables: PARTIAL PASS / RESIDUAL HOLD

The repaired fragment now pins all of the specifically requested structural
items:

1. **Quotient and dynamics: PASS.**  It fixes finite \(d\ge2\), finite
   \(m\ge1\), \(W>0\), \(0<a<W/2\), and
   \(I=[\tau,T]\subset(0,\infty)\), and displays the midpoint OU,
   longitudinal relative OU, and transverse torus Brownian SDEs.
2. **Initial law and weighted-space conditions: PASS.**  The midpoint
   variance is \(\varepsilon^2D_0/(2\gamma)\); the relative longitudinal
   variance is \(\varepsilon^2u_0^2\); the transverse law is wrapped Gaussian;
   and the text requires \(D_0,\gamma,u_0>0\),
   \(u_0^2<4D_0/\gamma\), and
   \(\Sigma_{\perp,0}\succ0\).  Together with
   \(D_0/(2\gamma)<D_0/\gamma\), these are the accepted weighted-space
   inequalities.
3. **Independence: PASS.**  The three initial laws are mutually independent;
   the midpoint and relative processes are independent; and all driving
   Brownian motions are stated to be independent.
4. **Minimum-image contact: PASS.**  The fragment states the minimum-image
   convention, the radius restriction \(a<W/2\), and the whole-window margin
   \(\sup_{t\in I}|r_*(t)|_{\rm mi}\le a-\eta\) for \(\eta>0\).
5. **Killing field and budget: PASS.**  The normalized physical slabs and
   \(K_{B,\bm w,\varepsilon}=B V_{\bm w,\varepsilon}\) are displayed, including
   the transverse \(W^{-(d-1)}\) normalization and fixed installed
   centre-space budget.
6. **Observables: PASS.**  The fragment locally defines
   \(G_{\varepsilon,\bm w}=B^{-1}\mathbb E_0K
   =\langle V,T_0q_0\rangle\) and the killed reaction-time density
   \(f_{B,\varepsilon,\bm w}\), so “unit budget” can no longer be confused
   with evaluation at \(B=1\).

However, the source theorem fixes a positive physical reference length at
Section 2.2 and a positive slab-width scale at the start of its Gaussian
construction.  The reader fragment introduces neither declaration before
using \(\ell_0\) and \(\rho\).  Semantic phrases such as “width” are not a
sufficient replacement for a closed theorem hypothesis when the symbols also
occur in denominators.  Therefore P1.1 is not completely closed.

Disposition: **P1 / HOLD CURRENT READER BYTES**.

### P1.2 -- finite-parameter evidence wording: CLOSED

The unsupported present-tense sentence has been replaced by

> Nontrivial contact, observability at a common positive budget, and
> finite-parameter robustness remain separate numerical validation gates.

This is a gate statement, not an assertion that a positive-budget result has
already passed.  It agrees with the analytical saturation ceiling and with
the current evidence boundary.

Disposition: **CLOSED**.

### P2.1 -- nonempty allocation family: CLOSED

The fragment now requires

\[
 \sum_{j=1}^m w_j=1,\qquad w_j\ge w_*>0,\qquad 0<w_*\le1/m.
\]

This makes \(\mathcal W_{w_*}\) nonempty (including the singleton at
\(w_*=1/m\)), compact, and strictly inside the simplex.

Disposition: **CLOSED**.

### P2.2 -- tail finiteness before generalized Rolle: CLOSED

The zero-count sketch now states that the extreme affine--exponential terms
dominate in both tails, hence all zeros lie in a compact interval; the
nonzero real-analytic exponential polynomial then has only finitely many
zeros there.  Generalized Rolle is invoked only after that finiteness step.
This matches the named version-2 repair.

Disposition: **CLOSED**.

### P2.3 -- adjacent odds and orientation: CLOSED

The fragment defines

\[
 q_k(x)=w_k\exp[-(x-c_k)^2/(2\sigma^2)]
\]

and explicitly states

\[
 \frac{q_{j+1}}{q_j}=\frac19
 \quad\text{at}\quad
 s_j-\frac{\sigma^2\log9}{c_{j+1}-c_j},
 \qquad
 \frac{q_{j+1}}{q_j}=9
 \quad\text{at the plus edge}.
\]

Direct subtraction of the two Gaussian exponents confirms this orientation
from the displayed weighted crossover.  The text cannot now be misread as a
claim about unlabelled full-posterior odds.

Disposition: **CLOSED**.

## 4. No new mathematical overclaim

Apart from the unpinned positivity of \(\ell_0\) and \(\rho\), the repaired
fragment remains equivalent to the accepted exact-\(m\) core.  In particular,
it retains:

- fixed finite \(d,m\) and a compact positive-time window;
- the increasing joint trajectory/centre orientation;
- the weighted crossover and exact \(1/9,9\) adjacent odds;
- \(m\) maxima, \(m-1\) minima, and complete \(2m-1\) zero exhaustion;
- slow-factor maximum and minimum shifts of \(O(\sigma^2)\) and
  \(O(\sigma^4)\), respectively;
- the sequential order “small positive \(\varepsilon\), then existential
  \(0<B<B_0(\varepsilon)\)”; and
- no useful \(B_0\), event-mass floor, growing-dimension/mode, or
  outside-window claim.

The phrase “budget-rescaled” is also preserved; the fragment does not call
\(f/B\) a normalized probability density.

## 5. Independent build, regression, and visual evidence

### 5.1 Fresh isolated build

The harness was built in a fresh temporary directory using the bundled
LaTeX workflow with TeX Live 2025.  The effective command was

```text
/Library/TeX/texbin/latexmk -norc -pdf -interaction=nonstopmode
  -halt-on-error -synctex=1
  -outdir=/private/tmp/round129-reader-spine.0holXZ
  manuscript/exact_m_theorem_spine_harness.tex
```

Result:

```text
exit code                     = 0
pages                         = 2
page size                     = 612 x 792 pt (US Letter)
PDF bytes                     = 287847
undefined references          = 0
multiply defined labels       = 0
LaTeX/package errors          = 0
overfull boxes                = 0
underfull boxes               = 0
missing glyphs                = 0
nameref compatibility warning = 1
```

The sole warning is the same harmless RevTeX/`nameref` replacement warning
seen in Round 126.  It produces no unresolved reference, duplicate
destination, or visible defect.

Fresh PDF hash:

```text
01b75382c1477873efc179d6bf9c98153ea6ff69235d0fb183b8bcb594723bab
```

The repository harness PDF has hash

```text
82ef5a5518b1d27a38721ab303a88b36646e1187b9058130dd94b67278d7ccd6
```

The PDF hashes differ because of generated timestamps, but their 180-dpi page
renderings are byte-identical:

```text
page 1  fd1cc026a3d20ad63905811f9f23a5dc0d4694339ff638ae2d1f53162a83b988
page 2  5b413f74ce3da542915484a6260ff1c2ddce7ad8684d45f65a5adc53faed5c28
```

Thus the repository PDF is synchronized with the audited source visually.

### 5.2 Two-page visual inspection

Both 180-dpi pages were inspected at original detail.  The SDEs, initial-law
array, minimum-image condition, simplex, killing field, observables, theorem,
crossover ratios, and weak-budget norm are legible.  There is no clipping,
overlap, margin intrusion, broken glyph, black rectangle, or lost equation
number.  The column break between Eqs. (4) and (5) is coherent.  Page 2 is
sparse because the standalone harness ends after the fragment; that is not a
layout defect, but full-manuscript pagination must still be checked after
integration.

### 5.3 Targeted zero-budget regression and source hygiene

The analytical zero-budget tests and linter were rerun without any
positive-budget input:

```text
pytest tests = 12 passed
Ruff        = All checks passed!
control-character scan = PASS
duplicate-label scan   = PASS
```

These checks support the unchanged analytical core only.  They do not supply
or imply finite-parameter positive-budget evidence.

## 6. Final disposition

```text
Round 126 P1.1 model SDE/covariance/independence = CLOSED
Round 126 P1.1 minimum-image contact             = CLOSED
Round 126 P1.1 K, V, G, and f definitions        = CLOSED
Round 126 P1.1 ell_0,rho positive-domain pin     = HOLD P1
Round 126 P1.2 numerical-gate wording            = CLOSED
Round 126 P2.1 nonempty weights                  = CLOSED
Round 126 P2.2 tail finiteness                   = CLOSED
Round 126 P2.3 odds orientation                  = CLOSED
compile and two-page rendering                   = PASS INDEPENDENT
positive-budget science                          = NOT RUN / NOT AUTHORIZED
```

Decision: **HOLD the current reader bytes for the single explicit
\(\ell_0,\rho>0\) parameter-domain repair.**  Once that clause is present and
the new bytes are rebuilt, the Round-126 reader-spine findings can be closed
without reopening the accepted exact-\(m\) theorem or running positive
budget.
