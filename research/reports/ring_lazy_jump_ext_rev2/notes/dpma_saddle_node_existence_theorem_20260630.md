# Saddle-node existence theorem for the directed-shortcut FPT density (PRR roadmap #1)

Derived by ChatGPT gpt-5-5-pro (chat 6a44a878), **independently numerically arbitrated here**
(all substantive claims match to the tolerances below). This is the general "when does a
second first-passage peak exist" criterion the PRR referee flagged as the biggest theoretical gap.

## Setup
Continuum FPT density (diffusion limit; [0,1] absorbing ends, interior δ-sink at x=θ=u/N,
strength b; start ξ): Φ_{ξ,θ}(τ;b)=Σ_j G_j e^{−μ_j τ}, μ_j=2w_j²=k_j²/2, with k_j=2w_j the
positive roots of the spectral determinant
  **D_θ(k;b) = k sin k + 2b sin(kθ) sin(k(1−θ)) = 0.**
Signed amplitudes G_j (affected: 2w²φ_{w,θ}(ξ)I/J; node sin(2θw)=0: G_n^node=nπ[1−(−1)ⁿ]sin(nπξ)).
Physical start convention ξ=θ (start at the shortcut source = sink location; antipodal ξ=θ=1/2).

## Theorem (existence criterion — resolvent/spectral-moment form)
Define signed spectral moments S_m(b,τ)=Σ_j G_j μ_j^m e^{−μ_j τ}. Then Φ'=−S₁, Φ''=S₂, so a
second interior peak of the FPT density is born/annihilated at a **saddle-node**
  **S₁(b_c,τ_c) = 0  and  S₂(b_c,τ_c) = 0,   with nondegeneracy S₃≠0, ∂_b S₁≠0.**
Equivalently the τ_c-eliminated scalar boundary C_θ,ξ(b):=S₁(b,τ₂(b))=0 where S₂(b,τ₂)=0 — the
generalized discriminant of the exponential sum S₁. No positivity is assumed (the G_j are signed).
The second peak exists for **0 < b < b_c(θ;ξ)**. (∂_b k_j from D: ∂_b k=−D_b/D_k,
D_b=2 sin(kθ)sin(k(1−θ)), D_k=sin k + k cos k + b[−(2θ−1)sin((2θ−1)k)+sin k].)

## Antipodal special case (recovers the certified number)
D_{1/2}=k sin k + b(1−cos k)=2 sin(k/2)[k cos(k/2)+b sin(k/2)] ⟹ tan w=−2w/b; node modes k=2mπ
have zero weight at ξ=1/2. Solving S₁=S₂=0: **b_c(1/2)=3.0764323604, τ_c=0.03836305186**;
S₃=2.83e5, ∂_b S₁=21.66 (nondegenerate). Normal form ⟹ peak–valley **separation
∼0.0247518·(b_c−b)^{1/2}**, **prominence ∼0.357444·(b_c−b)^{3/2}** — the √ fold / catastrophe signature.

## Minimal mode count (theorem)
A **2-mode fold is impossible even with signs**: S₁=0 ⟹ A₂=−A₁ (A_j=G_j μ_j e^{−μ_j τ}), then
S₂=(μ₁−μ₂)A₁=0 ⟹ A₁=A₂=0 (contradiction). **Minimum = 3 modes**, and the fold ratio
A₁:A₂:A₃=(μ₃−μ₂):(μ₁−μ₃):(μ₂−μ₁) forces **alternating signs** (G₁>0,G₂<0,G₃>0,…) — which the
true affected amplitudes have. (This also formally retires Pro's earlier wrong 2-mode argument.)

## b_c(θ) boundary (symmetric, b_c(θ)=b_c(1−θ); minimum at θ_min≈0.3808, b_c≈2.1645)
Endpoint (boundary layer d=min(θ,1−θ)→0): **b_c(θ) ∼ 0.7890261736 / d**, τ_c∼0.1579221011 d²
(half-line problem: absorbing 0, δ-sink at y=1 strength B, start y=1; B*=0.7890261736).
Near-antipodal: b_c(1/2+ε)=3.0764323604 − 133.107 ε² + O(ε⁴). b→0: plain Dirichlet spectrum;
b→∞: δ-sink → absorbing cut, Φ→δ(τ) for ξ=θ (no second peak) — consistent with finite b_c.

## Numerical arbitration (this repo — `code/dpma_saddle_node_bc_theta.py`)
Independent computation (continuum roots of D_θ + signed closed-form G + fold detection):

| θ | b_c (num) | b_c (Pro) | rel-diff | b_c·d |
|---|---|---|---|---|
| 0.50 | 3.0764 | 3.0764 | 6e-7 | 1.538 |
| 0.45 | 2.7716 | 2.7716 | 1e-6 | 1.247 |
| 0.40 | 2.2245 | 2.2245 | 2e-6 | 0.890 |
| 0.35 | 2.2655 | 2.2655 | 1e-6 | 0.793 |
| 0.30 | 2.6301 | 2.6301 | 2e-6 | **0.7890** |
| 0.25 | 3.1561 | 3.1561 | 1e-6 | **0.7890** |
| 0.20 | 3.9451 | 3.9451 | 6e-9 | **0.7890** |

- b_c(θ) matches Pro to **rel-diff ~1e-6** across θ∈[0.20,0.50].
- Endpoint constant **b_c·d→0.7890** confirmed (and already exact by θ≲0.30).
- Minimal-mode truncation (θ=ξ=1/2): **K=2 → no fold; K=3 → 3.0463; K≥5 → 3.0764** — matches Pro.
- (θ≤0.15 not resolved by the arbiter's τ-grid because τ_c→0; endpoint law covers that regime.)

## Status
**Roadmap #1 CLOSED.** This is the PRR "existence theorem": a threshold-free, signed-amplitude
saddle-node criterion S₁=S₂=0, the explicit b_c(θ) boundary with a clean endpoint law
b_c∼0.789/d, and a minimal-mode (≥3, alternating-sign) theorem — all analytically derived and
numerically arbitrated. Full derivation archived in the session scratch; criterion validation
in `code/dpma_saddle_node_bc_theta.py` → `artifacts/tables/dpma_saddle_node_bc_theta.txt`.
Remaining PRR roadmap: universality (2D/multiple-shortcut/robustness), physical embedding,
PRR-grade figures (the b_c(θ) boundary curve is now figure-ready), framing/prior-art.
