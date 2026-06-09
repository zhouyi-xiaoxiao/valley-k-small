# Luca calculations audit

This directory archives Luca's `Calculations.tex` / `Calculations.pdf`
attachments, the May 31 audit/correction files, and the June 2026 follow-up
checks of the updated manuscript.

## Files

- `source/original_from_outlook_Calculations.tex` - original TeX attachment
  from Luca's 2026-05-28 Outlook thread `Re: For tomorrow`.
- `source/original_from_outlook_Calculations.pdf` - original PDF attachment
  from the same thread.
- `source/20260606_luca_updated/Calculations.tex` / `.pdf` - Luca's updated
  Outlook attachments from 2026-06-06.
- `eq29_to_eq41_beginner_guide.html` - beginner-oriented walkthrough of Luca's
  updated Eq. (29)--Eq. (41), including which steps are now correct, where the
  first-passage sign is still wrong, the corrected closed-form replacement for
  Eq. (41), the tail-decay interpretation, and a short reply draft.
- `eq41_correction_explainer.html` - focused explainer for the Eq. (41)
  correction, including the "hard-fix" long-convolution form and the cleaner
  closed-form replacement.
- `luca_updated_20260606_check.tex` / `.pdf` - short follow-up note checking
  Luca's updated manuscript against the finite stochastic shortcut matrix and
  summarizing the beta double-peak scan.
- `luca_updated_eq29_to_eq41_corrected_snippet.tex` / `.pdf` - compact
  corrected replacement block for the updated manuscript's Eq. (29)--Eq. (41)
  chain, including the corrected Eq. (32), Eq. (33), Eq. (40), closed-form
  replacement for Eq. (41), and tail statement.
- `luca_updated_hard_route_derivation.tex` / `.pdf` - detailed hard-route
  derivation that follows the original time-convolution route, derives the
  corrected long Eq. (41)-style expression, recompresses it to the closed form,
  and assesses the updated PDF's pole figure.
- `luca_updated_hard_route_delivery_packet.pdf` - single send-ready packet that
  combines the hard-route derivation with `luca_updated_20260606_check.pdf`.
- `updated_calculation_remaining_issues_audit.tex` / `.pdf` - neutral
  full active-body issue ledger for the remaining problems in the 2026-06-06
  updated TeX/PDF.  It checks the pre-shortcut formulae as well as the shortcut
  section, separates hard mathematical issues, structural derivation issues,
  and minor compile/notation problems, and includes finite-matrix,
  finite-sum, and trigonometric-identity checks.
- `pre_shortcut_formula_check_report.md` /
  `pre_shortcut_formula_check_results.csv` - reproducible summary table for
  the pre-shortcut checks.  It shows which front-section formulae pass and
  isolates the literal Eq. (13) compact-index issue and the line-365 identity
  slips.
- `scripts/pre_shortcut_formula_checks.py` - finite-matrix and finite-sum
  checker for the active manuscript before the shortcut section.
- `codex_goal_full_active_body_audit.md` - optimized instruction for the full
  active-body audit scope.
- `advisor_reply_readiness_check.md` - current send-readiness checklist for
  replying to Luca's 2026-06-06 updated-version questions.  It records the
  minimum required answers, the checked evidence, and the two PDFs to attach.
- `draft_reply_luca_updated_20260606.txt` - unsent draft reply for Luca's
  updated-version email.
- `draft_reply_luca_updated_hard_route.txt` - unsent draft reply for sending
  the hard-route delivery packet.
- `draft_reply_updated_calculation_remaining_issues.txt` - unsent concise reply
  draft for sending the remaining-issues audit note.
- `Luca_minimal_sign_issue_note.tex` / `.pdf` - two-page minimal note for
  sending Luca the first hard sign issue without the full audit packet.
- `Luca_original_minimal_sign_issue_marked.tex` / `.pdf` - Luca's original
  eight-page PDF with only the minimal sign issue marked on pages 5--6.
- `quick_sign_test_report.tex` / `.pdf` - neutral, send-ready numerical check
  comparing the Eq. (29) ratio, Eq. (32) with both signs, and the direct
  stochastic shortcut matrix.
- `quick_sign_test_report.md` and `quick_sign_test_results.csv` -
  machine-readable quick-test summary and full numerical grid.
- `scripts/quick_sign_test.py` - reproducible script for the quick sign
  test.
- `Calculations_marked_changes_v3.tex` / `.pdf` - issue-by-issue marked audit.
- `Calculations_corrected_complete_v3.tex` / `.pdf` - full corrected derivation.
- `Calculations_original_annotated_inplace.tex` - in-place annotated version
  built from Luca's original TeX.  It preserves the original text/equation order
  and inserts `AUDIT NOTE`, `ERROR`, `CORRECTION`, `WHY`, and
  `CORRECTED CONTINUATION` boxes directly after the problematic steps.  Key
  wrong denominators, signs, and conclusions are also marked with red
  strikeout/cancel redlines before the blue replacement formula is shown.
- `Calculations_original_annotated_inplace.pdf` - compiled PDF of the in-place
  annotated manuscript.
- `Calculations_audit_packet_combined.tex` / `.pdf` - one-file packet that puts
  the in-place redline first and the complete corrected derivation second.
- `luca_calculations_annotated_audit.tex` - concise annotated manuscript that
  follows the original shortcut section and shows what is wrong, what is added,
  and the corrected conclusion.
- `luca_calculations_annotated_audit.pdf` - compiled version of the annotated
  manuscript, when built.

## Main correction

For a shortcut from `u` into absorbing target `v`, the transient perturbation is
extra killing at `u`.  The corrected denominator is

