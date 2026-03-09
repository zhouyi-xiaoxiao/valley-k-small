from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Sequence, Tuple

from vkcore.grid2d.model_core_reflecting import edge_key

from .types import Coord, Edge

DIRS = {
    "L": (-1, 0),
    "R": (1, 0),
    "U": (0, -1),
    "D": (0, 1),
}

DIR_MAP = {
    "L": "left",
    "R": "right",
    "U": "up",
    "D": "down",
}

CONFIG_FILENAMES = {
    "A": "A_geometry_U_detour.json",
    "B": "B_parallel_lanes_doors.json",
    "C": "C_wall_loop_conveyor.json",
    "X": "X_screenshot_baseline.json",
    "D": "D_screenshot_sticky_belt.json",
    "E": "E_screenshot_sticky_belt_bias.json",
    "R": "R_small_rect_baseline.json",
    "Y": "Y_screenshot_inside_walls.json",
    "Z": "Z_screenshot_wall_endpoints.json",
    "S": "S_small_rect_endpoints.json",
}


def add_segment(cells: set[Coord], x0: int, y0: int, x1: int, y1: int) -> None:
    if x0 != x1 and y0 != y1:
        raise ValueError("segment must be horizontal or vertical")
    if x0 == x1:
        y_start, y_end = sorted((y0, y1))
        for y in range(y_start, y_end + 1):
            cells.add((x0, y))
    else:
        x_start, x_end = sorted((x0, x1))
        for x in range(x_start, x_end + 1):
            cells.add((x, y0))


def build_barriers(allowed: set[Coord], N: int) -> List[Edge]:
    barriers: set[Edge] = set()
    for (x, y) in allowed:
        for dx, dy in DIRS.values():
            nx, ny = x + dx, y + dy
            if nx < 1 or nx > N or ny < 1 or ny > N:
                continue
            if (nx, ny) not in allowed:
                barriers.add(edge_key((x, y), (nx, ny)))
    return sorted(barriers)


@dataclass
class CaseDef:
    case_id: str
    name: str
    N: int
    q: float
    gx: float
    gy: float
    start: Coord
    target: Coord
    allowed: set[Coord]
    local_bias: Dict[Coord, Tuple[str, float]]
    sticky: Dict[Coord, float]
    doors: Dict[Edge, float]
    extra_barriers: set[Edge]
    t_max: int
    fast_set: set[Coord]
    slow_set: set[Coord]


# ---- Case builders ----

def _finalize_sets(*, allowed: set[Coord], fast_set: set[Coord], start: Coord, target: Coord) -> set[Coord]:
    slow_set = allowed.difference(fast_set)
    slow_set.discard(start)
    slow_set.discard(target)
    return slow_set


def build_a() -> CaseDef:
    N = 60
    allowed: set[Coord] = set()

    for x in range(28, 33):
        for y in range(10, 51):
            allowed.add((x, y))
    for x in range(1, 29):
        allowed.add((x, 50))
    for y in range(10, 51):
        allowed.add((1, y))
    for x in range(1, 33):
        allowed.add((x, 10))

    local_bias: Dict[Coord, Tuple[str, float]] = {}

    for x in range(28, 33):
        for y in range(11, 50):
            local_bias[(x, y)] = ("U", 0.95)

    local_bias[(1, 50)] = ("U", 0.95)
    for x in range(2, 28):
        local_bias[(x, 50)] = ("L", 0.95)
    local_bias[(28, 50)] = ("L", 0.6)
    for x in range(29, 33):
        local_bias[(x, 50)] = ("U", 0.6)

    for y in range(11, 50):
        local_bias[(1, y)] = ("U", 0.95)

    for x in range(1, 30):
        local_bias[(x, 10)] = ("R", 0.95)
    for x in range(31, 33):
        local_bias[(x, 10)] = ("L", 0.95)

    fast_set = {(x, y) for x in range(28, 33) for y in range(10, 51)}
    slow_set = _finalize_sets(allowed=allowed, fast_set=fast_set, start=(30, 50), target=(30, 10))

    return CaseDef(
        case_id="A",
        name="geometry U-detour vs straight tube",
        N=N,
        q=0.8,
        gx=0.0,
        gy=-0.2,
        start=(30, 50),
        target=(30, 10),
        allowed=allowed,
        local_bias=local_bias,
        sticky={},
        doors={},
        extra_barriers=set(),
        t_max=2000,
        fast_set=fast_set,
        slow_set=slow_set,
    )


