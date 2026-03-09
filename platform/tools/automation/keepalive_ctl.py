#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import plistlib
import re
import shlex
import signal
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]
KEEPALIVE_ROOT = REPO_ROOT / "artifacts" / "keepalive"
JOB_DIR = KEEPALIVE_ROOT / "jobs"
RUNS_DIR = KEEPALIVE_ROOT / "runs"
LAUNCH_AGENTS_DIR = Path.home() / "Library" / "LaunchAgents"
RUNNER_SCRIPT = REPO_ROOT / "scripts" / "keepalive_runner.py"
PYTHON_BIN = "/usr/bin/python3"
DEFAULT_INTERVAL_SECONDS = 900
DEFAULT_TIMEOUT_SECONDS = 5400
DEFAULT_CODEX_MODEL = "gpt-5.3-codex"
DEFAULT_CODEX_REASONING_EFFORT = "xhigh"
CODEX_REASONING_EFFORT_CHOICES = ("low", "medium", "high", "xhigh")
TASK_PROFILE_DEFAULTS: dict[str, tuple[int, int]] = {
    "optimize": (900, 5400),
    "review": (1800, 3600),
    "build": (1200, 7200),
    "monitor": (300, 1200),
}
TASK_PROFILE_KEYWORDS: dict[str, tuple[str, ...]] = {
    "review": ("review", "审查", "评审", "code review", "审阅", "检查代码"),
    "build": ("build", "构建", "编译", "发布", "pdf", "site", "web"),
    "monitor": ("monitor", "监控", "巡检", "health", "状态", "heartbeat"),
}
TASK_PROFILE_PROMPTS: dict[str, str] = {
    "optimize": "持续优化当前项目，自动执行并修复失败，不要停；按任务规模与时长按需使用 isambard-automation。",
    "review": "持续执行代码审查与风险检查，输出高优先级问题并给出修复建议。",
    "build": "持续执行构建与回归验证，发现失败时自动定位并修复构建阻塞。",
    "monitor": "持续巡检项目健康状态与关键检查项，发现异常立即给出可执行修复步骤。",
}

ISAMBARD_ROUTING_GUIDANCE = """
执行策略（按情况使用 isambard-automation）：
1) 若任务包含大规模参数扫描、批量并行作业、或预计本地单轮运行 >20 分钟，优先使用 isambard-automation：
   - 先做 isbard doctor/auth；
   - 再用 isbard submit/status/fetch 运行并回收结果。
2) 若任务是小规模快速验证（通常 <10 分钟），优先本地直接执行，减少远端切换开销。
3) 若远端失败（认证/配额/队列/网络），记录失败原因并自动回退到最小本地 smoke 验证，再决定是否重试远端。
4) 任何远端执行结果都要在总结中报告 JOB_ID、REMOTE_DIR、关键产物路径与下一步动作。
""".strip()


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def ensure_dirs() -> None:
    for path in [KEEPALIVE_ROOT, JOB_DIR, RUNS_DIR, LAUNCH_AGENTS_DIR]:
        path.mkdir(parents=True, exist_ok=True)


def validate_job_name(name: str) -> str:
    text = name.strip()
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", text):
        raise ValueError("name must match [A-Za-z0-9][A-Za-z0-9._-]*")
    return text


def label_for_job(name: str) -> str:
    return f"io.valleyksmall.keepalive.{name}"


def plist_path(label: str) -> Path:
    return LAUNCH_AGENTS_DIR / f"{label}.plist"


def job_config_path(name: str) -> Path:
    return JOB_DIR / f"{name}.json"


def run_paths(name: str) -> dict[str, str]:
    run_dir = (RUNS_DIR / name).resolve()
    return {
        "run_dir": str(run_dir),
        "heartbeat": str(run_dir / "heartbeat.json"),
        "latest": str(run_dir / "latest.json"),
        "history": str(run_dir / "history.jsonl"),
        "errors": str(run_dir / "errors.jsonl"),
        "pid": str(run_dir / "runner.pid"),
        "stdout_log": str(run_dir / "stdout.log"),
        "stderr_log": str(run_dir / "stderr.log"),
    }


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_existing_job(name: str) -> dict[str, Any] | None:
    path = job_config_path(name)
    if not path.exists():
        return None
    return read_json(path)


