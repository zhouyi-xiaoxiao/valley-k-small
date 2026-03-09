# Agent report (valley-k-small)

> Note (2025-12-16): the repo was reorganized so each report lives under `reports/<report_name>/` with its own `code/`, `figures/`, `data/`, `tables/`. Paths in this document follow the new structure; see `reports/README.md` for layout. The former `bimodality_flux_report` is now `reports/ring_lazy_flux/` (CN/EN).

## 2026-01-04 — Repo maintenance (summary automation + cleanup)

### Added scripts and docs
- Added `scripts/update_research_summary.py` (refreshes date + auto index in `docs/RESEARCH_SUMMARY.md`).
- Added `scripts/cleanup_local.py` (removes local artifacts; optional venv removal).
- Added `scripts/README.md`; updated `README.md`, `docs/README.md`, and `AGENTS.md` to document new scripts.

### Cleanup actions (logged commands)
- `find . -name .DS_Store`
- `find . -type d -name __pycache__`
- `find reports -type d -name build`
- `find . -name .DS_Store -delete`
- `rm -f .DS_Store`
- `rm -rf .venv venv`
- `rm -rf reports/ring_lazy_jump_ext/build reports/ring_lazy_jump_ext/code/__pycache__`
- `python3 scripts/update_research_summary.py`

### Summary refresh (self-contained update)
- `python3 scripts/update_research_summary.py`
### Summary refresh (latest progress block)
- `python3 scripts/update_research_summary.py`
### Summary refresh (context overview)
- `python3 scripts/update_research_summary.py`

### Removed artifacts
- All `.DS_Store` files under repo root and report/doc folders (removed twice; can reappear on macOS).
- Local virtualenvs: `.venv/`, `venv/`.
- LaTeX aux dir: `reports/ring_lazy_jump_ext/build/`.
- Python bytecode cache: `reports/ring_lazy_jump_ext/code/__pycache__/`.

## 2026-01-04 — Research summary made self-contained

### What changed
- Expanded `docs/RESEARCH_SUMMARY.md` to be standalone: added repo overview, key symbols, reproduction commands, and maintenance notes.
- Updated ChatGPT guidance inside the summary for model-rule disambiguation.

### Follow-up
- Added a “latest progress” placeholder and clarified that the summary is intended to be shared standalone (no repo access).
- Added a one-paragraph project overview and a “current focus” checklist for AI context.

## 2025-12-15 — Lazy ring + shortcut bimodality (flux)

### Goal
- Implement a **time-domain/flux** (master equation) solver for the first-passage-time pmf `f(t)` on a **lazy ring** with a **single directed shortcut**, plus a **robust bimodality** detector; add a short LaTeX methodology note; run a small verification demo.

### What I added
- `reports/ring_lazy_flux/code/lazy_ring_flux_bimodality.py`: O(N) per step, no dense `(N×N)` matrix; supports two shortcut constructions (`selfloop`, `rewire`); outputs tail-mass upper bound via survival probability; includes a robust bimodality test.
- `reports/ring_lazy_flux/ring_lazy_flux_cn.tex`: “paper-style” explanation of why flux is preferred over AW inversion for bimodality/shape detection tasks, with reproducibility command.

### Verification (demo run)
- Environment:
  - `python3 -V` → Python 3.9.6
  - `numpy` → 2.0.2
- Command:
  - `python3 reports/ring_lazy_flux/code/lazy_ring_flux_bimodality.py --demo`
- Expected checks:
  - `mass = sum_t f(t)` close to 1 (any shortfall is bounded by reported `surv`)
  - `surv` small at stop (tail mass upper bound)
  - `bimodal=True` for some parameter choices (shows the end-to-end pipeline works)

### Observed output (excerpt)
- Demo produced bimodal cases (example):
  - `q=0.90`, `selfloop`, `beta=0.05` (`p=0.0050`) → `bimodal=True`, `top2=((1, 0.005), (11, 0.0006993753360597668))`
- Single-case run (same parameters) for a full summary line:
  - `python3 reports/ring_lazy_flux/code/lazy_ring_flux_bimodality.py --N 101 --q 0.9 --start 1 --target 50 --model selfloop --u 1 --v 50 --p 0.005 --Tmax 50000 --eps-surv 1e-12`
  - Output:
    - `computed_steps=50000 mass=0.9999999999960359 surv=3.972e-12 bimodal=True`
    - `top2=((1, 0.005), (11, 0.000699375336059767)) valley=0.0004749999999999999`

