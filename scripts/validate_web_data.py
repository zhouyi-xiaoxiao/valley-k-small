#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Any

try:
    from jsonschema import Draft202012Validator
except ModuleNotFoundError:  # pragma: no cover
    Draft202012Validator = None  # type: ignore[assignment]


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_ROOT = REPO_ROOT / "site" / "public" / "data" / "v1"
WEB_SCHEMA_PATH = REPO_ROOT / "schemas" / "web_report.schema.json"
AGENT_SCHEMA_PATH = REPO_ROOT / "schemas" / "agent_sync_v1.schema.json"
THEORY_SCHEMA_PATH = REPO_ROOT / "schemas" / "theory_map_v1.schema.json"
CONTENT_SCHEMA_PATH = REPO_ROOT / "schemas" / "content_map_v1.schema.json"
BOOK_MANIFEST_SCHEMA_PATH = REPO_ROOT / "schemas" / "book_manifest_v1.schema.json"
BOOK_CHAPTER_SCHEMA_PATH = REPO_ROOT / "schemas" / "book_chapter_v1.schema.json"
BOOK_BACKBONE_SCHEMA_PATH = REPO_ROOT / "schemas" / "book_backbone_v1.schema.json"
GLOSSARY_SCHEMA_PATH = REPO_ROOT / "schemas" / "glossary_v1.schema.json"
TRANSLATION_QC_SCHEMA_PATH = REPO_ROOT / "schemas" / "translation_qc_v1.schema.json"


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_with_schema(payload: Any, schema: dict[str, Any], label: str) -> None:
    if Draft202012Validator is None:
        return
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(payload), key=lambda e: list(e.path))
    if errors:
        first = errors[0]
        path = "/".join(str(p) for p in first.path)
        raise ValueError(f"{label}: {first.message} @ {path}")


def normalize_finding_key(text: str) -> str:
    value = str(text).strip().lower()
    value = value.replace("`", "")
    value = value.replace("\\", "")
    value = " ".join(value.split())
    return "".join(ch for ch in value if ch.isalnum())


def looks_like_path_finding(text: str) -> bool:
    lowered = str(text).lower().strip()
    if lowered.startswith("see ") and "report assets" in lowered:
        return True
    if lowered.startswith("figures:") or lowered.startswith("environment:"):
        return True
    return "/" in lowered and any(tok in lowered for tok in ("reports/", "scripts/", "config/"))


def assert_text_quality(meta_payload: dict[str, Any], label: str) -> None:
    suspect_patterns = [
        ("raw_itemize", r"\bitemize\b"),
        ("double_backslash", r"\\\\"),
        ("empty_math_marker", r"\s_[,.;:]"),
        ("ellipsis_truncation", r"\.\.\.|…"),
        ("math_alignment_fragment", r"&="),
        ("broken_aw_token", r"\bt\s*t\s*\^\s*[a-z0-9_]+\b"),
        ("range_fragment", r"\b\d+\s*,\s*\.\.\.\s*,\s*[a-z0-9]+\b"),
        ("malformed_peak_token", r"\b[a-z]\s+p\d+\b"),
        ("double_comma_token", r"\b\d+\s*,\s*,\s*[a-z0-9]+\b"),
        ("malformed_k_pair", r"\bK\s+\d+\s*,\s*\d+\b"),
        ("malformed_probability_token", r"\bP\s*:\s*[0-9]+\b"),
        ("truncated_tail_all", r",\s*all\s*$"),
    ]
    fields = [str(meta_payload.get("summary", ""))]
    narrative = meta_payload.get("narrative", {})
    if isinstance(narrative, dict):
        for key in ("model_overview", "method_overview", "result_overview"):
            fields.append(str(narrative.get(key, "")))
    for text in fields:
        if not text:
            continue
        for name, pattern in suspect_patterns:
            if re.search(pattern, text, flags=re.IGNORECASE):
                raise SystemExit(f"Low readability in {label}: detected {name} pattern")
    findings = [str(x).strip() for x in meta_payload.get("key_findings", []) if str(x).strip()]
    non_placeholder = [x for x in findings if not (x.lower().startswith("see ") and "report assets" in x.lower())]
    if findings and not non_placeholder:
        raise SystemExit(f"Low readability in {label}: key_findings are placeholders only")
    for idx, card in enumerate(meta_payload.get("section_cards", []), start=1):
        heading = str(card.get("heading", "")).strip().lower()
        summary = str(card.get("summary", "")).strip().lower()
        if not summary:
            raise SystemExit(f"Low readability in {label}: section_cards[{idx}] has empty summary")
        if summary == heading:
            raise SystemExit(f"Low readability in {label}: section_cards[{idx}] duplicates heading text only")
        if re.search(r"section summary\.?$", summary):
            raise SystemExit(f"Low readability in {label}: section_cards[{idx}] contains placeholder summary")
        if "fallback narrative card" in summary:
            raise SystemExit(f"Low readability in {label}: section_cards[{idx}] contains fallback placeholder")
        for name, pattern in suspect_patterns:
            if re.search(pattern, summary, flags=re.IGNORECASE):
                raise SystemExit(f"Low readability in {label}: section_cards[{idx}] detected {name} pattern")


