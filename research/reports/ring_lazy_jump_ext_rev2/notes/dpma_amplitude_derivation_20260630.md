# Rigorous derivation of the continuum amplitude G_{ξ,θ} (PRR roadmap principle-item #1)

Derived by ChatGPT gpt-5-5-pro (continued in the existence-theorem thread, chat 6a44a878, so it had
the full setup in context); **every intermediate independently verified here** (not just final G).
This upgrades G from "numerically verified formula" to "derived from the defect resolvent" — the
analytic engine (S_n moments, fold S₁=S₂=0, b_c) now rests on a derivation, not a fit.

## Derivation chain (H_b = −½ ∂ₓₓ + b δ_θ on (0,1), Dirichlet ends; z=−k²/2, μ=k²/2=2w²)
1. **Free resolvent** R_0(x,y;z)=2 sinh(qx_<)sinh(q(1−x_>))/(q sinh q), q=√(2z); continued to
   q=ik: r_0(x,y;k)=2 sin(kx_<)sin(k(1−x_>))/(k sin k).
2. **Defect resolvent (Sherman–Morrison, rank-one δ-sink):**
   r_b = r_0 − b r_0(x,θ)r_0(θ,y)/(1+b r_0(θ,θ)) = r_0 − 4b φ(x)φ(y)/(k sin k · D_θ),
   with φ_{k,θ}(x)=sin(k(1−θ))sin(kx) [x≤θ] or sin(kθ)sin(k(1−x)) [x≥θ], and
   **D_θ(k;b)=k sin k + 2b sin(kθ)sin(k(1−θ))** (pole condition 1+b r_0(θ,θ)=0 ⟺ D_θ=0).
3. **Eigenfunction:** ψ_j = φ_{k_j,θ}; continuous at θ, Dirichlet at 0,1, and satisfies the δ-sink
   jump ψ'(θ⁺)−ψ'(θ⁻)=2bψ(θ) ⟺ −k sin k = 2b sin(kθ)sin(k(1−θ)) ⟺ D_θ=0. **[verified 1.8e-14]**
4. **Residue = FPT amplitude:** survival transform Q̄_ξ(z)=∫₀¹ r_b(y,ξ;z)dy; f̄(z)=1−z Q̄; the pole
   at z=−μ_j gives (via k−k_j = −(z+μ_j)/k_j and the singular part)
   **G_j = μ_j φ(ξ) I / J = μ_j ψ_j(ξ)∫ψ_j / ∫ψ_j²** — normalization-independent.
5. **Closed forms** (k=2w): I(k,θ)=[sin(k(1−θ))(1−cos kθ)+sin(kθ)(1−cos k(1−θ))]/k **[verified vs
   ∫φ, 8.5e-10]**; J(k,θ)=½[θB²+(1−θ)A²]−AB sin k/(2k), A=sin kθ, B=sin k(1−θ) **[verified vs ∫φ²,
   3.4e-10]**. ⇒ **G_{ξ,θ}(w)=2w² φ_{w,θ}(ξ) I/J**.
6. **Key normalization identity (crux):** at a root, **J(k_j,θ)=sin(k_j)·D_k(k_j;b)/(4b)**, with
   D_k=sin k + k cos k + 2b[θ cos(kθ)sin(k(1−θ))+(1−θ)sin(kθ)cos(k(1−θ))]. **[verified 2.9e-15 —
   exact algebraic identity]**. This ties the residue to the determinant derivative (also gives
   D_k(k_j)≠0 ⟺ nondegenerate affected mode).
7. **Antipodal reduction:** θ=1/2 ⇒ G_{ξ,1/2}=4w(1−cosw)sin(2wξ*)/(sin²w[1+b(b+2)/(4w²)]),
   ξ*=min(ξ,1−ξ) — recovers the previously-verified antipodal amplitude.
8. **Node modes** (sin(nπθ)=0): free Dirichlet mode sin(nπx), G_n^node=nπ[1−(−1)ⁿ]sin(nπξ) (even
   n vanish); at ξ=θ all node modes vanish.

## Arbitration (this repo, q-free continuum; script inline, reproduces via roots()+φ)
All four intermediates verified at (θ,b)=(1/2,1.5),(1/3,1.5),(0.4,2.0), lowest 4 roots:
I 8.5e-10, J 3.4e-10, **J=sin(k)D_k/(4b) 2.9e-15**, jump 1.8e-14. Plus the full curve already
matched exact residues to ~1e-5 O(1/N) (`dpma_general_u_master_curve.py`).

## Honest status of the N→∞ limit (Pro, verbatim demarcation)
- **Proven by standard 1D operator theory** (under the finite-difference/form hypotheses A–E:
  ξ_N→ξ, θ_N→θ; bulk norm-resolvent H_N→H_0=−½∂ₓₓ; δ-sink form scaling V_{N,θ}∼bN; symmetrizable
  generator; simple isolated poles): H_N→H_b in resolvent sense, fixed isolated eigenvalues +
  eigenprojections converge ⇒ **fixed-mode residues G_{N,j}→G_j**.
- **Additional assumption (Hypothesis F), not proven for the exact ring discretization:** uniform C¹
  convergence of the moment sums S_{m,N}→S_m (m=1,2,3, incl. ∂_b) on a neighborhood of the fold
  (τ∈[τ_c/2,3τ_c/2]; NOT down to τ=0 — heat-kernel short-time singularity). Sufficient practical
  bound: μ_{N,j}≥cj², |G_{N,j}|≤Cj^r uniformly ⇒ uniform summability at τ_c>0.
- **Fold persistence [proven under F]:** Jacobian det DF_c=−S_{1,b}S_3; nondeg S_{1,b}≠0, S_3≠0 ⇒
  IFT gives a unique nearby finite-N fold with b_{c,N}−b_c=O(ε_N) (matching the observed O(N⁻²)).

## Takeaway
G is now **derived**, not fitted; the engine is self-contained. The single remaining rigor caveat
(uniform C¹ tail control at N→∞) is standard and clearly labeled — a candidate for a short lemma
if a referee insists. Manuscript App. B = this derivation.
