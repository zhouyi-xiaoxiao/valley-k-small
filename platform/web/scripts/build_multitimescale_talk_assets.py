#!/usr/bin/env python3
"""Build the multitimescale encounter talk data and lightweight SVG assets."""

from __future__ import annotations

import json
from pathlib import Path
from textwrap import dedent


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "public" / "data" / "v1" / "talks" / "multitimescale-encounter"
ASSET_DIR = ROOT / "public" / "talk-assets" / "multitimescale-encounter"


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_json(path: Path, payload: object) -> None:
    write(path, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


def svg_shell(body: str) -> str:
    return dedent(
        f"""\
        <svg xmlns="http://www.w3.org/2000/svg" width="1600" height="900" viewBox="0 0 1600 900" fill="none">
          <rect width="1600" height="900" fill="#f7f7f3"/>
          {body}
        </svg>
        """
    )


def curve(points: list[tuple[int, int]], color: str, width: int = 16) -> str:
    commands = [f"{'M' if index == 0 else 'L'} {x} {y}" for index, (x, y) in enumerate(points)]
    return f'<path d="{" ".join(commands)}" stroke="{color}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"/>'


def label(x: int, y: int, text: str, size: int = 34, color: str = "#25313b", weight: int = 700) -> str:
    return (
        f'<text x="{x}" y="{y}" font-family="Inter, Arial, sans-serif" '
        f'font-size="{size}" font-weight="{weight}" fill="{color}">{text}</text>'
    )


def small(x: int, y: int, text: str, size: int = 24, color: str = "#5b6670") -> str:
    return label(x, y, text, size=size, color=color, weight=500)


def build_svgs() -> None:
    write(
        ASSET_DIR / "slide1-hidden-routes.svg",
        svg_shell(
            dedent(
                """\
                <rect x="120" y="126" width="606" height="600" fill="#ffffff" stroke="#d4d8cf" stroke-width="3"/>
                <rect x="846" y="126" width="634" height="600" fill="#ffffff" stroke="#d4d8cf" stroke-width="3"/>
                <circle cx="268" cy="426" r="22" fill="#0f766e"/>
                <circle cx="580" cy="426" r="22" fill="#b91c1c"/>
                <path d="M268 426 C360 260 478 258 580 426" stroke="#0f766e" stroke-width="16" stroke-linecap="round"/>
                <path d="M268 426 C356 590 486 598 580 426" stroke="#d97706" stroke-width="16" stroke-linecap="round"/>
                <path d="M972 620 L1042 438 L1112 304 L1182 452 L1252 606 L1322 508 L1392 360" stroke="#0f766e" stroke-width="18" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M972 620 L1042 438 L1112 304 L1182 452 L1252 606 L1322 508 L1392 360" stroke="#25313b" stroke-width="5" stroke-dasharray="14 18" stroke-linecap="round" stroke-linejoin="round" opacity="0.45"/>
                """
            )
            + label(166, 205, "route space", 30, "#25313b", 700)
            + small(956, 205, "first-passage trace")
            + small(192, 690, "fast and delayed branches can both survive")
            + small(952, 690, "shape is evidence only after controls")
        ),
    )

    write(
        ASSET_DIR / "slide2-evidence-grammar.svg",
        svg_shell(
            dedent(
                """\
                <rect x="126" y="166" width="362" height="468" fill="#ffffff" stroke="#d4d8cf" stroke-width="3"/>
                <rect x="620" y="166" width="362" height="468" fill="#ffffff" stroke="#d4d8cf" stroke-width="3"/>
                <rect x="1114" y="166" width="362" height="468" fill="#ffffff" stroke="#d4d8cf" stroke-width="3"/>
                <path d="M488 400 H620" stroke="#60706b" stroke-width="8" stroke-linecap="round"/>
                <path d="M982 400 H1114" stroke="#60706b" stroke-width="8" stroke-linecap="round"/>
                <circle cx="307" cy="380" r="92" fill="#d7ebe7"/>
                <circle cx="307" cy="482" r="54" fill="#f2d7a4"/>
                <path d="M690 502 L750 338 L812 258 L874 432 L936 354" stroke="#0f766e" stroke-width="16" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M1186 520 L1246 350 L1306 300 L1366 470 L1426 446" stroke="#b91c1c" stroke-width="14" stroke-dasharray="18 18" stroke-linecap="round" stroke-linejoin="round"/>
                """
            )
            + label(174, 242, "mechanism", 34)
            + label(672, 242, "decomposition", 34)
            + label(1164, 242, "artifact filter", 34)
            + small(170, 584, "routes, targets, budgets")
            + small(666, 584, "who contributes to f(t)?")
            + small(1160, 584, "parity, tails, shoulders")
        ),
    )

    write(
        ASSET_DIR / "slide3-ring-shortcut.svg",
        svg_shell(
            dedent(
                """\
                <circle cx="438" cy="440" r="236" stroke="#25313b" stroke-width="12"/>
                <circle cx="292" cy="282" r="24" fill="#0f766e"/>
                <circle cx="602" cy="588" r="28" fill="#b91c1c"/>
                <path d="M292 282 C420 236 542 302 602 588" stroke="#d97706" stroke-width="18" stroke-linecap="round"/>
                <path d="M872 620 L950 336 L1028 214 L1106 468 L1184 626 L1262 530 L1340 384" stroke="#0f766e" stroke-width="18" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M872 620 L950 336 L1028 214 L1106 468 L1184 626 L1262 530 L1340 384" stroke="#d97706" stroke-width="8" stroke-dasharray="18 18" stroke-linecap="round" stroke-linejoin="round" opacity="0.7"/>
                <rect x="844" y="162" width="536" height="548" fill="none" stroke="#d4d8cf" stroke-width="3"/>
                """
            )
            + label(176, 184, "minimal route competition", 32)
            + small(184, 742, "shortcut changes both timing and mass")
            + small(878, 742, "late branch is a mechanism candidate")
        ),
    )

    write(
        ASSET_DIR / "slide4-grid2d-targets.svg",
        svg_shell(
            dedent(
                """\
                <rect x="120" y="124" width="560" height="560" fill="#ffffff" stroke="#d4d8cf" stroke-width="3"/>
                <rect x="844" y="124" width="560" height="560" fill="#ffffff" stroke="#d4d8cf" stroke-width="3"/>
                <g stroke="#d8ded6" stroke-width="3">
                  <path d="M190 124 V684"/><path d="M260 124 V684"/><path d="M330 124 V684"/><path d="M400 124 V684"/><path d="M470 124 V684"/><path d="M540 124 V684"/><path d="M610 124 V684"/>
                  <path d="M120 194 H680"/><path d="M120 264 H680"/><path d="M120 334 H680"/><path d="M120 404 H680"/><path d="M120 474 H680"/><path d="M120 544 H680"/><path d="M120 614 H680"/>
                  <path d="M914 124 V684"/><path d="M984 124 V684"/><path d="M1054 124 V684"/><path d="M1124 124 V684"/><path d="M1194 124 V684"/><path d="M1264 124 V684"/><path d="M1334 124 V684"/>
                  <path d="M844 194 H1404"/><path d="M844 264 H1404"/><path d="M844 334 H1404"/><path d="M844 404 H1404"/><path d="M844 474 H1404"/><path d="M844 544 H1404"/><path d="M844 614 H1404"/>
                </g>
                <rect x="190" y="334" width="350" height="140" fill="#d7ebe7" opacity="0.85"/>
                <path d="M190 474 C310 616 482 622 610 334" stroke="#d97706" stroke-width="16" stroke-linecap="round"/>
                <path d="M260 404 H540" stroke="#0f766e" stroke-width="18" stroke-linecap="round"/>
                <circle cx="190" cy="404" r="24" fill="#0f766e"/>
                <rect x="540" y="334" width="42" height="42" fill="#b91c1c"/>
                <circle cx="914" cy="404" r="24" fill="#0f766e"/>
                <rect x="1264" y="264" width="42" height="42" fill="#b91c1c"/>
                <rect x="1194" y="544" width="42" height="42" fill="#b91c1c"/>
                <path d="M914 404 C1034 236 1170 236 1285 285" stroke="#0f766e" stroke-width="16" stroke-linecap="round"/>
                <path d="M914 404 C1034 620 1166 646 1215 565" stroke="#d97706" stroke-width="16" stroke-linecap="round"/>
                <g transform="translate(546 682)">
                  <rect width="508" height="178" rx="24" fill="#fffdf8" stroke="#9aa8a2" stroke-width="3"/>
                  <g transform="translate(32 30)">
                    <g stroke="#d8ded6" stroke-width="3">
                      <path d="M0 42 H168"/><path d="M0 84 H168"/><path d="M0 126 H168"/>
                      <path d="M42 0 V126"/><path d="M84 0 V126"/><path d="M126 0 V126"/>
                    </g>
                    <circle cx="84" cy="84" r="15" fill="#0f766e"/>
                    <circle cx="84" cy="42" r="9" fill="#d97706"/><circle cx="126" cy="84" r="9" fill="#d97706"/>
                    <circle cx="84" cy="126" r="9" fill="#d97706"/><circle cx="42" cy="84" r="9" fill="#d97706"/>
                    <path d="M84 74 V50" stroke="#25313b" stroke-width="6" stroke-linecap="round"/>
                    <path d="M94 84 H118" stroke="#25313b" stroke-width="6" stroke-linecap="round"/>
                    <path d="M84 94 V118" stroke="#25313b" stroke-width="6" stroke-linecap="round"/>
                    <path d="M74 84 H50" stroke="#25313b" stroke-width="6" stroke-linecap="round"/>
                    <path d="M84 38 L75 52 H93 Z" fill="#25313b"/>
                    <path d="M130 84 L116 75 V93 Z" fill="#25313b"/>
                    <path d="M84 130 L75 116 H93 Z" fill="#25313b"/>
                    <path d="M38 84 L52 75 V93 Z" fill="#25313b"/>
                  </g>
                  <text x="230" y="62" font-family="Inter, Arial, sans-serif" font-size="32" font-weight="700" fill="#25313b">2D lattice hop</text>
                  <text x="230" y="102" font-family="Inter, Arial, sans-serif" font-size="22" font-weight="500" fill="#5b6670">nearest-neighbour jumps</text>
                  <text x="230" y="134" font-family="Inter, Arial, sans-serif" font-size="22" font-weight="500" fill="#5b6670">come before target logic</text>
                </g>
                """
            )
            + label(154, 176, "one target", 30)
            + small(154, 216, "outside budget")
            + label(878, 176, "two targets", 30)
            + small(878, 216, "route-target pairs")
        ),
    )

    write(
        ASSET_DIR / "slide5-budget-vs-membrane.svg",
        svg_shell(
            dedent(
                """\
                <rect x="132" y="152" width="560" height="520" fill="#ffffff" stroke="#d4d8cf" stroke-width="3"/>
                <rect x="854" y="152" width="560" height="520" fill="#ffffff" stroke="#d4d8cf" stroke-width="3"/>
                <rect x="250" y="248" width="324" height="230" fill="#d7ebe7"/>
                <path d="M250 248 V478" stroke="#25313b" stroke-width="12"/>
                <path d="M574 248 V478" stroke="#25313b" stroke-width="12"/>
                <path d="M190 592 C288 360 446 350 620 592" stroke="#d97706" stroke-width="18" stroke-linecap="round"/>
                <path d="M930 586 L1010 424 L1090 334 L1170 460 L1250 594 L1330 510" stroke="#0f766e" stroke-width="18" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M930 640 L1010 612 L1090 572 L1170 520 L1250 488 L1330 474" stroke="#b91c1c" stroke-width="12" stroke-linecap="round" stroke-linejoin="round" opacity="0.75"/>
                """
            )
            + label(196, 228, "partition")
            + label(920, 228, "budget signal")
            + small(196, 714, "outside-time evidence separates valley and peak2")
            + small(920, 714, "membrane probability alone is not enough")
        ),
    )

    write(
        ASSET_DIR / "slide6-encounter-guardrail.svg",
        svg_shell(
            dedent(
                """\
                <rect x="108" y="132" width="434" height="584" fill="#ffffff" stroke="#d4d8cf" stroke-width="3"/>
                <rect x="583" y="132" width="434" height="584" fill="#ffffff" stroke="#d4d8cf" stroke-width="3"/>
                <rect x="1058" y="132" width="434" height="584" fill="#ffffff" stroke="#d4d8cf" stroke-width="3"/>
                <path d="M176 580 L230 390 L284 254 L338 520 L392 604 L446 536" stroke="#b91c1c" stroke-width="16" stroke-dasharray="18 18" stroke-linecap="round"/>
                <path d="M650 578 L710 330 L770 238 L830 386 L890 564 L950 610" stroke="#0f766e" stroke-width="16" stroke-linecap="round"/>
                <path d="M1124 584 L1190 408 L1256 314 L1322 434 L1388 540 L1454 586" stroke="#d97706" stroke-width="16" stroke-linecap="round"/>
                <line x1="132" y1="626" x2="514" y2="626" stroke="#25313b" stroke-width="4"/>
                <line x1="607" y1="626" x2="989" y2="626" stroke="#25313b" stroke-width="4"/>
                <line x1="1082" y1="626" x2="1464" y2="626" stroke="#25313b" stroke-width="4"/>
                """
            )
            + label(158, 222, "parity artifact", 30, "#b91c1c")
            + label(638, 222, "same-target tail", 30, "#0f766e")
            + label(1104, 222, "target-shift shoulder", 30, "#b45309")
            + small(182, 682, "reject as robust F2")
            + small(652, 682, "explain by decomposition")
            + small(1110, 682, "weak, not a clean double")
        ),
    )

    write(
        ASSET_DIR / "slide8-evidence-map.svg",
        svg_shell(
            dedent(
                """\
                <rect x="154" y="166" width="324" height="426" fill="#ffffff" stroke="#d4d8cf" stroke-width="3"/>
                <rect x="638" y="166" width="324" height="426" fill="#ffffff" stroke="#d4d8cf" stroke-width="3"/>
                <rect x="1122" y="166" width="324" height="426" fill="#ffffff" stroke="#d4d8cf" stroke-width="3"/>
                <path d="M478 378 H638" stroke="#60706b" stroke-width="8" stroke-linecap="round"/>
                <path d="M962 378 H1122" stroke="#60706b" stroke-width="8" stroke-linecap="round"/>
                <circle cx="316" cy="324" r="76" fill="#d7ebe7"/>
                <path d="M718 486 L778 306 L838 250 L898 432" stroke="#0f766e" stroke-width="16" stroke-linecap="round"/>
                <path d="M1202 492 L1262 320 L1322 270 L1382 438" stroke="#b91c1c" stroke-width="14" stroke-dasharray="18 18" stroke-linecap="round"/>
                """
            )
            + label(210, 240, "model family", 31)
            + label(690, 240, "decomposition", 31)
            + label(1170, 240, "claim status", 31)
            + small(204, 536, "ring / Grid2D / encounter")
            + small(688, 536, "route, target, budget")
            + small(1170, 536, "positive, guarded, rejected")
            + label(274, 686, "evidence grammar", 42, "#164e47")
        ),
    )


def build_talk_data() -> None:
    slides = [
        {
            "id": "opening",
            "order": 1,
            "start": "0:00",
            "end": "0:50",
            "title": "Double peaks are evidence, not decoration",
            "title_en": "Double peaks are evidence, not decoration",
            "title_cn": "双峰是证据，不是装饰",
            "sentence": "A first-passage distribution can reveal hidden route families, but only after artifacts are ruled out.",
            "sentence_en": "A first-passage distribution can reveal hidden route families, but only after artifacts are ruled out.",
            "sentence_cn": "first-passage 分布可以揭示隐藏路径族，但前提是先排除 artifact。",
            "question_en": "What would make a second peak trustworthy?",
            "question_cn": "什么条件下第二峰才可信？",
            "evidence": {
                "kind": "image",
                "src": "/talk-assets/multitimescale-encounter/slide1-hidden-routes.svg?v=20260531a",
                "alt_en": "Route diagram and first-passage trace sketch",
                "alt_cn": "路径图与 first-passage 曲线草图",
                "caption_en": "The talk treats shape as a hypothesis that must survive controls.",
                "caption_cn": "本演讲把 shape 当作需要经受控制检验的假设。",
                "show_overlay": True,
                "hide_caption": True,
            },
            "links": [
                {
                    "label_en": "Research atlas",
                    "label_cn": "研究 atlas",
                    "href": "/book/",
                }
            ],
        },
        {
            "id": "evidence-grammar",
            "order": 2,
            "start": "0:50",
            "end": "1:55",
            "title": "A peak is a claim that needs a ledger",
            "title_en": "A peak is a claim that needs a ledger",
            "title_cn": "一个峰就是一条需要 ledger 的 claim",
            "sentence": "The grammar is mechanism, decomposition, and artifact filter; shape alone is not enough.",
            "sentence_en": "The grammar is mechanism, decomposition, and artifact filter; shape alone is not enough.",
            "sentence_cn": "证据语法是 mechanism、decomposition 和 artifact filter；单看形状不够。",
            "question_en": "Can we say what generated the curve?",
            "question_cn": "我们能说明曲线是由什么生成的吗？",
            "evidence": {
                "kind": "image",
                "src": "/talk-assets/multitimescale-encounter/slide2-evidence-grammar.svg?v=20260531a",
                "alt_en": "Three-stage evidence grammar: mechanism, decomposition, artifact filter",
                "alt_cn": "三阶段证据语法：机制、分解、artifact 过滤",
                "caption_en": "Each positive reading needs a matching negative-control discipline.",
                "caption_cn": "每个正向解读都需要对应的 negative-control discipline。",
                "show_overlay": True,
                "hide_caption": True,
            },
        },
        {
            "id": "ring-shortcut",
            "order": 3,
            "start": "1:55",
            "end": "3:05",
            "title": "The ring gives the cleanest positive mechanism",
            "title_en": "The ring gives the cleanest positive mechanism",
            "title_cn": "环模型给出最干净的正向机制",
            "sentence": "A shortcut can preserve both a fast route and a delayed route, making two time scales visible.",
            "sentence_en": "A shortcut can preserve both a fast route and a delayed route, making two time scales visible.",
            "sentence_cn": "shortcut 可以同时保留快速路径和延迟路径，从而让两个时间尺度可见。",
            "question_en": "When does a shortcut split rather than smear the mass?",
            "question_cn": "shortcut 什么时候会分裂质量，而不是把它抹平？",
            "evidence": {
                "kind": "image",
                "src": "/talk-assets/multitimescale-encounter/slide3-ring-shortcut.svg?v=20260531a",
                "alt_en": "Ring shortcut with fast and delayed branches",
                "alt_cn": "带快速与延迟分支的环 shortcut",
                "caption_en": "Ring shortcut evidence anchors the positive part of the story.",
                "caption_cn": "环 shortcut 证据为正向部分定锚。",
                "show_overlay": True,
                "hide_caption": True,
            },
            "links": [
                {
                    "label_en": "ring_lazy_jump_ext_rev2",
                    "label_cn": "ring_lazy_jump_ext_rev2",
                    "href": "/reports/ring_lazy_jump_ext_rev2/",
                }
            ],
        },
        {
            "id": "grid2d-competition",
            "order": 4,
            "start": "3:05",
            "end": "4:25",
            "title": "In Grid2D, route competition becomes geometry",
            "title_en": "In Grid2D, route competition becomes geometry",
            "title_cn": "在 Grid2D 中，路径竞争变成几何问题",
            "sentence": "The walker still makes local lattice hops; the double-peak claim must separate routes from targets.",
            "sentence_en": "The walker still makes local lattice hops; the double-peak claim must separate routes from targets.",
            "sentence_cn": "walker 仍是在二维格点上局部跳动；双峰 claim 必须区分路径和 target。",
            "question_en": "Is the second peak a route, a target, or both?",
            "question_cn": "第二峰来自路径、target，还是两者都有？",
            "evidence": {
                "kind": "image",
                "src": "/talk-assets/multitimescale-encounter/slide4-grid2d-targets.svg?v=20260531b",
                "alt_en": "Nearest-neighbour lattice hop plus one-target and two-target Grid2D mechanism sketches",
                "alt_cn": "最近邻二维格点跳动，以及 one-target 与 two-target Grid2D 机制草图",
                "caption_en": "Grid2D starts from nearest-neighbour hops, then turns route competition into spatial and target competition.",
                "caption_cn": "Grid2D 从最近邻格点跳动开始，再把路径竞争转化为空间和 target 竞争。",
                "show_overlay": True,
                "hide_caption": True,
            },
            "links": [
                {
                    "label_en": "grid2d_membrane_near_target",
                    "label_cn": "grid2d_membrane_near_target",
                    "href": "/reports/grid2d_membrane_near_target/",
                },
                {
                    "label_en": "grid2d_two_target_double_peak",
                    "label_cn": "grid2d_two_target_double_peak",
                    "href": "/reports/grid2d_two_target_double_peak/",
                },
            ],
        },
        {
            "id": "budget-vs-membrane",
            "order": 5,
            "start": "4:25",
            "end": "5:45",
            "title": "Outside budget separates valley and peak2",
            "title_en": "Outside budget separates valley and peak2",
            "title_cn": "outside budget 更能分开 valley 与 peak2",
            "sentence": "Membrane crossing matters, but the stronger diagnostic is where the delayed branch spends its time.",
            "sentence_en": "Membrane crossing matters, but the stronger diagnostic is where the delayed branch spends its time.",
            "sentence_cn": "membrane crossing 很重要，但更强的诊断是 delayed branch 的时间预算在哪里。",
            "question_en": "What is the delayed branch doing between the peaks?",
            "question_cn": "两个峰之间，delayed branch 到底在做什么？",
            "evidence": {
                "kind": "image",
                "src": "/talk-assets/multitimescale-encounter/slide5-budget-vs-membrane.svg?v=20260531a",
                "alt_en": "Outside budget and membrane crossing evidence sketch",
                "alt_cn": "outside budget 与 membrane crossing 证据草图",
                "caption_en": "Budget decomposition is the mechanism-level check.",
                "caption_cn": "budget decomposition 是机制层面的检验。",
                "show_overlay": True,
                "hide_caption": True,
            },
            "links": [
                {
                    "label_en": "one-target budget report",
                    "label_cn": "one-target budget 报告",
                    "href": "/reports/grid2d_one_target_valley_peak_budget/",
                }
            ],
        },
        {
            "id": "encounter-guardrail",
            "order": 6,
            "start": "5:45",
            "end": "7:15",
            "title": "The encounter pilot is the guardrail",
            "title_en": "The encounter pilot is the guardrail",
            "title_cn": "encounter pilot 是科学护栏",
            "sentence": "The latest exact reflecting encounter model found no robust F2 double peak, only artifacts, tails, and weak shoulders.",
            "sentence_en": "The latest exact reflecting encounter model found no robust F2 double peak, only artifacts, tails, and weak shoulders.",
            "sentence_cn": "最新 exact reflecting encounter 模型没有发现稳健 F2 双峰，只看到 artifacts、tails 和 weak shoulders。",
            "question_en": "Which apparent late feature should be rejected?",
            "question_cn": "哪些看似 late feature 应该被拒绝？",
            "evidence": {
                "kind": "image",
                "src": "/talk-assets/multitimescale-encounter/slide6-encounter-guardrail.svg?v=20260531a",
                "alt_en": "Encounter guardrail with artifact categories",
                "alt_cn": "带 artifact 分类的 encounter 护栏图",
                "caption_en": "Negative evidence is part of the final story.",
                "caption_cn": "负结果也是最终叙事的一部分。",
                "show_overlay": True,
                "hide_caption": True,
            },
            "links": [
                {
                    "label_en": "final_multitimescale_fpt_encounter",
                    "label_cn": "final_multitimescale_fpt_encounter",
                    "href": "/reports/final_multitimescale_fpt_encounter/",
                }
            ],
        },
        {
            "id": "mechanism-lab",
            "order": 7,
            "start": "7:15",
            "end": "8:45",
            "title": "Try the evidence grammar",
            "title_en": "Try the evidence grammar",
            "title_cn": "试一下这套 evidence grammar",
            "sentence": "Switch among ring, Grid2D, and encounter cases to see how the same curve shape changes status after artifact checks.",
            "sentence_en": "Switch among ring, Grid2D, and encounter cases to see how the same curve shape changes status after artifact checks.",
            "sentence_cn": "在 ring、Grid2D 与 encounter 之间切换，看同样的曲线形状如何在 artifact check 后改变地位。",
            "question_en": "What survives a stricter artifact filter?",
            "question_cn": "更严格的 artifact filter 下，什么还能保留下来？",
            "animation": {"kind": "mechanism-lab"},
        },
        {
            "id": "final-map",
            "order": 8,
            "start": "8:45",
            "end": "10:00",
            "title": "The output is an evidence grammar",
            "title_en": "The output is an evidence grammar",
            "title_cn": "最终产物是一套 evidence grammar",
            "sentence": "The project is no longer just searching for double peaks; it is classifying when a peak deserves a mechanism claim.",
            "sentence_en": "The project is no longer just searching for double peaks; it is classifying when a peak deserves a mechanism claim.",
            "sentence_cn": "这个项目不再只是寻找双峰，而是在分类什么时候一个峰值得成为机制 claim。",
            "question_en": "What should the next experiment prove before it claims a double peak?",
            "question_cn": "下一组实验在声称双峰前需要先证明什么？",
            "evidence": {
                "kind": "image",
                "src": "/talk-assets/multitimescale-encounter/slide8-evidence-map.svg?v=20260531a",
                "alt_en": "Evidence grammar map from model family to claim status",
                "alt_cn": "从模型族到 claim status 的证据语法图",
                "caption_en": "Claim status is part of the deliverable.",
                "caption_cn": "claim status 本身就是交付物的一部分。",
                "show_overlay": True,
                "hide_caption": True,
            },
            "links": [
                {
                    "label_en": "Book mainline",
                    "label_cn": "书籍主线",
                    "href": "/book/",
                },
                {
                    "label_en": "Report network",
                    "label_cn": "报告网络",
                    "href": "/reports/",
                },
            ],
        },
    ]

    manifest = {
        "talk_id": "multitimescale-encounter",
        "title_en": "Hidden Routes, Real Peaks",
        "title_cn": "隐藏路径与真实双峰",
        "subtitle_en": "A mechanism-first talk on first-passage double peaks and exact encounter guardrails",
        "subtitle_cn": "关于 first-passage 双峰与 exact encounter 护栏的机制优先演讲",
        "audience_en": "Applied probability and mathematical biology audience",
        "audience_cn": "应用概率与数学建模听众",
        "duration_minutes": 10,
        "theme_en": "Mechanism evidence, not shape-chasing",
        "theme_cn": "机制证据，而不是追逐形状",
        "slides": slides,
    }

    script_en = {
        "talk_id": "multitimescale-encounter",
        "lang": "en",
        "blocks": [
            {
                "slide_id": "opening",
                "start": "0:00",
                "end": "0:50",
                "title": "Double peaks are evidence, not decoration",
                "spoken_text": "I want to make one claim precise: a double peak in a first-passage distribution can be evidence for hidden route families, but it is not evidence by itself. The rest of the talk is about what has to survive before I trust the shape.",
                "speaker_notes": "Open with the promise: positive mechanisms plus controls.",
                "timing_prompt": "State the evidence-not-decoration frame.",
            },
            {
                "slide_id": "evidence-grammar",
                "start": "0:50",
                "end": "1:55",
                "title": "A peak is a claim that needs a ledger",
                "spoken_text": "The grammar I use has three checks. First, propose a mechanism. Second, decompose the curve so the mass has a source. Third, run an artifact filter. Without all three, a second peak is only a visual clue.",
                "speaker_notes": "Make the talk's scoring rule explicit.",
                "timing_prompt": "Define mechanism, decomposition, artifact filter.",
            },
            {
                "slide_id": "ring-shortcut",
                "start": "1:55",
                "end": "3:05",
                "title": "The ring gives the cleanest positive mechanism",
                "spoken_text": "On the ring, the mechanism is clean. A shortcut can make a fast branch, while the ordinary route still carries delayed mass. The useful question is not whether a shortcut exists, but whether two route families remain separated and weighted enough to be visible.",
                "speaker_notes": "This is the positive example before the cautionary layer.",
                "timing_prompt": "Use the ring as the simplest positive case.",
            },
            {
                "slide_id": "grid2d-competition",
                "start": "3:05",
                "end": "4:25",
                "title": "In Grid2D, route competition becomes geometry",
                "spoken_text": "In two dimensions, I do not want to lose the basic picture: the walker is still hopping locally on a lattice. Once that primitive is clear, the same double-peak language becomes richer. A second feature can represent a route, a target, or a route-target pair, so the Grid2D work keeps geometry and target count visible instead of collapsing everything into one curve.",
                "speaker_notes": "Keep the lattice-hop schematic visible before moving to spatial mechanisms.",
                "timing_prompt": "Explain route versus target competition.",
            },
            {
                "slide_id": "budget-vs-membrane",
                "start": "4:25",
                "end": "5:45",
                "title": "Outside budget separates valley and peak2",
                "spoken_text": "The one-target Grid2D work sharpened the mechanism test. Membrane crossing matters, but the stronger signal is the time budget outside the central region. The delayed branch is not just crossing a boundary; it is spending time in a different part of the state space.",
                "speaker_notes": "Keep this slide mechanism-level, not table-level.",
                "timing_prompt": "Name outside budget as the sharper diagnostic.",
            },
            {
                "slide_id": "encounter-guardrail",
                "start": "5:45",
                "end": "7:15",
                "title": "The encounter pilot is the guardrail",
                "spoken_text": "The newest exact encounter work is important because it says no. In the current reflecting synchronous co-location model, I do not have a robust F2 double peak. The unusual shapes are better explained as parity artifacts, same-target long tails, or weak target-shift shoulders.",
                "speaker_notes": "Do not soften this negative result. It is the scientific discipline of the talk.",
                "timing_prompt": "Say the negative result plainly.",
            },
            {
                "slide_id": "mechanism-lab",
                "start": "7:15",
                "end": "8:45",
                "title": "Try the evidence grammar",
                "spoken_text": "This small interactive panel is the whole story in miniature. The ring case can be a positive mechanism candidate. The Grid2D case needs decomposition. The encounter case becomes a guardrail: stricter artifact filtering does not make it a clean double peak.",
                "speaker_notes": "Switch the buttons once while speaking.",
                "timing_prompt": "Demonstrate the selector and strictness slider.",
            },
            {
                "slide_id": "final-map",
                "start": "8:45",
                "end": "10:00",
                "title": "The output is an evidence grammar",
                "spoken_text": "So the project has changed shape. I am not simply looking for double peaks. I am building a grammar for when a double peak deserves a mechanism claim, when it needs more decomposition, and when it should be rejected.",
                "speaker_notes": "End with the upgraded research identity.",
                "timing_prompt": "Close on the evidence grammar.",
            },
        ],
    }

    script_cn = {
        "talk_id": "multitimescale-encounter",
        "lang": "cn",
        "blocks": [
            {
                "slide_id": item["slide_id"],
                "start": item["start"],
                "end": item["end"],
                "title": item["title"],
                "spoken_text": cn_text,
                "speaker_notes": cn_notes,
                "timing_prompt": cn_prompt,
            }
            for item, cn_text, cn_notes, cn_prompt in [
                (
                    script_en["blocks"][0],
                    "我想把一个判断讲清楚：first-passage 分布里的双峰可以成为隐藏路径族的证据，但它本身不是证据。整场演讲就是在问：一个形状要经过哪些控制检验，我才愿意相信它。",
                    "开场强调：不是追形状，而是做证据判断。",
                    "讲清楚 evidence-not-decoration。",
                ),
                (
                    script_en["blocks"][1],
                    "我使用三步证据语法。第一，提出机制。第二，把曲线分解出来，说明质量来自哪里。第三，排除 artifact。缺任何一步，第二峰都只是视觉线索。",
                    "把本 talk 的判据先摆出来。",
                    "定义 mechanism、decomposition、artifact filter。",
                ),
                (
                    script_en["blocks"][2],
                    "环模型是最干净的正向例子。shortcut 可以制造快速分支，而普通环路仍保留延迟质量。关键不是有没有 shortcut，而是两类路径族是否既分离又有足够权重。",
                    "先给正向机制，再进入更复杂的空间模型。",
                    "用环模型作为最小正向案例。",
                ),
                (
                    script_en["blocks"][3],
                    "到了二维，最基本的图不能丢：walker 仍然是在二维格点上做局部最近邻跳动。这个 primitive 讲清楚之后，同样的双峰语言才会变复杂：第二个特征可能代表路径，也可能代表 target，或者是 route-target pair。所以 Grid2D 工作不能只看一条曲线，必须保留几何和 target count。",
                    "先保留二维格子跳动示意，再从环直觉过渡到空间机制。",
                    "解释 route competition 和 target competition。",
                ),
                (
                    script_en["blocks"][4],
                    "one-target Grid2D 进一步把机制检验变尖锐。membrane crossing 重要，但更强的信号是 outside time budget。delayed branch 不只是过边界，而是在状态空间另一部分花时间。",
                    "这一页讲机制，不要陷入表格细节。",
                    "强调 outside budget 是更强诊断。",
                ),
                (
                    script_en["blocks"][5],
                    "最新 exact encounter 工作重要，是因为它说了不。在当前 reflecting synchronous co-location model 里，没有稳健 F2 双峰。那些异常形状更适合解释为 parity artifact、same-target long tail 或 weak target-shift shoulder。",
                    "不要弱化负结果，它是整场演讲的科学纪律。",
                    "直接讲 negative result。",
                ),
                (
                    script_en["blocks"][6],
                    "这个交互面板是整场故事的缩影。ring 可以是正向机制候选；Grid2D 需要 decomposition；encounter 是护栏：更严格排除 artifact 后，它不会变成干净双峰。",
                    "讲的时候切换一次按钮和 slider。",
                    "演示 selector 和 strictness slider。",
                ),
                (
                    script_en["blocks"][7],
                    "所以项目的形态已经变了。我不是单纯找双峰，而是在建立一套语法：什么时候双峰值得成为机制 claim，什么时候需要更多分解，什么时候应该被拒绝。",
                    "收束到 upgraded research identity。",
                    "用 evidence grammar 收尾。",
                ),
            ]
        ],
    }

    basic_demo = {
        "grid_width": 7,
        "grid_height": 5,
        "source": {"x": 0, "y": 2},
        "target": {"x": 6, "y": 2},
        "walks": [
            {
                "id": "fast",
                "hit_step": 6,
                "steps": [
                    {"x": 0, "y": 2},
                    {"x": 1, "y": 2},
                    {"x": 2, "y": 2},
                    {"x": 3, "y": 2},
                    {"x": 4, "y": 2},
                    {"x": 5, "y": 2},
                    {"x": 6, "y": 2},
                ],
            },
            {
                "id": "delayed",
                "hit_step": 10,
                "steps": [
                    {"x": 0, "y": 2},
                    {"x": 1, "y": 2},
                    {"x": 1, "y": 1},
                    {"x": 2, "y": 1},
                    {"x": 3, "y": 1},
                    {"x": 3, "y": 2},
                    {"x": 3, "y": 3},
                    {"x": 4, "y": 3},
                    {"x": 5, "y": 3},
                    {"x": 5, "y": 2},
                    {"x": 6, "y": 2},
                ],
            },
        ],
    }

    write_json(DATA_DIR / "manifest.json", manifest)
    write_json(DATA_DIR / "script.en.json", script_en)
    write_json(DATA_DIR / "script.cn.json", script_cn)
    write_json(DATA_DIR / "basic_demo.json", basic_demo)


def main() -> None:
    build_svgs()
    build_talk_data()
    print(f"Wrote talk data to {DATA_DIR}")
    print(f"Wrote talk assets to {ASSET_DIR}")


if __name__ == "__main__":
    main()
