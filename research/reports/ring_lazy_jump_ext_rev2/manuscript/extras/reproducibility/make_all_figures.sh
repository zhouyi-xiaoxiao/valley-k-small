#!/usr/bin/env bash
# Reproduce every figure and artifact table of the DPMA manuscript.
# Run from research/reports/ring_lazy_jump_ext_rev2/code/ with the pinned environment.
set -euo pipefail
PY="${PY:-python3}"
for s in dpma_schematic dpma_prr_figures dpma_channel_mc dpma_start_dependence \
         dpma_brownian_fold dpma_general_u_master_curve dpma_halfline_bstar \
         dpma_endpoint_law dpma_normal_form dpma_window_scan dpma_cusp_verify \
         dpma_multishortcut dpma_2d_finite_lattice dpma_saddle_node_bc_theta \
         dpma_2d_Lsweep dpma_bcN_convergence dpma_bd_convergence dpma_measurement \
         dpma_saddle_node_certification; do
  echo "== $s =="
  "$PY" "$s.py"
done
echo "All figures/tables regenerated in ../artifacts/."
