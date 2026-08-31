# Focused theorem-first physical-2D manuscript-spine rewrite blueprint

Date: 2026-07-14; updated 2026-07-15  
Purpose: post-result rewrite plan for the focused physical-`d=2` PRR route  
Execution boundary: the historical fixed-control `B=0.01` point remains valid
in its scoped two-mesh context, while allocation-v6 is a terminal scientific
HOLD.  The exact-`m` theorem spine is now accepted by Rounds 118 and 120.  A
roughly 6-page theorem-first body (seven physical pages including references)
and 23-page analytical Supplement now provide the coherent reader-facing
theory working set.  The exact-`m` spine and Supplement passed the independent
Round-149 hash-specific audit; the later C0-A main-text migration passed the
separate continuum C-A mathematical and rendered-PDF audit at its new exact
hashes.  Expanding that working set into the finite-parameter PRR paper remains
conditional on the new all-grid F1 controls and independent common-observable
F3 validation.

## Snapshot read

The editorial anchors in this blueprint were captured from the earlier
1079-line, 12-page historical manuscript snapshot:

- `manuscript/encounter_multimodal_prr.tex`, SHA-256
  `f3bf7cb11b7657bc65cdcbb3b9f7fcc15e3b799c072177d2daaeb738401c89ed`;
- `manuscript/encounter_multimodal_prr.pdf`, SHA-256
  `13986921d2f8c5f478845bfd1abeaa9161e173d0b8030430757b9f65694ab94b`;
- `audits/round_33_prr_promotion_strategy.md`, SHA-256
  `4c2037ebcbeb2f6cc2a38ac56919d513120683a294249432cca1f615b85d4f56`.

Line numbers below refer to this TeX snapshot. They are editorial anchors, not
instructions to patch a live file while the positive-`B` result is pending.

The live archived historical copy has since moved to 1166 lines and 13 pages:

- `manuscript/encounter_multimodal_prr.tex`, SHA-256
  `1c17be4ac1223fa769166cc13c4b551a1cf7925ae59a61a81021657421305c5b`;
- `manuscript/encounter_multimodal_prr.pdf`, SHA-256
  `fa4debf25af63f3c1d58cbc68b44d08b4c6add223e92207c18f7264bbf0774c6`.

Those live historical files remain archived and superseded; their extra pages
are not accepted content for the active theorem-first article.  After the
accepted C0-A operator-realization migration on 2026-07-15, the active main PDF
is seven physical pages (roughly six pages of body plus references), and its
23-page Supplement makes the current working set 30 physical pages in total:

- active main TeX SHA-256
  `10d62404f15e306072e093aaa6fa5abbf5f6bdb0ecb42a341e3740dcf77aac2c`;
- active main PDF SHA-256
  `577d2d4b494633a3e009f13fbd581a9c889d7c84fd11c18e5b3367a6e4b1a42e`;
- active Supplement PDF SHA-256
  `70de25968298d58222bbab10639a2253067f5c01d4d6462d743e3e6eca5790fb`;
- compile manifest SHA-256
  `704c96f173c51423457ef8b03fa8ee914ec10bedebc3e6aa435965991d34a6ea`.

## 1. Editorial decision

The submission manuscript should contain one physical argument, not a history
of six evidence programs:

> Under a conserved centre-space reactivity budget, separated exposure clocks
> construct prescribed finite encounter-reaction-time mode patterns; a weak-
> reaction mixed-jet theorem transfers their topology to the Doi law; and one
> four-slab physical-`d=2` family realizes distinct one-, two-, and three-mode
> finite-budget clocks under one conserved resource and an independent event-
> law validation.

The last clause may appear only after all 36 F1 rows and F3 pass.  The word
`exact` in the first clause is licensed by the independently accepted exact-
`m` theorem under its fixed-finite, compact-window, sequential limits.

The broad four-slab family with the broader catalyst/initial supports must be
the sole finite-parameter numerical spine. The narrow exact-kernel chains,
GIG screens, G1 negative searches, and the unrelated three-slab `B=0.6` fold
may document ancestry or reproducibility, but they must not interrupt the main
argument.

