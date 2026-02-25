#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = REPO_ROOT / "site" / "public" / "data" / "v1"
AGENT_DATA_ROOT = DATA_ROOT / "agent"
SCHEMAS_ROOT = REPO_ROOT / "schemas"
CHECKS_ROOT = REPO_ROOT / "artifacts" / "checks"
OUT_ROOT = REPO_ROOT / "artifacts" / "deliverables" / "agent_pack" / "v1"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(1024 * 1024)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def build_report_cards(
    index: dict[str, Any],
    *,
    claims_by_report: dict[str, list[dict[str, Any]]],
    arcs_by_report: dict[str, list[str]],
) -> list[dict[str, Any]]:
    cards: list[dict[str, Any]] = []
    for row in index.get("reports", []):
        rid = row["report_id"]
        report_root = DATA_ROOT / "reports" / rid
        meta_path = report_root / "meta.json"
        if not meta_path.exists():
            meta_path = report_root / "meta.cn.json"
        meta = read_json(meta_path)
        cards.append(
            {
                "report_id": rid,
                "group": row.get("group"),
                "updated_at": row.get("updated_at"),
                "title": meta.get("title"),
                "summary": meta.get("summary"),
                "key_findings": list(meta.get("key_findings", [])),
                "math_story": list(meta.get("math_story", [])),
                "dataset_count": len(meta.get("datasets", [])),
                "asset_count": len(meta.get("assets", [])),
                "claim_count": len(claims_by_report.get(rid, [])),
                "arc_ids": arcs_by_report.get(rid, []),
                "web_url": f"/reports/{rid}",
                "data_urls": {
                    "meta": f"/data/v1/reports/{rid}/meta.json",
                    "figures": f"/data/v1/reports/{rid}/figures.json",
                    "content_map": "/data/v1/content_map.json",
                },
            }
        )
    return cards


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def build_openclaw_tasks() -> tuple[list[dict[str, Any]], dict[str, Any] | None]:
    review_path = CHECKS_ROOT / "openclaw_review.json"
    if not review_path.exists():
        return [], None
    review = read_json(review_path)
    body = review.get("review", {})
    findings = list(body.get("findings", []))
    tasks: list[dict[str, Any]] = []
    for idx, f in enumerate(findings, start=1):
        tasks.append(
            {
                "task_id": f"oc-{idx:03d}",
                "severity": f.get("severity"),
                "area": f.get("area"),
                "issue": f.get("issue"),
                "fix": f.get("fix"),
                "status": "todo",
            }
        )
    return tasks, review


def build_guide_markdown(manifest: dict[str, Any]) -> str:
    lines = [
        "# Valley-K Small Agent Handoff Pack",
        "",
        f"- Generated at: {manifest['generated_at']}",
        f"- Report count: {manifest['report_count']}",
        "",
        "## Entry Files",
        "- `manifest.json` : package-level index and hashes",
        "- `content_map.json` : claim-level narrative arcs + evidence trails",
        "- `report_cards.jsonl` : one normalized report card per report",
        "- `openclaw_tasks.json` : actionable tasks extracted from OpenClaw review",
        "- `schema_refs.json` : schema + hash references",
        "",
        "## Recommended Agent Workflow",
        "1. Read `manifest.json` and validate all hashes.",
        "2. Read `content_map.json` to follow cross-report arcs and claim evidence links.",
        "3. Read `report_cards.jsonl` to locate target report(s) and math logic chain.",
        "4. Follow `openclaw_tasks.json` high severity items first.",
        "5. Regenerate via `python3 scripts/reportctl.py agent-pack` after edits.",
        "",
        "## Non-Temporary Review Trace",
        "OpenClaw review outputs are persisted to `artifacts/checks/openclaw_review.json` and mirrored into this pack.",
    ]
    return "\n".join(lines) + "\n"


