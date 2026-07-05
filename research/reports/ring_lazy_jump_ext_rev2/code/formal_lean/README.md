# DPMA formal audit package (Lean 4 + mathlib)

Machine-checked verification of the **exact algebraic content** of

> *Saddle-node bifurcation of first-passage-time densities induced by a directed shortcut*
> (`manuscript/dpma_prr_manuscript.tex`, report `ring_lazy_jump_ext_rev2`)

Every theorem below is proved **sorry-free** in Lean 4 against mathlib (pinned
toolchain `leanprover/lean4:v4.32.0-rc1`, mathlib `v4.32.0-rc1`; exact dependency
commits in `lake-manifest.json`). **46 theorems**; the generated axiom report
(`AxiomsReport.lean`, 2026-07-05 run) shows every one depends only on Lean's standard
`propext`, `Classical.choice`, `Quot.sound` — no `sorryAx`, no extra axioms.
Statement fidelity was additionally cross-audited per module against the manuscript
text by independent adversarial review (zero blocker findings; see
`notes/dpma_lean_formal_audit_20260705.md`).

## Scope: what is (and is not) formalized

The manuscript's mathematics has three layers. Formal verification applies to the
first; the audit is explicit about the other two.

| Tier | Content | Status |
|---|---|---|
| **1. Exact algebra** (finite identities, linear algebra, normal-form algebra) | everything in the table below | **Lean-proved, sorry-free** |
| **2. Certified numerics** (transcendental roots & spectral sums: `b_c(θ)`, `τ_c`, `B*`, `c_*`, prefactor *values* 0.0247518/0.357444, `N^{-2.08}` convergence, `β_c^{2D}≈0.68`, MC agreements) | Table II of the manuscript | cross-verified by 2–3 independent numerical methods each (`code/*.py`, `code/test_dpma_identities.py`); **not** formalized — verified interval arithmetic for oscillatory spectral sums is out of scope |
| **3. Analytic limit statements** (norm-resolvent continuum limit under hypothesis (F), Bromwich inversion contour, IFT fold persistence, window connectivity) | App. B "The N→∞ limit", App. C | classical results cited in the manuscript, with hypothesis (F) explicitly *stated as a hypothesis* in the text; connectivity is a numerical statement (App. E) |

## Claim ↔ theorem map

