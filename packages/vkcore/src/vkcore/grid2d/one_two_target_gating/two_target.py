from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

Coord = Tuple[int, int]

# ----------------------------
# Base exact model (matched to repo)
# ----------------------------

DIR_VEC: dict[str, Coord] = {
    "E": (1, 0),
    "W": (-1, 0),
    "N": (0, 1),
    "S": (0, -1),
}


@dataclass(frozen=True)
class TwoTargetCase:
    name: str
    Lx: int
    Wy: int
    start: Coord
    near: Coord
    far: Coord
    bx: float
    near_dx: int
    near_dy: int
    src_idx: np.ndarray
    dst_idx: np.ndarray
    probs: np.ndarray
    f_total: np.ndarray
    f_near: np.ndarray
    f_far: np.ndarray
    surv: np.ndarray
    t_peak1: int | None
    t_valley: int | None
    t_peak2: int | None
    peak_ratio: float | None
    valley_over_max: float | None
    p_near: float
    p_far: float
    t_mode_near: int
    t_mode_far: int
    hw_near: float
    hw_far: float
    sep_mode: float
    phase: int


@dataclass(frozen=True)
class GateConfig:
    near_ring_radius: int = 2
    x_out_offset: int = 2
    x_in_offset: int = 0
    progress_fracs: Tuple[float, ...] = (0.33, 0.66)


FAMILY_LABELS_FINE = [
    "N_direct",
    "N_detour",
    "F_clean",
    "F_linger",
    "F_rollback",
]

FAMILY_LABELS_COARSE = [
    "N_direct",
    "N_detour",
    "F_no_return",
    "F_rollback",
]


def idx(x: int, y: int, Lx: int) -> int:
    return y * Lx + x


def project_mass_nonnegative(p: np.ndarray, *, cap: float, eps: float = 1e-12) -> float:
    np.maximum(p, 0.0, out=p)
    s = float(p.sum())
    cap = max(0.0, float(cap))
    if s <= cap:
        return s
    if s <= cap + float(eps):
        if s > 0.0:
            p *= cap / s
        else:
            p.fill(0.0)
        return cap
    if s > 0.0:
        p *= cap / s
    else:
        p.fill(0.0)
    return cap


def _parse_global_bias(q: float, bx: float, by: float) -> Dict[str, float]:
    moves = {
        "E": q / 4.0 + 0.5 * bx,
        "W": q / 4.0 - 0.5 * bx,
        "N": q / 4.0 + 0.5 * by,
        "S": q / 4.0 - 0.5 * by,
    }
    arr = np.asarray([moves["E"], moves["W"], moves["N"], moves["S"]], dtype=np.float64)
    arr = np.maximum(arr, 0.0)
    s = float(arr.sum())
    if s <= 0.0:
        arr[:] = q / 4.0
    else:
        arr *= q / s
    return {
        "E": float(arr[0]),
        "W": float(arr[1]),
        "N": float(arr[2]),
        "S": float(arr[3]),
    }