### LaTeX build
- Compiled `valley-k-small/reports/ring_lazy_flux/ring_lazy_flux_cn.tex` to `valley-k-small/reports/ring_lazy_flux/ring_lazy_flux_cn.pdf` via:
  - `latexmk -xelatex -interaction=nonstopmode -halt-on-error ring_lazy_flux_cn.tex`
  - Updated the LaTeX to include the latest scan results/parameters (K=6 and K=2 summaries) and recompiled the PDF.
  - Added bimodality curve plots (`example_curves` + `peak_times`) and representative peak time tables, then recompiled again.
  - Refocused the report to the simplest setting (k=1 / K=2 lazy ring) and switched the plot style to stem/bar to avoid “oscillatory” misinterpretation from line-connecting a discrete pmf.

### Bimodality conclusion (deterministic scan)
- Ran:
  - `python3 reports/ring_valley_dst/code/bimodality_flux_scan.py --sc-src 6 --max-steps 2000 --eps-stop 1e-14`
  - `python3 reports/ring_valley_dst/code/bimodality_flux_scan.py --sc-src 1 --max-steps 2000 --eps-stop 1e-14`
- Results (N=100, K=6, n0=1, target=50):
  - `sc-src=6`: `n_fig3_bimodal=15`, `n_robust_bimodal=14`, `robust_bimodal_dsts={43..49,51..57}`
  - `sc-src=1`: `n_fig3_bimodal=18`, `n_robust_bimodal=7`, `robust_bimodal_dsts={36,37,38,39,62,63,64}`

### K=2 exploration (scan targets; src=n0)
- Note: for even `N` with `K=2` the walk is periodic (parity effects), which can create many local maxima; using odd `N` (e.g. 101) avoids strict parity constraints.
- Ran (all with `N=101`, `K=2`, `n0=1`, `sc-src=1`, `max-steps=8000`, `min-sep=50`, `require-valley`, `valley-frac=0.7`):
  - `--target 30`  → `n_valid=98`, `n_robust_bimodal=92`
  - `--target 40`  → `n_valid=98`, `n_robust_bimodal=92`
  - `--target 51`  → `n_valid=98`, `n_robust_bimodal=92`
  - `--target 60`  → `n_valid=98`, `n_robust_bimodal=92`
  - `--target 70`  → `n_valid=98`, `n_robust_bimodal=91`

### K=2 lazy walk check (odd/even N)
- Ran the lazy-ring selfloop model in `reports/ring_lazy_flux/code/lazy_ring_flux_bimodality.py` for both even and odd N:
  - `python3 reports/ring_lazy_flux/code/lazy_ring_flux_bimodality.py --N 100 --q 0.9 --start 1 --target 50 --model selfloop --u 1 --v 50 --p 0.005 --Tmax 200000 --eps-surv 1e-14`
  - `python3 reports/ring_lazy_flux/code/lazy_ring_flux_bimodality.py --N 101 --q 0.9 --start 1 --target 51 --model selfloop --u 1 --v 51 --p 0.005 --Tmax 200000 --eps-surv 1e-14`
- Both reported `bimodal=True` with `top2=((1, 0.005), (11, 0.000699...))`.

### User-provided dense exact check (paper criterion)
- Implemented the provided dense absorbing-chain code as `reports/ring_lazy_flux/code/user_dense_exact_scan.py` and ran:
  - `python3 reports/ring_lazy_flux/code/user_dense_exact_scan.py --Tmax 30000 --eps 1e-12`
- Observed (excerpt): for `N=100/101`, `q=0.60..0.80` the `selfloop` model at `beta=0.05` often gave `paper=True` and `macro=True` (two separated peaks); at `q=0.90` the output shows many local modes and `paper=True` can hold while `macro` may fail depending on peak locations.
- Note: NumPy emitted `matmul` overflow/invalid warnings during this dense iteration, so this approach may need extra numerical care for long horizons (flux recursion avoids this).

### Small-N existence proof (k=1, i.e. K=2 lazy ring)
- Using the flux method in `valley-k-small/reports/ring_lazy_flux/code/lazy_ring_flux_bimodality.py`, a quick search over small N found bimodality already at `N=8` with a directed shortcut from start directly to target:
  - `python3 reports/ring_lazy_flux/code/lazy_ring_flux_bimodality.py --N 8 --q 0.9 --start 1 --target 4 --model selfloop --u 1 --v 4 --p 0.002 --Tmax 200000 --eps-surv 1e-14`
  - Output reports `bimodal=True` with `top2=((1, 0.002), (15, 0.030396...))`.
