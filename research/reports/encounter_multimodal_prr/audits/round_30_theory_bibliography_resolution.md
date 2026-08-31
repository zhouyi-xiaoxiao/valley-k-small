# Round 30: independent theory and bibliography resolution audit

Date: 2026-07-13  
Mode: independent acceptance audit of the final post-Round-29 repair snapshot  
Edit boundary: no TeX, bibliography, theorem note, code, result, metadata, or
figure artifact was edited. This audit file is the only repository file added
by the auditor.

## Verdict

**PASS for the Round 29 repair set.** All seven Round 29 findings are closed on
the final snapshot: **P0 = 0, P1 = 0, P2 = 0**.

The adversarial reread also tested two edge cases not explicit in the original
acceptance list: the impossibility of imposing a rank-two condition on a
one-control fold, and the nondegeneracy/positivity domain of the Gaussian
initial law. Both are explicitly resolved in the final source. No unresolved
repair-level finding remains.

This is **not** a scientific-release or submission PASS. The compile manifest
correctly remains `release_eligible=false`. Positive-budget event mass,
quantitative finite-`B` continuation of the four-slab shapes, interval/global
root certification, independent killed-PDE validation, finite-grid
mesh/box convergence, positive-`B` physical-`d=3` evidence, companion-work
disclosure, author metadata, and archival code/data identifiers remain open.

| Decision layer | P0 | P1 | P2 | Decision |
| --- | ---: | ---: | ---: | --- |
| Round 29 repair acceptance | 0 | 0 | 0 | **PASS** |
| Scientific/publication release | not encoded as repair counts |  |  | **HOLD** |

## Final snapshot audited

The hashes below were recomputed after the final clean build. Earlier
intermediate repair hashes are not the acceptance target.

| Item | SHA-256 |
| --- | --- |
| `manuscript/encounter_multimodal_prr.tex` | `ed29b1613572de107e321ac4f7bde5826d5929cd22431f572fae6ac366a725c0` |
| `manuscript/references.bib` | `f9564d51d9453e215ff3dc92744f325a7b3329603d99cfe06437963bd61b4fde` |
| `manuscript/encounter_multimodal_prr.pdf` | `48e8e048e8e6272ae3a0b5aba54525204ea127d968b664a08de9a6f1a106f063` |
| `artifacts/data/manuscript_compile.json` | `8db37ba75ab3014132da23a0aaa2bcb156648775ccaf1dec08939c10c958b5b0` |
| `audits/round_29_theory_bibliography_attack.md` | `c45e2e10c4848ebf9d6c7d4d1f8467184c4faa8c93d6cfa99442ad680e638a44` |
| `notes/pde_mixed_jet_theorem.md` | `3fc37bafc6320556322e80daa2c56bad9fd4b19e1856100caa8adf92341a8007` |
| `notes/direct_physical_multimode_theorem.md` | `7493499883ba41ce043c3535e1ca3d6c7a4c5de0cce9e575e261b4f8da9c2974` |
| `artifacts/figures/observable_four_patch.pdf` | `2e88f9278236f273c67901316a1cad9a4d92472ec9ea7f5ef64e0f4232641ad8` |
| `artifacts/figures/observable_four_patch_metadata.json` | `5efb61e03d6a266e1714fdf49311ddb8054a5bb28b735910f7648e4cfeccfa0e` |
| `artifacts/figures/d2_d3_four_patch.pdf` | `c5419173faf0626b3c97af5d20e7477739771a11d142f661ed22857cdac93ac6` |
| `artifacts/figures/d2_d3_four_patch_metadata.json` | `dcb43fff821442df9e4ec32de398b06cce175c5f2afd42bbdb8a433bf2a18aa9` |
| `artifacts/data/continuum_observable_four_patch_result.json` | `4a929cdaf915a9b6180acc0c272a16ae77087d097f2d078b6483c6c9b320a9fc` |
| `artifacts/data/continuum_observable_four_patch_d3_result.json` | `125234df2817287c30699d80e30af0e711c036193f0a64a404c8f3e98f98f984` |
| `notes/observable_four_patch_protocol.md` | `cbfb6fbe7b69fb66f3b25f7bcde404929a53cf1e8d2045c5fa037fe0fa8432a1` |
| `notes/observable_four_patch_d3_protocol.md` | `280a99653077e7d3ab4f7106d9f078a3588cd7f2ff3ae154f550d99dc47851f9` |

