#!/usr/bin/env python3
"""Generate the reflecting two-walker encounter mean-validation smoke outputs."""

from __future__ import annotations

from pathlib import Path
import json
import math

from reflecting_encounter import EncounterCase
from reflecting_encounter import assert_validation_thresholds
from reflecting_encounter import validate_case
from reflecting_encounter import write_results_csv


REPORT_DIR = Path(__file__).resolve().parents[1]
ARTIFACTS_DIR = REPORT_DIR / "artifacts"
DATA_DIR = ARTIFACTS_DIR / "data"
FIGURES_DIR = ARTIFACTS_DIR / "figures"
OUTPUTS_DIR = ARTIFACTS_DIR / "outputs"


def smoke_cases() -> list[EncounterCase]:
    return [
        EncounterCase(L=7, x1_0=1, x2_0=5, q0=0.35, rho=rho)
        for rho in (0.25, 0.5, 1.0, 2.0, 4.0)
    ]


def plot_mean_vs_rho(results, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rhos = [result.case.rho for result in results]
    means = [result.exact_mean for result in results]

    width = 720
    height = 460
    left = 84
    right = 28
    top = 44
    bottom = 74
    plot_w = width - left - right
    plot_h = height - top - bottom
    log_rhos = [math.log10(rho) for rho in rhos]
    x_min = min(log_rhos)
    x_max = max(log_rhos)
    y_min = min(means)
    y_max = max(means)
    y_pad = 0.08 * (y_max - y_min if y_max > y_min else 1.0)
    y_min -= y_pad
    y_max += y_pad

    def px(log_rho: float) -> float:
        return left + (log_rho - x_min) / (x_max - x_min) * plot_w

    def py(mean: float) -> float:
        return top + (y_max - mean) / (y_max - y_min) * plot_h

    points = [(px(x), py(y)) for x, y in zip(log_rhos, means, strict=True)]
    polyline = " ".join(f"{x:.2f},{y:.2f}" for x, y in points)
    circles = "\n".join(
        f'<circle cx="{x:.2f}" cy="{y:.2f}" r="5" fill="#255c99" />' for x, y in points
    )
    x_ticks = "\n".join(
        f'<g><line x1="{px(math.log10(rho)):.2f}" y1="{top + plot_h}" '
        f'x2="{px(math.log10(rho)):.2f}" y2="{top + plot_h + 6}" stroke="#333" />'
        f'<text x="{px(math.log10(rho)):.2f}" y="{top + plot_h + 24}" '
        f'text-anchor="middle">{rho:g}</text></g>'
        for rho in rhos
    )
    y_ticks_values = [y_min + i * (y_max - y_min) / 4.0 for i in range(5)]
    y_ticks = "\n".join(
        f'<g><line x1="{left - 6}" y1="{py(value):.2f}" x2="{left}" y2="{py(value):.2f}" '
        f'stroke="#333" /><line x1="{left}" y1="{py(value):.2f}" '
        f'x2="{left + plot_w}" y2="{py(value):.2f}" stroke="#ddd" />'
        f'<text x="{left - 10}" y="{py(value) + 4:.2f}" text-anchor="end">{value:.1f}</text></g>'
        for value in y_ticks_values
    )

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <rect width="100%" height="100%" fill="white" />
  <style>
    text {{ font-family: Arial, Helvetica, sans-serif; font-size: 14px; fill: #222; }}
    .title {{ font-size: 17px; font-weight: 600; }}
    .label {{ font-size: 15px; }}
  </style>
  <text class="title" x="{width / 2:.1f}" y="24" text-anchor="middle">Reflecting interval mean encounter validation</text>
  <rect x="{left}" y="{top}" width="{plot_w}" height="{plot_h}" fill="none" stroke="#333" />
  {y_ticks}
  {x_ticks}
  <polyline points="{polyline}" fill="none" stroke="#255c99" stroke-width="3" />
  {circles}
  <text class="label" x="{left + plot_w / 2:.1f}" y="{height - 24}" text-anchor="middle">mobility ratio rho = Q1/Q2</text>
  <text class="label" transform="translate(22 {top + plot_h / 2:.1f}) rotate(-90)" text-anchor="middle">mean encounter time E[tau_E]</text>
  <text x="{left + plot_w:.1f}" y="{top - 12}" text-anchor="end">L=7, start=(1,5), q0=0.35</text>
</svg>
"""
    path.write_text(svg, encoding="utf-8")


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

    results = [validate_case(case) for case in smoke_cases()]
    for result in results:
        assert_validation_thresholds(result)

    csv_path = DATA_DIR / "mean_vs_rho_smoke.csv"
    figure_path = FIGURES_DIR / "mean_vs_rho_smoke.svg"
    summary_path = OUTPUTS_DIR / "smoke_summary.json"

    write_results_csv(results, csv_path)
    plot_mean_vs_rho(results, figure_path)

    summary = {
        "cases": len(results),
        "csv": str(csv_path.relative_to(REPORT_DIR)),
        "figure": str(figure_path.relative_to(REPORT_DIR)),
        "max_p1_row_error": max(result.p1_row_error for result in results),
        "max_p2_row_error": max(result.p2_row_error for result in results),
        "max_mass_balance_error": max(result.mass_balance_error for result in results),
        "max_mean_difference": max(result.mean_difference for result in results),
    }
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