- Plotted this small-N curve and embedded it in the LaTeX PDF:
  - Figure: `valley-k-small/reports/ring_lazy_flux/figures/lazy_ring_flux_bimodality/lazy_K2_smallN_N8.pdf`
  - Updated PDF: `valley-k-small/reports/ring_lazy_flux/ring_lazy_flux_cn.pdf`

### k=1 (K=2) clean bimodal example (non-oscillatory)
- The N=8 case has multiple local maxima (discrete-time micro-structure), which can look “oscillatory”. A cleaner paper-style bimodality example (exactly 2 strict local peaks) is:
  - `N=100`, `q=0.6`, `n0=1`, `target=50`, shortcut `u=n0+5=6 -> v=target+1=51`, `p=0.02`
  - `python3 reports/ring_lazy_flux/code/lazy_ring_flux_bimodality.py --N 100 --q 0.6 --start 1 --target 50 --model selfloop --u 6 --v 51 --p 0.02 --Tmax 200000 --eps-surv 1e-14`
  - Peaks (thresh=1e-12): `t1=52`, `t2=656` (ratio `t2/t1≈12.6`)
- Generated plot + embedded into the simplified PDF:
  - Figure: `valley-k-small/reports/ring_lazy_flux/figures/lazy_ring_flux_bimodality/lazy_K2_clean_example_N100.pdf` via `python3 reports/ring_lazy_flux/code/plot_lazy_k2_example.py`
  - Updated PDF: `valley-k-small/reports/ring_lazy_flux/ring_lazy_flux_cn.pdf`

### Equal-probability baseline (stay/left/right = 1/3)
- Updated the simplified PDF to focus on the equal-probability lazy walk (`q=2/3`) and a small-N example:
  - Example parameters: `N=10`, `q=2/3`, `start=1`, `target=5`, shortcut `u=1 -> v=5`, `p=0.006666...`
  - Figure: `valley-k-small/reports/ring_lazy_flux/figures/lazy_ring_flux_bimodality/lazy_K2_equalprob_N10.pdf` via `python3 reports/ring_lazy_flux/code/plot_lazy_k2_example.py`
  - PDF: `valley-k-small/reports/ring_lazy_flux/ring_lazy_flux_cn.pdf`
- The PDF also includes a small table of additional N where the strict-local-peak count is exactly 2 under the same baseline.

## 2025-12-15 — AW inversion (Chebyshev closed form) + small-N target scan (k=1 / K=2)

### Goal
- Switch the k=1 (K=2) lazy-ring “bimodality existence proof” to an **analytic curve** pipeline:
- evaluate the closed-form generating function $\~F(z)$ from `reports/ring_deriv_k2/note_k2.pdf`;
  - recover $f(t)$ by **AW/Cauchy inversion** (FFT);
  - cross-check against the non-matrix flux recursion.

### What changed
- `plot_lazy_k2_example.py`: switched to **bar/marker** plotting (discrete pmf; avoids misleading “oscillations” from line-connecting spikes) and added a small CLI to render other N/targets.
- `reports/ring_lazy_flux/code/plot_lazy_k2_aw_distance_scan.py`: added an AW-based scan figure (N vs ring-distance) that visualizes where **macro-bimodality** holds and reports the late-peak time `t2`.
- `reports/ring_lazy_flux/ring_lazy_flux_cn.tex`: refocused on k=1/K=2 equal-probability (`q=2/3`), embedded:
  - `reports/ring_lazy_flux/figures/lazy_ring_flux_bimodality/lazy_K2_equalprob_N10_aw_vs_flux.pdf` (even N example, exactly 2 strict peaks),
  - `reports/ring_lazy_flux/figures/lazy_ring_flux_bimodality/lazy_K2_equalprob_N11_target5_aw_vs_flux.pdf` (odd N example, exactly 2 strict peaks),
  - `reports/ring_lazy_flux/figures/lazy_ring_flux_bimodality/lazy_K2_equalprob_macro_scan_N6_20.pdf` (scan summary).

### Key deterministic results (equal-prob baseline)
- Even N example (clean 2-peak case):
  - `python3 reports/ring_lazy_flux/code/plot_lazy_k2_example.py`
  - Output: `#peaks(thresh=1e-07)=2 top2=[(1, 0.006666...), (10, 0.026234...)]`
  - AW vs flux: `max|aw-flux|≈9e-17`.
- Odd N example (clean 2-peak case):
  - `python3 reports/ring_lazy_flux/code/plot_lazy_k2_example.py --N 11 --target 5 --v 5 --tplot 60`
  - Output: `#peaks(thresh=1e-07)=2 top2=[(1, 0.006666...), (10, 0.022512...)]`
