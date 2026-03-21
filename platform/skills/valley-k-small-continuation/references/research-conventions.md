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
- For `luca_vs_recursion_unified_benchmark`, keep the active fairness discussion tied to native-task runtime ratios in `research/reports/luca_vs_recursion_unified_benchmark/artifacts/data/runtime_summary.json`; the historical fixed full-FPT note is retained only inside Appendix F of that report.
- For `ring_lazy_jump_ext` and `ring_lazy_jump_ext_rev2`, the selected representative beta is `0.01` (see `research/reports/ring_lazy_jump_ext_rev2/artifacts/outputs/selected_beta.txt`).
- For `grid2d_two_target_double_peak`, the reported clear-double phase uses explicit thresholds (`sep`, peak floor, valley ratio); keep threshold sets consistent when comparing runs.

## Output and build conventions
- Report outputs stay inside each report folder.
- TeX aux outputs go to `build/`.
- Prefer vector figure outputs (`.pdf`) for report inclusion.
- Use report `README.md` / `notes/*.md` as the source of truth for command order, but prefer `python3 scripts/reportctl.py run/build ...` in public-facing instructions.

## Canonical project context files
- Global research brief: `research/docs/RESEARCH_SUMMARY.md`
- Report index: `research/reports/README.md`
- Docs index: `research/docs/README.md`
- Script command index: `scripts/README.md`
