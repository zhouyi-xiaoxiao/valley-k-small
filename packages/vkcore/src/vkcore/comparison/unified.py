from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

import numpy as np

ROOT = Path(__file__).resolve().parents[5]
_BIMOD_CODE = ROOT / "research" / "reports" / "grid2d_bimodality" / "code"
if str(_BIMOD_CODE) not in sys.path:
    sys.path.insert(0, str(_BIMOD_CODE))

from fpt_aw_inversion import fpt_pmf_aw  # type: ignore  # noqa: E402
from fpt_exact_mc import exact_fpt  # type: ignore  # noqa: E402
from heterogeneity_determinant import DefectSystem, defect_pairs_from_config  # type: ignore  # noqa: E402
from model_core import ConfigSpec, LatticeConfig, edge_key, spec_to_internal  # type: ignore  # noqa: E402
from propagator_z_analytic import defect_free_propagator_from_config  # type: ignore  # noqa: E402

Coord = Tuple[int, int]

DIR_VEC = {
    "E": (1, 0),
    "W": (-1, 0),
    "N": (0, 1),
    "S": (0, -1),
}

COLOR_START = "#d62839"
COLOR_TARGET = "#1d4ed8"
COLOR_TARGET_ALT = "#0f172a"
COLOR_SHORTCUT = "#7c3aed"
COLOR_BIAS = "#fb8500"
COLOR_DEFECT = "#3b82f6"
COLOR_STICKY = "#06b6d4"
COLOR_BARRIER = "#ef4444"
COLOR_TEXT = "#1f2937"
COLOR_GRID = "#d4d4d8"
COLOR_DIAG = "#dbeafe"
COLOR_CARD = "#f8fafc"
COLOR_RING = "#94a3b8"


def to0(c: Coord) -> Coord:
    return (c[0] - 1, c[1] - 1)


def step_dir(a: Coord, b: Coord) -> str:
    dx = b[0] - a[0]
    dy = b[1] - a[1]
    if dx == 1 and dy == 0:
        return "E"
    if dx == -1 and dy == 0:
        return "W"
    if dx == 0 and dy == 1:
        return "N"
    if dx == 0 and dy == -1:
        return "S"
    raise ValueError(f"non-axis step: {a} -> {b}")


def segment_points(a: Coord, b: Coord) -> List[Coord]:
    if a[0] != b[0] and a[1] != b[1]:
        raise ValueError("segment must be axis-aligned")
    points: List[Coord] = []
    if a[0] == b[0]:
        y0, y1 = sorted((a[1], b[1]))
        for y in range(y0, y1 + 1):
            points.append((a[0], y))
        if b[1] < a[1]:
            points.reverse()
        return points
    x0, x1 = sorted((a[0], b[0]))
    for x in range(x0, x1 + 1):
        points.append((x, a[1]))
    if b[0] < a[0]:
        points.reverse()
    return points


def polyline_points(nodes: Sequence[Coord]) -> List[Coord]:
    if len(nodes) < 2:
        raise ValueError("polyline needs >= 2 nodes")
    out: List[Coord] = []
    for i in range(len(nodes) - 1):
        seg = segment_points(nodes[i], nodes[i + 1])
        if i > 0:
            seg = seg[1:]
        out.extend(seg)
    return out


def corridor_assignments(
    path_points: Sequence[Coord],
    *,
    width: int,
    skip: int,
    N: int,
) -> Tuple[Dict[Coord, str], set[Coord]]:
    arrows: Dict[Coord, str] = {}
    cells: set[Coord] = set()
    for i in range(skip, len(path_points) - 1):
        c = path_points[i]
        d = step_dir(path_points[i], path_points[i + 1])
        for dx in range(-width, width + 1):
            for dy in range(-width, width + 1):
                if abs(dx) + abs(dy) > width:
                    continue
                x = c[0] + dx
                y = c[1] + dy
                if 0 <= x < N and 0 <= y < N:
                    arrows[(x, y)] = d
                    cells.add((x, y))
    return arrows, cells


def build_case_layout(
    *,
    N: int,
    fast_path: Sequence[Coord],
    slow_path: Sequence[Coord],
    w1: int,
    w2: int,
    skip2: int,
) -> Tuple[Dict[Coord, str], set[Coord], set[Coord]]:
    fast_arrows, fast_cells = corridor_assignments(fast_path, width=w1, skip=0, N=N)
    slow_arrows, slow_cells = corridor_assignments(slow_path, width=w2, skip=skip2, N=N)
    arrow_map = dict(fast_arrows)
    arrow_map.update(slow_arrows)
    return arrow_map, fast_cells, slow_cells


