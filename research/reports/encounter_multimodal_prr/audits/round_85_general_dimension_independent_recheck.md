# Round 85: independent post-fix recheck of the general-dimension repair

Date: 2026-07-14  
Predecessors: `audits/round_82_general_dimension_independent_postedit_attack.md`
and `audits/round_84_general_dimension_scope_repair.md`  
Scope: exact-byte, read-only recheck of the three Round 82 findings, including
an in-memory adversarial mutation attack on the strengthened scope test and an
independent temporary compile/PDF check  
Mutation boundary: no pre-existing source, test, note, manuscript, Supplement,
manifest, PDF, figure, or numerical artifact was changed. No scientific
producer was run. This audit is the only repository file added.

## 1. Exact verdict

**HOLD-MUTATION-COVERAGE.**

Round 84 fully repairs the scientific wording and dimensional normalization:

- R82-1 is closed in the exact main-article bytes and canonical PDF. The
  general-\(d\) theorem now uses an embedded minimum-image \(d\)-ball and the
  explicit contact-interior margin
  \(\sup_{t\in I_*}|r_*(t)|_{\mathrm{mi}}\le a-\eta\); no “disk or sphere”
  phrase remains in any of the four core theory sources.
- R82-2 is closed in the main article, Supplement, direct theorem note, and
  mixed-jet note. Each states \([B]=L^dT^{-1}\) when the killing field has
  unit \(T^{-1}\), and each prohibits a common numerical comparison of the
  dimensional budget across dimensions.
- R82-3 is **only partially closed**. The strengthened test catches the
  theorem-local \(d\)-ball, contact margin, main-text unit, main-text
  sequential-limit/nonuniformity boundary, and static Supplement
  Haar/\(W^{-(d-1)}\)/all-image/quantifier tokens. However, an actual
  in-memory mutation attack found three publication-dangerous mutations that
  the complete current scope-test module accepts: reversing the direct note's
  no-cross-dimensional-uniformity sentence, reversing the mixed note's
  no-cross-dimensional-\(B\)-comparison sentence, and injecting a false
  physical-\(d=4\) positive-budget numerical-evidence claim.

No mathematical or living-source claim defect remains in the exact Round 84
bytes. The hold is solely because Round 82 required a mutation-hardened scope
guard and that guard still misses the named semantic regressions.

Open counts:

| P0 | P1 | P2 |
| ---: | ---: | ---: |
| 0 | 0 | 1 |

## 2. Round 82 closure ledger

| Finding | Exact-byte result | Status |
| --- | --- | --- |
| R82-1: general-\(d\) contact wording | Main lines 529--534 define \(I_*\), the deterministic relative mean, the explicit supremum margin, and the embedded minimum-image \(d\)-ball. The old phrase is absent from main, Supplement, direct note, and mixed note. Canonical PDF page 4 renders the new statement correctly. | **CLOSED** |
| R82-2: explicit units and cross-dimensional comparison | Main lines 524--527, Supplement lines 139--152, direct note lines 120--133, and mixed note lines 118--121 all give \([B]=L^dT^{-1}\) and an explicit no-common-numerical-cross-dimensional-comparison boundary. | **CLOSED** |
| R82-3: mutation-hardened regression | Static and four main-local mutations improved substantially, but the independent nine-case attack caught only six and missed three semantic scope promotions. | **OPEN P2** |

The P2 does not reopen R82-1 or R82-2 mathematically. It prevents declaring the
requested test-hardening closure complete.

## 3. Scientific exact-byte recheck

### 3.1 General-\(d\) contact geometry: PASS

The main article now states

\[
 r_*(t)=\bigl(r_{\parallel,0}e^{-\gamma t},r_{\perp,0}\bigr),
 \qquad
 \sup_{t\in I_*}|r_*(t)|_{\mathrm{mi}}\le a-\eta,
\]

and identifies \(\{|r|_{\mathrm{mi}}<a\}\) as the embedded
minimum-image \(d\)-ball. This is theorem-local, not supplied by an
unrelated later appendix. The Supplement and direct note retain the same
contact-interior hypothesis, while the mixed-jet note uses the same embedded
\(d\)-ball in its exact quotient definition.

