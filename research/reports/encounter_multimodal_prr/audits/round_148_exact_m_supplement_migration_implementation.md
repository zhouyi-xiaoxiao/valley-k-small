# Round 148: exact-\(m\) supplement migration implementation and self-audit

Date: 2026-07-14  
Reviewer: implementation agent / self-auditor  
Decision: **IMPLEMENTATION COMPLETE / SELF-AUDIT PASS / INDEPENDENT
HASH-SPECIFIC ACCEPTANCE REQUIRED / PRR HOLD / F0 HOLD / F1 HOLD**  
Findings: **P0 = 0, P1 = 0, P2 = 0 within the implementation boundary**

## 1. Scope and authority boundary

This round migrated the already accepted technical proof from
`notes/exact_m_mode_encounter_theorem_v2.md` into one reader-facing TeX
fragment:

```text
manuscript/exact_m_theorem_full_proof.tex
```

The fragment is designed to be read by
`manuscript/encounter_multimodal_prr_supplement.tex` through `\input{...}`.
It has no document class, package imports, bibliography command, or
`\end{document}` of its own.  The implementation agent changed no theorem
claim outside this migration and did not run positive-budget science,
finite-parameter continuum numerics, F0, F1, or a publication release.

This is an implementation record and a self-audit.  Because the same agent
performed the migration and the checks below, this round is not independent
mathematical acceptance of the frozen proof bytes.

## 2. Proof content migrated

The new fragment contains the complete reader-facing chain required by the
exact-\(m\) result:

1. the fixed-finite-dimensional Doi quotient, mutually independent initial
   laws, and the stationary midpoint variance
   \(\operatorname{Var}Z_t=\varepsilon^2D_0/(2\gamma)\);
2. the increasing dimensionless longitudinal coordinate, consistently
   transformed catalyst centres, normalized Gaussian slabs, compact
   simplex-interior allocation family, and conserved installed budget;
3. a differentiated contact-tail lemma under a contact-interior margin on
   the whole declared interval \(I\);
4. the exact common-variance Gaussian-mixture factorization and logarithmic
   slope identities;
5. a global \(2m-1\) real-zero bound counted with multiplicity, including
   two-tail finiteness, plus uniform adjacent-component isolation;
6. the complete pure-mixture topology, including \(m=1\), endpoint signs,
   weighted crossovers, \(m\) simple maxima, and \(m-1\) simple minima;
7. the full posterior-sector complement certificate, including the
   \(1/9\)- and \(9\)-odds crossover edges rather than a false exponential
   dominance assertion there;
8. preservation by a positive factor with uniformly bounded first two
   logarithmic derivatives, with \(O(\sigma^2)\) peak shifts,
   \(O(\sigma^4)\) valley shifts, and no complement roots;
9. the fixed-\(\varepsilon\), uniform-in-allocation \(C^2\) Doi transfer
   through Supplemental Theorem `thm:mixed-jet`; and
10. the exact quantifier order and the saturated-contact, event-mass,
    finite-budget, fixed-window, fixed-\(d\), and fixed-\(m\) scope limits.

No undefined `\bm1`-style macro is used.  The classical status of the
univariate Gaussian-mixture mode cap is now stated with
`carreiraPerpinanWilliams2003modes` and
`amendolaEngstromHaase2020modes`; the direct multiplicity proof is retained
because the later Doi transfer needs explicit root, curvature, and complement
margins.

## 3. Why Supplemental Sections S4 and S5 do not conflict

| Boundary | S4: retained local theorem | S5: migrated exact theorem |
| --- | --- | --- |
| Midpoint variance | permits time-varying \(s^2(t)\) | pins the stationary coefficient \(D_0/(2\gamma)\), giving a common mixture variance |
| Contact condition | required only on the union of target neighbourhoods \(I_*\) | required on the whole declared window \(I\) |
| Root construction | one strictly concave root in each shrinking target interval | peak and valley roots plus an exhaustive whole-window complement certificate |
| Guaranteed maxima | at least \(m\) | exactly \(m\) |
| Guaranteed minima | at least one between certified peak intervals; degeneracy not excluded | exactly \(m-1\), all nondegenerate |
| Extra stationary points | not excluded | excluded on all of \(I\), with nonstationary endpoints |
| Global zero bound | not used | \(2m-1\) zeros counted with multiplicity |
| Weak-budget order | fix small \(\epsilon\), then choose \(B<B_0(\epsilon)\) | the same sequential order |

