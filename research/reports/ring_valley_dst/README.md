# ring_valley_dst

This report studies DST-driven second-peak modulation on ring lattices.

## Active Entry Scripts
- `research/reports/ring_valley_dst/code/bimodality_flux_scan.py`
- `research/reports/ring_valley_dst/code/dst_shortcut_usage_mc.py`
- `research/reports/ring_valley_dst/code/second_peak_scan.py`
- `research/reports/ring_valley_dst/code/second_peak_shortcut_usage_mc.py`

Shared implementation lives under `packages/vkcore/src/vkcore/ring/valley_dst/`.

## Reproduce
From repo root:

```bash
python3 scripts/reportctl.py run --report ring_valley_dst -- \
  python3 code/bimodality_flux_scan.py --help
python3 scripts/reportctl.py run --report ring_valley_dst -- \
  python3 code/dst_shortcut_usage_mc.py --help
python3 scripts/reportctl.py run --report ring_valley_dst -- \
  python3 code/second_peak_scan.py --help
python3 scripts/reportctl.py run --report ring_valley_dst -- \
  python3 code/second_peak_shortcut_usage_mc.py --help
python3 scripts/reportctl.py build --report ring_valley_dst --lang cn
python3 scripts/reportctl.py build --report ring_valley_dst --lang en
```

## Canonical Paths
- Data and inputs: `research/reports/ring_valley_dst/artifacts/data/`
- Figures: `research/reports/ring_valley_dst/artifacts/figures/`
- Tables: `research/reports/ring_valley_dst/artifacts/tables/`
- PDFs: `research/reports/ring_valley_dst/manuscript/ring_valley_dst_cn.pdf`, `research/reports/ring_valley_dst/manuscript/ring_valley_dst_en.pdf`
