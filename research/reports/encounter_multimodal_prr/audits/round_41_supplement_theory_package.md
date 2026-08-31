# Round 41: Supplemental Material theory package

Date: 2026-07-13  
Scope: consolidate the report's sensitivity, weak-budget, and direct
fixed-finite-mode proofs into one self-contained PRR Supplemental Material
source  
Mutation boundary: additive only.  The main manuscript, theorem notes,
bibliography, formal sources, frozen positive-budget sources, and numerical
outputs were not edited.

## Verdict

**PASS for a self-contained, conventionally proved analytical supplement;
HOLD for formal-verification and scientific-release claims outside its stated
scope.**

The new source is
`manuscript/encounter_multimodal_prr_supplement.tex`.  It compiles as an
independent 11-page RevTeX document and puts the complete paper proof in one
reader-visible artifact rather than requiring a referee to reconstruct it from
Markdown notes.  The package does not claim a finite-parameter positive-budget
cusp, event-mass floor, numerical convergence, independent-solver agreement,
GIG-to-Doi universality, or Lean verification.

| Layer | P0 | P1 | P2 | Decision |
| --- | ---: | ---: | ---: | --- |
| mathematical statement/proof | 0 | 0 | 0 | PASS, scoped |
| proof self-containment | 0 | 0 | 0 | PASS |
| LaTeX/PDF build | 0 | 0 | 0 | PASS |
| formal verification | 0 | 1 | 0 | not Lean-verified |
| numerical/GIG supplemental modules | 0 | 0 | 0 | placeholders only; no claim |

## Source snapshot

| Source | SHA-256 | Role |
| --- | --- | --- |
| `manuscript/encounter_multimodal_prr_supplement.tex` | `23dd99b2e836eb6d1bfd90dc6e8cddaab955fb8725bc09d7436e5ef37e94446d` | new consolidated supplement |
| `notes/pde_mixed_jet_theorem.md` | `3fc37bafc6320556322e80daa2c56bad9fd4b19e1856100caa8adf92341a8007` | detailed sensitivity and weak-budget proof source |
| `notes/direct_physical_multimode_theorem.md` | `7493499883ba41ce043c3535e1ca3d6c7a4c5de0cce9e575e261b4f8da9c2974` | detailed direct-theorem proof source |
| `manuscript/references.bib` | `f9564d51d9453e215ff3dc92744f325a7b3329603d99cfe06437963bd61b4fde` | reused bibliography; not edited |
| `manuscript/encounter_multimodal_prr.tex` | `f3bf7cb11b7657bc65cdcbb3b9f7fcc15e3b799c072177d2daaeb738401c89ed` | main manuscript; not edited |

The new source has 1,035 lines, 3,755 words, and 39,497 bytes.

## Claim inventory

### S1: model and functional spaces

- Separates the exact bounded reflected quotient from the unbounded OU
  cylinder.
- Defines the conserved centre-space catalyst amount as `B`, rather than the
  configuration-space integral of the full killing field.
- States the bounded `L2` and unbounded
  `X_pi = L2(pi^{-1} dx)` density spaces and the corresponding weighted
  observable norm.
- Restricts all mixed time jets to one compact positive-time window.

### S2: exact sensitivity hierarchy

- Gives a frozen budget-tangent basis in a declared control metric.
- Derives the exact Duhamel first variation.
- Proves the all-finite-order affine-control state recursion
  `q_beta,t = A q_beta - B sum_i beta_i U_i q_{beta-e_i}`.
- Derives the general observable formula, including every direct observable
  derivative.  The displayed first- and second-order equations reproduce the
  required signs and multiplicities.
- States the safe generator-on-state time derivative and does not move the
  generator adjoint onto the discontinuous contact indicator.
- Records projected minimum-norm response as local constrained linear algebra,
  not global controllability.

### S3: weak-budget mixed jets

- Proves the bounded and unbounded analytic-semigroup realizations through the
  reversible similarity transform.
- States and proves the explicit compact-positive-time complex-tube estimate
  `F_B - G = O(B)` through every prescribed finite time/control mixed jet.
- Gives the analytic `n >= 2` Dyson-tail argument needed for an `O(B^2)` first-
  correction remainder through mixed jets.
- States mode-sign/curvature transfer, local contraction/displacement, and
  region-wise Weyl rank preservation in one frozen dimensionless metric.
- Explicitly excludes `t = 0`, `t = O(B^{-1})`, a finite event-mass floor, a
  certified finite `B`, global absence of extra roots, and numerical
  discretization error.

### S4: direct physical fixed-finite-mode theorem

- Quantifies the full mutually independent Gaussian/wrapped-Gaussian initial
  law and all Brownian drivers.
- Derives the midpoint and relative OU variances and states the strict weighted
  initial-law thresholds
  `s0^2 < D0/gamma` and `u0^2 < 4 D0/gamma`.
