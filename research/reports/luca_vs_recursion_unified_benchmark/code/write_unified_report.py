#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

from common import REPORT_DIR, workload_order, workload_specs


def _load_summary(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _fmt(x: float, nd: int = 3) -> str:
    return f"{float(x):.{nd}f}"


def _agg(summary: Dict[str, Any], task_kind: str) -> Dict[str, Any]:
    for row in summary["aggregates"]["by_task_kind"]:
        if row["task_kind"] == task_kind:
            return row
    return {}


def _wins(summary: Dict[str, Any], task_kind: str, family: str) -> List[str]:
    rows = [row["workload_id"] for row in summary["pair_rows"] if row["task_kind"] == task_kind and row["recommended_family"] == family]
    order = {wid: idx for idx, wid in enumerate(workload_order())}
    return sorted(rows, key=lambda wid: order.get(wid, 999))


def _figure_block(workload_id: str, caption: str) -> List[str]:
    return [
        "\\begin{figure}[p]",
        "\\centering",
        f"\\includegraphics[width=0.97\\linewidth]{{\\FigDir/{workload_id}_config_detailed.pdf}}",
        f"\\caption{{{caption}}}",
        "\\end{figure}",
    ]


def _resized_tabular(path: str) -> List[str]:
    return [
        "\\resizebox{\\linewidth}{!}{%",
        f"\\input{{{path}}}",
        "}",
    ]


def _pair_map(summary: Dict[str, Any]) -> Dict[str, Dict[str, Dict[str, Any]]]:
    out: Dict[str, Dict[str, Dict[str, Any]]] = {}
    for row in summary["pair_rows"]:
        out.setdefault(str(row["workload_id"]), {})[str(row["task_kind"])] = row
    return out


def _short_family_en(family: str) -> str:
    return "Time recursion" if family == "time_recursion" else "Luca/GF"


def _short_family_cn(family: str) -> str:
    return "时域递推" if family == "time_recursion" else "Luca/GF"


def _winner_factor(row: Dict[str, Any]) -> float:
    luca = float(row["median_seconds_luca"])
    time_family = float(row["median_seconds_time"])
    faster = min(luca, time_family)
    slower = max(luca, time_family)
    return slower / faster if faster > 0.0 else 0.0


def _verdict_text_en(pair_map: Dict[str, Dict[str, Dict[str, Any]]], workload_id: str) -> str:
    rows = pair_map.get(workload_id, {})
    diag = rows.get("diagnostic")
    curve = rows.get("curve")
    if not diag:
        return "The configuration figure also carries the direct speed verdict for this workload."
    text = (
        "Direct speed mapping for the configuration figure: "
        f"the diagnostic task is faster with {_short_family_en(str(diag['recommended_family']))} "
        f"(time={float(diag['median_seconds_time']):.4g}s, "
        f"luca={float(diag['median_seconds_luca']):.4g}s, "
        f"{_winner_factor(diag):.1f}x separation)."
    )
    if curve:
        if curve["recommended_family"] == diag["recommended_family"]:
            text += (
                " The curve task keeps the same winner "
                f"(time={float(curve['median_seconds_time']):.4g}s, "
                f"luca={float(curve['median_seconds_luca']):.4g}s)."
            )
        else:
            text += (
                " The curve task flips to "
                f"{_short_family_en(str(curve['recommended_family']))} "
                f"(time={float(curve['median_seconds_time']):.4g}s, "
                f"luca={float(curve['median_seconds_luca']):.4g}s)."
            )
    return text


def _verdict_text_cn(pair_map: Dict[str, Dict[str, Dict[str, Any]]], workload_id: str) -> str:
    rows = pair_map.get(workload_id, {})
    diag = rows.get("diagnostic")
    curve = rows.get("curve")
    if not diag:
        return "这张配置图同时承担该 workload 的直接速度结论。"
    text = (
        "与配置图直接对应的速度结论是："
        f"diagnostic 任务由{_short_family_cn(str(diag['recommended_family']))}更快"
        f"（time={float(diag['median_seconds_time']):.4g}s，"
        f"luca={float(diag['median_seconds_luca']):.4g}s，"
        f"相差 {_winner_factor(diag):.1f} 倍）。"
    )
    if curve:
        if curve["recommended_family"] == diag["recommended_family"]:
            text += (
                " curve 任务保持同一赢家"
                f"（time={float(curve['median_seconds_time']):.4g}s，"
                f"luca={float(curve['median_seconds_luca']):.4g}s）。"
            )
        else:
            text += (
                " curve 任务改为"
                f"{_short_family_cn(str(curve['recommended_family']))}更快"
                f"（time={float(curve['median_seconds_time']):.4g}s，"
                f"luca={float(curve['median_seconds_luca']):.4g}s）。"
            )
    return text


def _workload_section_en(pair_map: Dict[str, Dict[str, Dict[str, Any]]]) -> List[str]:
    specs = {spec.workload_id: spec for spec in workload_specs()}
    lines: List[str] = [
        "\\section{Workload Instantiations and Configuration Figures}",
        "Each workload is now documented inside this unified report, with its own detailed configuration figure and an explicit formula-level specialization of the two method families.",
        "\\begin{table}[H]",
        "\\centering\\small",
    ]
    lines.extend(_resized_tabular("\\TabDir/unified_workload_inventory_en.tex"))
    lines.extend(
        [
            "\\caption{The six benchmark workloads kept in the unified comparison.}",
            "\\end{table}",
        ]
    )

    lines.extend(
        [
            "\\subsection{RING-1T-paper}",
            "This workload is the analytic single-target ring benchmark. The resolvent family starts from the closed-form single-walker propagator",
            "\\begin{align}",
            "\\widetilde P_{n_0\\to n}(u) &= \\sum_{k=0}^{N-1} \\frac{h_k(n,n_0)}{1-u\\alpha_k},\\\\",
            "\\widetilde F_{n_0\\to m}(u) &= \\frac{\\widetilde P_{n_0\\to m}(u)}{\\widetilde P_{m\\to m}(u)},",
            "\\end{align}",
            "followed by an AW/Cauchy inversion on a radius-$r$ circle. The time solver instead iterates the absorbing chain directly.",
            _verdict_text_en(pair_map, "RING-1T-paper"),
        ]
    )
    lines.extend(_figure_block("RING-1T-paper", "Detailed ring geometry for the paper-like single-target shortcut benchmark."))

    lines.extend(
        [
            "\\clearpage",
            "\\subsection{ENC-FIXED}",
            "The fixed-site encounter workload is a single-target first-passage problem on the pair chain. The GF family evaluates the defect-free pair propagator and closes a one-target renewal equation:",
            "\\begin{align}",
            "G_0\\big((n_0,m_0)\\to(x,y);z\\big) &= \\frac{1}{N^2}\\sum_{k_1,k_2}\\frac{h_{k_1}(x,n_0)h_{k_2}(y,m_0)}{1-z\\lambda^{(1)}_{k_1}\\lambda^{(2)}_{k_2}},\\\\",
            "\\widetilde f_{\\delta}(z) &= \\frac{G\\big((n_0,m_0)\\to(\\delta,\\delta);z\\big)}{G\\big((\\delta,\\delta)\\to(\\delta,\\delta);z\\big)}.",
            "\\end{align}",
            "The time family evolves the absorbed pair density exactly on the $N^2$ state space.",
            _verdict_text_en(pair_map, "ENC-FIXED"),
        ]
    )
    lines.extend(_figure_block("ENC-FIXED", "Detailed configuration for the fixed-site encounter benchmark, including the single pair-state target."))

    lines.extend(
        [
            "\\clearpage",
            "\\subsection{ENC-ANY}",
            "The anywhere-encounter workload promotes the target from one pair-state to the full diagonal set $D=\\{(x,x):x\\in\\mathbb Z_N\\}$. The GF family uses the same defect-free pair propagator but now closes a multi-target renewal system:",
            "\\begin{align}",
            "G(z) &= G_0(z) + z\\,G_0(z)U\\left(I-zV^{\\top}G_0(z)U\\right)^{-1}V^{\\top}G_0(z),\\\\",
            "\\widetilde{\\mathbf f}_D(z) &= G_{DD}(z)^{-1}G_{Ds}(z),\\\\",
            "\\widetilde f_{\\mathrm{enc}}(z) &= \\mathbf 1^{\\top}\\widetilde{\\mathbf f}_D(z).",
            "\\end{align}",
            "Here the shortcut acts as a line defect on the pair torus, so the Woodbury correction is the bridge between the defect-free pair spectrum and the actual encounter PGF.",
            _verdict_text_en(pair_map, "ENC-ANY"),
        ]
    )
    lines.extend(_figure_block("ENC-ANY", "Detailed configuration for the anywhere-encounter benchmark, including the diagonal target set and the shortcut-induced defect line."))

    lines.extend(
        [
            "\\clearpage",
            "\\subsection{TT-C1}",
            "C1 is the practical two-target corridor benchmark. The GF family uses a defect-reduced resolvent instead of a full dense transient solve:",
            "\\begin{align}",
            "Q &= Q_0 + U\\Delta V^{\\top},\\\\",
            "(I-zQ)^{-1} &= (I-zQ_0)^{-1} + z(I-zQ_0)^{-1}U\\left(I-zV^{\\top}(I-zQ_0)^{-1}U\\Delta\\right)^{-1}V^{\\top}(I-zQ_0)^{-1},\\\\",
            "\\widetilde{\\mathbf f}(z) &= G_{TT}(z)^{-1}G_{Ts}(z),",
            "\\end{align}",
            "where $T=\\{m_1,m_2\\}$. The time solver is the sparse exact absorbing recursion on the transient graph, continued to the long horizon actually needed by the scientific claim.",
            _verdict_text_en(pair_map, "TT-C1"),
        ]
    )
    lines.extend(_figure_block("TT-C1", "Detailed C1 geometry, showing both the full local-bias field and the corridor support that determines the defect-reduced dimension."))

    lines.extend(
        [
            "\\clearpage",
            "\\subsection{TT-LF1}",
            "TT-LF1 keeps the same two-target mathematics but collapses the defect support to an ultra-sparse local perturbation. This is the in-repo positive anchor where the defect-reduced GF route can beat long-horizon sparse recursion.",
            _verdict_text_en(pair_map, "TT-LF1"),
        ]
    )
    lines.extend(_figure_block("TT-LF1", "Detailed LF1 sparse-defect geometry used as the positive Luca/GF anchor."))

    lines.extend(
        [
            "\\clearpage",
            "\\subsection{REF-S0}",
            "REF-S0 is the reflecting low-defect control. The GF family remains a single-target resolvent solve, but here the full AW route is still numerically feasible because the defect count is deliberately kept small:",
            "\\begin{align}",
            "\\widetilde F_{s\\to m}(z) &= \\frac{G_{sm}(z)}{G_{mm}(z)},\\\\",
            "f(t) &= [z^t]\\widetilde F_{s\\to m}(z).",
            "\\end{align}",
            "The time family is the standard exact absorbing recursion on the reflecting lattice.",
            _verdict_text_en(pair_map, "REF-S0"),
        ]
    )
    lines.extend(_figure_block("REF-S0", "Detailed reflecting low-defect S0 control geometry, highlighting the sticky site and the partially permeable barrier."))
    return lines


def _workload_section_cn(pair_map: Dict[str, Dict[str, Dict[str, Any]]]) -> List[str]:
    lines: List[str] = [
        "\\section{六个 Workload 的实例化与详细配置图}",
        "六个 workload 现在都在这份统一报告里直接说明：每个案例都给出详细配置图，并把两大家族在该案例上的公式实例化写清楚。",
        "\\begin{table}[H]",
        "\\centering\\small",
        "\\resizebox{\\linewidth}{!}{%",
        "\\input{\\TabDir/unified_workload_inventory_cn.tex}",
        "}",
        "\\caption{统一比较里保留的六个 workload。}",
        "\\end{table}",
        "\\subsection{RING-1T-paper}",
        "这是解析单目标 ring benchmark。生成函数家族从闭式单 walker 传播子出发：",
        "\\begin{align}",
        "\\widetilde P_{n_0\\to n}(u) &= \\sum_{k=0}^{N-1} \\frac{h_k(n,n_0)}{1-u\\alpha_k},\\\\",
        "\\widetilde F_{n_0\\to m}(u) &= \\frac{\\widetilde P_{n_0\\to m}(u)}{\\widetilde P_{m\\to m}(u)},",
        "\\end{align}",
        "再沿半径 $r$ 的圆周做 AW/Cauchy 反演。时域家族则直接推进吸收链。",
        _verdict_text_cn(pair_map, "RING-1T-paper"),
    ]
    lines.extend(_figure_block("RING-1T-paper", "paper-like 单目标 shortcut benchmark 的详细 ring 几何。"))

    lines.extend(
        [
            "\\clearpage",
            "\\subsection{ENC-FIXED}",
            "fixed-site encounter 在 pair chain 上是一个单 target 首达问题。GF 家族先写 defect-free pair propagator，再闭合单 target renewal：",
            "\\begin{align}",
            "G_0\\big((n_0,m_0)\\to(x,y);z\\big) &= \\frac{1}{N^2}\\sum_{k_1,k_2}\\frac{h_{k_1}(x,n_0)h_{k_2}(y,m_0)}{1-z\\lambda^{(1)}_{k_1}\\lambda^{(2)}_{k_2}},\\\\",
            "\\widetilde f_{\\delta}(z) &= \\frac{G\\big((n_0,m_0)\\to(\\delta,\\delta);z\\big)}{G\\big((\\delta,\\delta)\\to(\\delta,\\delta);z\\big)}.",
            "\\end{align}",
            "时域家族则在 $N^2$ 状态空间上精确推进吸收 pair density。",
            _verdict_text_cn(pair_map, "ENC-FIXED"),
        ]
    )
    lines.extend(_figure_block("ENC-FIXED", "fixed-site encounter benchmark 的详细配置图，其中 pair-state target 是单点 $(\\delta,\\delta)$。"))

    lines.extend(
        [
            "\\clearpage",
            "\\subsection{ENC-ANY}",
            "anywhere encounter 把 target 从单点提升成整条对角线 $D=\\{(x,x):x\\in\\mathbb Z_N\\}$。GF 家族仍从 defect-free pair propagator 出发，但需要多 target renewal：",
            "\\begin{align}",
            "G(z) &= G_0(z) + z\\,G_0(z)U\\left(I-zV^{\\top}G_0(z)U\\right)^{-1}V^{\\top}G_0(z),\\\\",
            "\\widetilde{\\mathbf f}_D(z) &= G_{DD}(z)^{-1}G_{Ds}(z),\\\\",
            "\\widetilde f_{\\mathrm{enc}}(z) &= \\mathbf 1^{\\top}\\widetilde{\\mathbf f}_D(z).",
            "\\end{align}",
            "shortcut 在 pair torus 上对应一条 defect line，因此 Woodbury 修正就是把 defect-free 频谱恢复成真实 encounter PGF 的关键步骤。",
            _verdict_text_cn(pair_map, "ENC-ANY"),
        ]
    )
    lines.extend(_figure_block("ENC-ANY", "anywhere encounter benchmark 的详细配置图：原 ring、对角 target set 与 shortcut 对应的 defect line 同时展示。"))

    lines.extend(
        [
            "\\clearpage",
            "\\subsection{TT-C1}",
            "C1 是最重要的 two-target 实务 benchmark。GF 家族不是去做完整 dense transient solve，而是做 defect-reduced resolvent：",
            "\\begin{align}",
            "Q &= Q_0 + U\\Delta V^{\\top},\\\\",
            "(I-zQ)^{-1} &= (I-zQ_0)^{-1} + z(I-zQ_0)^{-1}U\\left(I-zV^{\\top}(I-zQ_0)^{-1}U\\Delta\\right)^{-1}V^{\\top}(I-zQ_0)^{-1},\\\\",
            "\\widetilde{\\mathbf f}(z) &= G_{TT}(z)^{-1}G_{Ts}(z),",
            "\\end{align}",
            "其中 $T=\\{m_1,m_2\\}$。时域家族则是在瞬态图上做 sparse exact recursion，并延伸到支撑科学结论所需的长时窗。",
            _verdict_text_cn(pair_map, "TT-C1"),
        ]
    )
    lines.extend(_figure_block("TT-C1", "C1 的详细几何图：同时展示完整 local-bias field 与决定 defect-reduced 维数的 corridor support。"))

    lines.extend(
        [
            "\\clearpage",
            "\\subsection{TT-LF1}",
            "TT-LF1 复用相同的 two-target 数学，但把 defect support 压到极稀疏，因此成为本仓库里 Luca/GF 占优的正锚点。",
            _verdict_text_cn(pair_map, "TT-LF1"),
        ]
    )
    lines.extend(_figure_block("TT-LF1", "LF1 稀疏缺陷正锚点的详细配置图。"))

    lines.extend(
        [
            "\\clearpage",
            "\\subsection{REF-S0}",
            "REF-S0 是 reflecting 低缺陷控制例。GF 家族仍然是单 target resolvent + 反演，但在这个案例里 full AW 还保持可行：",
            "\\begin{align}",
            "\\widetilde F_{s\\to m}(z) &= \\frac{G_{sm}(z)}{G_{mm}(z)},\\\\",
            "f(t) &= [z^t]\\widetilde F_{s\\to m}(z).",
            "\\end{align}",
            "时域家族则是标准的 reflecting 吸收递推。",
            _verdict_text_cn(pair_map, "REF-S0"),
        ]
    )
    lines.extend(_figure_block("REF-S0", "reflecting 低缺陷 S0 控制案例的详细几何图，重点标出 sticky site 与部分透过 barrier。"))
    return lines


def _build_tex_en(summary: Dict[str, Any]) -> str:
    diag = _agg(summary, "diagnostic")
    curve = _agg(summary, "curve")
    luca_diag = ", ".join(_wins(summary, "diagnostic", "luca_gf")) or "none"
    time_diag = ", ".join(_wins(summary, "diagnostic", "time_recursion")) or "none"
    luca_curve = ", ".join(_wins(summary, "curve", "luca_gf")) or "none"
    time_curve = ", ".join(_wins(summary, "curve", "time_recursion")) or "none"
    pair_map = _pair_map(summary)

    lines: List[str] = [
        "\\documentclass[11pt]{article}",
        "\\usepackage[a4paper,margin=0.95in]{geometry}",
        "\\usepackage{amsmath,amssymb,mathtools,booktabs,graphicx,float,hyperref,enumitem,longtable,array,pdflscape}",
        "\\hypersetup{hidelinks}",
        "\\setlength{\\emergencystretch}{2em}",
        "\\newcommand{\\FigDir}{../figures}",
        "\\newcommand{\\TabDir}{../tables}",
        "\\title{Unified Computational Benchmark for First-Passage Problems\\\\Luca / Generating-Function Family vs. Time-Domain Recursion Family}",
        "\\author{valley-k-small automated report}",
        "\\date{\\today}",
        "\\begin{document}",
        "\\maketitle",
        "\\begin{abstract}",
        "This document is the single active computational-method comparison report in the repository. ",
        "It keeps the scientific reports separate, but collapses the comparison line into one bilingual benchmark with six workloads. ",
        "The benchmark rule is \\emph{practical native-task fairness}: each report is timed on the task it actually needed to complete, rather than on an artificially synchronized full-tail horizon. ",
        f"Under the diagnostic protocol the median ratio $t_{{\\mathrm{{time}}}}/t_{{\\mathrm{{Luca}}}}$ is {_fmt(diag.get('median_speedup_time_over_luca', 0.0), 4)}; ",
        f"time recursion wins on {time_diag}, while Luca/GF wins on {luca_diag}. ",
        f"Under the curve protocol the median ratio is {_fmt(curve.get('median_speedup_time_over_luca', 0.0), 4)}; ",
        f"time recursion wins on {time_curve}, while Luca/GF wins on {luca_curve}.",
        "\\end{abstract}",
        "\\section{Goal and Comparison Rule}",
        "We compare only two families.",
        "\\begin{itemize}[leftmargin=1.4em]",
        "\\item \\textbf{Luca / generating-function family}: closed-form propagators, defect-reduced resolvent recovery, renewal in transform space, and AW/Cauchy-FFT inversion.",
        "\\item \\textbf{Time-domain recursion family}: exact propagation on the transient state space, including sparse absorbing recursion and absorbed pair-distribution updates.",
        "\\end{itemize}",
        "The main benchmark is not a forced full-tail comparison. It is a report-production comparison: how much time does each family need to deliver the quantity that the scientific report actually required?",
        "\\section{Unified Notation and Runtime Protocol}",
        "Let $X_t$ be a discrete-time Markov chain, $T$ a target set, $\\tau_T=\\inf\\{t\\ge 1:X_t\\in T\\}$ the first-passage time,",
        "\\begin{align}",
        "f_T(t) &= \\mathbb P(\\tau_T=t),\\\\",
        "S_T(t) &= \\mathbb P(\\tau_T>t),\\\\",
        "\\widetilde f_T(z) &= \\sum_{t\\ge 1} f_T(t) z^t,\\\\",
        "\\widetilde P_{ij}(z) &= \\sum_{t\\ge 0} \\mathbb P_i(X_t=j) z^t = \\bigl[(I-zP)^{-1}\\bigr]_{ij}.",
        "\\end{align}",
        "For single-target problems, renewal closes immediately:",
        "\\begin{align}",
        "\\widetilde f_{i\\to m}(z)=\\frac{\\widetilde P_{im}(z)}{\\widetilde P_{mm}(z)}.",
        "\\end{align}",
        "For multiple targets, renewal becomes a small linear system on target-to-target propagators. ",
        "All timings use single-thread BLAS, one warm-up run, three measured runs, and the median wall time as the reported benchmark value.",
        "\\section{Luca / Generating-Function Family: Mathematical Spine}",
        "The common transform-domain workflow is:",
        "\\begin{enumerate}[leftmargin=1.5em]",
        "\\item Build a defect-free propagator or a closed-form single-walker PGF.",
        "\\item Recover the defected propagator through a finite-dimensional Woodbury or determinant system.",
        "\\item Close a one-target or multi-target renewal relation to obtain the FPT generating function.",
        "\\item Invert the PGF numerically with an AW/Cauchy-FFT contour.",
        "\\end{enumerate}",
        "The inversion step evaluates",
        "\\begin{align}",
        "f(t) = [z^t]\\widetilde f(z) = \\frac{1}{2\\pi i}\\oint_{|z|=r} \\frac{\\widetilde f(z)}{z^{t+1}}\\,dz",
        "\\approx \\frac{r^{-t}}{m}\\sum_{k=0}^{m-1}\\widetilde f\\!\\left(re^{2\\pi i k/m}\\right)e^{-2\\pi i kt/m}.",
        "\\end{align}",
        "This is the shared numerical shell behind the ring, encounter, two-target, and reflecting GF workloads.",
        "\\subsection{Encounter-Specific GF Route}",
        "For the two-walker shortcut encounter, the defect-free pair propagator is",
        "\\begin{align}",
        "G_0\\big((n_0,m_0)\\to(x,y);z\\big)=\\frac{1}{N^2}\\sum_{k_1,k_2}\\frac{h_{k_1}(x,n_0)h_{k_2}(y,m_0)}{1-z\\lambda_{k_1}^{(1)}\\lambda_{k_2}^{(2)}}.",
        "\\end{align}",
        "The shortcut becomes a line defect on the pair torus and is restored by",
        "\\begin{align}",
        "G(z)=G_0(z)+z\\,G_0(z)U\\left(I-zV^{\\top}G_0(z)U\\right)^{-1}V^{\\top}G_0(z).",
        "\\end{align}",
        "A1 and A8 are therefore not the production solver for the encounter report; they are the spectral anchor from which the new timed GF route is constructed.",
        "\\section{Time-Domain Recursion Family: Mathematical Spine}",
        "The time-domain family works directly with absorbing transient updates. If $Q$ is the transient transition matrix and $r$ the transient-to-target flux vector, then",
        "\\begin{align}",
        "u_{t+1} &= u_t Q,\\\\",
        "f(t+1) &= u_t r,\\\\",
        "S(t+1) &= u_{t+1}\\mathbf 1.",
        "\\end{align}",
        "For two-target problems, $r$ becomes a two-column target flux block. For the pair encounter, the exact recursion is naturally written in matrix form:",
        "\\begin{align}",
        "J_{t+1} &= P_1^{\\top}J_tP_2,\\\\",
        "f_{\\mathrm{enc}}(t+1) &= \\operatorname{tr}(J_{t+1}),",
        "\\end{align}",
        "with the diagonal or designated encounter site zeroed after each step to enforce absorption. ",
        "No asymptotic approximation is used here; the family name refers only to the domain in which the update is carried out.",
    ]
    lines.extend(_workload_section_en(pair_map))
    lines.extend(
        [
            "\\clearpage",
            "\\section{Main Benchmark Results}",
            "\\begin{table}[H]",
            "\\centering\\small",
            "\\resizebox{\\linewidth}{!}{%",
            "\\input{\\TabDir/unified_complexity_table.tex}",
            "}",
            "\\caption{Family-level complexity summary.}",
            "\\end{table}",
            "\\begin{table}[H]",
            "\\centering\\small",
            "\\resizebox{\\linewidth}{!}{%",
            "\\input{\\TabDir/unified_solver_map.tex}",
            "}",
            "\\caption{Family-internal solver mapping for the six workloads.}",
            "\\end{table}",
            "\\begin{figure}[H]",
            "\\centering",
            "\\includegraphics[width=0.98\\linewidth]{\\FigDir/unified_runtime_config_overview.pdf}",
            "\\caption{One-glance benchmark overview. The numbered mini-panels 1--6 are the six workload configurations, and the numbered groups on the top runtime chart follow the same order. This is the main practical benchmark figure used in the report.}",
            "\\end{figure}",
            "\\begin{table}[H]",
            "\\centering\\small",
            "\\resizebox{\\linewidth}{!}{%",
            "\\input{\\TabDir/unified_runtime_diagnostic_en.tex}",
            "}",
            "\\caption{Diagnostic-task runtime table.}",
            "\\end{table}",
            "\\begin{figure}[H]",
            "\\centering",
            "\\includegraphics[width=0.98\\linewidth]{\\FigDir/unified_speedup_by_workload.pdf}",
            "\\caption{Per-workload ratio $t_{\\mathrm{time}}/t_{\\mathrm{Luca}}$. Ratios above one favor the Luca/GF family.}",
            "\\end{figure}",
            "\\begin{figure}[H]",
            "\\centering",
            "\\includegraphics[width=0.98\\linewidth]{\\FigDir/unified_runtime_curve.pdf}",
            "\\caption{Curve-task runtime, kept secondary so that long-tail costs do not overwrite the practical report-production benchmark.}",
            "\\end{figure}",
            "\\begin{table}[H]",
            "\\centering\\small",
            "\\resizebox{\\linewidth}{!}{%",
            "\\input{\\TabDir/unified_runtime_curve_en.tex}",
            "}",
            "\\caption{Curve-task runtime table.}",
            "\\end{table}",
            "\\section{Recommendation Matrix}",
            "\\begin{table}[H]",
            "\\centering\\small",
            "\\resizebox{\\linewidth}{!}{%",
            "\\input{\\TabDir/unified_recommendation_en.tex}",
            "}",
            "\\caption{Decision matrix derived from the six-workload benchmark.}",
            "\\end{table}",
            "\\section{Conclusion}",
            "The comparison line is now fully centralized in one report. The scientific reports remain focused on science, while this document owns the algorithmic comparison, the fairness rule, the workload inventory, and the implementation-level guidance for choosing between transform-domain and time-domain solvers.",
            "\\clearpage",
            "\\appendix",
            "\\section{Appendix A: Symbol Table and Variable Mapping}",
            "\\begin{align}",
            "P &: \\text{full transition operator}, & Q &: \\text{transient transition operator},\\\\",
            "r &: \\text{transient-to-target flux}, & U\\Delta V^{\\top} &: \\text{defect update},\\\\",
            "G_0(z) &: (I-zQ_0)^{-1}, & G(z) &: (I-zQ)^{-1},\\\\",
            "m &: \\text{AW FFT length}, & r &: \\text{AW contour radius}.",
            "\\end{align}",
            "\\section{Appendix B: Detailed GF Derivations}",
            "The GF family reduces every workload to the same algebraic template. Starting from a defect-free $Q_0$, write",
            "\\begin{align}",
            "Q &= Q_0 + U\\Delta V^{\\top},\\\\",
            "I-zQ &= (I-zQ_0)\\Bigl[I-z(I-zQ_0)^{-1}U\\Delta V^{\\top}\\Bigr],\\\\",
            "(I-zQ)^{-1} &= (I-zQ_0)^{-1} + z(I-zQ_0)^{-1}U\\Bigl[I-zV^{\\top}(I-zQ_0)^{-1}U\\Delta\\Bigr]^{-1}V^{\\top}(I-zQ_0)^{-1}.",
            "\\end{align}",
            "For a target set $T=\\{m_1,\\dots,m_K\\}$, renewal is written as",
            "\\begin{align}",
            "G_{sT}(z)=\\widetilde{\\mathbf f}_T(z)^{\\top}G_{TT}(z),\\\\",
            "\\widetilde{\\mathbf f}_T(z)=G_{TT}(z)^{-1}G_{Ts}(z).",
            "\\end{align}",
            "The one-target formula is the $K=1$ specialization of this matrix equation.",
            "\\section{Appendix C: Detailed Time-Recursion Derivations}",
            "Given the transient state vector $u_t$, exact recursion uses",
            "\\begin{align}",
            "u_0 &= e_s,\\\\",
            "u_{t+1} &= u_tQ,\\\\",
            "f(t+1) &= u_tr,\\\\",
            "S(t+1) &= u_{t+1}\\mathbf 1. ",
            "\\end{align}",
            "For two-target problems, let $R=[r^{(1)}\\;r^{(2)}]$ and then $f_1(t+1)=u_tr^{(1)}$, $f_2(t+1)=u_tr^{(2)}$. ",
            "For pair encounters, the matrix recursion form is numerically convenient because the encounter condition is a structured absorbing set on the pair torus.",
            "\\section{Appendix D: Per-Workload Formula Specialization}",
            "RING-1T-paper uses a scalar renewal. ENC-FIXED uses a single-target renewal on the pair chain. ENC-ANY uses a diagonal target-set renewal on the pair torus. ",
            "TT-C1 and TT-LF1 use a two-target renewal after defect-reduced selected-propagator recovery. REF-S0 uses the single-target reflecting resolvent. ",
            "These are exactly the formulas instantiated in Section 5 alongside the detailed configuration figures.",
            "\\section{Appendix E: Complexity, Memory, Error Metrics, and Benchmark Protocol}",
            "The runtime comparison is accepted only after a same-window numerical agreement check between the two families. ",
            "For each workload, the overlap window is reported through $L^1$, $L^{\\infty}$, and a peak-location consistency flag. ",
            "This means wall time is never reported without a paired numerical sanity check.",
            "\\section{Appendix F: Embedded Historical Full-FPT Note}",
            "The repository no longer keeps an external active compare report for the old fixed full-tail fairness question. ",
            "Instead, the historical note is embedded here so that the active comparison line remains single-source.",
            "\\begin{table}[H]",
            "\\centering\\small",
            "\\resizebox{\\linewidth}{!}{%",
            "\\input{\\TabDir/unified_appendix_fairness_en.tex}",
            "}",
            "\\caption{Embedded historical fairness note retained inside the unified report.}",
            "\\end{table}",
            "\\end{document}",
        ]
    )
    return "\n".join(lines) + "\n"


def _build_tex_cn(summary: Dict[str, Any]) -> str:
    diag = _agg(summary, "diagnostic")
    curve = _agg(summary, "curve")
    luca_diag = "、".join(_wins(summary, "diagnostic", "luca_gf")) or "无"
    time_diag = "、".join(_wins(summary, "diagnostic", "time_recursion")) or "无"
    luca_curve = "、".join(_wins(summary, "curve", "luca_gf")) or "无"
    time_curve = "、".join(_wins(summary, "curve", "time_recursion")) or "无"
    pair_map = _pair_map(summary)

    lines: List[str] = [
        "\\documentclass[11pt]{ctexart}",
        "\\usepackage[a4paper,margin=0.95in]{geometry}",
        "\\usepackage{amsmath,amssymb,mathtools,booktabs,graphicx,float,hyperref,enumitem,longtable,array,pdflscape}",
        "\\hypersetup{hidelinks}",
        "\\setlength{\\emergencystretch}{2em}",
        "\\newcommand{\\FigDir}{../figures}",
        "\\newcommand{\\TabDir}{../tables}",
        "\\title{统一计算方法比较主稿\\\\Luca / 生成函数家族 vs. 时域递推家族}",
        "\\author{valley-k-small 自动化报告}",
        "\\date{\\today}",
        "\\begin{document}",
        "\\maketitle",
        "\\begin{abstract}",
        "这份文稿是仓库里唯一活跃的计算方法比较报告。科学主报告继续各自独立，但方法比较线统一收敛到这里，并固定保留六个 workload。 ",
        "主公平口径采用\\emph{实务 native-task}：每份科学报告实际需要完成什么任务，就按那个任务去计时，而不是强行统一 full-tail。 ",
        f"在 diagnostic 协议下，中位比值 $t_{{\\mathrm{{time}}}}/t_{{\\mathrm{{Luca}}}}={_fmt(diag.get('median_speedup_time_over_luca', 0.0), 4)}$；",
        f"时域递推赢在 {time_diag}，Luca/GF 赢在 {luca_diag}。 ",
        f"在 curve 协议下，中位比值为 {_fmt(curve.get('median_speedup_time_over_luca', 0.0), 4)}；",
        f"时域递推赢在 {time_curve}，Luca/GF 赢在 {luca_curve}。",
        "\\end{abstract}",
        "\\section{研究目标与比较口径}",
        "这里只比较两大家族：",
        "\\begin{itemize}[leftmargin=1.4em]",
        "\\item \\textbf{Luca / 生成函数家族}：闭式传播子、defect-reduced resolvent、变换域 renewal、AW/Cauchy-FFT 反演。",
        "\\item \\textbf{时域递推家族}：在瞬态状态空间上做精确推进，包括 sparse exact recursion 与 absorbed pair-distribution update。",
        "\\end{itemize}",
        "主 benchmark 不是强制 full-tail 公平，而是“为了交付当前科学结论，哪个家族更合适”。",
        "\\section{统一记号与 runtime 协议}",
        "设 $X_t$ 为离散时间 Markov 链，$T$ 为 target set，$\\tau_T=\\inf\\{t\\ge 1:X_t\\in T\\}$ 为首达时间，则",
        "\\begin{align}",
        "f_T(t) &= \\mathbb P(\\tau_T=t),\\\\",
        "S_T(t) &= \\mathbb P(\\tau_T>t),\\\\",
        "\\widetilde f_T(z) &= \\sum_{t\\ge 1} f_T(t) z^t,\\\\",
        "\\widetilde P_{ij}(z) &= \\sum_{t\\ge 0} \\mathbb P_i(X_t=j) z^t = \\bigl[(I-zP)^{-1}\\bigr]_{ij}.",
        "\\end{align}",
        "单 target 情况下 renewal 直接闭合为",
        "\\begin{align}",
        "\\widetilde f_{i\\to m}(z)=\\frac{\\widetilde P_{im}(z)}{\\widetilde P_{mm}(z)}.",
        "\\end{align}",
        "多 target 情况则在 target-to-target propagator 上变成一个小线性系统。 ",
        "全部 runtime 均采用单线程 BLAS、1 次 warm-up、3 次 measured，再取中位 wall time。",
        "\\section{Luca / 生成函数家族：完整数学主线}",
        "变换域家族的统一流程是：",
        "\\begin{enumerate}[leftmargin=1.5em]",
        "\\item 先写 defect-free propagator 或闭式单 walker PGF；",
        "\\item 再通过有限维 Woodbury / determinant 系统恢复 defected propagator；",
        "\\item 再闭合单 target 或多 target renewal，得到 FPT 的 generating function；",
        "\\item 最后在半径 $r$ 的圆周上做 AW/Cauchy-FFT 反演。",
        "\\end{enumerate}",
        "反演公式统一写成",
        "\\begin{align}",
        "f(t)=[z^t]\\widetilde f(z)=\\frac{1}{2\\pi i}\\oint_{|z|=r}\\frac{\\widetilde f(z)}{z^{t+1}}\\,dz",
        "\\approx \\frac{r^{-t}}{m}\\sum_{k=0}^{m-1}\\widetilde f\\!\\left(re^{2\\pi i k/m}\\right)e^{-2\\pi i kt/m}.",
        "\\end{align}",
        "\\subsection{Encounter 的 GF 路线}",
        "对于 two-walker shortcut encounter，defect-free pair propagator 为",
        "\\begin{align}",
        "G_0\\big((n_0,m_0)\\to(x,y);z\\big)=\\frac{1}{N^2}\\sum_{k_1,k_2}\\frac{h_{k_1}(x,n_0)h_{k_2}(y,m_0)}{1-z\\lambda_{k_1}^{(1)}\\lambda_{k_2}^{(2)}}.",
        "\\end{align}",
        "shortcut 在 pair torus 上变成 line defect，并通过",
        "\\begin{align}",
        "G(z)=G_0(z)+z\\,G_0(z)U\\left(I-zV^{\\top}G_0(z)U\\right)^{-1}V^{\\top}G_0(z)",
        "\\end{align}",
        "恢复真实 propagator。A1 与 A8 在这里不是主求解器，而是新 timed GF 路线的频谱锚点。",
        "\\section{时域递推家族：完整数学主线}",
        "时域家族直接推进吸收瞬态量。若 $Q$ 为瞬态转移矩阵、$r$ 为瞬态到 target 的流量，则",
        "\\begin{align}",
        "u_{t+1} &= u_tQ,\\\\",
        "f(t+1) &= u_tr,\\\\",
        "S(t+1) &= u_{t+1}\\mathbf 1.",
        "\\end{align}",
        "对 two-target 问题，把 $r$ 换成两列 target flux block 即可。对 encounter，最自然的写法是 pair recursion：",
        "\\begin{align}",
        "J_{t+1} &= P_1^{\\top}J_tP_2,\\\\",
        "f_{\\mathrm{enc}}(t+1) &= \\operatorname{tr}(J_{t+1}).",
        "\\end{align}",
        "这里每一步都把对角线或指定 encounter site 清零，从而实现精确吸收。全文统一不用“渐进递推”这个词；这里的 recursion 是精确时域推进。",
    ]
    lines.extend(_workload_section_cn(pair_map))
    lines.extend(
        [
            "\\clearpage",
            "\\section{主 benchmark 结果}",
            "\\begin{table}[H]",
            "\\centering\\small",
            "\\resizebox{\\linewidth}{!}{%",
            "\\input{\\TabDir/unified_complexity_table.tex}",
            "}",
            "\\caption{家族级复杂度总表。}",
            "\\end{table}",
            "\\begin{table}[H]",
            "\\centering\\small",
            "\\resizebox{\\linewidth}{!}{%",
            "\\input{\\TabDir/unified_solver_map.tex}",
            "}",
            "\\caption{六个 workload 的家族内部 solver 映射。}",
            "\\end{table}",
            "\\begin{figure}[H]",
            "\\centering",
            "\\includegraphics[width=0.98\\linewidth]{\\FigDir/unified_runtime_config_overview.pdf}",
            "\\caption{一目了然总览图。下方 1--6 号小图就是六个 workload 的配置图，上方 runtime 主图中的 1--6 号柱组与之按同样顺序一一对应。这是本报告的主 benchmark 图。}",
            "\\end{figure}",
            "\\begin{table}[H]",
            "\\centering\\small",
            "\\resizebox{\\linewidth}{!}{%",
            "\\input{\\TabDir/unified_runtime_diagnostic_cn.tex}",
            "}",
            "\\caption{diagnostic-task runtime 表。}",
            "\\end{table}",
            "\\begin{figure}[H]",
            "\\centering",
            "\\includegraphics[width=0.98\\linewidth]{\\FigDir/unified_speedup_by_workload.pdf}",
            "\\caption{逐 workload 的速度比 $t_{\\mathrm{time}}/t_{\\mathrm{Luca}}$。大于 1 表示 Luca/GF 更快。}",
            "\\end{figure}",
            "\\begin{figure}[H]",
            "\\centering",
            "\\includegraphics[width=0.98\\linewidth]{\\FigDir/unified_runtime_curve.pdf}",
            "\\caption{curve-task runtime。该口径刻意置于次级位置，避免长尾成本覆盖主 benchmark。}",
            "\\end{figure}",
            "\\begin{table}[H]",
            "\\centering\\small",
            "\\resizebox{\\linewidth}{!}{%",
            "\\input{\\TabDir/unified_runtime_curve_cn.tex}",
            "}",
            "\\caption{curve-task runtime 表。}",
            "\\end{table}",
            "\\section{推荐矩阵}",
            "\\begin{table}[H]",
            "\\centering\\small",
            "\\resizebox{\\linewidth}{!}{%",
            "\\input{\\TabDir/unified_recommendation_cn.tex}",
            "}",
            "\\caption{由六个 workload benchmark 导出的推荐矩阵。}",
            "\\end{table}",
            "\\section{结论}",
            "方法比较线现在完全收束到这一份报告。科学主报告继续讲科学，而这份文稿统一负责算法比较、fairness rule、workload inventory 与选型建议。",
            "\\clearpage",
            "\\appendix",
            "\\section{附录 A：符号表与变量映射}",
            "\\begin{align}",
            "P &: \\text{完整转移算子}, & Q &: \\text{瞬态转移矩阵},\\\\",
            "r &: \\text{瞬态到 target 的流量}, & U\\Delta V^{\\top} &: \\text{defect 更新},\\\\",
            "G_0(z) &: (I-zQ_0)^{-1}, & G(z) &: (I-zQ)^{-1},\\\\",
            "m &: \\text{AW FFT 长度}, & r &: \\text{AW 轮廓半径}.",
            "\\end{align}",
            "\\section{附录 B：GF 家族完整推导}",
            "GF 家族把所有 workload 都写进同一代数模板。由 defect-free $Q_0$ 出发，记",
            "\\begin{align}",
            "Q &= Q_0 + U\\Delta V^{\\top},\\\\",
            "I-zQ &= (I-zQ_0)\\Bigl[I-z(I-zQ_0)^{-1}U\\Delta V^{\\top}\\Bigr],\\\\",
            "(I-zQ)^{-1} &= (I-zQ_0)^{-1} + z(I-zQ_0)^{-1}U\\Bigl[I-zV^{\\top}(I-zQ_0)^{-1}U\\Delta\\Bigr]^{-1}V^{\\top}(I-zQ_0)^{-1}.",
            "\\end{align}",
            "若 target set 为 $T=\\{m_1,\\dots,m_K\\}$，则 renewal 写成",
            "\\begin{align}",
            "G_{sT}(z)=\\widetilde{\\mathbf f}_T(z)^{\\top}G_{TT}(z),\\\\",
            "\\widetilde{\\mathbf f}_T(z)=G_{TT}(z)^{-1}G_{Ts}(z).",
            "\\end{align}",
            "单 target 公式正是这个矩阵方程在 $K=1$ 时的退化。",
            "\\section{附录 C：时域递推家族完整推导}",
            "给定瞬态状态向量 $u_t$，精确递推统一写成",
            "\\begin{align}",
            "u_0 &= e_s,\\\\",
            "u_{t+1} &= u_tQ,\\\\",
            "f(t+1) &= u_tr,\\\\",
            "S(t+1) &= u_{t+1}\\mathbf 1.",
            "\\end{align}",
            "对 two-target 问题，让 $R=[r^{(1)}\\;r^{(2)}]$，于是 $f_1(t+1)=u_tr^{(1)}$、$f_2(t+1)=u_tr^{(2)}$。对 pair encounter，则矩阵递推形式更方便，因为吸收集在 pair torus 上具有结构。",
            "\\section{附录 D：六个 workload 的逐例公式展开}",
            "RING-1T-paper 是标量 renewal；ENC-FIXED 是 pair chain 上的单 target renewal；ENC-ANY 是 pair torus 对角集上的多 target renewal；TT-C1 与 TT-LF1 是 defect-reduced selected-propagator 恢复之后的两目标 renewal；REF-S0 是 reflecting 单 target resolvent。正文第五节已经把它们与详细配置图一一对应。",
            "\\section{附录 E：复杂度、内存、误差与数值协议}",
            "runtime 比较只有在共同比较窗口内通过数值一致性检查后才会进入主表。对每个 workload，都报告 $L^1$、$L^{\\infty}$ 与峰位一致性标志，因此 wall time 从不脱离数值 sanity check 单独汇报。",
            "\\section{附录 F：内嵌历史 full-FPT 口径说明}",
            "仓库里不再保留外部活跃 compare 报告去承载旧的 fixed full-tail fairness 问题。相关历史说明现在以内嵌附录形式保留在这里。",
            "\\begin{table}[H]",
            "\\centering\\small",
            "\\resizebox{\\linewidth}{!}{%",
            "\\input{\\TabDir/unified_appendix_fairness_cn.tex}",
            "}",
            "\\caption{统一报告内部保留的历史公平口径说明。}",
            "\\end{table}",
            "\\end{document}",
        ]
    )
    return "\n".join(lines) + "\n"


def _build_readme(summary: Dict[str, Any]) -> str:
    diag = _agg(summary, "diagnostic")
    curve = _agg(summary, "curve")
    lines = [
        "# Unified Computational Benchmark",
        "",
        "This is the single active computational-method comparison report in the repository.",
        "",
        "## Scope",
        "- Compare only two families: `luca_gf` and `time_recursion`.",
        "- Keep all scientific reports separate; centralize only the computational comparison line here.",
        "- Use practical native-task fairness as the main benchmark rule.",
        "- Embed the historical full-tail note inside Appendix F instead of maintaining a separate active compare report.",
        "",
        "## Snapshot",
        f"- Diagnostic-task median `time/luca` speed ratio: `{_fmt(diag.get('median_speedup_time_over_luca', 0.0), 4)}`",
        f"- Curve-task median `time/luca` speed ratio: `{_fmt(curve.get('median_speedup_time_over_luca', 0.0), 4)}`",
        "",
        "## Outputs",
        "- Data: `artifacts/data/manifest.csv`, `artifacts/data/runtime_raw.csv`, `artifacts/data/runtime_summary.json`",
        "- Runtime figures: `artifacts/figures/unified_runtime_diagnostic.pdf`, `artifacts/figures/unified_runtime_curve.pdf`, `artifacts/figures/unified_speedup_by_workload.pdf`",
        "- Detailed workload configuration figures: `artifacts/figures/<workload_id>_config_detailed.pdf` for all six workloads",
        "- Manuscripts: `manuscript/luca_vs_recursion_unified_benchmark_en.tex`, `manuscript/luca_vs_recursion_unified_benchmark_cn.tex`",
        "",
        "## Reproduce",
        "```bash",
        "python3 scripts/reportctl.py run --report luca_vs_recursion_unified_benchmark -- python3 code/build_manifest.py",
        "python3 scripts/reportctl.py run --report luca_vs_recursion_unified_benchmark -- python3 code/run_unified_benchmark.py",
        "python3 scripts/reportctl.py run --report luca_vs_recursion_unified_benchmark -- python3 code/plot_unified_figures.py",
        "python3 scripts/reportctl.py run --report luca_vs_recursion_unified_benchmark -- python3 code/write_unified_report.py",
        "",
        "python3 scripts/reportctl.py build --report luca_vs_recursion_unified_benchmark --lang en",
        "python3 scripts/reportctl.py build --report luca_vs_recursion_unified_benchmark --lang cn",
        "```",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Write bilingual manuscript and README for unified benchmark report.")
    parser.add_argument(
        "--summary",
        type=str,
        default=str(REPORT_DIR / "data" / "runtime_summary.json"),
    )
    args = parser.parse_args()

    summary = _load_summary(Path(args.summary))
    out_en = REPORT_DIR / "manuscript" / "luca_vs_recursion_unified_benchmark_en.tex"
    out_cn = REPORT_DIR / "manuscript" / "luca_vs_recursion_unified_benchmark_cn.tex"
    out_readme = REPORT_DIR / "README.md"
    out_en.write_text(_build_tex_en(summary), encoding="utf-8")
    out_cn.write_text(_build_tex_cn(summary), encoding="utf-8")
    out_readme.write_text(_build_readme(summary), encoding="utf-8")
    print(json.dumps({"tex_en": str(out_en), "tex_cn": str(out_cn), "readme": str(out_readme)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
