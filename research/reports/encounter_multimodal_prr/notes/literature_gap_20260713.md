# Primary-literature gap audit for conserved-reactivity encounter-time modality

Date: 2026-07-13  
Scope: literature and novelty audit for the proposed `encounter_multimodal_prr`
project, with the publication route updated after the terminal allocation-v6
scientific HOLD.  This note assesses claims; it does not certify that the
proposed continuum theorems or numerical gates have already been completed.

**2026-07-14 theorem-first correction.**  The presently proved construction is
a conserved-budget **support-design existence theorem**: the prescribed mode
count comes from an `m`-dependent set of slab locations, while all interior
weights on that support retain the same count.  It is not yet evidence that
weight redistribution on one fixed support switches among one, two, and three
modes.  The latter remains contingent on the unrun finite-parameter campaign.
Moreover, the univariate fact that an `m`-component Gaussian mixture has at
most `m` modes is classical; see Carreira-Perpi\~n\'an and Williams (2003), DOI
`10.1007/3-540-44935-3_44`, and the review by Am\'endola, Engstr\"om, and Haase
(2020), DOI `10.1093/imaiai/iaz013`.  The defensible analytical novelty is the
margin-bearing embedding in an exact Doi quotient, including the whole-window
slow-factor certificate and fixed-`epsilon` positive-budget transfer, not the
Gaussian-mixture upper bound itself.

## 1. Executive verdict

The broad phenomenon is **not new**.  The literature already contains:

- exact or asymptotic first-passage densities with two or more peaks in
  discrete Markov systems, disordered intervals, sparse networks, and
  strategically arranged two-dimensional traps;
- continuum first-encounter calculations for two mobile particles in physical
  dimensions two and three, including two-hump densities in some three-
  dimensional configurations;
- general reaction-time theory for spatially heterogeneous Robin reactivity;
- optimization of a spatial reactivity distribution under a fixed integral
  resource constraint, albeit for steady-state flux rather than timing
  modality;
- small-target Green-function/capacitance asymptotics, Doi--Robin calibration,
  and boundary-local-time formulations of imperfect reaction; and
- inverse first-passage constructions in which a time-dependent boundary is
  selected to realize a prescribed law.

Consequently, the paper must not be presented as the first demonstration of
multimodal first-passage or encounter times, the first use of spatial
heterogeneity, the first fixed-resource reactivity optimization, or the first
inverse first-passage control problem.

The defensible PRR-level opportunity is the following **combined
intersection**, which I did not find established in the primary works scanned:

> With transport, geometry, contact scale, and initial law held fixed, vary
> only a nonnegative time-independent spatial reactivity field under a
> resolution-independent physical integral budget; prove that prescribed fixed
> finite mode counts can be embedded in an exact Doi encounter process under
> explicit sequential limits; and realize distinct one-, two-, and three-mode
> finite-window reaction-time laws in one physical two-dimensional family at
> the same nonzero budget, with all-configuration and independent event-law
> validation.

Budget-projected response jets and local fold/cusp criteria remain useful
analytical tools, but a numerical cusp is no longer a conjunct of this paper.
Positive-budget physical `d=3` is likewise not a submission gate: the theorem
may state fixed-finite-dimensional scope, while the finite-parameter headline
remains physical `d=2` unless a separate `d=3` chain is later completed.

This is a **search-based inference, not a proof of absence**.  It is strong
enough to guide the project, but any eventual “to our knowledge” sentence
should remain qualified and should be checked again immediately before
submission.

At the current theorem-only stage the central message should therefore be
**prescribed finite-window modality by conserved-budget support design**, not
“redistribution controls mode count.”  The stronger conserved-reactivity
allocation-control message becomes available only if the frozen physical-2D
campaign and independent event-law comparison pass.

## 2. Nearest-neighbour collision map

