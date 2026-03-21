# ring_lazy_jump_ext_rev2

Revision v2 of the lazy jump-over extension report.

## Canonical Paths
- Manuscripts: `research/reports/ring_lazy_jump_ext_rev2/manuscript/ring_lazy_jump_ext_rev2_cn.tex`, `research/reports/ring_lazy_jump_ext_rev2/manuscript/ring_lazy_jump_ext_rev2_en.tex`
- PDFs: `research/reports/ring_lazy_jump_ext_rev2/manuscript/ring_lazy_jump_ext_rev2_cn.pdf`, `research/reports/ring_lazy_jump_ext_rev2/manuscript/ring_lazy_jump_ext_rev2_en.pdf`
- Workflow notes: `research/reports/ring_lazy_jump_ext_rev2/notes/readme_rev.md`
- Changelog: `research/reports/ring_lazy_jump_ext_rev2/notes/changelog_v2.md`
- Revision notes: `research/reports/ring_lazy_jump_ext_rev2/notes/revision_notes.md`
- Sensitivity outputs: `research/reports/ring_lazy_jump_ext_rev2/artifacts/outputs/sensitivity/`

## Reproduce
From repo root:

```bash
python3 scripts/reportctl.py run --report ring_lazy_jump_ext_rev2 -- \
  python3 code/jumpover_bimodality_pipeline.py
python3 scripts/reportctl.py run --report ring_lazy_jump_ext_rev2 -- \
  python3 code/plot_fig2_overlap_binbars.py
python3 scripts/reportctl.py build --report ring_lazy_jump_ext_rev2 --lang cn
python3 scripts/reportctl.py build --report ring_lazy_jump_ext_rev2 --lang en
```
