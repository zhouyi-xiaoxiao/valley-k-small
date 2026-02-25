#!/usr/bin/env python3
from __future__ import annotations

import argparse
import atexit
import json
import os
import signal
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
SITE_DIR = REPO_ROOT / "site"
DATA_ROOT = SITE_DIR / "public" / "data" / "v1"
ARTIFACTS_DIR = SITE_DIR / "public" / "artifacts"
LOOP_ROOT = REPO_ROOT / "artifacts" / "loop"
CHECKS_DIR = REPO_ROOT / "artifacts" / "checks"
HEARTBEAT_PATH = LOOP_ROOT / "progress" / "heartbeat.json"


@dataclass(frozen=True)
class Profile:
    name: str
    max_assets: int
    max_figures: int
    max_datasets: int
    max_points: int


PROFILES: list[Profile] = [
    Profile("balanced", max_assets=40, max_figures=24, max_datasets=3, max_points=1200),
    Profile("lean", max_assets=28, max_figures=16, max_datasets=2, max_points=800),
    Profile("fidelity", max_assets=60, max_figures=36, max_datasets=4, max_points=1600),
    Profile("ultra-lean", max_assets=20, max_figures=12, max_datasets=1, max_points=500),
]


def utc_now() -> datetime:
    return datetime.utcnow()


def utc_now_iso() -> str:
    return utc_now().isoformat() + "Z"


def parse_until(text: str | None) -> datetime | None:
    if not text:
        return None
    s = text.strip().lower()
    if s == "tomorrow":
        now = utc_now()
        tomorrow = (now + timedelta(days=1)).date().isoformat()
        return datetime.fromisoformat(tomorrow + "T23:59:59")
    if s.endswith("z"):
        s = s[:-1]
    return datetime.fromisoformat(s)


def ensure_dirs() -> None:
    for path in [LOOP_ROOT, LOOP_ROOT / "rounds", LOOP_ROOT / "progress", CHECKS_DIR]:
        path.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def append_jsonl(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")


def update_heartbeat(payload: dict[str, Any]) -> None:
    write_json(HEARTBEAT_PATH, payload)


def load_latest() -> dict[str, Any] | None:
    latest = LOOP_ROOT / "progress" / "latest.json"
    if not latest.exists():
        return None
    return json.loads(latest.read_text(encoding="utf-8"))


def dir_size_mb(path: Path) -> float:
    if not path.exists():
        return 0.0
    total = 0
    for p in path.rglob("*"):
        if p.is_file():
            try:
                total += p.stat().st_size
            except OSError:
                pass
    return round(total / (1024 * 1024), 3)


def run_cmd(
    name: str,
    cmd: list[str],
    *,
    round_id: str | None = None,
    profile_name: str | None = None,
    cwd: Path = REPO_ROOT,
    env: dict[str, str] | None = None,
    timeout: int = 1800,
) -> dict[str, Any]:
    start = time.time()
    started_at = utc_now_iso()
    start_event = {
        "event": "agent_start",
        "agent": name,
        "round_id": round_id,
        "profile": profile_name,
        "started_at": started_at,
        "command": cmd,
    }
    print(json.dumps(start_event, ensure_ascii=False), flush=True)
    update_heartbeat(
        {
            "status": "running",
            "phase": "agent",
            "agent": name,
            "round_id": round_id,
            "profile": profile_name,
            "started_at": started_at,
            "updated_at": started_at,
            "command": cmd,
        }
    )
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)
    try:
        proc = subprocess.run(
            cmd,
            cwd=cwd,
            env=merged_env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
            timeout=timeout,
        )
        status = "pass" if proc.returncode == 0 else "fail"
        output = proc.stdout[-25000:]
        rc = proc.returncode
    except subprocess.TimeoutExpired as exc:
        status = "timeout"
        output = (exc.stdout or "")[-25000:]
        rc = 124

    duration_s = round(time.time() - start, 3)
    result = {
        "agent": name,
        "status": status,
        "return_code": rc,
        "duration_s": duration_s,
        "command": cmd,
        "output_tail": output,
    }
    ended_at = utc_now_iso()
    done_event = {
        "event": "agent_done",
        "agent": name,
        "round_id": round_id,
        "profile": profile_name,
        "status": status,
        "duration_s": duration_s,
        "ended_at": ended_at,
    }
    print(json.dumps(done_event, ensure_ascii=False), flush=True)
    update_heartbeat(
        {
            "status": "running",
            "phase": "agent_done",
            "agent": name,
            "round_id": round_id,
            "profile": profile_name,
            "agent_status": status,
            "duration_s": duration_s,
            "updated_at": ended_at,
        }
    )
    return result


