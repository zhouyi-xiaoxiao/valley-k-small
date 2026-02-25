#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from report_registry import load_registry


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = REPO_ROOT / "site" / "public" / "data" / "v1"
DEFAULT_ARTIFACTS_DIR = REPO_ROOT / "site" / "public" / "artifacts"
TEXT_EXT = {".md", ".tex", ".txt"}
FIGURE_EXT = {".pdf", ".png", ".svg", ".jpg", ".jpeg", ".webp"}
DATA_EXT = {".json", ".csv", ".npz"}
MODEL_HINTS = ("model", "problem", "definition", "setup", "convention", "模型", "定义", "设定")
METHOD_HINTS = ("method", "analytic", "inversion", "algorithm", "scan", "protocol", "derivation", "方法", "推导", "验证")
RESULT_HINTS = ("finding", "result", "conclusion", "summary", "结论", "结果", "总结")
REPRO_HINTS = ("reproducibility", "command", "命令", "复现")
LATEX_SYMBOL_REPLACEMENTS = {
    r"\dots": "...",
    r"\cdots": "...",
    r"\to": "->",
    r"\mapsto": "=>",
    r"\times": "×",
    r"\cdot": "·",
    r"\pm": "±",
    r"\geq": "≥",
    r"\leq": "≤",
    r"\neq": "≠",
    r"\infty": "∞",
    r"\alpha": "alpha",
    r"\beta": "beta",
    r"\gamma": "gamma",
    r"\lambda": "lambda",
    r"\mu": "mu",
    r"\sigma": "sigma",
}
CLAIM_STOPWORDS = {
    "the",
    "and",
    "for",
    "with",
    "that",
    "this",
    "from",
    "into",
    "under",
    "over",
    "into",
    "via",
    "are",
    "is",
    "was",
    "were",
    "as",
    "of",
    "to",
    "in",
    "on",
    "at",
    "by",
    "or",
    "an",
    "a",
    "can",
    "be",
    "which",
    "using",
    "used",
    "show",
    "shows",
    "report",
    "结果",
    "结论",
    "研究",
    "模型",
    "方法",
    "通过",
    "以及",
    "并且",
    "可以",
    "用于",
}


