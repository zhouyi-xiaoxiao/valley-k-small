# Universality / robustness of the directed-shortcut saddle-node (PRR roadmap #2)

Derived by ChatGPT gpt-5-5-pro (chat 70843060), **numerically arbitrated here**. Answers the
PRR referee's "beautiful but model-specific 1D?" — the mechanism is a GENERIC fold, survives 2D,
and generalizes to multi-fold with multiple shortcuts.

## A. Model-independence (genericity theorem)
Woodbury / matrix-determinant lemma for a rank-m killing defect Q_b=Q_0−UBU^T:
`det(sI−Q_b)=det(sI−Q_0)·det[I_m+B W(s)]`, W_ab=⟨u_a|(sI−Q_0)^{-1}|u_b⟩. The FPT density is a
**signed** spectral mixture Φ=Σ_j G_j e^{−μ_j t}, and the second-peak birth/death is the fold
**S₁=S₂=0** (S_n=Σ_j G_j μ_j^n e^{−μ_j t}; Φ'=−S₁, Φ''=S₂), nondeg S₃≠0, ∇_b S₁≠0.
**Minimal universality theorem (Pro):** if Q_b is analytic in b with discrete diagonalizable
spectrum and C³ density, and the interior-extrema count changes between regular b-values without
an extremum escaping to t=0/∞, then ∃(t_c,b_c) with S₁=S₂=0; if nondegenerate it is a
structurally stable saddle-node. **The honest claim is NOT "every shortcut makes a peak"** (false)
but "whenever a shortcut-induced peak is born/annihilated generically, it is a fold of the signed
spectral mixture, not a 1D-ring artifact." The double-peak region is an OPEN set (IFT) → not fine-tuned.

## B. Multiple shortcuts (rank-m) — VALIDATED
Secular equation det[I_m+B W(k)]=0, W_ab=R_0(k;θ_a,θ_b) (interval resolvent). Explicit m=2:
`D₁₂(k)=k sin k + 2b₁ sin(kα)sin(k(1−α)) + 2b₂ sin(kβ)sin(k(1−β)) + (4b₁b₂/k)·sin(kα)sin(k(β−α))sin(k(1−β))`
— the **b₁b₂ term is a genuinely new interaction** (→0 when sources coalesce ⟹ b=b₁+b₂).
*Arbitration* (`code/dpma_multishortcut.py`): D₁₂(k_j) → ~1e-5 at the exact 2-shortcut ring
eigenvalues (N=800), O(1/N) → confirmed.

**NEW RESULT — two shortcuts create a THIRD peak.** Pro predicted (θ₁=0.38,θ₂=0.48,b₁=1.35,
b₂=0.14,ξ=0.463) → 3 maxima at τ≈2.8e-4, 5.3e-3, 6.1e-2. Exact 2-shortcut ring (N=1500) gives
**3 first-passage peaks at τ=3.0e-4, 5.3e-3, 6.1e-2** (~1–7% of prediction) = capture-via-near
shortcut + capture-via-far shortcut + diffusive arrival. So m shortcuts turn the single fold
(double peak) into **fold hypersurfaces in b-space**, with open regions of 2 AND 3 peaks, organized
by a **cusp** at S₁=S₂=S₃=0. Higher-codimension catastrophe, exactly solvable.

## C. Beyond 1D — 2D lattice survival — VALIDATED
Same algebra exactly (det[I+B W_L(−μ)]=0). Numerical test on a 31×31 torus
(`code/dpma_2d_universality.py`, directed shortcut source→target): at β=0 a single diffusive
peak; turning on the shortcut **births a capture peak**, the two coexist over a β-window, and the
**diffusive peak's prominence → 0 (fold) at β_c^{2D}≈0.5–0.65**, leaving a single capture peak.
The 1D saddle-node **survives in 2D** — not a 1D artifact.
**Sophisticated 2D caveat (Pro):** a single-site 2D sink is *marginal* (log-divergent self-Green
function), so the RAW b_c(L) drifts ∼1/logL with system size — this is expected 2D point-trap
marginality, NOT a falsifier. The robust universality test is the **moment condition S₁=S₂=0 +
√-fold scaling** (t_±−t_c∼±C|b−b_c|^{1/2}, ΔΦ∼|b−b_c|^{3/2}), not b_c(L) convergence.
[Open: verify the √-fold scaling in 2D + the log-renormalized b_eff across L — next numerical step.]

## D. Robustness
Structurally stable while S₃≠0, ∇_b S₁≠0 hold: δb_c=−(S₁,ε/S₁,b)δε for any perturbation ε.
- disorder in hop rates: fold persists (even helps — breaks dark modes);
- q (laziness): trivial rescale μ→qμ, τ_c→τ_c/q; b_c robust (already q-reduced);
- placement/start: fold persists under small shifts.
Destroyers: source at a symmetry node (dark modes G_j=0), source coalescence (rank drop), source
near the absorbing boundary, or start→shortcut (early peak escapes to τ=0, interior test breaks).

## PRR significance
This is the universality section: the directed-shortcut second peak is a **generic fold of a
signed spectral FPT mixture from a low-rank non-Hermitian defect** — demonstrated (i) model-
independently (Woodbury), (ii) with an explicit rank-m determinant + a new triple-peak/cusp
phenomenon, and (iii) surviving on a 2D lattice. Combined with roadmap #1 (existence theorem
+ b_c(θ)), the "narrow 1D model" objection is substantially answered. Records: derivation in
session scratch; `code/dpma_multishortcut.py`, `code/dpma_2d_universality.py`.
