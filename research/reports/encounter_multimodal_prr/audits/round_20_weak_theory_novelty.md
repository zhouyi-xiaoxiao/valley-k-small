# Round 20 targeted novelty collision audit: weak-budget and direct OU theorems

Date: 2026-07-13  
Scope: the proposed compact-positive-time result

\[
 B^{-1}f_B(t,w)=\langle V_w,T_0(t)q_0\rangle+O(B)
\]

through fixed mixed time/control jets, on a fixed physical-reactivity simplex,
together with the factorized free-exposure cusp determinant and quantitative
fold/cusp/rank persistence. The added scope is the direct small-noise OU
construction of any prescribed finite number of modes using normalized narrow
catalyst slabs. Only primary research papers were used as literature
evidence. The audited repository sources were:

- **notes/literature_gap_20260713.md**;
- **notes/pde_mixed_jet_theorem.md**;
- **notes/direct_physical_multimode_theorem.md**; and
- **manuscript/encounter_multimodal_prr.tex**, especially the section
  “Weak-reactivity continuum bridge and remaining global target”.

No TeX file was changed in this audit.

## 1. Executive verdict

### Novelty verdict

**AMBER-HIGH if the weak-budget theorem is presented as a standalone new
Feynman--Kac, weak-reaction, fixed-resource, or perturbation principle.**

**GREEN/AMBER as an enabling theorem in the proposed physics paper, but only
after a nontrivial physical free-exposure singularity is certified and
continued to observable finite \(B\), physical \(d=2\) and \(d=3\), with an
independent continuum solver.**

The most important new collision found in this round is Nguyen and Grebenkov
(2010). That paper already treats reflected diffusion with a spatially
heterogeneous **bulk** killing field, gives the full survival-time law in a
spectral/Feynman--Kac representation, asks how to arrange reactive regions at
fixed total reactive strength, and uses small-reactivity perturbation theory.
It is closer to the present weak-budget construction than the surface-flux
optimization paper currently emphasized in the manuscript.

Consequently, none of the following can carry novelty on its own:

1. a Doi/area-reactivity sink or its Feynman--Kac representation;
2. the leading weak-killing identity “reaction density divided by reactivity
   equals unreacted exposure”;
3. heterogeneous bulk or boundary reactivity;
4. a fixed total amount of bulk or surface reactivity;
5. perturbation of a diffusion/reaction spectrum by nonuniform reactivity;
6. mixture-mode analysis, a generic fold/cusp normal form, an inverse-function
   persistence argument, or a Weyl singular-value bound.

The targeted searches did **not** locate a primary paper that assembles all of
the following in one physical problem:

- two-mobile-particle encounter dynamics with transport, geometry, contact
  scale, and initial law fixed;
- redistribution of a static nonnegative centre-space Doi field on a physical
  integral simplex;
- an explicit compact-positive-time \(O(B)\) estimate for the complete
  time/control jet needed by a density cusp;
- a resource-tangent rank margin and quantitative fold/cusp persistence; and
- an independently converged physical-\(d=2\)/\(d=3\) modality phase diagram.

That absence is a **search inference, not a proof of novelty**. The safe
contribution is the complete model-specific assembly and its realized physical
consequence, not any one lemma in the assembly.

### Manuscript verdict

**PASS WITH REQUIRED CITATION AND POSITIONING REPAIRS; PRR GATE REMAINS HOLD.**

The new manuscript section is mathematically disciplined: it explicitly calls
the semigroup ingredients standard, limits the theorem to
\([\tau,T]\), rejects an application to \(B=0.6\), and does not claim
global-time normalization or a finite-\(B\) cusp. Its principal weakness is
literature coverage. The introduction and weak-bridge section omit the closest
bulk predecessor, and the literature note cites a preprint version of
Bressloff rather than the published primary paper.

The theorem alone is not a PRR-level headline. It becomes PRR-useful if it is
the rigorous bridge from a certified, observable free-exposure design to a
finite-\(B\) two-particle cusp/fold manifold and a dimension-resolved numerical
result.

If its proof survives technical audit, the direct OU/narrow-slab theorem
improves the project more than the reduced GIG construction because it would
give an exact continuum Doi realization for each fixed finite \(m\). Its
**complete combination was not located in the targeted primary literature**,
so the theorem is provisionally search-distinct.
However, its phenomenon-level ingredients collide strongly with established
work: strategically separated narrow traps already generate multimodal
continuum capture densities, exact OU Gaussian localization is standard, and
separated Gaussian mixtures can have arbitrarily many modes. The safe status
is therefore **YELLOW/GREEN as a model-specific existence theorem, not a
standalone PRR headline**. Section 9 gives the full direct-route audit.

