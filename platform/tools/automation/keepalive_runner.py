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
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]
KEEPALIVE_ROOT = REPO_ROOT / ".local" / "keepalive"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def append_jsonl(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def is_pid_running(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def run_command(cmd: str, workdir: Path, timeout_seconds: int) -> dict[str, Any]:
    started_at = utc_now_iso()
    t0 = time.time()
    try:
        proc = subprocess.run(
            ["/bin/zsh", "-lc", cmd],
            cwd=workdir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
            timeout=timeout_seconds,
        )
        status = "pass" if proc.returncode == 0 else "fail"
        return_code = int(proc.returncode)
        output_tail = (proc.stdout or "")[-25000:]
    except subprocess.TimeoutExpired as exc:
        status = "timeout"
        return_code = 124
        output_tail = ((exc.stdout or "") + "\n[TIMEOUT] keepalive command exceeded timeout.")[-25000:]

    ended_at = utc_now_iso()
    return {
        "status": status,
        "return_code": return_code,
        "started_at": started_at,
        "ended_at": ended_at,
        "duration_s": round(time.time() - t0, 3),
        "command": cmd,
        "workdir": str(workdir),
        "output_tail": output_tail,
    }


def sleep_with_interrupt(total_seconds: int, should_stop: callable) -> None:
    slept = 0
    total = max(0, int(total_seconds))
    while slept < total and not should_stop():
        remaining = total - slept
        chunk = min(1, remaining)
        time.sleep(chunk)
        slept += chunk


def backoff_seconds(interval_seconds: int, consecutive_failures: int) -> int:
    if consecutive_failures <= 0:
        return max(1, int(interval_seconds))
    k = min(3, int(consecutive_failures))
    candidate = int(interval_seconds) * (2**k)
    return max(1, min(3600, candidate))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run keepalive loop for a single job config.")
    parser.add_argument("--job-config", type=Path, required=True)
    parser.add_argument("--once", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.job_config.exists():
        print(f"job config not found: {args.job_config}", file=sys.stderr)
        return 2

    payload = read_json(args.job_config)
    name = str(payload.get("name", "")).strip()
    cmd = str(payload.get("cmd", "")).strip()
    label = str(payload.get("label", "")).strip()
    interval_seconds = int(payload.get("interval_seconds", 900))
    timeout_seconds = int(payload.get("timeout_seconds", 5400))
    workdir = Path(str(payload.get("workdir", REPO_ROOT))).expanduser()
    if not name or not cmd:
        print("job config missing required fields: name/cmd", file=sys.stderr)
        return 2

    paths_obj = payload.get("paths", {})
    run_dir = Path(str(paths_obj.get("run_dir", KEEPALIVE_ROOT / "runs" / name))).expanduser()
    heartbeat_path = Path(str(paths_obj.get("heartbeat", run_dir / "heartbeat.json"))).expanduser()
    latest_path = Path(str(paths_obj.get("latest", run_dir / "latest.json"))).expanduser()
    history_path = Path(str(paths_obj.get("history", run_dir / "history.jsonl"))).expanduser()
    errors_path = Path(str(paths_obj.get("errors", run_dir / "errors.jsonl"))).expanduser()
    pid_path = Path(str(paths_obj.get("pid", run_dir / "runner.pid"))).expanduser()

    run_dir.mkdir(parents=True, exist_ok=True)
    try:
        workdir = workdir.resolve()
    except FileNotFoundError:
        workdir.mkdir(parents=True, exist_ok=True)
        workdir = workdir.resolve()

    if pid_path.exists():
        raw = pid_path.read_text(encoding="utf-8").strip()
        if raw.isdigit():
            old_pid = int(raw)
            if old_pid != os.getpid() and is_pid_running(old_pid):
                print(
                    json.dumps(
                        {
                            "event": "runner_exit",
                            "reason": "another_runner_active",
                            "name": name,
                            "label": label,
                            "pid": old_pid,
                        },
                        ensure_ascii=False,
                    )
                )
                return 0

    pid_path.parent.mkdir(parents=True, exist_ok=True)
    pid_path.write_text(str(os.getpid()), encoding="utf-8")

    def _cleanup_pid() -> None:
        try:
            if pid_path.exists():
                pid_path.unlink()
        except OSError:
            pass

    atexit.register(_cleanup_pid)

    should_stop = False

    def _handle_signal(_signum: int, _frame: Any) -> None:
        nonlocal should_stop
        should_stop = True

    signal.signal(signal.SIGINT, _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)

    latest_round = 0
    if latest_path.exists():
        try:
            latest_round = int(read_json(latest_path).get("round", 0))
        except (ValueError, json.JSONDecodeError):
            latest_round = 0

    consecutive_failures = 0
    started_at = utc_now_iso()
    write_json(
        heartbeat_path,
        {
            "status": "running",
            "phase": "runner_started",
            "name": name,
            "label": label,
            "pid": os.getpid(),
            "started_at": started_at,
            "updated_at": started_at,
        },
    )
    print(
        json.dumps(
            {
                "event": "runner_start",
                "name": name,
                "label": label,
                "pid": os.getpid(),
                "started_at": started_at,
            },
            ensure_ascii=False,
        ),
        flush=True,
    )

    while not should_stop:
        latest_round += 1
        round_started_at = utc_now_iso()
        write_json(
            heartbeat_path,
            {
                "status": "running",
                "phase": "round_start",
                "name": name,
                "label": label,
                "round": latest_round,
                "updated_at": round_started_at,
            },
        )

        result = run_command(cmd, workdir, timeout_seconds)
        result["name"] = name
        result["label"] = label
        result["round"] = latest_round
        result["interval_seconds"] = interval_seconds
        result["timeout_seconds"] = timeout_seconds
        result["runner_pid"] = os.getpid()
        result["recorded_at"] = utc_now_iso()

        write_json(latest_path, result)
        append_jsonl(history_path, result)
        if result["status"] != "pass":
            append_jsonl(errors_path, result)
            consecutive_failures += 1
        else:
            consecutive_failures = 0

        print(
            json.dumps(
                {
                    "event": "round_done",
                    "name": name,
                    "round": latest_round,
                    "status": result["status"],
                    "return_code": result["return_code"],
                    "duration_s": result["duration_s"],
                },
                ensure_ascii=False,
            ),
            flush=True,
        )

        if args.once:
            break

        sleep_seconds = backoff_seconds(interval_seconds, consecutive_failures)
        write_json(
            heartbeat_path,
            {
                "status": "idle",
                "phase": "sleeping",
                "name": name,
                "label": label,
                "round": latest_round,
                "last_status": result["status"],
                "consecutive_failures": consecutive_failures,
                "sleep_seconds": sleep_seconds,
                "updated_at": utc_now_iso(),
            },
        )
        sleep_with_interrupt(sleep_seconds, lambda: should_stop)

    stopped_at = utc_now_iso()
    write_json(
        heartbeat_path,
        {
            "status": "stopped",
            "phase": "runner_stopped",
            "name": name,
            "label": label,
            "round": latest_round,
            "stopped_at": stopped_at,
            "updated_at": stopped_at,
        },
    )
    print(
        json.dumps(
            {"event": "runner_stop", "name": name, "label": label, "stopped_at": stopped_at},
            ensure_ascii=False,
        ),
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
