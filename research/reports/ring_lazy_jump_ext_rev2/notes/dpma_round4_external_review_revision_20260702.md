# DPMA round-4: external-review strategic revision + internal audit (2026-07-02)

An external review (ChatGPT, PDF-level; user-provided) of the 13pp version was assessed, largely
endorsed, and implemented; a fifth multi-agent internal audit round then verified the restructured
manuscript. Result: **14pp / 6 figures / 25 refs / two tables, 0 errors / 0 overfull / 0 undefined.**

## Assessment of the external review
Endorsed and implemented: the "above a predictable threshold" directional error (a genuine
contradiction with 0<b<b_c that all prior internal rounds missed); abstract overload → three-part
restructure with safer peak-definition and reversibility-scoped structural stability; weak-per-visit
scaling made explicit (λ = bq/N = O(1/N)); directedness-only-in-absorption stated in intro AND
abstract; **validation promoted to its own Sec IV ahead of the extensions**; contributions merged
5→4; notation table; 6-panel figure split into a fold figure (Fig. 2) and an extensions figure
(Fig. 6); `dpma_2d_universality.py` renamed `dpma_2d_finite_lattice.py`; phase-type (Neuts) and
Laguerre-rule (Pólya–Szegő) mathematical anchors — Laguerre's rule independently yields BOTH halves
of the minimal-mode theorem (double zero needs ≥3 terms with alternating signs); cover-letter draft
+ local reproducibility package (README/requirements/make_all/pytest identity tests, 5 tests pass).

Partially adopted: public repo + Zenodo DOI is prepared locally but **pushing is user-gated**.
Declined (documented in the cover-letter notes): title change (author-level call; current title
names the model honestly); "PRE instead" (recommendation stays PRR-first with PRE auto-fallback).

## New mathematics/numerics added (review items 8.1–8.2)
- `dpma_bcN_convergence.py`: finite-lattice fold threshold b_c,N(1/2) via bisection on exact
  eigvalsh modes, N=100–1200 → converges monotonically from above, **|b_c,N − b_c| ∝ N^-2.08**
  (4.7e-3 → 2.6e-5). Quoted in intro item 3, Sec III.B, Table II, App B, App E.
- `dpma_bd_convergence.py`: BD gate-width (ℓ=0.04/0.02/0.01) and time-step (3e-5–7.5e-6) sweeps,
  3×6e4 walkers/cell → late-peak location within two histogram bins of exact τ_p everywhere; R
  within 1–3.5% of exact (≤2.6 s.e.m.), bias shrinking with dt.
- `dpma_window_scan.py` extended to θ=0.20 (seven values, all clean single-transition).

## Internal audit round (30 raw → 29 confirmed, ALL minor/polish, 0 major)
Notable catches, all fixed: intro item-3 pointer promised finite-N checks in Sec IV that live
elsewhere (pointer broadened + Sec IV opener now names them); BD convergence prose overstated its
own artifact ("within a histogram bin"/"~2 s.e.m." → "two bins"/"~2.6 s.e.m.", artifact regenerated
to match); the same fit quoted as N^-2 / N^-2.1 / N^-2.08 in different places (unified to N^-2.08);
"their merger into a single-scale morphology" misstated the fold (the late peak merges with its
VALLEY; the two scales never merge) — fixed in Sec VI.A and the fig:start caption; residual
"interior second peak" phrasing under ξ=θ; notation table conflated q with laziness (q = hop
probability; stay = 1−q); β_c²ᴰ 0.69 vs 0.684 unified to ≈0.68 (bisected 0.684); fig:ext 2D panel
switched to log-y so the late maxima are actually visible; Fig. 3 caption dedup; App B local
A,B,C,E abbreviations scoped against B_j / Woodbury B / B=bd; reproducibility README Table-number
and row-index fixes after the new Table I (notation) shifted tab:verif to Table II; make_all driver
now includes all mapped scripts.

## Remaining human-gated items (unchanged)
Funding line; public repo + Zenodo DOI (package ready under extras/reproducibility/); title-change
decision; venue sign-off; push/arXiv timing.

## Round-5 addendum: second external review (7.8/10) — final referee-defense polish (same day)
The follow-up external review confirmed the round-4 verdict ("past the submit-worthy line") and
listed 7 final items; 6 adopted, 1 partially:
1. "two-peak window/region" purged under the source-started convention → defined once as the
   *peak window* (Sec III.A), Fig. 2(a) in-figure label → "interior peak exists", panel title →
   "finite-time interior peak exists".
2. Abstract trimmed ~10% (channel parenthetical, half-line clause) while keeping every
   audit-hardened qualifier.
3. DAS: final swap-in sentence added as a tex comment next to the availability paragraph
   (publishing the repo/DOI remains user-gated); App D "deposited script" → "accompanying script".
4. fig:start (the source-started defense evidence) promoted to a full-width figure*.
5. **Type 3 fonts eliminated**: pdf.fonttype=42 in all five figure scripts, all figures
   regenerated; verified old fig had 2 /Type3 dicts, new figs have 0 (FontFile2/TrueType embedded);
   manuscript PDF: 0 Type3 markers.
6. Discrete-time terminology fixed: Eq. (1) now P_lambda (transition matrix, not "generator");
   Woodbury frame explicitly "continuous-time generator (or, analogously, sub-stochastic transition
   matrix)"; App B "killed evolution operator"/"symmetrizable transient matrix"; Sec VI.C P_lambda.
7. Sec VI.B: "b is the per-frame trigger rate" → controlled parameter is kappa (b = kappa*l*L/(2D);
   frame-based: kappa = per-frame probability / frame time).
Declined as premature: writing the final DAS with a live URL/DOI before the repo exists (would
reintroduce the printed-placeholder blocker); handled via the swap-in comment instead.
Recompiled: 14pp, 0 errors / 0 overfull / 0 undefined; identity tests 5/5; validators OK.
