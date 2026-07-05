# Reproducibility package — DPMA saddle-node manuscript

This directory documents how to reproduce **every figure, table entry, and quoted number** in
`manuscript/dpma_prr_manuscript.tex` from the deterministic scripts in `../../code/`. It is the
staging content for the public repository + Zenodo DOI (to be created at submission; see
"Publishing" below — pushing is a human-gated step).

## Environment

```
Python 3.12.13
numpy==2.0.2
mpmath==1.4.1
matplotlib==3.9.4
pytest==9.0.3          # verification tests only
```

Install: `python -m pip install -r requirements.txt`

## One-command reproduction

```bash
cd research/reports/ring_lazy_jump_ext_rev2/code
bash ../manuscript/extras/reproducibility/make_all_figures.sh   # all figures + artifact tables
pytest test_dpma_identities.py -q                               # exact-identity verification tests
```

All outputs land in `../artifacts/figures/` and `../artifacts/tables/`. Every script is
deterministic; all randomized computations use **fixed seeds hard-coded in the scripts**.

## Script → manuscript map

| Script | Produces | Manuscript |
|---|---|---|
| `dpma_schematic.py` | `dpma_schematic.pdf` | Fig. 1 |
| `dpma_prr_figures.py` | `dpma_prr_figures.pdf`, `dpma_prr_extensions.pdf` | Fig. 2, Fig. 6 |
| `dpma_channel_mc.py` | `dpma_channel_mc.pdf` (+ log) | Fig. 3; MC π_sc; Table II row 12 |
| `dpma_start_dependence.py` | `dpma_start_dependence.pdf` | Fig. 4 |
| `dpma_brownian_fold.py` | `dpma_brownian_fold.pdf` | Fig. 5 |
| `dpma_saddle_node_bc_theta.py` | boundary machinery + table | b_c(θ); Table II row 6 |
| `dpma_saddle_node_certification.py` | certification table | exponents 0.498(1)/1.493(2) |
| `dpma_general_u_master_curve.py` | master-curve table | ≲6×10⁻⁵ agreement; N⁻²·⁰⁰ |
| `dpma_halfline_bstar.py` | half-line fold table | B*=0.7890262, c*=0.1579221 (App. C) |
| `dpma_endpoint_law.py` | endpoint table | b_c·θ=0.789026 over θ∈[0.20,0.27] |
| `dpma_normal_form.py` | normal-form table | prefactors 0.0247518 / 0.357444; −133.1 |
| `dpma_window_scan.py` | connectivity scan table | single-window verification (App. E) |
| `dpma_cusp_verify.py` | cusp residual table | Eq. (cusp); Table II row 11 |
| `dpma_multishortcut.py` | rank-2 machinery | triple peak; D₁₂ residuals (Table II row 10) |
| `dpma_2d_finite_lattice.py` | 2D torus machinery + table | β_c²ᴰ ≈ 0.69 |
| `dpma_2d_Lsweep.py` | L-sweep table | β_c²ᴰ(L), L=21–51 |
| `dpma_bcN_convergence.py` | threshold-convergence table | b_c,N − b_c ∝ N⁻²·⁰⁸ |
| `dpma_bd_convergence.py` | BD ℓ/Δt convergence table | App. E convergence paragraph |
| `dpma_measurement.py` | measurability table | ~4×10⁴ trials → ±0.25; ~2×10⁵ → ±0.1 |

## Fixed numerical parameters (as quoted in the paper)

- Monte Carlo: 4×10⁵ walkers, seed 12345/0 (see script), 59 logarithmic bins.
- Brownian dynamics: 6×10⁴ walkers, gate ℓ=0.02, Euler–Maruyama step 1.5×10⁻⁵, seeds logged.
- Root cutoffs: boundary bisection w≤40; connectivity scan w≤120; endpoint law wmax≈4/θ.
- 2D peak detection: capture/late split at t=120, relative height threshold 10⁻³·max F.
- Fold continuation window for exponent fits: b_c−b ∈ [1.4×10⁻³, 3.6×10⁻²], 7 points.

## Formal verification (Lean 4 + mathlib)

The exact algebraic layer of the manuscript (all finite identities, the Sherman–Morrison /
Green-function chain, the minimal-mode theorem, the normal-form prefactor algebra, and the
half-line transform algebra) is machine-verified in `../../code/formal_lean/` — 46 sorry-free
theorems, axiom report clean (only propext / Classical.choice / Quot.sound). See
`code/formal_lean/README.md` for the claim ↔ theorem map and the explicit three-tier scope
statement (exact algebra = Lean-proved; transcendental constants = multi-method numerics,
Table II; analytic limit statements = cited/hypothesis (F)). To re-verify:

```bash
cd ../../code/formal_lean     # copy/symlink to local disk first if the checkout is cloud-synced
lake exe cache get && lake build                     # zero errors, zero sorries
lake env lean AxiomsReport.lean                      # 46 lines, standard axioms only
```

## Publishing (human-gated)

To publish: copy `code/` + `artifacts/` + this directory into a standalone repository,
add LICENSE + CITATION.cff, push to GitHub, mint a Zenodo DOI, and replace the manuscript's
availability sentence with:

> The code and numerical data required to reproduce all figures and numerical values in this
> article are available in the public repository [name] and archived at Zenodo, DOI: [DOI].
