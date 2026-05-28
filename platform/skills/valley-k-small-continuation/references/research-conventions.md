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

## Scientific integrity guardrails
### Peak taxonomy
- `double_peak` is reserved for curves whose quantitative peak classifier
  returns the label `double_peak`; record the classifier name, thresholds, and
  output table or JSON near the generated figure/table.
- Use `shoulder` or `local_bump` when a second structure is visible but fails
  the configured double-peak thresholds.
- The phrase "double-peak-like" is allowed only for qualitative motivation or
  hypotheses, not as a result label.

### Full distribution vs mean
- Mean first-passage time is a scalar summary. It is not evidence for the
  presence, absence, or mechanism of a full first-passage distribution feature.
- When explaining shoulders, local bumps, second peaks, or double peaks, cite
  the distribution `f(t)` and the relevant decomposition, not only the mean.

### Mass-balance and transition checks
- Transition probabilities must be nonnegative.
- Discrete-time transition matrices must be row-stochastic unless the report
  explicitly documents a different convention.
- Absorbing states stop the process immediately.
- Two-target decompositions must check `f_total(t) = f_target1(t) + f_target2(t)`.
- Encounter-position decompositions must check `f_E(t) = sum_k f_k(t)`.
- Reflecting boundaries mean attempted-outside-stays unless the report states a
  different boundary rule in its model setup.

### Scope discipline
- Do not run large scans unless the user/task explicitly asks for them.
- Do not modify unrelated reports while working on a report-scoped task.
- End-of-run handoffs must list changed files, commands run, generated outputs,
  validation errors, and remaining risks.

## Output and build conventions
- Report outputs stay inside each report folder.
- TeX aux outputs go to `build/`.
- Prefer vector figure outputs (`.pdf`) for report inclusion.
- Use report `README.md` / `notes/*.md` as the source of truth for command order.

## Canonical project context files
- Global research brief: `research/docs/RESEARCH_SUMMARY.md`
- Report index: `research/reports/README.md`
- Docs index: `research/docs/README.md`
- Script command index: `scripts/README.md`
