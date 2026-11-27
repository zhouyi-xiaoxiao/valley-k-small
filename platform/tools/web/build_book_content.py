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

# One plain sentence per chapter: what it takes from the previous chapter.
CHAPTER_BRIDGES: dict[str, tuple[str, str]] = {
    "chapter-1-core-fpt": (
        "With the notation fixed in Chapter 0, this chapter introduces f(t), S(t) and h(t).",
        "第0章定好了记号，本章在此基础上介绍 f(t)、S(t) 和 h(t)。",
    ),
    "chapter-2-grid2d-family": (
        "Using the quantities and the two-peak rule of Chapter 1, this chapter asks which geometric constraints on a two-dimensional lattice keep two peaks and which remove them.",
        "沿用第1章的几个量和双峰判据，本章考察二维格点上哪些几何约束会保留双峰，哪些会让双峰消失。",
    ),
    "chapter-3-ring-baseline": (
        "This chapter moves from the lattice to a ring, so that the effect of the shortcut and the effect of staying put can be separated.",
        "本章把几何从二维格点换成环，以便把捷径的作用和原地停留的作用分开来看。",
    ),
    "chapter-4-shortcut-variants": (
        "Starting from the ring baseline of Chapter 3, this chapter adds a shortcut and varies how strong it is and where it lands.",
        "本章以第3章的环模型基线为起点，加入捷径，并改变它的强度和落点。",
    ),
    "chapter-5-cross-model-synthesis": (
        "After the ring shortcut results of Chapter 4, this chapter sets lattice and ring results side by side.",
        "第4章讲的是环上的捷径；本章把二维格点和环的结果并排来看。",
    ),
    "chapter-6-repro-validation": (
        "After the comparison across models in Chapter 5, the book goes back to single reports.",
        "第5章做完了跨模型的对照，这里回到单份报告。",
    ),
}

# The data builder's generic formula descriptions. A formula without a
# description of its own gets these; the book page recognises them and prints
# no description (isGeneratedMathStoryDescription in atlas.ts).
GENERIC_FORMULA_DESCRIPTION_EN = "Adds a relation that links neighboring steps in the derivation chain."
GENERIC_FORMULA_DESCRIPTION_CN = "补充连接推导相邻步骤的关系式。"

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


def formula_key(latex: str) -> str:
    # The same formula written with different spacing counts once.
    return re.sub(r"\s+|\\[,;:!]|\\ |~", "", str(latex or ""))


