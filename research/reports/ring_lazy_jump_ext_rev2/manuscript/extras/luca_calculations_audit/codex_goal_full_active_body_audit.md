# Optimized goal instruction: full active-body audit

Audit Luca's latest `Calculations.tex` and `Calculations.pdf` as a full active
manuscript, not only the shortcut section beginning around Eq. (29).

Scope:

- Use the latest Outlook attachments as the source of truth and verify their
  hashes against the archived files under
  `source/20260606_luca_updated/Calculations.tex` and `.pdf`.
- Audit only the active TeX body up to `\end{document}`. Treat material after
  `\end{document}` as commented scratch text unless the user explicitly asks to
  inspect it.
- Check the front part of the manuscript too: preliminary identities,
  no-shortcut first-passage formulae, killed propagator formulae, compact
  modal notation, Chebyshev generating functions, and the special antipodal
  self Green function.
- For each formula, distinguish:
  - numerically verified and safe as written,
  - mathematically correct but notationally fragile,
  - wrong if used literally,
  - wrong and downstream-conclusion-changing,
  - compile/self-containedness or typography issue.
- Use direct finite sums, finite transition matrices, absorbing submatrices,
  and resolvent checks wherever possible. Do not rely only on visual algebra.
- Produce a neutral collaborator-facing PDF with source line numbers, a
  severity-ranked issue ledger, and a compact "what to fix first" summary.
- Do not send email unless the user explicitly asks to send.

The final artifact should make it clear that the earlier no-shortcut formulae
mostly pass finite-matrix checks, while the real pre-shortcut issues are
indexing/object-name/identity slips, especially the compact Eq. (13) upper
limit and the two line-365 identities. The shortcut section still has the
downstream sign-propagation errors from Eq. (32) onward.