| Priority | Primary work | What is already established | Collision with the proposed paper | Remaining distinction that must be demonstrated |
|---|---|---|---|---|
| P0 | Lindsay, Spoonmore & Tzou, PRE 94, 042418 (2016), [DOI](https://doi.org/10.1103/PhysRevE.94.042418), [arXiv](https://arxiv.org/abs/1607.08095) | Full capture-time density for multiple small absorbing traps in a bounded reflecting 2D domain; Green-function/matched-asymptotic construction, numerical inversion, PDE and particle validation; strategically arranged traps yield multimodal densities. | Rules out “first continuum 2D spatial configuration producing multimodal FPT” and “first asymptotic/numerical treatment of multimodal narrow capture.” | Perfect fixed traps and geometry placement are varied.  The proposed paper must instead keep geometry and transport fixed, redistribute only partial reactivity under a physical integral budget, and establish its modality bifurcation geometry. |
| P0 | Le Vot, Yuste, Abad & Grebenkov, PRE 105, 044119 (2022), [DOI](https://doi.org/10.1103/PhysRevE.105.044119), [arXiv](https://arxiv.org/abs/2201.05388) | Broad-time Monte Carlo study of first-encounter densities for two mobile diffusers in bounded 2D and 3D domains.  The paper's reported 3D cases include two-hump shapes for suitable initial geometry and separated time scales. | Rules out “first 2D/3D two-particle encounter density” and “first bimodal continuum encounter time.” | Their encounter law is spatially homogeneous/perfect rather than a conserved heterogeneous catalyst field; there is no fixed-resource inverse design or fold/cusp continuation. |
| P0 | Giuggioli et al., *Target Search Problems* (2024), [DOI](https://doi.org/10.1007/978-3-031-67802-8_5), [arXiv](https://arxiv.org/abs/2311.00464) | Exact lattice-random-walk formalism in bounded/heterogeneous environments and explicit multiple first-passage peaks for biased walkers in a periodic hexagon; also radiation-boundary and multi-target constructions. | Rules out “first Markov/lattice FPT multimodality,” “first exact multimodal search,” and any attribution of the basic multipeak phenomenon to the new project. | Luca's multipeak example is produced by biased periodic transport.  The proposed control freezes transport and changes only static reactivity amplitudes under a conserved physical budget, then requires a continuum encounter realization. |
| P0 | Marris, Hens, Ghosh & Giuggioli (2025), [arXiv:2508.10140](https://arxiv.org/abs/2508.10140) | Exact first-passage dynamics on sparse graphs and a bimodality regime for a target node in a small-world network, with network features linked to the regime. | Rules out “first exact bimodal FPT in a disordered Markov network.” | Network/transport disorder creates the effect; no fixed catalyst budget, continuum two-body encounter field, or modality discriminant is developed. |
| P0 | Grebenkov, JCP 151, 104108 (2019), [DOI](https://doi.org/10.1063/1.5115030), [arXiv](https://arxiv.org/abs/1908.01143) | General spectral theory for continuously varying or piecewise-constant heterogeneous Robin reactivity, including propagator, survival probability, reaction-time distribution, and rate through a Dirichlet-to-Neumann representation. | Rules out “first heterogeneous-reactivity reaction-time theory,” “first spectral representation,” and “first patchwise partial-reactivity treatment.” | It does not solve fixed-integral inverse modality design, budget-projected response-jet controllability, or continuum fold/cusp loci for two-particle encounter. |
| P0 | Nicolaou & Mulder, *Scientific Reports* 13, 22815 (2023), [DOI](https://doi.org/10.1038/s41598-023-49566-4) | Optimizes a position-dependent Robin reactivity under a fixed mean/total surface-reactivity constraint, using a reusable particle-derived Markov representation; objective is steady-state total flux. | Rules out “first optimization of spatial reactivity under a fixed total resource” and “first catalyst redistribution problem.” | The proposed objective is the full transient reaction-time density and its modes, not steady flux; the resource lives in physical centre space for a two-body Doi encounter model, not on a fixed absorbing surface. |
| P0 | Isaacson, Mauro & Newby, PRE 94, 042414 (2016), [DOI](https://doi.org/10.1103/PhysRevE.94.042414), [arXiv](https://arxiv.org/abs/1605.01279) | Uniform-in-time small-reaction-radius expansions for Doi volume reactivity and Smoluchowski--Collins--Kimball partial absorption; calibrated models agree through a diffusion-limited-rate parameter. | Rules out presenting Doi--Robin calibration or a small-target bridge as new by itself. | The needed new bridge is uniform in the **joint control/time derivative jets** that preserve modes and fold/cusp nondegeneracy under a heterogeneous fixed budget.  Agreement of state solutions alone does not automatically give this. |
| P1 | Holehouse & Redner, PRE 109, L032102 (2024), [DOI](https://doi.org/10.1103/PhysRevE.109.L032102), [arXiv](https://arxiv.org/abs/2307.08879) | Exact first-passage distribution for disordered nearest-neighbour hopping on an interval and bimodality for some rate realizations. | Further rules out novelty based only on an exact finite-state bimodal law. | Disorder is in hopping rates; no conserved spatial killing/reactivity allocation or continuum encounter transfer. |
| P1 | Keidar & Reuveni, PRR 8, 023135 (2026), [DOI](https://doi.org/10.1103/c7wy-ddrc), [arXiv](https://arxiv.org/abs/2410.16129) | A universal linear-response formula for the **mean** first-passage time under rare perturbations, expressed through unperturbed moments and a post-activation mean completion time. | Rules out broad language claiming a first general response theory for first-passage kinetics. | The proposed response object is the full transient density and its time/control derivative jets under a static conserved spatial reactivity redistribution; it is not a universal MFPT response to stochastic perturbation activation. |
| P1 | Grebenkov, PRL 125, 078102 (2020), [DOI](https://doi.org/10.1103/PhysRevLett.125.078102), [arXiv](https://arxiv.org/abs/2007.11224) | Boundary-local-time/encounter-based formulation that separates transport geometry from surface reaction mechanisms and yields propagators, survival, FPT distributions, and reaction rates. | Rules out “first encounter/local-time reaction framework” and broad claims of first geometry--reactivity separation. | The proposed paper uses this ancestry but adds a declared conserved spatial control, modality jets, bifurcation discriminants, and constructive designs. |
| P1 | Grebenkov & Ward, *Multiscale Modeling & Simulation* (2026), [DOI](https://doi.org/10.1137/25M180562X), [arXiv](https://arxiv.org/abs/2509.26381) | Matched asymptotics for many partially reactive patches on a sphere; target capacitance expressed through a Green matrix and local reactive capacitances, plus effective-reactivity homogenization. | Makes a vague “new capacity/Green-matrix theory for patchy reactivity” claim unsafe. | Their main object is effective capture/reactivity, not the transient density's control jets or modality bifurcations under a conserved allocation. |
| P1 | Grebenkov & Ward, *European Journal of Applied Mathematics* (2026), [DOI](https://doi.org/10.1017/S0956792525100284), [arXiv](https://arxiv.org/abs/2509.26367) | Current planar small-target theory spanning Dirichlet, Robin, and Steklov conditions, with the characteristic 2D small-target structure. | Raises the standard for the proposed 2D asymptotic bridge and prevents generic claims about first Robin/capacity treatment of planar targets. | The proposed bridge must target transient density derivatives, control sensitivity, and persistence of modality singularities, not only effective rates, eigenvalues, or splitting data. |
| P1 | Ekström & Janson (2015), [arXiv:1508.07827](https://arxiv.org/abs/1508.07827) | Classical inverse first-passage problem: select a time-dependent Brownian boundary to realize a prescribed survival distribution, linked to optimal stopping. | Rules out “first inverse first-passage design/control.” | The proposed inverse problem is much more constrained: a static nonnegative spatial reactivity field, a fixed physical integral, fixed transport, and control of qualitative modality rather than an arbitrary moving boundary. |

## 3. What the literature establishes, by theme

### 3.1 Multimodal first-passage and reaction-time densities

Multimodality has several already-established mechanisms:

1. **Geometrically separated fast channels in a continuum.**  Lindsay et al.
   construct the full 2D narrow-capture density and explicitly recover peaks
   associated with rapid capture by strategically arranged absorbing traps,
   with longer-time content obtained by numerical Laplace inversion.
2. **Confinement and initial geometry in a two-particle continuum.**  Le Vot
   et al. resolve two-mobile-particle encounter-time densities over several
   decades in 2D and 3D; two-hump examples occur without heterogeneous
   catalyst allocation.
3. **Transport bias or disorder in discrete Markov dynamics.**  Giuggioli et
   al. obtain multiple peaks for biased motion in a periodic hexagon;
   Holehouse and Redner obtain bimodality on disordered intervals; Marris et
   al. obtain an exact bimodality regime in small-world networks.
4. **Multiple kinetic pathways in networks/energy landscapes.**  Woods and
   Wales analyze full first-passage distributions with competing pathways and
   rare events in kinetic transition networks ([DOI](https://doi.org/10.1039/D3CP04199A)).

The correct literature-facing statement is therefore not that spatial
structure can make a density multimodal.  At the current theorem stage it is
that conserved-reactivity **support design** can prescribe finite-window mode
topology in an exact Doi family under explicit sequential limits.  A stronger
claim that allocation alone switches the mode count on one fixed support is
available only if the prospective finite-parameter one-/two-/three-mode chain
passes; a modality phase diagram would require the separate fold/cusp branch.

### 3.2 Heterogeneous reactivity and fixed-resource design

Grebenkov's 2019 JCP paper is the principal analytical predecessor: arbitrary
space-dependent Robin reactivity is represented in the eigenbasis of the
Dirichlet-to-Neumann operator, and reaction-time distributions are among the
derived observables.  This must be cited early, not buried as a numerical
detail.

Nicolaou and Mulder are the decisive resource-constrained predecessor.  They
hold an integral/mean surface reactivity fixed and optimize its distribution
to maximize steady-state flux.  Thus the phrase “fixed-reactivity-budget
optimization” is not novel.  The proposed manuscript must explain explicitly
that it changes all three ingredients:

- **dynamical objective:** density modes and their bifurcations rather than
  steady-state flux;
- **physical system:** two mobile particles reacting on encounter rather than
  one diffuser absorbed on a fixed body; and
- **resource measure:** an integrated centre-space Doi reactivity field rather
  than boundary Robin reactivity.

These are meaningful distinctions only if the numerical implementation
converges to the declared continuum integral.  A fixed number or unweighted
sum of reactive grid states would not sustain the claim.

Keidar and Reuveni provide a second response-theory boundary that is especially
relevant to a PRR submission.  Their universal object is the linear response of
the **MFPT** to a rare perturbation protocol.  The present paper must not market
its Duhamel calculation as the first general first-passage response theory.
Its narrower but different target is a spatial-budget tangent response of the
**full reaction-time density**, including enough time derivatives to certify
mode topology.  That distinction should be stated in the Introduction and
made mathematically visible through the projected density jet, rather than left
as a verbal novelty claim.

### 3.3 Doi, Robin, boundary local time, and small targets

The Doi volume model, Robin/Collins--Kimball boundary model, and encounter/local-
time description are established model classes.  Isaacson et al. show a
uniform-in-time calibrated small-target equivalence between Doi and partial-
absorption descriptions in their setting.  Grebenkov develops the local-time
framework.  Current Grebenkov--Ward work supplies sophisticated patch-
capacity/Green-matrix asymptotics in 2D and 3D settings.

Accordingly, the continuum bridge must be more specific than “we recover a
Robin model from Doi” or “small targets are described by capacities.”  It has
to control the quantities that determine modality.  A useful target is a
uniform estimate, for controls in a compact interior subset of the resource
simplex and times in a fixed positive window,

\[
 \max_{0\le r\le r_*}\max_{0\le |\alpha|\le q_*}
 \left|\partial_t^r\partial_u^\alpha
 \bigl(f_a(t;u)-f_{\rm red}(t;u)\bigr)\right|
 \le \varepsilon_a,
 \qquad \varepsilon_a\to0,
\]

with dimension-correct rates and with enough derivatives to preserve the
simple critical points, a fold (`f_t=f_{tt}=0`, `f_{ttt}\ne0`), and a cusp when
claimed.  State convergence or mean-time convergence is insufficient.

For physical 2D, logarithmic/capacity scaling must be treated explicitly;
for physical 3D, the algebraic small-target scaling and capacitance structure
must be treated explicitly.  Reusing one dimension's extrapolation ansatz in
the other is a likely referee failure.

#### Targeted weak-reactivity collision check

A second targeted search was run after deriving the weak-budget
free-exposure bridge.  It confirms that neither the area/volume-reactivity
Feynman--Kac representation nor a small-reactivity Dyson expansion is new.
Prüstel and Meier-Schellersheim develop the area-reactivity model through a
generalized Feynman--Kac equation and relate survival, reaction rate, and
time-dependent rate coefficients
([J. Chem. Phys. 141, 194115 (2014)](https://doi.org/10.1063/1.4901115),
[arXiv:1405.3021](https://arxiv.org/abs/1405.3021)).  Bressloff likewise treats
interior partial absorption through occupation-time Brownian functionals and
Feynman--Kac
([arXiv:2201.01671](https://arxiv.org/abs/2201.01671)).  These works make any
claim of a first occupation-time, volume-reactivity, or Feynman--Kac treatment
unsafe.

The additional intersection searched was narrower: a conserved spatial
reactivity allocation, compact-positive-time convergence of the full
reaction-time **mixed time/control jet**, an explicit budget-tangent rank
margin, and quantitative persistence of a density fold or cusp.  The targeted
primary-source search did not locate that complete chain.  This remains a
search inference, not a proof of absence.  For the focused theorem-first route,
the defensible analytical contribution is instead the model-specific exact-
topology Doi embedding with explicit margins and sequential limits.  A
cusp/rank certificate belongs only to a later, separately completed promotion
branch.  The bounded-perturbation, Dyson, Cauchy, and Feynman--Kac ingredients
must be presented as standard tools rather than individual novelty claims.

### 3.4 Inverse FPT and fold/cusp language

Inverse first-passage is an existing mathematical field.  The Ekström--Janson
construction is already enough to make an unrestricted “inverse FPT is new”
claim false.  The new constraint is the scientifically interesting part:
static spatial reactivity, nonnegativity, a fixed integral resource, and fixed
transport.

The remainder of this subsection maps an optional stronger bifurcation branch,
not a submission conjunct of the focused theorem-first paper.  Targeted
searches for combinations of `first-passage`, `reaction-time
density`, `fold`, `cusp`, `catastrophe`, `mode bifurcation`, `reactivity`, and
`encounter` did **not** locate a primary work that continues fold/cusp loci of
the zeros of the time derivative of a reaction-time density under conserved
static spatial reactivity.  This is again a search inference rather than a
proof of nonexistence.

Generic fold and cusp normal forms are not themselves novel.  The publishable
content would be:

- the model-specific, budget-constrained jet conditions;
- a full-rank and well-conditioned physical unfolding;
- numerical continuation with isolated roots and nondegeneracy margins;
- persistence under continuum refinement and an independent solver; and
- a mechanistic interpretation in terms of competing encounter channels.

## 4. Relationship to Luca Giuggioli's work

The relationship should be framed as **direct ancestry plus a sharply
different control question**, not as competition over who first observed
multipeak FPTs.

### 4.1 What Luca's corpus already contributes

- Giuggioli, Pérez-Becker and Sanders developed an analytical encounter-time
  treatment for two walkers in overlapping one-dimensional territorial
  domains, with epidemic transmission as an application (PRL 110, 058103,
  [DOI](https://doi.org/10.1103/PhysRevLett.110.058103),
  [arXiv](https://arxiv.org/abs/1207.2427)).
- Giuggioli developed exact confined lattice-random-walk propagators and
  first-passage tools in arbitrary dimensions, including multiple and
  imperfect targets (PRX 10, 021045,
  [DOI](https://doi.org/10.1103/PhysRevX.10.021045)).
- Giuggioli et al. then exhibited multiple first-passage peaks for biased
  walkers in a periodic hexagon and treated radiation-boundary interactions.
- Marris et al. most recently identified an exact bimodality regime in sparse
  small-world networks and connected it to graph structure.

These works make Luca's program one of the nearest intellectual neighbours to
the discrete/finite-state side of this project.

### 4.2 The clean non-overlap

Luca's demonstrated multipeak mechanisms alter or exploit **transport
structure**: bias, periodic geometry, territorial overlap, graph disorder, or
network topology.  The proposed PRR project asks whether, with that entire
transport problem frozen, the **reaction operator alone** can be redistributed
under a conserved installed resource to create, annihilate, and robustly place
modes in a continuum two-body encounter law.

The strongest sentence is therefore:

> Exact lattice and network studies, including Giuggioli and co-workers, have
> shown that transport bias and disorder can produce multimodal first-passage
> laws.  We instead hold transport and geometry fixed and treat a conserved
> static reactivity field as the sole control, deriving and validating the
> resulting modality bifurcation geometry in continuum encounter dynamics.

### 4.3 Claims that Luca's work forbids

Do not claim:

- first multimodal Markov or lattice first-passage law;
- first exact connection between spatial structure and bimodality;
- first arbitrary-dimensional lattice search formalism;
- first multi-target or radiation-boundary lattice treatment; or
- first encounter-time application to two walkers.

If Luca is a collaborator or close source of the current preceding encounter
paper, the manuscript also needs a transparent related-work statement and a
precise map of reused versus new identities, code, and figures.

## 5. Novelty status of the proposed theorem chain

### Chain A: fixed-budget multi-rate projected-jet controllability

**Status: YELLOW as a standalone headline; GREEN as enabling theory if made
model-specific.**

The Duhamel/Frechet derivative and projection onto a linear budget tangent
space are standard semigroup and constrained-linear-algebra operations.  They
are not sufficient novelty alone.  What can be new is a theorem showing, for
the actual continuum encounter operator and physical patch family, that the
projected multi-time/multi-derivative response matrix has the needed rank and
a quantitative lower singular-value bound over a nontrivial parameter region.

Required deliverables:

1. include the direct derivative of the reaction observable as well as the
   generator response;
2. use the continuum physical cost covector, not grid counting;
3. prove differentiability uniformly away from `t=0` in all derivatives used
   by the finite-window topology certificate;
4. state a rank/singular-value criterion on the budget tangent space; and
5. verify every response quantity promoted in the physical `d=2` realization,
   with conditioning and validated residual evidence.

### Chain B: constructive arbitrary finite `m` modes

**Status: GREEN in the independently accepted fixed-finite, compact-window,
sequential scope of Rounds 118 and 120.**

Finite mixtures and finite phase-type/Markov families are flexible enough
that producing arbitrarily many separated peaks in a reduced family is not a
strong physics result by itself.  The theorem becomes valuable if it gives:

- explicit channel separation and amplitude inequalities;
- lower bounds on peak prominence and upper bounds on intervening valleys;
- perturbation radii that preserve all alternating simple critical points;
- a resource-normalized construction; and
- a model-to-continuum remainder small enough in the derivative jet to retain
  those inequalities.

The abstract may say exactly `m` modes in continuum Doi encounter dynamics only
after the global zero count, posterior-sector complement exclusion, slow-factor
root shifts, and fixed-`epsilon` weak-budget transfer are independently
accepted.  Those conditions are now closed by Rounds 118 and 120.  The
sequential quantifiers and absence of useful uniform-in-`m`,
uniform-in-dimension, event-mass, or finite-parameter lower bounds must remain
visible.

### Chain C: physical-2D fixed-control realization and persistence

**Status: GREEN and potentially PRR-level if all gates pass.**

This is the strongest component because the combination of conserved static
reactivity, two-body encounter, prescribed finite-window modality under one
installed budget, and independent validation appears absent from the closest
primary literature.  It needs more than one attractive density plot:

1. exact-rational same-budget controls fixed before their own positive-budget
   evaluations;
2. complete finite-window one-, two-, and three-mode root signatures with
   alternating derivative signs and nonzero event-basin masses;
3. odd/even, alignment, and box-family convergence for all three controls;
4. uncertainty envelopes that cannot change a root count or typed curvature;
5. a physically distinct off-lattice killed-process validation using the same
   windows and basin cuts;
6. no refitting after any positive-budget value is read; and
7. an honest physical-`d=2` claim, with `d=3` confined to theorem or
   supplemental leading-order context unless separately validated.

## 6. Recommended novelty language

### 6.1 Current safe central claim

> We formulate reaction-time modality as a constrained control problem for two
> diffusing particles.  Under a conserved centre-space reactivity integral, a
> constructive exact-Doi quotient embeds any prescribed fixed finite number of
> modes on a declared compact time window, using an `m`-dependent support
> design and explicit sequential limits.  The result is nonuniform, uses
> asymptotically saturated contact on that window, and supplies neither a
> useful finite budget nor an event-mass floor.  Whether fixed allocations on
> one physical two-dimensional support realize distinct one-, two-, and
> three-mode laws at a common positive budget remains an unrun numerical test.

Use “to our knowledge” only for the **entire combined statement**, not for any
individual ingredient.

### 6.2 Contingent PRR headline after numerical acceptance

> Conserved-reactivity control creates and organizes modality transitions in
> two-dimensional encounter times.

This wording is prohibited until the same-support one-/two-/three-mode and
off-lattice gates pass.  The working theorem-first title should instead use
“conserved-budget support design” and “finite-window.”

### 6.3 Claims to prohibit

- “We discover multimodal first-passage/encounter times.”
- “This is the first 2D spatial configuration with multiple FPT peaks.”
- “This is the first bimodal continuum encounter density.”
- “We introduce heterogeneous partial reactivity.”
- “We are the first to optimize a fixed total reactivity.”
- “We introduce inverse first-passage control.”
- “Doi--Robin equivalence/capacity asymptotics are new.”
- “A generic fold/cusp normal form is the main novelty.”
- “An arbitrary-mode reduced mixture proves arbitrary continuum encounter
  modes.”

## 7. Theory and evidence required for a defensible PRR submission

### 7.1 Exact continuum model and physical resource

Declare the two-particle no-flux generator and the killed/Doi reaction
operator.  Define

\[
 \kappa_w(c)=B\sum_j w_j\phi_j(c),\qquad
 w_j\ge0,\quad \sum_jw_j=1,\quad \int\phi_j(c)\,dc=1,
\]

so that `integral kappa_w dc = B` at every resolution.  Patch shapes,
locations, transport, contact profile/radius, and initial distribution remain
fixed during a control scan.  Derive the quadrature weights from this physical
integral; do not substitute a configuration-space volume or number of active
nodes without proving equivalence.

### 7.2 Budget-projected reaction-density jets

Derive the full control response of

\[
 f(t;u)=\langle 1,M_{K_u}e^{t(A_0-M_{K_u})}q_0\rangle,
\]

including both the direct observable derivative and the Duhamel term.  Extend
it to the time derivatives required by modality classification.  On the
budget tangent space `c^T h=0`, define the projected jet Jacobian and prove the
rank criterion for prescribed local changes in `f_t`, `f_tt`, and any other
selected jets.  Report the smallest singular value in physical units and
under an explicitly declared control norm.

### 7.3 Fold and cusp discriminants

For a one-control fold, solve and validate

\[
 f_t(t_*;u_*)=0,\qquad f_{tt}(t_*;u_*)=0,
\]

with `f_ttt != 0` and a nonzero budget-tangent unfolding derivative.  For a
cusp, state the exact degeneracy and show that two independent budget-tangent
controls give a full-rank unfolding.  A plotted merger of extrema is not a
certificate.  Store root brackets, residuals, derivative values,
singular-value ratios, and continuation direction.

### 7.4 Model-to-continuum transfer

Prove or tightly bound a remainder in a derivative norm strong enough to
transfer modes and singularities.  The required lemma should state explicitly
that if the reduced density has peak/valley and nondegeneracy margins larger
than the jet error, then the continuum density has the same alternating
critical-point pattern.  This is the missing link that turns a flexible
reduced mixture into an encounter theorem.

### 7.5 Separate 2D and 3D asymptotics

- **2D:** retain the logarithmic small-target/capacity parameter and show how
  patch interactions enter the Green matrix and jet error.
- **3D:** retain algebraic target-size/capacitance scaling and derive the
  corresponding response matrices.
- Explain which centre--relative-coordinate reduction is exact for the chosen
  geometry.  A slab or quotient construction must not be advertised as an
  arbitrary 2D/3D catalyst landscape.

### 7.6 Constructive multi-mode theorem

State explicit sufficient inequalities for channel dominance on disjoint time
windows, not just an existence assertion.  Include observability thresholds,
valley depth, and a perturbation radius.  Then show either:

1. a uniform continuum realization for arbitrary fixed finite `m`; or
2. an honest split claim: arbitrary `m` for the reduced family, plus resolved
   finite examples in the continuum.

The second option is scientifically acceptable but is a weaker abstract.

### 7.7 Numerical falsification gates

At minimum:

- deterministic action/semigroup solver with mass-balance and residual checks;
- root isolation on a predeclared time window, including tails and boundary
  modes;
- refinement families that can expose parity and boundary-clipping effects;
- independent PDE discretization or off-lattice Doi/Robin simulation with no
  parameter re-fitting;
- continuation of fold/cusp coordinates rather than isolated hand-picked
  parameter points;
- uncertainty/conditioning for high time derivatives; and
- negative controls: homogeneous allocation, permuted patch labels, changed
  mesh origin, and a nearby parameter on each side of every bifurcation.

## 8. Likely referee attacks

### P0: submission-blocking unless resolved

1. **“Multimodality is already known.”**  Cite Lindsay 2016, Le Vot 2022,
   Holehouse--Redner 2024, Giuggioli et al. 2024, and Marris et al. 2025, then
   make conserved-reactivity control the contribution.
2. **“Fixed-resource reactivity optimization is already known.”**  Cite
   Nicolaou--Mulder and distinguish transient modality, two-body encounter,
   and centre-space Doi cost.
3. **“Heterogeneous reaction-time theory is already known.”**  Cite
   Grebenkov 2019 and explain the inverse-design/bifurcation addition.
4. **“The reduced mixture is doing all the work.”**  Supply a continuum
   derivative-jet transfer theorem or sharply limit the claim.
5. **“A finite-grid fold is not a continuum fold.”**  Pass convergence,
   nondegeneracy, and independent-method gates.
6. **“The 3D result is not the first bimodal encounter density.”**  Cite Le
   Vot et al.; claim control and organization, not existence.
7. **“This duplicates the preceding encounter manuscript.”**  Give a
   theorem/figure/code overlap table and disclose the companion paper.  The
   preceding Green/Woodbury identity, scalar Duhamel response, finite fold,
   sign-variation condition, and reduced GIG screening cannot be re-sold as
   new.

### P1: major-revision risks

1. Doi--Robin state calibration is used as though it automatically controls
   mixed time/control derivatives.
2. A grid sum is called a conserved physical catalyst budget.
3. The 2D logarithmic and 3D algebraic asymptotics are conflated.
4. The cusp has poor unfolding conditioning or sits on the simplex boundary.
5. “Trimodal” is declared without five alternating simple critical points and
   prominence/valley margins.
6. Initial-condition tuning, rather than reactivity allocation, creates the
   extra peak.
7. Only one discretization or one matrix-exponential implementation is used.
8. Arbitrary `m` relies on vanishingly small peaks that fail any physical
   observability threshold.
9. The quotient/slab geometry is described as general 2D spatial placement.
10. The control uses patch motion or width changes while the theorem assumes
    fixed supports and amplitude-only variation.
11. The projected density-jet calculation is advertised as a first general
    first-passage response theory, despite the 2026 universal MFPT response
    framework of Keidar and Reuveni.

### P2: framing and reproducibility risks

1. Absolute “first” language rather than a qualified combined claim.
2. No machine-readable table of roots, jets, budgets, mesh levels, and
   residuals behind each phase diagram.
3. No robustness scan for patch width/location, contact radius, or initial
   law.
4. No units or declared norm behind control sensitivity and singular values.
5. Literature comparison discusses only mean FPT even though the contribution
   concerns the full density.

## 9. Submission decision rule

The project is plausibly PRR-level only if the exact finite-mode theorem and
physical-`d=2` fixed-control chain form one causal story.  Attractive reduced
mixtures or finite-grid curves alone are not enough.  The current strong
package is:

1. an independently accepted exact-`m` fixed-finite-`(d,m)` Doi theorem with
   the sequential `epsilon` then `B` quantifiers and complete finite-window
   topology stated honestly;
2. a production killed-process calculation for all 36 frozen
   control--configuration rows at one installed physical budget, with complete
   one-/two-/three-mode root and event-mass certificates;
3. odd/even, alignment, and box convergence with explicit uncertainty and no
   post-result retuning;
4. a physically distinct off-lattice event-law calculation using the same
   time windows and basin cuts; and
5. a focused physical-`d=2` manuscript that treats response jets and any
   fold/cusp identities as mechanism, not as an unperformed numerical cusp
   headline.

Positive-budget physical `d=3` and a numerical cusp may strengthen a later
paper, but neither is required for this focused route.  If the all-grid or
off-lattice chain holds, the bounded specialist result should be reported at
its honest PRE/JCP-style scope; the failed allocation cusp must not be revived
or retuned to preserve a PRR label.

## 10. BibTeX-ready primary-source identifiers

The following are the minimum primary sources to add to the eventual
bibliography.  Citation keys are suggestions only.

- `LindsaySpoonmoreTzou2016`: A. E. Lindsay, R. T. Spoonmore, and J. C. Tzou,
  “Hybrid asymptotic-numerical approach for estimating first-passage-time
  densities of the two-dimensional narrow capture problem,” *Phys. Rev. E*
  **94**, 042418 (2016). DOI `10.1103/PhysRevE.94.042418`;
  arXiv `1607.08095`; URL <https://arxiv.org/abs/1607.08095>.
- `LeVotYusteAbadGrebenkov2022`: F. Le Vot, S. B. Yuste, E. Abad, and D. S.
  Grebenkov, “First-encounter time of two diffusing particles in two- and
  three-dimensional confinement,” *Phys. Rev. E* **105**, 044119 (2022).
  DOI `10.1103/PhysRevE.105.044119`; arXiv `2201.05388`; URL
  <https://arxiv.org/abs/2201.05388>.
- `GiuggioliEtAl2024MultiTarget`: L. Giuggioli, S. Sarvaharman, D. Das,
  D. Marris, and T. Kay, “Multi-target search in bounded and heterogeneous
  environments: a lattice random walk perspective,” in *Target Search
  Problems* (Springer, 2024). DOI `10.1007/978-3-031-67802-8_5`; arXiv
  `2311.00464`; URL <https://arxiv.org/abs/2311.00464>.
- `MarrisHensGhoshGiuggioli2025`: D. Marris, C. Hens, S. Ghosh, and L.
  Giuggioli, “Predicting First-Passage Dynamics in Disordered Systems Exactly:
  Application to Sparse Networks” (2025). arXiv `2508.10140`; URL
  <https://arxiv.org/abs/2508.10140>.
- `HolehouseRedner2024`: J. Holehouse and S. Redner, “First-passage on
  disordered intervals,” *Phys. Rev. E* **109**, L032102 (2024). DOI
  `10.1103/PhysRevE.109.L032102`; arXiv `2307.08879`; URL
  <https://arxiv.org/abs/2307.08879>.
- `KeidarReuveni2026`: T. D. Keidar and S. Reuveni, “Universal linear
  response of first-passage kinetics: A framework for prediction and
  inference,” *Phys. Rev. Research* **8**, 023135 (2026). DOI
  `10.1103/c7wy-ddrc`; arXiv `2410.16129`; URL
  <https://arxiv.org/abs/2410.16129>.
- `Grebenkov2019Heterogeneous`: D. S. Grebenkov, “Spectral theory of imperfect
  diffusion-controlled reactions on heterogeneous catalytic surfaces,”
  *J. Chem. Phys.* **151**, 104108 (2019). DOI `10.1063/1.5115030`; arXiv
  `1908.01143`; URL <https://arxiv.org/abs/1908.01143>.
- `NicolaouMulder2023`: K. Nicolaou and B. M. Mulder, “A probabilistic
  algorithm for optimising the steady-state diffusional flux into a partially
  absorbing body,” *Scientific Reports* **13**, 22815 (2023). DOI
  `10.1038/s41598-023-49566-4`; URL
  <https://www.nature.com/articles/s41598-023-49566-4>.
- `IsaacsonMauroNewby2016`: S. A. Isaacson, A. J. Mauro, and J. Newby,
  “Uniform asymptotic approximation of diffusion to a small target:
  generalized reaction models,” *Phys. Rev. E* **94**, 042414 (2016). DOI
  `10.1103/PhysRevE.94.042414`; arXiv `1605.01279`; URL
  <https://arxiv.org/abs/1605.01279>.
- `Grebenkov2020LocalTime`: D. S. Grebenkov, “Paradigm shift in
  diffusion-mediated surface phenomena,” *Phys. Rev. Lett.* **125**, 078102
  (2020). DOI `10.1103/PhysRevLett.125.078102`; arXiv `2007.11224`; URL
  <https://arxiv.org/abs/2007.11224>.
- `GrebenkovWard2026Effective`: D. S. Grebenkov and M. J. Ward, “The Effective
  Reactivity for Capturing Brownian Motion by Partially Reactive Patches on a
  Spherical Surface,” *Multiscale Modeling & Simulation* (2026). DOI
  `10.1137/25M180562X`; arXiv `2509.26381`; URL
  <https://arxiv.org/abs/2509.26381>.
- `GrebenkovWard2026Planar`: D. S. Grebenkov and M. J. Ward, “Competition of
  small targets in planar domains: from Dirichlet to Robin and Steklov boundary
  condition,” *European Journal of Applied Mathematics* (2026). DOI
  `10.1017/S0956792525100284`; arXiv `2509.26367`; URL
  <https://arxiv.org/abs/2509.26367>.
- `Bressloff2021Fluxes`: P. C. Bressloff, “Asymptotic analysis of target
  fluxes in the three-dimensional narrow capture problem,” *Multiscale
  Modeling & Simulation* **19**, 612--632 (2021). DOI `10.1137/20M1380326`;
  arXiv `2011.08440`; URL <https://arxiv.org/abs/2011.08440>.
- `EkstromJanson2015`: E. Ekström and S. Janson, “The inverse first-passage
  problem and optimal stopping” (2015). arXiv `1508.07827`; URL
  <https://arxiv.org/abs/1508.07827>.
- `GiuggioliPerezBeckerSanders2013`: L. Giuggioli, S. Pérez-Becker, and D. P.
  Sanders, “Encounter times in overlapping domains: application to epidemic
  spread in a population of territorial animals,” *Phys. Rev. Lett.* **110**,
  058103 (2013). DOI `10.1103/PhysRevLett.110.058103`; arXiv `1207.2427`; URL
  <https://arxiv.org/abs/1207.2427>.
- `Giuggioli2020Confined`: L. Giuggioli, “Exact Spatiotemporal Dynamics of
  Confined Lattice Random Walks in Arbitrary Dimensions,” *Phys. Rev. X* **10**,
  021045 (2020). DOI `10.1103/PhysRevX.10.021045`; URL
  <https://doi.org/10.1103/PhysRevX.10.021045>.
- `WoodsWales2024`: C. J. Woods and D. J. Wales, “Analysis and interpretation
  of first passage time distributions featuring rare events,” *Phys. Chem.
  Chem. Phys.* **26**, 1640--1657 (2024). DOI `10.1039/D3CP04199A`; URL
  <https://doi.org/10.1039/D3CP04199A>.

## 11. Audit limitations

This scan prioritized original articles, journal landing pages, and arXiv
records through 2026-07-13.  Reviews were not used as evidence for novelty.
Searches covered multimodal/bimodal first-passage and reaction-time laws,
two-particle encounter in 2D/3D, heterogeneous Doi/Robin/local-time reaction,
fixed-resource reactivity optimization, inverse first passage, modality
fold/cusp terminology, and small-target/capacity asymptotics.

No bibliographic search can prove nonexistence, and terminology varies across
chemical kinetics, probability, narrow capture, and stochastic networks.  The
combined novelty claim should therefore be refreshed before submission and
tested by a domain expert familiar with both first-passage theory and
heterogeneous catalysis.
