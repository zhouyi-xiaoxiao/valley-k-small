# Unified Benchmark Protocol

- Compare only two families: `luca_gf` and `time_recursion`.
- Use the practical native-task fairness rule instead of forced full-tail equality.
- Keep `diagnostic` and `curve` tasks separate.
- Fix BLAS threads to one core.
- Timing protocol: `warmup=1`, `measured=3`, report the median.
- Keep the historical fixed-full-FPT note embedded in Appendix F of this unified report.
