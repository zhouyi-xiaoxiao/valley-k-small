# Round 27: adversarial PRR manuscript attack

Date: 2026-07-13  
Scope: `manuscript/encounter_multimodal_prr.tex`, generated numerical macros,
the four-slab, G1c, and G1d pinned results and audits, the direct physical
multimode theorem and its audit, the novelty/overlap notes, and the current
bibliography.  No manuscript or scientific artifact was edited in this round.

## 1. Verdict

**HOLD for scientific revision; the current text is not yet safe as a PRR
submission manuscript.**

The pinned numerical values are transcribed correctly and the manuscript has a
substantially better claim firewall than the earlier working draft.  In
particular, it does not call the four-slab calculation a finite-
\(B\) killed-Doi result, does not call the G1d fold a continuum result, and
keeps the physical-\(d=3\), independent-solver, mesh/box, and event-mass gates
open.

Two stop-ship problems remain.  First, the displayed weak-budget theorem is
stated in the unweighted bounded-domain norm but is then applied to the
unbounded Gaussian OU cylinder without stating the weighted-space corollary or
changing the norms.  Second, the Discussion promotes an at-least-\(m\),
\(m\)-dependent, epsilon-dependent slab construction into language that reads
as an exact mode-count realization by conserved reactivity with fixed
transport.  The proof does not establish that stronger statement.

Severity ledger:

| Severity | Count | Meaning |
|---|---:|---|
| P0 | 2 | theorem/claim defects that must be repaired before circulation as a scientific manuscript |
| P1 | 8 | submission-blocking scope, novelty, evidence, or narrative defects |
| P2 | 4 | local notation, wording, table, or provenance defects |

The present title and abstract are too strong for the current evidence package.
A safe working title is proposed in Sec. 6 below.

## 2. Evidence that does survive attack

The following checks passed and should be preserved during revision.

1. The generated macros pin the current result hashes exactly:
   - four-slab result
     `4a929cdaf915a9b6180acc0c272a16ae77087d097f2d078b6483c6c9b320a9fc`;
   - G1c result
     `cce1e34c599564dc932da6af4d4146c2c396836990e9b51414fc2f843e123bb4`;
   - G1d result
     `268e3f988330a2f28ad79b22cdf1f7e53a0142dc007d2a2a7cbfe40d18f91f92`.
2. The four-slab cusp time, weights, scaled fourth derivative, unfolding SVD
   ratio, selected step, selected weights, five reported sign-changing roots,
   peak ratio, and valley ratios in lines 615--669 agree with the pinned
   artifact and Round 25.
3. The G1c counts in lines 725--729 agree with the pinned result and Rounds
   22--24: 66 controls, 165 edges, three eligible interior interpolated seeds,
   45 equal-retained-root-count review edges, and eight one-versus-three
   retained-root transitions.
4. The G1d fold coordinates, weights, density, complete scaled jet, and
   dimensionless Jacobian determinant in lines 734--754 agree with the pinned
   artifact and Rounds 25--26.
5. The current PDF is a clean, byte-reproducible nine-page build with no
   missing files, undefined citations/references, overfull boxes, Type-3 fonts,
   or unembedded fonts.  This remains build evidence, not a scientific gate.

## 3. P0 findings

### P0.1: the unbounded Doi transfer is not stated in the norm in which it is used

**Locations:** lines 324--330, 358--374, 434--435, 500--503, and 846--859.

Lines 324--330 explicitly introduce a **bounded reflected** quotient and
unweighted \(L^2\) data.  Lines 360--373 define
\(v_{2,\delta}=\sup\|V_w\|_2\), a bounded-domain similarity constant
\(\kappa_\pi\), and the unweighted norm \(\|q_0\|_2\).  The direct theorem then
uses the same displayed estimate on
\(\mathbb R^2\times\mathbb T_W^{d-1}\) in lines 434--435 and 500--503.

That inference is not valid from the displayed theorem as written.  On the
unbounded OU cylinder, multiplication by the invariant Gaussian is not a
bounded similarity on unweighted \(L^2\).  The audited theorem instead uses

\[
 X_\pi=L^2(\pi^{-1}\,\mathrm dx),\qquad
 \|V\|_{X_\pi^*}=\|V\|_{L^2(\pi\,\mathrm dx)},
\]

with the map \(u\mapsto q=\pi u\) unitary and \(\kappa_\pi=1\).  The appendix
mentions an "unbounded mixed-jet theorem" in line 859, but the manuscript never
states it, and Eq. (weakbridge) still displays the bounded-domain norms.

