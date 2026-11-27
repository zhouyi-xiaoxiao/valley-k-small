#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_DATA_ROOT = REPO_ROOT / "platform" / "web" / "public" / "data" / "v1"


def utc_now_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def clean_text(text: str, *, max_chars: int = 220) -> str:
    value = re.sub(r"\s+", " ", str(text or "")).strip()
    if len(value) <= max_chars:
        return value
    clipped = value[: max_chars + 1]
    stop = max(clipped.rfind(". "), clipped.rfind("。"), clipped.rfind("; "), clipped.rfind("；"))
    if stop < int(max_chars * 0.45):
        stop = max_chars
    return clipped[:stop].rstrip(" ,;。；") + "…"


def chapter_core_question(chapter: dict[str, Any], lang: str) -> str:
    intro = chapter.get(f"intro_{lang}", [])
    if isinstance(intro, list) and intro:
        return clean_text(str(intro[0]), max_chars=180)
    return clean_text(str(chapter.get(f"summary_{lang}", "")), max_chars=180)


def chapter_transition(chapter: dict[str, Any], chapter_by_id: dict[str, dict[str, Any]], lang: str) -> str:
    # A pointer to the next chapter only. What a chapter takes from the
    # previous one is said once, in the chapter's own guide.
    next_id = chapter.get("next_chapter_id")
    if not next_id:
        return "This is the last chapter." if lang == "en" else "这是最后一章。"
    next_chapter = chapter_by_id.get(str(next_id), {})
    next_title = str(next_chapter.get(f"title_{lang}", next_id))
    if lang == "en":
        return f"Next: {next_title}."
    return f"下一章：《{next_title}》。"


