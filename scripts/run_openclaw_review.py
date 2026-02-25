#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
import uuid
import glob
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = REPO_ROOT / "artifacts" / "checks" / "openclaw_review.json"
DEFAULT_HISTORY = REPO_ROOT / "artifacts" / "checks" / "openclaw_review_history.jsonl"


def utc_now_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat().replace("+00:00", "Z")


def run(cmd: list[str], *, cwd: Path = REPO_ROOT, timeout: int = 900) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
        timeout=timeout,
    )


def parse_json_maybe(text: str) -> dict[str, Any] | None:
    text = text.strip()
    if not text:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if not match:
        return None
    candidate = match.group(0)
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        return None


def ensure_agent(agent_id: str, workspace: Path, model: str) -> tuple[bool, str]:
    listed = run(["openclaw", "agents", "list", "--json"], timeout=120)
    if listed.returncode != 0:
        return False, listed.stdout
    payload = parse_json_maybe(listed.stdout) or []
    existing = next((item for item in payload if item.get("id") == agent_id), None)
    if existing and existing.get("model") == model:
        return True, "agent exists"
    if existing:
        deleted = run(["openclaw", "agents", "delete", agent_id, "--force", "--json"], timeout=120)
        if deleted.returncode != 0:
            return False, deleted.stdout
    added = run(
        [
            "openclaw",
            "agents",
            "add",
            agent_id,
            "--workspace",
            str(workspace),
            "--model",
            model,
            "--non-interactive",
            "--json",
        ],
        timeout=180,
    )
    if added.returncode != 0:
        return False, added.stdout
    return True, "agent created"


def select_models(candidates: list[str]) -> list[str]:
    listed = run(["openclaw", "models", "list", "--all", "--plain"], timeout=120)
    if listed.returncode != 0:
        return candidates
    available = {line.strip() for line in listed.stdout.splitlines() if line.strip()}
    resolved = [model for model in candidates if model in available]
    return resolved or candidates