The compile manifest reproduces the TeX, bibliography, PDF, figure, figure
metadata, and transitive result/producer/test pins; it reports two
byte-identical clean PDF builds, zero missing files, zero overfull boxes, zero
undefined citations, and zero undefined references. Its build `status=PASS`
is explicitly scoped to build/PDF hygiene and does not override
`release_eligible=false`.

## Finding-by-finding acceptance tests

### P0.1 — Gaussian product initial law, independence, and
`pi_epsilon`: **CLOSED**

Acceptance evidence in TeX lines 457--515 and Appendix lines 1007--1028:

1. The theorem now fixes
   `D_0,gamma,W,rho,s_0,u_0>0`, `0<a<W/2`, and `z_0 != bar z` before using the
   Gaussian laws. This rules out the degenerate-normal edge case and makes the
   monotone midpoint path explicit.
2. It declares
   `Z_0 ~ N(z_0,epsilon^2 s_0^2)`,
   `R_parallel,0 ~ N(r_parallel,0,epsilon^2 u_0^2)`, and a transverse-torus
   wrapped Gaussian with covariance `epsilon^2 Sigma_perp,0`, where
   `Sigma_perp,0` is positive definite.
3. The midpoint initial variable, relative initial variables, quotient
   Brownian drivers, and midpoint driver are mutually independent.
4. For fixed positive `epsilon`, `pi_epsilon` is explicitly the product of the
   midpoint OU invariant Gaussian, longitudinal-relative OU invariant
   Gaussian, and uniform transverse-torus density.
5. The weighted-space thresholds are correct. For a Gaussian initial variance
   `v_0` and Gaussian invariant variance `v_infty`, the quadratic coefficient
   in `q_0^2/pi` is integrable exactly when `v_0 < 2 v_infty`. Substitution gives
   `s_0^2 < D_0/gamma` and `u_0^2 < 4D_0/gamma`. The wrapped Gaussian is square
   integrable against the uniform measure on the compact torus for every fixed
   positive `epsilon`.
6. The source explicitly limits the statement to fixed `epsilon`; it does not
   claim a weighted norm uniform as `epsilon -> 0`.
7. The declared product law and independent drivers are then invoked to make
   midpoint and relative motion independent, so the exact free-exposure
   channel factorization is justified inside the manuscript itself.
8. The Appendix now says "the declared Gaussian initial density," rather than
   relying on an unspecified variance-only class.

The manuscript-only acceptance test therefore passes without importing the
Markdown theorem note.

### P1.1 — regional Weyl rank condition and raw-response degeneration:
**CLOSED**

Acceptance evidence in TeX lines 365--415:

1. The contraction ball, its mapping-into-itself bounds, the unique zero in
   that ball, the displacement estimate, and invertibility of `DH_B(x_B)` are
   stated independently of the projected-rank paragraph.
2. The two-row matrix `R_B(x)` is defined by the two control-gradient rows in
   one frozen nondimensional time/tangent metric.
3. The rank hypothesis is regional:
   `s_* = inf_{x in U} sigma_2(R_0(x)) > 0` and
   `epsilon_R(B) = sup_{x in U} ||R_B(x)-R_0(x)||_2 < s_*`, with
   `U` the same closed contraction ball.
4. Weyl's inequality consequently gives the positive lower bound throughout
   `U`, explicitly including the displaced root `x_B`; no hidden comparison of
   matrices at different evaluation points remains.
5. The raw control response is explicitly `B R_B`, so normalized rank can
   persist while the absolute smallest singular value and event rate vanish as
   `B -> 0`.
6. The final source correctly limits `sigma_2(R_B)` to a cusp or another
   unfolding with at least two tangent controls. A one-control fold instead
   uses the contraction criterion and invertibility of `DH_B(x_B)` and is not
   assigned an impossible rank-two condition on a `2 x 1` response.

This last scope test matches the separate fold, cusp, and `J>=3` projected-rank
corollaries in `pde_mixed_jet_theorem.md`.

### P1.2 — Bressloff publisher record: **CLOSED**

The bibliography now uses the final publisher title
"Diffusion-mediated absorption by partially-reactive targets: Brownian
functionals and generalized propagators" together with *Journal of Physics A*
55, 205001 (2022), DOI
<https://doi.org/10.1088/1751-8121/ac5e75>. The title, author, journal, volume,
issue, article number, year, and DOI agree with the DOI/Crossref publisher
metadata. The preprint-title/final-DOI hybrid is gone.

### P2.1 — Ryu author metadata: **CLOSED**

Both entries now name **Seungoh Ryu**. The author strings and DOI metadata agree
with the APS records for
<https://doi.org/10.1103/PhysRevE.80.026109> and
<https://doi.org/10.1103/PhysRevLett.103.118701>.

