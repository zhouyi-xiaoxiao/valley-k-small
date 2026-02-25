#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from report_registry import load_registry


REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = REPO_ROOT / "site" / "public" / "data" / "v1"
OUT_DIR = REPO_ROOT / "artifacts" / "deliverables" / "publication"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(1024 * 1024)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip()


def tex_escape(text: str) -> str:
    s = clean_text(text)
    repl = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    for k, v in repl.items():
        s = s.replace(k, v)
    return s


def choose_meta(report_id: str, lang: str) -> dict[str, Any]:
    root = DATA_ROOT / "reports" / report_id
    preferred = root / f"meta.{lang}.json"
    if preferred.exists():
        return read_json(preferred)
    fallback = root / "meta.json"
    if fallback.exists():
        return read_json(fallback)
    raise FileNotFoundError(f"missing meta for report={report_id}")


def choose_report_pdf(report_item: dict[str, Any], lang: str) -> Path | None:
    report_dir = REPO_ROOT / report_item["path"]
    tex_names = list(report_item.get("main_tex", []))

    preferred: list[str] = []
    if lang == "cn":
        preferred.extend([n for n in tex_names if "_cn" in n])
    else:
        preferred.extend([n for n in tex_names if "_en" in n])
        if not preferred and len(tex_names) == 1:
            preferred.append(tex_names[0])

    candidates = preferred + [n for n in tex_names if n not in preferred]
    for tex_name in candidates:
        pdf_name = tex_name.replace(".tex", ".pdf")
        p = report_dir / pdf_name
        if p.exists():
            return p
    for p in sorted(report_dir.glob("*.pdf")):
        if p.name.startswith("."):
            continue
        return p
    return None


def render_header(lang: str, report_count: int, generated_at: str, base_url: str) -> str:
    if lang == "cn":
        title = "Valley-K Small 研究总册"
        subtitle = "网站-出版物-Agent 三位一体交付版"
        abstract = (
            "本总册由同源数据自动生成，覆盖 14 份报告、统一理论框架、关键数学逻辑链、"
            "以及与在线站点一致的机器可读索引。"
        )
        sec_exec = "执行摘要"
        sec_scope = "覆盖范围"
        sec_theory = "统一理论框架"
        sec_reports = "报告综述"
        sec_appendix = "附录：完整报告 PDF"
    else:
        title = "Valley-K Small Compendium"
        subtitle = "Website + Publication + Agent Handoff Edition"
        abstract = (
            "This compendium is generated from a single source of truth and covers 14 reports, "
            "a unified theory map, mathematical logic chains, and machine-readable interfaces that match the web site."
        )
        sec_exec = "Executive Summary"
        sec_scope = "Coverage"
        sec_theory = "Unified Theory Framework"
        sec_reports = "Report Digest"
        sec_appendix = "Appendix: Full Report PDFs"

    lines = [
        r"\documentclass[11pt]{article}",
        r"\usepackage[a4paper,margin=1in]{geometry}",
        r"\usepackage{fontspec}",
        r"\usepackage{hyperref}",
        r"\usepackage{longtable}",
        r"\usepackage{booktabs}",
        r"\usepackage{enumitem}",
        r"\usepackage{pdfpages}",
        r"\usepackage{xcolor}",
    ]
    if lang == "cn":
        lines.extend(
            [
                r"\usepackage{xeCJK}",
                r"\setmainfont{Times New Roman}",
                r"\IfFontExistsTF{Noto Serif CJK SC}{\setCJKmainfont{Noto Serif CJK SC}}{%",
                r"  \IfFontExistsTF{PingFang SC}{\setCJKmainfont{PingFang SC}}{%",
                r"    \IfFontExistsTF{Songti SC}{\setCJKmainfont{Songti SC}}{%",
                r"      \setCJKmainfont{STSong}%",
                r"    }%",
                r"  }%",
                r"}",
            ]
        )
    else:
        lines.append(r"\setmainfont{Times New Roman}")

    lines.extend(
        [
        r"\setlength{\parskip}{6pt}",
        r"\setlength{\parindent}{0pt}",
        r"\begin{document}",
        rf"\title{{{tex_escape(title)}}}",
        rf"\author{{{tex_escape(subtitle)}}}",
        rf"\date{{Generated at {tex_escape(generated_at)}}}",
        r"\maketitle",
        rf"\section*{{{tex_escape(sec_exec)}}}",
        tex_escape(abstract),
        rf"\section*{{{tex_escape(sec_scope)}}}",
        rf"- Reports covered: {report_count}\\",
        rf"- Web URL: \href{{{tex_escape(base_url)}}}{{{tex_escape(base_url)}}}\\",
        rf"- Data root: \texttt{{/data/v1}}",
        rf"\section*{{{tex_escape(sec_theory)}}}",
        ]
    )
    return "\n".join(lines), sec_reports, sec_appendix


def render_theory_cards(theory_map: dict[str, Any], lang: str) -> str:
    cards = theory_map.get("cards", [])
    lines = [r"\begin{longtable}{p{0.26\linewidth} p{0.66\linewidth}}", r"\toprule", r"Concept & Description\\", r"\midrule"]
    for card in cards:
        label = card.get("label_cn") if lang == "cn" else card.get("label_en")
        desc = card.get("description_cn") if lang == "cn" else card.get("description_en")
        lines.append(f"{tex_escape(str(label or ''))} & {tex_escape(str(desc or ''))}\\\\")
    lines.extend([r"\bottomrule", r"\end{longtable}"])
    return "\n".join(lines)


