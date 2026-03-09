#!/usr/bin/env python3
from __future__ import annotations

import argparse
import fnmatch
from datetime import date
from pathlib import Path
from typing import Any, Iterable

from report_registry import load_registry

AUTO_START = "<!-- AUTO-INDEX:START -->"
AUTO_END = "<!-- AUTO-INDEX:END -->"
PROGRESS_HEADER = "## 最新进展（手动追加）"
ALLOWED_EXTRA_PDF_PATTERNS = ("note_*.pdf", "method_comparison*.pdf", "fig*_description*.pdf", "*_smoke.pdf")
ALLOWED_EXTRA_TEX_PATTERNS = ("note_*.tex", "method_comparison*.tex", "*_smoke.tex")


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _canonical_pdf_names(item: dict[str, Any]) -> list[str]:
    return [f"{Path(tex).stem}.pdf" for tex in item.get("main_tex", [])]


def _list_extras(report_dir: Path, *, patterns: Iterable[str]) -> list[str]:
    out: set[str] = set()
    for name in [p.name for p in report_dir.glob("*") if p.is_file()]:
        if any(fnmatch.fnmatch(name, pat) for pat in patterns):
            out.add(name)
    return sorted(out)


def _collect_registry_rows(root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in load_registry():
        report_rel = str(item["path"])
        report_dir = root / report_rel
        manuscript_dir = report_dir / item.get("manuscript_dir", "manuscript")
        extras_dir = manuscript_dir / "extras"
        if not report_dir.is_dir():
            rows.append({"report": report_rel, "pdfs": [], "tex": []})
            continue

        canonical_pdfs = [n for n in _canonical_pdf_names(item) if (manuscript_dir / n).exists()]
        extra_pdfs = [n for n in _list_extras(extras_dir, patterns=ALLOWED_EXTRA_PDF_PATTERNS) if n not in canonical_pdfs]
        pdfs = canonical_pdfs + extra_pdfs

        canonical_tex = [str(t) for t in item.get("main_tex", []) if (manuscript_dir / str(t)).exists()]
        extra_tex = [n for n in _list_extras(extras_dir, patterns=ALLOWED_EXTRA_TEX_PATTERNS) if n not in canonical_tex]
        texs = canonical_tex + extra_tex

        rows.append({"report": report_rel, "pdfs": pdfs, "tex": texs})
    return rows


def render_table_rows(items: Iterable[dict[str, Any]]) -> list[str]:
    out: list[str] = []
    for row in items:
        rel = str(row["report"])
        pdfs = list(row["pdfs"])
        texs = list(row["tex"])
        pdf_items: list[str] = []
        for name in pdfs:
            prefix = "manuscript/extras" if any(fnmatch.fnmatch(name, pat) for pat in ALLOWED_EXTRA_PDF_PATTERNS) else "manuscript"
            pdf_items.append(f"`{rel}/{prefix}/{name}`")
        tex_items: list[str] = []
        for name in texs:
            prefix = "manuscript/extras" if any(fnmatch.fnmatch(name, pat) for pat in ALLOWED_EXTRA_TEX_PATTERNS) else "manuscript"
            tex_items.append(f"`{rel}/{prefix}/{name}`")
        pdf_cell = ", ".join(pdf_items) if pdf_items else "-"
        tex_cell = ", ".join(tex_items) if tex_items else "-"
        out.append(f"| `{rel}` | {pdf_cell} | {tex_cell} |")
    return out


def render_auto_index(root: Path) -> str:
    rows = _collect_registry_rows(root)
    lines = [
        AUTO_START,
        "| report | pdfs | tex |",
        "| --- | --- | --- |",
        *render_table_rows(rows),
        AUTO_END,
    ]
    return "\n".join(lines)


def update_last_updated(text: str, today: str) -> str:
    lines = text.splitlines()
    for idx, line in enumerate(lines):
        if line.startswith("最后更新:"):
            lines[idx] = f"最后更新: {today}"
            return "\n".join(lines)
    return text


def replace_or_append_auto_index(text: str, auto_block: str) -> str:
    if AUTO_START in text and AUTO_END in text:
        before, rest = text.split(AUTO_START, 1)
        _, after = rest.split(AUTO_END, 1)
        return before.rstrip() + "\n" + auto_block + "\n" + after.lstrip()
    header = "## 自动索引（由脚本生成）"
    return text.rstrip() + "\n\n" + header + "\n" + auto_block + "\n"


def trim_progress_items(text: str, *, max_items: int) -> tuple[str, list[str]]:
    if max_items <= 0 or PROGRESS_HEADER not in text:
        return text, []

    lines = text.splitlines()
    try:
        start_idx = lines.index(PROGRESS_HEADER)
    except ValueError:
        return text, []

    end_idx = len(lines)
    for i in range(start_idx + 1, len(lines)):
        if lines[i].startswith("## "):
            end_idx = i
            break

    section = lines[start_idx + 1 : end_idx]
    bullet_idx = [i for i, ln in enumerate(section) if ln.startswith("- ")]
    if len(bullet_idx) <= max_items:
        return text, []

    keep_cut = bullet_idx[max_items]
    kept = section[:keep_cut]
    archived = [ln for ln in section[keep_cut:] if ln.startswith("- ")]

    new_lines = lines[: start_idx + 1] + kept + lines[end_idx:]
    if new_lines and new_lines[-1] != "":
        new_lines.append("")
    return "\n".join(new_lines), archived


def append_archive_log(root: Path, archived_items: list[str], today: str) -> None:
    if not archived_items:
        return
    log_path = root / "research" / "docs" / "research_log" / "RESEARCH_PROGRESS_ARCHIVE.md"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    block = [f"## Archived on {today}", *archived_items, ""]
    if log_path.exists():
        old = log_path.read_text(encoding="utf-8")
        log_path.write_text(old.rstrip() + "\n\n" + "\n".join(block), encoding="utf-8")
    else:
        log_path.write_text("# RESEARCH Progress Archive\n\n" + "\n".join(block), encoding="utf-8")


def update_summary(summary_path: Path, today: str, *, max_progress_items: int) -> tuple[str, list[str]]:
    root = repo_root()
    text = summary_path.read_text(encoding="utf-8")
    text = update_last_updated(text, today)
    text, archived_items = trim_progress_items(text, max_items=max_progress_items)
    auto_block = render_auto_index(root)
    text = replace_or_append_auto_index(text, auto_block)
    return text, archived_items


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Refresh research/docs/RESEARCH_SUMMARY.md date and auto index."
    )
    parser.add_argument(
        "--summary",
        default="research/docs/RESEARCH_SUMMARY.md",
        help="Path to summary markdown file.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print updated content instead of writing.",
    )
    parser.add_argument(
        "--max-progress-items",
        type=int,
        default=30,
        help="Keep at most N latest bullet items under 最新进展 section.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = repo_root()
    summary_path = root / args.summary
    today = date.today().isoformat()
    updated, archived = update_summary(summary_path, today, max_progress_items=int(args.max_progress_items))
    if args.dry_run:
        print(updated)
        return 0
    summary_path.write_text(updated, encoding="utf-8")
    append_archive_log(root, archived, today)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