def count_reports() -> int:
    index_path = DATA_ROOT / "index.json"
    if not index_path.exists():
        return 0
    payload = json.loads(index_path.read_text(encoding="utf-8"))
    return len(payload.get("reports", []))


def score_round(results: list[dict[str, Any]], metrics: dict[str, float], report_count: int, total_s: float) -> float:
    passed = sum(1 for item in results if item["status"] == "pass")
    all_pass = passed == len(results)
    score = passed * 20.0
    if all_pass:
        score += 25.0
    score += min(35.0, report_count * 2.0)
    score -= metrics.get("site_out_mb", 0.0) * 0.15
    score -= metrics.get("artifacts_mb", 0.0) * 0.06
    score -= total_s / 140.0
    return round(score, 3)


def write_agent_checks(round_id: str, results: list[dict[str, Any]], score: float, profile: Profile) -> None:
    rows = []
    for item in results:
        payload = {
            "agent": item["agent"],
            "status": "pass" if item["status"] == "pass" else "fail",
            "round_id": round_id,
            "generated_at": utc_now_iso(),
            "duration_s": item["duration_s"],
            "return_code": item["return_code"],
            "profile": profile.name,
            "notes": "Loop optimization step.",
        }
        out_name = item["agent"].lower().replace(" ", "-").replace("_", "-")
        write_json(CHECKS_DIR / f"{out_name}.json", payload)
        rows.append(payload)

    cross = {
        "generated_at": utc_now_iso(),
        "round_id": round_id,
        "all_passed": all(r["status"] == "pass" for r in rows),
        "score": score,
        "profile": asdict(profile),
        "agents": rows,
    }
    write_json(CHECKS_DIR / "crosscheck_report.json", cross)


def ensure_site_deps() -> dict[str, Any]:
    node_modules = SITE_DIR / "node_modules"
    if node_modules.exists():
        return {"agent": "Agent-Setup", "status": "pass", "return_code": 0, "duration_s": 0.0, "command": ["skip:npm-install"], "output_tail": "node_modules exists"}
    return run_cmd("Agent-Setup", ["npm", "install"], cwd=SITE_DIR, timeout=3600)


