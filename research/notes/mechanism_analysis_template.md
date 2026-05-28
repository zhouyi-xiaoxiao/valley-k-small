# Mechanism Analysis Template

This note records the completed
`research/reports/grid2d_one_target_valley_peak_budget/` analysis as the
canonical template for future mechanism analyses. That report compares the
`peak1`, `valley`, and `peak2` windows in a one-target 2D first-passage problem
using event-time ratios, absolute budgets, and spatial decomposition. The
template below should guide later two-target and encounter reports without
changing their model-specific definitions.

## Source Example

The canonical one-target example is:

- Report: `research/reports/grid2d_one_target_valley_peak_budget/`
- Manuscripts:
  - `manuscript/grid2d_one_target_valley_peak_budget_en.tex`
  - `manuscript/grid2d_one_target_valley_peak_budget_cn.tex`
- Figures:
  - `artifacts/figures/fig1_geometry_curve_budget.pdf`
  - `artifacts/figures/fig2_tau_out_budget.pdf`
  - `artifacts/figures/fig3_tau_mem_budget.pdf`
- Figure-generation script:
  - `code/build_budget_bar_figures.py`

The completed analysis defines membrane permeability `kappa`, target-hit time
`T`, first corridor-exit time `tau_out`, first true membrane-crossing time
`tau_mem`, relative timing ratio, outside-time share, outside budget, and
post-crossing budget. Its mechanism claim is not based on visual peak shape
alone: it compares normalized timing, absolute budgets, and spatial residence
across `peak1`, `valley`, and `peak2`.

## Canonical Pattern

Use this sequence for future mechanism analyses:

1. Define event times.
   State the random time variables before interpreting any curve. In the
   one-target template, these are `T`, `tau_out`, and `tau_mem`. In later
   reports, the analogous variables might be target-channel hit times,
   first-entry times into a region, first-crossing times, or encounter times.

2. Define peak/valley windows.
   Identify the windows around `peak1`, `valley`, `peak2`, or any candidate
   bump using the report's quantitative classifier or an explicitly documented
   window rule. Late-time peaks or bumps should not be interpreted by visual
   inspection alone.

3. Compute normalized ratios.
   Normalize event timing or residence shares by the relevant hit or encounter
   time. The one-target report uses ratios such as
   `E[tau | tau < T, T in W] / E[T | T in W]` and percentages such as
   outside-time share. These ratios explain relative timing, but they are not
   sufficient by themselves to establish mechanism.

4. Compute absolute budgets.
   Convert the same behavior into expected step counts or mass contributions.
   The one-target example uses outside budget and post-crossing budget. This is
   the decisive second axis: a mechanism claim must be supported by a budget,
   channel, or contribution decomposition, not just by a visible curve feature.

5. Decompose by spatial region or channel.
   Split the relevant mass, time, or contribution into interpretable components.
   The one-target analysis decomposes outside residence into the left-side
   pocket, corridor, and merged outer/right-side bulk. For two-target problems,
   use target-channel decomposition. For encounter problems, use
   diagonal-position decomposition.

6. Interpret as phenomenon + evidence + mechanism + conclusion.
   Each result paragraph should follow this structure:
   - Phenomenon: what curve feature or window contrast is being explained.
   - Evidence: which ratios, budgets, or decompositions changed.
   - Mechanism: which region, channel, or contribution carries the change.
   - Conclusion: what can and cannot be claimed from the evidence.

## One-Target Lesson

The one-target budget report shows why this pattern matters. The late-time
structure is not explained by saying "there is a second peak" or by comparing
mean first-passage times alone. The useful mechanism is:

- The `peak2` window has more pre-hit outside residence than the `valley`
  window.
- The absolute outside budget separates `valley` from `peak2` more clearly than
  normalized exit timing alone.
- The spatial decomposition identifies the left-side pocket as an important
  carrier of the delayed residence.
- Membrane permeability mainly enlarges the post-crossing budget rather than
  making crossing probability alone a sufficient explanation.

This is the standard for later reports: a late-time peak, shoulder, or local
bump should be tied to a quantitative contribution, not to visual appearance.

## Guidance for Two-Target Analyses

For 1D or 2D two-target first-passage work, use the same pattern with target
channels:

- Define `T`, the first hit time of either target, and target-channel events
  such as `hit target 1 first` and `hit target 2 first`.
- Define the peak/valley windows on the total distribution `f_total(t)` using
  the classifier or documented window rule.
- Compute normalized timing or residence ratios within each window.
- Compute absolute budgets or probability mass contributions for each target
  channel.
- Enforce and report the decomposition
  `f_total(t) = f_target1(t) + f_target2(t)`.
- Interpret any shoulder, local bump, second peak, or `double_peak` claim by
  asking which target channel carries the relevant mass and which mechanism
  separates the windows.

Do not call a curve `double_peak` unless the quantitative classifier criteria
are met. If the classifier does not label it `double_peak`, use `shoulder`,
`local_bump`, or `second_peak` as appropriate.

## Guidance for Encounter Analyses

For two-walker encounter work, use the same pattern with encounter-position
channels:

- Define the encounter time `T_E` and the diagonal encounter position `k`.
- Define windows on the encounter distribution `f_E(t)` using the classifier or
  a documented window rule.
- Compute normalized timing or residence ratios for relevant pre-encounter
  events.
- Compute absolute budgets or mass contributions by diagonal position.
- Enforce and report the decomposition `f_E(t) = sum_k f_k(t)`.
- Interpret any late-time structure by identifying which diagonal positions or
  spatial channels carry the delayed mass.

Encounter mechanisms should not be stated only as changes in mean encounter
time. The mean can summarize the distribution, but the mechanism must come from
the full distribution and its diagonal-position decomposition.

## Reporting Checklist

For each future mechanism section, include:

- Model and boundary convention.
- Event-time definitions.
- Peak/valley window rule or classifier criteria.
- Normalized ratios.
- Absolute budgets.
- Spatial, target-channel, or diagonal-position decomposition.
- Mass-balance check.
- A phenomenon + evidence + mechanism + conclusion paragraph.
- Explicit labels for weaker structures: `shoulder`, `local_bump`, or
  `second_peak` unless `double_peak` is classifier-backed.

