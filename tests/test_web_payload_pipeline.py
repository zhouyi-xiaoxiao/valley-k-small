from __future__ import annotations

import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_web_payload_pipeline_smoke(tmp_path: Path) -> None:
    data_root = tmp_path / "data" / "v1"
    artifacts_root = tmp_path / "artifacts"
    checks_dir = tmp_path / "checks"

    cmd_web_data = [
        "python3",
        "platform/tools/web/build_web_data.py",
        "--mode",
        "full",
        "--reports",
        "ring_valley",
        "ring_valley_dst",
        "--output-dir",
        str(data_root),
        "--artifacts-dir",
        str(artifacts_root),
        "--max-assets",
        "10",
        "--max-figures",
        "8",
        "--max-datasets",
        "2",
        "--max-points",
        "80",
        "--no-copy-assets",
    ]
    proc_web_data = subprocess.run(
        cmd_web_data,
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    assert proc_web_data.returncode == 0, proc_web_data.stdout

    cmd_agent = [
        "python3",
        "platform/tools/web/build_agent_sync.py",
        "--data-root",
        str(data_root),
        "--checks-dir",
        str(checks_dir),
    ]
    cmd_book_glossary = [
        "python3",
        "platform/tools/web/build_glossary.py",
        "--data-root",
        str(data_root),
    ]
    proc_book_glossary = subprocess.run(
        cmd_book_glossary,
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    assert proc_book_glossary.returncode == 0, proc_book_glossary.stdout

    cmd_book_content = [
        "python3",
        "platform/tools/web/build_book_content.py",
        "--data-root",
        str(data_root),
    ]
    proc_book_content = subprocess.run(
        cmd_book_content,
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    assert proc_book_content.returncode == 0, proc_book_content.stdout

    cmd_translation_qc = [
        "python3",
        "platform/tools/web/validate_bilingual_quality.py",
        "--data-root",
        str(data_root),
    ]
    proc_translation_qc = subprocess.run(
        cmd_translation_qc,
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    assert proc_translation_qc.returncode == 0, proc_translation_qc.stdout

    proc_agent = subprocess.run(
        cmd_agent,
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    assert proc_agent.returncode == 0, proc_agent.stdout

    cmd_validate = [
        "python3",
        "platform/tools/web/validate_web_data.py",
        "--data-root",
        str(data_root),
    ]
    proc_validate = subprocess.run(
        cmd_validate,
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    assert proc_validate.returncode == 0, proc_validate.stdout

    assert (data_root / "index.json").exists()
    assert (data_root / "agent" / "manifest.json").exists()
    assert (data_root / "book" / "book_manifest.json").exists()
    assert (data_root / "agent" / "translation_qc.json").exists()
    assert (checks_dir / "crosscheck_report.json").exists()
