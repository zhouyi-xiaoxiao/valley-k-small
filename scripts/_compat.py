from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType


REPO_ROOT = Path(__file__).resolve().parents[1]
TOOL_ROOT = REPO_ROOT / "platform" / "tools"
SCRIPT_GROUPS = {
    "archive_report_runs.py": "repo",
    "audit_reports.py": "repo",
    "book_blueprint.py": "web",
    "build_agent_pack.py": "web",
    "build_agent_sync.py": "web",
    "build_book_backbone.py": "web",
    "build_book_content.py": "web",
    "build_glossary.py": "web",
    "build_publication_pdf.py": "web",
    "build_three_deliverables.py": "web",
    "build_web_data.py": "web",
    "check_docs_paths.py": "repo",
    "check_legacy_usage.py": "repo",
    "cleanup_local.py": "repo",
    "keepalive_ctl.py": "automation",
    "keepalive_runner.py": "automation",
    "migrate_archive_metadata_v2.py": "repo",
    "migrate_report_names.py": "repo",
    "multiagent_optimize_loop.py": "automation",
    "normalize_artifact_paths.py": "repo",
    "prune_legacy_artifacts.py": "repo",
    "report_registry.py": "repo",
    "reportctl.py": "repo",
    "run_content_iteration.py": "automation",
    "run_openclaw_review.py": "automation",
    "schema_utils.py": "repo",
    "update_research_summary.py": "repo",
    "validate_archives.py": "repo",
    "validate_bilingual_quality.py": "web",
    "validate_registry.py": "repo",
    "validate_web_data.py": "web",
    "worktree_hygiene.py": "repo",
}
_CACHE: dict[str, ModuleType] = {}


def _impl_path(wrapper_file: str) -> Path:
    name = Path(wrapper_file).name
    group = SCRIPT_GROUPS.get(name)
    if not group:
        raise RuntimeError(f"no compat mapping configured for {name}")
    return TOOL_ROOT / group / name


def _load_module(wrapper_file: str) -> ModuleType:
    name = Path(wrapper_file).name
    cached = _CACHE.get(name)
    if cached is not None:
        return cached

    impl_path = _impl_path(wrapper_file).resolve()
    if not impl_path.exists():
        raise RuntimeError(f"missing implementation for {name}: {impl_path}")

    for extra in [
        impl_path.parent,
        TOOL_ROOT / "repo",
        TOOL_ROOT / "web",
        TOOL_ROOT / "automation",
    ]:
        text = str(extra)
        if text not in sys.path:
            sys.path.insert(0, text)

    module_name = f"_compat_{name.replace('.', '_')}"
    spec = importlib.util.spec_from_file_location(module_name, impl_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"failed to load spec for {impl_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    _CACHE[name] = module
    return module


def export_impl(wrapper_file: str, target_globals: dict[str, object]) -> ModuleType:
    module = _load_module(wrapper_file)
    public = getattr(module, "__all__", None)
    if public is None:
        public = [name for name in module.__dict__ if not name.startswith("_")]
    for name in public:
        target_globals[name] = module.__dict__[name]
    target_globals.setdefault("__doc__", module.__doc__)
    return module


def run_main(wrapper_file: str) -> int:
    module = _load_module(wrapper_file)
    main = getattr(module, "main", None)
    if main is None:
        raise SystemExit(f"{Path(wrapper_file).name} has no main()")
    return int(main())
