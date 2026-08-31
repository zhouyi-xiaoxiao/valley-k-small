# Round 10 — Reviewer B independent JCP referee report

## Recommendation in one sentence

**JCP: reject in the present form, with encouragement to resubmit only after a genuinely continuum-facing, independently validated spatial-fold calculation and a sharper chemical-physics realization. PRE: major revision, potentially publishable if it is explicitly repositioned as a finite-state/finite-grid mechanism paper.**

This recommendation is not driven by an algebraic error. I independently recovered the finite Green fixture, the GIG normalizer and modes, the finite-CTMC fold exponents, all three declared finite-grid fold exponents, the 2D/3D capacity fits, and the multidimensional GIG roots. The problem is that the only genuinely new chemical-physics object claimed by the paper—the fixed-transport spatial-reactivity density fold—has not yet been shown to survive the discretization used to discover it. The manuscript says this honestly, but honest limitation language does not substitute for the missing central result at JCP level.

## Review scope and independence

- I read the complete frozen 1,797-line TeX source and the complete 23-page PDF from the beginning, not only the abstract, figures, or prior issue lists.
- I rendered all 23 PDF pages to PNG, inspected three full-document contact sheets, and inspected pages containing the Green fixture, both updated fold/control figures, capacity figures, multidimensional design, provenance, and references at full page resolution.
- I inspected the numerical generators, the 2D/3D encounter operators, the morphology logic, the archived CSV/JSON/NPZ evidence, the executed reader notebook, the pipeline and child manifests, and the submission gate.
- I did **not** read any Round-10 Reviewer-A file and did not use the first nine rounds as an authority. I did not edit the scientific source or artifacts.
- At scientific-review seal, the frozen canonical full run is `20260711T080604670455Z-44227`: all 16 expected stages returned zero, including the 18-cell executed reader notebook and manuscript compile. Independent current-byte checks gave `source_files ok=85 bad=0`, `formal_evidence ok=4 bad=0`, and `outputs ok=100 bad=0`. The canonical PDF hash is `a1b66517b24575a4a77e8a6815955532cf45a9a27b1c41f05edb8a224f7add06`; all 23 newly rendered page PNGs were pixel-identical to my immediately pre-run inspection. This was deliberately a dirty, non-release development run (`release.requested=false`, `start_gate_passed=false`, no exact tag).

## Overall scientific assessment

The paper is unusually careful about claim boundaries. The coordinate transform, mass balance, finite-volume-reaction Woodbury identity, fixed-shape mixture fold condition, and generic fold normal form are correct under the stated hypotheses. The finite four-state dark-mode/pole/residue example is also correct. The exact finite-CTMC fold is numerically convincing, although its minority-channel splitting probability, $8.95\times10^{-6}$, makes it a mathematical mechanism certificate rather than an observable two-stream chemical prediction. The translation-invariant 2D and 3D capacity benchmarks are strong numerical unit tests. The free-space multidimensional GIG construction also does what it says.

The central 2D evidence is qualitatively different. The five-grid matched endpoint comparison is **not a transition in the mathematical number of modes**: patterned and homogeneous densities both have two strict maxima on every grid. It is a resolution-class change under a declared 3% classifier, albeit one strengthened by a nonempty 1.81–4.58% cross-grid separating interval and persistence under the control-volume rematch. The separate M2D-F family does have exact finite-matrix folds, but their control coordinates are grossly nonconverged and highly sensitive to the grid measure used to define the budget. The upwind transport grids operate at cell Péclet numbers far from the continuum regime, and the binary contact/patch masks are only a few cells wide. In the trimodal family each catalyst patch is smaller than one longitudinal grid spacing on all four reported grids and is represented by as few as two reactive product states. These facts make the results useful discrete mechanisms, but not yet a JCP-quality prediction for the declared Doi SDE/PDE.

The novelty positioning is commendably narrow. My targeted literature search did not reveal an obvious prior paper containing the exact same fixed-transport, fixed-spatial-reactivity-budget *density-fold* experiment. However, essentially every ingredient surrounding that increment—multimodal first passage, channel mixtures, heterogeneous reactivity, fixed-total-reactivity design, Green reductions, GIG clocks, and capacity scaling—is already established and is acknowledged as such. Therefore the paper's priority rests almost entirely on the spatial fold itself. A fold that moves by order unity under grid refinement or a natural quadrature change is not yet a sufficiently established increment for JCP.

