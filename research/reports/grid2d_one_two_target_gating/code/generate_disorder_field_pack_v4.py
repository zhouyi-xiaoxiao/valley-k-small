#!/usr/bin/env python3
"""Generate the frozen independent 128-field v4 disorder pack."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import os
import tempfile
import zipfile
from pathlib import Path

import numpy as np
from scipy.ndimage import gaussian_filter

SCHEMA = "grid2d-one-two-target-gating-disorder-field-pack-v4"
FIELD_COUNT = 128
WIDTH = 64
HEIGHT = 48
SIGMA = 4.0
SEED_BASE = 8_202_607_270_000
SEED_STRIDE = 1_000_003
REPORT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PACK = REPORT_ROOT / "artifacts/data/disorder_field_pack_v4.npz"
DEFAULT_SIDECAR = REPORT_ROOT / "artifacts/data/disorder_field_pack_v4.manifest.json"


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalize_exact(field: np.ndarray) -> np.ndarray:
    result = np.asarray(field, dtype="<f8").copy(order="C")
    result -= float(result.mean(dtype=np.float64))
    scale = float(np.max(np.abs(result)))
    if not math.isfinite(scale) or scale <= 0:
        raise ValueError("degenerate field")
    result /= scale
    flat = result.reshape(-1)
    anchor = int(np.argmax(np.abs(flat)))
    flat[anchor] = math.copysign(1.0, float(flat[anchor]))
    candidates = np.delete(np.arange(flat.size), anchor)
    correction = int(candidates[np.argmin(np.abs(flat[candidates]))])
    for _ in range(32):
        residual = math.fsum(float(value) for value in flat)
        if residual == 0.0:
            break
        flat[correction] = float(flat[correction]) - residual
    if math.fsum(float(value) for value in flat) != 0.0:
        raise ArithmeticError("exact math.fsum zero invariant failed")
    if float(np.max(np.abs(flat))) != 1.0:
        raise ArithmeticError("exact maxabs-one invariant failed")
    return result


def generate_field(index: int) -> tuple[int, np.ndarray]:
    if not 0 <= index < FIELD_COUNT:
        raise ValueError("field index outside 0..127")
    seed = SEED_BASE + SEED_STRIDE * index
    rng = np.random.Generator(np.random.PCG64(seed))
    white = rng.standard_normal((HEIGHT, WIDTH), dtype=np.float64)
    smooth = gaussian_filter(white, sigma=SIGMA, mode="wrap", truncate=4.0)
    return seed, normalize_exact(smooth)


def _npy_bytes(array: np.ndarray) -> bytes:
    buffer = io.BytesIO()
    np.lib.format.write_array(buffer, np.ascontiguousarray(array), allow_pickle=False)
    return buffer.getvalue()


def _write_pack(path: Path, contrasts: np.ndarray, seeds: np.ndarray) -> None:
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_STORED) as archive:
        for name, array in (("contrasts", contrasts), ("seeds", seeds), ("sigma", np.asarray(SIGMA, dtype="<f8"))):
            info = zipfile.ZipInfo(f"{name}.npy", (1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_STORED
            info.create_system = 3
            info.external_attr = 0o600 << 16
            archive.writestr(info, _npy_bytes(array))


def _atomic_json(path: Path, payload: dict) -> None:
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True, allow_nan=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def build(pack: Path, sidecar: Path) -> dict:
    if pack.exists() or sidecar.exists():
        raise FileExistsError("v4 pack outputs are append-only")
    pack.parent.mkdir(parents=True, exist_ok=True)
    seeds = np.empty(FIELD_COUNT, dtype="<i8")
    contrasts = np.empty((FIELD_COUNT, HEIGHT, WIDTH), dtype="<f8")
    records = []
    for index in range(FIELD_COUNT):
        seed, contrast = generate_field(index)
        seeds[index] = seed
        contrasts[index] = contrast
        records.append({
            "index": index,
            "seed": seed,
            "sha256_float64_le": sha256_bytes(contrast.tobytes(order="C")),
            "exact_sum_fsum": math.fsum(float(x) for x in contrast.reshape(-1)),
            "max_abs": float(np.max(np.abs(contrast))),
        })
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{pack.name}.", dir=pack.parent)
    os.close(descriptor)
    temporary = Path(temporary_name)
    try:
        _write_pack(temporary, contrasts, seeds)
        os.replace(temporary, pack)
    finally:
        temporary.unlink(missing_ok=True)
    payload = {
        "schema": SCHEMA,
        "definition": {
            "shape": [FIELD_COUNT, HEIGHT, WIDTH], "sigma": SIGMA,
            "rng": "NumPy PCG64", "seed_base": SEED_BASE, "seed_stride": SEED_STRIDE,
            "smoothing": {"function": "scipy.ndimage.gaussian_filter", "mode": "wrap", "truncate": 4.0},
            "normalization": "exact math.fsum zero and exact maxabs one",
        },
        "pack": {"filename": pack.name, "sha256": sha256_file(pack)},
        "fields": records,
        "generator": {"filename": Path(__file__).name, "sha256": sha256_file(Path(__file__))},
    }
    _atomic_json(sidecar, payload)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-pack", type=Path, default=DEFAULT_PACK)
    parser.add_argument("--output-sidecar", type=Path, default=DEFAULT_SIDECAR)
    args = parser.parse_args()
    payload = build(args.output_pack.absolute(), args.output_sidecar.absolute())
    print(json.dumps({"status": "PASS", "pack_sha256": payload["pack"]["sha256"], "fields": FIELD_COUNT}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
