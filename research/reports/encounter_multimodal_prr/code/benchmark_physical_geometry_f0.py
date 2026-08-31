"""Control-blind benchmark for all 12 frozen v2 physical geometries."""

from __future__ import annotations

import argparse
import gc
import json
import math
import time
from fractions import Fraction
from typing import Any

import rate_defined_tensor_f0 as f0


def _mass_width(profile: f0.NormalizedBumpProfile) -> float:
    return float(
        sum(
            (entry.upper_fraction - entry.lower_fraction for entry in profile.mass_intervals),
            Fraction(0),
        )
    )


def _contact_area_bounds(
    geometry: f0.PhysicalConfigurationGeometryV2,
) -> tuple[Fraction, Fraction]:
    relative, transverse = geometry.axes[1:]
    lower = Fraction(0)
    upper = Fraction(0)
    for index, entry in enumerate(geometry.contact_fractions_relative):
        volume = (
            relative.cell_volumes[index // transverse.size]
            * transverse.cell_volumes[index % transverse.size]
        )
        lower += entry.lower_fraction * volume
        upper += entry.upper_fraction * volume
    return lower, upper


def run(*, panels_per_unit: int, precision_bits: int) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    total_start = time.perf_counter()
    for spec in f0.physical_configuration_specs_v2():
        row_start = time.perf_counter()
        geometry = f0.build_physical_geometry_v2(
            spec,
            panels_per_unit=panels_per_unit,
            precision_bits=precision_bits,
        )
        geometry.validate()
        area_lower, area_upper = _contact_area_bounds(geometry)
        area_oracle = math.pi * float(geometry.parameters.contact_radius) ** 2
        if not float(area_lower) <= area_oracle <= float(area_upper):
            raise RuntimeError("contact-area interval missed the independent pi*r^2 diagnostic")
        rows.append(
            {
                "label": spec.label,
                "shape": [axis.size for axis in geometry.axes],
                "states": spec.expected_states,
                "seconds": time.perf_counter() - row_start,
                "maximum_support_mass_interval_width": max(
                    _mass_width(profile) for profile in geometry.support_profiles
                ),
                "maximum_initial_marginal_interval_width": max(
                    _mass_width(profile) for profile in geometry.initial_profiles
                ),
                "contact_area_interval_width": float(area_upper - area_lower),
                "contact_area_oracle_contained": True,
                "installed_budget_relative_radius_exact": "0/1",
            }
        )
        del geometry
        gc.collect()
    return {
        "stage": "rate_defined_tensor_f0_control_blind_geometry_benchmark",
        "status": "PASS_F0_CONTROL_BLIND_GEOMETRY_METHOD_ONLY",
        "authorized_scientific_command": None,
        "prospective_control_values_read": False,
        "positive_budget_primary_control_evaluated": False,
        "precision_bits": precision_bits,
        "panels_per_unit": panels_per_unit,
        "configuration_order": list(f0.PHYSICAL_CONFIGURATION_ORDER_V2),
        "configuration_count": len(rows),
        "one_control_base_state_workload": sum(row["states"] for row in rows),
        "total_seconds": time.perf_counter() - total_start,
        "rows": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--science-free-control-blind", action="store_true")
    parser.add_argument("--panels-per-unit", type=int, default=16_384)
    parser.add_argument("--precision-bits", type=int, default=192)
    args = parser.parse_args()
    if not args.science_free_control_blind:
        raise SystemExit("explicit --science-free-control-blind is required")
    payload = run(
        panels_per_unit=args.panels_per_unit,
        precision_bits=args.precision_bits,
    )
    print(json.dumps(payload, allow_nan=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