## 2. Proposed reader-facing architecture

Target a focused main article of roughly 8--10 reprint pages before references,
with three principal figures and at most one compact quantitative table. Proof
details, numerical provenance, and secondary designs belong in a separate
Supplemental Material file.

| New main section | Scientific job | Target length |
| --- | --- | --- |
| I. Introduction | State the control question, literature gap, and three outcomes | 0.9--1.2 pages |
| II. Model and analytical results | Define the conserved budget; state the finite-mode theorem and weak-`B` cusp transfer | 2.0--2.5 pages |
| III. Broad four-slab realization in physical `d=2` | Connect the finite-table `B\downarrow0` design seeds to the same-budget one-/two-/three-mode finite-`B` controls | 2.0--2.5 pages |
| IV. Continuum and independent validation | Give mesh/alignment/box limits, uncertainty, and off-lattice or other independent killed-process comparison | 1.2--1.8 pages |
| V. Discussion | Explain the mechanism, scoped generality, and actual limits | 0.7--1.0 pages |

Recommended section and subsection headings:

1. `Introduction`
2. `Model and analytical results`
   - `Conserved-reactivity encounter model`
   - `Constructive finite-mode theorem`
   - `Weak-reaction transfer and cusp criterion`
3. `A broad four-slab realization in two dimensions`
   - `Exact free-exposure design`
   - `Finite-budget one-, two-, and three-mode realization`
4. `Continuum and independent validation`
   - `Mesh, alignment, and box convergence`
   - `Independent unbounded killed-process calculation`
5. `Discussion`

The logic should be theorem -> same-family exact design -> same-family
finite-`B` control geometry -> physical validation. Do not organize the final
paper chronologically by internal calculation name.

### Page-count staging and promotion boundary

Before the C0-A migration, the theorem-first PDF had six physical pages:
approximately five pages of body plus references.  It was an intentional
compact analytical skeleton, not a completed Regular Article or a rendering
defect.  The current seven-page PDF adds only the proved physical quotient,
natural-decay realization, positive-time observable bounds, and mass identity;
it keeps the complete C0 and C1--C3/root-transfer gates open.  Further page
growth remains tied to accepted scientific content rather than to moving audit
ledger material or superseded plots back into the main text:

A fresh fail-closed build on 2026-07-15 produced seven main physical pages and
23 Supplemental pages in two byte-identical isolated rebuilds, with zero
overfull boxes and no undefined references or citations.  Page-by-page
rendering of the main PDF showed no clipping, overlap, broken column, or
accidental blank page: page 6 completes the discussion and begins the
references, and page 7 contains the final references with expected unused
space.  That space will disappear naturally when accepted result content is
migrated; it is not a reason to import unaccepted material.

| Accepted stage | Honest main-body target | What may be added |
| --- | ---: | --- |
| pre-C0-A exact-`m` skeleton | about 5 pages | theorem spine, mechanism, evidence boundary |
| reader-facing C0-A migration (current) | about 6 pages | exact quotient and operator-realization proposition, explicitly not finite-volume convergence |
| complete independently accepted F0 | 7.5--8.5 pages | contact killing, full-operator/uniformization method, reproducibility boundary; no positive-budget result |
| accepted F1 and F3 | 8.5--10 pages | same-budget one/two/three-mode results, full configuration envelope, independent common-observable validation |
| accepted C1--C3/root transfer | 10--11 pages | computable continuum error composition and continuum root transfer |

Without C1--C3, the final wording remains `continuum-consistent numerical
evidence`; it must not become `continuum verified`.  The historical
`B=0.01` plots, one-grid fold, allocation-v6 ledger, and internal PASS/HOLD
tables do not count as honest page growth.

## 3. Exact disposition map for the current TeX

### Front matter and abstract

