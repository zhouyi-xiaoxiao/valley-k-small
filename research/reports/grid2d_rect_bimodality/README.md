# 2D Rectangle Bimodality

This report studies double-peak first-passage behavior in non-square rectangular domains for:
- two targets with a short/long path design
- one target with a reflecting-wall corridor and local bias

## Reproduce
From repo root:

```bash
python3 scripts/reportctl.py run --report grid2d_rect_bimodality -- \
  python3 code/rect_bimodality_report.py --quick
python3 scripts/reportctl.py run --report grid2d_rect_bimodality -- \
  python3 code/rect_bimodality_report.py
python3 scripts/reportctl.py build --report grid2d_rect_bimodality --lang cn
python3 scripts/reportctl.py build --report grid2d_rect_bimodality --lang en
```

## Canonical Paths
- Manuscripts: `research/reports/grid2d_rect_bimodality/manuscript/`
- PDFs: `research/reports/grid2d_rect_bimodality/manuscript/grid2d_rect_bimodality_cn.pdf`, `research/reports/grid2d_rect_bimodality/manuscript/grid2d_rect_bimodality_en.pdf`
- Figures: `research/reports/grid2d_rect_bimodality/artifacts/figures/`
- Tables: `research/reports/grid2d_rect_bimodality/artifacts/tables/`
- Scan data: `research/reports/grid2d_rect_bimodality/artifacts/data/`

## Notes
- `--quick` is the recommended smoke path before full regeneration.
- The report keeps both the two-target and one-target corridor branches in one canonical artifact tree.
