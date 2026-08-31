# Round 165: continuum C0-A and theorem-first working-set re-audit

Date: 2026-07-14

Decision: **C0-A OPERATOR-REALIZATION THEOREM PASS / FINAL P0 = 0 / P1 = 0 /
P2 = 0 / WORKING-SET BUILD PASS / COMPLETE C0 OPEN / C1--C3 OPEN /
CONTINUUM TOPOLOGY HOLD / F0 HOLD / NO F1 / NOT RELEASE ELIGIBLE**

This round integrates one genuine continuum theorem and the bounded Round-164
method successors without promoting either beyond its proof boundary.
The theorem-first main source and accepted exact-m proof remain unchanged.
The Supplemental Material now contains the physical two-dimensional
natural-decay operator corollary.  The research contract and next-stage path
record the new theorem and the narrower, still-open F0/continuum dependencies.

No positive-budget control value, F1 row, production-size state, or new
publication-level numerical result was evaluated or read.

## Final integrated bytes

| Object | SHA-256 |
| --- | --- |
| notes/continuum_research_program_v2.md | d965b604214a16ac74666a008a5913029dfe52519b4e06496f6416d01cee2ed4 |
| code/test_continuum_research_program_v2_scope.py | 21e69583d404a0a7650dc48a46dbf32c38a67d394fcc3c21ea49a901fb57cb71 |
| notes/research_contract.md | 28789c9a23ce0d7386b15333ec9141ea0c329eeee763e13c634903fe716d8d46 |
| notes/continuum_next_stage_path.md | 99976f000d673722d6e36984d4d092646f7a70147fce31eda832b45291eaa0b3 |
| code/test_general_dimension_scope_consistency.py | fefa5e3a6fc837ab9335a4cc5b17ac9757c52ad3d6bbce1e6df4ecd4aab55099 |
| manuscript/encounter_multimodal_prr_supplement.tex | 1323786749826d403535fac7034554a4b5fc32ce8dd1173ccf1747422ff69e77 |
| manuscript/encounter_multimodal_prr_theorem_first_working.tex | 6e7393e44bb1da9bb196b839534fdf43e18dd90d0829d941ad7e155f4afcbc67 |
| output/pdf/encounter_multimodal_prr_theorem_first_working.pdf | c766de16ca3a70eda63397d4d78ccb9f44415982afa4d4b6e0a295197488984b |
| output/pdf/encounter_multimodal_prr_theorem_first_supplement_working.pdf | ea2a33a1faa18bf8c24f002b75b177f94204fc05381ee73d14ae65d251db11ab |
| artifacts/data/theorem_first_working_compile.json | 38c03adfc95d3929aa5039b206cbe892a914f9ccf7a7e047ede337d9b2ffcb1b |

The Round-149 exact-m theorem source, proof, bibliography, and canonical main
PDF remain byte-identical.  Historical Round-149, Round-160, and Round-163
tests now pin immutable source/audit records and verify older generated hashes
inside their corresponding audit text; they no longer mistake a later valid
living-file update for historical drift.

## C0-A theorem

For physical \(d=2\), let

\[
 \pi(x)=Z_\pi^{-1}
 \exp\!\left[-\frac{\gamma}{2D}
 \bigl((z-\bar z)^2+r_\parallel^2\bigr)\right],
 \qquad Z_\pi=\frac{2\pi DW}{\gamma}.
\]

Direct differentiation gives \(\mathbf D\nabla\log\pi=b\).  On
\(H=L^2(\Omega_\infty,\pi dx)\), the free energy form closed from the compact
smooth Gaussian-torus core is a symmetric Dirichlet form.  Bounded
nonnegative sharp-contact killing is a bounded form perturbation, hence keeps
the same domain and gives a closed symmetric nonnegative Dirichlet form.
The first representation theorem supplies \(H_{\infty,c}\ge0\) and a
symmetric analytic sub-Markov contraction semigroup.

Multiplication \(Uu=\pi u\) is unitary from \(H\) to the natural density space,
and integration by parts identifies

\[
 A_{\infty,c}=U(-H_{\infty,c})U^{-1}
\]

