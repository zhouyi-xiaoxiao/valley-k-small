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


EN_WHITELIST = {
    "fpt",
    "aw",
    "fft",
    "hazard",
    "survival",
    "beta",
    "selfloop",
    "renormalize",
    "equal4",
    "grid",
    "ring",
    "claim",
    "katex",
    "jsonl",
    "manifest",
    "schema",
    "pdf",
    "tex",
}


def utc_now_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def normalize_text(text: str) -> str:
    value = str(text or "")
    value = re.sub(r"\\[A-Za-z]+", " ", value)
    value = re.sub(r"\$[^$]{0,240}\$", " ", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value


def excerpt(text: str, max_chars: int = 160) -> str:
    clean = normalize_text(text)
    if len(clean) <= max_chars:
        return clean
    return clean[: max_chars - 1].rstrip() + "…"


def load_glossary_tokens(data_root: Path) -> tuple[set[str], set[str]]:
    glossary_path = data_root / "glossary" / "terms.json"
    allow_cn: set[str] = set()
    allow_en: set[str] = set(EN_WHITELIST)
    if not glossary_path.exists():
        return allow_cn, allow_en
    payload = read_json(glossary_path)
    for term in payload.get("terms", []):
        for key in ("term_cn",):
            token = str(term.get(key, "")).strip()
            if token:
                allow_cn.add(token)
        for key in ("term_en",):
            token = str(term.get(key, "")).strip().lower()
            if token:
                allow_en.add(token)
        for token in term.get("aliases_en", []):
            word = str(token).strip().lower()
            if word:
                allow_en.add(word)
    return allow_cn, allow_en


def find_en_violations(text: str, allow_cn: set[str]) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    normalized = normalize_text(text)
    for match in re.finditer(r"[\u4e00-\u9fff]{2,}", normalized):
        segment = match.group(0)
        if any(segment in token for token in allow_cn):
            continue
        if len(segment) >= 4:
            issues.append(("high", segment))
        else:
            issues.append(("warning", segment))
    return issues


def english_phrase_segments(text: str) -> list[str]:
    pattern = re.compile(r"\b(?:[A-Za-z][A-Za-z0-9\-/]{2,})(?:\s+[A-Za-z][A-Za-z0-9\-/]{2,}){3,}\b")
    normalized = normalize_text(text)
    return [m.group(0) for m in pattern.finditer(normalized)]


def find_cn_violations(text: str, allow_en: set[str]) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    normalized = normalize_text(text)
    letters = len(re.findall(r"[A-Za-z]", normalized))
    cjk = len(re.findall(r"[\u4e00-\u9fff]", normalized))
    mostly_english = letters >= 40 and cjk < 8
    for phrase in english_phrase_segments(normalized):
        if any(token in phrase for token in ("/", "\\", ".py", ".json", ".tex", ".pdf", "--", "reports", "scripts")):
            continue
        if re.search(r"\d", phrase):
            continue
        words = [w.lower() for w in re.findall(r"[A-Za-z][A-Za-z0-9\-/]{1,}", phrase)]
        unknown = [w for w in words if w not in allow_en]
        if len(unknown) >= 8:
            issues.append(("warning" if mostly_english else "high", phrase))
        elif len(unknown) >= 6:
            issues.append(("warning", phrase))

    if letters >= 120 and letters > cjk * 3:
        issues.append(("warning" if mostly_english else "high", normalized[:120]))
    return issues


def iter_report_fields(meta: dict[str, Any]) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    out.append(("title", str(meta.get("title", ""))))
    out.append(("summary", str(meta.get("summary", ""))))
    narrative = meta.get("narrative", {})
    for key in ("model_overview", "method_overview", "result_overview"):
        out.append((f"narrative.{key}", str(narrative.get(key, ""))))
    return out


def iter_book_fields(chapter: dict[str, Any], lang: str) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    if lang == "en":
        out.append(("title_en", str(chapter.get("title_en", ""))))
        out.append(("summary_en", str(chapter.get("summary_en", ""))))
        for idx, row in enumerate(chapter.get("intro_en", []), start=1):
            out.append((f"intro_en[{idx}]", str(row)))
    else:
        out.append(("title_cn", str(chapter.get("title_cn", ""))))
        out.append(("summary_cn", str(chapter.get("summary_cn", ""))))
        for idx, row in enumerate(chapter.get("intro_cn", []), start=1):
            out.append((f"intro_cn[{idx}]", str(row)))

    for idx, row in enumerate(chapter.get("concept_cards", []), start=1):
        if lang == "en":
            out.append((f"concept_cards[{idx}].label_en", str(row.get("label_en", ""))))
            out.append((f"concept_cards[{idx}].description_en", str(row.get("description_en", ""))))
        else:
            out.append((f"concept_cards[{idx}].label_cn", str(row.get("label_cn", ""))))
            out.append((f"concept_cards[{idx}].description_cn", str(row.get("description_cn", ""))))

    for idx, row in enumerate(chapter.get("linked_reports", []), start=1):
        if lang == "en":
            out.append((f"linked_reports[{idx}].summary_en", str(row.get("summary_en", ""))))
            out.append((f"linked_reports[{idx}].book_role_en", str(row.get("book_role_en", ""))))
        else:
            out.append((f"linked_reports[{idx}].summary_cn", str(row.get("summary_cn", ""))))
            out.append((f"linked_reports[{idx}].book_role_cn", str(row.get("book_role_cn", ""))))

    for idx, row in enumerate(chapter.get("claim_ledger", []), start=1):
        if lang == "en":
            out.append((f"claim_ledger[{idx}].text_en", str(row.get("text_en", ""))))
        else:
            out.append((f"claim_ledger[{idx}].text_cn", str(row.get("text_cn", ""))))
    return out


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate CN/EN purity for report and book payloads.")
    parser.add_argument("--data-root", type=Path, default=DEFAULT_DATA_ROOT)
    parser.add_argument("--high-max", type=int, default=0)
    parser.add_argument("--warning-max", type=int, default=80)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    data_root: Path = args.data_root

    index_path = data_root / "index.json"
    if not index_path.exists():
        raise SystemExit(f"Missing index: {index_path}")

    allow_cn, allow_en = load_glossary_tokens(data_root)
    index = read_json(index_path)
    issues: list[dict[str, str]] = []
    scanned = 0

    def push_issue(*, severity: str, scope: str, location: str, lang: str, field: str, text: str, message: str) -> None:
        issues.append(
            {
                "severity": severity,
                "scope": scope,
                "location": location,
                "lang": lang,
                "field": field,
                "excerpt": excerpt(text),
                "message": message,
            }
        )

    for row in index.get("reports", []):
        rid = str(row.get("report_id", "")).strip()
        if not rid:
            continue
        languages = {str(x).strip().lower() for x in row.get("languages", []) if str(x).strip()}
        report_dir = data_root / "reports" / rid
        meta_en_path = report_dir / "meta.json"
        meta_cn_path = report_dir / "meta.cn.json"
        if meta_en_path.exists() and ("en" in languages or not languages):
            meta_en = read_json(meta_en_path)
            for field, text in iter_report_fields(meta_en):
                scanned += 1
                for severity, segment in find_en_violations(text, allow_cn):
                    push_issue(
                        severity=severity,
                        scope="report",
                        location=rid,
                        lang="en",
                        field=field,
                        text=segment,
                        message="EN text contains non-whitelisted Chinese segment.",
                    )
        if meta_cn_path.exists() and "cn" in languages:
            meta_cn = read_json(meta_cn_path)
            for field, text in iter_report_fields(meta_cn):
                scanned += 1
                for severity, segment in find_cn_violations(text, allow_en):
                    push_issue(
                        severity=severity,
                        scope="report",
                        location=rid,
                        lang="cn",
                        field=field,
                        text=segment,
                        message="CN text contains long non-whitelisted English phrase.",
                    )

    chapter_dir = data_root / "book" / "chapters"
    if chapter_dir.exists():
        for path in sorted(chapter_dir.glob("*.json")):
            chapter = read_json(path)
            chapter_id = str(chapter.get("chapter_id", path.stem))
            for field, text in iter_book_fields(chapter, "en"):
                scanned += 1
                for severity, segment in find_en_violations(text, allow_cn):
                    push_issue(
                        severity=severity,
                        scope="book",
                        location=chapter_id,
                        lang="en",
                        field=field,
                        text=segment,
                        message="Book EN text contains non-whitelisted Chinese segment.",
                    )
            for field, text in iter_book_fields(chapter, "cn"):
                scanned += 1
                for severity, segment in find_cn_violations(text, allow_en):
                    push_issue(
                        severity=severity,
                        scope="book",
                        location=chapter_id,
                        lang="cn",
                        field=field,
                        text=segment,
                        message="Book CN text contains long non-whitelisted English phrase.",
                    )

    high = sum(1 for item in issues if item["severity"] == "high")
    warning = sum(1 for item in issues if item["severity"] == "warning")
    passed = high <= int(args.high_max) and warning <= int(args.warning_max)

    payload = {
        "version": "v1",
        "generated_at": utc_now_iso(),
        "passed": passed,
        "thresholds": {
            "high_max": int(args.high_max),
            "warning_max": int(args.warning_max),
        },
        "stats": {
            "scanned_text_blocks": scanned,
            "high": high,
            "warning": warning,
        },
        "issues": issues[:400],
    }

    output_path = data_root / "agent" / "translation_qc.json"
    write_json(output_path, payload)

    print(json.dumps({"ok": passed, "output": output_path.as_posix(), "stats": payload["stats"]}, ensure_ascii=False, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
