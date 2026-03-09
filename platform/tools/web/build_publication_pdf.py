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


REPO_ROOT = Path(__file__).resolve().parents[3]
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
    value = re.sub(r"\s+", " ", str(text or "")).strip()
    if not value:
        return ""
    value = value.replace("…", " ")
    value = re.sub(r"\.{3,}", " ", value)
    value = re.sub(r"\bshortcu\b", "shortcut", value, flags=re.IGNORECASE)
    value = re.sub(r"\b1\s*,\s*,\s*N\b", "1..N", value, flags=re.IGNORECASE)
    value = re.sub(r"\b0\s*,\s*,\s*N\s*-\s*1\s*\^\s*2\b", "[0, N-1]^2", value, flags=re.IGNORECASE)
    value = re.sub(r"\b0\s*,\s*,\s*N\s*-\s*1\b", "0..N-1", value, flags=re.IGNORECASE)
    value = re.sub(r"\b([A-Za-z])\s+p(\d+)\b", lambda m: f"{m.group(1)}_p{m.group(2)}", value, flags=re.IGNORECASE)
    value = re.sub(r"\b([xy])\s+t\b", lambda m: f"{m.group(1)}_t", value, flags=re.IGNORECASE)
    value = re.sub(r"\bn\s+0\b", "n0", value, flags=re.IGNORECASE)
    value = re.sub(
        r"\bK\s+(\d(?:\s*,\s*\d)+)\b",
        lambda m: "K=" + "".join(m.group(1).split()),
        value,
        flags=re.IGNORECASE,
    )
    value = re.sub(r"\bP\s*:\s*([0-9]+(?:\.[0-9]+)?)\b", r"P=\1", value, flags=re.IGNORECASE)
    value = re.sub(r"\bwe use,\s*hence\b", "With fixed parameters,", value, flags=re.IGNORECASE)
    value = re.sub(r"\bup to\.\s*$", "", value, flags=re.IGNORECASE)
    value = re.sub(r"\s*,\s*all\s*$", ".", value, flags=re.IGNORECASE)
    value = re.sub(r"\s{2,}", " ", value)
    return value.strip()


def has_publication_claim_lint_issue(text: str) -> bool:
    value = clean_text(text)
    if not value:
        return True
    lowered = value.lower()
    if ",," in value:
        return True
    if lowered.endswith(("under the fig.", "under fig.", "in the fig.", "in fig.", "single co-located")):
        return True
    if re.search(r"\bn=\d+\s*,\s*=\s*\d+\b", lowered):
        return True
    if re.search(r"\bcase\s+[a-z]\s*:\s*n=\d+", lowered) and len(value) < 44:
        return True
    if value.endswith(("(", "[", "with", "and", "->")):
        return True
    return False


def cleaned_claim_text(claim: dict[str, Any], lang: str) -> str:
    key = "text_cn" if lang == "cn" else "text_en"
    text = clean_text(str(claim.get(key, "")))
    if text and not has_publication_claim_lint_issue(text):
        return text
    evidence = claim.get("evidence", [])
    if isinstance(evidence, list):
        for row in evidence:
            if not isinstance(row, dict):
                continue
            snippet_key = "snippet_cn" if lang == "cn" else "snippet_en"
            snippet = clean_text(str(row.get(snippet_key, "")))
            if snippet and not has_publication_claim_lint_issue(snippet):
                return snippet
    return text or clean_text(str(claim.get("claim_id", "")))


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


def normalize_formula_for_publication(latex: str, *, max_chars: int | None = None) -> str:
    value = clean_text(str(latex or ""))
    if not value:
        return ""
    value = value.replace(r"\textbackslash{}", "\\")
    value = value.replace(r"\textbackslash\{\}", "\\")
    # Keep escaped braces so delimiters like \left\{...\right\} remain valid LaTeX.
    value = value.replace(r"\_", "_")
    value = value.replace(r"\%", "%")
    value = value.replace(r"\$", "$")
    value = value.strip()
    if value.startswith(r"\[") and value.endswith(r"\]"):
        value = value[2:-2].strip()
    value = value.replace("…", " ")
    value = re.sub(r"\.{3,}\s*$", "", value)
    value = re.sub(r"\s+", " ", value).strip()
    if max_chars is None or len(value) <= max_chars:
        return value
    clipped = value[: max_chars + 1]
    stop = max(clipped.rfind(" + "), clipped.rfind(" - "), clipped.rfind(" = "), clipped.rfind(", "))
    if stop < int(max_chars * 0.55):
        stop = max_chars
    return clipped[:stop].strip()


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


