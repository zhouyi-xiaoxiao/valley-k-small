# Report Map

Use this map to jump directly to the correct entry script and build command family.

| report_id | folder | primary entry | build notes |
| --- | --- | --- | --- |
| `ring_valley` | `research/reports/ring_valley` | `python3 scripts/reportctl.py run --report ring_valley -- python3 code/valley_study.py` | single-language TeX (`manuscript/ring_valley.tex`) |
| `ring_valley_dst` | `research/reports/ring_valley_dst` | `python3 scripts/reportctl.py run --report ring_valley_dst -- python3 code/bimodality_flux_scan.py` | CN uses `xelatex`; EN uses `pdf`; extra diagnostics also live under `code/` |
| `ring_lazy_flux` | `research/reports/ring_lazy_flux` | `python3 scripts/reportctl.py run --report ring_lazy_flux -- python3 code/lazy_ring_flux_bimodality.py` | CN/EN pair in `manuscript/`; see report README for auxiliary scripts |
| `ring_lazy_jump` | `research/reports/ring_lazy_jump` | `python3 scripts/reportctl.py run --report ring_lazy_jump -- python3 code/jumpover_bimodality_pipeline.py` | CN/EN pair |
| `ring_lazy_jump_ext` | `research/reports/ring_lazy_jump_ext` | `python3 scripts/reportctl.py run --report ring_lazy_jump_ext -- python3 code/jumpover_bimodality_pipeline.py` | beta/N sweeps and MC class sweeps are documented in `notes/readme_ext.md` |
| `ring_lazy_jump_ext_rev2` | `research/reports/ring_lazy_jump_ext_rev2` | `python3 scripts/reportctl.py run --report ring_lazy_jump_ext_rev2 -- python3 code/jumpover_bimodality_pipeline.py` | use `code/plot_fig2_overlap_binbars.py` for Fig.2 helper outputs; see `notes/readme_rev.md` |
| `ring_two_target` | `research/reports/ring_two_target` | `python3 scripts/reportctl.py run --report ring_two_target -- python3 code/two_target_report.py` | CN `xelatex`, EN `pdf` |
| `ring_two_walker_encounter_shortcut` | `research/reports/ring_two_walker_encounter_shortcut` | `python3 scripts/reportctl.py run --report ring_two_walker_encounter_shortcut -- python3 code/two_walker_ring_encounter_report.py` | CN/EN pair plus continuous optimize helper under `code/continuous_optimize_loop.py` |
| `ring_deriv_k2` | `research/reports/ring_deriv_k2` | `python3 scripts/reportctl.py build --report ring_deriv_k2 --lang en` | single-language with supplementary notes in `manuscript/extras/` |
| `grid2d_bimodality` | `research/reports/grid2d_bimodality` | `python3 scripts/reportctl.py run --report grid2d_bimodality -- python3 code/bimodality_2d_pipeline.py` | CN/EN pair; canonical configs live under `code/config/` |
| `grid2d_reflecting_bimodality` | `research/reports/grid2d_reflecting_bimodality` | `python3 scripts/reportctl.py run --report grid2d_reflecting_bimodality -- python3 code/reflecting_bimodality_pipeline.py` | CN/EN pair |
| `grid2d_blackboard_bimodality` | `research/reports/grid2d_blackboard_bimodality` | `python3 scripts/reportctl.py run --report grid2d_blackboard_bimodality -- python3 code/blackboard_bimodality_pipeline.py` | `code/z_scan.py` is the second active entry script |
| `grid2d_rect_bimodality` | `research/reports/grid2d_rect_bimodality` | `python3 scripts/reportctl.py run --report grid2d_rect_bimodality -- python3 code/rect_bimodality_report.py` | `--quick` available for smoke run |
| `grid2d_membrane_near_target` | `research/reports/grid2d_membrane_near_target` | `python3 scripts/reportctl.py run --report grid2d_membrane_near_target -- python3 code/membrane_near_target_report.py` | bilingual report; shared implementation lives under `packages/vkcore/src/vkcore/grid2d/` |
| `grid2d_one_two_target_gating` | `research/reports/grid2d_one_two_target_gating` | `python3 scripts/reportctl.py run --report grid2d_one_two_target_gating -- python3 code/one_two_target_gating_report.py` | March 16 gating line is now a repo-native canonical subsystem |
| `grid2d_two_target_double_peak` | `research/reports/grid2d_two_target_double_peak` | `python3 scripts/reportctl.py run --report grid2d_two_target_double_peak -- python3 code/two_target_2d_report.py` | CN/EN main report only; local method-comparison side report has been retired |
| `grid2d_two_walker_encounter_shortcut` | `research/reports/grid2d_two_walker_encounter_shortcut` | `python3 scripts/reportctl.py run --report grid2d_two_walker_encounter_shortcut -- python3 code/two_walker_encounter_report.py` | CN/EN pair |
| `luca_vs_recursion_unified_benchmark` | `research/reports/luca_vs_recursion_unified_benchmark` | `python3 scripts/reportctl.py run --report luca_vs_recursion_unified_benchmark -- python3 code/build_manifest.py` | single active computational comparison line; follow with runtime, plotting, and report-writing steps |

## Unified wrappers
- List reports: `python3 scripts/reportctl.py list`
- Resolve one report: `python3 scripts/reportctl.py resolve --report <id>`
- Run inside report dir: `python3 scripts/reportctl.py run --report <id> -- <cmd>`
- Build main report by language: `python3 scripts/reportctl.py build --report <id> --lang <cn|en>`
