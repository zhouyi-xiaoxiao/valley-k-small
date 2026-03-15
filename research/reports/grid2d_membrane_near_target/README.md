# grid2d_membrane_near_target

New 2D extension report covering:
- one-target corridor with symmetric/directional semi-permeable membranes;
- no-corridor two-target setting with one target near the start.

## Generate data and figures
```bash
cd research/reports/grid2d_membrane_near_target
../../../.venv/bin/python code/membrane_near_target_report.py
```

## Build PDFs
Chinese:
```bash
cd research/reports/grid2d_membrane_near_target/manuscript
latexmk -xelatex -interaction=nonstopmode -halt-on-error -auxdir=build -emulate-aux-dir grid2d_membrane_near_target_cn.tex
```

English:
```bash
cd research/reports/grid2d_membrane_near_target/manuscript
latexmk -pdf -interaction=nonstopmode -halt-on-error -auxdir=build -emulate-aux-dir grid2d_membrane_near_target_en.tex
```

## Key outputs
- `data/summary.json`
- `data/corridor_membrane_directional_scan.csv`
- `data/membrane_directional_window_flux.csv`
- `data/one_target_start_scan.csv`
- `data/two_target_candidate_scans.csv`
- `data/two_target_start_scan.csv`
- `data/two_target_near_position_scan.csv`
- `figures/membrane_symmetric_*`
- `figures/membrane_directional_*`
- `figures/membrane_rep_dir_*.pdf`
- `figures/one_target_start_phase_map.pdf`
- `figures/one_target_start_sep_map.pdf`
- `figures/two_target_geometry_atlas.pdf`
- `figures/two_target_committor_surface.pdf`
- `figures/one_target_basin_schematic.pdf`
- `figures/two_target_*`
- `tables/*.tex`
- `outputs/*_fpt.csv`
