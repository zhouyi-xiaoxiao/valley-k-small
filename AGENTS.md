# Repository Guidelines

## Repo Contract
- The repository is agent-first: agents are the primary operators and maintainers.
- Human involvement is mainly natural-language direction, debugging help, and directional feedback on PDF outputs.
- Canonical research content lives under `research/`.
- Canonical platform and automation code lives under `platform/`.
- Shared Python code lives under `packages/vkcore/src/vkcore/`.
- Public script surface is only:
  - `python3 scripts/reportctl.py`
  - `./scripts/ka`

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
