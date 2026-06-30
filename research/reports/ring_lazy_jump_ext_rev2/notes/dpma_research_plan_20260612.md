# Double-peak mode attribution (DPMA) — research plan v1 (2026-06-12)

Status: plan finalized after one adversarial panel round (3 critics + 1
alternative-path designer) plus a primary-evidence geometry resolution.
Supervisor context: the t·α^t tail dispute is settled (tail = mode 1,
purely geometric); the new question is what controls the finite-time
double peak and which spectral terms matter.

## 0. The geometry resolution (supersedes part of the panel round)

Two distinct double-peak phenomena exist in the same model and were being
conflated:

- **Geometry A (start near the TARGET, rho small).** F(t) is monotone after
  its early peak; only the log-time density t·F(t) has a second hump. The
  hump is intrinsic to the confined ring (strongest at beta=0, contrast
  capped at ~1.05) and the shortcut only erases it. The panel verified this
  thoroughly; it is a shallow representation-dependent feature.
- **Geometry B (start near the SHORTCUT SOURCE; appendix C.2 geometry:
  paper sites n0=1..6, u=6, v=56, i.e. offset d=dist(n0,u), rho=L-d).**
  F(t) ITSELF has a strong two-route double peak: route 1 = captured by the
  shortcut at u (first peak, time scale ~d^2 + capture), route 2 = missed
  the shortcut, diffused the long way to v (second peak, time scale ~L^2).
  beta is CONSTRUCTIVE here (creates peak 1) and destructive at large
  values (drowns peak 2). Heights are O(0.1); h2/h1 in [0.1,10] per C.2.

The study object is Geometry B (it is what was sent to Luca and what
carries mass-scale structure); Geometry A is kept as a contrast subsection
reusing the panel's results.

**C.2 reproduction: PASS (6/6 rows exactly).** The C.2 classifier is now
pinned in code: classification acts on F(t) at integer t; strict local
maxima with t=1 admitted via F(0)=0; the tested pair is the FIRST TWO peaks
in time order; conditions: both peaks > 1e-12, secondary >= 1% of the
largest peak, separation >= 10 steps, h2/h1 in [0.1, 10], valley <= 0.8 *
min(pair). t_max = survival < 1e-13. The panel's "C.2 irreproducible"
finding was an artifact of testing Geometry A / t·F; no correction note to
Luca is needed.

### 0b. Classifier alignment with the repo canon (user directive 06-12)

Per the repo-wide inventory (research-conventions.md: no universal
double-peak definition exists; every report must DECLARE its classifier,
thresholds, and artifacts), this study emits THREE classifier layers per
cell, all on F(t):

1. `paper_bimodal` — vkcore `common.fpt_metrics.paper_style_bimodality`
   imported directly (h_min=1e-12, secondary >= 1% of largest, top-2 by
   height). The repo-core canonical gate.
2. `macro_bimodal` — jumpover-pipeline convention (h_min=1e-7, 1% filter,
   top-2 by height, timescale separation t2/t1 >= 10). The two-timescale
   gate; in Geometry B t2/t1 ~ O(L^2/d^2) >> 10 deep in the window.
3. `clear_double` (C.2 five-condition rule) — the report-historical anchor
   and the PRIMARY label source for this study (strictest; subsumes ratio,
   separation, height-balance and valley-depth conditions).

Vocabulary per research-conventions.md: `double_peak` iff clear_double;
otherwise `shoulder` when the valley fails (no real dip,
valley > 0.8*min(pair)) and `local_bump` for the remaining two-peak
structures; `single_peak` else. Continuous diagnostics (ratio_secondary,
h2/h1, valley_frac, t2/t1) are always recorded so thresholds can be
re-evaluated; threshold-sensitivity grids follow
sensitivity_thresholds.py conventions (h_min in {1e-8,1e-7,1e-6},
second_frac in {0.005,0.01,0.02}, t2/t1 in {8,10,12}, valley levels
{0.1,0.2,0.3} adapted to the C.2 0.8-of-min convention).

### 0c. Refined boundary laws (bisection scan, 2026-06-12)

> SUPERSEDED in part by the round-2 audit: the pi/pi*d identifications below
> were REFUTED by large-N extrapolation (binding-condition switch at N*(d);
> see dpma_final_report_20260612.md Law 4 for the corrected two-branch law).

From dpma_boundary_refined.csv (d in {3,4,5}, N up to 240, 14-step
bisection per edge):

- Upper edge collapse: pi_hi in [0.39, 0.43] across the entire plane,
  drifting slowly upward with N (0.392@N=44 -> 0.429@N=240, d=3) and
  nearly d-independent at fixed N. Working hypothesis: h2/h1 >= 0.1 is the
  binding condition with a slowly varying width ratio.
- Lower edge scaling law: pi_lo * N ~ c(d), c(3)~2.2, c(4)~2.9, c(5)~3.6
  (approximately linear in d). Binding condition to identify (h2/h1 <= 10
  vs valley condition) — record per-edge binding condition in the next
  scan iteration.
- Minimum system size: N_min(d) ~ 14 d (44/60/70 for d=3/4/5) below which
  no clear window exists at any beta.

## 1. Analytic layer (the "know in advance" deliverables) — status

1. **Capture-probability law (VERIFIED, machine precision):**
   pi_sc = rho/(a+L), a = q/(beta(1-q)) = N/b, b = beta(1-q)N/q.
   Route-mass split: peak 1 mass ~ pi_sc, peak 2 mass ~ 1-pi_sc.
   Derivation: renewal identity pi_sc = lam*G0(n0,u)/(1+lam*G0(u,u)) with
   the z=1 Chebyshev values G0(n0,u)=rho/q, G0(u,u)=L/q.
