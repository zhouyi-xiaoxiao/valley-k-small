# ChatGPT-Pro audit + 3-way reconciliation (2026-06-30)

Driven via the local ai-bridge MCP + browser automation (Control_Chrome): Claude
injected the audit prompt into ChatGPT and scraped the result. Two ChatGPT runs:
- **gpt-5-5-pro** (Extended Pro / "Pro 扩展", model slug verified) — AUTHORITATIVE.
  Chat: https://chatgpt.com/c/6a43b8d7-0ce4-83eb-ac6d-97b49c566b28
- **gpt-5-5-thinking** (ultra-high reasoning) — cross-check.
  Chat: https://chatgpt.com/c/6a43afa6-ea8c-83ed-87b9-7354f740b9c3
Third independent audit: Claude multi-agent workflow `wf_f9fb1a8b-f2c`
(`notes/dpma_adversarial_audit_20260630.md`).

## 3-way reconciliation (Claude / gpt-5.5-thinking / gpt-5-5-pro)

| claim | Claude | thinking | pro | reconciled action |
|---|---|---|---|---|
| 1 channel-mass π_sc | CONFIRMED (Sherman-Morrison) | CONFIRMED/wording | NEEDS-FIX blocker | formula exact; **rename to "shortcut splitting probability / integrated channel mass"; never call it first-peak mass** (already quantified 3-4× gap) |
| 2 spectral shift | CONFIRMED | CONFIRMED/major | NEEDS-FIX major | exact 1st-order; **state |ϕ_k(u)|²≈(2/N)sin² only in large-N interior regime**; node-freeze exact when ϕ_k(u)=0 |
| 3 q-reduction | exact (roots) | CONFIRMED/needs-fix | REFUTED | **adjudicated numerically: roots BYTE-IDENTICAL across q=0.5/0.667/0.9 ⟹ q-elimination EXACT (pro over-reaches).** Pro's u-parity point real but tiny (~0.01-0.04% @N=120, O(1/N) embedding) — add minor caveat |
| 4 A(d) window law | classifier-dependent | REFUTED as physics | REFUTED blocker | **unanimous: demote A(d)/b_pl/N* to C.2-classifier corollaries; not physical** (safe-pass applied) |
| 5 plateau master | leading-order | NEEDS-FIX | NEEDS-FIX major | tan w=−2w/b exact; **G_j leading-1/N**; b_pl=1.573 is a classifier threshold not physical |
| 6 b_c saddle-node | treated solid | NEEDS-FIX (certify) | **REFUTED blocker** | **KEY CORRECTION: b_c is a numerical CROSSOVER, not a certified saddle-node.** Downgrade; certification (2-mode discriminant) running on Pro |
| 7 general-u determinant | re-derived ✓ | CONFIRMED (matrix-det lemma) | NEEDS-FIX | **CONFIRMED** (thinking+Claude supplied the proof: det H0=2^−(N−1)U_{N−1}, [H0⁻¹]_uu=2U_{u−1}U_{N−u−1}/U_{N−1}; factor-2 derived). Pro just didn't derive it |
| 8 C.2 circularity | flagged | CONFIRMED | CONFIRMED | **unanimous: restructure — analytic criterion (#stationary points / hazard sign-changes), C.2 only as operational detector** |
| 9 θ-collapse retire | confirmed | CONFIRMED | MOSTLY | retire; salvage only near-antipodal θ≈1/2+O(1/N) or ρ∝N x=0.05 |
| 10 novelty | reframe | NEEDS-FIX | UNDER-CLAIMED (weaker) | **cite Giuggioli PRX 2020 (method anchor), Montroll-Weiss; Mattos=P(ω) not f(t)**; only defensible novelty = multi-peak temporal decomposition from interior directed shortcut + (if proven) peak bifurcation |

## Deliverable A — G_{ξ,θ}: NUMERICALLY ADJUDICATED & VERIFIED
Two competing closed forms were proposed; I tested both against exact finite-N
residues A_j=(N²/q)B_j (`code/dpma_general_u_master_amplitudes.py`):
- **gpt-5.5-thinking form VERIFIED**: G_{ξ,θ}=2w² φ_{w,θ}(ξ) I_{w,θ}/J_{w,θ}
  → ratio A/G → 1.0000, **max |A/G−1|=2.1e-4 @N=1200, O(1/N²)**, affected modes,
  θ=1/2 & 1/3. Node/unaffected modes (sin2θw=0) excluded (separate amplitude).
- gpt-5-5-pro form REJECTED: sin(w(1−ξ))sin(wθ)/(sinw+(b/2w)(1−cos2w)) → ratios
  16-26×, does not match.
- **Correction it implies**: the report's antipodal G (no ξ) is the CENTER-START
  (ξ=1/2) special case; general start carries a sin(2wξ) factor.
(Triangulation note: the weaker model gave the correct formula; the stronger model
was wrong-but-cautious — verification, not authority, settled it.)

## Deliverable B — prior-art (thinking+pro agree)
Cite: Giuggioli PRX 10,021045 (2020) [lattice-Green/defect-resolvent = method anchor],
Montroll-Weiss, Godec-Metzler PRX 6,041037 (2016) [conceptual: direct-vs-indirect],
Grebenkov / Bressloff / Lawley [interior partial-absorption / narrow escape].
Correct Mattos PRE 86,031143 (2012): P(ω) splitting-probability bimodality, NOT f(t).
NOT new alone: rank-one perturbation, Chebyshev determinant, diffusion-limit δ-sink.

## Publishability — 3-way reconciled (conservative)
- PRE: not submission-ready as-is (Claude 10-15%; thinking 35-50%; pro ❌-not-yet).
- J.Phys.A: viable today (55-70%) as an exact spectral / defect-resolvent study.
- PRR: not ready (5-40% range); gated on (a) **certifying b_c as a genuine saddle-node**
  (running on Pro), (b) reframing physics-first around the threshold-free transition +
  δ-sink, (c) removing classifier-defined quantities, (d) honest Giuggioli prior-art.
- One-line (pro): "math backbone consistent with defect-resolvent theory, but the paper
  over-claims physical phase transitions not yet mathematically certified."

## b_c saddle-node certification — RESOLVED: GENUINE SADDLE-NODE (Pro's refutation refuted)
gpt-5-5-pro's b_c run (recovered after a dropped stream via tab reload) argued b_c is
**NOT** a saddle-node: a 2-mode sum G₁e^{−μ₁τ}+G₂e^{−μ₂τ} with **G₁,G₂>0** is completely
monotone (no interior extrema) ⟹ "needs ≥3 modes; b_c is a spectral-dominance crossover,
not a fold."
**This is REFUTED — Pro's premise is false.** The modal amplitudes B_j are SIGNED
(verified: `code/dpma_saddle_node_certification.py` finds ~100 positive / ~100 negative
at N=400, ΣB_j≈0 as F(0)=0 forces). A signed-amplitude exponential mixture is NOT
completely monotone and DOES admit interior extrema. (Pro was likewise wrong on the G
formula — pattern: do not accept Pro's algebra without numerical check.)
**Independent certification (committed):** on the exact N→∞ master curve Φ(τ;b), as b→b_c
the (valley-min, peak-max) pair COALESCES — both gap (τ_max−τ_min) AND prominence
(Φ_max−Φ_min) → 0 together, then annihilate for b≥3.078:
  b=3.060 gap=3.2e-3 prom=5.0e-4 ; b=3.070 gap=2.0e-3 prom=1.2e-4 ;
  b=3.0764 gap=1.4e-4 prom=4.4e-8 ; b≥3.078: no pair.
gap→0 ∧ prominence→0 ⟹ Φ'(τ_c)=Φ''(τ_c)=0 (double root) ⟹ **GENUINE SADDLE-NODE**, not a
dominance crossover (which would kill the peak without the simultaneous collapse). This is
exactly the threshold-free certification all three audits demanded; the PRR headline
SURVIVES and is strengthened. Script: `code/dpma_saddle_node_certification.py`.