**Required repair.**  Add a formal unbounded corollary immediately after
Eq. (weakbridge): define
\(\mathcal Q_d^\infty=\mathbb R^2\times\mathbb T_W^{d-1}\), its Gaussian
invariant density, \(X_\pi\), the dual observable norm, and the stronger initial
law hypothesis.  State that the same mixed-jet estimate holds with
\(\kappa_\pi=1\), \(v_{2,\delta}\) replaced by the weighted dual norm, and
\(\|q_0\|_2\) replaced by \(\|q_0\|_{X_\pi}\).  Then cite that corollary, not the
bounded formula without qualification, in lines 500--503 and 897--900.  Also
replace "the bounded ... quotient introduced below" in lines 325--327: the
model introduced at lines 568--599 is the unbounded physical cylinder, while
the finite-volume experiments use a bounded reflected truncation.

Until this is inserted, the positive-\(B\) transfer step of the direct theorem
is not self-contained in the manuscript even though it is correct in the
audited theorem note.

### P0.2: the Discussion upgrades an at-least-mode theorem into an exact and causally broader realization claim

**Locations:** lines 807--815, reinforced by lines 55--63 and 96--98.

Lines 809--812 say that encounter operators "realize every prescribed fixed
finite mode count under a conserved physical budget."  The audited theorem
proves only **at least** \(m\) maxima and explicitly does not exclude early,
late, or interstitial extrema.  It also uses an \(m\)-dependent family in which
\(\epsilon\) scales both the OU transport noise and the catalyst width, with
centres chosen from the target times.  Thus it is not a statement that
reactivity redistribution alone, in one fixed transport/geometry, realizes
each exact global mode count.

The next clause, "the essential mechanism," is also too broad: the construction
deliberately keeps the deterministic relative trajectory inside contact near
all designed peaks.  It embeds localized exposure clocks in an exact encounter
operator but does not establish that nontrivial approach/separation encounter
dynamics are the universal mechanism.

**Required replacement for lines 809--812:** substantially use

> For each prescribed fixed finite \(m\), the direct theorem constructs an
> \(m\)-dependent longitudinal-slab OU quotient whose Doi density has at least
> \(m\) nondegenerate maxima after first choosing a sufficiently small joint
> noise/slab-width parameter \(\epsilon\) and then a sufficiently small positive
> budget.  The construction does not fix one transport/geometry across \(m\),
> does not determine the global number of modes, and deliberately keeps the
> relative deterministic path inside contact near the designed peaks.

The sentence at lines 96--98 must be qualified as applying **within each fixed
control family**.  Otherwise it conflicts with the theorem construction, which
varies transport noise and supports across \(\epsilon\) and \(m\).

## 4. P1 findings

### P1.1: the abstract omits the theorem's decisive hypotheses and mislabels epsilon

**Locations:** lines 53--65.

The abstract says "for every ... target times" but omits the monotone midpoint
path and contact-interior condition.  It then calls the first sequential
parameter a "geometry parameter," although Eqs. (narrowou)--(narrowslabs) make
\(\epsilon\) scale transport noise, initial variances, and slab width.  This
matters because "holding transport fixed" is the paper's causal premise.

**Required repair.**  Say that the claim is made for target times satisfying
the declared monotone-path/contact-interior condition, in an \(m\)-dependent
family where \(\epsilon\) jointly scales OU noise and slab width; only after
that family member is fixed does \(w\) become the sole control and \(B\) tend
to zero.  Retain "at least," the sequential order, and the statement that extra
extrema are not excluded.  Do not use "geometry parameter" for \(\epsilon\).

### P1.2: "observable" is used for a B=0 shape test with no reaction event mass

**Locations:** subsection title at line 601; lines 644--648, 654--661, 670--674,
784, 795--800, and especially 812--820.

The four-slab artifact is the \(B=0\) derivative per unit installed budget,
\(G=\lim_{B\downarrow0}f_B/B\).  Its declared gates constrain relative peak
height and two valley ratios.  They do not give a Doi event-mass floor, and
\(G\) is not a probability density normalized on the full half-line.  Round 25
therefore keeps `finite_B_Doi_verified=false` and the direct theorem notes that
fixed-window event mass is \(O(B)\).

Calling this an "observable trimodal continuum-kernel example" at lines
812--814 invites a physical-observability interpretation that the artifact
does not support.  The later statement that event mass is still missing does
not fully undo the headline wording.