def build_two_target_transition_arrays(
    *,
    N: int,
    q: float,
    delta: float,
    arrow_map: Dict[Coord, str],
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    p_step = q / 4.0
    p_stay0 = 1.0 - q
    src: List[int] = []
    dst: List[int] = []
    prob: List[float] = []

    def idx(x: int, y: int) -> int:
        return y * N + x

    for y in range(N):
        for x in range(N):
            moves = {"E": p_step, "W": p_step, "N": p_step, "S": p_step}
            p_stay = p_stay0
            arrow = arrow_map.get((x, y))
            if arrow is not None and p_stay > 0.0:
                shift = delta * p_stay
                p_stay -= shift
                moves[arrow] += shift

            out: Dict[int, float] = {}
            stay_extra = p_stay
            for d, p in moves.items():
                dx, dy = DIR_VEC[d]
                nx = x + dx
                ny = y + dy
                if nx < 0 or nx >= N or ny < 0 or ny >= N:
                    stay_extra += p
                    continue
                j = idx(nx, ny)
                out[j] = out.get(j, 0.0) + p
            j_self = idx(x, y)
            out[j_self] = out.get(j_self, 0.0) + stay_extra
            i = idx(x, y)
            for j, p in out.items():
                src.append(i)
                dst.append(j)
                prob.append(p)

    return (
        np.asarray(src, dtype=np.int64),
        np.asarray(dst, dtype=np.int64),
        np.asarray(prob, dtype=np.float64),
    )


def run_exact_two_target(
    *,
    N: int,
    start: Coord,
    target1: Coord,
    target2: Coord,
    src_idx: np.ndarray,
    dst_idx: np.ndarray,
    probs: np.ndarray,
    t_max: int,
    surv_tol: float,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    n_states = N * N

    def idx(xy: Coord) -> int:
        return xy[1] * N + xy[0]

    i_start = idx(start)
    i_m1 = idx(target1)
    i_m2 = idx(target2)

    p = np.zeros(n_states, dtype=np.float64)
    p[i_start] = 1.0

    f_any = [0.0]
    f_m1 = [0.0]
    f_m2 = [0.0]
    surv = [1.0]

    for _ in range(1, t_max + 1):
        p_next = np.zeros_like(p)
        np.add.at(p_next, dst_idx, p[src_idx] * probs)
        hit1 = float(p_next[i_m1])
        hit2 = float(p_next[i_m2])
        p_next[i_m1] = 0.0
        p_next[i_m2] = 0.0
        s = float(p_next.sum())
        f_any.append(hit1 + hit2)
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


def build_c1_geometry(*, N: int = 31) -> Tuple[Coord, Coord, Coord, Dict[Coord, str], float]:
    start = to0((15, 15))
    m1 = to0((22, 15))
    m2 = to0((7, 7))
    fast_nodes = [to0((15, 15)), to0((22, 15))]
    slow_nodes = [to0((15, 15)), to0((15, 27)), to0((3, 27)), to0((3, 7)), to0((7, 7))]
    fast_path = polyline_points(fast_nodes)
    slow_path = polyline_points(slow_nodes)
    arrow_map, _fast_cells, _slow_cells = build_case_layout(
        N=N,
        fast_path=fast_path,
        slow_path=slow_path,
        w1=1,
        w2=3,
        skip2=2,
    )
    return start, m1, m2, arrow_map, 0.2


def build_luca_fast_geometry(N: int) -> Tuple[Coord, Coord, Coord, Dict[Coord, str], float, float]:
    if N < 21:
        raise ValueError("N must be >= 21 for the default geometry.")
    q = 0.2
    delta = 0.2
    start = (N // 2, N // 2)
    m1 = (N // 2 + 8, N // 2)
    m2 = (N // 2 - 8, N // 2 - 8)
    arrow_map = {(start[0], start[1] - 1): "E"}
    return start, m1, m2, arrow_map, q, delta


def run_two_target_defect_reduced_aw(
    *,
    N: int,
    q: float,
    start: Coord,
    m1: Coord,
    m2: Coord,
    arrow_map: Dict[Coord, str],
    delta: float,
    t_max_aw: int,
    oversample: int,
    r_pow10: float,
) -> Dict[str, object]:
    map_dir = {"E": "right", "W": "left", "N": "down", "S": "up"}
    local_bias_arrows = {xy: map_dir[d] for xy, d in arrow_map.items()}

    cfg = LatticeConfig(
        N=N,
        q=q,
        g_x=0.0,
        g_y=0.0,
        boundary_x="reflecting",
        boundary_y="reflecting",
        start=start,
        target=m1,
        local_bias_arrows=local_bias_arrows,
        local_bias_delta=float(delta),
        sticky_sites={},
        barriers_reflect=set(),
        barriers_perm={},
    )

    base = defect_free_propagator_from_config(cfg)
    defects = defect_pairs_from_config(cfg)
    nodes = {start, m1, m2}
    for d in defects:
        nodes.add(d.u)
        nodes.add(d.v)
    nodes_list = sorted(nodes)
    node_index = {n: i for i, n in enumerate(nodes_list)}

    pair_eval = base.prepare_pair_evaluator(nodes_list, nodes_list)
    U = np.array([node_index[d.u] for d in defects], dtype=np.int64)
    V = np.array([node_index[d.v] for d in defects], dtype=np.int64)
    delta_vec = np.array([-d.eta_uv for d in defects], dtype=np.complex128)

    src_idx = np.array([node_index[start], node_index[m1], node_index[m2]], dtype=np.int64)
    dst_idx = np.array([node_index[m1], node_index[m2]], dtype=np.int64)

    m = 1 << (int(oversample * (t_max_aw + 1)) - 1).bit_length()
    r = float(10.0 ** (-float(r_pow10) / float(m)))
    k = np.arange(m, dtype=np.float64)
    z = r * np.exp(1j * 2.0 * np.pi * k / float(m))

    F1 = np.zeros(m, dtype=np.complex128)
    F2 = np.zeros(m, dtype=np.complex128)
    eye = np.eye(len(defects), dtype=np.complex128) if defects else np.zeros((0, 0), dtype=np.complex128)

    for i, zi in enumerate(z):
        P = pair_eval.evaluate(zi)
        if defects:
            P_vu = P[np.ix_(V, U)]
            A = eye - zi * (P_vu * delta_vec[None, :])
            B = P[np.ix_(V, dst_idx)]
            try:
                X = np.linalg.solve(A, B)
            except np.linalg.LinAlgError:
                X = np.linalg.solve(A + 1e-12 * eye, B)
            P_su = P[np.ix_(src_idx, U)]
            ST = P[np.ix_(src_idx, dst_idx)] + zi * ((P_su * delta_vec[None, :]) @ X)
        else:
            ST = P[np.ix_(src_idx, dst_idx)]
        Ps1, Ps2 = ST[0, 0], ST[0, 1]
        P11, P12 = ST[1, 0], ST[1, 1]
        P21, P22 = ST[2, 0], ST[2, 1]
        G = np.array([[P11, P21], [P12, P22]], dtype=np.complex128)
        b = np.array([Ps1, Ps2], dtype=np.complex128)
        try:
            x = np.linalg.solve(G, b)
        except np.linalg.LinAlgError:
            x = np.linalg.solve(G + 1e-12 * np.eye(2, dtype=np.complex128), b)
        F1[i], F2[i] = x[0], x[1]

    c1 = np.fft.fft(F1) / float(m)
    c2 = np.fft.fft(F2) / float(m)
    t = np.arange(m, dtype=np.float64)
    scale = r ** (-t)
    f1 = np.maximum((scale * c1).real[1 : t_max_aw + 1], 0.0)
    f2 = np.maximum((scale * c2).real[1 : t_max_aw + 1], 0.0)
    f_any = np.maximum(f1 + f2, 0.0)
    return {
        "grid": {"m": int(m), "r": float(r), "oversample": int(oversample), "r_pow10": float(r_pow10)},
        "f1": f1,
        "f2": f2,
        "f_any": f_any,
        "defect_pairs": int(len(defects)),
        "defect_nodes": int(len(nodes_list)),
        "local_bias_sites": int(len(local_bias_arrows)),
    }


def build_reflecting_s0_config() -> LatticeConfig:
    spec = ConfigSpec(
        N=30,
        q=0.8,
        g_x=-0.4,
        g_y=0.0,
        boundary_x="reflecting",
        boundary_y="reflecting",
        start=(1, 15),
        target=(30, 15),
        local_bias_arrows={},
        local_bias_delta=0.0,
        sticky_sites={(15, 15): 0.1},
        barriers_reflect=set(),
        barriers_perm={edge_key((20, 15), (21, 15)): 0.05},
    )
    return spec_to_internal(spec)


def run_reflecting_exact_recursion(cfg: LatticeConfig, *, t_max: int) -> Tuple[np.ndarray, float]:
    return exact_fpt(cfg, t_max=t_max)


def run_reflecting_full_aw(
    cfg: LatticeConfig,
    *,
    t_max: int,
    oversample: int,
    r_pow10: float,
) -> Tuple[np.ndarray, Any]:
    return fpt_pmf_aw(cfg, t_max=t_max, oversample=oversample, r_pow10=r_pow10)


def _load_plot_stack():
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    return plt, Line2D


def _winner_color(family: str | None) -> str:
    if family == "time_recursion":
        return COLOR_DEFECT
    if family == "luca_gf":
        return "#b45f06"
    return "#cbd5e1"


def _draw_param_card(
    ax: Any,
    title: str,
    lines: Sequence[str],
    *,
    edgecolor: str = "#cbd5e1",
    fontsize: float = 10.0,
) -> None:
    ax.axis("off")
    text = title + "\n\n" + "\n".join(lines)
    ax.text(
        0.02,
        0.98,
        text,
        va="top",
        ha="left",
        fontsize=fontsize,
        family="monospace",
        color=COLOR_TEXT,
        bbox={"boxstyle": "round,pad=0.5", "facecolor": COLOR_CARD, "edgecolor": edgecolor, "linewidth": 1.6},
    )


def _draw_speed_card(ax: Any, speed_info: Dict[str, Any] | None) -> None:
    ax.axis("off")
    if not speed_info:
        _draw_param_card(ax, "Speed verdict", ["No timing summary attached."], fontsize=9.0)
        return

    diag = speed_info.get("diagnostic")
    curve = speed_info.get("curve")
    winner = diag or curve
    edgecolor = _winner_color(str((winner or {}).get("recommended_family", "")))

    def _family_short(row: Dict[str, Any]) -> str:
        return "Time recursion" if row.get("recommended_family") == "time_recursion" else "Luca/GF"

    def _factor(row: Dict[str, Any]) -> float:
        luca = float(row["median_seconds_luca"])
        time_family = float(row["median_seconds_time"])
        faster = min(luca, time_family)
        slower = max(luca, time_family)
        return slower / faster if faster > 0.0 else float("inf")

    lines: List[str] = []
    if diag:
        lines.extend(
            [
                f"DIAGNOSTIC: {_family_short(diag)} faster",
                f"time={float(diag['median_seconds_time']):.4g}s, luca={float(diag['median_seconds_luca']):.4g}s",
                f"margin={_factor(diag):.1f}x",
            ]
        )
    if curve:
        curve_line = f"CURVE: {_family_short(curve)}"
        if diag and curve.get("recommended_family") == diag.get("recommended_family"):
            curve_line += " (same winner)"
        lines.extend(
            [
                "",
                curve_line,
                f"time={float(curve['median_seconds_time']):.4g}s, luca={float(curve['median_seconds_luca']):.4g}s",
            ]
        )

    _draw_param_card(ax, "Speed verdict", lines, edgecolor=edgecolor, fontsize=8.9)


def _ring_positions(N: int) -> np.ndarray:
    theta = np.linspace(0.0, 2.0 * np.pi, N, endpoint=False)
    return np.column_stack([np.cos(theta), np.sin(theta)])


def _draw_ring_panel(
    ax: Any,
    *,
    N: int,
    start: int,
    target: int,
    shortcut_src: int,
    shortcut_dst: int,
    title: str,
    second_walker: int | None = None,
) -> None:
    pts = _ring_positions(N)
    ax.plot(np.r_[pts[:, 0], pts[0, 0]], np.r_[pts[:, 1], pts[0, 1]], color=COLOR_RING, lw=1.6)
    ax.scatter(pts[:, 0], pts[:, 1], s=18, color="#cbd5e1", zorder=2)
    ax.scatter(pts[start, 0], pts[start, 1], s=80, marker="s", color=COLOR_START, zorder=4)
    ax.scatter(pts[target, 0], pts[target, 1], s=95, marker="D", color=COLOR_TARGET, zorder=4)
    if second_walker is not None:
        ax.scatter(pts[second_walker, 0], pts[second_walker, 1], s=85, marker="o", color=COLOR_TARGET_ALT, zorder=4)
    if shortcut_src != shortcut_dst:
        ax.annotate(
            "",
            xy=pts[shortcut_dst],
            xytext=pts[shortcut_src],
            arrowprops={"arrowstyle": "->", "lw": 2.4, "color": COLOR_SHORTCUT},
        )
    ax.set_title(title, fontsize=11)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlim(-1.3, 1.3)
    ax.set_ylim(-1.3, 1.3)


def _draw_pair_torus(
    ax: Any,
    *,
    N: int,
    target_mode: str,
    delta: int | None = None,
    defect_line_x: int | None = None,
    title: str,
) -> None:
    ax.set_facecolor("#ffffff")
    ax.imshow(np.zeros((N, N)), cmap="Greys", vmin=0.0, vmax=1.0, origin="lower", alpha=0.02)
    if target_mode == "diagonal":
        ax.plot(np.arange(N), np.arange(N), color=COLOR_TARGET, lw=2.0, label="target set")
    elif delta is not None:
        ax.scatter([delta], [delta], s=70, marker="D", color=COLOR_TARGET, label="single target")
    if defect_line_x is not None:
        ax.axvline(defect_line_x, color=COLOR_DEFECT, lw=2.0, ls="--", label="defect line")
    ax.set_title(title, fontsize=11)
    ax.set_xlabel("walker 1 position")
    ax.set_ylabel("walker 2 position")
    step = max(1, N // 5)
    ticks = list(range(0, N, step))
    ax.set_xticks(ticks)
    ax.set_yticks(ticks)
    ax.grid(color=COLOR_GRID, lw=0.5, alpha=0.5)
    handles, labels = ax.get_legend_handles_labels()
    if handles:
        ax.legend(handles, labels, frameon=False, fontsize=8, loc="upper right")


def _draw_grid_panel(
    ax: Any,
    *,
    N: int,
    start: Coord,
    m1: Coord,
    m2: Coord | None,
    arrow_map: Dict[Coord, str],
    sticky_sites: Dict[Coord, float] | None = None,
    barrier_edges: Sequence[Tuple[Coord, Coord]] | None = None,
    title: str,
) -> None:
    sticky_sites = sticky_sites or {}
    barrier_edges = barrier_edges or []
    ax.set_xlim(-0.5, N - 0.5)
    ax.set_ylim(-0.5, N - 0.5)
    ax.set_aspect("equal")
    ax.set_title(title, fontsize=11)
    ax.set_xticks(range(0, N, max(1, N // 6)))
    ax.set_yticks(range(0, N, max(1, N // 6)))
    ax.grid(color=COLOR_GRID, lw=0.4, alpha=0.6)

    if sticky_sites:
        xs = [xy[0] for xy in sticky_sites]
        ys = [xy[1] for xy in sticky_sites]
        ax.scatter(xs, ys, s=110, marker="o", facecolor=COLOR_STICKY, edgecolor="none", alpha=0.65, zorder=2)

    if arrow_map:
        pts = list(arrow_map.keys())
        xs = np.asarray([p[0] for p in pts], dtype=np.float64)
        ys = np.asarray([p[1] for p in pts], dtype=np.float64)
        u = np.asarray([DIR_VEC[arrow_map[p]][0] for p in pts], dtype=np.float64)
        v = np.asarray([DIR_VEC[arrow_map[p]][1] for p in pts], dtype=np.float64)
        ax.quiver(xs, ys, u, v, color=COLOR_BIAS, angles="xy", scale_units="xy", scale=1.9, width=0.004, zorder=3)

    for a, b in barrier_edges:
        ax.plot([a[0], b[0]], [a[1], b[1]], color=COLOR_BARRIER, lw=3.2, solid_capstyle="round", zorder=4)

    ax.scatter([start[0]], [start[1]], s=120, marker="s", color=COLOR_START, zorder=5)
    ax.scatter([m1[0]], [m1[1]], s=120, marker="D", color=COLOR_TARGET, zorder=5)
    if m2 is not None:
        ax.scatter([m2[0]], [m2[1]], s=120, marker="o", color=COLOR_TARGET_ALT, zorder=5)


def _draw_generic_legend(ax: Any) -> None:
    _plt, Line2D = _load_plot_stack()
    ax.axis("off")
    handles = [
        Line2D([0], [0], marker="s", color="none", markerfacecolor=COLOR_START, markersize=9, label="start"),
        Line2D([0], [0], marker="D", color="none", markerfacecolor=COLOR_TARGET, markersize=9, label="target / target set"),
        Line2D([0], [0], marker="o", color="none", markerfacecolor=COLOR_TARGET_ALT, markersize=9, label="second target / walker"),
        Line2D([0], [0], color=COLOR_BIAS, lw=2.0, label="local bias / defect support"),
        Line2D([0], [0], color=COLOR_SHORTCUT, lw=2.0, label="shortcut edge"),
        Line2D([0], [0], color=COLOR_BARRIER, lw=2.0, label="barrier / low-pass edge"),
    ]
    ax.legend(handles=handles, frameon=False, loc="center left", fontsize=9)


def _runtime_labels(rows: Sequence[Dict[str, Any]]) -> List[str]:
    return [f"{idx + 1}\n{row['workload_id']}" for idx, row in enumerate(rows)]


def _draw_runtime_bar_panel(ax: Any, rows: Sequence[Dict[str, Any]], *, title: str) -> None:
    luca = np.asarray([float(row["median_seconds_luca"]) for row in rows], dtype=np.float64)
    time_family = np.asarray([float(row["median_seconds_time"]) for row in rows], dtype=np.float64)
    x = np.arange(len(rows), dtype=np.float64)
    w = 0.36

    ax.bar(x - w / 2.0, luca, width=w, color="#b45f06", alpha=0.92, label="Luca / GF")
    ax.bar(x + w / 2.0, time_family, width=w, color="#2563eb", alpha=0.92, label="Time recursion")
    ax.set_yscale("log")
    ax.set_xticks(x)
    ax.set_xticklabels(_runtime_labels(rows))
    ax.set_ylabel("Median runtime (s)")
    ax.set_title(title, fontsize=13, color=COLOR_TEXT)
    ax.grid(axis="y", alpha=0.25, which="both")
    ax.legend(frameon=False, ncol=2, loc="upper right")
    for idx, row in enumerate(rows):
        family = str(row.get("recommended_family", ""))
        edge = _winner_color(family)
        name = "Luca faster" if family == "luca_gf" else "Time faster"
        ratio = float(row["speedup_time_over_luca"])
        if family == "time_recursion" and ratio > 0.0:
            margin = 1.0 / ratio
        else:
            margin = ratio
        y = max(float(row["median_seconds_luca"]), float(row["median_seconds_time"])) * 1.45
        ax.text(
            idx,
            y,
            f"{name}\n{margin:.1f}x",
            ha="center",
            va="bottom",
            fontsize=8.5,
            color=COLOR_TEXT,
            bbox={
                "boxstyle": "round,pad=0.25",
                "facecolor": "#ffffff",
                "edgecolor": edge,
                "linewidth": 1.2,
            },
        )


def _draw_overview_footer(ax: Any, *, workload_id: str, row: Dict[str, Any] | None, index: int) -> None:
    ax.axis("off")
    if not row:
        _draw_param_card(ax, f"{index}. {workload_id}", ["No timing row."], fontsize=8.5)
        return
    family = str(row.get("recommended_family", ""))
    edge = _winner_color(family)
    ratio = float(row["speedup_time_over_luca"])
    if family == "time_recursion" and ratio > 0.0:
        margin = 1.0 / ratio
        winner = "Time recursion faster"
    else:
        margin = ratio
        winner = "Luca / GF faster"
    lines = [
        winner,
        f"diag: time={float(row['median_seconds_time']):.4g}s",
        f"      luca={float(row['median_seconds_luca']):.4g}s",
        f"margin={margin:.1f}x",
    ]
    _draw_param_card(ax, f"{index}. {workload_id}", lines, edgecolor=edge, fontsize=8.15)


def _draw_overview_geometry(fig: Any, slot: Any, workload_id: str, cfg: Dict[str, Any]) -> None:
    if workload_id == "RING-1T-paper":
        ax = fig.add_subplot(slot)
        _draw_ring_panel(
            ax,
            N=int(cfg["N"]),
            start=int(cfg["start"]),
            target=int(cfg["target"]),
            shortcut_src=int(cfg["shortcut_src"]),
            shortcut_dst=int(cfg["shortcut_dst"]),
            title="Ring + shortcut",
        )
        ax.text(
            0.02,
            0.04,
            f"N={cfg['N']}, target={cfg['target']}, shortcut {cfg['shortcut_src']}->{cfg['shortcut_dst']}",
            transform=ax.transAxes,
            fontsize=8.0,
            family="monospace",
            color=COLOR_TEXT,
            bbox={"boxstyle": "round,pad=0.2", "facecolor": "#ffffff", "edgecolor": "#cbd5e1"},
        )
        return

    if workload_id == "ENC-FIXED":
        sub = slot.subgridspec(1, 2, width_ratios=[1.0, 1.0], wspace=0.16)
        _draw_ring_panel(
            fig.add_subplot(sub[0, 0]),
            N=int(cfg["N"]),
            start=int(cfg["n0"]),
            target=int(cfg["delta"]),
            second_walker=int(cfg["m0"]),
            shortcut_src=int(cfg["shortcut_src"]),
            shortcut_dst=int(cfg["shortcut_dst"]),
            title="Ring walkers",
        )
        _draw_pair_torus(
            fig.add_subplot(sub[0, 1]),
            N=int(cfg["N"]),
            target_mode="single",
            delta=int(cfg["delta"]),
            title="Pair torus target",
        )
        return

    if workload_id == "ENC-ANY":
        sub = slot.subgridspec(1, 2, width_ratios=[1.0, 1.0], wspace=0.16)
        _draw_ring_panel(
            fig.add_subplot(sub[0, 0]),
            N=int(cfg["N"]),
            start=int(cfg["n0"]),
            second_walker=int(cfg["m0"]),
            target=int(cfg["shortcut_dst"]),
            shortcut_src=int(cfg["shortcut_src"]),
            shortcut_dst=int(cfg["shortcut_dst"]),
            title="Ring + shortcut",
        )
        _draw_pair_torus(
            fig.add_subplot(sub[0, 1]),
            N=int(cfg["N"]),
            target_mode="diagonal",
            defect_line_x=int(cfg["shortcut_src"]),
            title="Diagonal target set",
        )
        return

    if workload_id == "TT-C1":
        start, m1, m2, arrow_map, _delta = build_c1_geometry(N=int(cfg["N"]))
        ax = fig.add_subplot(slot)
        _draw_grid_panel(ax, N=int(cfg["N"]), start=start, m1=m1, m2=m2, arrow_map=arrow_map, title="C1 local-bias field")
        return

    if workload_id == "TT-LF1":
        start, m1, m2, arrow_map, _q, _delta = build_luca_fast_geometry(int(cfg["N"]))
        ax = fig.add_subplot(slot)
        _draw_grid_panel(ax, N=int(cfg["N"]), start=start, m1=m1, m2=m2, arrow_map=arrow_map, title="Sparse defect anchor")
        return

    if workload_id == "REF-S0":
        cfg_ref = build_reflecting_s0_config()
        ax = fig.add_subplot(slot)
        _draw_grid_panel(
            ax,
            N=int(cfg_ref.N),
            start=cfg_ref.start,
            m1=cfg_ref.target,
            m2=None,
            arrow_map={},
            sticky_sites=cfg_ref.sticky_sites,
            barrier_edges=list(cfg_ref.barriers_perm.keys()),
            title="Reflecting control",
        )
        ax.plot([0, 0, cfg_ref.N - 1, cfg_ref.N - 1, 0], [0, cfg_ref.N - 1, cfg_ref.N - 1, 0, 0], color=COLOR_RING, lw=2.0)
        return

    raise ValueError(f"unknown workload id: {workload_id}")


def render_runtime_config_overview_figure(
    workloads: Sequence[Dict[str, Any]],
    diagnostic_rows: Sequence[Dict[str, Any]],
    out_path: Path,
) -> None:
    plt, _Line2D = _load_plot_stack()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    row_map = {str(row["workload_id"]): row for row in diagnostic_rows}

    fig = plt.figure(figsize=(13.8, 11.0))
    outer = fig.add_gridspec(3, 3, height_ratios=[1.15, 1.0, 1.0], hspace=0.28, wspace=0.16)
    ax_top = fig.add_subplot(outer[0, :])
    _draw_runtime_bar_panel(ax_top, diagnostic_rows, title="Diagnostic runtime with direct workload-to-configuration mapping")

    for idx, workload in enumerate(workloads):
        wid = str(workload["workload_id"])
        cfg = dict(workload["config"])
        row = row_map.get(wid)
        tile = outer[1 + idx // 3, idx % 3].subgridspec(2, 1, height_ratios=[0.76, 0.24], hspace=0.04)
        _draw_overview_geometry(fig, tile[0, 0], wid, cfg)
        _draw_overview_footer(fig.add_subplot(tile[1, 0]), workload_id=wid, row=row, index=idx + 1)

    fig.suptitle(
        "One-glance overview: the numbered tiles 1-6 match the numbered workload groups on the runtime chart",
        fontsize=14,
        color=COLOR_TEXT,
        y=0.995,
    )
    fig.tight_layout(rect=(0.0, 0.0, 1.0, 0.985))
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)


def render_workload_config_figure(
    workload_id: str,
    cfg: Dict[str, Any],
    out_path: Path,
    *,
    speed_info: Dict[str, Any] | None = None,
) -> None:
    plt, _Line2D = _load_plot_stack()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if workload_id == "RING-1T-paper":
        fig = plt.figure(figsize=(12.5, 4.6))
        gs = fig.add_gridspec(1, 3, width_ratios=[1.0, 1.05, 0.95])
        _draw_ring_panel(
            fig.add_subplot(gs[0, 0]),
            N=int(cfg["N"]),
            start=int(cfg["start"]),
            target=int(cfg["target"]),
            shortcut_src=int(cfg["shortcut_src"]),
            shortcut_dst=int(cfg["shortcut_dst"]),
            title="Ring geometry",
        )
        ax2 = fig.add_subplot(gs[0, 1])
        ax2.axis("off")
        ax2.text(
            0.02,
            0.92,
            "Transition stencil\n\n"
            "default: stay=1-q, left=q/2, right=q/2\n"
            "shortcut site: move beta mass to dst\n"
            "GF family: closed-form PGF + AW/Cauchy FFT\n"
            "time family: exact absorbing recursion",
            fontsize=10,
            va="top",
            family="monospace",
            color=COLOR_TEXT,
            bbox={"boxstyle": "round,pad=0.45", "facecolor": COLOR_CARD, "edgecolor": "#cbd5e1"},
        )
        card_gs = gs[0, 2].subgridspec(2, 1, height_ratios=[0.58, 0.42], hspace=0.18)
        _draw_param_card(
            fig.add_subplot(card_gs[0, 0]),
            "Parameters",
            [
                f"N={cfg['N']}, q={cfg['q']:.4g}, beta={cfg['beta']:.4g}",
                f"start={cfg['start']}, target={cfg['target']}",
                f"shortcut=({cfg['shortcut_src']} -> {cfg['shortcut_dst']})",
                f"AW oversample={cfg['aw_oversample']}, r_pow10={cfg['aw_r_pow10']}",
            ],
            fontsize=9.3,
        )
        _draw_speed_card(fig.add_subplot(card_gs[1, 0]), speed_info)
    elif workload_id == "ENC-FIXED":
        fig = plt.figure(figsize=(12.5, 4.8))
        gs = fig.add_gridspec(1, 4, width_ratios=[1.0, 1.05, 0.95, 0.9])
        _draw_ring_panel(
            fig.add_subplot(gs[0, 0]),
            N=int(cfg["N"]),
            start=int(cfg["n0"]),
            target=int(cfg["delta"]),
            second_walker=int(cfg["m0"]),
            shortcut_src=int(cfg["shortcut_src"]),
            shortcut_dst=int(cfg["shortcut_dst"]),
            title="Original ring walkers",
        )
        _draw_pair_torus(
            fig.add_subplot(gs[0, 1]),
            N=int(cfg["N"]),
            target_mode="single",
            delta=int(cfg["delta"]),
            title="Pair-state torus target",
        )
        _draw_generic_legend(fig.add_subplot(gs[0, 2]))
        card_gs = gs[0, 3].subgridspec(2, 1, height_ratios=[0.58, 0.42], hspace=0.18)
        _draw_param_card(
            fig.add_subplot(card_gs[0, 0]),
            "Parameters",
            [
                f"N={cfg['N']}, delta={cfg['delta']}",
                f"(q1,g1)=({cfg['q1']:.3g},{cfg['g1']:.3g})",
                f"(q2,g2)=({cfg['q2']:.3g},{cfg['g2']:.3g})",
                f"initial=(n0,m0)=({cfg['n0']},{cfg['m0']})",
                "GF: single-target renewal on pair propagator",
                "time: absorbed pair recursion",
            ],
            fontsize=9.0,
        )
        _draw_speed_card(fig.add_subplot(card_gs[1, 0]), speed_info)
    elif workload_id == "ENC-ANY":
        fig = plt.figure(figsize=(12.5, 4.8))
        gs = fig.add_gridspec(1, 4, width_ratios=[1.0, 1.05, 0.95, 0.9])
        _draw_ring_panel(
            fig.add_subplot(gs[0, 0]),
            N=int(cfg["N"]),
            start=int(cfg["n0"]),
            second_walker=int(cfg["m0"]),
            target=int(cfg["shortcut_dst"]),
            shortcut_src=int(cfg["shortcut_src"]),
            shortcut_dst=int(cfg["shortcut_dst"]),
            title="Original ring walkers + shortcut",
        )
        _draw_pair_torus(
            fig.add_subplot(gs[0, 1]),
            N=int(cfg["N"]),
            target_mode="diagonal",
            defect_line_x=int(cfg["shortcut_src"]),
            title="Pair torus: diagonal targets + defect line",
        )
        _draw_generic_legend(fig.add_subplot(gs[0, 2]))
        card_gs = gs[0, 3].subgridspec(2, 1, height_ratios=[0.58, 0.42], hspace=0.18)
        _draw_param_card(
            fig.add_subplot(card_gs[0, 0]),
            "Parameters",
            [
                f"N={cfg['N']}, beta={cfg['beta']:.3g}",
                f"(q1,g1)=({cfg['q1']:.3g},{cfg['g1']:.3g})",
                f"(q2,g2)=({cfg['q2']:.3g},{cfg['g2']:.3g})",
                f"initial=(n0,m0)=({cfg['n0']},{cfg['m0']})",
                f"shortcut=({cfg['shortcut_src']} -> {cfg['shortcut_dst']})",
                "GF: diagonal target-set renewal + AW",
            ],
            fontsize=9.0,
        )
        _draw_speed_card(fig.add_subplot(card_gs[1, 0]), speed_info)
    elif workload_id == "TT-C1":
        start, m1, m2, arrow_map, delta = build_c1_geometry(N=int(cfg["N"]))
        fast_nodes = [to0((15, 15)), to0((22, 15))]
        slow_nodes = [to0((15, 15)), to0((15, 27)), to0((3, 27)), to0((3, 7)), to0((7, 7))]
        fast_path = polyline_points(fast_nodes)
        slow_path = polyline_points(slow_nodes)
        fast_map, fast_cells = corridor_assignments(fast_path, width=1, skip=0, N=int(cfg["N"]))
        slow_map, slow_cells = corridor_assignments(slow_path, width=3, skip=2, N=int(cfg["N"]))
        fig = plt.figure(figsize=(12.8, 4.9))
        gs = fig.add_gridspec(1, 4, width_ratios=[1.05, 1.05, 0.85, 0.95])
        _draw_grid_panel(fig.add_subplot(gs[0, 0]), N=int(cfg["N"]), start=start, m1=m1, m2=m2, arrow_map=arrow_map, title="Full local-bias field")
        ax2 = fig.add_subplot(gs[0, 1])
        _draw_grid_panel(ax2, N=int(cfg["N"]), start=start, m1=m1, m2=m2, arrow_map=fast_map, title="Fast corridor support")
        xs = [p[0] for p in slow_cells]
        ys = [p[1] for p in slow_cells]
        ax2.scatter(xs, ys, s=20, color=COLOR_DIAG, alpha=0.55, zorder=1)
        _draw_generic_legend(fig.add_subplot(gs[0, 2]))
        card_gs = gs[0, 3].subgridspec(2, 1, height_ratios=[0.6, 0.4], hspace=0.18)
        _draw_param_card(
            fig.add_subplot(card_gs[0, 0]),
            "Parameters",
            [
                f"N={cfg['N']}, q={cfg['q']:.3g}, delta={delta:.3g}",
                f"start={start}, m1={m1}, m2={m2}",
                f"|fast cells|={len(fast_cells)}, |slow cells|={len(slow_cells)}",
                "GF: defect-reduced AW on selected propagators",
                "time: sparse exact recursion to long horizon",
            ],
            fontsize=8.95,
        )
        _draw_speed_card(fig.add_subplot(card_gs[1, 0]), speed_info)
    elif workload_id == "TT-LF1":
        start, m1, m2, arrow_map, q, delta = build_luca_fast_geometry(int(cfg["N"]))
        fig = plt.figure(figsize=(12.8, 4.9))
        gs = fig.add_gridspec(1, 4, width_ratios=[1.05, 1.05, 0.85, 0.95])
        _draw_grid_panel(fig.add_subplot(gs[0, 0]), N=int(cfg["N"]), start=start, m1=m1, m2=m2, arrow_map=arrow_map, title="Sparse-defect geometry")
        ax2 = fig.add_subplot(gs[0, 1])
        _draw_grid_panel(ax2, N=int(cfg["N"]), start=start, m1=m1, m2=m2, arrow_map={}, title="Defect mask")
        only = list(arrow_map.keys())[0]
        ax2.scatter([only[0]], [only[1]], s=180, marker="o", facecolor=COLOR_DIAG, edgecolor=COLOR_BIAS, linewidth=2.0, zorder=4)
        _draw_generic_legend(fig.add_subplot(gs[0, 2]))
        card_gs = gs[0, 3].subgridspec(2, 1, height_ratios=[0.6, 0.4], hspace=0.18)
        _draw_param_card(
            fig.add_subplot(card_gs[0, 0]),
            "Parameters",
            [
                f"N={cfg['N']}, q={q:.3g}, delta={delta:.3g}",
                f"start={start}, m1={m1}, m2={m2}",
                f"local bias sites={len(arrow_map)}, defect pairs~2",
                "Constructed ultra-sparse positive anchor for GF family",
            ],
            fontsize=9.0,
        )
        _draw_speed_card(fig.add_subplot(card_gs[1, 0]), speed_info)
    elif workload_id == "REF-S0":
        cfg_ref = build_reflecting_s0_config()
        fig = plt.figure(figsize=(12.2, 4.8))
        gs = fig.add_gridspec(1, 4, width_ratios=[1.1, 1.0, 0.82, 0.95])
        _draw_grid_panel(
            fig.add_subplot(gs[0, 0]),
            N=int(cfg_ref.N),
            start=cfg_ref.start,
            m1=cfg_ref.target,
            m2=None,
            arrow_map={},
            sticky_sites=cfg_ref.sticky_sites,
            barrier_edges=list(cfg_ref.barriers_perm.keys()),
            title="Reflecting low-defect control",
        )
        ax2 = fig.add_subplot(gs[0, 1])
        _draw_grid_panel(
            ax2,
            N=int(cfg_ref.N),
            start=cfg_ref.start,
            m1=cfg_ref.target,
            m2=None,
            arrow_map={},
            title="Boundary + defect annotations",
        )
        ax2.plot([0, 0, cfg_ref.N - 1, cfg_ref.N - 1, 0], [0, cfg_ref.N - 1, cfg_ref.N - 1, 0, 0], color=COLOR_RING, lw=2.0)
        _draw_generic_legend(fig.add_subplot(gs[0, 2]))
        card_gs = gs[0, 3].subgridspec(2, 1, height_ratios=[0.6, 0.4], hspace=0.18)
        _draw_param_card(
            fig.add_subplot(card_gs[0, 0]),
            "Parameters",
            [
                f"N={cfg_ref.N}, q={cfg_ref.q:.3g}, (gx,gy)=({cfg_ref.g_x:.3g},{cfg_ref.g_y:.3g})",
                f"start={cfg_ref.start}, target={cfg_ref.target}",
                f"sticky sites={len(cfg_ref.sticky_sites)}, low-pass barriers={len(cfg_ref.barriers_perm)}",
                "GF: full AW still feasible",
                "time: exact recursion baseline",
            ],
            fontsize=8.9,
        )
        _draw_speed_card(fig.add_subplot(card_gs[1, 0]), speed_info)
    else:
        raise ValueError(f"unknown workload id: {workload_id}")

    fig.suptitle(f"{workload_id} detailed configuration", fontsize=13, color=COLOR_TEXT, y=0.98)
    fig.tight_layout()
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
