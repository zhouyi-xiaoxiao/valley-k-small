#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_DATA_ROOT = REPO_ROOT / "site" / "public" / "data" / "v1"


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
    chapter_id = str(chapter.get("chapter_id", ""))
    next_id = chapter.get("next_chapter_id")
    if not next_id:
        return "No downstream chapter; consolidate assumptions, claims, and open questions." if lang == "en" else "无后续章节：请收束假设、结论与开放问题。"
    next_chapter = chapter_by_id.get(str(next_id), {})
    this_title = str(chapter.get(f"title_{lang}", chapter.get("chapter_id", "")))
    next_title = str(next_chapter.get(f"title_{lang}", next_id))
    if chapter_id == "chapter-2-grid2d-family" and str(next_id) == "chapter-3-ring-baseline":
        if lang == "en":
            return clean_text(
                "Bridge note: keep the same hazard/survival diagnostics from Grid2D, then switch geometry to ring so shortcut and lazy parameters can be isolated without boundary-shape confounders."
            )
        return clean_text("桥接说明：延续 Grid2D 的 hazard/survival 诊断，但将几何切换到环模型，以隔离 shortcut 与 lazy 参数并排除边界形状混杂。")
    if chapter_id == "chapter-5-cross-model-synthesis" and str(next_id) == "chapter-6-repro-validation":
        if lang == "en":
            return clean_text(
                "Before any new claims are added, move from synthesis to reproducibility gates and verify command-, schema-, and artifact-level closure."
            )
        return clean_text("在增加新结论前，先从综合解释转入复现门禁，逐项验证命令级、schema 级与产物级闭环。")
    if chapter_id == "chapter-6-repro-validation" and str(next_id) == "chapter-7-outlook":
        if lang == "en":
            return clean_text("Only unresolved items that pass reproducibility constraints should enter the outlook as auditable hypotheses.")
        return clean_text("只有通过复现约束后仍未解决的问题，才应进入展望并作为可审计假设。")
    if lang == "en":
        return clean_text(f"Carry notation and verified claims from {this_title} into {next_title}, then extend mechanism and evidence without resetting assumptions.")
    return clean_text(f"从《{this_title}》延续符号与已核对 claim 进入《{next_title}》，在不重置假设的前提下扩展机制与证据。")


def build_acts(chapters: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_order = {int(ch.get("order", 0)): ch for ch in chapters}

    def pick(*orders: int) -> list[str]:
        return [str(by_order[o]["chapter_id"]) for o in orders if o in by_order]

    return [
        {
            "act_id": "act-foundations",
            "title_en": "Act I: Foundations",
            "title_cn": "第一幕：基础定义",
            "objective_en": "Unify notation, FPT objects, and baseline assumptions before model-specific branches.",
            "objective_cn": "在进入模型分支前先统一符号、FPT 对象与基线假设。",
            "chapter_ids": pick(0, 1),
        },
        {
            "act_id": "act-families",
            "title_en": "Act II: Family Mechanisms",
            "title_cn": "第二幕：模型家族机制",
            "objective_en": "Expand Grid2D and Ring families with derivation-backed interaction checkpoints.",
            "objective_cn": "在 Grid2D 与 Ring 家族中用推导与交互检查点展开机制差异。",
            "chapter_ids": pick(2, 3, 4),
        },
        {
            "act_id": "act-synthesis",
            "title_en": "Act III: Cross-Model Synthesis",
            "title_cn": "第三幕：跨模型综合",
            "objective_en": "Merge claims into a shared explanatory frame and validate reproducibility pathways.",
            "objective_cn": "把各章节 claim 汇入统一解释框架，并验证复现链路。",
            "chapter_ids": pick(5, 6),
        },
        {
            "act_id": "act-outlook",
            "title_en": "Act IV: Outlook",
            "title_cn": "第四幕：展望",
            "objective_en": "Stabilize conclusions, isolate unresolved gaps, and define next-step research questions.",
            "objective_cn": "收束结论、标注未解缺口，并给出下一步研究问题。",
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
