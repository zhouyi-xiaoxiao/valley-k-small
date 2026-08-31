# Round 29: independent theory and bibliography attack

Date: 2026-07-13  
Mode: independent adversarial read; no manuscript, bibliography, theorem-note,
result, or figure artifact was edited  
Scope: the current encounter_multimodal_prr.tex, references.bib,
pde_mixed_jet_theorem.md, direct_physical_multimode_theorem.md, and the Round
27--28 audit pair. The not-yet-integrated physical-\(d=3\) numerical result and
the broad-bridge temporary seed failure were deliberately excluded.

Snapshot attacked:

- TeX SHA-256: 0d6af5af983efebfcdf0927718367191672918bc707ef292ab4076ab13582520;
- bibliography SHA-256: 3a2f85a5c62e9dca55f32be567df8aea15be721312e6ef7c99dada780a633340;
- mixed-jet note SHA-256: 3fc37bafc6320556322e80daa2c56bad9fd4b19e1856100caa8adf92341a8007;
- direct-theorem note SHA-256: 7493499883ba41ce043c3535e1ca3d6c7a4c5de0cce9e575e261b4f8da9c2974.

Concurrency note: while this audit was being written, a separate task inserted
the out-of-scope \(d=3\) numerical section and changed the TeX SHA-256 to
667eaf5b5544ab18823a39d55a573b4219fdb1cfd3b4e524c39a6945e816dbd6. A focused
post-change reread confirmed that every finding below remained present. The
new \(d=3\) claims themselves were not assessed. Line numbers after the
insertion can be shifted by approximately three lines before the numerical
section; the quoted text and section handles are the authoritative locations.

## Verdict

**Round 28 did not completely close the theory/bibliography attack surface.**
The current manuscript has **one P0, two P1, and four P2 findings**. The core
construction appears repairable: the P0 is an omitted hypothesis already
stated correctly in the direct-theorem note, not evidence that the
construction itself fails. Nevertheless, the manuscript currently labels a
theorem PROVED under assumptions that do not imply the weighted-space
membership or exact channel factorization used in its proof. The present
source must remain release_eligible=false.

| Priority | Count | Disposition |
|---|---:|---|
| P0 | 1 | central theorem is not self-contained as stated |
| P1 | 2 | quantitative rank proposition and one publisher citation need repair |
| P2 | 4 | author metadata, citation wording, figure vocabulary, and one domain word |

## P0 findings

### P0.1: the direct physical theorem omits the Gaussian product initial law required by its exact formula and weighted-space invocation

**Locations:** TeX lines 436--479, 500--523, and 896--909; compare
direct_physical_multimode_theorem.md lines 37--95 and 131--156.

The manuscript specifies the midpoint SDE and says only that the initial
midpoint and relative *variances* are \(O(\epsilon^2)\). It does not state
that:

1. \(Z_0\sim N(z_0,\epsilon^2s_0^2)\);
2. \(R_{\parallel,0}\sim N(r_{\parallel,0},\epsilon^2u_0^2)\);
3. \(R_{\perp,0}\) is a wrapped Gaussian with a declared positive-definite
   covariance; and
4. these initial variables, and the corresponding quotient Brownian drivers,
   are mutually independent.

The omission breaks two written implications.

- Variance bounds alone do **not** imply
  \(q_0\in L^2(\pi_\epsilon^{-1}\,dx)\). For example, a normalized
  polynomial-tailed density can have finite, arbitrarily small variance while
  \(\int q_0^2/\pi_\epsilon=\infty\) against a Gaussian invariant density.
  Thus TeX lines 450--453 and 896--909 are false for the initial-law class
  actually stated.
- The exact product
  \(g_{j,\epsilon}(t)=c_{d,\epsilon}(t)a_{j,\epsilon}(t)\) and the Gaussian
  convolution in Eq. (physicalclock) require midpoint/relative independence
  and a Gaussian midpoint law. They do not follow from the listed variances.

The theorem note contains the missing assumptions and shows that the intended
repair is local, but a paper reader cannot be required to import an unpublished
repository note to complete a theorem.

**Required repair.** Before Eq. (narrowslabs), state the full mutually
independent product law exactly as in Eqs. (2.1), (2.5), and (2.6) of the note,
including positive definiteness of the transverse covariance and independence
from the Brownian drivers. Define the fixed-\(\epsilon\) invariant density
\(\pi_\epsilon\), Gaussian in the two unbounded OU coordinates and uniform on
the torus. Then say explicitly that exponent comparison for these *Gaussian*
factors gives \(s_0^2<D_0/\gamma\) and \(u_0^2<4D_0/\gamma\), and that
independence yields the exact contact-times-midpoint factorization. Amend the
Appendix phrase “the initial density” to “the declared Gaussian initial
density.”