| Manuscript claim (anchor) | Lean theorem(s) | File |
|---|---|---|
| Chebyshev product identity `A_{N−r}A_u − A_{N−u}A_r = A_N A_{u−r}` (App. A, below eq:Fraw) | `sin_product_identity`, `chebyshev_product` | `FormalLean/Trig.lean` |
| Tridiagonal Green/cofactor structure of `G⁰` (App. A, eq:Guu) | `green_column_solves`, `green_jump`, `chebyshev_recurrence` | `FormalLean/Trig.lean` |
| Montroll determinant `D_u = aU_{N−1} + 2U_{u−1}U_{N−u−1}` from the SM denominator (Sec. II.B, eq:Du) | `montroll_determinant` | `FormalLean/Trig.lean` |
| Numerator collapse eq:Fraw → eq:num (App. A) | `numerator_collapse` | `FormalLean/Trig.lean` |
| Antipodal factorization `U_{N−1} = 2U_{N/2−1}T_{N/2}` (Sec. II.B) | `antipodal_factorization` | `FormalLean/Trig.lean` |
| δ-sink jump `φ'(θ⁺)−φ'(θ⁻) = −k sin k`; jump condition ⟺ `D_θ = 0` (App. B step 3; eq:Dtheta) | `branch_deriv_left/right`, `jump_value`, `jump_iff_secular`, `phi_continuous_at_theta`, `phi_dirichlet` | `FormalLean/JumpCondition.lean` |
| Antipodal collapse `D_{1/2}(2w;b)=0 ⟺ tan w = −2w/b` (Sec. II.C) | `antipodal_collapse` | `FormalLean/JumpCondition.lean` |
| Normalization identity `J = sin(k)D_k/(4b)` at roots (App. B step 6, eq:JD) | `J_identity_abstract`, `J_identity` | `FormalLean/Normalization.lean` |
| Antipodal reductions: `sin²w(4w²+b²)=4w²`, `J`-closed form, amplitude `G = 4w(1−cos w)/(sin w(1+b(b+2)/4w²))` (App. B step 7) | `antipodal_sin_sq`, `antipodal_J`, `antipodal_G` | `FormalLean/Normalization.lean` |
| `Φ' = −S₁`, `Φ'' = S₂` for signed exponential mixtures (Sec. III.A, eq:Sn/eq:fold) | `Phi_hasDerivAt`, `S1_hasDerivAt` | `FormalLean/MinimalModes.lean` |
| Two-mode fold impossible, even with signs (Sec. III.D) | `no_two_mode_fold`, `no_two_mode_fold_exp` | `FormalLean/MinimalModes.lean` |
| Fold ratio `A₁:A₂:A₃ = (μ₃−μ₂):(μ₁−μ₃):(μ₂−μ₁)` ⇒ alternating signs (Sec. III.D, App. C) | `three_mode_ratio`, `three_mode_alternating` | `FormalLean/MinimalModes.lean` |
| Normal-form extrema, gap `2√(2S_{1,b}/S₃)·√(b_c−b)` (App. C, eq:nf/eq:prefac) | `nf_roots`, `nf_gap`, `Phinf_hasDerivAt` | `FormalLean/NormalForm.lean` |
| Prominence `ΔΦ = (2/3)S₃δ³ = (4√2/3)S_{1,b}^{3/2}S₃^{−1/2}(b_c−b)^{3/2}` (App. C, eq:prefac) | `nf_prominence_exact`, `nf_prominence`, `prominence_constant` | `FormalLean/NormalForm.lean` |
| Sherman–Morrison defect column (App. A, eq:smcol; Sec. V.A Woodbury rank-one case) | `sherman_morrison_solve` | `FormalLean/PiSc.lean` |
| Splitting probability `π_sc = 2min(r,u)[N−max(r,u)]/(aN+2u(N−u))` (App. A, eq:pisc) | `pisc_solves`, `pisc_value` | `FormalLean/PiSc.lean` |
| Antipodal `π_sc = r*/(a+N/2)`, `r* = min(r,N−r)` (App. A) | `pisc_antipodal` | `FormalLean/PiSc.lean` |
| Half-line transform eq:fhl (denominator, SM structure, boundary flux, Lévy limit `B=0`) | `r0_11_closed`, `sm_scalar`, `flux_at_zero`, `fhat_assembly`, `fhat_levy` | `FormalLean/HalfLine.lean` |
| Branch-cut integrand of eq:phihl (incl. positivity form `(g+cos v)²+sin²v` and strict positivity on the support) | `cut_g_transform`, `cut_normSq`, `cut_denominator_form`, `cut_denominator_pos`, `cut_im` | `FormalLean/HalfLine.lean` |

Encoding notes (fidelity):

- Chebyshev-polynomial statements are formalized in the `y = cos φ` trig
  parametrization (`A_m = sin(mφ)/sin φ`) — the manuscript's own proof route — and
  hold for **all real** index parameters, strictly generalizing the integer statements.
- `π_sc` is certified through the first-step (backward-equation) linear system of the
  killed walk — the same linear system as the manuscript's resolvent expression
  `π_sc = λ⟨u|(I−P_λ)⁻¹|r⟩` — by exhibiting the closed form as its exact solution,
  together with the constructive Sherman–Morrison solve used in eq:smcol.
- The normal-form module certifies the **prefactor algebra** of eq:prefac exactly for
  the truncated normal form eq:nf (the manuscript's `≃`); the numerical values
  0.0247518/0.357444 then follow from the Tier-2 fold data (S₃, S_{1,b}).

## Building / verifying

```bash
# one-time: install elan (Lean toolchain manager), then from this directory:
lake exe cache get   # fetch prebuilt mathlib (~7 GB in .lake/)
lake build           # must end with no errors and no 'sorry' warnings
grep -rn "sorry\|admit\|native_decide" FormalLean/  # must be empty
```

Axiom hygiene: `AxiomsReport.lean` prints the axioms of every audited theorem;
building it must show only `propext`, `Classical.choice`, `Quot.sound`.

Note (OneDrive): do not build inside a cloud-synced checkout; copy or symlink this
directory to local disk first (same policy as the repo's `od-divert` setup — the
committed sources here are build-artifact-free; `.lake/` is git-ignored).