2. **Uniform spectral-shift law (VERIFIED numerically; to be re-verified at
   50 digits):** delta s_j = -beta(1-q)*2/N for every reflection-symmetric
   mode at first order (u is a common antinode, squared normalized
   amplitude exactly 2/N); antisymmetric modes frozen. Equivalent tilt
   form: F_beta(t) ~ F_0(t)*exp(-2 beta (1-q) t/N) at first order.
   Second order is mode-dependent (visible at b ~ O(1)).
3. **q-reduction lemma (to write up, 2 lines):** roots depend on (L, a) and
   a=N/b, so all structure lives in (N, d, b); q only rescales 1-s (time
   unit). Drop q from all scans; state results in b.
4. **Boundary collapse (pilot-VERIFIED, refinement running):** the clear
   double-peak window edges sit at nearly constant pi_sc across N and d
   (lower edge pi_sc ~ 0.01-0.05: the 1%-secondary condition; upper edge
   pi_sc ~ 0.32-0.41: the h2/h1 >= 0.1 condition). Inverting gives the
   analytic boundary prediction beta_pm(N,d) = q*pi_pm /((1-q)(rho - pi_pm*L)).
   To do: bisection-refined edges, pi_pm(N,d) drift quantification, width
   correction model.
5. **Exact hump time:** use t* = -1/ln(s_1) (not 1/(1-s_1)); closed form via
   the shift law.

## 2. The three figures (user's plan, upgraded per panel)

- **Fig 1 (phase/feature diagram).** Axes (N, b) per offset family
  (fixed d in {3,4,5}; plus a fixed-d/N family as robustness). Primary
  layer: continuous fields (ratio_secondary, h2/h1, valley_frac) as heat
  maps. Overlays: C.2 clear-classifier region (the observability region),
  the threshold-free fold locus (where valley+peak2 annihilate), the
  analytic beta_pm(N,d) curves from pi_sc, and the beta_c=2q/((1-q)N)
  reference line. Never called a phase transition: "fold/annihilation
  boundary of the secondary peak" + observability window.
- **Fig 2 (spectrum flow = theorem figure).** Parallel-lines law:
  N^2(1-s_k)/q vs b collapses to (2k-1)^2 pi^2/2 + 2b; plus
  uniformity-residual panel (the mode-dependent second order), interlacing
  brackets, and antisymmetric modes frozen at gamma_r. Numerical curves +
  first-order law overlay.
- **Fig 3 (amplitude flow + attribution).** B_j(b) flows (Chebyshev residue
  formula; delta B_j at O(1/a) to derive); feature-resolved attribution
  stack: (a) two-route split (capture wave vs around wave) as primary
  decomposition with masses pi_sc vs 1-pi_sc; (b) mode-1-vs-rest split at
  the three feature times; (c) truncation certificates k_eps(feature)
  (minimal top-K modes for 1% at t1, tv, t2); (d) sum-rule-projected
  leave-one-out only in an appendix with explicit caveats.

## 3. Answer shape for "which term contributes most"

- Tail and second peak: mode 1 alone (B_1 s_1^{t-1}; t* = -1/ln s_1) —
  already established, restated with truncation certificates.
- Valley: modes 1-2 (two-mode theory; panel verified to 4 decimals in
  geometry A; to re-verify in geometry B).
- First peak (capture wave): a coherent many-mode packet — k_eps measured;
  its MASS is the single closed-form number pi_sc = rho/(a+L); attribution
  by mode is the wrong language for it (sum-rule-constrained interference)
  and the two-route split is the canonical statement.
- Control parameter: everything collapses in b = beta(1-q)N/q.

## 4. Numerics protocol (per feasibility review)

- Engine: symmetric transient block eigh (optionally folded L x L
  symmetric-sector tridiagonal); Chebyshev-root cross-check with bracketed
  50-digit mpmath at spot points (anderson solver; secant stalls at L~150).
- Detection hygiene: integer-t evaluation to max(64, 8 d^2, parity
  horizon); strict maxima with t=1 boundary candidate; tie/plateau rules
  declared; first-two-peaks-in-time pair (C.2); survival cutoff 1e-13.
- Invariants per cell: mass balance |sum F + surv - 1| < 1e-9; F >= -1e-12;
  F(t<rho-ish) structure; closed-form-vs-eigh |dB| < 1e-8; B_1 > 0.
- Artifacts: tidy CSV + JSON manifest (classifier version, thresholds,
  grids) under artifacts/data/, figures under artifacts/figures/,
  deterministic; scripts in code/ (shortcut_double_peak_mode_attribution.py,
  dpma_phase_scan.py, dpma_boundary_refine.py).

## 5. Literature positioning (panel: do before writing)

Two-route bimodal first-passage is known phenomenology (Mattos,
Mejia-Monasterio, Metzler, Oshanin PRE 86, 031143 (2012) "direct vs
indirect"; Godec & Metzler PRX 6, 041037 (2016); Grebenkov et al.).
Our contribution: exact finite-N spectral control, a single closed-form
control parameter pi_sc = rho/(a+L) with a verified boundary collapse, the
uniform-shift/tilt spectral-response law, and the Montroll-defect Chebyshev
determinant D = a T_L + U_{L-1} as the unifying object.

## 6. Remaining work queue

1. boundary refinement scan (RUNNING) -> pi_pm(N,d) table + collapse fig
2. delta B_j first-order derivation + 50-digit verification of laws 1-3
3. two-mode/two-route reduced model for the fold locus; compare with data
4. full-grid scan with manifest; three figures; attribution tables
5. adversarial round 2 on RESULTS (play-Luca + methodology + numerics)
6. write-up note (EN, Luca-ready, letter style) + bilingual summary
7. reportctl summary refresh + handoff updates