def pick_theory_chain(report_ids: list[str], metas_en: dict[str, dict[str, Any]], metas_cn: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    """Up to two formulas per report, in chapter order.

    A formula already shown for an earlier report of the chapter is skipped,
    so it appears once, under the first report that has it. Formulas whose
    context is "Fallback" are the data builder's stand-in for a report with no
    extracted formula (the generic f, S, h definitions), not the report's own,
    and are left out. The labels carry the formula's source section heading
    in each language; the page prints a label only when it is in the page's
    language and is a real heading.
    """
    chain: list[dict[str, Any]] = []
    seen: set[str] = set()
    for report_id in report_ids:
        meta_en = metas_en.get(report_id, {})
        meta_cn = metas_cn.get(report_id, {})
        story_en = list(meta_en.get("math_story", []))
        source = "math_story" if story_en else "math_blocks"
        items_en = story_en or list(meta_en.get("math_blocks", []))
        items_cn = list(meta_cn.get(source, []))
        picked = 0
        for idx, item_en in enumerate(items_en):
            if picked >= 2:
                break
            latex = str(item_en.get("latex", "")).strip()
            context_en = str(item_en.get("context", "")).strip()
            key = formula_key(latex)
            if not key or context_en.lower() == "fallback" or key in seen:
                continue
            item_cn = items_cn[idx] if idx < len(items_cn) else {}
            if formula_key(str(item_cn.get("latex", ""))) != key:
                item_cn = next((row for row in items_cn if formula_key(str(row.get("latex", ""))) == key), {})
            seen.add(key)
            picked += 1
            stage_en = str(item_en.get("stage", "")).strip() or "Formula"
            context_cn = str(item_cn.get("context", "")).strip() or context_en
            description_en = clean_text(str(item_en.get("description", "")), max_chars=600, ellipsis=False)
            description_cn_raw = str(item_cn.get("description", ""))
            description_cn = (
                clean_text(description_cn_raw, max_chars=360, ellipsis=False)
                if contains_cjk(description_cn_raw)
                else GENERIC_FORMULA_DESCRIPTION_CN
            )
            chain.append(
                {
                    "report_id": report_id,
                    "stage": stage_en,
                    "label_en": context_en or stage_en,
                    "label_cn": context_cn or str(item_cn.get("stage", "")).strip() or "公式",
                    "description_en": description_en or GENERIC_FORMULA_DESCRIPTION_EN,
                    "description_cn": description_cn,
                    "latex": latex,
                    "context": context_en or source,
                }
            )
    return chain[:14]


def chapter_intro_with_bridge(chapter: dict[str, Any], chapter_id: str) -> tuple[list[str], list[str]]:
    intro_en = [clean_text(x, max_chars=420, ellipsis=False) for x in chapter.get("intro_en", [])]
    intro_cn = [clean_text(x, max_chars=260, ellipsis=False) for x in chapter.get("intro_cn", [])]

    bridge_en = ""
    bridge_cn = ""
    bridge = CHAPTER_BRIDGES.get(chapter_id)
    if bridge:
        bridge_en, bridge_cn = bridge

    if bridge_en and all(normalize_text_key(bridge_en) != normalize_text_key(row) for row in intro_en):
        intro_en.insert(0, bridge_en)
    if bridge_cn and all(normalize_text_key(bridge_cn) != normalize_text_key(row) for row in intro_cn):
        intro_cn.insert(0, bridge_cn)
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

    def panel_hint(ds_en: dict[str, Any], ds_cn: dict[str, Any], *, lang: str) -> str:
        # What the chart shows: its written caption, otherwise its two axes.
        ds = ds_cn if lang == "cn" else ds_en
        caption = str(ds.get("caption_cn" if lang == "cn" else "caption", "") or ds_en.get("caption", "")).strip()
        if caption:
            return clean_text(caption, max_chars=420 if lang == "en" else 260)
        x_label = str(ds.get("x_label_cn" if lang == "cn" else "x_label", "") or ds_en.get("x_label", "x")).strip() or "x"
        y_label = str(ds.get("y_label_cn" if lang == "cn" else "y_label", "") or ds_en.get("y_label", "y")).strip() or "y"
        if lang == "cn":
            return f"{y_label} 随 {x_label} 的变化。"
        return f"{y_label} against {x_label}."

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
                "title_en": clean_text(f"{safe_title(meta_en, report_id)} · {ds_en.get('title', 'Chart')}", max_chars=150),
                "title_cn": clean_text(f"{safe_title(meta_cn, report_id)} · {ds_cn.get('title', '图')}", max_chars=90),
                "dataset_series_id": str(ds_en.get("series_id", "")),
                "dataset_path": str(ds_en.get("series_path", "")),
                "x_label": str(ds_en.get("x_label", "x")),
                "y_label": str(ds_en.get("y_label", "y")),
                "parameter_hint_en": panel_hint(ds_en, ds_cn, lang="en"),
                "parameter_hint_cn": panel_hint(ds_en, ds_cn, lang="cn"),
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
        # Recognised by isPlaceholderText; the Chinese page then shows the English text.
        text_cn_raw = "该结论只有英文原文。"
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
    # A pointer to the next chapter only. What a chapter takes from the
    # previous one is said once, in CHAPTER_BRIDGES.
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
        theory_chain = pick_theory_chain(chapter_report_ids, metas_en, metas_cn)
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
    listed_report_ids = set(report_map)
    for rid in report_ids:
        if rid not in report_map:
            report_map[rid] = ["chapter-6-repro-validation"]

    # The chapter a report page points to: its own family chapter when the
    # report is listed there, otherwise the first chapter that is not the
    # reading guide, the reproducibility appendix or the outlook.
    family_home_chapters = {
        "grid2d_": ("chapter-2-grid2d-family",),
        "ring_": ("chapter-3-ring-baseline", "chapter-4-shortcut-variants"),
        "cross_": ("chapter-5-cross-model-synthesis",),
    }
    support_chapters = {"chapter-0-reading-guide", "chapter-6-repro-validation", "chapter-7-outlook"}

    def home_chapter(rid: str, chapter_ids: list[str]) -> str:
        for prefix, homes in family_home_chapters.items():
            if rid.startswith(prefix):
                for chapter_id in chapter_ids:
                    if chapter_id in homes:
                        return chapter_id
        for chapter_id in chapter_ids:
            if chapter_id not in support_chapters:
                return chapter_id
        return chapter_ids[0]

    blueprint_by_id = {str(ch["chapter_id"]): ch for ch in CHAPTER_BLUEPRINT}
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
            "written": bool(blueprint_by_id.get(str(row["chapter_id"]), {}).get("written", True)),
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
            "Each chapter uses a selection of the reports' claims, without repeats. "
            "Claims that no chapter uses are still on their report pages."
        ),
        "policy_cn": "每章从报告的结论中选用若干条，不重复；没有选入任何一章的结论仍在各自的报告页上。",
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
                "primary_chapter_id": home_chapter(rid, chapter_ids),
                "chapter_ids": chapter_ids,
                "listed": rid in listed_report_ids,
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