| Current anchor | Action | Destination or replacement |
| --- | --- | --- |
| Lines 1--3 | Keep only as non-rendered source-development comments until the final release; remove before archival source deposit | Never render internal submission status |
| Lines 21--24 and 43--44 | Replace after the scientific branch is resolved | Use one of the conditional titles in Sec. 8 below; metadata and visible title must match exactly |
| Line 38, `\status` macro | Delete from the submission source once all usages are removed | Scientific scope is conveyed in prose, equations, estimates, and uncertainty, not badges |
| Lines 54--80 | Replace in full | Use the outcome-first template in Sec. 7; do not edit it piecemeal |

### Introduction

| Current anchor | Action | Destination or replacement |
| --- | --- | --- |
| Lines 86--97 | Keep and compress | One opening paragraph: multimodal first-passage/reaction laws exist; the unresolved question is modality control by redistributing a conserved reactivity resource |
| Lines 99--113 | Keep and sharpen | One gap paragraph distinguishing transient timing-modality control from heterogeneous absorption, steady-flux optimization, and encounter-history theory |
| Lines 115--121 | Remove entirely from reader-facing paper | The evidence ontology is internal QA, not scientific exposition |
| Lines 123--130 | Split | Put normal citations and one precise non-overlap sentence in the Introduction; put the detailed companion-work overlap disclosure in the cover letter and Supplemental provenance note |
| Lines 131--139, displayed project chain | Replace | Three short outcome paragraphs or a single contribution paragraph; do not use a workflow diagram as a result |
| Lines 141--147 | Keep, but compress to two sentences | State the every-fixed-finite-`d>=2`, fixed-finite-`m` theorem scope and that the resolved finite-parameter realization is restricted to physical `d=2` |

The Introduction should end with three actual results, in this order:

1. a constructive fixed-finite-mode theorem in the exact slab quotient for every fixed finite integer `d>=2`;
2. an `O(B)` mixed-jet transfer and a model-specific cusp determinant under the
   conserved budget; and
3. **conditionally**, a converged and independently validated positive-`B`
   cusp/trimodal region in one broad physical-`d=2` family.

If item 3 is not obtained, the Introduction and title must switch to the
theorem-first fallback route rather than implying cusp control.

### Model and analytical results

| Current anchor | Action | Destination or replacement |
| --- | --- | --- |
| Lines 149--187 | Keep in main, lightly compress | This is the physical invariant of the paper: fixed transport/supports and `\int \kappa=B`; retain the mass-balance identity |
| Lines 189--210 | Move out of main | Put the GIG lemma and screens in Supplemental Sec. S1, or reduce to one ancestry sentence with a companion citation in the Introduction |
| Lines 213--246 | Compress in main; move derivation to supplement | State the budget-tangent projected response and minimum-norm formula; move the full Duhamel derivation to Supplemental Sec. S2 |
| Lines 248--278 | Keep the definitions needed for the finite-`B` phase diagram | Retain fold/cusp conditions, projected rank, and the need for a remote pair; omit generic catastrophe exposition |
| Lines 283--311 | Move most derivation to supplement | Main text should state that exact state/control sensitivities include direct observable terms; Supplemental Sec. S2 carries the PDE hierarchy |
| Lines 313--346 | Keep as a named theorem, but compress the proof constants | Main statement: `f_B/B` converges to the exact free-exposure law in the required compact positive-time mixed jet with `O(B)` error; full complex-tube bound goes to Supplemental Sec. S3 |
| Lines 348--363 | Main theorem hypothesis in one sentence; full functional analysis to supplement | Preserve the unbounded weighted-space scope because it connects the theorem to the physical cylinder |
| Lines 365--415 | Keep a concise persistence corollary | State the contraction displacement, quartic nondegeneracy, and projected-rank preservation; full norm bookkeeping goes to Supplemental Sec. S3 |
| Lines 417--446 | Keep in main | The Wronskian-like determinant and identity in Eq. (current `cuspdetidentity`) are the model-specific analytical design criterion |
| Lines 448--453 | Rewrite as a normal limitation paragraph in Discussion | Remove references to pilots and project gates |
| Lines 455--542 | Compress to setup plus theorem statement | Main text needs the OU midpoint, normalized slab family, contact-interior condition, and separated-clock limit; detailed initial-covariance and tail derivations go to Supplemental Sec. S4 |
| Lines 543--553 | Replace prominently by accepted Theorem 1 | State: each prescribed fixed finite `m`, an `m`-dependent family, exactly `m` maxima and `m-1` minima on the declared compact window, first fixed small `epsilon`, then small positive `B`; cite the full posterior-sector proof in the supplement |
| Lines 555--567 | Reduce to a proof sketch of one paragraph | Full proof and uniformity details move to Supplemental Sec. S4 |
| Lines 569--580 | Keep in main as theorem scope | Preserve the absence of an absolute event-mass floor, exact global count, fixed geometry across `d` or `m`, uniform-in-`d`/`m` bounds, a `d -> infinity` limit, or interchangeable limits |
| Lines 582--587 | Move to Supplemental Sec. S1 or delete | The GIG-to-Doi non-universality is not part of the focused result spine |

