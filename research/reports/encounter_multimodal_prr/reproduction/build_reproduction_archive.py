#!/usr/bin/env python3
"""Refresh the clean reproduction tree, checksum manifest, and release ZIP.

Run only after the article, Supplemental Material, robustness JSON files, and
W1--W5 figures have reached their final state.  The script copies an explicit
allow-list and therefore excludes logs, locks, caches, temporary LaTeX files,
and raw development material.
"""

from __future__ import annotations

import argparse
import hashlib
import shutil
import zipfile
from pathlib import Path


REPRODUCTION = Path(__file__).resolve().parent
REPORT = REPRODUCTION.parent
ARCHIVE_NAME = "encounter_multimodal_prr_reproduction_v1"
ARCHIVE = REPRODUCTION / ARCHIVE_NAME
ZIP_PATH = REPRODUCTION / f"{ARCHIVE_NAME}.zip"

CODE_FILES = (
    "validate_exact_m_offlattice.py",
    "exact_m_offlattice_production.py",
    "exact_m_prr_upgrade_core.py",
    "exact_m_prr_upgrade_preflight.py",
    "exact_m_prr_upgrade_w1.py",
    "exact_m_prr_upgrade_w2.py",
    "exact_m_prr_upgrade_w3.py",
    "exact_m_prr_upgrade_w4.py",
    "exact_m_prr_upgrade_w5.py",
    "exact_m_prr_upgrade_campaign_summary.py",
    "exact_m_prr_robustness.py",
)
ANALYSIS_FILES = (
    "b0_dyson_numerics.py",
    "b0_dyson_chaincheck.py",
)
FIGURE_STEMS = (
    "exact_m_phase_diagram_m2_prr",
    "exact_m_phase_diagram_m3_prr",
    "exact_m_b0_empirical_prr",
    "exact_m_jitter_robustness_prr",
    "exact_m_m5_demo_prr",
    "exact_m_d3_spotcheck_prr",
)
MANUSCRIPTS = {
    "encounter_multimodal_prr_v2.pdf": "article.pdf",
    "encounter_multimodal_prr_v2_supplement.pdf": "supplement.pdf",
}


def require(path: Path) -> Path:
    if not path.is_file():
        raise FileNotFoundError(f"required release input is missing: {path}")
    return path


def reset_generated_dir(name: str) -> Path:
    target = ARCHIVE / name
    if target.parent != ARCHIVE:
        raise RuntimeError(f"refusing unsafe generated-directory target: {target}")
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True)
    return target


def clear_release_receipts() -> None:
    """Remove only receipts created by this builder before a refresh."""

    for path in (
        ARCHIVE / "MANIFEST.sha256",
        ZIP_PATH,
        ZIP_PATH.with_suffix(".zip.sha256"),
    ):
        if path.exists():
            path.unlink()


def copy_release_inputs(*, include_manuscripts: bool) -> None:
    code_out = reset_generated_dir("code")
    data_out = reset_generated_dir("artifacts") / "data"
    figure_out = ARCHIVE / "artifacts" / "figures"
    manuscript_out = reset_generated_dir("manuscript")
    data_out.mkdir(parents=True)
    figure_out.mkdir(parents=True)

    for name in CODE_FILES:
        shutil.copy2(require(REPORT / "code" / name), code_out / name)
    for name in ANALYSIS_FILES:
        shutil.copy2(
            require(REPORT / "manuscript" / "prr_assets" / name),
            code_out / name,
        )

    source_data = REPORT / "artifacts" / "data"
    for family in ("exact_m_offlattice_production", "exact_m_prr_upgrade"):
        for source in sorted((source_data / family).rglob("*.json")):
            relative = source.relative_to(source_data)
            destination = data_out / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)

    source_figures = REPORT / "artifacts" / "figures"
    for stem in FIGURE_STEMS:
        for suffix in (".pdf", ".png"):
            source = require(source_figures / f"{stem}{suffix}")
            shutil.copy2(source, figure_out / source.name)

    if include_manuscripts:
        source_manuscript = REPORT / "manuscript" / "prr_submission"
        for source_name, archive_name in MANUSCRIPTS.items():
            shutil.copy2(
                require(source_manuscript / source_name),
                manuscript_out / archive_name,
            )


def write_manifest() -> None:
    manifest = ARCHIVE / "MANIFEST.sha256"
    rows = []
    for path in sorted(p for p in ARCHIVE.rglob("*") if p.is_file()):
        if path == manifest:
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        rows.append(f"{digest}  {path.relative_to(ARCHIVE).as_posix()}")
    manifest.write_text("\n".join(rows) + "\n", encoding="utf-8")


def write_zip() -> None:
    if ZIP_PATH.exists():
        ZIP_PATH.unlink()
    with zipfile.ZipFile(
        ZIP_PATH,
        mode="w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
    ) as bundle:
        for path in sorted(p for p in ARCHIVE.rglob("*") if p.is_file()):
            bundle.write(path, Path(ARCHIVE_NAME) / path.relative_to(ARCHIVE))
    digest = hashlib.sha256(ZIP_PATH.read_bytes()).hexdigest()
    ZIP_PATH.with_suffix(".zip.sha256").write_text(
        f"{digest}  {ZIP_PATH.name}\n", encoding="utf-8"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--stage-only",
        action="store_true",
        help=(
            "refresh code/data/figures but omit manuscripts, MANIFEST, and ZIP; "
            "use while final PDFs are still being compiled"
        ),
    )
    args = parser.parse_args()
    clear_release_receipts()
    copy_release_inputs(include_manuscripts=not args.stage_only)
    if args.stage_only:
        print(f"staging tree (not a release): {ARCHIVE}")
        return
    write_manifest()
    write_zip()
    print(f"archive tree: {ARCHIVE}")
    print(f"release zip: {ZIP_PATH}")


if __name__ == "__main__":
    main()