- States `0 < a < W/2`, positive-definite transverse covariance, distinct
  target times on a monotone midpoint path, and one fixed contact-interior
  margin on pairwise disjoint target neighborhoods.
- Proves the differentiated wrapped-Gaussian contact tail, own-channel `C2`
  local Gaussian limit, and cross-channel exponential bound.
- Displays the exact logical order
  `exists epsilon0; forall epsilon < epsilon0; exists B0(epsilon); forall B < B0(epsilon)`
  uniformly over a compact simplex-interior weight set.
- Concludes exactly one nondegenerate maximum in each named local interval and
  therefore at least the prescribed fixed finite number of modes.  It does not
  claim an exact global count or nondegenerate separator minima.
- Separates order-one free-exposure area from order-`B` Doi event mass and
  explicitly denies an absolute event-mass floor.

### S5-S6: evidence boundary and placeholders

- Labels the semigroup, Gaussian-tail, and nested-limit proofs as conventional
  human-audited mathematics, not Lean verification.
- Identifies the companion Lean modules as finite-algebra coverage only.
- Leaves reduced-clock/GIG ancestry and numerical evidence as explicit
  zero-claim placeholders.  No incomplete result or frozen numerical value is
  written into the supplement.

## Quantifier and hypothesis audit

| Attack | Outcome |
| --- | --- |
| one fixed geometry supports all `m` | denied; the family depends on fixed finite `m` |
| exact global number of modes equals `m` | denied; only named maxima and at least `m` are proved |
| epsilon and `B` limits commute | denied; epsilon is fixed before `B` |
| `B0` is uniform as epsilon tends to zero | denied |
| target times are arbitrary | excluded by monotone-path and contact-interior hypotheses |
| simplex boundary weights are allowed | excluded by a compact interior weight set |
| time jets hold at zero | excluded by `tau > 0` |
| long-time or global-tail control follows | denied |
| small-`B` theory supplies visible event mass | denied |
| arbitrary localized patches or arbitrary dimension | denied |
| direct observable terms may be omitted | explicitly contradicted by S2 |
| sharp contact indicator is differentiated spatially by adjoint transfer | not used |

## Compile and PDF hygiene

The LaTeX compile skill was run with TeX Live/`latexmk` in two fresh temporary
output directories with `SOURCE_DATE_EPOCH=1783900800`.  Both builds exited
zero and produced byte-identical PDFs:

- PDF SHA-256:
  `56d1f4593d43d8cd0037ef50cf712089df28625c8415bef05ac8c33d9b6581da`;
- pages: 11;
- media box: US Letter, `612 x 792` PDF points;
- encryption: none;
- PDF `Suspects`: no;
- fonts: every listed font embedded and subset;
- raster images: none;
- empty pages: none by extraction and visual review;
- undefined citations/references: none;
- overfull/underfull boxes: none;
- fatal LaTeX errors: none.

All 11 pages were rendered to PNG at 120 dpi and inspected.  The first visual
pass exposed four missing spacing-command backslashes (`qquad`/`quad`) that
were syntactically legal but reader-visible; they were repaired before the two
final clean builds.  The final pages have no clipped text, overlap, broken
glyphs, malformed equations, or table overflow.  The only remaining log
message is RevTeX/hyperref's harmless `nameref` warning that it restores the
kernel `label` definition; it does not leave an unresolved reference or affect
the rendered document.

No compiled PDF was published into the manuscript directory.  Compilation,
rendering, and extracted-text artifacts remain temporary QA products rather
than new release inputs.

## Frozen-chain boundary check

The positive-budget source hashes after this additive work remain:

| Frozen role | SHA-256 |
| --- | --- |
| external manifest anchor | `01b435c834cec9e7bfde2069b19fcdcaa4e06178ccfe0d4b6082f0705dfd5805` |
| producer | `0c70ffb4a9034772928e2fa95d2ca79ef33754e5aa4157a2f101e15cb312b003` |
| tests | `ee784d1cf6cc4e7ee66968deb8f3421394f697eebee3a50f783533aa469a8f78` |
| protocol | `f25a8107d7a975342a3b1cbbf84c29df26654a8f6310f0429cba5ffdf7bcda00` |

No positive-budget result, reproducibility record, replica, staging file, or
running process was read, edited, stopped, or restarted for this package.

## Final decision

- Supplemental theory consolidation: **PASS**.
- S2 sensitivity hierarchy: **PASS**.
- S3 weak-budget mixed-jet proof: **PASS, compact positive time and fixed
  finite jets only**.
- S4 fixed-finite-`m` OU/contact-tail proof: **PASS, physical `d=2,3` and
  sequential epsilon-then-`B` limits only**.
- Lean verification of S3-S4: **NOT PRESENT**.
- Numerical and GIG supplement content: **NOT CLAIMED / PLACEHOLDERS ONLY**.
- PRR scientific release: **unchanged HOLD**, because this proof package does
  not replace the same-family finite-parameter cusp, event-mass, convergence,
  and independent-solver gates.
