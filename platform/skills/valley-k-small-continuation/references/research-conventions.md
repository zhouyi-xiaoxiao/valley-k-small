# Research Conventions

## Model-rule disambiguation (always state explicitly)
- Random walk type: `lazy` (`q < 1`) or `non-lazy` (`q = 1`).
- Shortcut rule: `selfloop`, `renormalize`, or `equal4`.
- Target mode: single-target or two-target.
- Boundary mode (2D): periodic / reflecting / mixed.

## Parameter payload for reproducible discussion
When asking analysis or reporting results, include:
- `(N, K, q, beta, src, dst, target, rho)`
- Bimodality criteria: `h_min`, `second_frac`, `t2/t1`, valley threshold if used.

## Interpretation guardrails
- Do not compare results across rule families without restating the rule switch.
- For `cross_luca_regime_map`, keep the fairness metric as ratio `R = sparse/luca` under fixed full-FPT horizon; do not mix raw seconds across families.
- For `ring_lazy_jump_ext` and `ring_lazy_jump_ext_rev2`, the selected representative beta is `0.01` (see `outputs/selected_beta.txt`).
- For `grid2d_two_target_double_peak`, the reported clear-double phase uses explicit thresholds (`sep`, peak floor, valley ratio); keep threshold sets consistent when comparing runs.

## Output and build conventions
- Report outputs stay inside each report folder.
- TeX aux outputs go to `build/`.
- Prefer vector figure outputs (`.pdf`) for report inclusion.
- Use report `README.md` / `notes/*.md` as the source of truth for command order.

## Canonical project context files
- Global research brief: `docs/RESEARCH_SUMMARY.md`
- Report index: `reports/README.md`
- Docs index: `docs/README.md`
- Script command index: `scripts/README.md`