The main article should name only two analytical results:

- **Theorem 1 (constructive finite-mode existence).** The scoped statement for
  every fixed finite integer `d>=2` and fixed finite `m`, with no
  uniform-in-`d` claim.
- **Theorem 2 / Corollary (weak-reaction jet transfer).** The `O(B)` mixed-jet
  result plus explicit fold/cusp persistence conditions and the conserved-
  simplex determinant identity.

Avoid presenting elementary projected linear algebra or generic fold/cusp
normal forms as separate novelty claims.

### Numerical realization and validation

| Current anchor | Action | Destination or replacement |
| --- | --- | --- |
| Lines 589--624 | Keep and compress in main | Define the exact physical-`d=2` quotient, true disk contact, longitudinal slabs, and the conserved full centre-space budget |
| Lines 626--639 | Remove G1 framing from main | Replace with the broad-family physical parameters and a neutral description of the numerical domain; box effects belong in Sec. IV |
| Lines 641--720 | Move to Supplemental Sec. S5 | This narrow half-width-`0.008` exact-kernel chain is not the family used for finite-`B` validation; current Fig. 1 becomes Fig. S1 |
| Lines 722--776 | Reduce to one main-text sentence or move fully to Supplemental Sec. S6 | The exact `d=3` sphere-kernel calculation supports dimension-correct analytical breadth only; it is not the finite-budget result |
| Lines 777--792, current Fig. 2 | Move to Supplemental Fig. S2 by default | Elevate only after a separately justified same-allocation or positive-`B` `d=3` result; otherwise it distracts from the focused physical-`d=2` chain |
| Lines 794--810 | Retain only as historical design context | Replace the old cusp seed by the accepted exact-rational modal-selector controls and their honest finite-table scope |
| Lines 812--860 | Remove from submission main text | Put the negative three-slab search, smoke tests, and derivative wiggle in the reproducibility archive; include in Supplemental Sec. S8 only if needed to explain a method choice |
| Lines 861--907 | Remove from focused main text | The separate three-slab `B=0.6` fold is not on the broad-family continuation; retain in archive or a clearly historical supplemental subsection |
| Lines 908--919, current Fig. 3 | Remove from focused main figures | Archive or Supplemental Fig. S3; do not use it to support the new fixed-control topology claim |
| Lines 921--926 | Replace with achieved results | A final paper reports the accepted one-/two-/three-mode controls and independent validation, not a list of calculations still required |
| Lines 928--964 | Delete in full from reader-facing manuscript | The gate ledger remains an internal release artifact; if useful, replace it with a quantitative result table containing values and uncertainty, never PASS/NOT RUN labels |
| Lines 966--996 | Rewrite in full around the one-family mechanism | Keep only the theorem's scientifically meaningful limits; remove calculation history and next-work workflow |
| Lines 998--1002 | Fill before submission | No `pending` language in the archival article |
| Lines 1004--1075 | Move to Supplemental Sec. S4 | Retain a one-paragraph proof sketch in main; the full tail/localization estimates belong in Supplemental Material |

## 4. Main-figure contract

### Figure 1: geometry, conserved budget, and exact design seed

Create a new broad-family figure; do not repurpose the current narrow-family
Fig. 1 without recomputation.

- (a) physical two-particle geometry, true disk contact, midpoint coordinate,
  and four longitudinal catalyst slabs;
