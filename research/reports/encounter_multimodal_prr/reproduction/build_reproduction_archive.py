#!/usr/bin/env python3
"""Refresh the clean reproduction tree, checksum manifest, and release ZIP.

Run only after the article, Supplemental Material, robustness JSON files, the
covariance-aware reclassification records, the Lean 4 package, and the W1--W5
figures have reached their final state.  The script copies an explicit
allow-list and therefore excludes logs, locks, caches, temporary LaTeX files,
Lean build products (``.lake/``), and raw development material.

Release-mode self-checks (skipped with ``--stage-only``):

* the report tree outside ``reproduction/`` must be committed;
* the copied Lean sources must reproduce the SHA-256 anchors quoted in the
  Supplemental Material;
* the archived Supplemental Material must contain the Lean section, and the
  archived article must carry the final data-availability statement;
* every archived figure PDF must be byte-identical to the submitted copy;
* ``environment/reference_platform.json`` and ``CITATION.cff`` receive the
  source commit (``git rev-parse HEAD``) and the build date, so those values
  are never typed by hand.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import re
import shutil
import subprocess
import zipfile
from pathlib import Path


REPRODUCTION = Path(__file__).resolve().parent
REPORT = REPRODUCTION.parent
ARCHIVE_NAME = "encounter_multimodal_prr_reproduction_v1"
ARCHIVE = REPRODUCTION / ARCHIVE_NAME
ZIP_PATH = REPRODUCTION / f"{ARCHIVE_NAME}.zip"
PUBLIC_REPOSITORY = "https://github.com/zhouyi-xiaoxiao/prescribed-reaction-time-modes"

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
    # covariance-aware classifier (formal definition used in the article)
    "reclassify_covariance_aware.py",
    "w3_jitter_covariance_recheck.py",
    "remake_b0_figure_covariance.py",
    "remake_jitter_figure_covariance.py",
)
ANALYSIS_FILES = (
    "b0_dyson_numerics.py",
    "b0_dyson_chaincheck.py",
)
# Non-JSON data records that the JSON glob below would miss.
DATA_EXTRA_FILES = (
    "exact_m_prr_upgrade/covariance_aware_reclassification_summary.txt",
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
MANUSCRIPT_MASTERS = (
    "encounter_multimodal_prr_v2.tex",
    "encounter_multimodal_prr_v2_supplement.tex",
)
MANUSCRIPT_SOURCES = MANUSCRIPT_MASTERS + (
    "references.bib",
    "prr_assets/fig1_mechanism_schematic.tex",
    "prr_assets/design_recipe_box.tex",
    "prr_assets/b0_quantitative_bound.tex",
    "prr_assets/physical_units_mapping.tex",
)
# Theorem fragments: shipped only while a master file still \input's them
# (they are inlined into the masters at freeze time; a stale copy must not ship).
MANUSCRIPT_FRAGMENTS = (
    "exact_m_theorem_spine.tex",
    "exact_m_theorem_full_proof.tex",
)

# Lean 4 package of the Supplemental Material (explicit allow-list; never
# .lake/, never SOURCE_HASHES_pre_recheck.txt).
LEAN_ROOT = REPORT / "code" / "formal_lean_prr"
LEAN_ARCHIVE_SUBDIR = Path("lean") / "formal_lean_prr"
LEAN_FILES = (
    "FormalPRR.lean",
    "lakefile.toml",
    "lean-toolchain",
    "lake-manifest.json",
    "consolidated_axioms.txt",
    "axioms_report_alpha.txt",
    "axioms_report_beta.txt",
    "codex_lean_audit.txt",
    "codex_lean_recheck.txt",
    "FORMALIZATION_TARGETS.md",
)
# Receipts produced at freeze time (audit-resolution note, build receipt on
# the released hashes, package README).  Required for a release.
LEAN_RECEIPT_FILES = (
    "codex_lean_recheck_resolution.txt",
    "BUILD_RECEIPT.txt",
    "README.md",
)
LEAN_SOURCE_GLOB = "FormalPRR/*.lean"
# First 16 hex digits of sha256(FormalPRR/<Module>.lean) quoted in the SM.
SM_HASH_ANCHORS = {
    "ExpPolyZeros": "7d99dc72cfe1cfd8",
    "ZeroBound": "f29cd9d8b637363b",
    "MixtureIdentities": "74a8fc956adfabe2",
    "GaussianMixture": "7e7e60bccd99bc74",
    "CrossoverBounds": "8e1e0816afea792a",
    "BudgetThreshold": "8166ecfc0e2c9390",
    "BZeroThreshold": "8f7dce937bf97771",
    "B0ChainKernel": "5ffaed91d4863c9a",
    "WindowSignature": "5bd7020e5b91a5da",
}


def require(path: Path) -> Path:
    if not path.is_file():
        raise FileNotFoundError(f"required release input is missing: {path}")
    return path


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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


def fragments_still_input() -> tuple[str, ...]:
    """Return the theorem fragments that a master tex file still \\input's."""

    source_manuscript = REPORT / "manuscript" / "prr_submission"
    text = "\n".join(
        require(source_manuscript / name).read_text(encoding="utf-8")
        for name in MANUSCRIPT_MASTERS
    )
    live = []
    for fragment in MANUSCRIPT_FRAGMENTS:
        stem = fragment[: -len(".tex")]
        pattern = r"^[^%\n]*\\input\{" + re.escape(stem) + r"(?:\.tex)?\}"
        if re.search(pattern, text, flags=re.MULTILINE):
            live.append(fragment)
    return tuple(live)


