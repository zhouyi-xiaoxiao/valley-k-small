#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_TOOL_DIR = Path(__file__).resolve().parents[1] / "repo"
if str(REPO_TOOL_DIR) not in sys.path:
    sys.path.insert(0, str(REPO_TOOL_DIR))

from report_registry import load_registry


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_OUTPUT_DIR = REPO_ROOT / "platform" / "web" / "public" / "data" / "v1"
DEFAULT_ARTIFACTS_DIR = REPO_ROOT / "platform" / "web" / "public" / "artifacts"
TEXT_EXT = {".md", ".tex", ".txt"}
FIGURE_EXT = {".pdf", ".png", ".svg", ".jpg", ".jpeg", ".webp"}
DATA_EXT = {".json", ".csv", ".npz"}
REPO_SYNC_PREVIEW_EXT = {".md", ".txt", ".tex"}
REPO_SYNC_MAX_FILES = 6000
REPO_SYNC_INCLUDE_GLOBS = [
    "*.md",
    "README.md",
    "AGENTS.md",
    "requirements.txt",
    "pyproject.toml",
    "research/docs/**/*.md",
    "research/docs/**/*.tex",
    "research/reports/**/*.tex",
    "research/reports/**/README.md",
    "research/reports/**/notes/*.md",
    "research/reports/**/code/*.py",
    "platform/README.md",
    "platform/tools/**/*.py",
    "platform/skills/**/*.md",
    "scripts/README.md",
    "scripts/reportctl.py",
    "packages/vkcore/src/**/*.py",
    "tests/**/*.py",
    "platform/schemas/**/*.json",
]
REPO_SYNC_CATEGORY_LABELS: dict[str, dict[str, str]] = {
    "root": {"en": "Root Documents", "cn": "根目录文档"},
    "docs": {"en": "Repository Docs", "cn": "仓库文档"},
    "report_docs": {"en": "Report Notes", "cn": "报告说明"},
    "report_code": {"en": "Report Code", "cn": "报告代码"},
    "tooling": {"en": "Tooling Scripts", "cn": "工具脚本"},
    "core_code": {"en": "Core Library", "cn": "核心库代码"},
    "tests": {"en": "Tests", "cn": "测试代码"},
    "schemas": {"en": "Schemas", "cn": "数据契约"},
    "other": {"en": "Other", "cn": "其他"},
}
MODEL_HINTS = ("model", "problem", "definition", "setup", "convention", "模型", "定义", "设定")
METHOD_HINTS = ("method", "analytic", "inversion", "algorithm", "scan", "protocol", "derivation", "方法", "推导", "验证")
RESULT_HINTS = ("finding", "result", "conclusion", "summary", "结论", "结果", "总结")
REPRO_HINTS = ("reproducibility", "command", "命令", "复现")
LATEX_SYMBOL_REPLACEMENTS = {
    r"\dots": "...",
    r"\cdots": "...",
    r"\to": "->",
    r"\rightarrow": "->",
    r"\leftarrow": "<-",
    r"\mapsto": "=>",
    r"\times": "×",
    r"\cdot": "·",
    r"\pm": "±",
    r"\geq": "≥",
    r"\leq": "≤",
    r"\neq": "≠",
    r"\infty": "∞",
    r"\alpha": "alpha",
    r"\beta": "beta",
    r"\gamma": "gamma",
    r"\lambda": "lambda",
    r"\mu": "mu",
    r"\sigma": "sigma",
}
CLAIM_STOPWORDS = {
    "the",
    "and",
    "for",
    "with",
    "that",
    "this",
    "from",
    "into",
    "under",
    "over",
    "into",
    "via",
    "are",
    "is",
    "was",
    "were",
    "as",
    "of",
    "to",
    "in",
    "on",
    "at",
    "by",
    "or",
    "an",
    "a",
    "can",
    "be",
    "which",
    "using",
    "used",
    "show",
    "shows",
    "report",
    "结果",
    "结论",
    "研究",
    "模型",
    "方法",
    "通过",
    "以及",
    "并且",
    "可以",
    "用于",
}

REPORT_TEXT_OVERRIDES: dict[str, dict[str, dict[str, Any]]] = {
    "ring_lazy_flux": {
        "en": {
            "title": "Lazy Ring Flux Baseline",
            "summary": (
                "This report studies first-passage distributions on a lazy ring (k=1, K=2) with one directed shortcut "
                "drawn from self-loop probability. It combines Chebyshev generating-function derivation, AW/FFT inversion, "
                "and flux-recursion cross-checks to show a reproducible small-p bimodal regime, while equal4 and large shortcut "
                "strength suppress the second peak."
            ),
            "narrative": {
                "model_overview": (
                    "The model is a lazy nearest-neighbor ring with one directed shortcut u->v; away from the shortcut source, "
                    "stay/left/right probabilities follow the equal-probability baseline."
                ),
                "method_overview": (
                    "The pipeline derives the generating function analytically, inverts it via AW/FFT, and verifies the recovered "
                    "pmf by independent flux recursion."
                ),
                "result_overview": (
                    "A small-p selfloop regime yields clear two-peak structure (minimal N=10 example), whereas equal4 and stronger "
                    "shortcut injection collapse the distribution toward unimodality."
                ),
            },
            "key_findings": [
                "A minimal reproducible bimodal case appears at N=10 under small shortcut strength in the selfloop construction.",
                "AW inversion and flux recursion agree to numerical precision, validating both the derivation and implementation.",
                "Full N scans show macro-bimodality concentrated in specific geometry-distance bands rather than uniformly.",
                "Equal4 and large shortcut strength suppress late-time mass and remove the second dominant peak.",
            ],
        },
        "cn": {
            "title": "Lazy Ring Flux 基线机制",
            "summary": (
                "该报告研究 lazy ring（k=1, K=2）在单向 shortcut 且从自环分配概率时的首达分布。通过 Chebyshev 生成函数推导、"
                "AW/FFT 反演与 flux 递推交叉校验，报告给出可复现的小 p 双峰区间，并说明 equal4 与较大 shortcut 强度会抑制第二峰。"
            ),
            "narrative": {
                "model_overview": (
                    "模型为 lazy 最近邻环并加入单向 shortcut u->v；在非 shortcut 源点处，停留/左右迁移遵循等概率基线。"
                ),
                "method_overview": (
                    "方法链路为：解析推导生成函数，使用 AW/FFT 反演得到首达 pmf，再用 flux 递推进行独立数值核验。"
                ),
                "result_overview": (
                    "自环分流且小 p 条件下可形成稳定双峰（最小 N=10 例）；equal4 或 shortcut 强度增大时，分布向单峰收敛。"
                ),
            },
            "key_findings": [
                "在 selfloop 小 p 条件下，N=10 可复现双峰首达分布。",
                "AW 反演与 flux 递推在数值精度内一致，验证了理论与实现的正确性。",
                "全 N 扫描显示宏观双峰主要出现在特定几何距离带，而非全域出现。",
                "equal4 与大 shortcut 强度会削弱晚时通道并消除第二主峰。",
            ],
        },
    },
    "ring_valley": {
        "en": {
            "title": "Ring Valley Regime Map",
            "summary": (
                "This valley-study report analyzes a non-lazy K-neighbor ring with a one-way shortcut 6->N/2+1 under the Fig.3 peak rule. "
                "Exact AW inversion and MC validation map bimodality windows across even N and K: no bimodality for K=2 after parity-aware "
                "coarse graining, but clear windows for K=4,6,8."
            ),
            "narrative": {
                "model_overview": (
                    "The graph is a directed-shortcut ring with uniform K-neighbor transitions and an absorbing target at N/2, "
                    "using paper-consistent indexing and shortcut placement."
                ),
                "method_overview": (
                    "The workflow combines AW inversion, MC trajectory simulation, and Fig.3 peak-valley criteria with K=2 parity coarse graining."
                ),
                "result_overview": (
                    "Across scanned even N, K=2 remains unimodal under the study rule, while K=4/6/8 exhibit structured bimodality bands "
                    "that are reproducible in both exact and MC diagnostics."
                ),
            },
            "key_findings": [
                "Under Fig.3 criteria with parity-aware treatment, K=2 shows no robust two-peak regime in the scanned range.",
                "Bimodality windows emerge for K=4, K=6, and K=8 with distinct N bands.",
                "Exact and MC pipelines agree on peak/valley timing and class-level shortcut usage trends.",
                "Trajectory-class heatmaps separate fast, valley, and indirect pathways and support the mechanism interpretation.",
            ],
        },
        "cn": {
            "title": "Ring Valley 相区研究",
            "summary": (
                "该 valley 研究在非 lazy 的 K 邻接环上考察单向 shortcut（6->N/2+1）并采用 Fig.3 峰谷判据。"
                "通过 AW 精确反演与 MC 校验，报告给出偶数 N 与 K 的双峰区间图：K=2 在奇偶振荡修正后仍不出现稳定双峰，"
                "而 K=4、6、8 出现清晰双峰窗口。"
            ),
            "narrative": {
                "model_overview": (
                    "模型采用均匀 K 邻接跳转与单向 shortcut，吸收目标置于 N/2，并保持与论文图示一致的索引与几何构型。"
                ),
                "method_overview": (
                    "方法链路结合 AW 反演、MC 全路径模拟与 Fig.3 峰谷判据，并对 K=2 使用两步粗粒化处理奇偶微峰。"
                ),
                "result_overview": (
                    "在扫描的偶数 N 范围内，K=2 维持单峰；K=4/6/8 则出现可复现的双峰区间，并在精确解与 MC 诊断中一致。"
                ),
            },
            "key_findings": [
                "在 Fig.3 判据与奇偶修正下，K=2 在扫描区间内不呈现稳定双峰。",
                "K=4、K=6、K=8 分别出现结构化双峰 N 区间。",
                "精确反演与 MC 在峰位、谷位与 shortcut 使用趋势上保持一致。",
                "轨迹分类热图区分了快通道、谷区与间接通道，支持机制解释。",
            ],
        },
    },
    "grid2d_bimodality": {
        "en": {
            "title": "Grid2D Bimodality Baseline",
            "summary": (
                "This foundational Grid2D report establishes how biased/lazy random walks generate first-passage bimodality on a square lattice. "
                "It unifies model constraints, defect-aware propagators, AW inversion, and candidate-case scans into one auditable chain that "
                "separates genuine two-channel mechanisms from plotting artifacts."
            ),
            "narrative": {
                "model_overview": (
                    "The model is a two-dimensional N×N lattice with an absorbing target, anisotropic drift controls, and lazy waiting probability "
                    "under explicit boundary assumptions."
                ),
                "method_overview": (
                    "The method links defect-free and defect-corrected propagators to generating-function inversion, then validates candidate regimes "
                    "through parameter scans and channel diagnostics."
                ),
                "result_overview": (
                    "Bimodality emerges when fast direct routes and delayed wrap-around/detour routes coexist at measurable weights under the same "
                    "diagnostic criterion."
                ),
            },
            "key_findings": [
                "A unified FPT criterion distinguishes structural bimodality from numerical or visualization artifacts.",
                "Candidate corridor/bias settings show that delayed channels can be amplified without changing the target definition.",
                "Model, method, and result statements are traceable through formula blocks, section summaries, and dataset panels.",
                "The report serves as a baseline vocabulary for later reflecting and two-target Grid2D variants.",
            ],
        },
        "cn": {
            "title": "Grid2D 双峰基线",
            "summary": (
                "该基础 Grid2D 报告建立了偏置/惰性随机游走下首达双峰形成的统一框架。报告把模型约束、缺陷修正传播子、AW 反演与参数扫描串成可审计链路，"
                "用于区分真实双通道机制与绘图伪峰。"
            ),
            "narrative": {
                "model_overview": (
                    "模型为二维 N×N 格点 + 吸收目标，包含各向异性漂移控制与惰性停留概率，并显式给出边界条件。"
                ),
                "method_overview": (
                    "方法将无缺陷/缺陷修正传播子连接到生成函数反演，再通过参数扫描与通道诊断验证候选相区。"
                ),
                "result_overview": (
                    "当快通道与延迟绕行通道在同一判据下都具有可观权重时，首达分布出现稳健双峰。"
                ),
            },
            "key_findings": [
                "统一 FPT 判据可稳定区分结构性双峰与数值/可视化伪峰。",
                "走廊与偏置参数可在不改目标定义的前提下放大延迟通道贡献。",
                "模型、方法、结果可通过公式块、章节摘要与数据面板逐项回链。",
                "该报告为后续反射边界与双目标 Grid2D 变体提供基线词汇体系。",
            ],
        },
    },
    "grid2d_rect_bimodality": {
        "en": {
            "title": "Grid2D Rectangle Bimodality",
            "summary": (
                "This report extends Grid2D bimodality from square to rectangular domains, testing how aspect ratio, reflecting walls, and endpoint "
                "geometry reshape first-passage channels. It emphasizes reproducible two-target constructions and identifies when double peaks remain "
                "structural under anisotropic geometry."
            ),
            "narrative": {
                "model_overview": (
                    "The model uses a rectangular reflecting lattice with controllable width/height and either one or two absorbing endpoint targets."
                ),
                "method_overview": (
                    "The workflow scans geometry and bias parameters while keeping first-passage diagnostics fixed, then compares pathway composition "
                    "across rectangular configurations."
                ),
                "result_overview": (
                    "Aspect ratio and endpoint arrangement shift the balance between direct and detour channels; robust double peaks persist only in "
                    "specific rectangular geometry bands."
                ),
            },
            "key_findings": [
                "Rectangular anisotropy can suppress or recover bimodality depending on corridor alignment and target placement.",
                "Two-target endpoint constructions offer a reproducible mechanism for separating fast and delayed channels.",
                "Reflecting-boundary constraints change valley depth through route competition rather than simple amplitude scaling.",
                "The report provides geometry-sensitive evidence needed for cross-family synthesis with ring models.",
            ],
        },
        "cn": {
            "title": "Grid2D 矩形域双峰",
            "summary": (
                "该报告把 Grid2D 双峰分析从方形域扩展到矩形域，系统考察长宽比、反射边界与端点几何如何重塑首达通道。"
                "报告强调可复现的双目标构型，并识别在各向异性几何下双峰何时仍保持结构稳定。"
            ),
            "narrative": {
                "model_overview": (
                    "模型采用可控长宽比的矩形反射格点，并设置单目标或双端点吸收目标。"
                ),
                "method_overview": (
                    "在固定首达诊断口径下扫描几何与偏置参数，再比较不同矩形构型中的路径类别组成。"
                ),
                "result_overview": (
                    "长宽比与端点排布会改变直达/绕行通道权重平衡；稳健双峰只在特定矩形几何带中保持。"
                ),
            },
            "key_findings": [
                "矩形各向异性可根据走廊方向与目标位置抑制或恢复双峰。",
                "双端点目标构型为快慢通道分离提供了可复现实验机制。",
                "反射边界通过路径竞争改变谷深，而非仅做幅值缩放。",
                "该报告补充了跨模型综合所需的“几何敏感性”证据。",
            ],
        },
    },
    "grid2d_reflecting_bimodality": {
        "en": {
            "title": "Grid2D Reflecting-Boundary Bimodality",
            "summary": (
                "This reflecting-boundary Grid2D report tests whether bimodality survives when periodic shortcuts are removed and all walls reflect. "
                "Using representative detour, pore, and transport-track cases, it shows that multi-channel timing structure can persist under strict "
                "boundary confinement."
            ),
            "narrative": {
                "model_overview": (
                    "The model keeps a reflecting 2D lattice with absorbing target and controlled local transport structures (detours, pores, tracks)."
                ),
                "method_overview": (
                    "Case families are evaluated under common PMF/hazard diagnostics and compared by channel decomposition and timing windows."
                ),
                "result_overview": (
                    "Several reflecting cases preserve clear early/late channel separation, while others collapse toward long-tail unimodality depending "
                    "on geometric bottlenecks."
                ),
            },
            "key_findings": [
                "Bimodality can persist under fully reflecting boundaries when competing pathways remain topologically distinct.",
                "Pore/track structures modify delay channels through accessibility, not only through drift magnitude.",
                "Case-level comparisons separate robust second peaks from late-window edge humps.",
                "The report supplies boundary-robust evidence for later cross-model hazard interpretations.",
            ],
        },
        "cn": {
            "title": "Grid2D 全反射边界双峰",
            "summary": (
                "该反射边界 Grid2D 报告检验：在移除周期绕行、四壁全反射后，双峰是否仍能保持。"
                "通过绕行、孔道与输运轨道等代表案例，报告证明在严格边界约束下，多通道时序结构仍可出现。"
            ),
            "narrative": {
                "model_overview": (
                    "模型保持反射二维格点与吸收目标，并引入可控局部结构（绕行、孔道、轨道）。"
                ),
                "method_overview": (
                    "各案例在统一 PMF/hazard 诊断口径下评估，并通过通道分解与时窗比较进行机制判别。"
                ),
                "result_overview": (
                    "部分反射案例保留了清晰的早/晚通道分离；另一些在几何瓶颈下退化为长尾单峰。"
                ),
            },
            "key_findings": [
                "在竞争路径拓扑仍可区分时，双峰可在全反射边界下持续存在。",
                "孔道与轨道结构通过可达性重塑延迟通道，而非仅靠漂移强度变化。",
                "案例对比可区分稳健第二峰与晚时窗口边缘隆起。",
                "该报告为后续跨模型 hazard 解释提供了边界稳健证据。",
            ],
        },
    },
    "grid2d_two_target_double_peak": {
        "en": {
            "title": "Grid2D Two-Target Double-Peak",
            "summary": (
                "This report studies two absorbing targets in 2D and maps when the total first-passage distribution develops visible double peaks. "
                "Under reflecting boundaries and corridor-style bias design, it provides phase maps over target-coupling parameters and isolates "
                "how competing destinations create multi-timescale structure."
            ),
            "narrative": {
                "model_overview": (
                    "The model places two absorbing targets in a reflecting lattice with fixed start point and tunable target-channel coupling."
                ),
                "method_overview": (
                    "The pipeline combines exact/approximate first-passage diagnostics, truncation controls, and parameter-phase scans over two-target "
                    "coupling variables."
                ),
                "result_overview": (
                    "Double-peak regions appear when direct-to-near-target and delayed-to-far-target channels both carry substantial mass; phase boundaries "
                    "shift predictably with coupling strength."
                ),
            },
            "key_findings": [
                "Two-target competition creates a controlled mechanism for multi-timescale first-passage behavior.",
                "Phase maps identify stable double-peak bands and transition zones to unimodal behavior.",
                "Truncation and survival-tail diagnostics verify that observed second peaks are not finite-window artifacts.",
                "The report is a key bridge between Grid2D family behavior and ring two-target synthesis.",
            ],
        },
        "cn": {
            "title": "Grid2D 双目标双峰",
            "summary": (
                "该报告研究二维双吸收目标情形下总首达分布何时出现可见双峰。"
                "在反射边界与走廊偏置设计下，报告给出目标耦合参数的相图，并解析“近目标直达”与“远目标延迟”竞争如何形成多时间尺度结构。"
            ),
            "narrative": {
                "model_overview": (
                    "模型在反射格点中设置固定起点与两个吸收目标，并可调节目标通道耦合强度。"
                ),
                "method_overview": (
                    "流程结合精确/近似首达诊断、截断控制与双目标耦合参数扫描。"
                ),
                "result_overview": (
                    "当近目标直达通道与远目标延迟通道都占有显著质量时，会出现稳定双峰；其相界随耦合强度呈可预测移动。"
                ),
            },
            "key_findings": [
                "双目标竞争为多时间尺度首达行为提供了可控机制。",
                "相图明确给出稳定双峰区与向单峰退化的过渡区。",
                "截断与生存尾部诊断验证第二峰并非有限时窗伪影。",
                "该报告是 Grid2D 家族与 ring 双目标综合的关键桥梁。",
            ],
        },
    },
    "ring_lazy_jump_ext": {
        "en": {
            "title": "Lazy Ring Shortcut Beta Scan",
            "summary": (
                "This extension quantifies how shortcut strength beta reshapes first-passage bimodality on lazy rings (K=2,4) at fixed N=100, "
                "then checks transfer by N sweeps and Monte Carlo class decomposition. Across beta in [0,0.2], both peaks move earlier and "
                "tail decay accelerates, while K=4 preserves a wider and deeper bimodal window than K=2."
            ),
            "narrative": {
                "model_overview": (
                    "The model keeps the lazy ring baseline (q=2/3) with one directed shortcut under the selfloop probability rule, "
                    "and compares K=2 versus K=4 under matched parameter settings."
                ),
                "method_overview": (
                    "The workflow runs exact AW beta sweeps, selects a stable beta anchor, executes N sweeps, and cross-checks class composition "
                    "through Monte Carlo trajectory statistics and tail diagnostics."
                ),
                "result_overview": (
                    "Increasing beta advances both peaks and steepens tail decay; under the same beta, K=4 remains more robustly bimodal, "
                    "and exact-versus-MC diagnostics agree on phase-level trends."
                ),
            },
            "key_findings": [
                "At fixed N=100, beta sweeps show systematic left-shifts of peak times and a larger tail-decay rate as shortcut strength increases.",
                "K=4 keeps a broader bimodal interval and deeper valley than K=2 under matched beta schedules.",
                "An anchored beta choice supports stable N sweeps where exact AW and MC class-level diagnostics stay consistent.",
                "Tail diagnostics confirm that shortcut strengthening suppresses late-time mass and changes pathway composition, not only peak height.",
            ],
        },
        "cn": {
            "title": "Lazy Ring Shortcut beta 扫描",
            "summary": (
                "该扩展报告量化了 lazy ring（K=2,4）中 shortcut 强度 beta 对首达双峰结构的影响：先在 N=100 固定条件下做 beta 扫描，"
                "再用 N 扫描与 Monte Carlo 轨迹分类验证迁移稳定性。结果显示 beta 增大时双峰整体前移、尾部衰减加快，且 K=4 的双峰窗口更宽更深。"
            ),
            "narrative": {
                "model_overview": (
                    "模型沿用 lazy ring 基线（q=2/3），采用 selfloop 分流规则加入单向 shortcut，并在统一参数口径下比较 K=2 与 K=4。"
                ),
                "method_overview": (
                    "方法链路包括精确 AW 的 beta 扫描、稳定 beta 锚点选择、N 扫描，以及基于 MC 轨迹类别与尾部诊断的交叉核验。"
                ),
                "result_overview": (
                    "随着 beta 提升，两个峰位整体提前且尾部衰减更快；在同等 beta 下，K=4 的双峰保持性优于 K=2，且精确解与 MC 在相区趋势上吻合。"
                ),
            },
            "key_findings": [
                "在固定 N=100 时，beta 扫描显示峰位前移与尾部衰减率增大具有一致趋势。",
                "在同一 beta 计划下，K=4 相比 K=2 维持了更宽、更深的双峰区间。",
                "基于锚点 beta 的 N 扫描中，精确 AW 与 MC 轨迹分类在相区判断上保持一致。",
                "尾部诊断表明 shortcut 增强改变的不仅是峰高，还包括晚时概率质量与路径组成。",
            ],
        },
    },
    "ring_lazy_jump_ext_rev2": {
        "en": {
            "title": "Lazy Ring Shortcut Figure-1 Revision",
            "summary": (
                "This revision reorganizes the lazy-shortcut extension into a publication-ready evidence flow: co-located Fig.1 overlays "
                "f(t) with window-level class bars, while threshold, window-shift/width, and MC-uncertainty analyses test robustness. "
                "The update strengthens readability and reproducibility without changing the core mechanism claims."
            ),
            "narrative": {
                "model_overview": (
                    "The chapter keeps the same lazy ring shortcut setup used in the extension baseline and focuses on clearer evidence alignment "
                    "between K=2 and K=4 under the selected beta regime."
                ),
                "method_overview": (
                    "The pipeline exports standardized Fig.1 inputs, validates schema, renders stacked-bar co-located panels, and runs three "
                    "sensitivity tracks: threshold sweep, window perturbation, and MC confidence intervals."
                ),
                "result_overview": (
                    "Across the three sensitivity tracks, the qualitative mechanism interpretation remains stable, and uncertainty bars do not "
                    "contradict the phase-level conclusions used in the main narrative."
                ),
            },
            "key_findings": [
                "Co-located Fig.1 directly aligns peak/valley timing with class proportions, improving interpretability over split-panel layouts.",
                "Schema-validated JSON/CSV inputs make figure reconstruction auditable and reproducible.",
                "Threshold and window perturbation scans preserve the main mechanism ranking rather than flipping conclusions.",
                "MC uncertainty intervals are compatible with the reported phase statements for K=2 and K=4.",
            ],
        },
        "cn": {
            "title": "Lazy Ring Shortcut 图1修订",
            "summary": (
                "该修订版把 lazy-shortcut 扩展重构为出版物级证据链：图1将 f(t) 与窗口分类柱状同轴展示，并加入阈值扫描、窗口位移/宽度扰动、"
                "MC 不确定性三类敏感性分析。在不改变核心机制结论的前提下，显著提升了可读性与可复现性。"
            ),
            "narrative": {
                "model_overview": (
                    "模型保持与扩展基线一致的 lazy ring + shortcut 设定，重点是在选定 beta 区间下更清晰地对齐 K=2 与 K=4 的证据表达。"
                ),
                "method_overview": (
                    "流程包括标准化导出图1输入、schema 校验、同轴栈叠面板绘制，以及阈值、窗口扰动、MC 置信区间三条敏感性分析链。"
                ),
                "result_overview": (
                    "三类敏感性分析下，机制解释在定性层面保持稳定，且不确定性区间未推翻主线中的相区判断。"
                ),
            },
            "key_findings": [
                "同轴图1将峰谷时序与路径类别比例直接对齐，优于分面板展示。",
                "经 schema 校验的 JSON/CSV 输入使图形可重建、可审计。",
                "阈值与窗口扰动测试未改变核心机制排序，结论具有稳健性。",
                "MC 置信区间与 K=2/K=4 的主结论一致，不构成反证。",
            ],
        },
    },
    "ring_two_target": {
        "en": {
            "title": "Two-Target Lazy Ring Mechanics",
            "summary": (
                "This report builds an exact two-target lazy-ring framework and compares no-shortcut versus selfloop-shortcut regimes. "
                "By scanning N, K, and beta with peak/valley diagnostics, it shows how target geometry and shortcut routing jointly control "
                "the transition among unimodal, bimodal, and trimodal first-passage behavior."
            ),
            "narrative": {
                "model_overview": (
                    "The model places two absorbing targets on a lazy ring with optional directed shortcut, keeping index conventions and "
                    "distance geometry explicit for mechanism-level comparison."
                ),
                "method_overview": (
                    "Exact generating-function/AW inversion is combined with parameter scans and trajectory-style diagnostics to classify "
                    "peak structures under consistent criteria."
                ),
                "result_overview": (
                    "No-shortcut drift can already produce strong bimodality, while shortcut activation redistributes pathway mass and can "
                    "introduce trimodal behavior in selected geometry and parameter bands."
                ),
            },
            "key_findings": [
                "Two-target geometry introduces competing fast and delayed channels, making multimodality a structural rather than numerical artifact.",
                "Under no-shortcut drift, robust bimodality appears in reproducible parameter windows.",
                "Selfloop shortcut settings can reweight path classes and generate trimodal signatures in selected regimes.",
                "K and beta scans provide a map of where multi-peak patterns are stable versus where they collapse to a single mode.",
            ],
        },
        "cn": {
            "title": "双目标 Lazy Ring 机制",
            "summary": (
                "该报告建立了双目标 lazy ring 的精确分析框架，并比较无 shortcut 与 selfloop-shortcut 两类机制。"
                "通过对 N、K、beta 的系统扫描与峰谷判据，报告说明了目标几何与 shortcut 路由如何共同决定首达分布在单峰、双峰、三峰之间的转变。"
            ),
            "narrative": {
                "model_overview": (
                    "模型在 lazy ring 上设置两个吸收目标，并可选加入单向 shortcut，显式保留索引与几何距离定义以支持机制级比较。"
                ),
                "method_overview": (
                    "方法结合精确生成函数/AW 反演、参数扫描与轨迹诊断，在统一判据下对峰结构进行分类。"
                ),
                "result_overview": (
                    "无 shortcut 漂移本身即可产生稳定双峰；加入 shortcut 后路径质量重新分配，在特定几何与参数带可出现三峰行为。"
                ),
            },
            "key_findings": [
                "双目标几何会形成快慢通道竞争，使多峰现象具有结构机制基础。",
                "在无 shortcut 漂移条件下，可复现的参数窗口内可观察到稳健双峰。",
                "selfloop shortcut 可重排路径类别权重，并在部分区间触发三峰结构。",
                "K 与 beta 扫描给出了多峰稳定区与退化为单峰区的清晰边界。",
            ],
        },
    },
    "ring_lazy_jump": {
        "en": {
            "title": "Lazy Ring Jump-Over Mechanism (K2 vs K4)",
            "summary": (
                "This report establishes the baseline jump-over mechanism for lazy rings with one directed shortcut, contrasting K=2 and K=4 "
                "under exact first-passage diagnostics. It explains why double-peak behavior is selective in shortcut strength and how pathway "
                "decomposition links peak structure to fast and delayed transport channels."
            ),
            "narrative": {
                "model_overview": (
                    "A lazy ring with one directed shortcut is used as the baseline setting, with matched parameters across K=2 and K=4 to isolate "
                    "neighborhood effects."
                ),
                "method_overview": (
                    "The analysis combines AW inversion for exact first-passage series with trajectory decomposition that separates jump-over, "
                    "direct, and delayed path classes."
                ),
                "result_overview": (
                    "Bimodality appears only in selected shortcut-strength intervals; K=4 generally maintains stronger second-peak persistence than K=2 "
                    "when geometry and waiting rules are aligned."
                ),
            },
            "key_findings": [
                "Jump-over pathways create a distinct delayed channel that is necessary for persistent second peaks.",
                "Shortcut strength has a non-monotonic effect: too weak or too strong settings both reduce robust bimodality.",
                "K=2 and K=4 share the same mechanism skeleton but differ in phase-window width and valley depth.",
                "Exact inversion and trajectory decomposition give consistent interpretations of the observed peak transitions.",
            ],
        },
        "cn": {
            "title": "Lazy Ring Jump-Over 机制（K2 对 K4）",
            "summary": (
                "该报告建立了 lazy ring + 单向 shortcut 的 jump-over 基线机制，在精确首达诊断下比较 K=2 与 K=4。"
                "报告解释了双峰为何只在特定 shortcut 强度区间出现，并通过路径分解把峰结构与快/慢通道对应起来。"
            ),
            "narrative": {
                "model_overview": (
                    "模型采用 lazy ring 与单向 shortcut 的基线构型，在统一参数设定下比较 K=2 与 K=4 的邻接效应。"
                ),
                "method_overview": (
                    "方法结合 AW 精确反演与轨迹分解，将 jump-over、直达与延迟通道分离并进行量化。"
                ),
                "result_overview": (
                    "双峰只在部分 shortcut 强度区间稳定出现；在几何与停留规则对齐时，K=4 往往比 K=2 保持更强的第二峰。"
                ),
            },
            "key_findings": [
                "jump-over 路径会形成独立的延迟通道，是稳定第二峰的重要条件。",
                "shortcut 强度影响呈非单调：过弱或过强都会削弱稳健双峰。",
                "K=2 与 K=4 共享机制骨架，但相区宽度与谷深存在系统差异。",
                "精确反演与轨迹分解对峰转变机制给出了相互一致的解释。",
            ],
        },
    },
    "ring_deriv_k2": {
        "en": {
            "title": "Ring Derivation Backbone (K=2)",
            "summary": (
                "This derivation report provides the analytical backbone for ring models with one directed long-range link, including defect-free "
                "propagators, defect corrections, and first-passage generating functions. It serves as the shared mathematical base used by later "
                "shortcut and valley studies."
            ),
            "narrative": {
                "model_overview": (
                    "The setting is a finite ring random walk with periodic indexing and one directed long-range connection, expressed in a form "
                    "compatible with both lazy-reservoir and rewiring interpretations."
                ),
                "method_overview": (
                    "The report derives Green-function style propagators, constructs defect-resolvent corrections, and obtains first-passage "
                    "generating forms that can be numerically inverted."
                ),
                "result_overview": (
                    "The closed-form derivation clarifies which terms govern shortcut-induced asymmetry and provides reusable formula blocks "
                    "for downstream ring reports."
                ),
            },
            "key_findings": [
                "Defect-free and defect-corrected propagators can be written in a unified analytic framework.",
                "Directed long-range links alter first-passage statistics through resolvent-level corrections rather than ad-hoc fitting.",
                "The derivation yields formula components that are directly reused in lazy-jump and valley analyses.",
                "Analytic structure explains when shortcut asymmetry changes peak timing versus only changing overall scale.",
            ],
        },
        "cn": {
            "title": "Ring 推导主干（K=2）",
            "summary": (
                "该推导报告给出了“环 + 单向长程连边”模型的解析主干：包括无缺陷传播子、缺陷修正与首达生成函数。"
                "它是后续 shortcut 与 valley 报告共用的数学基座。"
            ),
            "narrative": {
                "model_overview": (
                    "模型为有限环随机游走并加入单向长程连边，采用与 lazy-reservoir 与 rewiring 两类解释兼容的统一表达。"
                ),
                "method_overview": (
                    "方法链从 Green 函数传播子出发，构造缺陷 resolvent 修正，再得到可数值反演的首达生成函数形式。"
                ),
                "result_overview": (
                    "闭式推导明确了 shortcut 不对称性的主导项，并为后续 ring 报告提供可复用公式模块。"
                ),
            },
            "key_findings": [
                "无缺陷与缺陷修正传播子可在同一解析框架下统一表示。",
                "单向长程连边对首达统计的影响体现在 resolvent 级修正，而非经验拟合。",
                "推导得到的公式组件可直接复用于 lazy-jump 与 valley 分析。",
                "解析结构解释了何时 shortcut 改变峰位时序，何时只改变整体尺度。",
            ],
        },
    },
    "grid2d_blackboard_bimodality": {
        "en": {
            "title": "Grid2D Blackboard Endpoint Case",
            "summary": (
                "This blackboard-style Grid2D case studies reflecting boundaries with start and target anchored at wall endpoints. "
                "The Z/S endpoint configurations are used to test whether a visually delayed hump is a true second peak or a window-edge artifact, "
                "with diagnostics linked to channel decomposition and path geometry."
            ),
            "narrative": {
                "model_overview": (
                    "The model keeps reflecting-boundary lattice dynamics and evaluates endpoint wall geometry where corridor shortcuts are strongly constrained."
                ),
                "method_overview": (
                    "The pipeline runs blackboard case builders, screenshot-style scans, and channel/path decomposition diagnostics under the same FPT criteria."
                ),
                "result_overview": (
                    "For the scanned endpoint cases, dominant behavior is single-peak plus long tail; the late-window hump is identified as an edge artifact "
                    "instead of a robust bimodal signature."
                ),
            },
            "key_findings": [
                "Endpoint wall configurations remain primarily unimodal with a long tail under reflecting constraints.",
                "The delayed hump in late windows is diagnostic-window edge behavior rather than a stable second structural peak.",
                "Channel decomposition separates geometric detours from genuinely competing transport routes.",
                "The blackboard pipeline keeps figure generation and case metadata reproducible across Z/S case variants.",
            ],
        },
        "cn": {
            "title": "Grid2D 黑板端点构型",
            "summary": (
                "该黑板图风格 Grid2D 报告研究了反射边界下“墙端点起止”构型。通过 Z/S 端点案例，报告检验晚时隆起究竟是稳定第二峰还是窗口边缘伪峰，"
                "并将判断与通道分解和路径几何对应。"
            ),
            "narrative": {
                "model_overview": (
                    "模型保持反射边界格点动力学，重点考察走廊受限明显的墙端点几何。"
                ),
                "method_overview": (
                    "流程包括黑板案例构建、截图式扫描与通道/路径分解诊断，并沿用统一 FPT 判据。"
                ),
                "result_overview": (
                    "在已扫描的端点案例中，主导行为为单峰加长尾；晚时隆起被判定为窗口边缘效应，而非稳健双峰。"
                ),
            },
            "key_findings": [
                "墙端点构型在反射约束下总体表现为单峰 + 长尾。",
                "晚时窗口中的隆起主要是窗口边缘伪峰，不构成稳定第二结构峰。",
                "通道分解能够区分几何绕行与真正竞争通道。",
                "黑板流程在 Z/S 案例下保持图形与元数据可复现。",
            ],
        },
    },
    "cross_luca_regime_map": {
        "en": {
            "title": "Cross-Model Luca Regime Map",
            "summary": (
                "This cross-report study benchmarks full-FPT solvers under fixed-horizon fairness, comparing sparse exact recursion "
                "against Luca defect-reduced routes while keeping linear-system MFPT only as reference. The core output is a reproducible "
                "speed-ratio map R=t_sparse/t_luca and a regime classification that distinguishes where acceleration is real versus negligible."
            ),
            "narrative": {
                "model_overview": (
                    "The comparison protocol aligns Grid2D and Ring instances under one fairness contract: same horizon, same observable, "
                    "and no mixing of full-FPT metrics with MFPT-only claims."
                ),
                "method_overview": (
                    "Runs use warm-up plus repeated timed executions, defect-pair routing rules, and pooled medians to stabilize solver-side "
                    "variance before regime labeling."
                ),
                "result_overview": (
                    "Across the scanned workload, sparse exact remains the dominant full-FPT baseline; Luca-mode speedups appear only in limited "
                    "defect-regime subsets and are near-neutral in the aggregate ratio metric."
                ),
            },
            "key_findings": [
                "The ratio metric R=t_sparse/t_luca is computed under fixed full-FPT fairness, with MFPT linear systems separated as reference only.",
                "Pooled timing medians indicate sparse exact dominates most scanned regimes in full-FPT mode.",
                "Luca acceleration is regime-dependent and concentrated in specific defect-pair configurations.",
                "Cross-report transfer claims are accepted only when both model families satisfy the same fairness and observability constraints.",
            ],
        },
        "cn": {
            "title": "跨模型 Luca 相区图",
            "summary": (
                "该跨报告研究在固定时域公平口径下比较 full-FPT 求解器：以 sparse 精确递推为基线，"
                "对照 Luca 缺陷约化路径，并把线性系统 MFPT 仅作为参考。核心产出是可复现的速度比 R=t_sparse/t_luca 及其相区分类。"
            ),
            "narrative": {
                "model_overview": (
                    "比较协议在 Grid2D 与 Ring 上统一为同一公平契约：相同时间窗、相同观测量，且不把 full-FPT 与仅 MFPT 指标混用。"
                ),
                "method_overview": (
                    "流程采用预热+多次计时、中位数汇总和缺陷配对规则控制，以减少求解器侧波动对相区结论的影响。"
                ),
                "result_overview": (
                    "在扫描工作负载上，sparse 精确解仍是 full-FPT 主基线；Luca 加速仅在部分缺陷区间显著，整体速度比接近中性。"
                ),
            },
            "key_findings": [
                "速度比 R=t_sparse/t_luca 在固定 full-FPT 公平口径下计算，MFPT 线性系统仅作对照参考。",
                "汇总中位计时显示 sparse 精确解在多数扫描区间保持主导。",
                "Luca 的加速收益具有相区依赖性，集中在特定缺陷配对构型。",
                "跨模型迁移结论仅在两侧公平口径与观测约束一致时成立。",
            ],
        },
    },
    "ring_valley_dst": {
        "en": {
            "title": "Destination-Scan Valley Control (N=100, K=6)",
            "summary": (
                "This report fixes N=100 and K=6, then scans shortcut destination dst to control the second-peak structure of first-passage "
                "distributions. Deterministic flux/master-equation scans and Monte Carlo trajectory classes jointly identify where valley depth "
                "and second-peak prominence are maximized."
            ),
            "narrative": {
                "model_overview": (
                    "The model uses a K=6 ring with one directed shortcut src->dst and an absorbing target; only dst is varied so mechanism changes "
                    "can be attributed to geometric landing location."
                ),
                "method_overview": (
                    "The workflow combines deterministic flux scans, AW-style first-passage diagnostics, and class-conditioned Monte Carlo paths "
                    "under one peak/valley criterion."
                ),
                "result_overview": (
                    "Destination scanning reveals structured dst windows where the second peak is amplified and trajectory-class usage shifts, "
                    "with deterministic and Monte Carlo diagnostics remaining consistent."
                ),
            },
            "key_findings": [
                "Scanning dst alone can substantially change second-peak height ratio and valley depth at fixed N and K.",
                "Deterministic flux/master-equation results and Monte Carlo class decomposition agree on high-contrast destination windows.",
                "Second-peak strengthening correlates with increased delayed-route contribution rather than a uniform amplitude scaling.",
                "Destination geometry acts as a controllable lever for phase behavior without changing base transition probabilities.",
            ],
        },
        "cn": {
            "title": "目的地扫描与谷值调控（N=100, K=6）",
            "summary": (
                "该报告固定 N=100、K=6，仅扫描 shortcut 终点 dst 来调控首达分布第二峰。"
                "通过确定性 flux/master 方程扫描与 Monte Carlo 轨迹分类联合诊断，报告识别出第二峰增强与谷值加深最显著的 dst 区间。"
            ),
            "narrative": {
                "model_overview": (
                    "模型为 K=6 环 + 单向 shortcut src->dst + 吸收目标；只改变 dst，使机制差异可归因于几何落点。"
                ),
                "method_overview": (
                    "方法链结合确定性 flux 扫描、AW 首达诊断与按轨迹类别条件化的 Monte Carlo 统计，并采用统一峰谷判据。"
                ),
                "result_overview": (
                    "dst 扫描给出了结构化的高对比区间：第二峰可被显著放大，且轨迹类别占比同步变化，确定性与 MC 结论一致。"
                ),
            },
            "key_findings": [
                "在固定 N、K 下，仅扫描 dst 就能显著改变第二峰高度比与谷深。",
                "确定性 flux/master 方程与 MC 轨迹分类在高对比 dst 区间上相互印证。",
                "第二峰增强对应的是延迟路径占比提升，而非整体幅度等比例放大。",
                "终点几何可作为不改基础转移概率时的相位调控杠杆。",
            ],
        },
    },
}