- (b) conserved-budget allocation: fixed supports and fixed sum of integrated
  slab strengths;
- (c) exact broad-family free-exposure channels and the three normalized
  finite-table-selected mixtures used only as pre-positive-`B` design seeds.

The caption must say `B\downarrow0 normalized free-exposure limit`, not
`reaction-time density at B=0`. It should report the broad support widths and
must not include audit provenance vocabulary.

### Figure 2: decisive same-budget modality control

This is mandatory for the active theorem-first physical-2D route.

- (a) show the three exact-rational allocations on the same four-support
  budget simplex (or as one compact allocation matrix), with every transport,
  geometry, support, contact, and budget parameter visibly shared;
- (b--d) show the independently accepted all-configuration one-, two-, and
  three-maximum finite-`B` curves with certified root intervals, not a sampled
  sign screen;
- report valley-partitioned event masses and the common-window contrasts used
  by the off-lattice comparison, with uncertainty;
- state the declared finite window and do not infer a cusp, fold manifold, or
  global phase diagram from the three fixed controls.

The terminal allocation-v6 cusp and the unrelated G1d fold are archival
context and do not enter this figure.

### Figure 3: convergence and independent physical validation

- (a) retained root times, valley ratios, and basin masses versus mesh/alignment
  level with conservative continuum estimates;
- (b) changes under the midpoint, relative, and combined box enlargements;
- (c) finite-volume density/survival against the independent unbounded killed-
  process calculation at unchanged physical inputs;
- (d) cross-method differences with uncertainty bands and the predeclared
  scientific margins.

Do not use Boolean gate graphics. Plot estimates, error bars, thresholds, and
the amount of margin directly.

### Optional Figure 4

Only if it materially clarifies the analytical result, add a compact schematic
of the separated-clock construction for arbitrary fixed finite `m`. The
current `d=2/d=3` exact-kernel comparison remains supplemental under the
focused physical-`d=2` route.

## 5. Reader-facing quantitative table

If a table is retained, it should summarize the **same frozen physical-`d=2`
family and budget** only:

| Quantity | one-mode control | two-mode control | three-mode control | independent event law |
| --- | --- | --- | --- | --- |
| exact allocation ratios | values | values | values | unchanged inputs |
| certified roots/curvatures | one maximum | two maxima/one minimum | three maxima/two minima | common-window contrasts only |
| all-grid deterministic envelope | value plus bound | value plus bound | value plus bound | compatibility allowance |
| basin masses and survival | values plus error | values plus error | values plus error | simultaneous confidence intervals |

This replaces the current gate ledger. It must not mix the narrow family, G1d,
or `d=3` values into the same numerical column.

## 6. Claim-scope table

This table is an authoring constraint. It need not appear verbatim in the paper.