def build_transition_arrays_general_rect(
    *,
    Lx: int,
    Wy: int,
    q: float,
    local_bias_map: Dict[Coord, Tuple[str, float]],
    sticky_map: Dict[Coord, float],
    barrier_map: Dict[Tuple[Coord, Coord], float],
    long_range_map: Dict[Coord, List[Tuple[Coord, float]]],
    global_bias: Tuple[float, float],
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    base_moves = _parse_global_bias(q, float(global_bias[0]), float(global_bias[1]))
    src: List[int] = []
    dst: List[int] = []
    prob: List[float] = []
    for y in range(Wy):
        for x in range(Lx):
            c = (x, y)
            moves = dict(base_moves)
            sticky = float(sticky_map.get(c, 1.0))
            sticky = min(max(sticky, 0.0), 1.0)
            for d in moves:
                moves[d] *= sticky
            p_stay = 1.0 - float(sum(moves.values()))
            if p_stay < 0.0 and p_stay > -1e-12:
                p_stay = 0.0
            if p_stay < -1e-9:
                raise ValueError(f"negative stay probability at {c}: {p_stay}")
            lb = local_bias_map.get(c)
            if lb is not None and p_stay > 0.0:
                d, delta = lb
                if d not in DIR_VEC:
                    raise ValueError(f"unknown local bias direction: {d}")
                delta = float(min(max(delta, 0.0), 1.0))
                shift = delta * p_stay
                p_stay -= shift
                moves[d] += shift
            out: Dict[int, float] = {}
            stay_extra = p_stay
            for d, p in moves.items():
                if p <= 0.0:
                    continue
                dx0, dy0 = DIR_VEC[d]
                nx = x + dx0
                ny = y + dy0
                if nx < 0 or nx >= Lx or ny < 0 or ny >= Wy:
                    stay_extra += p
                    continue
                edge_key = ((x, y), (nx, ny)) if (x, y) <= (nx, ny) else ((nx, ny), (x, y))
                pass_prob = float(barrier_map.get(edge_key, 1.0))
                pass_prob = min(max(pass_prob, 0.0), 1.0)
                flow = p * pass_prob
                blocked = p - flow
                if blocked > 0.0:
                    stay_extra += blocked
                if flow > 0.0:
                    j = idx(nx, ny, Lx)
                    out[j] = out.get(j, 0.0) + flow
            for to_pos, p_jump in long_range_map.get(c, []):
                if p_jump <= 0.0:
                    continue
                take = min(float(p_jump), max(stay_extra, 0.0))
                if take <= 0.0:
                    continue
                stay_extra -= take
                j_to = idx(to_pos[0], to_pos[1], Lx)
                out[j_to] = out.get(j_to, 0.0) + take
            j_self = idx(x, y, Lx)
            out[j_self] = out.get(j_self, 0.0) + stay_extra
            s = float(sum(out.values()))
            if s <= 0.0:
                raise ValueError(f"row sum <= 0 at {(x, y)}")
            if not np.isclose(s, 1.0, atol=1e-12):
                for j in list(out.keys()):
                    out[j] /= s
            i = idx(x, y, Lx)
            for j, p in out.items():
                src.append(i)
                dst.append(j)
                prob.append(float(p))
    return np.asarray(src, dtype=np.int64), np.asarray(dst, dtype=np.int64), np.asarray(prob, dtype=np.float64)


def run_exact_two_target_rect(
    *,
    Lx: int,
    Wy: int,
    start: Coord,
    target1: Coord,
    target2: Coord,
    src_idx: np.ndarray,
    dst_idx: np.ndarray,
    probs: np.ndarray,
    t_max: int,
    surv_tol: float,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    n_states = Lx * Wy
    i_start = idx(start[0], start[1], Lx)
    i_m1 = idx(target1[0], target1[1], Lx)
    i_m2 = idx(target2[0], target2[1], Lx)
    p = np.zeros(n_states, dtype=np.float64)
    p[i_start] = 1.0
    f_any = [0.0]
    f_m1 = [0.0]
    f_m2 = [0.0]
    surv = [1.0]
    for _ in range(1, int(t_max) + 1):
        surv_prev = float(surv[-1])
        p_next = np.zeros_like(p)
        np.add.at(p_next, dst_idx, p[src_idx] * probs)
        hit1 = max(float(p_next[i_m1]), 0.0)
        hit2 = max(float(p_next[i_m2]), 0.0)
        hit = hit1 + hit2
        if hit > surv_prev:
            scale = (surv_prev / hit) if hit > 0.0 else 0.0
            hit1 *= scale
            hit2 *= scale
            hit = surv_prev
        p_next[i_m1] = 0.0
        p_next[i_m2] = 0.0
        remaining_cap = max(0.0, surv_prev - hit)
        s = project_mass_nonnegative(p_next, cap=remaining_cap)
        f_any.append(hit)
        f_m1.append(hit1)
        f_m2.append(hit2)
        surv.append(s)
        p = p_next
        if s < surv_tol:
            break
    return (
        np.asarray(f_any, dtype=np.float64),
        np.asarray(f_m1, dtype=np.float64),
        np.asarray(f_m2, dtype=np.float64),
        np.asarray(surv, dtype=np.float64),
    )


# ----------------------------
# Peak / phase logic (matched to repo)
# ----------------------------


def smooth_series_display(y: np.ndarray, window: int = 5) -> np.ndarray:
    w = int(max(1, window))
    if w <= 1 or y.size < w:
        return y.astype(np.float64, copy=True)
    if w % 2 == 0:
        w += 1
    pad = w // 2
    ypad = np.pad(y.astype(np.float64), (pad, pad), mode="edge")
    kernel = np.ones(w, dtype=np.float64) / float(w)
    return np.convolve(ypad, kernel, mode="valid")


def find_two_peaks(
    f: np.ndarray,
    *,
    min_rel_height: float = 0.06,
    min_gap: int = 20,
    smooth_window: int = 7,
    min_peak_balance: float = 0.08,
    min_valley_drop: float = 0.08,
    min_minor_peak_drop: float = 0.005,
    dominance_tol: float = 0.02,
) -> Tuple[int | None, int | None]:
    if f.size < 3:
        return None, None
    fs = smooth_series_display(f.astype(np.float64), window=max(3, int(smooth_window)))
    f_max = float(np.max(fs))
    if f_max <= 0.0:
        return None, None
    thr = float(min_rel_height) * f_max
    peaks: List[int] = []
    for t in range(1, fs.size - 1):
        if fs[t] > fs[t - 1] and fs[t] >= fs[t + 1] and fs[t] >= thr:
            peaks.append(t)
    if len(peaks) < 2:
        return None, None
    gap = max(1, int(min_gap))
    best_pair: Tuple[int, int] | None = None
    best_score = -1.0
    for i, a in enumerate(peaks[:-1]):
        ha = float(fs[a])
        for b in peaks[i + 1 :]:
            if (b - a) < gap:
                continue
            hb = float(fs[b])
            if ha <= 0.0 or hb <= 0.0:
                continue
            k_min = int(np.argmin(fs[a : b + 1]))
            v_idx = int(a + k_min)
            if not (a < v_idx < b):
                continue
            left_dom = float(np.max(fs[: v_idx + 1]))
            right_dom = float(np.max(fs[v_idx:]))
            tol = max(0.0, float(dominance_tol))
            if ha < (1.0 - tol) * left_dom:
                continue
            if hb < (1.0 - tol) * right_dom:
                continue
            bal = float(min(ha, hb) / max(ha, hb))
            if bal < float(min_peak_balance):
                continue
            hv = float(fs[v_idx])
            valley_drop = float(1.0 - hv / max(ha, hb))
            if valley_drop < float(min_valley_drop):
                continue
            minor_drop = float(1.0 - hv / max(min(ha, hb), 1e-15))
            if minor_drop < float(min_minor_peak_drop):
                continue
            score = float(b - a) * min(ha, hb) * valley_drop * max(1e-6, minor_drop)
            if score > best_score:
                best_score = score
                best_pair = (int(a), int(b))
    if best_pair is None:
        return None, None
    return best_pair


def half_width_at_half_max(f: np.ndarray, mode: int) -> float:
    if mode <= 0 or mode >= len(f):
        return 0.0
    peak = float(f[mode])
    if peak <= 0.0:
        return 0.0
    thr = 0.5 * peak
    left = int(mode)
    right = int(mode)
    while left > 1 and f[left - 1] >= thr:
        left -= 1
    while right < len(f) - 1 and f[right + 1] >= thr:
        right += 1
    return 0.5 * float(right - left)


def summarize_case(
    *,
    Lx: int,
    Wy: int,
    name: str,
    start: Coord,
    near: Coord,
    far: Coord,
    bx: float,
    near_dx: int,
    near_dy: int,
    src_idx: np.ndarray,
    dst_idx: np.ndarray,
    probs: np.ndarray,
    f_total: np.ndarray,
    f_near: np.ndarray,
    f_far: np.ndarray,
    surv: np.ndarray,
) -> TwoTargetCase:
    tp1, tp2 = find_two_peaks(f_total)
    tv = None
    peak_ratio = None
    valley_over_max = None
    f_s = smooth_series_display(f_total.astype(np.float64), window=7)
    if tp1 is not None and tp2 is not None and tp1 + 1 < tp2:
        window = f_s[tp1 : tp2 + 1]
        k = int(np.argmin(window))
        tv = tp1 + k
        hp1 = float(f_s[tp1])
        hp2 = float(f_s[tp2])
        hv = float(f_s[tv])
        if hp1 > 0.0 and hp2 > 0.0:
            peak_ratio = float(min(hp1, hp2) / max(hp1, hp2))
            valley_over_max = float(hv / max(hp1, hp2))
    absorbed = float(np.sum(f_total))
    p_near = float(np.sum(f_near) / absorbed) if absorbed > 1e-15 else 0.0
    p_far = float(np.sum(f_far) / absorbed) if absorbed > 1e-15 else 0.0
    t_mode_near = int(np.argmax(f_near[1:]) + 1) if len(f_near) > 1 else 0
    t_mode_far = int(np.argmax(f_far[1:]) + 1) if len(f_far) > 1 else 0
    hw_near = half_width_at_half_max(f_near, t_mode_near)
    hw_far = half_width_at_half_max(f_far, t_mode_far)
    denom = hw_near + hw_far
    sep_mode = float(abs(t_mode_far - t_mode_near) / denom) if denom > 0 else 0.0
    has_double = int(tp1 is not None and tp2 is not None)
    clear_double = int(has_double and sep_mode >= 1.0)
    phase = 2 if clear_double else (1 if has_double else 0)
    return TwoTargetCase(
        name=name,
        Lx=Lx,
        Wy=Wy,
        start=start,
        near=near,
        far=far,
        bx=bx,
        near_dx=near_dx,
        near_dy=near_dy,
        src_idx=src_idx,
        dst_idx=dst_idx,
        probs=probs,
        f_total=f_total,
        f_near=f_near,
        f_far=f_far,
        surv=surv,
        t_peak1=tp1,
        t_valley=tv,
        t_peak2=tp2,
        peak_ratio=peak_ratio,
        valley_over_max=valley_over_max,
        p_near=p_near,
        p_far=p_far,
        t_mode_near=t_mode_near,
        t_mode_far=t_mode_far,
        hw_near=hw_near,
        hw_far=hw_far,
        sep_mode=sep_mode,
        phase=phase,
    )


def build_case(
    *,
    name: str,
    Lx: int = 60,
    Wy: int = 16,
    start_x: int = 7,
    far_target_x: int = 58,
    near_dx: int,
    near_dy: int,
    bx: float,
    q: float = 0.8,
    t_max: int = 5000,
    surv_tol: float = 1e-12,
) -> TwoTargetCase:
    y_mid = int((Wy - 1) // 2)
    start = (int(start_x), y_mid)
    near = (min(Lx - 2, int(start_x + near_dx)), max(0, min(Wy - 1, y_mid + int(near_dy))))
    far = (int(far_target_x), y_mid)
    src_idx, dst_idx, probs = build_transition_arrays_general_rect(
        Lx=Lx,
        Wy=Wy,
        q=q,
        local_bias_map={},
        sticky_map={},
        barrier_map={},
        long_range_map={},
        global_bias=(float(bx), 0.0),
    )
    f_total, f_near, f_far, surv = run_exact_two_target_rect(
        Lx=Lx,
        Wy=Wy,
        start=start,
        target1=near,
        target2=far,
        src_idx=src_idx,
        dst_idx=dst_idx,
        probs=probs,
        t_max=t_max,
        surv_tol=surv_tol,
    )
    return summarize_case(
        Lx=Lx,
        Wy=Wy,
        name=name,
        start=start,
        near=near,
        far=far,
        bx=bx,
        near_dx=near_dx,
        near_dy=near_dy,
        src_idx=src_idx,
        dst_idx=dst_idx,
        probs=probs,
        f_total=f_total,
        f_near=f_near,
        f_far=f_far,
        surv=surv,
    )


def solve_committor(
    *,
    n_states: int,
    src_idx: np.ndarray,
    dst_idx: np.ndarray,
    probs: np.ndarray,
    set_A: np.ndarray,
    set_B: np.ndarray,
    max_iter: int = 20000,
    tol: float = 1e-11,
) -> np.ndarray:
    q = np.zeros(n_states, dtype=np.float64)
    q[set_B] = 1.0
    for _ in range(max_iter):
        acc = np.bincount(src_idx, weights=probs * q[dst_idx], minlength=n_states)
        acc[set_A] = 0.0
        acc[set_B] = 1.0
        diff = float(np.max(np.abs(acc - q)))
        q = acc
        if diff < tol:
            break
    return q


def committor_diagnostics(case: TwoTargetCase) -> dict:
    n_states = int(case.Lx * case.Wy)
    near_i = idx(case.near[0], case.near[1], case.Lx)
    far_i = idx(case.far[0], case.far[1], case.Lx)
    start_i = idx(case.start[0], case.start[1], case.Lx)
    set_A = np.zeros(n_states, dtype=bool)
    set_B = np.zeros(n_states, dtype=bool)
    set_A[near_i] = True
    set_B[far_i] = True
    q_far = solve_committor(
        n_states=n_states,
        src_idx=case.src_idx,
        dst_idx=case.dst_idx,
        probs=case.probs,
        set_A=set_A,
        set_B=set_B,
    )
    q_next = np.bincount(case.src_idx, weights=case.probs * q_far[case.dst_idx], minlength=n_states)
    interior = np.logical_not(np.logical_or(set_A, set_B))
    interior_res = float(np.max(np.abs(q_far[interior] - q_next[interior]))) if np.any(interior) else 0.0
    return {
        "q_far": q_far,
        "q_far_start": float(q_far[start_i]),
        "consistency_gap_vs_p_far": float(abs(float(q_far[start_i]) - float(case.p_far))),
        "interior_residual_inf": interior_res,
    }


def window_ranges(tp1: int | None, tv: int | None, tp2: int | None, n: int) -> List[Tuple[str, int, int]]:
    if tp1 is None or tv is None or tp2 is None:
        return [("early", 10, 60), ("middle", 120, 200), ("late", 260, 360)]
    gap = max(20, int(tp2) - int(tp1))
    half = int(max(8, min(26, gap // 7)))
    return [
        ("peak1", max(1, int(tp1) - half), min(n - 1, int(tp1) + half)),
        ("valley", max(1, int(tv) - half), min(n - 1, int(tv) + half)),
        ("peak2", max(1, int(tp2) - half), min(n - 1, int(tp2) + half)),
    ]


# ----------------------------
# Gate-lifted exact family decomposition
# ----------------------------


def build_augmented_gate_model(case: TwoTargetCase, gate: GateConfig) -> dict:
    Lx = case.Lx
    n_states = int(case.Lx * case.Wy)
    near_i = idx(case.near[0], case.near[1], case.Lx)
    far_i = idx(case.far[0], case.far[1], case.Lx)
    xs = np.arange(n_states) % Lx
    ys = np.arange(n_states) // Lx
    near_ring = (
        (np.abs(xs - case.near[0]) + np.abs(ys - case.near[1]) <= int(gate.near_ring_radius))
        & (np.arange(n_states) != near_i)
        & (np.arange(n_states) != far_i)
    )
    x_out = min(Lx - 2, int(case.near[0] + gate.x_out_offset))
    x_in = min(x_out - 1, int(case.near[0] + gate.x_in_offset))
    src_x = xs[case.src_idx]
    dst_x = xs[case.dst_idx]
    cross_out = (src_x == x_out) & (dst_x == x_out + 1)
    cross_in = (src_x == x_in + 1) & (dst_x == x_in)
    n_aug = n_states * 8
    src_aug: List[int] = []
    dst_aug: List[int] = []
    prob_aug: List[float] = []
    abs_src_aug: List[int] = []
    abs_family: List[int] = []
    abs_prob: List[float] = []
    for linger in (0, 1):
        for escaped in (0, 1):
            for rollback in (0, 1):
                off = n_states * (linger + 2 * escaped + 4 * rollback)
                for s, d, p, co, ci in zip(case.src_idx, case.dst_idx, case.probs, cross_out, cross_in):
                    s = int(s)
                    d = int(d)
                    p = float(p)
                    if s == near_i or s == far_i:
                        continue
                    nl, ne, nr = linger, escaped, rollback
                    if co:
                        ne = 1
                    if escaped and ci:
                        nr = 1
                    if (ne == 0) and near_ring[d]:
                        nl = 1
                    srca = s + off
                    if d == near_i:
                        fam = 0 if ne == 0 else 1
                        abs_src_aug.append(srca)
                        abs_family.append(fam)
                        abs_prob.append(p)
                    elif d == far_i:
                        fam = 4 if nr == 1 else (3 if nl == 1 else 2)
                        abs_src_aug.append(srca)
                        abs_family.append(fam)
                        abs_prob.append(p)
                    else:
                        dsta = d + n_states * (nl + 2 * ne + 4 * nr)
                        src_aug.append(srca)
                        dst_aug.append(dsta)
                        prob_aug.append(p)
    x_start_progress = x_out + 1
    x_far = case.far[0]
    progress_xs: List[int] = []
    for frac in gate.progress_fracs:
        gx = int(round(x_start_progress + float(frac) * (x_far - x_start_progress)))
        gx = max(x_start_progress, min(x_far - 1, gx))
        if gx not in progress_xs:
            progress_xs.append(gx)
    return {
        "near_ring": near_ring,
        "x_out": x_out,
        "x_in": x_in,
        "progress_xs": progress_xs,
        "src_aug": np.asarray(src_aug, dtype=np.int64),
        "dst_aug": np.asarray(dst_aug, dtype=np.int64),
        "prob_aug": np.asarray(prob_aug, dtype=np.float64),
        "abs_src_aug": np.asarray(abs_src_aug, dtype=np.int64),
        "abs_family": np.asarray(abs_family, dtype=np.int64),
        "abs_prob": np.asarray(abs_prob, dtype=np.float64),
        "n_states": n_states,
        "n_aug": n_aug,
    }


@dataclass(frozen=True)
class FamilyExactResult:
    family_flux_fine: np.ndarray
    family_flux_coarse: np.ndarray
    masses_fine: np.ndarray
    masses_coarse: np.ndarray
    family_modes_fine: np.ndarray
    family_hws_fine: np.ndarray
    early_family_fine: str
    late_family_fine: str
    early_family_coarse: str
    late_family_coarse: str
    sep_gate_fine: float
    sep_gate_coarse: float
    peak_windows: List[Tuple[str, int, int]]
    peak_window_frac_fine: Dict[str, np.ndarray]
    peak_window_frac_coarse: Dict[str, np.ndarray]
    closure_max_abs: float
    model: dict


def coarse_from_fine(family_flux_fine: np.ndarray) -> np.ndarray:
    return np.column_stack(
        [
            family_flux_fine[:, 0],
            family_flux_fine[:, 1],
            family_flux_fine[:, 2] + family_flux_fine[:, 3],
            family_flux_fine[:, 4],
        ]
    )


def _family_summary_arrays(flux: np.ndarray, labels: Sequence[str], windows: List[Tuple[str, int, int]]) -> Tuple[np.ndarray, np.ndarray, Dict[str, np.ndarray], int, int, float]:
    masses = flux.sum(axis=0)
    modes = np.asarray([int(np.argmax(flux[:, i])) for i in range(flux.shape[1])], dtype=np.int64)
    hws = np.asarray([half_width_at_half_max(flux[:, i], int(modes[i])) for i in range(flux.shape[1])], dtype=np.float64)
    window_mass: Dict[str, np.ndarray] = {}
    window_frac: Dict[str, np.ndarray] = {}
    for name, lo, hi in windows:
        m = flux[lo : hi + 1].sum(axis=0)
        window_mass[name] = m
        window_frac[name] = m / m.sum() if float(m.sum()) > 0.0 else np.zeros_like(m)
    peak1_key = "peak1" if "peak1" in window_mass else list(window_mass.keys())[0]
    peak2_key = "peak2" if "peak2" in window_mass else list(window_mass.keys())[-1]
    early_idx = int(np.argmax(window_mass[peak1_key]))
    late_idx = int(np.argmax(window_mass[peak2_key]))
    denom = float(hws[early_idx] + hws[late_idx])
    sep_gate = float(abs(int(modes[late_idx]) - int(modes[early_idx])) / denom) if denom > 0.0 else float("nan")
    return masses, modes, window_frac, early_idx, late_idx, sep_gate


def run_family_exact(case: TwoTargetCase, gate: GateConfig, *, t_max: int = 5000, surv_tol: float = 1e-12) -> FamilyExactResult:
    model = build_augmented_gate_model(case, gate)
    p = np.zeros(model["n_aug"], dtype=np.float64)
    p[idx(case.start[0], case.start[1], case.Lx)] = 1.0
    family_flux = [np.zeros(len(FAMILY_LABELS_FINE), dtype=np.float64)]
    for _ in range(1, t_max + 1):
        p_next = np.zeros_like(p)
        np.add.at(p_next, model["dst_aug"], p[model["src_aug"]] * model["prob_aug"])
        f = np.bincount(
            model["abs_family"],
            weights=p[model["abs_src_aug"]] * model["abs_prob"],
            minlength=len(FAMILY_LABELS_FINE),
        )
        family_flux.append(f)
        p = p_next
        if float(p.sum()) < surv_tol:
            break
    family_flux_fine = np.vstack(family_flux)
    family_flux_coarse = coarse_from_fine(family_flux_fine)
    windows = window_ranges(case.t_peak1, case.t_valley, case.t_peak2, len(case.f_total))
    masses_fine, modes_fine, window_frac_fine, early_idx_fine, late_idx_fine, sep_gate_fine = _family_summary_arrays(
        family_flux_fine, FAMILY_LABELS_FINE, windows
    )
    masses_coarse, modes_coarse, window_frac_coarse, early_idx_coarse, late_idx_coarse, sep_gate_coarse = _family_summary_arrays(
        family_flux_coarse, FAMILY_LABELS_COARSE, windows
    )
    closure_max_abs = float(np.max(np.abs(family_flux_fine.sum(axis=1) - case.f_total[: family_flux_fine.shape[0]])))
    family_hws_fine = np.asarray([half_width_at_half_max(family_flux_fine[:, i], int(modes_fine[i])) for i in range(family_flux_fine.shape[1])], dtype=np.float64)
    return FamilyExactResult(
        family_flux_fine=family_flux_fine,
        family_flux_coarse=family_flux_coarse,
        masses_fine=masses_fine,
        masses_coarse=masses_coarse,
        family_modes_fine=modes_fine,
        family_hws_fine=family_hws_fine,
        early_family_fine=FAMILY_LABELS_FINE[early_idx_fine],
        late_family_fine=FAMILY_LABELS_FINE[late_idx_fine],
        early_family_coarse=FAMILY_LABELS_COARSE[early_idx_coarse],
        late_family_coarse=FAMILY_LABELS_COARSE[late_idx_coarse],
        sep_gate_fine=sep_gate_fine,
        sep_gate_coarse=sep_gate_coarse,
        peak_windows=windows,
        peak_window_frac_fine=window_frac_fine,
        peak_window_frac_coarse=window_frac_coarse,
        closure_max_abs=closure_max_abs,
        model=model,
    )


# ----------------------------
# Monte Carlo validation / event times
# ----------------------------


def build_fixed_row_sampler(src_idx: np.ndarray, dst_idx: np.ndarray, probs: np.ndarray, n_states: int) -> Tuple[np.ndarray, np.ndarray]:
    order = np.argsort(src_idx, kind="stable")
    src = src_idx[order]
    dst = dst_idx[order]
    p = probs[order]
    counts = np.bincount(src, minlength=n_states)
    max_deg = int(counts.max())
    row_dst = -np.ones((n_states, max_deg), dtype=np.int32)
    row_prob = np.zeros((n_states, max_deg), dtype=np.float64)
    offsets = np.zeros(n_states + 1, dtype=np.int64)
    offsets[1:] = np.cumsum(counts)
    for i in range(n_states):
        a, b = int(offsets[i]), int(offsets[i + 1])
        d = dst[a:b]
        pr = p[a:b]
        row_dst[i, : len(d)] = d
        row_prob[i, : len(pr)] = pr
    cdf = np.cumsum(row_prob, axis=1)
    cdf[:, -1] = 1.0
    return row_dst, cdf


@dataclass(frozen=True)
class MCSummary:
    family_mass_mc: np.ndarray
    family_mass_exact: np.ndarray
    family_abs_err: np.ndarray
    branch_near_mc: float
    branch_far_mc: float
    branch_near_exact: float
    branch_far_exact: float
    events_rows: List[dict]
    side_rows: List[dict]
    raw: dict


def run_mc(case: TwoTargetCase, gate: GateConfig, *, n_walkers: int = 50000, seed: int = 123, t_max: int = 5000) -> dict:
    n_states = int(case.Lx * case.Wy)
    row_dst, cdf = build_fixed_row_sampler(case.src_idx, case.dst_idx, case.probs, n_states)
    rng = np.random.default_rng(seed)
    start_i = idx(case.start[0], case.start[1], case.Lx)
    near_i = idx(case.near[0], case.near[1], case.Lx)
    far_i = idx(case.far[0], case.far[1], case.Lx)
    xs = np.arange(n_states) % case.Lx
    ys = np.arange(n_states) // case.Lx
    near_ring = (
        (np.abs(xs - case.near[0]) + np.abs(ys - case.near[1]) <= int(gate.near_ring_radius))
        & (np.arange(n_states) != near_i)
        & (np.arange(n_states) != far_i)
    )
    x_out = min(case.Lx - 2, int(case.near[0] + gate.x_out_offset))
    x_in = min(x_out - 1, int(case.near[0] + gate.x_in_offset))
    x_start_progress = x_out + 1
    progress_xs: List[int] = []
    for frac in gate.progress_fracs:
        gx = int(round(x_start_progress + float(frac) * (case.far[0] - x_start_progress)))
        gx = max(x_start_progress, min(case.far[0] - 1, gx))
        if gx not in progress_xs:
            progress_xs.append(gx)
    cur = np.full(n_walkers, start_i, dtype=np.int32)
    active = np.ones(n_walkers, dtype=bool)
    absorb_t = np.full(n_walkers, -1, dtype=np.int32)
    absorb_target = np.full(n_walkers, -1, dtype=np.int8)
    linger = np.zeros(n_walkers, dtype=bool)
    escaped = np.zeros(n_walkers, dtype=bool)
    rollback = np.zeros(n_walkers, dtype=bool)
    first_side = np.full(n_walkers, -1, dtype=np.int8)  # 0 lower, 1 center, 2 upper
    t_escape = np.full(n_walkers, -1, dtype=np.int32)
    t_prog = np.full((len(progress_xs), n_walkers), -1, dtype=np.int32)
    for t in range(1, t_max + 1):
        if not bool(active.any()):
            break
        idx_active = np.nonzero(active)[0]
        states = cur[idx_active]
        u = rng.random(len(idx_active))
        rows_cdf = cdf[states]
        k = (u[:, None] > rows_cdf).sum(axis=1)
        nxt = row_dst[states, k]
        s_x = xs[states]
        d_x = xs[nxt]
        d_y = ys[nxt]
        cross_out = (s_x == x_out) & (d_x == x_out + 1)
        cross_in = (s_x == x_in + 1) & (d_x == x_in)
        for gi, gx in enumerate(progress_xs):
            cross_prog = (s_x == gx) & (d_x == gx + 1)
            mask = cross_prog & (t_prog[gi, idx_active] < 0)
            if bool(mask.any()):
                t_prog[gi, idx_active[mask]] = t
        linger_mask = (~escaped[idx_active]) & near_ring[nxt]
        if bool(linger_mask.any()):
            linger[idx_active[linger_mask]] = True
        esc_mask = cross_out & (~escaped[idx_active])
        if bool(esc_mask.any()):
            esc_idx = idx_active[esc_mask]
            escaped[esc_idx] = True
            t_escape[esc_idx] = t
            y_cross = d_y[esc_mask]
            side = np.where(y_cross > case.near[1], 2, np.where(y_cross < case.near[1], 0, 1))
            fs_mask = first_side[esc_idx] < 0
            if bool(fs_mask.any()):
                first_side[esc_idx[fs_mask]] = side[fs_mask]
        rb_mask = escaped[idx_active] & cross_in
        if bool(rb_mask.any()):
            rollback[idx_active[rb_mask]] = True
        hit_near = nxt == near_i
        hit_far = nxt == far_i
        if bool(hit_near.any()):
            hit_idx = idx_active[hit_near]
            absorb_t[hit_idx] = t
            absorb_target[hit_idx] = 0
            active[hit_idx] = False
        if bool(hit_far.any()):
            hit_idx = idx_active[hit_far]
            absorb_t[hit_idx] = t
            absorb_target[hit_idx] = 1
            active[hit_idx] = False
        cur[idx_active] = nxt
    family = np.full(n_walkers, -1, dtype=np.int8)
    near_mask = absorb_target == 0
    far_mask = absorb_target == 1
    family[near_mask & (~escaped)] = 0
    family[near_mask & escaped] = 1
    family[far_mask & rollback] = 4
    family[far_mask & (~rollback) & linger] = 3
    family[far_mask & (~rollback) & (~linger)] = 2
    return {
        "absorb_t": absorb_t,
        "absorb_target": absorb_target,
        "family": family,
        "linger": linger,
        "escaped": escaped,
        "rollback": rollback,
        "first_side": first_side,
        "t_escape": t_escape,
        "t_prog": t_prog,
        "progress_xs": progress_xs,
        "x_out": x_out,
        "x_in": x_in,
        "near_ring_radius": gate.near_ring_radius,
    }


def summarize_mc(case: TwoTargetCase, exact_result: FamilyExactResult, mc_raw: dict) -> MCSummary:
    fam_mass_mc = np.asarray([float(np.mean(mc_raw["family"] == i)) for i in range(len(FAMILY_LABELS_FINE))], dtype=np.float64)
    fam_mass_exact = exact_result.masses_fine.astype(np.float64, copy=True)
    fam_abs_err = np.abs(fam_mass_mc - fam_mass_exact)
    rows: List[dict] = []
    for i, lab in enumerate(FAMILY_LABELS_FINE):
        mask = mc_raw["family"] == i
        if int(mask.sum()) == 0:
            continue
        row = {
            "family": lab,
            "n": int(mask.sum()),
            "mass_mc": float(np.mean(mask)),
            "mass_exact": float(fam_mass_exact[i]),
            "abs_err": float(fam_abs_err[i]),
        }
        esc = mc_raw["t_escape"][mask]
        row["t_escape_med"] = float(np.median(esc[esc > 0])) if bool(np.any(esc > 0)) else None
        hit = mc_raw["absorb_t"][mask]
        row["t_hit_med"] = float(np.median(hit[hit > 0])) if bool(np.any(hit > 0)) else None
        for gi, gx in enumerate(mc_raw["progress_xs"]):
            tp = mc_raw["t_prog"][gi, mask]
            row[f"t_x{gx}_med"] = float(np.median(tp[tp > 0])) if bool(np.any(tp > 0)) else None
        rows.append(row)
    side_rows: List[dict] = []
    for i, lab in enumerate(FAMILY_LABELS_FINE):
        mask = mc_raw["family"] == i
        side = mc_raw["first_side"][mask]
        valid = side >= 0
        if int(valid.sum()) == 0:
            continue
        side_rows.append(
            {
                "family": lab,
                "lower": float(np.mean(side[valid] == 0)),
                "center": float(np.mean(side[valid] == 1)),
                "upper": float(np.mean(side[valid] == 2)),
            }
        )
    branch_near_mc = float(np.mean(mc_raw["absorb_target"] == 0))
    branch_far_mc = float(np.mean(mc_raw["absorb_target"] == 1))
    return MCSummary(
        family_mass_mc=fam_mass_mc,
        family_mass_exact=fam_mass_exact,
        family_abs_err=fam_abs_err,
        branch_near_mc=branch_near_mc,
        branch_far_mc=branch_far_mc,
        branch_near_exact=float(case.p_near),
        branch_far_exact=float(case.p_far),
        events_rows=rows,
        side_rows=side_rows,
        raw=mc_raw,
    )


# ----------------------------
# Scan helpers
# ----------------------------


def run_scan_over_dy(*, d: int, dy_vals: Iterable[int], bx: float, gate: GateConfig) -> List[dict]:
    rows: List[dict] = []
    for dy in dy_vals:
        case = build_case(name=f"d{d}_dy{dy}_bx{bx:+.2f}", near_dx=d, near_dy=int(dy), bx=bx)
        exact = run_family_exact(case, gate, t_max=len(case.f_total) - 1)
        rows.append(
            {
                "dy": int(dy),
                "phase": int(case.phase),
                "p_near": float(case.p_near),
                "p_far": float(case.p_far),
                "sep_mode": float(case.sep_mode),
                "N_direct": float(exact.masses_coarse[0]),
                "N_detour": float(exact.masses_coarse[1]),
                "F_no_return": float(exact.masses_coarse[2]),
                "F_rollback": float(exact.masses_coarse[3]),
                "early_family": exact.early_family_coarse,
                "late_family": exact.late_family_coarse,
                "sep_gate": float(exact.sep_gate_coarse),
                "peak2_no_return_frac": float(exact.peak_window_frac_coarse[exact.peak_windows[-1][0]][2]),
            }
        )
    return rows


def run_scan_over_d(*, d_vals: Iterable[int], dy: int, bx: float, gate: GateConfig) -> List[dict]:
    rows: List[dict] = []
    for d in d_vals:
        case = build_case(name=f"d{d}_dy{dy}_bx{bx:+.2f}", near_dx=int(d), near_dy=dy, bx=bx)
        exact = run_family_exact(case, gate, t_max=len(case.f_total) - 1)
        rows.append(
            {
                "d": int(d),
                "phase": int(case.phase),
                "p_near": float(case.p_near),
                "p_far": float(case.p_far),
                "sep_mode": float(case.sep_mode),
                "N_direct": float(exact.masses_coarse[0]),
                "N_detour": float(exact.masses_coarse[1]),
                "F_no_return": float(exact.masses_coarse[2]),
                "F_rollback": float(exact.masses_coarse[3]),
                "early_family": exact.early_family_coarse,
                "late_family": exact.late_family_coarse,
                "sep_gate": float(exact.sep_gate_coarse),
                "peak2_no_return_frac": float(exact.peak_window_frac_coarse[exact.peak_windows[-1][0]][2]),
            }
        )
    return rows


def run_gate_robustness(case: TwoTargetCase, *, ring_vals: Sequence[int], out_offsets: Sequence[int]) -> List[dict]:
    rows: List[dict] = []
    for r in ring_vals:
        for off in out_offsets:
            gate = GateConfig(near_ring_radius=int(r), x_out_offset=int(off), x_in_offset=0)
            exact = run_family_exact(case, gate, t_max=len(case.f_total) - 1)
            rows.append(
                {
                    "near_ring_radius": int(r),
                    "x_out_offset": int(off),
                    "early_family_fine": exact.early_family_fine,
                    "late_family_fine": exact.late_family_fine,
                    "early_family_coarse": exact.early_family_coarse,
                    "late_family_coarse": exact.late_family_coarse,
                    "sep_gate_coarse": float(exact.sep_gate_coarse),
                    "peak2_F_no_return_frac": float(exact.peak_window_frac_coarse[exact.peak_windows[-1][0]][2]),
                    "mass_F_rollback": float(exact.masses_coarse[3]),
                    "mass_F_no_return": float(exact.masses_coarse[2]),
                }
            )
    return rows


# ----------------------------
# Plotting helpers
# ----------------------------

PALETTE_FINE = {
    "N_direct": "#c62828",
    "N_detour": "#ef6c00",
    "F_clean": "#1f77b4",
    "F_linger": "#26a69a",
    "F_rollback": "#6a1b9a",
}

PALETTE_COARSE = {
    "N_direct": "#c62828",
    "N_detour": "#ef6c00",
    "F_no_return": "#1f77b4",
    "F_rollback": "#6a1b9a",
}


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def save_fig(fig: plt.Figure, out_path: Path) -> None:
    ensure_dir(out_path.parent)
    fig.savefig(out_path, dpi=220, bbox_inches="tight", pad_inches=0.03)
    if out_path.suffix.lower() == ".pdf":
        fig.savefig(out_path.with_suffix(".png"), dpi=220, bbox_inches="tight", pad_inches=0.03)
    plt.close(fig)


def _column_array(rows: Sequence[dict], key: str, *, dtype: type = float) -> np.ndarray:
    return np.asarray([dtype(row[key]) for row in rows], dtype=dtype)


def _row_lookup(rows: Sequence[dict], **match: int) -> dict:
    for row in rows:
        if all(int(row[key]) == int(value) for key, value in match.items()):
            return row
    raise KeyError(f"missing row for match={match}")


def plot_geometry_with_gates(case: TwoTargetCase, exact_result: FamilyExactResult, out_path: Path) -> None:
    q_info = committor_diagnostics(case)
    q_far = q_info["q_far"].reshape(case.Wy, case.Lx)
    fig, ax = plt.subplots(figsize=(10.2, 4.4))
    im = ax.imshow(q_far, origin="lower", cmap="viridis", aspect="auto", extent=(-0.5, case.Lx - 0.5, -0.5, case.Wy - 0.5))
    # grid
    for x in range(case.Lx + 1):
        ax.plot([x - 0.5, x - 0.5], [-0.5, case.Wy - 0.5], color="white", lw=0.18, alpha=0.45, zorder=1)
    for y in range(case.Wy + 1):
        ax.plot([-0.5, case.Lx - 0.5], [y - 0.5, y - 0.5], color="white", lw=0.18, alpha=0.45, zorder=1)
    near_ring = exact_result.model["near_ring"].reshape(case.Wy, case.Lx)
    ys, xs = np.where(near_ring)
    ax.scatter(xs, ys, s=12, marker="s", facecolors="none", edgecolors="#ffcc80", linewidths=0.6, label="near ring", zorder=3)
    x_in = exact_result.model["x_in"]
    x_out = exact_result.model["x_out"]
    ax.plot([x_in + 0.5, x_in + 0.5], [-0.5, case.Wy - 0.5], color="#ef6c00", lw=1.4, ls="--", zorder=4, label="rollback gate")
    ax.plot([x_out + 0.5, x_out + 0.5], [-0.5, case.Wy - 0.5], color="#1f77b4", lw=1.4, ls="--", zorder=4, label="escape gate")
    for gx in exact_result.model["progress_xs"]:
        ax.plot([gx + 0.5, gx + 0.5], [-0.5, case.Wy - 0.5], color="#90caf9", lw=1.0, ls=":", zorder=3)
    ax.scatter([case.start[0]], [case.start[1]], s=62, marker="s", color="#e53935", zorder=5)
    ax.scatter([case.near[0]], [case.near[1]], s=72, marker="o", color="#fb8c00", zorder=5)
    ax.scatter([case.far[0]], [case.far[1]], s=78, marker="D", color="#1565c0", zorder=5)
    ax.annotate("start", xy=case.start, xytext=(case.start[0] - 2.0, case.start[1] + 2.0), fontsize=8, color="white", arrowprops=dict(arrowstyle="-|>", color="white", lw=0.8))
    ax.annotate("near", xy=case.near, xytext=(case.near[0] - 1.6, case.near[1] + 2.2), fontsize=8, color="white", arrowprops=dict(arrowstyle="-|>", color="white", lw=0.8))
    ax.annotate("far", xy=case.far, xytext=(case.far[0] - 3.0, case.far[1] + 2.0), fontsize=8, color="white", arrowprops=dict(arrowstyle="-|>", color="white", lw=0.8))
    ax.set_title(f"{case.name}: q_far field + gate ladder")
    ax.set_xlim(-0.5, case.Lx - 0.5)
    ax.set_ylim(-0.5, case.Wy - 0.5)
    ax.set_aspect("equal")
    ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label("q_far(x)")
    ax.legend(loc="upper center", ncol=3, fontsize=8, frameon=True)
    save_fig(fig, out_path)


def plot_branch_fpt(case: TwoTargetCase, out_path: Path) -> None:
    t = np.arange(len(case.f_total))
    fs = smooth_series_display(case.f_total, window=7)
    fn = smooth_series_display(case.f_near, window=7)
    ff = smooth_series_display(case.f_far, window=7)
    fig, axes = plt.subplots(1, 2, figsize=(11.0, 4.4), sharex=True)
    for ax, use_log in zip(axes, [False, True]):
        if use_log:
            ax.semilogy(t, np.maximum(fs, 1e-15), color="#111111", lw=1.8, label="total")
            ax.semilogy(t, np.maximum(fn, 1e-15), color="#c62828", lw=1.4, label="near target")
            ax.semilogy(t, np.maximum(ff, 1e-15), color="#1565c0", lw=1.4, label="far target")
            ax.set_ylabel("pmf (log)")
            ax.set_ylim(1e-6, max(1e-2, 1.6 * float(max(fs.max(), fn.max(), ff.max()))))
        else:
            ax.plot(t, fs, color="#111111", lw=1.8, label="total")
            ax.plot(t, fn, color="#c62828", lw=1.4, label="near target")
            ax.plot(t, ff, color="#1565c0", lw=1.4, label="far target")
            ax.set_ylabel("pmf")
        ax.set_xlabel("t")
        ax.grid(alpha=0.22)
        for label, x, color, ls in [("p1", case.t_peak1, "#c62828", "--"), ("valley", case.t_valley, "#666666", ":"), ("p2", case.t_peak2, "#1565c0", "--")]:
            if x is None:
                continue
            ax.axvline(int(x), color=color, ls=ls, lw=1.0, alpha=0.8)
        for w_name, lo, hi in window_ranges(case.t_peak1, case.t_valley, case.t_peak2, len(case.f_total)):
            shade = "#fde0dc" if w_name == "peak1" else ("#eceff1" if w_name == "valley" else "#e3f2fd")
            ax.axvspan(lo, hi, color=shade, alpha=0.25, lw=0)
    axes[0].set_title(f"{case.name}: total / near / far")
    axes[1].set_title("same case on log scale")
    axes[0].text(
        0.02,
        0.97,
        "\n".join(
            [
                f"phase={case.phase}",
                f"sep_mode={case.sep_mode:.2f}",
                f"P_near={case.p_near:.3f}",
                f"P_far={case.p_far:.3f}",
                f"valley/max={case.valley_over_max:.3f}" if case.valley_over_max is not None else "valley/max=-",
                f"peak_ratio={case.peak_ratio:.3f}" if case.peak_ratio is not None else "peak_ratio=-",
            ]
        ),
        transform=axes[0].transAxes,
        ha="left",
        va="top",
        fontsize=8,
        bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="#666666", lw=0.7, alpha=0.95),
    )
    handles, labels = axes[1].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", bbox_to_anchor=(0.5, 1.03), ncol=3, fontsize=8)
    fig.tight_layout(rect=(0, 0, 1, 0.98))
    save_fig(fig, out_path)


def plot_family_fpt(case: TwoTargetCase, exact_result: FamilyExactResult, out_path: Path, *, coarse: bool = True) -> None:
    t = np.arange(exact_result.family_flux_coarse.shape[0] if coarse else exact_result.family_flux_fine.shape[0])
    flux = exact_result.family_flux_coarse if coarse else exact_result.family_flux_fine
    labels = FAMILY_LABELS_COARSE if coarse else FAMILY_LABELS_FINE
    palette = PALETTE_COARSE if coarse else PALETTE_FINE
    fig, axes = plt.subplots(1, 2, figsize=(11.0, 4.4), sharex=True)
    for ax, use_log in zip(axes, [False, True]):
        y_total = smooth_series_display(case.f_total[: len(t)], window=7)
        if use_log:
            ax.semilogy(t, np.maximum(y_total, 1e-15), color="#111111", lw=1.6, label="total")
        else:
            ax.plot(t, y_total, color="#111111", lw=1.6, label="total")
        for i, lab in enumerate(labels):
            ys = smooth_series_display(flux[:, i], window=5)
            if use_log:
                ax.semilogy(t, np.maximum(ys, 1e-15), color=palette[lab], lw=1.2, label=lab)
            else:
                ax.plot(t, ys, color=palette[lab], lw=1.2, label=lab)
        for w_name, lo, hi in exact_result.peak_windows:
            shade = "#fde0dc" if w_name == "peak1" else ("#eceff1" if w_name == "valley" else "#e3f2fd")
            ax.axvspan(lo, hi, color=shade, alpha=0.22, lw=0)
        ax.grid(alpha=0.22)
        ax.set_xlabel("t")
        ax.set_ylabel("family pmf" if not use_log else "family pmf (log)")
    axes[0].set_title(f"{case.name}: {'coarse' if coarse else 'fine'} gate families")
    axes[1].set_title("same case on log scale")
    handles, labels_ = axes[1].get_legend_handles_labels()
    fig.legend(handles, labels_, loc="upper center", bbox_to_anchor=(0.5, 1.06), ncol=3 if len(labels_) <= 6 else 4, fontsize=8)
    fig.tight_layout(rect=(0, 0, 1, 0.98))
    save_fig(fig, out_path)


def plot_window_composition(case: TwoTargetCase, exact_result: FamilyExactResult, out_path: Path) -> None:
    win_names = [w[0] for w in exact_result.peak_windows]
    fig, axes = plt.subplots(1, 2, figsize=(11.2, 4.4))
    # coarse
    bottom = np.zeros(len(win_names), dtype=np.float64)
    x = np.arange(len(win_names), dtype=np.int64)
    for i, lab in enumerate(FAMILY_LABELS_COARSE):
        vals = np.asarray([exact_result.peak_window_frac_coarse[n][i] for n in win_names], dtype=np.float64)
        axes[0].bar(x, vals, bottom=bottom, color=PALETTE_COARSE[lab], label=lab)
        bottom += vals
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(win_names)
    axes[0].set_ylim(0, 1.0)
    axes[0].set_title("Coarse 4-family composition")
    axes[0].set_ylabel("fraction")
    # fine
    bottom = np.zeros(len(win_names), dtype=np.float64)
    for i, lab in enumerate(FAMILY_LABELS_FINE):
        vals = np.asarray([exact_result.peak_window_frac_fine[n][i] for n in win_names], dtype=np.float64)
        axes[1].bar(x, vals, bottom=bottom, color=PALETTE_FINE[lab], label=lab)
        bottom += vals
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(win_names)
    axes[1].set_ylim(0, 1.0)
    axes[1].set_title("Fine 5-family composition")
    axes[1].set_ylabel("fraction")
    for ax in axes:
        ax.grid(axis="y", alpha=0.22)
    axes[0].legend(loc="upper center", bbox_to_anchor=(0.5, 1.18), ncol=2, fontsize=8, frameon=False)
    axes[1].legend(loc="upper center", bbox_to_anchor=(0.5, 1.18), ncol=3, fontsize=8, frameon=False)
    fig.suptitle(f"{case.name}: which families populate peak1 / valley / peak2?", fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    save_fig(fig, out_path)


def plot_side_usage(case: TwoTargetCase, mc_summary: MCSummary, out_path: Path) -> None:
    rows = list(mc_summary.side_rows)
    if not rows:
        return
    fig, ax = plt.subplots(figsize=(7.8, 3.8))
    y = np.arange(len(rows))
    lower = _column_array(rows, "lower")
    center = _column_array(rows, "center")
    upper = _column_array(rows, "upper")
    ax.barh(y, lower, color="#42a5f5", label="lower side")
    ax.barh(y, center, left=lower, color="#b0bec5", label="center")
    ax.barh(y, upper, left=lower + center, color="#ffb74d", label="upper side")
    ax.set_yticks(y)
    ax.set_yticklabels([str(row["family"]) for row in rows])
    ax.set_xlim(0, 1.0)
    ax.set_xlabel("fraction at first escape crossing")
    ax.set_title(f"{case.name}: upper/lower side choice at the escape gate (MC)")
    ax.grid(axis="x", alpha=0.22)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.18), ncol=3, fontsize=8, frameon=False)
    fig.tight_layout()
    save_fig(fig, out_path)


def plot_mc_vs_exact(case_summaries: Sequence[Tuple[TwoTargetCase, MCSummary]], out_path: Path) -> None:
    fig, axes = plt.subplots(1, len(case_summaries), figsize=(4.2 * len(case_summaries), 4.2), sharey=True)
    if len(case_summaries) == 1:
        axes = [axes]
    for ax, (case, mc_summary) in zip(axes, case_summaries):
        x = np.arange(len(FAMILY_LABELS_FINE))
        w = 0.38
        ax.bar(x - w / 2, mc_summary.family_mass_exact, width=w, color="#90caf9", label="exact")
        ax.bar(x + w / 2, mc_summary.family_mass_mc, width=w, color="#ef9a9a", label="MC")
        ax.set_xticks(x)
        ax.set_xticklabels(FAMILY_LABELS_FINE, rotation=30, ha="right")
        ax.set_title(case.name)
        ax.grid(axis="y", alpha=0.22)
    axes[0].set_ylabel("family mass")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", bbox_to_anchor=(0.5, 1.08), ncol=2, frameon=False)
    fig.suptitle("Exact vs MC family masses", fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    save_fig(fig, out_path)


def plot_scan_family_lines(rows: Sequence[dict], *, x_col: str, title: str, out_path: Path) -> None:
    fig, axes = plt.subplots(2, 1, figsize=(9.0, 6.2), sharex=True)
    x = _column_array(rows, x_col, dtype=float)
    axes[0].plot(x, _column_array(rows, "p_near"), marker="o", lw=1.8, color="#c62828", label="P_near")
    axes[0].plot(x, _column_array(rows, "p_far"), marker="o", lw=1.8, color="#1565c0", label="P_far")
    axes[0].plot(x, _column_array(rows, "sep_mode"), marker="s", lw=1.5, color="#455a64", label="sep_mode")
    axes[0].grid(alpha=0.22)
    axes[0].legend(loc="best", fontsize=8)
    axes[0].set_ylabel("branch metric")
    axes[1].plot(x, _column_array(rows, "N_direct"), marker="o", lw=1.6, color=PALETTE_COARSE["N_direct"], label="N_direct")
    axes[1].plot(x, _column_array(rows, "N_detour"), marker="o", lw=1.6, color=PALETTE_COARSE["N_detour"], label="N_detour")
    axes[1].plot(x, _column_array(rows, "F_no_return"), marker="o", lw=1.6, color=PALETTE_COARSE["F_no_return"], label="F_no_return")
    axes[1].plot(x, _column_array(rows, "F_rollback"), marker="o", lw=1.6, color=PALETTE_COARSE["F_rollback"], label="F_rollback")
    for xv, ph in zip(x, _column_array(rows, "phase", dtype=int)):
        axes[1].text(xv, 1.02, f"phase={int(ph)}", fontsize=7, rotation=0, ha="center", va="bottom")
    axes[1].set_ylim(0, 1.08)
    axes[1].grid(alpha=0.22)
    axes[1].legend(loc="best", fontsize=8, ncol=2)
    axes[1].set_xlabel(x_col)
    axes[1].set_ylabel("coarse family mass")
    fig.suptitle(title, fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    save_fig(fig, out_path)


def plot_robustness_heatmap(rows: Sequence[dict], out_path: Path) -> None:
    ring_vals = sorted({int(row["near_ring_radius"]) for row in rows})
    off_vals = sorted({int(row["x_out_offset"]) for row in rows})
    mat = np.zeros((len(ring_vals), len(off_vals)), dtype=float)
    for i, r in enumerate(ring_vals):
        for j, off in enumerate(off_vals):
            row = _row_lookup(rows, near_ring_radius=r, x_out_offset=off)
            mat[i, j] = float(row["peak2_F_no_return_frac"])
    fig, ax = plt.subplots(figsize=(6.0, 4.0))
    im = ax.imshow(mat, origin="lower", cmap="Blues", vmin=0.0, vmax=1.0, aspect="auto")
    ax.set_xticks(np.arange(len(off_vals)))
    ax.set_xticklabels([str(v) for v in off_vals])
    ax.set_yticks(np.arange(len(ring_vals)))
    ax.set_yticklabels([str(v) for v in ring_vals])
    ax.set_xlabel("x_out_offset")
    ax.set_ylabel("near_ring_radius")
    ax.set_title("Anchor robustness: peak2 F_no_return fraction")
    for i in range(len(ring_vals)):
        for j in range(len(off_vals)):
            row = _row_lookup(rows, near_ring_radius=ring_vals[i], x_out_offset=off_vals[j])
            ax.text(j, i, f"{mat[i,j]:.2f}\n{row['late_family_fine']}", ha="center", va="center", fontsize=7, color="black")
    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label("peak2 fraction from F_no_return")
    fig.tight_layout()
    save_fig(fig, out_path)


# ----------------------------
# Export helpers
# ----------------------------


def case_metrics_dict(case: TwoTargetCase, exact_result: FamilyExactResult, mc_summary: MCSummary | None = None) -> dict:
    payload = {
        "name": case.name,
        "near_dx": int(case.near_dx),
        "near_dy": int(case.near_dy),
        "bx": float(case.bx),
        "phase": int(case.phase),
        "t_peak1": None if case.t_peak1 is None else int(case.t_peak1),
        "t_valley": None if case.t_valley is None else int(case.t_valley),
        "t_peak2": None if case.t_peak2 is None else int(case.t_peak2),
        "p_near": float(case.p_near),
        "p_far": float(case.p_far),
        "sep_mode": float(case.sep_mode),
        "valley_over_max": None if case.valley_over_max is None else float(case.valley_over_max),
        "peak_ratio": None if case.peak_ratio is None else float(case.peak_ratio),
        "early_family_fine": exact_result.early_family_fine,
        "late_family_fine": exact_result.late_family_fine,
        "early_family_coarse": exact_result.early_family_coarse,
        "late_family_coarse": exact_result.late_family_coarse,
        "sep_gate_fine": float(exact_result.sep_gate_fine),
        "sep_gate_coarse": float(exact_result.sep_gate_coarse),
        "closure_max_abs": float(exact_result.closure_max_abs),
    }
    for i, lab in enumerate(FAMILY_LABELS_FINE):
        payload[f"mass_{lab}"] = float(exact_result.masses_fine[i])
    for i, lab in enumerate(FAMILY_LABELS_COARSE):
        payload[f"mass_{lab}"] = float(exact_result.masses_coarse[i])
    if mc_summary is not None:
        payload.update(
            {
                "mc_branch_near": float(mc_summary.branch_near_mc),
                "mc_branch_far": float(mc_summary.branch_far_mc),
                "mc_max_family_abs_err": float(np.max(mc_summary.family_abs_err)),
            }
        )
    return payload


def save_case_timeseries(case: TwoTargetCase, exact_result: FamilyExactResult, out_path: Path) -> None:
    ensure_dir(out_path.parent)
    fieldnames = [
        "t",
        "f_total",
        "f_near",
        "f_far",
        "N_direct",
        "N_detour",
        "F_clean",
        "F_linger",
        "F_rollback",
        "F_no_return",
    ]
    with out_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for t in range(len(case.f_total)):
            writer.writerow(
                {
                    "t": int(t),
                    "f_total": float(case.f_total[t]),
                    "f_near": float(case.f_near[t]),
                    "f_far": float(case.f_far[t]),
                    "N_direct": float(exact_result.family_flux_fine[t, 0]),
                    "N_detour": float(exact_result.family_flux_fine[t, 1]),
                    "F_clean": float(exact_result.family_flux_fine[t, 2]),
                    "F_linger": float(exact_result.family_flux_fine[t, 3]),
                    "F_rollback": float(exact_result.family_flux_fine[t, 4]),
                    "F_no_return": float(exact_result.family_flux_coarse[t, 2]),
                }
            )
