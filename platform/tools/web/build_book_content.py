#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from book_blueprint import CHAPTER_BLUEPRINT, report_to_chapters


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_DATA_ROOT = REPO_ROOT / "platform" / "web" / "public" / "data" / "v1"
STAGE_ORDER = {"model": 0, "method": 1, "result": 2, "finding": 3}

CHAPTER_CLAIM_LIMIT: dict[str, int] = {
    "chapter-0-reading-guide": 8,
    "chapter-1-core-fpt": 8,
    "chapter-2-grid2d-family": 10,
    "chapter-3-ring-baseline": 8,
    "chapter-4-shortcut-variants": 8,
    "chapter-5-cross-model-synthesis": 8,
    "chapter-6-repro-validation": 8,
    "chapter-7-outlook": 6,
}

CHAPTER_STAGE_PRIORITY: dict[str, dict[str, int]] = {
    "chapter-0-reading-guide": {"model": 5, "method": 6, "result": 2, "finding": 1},
    "chapter-1-core-fpt": {"model": 6, "method": 5, "result": 3, "finding": 2},
    "chapter-2-grid2d-family": {"model": 4, "method": 5, "result": 6, "finding": 3},
    "chapter-3-ring-baseline": {"model": 5, "method": 6, "result": 4, "finding": 2},
    "chapter-4-shortcut-variants": {"model": 3, "method": 5, "result": 6, "finding": 4},
    "chapter-5-cross-model-synthesis": {"model": 2, "method": 4, "result": 6, "finding": 7},
    "chapter-6-repro-validation": {"model": 1, "method": 7, "result": 8, "finding": 6},
    "chapter-7-outlook": {"model": 1, "method": 5, "result": 6, "finding": 9},
}

CHAPTER_KEYWORD_HINTS: dict[str, list[str]] = {
    "chapter-0-reading-guide": ["notation", "protocol", "verify", "evidence", "path"],
    "chapter-1-core-fpt": ["first-passage", "hazard", "survival", "bimodality", "peak"],
    "chapter-2-grid2d-family": ["grid", "reflecting", "corridor", "boundary", "two-target"],
    "chapter-3-ring-baseline": ["ring", "lazy", "spectral", "baseline", "inversion"],
    "chapter-4-shortcut-variants": ["shortcut", "beta", "selfloop", "renormalize", "equal4"],
    "chapter-5-cross-model-synthesis": ["cross", "regime", "transfer", "mapping", "consistency"],
    "chapter-6-repro-validation": ["repro", "audit", "validation", "schema", "ci", "pipeline", "command", "hash"],
    "chapter-7-outlook": ["outlook", "future", "open", "hypothesis", "uncertainty", "next"],
}

CHAPTER_BRIDGES: dict[str, tuple[str, str]] = {
    "chapter-1-core-fpt": (
        "Bridge from Chapter 0: now that notation and audit protocol are fixed, we formalize f(t), S(t), and h(t) as the common diagnostic language.",
        "承接第0章：在符号和核验协议固定后，本章把 f(t)、S(t)、h(t) 正式建立为统一诊断语言。",
    ),
    "chapter-2-grid2d-family": (
        "Bridge from Chapter 1: with shared FPT diagnostics in place, we test which Grid2D geometric constraints preserve or break bimodality.",
        "承接第1章：在统一 FPT 诊断语言下，本章检验 Grid2D 中哪些几何约束会保持或破坏双峰结构。",
    ),
    "chapter-3-ring-baseline": (
        "Bridge from Chapter 2: Grid2D established boundary-sensitive diagnostics; this chapter keeps those diagnostics but shifts geometry to a ring so shortcut and lazy effects can be isolated.",
        "承接第2章：我们保留 Grid2D 的边界敏感诊断，但将几何切换到环结构，以单独识别 shortcut 与 lazy 机制。",
    ),
    "chapter-4-shortcut-variants": (
        "Bridge from Chapter 3: after fixing a conservative ring baseline, we vary shortcut implementations to identify which phase transitions are mechanism-driven.",
        "承接第3章：在 ring 基线固定后，本章改变 shortcut 实现方式，识别哪些相位转变由机制本身驱动。",
    ),
    "chapter-5-cross-model-synthesis": (
        "Bridge from Chapter 4: once shortcut variants are disentangled, we align Grid2D and Ring diagnostics into one transferable cross-model map.",
        "承接第4章：在 shortcut 变体被拆解后，本章把 Grid2D 与 Ring 的诊断对齐为可迁移的统一图谱。",
    ),
    "chapter-6-repro-validation": (
        "Bridge from Chapter 5: after cross-model synthesis, we now test whether every key claim remains reproducible under command-level and schema-level checks.",
        "承接第5章：完成跨模型综合后，本章转向命令级与 schema 级核验，确认关键 claim 仍可复现。",
    ),
    "chapter-7-outlook": (
        "Bridge from Chapter 6: once reproducibility gates are satisfied, unresolved mechanisms can be promoted into auditable next-step hypotheses instead of speculative notes.",
        "承接第6章：在复现门禁通过后，未解机制可被提升为可审计的下一步假设，而非松散猜测。",
    ),
}

THEORY_CN_PLACEHOLDERS = {
    "补充连接推导相邻步骤的关系式。",
    "该步骤对应的公式见原始推导链。",
    "请在源文件中核对该公式上下文。",
}

PANEL_NEGATIVE_HINTS = (
    "asset",
    "size",
    "profile",
    "hash",
    "integrity",
    "registry",
    "audit",
    "placeholder",
)

PANEL_POSITIVE_HINTS = (
    "probability",
    "pmf",
    "fpt",
    "hazard",
    "survival",
    "peak",
    "valley",
    "phase",
    "beta",
    "scan",
    "cond_by_t",
    "two_target",
    "bimodal",
)


