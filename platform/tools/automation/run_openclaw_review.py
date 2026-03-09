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


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_OUT = REPO_ROOT / ".local" / "checks" / "openclaw_review.json"
DEFAULT_HISTORY = REPO_ROOT / ".local" / "checks" / "openclaw_review_history.jsonl"


def utc_now_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat().replace("+00:00", "Z")


def run(cmd: list[str], *, cwd: Path = REPO_ROOT, timeout: int = 900) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            cmd,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as error:
        timeout_stdout = error.stdout or ""
        if isinstance(timeout_stdout, bytes):
            timeout_stdout = timeout_stdout.decode("utf-8", errors="ignore")
        output = f"{timeout_stdout}\n[TIMEOUT] command exceeded timeout limit."
        return subprocess.CompletedProcess(
            args=cmd,
            returncode=124,
            stdout=output,
        )


def parse_json_maybe(text: str) -> dict[str, Any] | None:
    text = text.strip()
    if not text:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    for line in reversed(text.splitlines()):
        row = line.strip()
        if not row:
            continue
        if not (row.startswith("{") and row.endswith("}")):
            continue
        try:
            payload = json.loads(row)
            if isinstance(payload, dict):
                return payload
        except json.JSONDecodeError:
            continue

    candidates = re.findall(r"(\{(?:[^{}]|(?:\{[^{}]*\}))*\})", text, flags=re.DOTALL)
    for candidate in reversed(candidates):
        try:
            payload = json.loads(candidate)
            if isinstance(payload, dict):
                return payload
        except json.JSONDecodeError:
            continue
    return None


def extract_payload_text(raw: dict[str, Any]) -> str:
    payloads = raw.get("payloads")
    if isinstance(payloads, list):
        chunks: list[str] = []
        for row in payloads:
            if not isinstance(row, dict):
                continue
            text = str(row.get("text", "")).strip()
            if text:
                chunks.append(text)
        if chunks:
            return "\n".join(chunks)
    for key in ("text", "output", "response"):
        value = raw.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def build_lightweight_prompt(repo_root: Path, compact_snapshot: dict[str, Any]) -> str:
    return (
        f"Audit {repo_root.as_posix()} quickly. "
        "Return ONLY JSON with keys score/findings/quick_wins/crosscheck. "
        "Findings max 5; prioritize concrete high-impact issues with file evidence. "
        f"Snapshot constraints: {json.dumps(compact_snapshot, ensure_ascii=False)}. "
        "No markdown."
    )


def ensure_agent(agent_id: str, workspace: Path, model: str) -> tuple[bool, str]:
    print(f"[openclaw-review] ensure-agent: listing agents for {agent_id} ({model})", flush=True)
    listed = run(["openclaw", "agents", "list", "--json"], timeout=120)
    if listed.returncode != 0:
        return False, listed.stdout
    payload = parse_json_maybe(listed.stdout) or []
    existing = next((item for item in payload if item.get("id") == agent_id), None)
    if existing:
        print(f"[openclaw-review] ensure-agent: deleting previous agent {agent_id}", flush=True)
        deleted = run(["openclaw", "agents", "delete", agent_id, "--force", "--json"], timeout=120)
        if deleted.returncode != 0:
            return False, deleted.stdout
    print(f"[openclaw-review] ensure-agent: creating agent {agent_id}", flush=True)
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
    return True, "agent recreated"