def normalize_space(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def dedupe_preserve(items: list[str], *, max_items: int) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for raw in items:
        val = normalize_space(raw)
        if not val:
            continue
        key = re.sub(r"[^a-z0-9]+", "", val.lower())
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(val)
        if len(out) >= max_items:
            break
    return out


def contains_cjk(text: str) -> bool:
    return bool(re.search(r"[\u4e00-\u9fff]", text))


def is_placeholder_finding(text: str, report_id: str) -> bool:
    lowered = normalize_space(text).lower()
    if not lowered:
        return True
    patterns = [
        f"see {report_id.lower()} report assets for detailed findings",
        "see report assets for detailed findings",
        "fallback narrative card",
    ]
    if any(p in lowered for p in patterns):
        return True
    if lowered.startswith("see ") and "report assets" in lowered:
        return True
    return False


def clean_findings(findings: list[str], report_id: str, max_items: int = 8) -> list[str]:
    normalized = dedupe_preserve(findings, max_items=max(12, max_items * 2))
    kept = [item for item in normalized if not is_placeholder_finding(item, report_id)]
    if not kept:
        kept = [
            f"Core derivation and reproducible evidence are available for {report_id}; "
            "see the mathematical logic chain and interactive datasets on this page."
        ]
    return dedupe_preserve(kept, max_items=max_items)


def strip_tex_comments(text: str) -> str:
    return re.sub(r"(?<!\\)%.*", "", text)


def polish_extracted_text(text: str) -> str:
    value = normalize_space(text)
    if not value:
        return ""
    value = value.replace("``", '"').replace("''", '"')
    value = value.replace("`", "")
    value = value.replace("~", " ")
    value = value.replace("\\", " ")
    value = value.replace("_", " ")
    value = re.sub(r"\b(itemize|enumerate|figure|table|align|equation)\b", " ", value, flags=re.IGNORECASE)
    value = re.sub(r"\[\s*\]", " ", value)
    value = re.sub(r"\(\s*\)", " ", value)
    value = re.sub(r"\s+([,.;:)\]])", r"\1", value)
    value = re.sub(r"([(\[])\s+", r"\1", value)
    value = normalize_space(value)
    return value


def latex_to_plain(text: str) -> str:
    value = strip_tex_comments(text)
    for source, target in LATEX_SYMBOL_REPLACEMENTS.items():
        value = value.replace(source, target)
    value = value.replace("\\,", " ")
    value = value.replace("\\;", " ")
    value = value.replace("\\!", " ")
    value = value.replace("\\left", " ")
    value = value.replace("\\right", " ")
    value = value.replace("\\,", " ")
    value = value.replace("\\quad", " ")
    value = value.replace("\\qquad", " ")
    for _ in range(8):
        updated = re.sub(r"\\frac\{([^{}]{1,120})\}\{([^{}]{1,120})\}", r"(\1)/(\2)", value)
        if updated == value:
            break
        value = updated
    value = re.sub(r"\\sqrt\{([^{}]{1,120})\}", r"sqrt(\1)", value)
    value = re.sub(
        r"\\begin\{(?:figure|table|longtable|tabular|verbatim|lstlisting)\*?\}.*?\\end\{(?:figure|table|longtable|tabular|verbatim|lstlisting)\*?\}",
        " ",
        value,
        flags=re.DOTALL,
    )
    value = re.sub(r"\\(begin|end)\{[^{}]+\}(?:\[[^\]]*\])?", " ", value)
    value = re.sub(r"\\(section|subsection|subsubsection|paragraph)\*?\{([^{}]*)\}", r" \2 ", value)
    value = re.sub(r"\\item\b", " ", value)
    value = re.sub(r"\\[a-zA-Z]+\*?(?:\[[^\]]*\])?\{([^{}]*)\}", r" \1 ", value)
    value = re.sub(r"\\[a-zA-Z]+\*?", " ", value)
    value = re.sub(r"\$([^$]{1,240})\$", r" \1 ", value)
    value = re.sub(r"[{}]", " ", value)
    return polish_extracted_text(value)


def summarize_plain(text: str, *, max_chars: int = 320) -> str:
    plain = normalize_space(text)
    if len(plain) <= max_chars:
        return plain
    clipped = plain[: max_chars + 1]
    stop = max(clipped.rfind(". "), clipped.rfind("。"), clipped.rfind("; "), clipped.rfind("；"))
    if stop < int(max_chars * 0.5):
        stop = max_chars
    return clipped[:stop].rstrip(" ,;。；") + "…"


def canonical_summary(text: str, *, max_chars: int = 1200) -> str:
    """
    Canonical summary text for meta payloads.
    Keep complete prose where possible and avoid terminal ellipsis.
    """
    plain = normalize_space(text).replace("…", "")
    if len(plain) <= max_chars:
        return plain
    clipped = plain[: max_chars + 1]
    stop = max(clipped.rfind(". "), clipped.rfind("。"), clipped.rfind("; "), clipped.rfind("；"))
    if stop >= int(max_chars * 0.6):
        return clipped[: stop + 1].rstrip(" ,;。；")
    return clipped[:max_chars].rstrip(" ,;。；")


def is_placeholder_section_summary(heading: str, summary: str) -> bool:
    normalized = normalize_space(summary)
    if not normalized:
        return True
    lowered = normalized.lower()
    heading_key = normalize_finding_key(heading)
    summary_key = normalize_finding_key(normalized)
    if heading_key and summary_key == heading_key:
        return True
    if re.search(r"section summary\.?$", lowered):
        return True
    if "fallback narrative card" in lowered:
        return True
    if lowered in {"overview.", "introduction.", "methods.", "results.", "discussion."}:
        return True
    if len(normalized) < 18:
        return True
    return False


def parse_tex_title(tex_text: str) -> str:
    m = re.search(r"\\title\{(.*?)\}", tex_text, flags=re.DOTALL)
    if not m:
        return ""
    return summarize_plain(latex_to_plain(m.group(1)), max_chars=140)


def parse_tex_abstract(tex_text: str) -> str:
    m = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", tex_text, flags=re.DOTALL)
    if not m:
        return ""
    return canonical_summary(latex_to_plain(m.group(1)), max_chars=1200)


def pick_main_tex_path(item: dict[str, Any], report_dir: Path, lang: str) -> Path | None:
    candidates = [str(x) for x in item.get("main_tex", []) if str(x).endswith(".tex")]
    ranked: list[str] = []
    lang_tag = f"_{lang}"
    ranked.extend([name for name in candidates if lang_tag in name])
    if lang == "en":
        ranked.extend([name for name in candidates if "_cn" not in name])
    ranked.extend(candidates)

    seen: set[str] = set()
    for rel in ranked:
        if rel in seen:
            continue
        seen.add(rel)
        path = report_dir / rel
        if path.exists():
            return path

    fallback = sorted(p for p in report_dir.rglob("*.tex") if p.is_file() and "build" not in p.parts)
    return fallback[0] if fallback else None


def split_sections(tex_text: str) -> list[dict[str, Any]]:
    pattern = re.compile(r"\\section\*?\{([^{}]+)\}")
    matches = list(pattern.finditer(tex_text))
    if not matches:
        return []

    sections: list[dict[str, Any]] = []
    for idx, match in enumerate(matches):
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(tex_text)
        title = normalize_space(latex_to_plain(match.group(1)))
        body = tex_text[start:end]
        if not title:
            continue
        body_plain = latex_to_plain(body)
        sections.append(
            {
                "title": title,
                "start": start,
                "end": end,
                "summary": summarize_plain(body_plain, max_chars=340),
                "body": body,
            }
        )
    return sections


def section_title_for_index(sections: list[dict[str, Any]], index: int) -> str:
    for section in sections:
        if int(section["start"]) <= index < int(section["end"]):
            return str(section["title"])
    if sections:
        return str(sections[0]["title"])
    return "Overview"


def extract_itemize_lines(text: str, *, limit: int = 10) -> list[str]:
    findings: list[str] = []
    for block in re.finditer(r"\\begin\{itemize\}(.*?)\\end\{itemize\}", text, flags=re.DOTALL):
        part = block.group(1)
        for raw in re.findall(r"\\item\s+(.*?)(?=(\\item|$))", part, flags=re.DOTALL):
            cleaned = summarize_plain(latex_to_plain(raw[0]), max_chars=220)
            if cleaned:
                findings.append(cleaned)
            if len(findings) >= limit:
                return findings
    return findings


def extract_findings_from_sections(sections: list[dict[str, Any]]) -> list[str]:
    findings: list[str] = []
    for section in sections:
        title_lower = str(section["title"]).lower()
        if not any(key in title_lower for key in RESULT_HINTS):
            continue
        findings.extend(extract_itemize_lines(str(section["body"]), limit=8))
        if len(findings) < 8:
            findings.append(str(section["summary"]))
    return dedupe_preserve(findings, max_items=8)


def extract_repro_commands(tex_text: str, sections: list[dict[str, Any]]) -> list[str]:
    commands: list[str] = []
    target_ranges: list[tuple[int, int]] = []
    for section in sections:
        title_lower = str(section["title"]).lower()
        if any(key in title_lower for key in REPRO_HINTS):
            target_ranges.append((int(section["start"]), int(section["end"])))

    search_space = tex_text
    if target_ranges:
        chunks = [tex_text[start:end] for start, end in target_ranges]
        search_space = "\n".join(chunks)

    commands.extend(re.findall(r"\\path\{([^{}]+)\}", search_space))
    commands.extend(re.findall(r"\\texttt\{([^{}]*?(?:python|pytest|npm|reportctl)[^{}]*)\}", search_space))
    commands.extend(re.findall(r"(python3?\s+[^\n\\]+)", latex_to_plain(search_space)))

    cleaned = []
    for cmd in commands:
        text = normalize_space(cmd.strip())
        if not text:
            continue
        if len(text) > 220:
            continue
        cleaned.append(text)
    return dedupe_preserve(cleaned, max_items=10)


def classify_formula_stage(latex: str, context: str, lang: str) -> tuple[str, str]:
    lowered = latex.lower()
    context_lower = context.lower()
    if "p_{t+1}" in lowered or "p(t+1)" in lowered or "b p" in lowered:
        return (
            ("Markov Update", "马尔可夫更新")[lang == "cn"],
            (
                "Advances state probability by one step through the transition operator.",
                "通过转移算子推进一步状态概率更新。",
            )[lang == "cn"],
        )
    if "f(t)" in lowered or "\\pr" in lowered:
        return (
            ("Distribution Setup", "分布定义")[lang == "cn"],
            (
                "Defines first-passage probability objects used by later diagnostics.",
                "定义后续诊断所依赖的首达时间概率对象。",
            )[lang == "cn"],
        )
    if "s(t)" in lowered or "survival" in lowered:
        return (
            ("Survival Link", "生存函数联系")[lang == "cn"],
            (
                "Connects probability mass to survival dynamics over time.",
                "连接概率质量与随时间演化的生存过程。",
            )[lang == "cn"],
        )
    if "h(t)" in lowered or "hazard" in lowered:
        return (
            ("Hazard Interpretation", "风险率解释")[lang == "cn"],
            (
                "Converts PMF and survival into a peak/valley-sensitive hazard view.",
                "将 PMF 与生存函数转化为对峰谷敏感的风险率视角。",
            )[lang == "cn"],
        )
    if "\\beta" in lowered or "beta" in lowered or ("u\\to" in lowered and "v" in lowered):
        return (
            ("Shortcut Perturbation", "shortcut 扰动")[lang == "cn"],
            (
                "Captures how shortcut intensity changes transition balance.",
                "刻画 shortcut 强度如何改变转移平衡。",
            )[lang == "cn"],
        )
    if "\\lambda" in lowered or "eigen" in lowered or "\\sum" in lowered or "fft" in lowered:
        return (
            ("Spectral / Inversion Step", "谱分解 / 反演步骤")[lang == "cn"],
            (
                "Provides analytic inversion machinery for computing trajectories.",
                "提供用于计算轨迹分布的解析反演机制。",
            )[lang == "cn"],
        )
    if "model" in context_lower or "definition" in context_lower:
        return (
            ("Model Constraint", "模型约束")[lang == "cn"],
            (
                "States the structural constraints and parameter ranges of the model.",
                "给出模型结构约束与参数范围。",
            )[lang == "cn"],
        )
    return (
        ("Derivation Link", "推导连接")[lang == "cn"],
        (
            "Adds a relation that links neighboring steps in the derivation chain.",
            "补充连接推导相邻步骤的关系式。",
        )[lang == "cn"],
    )


def build_math_story(math_blocks: list[dict[str, str]], lang: str) -> list[dict[str, str]]:
    story: list[dict[str, str]] = []
    for block in math_blocks:
        context = str(block.get("context", "Overview"))
        stage, description = classify_formula_stage(str(block.get("latex", "")), context, lang)
        story.append(
            {
                "stage": stage,
                "description": description,
                "latex": str(block.get("latex", "")),
                "context": context,
            }
        )
    trimmed = story[:6]
    if trimmed:
        return trimmed
    return [
        {
            "stage": ("Fallback Chain", "兜底逻辑链")[lang == "cn"],
            "description": (
                "Base FPT relation retained when no explicit formula block is detected.",
                "在未提取到显式公式时保留基础首达时间关系。",
            )[lang == "cn"],
            "latex": r"f(t)=\Pr[T=t],\quad S(t)=\Pr[T>t],\quad h(t)=\frac{f(t)}{S(t-1)}",
            "context": "Fallback",
        }
    ]


def extract_math_blocks(tex_text: str, sections: list[dict[str, Any]], source_path: str, lang: str) -> list[dict[str, str]]:
    candidates: list[tuple[str, int]] = []
    env_pattern = re.compile(
        r"\\begin\{(equation\*?|align\*?|gather\*?|multline\*?)\}(.*?)\\end\{\1\}",
        flags=re.DOTALL,
    )
    for match in env_pattern.finditer(tex_text):
        latex = normalize_space(match.group(2))
        if latex:
            candidates.append((latex, match.start()))

    for match in re.finditer(r"\\\[(.*?)\\\]", tex_text, flags=re.DOTALL):
        latex = normalize_space(match.group(1))
        if latex:
            candidates.append((latex, match.start()))

    for match in re.finditer(r"\$([^$\n]{8,180})\$", tex_text):
        latex = normalize_space(match.group(1))
        if latex and ("=" in latex or "\\Pr" in latex or "\\sum" in latex):
            candidates.append((latex, match.start()))

    blocks: list[dict[str, str]] = []
    seen: set[str] = set()
    for latex, idx in sorted(candidates, key=lambda row: row[1]):
        cleaned = sanitize_latex_for_katex(latex)
        if not cleaned:
            continue
        if is_trivial_formula_signature(cleaned):
            continue
        signature = re.sub(r"[^a-z0-9]+", "", cleaned.lower())
        if not signature or signature in seen:
            continue
        seen.add(signature)
        blocks.append(
            {
                "latex": cleaned,
                "context": section_title_for_index(sections, idx),
                "source_path": source_path,
                "lang": lang,
            }
        )
        if len(blocks) >= 14:
            break

    if not blocks:
        blocks.append(
            {
                "latex": r"f(t)=\Pr[T=t],\quad S(t)=\Pr[T>t],\quad h(t)=\frac{f(t)}{S(t-1)}",
                "context": "Fallback",
                "source_path": source_path,
                "lang": lang,
            }
        )
    return blocks


def pick_narrative_summary(sections: list[dict[str, Any]], hints: tuple[str, ...], fallback: str) -> str:
    for section in sections:
        title_lower = str(section["title"]).lower()
        if any(h in title_lower for h in hints):
            return str(section["summary"])
    if sections:
        return str(sections[0]["summary"])
    return fallback


def build_narrative_fields(sections: list[dict[str, Any]], fallback: str) -> dict[str, str]:
    model = pick_narrative_summary(sections, MODEL_HINTS, fallback)
    method = pick_narrative_summary(sections, METHOD_HINTS, fallback)
    result = pick_narrative_summary(sections, RESULT_HINTS, fallback)
    values = [model, method, result]
    if len({normalize_finding_key(v) for v in values if v}) >= 2:
        return {
            "model_overview": model,
            "method_overview": method,
            "result_overview": result,
        }

    section_summaries = [
        str(section.get("summary", fallback))
        for section in sections
        if section.get("summary")
        and not is_placeholder_section_summary(str(section.get("title", "")), str(section.get("summary", "")))
    ]
    while len(section_summaries) < 3:
        section_summaries.append(fallback)
    return {
        "model_overview": section_summaries[0],
        "method_overview": section_summaries[1],
        "result_overview": section_summaries[2],
    }


def extract_tex_story(item: dict[str, Any], report_dir: Path, report_id: str, lang: str) -> dict[str, Any]:
    tex_path = pick_main_tex_path(item, report_dir, lang)
    if not tex_path or not tex_path.exists():
        fallback_source = str(item.get("path", report_id))
        fallback_math = [
            {
                "latex": r"f(t)=\Pr[T=t]",
                "context": "Fallback",
                "source_path": fallback_source,
                "lang": lang,
            }
        ]
        return {
            "title": "",
            "summary": "",
            "section_cards": [
                {
                    "heading": "Overview",
                    "summary": f"Fallback narrative card for {report_id}.",
                    "source_path": fallback_source,
                }
            ],
            "math_blocks": fallback_math,
            "math_story": build_math_story(fallback_math, lang),
            "findings": [],
            "reproducibility_commands": [],
            "narrative": {
                "model_overview": f"Model summary placeholder for {report_id}.",
                "method_overview": f"Method summary placeholder for {report_id}.",
                "result_overview": f"Result summary placeholder for {report_id}.",
            },
            "source_documents": [fallback_source],
        }

    raw = tex_path.read_text(encoding="utf-8", errors="ignore")
    sections = split_sections(raw)
    abstract = parse_tex_abstract(raw)
    summary_fallback = canonical_summary(
        abstract or (sections[0]["summary"] if sections else f"Research report {report_id}."),
        max_chars=1200,
    )
    section_cards: list[dict[str, str]] = []
    for section in sections[:10]:
        heading = str(section["title"])
        summary = normalize_space(str(section.get("summary", "")))
        if is_placeholder_section_summary(heading, summary):
            body_candidate = summarize_plain(latex_to_plain(str(section.get("body", ""))), max_chars=240)
            summary = normalize_space(body_candidate)
        if is_placeholder_section_summary(heading, summary):
            summary = summarize_plain(summary_fallback, max_chars=240)
        section_cards.append(
            {
                "heading": heading,
                "summary": summary,
                "source_path": rel_repo_path(tex_path),
            }
        )
    findings = extract_findings_from_sections(sections)
    math_blocks = extract_math_blocks(raw, sections, rel_repo_path(tex_path), lang)
    math_story = build_math_story(math_blocks, lang)
    if not section_cards:
        section_cards = [
            {
                "heading": "Overview",
                "summary": summarize_plain(summary_fallback, max_chars=340),
                "source_path": rel_repo_path(tex_path),
            }
        ]
    return {
        "title": parse_tex_title(raw),
        "summary": canonical_summary(summary_fallback, max_chars=1200),
        "section_cards": section_cards,
        "math_blocks": math_blocks,
        "math_story": math_story,
        "findings": findings,
        "reproducibility_commands": extract_repro_commands(raw, sections),
        "narrative": build_narrative_fields(sections, summary_fallback),
        "source_documents": [rel_repo_path(tex_path)],
    }


def utc_now_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat().replace("+00:00", "Z")


def iso_from_timestamp(ts: float) -> str:
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat().replace("+00:00", "Z")


def detect_report_updated_at(report_dir: Path, fallback_iso: str) -> str:
    latest_ts = 0.0
    for path in report_dir.rglob("*"):
        if not path.is_file():
            continue
        if "build" in path.parts or "__pycache__" in path.parts or ".venv" in path.parts:
            continue
        try:
            latest_ts = max(latest_ts, float(path.stat().st_mtime))
        except OSError:
            continue
    if latest_ts <= 0:
        return fallback_iso
    return iso_from_timestamp(latest_ts)


def normalize_finding_key(text: str) -> str:
    raw = normalize_space(text)
    if not raw:
        return ""
    raw = re.sub(r"`", "", raw)
    raw = raw.replace("\\", "")
    raw = re.sub(r"\s+", " ", raw)
    raw = re.sub(r"[^\w]+", "", raw.lower(), flags=re.UNICODE)
    return raw


def is_trivial_formula_signature(latex: str) -> bool:
    compact = re.sub(r"\s+", "", normalize_space(latex))
    if not compact:
        return True
    if len(normalize_finding_key(compact)) < 10:
        return True
    if re.fullmatch(r"[A-Za-z\\_{}0-9]+=[-+]?\d+(?:\.\d+)?", compact):
        return True
    if re.fullmatch(r"\\text\{[^{}]+\}=\\text\{[^{}]+\}", compact):
        return True
    if re.fullmatch(r"[A-Za-z\\_{}]+=\d+e-?\d+", compact, flags=re.IGNORECASE):
        return True
    token_count = len(re.findall(r"[A-Za-z]+|\\[A-Za-z]+", compact))
    if "=" in compact and token_count <= 2 and re.search(r"\d", compact):
        return True
    return False


def tokenize_claim_text(text: str) -> set[str]:
    tokens = re.findall(r"[a-zA-Z0-9_]+|[\u4e00-\u9fff]{1,4}", normalize_space(text).lower())
    out: set[str] = set()
    for tok in tokens:
        if len(tok) < 2:
            continue
        if tok in CLAIM_STOPWORDS:
            continue
        out.add(tok)
    return out


def looks_like_path_finding(text: str) -> bool:
    lowered = text.lower()
    if lowered.startswith("see ") and "report assets" in lowered:
        return True
    if lowered.startswith("figures:") or lowered.startswith("environment:"):
        return True
    return bool(re.search(r"(?:reports|figures|config|code|scripts)/", lowered))


def enforce_unique_key_findings(output_dir: Path, report_ids: list[str]) -> list[dict[str, Any]]:
    key_to_reports: dict[str, set[str]] = defaultdict(set)
    payloads: dict[tuple[str, str], dict[str, Any]] = {}

    for report_id in report_ids:
        for meta_name in ("meta.json", "meta.cn.json"):
            path = output_dir / "reports" / report_id / meta_name
            if not path.exists():
                continue
            payload = json.loads(path.read_text(encoding="utf-8"))
            payloads[(report_id, meta_name)] = payload
            for finding in payload.get("key_findings", []):
                text = normalize_space(str(finding))
                if not text or looks_like_path_finding(text):
                    continue
                key = normalize_finding_key(text)
                if key:
                    key_to_reports[key].add(report_id)

    duplicate_keys = {key for key, reports in key_to_reports.items() if len(reports) > 1}
    if not duplicate_keys:
        return []

    details: list[dict[str, Any]] = []
    for key in sorted(duplicate_keys):
        details.append({"key": key, "report_ids": sorted(key_to_reports[key])})

    for (report_id, meta_name), payload in payloads.items():
        findings = list(payload.get("key_findings", []))
        changed = False
        new_findings: list[str] = []
        for finding in findings:
            text = normalize_space(str(finding))
            if not text or looks_like_path_finding(text):
                new_findings.append(text)
                continue
            key = normalize_finding_key(text)
            if key in duplicate_keys and f"[{report_id}]" not in text:
                text = f"{text} [{report_id}]"
                changed = True
            new_findings.append(text)

        if changed:
            payload["key_findings"] = dedupe_preserve(new_findings, max_items=8)
            path = output_dir / "reports" / report_id / meta_name
            path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")

    return details


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(1024 * 1024)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def infer_group(report_id: str) -> str:
    if report_id.startswith("ring_"):
        return "ring"
    if report_id.startswith("grid2d_"):
        return "grid2d"
    if report_id.startswith("cross_"):
        return "cross"
    return "misc"


def parse_readme(report_dir: Path, report_id: str) -> tuple[str, str, list[str]]:
    readme = report_dir / "README.md"
    if not readme.exists():
        title = report_id.replace("_", " ")
        summary = f"Interactive summary for {report_id}."
        findings = [f"This report ({report_id}) is included in the online atlas."]
        return title, summary, findings

    text = readme.read_text(encoding="utf-8", errors="ignore")
    lines = [line.rstrip() for line in text.splitlines()]

    title = report_id.replace("_", " ")
    for line in lines:
        if line.startswith("#"):
            title = line.lstrip("#").strip()
            break

    summary = ""
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#") or stripped.startswith("-"):
            continue
        summary = stripped
        break
    if not summary:
        summary = f"Research report {report_id}."
    summary = canonical_summary(summary, max_chars=1200)

    findings: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("- "):
            findings.append(stripped[2:].strip())
        if len(findings) >= 6:
            break
    if not findings:
        findings = [f"See {report_id} report assets for detailed findings."]

    return title, summary, dedupe_preserve(findings, max_items=8)


def rel_repo_path(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def clean_output_dir(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def git_changed_paths() -> list[str]:
    commands = [
        ["git", "diff", "--name-only", "HEAD~1..HEAD"],
        ["git", "diff", "--name-only", "HEAD"],
    ]
    for cmd in commands:
        proc = subprocess.run(
            cmd,
            cwd=REPO_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        if proc.returncode == 0 and proc.stdout.strip():
            return [line.strip() for line in proc.stdout.splitlines() if line.strip()]
    return []


def detect_changed_reports(registry: list[dict[str, Any]]) -> set[str]:
    changed = git_changed_paths()
    if not changed:
        return {item["id"] for item in registry}

    if "reports/report_registry.yaml" in changed:
        return {item["id"] for item in registry}

    matched: set[str] = set()
    for rel in changed:
        for item in registry:
            report_path = str(item["path"]).rstrip("/") + "/"
            if rel.startswith(report_path):
                matched.add(item["id"])
    if matched:
        return matched
    # If only pipeline/UI code changed, regenerate all reports to avoid empty payloads in clean CI.
    return {item["id"] for item in registry}


def copy_asset(
    src: Path,
    report_id: str,
    report_dir: Path,
    artifacts_dir: Path,
    *,
    no_copy_assets: bool,
) -> tuple[str, str]:
    rel_inside = src.relative_to(report_dir)
    web_path = f"/artifacts/{report_id}/{rel_inside.as_posix()}"
    source_path = rel_repo_path(src)
    if not no_copy_assets:
        dst = artifacts_dir / report_id / rel_inside
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    return web_path, source_path


def asset_kind(path: Path) -> str:
    ext = path.suffix.lower()
    if ext == ".pdf":
        return "pdf"
    if ext == ".tex":
        return "tex"
    if ext in FIGURE_EXT:
        return "figure"
    if ext in DATA_EXT:
        return "data"
    return "other"


def gather_files(report_dir: Path, extensions: set[str], max_items: int) -> list[Path]:
    files = [
        p
        for p in report_dir.rglob("*")
        if p.is_file()
        and p.suffix.lower() in extensions
        and "build" not in p.parts
        and "__pycache__" not in p.parts
        and ".venv" not in p.parts
    ]
    files.sort(key=lambda p: p.as_posix())
    return files[:max_items]


def disambiguate_asset_labels(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    taken: set[tuple[str, str]] = set()
    for record in records:
        kind = str(record.get("kind", "other"))
        label = str(record.get("label", "")).strip() or "asset"
        key = (kind, label.lower())
        if key not in taken:
            record["label"] = label
            taken.add(key)
            continue

        source_path = str(record.get("source_path", ""))
        parts = list(Path(source_path).parts)
        if len(parts) >= 2 and parts[0] == "reports":
            parts = parts[2:]
        parent_parts = [p for p in parts[:-1] if p]

        candidate = ""
        for depth in range(1, min(6, len(parent_parts)) + 1):
            context = "/".join(parent_parts[-depth:])
            trial = f"{context}/{label}"
            if (kind, trial.lower()) not in taken:
                candidate = trial
                break

        if not candidate:
            suffix = 2
            while True:
                trial = f"{label} ({suffix})"
                if (kind, trial.lower()) not in taken:
                    candidate = trial
                    break
                suffix += 1

        record["label"] = candidate
        taken.add((kind, candidate.lower()))
    return records


def disambiguate_figure_titles(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    taken: set[str] = set()
    for record in records:
        title = normalize_space(str(record.get("title", ""))) or "figure"
        if title.lower() not in taken:
            record["title"] = title
            taken.add(title.lower())
            continue

        source_path = str(record.get("source_path", ""))
        parts = list(Path(source_path).parts)
        if len(parts) >= 2 and parts[0] == "reports":
            parts = parts[2:]
        parent_parts = [p for p in parts[:-1] if p]
        context = "/".join(parent_parts[-2:]) if parent_parts else "variant"
        candidate = f"{title} ({context})"
        suffix = 2
        while candidate.lower() in taken:
            candidate = f"{title} ({context}, {suffix})"
            suffix += 1
        record["title"] = candidate
        taken.add(candidate.lower())
    return records


def infer_series_type(name: str, values: list[float]) -> str:
    lowered = name.lower()
    finite_values = [float(v) for v in values if isinstance(v, (int, float)) and math.isfinite(float(v))]
    unique_values = sorted({round(v, 10) for v in finite_values})

    if unique_values and set(unique_values).issubset({0.0, 1.0}):
        return "binary"
    if re.search(r"(flag|indicator|bool|pass|fail|is_)", lowered):
        return "binary"
    if re.search(r"(pmf|cdf|prob|mass|survival|hazard|density|ratio|rate|share)", lowered):
        return "probability"
    # Ambiguous tokens like n/t/k are often true metrics in this corpus.
    if lowered in {"n", "t", "k"}:
        if finite_values:
            span = max(finite_values) - min(finite_values)
            if span > 2 or len(unique_values) > 4:
                return "metric"
        return "parameter"
    if re.search(r"(beta|alpha|lambda|theta|step|time|index|dst|start|target|door|seed)", lowered):
        return "parameter"
    return "metric"


def infer_series_unit(name: str, series_type: str) -> str:
    lowered = name.lower()
    if series_type == "binary":
        return "indicator"
    if series_type == "probability":
        return "probability"
    if re.search(r"(time|step|tick|iter)", lowered):
        return "step"
    if re.search(r"(count|hits|visits|size)", lowered):
        return "count"
    if series_type == "parameter":
        return "parameter"
    return "value"


def build_series_semantics(name: str, values: list[float]) -> dict[str, Any]:
    finite_values = [float(v) for v in values if isinstance(v, (int, float)) and math.isfinite(float(v))]
    series_type = infer_series_type(name, finite_values)
    unit = infer_series_unit(name, series_type)
    if finite_values:
        min_v = min(finite_values)
        max_v = max(finite_values)
        positive_ratio = sum(1 for v in finite_values if v > 0) / max(1, len(finite_values))
    else:
        min_v = 0.0
        max_v = 0.0
        positive_ratio = 0.0
    return {
        "name": name,
        "series_type": series_type,
        "unit": unit,
        "min": float(min_v),
        "max": float(max_v),
        "positive_ratio": float(round(positive_ratio, 6)),
    }


def dedupe_sequence(items: list[Any], *, max_items: int | None = None) -> list[Any]:
    out: list[Any] = []
    seen: set[str] = set()
    for item in items:
        if isinstance(item, (dict, list)):
            key = json.dumps(item, ensure_ascii=False, sort_keys=True)
        else:
            key = normalize_space(str(item))
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(item)
        if max_items is not None and len(out) >= max_items:
            break
    return out


def ensure_locale_field_parity(
    left: list[Any],
    right: list[Any],
    *,
    max_items: int | None = None,
    min_ratio: float = 0.9,
) -> tuple[list[Any], list[Any]]:
    a = dedupe_sequence(list(left), max_items=max_items)
    b = dedupe_sequence(list(right), max_items=max_items)
    if not a and b:
        a = list(b)
    if not b and a:
        b = list(a)
    if a and b:
        ratio = min(len(a), len(b)) / max(1, max(len(a), len(b)))
        if ratio < min_ratio:
            merged = dedupe_sequence(a + b, max_items=max_items)
            a = dedupe_sequence(a + merged, max_items=max_items)
            b = dedupe_sequence(b + merged, max_items=max_items)
    return a, b


def align_locale_payloads(base_meta: dict[str, Any], cn_meta: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    limits = {
        "key_findings": 8,
        "math_blocks": 14,
        "math_story": 6,
        "section_cards": 10,
        "reproducibility_commands": 10,
        "source_documents": 6,
    }
    for field, limit in limits.items():
        left = list(base_meta.get(field, []))
        right = list(cn_meta.get(field, []))
        aligned_left, aligned_right = ensure_locale_field_parity(left, right, max_items=limit, min_ratio=0.9)
        base_meta[field] = aligned_left
        cn_meta[field] = aligned_right
    return base_meta, cn_meta


def sanitize_latex_for_katex(latex: str) -> str:
    value = normalize_space(strip_tex_comments(latex))
    if not value:
        return ""
    value = re.sub(r"\\(?:label|tag\*?)\{[^{}]*\}", " ", value)
    value = value.replace("\\nonumber", " ")
    value = value.replace("\\notag", " ")
    value = re.sub(r"\\(?:eqref|ref)\{([^{}]+)\}", r"\\text{[\1]}", value)
    value = re.sub(r"\\textbf\{([^{}]*)\}", r"\\text{\1}", value)
    value = re.sub(r"\\mathrm\{([^{}]*)\}", r"\\text{\1}", value)
    if contains_cjk(value) and not re.search(r"[=\\_^{}()\\[\\]+\\-*/]", value):
        return ""
    if ("&" in value or "\\\\" in value) and "\\begin{" not in value:
        value = rf"\begin{{aligned}} {value} \end{{aligned}}"
    value = normalize_space(value)
    return value


def parse_csv_dataset(path: Path, max_points: int) -> dict[str, Any] | None:
    with path.open("r", encoding="utf-8", errors="ignore", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            return None

        rows: list[dict[str, str]] = []
        for idx, row in enumerate(reader):
            if idx >= max_points:
                break
            rows.append({k: (v or "").strip() for k, v in row.items() if k})

    if not rows:
        return None

    numeric_fields: list[str] = []
    for field in reader.fieldnames:
        if not field:
            continue
        values = [row.get(field, "") for row in rows]
        numeric = 0
        for v in values:
            if not v:
                continue
            try:
                num = float(v)
                if math.isfinite(num):
                    numeric += 1
            except ValueError:
                pass
        if numeric >= max(3, int(len(values) * 0.65)):
            numeric_fields.append(field)

    if len(numeric_fields) < 1:
        return None

    preferred_x = [
        name
        for name in numeric_fields
        if re.search(r"(^t$|time|step|x|index|n$)", name, re.IGNORECASE)
    ]
    x_field = preferred_x[0] if preferred_x else numeric_fields[0]
    y_fields = [name for name in numeric_fields if name != x_field][:3]
    if not y_fields:
        y_fields = [x_field]

    x_values: list[float] = []
    series: list[dict[str, Any]] = []
    y_map: dict[str, list[float]] = {name: [] for name in y_fields}

    for row in rows:
        raw_x = row.get(x_field, "")
        try:
            x_value = float(raw_x)
            if not math.isfinite(x_value):
                raise ValueError
        except ValueError:
            x_value = float(len(x_values))
        x_values.append(x_value)
        for y_name in y_fields:
            raw_y = row.get(y_name, "")
            try:
                y_value = float(raw_y)
                if not math.isfinite(y_value):
                    raise ValueError
            except ValueError:
                y_value = 0.0
            y_map[y_name].append(y_value)

    semantics: list[dict[str, Any]] = []
    default_series: list[str] = []
    for y_name in y_fields:
        semantic = build_series_semantics(y_name, y_map[y_name])
        semantics.append(semantic)
        if semantic["series_type"] in {"metric", "probability"}:
            default_series.append(y_name)
        series.append(
            {
                "name": y_name,
                "x": x_values,
                "y": y_map[y_name],
                "series_type": semantic["series_type"],
                "unit": semantic["unit"],
            }
        )
    if not default_series and y_fields:
        default_series = [y_fields[0]]

    return {
        "x_label": x_field,
        "y_label": ", ".join(y_fields),
        "series": series,
        "series_semantics": semantics,
        "default_series": default_series,
        "provenance": {"type": "csv", "source": rel_repo_path(path)},
    }


def parse_json_dataset(path: Path, max_points: int) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8", errors="ignore"))
    except json.JSONDecodeError:
        return None

    records: list[dict[str, Any]] | None = None
    if isinstance(payload, list) and payload and isinstance(payload[0], dict):
        records = [item for item in payload[:max_points] if isinstance(item, dict)]
    elif isinstance(payload, dict):
        for key in ("rows", "data", "results"):
            maybe = payload.get(key)
            if isinstance(maybe, list) and maybe and isinstance(maybe[0], dict):
                records = [item for item in maybe[:max_points] if isinstance(item, dict)]
                break
        if records is None:
            vector_keys = [k for k, v in payload.items() if isinstance(v, list)]
            if vector_keys:
                length = min(len(payload[k]) for k in vector_keys if isinstance(payload[k], list))
                if length > 0:
                    rows: list[dict[str, Any]] = []
                    for i in range(min(length, max_points)):
                        rows.append({k: payload[k][i] for k in vector_keys})
                    records = rows

    if not records:
        return None

    numeric_fields: list[str] = []
    all_keys = sorted({k for row in records for k in row.keys()})
    for key in all_keys:
        values = [row.get(key) for row in records]
        numeric = sum(1 for v in values if isinstance(v, (int, float)) and math.isfinite(float(v)))
        if numeric >= max(3, int(len(values) * 0.65)):
            numeric_fields.append(key)

    if not numeric_fields:
        return None

    preferred_x = [
        name
        for name in numeric_fields
        if re.search(r"(^t$|time|step|x|index|n$)", name, re.IGNORECASE)
    ]
    x_field = preferred_x[0] if preferred_x else numeric_fields[0]
    y_fields = [name for name in numeric_fields if name != x_field][:3]
    if not y_fields:
        y_fields = [x_field]

    x_values: list[float] = []
    series_map: dict[str, list[float]] = {name: [] for name in y_fields}
    for idx, row in enumerate(records):
        raw_x = row.get(x_field, idx)
        if isinstance(raw_x, (int, float)):
            x_val = float(raw_x) if math.isfinite(float(raw_x)) else float(idx)
        else:
            x_val = float(idx)
        x_values.append(x_val)

        for y_name in y_fields:
            raw_y = row.get(y_name, 0.0)
            if isinstance(raw_y, (int, float)):
                y_val = float(raw_y)
                series_map[y_name].append(y_val if math.isfinite(y_val) else 0.0)
            else:
                series_map[y_name].append(0.0)

    semantics: list[dict[str, Any]] = []
    default_series: list[str] = []
    series: list[dict[str, Any]] = []
    for y_name in y_fields:
        semantic = build_series_semantics(y_name, series_map[y_name])
        semantics.append(semantic)
        if semantic["series_type"] in {"metric", "probability"}:
            default_series.append(y_name)
        series.append(
            {
                "name": y_name,
                "x": x_values,
                "y": series_map[y_name],
                "series_type": semantic["series_type"],
                "unit": semantic["unit"],
            }
        )
    if not default_series and y_fields:
        default_series = [y_fields[0]]
    return {
        "x_label": x_field,
        "y_label": ", ".join(y_fields),
        "series": series,
        "series_semantics": semantics,
        "default_series": default_series,
        "provenance": {"type": "json", "source": rel_repo_path(path)},
    }


def fallback_asset_dataset(report_id: str, assets: list[dict[str, Any]]) -> dict[str, Any]:
    ranked = sorted(assets, key=lambda item: item["size"], reverse=True)[:20]
    x_vals = list(range(1, len(ranked) + 1))
    y_vals = [float(item["size"]) for item in ranked]
    labels = [item["label"] for item in ranked]
    return {
        "report_id": report_id,
        "series_id": "asset-size-profile",
        "x_label": "Asset rank",
        "y_label": "Size (bytes)",
        "series": [
            {
                "name": "size_by_rank",
                "x": x_vals,
                "y": y_vals,
                "series_type": "metric",
                "unit": "bytes",
            }
        ],
        "series_semantics": [build_series_semantics("size_by_rank", y_vals)],
        "default_series": ["size_by_rank"],
        "provenance": {"type": "derived", "source": f"assets:{','.join(labels[:5])}"},
    }


def build_datasets(
    report_id: str,
    report_dir: Path,
    out_report_dir: Path,
    max_datasets: int,
    max_points: int,
    assets: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    data_candidates = [
        p
        for p in report_dir.rglob("*")
        if p.is_file()
        and p.suffix.lower() in {".csv", ".json"}
        and "build" not in p.parts
        and "figures" not in p.parts
        and "tables" not in p.parts
    ]
    data_candidates.sort(key=lambda p: p.as_posix())

    datasets_meta: list[dict[str, Any]] = []
    seen_ids: set[str] = set()

    series_dir = out_report_dir / "series"
    series_dir.mkdir(parents=True, exist_ok=True)

    for candidate in data_candidates:
        if len(datasets_meta) >= max_datasets:
            break
        parsed: dict[str, Any] | None = None
        if candidate.suffix.lower() == ".csv":
            parsed = parse_csv_dataset(candidate, max_points)
        elif candidate.suffix.lower() == ".json":
            parsed = parse_json_dataset(candidate, max_points)

        if not parsed:
            continue

        stem = re.sub(r"[^a-zA-Z0-9_-]+", "-", candidate.stem.lower()).strip("-")
        series_id = stem or f"dataset-{len(datasets_meta) + 1}"
        if series_id in seen_ids:
            suffix = 2
            while f"{series_id}-{suffix}" in seen_ids:
                suffix += 1
            series_id = f"{series_id}-{suffix}"
        seen_ids.add(series_id)

        payload = {
            "report_id": report_id,
            "series_id": series_id,
            "x_label": parsed["x_label"],
            "y_label": parsed["y_label"],
            "series": parsed["series"],
            "series_semantics": parsed.get("series_semantics", []),
            "default_series": parsed.get("default_series", []),
            "provenance": parsed["provenance"],
        }

        series_rel = f"/data/v1/reports/{report_id}/series/{series_id}.json"
        series_path = series_dir / f"{series_id}.json"
        series_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")

        datasets_meta.append(
            {
                "series_id": series_id,
                "title": candidate.stem,
                "x_label": parsed["x_label"],
                "y_label": parsed["y_label"],
                "series_path": series_rel,
                "default_series": parsed.get("default_series", []),
                "series_semantics": parsed.get("series_semantics", []),
                "provenance": parsed["provenance"],
            }
        )

    if not datasets_meta:
        fallback = fallback_asset_dataset(report_id, assets)
        series_rel = f"/data/v1/reports/{report_id}/series/{fallback['series_id']}.json"
        series_path = series_dir / f"{fallback['series_id']}.json"
        series_path.write_text(json.dumps(fallback, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
        datasets_meta.append(
            {
                "series_id": fallback["series_id"],
                "title": "Asset Size Profile",
                "x_label": fallback["x_label"],
                "y_label": fallback["y_label"],
                "series_path": series_rel,
                "default_series": fallback.get("default_series", []),
                "series_semantics": fallback.get("series_semantics", []),
                "provenance": fallback["provenance"],
            }
        )

    return datasets_meta


def build_report_payload(
    item: dict[str, Any],
    output_dir: Path,
    artifacts_dir: Path,
    *,
    max_assets: int,
    max_figures: int,
    max_datasets: int,
    max_points: int,
    no_copy_assets: bool,
    generated_at: str,
) -> dict[str, Any]:
    report_id = str(item["id"])
    report_rel = str(item["path"])
    report_dir = REPO_ROOT / report_rel
    out_report_dir = output_dir / "reports" / report_id
    out_report_dir.mkdir(parents=True, exist_ok=True)

    readme_title, readme_summary, readme_findings = parse_readme(report_dir, report_id)
    tex_en = extract_tex_story(item, report_dir, report_id, "en")
    tex_cn = extract_tex_story(item, report_dir, report_id, "cn")

    top_assets = gather_files(report_dir, {".pdf", ".tex"}, max_assets)
    figure_assets = gather_files(report_dir / "figures" if (report_dir / "figures").exists() else report_dir, FIGURE_EXT, max_figures)

    assets: list[dict[str, Any]] = []
    figure_records: list[dict[str, Any]] = []
    seen_asset_fingerprints: set[tuple[str, str]] = set()

    selected = top_assets + [p for p in figure_assets if p not in top_assets]
    for idx, src in enumerate(selected[: max_assets + max_figures]):
        kind = asset_kind(src)
        digest = sha256_file(src)
        fingerprint = (digest, kind)
        if fingerprint in seen_asset_fingerprints:
            continue
        seen_asset_fingerprints.add(fingerprint)

        web_path, source_path = copy_asset(
            src,
            report_id,
            report_dir,
            artifacts_dir,
            no_copy_assets=no_copy_assets,
        )
        record = {
            "kind": kind,
            "label": src.name,
            "web_path": web_path,
            "source_path": source_path,
            "size": int(src.stat().st_size),
            "sha256": digest,
        }
        assets.append(record)

        if src.suffix.lower() in FIGURE_EXT:
            figure_records.append(
                {
                    "id": f"fig-{idx + 1}",
                    "title": src.stem.replace("_", " "),
                    "web_path": web_path,
                    "source_path": source_path,
                }
            )

    assets = disambiguate_asset_labels(assets)
    figure_records = disambiguate_figure_titles(figure_records)

    datasets = build_datasets(
        report_id,
        report_dir,
        out_report_dir,
        max_datasets=max_datasets,
        max_points=max_points,
        assets=assets,
    )
    report_updated_at = detect_report_updated_at(report_dir, generated_at)

    title_en = tex_en["title"] or readme_title
    title_cn = tex_cn["title"] or title_en
    summary_en = canonical_summary(tex_en["summary"] or readme_summary, max_chars=1200)
    summary_cn = canonical_summary(tex_cn["summary"] or summary_en, max_chars=1200)
    findings_en = clean_findings(readme_findings + list(tex_en["findings"]), report_id, max_items=8)
    findings_cn = clean_findings(readme_findings + list(tex_cn["findings"]), report_id, max_items=8)
    inferred_languages = ["en"]
    if contains_cjk(title_cn) or contains_cjk(summary_cn) or any(contains_cjk(item) for item in findings_cn):
        inferred_languages.append("cn")
    elif tex_cn.get("source_documents"):
        inferred_languages.append("cn")

    base_meta = {
        "report_id": report_id,
        "lang": "en",
        "title": title_en,
        "summary": summary_en,
        "key_findings": findings_en,
        "narrative": tex_en["narrative"],
        "section_cards": tex_en["section_cards"],
        "math_blocks": tex_en["math_blocks"],
        "math_story": tex_en["math_story"],
        "reproducibility_commands": tex_en["reproducibility_commands"],
        "source_documents": tex_en["source_documents"],
        "datasets": datasets,
        "assets": assets,
        "updated_at": report_updated_at,
    }
    cn_meta = {
        **base_meta,
        "lang": "cn",
        "title": title_cn,
        "summary": summary_cn,
        "key_findings": findings_cn,
        "narrative": tex_cn["narrative"] if tex_cn["section_cards"] else tex_en["narrative"],
        "section_cards": tex_cn["section_cards"] if tex_cn["section_cards"] else tex_en["section_cards"],
        "math_blocks": tex_cn["math_blocks"] if tex_cn["math_blocks"] else tex_en["math_blocks"],
        "math_story": tex_cn["math_story"] if tex_cn["math_story"] else tex_en["math_story"],
        "reproducibility_commands": tex_cn["reproducibility_commands"]
        if tex_cn["reproducibility_commands"]
        else tex_en["reproducibility_commands"],
        "source_documents": tex_cn["source_documents"] if tex_cn["source_documents"] else tex_en["source_documents"],
    }
    base_meta, cn_meta = align_locale_payloads(base_meta, cn_meta)

    (out_report_dir / "meta.json").write_text(
        json.dumps(base_meta, ensure_ascii=False, indent=2, allow_nan=False),
        encoding="utf-8",
    )
    (out_report_dir / "meta.cn.json").write_text(
        json.dumps(cn_meta, ensure_ascii=False, indent=2, allow_nan=False),
        encoding="utf-8",
    )
    (out_report_dir / "figures.json").write_text(
        json.dumps(figure_records, ensure_ascii=False, indent=2, allow_nan=False),
        encoding="utf-8",
    )

    return {
        "report_id": report_id,
        "path": report_rel,
        "languages": inferred_languages,
        "group": infer_group(report_id),
        "updated_at": report_updated_at,
    }


def detect_notions_from_formula(latex: str) -> set[str]:
    lowered = latex.lower()
    notions: set[str] = set()
    if "f(t)" in lowered or "\\pr" in lowered or "first" in lowered:
        notions.add("fpt-pmf")
    if "s(t)" in lowered or "survival" in lowered:
        notions.add("survival")
    if "h(t)" in lowered or "hazard" in lowered:
        notions.add("hazard")
    if "beta" in lowered or "\\beta" in lowered:
        notions.add("beta-scan")
    if "q=" in lowered or "\\lambda" in lowered or "eigen" in lowered:
        notions.add("spectral")
    if "\\sum" in lowered or "fft" in lowered or "aw" in lowered:
        notions.add("aw-inversion")
    return notions


def build_theory_map(output_dir: Path, reports: list[dict[str, Any]], generated_at: str) -> None:
    notions_meta = {
        "fpt-pmf": {
            "label_en": "First-passage distribution",
            "label_cn": "首达时间分布",
            "description_en": "Core PMF/CDF/survival quantities used across the major report families.",
            "description_cn": "在主要报告族中反复出现的 PMF/CDF/生存函数核心量。",
        },
        "survival": {
            "label_en": "Survival and hazard",
            "label_cn": "生存函数与风险率",
            "description_en": "Links between f(t), S(t), and hazard-style diagnostics.",
            "description_cn": "用于连接 f(t)、S(t) 与风险率诊断的定义。",
        },
        "hazard": {
            "label_en": "Hazard interpretation",
            "label_cn": "风险率解释",
            "description_en": "Peak/valley interpretation using hazard dynamics.",
            "description_cn": "通过风险率动态解释峰谷结构。",
        },
        "beta-scan": {
            "label_en": "Beta / shortcut scan",
            "label_cn": "beta/shortcut 扫描",
            "description_en": "How shortcut strength changes bimodality and phase behavior.",
            "description_cn": "shortcut 强度变化对双峰与相图的影响。",
        },
        "spectral": {
            "label_en": "Spectral decomposition",
            "label_cn": "谱分解",
            "description_en": "Eigenvalue / resolvent based derivations.",
            "description_cn": "基于特征值与 resolvent 的推导框架。",
        },
        "aw-inversion": {
            "label_en": "AW inversion",
            "label_cn": "AW 反演",
            "description_en": "Discrete Cauchy / FFT inversion from generating functions.",
            "description_cn": "从生成函数做离散 Cauchy / FFT 反演。",
        },
    }

    notion_reports: dict[str, set[str]] = defaultdict(set)
    report_formula_counts: dict[str, int] = {}
    finding_counter: Counter[str] = Counter()
    finding_examples: dict[str, str] = {}
    finding_reports: dict[str, set[str]] = defaultdict(set)
    formula_counter: Counter[str] = Counter()
    formula_examples: dict[str, str] = {}
    formula_reports: dict[str, set[str]] = defaultdict(set)
    asset_dup_stats: dict[str, dict[str, int]] = {}

    for row in reports:
        report_id = str(row["report_id"])
        meta_path = output_dir / "reports" / report_id / "meta.json"
        if not meta_path.exists():
            continue
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        math_blocks = list(meta.get("math_blocks", []))
        report_formula_counts[report_id] = len(math_blocks)
        report_notions: set[str] = set()
        for block in math_blocks:
            latex = str(block.get("latex", ""))
            signature = normalize_finding_key(latex)
            if signature:
                formula_counter[signature] += 1
                formula_examples.setdefault(signature, latex)
                formula_reports[signature].add(report_id)
            for notion in detect_notions_from_formula(latex):
                notion_reports[notion].add(report_id)
                report_notions.add(notion)
        if not report_notions:
            notion_reports["fpt-pmf"].add(report_id)

        for finding in meta.get("key_findings", []):
            text = normalize_space(str(finding))
            if not text:
                continue
            if looks_like_path_finding(text):
                continue
            key = normalize_finding_key(text)
            if not key:
                continue
            finding_counter[key] += 1
            finding_examples.setdefault(key, text)
            finding_reports[key].add(report_id)

        labels = [f"{row.get('kind', 'other')}::{str(row.get('label', '')).lower()}" for row in meta.get("assets", [])]
        duplicate_count = max(0, len(labels) - len(set(labels)))
        if labels:
            asset_dup_stats[report_id] = {"duplicate_count": duplicate_count, "total_assets": len(labels)}

    theory_cards = []
    for notion_id, payload in notions_meta.items():
        linked = sorted(notion_reports.get(notion_id, set()))
        if not linked:
            continue
        theory_cards.append(
            {
                "id": notion_id,
                **payload,
                "report_ids": linked,
                "report_count": len(linked),
            }
        )

    all_report_ids = {str(row["report_id"]) for row in reports}
    mapped_report_ids = set().union(*(set(card["report_ids"]) for card in theory_cards)) if theory_cards else set()
    unmapped_report_ids = sorted(all_report_ids - mapped_report_ids)

    repeated_findings = []
    for key, count in finding_counter.items():
        report_ids = sorted(finding_reports.get(key, set()))
        if len(report_ids) <= 1:
            continue
        repeated_findings.append(
            {
                "text": finding_examples[key],
                "count": count,
                "report_ids": report_ids,
            }
        )
    repeated_findings.sort(key=lambda row: int(row["count"]), reverse=True)

    repeated_formulas = []
    for key, count in formula_counter.items():
        report_ids = sorted(formula_reports.get(key, set()))
        if len(report_ids) <= 1:
            continue
        repeated_formulas.append(
            {
                "latex": formula_examples[key],
                "count": count,
                "report_ids": report_ids,
            }
        )
    repeated_formulas.sort(key=lambda row: int(row["count"]), reverse=True)
    redundant_repeated_formulas = [
        row for row in repeated_formulas if is_trivial_formula_signature(str(row.get("latex", "")))
    ]
    shared_core_formulas = [
        row for row in repeated_formulas if not is_trivial_formula_signature(str(row.get("latex", "")))
    ]

    asset_dup_excess = {
        report_id: payload
        for report_id, payload in asset_dup_stats.items()
        if payload.get("duplicate_count", 0) > 0
    }

    consistency_checks = [
        {
            "check": "all_reports_have_formula",
            "pass": all(count >= 1 for count in report_formula_counts.values()) if report_formula_counts else False,
            "details": report_formula_counts,
        },
        {
            "check": "all_reports_mapped_in_theory_cards",
            "pass": len(unmapped_report_ids) == 0,
            "details": {"unmapped_report_ids": unmapped_report_ids},
        },
        {
            "check": "duplicate_key_findings",
            "pass": len(repeated_findings) == 0,
            "details": repeated_findings[:12],
        },
        {
            "check": "duplicate_math_signatures",
            "pass": len(redundant_repeated_formulas) <= max(2, int(len(reports) * 0.15)),
            "details": {
                "redundant_signatures": redundant_repeated_formulas[:12],
                "shared_core_signatures": shared_core_formulas[:12],
                "redundant_count": len(redundant_repeated_formulas),
                "shared_core_count": len(shared_core_formulas),
            },
        },
        {
            "check": "asset_label_duplication",
            "pass": len(asset_dup_excess) == 0,
            "details": asset_dup_excess,
        },
    ]

    theory_payload = {
        "version": "v1",
        "generated_at": generated_at,
        "cards": theory_cards,
        "consistency_checks": consistency_checks,
    }
    (output_dir / "theory_map.json").write_text(
        json.dumps(theory_payload, ensure_ascii=False, indent=2, allow_nan=False),
        encoding="utf-8",
    )


def build_report_network(output_dir: Path, reports: list[dict[str, Any]], generated_at: str) -> None:
    theory_map_path = output_dir / "theory_map.json"
    theory_payload: dict[str, Any] = {}
    if theory_map_path.exists():
        theory_payload = json.loads(theory_map_path.read_text(encoding="utf-8"))

    cards = list(theory_payload.get("cards", []))
    notion_labels: dict[str, dict[str, str]] = {}
    notion_by_report: dict[str, set[str]] = defaultdict(set)
    for card in cards:
        notion_id = str(card.get("id", "")).strip()
        if not notion_id:
            continue
        notion_labels[notion_id] = {
            "label_en": str(card.get("label_en", notion_id)),
            "label_cn": str(card.get("label_cn", notion_id)),
        }
        for report_id in card.get("report_ids", []):
            rid = str(report_id).strip()
            if rid:
                notion_by_report[rid].add(notion_id)

    ordered_ids = [str(row["report_id"]) for row in reports]
    report_by_id = {str(row["report_id"]): row for row in reports}
    group_tracks: dict[str, list[str]] = defaultdict(list)
    for row in reports:
        group_tracks[str(row.get("group", "misc"))].append(str(row["report_id"]))

    meta_by_report: dict[str, dict[str, Any]] = {}
    cn_meta_by_report: dict[str, dict[str, Any]] = {}
    for rid in ordered_ids:
        meta_path = output_dir / "reports" / rid / "meta.json"
        meta_cn_path = output_dir / "reports" / rid / "meta.cn.json"
        if meta_path.exists():
            meta_by_report[rid] = json.loads(meta_path.read_text(encoding="utf-8"))
        else:
            meta_by_report[rid] = {}
        if meta_cn_path.exists():
            cn_meta_by_report[rid] = json.loads(meta_cn_path.read_text(encoding="utf-8"))
        else:
            cn_meta_by_report[rid] = {}

    token_cache: dict[str, set[str]] = {}

    def id_tokens(report_id: str) -> set[str]:
        cached = token_cache.get(report_id)
        if cached is not None:
            return cached
        tokens = {tok for tok in re.split(r"[_\-]+", report_id.lower()) if tok}
        token_cache[report_id] = tokens
        return tokens

    def adjacency_in_group(a: str, b: str) -> bool:
        group = str(report_by_id.get(a, {}).get("group", "misc"))
        track = group_tracks.get(group, [])
        if a not in track or b not in track:
            return False
        return abs(track.index(a) - track.index(b)) == 1

    def build_link(a: str, b: str) -> dict[str, Any] | None:
        if a == b:
            return None
        group_a = str(report_by_id.get(a, {}).get("group", "misc"))
        group_b = str(report_by_id.get(b, {}).get("group", "misc"))
        notions_a = notion_by_report.get(a, set())
        notions_b = notion_by_report.get(b, set())
        shared_notions = sorted(notions_a.intersection(notions_b))
        score = 0.0
        if shared_notions:
            score += 3.0 * len(shared_notions)
        if group_a == group_b:
            score += 2.0
        if adjacency_in_group(a, b):
            score += 1.0
        overlap = id_tokens(a).intersection(id_tokens(b))
        if len(overlap) >= 2:
            score += 1.0
        if score <= 0:
            return None
        return {
            "report_id": b,
            "score": round(score, 2),
            "same_group": group_a == group_b,
            "adjacent_in_track": adjacency_in_group(a, b),
            "shared_notion_ids": shared_notions,
            "shared_token_count": len(overlap),
        }

    report_nodes: list[dict[str, Any]] = []
    for rid in ordered_ids:
        group = str(report_by_id.get(rid, {}).get("group", "misc"))
        track = group_tracks.get(group, [])
        idx = track.index(rid) if rid in track else -1
        previous_in_group = track[idx - 1] if idx > 0 else ""
        next_in_group = track[idx + 1] if idx >= 0 and idx + 1 < len(track) else ""

        links: list[dict[str, Any]] = []
        for other in ordered_ids:
            row = build_link(rid, other)
            if row:
                links.append(row)

        same_group_links = [row for row in links if bool(row.get("same_group"))]
        cross_group_links = [row for row in links if not bool(row.get("same_group"))]
        same_group_links.sort(key=lambda row: (-float(row["score"]), str(row["report_id"])))
        cross_group_links.sort(key=lambda row: (-float(row["score"]), str(row["report_id"])))

        meta = meta_by_report.get(rid, {})
        meta_cn = cn_meta_by_report.get(rid, {})
        report_nodes.append(
            {
                "report_id": rid,
                "group": group,
                "title_en": str(meta.get("title", rid)),
                "title_cn": str(meta_cn.get("title", meta.get("title", rid))),
                "summary_en": summarize_plain(str(meta.get("summary", "")), max_chars=220),
                "summary_cn": summarize_plain(str(meta_cn.get("summary", meta.get("summary", ""))), max_chars=220),
                "notion_ids": sorted(notion_by_report.get(rid, set())),
                "previous_in_group": previous_in_group,
                "next_in_group": next_in_group,
                "same_group_links": same_group_links[:6],
                "cross_group_links": cross_group_links[:6],
            }
        )

    ordered_groups = []
    for row in reports:
        group = str(row.get("group", "misc"))
        if group not in ordered_groups:
            ordered_groups.append(group)

    group_paths = [
        {
            "group": group,
            "report_ids": group_tracks.get(group, []),
            "step_count": len(group_tracks.get(group, [])),
        }
        for group in ordered_groups
    ]

    full_story = []
    for group in ordered_groups:
        full_story.extend(group_tracks.get(group, []))

    payload = {
        "version": "v1",
        "generated_at": generated_at,
        "notion_labels": notion_labels,
        "group_paths": group_paths,
        "global_storyline": {
            "label_en": "Grid and ring mechanisms converge into cross-report synthesis.",
            "label_cn": "二维与环模型机制最终汇入跨报告综合结论。",
            "report_ids": full_story,
        },
        "reports": report_nodes,
    }
    (output_dir / "report_network.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False),
        encoding="utf-8",
    )


def build_content_map(output_dir: Path, reports: list[dict[str, Any]], generated_at: str) -> None:
    network_path = output_dir / "report_network.json"
    network_payload: dict[str, Any] = {}
    if network_path.exists():
        network_payload = json.loads(network_path.read_text(encoding="utf-8"))

    network_nodes = {
        str(row.get("report_id", "")): row
        for row in list(network_payload.get("reports", []))
        if str(row.get("report_id", "")).strip()
    }

    meta_by_report: dict[str, dict[str, Any]] = {}
    cn_meta_by_report: dict[str, dict[str, Any]] = {}
    report_path_by_id: dict[str, str] = {}
    for row in reports:
        rid = str(row["report_id"])
        report_path_by_id[rid] = str(row.get("path", ""))
        meta_path = output_dir / "reports" / rid / "meta.json"
        meta_cn_path = output_dir / "reports" / rid / "meta.cn.json"
        meta_by_report[rid] = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
        cn_meta_by_report[rid] = json.loads(meta_cn_path.read_text(encoding="utf-8")) if meta_cn_path.exists() else {}

    claim_rows: list[dict[str, Any]] = []
    claim_ids_by_report: dict[str, list[str]] = defaultdict(list)
    report_guides: list[dict[str, Any]] = []

    for row in reports:
        rid = str(row["report_id"])
        meta = meta_by_report.get(rid, {})
        meta_cn = cn_meta_by_report.get(rid, {})
        node = network_nodes.get(rid, {})

        objective_en = normalize_space(str(meta.get("narrative", {}).get("result_overview", "")))
        objective_cn = normalize_space(str(meta_cn.get("narrative", {}).get("result_overview", "")))
        if not objective_en:
            objective_en = summarize_plain(str(meta.get("summary", "Research objective unavailable.")), max_chars=240)
        if not objective_cn:
            objective_cn = summarize_plain(
                str(meta_cn.get("summary", meta.get("summary", "研究目标暂缺。"))),
                max_chars=240,
            )

        upstream: list[str] = []
        prev_id = str(node.get("previous_in_group", "")).strip()
        if prev_id:
            upstream.append(prev_id)

        downstream: list[str] = []
        next_id = str(node.get("next_in_group", "")).strip()
        if next_id:
            downstream.append(next_id)

        related_candidates = [
            str(link.get("report_id", "")).strip()
            for link in list(node.get("same_group_links", []))[:3] + list(node.get("cross_group_links", []))[:3]
        ]
        related = dedupe_preserve([x for x in related_candidates if x and x != rid], max_items=6)

        report_guides.append(
            {
                "report_id": rid,
                "objective_en": objective_en,
                "objective_cn": objective_cn,
                "upstream_report_ids": upstream,
                "downstream_report_ids": downstream,
                "related_report_ids": related,
                "verification_steps_en": [
                    "Read the key claims and their evidence references first.",
                    "Verify at least one equation card and one dataset panel against source paths.",
                    "Cross-check this report with upstream/downstream linked reports.",
                ],
                "verification_steps_cn": [
                    "先读关键 claim 及其证据引用。",
                    "至少核对一条公式卡与一个数据面板的来源路径。",
                    "再与上游/下游关联报告做交叉核对。",
                ],
            }
        )

        findings_en = dedupe_preserve([str(x) for x in meta.get("key_findings", [])], max_items=8)
        findings_cn = dedupe_preserve([str(x) for x in meta_cn.get("key_findings", [])], max_items=8)
        section_cards_en = list(meta.get("section_cards", []))
        section_cards_cn = list(meta_cn.get("section_cards", []))
        math_blocks_en = list(meta.get("math_blocks", []))
        datasets = list(meta.get("datasets", []))
        source_docs = [str(x) for x in meta.get("source_documents", []) if str(x).strip()]
        narrative_en = dict(meta.get("narrative", {}))
        narrative_cn = dict(meta_cn.get("narrative", {}))

        staged_candidates: list[tuple[str, str, str]] = [
            (
                "model",
                normalize_space(str(narrative_en.get("model_overview", ""))),
                normalize_space(str(narrative_cn.get("model_overview", ""))),
            ),
            (
                "method",
                normalize_space(str(narrative_en.get("method_overview", ""))),
                normalize_space(str(narrative_cn.get("method_overview", ""))),
            ),
            (
                "result",
                normalize_space(str(narrative_en.get("result_overview", ""))),
                normalize_space(str(narrative_cn.get("result_overview", ""))),
            ),
        ]
        for idx, line in enumerate(findings_en[:2]):
            staged_candidates.append(
                (
                    "finding",
                    normalize_space(str(line)),
                    normalize_space(str(findings_cn[idx] if idx < len(findings_cn) else objective_cn)),
                )
            )

        staged_claims: list[tuple[str, str, str]] = []
        seen_claim_signatures: set[str] = set()
        for stage, text_en, text_cn in staged_candidates:
            cleaned_en = normalize_space(text_en)
            cleaned_cn = normalize_space(text_cn)
            if not cleaned_en:
                continue
            signature = normalize_finding_key(cleaned_en)
            if not signature or signature in seen_claim_signatures:
                continue
            seen_claim_signatures.add(signature)
            if not cleaned_cn:
                cleaned_cn = summarize_plain(objective_cn, max_chars=220)
            staged_claims.append((stage, cleaned_en, cleaned_cn))

        if not staged_claims:
            staged_claims = [
                (
                    "result",
                    summarize_plain(objective_en, max_chars=240),
                    summarize_plain(objective_cn, max_chars=240),
                )
            ]

        stage_hint_map: dict[str, tuple[str, ...]] = {
            "model": MODEL_HINTS,
            "method": METHOD_HINTS,
            "result": RESULT_HINTS,
            "finding": RESULT_HINTS,
        }

        for idx, (stage, text_en, text_cn) in enumerate(staged_claims):
            claim_id = f"{rid}-c{idx + 1}"
            claim_tokens = tokenize_claim_text(text_en)

            evidence: list[dict[str, Any]] = []

            for source_path in source_docs[:1]:
                evidence.append(
                    {
                        "evidence_type": "source_document",
                        "path": source_path,
                        "snippet_en": summarize_plain(text_en, max_chars=180),
                        "snippet_cn": summarize_plain(text_cn, max_chars=180),
                    }
                )

            section_scored: list[tuple[int, int]] = []
            for j, card in enumerate(section_cards_en):
                summary = normalize_space(str(card.get("summary", "")))
                if not summary:
                    continue
                title = normalize_space(str(card.get("heading", ""))).lower()
                overlap = len(claim_tokens.intersection(tokenize_claim_text(summary)))
                hint_bonus = 2 if any(h in title for h in stage_hint_map.get(stage, ())) else 0
                section_scored.append((overlap + hint_bonus, j))
            section_scored.sort(reverse=True)
            for _, j in section_scored[:2]:
                card_en = section_cards_en[j]
                card_cn = section_cards_cn[j] if j < len(section_cards_cn) else {}
                evidence.append(
                    {
                        "evidence_type": "section_summary",
                        "path": str(card_en.get("source_path", report_path_by_id.get(rid, rid))),
                        "snippet_en": summarize_plain(str(card_en.get("summary", text_en)), max_chars=180),
                        "snippet_cn": summarize_plain(str(card_cn.get("summary", text_cn)), max_chars=180),
                    }
                )

            math_limit = 2 if stage in {"model", "method"} else 1
            for block in math_blocks_en[:math_limit]:
                evidence.append(
                    {
                        "evidence_type": "math_block",
                        "path": str(block.get("source_path", report_path_by_id.get(rid, rid))),
                        "snippet_en": summarize_plain(str(block.get("context", "math block")), max_chars=120),
                        "snippet_cn": summarize_plain(str(block.get("context", "公式片段")), max_chars=120),
                    }
                )

            if datasets and stage in {"method", "result", "finding"}:
                ds = datasets[0]
                evidence.append(
                    {
                        "evidence_type": "dataset",
                        "path": str(ds.get("series_path", "")),
                        "snippet_en": summarize_plain(
                            f"{ds.get('title', 'dataset')}: {ds.get('x_label', 'x')} -> {ds.get('y_label', 'y')}",
                            max_chars=160,
                        ),
                        "snippet_cn": summarize_plain(
                            f"{ds.get('title', '数据集')}: {ds.get('x_label', 'x')} -> {ds.get('y_label', 'y')}",
                            max_chars=160,
                        ),
                    }
                )

            deduped_evidence: list[dict[str, Any]] = []
            seen_keys: set[str] = set()
            for row_evidence in evidence:
                key = f"{row_evidence.get('evidence_type')}::{row_evidence.get('path')}::{row_evidence.get('snippet_en')}"
                if key in seen_keys:
                    continue
                seen_keys.add(key)
                deduped_evidence.append(row_evidence)

            if not deduped_evidence:
                deduped_evidence = [
                    {
                        "evidence_type": "source_document",
                        "path": report_path_by_id.get(rid, rid),
                        "snippet_en": summarize_plain(text_en, max_chars=180),
                        "snippet_cn": summarize_plain(text_cn, max_chars=180),
                    }
                ]

            claim_rows.append(
                {
                    "claim_id": claim_id,
                    "report_id": rid,
                    "stage": stage,
                    "text_en": summarize_plain(text_en, max_chars=260),
                    "text_cn": summarize_plain(text_cn, max_chars=260),
                    "evidence": deduped_evidence[:6],
                    "linked_claim_ids": [],
                    "linked_report_ids": [],
                }
            )
            claim_ids_by_report[rid].append(claim_id)

    score_links: dict[str, list[tuple[int, str, str]]] = defaultdict(list)
    claim_list = list(claim_rows)
    for i, left in enumerate(claim_list):
        tokens_left = tokenize_claim_text(str(left.get("text_en", "")))
        if not tokens_left:
            continue
        for right in claim_list[i + 1 :]:
            if str(left.get("report_id")) == str(right.get("report_id")):
                continue
            tokens_right = tokenize_claim_text(str(right.get("text_en", "")))
            overlap = len(tokens_left.intersection(tokens_right))
            left_stage = str(left.get("stage"))
            right_stage = str(right.get("stage"))
            required_overlap = 1 if {"model", "method"}.intersection({left_stage, right_stage}) else 2
            if overlap < required_overlap:
                continue
            stage_bonus = 1 if left_stage == right_stage else 0
            score = overlap + stage_bonus
            left_id = str(left.get("claim_id"))
            right_id = str(right.get("claim_id"))
            score_links[left_id].append((score, right_id, str(right.get("report_id"))))
            score_links[right_id].append((score, left_id, str(left.get("report_id"))))

    guide_by_report = {row["report_id"]: row for row in report_guides}
    for claim in claim_rows:
        claim_id = str(claim.get("claim_id"))
        related = sorted(score_links.get(claim_id, []), key=lambda row: (-row[0], row[1]))[:5]
        linked_claim_ids = [row[1] for row in related]
        linked_report_ids = dedupe_preserve([row[2] for row in related], max_items=5)
        if not linked_report_ids:
            guide = guide_by_report.get(str(claim.get("report_id")), {})
            linked_report_ids = dedupe_preserve(
                list(guide.get("related_report_ids", [])) + list(guide.get("upstream_report_ids", [])),
                max_items=3,
            )
        claim["linked_claim_ids"] = linked_claim_ids
        claim["linked_report_ids"] = linked_report_ids

    arcs: list[dict[str, Any]] = []
    group_paths = list(network_payload.get("group_paths", []))
    for path_row in group_paths:
        group = str(path_row.get("group", "misc"))
        report_ids = [str(x) for x in path_row.get("report_ids", []) if str(x).strip()]
        checkpoints: list[dict[str, str]] = []
        claim_ids: list[str] = []
        for rid in report_ids:
            meta = meta_by_report.get(rid, {})
            meta_cn = cn_meta_by_report.get(rid, {})
            guide = guide_by_report.get(rid, {})
            checkpoints.append(
                {
                    "report_id": rid,
                    "title_en": str(meta.get("title", rid)),
                    "title_cn": str(meta_cn.get("title", meta.get("title", rid))),
                    "contribution_en": str(guide.get("objective_en", summarize_plain(str(meta.get("summary", "")), max_chars=180))),
                    "contribution_cn": str(
                        guide.get(
                            "objective_cn",
                            summarize_plain(str(meta_cn.get("summary", meta.get("summary", ""))), max_chars=180),
                        )
                    ),
                }
            )
            claim_ids.extend(claim_ids_by_report.get(rid, []))
        if not report_ids:
            continue
        arcs.append(
            {
                "arc_id": f"group-{group}",
                "label_en": f"{group} progression",
                "label_cn": f"{group} 研究推进链",
                "summary_en": f"{group} track links {len(report_ids)} reports into one continuous argument.",
                "summary_cn": f"{group} 轨道把 {len(report_ids)} 份报告串成连续论证。",
                "report_ids": report_ids,
                "claim_ids": dedupe_preserve(claim_ids, max_items=200),
                "checkpoint_count": len(checkpoints),
                "checkpoints": checkpoints,
            }
        )

    global_story = dict(network_payload.get("global_storyline", {}))
    global_reports = [str(x) for x in global_story.get("report_ids", []) if str(x).strip()]
    if global_reports:
        global_claim_ids: list[str] = []
        for rid in global_reports:
            global_claim_ids.extend(claim_ids_by_report.get(rid, []))
        arcs.append(
            {
                "arc_id": "global-synthesis",
                "label_en": str(global_story.get("label_en", "Global synthesis")),
                "label_cn": str(global_story.get("label_cn", "全局综合")),
                "summary_en": "Global storyline that connects all report families from mechanism to synthesis.",
                "summary_cn": "连接全部报告家族的全局叙事主线，从机制到综合结论。",
                "report_ids": global_reports,
                "claim_ids": dedupe_preserve(global_claim_ids, max_items=300),
                "checkpoint_count": len(global_reports),
                "checkpoints": [
                    {
                        "report_id": rid,
                        "title_en": str(meta_by_report.get(rid, {}).get("title", rid)),
                        "title_cn": str(
                            cn_meta_by_report.get(rid, {}).get("title", meta_by_report.get(rid, {}).get("title", rid))
                        ),
                        "contribution_en": str(guide_by_report.get(rid, {}).get("objective_en", "")),
                        "contribution_cn": str(guide_by_report.get(rid, {}).get("objective_cn", "")),
                    }
                    for rid in global_reports
                ],
            }
        )

    all_report_ids = {str(row["report_id"]) for row in reports}
    claims_report_ids = {str(row["report_id"]) for row in claim_rows}
    guides_report_ids = {str(row["report_id"]) for row in report_guides}
    missing_claim_reports = sorted(all_report_ids - claims_report_ids)
    missing_guide_reports = sorted(all_report_ids - guides_report_ids)
    claims_without_evidence = sorted([str(row["claim_id"]) for row in claim_rows if not row.get("evidence")])
    linked_claim_count = sum(1 for row in claim_rows if row.get("linked_report_ids"))
    duplicate_claim_signatures = Counter(normalize_finding_key(str(row.get("text_en", ""))) for row in claim_rows)
    repeated_claims = [
        {"signature": sig, "count": count}
        for sig, count in duplicate_claim_signatures.items()
        if sig and count > 1
    ]
    repeated_claims.sort(key=lambda row: int(row["count"]), reverse=True)

    consistency_checks = [
        {
            "check": "all_reports_have_claims",
            "pass": len(missing_claim_reports) == 0,
            "details": {"missing_report_ids": missing_claim_reports, "claim_count": len(claim_rows)},
        },
        {
            "check": "all_claims_have_evidence",
            "pass": len(claims_without_evidence) == 0,
            "details": {"claims_without_evidence": claims_without_evidence},
        },
        {
            "check": "all_reports_have_guides",
            "pass": len(missing_guide_reports) == 0,
            "details": {"missing_report_ids": missing_guide_reports},
        },
        {
            "check": "cross_report_claim_links",
            "pass": linked_claim_count >= max(1, int(len(claim_rows) * 0.65)),
            "details": {"linked_claim_count": linked_claim_count, "claim_count": len(claim_rows)},
        },
        {
            "check": "duplicate_claim_signatures",
            "pass": len(repeated_claims) <= max(4, int(len(claim_rows) * 0.2)),
            "details": repeated_claims[:20],
        },
    ]

    payload = {
        "version": "v1",
        "generated_at": generated_at,
        "report_count": len(all_report_ids),
        "arcs": arcs,
        "claims": claim_rows,
        "report_guides": report_guides,
        "consistency_checks": consistency_checks,
    }
    (output_dir / "content_map.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False),
        encoding="utf-8",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build site/public/data/v1 web payloads from report assets.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--artifacts-dir", type=Path, default=DEFAULT_ARTIFACTS_DIR)
    parser.add_argument("--mode", choices=["full", "changed"], default="full")
    parser.add_argument("--reports", nargs="*", default=[])
    parser.add_argument("--max-assets", type=int, default=40)
    parser.add_argument("--max-figures", type=int, default=24)
    parser.add_argument("--max-datasets", type=int, default=3)
    parser.add_argument("--max-points", type=int, default=1200)
    parser.add_argument("--no-copy-assets", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_dir: Path = args.output_dir
    artifacts_dir: Path = args.artifacts_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    registry = load_registry()
    ids_in_registry = {item["id"] for item in registry}

    if args.reports:
        selected_ids = {rid for rid in args.reports if rid in ids_in_registry}
        if not selected_ids:
            raise SystemExit("No matching reports found in --reports")
    elif args.mode == "changed":
        selected_ids = detect_changed_reports(registry)
    else:
        selected_ids = ids_in_registry

    existing_index_path = output_dir / "index.json"
    existing_entries: dict[str, dict[str, Any]] = {}
    if existing_index_path.exists():
        try:
            existing = json.loads(existing_index_path.read_text(encoding="utf-8"))
            for row in existing.get("reports", []):
                if "report_id" in row:
                    existing_entries[row["report_id"]] = row
        except json.JSONDecodeError:
            existing_entries = {}

    if args.mode == "full" and not args.reports:
        clean_output_dir(output_dir / "reports")
        clean_output_dir(artifacts_dir)

    generated_at = utc_now_iso()

    built_entries: dict[str, dict[str, Any]] = {}
    for item in registry:
        report_id = str(item["id"])
        if report_id not in selected_ids:
            if report_id in existing_entries:
                built_entries[report_id] = existing_entries[report_id]
            continue

        entry = build_report_payload(
            item,
            output_dir,
            artifacts_dir,
            max_assets=max(1, args.max_assets),
            max_figures=max(1, args.max_figures),
            max_datasets=max(1, args.max_datasets),
            max_points=max(20, args.max_points),
            no_copy_assets=bool(args.no_copy_assets),
            generated_at=generated_at,
        )
        built_entries[report_id] = entry

    reports = [built_entries[item["id"]] for item in registry if item["id"] in built_entries]
    index_payload = {
        "version": "v1",
        "generated_at": generated_at,
        "reports": reports,
    }
    existing_index_path.write_text(
        json.dumps(index_payload, ensure_ascii=False, indent=2, allow_nan=False),
        encoding="utf-8",
    )
    duplicate_resolution = enforce_unique_key_findings(output_dir, [row["report_id"] for row in reports])
    build_theory_map(output_dir, reports, generated_at)
    build_report_network(output_dir, reports, generated_at)
    build_content_map(output_dir, reports, generated_at)

    print(
        json.dumps(
            {
                "ok": True,
                "mode": args.mode,
                "selected_reports": sorted(selected_ids),
                "written_reports": [row["report_id"] for row in reports],
                "duplicate_resolution": duplicate_resolution[:10],
                "output_dir": output_dir.as_posix(),
                "artifacts_dir": artifacts_dir.as_posix(),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