## Findings by severity

### B0 — submission/release blockers

#### B0.1 — The scientific full proof is fresh, but there is no release proof

The frozen canonical full run `20260711T080604670455Z-44227` is fresh and internally hash-consistent: 16/16 stages pass, and I independently verified all 85 direct-source, four formal-evidence, and 100 output hashes. An earlier post-change full attempt correctly failed closed in the reader notebook, was repaired at the infrastructure layer, and was rerun from stage 1 rather than promoted; this is good behavior.

The first verify attempt, `20260711T081827250359Z-52352`, stopped at the audit-structure pytest after 124 tests passed and one failed because Round-08/10 resolution files were not yet complete. Lean was therefore not started, and there is not yet a canonical `publication_pipeline.verify.manifest.json`. This does **not** alter any scientific finding in this report; it is an audit-packaging/release hold.

More fundamentally, the passing full run started dirty, had no exact tag, and did not pass a release start gate. A clean source tag followed by `full --release`, a committed/tagged artifact snapshot, `verify --release`, a committed/tagged final proof snapshot, and the external proof checker remains mandatory before any package is called submission-ready. “16/16 PASS” proves the declared development commands completed and current bytes match; it does not establish an immutable release chain.

#### B0.2 — Author-owned metadata and public archive are unresolved

Every checkbox in `manuscript/SUBMISSION_METADATA_REQUIRED.md` remains open: final author metadata and ORCIDs, funding/grants, conflict of interest, CRediT, archival code/data DOI and license, and final release execution. The TeX deliberately retains TODOs for provenance, funding, and the data DOI. These are appropriate safeguards, but they are hard submission blockers.

#### B0.3 — The advertised top-level inventory is not yet fully transitive

`build_report.py` imports `vkcore.fpt`, and its child/legacy manifest correctly lists `packages/vkcore/src/vkcore/fpt.py` as a dependency. The top-level `_source_inventory()` in `run_publication_pipeline.py`, however, enumerates `encounter.py`, `encounter2d.py`, `encounter3d.py`, `morphology.py`, `plotting.py`, and `provenance.py` but omits `fpt.py` (and the executed package `__init__.py`). The external proof checker verifies the current bytes of the rows it is given but does not recursively re-hash dependencies named inside the child manifest. Thus the direct current-source inventory is not fully transitive. This is straightforward to repair and does not invalidate the successful frozen calculation, but it should be repaired before relying on the release proof.

### B1 — major scientific blockers

#### B1.1 — The robust five-grid endpoint result is a thresholded resolution change, not a modality change

The manuscript does disclose this point, but it remains central to journal fit. In `finite_radius_2d_matched_control.json`, the exact-semigroup audit finds two strict modes for both the patterned and homogeneous systems on all five grids. The patterned secondary/primary height ratios are 4.58–8.15%; the homogeneous ratios are 1.02–1.81%. The “resolved-bimodal versus resolved-unimodal” statement is created by a 3% classifier threshold, not by creation or destruction of a critical-point pair.

An independent threshold-only falsification gives:

| secondary-height threshold | patterned passing | homogeneous passing |
|---:|---:|---:|
| 1.0% | 5/5 | 5/5 |
| 1.5% | 5/5 | 3/5 |
| 2.0% | 5/5 | 0/5 |
| 3.0% (declared) | 5/5 | 0/5 |
| 5.0% | 4/5 | 0/5 |
| 8.0% | 1/5 | 0/5 |
| 10.0% | 0/5 | 0/5 |

The full classifier also uses prominence, lobe mass, valley depth, and persistence, so this table is not a replacement classifier. The final manuscript correctly identifies the nonempty cross-grid peak-height interval 1.81–4.58% within which all ten state-count endpoints separate, which is stronger than selecting 3% after inspecting a single grid. Even so, the headline contrast has no threshold-independent meaning. For a chemical-physics claim of “resolved modality,” the resolution rule needs an experimental/noise/detection rationale or an uncertainty analysis. Otherwise the mathematically precise statement is simply that patterning amplifies an already-existing second maximum.