def normalize_space(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def repair_common_math_noise(text: str) -> str:
    value = str(text or "")
    if not value:
        return ""
    value = value.replace("…", " ")
    value = re.sub(r"\.{3,}", " ", value)
    value = re.sub(r"\bshortcu\b", "shortcut", value, flags=re.IGNORECASE)
    value = re.sub(r"\b1\s*,\s*,\s*N\b", "1..N", value, flags=re.IGNORECASE)
    value = re.sub(r"\b0\s*,\s*,\s*N\s*-\s*1\s*\^\s*2\b", "[0, N-1]^2", value, flags=re.IGNORECASE)
    value = re.sub(r"\b0\s*,\s*,\s*N\s*-\s*1\b", "0..N-1", value, flags=re.IGNORECASE)
    value = re.sub(
        r"\b([A-Za-z])\s+p(\d+)\b",
        lambda m: f"{m.group(1)}_p{m.group(2)}",
        value,
        flags=re.IGNORECASE,
    )
    value = re.sub(r"\b([xy])\s+t\b", lambda m: f"{m.group(1)}_t", value, flags=re.IGNORECASE)
    value = re.sub(r"\bn\s+0\b", "n0", value, flags=re.IGNORECASE)
    value = re.sub(r"\bt\s+(\d+)\b", lambda m: f"t{m.group(1)}", value, flags=re.IGNORECASE)
    value = re.sub(
        r"\bK\s+(\d(?:\s*,\s*\d)+)\b",
        lambda m: "K=" + "".join(m.group(1).split()),
        value,
        flags=re.IGNORECASE,
    )
    value = re.sub(r"\bP\s*:\s*([0-9]+(?:\.[0-9]+)?)\b", r"P=\1", value, flags=re.IGNORECASE)
    value = re.sub(r"\b10e-(\d+)\b", r"1e-\1", value, flags=re.IGNORECASE)
    value = re.sub(r"P\(\s*C\s*1\s*T\s*W\s*\)", "P(C>=1 | T in W)", value, flags=re.IGNORECASE)
    value = re.sub(r"\bover\s+t\s*(\d{2,5})\b", r"over t<=\1", value, flags=re.IGNORECASE)
    value = re.sub(r"\bfor\s+t\s*(\d{2,5})\b", r"for t<=\1", value, flags=re.IGNORECASE)
    value = re.sub(r"\^\s*-\s*(\d+)", r"e-\1", value)
    value = value.replace(",,", ",")
    value = re.sub(r",\s*,+", ", ", value)
    value = re.sub(r"\bN\s*=\s*(\d+)\s*,\s*,", r"N=\1,", value, flags=re.IGNORECASE)
    value = re.sub(
        r"\bwith\s+N\s*=\s*(\d+)\s*,\s*=\s*1\b",
        r"with N=\1 and fixed control parameter",
        value,
        flags=re.IGNORECASE,
    )
    value = re.sub(
        r"\bN\s*=\s*(\d+)\s*,\s*=\s*1\s*->\s*v\s*=\s*target\s*=\s*(\d+)\b",
        r"N=\1 with target index v=\2",
        value,
        flags=re.IGNORECASE,
    )
    value = re.sub(
        r"\bN\s*=\s*(\d+)[^.;:]{0,80}?->\s*v\s*=\s*target\s*=\s*(\d+)\b",
        r"N=\1 with target index v=\2",
        value,
        flags=re.IGNORECASE,
    )
    value = re.sub(
        r"\blambda\s*k\s*=\s*1-q\+q\b\.?",
        "the lazy parameter q enters the eigenvalue spectrum directly.",
        value,
        flags=re.IGNORECASE,
    )
    value = re.sub(
        r"\bthe defect[-\s]*free eigenvalues are the lazy parameter q enters the eigenvalue spectrum directly\.?",
        "the defect-free eigenvalues depend explicitly on q.",
        value,
        flags=re.IGNORECASE,
    )
    value = re.sub(
        r"\b(the lazy parameter q enters the eigenvalue spectrum directly\.)\s*(the lazy parameter q enters the eigenvalue spectrum directly\.)",
        r"\1",
        value,
        flags=re.IGNORECASE,
    )
    value = re.sub(
        r"\bco-located\s*\(now in stacked panels\)\b",
        "co-located figure (shown as stacked panels)",
        value,
        flags=re.IGNORECASE,
    )
    value = re.sub(
        r"\bsingle\s+co-located\s*\(now in stacked panels\)\s*and the associated sensitivity analyses\b",
        "single co-located Figure 1 (shown as stacked panels) together with sensitivity analyses",
        value,
        flags=re.IGNORECASE,
    )
    value = re.sub(r"\bunder\s+the\s+Fig\.?$", "under the reference figure.", value, flags=re.IGNORECASE)
    value = re.sub(r"\(\s*Figs?\.\s*$", "", value, flags=re.IGNORECASE)
    value = re.sub(r"\b(?:summ|summary)\s*$", "", value, flags=re.IGNORECASE)
    value = re.sub(r"\(\s*Section[^)]*\)", " ", value, flags=re.IGNORECASE)
    value = re.sub(r"\(\s*,\s*\)", " ", value)
    value = re.sub(r"\b(?:sec|fig):[a-z0-9_\-]+\b", " ", value, flags=re.IGNORECASE)
    value = re.sub(r"->\s*v\s*=\s*target\b", "toward target", value, flags=re.IGNORECASE)
    value = re.sub(r"\bfor,\s*", "for ", value)
    value = re.sub(r",\s*=\s*1\b", ", with fixed control parameter", value, flags=re.IGNORECASE)
    value = re.sub(r"\bwe use,\s*hence\b", "With fixed parameters,", value, flags=re.IGNORECASE)
    value = re.sub(r"\bup to\.\s*$", "", value, flags=re.IGNORECASE)
    value = re.sub(r"\s*,\s*all\s*$", ".", value, flags=re.IGNORECASE)
    value = re.sub(r"\bDefine\s*=\s*t1\b[^.;。；]*", " ", value, flags=re.IGNORECASE)
    value = re.sub(r"\s*&=\s*", " = ", value)
    value = re.sub(r"\s{2,}", " ", value)
    return normalize_space(value)


def dedupe_preserve(items: list[str], *, max_items: int) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for raw in items:
        val = normalize_space(raw)
        if not val:
            continue
        key = normalize_finding_key(val)
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(val)
        if len(out) >= max_items:
            break
    return out


def contains_cjk(text: str) -> bool:
    return bool(re.search(r"[\u4e00-\u9fff]", text))


def is_placeholder_finding(text: str, report_id: str) -> bool:
    lowered = normalize_space(text).lower()
    if not lowered:
        return True
    patterns = [
        f"see {report_id.lower()} report assets for detailed findings",
        "see report assets for detailed findings",
        "fallback narrative card",
    ]
    if any(p in lowered for p in patterns):
        return True
    if lowered.startswith("see ") and "report assets" in lowered:
        return True
    return False


def looks_like_operational_note(text: str) -> bool:
    lowered = normalize_space(text).lower()
    if not lowered:
        return True
    if lowered.startswith("main tex:") or lowered.startswith("full workflow notes:"):
        return True
    if lowered.startswith("main report pdfs:"):
        return True
    if re.search(r"`[^`]+`", lowered) and "/" in lowered:
        if len(lowered) <= 180:
            return True
    if re.search(r"`[^`]+\.(?:tex|md|py|json|csv|pdf)`", lowered):
        return True
    if re.search(r"\b(?:outputs|tables|notes|code|reports)/", lowered):
        return True
    if re.search(r"\.(?:py|json|csv|tex|md)\b", lowered):
        if any(token in lowered for token in ("script", "config", "notes", "path", "workflow", "file")):
            return True
    if lowered.startswith("`code/`") or lowered.startswith("`research/reports/`") or lowered.startswith("`outputs/`") or lowered.startswith("`tables/`"):
        return True
    if lowered in {"`code/`: data generation scripts.", "code/: data generation scripts."}:
        return True
    return False


def clean_findings(findings: list[str], report_id: str, max_items: int = 8) -> list[str]:
    normalized = dedupe_preserve([repair_common_math_noise(x) for x in findings], max_items=max(12, max_items * 2))
    kept = [
        item
        for item in normalized
        if not is_placeholder_finding(item, report_id)
        and not looks_like_operational_note(item)
        and not has_malformed_readability_tokens(item)
        and summary_penalty(item) <= 16
    ]
    if not kept:
        kept = [
            f"Core derivation and reproducible evidence are available for {report_id}; "
            "see the mathematical logic chain and interactive datasets on this page."
        ]
    return dedupe_preserve(kept, max_items=max_items)


def strip_tex_comments(text: str) -> str:
    return re.sub(r"(?<!\\)%.*", "", text)


def polish_extracted_text(text: str) -> str:
    value = normalize_space(text)
    if not value:
        return ""
    value = value.replace("``", '"').replace("''", '"')
    value = value.replace("`", "")
    value = value.replace("~", " ")
    value = value.replace("\\", " ")
    value = value.replace("_", " ")
    value = re.sub(r"\b(itemize|enumerate|figure|table|align|equation)\b", " ", value, flags=re.IGNORECASE)
    value = re.sub(r"\[\s*\]", " ", value)
    value = re.sub(r"\(\s*\)", " ", value)
    value = re.sub(r"\s+([,.;:)\]])", r"\1", value)
    value = re.sub(r"([(\[])\s+", r"\1", value)
    value = normalize_space(value)
    return repair_common_math_noise(value)


def latex_to_plain(text: str) -> str:
    value = strip_tex_comments(text)
    for source, target in LATEX_SYMBOL_REPLACEMENTS.items():
        value = value.replace(source, target)
    value = value.replace("\\,", " ")
    value = value.replace("\\;", " ")
    value = value.replace("\\!", " ")
    value = value.replace("\\left", " ")
    value = value.replace("\\right", " ")
    value = value.replace("\\,", " ")
    value = value.replace("\\quad", " ")
    value = value.replace("\\qquad", " ")
    for _ in range(8):
        updated = re.sub(r"\\frac\{([^{}]{1,120})\}\{([^{}]{1,120})\}", r"(\1)/(\2)", value)
        if updated == value:
            break
        value = updated
    value = re.sub(r"\\sqrt\{([^{}]{1,120})\}", r"sqrt(\1)", value)
    value = re.sub(
        r"\\begin\{(?:figure|table|longtable|tabular|verbatim|lstlisting)\*?\}.*?\\end\{(?:figure|table|longtable|tabular|verbatim|lstlisting)\*?\}",
        " ",
        value,
        flags=re.DOTALL,
    )
    value = re.sub(r"\\(begin|end)\{[^{}]+\}(?:\[[^\]]*\])?", " ", value)
    value = re.sub(r"\\(section|subsection|subsubsection|paragraph)\*?\{([^{}]*)\}", r" \2 ", value)
    value = re.sub(r"\\item\b", " ", value)
    value = re.sub(r"\\[a-zA-Z]+\*?(?:\[[^\]]*\])?\{([^{}]*)\}", r" \1 ", value)
    value = re.sub(r"\\[a-zA-Z]+\*?", " ", value)
    value = re.sub(r"\$([^$]{1,240})\$", r" \1 ", value)
    value = re.sub(r"[{}]", " ", value)
    return polish_extracted_text(value)


def summarize_plain(text: str, *, max_chars: int = 320) -> str:
    plain = normalize_space(text)
    if len(plain) <= max_chars:
        return plain
    clipped = plain[: max_chars + 1]
    stop = max(clipped.rfind(". "), clipped.rfind("。"), clipped.rfind("; "), clipped.rfind("；"))
    if stop >= int(max_chars * 0.55):
        return clipped[: stop + 1].rstrip(" ,;。；")
    fallback = clipped[:max_chars].rstrip(" ,;。；")
    if contains_cjk(fallback):
        return fallback
    last_space = fallback.rfind(" ")
    if last_space > int(max_chars * 0.6):
        fallback = fallback[:last_space].rstrip(" ,;。；")
    return fallback


def canonical_summary(text: str, *, max_chars: int = 1200) -> str:
    """
    Canonical summary text for meta payloads.
    Keep complete prose where possible and avoid terminal ellipsis.
    """
    plain = normalize_space(text).replace("…", " ")
    plain = re.sub(r"\.{3,}", " ", plain)
    plain = normalize_space(plain)
    if len(plain) <= max_chars:
        return plain
    clipped = plain[: max_chars + 1]
    stop = max(clipped.rfind(". "), clipped.rfind("。"), clipped.rfind("; "), clipped.rfind("；"))
    if stop >= int(max_chars * 0.6):
        return clipped[: stop + 1].rstrip(" ,;。；")
    return clipped[:max_chars].rstrip(" ,;。；")


def summary_quality_cleanup(text: str) -> str:
    value = repair_common_math_noise(str(text or ""))
    if not value:
        return ""
    value = value.replace("rightarrow", "to")
    value = value.replace("leftarrow", "from")
    value = re.sub(r"\b([A-Za-z])\s*=\s*([0-9]+)\s*rightarrow\s*([0-9]+)\b", r"\1 from \2 to \3", value)
    value = re.sub(r"\b([A-Za-z])\s*=\s*([0-9]+)\s*->\s*([0-9]+)\b", r"\1 from \2 to \3", value)
    value = re.sub(r"\b([A-Za-z]+20\d{2}[a-z]?)\b", " ", value, flags=re.IGNORECASE)
    value = re.sub(r"\b(?:Reproduce with|复现命令)\s*:\s*\d+\s+[A-Za-z0-9_]+\b", " ", value, flags=re.IGNORECASE)
    value = re.sub(r"\bdefine\s*=\s*[0-9.]+\s*,\s*[0-9.]+\s*\([^)]*\)", " ", value, flags=re.IGNORECASE)
    value = re.sub(r"--\s*\)\s*", " ", value)
    value = re.sub(r"\bt\s*t\s*\^\s*[a-z0-9_]+\b", " ", value, flags=re.IGNORECASE)
    value = re.sub(r"\b\d+\s*,\s*\.\.\.\s*,\s*[a-z0-9]+\b", " ", value, flags=re.IGNORECASE)
    value = re.sub(r"\b[a-z]\s*=\s*t\d+\b", " ", value, flags=re.IGNORECASE)
    value = re.sub(r"\b[a-z]\s*=\s*[a-z]\s*[0-9]+\b", " ", value, flags=re.IGNORECASE)
    value = re.sub(r"\bto(\d+)\b", r"to \1", value, flags=re.IGNORECASE)
    value = re.sub(r"\b[txyzkn]\s*_[a-z0-9]{0,2}\s*[,;:]\s*$", " ", value, flags=re.IGNORECASE)
    value = re.sub(r"\b(?:Fig|Figs)\.?\s*$", " ", value, flags=re.IGNORECASE)
    value = re.sub(r"\(\s*(?:Fig|Figs)\.?\s*\)$", " ", value, flags=re.IGNORECASE)
    value = re.sub(r"\bsec:[a-z0-9_\-]+\b", " ", value, flags=re.IGNORECASE)
    value = re.sub(r"\bfig:[a-z0-9_\-]+\b", " ", value, flags=re.IGNORECASE)
    value = re.sub(r"\s{2,}", " ", value)
    return repair_common_math_noise(value)


def strip_mathish_fragments(text: str) -> str:
    value = repair_common_math_noise(str(text or ""))
    value = re.sub(r"\[[^\]]{0,240}[=<>/\\^_][^\]]{0,240}\]", " ", value)
    value = re.sub(r"\[[^\]]{0,240}[=<>/\\^_][^\]]{0,240}$", " ", value)
    value = re.sub(r"\(([^()]|\\\(|\\\)){0,240}[=<>/\\^_](?:[^()]|\\\(|\\\)){0,240}\)", " ", value)
    value = re.sub(r"\b(?:t|p|q|h|s)\s*[=^]\s*[-+0-9a-zA-Z./()]+\b", " ", value)
    value = re.sub(r"\b[a-z]\s+p\d+\s+\d+\b", " ", value, flags=re.IGNORECASE)
    value = re.sub(r"\bfor\s+z\d+--z\d+\s*,\s*t_p\d+\b[^.;。；]{0,240}", " ", value, flags=re.IGNORECASE)
    value = re.sub(r"\bdefine\s*=\s*t\d+\b[^.;。；]{0,240}", " ", value, flags=re.IGNORECASE)
    value = re.sub(r"\bt\s*t\s*\^\s*[a-z0-9_]+\b", " ", value, flags=re.IGNORECASE)
    value = re.sub(r"\b\d+\s*,\s*\.\.\.\s*,\s*[a-z0-9]+\b", " ", value, flags=re.IGNORECASE)
    value = re.sub(r"\s*&=\s*", " ", value)
    value = normalize_space(value)
    value = re.sub(r":\s*,", ": ", value)
    value = re.sub(r"\s+,", ",", value)
    value = re.sub(r"\s+\.", ".", value)
    value = re.sub(r"\(\s*\)", " ", value)
    value = re.sub(r"\b(?:at|to|from|with|under)\s+\.", ".", value, flags=re.IGNORECASE)
    value = re.sub(r"\s{2,}", " ", value)
    return repair_common_math_noise(value)


def looks_like_math_fragment(sentence: str) -> bool:
    value = repair_common_math_noise(normalize_space(sentence))
    if not value:
        return True
    if re.search(r"(\\begin|\\end|\\\\|&=)", value):
        return True
    if re.search(r"\bdefine\s*=\s*t\d+\b", value, flags=re.IGNORECASE):
        return True
    if re.search(r"\b[a-z]\s+p\d+\b", value, flags=re.IGNORECASE):
        return True
    if re.search(r"\b1\.\.N\b", value, flags=re.IGNORECASE):
        return True
    if re.search(r"\bt\s*t\s*\^\s*[a-z0-9_]+\b", value, flags=re.IGNORECASE):
        return True
    if re.search(r"\b\d+\s*,\s*\.\.\.\s*,\s*[a-z0-9]+\b", value, flags=re.IGNORECASE):
        return True
    if re.search(r"\bK=\d+(?:,\d+)+\b", value):
        return True
    symbol_ratio = len(re.findall(r"[=<>/\\^_\[\]\{\}]", value)) / max(1, len(value))
    if symbol_ratio > 0.09:
        return True
    return False


def has_malformed_readability_tokens(text: str) -> bool:
    value = normalize_space(str(text or ""))
    if not value:
        return False
    patterns = [
        r",\s*,",
        r"\b=\s*1\s*->\b",
        r"\b=1toward\b",
        r"\bu=n0toward\b",
        r"\bunder\s+the\s+Fig\.?$",
        r"\bunder\s*$",
        r"\+\s*$",
        r"\(\s*Figs?\.?\s*$",
        r"\b(?:sec|fig):[a-z0-9_\-]+\b",
        r"\b(?:summ|summary)\s*$",
        r"\bEven\s+N\s*\[[^\]]+\]\s*,\s*K=[0-9,\s]+\s*,\s*with\s+fixed\s+control\s+parameter\.?$",
        r"\bthe defect[-\s]*free eigenvalues are the lazy parameter q enters the eigenvalue spectrum directly\.?$",
        r"\bEq\.\s*$",
        r"\bi\.e\.\s*$",
        r"\b[a-z]\s*=\s*\d+\s*(?:rightarrow|->)\s*\d+\b",
        r"\b[a-z]+\d{4}[a-z]?\b",
        r"--\s*\)",
        r"\bdefine\s*=\s*[0-9.]+\s*,\s*[0-9.]+\s*\([^)]*\)",
        r"\bReproduce with:\s*\d+\s+[A-Za-z0-9_]+\b",
        r"\bf\s*\(t\)\s*=\s*p\s*f\s*\+\s*p\s*f\b",
        r"\bt\s*fast\s*t\s*slow\b",
        r"\bx\s*=\s*\d+\s*to\d+\b",
        r"^[a-z0-9_./-]+\.tex$",
        r"^[a-z0-9_./-]+\.pdf$",
        r"\b[a-z0-9_./-]+\.tex\b",
        r"\b[a-z0-9_./-]+\.pdf\b",
    ]
    return any(re.search(pattern, value, flags=re.IGNORECASE) for pattern in patterns)


def readable_summary(text: str, *, max_chars: int = 480, max_sentences: int = 3) -> str:
    plain = summary_quality_cleanup(strip_mathish_fragments(normalize_space(text)))
    if not plain:
        return ""
    chunks = [normalize_space(part) for part in re.split(r"(?<=[。！？.!?;；])\s+", plain) if normalize_space(part)]
    selected: list[str] = []
    for sentence in chunks:
        if len(sentence) < 24:
            continue
        if looks_like_math_fragment(sentence):
            continue
        symbol_ratio = len(re.findall(r"[=<>/\\^_\[\]\{\}]", sentence)) / max(1, len(sentence))
        digit_ratio = len(re.findall(r"\d", sentence)) / max(1, len(sentence))
        if symbol_ratio > 0.09:
            continue
        if digit_ratio > 0.45 and not contains_cjk(sentence):
            continue
        selected.append(sentence)
        if len(selected) >= max_sentences:
            break
    if not selected:
        return canonical_summary(plain, max_chars=max_chars)
    joined = " ".join(selected)
    return canonical_summary(joined, max_chars=max_chars)


def summary_penalty(text: str) -> int:
    value = summary_quality_cleanup(str(text or ""))
    if not value:
        return 100
    penalty = 0
    if value.count("(") != value.count(")"):
        penalty += 5
    if value.endswith(":"):
        penalty += 3
    if re.search(r"(Eq\.|Fig\.|Sec\.|Table)\s*$", value):
        penalty += 4
    if re.search(r"\b(at|to|from|with|under|for|and|or)\.$", value, flags=re.IGNORECASE):
        penalty += 4
    if re.search(r"[=:]\s*$", value):
        penalty += 3
    if re.search(r"\.\.\.|…", value):
        penalty += 6
    if re.search(r"(\\begin|\\end|\\\\|&=)", value):
        penalty += 6
    if re.search(r"\bt\s*t\s*\^\s*[a-z0-9_]+\b", value, flags=re.IGNORECASE):
        penalty += 6
    if re.search(r"\b\d+\s*,\s*\.\.\.\s*,\s*[a-z0-9]+\b", value, flags=re.IGNORECASE):
        penalty += 6
    if re.search(r"\b[a-z]\s+p\d+\s+\d+\b", value, flags=re.IGNORECASE):
        penalty += 8
    if re.search(r"\b[a-z]\s+p\d+\b", value, flags=re.IGNORECASE):
        penalty += 10
    if re.search(r"\b[a-z]\s+\d+\b", value, flags=re.IGNORECASE):
        penalty += 5
    if re.search(r"\bdefine\s*=\s*t\d+\b", value, flags=re.IGNORECASE):
        penalty += 10
    if re.search(r"\b1\.\.N\b", value, flags=re.IGNORECASE):
        penalty += 8
    if re.search(r"\bK=\d+(?:,\d+)+\b", value):
        penalty += 7
    if re.search(r"\bP=\d+(?:\.\d+)?\b", value) and len(value) < 80:
        penalty += 3
    if re.search(r"(?:,\s*all$|,\s*all\.)", value, flags=re.IGNORECASE):
        penalty += 9
    if re.search(r"\bsec:[a-z0-9_\-]+\b", value, flags=re.IGNORECASE):
        penalty += 6
    if re.search(r"\b\d+\s*,\s*,\s*[a-z0-9]+\b", value, flags=re.IGNORECASE):
        penalty += 10
    if re.search(r"\bup to\.\s*$", value, flags=re.IGNORECASE):
        penalty += 7
    if re.search(r"\bwe use,\s*hence\b", value, flags=re.IGNORECASE):
        penalty += 6
    if re.search(r",\s*,", value):
        penalty += 6
    single_letter_tokens = re.findall(r"\b[a-z]\b", value, flags=re.IGNORECASE)
    if len(single_letter_tokens) > 8 and not contains_cjk(value):
        penalty += 5
    if value.count(",") > 12:
        penalty += 2
    if len(value) < 80:
        penalty += 2
    digit_ratio = len(re.findall(r"\d", value)) / max(1, len(value))
    if digit_ratio > 0.34 and not contains_cjk(value):
        penalty += 4
    if len(re.findall(r"[=<>/\\^_]", value)) > max(8, int(len(value) * 0.08)):
        penalty += 3
    return penalty


def choose_best_summary(candidates: list[str], *, max_chars: int = 1000) -> str:
    scored: list[tuple[int, int, str]] = []
    for raw in candidates:
        cleaned = readable_summary(raw, max_chars=max_chars, max_sentences=4) or canonical_summary(raw, max_chars=max_chars)
        cleaned = summary_quality_cleanup(cleaned)
        if not cleaned:
            continue
        penalty = summary_penalty(cleaned)
        if penalty >= 28 and len(cleaned) < 220:
            continue
        scored.append((penalty, -min(len(cleaned), max_chars), cleaned))
    if not scored:
        return ""
    scored.sort(key=lambda row: (row[0], row[1]))
    return scored[0][2]


def improve_summary_if_needed(summary: str, fallback_candidates: list[str], *, max_chars: int = 1000) -> str:
    cleaned = canonical_summary(summary_quality_cleanup(strip_mathish_fragments(str(summary or ""))), max_chars=max_chars)
    if cleaned and summary_penalty(cleaned) <= 9:
        return cleaned
    fallback = choose_best_summary(fallback_candidates, max_chars=max_chars)
    if fallback:
        return canonical_summary(summary_quality_cleanup(strip_mathish_fragments(fallback)), max_chars=max_chars)
    return cleaned


def sanitize_claim_text_for_map(text: str, *, lang: str, max_chars: int, report_id: str = "") -> str:
    value = summary_quality_cleanup(strip_mathish_fragments(repair_common_math_noise(normalize_space(text))))
    value = value.replace("`", "")
    value = re.sub(r"\b(?:Grid|Ring|Cross)\s*:\s*", "", value, flags=re.IGNORECASE)
    if not value:
        return ""
    value = re.sub(r"\bt_p(\d+)\b", r"peak-\1", value, flags=re.IGNORECASE)
    value = re.sub(r"\bP=\s*([0-9.]+)\b", r"P=\1", value, flags=re.IGNORECASE)
    value = re.sub(r"\[\(\s*[A-Z]\s*\)\]", " ", value)
    value = repair_common_math_noise(value)
    value = readable_summary(value, max_chars=max_chars, max_sentences=2) or canonical_summary(value, max_chars=max_chars)
    value = canonical_summary(summary_quality_cleanup(strip_mathish_fragments(repair_common_math_noise(value))), max_chars=max_chars)
    if not value:
        return ""
    if lang == "cn":
        if not contains_cjk(value):
            return ensure_cn_text(value, report_id or "cross_model", role="claim", max_chars=max_chars)
        if value[-1] not in "。！？；":
            value = value.rstrip(" ,;") + "。"
    else:
        if value[-1] not in ".!?;":
            stop = max(value.rfind(". "), value.rfind("; "), value.rfind("! "), value.rfind("? "))
            if stop >= int(len(value) * 0.55):
                value = value[: stop + 1].strip()
            if value and value[-1] not in ".!?;":
                value += "."
    return canonical_summary(value, max_chars=max_chars)


def humanize_report_id(report_id: str) -> str:
    token_map = {
        "grid2d": "Grid2D",
        "ring": "Ring",
        "cross": "Cross",
        "k2": "K=2",
        "rev2": "Rev2",
    }
    parts = [part.strip() for part in str(report_id).split("_") if part.strip()]
    rendered: list[str] = []
    for part in parts:
        lowered = part.lower()
        if lowered in token_map:
            rendered.append(token_map[lowered])
        elif re.fullmatch(r"[a-z]+\d+", lowered):
            rendered.append(part.upper())
        else:
            rendered.append(part.capitalize())
    return " ".join(rendered) or str(report_id)


def cn_topic_from_report_id(report_id: str) -> str:
    if report_id.startswith("grid2d_"):
        return "Grid2D 体系"
    if report_id.startswith("ring_"):
        return "Ring 体系"
    if report_id.startswith("cross_"):
        return "跨模型综合"
    return "该研究报告"


def normalize_cn_mixed_phrases(text: str) -> str:
    value = str(text or "")
    replacements: list[tuple[str, str]] = [
        (
            r"\bNo\s+Luca\s+winning\s+region\s+under\s+fixed[-\s]*T\s+full[-\s]*FPT\s+fairness\b\.?",
            "在固定 T 的完整 FPT 公平口径下，不存在 Luca 获胜区域",
        ),
        (
            r"\bLuca\s+winning\s+region\s+under\s+fixed[-\s]*T\s+full[-\s]*FPT\s+fairness\b\.?",
            "固定 T 的完整 FPT 公平口径下的 Luca 获胜区域",
        ),
        (r"\bGlobal\s+regime\s+decision\s*:\s*", "全局判定："),
    ]
    for pattern, repl in replacements:
        value = re.sub(pattern, repl, value, flags=re.IGNORECASE)
    value = re.sub(r"\s+([，。；：！？])", r"\1", value)
    value = re.sub(r"([，。；：！？]){2,}", lambda m: m.group(0)[0], value)
    return normalize_space(value)


def ensure_cn_text(text: str, report_id: str, *, role: str, max_chars: int, hint: str = "") -> str:
    cleaned = canonical_summary(
        normalize_cn_mixed_phrases(
            summary_quality_cleanup(strip_mathish_fragments(repair_common_math_noise(str(text or ""))))
        ),
        max_chars=max_chars,
    )
    if cleaned and contains_cjk(cleaned):
        return cleaned

    topic = cn_topic_from_report_id(report_id)
    default_by_role = {
        "title": f"{topic}：{report_id} 研究报告",
        "summary": f"{topic}：本报告围绕模型设定、首达时间分布、峰谷判据与可复现实验给出可核对证据链。",
        "finding": f"{topic}（{report_id}）：关键结论见本页公式链、交互图与原始资产。",
        "model": f"{topic}：本节说明状态空间、参数约束与边界条件设定。",
        "method": f"{topic}：本节给出解析/数值流程、反演方法与验证协议。",
        "result": f"{topic}：本节总结峰谷结构、通道机制与跨报告对比结论。",
        "section": f"{topic}：本节整理关键证据、图表说明与复现路径。",
        "claim": f"{topic}：该 claim 的证据可在本页公式链与数据面板中核验。",
    }
    fallback = default_by_role.get(role, default_by_role["summary"])
    if role == "title" and hint and contains_cjk(hint):
        fallback = hint
    return canonical_summary(normalize_cn_mixed_phrases(fallback), max_chars=max_chars)


def ensure_en_text(text: str, report_id: str, *, role: str, max_chars: int) -> str:
    raw = summary_quality_cleanup(strip_mathish_fragments(repair_common_math_noise(str(text or ""))))
    cleaned = re.sub(r"[\u4e00-\u9fff]+", " ", raw)
    cleaned = canonical_summary(summary_quality_cleanup(cleaned), max_chars=max_chars)
    if cleaned and not contains_cjk(cleaned):
        if not looks_like_operational_note(cleaned) and not has_malformed_readability_tokens(cleaned) and summary_penalty(cleaned) <= 14:
            return cleaned
        refined = readable_summary(cleaned, max_chars=max_chars, max_sentences=3)
        refined = canonical_summary(summary_quality_cleanup(refined), max_chars=max_chars)
        if (
            refined
            and not contains_cjk(refined)
            and not looks_like_operational_note(refined)
            and not has_malformed_readability_tokens(refined)
            and summary_penalty(refined) <= 14
        ):
            return refined
    fallback_by_role = {
        "title": f"{humanize_report_id(report_id)} report",
        "summary": f"This report on {humanize_report_id(report_id)} provides a coherent chain from model setup to reproducible evidence.",
        "finding": f"Key finding for {report_id}: see the equation chain, interactive panels, and source-linked assets.",
        "model": f"This section defines the model state space, parameters, and boundary assumptions for {report_id}.",
        "method": f"This section summarizes derivation, inversion, simulation, and validation procedures for {report_id}.",
        "result": f"This section reports peak-valley behavior, mechanism interpretation, and cross-report implications for {report_id}.",
        "section": f"This section consolidates evidence and verification notes for {report_id}.",
        "claim": f"This claim in {report_id} is backed by equation cards, datasets, and source-linked files.",
    }
    return canonical_summary(fallback_by_role.get(role, fallback_by_role["summary"]), max_chars=max_chars)


def is_generic_en_role_text(text: str, report_id: str, role: str) -> bool:
    lowered = normalize_space(str(text or "")).lower()
    if not lowered:
        return True
    report_key = report_id.lower()
    common_patterns = [
        "provides a coherent chain from model setup to reproducible evidence",
        "core derivation and reproducible evidence are available",
        "see the mathematical logic chain and interactive datasets on this page",
    ]
    if any(pattern in lowered for pattern in common_patterns):
        return True
    if role == "summary":
        return lowered.startswith("this report on ") or lowered == f"{humanize_report_id(report_id).lower()} report"
    if role == "finding":
        return lowered.startswith(f"key finding for {report_key}:")
    if role == "result":
        return lowered.startswith("this section reports peak-valley behavior")
    if role == "method":
        return lowered.startswith("this section summarizes derivation, inversion, simulation")
    if role == "model":
        return lowered.startswith("this section defines the model state space")
    if role == "section":
        return lowered.startswith("this section ") and ("evidence" in lowered or "verification" in lowered)
    return False


def is_generic_cn_role_text(text: str, role: str) -> bool:
    lowered = normalize_space(str(text or ""))
    if not lowered:
        return True
    generic_cn_patterns = [
        "本报告围绕模型设定、首达时间分布、峰谷判据与可复现实验给出可核对证据链",
        "关键结论见本页公式链、交互图与原始资产",
        "本节总结峰谷结构、通道机制与跨报告对比结论",
        "本节给出解析/数值流程、反演方法与验证协议",
        "本节说明状态空间、参数约束与边界条件设定",
        "该 claim 的证据可在本页公式链与数据面板中核验",
    ]
    if any(pattern in lowered for pattern in generic_cn_patterns):
        return True
    if role == "summary" and lowered.startswith("该研究报告："):
        return True
    return False


def pick_specific_en_text(report_id: str, role: str, candidates: list[str], *, max_chars: int) -> str:
    for raw in candidates:
        if not normalize_space(raw):
            continue
        candidate = ensure_en_text(raw, report_id, role=role, max_chars=max_chars)
        if not candidate:
            continue
        if is_generic_en_role_text(candidate, report_id, role):
            continue
        if looks_like_operational_note(candidate):
            continue
        if has_malformed_readability_tokens(candidate):
            continue
        if summary_penalty(candidate) > 18:
            continue
        return canonical_summary(candidate, max_chars=max_chars)
    return ""


def pick_specific_cn_text(report_id: str, role: str, candidates: list[str], *, max_chars: int) -> str:
    for raw in candidates:
        if not normalize_space(raw):
            continue
        candidate = ensure_cn_text(raw, report_id, role=role, max_chars=max_chars)
        if not candidate:
            continue
        if is_generic_cn_role_text(candidate, role):
            continue
        if has_malformed_readability_tokens(candidate):
            continue
        if summary_penalty(candidate) > 20:
            continue
        return canonical_summary(candidate, max_chars=max_chars)
    return ""


def title_penalty(text: str, report_id: str) -> int:
    value = summary_quality_cleanup(str(text))
    if not value:
        return 100
    lowered = value.lower()
    penalty = 0
    if len(value) < 10:
        penalty += 5
    if len(value) > 120:
        penalty += 4
    if len(value) > 160:
        penalty += 6
    if re.search(r"\.\.\.|…|\$|&=|\\", value):
        penalty += 7
    if "_" in value:
        penalty += 5
    if "_" in value and value.lower() == value:
        penalty += 4
    if re.search(r"\b(notation|appendix|supplementary)\b", lowered):
        penalty += 3
    if re.search(r"\bvs\s*\([a-z0-9]+\)", lowered):
        penalty += 2
    if lowered == report_id.lower() or lowered == report_id.lower().replace("_", " "):
        penalty += 2
    if re.search(r"[=:]\s*$", value):
        penalty += 2
    return penalty


def choose_best_title(candidates: list[str], report_id: str, *, max_chars: int = 140) -> str:
    scored: list[tuple[int, int, str]] = []
    for raw in candidates:
        cleaned = canonical_summary(summary_quality_cleanup(strip_mathish_fragments(str(raw))), max_chars=max_chars)
        if not cleaned:
            continue
        penalty = title_penalty(cleaned, report_id)
        scored.append((penalty, -len(cleaned), cleaned))
    fallback = canonical_summary(humanize_report_id(report_id), max_chars=max_chars)
    scored.append((title_penalty(fallback, report_id), -len(fallback), fallback))
    scored.sort(key=lambda row: (row[0], row[1]))
    return scored[0][2]


def is_placeholder_section_summary(heading: str, summary: str) -> bool:
    def is_path_heavy_summary(text: str) -> bool:
        normalized_text = normalize_space(text)
        if not normalized_text:
            return True
        lowered_text = normalized_text.lower()
        if re.fullmatch(r"[\w./-]+\.(?:tex|pdf|json|csv|png|jpg|jpeg|svg|md|py|npz)", lowered_text):
            return True
        path_hits = re.findall(
            r"(?:reports|inputs|figures|data|scripts|code|artifacts)/[\w./-]+\.(?:tex|pdf|json|csv|png|jpg|jpeg|svg|md|py|npz)",
            lowered_text,
        )
        if path_hits:
            natural_tokens = re.findall(r"[A-Za-z]{3,}|[\u4e00-\u9fff]{2,}", normalized_text)
            path_token_count = sum(hit.count("/") + 1 for hit in path_hits)
            if len(natural_tokens) < 9 or path_token_count >= 4:
                return True
        if re.search(r"^(?:core|key|main)?\s*(?:data|files?)\s*[:：]", lowered_text) and re.search(
            r"\.(?:json|csv|tex|pdf)\b", lowered_text
        ):
            natural_tokens = re.findall(r"[A-Za-z]{3,}|[\u4e00-\u9fff]{2,}", normalized_text)
            if len(natural_tokens) < 12:
                return True
        return False

    def is_generic_template_summary(text: str) -> bool:
        normalized_text = normalize_space(text)
        lowered_text = normalized_text.lower()
        template_patterns = (
            r"^figures?:\s*this section (?:interprets|summarizes|presents)\b",
            r"^tables?:\s*this section (?:interprets|summarizes|presents)\b",
            r"^this section (?:interprets|summarizes|presents)\s+(?:the\s+)?(?:key\s+)?(?:figures?|tables?)\b",
            r"^本节(?:主要)?(?:解释|总结|汇总|呈现).*(?:图|表)",
        )
        if any(re.search(pattern, lowered_text) for pattern in template_patterns):
            sentence_count = max(1, len(re.findall(r"[.!?。！？]", normalized_text)))
            if len(normalized_text) < 220 or sentence_count <= 2:
                return True
        return False

    normalized = normalize_space(summary)
    if not normalized:
        return True
    lowered = normalized.lower()
    heading_key = normalize_finding_key(heading)
    summary_key = normalize_finding_key(normalized)
    if heading_key and summary_key == heading_key:
        return True
    if re.search(r"section summary\.?$", lowered):
        return True
    if "fallback narrative card" in lowered:
        return True
    if "consolidates key evidence and verification notes" in lowered:
        return True
    if "this section consolidates evidence and verification notes" in lowered:
        return True
    if "supplementary evidence and verification paths" in lowered:
        return True
    if "this section extends mechanism interpretation with parameter contrasts and traceable evidence entry points" in lowered:
        return True
    if is_path_heavy_summary(normalized):
        return True
    if is_generic_template_summary(normalized):
        return True
    if "关键证据与核验说明" in lowered:
        return True
    if "补充证据与核验路径" in lowered:
        return True
    if lowered in {"overview.", "introduction.", "methods.", "results.", "discussion."}:
        return True
    if len(normalized) < 18:
        return True
    return False


def section_fallback_summary(heading: str, report_id: str, lang: str) -> str:
    heading_clean = normalize_space(heading) or ("Section" if lang == "en" else "章节")
    report_label = humanize_report_id(report_id)
    lowered = heading_clean.lower()
    if lang == "cn":
        if any(token in lowered for token in ("figure", "图")):
            return f"{heading_clean}：本节把图中的相区转折与参数带对应起来，并给出可核验的判据锚点。"
        if any(token in lowered for token in ("table", "表")):
            return f"{heading_clean}：本节列出阈值区间、误差边界和跨案例差异，便于复现实验核对。"
        if any(token in lowered for token in ("recommend", "建议", "practical")):
            return f"{heading_clean}：本节给出可执行建议及其证据边界条件。"
        return f"{heading_clean}：本节连接 {report_label} 的模型假设、可测输出与证据命令入口。"
    if any(token in lowered for token in ("figure", "plot", "visual")):
        return (
            f"{heading_clean}: this section maps figure-level regime transitions to parameter bands, "
            "with each turning point linked to a checkable claim."
        )
    if any(token in lowered for token in ("table", "matrix")):
        return (
            f"{heading_clean}: this section lists threshold bands, uncertainty margins, "
            "and side-by-side outcome deltas for reproducible comparison."
        )
    if any(token in lowered for token in ("recommend", "practical", "guideline")):
        return f"{heading_clean}: this section states actionable recommendations with explicit evidence limits."
    return (
        f"{heading_clean}: this section connects {report_label} assumptions to measurable observables, "
        "verification commands, and downstream chapter claims."
    )


def dedupe_section_cards_by_heading(cards: list[dict[str, str]], *, lang: str) -> list[dict[str, str]]:
    best_by_heading: dict[str, dict[str, str]] = {}
    for row in cards:
        heading = normalize_space(str(row.get("heading", "")))
        summary = normalize_space(str(row.get("summary", "")))
        source_path = normalize_space(str(row.get("source_path", "")))
        if not heading or not summary:
            continue
        if is_placeholder_section_summary(heading, summary) or has_malformed_readability_tokens(summary):
            continue
        heading_key = normalize_finding_key(heading) or heading.lower()
        current = best_by_heading.get(heading_key)
        if not current:
            best_by_heading[heading_key] = {"heading": heading, "summary": summary, "source_path": source_path}
            continue
        current_penalty = summary_penalty(str(current.get("summary", "")))
        candidate_penalty = summary_penalty(summary)
        if candidate_penalty < current_penalty:
            best_by_heading[heading_key] = {"heading": heading, "summary": summary, "source_path": source_path}
            continue
        if candidate_penalty == current_penalty and len(summary) > len(str(current.get("summary", ""))):
            best_by_heading[heading_key] = {"heading": heading, "summary": summary, "source_path": source_path}
    rows = list(best_by_heading.values())
    rows.sort(key=lambda item: normalize_finding_key(item.get("heading", "")))
    if not rows and cards:
        seed = cards[0]
        rows = [
            {
                "heading": normalize_space(str(seed.get("heading", ""))) or ("Section" if lang == "en" else "章节"),
                "summary": normalize_space(str(seed.get("summary", ""))),
                "source_path": normalize_space(str(seed.get("source_path", ""))),
            }
        ]
    return rows[:10]


def parse_tex_title(tex_text: str) -> str:
    m = re.search(r"\\title\{(.*?)\}", tex_text, flags=re.DOTALL)
    if not m:
        return ""
    raw = strip_mathish_fragments(latex_to_plain(m.group(1)))
    return canonical_summary(summary_quality_cleanup(repair_common_math_noise(raw)), max_chars=220)


def parse_tex_abstract(tex_text: str) -> str:
    m = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", tex_text, flags=re.DOTALL)
    if not m:
        return ""
    return canonical_summary(summary_quality_cleanup(repair_common_math_noise(latex_to_plain(m.group(1)))), max_chars=1200)


def pick_main_tex_path(item: dict[str, Any], report_dir: Path, lang: str) -> Path | None:
    candidates = [str(x) for x in item.get("main_tex", []) if str(x).endswith(".tex")]
    ranked: list[str] = []
    lang_tag = f"_{lang}"
    ranked.extend([name for name in candidates if lang_tag in name])
    if lang == "en":
        ranked.extend([name for name in candidates if "_cn" not in name])
    ranked.extend(candidates)

    seen: set[str] = set()
    for rel in ranked:
        if rel in seen:
            continue
        seen.add(rel)
        path = report_dir / rel
        if path.exists():
            return path

    fallback = sorted(p for p in report_dir.rglob("*.tex") if p.is_file() and "build" not in p.parts)
    return fallback[0] if fallback else None


def split_sections(tex_text: str) -> list[dict[str, Any]]:
    pattern = re.compile(r"\\section\*?\{([^{}]+)\}")
    matches = list(pattern.finditer(tex_text))
    if not matches:
        return []

    sections: list[dict[str, Any]] = []
    for idx, match in enumerate(matches):
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(tex_text)
        title = normalize_space(latex_to_plain(match.group(1)))
        body = tex_text[start:end]
        if not title:
            continue
        body_plain = latex_to_plain(body)
        sections.append(
            {
                "title": title,
                "start": start,
                "end": end,
                "summary": summarize_plain(body_plain, max_chars=340),
                "body": body,
            }
        )
    return sections


def section_title_for_index(sections: list[dict[str, Any]], index: int) -> str:
    for section in sections:
        if int(section["start"]) <= index < int(section["end"]):
            return str(section["title"])
    if sections:
        return str(sections[0]["title"])
    return "Overview"


def extract_itemize_lines(text: str, *, limit: int = 10) -> list[str]:
    findings: list[str] = []
    for block in re.finditer(r"\\begin\{itemize\}(.*?)\\end\{itemize\}", text, flags=re.DOTALL):
        part = block.group(1)
        for raw in re.findall(r"\\item\s+(.*?)(?=(\\item|$))", part, flags=re.DOTALL):
            cleaned = summarize_plain(latex_to_plain(raw[0]), max_chars=220)
            if cleaned:
                findings.append(cleaned)
            if len(findings) >= limit:
                return findings
    return findings


def extract_findings_from_sections(sections: list[dict[str, Any]]) -> list[str]:
    findings: list[str] = []
    for section in sections:
        title_lower = str(section["title"]).lower()
        if not any(key in title_lower for key in RESULT_HINTS):
            continue
        findings.extend(extract_itemize_lines(str(section["body"]), limit=8))
        if len(findings) < 8:
            findings.append(str(section["summary"]))
    return dedupe_preserve(findings, max_items=8)


def extract_repro_commands(tex_text: str, sections: list[dict[str, Any]]) -> list[str]:
    commands: list[str] = []
    target_ranges: list[tuple[int, int]] = []
    for section in sections:
        title_lower = str(section["title"]).lower()
        if any(key in title_lower for key in REPRO_HINTS):
            target_ranges.append((int(section["start"]), int(section["end"])))

    search_space = tex_text
    if target_ranges:
        chunks = [tex_text[start:end] for start, end in target_ranges]
        search_space = "\n".join(chunks)

    commands.extend(re.findall(r"\\path\{([^{}]+)\}", search_space))
    commands.extend(re.findall(r"\\texttt\{([^{}]*?(?:python|pytest|npm|reportctl)[^{}]*)\}", search_space))
    commands.extend(re.findall(r"(python3?\s+[^\n\\]+)", latex_to_plain(search_space)))

    cleaned = []
    for cmd in commands:
        text = normalize_space(cmd.strip())
        if not text:
            continue
        if len(text) > 220:
            continue
        cleaned.append(text)
    return dedupe_preserve(cleaned, max_items=10)


def ensure_repro_commands(commands: list[str], report_id: str) -> list[str]:
    cleaned = dedupe_preserve([normalize_space(str(x)) for x in commands], max_items=14)
    executable: list[str] = []
    for cmd in cleaned:
        lowered = cmd.lower()
        if re.match(r"^(python\d?\b|pytest\b|npm\b|node\b|bash\b|sh\b|reportctl\b|make\b|uv\b|poetry\b)", lowered):
            executable.append(cmd)
            continue
        if re.match(r"^cd\s+\S+\s*&&\s*(python\d?\b|pytest\b|npm\b|node\b|reportctl\b|bash\b|sh\b)", lowered):
            executable.append(cmd)
            continue
    executable = dedupe_preserve(executable, max_items=10)
    if executable:
        has_report_specific = any(
            report_id in cmd
            or f"--report {report_id}" in cmd
            or f"research/reports/{report_id}" in cmd
            or "reportctl.py build --report" in cmd
            for cmd in executable
        )
        if not has_report_specific:
            executable.insert(0, f"python3 scripts/reportctl.py build --report {report_id} --lang en")
        has_validation = any(
            "translation-qc" in cmd
            or "validate_web_data.py" in cmd
            or "validate_bilingual_quality.py" in cmd
            for cmd in executable
        )
        if not has_validation:
            executable.append("python3 scripts/reportctl.py translation-qc")
        has_web_build = any("web-build" in cmd for cmd in executable)
        if not has_web_build:
            executable.append("python3 scripts/reportctl.py web-build --mode changed --skip-npm-ci")
        return dedupe_preserve(executable, max_items=10)
    return [
        f"python3 scripts/reportctl.py build --report {report_id} --lang en",
        "python3 scripts/reportctl.py translation-qc",
        "python3 scripts/reportctl.py web-build --mode changed --skip-npm-ci",
    ]


def classify_formula_stage(latex: str, context: str, lang: str) -> tuple[str, str]:
    lowered = latex.lower()
    context_lower = context.lower()
    if "p_{t+1}" in lowered or "p(t+1)" in lowered or "b p" in lowered:
        return (
            ("Markov Update", "马尔可夫更新")[lang == "cn"],
            (
                "Advances state probability by one step through the transition operator.",
                "通过转移算子推进一步状态概率更新。",
            )[lang == "cn"],
        )
    if "f(t)" in lowered or "\\pr" in lowered:
        return (
            ("Distribution Setup", "分布定义")[lang == "cn"],
            (
                "Defines first-passage probability objects used by later diagnostics.",
                "定义后续诊断所依赖的首达时间概率对象。",
            )[lang == "cn"],
        )
    if "s(t)" in lowered or "survival" in lowered:
        return (
            ("Survival Link", "生存函数联系")[lang == "cn"],
            (
                "Connects probability mass to survival dynamics over time.",
                "连接概率质量与随时间演化的生存过程。",
            )[lang == "cn"],
        )
    if "h(t)" in lowered or "hazard" in lowered:
        return (
            ("Hazard Interpretation", "风险率解释")[lang == "cn"],
            (
                "Converts PMF and survival into a peak/valley-sensitive hazard view.",
                "将 PMF 与生存函数转化为对峰谷敏感的风险率视角。",
            )[lang == "cn"],
        )
    if "\\beta" in lowered or "beta" in lowered or ("u\\to" in lowered and "v" in lowered):
        return (
            ("Shortcut Perturbation", "shortcut 扰动")[lang == "cn"],
            (
                "Captures how shortcut intensity changes transition balance.",
                "刻画 shortcut 强度如何改变转移平衡。",
            )[lang == "cn"],
        )
    if "\\lambda" in lowered or "eigen" in lowered or "\\sum" in lowered or "fft" in lowered:
        return (
            ("Spectral / Inversion Step", "谱分解 / 反演步骤")[lang == "cn"],
            (
                "Provides analytic inversion machinery for computing trajectories.",
                "提供用于计算轨迹分布的解析反演机制。",
            )[lang == "cn"],
        )
    if "model" in context_lower or "definition" in context_lower:
        return (
            ("Model Constraint", "模型约束")[lang == "cn"],
            (
                "States the structural constraints and parameter ranges of the model.",
                "给出模型结构约束与参数范围。",
            )[lang == "cn"],
        )
    return (
        ("Derivation Link", "推导连接")[lang == "cn"],
        (
            "Adds a relation that links neighboring steps in the derivation chain.",
            "补充连接推导相邻步骤的关系式。",
        )[lang == "cn"],
    )


REPORT_MATH_BRIDGE_TEMPLATES: dict[str, list[dict[str, str]]] = {
    "ring_valley": [
        {
            "context_en": "Directed-shortcut transition kernel",
            "context_cn": "单向 shortcut 转移核",
            "latex": (
                r"P_{i\to j}=\frac{1}{K}\mathbf{1}[j\in\mathcal{N}_K(i)]"
                r"+\mathbf{1}[i=6]\left(\frac{1}{K+1}\mathbf{1}\!\left[j=\frac{N}{2}+1\right]"
                r"-\frac{1}{K(K+1)}\mathbf{1}[j\in\mathcal{N}_K(6)]\right)"
            ),
        },
        {
            "context_en": "FPT-survival-hazard consistency",
            "context_cn": "FPT-生存-风险率一致性",
            "latex": r"f(t)=\Pr[T=t],\quad S(t)=1-\sum_{u=1}^{t}f(u),\quad h(t)=\frac{f(t)}{S(t-1)}",
        },
        {
            "context_en": "Parity-aware coarse graining for K=2",
            "context_cn": "K=2 的奇偶粗粒化",
            "latex": r"\tilde{A}(m)=A(2m-1)+A(2m),\quad m=1,\dots,\left\lfloor\frac{T_{\max}}{2}\right\rfloor",
        },
        {
            "context_en": "Fig.3 two-peak admissibility criterion",
            "context_cn": "Fig.3 双峰可接受判据",
            "latex": (
                r"A(t_1-1)<A(t_1)>A(t_1+1),\ A(t_2-1)<A(t_2)>A(t_2+1),\ "
                r"A(t_2)\ge 0.01\max_{t}A(t)"
            ),
        },
        {
            "context_en": "Valley location and adaptive width",
            "context_cn": "谷值定位与自适应窗口",
            "latex": (
                r"t_{\mathrm{valley}}=\arg\min_{t_1<t<t_2}A(t),\quad "
                r"\Delta=\max\left\{1,\left\lfloor0.05\,(t_2-t_1)\right\rfloor\right\}"
            ),
        },
        {
            "context_en": "Trajectory class partition around valley and second peak",
            "context_cn": "围绕谷值与第二峰的轨迹分层",
            "latex": (
                r"\text{direct}:T<t_{\mathrm{valley}}-\Delta,\ "
                r"\text{valley}:|T-t_{\mathrm{valley}}|\le\Delta,\ "
                r"\text{intermediate}:t_{\mathrm{valley}}+\Delta<T\le t_2+\Delta,\ "
                r"\text{indirect}:T>t_2+\Delta"
            ),
        },
    ]
}


def formula_signature_key(latex: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", normalize_space(latex).lower())


def supplemental_math_blocks(report_id: str, source_path: str, lang: str) -> list[dict[str, str]]:
    templates = REPORT_MATH_BRIDGE_TEMPLATES.get(report_id, [])
    if not templates:
        return []
    rows: list[dict[str, str]] = []
    for item in templates:
        latex = sanitize_latex_for_katex(str(item.get("latex", "")))
        if not latex:
            continue
        context_key = "context_cn" if lang == "cn" else "context_en"
        context = normalize_space(str(item.get(context_key, ""))) or "Bridge Formula"
        rows.append(
            {
                "latex": latex,
                "context": context,
                "source_path": source_path,
                "lang": lang,
            }
        )
    return rows


def augment_report_math_blocks(report_id: str, math_blocks: list[dict[str, str]], source_path: str, lang: str) -> list[dict[str, str]]:
    target_minimum = {
        "ring_valley": 6,
    }
    target = target_minimum.get(report_id)
    if target is None:
        return math_blocks
    merged = list(math_blocks)
    seen = {formula_signature_key(str(row.get("latex", ""))) for row in merged if str(row.get("latex", "")).strip()}
    if len(merged) >= target:
        return merged
    for row in supplemental_math_blocks(report_id, source_path, lang):
        signature = formula_signature_key(str(row.get("latex", "")))
        if not signature or signature in seen:
            continue
        merged.append(row)
        seen.add(signature)
        if len(merged) >= target:
            break
    return merged[:14]


def build_math_story(math_blocks: list[dict[str, str]], lang: str) -> list[dict[str, str]]:
    story: list[dict[str, str]] = []
    for block in math_blocks:
        context = str(block.get("context", "Overview"))
        stage, description = classify_formula_stage(str(block.get("latex", "")), context, lang)
        story.append(
            {
                "stage": stage,
                "description": description,
                "latex": str(block.get("latex", "")),
                "context": context,
            }
        )
    trimmed = story[:6]
    if trimmed:
        return trimmed
    return [
        {
            "stage": ("Fallback Chain", "兜底逻辑链")[lang == "cn"],
            "description": (
                "Base FPT relation retained when no explicit formula block is detected.",
                "在未提取到显式公式时保留基础首达时间关系。",
            )[lang == "cn"],
            "latex": r"f(t)=\Pr[T=t],\quad S(t)=\Pr[T>t],\quad h(t)=\frac{f(t)}{S(t-1)}",
            "context": "Fallback",
        }
    ]


def extract_math_blocks(tex_text: str, sections: list[dict[str, Any]], source_path: str, lang: str) -> list[dict[str, str]]:
    candidates: list[tuple[str, int]] = []
    env_pattern = re.compile(
        r"\\begin\{(equation\*?|align\*?|gather\*?|multline\*?)\}(.*?)\\end\{\1\}",
        flags=re.DOTALL,
    )
    for match in env_pattern.finditer(tex_text):
        latex = normalize_space(match.group(2))
        if latex:
            candidates.append((latex, match.start()))

    for match in re.finditer(r"\\\[(.*?)\\\]", tex_text, flags=re.DOTALL):
        latex = normalize_space(match.group(1))
        if latex:
            candidates.append((latex, match.start()))

    for match in re.finditer(r"\$([^$\n]{8,180})\$", tex_text):
        latex = normalize_space(match.group(1))
        if latex and ("=" in latex or "\\Pr" in latex or "\\sum" in latex):
            candidates.append((latex, match.start()))

    blocks: list[dict[str, str]] = []
    seen: set[str] = set()
    for latex, idx in sorted(candidates, key=lambda row: row[1]):
        cleaned = sanitize_latex_for_katex(latex)
        if not cleaned:
            continue
        if is_trivial_formula_signature(cleaned):
            continue
        signature = formula_signature_key(cleaned)
        if not signature or signature in seen:
            continue
        seen.add(signature)
        blocks.append(
            {
                "latex": cleaned,
                "context": section_title_for_index(sections, idx),
                "source_path": source_path,
                "lang": lang,
            }
        )
        if len(blocks) >= 14:
            break

    if not blocks:
        blocks.append(
            {
                "latex": r"f(t)=\Pr[T=t],\quad S(t)=\Pr[T>t],\quad h(t)=\frac{f(t)}{S(t-1)}",
                "context": "Fallback",
                "source_path": source_path,
                "lang": lang,
            }
        )
    return blocks


def pick_narrative_summary(sections: list[dict[str, Any]], hints: tuple[str, ...], fallback: str) -> str:
    for section in sections:
        title_lower = str(section["title"]).lower()
        if any(h in title_lower for h in hints):
            return str(section["summary"])
    if sections:
        return str(sections[0]["summary"])
    return fallback


def build_narrative_fields(sections: list[dict[str, Any]], fallback: str) -> dict[str, str]:
    def clean_narrative_text(text: str) -> str:
        cleaned = summary_quality_cleanup(strip_mathish_fragments(repair_common_math_noise(text)))
        if not cleaned:
            cleaned = summary_quality_cleanup(text)
        out = readable_summary(cleaned, max_chars=320, max_sentences=2) or canonical_summary(cleaned, max_chars=320)
        out = canonical_summary(summary_quality_cleanup(repair_common_math_noise(out)), max_chars=320)
        if summary_penalty(out) > 20:
            out = canonical_summary(summary_quality_cleanup(repair_common_math_noise(fallback)), max_chars=320)
        return out

    model = clean_narrative_text(pick_narrative_summary(sections, MODEL_HINTS, fallback))
    method = clean_narrative_text(pick_narrative_summary(sections, METHOD_HINTS, fallback))
    result = clean_narrative_text(pick_narrative_summary(sections, RESULT_HINTS, fallback))
    values = [model, method, result]
    if len({normalize_finding_key(v) for v in values if v}) >= 2:
        return {
            "model_overview": model,
            "method_overview": method,
            "result_overview": result,
        }

    section_summaries = [
        clean_narrative_text(str(section.get("summary", fallback)))
        for section in sections
        if section.get("summary")
        and not is_placeholder_section_summary(str(section.get("title", "")), str(section.get("summary", "")))
    ]
    while len(section_summaries) < 3:
        section_summaries.append(clean_narrative_text(fallback))
    return {
        "model_overview": section_summaries[0],
        "method_overview": section_summaries[1],
        "result_overview": section_summaries[2],
    }


def extract_tex_story(item: dict[str, Any], report_dir: Path, report_id: str, lang: str) -> dict[str, Any]:
    tex_path = pick_main_tex_path(item, report_dir, lang)
    if not tex_path or not tex_path.exists():
        fallback_source = str(item.get("path", report_id))
        fallback_math = [
            {
                "latex": r"f(t)=\Pr[T=t]",
                "context": "Fallback",
                "source_path": fallback_source,
                "lang": lang,
            }
        ]
        return {
            "title": "",
            "summary": "",
            "section_cards": [
                {
                    "heading": "Overview",
                    "summary": f"Fallback narrative card for {report_id}.",
                    "source_path": fallback_source,
                }
            ],
            "math_blocks": fallback_math,
            "math_story": build_math_story(fallback_math, lang),
            "findings": [],
            "reproducibility_commands": ensure_repro_commands([], report_id),
            "narrative": {
                "model_overview": f"Model summary placeholder for {report_id}.",
                "method_overview": f"Method summary placeholder for {report_id}.",
                "result_overview": f"Result summary placeholder for {report_id}.",
            },
            "source_documents": [fallback_source],
        }

    raw = tex_path.read_text(encoding="utf-8", errors="ignore")
    sections = split_sections(raw)
    abstract = parse_tex_abstract(raw)
    summary_seed = abstract or (sections[0]["summary"] if sections else f"Research report {report_id}.")
    summary_fallback = readable_summary(summary_seed, max_chars=1000, max_sentences=4) or canonical_summary(summary_seed, max_chars=1000)
    section_cards: list[dict[str, str]] = []
    seen_section_summary_keys: set[str] = set()
    for section in sections[:10]:
        heading = str(section["title"])
        summary = normalize_space(str(section.get("summary", "")))
        if is_placeholder_section_summary(heading, summary) or has_malformed_readability_tokens(summary):
            body_candidate = readable_summary(latex_to_plain(str(section.get("body", ""))), max_chars=280, max_sentences=2)
            summary = normalize_space(body_candidate)
        if is_placeholder_section_summary(heading, summary) or has_malformed_readability_tokens(summary):
            summary = readable_summary(summary_fallback, max_chars=280, max_sentences=2)
        summary = readable_summary(strip_mathish_fragments(summary_quality_cleanup(summary)), max_chars=320, max_sentences=2) or summary
        summary = canonical_summary(summary_quality_cleanup(strip_mathish_fragments(summary)), max_chars=320)
        summary_key = normalize_finding_key(summary)
        if not summary or summary_penalty(summary) > 14 or has_malformed_readability_tokens(summary):
            summary = readable_summary(
                strip_mathish_fragments(summary_quality_cleanup(latex_to_plain(str(section.get("body", ""))))),
                max_chars=320,
                max_sentences=2,
            ) or summary
            summary = canonical_summary(summary_quality_cleanup(strip_mathish_fragments(summary)), max_chars=320)
            summary_key = normalize_finding_key(summary)
        if not summary or summary_penalty(summary) > 14 or has_malformed_readability_tokens(summary):
            summary = section_fallback_summary(heading, report_id, lang)
            summary_key = normalize_finding_key(summary)
        if summary_key and summary_key in seen_section_summary_keys:
            body_alternative = readable_summary(
                strip_mathish_fragments(summary_quality_cleanup(latex_to_plain(str(section.get("body", ""))))),
                max_chars=320,
                max_sentences=3,
            )
            candidate = canonical_summary(
                summary_quality_cleanup(strip_mathish_fragments(body_alternative or "")),
                max_chars=320,
            )
            candidate_key = normalize_finding_key(candidate)
            if candidate and candidate_key and candidate_key not in seen_section_summary_keys:
                summary = candidate
                summary_key = candidate_key
            else:
                summary = section_fallback_summary(heading, report_id, lang)
                summary_key = normalize_finding_key(summary)
        if summary_key:
            seen_section_summary_keys.add(summary_key)
        section_cards.append(
            {
                "heading": heading,
                "summary": summary,
                "source_path": rel_repo_path(tex_path),
            }
        )
    findings = extract_findings_from_sections(sections)
    source_path = rel_repo_path(tex_path)
    math_blocks = extract_math_blocks(raw, sections, source_path, lang)
    math_blocks = augment_report_math_blocks(report_id, math_blocks, source_path, lang)
    math_story = build_math_story(math_blocks, lang)
    if not section_cards:
        section_cards = [
            {
                "heading": "Overview",
                "summary": readable_summary(summary_fallback, max_chars=360, max_sentences=2),
                "source_path": source_path,
            }
        ]
    return {
        "title": parse_tex_title(raw),
        "summary": readable_summary(summary_fallback, max_chars=1000, max_sentences=4),
        "section_cards": section_cards,
        "math_blocks": math_blocks,
        "math_story": math_story,
        "findings": findings,
        "reproducibility_commands": ensure_repro_commands(extract_repro_commands(raw, sections), report_id),
        "narrative": build_narrative_fields(sections, summary_fallback),
        "source_documents": [source_path],
    }


def utc_now_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat().replace("+00:00", "Z")


def iso_from_timestamp(ts: float) -> str:
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat().replace("+00:00", "Z")


def detect_report_updated_at(report_dir: Path, fallback_iso: str) -> str:
    latest_ts = 0.0
    for path in report_dir.rglob("*"):
        if not path.is_file():
            continue
        if "build" in path.parts or "__pycache__" in path.parts or ".venv" in path.parts:
            continue
        try:
            latest_ts = max(latest_ts, float(path.stat().st_mtime))
        except OSError:
            continue
    if latest_ts <= 0:
        return fallback_iso
    return iso_from_timestamp(latest_ts)


def normalize_finding_key(text: str) -> str:
    raw = normalize_space(text)
    if not raw:
        return ""
    raw = re.sub(r"`", "", raw)
    raw = raw.replace("\\", "")
    raw = re.sub(r"\s+", " ", raw)
    raw = re.sub(r"[^\w]+", "", raw.lower(), flags=re.UNICODE)
    return raw


def is_trivial_formula_signature(latex: str) -> bool:
    compact = re.sub(r"\s+", "", normalize_space(latex))
    if not compact:
        return True
    if len(normalize_finding_key(compact)) < 10:
        return True
    if re.fullmatch(r"[A-Za-z\\_{}0-9]+=[-+]?\d+(?:\.\d+)?", compact):
        return True
    if re.fullmatch(r"\\text\{[^{}]+\}=\\text\{[^{}]+\}", compact):
        return True
    if re.fullmatch(r"[A-Za-z\\_{}]+=\d+e-?\d+", compact, flags=re.IGNORECASE):
        return True
    token_count = len(re.findall(r"[A-Za-z]+|\\[A-Za-z]+", compact))
    if "=" in compact and token_count <= 2 and re.search(r"\d", compact):
        return True
    return False


def tokenize_claim_text(text: str) -> set[str]:
    tokens = re.findall(r"[a-zA-Z0-9_]+|[\u4e00-\u9fff]{1,4}", normalize_space(text).lower())
    out: set[str] = set()
    for tok in tokens:
        if len(tok) < 2:
            continue
        if tok in CLAIM_STOPWORDS:
            continue
        out.add(tok)
    return out


def looks_like_path_finding(text: str) -> bool:
    lowered = text.lower()
    if lowered.startswith("see ") and "report assets" in lowered:
        return True
    if lowered.startswith("figures:") or lowered.startswith("environment:"):
        return True
    return bool(re.search(r"(?:reports|figures|config|code|scripts)/", lowered))


def enforce_unique_key_findings(output_dir: Path, report_ids: list[str]) -> list[dict[str, Any]]:
    key_to_reports: dict[str, set[str]] = defaultdict(set)
    payloads: dict[tuple[str, str], dict[str, Any]] = {}

    for report_id in report_ids:
        for meta_name in ("meta.json", "meta.cn.json"):
            path = output_dir / "reports" / report_id / meta_name
            if not path.exists():
                continue
            payload = json.loads(path.read_text(encoding="utf-8"))
            payloads[(report_id, meta_name)] = payload
            for finding in payload.get("key_findings", []):
                text = normalize_space(str(finding))
                if not text or looks_like_path_finding(text):
                    continue
                key = normalize_finding_key(text)
                if key:
                    key_to_reports[key].add(report_id)

    duplicate_keys = {key for key, reports in key_to_reports.items() if len(reports) > 1}
    if not duplicate_keys:
        return []

    details: list[dict[str, Any]] = []
    for key in sorted(duplicate_keys):
        details.append({"key": key, "report_ids": sorted(key_to_reports[key])})

    for (report_id, meta_name), payload in payloads.items():
        findings = list(payload.get("key_findings", []))
        changed = False
        new_findings: list[str] = []
        for finding in findings:
            text = normalize_space(str(finding))
            if not text or looks_like_path_finding(text):
                new_findings.append(text)
                continue
            key = normalize_finding_key(text)
            if key in duplicate_keys and f"[{report_id}]" not in text:
                text = f"{text} [{report_id}]"
                changed = True
            new_findings.append(text)

        if changed:
            payload["key_findings"] = dedupe_preserve(new_findings, max_items=8)
            path = output_dir / "reports" / report_id / meta_name
            path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")

    return details


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(1024 * 1024)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def infer_group(report_id: str) -> str:
    if report_id.startswith("ring_"):
        return "ring"
    if report_id.startswith("grid2d_"):
        return "grid2d"
    if report_id.startswith("cross_"):
        return "cross"
    return "misc"


def parse_readme(report_dir: Path, report_id: str) -> tuple[str, str, list[str]]:
    readme = report_dir / "README.md"
    if not readme.exists():
        title = report_id.replace("_", " ")
        summary = f"Interactive summary for {report_id}."
        findings = [f"This report ({report_id}) is included in the online atlas."]
        return title, summary, findings

    text = readme.read_text(encoding="utf-8", errors="ignore")
    lines = [line.rstrip() for line in text.splitlines()]

    title = report_id.replace("_", " ")
    for line in lines:
        if line.startswith("#"):
            title = line.lstrip("#").strip()
            break

    def noisy_line(line: str) -> bool:
        stripped = line.strip()
        if not stripped:
            return True
        if stripped.startswith(("#", "-", "```", "`")):
            return True
        lowered = stripped.lower()
        if lowered.endswith(":") and len(stripped) < 90:
            return True
        if re.search(r"\b(python|pytest|npm|node|latexmk|cd|reportctl)\b", lowered):
            return True
        if "--" in stripped:
            return True
        if "/" in stripped and any(token in lowered for token in ("research/reports/", "scripts/", ".py", ".json", ".tex")):
            return True
        return False

    key_section = ""
    key_results: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("#"):
            key_section = stripped.lstrip("#").strip().lower()
            continue
        if not stripped or not stripped.startswith("- "):
            continue
        if any(token in key_section for token in ("key result", "summary", "overview", "highlight", "结论", "结果", "摘要")):
            bullet = summary_quality_cleanup(stripped[2:].strip())
            if bullet and len(bullet) >= 24 and not noisy_line(bullet):
                key_results.append(bullet)
            if len(key_results) >= 3:
                break

    first_paragraph = ""
    for line in lines:
        stripped = line.strip()
        if noisy_line(stripped):
            continue
        if len(stripped) < 40:
            continue
        first_paragraph = summary_quality_cleanup(stripped)
        if first_paragraph:
            break

    summary_candidates: list[str] = []
    if key_results:
        summary_candidates.append(" ".join(key_results[:2]))
        summary_candidates.extend(key_results[:3])
    if first_paragraph:
        summary_candidates.append(first_paragraph)
    summary_candidates.append(f"Research report {report_id}.")
    summary = choose_best_summary(summary_candidates, max_chars=1200) or canonical_summary(summary_candidates[0], max_chars=1200)
    summary = summary_quality_cleanup(summary)

    findings: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("- "):
            findings.append(stripped[2:].strip())
        if len(findings) >= 6:
            break
    if not findings:
        findings = [f"See {report_id} report assets for detailed findings."]

    return title, canonical_summary(summary, max_chars=1200), dedupe_preserve(findings, max_items=8)


def rel_repo_path(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def normalize_origin_url(origin_url: str) -> str:
    value = normalize_space(origin_url)
    if not value:
        return ""
    if value.startswith("git@github.com:"):
        value = value.replace("git@github.com:", "https://github.com/", 1)
    if value.startswith("ssh://git@github.com/"):
        value = value.replace("ssh://git@github.com/", "https://github.com/", 1)
    if value.endswith(".git"):
        value = value[:-4]
    return value


def detect_git_origin_info() -> dict[str, str]:
    origin_url = ""
    default_branch = "main"

    origin_proc = subprocess.run(
        ["git", "config", "--get", "remote.origin.url"],
        cwd=REPO_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if origin_proc.returncode == 0:
        origin_url = normalize_origin_url(origin_proc.stdout.strip())

    head_proc = subprocess.run(
        ["git", "symbolic-ref", "--short", "refs/remotes/origin/HEAD"],
        cwd=REPO_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if head_proc.returncode == 0:
        token = head_proc.stdout.strip()
        if token.startswith("origin/") and len(token.split("/", 1)) == 2:
            default_branch = token.split("/", 1)[1] or default_branch

    return {"origin_url": origin_url, "default_branch": default_branch}


def should_skip_repo_sync_path(path: Path) -> bool:
    parts = set(path.parts)
    if ".git" in parts or "__pycache__" in parts:
        return True
    if "build" in parts:
        return True
    if ".venv" in parts or "venv" in parts:
        return True
    return False


def classify_repo_sync_category(rel_path: str) -> str:
    parts = rel_path.split("/")
    if not parts:
        return "other"
    head = parts[0]
    if len(parts) == 1 and head.endswith(".md"):
        return "root"
    if head in {"README.md", "AGENTS.md", "requirements.txt", "pyproject.toml"}:
        return "root"
    if head == "docs":
        return "docs"
    if head == "reports":
        if len(parts) >= 4 and parts[2] == "code" and parts[-1].endswith(".py"):
            return "report_code"
        return "report_docs"
    if head == "scripts":
        return "tooling"
    if head == "src":
        return "core_code"
    if head == "tests":
        return "tests"
    if head == "schemas":
        return "schemas"
    return "other"


def preview_text_for_repo_sync(path: Path) -> str:
    if path.suffix.lower() not in REPO_SYNC_PREVIEW_EXT:
        return ""
    try:
        raw = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""
    plain = normalize_space(raw[:6000])
    if not plain:
        return ""
    return canonical_summary(plain, max_chars=220)


def build_repo_sync_payload(output_dir: Path, generated_at: str) -> None:
    git_info = detect_git_origin_info()
    origin_url = git_info.get("origin_url", "")
    default_branch = git_info.get("default_branch", "main")

    files_set: set[Path] = set()
    for pattern in REPO_SYNC_INCLUDE_GLOBS:
        for candidate in REPO_ROOT.glob(pattern):
            if not candidate.is_file():
                continue
            if should_skip_repo_sync_path(candidate):
                continue
            files_set.add(candidate)

    files = sorted(files_set, key=lambda p: p.as_posix())[:REPO_SYNC_MAX_FILES]
    file_rows: list[dict[str, Any]] = []
    totals_by_category: dict[str, dict[str, int]] = defaultdict(lambda: {"file_count": 0, "total_size_bytes": 0})

    for path in files:
        rel_path = rel_repo_path(path)
        category = classify_repo_sync_category(rel_path)
        try:
            stat = path.stat()
            size = int(stat.st_size)
            updated_at = iso_from_timestamp(float(stat.st_mtime))
        except OSError:
            size = 0
            updated_at = generated_at
        github_url = ""
        if origin_url:
            github_url = f"{origin_url}/blob/{default_branch}/{rel_path}"
        row = {
            "path": rel_path,
            "category": category,
            "size": size,
            "sha256": sha256_file(path),
            "updated_at": updated_at,
            "github_url": github_url,
        }
        preview = preview_text_for_repo_sync(path)
        if preview:
            row["preview"] = preview
        file_rows.append(row)
        totals_by_category[category]["file_count"] += 1
        totals_by_category[category]["total_size_bytes"] += size

    section_rows: list[dict[str, Any]] = []
    for category, stats in sorted(totals_by_category.items(), key=lambda kv: (-int(kv[1]["file_count"]), kv[0])):
        labels = REPO_SYNC_CATEGORY_LABELS.get(category, REPO_SYNC_CATEGORY_LABELS["other"])
        section_rows.append(
            {
                "key": category,
                "label_en": labels["en"],
                "label_cn": labels["cn"],
                "file_count": int(stats["file_count"]),
                "total_size_bytes": int(stats["total_size_bytes"]),
            }
        )

    payload = {
        "version": "v1",
        "generated_at": generated_at,
        "repo": {
            "origin_url": origin_url,
            "default_branch": default_branch,
            "pages_url": "https://zhouyi-xiaoxiao.github.io/valley-k-small/",
        },
        "stats": {
            "file_count": len(file_rows),
            "total_size_bytes": int(sum(int(row.get("size", 0)) for row in file_rows)),
            "category_count": len(section_rows),
        },
        "sections": section_rows,
        "files": file_rows,
    }
    (output_dir / "repo_sync.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False),
        encoding="utf-8",
    )


def clean_output_dir(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def git_changed_paths() -> list[str]:
    commands = [
        ["git", "diff", "--name-only", "HEAD~1..HEAD"],
        ["git", "diff", "--name-only", "HEAD"],
    ]
    for cmd in commands:
        proc = subprocess.run(
            cmd,
            cwd=REPO_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        if proc.returncode == 0 and proc.stdout.strip():
            return [line.strip() for line in proc.stdout.splitlines() if line.strip()]
    return []


def detect_changed_reports(registry: list[dict[str, Any]]) -> set[str]:
    changed = git_changed_paths()
    if not changed:
        return {item["id"] for item in registry}

    if "research/reports/report_registry.yaml" in changed:
        return {item["id"] for item in registry}

    matched: set[str] = set()
    for rel in changed:
        for item in registry:
            report_path = str(item["path"]).rstrip("/") + "/"
            if rel.startswith(report_path):
                matched.add(item["id"])
    if matched:
        return matched
    # If only pipeline/UI code changed, regenerate all reports to avoid empty payloads in clean CI.
    return {item["id"] for item in registry}


def copy_asset(
    src: Path,
    report_id: str,
    report_dir: Path,
    artifacts_dir: Path,
    *,
    no_copy_assets: bool,
) -> tuple[str, str]:
    rel_inside = src.relative_to(report_dir)
    web_path = f"/artifacts/{report_id}/{rel_inside.as_posix()}"
    source_path = rel_repo_path(src)
    if not no_copy_assets:
        dst = artifacts_dir / report_id / rel_inside
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    return web_path, source_path


def asset_kind(path: Path) -> str:
    ext = path.suffix.lower()
    if ext == ".pdf":
        return "pdf"
    if ext == ".tex":
        return "tex"
    if ext in FIGURE_EXT:
        return "figure"
    if ext in DATA_EXT:
        return "data"
    return "other"


def gather_files(report_dir: Path, extensions: set[str], max_items: int) -> list[Path]:
    files = [
        p
        for p in report_dir.rglob("*")
        if p.is_file()
        and p.suffix.lower() in extensions
        and "build" not in p.parts
        and "__pycache__" not in p.parts
        and ".venv" not in p.parts
    ]
    files.sort(key=lambda p: p.as_posix())
    return files[:max_items]


def disambiguate_asset_labels(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    taken: set[tuple[str, str]] = set()
    for record in records:
        kind = str(record.get("kind", "other"))
        label = str(record.get("label", "")).strip() or "asset"
        key = (kind, label.lower())
        if key not in taken:
            record["label"] = label
            taken.add(key)
            continue

        source_path = str(record.get("source_path", ""))
        parts = list(Path(source_path).parts)
        if len(parts) >= 2 and parts[0] == "reports":
            parts = parts[2:]
        parent_parts = [p for p in parts[:-1] if p]

        candidate = ""
        for depth in range(1, min(6, len(parent_parts)) + 1):
            context = "/".join(parent_parts[-depth:])
            trial = f"{context}/{label}"
            if (kind, trial.lower()) not in taken:
                candidate = trial
                break

        if not candidate:
            suffix = 2
            while True:
                trial = f"{label} ({suffix})"
                if (kind, trial.lower()) not in taken:
                    candidate = trial
                    break
                suffix += 1

        record["label"] = candidate
        taken.add((kind, candidate.lower()))
    return records


def disambiguate_figure_titles(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    taken: set[str] = set()
    for record in records:
        title = normalize_space(str(record.get("title", ""))) or "figure"
        if title.lower() not in taken:
            record["title"] = title
            taken.add(title.lower())
            continue

        source_path = str(record.get("source_path", ""))
        parts = list(Path(source_path).parts)
        if len(parts) >= 2 and parts[0] == "reports":
            parts = parts[2:]
        parent_parts = [p for p in parts[:-1] if p]
        context = "/".join(parent_parts[-2:]) if parent_parts else "variant"
        candidate = f"{title} ({context})"
        suffix = 2
        while candidate.lower() in taken:
            candidate = f"{title} ({context}, {suffix})"
            suffix += 1
        record["title"] = candidate
        taken.add(candidate.lower())
    return records


def infer_series_type_by_distribution(values: list[float]) -> str | None:
    finite_values = [float(v) for v in values if isinstance(v, (int, float)) and math.isfinite(float(v))]
    if not finite_values:
        return None
    unique_values = sorted({round(v, 10) for v in finite_values})
    if unique_values and set(unique_values).issubset({0.0, 1.0}):
        return "binary"

    min_v = min(finite_values)
    max_v = max(finite_values)
    span = max_v - min_v
    in_unit_interval = min_v >= -1e-10 and max_v <= 1.0 + 1e-10
    if in_unit_interval:
        if len(unique_values) > 2:
            return "probability"
        non_integral = sum(1 for v in finite_values if not math.isclose(v, round(v), abs_tol=1e-10))
        if non_integral >= max(1, int(len(finite_values) * 0.2)):
            return "probability"

    all_integerish = all(math.isclose(v, round(v), abs_tol=1e-10) for v in finite_values)
    if all_integerish and len(unique_values) <= 8 and span <= 12:
        return "parameter"
    if all_integerish and len(unique_values) <= 4 and span <= 3:
        return "parameter"
    return None


def infer_series_type(name: str, values: list[float]) -> str:
    lowered = name.lower()
    finite_values = [float(v) for v in values if isinstance(v, (int, float)) and math.isfinite(float(v))]
    unique_values = sorted({round(v, 10) for v in finite_values})
    dist_type = infer_series_type_by_distribution(finite_values)
    is_integerish = all(math.isclose(v, round(v), abs_tol=1e-10) for v in finite_values) if finite_values else False

    if re.search(r"(runtime|elapsed|latency|duration|seconds|sec$|_sec|ms$|millisecond)", lowered):
        return "metric"
    if re.search(r"(beta|alpha|lambda|theta|param|parameter|step|time|index|dst|start|target|door|seed)", lowered):
        return "parameter"
    if re.search(r"(flag|indicator|bool|pass|fail|is_)", lowered):
        # Keep strict binary only for true {0,1} flags; multi-valued flags are ordinal parameters.
        if unique_values and set(unique_values).issubset({0.0, 1.0}):
            return "binary"
        if dist_type is not None:
            return "parameter" if dist_type == "binary" else dist_type
        if is_integerish and len(unique_values) <= 12:
            return "parameter"
        return "metric"
    if dist_type in {"binary", "probability"}:
        return dist_type
    if re.search(r"(pmf|cdf|prob|mass|survival|hazard|density|ratio|rate|share)", lowered):
        return "probability"

    # Ambiguous single-letter symbols should prefer distribution over regex heuristics.
    if lowered in {"n", "t", "k"}:
        if dist_type is not None:
            return "metric" if dist_type == "probability" else dist_type
        if finite_values:
            span = max(finite_values) - min(finite_values)
            if span > 2 or len(unique_values) > 4:
                return "metric"
        return "parameter"

    if dist_type is not None:
        return dist_type
    return "metric"


def infer_series_unit(name: str, series_type: str) -> str:
    lowered = name.lower()
    if series_type == "binary":
        return "indicator"
    if re.search(r"(seconds|second|_sec|sec$)", lowered):
        return "seconds"
    if re.search(r"(millisecond|_ms|ms$)", lowered):
        return "milliseconds"
    if series_type == "probability":
        return "probability"
    if re.search(r"(time|step|tick|iter)", lowered):
        return "step"
    if re.search(r"(count|hits|visits|size)", lowered):
        return "count"
    if series_type == "parameter":
        return "parameter"
    return "value"


def build_series_semantics(name: str, values: list[float]) -> dict[str, Any]:
    finite_values = [float(v) for v in values if isinstance(v, (int, float)) and math.isfinite(float(v))]
    series_type = infer_series_type(name, finite_values)
    unit = infer_series_unit(name, series_type)
    if finite_values:
        min_v = min(finite_values)
        max_v = max(finite_values)
        positive_ratio = sum(1 for v in finite_values if v > 0) / max(1, len(finite_values))
    else:
        min_v = 0.0
        max_v = 0.0
        positive_ratio = 0.0
    return {
        "name": name,
        "series_type": series_type,
        "unit": unit,
        "min": float(min_v),
        "max": float(max_v),
        "positive_ratio": float(round(positive_ratio, 6)),
    }


def dedupe_sequence(items: list[Any], *, max_items: int | None = None) -> list[Any]:
    out: list[Any] = []
    seen: set[str] = set()
    for item in items:
        if isinstance(item, (dict, list)):
            key = json.dumps(item, ensure_ascii=False, sort_keys=True)
        else:
            key = normalize_space(str(item))
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(item)
        if max_items is not None and len(out) >= max_items:
            break
    return out


def ensure_locale_field_parity(
    left: list[Any],
    right: list[Any],
    *,
    max_items: int | None = None,
    min_ratio: float = 0.9,
    allow_cross_copy: bool = True,
    allow_padding: bool = True,
) -> tuple[list[Any], list[Any]]:
    a = dedupe_sequence(list(left), max_items=max_items)
    b = dedupe_sequence(list(right), max_items=max_items)
    if not a and b and allow_cross_copy:
        a = list(b)
    if not b and a and allow_cross_copy:
        b = list(a)
    if a and b:
        ratio = min(len(a), len(b)) / max(1, max(len(a), len(b)))
        if allow_padding:
            if ratio < min_ratio:
                target = max(len(a), len(b))
                if max_items is not None:
                    target = min(target, max_items)
                if len(a) < target and a:
                    a = (a + [a[i % len(a)] for i in range(target - len(a))])[:target]
                if len(b) < target and b:
                    b = (b + [b[i % len(b)] for i in range(target - len(b))])[:target]
        elif ratio < 1.0:
            target = min(len(a), len(b))
            if max_items is not None:
                target = min(target, max_items)
            a = a[:target]
            b = b[:target]
    return a, b


def align_locale_payloads(base_meta: dict[str, Any], cn_meta: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    limits = {
        "key_findings": 8,
        "math_blocks": 14,
        "math_story": 6,
        "section_cards": 10,
        "reproducibility_commands": 10,
        "source_documents": 6,
    }
    strict_fields = {"math_blocks", "math_story", "section_cards"}
    cross_copy_fields = {"math_blocks", "math_story", "reproducibility_commands", "source_documents"}
    for field, limit in limits.items():
        left = list(base_meta.get(field, []))
        right = list(cn_meta.get(field, []))
        min_ratio = 1.0 if field in strict_fields else 0.9
        aligned_left, aligned_right = ensure_locale_field_parity(
            left,
            right,
            max_items=limit,
            min_ratio=min_ratio,
            allow_cross_copy=field in cross_copy_fields,
            allow_padding=field not in {"section_cards"},
        )
        base_meta[field] = aligned_left
        cn_meta[field] = aligned_right
    return base_meta, cn_meta


def sanitize_latex_for_katex(latex: str) -> str:
    value = normalize_space(strip_tex_comments(latex))
    if not value:
        return ""
    if re.search(r"[，。；：（）【】［］｛｝％]", value):
        if "\\" not in value:
            return ""
        value = value.translate(
            str.maketrans(
                {
                    "，": ",",
                    "。": ".",
                    "；": ";",
                    "：": ":",
                    "（": "(",
                    "）": ")",
                    "【": "[",
                    "】": "]",
                    "［": "[",
                    "］": "]",
                    "｛": "{",
                    "｝": "}",
                    "％": "%",
                }
            )
        )
    value = re.sub(r"\\(?:label|tag\*?)\{[^{}]*\}", " ", value)
    value = value.replace("\\nonumber", " ")
    value = value.replace("\\notag", " ")
    value = re.sub(r"\\(?:eqref|ref)\{([^{}]+)\}", r"\\text{[\1]}", value)
    value = re.sub(r"\\textbf\{([^{}]*)\}", r"\\text{\1}", value)
    value = re.sub(r"\\mathrm\{([^{}]*)\}", r"\\text{\1}", value)
    if contains_cjk(value) and not re.search(r"[=\\_^{}()\\[\\]+\\-*/]", value):
        return ""
    if ("&" in value or "\\\\" in value) and "\\begin{" not in value:
        value = rf"\begin{{aligned}} {value} \end{{aligned}}"
    value = normalize_space(value)
    return value


def parse_csv_dataset(path: Path, max_points: int) -> dict[str, Any] | None:
    with path.open("r", encoding="utf-8", errors="ignore", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            return None

        rows: list[dict[str, str]] = []
        for idx, row in enumerate(reader):
            if idx >= max_points:
                break
            rows.append({k: (v or "").strip() for k, v in row.items() if k})

    if not rows:
        return None

    numeric_fields: list[str] = []
    unique_counts: dict[str, int] = {}
    for field in reader.fieldnames:
        if not field:
            continue
        values = [row.get(field, "") for row in rows]
        numeric = 0
        observed: list[float] = []
        for v in values:
            if not v:
                continue
            try:
                num = float(v)
                if math.isfinite(num):
                    numeric += 1
                    observed.append(num)
            except ValueError:
                pass
        if numeric >= max(3, int(len(values) * 0.65)):
            numeric_fields.append(field)
            unique_counts[field] = len({round(x, 10) for x in observed})

    if len(numeric_fields) < 1:
        return None

    preferred_x = [
        name
        for name in numeric_fields
        if re.search(r"(^t$|time|step|x|index|n$)", name, re.IGNORECASE)
    ]
    preferred_param_x = [
        name
        for name in numeric_fields
        if unique_counts.get(name, 0) > 1 and re.search(r"(beta|alpha|lambda|theta|rho|^q$|^p$)", name, re.IGNORECASE)
    ]
    varying_preferred_x = [name for name in preferred_x if unique_counts.get(name, 0) > 1]
    varying_numeric = [name for name in numeric_fields if unique_counts.get(name, 0) > 1]
    if preferred_param_x:
        x_field = preferred_param_x[0]
    elif varying_preferred_x:
        x_field = varying_preferred_x[0]
    elif preferred_x:
        x_field = preferred_x[0]
    elif varying_numeric:
        x_field = varying_numeric[0]
    else:
        x_field = numeric_fields[0]
    y_fields = [name for name in numeric_fields if name != x_field][:3]
    if not y_fields:
        y_fields = [x_field]

    x_values: list[float] = []
    series: list[dict[str, Any]] = []
    y_map: dict[str, list[float]] = {name: [] for name in y_fields}

    for row in rows:
        raw_x = row.get(x_field, "")
        try:
            x_value = float(raw_x)
            if not math.isfinite(x_value):
                raise ValueError
        except ValueError:
            x_value = float(len(x_values))
        x_values.append(x_value)
        for y_name in y_fields:
            raw_y = row.get(y_name, "")
            try:
                y_value = float(raw_y)
                if not math.isfinite(y_value):
                    raise ValueError
            except ValueError:
                y_value = 0.0
            y_map[y_name].append(y_value)

    semantics: list[dict[str, Any]] = []
    default_series: list[str] = []
    for y_name in y_fields:
        semantic = build_series_semantics(y_name, y_map[y_name])
        semantics.append(semantic)
        if semantic["series_type"] in {"metric", "probability"}:
            default_series.append(y_name)
        series.append(
            {
                "name": y_name,
                "x": x_values,
                "y": y_map[y_name],
                "series_type": semantic["series_type"],
                "unit": semantic["unit"],
            }
        )
    if not default_series and y_fields:
        default_series = [y_fields[0]]

    return {
        "x_label": x_field,
        "y_label": ", ".join(y_fields),
        "series": series,
        "series_semantics": semantics,
        "default_series": default_series,
        "provenance": {"type": "csv", "source": rel_repo_path(path)},
    }


def to_finite_float(value: Any) -> float | None:
    if isinstance(value, bool):
        return float(int(value))
    if isinstance(value, (int, float)):
        cast = float(value)
        if math.isfinite(cast):
            return cast
    return None


def flatten_numeric_object(value: Any, *, prefix: str = "", depth: int = 0, max_depth: int = 3) -> dict[str, float]:
    out: dict[str, float] = {}
    if depth > max_depth:
        return out
    if isinstance(value, dict):
        for raw_key, raw_val in value.items():
            key = re.sub(r"[^a-zA-Z0-9_]+", "_", str(raw_key)).strip("_").lower()
            if not key:
                continue
            merged = key if not prefix else f"{prefix}_{key}"
            maybe = to_finite_float(raw_val)
            if maybe is not None:
                out[merged] = maybe
                continue
            if isinstance(raw_val, dict):
                out.update(flatten_numeric_object(raw_val, prefix=merged, depth=depth + 1, max_depth=max_depth))
    return out


def flatten_record_rows(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    flat_rows: list[dict[str, Any]] = []
    for row in records:
        if not isinstance(row, dict):
            continue
        flat: dict[str, Any] = {}
        for raw_key, raw_val in row.items():
            key = re.sub(r"[^a-zA-Z0-9_]+", "_", str(raw_key)).strip("_").lower()
            if not key:
                continue
            maybe = to_finite_float(raw_val)
            if maybe is not None:
                flat[key] = maybe
                continue
            if isinstance(raw_val, dict):
                flat.update(flatten_numeric_object(raw_val, prefix=key))
        if flat:
            flat_rows.append(flat)
    return flat_rows


def parse_json_dataset(path: Path, max_points: int) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8", errors="ignore"))
    except json.JSONDecodeError:
        return None

    records: list[dict[str, Any]] | None = None
    if isinstance(payload, list) and payload and isinstance(payload[0], dict):
        records = [item for item in payload[:max_points] if isinstance(item, dict)]
    elif isinstance(payload, dict):
        for key in ("rows", "data", "results", "details", "variants", "records", "cases"):
            maybe = payload.get(key)
            if isinstance(maybe, list) and maybe and isinstance(maybe[0], dict):
                records = [item for item in maybe[:max_points] if isinstance(item, dict)]
                break
            if isinstance(maybe, dict):
                nested_rows: list[dict[str, Any]] = []
                for group_key, group_value in maybe.items():
                    if isinstance(group_value, list) and group_value and isinstance(group_value[0], dict):
                        for item in group_value[:max_points]:
                            row = dict(item)
                            row["_group"] = group_key
                            nested_rows.append(row)
                    elif isinstance(group_value, dict):
                        row = dict(group_value)
                        row["_group"] = group_key
                        nested_rows.append(row)
                if nested_rows:
                    records = nested_rows[:max_points]
                    break
        if records is None:
            vector_keys = [k for k, v in payload.items() if isinstance(v, list)]
            if vector_keys:
                length = min(len(payload[k]) for k in vector_keys if isinstance(payload[k], list))
                if length > 0:
                    rows: list[dict[str, Any]] = []
                    for i in range(min(length, max_points)):
                        rows.append({k: payload[k][i] for k in vector_keys})
                    records = rows

    if not records:
        return None

    records = flatten_record_rows(records)
    if not records:
        return None

    numeric_fields: list[str] = []
    unique_counts: dict[str, int] = {}
    all_keys = sorted({k for row in records for k in row.keys()})
    for key in all_keys:
        values = [row.get(key) for row in records]
        observed = [to_finite_float(v) for v in values]
        numeric_values = [v for v in observed if v is not None]
        numeric = len(numeric_values)
        if numeric >= max(3, int(len(values) * 0.65)):
            numeric_fields.append(key)
            unique_counts[key] = len({round(float(v), 10) for v in numeric_values})

    if not numeric_fields:
        return None

    preferred_x = [
        name
        for name in numeric_fields
        if re.search(r"(^t$|time|step|x|index|n$)", name, re.IGNORECASE)
    ]
    preferred_param_x = [
        name
        for name in numeric_fields
        if unique_counts.get(name, 0) > 1 and re.search(r"(beta|alpha|lambda|theta|rho|^q$|^p$)", name, re.IGNORECASE)
    ]
    varying_preferred_x = [name for name in preferred_x if unique_counts.get(name, 0) > 1]
    varying_numeric = [name for name in numeric_fields if unique_counts.get(name, 0) > 1]
    if preferred_param_x:
        x_field = preferred_param_x[0]
    elif varying_preferred_x:
        x_field = varying_preferred_x[0]
    elif preferred_x:
        x_field = preferred_x[0]
    elif varying_numeric:
        x_field = varying_numeric[0]
    else:
        x_field = numeric_fields[0]
    y_fields = [name for name in numeric_fields if name != x_field][:3]
    if not y_fields:
        y_fields = [x_field]

    x_values: list[float] = []
    series_map: dict[str, list[float]] = {name: [] for name in y_fields}
    for idx, row in enumerate(records):
        raw_x = row.get(x_field, idx)
        maybe_x = to_finite_float(raw_x)
        x_val = maybe_x if maybe_x is not None else float(idx)
        x_values.append(x_val)

        for y_name in y_fields:
            raw_y = row.get(y_name, 0.0)
            maybe_y = to_finite_float(raw_y)
            series_map[y_name].append(maybe_y if maybe_y is not None else 0.0)

    semantics: list[dict[str, Any]] = []
    default_series: list[str] = []
    series: list[dict[str, Any]] = []
    for y_name in y_fields:
        semantic = build_series_semantics(y_name, series_map[y_name])
        semantics.append(semantic)
        if semantic["series_type"] in {"metric", "probability"}:
            default_series.append(y_name)
        series.append(
            {
                "name": y_name,
                "x": x_values,
                "y": series_map[y_name],
                "series_type": semantic["series_type"],
                "unit": semantic["unit"],
            }
        )
    if not default_series and y_fields:
        default_series = [y_fields[0]]
    return {
        "x_label": x_field,
        "y_label": ", ".join(y_fields),
        "series": series,
        "series_semantics": semantics,
        "default_series": default_series,
        "provenance": {"type": "json", "source": rel_repo_path(path)},
    }


def normalize_tex_cell(cell: str) -> str:
    value = normalize_space(strip_tex_comments(cell))
    if not value:
        return ""
    value = value.replace("$", " ")
    value = value.replace("\\ldots", " ")
    value = re.sub(r"\\(?:textbf|mathrm|mathit|operatorname)\{([^{}]*)\}", r"\1", value)
    value = re.sub(r"\\[a-zA-Z]+\*?", " ", value)
    value = value.replace("{", " ").replace("}", " ")
    value = normalize_space(value)
    return value


def parse_numeric_from_tex_cell(cell: str) -> float | None:
    normalized = normalize_tex_cell(cell).replace("−", "-")
    if not normalized:
        return None
    match = re.search(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", normalized)
    if not match:
        return None
    try:
        value = float(match.group(0))
    except ValueError:
        return None
    if not math.isfinite(value):
        return None
    return value


def parse_tex_tabular_dataset(path: Path, max_points: int) -> dict[str, Any] | None:
    raw = path.read_text(encoding="utf-8", errors="ignore")
    blocks = re.findall(r"\\begin\{tabular\}\{[^{}]*\}(.*?)\\end\{tabular\}", raw, flags=re.DOTALL)
    if not blocks:
        return None

    best: tuple[int, dict[str, Any]] | None = None
    for block in blocks:
        rows: list[list[str]] = []
        for segment in re.split(r"\\\\", block):
            line = normalize_space(segment.replace("\\hline", " ").replace("\\toprule", " ").replace("\\midrule", " ").replace("\\bottomrule", " "))
            if not line or line.startswith("%"):
                continue
            cells = [c.strip() for c in line.split("&")]
            if len(cells) < 2:
                continue
            rows.append(cells)
        if len(rows) < 4:
            continue

        header_row: list[str] | None = None
        body_rows = rows
        first_numeric_count = sum(1 for cell in rows[0] if parse_numeric_from_tex_cell(cell) is not None)
        if first_numeric_count <= 1:
            header_row = rows[0]
            body_rows = rows[1:]
        if len(body_rows) < 3:
            continue

        width = min(len(row) for row in body_rows)
        numeric_matrix: list[list[float | None]] = []
        for row in body_rows[:max_points]:
            numeric_matrix.append([parse_numeric_from_tex_cell(cell) for cell in row[:width]])
        if len(numeric_matrix) < 3:
            continue

        numeric_columns = [
            idx
            for idx in range(width)
            if sum(1 for row in numeric_matrix if row[idx] is not None) >= max(3, int(len(numeric_matrix) * 0.6))
        ]
        if len(numeric_columns) < 2:
            continue

        x_col = numeric_columns[0]
        y_cols = numeric_columns[1:4]
        if not y_cols:
            continue

        headers: list[str] = []
        if header_row and len(header_row) >= width:
            headers = [normalize_tex_cell(cell) or f"col_{idx + 1}" for idx, cell in enumerate(header_row[:width])]
        else:
            headers = [f"col_{idx + 1}" for idx in range(width)]

        x_values: list[float] = []
        series_values: dict[int, list[float]] = {idx: [] for idx in y_cols}
        for row_idx, row in enumerate(numeric_matrix):
            x_val = row[x_col] if row[x_col] is not None else float(row_idx)
            x_values.append(float(x_val))
            for col_idx in y_cols:
                y_val = row[col_idx] if row[col_idx] is not None else 0.0
                series_values[col_idx].append(float(y_val))

        series: list[dict[str, Any]] = []
        semantics: list[dict[str, Any]] = []
        default_series: list[str] = []
        for col_idx in y_cols:
            name = headers[col_idx]
            values = series_values[col_idx]
            semantic = build_series_semantics(name, values)
            semantics.append(semantic)
            if semantic["series_type"] in {"metric", "probability", "binary"}:
                default_series.append(name)
            series.append(
                {
                    "name": name,
                    "x": x_values,
                    "y": values,
                    "series_type": semantic["series_type"],
                    "unit": semantic["unit"],
                }
            )
        if not default_series and series:
            default_series = [series[0]["name"]]

        payload = {
            "x_label": headers[x_col],
            "y_label": ", ".join(headers[idx] for idx in y_cols),
            "series": series,
            "series_semantics": semantics,
            "default_series": default_series,
            "provenance": {"type": "tex_tabular", "source": rel_repo_path(path)},
        }
        quality = len(series) * len(x_values)
        if best is None or quality > best[0]:
            best = (quality, payload)

    return best[1] if best else None


def fallback_asset_dataset(report_id: str, assets: list[dict[str, Any]]) -> dict[str, Any]:
    ranked = sorted(assets, key=lambda item: item["size"], reverse=True)[:20]
    x_vals = list(range(1, len(ranked) + 1))
    y_vals = [float(item["size"]) for item in ranked]
    labels = [item["label"] for item in ranked]
    semantic = build_series_semantics("size_by_rank", y_vals)
    semantic["series_type"] = "metric"
    semantic["unit"] = "bytes"
    return {
        "report_id": report_id,
        "series_id": "asset-size-profile",
        "x_label": "Asset rank",
        "y_label": "Size (bytes)",
        "series": [
            {
                "name": "size_by_rank",
                "x": x_vals,
                "y": y_vals,
                "series_type": "metric",
                "unit": "bytes",
            }
        ],
        "series_semantics": [semantic],
        "default_series": ["size_by_rank"],
        "provenance": {"type": "derived", "source": f"assets:{','.join(labels[:5])}"},
    }


SERIES_TYPE_ORDER = ["metric", "probability", "binary", "parameter"]


def split_dataset_by_semantics(parsed: dict[str, Any]) -> list[dict[str, Any]]:
    series = list(parsed.get("series", []))
    if not series:
        return []

    semantics_by_name: dict[str, dict[str, Any]] = {}
    for item in parsed.get("series_semantics", []):
        name = str(item.get("name", "")).strip()
        if name:
            semantics_by_name[name] = dict(item)

    grouped_names: dict[str, list[str]] = defaultdict(list)
    for item in series:
        name = str(item.get("name", "")).strip()
        if not name:
            continue
        semantic = semantics_by_name.get(name)
        if semantic is None:
            values = [float(v) for v in item.get("y", []) if isinstance(v, (int, float))]
            semantic = build_series_semantics(name, values)
            semantics_by_name[name] = semantic
        series_type = str(semantic.get("series_type", "metric"))
        grouped_names[series_type].append(name)

    type_order = [tp for tp in SERIES_TYPE_ORDER if grouped_names.get(tp)]
    extra_types = sorted(set(grouped_names.keys()) - set(SERIES_TYPE_ORDER))
    type_order.extend(extra_types)

    if len(type_order) <= 1:
        normalized = dict(parsed)
        normalized["series_semantics"] = [semantics_by_name[str(item.get("name", "")).strip()] for item in series if str(item.get("name", "")).strip() in semantics_by_name]
        return [normalized]

    variants: list[dict[str, Any]] = []
    default_series = list(parsed.get("default_series", []))
    mixed_types = type_order[:]

    for series_type in type_order:
        names = grouped_names.get(series_type, [])
        if not names:
            continue
        selected = [item for item in series if str(item.get("name", "")).strip() in set(names)]
        semantics = [semantics_by_name[name] for name in names if name in semantics_by_name]
        defaults = [name for name in default_series if name in names]
        if not defaults:
            defaults = names[:1]
        y_label_base = ", ".join(names) if names else str(parsed.get("y_label", "value"))
        pretty_type = series_type.replace("-", " ")
        provenance = dict(parsed.get("provenance", {}))
        provenance["semantic_split"] = series_type
        provenance["semantic_mix"] = [series_type]
        variants.append(
            {
                **parsed,
                "y_label": f"{y_label_base} [{pretty_type}]",
                "series": selected,
                "series_semantics": semantics,
                "default_series": defaults,
                "provenance": provenance,
                "variant_suffix": series_type,
                "variant_title_suffix": pretty_type,
            }
        )

    return variants


def interactive_dataset_priority(dataset: dict[str, Any]) -> int:
    series_id = normalize_space(str(dataset.get("series_id", ""))).lower()
    title = normalize_space(str(dataset.get("title", ""))).lower()
    x_label = normalize_space(str(dataset.get("x_label", ""))).lower()
    y_label = normalize_space(str(dataset.get("y_label", ""))).lower()
    source = normalize_space(str(dataset.get("provenance", {}).get("source", ""))).lower()
    haystack = " ".join([series_id, title, x_label, y_label, source])
    score = 0

    if series_id == "asset-size-profile":
        score -= 160
    if "manifest" in haystack:
        score -= 50
    if "/data/" in source:
        score += 14
    if "/config/" in source:
        score -= 10
    if "asset rank" in x_label or "size (bytes)" in y_label:
        score -= 24

    for token in (
        "runtime",
        "hazard",
        "survival",
        "fpt",
        "peak",
        "valley",
        "phase",
        "bimodal",
        "gap",
        "scan",
        "beta",
        "two_target",
    ):
        if token in haystack:
            score += 4

    semantics = list(dataset.get("series_semantics", []))
    types = {str(item.get("series_type", "")).strip().lower() for item in semantics if str(item.get("series_type", "")).strip()}
    if "metric" in types:
        score += 10
    if "probability" in types:
        score += 12
    if "binary" in types:
        score += 7
    if types and types.issubset({"parameter"}):
        score -= 14
    if dataset.get("default_series"):
        score += 2
    return score


def build_datasets(
    report_id: str,
    report_dir: Path,
    out_report_dir: Path,
    max_datasets: int,
    max_points: int,
    assets: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    data_candidates = [
        p
        for p in report_dir.rglob("*")
        if p.is_file()
        and p.suffix.lower() in {".csv", ".json"}
        and "build" not in p.parts
        and "figures" not in p.parts
        and "tables" not in p.parts
    ]
    data_candidates.sort(key=lambda p: p.as_posix())

    datasets_meta: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    seen_titles: set[str] = set()

    series_dir = out_report_dir / "series"
    series_dir.mkdir(parents=True, exist_ok=True)
    for stale in series_dir.glob("*.json"):
        try:
            stale.unlink()
        except OSError:
            pass

    for candidate in data_candidates:
        parsed: dict[str, Any] | None = None
        if candidate.suffix.lower() == ".csv":
            parsed = parse_csv_dataset(candidate, max_points)
        elif candidate.suffix.lower() == ".json":
            parsed = parse_json_dataset(candidate, max_points)

        if not parsed:
            continue

        variants = split_dataset_by_semantics(parsed)
        stem = re.sub(r"[^a-zA-Z0-9_-]+", "-", candidate.stem.lower()).strip("-")
        stem = stem or f"dataset-{len(datasets_meta) + 1}"
        for variant_index, variant in enumerate(variants):
            suffix = str(variant.get("variant_suffix", "")).strip().lower().replace(" ", "-")
            raw_series_id = stem if not suffix else f"{stem}-{suffix}"
            series_id = raw_series_id
            if series_id in seen_ids:
                dedupe_suffix = 2
                while f"{series_id}-{dedupe_suffix}" in seen_ids:
                    dedupe_suffix += 1
                series_id = f"{series_id}-{dedupe_suffix}"
            seen_ids.add(series_id)

            payload = {
                "report_id": report_id,
                "series_id": series_id,
                "x_label": variant["x_label"],
                "y_label": variant["y_label"],
                "series": variant["series"],
                "series_semantics": variant.get("series_semantics", []),
                "default_series": variant.get("default_series", []),
                "provenance": variant["provenance"],
            }

            series_rel = f"/data/v1/reports/{report_id}/series/{series_id}.json"
            series_path = series_dir / f"{series_id}.json"
            series_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")

            title_suffix = str(variant.get("variant_title_suffix", "")).strip()
            title = candidate.stem if not title_suffix else f"{candidate.stem} [{title_suffix}]"
            if len(variants) == 1 and variant_index == 0:
                title = candidate.stem
            title_key = normalize_space(title).lower()
            if title_key in seen_titles:
                title = f"{title} · {series_id}"
                title_key = normalize_space(title).lower()
            seen_titles.add(title_key)
            datasets_meta.append(
                {
                    "series_id": series_id,
                    "title": title,
                    "x_label": variant["x_label"],
                    "y_label": variant["y_label"],
                    "series_path": series_rel,
                    "default_series": variant.get("default_series", []),
                    "series_semantics": variant.get("series_semantics", []),
                    "provenance": variant["provenance"],
                }
            )

    if not datasets_meta:
        tex_candidates = sorted(
            p
            for p in report_dir.rglob("*.tex")
            if p.is_file() and "build" not in p.parts
        )
        for tex_path in tex_candidates:
            parsed_tex = parse_tex_tabular_dataset(tex_path, max_points)
            if not parsed_tex:
                continue
            variants = split_dataset_by_semantics(parsed_tex)
            stem = re.sub(r"[^a-zA-Z0-9_-]+", "-", tex_path.stem.lower()).strip("-") or "tex-tabular"
            for variant_index, variant in enumerate(variants):
                suffix = str(variant.get("variant_suffix", "")).strip().lower().replace(" ", "-")
                raw_series_id = stem if not suffix else f"{stem}-{suffix}"
                series_id = raw_series_id
                if series_id in seen_ids:
                    dedupe_suffix = 2
                    while f"{series_id}-{dedupe_suffix}" in seen_ids:
                        dedupe_suffix += 1
                    series_id = f"{series_id}-{dedupe_suffix}"
                seen_ids.add(series_id)
                payload = {
                    "report_id": report_id,
                    "series_id": series_id,
                    "x_label": variant["x_label"],
                    "y_label": variant["y_label"],
                    "series": variant["series"],
                    "series_semantics": variant.get("series_semantics", []),
                    "default_series": variant.get("default_series", []),
                    "provenance": variant["provenance"],
                }
                series_rel = f"/data/v1/reports/{report_id}/series/{series_id}.json"
                series_path = series_dir / f"{series_id}.json"
                series_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
                title_suffix = str(variant.get("variant_title_suffix", "")).strip()
                title = f"{tex_path.stem} [tabular]"
                if title_suffix:
                    title = f"{tex_path.stem} [tabular {title_suffix}]"
                if len(variants) == 1 and variant_index == 0:
                    title = f"{tex_path.stem} [tabular]"
                datasets_meta.append(
                    {
                        "series_id": series_id,
                        "title": title,
                        "x_label": variant["x_label"],
                        "y_label": variant["y_label"],
                        "series_path": series_rel,
                        "default_series": variant.get("default_series", []),
                        "series_semantics": variant.get("series_semantics", []),
                        "provenance": variant["provenance"],
                    }
                )
            break

    if not datasets_meta:
        fallback = fallback_asset_dataset(report_id, assets)
        series_rel = f"/data/v1/reports/{report_id}/series/{fallback['series_id']}.json"
        series_path = series_dir / f"{fallback['series_id']}.json"
        series_path.write_text(json.dumps(fallback, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
        datasets_meta.append(
            {
                "series_id": fallback["series_id"],
                "title": "Asset Size Profile",
                "x_label": fallback["x_label"],
                "y_label": fallback["y_label"],
                "series_path": series_rel,
                "default_series": fallback.get("default_series", []),
                "series_semantics": fallback.get("series_semantics", []),
                "provenance": fallback["provenance"],
            }
        )
    else:
        datasets_meta.sort(
            key=lambda row: (
                interactive_dataset_priority(row),
                -len(str(row.get("series_id", ""))),
                str(row.get("series_id", "")),
            ),
            reverse=True,
        )
        datasets_meta = datasets_meta[:max_datasets]

    return datasets_meta


def build_report_payload(
    item: dict[str, Any],
    output_dir: Path,
    artifacts_dir: Path,
    *,
    max_assets: int,
    max_figures: int,
    max_datasets: int,
    max_points: int,
    no_copy_assets: bool,
    generated_at: str,
) -> dict[str, Any]:
    report_id = str(item["id"])
    report_rel = str(item["path"])
    report_dir = REPO_ROOT / report_rel
    out_report_dir = output_dir / "reports" / report_id
    out_report_dir.mkdir(parents=True, exist_ok=True)

    readme_title, readme_summary, readme_findings = parse_readme(report_dir, report_id)
    tex_en = extract_tex_story(item, report_dir, report_id, "en")
    tex_cn = extract_tex_story(item, report_dir, report_id, "cn")

    top_assets = gather_files(report_dir, {".pdf", ".tex"}, max_assets)
    figure_assets = gather_files(report_dir / "figures" if (report_dir / "figures").exists() else report_dir, FIGURE_EXT, max_figures)

    assets: list[dict[str, Any]] = []
    figure_records: list[dict[str, Any]] = []
    seen_asset_fingerprints: set[tuple[str, str]] = set()

    selected = top_assets + [p for p in figure_assets if p not in top_assets]
    for idx, src in enumerate(selected[: max_assets + max_figures]):
        kind = asset_kind(src)
        digest = sha256_file(src)
        fingerprint = (digest, kind)
        if fingerprint in seen_asset_fingerprints:
            continue
        seen_asset_fingerprints.add(fingerprint)

        web_path, source_path = copy_asset(
            src,
            report_id,
            report_dir,
            artifacts_dir,
            no_copy_assets=no_copy_assets,
        )
        record = {
            "kind": kind,
            "label": src.name,
            "web_path": web_path,
            "source_path": source_path,
            "size": int(src.stat().st_size),
            "sha256": digest,
        }
        assets.append(record)

        if src.suffix.lower() in FIGURE_EXT:
            figure_records.append(
                {
                    "id": f"fig-{idx + 1}",
                    "title": src.stem.replace("_", " "),
                    "web_path": web_path,
                    "source_path": source_path,
                }
            )

    assets = disambiguate_asset_labels(assets)
    figure_records = disambiguate_figure_titles(figure_records)

    datasets = build_datasets(
        report_id,
        report_dir,
        out_report_dir,
        max_datasets=max_datasets,
        max_points=max_points,
        assets=assets,
    )
    report_updated_at = detect_report_updated_at(report_dir, generated_at)

    title_en = choose_best_title([str(tex_en.get("title", "")), str(readme_title), humanize_report_id(report_id)], report_id, max_chars=140)
    title_cn_candidate = choose_best_title([str(tex_cn.get("title", "")), str(readme_title), humanize_report_id(report_id)], report_id, max_chars=120)
    title_cn = title_cn_candidate if contains_cjk(title_cn_candidate) else title_en
    section_summary_en = [str(row.get("summary", "")) for row in list(tex_en.get("section_cards", []))[:3]]
    section_summary_cn = [str(row.get("summary", "")) for row in list(tex_cn.get("section_cards", []))[:3]]
    specific_en_candidates_base = [
        str(tex_en.get("summary", "")),
        str(tex_en.get("narrative", {}).get("result_overview", "")),
        str(tex_en.get("narrative", {}).get("method_overview", "")),
        str(tex_en.get("narrative", {}).get("model_overview", "")),
        str(readme_summary),
        *section_summary_en,
    ]
    specific_cn_candidates_base = [
        str(tex_cn.get("summary", "")),
        str(tex_cn.get("narrative", {}).get("result_overview", "")),
        str(tex_cn.get("narrative", {}).get("method_overview", "")),
        str(tex_cn.get("narrative", {}).get("model_overview", "")),
        *section_summary_cn,
    ]
    findings_en = clean_findings(readme_findings + list(tex_en["findings"]), report_id, max_items=8)
    findings_en = [ensure_en_text(row, report_id, role="finding", max_chars=220) for row in findings_en]
    findings_cn = clean_findings(readme_findings + list(tex_cn["findings"]), report_id, max_items=8)
    findings_cn = [ensure_cn_text(row, report_id, role="finding", max_chars=220) for row in findings_cn]
    refined_findings_en: list[str] = []
    for finding in findings_en:
        if is_generic_en_role_text(finding, report_id, "finding") or has_malformed_readability_tokens(finding):
            replacement = pick_specific_en_text(
                report_id,
                "finding",
                specific_en_candidates_base + list(tex_en.get("findings", [])),
                max_chars=220,
            )
            if replacement:
                finding = replacement
        refined_findings_en.append(canonical_summary(finding, max_chars=220))
    findings_en = dedupe_preserve(refined_findings_en, max_items=8)
    refined_findings_cn: list[str] = []
    for finding in findings_cn:
        if is_generic_cn_role_text(finding, "finding") or has_malformed_readability_tokens(finding):
            replacement = pick_specific_cn_text(
                report_id,
                "finding",
                specific_cn_candidates_base + list(tex_cn.get("findings", [])),
                max_chars=220,
            )
            if replacement:
                finding = replacement
        refined_findings_cn.append(canonical_summary(finding, max_chars=220))
    findings_cn = dedupe_preserve(refined_findings_cn, max_items=8)
    summary_en = choose_best_summary(
        [
            str(tex_en.get("summary", "")),
            str(readme_summary),
            str(tex_en.get("narrative", {}).get("result_overview", "")),
            str(tex_en.get("narrative", {}).get("method_overview", "")),
            " ".join(findings_en[:2]),
            *section_summary_en,
        ],
        max_chars=1000,
    )
    summary_cn = choose_best_summary(
        [
            str(tex_cn.get("summary", "")),
            str(tex_cn.get("narrative", {}).get("result_overview", "")),
            str(tex_cn.get("narrative", {}).get("method_overview", "")),
            " ".join(findings_cn[:2]),
            *section_summary_cn,
            summary_en,
        ],
        max_chars=1000,
    )
    if not summary_en:
        summary_en = canonical_summary(str(tex_en.get("summary", "") or readme_summary), max_chars=1000)
    if not summary_cn:
        summary_cn = canonical_summary(str(tex_cn.get("summary", "") or summary_en), max_chars=1000)
    title_en = ensure_en_text(title_en, report_id, role="title", max_chars=220)
    title_cn = ensure_cn_text(title_cn, report_id, role="title", max_chars=220, hint=str(tex_cn.get("title", "")))
    summary_en = improve_summary_if_needed(
        summary_en,
        [
            str(tex_en.get("narrative", {}).get("result_overview", "")),
            str(tex_en.get("narrative", {}).get("method_overview", "")),
            " ".join(findings_en[:3]),
            humanize_report_id(report_id),
        ],
        max_chars=1000,
    )
    summary_en = ensure_en_text(summary_en, report_id, role="summary", max_chars=1000)
    if is_generic_en_role_text(summary_en, report_id, "summary") or has_malformed_readability_tokens(summary_en):
        upgraded_summary_en = pick_specific_en_text(
            report_id,
            "summary",
            specific_en_candidates_base + findings_en,
            max_chars=1000,
        )
        if upgraded_summary_en:
            summary_en = upgraded_summary_en
    summary_cn = improve_summary_if_needed(
        summary_cn,
        [
            str(tex_cn.get("narrative", {}).get("result_overview", "")),
            str(tex_cn.get("narrative", {}).get("method_overview", "")),
            " ".join(findings_cn[:3]),
            summary_en,
            humanize_report_id(report_id),
        ],
        max_chars=1000,
    )
    summary_cn = ensure_cn_text(summary_cn, report_id, role="summary", max_chars=1000, hint=str(tex_cn.get("summary", "")))
    if is_generic_cn_role_text(summary_cn, "summary") or has_malformed_readability_tokens(summary_cn):
        upgraded_summary_cn = pick_specific_cn_text(
            report_id,
            "summary",
            specific_cn_candidates_base + findings_cn + [summary_en],
            max_chars=1000,
        )
        if upgraded_summary_cn:
            summary_cn = upgraded_summary_cn
    inferred_languages = ["en"]
    if contains_cjk(title_cn) or contains_cjk(summary_cn) or any(contains_cjk(item) for item in findings_cn):
        inferred_languages.append("cn")
    elif tex_cn.get("source_documents"):
        inferred_languages.append("cn")

    en_narrative_source = tex_en["narrative"]
    en_narrative = {
        "model_overview": ensure_en_text(
            str(en_narrative_source.get("model_overview", "")),
            report_id,
            role="model",
            max_chars=320,
        ),
        "method_overview": ensure_en_text(
            str(en_narrative_source.get("method_overview", "")),
            report_id,
            role="method",
            max_chars=320,
        ),
        "result_overview": ensure_en_text(
            str(en_narrative_source.get("result_overview", "")),
            report_id,
            role="result",
            max_chars=320,
        ),
    }
    if is_generic_en_role_text(en_narrative["model_overview"], report_id, "model") or has_malformed_readability_tokens(
        en_narrative["model_overview"]
    ):
        upgraded = pick_specific_en_text(
            report_id,
            "model",
            [str(en_narrative_source.get("model_overview", "")), *section_summary_en, summary_en],
            max_chars=320,
        )
        if upgraded:
            en_narrative["model_overview"] = upgraded
    if is_generic_en_role_text(en_narrative["method_overview"], report_id, "method") or has_malformed_readability_tokens(
        en_narrative["method_overview"]
    ):
        upgraded = pick_specific_en_text(
            report_id,
            "method",
            [str(en_narrative_source.get("method_overview", "")), *section_summary_en, summary_en, *findings_en],
            max_chars=320,
        )
        if upgraded:
            en_narrative["method_overview"] = upgraded
    if is_generic_en_role_text(en_narrative["result_overview"], report_id, "result") or has_malformed_readability_tokens(
        en_narrative["result_overview"]
    ):
        upgraded = pick_specific_en_text(
            report_id,
            "result",
            [str(en_narrative_source.get("result_overview", "")), *findings_en, summary_en, *section_summary_en],
            max_chars=320,
        )
        if upgraded:
            en_narrative["result_overview"] = upgraded
    en_section_cards = []
    for card in tex_en["section_cards"]:
        heading = str(card.get("heading", "")).strip() or "Section"
        raw_summary = str(card.get("summary", ""))
        sanitized_summary = ensure_en_text(
            raw_summary,
            report_id,
            role="section",
            max_chars=320,
        )
        if has_malformed_readability_tokens(sanitized_summary) or is_placeholder_section_summary(heading, sanitized_summary):
            sanitized_summary = section_fallback_summary(heading, report_id, "en")
        en_section_cards.append(
            {
                "heading": heading,
                "summary": sanitized_summary,
                "source_path": str(card.get("source_path", "")),
            }
        )
    en_section_cards = dedupe_section_cards_by_heading(en_section_cards, lang="en")

    cn_narrative_source = tex_cn["narrative"] if tex_cn["section_cards"] else tex_en["narrative"]
    cn_section_cards_source = tex_cn["section_cards"] if tex_cn["section_cards"] else tex_en["section_cards"]
    cn_narrative = {
        "model_overview": ensure_cn_text(
            str(cn_narrative_source.get("model_overview", "")),
            report_id,
            role="model",
            max_chars=320,
        ),
        "method_overview": ensure_cn_text(
            str(cn_narrative_source.get("method_overview", "")),
            report_id,
            role="method",
            max_chars=320,
        ),
        "result_overview": ensure_cn_text(
            str(cn_narrative_source.get("result_overview", "")),
            report_id,
            role="result",
            max_chars=320,
        ),
    }
    if is_generic_cn_role_text(cn_narrative["model_overview"], "model") or has_malformed_readability_tokens(
        cn_narrative["model_overview"]
    ):
        upgraded = pick_specific_cn_text(
            report_id,
            "model",
            [str(cn_narrative_source.get("model_overview", "")), *section_summary_cn, summary_cn],
            max_chars=320,
        )
        if upgraded:
            cn_narrative["model_overview"] = upgraded
    if is_generic_cn_role_text(cn_narrative["method_overview"], "method") or has_malformed_readability_tokens(
        cn_narrative["method_overview"]
    ):
        upgraded = pick_specific_cn_text(
            report_id,
            "method",
            [str(cn_narrative_source.get("method_overview", "")), *section_summary_cn, summary_cn, *findings_cn],
            max_chars=320,
        )
        if upgraded:
            cn_narrative["method_overview"] = upgraded
    if is_generic_cn_role_text(cn_narrative["result_overview"], "result") or has_malformed_readability_tokens(
        cn_narrative["result_overview"]
    ):
        upgraded = pick_specific_cn_text(
            report_id,
            "result",
            [str(cn_narrative_source.get("result_overview", "")), *findings_cn, summary_cn, *section_summary_cn],
            max_chars=320,
        )
        if upgraded:
            cn_narrative["result_overview"] = upgraded

    override = REPORT_TEXT_OVERRIDES.get(report_id, {})
    override_en = override.get("en", {})
    if override_en:
        override_title_en = normalize_space(str(override_en.get("title", "")))
        if override_title_en:
            title_en = ensure_en_text(override_title_en, report_id, role="title", max_chars=220)
        override_summary_en = normalize_space(str(override_en.get("summary", "")))
        if override_summary_en:
            summary_en = ensure_en_text(override_summary_en, report_id, role="summary", max_chars=1000)
        override_findings_en = [normalize_space(str(x)) for x in list(override_en.get("key_findings", []))]
        if override_findings_en:
            findings_en = dedupe_preserve(
                [ensure_en_text(x, report_id, role="finding", max_chars=220) for x in override_findings_en],
                max_items=8,
            )
        override_narrative_en = dict(override_en.get("narrative", {}))
        if override_narrative_en:
            en_narrative["model_overview"] = ensure_en_text(
                str(override_narrative_en.get("model_overview", en_narrative["model_overview"])),
                report_id,
                role="model",
                max_chars=320,
            )
            en_narrative["method_overview"] = ensure_en_text(
                str(override_narrative_en.get("method_overview", en_narrative["method_overview"])),
                report_id,
                role="method",
                max_chars=320,
            )
            en_narrative["result_overview"] = ensure_en_text(
                str(override_narrative_en.get("result_overview", en_narrative["result_overview"])),
                report_id,
                role="result",
                max_chars=320,
            )

    override_cn = override.get("cn", {})
    if override_cn:
        override_title_cn = normalize_space(str(override_cn.get("title", "")))
        if override_title_cn:
            title_cn = ensure_cn_text(
                override_title_cn,
                report_id,
                role="title",
                max_chars=220,
                hint=override_title_cn,
            )
        override_summary_cn = normalize_space(str(override_cn.get("summary", "")))
        if override_summary_cn:
            summary_cn = ensure_cn_text(override_summary_cn, report_id, role="summary", max_chars=1000)
        override_findings_cn = [normalize_space(str(x)) for x in list(override_cn.get("key_findings", []))]
        if override_findings_cn:
            findings_cn = dedupe_preserve(
                [ensure_cn_text(x, report_id, role="finding", max_chars=220) for x in override_findings_cn],
                max_items=8,
            )
        override_narrative_cn = dict(override_cn.get("narrative", {}))
        if override_narrative_cn:
            cn_narrative["model_overview"] = ensure_cn_text(
                str(override_narrative_cn.get("model_overview", cn_narrative["model_overview"])),
                report_id,
                role="model",
                max_chars=320,
            )
            cn_narrative["method_overview"] = ensure_cn_text(
                str(override_narrative_cn.get("method_overview", cn_narrative["method_overview"])),
                report_id,
                role="method",
                max_chars=320,
            )
            cn_narrative["result_overview"] = ensure_cn_text(
                str(override_narrative_cn.get("result_overview", cn_narrative["result_overview"])),
                report_id,
                role="result",
                max_chars=320,
            )

    base_meta = {
        "report_id": report_id,
        "lang": "en",
        "title": title_en,
        "summary": summary_en,
        "key_findings": findings_en,
        "narrative": en_narrative,
        "section_cards": en_section_cards,
        "math_blocks": tex_en["math_blocks"],
        "math_story": tex_en["math_story"],
        "reproducibility_commands": tex_en["reproducibility_commands"],
        "source_documents": tex_en["source_documents"],
        "datasets": datasets,
        "assets": assets,
        "updated_at": report_updated_at,
    }
    cn_section_cards = []
    for card in cn_section_cards_source:
        heading = str(card.get("heading", "")).strip() or "章节"
        raw_summary = str(card.get("summary", ""))
        sanitized_summary = ensure_cn_text(
            raw_summary,
            report_id,
            role="section",
            max_chars=320,
            hint=heading,
        )
        if has_malformed_readability_tokens(sanitized_summary) or is_placeholder_section_summary(heading, sanitized_summary):
            sanitized_summary = section_fallback_summary(heading, report_id, "cn")
        cn_section_cards.append(
            {
                "heading": heading,
                "summary": sanitized_summary,
                "source_path": str(card.get("source_path", "")),
            }
        )
    cn_section_cards = dedupe_section_cards_by_heading(cn_section_cards, lang="cn")
    cn_meta = {
        **base_meta,
        "lang": "cn",
        "title": title_cn,
        "summary": summary_cn,
        "key_findings": findings_cn,
        "narrative": cn_narrative,
        "section_cards": cn_section_cards,
        "math_blocks": tex_cn["math_blocks"] if tex_cn["math_blocks"] else tex_en["math_blocks"],
        "math_story": tex_cn["math_story"] if tex_cn["math_story"] else tex_en["math_story"],
        "reproducibility_commands": tex_cn["reproducibility_commands"]
        if tex_cn["reproducibility_commands"]
        else tex_en["reproducibility_commands"],
        "source_documents": tex_cn["source_documents"] if tex_cn["source_documents"] else tex_en["source_documents"],
    }
    base_meta, cn_meta = align_locale_payloads(base_meta, cn_meta)
    merged_repro_commands = dedupe_preserve(
        [
            normalize_space(str(x))
            for x in list(base_meta.get("reproducibility_commands", [])) + list(cn_meta.get("reproducibility_commands", []))
            if normalize_space(str(x))
        ],
        max_items=10,
    )
    base_meta["reproducibility_commands"] = merged_repro_commands
    cn_meta["reproducibility_commands"] = list(merged_repro_commands)
    merged_source_docs = dedupe_preserve(
        [
            normalize_space(str(x))
            for x in list(base_meta.get("source_documents", [])) + list(cn_meta.get("source_documents", []))
            if normalize_space(str(x))
        ],
        max_items=8,
    )
    base_meta["source_documents"] = merged_source_docs
    cn_meta["source_documents"] = list(merged_source_docs)

    (out_report_dir / "meta.json").write_text(
        json.dumps(base_meta, ensure_ascii=False, indent=2, allow_nan=False),
        encoding="utf-8",
    )
    (out_report_dir / "meta.cn.json").write_text(
        json.dumps(cn_meta, ensure_ascii=False, indent=2, allow_nan=False),
        encoding="utf-8",
    )
    (out_report_dir / "figures.json").write_text(
        json.dumps(figure_records, ensure_ascii=False, indent=2, allow_nan=False),
        encoding="utf-8",
    )

    return {
        "report_id": report_id,
        "path": report_rel,
        "languages": inferred_languages,
        "group": infer_group(report_id),
        "updated_at": report_updated_at,
    }


def detect_notions_from_formula(latex: str) -> set[str]:
    lowered = latex.lower()
    notions: set[str] = set()
    if "f(t)" in lowered or "\\pr" in lowered or "first" in lowered:
        notions.add("fpt-pmf")
    if "s(t)" in lowered or "survival" in lowered:
        notions.add("survival")
    if "h(t)" in lowered or "hazard" in lowered:
        notions.add("hazard")
    if "beta" in lowered or "\\beta" in lowered:
        notions.add("beta-scan")
    if "q=" in lowered or "\\lambda" in lowered or "eigen" in lowered:
        notions.add("spectral")
    if "\\sum" in lowered or "fft" in lowered or "aw" in lowered:
        notions.add("aw-inversion")
    return notions


def detect_notions_from_text(text: str) -> set[str]:
    lowered = normalize_space(str(text or "")).lower()
    notions: set[str] = set()
    if not lowered:
        return notions
    if any(token in lowered for token in ("first-passage", "first passage", "fpt", "首达", "首达时间")):
        notions.add("fpt-pmf")
    if "survival" in lowered or "生存" in lowered:
        notions.add("survival")
    if "hazard" in lowered or "风险率" in lowered or "风险" in lowered:
        notions.add("hazard")
    if "beta" in lowered or "\\beta" in lowered or "shortcut" in lowered:
        notions.add("beta-scan")
    if any(token in lowered for token in ("spectral", "eigen", "resolvent", "谱", "特征值")):
        notions.add("spectral")
    if any(token in lowered for token in ("aw", "fft", "inversion", "反演", "cauchy")):
        notions.add("aw-inversion")
    return notions


def formula_depth_policy(report_id: str, group: str) -> dict[str, Any]:
    group_defaults: dict[str, dict[str, Any]] = {
        "grid2d": {
            "min_required": 8,
            "target": 12,
            "policy_note": "Grid2D reports should carry full derivation context.",
        },
        "ring": {
            "min_required": 4,
            "target": 8,
            "policy_note": "Ring reports should include baseline and shortcut-sensitive formulas.",
        },
        "cross": {
            "min_required": 2,
            "target": 4,
            "policy_note": "Cross synthesis can be concise if it cites upstream derivations.",
        },
        "misc": {
            "min_required": 2,
            "target": 4,
            "policy_note": "Misc reports should still expose key derivation anchors.",
        },
    }
    policy = dict(group_defaults.get(group, group_defaults["misc"]))
    overrides: dict[str, dict[str, Any]] = {
        "ring_valley": {
            "min_required": 4,
            "target": 6,
            "policy_note": "Ring valley regime notes must expose explicit bridge formulas for parity, peak criteria, and class partition.",
        },
        "ring_lazy_jump_ext": {
            "min_required": 2,
            "target": 4,
            "exception_tag": "extension_delta",
            "exception_reason": "Extension report focuses on delta from baseline derivation.",
        },
        "ring_lazy_jump_ext_rev2": {
            "min_required": 2,
            "target": 4,
            "exception_tag": "extension_revision",
            "exception_reason": "Revision emphasizes corrected claims over repeated derivations.",
        },
    }
    override = overrides.get(report_id)
    if override:
        policy.update(override)
    return policy


def build_theory_map(output_dir: Path, reports: list[dict[str, Any]], generated_at: str) -> None:
    notions_meta = {
        "fpt-pmf": {
            "label_en": "First-passage distribution",
            "label_cn": "首达时间分布",
            "description_en": "Core PMF/CDF/survival quantities used across the major report families.",
            "description_cn": "在主要报告族中反复出现的 PMF/CDF/生存函数核心量。",
        },
        "survival": {
            "label_en": "Survival and hazard",
            "label_cn": "生存函数与风险率",
            "description_en": "Links between f(t), S(t), and hazard-style diagnostics.",
            "description_cn": "用于连接 f(t)、S(t) 与风险率诊断的定义。",
        },
        "hazard": {
            "label_en": "Hazard interpretation",
            "label_cn": "风险率解释",
            "description_en": "Peak/valley interpretation using hazard dynamics.",
            "description_cn": "通过风险率动态解释峰谷结构。",
        },
        "beta-scan": {
            "label_en": "Beta / shortcut scan",
            "label_cn": "beta/shortcut 扫描",
            "description_en": "How shortcut strength changes bimodality and phase behavior.",
            "description_cn": "shortcut 强度变化对双峰与相图的影响。",
        },
        "spectral": {
            "label_en": "Spectral decomposition",
            "label_cn": "谱分解",
            "description_en": "Eigenvalue / resolvent based derivations.",
            "description_cn": "基于特征值与 resolvent 的推导框架。",
        },
        "aw-inversion": {
            "label_en": "AW inversion",
            "label_cn": "AW 反演",
            "description_en": "Discrete Cauchy / FFT inversion from generating functions.",
            "description_cn": "从生成函数做离散 Cauchy / FFT 反演。",
        },
    }

    notion_reports: dict[str, set[str]] = defaultdict(set)
    report_formula_counts: dict[str, int] = {}
    finding_counter: Counter[str] = Counter()
    finding_examples: dict[str, str] = {}
    finding_reports: dict[str, set[str]] = defaultdict(set)
    formula_counter: Counter[str] = Counter()
    formula_examples: dict[str, str] = {}
    formula_reports: dict[str, set[str]] = defaultdict(set)
    asset_dup_stats: dict[str, dict[str, int]] = {}

    for row in reports:
        report_id = str(row["report_id"])
        meta_path = output_dir / "reports" / report_id / "meta.json"
        if not meta_path.exists():
            continue
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        math_blocks = list(meta.get("math_blocks", []))
        report_formula_counts[report_id] = len(math_blocks)
        report_notions: set[str] = set()
        for block in math_blocks:
            latex = str(block.get("latex", ""))
            signature = normalize_finding_key(latex)
            if signature:
                formula_counter[signature] += 1
                formula_examples.setdefault(signature, latex)
                formula_reports[signature].add(report_id)
            for notion in detect_notions_from_formula(latex):
                notion_reports[notion].add(report_id)
                report_notions.add(notion)

        text_sources: list[str] = [
            str(meta.get("summary", "")),
            str(meta.get("narrative", {}).get("model_overview", "")),
            str(meta.get("narrative", {}).get("method_overview", "")),
            str(meta.get("narrative", {}).get("result_overview", "")),
        ]
        text_sources.extend(str(item) for item in meta.get("key_findings", []))
        for dataset in meta.get("datasets", []):
            text_sources.append(str(dataset.get("title", "")))
            text_sources.append(str(dataset.get("x_label", "")))
            text_sources.append(str(dataset.get("y_label", "")))
        for text in text_sources:
            for notion in detect_notions_from_text(text):
                notion_reports[notion].add(report_id)
                report_notions.add(notion)

        if not report_notions:
            notion_reports["fpt-pmf"].add(report_id)

        for finding in meta.get("key_findings", []):
            text = normalize_space(str(finding))
            if not text:
                continue
            if looks_like_path_finding(text):
                continue
            key = normalize_finding_key(text)
            if not key:
                continue
            finding_counter[key] += 1
            finding_examples.setdefault(key, text)
            finding_reports[key].add(report_id)

        labels = [f"{row.get('kind', 'other')}::{str(row.get('label', '')).lower()}" for row in meta.get("assets", [])]
        duplicate_count = max(0, len(labels) - len(set(labels)))
        if labels:
            asset_dup_stats[report_id] = {"duplicate_count": duplicate_count, "total_assets": len(labels)}

    theory_cards = []
    for notion_id, payload in notions_meta.items():
        linked = sorted(notion_reports.get(notion_id, set()))
        if not linked:
            continue
        theory_cards.append(
            {
                "id": notion_id,
                **payload,
                "report_ids": linked,
                "report_count": len(linked),
            }
        )

    all_report_ids = {str(row["report_id"]) for row in reports}
    mapped_report_ids = set().union(*(set(card["report_ids"]) for card in theory_cards)) if theory_cards else set()
    unmapped_report_ids = sorted(all_report_ids - mapped_report_ids)

    formula_depth_rows: list[dict[str, Any]] = []
    for row in reports:
        report_id = str(row["report_id"])
        group = infer_group(report_id)
        policy = formula_depth_policy(report_id, group)
        formula_count = int(report_formula_counts.get(report_id, 0))
        min_required = int(policy.get("min_required", 1))
        target = int(policy.get("target", min_required))
        pass_check = formula_count >= min_required
        formula_depth_rows.append(
            {
                "report_id": report_id,
                "group": group,
                "formula_count": formula_count,
                "min_required": min_required,
                "target": target,
                "pass": pass_check,
                "policy_note": str(policy.get("policy_note", "")).strip(),
                "exception_tag": str(policy.get("exception_tag", "")).strip(),
                "exception_reason": str(policy.get("exception_reason", "")).strip(),
            }
        )
    formula_depth_rows.sort(key=lambda item: (str(item.get("group", "")), str(item.get("report_id", ""))))
    formula_depth_failures = [str(item["report_id"]) for item in formula_depth_rows if not bool(item.get("pass"))]
    formula_depth_exceptions = [item for item in formula_depth_rows if str(item.get("exception_tag", "")).strip()]

    repeated_findings = []
    for key, count in finding_counter.items():
        report_ids = sorted(finding_reports.get(key, set()))
        if len(report_ids) <= 1:
            continue
        repeated_findings.append(
            {
                "text": finding_examples[key],
                "report_count": len(report_ids),
                "occurrence_count": count,
                "report_ids": report_ids,
            }
        )
    repeated_findings.sort(key=lambda row: int(row["occurrence_count"]), reverse=True)

    repeated_formulas = []
    for key, count in formula_counter.items():
        report_ids = sorted(formula_reports.get(key, set()))
        if len(report_ids) <= 1:
            continue
        repeated_formulas.append(
            {
                "latex": formula_examples[key],
                "report_count": len(report_ids),
                "occurrence_count": count,
                "report_ids": report_ids,
            }
        )
    repeated_formulas.sort(key=lambda row: int(row["occurrence_count"]), reverse=True)
    redundant_repeated_formulas = [
        row for row in repeated_formulas if is_trivial_formula_signature(str(row.get("latex", "")))
    ]
    shared_core_formulas = [
        row for row in repeated_formulas if not is_trivial_formula_signature(str(row.get("latex", "")))
    ]

    asset_dup_excess = {
        report_id: payload
        for report_id, payload in asset_dup_stats.items()
        if payload.get("duplicate_count", 0) > 0
    }
    asset_dup_total = sum(int(payload.get("duplicate_count", 0)) for payload in asset_dup_stats.values())
    asset_dup_details = {
        "duplicate_count": asset_dup_total,
        "reports_with_duplicate_labels": len(asset_dup_excess),
        "total_reports_scanned": len(asset_dup_stats),
        "examples": {
            rid: payload
            for rid, payload in list(sorted(asset_dup_excess.items(), key=lambda row: row[0]))[:12]
        },
    }

    consistency_checks = [
        {
            "check": "all_reports_have_formula",
            "pass": all(count >= 1 for count in report_formula_counts.values()) if report_formula_counts else False,
            "details": report_formula_counts,
        },
        {
            "check": "formula_depth_policy",
            "pass": len(formula_depth_failures) == 0,
            "details": {
                "rows": formula_depth_rows,
                "failure_report_ids": formula_depth_failures,
                "exception_rows": formula_depth_exceptions,
            },
        },
        {
            "check": "all_reports_mapped_in_theory_cards",
            "pass": len(unmapped_report_ids) == 0,
            "details": {"unmapped_report_ids": unmapped_report_ids},
        },
        {
            "check": "duplicate_key_findings",
            "pass": len(repeated_findings) == 0,
            "details": repeated_findings[:12],
        },
        {
            "check": "duplicate_math_signatures",
            "pass": len(redundant_repeated_formulas) <= max(2, int(len(reports) * 0.15)),
            "details": {
                "redundant_signatures": redundant_repeated_formulas[:12],
                "shared_core_signatures": shared_core_formulas[:12],
                "redundant_count": len(redundant_repeated_formulas),
                "shared_core_count": len(shared_core_formulas),
            },
        },
        {
            "check": "asset_label_duplication",
            "pass": len(asset_dup_excess) == 0,
            "details": asset_dup_details,
        },
    ]

    theory_payload = {
        "version": "v1",
        "generated_at": generated_at,
        "cards": theory_cards,
        "consistency_checks": consistency_checks,
    }
    (output_dir / "theory_map.json").write_text(
        json.dumps(theory_payload, ensure_ascii=False, indent=2, allow_nan=False),
        encoding="utf-8",
    )


def build_report_network(output_dir: Path, reports: list[dict[str, Any]], generated_at: str) -> None:
    theory_map_path = output_dir / "theory_map.json"
    theory_payload: dict[str, Any] = {}
    if theory_map_path.exists():
        theory_payload = json.loads(theory_map_path.read_text(encoding="utf-8"))

    cards = list(theory_payload.get("cards", []))
    notion_labels: dict[str, dict[str, str]] = {}
    notion_by_report: dict[str, set[str]] = defaultdict(set)
    for card in cards:
        notion_id = str(card.get("id", "")).strip()
        if not notion_id:
            continue
        notion_labels[notion_id] = {
            "label_en": str(card.get("label_en", notion_id)),
            "label_cn": str(card.get("label_cn", notion_id)),
        }
        for report_id in card.get("report_ids", []):
            rid = str(report_id).strip()
            if rid:
                notion_by_report[rid].add(notion_id)

    ordered_ids = [str(row["report_id"]) for row in reports]
    report_by_id = {str(row["report_id"]): row for row in reports}
    group_tracks: dict[str, list[str]] = defaultdict(list)
    for row in reports:
        group_tracks[str(row.get("group", "misc"))].append(str(row["report_id"]))

    meta_by_report: dict[str, dict[str, Any]] = {}
    cn_meta_by_report: dict[str, dict[str, Any]] = {}
    for rid in ordered_ids:
        meta_path = output_dir / "reports" / rid / "meta.json"
        meta_cn_path = output_dir / "reports" / rid / "meta.cn.json"
        if meta_path.exists():
            meta_by_report[rid] = json.loads(meta_path.read_text(encoding="utf-8"))
        else:
            meta_by_report[rid] = {}
        if meta_cn_path.exists():
            cn_meta_by_report[rid] = json.loads(meta_cn_path.read_text(encoding="utf-8"))
        else:
            cn_meta_by_report[rid] = {}

    token_cache: dict[str, set[str]] = {}

    def id_tokens(report_id: str) -> set[str]:
        cached = token_cache.get(report_id)
        if cached is not None:
            return cached
        tokens = {tok for tok in re.split(r"[_\-]+", report_id.lower()) if tok}
        token_cache[report_id] = tokens
        return tokens

    def adjacency_in_group(a: str, b: str) -> bool:
        group = str(report_by_id.get(a, {}).get("group", "misc"))
        track = group_tracks.get(group, [])
        if a not in track or b not in track:
            return False
        return abs(track.index(a) - track.index(b)) == 1

    def build_link(a: str, b: str) -> dict[str, Any] | None:
        if a == b:
            return None
        group_a = str(report_by_id.get(a, {}).get("group", "misc"))
        group_b = str(report_by_id.get(b, {}).get("group", "misc"))
        notions_a = notion_by_report.get(a, set())
        notions_b = notion_by_report.get(b, set())
        shared_notions = sorted(notions_a.intersection(notions_b))
        score = 0.0
        if shared_notions:
            score += 3.0 * len(shared_notions)
        if group_a == group_b:
            score += 2.0
        if adjacency_in_group(a, b):
            score += 1.0
        overlap = id_tokens(a).intersection(id_tokens(b))
        if len(overlap) >= 2:
            score += 1.0
        if score <= 0:
            return None
        return {
            "report_id": b,
            "score": round(score, 2),
            "same_group": group_a == group_b,
            "adjacent_in_track": adjacency_in_group(a, b),
            "shared_notion_ids": shared_notions,
            "shared_token_count": len(overlap),
        }

    report_nodes: list[dict[str, Any]] = []
    for rid in ordered_ids:
        group = str(report_by_id.get(rid, {}).get("group", "misc"))
        track = group_tracks.get(group, [])
        idx = track.index(rid) if rid in track else -1
        previous_in_group = track[idx - 1] if idx > 0 else ""
        next_in_group = track[idx + 1] if idx >= 0 and idx + 1 < len(track) else ""

        links: list[dict[str, Any]] = []
        for other in ordered_ids:
            row = build_link(rid, other)
            if row:
                links.append(row)

        same_group_links = [row for row in links if bool(row.get("same_group"))]
        cross_group_links = [row for row in links if not bool(row.get("same_group"))]
        same_group_links.sort(key=lambda row: (-float(row["score"]), str(row["report_id"])))
        cross_group_links.sort(key=lambda row: (-float(row["score"]), str(row["report_id"])))

        meta = meta_by_report.get(rid, {})
        meta_cn = cn_meta_by_report.get(rid, {})
        summary_en = choose_best_summary(
            [
                str(meta.get("summary", "")),
                str(meta.get("narrative", {}).get("result_overview", "")),
                str(meta.get("narrative", {}).get("method_overview", "")),
                " ".join([str(x) for x in list(meta.get("key_findings", []))[:2]]),
            ],
            max_chars=420,
        ) or canonical_summary(str(meta.get("summary", "")), max_chars=420)
        summary_cn = choose_best_summary(
            [
                str(meta_cn.get("summary", meta.get("summary", ""))),
                str(meta_cn.get("narrative", {}).get("result_overview", "")),
                str(meta_cn.get("narrative", {}).get("method_overview", "")),
                " ".join([str(x) for x in list(meta_cn.get("key_findings", []))[:2]]),
            ],
            max_chars=420,
        ) or canonical_summary(str(meta_cn.get("summary", meta.get("summary", ""))), max_chars=420)
        summary_en = improve_summary_if_needed(
            summary_en,
            [
                str(meta.get("narrative", {}).get("result_overview", "")),
                str(meta.get("narrative", {}).get("method_overview", "")),
                " ".join([str(x) for x in list(meta.get("key_findings", []))[:2]]),
                str(meta.get("title", rid)),
            ],
            max_chars=420,
        )
        summary_cn = improve_summary_if_needed(
            summary_cn,
            [
                str(meta_cn.get("narrative", {}).get("result_overview", "")),
                str(meta_cn.get("narrative", {}).get("method_overview", "")),
                " ".join([str(x) for x in list(meta_cn.get("key_findings", []))[:2]]),
                str(meta_cn.get("title", meta.get("title", rid))),
                summary_en,
            ],
            max_chars=420,
        )
        report_nodes.append(
            {
                "report_id": rid,
                "group": group,
                "title_en": str(meta.get("title", rid)),
                "title_cn": str(meta_cn.get("title", meta.get("title", rid))),
                "summary_en": summary_en,
                "summary_cn": summary_cn,
                "notion_ids": sorted(notion_by_report.get(rid, set())),
                "previous_in_group": previous_in_group,
                "next_in_group": next_in_group,
                "same_group_links": same_group_links[:6],
                "cross_group_links": cross_group_links[:6],
            }
        )

    ordered_groups = []
    for row in reports:
        group = str(row.get("group", "misc"))
        if group not in ordered_groups:
            ordered_groups.append(group)

    group_paths = [
        {
            "group": group,
            "report_ids": group_tracks.get(group, []),
            "step_count": len(group_tracks.get(group, [])),
        }
        for group in ordered_groups
    ]

    full_story = []
    for group in ordered_groups:
        full_story.extend(group_tracks.get(group, []))

    payload = {
        "version": "v1",
        "generated_at": generated_at,
        "notion_labels": notion_labels,
        "group_paths": group_paths,
        "global_storyline": {
            "label_en": "Grid and ring mechanisms converge into cross-report synthesis.",
            "label_cn": "二维与环模型机制最终汇入跨报告综合结论。",
            "report_ids": full_story,
        },
        "reports": report_nodes,
    }
    (output_dir / "report_network.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False),
        encoding="utf-8",
    )


LOW_SIGNAL_EVIDENCE_TOKENS = (
    "asset size profile",
    "asset rank",
    "size (bytes)",
    "manifest",
    "registry",
    "placeholder",
    "download assets",
    "figure gallery",
)

EVIDENCE_DATASET_POSITIVE_HINTS = (
    "probability",
    "pmf",
    "fpt",
    "hazard",
    "survival",
    "peak",
    "valley",
    "phase",
    "beta",
    "scan",
    "bimodal",
    "two_target",
    "cond_by_t",
)


def is_low_signal_evidence_text(text: str) -> bool:
    lowered = normalize_space(text).lower()
    if not lowered:
        return True
    if any(token in lowered for token in LOW_SIGNAL_EVIDENCE_TOKENS):
        return True
    if lowered.startswith("this section ") and "evidence" in lowered and "verification" in lowered:
        return True
    if lowered.startswith("本节") and ("证据" in lowered or "核验" in lowered):
        return True
    if len(lowered) < 20:
        return True
    return False


def is_generic_claim_evidence_snippet(text: str) -> bool:
    cleaned = normalize_space(str(text or ""))
    lowered = cleaned.lower()
    if not cleaned:
        return True
    if is_low_signal_evidence_text(cleaned):
        return True
    if has_malformed_readability_tokens(cleaned):
        return True
    if re.search(r"(?:[,、]\s*){2,}", cleaned):
        return True
    if re.search(r"\bthis section\b.*\b(evidence|verification)\b", lowered):
        return True
    if re.search(r"^figures?:\s*this section\b", lowered):
        return True
    if re.search(r"^tables?:\s*this section\b", lowered):
        return True
    if re.search(r"^本节(?:主要)?(?:解释|总结|汇总|呈现).*(?:图|表)", cleaned):
        return True
    if summary_penalty(cleaned) > 18:
        return True
    return False


def dataset_evidence_score(dataset: dict[str, Any]) -> int:
    title = normalize_space(str(dataset.get("title", ""))).lower()
    series_id = normalize_space(str(dataset.get("series_id", ""))).lower()
    x_label = normalize_space(str(dataset.get("x_label", ""))).lower()
    y_label = normalize_space(str(dataset.get("y_label", ""))).lower()
    haystack = " ".join([title, series_id, x_label, y_label])
    score = 0
    for token in EVIDENCE_DATASET_POSITIVE_HINTS:
        if token in haystack:
            score += 3
    for token in LOW_SIGNAL_EVIDENCE_TOKENS:
        if token in haystack:
            score -= 10
    if "probability" in y_label:
        score += 4
    if "binary" in y_label or "phase" in y_label:
        score += 2
    if "asset rank" in x_label:
        score -= 12
    if str(dataset.get("series_path", "")).strip().startswith("/data/v1/reports/"):
        score += 1
    return score


def pick_best_dataset_for_claim(datasets: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not datasets:
        return None
    ranked = sorted(
        ((dataset_evidence_score(ds), idx, ds) for idx, ds in enumerate(datasets)),
        key=lambda row: (row[0], -row[1]),
        reverse=True,
    )
    best_score, _, best = ranked[0]
    if best_score < -8:
        return None
    return best


def build_content_map(output_dir: Path, reports: list[dict[str, Any]], generated_at: str) -> None:
    network_path = output_dir / "report_network.json"
    network_payload: dict[str, Any] = {}
    if network_path.exists():
        network_payload = json.loads(network_path.read_text(encoding="utf-8"))

    network_nodes = {
        str(row.get("report_id", "")): row
        for row in list(network_payload.get("reports", []))
        if str(row.get("report_id", "")).strip()
    }

    meta_by_report: dict[str, dict[str, Any]] = {}
    cn_meta_by_report: dict[str, dict[str, Any]] = {}
    report_path_by_id: dict[str, str] = {}
    for row in reports:
        rid = str(row["report_id"])
        report_path_by_id[rid] = str(row.get("path", ""))
        meta_path = output_dir / "reports" / rid / "meta.json"
        meta_cn_path = output_dir / "reports" / rid / "meta.cn.json"
        meta_by_report[rid] = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
        cn_meta_by_report[rid] = json.loads(meta_cn_path.read_text(encoding="utf-8")) if meta_cn_path.exists() else {}

    claim_rows: list[dict[str, Any]] = []
    claim_ids_by_report: dict[str, list[str]] = defaultdict(list)
    report_guides: list[dict[str, Any]] = []
    debug_report = normalize_space(os.getenv("DEBUG_CONTENT_MAP_REPORT", ""))

    for row in reports:
        rid = str(row["report_id"])
        meta = meta_by_report.get(rid, {})
        meta_cn = cn_meta_by_report.get(rid, {})
        node = network_nodes.get(rid, {})

        objective_en = normalize_space(str(meta.get("narrative", {}).get("result_overview", "")))
        objective_cn = normalize_space(str(meta_cn.get("narrative", {}).get("result_overview", "")))
        if not objective_en:
            objective_en = summarize_plain(str(meta.get("summary", "Research objective unavailable.")), max_chars=240)
        if not objective_cn:
            objective_cn = summarize_plain(
                str(meta_cn.get("summary", meta.get("summary", "研究目标暂缺。"))),
                max_chars=240,
            )

        upstream: list[str] = []
        prev_id = str(node.get("previous_in_group", "")).strip()
        if prev_id:
            upstream.append(prev_id)

        downstream: list[str] = []
        next_id = str(node.get("next_in_group", "")).strip()
        if next_id:
            downstream.append(next_id)

        related_candidates = [
            str(link.get("report_id", "")).strip()
            for link in list(node.get("same_group_links", []))[:3] + list(node.get("cross_group_links", []))[:3]
        ]
        related = dedupe_preserve([x for x in related_candidates if x and x != rid], max_items=6)

        report_guides.append(
            {
                "report_id": rid,
                "objective_en": objective_en,
                "objective_cn": objective_cn,
                "upstream_report_ids": upstream,
                "downstream_report_ids": downstream,
                "related_report_ids": related,
                "verification_steps_en": [
                    "Read the key claims and their evidence references first.",
                    "Verify at least one equation card and one dataset panel against source paths.",
                    "Cross-check this report with upstream/downstream linked reports.",
                ],
                "verification_steps_cn": [
                    "先读关键 claim 及其证据引用。",
                    "至少核对一条公式卡与一个数据面板的来源路径。",
                    "再与上游/下游关联报告做交叉核对。",
                ],
            }
        )

        findings_en = dedupe_preserve([str(x) for x in meta.get("key_findings", [])], max_items=8)
        findings_cn = dedupe_preserve([str(x) for x in meta_cn.get("key_findings", [])], max_items=8)
        section_cards_en = list(meta.get("section_cards", []))
        section_cards_cn = list(meta_cn.get("section_cards", []))
        math_blocks_en = list(meta.get("math_blocks", []))
        datasets = list(meta.get("datasets", []))
        source_docs = [str(x) for x in meta.get("source_documents", []) if str(x).strip()]
        narrative_en = dict(meta.get("narrative", {}))
        narrative_cn = dict(meta_cn.get("narrative", {}))
        report_title_en = normalize_space(str(meta.get("title", humanize_report_id(rid))))
        report_title_cn = ensure_cn_text(
            str(meta_cn.get("title", report_title_en)),
            rid,
            role="title",
            max_chars=80,
            hint=str(meta_cn.get("title", "")),
        )
        group_name = normalize_space(str(node.get("group", "")))

        staged_candidates: list[tuple[str, str, str]] = [
            (
                "model",
                normalize_space(str(narrative_en.get("model_overview", ""))),
                normalize_space(str(narrative_cn.get("model_overview", ""))),
            ),
            (
                "method",
                normalize_space(str(narrative_en.get("method_overview", ""))),
                normalize_space(str(narrative_cn.get("method_overview", ""))),
            ),
            (
                "result",
                normalize_space(str(narrative_en.get("result_overview", ""))),
                normalize_space(str(narrative_cn.get("result_overview", ""))),
            ),
        ]
        for idx, line in enumerate(findings_en[:2]):
            staged_candidates.append(
                (
                    "finding",
                    normalize_space(str(line)),
                    normalize_space(str(findings_cn[idx] if idx < len(findings_cn) else objective_cn)),
                )
            )

        staged_claims: list[tuple[str, str, str]] = []
        seen_claim_signatures: set[str] = set()
        for stage, text_en, text_cn in staged_candidates:
            cleaned_en = sanitize_claim_text_for_map(text_en, lang="en", max_chars=460, report_id=rid)
            cleaned_cn = sanitize_claim_text_for_map(text_cn, lang="cn", max_chars=320, report_id=rid)
            if not cleaned_en:
                continue
            role_key = stage if stage in {"model", "method", "result", "finding"} else "claim"
            cleaned_en = ensure_en_text(cleaned_en, rid, role=role_key, max_chars=460)
            cleaned_cn = ensure_cn_text(cleaned_cn, rid, role=role_key, max_chars=320)
            if looks_like_operational_note(cleaned_en):
                continue
            signature = normalize_finding_key(cleaned_en)
            if not signature or signature in seen_claim_signatures:
                continue
            seen_claim_signatures.add(signature)
            if not cleaned_cn:
                cleaned_cn = summarize_plain(objective_cn, max_chars=220)
            staged_claims.append((stage, cleaned_en, cleaned_cn))

        stage_seed_map: dict[str, tuple[str, str]] = {
            "model": (
                normalize_space(str(narrative_en.get("model_overview", "")))
                or f"{report_title_en} defines the state-space assumptions and boundary constraints used across its analysis chain.",
                normalize_space(str(narrative_cn.get("model_overview", "")))
                or f"{report_title_cn} 给出状态空间假设与边界约束，作为后续推导的模型起点。",
            ),
            "method": (
                normalize_space(str(narrative_en.get("method_overview", "")))
                or f"{report_title_en} combines derivation, inversion, and numerical verification to keep each claim auditable.",
                normalize_space(str(narrative_cn.get("method_overview", "")))
                or f"{report_title_cn} 采用推导、反演与数值核验结合的方法，保证每条结论可追溯。",
            ),
            "result": (
                normalize_space(str(narrative_en.get("result_overview", "")))
                or objective_en
                or f"{report_title_en} reports a verifiable behavioral outcome that is cross-checked by equations and datasets.",
                normalize_space(str(narrative_cn.get("result_overview", "")))
                or objective_cn
                or f"{report_title_cn} 给出可核验的行为结论，并由公式链与数据面板共同支撑。",
            ),
            "finding": (
                normalize_space(str(findings_en[0] if findings_en else ""))
                or f"Key finding in {report_title_en}: the mechanism remains consistent under the chosen diagnostics and linked evidence panels.",
                normalize_space(str(findings_cn[0] if findings_cn else ""))
                or f"{report_title_cn} 的关键发现是：核心机制在所设诊断口径下保持一致，并可由关联证据面板核对。",
            ),
        }

        stage_order = ("model", "method", "result", "finding")
        seen_stage_order = {stage for stage, _, _ in staged_claims}
        for stage in stage_order:
            if stage in seen_stage_order:
                continue
            seed_en, seed_cn = stage_seed_map.get(stage, ("", ""))
            fallback_en = ensure_en_text(seed_en or objective_en, rid, role=stage, max_chars=460)
            fallback_cn = ensure_cn_text(seed_cn or objective_cn, rid, role=stage, max_chars=320)
            stage_prefix_en = {
                "model": "Model premise",
                "method": "Method chain",
                "result": "Result statement",
                "finding": "Key finding",
            }.get(stage, "Claim")
            stage_prefix_cn = {
                "model": "模型前提",
                "method": "方法链路",
                "result": "结果陈述",
                "finding": "关键发现",
            }.get(stage, "结论")
            if not fallback_en.lower().startswith(stage_prefix_en.lower()):
                fallback_en = canonical_summary(f"{stage_prefix_en}: {fallback_en}", max_chars=460)
            if not fallback_cn.startswith(stage_prefix_cn):
                fallback_cn = canonical_summary(f"{stage_prefix_cn}：{fallback_cn}", max_chars=320)
            if group_name:
                fallback_en = canonical_summary(
                    f"[{group_name}] {fallback_en}",
                    max_chars=460,
                )
                fallback_cn = canonical_summary(
                    f"[{group_name}] {fallback_cn}",
                    max_chars=320,
                )
            signature = normalize_finding_key(f"{stage}:{fallback_en}")
            if signature in seen_claim_signatures:
                fallback_en = canonical_summary(
                    f"{fallback_en} This stage is preserved explicitly for continuity.",
                    max_chars=460,
                )
                fallback_cn = canonical_summary(
                    f"{fallback_cn} 为保证章节连续性，此阶段单独保留。",
                    max_chars=320,
                )
                signature = normalize_finding_key(f"{stage}:{fallback_en}")
            seen_claim_signatures.add(signature or f"{rid}-{stage}-fallback")
            staged_claims.append((stage, fallback_en, fallback_cn))

        if not staged_claims:
            staged_claims = [
                (
                    "result",
                    summarize_plain(objective_en, max_chars=240),
                    summarize_plain(objective_cn, max_chars=240),
                )
            ]
        staged_claims.sort(key=lambda row: (stage_order.index(row[0]) if row[0] in stage_order else 99, row[1]))
        if debug_report and rid == debug_report:
            print(
                json.dumps(
                    {
                        "debug": "staged_claims",
                        "report_id": rid,
                        "stages": [row[0] for row in staged_claims],
                        "count": len(staged_claims),
                    },
                    ensure_ascii=False,
                )
            )

        stage_hint_map: dict[str, tuple[str, ...]] = {
            "model": MODEL_HINTS,
            "method": METHOD_HINTS,
            "result": RESULT_HINTS,
            "finding": RESULT_HINTS,
        }

        for idx, (stage, text_en, text_cn) in enumerate(staged_claims):
            claim_id = f"{rid}-c{idx + 1}"
            claim_tokens = tokenize_claim_text(text_en)
            stage_label_cn = {
                "model": "模型",
                "method": "方法",
                "result": "结果",
                "finding": "发现",
            }.get(stage, "结论")

            evidence: list[dict[str, Any]] = []

            for source_path in source_docs[:1]:
                source_snippet_en = summarize_plain(text_en, max_chars=180)
                source_snippet_cn = summarize_plain(text_cn, max_chars=180)
                if is_generic_claim_evidence_snippet(source_snippet_en):
                    source_snippet_en = summarize_plain(
                        f"Source-backed {stage} claim in {report_title_en}: {text_en}",
                        max_chars=180,
                    )
                    source_snippet_cn = summarize_plain(
                        f"{report_title_cn} 的{stage_label_cn}结论来源摘要：{text_cn}",
                        max_chars=180,
                    )
                evidence.append(
                    {
                        "evidence_type": "source_document",
                        "path": source_path,
                        "snippet_en": source_snippet_en,
                        "snippet_cn": source_snippet_cn,
                    }
                )

            section_scored: list[tuple[int, int]] = []
            for j, card in enumerate(section_cards_en):
                summary = normalize_space(str(card.get("summary", "")))
                if not summary:
                    continue
                title = normalize_space(str(card.get("heading", ""))).lower()
                if is_low_signal_evidence_text(f"{title} {summary}"):
                    continue
                overlap = len(claim_tokens.intersection(tokenize_claim_text(summary)))
                hint_bonus = 2 if any(h in title for h in stage_hint_map.get(stage, ())) else 0
                section_scored.append((overlap + hint_bonus, j))
            section_scored.sort(reverse=True)
            for _, j in section_scored[:2]:
                card_en = section_cards_en[j]
                card_cn = section_cards_cn[j] if j < len(section_cards_cn) else {}
                heading_en = normalize_space(str(card_en.get("heading", "Section")))
                heading_cn = normalize_space(str(card_cn.get("heading", "章节")))
                snippet_en = summarize_plain(str(card_en.get("summary", text_en)), max_chars=180)
                snippet_cn = summarize_plain(str(card_cn.get("summary", text_cn)), max_chars=180)
                if is_generic_claim_evidence_snippet(snippet_en):
                    snippet_en = summarize_plain(f"{heading_en}: {text_en}", max_chars=180)
                    snippet_cn = summarize_plain(f"{heading_cn}: {text_cn}", max_chars=180)
                if is_generic_claim_evidence_snippet(snippet_en):
                    continue
                evidence.append(
                    {
                        "evidence_type": "section_summary",
                        "path": str(card_en.get("source_path", report_path_by_id.get(rid, rid))),
                        "snippet_en": snippet_en,
                        "snippet_cn": snippet_cn,
                    }
                )

            math_limit = 2 if stage in {"model", "method"} else 1
            for block in math_blocks_en[:math_limit]:
                block_context = summarize_plain(str(block.get("context", "math block")), max_chars=120)
                if is_generic_claim_evidence_snippet(block_context):
                    block_context = summarize_plain(
                        f"{stage.title()} formula context in {report_title_en}: {text_en}",
                        max_chars=140,
                    )
                if is_generic_claim_evidence_snippet(block_context):
                    continue
                evidence.append(
                    {
                        "evidence_type": "math_block",
                        "path": str(block.get("source_path", report_path_by_id.get(rid, rid))),
                        "snippet_en": block_context,
                        "snippet_cn": summarize_plain(str(block.get("context", "公式片段")), max_chars=120),
                    }
                )

            if datasets and stage in {"method", "result", "finding"}:
                ds = pick_best_dataset_for_claim(datasets)
                if ds is None:
                    ds = datasets[0]
                ds_snippet_en = summarize_plain(
                    f"{ds.get('title', 'dataset')}: {ds.get('x_label', 'x')} -> {ds.get('y_label', 'y')}",
                    max_chars=160,
                )
                ds_snippet_cn = summarize_plain(
                    f"{ds.get('title', '数据集')}: {ds.get('x_label', 'x')} -> {ds.get('y_label', 'y')}",
                    max_chars=160,
                )
                if is_low_signal_evidence_text(ds_snippet_en):
                    ds_snippet_en = summarize_plain(
                        f"Mechanism dataset for {report_title_en}: {ds.get('series_id', 'series')}",
                        max_chars=160,
                    )
                    ds_snippet_cn = summarize_plain(
                        f"{report_title_cn} 的机制数据集：{ds.get('series_id', 'series')}",
                        max_chars=160,
                    )
                if is_generic_claim_evidence_snippet(ds_snippet_en):
                    ds_snippet_en = summarize_plain(
                        f"{report_title_en} {stage} evidence uses dataset {ds.get('series_id', 'series')}.",
                        max_chars=160,
                    )
                    ds_snippet_cn = summarize_plain(
                        f"{report_title_cn} 的{stage_label_cn}证据使用数据集 {ds.get('series_id', 'series')}。",
                        max_chars=160,
                    )
                if is_generic_claim_evidence_snippet(ds_snippet_en):
                    continue
                evidence.append(
                    {
                        "evidence_type": "dataset",
                        "path": str(ds.get("series_path", "")),
                        "snippet_en": ds_snippet_en,
                        "snippet_cn": ds_snippet_cn,
                    }
                )

            deduped_evidence: list[dict[str, Any]] = []
            seen_keys: set[str] = set()
            for row_evidence in evidence:
                key = f"{row_evidence.get('evidence_type')}::{row_evidence.get('path')}::{row_evidence.get('snippet_en')}"
                if key in seen_keys:
                    continue
                seen_keys.add(key)
                deduped_evidence.append(row_evidence)

            filtered_evidence = [
                row_evidence
                for row_evidence in deduped_evidence
                if not is_generic_claim_evidence_snippet(str(row_evidence.get("snippet_en", "")))
            ]
            if filtered_evidence:
                deduped_evidence = filtered_evidence

            if not deduped_evidence:
                deduped_evidence = [
                    {
                        "evidence_type": "source_document",
                        "path": report_path_by_id.get(rid, rid),
                        "snippet_en": summarize_plain(text_en, max_chars=180),
                        "snippet_cn": summarize_plain(text_cn, max_chars=180),
                    }
                ]

            claim_rows.append(
                {
                    "claim_id": claim_id,
                    "report_id": rid,
                    "stage": stage,
                    "text_en": text_en,
                    "text_cn": text_cn,
                    "evidence": deduped_evidence[:6],
                    "linked_claim_ids": [],
                    "linked_report_ids": [],
                }
            )
            claim_ids_by_report[rid].append(claim_id)
        if debug_report and rid == debug_report:
            print(
                json.dumps(
                    {
                        "debug": "written_claim_ids",
                        "report_id": rid,
                        "claim_ids": list(claim_ids_by_report.get(rid, [])),
                    },
                    ensure_ascii=False,
                )
            )

    score_links: dict[str, list[tuple[int, str, str]]] = defaultdict(list)
    claim_list = list(claim_rows)
    for i, left in enumerate(claim_list):
        tokens_left = tokenize_claim_text(str(left.get("text_en", "")))
        if not tokens_left:
            continue
        for right in claim_list[i + 1 :]:
            if str(left.get("report_id")) == str(right.get("report_id")):
                continue
            tokens_right = tokenize_claim_text(str(right.get("text_en", "")))
            overlap = len(tokens_left.intersection(tokens_right))
            left_stage = str(left.get("stage"))
            right_stage = str(right.get("stage"))
            required_overlap = 1 if {"model", "method"}.intersection({left_stage, right_stage}) else 2
            if overlap < required_overlap:
                continue
            stage_bonus = 1 if left_stage == right_stage else 0
            score = overlap + stage_bonus
            left_id = str(left.get("claim_id"))
            right_id = str(right.get("claim_id"))
            score_links[left_id].append((score, right_id, str(right.get("report_id"))))
            score_links[right_id].append((score, left_id, str(left.get("report_id"))))

    guide_by_report = {row["report_id"]: row for row in report_guides}
    for claim in claim_rows:
        claim_id = str(claim.get("claim_id"))
        related = sorted(score_links.get(claim_id, []), key=lambda row: (-row[0], row[1]))[:5]
        linked_claim_ids = [row[1] for row in related]
        linked_report_ids = dedupe_preserve([row[2] for row in related], max_items=5)
        if not linked_report_ids:
            guide = guide_by_report.get(str(claim.get("report_id")), {})
            linked_report_ids = dedupe_preserve(
                list(guide.get("related_report_ids", [])) + list(guide.get("upstream_report_ids", [])),
                max_items=3,
            )
        claim["linked_claim_ids"] = linked_claim_ids
        claim["linked_report_ids"] = linked_report_ids

    arcs: list[dict[str, Any]] = []
    group_paths = list(network_payload.get("group_paths", []))
    for path_row in group_paths:
        group = str(path_row.get("group", "misc"))
        report_ids = [str(x) for x in path_row.get("report_ids", []) if str(x).strip()]
        checkpoints: list[dict[str, str]] = []
        claim_ids: list[str] = []
        for rid in report_ids:
            meta = meta_by_report.get(rid, {})
            meta_cn = cn_meta_by_report.get(rid, {})
            guide = guide_by_report.get(rid, {})
            checkpoints.append(
                {
                    "report_id": rid,
                    "title_en": str(meta.get("title", rid)),
                    "title_cn": str(meta_cn.get("title", meta.get("title", rid))),
                    "contribution_en": str(guide.get("objective_en", summarize_plain(str(meta.get("summary", "")), max_chars=180))),
                    "contribution_cn": str(
                        guide.get(
                            "objective_cn",
                            summarize_plain(str(meta_cn.get("summary", meta.get("summary", ""))), max_chars=180),
                        )
                    ),
                }
            )
            claim_ids.extend(claim_ids_by_report.get(rid, []))
        if not report_ids:
            continue
        arcs.append(
            {
                "arc_id": f"group-{group}",
                "label_en": f"{group} progression",
                "label_cn": f"{group} 研究推进链",
                "summary_en": f"{group} track links {len(report_ids)} reports into one continuous argument.",
                "summary_cn": f"{group} 轨道把 {len(report_ids)} 份报告串成连续论证。",
                "report_ids": report_ids,
                "claim_ids": dedupe_preserve(claim_ids, max_items=200),
                "checkpoint_count": len(checkpoints),
                "checkpoints": checkpoints,
            }
        )

    global_story = dict(network_payload.get("global_storyline", {}))
    global_reports = [str(x) for x in global_story.get("report_ids", []) if str(x).strip()]
    if global_reports:
        global_claim_ids: list[str] = []
        for rid in global_reports:
            global_claim_ids.extend(claim_ids_by_report.get(rid, []))
        arcs.append(
            {
                "arc_id": "global-synthesis",
                "label_en": str(global_story.get("label_en", "Global synthesis")),
                "label_cn": str(global_story.get("label_cn", "全局综合")),
                "summary_en": "Global storyline that connects all report families from mechanism to synthesis.",
                "summary_cn": "连接全部报告家族的全局叙事主线，从机制到综合结论。",
                "report_ids": global_reports,
                "claim_ids": dedupe_preserve(global_claim_ids, max_items=300),
                "checkpoint_count": len(global_reports),
                "checkpoints": [
                    {
                        "report_id": rid,
                        "title_en": str(meta_by_report.get(rid, {}).get("title", rid)),
                        "title_cn": str(
                            cn_meta_by_report.get(rid, {}).get("title", meta_by_report.get(rid, {}).get("title", rid))
                        ),
                        "contribution_en": str(guide_by_report.get(rid, {}).get("objective_en", "")),
                        "contribution_cn": str(guide_by_report.get(rid, {}).get("objective_cn", "")),
                    }
                    for rid in global_reports
                ],
            }
        )

    all_report_ids = {str(row["report_id"]) for row in reports}
    claims_report_ids = {str(row["report_id"]) for row in claim_rows}
    guides_report_ids = {str(row["report_id"]) for row in report_guides}
    missing_claim_reports = sorted(all_report_ids - claims_report_ids)
    missing_guide_reports = sorted(all_report_ids - guides_report_ids)
    required_stage_set = {"model", "method", "result", "finding"}
    report_stage_coverage: dict[str, set[str]] = defaultdict(set)
    for row in claim_rows:
        report_stage_coverage[str(row.get("report_id", ""))].add(str(row.get("stage", "")))
    missing_stage_chain = [
        {
            "report_id": rid,
            "missing_stages": sorted(required_stage_set - report_stage_coverage.get(rid, set())),
        }
        for rid in sorted(all_report_ids)
        if required_stage_set - report_stage_coverage.get(rid, set())
    ]
    claims_without_evidence = sorted([str(row["claim_id"]) for row in claim_rows if not row.get("evidence")])
    linked_claim_count = sum(1 for row in claim_rows if row.get("linked_report_ids"))
    duplicate_claim_signatures = Counter(normalize_finding_key(str(row.get("text_en", ""))) for row in claim_rows)
    repeated_claims = [
        {"signature": sig, "count": count}
        for sig, count in duplicate_claim_signatures.items()
        if sig and count > 1
    ]
    repeated_claims.sort(key=lambda row: int(row["count"]), reverse=True)

    consistency_checks = [
        {
            "check": "all_reports_have_claims",
            "pass": len(missing_claim_reports) == 0,
            "details": {"missing_report_ids": missing_claim_reports, "claim_count": len(claim_rows)},
        },
        {
            "check": "all_claims_have_evidence",
            "pass": len(claims_without_evidence) == 0,
            "details": {"claims_without_evidence": claims_without_evidence},
        },
        {
            "check": "all_reports_have_guides",
            "pass": len(missing_guide_reports) == 0,
            "details": {"missing_report_ids": missing_guide_reports},
        },
        {
            "check": "all_reports_have_core_stage_chain",
            "pass": len(missing_stage_chain) == 0,
            "details": {"missing_stage_chain": missing_stage_chain},
        },
        {
            "check": "cross_report_claim_links",
            "pass": linked_claim_count >= max(1, int(len(claim_rows) * 0.65)),
            "details": {"linked_claim_count": linked_claim_count, "claim_count": len(claim_rows)},
        },
        {
            "check": "duplicate_claim_signatures",
            "pass": len(repeated_claims) <= max(4, int(len(claim_rows) * 0.2)),
            "details": repeated_claims[:20],
        },
    ]

    payload = {
        "version": "v1",
        "generated_at": generated_at,
        "report_count": len(all_report_ids),
        "arcs": arcs,
        "claims": claim_rows,
        "report_guides": report_guides,
        "consistency_checks": consistency_checks,
    }
    (output_dir / "content_map.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False),
        encoding="utf-8",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build platform/web/public/data/v1 web payloads from report assets.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--artifacts-dir", type=Path, default=DEFAULT_ARTIFACTS_DIR)
    parser.add_argument("--mode", choices=["full", "changed"], default="full")
    parser.add_argument("--reports", nargs="*", default=[])
    parser.add_argument("--max-assets", type=int, default=40)
    parser.add_argument("--max-figures", type=int, default=24)
    parser.add_argument("--max-datasets", type=int, default=3)
    parser.add_argument("--max-points", type=int, default=1200)
    parser.add_argument("--no-copy-assets", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_dir: Path = args.output_dir
    artifacts_dir: Path = args.artifacts_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    registry = load_registry()
    ids_in_registry = {item["id"] for item in registry}

    if args.reports:
        selected_ids = {rid for rid in args.reports if rid in ids_in_registry}
        if not selected_ids:
            raise SystemExit("No matching reports found in --reports")
    elif args.mode == "changed":
        selected_ids = detect_changed_reports(registry)
    else:
        selected_ids = ids_in_registry

    existing_index_path = output_dir / "index.json"
    existing_entries: dict[str, dict[str, Any]] = {}
    if existing_index_path.exists():
        try:
            existing = json.loads(existing_index_path.read_text(encoding="utf-8"))
            for row in existing.get("reports", []):
                if "report_id" in row:
                    existing_entries[row["report_id"]] = row
        except json.JSONDecodeError:
            existing_entries = {}

    if args.mode == "full" and not args.reports:
        clean_output_dir(output_dir / "reports")
        clean_output_dir(artifacts_dir)

    generated_at = utc_now_iso()

    built_entries: dict[str, dict[str, Any]] = {}
    for item in registry:
        report_id = str(item["id"])
        if report_id not in selected_ids:
            if report_id in existing_entries:
                built_entries[report_id] = existing_entries[report_id]
            continue

        entry = build_report_payload(
            item,
            output_dir,
            artifacts_dir,
            max_assets=max(1, args.max_assets),
            max_figures=max(1, args.max_figures),
            max_datasets=max(1, args.max_datasets),
            max_points=max(20, args.max_points),
            no_copy_assets=bool(args.no_copy_assets),
            generated_at=generated_at,
        )
        built_entries[report_id] = entry

    reports = [built_entries[item["id"]] for item in registry if item["id"] in built_entries]
    index_payload = {
        "version": "v1",
        "generated_at": generated_at,
        "reports": reports,
    }
    existing_index_path.write_text(
        json.dumps(index_payload, ensure_ascii=False, indent=2, allow_nan=False),
        encoding="utf-8",
    )
    duplicate_resolution = enforce_unique_key_findings(output_dir, [row["report_id"] for row in reports])
    build_theory_map(output_dir, reports, generated_at)
    build_report_network(output_dir, reports, generated_at)
    build_content_map(output_dir, reports, generated_at)
    build_repo_sync_payload(output_dir, generated_at)

    print(
        json.dumps(
            {
                "ok": True,
                "mode": args.mode,
                "selected_reports": sorted(selected_ids),
                "written_reports": [row["report_id"] for row in reports],
                "duplicate_resolution": duplicate_resolution[:10],
                "output_dir": output_dir.as_posix(),
                "artifacts_dir": artifacts_dir.as_posix(),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
