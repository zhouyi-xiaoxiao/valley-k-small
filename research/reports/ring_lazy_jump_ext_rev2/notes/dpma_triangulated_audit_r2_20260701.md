# Triangulated adversarial audit — ROUND 2 (revised 9pp manuscript) — 2026-07-01

Second full triangulated pass on the round-1-revised manuscript, then a major revision to 11pp.
Adversaries: Claude repo-grounded Workflow (`wucg4lcgd`, 37 agents, 2 rounds, 13+10 survived) +
ChatGPT gpt-5-5-thinking + ChatGPT Extended Pro `gpt-5-5-pro` (PRR-referee thread `6a43f5cd`; stream
dropped twice, recovered server-side via reload — 32.8 KB report confirmed on gpt-5-5-pro).

## Verdicts (both markedly UP from round 1)
- **ChatGPT Extended Pro: MAJOR REVISION** (was reject/transfer). "Substantially improved, plausibly
  PRR-track... possibly approaching acceptance after one more round." Praised the new §IV.E (MC +
  channel + off-antipodal) as exactly the right additions.
- **Claude Workflow: CONDITIONAL / MOSTLY meets standard.** Core correct and honestly hedged; three
  repo-grounded gaps (below) were the bar to PRR.
- **Page count settled:** PRR regular articles have no page limit (typ. 8–16pp); 9→11pp is normal.

## The decisive convergence (repo ground truth resolved it)
The single most important remaining issue (Pro #1, and the peak-definition problem): under the
source-started convention ξ=θ the **shortcut-capture feature is a boundary/initial-time mode, not a
clean interior maximum** — so "double peak / iff" was imprecise, and the paper looked like it might be
an artifact of releasing exactly at the gate. Resolved by (a) precise language and (b) a NEW
computation showing that off the gate both features are genuine interior peaks and the fold persists.

## Round-2 CORRECTIONS applied (manuscript now 11pp, compiles 0 err/overfull/stuck, refs OK)
NUMERICAL-CORRECTNESS (caught by Claude's repo access; Pro couldn't see):
- **2D threshold was WRONG.** Committed data shows the 2nd interior maximum's prominence→0 between
  β=0.68 and 0.70 (peak vanishes at 0.70), so β_c^2D≈0.69 — NOT 0.55–0.65 (that was a 0.95·min valley
  heuristic + grid stopping at 0.65). Fixed text+captions to ≈0.69; extended `dpma_prr_figures.py`
  panel-F grid to 0.72 with the extremum-merging criterion; regenerated Fig 2.
- **Endpoint constant B*=0.7890261736 was circular/unreproduced.** The committed check cross-checks
  against Pro's own hardcoded B*/d table and fails/12%-off at d≤0.10. Reduced to B*≈0.789 (3 digits,
  numerically observed, closed form open); wrote out the half-line rescaling (y=x/d, B=b·d) in App C.
- **Fig-3 channel claim overreached.** The shortcut channel supplies 36–78% of the "late diffusive"
  bump; reworded — f_sc monotone carries short-time mass, the late bump gets comparable contributions
  from BOTH channels, the fold annihilates the second arrival-time SCALE not a pure channel.
- π_sc "exact"=0.5656 was a truncated sum (true 0.565217) and MC match was seed-borderline (1.24σ);
  now 0.5647±0.0008 vs exact 0.5652. Master-curve tol ~1e-5→≤6e-5 (per-mode ~2e-4). Prefactors
  0.0247518/0.357444/−133.107 → 0.025/0.36/−133 (no committed script). Minimal-mode K=4-gives-no-fold
  parity added.
HONESTY/PRECISION (both audits):
- Global "iff/precisely" → "numerical continuation gives a single connected two-mode window"; local
  fold kept as theorem. Peak definition made explicit (boundary capture mode vs interior extrema).
- b/λ collision fixed: Eq (1) → Q_λ=Q_0−λ|u><u| (discrete), b=λN/q continuum; admissibility 0≤λ≤1−q.
  Woodbury Q_b→Q_B. q-rescaling error fixed (τ_c→τ_c/q was wrong; raw t_c~N²τ_c/q). "moving start onto
  shortcut destroys theorem" reworded. Woodbury softened (determinant identity, not the source of
  universality — structural stability is). Cusp "slightly off" → "distinct control values (b_2 0.14 vs
  1.08)". "non-Hermitian" dropped from abstract/contributions (survival block self-adjoint).
COMPLETENESS additions:
- Exact generating function Eq (genfun) + channel generating functions (App A) + finite→continuum
  scaling. Non-dimensionalization b~κℓL/D with validity ℓ≪L and the lab κ target (Sec V.A). C_ab
  formula (App D). Code-availability statement + scan ranges + MC details (App E).

## Two NEW figures (the significance difference-makers both audits ranked #1)
- **Fig 4 `dpma_start_dependence.py`** (§IV.E(iv) + Sec V): released off the gate (ξ=0.44) both features
  are genuine INTERIOR peaks that fold; b_c(θ=½;ξ) varies smoothly/symmetrically about ξ=θ (3.076→3.137
  over ξ=0.44–0.56) → fold robust to release position, not a knife-edge. (Far from the gate the
  morphology changes — stated honestly. Continuum used, not the discrete ring, because ξ≠θ discrete
  densities have short-time lattice oscillations.)
- **Fig 5 `dpma_brownian_fold.py`** (§IV.F "An independent continuum instance"): a direct continuum
  Brownian-dynamics (Euler–Maruyama, gate width ℓ=0.02, NO lattice, NO spectral input) reproduces both
  the exact δ-sink density Φ(τ) AND the fold — two interior peaks below b_c, one above. Converts
  Woodbury model-independence from algebra into a demonstrated second instance.

## Still open (non-blocking, pre-submission)
- Add cites Pro flagged (Godec–Metzler two-channel diffusion JPA; gated FPT / Kumar; optical-tweezer
  resetting experiments) — deferred to avoid unverified bibitems.
- Optional: commit a half-line solver reproducing B* at d≤0.1; a normal-form-prefactor script; a 2D
  gap+prominence co-collapse test; a noisy simulated-experiment protocol showing recoverability.
- Confirm funding line in acknowledgments.
Related: [[project-dpma-double-peak]] [[reference-triangulated-audit]].
