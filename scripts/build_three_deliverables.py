#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable or "python3"
SITE_DIR = REPO_ROOT / "site"
OUT_DIR = REPO_ROOT / "artifacts" / "deliverables"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def run_step(name: str, cmd: list[str], *, cwd: Path | None = None, env: dict[str, str] | None = None) -> dict[str, Any]:
    proc = subprocess.run(cmd, cwd=cwd or REPO_ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, check=False)
    return {
        "agent": name,
        "command": cmd,
        "return_code": int(proc.returncode),
        "status": "pass" if proc.returncode == 0 else "fail",
        "output_tail": (proc.stdout or "")[-20000:],
        "finished_at": utc_now_iso(),
    }


def build_all(*, mode: str, skip_site_build: bool, skip_openclaw: bool, content_rounds: int) -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    steps: list[dict[str, Any]] = []

    steps.append(run_step("Agent-A-WebData", [PYTHON, "scripts/build_web_data.py", "--mode", mode]))
    steps.append(run_step("Agent-B-BookData-Glossary", [PYTHON, "scripts/build_glossary.py"]))
    steps.append(run_step("Agent-C-BookData-Chapters", [PYTHON, "scripts/build_book_content.py"]))
    steps.append(run_step("Agent-D-TranslationQC", [PYTHON, "scripts/validate_bilingual_quality.py"]))
    steps.append(run_step("Agent-E-AgentSync", [PYTHON, "scripts/build_agent_sync.py"]))
    steps.append(run_step("Agent-F-Validate", [PYTHON, "scripts/validate_web_data.py"]))

    if not skip_site_build:
        steps.append(
            run_step(
                "Agent-G-FrontendBuild",
                ["npm", "run", "build"],
                cwd=SITE_DIR,
                env={
                    **os.environ,
                    "NEXT_PUBLIC_BASE_PATH": "/valley-k-small",
                    "NODE_OPTIONS": "--max-old-space-size=1536",
                },
            )
        )
    else:
        steps.append(
            {
                "agent": "Agent-G-FrontendBuild",
                "command": ["skip:site-build"],
                "return_code": 0,
                "status": "pass",
                "output_tail": "Skipped by --skip-site-build",
                "finished_at": utc_now_iso(),
            }
        )

    steps.append(run_step("Agent-H-PublicationEN", [PYTHON, "scripts/build_publication_pdf.py", "--lang", "en"]))
    steps.append(run_step("Agent-I-PublicationCN", [PYTHON, "scripts/build_publication_pdf.py", "--lang", "cn"]))
    steps.append(run_step("Agent-J-AgentPack", [PYTHON, "scripts/build_agent_pack.py"]))

    content_cmd = [
        PYTHON,
        "scripts/run_content_iteration.py",
        "--rounds",
        str(max(1, int(content_rounds))),
        "--mode",
        mode,
    ]
    if skip_openclaw:
        content_cmd.append("--skip-openclaw")
    steps.append(run_step("Agent-K-ContentIteration", content_cmd))

    ok = all(s["status"] == "pass" for s in steps)
    payload = {
        "ok": ok,
        "generated_at": utc_now_iso(),
        "mode": mode,
        "skip_site_build": skip_site_build,
        "skip_openclaw": skip_openclaw,
        "content_rounds": int(content_rounds),
        "steps": steps,
        "deliverables": {
            "website": "https://zhouyi-xiaoxiao.github.io/valley-k-small/",
            "publication_en": "artifacts/deliverables/publication/valley_k_small_compendium_en.pdf",
            "publication_cn": "artifacts/deliverables/publication/valley_k_small_compendium_cn.pdf",
            "agent_pack": "artifacts/deliverables/agent_pack/v1",
            "content_iteration": "artifacts/checks/content_iteration/summary.json",
        },
    }
    out_path = OUT_DIR / "delivery_manifest.json"
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Build 3 deliverables: website, publication PDF, and agent pack.")
    p.add_argument("--mode", choices=["full", "changed"], default="changed")
    p.add_argument("--skip-site-build", action="store_true")
    p.add_argument("--skip-openclaw", action="store_true")
    p.add_argument("--content-rounds", type=int, default=2)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    payload = build_all(
        mode=str(args.mode),
        skip_site_build=bool(args.skip_site_build),
        skip_openclaw=bool(args.skip_openclaw),
        content_rounds=max(1, int(args.content_rounds)),
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
