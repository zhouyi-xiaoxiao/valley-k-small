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
    "R1": "R1_dual_corridor_U_top.json",
    "R2": "R2_big_rectangle_detour.json",
    "R3": "R3_sticky_segment_on_slow_branch.json",
    "R4": "R4_internal_branch_boundary_loop.json",
    "R5": "R5_vertical_short_vs_left_detour.json",
    "R6": "R6_parallel_lanes_lower_has_many_doors.json",
    "R7": "R7_membrane_pore_detour.json",
    "C3": "C3_local_active_track_detour.json",
    "MB1": "MB1_parallel_lanes_slow_lane_is_sticky.json",
    "MB2": "MB2_parallel_lanes_slow_lane_has_10_doors.json",
    "MB3": "MB3_parallel_lanes_short_sticky_segment.json",
    "NB1": "NB1_boundary_layer_short_sticky.json",
    "NB2": "NB2_boundary_layer_sticky_strip.json",
    "NB3": "NB3_boundary_layer_sticky_strip_bias.json",
    "NB4": "NB4_perimeter_clockwise_belt.json",
    "NB5": "NB5_perimeter_clockwise_belt_gbias.json",
    "S1": "S1_soft_two_tracks_minbarrier0.json",
    "S2": "S2_soft_two_tracks_turn_y10.json",
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
    t_max: int
    fast_set: set[Coord]
    slow_set: set[Coord]


# ---- Case builders ----

def _finalize_sets(*, allowed: set[Coord], fast_set: set[Coord], start: Coord, target: Coord) -> set[Coord]:
    slow_set = allowed.difference(fast_set)
    slow_set.discard(start)
    slow_set.discard(target)
    return slow_set


def build_r1() -> CaseDef:
    N = 60
    allowed: set[Coord] = set()
    add_segment(allowed, 10, 30, 50, 30)
    add_segment(allowed, 10, 30, 10, 1)
    add_segment(allowed, 10, 1, 50, 1)
    add_segment(allowed, 50, 1, 50, 30)

    local_bias: Dict[Coord, Tuple[str, float]] = {(10, 30): ("U", 0.6)}
    for x in range(11, 50):
        local_bias[(x, 30)] = ("R", 0.95)
    for y in range(2, 30):
        local_bias[(10, y)] = ("U", 0.95)
    for x in range(10, 50):
        local_bias[(x, 1)] = ("R", 0.95)
    for y in range(1, 30):
        local_bias[(50, y)] = ("D", 0.95)

    fast_set = {(x, 30) for x in range(10, 51)}
    slow_set = _finalize_sets(allowed=allowed, fast_set=fast_set, start=(10, 30), target=(50, 30))

    return CaseDef(
        case_id="R1",
        name="dual corridor with top U-shaped detour",
        N=N,
        q=0.8,
        gx=-0.2,
        gy=0.0,
        start=(10, 30),
        target=(50, 30),
        allowed=allowed,
        local_bias=local_bias,
        sticky={},
        doors={},
        t_max=1500,
        fast_set=fast_set,
        slow_set=slow_set,
    )


def build_r2() -> CaseDef:
    N = 60
    allowed: set[Coord] = set()
    add_segment(allowed, 10, 10, 50, 10)
    add_segment(allowed, 10, 10, 10, 50)
    add_segment(allowed, 10, 50, 50, 50)
    add_segment(allowed, 50, 50, 50, 10)

    local_bias: Dict[Coord, Tuple[str, float]] = {(10, 10): ("D", 0.6)}
    for x in range(11, 50):
        local_bias[(x, 10)] = ("R", 0.95)
    for y in range(11, 50):
        local_bias[(10, y)] = ("D", 0.95)
    for x in range(10, 50):
        local_bias[(x, 50)] = ("R", 0.95)
    for y in range(11, 51):
        local_bias[(50, y)] = ("U", 0.95)

    fast_set = {(x, 10) for x in range(10, 51)}
    slow_set = _finalize_sets(allowed=allowed, fast_set=fast_set, start=(10, 10), target=(50, 10))

    return CaseDef(
        case_id="R2",
        name="short top edge vs large rectangular detour",
        N=N,
        q=0.8,
        gx=-0.2,
        gy=0.0,
        start=(10, 10),
        target=(50, 10),
        allowed=allowed,
        local_bias=local_bias,
        sticky={},
        doors={},
        t_max=2000,
        fast_set=fast_set,
        slow_set=slow_set,
    )


