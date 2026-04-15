from __future__ import annotations

from typing import Any, Literal

import numpy as np

from vkcore.grid2d.rect_bimodality.cli import (
    build_ot_case_geometry,
    build_transition_arrays_general_rect,
    classify_phase_one_target,
    run_exact_one_target_rect,
    summarize_one_target,
)


GateMode = Literal["line", "halfspace"]

LGR_STATE_LABELS = [
    "L0G0R0",
    "L0G0R1",
    "L0G1R0",
    "L0G1R1",
    "L1G0R0",
    "L1G0R1",
    "L1G1R0",
    "L1G1R1",
]
LR_STATE_LABELS = ["L0R0", "L0R1", "L1R0", "L1R1"]
GATE_ANCHOR_FAMILY_LABELS = ["N0", "N1", "P0", "P1", "Q0", "Q1"]
THREE_FAMILY_LABELS = ["N", "P", "Q"]
SIDE_GATE_ANCHOR_LABELS = ["N", "TP", "BP", "TQ", "BQ"]
SIDE_LGR_STATE_LABELS = [
    "D0G0R0",
    "D0G0R1",
    "D0G1R0",
    "D0G1R1",
    "T1G0R0",
    "T1G0R1",
    "T1G1R0",
    "T1G1R1",
    "B1G0R0",
    "B1G0R1",
    "B1G1R0",
    "B1G1R1",
]
SIDE_R_LABELS = ["D0", "D1", "T0", "T1", "B0", "B1"]


def idx(x: int, y: int, lx: int) -> int:
    return int(y) * int(lx) + int(x)


def _edge_idx_key(a: int, b: int) -> tuple[int, int]:
    return (int(a), int(b)) if int(a) <= int(b) else (int(b), int(a))


def _validate_gate_mode(gate_mode: str) -> GateMode:
    if gate_mode not in ("line", "halfspace"):
        raise ValueError(f"unsupported gate_mode={gate_mode!r}")
    return gate_mode  # type: ignore[return-value]


def _lgr_flag(leak: int, gate_seen: int, rollback: int) -> int:
    return int(leak) + 2 * int(gate_seen) + 4 * int(rollback)


def _side_lgr_flag(leak_state: int, gate_seen: int, rollback: int) -> int:
    return int(leak_state) + 3 * int(gate_seen) + 6 * int(rollback)


def _gate_anchor_state_flag(leak_stage: int, gate_seen: int, rollback: int) -> int:
    return int(leak_stage) + 3 * int(gate_seen) + 6 * int(rollback)


def _gate_anchor_family_flag(leak_stage: int, rollback: int) -> int:
    leak_arr = np.asarray(leak_stage, dtype=np.int64)
    return 2 * leak_arr + int(rollback)


def _gate_anchor_side_flag(side_stage: int, gate_seen: int) -> int:
    return int(side_stage) + 5 * int(gate_seen)


def _rollback_state_flag(leak: int, left_a: int, rollback: int) -> int:
    return int(leak) + 2 * int(left_a) + 4 * int(rollback)


def _rollback_side_state_flag(leak_state: int, left_a: int, rollback: int) -> int:
    return int(leak_state) + 3 * int(left_a) + 6 * int(rollback)


