#!/usr/bin/env python3
"""Round-based local optimizer for the ring shortcut encounter report."""

from __future__ import annotations

import argparse
import json
import shlex
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence

REPORT_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = REPORT_DIR.parents[1]
DEFAULT_PYTHON = REPO_ROOT / ".venv" / "bin" / "python"
LOOP_DIR = REPORT_DIR / "outputs" / "loop"
REPORT_TEST = REPO_ROOT / "tests" / "test_ring_two_walker_encounter_shortcut.py"


def run_command(cmd: Sequence[str], *, cwd: Path, log_path: Path) -> tuple[int, float]:
    start = time.perf_counter()
    with log_path.open("w", encoding="utf-8") as fh:
        fh.write(f"$ {shlex.join(cmd)}\n")
        fh.flush()
        proc = subprocess.run(cmd, cwd=str(cwd), stdout=fh, stderr=subprocess.STDOUT, check=False)
    duration = time.perf_counter() - start
    return int(proc.returncode), float(duration)


def latex_clean(tex_name: str, *, log_path: Path) -> tuple[int, float]:
    clean_cmd = [
        "latexmk",
        "-C",
        "-auxdir=build",
        "-emulate-aux-dir",
        tex_name,
    ]
    return run_command(clean_cmd, cwd=REPORT_DIR, log_path=log_path)


def build_steps(python_exec: str) -> list[tuple[str, list[str]]]:
    return [
        (
            "codegen",
            [python_exec, "code/two_walker_ring_encounter_report.py"],
        ),
        (
            "build_cn",
            [
                "latexmk",
                "-xelatex",
                "-interaction=nonstopmode",
                "-halt-on-error",
                "-auxdir=build",
                "-emulate-aux-dir",
                "ring_two_walker_encounter_shortcut_cn.tex",
            ],
        ),
        (
            "build_en",
            [
                "latexmk",
                "-pdf",
                "-interaction=nonstopmode",
                "-halt-on-error",
                "-auxdir=build",
                "-emulate-aux-dir",
                "ring_two_walker_encounter_shortcut_en.tex",
            ],
        ),
        (
            "py_compile",
            [
                python_exec,
                "-m",
                "py_compile",
                "code/two_walker_ring_encounter_report.py",
                "code/check_encounter_consistency.py",
                "code/continuous_optimize_loop.py",
            ],
        ),
        (
            "consistency_check",
            [python_exec, "code/check_encounter_consistency.py"],
        ),
        (
            "pytest_report",
            [python_exec, "-m", "pytest", "-q", str(REPORT_TEST)],
        ),
        (
            "refresh_research_summary",
            [python_exec, str(REPO_ROOT / "scripts" / "update_research_summary.py")],
        ),
    ]


def maybe_retry_with_latex_clean(
    step_name: str,
    cmd: Sequence[str],
    *,
    report_log_prefix: Path,
) -> tuple[int, float, bool]:
    if step_name not in {"build_cn", "build_en"}:
        return 1, 0.0, False

    tex_name = "ring_two_walker_encounter_shortcut_cn.tex" if step_name == "build_cn" else "ring_two_walker_encounter_shortcut_en.tex"
    clean_log = report_log_prefix.with_name(report_log_prefix.name + "_autofix_clean.log")
    retry_log = report_log_prefix.with_name(report_log_prefix.name + "_autofix_retry.log")

    clean_code, clean_dur = latex_clean(tex_name, log_path=clean_log)
    if clean_code != 0:
        return clean_code, clean_dur, False

    retry_code, retry_dur = run_command(cmd, cwd=REPORT_DIR, log_path=retry_log)
    return retry_code, (clean_dur + retry_dur), True


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rounds", type=int, default=2, help="Number of optimization rounds to run.")
    parser.add_argument(
        "--python",
        default=str(DEFAULT_PYTHON),
        help="Python executable for code generation/tests (default: repo .venv).",
    )
    parser.add_argument(
        "--stop-on-failure",
        action="store_true",
        help="Stop immediately if a round fails after autofix attempts.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rounds = max(int(args.rounds), 1)
    python_exec = str(args.python)
    LOOP_DIR.mkdir(parents=True, exist_ok=True)

    session: dict[str, object] = {
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "report_dir": str(REPORT_DIR),
        "python_exec": python_exec,
        "rounds_requested": rounds,
        "rounds": [],
    }

    print(f"[loop] report={REPORT_DIR}")
    print(f"[loop] python={python_exec}")
    print(f"[loop] rounds={rounds}")

    overall_ok = True
    for r in range(1, rounds + 1):
        round_start = time.perf_counter()
        round_rec: dict[str, object] = {
            "round": r,
            "started_at_utc": datetime.now(timezone.utc).isoformat(),
            "steps": [],
            "passed": True,
        }
        print(f"\n[round {r}] start")

        for step_name, cmd in build_steps(python_exec):
            log_path = LOOP_DIR / f"round_{r:02d}_{step_name}.log"
            code, dur = run_command(cmd, cwd=REPORT_DIR, log_path=log_path)
            step_rec: dict[str, object] = {
                "name": step_name,
                "cmd": list(cmd),
                "returncode": code,
                "duration_sec": dur,
                "log": str(log_path),
                "autofix_applied": False,
            }

            if code != 0 and step_name in {"build_cn", "build_en"}:
                retry_code, retry_dur, applied = maybe_retry_with_latex_clean(
                    step_name,
                    cmd,
                    report_log_prefix=log_path,
                )
                step_rec["autofix_applied"] = applied
                step_rec["autofix_total_duration_sec"] = retry_dur
                if applied:
                    step_rec["returncode_after_autofix"] = retry_code
                    code = retry_code

            if code != 0:
                round_rec["passed"] = False

            round_rec["steps"].append(step_rec)
            status = "ok" if code == 0 else "fail"
            print(f"[round {r}] {step_name}: {status} ({dur:.2f}s)")

            if code != 0:
                if args.stop_on_failure:
                    print(f"[round {r}] stopping early due to failure at step={step_name}")
                    break
                print(f"[round {r}] continuing after failed step={step_name}")
                break

        round_rec["duration_sec"] = time.perf_counter() - round_start
        session["rounds"].append(round_rec)
        overall_ok = overall_ok and bool(round_rec.get("passed"))

        print(
            f"[round {r}] done: passed={round_rec['passed']}, "
            f"duration={float(round_rec['duration_sec']):.2f}s"
        )

        if not round_rec["passed"] and args.stop_on_failure:
            break

    session["finished_at_utc"] = datetime.now(timezone.utc).isoformat()
    session["passed"] = overall_ok
    summary_path = LOOP_DIR / "summary.json"
    summary_path.write_text(json.dumps(session, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n[loop] summary: {summary_path}")
    print(f"[loop] passed={overall_ok}")
    return 0 if overall_ok else 1


if __name__ == "__main__":
    sys.exit(main())
