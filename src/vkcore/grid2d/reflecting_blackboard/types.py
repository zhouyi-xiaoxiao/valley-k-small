from __future__ import annotations

from typing import Dict, Tuple

Coord = Tuple[int, int]
Edge = Tuple[Coord, Coord]
LocalBias = Dict[Coord, Tuple[str, float]]