The final product-control-volume rematch is nevertheless a useful positive robustness result. On all five grids the rematched homogeneous endpoint remains resolved-unimodal, has zero positive accepted views, and has a strict secondary/primary ratio of only 0.675–1.217%, while the unchanged patterned endpoint remains resolved-bimodal. This rules out the narrow falsification that the declared 3% endpoint contrast is solely an equal-boundary-node budget artifact. It does not turn the classifier transition into a strict critical-point transition, nor does it establish continuum convergence.

#### B1.2 — The reported 2D transport grids are far outside a controlled upwind continuum regime

The one-walker generator uses rates

\[
q_+=D/h^2+v/h,\qquad q_-=D/h^2.
\]

Its first Kramers–Moyal moments are the desired drift $v$ but an effective diffusion

\[
D_{\rm eff}=\frac{h^2}{2}(q_++q_-)=D+\frac{|v|h}{2}
=D\left(1+\frac{\mathrm{Pe}_h}{2}\right),
\qquad \mathrm{Pe}_h=|v|h/D.
\]

For the principal M2D-E grids, walker 1 has longitudinal $\mathrm{Pe}_h=9.0$ on $9\times5$ and 4.5 even on $17\times13$, so $D_{\rm eff}/D=5.5$ and 3.25, respectively. Walker 2 goes from $\mathrm{Pe}_h=3.125$ to 1.5625, so its ratio is still 2.56 to 1.78. The transverse upwind OU drift is worse: one grid node away from the centre on the finest $17\times13$ grid gives $\mathrm{Pe}_{h,y}=4.17$ for walker 1 and 13.02 for walker 2, corresponding locally to $D_{\rm eff}/D=3.08$ and 7.51.

These are legitimate finite-lattice jump processes, but they are not quantitatively resolved approximations of the SDE written in Sec. II. The observed folds and clock weights can therefore be controlled by numerical diffusion. Reporting several grids whose Péclet numbers remain $O(1\!-\!10)$ is not a continuum-convergence study. A positivity-preserving finite-volume/exponential-fitting scheme or a much finer relative/centre solver is needed, with convergence demonstrated at fixed physical $D,v,\gamma,a,\kappa$.

#### B1.3 — The spatial fold location is a grid- and budget-discretization quantity

The now-declared state-count M2D-F folds are

\[
\begin{array}{c|ccc}
\text{grid} & 9\times5 & 11\times7 & 13\times9\\ \hline
t_c & 16.8093321 & 18.0995323 & 16.5807587\\
\theta_c & 0.2753730 & 0.0138104 & 0.2558920
\end{array}
\]

Their derivative residuals and local $1/2,3/2$ exponents are excellent; the problem is the physical control. Before the $9\times5$ value was promoted into the canonical artifact, I independently solved it from three distinct initial guesses and obtained $(t_c,\theta_c)=(16.8093320824,0.2753729985)$, maximum residual $2.1\times10^{-17}$, $f_{ttt}=-1.34\times10^{-5}$, and $f_{t\theta}=1.67\times10^{-4}$. The final canonical number agrees. The odd-grid control sequence $(0.2754,0.0138,0.2559)$ spans 0.262 and has no converging trend.

The even grids make the topology less, not more, continuum-like. Both already possess a subthreshold strict second maximum at $\theta=0$. On $12\times8$ the nondegenerate continuation root is $(t_c,\theta_c)=(18.26877,-0.06158)$, outside the physical interval. On $10\times6$, the declared curvature-branch scan and four bounded least-squares starts find only a positive near miss, $f_t=3.8721\times10^{-6}$; this is bounded no-root evidence, not a root-count theorem. Thus a creation fold is not consistently located inside the declared physical path.

The fold also changes materially under a natural physical quadrature. The principal budget uses equal weight for every boundary node. Replacing only that measure by the tensor-product boundary-node trapezoidal/control-volume rule on the four-dimensional product domain, while retaining the same generator, masks, rates, and continuation, gives

\[
\begin{array}{c|ccc}
\text{grid} & 9\times5 & 11\times7 & 13\times9\\ \hline
\theta_c^{\rm cv} & 0.6244414 & 0.2407691 & 0.4593453
\end{array}
\]