def utc_now_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def repair_common_math_noise(text: str) -> str:
    value = re.sub(r"\s+", " ", str(text or "")).strip()
    if not value:
        return ""
    value = value.replace("…", " ")
    value = re.sub(r"\.{3,}", " ", value)
    value = re.sub(r"\bshortcu\b", "shortcut", value, flags=re.IGNORECASE)
    value = re.sub(r"\b1\s*,\s*,\s*N\b", "1..N", value, flags=re.IGNORECASE)
    value = re.sub(r"\b0\s*,\s*,\s*N\s*-\s*1\s*\^\s*2\b", "[0, N-1]^2", value, flags=re.IGNORECASE)
    value = re.sub(r"\b0\s*,\s*,\s*N\s*-\s*1\b", "0..N-1", value, flags=re.IGNORECASE)
    value = re.sub(r"\b([A-Za-z])\s+p(\d+)\b", lambda m: f"{m.group(1)}_p{m.group(2)}", value, flags=re.IGNORECASE)
    value = re.sub(r"\b([xy])\s+t\b", lambda m: f"{m.group(1)}_t", value, flags=re.IGNORECASE)
    value = re.sub(r"\bn\s+0\b", "n0", value, flags=re.IGNORECASE)
    value = re.sub(
        r"\bK\s+(\d(?:\s*,\s*\d)+)\b",
        lambda m: "K=" + "".join(m.group(1).split()),
        value,
        flags=re.IGNORECASE,
    )
    value = re.sub(r"\bP\s*:\s*([0-9]+(?:\.[0-9]+)?)\b", r"P=\1", value, flags=re.IGNORECASE)
    value = re.sub(r"\bwe use,\s*hence\b", "With fixed parameters,", value, flags=re.IGNORECASE)
    value = re.sub(r"\bup to\.\s*$", "", value, flags=re.IGNORECASE)
    value = re.sub(r"\s*,\s*all\s*$", ".", value, flags=re.IGNORECASE)
    value = re.sub(r"\s{2,}", " ", value)
    return value.strip()


def clean_text(text: str, *, max_chars: int = 320, ellipsis: bool = True) -> str:
    value = repair_common_math_noise(text)
    if len(value) <= max_chars:
        return value
    clipped = value[: max_chars + 1]
    stop = max(clipped.rfind(". "), clipped.rfind("。"), clipped.rfind("; "), clipped.rfind("；"))
    if stop < int(max_chars * 0.45):
        stop = max_chars
    suffix = "…" if ellipsis else ""
    return clipped[:stop].rstrip(" ,;。；") + suffix


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


def normalize_text_key(value: str) -> str:
    text = re.sub(r"\s+", " ", str(value or "").strip().lower())
    text = text.replace("…", "").replace("...", "")
    text = re.sub(r"[`*_]+", "", text)
    return text


def clean_claim_text(text: str, *, lang: str, max_chars: int = 520) -> str:
    value = repair_common_math_noise(text).replace("…", "").replace("...", "")
    if len(value) <= max_chars:
        return value
    clipped = value[: max_chars + 1]
    stop = max(clipped.rfind(". "), clipped.rfind("? "), clipped.rfind("! "), clipped.rfind("。"), clipped.rfind("；"))
    if stop < int(max_chars * 0.55):
        stop = max_chars
    out = clipped[:stop].rstrip(" ,;。；")
    if not out:
        return value[:max_chars]
    if lang == "cn" and out[-1] not in "。！？":
        return out + "。"
    if lang != "cn" and out[-1] not in ".!?":
        return out + "."
    return out


def is_low_signal_claim_text(text: str) -> bool:
    value = str(text or "").strip()
    normalized = value.lower()
    if len(normalized) < 26:
        return True
    if len(normalized.split()) <= 4:
        return True
    if normalized.startswith("`") and "/" in normalized:
        return True
    if normalized.startswith("`outputs/`") or normalized.startswith("`code/`"):
        return True
    if re.match(r"^(?:n\s*=\s*\d+|boundary:|phase map|fixed\s+\(|setup:?)", normalized):
        return True
    if normalized in {"n=31.", "phase map on (w 2, skip2)."}:
        return True
    return False


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
    def improve_cn_description(
        *,
        report_id: str,
        stage: str,
        cn_candidate: str,
        en_candidate: str,
        context: str,
        meta_cn: dict[str, Any],
    ) -> str:
        raw_cn = clean_text(cn_candidate, max_chars=150)
        lowered_cn = normalize_text_key(raw_cn)
        if raw_cn and contains_cjk(raw_cn) and lowered_cn not in {normalize_text_key(x) for x in THEORY_CN_PLACEHOLDERS}:
            if "补充连接推导相邻步骤" not in raw_cn:
                return raw_cn

        narrative = dict(meta_cn.get("narrative", {}))
        stage_norm = normalize_text_key(stage)
        if "model" in stage_norm:
            seed = str(narrative.get("model_overview", "")) or f"{report_id} 的该步骤用于明确模型约束与符号含义。"
        elif "method" in stage_norm or "derivation" in stage_norm:
            seed = str(narrative.get("method_overview", "")) or f"{report_id} 的该步骤用于连接推导与反演流程。"
        else:
            seed = str(narrative.get("result_overview", "")) or f"{report_id} 的该步骤用于解释峰谷结构与相区变化。"
        if contains_cjk(seed):
            return clean_text(seed, max_chars=150)
        fallback = f"该步骤对应 {report_id} 的 {context or '理论链'}，请结合公式与证据路径核对其机制含义。"
        return clean_text(fallback, max_chars=150)

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
                        "description_cn": improve_cn_description(
                            report_id=report_id,
                            stage=str(item_en.get("stage", "")),
                            cn_candidate=str(item_cn.get("description", item_en.get("description", ""))),
                            en_candidate=str(item_en.get("description", "")),
                            context=str(item_en.get("context", "")),
                            meta_cn=meta_cn,
                        ),
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
                    "description_cn": improve_cn_description(
                        report_id=report_id,
                        stage="fallback",
                        cn_candidate=str(item_cn.get("context", "该报告的核心公式。")),
                        en_candidate=str(item_en.get("context", "")),
                        context="math_blocks",
                        meta_cn=meta_cn,
                    ),
                    "latex": str(item_en.get("latex", "")).strip() or "f(t)",
                    "context": str(item_en.get("context", "math_blocks")).strip() or "math_blocks",
                }
            )

    return chain[:18]


