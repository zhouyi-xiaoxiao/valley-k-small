# v6 Repro Notes (2D bimodality)

This note is historical context for the v6 plotting pass. The active public interface is still:
- `python3 scripts/reportctl.py run --report grid2d_bimodality -- ...`
- `python3 scripts/reportctl.py build --report grid2d_bimodality --lang <cn|en>`

## Historical v6 Repro Commands
1. Generate data + figures:

```bash
python3 scripts/reportctl.py run --report grid2d_bimodality -- \
  env MPLCONFIGDIR=.mplcache python3 code/bimodality_2d_pipeline.py \
  --cases-json code/config/cases_v3.json \
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

2. Build the historical v6 manuscript:

```bash
python3 scripts/reportctl.py run --report grid2d_bimodality -- \
  latexmk -xelatex -interaction=nonstopmode -halt-on-error \
  -auxdir=manuscript/build -emulate-aux-dir manuscript/2d_bimodality_cn_v6.tex
```

## Canonical Pointers
1. Data + figures pipeline: `research/reports/grid2d_bimodality/code/bimodality_2d_pipeline.py`
2. Plotting helpers: `research/reports/grid2d_bimodality/code/viz/`
3. Case geometry: `research/reports/grid2d_bimodality/code/config/cases_v3.json`
4. Current canonical manuscripts: `research/reports/grid2d_bimodality/manuscript/`
5. Current canonical artifacts: `research/reports/grid2d_bimodality/artifacts/`

## Historical v6 TODO
- [ ] 多数轨迹图空白太大，需要 ROI 版式（主图全域 + 右侧 zoom / 或两栏 full+zoom）
- [ ] 去掉周期边界的巨大弧线箭头，统一改为 two-tile unwrapped 直线表示 wrap 通道
- [ ] FPT 图需要多尺度：全局 log + fast 峰局部 + slow 峰局部（或双 inset）
- [ ] 修复 channel mixture 在 `t=tmax` 处的巨大尖峰（artifact）
- [ ] Candidate B：fast 通道概率显示为 0，需要调整通道判别规则与展示
- [ ] 热图 panel 空白（Candidate B 明显），需要更稳健的 LogNorm / `vmin` / `vmax` 与 0 mask 策略
- [ ] 所有图：禁止文字重叠；字号/线宽/标记统一；输出 PDF（矢量）+ PNG（高 dpi）