All three weighted roots are physical and nondegenerate, but their controls span 0.384 and remain nonmonotone. The corresponding homogeneous rates are 1.8405, 2.5056, and 2.4062, compared with the exact boundary-clipped finite-$a$ continuum reference 2.2501572. The issue is therefore not root-finder failure; it is that the root describes the chosen finite operator and chosen budget measure. The paper needs a cell-averaged physical budget and a Cauchy/extrapolation study of the same fold branch on successively refined grids.

#### B1.4 — Contact and catalyst supports are not spatially resolved

Even in the finest matched endpoint grid, $a/h_x=2.08$ and $a/h_y=1.56$; the supports are binary node tests, not cell averages. The M2D-T trimodal family is more severe. Its patch radii are 0.06, 0.05, and 0.05, whereas $h_x=0.125,0.10,0.0833,0.0714$. Hence all three disks are smaller than one longitudinal spacing on every reported grid. The numbers of reactive product states per near/middle/far patch are:

| grid | reactive states |
|---|---:|
| $9\times5$ | 3 / 3 / 2 |
| $11\times7$ | 5 / 5 / 3 |
| $13\times9$ | 4 / 4 / 3 |
| $15\times11$ | 18 / 5 / 5 |

The nonmonotone counts are a direct aliasing diagnostic. The third maximum moves from 34.21 to 48.84 across the sequence. The four calculations convincingly show trimodality in four finite CTMCs, but they do not show persistence for one resolved continuum geometry. A cell-fraction sink and refinements with several cells across both $a$ and every patch radius are required before this can carry JCP weight.

#### B1.5 — The capacity checks do not validate the central modality discretization

I independently reproduced the capacity results: the 2D finest log-slope ratio is 0.98483 with $R^2=0.999961$; the 3D smallest-four-radius inverse-$a_{\rm eff}$ slope error is 0.1144%; the fixed-radius finest-pair difference is 0.0651%; and the smallest-radius reaction-limited 3D error is 0.0423%. These are good calculations.

They use different, translation-invariant relative-coordinate solvers with periodic cell-centred grids and cell-averaged targets. They therefore validate those solvers and the known capacity laws, not the boundary-node, binary-mask, high-Péclet, centre-patterned modality solver. They cannot be used as a surrogate convergence test for M2D-E/F/T. Likewise, the 3D section computes a mean time, not a six-dimensional centre-patterned reaction-time density.

#### B1.6 — The remaining novelty is not yet developed to JCP chemical-physics depth

The exact finite-CTMC fold is real, but its emerging channel has probability $8.95\times10^{-6}$ and prominence of order $10^{-13}$ near the reported continuation points. No dimensional mapping identifies a catalyst, reactant pair, length scale, time scale, intrinsic rate, or detection resolution for which the fold is observable. No independent Brownian-dynamics/FEM/finite-volume solver confirms it, and no matched Doi–Robin calculation checks reaction-model robustness.

Because the generic fold calculus, Woodbury reduction, GIG family, capacity asymptotics, multimodal first passage, and heterogeneous reaction are not new, the paper needs either (i) a converged continuum spatial fold with a predictive phase boundary, or (ii) a concrete chemical application in which the finite-state design makes a testable quantitative prediction. Without one of these, JCP would receive a careful assembly of known tools around an unresolved central calculation.

### B2 — significant issues that require revision

#### B2.1 — “Fixed integrated killing budget” needs a physically unique definition and robustness test

The declared nondimensional reaction model is internally unit-consistent: $D_i$ has units $L^2/T$, drift has $L/T$, transverse confinement has $1/T$, and the Doi volume-sink rate $kappa$ has $1/T$. The manuscript is also explicit that its principal budget is an unweighted statewise sum and not a stationary-exposure, pathwise-hazard, splitting-probability, or mean-lifetime match. That honesty is welcome. Nevertheless, the phrase “fixed integrated killing budget” appears in the abstract and novelty statement with a more physical sound than the finite grid measure warrants.