def build_b() -> CaseDef:
    N = 60
    allowed: set[Coord] = set()
    for y in range(10, 51):
        allowed.add((29, y))
        allowed.add((31, y))
    for x in range(29, 32):
        allowed.add((x, 10))
        allowed.add((x, 50))

    local_bias: Dict[Coord, Tuple[str, float]] = {}
    for y in range(11, 51):
        local_bias[(29, y)] = ("U", 0.95)
        local_bias[(31, y)] = ("U", 0.95)

    local_bias[(29, 10)] = ("R", 0.95)
    local_bias[(31, 10)] = ("L", 0.95)

    doors: Dict[Edge, float] = {}
    for y in range(11, 51):
        doors[edge_key((31, y - 1), (31, y))] = 0.2

    slow_set = {(31, y) for y in range(10, 51)}
    fast_set = allowed.difference(slow_set)

    return CaseDef(
        case_id="B",
        name="parallel lanes with door array slowdown",
        N=N,
        q=0.8,
        gx=0.0,
        gy=-0.2,
        start=(30, 50),
        target=(30, 10),
        allowed=allowed,
        local_bias=local_bias,
        sticky={},
        doors=doors,
        extra_barriers=set(),
        t_max=3000,
        fast_set=fast_set,
        slow_set=slow_set,
    )


def build_c() -> CaseDef:
    N = 60
    allowed: set[Coord] = set()
    for y in range(10, 51):
        allowed.add((30, y))
    for x in range(10, 51):
        allowed.add((x, 10))
        allowed.add((x, 50))
    for y in range(10, 51):
        allowed.add((10, y))
        allowed.add((50, y))

    local_bias: Dict[Coord, Tuple[str, float]] = {}
    sticky: Dict[Coord, float] = {}

    delta_loop = 0.1
    for x in range(10, 50):
        local_bias[(x, 10)] = ("R", delta_loop)
    for y in range(10, 50):
        local_bias[(50, y)] = ("D", delta_loop)
    for x in range(11, 51):
        local_bias[(x, 50)] = ("L", delta_loop)
    for y in range(11, 51):
        local_bias[(10, y)] = ("U", delta_loop)

    for y in range(11, 51):
        local_bias[(30, y)] = ("U", 0.95)
    local_bias[(30, 10)] = ("U", 0.95)
    local_bias[(30, 50)] = ("U", 0.95)

    for x in range(10, 51):
        sticky[(x, 10)] = 0.2
        sticky[(x, 50)] = 0.2
    for y in range(10, 51):
        sticky[(10, y)] = 0.2
        sticky[(50, y)] = 0.2

    fast_set = {(30, y) for y in range(10, 51)}
    slow_set = _finalize_sets(allowed=allowed, fast_set=fast_set, start=(30, 50), target=(30, 10))

    return CaseDef(
        case_id="C",
        name="wall loop conveyor vs central fast corridor",
        N=N,
        q=0.8,
        gx=0.0,
        gy=0.0,
        start=(30, 50),
        target=(30, 10),
        allowed=allowed,
        local_bias=local_bias,
        sticky=sticky,
        doors={},
        extra_barriers=set(),
        t_max=2500,
        fast_set=fast_set,
        slow_set=slow_set,
    )


def _full_grid_allowed(N: int) -> set[Coord]:
    return {(x, y) for x in range(1, N + 1) for y in range(1, N + 1)}


def _screenshot_internal_walls(*, y0: int = 15, y1: int = 45) -> set[Edge]:
    barriers: set[Edge] = set()
    for y in range(y0, y1 + 1):
        barriers.add(edge_key((28, y), (29, y)))
        barriers.add(edge_key((31, y), (32, y)))
    return barriers


def _screenshot_corridor_bias(
    *,
    delta_core: float,
    delta_open: float,
    y0: int = 15,
    y1: int = 45,
) -> Dict[Coord, Tuple[str, float]]:
    local_bias: Dict[Coord, Tuple[str, float]] = {}
    for x in range(29, 32):
        for y in range(y0, y1 + 1):
            local_bias[(x, y)] = ("U", delta_core)
    for x in range(29, 32):
        for y in range(y1 + 1, 51):
            local_bias[(x, y)] = ("U", delta_open)
        for y in range(10, y0):
            local_bias[(x, y)] = ("U", delta_open)
    return local_bias


