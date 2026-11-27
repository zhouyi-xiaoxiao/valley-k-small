#!/usr/bin/env python3
from __future__ import annotations

from typing import Any


CHAPTER_BLUEPRINT: list[dict[str, Any]] = [
    {
        "chapter_id": "chapter-0-reading-guide",
        "slug": "reading-guide-notation",
        "order": 0,
        "kicker_en": "Reading guide",
        "kicker_cn": "阅读导引",
        "title_en": "Chapter 0: Reading guide and notation",
        "title_cn": "第0章：阅读方法与符号",
        "summary_en": "How to read this book, how to follow each claim to its report, and the notation of the lattice and ring models.",
        "summary_cn": "怎样读这本书、怎样从每条结论找到它所在的报告，以及二维格点和环模型的记号。",
        "intro_en": [
            "This chapter explains how to read the book: start from the claims, follow each one to its report, then read the formulas and the charts.",
            "The lattice and ring reports use the same symbols where they can: f(t) for the probability of first arriving at step t, and q for the probability of moving in one step.",
        ],
        "intro_cn": [
            "本章先说明怎样读这本书：先看结论，再顺着结论找到它所在的报告，然后读公式和图。",
            "二维格点和环模型的报告尽量用同一套记号：f(t) 是第 t 步首次到达的概率，q 是每一步移动的概率。",
        ],
        "report_ids": ["grid2d_bimodality", "ring_deriv_k2", "ring_two_target"],
        "concept_keywords": ["first-passage", "spectral", "notation", "hazard", "survival"],
    },
    {
        "chapter_id": "chapter-1-core-fpt",
        "slug": "core-fpt-concepts",
        "order": 1,
        "kicker_en": "Core concepts",
        "kicker_cn": "核心概念",
        "title_en": "Chapter 1: Core first-passage concepts",
        "title_cn": "第1章：首达时间的基本概念",
        "summary_en": "The quantities every later chapter uses: the first-passage distribution f(t), the survival function, the hazard rate, and the rule for deciding whether f(t) has two peaks.",
        "summary_cn": "后面各章都要用到的几个量：首达时间分布 f(t)、生存函数、风险率，以及判断 f(t) 是否有两个峰的判据。",
        "intro_en": [
            "f(t) is read together with two companions: the survival function S(t), the probability that the target has not been reached by step t, and the hazard rate h(t) = f(t)/S(t − 1), the probability of arriving at step t given no arrival before.",
            "Whether f(t) has two peaks is decided by a criterion stated in each report, not by eye; the lattice reports and the ring reports use different criteria.",
        ],
        "intro_cn": [
            "读 f(t) 时还要看另外两个量：生存函数 S(t)，即到第 t 步为止还没到达目标的概率；风险率 h(t) = f(t)/S(t − 1)，即在此前一直没有到达的条件下，恰在第 t 步到达的概率。",
            "f(t) 是否有两个峰不凭肉眼判断，而按各报告写明的判据来定；二维格点报告和环模型报告用的判据不同。",
        ],
        "report_ids": ["grid2d_bimodality", "grid2d_two_target_double_peak", "ring_lazy_flux", "ring_two_target"],
        "concept_keywords": ["first-passage", "hazard", "survival", "bimodality"],
    },
    {
        "chapter_id": "chapter-2-grid2d-family",
        "slug": "grid2d-family",
        "order": 2,
        "kicker_en": "Two-dimensional lattices",
        "kicker_cn": "二维格点",
        "title_en": "Chapter 2: Two-dimensional lattices",
        "title_cn": "第2章：二维格点",
        "summary_en": "From the periodic baseline to reflecting walls and two targets: which changes to the lattice keep the two peaks of f(t) and which remove them.",
        "summary_cn": "从周期边界的基线到反射边界和双目标：格点的哪些改动保留 f(t) 的两个峰，哪些让它消失。",
        "intro_en": [
            "The lattice reports are read in order: the baseline, geometric constraints, reflecting boundaries, and two targets.",
            "For each change, the chapter says whether f(t) keeps its two peaks.",
            "Each claim below links to the report it comes from.",
        ],
        "intro_cn": [
            "本章按顺序读二维格点的几份报告：基线、几何约束、反射边界、双目标。",
            "对每一种改动，本章说明 f(t) 是否仍有两个峰。",
            "下面每条结论都连到它所在的报告。",
        ],
        "report_ids": [
            "grid2d_bimodality",
            "grid2d_blackboard_bimodality",
            "grid2d_rect_bimodality",
            "grid2d_reflecting_bimodality",
            "grid2d_two_target_double_peak",
        ],
        "concept_keywords": ["grid", "boundary", "reflecting", "corridor", "two-target"],
    },
    {
        "chapter_id": "chapter-3-ring-baseline",
        "slug": "ring-family-baseline",
        "order": 3,
        "kicker_en": "Ring baseline",
        "kicker_cn": "环模型基线",
        "title_en": "Chapter 3: The ring baseline",
        "title_cn": "第3章：环模型基线",
        "summary_en": "Rings where the walker may stay put and rings where it may not: the closed Chebyshev form of the propagator, how f(t) is computed exactly, and for which N and K two peaks appear.",
        "summary_cn": "可以原地停留和不能停留的两种环：传播子的切比雪夫闭式、f(t) 的精确算法，以及 N 和 K 取哪些值时出现两个峰。",
        "intro_en": [
            "The ring reports give the propagator in closed Chebyshev form and compute f(t) exactly.",
            "This chapter starts from the ring without a shortcut, with and without staying put, and then adds a single directed shortcut.",
            "Later chapters compare their results with these rings.",
        ],
        "intro_cn": [
            "环模型的报告给出传播子的切比雪夫闭式，并精确计算 f(t)。",
            "本章先看没有捷径的环（可以停留和不能停留两种），再加入一条有向捷径。",
            "后面各章都拿这里的环作对照。",
        ],
        "report_ids": ["ring_deriv_k2", "ring_lazy_flux", "ring_lazy_jump", "ring_valley"],
        "concept_keywords": ["ring", "spectral", "lazy", "baseline", "inversion"],
    },
    {
        "chapter_id": "chapter-4-shortcut-variants",
        "slug": "shortcut-variants",
        "order": 4,
        "kicker_en": "Shortcut variants",
        "kicker_cn": "捷径变体",
        "title_en": "Chapter 4: Shortcut variants",
        "title_cn": "第4章：捷径的各种变体",
        "summary_en": "On rings of 100 sites: for which shortcut strengths β and which landing sites f(t) has two peaks, how this differs between K = 2 and K = 4 (the landing-site scan uses K = 6), and which routes make the early and the late peak.",
        "summary_cn": "在 100 个格点的环上：捷径强度 β 取哪些值、捷径落在哪些格点时 f(t) 有两个峰，K = 2 与 K = 4 有何不同（落点扫描用的是 K = 6），以及早峰和晚峰各由哪些路径构成。",
        "intro_en": [
            "Once a shortcut is added, its strength β and the site it lands on decide whether f(t) has one peak or two.",
            "The chapter sets rings with K = 2 and K = 4 side by side and gives, for each, the range of β with two peaks and the share of walkers in each peak that used the shortcut.",
        ],
        "intro_cn": [
            "加入捷径后，捷径强度 β 和捷径落在哪个格点决定 f(t) 是一个峰还是两个峰。",
            "本章把 K = 2 和 K = 4 的环并排比较，分别给出出现两个峰的 β 范围，以及每个峰里走过捷径的游走者所占的比例。",
        ],
        "report_ids": ["ring_lazy_jump", "ring_lazy_jump_ext", "ring_lazy_jump_ext_rev2", "ring_valley_dst"],
        "concept_keywords": ["shortcut", "beta", "selfloop", "renormalize", "equal4"],
    },
    {
        "chapter_id": "chapter-5-cross-model-synthesis",
        "slug": "cross-model-synthesis",
        "order": 5,
        "kicker_en": "Cross-model synthesis",
        "kicker_cn": "跨模型综合",
        "title_en": "Chapter 5: Cross-model synthesis",
        "title_cn": "第5章：跨模型综合",
        "summary_en": "Two-target results on the lattice and on the ring side by side, where the shortcut lands, and a timing comparison of two exact methods for f(t) on 160 lattice cases.",
        "summary_cn": "把二维格点和环上的双目标结果并排比较，看捷径落点的作用，并在 160 个格点算例上比较两种精确计算 f(t) 的方法所用的时间。",
        "intro_en": [
            "The lattice and the ring have different geometry, so this chapter compares them through the same quantity: the times of the two peaks of f(t).",
            "It also compares two exact ways of computing f(t) on 160 lattice cases: stepping the transition matrix forward, and inverting the generating function.",
        ],
        "intro_cn": [
            "二维格点和环的几何不同，所以本章用同一个量来比较它们：f(t) 两个峰出现的时间。",
            "本章还在 160 个格点算例上比较两种精确计算 f(t) 的方法：按转移矩阵逐步递推，以及反演生成函数。",
        ],
        "report_ids": ["cross_luca_regime_map", "grid2d_two_target_double_peak", "ring_two_target", "ring_valley_dst"],
        "concept_keywords": ["cross", "regime", "synthesis", "phase", "hazard"],
    },
    {
        "chapter_id": "chapter-6-repro-validation",
        "slug": "reproducibility-validation",
        "order": 6,
        "kicker_en": "Robustness checks",
        "kicker_cn": "稳健性检查",
        "title_en": "Chapter 6: Robustness checks",
        "title_cn": "第6章：稳健性检查",
        "summary_en": "Whether the two-peak results hold when the setting changes (fully reflecting walls, other widths and start positions), and which route fills each peak on the ring.",
        "summary_cn": "条件改变时（墙壁全部反射、宽度和起点不同）双峰结果是否仍然成立，以及环上每个峰由哪条路径构成。",
        "intro_en": [
            "This chapter asks whether the two-peak results of the earlier chapters still hold when the setting changes: walls made fully reflecting, the lattice made wider, the start moved.",
            "For the ring, Monte Carlo counts of the walkers in each peak show which route fills it.",
        ],
        "intro_cn": [
            "本章看前面各章的双峰结果在条件改变时是否仍然成立：墙壁全部改为反射、格点加宽、起点移动。",
            "对环模型，用蒙特卡洛统计每个峰里的游走者，看每个峰由哪条路径构成。",
        ],
        "report_ids": [
            "grid2d_bimodality",
            "grid2d_rect_bimodality",
            "grid2d_reflecting_bimodality",
            "grid2d_two_target_double_peak",
            "ring_lazy_flux",
            "ring_lazy_jump_ext_rev2",
            "ring_valley_dst",
        ],
        "concept_keywords": ["reproducibility", "audit", "validation", "schema", "consistency"],
    },
    {
        "chapter_id": "chapter-7-outlook",
        "slug": "outlook-open-questions",
        "order": 7,
        "kicker_en": "Outlook",
        "kicker_cn": "展望",
        "title_en": "Chapter 7: Outlook and open questions",
        # Not written yet: the chapter page prints no read time.
        "written": False,
        "title_cn": "第7章：展望与开放问题",
        "summary_en": "Not yet written: the open questions will be stated here, drawn from the reports this chapter lists.",
        "summary_cn": "尚未写成：开放问题将写在这里，依据本章所列的报告。",
        "intro_en": [
            "This chapter is not written yet; its open questions will come from the reports it lists.",
        ],
        "intro_cn": [
            "本章尚未写成；开放问题将出自本章所列的报告。",
        ],
        "report_ids": ["cross_luca_regime_map", "ring_valley_dst", "grid2d_two_target_double_peak", "ring_two_target"],
        "concept_keywords": ["outlook", "open question", "phase transition", "future work"],
    },
]


def report_to_chapters() -> dict[str, list[str]]:
    mapping: dict[str, list[str]] = {}
    for chapter in CHAPTER_BLUEPRINT:
        chapter_id = str(chapter["chapter_id"])
        for report_id in chapter.get("report_ids", []):
            rid = str(report_id)
            mapping.setdefault(rid, []).append(chapter_id)
    return mapping