def save_job_config(
    *,
    name: str,
    cmd: str,
    interval_seconds: int,
    timeout_seconds: int,
    workdir: Path,
) -> tuple[Path, dict[str, Any]]:
    now = utc_now_iso()
    config_path = job_config_path(name)
    existing = load_existing_job(name) or {}
    paths_obj = {
        **run_paths(name),
        "job_config": str(config_path.resolve()),
    }
    run_dir = Path(paths_obj["run_dir"])
    run_dir.mkdir(parents=True, exist_ok=True)

    payload = {
        "name": name,
        "cmd": cmd,
        "interval_seconds": max(1, int(interval_seconds)),
        "timeout_seconds": max(1, int(timeout_seconds)),
        "workdir": str(workdir),
        "created_at": existing.get("created_at", now),
        "updated_at": now,
        "label": label_for_job(name),
        "paths": paths_obj,
    }
    write_json(config_path, payload)
    return config_path, payload


def build_plist_payload(job: dict[str, Any], config_path: Path) -> dict[str, Any]:
    paths_obj = job["paths"]
    env_path = os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin")
    return {
        "Label": job["label"],
        "RunAtLoad": True,
        "KeepAlive": True,
        "WorkingDirectory": str(REPO_ROOT),
        "ProgramArguments": [
            PYTHON_BIN,
            str(RUNNER_SCRIPT),
            "--job-config",
            str(config_path.resolve()),
        ],
        "StandardOutPath": str(paths_obj["stdout_log"]),
        "StandardErrorPath": str(paths_obj["stderr_log"]),
        "EnvironmentVariables": {
            "PATH": env_path,
        },
    }


def write_plist(job: dict[str, Any], config_path: Path) -> Path:
    path = plist_path(job["label"])
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as f:
        plistlib.dump(build_plist_payload(job, config_path), f, sort_keys=False)
    return path


def launchd_target(label: str) -> str:
    return f"gui/{os.getuid()}/{label}"