def _merge_local_bias(
    base: Dict[Coord, Tuple[str, float]],
    extra: Dict[Coord, Tuple[str, float]],
) -> Dict[Coord, Tuple[str, float]]:
    out = dict(base)
    out.update(extra)
    return out


def _screenshot_base(
    *,
    gx: float,
    gy: float,
    delta_core: float,
    delta_open: float,
    t_max: int,
    sticky: Dict[Coord, float] | None = None,
    boundary_bias: Dict[Coord, Tuple[str, float]] | None = None,
    case_id: str,
    name: str,
    start: Coord | None = None,
    target: Coord | None = None,
) -> CaseDef:
    N = 60
    allowed = _full_grid_allowed(N)
    extra_barriers = _screenshot_internal_walls()
    corridor_bias = _screenshot_corridor_bias(delta_core=delta_core, delta_open=delta_open)
    local_bias = corridor_bias
    if boundary_bias:
        local_bias = _merge_local_bias(local_bias, boundary_bias)
    sticky_sites = sticky or {}

    start_xy = start or (30, 50)
    target_xy = target or (30, 10)
    fast_set = {(x, y) for x in range(29, 32) for y in range(10, 51)}
    slow_set = _finalize_sets(allowed=allowed, fast_set=fast_set, start=start_xy, target=target_xy)

    return CaseDef(
        case_id=case_id,
        name=name,
        N=N,
        q=0.8,
        gx=gx,
        gy=gy,
        start=start_xy,
        target=target_xy,
        allowed=allowed,
        local_bias=local_bias,
        sticky=sticky_sites,
        doors={},
        extra_barriers=extra_barriers,
        t_max=t_max,
        fast_set=fast_set,
        slow_set=slow_set,
    )


def build_x() -> CaseDef:
    return _screenshot_base(
        case_id="X",
        name="screenshot baseline (two walls + corridor bias)",
        gx=0.0,
        gy=-0.2,
        delta_core=0.95,
        delta_open=0.6,
        t_max=6000,
    )


def build_d() -> CaseDef:
    N = 60
    sticky: Dict[Coord, float] = {}
    for x in range(1, N + 1):
        sticky[(x, 1)] = 0.2
        sticky[(x, N)] = 0.2
    for y in range(1, N + 1):
        sticky[(1, y)] = 0.2
        sticky[(N, y)] = 0.2
    return _screenshot_base(
        case_id="D",
        name="screenshot + sticky perimeter belt",
        gx=0.0,
        gy=-0.2,
        delta_core=0.95,
        delta_open=0.6,
        t_max=6000,
        sticky=sticky,
    )


def build_e() -> CaseDef:
    N = 60
    sticky: Dict[Coord, float] = {}
    for x in range(1, N + 1):
        sticky[(x, 1)] = 0.2
        sticky[(x, N)] = 0.2
    for y in range(1, N + 1):
        sticky[(1, y)] = 0.2
        sticky[(N, y)] = 0.2
    boundary_bias: Dict[Coord, Tuple[str, float]] = {}
    delta_belt = 0.1
    for x in range(1, N):
        boundary_bias[(x, 1)] = ("R", delta_belt)
    for y in range(1, N):
        boundary_bias[(N, y)] = ("D", delta_belt)
    for x in range(2, N + 1):
        boundary_bias[(x, N)] = ("L", delta_belt)
    for y in range(2, N + 1):
        boundary_bias[(1, y)] = ("U", delta_belt)
    return _screenshot_base(
        case_id="E",
        name="screenshot + sticky belt + clockwise bias",
        gx=0.0,
        gy=-0.2,
        delta_core=0.95,
        delta_open=0.6,
        t_max=5000,
        sticky=sticky,
        boundary_bias=boundary_bias,
    )


def build_y() -> CaseDef:
    return _screenshot_base(
        case_id="Y",
        name="screenshot baseline (start/target inside walls)",
        gx=0.0,
        gy=-0.2,
        delta_core=0.95,
        delta_open=0.6,
        t_max=4000,
        start=(30, 40),
        target=(30, 20),
    )