def build_r3() -> CaseDef:
    case = build_r1()
    sticky: Dict[Coord, float] = {}
    for x in range(30, 41):
        sticky[(x, 1)] = 0.6
        case.local_bias.pop((x, 1), None)
    case.case_id = "R3"
    case.name = "sticky segment on slow branch"
    case.sticky = sticky
    case.t_max = 2000
    return case


def build_r4() -> CaseDef:
    N = 60
    allowed: set[Coord] = set()
    add_segment(allowed, 10, 30, 50, 30)
    add_segment(allowed, 30, 30, 30, 60)
    add_segment(allowed, 30, 60, 50, 60)
    add_segment(allowed, 50, 60, 50, 30)

    local_bias: Dict[Coord, Tuple[str, float]] = {(30, 30): ("D", 0.6)}
    for x in range(11, 50):
        if x == 30:
            continue
        local_bias[(x, 30)] = ("R", 0.95)
    for y in range(31, 60):
        local_bias[(30, y)] = ("D", 0.95)
    for x in range(30, 50):
        local_bias[(x, 60)] = ("R", 0.95)
    for y in range(31, 61):
        local_bias[(50, y)] = ("U", 0.95)

    fast_set = {(x, 30) for x in range(10, 51)}
    slow_set = _finalize_sets(allowed=allowed, fast_set=fast_set, start=(10, 30), target=(50, 30))

    return CaseDef(
        case_id="R4",
        name="mid-route branching with boundary loop",
        N=N,
        q=0.8,
        gx=-0.25,
        gy=0.0,
        start=(10, 30),
        target=(50, 30),
        allowed=allowed,
        local_bias=local_bias,
        sticky={},
        doors={},
        t_max=2000,
        fast_set=fast_set,
        slow_set=slow_set,
    )


def build_r5() -> CaseDef:
    N = 60
    allowed: set[Coord] = set()
    add_segment(allowed, 30, 50, 30, 10)
    add_segment(allowed, 30, 50, 1, 50)
    add_segment(allowed, 1, 50, 1, 10)
    add_segment(allowed, 1, 10, 30, 10)

    local_bias: Dict[Coord, Tuple[str, float]] = {(30, 50): ("L", 0.6)}
    for y in range(11, 50):
        local_bias[(30, y)] = ("U", 0.95)
    for x in range(2, 30):
        local_bias[(x, 50)] = ("L", 0.95)
    for y in range(11, 51):
        local_bias[(1, y)] = ("U", 0.95)
    for x in range(1, 30):
        local_bias[(x, 10)] = ("R", 0.95)

    fast_set = {(30, y) for y in range(10, 51)}
    slow_set = _finalize_sets(allowed=allowed, fast_set=fast_set, start=(30, 50), target=(30, 10))

    return CaseDef(
        case_id="R5",
        name="rotated variant (vertical shortcut)",
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
        t_max=2000,
        fast_set=fast_set,
        slow_set=slow_set,
    )


def build_r6() -> CaseDef:
    N = 60
    allowed: set[Coord] = set()
    add_segment(allowed, 10, 30, 10, 20)
    add_segment(allowed, 10, 30, 10, 40)
    add_segment(allowed, 10, 20, 50, 20)
    add_segment(allowed, 10, 40, 50, 40)
    add_segment(allowed, 50, 20, 50, 30)
    add_segment(allowed, 50, 40, 50, 30)

    local_bias: Dict[Coord, Tuple[str, float]] = {}
    for x in range(11, 50):
        local_bias[(x, 20)] = ("R", 0.95)
        local_bias[(x, 40)] = ("R", 0.95)
    for y in range(21, 30):
        local_bias[(10, y)] = ("U", 0.6)
    for y in range(31, 40):
        local_bias[(10, y)] = ("D", 0.6)
    for y in range(21, 30):
        local_bias[(50, y)] = ("D", 0.6)
    for y in range(31, 40):
        local_bias[(50, y)] = ("U", 0.6)

    doors: Dict[Edge, float] = {}
    for x in range(10, 50):
        a = (x, 40)
        b = (x + 1, 40)
        doors[edge_key(a, b)] = 0.1

    fast_set = {(x, 20) for x in range(10, 51)}
    slow_set = {(x, 40) for x in range(10, 51)}

    return CaseDef(
        case_id="R6",
        name="parallel lanes with door array slowdown",
        N=N,
        q=0.8,
        gx=0.0,
        gy=0.0,
        start=(10, 30),
        target=(50, 30),
        allowed=allowed,
        local_bias=local_bias,
        sticky={},
        doors=doors,
        t_max=12000,
        fast_set=fast_set,
        slow_set=slow_set,
    )


