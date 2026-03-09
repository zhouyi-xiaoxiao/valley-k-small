# Core Checklist

## Session Start
- Confirm repo root: `pwd` should end with `valley-k-small`
- Scan active report IDs: `python3 scripts/reportctl.py list`
- Read `AGENTS.md` and the target report `README.md`

## Report Task Loop
1. Resolve the target report:
   - `python3 scripts/reportctl.py resolve --report <id>`
2. Run the report pipeline:
   - `python3 scripts/reportctl.py run --report <id> -- python3 code/<entry>.py ...`
3. Verify regenerated assets under that report's `artifacts/`
4. Build TeX in the report manuscript folder

## Repository Health Checks
- `python3 scripts/reportctl.py validate-registry`
- `python3 scripts/reportctl.py validate-archives`
- `python3 scripts/reportctl.py check-docs-paths`
- Optional:
  - `python3 scripts/reportctl.py audit --fast`
  - `python3 scripts/reportctl.py doctor`

## Mandatory End-of-Run Updates
- `python3 scripts/reportctl.py summary`
- Update `research/docs/RESEARCH_SUMMARY.md` narrative sections affected by your edits
- If report/doc inventory changed, update:
  - `research/reports/README.md`
  - `research/docs/README.md`

## Optional Cleanup
- `python3 scripts/reportctl.py cleanup`
- `python3 scripts/reportctl.py cleanup --include-venv`
- `python3 scripts/reportctl.py cleanup --include-runtime`
