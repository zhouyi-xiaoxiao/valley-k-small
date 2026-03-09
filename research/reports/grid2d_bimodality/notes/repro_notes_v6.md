# v6 Repro Notes (2D bimodality)

## v6 Repro Commands
1) Generate data + figures (v6):
```
MPLCONFIGDIR=reports/grid2d_bimodality/.mplcache \
python3 reports/grid2d_bimodality/code/bimodality_2d_pipeline.py \
  --cases-json reports/grid2d_bimodality/config/cases_v3.json \
  --mc-samples 20000 \
  --t-max 3000 \
  --t-max-aw 3000 \
  --t-max-scan 1500 \
  --fpt-method both \
  --fig-version v6 \
  --plot-style fig3v2 \
  --png-dpi 600 \
  --mc-bin-width 5 \
  --mc-smooth-window 7 \
  --peak-smooth-window 7 \
  --log-eps 1e-14
```

2) Build PDF (v6):
```
cd reports/grid2d_bimodality && \
latexmk -xelatex -interaction=nonstopmode -halt-on-error \
  -auxdir=build -emulate-aux-dir 2d_bimodality_cn_v6.tex
```

## Current state (v5)
1) Data + figures pipeline: `research/reports/grid2d_bimodality/code/bimodality_2d_pipeline.py`
2) Plotting (v5): `research/reports/grid2d_bimodality/code/viz/fig3_style.py` and helpers in `research/reports/grid2d_bimodality/code/viz/`
3) Case geometry: `research/reports/grid2d_bimodality/config/cases_v3.json`
4) Report entry: `research/reports/grid2d_bimodality/2d_bimodality_cn_v5.tex` -> `research/reports/grid2d_bimodality/2d_bimodality_cn_v5.pdf`
5) v5 figures: `research/reports/grid2d_bimodality/figures_v5/` (env/paths/heatmaps/FPT/channel_decomp/unwrapped)

## v6 TODO (visual + mechanism fixes)
- [ ] 多数轨迹图空白太大，需要 ROI 版式（主图全域 + 右侧 zoom / 或两栏 full+zoom）
- [ ] 去掉周期边界的巨大弧线箭头，统一改为 two-tile unwrapped 直线表示 wrap 通道
- [ ] FPT 图需要多尺度：全局 log + fast 峰局部 + slow 峰局部（或双 inset）
- [ ] 修复 channel mixture 在 t=tmax 处的巨大尖峰（artifact）
- [ ] Candidate B：fast 通道概率显示为 0，需要调整通道判别规则与展示
- [ ] 热图 panel 空白（Candidate B 明显），需要更稳健的 LogNorm / vmin/vmax 与 0 mask 策略
- [ ] 所有图：禁止文字重叠；字号/线宽/标记统一；输出 PDF(矢量) + PNG(高 dpi)