def copy_lean_package(*, require_receipts: bool) -> None:
    lean_out = reset_generated_dir("lean") / LEAN_ARCHIVE_SUBDIR.name
    (lean_out / "FormalPRR").mkdir(parents=True)

    sources = sorted(LEAN_ROOT.glob(LEAN_SOURCE_GLOB))
    if not sources:
        raise FileNotFoundError(f"no Lean sources found under {LEAN_ROOT}")
    for source in sources:
        shutil.copy2(source, lean_out / "FormalPRR" / source.name)
    for name in LEAN_FILES:
        shutil.copy2(require(LEAN_ROOT / name), lean_out / name)
    for name in LEAN_RECEIPT_FILES:
        source = LEAN_ROOT / name
        if source.is_file():
            shutil.copy2(source, lean_out / name)
        elif require_receipts:
            raise FileNotFoundError(
                f"Lean release receipt is missing: {source} "
                "(build the package on the released hashes first, or pass "
                "--allow-missing-lean-receipts for a non-release staging tree)"
            )
        else:
            print(f"WARNING: Lean receipt not yet available, skipped: {source}")

    # Anchor check against the Supplemental Material (always).
    for module, expected in SM_HASH_ANCHORS.items():
        actual = sha256_of(lean_out / "FormalPRR" / f"{module}.lean")[:16]
        if actual != expected:
            raise RuntimeError(
                f"Lean anchor mismatch for {module}.lean: SM quotes {expected}, "
                f"archived source hashes to {actual}"
            )


def copy_release_inputs(*, include_manuscripts: bool, require_lean_receipts: bool) -> None:
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
    for rel in DATA_EXTRA_FILES:
        destination = data_out / rel
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(require(source_data / rel), destination)

    source_figures = REPORT / "artifacts" / "figures"
    for stem in FIGURE_STEMS:
        for suffix in (".pdf", ".png"):
            source = require(source_figures / f"{stem}{suffix}")
            shutil.copy2(source, figure_out / source.name)

    copy_lean_package(require_receipts=require_lean_receipts)

    if include_manuscripts:
        source_manuscript = REPORT / "manuscript" / "prr_submission"
        for source_name, archive_name in MANUSCRIPTS.items():
            shutil.copy2(
                require(source_manuscript / source_name),
                manuscript_out / archive_name,
            )
        for rel in MANUSCRIPT_SOURCES + fragments_still_input():
            dst = manuscript_out / "source" / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(require(source_manuscript / rel), dst)


def _pdf_text(pdf: Path) -> str:
    return subprocess.run(
        ["pdftotext", str(pdf), "-"], capture_output=True, text=True, check=True
    ).stdout


def check_release_contents() -> None:
    """Content guards: the archived PDFs and figures must be the submitted ones."""

    supp_text = _pdf_text(ARCHIVE / "manuscript" / "supplement.pdf").lower()
    if "machine-checked kernels" not in supp_text:
        raise RuntimeError(
            "archived supplement.pdf predates the Lean section; recompile first"
        )
    art_text = _pdf_text(ARCHIVE / "manuscript" / "article.pdf")
    art_compact = re.sub(r"\s+", "", art_text).lower()
    if (
        "prescribed-reaction-time-modes" not in art_compact
        or "insertedhere" in art_compact
    ):
        raise RuntimeError(
            "archived article.pdf does not carry the final data-availability statement"
        )
    sub_figs = REPORT / "manuscript" / "prr_submission" / "figures"
    for stem in FIGURE_STEMS:
        archived = sha256_of(ARCHIVE / "artifacts" / "figures" / f"{stem}.pdf")
        submitted = sha256_of(require(sub_figs / f"{stem}.pdf"))
        if archived != submitted:
            raise RuntimeError(f"figure {stem}.pdf differs from the submitted copy")