### P2.2 — Ray--Lindsay support versus manuscript-specific determinant:
**CLOSED**

TeX lines 426--428 now say only that analytical modality criteria for finite
mixtures are classical, citing Ray--Lindsay, and immediately identify the
Wronskian-like determinant and conserved-simplex identity as specific to the
present encounter clocks. This is supported by the primary paper's ridgeline,
curvature, and modality analysis and no longer attributes the manuscript's
determinant to that source. Bibliographic metadata agree with
<https://doi.org/10.1214/009053605000000417>.

### P2.3 — human-readable figure vocabulary and provenance: **CLOSED**

The committed `observable_four_patch.pdf` was rendered with Poppler and
inspected at full resolution. Panel (c) is visibly titled "Frozen inward-step
scan" and its vertical label is "relative-shape ratio". The former positive
panel label "observability" is absent. Negative boundary wording such as "no
event-mass claim" remains appropriate.

The regenerated PDF/PNG hashes match the figure metadata. The plot-script hash
and all result, manifest, producer, protocol, and focused-test source pins also
match, and `manuscript_compile.json` pins the refreshed figure and metadata.
The focused figure suite completed **7 passed in 24.10 s**.

### P2.4 — fixed finite mode-count wording: **CLOSED**

The ambiguous phrase "bounded at-least-m statement" is gone. TeX line 584 now
uses "fixed-finite-`m`, at-least-`m` statement," which cannot be confused with
the spatial domain of the unbounded OU cylinder.

## Scientific-boundary audit of the new physical-d=2/d=3 comparison caption

**PASS; no caption overreach found.** The comparison was checked against both
result JSON files, protocols, metadata, the rendered standalone figure, and
the rendered manuscript page.

- The two result files have identical declared longitudinal/physical inputs:
  diffusion `0.002`, OU stiffness `0.1`, OU mean `0.95`, contact radius `0.16`,
  slab centres `(0.35,0.60,0.75,0.90)`, patch half-width `0.008`, initial
  half-width `0.004`, and transverse period `1`.
- Both use the same four-level frozen selection priority, while the caption
  correctly says that the selected allocations differ. The selected steps are
  `0.11` in `d=2` and `0.10` in `d=3`.
- Both saved results have five alternating roots and three maxima under the
  declared **relative-shape** gates. The caption's "qualified" is therefore
  tied to the immediately preceding peak-balance/valley-threshold sentence,
  not to absolute event mass.
- The reported `d=3` second-valley ratio is `0.8448001279484201`, leaving
  `0.005199872051579901` below the `0.85` ceiling, consistent with the printed
  `0.0052` robustness warning.
- Each curve is separately normalized only for shape comparison. The caption
  and visible figure footer say `B=0`, result-informed, relative-shape only,
  `continuum_verified=false`, `finite_B=false`, `independent_PDE=false`,
  `project=false`, and no event-mass observability claim.
- The caption explicitly disclaims positive event mass, finite-`B`
  persistence, an independent killed-PDE solve, and a project gate. The nearby
  prose also disclaims interval certification.

Thus the figure supports a dimension-to-dimension **shape comparison under
separately selected conserved allocations**, not a claim of one fixed control
being robust at positive budget across dimensions.

## Executed checks

1. Recomputed all snapshot and transitive figure-chain SHA-256 values.
2. Read the final TeX theorem, persistence criterion, Appendix, captions, and
   rendered bibliography against the theorem notes.
3. Checked the four affected DOI records using publisher/primary metadata.
4. Re-derived the Gaussian `L^2(pi_epsilon^{-1})` thresholds and the matrix
   dimensions of the fold/cusp projected responses.
5. Rendered both standalone figures with Poppler; inspected their visible
   labels, footers, and plotted thresholds.
6. Rendered manuscript pages 7--8; the labels, scope footers, and both captions
   are legible with no clipping or overlap.
7. Ran the two focused figure test modules with bytecode/cache writes disabled:
   **7 passed in 24.10 s**.
8. Verified the final compile manifest: byte-identical clean rebuilds, no
   missing files, no overfull boxes, no undefined citations/references, and
   `release_eligible=false`.

## Final decision

- **Round 30 repair resolution: PASS.** No P0/P1/P2 finding remains in the
  final audited snapshot.
- **Scientific and submission release: HOLD.** This audit closes only the
  Round 29 theory/bibliography/figure-language repair set; it does not promote
  the remaining numerical, continuum, event-mass, solver, disclosure, or
  metadata gates.
