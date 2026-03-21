# grid2d_membrane_near_target

Canonical bilingual report for the membrane-near-target extension line:
- one-target corridor with symmetric and directional semi-permeable membranes
- no-corridor two-target setting with one target near the start

## Reproduce
From repo root:

```bash
python3 scripts/reportctl.py run --report grid2d_membrane_near_target -- \
  python3 code/membrane_near_target_report.py
python3 scripts/reportctl.py build --report grid2d_membrane_near_target --lang cn
python3 scripts/reportctl.py build --report grid2d_membrane_near_target --lang en
```

## Canonical Paths
- Data products: `research/reports/grid2d_membrane_near_target/artifacts/data/`
- Figures: `research/reports/grid2d_membrane_near_target/artifacts/figures/`
- Tables: `research/reports/grid2d_membrane_near_target/artifacts/tables/`
- Time-series outputs: `research/reports/grid2d_membrane_near_target/artifacts/outputs/`
- PDFs: `research/reports/grid2d_membrane_near_target/manuscript/grid2d_membrane_near_target_cn.pdf`, `research/reports/grid2d_membrane_near_target/manuscript/grid2d_membrane_near_target_en.pdf`

## Notes
- Shared implementation is repo-native and lives under `packages/vkcore/src/vkcore/grid2d/`.
- Representative one-target and two-target artifacts are regenerated from the canonical code path rather than imported bundles.