def build_agent_pack() -> dict[str, Any]:
    if not (DATA_ROOT / "index.json").exists():
        raise SystemExit("missing web data index; run `python3 scripts/reportctl.py web-data --mode full` first")
    if not (AGENT_DATA_ROOT / "manifest.json").exists():
        raise SystemExit("missing agent sync outputs; run `python3 scripts/reportctl.py agent-sync` first")
    if not (DATA_ROOT / "content_map.json").exists():
        raise SystemExit("missing content map outputs; run `python3 scripts/reportctl.py web-data --mode full` first")

    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    index = read_json(DATA_ROOT / "index.json")
    agent_manifest = read_json(AGENT_DATA_ROOT / "manifest.json")
    theory_map = read_json(DATA_ROOT / "theory_map.json")
    content_map = read_json(DATA_ROOT / "content_map.json")
    claims_by_report: dict[str, list[dict[str, Any]]] = {}
    for claim in content_map.get("claims", []):
        rid = str(claim.get("report_id", "")).strip()
        if not rid:
            continue
        claims_by_report.setdefault(rid, []).append(claim)
    arcs_by_report: dict[str, list[str]] = {}
    for arc in content_map.get("arcs", []):
        arc_id = str(arc.get("arc_id", "")).strip()
        if not arc_id:
            continue
        for rid in arc.get("report_ids", []):
            rid_key = str(rid).strip()
            if not rid_key:
                continue
            arcs_by_report.setdefault(rid_key, []).append(arc_id)

    report_cards = build_report_cards(index, claims_by_report=claims_by_report, arcs_by_report=arcs_by_report)
    openclaw_tasks, openclaw_raw = build_openclaw_tasks()

    report_cards_path = OUT_ROOT / "report_cards.jsonl"
    write_jsonl(report_cards_path, report_cards)
    openclaw_tasks_path = OUT_ROOT / "openclaw_tasks.json"
    write_json(openclaw_tasks_path, {"generated_at": utc_now_iso(), "tasks": openclaw_tasks})

    if openclaw_raw is not None:
        write_json(OUT_ROOT / "openclaw_review.snapshot.json", openclaw_raw)

    schema_refs = {
        "generated_at": utc_now_iso(),
        "schemas": [],
    }
    for s in sorted(SCHEMAS_ROOT.glob("*.json")):
        schema_refs["schemas"].append(
            {
                "name": s.name,
                "path": s.relative_to(REPO_ROOT).as_posix(),
                "sha256": sha256_file(s),
            }
        )
    write_json(OUT_ROOT / "schema_refs.json", schema_refs)

    sync_files = [
        "manifest.json",
        "guide.json",
        "reports.jsonl",
        "events.jsonl",
    ]
    for name in sync_files:
        src = AGENT_DATA_ROOT / name
        dst = OUT_ROOT / "agent_sync" / name
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    shutil.copy2(DATA_ROOT / "content_map.json", OUT_ROOT / "content_map.json")

    summary = {
        "generated_at": utc_now_iso(),
        "report_count": len(report_cards),
        "claim_count": len(content_map.get("claims", [])),
        "theory_card_count": len(theory_map.get("cards", [])),
        "openclaw_task_count": len(openclaw_tasks),
        "agent_manifest_generated_at": agent_manifest.get("generated_at"),
    }
    write_json(OUT_ROOT / "summary.json", summary)

    manifest = {
        "version": "agent-pack-v1",
        "generated_at": utc_now_iso(),
        "report_count": len(report_cards),
        "files": {
            "summary": "summary.json",
            "report_cards": "report_cards.jsonl",
            "openclaw_tasks": "openclaw_tasks.json",
            "schema_refs": "schema_refs.json",
            "content_map": "content_map.json",
            "agent_sync": "agent_sync/",
            "guide": "AGENT_GUIDE.md",
        },
        "hashes": {
            "report_cards_sha256": sha256_file(report_cards_path),
            "openclaw_tasks_sha256": sha256_file(openclaw_tasks_path),
            "content_map_sha256": sha256_file(OUT_ROOT / "content_map.json"),
        },
    }
    write_json(OUT_ROOT / "manifest.json", manifest)
    (OUT_ROOT / "AGENT_GUIDE.md").write_text(build_guide_markdown(manifest), encoding="utf-8")

    history_path = OUT_ROOT / "run_history.jsonl"
    with history_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(summary, ensure_ascii=False) + "\n")

    return {
        "ok": True,
        "output_dir": OUT_ROOT.relative_to(REPO_ROOT).as_posix(),
        "manifest": (OUT_ROOT / "manifest.json").relative_to(REPO_ROOT).as_posix(),
        "report_count": len(report_cards),
        "openclaw_task_count": len(openclaw_tasks),
    }


def parse_args() -> argparse.Namespace:
    return argparse.ArgumentParser(description="Build agent handoff package (v1).").parse_args()


def main() -> int:
    _ = parse_args()
    payload = build_agent_pack()
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
