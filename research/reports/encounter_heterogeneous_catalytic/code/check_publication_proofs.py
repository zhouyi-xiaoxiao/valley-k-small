#!/usr/bin/env python3
"""Fail closed unless full, verify, aggregate, logs, and thirteen audits are fresh."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path

import build_audit_ledger as audit_ledger_builder
import run_publication_pipeline as pipeline

REPORT = Path(__file__).resolve().parents[1]
REPO = Path(__file__).resolve().parents[4]
DATA = REPORT / "artifacts" / "data"
SUBMISSION_CHECKLIST = REPORT / "manuscript" / "SUBMISSION_METADATA_REQUIRED.md"
MANUSCRIPT_TEX = REPORT / "manuscript" / "encounter_modality_jcp.tex"
SUPPLEMENT_TEX = REPORT / "manuscript" / "encounter_modality_supplement.tex"

MAIN_CORE_CLAIM_MARKERS = (
    "Reaction-support Green reduction",
    "Finite reversible spectral gate",
    "Fixed-budget modality susceptibility",
    "Finite encounter-chain fold",
    "M2D-F matched-budget folds",
)
MAIN_SCOPE_BOUNDARY_MARKERS = (
    "finite-model calculus",
    "necessary spectral gate",
    "finite-generator mechanism certificates, not a continuum critical value",
    "Mere \\(C^2\\) convergence of the densities is not sufficient",
    "no independent Robin or Brownian solver validates the fold",
    "Establishing a continuum fold requires a new convergence calculation",
)
SUPPLEMENT_SCOPE_BOUNDARY_MARKERS = (
    "no continuum modality theorem is asserted",
    "It is not a theorem for a bounded Doi problem",
    "No common continuation relation between M2D-E and M2D-F is asserted",
    "not an interval-exhaustive root certificate",
    "cell-averaged continuum theorem or a converged trimodality phase boundary",
    "finite rational matrix algebra, not a Laplace transform",
)
FORBIDDEN_MANUSCRIPT_CLAIMS = (
    "first observation of bimodal",
    "heterogeneity is necessary for bimodality",
    "we prove a continuum fold",
    "we establish a continuum fold",
    "finite grids prove a continuum fold",
)


def _manuscript_sources() -> tuple[Path, Path]:
    """Return the two independently compiled submission sources."""

    return MANUSCRIPT_TEX, SUPPLEMENT_TEX


def _normalized_source(path: Path) -> str:
    pipeline._require_materialized(path)
    return " ".join(path.read_text(encoding="utf-8").split())


def _manuscript_claim_boundary_errors() -> list[str]:
    """Fail closed on loss of the focused main claims or either scope boundary."""

    errors: list[str] = []
    sources: dict[str, str] = {}
    for role, path in zip(("main article", "Supplemental Material"), _manuscript_sources()):
        if not path.is_file():
            errors.append(f"{role} source is missing: {path}")
            continue
        try:
            sources[role] = _normalized_source(path)
        except (OSError, RuntimeError) as exc:
            errors.append(f"{role} source is unreadable: {path}: {exc}")

    main = sources.get("main article")
    if main is not None:
        for marker in MAIN_CORE_CLAIM_MARKERS:
            if " ".join(marker.split()) not in main:
                errors.append(f"main article lacks core claim marker: {marker}")
        for marker in MAIN_SCOPE_BOUNDARY_MARKERS:
            if " ".join(marker.split()) not in main:
                errors.append(f"main article lacks finite-model scope boundary: {marker}")

    supplement = sources.get("Supplemental Material")
    if supplement is not None:
        for marker in SUPPLEMENT_SCOPE_BOUNDARY_MARKERS:
            if " ".join(marker.split()) not in supplement:
                errors.append(
                    f"Supplemental Material lacks audited scope boundary: {marker}"
                )

    combined = " ".join(sources.values()).lower()
    for claim in FORBIDDEN_MANUSCRIPT_CLAIMS:
        if " ".join(claim.split()).lower() in combined:
            errors.append(f"submission sources retain forbidden overclaim: {claim}")
    return errors


def _git(*args: str) -> str | None:
    process = subprocess.run(
        ("git", *args),
        cwd=REPO,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return process.stdout.strip() if process.returncode == 0 else None


def _git_success(*args: str) -> bool:
    return subprocess.run(
        ("git", *args),
        cwd=REPO,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    ).returncode == 0


def _release_chain_errors(
    records: dict[
        str,
        tuple[dict[str, object], dict[str, object], dict[str, object]],
    ],
) -> list[str]:
    """Validate the source-tag -> artifact-tag -> final-tag release chain."""

    errors: list[str] = []
    current_commit = _git("rev-parse", "HEAD")
    current_status = _git("status", "--porcelain")
    current_tag = _git("describe", "--exact-match", "--tags", "HEAD")
    if current_status != "":
        errors.append("final release checker must run from a clean working tree")
    if not current_commit:
        errors.append("final release checker cannot read current HEAD")
    if not current_tag:
        errors.append("final release checker must run at an exact final tag")
    elif current_commit:
        resolved = _git(
            "rev-parse", "--verify", f"refs/tags/{current_tag}^{{commit}}"
        )
        if resolved != current_commit:
            errors.append(
                f"final tag {current_tag!r} does not resolve to current HEAD: "
                f"resolved={resolved!r} head={current_commit!r}"
            )

    for profile in ("full", "verify"):
        if profile not in records:
            errors.append(f"{profile} release record is missing")
            continue
        start, release, end_git = records[profile]
        if not release.get("requested") or not release.get("start_gate_passed"):
            errors.append(f"{profile} canonical proof was not a release-mode run")
        if start.get("clean") is not True or not start.get("exact_tag"):
            errors.append(f"{profile} run did not start clean at an exact tag")
        if not start.get("commit"):
            errors.append(f"{profile} release start commit is missing")
        if end_git.get("commit") != start.get("commit"):
            errors.append(
                f"{profile} HEAD changed during the release run: "
                f"start={start.get('commit')!r} end={end_git.get('commit')!r}"
            )
        tag = str(start.get("exact_tag", ""))
        commit = str(start.get("commit", ""))
        if tag and commit:
            resolved = _git(
                "rev-parse", "--verify", f"refs/tags/{tag}^{{commit}}"
            )
            if resolved != commit:
                errors.append(
                    f"{profile} recorded tag {tag!r} no longer resolves to its "
                    f"recorded commit: resolved={resolved!r} recorded={commit!r}"
                )

    if "full" in records and "verify" in records:
        full_commit = str(records["full"][0].get("commit", ""))
        verify_commit = str(records["verify"][0].get("commit", ""))
        if full_commit and verify_commit and not _git_success(
            "merge-base", "--is-ancestor", full_commit, verify_commit
        ):
            errors.append(
                "full source-tag commit is not an ancestor of the verify artifact-tag commit"
            )
        if verify_commit and current_commit and not _git_success(
            "merge-base", "--is-ancestor", verify_commit, current_commit
        ):
            errors.append(
                "verify artifact-tag commit is not an ancestor of the final tagged commit"
            )
    return errors


def _submission_metadata_errors() -> list[str]:
    """Require author-owned submission facts without blocking development builds."""

    errors: list[str] = []
    if not SUBMISSION_CHECKLIST.is_file():
        return [f"submission metadata checklist is missing: {SUBMISSION_CHECKLIST}"]
    pipeline._require_materialized(SUBMISSION_CHECKLIST)
    source = SUBMISSION_CHECKLIST.read_text(encoding="utf-8")
    checkbox_pattern = re.compile(
        r"(?ms)^\s*-\s*\[([^\]]*)\]\s+(.*?)(?=^\s*-\s*\[[^\]]*\]|\Z)"
    )
    checkbox_blocks = checkbox_pattern.findall(source)
    if not checkbox_blocks:
        errors.append("submission metadata checklist contains no checkboxes")
    invalid_marks = [mark for mark, _ in checkbox_blocks if mark.strip().lower() not in {"", "x"}]
    if invalid_marks:
        errors.append(
            f"submission metadata checklist has invalid checkbox markers: {invalid_marks}"
        )
    unchecked = sum(mark.strip().lower() != "x" for mark, _ in checkbox_blocks)
    if unchecked:
        errors.append(
            f"submission metadata checklist has {unchecked} unchecked item(s)"
        )
    checked_items = [
        text for mark, text in checkbox_blocks if mark.strip().lower() == "x"
    ]
    required_categories = {
        "authors and affiliations": r"author[\s\S]{0,160}affiliation",
        "ORCID": r"\bORCID\b",
        "funding": r"\bfunding\b|\bgrant\b",
        "conflict of interest": r"\bconflict[- ]of[- ]interest\b",
        "CRediT contributions": r"\bCRediT\b",
        "archive DOI": r"\bDOI\b",
        "code/data license": r"\blicen[cs]e\b",
        "data/code availability": r"data[- ]availability|code[- ]availability",
        "release chain": r"\brelease chain\b",
    }
    for category, pattern in required_categories.items():
        if not any(
            re.search(pattern, item, flags=re.IGNORECASE) is not None
            for item in checked_items
        ):
            errors.append(
                f"submission metadata checklist lacks a checked {category} item"
            )

    files_to_scan = [SUBMISSION_CHECKLIST, *_manuscript_sources()]
    patterns = {
        "TODO": re.compile(r"\bTODO(?:\([^)]*\))?\b", re.IGNORECASE),
        "TBD": re.compile(r"\bTBD\b", re.IGNORECASE),
        "PLACEHOLDER": re.compile(r"\bPLACEHOLDER\b", re.IGNORECASE),
        "will be supplied": re.compile(r"\bwill be supplied\b", re.IGNORECASE),
    }
    for path in files_to_scan:
        if not path.is_file():
            errors.append(f"submission source is missing: {path}")
            continue
        pipeline._require_materialized(path)
        text = path.read_text(encoding="utf-8")
        for label, pattern in patterns.items():
            if pattern.search(text):
                errors.append(f"submission source retains unresolved {label}: {path}")
    return errors


def _live_inventory_errors(
    label: str,
    stored: object,
    builder,
) -> list[str]:
    """Compare an aggregate inventory with a freshly rebuilt live inventory."""

    if not isinstance(stored, list) or not all(
        isinstance(row, dict) for row in stored
    ):
        return [f"aggregate {label} inventory is malformed"]
    try:
        live = builder()
    except Exception as exc:
        return [f"live {label} inventory could not be built: {exc}"]
    return pipeline._inventory_freshness_errors(
        f"aggregate {label}", stored, live
    )


def _saved_formal_integrity_errors() -> list[str]:
    """Require the saved formal-integrity JSON to equal a live reconstruction."""

    path = DATA / "lean_formal_integrity.json"
    if not path.is_file():
        return [f"saved Lean formal-integrity record is missing: {path}"]
    try:
        stored = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"saved Lean formal-integrity record is unreadable: {exc}"]
    try:
        live = pipeline._formal_integrity_payload()
    except Exception as exc:
        return [f"live Lean formal-integrity payload could not be rebuilt: {exc}"]
    if stored == live:
        return []

    errors = ["saved Lean formal-integrity record differs from the live payload"]
    stored_reports = {
        str(row.get("driver")): row
        for row in stored.get("axiom_reports", [])
        if isinstance(row, dict)
    } if isinstance(stored, dict) else {}
    live_reports = {
        str(row.get("driver")): row
        for row in live.get("axiom_reports", [])
        if isinstance(row, dict)
    }
    for driver in sorted(set(stored_reports) | set(live_reports)):
        if stored_reports.get(driver) != live_reports.get(driver):
            errors.append(f"formal-integrity report row changed for {driver}")
    return errors


def _formal_report_log_binding_errors() -> list[str]:
    """Bind curated/current reports to the raw logs of the canonical verify run."""

    manifest_path = DATA / "publication_pipeline.verify.manifest.json"
    if not manifest_path.is_file():
        return [f"canonical verify manifest is missing: {manifest_path}"]
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"canonical verify manifest is unreadable: {exc}"]
    stages = manifest.get("stages") if isinstance(manifest, dict) else None
    if not isinstance(stages, list):
        return ["canonical verify manifest has no stage list"]
    stage_rows = {
        str(row.get("name")): row
        for row in stages
        if isinstance(row, dict) and row.get("name")
    }
    errors: list[str] = []
    for stage_name, driver_name in pipeline.FORMAL_STAGE_DRIVERS.items():
        stage = stage_rows.get(stage_name)
        if stage is None:
            errors.append(f"canonical verify manifest lacks {stage_name}")
            continue
        log_value = stage.get("log")
        if not isinstance(log_value, str) or not log_value:
            errors.append(f"canonical verify stage {stage_name} has no log path")
            continue
        log_path = Path(log_value)
        if not log_path.is_absolute():
            log_path = REPO / log_path
        report_name = pipeline.FORMAL_DRIVER_REPORTS[driver_name]
        report_path = pipeline.FORMAL / report_name
        if not log_path.is_file():
            errors.append(f"canonical verify axiom log is missing: {log_path}")
            continue
        if not report_path.is_file():
            errors.append(f"current axiom report is missing: {report_path}")
            continue
        try:
            log_rows = pipeline._parse_axiom_output(
                log_path.read_text(encoding="utf-8")
            )
            report_rows = pipeline._parse_axiom_output(
                report_path.read_text(encoding="utf-8")
            )
        except (OSError, RuntimeError) as exc:
            errors.append(f"cannot parse {stage_name} report/log pair: {exc}")
            continue
        if report_rows != log_rows:
            missing = sorted(set(log_rows) - set(report_rows))
            extra = sorted(set(report_rows) - set(log_rows))
            changed = sorted(
                theorem
                for theorem in set(report_rows) & set(log_rows)
                if report_rows[theorem] != log_rows[theorem]
            )
            errors.append(
                f"current report is not canonically identical to raw {stage_name} log: "
                f"missing={missing} extra={extra} changed_axioms={changed}"
            )
    return errors


def _audit_ledger_errors(stored: object) -> list[str]:
    """Rebuild the audit ledger so reviewer/resolution byte changes cannot pass."""

    if not isinstance(stored, dict):
        return ["thirteen-round audit ledger is not a JSON object"]
    errors: list[str] = []
    if stored.get("schema_version") != 2:
        errors.append("thirteen-round audit ledger schema is not version 2")
    try:
        live = audit_ledger_builder.build_ledger()
    except Exception as exc:
        errors.append(f"live thirteen-round audit ledger could not be rebuilt: {exc}")
        return errors
    for key in ("policy", "round_count", "all_rounds_pass", "rounds"):
        if stored.get(key) != live.get(key):
            errors.append(
                f"thirteen-round audit ledger differs from live audit Markdown: {key}"
            )
    rounds = live.get("rounds", [])
    if (
        live.get("round_count") != 13
        or len(rounds) != 13
        or [row.get("round") for row in rounds] != list(range(1, 14))
        or [row.get("status") for row in rounds] != ["PASS"] * 13
        or live.get("all_rounds_pass") is not True
    ):
        errors.append("thirteen-round live audit ledger is incomplete or non-passing")
    return errors


def proof_errors(*, require_clean_tag: bool = False) -> list[str]:
    errors: list[str] = []
    errors.extend(_manuscript_claim_boundary_errors())
    for profile in ("full", "verify"):
        errors.extend(pipeline._canonical_profile_errors(profile))
    errors.extend(_saved_formal_integrity_errors())
    errors.extend(_formal_report_log_binding_errors())

    aggregate_path = DATA / "publication_pipeline.manifest.json"
    if not aggregate_path.is_file():
        errors.append(f"aggregate manifest is missing: {aggregate_path}")
        return errors
    try:
        aggregate = json.loads(aggregate_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"aggregate manifest is unreadable: {exc}")
        return errors
    if aggregate.get("schema_version") != 3:
        errors.append("aggregate manifest schema is not the current version 3")

    profile_rows = aggregate.get("profile_runs", [])
    latest_rows = aggregate.get("latest_attempts", [])
    attempt_rows = aggregate.get("attempt_runs", [])
    if not isinstance(profile_rows, list) or not all(
        isinstance(row, dict) for row in profile_rows
    ):
        errors.append("aggregate profile rows are malformed")
        profile_rows = []
    if not isinstance(latest_rows, list) or not all(
        isinstance(row, dict) for row in latest_rows
    ):
        errors.append("aggregate latest-attempt rows are malformed")
        latest_rows = []
    if not isinstance(attempt_rows, list) or not all(
        isinstance(row, dict) for row in attempt_rows
    ):
        errors.append("aggregate immutable-attempt rows are malformed")
        attempt_rows = []
    if [row.get("profile") for row in profile_rows] != ["full", "verify"]:
        errors.append("aggregate does not contain exactly full and verify profiles")
    if [row.get("profile") for row in latest_rows] != ["full", "verify"]:
        errors.append("aggregate does not contain exactly two latest attempts")
    for row in [*profile_rows, *latest_rows]:
        row_path = str(row.get("path", ""))
        if not row_path:
            errors.append("aggregate proof row has no path")
            continue
        path = REPO / row_path
        if not path.is_file():
            errors.append(f"aggregate proof row is missing: {path}")
            continue
        if path.stat().st_size != row.get("bytes"):
            errors.append(f"aggregate proof byte count changed: {path}")
        if pipeline._sha256(path) != row.get("sha256"):
            errors.append(f"aggregate proof hash changed: {path}")
    if any(not row.get("all_stages_passed", False) for row in profile_rows):
        errors.append("one or more canonical profile rows are not passing")
    if any(not row.get("complete", False) for row in latest_rows):
        errors.append("one or more latest profile attempts are not complete")
    errors.extend(
        _live_inventory_errors(
            "attempt manifest", attempt_rows, pipeline._attempt_manifest_rows
        )
    )

    errors.extend(
        _live_inventory_errors(
            "source",
            aggregate.get("source_files"),
            lambda: pipeline._source_inventory(include_audits=True),
        )
    )
    errors.extend(
        _live_inventory_errors(
            "formal evidence", aggregate.get("formal_evidence"), pipeline._formal_evidence
        )
    )
    errors.extend(
        _live_inventory_errors(
            "output",
            aggregate.get("outputs"),
            lambda: pipeline._tracked_outputs(include_logs=True, include_audits=True),
        )
    )

    ledger_path = REPORT / "audits" / "audit_ledger.json"
    if not ledger_path.is_file():
        errors.append(f"thirteen-round audit ledger is missing: {ledger_path}")
    else:
        try:
            ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"thirteen-round audit ledger is unreadable: {exc}")
        else:
            errors.extend(_audit_ledger_errors(ledger))

    if require_clean_tag:
        release_records: dict[
            str,
            tuple[dict[str, object], dict[str, object], dict[str, object]],
        ] = {}
        for profile in ("full", "verify"):
            path = DATA / f"publication_pipeline.{profile}.manifest.json"
            if not path.is_file():
                continue
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                errors.append(f"{profile} release record is unreadable: {exc}")
                continue
            start = payload.get("start_git", {})
            release = payload.get("release", {})
            end_git = payload.get("git", {})
            if (
                isinstance(start, dict)
                and isinstance(release, dict)
                and isinstance(end_git, dict)
            ):
                release_records[profile] = (start, release, end_git)
        errors.extend(_release_chain_errors(release_records))
        errors.extend(_submission_metadata_errors())
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--require-clean-tag",
        action="store_true",
        help=(
            "also require a clean final tag and a valid source-tag -> "
            "artifact-tag -> final-tag release chain"
        ),
    )
    args = parser.parse_args()
    errors = proof_errors(require_clean_tag=args.require_clean_tag)
    if errors:
        raise RuntimeError("\n".join(f"- {message}" for message in errors))
    print("publication proofs: PASS (full, verify, aggregate, logs, thirteen audits)")


if __name__ == "__main__":
    main()