As a diagnostic, I computed the free-pair stationary exposure to the two endpoint fields. Although their unweighted state sums are exactly equal, patterned/homogeneous stationary-exposure ratios are only 0.328, 0.307, 0.330, 0.182, and 0.256 across the five grids. This is not an argument that stationary exposure *must* be held fixed—the purpose of patterning is precisely to reweight trajectories—but it shows that different plausible notions of “same amount of catalyst” and “same reactive opportunity” are far from equivalent. The paper should motivate a continuum catalyst-cost functional, discretize that functional consistently, and show which conclusions survive alternative defensible costs.

For the M2D-E endpoint, the final tensor-product trapezoidal/control-volume audit changes the finest matched homogeneous rate from 1.8491 (14.8% below the continuum reference) to 2.2064 (1.70% above it). This confirms that boundary-node weighting is not a small detail at the present resolutions, even though the resolved endpoint contrast itself survives this one-factor rematch on all five grids.

#### B2.2 — The endpoint contrast, fold, adverse controls, and trimodality live in different parameter families

M2D-E gives the five-grid resolution contrast; M2D-F gives the folds after changing $a$, drift, and starts; M2D-C gives nonfactorial controls; M2D-T gives trimodality after changing starts, drift, patch radii, and rates. The manuscript labels these families correctly, but the scientific narrative sometimes makes them feel like one evidence chain. They are separate existence examples. In particular, the robust M2D-E endpoint contrast does not show that the same path has a physical fold, and the M2D-C controls do not isolate one causal factor in M2D-E/F. JCP-level causal language requires a single registered physical family with matched one-factor continuations.

#### B2.3 — No independent numerical method checks the modality roots

Exact matrix-exponential derivatives remove time-grid differentiation error, but every bounded 2D conclusion still comes from the same generator construction, binary masks, and sparse exponential machinery. A second code path—Brownian dynamics with Doi reaction, finite-volume/FEM forward propagation, or an independently assembled relative/centre solver—is needed to separate mathematical roots from implementation-specific ones.

#### B2.4 — The manuscript is too broad relative to the strength of its central result

Twenty-three dense pages and twelve figures combine a synchronous discovery lattice, an independent-clock CTMC, finite Green spectral fixtures, GIG screening, two separate 2D bimodal families, coordinate sensitivity, controls, trimodality, 2D/3D capacity, and a four-dimensional GIG design. The breadth is impressive but dilutes the main claim. For JCP, capacity and free GIG design should become validation/supplement unless they are analytically connected to a converged spatial fold. For PRE, a focused finite-state modality-mechanism paper would be clearer.

### B3 — minor/presentation issues

- The frozen PDF is visually clean: 23 pages, 12 figures, no overfull boxes, missing files, undefined final citations, or undefined final references. The originally rendered literal `qquad` in Eq. (31) has been fixed and no longer appears in PDF text extraction.
- The PDF has blank title/author/subject/keyword metadata and is untagged. This is minor scientifically but should be addressed in the archival/submission package where possible.
- The source is explicitly `revtex4-2` with `aps,pre` options and the repository describes it as PRE-oriented. That is appropriate for the recommended route, but a genuine JCP submission should use the current AIP/JCP format and reorganize the manuscript to JCP expectations.
- The finite two-site Green fixture should state the single-walker jump rate (or print the walker generator) in the main text, because the quoted eigenvalues depend on that time scale.
- “Exactly five detected roots” should consistently remain “five sign-changing roots detected on the declared scan”; the manuscript mostly observes this distinction already. A global count would require interval or spectral-exponential root certification.

## Falsification attempts and outcomes

