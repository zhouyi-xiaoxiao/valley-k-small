# Implementation Roadmap

This roadmap scopes the remaining first-passage and first-encounter research
work. It is a planning document only; it does not authorize large scans or
unrelated report edits.

## Prompt Policy
- Use normal prompts for bounded document edits, figure readability revisions,
  small validation tests, one-file fixes, and inspection tasks.
- Use `/goal` for long-running research programs that need repeated iteration:
  multi-report figure revision, new two-target model implementation, reflecting
  encounter validation, diagonal encounter decomposition, or full report
  integration.
- Do not run large scans unless a prompt or `/goal` explicitly requests the
  scan scope, parameters, and expected outputs.

## Dependencies
- Setup precedes all implementation work.
- Current report revision can proceed before new models, but must not change
  classifier semantics.
- 1D two-target work should precede 2D two-target work because it fixes notation,
  target-channel bookkeeping, and decomposition tests.
- Encounter mean validation should precede diagonal encounter decomposition
  because the mean and mass-balance checks establish the transition kernel.
- Scans depend on validated kernels, classifiers, and decomposition tests.
- Final report integration depends on accepted figures, tables, tests, and notes
  from the relevant modules.

## Setup
Prompt type: normal prompt.

Tasks:
- Inspect `AGENTS.md`, `CLAUDE.md`, `research/reports/README.md`,
  `research/reports/report_registry.yaml`, and the target report `README.md`.
- Confirm the public CLI surface with `python3 scripts/reportctl.py --help`.
- Run only lightweight checks needed for the task.
- Identify the target report before editing.

Acceptance criteria:
- The target report is resolved with `reportctl.py resolve`.
- The expected output directories are identified.
- No scientific code or generated outputs are changed during setup-only work.

## Current Report Revision
Prompt type: normal prompts for one report or figure; `/goal` for revising a
whole report family.

Tasks:
- Improve readability of current figures: axes, legends, parameter payloads,
  target labels, boundary mode labels, and classifier annotations.
- Keep figures inside the owning report's `artifacts/figures/`.
- Update captions so they distinguish `double_peak`, `second_peak`,
  `local_bump`, and `shoulder` accurately.
- Keep the distinction between mean first-passage time and the full distribution
  explicit in text and captions.

Dependencies:
- Setup.
- Existing classifier outputs or newly generated small diagnostic artifacts.

Acceptance criteria:
- Revised figures are readable in the compiled PDF.
- Captions do not overclaim double peaks.
- Changed artifacts and commands are recorded in report notes or final handoff.
- Focused build or validation passes for the edited report.

## 1D Two-Target First Passage
Prompt type: `/goal` for implementation; normal prompts for derivation review or
small tests.

Tasks:
- Define the 1D two-target transition kernel and absorbing target convention.
- Compute `f_target1(t)`, `f_target2(t)`, and `f_total(t)`.
- Add or run checks for nonnegative probabilities, row-stochastic transition
  matrices, absorbing stop, and mass balance.
- Produce target-channel decomposition figures and tables.

Dependencies:
- Setup.
- Existing ring report conventions.

Acceptance criteria:
- `f_total(t)=f_target1(t)+f_target2(t)` holds within documented tolerance.
- Absorption stops immediately at either target.
- The report records model parameters, classifier criteria, and validation
  tolerances.

## 2D Two-Target First Passage
Prompt type: `/goal` for implementation; normal prompts for focused plotting,
validation, or text revision.

Tasks:
- Extend target-channel decomposition to 2D geometries.
- State boundary conditions explicitly: periodic, reflecting, absorbing, mixed,
  lazy, or non-lazy.
- Validate transition kernels before interpreting distribution shape.
- Compare near-target and far-target channels without using the mean as a
  substitute for the full distribution.

Dependencies:
- Setup.
- Accepted 1D two-target bookkeeping.
- Existing 2D report conventions.

Acceptance criteria:
- `f_total(t)=f_target1(t)+f_target2(t)` holds within documented tolerance.
- Transition probabilities are nonnegative and row-stochastic.
- Figures show target locations, boundary mode, and channel labels.
- Double-peak claims are backed by classifier output.

## Encounter Mean Validation
Prompt type: `/goal` for reflecting-boundary validation; normal prompts for small
derivations, tests, or figure edits.

Tasks:
- Implement or review reflecting-boundary two-walker encounter validation.
- Treat reflecting boundary as attempted-outside-stays unless stated otherwise.
- Verify the encounter-time distribution, mean encounter time, and mass balance.
- Avoid saying the 2D encounter walker always has eight directions unless
  synchronous lazy update is explicitly used.

Dependencies:
- Setup.
- Validated boundary-condition convention.

Acceptance criteria:
- Encounter probabilities are nonnegative and mass is conserved or absorbed as
  documented.
- Mean encounter time is computed from the full distribution, not substituted
  for it.
- Boundary behavior is covered by tests or a documented small example.

## Encounter Diagonal Decomposition
Prompt type: `/goal` for implementation; normal prompts for focused validation
or plotting.

Tasks:
- Decompose encounter distributions by diagonal encounter position `k`.
- Compute and store per-position components `f_k(t)`.
- Validate `f_E(t)=sum_k f_k(t)`.
- Produce readable figures showing total and position-decomposed encounter
  distributions.

Dependencies:
- Encounter mean validation.
- Validated transition kernel and absorbing encounter convention.

Acceptance criteria:
- `f_E(t)=sum_k f_k(t)` holds within documented tolerance.
- Per-position labels and diagonal geometry are unambiguous.
- Figures distinguish total, dominant positions, and residual components
  without clutter.

## Scans
Prompt type: `/goal` for any broad parameter scan; normal prompt only for a
single small diagnostic or smoke run.

Tasks:
- Define scan parameters, ranges, tolerances, and output names before running.
- Use the quantitative peak classifier for any `double_peak` labels.
- Record configs, summary CSV/JSON, selected curves, and validation failures.
- Avoid changing unrelated reports while scanning one report family.

Dependencies:
- Validated model kernels.
- Accepted classifier criteria.
- Relevant decomposition checks.

Acceptance criteria:
- Scan config is saved with outputs.
- Every `double_peak` label is classifier-backed.
- Weaker cases are labeled `shoulder`, `local_bump`, or `second_peak`.
- Failed or borderline cases are recorded, not silently promoted.

## Final Report Integration
Prompt type: `/goal` for full integration; normal prompts for a single report
section, caption, or build fix.

Tasks:
- Integrate validated methods, figures, tables, and conclusions into CN/EN
  manuscripts.
- Keep generated outputs in the owning report directories.
- Update report notes with commands, generated outputs, validation errors, and
  remaining risks.
- Refresh repository summaries only when report inventory or brief content
  changes.

Dependencies:
- Accepted current report revisions.
- Accepted 1D/2D two-target modules.
- Accepted encounter validation and diagonal decomposition.
- Completed scans, if explicitly requested.

Acceptance criteria:
- Manuscripts build for the requested language(s).
- Claims match classifier and decomposition evidence.
- The final handoff lists changed files, commands run, generated outputs,
  validation errors, and remaining risks.