def build_r7() -> CaseDef:
    N = 60
    allowed: set[Coord] = set()
    add_segment(allowed, 10, 30, 50, 30)
    add_segment(allowed, 29, 30, 29, 1)
    add_segment(allowed, 29, 1, 31, 1)
    add_segment(allowed, 31, 1, 31, 30)

    delta = 0.95
    local_bias: Dict[Coord, Tuple[str, float]] = {}
    for x in range(10, 51):
        if x == 29:
            continue
        local_bias[(x, 30)] = ("R", delta)
    for y in range(2, 30):
        local_bias[(29, y)] = ("U", delta)
    for x in range(29, 31):
        local_bias[(x, 1)] = ("R", delta)
    for y in range(1, 30):
        local_bias[(31, y)] = ("D", delta)

    doors: Dict[Edge, float] = {edge_key((30, 30), (31, 30)): 0.8}

    fast_set = {(x, 30) for x in range(10, 51)}
    slow_set = _finalize_sets(allowed=allowed, fast_set=fast_set, start=(10, 30), target=(50, 30))

    return CaseDef(
        case_id="R7",
        name="semipermeable pore shortcut vs long detour",
        N=N,
        q=0.8,
        gx=-0.2,
        gy=0.0,
        start=(10, 30),
        target=(50, 30),
        allowed=allowed,
        local_bias=local_bias,
        sticky={},
        doors=doors,
        t_max=2000,
        fast_set=fast_set,
        slow_set=slow_set,
    )


def build_c3() -> CaseDef:
    N = 60
    allowed: set[Coord] = set()
    add_segment(allowed, 10, 29, 50, 29)
    add_segment(allowed, 10, 30, 10, 60)
    add_segment(allowed, 10, 60, 50, 60)
    add_segment(allowed, 50, 60, 50, 30)

    delta_track = 0.95
    delta_detour = 0.55
    local_bias: Dict[Coord, Tuple[str, float]] = {}
    for x in range(10, 51):
        local_bias[(x, 29)] = ("R", delta_track)
    for y in range(31, 60):
        local_bias[(10, y)] = ("D", delta_detour)
    for x in range(10, 50):
        local_bias[(x, 60)] = ("R", delta_detour)
    for y in range(31, 61):
        local_bias[(50, y)] = ("U", delta_detour)
    local_bias[(10, 30)] = ("D", 0.35)
    local_bias[(50, 60)] = ("U", delta_detour)

    fast_set = {(x, 29) for x in range(10, 51)}
    slow_set = _finalize_sets(allowed=allowed, fast_set=fast_set, start=(10, 30), target=(50, 30))

    return CaseDef(
        case_id="C3",
        name="local active track vs long detour loop",
        N=N,
        q=0.8,
        gx=-0.15,
        gy=0.0,
        start=(10, 30),
        target=(50, 30),
        allowed=allowed,
        local_bias=local_bias,
        sticky={},
        doors={},
        t_max=3000,
        fast_set=fast_set,
        slow_set=slow_set,
    )


def _build_minbias_two_lanes(
    *,
    case_id: str,
    name: str,
    sticky: Dict[Coord, float],
    doors: Dict[Edge, float],
    t_max: int,
) -> CaseDef:
    N = 60
    allowed: set[Coord] = set()
    add_segment(allowed, 1, 30, 50, 30)
    add_segment(allowed, 1, 32, 50, 32)
    add_segment(allowed, 1, 30, 1, 32)
    add_segment(allowed, 50, 30, 50, 32)

    fast_set = {(x, 30) for x in range(1, 51)}
    slow_set = {(x, 32) for x in range(1, 51)}

    return CaseDef(
        case_id=case_id,
        name=name,
        N=N,
        q=0.8,
        gx=-0.5,
        gy=0.0,
        start=(1, 31),
        target=(50, 30),
        allowed=allowed,
        local_bias={},
        sticky=sticky,
        doors=doors,
        t_max=t_max,
        fast_set=fast_set,
        slow_set=slow_set,
    )


