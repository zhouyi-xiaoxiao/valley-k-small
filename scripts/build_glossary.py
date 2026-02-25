#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from book_blueprint import report_to_chapters


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_ROOT = REPO_ROOT / "site" / "public" / "data" / "v1"


MANUAL_LOCKED_TERMS: list[dict[str, Any]] = [
    {
        "term_id": "fpt",
        "category": "core-metric",
        "term_en": "First-Passage Time (FPT)",
        "term_cn": "首达时间（FPT）",
        "definition_en": "Random time needed for the trajectory to hit an absorbing target for the first time.",
        "definition_cn": "轨迹首次到达吸收目标所需的随机时间。",
        "aliases_en": ["first-passage distribution", "first-hit time"],
        "aliases_cn": ["首中时间", "首达分布"],
        "formula": "f(t)",
    },
    {
        "term_id": "survival",
        "category": "core-metric",
        "term_en": "Survival Function",
        "term_cn": "生存函数",
        "definition_en": "Probability that first passage has not happened by step t.",
        "definition_cn": "到步长 t 为止尚未首达的概率。",
        "aliases_en": ["tail probability", "S(t)"],
        "aliases_cn": ["尾概率", "S(t)"],
        "formula": "S(t)=P(T>t)",
    },
    {
        "term_id": "hazard",
        "category": "core-metric",
        "term_en": "Hazard Rate",
        "term_cn": "风险率（hazard）",
        "definition_en": "Conditional probability of first passage at step t given survival up to t.",
        "definition_cn": "在已存活到 t 的条件下，于 t 步发生首达的条件概率。",
        "aliases_en": ["discrete hazard", "failure rate"],
        "aliases_cn": ["条件首达率", "离散 hazard"],
        "formula": "h(t)=f(t)/S(t-1)",
    },
    {
        "term_id": "aw-inversion",
        "category": "method",
        "term_en": "AW Inversion",
        "term_cn": "AW 反演",
        "definition_en": "Discrete Cauchy/FFT-based inversion from generating functions to time-domain FPT quantities.",
        "definition_cn": "从生成函数到时域首达量的离散 Cauchy/FFT 反演过程。",
        "aliases_en": ["Abate-Whitt inversion", "FFT inversion"],
        "aliases_cn": ["Abate-Whitt 反演", "FFT 反演"],
        "formula": "f_t \approx FFT(F(z_k))",
    },
    {
        "term_id": "bimodality-criterion",
        "category": "diagnostic",
        "term_en": "Bimodality Criterion",
        "term_cn": "双峰判据",
        "definition_en": "Operational criterion to separate true two-peak structure from noisy shoulders.",
        "definition_cn": "区分真实双峰与噪声肩部的可操作判据。",
        "aliases_en": ["double-peak criterion"],
        "aliases_cn": ["双峰诊断"],
        "formula": "peak-valley-peak consistency",
    },
    {
        "term_id": "selfloop-mode",
        "category": "shortcut-variant",
        "term_en": "Selfloop Shortcut Mode",
        "term_cn": "selfloop 机制",
        "definition_en": "Shortcut probability mass is taken from self-loop probability without renormalizing other moves.",
        "definition_cn": "shortcut 概率质量从停留概率中分配，不重标其余移动概率。",
        "aliases_en": ["selfloop allocation"],
        "aliases_cn": ["停留抽取机制"],
        "formula": "p_stay -> p_stay-β",
    },
    {
        "term_id": "renormalize-mode",
        "category": "shortcut-variant",
        "term_en": "Renormalize Shortcut Mode",
        "term_cn": "renormalize 机制",
        "definition_en": "Base transition weights are rescaled after shortcut injection to preserve normalization constraints.",
        "definition_cn": "注入 shortcut 后，对基准转移权重重标以保持归一化约束。",
        "aliases_en": ["mass renormalization"],
        "aliases_cn": ["重标机制"],
        "formula": "p_i' = c · p_i",
    },
    {
        "term_id": "equal4-mode",
        "category": "shortcut-variant",
        "term_en": "Equal4 Baseline",
        "term_cn": "equal4 基线",
        "definition_en": "Four-way equalized baseline used to compare shortcut effects under symmetric local movement.",
        "definition_cn": "用于比较 shortcut 影响的四向等概率基线。",
        "aliases_en": ["equalized K=4 baseline"],
        "aliases_cn": ["四向等概率基线"],
        "formula": "p(±1)=p(±2)",
    },
    {
        "term_id": "beta-scan",
        "category": "parameter",
        "term_en": "Beta Scan",
        "term_cn": "beta 扫描",
        "definition_en": "Parameter sweep over shortcut strength β to identify phase shifts and regime boundaries.",
        "definition_cn": "对 shortcut 强度 β 的参数扫描，用于识别相位转折与分区边界。",
        "aliases_en": ["shortcut strength sweep"],
        "aliases_cn": ["shortcut 强度扫描"],
        "formula": "β ∈ [0,1]",
    },
    {
        "term_id": "claim-ledger",
        "category": "workflow",
        "term_en": "Claim Ledger",
        "term_cn": "Claim 台账",
        "definition_en": "Structured mapping from statement to evidence paths and cross-report links.",
        "definition_cn": "将陈述映射到证据路径与跨报告链接的结构化台账。",
        "aliases_en": ["claim-evidence map"],
        "aliases_cn": ["claim-证据映射"],
        "formula": "claim -> evidence -> linked reports",
    },
]


