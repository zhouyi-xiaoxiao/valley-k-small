from __future__ import annotations

import sys
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = ROOT / "packages" / "vkcore" / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from vkcore.ring.encounter import (  # noqa: E402
    encounter_gf_anywhere,
    encounter_gf_fixed_site,
    encounter_time_anywhere,
    encounter_time_fixed_site,
)


def test_encounter_gf_anywhere_matches_time_small_n() -> None:
    cfg = dict(
        N=11,
        q1=0.7,
        g1=0.3,
        q2=0.65,
        g2=-0.2,
        n0=1,
        m0=6,
        shortcut_src=1,
        shortcut_dst=7,
        beta=0.18,
        t_max=30,
    )
    gf = encounter_gf_anywhere(**cfg, oversample=8, r_pow10=8.0)
    td = encounter_time_anywhere(**cfg)
    diff = np.abs(np.asarray(gf["f"]) - np.asarray(td["f"]))
    assert float(diff.max()) < 1e-12


def test_encounter_gf_fixed_site_matches_time_small_n() -> None:
    cfg = dict(
        N=11,
        q1=0.7,
        g1=0.3,
        q2=0.65,
        g2=-0.2,
        n0=1,
        m0=6,
        delta=0,
        shortcut_src=1,
        shortcut_dst=7,
        beta=0.18,
        t_max=30,
    )
    gf = encounter_gf_fixed_site(**cfg, oversample=8, r_pow10=8.0)
    td = encounter_time_fixed_site(**cfg)
    diff = np.abs(np.asarray(gf["f"]) - np.asarray(td["f"]))
    assert float(diff.max()) < 1e-9