S5 is therefore a stricter stationary/common-variance, whole-window subfamily
of the broader S4 setup.  Its stronger exact-topology conclusion uses stronger
hypotheses and an additional global argument; it does not retroactively
strengthen S4.  Both results remain pointwise in fixed finite \(d,m\), permit
all thresholds to depend on the fixed data, and make no useful uniform
positive-budget or event-mass claim.

The integrated abstract, the transition immediately before the S5 input, the
formal-verification table, and the reserved-module status paragraph preserve
this distinction.

## 4. Frozen source and build bytes

The final bytes checked in this round were:

| object | SHA-256 |
| --- | --- |
| `manuscript/exact_m_theorem_full_proof.tex` | `a372b5a33d2203b8f3214a153f4aaf1e81497bf146c0ac1db1cfda97919c1c7b` |
| `manuscript/encounter_multimodal_prr_supplement.tex` | `566b752f2d5c2c8fabdf0a421f16599317a697dd46f7d41b6b16475495cb2e65` |
| `manuscript/references.bib` | `2f90b6735993c6d2fa8bb8f1a6c35c334706d02585361d4ee9238ac020ce9c76` |
| compiled Supplemental PDF | `fadc9b1277d51d7c0bca763bf59c47d17275543e5fd5afba22bea69b7fdd62d2` |

The compiled PDF had 20 pages and 540,550 bytes.  Its embedded title was:

```text
Supplemental Material: finite-window modality by conserved-budget support design
```

## 5. Static and TeX Live checks

Before compilation, the proof/supplement pair had:

```text
new proof labels                         87, all unique
duplicate labels across proof/supp       0
unresolved proof ref/eqref targets        0
unresolved new bibliography keys         0
C0 control characters in proof           0
inline \( / \) delimiter counts         244 / 244
```

The latest workspace Supplemental bytes were then compiled with TeX Live
2025 through the bundled LaTeX compile driver, which invoked:

```text
/Library/TeX/texbin/latexmk -norc -pdf -interaction=nonstopmode \
  -halt-on-error -synctex=1 \
  -outdir=/private/tmp/exact_m_full_proof_compile_clean \
  manuscript/encounter_multimodal_prr_supplement.tex
```

Observed result:

```text
latexmk exit code                         0
Missing $ inserted                        0
undefined references/citations            0
undefined control sequences               0
multiply defined labels                   0
LaTeX errors / emergency / fatal stops    0
overfull boxes                            0
```

The log retained only the existing REVTeX default-size warning, the
`nameref` package label-definition warning, and one underfull box in the
formal-boundary table at Supplemental source lines 1212--1213.  None is an
exact-\(m\) proof syntax or cross-reference failure.

## 6. Acceptance and release boundary

This round establishes that the accepted technical proof has been migrated
into a syntactically valid, cross-reference-complete, reader-facing
Supplemental section and that the current integrated Supplemental source
compiles cleanly on the frozen bytes above.

It does **not** establish:

- an independent mathematical re-audit of every sector inequality, uniform
  constant, or fixed-\(\varepsilon\) semigroup hypothesis;
- a nontrivial-contact finite-parameter continuum example;
- a useful common positive budget;
- event-basin mass, survival, solver-convergence, or discretization evidence;
- F0 or F1 acceptance; or
- PRR submission readiness.

A fresh agent must independently audit the exact proof hash above before the
migration can receive independent acceptance.  Until that happens, and until
the separate finite-parameter and selector gates close, the release state is:

```text
exact-m migration implementation          COMPLETE
implementation self-audit                 PASS
independent exact-byte proof acceptance   PENDING
PRR                                       HOLD
F0                                        HOLD
F1                                        HOLD
```