def render_header(lang: str, report_count: int, generated_at: str, base_url: str) -> tuple[str, str, str, str]:
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
        sec_book = "书籍主线章节"
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
        sec_book = "Book Mainline Chapters"
        sec_reports = "Report Digest"
        sec_appendix = "Appendix: Full Report PDFs"

    lines = [
        r"\documentclass[11pt]{article}",
        r"\usepackage[a4paper,margin=1in]{geometry}",
        r"\usepackage{fontspec}",
        r"\usepackage{amsmath,amssymb}",
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
    return "\n".join(lines), sec_book, sec_reports, sec_appendix


def render_theory_cards(theory_map: dict[str, Any], lang: str) -> str:
    cards = theory_map.get("cards", [])
    lines = [r"\begin{longtable}{p{0.26\linewidth} p{0.66\linewidth}}", r"\toprule", r"Concept & Description\\", r"\midrule"]
    for card in cards:
        label = card.get("label_cn") if lang == "cn" else card.get("label_en")
        desc = card.get("description_cn") if lang == "cn" else card.get("description_en")
        lines.append(f"{tex_escape(str(label or ''))} & {tex_escape(str(desc or ''))}\\\\")
    lines.extend([r"\bottomrule", r"\end{longtable}"])
    return "\n".join(lines)


def render_book_mainline(lang: str) -> tuple[str, list[dict[str, Any]]]:
    manifest_path = DATA_ROOT / "book" / "book_manifest.json"
    chapter_root = DATA_ROOT / "book" / "chapters"
    if not manifest_path.exists() or not chapter_root.exists():
        return "", []

    manifest = read_json(manifest_path)
    rows = sorted(manifest.get("chapters", []), key=lambda row: int(row.get("order", 0)))
    lines: list[str] = []
    summary_rows: list[dict[str, Any]] = []

    for row in rows:
        chapter_id = str(row.get("chapter_id", "")).strip()
        if not chapter_id:
            continue
        chapter_path = chapter_root / f"{chapter_id}.json"
        if not chapter_path.exists():
            continue
        chapter = read_json(chapter_path)

        title = chapter.get("title_cn") if lang == "cn" else chapter.get("title_en")
        summary = chapter.get("summary_cn") if lang == "cn" else chapter.get("summary_en")
        intros = chapter.get("intro_cn") if lang == "cn" else chapter.get("intro_en")
        concept_cards = chapter.get("concept_cards", [])
        theory_chain = chapter.get("theory_chain", [])
        claim_ledger_raw = list(chapter.get("claim_ledger", []))
        claim_ledger = [
            row
            for row in claim_ledger_raw
            if str(row.get("claim_type", "scientific")).strip().lower() == "scientific"
        ] or claim_ledger_raw
        linked_reports = chapter.get("linked_reports", [])

        lines.append(rf"\subsection*{{{tex_escape(str(title))} (\texttt{{{tex_escape(chapter_id)}}})}}")
        lines.append(rf"\textbf{{Summary}}: {tex_escape(str(summary))}")

        lines.append(r"\textbf{Chapter Guide}")
        lines.append(r"\begin{itemize}[leftmargin=1.2em]")
        for paragraph in list(intros or [])[:3]:
            lines.append(rf"\item {tex_escape(str(paragraph))}")
        lines.append(r"\end{itemize}")

        lines.append(r"\textbf{Concept Cards}")
        lines.append(r"\begin{itemize}[leftmargin=1.2em]")
        for card in concept_cards[:4]:
            label = card.get("label_cn") if lang == "cn" else card.get("label_en")
            desc = card.get("description_cn") if lang == "cn" else card.get("description_en")
            lines.append(rf"\item {tex_escape(str(label))}: {tex_escape(clean_text(str(desc)))}")
        lines.append(r"\end{itemize}")

        lines.append(r"\textbf{Theory Chain}")
        lines.append(r"\begin{itemize}[leftmargin=1.2em]")
        for item in theory_chain[:5]:
            desc = item.get("description_cn") if lang == "cn" else item.get("description_en")
            stage = tex_escape(str(item.get("stage", "step")))
            lines.append(rf"\item [{stage}] {tex_escape(clean_text(str(desc)))}")
            formula = normalize_formula_for_publication(str(item.get("latex") or ""))
            if formula:
                lines.append(rf"\[ {formula} \]")
        lines.append(r"\end{itemize}")

        lines.append(r"\textbf{Claim Ledger}")
        lines.append(r"\begin{itemize}[leftmargin=1.2em]")
        for claim in claim_ledger:
            text = cleaned_claim_text(claim, lang)
            lines.append(
                rf"\item [{tex_escape(str(claim.get('stage', 'finding')))}] "
                rf"{tex_escape(text)} "
                rf"(evidence={len(claim.get('evidence', []))})"
            )
        lines.append(r"\end{itemize}")

        lines.append(r"\textbf{Linked Reports}")
        lines.append(r"\begin{itemize}[leftmargin=1.2em]")
        for report in linked_reports[:6]:
            rtitle = report.get("title_cn") if lang == "cn" else report.get("title_en")
            lines.append(rf"\item {tex_escape(str(rtitle))} (\texttt{{{tex_escape(str(report.get('report_id', '')))}}})")
        lines.append(r"\end{itemize}")

        summary_rows.append(
            {
                "chapter_id": chapter_id,
                "title": title,
                "claim_count": len(claim_ledger),
                "interactive_count": len(chapter.get("interactive_panels", [])),
                "report_count": len(linked_reports),
            }
        )

    return "\n".join(lines), summary_rows


def render_report_digest(
    registry: list[dict[str, Any]],
    lang: str,
    *,
    content_map: dict[str, Any] | None = None,
) -> tuple[str, list[dict[str, Any]]]:
    lines: list[str] = []
    included: list[dict[str, Any]] = []
    guide_by_report: dict[str, dict[str, Any]] = {}
    if isinstance(content_map, dict):
        for row in content_map.get("report_guides", []):
            rid = str(row.get("report_id", "")).strip()
            if rid:
                guide_by_report[rid] = row
    for item in registry:
        rid = item["id"]
        meta = choose_meta(rid, lang=lang)
        title = str(meta.get("title") or rid)
        summary = clean_text(str(meta.get("summary") or ""))
        findings = list(meta.get("key_findings", []))[:8]
        math_story = list(meta.get("math_story", []))[:6]
        repro_commands = [str(cmd).strip() for cmd in meta.get("reproducibility_commands", []) if str(cmd).strip()][:4]
        pdf_path = choose_report_pdf(item, lang=lang)

        lines.append(rf"\subsection*{{{tex_escape(title)} (\texttt{{{tex_escape(rid)}}})}}")
        lines.append(rf"\textbf{{Summary}}: {tex_escape(summary)}")
        guide = guide_by_report.get(rid, {})
        objective = clean_text(
            str(
                guide.get("objective_cn")
                if lang == "cn"
                else guide.get("objective_en")
            )
        )
        if objective:
            lines.append(rf"\textbf{{Continuity Objective}}: {tex_escape(objective)}")
        upstream = [str(x) for x in guide.get("upstream_report_ids", []) if str(x).strip()]
        downstream = [str(x) for x in guide.get("downstream_report_ids", []) if str(x).strip()]
        related = [str(x) for x in guide.get("related_report_ids", []) if str(x).strip()]
        continuity_tokens = []
        if upstream:
            continuity_tokens.append(f"upstream={','.join(upstream[:2])}")
        if downstream:
            continuity_tokens.append(f"downstream={','.join(downstream[:2])}")
        if related:
            continuity_tokens.append(f"bridges={','.join(related[:3])}")
        if continuity_tokens:
            lines.append(rf"\textbf{{Cross-Report Links}}: {tex_escape('; '.join(continuity_tokens))}")
        lines.append(r"\textbf{Key Findings}")
        lines.append(r"\begin{itemize}[leftmargin=1.2em]")
        if findings:
            for f in findings:
                lines.append(rf"\item {tex_escape(str(f))}")
        else:
            lines.append(r"\item No findings extracted.")
        lines.append(r"\end{itemize}")

        lines.append(r"\textbf{Reproducibility Commands}")
        lines.append(r"\begin{itemize}[leftmargin=1.2em]")
        if repro_commands:
            for cmd in repro_commands:
                lines.append(rf"\item \texttt{{{tex_escape(cmd)}}}")
        else:
            lines.append(r"\item No executable command was declared for this report snapshot.")
        lines.append(r"\end{itemize}")

        lines.append(r"\textbf{Mathematical Logic Chain}")
        lines.append(r"\begin{itemize}[leftmargin=1.2em]")
        if math_story:
            for node in math_story:
                stage = str(node.get("stage") or "step")
                explanation = str(node.get("description") or node.get("explanation") or "")
                lines.append(rf"\item [{tex_escape(stage)}] {tex_escape(explanation)}")
                formula = normalize_formula_for_publication(str(node.get("latex") or ""))
                if formula:
                    lines.append(rf"\[ {formula} \]")
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
    content_map = read_json(DATA_ROOT / "content_map.json") if (DATA_ROOT / "content_map.json").exists() else {}
    registry = load_registry()

    header_tex, sec_book, sec_reports, sec_appendix = render_header(
        lang=lang,
        report_count=len(index.get("reports", [])),
        generated_at=utc_now_iso(),
        base_url=base_url,
    )
    theory_tex = render_theory_cards(theory_map, lang=lang)
    book_tex, book_rows = render_book_mainline(lang=lang)
    digest_tex, digest_rows = render_report_digest(registry, lang=lang, content_map=content_map)

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
    ]
    if book_tex:
        parts.extend(
            [
                rf"\section*{{{tex_escape(sec_book)}}}",
                book_tex,
            ]
        )
    parts.extend(
        [
        rf"\section*{{{tex_escape(sec_reports)}}}",
        digest_tex,
        ]
    )
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
        "book_chapter_count": len(book_rows),
        "appendix_report_count": len(appendix_paths) if include_appendix else 0,
        "base_url": base_url,
        "book_chapters": book_rows,
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