```tex
1 + z \beta(1-q) \widetilde W_u(u,z)
```

not

```tex
1 - z \beta(1-q) \widetilde W_u(u,z).
```

Thus the original threshold `beta <= 2q / ((1-q)N)` is not a valid analytical
condition for the corrected stochastic shortcut-to-target model.

## What was added in the in-place version

- Portable fallbacks for Luca's missing local style files and the missing
  `phifunction.pdf` figure attachment.
- A model statement before the shortcut defect formula, making explicit that
  `u -> v` is killing when `v` is absorbing.
- Corrected propagator, first-passage generating function, symmetric-case
  generating function, pole equation, residue expansion, and tail conclusion.
- Redline-style cancellations for the exact local mistakes:
  `1 - z beta(1-q) W_u(u,z)`, the negative first-passage shortcut term,
  the `a - phi(z)` pole denominator, and the original beta-threshold/tail claim.
- A final note separating asymptotic tail decay from finite-time visual
  bimodality.

## How the files fit together

Use `Calculations_original_annotated_inplace.pdf` when sending comments back to
the original author: it preserves Luca's manuscript order and shows the exact
redline edits in context.

Use `Luca_minimal_sign_issue_note.pdf` plus
`Luca_original_minimal_sign_issue_marked.pdf` for a very small first reply:
these only point to the earliest sign error and avoid sending the full
correction all at once.

Use `quick_sign_test_report.pdf` for the requested follow-up test.  It
shows that the direct stochastic shortcut matrix matches the corrected
plus/plus Eq. (32) to machine precision, while the literal printed Eq. (29)
matches the original minus/minus Eq. (32), meaning the inconsistency is already
present in the printed Eq. (29) if interpreted as a stochastic `u -> v`
shortcut.

Use `Calculations_corrected_complete_v3.pdf` when checking the algebra behind
the replacement formulae: it is the expanded 21-page derivation and is meant to
avoid hidden steps.

Use `Calculations_marked_changes_v3.pdf` as the compact issue ledger: it lists
the audit items and explains why each correction is needed.

Use `Calculations_audit_packet_combined.pdf` if a single attachment is more
convenient.  It keeps the redline and the full derivation separate inside one
PDF, so the author can audit the original manuscript first and then check the
complete algebra trail.

Use `eq29_to_eq41_beginner_guide.html` for self-study before replying: it is the
least compressed explanation of the updated manuscript, with the corrected
formulae placed next to the original equation numbers.

Use `luca_updated_eq29_to_eq41_corrected_snippet.pdf` when a short mathematical
replacement note is more useful than the full beginner explainer.

Use `luca_updated_hard_route_delivery_packet.pdf` as the most complete compact
send-back artifact for the 2026-06-06 updated manuscript: it contains the hard
calculation, the closed-form reconciliation, the figure-caption assessment, and
the numerical checks in one PDF.

Use `updated_calculation_remaining_issues_audit.pdf` when the goal is to show
all remaining active-body issues in the updated TeX/PDF at once.  It is
deliberately neutral in tone and organized by source line, so it is easier to
send as a collaborator-facing checklist.  It now includes the front-section
checks rather than focusing only on Eq. (29) onward.

## Build

Run from this directory:

```bash
latexmk -pdf -interaction=nonstopmode -halt-on-error \
  -auxdir=build -emulate-aux-dir Calculations_original_annotated_inplace.tex

latexmk -pdf -interaction=nonstopmode -halt-on-error \
  -auxdir=build -emulate-aux-dir Calculations_corrected_complete_v3.tex

latexmk -pdf -interaction=nonstopmode -halt-on-error \
  -auxdir=build -emulate-aux-dir Calculations_audit_packet_combined.tex

latexmk -pdf -interaction=nonstopmode -halt-on-error \
  -auxdir=build -emulate-aux-dir Luca_minimal_sign_issue_note.tex

latexmk -pdf -interaction=nonstopmode -halt-on-error \
  -auxdir=build -emulate-aux-dir Luca_original_minimal_sign_issue_marked.tex

python3 scripts/quick_sign_test.py \
  --csv quick_sign_test_results.csv \
  --md quick_sign_test_report.md

python3 scripts/pre_shortcut_formula_checks.py \
  --csv pre_shortcut_formula_check_results.csv \
  --md pre_shortcut_formula_check_report.md

latexmk -pdf -interaction=nonstopmode -halt-on-error \
  -auxdir=build -emulate-aux-dir quick_sign_test_report.tex

latexmk -pdf -interaction=nonstopmode -halt-on-error \
  -auxdir=build -emulate-aux-dir luca_calculations_annotated_audit.tex

latexmk -pdf -interaction=nonstopmode -halt-on-error \
  luca_updated_eq29_to_eq41_corrected_snippet.tex

latexmk -pdf -interaction=nonstopmode -halt-on-error \
  luca_updated_hard_route_derivation.tex

latexmk -pdf -interaction=nonstopmode -halt-on-error \
  updated_calculation_remaining_issues_audit.tex
```

The latest checked builds have no overfull boxes, underfull boxes, undefined
references, fatal errors, or LaTeX errors.  The in-place REVTeX redline keeps one
benign `nameref` compatibility warning about `\label`; the complete derivation
log is clean.

## As-sent provenance (added 2026-06-09)

- `as_sent_email_attachments/` - byte-exact copies of every attachment actually
  sent to Luca in the thread, pulled back from Outlook Sent Items via Graph,
  organised by send timestamp, with a thread timeline README. The working
  copies above keep evolving after each send; use this folder when you need
  exactly what Luca received.