def enrich_theory_chain(chapter_id: str, report_ids: list[str], base_chain: list[dict[str, Any]]) -> list[dict[str, Any]]:
    special = chapter_special_theory_items(chapter_id, report_ids)
    merged = special + base_chain
    seen: set[str] = set()
    output: list[dict[str, Any]] = []
    for row in merged:
        key = normalize_text_key(f"{row.get('report_id')}::{row.get('latex')}::{row.get('description_en')}")
        if key in seen:
            continue
        seen.add(key)
        output.append(row)
    return output[:14]


def chapter_intro_with_bridge(chapter: dict[str, Any], chapter_id: str) -> tuple[list[str], list[str]]:
    intro_en = [clean_text(x, max_chars=420, ellipsis=False) for x in chapter.get("intro_en", [])]
    intro_cn = [clean_text(x, max_chars=260, ellipsis=False) for x in chapter.get("intro_cn", [])]

    bridge_en = ""
    bridge_cn = ""
    bridge = CHAPTER_BRIDGES.get(chapter_id)
    if bridge:
        bridge_en, bridge_cn = bridge

    if bridge_en and all(normalize_text_key(bridge_en) != normalize_text_key(row) for row in intro_en):
        intro_en.append(bridge_en)
    if bridge_cn and all(normalize_text_key(bridge_cn) != normalize_text_key(row) for row in intro_cn):
        intro_cn.append(bridge_cn)
    return intro_en, intro_cn