def build_local_snapshot(repo_root: Path) -> dict[str, Any]:
    snapshot: dict[str, Any] = {}
    theory_map_path = repo_root / "site" / "public" / "data" / "v1" / "theory_map.json"
    if theory_map_path.exists():
        try:
            theory_map = json.loads(theory_map_path.read_text(encoding="utf-8"))
            checks = {
                str(item.get("check", "")): {
                    "pass": bool(item.get("pass")),
                    "details": item.get("details"),
                }
                for item in theory_map.get("consistency_checks", [])
            }
            snapshot["theory_checks"] = {
                "duplicate_math_signatures": checks.get("duplicate_math_signatures", {}).get("pass"),
                "asset_label_duplication": checks.get("asset_label_duplication", {}).get("pass"),
                "formula_depth_policy": checks.get("formula_depth_policy", {}).get("pass"),
            }
            formula_depth = checks.get("formula_depth_policy", {}).get("details")
            if isinstance(formula_depth, dict):
                snapshot["formula_depth_policy"] = {
                    "failure_report_ids": list(formula_depth.get("failure_report_ids", []))[:20],
                    "exception_count": len(list(formula_depth.get("exception_rows", [])))
                    if isinstance(formula_depth.get("exception_rows"), list)
                    else 0,
                }
        except json.JSONDecodeError:
            snapshot["theory_checks"] = {"parse_error": True}

    parity_fields = ("key_findings", "math_blocks", "math_story", "section_cards", "reproducibility_commands", "source_documents")
    strict_fields = {"math_blocks", "math_story", "section_cards"}
    mismatches: list[dict[str, Any]] = []
    index_path = repo_root / "site" / "public" / "data" / "v1" / "index.json"
    if index_path.exists():
        try:
            index_payload = json.loads(index_path.read_text(encoding="utf-8"))
            for item in index_payload.get("reports", []):
                report_id = str(item.get("report_id", "")).strip()
                if not report_id:
                    continue
                report_root = repo_root / "site" / "public" / "data" / "v1" / "reports" / report_id
                meta_en = report_root / "meta.json"
                meta_cn = report_root / "meta.cn.json"
                if not meta_en.exists() or not meta_cn.exists():
                    mismatches.append(
                        {
                            "report_id": report_id,
                            "field": "meta_presence",
                            "en_exists": meta_en.exists(),
                            "cn_exists": meta_cn.exists(),
                        }
                    )
                    continue
                en_payload = json.loads(meta_en.read_text(encoding="utf-8"))
                cn_payload = json.loads(meta_cn.read_text(encoding="utf-8"))
                for field in parity_fields:
                    left = en_payload.get(field, [])
                    right = cn_payload.get(field, [])
                    if not isinstance(left, list) or not isinstance(right, list):
                        mismatches.append({"report_id": report_id, "field": field, "reason": "non_list_payload"})
                        continue
                    if not left and right:
                        mismatches.append({"report_id": report_id, "field": field, "en": 0, "cn": len(right)})
                        continue
                    if not right and left:
                        mismatches.append({"report_id": report_id, "field": field, "en": len(left), "cn": 0})
                        continue
                    if left and right:
                        ratio = min(len(left), len(right)) / max(1, max(len(left), len(right)))
                        min_ratio = 1.0 if field in strict_fields else 0.9
                        if ratio < min_ratio:
                            mismatches.append(
                                {
                                    "report_id": report_id,
                                    "field": field,
                                    "en": len(left),
                                    "cn": len(right),
                                    "min_ratio": min_ratio,
                                }
                            )
        except json.JSONDecodeError:
            mismatches.append({"report_id": "__all__", "field": "json_parse", "reason": "index/meta parse error"})
    snapshot["locale_parity"] = {
        "mismatch_count": len(mismatches),
        "mismatches": mismatches[:12],
    }

    mixed = 0
    total = 0
    for path in glob.glob(str(repo_root / "site" / "public" / "data" / "v1" / "reports" / "*" / "series" / "*.json")):
        try:
            payload = json.loads(Path(path).read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        total += 1
        types = {str(row.get("series_type", "")).strip() for row in payload.get("series", []) if str(row.get("series_type", "")).strip()}
        if len(types) > 1:
            mixed += 1
    snapshot["semantic_payload_homogeneity"] = {"mixed_series_payloads": mixed, "total_series_payloads": total}

    render_pages = repo_root / "site" / "src" / "lib" / "render-pages.tsx"
    if render_pages.exists():
        source = render_pages.read_text(encoding="utf-8", errors="ignore")
        snapshot["theory_ui"] = {
            "contains_raw_json_rendering": "JSON.stringify(check.details" in source,
            "contains_duplication_governance_section": "Duplication Governance" in source,
            "contains_stage_matrix_section": "Stage Coverage Matrix" in source,
        }

    plot_panel = repo_root / "site" / "src" / "components" / "ReportPlotPanel.tsx"
    validate_script = repo_root / "scripts" / "validate_web_data.py"
    if plot_panel.exists():
        source = plot_panel.read_text(encoding="utf-8", errors="ignore")
        snapshot["interaction_ui"] = {
            "has_infer_series_type_function": "function inferSeriesType(" in source,
            "has_semantic_warning_banner": "Semantic warning:" in source,
        }
    if validate_script.exists():
        source = validate_script.read_text(encoding="utf-8", errors="ignore")
        snapshot["semantic_validation"] = {
            "strict_series_semantics_check": "def assert_series_semantics(" in source,
        }
    return snapshot


def build_prompt(repo_root: Path, local_snapshot: dict[str, Any]) -> str:
    return (
        "You are a strict QA reviewer for a mathematics-heavy website and publication pipeline. "
        "Review the repository at "
        f"{repo_root.as_posix()} "
        "with focus on content coherence, readability, mathematical continuity, interaction quality, verifiability, and duplication risk. "
        "Cross-check these files first: "
        "site/src/lib/render-pages.tsx, site/src/lib/render-book-pages.tsx, site/src/components/ReportPlotPanel.tsx, "
        "site/public/data/v1/index.json, site/public/data/v1/theory_map.json, "
        "site/public/data/v1/report_network.json, site/public/data/v1/content_map.json, "
        "site/public/data/v1/book/book_manifest.json, site/public/data/v1/book/toc.json, "
        "artifacts/deliverables/publication/valley_k_small_compendium_en.pdf. "
        "Also sample-check at least 5 report metadata files under site/public/data/v1/reports/*/meta.json. "
        "Ground-truth snapshot computed locally (must be respected unless you provide explicit contradictory evidence): "
        f"{json.dumps(local_snapshot, ensure_ascii=False)}. "
        "If snapshot.locale_parity.mismatch_count is 0, do not claim locale mismatch unless you provide exact conflicting file values. "
        "If snapshot.theory_ui.contains_raw_json_rendering is false, do not claim raw-JSON UI rendering without contrary file evidence. "
        "For each finding, emphasize concrete content-level defects and whether statements are verifiable from evidence paths. "
        "If your claim contradicts the snapshot, set severity='disputed' and provide exact contrary values from files. "
        "Return ONLY compact JSON with keys: "
        "score (0-100), findings (array of {severity, area, issue, evidence, fix}), "
        "quick_wins (array), crosscheck (array). "
        "No markdown."
    )


def normalize_review_against_snapshot(review: dict[str, Any], snapshot: dict[str, Any]) -> dict[str, Any]:
    findings = review.get("findings")
    if not isinstance(findings, list):
        return review

    parity_clean = int(snapshot.get("locale_parity", {}).get("mismatch_count", 0)) == 0
    no_raw_json_ui = bool(snapshot.get("theory_ui", {}).get("contains_raw_json_rendering", True)) is False
    formula_policy_enabled = bool(snapshot.get("theory_checks", {}).get("formula_depth_policy", False))
    has_duplication_section = bool(snapshot.get("theory_ui", {}).get("contains_duplication_governance_section", False))
    infer_symbol_absent = bool(snapshot.get("interaction_ui", {}).get("has_infer_series_type_function", True)) is False
    strict_semantics_validation = bool(snapshot.get("semantic_validation", {}).get("strict_series_semantics_check", False))

    normalized: list[dict[str, Any]] = []
    disputed_count = 0
    for item in findings:
        if not isinstance(item, dict):
            continue
        row = dict(item)
        issue = str(row.get("issue", "")).lower()
        evidence = str(row.get("evidence", "")).lower()
        combined = f"{issue}\n{evidence}"
        dispute_notes: list[str] = []

        if parity_clean and ("locale" in combined or "en/cn" in combined or "mismatch" in combined):
            if "math_blocks" in combined or "parity" in combined:
                dispute_notes.append("local snapshot locale_parity.mismatch_count=0")
        if no_raw_json_ui and ("raw json" in combined or "json.stringify(check.details" in combined):
            dispute_notes.append("local snapshot theory_ui.contains_raw_json_rendering=false")
        if formula_policy_enabled and ("formula-depth" in combined or "formula depth" in combined):
            dispute_notes.append("local snapshot theory_checks.formula_depth_policy=true")
        if has_duplication_section and ("shared-core" in combined or "shared core" in combined):
            if "not clearly separated" in combined or "generic check output" in combined:
                dispute_notes.append("local snapshot theory_ui.contains_duplication_governance_section=true")
        if infer_symbol_absent and strict_semantics_validation and ("fallback" in combined and "series" in combined and "heuristic" in combined):
            dispute_notes.append("local snapshot interaction_ui.has_infer_series_type_function=false + semantic_validation.strict_series_semantics_check=true")

        if dispute_notes:
            row["severity"] = "disputed"
            evidence_text = str(row.get("evidence", "")).strip()
            note_text = "; ".join(dispute_notes)
            row["evidence"] = f"{evidence_text} | Snapshot contradiction: {note_text}".strip()
            disputed_count += 1
        normalized.append(row)

    review["findings"] = normalized
    if disputed_count > 0:
        quick_wins = review.get("quick_wins")
        if not isinstance(quick_wins, list):
            quick_wins = []
        quick_wins.append(f"{disputed_count} finding(s) marked disputed by deterministic local snapshot checks.")
        review["quick_wins"] = quick_wins
    return review


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run OpenClaw external review for valley-k-small web quality.")
    parser.add_argument("--agent-id", default="vk-review-qa")
    parser.add_argument("--workspace", type=Path, default=REPO_ROOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--history", type=Path, default=DEFAULT_HISTORY)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    model_candidates = [
        "openai-codex/gpt-5.3-codex",
        "openai/gpt-5.2-pro-extended-thinking",
        "openai/gpt-5.2-pro",
        "openai-codex/gpt-5.2",
    ]
    selected_models = select_models(model_candidates)
    local_snapshot = build_local_snapshot(args.workspace)
    prompt = build_prompt(args.workspace, local_snapshot)
    attempt_errors: list[dict[str, str]] = []

    for selected_model in selected_models:
        ok, note = ensure_agent(args.agent_id, args.workspace, selected_model)
        if not ok:
            attempt_errors.append({"model": selected_model, "stage": "ensure_agent", "error": note.strip()[:4000]})
            continue

        session_id = f"oc-review-{uuid.uuid4()}"
        reviewed = run(
            [
                "openclaw",
                "agent",
                "--local",
                "--agent",
                args.agent_id,
                "--session-id",
                session_id,
                "--thinking",
                "high",
                "--timeout",
                "900",
                "--json",
                "--message",
                prompt,
            ],
            timeout=960,
        )
        if reviewed.returncode != 0:
            attempt_errors.append(
                {
                    "model": selected_model,
                    "stage": "review",
                    "error": reviewed.stdout.strip()[:8000],
                }
            )
            continue

        raw = parse_json_maybe(reviewed.stdout) or {}
        text_payload = ""
        if isinstance(raw, dict):
            payloads = raw.get("payloads")
            if isinstance(payloads, list) and payloads:
                first = payloads[0]
                if isinstance(first, dict):
                    text_payload = str(first.get("text", ""))
        parsed_review = parse_json_maybe(text_payload) or {"raw_text": text_payload.strip()}
        review_ok = isinstance(parsed_review, dict) and "score" in parsed_review and "findings" in parsed_review
        if not review_ok:
            attempt_errors.append(
                {
                    "model": selected_model,
                    "stage": "parse",
                    "error": json.dumps(parsed_review, ensure_ascii=False)[:4000],
                }
            )
            continue
        parsed_review = normalize_review_against_snapshot(parsed_review, local_snapshot)

        output = {
            "ok": True,
            "generated_at": utc_now_iso(),
            "agent_id": args.agent_id,
            "session_id": session_id,
            "model": selected_model,
            "model_candidates": selected_models,
            "agent_setup_note": note,
            "attempt_errors": attempt_errors,
            "review": parsed_review,
        }
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
        args.history.parent.mkdir(parents=True, exist_ok=True)
        with args.history.open("a", encoding="utf-8") as f:
            f.write(json.dumps(output, ensure_ascii=False) + "\n")
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return 0

    payload = {
        "ok": False,
        "generated_at": utc_now_iso(),
        "agent_id": args.agent_id,
        "model_candidates": selected_models,
        "attempt_errors": attempt_errors,
        "error": "All configured models failed for OpenClaw review.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    args.history.parent.mkdir(parents=True, exist_ok=True)
    with args.history.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