Acceptance test: the theorem and proof must remain true if the reader sees only
the manuscript, with no appeal to the Markdown note.

## P1 findings

### P1.1: the Weyl/rank paragraph is under-specified at the displaced root

**Locations:** TeX lines 362--394; compare pde_mixed_jet_theorem.md lines
706--911.

The contraction part is correct: its two displayed hypotheses make
\(x\mapsto x-A_0^{-1}H_B(x)\) a contraction of the closed ball into itself.
There is exactly one zero **in that ball**, with the stated displacement bound.
No false global uniqueness claim was found.

The following Weyl sentence, however, writes \(R_B\) without defining its rows
or evaluation point and compares \(R_B\) with \(R_0\) without saying whether
both are evaluated at the same \(x\), uniformly on the ball, or at \(x_B\) and
\(x_0\), respectively. The abbreviated condition “an operator-norm error at
most \(\sigma_2(R_0)/2\)” is not a sufficient standalone hypothesis for rank
at the displaced root unless the evaluation point is fixed or its displacement
is also controlled.

**Required repair.** Define

\[
R_B(x)=
\begin{pmatrix}
\nabla_\theta(F_B)_t(x)\\
\nabla_\theta(F_B)_{tt}(x)
\end{pmatrix}
\]

in one fixed dimensionless tangent metric. Then use either the region form

\[
s_*=\inf_{x\in\overline{B_r(x_0)}}\sigma_2(R_0(x))>0,\qquad
\varepsilon_R(B)=\sup_x\|R_B(x)-R_0(x)\|_2,
\]

which gives
\(\inf_x\sigma_2(R_B(x))\ge s_*-\varepsilon_R(B)\), or reproduce the note's
displaced-root bound with the \(R_0\) Lipschitz term. Also retain the note's
scale statement: the raw response for \(f_B\) is \(B R_B\), so rank may persist
while its absolute smallest singular value and event rate vanish as
\(B\downarrow0\). State that all norms use a frozen nondimensionalization;
otherwise the numerical constants depend on mixing time and control units.

### P1.2: bressloff2022feynmanKac combines a preprint title with a different final-paper DOI

**Location:** references.bib lines 152--161; cited at TeX lines 318--322.

The entry title

> Diffusion-mediated surface reactions, Brownian functionals and the
> Feynman--Kac formula

is the title of arXiv:2201.01671, not the publisher title attached to DOI
10.1088/1751-8121/ac5e75. The final Journal of Physics A paper at that DOI is

> Diffusion-mediated absorption by partially-reactive targets: Brownian
> functionals and generalized propagators.

The final paper still supports the nearby occupation-time/boundary-local-time
claim, so this is a provenance mismatch rather than a failure of scientific
support.

**Required repair.** Prefer the peer-reviewed record and replace the title by
the final publisher title while retaining journal 55, issue 20, article 205001,
year 2022, and the DOI. Alternatively, cite the arXiv item as a separate
preprint entry with its own identifier and do not attach the journal DOI to the
preprint title.

Publisher/primary checks:

- final DOI: <https://doi.org/10.1088/1751-8121/ac5e75>;
- author preprint carrying the current title:
  <https://arxiv.org/abs/2201.01671>.

## P2 findings

### P2.1: both Ryu entries name the wrong scientist

**Locations:** references.bib lines 163--183.

Both papers were written by **Seungoh Ryu**, not “Seunghwa Ryu.” The latter is
a different researcher's name. The DOIs, titles, journals, volumes, issues,
article numbers, and years otherwise agree with the publisher records.

**Required repair.** Change the author in both entries to “Ryu, Seungoh.”

Primary/publisher checks:

- APS Physical Review E issue record:
  <https://journals.aps.org/pre/issues/80/2/deliverables/table-of-contents/online>;
- APS Physical Review Letters issue record:
  <https://journals.aps.org/prl/issues/103/11/deliverables/table-of-contents/print>.

### P2.2: Ray--Lindsay supports classical mixture-modality analysis, not the claimed determinant ancestry

**Locations:** TeX lines 405--407; references.bib lines 207--216.

Ray and Lindsay (2005) is correctly identified by DOI and is a strong primary
source for analytical modality/topography criteria for normal mixtures. Its
main machinery is the ridgeline and curvature function. A full-text search of
the primary paper does not supply the generic three-channel Wronskian-like
determinant claimed in the sentence “A determinant description of mixture
modality is classical.” The manuscript's determinant identity may be correct,
but that exact historical wording is not supported by this citation.

