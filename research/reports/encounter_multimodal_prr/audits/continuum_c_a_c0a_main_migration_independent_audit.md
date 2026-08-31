# Continuum C-A: independent audit of the C0-A main-text migration

Date: 2026-07-15  
Status: **PASS C0-A MAIN MIGRATION ONLY / COMPLETE C0 OPEN / C1--C3 OPEN /
NO FINITE-VOLUME-TO-CONTINUUM ROOT TRANSFER / NO POSITIVE-B RESULT**

## Frozen artifacts reviewed

- main source SHA-256:
  `10d62404f15e306072e093aaa6fa5abbf5f6bdb0ecb42a341e3740dcf77aac2c`;
- main PDF SHA-256:
  `577d2d4b494633a3e009f13fbd581a9c889d7c84fd11c18e5b3367a6e4b1a42e`;
- Supplemental PDF SHA-256:
  `70de25968298d58222bbab10639a2253067f5c01d4d6462d743e3e6eca5790fb`;
- compile-manifest SHA-256:
  `704c96f173c51423457ef8b03fa8ee914ec10bedebc3e6aa435965991d34a6ea`.

The review was read-only and independent of the main-text edit.  It compared
the inserted proposition against the living continuum-v2 contract, the full
Supplemental corollary and proof, and the Round-167 anisotropy erratum.

## Mathematical attack

The following checks pass.

1. The physical-`d=2` quotient is
   `R_z x R_r_parallel x T_W`, with
   `D=diag(D/2,2D,2D)` and
   `b=(-gamma(z-zbar),-gamma r_parallel,0)`.
2. The factor `W^{-1}` in the sharp contact observable correctly restores the
   omitted common transverse centre coordinate and does not duplicate the
   normalized relative-coordinate density.
3. The living reversible density is the anisotropic formula

   \[
   \pi=Z_\pi^{-1}\exp[-\gamma(z-\bar z)^2/D
                          -\gamma r_\parallel^2/(4D)],
   \qquad Z_\pi=2\pi DW/\gamma,
   \]

   and it satisfies `D grad(log pi)=b`.  The withdrawn isotropic Round-165
   exponent does not appear.
4. The weighted core, closed form, common domain, norm equivalence and unitary
   map `Uu=pi u` are consistent.  The generator sign
   `A=U(-H)U^{-1}` is the forward generator `L-B M_V`.
5. The `r=0,1,2` positive-time observable formula and spectral constants are
   correct.  The text uses `B^{-1}f_B` only for `B>0`, while the observable
   itself remains defined at `B=0`.
6. Positivity and the integrated mass identity follow from the sub-Markov
   semigroup and Gaussian-cutoff test of the weak evolution.
7. Proposition numbering and all equation/section references resolve.

No P0 or P1 mathematical defect was found.

## Build and visual attack

The fail-closed compiler produced two byte-identical isolated builds of both
documents.  The manifest records:

- seven Letter-sized main pages and 23 Supplemental pages;
- zero overfull boxes;
- zero undefined references or citations in the accepted final build;
- all fonts embedded and no Type-3 fonts;
- `positive_budget_evaluated=false`;
- `positive_budget_scientific_values_read=false`;
- `release_eligible=false`.

All seven main pages were rendered and inspected.  No clipping, overlap,
broken column, malformed glyph or accidental blank page was found.  Page 7 is
a sparse continuation of the references.

## Claim boundary

The migrated proposition establishes only the unbounded physical target,
form-associated natural-decay realization, positive-time observable calculus
and mass identity.  It does not establish:

- the complete hash-bound C0 model contract;
- finite-volume forms and identification maps;
- C1 Mosco or strong-resolvent convergence;
- computable C2/C3 spatial or box-truncation errors;
- finite-volume-to-unbounded-continuum root transfer;
- positive-budget topology, F0, F1 or F3.

The stale auxiliary status line was corrected to record that C0-A now appears
as main Proposition 1 plus the Supplemental corollary.  The evidence vocabulary
was also repaired so that odd/even and independent-method agreement is only
continuum-consistent finite-window numerical evidence; `CONTINUUM VERIFIED`
remains reserved for the full C0--C7 chain and strict root-margin inequalities.

## Decision

The seven-page main PDF is accepted as the current internal theorem-first
working artifact.  This audit does not make it release-eligible and does not
authorize migration of any open numerical or continuum result.
