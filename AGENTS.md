# Repository Guidelines

## Quickstart

1. Read `CLAUDE.md` (router) and this file (contract).
2. Run `python3 scripts/reportctl.py --help` to see the CLI surface.
3. Read `platform/skills/valley-k-small-continuation/SKILL.md` for the operational playbook.
4. Health check: `python3 scripts/reportctl.py doctor`.
5. Then start work — refresh `research/docs/RESEARCH_SUMMARY.md` (`reportctl.py summary`) after any inventory change.

## Project Purpose
`valley-k-small` studies first-passage and first-encounter time distributions
in structured lattice random walks. The remaining research work is to revise
current reports and readable figures, extend one- and two-dimensional
two-target first-passage models, validate reflecting-boundary two-walker
encounters, and decompose encounter distributions by diagonal encounter
position.

## Repo Contract
- The repository is agent-first: agents are the primary operators and maintainers.
- Human involvement is mainly natural-language direction, debugging help, and directional feedback on PDF outputs.
- Canonical research content lives under `research/`.
- Canonical platform and automation code lives under `platform/`.
- Shared Python code lives under `packages/vkcore/src/vkcore/`.
- Public script surface is only:
  - `python3 scripts/reportctl.py`
  - `./scripts/ka`
- Do not modify scientific code when the task is documentation, planning,
  guardrails, or repository policy only.
- Do not run large scans unless the task explicitly asks for them.
- Do not modify unrelated reports.
- Prefer small, reproducible commands over broad regeneration.

## Mathematical Guardrails
The scientific goal is to explain shoulders, local bumps, second peaks, and
double-peak-like structures through exact computation, mass-balance checks,
target-channel decomposition, and encounter-position decomposition.

Hard rules:
- Do not call a curve `double_peak` unless the quantitative peak classifier
  labels it as `double_peak`.
- Use `shoulder` or `local_bump` for weaker structures.
- Do not overclaim double peaks from visual inspection alone; cite classifier
  criteria, thresholds, and output artifacts.
- Do not confuse mean first-passage time with the full first-passage
  distribution.
- All transition probabilities must be nonnegative.
- All discrete-time transition matrices must be row-stochastic unless
  explicitly documented otherwise.
- Absorbing states must stop the process immediately.
- Mass balance must hold in every exact recursion or simulation summary.
- Two-target distributions must satisfy `f_total(t) = f_target1(t) + f_target2(t)`.
- Encounter distributions must satisfy `f_E(t) = sum_k f_k(t)`.

## Boundary-Condition Conventions
- Reflecting boundary means attempted-outside-stays unless explicitly stated
  otherwise.
- State whether each model is periodic, reflecting, absorbing, mixed, lazy, or
  non-lazy before comparing results.
- Do not state that the 2D encounter walker always has eight directions unless
  synchronous lazy update is explicitly used.
- Absorbing targets take precedence over further motion: once hit, the process
  has stopped.

## Plotting Rules
- Figures must make the distribution feature readable at report scale: label
  axes, units, parameters, target locations, boundary mode, and classifier
  labels where relevant.
- When showing peaks, also show or report the peak-classifier thresholds and
  enough diagnostic context to distinguish `double_peak`, `second_peak`,
  `local_bump`, and `shoulder`.
- Prefer vector figures for manuscripts and keep generated assets under the
  owning report's `artifacts/figures/`.
- Do not use a plot title or caption to promote a qualitative bump to
  `double_peak` unless the classifier says `double_peak`.

## Testing Expectations
- For code changes, run the narrowest relevant tests first, then the applicable
  `reportctl` validation command.
- For report structure or documentation changes, run `python3 scripts/reportctl.py
  check-docs-paths` and `python3 scripts/reportctl.py validate-science-rules`.
- For transition-matrix work, add or run checks for nonnegative probabilities,
  row sums, absorbing-state stopping, and mass balance.
- For two-target and encounter work, include explicit decomposition tests:
  `f_total(t) = f_target1(t) + f_target2(t)` and `f_E(t) = sum_k f_k(t)`.

## Report Output Conventions
- Report outputs stay inside `research/reports/<report_id>/artifacts/`.
- Manuscripts and extras stay under `research/reports/<report_id>/manuscript/`.
- Notes, run commands, assumptions, and validation remarks stay under
  `research/reports/<report_id>/notes/`.
- End-of-run reports must include changed files, commands run, generated
  outputs, validation errors, and remaining risks.


## Report Layout
- Each report lives at `research/reports/<report_id>/`.
- Required top-level subdirectories:
  - `code/`
  - `notes/`
  - `manuscript/`
  - `artifacts/`
- Report roots should not keep loose `*.tex` or `*.pdf`.

## Mandatory Upkeep
- Keep `research/docs/RESEARCH_SUMMARY.md` current.
- After edits that affect the repo brief or report inventory, run:
  - `python3 scripts/reportctl.py summary`
- When adding or removing reports/docs, update:
  - `research/reports/README.md`
  - `research/docs/README.md`

## Validation
- Registry: `python3 scripts/reportctl.py validate-registry`
- Archives: `python3 scripts/reportctl.py validate-archives`
- Docs paths: `python3 scripts/reportctl.py check-docs-paths`
- Scientific guardrails: `python3 scripts/reportctl.py validate-science-rules`
- Full repo health: `python3 scripts/reportctl.py doctor`
- Fast audit: `python3 scripts/reportctl.py audit --fast`

## Cleanup
- Safe cleanup: `python3 scripts/reportctl.py cleanup`
- Include hidden runtime state: `python3 scripts/reportctl.py cleanup --include-runtime`
- Include virtualenvs only intentionally: `python3 scripts/reportctl.py cleanup --include-venv`

## Keepalive
- Prefer `./scripts/ka` for recurring Codex execution.
- Natural-language mapping:
  - “启动自动优化/持续跑” -> `./scripts/ka start <job> [task text...]`
  - “自动审查/定时 review” -> `./scripts/ka start-as review <job> [task text...]`
  - “自动构建/持续构建” -> `./scripts/ka start-as build <job> [task text...]`
  - “巡检/监控” -> `./scripts/ka start-as monitor <job> [task text...]`

## Conventions
- Python: 4-space indentation, type hints preferred, `snake_case` for functions/variables, `CamelCase` for classes/dataclasses.
- Keep generated outputs deterministic when practical.
- Do not commit `.venv/`, `venv/`, `build/`, `.next/`, `out/`, `node_modules/`, `__pycache__/`, `*.pyc`, or `.local/`.
