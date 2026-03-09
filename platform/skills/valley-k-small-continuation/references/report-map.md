# Report Map

Use this map to jump directly to the correct entry script and build command family.

| report_id | folder | primary entry | build notes |
| --- | --- | --- | --- |
| `ring_valley` | `research/reports/ring_valley` | `python3 code/valley_study.py` | single-language TeX (`manuscript/ring_valley.tex`) |
| `ring_valley_dst` | `research/reports/ring_valley_dst` | `python3 code/bimodality_flux_scan.py` / `python3 code/dst_shortcut_usage_mc.py` | CN uses `xelatex`; EN uses `pdf` |
| `ring_lazy_flux` | `research/reports/ring_lazy_flux` | report-specific scripts under `code/` (see report README) | CN/EN pair in `manuscript/` |
| `ring_lazy_jump` | `research/reports/ring_lazy_jump` | `python3 code/jumpover_bimodality_pipeline.py` | CN/EN pair |
| `ring_lazy_jump_ext` | `research/reports/ring_lazy_jump_ext` | beta/N sweeps in `code/` (`beta_sweep_peaks_tail.py`, `N_sweep_peaks_tail.py`, MC class sweeps) | follow `notes/readme_ext.md` |
| `ring_lazy_jump_ext_rev2` | `research/reports/ring_lazy_jump_ext_rev2` | `make fig2`, `make sensitivity`, `make pdf` | follow `notes/readme_rev.md` |
| `ring_two_target` | `research/reports/ring_two_target` | `python3 code/two_target_report.py` | CN `xelatex`, EN `pdf` |
| `ring_deriv_k2` | `research/reports/ring_deriv_k2` | derivation-oriented TeX workflow | single-language with supplementary notes in `manuscript/extras/` |
| `grid2d_bimodality` | `research/reports/grid2d_bimodality` | `python3 code/bimodality_2d_pipeline.py` | CN/EN pair; config available via compatibility link `config/` |
| `grid2d_reflecting_bimodality` | `research/reports/grid2d_reflecting_bimodality` | `python3 code/reflecting_bimodality_pipeline.py` | CN/EN pair |
| `grid2d_blackboard_bimodality` | `research/reports/grid2d_blackboard_bimodality` | `python3 code/blackboard_bimodality_pipeline.py` (+ `z_scan.py`) | CN/EN pair |
| `grid2d_two_target_double_peak` | `research/reports/grid2d_two_target_double_peak` | `python3 code/two_target_2d_report.py` + `python3 code/compare_numeric_methods.py` | CN/EN main + extras in `manuscript/extras/` |
| `grid2d_rect_bimodality` | `research/reports/grid2d_rect_bimodality` | `python3 code/rect_bimodality_report.py` | `--quick` available for smoke run |
| `cross_luca_regime_map` | `research/reports/cross_luca_regime_map` | `build_manifest.py` -> `run_regime_scan.py` -> `plot_regime_figures.py` -> `write_regime_report.py` | fixed-horizon full-FPT fairness protocol |

## Unified wrappers
- List reports: `python3 scripts/reportctl.py list`
- Resolve one report: `python3 scripts/reportctl.py resolve --report <id>`
- Run inside report dir: `python3 scripts/reportctl.py run --report <id> -- <cmd>`
- Build main report by language: `python3 scripts/reportctl.py build --report <id> --lang <cn|en>`