| attempted falsification | independent test | outcome |
|---|---|---|
| Frozen canonical artifacts are stale or tampered | Recomputed SHA-256 for every row in the final full manifest and compared the recompiled PDF against `manuscript_compile.json` | Not falsified: 85/85 direct sources, 4/4 formal records, and 100/100 outputs match; PDF hash is `a1b66517...f7add06`. |
| New fold/endpoint diagnostics propagate through the reader notebook | Inspected the first failed full attempt, reproduced the nested-object check, then inspected the infrastructure fix and fresh from-scratch run | Initially falsified by a `TypeError` in notebook cell 12; the attempt remained noncanonical. After the builder-only fix, the fresh full run executed 18 cells with zero errors and passed all 16 stages. |
| Verify evidence is already release-complete | Inspected the immutable verify attempt and stage log | Falsified as packaging only: 124 tests passed and one audit-structure test failed on missing Round-08/10 resolution; Lean did not start. No scientific artifact test failed, but no canonical verify/release proof exists yet. |
| Restricted Green fixture has a sign/order error | Rebuilt $L_0,T,U,K$ directly; tested dark mode, renewal determinant, and channel residues | Passed exactly: $U^Tv_{\rm dark}=0$, both eigen residuals zero, renewal matrix rank one at $-5/2$, residues $1/4,-1/4$ cancel. |
| GIG normalization or mode formula is wrong | Independent log-coordinate quadrature and analytic log-slope check for both declared channels | Relative normalization errors $2.55\times10^{-16}$ and $1.31\times10^{-16}$; mode log slopes zero. |
| Generic/finite fold exponents are regression artifacts | Refit archived held-out rows without using saved fit coefficients | Finite CTMC: 0.500954 and 1.508770. M2D-F on $9\times5$, $11\times7$, $13\times9$: $(0.498902,1.500051)$, $(0.493314,1.484297)$, $(0.499325,1.503854)$. Passed locally. |
| Exact tube volume or coordinate diffusion transform is wrong | Independent angular quadrature and covariance transform | Tube formula matched to machine precision for $a=0.13,0.17$; off-diagonal diffusion covariance $<2.5\times10^{-20}$, Jacobian 1. |
| The factorized M2D-F continuum budget reference is exact despite patch proximity to the wall | Compared patch clearance with $a/2$ and independently integrated the midpoint-feasible relative-disk cross-section | Initially falsified: clearances 0.070 and 0.080 are below $a/2=0.085$. The final source now uses the clipped value 2.2501572220; my independent quadrature agrees, and the former factorized value differs by only $2.13\times10^{-5}$ relatively. |
| 2D/3D capacity numbers are misreported | Refit all raw CSV rows | Reproduced every quoted slope/error to displayed precision. |
| Multidimensional GIG scan misses ordinary extra sign-changing roots | Reconstructed all 12 mixtures and scanned $t\in[10^{-8},10^{10}]$ on 300,001 log points | Found exactly $2m-1$ sign-changing roots in every case. This does not exclude even-multiplicity tangencies, as the paper correctly states. |
| Matched endpoints exhibit a strict modality change | Counted exact-semigroup stationary points on both sides and varied the height threshold | Falsified: both sides are strict bimodal on all five grids; only the resolution label changes. |
| The five-grid resolved endpoint contrast is an artifact of equal boundary-node budget weights | Rematched every homogeneous endpoint with tensor-product boundary control-volume weights and reran strict/multiscale morphology | Not falsified: all five rematched homogeneous endpoints remain resolved-unimodal with zero positive accepted views; the patterned endpoints remain resolved-bimodal. |
| The three M2D-F grids represent a converging physical branch | Independently solved the previously absent $9\times5$ fold from three guesses; examined the final three-grid artifact and even-grid topology controls | Falsified: odd-grid controls are 0.2754, 0.0138, 0.2559; the $12\times8$ root is at $\theta<0$, while the bounded $10\times6$ search only finds a positive near miss. |
| Fold is insensitive to the finite-grid budget measure | Replaced equal boundary-node weights by tensor-product boundary control-volume weights and resolved all three roots | Falsified: $\theta_c$ moved from $(0.2754,0.0138,0.2559)$ to $(0.6244,0.2408,0.4593)$. |
| Four trimodal grids resolve the same catalyst geometry | Compared patch radii to $h_x,h_y$, reactive-state counts, and exact root drift | Falsified as a convergence claim: patch radii remain below one $h_x$, counts are 2–18 and nonmonotone, late root shifts 34.2 to 48.8. Finite-grid existence itself remains valid. |
| PDF has clipping, overlap, missing graphics, or residual literal typo | Rendered all 23 pages; inspected three contact sheets and selected full pages; ran `pdftotext`, `pdfinfo` | Layout and figures passed; the one literal `qquad` defect was corrected during review. |
| Novelty is plainly pre-empted by a direct prior article | Targeted searches around spatial reactivity, fixed total reactivity, bimodal reaction-time density, and first-passage fold; checked the closest cited primary literature | No exact direct precursor found. Novelty is plausible but narrow; the evidence level, not obvious priority loss, drives rejection. |