- Small-N scan (macro criterion: `t2/t1>=10`, `thresh=1e-7`, `second_frac=1%`):
  - `python3 reports/ring_lazy_flux/code/plot_lazy_k2_aw_distance_scan.py`
  - Observed: for this setup (shortcut `u=n0 -> v=target`, `beta=0.02`), **macro-bimodality starts at N=10** and occurs mainly for larger ring distances (near antipodal targets).

### LaTeX build
- `cd valley-k-small/reports/ring_lazy_flux && latexmk -xelatex -interaction=nonstopmode -halt-on-error ring_lazy_flux_cn.tex`
- Output: `valley-k-small/reports/ring_lazy_flux/ring_lazy_flux_cn.pdf`

## 2025-12-15 — Full N-scan table + multi-figure AW gallery + English report

### Goal
- Enumerate **all endpoints** (for each N) from small → larger N and append a **full data table** to the report.
- Generate **more AW-inversion figures** (multi-panel PDFs).
- Produce an **English LaTeX report** in parallel.
- Keep `reports/ring_lazy_flux/` clean: only `.tex/.pdf` at top level; LaTeX aux files go to `reports/ring_lazy_flux/build/`.

### Full scan (AW analytic)
- Script: `scan_lazy_k2_aw_fulltable.py` (optimized for the scan setting `u=n0 -> v=target`, batched over distances).
- Run:
  - `python3 scan_lazy_k2_aw_fulltable.py --N-min 3 --N-max 60`
- Outputs:
  - CSV + metadata (non-tex/pdf) → `build/lazy_k2_aw_scan/lazy_K2_equalprob_full_scan.csv` and `build/lazy_k2_aw_scan/lazy_K2_equalprob_full_scan_meta.txt`
  - Longtable inputs → `reports/ring_lazy_flux/tables/lazy_K2_equalprob_full_scan_table_cn.tex` and `reports/ring_lazy_flux/tables/lazy_K2_equalprob_full_scan_table_en.tex`
- Observed scan summary (equal-prob baseline `q=2/3`, `beta=0.02`):
  - Macro-bimodality first appears at `N=10`.
  - For every `N=10..60`, at least one endpoint is macro-bimodal under the report criterion (`h_min=1e-7`, `second_frac=1%`, `t2/t1>=10`).

### Additional AW figures (multi-figure PDFs)
- Heatmap updated to the full range:
  - `python3 reports/ring_lazy_flux/code/plot_lazy_k2_aw_distance_scan.py --N-min 3 --N-max 60`
  - Output: `reports/ring_lazy_flux/figures/lazy_ring_flux_bimodality/lazy_K2_equalprob_macro_scan_N3_60.pdf`
  - Note: y-axis tick labels are downsampled to avoid overlap for large N ranges (implemented in `reports/ring_lazy_flux/code/plot_lazy_k2_aw_distance_scan.py`).
- Multi-panel antipodal galleries:
  - `python3 reports/ring_lazy_flux/code/plot_lazy_k2_aw_antipodal_panels.py --group even_small` → `reports/ring_lazy_flux/figures/lazy_ring_flux_bimodality/lazy_K2_aw_antipodal_even_small.pdf`
  - `python3 reports/ring_lazy_flux/code/plot_lazy_k2_aw_antipodal_panels.py --group odd_small`  → `reports/ring_lazy_flux/figures/lazy_ring_flux_bimodality/lazy_K2_aw_antipodal_odd_small.pdf`
  - `python3 reports/ring_lazy_flux/code/plot_lazy_k2_aw_antipodal_panels.py --group even_medium` → `reports/ring_lazy_flux/figures/lazy_ring_flux_bimodality/lazy_K2_aw_antipodal_even_medium.pdf`

### Reports
- Chinese report (appendix includes full table):
  - Source: `reports/ring_lazy_flux/ring_lazy_flux_cn.tex`
  - PDF: `reports/ring_lazy_flux/ring_lazy_flux_cn.pdf`
- English report:
  - Source: `reports/ring_lazy_flux/ring_lazy_flux_en.tex`
  - PDF: `reports/ring_lazy_flux/ring_lazy_flux_en.pdf`

### LaTeX build hygiene (“non pdf/tex → build”)
- Built with aux dir:
  - `cd reports/ring_lazy_flux && latexmk -xelatex -interaction=nonstopmode -halt-on-error -auxdir=build -emulate-aux-dir ring_lazy_flux_cn.tex`
  - `cd reports/ring_lazy_flux && latexmk -xelatex -interaction=nonstopmode -halt-on-error -auxdir=build -emulate-aux-dir ring_lazy_flux_en.tex`
