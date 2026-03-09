# Core Checklist

## Session Start
- Confirm repo root: `pwd` should end with `valley-k-small`.
- Scan active report IDs: `python3 scripts/reportctl.py list`.
- Read `AGENTS.md` and the target report `README.md` before edits.

## Report Task Loop
1. Resolve target report: `python3 scripts/reportctl.py resolve --report <id>`.
2. Run report script via wrapper or direct command:
   - `python3 scripts/reportctl.py run --report <id> -- python3 code/<entry>.py ...`
3. Verify regenerated assets under that report folder (`figures/`, `data/`, `tables/`, `outputs/`).
4. Build TeX in report folder:
   - CN: `latexmk -xelatex -interaction=nonstopmode -halt-on-error -auxdir=build -emulate-aux-dir <report>_cn.tex`
   - EN: `latexmk -pdf -interaction=nonstopmode -halt-on-error -auxdir=build -emulate-aux-dir <report>_en.tex`

## Repository Health Checks
- Registry + archives:
  - `python3 scripts/validate_registry.py`
  - `python3 scripts/validate_archives.py`
- Docs path hygiene:
  - `python3 scripts/check_docs_paths.py`
- Optional fast audit:
  - `python3 scripts/reportctl.py audit --fast`

## Mandatory End-of-Run Updates
- Refresh research summary date/index:
  - `python3 scripts/update_research_summary.py`
- Update `docs/RESEARCH_SUMMARY.md` narrative sections affected by your edits.
- If report/doc inventory changed, update:
  - `reports/README.md`
  - `docs/README.md`

## Optional Cleanup
- Local artifact cleanup:
  - `python3 scripts/cleanup_local.py`
- Include venv cleanup only if intended:
  - `python3 scripts/cleanup_local.py --include-venv`