The differentiated tail proof still uses product-geodesic separation, keeps
the contact-ball boundary away from the cut locus with \(a<W/2\), and sums
every wrapped Gaussian lattice image. No single chart for the complement is
assumed.

### 3.2 \(B\) normalization and units: PASS in all four core sources

All four sources retain

\[
 V_j=W^{-(d-1)}\chi_a\phi_j,
 \qquad K_{B,w}=BV_w,
 \qquad [B]=L^dT^{-1}
\]

for a local killing rate of unit \(T^{-1}\). The factor
\(W^{-(d-1)}\) normalizes the omitted transverse common-centre Haar orbit;
it is not a normalization by relative contact volume. Each core source also
states that equal/common numerical values of this dimensional budget are not
compared across dimensions without a separate nondimensional convention.

No surviving text compares cross-dimensional \(B_0\), amplitude, or event
mass. No numerical evidence above physical \(d=3\) was found in the living
article, Supplement, notes, README, research contract, theorem program, or
focused rewrite blueprint.

### 3.3 Quantifier order, Haar quotient, all-image tail, and analytic dimension scope: PASS

The Supplement's boxed theorem retains the ordered quantifiers

\[
 \exists\epsilon_0\;
 \forall\epsilon\in(0,\epsilon_0)\;
 \exists B_0(\epsilon)\;
 \forall B\in(0,B_0)\;
 \forall w\in\mathcal W.
\]

The diagonal-Haar identity and \(W^{-(d-1)}\) centre-space normalization
are unchanged. The all-image tail text explicitly contains “every Euclidean
lift” and “summing the images.” The weighted \(H^1\) form and bounded
multiplication proof remain pointwise in each fixed finite \(d\) and invoke
no low-dimensional Sobolev embedding. The sources explicitly deny uniformity
in \(d\), a \(d\to\infty\) limit, and a numerical promotion beyond the
physical \(d=2,3\) evidence boundary.

## 4. Independent mutation attack

### 4.1 Method

The current `code/test_general_dimension_scope_consistency.py` was imported
without modification. Its `_read` helper was monkey-patched **in memory** to
return one mutated source at a time, and all four test functions in that module
were run for each mutation. No mutated file was written to the repository or
to a temporary checkout.

A mutation is “CAUGHT” when at least one current test raises; it is “MISSED”
when the complete module accepts the mutated source.

### 4.2 Results

| Mutation | Result |
| --- | --- |
| Remove the Supplement's ordered \(\forall\epsilon\) token before \(\exists B_0\) | **CAUGHT** |
| Remove the Supplement's diagonal-Haar contract label | **CAUGHT** |
| Replace every Supplement \(W^{-(d-1)}\) normalization token | **CAUGHT** |
| Replace “every Euclidean lift” by a nearest-image-only statement | **CAUGHT** |
| Reverse the main theorem's no-uniform/no-cross-dimensional comparison sentence | **CAUGHT** |
| Reverse the main abstract's open positive-budget physical-\(d=3\) gate | **CAUGHT** |
| Reverse the direct theorem note's statement that \(B_0\), budget, amplitude, and mass are not uniform or compared across dimensions | **MISSED** |
| Reverse the mixed-jet note's statement that the dimensional \(B\) is not compared at one common numerical value across dimensions | **MISSED** |
| Inject “physical-\(d=4\) positive-budget numerical evidence is complete” into the main abstract while leaving the \(d=3\) open-gate sentence present | **MISSED** |

The misses follow directly from the test structure:

1. the four built-in mutation cases target only the main theorem text;
2. the Supplement/direct/mixed checks require the token “uniform,” not an
   explicitly negative theorem-local phrase; and
3. numerical scope is established by requiring existing \(d=3\) caveats,
   without forbidding a simultaneous unsupported numerical claim for
   \(d>3\).

Therefore a green 18-test run does not yet prove the semantic closure claimed
for R82-3.

### 4.3 Required repair

The next test-only repair should:

- define negative, theorem-local contracts for **each** of main, Supplement,
  direct note, and mixed note, including the dimensional-\(B\) no-comparison
  sentence and the no-uniform-in-\(d\) sentence;
