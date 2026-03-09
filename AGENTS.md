# Repository Guidelines

## Current Layout
- `research/reports/<report_id>/` is the canonical home for each report.
  - `code/`: report entry scripts
  - `notes/`: report notes and reproduction guidance
  - `manuscript/`: TeX/PDF sources, extras, aux build dir
  - `artifacts/`: figures, tables, data, outputs
- `research/docs/`: research brief, research logs, submission material.
- `research/archives/`: archived timestamp runs and legacy artifacts.
- `platform/web/`: Next.js site and generated public payloads.
- `platform/tools/`: real script implementations split into `repo/`, `web/`, and `automation/`.
- `platform/schemas/`: JSON schemas.
- `platform/skills/`: Codex skill material.
- `packages/vkcore/src/vkcore/`: shared Python core library.
- `scripts/`: thin compatibility wrappers and shell entrypoints.

## Research Summary Upkeep
- Maintain `research/docs/RESEARCH_SUMMARY.md` as the single ChatGPT-ready research brief.
- On every Codex run in this repo, refresh the "最后更新" date and update any sections affected by your changes.
- Use `python3 scripts/update_research_summary.py` to refresh the date and the auto index block.
- When adding/removing reports or docs, update `research/reports/README.md` and `research/docs/README.md`.

## Cleanup
- Use `python3 scripts/cleanup_local.py` to remove local artifacts (`.DS_Store`, `__pycache__`, `build/`, `*.pyc`).
- Use `python3 scripts/cleanup_local.py --include-venv` only when you intend to remove local virtualenvs.
- Use `python3 scripts/cleanup_local.py --include-runtime` to clean runtime noise under `platform/runtime/` and related local caches.

## Keepalive
- Prefer `./scripts/ka` for recurring autonomous Codex execution.
- Natural-language intent mapping:
  - "启动自动优化/持续跑": `./scripts/ka start <job> [task text...]`
  - "自动审查/定时 review": `./scripts/ka start-as review <job> [task text...]`
  - "自动构建/持续构建": `./scripts/ka start-as build <job> [task text...]`
  - "巡检/监控": `./scripts/ka start-as monitor <job> [task text...]`
- Default keepalive Codex runtime: `gpt-5.3-codex` with `xhigh` reasoning effort unless the user overrides it.

## Build and Test
- Install Python deps: `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`
- List or resolve reports: `python3 scripts/reportctl.py list`
- Build a report: `python3 scripts/reportctl.py build --report <id> --lang <cn|en>`
- Fast repo audit: `python3 scripts/reportctl.py audit --fast`
- Health check: `python3 scripts/reportctl.py doctor`

## Conventions
- Python: 4-space indentation, type hints preferred, `snake_case` for functions/variables, `CamelCase` for classes/dataclasses.
- Keep outputs deterministic when practical.
- Do not commit local environments, LaTeX aux files, `.next/`, `out/`, `node_modules/`, or runtime logs.

## Compatibility
- Root-level `reports/`, `docs/`, `archives/`, `site/`, `schemas/`, `skills/`, `src/`, and `artifacts/` may exist as symlinks for backward compatibility.
- New edits should target `research/`, `platform/`, and `packages/` paths directly.
