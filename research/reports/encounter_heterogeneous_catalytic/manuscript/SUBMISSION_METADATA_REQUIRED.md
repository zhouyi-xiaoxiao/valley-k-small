# Author-owned submission metadata — unresolved release gate

The scientific manuscript can be built and audited without inventing these
facts, but no submission package may be labelled release-ready until the authors
confirm every item below.

- [ ] Confirm the final author names, order, research-time affiliations, and
  active email address for every author, including Luca Giuggioli.
- [ ] Designate exactly one APS Corresponding Author. Supply and authenticate
  that author's ORCID; supply the other author's ORCID or explicitly decline
  it.
- [ ] Supply the exact funding/acknowledgment wording and every grant identifier,
  or explicitly confirm that no dedicated funding acknowledgment is required.
- [ ] Confirm the conflict-of-interest declaration. Do not insert “no conflicts”
  until both authors explicitly approve it.
- [ ] Approve a CRediT author-contribution statement for Xiaoxiao Zhouyi and Luca
  Giuggioli.
- [ ] Supply an author-verified APS AI-use disclosure. For every materially used
  tool, identify the tool/model and version or dated service identity, its
  scientific/coding/numerical/manuscript purpose, how the authors instructed
  it, and how they independently verified and accepted or rejected its output.
  Research use belongs in Methods; other material manuscript-preparation use
  belongs in Acknowledgments. Retain the underlying AI-use record.
- [ ] Select and approve licenses for code, data, figures, and documentation;
  approve immediate public release or specify an embargo.
- [ ] Supply the public archival data/software DOI or permanent identifier after
  repository deposit, add a formal data/software reference, and approve one
  complete APS Data Availability Statement covering both data and software.
- [ ] Confirm whether the related PRR manuscript will be submitted, under
  review, or published; supply any APS accession code and approve the
  scientific-distinction or joint-submission wording in both cover letters.
- [ ] Approve the standalone Supplemental Material as publish-ready. It will not
  receive ordinary APS copyediting or a normal article proof.
- [ ] Approve suggested/excluded referees after checking conflicts.
- [ ] Confirm whether PRE open access will use Bristol's APS-Jisc eligibility,
  which depends on the Bristol Corresponding Author being designated from the
  initial submission.
- [ ] Both authors approve the final main article, Supplemental Material,
  repository, cover letter, and submission.
- [ ] Execute the documented release chain: clean audited source tag -> `full
  --release` -> committed/tagged artifact snapshot -> `verify --release` ->
  committed/tagged final proof snapshot; then run the external proof checker
  from that clean final tag.

Current manuscript TODO comments intentionally preserve these missing fields.