def build_mb1() -> CaseDef:
    sticky = {(x, 32): 0.2 for x in range(1, 51)}
    return _build_minbias_two_lanes(
        case_id="MB1",
        name="parallel lanes with sticky slow lane",
        sticky=sticky,
        doors={},
        t_max=5000,
    )


def build_mb2() -> CaseDef:
    doors: Dict[Edge, float] = {}
    for x in range(10, 20):
        doors[edge_key((x, 32), (x + 1, 32))] = 0.03
    return _build_minbias_two_lanes(
        case_id="MB2",
        name="parallel lanes with 10 doors on slow lane",
        sticky={},
        doors=doors,
        t_max=12000,
    )


def build_mb3() -> CaseDef:
    sticky = {(x, 32): 0.05 for x in range(15, 27)}
    return _build_minbias_two_lanes(
        case_id="MB3",
        name="parallel lanes with short sticky segment",
        sticky=sticky,
        doors={},
        t_max=11000,
    )


def _full_grid_allowed(N: int) -> set[Coord]:
    return {(x, y) for x in range(1, N + 1) for y in range(1, N + 1)}


def _build_nobarrier_case(
    *,
    case_id: str,
    name: str,
    sticky: Dict[Coord, float],
    local_bias: Dict[Coord, Tuple[str, float]],
    t_max: int,
) -> CaseDef:
    N = 60
    allowed = _full_grid_allowed(N)
    slow_set = set(sticky)
    fast_set = allowed.difference(slow_set)
    return CaseDef(
        case_id=case_id,
        name=name,
        N=N,
        q=0.8,
        gx=0.0,
        gy=0.4,
        start=(50, 60),
        target=(42, 60),
        allowed=allowed,
        local_bias=local_bias,
        sticky=sticky,
        doors={},
        t_max=t_max,
        fast_set=fast_set,
        slow_set=slow_set,
    )


def build_nb1() -> CaseDef:
    sticky = {(x, 59): 0.02 for x in range(47, 51)}
    return _build_nobarrier_case(
        case_id="NB1",
        name="boundary-layer slowdown with short sticky strip",
        sticky=sticky,
        local_bias={},
        t_max=20000,
    )


def build_nb2() -> CaseDef:
    sticky = {(x, 59): 0.02 for x in range(43, 51)}
    return _build_nobarrier_case(
        case_id="NB2",
        name="boundary-layer slowdown with longer sticky strip",
        sticky=sticky,
        local_bias={},
        t_max=20000,
    )


def build_nb3() -> CaseDef:
    sticky = {(x, 59): 0.02 for x in range(43, 51)}
    local_bias = {(x, 60): ("L", 0.7) for x in range(43, 51)}
    return _build_nobarrier_case(
        case_id="NB3",
        name="boundary-layer sticky strip with mild local bias",
        sticky=sticky,
        local_bias=local_bias,
        t_max=20000,
    )


def _build_perimeter_belt_case(
    *,
    case_id: str,
    name: str,
    gx: float,
    gy: float,
) -> CaseDef:
    N = 60
    allowed = _full_grid_allowed(N)
    sticky: Dict[Coord, float] = {}
    local_bias: Dict[Coord, Tuple[str, float]] = {}

    for x in range(1, N + 1):
        sticky[(x, 1)] = 0.2
        sticky[(x, N)] = 0.2
        if x < N:
            local_bias[(x, N)] = ("R", 0.63)
        if x > 1:
            local_bias[(x, 1)] = ("L", 0.63)
    for y in range(1, N + 1):
        sticky[(1, y)] = 0.2
        sticky[(N, y)] = 0.2
        if y > 1:
            local_bias[(N, y)] = ("U", 0.63)
        if y < N:
            local_bias[(1, y)] = ("D", 0.63)

    local_bias[(1, N)] = ("R", 0.63)
    local_bias[(N, N)] = ("U", 0.63)
    local_bias[(N, 1)] = ("L", 0.63)
    local_bias[(1, 1)] = ("D", 0.63)

    slow_set = {(x, 1) for x in range(1, N + 1)}
    fast_set = allowed.difference(slow_set)
    slow_set.discard((12, 60))
    slow_set.discard((10, 60))

    return CaseDef(
        case_id=case_id,
        name=name,
        N=N,
        q=0.8,
        gx=gx,
        gy=gy,
        start=(12, 60),
        target=(10, 60),
        allowed=allowed,
        local_bias=local_bias,
        sticky=sticky,
        doors={},
        t_max=20000,
        fast_set=fast_set,
        slow_set=slow_set,
    )


