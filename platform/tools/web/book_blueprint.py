#!/usr/bin/env python3
from __future__ import annotations

from typing import Any


CHAPTER_BLUEPRINT: list[dict[str, Any]] = [
    {
        "chapter_id": "chapter-0-reading-guide",
        "slug": "reading-guide-notation",
        "order": 0,
        "kicker_en": "Reading Guide",
        "kicker_cn": "阅读导引",
        "title_en": "Chapter 0: Reading Guide & Notation",
        "title_cn": "第0章：阅读方法与符号",
        "summary_en": "How to read this atlas, verify claims, and reuse symbols consistently across all reports.",
        "summary_cn": "说明如何阅读本书、如何核对 claim 证据、以及如何在全报告范围内统一符号。",
        "intro_en": [
            "This chapter defines the reading protocol: start from claims, verify evidence paths, then inspect formula chains and interactive traces.",
            "Notation is aligned across grid and ring families, so symbol reuse does not introduce hidden semantic drift.",
            "After this chapter, every subsequent page can be read as one continuous argument instead of isolated report fragments.",
        ],
        "intro_cn": [
            "本章先给出阅读协议：先看 claim，再核对证据路径，然后进入公式链与交互图。",
            "网格与环模型共享同一套符号约束，避免跨报告阅读时语义漂移。",
            "完成本章后，后续章节可以作为一条连续论证阅读，而非彼此割裂的报告片段。",
        ],
        "report_ids": ["grid2d_bimodality", "ring_deriv_k2", "ring_two_target"],
        "concept_keywords": ["first-passage", "spectral", "notation", "hazard", "survival"],
    },
    {
        "chapter_id": "chapter-1-core-fpt",
        "slug": "core-fpt-concepts",
        "order": 1,
        "kicker_en": "Core Concepts",
        "kicker_cn": "核心概念",
        "title_en": "Chapter 1: Core FPT Concepts",
        "title_cn": "第1章：FPT 核心概念",
        "summary_en": "Build the common vocabulary of f(t), survival, hazard, and practical bimodality diagnostics.",
        "summary_cn": "建立 f(t)、生存函数、hazard 与双峰判据的统一词汇与可操作诊断。",
        "intro_en": [
            "The first-passage distribution is interpreted through complementary views: density, cumulative survival, and hazard-style turning points.",
            "Bimodality is treated as an evidence-backed diagnosis, not a visual impression, and every chapter keeps this constraint.",
            "The same diagnostic language is reused in both lattice and ring settings to keep conclusions comparable.",
        ],
        "intro_cn": [
            "我们用互补视角解释首达分布：密度、累计生存函数、以及 hazard 转折点。",
            "双峰不靠主观图像判断，而是依赖可回链证据的诊断标准，并在后续章节保持一致。",
            "同一诊断语言同时用于网格和环模型，使跨模型结论可比较。",
        ],
        "report_ids": ["grid2d_bimodality", "grid2d_two_target_double_peak", "ring_lazy_flux", "ring_two_target"],
        "concept_keywords": ["first-passage", "hazard", "survival", "bimodality"],
    },
    {
        "chapter_id": "chapter-2-grid2d-family",
        "slug": "grid2d-family",
        "order": 2,
        "kicker_en": "Grid2D Family",
        "kicker_cn": "Grid2D 家族",
        "title_en": "Chapter 2: Grid2D Family",
        "title_cn": "第2章：Grid2D 家族",
        "summary_en": "From periodic baseline to reflecting and two-target variants, showing which structures preserve or break bimodality.",
        "summary_cn": "从周期基线到反射边界与双目标变体，系统比较哪些结构保持或破坏双峰。",
        "intro_en": [
            "Grid2D reports are organized as one progression: baseline, geometric constraints, reflecting boundaries, and two-target interactions.",
            "The chapter highlights which mechanisms remain stable and which are sensitive to boundary or geometry changes.",
            "Every subsection links back to the same claim ledger so conclusions can be checked without rereading all PDFs.",
        ],
        "intro_cn": [
            "Grid2D 报告在本章被串成连续推进：基线、几何约束、反射边界、双目标耦合。",
            "重点是区分稳定机制与对边界/几何敏感的机制。",
            "每个小节都回链到统一 claim 台账，避免反复翻阅 PDF 才能核对结论。",
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
        "kicker_en": "Ring Baseline",
        "kicker_cn": "Ring 基线",
        "title_en": "Chapter 3: Ring Family Baseline",
        "title_cn": "第3章：Ring 家族基线",
        "summary_en": "Establish lazy and non-lazy ring baselines, then align inversion logic and reference behavior before shortcut variants.",
        "summary_cn": "建立 lazy 与 non-lazy 的 ring 双基线，再统一反演主线与 shortcut 变体前的参照行为。",
        "intro_en": [
            "Ring models provide a compact setting for isolating drift, waiting probability, and spectral structure.",
            "This baseline chapter is intentionally conservative: it first aligns lazy and non-lazy controls before adding shortcut perturbations.",
            "The resulting baseline is reused in later chapters as a control for mechanism attribution.",
        ],
        "intro_cn": [
            "环模型提供了紧凑环境，可分离漂移、停留概率与谱结构的作用。",
            "本章先对齐 lazy 与 non-lazy 对照基线，再讨论 shortcut 扰动，避免机制归因混淆。",
            "后续章节都会把这里的结果作为对照组。",
        ],
        "report_ids": ["ring_deriv_k2", "ring_lazy_flux", "ring_lazy_jump", "ring_valley"],
        "concept_keywords": ["ring", "spectral", "lazy", "baseline", "inversion"],
    },
    {
        "chapter_id": "chapter-4-shortcut-variants",
        "slug": "shortcut-variants",
        "order": 4,
        "kicker_en": "Shortcut Variants",
        "kicker_cn": "Shortcut 变体",
        "title_en": "Chapter 4: Shortcut Variants",
        "title_cn": "第4章：Shortcut 变体机制",
        "summary_en": "Compare selfloop/renormalize/equal4 mechanisms and beta scans to explain when shortcut strength flips phase behavior.",
        "summary_cn": "比较 selfloop/renormalize/equal4 与 beta 扫描，解释 shortcut 强度何时触发相位行为改变。",
        "intro_en": [
            "Once shortcuts are introduced, implementation choices become model assumptions that can alter observed phases.",
            "This chapter compares mechanism variants side by side and keeps a strict mapping to parameterized evidence.",
            "The key output is a stable interpretation of beta-strength transitions across compatible ring settings.",
        ],
        "intro_cn": [
            "引入 shortcut 后，实现方式本身就成为模型假设，可能改变相位观测。",
            "本章并排比较机制变体，并将每个判断绑定到可参数化证据。",
            "核心产出是跨 ring 设定可复用的 beta 强度转变解释。",
        ],
        "report_ids": ["ring_lazy_jump", "ring_lazy_jump_ext", "ring_lazy_jump_ext_rev2", "ring_valley_dst"],
        "concept_keywords": ["shortcut", "beta", "selfloop", "renormalize", "equal4"],
    },
    {
        "chapter_id": "chapter-5-cross-model-synthesis",
        "slug": "cross-model-synthesis",
        "order": 5,
        "kicker_en": "Cross-Model Synthesis",
        "kicker_cn": "跨模型综合",
        "title_en": "Chapter 5: Cross-Model Synthesis",
        "title_cn": "第5章：跨模型综合",
        "summary_en": "Unify Grid2D and Ring evidence through shared diagnostics and cross-model regime mapping.",
        "summary_cn": "通过共享诊断与跨模型相图，把 Grid2D 与 Ring 的证据整合到同一解释框架。",
        "intro_en": [
            "This chapter joins lattice and ring narratives by aligning diagnostics instead of forcing identical geometry.",
            "Cross-model statements are accepted only when both sides provide auditable evidence paths.",
            "The synthesis output is a reusable map for transferring intuition across families without overclaiming.",
        ],
        "intro_cn": [
            "本章通过“诊断对齐”而非“几何等同”来连接网格与环模型叙事。",
            "跨模型结论只在两侧都具备可审计证据路径时成立。",
            "最终形成可复用的迁移图谱，在避免过度外推的前提下转移直觉。",
        ],
        "report_ids": ["cross_luca_regime_map", "grid2d_two_target_double_peak", "ring_two_target", "ring_valley_dst"],
        "concept_keywords": ["cross", "regime", "synthesis", "phase", "hazard"],
    },
    {
        "chapter_id": "chapter-6-repro-validation",
        "slug": "reproducibility-validation",
        "order": 6,
        "kicker_en": "Validation",
        "kicker_cn": "复现与验证",
        "title_en": "Chapter 6: Reproducibility & Validation",
        "title_cn": "第6章：复现与验证",
        "summary_en": "Show command-level reproducibility, audit constraints, and practical error boundaries for the full pipeline.",
        "summary_cn": "汇总命令级复现、审计门禁与全链路误差边界。",
        "intro_en": [
            "Reproducibility is treated as part of the scientific claim: commands, generated data, and validation records are all first-class artifacts.",
            "This chapter lists the operational checkpoints used by CI and agent handoff packages.",
            "The emphasis is not only on rerunning scripts, but also on verifying claim-evidence integrity after each change.",
        ],
        "intro_cn": [
            "复现能力被视为科研 claim 的一部分：命令、数据产物与校验记录都属于一等产物。",
            "本章整理 CI 与 agent 交接包中的关键检查点。",
            "重点不仅是“能重跑”，更是“变更后 claim-证据仍然一致”。",
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
        "kicker_cn": "前沿与展望",
        "title_en": "Chapter 7: Outlook & Open Questions",
        "title_cn": "第7章：展望与开放问题",
        "summary_en": "Summarize unresolved mechanisms and propose next experiments with explicit evidence prerequisites.",
        "summary_cn": "总结尚未解决的机制问题，并给出带证据前提的下一步实验路线。",
        "intro_en": [
            "The final chapter is not a loose discussion: each open question is anchored to known evidence gaps.",
            "We separate confirmed mechanisms from plausible hypotheses to prevent narrative inflation.",
            "The output is a roadmap that an incoming agent can continue without restarting context collection.",
        ],
        "intro_cn": [
            "最后一章不是泛泛讨论，每个开放问题都对应已知证据缺口。",
            "我们明确区分“已确认机制”与“合理假设”，避免叙事膨胀。",
            "产出是一份可交接路线图，使新 agent 无需重新收集全部上下文。",
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