def git_head() -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=REPORT, text=True
    ).strip()


def git_dirty_outside_reproduction() -> str:
    return subprocess.run(
        ["git", "status", "--porcelain", "--", str(REPORT), f":!{REPRODUCTION}"],
        capture_output=True,
        text=True,
        check=True,
        cwd=REPORT,
    ).stdout.strip()


def write_release_metadata() -> tuple[str, str]:
    """Stamp the source commit and build date into the tracked metadata files."""

    commit = git_head()
    release_date = _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%d")

    platform_json = ARCHIVE / "environment" / "reference_platform.json"
    meta = json.loads(platform_json.read_text(encoding="utf-8"))
    meta.pop("base_repository_commit", None)
    meta["release_commit"] = commit
    meta["release_date"] = release_date
    meta["release_repository"] = PUBLIC_REPOSITORY
    platform_json.write_text(
        json.dumps(meta, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    cff = ARCHIVE / "CITATION.cff"
    lines = cff.read_text(encoding="utf-8").splitlines()
    updated: list[str] = []
    seen_commit = False
    for line in lines:
        if line.startswith("date-released:"):
            line = f"date-released: {release_date}"
        elif line.startswith("commit:"):
            line = f"commit: {commit}"
            seen_commit = True
        updated.append(line)
    if not seen_commit:
        insert_at = next(
            (i + 1 for i, line in enumerate(updated) if line.startswith("date-released:")),
            len(updated),
        )
        updated.insert(insert_at, f"commit: {commit}")
    cff.write_text("\n".join(updated).rstrip("\n") + "\n", encoding="utf-8")
    return commit, release_date


def write_manifest() -> int:
    manifest = ARCHIVE / "MANIFEST.sha256"
    rows = []
    for path in sorted(p for p in ARCHIVE.rglob("*") if p.is_file()):
        if path == manifest:
            continue
        rows.append(f"{sha256_of(path)}  {path.relative_to(ARCHIVE).as_posix()}")
    manifest.write_text("\n".join(rows) + "\n", encoding="utf-8")
    return len(rows)


def write_zip() -> str:
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
    digest = sha256_of(ZIP_PATH)
    ZIP_PATH.with_suffix(".zip.sha256").write_text(
        f"{digest}  {ZIP_PATH.name}\n", encoding="utf-8"
    )
    return digest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--stage-only",
        action="store_true",
        help=(
            "refresh code/data/figures/lean but omit manuscripts, MANIFEST, ZIP, "
            "the content guards and the metadata stamp; use while final PDFs "
            "are still being compiled"
        ),
    )
    parser.add_argument(
        "--allow-missing-lean-receipts",
        action="store_true",
        help=(
            "do not fail when BUILD_RECEIPT.txt / README.md / "
            "codex_lean_recheck_resolution.txt are absent from the Lean package "
            "(staging only; a release must ship them)"
        ),
    )
    args = parser.parse_args()

    if not args.stage_only:
        dirty = git_dirty_outside_reproduction()
        if dirty:
            raise RuntimeError(
                "commit the report tree before building the release:\n" + dirty
            )

    clear_release_receipts()
    copy_release_inputs(
        include_manuscripts=not args.stage_only,
        require_lean_receipts=not (args.stage_only or args.allow_missing_lean_receipts),
    )
    if args.stage_only:
        print(f"staging tree (not a release): {ARCHIVE}")
        return

    check_release_contents()
    commit, release_date = write_release_metadata()
    n_files = write_manifest()
    zip_digest = write_zip()
    total_bytes = sum(
        p.stat().st_size for p in ARCHIVE.rglob("*") if p.is_file()
    )
    print(f"archive tree: {ARCHIVE}")
    print(f"release zip: {ZIP_PATH}")
    print(
        f"summary: {n_files} files in MANIFEST.sha256, {total_bytes} bytes, "
        f"zip sha256 {zip_digest}, source commit {commit}, build date {release_date}"
    )
    print(
        "next: commit the refreshed tree (it now records the source commit), "
        "then tag v1.0.0 on that commit and push it to " + PUBLIC_REPOSITORY
    )


if __name__ == "__main__":
    main()
