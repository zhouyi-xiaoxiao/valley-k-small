# Physical Review Research initial-submission checklist

> **Superseding v2 checklist — 14 August 2026.** The 30 July theorem-only PDF
> set, two-author metadata, theorem-only Data Availability wording, and its
> hashes are historical and must not be uploaded. This checklist now points to
> the single-author manuscript with finite-parameter off-lattice evidence.

Status: **CURRENT V2 REVISION IN PROGRESS; PORTAL UPLOAD NOT YET AUTHORIZED**

Official references:

- <https://journals.aps.org/prresearch/authors>
- <https://journals.aps.org/authors/web-submission-guidelines-physical-review>
- <https://journals.aps.org/authors/data-availability-statements>
- <https://journals.aps.org/authors/appropriate-use-ai-tools>

## Current initial-submission files

The current source-of-truth directory is `../manuscript/prr_submission/`.
After all revisions, compile and visually inspect:

1. Main manuscript:
   `../manuscript/prr_submission/encounter_multimodal_prr_v2.pdf`
2. Supplemental Material:
   `../manuscript/prr_submission/encounter_multimodal_prr_v2_supplement.pdf`
3. Cover letter:
   `PRR_COVER_LETTER.md`, cross-checked against
   `../manuscript/prr_submission/PRR_COVER_LETTER.md`
4. Current related manuscripts for editor comparison:
   PRE **EU13106** and JCP **JCP26-AR-03623**.

Do not reuse `output/pdf/*20260730_verified.pdf`, the old theorem-only source
archive, or `THEOREM_ONLY_INITIAL_SUBMISSION_SET_20260730.sha256`. Their
historical verification does not validate the current v2 files.

## Required package verification

- [ ] Rebuild the main and Supplemental PDFs from the final current sources.
- [ ] Confirm title, sole author, affiliation, abstract, references, figure
      labels, tables, and Data Availability Statement in the rendered PDFs.
- [ ] Confirm the main and Supplemental titles match the cover letter and
      portal metadata exactly.
- [ ] Render and inspect every page; check floats, blank space, reference
      placement, figure captions, and Supplemental cross-references.
- [ ] Generate fresh hashes only after the final rebuild and record the exact
      source/PDF identities in a new current manifest.
- [ ] Confirm that the reproduction archive contains the scripts, raw or
      sufficient numerical records, seeds, classifier settings, and figure
      inputs required by the current finite-parameter claims.
- [ ] Deposit the archive publicly with a persistent identifier and license;
      update the manuscript Data Availability Statement to cite that record.

## Portal and sole-author facts

- [ ] Select **Physical Review Research** and **Regular Article**.
- [ ] Enter the final title and abstract from the rebuilt current PDF.
- [ ] Enter **Xiaoxiao Zhouyi** as sole and corresponding author; do not carry
      Luca Giuggioli forward from the superseded checklist.
- [ ] Authenticate Xiaoxiao Zhouyi’s ORCID in the APS account.
- [ ] Enter the complete Data Availability Statement for a manuscript that
      contains numerical simulations; do not use the theorem-only/no-data text.
- [ ] Confirm funding, computational-resource acknowledgments, conflicts of
      interest, sole-author CRediT statement if requested, and APC/open-access
      arrangements.
- [ ] Finalize the substantive AI-use disclosure from
      `AI_USE_DISCLOSURE_DRAFT_20260730.md` only after the completed-action
      statements have been verified.
- [ ] Provide any prior Physical Review submission/transfer history for this
      PRR manuscript.
- [ ] Disclose related PRE manuscript **EU13106** and JCP manuscript
      **JCP26-AR-03623** as related but distinct; upload current copies and the
      overlap/priority comparison, and state whether joint handling is sought.
- [ ] At PRR submission, separately notify the JCP editor and provide the PRR
      manuscript plus the overlap map against the actual submitted JCP revision,
      including its continuum bridge and off-lattice campaign, because the
      existing JCP cover predates the completed PRR package and discloses only
      PRE **EU13106**.
- [ ] Check suggested-referee affiliations and conflicts live immediately
      before submission.
- [ ] Review the cover letter’s date, title, related-work status, and novelty
      wording immediately before upload.
- [ ] Give explicit sole-author approval for the exact PDF hashes and every
      declaration.

## Final portal check

After APS renders or previews the uploaded files, compare every page with the
freshly hashed local PDFs, confirm the Supplemental Material is classified
separately, confirm the portal author list contains exactly one author, and
stop before the final submission button unless the complete portal record has
received explicit final approval.