- Removed top-level LaTeX aux files from `reports/ring_lazy_flux/` so only `.tex/.pdf` remain at that level.

## 2025-12-15 — Compare against `valley` (K=2 shows no bimodality there)

### User request
- Investigate why `valley` reports **no bimodality for K=2** (no second peak under the Fig.3 rule), and include that contrast in the k=1/K=2 report.

### What I found in the existing code/report
- `reports/ring_valley/ring_valley.tex` and `reports/ring_valley/code/valley_study.py` use a **different probability model** than the lazy/selfloop model:
  - Non-lazy walk (no self-loop), uniform jump among K neighbors.
  - Add one directed edge at the shortcut source and renormalize outgoing probabilities to `1/(K+1)` at that node (so original neighbor edges drop from `1/K` to `1/(K+1)`).
  - For `K=2`, they coarse-grain by 2 steps before running the Fig.3 peak rule to suppress parity micro-peaks.
- Their saved scan output `reports/ring_valley/data/bimodality_scan.json` indeed has `K=2` with `bimodal_count=0` (while `K=4,6,8` do have bimodal ranges).

### Deterministic reproduction (exact master equation)
- Script: `reports/ring_lazy_flux/code/scan_valley_report_k2_summary.py`
- Ran:
  - `python3 reports/ring_lazy_flux/code/scan_valley_report_k2_summary.py`
- Output (non-tex/pdf → `reports/ring_lazy_flux/build/`):
  - `reports/ring_lazy_flux/build/valley_report_k2_compare/valley_report_k2_summary.csv`
  - `reports/ring_lazy_flux/build/valley_report_k2_compare/valley_report_k2_summary_meta.txt`
- Result: for representative even `N={10,20,50,100,160}`, after 2-step coarse-graining the `valley` model has **exactly 1 dominant peak** (so not bimodal).

### Comparison figure
- Script: `reports/ring_lazy_flux/code/plot_k2_valley_report_contrast.py`
- Ran:
  - `python3 reports/ring_lazy_flux/code/plot_k2_valley_report_contrast.py`
- Output:
  - `reports/ring_lazy_flux/figures/lazy_ring_flux_bimodality/k2_valley_report_vs_lazy_contrast.pdf`
  - Left panel: `valley` model (coarse-grained) shows a single peak.
  - Right panel: lazy selfloop model with the same shortcut geometry `u=6 -> v=51` shows two dominant peaks (AW + flux overlay).

### Report integration
- Chinese report:
  - Added a comparison section + table + figure in `reports/ring_lazy_flux/ring_lazy_flux_cn.tex`
  - Table inputs: `reports/ring_lazy_flux/tables/valley_report_k2_summary_cn.tex`
  - PDF: `reports/ring_lazy_flux/ring_lazy_flux_cn.pdf`
- English report:
  - Updated `reports/ring_lazy_flux/ring_lazy_flux_en.tex`
  - Table inputs: `reports/ring_lazy_flux/tables/valley_report_k2_summary_en.tex`
  - PDF: `reports/ring_lazy_flux/ring_lazy_flux_en.pdf`

## 2025-12-15 — “equal shortcut probability” update (equal4 = 1/4 each at u)

### User request
- Change the shortcut rule so that at the shortcut source `u` the walker chooses **stay / left / right / shortcut** with **equal probability**.
- For the lazy walk this means: **each is `1/4`** at node `u` (the shortcut, when chosen, deterministically jumps to `v`).

### Code changes
- Added `model="equal4"` to `reports/ring_lazy_flux/code/lazy_ring_flux_bimodality.py`:
  - At node `u`, override the outgoing distribution to `{stay,left,right,shortcut} = 1/4` each.
  - Elsewhere keep the baseline lazy ring with parameter `q` (in the report, `q=2/3` gives stay/left/right each `1/3` on non-shortcut nodes).
- Extended `lazy_ring_aw_chebyshev.py` with an analytic AW pipeline for this rule:
  - Implemented a **rank-1 (single-column) defect update** (Sherman–Morrison) on the defect-free ring propagator `\tilde Q(d,z)`.
  - New entry points:
    - `fpt_genfun_column_defect(...)` (general single-column defect → FPT generating function)
    - `fpt_genfun_equal4(...)` (equal4 shortcut-source rule)
    - `fpt_pmf_aw_equal4(...)` (AW inversion for equal4)

