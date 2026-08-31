#!/usr/bin/env python3
"""Fail-closed validation for v3 gating canary and production manifests."""

from __future__ import annotations

import argparse
import json
import math
from datetime import datetime
from pathlib import Path
from typing import Any, Mapping

from build_gating_campaign_manifest_v3 import (
    DEFAULT_FIELD_PACK,
    DEFAULT_FIELD_PACK_MANIFEST,
    DEFAULT_RUNNER_SOURCE,
    MANIFEST_SCHEMA,
    PRIMARY_CHECKPOINTS,
    TAIL_CHECKPOINTS,
    WALK_STREAMS,
    _canary_cells,
    _load_field_pack,
    _preregistration,
    _production_cells,
    _tail_cells,
    decode_production_cell_id,
    encode_production_cell_id,
    load_json,
    sha256_file,
    validate_sha256,
    walk_seed,
)

PLACEHOLDER_TOKENS = (
    "placeholder",
    "changeme",
    "replace_me",
    "replace-me",
    "todo",
    "tbd",
    "<sha",
    "<path",
    "<image",
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--field-pack", type=Path, default=DEFAULT_FIELD_PACK)
    parser.add_argument(
        "--field-pack-manifest", type=Path, default=DEFAULT_FIELD_PACK_MANIFEST
    )
    parser.add_argument("--runner-source", type=Path, default=DEFAULT_RUNNER_SOURCE)
    parser.add_argument(
        "--container-file",
        type=Path,
        help="Optionally verify the pinned container hash against a local SIF/image file.",
    )
    return parser.parse_args(argv)


def _mapping(value: Any, name: str) -> Mapping[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{name} must be an object")
    return value


def _array(value: Any, name: str) -> list[Any]:
    if not isinstance(value, list):
        raise ValueError(f"{name} must be an array")
    return value


def _walk_no_placeholders(value: Any, path: str = "$", *, key_name: str = "") -> None:
    if value is None:
        raise ValueError(f"{path} is null; frozen manifests may not contain placeholders")
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError(f"{path} is nonfinite")
    if isinstance(value, str):
        lowered = value.casefold()
        if any(token in lowered for token in PLACEHOLDER_TOKENS):
            raise ValueError(f"{path} contains a placeholder token")
        if "sha256" in key_name.casefold():
            validate_sha256(value, path)
        return
    if isinstance(value, list):
        for index, child in enumerate(value):
            _walk_no_placeholders(child, f"{path}[{index}]", key_name=key_name)
        return
    if isinstance(value, dict):
        for key, child in value.items():
            if not isinstance(key, str) or not key:
                raise ValueError(f"{path} contains a non-string or empty key")
            _walk_no_placeholders(child, f"{path}.{key}", key_name=key)


def _validate_defaults(manifest: Mapping[str, Any]) -> None:
    defaults = _mapping(manifest.get("defaults"), "defaults")
    expected = {
        "walkers": 1_000_000,
        "steps": 80_000,
        "batch_size": 131_072,
        "base_hold": 0.30,
        "target_radius": 3,
        "start_x": 7,
        "start_y": 24,
        "target1_x": 54,
        "target1_y": 24,
        "checkpoints": list(PRIMARY_CHECKPOINTS),
        "seed_base": 1_729,
    }
    if dict(defaults) != expected:
        raise ValueError("defaults differ from the frozen runner contract")
    profiles = _mapping(manifest.get("profiles"), "profiles")
    expected_profiles = {
        "tail_160k": {
            "steps": 160_000,
            "checkpoints": list(TAIL_CHECKPOINTS),
        }
    }
    if dict(profiles) != expected_profiles:
        raise ValueError("profiles differ from the frozen tail-escalation contract")


def _validate_campaign(manifest: Mapping[str, Any]) -> tuple[str, int, int]:
    campaign = _mapping(manifest.get("campaign"), "campaign")
    kind = campaign.get("kind")
    if kind not in ("canary", "production", "tail160k"):
        raise ValueError("campaign.kind must be 'canary', 'production', or 'tail160k'")
    created_utc = campaign.get("created_utc")
    if not isinstance(created_utc, str):
        raise ValueError("campaign.created_utc must be an ISO-8601 string")
    try:
        parsed = datetime.fromisoformat(created_utc)
    except ValueError as exc:
        raise ValueError("campaign.created_utc is not valid ISO-8601") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("campaign.created_utc must include a timezone offset")
    domain = _mapping(campaign.get("domain"), "campaign.domain")
    if kind == "tail160k" and campaign.get("activation_gate") != (
        "submit only when the verified 80k reducer tail gate is FAIL"
    ):
        raise ValueError("tail160k campaign is missing its frozen activation gate")
    if kind != "tail160k" and "activation_gate" in campaign:
        raise ValueError("only the tail160k campaign may define activation_gate")
    width = domain.get("width")
    height = domain.get("height")
    if isinstance(width, bool) or not isinstance(width, int):
        raise ValueError("campaign.domain.width must be an integer")
    if isinstance(height, bool) or not isinstance(height, int):
        raise ValueError("campaign.domain.height must be an integer")
    if (width, height) != (64, 48):
        raise ValueError("the frozen campaign domain must be width=64, height=48")
    return kind, width, height


def _validate_artifact_records(
    manifest: Mapping[str, Any],
    *,
    field_pack: Path | None,
    field_pack_manifest: Path | None,
    runner_source: Path | None,
    container_file: Path | None,
) -> tuple[int, int, int]:
    artifacts = _mapping(manifest.get("artifacts"), "artifacts")
    field_record = _mapping(artifacts.get("field_pack"), "artifacts.field_pack")
    runner_record = _mapping(artifacts.get("runner_source"), "artifacts.runner_source")
    container_record = _mapping(artifacts.get("container"), "artifacts.container")
    builder_record = _mapping(artifacts.get("manifest_builder"), "artifacts.manifest_builder")
    validator_record = _mapping(
        artifacts.get("manifest_validator"), "artifacts.manifest_validator"
    )

    top_pack_hash = validate_sha256(
        manifest.get("field_pack_sha256"), "field_pack_sha256"
    )
    if validate_sha256(field_record.get("sha256"), "artifacts.field_pack.sha256") != top_pack_hash:
        raise ValueError("top-level and artifact field-pack hashes differ")
    validate_sha256(
        field_record.get("sidecar_sha256"), "artifacts.field_pack.sidecar_sha256"
    )
    validate_sha256(runner_record.get("sha256"), "artifacts.runner_source.sha256")
    validate_sha256(container_record.get("sha256"), "artifacts.container.sha256")
    validate_sha256(builder_record.get("sha256"), "artifacts.manifest_builder.sha256")
    validate_sha256(validator_record.get("sha256"), "artifacts.manifest_validator.sha256")
    if not isinstance(container_record.get("reference"), str) or not container_record.get(
        "reference"
    ):
        raise ValueError("artifacts.container.reference must be a nonempty string")

    source = Path(__file__).resolve()
    builder_source = source.with_name("build_gating_campaign_manifest_v3.py")
    if sha256_file(builder_source) != builder_record["sha256"]:
        raise ValueError("manifest-builder source hash does not match this validator runtime")
    if sha256_file(source) != validator_record["sha256"]:
        raise ValueError("manifest-validator source hash does not match this validator runtime")

    if (field_pack is None) != (field_pack_manifest is None):
        raise ValueError("field_pack and field_pack_manifest must be supplied together")
    if field_pack is not None and field_pack_manifest is not None:
        contrasts, _seeds, actual_hash, _sidecar = _load_field_pack(
            field_pack, field_pack_manifest
        )
        if actual_hash != top_pack_hash:
            raise ValueError("live field pack does not match the manifest")
        if sha256_file(field_pack_manifest) != field_record["sidecar_sha256"]:
            raise ValueError("live field-pack sidecar does not match the manifest")
        field_count, height, width = contrasts.shape
    else:
        preregistration = _mapping(manifest.get("preregistration"), "preregistration")
        field_count = preregistration.get("field_count")
        campaign = _mapping(manifest.get("campaign"), "campaign")
        domain = _mapping(campaign.get("domain"), "campaign.domain")
        width, height = domain.get("width"), domain.get("height")
        if isinstance(field_count, bool) or not isinstance(field_count, int):
            raise ValueError("preregistration.field_count must be an integer")

    if runner_source is not None:
        if sha256_file(runner_source) != runner_record["sha256"]:
            raise ValueError("live runner source does not match the manifest")
    if container_file is not None:
        if sha256_file(container_file) != container_record["sha256"]:
            raise ValueError("live container file does not match the manifest")
    return int(field_count), int(width), int(height)


def _validate_preregistration(manifest: Mapping[str, Any], field_count: int) -> None:
    preregistration = _mapping(manifest.get("preregistration"), "preregistration")
    expected = _preregistration(field_count)
    if dict(preregistration) != expected:
        raise ValueError(
            "preregistration differs from the frozen geometry, ROPE, gates, stages, or budget"
        )
    budget = _mapping(preregistration.get("budget"), "preregistration.budget")
    if float(budget.get("unallocated_margin")) < 0.0:
        raise ValueError("campaign hard cap is below the frozen stage, precision, and reserve caps")


def _validate_cell_mapping(
    manifest: Mapping[str, Any], *, kind: str, field_count: int
) -> tuple[int, int]:
    raw_cells = _array(manifest.get("cells"), "cells")
    if kind == "canary":
        expected_cells = _canary_cells(field_count)
    elif kind == "production":
        expected_cells = _production_cells(field_count)
    else:
        expected_cells = _tail_cells(field_count)
    campaign = _mapping(manifest.get("campaign"), "campaign")
    if campaign.get("cell_count") != len(raw_cells):
        raise ValueError("campaign.cell_count does not equal len(cells)")
    if len(raw_cells) != len(expected_cells):
        raise ValueError(
            f"{kind} manifest has {len(raw_cells)} cells; expected {len(expected_cells)}"
        )

    seen_ids: set[int] = set()
    for index, (actual, expected) in enumerate(zip(raw_cells, expected_cells, strict=True)):
        if not isinstance(actual, dict):
            raise ValueError(f"cells[{index}] must be an object")
        if actual != expected:
            raise ValueError(
                f"cells[{index}] differs from the frozen {kind} task mapping; "
                f"expected={expected!r}, actual={actual!r}"
            )
        cell_id = actual["cell_id"]
        if cell_id in seen_ids:
            raise ValueError(f"duplicate cell_id: {cell_id}")
        seen_ids.add(cell_id)

    expected_ids = set(range(len(expected_cells)))
    if seen_ids != expected_ids:
        missing = sorted(expected_ids - seen_ids)
        extra = sorted(seen_ids - expected_ids)
        raise ValueError(f"noncontiguous cell IDs; missing={missing[:8]}, extra={extra[:8]}")

    if kind == "production":
        for cell in raw_cells:
            decoded = decode_production_cell_id(cell["cell_id"], field_count=field_count)
            encoded = encode_production_cell_id(
                geometry_index_value=decoded["geometry_index"],
                amplitude_index=decoded["amplitude_index"],
                field_index=decoded["field_index"],
                stream_index=decoded["stream_index"],
                field_count=field_count,
            )
            if encoded != cell["cell_id"]:
                raise ValueError(f"cell {cell['cell_id']} failed task-map round trip")

    occurrences: dict[tuple[int, int], set[tuple[float, int, int]]] = {}
    seed_by_pair: dict[tuple[int, int], int] = {}
    for cell in raw_cells:
        pair = (cell["disorder_replicate"], cell["walk_replicate"])
        seed = walk_seed(*pair)
        if pair in seed_by_pair and seed_by_pair[pair] != seed:
            raise ValueError("walk seed changed across amplitude or geometry")
        seed_by_pair[pair] = seed
        occurrences.setdefault(pair, set()).add(
            (cell["amplitude"], cell["target2_x"], cell["target2_y"])
        )
    expected_occurrences = {"canary": 2, "production": 15 * 6, "tail160k": 3 * 2}[
        kind
    ]
    for pair, conditions in occurrences.items():
        if len(conditions) != expected_occurrences:
            raise ValueError(
                f"CRN pair {pair} covers {len(conditions)} conditions; "
                f"expected {expected_occurrences}"
            )
    expected_pairs = (
        {(field_index, stream) for field_index in range(2) for stream in WALK_STREAMS}
        if kind == "canary"
        else {
            (field_index, stream)
            for field_index in range(field_count)
            for stream in WALK_STREAMS
        }
    )
    if set(seed_by_pair) != expected_pairs:
        raise ValueError("manifest does not cover the expected disorder/stream seed pairs")
    if len(set(seed_by_pair.values())) != len(seed_by_pair):
        raise ValueError("walk-seed schedule has a collision")
    return len(raw_cells), len(seed_by_pair)


def validate_manifest(
    manifest: Mapping[str, Any],
    *,
    field_pack: Path | None = None,
    field_pack_manifest: Path | None = None,
    runner_source: Path | None = None,
    container_file: Path | None = None,
) -> dict[str, Any]:
    """Validate a decoded manifest and return a compact audit summary."""

    _walk_no_placeholders(manifest)
    if manifest.get("schema") != MANIFEST_SCHEMA:
        raise ValueError(f"schema must be {MANIFEST_SCHEMA!r}")
    kind, campaign_width, campaign_height = _validate_campaign(manifest)
    _validate_defaults(manifest)
    field_count, pack_width, pack_height = _validate_artifact_records(
        manifest,
        field_pack=field_pack,
        field_pack_manifest=field_pack_manifest,
        runner_source=runner_source,
        container_file=container_file,
    )
    if (campaign_width, campaign_height) != (pack_width, pack_height):
        raise ValueError("campaign domain does not equal the field-pack contrast shape")
    _validate_preregistration(manifest, field_count)
    cell_count, crn_pair_count = _validate_cell_mapping(
        manifest, kind=kind, field_count=field_count
    )
    return {
        "schema": MANIFEST_SCHEMA,
        "campaign_kind": kind,
        "field_count": field_count,
        "cell_count": cell_count,
        "crn_pair_count": crn_pair_count,
        "task_mapping": "valid",
        "rope": "valid",
        "gates": "valid",
        "placeholders": 0,
    }


def validate_manifest_file(
    path: Path,
    *,
    field_pack: Path | None = None,
    field_pack_manifest: Path | None = None,
    runner_source: Path | None = None,
    container_file: Path | None = None,
) -> dict[str, Any]:
    manifest = load_json(path)
    return validate_manifest(
        manifest,
        field_pack=field_pack,
        field_pack_manifest=field_pack_manifest,
        runner_source=runner_source,
        container_file=container_file,
    )


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    summary = validate_manifest_file(
        args.manifest,
        field_pack=args.field_pack,
        field_pack_manifest=args.field_pack_manifest,
        runner_source=args.runner_source,
        container_file=args.container_file,
    )
    summary["manifest"] = str(args.manifest)
    summary["manifest_sha256"] = sha256_file(args.manifest)
    print(json.dumps(summary, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
