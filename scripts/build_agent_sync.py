#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_ROOT = REPO_ROOT / "site" / "public" / "data" / "v1"
DEFAULT_CHECKS_DIR = REPO_ROOT / "artifacts" / "checks"


def utc_now_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat().replace("+00:00", "Z")


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = "\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n"
    path.write_text(text, encoding="utf-8")
    return text


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build /data/v1/agent machine-readable outputs.")
    parser.add_argument("--data-root", type=Path, default=DEFAULT_DATA_ROOT)
    parser.add_argument("--checks-dir", type=Path, default=DEFAULT_CHECKS_DIR)
    return parser.parse_args()


def ensure_required(path: Path) -> Path:
    if not path.exists():
        raise SystemExit(f"Missing required file: {path}")
    return path


def build_claim_graph_rows(content_map: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for claim in content_map.get("claims", []):
        evidence_paths = [str(ev.get("path", "")).strip() for ev in claim.get("evidence", []) if str(ev.get("path", "")).strip()]
        rows.append(
            {
                "claim_id": str(claim.get("claim_id", "")),
                "report_id": str(claim.get("report_id", "")),
                "stage": str(claim.get("stage", "finding")),
                "linked_claim_ids": [str(x) for x in claim.get("linked_claim_ids", []) if str(x).strip()],
                "linked_report_ids": [str(x) for x in claim.get("linked_report_ids", []) if str(x).strip()],
                "evidence_paths": evidence_paths,
                "evidence_count": len(evidence_paths),
            }
        )
    return rows


def build_book_chapter_rows(chapter_payloads: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for chapter in chapter_payloads:
        rows.append(
            {
                "chapter_id": str(chapter.get("chapter_id", "")),
                "order": int(chapter.get("order", 0)),
                "title_en": str(chapter.get("title_en", "")),
                "title_cn": str(chapter.get("title_cn", "")),
                "report_ids": [str(item.get("report_id", "")) for item in chapter.get("linked_reports", []) if str(item.get("report_id", "")).strip()],
                "interactive_count": len(chapter.get("interactive_panels", [])),
                "claim_count": len(chapter.get("claim_ledger", [])),
                "theory_chain_count": len(chapter.get("theory_chain", [])),
                "source_paths": [str(x) for x in chapter.get("source_paths", []) if str(x).strip()],
            }
        )
    return rows


def main() -> int:
    args = parse_args()
    data_root: Path = args.data_root
    generated_at = utc_now_iso()

    index_path = ensure_required(data_root / "index.json")
    theory_map_path = ensure_required(data_root / "theory_map.json")
    report_network_path = ensure_required(data_root / "report_network.json")
    content_map_path = ensure_required(data_root / "content_map.json")
    book_manifest_path = ensure_required(data_root / "book" / "book_manifest.json")
    book_backbone_path = ensure_required(data_root / "book" / "backbone.json")
    book_claim_coverage_path = ensure_required(data_root / "book" / "book_claim_coverage.json")
    translation_qc_path = ensure_required(data_root / "agent" / "translation_qc.json")

    index_payload = read_json(index_path)
    theory_map = read_json(theory_map_path)
    content_map = read_json(content_map_path)
    book_manifest = read_json(book_manifest_path)
    book_backbone = read_json(book_backbone_path)
    book_claim_coverage = read_json(book_claim_coverage_path)
    translation_qc = read_json(translation_qc_path)

    reports = list(index_payload.get("reports", []))

    agent_dir = data_root / "agent"
    agent_dir.mkdir(parents=True, exist_ok=True)

    report_records: list[dict[str, Any]] = []
    events: list[dict[str, Any]] = []

    for item in reports:
        report_id = str(item["report_id"])
        report_meta_path = data_root / "reports" / report_id / "meta.json"
        meta = read_json(report_meta_path) if report_meta_path.exists() else {}

        record = {
            "report_id": report_id,
            "group": item.get("group", "misc"),
            "path": item.get("path", ""),
            "languages": item.get("languages", []),
            "updated_at": item.get("updated_at", generated_at),
            "title": meta.get("title", report_id),
            "summary": meta.get("summary", ""),
            "key_findings": meta.get("key_findings", []),
            "narrative": meta.get("narrative", {}),
            "formula_count": len(meta.get("math_blocks", [])),
            "section_count": len(meta.get("section_cards", [])),
            "repro_command_count": len(meta.get("reproducibility_commands", [])),
            "dataset_count": len(meta.get("datasets", [])),
            "asset_count": len(meta.get("assets", [])),
            "dataset_series_ids": [d.get("series_id") for d in meta.get("datasets", []) if d.get("series_id")],
        }
        report_records.append(record)

        events.append(
            {
                "event": "report_synced",
                "report_id": report_id,
                "timestamp": generated_at,
                "dataset_count": record["dataset_count"],
                "asset_count": record["asset_count"],
                "formula_count": record["formula_count"],
            }
        )

    reports_jsonl_path = agent_dir / "reports.jsonl"
    events_jsonl_path = agent_dir / "events.jsonl"
    reports_jsonl = write_jsonl(reports_jsonl_path, report_records)
    events_jsonl = write_jsonl(events_jsonl_path, events)

    chapter_payloads: list[dict[str, Any]] = []
    chapter_dir = data_root / "book" / "chapters"
    for chapter_row in sorted(book_manifest.get("chapters", []), key=lambda row: int(row.get("order", 0))):
        chapter_id = str(chapter_row.get("chapter_id", "")).strip()
        if not chapter_id:
            continue
        path = ensure_required(chapter_dir / f"{chapter_id}.json")
        chapter_payloads.append(read_json(path))

    chapter_rows = build_book_chapter_rows(chapter_payloads)
    claim_graph_rows = build_claim_graph_rows(content_map)

    book_manifest_agent_path = agent_dir / "book_manifest.json"
    write_json(book_manifest_agent_path, book_manifest)
    book_chapters_jsonl_path = agent_dir / "book_chapters.jsonl"
    claim_graph_jsonl_path = agent_dir / "claim_graph.jsonl"
    book_chapters_jsonl = write_jsonl(book_chapters_jsonl_path, chapter_rows)
    claim_graph_jsonl = write_jsonl(claim_graph_jsonl_path, claim_graph_rows)

    manifest = {
        "version": "v1",
        "generated_at": generated_at,
        "report_count": len(report_records),
        "files": {
            "reports_jsonl": "/data/v1/agent/reports.jsonl",
            "events_jsonl": "/data/v1/agent/events.jsonl",
            "book_manifest": "/data/v1/agent/book_manifest.json",
            "book_chapters_jsonl": "/data/v1/agent/book_chapters.jsonl",
            "claim_graph_jsonl": "/data/v1/agent/claim_graph.jsonl",
            "book_claim_coverage": "/data/v1/book/book_claim_coverage.json",
            "translation_qc": "/data/v1/agent/translation_qc.json",
            "theory_map": "/data/v1/theory_map.json",
            "guide_json": "/data/v1/agent/guide.json",
            "report_network": "/data/v1/report_network.json",
            "content_map": "/data/v1/content_map.json",
        },
        "hashes": {
            "reports_jsonl_sha256": sha256_bytes(reports_jsonl.encode("utf-8")),
            "events_jsonl_sha256": sha256_bytes(events_jsonl.encode("utf-8")),
            "book_manifest_sha256": sha256_file(book_manifest_agent_path),
            "book_chapters_jsonl_sha256": sha256_bytes(book_chapters_jsonl.encode("utf-8")),
            "claim_graph_jsonl_sha256": sha256_bytes(claim_graph_jsonl.encode("utf-8")),
            "book_claim_coverage_sha256": sha256_file(book_claim_coverage_path),
            "translation_qc_sha256": sha256_file(translation_qc_path),
            "report_network_sha256": sha256_file(report_network_path),
            "content_map_sha256": sha256_file(content_map_path),
        },
    }
    write_json(agent_dir / "manifest.json", manifest)

    guide_payload = {
        "version": "v1",
        "generated_at": generated_at,
        "entrypoints": manifest["files"],
        "schemas": {
            "manifest": "/schemas/agent_sync_v1.schema.json#/$defs/manifest",
            "report_record": "/schemas/agent_sync_v1.schema.json#/$defs/report_record",
            "event_record": "/schemas/agent_sync_v1.schema.json#/$defs/event_record",
            "book_chapter_record": "/schemas/agent_sync_v1.schema.json#/$defs/book_chapter_record",
            "claim_graph_record": "/schemas/agent_sync_v1.schema.json#/$defs/claim_graph_record",
            "translation_qc": "/schemas/translation_qc_v1.schema.json",
            "book_manifest": "/schemas/book_manifest_v1.schema.json",
            "book_chapter": "/schemas/book_chapter_v1.schema.json",
            "glossary": "/schemas/glossary_v1.schema.json",
            "web_report": "/schemas/web_report.schema.json",
            "theory_map": "/schemas/theory_map_v1.schema.json",
            "content_map": "/schemas/content_map_v1.schema.json",
        },
        "recommended_flow": [
            "Read manifest.json and verify SHA256 values before consuming streams.",
            "Process reports.jsonl for normalized report snapshots and metadata joins.",
            "Load book_manifest.json and book_chapters.jsonl for chapter-first continuity traversal.",
            "Load book/backbone.json as the canonical logic spine before report-level deep dives.",
            "Use claim_graph.jsonl and content_map.json for claim-level evidence graph construction.",
            "Check translation_qc.json before generating language-specific outputs.",
            "Join theory_map.json with report_network.json to traverse cross-report theory links.",
        ],
        "record_contract": {
            "report_identity": ["report_id", "group", "path", "languages", "updated_at"],
            "chapter_identity": ["chapter_id", "order", "title_en", "title_cn", "report_ids"],
            "claim_graph": ["claim_id", "report_id", "stage", "evidence_paths", "linked_report_ids"],
            "book_backbone": ["acts", "chapter_spine", "quality_checks"],
            "book_claim_coverage": [
                "global_claim_count",
                "chapter_claim_count",
                "chapter_native_claim_count",
                "excluded_claim_count",
                "excluded_claim_ids",
            ],
        },
        "book_claim_coverage": {
            "global_claim_count": int(book_claim_coverage.get("global_claim_count", 0)),
            "chapter_claim_count": int(book_claim_coverage.get("chapter_claim_count", 0)),
            "chapter_native_claim_count": int(book_claim_coverage.get("chapter_native_claim_count", 0)),
            "excluded_claim_count": int(book_claim_coverage.get("excluded_claim_count", 0)),
        },
    }
    write_json(agent_dir / "guide.json", guide_payload)

    checks_dir = args.checks_dir
    checks_dir.mkdir(parents=True, exist_ok=True)

    openclaw_path = checks_dir / "openclaw_review.json"
    openclaw_payload: dict[str, Any] = read_json(openclaw_path) if openclaw_path.exists() else {}
    openclaw_score = openclaw_payload.get("review", {}).get("score") if isinstance(openclaw_payload, dict) else None

    chapter_qc = {
        "all_interactive": all(row["interactive_count"] >= 1 for row in chapter_rows),
        "all_claimed": all(row["claim_count"] >= 1 for row in chapter_rows),
        "all_theory": all(row["theory_chain_count"] >= 1 for row in chapter_rows),
        "backbone_spine_covered": len(list(book_backbone.get("chapter_spine", []))) == len(chapter_rows),
    }

    publication_dir = REPO_ROOT / "artifacts" / "deliverables" / "publication"
    publication_ok = (publication_dir / "valley_k_small_compendium_en.pdf").exists() and (
        publication_dir / "valley_k_small_compendium_cn.pdf"
    ).exists()

    per_agent = [
        {
            "id": "agent-A-content-synthesis",
            "agent": "Content Synthesis",
            "status": "pass" if len(chapter_rows) >= 8 else "fail",
            "generated_at": generated_at,
            "notes": f"book chapters={len(chapter_rows)}",
        },
        {
            "id": "agent-B-bilingual-qa",
            "agent": "Bilingual QA",
            "status": "pass" if bool(translation_qc.get("passed")) else "fail",
            "generated_at": generated_at,
            "notes": f"translation_qc.high={translation_qc.get('stats', {}).get('high', 'n/a')}",
        },
        {
            "id": "agent-C-theory-integrity",
            "agent": "Theory Integrity",
            "status": "pass" if len(theory_map.get("cards", [])) > 0 else "fail",
            "generated_at": generated_at,
            "notes": f"theory cards={len(theory_map.get('cards', []))}",
        },
        {
            "id": "agent-D-frontend-book-ux",
            "agent": "Frontend Book UX",
            "status": "pass" if chapter_qc["all_interactive"] else "fail",
            "generated_at": generated_at,
            "notes": f"all_interactive={chapter_qc['all_interactive']}",
        },
        {
            "id": "agent-E-interaction",
            "agent": "Interaction",
            "status": "pass" if chapter_qc["all_theory"] else "fail",
            "generated_at": generated_at,
            "notes": f"all_theory={chapter_qc['all_theory']}",
        },
        {
            "id": "agent-F-publication-sync",
            "agent": "Publication Sync",
            "status": "pass" if publication_ok else "warning",
            "generated_at": generated_at,
            "notes": "publication PDFs found" if publication_ok else "publication PDFs not built in this step",
        },
        {
            "id": "agent-G-agent-handoff",
            "agent": "Agent Handoff",
            "status": "pass" if len(claim_graph_rows) > 0 else "fail",
            "generated_at": generated_at,
            "notes": f"claim_graph rows={len(claim_graph_rows)}",
        },
        {
            "id": "agent-I-backbone-system",
            "agent": "Backbone System",
            "status": "pass" if chapter_qc["backbone_spine_covered"] else "fail",
            "generated_at": generated_at,
            "notes": f"backbone_spine={len(list(book_backbone.get('chapter_spine', [])))}",
        },
        {
            "id": "agent-H-meta-qa",
            "agent": "Meta QA (OpenClaw)",
            "status": "pass" if isinstance(openclaw_score, int) and openclaw_score >= 85 else "warning",
            "generated_at": generated_at,
            "notes": f"openclaw_score={openclaw_score}",
        },
    ]

    for item in per_agent:
        write_json(checks_dir / f"{item['id']}.json", item)

    crosscheck = {
        "generated_at": generated_at,
        "all_passed": all(item["status"] == "pass" for item in per_agent if item["status"] != "warning"),
        "agents": per_agent,
    }
    write_json(checks_dir / "crosscheck_report.json", crosscheck)

    print(
        json.dumps(
            {
                "ok": True,
                "data_root": data_root.as_posix(),
                "agent_manifest": (agent_dir / "manifest.json").as_posix(),
                "report_count": len(report_records),
                "chapter_count": len(chapter_rows),
                "backbone_chapter_count": len(list(book_backbone.get("chapter_spine", []))),
                "claim_graph_count": len(claim_graph_rows),
                "checks_dir": checks_dir.as_posix(),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
