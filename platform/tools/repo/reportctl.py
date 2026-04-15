#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import py_compile
import subprocess
import sys
from pathlib import Path
from typing import Sequence

from report_registry import load_registry, resolve_report


REPO_ROOT = Path(__file__).resolve().parents[3]
SITE_DIR = REPO_ROOT / "platform" / "web"
TOOL_ROOT = REPO_ROOT / "platform" / "tools"


def _preferred_python() -> str:
    repo_python = REPO_ROOT / ".venv" / "bin" / "python"
    if repo_python.exists() and os.access(repo_python, os.X_OK):
        try:
            proc = subprocess.run(
                [str(repo_python), "--version"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=3,
                check=False,
            )
            if proc.returncode == 0:
                return str(repo_python)
        except (OSError, subprocess.SubprocessError):
            pass
    return sys.executable or "python3"


PYTHON = _preferred_python()


def _repo_tool(name: str) -> Path:
    return TOOL_ROOT / "repo" / name


def _web_tool(name: str) -> Path:
    return TOOL_ROOT / "web" / name


def _automation_tool(name: str) -> Path:
    return TOOL_ROOT / "automation" / name


def _tool_cmd(tool_path: Path, *args: str) -> list[str]:
    return [PYTHON, str(tool_path), *args]


def _pick_main_tex(report: dict, lang: str) -> str:
    tex_list = list(report.get("main_tex", []))
    if not tex_list:
        raise SystemExit(f"No main_tex configured for report {report['id']}")

    def _has_lang_suffix(name: str, lang_code: str) -> bool:
        stem = Path(name).stem.lower()
        return stem.endswith(f"_{lang_code.lower()}")

    if lang == "cn":
        for name in tex_list:
            if _has_lang_suffix(name, "cn"):
                return name
        raise SystemExit(f"report {report['id']} has no _cn main_tex")
    if lang == "en":
        for name in tex_list:
            if _has_lang_suffix(name, "en"):
                return name
        if len(tex_list) == 1:
            return tex_list[0]
        raise SystemExit(f"report {report['id']} has no _en main_tex")
    raise SystemExit(f"unsupported lang: {lang}")


def _expand_build_lang(lang: str) -> list[str]:
    token = str(lang).strip().lower()
    if token in {"cn", "en"}:
        return [token]
    parts = [p.strip() for p in token.split("/") if p.strip()]
    if len(parts) == 2 and set(parts) == {"cn", "en"}:
        return parts
    raise SystemExit(
        f"unsupported build lang: {lang}; expected one of cn, en, en/cn, cn/en"
    )


def _run_cmd(step: str, cmd: list[str], *, scope: str) -> int:
    print(f"[{scope}] {step}: {' '.join(cmd)}")
    proc = subprocess.run(cmd, cwd=REPO_ROOT)
    if proc.returncode != 0:
        print(f"[{scope}] FAIL {step}: rc={proc.returncode}")
    return int(proc.returncode)


def _run_tool(step: str, tool_path: Path, *args: str, scope: str) -> int:
    return _run_cmd(step, _tool_cmd(tool_path, *args), scope=scope)


def _compile_targets() -> list[Path]:
    files: list[Path] = []
    files.extend(sorted((REPO_ROOT / "research" / "reports").glob("**/code/*.py")))
    files.extend(sorted((REPO_ROOT / "packages" / "vkcore" / "src").glob("**/*.py")))
    return [p for p in files if p.is_file()]


def cmd_list() -> int:
    for item in load_registry():
        aliases = ", ".join(item.get("aliases", [])) or "-"
        print(f"{item['id']}\taliases=[{aliases}]\tpath={item['path']}")
    return 0


def cmd_resolve(report_token: str) -> int:
    try:
        item = resolve_report(report_token, load_registry())
    except KeyError as exc:
        raise SystemExit(str(exc))
    print(item["id"])
    print(item["path"])
    return 0


def cmd_run(report_token: str, command: Sequence[str]) -> int:
    try:
        item = resolve_report(report_token, load_registry())
    except KeyError as exc:
        raise SystemExit(str(exc))
    report_dir = REPO_ROOT / item["path"]
    cmd = list(command)
    if cmd and cmd[0] == "--":
        cmd = cmd[1:]
    if not cmd:
        print(f"Resolved: {item['id']} -> {report_dir}")
        print(f"Manuscript dir: {item.get('manuscript_dir', 'manuscript')}")
        print(f"Artifact dir: {item.get('artifact_dir', 'artifacts')}")
        print(f"Main TeX: {', '.join(item.get('main_tex', []))}")
        print(f"Entry scripts: {', '.join(item.get('entry_scripts', [])) or '-'}")
        return 0
    proc = subprocess.run(cmd, cwd=report_dir)
    return int(proc.returncode)


def cmd_build(report_token: str, lang: str) -> int:
    try:
        item = resolve_report(report_token, load_registry())
    except KeyError as exc:
        raise SystemExit(str(exc))
    report_dir = REPO_ROOT / item["path"]
    manuscript_dir = report_dir / item.get("manuscript_dir", "manuscript")
    for lang_code in _expand_build_lang(lang):
        tex_name = _pick_main_tex(item, lang=lang_code)
        engine = "-xelatex" if "_cn" in tex_name else "-pdf"
        cmd = [
            "latexmk",
            engine,
            "-interaction=nonstopmode",
            "-halt-on-error",
            "-auxdir=build",
            "-emulate-aux-dir",
            tex_name,
        ]
        rc = subprocess.run(cmd, cwd=manuscript_dir).returncode
        if rc == 0:
            continue

        retry_cmd = ["latexmk", "-gg", *cmd[1:]]
        print(
            f"[build] initial build failed (rc={rc}), retrying with forced refresh: {' '.join(retry_cmd)}"
        )
        retry_rc = subprocess.run(retry_cmd, cwd=manuscript_dir).returncode
        if retry_rc != 0:
            return retry_rc
    return 0


def cmd_summary(*, dry_run: bool, max_progress_items: int) -> int:
    args = []
    if dry_run:
        args.append("--dry-run")
    args += ["--max-progress-items", str(max(1, int(max_progress_items)))]
    return subprocess.run(
        _tool_cmd(_repo_tool("update_research_summary.py"), *args),
        cwd=REPO_ROOT,
    ).returncode


def cmd_cleanup(*, include_venv: bool, dry_run: bool, include_runtime: bool) -> int:
    args = []
    if include_venv:
        args.append("--include-venv")
    if dry_run:
        args.append("--dry-run")
    if include_runtime:
        args.append("--include-runtime")
    return subprocess.run(
        _tool_cmd(_repo_tool("cleanup_local.py"), *args),
        cwd=REPO_ROOT,
    ).returncode


def cmd_validate_registry() -> int:
    return subprocess.run(
        _tool_cmd(_repo_tool("validate_registry.py")),
        cwd=REPO_ROOT,
    ).returncode


def cmd_validate_archives() -> int:
    return subprocess.run(
        _tool_cmd(_repo_tool("validate_archives.py")),
        cwd=REPO_ROOT,
    ).returncode


def cmd_check_docs_paths() -> int:
    return subprocess.run(
        _tool_cmd(_repo_tool("check_docs_paths.py")),
        cwd=REPO_ROOT,
    ).returncode


def cmd_audit(fast: bool, full: bool) -> int:
    args: list[str] = []
    if fast:
        args.append("--fast")
    elif full:
        args.append("--full")
    return subprocess.run(
        _tool_cmd(_repo_tool("audit_reports.py"), *args),
        cwd=REPO_ROOT,
    ).returncode


def cmd_archive(report: str | None, dry_run: bool, verify: bool) -> int:
    args: list[str] = []
    if report:
        args += ["--report", report]
    if dry_run:
        args.append("--dry-run")
    if verify:
        args.append("--verify")
    return subprocess.run(
        _tool_cmd(_repo_tool("archive_report_runs.py"), *args),
        cwd=REPO_ROOT,
    ).returncode


def cmd_doctor(*, full: bool, skip_pytest: bool) -> int:
    steps = [
        ("validate-registry", _tool_cmd(_repo_tool("validate_registry.py"))),
        ("validate-archives", _tool_cmd(_repo_tool("validate_archives.py"))),
        ("check-docs-paths", _tool_cmd(_repo_tool("check_docs_paths.py"))),
    ]
    for name, cmd in steps:
        rc = _run_cmd(name, cmd, scope="doctor")
        if rc != 0:
            return rc

    print("[doctor] py_compile: research/reports/**/code/*.py + packages/vkcore/src/**/*.py")
    for py in _compile_targets():
        try:
            py_compile.compile(str(py), doraise=True)
        except py_compile.PyCompileError as exc:
            print(f"[doctor] FAIL py_compile: {py.relative_to(REPO_ROOT)}")
            print(str(exc))
            return 1

    if not skip_pytest:
        rc = _run_cmd("pytest", [PYTHON, "-m", "pytest", "-q"], scope="doctor")
        if rc != 0:
            return rc

    audit_mode = "--full" if full else "--fast"
    return _run_tool(
        "audit",
        _repo_tool("audit_reports.py"),
        audit_mode,
        scope="doctor",
    )


def cmd_prune_legacy_artifacts(*, dry_run: bool, report: str | None) -> int:
    args: list[str] = []
    if dry_run:
        args.append("--dry-run")
    if report:
        args += ["--report", report]
    return subprocess.run(
        _tool_cmd(_repo_tool("prune_legacy_artifacts.py"), *args),
        cwd=REPO_ROOT,
    ).returncode


def cmd_web_data(*, mode: str, reports: list[str]) -> int:
    args = ["--mode", mode]
    if reports:
        args += ["--reports", *reports]
    return subprocess.run(
        _tool_cmd(_web_tool("build_web_data.py"), *args),
        cwd=REPO_ROOT,
    ).returncode


def cmd_book_data() -> int:
    steps = [
        ("build-glossary", _tool_cmd(_web_tool("build_glossary.py"))),
        ("build-book-content", _tool_cmd(_web_tool("build_book_content.py"))),
        ("build-book-backbone", _tool_cmd(_web_tool("build_book_backbone.py"))),
    ]
    for name, cmd in steps:
        rc = _run_cmd(name, cmd, scope="book-data")
        if rc != 0:
            return rc
    return 0


def cmd_backbone_data() -> int:
    return subprocess.run(
        _tool_cmd(_web_tool("build_book_backbone.py")),
        cwd=REPO_ROOT,
    ).returncode


def cmd_agent_sync() -> int:
    return subprocess.run(
        _tool_cmd(_web_tool("build_agent_sync.py")),
        cwd=REPO_ROOT,
    ).returncode


def cmd_translation_qc(*, high_max: int, warning_max: int) -> int:
    args = [
        "--high-max",
        str(max(0, high_max)),
        "--warning-max",
        str(max(0, warning_max)),
    ]
    return subprocess.run(
        _tool_cmd(_web_tool("validate_bilingual_quality.py"), *args),
        cwd=REPO_ROOT,
    ).returncode


def cmd_validate_web_data(*, data_root: str | None) -> int:
    args: list[str] = []
    if data_root:
        args += ["--data-root", data_root]
    return subprocess.run(
        _tool_cmd(_web_tool("validate_web_data.py"), *args),
        cwd=REPO_ROOT,
    ).returncode


def cmd_web_build(*, mode: str, skip_npm_ci: bool) -> int:
    steps = [
        ("web-data", _tool_cmd(_web_tool("build_web_data.py"), "--mode", mode)),
        ("build-glossary", _tool_cmd(_web_tool("build_glossary.py"))),
        ("build-book-content", _tool_cmd(_web_tool("build_book_content.py"))),
        ("build-book-backbone", _tool_cmd(_web_tool("build_book_backbone.py"))),
        ("translation-qc", _tool_cmd(_web_tool("validate_bilingual_quality.py"))),
        ("agent-sync", _tool_cmd(_web_tool("build_agent_sync.py"))),
        ("validate-web-data", _tool_cmd(_web_tool("validate_web_data.py"))),
    ]
    for name, cmd in steps:
        rc = _run_cmd(name, cmd, scope="web-build")
        if rc != 0:
            return rc

    if not SITE_DIR.exists():
        print(f"[web-build] missing site dir: {SITE_DIR}")
        return 1

    if not skip_npm_ci:
        print("[web-build] npm ci")
        rc = subprocess.run(["npm", "ci"], cwd=SITE_DIR).returncode
        if rc != 0:
            return rc

    print("[web-build] npm run build")
    return subprocess.run(["npm", "run", "build"], cwd=SITE_DIR).returncode


def _git_capture(cmd: list[str]) -> tuple[int, str]:
    proc = subprocess.run(
        cmd,
        cwd=REPO_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    return int(proc.returncode), proc.stdout.strip()


def git_sync_status(*, fetch_remote: bool) -> dict[str, object]:
    if fetch_remote:
        subprocess.run(["git", "fetch", "origin"], cwd=REPO_ROOT, check=False)

    _, branch = _git_capture(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    branch = branch or "HEAD"

    _, dirty_raw = _git_capture(["git", "status", "--porcelain"])
    dirty_count = len([line for line in dirty_raw.splitlines() if line.strip()])

    ahead = 0
    behind = 0
    rc, diff_raw = _git_capture(
        ["git", "rev-list", "--left-right", "--count", f"HEAD...origin/{branch}"]
    )
    if rc == 0 and diff_raw:
        parts = diff_raw.split()
        if len(parts) >= 2:
            ahead = int(parts[0])
            behind = int(parts[1])

    _, origin_url = _git_capture(["git", "config", "--get", "remote.origin.url"])
    return {
        "branch": branch,
        "origin": origin_url,
        "ahead": ahead,
        "behind": behind,
        "dirty_count": dirty_count,
    }


def cmd_sync_local_remote(
    *,
    mode: str,
    skip_npm_ci: bool,
    no_site_build: bool,
    fetch_remote: bool,
) -> int:
    status_before = git_sync_status(fetch_remote=fetch_remote)
    print(f"[sync-local-remote] git status before: {status_before}", flush=True)

    if no_site_build:
        steps = [
            ("web-data", _tool_cmd(_web_tool("build_web_data.py"), "--mode", mode)),
            ("agent-sync", _tool_cmd(_web_tool("build_agent_sync.py"))),
            ("validate-web-data", _tool_cmd(_web_tool("validate_web_data.py"))),
        ]
        for name, cmd in steps:
            rc = _run_cmd(name, cmd, scope="sync-local-remote")
            if rc != 0:
                return rc
        rc = 0
    else:
        rc = cmd_web_build(mode=mode, skip_npm_ci=skip_npm_ci)
        if rc != 0:
            return rc

    status_after = git_sync_status(fetch_remote=False)
    print(f"[sync-local-remote] git status after: {status_after}", flush=True)
    return rc


def cmd_web_preview(*, port: int) -> int:
    out_dir = SITE_DIR / "out"
    if not out_dir.exists():
        print(f"[web-preview] missing build output: {out_dir}")
        print("[web-preview] run `python3 scripts/reportctl.py web-build` first")
        return 1
    return subprocess.run(
        [PYTHON, "-m", "http.server", str(port), "--directory", str(out_dir)],
        cwd=SITE_DIR,
    ).returncode


def cmd_book_preview(*, port: int) -> int:
    out_dir = SITE_DIR / "out"
    if not out_dir.exists():
        print(f"[book-preview] missing build output: {out_dir}")
        print("[book-preview] run `python3 scripts/reportctl.py web-build` first")
        return 1
    print(f"[book-preview] open http://127.0.0.1:{port}/book/ after server starts")
    return subprocess.run(
        [PYTHON, "-m", "http.server", str(port), "--directory", str(out_dir)],
        cwd=SITE_DIR,
    ).returncode


def cmd_openclaw_review() -> int:
    return subprocess.run(
        _tool_cmd(_automation_tool("run_openclaw_review.py")),
        cwd=REPO_ROOT,
    ).returncode


def cmd_publication_pdf(*, lang: str, no_appendix: bool, base_url: str) -> int:
    args = ["--lang", lang, "--base-url", base_url]
    if no_appendix:
        args.append("--no-appendix")
    return subprocess.run(
        _tool_cmd(_web_tool("build_publication_pdf.py"), *args),
        cwd=REPO_ROOT,
    ).returncode


def cmd_agent_pack() -> int:
    return subprocess.run(
        _tool_cmd(_web_tool("build_agent_pack.py")),
        cwd=REPO_ROOT,
    ).returncode


def cmd_deliverables(
    *,
    mode: str,
    skip_site_build: bool,
    skip_openclaw: bool,
    content_rounds: int,
) -> int:
    args = ["--mode", mode, "--content-rounds", str(max(1, content_rounds))]
    if skip_site_build:
        args.append("--skip-site-build")
    if skip_openclaw:
        args.append("--skip-openclaw")
    return subprocess.run(
        _tool_cmd(_web_tool("build_three_deliverables.py"), *args),
        cwd=REPO_ROOT,
    ).returncode


def cmd_content_iterate(
    *,
    rounds: int,
    mode: str,
    build_site: bool,
    skip_openclaw: bool,
    target_score: int,
) -> int:
    args = [
        "--rounds",
        str(max(1, rounds)),
        "--mode",
        mode,
        "--target-score",
        str(max(1, target_score)),
    ]
    if build_site:
        args.append("--build-site")
    if skip_openclaw:
        args.append("--skip-openclaw")
    return subprocess.run(
        _tool_cmd(_automation_tool("run_content_iteration.py"), *args),
        cwd=REPO_ROOT,
    ).returncode


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Canonical CLI for valley-k-small")
    sub = parser.add_subparsers(dest="subcmd", required=True)

    sub.add_parser("list", help="List registered reports")

    p_resolve = sub.add_parser("resolve", help="Resolve canonical report id")
    p_resolve.add_argument("--report", required=True)

    p_run = sub.add_parser("run", help="Run a command inside a report directory")
    p_run.add_argument("--report", required=True)
    p_run.add_argument("command", nargs=argparse.REMAINDER)

    p_build = sub.add_parser("build", help="Build main TeX for a report")
    p_build.add_argument("--report", required=True)
    p_build.add_argument("--lang", required=True, choices=["cn", "en", "en/cn", "cn/en"])

    p_summary = sub.add_parser("summary", help="Refresh research summary date and auto index")
    p_summary.add_argument("--dry-run", action="store_true")
    p_summary.add_argument("--max-progress-items", type=int, default=30)

    p_cleanup = sub.add_parser("cleanup", help="Remove local artifacts and hidden runtime state")
    p_cleanup.add_argument("--include-venv", action="store_true")
    p_cleanup.add_argument("--dry-run", action="store_true")
    p_cleanup.add_argument("--include-runtime", action="store_true")

    sub.add_parser("validate-registry", help="Validate report registry")
    sub.add_parser("validate-archives", help="Validate archive metadata")
    sub.add_parser("check-docs-paths", help="Validate active documentation path references")

    p_audit = sub.add_parser("audit", help="Run repository audit")
    p_audit.add_argument("--fast", action="store_true")
    p_audit.add_argument("--full", action="store_true")

    p_archive = sub.add_parser("archive", help="Archive timestamp runs")
    p_archive.add_argument("--dry-run", action="store_true")
    p_archive.add_argument("--report", default=None)
    p_archive.add_argument("--verify", action="store_true")

    p_doctor = sub.add_parser("doctor", help="Run repository health checks")
    p_doctor.add_argument("--full", action="store_true")
    p_doctor.add_argument("--skip-pytest", action="store_true")

    p_prune = sub.add_parser(
        "prune-legacy-artifacts",
        help="Archive legacy-named top-level report PDFs",
    )
    p_prune.add_argument("--dry-run", action="store_true")
    p_prune.add_argument("--report", default=None)

    p_web_data = sub.add_parser("web-data", help="Build web JSON payloads")
    p_web_data.add_argument("--mode", choices=["full", "changed"], default="changed")
    p_web_data.add_argument("--report", action="append", default=[])

    sub.add_parser("book-data", help="Build chapterized book payloads + glossary")
    sub.add_parser("backbone-data", help="Build logical backbone payload")
    sub.add_parser("agent-sync", help="Build agent-sync JSONL + manifest outputs")

    p_translation_qc = sub.add_parser("translation-qc", help="Run bilingual CN/EN quality checks")
    p_translation_qc.add_argument("--high-max", type=int, default=0)
    p_translation_qc.add_argument("--warning-max", type=int, default=80)

    p_validate_web = sub.add_parser("validate-web-data", help="Validate generated web payloads")
    p_validate_web.add_argument("--data-root", default=None)

    p_web_build = sub.add_parser("web-build", help="Build web data plus static site export")
    p_web_build.add_argument("--mode", choices=["full", "changed"], default="changed")
    p_web_build.add_argument("--skip-npm-ci", action="store_true")

    p_sync = sub.add_parser(
        "sync-local-remote",
        help="Sync payloads and report local/origin git status",
    )
    p_sync.add_argument("--mode", choices=["full", "changed"], default="full")
    p_sync.add_argument("--skip-npm-ci", action="store_true")
    p_sync.add_argument("--no-site-build", action="store_true")
    p_sync.add_argument("--no-fetch", action="store_true")

    p_web_preview = sub.add_parser("web-preview", help="Serve built static site locally")
    p_web_preview.add_argument("--port", type=int, default=4173)

    p_book_preview = sub.add_parser("book-preview", help="Serve built site and highlight /book")
    p_book_preview.add_argument("--port", type=int, default=4173)

    sub.add_parser("openclaw-review", help="Run OpenClaw QA review")

    p_pub = sub.add_parser("publication-pdf", help="Build publication-grade compendium PDF")
    p_pub.add_argument("--lang", choices=["en", "cn"], default="en")
    p_pub.add_argument("--no-appendix", action="store_true")
    p_pub.add_argument(
        "--base-url",
        default="https://zhouyi-xiaoxiao.github.io/valley-k-small/",
    )

    sub.add_parser("agent-pack", help="Build hidden agent handoff pack under .local/")

    p_deliv = sub.add_parser(
        "deliverables",
        help="Build website, publication PDF, and agent pack deliverables",
    )
    p_deliv.add_argument("--mode", choices=["full", "changed"], default="changed")
    p_deliv.add_argument("--skip-site-build", action="store_true")
    p_deliv.add_argument("--skip-openclaw", action="store_true")
    p_deliv.add_argument("--content-rounds", type=int, default=2)

    p_iter = sub.add_parser("content-iterate", help="Run the persistent content QA loop")
    p_iter.add_argument("--rounds", type=int, default=3)
    p_iter.add_argument("--mode", choices=["full", "changed"], default="full")
    p_iter.add_argument("--build-site", action="store_true")
    p_iter.add_argument("--skip-openclaw", action="store_true")
    p_iter.add_argument("--target-score", type=int, default=75)

    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.subcmd == "list":
        return cmd_list()
    if args.subcmd == "resolve":
        return cmd_resolve(args.report)
    if args.subcmd == "run":
        return cmd_run(args.report, args.command)
    if args.subcmd == "build":
        return cmd_build(args.report, args.lang)
    if args.subcmd == "summary":
        return cmd_summary(
            dry_run=bool(args.dry_run),
            max_progress_items=int(args.max_progress_items),
        )
    if args.subcmd == "cleanup":
        return cmd_cleanup(
            include_venv=bool(args.include_venv),
            dry_run=bool(args.dry_run),
            include_runtime=bool(args.include_runtime),
        )
    if args.subcmd == "validate-registry":
        return cmd_validate_registry()
    if args.subcmd == "validate-archives":
        return cmd_validate_archives()
    if args.subcmd == "check-docs-paths":
        return cmd_check_docs_paths()
    if args.subcmd == "audit":
        return cmd_audit(bool(args.fast), bool(args.full))
    if args.subcmd == "archive":
        return cmd_archive(args.report, bool(args.dry_run), bool(args.verify))
    if args.subcmd == "doctor":
        return cmd_doctor(full=bool(args.full), skip_pytest=bool(args.skip_pytest))
    if args.subcmd == "prune-legacy-artifacts":
        return cmd_prune_legacy_artifacts(
            dry_run=bool(args.dry_run),
            report=args.report,
        )
    if args.subcmd == "web-data":
        return cmd_web_data(mode=str(args.mode), reports=list(args.report))
    if args.subcmd == "book-data":
        return cmd_book_data()
    if args.subcmd == "backbone-data":
        return cmd_backbone_data()
    if args.subcmd == "agent-sync":
        return cmd_agent_sync()
    if args.subcmd == "translation-qc":
        return cmd_translation_qc(
            high_max=int(args.high_max),
            warning_max=int(args.warning_max),
        )
    if args.subcmd == "validate-web-data":
        return cmd_validate_web_data(data_root=args.data_root)
    if args.subcmd == "web-build":
        return cmd_web_build(
            mode=str(args.mode),
            skip_npm_ci=bool(args.skip_npm_ci),
        )
    if args.subcmd == "sync-local-remote":
        return cmd_sync_local_remote(
            mode=str(args.mode),
            skip_npm_ci=bool(args.skip_npm_ci),
            no_site_build=bool(args.no_site_build),
            fetch_remote=not bool(args.no_fetch),
        )
    if args.subcmd == "web-preview":
        return cmd_web_preview(port=int(args.port))
    if args.subcmd == "book-preview":
        return cmd_book_preview(port=int(args.port))
    if args.subcmd == "openclaw-review":
        return cmd_openclaw_review()
    if args.subcmd == "publication-pdf":
        return cmd_publication_pdf(
            lang=str(args.lang),
            no_appendix=bool(args.no_appendix),
            base_url=str(args.base_url),
        )
    if args.subcmd == "agent-pack":
        return cmd_agent_pack()
    if args.subcmd == "deliverables":
        return cmd_deliverables(
            mode=str(args.mode),
            skip_site_build=bool(args.skip_site_build),
            skip_openclaw=bool(args.skip_openclaw),
            content_rounds=int(args.content_rounds),
        )
    if args.subcmd == "content-iterate":
        return cmd_content_iterate(
            rounds=int(args.rounds),
            mode=str(args.mode),
            build_site=bool(args.build_site),
            skip_openclaw=bool(args.skip_openclaw),
            target_score=int(args.target_score),
        )
    raise SystemExit(f"unsupported subcmd: {args.subcmd}")


if __name__ == "__main__":
    raise SystemExit(main())
