# 2D Bimodality Report

This report is the canonical periodic-boundary 2D bimodality line for cases A/B/C.

## Reproduce
From repo root:

```bash
python3 scripts/reportctl.py run --report grid2d_bimodality -- \
  env MPLCONFIGDIR=.mplcache python3 code/bimodality_2d_pipeline.py \
  --cases-json code/config/cases.json \
  --mc-samples 30000 \
  --t-max 3000 \
  --t-max-aw 3000 \
  --t-max-scan 1500 \
  --fpt-method both \
  --fig-version main \
  --plot-style fig3v5 \
  --png-dpi 800 \
  --mc-bin-width 2 \
  --mc-smooth-window 5 \
  --peak-smooth-window 9 \
  --log-eps 1e-14 \
  --tune_B 1
python3 scripts/reportctl.py build --report grid2d_bimodality --lang cn
python3 scripts/reportctl.py build --report grid2d_bimodality --lang en
```

## Canonical Paths
- Configs: `research/reports/grid2d_bimodality/code/config/`
- Manuscripts: `research/reports/grid2d_bimodality/manuscript/grid2d_bimodality_cn.tex`, `research/reports/grid2d_bimodality/manuscript/grid2d_bimodality_en.tex`
- PDFs: `research/reports/grid2d_bimodality/manuscript/grid2d_bimodality_cn.pdf`, `research/reports/grid2d_bimodality/manuscript/grid2d_bimodality_en.pdf`
- Figures: `research/reports/grid2d_bimodality/artifacts/figures/`
- Metrics and reproducibility payloads: `research/reports/grid2d_bimodality/artifacts/data/`
- Scan outputs: `research/reports/grid2d_bimodality/artifacts/outputs/scan_B.json`, `research/reports/grid2d_bimodality/artifacts/outputs/tune_B.json`

## Notes
- Candidate A captures periodic wrap-around bimodality with two clear time scales.
- Candidate B is the tuned mixed-boundary corridor case.
- Candidate C is the door + sticky + wrap-around case with minimal local-bias support.

## Tests
```bash
python3 scripts/reportctl.py run --report grid2d_bimodality -- python3 code/tests/test_aw_pgf.py
python3 scripts/reportctl.py run --report grid2d_bimodality -- python3 code/tests/test_aw_toy_v5.py
```
