#!/usr/bin/env python3
from __future__ import annotations

import re
from typing import Any


def _json_path(path: list[str | int]) -> str:
    if not path:
        return "$"
    out = "$"
    for part in path:
        if isinstance(part, int):
            out += f"[{part}]"
        else:
            out += f".{part}"
    return out


def _validate_subset(instance: Any, schema: dict[str, Any], path: list[str | int], errors: list[str]) -> None:
    if "const" in schema and instance != schema["const"]:
        errors.append(f"{_json_path(path)}: expected const {schema['const']!r}, got {instance!r}")

    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{_json_path(path)}: value {instance!r} not in enum {schema['enum']!r}")

    stype = schema.get("type")
    if stype == "object":
        if not isinstance(instance, dict):
            errors.append(f"{_json_path(path)}: expected object, got {type(instance).__name__}")
            return
        required = schema.get("required", [])
        for key in required:
            if key not in instance:
                errors.append(f"{_json_path(path)}: missing required property {key!r}")
        properties = schema.get("properties", {})
        additional = schema.get("additionalProperties", True)
        for key, val in instance.items():
            if key in properties:
                _validate_subset(val, properties[key], [*path, key], errors)
            elif additional is False:
                errors.append(f"{_json_path(path)}: additional property {key!r} is not allowed")
        return

    if stype == "array":
        if not isinstance(instance, list):
            errors.append(f"{_json_path(path)}: expected array, got {type(instance).__name__}")
            return
        min_items = schema.get("minItems")
        if isinstance(min_items, int) and len(instance) < min_items:
            errors.append(f"{_json_path(path)}: expected at least {min_items} items, got {len(instance)}")
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for idx, val in enumerate(instance):
                _validate_subset(val, item_schema, [*path, idx], errors)
        return

    if stype == "string":
        if not isinstance(instance, str):
            errors.append(f"{_json_path(path)}: expected string, got {type(instance).__name__}")
            return
        pattern = schema.get("pattern")
        if isinstance(pattern, str) and re.match(pattern, instance) is None:
            errors.append(f"{_json_path(path)}: value {instance!r} does not match pattern {pattern!r}")
        return

    if stype == "integer":
        if not isinstance(instance, int) or isinstance(instance, bool):
            errors.append(f"{_json_path(path)}: expected integer, got {type(instance).__name__}")
            return
        minimum = schema.get("minimum")
        if isinstance(minimum, int) and instance < minimum:
            errors.append(f"{_json_path(path)}: expected >= {minimum}, got {instance}")
        return

    if stype == "boolean":
        if not isinstance(instance, bool):
            errors.append(f"{_json_path(path)}: expected boolean, got {type(instance).__name__}")
        return


def validate_with_schema(instance: Any, schema: dict[str, Any]) -> list[str]:
    try:
        import jsonschema  # type: ignore
    except Exception:
        errors: list[str] = []
        _validate_subset(instance, schema, [], errors)
        return errors

    validator = jsonschema.Draft202012Validator(schema)
    out: list[str] = []
    for err in sorted(validator.iter_errors(instance), key=lambda e: list(e.path)):
        out.append(f"{_json_path(list(err.path))}: {err.message}")
    return out
