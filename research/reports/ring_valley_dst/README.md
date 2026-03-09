# ring_valley_dst

This report studies DST-driven second-peak modulation on ring lattices (CN/EN).

## Entry scripts (thin wrappers)
- `research/reports/ring_valley_dst/code/bimodality_flux_scan.py`
- `research/reports/ring_valley_dst/code/dst_shortcut_usage_mc.py`
- `research/reports/ring_valley_dst/code/second_peak_scan.py`
- `research/reports/ring_valley_dst/code/second_peak_shortcut_usage_mc.py`

Core implementation now lives in:
- `packages/vkcore/src/vkcore/ring/valley_dst/`

## Quick run
From repo root:

```bash
source .venv/bin/activate
python3 reports/ring_valley_dst/code/bimodality_flux_scan.py --help
python3 reports/ring_valley_dst/code/dst_shortcut_usage_mc.py --help
python3 reports/ring_valley_dst/code/second_peak_scan.py --help
python3 reports/ring_valley_dst/code/second_peak_shortcut_usage_mc.py --help
```

## Build PDFs
```bash
cd reports/ring_valley_dst
latexmk -xelatex -interaction=nonstopmode -halt-on-error -auxdir=build -emulate-aux-dir ring_valley_dst_cn.tex
latexmk -pdf -interaction=nonstopmode -halt-on-error -auxdir=build -emulate-aux-dir ring_valley_dst_en.tex
```
