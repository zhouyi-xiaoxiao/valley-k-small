#!/usr/bin/env python3
"""Generate diagonal-position decomposition smoke outputs."""

from __future__ import annotations

from pathlib import Path
import json

from reflecting_encounter import EncounterCase
from reflecting_encounter import assert_diagonal_thresholds
from reflecting_encounter import validate_diagonal_case
from reflecting_encounter import write_diagonal_contribution_csv
from reflecting_encounter import write_total_distribution_csv
from reflecting_encounter import write_window_contribution_csv


REPORT_DIR = Path(__file__).resolve().parents[1]
ARTIFACTS_DIR = REPORT_DIR / "artifacts"
DATA_DIR = ARTIFACTS_DIR / "data"
FIGURES_DIR = ARTIFACTS_DIR / "figures"
OUTPUTS_DIR = ARTIFACTS_DIR / "outputs"


def representative_case() -> EncounterCase:
    return EncounterCase(L=7, x1_0=1, x2_0=5, q0=0.35, rho=4.0)


def _color(value: float, max_value: float) -> str:
    if max_value <= 0.0:
        return "#f7fbff"
    z = min(max(float(value) / float(max_value), 0.0), 1.0)
    # Blue-to-red sequential ramp with enough contrast for low mass cells.
    r = int(247 * (1.0 - z) + 178 * z)
    g = int(251 * (1.0 - z) + 24 * z)
    b = int(255 * (1.0 - z) + 43 * z)
    return f"#{r:02x}{g:02x}{b:02x}"


def write_heatmap_svg(result, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    width = 940
    height = 430
    left = 74
    right = 38
    top = 54
    bottom = 74
    plot_w = width - left - right
    plot_h = height - top - bottom
    L = result.case.L
    n_t = int(result.times.size)
    cell_w = plot_w / max(n_t, 1)
    cell_h = plot_h / max(L, 1)
    max_value = float(result.f_by_position.max()) if result.f_by_position.size else 0.0

    rects: list[str] = []
    for ti in range(n_t):
        x = left + ti * cell_w
        for k in range(L):
            y = top + (L - 1 - k) * cell_h
            rects.append(
                f'<rect x="{x:.2f}" y="{y:.2f}" width="{cell_w + 0.25:.2f}" '
                f'height="{cell_h + 0.25:.2f}" fill="{_color(result.f_by_position[ti, k], max_value)}" />'
            )

    x_ticks = []
    for frac in (0.0, 0.25, 0.5, 0.75, 1.0):
        idx = min(n_t - 1, max(0, round(frac * (n_t - 1)))) if n_t else 0
        t = int(result.times[idx]) if n_t else 0
        x = left + frac * plot_w
        x_ticks.append(
            f'<g><line x1="{x:.2f}" y1="{top + plot_h}" x2="{x:.2f}" '
            f'y2="{top + plot_h + 6}" stroke="#333" />'
            f'<text x="{x:.2f}" y="{top + plot_h + 25}" text-anchor="middle">{t}</text></g>'
        )

    y_ticks = []
    for k in range(L):
        y = top + (L - 1 - k + 0.5) * cell_h
        y_ticks.append(
            f'<g><line x1="{left - 6}" y1="{y:.2f}" x2="{left}" y2="{y:.2f}" '
            f'stroke="#333" /><text x="{left - 12}" y="{y + 5:.2f}" text-anchor="end">{k}</text></g>'
        )

    legend_x = width - right - 130
    legend_y = top - 22
    legend = "\n".join(
        f'<rect x="{legend_x + i * 13}" y="{legend_y}" width="13" height="12" '
        f'fill="{_color(i / 9.0 * max_value, max_value)}" />'
        for i in range(10)
    )

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <rect width="100%" height="100%" fill="white" />
  <style>
    text {{ font-family: Arial, Helvetica, sans-serif; font-size: 14px; fill: #222; }}
    .title {{ font-size: 17px; font-weight: 600; }}
    .label {{ font-size: 15px; }}
  </style>
  <text class="title" x="{width / 2:.1f}" y="26" text-anchor="middle">Diagonal encounter contribution heatmap</text>
  <text x="{left}" y="47">L={result.case.L}, start=({result.case.x1_0},{result.case.x2_0}), rho={result.case.rho:g}, q0={result.case.q0:g}</text>
  <rect x="{left}" y="{top}" width="{plot_w}" height="{plot_h}" fill="none" stroke="#333" />
  {''.join(rects)}
  <rect x="{left}" y="{top}" width="{plot_w}" height="{plot_h}" fill="none" stroke="#333" />
  {''.join(x_ticks)}
  {''.join(y_ticks)}
  <text class="label" x="{left + plot_w / 2:.1f}" y="{height - 24}" text-anchor="middle">time t</text>
  <text class="label" transform="translate(22 {top + plot_h / 2:.1f}) rotate(-90)" text-anchor="middle">encounter position k</text>
  {legend}
  <text x="{legend_x}" y="{legend_y - 7}">low</text>
  <text x="{legend_x + 130}" y="{legend_y - 7}" text-anchor="end">high f_k(t)</text>
</svg>
"""
    path.write_text(svg, encoding="utf-8")


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

    result = validate_diagonal_case(representative_case())
    assert_diagonal_thresholds(result)

    total_csv = DATA_DIR / "diagonal_asymmetric_f_total.csv"
    contribution_csv = DATA_DIR / "diagonal_asymmetric_f_by_position.csv"
    windows_csv = DATA_DIR / "diagonal_asymmetric_windows.csv"
    heatmap = FIGURES_DIR / "diagonal_asymmetric_heatmap.svg"
    summary_path = OUTPUTS_DIR / "diagonal_smoke_summary.json"

    write_total_distribution_csv(result, total_csv)
    write_diagonal_contribution_csv(result, contribution_csv)
    write_window_contribution_csv(result, windows_csv)
    write_heatmap_svg(result, heatmap)

    summary = {
        "case": {
            "L": result.case.L,
            "x1_0": result.case.x1_0,
            "x2_0": result.case.x2_0,
            "q0": result.case.q0,
            "rho": result.case.rho,
            "Q1": result.Q1,
            "Q2": result.Q2,
        },
        "distribution_steps": int(result.times[-1]),
        "total_csv": str(total_csv.relative_to(REPORT_DIR)),
        "contribution_csv": str(contribution_csv.relative_to(REPORT_DIR)),
        "windows_csv": str(windows_csv.relative_to(REPORT_DIR)),
        "heatmap": str(heatmap.relative_to(REPORT_DIR)),
        "mass_balance_error": result.mass_balance_error,
        "diagonal_decomposition_error": result.decomposition_error,
        "tail_mass": result.tail_mass,
        "window_names": [window.name for window in result.windows],
    }
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
