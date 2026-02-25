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


def parse_tex_title(tex_text: str) -> str:
    m = re.search(r"\\title\{(.*?)\}", tex_text, flags=re.DOTALL)
    if not m:
        return ""
    return summarize_plain(latex_to_plain(m.group(1)), max_chars=140)


def parse_tex_abstract(tex_text: str) -> str:
    m = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", tex_text, flags=re.DOTALL)
    if not m:
        return ""
    return summarize_plain(latex_to_plain(m.group(1)), max_chars=420)


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
        signature = re.sub(r"[^a-z0-9]+", "", latex.lower())
        if not signature or signature in seen:
            continue
        seen.add(signature)
        blocks.append(
            {
                "latex": latex,
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

    section_summaries = [str(section.get("summary", fallback)) for section in sections if section.get("summary")]
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
    section_cards = [
        {
            "heading": str(section["title"]),
            "summary": str(section["summary"]).strip() or f"{section['title']} section summary.",
            "source_path": rel_repo_path(tex_path),
        }
        for section in sections[:10]
    ]
    findings = extract_findings_from_sections(sections)
    math_blocks = extract_math_blocks(raw, sections, rel_repo_path(tex_path), lang)
    math_story = build_math_story(math_blocks, lang)
    abstract = parse_tex_abstract(raw)
    summary_fallback = abstract or (sections[0]["summary"] if sections else f"Research report {report_id}.")
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
        "summary": summary_fallback,
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
    summary = summarize_plain(summary, max_chars=320)

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
    return matched


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

    for y_name in y_fields:
        series.append({"name": y_name, "x": x_values, "y": y_map[y_name]})

    return {
        "x_label": x_field,
        "y_label": ", ".join(y_fields),
        "series": series,
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

    series = [{"name": y_name, "x": x_values, "y": series_map[y_name]} for y_name in y_fields]
    return {
        "x_label": x_field,
        "y_label": ", ".join(y_fields),
        "series": series,
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
        "series": [{"name": "size_by_rank", "x": x_vals, "y": y_vals}],
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
    summary_en = tex_en["summary"] or readme_summary
    summary_cn = tex_cn["summary"] or summary_en
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