def build_nb4() -> CaseDef:
    return _build_perimeter_belt_case(
        case_id="NB4",
        name="perimeter clockwise belt (boundary-only sticky + bias)",
        gx=0.0,
        gy=0.0,
    )


def build_nb5() -> CaseDef:
    return _build_perimeter_belt_case(
        case_id="NB5",
        name="perimeter belt with global bias (boundary-only sticky + bias)",
        gx=-0.1,
        gy=0.0,
    )


def _build_soft_two_tracks(
    *,
    case_id: str,
    name: str,
    turn_y: int,
    slow_delta: float,
) -> CaseDef:
    N = 60
    allowed = _full_grid_allowed(N)
    local_bias: Dict[Coord, Tuple[str, float]] = {}
    sticky: Dict[Coord, float] = {}

    # Fast track: short horizontal lane.
    for x in range(11, 50):
        local_bias[(x, 30)] = ("R", 0.95)
        sticky[(x, 30)] = 0.05

    # Slow detour: up -> right -> down, with weaker bias.
    for y in range(turn_y + 1, 31):
        local_bias[(10, y)] = ("U", slow_delta)
        sticky[(10, y)] = 0.05
    for x in range(10, 50):
        local_bias[(x, turn_y)] = ("R", slow_delta)
        sticky[(x, turn_y)] = 0.05
    for y in range(turn_y, 30):
        local_bias[(50, y)] = ("D", slow_delta)
        sticky[(50, y)] = 0.05

    fast_set = {(x, 30) for x in range(10, 51)}
    slow_set = {(x, turn_y) for x in range(10, 51)}

    return CaseDef(
        case_id=case_id,
        name=name,
        N=N,
        q=0.8,
        gx=0.0,
        gy=0.0,
        start=(10, 30),
        target=(50, 30),
        allowed=allowed,
        local_bias=local_bias,
        sticky=sticky,
        doors={},
        t_max=8000,
        fast_set=fast_set,
        slow_set=slow_set,
    )


def build_s1() -> CaseDef:
    return _build_soft_two_tracks(
        case_id="S1",
        name="soft two tracks without barriers (turn at y=1)",
        turn_y=1,
        slow_delta=0.3,
    )


def build_s2() -> CaseDef:
    return _build_soft_two_tracks(
        case_id="S2",
        name="soft two tracks without barriers (turn at y=10)",
        turn_y=10,
        slow_delta=0.2,
    )


def iter_cases(case_ids: Sequence[str] | None = None) -> Iterable[CaseDef]:
    builders = {
        "R1": build_r1,
        "R2": build_r2,
        "R3": build_r3,
        "R4": build_r4,
        "R5": build_r5,
        "R6": build_r6,
        "R7": build_r7,
        "C3": build_c3,
        "MB1": build_mb1,
        "MB2": build_mb2,
        "MB3": build_mb3,
        "NB1": build_nb1,
        "NB2": build_nb2,
        "NB3": build_nb3,
        "NB4": build_nb4,
        "NB5": build_nb5,
        "S1": build_s1,
        "S2": build_s2,
    }
    order = (
        "R1",
        "R2",
        "R3",
        "R4",
        "R5",
        "R6",
        "R7",
        "C3",
        "MB1",
        "MB2",
        "MB3",
        "NB1",
        "NB2",
        "NB3",
        "NB4",
        "NB5",
        "S1",
        "S2",
    )
    if case_ids:
        for case_id in case_ids:
            if case_id not in builders:
                raise ValueError(f"Unknown case id: {case_id}")
            yield builders[case_id]()
        return
    for case_id in order:
        yield builders[case_id]()

