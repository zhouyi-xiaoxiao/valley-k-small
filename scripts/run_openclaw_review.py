#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
import uuid
import glob
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = REPO_ROOT / "artifacts" / "checks" / "openclaw_review.json"
DEFAULT_HISTORY = REPO_ROOT / "artifacts" / "checks" / "openclaw_review_history.jsonl"


def utc_now_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat().replace("+00:00", "Z")


def run(cmd: list[str], *, cwd: Path = REPO_ROOT, timeout: int = 900) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
        timeout=timeout,
    )


def parse_json_maybe(text: str) -> dict[str, Any] | None:
    text = text.strip()
    if not text:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if not match:
        return None
    candidate = match.group(0)
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        return None


def ensure_agent(agent_id: str, workspace: Path, model: str) -> tuple[bool, str]:
    listed = run(["openclaw", "agents", "list", "--json"], timeout=120)
    if listed.returncode != 0:
        return False, listed.stdout
    payload = parse_json_maybe(listed.stdout) or []
    existing = next((item for item in payload if item.get("id") == agent_id), None)
    if existing and existing.get("model") == model:
        return True, "agent exists"
    if existing:
        deleted = run(["openclaw", "agents", "delete", agent_id, "--force", "--json"], timeout=120)
        if deleted.returncode != 0:
            return False, deleted.stdout
    added = run(
        [
            "openclaw",
            "agents",
            "add",
            agent_id,
            "--workspace",
            str(workspace),
            "--model",
            model,
            "--non-interactive",
            "--json",
        ],
        timeout=180,
    )
    if added.returncode != 0:
        return False, added.stdout
    return True, "agent created"


def select_models(candidates: list[str]) -> list[str]:
    listed = run(["openclaw", "models", "list", "--all", "--plain"], timeout=120)
    if listed.returncode != 0:
        return candidates
    available = {line.strip() for line in listed.stdout.splitlines() if line.strip()}
    resolved = [model for model in candidates if model in available]
    return resolved or candidates