### Verification (AW vs flux)
- Quick equality check (machine precision) for a small case:
  - `python3 - <<'PY' ... fpt_pmf_aw_equal4(...) vs fpt_pmf_flux_ring(..., model=\"equal4\") ... PY`
  - Observed `max|AW-flux| ≈ 3.5e-17` for `N=10,q=2/3,start=1,target=5,u=1,v=5`.

### Paper-like geometry scan (main conclusion)
- Geometry (per `N`):
  - `start=n0=1`, `target=floor(N/2)`, `u=n0+5`, `v=target+1`
- Ran:
  - `python3 scan_lazy_k2_equal4_paper_geometry.py --N-min 10 --N-max 200 --q 0.6666666667 --Tmax 200000 --eps-surv 1e-14`
- Output:
  - CSV: `build/lazy_k2_equal4_paper_geometry/scan_equal4_paper_geometry.csv`
  - Meta: `build/lazy_k2_equal4_paper_geometry/scan_equal4_paper_geometry_meta.txt`
  - Summary tables: `reports/ring_lazy_flux/tables/lazy_K2_equal4_paper_geometry_summary_cn.tex` and `reports/ring_lazy_flux/tables/lazy_K2_equal4_paper_geometry_summary_en.tex`
- Result:
  - `paper_bimodal_count=0`, `macro_bimodal_count=0` over `N=10..200` (with `h_min=1e-7`, `second_frac=1%`, `t2/t1>=10`).
  - I.e. under this “equal4” rule, the paper-like geometry is **unimodal** for all scanned `N`.

### Figure + PDF updates
- Generated a direct selfloop-vs-equal4 comparison figure at `N=100`:
  - `python3 plot_lazy_k2_paper_geometry_equal4_compare.py --N 100 --q 0.6666666667 --beta 0.02 --tplot 2500`
  - Output: `reports/ring_lazy_flux/figures/lazy_ring_flux_bimodality/lazy_K2_paper_geometry_selfloop_vs_equal4_N100.pdf`
- Updated both reports to include:
  - The equal4 rule definition (`1/4` each at `u`)
  - The scan conclusion (no bimodality for the paper-like geometry)
  - The summary table and the comparison figure
- Recompiled:
  - `cd reports/ring_lazy_flux && latexmk -xelatex -interaction=nonstopmode -halt-on-error -auxdir=build -emulate-aux-dir ring_lazy_flux_cn.tex`
  - `cd reports/ring_lazy_flux && latexmk -xelatex -interaction=nonstopmode -halt-on-error -auxdir=build -emulate-aux-dir ring_lazy_flux_en.tex`

### What “p” and “q” mean (clarification)
- `q` (baseline lazy ring): total move probability (so stay is `1-q`, and left/right are `q/2` each).
  - Equal-prob non-shortcut nodes (stay/left/right each `1/3`) corresponds to `q=2/3`.
- `p` (selfloop rule only): probability moved from the self-loop at `u` to the directed edge `u->v`.
  - This is a different rule than equal4; equal4 does **not** use a free `p` parameter (it fixes `P(u->v)=1/4`).

### Doc clarity fix
- To avoid confusing “equal-prob baseline” (non-shortcut nodes) with “equal4 at u”:
  - Updated `reports/ring_lazy_flux/ring_lazy_flux_cn.tex` to explicitly label the `N=10` example as **selfloop (not equal4)** and add a cross-reference to the equal4 section.
  - Updated `reports/ring_lazy_flux/ring_lazy_flux_en.tex` similarly.
  - Recompiled both PDFs with `latexmk ... -auxdir=build -emulate-aux-dir`.

### Figure title fix
- The N=10 overlay figure title was too long and got clipped in the PDF. Fixed by splitting the title into 2 lines in:
  - `plot_lazy_k2_example.py`
- Regenerated the figure and rebuilt both reports:
  - figure: `reports/ring_lazy_flux/figures/lazy_ring_flux_bimodality/lazy_K2_equalprob_N10_aw_vs_flux.pdf`
  - PDFs: `reports/ring_lazy_flux/ring_lazy_flux_cn.pdf`, `reports/ring_lazy_flux/ring_lazy_flux_en.pdf`

## 2025-12-15 — Selfloop small-$p$ collection + “large $p$ suppresses bimodality” evidence

### User request
- “Scan and record” the selfloop probability scale `p` (or `beta`) and support the hypothesis that **large shortcut probability makes bimodality unlikely**.
- Collect the **small-$p$ bimodal curves** and bundle them together.

