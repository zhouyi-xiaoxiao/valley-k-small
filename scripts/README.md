# Scripts

## reportctl.py
Unified repository CLI:
- `list`: list reports from `reports/report_registry.yaml`
- `resolve --report <id>`: resolve canonical report id/path
- `run --report <id> -- <cmd>`: run command in report directory
- `build --report <id> --lang <cn|en>`: build main TeX
- `audit [--fast|--full]`: run audit pipeline
- `archive [--dry-run|--report <id>|--verify]`: archive timestamp runs / verify archive metadata
- `doctor [--full|--skip-pytest]`: one-command health check (metadata + docs paths + py_compile + pytest + audit)
- `prune-legacy-artifacts [--dry-run|--report <id>]`: archive legacy-named top-level PDFs from active report folders

Usage:
```
python3 scripts/reportctl.py list
python3 scripts/reportctl.py resolve --report ring_valley_dst
python3 scripts/reportctl.py run --report ring_valley_dst -- python3 code/bimodality_flux_scan.py --help
python3 scripts/reportctl.py build --report ring_valley_dst --lang cn
python3 scripts/reportctl.py audit --fast
python3 scripts/reportctl.py doctor
python3 scripts/reportctl.py prune-legacy-artifacts --dry-run
```

## validate_registry.py
Validates `reports/report_registry.yaml` (YAML v2).

Usage:
```
python3 scripts/validate_registry.py
```

## validate_archives.py
Validates `archives/reports/index.jsonl` and all `reports/*/**/latest/manifest.json`.

Usage:
```
python3 scripts/validate_archives.py
```

## check_docs_paths.py
Checks active documentation for:
- broken repo-relative path references in backticks
- absolute `/Users/...` path tokens outside `docs/research_log/`

Usage:
```
python3 scripts/check_docs_paths.py
```

JSON output:
```
python3 scripts/check_docs_paths.py --json
```

## audit_reports.py
Runs repository-wide report audits in one command:
- Metadata precheck (`validate_registry.py` + `validate_archives.py`).
- TeX build audit (fast mode uses registry main tex; full mode uses `reports/*/*.tex`).
- Warning scan on TeX logs (`overfull`, `underfull`, undefined refs/cites/control sequence, missing files, duplicate destination).
- Python syntax audit for `reports/**/code/*.py` and `src/**/*.py` via `py_compile`.
- Writes machine-readable outputs:
  - `reports/_audit_all_tex_results.json`
  - `reports/_audit_python_results.json`

Usage:
```
python3 scripts/audit_reports.py
```

Fast:
```
python3 scripts/audit_reports.py --fast
```

TeX only:
```
python3 scripts/audit_reports.py --tex-only
```

Python only:
```
python3 scripts/audit_reports.py --python-only
```

## update_research_summary.py
Refreshes `docs/RESEARCH_SUMMARY.md` by:
- Updating the "最后更新" date to today.
- Regenerating the auto index table of report PDFs/TEX files.

Usage:
```
python3 scripts/update_research_summary.py
```

Dry run:
```
python3 scripts/update_research_summary.py --dry-run
```

## cleanup_local.py
Removes common local artifacts (safe cleanup):
- `.DS_Store`, `__pycache__`, `build/`, `.pytest_cache`, `*.pyc`, `*.pyo`
- Optional: remove `.venv/` and `venv/` with `--include-venv`

Usage:
```
python3 scripts/cleanup_local.py
```

Include venv removal:
```
python3 scripts/cleanup_local.py --include-venv
```

## archive_report_runs.py
Moves historical `runs/<YYYYMMDD_HHMMSS>` directories from active reports into `archives/reports/`,
creates/updates latest `manifest.json`, and appends schema-v2 records to `archives/reports/index.jsonl`.

Usage:
```
python3 scripts/archive_report_runs.py
python3 scripts/archive_report_runs.py --dry-run
python3 scripts/archive_report_runs.py --report ring_valley_dst
python3 scripts/archive_report_runs.py --verify
```

## normalize_artifact_paths.py
Normalizes absolute paths inside generated JSON artifacts to repository-relative paths.

Usage:
```
python3 scripts/normalize_artifact_paths.py
python3 scripts/normalize_artifact_paths.py --include-archives
```

## prune_legacy_artifacts.py
Archives legacy-named top-level report PDFs from active report folders into:
- `archives/reports/_legacy_named_artifacts/`
- manifest: `archives/reports/_legacy_named_artifacts/manifest.jsonl`

Usage:
```
python3 scripts/prune_legacy_artifacts.py --dry-run
python3 scripts/prune_legacy_artifacts.py
python3 scripts/prune_legacy_artifacts.py --report ring_valley_dst
```

## check_legacy_usage.py
Counts legacy report-name tokens / absolute path usage and writes:
- `docs/research_log/legacy_usage_report.json`

Usage:
```
python3 scripts/check_legacy_usage.py
```

## build_web_data.py
Builds website payloads from report assets into `site/public/data/v1` and copies web-preview artifacts to `site/public/artifacts`.

Usage:
```
python3 scripts/build_web_data.py --mode full
python3 scripts/build_web_data.py --mode changed
python3 scripts/build_web_data.py --reports ring_valley_dst grid2d_rect_bimodality
```

## build_agent_sync.py
Builds machine-readable agent sync outputs:
- `site/public/data/v1/agent/manifest.json`
- `site/public/data/v1/agent/reports.jsonl`
- `site/public/data/v1/agent/events.jsonl`

Also emits baseline multi-agent check artifacts:
- `artifacts/checks/agent-*.json`
- `artifacts/checks/crosscheck_report.json`

Usage:
```
python3 scripts/build_agent_sync.py
```

## validate_web_data.py
Validates web payloads and agent-sync outputs against JSON schemas:
- `schemas/web_report.schema.json`
- `schemas/agent_sync_v1.schema.json`

Usage:
```
python3 scripts/validate_web_data.py
python3 scripts/validate_web_data.py --data-root site/public/data/v1
```

## reportctl web commands
Unified wrappers for web workflows:
```
python3 scripts/reportctl.py web-data --mode changed
python3 scripts/reportctl.py agent-sync
python3 scripts/reportctl.py web-build --mode full
python3 scripts/reportctl.py web-preview --port 4173
```

## multiagent_optimize_loop.py
Runs a continuous multi-agent optimization/testing loop for the web stack.
Each round executes:
- Agent-A Data (`build_web_data.py`)
- Agent-B Sync (`build_agent_sync.py`)
- Agent-C Validate (`validate_web_data.py`)
- Agent-D QA tests (`pytest tests/test_web_payload_pipeline.py`)
- Agent-E QA docs (`check_docs_paths.py`)
- Agent-F Frontend build (`npm run build`)

Outputs:
- `artifacts/loop/rounds/*.json`
- `artifacts/loop/progress/latest.{json,md}`
- `artifacts/checks/crosscheck_report.json`

Usage:
```
python3 scripts/multiagent_optimize_loop.py --once
python3 scripts/multiagent_optimize_loop.py --interval-seconds 900 --until tomorrow
```

Helper control script:
```
./scripts/loop_ctl.sh start
./scripts/loop_ctl.sh status
./scripts/loop_ctl.sh stop
```

## migrate_report_names.py
Applies the report directory rename mapping (`2d_* -> grid2d_*`, `lazy_* -> ring_lazy_*`, etc.)
for historical migration replay (legacy tool; compatibility symlinks are no longer kept in active state).

Dry run:
```
python3 scripts/migrate_report_names.py --dry-run
```