def build_z() -> CaseDef:
    return _screenshot_base(
        case_id="Z",
        name="screenshot baseline (start/target at wall endpoints)",
        gx=0.0,
        gy=-0.2,
        delta_core=0.95,
        delta_open=0.6,
        t_max=3000,
        start=(30, 45),
        target=(30, 15),
    )


def build_s() -> CaseDef:
    Nx, Ny = 18, 30
    N = max(Nx, Ny)
    allowed = {(x, y) for x in range(1, Nx + 1) for y in range(1, Ny + 1)}

    x_left = 7
    x_right = 10
    corridor_xs = range(x_left + 1, x_right + 1)  # 8..10
    y_start, y_end = 4, 27
    y0, y1 = 9, 22

    extra_barriers: set[Edge] = set()
    for y in range(y0, y1 + 1):
        extra_barriers.add(edge_key((x_left, y), (x_left + 1, y)))
        extra_barriers.add(edge_key((x_right, y), (x_right + 1, y)))

    local_bias: Dict[Coord, Tuple[str, float]] = {}
    delta_core = 0.95
    delta_open = 0.6
    for x in corridor_xs:
        for y in range(y_start, y_end + 1):
            delta = delta_core if y0 <= y <= y1 else delta_open
            local_bias[(x, y)] = ("U", delta)

    start = (9, y1)
    target = (9, y0)
    fast_set = {(x, y) for x in corridor_xs for y in range(y_start, y_end + 1)}
    slow_set = _finalize_sets(allowed=allowed, fast_set=fast_set, start=start, target=target)

    return CaseDef(
        case_id="S",
        name="small rectangle (start/target at wall endpoints)",
        N=N,
        q=0.8,
        gx=0.0,
        gy=-0.2,
        start=start,
        target=target,
        allowed=allowed,
        local_bias=local_bias,
        sticky={},
        doors={},
        extra_barriers=extra_barriers,
        t_max=2000,
        fast_set=fast_set,
        slow_set=slow_set,
    )


def build_r() -> CaseDef:
    Nx, Ny = 20, 30
    N = max(Nx, Ny)
    allowed = {(x, y) for x in range(1, Nx + 1) for y in range(1, Ny + 1)}

    x_left = 8
    x_right = 11
    corridor_xs = range(x_left + 1, x_right + 1)  # 9..11
    y_start, y_end = 4, 28
    y0, y1 = 8, 24

    extra_barriers: set[Edge] = set()
    for y in range(y0, y1 + 1):
        extra_barriers.add(edge_key((x_left, y), (x_left + 1, y)))
        extra_barriers.add(edge_key((x_right, y), (x_right + 1, y)))

    local_bias: Dict[Coord, Tuple[str, float]] = {}
    delta_core = 0.95
    delta_open = 0.6
    for x in corridor_xs:
        for y in range(y_start, y_end + 1):
            delta = delta_core if y0 <= y <= y1 else delta_open
            local_bias[(x, y)] = ("U", delta)

    start = (10, 28)
    target = (10, 4)
    fast_set = {(x, y) for x in corridor_xs for y in range(y_start, y_end + 1)}
    slow_set = _finalize_sets(allowed=allowed, fast_set=fast_set, start=start, target=target)

    return CaseDef(
        case_id="R",
        name="small rectangle baseline (two walls + corridor bias)",
        N=N,
        q=0.8,
        gx=0.0,
        gy=-0.2,
        start=start,
        target=target,
        allowed=allowed,
        local_bias=local_bias,
        sticky={},
        doors={},
        extra_barriers=extra_barriers,
        t_max=3000,
        fast_set=fast_set,
        slow_set=slow_set,
    )


def iter_cases(case_ids: Sequence[str] | None = None) -> Iterable[CaseDef]:
    builders = {
        "A": build_a,
        "B": build_b,
        "C": build_c,
        "X": build_x,
        "D": build_d,
        "E": build_e,
        "R": build_r,
        "Y": build_y,
        "Z": build_z,
        "S": build_s,
    }
    order = ("A", "B", "C", "X", "D", "E", "R", "Y", "Z", "S")
    if case_ids:
        for case_id in case_ids:
            if case_id not in builders:
                raise ValueError(f"Unknown case id: {case_id}")
            yield builders[case_id]()
        return
    for case_id in order:
        yield builders[case_id]()