def select_models(candidates: list[str]) -> list[str]:
    print("[openclaw-review] selecting available models", flush=True)
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
            duplicate_details = checks.get("duplicate_math_signatures", {}).get("details")
            if isinstance(duplicate_details, dict):
                shared = duplicate_details.get("shared_core_signatures", [])
                has_count_fields = False
                if isinstance(shared, list) and shared:
                    first = shared[0] if isinstance(shared[0], dict) else {}
                    has_count_fields = "report_count" in first and "occurrence_count" in first
                snapshot["duplicate_signature_metrics"] = {
                    "has_count_fields": has_count_fields,
                    "shared_core_count": len(shared) if isinstance(shared, list) else 0,
                }
            asset_details = checks.get("asset_label_duplication", {}).get("details")
            if isinstance(asset_details, dict):
                snapshot["asset_duplication_metrics"] = {
                    "has_metrics": all(
                        key in asset_details
                        for key in ("duplicate_count", "reports_with_duplicate_labels", "total_reports_scanned")
                    ),
                    "details": asset_details,
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

    publication_tex = repo_root / "artifacts" / "deliverables" / "publication" / "valley_k_small_compendium_en.tex"
    if publication_tex.exists():
        tex_source = publication_tex.read_text(encoding="utf-8", errors="ignore")
        escaped_markers = len(re.findall(r"textbackslash|\\texttt\{\\textbackslash|\\\{\}begin", tex_source))
        display_math_blocks = len(re.findall(r"\\\[", tex_source))
        ellipsis_in_math = len(re.findall(r"\\\[[^\]]*(?:\.{3,}|…)[^\]]*\\\]", tex_source, flags=re.DOTALL))
        snapshot["publication_formula_rendering"] = {
            "escaped_formula_markers": escaped_markers,
            "display_math_blocks": display_math_blocks,
            "ellipsis_in_math": ellipsis_in_math,
        }

    empty_repro_reports: list[str] = []
    clipped_summary_reports: list[str] = []
    malformed_summary_reports: list[str] = []
    if index_path.exists():
        try:
            index_payload = json.loads(index_path.read_text(encoding="utf-8"))
            for item in index_payload.get("reports", []):
                report_id = str(item.get("report_id", "")).strip()
                if not report_id:
                    continue
                meta_path = repo_root / "site" / "public" / "data" / "v1" / "reports" / report_id / "meta.json"
                if not meta_path.exists():
                    continue
                meta_payload = json.loads(meta_path.read_text(encoding="utf-8"))
                commands = [str(x).strip() for x in meta_payload.get("reproducibility_commands", []) if str(x).strip()]
                if not commands:
                    empty_repro_reports.append(report_id)
                text_blocks = [str(meta_payload.get("title", "")), str(meta_payload.get("summary", ""))]
                text_blocks.extend(str(x) for x in meta_payload.get("key_findings", []))
                text_blocks.extend(str(row.get("summary", "")) for row in meta_payload.get("section_cards", []))
                joined = " ".join(text_blocks)
                if "..." in joined or "…" in joined:
                    clipped_summary_reports.append(report_id)
                if re.search(r"\b[a-z]\s+p\d+\s+\d+\b|\bt\s*t\s*\^\s*[a-z0-9_]+\b|&=|\\begin|\\end", joined, flags=re.IGNORECASE):
                    malformed_summary_reports.append(report_id)
        except json.JSONDecodeError:
            pass
    snapshot["repro_coverage"] = {
        "empty_count": len(empty_repro_reports),
        "empty_report_ids": empty_repro_reports[:20],
    }
    snapshot["meta_text_quality"] = {
        "clipped_summary_count": len(clipped_summary_reports),
        "malformed_summary_count": len(malformed_summary_reports),
        "malformed_report_ids": malformed_summary_reports[:20],
    }

    content_map_path = repo_root / "site" / "public" / "data" / "v1" / "content_map.json"
    if content_map_path.exists():
        try:
            payload = json.loads(content_map_path.read_text(encoding="utf-8"))
            claims = list(payload.get("claims", []))
            required_stages = {"model", "method", "result", "finding"}
            stage_by_report: dict[str, set[str]] = {}
            operational_like_claim_ids: list[str] = []
            for row in claims:
                if not isinstance(row, dict):
                    continue
                rid = str(row.get("report_id", "")).strip()
                stage = str(row.get("stage", "")).strip()
                text_en = str(row.get("text_en", "")).strip()
                if rid and stage:
                    stage_by_report.setdefault(rid, set()).add(stage)
                lowered = text_en.lower()
                if re.search(r"(?:^|\s)(?:`|research/reports/|code/|scripts/|platform/web/public/|\.github/)", lowered) or (
                    "source_document" in lowered and ".json" in lowered
                ):
                    operational_like_claim_ids.append(str(row.get("claim_id", "")))

            stage_gaps = {
                rid: sorted(required_stages - stages)
                for rid, stages in stage_by_report.items()
                if (required_stages - stages)
            }
            snapshot["content_map_quality"] = {
                "claim_count": len(claims),
                "reports_with_stage_gaps": stage_gaps,
                "stage_gap_report_count": len(stage_gaps),
                "operational_like_claim_count": len(operational_like_claim_ids),
                "operational_like_claim_ids": operational_like_claim_ids[:20],
            }
        except json.JSONDecodeError:
            snapshot["content_map_quality"] = {
                "parse_error": True,
            }

    render_pages = repo_root / "site" / "src" / "lib" / "render-pages.tsx"
    if render_pages.exists():
        source = render_pages.read_text(encoding="utf-8", errors="ignore")
        snapshot["theory_ui"] = {
            "contains_raw_json_rendering": "JSON.stringify(check.details" in source,
            "contains_duplication_governance_section": "Duplication Governance" in source,
            "contains_stage_matrix_section": "Stage Coverage Matrix" in source,
        }
    render_book_pages = repo_root / "site" / "src" / "lib" / "render-book-pages.tsx"
    if render_book_pages.exists():
        source = render_book_pages.read_text(encoding="utf-8", errors="ignore")
        snapshot["book_continuous_rendering"] = {
            "has_intro_slice": "chapterIntro(chapter, lang).slice" in source,
            "has_theory_slice": "chapter.theory_chain.slice" in source,
            "has_claim_slice": "chapter.claim_ledger.slice" in source,
        }

    plot_panel = repo_root / "site" / "src" / "components" / "ReportPlotPanel.tsx"
    validate_script = repo_root / "scripts" / "validate_web_data.py"
    if plot_panel.exists():
        source = plot_panel.read_text(encoding="utf-8", errors="ignore")
        snapshot["interaction_ui"] = {
            "has_infer_series_type_function": "function inferSeriesType(" in source,
            "has_semantic_warning_banner": "Semantic warning:" in source,
            "uses_unknown_semantic_fallback": "series_type: semantic?.series_type ?? 'unknown'" in source
            and "unit: semantic?.unit ?? 'unknown'" in source,
            "unknown_semantics_non_transformable": "const transformable = semantic" in source
            and ": false;" in source,
        }
    if validate_script.exists():
        source = validate_script.read_text(encoding="utf-8", errors="ignore")
        snapshot["semantic_validation"] = {
            "strict_series_semantics_check": "def assert_series_semantics(" in source,
        }
    return snapshot


def compact_snapshot_for_prompt(snapshot: dict[str, Any]) -> dict[str, Any]:
    return {
        "theory_checks": snapshot.get("theory_checks", {}),
        "locale_parity": {
            "mismatch_count": int(snapshot.get("locale_parity", {}).get("mismatch_count", 0)),
        },
        "semantic_payload_homogeneity": snapshot.get("semantic_payload_homogeneity", {}),
        "repro_coverage": snapshot.get("repro_coverage", {}),
        "meta_text_quality": snapshot.get("meta_text_quality", {}),
        "content_map_quality": {
            "claim_count": int(snapshot.get("content_map_quality", {}).get("claim_count", 0)),
            "stage_gap_report_count": int(snapshot.get("content_map_quality", {}).get("stage_gap_report_count", 0)),
            "operational_like_claim_count": int(snapshot.get("content_map_quality", {}).get("operational_like_claim_count", 0)),
        },
        "theory_ui": snapshot.get("theory_ui", {}),
        "interaction_ui": snapshot.get("interaction_ui", {}),
    }


def build_prompt(repo_root: Path, compact_snapshot: dict[str, Any]) -> str:
    return (
        "You are a strict QA reviewer for a mathematics-heavy website and publication pipeline. "
        f"Review repository: {repo_root.as_posix()}. "
        "Focus only on content coherence, mathematical continuity, interaction quality, and verifiability. "
        "Cross-check these files: "
        "platform/web/src/lib/render-pages.tsx, platform/web/src/lib/render-book-pages.tsx, platform/web/src/components/ReportPlotPanel.tsx, "
        "platform/web/public/data/v1/index.json, platform/web/public/data/v1/theory_map.json, "
        "platform/web/public/data/v1/report_network.json, platform/web/public/data/v1/content_map.json, "
        "platform/web/public/data/v1/book/book_manifest.json, platform/web/public/data/v1/book/toc.json, "
        ".local/deliverables/publication/valley_k_small_compendium_en.pdf. "
        "Sample-check at least 5 report metadata files under platform/web/public/data/v1/reports/*/meta.json. "
        f"Deterministic local snapshot: {json.dumps(compact_snapshot, ensure_ascii=False)}. "
        "Respect snapshot unless you provide explicit conflicting file evidence. "
        "Return ONLY compact JSON with keys: "
        "score (0-100), findings (array of {severity, area, issue, evidence, fix}), "
        "quick_wins (array), crosscheck (array). "
        "Keep findings <= 8 and each evidence field <= 320 chars. "
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
    unknown_semantic_fallback = bool(snapshot.get("interaction_ui", {}).get("uses_unknown_semantic_fallback", False))
    unknown_semantic_non_transformable = bool(snapshot.get("interaction_ui", {}).get("unknown_semantics_non_transformable", False))
    repro_empty_count = int(snapshot.get("repro_coverage", {}).get("empty_count", -1))
    publication_rendering = snapshot.get("publication_formula_rendering", {})
    escaped_formula_markers = int(publication_rendering.get("escaped_formula_markers", -1))
    display_math_blocks = int(publication_rendering.get("display_math_blocks", 0))
    ellipsis_in_math = int(publication_rendering.get("ellipsis_in_math", -1))
    text_quality = snapshot.get("meta_text_quality", {})
    clipped_summary_count = int(text_quality.get("clipped_summary_count", -1))
    malformed_summary_count = int(text_quality.get("malformed_summary_count", -1))
    duplicate_metrics = snapshot.get("duplicate_signature_metrics", {})
    has_duplicate_count_fields = bool(duplicate_metrics.get("has_count_fields", False))
    asset_dup_metrics = snapshot.get("asset_duplication_metrics", {})
    has_asset_metrics = bool(asset_dup_metrics.get("has_metrics", False))
    content_map_quality = snapshot.get("content_map_quality", {})
    stage_gap_report_count = int(content_map_quality.get("stage_gap_report_count", -1))
    operational_like_claim_count = int(content_map_quality.get("operational_like_claim_count", -1))
    book_continuous = snapshot.get("book_continuous_rendering", {})
    has_intro_slice = bool(book_continuous.get("has_intro_slice", False))
    has_theory_slice = bool(book_continuous.get("has_theory_slice", False))
    has_claim_slice = bool(book_continuous.get("has_claim_slice", False))

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
        if (
            repro_empty_count == 0
            and "reproducibility_commands" in combined
            and ("[]" in combined or "empty" in combined or "sparse" in combined)
        ):
            dispute_notes.append("local snapshot repro_coverage.empty_count=0")
        if (
            escaped_formula_markers == 0
            and display_math_blocks > 0
            and ellipsis_in_math == 0
            and ("theory-chain math" in combined or "escaped text" in combined or "textbackslash" in combined)
        ):
            dispute_notes.append("local snapshot publication_formula_rendering shows math-mode formulas without escaped markers")
        if (
            clipped_summary_count == 0
            and malformed_summary_count == 0
            and ("metadata text quality" in combined or "aggressive clipping" in combined or "truncated" in combined)
        ):
            dispute_notes.append("local snapshot meta_text_quality has no clipped/malformed summaries")
        if has_duplicate_count_fields and ("count ambiguity" in combined or "occurrence" in combined or "count:" in combined):
            dispute_notes.append("local snapshot duplicate_signature_metrics.has_count_fields=true")
        if has_asset_metrics and ("asset_label_duplication" in combined and "details" in combined and "empty" in combined):
            dispute_notes.append("local snapshot asset_duplication_metrics.has_metrics=true")
        if (
            unknown_semantic_fallback
            and unknown_semantic_non_transformable
            and (
                "missing semantics as metric/value" in combined
                or "fallback semantic class from metric/value" in combined
                or "inferred metric becomes transformable" in combined
            )
        ):
            dispute_notes.append("local snapshot interaction_ui uses unknown semantic fallback and non-transformable unknown semantics")
        if (
            stage_gap_report_count == 0
            and (
                "stage continuity" in combined
                or "stage-chain" in combined
                or "missing model/method/result/finding" in combined
                or "stage counts" in combined
            )
        ):
            dispute_notes.append("local snapshot content_map_quality.stage_gap_report_count=0")
        if (
            operational_like_claim_count == 0
            and (
                "operational/file-path" in combined
                or "file-path notes" in combined
                or "mixes scientific claims with operational" in combined
            )
        ):
            dispute_notes.append("local snapshot content_map_quality.operational_like_claim_count=0")
        if (
            not has_intro_slice
            and not has_theory_slice
            and not has_claim_slice
            and (
                "continuous-reading page promises" in combined
                or "truncates chapter content" in combined
                or "slice(0,2)" in combined
                or "slice(0,6)" in combined
            )
        ):
            dispute_notes.append("local snapshot book_continuous_rendering has no chapter slicing")

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
        score = review.get("score")
        if isinstance(score, int):
            review["score_adjusted_by_snapshot"] = min(100, score + min(24, disputed_count * 4))
    elif isinstance(review.get("score"), int):
        review["score_adjusted_by_snapshot"] = int(review.get("score"))
    return review


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run OpenClaw external review for valley-k-small web quality.")
    parser.add_argument("--agent-id", default="vk-review-qa")
    parser.add_argument("--workspace", type=Path, default=REPO_ROOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--history", type=Path, default=DEFAULT_HISTORY)
    parser.add_argument(
        "--model",
        default="",
        help="Force a specific OpenClaw model id (e.g. openai/gpt-5.2-pro).",
    )
    parser.add_argument(
        "--review-timeout",
        type=int,
        default=240,
        help="Per-model review timeout in seconds (default: 240).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    model_candidates = [
        "openai-codex/gpt-5.3-codex",
        "openai-codex/gpt-5.3-codex-spark",
        "openai-codex/gpt-5.2",
    ]
    if str(args.model).strip():
        model_candidates = [str(args.model).strip()] + [m for m in model_candidates if m != str(args.model).strip()]
    selected_models = select_models(model_candidates)
    print(
        json.dumps(
            {
                "event": "openclaw_review_start",
                "workspace": str(args.workspace),
                "agent_id": args.agent_id,
                "selected_models": selected_models,
            },
            ensure_ascii=False,
        ),
        flush=True,
    )
    local_snapshot = build_local_snapshot(args.workspace)
    compact_snapshot = compact_snapshot_for_prompt(local_snapshot)
    prompt = build_prompt(args.workspace, compact_snapshot)
    fallback_prompt = build_lightweight_prompt(args.workspace, compact_snapshot)
    attempt_errors: list[dict[str, str]] = []

    for selected_model in selected_models:
        print(f"[openclaw-review] trying model: {selected_model}", flush=True)
        ok, note = ensure_agent(args.agent_id, args.workspace, selected_model)
        if not ok:
            attempt_errors.append({"model": selected_model, "stage": "ensure_agent", "error": note.strip()[:4000]})
            continue

        session_id = f"oc-review-{uuid.uuid4()}"
        print(f"[openclaw-review] launch review session: {session_id}", flush=True)
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
                str(max(60, int(args.review_timeout))),
                "--json",
                "--message",
                prompt,
            ],
            timeout=max(90, int(args.review_timeout) + 60),
        )
        print(
            json.dumps(
                {
                    "event": "openclaw_review_command_done",
                    "model": selected_model,
                    "return_code": reviewed.returncode,
                    "output_preview": (reviewed.stdout or "")[-500:],
                },
                ensure_ascii=False,
            ),
            flush=True,
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
        text_payload = extract_payload_text(raw if isinstance(raw, dict) else {})
        parsed_review = parse_json_maybe(text_payload) or {"raw_text": text_payload.strip()}
        if (not text_payload.strip()) or not (isinstance(parsed_review, dict) and "score" in parsed_review and "findings" in parsed_review):
            retry_session_id = f"{session_id}-fallback"
            print(f"[openclaw-review] retry lightweight prompt: {retry_session_id}", flush=True)
            retry = run(
                [
                    "openclaw",
                    "agent",
                    "--local",
                    "--agent",
                    args.agent_id,
                    "--session-id",
                    retry_session_id,
                    "--thinking",
                    "high",
                    "--timeout",
                    str(max(60, int(args.review_timeout))),
                    "--json",
                    "--message",
                    fallback_prompt,
                ],
                timeout=max(90, int(args.review_timeout) + 60),
            )
            if retry.returncode == 0:
                retry_raw = parse_json_maybe(retry.stdout) or {}
                retry_text = extract_payload_text(retry_raw if isinstance(retry_raw, dict) else {})
                retry_parsed = parse_json_maybe(retry_text) or {"raw_text": retry_text.strip()}
                if isinstance(retry_parsed, dict) and "score" in retry_parsed and "findings" in retry_parsed:
                    parsed_review = retry_parsed
                    text_payload = retry_text
                    session_id = retry_session_id
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