**Required repair.**  Use "relative-prominence-qualified free-exposure
confirmation" or "passes the declared B=0 shape gates" throughout.  At the
start of the subsection define the plotted object explicitly as \(G\), the
\(B=0\) budget-normalized derivative, and state that no event-mass
observability claim is made.  Reserve "observable reaction-time modes" for a
positive-\(B\) computation that passes an absolute event-mass floor.  Rewrite
lines 812--815 to say that the result-informed calculation exhibits three
relative-prominence-qualified maxima on the declared floating-point screen,
not an observable finite-\(B\) reaction-time law.

### P1.3: G1c/G1d root counts and evidence timing are stronger in the text than in the artifacts

**Locations:** lines 725--760 and the G1d abstract clause at lines 71--75.

The G1c counts are counts of **retained sign-changing roots on the frozen
\(\Delta t=0.25\) screen**, not global critical-point counts.  Likewise, the
G1d side values 3 and 1 are retained strict sign-changing roots on
\(t\in[3,18]\) with \(\Delta t=0.02\); Round 25 explicitly says they do not
exclude an even-multiplicity root or a sub-grid pair.  Lines 755--757 currently
state unqualified root topology.  This contradicts Round 26's assertion that
the manuscript had adopted the sign-changing-screen wording.

The G1d artifact also says
`POST_RESULT_CONFIRMATION_NOT_PREREGISTERED_DISCOVERY`.  "Separately frozen" in
the abstract and line 734 is not enough: the segment was selected after G1c.

**Required repair.**  Replace the relevant statements by:

- "eight edges with one versus three retained sign-changing roots on the
  frozen G1c screen";
- "the frozen G1d sign-changing-root screen retains max--min--max at
  \(\lambda_f-0.02\) and one maximum at \(\lambda_f+0.02\); this is not a
  global root census"; and
- "a result-informed, post-G1c confirmation whose numerical choices were
  prospectively frozen before execution, not a preregistered discovery."

The same discipline should be applied to the four-slab sentence at lines
633--648: say that the declared \([0.1,100]\), \(\Delta t=0.002\) screen retains
five alternating simple roots; the existing interval-certificate caveat then
has a concrete referent.

### P1.4: the unbounded physical model and bounded zero-flux finite-grid model are conflated

**Locations:** lines 565--599 and 682--705.

Lines 568--599 present particles on \(\mathbb R\times\mathbb T_W\) and an
unbounded quotient.  The G1 finite-volume solver instead represents both
longitudinal coordinates by one finite zero-flux box.  Its own smoke artifact
lists this as a limitation, and G1d is explicitly a result on one finite box.
The manuscript describes SG fluxes and a mesh but never states the finite box
or reflecting truncation before reporting the fold.

**Required repair.**  Define two objects separately:

1. the unbounded physical OU cylinder used by the exact free kernels and the
   direct theorem; and
2. the bounded reflected box used by G1a--G1d, with its actual box limits and
   the statement that no box-to-unbounded convergence has been shown.

Do not call the G1d model merely a mesh version of Eq. (quotient).  The fold is
for a distinct bounded-box Doi model until box convergence is completed.

### P1.5: the manuscript asserts quantitative persistence without stating the quantitative theorem

**Locations:** abstract lines 63--65 and main text lines 376--380.

The text says that quantitative contraction and Weyl bounds transfer modes,
folds, cusps, and rank, and the abstract calls these "exact fold/cusp
persistence criteria."  The manuscript displays the \(O(B)\) scalar mixed-jet
bound but never states the contraction hypotheses, the finite-dimensional norm
assembly, the simplex-interior ball, or the Weyl rank floor.  Those details
exist only in `notes/pde_mixed_jet_theorem.md` and its audit.

**Required repair.**  Add a concise proposition for the fold map
\((F_t,F_{tt})\) and cusp map \((F_t,F_{tt},F_{ttt})\).  It must specify a
closed ball inside positive time and the simplex interior, an inverse-Jacobian
margin \(\mu\), residual and derivative perturbation bounds that make the
Newton map a contraction, and the resulting displacement/nondegeneracy bound.
For the two-row projected response, state explicitly
\(\sigma_2(R_B)\ge\sigma_2(R_0)-\|R_B-R_0\|_2\) and assemble entrywise Cauchy
bounds into the operator norm.  Otherwise weaken the abstract to say only that
the estimate supplies a route to persistence under separately stated
nondegeneracy hypotheses.

### P1.6: novelty language and bibliography do not implement the repository's own collision audit

**Locations:** lines 96--106, 350--407, and the 13-entry bibliography.

"Their unestablished intersection" at lines 105--106 is an unqualified absence
claim.  The novelty audit permits only a targeted-search inference and says the
weak-budget ingredients are standard.  It also requires primary citations at
the point of use.  The current bibliography contains Nguyen--Grebenkov but is
still missing:

- Prüstel--Meier-Schellersheim (2014), area reactivity and the reaction-density
  equals reactivity-times-occupancy identity;
- Bressloff (2022), the published occupation-time/interior-absorption paper;
- Ryu (2009) and Ryu--Johnson (2009), perturbative nonuniform reactivity;
- Grebenkov (2007) and Grebenkov (2020), occupation/multiple-local-time
  functionals; and
- Ray--Lindsay (2005), established mixture-modality geometry.

**Required repair.**  Replace "unestablished" by a bounded statement such as
"the intersection targeted here; a targeted primary-source search did not
locate the complete chain, which is not proof of absence."  Cite the
area/occupation predecessors at Eq. (freeexposure), the perturbative-reactivity
papers near the sensitivity equations, and Ray--Lindsay near the determinant.
Replace lines 405--407 by the safer wording already recommended in Round 20:
these standard ingredients provide a model-specific route from a quantified
free-exposure singularity to a nearby weak-Doi singularity; a finite-budget
observable realization remains a separate gate.

### P1.7: title and narrative architecture promise more than the current result, while inherited GIG material is over-weighted

**Locations:** title line 43; abstract lines 53--77; GIG sections 182--250 and
520--563; Discussion 805--825.

The title reads as a completed finite-parameter physical design result.  The
current finite-parameter four-slab object is only \(B=0\) free exposure, the
positive-\(B\) fold is only one bounded finite grid, and \(d=3\) numerics have
not run.  The only positive-\(B\) continuum result is a sequential small-
\(\epsilon\), small-\(B\), slab-symmetry existence family.

At the same time, two long GIG sections occupy prime manuscript space although
the overlap map classifies the formula, parameter lineage, and numerical
screening as shared with the companion encounter work.  The genuinely new
physical program is therefore diluted and exposed to a salami/overlap attack.

**Required repair.**  Until the finite-\(B\), independent-solver, and \(d=3\)
gates pass, use a title such as

> Conserved-reactivity control of encounter-time modality: weak-reaction
> theory and continuum-kernel designs

Move the inherited GIG numerical scan and optional global bridge to an appendix
or companion/Supplemental Material, retaining only the reduced theorem as a
short design lemma with explicit ancestry.  Lead the abstract and Discussion
with the conserved centre-space budget, the exact encounter-specific channel
factorization/discriminant, and the evidence hierarchy—not with generic
mixture flexibility.

### P1.8: Luca/companion-paper ancestry is acknowledged internally but not release-ready

**Locations:** lines 89--94 and 116--124; acknowledgments lines 827--830.

The manuscript cites the 2024 chapter and the 2025 network preprint, but not
the foundational Giuggioli--Pérez-Becker--Sanders two-walker encounter paper
(PRL 110, 058103) or Giuggioli's confined arbitrary-dimensional propagator
paper (PRX 10, 021045).  The companion manuscripts are described without
public identifiers, editor-facing copies, or a final equation/code/figure
overlap statement.  This is acceptable only because the PDF is explicitly an
internal draft.

**Required repair before submission.**  Add the two primary Luca citations,
replace repository-style descriptions by an author-approved related-work
statement, provide unpublished related manuscripts to the editor under journal
policy, and include a precise reused-versus-new equation/code/data/figure map.
No companion artifact may be described as an independent validation of this
paper.

## 5. P2 findings

### P2.1: the four-slab mixture is denoted by an undefined F

**Location:** lines 615--624.

The manuscript defines \(F_B=f_B/B\) and its \(B=0\) limit \(G\), but the
four-slab subsection solves \(F_t=F_{tt}=F_{ttt}=0\) without defining an
unsubscripted \(F\).  Use \(G\) consistently (including \(G^{(4)}\)) or define
\(F\equiv G\) locally.  Using \(G\) is preferable because it reinforces the
\(B=0\) evidence boundary.

### P2.2: two local descriptions are imprecise

**Locations:** lines 463--469 and 644--648.

1. \(S^2(t)\) is not the "\(O(\epsilon^2)\) midpoint-variance coefficient plus
   \(\rho^2\)."  It is the coefficient \(s^2(t)+\rho^2\), while the physical
   convolved variance is \(\epsilon^2S^2(t)\).
2. The declared \(0.10\) peak gate is not an absolute floor passed separately
   by each maximum.  It is
   \(\min(P_1,P_2,P_3)/\max(P_1,P_2,P_3)\ge0.10\).  State the ratio gate
   exactly.  The reported value \(0.85413\) is correct.