as the form-associated natural-decay realization whose action agrees with the
algebraic generator on the displayed core.  The final text does not assert or
need essential self-adjointness of the minimal core operator.

The spectral theorem gives, for \(r=0,1,2\), \(t\in[\tau,T]\),

\[
 \|H_{\infty,c}^{\,r}e^{-tH_{\infty,c}}\|
 \le C_r(\tau),\qquad
 C_0(\tau)=1,\qquad
 C_r(\tau)=\left(\frac{r}{e\tau}\right)^r.
\]

Gaussian cutoffs put the constant function one in the form domain.  Testing
the weak evolution with that function and using sub-Markov positivity gives

\[
 \int_{\Omega_\infty}q_{\infty,c}(t)\,dx
 +B\int_0^tF_{\infty,c}(s)\,ds=1.
\]

An independent mathematical reader checked the Gaussian cutoff, form
closedness, bounded killing, unitary realization, spectral constants, and
integrated mass identity.  The first read returned P0=0, P1=0 and two wording
P2s: graph-closure ambiguity and a malformed thin-space exponent.  After the
text was changed to form-associated realization, explicitly disclaimed the
unneeded essential-self-adjointness assertion, and repaired
\(H_{\infty,c}^{\,r}\), the same reader rechecked the final exact bytes and
returned P0=0, P1=0, P2=0.

## Exact theorem boundary

C0-A closes only the unbounded physical operator/form/semigroup and elementary
observable-calculus sublemma.  It does not close:

~~~text
concrete hash-bound model contract                     = OPEN C0
finite-box form and identification maps                = OPEN C0
fixed-box Mosco / strong-resolvent convergence         = OPEN C1
computable positive-time spatial errors r=0,1,2        = OPEN C2
first/second derivative box-truncation errors          = OPEN C3
error composition and complete continuum root transfer = OPEN C5/C6
independent clean continuum audit                      = OPEN C7
continuum stationary topology                          = HOLD
~~~

The direct OU exit estimate remains an order-zero input and is not reused as a
first- or second-time-derivative bound.

## Numerical and status validation

The complete local seven-layer tiny method regression passed:

~~~text
packed kernel
directed interval action
rate-action composition
tiny uniformization
target-aware adapter
independent semantic replay
tiny-Q jets

combined result                                155 / 155 passed
~~~

The status/theory/environment/compile suite, including Rounds 149, 160--164,
passed 58/58.  A narrower integrated continuum and theorem-first suite passed
48/48 before the final aggregate.  Ruff check and format check passed on all
twelve changed Python files.

Repository-level documentation-path and science-rule checks passed.

## Deterministic build and visual check

The report-owned compiler performed two isolated builds of each document and
published only after validation.  An additional TeX Live latexmk build through
the bundled LaTeX workflow also succeeded for both sources.

~~~text
main pages                                      5
Supplemental pages                             21
main rebuilds byte-identical                    yes
Supplemental rebuilds byte-identical            yes
all fonts embedded                              yes
Type-3 fonts                                      0
overfull boxes                                    0
undefined references                              0
undefined citations                               0
Ghostscript parse                               pass
release_eligible                               false
positive_budget_evaluated                      false
positive_budget_scientific_values_read         false
~~~

All five main pages and all twenty-one Supplemental pages were rendered to
contact sheets for visual review.  The first and final main pages and the new
C0-A page were also inspected at larger scale.  No clipping, overlap, broken
formula, or unreadable transition was found.

The five-page main document remains an intentionally compact theorem-first
working skeleton.  Its page count is not treated as a publication gate.  It
should grow only when the held finite-parameter numerical result supplies
defensible methods, figures, and results; this round does not pad it with
internal implementation detail.

## Final status

~~~text
exact-m complete finite-window theorem          = ACCEPTED WITH STATED SCOPE
physical natural-decay C0-A sublemma             = PROVED / RE-AUDITED
Round-164 tiny method successors                 = METHOD PASS ONLY
F0 complete certificate                          = HOLD
F1 positive-budget 36-row campaign               = NOT AUTHORIZED / NOT RUN
strict continuum topology                        = HOLD
PRR submission package                           = HOLD
~~~