def build_local_snapshot(repo_root: Path) -> dict[str, Any]:
    snapshot: dict[str, Any] = {}
    theory_map_path = repo_root / "site" / "public" / "data" / "v1" / "theory_map.json"
    if theory_map_path.exists():
        try:
            theory_map = json.loads(theory_map_path.read_text(encoding="utf-8"))
            checks = {str(item.get("check", "")): bool(item.get("pass")) for item in theory_map.get("consistency_checks", [])}
            snapshot["theory_checks"] = {
                "duplicate_math_signatures": checks.get("duplicate_math_signatures"),
                "asset_label_duplication": checks.get("asset_label_duplication"),
            }
        except json.JSONDecodeError:
            snapshot["theory_checks"] = {"parse_error": True}

    mixed = 0
    total = 0
    for path in glob.glob(str(repo_root / "site" / "public" / "data" / "v1" / "reports" / "*" / "series" / "*.json")):
        try:
            payload = json.loads(Path(path).read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        total += 1
        types = {str(row.get("series_type", "")).strip() for row in payload.get("series", []) if str(row.get("series_type", "")).strip()}
        if len(types) > 1:
            mixed += 1
    snapshot["semantic_payload_homogeneity"] = {"mixed_series_payloads": mixed, "total_series_payloads": total}
    return snapshot


def build_prompt(repo_root: Path, local_snapshot: dict[str, Any]) -> str:
    return (
        "You are a strict QA reviewer for a mathematics-heavy website and publication pipeline. "
        "Review the repository at "
        f"{repo_root.as_posix()} "
        "with focus on content coherence, readability, mathematical continuity, interaction quality, verifiability, and duplication risk. "
        "Cross-check these files first: "
        "site/src/lib/render-pages.tsx, site/src/lib/render-book-pages.tsx, site/src/components/ReportPlotPanel.tsx, "
        "site/public/data/v1/index.json, site/public/data/v1/theory_map.json, "
        "site/public/data/v1/report_network.json, site/public/data/v1/content_map.json, "
        "site/public/data/v1/book/book_manifest.json, site/public/data/v1/book/toc.json, "
        "artifacts/deliverables/publication/valley_k_small_compendium_en.pdf. "
        "Also sample-check at least 5 report metadata files under site/public/data/v1/reports/*/meta.json. "
        "Ground-truth snapshot computed locally (must be respected unless you provide explicit contradictory evidence): "
        f"{json.dumps(local_snapshot, ensure_ascii=False)}. "
        "For each finding, emphasize concrete content-level defects and whether statements are verifiable from evidence paths. "
        "If your claim contradicts the snapshot, set severity='disputed' and provide exact contrary values from files. "
        "Return ONLY compact JSON with keys: "
        "score (0-100), findings (array of {severity, area, issue, evidence, fix}), "
        "quick_wins (array), crosscheck (array). "
        "No markdown."
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run OpenClaw external review for valley-k-small web quality.")
    parser.add_argument("--agent-id", default="vk-review-qa")
    parser.add_argument("--workspace", type=Path, default=REPO_ROOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--history", type=Path, default=DEFAULT_HISTORY)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    model_candidates = [
        "openai/gpt-5.2-pro-extended-thinking",
        "openai/gpt-5.2-pro",
        "openai-codex/gpt-5.3-codex",
        "openai-codex/gpt-5.2",
    ]
    selected_models = select_models(model_candidates)
    local_snapshot = build_local_snapshot(args.workspace)
    prompt = build_prompt(args.workspace, local_snapshot)
    attempt_errors: list[dict[str, str]] = []

    for selected_model in selected_models:
        ok, note = ensure_agent(args.agent_id, args.workspace, selected_model)
        if not ok:
            attempt_errors.append({"model": selected_model, "stage": "ensure_agent", "error": note.strip()[:4000]})
            continue

        session_id = f"oc-review-{uuid.uuid4()}"
        reviewed = run(
            [
                "openclaw",
                "agent",
                "--local",
                "--agent",
                args.agent_id,
                "--session-id",
                session_id,
                "--thinking",
                "high",
                "--timeout",
                "900",
                "--json",
                "--message",
                prompt,
            ],
            timeout=960,
        )
        if reviewed.returncode != 0:
            attempt_errors.append(
                {
                    "model": selected_model,
                    "stage": "review",
                    "error": reviewed.stdout.strip()[:8000],
                }
            )
            continue

        raw = parse_json_maybe(reviewed.stdout) or {}
        text_payload = ""
        if isinstance(raw, dict):
            payloads = raw.get("payloads")
            if isinstance(payloads, list) and payloads:
                first = payloads[0]
                if isinstance(first, dict):
                    text_payload = str(first.get("text", ""))
        parsed_review = parse_json_maybe(text_payload) or {"raw_text": text_payload.strip()}
        review_ok = isinstance(parsed_review, dict) and "score" in parsed_review and "findings" in parsed_review
        if not review_ok:
            attempt_errors.append(
                {
                    "model": selected_model,
                    "stage": "parse",
                    "error": json.dumps(parsed_review, ensure_ascii=False)[:4000],
                }
            )
            continue

        output = {
            "ok": True,
            "generated_at": utc_now_iso(),
            "agent_id": args.agent_id,
            "session_id": session_id,
            "model": selected_model,
            "model_candidates": selected_models,
            "agent_setup_note": note,
            "attempt_errors": attempt_errors,
            "review": parsed_review,
        }
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
        args.history.parent.mkdir(parents=True, exist_ok=True)
        with args.history.open("a", encoding="utf-8") as f:
            f.write(json.dumps(output, ensure_ascii=False) + "\n")
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return 0

    payload = {
        "ok": False,
        "generated_at": utc_now_iso(),
        "agent_id": args.agent_id,
        "model_candidates": selected_models,
        "attempt_errors": attempt_errors,
        "error": "All configured models failed for OpenClaw review.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    args.history.parent.mkdir(parents=True, exist_ok=True)
    with args.history.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
