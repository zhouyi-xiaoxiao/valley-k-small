# Round 123: reader-facing exact-(m) theory-spine build

Date: 2026-07-14  
Decision: **PASS-COMPILE-AND-VISUAL-SELF-CHECK / HOLD-MAIN-INTEGRATION**

## Scope

The independently accepted exact-(m) theorem has been converted from a
proof/audit note into a conventional two-column manuscript section.  This
round does not edit the historical main TeX, add a finite-parameter result, or
authorize positive-budget science.

## Reader-facing content

The section states the physical quotient assumptions, conserved simplex
budget, exact-$m$ Doi theorem, common-variance Gaussian mechanism, global
$2m-1$ zero bound, weighted crossover, peak/valley displacement scales,
posterior-sector exclusion, and fixed-$\varepsilon$ weak-budget transfer.  Its
closing paragraph preserves every material limit: fixed finite $(d,m)$, compact
time window, sequential $\varepsilon$-then-$B$ quantifiers, no useful
uniform $B_0$, no event-mass floor, and no topology claim outside the window.
It also identifies the whole-window contact-interior assumption as an
asymptotically saturated-contact construction.

It intentionally contains no internal `PASS/HOLD/Round` ontology and no
uncompleted F1/F3 value.

## Frozen files

```text
manuscript/exact_m_theorem_spine.tex
f29b0df2a0ff079d117a82f07311dfb63e2c254681e07fa6a2fe1fab8b4e920d

manuscript/exact_m_theorem_spine_harness.tex
ebf18006252e5d16b384ecf117174774fb29a66f580e49565d4e32c489a07641

manuscript/exact_m_theorem_spine_harness.pdf
86428cf18eb9a84e831588cefae2ff7c9782ea3675b0f105cb156eab6673f582
```

## Verification

The harness was built with TeX Live 2025 `latexmk`/`pdflatex` under
REVTeX 4.2 in two-column reprint format.

```text
pages                         = 2
page size                     = 612 x 792 pt
undefined references          = 0
duplicate labels              = 0
overfull boxes                = 0
underfull boxes               = 0
visual clipping/overlap       = none observed on both rendered pages
positive-budget science run   = false
```

The PDF is a section build harness, not the submission manuscript.  Main-text
integration remains behind the all-grid F1 and independent F3 evidence gates;
an independent editorial/theory attack of the prose is still required before
that integration.
