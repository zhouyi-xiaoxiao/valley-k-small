---
name: valley-k-small-continuation
description: Operational playbook for the valley-k-small repository (ring/grid2d first-passage reports). Use when continuing report work, regenerating figures/data/PDFs, updating docs indexes, running reportctl/web/deliverable pipelines, or preparing reproducible handoffs.
---

# Valley-k-small Continuation

## Quick Start
1. Confirm work is in the repo root.
2. Read `AGENTS.md` plus the target report README before changing code or text.
3. Run `python3 scripts/reportctl.py list` and `python3 scripts/reportctl.py resolve --report <id>` for report-scoped tasks.
4. Load one focused reference from `references/` (checklist, report map, or model conventions).

## Non-Negotiables
- Run `python3 scripts/update_research_summary.py` on every Codex run in this repo after edits.
- Update `research/docs/RESEARCH_SUMMARY.md` sections affected by your changes (not just the date/index block).
- When report/doc inventory changes, update `research/reports/README.md` and `research/docs/README.md`.
- Keep local artifacts out of commits (`build/`, `.DS_Store`, `__pycache__`, `.venv`, `*.pyc`, LaTeX aux files).
- Prefer report entry wrappers in `research/reports/<report>/code/`; shared logic lives in `packages/vkcore/src/vkcore/...`.

## Workflow Router
### Report logic, figures, or tables changed
1. Run the report pipeline script(s).
2. Confirm expected files appear under that report's `artifacts/figures/`, `artifacts/data/`, `artifacts/tables/`, `artifacts/outputs/`.
3. Build impacted CN/EN TeX sources.
4. Run scoped checks (`py_compile`, docs path check, optional fast audit).
5. Refresh `research/docs/RESEARCH_SUMMARY.md`.

### Cross-repo maintenance changed
1. Run `python3 scripts/validate_registry.py`.
2. Run `python3 scripts/validate_archives.py`.
3. Run `python3 scripts/check_docs_paths.py`.
4. Optionally run `python3 scripts/reportctl.py audit --fast` or `python3 scripts/reportctl.py doctor`.

### Web, deliverables, or agent handoff pipeline changed
- Use `reportctl` wrappers: `web-data`, `agent-sync`, `web-build`, `web-preview`, `deliverables`, `publication-pdf`, `agent-pack`.
- Validate outputs with `python3 scripts/validate_web_data.py`.

### Keepalive automation requested
When the user asks for recurring autonomous Codex execution, use:
- `./scripts/ka start <name> [task text...]` for quick start with auto profile detection.
- `./scripts/ka start-as <optimize|review|build|monitor> <name> [task text...]` for explicit profile.
- `./scripts/ka status <name>` / `./scripts/ka logs <name> [tail]` / `./scripts/ka stop <name>`.
- Default keepalive Codex runtime: `gpt-5.3-codex` with `xhigh` reasoning effort (unless user explicitly overrides).

Natural-language trigger mapping:
- "启动自动优化/持续跑": `ka start`.
- "自动审查/定时review": `ka start-as review`.
- "自动构建/持续构建": `ka start-as build`.
- "巡检/监控": `ka start-as monitor`.

### Isambard routing for optimize automation
- For optimize loops, use `isambard-automation` when workload is heavy:
  - large parameter sweeps,
  - batch jobs that can run in parallel,
  - expected local runtime >20 minutes per round.
- For short checks/smoke runs (<10 minutes), keep execution local.
- Remote flow baseline: `isbard doctor` -> `isbard auth` (if needed) -> `isbard submit/status/fetch`.
- If remote execution fails, record the reason and run a minimal local smoke check before retrying remote.
- In every remote round summary, report `JOB_ID`, `REMOTE_DIR`, fetched artifact paths, and next step.

## Build Conventions
- CN reports usually build with `latexmk -xelatex ... *_cn.tex`.
- EN reports usually build with `latexmk -pdf ... *_en.tex`.
- Use `-auxdir=build -emulate-aux-dir` in report folders to avoid top-level aux noise.

## Handoff Standard
Always include:
- Files changed.
- Exact commands run.
- What was regenerated.
- Which checks passed or were skipped.
- Any assumptions or unresolved risks.

## References
- `references/core-checklist.md`: task checklists and maintenance gates.
- `references/report-map.md`: report IDs, entry scripts, and build commands.
- `references/research-conventions.md`: model-rule conventions and interpretation guardrails.
