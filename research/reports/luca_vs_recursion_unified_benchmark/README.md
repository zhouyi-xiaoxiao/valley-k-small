# Unified Computational Benchmark

This is the single active computational-method comparison report in the repository.

## Scope
- Compare only `luca_gf` and `time_recursion`.
- Keep scientific reports separate and centralize only the computational comparison line here.
- Use practical native-task fairness as the active benchmark rule.
- Keep the historical fixed full-FPT note only inside Appendix F of this report.

## Reproduce
From repo root:

```bash
python3 scripts/reportctl.py run --report luca_vs_recursion_unified_benchmark -- \
  python3 code/build_manifest.py
python3 scripts/reportctl.py run --report luca_vs_recursion_unified_benchmark -- \
  python3 code/run_unified_benchmark.py
python3 scripts/reportctl.py run --report luca_vs_recursion_unified_benchmark -- \
  python3 code/plot_unified_figures.py
python3 scripts/reportctl.py run --report luca_vs_recursion_unified_benchmark -- \
  python3 code/write_unified_report.py
python3 scripts/reportctl.py build --report luca_vs_recursion_unified_benchmark --lang en
python3 scripts/reportctl.py build --report luca_vs_recursion_unified_benchmark --lang cn
```

## Canonical Paths
- Data: `research/reports/luca_vs_recursion_unified_benchmark/artifacts/data/manifest.csv`, `research/reports/luca_vs_recursion_unified_benchmark/artifacts/data/runtime_raw.csv`, `research/reports/luca_vs_recursion_unified_benchmark/artifacts/data/runtime_summary.json`
- Figures: `research/reports/luca_vs_recursion_unified_benchmark/artifacts/figures/`
- Tables: `research/reports/luca_vs_recursion_unified_benchmark/artifacts/tables/`
- Manuscripts: `research/reports/luca_vs_recursion_unified_benchmark/manuscript/luca_vs_recursion_unified_benchmark_en.tex`, `research/reports/luca_vs_recursion_unified_benchmark/manuscript/luca_vs_recursion_unified_benchmark_cn.tex`
