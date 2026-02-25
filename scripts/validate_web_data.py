#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
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

    for item in reports:
        report_id = item["report_id"]
        report_dir = data_root / "reports" / report_id
        if not report_dir.exists():
            raise SystemExit(f"Missing report dir: {report_dir}")

        for meta_name in ("meta.json", "meta.cn.json"):
            meta_path = report_dir / meta_name
            if not meta_path.exists():
                raise SystemExit(f"Missing meta file: {meta_path}")
            meta_payload = read_json(meta_path)
            validate_with_schema(meta_payload, web_schema, str(meta_path))
            assert_text_quality(meta_payload, str(meta_path))

            for dataset in meta_payload.get("datasets", []):
                rel = dataset.get("series_path", "")
                if not isinstance(rel, str) or not rel.startswith("/data/v1/"):
                    raise SystemExit(f"Invalid series_path in {meta_path}: {rel}")
                series_path = data_root.parent.parent / rel.lstrip("/")
                if not series_path.exists():
                    raise SystemExit(f"Missing series file: {series_path}")

            if meta_name == "meta.json":
                for finding in meta_payload.get("key_findings", []):
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

    print(
        json.dumps(
            {
                "ok": True,
                "reports": len(reports),
                "index": index_path.as_posix(),
                "agent_manifest": manifest_path.as_posix(),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
