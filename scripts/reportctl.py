#!/usr/bin/env python3
from __future__ import annotations

import argparse
import py_compile
import subprocess
import sys
from pathlib import Path
from typing import Sequence

from report_registry import load_registry, resolve_report


REPO_ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable or "python3"
SITE_DIR = REPO_ROOT / "site"


def _pick_main_tex(report: dict, lang: str) -> str:
    tex_list = list(report.get("main_tex", []))
    if not tex_list:
        raise SystemExit(f"No main_tex configured for report {report['id']}")
    if lang == "cn":
        for name in tex_list:
            if "_cn" in name:
                return name
        raise SystemExit(f"report {report['id']} has no _cn main_tex")
    if lang == "en":
        for name in tex_list:
            if "_en" in name:
                return name
        if len(tex_list) == 1:
            return tex_list[0]
        raise SystemExit(f"report {report['id']} has no _en main_tex")
    raise SystemExit(f"unsupported lang: {lang}")


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
    tex_name = _pick_main_tex(item, lang=lang)
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
    return subprocess.run(cmd, cwd=report_dir).returncode


def cmd_audit(fast: bool, full: bool) -> int:
    mode_flag = "--fast" if fast else "--full" if full else ""
    cmd = [PYTHON, "scripts/audit_reports.py"]
    if mode_flag:
        cmd.append(mode_flag)
    return subprocess.run(cmd, cwd=REPO_ROOT).returncode


def cmd_archive(report: str | None, dry_run: bool, verify: bool) -> int:
    cmd = [PYTHON, "scripts/archive_report_runs.py"]
    if report:
        cmd += ["--report", report]
    if dry_run:
        cmd.append("--dry-run")
    if verify:
        cmd.append("--verify")
    return subprocess.run(cmd, cwd=REPO_ROOT).returncode


def _compile_targets() -> list[Path]:
    files: list[Path] = []
    files.extend(sorted((REPO_ROOT / "reports").glob("**/code/*.py")))
    files.extend(sorted((REPO_ROOT / "src").glob("**/*.py")))
    return [p for p in files if p.is_file()]


def _run_cmd(step: str, cmd: list[str], *, scope: str = "doctor") -> int:
    print(f"[{scope}] {step}: {' '.join(cmd)}")
    proc = subprocess.run(cmd, cwd=REPO_ROOT)
    if proc.returncode != 0:
        print(f"[{scope}] FAIL {step}: rc={proc.returncode}")
    return int(proc.returncode)


def cmd_doctor(*, full: bool, skip_pytest: bool) -> int:
    steps = [
        ("validate_registry", [PYTHON, "scripts/validate_registry.py"]),
        ("validate_archives", [PYTHON, "scripts/validate_archives.py"]),
        ("check_docs_paths", [PYTHON, "scripts/check_docs_paths.py"]),
    ]
    for name, cmd in steps:
        rc = _run_cmd(name, cmd, scope="doctor")
        if rc != 0:
            return rc

    print("[doctor] py_compile: reports/**/code/*.py + src/**/*.py")
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

    audit_cmd = [PYTHON, "scripts/audit_reports.py", "--full" if full else "--fast"]
    return _run_cmd("audit", audit_cmd, scope="doctor")


def cmd_prune_legacy_artifacts(*, dry_run: bool, report: str | None) -> int:
    cmd = [PYTHON, "scripts/prune_legacy_artifacts.py"]
    if dry_run:
        cmd.append("--dry-run")
    if report:
        cmd += ["--report", report]
    return subprocess.run(cmd, cwd=REPO_ROOT).returncode


def cmd_web_data(*, mode: str, reports: list[str]) -> int:
    cmd = [PYTHON, "scripts/build_web_data.py", "--mode", mode]
    if reports:
        cmd += ["--reports", *reports]
    return subprocess.run(cmd, cwd=REPO_ROOT).returncode


def cmd_agent_sync() -> int:
    cmd = [PYTHON, "scripts/build_agent_sync.py"]
    return subprocess.run(cmd, cwd=REPO_ROOT).returncode


