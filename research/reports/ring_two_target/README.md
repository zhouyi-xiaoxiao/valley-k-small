# ring_two_target

Two-target lazy ring report with bilingual manuscripts.

## Reproduce
From repo root:

```bash
python3 scripts/reportctl.py run --report ring_two_target -- \
  python3 code/two_target_report.py
python3 scripts/reportctl.py build --report ring_two_target --lang cn
python3 scripts/reportctl.py build --report ring_two_target --lang en
```

## Canonical Paths
- Data: `research/reports/ring_two_target/artifacts/data/scan_bimodality_K2.csv`, `research/reports/ring_two_target/artifacts/data/scan_bimodality_K4.csv`, `research/reports/ring_two_target/artifacts/data/model_configs.csv`, `research/reports/ring_two_target/artifacts/data/model_configs.json`
- Time-series outputs: `research/reports/ring_two_target/artifacts/outputs/*_fpt.csv`
- Tables: `research/reports/ring_two_target/artifacts/tables/case_configs.tex`, `research/reports/ring_two_target/artifacts/tables/case_peaks.tex`
- PDFs: `research/reports/ring_two_target/manuscript/ring_two_target_cn.pdf`, `research/reports/ring_two_target/manuscript/ring_two_target_en.pdf`
