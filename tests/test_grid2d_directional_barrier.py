from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
VKCORE_SRC = ROOT / "packages" / "vkcore" / "src"
if str(VKCORE_SRC) not in sys.path:
    sys.path.insert(0, str(VKCORE_SRC))

from vkcore.grid2d.rect_bimodality.cli import build_transition_arrays_general_rect, idx


def _row_dict(src_idx: np.ndarray, dst_idx: np.ndarray, probs: np.ndarray, state: int) -> dict[int, float]:
    mask = src_idx == int(state)
    return {int(d): float(p) for d, p in zip(dst_idx[mask], probs[mask])}


def test_legacy_barrier_builder_is_stable_without_directed_input() -> None:
    kwargs = dict(
        Lx=2,
        Wy=1,
        q=1.0,
        local_bias_map={},
        sticky_map={},
        barrier_map={(((0, 0), (1, 0))): 0.25},
        long_range_map={},
        global_bias=(0.0, 0.0),
    )
    src_a, dst_a, prob_a = build_transition_arrays_general_rect(**kwargs)
    src_b, dst_b, prob_b = build_transition_arrays_general_rect(**kwargs, directed_barrier_map=None)
    assert np.array_equal(src_a, src_b)
    assert np.array_equal(dst_a, dst_b)
    assert np.allclose(prob_a, prob_b)


def test_symmetric_directed_override_matches_legacy_undirected_barrier() -> None:
    kwargs = dict(
        Lx=2,
        Wy=1,
        q=1.0,
        local_bias_map={},
        sticky_map={},
        barrier_map={(((0, 0), (1, 0))): 0.25},
        long_range_map={},
        global_bias=(0.0, 0.0),
    )
    src_old, dst_old, prob_old = build_transition_arrays_general_rect(**kwargs)
    src_new, dst_new, prob_new = build_transition_arrays_general_rect(
        **kwargs,
        directed_barrier_map={
            ((0, 0), (1, 0)): 0.25,
            ((1, 0), (0, 0)): 0.25,
        },
    )
    assert np.array_equal(src_old, src_new)
    assert np.array_equal(dst_old, dst_new)
    assert np.allclose(prob_old, prob_new)


def test_directed_barrier_override_changes_each_crossing_direction_independently() -> None:
    src_idx, dst_idx, probs = build_transition_arrays_general_rect(
        Lx=2,
        Wy=1,
        q=1.0,
        local_bias_map={},
        sticky_map={},
        barrier_map={(((0, 0), (1, 0))): 0.25},
        directed_barrier_map={
            ((0, 0), (1, 0)): 0.8,
            ((1, 0), (0, 0)): 0.1,
        },
        long_range_map={},
        global_bias=(0.0, 0.0),
    )

    left = _row_dict(src_idx, dst_idx, probs, idx(0, 0, 2))
    right = _row_dict(src_idx, dst_idx, probs, idx(1, 0, 2))

    assert np.isclose(sum(left.values()), 1.0)
    assert np.isclose(sum(right.values()), 1.0)
    assert np.isclose(left[idx(1, 0, 2)], 0.20)
    assert np.isclose(left[idx(0, 0, 2)], 0.80)
    assert np.isclose(right[idx(0, 0, 2)], 0.025)
    assert np.isclose(right[idx(1, 0, 2)], 0.975)
