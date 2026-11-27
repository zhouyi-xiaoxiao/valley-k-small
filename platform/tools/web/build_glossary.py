#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from book_blueprint import report_to_chapters


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_DATA_ROOT = REPO_ROOT / "platform" / "web" / "public" / "data" / "v1"


MANUAL_LOCKED_TERMS: list[dict[str, Any]] = [
    {
        "term_id": "fpt",
        "category": "core-metric",
        "term_en": "First-passage time (FPT)",
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
        "term_en": "Survival function",
        "term_cn": "生存函数",
        "definition_en": "Probability that first passage has not happened by step t.",
        "definition_cn": "到第 t 步为止尚未首达的概率。",
        "aliases_en": ["tail probability", "S(t)"],
        "aliases_cn": ["尾概率", "S(t)"],
        "formula": "S(t)=P(T>t)",
    },
    {
        "term_id": "hazard",
        "category": "core-metric",
        "term_en": "Hazard rate",
        "term_cn": "风险率",
        "definition_en": "Probability of first passage at step t, given that it has not happened before step t.",
        "definition_cn": "在第 t 步之前尚未首达的条件下，恰在第 t 步首达的概率。",
        "aliases_en": ["discrete hazard", "failure rate"],
        "aliases_cn": ["条件首达率", "离散风险率"],
        "formula": "h(t)=f(t)/S(t-1)",
    },
    {
        "term_id": "bimodality-criterion",
        "category": "diagnostic",
        "term_en": "Two-peak rule",
        "term_cn": "双峰判据",
        "definition_en": (
            "A curve counts as having two peaks only if two strict local maxima pass the report's thresholds. In the "
            "ring reports a peak is a strict local maximum with f(t) ≥ 10⁻⁷, and the second peak must reach at least 1% "
            "of the highest; other reports add a limit on the valley depth and state it."
        ),
        "definition_cn": (
            "只有两个严格局部极大值都通过报告的阈值，曲线才算有两个峰。环模型报告中，峰是满足 f(t) ≥ 10⁻⁷ 的严格局部极大值，"
            "第二个峰至少要达到最高峰的 1%；其他报告另加谷深上限，并在报告中写明。"
        ),
        "aliases_en": ["double-peak criterion", "bimodality criterion"],
        "aliases_cn": ["双峰诊断"],
        "formula": r"f(t-1)<f(t)>f(t+1),\quad f(t)\ge 10^{-7},\quad h_2\ge 0.01\,h_1",
    },
    {
        "term_id": "aw-inversion",
        "category": "method",
        "term_en": "Abate–Whitt (AW) inversion",
        "term_cn": "Abate–Whitt（AW）反演",
        "definition_en": (
            "Recovers the first-passage probabilities f(t) from the generating function F(z): F is evaluated at points "
            "zₖ on a circle of radius r, and a fast Fourier transform (FFT) of these values gives f(t)."
        ),
        "definition_cn": "由生成函数 F(z) 求出首达概率 f(t)：在半径为 r 的圆上取点 zₖ 计算 F，再对这些值做快速傅里叶变换（FFT）得到 f(t)。",
        "aliases_en": ["Abate-Whitt inversion", "FFT inversion"],
        "aliases_cn": ["Abate-Whitt 反演", "FFT 反演"],
        "formula": r"f(t)\approx r^{-t}\frac{1}{m}\sum_{k=0}^{m-1}F(z_k)\,e^{-2\pi i k t/m},\quad z_k=r\,e^{2\pi i k/m}",
    },
    # The three shortcut rules of the ring reports (code names selfloop,
    # renormalize, equal4). u is the site where the shortcut starts, v where it
    # lands. Sources: ring_lazy_flux_en.tex (Model; equal4 section; comparison
    # with ring_valley) and vkcore/ring/jumpover_pipeline.py.
    {
        "term_id": "selfloop-mode",
        "category": "shortcut-variant",
        "term_en": "Shortcut taken from the stay probability",
        "term_cn": "捷径概率取自原地停留概率",
        "definition_en": (
            "Shortcut rule of the lazy-ring reports: at the site where the shortcut starts, a fraction β of the "
            "stay-put probability 1 − q goes to the shortcut; the other steps keep their probabilities."
        ),
        "definition_cn": "懒惰环报告用的捷径规则：在捷径起点，原地不动的概率 1 − q 中有 β 这一份改走捷径，其余走法的概率不变。",
        "aliases_en": ["stay-probability allocation"],
        "aliases_cn": ["停留抽取机制"],
        "formula": r"P(u\to u)=1-q-p,\quad P(u\to v)=p,\quad p=\beta(1-q)",
        # Reports whose own sources use this rule:
        #   final_multitimescale_fpt_encounter_en.tex:171 "lazy\_selfloop"
        #   ring_deriv_k2_en.tex:32 "(A) Lazy-reservoir shortcut: the shortcut probability is taken from the self-loop"
        #   ring_lazy_flux_en.tex:30 "the ``take probability from the self-loop'' model"
        #   ring_lazy_jump_en.tex:49 "Under the selfloop rule, at the source we take probability mass from the self-loop"
        #   ring_lazy_jump_ext/manuscript/sections/repro_en.tex:7 "--mode lazy_selfloop"
        #   ring_lazy_jump_ext_rev2_en.tex:29 "and the lazy\_selfloop mode"
        #   ring_two_target_en.tex:202 "shortcut strength under the selfloop rule"
        #   ring_two_walker_encounter_shortcut_en.tex:43 "Directed Shortcut Injection (Selfloop Mode)"
        "report_ids": [
            "final_multitimescale_fpt_encounter",
            "ring_deriv_k2",
            "ring_lazy_flux",
            "ring_lazy_jump",
            "ring_lazy_jump_ext",
            "ring_lazy_jump_ext_rev2",
            "ring_two_target",
            "ring_two_walker_encounter_shortcut",
        ],
    },
    {
        "term_id": "renormalize-mode",
        "category": "shortcut-variant",
        "term_en": "Shortcut with the other steps rescaled",
        "term_cn": "加入捷径后其余走法等比缩小",
        "definition_en": (
            "Shortcut rule of the non-lazy ring-valley reports: the shortcut is added at its source as one more move, "
            "and all K + 1 moves there get probability 1/(K + 1), so each ring step drops from 1/K to 1/(K + 1)."
        ),
        "definition_cn": (
            "非懒惰环（环上的谷）报告用的捷径规则：在捷径起点把捷径加为多出的一种走法，K + 1 种走法的概率都取 1/(K + 1)，"
            "每个环上步长的概率由 1/K 降为 1/(K + 1)。"
        ),
        "aliases_en": ["mass renormalization"],
        "aliases_cn": ["重标机制"],
        "formula": r"P(u\to u\pm j)=P(u\to v)=\frac{1}{K+1}",
        # Reports whose own sources use this rule:
        #   ring_valley_en.tex:25 "directed edge list with weights 1/deg(src)" (vkcore/ring/valley_study.py:99,111:
        #     deg counts the shortcut, p = 1/deg)
        #   ring_valley_dst_en.tex:192 "the walker uses the shortcut n0 -> dst with probability 1/(K+1)=1/7"
        #   ring_lazy_flux/code/plot_k2_valley_report_contrast.py:41 "valley_report model (non-lazy K-neighbour ring,
        #     add one directed edge and renormalize at source)"
        "report_ids": ["ring_lazy_flux", "ring_valley", "ring_valley_dst"],
    },
    {
        "term_id": "equal4-mode",
        "category": "shortcut-variant",
        "term_en": "Four equal options at the shortcut site",
        "term_cn": "捷径起点四种走法等概率",
        "definition_en": (
            "Shortcut rule compared in the nearest-neighbour lazy-ring report: at the site where the shortcut starts, "
            "the walker stays, steps left, steps right or takes the shortcut, each with probability 1/4; every other "
            "site keeps its usual step probabilities."
        ),
        "definition_cn": "最近邻懒惰环报告比较的一种捷径规则：在捷径起点，原地不动、左移、右移和走捷径的概率各为 1/4；其余格点的步长概率不变。",
        "aliases_en": ["four-equal-options rule"],
        "aliases_cn": ["四等分规则"],
        "formula": r"P(u\to u)=P(u\to u\pm1)=P(u\to v)=\tfrac14",
        # The only report whose sources use this rule:
        #   ring_lazy_flux_en.tex:35 "the “equal4” rule (stay/left/right/shortcut each 1/4 at u)"
        "report_ids": ["ring_lazy_flux"],
    },
    {
        "term_id": "beta-scan",
        "category": "parameter",
        "term_en": "β scan (shortcut strength)",
        "term_cn": "β（捷径强度）扫描",
        "definition_en": "The calculation repeated over a range of shortcut strengths β, to find where two peaks appear and where they disappear.",
        "definition_cn": "在一组捷径强度 β 上重复计算，找出两个峰在哪里出现、在哪里消失。",
        "aliases_en": ["shortcut strength sweep"],
        "aliases_cn": ["捷径强度扫描"],
        "formula": "β ∈ [0,1]",
    },
    # A feature of this site rather than a research term: kept for the theory
    # page's notation list, placed last so the book's short glossary skips it.
    {
        "term_id": "claim-ledger",
        "category": "workflow",
        "term_en": "Claims and sources",
        "term_cn": "结论与出处",
        "definition_en": "The list, on each report page, of the report's claims, each with the files it comes from and the related reports.",
        "definition_cn": "每份报告页上列出的结论，每条都附有它所依据的文件和相关报告。",
        "aliases_en": ["claim list"],
        "aliases_cn": ["结论清单"],
        "formula": "",
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


def sanitize_formula_text(value: str) -> str:
    cleaned = str(value or "").replace("\x07", "\\")
    cleaned = cleaned.replace("\r", " ").replace("\n", " ")
    return " ".join(cleaned.split())


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
        # A term with its own report list (the shortcut rules) names only those
        # reports; every other hand-written term is shared by all of them.
        related_report_ids = sorted(base.get("report_ids") or report_map.keys())
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
            "formula": sanitize_formula_text(str(base.get("formula", ""))),
            "related_report_ids": related_report_ids,
            "related_chapter_ids": chapter_ids_for_reports(related_report_ids, report_map),
            "provenance": [
                {
                    "type": "manual_lock_table",
                    "source": "platform/tools/web/build_glossary.py#MANUAL_LOCKED_TERMS",
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
                    "source": f"platform/web/public/data/v1/theory_map.json#cards/{card.get('id')}",
                }
            ],
        }
        terms.append(term)

    dedup: dict[str, dict[str, Any]] = {}
    for term in terms:
        dedup[term["term_id"]] = term

    # Hand-written terms in the order of the table above (basic quantities, the
    # peak rule, the inversion method, then the three shortcut rules, so a short
    # list shows all three); theory cards after them, by id.
    manual_order = {str(base["term_id"]): index for index, base in enumerate(MANUAL_LOCKED_TERMS)}
    merged = sorted(
        dedup.values(),
        key=lambda row: (manual_order.get(str(row["term_id"]), len(manual_order)), str(row["term_id"])),
    )
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
