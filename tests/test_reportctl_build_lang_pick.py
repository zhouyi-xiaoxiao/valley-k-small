from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import reportctl


def test_pick_main_tex_matches_lang_suffix_exactly() -> None:
    report = {
        "id": "ring_two_walker_encounter_shortcut",
        "main_tex": [
            "ring_two_walker_encounter_shortcut_cn.tex",
            "ring_two_walker_encounter_shortcut_en.tex",
        ],
    }
    assert reportctl._pick_main_tex(report, "cn") == "ring_two_walker_encounter_shortcut_cn.tex"
    assert reportctl._pick_main_tex(report, "en") == "ring_two_walker_encounter_shortcut_en.tex"


def test_expand_build_lang_supports_dual_aliases() -> None:
    assert reportctl._expand_build_lang("en") == ["en"]
    assert reportctl._expand_build_lang("cn") == ["cn"]
    assert reportctl._expand_build_lang("en/cn") == ["en", "cn"]
    assert reportctl._expand_build_lang("cn/en") == ["cn", "en"]