**Required repair.** Write instead:

> Analytical modality criteria for finite mixtures are classical
> [Ray--Lindsay]; the following Wronskian-like determinant and its
> conserved-simplex identity are specific to the present encounter clocks.

Primary paper: <https://doi.org/10.1214/009053605000000417>.

### P2.3: a caption disclaimer does not fully cure the B=0 panel label “observability”

**Location:** TeX lines 652--665.

The prose now consistently distinguishes
\(G=\lim_{B\downarrow0}f_B/B\) from a positive-event-mass Doi law, and the
caption explicitly disclaims the legacy word. That is logically honest. For a
strong-journal figure, however, leaving “observability” inside the plotted
panel while explaining it away in the caption is avoidable semantic friction
and invites exactly the \(B=0\) versus event-mass confusion the text is
designed to prevent.

**Required repair.** Regenerate the figure with “relative shape gates” or
“relative peak/valley gates” in the panel itself, then refresh the figure hash,
metadata, source pin, and manuscript provenance chain. Do not change the frozen
scientific result.

### P2.4: “bounded at-least-m statement” is domain-ambiguous in an unbounded-cylinder theorem

**Location:** TeX lines 539--542.

Here “bounded” evidently means that \(m\) is fixed and finite, but the theorem
is posed on an unbounded OU cylinder and the manuscript later contrasts it with
a bounded reflected G1 box. This single adjective weakens an otherwise clean
domain separation.

**Required repair.** Replace “the bounded at-least-\(m\) statement” by “the
fixed-finite-\(m\), at-least-\(m\) statement.”

## Attacks that passed

1. **At-least-\(m\) and sequential limits:** abstract lines 59--66, theorem
   lines 500--537, ledger line 823, and Discussion lines 850--859 consistently
   state a fixed finite \(m\), an \(m\)- and \(\epsilon\)-dependent slab family,
   first sufficiently small \(\epsilon\) and then sufficiently small positive
   \(B\), at least \(m\) maxima, possible extra extrema, and no absolute
   event-mass floor.
2. **Contact-interior scope:** the abstract, theorem construction, limitations,
   ledger, and Discussion all retain it. No arbitrary localized-patch or
   arbitrary-\(d\) theorem is claimed.
3. **Contraction/uniqueness:** the displayed contraction hypotheses are
   sufficient for a unique zero in the declared closed ball. The text does not
   promote this to global uniqueness.
4. **\(B=0\) versus event mass:** apart from P2.3, the manuscript consistently
   calls the four-slab result a normalized free-exposure shape confirmation,
   not a reaction-time probability density. Positive-\(B\) event mass remains
   a separate gate, and the direct theorem correctly states
   fixed-\(\epsilon\) local mass as \(B\) times free-exposure area plus
   \(O(B^2)\).
5. **Unbounded model versus G1 box:** TeX lines 549--596 and 744--809
   explicitly distinguish the exact unbounded OU cylinder from the reflected
   G1 truncation, print the G1 bounds, deny a box-to-unbounded limit, and keep
   the two parameter families separate. P2.4 is the only residual wording leak.
6. **Title, abstract, and Discussion:** the working title is appropriately
   weaker than a finite-parameter positive-\(B\)/dimension-robust claim. The
   abstract is evidence-layered, and the Discussion does not claim one fixed
   geometry realizes arbitrary mode counts.
7. **Luca/companion ancestry:** the 2013 PRL and 2020 PRX records have correct
   DOI metadata and are cited near the lattice/encounter ancestry. The two
   companion manuscripts are not used as independent validation. Public
   identifiers, editor-facing copies, and an author-approved overlap map remain
   explicit release gates. This passes only for the internal draft, exactly as
   Round 28 says.
8. **Other newly added references:** the checked Prüstel--Meier-Schellersheim,
   Grebenkov residence/local-time, Grebenkov multiple-local-time,
   Ray--Lindsay, Giuggioli--Pérez-Becker--Sanders, and Giuggioli PRX DOI
   metadata agree with their publisher/primary records. Their nearby claims are
   appropriately bounded after the Ray--Lindsay wording repair above.

## Release decision

**HOLD.** Close P0.1 first, then P1.1 and P1.2, then the four P2 items. A clean
compile and provenance pass after those textual/figure repairs would close this
Round 29 audit, but would still not close the separately declared
positive-\(B\), event-mass, continuum-convergence, independent-solver,
physical-\(d=3\), or companion-disclosure release gates.