| Evidence class | Defensible final claim | Required qualifier | Prohibited promotion |
| --- | --- | --- | --- |
| Constructive theorem | For every fixed finite integer `d>=2` and every prescribed fixed finite `m`, a `d`- and `m`-dependent exact Doi slab family has exactly `m` nondegenerate maxima and `m-1` nondegenerate minima on the declared compact window after first fixing small `epsilon` and then small positive `B` | Geometry and admissible small parameters may depend on `d,m`; contact-interior and monotone-path hypotheses; no uniform-in-`d`/`m`, useful `B0`, or mass-floor claim | One fixed geometry has arbitrarily many modes; exact topology outside the declared window; uniform-in-`d`, `d -> infinity`, cross-dimensional budget/amplitude, uniform-`m`, or interchangeable-limit claim |
| Weak-`B` theorem | The budget-normalized Doi mixed jet differs from free exposure by `O(B)` on compact positive times, and explicit contraction/rank margins transfer folds/cusps locally | The analytical small-`B` threshold is not automatically a certificate at the numerical `B` | Calling the exact free-exposure cusp a finite-budget Doi cusp without continuation |
| Broad physical-`d=2` `B\downarrow0` calculation | The exact normalized free-exposure kernel has the reported cusp and selected five-root shape | Leading normalized object; separately selected broad supports; numerical root window stated | Positive event mass; killed-process law at `B=0`; finite-`B` phase diagram; unbounded positive-`B` validation |
| Broad physical-`d=2` positive-`B` point, if it passes | The unchanged broad allocation has at least three event-mass-qualified modes on the declared window on the tested discretizations | State box, meshes, root window, uncertainty, and that one point is not a cusp | Exact global trimodality; continuum/unbounded claim from two odd meshes; allocation-control cusp |
| Frozen same-budget physical-`d=2` controls, if completed | Three pre-F1 allocations have respectively exactly one, two, and three maxima on the declared finite window in every required FV configuration | Result-informed family; exact controls held out only from their own first positive-`B` evaluation; complete interval roots and all-grid envelope | A cusp, phase diagram, blind family-level discovery, or a topology claim outside the declared window |
| Continuum/independent validation, if completed | The selected positive-`B` topology, survival, and basin masses persist under mesh/alignment/box limits and a physically distinct unbounded killed-process method | Report estimates and uncertainties; independent Monte Carlo does not validate fourth derivatives by itself | Calling repeated runs, alternative quadrature of the same kernel, or CSR checks an independent physical solver |
| Physical `d=3` | The constructive theorem holds in `d=3`; a separately selected exact sphere free-kernel design has the reported `B\downarrow0` topology | Separate allocation; normalized free exposure only | One allocation robust across dimensions; finite-budget `d=3` modality; symmetric `d=2/d=3` headline without positive-`B` `d=3` validation |

## 7. Outcome-first abstract template

The final abstract should be 170--210 words and should not narrate the audit or
calculation history. Fill every angle-bracket placeholder from the released
artifact; delete conditional sentences whose evidence is absent.

> Redistributing a fixed amount of spatial reactivity can reorganize the timing
> of two-particle encounter reactions without changing transport, contact
> geometry, the initial law, or catalyst supports. We formulate this control
> problem for a Doi encounter process. For every fixed finite `d>=2` and
> prescribed fixed finite `m`, ordered narrow reactive slabs placed along a
> monotone transport trajectory generate exactly `m` nondegenerate maxima and
> `m-1` nondegenerate minima on a declared compact window after sequential
> small-noise and weak-reactivity limits. A compact-positive-time mixed-jet
> estimate transfers
> the strict topology margins from free exposure to positive budget. In a
> physical two-dimensional realization at one installed budget
> `B=<B_PLUS>`, three prospectively fixed allocation vectors produce one, two,
> and three certified finite-window maxima across all mesh, parity, alignment,
> and box challenges. A separately powered off-lattice calculation uses the
> same basin cuts and time windows and agrees within `<CROSS_METHOD_MARGIN>`,
> with basin probabilities `<MASS_RANGE_WITH_UNCERTAINTY>`. Thus a conserved
> spatial resource acts as a constructive coordinate for encounter-time
> topology.

Conditional rules:

- Use `exactly m` only with the fixed-finite, compact-window, sequential-limit
  qualifiers accepted by Rounds 118 and 120; do not extend it outside the
  declared window or imply a useful uniform budget threshold.
- Use the physical-2D realization sentence only after all 36 F1 rows and the
  independent F3 event-law gate pass.  A partial grid set or FV-only pass does
  not license `resolved` or `independently validated`.
- Keep `d=3` confined to the theorem sentence unless positive-`B`, converged,
  independently validated `d=3` evidence is later completed.
- Report event masses as basin probabilities with uncertainty. Do not call the
  internal `0.005` robustness floor an experimental observability threshold.

## 8. Conditional title options

### After exact topology, all-grid F1, and independent F3 pass

Preferred:

1. **Multimodal encounter times from conserved spatial reactivity: constructive theory and a two-dimensional realization**
2. **Conserved-reactivity control of encounter-time topology**
3. **Spatial reactivity allocation controls multimodal encounter times**

Use title 2 or 3 only if all-grid and independent-process evidence justify the
unqualified finite-budget verb `controls`.  Do not put `cusp control`, `phase
diagram`, or `catastrophe` in the title; allocation-v6 is a terminal negative
branch.

