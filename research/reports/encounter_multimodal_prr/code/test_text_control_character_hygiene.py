"""Reject hidden C0/DEL bytes from the report's human-readable sources."""

from pathlib import Path

REPORT_ROOT = Path(__file__).resolve().parents[1]
TEXT_SUFFIXES = {
    ".bib",
    ".c",
    ".cfg",
    ".cpp",
    ".h",
    ".json",
    ".lean",
    ".md",
    ".py",
    ".sh",
    ".tex",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}
ALLOWED_C0 = {0x09, 0x0A, 0x0D}


def _forbidden_offsets(payload: bytes) -> list[tuple[int, int]]:
    return [
        (offset, value)
        for offset, value in enumerate(payload)
        if (value < 0x20 and value not in ALLOWED_C0) or value == 0x7F
    ]


def test_report_text_sources_have_no_hidden_control_bytes() -> None:
    failures: list[str] = []
    for path in sorted(REPORT_ROOT.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        bad = _forbidden_offsets(path.read_bytes())
        if bad:
            preview = ", ".join(f"offset={offset}:0x{value:02x}" for offset, value in bad[:8])
            failures.append(f"{path.relative_to(REPORT_ROOT)}: {preview}")

    assert not failures, "forbidden control bytes:\n" + "\n".join(failures)
