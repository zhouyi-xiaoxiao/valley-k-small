#!/usr/bin/env python3
"""Run repository-wide report audits (metadata + TeX build + Python syntax)."""

from __future__ import annotations

import argparse
import json
import py_compile
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from report_registry import load_registry


REPO_ROOT = Path(__file__).resolve().parents[3]
REPORTS_ROOT = REPO_ROOT / "research" / "reports"
AUDIT_ROOT = REPO_ROOT / "research" / "archives" / "meta" / "repo_audits"
TEX_JSON = AUDIT_ROOT / "_audit_all_tex_results.json"
PY_JSON = AUDIT_ROOT / "_audit_python_results.json"
AUDIT_ROOT.mkdir(parents=True, exist_ok=True)

LATEXMK_COMMON = [
    "latexmk",
    "-interaction=nonstopmode",
    "-halt-on-error",
    "-auxdir=build",
    "-emulate-aux-dir",
]

WARN_PATTERNS = {
    "overfull": re.compile(r"Overfull \\\\hbox"),
    "underfull": re.compile(r"Underfull \\\\hbox"),
    "undef_ref": re.compile(r"LaTeX Warning: Reference .* undefined"),
    "undef_cite": re.compile(r"LaTeX Warning: Citation .* undefined"),
    "undefined_control": re.compile(r"Undefined control sequence"),
    "missing_file": re.compile(r"LaTeX Error: File `.*' not found"),
    "duplicate_dest": re.compile(r"destination with the same identifier"),
}


@dataclass(frozen=True)
class TexCase:
    path: Path
    engine: str


def detect_engine(tex_path: Path) -> str:
    name = tex_path.name.lower()
    return "-xelatex" if "_cn" in name else "-pdf"


def run_metadata_validation() -> None:
    checks = (
        ("registry", ["python3", "platform/tools/repo/validate_registry.py"]),
        ("archives", ["python3", "platform/tools/repo/validate_archives.py"]),
    )
    for name, cmd in checks:
        proc = subprocess.run(cmd, cwd=REPO_ROOT, check=False)
        if proc.returncode != 0:
            print(f"[meta] FAIL {name}: rc={proc.returncode} cmd={' '.join(cmd)}")
            raise SystemExit(1)
        print(f"[meta] ok   {name}")


def discover_tex_cases(*, mode: str) -> list[TexCase]:
    cases: list[TexCase] = []
    if mode == "fast":
        for item in load_registry():
            report_dir = REPO_ROOT / item["path"]
            manuscript_dir = report_dir / item.get("manuscript_dir", "manuscript")
            for tex_name in item.get("main_tex", []):
                tex = manuscript_dir / tex_name
                if tex.exists():
                    cases.append(TexCase(path=tex, engine=detect_engine(tex)))
        return sorted(cases, key=lambda c: c.path.as_posix())

    for tex in sorted(REPORTS_ROOT.glob("*/manuscript/**/*.tex")):
        if "/build/" in tex.as_posix():
            continue
        cases.append(TexCase(path=tex, engine=detect_engine(tex)))
    return cases


def parse_warnings(log_text: str) -> dict[str, int]:
    return {k: len(p.findall(log_text)) for k, p in WARN_PATTERNS.items()}


def run_tex_audit(*, mode: str) -> tuple[list[dict[str, Any]], dict[str, int]]:
    rows: list[dict[str, Any]] = []
    agg = {k: 0 for k in WARN_PATTERNS}
    if shutil.which("latexmk") is None:
        print("[tex] SKIP latexmk not found; TeX audit skipped")
        TEX_JSON.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return rows, agg

    for case in discover_tex_cases(mode=mode):
        tex_dir = case.path.parent
        cmd = LATEXMK_COMMON + [case.engine, case.path.name]
        proc = subprocess.run(
            cmd,
            cwd=tex_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )
        log_path = tex_dir / "build" / f"{case.path.stem}.log"
        log_text = log_path.read_text(encoding="utf-8", errors="ignore") if log_path.exists() else proc.stdout
        warn = parse_warnings(log_text)
        for k, v in warn.items():
            agg[k] += v
        rows.append(
            {
                "tex": case.path.relative_to(REPO_ROOT).as_posix(),
                "engine": case.engine,
                "rc": proc.returncode,
                "warn": warn,
                "mode": mode,
            }
        )
        print(f"[tex] rc={proc.returncode:>2} {case.engine:>8} {case.path.relative_to(REPO_ROOT)}")
    TEX_JSON.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return rows, agg


def run_python_audit() -> dict[str, Any]:
    files: list[Path] = []
    for py in sorted(REPORTS_ROOT.glob("**/code/*.py")):
        try:
            report_dir_name = py.relative_to(REPORTS_ROOT).parts[0]
        except Exception:
            continue
        if (REPORTS_ROOT / report_dir_name).is_symlink():
            continue
        files.append(py)

    for py in sorted((REPO_ROOT / "packages" / "vkcore" / "src").glob("**/*.py")):
        if "__pycache__" in py.parts:
            continue
        files.append(py)

    errors: list[dict[str, str]] = []
    for py in files:
        try:
            py_compile.compile(str(py), doraise=True)
        except py_compile.PyCompileError as exc:
            errors.append({"file": py.relative_to(REPO_ROOT).as_posix(), "error": str(exc)})
            print(f"[py ] FAIL {py.relative_to(REPO_ROOT)}")
        else:
            print(f"[py ]  ok  {py.relative_to(REPO_ROOT)}")

    result = {"files": len(files), "errors": errors}
    PY_JSON.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit all reports in this repository.")
    parser.add_argument("--tex-only", action="store_true", help="Run only TeX audit.")
    parser.add_argument("--python-only", action="store_true", help="Run only Python syntax audit.")
    parser.add_argument("--fast", action="store_true", help="Fast mode: audit only registry main TeX files.")
    parser.add_argument("--full", action="store_true", help="Full mode: audit all TeX files under research/reports/*/manuscript/.")
    args = parser.parse_args()

    if args.tex_only and args.python_only:
        raise SystemExit("--tex-only and --python-only cannot be used together.")
    if args.fast and args.full:
        raise SystemExit("--fast and --full cannot be used together.")

    mode = "fast" if args.fast else "full"

    run_metadata_validation()

    tex_rows: list[dict[str, Any]] = []
    tex_agg: dict[str, int] = {k: 0 for k in WARN_PATTERNS}
    py_result: dict[str, Any] = {"files": 0, "errors": []}

    if not args.python_only:
        tex_rows, tex_agg = run_tex_audit(mode=mode)
    if not args.tex_only:
        py_result = run_python_audit()

    if not args.python_only:
        fails = [r for r in tex_rows if r["rc"] != 0]
        print("\n[tex-summary]")
        print(f"mode={mode} total={len(tex_rows)} fails={len(fails)} warnings={tex_agg}")
        for r in fails:
            print(f"  FAIL rc={r['rc']}: {r['tex']}")
    if not args.tex_only:
        print("\n[py-summary]")
        print(f"files={py_result['files']} errors={len(py_result['errors'])}")
        for err in py_result["errors"]:
            print(f"  FAIL: {err['file']}")

    tex_ok = True if args.python_only else all(r["rc"] == 0 for r in tex_rows)
    py_ok = True if args.tex_only else len(py_result["errors"]) == 0
    return 0 if tex_ok and py_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
