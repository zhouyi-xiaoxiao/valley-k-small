from __future__ import annotations

from . import _bimodality_flux_scan as _flux
from . import _dst_shortcut_usage_mc as _dst
from . import _second_peak_scan as _scan
from . import _second_peak_shortcut_usage_mc as _sp

# Re-export plotting helpers used by report-local tooling.
plot_bimodality_scan = _flux.plot_bimodality_scan
plot_peak_times = _flux.plot_peak_times
plot_example_curves = _flux.plot_example_curves
plot_aw_vs_flux_overlay = _flux.plot_aw_vs_flux_overlay

plot_peak2_scan = _dst.plot_peak2_scan
plot_peak_times_scan = _dst.plot_peak_times_scan
plot_exact_gallery = _dst.plot_exact_gallery
plot_crossing_fractions = _dst.plot_crossing_fractions

plot_peak2_vs_x = _scan.plot_peak2_vs_x
plot_peak_times_vs_x = _scan.plot_peak_times_vs_x
plot_examples = _scan.plot_examples

plot_exact_gallery_second_peak = _sp.plot_exact_gallery
plot_crossing_fractions_second_peak = _sp.plot_crossing_fractions