def assert_locale_parity(meta_en: dict[str, Any], meta_cn: dict[str, Any], label: str) -> None:
    key_fields = (
        "key_findings",
        "math_blocks",
        "math_story",
        "section_cards",
        "reproducibility_commands",
        "source_documents",
    )
    strict_fields = {"math_blocks", "math_story", "section_cards"}
    for field in key_fields:
        left = meta_en.get(field, [])
        right = meta_cn.get(field, [])
        if not isinstance(left, list) or not isinstance(right, list):
            raise SystemExit(f"Locale parity error in {label}: field {field} must be list in both locales")
        if not left and right:
            raise SystemExit(f"Locale parity error in {label}: EN {field} is empty while CN is non-empty")
        if not right and left:
            raise SystemExit(f"Locale parity error in {label}: CN {field} is empty while EN is non-empty")
        if left and right:
            ratio = min(len(left), len(right)) / max(1, max(len(left), len(right)))
            min_ratio = 1.0 if field in strict_fields else 0.9
            if ratio < min_ratio:
                raise SystemExit(
                    f"Locale parity error in {label}: field {field} has severe mismatch (EN={len(left)}, CN={len(right)})"
                )


def assert_repro_commands(meta_payload: dict[str, Any], label: str) -> None:
    commands = [str(x).strip() for x in meta_payload.get("reproducibility_commands", []) if str(x).strip()]
    if not commands:
        raise SystemExit(f"Reproducibility gate failed in {label}: reproducibility_commands is empty")
    placeholder_patterns = (
        r"^todo\b",
        r"^n/?a$",
        r"placeholder",
    )
    for cmd in commands:
        lowered = cmd.lower()
        if any(re.search(pattern, lowered, flags=re.IGNORECASE) for pattern in placeholder_patterns):
            raise SystemExit(f"Reproducibility gate failed in {label}: placeholder command '{cmd}'")


def run_katex_lint(formulas: list[dict[str, str]]) -> list[dict[str, str]]:
    if not formulas:
        return []
    script = r"""
const fs = require('fs');
let katex = null;
let loadError = null;
for (const candidate of ['katex', './site/node_modules/katex']) {
  try {
    katex = require(candidate);
    break;
  } catch (err) {
    loadError = err;
  }
}
if (!katex) {
  process.stdout.write(JSON.stringify({
    skipped: true,
    reason: 'katex_module_unavailable',
    error: String(loadError && loadError.message ? loadError.message : loadError || '')
  }));
  process.exit(0);
}
const payload = JSON.parse(fs.readFileSync(0, 'utf8'));
const errors = [];
for (const row of payload) {
  try {
    katex.renderToString(row.latex, { throwOnError: true, displayMode: true, strict: 'error' });
  } catch (err) {
    errors.push({
      report_id: row.report_id || '',
      lang: row.lang || '',
      context: row.context || '',
      latex: row.latex || '',
      error: String(err && err.message ? err.message : err)
    });
  }
}
process.stdout.write(JSON.stringify({ errors }));
"""
    proc = subprocess.run(
        ["node", "-e", script],
        cwd=REPO_ROOT,
        input=json.dumps(formulas, ensure_ascii=False),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if proc.returncode != 0:
        raise SystemExit(f"KaTeX lint failed to run: {proc.stdout.strip()[:1200]}")
    try:
        parsed = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"KaTeX lint invalid JSON output: {exc}") from exc
    if parsed.get("skipped"):
        return []
    errors = parsed.get("errors", [])
    if not isinstance(errors, list):
        raise SystemExit("KaTeX lint output malformed: errors is not a list")
    return errors


