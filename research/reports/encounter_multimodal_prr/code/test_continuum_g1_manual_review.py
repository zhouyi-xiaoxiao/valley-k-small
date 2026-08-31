from __future__ import annotations

import json
from pathlib import Path

import continuum_g1_manual_review as review
import numpy as np
import pytest


def test_configuration_is_the_frozen_post_result_diagnostic() -> None:
    manifest = review.load_json(review.MANIFEST)
    configuration = review.configuration_from_manifest(manifest)
    assert configuration.state_count == 207025
    assert configuration.theta_values == (0.7,)
    assert configuration.time_spacing == 0.05
    assert configuration.time_points == 401
    assert manifest["classification_rules"]["original_frozen_line_empty_action_authorized"] is False


def test_common_time_differences_aligns_and_detects_tamper() -> None:
    times = np.arange(0.0, 0.55, 0.05)
    dense = {"time": times}
    for offset, name in enumerate(("f", "f_t", "f_tt", "f_ttt", "survival"), start=1):
        dense[name] = offset + times
    formal_times = [0.0, 0.25, 0.5]
    formal = {"time": formal_times}
    for offset, name in enumerate(("f", "f_t", "f_tt", "f_ttt", "survival"), start=1):
        formal[name] = [offset + value for value in formal_times]
    assert review.common_time_differences(dense, formal) == {
        name: 0.0 for name in ("f", "f_t", "f_tt", "f_ttt", "survival")
    }
    formal["f_t"][1] += 1.0e-4
    assert review.common_time_differences(dense, formal)["f_t"] == pytest.approx(1.0e-4)


def test_formal_result_hash_is_pinned() -> None:
    manifest = json.loads(Path(review.MANIFEST).read_text(encoding="utf-8"))
    assert review.sha256(review.FORMAL_RESULT) == manifest["trigger"]["formal_result_sha256"]
