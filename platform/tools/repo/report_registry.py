#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class RegistryEntry:
    id: str
    aliases: list[str]
    path: str
    manuscript_dir: str
    artifact_dir: str
    main_tex: list[str]
    entry_scripts: list[str]
    languages: list[str]
    archive_policy: str
    status: str


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def registry_path() -> Path:
    return repo_root() / "research" / "reports" / "report_registry.yaml"


def _strip_quotes(value: str) -> str:
    value = value.strip()
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    return value


def _parse_inline_list(value: str) -> list[str]:
    value = value.strip()
    if value == "[]":
        return []
    if not (value.startswith("[") and value.endswith("]")):
        raise ValueError(f"Expected inline list, got: {value}")
    body = value[1:-1].strip()
    if not body:
        return []
    parts = [p.strip() for p in body.split(",")]
    return [_strip_quotes(p) for p in parts if p]


def load_registry_payload(path: Path | None = None) -> dict[str, Any]:
    path = path or registry_path()
    lines = path.read_text(encoding="utf-8").splitlines()

    version: int | None = None
    reports: list[dict[str, Any]] = []
    cur: dict[str, Any] | None = None

    for raw in lines:
        line = raw.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue

        if line.startswith("version:"):
            version = int(line.split(":", 1)[1].strip())
            continue

        if line.strip() == "reports:":
            continue

        if line.startswith("  - "):
            if cur is not None:
                reports.append(cur)
            cur = {}
            body = line[4:]
            key, value = body.split(":", 1)
            cur[key.strip()] = _strip_quotes(value.strip())
            continue

        if line.startswith("    ") and cur is not None:
            body = line.strip()
            key, value = body.split(":", 1)
            key = key.strip()
            value = value.strip()
            if value.startswith("["):
                cur[key] = _parse_inline_list(value)
            else:
                cur[key] = _strip_quotes(value)
            continue

        raise ValueError(f"Unsupported registry line: {line}")

    if cur is not None:
        reports.append(cur)

    if version is None:
        raise ValueError("Missing version in report registry")

    return {"version": version, "reports": reports}


def load_registry(path: Path | None = None) -> list[dict[str, Any]]:
    payload = load_registry_payload(path)
    return list(payload["reports"])


def resolve_report(token: str, registry: list[dict[str, Any]]) -> dict[str, Any]:
    key = token.strip()
    for item in registry:
        names = {item["id"], Path(item["path"]).name, *item.get("aliases", [])}
        if key in names:
            return item
    raise KeyError(f"Unknown report '{token}'")


def render_registry_yaml(payload: dict[str, Any]) -> str:
    lines: list[str] = [f"version: {int(payload['version'])}", "reports:"]
    for item in payload.get("reports", []):
        lines.append(f"  - id: {item['id']}")
        lines.append(f"    aliases: [{', '.join(item.get('aliases', []))}]")
        lines.append(f"    path: {item['path']}")
        lines.append(f"    manuscript_dir: {item['manuscript_dir']}")
        lines.append(f"    artifact_dir: {item['artifact_dir']}")
        lines.append(f"    main_tex: [{', '.join(item.get('main_tex', []))}]")
        lines.append(f"    entry_scripts: [{', '.join(item.get('entry_scripts', []))}]")
        lines.append(f"    languages: [{', '.join(item.get('languages', []))}]")
        lines.append(f"    archive_policy: {item['archive_policy']}")
        lines.append(f"    status: {item['status']}")
    return "\n".join(lines) + "\n"