def assert_series_semantics(series_payload: dict[str, Any], label: str) -> None:
    series = list(series_payload.get("series", []))
    semantics = list(series_payload.get("series_semantics", []))
    if not series:
        raise SystemExit(f"Semantic payload error in {label}: empty series array")
    if not semantics:
        raise SystemExit(f"Semantic payload error in {label}: missing series_semantics")

    sem_by_name: dict[str, dict[str, Any]] = {}
    for item in semantics:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name", "")).strip()
        if name:
            sem_by_name[name] = item

    for row in series:
        if not isinstance(row, dict):
            continue
        name = str(row.get("name", "")).strip()
        if not name:
            raise SystemExit(f"Semantic payload error in {label}: unnamed series row")
        semantic = sem_by_name.get(name)
        if semantic is None:
            raise SystemExit(f"Semantic payload error in {label}: missing semantic row for series '{name}'")
        declared_type = str(row.get("series_type", "")).strip()
        semantic_type = str(semantic.get("series_type", "")).strip()
        if declared_type and semantic_type and declared_type != semantic_type:
            raise SystemExit(
                f"Semantic payload error in {label}: series_type mismatch for '{name}' ({declared_type} vs {semantic_type})"
            )
        declared_unit = str(row.get("unit", "")).strip()
        semantic_unit = str(semantic.get("unit", "")).strip()
        if declared_unit and semantic_unit and declared_unit != semantic_unit:
            raise SystemExit(
                f"Semantic payload error in {label}: unit mismatch for '{name}' ({declared_unit} vs {semantic_unit})"
            )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate web + agent sync payloads.")
    parser.add_argument("--data-root", type=Path, default=DEFAULT_DATA_ROOT)
    parser.add_argument("--web-schema", type=Path, default=WEB_SCHEMA_PATH)
    parser.add_argument("--agent-schema", type=Path, default=AGENT_SCHEMA_PATH)
    parser.add_argument("--theory-schema", type=Path, default=THEORY_SCHEMA_PATH)
    parser.add_argument("--content-schema", type=Path, default=CONTENT_SCHEMA_PATH)
    parser.add_argument("--book-manifest-schema", type=Path, default=BOOK_MANIFEST_SCHEMA_PATH)
    parser.add_argument("--book-chapter-schema", type=Path, default=BOOK_CHAPTER_SCHEMA_PATH)
    parser.add_argument("--book-backbone-schema", type=Path, default=BOOK_BACKBONE_SCHEMA_PATH)
    parser.add_argument("--glossary-schema", type=Path, default=GLOSSARY_SCHEMA_PATH)
    parser.add_argument("--translation-qc-schema", type=Path, default=TRANSLATION_QC_SCHEMA_PATH)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    data_root: Path = args.data_root

    index_path = data_root / "index.json"
    if not index_path.exists():
        raise SystemExit(f"Missing index file: {index_path}")

    web_schema = read_json(args.web_schema)
    agent_schema = read_json(args.agent_schema)
    theory_schema = read_json(args.theory_schema)
    content_schema = read_json(args.content_schema)
    book_manifest_schema = read_json(args.book_manifest_schema)
    book_chapter_schema = read_json(args.book_chapter_schema)
    book_backbone_schema = read_json(args.book_backbone_schema)
    glossary_schema = read_json(args.glossary_schema)
    translation_qc_schema = read_json(args.translation_qc_schema)

    index_payload = read_json(index_path)
    reports = list(index_payload.get("reports", []))
    finding_report_ids: dict[str, set[str]] = {}
    finding_examples: dict[str, str] = {}
    formulas_for_lint: list[dict[str, str]] = []

    for item in reports:
        report_id = item["report_id"]
        report_dir = data_root / "reports" / report_id
        if not report_dir.exists():
            raise SystemExit(f"Missing report dir: {report_dir}")
        meta_en_path = report_dir / "meta.json"
        meta_cn_path = report_dir / "meta.cn.json"
        if not meta_en_path.exists():
            raise SystemExit(f"Missing meta file: {meta_en_path}")
        if not meta_cn_path.exists():
            raise SystemExit(f"Missing meta file: {meta_cn_path}")

        meta_en = read_json(meta_en_path)
        meta_cn = read_json(meta_cn_path)
        validate_with_schema(meta_en, web_schema, str(meta_en_path))
        validate_with_schema(meta_cn, web_schema, str(meta_cn_path))
        assert_text_quality(meta_en, str(meta_en_path))
        assert_text_quality(meta_cn, str(meta_cn_path))
        assert_repro_commands(meta_en, str(meta_en_path))
        assert_repro_commands(meta_cn, str(meta_cn_path))
        assert_locale_parity(meta_en, meta_cn, str(report_id))

        for meta_payload, meta_path in ((meta_en, meta_en_path), (meta_cn, meta_cn_path)):
            for dataset in meta_payload.get("datasets", []):
                rel = dataset.get("series_path", "")
                if not isinstance(rel, str) or not rel.startswith("/data/v1/"):
                    raise SystemExit(f"Invalid series_path in {meta_path}: {rel}")
                series_path = data_root.parent.parent / rel.lstrip("/")
                if not series_path.exists():
                    raise SystemExit(f"Missing series file: {series_path}")
                series_payload = read_json(series_path)
                assert_series_semantics(series_payload, str(series_path))

            lang = str(meta_payload.get("lang", "en"))
            for block in meta_payload.get("math_blocks", []):
                latex = str(block.get("latex", "")).strip()
                if latex:
                    formulas_for_lint.append(
                        {
                            "report_id": str(report_id),
                            "lang": lang,
                            "context": str(block.get("context", "math_blocks")),
                            "latex": latex,
                        }
                    )
            for block in meta_payload.get("math_story", []):
                latex = str(block.get("latex", "")).strip()
                if latex:
                    formulas_for_lint.append(
                        {
                            "report_id": str(report_id),
                            "lang": lang,
                            "context": str(block.get("context", "math_story")),
                            "latex": latex,
                        }
                    )

        for finding in meta_en.get("key_findings", []):
            text = str(finding).strip()
            if not text or looks_like_path_finding(text):
                continue
            key = normalize_finding_key(text)
            if not key:
                continue
            finding_report_ids.setdefault(key, set()).add(str(report_id))
            finding_examples.setdefault(key, text)

    manifest_path = data_root / "agent" / "manifest.json"
    reports_jsonl = data_root / "agent" / "reports.jsonl"
    events_jsonl = data_root / "agent" / "events.jsonl"
    book_manifest_json = data_root / "agent" / "book_manifest.json"
    book_chapters_jsonl = data_root / "agent" / "book_chapters.jsonl"
    claim_graph_jsonl = data_root / "agent" / "claim_graph.jsonl"
    translation_qc_json = data_root / "agent" / "translation_qc.json"
    guide_json = data_root / "agent" / "guide.json"

    if (
        not manifest_path.exists()
        or not reports_jsonl.exists()
        or not events_jsonl.exists()
        or not book_manifest_json.exists()
        or not book_chapters_jsonl.exists()
        or not claim_graph_jsonl.exists()
        or not translation_qc_json.exists()
        or not guide_json.exists()
    ):
        raise SystemExit("Missing one or more agent sync files")

    manifest_payload = read_json(manifest_path)
    validate_with_schema(manifest_payload, agent_schema["$defs"]["manifest"], str(manifest_path))

    theory_map_path = data_root / "theory_map.json"
    if not theory_map_path.exists():
        raise SystemExit(f"Missing theory map file: {theory_map_path}")
    theory_map = read_json(theory_map_path)
    validate_with_schema(theory_map, theory_schema, str(theory_map_path))

    report_network_path = data_root / "report_network.json"
    if not report_network_path.exists():
        raise SystemExit(f"Missing report network file: {report_network_path}")
    report_network = read_json(report_network_path)
    if not isinstance(report_network, dict):
        raise SystemExit("Invalid report network payload: expected object")
    nodes = list(report_network.get("reports", []))
    if len(nodes) != len(reports):
        raise SystemExit(
            f"Invalid report network payload: reports length mismatch ({len(nodes)} vs {len(reports)})"
        )

    content_map_path = data_root / "content_map.json"
    if not content_map_path.exists():
        raise SystemExit(f"Missing content map file: {content_map_path}")
    content_map = read_json(content_map_path)
    validate_with_schema(content_map, content_schema, str(content_map_path))
    if int(content_map.get("report_count", -1)) != len(reports):
        raise SystemExit(
            f"Invalid content map payload: report_count mismatch ({content_map.get('report_count')} vs {len(reports)})"
        )
    claim_rows = list(content_map.get("claims", []))
    claim_report_ids = {str(row.get("report_id", "")).strip() for row in claim_rows if str(row.get("report_id", "")).strip()}
    report_ids = {str(item.get("report_id", "")).strip() for item in reports if str(item.get("report_id", "")).strip()}
    missing_claim_reports = sorted(report_ids - claim_report_ids)
    if missing_claim_reports:
        raise SystemExit(
            "Invalid content map payload: some reports have no claims: "
            + ",".join(missing_claim_reports[:10])
        )
    claims_without_evidence = [str(row.get("claim_id", "")) for row in claim_rows if not list(row.get("evidence", []))]
    if claims_without_evidence:
        raise SystemExit(
            "Invalid content map payload: claims missing evidence: "
            + ",".join(claims_without_evidence[:12])
        )

    book_root = data_root / "book"
    book_manifest_path = book_root / "book_manifest.json"
    book_backbone_path = book_root / "backbone.json"
    book_toc_path = book_root / "toc.json"
    glossary_path = data_root / "glossary" / "terms.json"

    if not book_manifest_path.exists():
        raise SystemExit(f"Missing book manifest: {book_manifest_path}")
    if not book_backbone_path.exists():
        raise SystemExit(f"Missing book backbone: {book_backbone_path}")
    if not book_toc_path.exists():
        raise SystemExit(f"Missing book toc: {book_toc_path}")
    if not glossary_path.exists():
        raise SystemExit(f"Missing glossary terms: {glossary_path}")

    book_manifest_payload = read_json(book_manifest_path)
    book_backbone_payload = read_json(book_backbone_path)
    book_toc_payload = read_json(book_toc_path)
    glossary_payload = read_json(glossary_path)
    translation_qc_payload = read_json(translation_qc_json)

    validate_with_schema(book_manifest_payload, book_manifest_schema, str(book_manifest_path))
    validate_with_schema(book_backbone_payload, book_backbone_schema, str(book_backbone_path))
    validate_with_schema(glossary_payload, glossary_schema, str(glossary_path))
    validate_with_schema(translation_qc_payload, translation_qc_schema, str(translation_qc_json))

    toc_en = list(book_toc_payload.get("en", []))
    toc_cn = list(book_toc_payload.get("cn", []))
    chapter_rows = list(book_manifest_payload.get("chapters", []))
    if len(toc_en) != len(chapter_rows) or len(toc_cn) != len(chapter_rows):
        raise SystemExit(
            "Invalid book toc payload: chapter count mismatch "
            f"(toc_en={len(toc_en)}, toc_cn={len(toc_cn)}, chapters={len(chapter_rows)})"
        )

    chapter_ids = {str(row.get("chapter_id", "")).strip() for row in chapter_rows if str(row.get("chapter_id", "")).strip()}
    if len(chapter_ids) != len(chapter_rows):
        raise SystemExit("Invalid book manifest: duplicate chapter_id detected")
    if int(book_backbone_payload.get("chapter_count", -1)) != len(chapter_rows):
        raise SystemExit(
            "Invalid book backbone: chapter_count mismatch "
            f"({book_backbone_payload.get('chapter_count')} vs {len(chapter_rows)})"
        )
    spine_rows = list(book_backbone_payload.get("chapter_spine", []))
    spine_ids = {str(row.get("chapter_id", "")).strip() for row in spine_rows if str(row.get("chapter_id", "")).strip()}
    if spine_ids != chapter_ids:
        missing_from_spine = sorted(chapter_ids - spine_ids)
        unknown_in_spine = sorted(spine_ids - chapter_ids)
        raise SystemExit(
            "Invalid book backbone: chapter coverage mismatch "
            f"(missing={missing_from_spine[:8]}, unknown={unknown_in_spine[:8]})"
        )

    for chapter in chapter_rows:
        chapter_id = str(chapter.get("chapter_id", "")).strip()
        chapter_path = book_root / "chapters" / f"{chapter_id}.json"
        if not chapter_path.exists():
            raise SystemExit(f"Missing chapter payload: {chapter_path}")
        chapter_payload = read_json(chapter_path)
        validate_with_schema(chapter_payload, book_chapter_schema, str(chapter_path))
        if len(chapter_payload.get("interactive_panels", [])) < 1:
            raise SystemExit(f"Invalid chapter payload: no interactive panels in {chapter_id}")
        if len(chapter_payload.get("claim_ledger", [])) < 1:
            raise SystemExit(f"Invalid chapter payload: no claim ledger rows in {chapter_id}")
        for claim in chapter_payload.get("claim_ledger", []):
            if not list(claim.get("evidence", [])):
                raise SystemExit(
                    f"Invalid chapter payload: claim without evidence in {chapter_id}: {claim.get('claim_id')}"
                )

    report_chapter_map = book_manifest_payload.get("report_chapter_map", {})
    missing_book_links = sorted([rid for rid in report_ids if rid not in report_chapter_map])
    if missing_book_links:
        raise SystemExit(
            "Invalid book manifest: some reports are not mapped to chapters: "
            + ",".join(missing_book_links[:10])
        )

    if not bool(translation_qc_payload.get("passed", False)):
        stats = translation_qc_payload.get("stats", {})
        raise SystemExit(
            "Translation QC gate failed: "
            f"high={stats.get('high', 'n/a')} warning={stats.get('warning', 'n/a')}"
        )

    report_record_schema = agent_schema["$defs"]["report_record"]
    for idx, line in enumerate(reports_jsonl.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        payload = json.loads(line)
        validate_with_schema(payload, report_record_schema, f"reports.jsonl:{idx}")

    event_schema = agent_schema["$defs"]["event_record"]
    for idx, line in enumerate(events_jsonl.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        payload = json.loads(line)
        validate_with_schema(payload, event_schema, f"events.jsonl:{idx}")

    chapter_record_schema = agent_schema["$defs"]["book_chapter_record"]
    for idx, line in enumerate(book_chapters_jsonl.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        payload = json.loads(line)
        validate_with_schema(payload, chapter_record_schema, f"book_chapters.jsonl:{idx}")

    claim_graph_schema = agent_schema["$defs"]["claim_graph_record"]
    for idx, line in enumerate(claim_graph_jsonl.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        payload = json.loads(line)
        validate_with_schema(payload, claim_graph_schema, f"claim_graph.jsonl:{idx}")

    duplicates = [
        {
            "text": finding_examples[key],
            "report_ids": sorted(report_ids),
        }
        for key, report_ids in finding_report_ids.items()
        if len(report_ids) > 1
    ]
    if duplicates:
        first = duplicates[0]
        raise SystemExit(
            "Duplicate key findings detected across reports: "
            f"{first['text']} (reports={','.join(first['report_ids'])})"
        )

    formula_errors = run_katex_lint(formulas_for_lint)
    if formula_errors:
        first = formula_errors[0]
        raise SystemExit(
            "KaTeX renderability check failed: "
            f"{len(formula_errors)} formula(s) invalid; first at report={first.get('report_id')} "
            f"lang={first.get('lang')} context={first.get('context')} error={first.get('error')}"
        )

    print(
        json.dumps(
            {
                "ok": True,
                "reports": len(reports),
                "book_chapters": len(chapter_rows),
                "book_backbone_chapters": len(spine_rows),
                "index": index_path.as_posix(),
                "agent_manifest": manifest_path.as_posix(),
                "formula_count": len(formulas_for_lint),
                "translation_qc": translation_qc_json.as_posix(),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