## Actual commands and spot-checks

Representative commands actually run from the repository root included:

```bash
jq '{profile,execution,release,start_git,git}' \
  research/reports/encounter_heterogeneous_catalytic/artifacts/data/publication_pipeline.full.manifest.json

jq -r '.source_files[] | "\(.sha256)  \(.path)"' \
  research/reports/encounter_heterogeneous_catalytic/artifacts/data/publication_pipeline.full.manifest.json \
  | shasum -a 256 -c -
jq -r '.formal_evidence[] | "\(.sha256)  \(.path)"' \
  research/reports/encounter_heterogeneous_catalytic/artifacts/data/publication_pipeline.full.manifest.json \
  | shasum -a 256 -c -
jq -r '.outputs[] | "\(.sha256)  \(.path)"' \
  research/reports/encounter_heterogeneous_catalytic/artifacts/data/publication_pipeline.full.manifest.json \
  | shasum -a 256 -c -

jq '[.grids[] | {grid, theta:.fold.theta, scaling}]' \
  research/reports/encounter_heterogeneous_catalytic/artifacts/data/finite_radius_2d_fold_metrics.json
jq '[.[] | {nx,ny,homogeneous_strict_secondary_peak_ratio,
  product_trapezoidal_homogeneous_strict_secondary_peak_ratio}]' \
  research/reports/encounter_heterogeneous_catalytic/artifacts/data/finite_radius_2d_matched_control.json

pdftoppm -png -r 130 \
  research/reports/encounter_heterogeneous_catalytic/manuscript/encounter_modality_jcp.pdf \
  /tmp/pdfs/round10_b/canonical/page
pdfinfo research/reports/encounter_heterogeneous_catalytic/manuscript/encounter_modality_jcp.pdf
pdftotext -layout research/reports/encounter_heterogeneous_catalytic/manuscript/encounter_modality_jcp.pdf -
```

I also executed read-only `.venv/bin/python` heredocs for direct Green/GIG reconstruction, independent log--log regression, wide-range derivative-root scans, extra-grid and alternative-budget fold solves, threshold sweeps, capacity refits, and exact boundary-section quadrature. The frozen-data spot check returned M2D-F exponent pairs $(0.498902,1.500051)$, $(0.493314,1.484297)$, and $(0.499325,1.503854)$; the threshold counts printed in B1.1; all five control-volume homogeneous calls; and the support/root values in B1.4. I used `rg`, `nl -ba`, `jq`, `column`, `shasum`, and direct inspection of all archived CSV/JSON records and the executed notebook. I did not rerun artifact-writing validation scripts or modify any canonical artifact.

## Claim-versus-evidence matrix

