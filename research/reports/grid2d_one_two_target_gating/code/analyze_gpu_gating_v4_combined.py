#!/usr/bin/env python3
"""Fail-closed v4-only and combined 160-block max-|t| analysis."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import os
import tempfile
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np

SCHEMA = "grid2d-one-two-target-gating-v4-combined-max-t-v1"
GEOMETRIES = tuple((x, y) for x in (24, 32, 40) for y in (9, 16, 24, 31, 38))
TREATMENTS = (0.05, 0.10, 0.15, 0.20, 0.25)
AMPLITUDES = (0.0, *TREATMENTS)
CSV_FIELDS = ("contrast_index", "target2_x", "target2_y", "control_amplitude", "treatment_amplitude", "n_disorder_blocks", "mean_effect", "standard_error", "observed_t", "simultaneous_ci_lower", "simultaneous_ci_upper", "adjusted_p_value")
UPSTREAM_FIELDS = ("row_type", "condition_id", "comparison_id", "profile", "disorder_replicate", "walk_replicates", "steps", "target2_x", "target2_y", "amplitude", "gating_probability_drop", "gating_probability_drop_t_half", "gating_tail_delta", "one_unresolved_probability", "two_unresolved_probability", "diversion_probability", "acceleration_probability", "target2_first_probability", "primary_paired_effect")


class AuditError(RuntimeError):
    pass


def require(value: bool, message: str) -> None:
    if not value:
        raise AuditError(message)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    require(path.is_file() and not path.is_symlink(), f"missing/symlinked input {path}")
    def strict(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result = {}
        for key, value in pairs:
            require(key not in result, f"duplicate JSON key {key!r}"); result[key] = value
        return result
    value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=strict)
    require(isinstance(value, dict), "JSON root must be object")
    return value


def reduction_values(json_path: Path, csv_path: Path, *, blocks: int, schema: str) -> tuple[dict[tuple[int, int, float, int], float], dict[str, Any]]:
    payload = load_json(json_path)
    audit = payload.get("audit")
    require(payload.get("schema") == schema and isinstance(audit, dict) and audit.get("pass") is True, "reducer audit/schema gate failed")
    sacct = audit.get("sacct")
    require(isinstance(sacct, dict) and sacct.get("verified") is True, "reducer sacct gate failed")
    csv_record = payload.get("csv")
    require(isinstance(csv_record, dict) and csv_record.get("sha256") == sha256_file(csv_path), "reducer CSV hash drift")
    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle); require(tuple(reader.fieldnames or ()) == UPSTREAM_FIELDS, "reducer CSV header drift"); rows = list(reader)
    expected_rows = 15 * 6 * blocks + blocks
    require(len(rows) == expected_rows == csv_record.get("rows"), "reducer CSV row count drift")
    values: dict[tuple[int, int, float, int], float] = {}
    primary_count = 0
    for row in rows:
        if row["row_type"] == "primary_pair":
            primary_count += 1; continue
        require(row["row_type"] == "block_mean" and row["walk_replicates"] == "0;1", "unexpected row type or stream aggregation")
        try:
            key = (int(row["target2_x"]), int(row["target2_y"]), float(row["amplitude"]), int(row["disorder_replicate"]))
            value = float(row["gating_probability_drop"])
        except ValueError as exc:
            raise AuditError(f"invalid CSV scalar: {exc}") from exc
        require(math.isfinite(value) and key not in values, f"duplicate/nonfinite block {key}")
        values[key] = value
    expected = {(x, y, amplitude, block) for x, y in GEOMETRIES for amplitude in AMPLITUDES for block in range(blocks)}
    require(set(values) == expected and primary_count == blocks, "scientific block inventory drift")
    return values, {"json_sha256": sha256_file(json_path), "csv_sha256": sha256_file(csv_path), "inventory_digest": audit.get("inventory_digest"), "tail_gate": payload.get("tail_gate"), "primary": payload.get("primary")}


def effect_matrix(values: Mapping[tuple[int, int, float, int], float], blocks: int) -> np.ndarray:
    columns = [(x, y, amplitude) for x, y in GEOMETRIES for amplitude in TREATMENTS]
    matrix = np.empty((blocks, 75), dtype=np.float64)
    for column, (x, y, amplitude) in enumerate(columns):
        for block in range(blocks):
            matrix[block, column] = values[(x, y, amplitude, block)] - values[(x, y, 0.0, block)]
    return matrix


def max_t(matrix: np.ndarray, *, seed: int, resamples: int) -> dict[str, Any]:
    blocks, contrasts = matrix.shape
    require(contrasts == 75 and blocks in (128, 160), "max-t matrix shape drift")
    means = matrix.mean(axis=0); se = matrix.std(axis=0, ddof=1) / math.sqrt(blocks)
    require(bool(np.isfinite(se).all()) and bool(np.all(se > 0)), "zero/nonfinite observed SE")
    observed = means / se
    rng = np.random.Generator(np.random.PCG64(seed)); maxima = np.empty(resamples)
    for start in range(0, resamples, 125):
        stop = min(start + 125, resamples)
        indices = rng.integers(0, blocks, size=(stop - start, blocks), dtype=np.int64)
        sample = matrix[indices]
        sample_se = sample.std(axis=1, ddof=1) / math.sqrt(blocks)
        require(bool(np.all(sample_se > 0)) and bool(np.isfinite(sample_se).all()), "bootstrap zero/nonfinite SE")
        maxima[start:stop] = np.max(np.abs((sample.mean(axis=1) - means) / sample_se), axis=1)
    critical_one_indexed = math.ceil((resamples + 1) * 0.95)
    critical = float(np.sort(maxima)[critical_one_indexed - 1])
    adjusted = (1 + np.sum(maxima[:, None] >= np.abs(observed)[None, :], axis=0)) / (resamples + 1)
    rows = []
    columns = [(x, y, amplitude) for x, y in GEOMETRIES for amplitude in TREATMENTS]
    for i, (x, y, amplitude) in enumerate(columns):
        rows.append({"contrast_index": i, "target2_x": x, "target2_y": y, "control_amplitude": 0.0, "treatment_amplitude": amplitude, "n_disorder_blocks": blocks, "mean_effect": float(means[i]), "standard_error": float(se[i]), "observed_t": float(observed[i]), "simultaneous_ci_lower": float(means[i] - critical * se[i]), "simultaneous_ci_upper": float(means[i] + critical * se[i]), "adjusted_p_value": float(adjusted[i])})
    return {"blocks": blocks, "seed": seed, "resamples": resamples, "critical_order_statistic_one_indexed": critical_one_indexed, "critical_value": critical, "rows": rows}


def analyze(v3_json: Path, v3_csv: Path, v4_json: Path, v4_csv: Path) -> dict[str, Any]:
    v3, v3_prov = reduction_values(v3_json, v3_csv, blocks=32, schema="grid2d-one-two-target-gating-gpu-v3-reduction-v1")
    v4, v4_prov = reduction_values(v4_json, v4_csv, blocks=128, schema="grid2d-one-two-target-gating-gpu-v4-reduction-v1")
    v3_effects = effect_matrix(v3, 32); v4_effects = effect_matrix(v4, 128)
    combined = np.vstack((v3_effects, v4_effects))
    # Pack heterogeneity was frozen before pooling: report all 75 differences,
    # plus the primary contrast at geometry (32,24), amplitude .20.
    delta = v4_effects.mean(axis=0) - v3_effects.mean(axis=0)
    pooled_se = np.sqrt(v4_effects.var(axis=0, ddof=1) / 128 + v3_effects.var(axis=0, ddof=1) / 32)
    columns = [(x, y, amplitude) for x, y in GEOMETRIES for amplitude in TREATMENTS]
    heterogeneity = [{"contrast_index": i, "target2_x": x, "target2_y": y, "amplitude": amplitude, "v4_minus_v3_mean": float(delta[i]), "welch_standard_error": float(pooled_se[i]), "welch_t": float(delta[i] / pooled_se[i]) if pooled_se[i] > 0 else None} for i, (x, y, amplitude) in enumerate(columns)]
    return {"schema": SCHEMA, "status": "PASS_V4_AND_COMBINED_MAX_T", "audit": {"pass": True, "v3": v3_prov, "v4": v4_prov, "exact_combined_blocks": 160}, "method": {"inference_unit": "disorder block after averaging streams 0 and 1", "joint_surface_contrasts": 75, "bit_generator": "PCG64", "combined_seed": 2026072701, "combined_resamples": 20000, "tail_diagnostics": "retained verbatim from both strict reducers"}, "v4_only": max_t(v4_effects, seed=2026072700, resamples=20000), "combined": max_t(combined, seed=2026072701, resamples=20000), "pack_heterogeneity": heterogeneity}


def csv_bytes(rows: Sequence[Mapping[str, Any]]) -> bytes:
    buffer = io.StringIO(newline=""); writer = csv.DictWriter(buffer, fieldnames=CSV_FIELDS, lineterminator="\n"); writer.writeheader()
    for row in rows: writer.writerow({key: row[key] for key in CSV_FIELDS})
    return buffer.getvalue().encode()


def commit(path: Path, data: bytes) -> None:
    require(not path.exists(), f"refusing to overwrite {path}"); path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent); temp = Path(name)
    try:
        with os.fdopen(fd, "wb") as handle: handle.write(data); handle.flush(); os.fsync(handle.fileno())
        os.chmod(temp, 0o600); os.link(temp, path)
    finally: temp.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("v3_json", "v3_csv", "v4_json", "v4_csv", "output_json", "output_csv"): parser.add_argument("--" + name.replace("_", "-"), dest=name, type=Path, required=True)
    args = parser.parse_args()
    try:
        payload = analyze(args.v3_json, args.v3_csv, args.v4_json, args.v4_csv)
        data_csv = csv_bytes(payload["combined"]["rows"])
        payload["csv"] = {"filename": args.output_csv.name, "sha256": hashlib.sha256(data_csv).hexdigest(), "rows": 75}
        data_json = (json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()
        require(not args.output_json.exists() and not args.output_csv.exists(), "outputs already exist")
        commit(args.output_csv, data_csv)
        try: commit(args.output_json, data_json)
        except BaseException: args.output_csv.unlink(missing_ok=True); raise
    except AuditError as exc:
        print(f"FAIL-CLOSED: {exc}", file=os.sys.stderr); return 2
    print(json.dumps({"status": payload["status"], "blocks": 160, "critical": payload["combined"]["critical_value"]}, sort_keys=True)); return 0


if __name__ == "__main__":
    raise SystemExit(main())