def utc_now_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def uniq(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for raw in items:
        text = str(raw).strip()
        if not text or text in seen:
            continue
        seen.add(text)
        out.append(text)
    return out


def chapter_ids_for_reports(report_ids: list[str], mapping: dict[str, list[str]]) -> list[str]:
    chapter_ids: list[str] = []
    for rid in report_ids:
        chapter_ids.extend(mapping.get(rid, []))
    return uniq(chapter_ids)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build bilingual glossary lock table for book pages.")
    parser.add_argument("--data-root", type=Path, default=DEFAULT_DATA_ROOT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    data_root: Path = args.data_root
    theory_map_path = data_root / "theory_map.json"
    if not theory_map_path.exists():
        raise SystemExit(f"Missing theory map: {theory_map_path}")

    theory_map = read_json(theory_map_path)
    report_map = report_to_chapters()

    terms: list[dict[str, Any]] = []

    for base in MANUAL_LOCKED_TERMS:
        related_report_ids = sorted(report_map.keys())
        term = {
            "term_id": base["term_id"],
            "category": base["category"],
            "term_en": base["term_en"],
            "term_cn": base["term_cn"],
            "definition_en": base["definition_en"],
            "definition_cn": base["definition_cn"],
            "aliases_en": uniq(list(base.get("aliases_en", []))),
            "aliases_cn": uniq(list(base.get("aliases_cn", []))),
            "locked": True,
            "formula": str(base.get("formula", "")),
            "related_report_ids": related_report_ids,
            "related_chapter_ids": chapter_ids_for_reports(related_report_ids, report_map),
            "provenance": [
                {
                    "type": "manual_lock_table",
                    "source": "scripts/build_glossary.py#MANUAL_LOCKED_TERMS",
                }
            ],
        }
        terms.append(term)

    for card in theory_map.get("cards", []):
        report_ids = uniq([str(x) for x in card.get("report_ids", [])])
        term = {
            "term_id": f"theory-{card['id']}",
            "category": "theory-card",
            "term_en": str(card.get("label_en", "")).strip() or str(card.get("id", "")),
            "term_cn": str(card.get("label_cn", "")).strip() or str(card.get("id", "")),
            "definition_en": str(card.get("description_en", "")).strip() or "Theory concept card.",
            "definition_cn": str(card.get("description_cn", "")).strip() or "理论概念卡片。",
            "aliases_en": [],
            "aliases_cn": [],
            "locked": True,
            "related_report_ids": report_ids,
            "related_chapter_ids": chapter_ids_for_reports(report_ids, report_map),
            "provenance": [
                {
                    "type": "theory_map",
                    "source": f"site/public/data/v1/theory_map.json#cards/{card.get('id')}",
                }
            ],
        }
        terms.append(term)

    dedup: dict[str, dict[str, Any]] = {}
    for term in terms:
        dedup[term["term_id"]] = term

    merged = sorted(dedup.values(), key=lambda row: str(row["term_id"]))
    payload = {
        "version": "v1",
        "generated_at": utc_now_iso(),
        "term_count": len(merged),
        "terms": merged,
    }

    output_path = data_root / "glossary" / "terms.json"
    write_json(output_path, payload)

    print(
        json.dumps(
            {
                "ok": True,
                "output": output_path.as_posix(),
                "term_count": len(merged),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