def run_round(round_no: int, profile: Profile, base_path: str, mode: str) -> dict[str, Any]:
    round_id = f"r{round_no:04d}-{utc_now().strftime('%Y%m%dT%H%M%SZ')}"
    started_at = utc_now_iso()
    update_heartbeat(
        {
            "status": "running",
            "phase": "round_start",
            "round_id": round_id,
            "round_no": round_no,
            "profile": profile.name,
            "mode": mode,
            "started_at": started_at,
            "updated_at": started_at,
        }
    )
    print(
        json.dumps(
            {
                "event": "round_start",
                "round_id": round_id,
                "round_no": round_no,
                "profile": profile.name,
                "mode": mode,
                "started_at": started_at,
            },
            ensure_ascii=False,
        ),
        flush=True,
    )

    results: list[dict[str, Any]] = []

    setup_result = ensure_site_deps()
    results.append(setup_result)

    results.append(
        run_cmd(
            "Agent-A-Data",
            [
                sys.executable,
                "scripts/build_web_data.py",
                "--mode",
                mode,
                "--max-assets",
                str(profile.max_assets),
                "--max-figures",
                str(profile.max_figures),
                "--max-datasets",
                str(profile.max_datasets),
                "--max-points",
                str(profile.max_points),
            ],
            round_id=round_id,
            profile_name=profile.name,
        )
    )

    results.append(run_cmd("Agent-B-Sync", [sys.executable, "scripts/build_agent_sync.py"], round_id=round_id, profile_name=profile.name))
    results.append(run_cmd("Agent-C-Validate", [sys.executable, "scripts/validate_web_data.py"], round_id=round_id, profile_name=profile.name))

    with ThreadPoolExecutor(max_workers=2) as executor:
        fut_pytest = executor.submit(
            run_cmd,
            "Agent-D-QA-Tests",
            [sys.executable, "-m", "pytest", "-q", "tests/test_web_payload_pipeline.py"],
            round_id=round_id,
            profile_name=profile.name,
        )
        fut_docs = executor.submit(
            run_cmd,
            "Agent-E-QA-Docs",
            [sys.executable, "scripts/check_docs_paths.py"],
            round_id=round_id,
            profile_name=profile.name,
        )
        results.append(fut_pytest.result())
        results.append(fut_docs.result())

    results.append(
        run_cmd(
            "Agent-F-Frontend-Build",
            ["npm", "run", "build"],
            round_id=round_id,
            profile_name=profile.name,
            cwd=SITE_DIR,
            env={"NEXT_PUBLIC_BASE_PATH": base_path},
            timeout=3600,
        )
    )
    results.append(
        run_cmd(
            "Agent-G-OpenClaw-Review",
            [sys.executable, "scripts/run_openclaw_review.py"],
            round_id=round_id,
            profile_name=profile.name,
            timeout=1800,
        )
    )

    ended_at = utc_now_iso()
    total_s = round(sum(item["duration_s"] for item in results), 3)
    report_count = count_reports()
    metrics = {
        "site_out_mb": dir_size_mb(SITE_DIR / "out"),
        "data_mb": dir_size_mb(DATA_ROOT),
        "artifacts_mb": dir_size_mb(ARTIFACTS_DIR),
    }
    score = score_round(results, metrics, report_count, total_s)

    payload = {
        "round_id": round_id,
        "round_no": round_no,
        "started_at": started_at,
        "ended_at": ended_at,
        "duration_s": total_s,
        "profile": asdict(profile),
        "mode": mode,
        "report_count": report_count,
        "metrics": metrics,
        "score": score,
        "results": results,
    }

    write_json(LOOP_ROOT / "rounds" / f"{round_id}.json", payload)
    append_jsonl(LOOP_ROOT / "progress" / "history.jsonl", payload)
    write_json(LOOP_ROOT / "progress" / "latest.json", payload)

    write_agent_checks(round_id, results, score, profile)

    md = [
        f"# Loop Progress ({round_id})",
        "",
        f"- Started: {started_at}",
        f"- Ended: {ended_at}",
        f"- Profile: {profile.name}",
        f"- Score: {score}",
        f"- Report count: {report_count}",
        f"- Metrics: out={metrics['site_out_mb']}MB, data={metrics['data_mb']}MB, artifacts={metrics['artifacts_mb']}MB",
        "",
        "## Agent Results",
    ]
    for item in results:
        md.append(f"- {item['agent']}: {item['status']} ({item['duration_s']}s)")
    (LOOP_ROOT / "progress" / "latest.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    best_path = LOOP_ROOT / "progress" / "best_config.json"
    best = None
    if best_path.exists():
        best = json.loads(best_path.read_text(encoding="utf-8"))
    if not best or score >= float(best.get("score", -1e9)):
        write_json(
            best_path,
            {
                "updated_at": ended_at,
                "score": score,
                "round_id": round_id,
                "profile": asdict(profile),
                "metrics": metrics,
            },
        )

    print(
        json.dumps(
            {
                "event": "round_done",
                "round_id": round_id,
                "round_no": round_no,
                "profile": profile.name,
                "score": score,
                "ended_at": ended_at,
            },
            ensure_ascii=False,
        ),
        flush=True,
    )
    update_heartbeat(
        {
            "status": "idle",
            "phase": "round_done",
            "round_id": round_id,
            "round_no": round_no,
            "profile": profile.name,
            "score": score,
            "ended_at": ended_at,
            "updated_at": ended_at,
        }
    )

    return payload


def save_pid(pid_file: Path) -> None:
    pid_file.parent.mkdir(parents=True, exist_ok=True)
    pid_file.write_text(str(os.getpid()), encoding="utf-8")

    def _cleanup() -> None:
        if pid_file.exists():
            try:
                pid_file.unlink()
            except OSError:
                pass

    atexit.register(_cleanup)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run continuous multi-agent web optimization loop.")
    parser.add_argument("--interval-seconds", type=int, default=900)
    parser.add_argument("--max-rounds", type=int, default=0, help="0 means unlimited")
    parser.add_argument("--until", default="tomorrow", help="ISO UTC or 'tomorrow' (UTC 23:59:59)")
    parser.add_argument("--base-path", default="/valley-k-small")
    parser.add_argument("--mode", choices=["changed", "full"], default="changed")
    parser.add_argument("--pid-file", type=Path, default=LOOP_ROOT / "daemon.pid")
    parser.add_argument("--once", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    ensure_dirs()
    save_pid(args.pid_file)

    until_dt = parse_until(args.until)
    interval = max(30, int(args.interval_seconds))
    max_rounds = max(0, int(args.max_rounds))

    latest = load_latest()
    round_no = int(latest["round_no"]) if latest and "round_no" in latest else 0

    print(
        json.dumps(
            {
                "ok": True,
                "started_at": utc_now_iso(),
                "interval_seconds": interval,
                "until": until_dt.isoformat() + "Z" if until_dt else None,
                "max_rounds": max_rounds,
                "base_path": args.base_path,
                "mode": args.mode,
                "pid": os.getpid(),
                "pid_file": str(args.pid_file),
            },
            ensure_ascii=False,
            indent=2,
        )
    )

    should_stop = False

    def _handle_signal(signum: int, _frame: Any) -> None:
        nonlocal should_stop
        should_stop = True

    signal.signal(signal.SIGINT, _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)

    rounds_this_run = 0

    while not should_stop:
        now = utc_now()
        if until_dt and now >= until_dt:
            break

        round_no += 1
        rounds_this_run += 1
        profile = PROFILES[(round_no - 1) % len(PROFILES)]

        try:
            run_payload = run_round(round_no, profile, args.base_path, args.mode)
            print(
                json.dumps(
                    {
                        "round_id": run_payload["round_id"],
                        "score": run_payload["score"],
                        "report_count": run_payload["report_count"],
                        "metrics": run_payload["metrics"],
                    },
                    ensure_ascii=False,
                )
            )
        except Exception as exc:  # pragma: no cover
            err_payload = {
                "round_no": round_no,
                "timestamp": utc_now_iso(),
                "error": str(exc),
            }
            write_json(LOOP_ROOT / "progress" / "latest-error.json", err_payload)
            append_jsonl(LOOP_ROOT / "progress" / "errors.jsonl", err_payload)
            update_heartbeat(
                {
                    "status": "error",
                    "phase": "round_exception",
                    "round_no": round_no,
                    "error": str(exc),
                    "updated_at": utc_now_iso(),
                }
            )

        if args.once:
            break
        if max_rounds and rounds_this_run >= max_rounds:
            break

        slept = 0
        while slept < interval and not should_stop:
            if until_dt and utc_now() >= until_dt:
                should_stop = True
                break
            time.sleep(min(5, interval - slept))
            slept += min(5, interval - slept)

    print(
        json.dumps(
            {
                "ok": True,
                "stopped_at": utc_now_iso(),
                "rounds_completed_total": round_no,
                "rounds_completed_this_run": rounds_this_run,
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