| manuscript claim/layer | evidence I verified | referee disposition |
|---|---|---|
| Coordinate transform, unit Jacobian, diffusion decoupling, mass balance | Algebra and independent numerical covariance/tube-volume checks | **Supported.** Keep. |
| Volume-reaction restricted Green/Woodbury identity | Operator algebra plus exact four-state fixture | **Supported under stated bounded-volume hypotheses.** No continuum pole theorem follows, and the manuscript correctly withholds it. |
| Fixed-shape GIG law and fold determinant | Independent normalization, mode, derivative, and fold checks | **Supported as GIG algebra/screening.** Not a confined Doi approximation without a remainder. |
| Physical finite-CTMC fold with $1/2,3/2$ laws | Exact derivatives, residuals, held-out regression reproduced | **Supported for one finite chain.** Chemically weak because the minority channel is $8.95\times10^{-6}$. |
| Patterning changes M2D-E from unimodal to bimodal | Five-grid classifier, exact stationary points, cross-grid threshold interval, and five control-volume-rematched homogeneous endpoints | **Not supported as strict modality.** Supported as a resolution-class/amplification change that survives the two declared budget measures. |
| M2D-F spatial redistribution has a nondegenerate fold | Exact roots on all three declared odd grids, the out-of-domain $12\times8$ root, bounded $10\times6$ diagnostics, and three control-volume-budget roots | **Supported only for individual finite matrices.** Control location is nonconverged and measure-sensitive. |
| Midpoint/weighted-coordinate sensitivity | Mask distances and grid labels checked | **Supported as a warning.** It further demonstrates underresolution rather than continuum robustness. |
| M2D-C identifies the spatial mechanism | Separate controls and uniform counterexample checked | **Suggestive, not factorial causal proof.** Families differ in several parameters. |
| M2D-T gives bounded trimodality | Five alternating roots and channel dominance reproduced on four grids | **Supported as finite-CTMC existence.** Not a resolved-geometry or continuum result. |
| 2D logarithmic and 3D Newtonian/Doi capacity laws | Raw fits independently reproduced | **Strongly supported for the separate periodic mean-time solvers.** Does not validate centre-patterned modality. |
| $d=1,\ldots,4$, 2/3/4-mode GIG design | Reconstructed mixtures; wide-range scan recovered all reported roots | **Supported as abstract free-space GIG design.** Physical splitting-weight realization and bounded Doi extension remain open. |
| Reproducible submission package | Fresh 16/16 full development run, 18-cell notebook, compile record, and independent 85/4/100 current-byte audit | **Scientifically reproducible in the frozen workspace, but not release-ready.** Verify/audit packaging is incomplete, run is dirty/non-release, metadata/DOI are open, and the direct top inventory misses an executed dependency. |
| Novel JCP-level chemical-physics result | Literature boundary is careful; no direct precursor identified | **Not yet established at JCP level.** The unique increment lacks continuum/experimental validation. |

## What would change the JCP decision

This is not a request for more plots on the existing grids. A credible JCP resubmission should contain, at minimum:

1. A cell-averaged finite-volume/FEM or relative–centre solver for one fixed M2D family, with a physically defined continuum catalyst-cost functional.
2. Successive refinements for which cell Péclet numbers, $a/h$, and every patch-radius/$h$ ratio enter a controlled regime; report Cauchy errors for the density and its first three time derivatives near the fold.
3. Continuation of the **same fold branch** on at least four resolved grids, with a stable extrapolated $\theta_c$, error bar, and an independent solver or Brownian-dynamics validation.
4. A strict mathematical modality result on the same family, or an experimentally justified resolution/noise model if “resolved modality” remains the observable.
5. A cell-averaged refinement of the trimodal geometry if trimodality remains a main claim; the present 2–5-state patches are inadequate.
6. A dimensional chemical realization: plausible $D_i,v_i,a,\kappa_i$, catalyst dimensions, reaction-time window, and predicted measurement signature. A matched Doi–Robin comparison would materially strengthen reaction-model robustness.
7. A narrower manuscript in which capacity and multidimensional GIG material either derive a quantitative prediction for that fold or move to supplement.
8. The complete clean-tag full/verify release chain, transitive source inventory, archival DOI/license, and author-owned metadata.

## PRE versus JCP

### JCP

**Reject.** The required remedy is a new continuum calculation or a new chemical application, not ordinary revision of exposition. I would be open to a substantially new resubmission after the items above are completed. If the editorial vocabulary does not permit “reject and resubmit,” this is at least a major revision whose scope exceeds a normal revision cycle.

### PRE

**Major revision, potentially suitable.** PRE is a much better match for an exact finite-state modality-bifurcation/mechanism paper. The current work could be publishable there if it:

- makes the finite-lattice object, not the unresolved Doi continuum, the primary result;
- calls the M2D-E finding “secondary-mode amplification” or “resolution-class change,” not a strict modality change;
- retains the full $9\times5$, $11\times7$, $13\times9$ fold and budget-sensitivity evidence without presenting it as a converged continuum branch;
- quantifies the high-Péclet numerical-diffusion regime and does not call those grids a refinement toward the stated SDE;
- demotes the underresolved M2D-T and multidimensional GIG constructions to finite-grid/screening demonstrations; and
- completes the release and metadata gates.

That route preserves the genuinely solid parts—the exact Green/channel algebra, the finite-CTMC physical fold, the normal-form scaling, and the finite-state trimodal existence—without asking them to carry a chemical continuum claim they do not yet support.