## 2. Decisive P0 collision: heterogeneous bulk killing at fixed strength

### Nguyen and Grebenkov, Journal of Statistical Physics 141, 532--554 (2010)

Primary paper: [DOI 10.1007/s10955-010-0054-1](https://doi.org/10.1007/s10955-010-0054-1);
[author PDF](https://pmc.polytechnique.fr/pagesperso/dg/publi/2010_06.pdf).

This paper considers reflected Brownian motion in a bounded domain with a
spatially varying bulk reaction/relaxation rate \(B(x)\). Its Kac functional
is

\[
 \phi_t=\int_0^t B(X_s)\,ds,
 \qquad S_h(t)=\mathbb E[e^{-h\phi_t}],
\]

and the corresponding PDE has the sink \(hB(x)\). The paper gives a
multi-exponential representation of \(S_h\), explicitly interprets
\(-\partial_tS_h\) as the density of the finite-reactivity survival/reaction
time, and asks for the optimal shape and arrangement of reactive regions at a
fixed total amount or strength. Appendix D expands the principal reaction rate
to second order in small \(h\), with the first term equal to the total amount
of reactive material and the second term measuring heterogeneity.

This creates four direct collisions:

1. **volume rather than only surface reactivity was already treated;**
2. **the complete survival-time law, not only a mean, was already available;**
3. **fixed total bulk reactive strength was already an explicit design
   constraint;** and
4. **small-reactivity perturbation was already used to compare spatial
   allocations.**

It does **not** derive compact-time mixed time/control-jet error bounds, study
the topology of \(-S_h'(t)\), continue fold/cusp loci, use a two-particle
encounter generator, or validate physical \(d=2\)/\(d=3\) modality. Those are
the remaining distinctions.

This source must be promoted to P0 in the literature note and cited in the
manuscript introduction before any fixed-budget weak-Doi claim.

## 3. Nearest-primary-source collision map

| Priority | Primary source | Established component | Collision risk | Remaining non-overlap |
|---|---|---|---|---|
| P0 | Nguyen & Grebenkov (2010), [DOI](https://doi.org/10.1007/s10955-010-0054-1) | Heterogeneous bulk killing in a reflected domain; Feynman--Kac/spectral full survival law; fixed total reactive strength; small-\(h\) perturbation of the long-time rate. | **High.** It defeats novelty claims based on bulk killing, fixed bulk resource, a full reaction-time law, or small-reactivity perturbation. | No transient modality objective, budget-projected mixed jet, cusp/rank continuation, or two-body encounter realization. |
| P0 | Prüstel & Meier-Schellersheim (2014), [DOI](https://doi.org/10.1063/1.4901115), [arXiv](https://arxiv.org/abs/1405.3021) | Area-reactivity model for an isolated diffusing pair; generalized Feynman--Kac sink; survival and reaction rate. Their exact identity has reaction density/rate equal to intrinsic reactivity times killed occupancy of the reaction area. | **High** for \(B^{-1}f_B\to\) exposure as a physical idea. | Homogeneous reaction area, no fixed allocation simplex, mixed-jet bound, or modality singularity. |
| P0 | Bressloff (2022), [DOI](https://doi.org/10.1088/1751-8121/ac5e75), [arXiv](https://arxiv.org/abs/2201.01671) | Interior partial absorption through occupation-time Brownian functionals and generalized propagators, including discontinuous target indicators and stopping laws. | **High** for claims of first occupation-time/interior partial-absorption formulation. | No conserved heterogeneous allocation or fold/cusp design. |
| P0 | Grebenkov (2019), [DOI](https://doi.org/10.1063/1.5115030), [arXiv](https://arxiv.org/abs/1908.01143) | General continuously varying/piecewise heterogeneous Robin reactivity with propagator, survival probability, and reaction-time density. | **High** for general heterogeneous-reactivity and full-distribution claims. | Surface rather than centre-space Doi resource; no modality bifurcation control. |
| P1 | Grebenkov (2007), [DOI](https://doi.org/10.1103/PhysRevE.76.041139) | Matrix/Feynman--Kac treatment of residence/occupation functionals of reflected Brownian motion, their transforms, moments, and survival interpretation. | **Medium-high** for presenting free exposure or occupation clocks as a new construct. | No resource-constrained timing-modality design. |
| P1 | Ryu (2009), [DOI](https://doi.org/10.1103/PhysRevE.80.026109), [arXiv](https://arxiv.org/abs/0903.1655) | Perturbative effect of spatially nonuniform partial absorption on the diffusion/relaxation spectrum, with bounds on the slowest mode. | **Medium-high** for generic “reactivity response” or perturbation novelty. | Boundary spectrum/long-time modes, not the transient reaction-density control jet or its time modes. |
| P1 | Ryu & Johnson (2009), [DOI](https://doi.org/10.1103/PhysRevLett.103.118701), [arXiv](https://arxiv.org/abs/0903.1653) | Perturbation theory, exact results, and simulations for nonuniform partially absorbing boundaries. | **Medium** for a broad linear-response claim. | No fixed resource, transient modality, or two-body encounter. |
| P1 | Grebenkov (2020), [DOI](https://doi.org/10.1088/1742-5468/abb6e4), [arXiv](https://arxiv.org/abs/2008.12986) | Joint exposure/local-time statistics for multiple boundary subsets, multi-parameter Laplace transform, and related first-passage-time laws. | **Medium** for claiming that multiple patch-specific exposure parameters are new. | Boundary local times rather than a fixed bulk simplex; no mode fold/cusp. |
| P1 | Nicolaou & Mulder (2023), [DOI](https://doi.org/10.1038/s41598-023-49566-4) | Optimization of a spatial Robin-reactivity distribution under a finite total surface resource. | **High** for “first fixed-total-reactivity optimization.” | Steady-state flux objective on a fixed body, not transient reaction-density modality in a two-body Doi model. |
| P1 | Ray & Lindsay (2005), [DOI](https://doi.org/10.1214/009053605000000417) | Rigorous critical-point and modality analysis for mixture densities, including reduced manifolds and curvature criteria. | **Medium** for treating mixture modality or derivative discriminants as a new mathematical topic. | Gaussian statistical mixtures, not free encounter-exposure clocks or physical reactivity control. |
| P2 | Keidar & Reuveni (2026), [PRR article](https://doi.org/10.1103/c7wy-ddrc), [arXiv](https://arxiv.org/abs/2410.16129) | Universal linear response of the **mean** first-passage time to rare perturbations. | **Low-medium.** It makes an unqualified “first linear response of first passage” phrase unsafe. | Rare perturbations and the mean only; not weak spatial killing, the full density jet, or modality. |

The map intentionally excludes reviews as evidence. It also separates
boundary-local-time predecessors from the present bulk Doi field rather than
conflating them.

## 4. Claim-by-claim novelty decomposition

### 4.1 \(B^{-1}f_B=G+O(B)\) at fixed positive time

**Status: RED as a bare leading-order idea; YELLOW as the precise mixed-jet
estimate.**

For Doi killing,

\[
 f_B(t,w)=B\langle V_w,q_{B,w}(t)\rangle.
\]

The Feynman--Kac/Dyson limit \(q_{B,w}\to T_0q_0\) immediately yields
\(B^{-1}f_B\to\langle V_w,T_0q_0\rangle\). Prüstel's area-reactivity
identity and Nguyen--Grebenkov's Kac representation already contain this
physical structure. The first correction is likewise a standard
Duhamel/Dyson term.

What the repository adds is a precise **uniform compact-positive-time error
bound through the entire finite time/control jet needed by the cusp map**, for
the declared operator, \(L^2\) initial law, discontinuous indicator, and
physical simplex. The targeted primary search did not find this exact
statement. However, because its proof uses standard bounded-perturbation and
Cauchy estimates, it should be sold as a model-closing technical theorem, not
as a new general semigroup principle.

### 4.2 Fixed total spatial reactivity simplex

**Status: RED as an isolated novelty claim.**

Nguyen--Grebenkov already impose fixed total bulk reactive strength;
Nicolaou--Mulder impose a fixed total surface-reactivity resource. The new
distinction is narrower: the budget is a resolution-independent centre-space
Doi integral, the support/transport/initial law are frozen, and the objective
is the topology of the transient reaction-time density.

### 4.3 Exact sensitivity PDEs and direct observable terms

**Status: YELLOW enabling theory, not a standalone headline.**

The repository correctly includes the direct terms generated by
differentiating \(V_w\) in the observable. This is important and easy to get
wrong, but it is a correct application of parameter differentiation/Duhamel,
not by itself a novelty claim. Ryu's nonuniform-reactivity perturbation work
and the older Feynman--Kac literature make a broad “first sensitivity” claim
unsafe.

### 4.4 Factorized three-clock cusp determinant

**Status: YELLOW in the model; RED as abstract mixture algebra.**

The conditions

\[
 \det[g',g'',g''']=0,\quad
 \operatorname{rank}[g',g'',g''']=2,
\]

with a positive null vector, a nonzero fourth derivative, and rank-two budget
unfolding are the expected critical-point conditions for a three-component
mixture. The identity relating the derivative of the determinant to the cusp
Jacobian follows by determinant differentiation and a change of basis. It is
useful and elegant, but not a credible general mathematical novelty.

Its publishable role is the **exact encounter-specific factorization**
\(g_j=a_jc_d\), which converts a spatial patch geometry into a cheap candidate
test, followed by a certified physical cusp and finite-\(B\) continuation.
Ray--Lindsay should be used to acknowledge that rigorous mixture-topography
analysis is established, while making clear that their Gaussian setting does
not contain this reaction model.

### 4.5 Quantitative fold/cusp and projected-rank persistence

**Status: RED as general analysis; GREEN/YELLOW as a physical transfer
result.**

Contraction/inverse-function persistence of a nondegenerate zero and Weyl's
singular-value inequality are standard. The targeted search did not locate
their use for conserved-reactivity reaction-density cusps, but that does not
make the general lemmas new. The valuable result is a computed nonempty
interval

\[
 B_{\rm obs}\le B\le B_*
\]

on which (i) a physical free-exposure singularity persists, (ii) the unfolding
rank remains separated from zero, and (iii) event mass and peak prominence are
observable. That interval is not yet established.

## 5. Audit of the existing literature note

### What is already correct

The section “Targeted weak-reactivity collision check” correctly says that
Feynman--Kac, area/volume reactivity, and a small-reactivity Dyson expansion
are not new. It also correctly restricts the possible novelty to the
intersection of a conserved allocation, mixed jets, resource-tangent rank,
and singularity persistence, and labels absence as a search inference.

### Required repairs

1. **Add Nguyen--Grebenkov 2010 as P0.** Its omission materially understates
   the closest collision because it combines heterogeneous *bulk* killing,
   the full survival law, fixed total reactive strength, and small-\(h\)
   perturbation.
2. **Add Ryu 2009 and Ryu--Johnson 2009 at P1.** They establish perturbative
   response to nonuniform partial absorption and prevent a broad linear-
   response claim.
3. **Replace the Bressloff preprint-only citation with the published paper:**
   J. Phys. A 55, 205001 (2022), DOI
   [10.1088/1751-8121/ac5e75](https://doi.org/10.1088/1751-8121/ac5e75).
4. **Add Grebenkov 2007 and the 2020 multiple-local-time paper** when
   discussing exposure clocks and multiple reactive subsets.
5. Retain the sentence that absence is not proved. Do not upgrade it to
   “first” even after these additions.

## 6. Audit of the manuscript's new section

### Scientifically correct and safe

- The distinction between \(F_B=f_B/B\) and the unnormalized density is
  explicit.
- The theorem is restricted to \(0<\tau\le t\le T<\infty\), so it does not
  conflate the fixed-time and \(t=O(B^{-1})\) limits.
- The first Dyson correction and \(O(B^2)\) remainder are not oversold.
- The direct observable derivatives are present.
- The cusp determinant includes positivity, rank, fourth-derivative, and
  budget-unfolding conditions.
- The section explicitly says that standard semigroup ingredients are not
  new and lists the missing numerical/observability gates.

### Required citation placement before submission

1. In the introduction's paragraph beginning “Here the unreactive transport”,
   cite Nguyen--Grebenkov 2010 alongside Grebenkov 2019 and
   Nicolaou--Mulder 2023. State that fixed-total **bulk** reactive-strength
   arrangement and full survival laws already exist.
2. At Eq. “freeexposure”, cite Nguyen--Grebenkov 2010,
   Prüstel--Meier-Schellersheim 2014, and Bressloff 2022. Say explicitly that
   the weak-exposure leading term is standard; the new technical result is the
   uniform declared mixed-jet bound for this encounter operator.
3. Near the sensitivity PDEs, cite Ryu 2009/Ryu--Johnson 2009 as prior
   perturbative work on nonuniform partial absorption; do not imply their work
   contains the present transient jet.
4. Near the three-clock determinant, optionally cite Ray--Lindsay 2005 to
   acknowledge established mixture-modality geometry. Do not label the
   determinant identity a first or general new discriminant.

### Wording risk

The current sentence

> the contribution is their model-specific mixed-jet, budget, and
> singularity-persistence assembly

is defensible only as a **target contribution** while the physical cusp and
finite-\(B\) application remain open. Before those gates pass, the safer
working wording is:

> Here these standard ingredients provide a model-specific route from a
> quantitatively certified free-exposure cusp to a nearby weak-Doi cusp; the
> physical realization and observable finite-budget interval remain separate
> gates.

No edit was applied in this audit.

## 7. Mandatory claim firewall

### Prohibit

- “We introduce the free-exposure/weak-reaction limit.”
- “This is the first Feynman--Kac or occupation-time treatment of Doi/area
  reactivity.”
- “This is the first heterogeneous bulk-reactivity survival law.”
- “This is the first optimization or control under fixed total reactivity.”
- “We derive the first response theory for nonuniform partial absorption.”
- “The determinant gives a new general theory of mixture modality.”
- “We prove a new general fold/cusp persistence theorem.”
- “The weak-\(B\) theorem proves a cusp at \(B=0.6\), a global reaction-time
  density, or trimodality.”
- “To our knowledge” attached to any one of the above ingredients.

### Safe now

> For the declared encounter operator, we derive an explicit
> compact-positive-time \(O(B)\) estimate uniform in the finite time/control
> jet required by the cusp map. Combined with quantitative margins of a
> free-exposure design, this yields a conditional persistence criterion for a
> nearby weak-Doi fold or cusp.

### Safe only after the physical gates pass

> With transport, geometry, contact scale, and initial law fixed, we show that
> redistributing a static centre-space Doi reactivity under one physical
> integral budget creates and organizes reaction-time modality transitions in
> two-particle continuum encounter dynamics.

If a novelty qualifier is needed, attach it only to the entire combined
sentence and use “To our knowledge”; never attach it to Feynman--Kac, weak
killing, fixed reactivity, mixture modality, or cusp persistence separately.

## 8. Minimum citation set for the weak-theory section

The following primary papers are mandatory or strongly recommended:

1. B. T. Nguyen and D. S. Grebenkov, *J. Stat. Phys.* **141**, 532--554
   (2010), [DOI](https://doi.org/10.1007/s10955-010-0054-1): closest bulk,
   fixed-strength, full-survival predecessor.
2. T. Prüstel and M. Meier-Schellersheim, *J. Chem. Phys.* **141**, 194115
   (2014), [DOI](https://doi.org/10.1063/1.4901115): area-reactivity
   Feynman--Kac and reaction-rate/exposure identity.
3. P. C. Bressloff, *J. Phys. A* **55**, 205001 (2022),
   [DOI](https://doi.org/10.1088/1751-8121/ac5e75): interior partial
   absorption through occupation-time generalized propagators.
4. D. S. Grebenkov, *Phys. Rev. E* **76**, 041139 (2007),
   [DOI](https://doi.org/10.1103/PhysRevE.76.041139): reflected Brownian
   residence/occupation functionals.
5. S. Ryu, *Phys. Rev. E* **80**, 026109 (2009),
   [DOI](https://doi.org/10.1103/PhysRevE.80.026109), and S. Ryu and D. L.
   Johnson, *Phys. Rev. Lett.* **103**, 118701 (2009),
   [DOI](https://doi.org/10.1103/PhysRevLett.103.118701): perturbative
   nonuniform partial absorption.
6. D. S. Grebenkov, *J. Chem. Phys.* **151**, 104108 (2019),
   [DOI](https://doi.org/10.1063/1.5115030): heterogeneous Robin full
   reaction-time theory.
7. D. S. Grebenkov, *J. Stat. Mech.* 103205 (2020),
   [DOI](https://doi.org/10.1088/1742-5468/abb6e4): multiple local-time/
   reactive-subset parameters.
8. K. Nicolaou and B. M. Mulder, *Sci. Rep.* **13**, 22815 (2023),
   [DOI](https://doi.org/10.1038/s41598-023-49566-4): fixed-total surface
   reactivity optimization.

Ray--Lindsay 2005 is recommended for the mixture-topography sentence but is
not needed to justify the diffusion physics.

## 9. Added audit: direct OU small-noise/narrow-slab arbitrary-\(m\) route

### 9.1 What is actually new enough to test

The proof draft in **notes/direct_physical_multimode_theorem.md** considers a
special slab quotient. A monotone OU midpoint distribution of width
\(O(\varepsilon)\) sweeps through normalized static catalyst slabs of width
\(O(\varepsilon)\), centred at the deterministic positions
\(c_j=\mu(t_j)\). The exact free-exposure clocks are

\[
 g_{j,\varepsilon}(t)
 =c_{d,\varepsilon}(t)
 \frac{\exp[-(c_j-\mu(t))^2/(2\varepsilon^2S^2(t))]}
 {W^{d-1}\sqrt{2\pi}\,\varepsilon S(t)} .
\]

For each fixed finite \(m\), separated target times make the own-channel
derivatives polynomially large and cross-channel derivatives exponentially
small. The channel-dominance lemma then gives one nondegenerate maximum in
each prescribed \(O(\varepsilon)\) window. For fixed \(\varepsilon\), the
weak-budget mixed-jet theorem transfers these maxima to the full Doi density
for \(0<B<B_0(\varepsilon)\).

The potentially distinctive object is not “narrow spatial targets make
peaks.” It is the whole constrained statement:

> in a declared two-particle continuum Doi operator, normalized static
> catalyst slabs with one fixed centre-space integral realize at least any
> prescribed finite number of local reaction-time modes, and a quantitative
> weak-reactivity jet theorem transfers the separated free-exposure modes to
> positive \(B\).

No primary source located in this targeted search states that exact
combination. This is a search result, not a priority proof.

### 9.2 Primary-source collision map

| Primary source | Established result relevant to the direct route | Collision level | Remaining distinction |
|---|---|---:|---|
| Lindsay, Spoonmore & Tzou (2016), [DOI](https://doi.org/10.1103/PhysRevE.94.042418), [arXiv](https://arxiv.org/abs/1607.08095) | Full \(2d\) narrow-capture density for multiple small traps. Two strategically separated static absorbing sets give a bimodal density; their moving-trap illustration gives repeated modes on successive sweeps. | **P0 / high.** Spatial separation plus arrival-time gating as a multimodality mechanism is established. | Perfect traps rather than normalized finite Doi killing; no fixed-reactivity simplex, arbitrary-\(m\) theorem, two-body contact factor, or weak-\(B\) jet transfer. |
| Nguyen & Grebenkov (2010), [DOI](https://doi.org/10.1007/s10955-010-0054-1) | Full survival/reaction-time law for heterogeneous bulk killing, spatial arrangement at fixed total reactive strength, and small-reactivity perturbation. | **P0 / high.** Static finite-volume reactivity, fixed resource, and weak killing are established. | No transient mode topology or constructive arbitrary-\(m\) result. |
| Bressloff & Schumm (2022), [DOI](https://doi.org/10.1137/21M1449580) | Multiple small partially absorbing interior targets in \(d=2,3\), represented by killing inside targets and treated by narrow-target asymptotics. | **P1 / medium-high.** Narrow partial bulk targets in both physical dimensions are established. | Focus on fluxes/MFPT and resetting, not multimodal full-density design or a conserved amplitude simplex. |
| Le Vot, Yuste, Abad & Grebenkov (2022), [DOI](https://doi.org/10.1103/PhysRevE.105.044119), [arXiv](https://arxiv.org/abs/2201.05388) | First-encounter densities of two mobile particles in confined \(d=2,3\), including two-hump cases. | **P0 / high** against broad encounter-multimodality language. | No static heterogeneous catalyst allocation or arbitrary-\(m\) construction. |
| Ray & Lindsay (2005), [DOI](https://doi.org/10.1214/009053605000000417) | Modality and critical-point topology of Gaussian mixtures. Well-separated positive Gaussian components give the elementary route to multiple modes. | **P1 / medium-high.** The separated-Gaussian part is not new abstract mathematics. | No embedding into an OU exposure field, Doi reaction law, or physical resource normalization. |
| Ekström & Janson (2015), [arXiv](https://arxiv.org/abs/1508.07827) | A time-dependent Brownian boundary can be selected to realize a prescribed survival law. | **P1 / medium** against broad inverse-FPT claims. | Moving boundary and unrestricted target law, rather than static nonnegative reactivity under one integral budget. |
| Grebenkov & Ward (2026), [DOI](https://doi.org/10.1137/25M180562X), [arXiv](https://arxiv.org/abs/2509.26381) | Many partially reactive patches, Green matrices, local reactive capacitances, and homogenized effective reactivity. | **P1 / medium.** Current narrow-reactivity theory already handles many partial patches. | Effective capture/reactivity rather than transient density modes and weak-Doi persistence. |

The original OU transition kernel is Gaussian
([Uhlenbeck & Ornstein 1930](https://doi.org/10.1103/PhysRev.36.823)).
Thus the convolution formula and localization around
\(\mu(t_j)=c_j\) should be presented as an exact tractable mechanism, not as a
new small-noise principle.

### 9.3 Claim-by-claim verdict

| Candidate claim | Verdict |
|---|---|
| Static narrow spatial sets can make a continuum capture/reaction density multimodal | **FAIL as novelty; Lindsay 2016 is decisive** |
| A small-noise OU packet creates a Gaussian clock when it crosses a narrow slab | **FAIL as standalone novelty; exact OU/Gaussian localization** |
| Separated positive Gaussian-like clocks give one mode per channel | **FAIL as general mathematics; standard mixture/separation mechanism** |
| Fixed total bulk or surface reactivity is new | **FAIL; Nguyen--Grebenkov and Nicolaou--Mulder** |
| For each fixed finite \(m\), the declared OU slab Doi family has at least \(m\) local modes at some positive \(B\) | **SEARCH-DISTINCT combined theorem, conditional on proof audit** |
| The theorem proves exactly \(m\) modes globally | **FAIL; it proves designated local maxima and does not exclude extra critical points** |
| One fixed configuration supports arbitrary \(m\) | **FAIL; the geometry and required \(\varepsilon\) depend on \(m\) and the target times** |
| Reactivity redistribution alone creates a fold/cusp | **NOT SHOWN by this theorem; all interior weights already retain the separated modes** |
| A general \(d\)-dimensional spatial-configuration theorem | **OVERBROAD; this is a symmetry-reduced slab family for each fixed \(d\)** |
| Observable arbitrary-\(m\) positive-budget physics | **OPEN; \(B_0(\varepsilon)\), prominence, and event-mass overlap are unquantified** |

### 9.4 Scientific caveats that must remain in the theorem statement

1. **The construction is a family, not one configuration.** For each \(m\)
   and chosen \((t_1,\ldots,t_m)\), the patch centres are redesigned and
   \(\varepsilon\) must be reduced until all channels separate. The correct
   claim is existential for each fixed finite \(m\), not uniform in \(m\).
2. **The singular limits are sequential.** The catalyst supremum norm grows
   as \(O(\varepsilon^{-1})\), so the constants in the weak-budget theorem
   deteriorate and \(B_0(\varepsilon)\) may collapse rapidly. There is no
   current proof that an observable lower budget and the admissible upper
   budget overlap.
3. **The encounter factor is deliberately almost inert.** The deterministic
   relative path is held strictly inside the contact ball, making
   \(c_{d,\varepsilon}\to1\) near every designed peak. A skeptical referee can
   therefore interpret the result as one-body midpoint killing of an
   already-contacting pair. It is an exact encounter-model theorem, but not
   yet a demonstration that nontrivial approach/separation encounter dynamics
   creates the modes.
4. **The spatial result is slab-specific.** The catalyst varies along one
   longitudinal midpoint coordinate and is uniform across the transverse
   torus. The statement “for every fixed \(d\ge2\)” does not establish
   arbitrary localized configurations in physical \(d=2\) or \(d=3\) space.
5. **This is not the amplitude-control bifurcation result.** Once the slabs
   are sufficiently separated, every weight in a compact simplex-interior set
   retains all \(m\) modes. The theorem proves realizability under a conserved
   budget, not the creation/annihilation fold or cusp obtained by
   redistributing amplitudes on one frozen geometry.
6. **Only local mode count is certified.** “Exactly one maximum in each
   prescribed interval” plus intervening minima gives at least \(m\) modes;
   it does not exclude early, late, or interstitial extra extrema.

These caveats do not invalidate the theorem. They determine its correct role:
it closes the reduced-to-continuum **existence** gap while leaving the
finite-parameter, observable, allocation-controlled physics gap open.

### 9.5 Safe and unsafe wording

Safe:

> Within the specified OU slab quotient, for every prescribed finite \(m\) we
> construct an \(\varepsilon\)-dependent family of normalized static catalyst
> slabs. For sufficiently small fixed \(\varepsilon\), and then sufficiently
> small positive installed budget \(B\), the exact Doi reaction-time density
> has at least \(m\) nondegenerate local maxima on the prescribed compact time
> interval.

Also safe, with a literature qualifier:

> To our knowledge, prior narrow-capture work establishes spatially induced
> multimodality but not this resource-normalized arbitrary-finite-mode
> realization and weak-Doi transfer in a two-particle encounter operator.

Unsafe:

- “We first show that spatial configuration creates multimodal continuum
  first-passage times.”
- “Narrow catalysts provide a new general mechanism for multimodality.”
- “We prove arbitrary-dimensional arbitrary-mode encounter physics.”
- “A fixed catalyst configuration can realize arbitrarily many modes.”
- “The theorem proves observable modes at finite physical reactivity.”
- “The theorem establishes the conserved-reactivity fold/cusp.”

### 9.6 PRR value and required promotion path

If its proof survives technical audit, the direct theorem is stronger than
the reduced GIG theorem and should replace any claim that a physical
realization bridge is wholly missing. It is still a supporting theorem rather
than the PRR physics headline. To promote it:

1. derive a quantitative scaling bound for \(B_0(\varepsilon,m)\) and exhibit
   a nonempty window satisfying declared peak prominence and event-mass
   floors;
2. give a finite, nonsingular \(d=2\) realization and an independently solved
   \(d=3\) realization, without retuning the qualitative claim;
3. show robustness when the relative coordinate has a genuinely varying
   contact probability, rather than remaining uniformly inside contact;
4. demonstrate a fold/cusp or mode-count change caused solely by redistributing
   weights on one frozen patch geometry; and
5. state clearly that Lindsay 2016 owns the phenomenon-level precedent and
   that the contribution is the constrained Doi realization plus transfer.

**Direct-route conclusion:** **no fatal exact-theorem collision was located,
but the mechanism has high prior-art overlap.** The correct novelty unit is
the resource-normalized OU-slab embedding together with positive-\(B\)
mixed-jet persistence. That unit is provisionally publishable, subject to
proof audit; by itself it does not clear the PRR gate.

## 10. Search boundary and residual risk

The targeted search combined terms for area/volume reactivity,
Feynman--Kac/occupation time, heterogeneous reactivity, fixed total reactive
strength, small-reactivity perturbation, first-passage linear response,
mixture modality, fold/cusp discriminants, narrow capture, multiple static and
moving traps, small-noise OU localization, arbitrary mode counts, and inverse
first-passage construction. It followed primary records and full texts through
DOI publisher pages, APS/JCP/JSTAT/J. Phys. A/SIAM records, author-hosted PDFs,
and arXiv versions. Reviews were used only to route to primary papers and are
not evidence in this audit.

Residual risk remains nontrivial because terminology is fragmented across
diffusion-reaction theory, NMR relaxation, porous-media survival, stochastic
processes, and mixture topology. The conclusion is therefore not “no prior
paper exists.” It is:

> no direct prior realization of the full combined chain was located in this
> targeted primary-source audit, while nearly every mathematical ingredient
> considered separately has a close predecessor.

The collision screen should be rerun immediately before submission, and a
domain expert should specifically review the Nguyen--Grebenkov/Ryu lineage.

## 11. Final gate

| Gate | Status after this audit |
|---|---|
| Feynman--Kac/occupation-time novelty | **FAIL as a claim; established** |
| Weak-exposure leading term novelty | **FAIL as a claim; standard consequence** |
| Fixed total bulk/surface reactivity novelty | **FAIL as a claim; established** |
| Precise compact-time mixed-jet \(O(B)\) estimate | **SEARCH-DISTINCT, but standard-method theorem** |
| Factorized encounter cusp recipe | **POTENTIALLY DISTINCT only model-specifically** |
| Quantitative weak-Doi cusp/rank transfer | **POTENTIALLY DISTINCT only with realized margins** |
| Narrow spatial configuration creates multimodality | **FAIL as a novelty claim; Lindsay 2016** |
| Direct OU arbitrary-fixed-\(m\) Doi realization | **SEARCH-DISTINCT combined theorem; proof audit required** |
| General \(d\)-dimensional or one-configuration arbitrary-\(m\) claim | **FAIL / OVERBROAD** |
| Direct-theorem finite-\(B\) observability | **OPEN** |
| Observable finite-\(B\) interval | **OPEN** |
| Physical-\(d=2\) cusp/fold manifold | **OPEN** |
| Independent physical-\(d=3\) validation | **OPEN** |
| PRR-level combined claim | **HOLD** |

**Adversarial conclusion:** the weak-budget theorem materially improves the
project because it replaces an uncontrolled heuristic bridge by an explicit
jet-level one. The direct OU theorem, if its proof survives, additionally
closes an exact but singular reduced-to-continuum arbitrary-finite-mode
existence gap. Neither result by itself supplies the finite-parameter,
allocation-controlled physics needed for PRR. The paper's strongest
defensible route is to use both as analytical support behind a certified and
observable conserved-reactivity modality transition in physical two- and
three-dimensional encounter dynamics.
