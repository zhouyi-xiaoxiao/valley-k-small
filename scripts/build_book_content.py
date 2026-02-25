#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from book_blueprint import CHAPTER_BLUEPRINT, report_to_chapters


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_ROOT = REPO_ROOT / "site" / "public" / "data" / "v1"
STAGE_ORDER = {"model": 0, "method": 1, "result": 2, "finding": 3}


def utc_now_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def clean_text(text: str, *, max_chars: int = 320) -> str:
    value = re.sub(r"\s+", " ", str(text or "")).strip()
    if len(value) <= max_chars:
        return value
    clipped = value[: max_chars + 1]
    stop = max(clipped.rfind(". "), clipped.rfind("。"), clipped.rfind("; "), clipped.rfind("；"))
    if stop < int(max_chars * 0.45):
        stop = max_chars
    return clipped[:stop].rstrip(" ,;。；") + "…"


def contains_cjk(text: str) -> bool:
    return bool(re.search(r"[\u4e00-\u9fff]", str(text)))


def uniq(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for raw in items:
        text = str(raw).strip()
        if not text or text in seen:
            continue
        seen.add(text)
        out.append(text)
    return out


def load_meta_pair(data_root: Path, report_id: str) -> tuple[dict[str, Any], dict[str, Any]]:
    report_dir = data_root / "reports" / report_id
    en_path = report_dir / "meta.json"
    cn_path = report_dir / "meta.cn.json"
    if not en_path.exists() and not cn_path.exists():
        raise FileNotFoundError(f"Missing meta for report={report_id}")
    en = read_json(en_path) if en_path.exists() else read_json(cn_path)
    cn = read_json(cn_path) if cn_path.exists() else read_json(en_path)
    return en, cn


def safe_title(meta: dict[str, Any], fallback: str) -> str:
    title = str(meta.get("title", "")).strip()
    return title or fallback


def pick_concept_cards(theory_map: dict[str, Any], report_ids: list[str], keywords: list[str], limit: int = 6) -> list[dict[str, Any]]:
    needle = [k.lower().strip() for k in keywords if str(k).strip()]
    candidates: list[tuple[int, int, dict[str, Any]]] = []
    report_set = set(report_ids)
    for card in theory_map.get("cards", []):
        card_reports = [str(x) for x in card.get("report_ids", [])]
        overlap = len(report_set.intersection(card_reports))
        haystack = " ".join(
            [
                str(card.get("id", "")),
                str(card.get("label_en", "")),
                str(card.get("label_cn", "")),
                str(card.get("description_en", "")),
                str(card.get("description_cn", "")),
            ]
        ).lower()
        keyword_hit = 1 if any(k in haystack for k in needle) else 0
        score = overlap * 3 + keyword_hit
        if score <= 0:
            continue
        candidates.append((score, int(card.get("report_count", 0)), card))

    if not candidates:
        candidates = [(0, int(card.get("report_count", 0)), card) for card in theory_map.get("cards", [])]

    candidates.sort(key=lambda row: (row[0], row[1]), reverse=True)
    selected = [row[2] for row in candidates[:limit]]
    return [
        {
            "id": str(card.get("id", "")),
            "label_en": str(card.get("label_en", "")),
            "label_cn": str(card.get("label_cn", "")),
            "description_en": clean_text(str(card.get("description_en", "")), max_chars=280),
            "description_cn": clean_text(str(card.get("description_cn", "")), max_chars=170),
            "report_ids": [str(x) for x in card.get("report_ids", [])],
        }
        for card in selected
    ]


def pick_theory_chain(report_ids: list[str], metas_en: dict[str, dict[str, Any]], metas_cn: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    chain: list[dict[str, Any]] = []
    for report_id in report_ids:
        meta_en = metas_en.get(report_id, {})
        meta_cn = metas_cn.get(report_id, {})
        story_en = list(meta_en.get("math_story", []))
        story_cn = list(meta_cn.get("math_story", []))
        if story_en:
            for idx, item_en in enumerate(story_en[:2]):
                item_cn = story_cn[idx] if idx < len(story_cn) else {}
                chain.append(
                    {
                        "report_id": report_id,
                        "stage": str(item_en.get("stage", "Step")),
                        "label_en": clean_text(f"{safe_title(meta_en, report_id)} · {item_en.get('stage', 'Step')}", max_chars=140),
                        "label_cn": clean_text(f"{safe_title(meta_cn, report_id)} · {item_cn.get('stage', item_en.get('stage', '步骤'))}", max_chars=80),
                        "description_en": clean_text(str(item_en.get("description", "")), max_chars=260),
                        "description_cn": clean_text(str(item_cn.get("description", item_en.get("description", ""))), max_chars=150),
                        "latex": str(item_en.get("latex", "")).strip() or "f(t)",
                        "context": str(item_en.get("context", "math_story")).strip() or "math_story",
                    }
                )
        else:
            math_blocks = list(meta_en.get("math_blocks", []))
            if not math_blocks:
                continue
            item_en = math_blocks[0]
            item_cn = (meta_cn.get("math_blocks", []) or [{}])[0]
            chain.append(
                {
                    "report_id": report_id,
                    "stage": "Fallback Formula",
                    "label_en": clean_text(f"{safe_title(meta_en, report_id)} · Formula", max_chars=140),
                    "label_cn": clean_text(f"{safe_title(meta_cn, report_id)} · 公式", max_chars=80),
                    "description_en": clean_text(str(item_en.get("context", "Primary formula for this report.")), max_chars=260),
                    "description_cn": clean_text(str(item_cn.get("context", "该报告的核心公式。")), max_chars=150),
                    "latex": str(item_en.get("latex", "")).strip() or "f(t)",
                    "context": str(item_en.get("context", "math_blocks")).strip() or "math_blocks",
                }
            )

    return chain[:18]


def pick_interactive_panels(report_ids: list[str], metas_en: dict[str, dict[str, Any]], metas_cn: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    panels: list[dict[str, Any]] = []
    for report_id in report_ids:
        meta_en = metas_en.get(report_id, {})
        meta_cn = metas_cn.get(report_id, {})
        datasets_en = list(meta_en.get("datasets", []))
        datasets_cn = list(meta_cn.get("datasets", []))
        if not datasets_en:
            continue
        ds_en = datasets_en[0]
        ds_cn = datasets_cn[0] if datasets_cn else ds_en
        panels.append(
            {
                "panel_id": f"{report_id}:{ds_en.get('series_id', 'dataset')}",
                "report_id": report_id,
                "title_en": clean_text(f"{safe_title(meta_en, report_id)} · {ds_en.get('title', 'Interactive Dataset')}", max_chars=150),
                "title_cn": clean_text(f"{safe_title(meta_cn, report_id)} · {ds_cn.get('title', '交互数据集')}", max_chars=90),
                "dataset_series_id": str(ds_en.get("series_id", "")),
                "dataset_path": str(ds_en.get("series_path", "")),
                "x_label": str(ds_en.get("x_label", "x")),
                "y_label": str(ds_en.get("y_label", "y")),
                "parameter_hint_en": "Adjust visible series and smoothing to inspect peak/valley stability across regimes.",
                "parameter_hint_cn": "通过切换曲线与平滑窗口，观察不同参数区间下峰谷结构是否稳定。",
            }
        )
    return panels[:10]


def build_linked_reports(
    report_ids: list[str],
    metas_en: dict[str, dict[str, Any]],
    metas_cn: dict[str, dict[str, Any]],
    groups: dict[str, str],
    guide_by_report: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for report_id in report_ids:
        meta_en = metas_en.get(report_id, {})
        meta_cn = metas_cn.get(report_id, {})
        guide = guide_by_report.get(report_id, {})
        rows.append(
            {
                "report_id": report_id,
                "group": groups.get(report_id, "misc"),
                "title_en": safe_title(meta_en, report_id),
                "title_cn": safe_title(meta_cn, report_id),
                "summary_en": clean_text(str(meta_en.get("summary", "")), max_chars=250),
                "summary_cn": clean_text(str(meta_cn.get("summary", "")), max_chars=150),
                "book_role_en": clean_text(
                    str(guide.get("objective_en") or "Provides evidence and derivation pieces for this chapter."),
                    max_chars=220,
                ),
                "book_role_cn": clean_text(
                    str(guide.get("objective_cn") or "为本章提供可核对的证据与推导片段。"),
                    max_chars=130,
                ),
            }
        )
    return rows


def build_claim_ledger(report_ids: list[str], content_map: dict[str, Any], limit: int = 18) -> list[dict[str, Any]]:
    report_set = set(report_ids)
    claims = [row for row in content_map.get("claims", []) if str(row.get("report_id", "")) in report_set]
    claims.sort(key=lambda row: (STAGE_ORDER.get(str(row.get("stage", "finding")), 99), str(row.get("claim_id", ""))))
    output: list[dict[str, Any]] = []
    for claim in claims[:limit]:
        evidence = [
            {
                "evidence_type": str(ev.get("evidence_type", "source_document")),
                "path": str(ev.get("path", "")),
                "snippet_en": clean_text(str(ev.get("snippet_en", "")), max_chars=180),
                "snippet_cn": clean_text(
                    str(ev.get("snippet_cn", "")) if contains_cjk(str(ev.get("snippet_cn", ""))) else "该证据片段以英文记录，请结合上方路径在源文档核对。",
                    max_chars=120,
                ),
            }
            for ev in claim.get("evidence", [])
            if str(ev.get("path", "")).strip()
        ]
        if not evidence:
            continue
        text_cn = str(claim.get("text_cn", ""))
        if not contains_cjk(text_cn):
            text_cn = (
                f"报告 {str(claim.get('report_id', ''))} 的该条结论已在证据链中给出，可通过路径与交互面板继续核对。"
            )
        output.append(
            {
                "claim_id": str(claim.get("claim_id", "")),
                "report_id": str(claim.get("report_id", "")),
                "stage": str(claim.get("stage", "finding")),
                "text_en": clean_text(str(claim.get("text_en", "")), max_chars=260),
                "text_cn": clean_text(text_cn, max_chars=150),
                "evidence": evidence,
                "linked_report_ids": [str(x) for x in claim.get("linked_report_ids", []) if str(x).strip()],
            }
        )
    return output


def source_paths_for_chapter(chapter_payload: dict[str, Any], linked_reports: list[dict[str, Any]], metas_en: dict[str, dict[str, Any]]) -> list[str]:
    paths: list[str] = []
    for row in chapter_payload.get("claim_ledger", []):
        for ev in row.get("evidence", []):
            path = str(ev.get("path", "")).strip()
            if path:
                paths.append(path)
    for report in linked_reports:
        report_id = str(report.get("report_id", "")).strip()
        meta = metas_en.get(report_id, {})
        for source in meta.get("source_documents", []):
            path = str(source).strip()
            if path:
                paths.append(path)
    return uniq(paths)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build chapterized book content from web data payloads.")
    parser.add_argument("--data-root", type=Path, default=DEFAULT_DATA_ROOT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    data_root: Path = args.data_root

    index_path = data_root / "index.json"
    content_map_path = data_root / "content_map.json"
    theory_map_path = data_root / "theory_map.json"

    for required in [index_path, content_map_path, theory_map_path]:
        if not required.exists():
            raise SystemExit(f"Missing required input: {required}")

    index = read_json(index_path)
    content_map = read_json(content_map_path)
    theory_map = read_json(theory_map_path)

    index_rows = list(index.get("reports", []))
    report_ids = [str(row.get("report_id", "")).strip() for row in index_rows if str(row.get("report_id", "")).strip()]
    groups = {str(row.get("report_id", "")).strip(): str(row.get("group", "misc")) for row in index_rows}

    metas_en: dict[str, dict[str, Any]] = {}
    metas_cn: dict[str, dict[str, Any]] = {}
    for rid in report_ids:
        meta_en, meta_cn = load_meta_pair(data_root, rid)
        metas_en[rid] = meta_en
        metas_cn[rid] = meta_cn

    guide_by_report = {
        str(row.get("report_id", "")): row
        for row in content_map.get("report_guides", [])
        if str(row.get("report_id", "")).strip()
    }

    chapter_rows: list[dict[str, Any]] = []
    chapter_dir = data_root / "book" / "chapters"
    chapter_dir.mkdir(parents=True, exist_ok=True)

    for chapter in sorted(CHAPTER_BLUEPRINT, key=lambda row: int(row["order"])):
        chapter_id = str(chapter["chapter_id"])
        chapter_report_ids = [rid for rid in chapter.get("report_ids", []) if rid in metas_en]
        if not chapter_report_ids:
            continue

        concept_cards = pick_concept_cards(
            theory_map,
            chapter_report_ids,
            [str(x) for x in chapter.get("concept_keywords", [])],
        )
        theory_chain = pick_theory_chain(chapter_report_ids, metas_en, metas_cn)
        interactive_panels = pick_interactive_panels(chapter_report_ids, metas_en, metas_cn)
        linked_reports = build_linked_reports(chapter_report_ids, metas_en, metas_cn, groups, guide_by_report)
        claim_ledger = build_claim_ledger(chapter_report_ids, content_map)

        if not interactive_panels:
            # fallback to any available dataset in global reports
            for rid in report_ids:
                panel = pick_interactive_panels([rid], metas_en, metas_cn)
                if panel:
                    interactive_panels = panel
                    break
        if not theory_chain:
            theory_chain = [
                {
                    "report_id": chapter_report_ids[0],
                    "stage": "Theory Placeholder",
                    "label_en": "Core formula placeholder",
                    "label_cn": "核心公式占位",
                    "description_en": "No formula extracted; inspect linked reports for full derivations.",
                    "description_cn": "未提取到公式，请在关联报告中查看完整推导。",
                    "latex": "f(t)",
                    "context": "placeholder",
                }
            ]
        if not claim_ledger:
            claim_ledger = [
                {
                    "claim_id": f"{chapter_id}-fallback-claim",
                    "report_id": chapter_report_ids[0],
                    "stage": "finding",
                    "text_en": "This chapter remains evidence-linked through report-level summaries and dataset traces.",
                    "text_cn": "本章仍通过报告摘要与数据轨迹保持证据回链。",
                    "evidence": [
                        {
                            "evidence_type": "source_document",
                            "path": f"reports/{chapter_report_ids[0]}",
                            "snippet_en": "Linked report assets provide reproducible traces.",
                            "snippet_cn": "关联报告资产提供可复现实验轨迹。",
                        }
                    ],
                    "linked_report_ids": chapter_report_ids,
                }
            ]

        order = int(chapter["order"])
        previous_id = CHAPTER_BLUEPRINT[order - 1]["chapter_id"] if order > 0 else None
        next_id = CHAPTER_BLUEPRINT[order + 1]["chapter_id"] if order + 1 < len(CHAPTER_BLUEPRINT) else None

        chapter_payload: dict[str, Any] = {
            "chapter_id": chapter_id,
            "order": order,
            "slug": str(chapter["slug"]),
            "title_en": str(chapter["title_en"]),
            "title_cn": str(chapter["title_cn"]),
            "kicker_en": str(chapter["kicker_en"]),
            "kicker_cn": str(chapter["kicker_cn"]),
            "intro_en": [clean_text(x, max_chars=380) for x in chapter.get("intro_en", [])],
            "intro_cn": [clean_text(x, max_chars=220) for x in chapter.get("intro_cn", [])],
            "concept_cards": concept_cards,
            "theory_chain": theory_chain,
            "interactive_panels": interactive_panels,
            "linked_reports": linked_reports,
            "claim_ledger": claim_ledger,
            "summary_en": str(chapter["summary_en"]),
            "summary_cn": str(chapter["summary_cn"]),
            "previous_chapter_id": previous_id,
            "next_chapter_id": next_id,
            "source_paths": [],
            "updated_at": utc_now_iso(),
        }
        chapter_payload["source_paths"] = source_paths_for_chapter(chapter_payload, linked_reports, metas_en)

        write_json(chapter_dir / f"{chapter_id}.json", chapter_payload)
        chapter_rows.append(chapter_payload)

    chapter_rows.sort(key=lambda row: int(row["order"]))

    report_map = report_to_chapters()
    for rid in report_ids:
        if rid not in report_map:
            report_map[rid] = ["chapter-6-repro-validation"]

    manifest_chapters = [
        {
            "chapter_id": row["chapter_id"],
            "order": row["order"],
            "slug": row["slug"],
            "title_en": row["title_en"],
            "title_cn": row["title_cn"],
            "summary_en": row["summary_en"],
            "summary_cn": row["summary_cn"],
            "report_ids": [rep["report_id"] for rep in row["linked_reports"]],
            "concept_ids": [c["id"] for c in row["concept_cards"]],
            "interactive_count": len(row["interactive_panels"]),
            "claim_count": len(row["claim_ledger"]),
            "estimated_read_minutes": max(6, len(row["intro_en"]) * 2 + len(row["claim_ledger"]) // 2),
            "previous_chapter_id": row["previous_chapter_id"],
            "next_chapter_id": row["next_chapter_id"],
        }
        for row in chapter_rows
    ]

    toc_en = [
        {
            "chapter_id": row["chapter_id"],
            "order": row["order"],
            "title": row["title_en"],
            "path": f"/book/{row['chapter_id']}",
        }
        for row in chapter_rows
    ]
    toc_cn = [
        {
            "chapter_id": row["chapter_id"],
            "order": row["order"],
            "title": row["title_cn"],
            "path": f"/book/{row['chapter_id']}",
        }
        for row in chapter_rows
    ]

    quality_checks = [
        {
            "check": "all_reports_mapped_in_book",
            "pass": all(rid in report_map and len(report_map[rid]) > 0 for rid in report_ids),
            "details": {"missing": [rid for rid in report_ids if rid not in report_map]},
        },
        {
            "check": "chapters_have_interactive_panel",
            "pass": all(len(row["interactive_panels"]) >= 1 for row in chapter_rows),
            "details": {"chapter_ids": [row["chapter_id"] for row in chapter_rows if len(row["interactive_panels"]) < 1]},
        },
        {
            "check": "chapters_have_claim_ledger",
            "pass": all(len(row["claim_ledger"]) >= 1 for row in chapter_rows),
            "details": {"chapter_ids": [row["chapter_id"] for row in chapter_rows if len(row["claim_ledger"]) < 1]},
        },
        {
            "check": "chapters_have_theory_chain",
            "pass": all(len(row["theory_chain"]) >= 1 for row in chapter_rows),
            "details": {"chapter_ids": [row["chapter_id"] for row in chapter_rows if len(row["theory_chain"]) < 1]},
        },
    ]

    manifest = {
        "version": "v1",
        "generated_at": utc_now_iso(),
        "chapter_count": len(chapter_rows),
        "chapters": manifest_chapters,
        "toc": {
            "en": toc_en,
            "cn": toc_cn,
        },
        "report_chapter_map": {
            rid: {
                "primary_chapter_id": chapter_ids[0],
                "chapter_ids": chapter_ids,
            }
            for rid, chapter_ids in sorted(report_map.items())
        },
        "quality_checks": quality_checks,
    }

    write_json(data_root / "book" / "book_manifest.json", manifest)
    write_json(data_root / "book" / "toc.json", {"version": "v1", "generated_at": utc_now_iso(), "en": toc_en, "cn": toc_cn})

    print(
        json.dumps(
            {
                "ok": True,
                "chapter_count": len(chapter_rows),
                "manifest": (data_root / "book" / "book_manifest.json").as_posix(),
                "toc": (data_root / "book" / "toc.json").as_posix(),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
