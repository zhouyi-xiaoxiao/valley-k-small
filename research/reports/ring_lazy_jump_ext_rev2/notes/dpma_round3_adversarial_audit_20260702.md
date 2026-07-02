# DPMA round-3 audits + first-submission deepening (2026-07-02)

Two multi-agent adversarial audit rounds were run on 2026-07-02 (Claude Workflow, repo-grounded,
with per-finding adversarial verification and numeric checks against the deposited scripts).

## Round A — publication-readiness assessment (47 raw → 46 confirmed)
Question: does the 11pp manuscript meet first-submission standards for writing, logic, appendix
derivation depth? Key outcomes, all fixed the same day:

- **Derivation depth (majors).** App A: numerator N_{r,u} and π_sc now derived (Sherman–Morrison
  column + Chebyshev product identity A_{N-r}A_u − A_{N-u}A_r = A_N A_{u-r}); the G⁰_uu
  proportionality replaced by the exact prefactor. App B: J = sin(k)D_k/(4b) **proven
  algebraically** on the page (4-line trig identity), residue-extraction chain displayed, antipodal
  reduction derived, δ-jump equivalence proven. App C: the half-line boundary-layer problem is now
  **solved explicitly** — closed-form arrival transform f̂(s;B), branch-cut inversion Φ_hl(σ;B),
  fold → **B\* = 0.7890262, c\* = 0.1579221** (`dpma_halfline_bstar.py`; matches the old 10-digit
  quote 0.7890261736 exactly and interval bisection to 6 digits). Normal-form prefactors now
  **analytic**: gap = 2√(2S₁ᵦ/S₃)·√(b_c−b), ΔΦ = (4√2/3)·S₁ᵦ^{3/2}S₃^{−1/2}(b_c−b)^{3/2} →
  0.0247518 / 0.357444 (`dpma_normal_form.py`; −133 ε² coefficient re-fitted: −133.1, committed).
- **Honesty/consistency**: "regular perturbation yields −133" → honest quadratic fit; channel claim
  (late peak fed by BOTH channels) propagated; abstract restructured; Sec IV retitled "Structural
  stability and model independence"; 2D geometry fully specified; Fig 2(a) asymptote values no
  longer plotted as data; code/data availability statement made compile-clean; +8 references
  (Condamin, Bénichou-Voituriez, Grebenkov-Metzler-Oshanin, Pal-Reuveni, Kato, Albeverio,
  Wilemski-Fixman, Szabo-Schulten).

## Round B — adversarial audit of the revised 13pp version (38 raw → 37 confirmed)
Numeric verifiers caught real errors in the *newly added* material; all fixed:

1. **Measurability chain wrong (major).** Stale slope 0.05/unit-b; true |dR/db| ≈ 0.086 from the
   exact R(b) table. Corrected: 4×10⁴ trials resolve b_c to ±0.25; ±0.1 needs ≈2×10⁵
   (script + App E + Sec V.B all fixed and regenerated).
2. **Dimensional restoration off by 2 (major).** With unit variance rate in Eq. (5):
   τ = 2Dt/L², b = κℓL/(2D), κ_c ≈ 4.3 D/(ℓL) (was κℓL/D, 2.2).
3. **Seven leftover "diffusive-return/diffusive peak" labels** contradicting the channel reframe →
   neutral names (the verifier computed the late peak splits 0.523 shortcut / 0.477 diffusive).
4. **Fig 2(b) fold invisible at print scale (major)** → inset zoom added; also panel titles (a)–(f),
   suptitle and ALL-CAPS slogans removed.
5. **Window-connectivity unverified** → new dense-b scan (`dpma_window_scan.py`, w ≤ 120 spectrum):
   single connected two-peak window CONFIRMED at all six θ (exactly one transition, matching b_c).
   NOTE: a naive scan with the default w ≤ 40 spectrum produces spurious extra extrema at
   off-center θ (fold times τ_c ~ 0.16 θ² need deeper modes) — documented in the script.
6. **2D single-size evidence** → size sweep (`dpma_2d_Lsweep.py`): β_c²ᴰ = 0.669/0.684/0.686/0.682
   at L = 21/31/41/51 — nearly size-independent; log-drift not yet visible; stated honestly.
   NOTE: the "visually double" flag (deep-valley condition) breaks at β≈0.46; the fold criterion is
   late-maximum existence (prominence → 0), which is what the paper and the sweep use.
7. **O(N⁻²) vs hardcoded "O(1/N)" artifact verdict**: measured exponent 2.00
   (`dpma_general_u_master_curve.py` now computes it; the old string was hardcoded and wrong).
8. Smaller: π_sc = ρ/(a+N/2) (L undefined); c\* only 3-digit-confirmed by interval; w≤40 not k≤40;
   Table I rank-2 residual ≲1.3×10⁻⁴; exponents quoted as 0.498(1)/1.493(2); π_sc digits
   0.56466±0.00078 vs 0.56522 (Table's 0.6×10⁻³ now traceable); δ-sink literature lineage cited;
   BD instance reframed as "direct stochastic realization" (same continuum model, no exact
   machinery); cusp solve unknowns stated ((η,b₂,τ_c) at fixed (α,b₁)); tcut/threshold disclosed.

## Remaining human-only items (unchanged)
Funding line (`% CONFIRM`, acknowledgments); repository DOI at publication; venue decision;
push/arXiv timing.