### P2.3: the gate table compresses away essential scope and uses ambiguous status labels

**Locations:** lines 770--793.

The fixed-finite-\(m\) row omits the contact-interior assumption and sequential
small-\(\epsilon\)/small-\(B\) order.  The four-slab row says "observable three
modes" despite no event mass.  The G1d row omits post-result/result-informed
timing and finite-box scope.  "PROVED CONDITIONAL" for the weak-
\(B\) theorem conflates a proved theorem with its conditional application.

Expand the scope cells and use, for example, "PROVED; APPLICATION REQUIRES
MARGINS" for weak-\(B\), "PASS RESULT-INFORMED B=0 SHAPE CONFIRMATION" for the
four slabs, and "PASS ONE BOUNDED FINITE GRID" for G1d.

### P2.4: the PDF compile manifest does not close the full source-to-PDF hash chain

The macros and figure metadata are well pinned, but
`artifacts/data/manuscript_compile.json` records the numerical-input hash and
PDF hash without recording the TeX, bibliography, or included-figure hashes.
At audit time the relevant hashes were:

- TeX: `dec9f8c955089bb6a4c25516012d666ab252dd6fd04f6a4e7d97583da1e962cf`;
- bibliography:
  `656ebc7235e16e2785e4f55c4afa25804f0842c65411284873bc0d63d0d5df98`;
- numerical macros:
  `cabe57b3651ed1c1d85062935a3c6285824a13c71558046e32d31005b64878b6`;
- included four-slab PDF:
  `08bcf55aa8a5b6e97bf313814e006b491aa171f7870b2795c694c9977f9f3bfc`;
- manuscript PDF:
  `cc2a2710a6da0e80e9065b5ef98708496c106c8911d3d17f1a2dfdeca17ec937`.

Update the build manifest generator to pin every transitive manuscript input,
including figure metadata/result pins, rather than relying on filesystem
coincidence.

## 6. Title and abstract decision

### Current title

`Designing multimodal encounter-reaction times under conserved spatial
reactivity` is **too strong as a submission title now**.  It suppresses all of
the distinctions that currently keep the paper honest: longitudinal slabs,
sequential weak noise/reaction in the direct theorem, \(B=0\) in the four-slab
example, one finite box for G1d, and absent \(d=3\) numerics.

Safe current working title:

> Conserved-reactivity control of encounter-time modality: weak-reaction
> theory and continuum-kernel designs

Safe stronger title only after the positive-\(B\), continuum/independent-solver,
and \(d=3\) gates pass:

> Conserved-reactivity control of cusp-organized encounter-time modality in
> two and three dimensions

### Required abstract structure

A safe abstract should make the evidence ladder explicit in this order:

1. Within each fixed family, only the nonnegative catalyst weights vary under
   one centre-space integral budget.
2. The direct theorem is for fixed finite \(m\), admissible target times, an
   \(m\)-dependent slab family, and sequential \(\epsilon\) then \(B\); it gives
   at least \(m\), not exactly \(m\), with no event-mass floor.
3. The four-slab result is a result-informed \(B=0\) free-exposure
   confirmation passing relative shape floors, not an observable reaction-time
   law.
4. G1d is a post-result, result-informed fold on one bounded reflected
   \(207025\)-state grid at \(B=0.6\), not continuum persistence.
5. Positive-\(B\) four-slab event mass, box/mesh convergence, independent
   solver, and physical \(d=3\) remain release gates.

## 7. Minimum repair order

1. Repair P0.1 by stating the unbounded weighted-space theorem in the
   manuscript and applying the correct norms.
2. Repair P0.2 and P1.1 by rewriting the abstract, premise paragraph, and
   Discussion to preserve at-least-\(m\), the joint epsilon scaling, and the
   contact-interior/slab scope.
3. Remove physical-observability language from the \(B=0\) result and make
   event mass a distinct positive-\(B\) gate.
4. Adopt retained-sign-changing-root and result-informed wording for G1c/G1d.
5. Separate the unbounded physical cylinder from the bounded reflected
   finite-volume box.
6. Add the quantitative persistence proposition and the missing primary
   novelty/ancestry citations.
7. Compress inherited GIG material, revise the title/table, and close the
   source-to-PDF provenance chain.

After these repairs, another claim-by-claim audit is warranted.  The manuscript
should remain `release_eligible=false` even if all textual findings close,
because the positive-\(B\) four-slab, continuum convergence, independent
solver, event-mass, and physical-\(d=3\) scientific gates are still open.