### Scans (deterministic, flux)
- Paper-like geometry per `N`:
  - `start=n0=1`, `target=floor(N/2)`, `u=n0+5`, `v=target+1`
  - baseline `q=2/3` (non-shortcut nodes: stay/left/right each `1/3`)
  - selfloop shortcut: `p = beta*(1-q)` taken from the self-loop at `u`

- N-scan at small p (`beta=0.02` so `p=0.006666...`):
  - `python3 scan_lazy_k2_selfloop_paper_geometry_N_scan.py --N-min 10 --N-max 200 --q 0.6666666667 --beta 0.02 --Tmax 200000 --eps-surv 1e-14`
  - Output: `build/lazy_k2_selfloop_paper_geometry/scan_selfloop_paper_geometry_N10_200_beta0.02.csv`
  - Result summary: `paper_bimodal_count=143`, `macro_bimodal_count=132` over `N=10..200` (criterion `h_min=1e-7`, second peak ≥1%, macro `t2/t1>=10`).

- Beta scan at fixed `N=100` (shows threshold where bimodality disappears):
  - `python3 scan_lazy_k2_selfloop_beta_scan.py --N 100 --q 0.6666666667 --betas "0,0.0005,0.001,0.002,0.005,0.01,0.02,0.03,0.05,0.07,0.1,0.15,0.2,0.3,0.5,1.0" --Tmax 200000 --eps-surv 1e-14`
  - Output: `build/lazy_k2_selfloop_paper_geometry/beta_scan_N100_q0.666667_uoff5_voff1.csv`
  - Observation: paper/macro bimodality drops to 0 starting around `beta≈0.07` (i.e. `p≈0.023`), supporting “large p suppresses bimodality”.

### Plots (AW analytic + flux overlay)
- Small-$p$ bimodal curve collection (bundled):
  - `python3 plot_lazy_k2_selfloop_smallp_gallery.py --q 0.6666666667 --beta 0.02 --tplot 5000 --oversample 8 --r-pow10 18.0`
  - Output: `reports/ring_lazy_flux/figures/lazy_ring_flux_bimodality/lazy_K2_selfloop_smallp_gallery_beta0.02.pdf` (multi-page)
- Beta sensitivity panels at `N=100`:
  - `python3 plot_lazy_k2_selfloop_beta_sensitivity.py --N 100 --q 0.6666666667 --betas "0.002,0.005,0.01,0.02,0.05,0.1" --tplot 2500`
  - Output: `reports/ring_lazy_flux/figures/lazy_ring_flux_bimodality/lazy_K2_selfloop_beta_sensitivity_N100.pdf`
- Beta scan table (TeX):
  - `python3 make_lazy_k2_selfloop_beta_scan_table.py`
  - Output: `reports/ring_lazy_flux/tables/lazy_K2_selfloop_beta_scan_N100_cn.tex` and `reports/ring_lazy_flux/tables/lazy_K2_selfloop_beta_scan_N100_en.tex`

### Report updates + rebuild
- Embedded the new evidence into both CN/EN PDFs:
  - Added `pdfpages` and included the small-$p$ gallery as an appendix.
  - Added a beta-scan subsection + table + sensitivity figure.
- Rebuilt:
  - `cd reports/ring_lazy_flux && latexmk -xelatex -interaction=nonstopmode -halt-on-error -auxdir=build -emulate-aux-dir ring_lazy_flux_cn.tex`
  - `cd reports/ring_lazy_flux && latexmk -xelatex -interaction=nonstopmode -halt-on-error -auxdir=build -emulate-aux-dir ring_lazy_flux_en.tex`

## 2025-12-15 — Compact bimodal gallery + “next steps” notes (CN/EN)

### User request
- Make the small-$p$ bimodal gallery more compact (multiple plots per page, not one-$N$-per-page).
- Add “possible next steps” to both CN/EN reports (scan $(q,p)$ / $(q,\beta)$), without actually running the scans.

### New compact gallery
- Added script:
  - `plot_lazy_k2_selfloop_smallp_gallery_compact.py` (AW analytic, multi-panel pages).
- Generated compact PDF (default: 3×2 panels per page):
  - `python3 plot_lazy_k2_selfloop_smallp_gallery_compact.py --q 0.6666666667 --beta 0.02 --tplot 5000 --ncols 3 --nrows 2`
  - Output: `reports/ring_lazy_flux/figures/lazy_ring_flux_bimodality/lazy_K2_selfloop_smallp_gallery_compact_beta0.02.pdf`

