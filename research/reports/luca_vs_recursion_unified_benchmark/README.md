# Unified Computational Benchmark

This is the single active computational-method comparison report in the repository.

## Scope
- Compare only two families: `luca_gf` and `time_recursion`.
- Keep all scientific reports separate; centralize only the computational comparison line here.
- Use practical native-task fairness as the main benchmark rule.
- Treat `Luca/GF` as a Giuggioli/Sarvaharman method family with workload-specific layers, not as a single monolithic solver.
- Embed the historical full-tail note inside Appendix F instead of maintaining a separate active compare report.

## Snapshot
- Diagnostic-task median `time/luca` speed ratio: `0.0490`
- Curve-task median `time/luca` speed ratio: `0.0398`

## Outputs
- Data: `artifacts/data/manifest.csv`, `artifacts/data/runtime_raw.csv`, `artifacts/data/runtime_summary.json`
- Runtime figures: `artifacts/figures/unified_runtime_diagnostic.pdf`, `artifacts/figures/unified_runtime_curve.pdf`, `artifacts/figures/unified_speedup_by_workload.pdf`
- Detailed workload configuration figures: `artifacts/figures/<workload_id>_config_detailed.pdf` for all six workloads
- Audit note: `notes/theory_audit_2026-04-15.md`
- Appendix tables: `artifacts/tables/unified_audit_appendix_en.tex`, `artifacts/tables/unified_audit_appendix_cn.tex`
- Manuscripts: `manuscript/luca_vs_recursion_unified_benchmark_en.tex`, `manuscript/luca_vs_recursion_unified_benchmark_cn.tex`

## Reproduce
```bash
python3 scripts/reportctl.py run --report luca_vs_recursion_unified_benchmark -- python3 code/build_manifest.py
python3 scripts/reportctl.py run --report luca_vs_recursion_unified_benchmark -- python3 code/run_unified_benchmark.py
python3 scripts/reportctl.py run --report luca_vs_recursion_unified_benchmark -- python3 code/plot_unified_figures.py
python3 scripts/reportctl.py run --report luca_vs_recursion_unified_benchmark -- python3 code/write_unified_report.py

python3 scripts/reportctl.py build --report luca_vs_recursion_unified_benchmark --lang en
python3 scripts/reportctl.py build --report luca_vs_recursion_unified_benchmark --lang cn
```