### Only the exact free-exposure design survives

Use an explicitly leading-order title such as:

**Free-exposure design of encounter-time modality under conserved reactivity**

This is not a finite-budget reaction-time-control headline and is not the
focused physical-`d=2` route.

### Two/three-dimensional headline

Only after a separate positive-`B`, converged, independently validated `d=3`
result may the title say `in two and three dimensions`. The current exact sphere
kernel and `d=3` theorem do not license that finite-budget headline.

## 9. Remove the internal audit ontology from the submission

The following strings or concepts should not appear in the reader-facing title,
abstract, main text, captions, or conclusion:

- `internal status`, `not a submission claim`, `project gate`, `gate failed`,
  `PASS`, `NOT RUN`, `HOLD`, `SEND-2D`, `REDIRECT`;
- `Round`, `audit`, `G1a`, `G1b`, `G1c`, `G1d`, `post-G1c`, `held-out`;
- bracketed labels such as `[proved]`, `[discrete diagnostic]`, or
  `[implementation smoke pass]`;
- machine-readable flag names and counts of software gates;
- repeated `result-informed`, `frozen`, `predeclared`, and `not preregistered`
  caveats in every result paragraph and caption.

Transparent scientific provenance must remain, but in conventional form:

- replace `result-informed` with a precise statement of how the geometry was
  designed;
- replace repeated `frozen/predeclared` language with one Methods sentence:
  `The B\downarrow0 calculation was used to choose the design; all positive-B,
  convergence, and independent validations used the stated physical inputs
  without refitting.`;
- replace status badges with estimates, error bars, scope, and ordinary
  declarative sentences;
- move code hashes, manifests, selection traces, and negative-search history to
  Data Availability, Supplemental Methods, and the reproducibility archive.

## 10. Supplemental Material structure

1. **S1. Reduced-clock ancestry and non-overlap:** GIG lemma and only the
   calculations needed to delimit novelty.
2. **S2. Exact sensitivity hierarchy:** Duhamel formula, direct observable
   terms, budget projection, and derivative implementation.
3. **S3. Weak-`B` mixed-jet proof:** bounded and weighted unbounded spaces,
   Cauchy estimates, contraction, and Weyl-rank argument.
4. **S4. Constructive theorem proof:** full OU/wrapped-Gaussian hypotheses,
   contact tails, own-clock/cross-clock estimates, and sequential limits.
5. **S5. Narrow exact `d=2` kernel:** current Fig. 1 and quadrature checks,
   explicitly secondary to the broad family.
6. **S6. Exact `d=3` sphere kernel:** current Fig. 2, separate allocation, and
   representation cross-check.
7. **S7. Broad-family numerical methods and full convergence tables:** SG/FV
   details, contact quadrature, every mesh/box value, tail/root certificates,
   and uncertainty construction.
8. **S8. Selection and reproducibility provenance:** optional negative screens
   and the G1d diagnostic only if needed; otherwise leave these in the archival
   repository rather than burdening the submitted supplement.

## 11. Post-result rewrite branch

1. Preserve the old fixed-control `B=0.01` result and allocation-v6 HOLD as
   historical context; neither is promoted into the new evidentiary chain.
2. Preserve the independently accepted exact-`m` theorem and its fixed-finite,
   compact-window, sequential-limit scope in the main statement and supplement.
3. Only after the new F0, all 36 F1 rows, and powered F3 validation pass,
   expand and regenerate the dedicated theorem-first working source as one
   coherent finite-parameter paper.  Keep the historical TeX archived rather
   than accumulating another subsection and another gate row there.
4. If F1 or F3 holds, report the bounded result at its honest specialist scope
   and reassess journal fit; do not recover the cusp route or refit controls.
5. Regenerate all numerical macros, figures, source manifests, title metadata,
   PDF hashes, and Supplemental cross-references after the rewrite.

This architecture preserves all valid science while making the finite-parameter
claim legible: one conserved budget, one physical-`d=2` family, three fixed
allocations with distinct topology, and one independent event-law chain.
