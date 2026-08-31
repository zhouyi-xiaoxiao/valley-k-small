#!/usr/bin/env python3
"""Generate a deterministic, provenance-rich v3 disorder-field pack.

Each field starts as independent standard-normal white noise, is smoothed with
``scipy.ndimage.gaussian_filter`` in ``reflect`` mode, and is normalized to
exact zero mean (under ``math.fsum``) and exact unit maximum absolute value.
The resulting NPZ is byte-deterministic for a fixed NumPy/SciPy runtime.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import os
import platform
import sys
import tempfile
import time
import zipfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable

import numpy as np

PACK_SCHEMA = "grid2d-one-two-target-gating-disorder-field-pack-v3"
DEFAULT_FIELD_COUNT = 32
MAX_FIELD_COUNT = 128
DEFAULT_WIDTH = 64
DEFAULT_HEIGHT = 48
DEFAULT_SIGMA = 4.0
DEFAULT_SEED_BASE = 20_260_726
DEFAULT_SEED_STRIDE = 7_919
GAUSSIAN_TRUNCATE = 4.0

REPORT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPORT_ROOT / "artifacts" / "data"
DEFAULT_OUTPUT_PACK = DATA_DIR / "disorder_field_pack_v3.npz"
DEFAULT_OUTPUT_MANIFEST = DATA_DIR / "disorder_field_pack_v3.manifest.json"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-pack", type=Path, default=DEFAULT_OUTPUT_PACK)
    parser.add_argument("--output-manifest", type=Path, default=DEFAULT_OUTPUT_MANIFEST)
    parser.add_argument("--field-count", type=int, default=DEFAULT_FIELD_COUNT)
    parser.add_argument("--width", type=int, default=DEFAULT_WIDTH)
    parser.add_argument("--height", type=int, default=DEFAULT_HEIGHT)
    parser.add_argument("--sigma", type=float, default=DEFAULT_SIGMA)
    parser.add_argument("--seed-base", type=int, default=DEFAULT_SEED_BASE)
    parser.add_argument("--seed-stride", type=int, default=DEFAULT_SEED_STRIDE)
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace existing output files after validating all arguments.",
    )
    return parser.parse_args(argv)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _validate_parameters(
    *, field_count: int, width: int, height: int, sigma: float, seed_base: int, seed_stride: int
) -> None:
    if not 1 <= field_count <= MAX_FIELD_COUNT:
        raise ValueError(f"field_count must be in [1, {MAX_FIELD_COUNT}]")
    if width < 1 or height < 1:
        raise ValueError("width and height must be positive")
    if not math.isfinite(sigma) or sigma <= 0.0:
        raise ValueError("sigma must be a positive finite number")
    if seed_base < 0 or seed_stride < 1:
        raise ValueError("seed_base must be nonnegative and seed_stride must be positive")
    if seed_base + (field_count - 1) * seed_stride > np.iinfo(np.int64).max:
        raise ValueError("seed schedule exceeds signed int64")


def disorder_seed(index: int, *, seed_base: int, seed_stride: int) -> int:
    if index < 0:
        raise ValueError("field index must be nonnegative")
    return seed_base + seed_stride * index


def _normalize_exact_zero_mean_unit_max(field: np.ndarray) -> np.ndarray:
    """Return float64 data with fsum(data)==0 and max(abs(data))==1.

    One maximum-magnitude entry is kept as an exact +/-1 anchor.  A separate
    low-magnitude entry absorbs the final floating-point summation residual,
    so enforcing exact zero sum cannot move the unit anchor.
    """

    result = np.asarray(field, dtype=np.float64).copy(order="C")
    if result.ndim != 2 or result.size < 2:
        raise ValueError("a field must be a two-dimensional array with at least two cells")
    if not np.isfinite(result).all():
        raise ValueError("field contains nonfinite values before normalization")

    result -= float(result.mean(dtype=np.float64))
    maximum = float(np.max(np.abs(result)))
    if not math.isfinite(maximum) or maximum <= 0.0:
        raise ValueError("smoothed field has no finite nonzero contrast")
    result /= maximum

    flat = result.reshape(-1)
    anchor_index = int(np.argmax(np.abs(flat)))
    flat[anchor_index] = math.copysign(1.0, float(flat[anchor_index]))
    candidate_indices = np.arange(flat.size)
    candidate_indices = candidate_indices[candidate_indices != anchor_index]
    correction_index = int(candidate_indices[np.argmin(np.abs(flat[candidate_indices]))])

    for _ in range(16):
        residual = math.fsum(float(value) for value in flat)
        if residual == 0.0:
            break
        flat[correction_index] = float(flat[correction_index]) - residual
    exact_sum = math.fsum(float(value) for value in flat)
    if exact_sum != 0.0:
        raise ArithmeticError(f"could not force exact zero sum; residual={exact_sum!r}")
    if float(np.max(np.abs(flat))) != 1.0:
        raise ArithmeticError("unit maximum-absolute-value invariant failed")
    return np.asarray(result, dtype="<f8", order="C")


def generate_contrast_field(
    *, seed: int, height: int, width: int, sigma: float
) -> np.ndarray:
    """Generate one transparent Gaussian-smoothed white-noise contrast field."""

    try:
        from scipy.ndimage import gaussian_filter
    except ImportError as exc:  # pragma: no cover - exercised by the CLI environment
        raise RuntimeError("SciPy is required to generate v3 disorder fields") from exc

    generator = np.random.Generator(np.random.PCG64(seed))
    white_noise = generator.standard_normal(
        size=(height, width), dtype=np.float64
    )
    smoothed = gaussian_filter(
        white_noise,
        sigma=float(sigma),
        order=0,
        mode="reflect",
        cval=0.0,
        truncate=GAUSSIAN_TRUNCATE,
    )
    return _normalize_exact_zero_mean_unit_max(smoothed)


def _npy_bytes(array: np.ndarray) -> bytes:
    buffer = io.BytesIO()
    np.lib.format.write_array(buffer, np.ascontiguousarray(array), allow_pickle=False)
    return buffer.getvalue()


def _write_deterministic_npz(path: Path, members: Iterable[tuple[str, np.ndarray]]) -> None:
    """Write an NPZ without current-time ZIP metadata."""

    with zipfile.ZipFile(path, mode="w", compression=zipfile.ZIP_STORED) as archive:
        for name, array in members:
            info = zipfile.ZipInfo(f"{name}.npy", date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_STORED
            info.create_system = 3
            info.external_attr = 0o600 << 16
            archive.writestr(info, _npy_bytes(array))


def _atomic_json_write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
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
        if temporary.exists():
            temporary.unlink()


def generate_field_pack(
    *,
    output_pack: Path,
    output_manifest: Path,
    field_count: int = DEFAULT_FIELD_COUNT,
    width: int = DEFAULT_WIDTH,
    height: int = DEFAULT_HEIGHT,
    sigma: float = DEFAULT_SIGMA,
    seed_base: int = DEFAULT_SEED_BASE,
    seed_stride: int = DEFAULT_SEED_STRIDE,
    overwrite: bool = False,
    argv: list[str] | None = None,
) -> dict[str, Any]:
    """Generate the NPZ and JSON manifest, returning the manifest payload."""

    _validate_parameters(
        field_count=field_count,
        width=width,
        height=height,
        sigma=sigma,
        seed_base=seed_base,
        seed_stride=seed_stride,
    )
    if output_pack.resolve() == output_manifest.resolve():
        raise ValueError("pack and manifest outputs must be different files")
    existing = [path for path in (output_pack, output_manifest) if path.exists()]
    if existing and not overwrite:
        raise FileExistsError(
            "refusing to replace existing output(s): " + ", ".join(str(path) for path in existing)
        )

    started = time.perf_counter()
    seeds = np.asarray(
        [
            disorder_seed(index, seed_base=seed_base, seed_stride=seed_stride)
            for index in range(field_count)
        ],
        dtype="<i8",
    )
    contrasts = np.empty((field_count, height, width), dtype="<f8")
    field_records: list[dict[str, Any]] = []
    for index, seed in enumerate(seeds.tolist()):
        field_started = time.perf_counter()
        contrast = generate_contrast_field(
            seed=int(seed), height=height, width=width, sigma=sigma
        )
        contrasts[index] = contrast
        field_records.append(
            {
                "index": index,
                "seed": int(seed),
                "sigma": float(sigma),
                "sha256_float64_le": sha256_bytes(contrast.tobytes(order="C")),
                "exact_sum_fsum": math.fsum(float(value) for value in contrast.reshape(-1)),
                "numpy_mean": float(contrast.mean(dtype=np.float64)),
                "minimum": float(contrast.min()),
                "maximum": float(contrast.max()),
                "max_abs": float(np.max(np.abs(contrast))),
                "standard_deviation": float(contrast.std(dtype=np.float64)),
                "generation_seconds": time.perf_counter() - field_started,
            }
        )

    output_pack.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{output_pack.name}.", dir=output_pack.parent
    )
    os.close(descriptor)
    temporary_pack = Path(temporary_name)
    try:
        _write_deterministic_npz(
            temporary_pack,
            (
                ("contrasts", contrasts),
                ("seeds", seeds),
                ("sigma", np.asarray(float(sigma), dtype="<f8")),
            ),
        )
        os.replace(temporary_pack, output_pack)
    finally:
        if temporary_pack.exists():
            temporary_pack.unlink()

    source = Path(__file__).resolve()
    try:
        import scipy

        scipy_version = scipy.__version__
    except ImportError:  # pragma: no cover - generation already fails first
        scipy_version = "unavailable"
    manifest: dict[str, Any] = {
        "schema": PACK_SCHEMA,
        "created_utc": datetime.now(UTC).isoformat(),
        "definition": {
            "field_count": field_count,
            "shape": [field_count, height, width],
            "dtype": "float64-little-endian",
            "white_noise": "numpy.random.Generator(PCG64).standard_normal(float64)",
            "smoothing": {
                "implementation": "scipy.ndimage.gaussian_filter",
                "sigma": float(sigma),
                "order": 0,
                "mode": "reflect",
                "truncate": GAUSSIAN_TRUNCATE,
            },
            "normalization": {
                "centering": "subtract float64 numpy mean, then exact math.fsum correction",
                "exact_zero_mean_reduction": "math.fsum over C-order float64 values",
                "scale": "maximum absolute value equals exactly 1.0",
            },
        },
        "seed_schedule": {
            "formula": "seed_base + seed_stride * field_index",
            "seed_base": seed_base,
            "seed_stride": seed_stride,
        },
        "fields": field_records,
        "pack": {
            "filename": output_pack.name,
            "byte_count": output_pack.stat().st_size,
            "sha256": sha256_file(output_pack),
            "members": {
                "contrasts": {
                    "shape": list(contrasts.shape),
                    "dtype": str(contrasts.dtype),
                    "sha256_array_bytes": sha256_bytes(contrasts.tobytes(order="C")),
                },
                "seeds": {
                    "shape": list(seeds.shape),
                    "dtype": str(seeds.dtype),
                    "sha256_array_bytes": sha256_bytes(seeds.tobytes(order="C")),
                },
                "sigma": {"value": float(sigma), "dtype": "float64"},
            },
        },
        "provenance": {
            "generator_source": source.name,
            "generator_source_sha256": sha256_file(source),
            "argv": list(sys.argv if argv is None else argv),
        },
        "runtime": {
            "elapsed_seconds": time.perf_counter() - started,
            "hostname": platform.node(),
            "platform": platform.platform(),
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy_version,
        },
    }
    _atomic_json_write(output_manifest, manifest)
    return manifest


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    manifest = generate_field_pack(
        output_pack=args.output_pack,
        output_manifest=args.output_manifest,
        field_count=args.field_count,
        width=args.width,
        height=args.height,
        sigma=args.sigma,
        seed_base=args.seed_base,
        seed_stride=args.seed_stride,
        overwrite=args.overwrite,
        argv=list(sys.argv if argv is None else argv),
    )
    print(
        json.dumps(
            {
                "schema": manifest["schema"],
                "field_count": manifest["definition"]["field_count"],
                "pack_sha256": manifest["pack"]["sha256"],
                "manifest": str(args.output_manifest),
            },
            sort_keys=True,
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
