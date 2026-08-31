# Final submission independent audit — 20 July 2026

## Disposition

The final dated theorem-only article, Supplemental Material, PDFs, and clean
source archive pass the scientific/package audit with **P0 = 0 and P1 = 0**.
The selected branch is faithfully fail-closed:

- F0: `HOLD_F0`;
- F1: `NOT_RUN` (zero formal rows and no refit);
- F2: `NOT_RUN`;
- F3: `NOT_RUN`; and
- strict C0--C3/root transfer: `CONDITIONAL_NOT_ELECTED`.

This is not a finite-parameter success branch.  The admissible scientific
claim is the accepted exact-\(m\) Doi continuum existence theorem on a
declared compact positive-time window.  No finite-parameter physical-\(d=2\)
numerical evidence, off-lattice validation, or rigorous numerical-continuum
convergence result is claimed.

Portal upload is **not yet author-complete**.  The remaining ORCID,
funding/acknowledgment, conflict-of-interest, CRediT, tool-use, related-work
status/accession, all-author approval, APC, and public-archive identifier and
license fields require author confirmation.  These are author-owned portal
facts, not scientific or package P0/P1 defects.

## Audited final hashes

| Artifact | SHA-256 |
| --- | --- |
| Main TeX | `304e658b611d23af61a4672d3f087060fe6c0b69ef015d9411c986b413a5ea71` |
| Supplemental TeX | `f1c9a278f8fcfbffb2b076644e0c2598e2dd95d6296a29303aa702fa073bc7f7` |
| Frozen theorem spine | `79b0a4467a67999f605b8a5d8ec07e41a88c07edc8cdf1639ad6b8d4ce70658e` |
| Frozen complete proof | `a372b5a33d2203b8f3214a153f4aaf1e81497bf146c0ac1db1cfda97919c1c7b` |
| Bibliography | `b58d9aaaa29a8f8352cfd4a60486e077e164565d5a94e84e026ecb742eb27621` |
| Main PDF | `9590bc055f8a7ca2e475f69702adca1382cda3330681375c088c7c32a70f0825` |
| Supplemental PDF | `1a94d6f42d50725866e86238fa29e41ce7418c2e70f43b56c418cb632c96bb5d` |
| Clean source archive | `f35583513ac57672bb1c3fb9ac37b63ba098ab37d16c1a3760b97d60e5363f30` |
| Compile manifest | `4276158b6e6c0ab8a70a5a4565c1e09510543a904a654297cf802e9b2f484f49` |
| Source-package manifest | `515fff513910ffa202b51e985a312ac91adb92e257077fcc782a5224f20beace` |
| Terminal branch receipt | `756675955d2749e5db55dd37dba458204f614b279a5cf43707686b545b57ef72` |
| F0 semantic independent receipt | `0ed41cf67c21a90c33103badef4bcad42d1f633c0b9a449a784e5f25ea7cf957` |
| F0 resource independent receipt | `8a332c7a4dd3c594709283403292cd26b77abd076f7cc137c05176cf1cf14758` |

## Checks performed

1. Ran the five focused final suites for the compile driver, clean source
   package, independent F0 semantic replay, independent F0 resource replay,
   and terminal branch receipt: **50 passed**.
2. Independently reproduced the compressed source archive from the current
   source payloads.  The reproduced archive was byte-identical to the
   published archive at SHA-256
   `f35583513ac57672bb1c3fb9ac37b63ba098ab37d16c1a3760b97d60e5363f30`.
3. Inspected the archive as seven regular, flat, mode-`0644`, uid/gid-zero
   members with the frozen timestamp.  The internal `SHA256SUMS` ledger
   verified every payload, and no unsafe or noncanonical member was present.
4. Rebuilt both PDFs from a fresh extraction of that archive with the declared
   deterministic environment.  The rebuilt PDFs were byte-identical to the
   published main and Supplemental PDFs at the hashes above.
5. Checked the final reader sources, extracted PDF text, cover letter, and
   overlap/priority map for internal branch/status vocabulary and unfinished
   working markers.  No reader-facing `HOLD`, `PASS`, F0--F3, C0--C3,
   `placeholder`, working-draft/paper, non-submission, release-gate, or
   internal-round marker was exposed.  The publisher-inserted Supplemental
   Material URL wording is the journal-facing citation form, not an internal
   project marker.
6. Checked claim scope in the abstract, introduction, finite-parameter scope,
   discussion, Supplemental scope section, cover letter, and overlap map.
   Finite-parameter and numerical-continuum language occurs only as an
   explicit exclusion or limitation; no positive numerical or off-lattice
   result is asserted.
7. Confirmed the compile receipt records two isolated builds of each
   document, byte-identical rebuilds, zero undefined references/citations,
   zero overfull boxes, Ghostscript parsing, no Type-3 fonts, all fonts
   embedded, and no NUL/replacement characters.  The final output has four
   main pages and ten Supplemental pages, all at \(612\times792\) points.
   The final all-page render review at these dated hashes was reported clean.
8. Reconciled the independent F0 receipts with the terminal aggregate.  The
   semantic replay passes only at method-replay scope, while the formal
   resource gate fails because peak RSS was 5,455,511,552 bytes against a
   4,294,967,296-byte cap and peak footprint was 17,931,596,736 bytes against
   an 8,589,934,592-byte cap.  Swap delta was zero and the wall-time cap was
   not the failure.  Every science/F0/F1 promotion flag remains false.
9. Confirmed that the cover letter and overlap map disclose the two related
   manuscripts, separate their finite-model/numerical content from the exact
   theorem, and avoid a broad priority claim.  Their live venues, statuses,
   accession codes, e-print identifiers, and joint-handling intent correctly
   remain on the author action list.

## Severity ledger

| Scope | P0 | P1 | Disposition |
| --- | ---: | ---: | --- |
| Scientific claim ceiling | 0 | 0 | Pass |
| Main/Supplement reader package | 0 | 0 | Pass |
| Deterministic source reproduction | 0 | 0 | Pass |
| F0 terminal-branch fidelity | 0 | 0 | Pass |
| Overlap/priority disclosure | 0 | 0 | Pass subject to author-supplied live identifiers |

The article package is therefore ready for author metadata completion and
portal preflight, but it must not be represented as already portal-complete.