def run_launchctl(args: list[str], check: bool = False) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(
        ["launchctl", *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if check and proc.returncode != 0:
        err = (proc.stderr or proc.stdout or "").strip()
        raise RuntimeError(f"launchctl {' '.join(args)} failed: {err}")
    return proc


def is_pid_running(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def read_runner_pid(pid_path: Path) -> int | None:
    if not pid_path.exists():
        return None
    raw = pid_path.read_text(encoding="utf-8", errors="replace").strip()
    if not raw.isdigit():
        return None
    return int(raw)


def assert_darwin() -> None:
    if sys.platform != "darwin":
        raise RuntimeError("keepalive launchd mode requires macOS (Darwin).")


def infer_task_profile(task_text: str | None) -> str:
    text = (task_text or "").strip().lower()
    for profile, keywords in TASK_PROFILE_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            return profile
    return "optimize"


def resolve_interval_timeout(
    profile: str, interval_override: int | None, timeout_override: int | None
) -> tuple[int, int]:
    base_interval, base_timeout = TASK_PROFILE_DEFAULTS.get(
        profile, (DEFAULT_INTERVAL_SECONDS, DEFAULT_TIMEOUT_SECONDS)
    )
    interval = int(interval_override) if interval_override is not None else base_interval
    timeout = int(timeout_override) if timeout_override is not None else base_timeout
    return max(1, interval), max(1, timeout)


def build_codex_exec_cmd(
    *,
    cd_path: Path,
    prompt: str,
    model: str | None,
    reasoning_effort: str | None,
    extra_args: list[str],
) -> str:
    resolved_model = str(model or DEFAULT_CODEX_MODEL).strip()
    resolved_effort = str(reasoning_effort or DEFAULT_CODEX_REASONING_EFFORT).strip().lower()
    parts: list[str] = [
        "codex",
        "exec",
        "--dangerously-bypass-approvals-and-sandbox",
        "-C",
        str(cd_path),
    ]
    if resolved_model:
        parts.extend(["-m", resolved_model])
    if resolved_effort:
        parts.extend(["-c", f'model_reasoning_effort="{resolved_effort}"'])
    for item in extra_args:
        trimmed = str(item).strip()
        if trimmed:
            parts.append(trimmed)
    parts.append(prompt)
    return " ".join(shlex.quote(p) for p in parts)


def augment_prompt_for_profile(profile: str, prompt: str) -> str:
    text = str(prompt).strip()
    if profile != "optimize":
        return text
    lowered = text.lower()
    if "isambard-automation" in lowered or "isbard" in lowered:
        return text
    return f"{text}\n\n{ISAMBARD_ROUTING_GUIDANCE}"


def up_job(
    *,
    name: str,
    cmd: str,
    interval_seconds: int,
    timeout_seconds: int,
    workdir: Path,
) -> dict[str, Any]:
    assert_darwin()
    ensure_dirs()
    job_name = validate_job_name(name)
    command = str(cmd).strip()
    if not command:
        raise RuntimeError("--cmd must not be empty")

    workdir.mkdir(parents=True, exist_ok=True)
    config_path, job = save_job_config(
        name=job_name,
        cmd=command,
        interval_seconds=int(interval_seconds),
        timeout_seconds=int(timeout_seconds),
        workdir=workdir,
    )
    plist = write_plist(job, config_path)
    target = launchd_target(job["label"])

    run_launchctl(["bootout", target], check=False)
    run_launchctl(["bootstrap", f"gui/{os.getuid()}", str(plist)], check=True)
    run_launchctl(["kickstart", "-k", target], check=True)

    print(f"up: {job_name}")
    print(f"label: {job['label']}")
    print(f"config: {config_path}")
    print(f"plist: {plist}")
    print(f"target: {target}")
    print(f"interval_seconds: {job['interval_seconds']}")
    print(f"timeout_seconds: {job['timeout_seconds']}")
    print(f"workdir: {job['workdir']}")
    return job


def up_local_job(
    *,
    name: str,
    cmd: str,
    interval_seconds: int,
    timeout_seconds: int,
    workdir: Path,
) -> dict[str, Any]:
    ensure_dirs()
    job_name = validate_job_name(name)
    command = str(cmd).strip()
    if not command:
        raise RuntimeError("--cmd must not be empty")

    workdir.mkdir(parents=True, exist_ok=True)
    config_path, job = save_job_config(
        name=job_name,
        cmd=command,
        interval_seconds=int(interval_seconds),
        timeout_seconds=int(timeout_seconds),
        workdir=workdir,
    )

    paths_obj = job["paths"]
    run_dir = Path(str(paths_obj["run_dir"]))
    run_dir.mkdir(parents=True, exist_ok=True)
    pid_path = Path(str(paths_obj["pid"]))
    existing_pid = read_runner_pid(pid_path)
    if existing_pid and is_pid_running(existing_pid):
        print(f"up-local: {job_name} already running (pid={existing_pid})")
        print(f"config: {config_path}")
        print(f"manual_log: {run_dir / 'manual_runner.log'}")
        return job

    manual_log = run_dir / "manual_runner.log"
    env = dict(os.environ)
    env.setdefault("PATH", os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"))
    with manual_log.open("a", encoding="utf-8") as logf:
        proc = subprocess.Popen(
            [PYTHON_BIN, str(RUNNER_SCRIPT), "--job-config", str(config_path.resolve())],
            cwd=REPO_ROOT,
            stdout=logf,
            stderr=subprocess.STDOUT,
            start_new_session=True,
            close_fds=True,
            env=env,
        )

    print(f"up-local: {job_name}")
    print(f"label: {job['label']}")
    print(f"config: {config_path}")
    print(f"manual_pid: {proc.pid}")
    print(f"manual_log: {manual_log}")
    print(f"interval_seconds: {job['interval_seconds']}")
    print(f"timeout_seconds: {job['timeout_seconds']}")
    print(f"workdir: {job['workdir']}")
    return job


def cmd_up(args: argparse.Namespace) -> int:
    workdir = Path(args.workdir).expanduser().resolve() if args.workdir else REPO_ROOT.resolve()
    up_job(
        name=args.name,
        cmd=args.cmd,
        interval_seconds=int(args.interval_seconds),
        timeout_seconds=int(args.timeout_seconds),
        workdir=workdir,
    )
    return 0


def cmd_up_local(args: argparse.Namespace) -> int:
    workdir = Path(args.workdir).expanduser().resolve() if args.workdir else REPO_ROOT.resolve()
    up_local_job(
        name=args.name,
        cmd=args.cmd,
        interval_seconds=int(args.interval_seconds),
        timeout_seconds=int(args.timeout_seconds),
        workdir=workdir,
    )
    return 0


def cmd_up_codex(args: argparse.Namespace) -> int:
    profile = str(args.task_type).strip() if args.task_type else infer_task_profile(args.task)
    interval_seconds, timeout_seconds = resolve_interval_timeout(
        profile, args.interval_seconds, args.timeout_seconds
    )
    prompt = str(args.prompt or args.task or TASK_PROFILE_PROMPTS.get(profile, "")).strip()
    if not prompt:
        raise RuntimeError("missing prompt: pass --prompt or --task")
    prompt = augment_prompt_for_profile(profile, prompt)

    cd_path = Path(args.cd).expanduser().resolve()
    cd_path.mkdir(parents=True, exist_ok=True)
    workdir = Path(args.workdir).expanduser().resolve() if args.workdir else cd_path
    workdir.mkdir(parents=True, exist_ok=True)
    cmd = build_codex_exec_cmd(
        cd_path=cd_path,
        prompt=prompt,
        model=args.model,
        reasoning_effort=args.reasoning_effort,
        extra_args=list(args.extra_arg or []),
    )

    up_job(
        name=args.name,
        cmd=cmd,
        interval_seconds=interval_seconds,
        timeout_seconds=timeout_seconds,
        workdir=workdir,
    )
    print(f"profile: {profile}")
    print(f"codex_cd: {cd_path}")
    print(f"model: {args.model}")
    print(f"reasoning_effort: {args.reasoning_effort}")
    return 0


def cmd_up_codex_local(args: argparse.Namespace) -> int:
    profile = str(args.task_type).strip() if args.task_type else infer_task_profile(args.task)
    interval_seconds, timeout_seconds = resolve_interval_timeout(
        profile, args.interval_seconds, args.timeout_seconds
    )
    prompt = str(args.prompt or args.task or TASK_PROFILE_PROMPTS.get(profile, "")).strip()
    if not prompt:
        raise RuntimeError("missing prompt: pass --prompt or --task")
    prompt = augment_prompt_for_profile(profile, prompt)

    cd_path = Path(args.cd).expanduser().resolve()
    cd_path.mkdir(parents=True, exist_ok=True)
    workdir = Path(args.workdir).expanduser().resolve() if args.workdir else cd_path
    workdir.mkdir(parents=True, exist_ok=True)
    cmd = build_codex_exec_cmd(
        cd_path=cd_path,
        prompt=prompt,
        model=args.model,
        reasoning_effort=args.reasoning_effort,
        extra_args=list(args.extra_arg or []),
    )

    up_local_job(
        name=args.name,
        cmd=cmd,
        interval_seconds=interval_seconds,
        timeout_seconds=timeout_seconds,
        workdir=workdir,
    )
    print(f"profile: {profile}")
    print(f"codex_cd: {cd_path}")
    print(f"model: {args.model}")
    print(f"reasoning_effort: {args.reasoning_effort}")
    return 0


def cmd_down(args: argparse.Namespace) -> int:
    assert_darwin()
    ensure_dirs()
    name = validate_job_name(args.name)
    cfg = load_existing_job(name)
    label = cfg.get("label", label_for_job(name)) if cfg else label_for_job(name)
    target = launchd_target(label)
    plist = plist_path(label)
    config = job_config_path(name)
    paths_obj = cfg.get("paths", {}) if cfg else run_paths(name)
    pid_path = Path(str(paths_obj.get("pid", RUNS_DIR / name / "runner.pid")))

    proc = run_launchctl(["bootout", target], check=False)
    if proc.returncode == 0:
        print(f"down: stopped {target}")
    else:
        print(f"down: not loaded ({target})")

    local_pid = read_runner_pid(pid_path)
    if local_pid and is_pid_running(local_pid):
        try:
            os.kill(local_pid, signal.SIGTERM)
        except OSError:
            pass
        print(f"down: signaled local runner pid={local_pid}")
    elif local_pid:
        print(f"down: local runner pid stale ({local_pid})")

    if args.purge and pid_path.exists():
        try:
            pid_path.unlink()
        except OSError:
            pass

    if args.purge:
        if plist.exists():
            plist.unlink()
        if config.exists():
            config.unlink()
        print("purge: removed plist + job config")
    return 0


def _tail_file(path: Path, lines: int) -> str:
    if not path.exists():
        return "(missing)"
    data = path.read_text(encoding="utf-8", errors="replace").splitlines()
    chunk = data[-max(1, int(lines)) :]
    return "\n".join(chunk) if chunk else "(empty)"


def cmd_logs(args: argparse.Namespace) -> int:
    ensure_dirs()
    name = validate_job_name(args.name)
    cfg = load_existing_job(name)
    paths_obj = cfg.get("paths", {}) if cfg else run_paths(name)
    stdout_path = Path(str(paths_obj.get("stdout_log", RUNS_DIR / name / "stdout.log")))
    stderr_path = Path(str(paths_obj.get("stderr_log", RUNS_DIR / name / "stderr.log")))
    line_count = max(1, int(args.tail))

    print(f"== stdout ({stdout_path}) ==")
    print(_tail_file(stdout_path, line_count))
    print()
    print(f"== stderr ({stderr_path}) ==")
    print(_tail_file(stderr_path, line_count))
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    ensure_dirs()
    name = validate_job_name(args.name)
    cfg = load_existing_job(name)
    label = cfg.get("label", label_for_job(name)) if cfg else label_for_job(name)
    target = launchd_target(label)
    paths_obj = cfg.get("paths", {}) if cfg else run_paths(name)
    heartbeat_path = Path(str(paths_obj.get("heartbeat", RUNS_DIR / name / "heartbeat.json")))
    latest_path = Path(str(paths_obj.get("latest", RUNS_DIR / name / "latest.json")))
    stderr_path = Path(str(paths_obj.get("stderr_log", RUNS_DIR / name / "stderr.log")))
    pid_path = Path(str(paths_obj.get("pid", RUNS_DIR / name / "runner.pid")))
    run_dir = Path(str(paths_obj.get("run_dir", RUNS_DIR / name)))
    manual_log = run_dir / "manual_runner.log"

    proc = run_launchctl(["print", target], check=False)
    print(f"name: {name}")
    print(f"label: {label}")
    print(f"target: {target}")
    print(f"launchd_loaded: {'yes' if proc.returncode == 0 else 'no'}")
    local_pid = read_runner_pid(pid_path)
    local_alive = bool(local_pid and is_pid_running(local_pid))
    print(f"local_runner_pid: {local_pid if local_pid else 'none'}")
    print(f"local_runner_alive: {'yes' if local_alive else 'no'}")
    if manual_log.exists():
        print(f"manual_log: {manual_log}")

    if heartbeat_path.exists():
        hb = read_json(heartbeat_path)
        print("heartbeat:")
        print(json.dumps(hb, ensure_ascii=False, indent=2))
    else:
        print(f"heartbeat: missing ({heartbeat_path})")

    if latest_path.exists():
        latest = read_json(latest_path)
        digest = {
            "round": latest.get("round"),
            "status": latest.get("status"),
            "return_code": latest.get("return_code"),
            "started_at": latest.get("started_at"),
            "ended_at": latest.get("ended_at"),
            "duration_s": latest.get("duration_s"),
        }
        print("latest:")
        print(json.dumps(digest, ensure_ascii=False, indent=2))
    else:
        print(f"latest: missing ({latest_path})")

    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout or "").strip()
        if err:
            print("launchctl_print_error:")
            print(err)

    if (not heartbeat_path.exists() or not latest_path.exists()) and stderr_path.exists():
        err_tail = _tail_file(stderr_path, 20)
        if "Operation not permitted" in err_tail:
            print("hint:")
            print(
                "launchd appears to be blocked by macOS file permissions. "
                "Grant Full Disk Access to the Python binary in use, or move the repo out of protected folders "
                "(for example Desktop/Downloads/iCloud-synced Desktop) and recreate the job."
            )
            print("hint_local:")
            print(
                "Use local background mode to bypass launchd for this path: "
                f"./scripts/keepalive up-codex-local --name {name} --task-type optimize --task '持续优化当前项目并自动修复失败，不要停'"
            )
    return 0


def cmd_run_once(args: argparse.Namespace) -> int:
    ensure_dirs()
    name = validate_job_name(args.name)
    cmd = str(args.cmd).strip()
    if not cmd:
        raise RuntimeError("--cmd must not be empty")

    existing = load_existing_job(name) or {}
    interval_seconds = int(existing.get("interval_seconds", DEFAULT_INTERVAL_SECONDS))
    workdir = (
        Path(args.workdir).expanduser().resolve()
        if args.workdir
        else Path(str(existing.get("workdir", REPO_ROOT))).expanduser().resolve()
    )
    workdir.mkdir(parents=True, exist_ok=True)

    config_path, _job = save_job_config(
        name=name,
        cmd=cmd,
        interval_seconds=interval_seconds,
        timeout_seconds=int(args.timeout_seconds),
        workdir=workdir,
    )
    proc = subprocess.run(
        [PYTHON_BIN, str(RUNNER_SCRIPT), "--job-config", str(config_path), "--once"],
        cwd=REPO_ROOT,
        check=False,
    )
    return int(proc.returncode)


def cmd_profiles(args: argparse.Namespace) -> int:
    payload = {
        profile: {
            "interval_seconds": interval,
            "timeout_seconds": timeout,
            "default_prompt": TASK_PROFILE_PROMPTS.get(profile, ""),
            "default_model": DEFAULT_CODEX_MODEL,
            "default_reasoning_effort": DEFAULT_CODEX_REASONING_EFFORT,
        }
        for profile, (interval, timeout) in TASK_PROFILE_DEFAULTS.items()
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        for profile, meta in payload.items():
            print(
                f"{profile}: interval={meta['interval_seconds']} timeout={meta['timeout_seconds']} "
                f"prompt={meta['default_prompt']}"
            )
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Manage macOS launchd keepalive jobs.")
    sub = parser.add_subparsers(dest="subcmd", required=True)

    p_up = sub.add_parser("up", help="Create/update a job and start launchd service")
    p_up.add_argument("--name", required=True)
    p_up.add_argument("--cmd", required=True)
    p_up.add_argument("--interval-seconds", type=int, default=DEFAULT_INTERVAL_SECONDS)
    p_up.add_argument("--timeout-seconds", type=int, default=DEFAULT_TIMEOUT_SECONDS)
    p_up.add_argument("--workdir", default=None)

    p_up_local = sub.add_parser("up-local", help="Create/update a job and start local detached runner")
    p_up_local.add_argument("--name", required=True)
    p_up_local.add_argument("--cmd", required=True)
    p_up_local.add_argument("--interval-seconds", type=int, default=DEFAULT_INTERVAL_SECONDS)
    p_up_local.add_argument("--timeout-seconds", type=int, default=DEFAULT_TIMEOUT_SECONDS)
    p_up_local.add_argument("--workdir", default=None)

    p_up_codex = sub.add_parser(
        "up-codex",
        help="Create/update a Codex recurring job with task-adaptive defaults",
    )
    p_up_codex.add_argument("--name", required=True)
    p_up_codex.add_argument(
        "--task-type",
        choices=sorted(TASK_PROFILE_DEFAULTS.keys()),
        default=None,
    )
    p_up_codex.add_argument("--task", default="", help="Task text used for profile inference/default prompt")
    p_up_codex.add_argument("--prompt", default=None, help="Explicit Codex prompt")
    p_up_codex.add_argument("--cd", default=str(REPO_ROOT), help="Workspace path passed to codex -C")
    p_up_codex.add_argument("--interval-seconds", type=int, default=None)
    p_up_codex.add_argument("--timeout-seconds", type=int, default=None)
    p_up_codex.add_argument("--model", default=DEFAULT_CODEX_MODEL)
    p_up_codex.add_argument(
        "--reasoning-effort",
        choices=CODEX_REASONING_EFFORT_CHOICES,
        default=DEFAULT_CODEX_REASONING_EFFORT,
    )
    p_up_codex.add_argument(
        "--extra-arg",
        action="append",
        default=[],
        help="Extra single argument appended to codex exec (repeatable)",
    )
    p_up_codex.add_argument("--workdir", default=None)

    p_up_codex_local = sub.add_parser(
        "up-codex-local",
        help="Create/update a Codex recurring job and run it via local detached runner",
    )
    p_up_codex_local.add_argument("--name", required=True)
    p_up_codex_local.add_argument(
        "--task-type",
        choices=sorted(TASK_PROFILE_DEFAULTS.keys()),
        default=None,
    )
    p_up_codex_local.add_argument("--task", default="", help="Task text used for profile inference/default prompt")
    p_up_codex_local.add_argument("--prompt", default=None, help="Explicit Codex prompt")
    p_up_codex_local.add_argument("--cd", default=str(REPO_ROOT), help="Workspace path passed to codex -C")
    p_up_codex_local.add_argument("--interval-seconds", type=int, default=None)
    p_up_codex_local.add_argument("--timeout-seconds", type=int, default=None)
    p_up_codex_local.add_argument("--model", default=DEFAULT_CODEX_MODEL)
    p_up_codex_local.add_argument(
        "--reasoning-effort",
        choices=CODEX_REASONING_EFFORT_CHOICES,
        default=DEFAULT_CODEX_REASONING_EFFORT,
    )
    p_up_codex_local.add_argument(
        "--extra-arg",
        action="append",
        default=[],
        help="Extra single argument appended to codex exec (repeatable)",
    )
    p_up_codex_local.add_argument("--workdir", default=None)

    p_down = sub.add_parser("down", help="Stop launchd service for a job")
    p_down.add_argument("--name", required=True)
    p_down.add_argument("--purge", action="store_true")

    p_status = sub.add_parser("status", help="Show launchd + heartbeat + latest status")
    p_status.add_argument("--name", required=True)

    p_logs = sub.add_parser("logs", help="Tail stdout/stderr logs for a job")
    p_logs.add_argument("--name", required=True)
    p_logs.add_argument("--tail", type=int, default=200)

    p_once = sub.add_parser("run-once", help="Run exactly one round without launchd")
    p_once.add_argument("--name", required=True)
    p_once.add_argument("--cmd", required=True)
    p_once.add_argument("--timeout-seconds", type=int, default=DEFAULT_TIMEOUT_SECONDS)
    p_once.add_argument("--workdir", default=None)

    p_profiles = sub.add_parser("profiles", help="Show task-adaptive keepalive profile defaults")
    p_profiles.add_argument("--json", action="store_true")

    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        if args.subcmd == "up":
            return cmd_up(args)
        if args.subcmd == "up-local":
            return cmd_up_local(args)
        if args.subcmd == "up-codex":
            return cmd_up_codex(args)
        if args.subcmd == "up-codex-local":
            return cmd_up_codex_local(args)
        if args.subcmd == "down":
            return cmd_down(args)
        if args.subcmd == "status":
            return cmd_status(args)
        if args.subcmd == "logs":
            return cmd_logs(args)
        if args.subcmd == "run-once":
            return cmd_run_once(args)
        if args.subcmd == "profiles":
            return cmd_profiles(args)
        raise RuntimeError(f"unsupported subcommand: {args.subcmd}")
    except Exception as exc:
        print(f"[keepalive] error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
