# Triangulated adversarial audit of the full PRR manuscript — 2026-07-01

Three heterogeneous adversaries audited `manuscript/dpma_prr_manuscript.tex` (the expanded 8-page
full article), reconciled by numerical/repo ground truth (TANA). Purpose: pre-submission hardening.

## The three adversaries + verdicts
1. **Claude dynamic Workflow (repo-grounded), 60 agents, 2 rounds** — 49 raw findings → 29 survived
   adversarial verification → ~11 distinct. **Verdict: MINOR REVISION (heavy). 0 blockers.** Sees the
   committed code, so it knows the numerics ARE certified; treats issues as honesty/notation/scoping.
   Record: workflow `wemf1s1t3` / `wf_f1f49ef9-3c7`.
2. **ChatGPT gpt-5-5-thinking (no repo)** — full referee pass. **Verdict: MAJOR REVISION.** Same
   substantive findings; harsher because it reads "verified" claims as weaker without the code.
3. **ChatGPT gpt-5-5-pro / Extended Pro (no repo, no figures)** — full PRR referee report.
   **Verdict: REJECT/TRANSFER in current form; PRR only with major reframing.** Harshest, driven by
   (a) no figure access (couldn't see b_c(θ), 2D panels, certification plots that exist) and (b) a
   genuine strategic point: PRR acceptance hinges on the broad-physics framing. NB the Pro stream
   dropped twice mid-generation; recovered server-side via reload (final answer confirmed on
   `gpt-5-5-pro`). Chat: PRR-referee thread `6a43f5cd`.

## Arbitration (numerical ground truth resolves the severity spread)
The verdict spread (minor↔major↔reject) is **explained entirely by repo/figure access**, not by
disagreement on facts. The math core is independently confirmed correct and reproducible (Claude
re-derived it; committed scripts match to the tolerances in Table I). So the severity is arbitrated
DOWN: the fixes are honesty/framing/notation, **not new physics**. All three agree the single PRR
novelty is the **certified saddle-node of the FPT density** (not the resolvent/δ-sink/bimodality).

## CONVERGED findings — ALL FIXED in the .tex (2026-07-01)
- **Sign error** Eq. (mdl), App. A: `[1−zλG⁰]`→`[1+zλG⁰]` (matrix-determinant lemma; I verified
  independently — only + reproduces the correct D_u). Downstream D_u was already correct.
- **Sign error** App. B IFT Jacobian: `det DF_c = −S_{1,b}S₃`→`+S_{1,b}S₃` (∂_τS₁=−S₂=0, ∂_τS₂=−S₃).
  Conclusion unaffected. Also fixed in `notes/dpma_amplitude_derivation_20260630.md`.
- **Start-dependence** b_c(θ;ξ): stated the source-started convention ξ=θ throughout (abstract,
  contributions, Sec III.A), wrote b_c(θ;ξ), and added the release-at-gate (ξ=θ) requirement to the
  colloidal realization (Sec V.B).
- **Global "iff" softened**: local fold S₁=S₂=0 is exact; the global single-connected-interval /
  no-re-entrance statement is now labelled numerically certified over the scanned range, not proven.
  Section retitled "Saddle-node fold criterion and phase boundary" (was "existence theorem").
- **Universality scoped**: Woodbury real-signed-mixture claim restricted to reversible (symmetrizable)
  diagonal low-rank killing; non-reversible directed dynamics flagged as needing extra hypotheses.
- **"non-Hermitian" downshifted**: abstract now "low-rank killing defect"; Sec V.C states the
  survival-sector operator is self-adjoint in the one-defect model (open-system loss, not spectral).
- **2D honest**: softened to finite-lattice (L=31) evidence; β_c^{2D}≈0.5–0.65 (consistent with the
  figure); large-L point-sink log-marginality + a size-independent 2D scaling test explicitly left to
  future work; removed the unbacked "L=17,25,33" (only L=31 is committed).
- **δ-sink prior art**: added a sentence (Sec II.C) attributing the point-interaction eigenvalue
  condition to the standard point-sink literature; scoped novelty to the finite-N directed-shortcut
  Montroll determinant + bifurcation classification.
- **Language discipline**: "known to be bimodal"→"can be bimodal"; "explicit boundary"→"computable
  boundary"; "universal normal-form scaling"→"generic saddle-node scaling"; "survives on 2D"→"persists
  on finite 2D lattices".
- **Notation collisions** fixed: β (rate) vs position → second shortcut position renamed β→η (Sec IV.B,
  App D, cusp Eq); gate width a→ℓ (Sec V.A, vs a=q/λ); App B spectral momentum q→ϰ (vs laziness q);
  Eq (G) φ_{w,θ}→φ_{k,θ} with k=2w (I,J in k).
- **Copy-edit**: Fig 2(a) caption 0.789/θ→0.789/min(θ,1−θ) (both branches); Table I cusp-residual
  bound ≤10⁻¹⁰→≤10⁻⁹ (n=3 is ~4e-10); App E "eigvalsh returns eigenvalues only" → "poles via eigvalsh,
  amplitudes from closed-form residues"; App A A₀:=U₋₁=0 defined; π_sc ρ=min(r,N−r) defined; uncited
  Arnold1992 (cusp) + Ashida2020 (EP) now cited; added dpma_multishortcut.py to the App E script list.
Recompiles clean: 8 pp, 0 errors, 0 overfull, all 59 labels/refs/cites resolved.

## DEFERRED (non-blocking; for a future copy-edit / larger revision)
- Remaining symbol overloads flagged by Claude but left as-is (lower confusion risk): L (=N/2 shorthand
  vs torus side), B (residues vs Woodbury matrix vs sin-shorthand vs endpoint const), A (fold amp vs
  Chebyshev vs sin-shorthand), f(t) vs Φ(τ). A dedicated notation pass is advisable but risks new errors.
- Prefactor constants (0.0247518, 0.357444, −133.107) and the eigenvalue-gap "verified" parenthetical
  are analytically derived / note-backed but lack a dedicated committed script; either commit small
  scripts or reduce displayed precision (a pre-submission choice).
- **Pro's strategic reframe (venue decision, Luca's call):** the title/abstract already lead with the
  FPT-density saddle-node (the physics, per Pro's own recommendation), and the paper DOES contain the
  b_c(θ) phase boundary, the rank-2 cusp, the 2D test, and a physical-realizations section that Pro
  (text-only, no figures) under-weighted.

## PRR-strengthening additions DONE (2026-07-01, user chose "strengthen for PRR")
New `code/dpma_channel_mc.py` → `artifacts/figures/dpma_channel_mc.pdf` = **Fig 3** (full-width, new
§IV.E "Direct simulation and channel resolution"; manuscript now 9pp), directly addressing three of
Pro's asks:
- **(a) Direct Monte-Carlo cross-check** (4×10⁵ walkers, no spectral input) reproduces the exact FPT
  density across 4 decades in τ; simulated π_sc=0.565 matches exact to 1e-3 → rebuts "solvable-model
  curiosity."
- **(b) Exact channel-resolution** f=f_sc+f_diff (the absorption vector splits exactly): early mode =
  shortcut capture, late mode = diffusive return; the saddle-node = annihilation of the diffusive-
  return peak. Identifies which channel makes which arrival-time mode.
- **(c) Non-antipodal robustness** at θ=0.38 across b_c(θ)≈2.16 (interior maxima 1→1→0 for b=1.5/2.16/
  2.8) → fold not special to the antipode.
Presentation note: source-started (ξ=θ) densities need LOG-LOG axes — the shortcut-capture spike near
τ→0 swamps the diffusive bump on linear axes. Compiles clean (9pp, 0 err/overfull/stuck, refs OK).
Still OPTIONAL for an even stronger PRR run (not done): a full general-(θ,ξ) modal-transition phase
diagram (b_c(θ) at ξ=θ already exists as Fig 2a), and a direct 2D-fold simulation.

## Reconciled bottom line
Math bulletproof and reproducible; all honesty/notation/scoping fixes applied. The residual question
is **strategic venue/framing** (aggressive PRR reframe + robustness/figures, or bank PRE/JPA) — Luca's
call. See also [[project-dpma-double-peak]] [[reference-triangulated-audit]].
