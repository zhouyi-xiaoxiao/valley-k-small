# Repository Guidelines

## Recent Update
- `reports/ring_lazy_jump_ext/` front-loads a condensed conclusion section, integrates key figures up front, and refreshes exact f(t) plots with clearer peak/valley emphasis and a tighter time window.
- `reports/ring_lazy_jump_ext/` uses `sections/` for extension sections, `outputs/` for generated artifacts, `ring_lazy_jump_ext_{cn,en}.tex` for the bilingual sources, and `build/` for LaTeX aux files. See `reports/ring_lazy_jump_ext/notes/readme_ext.md` for commands.

## Project Structure & Module Organization
- `reports/<report_name>/`: each report is self-contained.
  - `*.tex` / `*.pdf`: report source + compiled PDF.
  - `code/`: code used to generate figures/data/tables for that report.
  - `figures/`, `data/`, `tables/`, `inputs/`: report assets (as needed).
  - `build/`: LaTeX auxiliary build outputs (should stay out of version control).
- `docs/`: misc notes and submission PDFs (not tied to a single report).

## Research Summary Upkeep (must do)
- Maintain `docs/RESEARCH_SUMMARY.md` as the single ChatGPT-ready research brief.
- On every Codex run in this repo, refresh the "最后更新" date and update any sections affected by your changes.
- Use `python3 scripts/update_research_summary.py` to refresh the date and the auto index block.
- When adding/removing reports or docs, update `reports/README.md` and `docs/README.md` accordingly.

## Local Cleanup
- Use `python3 scripts/cleanup_local.py` to remove local artifacts (`.DS_Store`, `__pycache__`, `build/`, `*.pyc`).
- Use `python3 scripts/cleanup_local.py --include-venv` only when you intend to remove local virtualenvs.

## Build, Test, and Development Commands
- Install Python deps (recommended in a venv): `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`.
- Run a report pipeline (example: `valley`): `cd reports/ring_valley && python3 code/valley_study.py`.
- Build a report PDF (run inside the report folder): `latexmk -pdf -interaction=nonstopmode -halt-on-error -auxdir=build -emulate-aux-dir <report>.tex`.

## Coding Style & Naming Conventions
- Python: 4-space indentation; prefer type hints; `snake_case` for functions/variables; `CamelCase` for dataclasses/classes.
- Keep outputs deterministic when possible (fixed seeds are preferred for plots).
- Don’t commit environments (`.venv/`, `venv/`) or LaTeX aux files (`build/`, `*.aux`, `*.log`, `*.fls`, `*.fdb_latexmk`).

## Testing Guidelines
- No dedicated test framework is set up yet. Use lightweight sanity checks:
  - `python3 -m py_compile reports/**/code/*.py` (or compile individual scripts you changed).
  - Run a small/fast case and confirm expected files appear under that report’s `figures/` and `data/`.
  - Ensure `latexmk` builds complete without errors (inside the report folder).

## Commit & Pull Request Guidelines
- This repo currently has no established git history/commit conventions. Use short, imperative commit messages or Conventional Commits (recommended), e.g. `docs: clarify notation`, `fix: correct Chebyshev reduction`, `feat: add scan flag`.
- PRs should include: a short description, commands run, and (when outputs change) updated PDFs or clear regeneration steps.
