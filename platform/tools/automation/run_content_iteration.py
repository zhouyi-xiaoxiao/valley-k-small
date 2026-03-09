#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]
PYTHON = sys.executable or "python3"
DATA_ROOT = REPO_ROOT / "platform" / "web" / "public" / "data" / "v1"
OUT_DIR = REPO_ROOT / ".local" / "checks" / "content_iteration"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def run(cmd: list[str], *, cwd: Path = REPO_ROOT, timeout: int = 3600) -> dict[str, Any]:
    try:
        proc = subprocess.run(
            cmd,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
            timeout=timeout,
        )
        output = proc.stdout or ""
        code = int(proc.returncode)
    except subprocess.TimeoutExpired as error:
        output = (error.stdout or "") + "\n[TIMEOUT] content iteration step exceeded timeout."
        code = 124
    return {
        "command": cmd,
        "return_code": code,
        "ok": code == 0,
        "output_tail": output[-16000:],
    }


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def collect_local_metrics() -> dict[str, Any]:
    metrics: dict[str, Any] = {
        "reports": 0,
        "claims": 0,
        "claims_missing_evidence": 0,
        "claims_with_cross_links": 0,
        "en_summary_terminal_ellipsis": 0,
        "placeholder_section_summaries": 0,
    }
    index_path = DATA_ROOT / "index.json"
    if not index_path.exists():
        return metrics
    index = read_json(index_path)
    report_ids = [str(row.get("report_id", "")).strip() for row in index.get("reports", []) if str(row.get("report_id", "")).strip()]
    metrics["reports"] = len(report_ids)

    content_map_path = DATA_ROOT / "content_map.json"
    if content_map_path.exists():
        content_map = read_json(content_map_path)
        claims = list(content_map.get("claims", []))
        metrics["claims"] = len(claims)
        metrics["claims_missing_evidence"] = sum(1 for row in claims if not list(row.get("evidence", [])))
        metrics["claims_with_cross_links"] = sum(1 for row in claims if list(row.get("linked_report_ids", [])))

    for rid in report_ids:
        meta_path = DATA_ROOT / "reports" / rid / "meta.json"
        if not meta_path.exists():
            continue
        meta = read_json(meta_path)
        summary = str(meta.get("summary", "")).strip()
        if summary.endswith("…"):
            metrics["en_summary_terminal_ellipsis"] += 1
        for card in meta.get("section_cards", []):
            summary_card = str(card.get("summary", "")).strip().lower()
            if summary_card.endswith("section summary.") or summary_card.endswith("section summary"):
                metrics["placeholder_section_summaries"] += 1
    return metrics


def parse_openclaw_score() -> int | None:
    path = REPO_ROOT / ".local" / "checks" / "openclaw_review.json"
    if not path.exists():
        return None
    try:
        payload = read_json(path)
        review = payload.get("review", {})
        adjusted = review.get("score_adjusted_by_snapshot")
        if isinstance(adjusted, int):
            return adjusted
        score = review.get("score")
        if isinstance(score, int):
            return score
    except json.JSONDecodeError:
        return None
    return None


def run_round(round_idx: int, *, mode: str, build_site: bool, with_openclaw: bool) -> dict[str, Any]:
    steps: list[dict[str, Any]] = []
    steps.append(run([PYTHON, "platform/tools/web/build_web_data.py", "--mode", mode], timeout=2400))
    steps.append(run([PYTHON, "platform/tools/web/build_glossary.py"], timeout=900))
    steps.append(run([PYTHON, "platform/tools/web/build_book_content.py"], timeout=900))
    steps.append(run([PYTHON, "platform/tools/web/build_book_backbone.py"], timeout=900))
    steps.append(run([PYTHON, "platform/tools/web/validate_bilingual_quality.py"], timeout=900))
    steps.append(run([PYTHON, "platform/tools/web/build_agent_sync.py"], timeout=900))
    steps.append(run([PYTHON, "platform/tools/web/validate_web_data.py"], timeout=900))
    if build_site:
        steps.append(run(["npm", "run", "build"], cwd=REPO_ROOT / "platform" / "web", timeout=2400))
    if with_openclaw:
        steps.append(run([PYTHON, "platform/tools/automation/run_openclaw_review.py"], timeout=2400))

    ok = all(bool(step["ok"]) for step in steps)
    local_metrics = collect_local_metrics()
    openclaw_score = parse_openclaw_score() if with_openclaw else None
    return {
        "round": round_idx,
        "generated_at": utc_now_iso(),
        "mode": mode,
        "ok": ok,
        "steps": steps,
        "openclaw_score": openclaw_score,
        "local_metrics": local_metrics,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run iterative content quality loops for valley-k-small.")
    parser.add_argument("--rounds", type=int, default=3)
    parser.add_argument("--mode", choices=["full", "changed"], default="full")
    parser.add_argument("--build-site", action="store_true")
    parser.add_argument("--skip-openclaw", action="store_true")
    parser.add_argument("--target-score", type=int, default=75)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rounds = max(1, int(args.rounds))
    mode = str(args.mode)
    build_site = bool(args.build_site)
    with_openclaw = not bool(args.skip_openclaw)
    target_score = int(args.target_score)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    history: list[dict[str, Any]] = []
    best_score: int | None = None
    best_round: int | None = None

    for idx in range(1, rounds + 1):
        row = run_round(idx, mode=mode, build_site=build_site, with_openclaw=with_openclaw)
        history.append(row)
        (OUT_DIR / f"round_{idx:02d}.json").write_text(json.dumps(row, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        score = row.get("openclaw_score")
        if isinstance(score, int):
            if best_score is None or score > best_score:
                best_score = score
                best_round = idx

    final_ok = all(bool(row.get("ok")) for row in history)
    latest_metrics = history[-1]["local_metrics"] if history else {}
    summary = {
        "ok": final_ok,
        "generated_at": utc_now_iso(),
        "rounds": rounds,
        "mode": mode,
        "with_openclaw": with_openclaw,
        "target_score": target_score,
        "best_score": best_score,
        "best_round": best_round,
        "latest_metrics": latest_metrics,
        "history_file_count": len(history),
        "round_files": [f"round_{i:02d}.json" for i in range(1, rounds + 1)],
    }
    (OUT_DIR / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with (OUT_DIR / "run_history.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(summary, ensure_ascii=False) + "\n")

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if not final_ok:
        return 1
    if with_openclaw and isinstance(best_score, int) and best_score < target_score:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