- reject positive phrases such as “uniform in \(d\),” “compared across
  dimensions,” and “common numerical \(B\) across dimensions” in those
  theorem sections;
- forbid numerical-evidence promotions for physical \(d>3\) in every living
  scope surface; and
- add direct mutation cases for the three missed attacks above, in addition
  to the existing \(d\)-ball, margin, sequential-limit, and unit mutations.

## 5. Regression, compile, and PDF evidence

Focused regressions were run without a scientific producer:

```text
../../../.venv/bin/python -m pytest -q \
  code/test_general_dimension_scope_consistency.py \
  code/test_living_scope_consistency.py \
  code/test_compile_manuscript.py

18 passed
```

Ruff on `code/test_general_dimension_scope_consistency.py` passed.

Using TeX Live in a temporary directory with
`SOURCE_DATE_EPOCH=1783900800`, the independently rebuilt 13-page article PDF
was byte-identical to the canonical PDF:

```text
fa4debf25af63f3c1d58cbc68b44d08b4c6add223e92207c18f7264bbf0774c6
```

The canonical manifest correctly pins the repaired TeX hash and PDF hash,
reports two byte-identical clean builds, 13 letter pages, 798,156 bytes, 45
embedded/subset font rows, zero Type-3/unembedded rows, and zero missing-file,
overfull-box, undefined-reference, or undefined-citation counts. It remains
`release_eligible=false`, as required by the larger scientific gate boundary.

Article page 4 was independently rendered at 180 dpi. The unit sentence,
explicit contact margin, and embedded \(d\)-ball are readable without clipping,
collision, or an excessive gap. A separate temporary Supplement build
completed in 12 letter pages and 480,925 bytes, with 31 embedded font rows and
no overfull-box, undefined-reference, or undefined-citation match. All
temporary compile/render outputs were deleted.

## 6. Exact bytes inspected

| File | SHA-256 |
| --- | --- |
| `audits/round_82_general_dimension_independent_postedit_attack.md` | `428b0970dbd4855cd366fde9770b8a32d744035177adb5a3a99c524419728f2f` |
| `audits/round_84_general_dimension_scope_repair.md` | `c2808da3aa4a260a3c2333979119651242d9ffc3895869beb87d5347c1881120` |
| `manuscript/encounter_multimodal_prr.tex` | `1c17be4ac1223fa769166cc13c4b551a1cf7925ae59a61a81021657421305c5b` |
| `manuscript/encounter_multimodal_prr_supplement.tex` | `4a5b3073d346fd50528d8c5a8fd51b914d94730c8d5b82def641627bfd168f07` |
| `notes/direct_physical_multimode_theorem.md` | `2b35d1b1053045220b29975d30f8b3c842d33273ca46de86b8cf7798c26a9c3d` |
| `notes/pde_mixed_jet_theorem.md` | `ac0e6cbb34d446d2b9ae2b52c22684ee72da7cadb04d864aacba085dff75f095` |
| `code/test_general_dimension_scope_consistency.py` | `73a88eabe3209149e69cc231597055fbd4e0de415cc8e55d5eb984b688afcfbc` |
| `artifacts/data/manuscript_compile.json` | `795f8c2bdaced87414c4d87adbaf2a2ea813fb07dbee710669e9b42035b3f493` |
| `manuscript/encounter_multimodal_prr.pdf` | `fa4debf25af63f3c1d58cbc68b44d08b4c6add223e92207c18f7264bbf0774c6` |
| `README.md` | `024c5d45da89b2e630fe8cbbeb7acf895f7710035da5b9d7152270b940ca07c3` |

## 7. Release decision

The repaired general-\(d\) theorem and its living scientific wording are
mathematically acceptable. The canonical PDF/manifest are synchronized and
reproducible. Nevertheless, Round 84 does **not** completely close all three
Round 82 findings because the required semantic mutation guard remains
incomplete.

The exact Round 85 decision is therefore **HOLD-MUTATION-COVERAGE**, with
P0/P1/P2 = \(0/0/1\). After a test-only mutation-hardening repair catches the
three missed cases, an independent recheck may accept the general-dimension
promotion. This does not change the separate project-level HOLD for the
allocation cusp, continuation, independent solver, or positive-budget
physical-\(d=3\) evidence.