def window_ranges(tp1: int | None, tv: int | None, tp2: int | None, n: int) -> list[tuple[str, int, int]]:
    if tp1 is None or tv is None or tp2 is None:
        return [("early", 10, 60), ("middle", 120, 200), ("late", 260, 360)]
    gap = max(20, int(tp2) - int(tp1))
    half = int(max(8, min(26, gap // 7)))
    return [
        ("peak1", max(1, int(tp1) - half), min(n - 1, int(tp1) + half)),
        ("valley", max(1, int(tv) - half), min(n - 1, int(tv) + half)),
        ("peak2", max(1, int(tp2) - half), min(n - 1, int(tp2) + half)),
    ]


def solve_committor(
    *,
    n_states: int,
    src_idx: np.ndarray,
    dst_idx: np.ndarray,
    probs: np.ndarray,
    set_A: np.ndarray,
    set_B: np.ndarray,
    max_iter: int = 20_000,
    tol: float = 1.0e-11,
) -> np.ndarray:
    q = np.zeros(int(n_states), dtype=np.float64)
    q[set_B] = 1.0
    for _ in range(int(max_iter)):
        acc = np.bincount(src_idx, weights=probs * q[dst_idx], minlength=int(n_states))
        acc[set_A] = 0.0
        acc[set_B] = 1.0
        diff = float(np.max(np.abs(acc - q)))
        q = acc
        if diff < float(tol):
            break
    return q


def build_start_basin_mask(*, Lx: int, Wy: int, start_x: int, y_mid: int) -> np.ndarray:
    n_states = int(Lx) * int(Wy)
    basin = np.zeros(n_states, dtype=bool)
    for y in range(int(Wy)):
        for x in range(int(Lx)):
            if x <= int(start_x) + 1 and abs(y - int(y_mid)) <= 1:
                basin[idx(x, y, Lx)] = True
    return basin


def build_x_gate_mask(*, Lx: int, Wy: int, X_g: int, gate_mode: GateMode) -> np.ndarray:
    _validate_gate_mode(gate_mode)
    gate_mask = np.zeros(int(Lx) * int(Wy), dtype=bool)
    x_gate = int(X_g)
    for y in range(int(Wy)):
        for x in range(int(Lx)):
            if gate_mode == "line":
                gate_mask[idx(x, y, Lx)] = x == x_gate
            else:
                gate_mask[idx(x, y, Lx)] = x >= x_gate
    return gate_mask


def build_committor_gate_mask(*, q_values: np.ndarray, q_star: float) -> np.ndarray:
    return np.asarray(q_values, dtype=np.float64) >= float(q_star)


def compute_one_target_forward_history(
    case: dict[str, Any],
    *,
    Lx: int,
    max_t: int,
) -> tuple[list[np.ndarray], np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Forward transient state distributions up to `max_t` for one-target cases."""
    n_states = int(Lx) * int(case["Wy"])
    start = case["start"]
    target = case["target"]
    start_idx = idx(start[0], start[1], Lx)
    target_idx = idx(target[0], target[1], Lx)

    src_idx = np.asarray(case["src_idx"], dtype=np.int64)
    dst_idx = np.asarray(case["dst_idx"], dtype=np.int64)
    probs = np.asarray(case["probs"], dtype=np.float64)

    hit_mask = dst_idx == int(target_idx)
    src_nonhit = src_idx[~hit_mask]
    dst_nonhit = dst_idx[~hit_mask]
    prob_nonhit = probs[~hit_mask]
    hit_prob = np.bincount(src_idx[hit_mask], weights=probs[hit_mask], minlength=n_states).astype(np.float64)

    p = np.zeros(n_states, dtype=np.float64)
    p[int(start_idx)] = 1.0
    history: list[np.ndarray] = [p.copy()]
    for _ in range(int(max_t)):
        p_next = np.zeros_like(p)
        np.add.at(p_next, dst_nonhit, p[src_nonhit] * prob_nonhit)
        history.append(p_next.copy())
        p = p_next
    return history, src_nonhit, dst_nonhit, prob_nonhit, hit_prob


def compute_one_target_window_path_statistics(
    case: dict[str, Any],
    *,
    Lx: int,
    windows: list[tuple[str, int, int]],
) -> dict[str, dict[str, Any]]:
    """Exact window-conditioned occupancy and directional membrane flux."""
    if not windows:
        return {}
    max_hi = max(int(hi) for _, _, hi in windows)
    history, src_nonhit, dst_nonhit, prob_nonhit, hit_prob = compute_one_target_forward_history(
        case,
        Lx=Lx,
        max_t=max_hi,
    )
    n_states = int(Lx) * int(case["Wy"])

    c2o_pairs = {
        (idx(a[0], a[1], Lx), idx(b[0], b[1], Lx))
        for a, b in case.get("membrane_c2o_edges", set())
    }
    o2c_pairs = {
        (idx(a[0], a[1], Lx), idx(b[0], b[1], Lx))
        for a, b in case.get("membrane_o2c_edges", set())
    }
    edge_pairs = list(zip(src_nonhit.tolist(), dst_nonhit.tolist()))
    c2o_mask = np.asarray([pair in c2o_pairs for pair in edge_pairs], dtype=bool)
    o2c_mask = np.asarray([pair in o2c_pairs for pair in edge_pairs], dtype=bool)

    out: dict[str, dict[str, Any]] = {}
    start_idx = idx(case["start"][0], case["start"][1], Lx)
    for name, lo, hi in windows:
        lo_i = max(1, int(lo))
        hi_i = min(int(max_hi), int(hi))
        if hi_i < lo_i:
            continue
        b_next = np.zeros(n_states, dtype=np.float64)
        occ = np.zeros(n_states, dtype=np.float64)
        flux_c2o = 0.0
        flux_o2c = 0.0
        for t in range(hi_i - 1, -1, -1):
            b_t = np.zeros(n_states, dtype=np.float64)
            np.add.at(b_t, src_nonhit, prob_nonhit * b_next[dst_nonhit])
            if lo_i <= (t + 1) <= hi_i:
                b_t += hit_prob
            occ += history[t] * b_t
            if c2o_mask.any():
                flux_c2o += float(np.sum(history[t][src_nonhit[c2o_mask]] * prob_nonhit[c2o_mask] * b_next[dst_nonhit[c2o_mask]]))
            if o2c_mask.any():
                flux_o2c += float(np.sum(history[t][src_nonhit[o2c_mask]] * prob_nonhit[o2c_mask] * b_next[dst_nonhit[o2c_mask]]))
            b_next = b_t

        hit_mass = float(np.sum(case["f_total"][lo_i : hi_i + 1]))
        occ_sum = float(np.sum(occ))
        occ_norm = occ / occ_sum if occ_sum > 0.0 else occ
        out[name] = {
            "occupancy": occ_norm.reshape(int(case["Wy"]), Lx),
            "occupancy_mass": occ_sum,
            "hit_mass": hit_mass,
            "flux_c2o": float(flux_c2o),
            "flux_o2c": float(flux_o2c),
            "consistency_gap": float(abs(float(b_next[int(start_idx)]) - hit_mass)),
        }
    return out


def compute_one_target_first_event_statistics(
    case: dict[str, Any],
    *,
    Lx: int,
    windows: list[tuple[str, int, int]],
    event_state_mask: np.ndarray | None = None,
    event_edge_pairs: set[tuple[int, int]] | None = None,
) -> dict[str, dict[str, Any]]:
    """Exact first-event timing conditioned on hitting inside each window.

    Exactly one of `event_state_mask` or `event_edge_pairs` must be provided.
    - `event_state_mask`: first time the chain enters the marked states.
    - `event_edge_pairs`: first time the chain traverses one of the directed edges.
    """
    if bool(event_state_mask is None) == bool(event_edge_pairs is None):
        raise ValueError("provide exactly one of event_state_mask or event_edge_pairs")
    if not windows:
        return {}

    max_hi = max(int(hi) for _, _, hi in windows)
    history, src_nonhit, dst_nonhit, prob_nonhit, hit_prob = compute_one_target_forward_history(
        case,
        Lx=Lx,
        max_t=max_hi,
    )
    n_states = int(Lx) * int(case["Wy"])
    start_idx = idx(case["start"][0], case["start"][1], Lx)

    event_state_flat: np.ndarray | None = None
    if event_state_mask is not None:
        event_state_flat = np.asarray(event_state_mask, dtype=bool).reshape(n_states)

    event_edge_mask: np.ndarray | None = None
    if event_edge_pairs is not None:
        edge_pairs = list(zip(src_nonhit.tolist(), dst_nonhit.tolist()))
        event_edge_mask = np.asarray([pair in event_edge_pairs for pair in edge_pairs], dtype=bool)

    p_no_event = np.zeros(n_states, dtype=np.float64)
    first_event_at_zero = 0.0
    if event_state_flat is not None and bool(event_state_flat[int(start_idx)]):
        first_event_at_zero = 1.0
    else:
        p_no_event[int(start_idx)] = 1.0

    history_no_event: list[np.ndarray] = [p_no_event.copy()]
    if event_state_flat is not None:
        stay_mask = ~event_state_flat[dst_nonhit]
    else:
        stay_mask = ~np.asarray(event_edge_mask, dtype=bool)
    for _ in range(int(max_hi)):
        p_next = np.zeros_like(p_no_event)
        if np.any(stay_mask):
            np.add.at(p_next, dst_nonhit[stay_mask], p_no_event[src_nonhit[stay_mask]] * prob_nonhit[stay_mask])
        history_no_event.append(p_next.copy())
        p_no_event = p_next

    out: dict[str, dict[str, Any]] = {}
    t_idx = np.arange(max_hi + 1, dtype=np.float64)
    for window_name, lo, hi in windows:
        lo_i = max(1, int(lo))
        hi_i = min(int(max_hi), int(hi))
        if hi_i < lo_i:
            continue
        total_hit = float(np.sum(case["f_total"][lo_i : hi_i + 1]))
        if total_hit <= 0.0:
            out[window_name] = {
                "joint_mass": np.zeros(max_hi + 1, dtype=np.float64),
                "conditional_density": np.zeros(max_hi + 1, dtype=np.float64),
                "conditional_cdf": np.zeros(max_hi + 1, dtype=np.float64),
                "event_probability": 0.0,
                "mean_event_time_given_event": float("nan"),
                "mean_hit_time_in_window": float("nan"),
                "consistency_gap": 0.0,
            }
            continue

        b_next = np.zeros(n_states, dtype=np.float64)
        joint = np.zeros(max_hi + 1, dtype=np.float64)
        if first_event_at_zero > 0.0:
            # If the initial state is already inside the event set, the first event
            # happens at t=0 and the remaining hit probability is just the window mass.
            joint[0] = total_hit
        for t in range(hi_i - 1, -1, -1):
            if event_state_flat is not None:
                event_src = src_nonhit[event_state_flat[dst_nonhit]]
                event_dst = dst_nonhit[event_state_flat[dst_nonhit]]
                event_pr = prob_nonhit[event_state_flat[dst_nonhit]]
            else:
                assert event_edge_mask is not None
                event_src = src_nonhit[event_edge_mask]
                event_dst = dst_nonhit[event_edge_mask]
                event_pr = prob_nonhit[event_edge_mask]
            if event_src.size > 0:
                joint[t + 1] = float(np.sum(history_no_event[t][event_src] * event_pr * b_next[event_dst]))

            b_t = np.zeros(n_states, dtype=np.float64)
            np.add.at(b_t, src_nonhit, prob_nonhit * b_next[dst_nonhit])
            if lo_i <= (t + 1) <= hi_i:
                b_t += hit_prob
            b_next = b_t

        conditional_density = joint / total_hit
        conditional_cdf = np.cumsum(conditional_density)
        event_probability = float(conditional_cdf[-1]) if conditional_cdf.size else 0.0
        mean_event_time = float("nan")
        if event_probability > 0.0:
            mean_event_time = float(np.sum(t_idx * conditional_density) / event_probability)
        hit_weights = np.asarray(case["f_total"][lo_i : hi_i + 1], dtype=np.float64)
        mean_hit_time = float(np.sum(np.arange(lo_i, hi_i + 1, dtype=np.float64) * hit_weights) / total_hit)
        out[window_name] = {
            "joint_mass": joint,
            "conditional_density": conditional_density,
            "conditional_cdf": conditional_cdf,
            "event_probability": event_probability,
            "mean_event_time_given_event": mean_event_time,
            "mean_hit_time_in_window": mean_hit_time,
            "consistency_gap": float(abs(float(b_next[int(start_idx)]) - total_hit)),
        }
    return out


def membrane_edges_to_idx(
    *,
    membrane_edges: set[tuple[tuple[int, int], tuple[int, int]]],
    lx: int,
) -> set[tuple[int, int]]:
    return {
        _edge_idx_key(idx(a[0], a[1], lx), idx(b[0], b[1], lx))
        for (a, b) in membrane_edges
    }


def _build_rollback_exact_edges(
    *,
    n_states: int,
    start_idx: int,
    src_idx: np.ndarray,
    dst_idx: np.ndarray,
    probs: np.ndarray,
    target_idx: int,
    set_A: np.ndarray,
    membrane_idx_edges: set[tuple[int, int]],
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, int]:
    src = src_idx.astype(np.int64, copy=False)
    dst = dst_idx.astype(np.int64, copy=False)
    pr = probs.astype(np.float64, copy=False)

    is_hit = dst == int(target_idx)
    is_mem = np.fromiter(
        (_edge_idx_key(int(a), int(b)) in membrane_idx_edges for a, b in zip(src, dst)),
        dtype=bool,
        count=src.size,
    )
    is_A_dst = np.asarray(set_A[dst], dtype=bool)

    src_non = src[~is_hit]
    dst_non = dst[~is_hit]
    pr_non = pr[~is_hit]
    mem_non = is_mem[~is_hit]
    A_dst_non = is_A_dst[~is_hit]

    src_hit = src[is_hit]
    pr_hit = pr[is_hit]
    mem_hit = is_mem[is_hit]

    ext_src_parts: list[np.ndarray] = []
    ext_dst_parts: list[np.ndarray] = []
    ext_pr_parts: list[np.ndarray] = []
    hit_src_parts: list[np.ndarray] = []
    hit_cls_parts: list[np.ndarray] = []
    hit_pr_parts: list[np.ndarray] = []

    for leak in (0, 1):
        for left_a in (0, 1):
            for rollback in (0, 1):
                flag = _rollback_state_flag(leak, left_a, rollback)
                base = int(flag * n_states)

                leak_non = np.logical_or(bool(leak), mem_non)
                left_non = np.logical_or(bool(left_a), ~A_dst_non)
                rollback_non = np.logical_or(bool(rollback), np.logical_and(bool(left_a), A_dst_non))
                next_flag = (
                    leak_non.astype(np.int64)
                    + 2 * left_non.astype(np.int64)
                    + 4 * rollback_non.astype(np.int64)
                )

                ext_src_parts.append(base + src_non)
                ext_dst_parts.append(dst_non + next_flag * int(n_states))
                ext_pr_parts.append(pr_non)

                leak_hit = np.logical_or(bool(leak), mem_hit)
                cls_hit = 2 * leak_hit.astype(np.int64) + int(rollback)
                hit_src_parts.append(base + src_hit)
                hit_cls_parts.append(cls_hit.astype(np.int64))
                hit_pr_parts.append(pr_hit)

    ext_src = np.concatenate(ext_src_parts) if ext_src_parts else np.empty(0, dtype=np.int64)
    ext_dst = np.concatenate(ext_dst_parts) if ext_dst_parts else np.empty(0, dtype=np.int64)
    ext_pr = np.concatenate(ext_pr_parts) if ext_pr_parts else np.empty(0, dtype=np.float64)
    hit_src_ext = np.concatenate(hit_src_parts) if hit_src_parts else np.empty(0, dtype=np.int64)
    hit_cls = np.concatenate(hit_cls_parts) if hit_cls_parts else np.empty(0, dtype=np.int64)
    hit_pr = np.concatenate(hit_pr_parts) if hit_pr_parts else np.empty(0, dtype=np.float64)
    start_flag = _rollback_state_flag(0, int(not bool(set_A[int(start_idx)])), 0)
    return ext_src, ext_dst, ext_pr, hit_src_ext, hit_cls, hit_pr, start_flag


def exact_rollback_class_fpt(
    *,
    n_states: int,
    start_idx: int,
    src_idx: np.ndarray,
    dst_idx: np.ndarray,
    probs: np.ndarray,
    target_idx: int,
    set_A: np.ndarray,
    membrane_idx_edges: set[tuple[int, int]],
    t_max: int,
    surv_tol: float = 1.0e-12,
) -> tuple[np.ndarray, np.ndarray]:
    n_ext = int(n_states) * 8
    ext_src, ext_dst, ext_pr, hit_src_ext, hit_cls, hit_pr, start_flag = _build_rollback_exact_edges(
        n_states=n_states,
        start_idx=start_idx,
        src_idx=src_idx,
        dst_idx=dst_idx,
        probs=probs,
        target_idx=target_idx,
        set_A=set_A,
        membrane_idx_edges=membrane_idx_edges,
    )

    p = np.zeros(n_ext, dtype=np.float64)
    p[int(start_idx) + int(start_flag) * int(n_states)] = 1.0

    f_lr = np.zeros((int(t_max) + 1, 4), dtype=np.float64)
    surv = np.zeros(int(t_max) + 1, dtype=np.float64)
    surv[0] = 1.0

    for t in range(1, int(t_max) + 1):
        if hit_src_ext.size > 0:
            hit_flux = p[hit_src_ext] * hit_pr
            for cls in range(4):
                mask = hit_cls == cls
                if np.any(mask):
                    f_lr[t, cls] = float(np.sum(hit_flux[mask]))

        p_next = np.zeros_like(p)
        if ext_src.size > 0:
            np.add.at(p_next, ext_dst, p[ext_src] * ext_pr)

        surv[t] = max(0.0, float(np.sum(p_next)))
        p = p_next
        if surv[t] < float(surv_tol):
            if t < int(t_max):
                surv[t + 1 :] = surv[t]
            break

    return f_lr, surv


def summarize_rollback_class_masses(f_lr: np.ndarray) -> dict[str, float]:
    masses = np.asarray(f_lr, dtype=np.float64).sum(axis=0)
    total = float(np.sum(masses))
    if total <= 0.0:
        return {
            "no_leak_total": 0.0,
            "leak_total": 0.0,
            "rollback_total": 0.0,
            "pre_gate_leak_total": 0.0,
            "post_gate_leak_total": 0.0,
        }
    return {
        "no_leak_total": float((masses[0] + masses[1]) / total),
        "leak_total": float((masses[2] + masses[3]) / total),
        "rollback_total": float((masses[1] + masses[3]) / total),
        "pre_gate_leak_total": 0.0,
        "post_gate_leak_total": 0.0,
    }


def _build_gate_anchor_exact_edges(
    *,
    n_states: int,
    start_idx: int,
    src_idx: np.ndarray,
    dst_idx: np.ndarray,
    probs: np.ndarray,
    target_idx: int,
    set_A: np.ndarray,
    gate_mask: np.ndarray,
    membrane_idx_edges: set[tuple[int, int]],
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, int]:
    src = src_idx.astype(np.int64, copy=False)
    dst = dst_idx.astype(np.int64, copy=False)
    pr = probs.astype(np.float64, copy=False)

    is_hit = dst == int(target_idx)
    is_mem = np.fromiter(
        (_edge_idx_key(int(a), int(b)) in membrane_idx_edges for a, b in zip(src, dst)),
        dtype=bool,
        count=src.size,
    )
    is_A_src = np.asarray(set_A[src], dtype=bool)
    is_A_dst = np.asarray(set_A[dst], dtype=bool)
    is_gate_dst = np.asarray(gate_mask[dst], dtype=bool)

    src_non = src[~is_hit]
    dst_non = dst[~is_hit]
    pr_non = pr[~is_hit]
    mem_non = is_mem[~is_hit]
    A_src_non = is_A_src[~is_hit]
    A_dst_non = is_A_dst[~is_hit]
    gate_dst_non = is_gate_dst[~is_hit]

    src_hit = src[is_hit]
    pr_hit = pr[is_hit]
    mem_hit = is_mem[is_hit]
    gate_hit = is_gate_dst[is_hit]

    ext_src_parts: list[np.ndarray] = []
    ext_dst_parts: list[np.ndarray] = []
    ext_pr_parts: list[np.ndarray] = []
    hit_src_parts: list[np.ndarray] = []
    hit_cls_parts: list[np.ndarray] = []
    hit_pr_parts: list[np.ndarray] = []

    for leak_stage in range(3):
        for gate_seen in (0, 1):
            for rollback in (0, 1):
                flag = _gate_anchor_state_flag(leak_stage, gate_seen, rollback)
                base = int(flag * n_states)

                leak_non = np.full(src_non.shape, int(leak_stage), dtype=np.int64)
                leak_non = np.where((leak_non == 0) & mem_non & (~bool(gate_seen)), 1, leak_non)
                leak_non = np.where((leak_non == 0) & mem_non & bool(gate_seen), 2, leak_non)
                gate_non_next = np.logical_or(bool(gate_seen), gate_dst_non)
                rollback_non_next = np.logical_or(
                    bool(rollback),
                    np.logical_and(bool(gate_seen), np.logical_and(~A_src_non, A_dst_non)),
                )
                next_flag = leak_non + 3 * gate_non_next.astype(np.int64) + 6 * rollback_non_next.astype(np.int64)

                ext_src_parts.append(base + src_non)
                ext_dst_parts.append(dst_non + next_flag * int(n_states))
                ext_pr_parts.append(pr_non)

                leak_hit = np.full(src_hit.shape, int(leak_stage), dtype=np.int64)
                leak_hit = np.where((leak_hit == 0) & mem_hit & (~bool(gate_seen)), 1, leak_hit)
                leak_hit = np.where((leak_hit == 0) & mem_hit & bool(gate_seen), 2, leak_hit)
                cls_hit = _gate_anchor_family_flag(leak_hit, int(rollback))
                hit_src_parts.append(base + src_hit)
                hit_cls_parts.append(cls_hit.astype(np.int64))
                hit_pr_parts.append(pr_hit)

    ext_src = np.concatenate(ext_src_parts) if ext_src_parts else np.empty(0, dtype=np.int64)
    ext_dst = np.concatenate(ext_dst_parts) if ext_dst_parts else np.empty(0, dtype=np.int64)
    ext_pr = np.concatenate(ext_pr_parts) if ext_pr_parts else np.empty(0, dtype=np.float64)
    hit_src_ext = np.concatenate(hit_src_parts) if hit_src_parts else np.empty(0, dtype=np.int64)
    hit_cls = np.concatenate(hit_cls_parts) if hit_cls_parts else np.empty(0, dtype=np.int64)
    hit_pr = np.concatenate(hit_pr_parts) if hit_pr_parts else np.empty(0, dtype=np.float64)
    start_flag = _gate_anchor_state_flag(0, int(bool(gate_mask[int(start_idx)])), 0)
    return ext_src, ext_dst, ext_pr, hit_src_ext, hit_cls, hit_pr, start_flag


def exact_gate_anchor_family_fpt(
    *,
    n_states: int,
    start_idx: int,
    src_idx: np.ndarray,
    dst_idx: np.ndarray,
    probs: np.ndarray,
    target_idx: int,
    set_A: np.ndarray,
    gate_mask: np.ndarray,
    membrane_idx_edges: set[tuple[int, int]],
    t_max: int,
    surv_tol: float = 1.0e-12,
) -> tuple[np.ndarray, np.ndarray]:
    n_ext = int(n_states) * 12
    ext_src, ext_dst, ext_pr, hit_src_ext, hit_cls, hit_pr, start_flag = _build_gate_anchor_exact_edges(
        n_states=n_states,
        start_idx=start_idx,
        src_idx=src_idx,
        dst_idx=dst_idx,
        probs=probs,
        target_idx=target_idx,
        set_A=set_A,
        gate_mask=gate_mask,
        membrane_idx_edges=membrane_idx_edges,
    )

    p = np.zeros(n_ext, dtype=np.float64)
    p[int(start_idx) + int(start_flag) * int(n_states)] = 1.0

    f_family = np.zeros((int(t_max) + 1, 6), dtype=np.float64)
    surv = np.zeros(int(t_max) + 1, dtype=np.float64)
    surv[0] = 1.0

    for t in range(1, int(t_max) + 1):
        if hit_src_ext.size > 0:
            hit_flux = p[hit_src_ext] * hit_pr
            for cls in range(6):
                mask = hit_cls == cls
                if np.any(mask):
                    f_family[t, cls] = float(np.sum(hit_flux[mask]))

        p_next = np.zeros_like(p)
        if ext_src.size > 0:
            np.add.at(p_next, ext_dst, p[ext_src] * ext_pr)

        surv[t] = max(0.0, float(np.sum(p_next)))
        p = p_next
        if surv[t] < float(surv_tol):
            if t < int(t_max):
                surv[t + 1 :] = surv[t]
            break

    return f_family, surv


def marginalize_gate_anchor_to_lr(f_family: np.ndarray) -> np.ndarray:
    f_family = np.asarray(f_family, dtype=np.float64)
    f_lr = np.zeros((f_family.shape[0], 4), dtype=np.float64)
    f_lr[:, 0] = f_family[:, 0]
    f_lr[:, 1] = f_family[:, 1]
    f_lr[:, 2] = f_family[:, 2] + f_family[:, 4]
    f_lr[:, 3] = f_family[:, 3] + f_family[:, 5]
    return f_lr


def marginalize_gate_anchor_to_npq(f_family: np.ndarray) -> np.ndarray:
    f_family = np.asarray(f_family, dtype=np.float64)
    f_npq = np.zeros((f_family.shape[0], 3), dtype=np.float64)
    f_npq[:, 0] = f_family[:, 0] + f_family[:, 1]
    f_npq[:, 1] = f_family[:, 2] + f_family[:, 3]
    f_npq[:, 2] = f_family[:, 4] + f_family[:, 5]
    return f_npq


def exact_gate_anchor_npq_fpt(
    *,
    n_states: int,
    start_idx: int,
    src_idx: np.ndarray,
    dst_idx: np.ndarray,
    probs: np.ndarray,
    target_idx: int,
    set_A: np.ndarray,
    gate_mask: np.ndarray,
    membrane_idx_edges: set[tuple[int, int]],
    t_max: int,
    surv_tol: float = 1.0e-12,
) -> tuple[np.ndarray, np.ndarray]:
    f_family, surv = exact_gate_anchor_family_fpt(
        n_states=n_states,
        start_idx=start_idx,
        src_idx=src_idx,
        dst_idx=dst_idx,
        probs=probs,
        target_idx=target_idx,
        set_A=set_A,
        gate_mask=gate_mask,
        membrane_idx_edges=membrane_idx_edges,
        t_max=t_max,
        surv_tol=surv_tol,
    )
    return marginalize_gate_anchor_to_npq(f_family), surv


def summarize_gate_anchor_family_masses(f_family: np.ndarray) -> dict[str, float]:
    masses = np.asarray(f_family, dtype=np.float64).sum(axis=0)
    total = float(np.sum(masses))
    if total <= 0.0:
        return {
            "no_leak_total": 0.0,
            "pre_gate_leak_total": 0.0,
            "post_gate_leak_total": 0.0,
            "rollback_total": 0.0,
            "leak_total": 0.0,
        }
    return {
        "no_leak_total": float((masses[0] + masses[1]) / total),
        "pre_gate_leak_total": float((masses[2] + masses[3]) / total),
        "post_gate_leak_total": float((masses[4] + masses[5]) / total),
        "rollback_total": float((masses[1] + masses[3] + masses[5]) / total),
        "leak_total": float((masses[2] + masses[3] + masses[4] + masses[5]) / total),
    }


def summarize_gate_anchor_npq_masses(
    f_npq: np.ndarray,
    *,
    rollback_total: float | None = None,
) -> dict[str, float]:
    masses = np.asarray(f_npq, dtype=np.float64).sum(axis=0)
    total = float(np.sum(masses))
    if total <= 0.0:
        return {
            "no_leak_total": 0.0,
            "pre_gate_leak_total": 0.0,
            "post_gate_leak_total": 0.0,
            "rollback_total": 0.0,
            "leak_total": 0.0,
        }
    return {
        "no_leak_total": float(masses[0] / total),
        "pre_gate_leak_total": float(masses[1] / total),
        "post_gate_leak_total": float(masses[2] / total),
        "rollback_total": 0.0 if rollback_total is None else float(rollback_total),
        "leak_total": float((masses[1] + masses[2]) / total),
    }


def exact_gate_anchor_side_family_fpt(
    *,
    n_states: int,
    start_idx: int,
    src_idx: np.ndarray,
    dst_idx: np.ndarray,
    probs: np.ndarray,
    target_idx: int,
    gate_mask: np.ndarray,
    top_idx_edges: set[tuple[int, int]],
    bottom_idx_edges: set[tuple[int, int]],
    t_max: int,
    surv_tol: float = 1.0e-12,
) -> tuple[np.ndarray, np.ndarray]:
    src = src_idx.astype(np.int64, copy=False)
    dst = dst_idx.astype(np.int64, copy=False)
    pr = probs.astype(np.float64, copy=False)
    is_hit = dst == int(target_idx)
    edge_keys = np.fromiter(
        (_edge_idx_key(int(a), int(b)) for a, b in zip(src, dst)),
        dtype=object,
        count=src.size,
    )
    is_top = np.fromiter((k in top_idx_edges for k in edge_keys), dtype=bool, count=src.size)
    is_bottom = np.fromiter((k in bottom_idx_edges for k in edge_keys), dtype=bool, count=src.size)
    is_gate_dst = np.asarray(gate_mask[dst], dtype=bool)

    src_non = src[~is_hit]
    dst_non = dst[~is_hit]
    pr_non = pr[~is_hit]
    top_non = is_top[~is_hit]
    bottom_non = is_bottom[~is_hit]
    gate_dst_non = is_gate_dst[~is_hit]

    src_hit = src[is_hit]
    pr_hit = pr[is_hit]
    top_hit = is_top[is_hit]
    bottom_hit = is_bottom[is_hit]

    n_flags = 10
    ext_src_parts: list[np.ndarray] = []
    ext_dst_parts: list[np.ndarray] = []
    ext_pr_parts: list[np.ndarray] = []
    hit_src_parts: list[np.ndarray] = []
    hit_cls_parts: list[np.ndarray] = []
    hit_pr_parts: list[np.ndarray] = []

    for side_stage in range(5):
        for gate_seen in (0, 1):
            flag = _gate_anchor_side_flag(side_stage, gate_seen)
            base_flag = int(flag * n_states)

            side_non = np.full(src_non.shape, int(side_stage), dtype=np.int64)
            side_non = np.where((side_non == 0) & top_non & (~bool(gate_seen)), 1, side_non)
            side_non = np.where((side_non == 0) & bottom_non & (~bool(gate_seen)), 2, side_non)
            side_non = np.where((side_non == 0) & top_non & bool(gate_seen), 3, side_non)
            side_non = np.where((side_non == 0) & bottom_non & bool(gate_seen), 4, side_non)
            gate_non_next = np.logical_or(bool(gate_seen), gate_dst_non)
            flag_non = side_non + 5 * gate_non_next.astype(np.int64)

            ext_src_parts.append(base_flag + src_non)
            ext_dst_parts.append(dst_non + flag_non * n_states)
            ext_pr_parts.append(pr_non)

            side_hit = np.full(src_hit.shape, int(side_stage), dtype=np.int64)
            side_hit = np.where((side_hit == 0) & top_hit & (~bool(gate_seen)), 1, side_hit)
            side_hit = np.where((side_hit == 0) & bottom_hit & (~bool(gate_seen)), 2, side_hit)
            side_hit = np.where((side_hit == 0) & top_hit & bool(gate_seen), 3, side_hit)
            side_hit = np.where((side_hit == 0) & bottom_hit & bool(gate_seen), 4, side_hit)
            hit_src_parts.append(base_flag + src_hit)
            hit_cls_parts.append(side_hit.astype(np.int64))
            hit_pr_parts.append(pr_hit)

    ext_src = np.concatenate(ext_src_parts) if ext_src_parts else np.empty(0, dtype=np.int64)
    ext_dst = np.concatenate(ext_dst_parts) if ext_dst_parts else np.empty(0, dtype=np.int64)
    ext_pr = np.concatenate(ext_pr_parts) if ext_pr_parts else np.empty(0, dtype=np.float64)
    hit_src_ext = np.concatenate(hit_src_parts) if hit_src_parts else np.empty(0, dtype=np.int64)
    hit_cls = np.concatenate(hit_cls_parts) if hit_cls_parts else np.empty(0, dtype=np.int64)
    hit_pr = np.concatenate(hit_pr_parts) if hit_pr_parts else np.empty(0, dtype=np.float64)

    start_flag = _gate_anchor_side_flag(0, int(bool(gate_mask[int(start_idx)])))
    p = np.zeros(n_states * n_flags, dtype=np.float64)
    p[int(start_idx) + int(start_flag) * int(n_states)] = 1.0
    f_side = np.zeros((int(t_max) + 1, 5), dtype=np.float64)
    surv = np.zeros(int(t_max) + 1, dtype=np.float64)
    surv[0] = 1.0

    for t in range(1, int(t_max) + 1):
        if hit_src_ext.size > 0:
            hits = p[hit_src_ext] * hit_pr
            for cls in range(5):
                mask = hit_cls == cls
                if np.any(mask):
                    f_side[t, cls] = float(np.sum(hits[mask]))
        p_next = np.zeros_like(p)
        if ext_src.size > 0:
            np.add.at(p_next, ext_dst, p[ext_src] * ext_pr)
        surv[t] = max(0.0, float(p_next.sum()))
        p = p_next
        if surv[t] < float(surv_tol):
            if t < int(t_max):
                surv[t + 1 :] = surv[t]
            break

    return f_side, surv


def _build_lgr_exact_edges(
    *,
    n_states: int,
    start_idx: int,
    src_idx: np.ndarray,
    dst_idx: np.ndarray,
    probs: np.ndarray,
    target_idx: int,
    set_A: np.ndarray,
    gate_mask: np.ndarray,
    membrane_idx_edges: set[tuple[int, int]],
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, int]:
    src = src_idx.astype(np.int64, copy=False)
    dst = dst_idx.astype(np.int64, copy=False)
    pr = probs.astype(np.float64, copy=False)

    is_hit = dst == int(target_idx)
    is_mem = np.fromiter(
        (_edge_idx_key(int(a), int(b)) in membrane_idx_edges for a, b in zip(src, dst)),
        dtype=bool,
        count=src.size,
    )
    is_A_src = np.asarray(set_A[src], dtype=bool)
    is_A_dst = np.asarray(set_A[dst], dtype=bool)
    is_gate_dst = np.asarray(gate_mask[dst], dtype=bool)

    src_non = src[~is_hit]
    dst_non = dst[~is_hit]
    pr_non = pr[~is_hit]
    mem_non = is_mem[~is_hit]
    A_src_non = is_A_src[~is_hit]
    A_dst_non = is_A_dst[~is_hit]
    gate_dst_non = is_gate_dst[~is_hit]

    src_hit = src[is_hit]
    pr_hit = pr[is_hit]
    mem_hit = is_mem[is_hit]
    gate_hit = is_gate_dst[is_hit]

    ext_src_parts: list[np.ndarray] = []
    ext_dst_parts: list[np.ndarray] = []
    ext_pr_parts: list[np.ndarray] = []
    hit_src_parts: list[np.ndarray] = []
    hit_cls_parts: list[np.ndarray] = []
    hit_pr_parts: list[np.ndarray] = []

    for leak in (0, 1):
        for gate_seen in (0, 1):
            for rollback in (0, 1):
                flag = _lgr_flag(leak, gate_seen, rollback)
                base = int(flag * n_states)

                leak_non = np.logical_or(bool(leak), mem_non)
                gate_non_next = np.logical_or(bool(gate_seen), gate_dst_non)
                rollback_non_next = np.logical_or(
                    bool(rollback),
                    np.logical_and(bool(gate_seen), np.logical_and(~A_src_non, A_dst_non)),
                )
                next_flag = (
                    leak_non.astype(np.int64)
                    + 2 * gate_non_next.astype(np.int64)
                    + 4 * rollback_non_next.astype(np.int64)
                )

                ext_src_parts.append(base + src_non)
                ext_dst_parts.append(dst_non + next_flag * int(n_states))
                ext_pr_parts.append(pr_non)

                leak_hit = np.logical_or(bool(leak), mem_hit)
                gate_hit_next = np.logical_or(bool(gate_seen), gate_hit)
                cls_hit = (
                    leak_hit.astype(np.int64)
                    + 2 * gate_hit_next.astype(np.int64)
                    + 4 * int(rollback)
                )
                hit_src_parts.append(base + src_hit)
                hit_cls_parts.append(cls_hit.astype(np.int64))
                hit_pr_parts.append(pr_hit)

    ext_src = np.concatenate(ext_src_parts) if ext_src_parts else np.empty(0, dtype=np.int64)
    ext_dst = np.concatenate(ext_dst_parts) if ext_dst_parts else np.empty(0, dtype=np.int64)
    ext_pr = np.concatenate(ext_pr_parts) if ext_pr_parts else np.empty(0, dtype=np.float64)
    hit_src_ext = np.concatenate(hit_src_parts) if hit_src_parts else np.empty(0, dtype=np.int64)
    hit_cls = np.concatenate(hit_cls_parts) if hit_cls_parts else np.empty(0, dtype=np.int64)
    hit_pr = np.concatenate(hit_pr_parts) if hit_pr_parts else np.empty(0, dtype=np.float64)
    start_flag = _lgr_flag(0, int(bool(gate_mask[int(start_idx)])), 0)
    return ext_src, ext_dst, ext_pr, hit_src_ext, hit_cls, hit_pr, start_flag


def exact_lgr_class_fpt(
    *,
    n_states: int,
    start_idx: int,
    src_idx: np.ndarray,
    dst_idx: np.ndarray,
    probs: np.ndarray,
    target_idx: int,
    set_A: np.ndarray,
    gate_mask: np.ndarray,
    membrane_idx_edges: set[tuple[int, int]],
    t_max: int,
    surv_tol: float = 1.0e-12,
) -> tuple[np.ndarray, np.ndarray]:
    n_ext = int(n_states) * 8
    ext_src, ext_dst, ext_pr, hit_src_ext, hit_cls, hit_pr, start_flag = _build_lgr_exact_edges(
        n_states=n_states,
        start_idx=start_idx,
        src_idx=src_idx,
        dst_idx=dst_idx,
        probs=probs,
        target_idx=target_idx,
        set_A=set_A,
        gate_mask=gate_mask,
        membrane_idx_edges=membrane_idx_edges,
    )

    p = np.zeros(n_ext, dtype=np.float64)
    p[int(start_idx) + int(start_flag) * int(n_states)] = 1.0

    f_lgr = np.zeros((int(t_max) + 1, 8), dtype=np.float64)
    surv = np.zeros(int(t_max) + 1, dtype=np.float64)
    surv[0] = 1.0

    for t in range(1, int(t_max) + 1):
        if hit_src_ext.size > 0:
            hit_flux = p[hit_src_ext] * hit_pr
            for cls in range(8):
                mask = hit_cls == cls
                if np.any(mask):
                    f_lgr[t, cls] = float(np.sum(hit_flux[mask]))

        p_next = np.zeros_like(p)
        if ext_src.size > 0:
            np.add.at(p_next, ext_dst, p[ext_src] * ext_pr)

        surv[t] = max(0.0, float(np.sum(p_next)))
        p = p_next
        if surv[t] < float(surv_tol):
            if t < int(t_max):
                surv[t + 1 :] = surv[t]
            break

    return f_lgr, surv


def marginalize_lgr_to_lr(f_lgr: np.ndarray) -> np.ndarray:
    f_lgr = np.asarray(f_lgr, dtype=np.float64)
    f_lr = np.zeros((f_lgr.shape[0], 4), dtype=np.float64)
    for leak in (0, 1):
        for rollback in (0, 1):
            dst = leak + 2 * rollback
            cols = [_lgr_flag(leak, gate_seen, rollback) for gate_seen in (0, 1)]
            f_lr[:, dst] = np.sum(f_lgr[:, cols], axis=1)
    return f_lr


def exact_lr_class_fpt(
    *,
    n_states: int,
    start_idx: int,
    src_idx: np.ndarray,
    dst_idx: np.ndarray,
    probs: np.ndarray,
    target_idx: int,
    set_A: np.ndarray,
    q_values: np.ndarray,
    q_star: float,
    membrane_idx_edges: set[tuple[int, int]],
    t_max: int,
    surv_tol: float = 1.0e-12,
) -> tuple[np.ndarray, np.ndarray]:
    gate_mask = build_committor_gate_mask(q_values=q_values, q_star=q_star)
    f_lgr, surv = exact_lgr_class_fpt(
        n_states=n_states,
        start_idx=start_idx,
        src_idx=src_idx,
        dst_idx=dst_idx,
        probs=probs,
        target_idx=target_idx,
        set_A=set_A,
        gate_mask=gate_mask,
        membrane_idx_edges=membrane_idx_edges,
        t_max=t_max,
        surv_tol=surv_tol,
    )
    return marginalize_lgr_to_lr(f_lgr), surv


def window_fraction_dict(
    flux: np.ndarray,
    windows: list[tuple[str, int, int]],
    labels: list[str],
) -> dict[str, dict[str, float]]:
    out: dict[str, dict[str, float]] = {}
    for name, lo, hi in windows:
        mass = flux[lo : hi + 1].sum(axis=0)
        total = float(mass.sum())
        out[name] = {
            labels[i]: (float(mass[i] / total) if total > 0 else 0.0)
            for i in range(len(labels))
        }
    return out


def split_membrane_edges_by_side(
    *,
    membrane_edges: set[tuple[tuple[int, int], tuple[int, int]]],
    wall_span: tuple[int, int, int, int, int],
    lx: int,
) -> tuple[set[tuple[int, int]], set[tuple[int, int]]]:
    _, y_low, y_high, _, _ = wall_span
    top_edges: set[tuple[int, int]] = set()
    bottom_edges: set[tuple[int, int]] = set()
    for edge in membrane_edges:
        (x0, y0), (x1, y1) = edge
        key = _edge_idx_key(idx(x0, y0, lx), idx(x1, y1, lx))
        lowy, highy = min(y0, y1), max(y0, y1)
        if lowy == y_high and highy == y_high + 1:
            top_edges.add(key)
        elif lowy == y_low - 1 and highy == y_low:
            bottom_edges.add(key)
    return top_edges, bottom_edges


def exact_lgr_side_class_fpt(
    *,
    n_states: int,
    start_idx: int,
    src_idx: np.ndarray,
    dst_idx: np.ndarray,
    probs: np.ndarray,
    target_idx: int,
    set_A: np.ndarray,
    gate_mask: np.ndarray,
    top_idx_edges: set[tuple[int, int]],
    bottom_idx_edges: set[tuple[int, int]],
    t_max: int,
    surv_tol: float = 1.0e-12,
) -> tuple[np.ndarray, np.ndarray]:
    src = src_idx.astype(np.int64, copy=False)
    dst = dst_idx.astype(np.int64, copy=False)
    pr = probs.astype(np.float64, copy=False)
    is_hit = dst == int(target_idx)
    edge_keys = np.fromiter(
        (_edge_idx_key(int(a), int(b)) for a, b in zip(src, dst)),
        dtype=object,
        count=src.size,
    )
    is_top = np.fromiter((k in top_idx_edges for k in edge_keys), dtype=bool, count=src.size)
    is_bottom = np.fromiter((k in bottom_idx_edges for k in edge_keys), dtype=bool, count=src.size)
    is_A_src = np.asarray(set_A[src], dtype=bool)
    is_A_dst = np.asarray(set_A[dst], dtype=bool)
    is_gate_dst = np.asarray(gate_mask[dst], dtype=bool)

    src_non = src[~is_hit]
    dst_non = dst[~is_hit]
    pr_non = pr[~is_hit]
    top_non = is_top[~is_hit]
    bottom_non = is_bottom[~is_hit]
    A_src_non = is_A_src[~is_hit]
    A_dst_non = is_A_dst[~is_hit]
    gate_dst_non = is_gate_dst[~is_hit]

    src_hit = src[is_hit]
    pr_hit = pr[is_hit]
    top_hit = is_top[is_hit]
    bottom_hit = is_bottom[is_hit]
    gate_hit = is_gate_dst[is_hit]

    n_flags = 12
    ext_src_parts: list[np.ndarray] = []
    ext_dst_parts: list[np.ndarray] = []
    ext_pr_parts: list[np.ndarray] = []
    hit_src_parts: list[np.ndarray] = []
    hit_cls_parts: list[np.ndarray] = []
    hit_pr_parts: list[np.ndarray] = []

    for leak_state in range(3):
        for gate_seen in (0, 1):
            for rollback in (0, 1):
                flag = _side_lgr_flag(leak_state, gate_seen, rollback)
                base_flag = int(flag * n_states)
                leak_non = np.full(src_non.shape, leak_state, dtype=np.int64)
                leak_non = np.where((leak_non == 0) & top_non, 1, leak_non)
                leak_non = np.where((leak_non == 0) & bottom_non, 2, leak_non)
                gate_non_next = np.logical_or(bool(gate_seen), gate_dst_non)
                rollback_non = np.logical_or(
                    bool(rollback),
                    np.logical_and(bool(gate_seen), np.logical_and(~A_src_non, A_dst_non)),
                )
                flag_non = leak_non + 3 * gate_non_next.astype(np.int64) + 6 * rollback_non.astype(np.int64)

                ext_src_parts.append(base_flag + src_non)
                ext_dst_parts.append(dst_non + flag_non * n_states)
                ext_pr_parts.append(pr_non)

                leak_hit = np.full(src_hit.shape, leak_state, dtype=np.int64)
                leak_hit = np.where((leak_hit == 0) & top_hit, 1, leak_hit)
                leak_hit = np.where((leak_hit == 0) & bottom_hit, 2, leak_hit)
                gate_hit_next = np.logical_or(bool(gate_seen), gate_hit)
                cls_hit = leak_hit + 3 * gate_hit_next.astype(np.int64) + 6 * int(rollback)
                hit_src_parts.append(base_flag + src_hit)
                hit_cls_parts.append(cls_hit.astype(np.int64))
                hit_pr_parts.append(pr_hit)

    ext_src = np.concatenate(ext_src_parts) if ext_src_parts else np.empty(0, dtype=np.int64)
    ext_dst = np.concatenate(ext_dst_parts) if ext_dst_parts else np.empty(0, dtype=np.int64)
    ext_pr = np.concatenate(ext_pr_parts) if ext_pr_parts else np.empty(0, dtype=np.float64)
    hit_src_ext = np.concatenate(hit_src_parts) if hit_src_parts else np.empty(0, dtype=np.int64)
    hit_cls = np.concatenate(hit_cls_parts) if hit_cls_parts else np.empty(0, dtype=np.int64)
    hit_pr = np.concatenate(hit_pr_parts) if hit_pr_parts else np.empty(0, dtype=np.float64)

    start_flag = _side_lgr_flag(0, int(bool(gate_mask[int(start_idx)])), 0)
    p = np.zeros(n_states * n_flags, dtype=np.float64)
    p[int(start_idx) + int(start_flag) * int(n_states)] = 1.0
    f_side_lgr = np.zeros((int(t_max) + 1, n_flags), dtype=np.float64)
    surv = np.zeros(int(t_max) + 1, dtype=np.float64)
    surv[0] = 1.0

    for t in range(1, int(t_max) + 1):
        if hit_src_ext.size > 0:
            hits = p[hit_src_ext] * hit_pr
            for cls in range(n_flags):
                mask = hit_cls == cls
                if np.any(mask):
                    f_side_lgr[t, cls] = float(np.sum(hits[mask]))
        p_next = np.zeros_like(p)
        if ext_src.size > 0:
            np.add.at(p_next, ext_dst, p[ext_src] * ext_pr)
        surv[t] = max(0.0, float(p_next.sum()))
        p = p_next
        if surv[t] < float(surv_tol):
            if t < int(t_max):
                surv[t + 1 :] = surv[t]
            break

    return f_side_lgr, surv


def marginalize_side_lgr_to_side_r(f_side_lgr: np.ndarray) -> np.ndarray:
    f_side_lgr = np.asarray(f_side_lgr, dtype=np.float64)
    f_side = np.zeros((f_side_lgr.shape[0], 6), dtype=np.float64)
    for leak_state in range(3):
        for rollback in (0, 1):
            dst = leak_state * 2 + rollback
            cols = [_side_lgr_flag(leak_state, gate_seen, rollback) for gate_seen in (0, 1)]
            f_side[:, dst] = np.sum(f_side_lgr[:, cols], axis=1)
    return f_side


def exact_rollback_side_class_fpt(
    *,
    n_states: int,
    start_idx: int,
    src_idx: np.ndarray,
    dst_idx: np.ndarray,
    probs: np.ndarray,
    target_idx: int,
    set_A: np.ndarray,
    top_idx_edges: set[tuple[int, int]],
    bottom_idx_edges: set[tuple[int, int]],
    t_max: int,
    surv_tol: float = 1.0e-12,
) -> tuple[np.ndarray, np.ndarray]:
    src = src_idx.astype(np.int64, copy=False)
    dst = dst_idx.astype(np.int64, copy=False)
    pr = probs.astype(np.float64, copy=False)
    is_hit = dst == int(target_idx)
    edge_keys = np.fromiter(
        (_edge_idx_key(int(a), int(b)) for a, b in zip(src, dst)),
        dtype=object,
        count=src.size,
    )
    is_top = np.fromiter((k in top_idx_edges for k in edge_keys), dtype=bool, count=src.size)
    is_bottom = np.fromiter((k in bottom_idx_edges for k in edge_keys), dtype=bool, count=src.size)
    is_A_dst = np.asarray(set_A[dst], dtype=bool)

    src_non = src[~is_hit]
    dst_non = dst[~is_hit]
    pr_non = pr[~is_hit]
    top_non = is_top[~is_hit]
    bottom_non = is_bottom[~is_hit]
    A_dst_non = is_A_dst[~is_hit]

    src_hit = src[is_hit]
    pr_hit = pr[is_hit]
    top_hit = is_top[is_hit]
    bottom_hit = is_bottom[is_hit]

    n_flags = 12
    ext_src_parts: list[np.ndarray] = []
    ext_dst_parts: list[np.ndarray] = []
    ext_pr_parts: list[np.ndarray] = []
    hit_src_parts: list[np.ndarray] = []
    hit_cls_parts: list[np.ndarray] = []
    hit_pr_parts: list[np.ndarray] = []

    for leak_state in range(3):
        for left_a in (0, 1):
            for rollback in (0, 1):
                flag = _rollback_side_state_flag(leak_state, left_a, rollback)
                base_flag = int(flag * n_states)
                leak_non = np.full(src_non.shape, leak_state, dtype=np.int64)
                leak_non = np.where((leak_non == 0) & top_non, 1, leak_non)
                leak_non = np.where((leak_non == 0) & bottom_non, 2, leak_non)
                left_non = np.logical_or(bool(left_a), ~A_dst_non)
                rollback_non = np.logical_or(bool(rollback), np.logical_and(bool(left_a), A_dst_non))
                flag_non = leak_non + 3 * left_non.astype(np.int64) + 6 * rollback_non.astype(np.int64)

                ext_src_parts.append(base_flag + src_non)
                ext_dst_parts.append(dst_non + flag_non * n_states)
                ext_pr_parts.append(pr_non)

                leak_hit = np.full(src_hit.shape, leak_state, dtype=np.int64)
                leak_hit = np.where((leak_hit == 0) & top_hit, 1, leak_hit)
                leak_hit = np.where((leak_hit == 0) & bottom_hit, 2, leak_hit)
                cls_hit = 2 * leak_hit + int(rollback)
                hit_src_parts.append(base_flag + src_hit)
                hit_cls_parts.append(cls_hit.astype(np.int64))
                hit_pr_parts.append(pr_hit)

    ext_src = np.concatenate(ext_src_parts) if ext_src_parts else np.empty(0, dtype=np.int64)
    ext_dst = np.concatenate(ext_dst_parts) if ext_dst_parts else np.empty(0, dtype=np.int64)
    ext_pr = np.concatenate(ext_pr_parts) if ext_pr_parts else np.empty(0, dtype=np.float64)
    hit_src_ext = np.concatenate(hit_src_parts) if hit_src_parts else np.empty(0, dtype=np.int64)
    hit_cls = np.concatenate(hit_cls_parts) if hit_cls_parts else np.empty(0, dtype=np.int64)
    hit_pr = np.concatenate(hit_pr_parts) if hit_pr_parts else np.empty(0, dtype=np.float64)

    start_flag = _rollback_side_state_flag(0, int(not bool(set_A[int(start_idx)])), 0)
    p = np.zeros(n_states * n_flags, dtype=np.float64)
    p[int(start_idx) + int(start_flag) * int(n_states)] = 1.0
    f_side = np.zeros((int(t_max) + 1, 6), dtype=np.float64)
    surv = np.zeros(int(t_max) + 1, dtype=np.float64)
    surv[0] = 1.0

    for t in range(1, int(t_max) + 1):
        if hit_src_ext.size > 0:
            hits = p[hit_src_ext] * hit_pr
            for cls in range(6):
                mask = hit_cls == cls
                if np.any(mask):
                    f_side[t, cls] = float(np.sum(hits[mask]))
        p_next = np.zeros_like(p)
        if ext_src.size > 0:
            np.add.at(p_next, ext_dst, p[ext_src] * ext_pr)
        surv[t] = max(0.0, float(p_next.sum()))
        p = p_next
        if surv[t] < float(surv_tol):
            if t < int(t_max):
                surv[t + 1 :] = surv[t]
            break

    return f_side, surv


def exact_lr_side_class_fpt(
    *,
    n_states: int,
    start_idx: int,
    src_idx: np.ndarray,
    dst_idx: np.ndarray,
    probs: np.ndarray,
    target_idx: int,
    set_A: np.ndarray,
    q_values: np.ndarray,
    q_star: float,
    top_idx_edges: set[tuple[int, int]],
    bottom_idx_edges: set[tuple[int, int]],
    t_max: int,
    surv_tol: float = 1.0e-12,
) -> tuple[np.ndarray, np.ndarray]:
    gate_mask = build_committor_gate_mask(q_values=q_values, q_star=q_star)
    f_side_lgr, surv = exact_lgr_side_class_fpt(
        n_states=n_states,
        start_idx=start_idx,
        src_idx=src_idx,
        dst_idx=dst_idx,
        probs=probs,
        target_idx=target_idx,
        set_A=set_A,
        gate_mask=gate_mask,
        top_idx_edges=top_idx_edges,
        bottom_idx_edges=bottom_idx_edges,
        t_max=t_max,
        surv_tol=surv_tol,
    )
    return marginalize_side_lgr_to_side_r(f_side_lgr), surv


def build_membrane_case(
    *,
    Lx: int,
    Wy: int,
    bx: float,
    corridor_halfwidth: int,
    wall_margin: int,
    delta_core: float,
    delta_open: float,
    start_x: int,
    target_x: int,
    kappa_top: float,
    kappa_bottom: float,
    start: tuple[int, int] | None = None,
    target: tuple[int, int] | None = None,
    t_max_total: int = 5000,
) -> dict[str, Any]:
    start_default, target_default, local_bias_map, barrier_map, channel_mask, wall_span = build_ot_case_geometry(
        Lx=Lx,
        Wy=Wy,
        corridor_halfwidth=corridor_halfwidth,
        wall_margin=wall_margin,
        delta_core=delta_core,
        delta_open=delta_open,
        start_x=start_x,
        target_x=target_x,
    )
    start = start_default if start is None else (int(start[0]), int(start[1]))
    target = target_default if target is None else (int(target[0]), int(target[1]))
    y_mid, y_low, y_high, _, _ = wall_span

    membrane_edges: set[tuple[tuple[int, int], tuple[int, int]]] = set()
    for edge in list(barrier_map.keys()):
        (x0, y0), (x1, y1) = edge
        if x0 != x1 or abs(y1 - y0) != 1:
            continue
        lowy = min(y0, y1)
        highy = max(y0, y1)
        if lowy == y_low - 1 and highy == y_low:
            barrier_map[edge] = float(kappa_bottom)
            membrane_edges.add(edge)
        elif lowy == y_high and highy == y_high + 1:
            barrier_map[edge] = float(kappa_top)
            membrane_edges.add(edge)

    src_idx, dst_idx, probs = build_transition_arrays_general_rect(
        Lx=Lx,
        Wy=Wy,
        q=0.8,
        local_bias_map=local_bias_map,
        sticky_map={},
        barrier_map=barrier_map,
        long_range_map={},
        global_bias=(float(bx), 0.0),
    )

    f_total, f_corr, f_outer, surv = run_exact_one_target_rect(
        Lx=Lx,
        Wy=Wy,
        start=start,
        target=target,
        src_idx=src_idx,
        dst_idx=dst_idx,
        probs=probs,
        t_max=int(t_max_total),
        surv_tol=1.0e-12,
        channel_mask=channel_mask,
    )

    spec = type(
        "Spec",
        (),
        {
            "Wy": Wy,
            "bx": bx,
            "corridor_halfwidth": corridor_halfwidth,
            "wall_margin": wall_margin,
            "delta_core": delta_core,
            "delta_open": delta_open,
        },
    )()
    res = summarize_one_target(spec, f_total, surv)
    res.phase = classify_phase_one_target(res)

    return {
        "Lx": int(Lx),
        "start": start,
        "target": target,
        "wall_span": wall_span,
        "y_mid": y_mid,
        "channel_mask": channel_mask,
        "barrier_map": barrier_map,
        "membrane_edges": membrane_edges,
        "src_idx": src_idx,
        "dst_idx": dst_idx,
        "probs": probs,
        "f_total": f_total,
        "f_corr": f_corr,
        "f_outer": f_outer,
        "surv": surv,
        "res": res,
        "kappa_top": float(kappa_top),
        "kappa_bottom": float(kappa_bottom),
        "corridor_halfwidth": int(corridor_halfwidth),
        "wall_margin": int(wall_margin),
        "delta_core": float(delta_core),
        "delta_open": float(delta_open),
        "Wy": int(Wy),
        "bx": float(bx),
    }


def build_membrane_case_directional(
    *,
    Lx: int,
    Wy: int,
    bx: float,
    corridor_halfwidth: int,
    wall_margin: int,
    delta_core: float,
    delta_open: float,
    start_x: int,
    target_x: int,
    kappa_c2o: float,
    kappa_o2c: float,
    start: tuple[int, int] | None = None,
    target: tuple[int, int] | None = None,
    t_max_total: int = 5000,
) -> dict[str, Any]:
    start_default, target_default, local_bias_map, barrier_map, channel_mask, wall_span = build_ot_case_geometry(
        Lx=Lx,
        Wy=Wy,
        corridor_halfwidth=corridor_halfwidth,
        wall_margin=wall_margin,
        delta_core=delta_core,
        delta_open=delta_open,
        start_x=start_x,
        target_x=target_x,
    )
    y_mid, y_low, y_high, _, _ = wall_span
    start = start_default if start is None else (int(start[0]), int(start[1]))
    target = target_default if target is None else (int(target[0]), int(target[1]))

    local_bias_map.pop(start_default, None)
    local_bias_map.pop(target_default, None)
    local_bias_map.pop(start, None)
    local_bias_map.pop(target, None)

    membrane_edges: set[tuple[tuple[int, int], tuple[int, int]]] = set()
    directed_barrier_map: dict[tuple[tuple[int, int], tuple[int, int]], float] = {}
    membrane_c2o_edges: set[tuple[tuple[int, int], tuple[int, int]]] = set()
    membrane_o2c_edges: set[tuple[tuple[int, int], tuple[int, int]]] = set()
    for edge in list(barrier_map.keys()):
        (x0, y0), (x1, y1) = edge
        if x0 != x1 or abs(y1 - y0) != 1:
            continue
        lowy = min(y0, y1)
        highy = max(y0, y1)
        if not (lowy == y_low - 1 and highy == y_low) and not (lowy == y_high and highy == y_high + 1):
            continue
        membrane_edges.add(edge)
        a, b = edge
        a_in = bool(channel_mask[idx(a[0], a[1], Lx)])
        b_in = bool(channel_mask[idx(b[0], b[1], Lx)])
        if a_in == b_in:
            continue
        c = a if a_in else b
        o = b if a_in else a
        directed_barrier_map[(c, o)] = float(kappa_c2o)
        directed_barrier_map[(o, c)] = float(kappa_o2c)
        membrane_c2o_edges.add((c, o))
        membrane_o2c_edges.add((o, c))

    src_idx, dst_idx, probs = build_transition_arrays_general_rect(
        Lx=Lx,
        Wy=Wy,
        q=0.8,
        local_bias_map=local_bias_map,
        sticky_map={},
        barrier_map=barrier_map,
        directed_barrier_map=directed_barrier_map,
        long_range_map={},
        global_bias=(float(bx), 0.0),
    )

    f_total, f_corr, f_outer, surv = run_exact_one_target_rect(
        Lx=Lx,
        Wy=Wy,
        start=start,
        target=target,
        src_idx=src_idx,
        dst_idx=dst_idx,
        probs=probs,
        t_max=int(t_max_total),
        surv_tol=1.0e-12,
        channel_mask=channel_mask,
    )

    spec = type(
        "Spec",
        (),
        {
            "Wy": Wy,
            "bx": bx,
            "corridor_halfwidth": corridor_halfwidth,
            "wall_margin": wall_margin,
            "delta_core": delta_core,
            "delta_open": delta_open,
        },
    )()
    res = summarize_one_target(spec, f_total, surv)
    res.phase = classify_phase_one_target(res)

    return {
        "Lx": int(Lx),
        "start": start,
        "target": target,
        "wall_span": wall_span,
        "y_mid": y_mid,
        "channel_mask": channel_mask,
        "barrier_map": barrier_map,
        "directed_barrier_map": directed_barrier_map,
        "membrane_edges": membrane_edges,
        "membrane_c2o_edges": membrane_c2o_edges,
        "membrane_o2c_edges": membrane_o2c_edges,
        "src_idx": src_idx,
        "dst_idx": dst_idx,
        "probs": probs,
        "f_total": f_total,
        "f_corr": f_corr,
        "f_outer": f_outer,
        "surv": surv,
        "res": res,
        "kappa_c2o": float(kappa_c2o),
        "kappa_o2c": float(kappa_o2c),
        "corridor_halfwidth": int(corridor_halfwidth),
        "wall_margin": int(wall_margin),
        "delta_core": float(delta_core),
        "delta_open": float(delta_open),
        "Wy": int(Wy),
        "bx": float(bx),
    }


__all__ = [
    "GateMode",
    "GATE_ANCHOR_FAMILY_LABELS",
    "LGR_STATE_LABELS",
    "LR_STATE_LABELS",
    "SIDE_GATE_ANCHOR_LABELS",
    "SIDE_LGR_STATE_LABELS",
    "SIDE_R_LABELS",
    "THREE_FAMILY_LABELS",
    "build_committor_gate_mask",
    "build_membrane_case_directional",
    "build_membrane_case",
    "build_start_basin_mask",
    "build_x_gate_mask",
    "compute_one_target_forward_history",
    "compute_one_target_first_event_statistics",
    "compute_one_target_window_path_statistics",
    "exact_gate_anchor_family_fpt",
    "exact_gate_anchor_npq_fpt",
    "exact_gate_anchor_side_family_fpt",
    "exact_lgr_class_fpt",
    "exact_lgr_side_class_fpt",
    "exact_rollback_class_fpt",
    "exact_rollback_side_class_fpt",
    "exact_lr_class_fpt",
    "exact_lr_side_class_fpt",
    "marginalize_gate_anchor_to_npq",
    "marginalize_gate_anchor_to_lr",
    "marginalize_lgr_to_lr",
    "marginalize_side_lgr_to_side_r",
    "membrane_edges_to_idx",
    "solve_committor",
    "split_membrane_edges_by_side",
    "summarize_gate_anchor_family_masses",
    "summarize_gate_anchor_npq_masses",
    "summarize_rollback_class_masses",
    "window_fraction_dict",
    "window_ranges",
]