def render_report_digest(registry: list[dict[str, Any]], lang: str) -> tuple[str, list[dict[str, Any]]]:
    lines: list[str] = []
    included: list[dict[str, Any]] = []
    for item in registry:
        rid = item["id"]
        meta = choose_meta(rid, lang=lang)
        title = str(meta.get("title") or rid)
        summary = clean_text(str(meta.get("summary") or ""))
        findings = list(meta.get("key_findings", []))[:8]
        math_story = list(meta.get("math_story", []))[:6]
        pdf_path = choose_report_pdf(item, lang=lang)

        lines.append(rf"\subsection*{{{tex_escape(title)} (\texttt{{{tex_escape(rid)}}})}}")
        lines.append(rf"\textbf{{Summary}}: {tex_escape(summary)}")
        lines.append(r"\textbf{Key Findings}")
        lines.append(r"\begin{itemize}[leftmargin=1.2em]")
        if findings:
            for f in findings:
                lines.append(rf"\item {tex_escape(str(f))}")
        else:
            lines.append(r"\item No findings extracted.")
        lines.append(r"\end{itemize}")

        lines.append(r"\textbf{Mathematical Logic Chain}")
        lines.append(r"\begin{itemize}[leftmargin=1.2em]")
        if math_story:
            for node in math_story:
                stage = str(node.get("stage") or "step")
                explanation = str(node.get("explanation") or "")
                lines.append(rf"\item [{tex_escape(stage)}] {tex_escape(explanation)}")
        else:
            lines.append(r"\item No math logic chain extracted.")
        lines.append(r"\end{itemize}")

        included.append(
            {
                "report_id": rid,
                "title": title,
                "meta_lang": meta.get("lang"),
                "pdf_path": pdf_path.relative_to(REPO_ROOT).as_posix() if pdf_path else None,
                "findings_count": len(findings),
                "math_story_count": len(math_story),
            }
        )
    return "\n".join(lines), included


def render_appendix(pdf_paths: list[Path]) -> str:
    lines: list[str] = []
    for p in pdf_paths:
        rel = os.path.relpath(p, OUT_DIR).replace("\\", "/")
        title = tex_escape(p.name)
        lines.append(rf"\includepdf[pages=-,pagecommand={{\section*{{{title}}}}}]{{{rel}}}")
    return "\n".join(lines)


def build_compendium(*, lang: str, include_appendix: bool, base_url: str) -> dict[str, Any]:
    if not (DATA_ROOT / "index.json").exists():
        raise SystemExit("missing site/public/data/v1/index.json; run `python3 scripts/reportctl.py web-data --mode full` first")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    index = read_json(DATA_ROOT / "index.json")
    theory_map = read_json(DATA_ROOT / "theory_map.json")
    registry = load_registry()

    header_tex, sec_reports, sec_appendix = render_header(
        lang=lang,
        report_count=len(index.get("reports", [])),
        generated_at=utc_now_iso(),
        base_url=base_url,
    )
    theory_tex = render_theory_cards(theory_map, lang=lang)
    digest_tex, digest_rows = render_report_digest(registry, lang=lang)

    appendix_paths: list[Path] = []
    for item in registry:
        p = choose_report_pdf(item, lang=lang)
        if p:
            appendix_paths.append(p)

    tex_path = OUT_DIR / f"valley_k_small_compendium_{lang}.tex"
    pdf_path = OUT_DIR / f"valley_k_small_compendium_{lang}.pdf"

    parts = [
        header_tex,
        theory_tex,
        rf"\section*{{{tex_escape(sec_reports)}}}",
        digest_tex,
    ]
    if include_appendix and appendix_paths:
        parts.append(rf"\section*{{{tex_escape(sec_appendix)}}}")
        parts.append(render_appendix(appendix_paths))
    parts.append(r"\end{document}")
    tex_path.write_text("\n\n".join(parts) + "\n", encoding="utf-8")

    latexmk = shutil.which("latexmk")
    if not latexmk:
        raise SystemExit("latexmk not found; cannot build publication PDF")

    cmd = [
        latexmk,
        "-xelatex",
        "-interaction=nonstopmode",
        "-halt-on-error",
        "-auxdir=build",
        "-emulate-aux-dir",
        tex_path.name,
    ]
    proc = subprocess.run(cmd, cwd=OUT_DIR)
    if proc.returncode != 0:
        raise SystemExit(proc.returncode)
    if not pdf_path.exists():
        raise SystemExit(f"build succeeded but missing output: {pdf_path}")

    payload = {
        "ok": True,
        "lang": lang,
        "generated_at": utc_now_iso(),
        "tex_path": tex_path.relative_to(REPO_ROOT).as_posix(),
        "pdf_path": pdf_path.relative_to(REPO_ROOT).as_posix(),
        "pdf_sha256": sha256_file(pdf_path),
        "report_count": len(digest_rows),
        "appendix_report_count": len(appendix_paths) if include_appendix else 0,
        "base_url": base_url,
        "reports": digest_rows,
    }
    manifest_path = OUT_DIR / f"manifest_{lang}.json"
    manifest_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Build publication-grade Valley-K Small compendium PDF.")
    p.add_argument("--lang", choices=["en", "cn"], default="en")
    p.add_argument("--no-appendix", action="store_true", help="Do not append full report PDFs.")
    p.add_argument("--base-url", default="https://zhouyi-xiaoxiao.github.io/valley-k-small/")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    payload = build_compendium(
        lang=args.lang,
        include_appendix=not bool(args.no_appendix),
        base_url=str(args.base_url),
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