def build_acts(chapters: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_order = {int(ch.get("order", 0)): ch for ch in chapters}

    def pick(*orders: int) -> list[str]:
        return [str(by_order[o]["chapter_id"]) for o in orders if o in by_order]

    return [
        {
            "act_id": "act-foundations",
            "title_en": "Part I: Foundations",
            "title_cn": "第一部分：基础定义",
            "objective_en": "The notation, the first-passage quantities and the baseline assumptions shared by all models.",
            "objective_cn": "各模型共用的记号、首达时间的几个基本量和基线假设。",
            "chapter_ids": pick(0, 1),
        },
        {
            "act_id": "act-families",
            "title_en": "Part II: The lattice and the ring",
            "title_cn": "第二部分：二维格点与环",
            "objective_en": "The two-dimensional lattice and the ring, one at a time, with their formulas and charts.",
            "objective_cn": "逐一讨论二维格点和环模型，给出各自的公式和图。",
            "chapter_ids": pick(2, 3, 4),
        },
        {
            "act_id": "act-synthesis",
            "title_en": "Part III: Cross-model synthesis",
            "title_cn": "第三部分：跨模型综合",
            "objective_en": "Lattice and ring results read together, and how far they hold when the setting changes.",
            "objective_cn": "把二维格点和环的结果放在一起读，并看条件改变时它们是否仍然成立。",
            "chapter_ids": pick(5, 6),
        },
        {
            "act_id": "act-outlook",
            "title_en": "Part IV: Outlook",
            "title_cn": "第四部分：展望",
            "objective_en": "The open questions, not yet written.",
            "objective_cn": "开放问题，尚未写成。",
            "chapter_ids": pick(7),
        },
    ]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build chapterized logical backbone for book-first reading.")
    parser.add_argument("--data-root", type=Path, default=DEFAULT_DATA_ROOT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    data_root: Path = args.data_root

    manifest_path = data_root / "book" / "book_manifest.json"
    chapter_dir = data_root / "book" / "chapters"
    if not manifest_path.exists():
        raise SystemExit(f"Missing manifest: {manifest_path}")

    manifest = read_json(manifest_path)
    chapter_rows = sorted(list(manifest.get("chapters", [])), key=lambda row: int(row.get("order", 0)))
    chapters: list[dict[str, Any]] = []
    for row in chapter_rows:
        chapter_id = str(row.get("chapter_id", "")).strip()
        if not chapter_id:
            continue
        chapter_path = chapter_dir / f"{chapter_id}.json"
        if not chapter_path.exists():
            raise SystemExit(f"Missing chapter payload: {chapter_path}")
        chapters.append(read_json(chapter_path))

    chapter_by_id = {str(ch.get("chapter_id", "")): ch for ch in chapters}
    chapter_spine: list[dict[str, Any]] = []
    for chapter in sorted(chapters, key=lambda row: int(row.get("order", 0))):
        chapter_id = str(chapter.get("chapter_id", ""))
        linked_reports = [str(item.get("report_id", "")).strip() for item in chapter.get("linked_reports", []) if str(item.get("report_id", "")).strip()]
        key_claim_ids = [str(item.get("claim_id", "")).strip() for item in chapter.get("claim_ledger", []) if str(item.get("claim_id", "")).strip()][:8]
        key_formulae = [str(item.get("latex", "")).strip() for item in chapter.get("theory_chain", []) if str(item.get("latex", "")).strip()][:6]
        key_notions = [str(item.get("id", "")).strip() for item in chapter.get("concept_cards", []) if str(item.get("id", "")).strip()][:8]
        prev_id = chapter.get("previous_chapter_id")
        next_id = chapter.get("next_chapter_id")

        chapter_spine.append(
            {
                "chapter_id": chapter_id,
                "order": int(chapter.get("order", 0)),
                "title_en": str(chapter.get("title_en", chapter_id)),
                "title_cn": str(chapter.get("title_cn", chapter_id)),
                "core_question_en": chapter_core_question(chapter, "en"),
                "core_question_cn": chapter_core_question(chapter, "cn"),
                "input_dependencies": [str(prev_id)] if prev_id else [],
                "output_to": [str(next_id)] if next_id else [],
                "key_claim_ids": key_claim_ids,
                "key_formulae": key_formulae,
                "key_notions": key_notions,
                "evidence_report_ids": linked_reports,
                "transition_to_next_en": chapter_transition(chapter, chapter_by_id, "en"),
                "transition_to_next_cn": chapter_transition(chapter, chapter_by_id, "cn"),
                "interactive_count": len(chapter.get("interactive_panels", [])),
                "claim_count": len(chapter.get("claim_ledger", [])),
                "formula_count": len(key_formulae),
            }
        )

    acts = build_acts(chapters)

    checks = [
        {
            "check": "all_chapters_have_claims",
            "pass": all(int(row.get("claim_count", 0)) > 0 for row in chapter_spine),
            "details": {str(row.get("chapter_id", "")): int(row.get("claim_count", 0)) for row in chapter_spine},
        },
        {
            "check": "all_chapters_have_formulae",
            "pass": all(int(row.get("formula_count", 0)) > 0 for row in chapter_spine),
            "details": {str(row.get("chapter_id", "")): int(row.get("formula_count", 0)) for row in chapter_spine},
        },
        {
            "check": "spine_is_connected",
            "pass": all((row.get("order", 0) == 0) or bool(row.get("input_dependencies")) for row in chapter_spine),
            "details": {
                str(row.get("chapter_id", "")): {
                    "input_dependencies": list(row.get("input_dependencies", [])),
                    "output_to": list(row.get("output_to", [])),
                }
                for row in chapter_spine
            },
        },
    ]

    payload = {
        "version": "v1",
        "generated_at": utc_now_iso(),
        "chapter_count": len(chapter_spine),
        "acts": acts,
        "chapter_spine": chapter_spine,
        "quality_checks": checks,
    }

    out_path = data_root / "book" / "backbone.json"
    write_json(out_path, payload)
    print(
        json.dumps(
            {
                "ok": True,
                "output": str(out_path),
                "chapter_count": len(chapter_spine),
                "act_count": len(acts),
                "all_checks_pass": all(bool(row.get("pass")) for row in checks),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
