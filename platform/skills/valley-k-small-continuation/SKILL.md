---
name: valley-k-small-continuation
description: Operational playbook for continuing report work, repo maintenance, web payload generation, and agent handoff tasks in valley-k-small.
---

# Valley-k-small Continuation

## Quick Start
1. Confirm you are in the repo root.
2. Read `AGENTS.md` and the target report `README.md`.
3. Run `python3 scripts/reportctl.py list` and `python3 scripts/reportctl.py resolve --report <id>` for report-scoped tasks.
4. Load one focused reference from `references/`.

## Non-Negotiables
- Refresh the research brief after relevant edits:
  - `python3 scripts/reportctl.py summary`
- Update `research/docs/RESEARCH_SUMMARY.md` sections affected by your changes, not just the date/index.
- When report/doc inventory changes, update:
  - `research/reports/README.md`
  - `research/docs/README.md`
- Keep local artifacts out of commits:
  - `build/`, `.DS_Store`, `__pycache__`, `.venv`, `*.pyc`, `.local/`
- Prefer report entry wrappers under `research/reports/<report>/code/`; shared logic belongs in `packages/vkcore/src/vkcore/`.

## Workflow Router
### Report logic, figures, or tables changed
1. Run the report pipeline script(s).
2. Confirm outputs appear under that report's `artifacts/figures/`, `artifacts/data/`, `artifacts/tables/`, `artifacts/outputs/`.
3. Build impacted CN/EN TeX sources.
4. Run scoped checks.
5. Refresh the research summary.

### Cross-repo maintenance changed
1. `python3 scripts/reportctl.py validate-registry`
2. `python3 scripts/reportctl.py validate-archives`
3. `python3 scripts/reportctl.py check-docs-paths`
4. Optionally `python3 scripts/reportctl.py audit --fast` or `python3 scripts/reportctl.py doctor`

### Web, deliverables, or agent handoff pipeline changed
- Use `reportctl`:
  - `web-data`
  - `book-data`
  - `translation-qc`
  - `validate-web-data`
  - `agent-sync`
  - `web-build`
  - `deliverables`
  - `publication-pdf`
  - `agent-pack`

### Keepalive automation requested
- `./scripts/ka start <name> [task text...]`
- `./scripts/ka start-as <optimize|review|build|monitor> <name> [task text...]`
- `./scripts/ka status <name>`
- `./scripts/ka logs <name> [tail]`
- `./scripts/ka stop <name>`

## Build Conventions
- CN reports usually build with `latexmk -xelatex ... *_cn.tex`.
- EN reports usually build with `latexmk -pdf ... *_en.tex`.
- Use `-auxdir=build -emulate-aux-dir` inside report manuscript folders.

## Handoff Standard
Always include:
- files changed
- exact commands run
- what was regenerated
- which checks passed or were skipped
- assumptions or unresolved risks

## References
- `references/core-checklist.md`
- `references/report-map.md`
- `references/research-conventions.md`