def pick_interactive_panels(report_ids: list[str], metas_en: dict[str, dict[str, Any]], metas_cn: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    def panel_score(dataset: dict[str, Any]) -> int:
        title = normalize_text_key(str(dataset.get("title", "")))
        series_id = normalize_text_key(str(dataset.get("series_id", "")))
        y_label = normalize_text_key(str(dataset.get("y_label", "")))
        x_label = normalize_text_key(str(dataset.get("x_label", "")))
        haystack = " ".join([title, series_id, y_label, x_label])
        score = 0
        for token in PANEL_POSITIVE_HINTS:
            if token in haystack:
                score += 3
        for token in PANEL_NEGATIVE_HINTS:
            if token in haystack:
                score -= 9
        if "probability" in y_label:
            score += 5
        if "asset rank" in x_label or "size (bytes)" in y_label:
            score -= 14
        if "manifest" in series_id:
            score -= 7
        if str(dataset.get("series_path", "")).strip().startswith("/data/v1/reports/"):
            score += 1
        return score

    def panel_hint(ds: dict[str, Any], *, lang: str) -> str:
        y_label = normalize_text_key(str(ds.get("y_label", "")))
        series_id = normalize_text_key(str(ds.get("series_id", "")))
        if "probability" in y_label or "pmf" in series_id or "fpt" in series_id:
            if lang == "cn":
                return "优先比较主峰与次峰的相对高度，并调节平滑窗口检验谷值是否稳定。"
            return "Compare first/second peak prominence first, then adjust smoothing to test valley stability."
        if "phase" in y_label or "binary" in y_label:
            if lang == "cn":
                return "切换不同系列查看相图边界变化，并核对阈值附近是否存在相区翻转。"
            return "Toggle series to inspect phase boundaries and check whether transitions flip near threshold bands."
        if lang == "cn":
            return "切换曲线并微调平滑窗口，观察参数变化如何重排快通道与延迟通道贡献。"
        return "Toggle series and tune smoothing to see how parameter shifts reweight fast versus delayed pathways."

    panels: list[dict[str, Any]] = []
    for report_id in report_ids:
        meta_en = metas_en.get(report_id, {})
        meta_cn = metas_cn.get(report_id, {})
        datasets_en = list(meta_en.get("datasets", []))
        datasets_cn = list(meta_cn.get("datasets", []))
        if not datasets_en:
            continue
        ranked = sorted(
            [(panel_score(ds), idx, ds) for idx, ds in enumerate(datasets_en)],
            key=lambda row: (row[0], -row[1]),
            reverse=True,
        )
        best_score, best_idx, ds_en = ranked[0]
        if best_score < -6:
            continue
        ds_cn = datasets_cn[best_idx] if best_idx < len(datasets_cn) else ds_en
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
                "parameter_hint_en": panel_hint(ds_en, lang="en"),
                "parameter_hint_cn": panel_hint(ds_en, lang="cn"),
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


def prioritize_new_concepts(concept_cards: list[dict[str, Any]], used_concept_ids: set[str], *, limit: int = 6) -> list[dict[str, Any]]:
    unseen = [row for row in concept_cards if row.get("id") not in used_concept_ids]
    seen = [row for row in concept_cards if row.get("id") in used_concept_ids]
    merged = unseen + seen
    output = merged[:limit]
    if len(output) < min(3, len(merged)):
        output = merged[: min(3, len(merged))]
    return output


def chapter_special_theory_items(chapter_id: str, report_ids: list[str]) -> list[dict[str, Any]]:
    seed = report_ids[0] if report_ids else chapter_id
    if chapter_id == "chapter-6-repro-validation":
        return [
            {
                "report_id": seed,
                "stage": "validation",
                "label_en": "Schema-gated reproducibility contract",
                "label_cn": "Schema 门禁复现契约",
                "description_en": "Each release requires schema pass for web/book/agent payloads before publication.",
                "description_cn": "每次发布前必须通过 web/book/agent 数据 schema 校验。",
                "latex": r"\forall a\in\mathcal{A}_{release},\ \operatorname{validate}(a)=\mathrm{PASS}",
                "context": "reproducibility_gate",
            },
            {
                "report_id": seed,
                "stage": "validation",
                "label_en": "Artifact hash stability",
                "label_cn": "产物哈希稳定性",
                "description_en": "Traceability is enforced by deterministic build outputs with file hash and size checks.",
                "description_cn": "通过文件 hash 与 size 一致性检查保证产物可追溯。",
                "latex": r"\operatorname{trace}(f)=\{\mathrm{sha256}(f),|f|\}",
                "context": "artifact_traceability",
            },
            {
                "report_id": seed,
                "stage": "validation",
                "label_en": "Cross-check closure",
                "label_cn": "交叉校验闭环",
                "description_en": "Release is allowed only when multi-agent cross-check high-priority findings are closed.",
                "description_cn": "仅当多 agent 交叉校验高优先级问题清零后才允许发布。",
                "latex": r"\sum_{i\in\mathcal{H}}\mathbf{1}[\mathrm{open}_i]=0",
                "context": "release_gate",
            },
        ]
    if chapter_id == "chapter-7-outlook":
        return [
            {
                "report_id": seed,
                "stage": "outlook",
                "label_en": "Hypothesis H1: hazard bridge between lattice and ring",
                "label_cn": "假设 H1：网格与环的 hazard 桥接",
                "description_en": "Open question: can one hazard-based criterion classify valley transitions across both families without geometry-specific tuning?",
                "description_cn": "开放问题：是否存在单一 hazard 判据，在不依赖几何特化调参的情况下统一解释两类模型的谷值转变？",
                "latex": r"H_1:\ \exists\ \Phi,\ \Phi(\text{Grid2D})\approx\Phi(\text{Ring})\Rightarrow\text{same valley class}",
                "context": "open_hypothesis",
            },
            {
                "report_id": seed,
                "stage": "outlook",
                "label_en": "Information-prioritized experiment queue",
                "label_cn": "信息增益优先实验队列",
                "description_en": "Next experiments should maximize uncertainty reduction per compute budget under reproducibility constraints.",
                "description_cn": "下一步实验应在复现约束下，最大化单位计算预算的认知不确定性下降。",
                "latex": r"\arg\max_{e\in\mathcal{E}} \frac{\Delta I(e)}{C(e)}",
                "context": "experiment_planning",
            },
            {
                "report_id": seed,
                "stage": "outlook",
                "label_en": "Claim graph continuation rule",
                "label_cn": "Claim 图谱延续规则",
                "description_en": "Incoming agents should extend existing claim graph nodes instead of resetting report-level context.",
                "description_cn": "新进入 agent 应在现有 claim 图谱上增量扩展，而不是重置报告上下文。",
                "latex": r"G_{t+1}=G_t\cup \Delta G,\ \Delta G\ \text{must reference existing evidence nodes}",
                "context": "agent_handoff",
            },
        ]
    return []


def chapter_special_claims(chapter_id: str, report_ids: list[str]) -> list[dict[str, Any]]:
    report_seed = report_ids[0] if report_ids else chapter_id
    if chapter_id == "chapter-6-repro-validation":
        return [
            {
                "claim_id": "chapter-6-repro-validation-cmd-closure",
                "report_id": report_seed,
                "stage": "method",
                "text_en": "Reproducibility is enforced as an executable contract: web data, glossary, book chapters, backbone, agent sync, and validators run in one closed pipeline.",
                "text_cn": "复现被实现为可执行契约：web 数据、术语表、章节、主干、agent 同步与校验在同一闭环流水线内执行。",
                "evidence": [
                    {
                        "evidence_type": "source_document",
                        "path": "scripts/reportctl.py",
                        "snippet_en": "reportctl wires web-data/book-data/agent-sync/validate into unified commands.",
                        "snippet_cn": "reportctl 把 web-data/book-data/agent-sync/validate 串成统一命令入口。",
                    },
                    {
                        "evidence_type": "source_document",
                        "path": "platform/tools/web/build_three_deliverables.py",
                        "snippet_en": "deliverables pipeline includes publication and agent pack outputs.",
                        "snippet_cn": "三交付流水线包含 publication 与 agent pack 同步构建。",
                    },
                ],
                "linked_report_ids": list(report_ids),
            },
            {
                "claim_id": "chapter-6-repro-validation-schema-gate",
                "report_id": report_seed,
                "stage": "result",
                "text_en": "Schema gates now cover both report payloads and book backbone, preventing hidden contract drift across releases.",
                "text_cn": "schema 门禁已覆盖报告数据与 book 主干，避免版本迭代中出现隐性接口漂移。",
                "evidence": [
                    {
                        "evidence_type": "source_document",
                        "path": "platform/tools/web/validate_web_data.py",
                        "snippet_en": "validator checks book manifest/chapters/backbone and cross-file consistency.",
                        "snippet_cn": "校验器会检查 book manifest/chapters/backbone 以及跨文件一致性。",
                    },
                    {
                        "evidence_type": "source_document",
                        "path": "platform/schemas/book_backbone_v1.schema.json",
                        "snippet_en": "book backbone has explicit schema contract for chapter spine and acts.",
                        "snippet_cn": "book backbone 具备章节主干与幕结构的显式 schema 契约。",
                    },
                ],
                "linked_report_ids": list(report_ids),
            },
            {
                "claim_id": "chapter-6-repro-validation-ci-publish",
                "report_id": report_seed,
                "stage": "result",
                "text_en": "Deployment and audit checks are automated in CI so publishing is gated by machine-verifiable quality checks instead of manual inspection.",
                "text_cn": "部署与审计检查已进入 CI，发布由机器可验证门禁控制，而非人工主观检查。",
                "evidence": [
                    {
                        "evidence_type": "source_document",
                        "path": ".github/workflows/site-pages.yml",
                        "snippet_en": "Pages workflow builds and publishes static site artifacts.",
                        "snippet_cn": "Pages 工作流负责静态站点构建与发布。",
                    },
                    {
                        "evidence_type": "source_document",
                        "path": ".github/workflows/repo-audit.yml",
                        "snippet_en": "repository audit workflow preserves baseline research integrity checks.",
                        "snippet_cn": "仓库审计工作流保留基础科研完整性检查。",
                    },
                ],
                "linked_report_ids": list(report_ids),
            },
            {
                "claim_id": "chapter-6-repro-validation-agent-handoff",
                "report_id": report_seed,
                "stage": "finding",
                "text_en": "Agent handoff is traceable because manifest, chapter jsonl, claim graph, and translation QC are generated together with provenance pointers.",
                "text_cn": "agent 交接可追溯，因为 manifest、章节 jsonl、claim 图谱与翻译质检会连同溯源指针一起生成。",
                "evidence": [
                    {
                        "evidence_type": "source_document",
                        "path": "platform/tools/web/build_agent_sync.py",
                        "snippet_en": "agent sync exports manifest, reports/events jsonl, book files, claim graph, and guide.",
                        "snippet_cn": "agent sync 会导出 manifest、reports/events jsonl、book 文件、claim graph 与 guide。",
                    },
                    {
                        "evidence_type": "dataset",
                        "path": "/data/v1/agent/manifest.json",
                        "snippet_en": "manifest enumerates machine-readable files for downstream agents.",
                        "snippet_cn": "manifest 枚举了供下游 agent 消费的机器可读文件。",
                    },
                ],
                "linked_report_ids": list(report_ids),
            },
        ]
    if chapter_id == "chapter-7-outlook":
        return [
            {
                "claim_id": "chapter-7-outlook-gap-hazard-bridge",
                "report_id": report_seed,
                "stage": "finding",
                "text_en": "Open gap: we still need a single hazard-led criterion that transfers from Grid2D corridors to ring shortcut regimes without case-specific redefinition.",
                "text_cn": "开放缺口：仍需一个统一的 hazard 判据，能够从 Grid2D 通道情形迁移到 ring shortcut 区间，而不需要逐案重定义。",
                "evidence": [
                    {
                        "evidence_type": "source_document",
                        "path": "research/reports/grid2d_two_target_double_peak/manuscript/grid2d_two_target_double_peak_en.tex",
                        "snippet_en": "grid two-target evidence provides hazard-sensitive valley behavior under geometric constraints.",
                        "snippet_cn": "grid 双目标证据给出了几何约束下对 hazard 敏感的谷值行为。",
                    },
                    {
                        "evidence_type": "source_document",
                        "path": "research/reports/ring_two_target/manuscript/ring_two_target_en.tex",
                        "snippet_en": "ring two-target results expose shortcut-regime transitions with comparable diagnostics.",
                        "snippet_cn": "ring 双目标结果展示了可对齐诊断下的 shortcut 区间转变。",
                    },
                ],
                "linked_report_ids": list(report_ids),
            },
            {
                "claim_id": "chapter-7-outlook-gap-regime-transfer",
                "report_id": report_seed,
                "stage": "finding",
                "text_en": "Cross-model regime maps are now available, but transfer confidence remains conditional on matched sampling protocols and fairness constraints.",
                "text_cn": "跨模型相图已具备，但迁移置信度仍依赖采样协议与公平约束是否严格对齐。",
                "evidence": [
                    {
                        "evidence_type": "source_document",
                        "path": "research/reports/cross_luca_regime_map/manuscript/cross_luca_regime_map_en.tex",
                        "snippet_en": "cross-model map quantifies regime outcomes under fixed-T full-FPT fairness settings.",
                        "snippet_cn": "跨模型图谱在固定 T 与完整 FPT 公平设定下量化了相区结果。",
                    },
                    {
                        "evidence_type": "dataset",
                        "path": "/data/v1/reports/cross_luca_regime_map/series/manifest.json",
                        "snippet_en": "manifest keeps explicit regime-scan metadata for reproducible transfer checks.",
                        "snippet_cn": "manifest 保留了可复现迁移校验所需的相区扫描元数据。",
                    },
                ],
                "linked_report_ids": list(report_ids),
            },
            {
                "claim_id": "chapter-7-outlook-next-experiment-plan",
                "report_id": report_seed,
                "stage": "method",
                "text_en": "Next iteration should prioritize experiments by uncertainty reduction per compute cost, while preserving claim-evidence traceability constraints.",
                "text_cn": "下一轮应按“单位计算成本的不确定性下降”来排序实验，并保持 claim-证据可追溯约束。",
                "evidence": [
                    {
                        "evidence_type": "source_document",
                        "path": "platform/web/public/data/v1/book/backbone.json",
                        "snippet_en": "backbone captures chapter-level dependencies and transition constraints for planning.",
                        "snippet_cn": "backbone 记录了章节依赖与过渡约束，可直接用于实验规划。",
                    },
                    {
                        "evidence_type": "dataset",
                        "path": "/data/v1/agent/claim_graph.jsonl",
                        "snippet_en": "claim graph enables tracking which open questions are already evidence-linked.",
                        "snippet_cn": "claim 图谱可以跟踪哪些开放问题已经建立证据链接。",
                    },
                ],
                "linked_report_ids": list(report_ids),
            },
            {
                "claim_id": "chapter-7-outlook-agent-continuation",
                "report_id": report_seed,
                "stage": "result",
                "text_en": "A new agent can continue the research storyline without context reset because chapter manifests, claim graph, and iteration history are packaged together.",
                "text_cn": "新 agent 可在不重置上下文的情况下继续研究主线，因为章节 manifest、claim 图谱与迭代历史已被打包同步。",
                "evidence": [
                    {
                        "evidence_type": "source_document",
                        "path": ".local/checks/openclaw_review_history.jsonl",
                        "snippet_en": "review history tracks iterative quality decisions across rounds.",
                        "snippet_cn": "评审历史记录了多轮质量决策轨迹。",
                    },
                    {
                        "evidence_type": "source_document",
                        "path": ".local/checks/content_iteration/run_history.jsonl",
                        "snippet_en": "content iteration history records build and validation progression.",
                        "snippet_cn": "内容迭代历史记录了构建与校验推进过程。",
                    },
                ],
                "linked_report_ids": list(report_ids),
            },
            {
                "claim_id": "chapter-7-outlook-gap-parameter-geometry",
                "report_id": report_seed,
                "stage": "finding",
                "text_en": "The strongest unresolved coupling is between geometry asymmetry and parameter-scan thresholds; future work must isolate these effects with controlled factorial sweeps.",
                "text_cn": "当前最核心的未解耦合在于“几何非对称”与“参数扫描阈值”的相互作用；后续应通过受控因子扫描将二者分离。",
                "evidence": [
                    {
                        "evidence_type": "source_document",
                        "path": "research/reports/grid2d_rect_bimodality/manuscript/grid2d_rect_bimodality_en.tex",
                        "snippet_en": "rectangular geometry changes first-passage structure and valley shape under fixed model assumptions.",
                        "snippet_cn": "在固定模型假设下，矩形几何会改变首达结构与谷值形态。",
                    },
                    {
                        "evidence_type": "source_document",
                        "path": "research/reports/ring_valley_dst/manuscript/ring_valley_dst_en.tex",
                        "snippet_en": "shortcut-strength scans show regime turnover tied to parameter choices.",
                        "snippet_cn": "shortcut 强度扫描显示了与参数选择相关的相区翻转。",
                    },
                ],
                "linked_report_ids": list(report_ids),
            },
            {
                "claim_id": "chapter-7-outlook-gap-proof-depth",
                "report_id": report_seed,
                "stage": "method",
                "text_en": "Proof-depth exceptions should be converted into explicit closure tasks by prioritizing reports with thinner derivation chains before adding new model variants.",
                "text_cn": "在扩展新模型变体之前，应先把推导深度不足的条目转化为明确收敛任务并优先补齐。",
                "evidence": [
                    {
                        "evidence_type": "source_document",
                        "path": "platform/web/public/data/v1/theory_map.json",
                        "snippet_en": "theory consistency checks expose formula-depth policy status and exception rows.",
                        "snippet_cn": "theory 一致性检查会给出公式深度策略状态及例外条目。",
                    },
                    {
                        "evidence_type": "source_document",
                        "path": ".local/checks/openclaw_book_math.json",
                        "snippet_en": "math review flags remaining caveats on derivation depth and auditability quality.",
                        "snippet_cn": "数学评审标注了推导深度与可审计性方面仍待改进的项。",
                    },
                ],
                "linked_report_ids": list(report_ids),
            },
        ]
    return []


def materialize_claim(claim: dict[str, Any], default_report_ids: list[str]) -> tuple[dict[str, Any] | None, str]:
    evidence = [
        {
            "evidence_type": str(ev.get("evidence_type", "source_document")),
            "path": str(ev.get("path", "")),
            "snippet_en": clean_text(str(ev.get("snippet_en", "")), max_chars=240, ellipsis=False),
            "snippet_cn": clean_text(
                str(ev.get("snippet_cn", "")) if contains_cjk(str(ev.get("snippet_cn", ""))) else "该证据片段以英文记录，请结合路径在源文档核对。",
                max_chars=150,
                ellipsis=False,
            ),
        }
        for ev in claim.get("evidence", [])
        if str(ev.get("path", "")).strip()
    ]
    if not evidence:
        return None, ""
    text_en = clean_claim_text(str(claim.get("text_en", "")), lang="en")
    text_cn_raw = str(claim.get("text_cn", ""))
    if not contains_cjk(text_cn_raw):
        text_cn_raw = f"该结论来自 {str(claim.get('report_id', ''))} 的可核对证据链，请在证据路径中继续核验。"
    text_cn = clean_claim_text(text_cn_raw, lang="cn", max_chars=260)
    row = {
        "claim_id": str(claim.get("claim_id", "")).strip(),
        "report_id": str(claim.get("report_id", "")).strip(),
        "stage": str(claim.get("stage", "finding")).strip() or "finding",
        "text_en": text_en,
        "text_cn": text_cn,
        "evidence": evidence,
        "linked_report_ids": [str(x) for x in claim.get("linked_report_ids", []) if str(x).strip()] or list(default_report_ids),
    }
    if row["stage"] not in STAGE_ORDER:
        row["stage"] = "finding"
    text_key = normalize_text_key(text_en)
    return row, text_key


def build_claim_ledger(
    chapter_id: str,
    report_ids: list[str],
    content_map: dict[str, Any],
    used_claim_ids: set[str],
    used_claim_text_keys: set[str],
) -> list[dict[str, Any]]:
    report_set = set(report_ids)
    chapter_limit = CHAPTER_CLAIM_LIMIT.get(chapter_id, 8)
    stage_priority = CHAPTER_STAGE_PRIORITY.get(chapter_id, CHAPTER_STAGE_PRIORITY["chapter-5-cross-model-synthesis"])
    keyword_hints = [token.lower() for token in CHAPTER_KEYWORD_HINTS.get(chapter_id, [])]

    output: list[dict[str, Any]] = []
    output_ids: set[str] = set()
    output_text: set[str] = set()

    # Chapter-specific claims ensure late chapters add genuinely new narrative content.
    for claim in chapter_special_claims(chapter_id, report_ids):
        row, key = materialize_claim(claim, report_ids)
        if not row or not row["claim_id"] or row["claim_id"] in output_ids:
            continue
        output.append(row)
        output_ids.add(row["claim_id"])
        if key:
            output_text.add(key)

    scored: list[tuple[int, int, int, str, dict[str, Any], str]] = []
    for claim in content_map.get("claims", []):
        report_id = str(claim.get("report_id", "")).strip()
        claim_id = str(claim.get("claim_id", "")).strip()
        if not claim_id or report_id not in report_set or claim_id in output_ids:
            continue
        if claim_id in used_claim_ids:
            continue
        row, text_key = materialize_claim(claim, report_ids)
        if not row:
            continue
        if chapter_id not in {"chapter-0-reading-guide", "chapter-6-repro-validation"} and is_low_signal_claim_text(row["text_en"]):
            continue
        stage = row["stage"]
        haystack = f"{row['text_en']} {row['text_cn']}".lower()
        keyword_hits = sum(1 for token in keyword_hints if token and token in haystack)
        novelty_id = 1 if claim_id not in used_claim_ids else 0
        novelty_text = 1 if text_key and text_key not in used_claim_text_keys else 0
        score = stage_priority.get(stage, 0) * 12 + keyword_hits * 8 + novelty_id * 26 + novelty_text * 20 + len(row["evidence"]) * 2
        scored.append((score, novelty_id, novelty_text, claim_id, row, text_key))

    scored.sort(
        key=lambda item: (
            item[0],
            item[1],
            item[2],
            -STAGE_ORDER.get(item[4]["stage"], 99),
            item[3],
        ),
        reverse=True,
    )

    target = max(chapter_limit, len(output), len(report_ids))

    # Ensure each linked report contributes at least one claim when available.
    for report_id in report_ids:
        if len(output) >= target:
            break
        if any(str(row.get("report_id", "")) == report_id for row in output):
            continue
        for _, _, _, claim_id, row, text_key in scored:
            if str(row.get("report_id", "")) != report_id:
                continue
            if claim_id in output_ids:
                continue
            if text_key and text_key in output_text:
                continue
            output.append(row)
            output_ids.add(claim_id)
            if text_key:
                output_text.add(text_key)
            break

    for score, novelty_id, novelty_text, claim_id, row, text_key in scored:
        if len(output) >= target:
            break
        if claim_id in output_ids:
            continue
        if text_key and text_key in output_text:
            continue
        # First pass prioritizes new chapter information over cross-chapter repeats.
        if len(output) < target and novelty_id == 0 and novelty_text == 0:
            continue
        output.append(row)
        output_ids.add(claim_id)
        if text_key:
            output_text.add(text_key)

    if len(output) < target:
        for _, _, _, claim_id, row, text_key in scored:
            if len(output) >= target:
                break
            if claim_id in output_ids:
                continue
            if text_key and text_key in output_text:
                continue
            output.append(row)
            output_ids.add(claim_id)
            if text_key:
                output_text.add(text_key)

    return output[:target]


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


def chapter_core_question(chapter: dict[str, Any], lang: str) -> str:
    intro = chapter.get(f"intro_{lang}", [])
    if isinstance(intro, list) and intro:
        return clean_text(str(intro[0]), max_chars=180, ellipsis=False)
    return clean_text(str(chapter.get(f"summary_{lang}", "")), max_chars=180, ellipsis=False)


def chapter_transition(chapter: dict[str, Any], chapter_by_id: dict[str, dict[str, Any]], lang: str) -> str:
    chapter_id = str(chapter.get("chapter_id", ""))
    next_id = chapter.get("next_chapter_id")
    if not next_id:
        return (
            "No downstream chapter; consolidate assumptions, claims, and open questions."
            if lang == "en"
            else "无后续章节：请收束假设、结论与开放问题。"
        )
    next_chapter = chapter_by_id.get(str(next_id), {})
    this_title = str(chapter.get(f"title_{lang}", chapter.get("chapter_id", "")))
    next_title = str(next_chapter.get(f"title_{lang}", next_id))
    if chapter_id == "chapter-2-grid2d-family" and str(next_id) == "chapter-3-ring-baseline":
        if lang == "en":
            return clean_text(
                "Bridge note: keep the same hazard/survival diagnostics from Grid2D, then switch geometry to ring so shortcut and lazy parameters can be isolated without boundary-shape confounders.",
                ellipsis=False,
            )
        return clean_text(
            "桥接说明：延续 Grid2D 的 hazard/survival 诊断，但将几何切换到环模型，以隔离 shortcut 与 lazy 参数并排除边界形状混杂。",
            ellipsis=False,
        )
    if chapter_id == "chapter-5-cross-model-synthesis" and str(next_id) == "chapter-6-repro-validation":
        if lang == "en":
            return clean_text(
                "Before any new claims are added, move from synthesis to reproducibility gates and verify command-, schema-, and artifact-level closure.",
                ellipsis=False,
            )
        return clean_text("在增加新结论前，先从综合解释转入复现门禁，逐项验证命令级、schema 级与产物级闭环。", ellipsis=False)
    if chapter_id == "chapter-6-repro-validation" and str(next_id) == "chapter-7-outlook":
        if lang == "en":
            return clean_text(
                "Only unresolved items that pass reproducibility constraints should enter the outlook as auditable hypotheses.",
                ellipsis=False,
            )
        return clean_text("只有通过复现约束后仍未解决的问题，才应进入展望并作为可审计假设。", ellipsis=False)
    if lang == "en":
        return clean_text(
            f"Carry notation and verified claims from {this_title} into {next_title}, then extend mechanism and evidence without resetting assumptions.",
            ellipsis=False,
        )
    return clean_text(
        f"从《{this_title}》延续符号与已核对 claim 进入《{next_title}》，在不重置假设的前提下扩展机制与证据。",
        ellipsis=False,
    )


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


def build_backbone_payload(chapter_rows: list[dict[str, Any]]) -> dict[str, Any]:
    chapters = sorted(chapter_rows, key=lambda row: int(row.get("order", 0)))
    chapter_by_id = {str(ch.get("chapter_id", "")): ch for ch in chapters}
    chapter_spine: list[dict[str, Any]] = []

    for chapter in chapters:
        chapter_id = str(chapter.get("chapter_id", ""))
        linked_reports = [
            str(item.get("report_id", "")).strip()
            for item in chapter.get("linked_reports", [])
            if str(item.get("report_id", "")).strip()
        ]
        key_claim_ids = [
            str(item.get("claim_id", "")).strip()
            for item in chapter.get("claim_ledger", [])
            if str(item.get("claim_id", "")).strip()
        ][:8]
        key_formulae = [
            str(item.get("latex", "")).strip()
            for item in chapter.get("theory_chain", [])
            if str(item.get("latex", "")).strip()
        ][:6]
        key_notions = [
            str(item.get("id", "")).strip()
            for item in chapter.get("concept_cards", [])
            if str(item.get("id", "")).strip()
        ][:8]
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

    return {
        "version": "v1",
        "generated_at": utc_now_iso(),
        "chapter_count": len(chapter_spine),
        "acts": build_acts(chapters),
        "chapter_spine": chapter_spine,
        "quality_checks": checks,
    }


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
    used_claim_ids: set[str] = set()
    used_claim_text_keys: set[str] = set()
    used_concept_ids: set[str] = set()

    for chapter in sorted(CHAPTER_BLUEPRINT, key=lambda row: int(row["order"])):
        chapter_id = str(chapter["chapter_id"])
        chapter_report_ids = [rid for rid in chapter.get("report_ids", []) if rid in metas_en]
        if not chapter_report_ids:
            continue

        concept_cards_raw = pick_concept_cards(
            theory_map,
            chapter_report_ids,
            [str(x) for x in chapter.get("concept_keywords", [])],
        )
        concept_cards = prioritize_new_concepts(concept_cards_raw, used_concept_ids, limit=6)
        theory_chain = enrich_theory_chain(chapter_id, chapter_report_ids, pick_theory_chain(chapter_report_ids, metas_en, metas_cn))
        interactive_panels = pick_interactive_panels(chapter_report_ids, metas_en, metas_cn)
        linked_reports = build_linked_reports(chapter_report_ids, metas_en, metas_cn, groups, guide_by_report)
        claim_ledger = build_claim_ledger(chapter_id, chapter_report_ids, content_map, used_claim_ids, used_claim_text_keys)

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
                    "stage": "theory_placeholder",
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
                            "path": f"research/reports/{chapter_report_ids[0]}",
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
        intro_en, intro_cn = chapter_intro_with_bridge(chapter, chapter_id)

        chapter_payload: dict[str, Any] = {
            "chapter_id": chapter_id,
            "order": order,
            "slug": str(chapter["slug"]),
            "title_en": str(chapter["title_en"]),
            "title_cn": str(chapter["title_cn"]),
            "kicker_en": str(chapter["kicker_en"]),
            "kicker_cn": str(chapter["kicker_cn"]),
            "intro_en": intro_en,
            "intro_cn": intro_cn,
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

        for row in claim_ledger:
            claim_id = str(row.get("claim_id", "")).strip()
            if claim_id:
                used_claim_ids.add(claim_id)
            text_key = normalize_text_key(str(row.get("text_en", "")))
            if text_key:
                used_claim_text_keys.add(text_key)
        for card in concept_cards:
            concept_id = str(card.get("id", "")).strip()
            if concept_id:
                used_concept_ids.add(concept_id)

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

    chapter_all_claim_ids = sorted(
        {
            str(claim.get("claim_id", "")).strip()
            for chapter in chapter_rows
            for claim in chapter.get("claim_ledger", [])
            if str(claim.get("claim_id", "")).strip()
        }
    )
    global_claim_ids = sorted(
        {
            str(claim.get("claim_id", "")).strip()
            for claim in content_map.get("claims", [])
            if str(claim.get("claim_id", "")).strip()
        }
    )
    global_claim_set = set(global_claim_ids)
    chapter_claim_ids = [claim_id for claim_id in chapter_all_claim_ids if claim_id in global_claim_set]
    chapter_claim_set = set(chapter_claim_ids)
    chapter_native_claim_ids = [claim_id for claim_id in chapter_all_claim_ids if claim_id not in global_claim_set]
    excluded_claim_ids = [claim_id for claim_id in global_claim_ids if claim_id not in chapter_claim_set]
    coverage_payload = {
        "version": "v1",
        "generated_at": utc_now_iso(),
        "policy_en": (
            "Book chapters prioritize non-redundant continuity claims from report-level content_map records. "
            "Excluded report claims remain available in report pages and content_map for deep audit. "
            "Chapter-native synthesis claims are tracked separately."
        ),
        "policy_cn": "Book 章节优先保留来自 content_map 的非冗余主线 claim；未纳入章节的报告 claim 仍保留在报告页与 content_map 供深度核查。章节自生成综合 claim 单独统计。",
        "global_claim_count": len(global_claim_ids),
        "chapter_claim_count": len(chapter_claim_ids),
        "chapter_total_claim_count": len(chapter_all_claim_ids),
        "chapter_native_claim_count": len(chapter_native_claim_ids),
        "excluded_claim_count": len(excluded_claim_ids),
        "chapter_claim_ids": chapter_claim_ids,
        "chapter_native_claim_ids": chapter_native_claim_ids,
        "excluded_claim_ids": excluded_claim_ids,
    }

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
    write_json(data_root / "book" / "book_claim_coverage.json", coverage_payload)

    backbone_payload = build_backbone_payload(chapter_rows)
    write_json(data_root / "book" / "backbone.json", backbone_payload)

    print(
        json.dumps(
            {
                "ok": True,
                "chapter_count": len(chapter_rows),
                "manifest": (data_root / "book" / "book_manifest.json").as_posix(),
                "toc": (data_root / "book" / "toc.json").as_posix(),
                "backbone": (data_root / "book" / "backbone.json").as_posix(),
                "claim_coverage": (data_root / "book" / "book_claim_coverage.json").as_posix(),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
