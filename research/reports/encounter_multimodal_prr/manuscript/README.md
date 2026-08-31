# Manuscript status: PRR v2 numerical submission package

> **Superseding notice — 14 August 2026.** The active single-author PRR
> package is now `prr_submission/encounter_multimodal_prr_v2.tex` together
> with `prr_submission/encounter_multimodal_prr_v2_supplement.tex`.  It
> contains the exact finite-window theorem, positive-budget transfer,
> off-lattice finite-parameter campaigns, operational classifier analyses,
> robustness records, and a versioned reproduction archive.  The theorem-only
> state described below is historical and must not be uploaded.

Current reader-facing files are maintained in `prr_submission/`.  The article,
Supplemental Material, cover letter, references, figures, and metadata there
are single-author materials for Xiaoxiao Zhouyi.  The three budget scales are
kept distinct: `B_top` is the theorem topology threshold, `B_cert` is a
fixed-allocation sufficient value, and `B_op` is an operational numerical
classifier crossing.

## Historical theorem-only package

The former reader sources were:

- `encounter_multimodal_prr_submission.tex`;
- `encounter_multimodal_prr_submission_supplement.tex`;
- `exact_m_theorem_spine.tex`;
- the clean submission rendering of `exact_m_theorem_full_proof.tex`; and
- `references.bib`.

The deterministic builder validates the selected pre-science resource receipt,
uses the frozen accepted theorem bytes, makes two isolated builds of each
document, and rejects internal stage markers in the rendered text:

```bash
.venv/bin/python \
  research/reports/encounter_multimodal_prr/code/compile_theorem_first_submission.py
```

The reader PDFs are:

- `../output/pdf/encounter_multimodal_prr_submission.pdf`;
- `../output/pdf/encounter_multimodal_prr_submission_supplement.pdf`.

That selected paper contains the exact prescribed finite-modality Doi theorem
and states explicitly that no finite-parameter physical evidence is used.
The pre-science production resource limitation is retained in the internal
terminal receipt, not narrated as a scientific result in the reader article.
The paper contains no finite-parameter physical result, no off-lattice result,
and no strict numerical continuum-convergence claim.

The following files are historical reconstruction sources and must not be
uploaded:

- `encounter_multimodal_prr.tex` and its PDF;
- `encounter_multimodal_prr_theorem_first_working.tex`;
- `encounter_multimodal_prr_supplement.tex`; and
- their working PDFs and auxiliary files.

For a current portal upload, follow
`../submission/AUTHOR_ACTIONS_BEFORE_PORTAL_UPLOAD.md` and use only the final
checked files from `prr_submission/` and the final reproduction archive.
