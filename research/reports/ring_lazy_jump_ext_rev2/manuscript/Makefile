PY = python3
BETA = 0.01
FIG2_XMAX = 1350
FIG2_JSON = data/fig2_bins_bars_beta$(BETA).json
FT_CSV = data/ft_beta$(BETA).csv
FIG2_PDF = figures/fig2_overlap_binbars_beta$(BETA)_x$(FIG2_XMAX).pdf
WINDOW_TEX = tables/window_params_beta$(BETA).tex
WINDOW_CSV = tables/window_params_beta$(BETA).csv
WINDOW_TEX_EN = tables/window_params_beta$(BETA)_en.tex

.PHONY: export fig2 sensitivity pdf check clean window-table

export:
	$(PY) code/export_fig2_inputs.py --beta $(BETA) --N 100 --ref-k 4 --out-json $(FIG2_JSON) --out-ft $(FT_CSV) --quiet

window-table: export
	$(PY) code/export_window_table.py --input-json $(FIG2_JSON) --ft-csv $(FT_CSV) --out-csv $(WINDOW_CSV) --out-tex $(WINDOW_TEX) --out-tex-en $(WINDOW_TEX_EN)

fig2: export window-table
	$(PY) code/validate_fig2_json.py --input $(FIG2_JSON) --schema data/fig2_bins_bars.schema.json
	$(PY) code/plot_fig2_overlap_binbars.py --input-json $(FIG2_JSON) --ft-csv $(FT_CSV) --out $(FIG2_PDF) --xlim 1 $(FIG2_XMAX)

sensitivity: export
	$(PY) code/sensitivity_thresholds.py --ft-csv $(FT_CSV) --beta $(BETA) --out-csv outputs/sensitivity/threshold_sweep.csv --out-fig outputs/sensitivity/threshold_sweep_heatmap.pdf
	$(PY) code/sensitivity_bin_intervals.py --input-json $(FIG2_JSON) --beta $(BETA) --out-csv outputs/sensitivity/bin_shift_summary.csv --out-fig outputs/sensitivity/bin_shift_plot.pdf
	$(PY) code/sensitivity_mc_uncertainty.py --input-json $(FIG2_JSON) --beta $(BETA) --out-csv outputs/sensitivity/mc_uncertainty.csv --out-fig outputs/sensitivity/mc_uncertainty_plot.pdf

pdf: window-table
	latexmk -xelatex -interaction=nonstopmode -halt-on-error -auxdir=build -emulate-aux-dir ring_lazy_jump_ext_rev2_cn.tex

check: fig2 sensitivity pdf
	test -s $(FIG2_PDF)
	test -s ring_lazy_jump_ext_rev2_cn.pdf

clean:
	rm -rf build
	rm -f figures/fig2_overlap_binbars_beta$(BETA)_x$(FIG2_XMAX).meta.json