def cmd_web_build(*, mode: str, skip_npm_ci: bool) -> int:
    steps = [
        ("web-data", [PYTHON, "scripts/build_web_data.py", "--mode", mode]),
        ("agent-sync", [PYTHON, "scripts/build_agent_sync.py"]),
        ("validate-web-data", [PYTHON, "scripts/validate_web_data.py"]),
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


def cmd_web_preview(*, port: int) -> int:
    out_dir = SITE_DIR / "out"
    if not out_dir.exists():
        print(f"[web-preview] missing build output: {out_dir}")
        print("[web-preview] run `python3 scripts/reportctl.py web-build` first")
        return 1

    cmd = [PYTHON, "-m", "http.server", str(port), "--directory", str(out_dir)]
    return subprocess.run(cmd, cwd=SITE_DIR).returncode


def cmd_openclaw_review() -> int:
    cmd = [PYTHON, "scripts/run_openclaw_review.py"]
    return subprocess.run(cmd, cwd=REPO_ROOT).returncode


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Unified report operations")
    sub = parser.add_subparsers(dest="subcmd", required=True)

    sub.add_parser("list", help="List registered reports")

    p_resolve = sub.add_parser("resolve", help="Resolve canonical report id")
    p_resolve.add_argument("--report", required=True)

    p_run = sub.add_parser("run", help="Run command in report directory")
    p_run.add_argument("--report", required=True)
    p_run.add_argument("command", nargs=argparse.REMAINDER)

    p_build = sub.add_parser("build", help="Build main TeX for a report")
    p_build.add_argument("--report", required=True)
    p_build.add_argument("--lang", required=True, choices=["cn", "en"])

    p_audit = sub.add_parser("audit", help="Run audit")
    p_audit.add_argument("--fast", action="store_true")
    p_audit.add_argument("--full", action="store_true")

    p_archive = sub.add_parser("archive", help="Archive timestamp runs")
    p_archive.add_argument("--dry-run", action="store_true")
    p_archive.add_argument("--report", default=None)
    p_archive.add_argument("--verify", action="store_true")

    p_doctor = sub.add_parser("doctor", help="Run full repository health checks")
    p_doctor.add_argument("--full", action="store_true", help="Use full TeX audit instead of fast mode")
    p_doctor.add_argument("--skip-pytest", action="store_true", help="Skip pytest execution")

    p_prune = sub.add_parser("prune-legacy-artifacts", help="Archive legacy-named top-level PDFs")
    p_prune.add_argument("--dry-run", action="store_true")
    p_prune.add_argument("--report", default=None)

    p_web_data = sub.add_parser("web-data", help="Build web JSON payloads")
    p_web_data.add_argument("--mode", choices=["full", "changed"], default="changed")
    p_web_data.add_argument("--report", action="append", default=[])

    sub.add_parser("agent-sync", help="Build agent-sync JSONL + manifest outputs")

    p_web_build = sub.add_parser("web-build", help="Build web data + site static export")
    p_web_build.add_argument("--mode", choices=["full", "changed"], default="changed")
    p_web_build.add_argument("--skip-npm-ci", action="store_true")

    p_web_preview = sub.add_parser("web-preview", help="Serve built static site locally")
    p_web_preview.add_argument("--port", type=int, default=4173)

    sub.add_parser("openclaw-review", help="Run OpenClaw high-thinking QA review and write artifacts/checks/openclaw_review.json")

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
    if args.subcmd == "audit":
        return cmd_audit(bool(args.fast), bool(args.full))
    if args.subcmd == "archive":
        return cmd_archive(args.report, bool(args.dry_run), bool(args.verify))
    if args.subcmd == "doctor":
        return cmd_doctor(full=bool(args.full), skip_pytest=bool(args.skip_pytest))
    if args.subcmd == "prune-legacy-artifacts":
        return cmd_prune_legacy_artifacts(dry_run=bool(args.dry_run), report=args.report)
    if args.subcmd == "web-data":
        return cmd_web_data(mode=str(args.mode), reports=list(args.report))
    if args.subcmd == "agent-sync":
        return cmd_agent_sync()
    if args.subcmd == "web-build":
        return cmd_web_build(mode=str(args.mode), skip_npm_ci=bool(args.skip_npm_ci))
    if args.subcmd == "web-preview":
        return cmd_web_preview(port=int(args.port))
    if args.subcmd == "openclaw-review":
        return cmd_openclaw_review()
    raise SystemExit(f"unsupported subcmd: {args.subcmd}")


if __name__ == "__main__":
    raise SystemExit(main())