### Report updates + rebuild
- Updated both TeX sources to:
  - Replace the appendix include to use the compact gallery PDF.
  - Add a short “next steps” section describing how to scan $(q,p)$ / $(q,\beta)$ and geometry, and how to reduce micro-oscillation false peaks.
  - Add the new script to the reproducibility command list.
- Rebuilt:
  - `cd reports/ring_lazy_flux && latexmk -xelatex -interaction=nonstopmode -halt-on-error -auxdir=build -emulate-aux-dir ring_lazy_flux_cn.tex`
  - `cd reports/ring_lazy_flux && latexmk -xelatex -interaction=nonstopmode -halt-on-error -auxdir=build -emulate-aux-dir ring_lazy_flux_en.tex`

### Small fix
- Fixed LaTeX escapes in the EN “next steps” math (use `\beta`, `\in`, `\max` instead of `\\...`) and rebuilt the EN PDF.

## 2025-12-15 — Make reports public-facing (remove 2nd-person phrasing)

### User request
- Remove personal/2nd-person wording (e.g. “you want / you asked / 你要的 / 如果你...”) from the CN/EN public reports.

### Changes
- CN report (`reports/ring_lazy_flux/ring_lazy_flux_cn.tex`):
  - Replaced “你要的/如果你/你反复提到的/如果你想...” with neutral academic phrasing (“本文采用/若采用/为...”，etc.).
- EN report (`reports/ring_lazy_flux/ring_lazy_flux_en.tex`):
  - Replaced “you asked for / you want” with neutral phrasing.
- Rebuilt both PDFs:
  - `cd reports/ring_lazy_flux && latexmk -xelatex -interaction=nonstopmode -halt-on-error -auxdir=build -emulate-aux-dir ring_lazy_flux_cn.tex`
  - `cd reports/ring_lazy_flux && latexmk -xelatex -interaction=nonstopmode -halt-on-error -auxdir=build -emulate-aux-dir ring_lazy_flux_en.tex`

## 2025-12-15 — Front-load conclusions (after setup)

### User request
- Make the public report “conclusion-first”: place a concise conclusions section right after the setup (model + methods + criteria), before detailed examples and scans.

### Changes
- CN: inserted `\section{主要结论（先行）}` immediately after the criteria section, and added figure labels for the N=10 and N=11 examples for clean cross-references.
- EN: inserted `\section{Key findings (front-loaded)}` immediately after the criteria section, added a label to the minimal-example section, and added figure labels for the N=10 and N=11 examples.

### Rebuild
- `cd reports/ring_lazy_flux && latexmk -xelatex -interaction=nonstopmode -halt-on-error -auxdir=build -emulate-aux-dir ring_lazy_flux_cn.tex`
- `cd reports/ring_lazy_flux && latexmk -xelatex -interaction=nonstopmode -halt-on-error -auxdir=build -emulate-aux-dir ring_lazy_flux_en.tex`

## 2025-12-15 — De-emphasize supplementary AW galleries (move to appendix)

### User request
- Move the “more AW curves” multi-panel section to the back since it is not a core focus.

### Changes
- CN report: moved `\section{更多 AW 曲线（多图）}` into the appendix as `\section{补充图：对径终点 AW 曲线（多图）}`.
- EN report: moved `\section{More AW curves (multi-figure panels)}` into the appendix as `\section{Supplementary: antipodal AW curves (multi-figure panels)}`.

### Rebuild
- `cd reports/ring_lazy_flux && latexmk -xelatex -interaction=nonstopmode -halt-on-error -auxdir=build -emulate-aux-dir ring_lazy_flux_cn.tex`
- `cd reports/ring_lazy_flux && latexmk -xelatex -interaction=nonstopmode -halt-on-error -auxdir=build -emulate-aux-dir ring_lazy_flux_en.tex`

## 2025-12-15 — Tweak conclusions heading

### User request
- Remove the extra “先行” wording from the CN conclusions section title.

### Change
- CN: renamed `\section{主要结论（先行）}` to `\section{主要结论}`.
- EN: renamed `\section{Key findings (front-loaded)}` to `\section{Key findings}` for consistency.

### Rebuild
- `cd reports/ring_lazy_flux && latexmk -xelatex -interaction=nonstopmode -halt-on-error -auxdir=build -emulate-aux-dir ring_lazy_flux_cn.tex`
- `cd reports/ring_lazy_flux && latexmk -xelatex -interaction=nonstopmode -halt-on-error -auxdir=build -emulate-aux-dir ring_lazy_flux_en.tex`
