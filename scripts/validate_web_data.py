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
            if re.search(pattern, text):
                raise SystemExit(f"Low readability in {label}: detected {name} pattern")
    findings = [str(x).strip() for x in meta_payload.get("key_findings", []) if str(x).strip()]
    non_placeholder = [x for x in findings if not (x.lower().startswith("see ") and "report assets" in x.lower())]
    if findings and not non_placeholder:
        raise SystemExit(f"Low readability in {label}: key_findings are placeholders only")


def assert_locale_parity(meta_en: dict[str, Any], meta_cn: dict[str, Any], label: str) -> None:
    key_fields = (
        "key_findings",
        "math_blocks",
        "math_story",
        "section_cards",
        "reproducibility_commands",
        "source_documents",
    )
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
            if ratio < 0.9:
                raise SystemExit(
                    f"Locale parity error in {label}: field {field} has severe mismatch (EN={len(left)}, CN={len(right)})"
                )


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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate web + agent sync payloads.")
    parser.add_argument("--data-root", type=Path, default=DEFAULT_DATA_ROOT)
    parser.add_argument("--web-schema", type=Path, default=WEB_SCHEMA_PATH)
    parser.add_argument("--agent-schema", type=Path, default=AGENT_SCHEMA_PATH)
    parser.add_argument("--theory-schema", type=Path, default=THEORY_SCHEMA_PATH)
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
        assert_locale_parity(meta_en, meta_cn, str(report_id))

        for meta_payload, meta_path in ((meta_en, meta_en_path), (meta_cn, meta_cn_path)):
            for dataset in meta_payload.get("datasets", []):
                rel = dataset.get("series_path", "")
                if not isinstance(rel, str) or not rel.startswith("/data/v1/"):
                    raise SystemExit(f"Invalid series_path in {meta_path}: {rel}")
                series_path = data_root.parent.parent / rel.lstrip("/")
                if not series_path.exists():
                    raise SystemExit(f"Missing series file: {series_path}")

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
    guide_json = data_root / "agent" / "guide.json"

    if not manifest_path.exists() or not reports_jsonl.exists() or not events_jsonl.exists() or not guide_json.exists():
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
                "index": index_path.as_posix(),
                "agent_manifest": manifest_path.as_posix(),
                "formula_count": len(formulas_for_lint),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
