#!/usr/bin/env python3
"""Generate cases_v3.json from cases_v1.json and current candidate specs."""

from __future__ import annotations

import json
from pathlib import Path

from configs_candidates import candidate_A_spec, candidate_B_spec, candidate_C_spec


def main() -> None:
    base_path = Path(__file__).resolve().parents[1] / "config" / "cases_v1.json"
    out_path = Path(__file__).resolve().parents[1] / "config" / "cases_v3.json"
    base = json.loads(base_path.read_text(encoding="utf-8"))

    cases = []

    spec = candidate_A_spec(N=60)
    cases.append(
        {
            "id": "A",
            "name": "periodic+bias wrap-around",
            "N": spec.N,
            "q": spec.q,
            "boundary": {"x": spec.boundary_x, "y": spec.boundary_y},
            "global_bias": {"gx": spec.g_x, "gy": spec.g_y},
            "start": list(spec.start),
            "target": list(spec.target),
            "local_bias": [{"x": x, "y": y, "dir": d} for (x, y), d in spec.local_bias_arrows.items()],
            "sticky": [{"x": x, "y": y, "factor": f} for (x, y), f in spec.sticky_sites.items()],
            "barriers_reflect": [],
            "barriers_perm": [],
            "classification_rule": base["cases"][0]["classification_rule"],
        }
    )

    spec = candidate_B_spec(L=9, N=60)
    cases.append(
        {
            "id": "B",
            "name": "reflecting + biased corridor",
            "N": spec.N,
            "q": spec.q,
            "boundary": {"x": spec.boundary_x, "y": spec.boundary_y},
            "global_bias": {"gx": spec.g_x, "gy": spec.g_y},
            "start": list(spec.start),
            "target": list(spec.target),
            "local_bias": [{"x": x, "y": y, "dir": d} for (x, y), d in spec.local_bias_arrows.items()],
            "sticky": [],
            "barriers_reflect": [],
            "barriers_perm": [],
            "classification_rule": base["cases"][1]["classification_rule"],
            "corridor": {
                "y": 55,
                "x_start": min(x for x, _ in spec.local_bias_arrows),
                "x_end": max(x for x, _ in spec.local_bias_arrows),
                "direction": "left",
                "delta": spec.local_bias_delta,
            },
        }
    )

    spec = candidate_C_spec(n_bias=0, N=60)
    bar_reflect = [[list(a), list(b)] for a, b in spec.barriers_reflect]
    bar_perm = [{"edge": [list(a), list(b)], "p_pass": p} for (a, b), p in spec.barriers_perm.items()]
    cases.append(
        {
            "id": "C",
            "name": "mixed boundary + barrier/door + sticky",
            "N": spec.N,
            "q": spec.q,
            "boundary": {"x": spec.boundary_x, "y": spec.boundary_y},
            "global_bias": {"gx": spec.g_x, "gy": spec.g_y},
            "start": list(spec.start),
            "target": list(spec.target),
            "local_bias": [{"x": x, "y": y, "dir": d} for (x, y), d in spec.local_bias_arrows.items()],
            "sticky": [{"x": x, "y": y, "factor": f} for (x, y), f in spec.sticky_sites.items()],
            "barriers_reflect": bar_reflect,
            "barriers_perm": bar_perm,
            "classification_rule": base["cases"][2]["classification_rule"],
        }
    )

    payload = {
        "coordinate_system": base.get("coordinate_system", "1-based (x,y), y points downward"),
        "seed": base.get("seed", 0),
        "cases": cases,
    }
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
