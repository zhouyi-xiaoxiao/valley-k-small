# Round 09, reviewer A: prior-art novelty and journal-fit audit

**Audit date:** 2026-07-11  
**Overall submission gate:** **FAIL in the present wording; conditional PASS after the three B1 items below are resolved**  
**Fatal-duplication gate:** **PASS — no B0 duplicate of the full contribution was identified**  
**Current best journal route:** **PRE first if submitting the present evidence package; JCP first only after strengthening the continuum/chemical-physics layer; PRResearch is not recommended in the present form**

## 1. Scope, evidence labels, and limits of this audit

I audited the novelty claims in `manuscript/encounter_modality_jcp.tex`, especially
lines 96--186 and 1360--1508, against primary papers, publisher pages, and official
journal pages available through 2026-07-11. I did not use another Round-09 review.

The labels below have precise meanings:

- **[C] confirmed:** the linked primary source or official page states the fact.
- **[I] inference:** a reasoned comparison between the source and this manuscript,
  not a fact asserted by the source.
- **[N] targeted negative search:** I found no direct duplicate in the searched
  literature. This is evidence for a defensible “to our knowledge” claim, not proof
  of global absence. A closed Scopus/Web of Science/Crossref citation search by an
  information specialist would be needed for a formal novelty opinion.

The manuscript already exercises unusually good restraint: it explicitly says that
Green functions, multi-target reductions, heterogeneous reactivity, bimodality, and
higher-dimensional encounter distributions are not new. The remaining problem is
not wholesale overclaiming; it is that the narrow surviving increment is not yet
distinguished sharply enough from the closest Giuggioli precedents.

| Severity | Count | Gate |
|---|---:|---|
| B0 | 0 | **PASS** |
| B1 | 3 | **FAIL** until resolved |
| B2 | 5 | Open; does not alone fail the narrow novelty claim, but controls journal ceiling |
| B3 | 3 | Open editorial hardening |

## 2. Executive novelty finding

The following claims **do not survive** a prior-art challenge:

1. first Green/Woodbury or defect reduction for encounter/reaction problems;
2. first theory of multiple heterogeneous reactive locations;
3. first heterogeneous catalytic reaction-time distribution;
4. first bimodal or multimodal first-passage/reaction-time density in 1D or 2D;
5. first use of a GIG law as a first-hitting-time family;
6. first logarithmic/Newtonian capacity or effective-radius law;
7. first general multi-target design or multiple-peak configuration;
8. first demonstration that changing a reaction mechanism can change a
   first-reaction-time density from one mode to two.

The strongest **defensible** increment is narrower:

> **[I/N] For a fixed transport process and a declared fixed integrated-killing
> budget, spatial redistribution of finite-radius Doi reactivity is used to select
> encounter channels and change the number of resolved reaction-time modes; the
> transition is located by channel-resolved derivative conditions for a
> nondegenerate physical-parameter fold, with finite-grid 2D controls and a
> finite-grid three-channel mechanism certificate.**

I did not identify a primary paper that contains that complete combination. This is
publishable novelty if stated exactly at its current evidence level. The manuscript
must not shorten it to “spatial heterogeneity creates multiple peaks,” because that
statement is already occupied by several literatures.

## 3. Claim-by-claim prior-art matrix

| Element | Confirmed prior art | What, if anything, survives here | Novelty verdict |
|---|---|---|---|
| **Encounter Green/Woodbury and channel fluxes** | Giuggioli gives exact confined lattice propagators in arbitrary dimensions, first-passage laws to single/multiple targets, and partially absorbing traps ([PRX 2020](https://doi.org/10.1103/PhysRevX.10.021045)). Giuggioli and Sarvaharman treat multiple heterogeneous reactive encounter locations and exact mean reaction time ([J. Phys. A 2022](https://doi.org/10.1088/1751-8121/ac8587)). Grebenkov represents heterogeneous catalytic reactivity by a matrix in a Dirichlet-to-Neumann basis and derives survival and reaction-time distributions ([JCP 2019](https://doi.org/10.1063/1.5115030)). Bressloff obtains target-resolved Laplace fluxes with Green matrices for multiple reactive targets ([MMS 2021](https://doi.org/10.1137/20M1380326); [PRE 2022](https://doi.org/10.1103/PhysRevE.105.034141)). | The inverse-free restriction to the Doi support, zero-rate-safe implementation, channel derivatives, and explicit use as the computational layer for a modality fold are a useful synthesis. The Woodbury identity and the existence of a reduced reactive matrix are not the invention. | **Not novel alone; moderate enabling-method novelty only when tied to the fold observable.** |
| **Two-channel GIG fold** | A GIG family with nonpositive power was proved to be a first-hitting-time law of diffusions in 1978 ([SPA 7, 49](https://doi.org/10.1016/0304-4149%2878%2990036-4)); GIG first-passage modeling was used explicitly in 1997 ([Biol. Cybern.](https://doi.org/10.1007/s004220050390)). Modality boundaries of mixture densities and degenerate critical points are a mature subject; see the ridgeline/modality theory of Ray and Lindsay ([Ann. Stat. 2005](https://doi.org/10.1214/009053605000000417)). | The specific relative/centre free-encounter mapping to a GIG exponent, the physical interpretation of the parameters, and elimination of the two-channel fold along a declared physical path appear useful. The manuscript correctly calls this a screening law because it has no uniform confined-channel remainder. | **Potentially novel application/algebra; GIG and generic fold theory are not novel.** |
| **Reactivity-induced reaction-time bimodality** | Grebenkov's encounter/local-time framework separates transport from surface reaction mechanism ([PRL 2020](https://doi.org/10.1103/PhysRevLett.125.078102)). Its published [Supplemental Material](https://pmc.polytechnique.fr/pagesperso/dg/publi/2020_06_SM.pdf), Fig. S6, explicitly shows a reaction-time density changing progressively from monomodal to bimodal when the surface is initially passive and activates after accumulated encounters. | That control is history/local-time dependent on one surface. The present control is a static **spatial** Doi killing field, redistributed at fixed transport and integrated budget, and the transition is located as a derivative-certified physical fold. | **Very close conceptual prior; direct citation and distinction are mandatory.** |
| **2D patterned Doi reaction-time fold** | Doi volume reaction and its continuum/discrete limits are established ([Doi 1976](https://doi.org/10.1088/0305-4470/9/9/009); [Isaacson 2013](https://doi.org/10.1063/1.4816377); [Isaacson--Mauro--Newby 2016](https://doi.org/10.1103/PhysRevE.94.042414)). Heterogeneous reactivity operators are established by Grebenkov 2019, while Grebenkov 2020 already demonstrates reaction-mechanism-induced mono/bimodality. Lindsay, Spoonmore, and Tzou compute full 2D narrow-capture densities and explicitly obtain multimodal behavior when traps are strategically arranged ([PRE 2016](https://doi.org/10.1103/PhysRevE.94.042418)). | **[N]** I found no direct prior work that holds the transport generator and integrated killing fixed, redistributes finite-radius Doi reactivity, separates channel fluxes, and locates the induced modality transition with \(f_t=f_{tt}=0\) plus nondegeneracy/transversality checks. This is the manuscript's strongest novelty. | **Strong likely novelty as a finite-grid mechanism; not yet a continuum fold or converged critical value.** |
| **Two- and three-patch multiple modes** | Multiple peaks are explicit in Giuggioli-related work ([PRE 2020](https://doi.org/10.1103/PhysRevE.102.062124); [Springer chapter 2024](https://doi.org/10.1007/978-3-031-67802-8_5); [NJP 2024](https://doi.org/10.1088/1367-2630/ad5d85); [arXiv:2508.10140](https://arxiv.org/abs/2508.10140)), in strategically arranged 2D traps ([PRE 2016](https://doi.org/10.1103/PhysRevE.94.042418)), and in disordered intervals ([PRE 2024](https://doi.org/10.1103/PhysRevE.109.L032102)). | The matched-transport/matched-budget attribution of individual maxima to near/middle/far Doi channels, including five alternating derivative roots on four grids, is a more specific mechanism certificate than a multipeak plot. | **Novel configuration evidence is plausible; “first trimodality” or “general multipeak criterion” would fail.** |
| **Capacity and Doi effective radius** | Small-target logarithmic and Newtonian capacity, partial reactivity, competition, and Green-matrix interactions are established. Relevant primary sources include Bressloff--Schumm's partially absorbing volume targets in 2D/3D ([MMS 2022](https://doi.org/10.1137/21M1449580)), Grebenkov--Ward's planar competing patches ([EJAM 2026](https://doi.org/10.1017/S0956792525100284)), and effective partially reactive patches on a sphere ([MMS 2026](https://doi.org/10.1137/25M180562X)). | Reproducing the correct laws is an important validation of the solver and parameter scaling. It does not create a new capacity theory and does not validate centre-patterned modality. | **Validation, not novelty.** |
| **Constructive multidimensional design** | Multi-target placement and transport optimization are established; Giuggioli 2020 treats target number/location effects, and mixture-mode design is not conceptually new. | The closed prescription $A_j=B m_j^2+p m_j$, inverse-isolated-height weights, and the 12 checked $d=1,\ldots,4$ GIG cases appear to be a compact new screening construction. However, the weights are not yet realized by bounded finite-radius Doi patches, and no exclusion theorem proves the exact number of roots. | **Moderate, supporting novelty; not a general multidimensional encounter-design theorem.** |
| **Generic fold exponents** | A saddle-node/fold and its square-root root separation are standard local bifurcation facts; mixture-modality boundaries are standard as above. | The physical-path transversality check and direct matrix/PDE derivative evaluation are valuable in this reaction-time setting. | **Application novelty only. Do not present the $1/2$ and $3/2$ exponents as new mathematics.** |

## 4. Relationship to Luca Giuggioli's work

This relationship needs to be presented as a **direct continuation with a new
observable and control experiment**, not merely as broad background.

### 4.1 Confirmed overlap map

| Work | What it already establishes | Correct distinction for this manuscript |
|---|---|---|
| Giuggioli, Pérez-Becker, Sanders, *Encounter times of random walkers with overlapping domains*, [PRL 110, 058103 (2013)](https://doi.org/10.1103/PhysRevLett.110.058103) | **[C]** Encounter/transmission of two walkers whose accessible domains overlap. | The present work adds spatially selected finite-rate reaction channels and studies the shape of the full reaction-time density. |
| Giuggioli, *Exact spatiotemporal dynamics of confined lattice random walks in arbitrary dimensions*, [PRX 10, 021045 (2020)](https://doi.org/10.1103/PhysRevX.10.021045) | **[C]** Exact propagators, first passage to single/multiple targets, and partial absorption in arbitrary-dimensional confined lattices. | Green/propagator and multi-target machinery are inherited context. The claimed increment must be a modality boundary under a physical reactivity control. |
| Sarvaharman and Giuggioli, *Closed-form solutions ... biased lattice random walks*, [PRE 102, 062124 (2020)](https://doi.org/10.1103/PhysRevE.102.062124) | **[C]** The abstract explicitly reports **bimodal first-passage probabilities** in periodic domains and multi-target placement effects. | This is the most important missing citation. It establishes transport/bias-generated bimodality; the new comparison is reactivity redistribution at fixed transport. |
| Giuggioli and Sarvaharman, *Spatio-temporal dynamics of random transmission events*, [J. Phys. A 55, 375005 (2022)](https://doi.org/10.1088/1751-8121/ac8587) | **[C]** An analytic theory in arbitrary spatial domains and arbitrary transfer efficiency; exact mean reaction time with multiple heterogeneous reactive locations. | The present work cannot claim heterogeneous locations or general transmission theory. It moves from the mean to full density shape, channel-resolved modes, and a fold calculation. |
| Das and Giuggioli, *Discrete space-time resetting model*, [J. Phys. A 55, 424004 (2022)](https://doi.org/10.1088/1751-8121/ac9765) | **[C]** First-passage and two-walker transmission with resetting; the paper reports multi-fold nonmonotonic behavior of first-passage mode probability as resetting varies. | Resetting changes transport. The present control changes only the killing field along the matched-budget path. “Fold” must be defined as coalescence of time-density critical points, not merely nonmonotonicity of a mode statistic. |
| Sarvaharman and Giuggioli, [PRResearch 5, 043281 (2023)](https://doi.org/10.1103/PhysRevResearch.5.043281) | **[C]** Exact defect treatment of inert particle--environment heterogeneities, including propagators and first-passage/splitting observables. | This is transport disorder, not spatial Doi killing. It reinforces the need to state that the transport generator is held fixed. |
| Giuggioli *et al.*, *Multi-target Search in Bounded and Heterogeneous Environments*, [Springer chapter (2024)](https://doi.org/10.1007/978-3-031-67802-8_5) | **[C]** The abstract and full Bristol preprint explicitly show multiple first-passage peaks for biased walkers, partially absorbing targets/radiation boundaries, 2D disorder affecting two-target splitting, and first-reaction dynamics. The full text contains no “fold” or “modality” formulation. | This source must be described as a direct multiple-peak precedent, not only as a generic multi-target reduction. The defensible addition is a catalytic-pattern control and derivative-level fold, not the observation of peaks. |
| Barbini and Giuggioli, *Lattice Random Walk Dynamics with stochastic resetting in heterogeneous space*, [J. Phys. A 57, 425001 (2024)](https://doi.org/10.1088/1751-8121/ad7ca2) | **[C]** A heterogeneous two-medium/resetting model with nonmonotonic dependence of the first-passage mode on bias. | Adjacent prior art for mode control by transport heterogeneity; again distinct from fixed-transport catalytic redistribution. |
| Marris and Giuggioli, *Persistent and anti-persistent motion ...*, [NJP 26, 073020 (2024)](https://doi.org/10.1088/1367-2630/ad5d85) | **[C]** In arbitrary-dimensional correlated lattice walks, strong persistence produces first-passage multimodality, which boundary reversal can suppress. | A direct Luca-line multimodality precedent generated by temporal transport correlations, not by a static spatial killing field. |
| Marris, Hens, Ghosh, and Giuggioli, *Predicting First-Passage Dynamics in Disordered Systems Exactly*, [arXiv:2508.10140 (2025)](https://arxiv.org/abs/2508.10140) | **[C]** The primary preprint identifies a first-passage/first-absorption bimodality regime on sparse small-world networks and attributes its modes to trajectory classes. As of the audit cutoff I found a preprint, not an official journal version. | This is especially close in language (“bimodality regime” and trajectory attribution) but changes the network transport. The new paper must reserve its claim for **catalytic spatial redistribution and derivative fold location**. |
| Kay and Giuggioli, permeable-interface/local-time works ([PRResearch 4, L032039 (2022)](https://doi.org/10.1103/PhysRevResearch.4.L032039); [PRResearch 7, 013097 (2025)](https://doi.org/10.1103/PhysRevResearch.7.013097)) | **[C]** Microscopic defect/local-time descriptions of permeable barriers and crossing statistics. | Adjacent mathematical lineage, but no direct duplicate of the Doi modality-fold result was found. |

The 2026 Das--Giuggioli tethering paper ([PRE 113, 044102](https://doi.org/10.1103/5w7v-8hx7)) studies first-passage variables under focal potentials; I found no direct spatial-reactivity modality-fold overlap. It should be monitored but is not presently a blocking citation.

### 4.2 The one-sentence positioning that survives

An accurate positioning sentence would be:

> Prior Giuggioli work established exact propagators, multi-target and partially
> absorbing encounter/transmission laws, and transport-generated first-passage
> bimodality, while Grebenkov showed that encounter-history-dependent surface
> reactivity can itself induce reaction-time bimodality; here we keep the transport
> dynamics fixed and ask whether a **static spatial**, fixed-budget redistribution
> of finite-radius Doi reactivity selects those clocks strongly enough to cross a
> derivative-certified reaction-time modality fold.

This sentence makes the scientific lineage explicit while preserving the real new
question.

## 5. Severity-ranked findings

### B0 — none

No source found contains the complete package of fixed-transport/fixed-budget Doi
reactivity redistribution, channel-resolved full reaction-time fluxes, a physical-path
fold with nondegeneracy checks, the matched patterned/homogeneous 2D controls, and
the bounded three-channel finite-grid certificate. There is therefore no demonstrated
fatal duplication.

### B1-1 — closest Giuggioli multiple-peak/mode precedents are under-described

**Status: FAIL.** `references.bib` contains the 2024 chapter but not Sarvaharman--
Giuggioli 2020, Das--Giuggioli 2022, Marris--Giuggioli 2024, Barbini--Giuggioli
2024, or the 2025 Marris *et al.* preprint. More importantly, the introduction
(`encounter_modality_jcp.tex:96-107`) and novelty paragraph (`:1453-1468`)
describe the Giuggioli line mainly as propagators, heterogeneous locations, and
multi-target reductions. They do not tell the reader that this line already
exhibits bimodal/multiple first-passage peaks, arbitrary-dimensional
transport-generated multimodality, a bimodality regime on a disordered network,
and mode nonmonotonicity.

**Required resolution:** add at least [PRE 102, 062124](https://doi.org/10.1103/PhysRevE.102.062124),
[NJP 26, 073020](https://doi.org/10.1088/1367-2630/ad5d85), and
[J. Phys. A 55, 424004](https://doi.org/10.1088/1751-8121/ac9765); describe the
multiple-peak result in the cited 2024 chapter explicitly; and state the
fixed-transport/fixed-budget distinction in both the introduction and novelty
subsection. Discuss [arXiv:2508.10140](https://arxiv.org/abs/2508.10140) as a
preprint if the journal's citation policy permits. Barbini--Giuggioli 2024 is
also recommended.

### B1-2 — the novelty paragraph still lists established machinery as part of “the increment”

**Status: FAIL.** At `encounter_modality_jcp.tex:1464-1468`, “channel-resolved Green
response” appears in the list of increments. In light of Giuggioli 2020/2022,
Grebenkov 2019, and Bressloff 2021/2022, a referee can read this as claiming a new
Green or target-resolved reaction formalism even though lines 105--107 disclaim that
claim.

**Required resolution:** make the novelty grammatical object the **modality
calculation**, not the Green representation. For example:

> We use established Green/multi-target ideas as a computational layer. The new
> result is their deployment in a matched physical experiment in which only the
> spatial Doi reactivity is redistributed, together with derivative-level location of
> the resulting reaction-time fold and a bounded finite-grid three-channel
> mechanism certificate.

Keep “finite-grid” in the sentence. Do not call the restricted Woodbury identity a
new theory.

### B1-3 — Grebenkov 2020 already shows reaction-mechanism-induced mono/bimodality

**Status: FAIL.** Grebenkov's [PRL 2020](https://doi.org/10.1103/PhysRevLett.125.078102)
and its [Supplemental Material](https://pmc.polytechnique.fr/pagesperso/dg/publi/2020_06_SM.pdf)
are absent from `references.bib`. Figure S6 and the accompanying text explicitly
show a first-reaction-time density changing from monomodal to bimodal as an
initially passive surface becomes reactive after a prescribed accumulated local
time. This directly precludes a broad claim that the present paper is the first to
control reaction-time modality through reactivity.

**Required resolution:** cite the PRL and state the distinction precisely:
Grebenkov changes a history/encounter-dependent surface reaction law, whereas the
present manuscript redistributes a time-independent **spatial** Doi killing field
at fixed transport and fixed integrated budget, then locates a derivative-level
fold. That narrower statement still appears to survive.

### B2-1 — add foundational GIG first-passage citations

**Status: open.** The current bibliography does not identify the longstanding GIG
first-hitting-time literature. Add at least Barndorff-Nielsen, Blæsild, and
Halgreen, [doi:10.1016/0304-4149(78)90036-4](https://doi.org/10.1016/0304-4149%2878%2990036-4). Iyengar and Liao,
[doi:10.1007/s004220050390](https://doi.org/10.1007/s004220050390), is an optional
application citation. Say that the **mapping and design use**, not the GIG family or
its mode formula, is the contribution.

### B2-2 — the 2D fold is the main novelty but remains a finite-grid certificate

**Status: open.** The manuscript correctly discloses that the two fold coordinates
differ by 0.242, that the critical value is not grid-converged, that the coarsest
midpoint/weighted convention changes modality label, and that no independent Robin
solver is present (`:1482-1498`). This honesty protects correctness but weakens JCP
and PRResearch significance.

**Best strengthening experiment:** compute the matched-budget fold on at least three
successively refined cell-averaged grids with the physical patch radii fixed, and add
either (i) an independently implemented Robin/radiation solver with a calibrated
Doi--Robin map, or (ii) a finite-volume convergence bound sufficient to bracket a
continuum fold. A robust endpoint change alone is publishable at PRE, but it is less
compelling as the headline of a JCP “predictive boundary” paper.

### B2-3 — the trimodal and multidimensional claims must remain certificates/screening

**Status: open.** No continuum trimodal region, cusp, general-(d) theorem, physical
realization of the designed weights, or certified exclusion of extra tangencies has
been established. Retain the existing limitations. In the abstract/conclusion, use
“bounded finite-grid trimodality mechanism certificate” and “free-space GIG screening
construction,” never “general explanation of multidimensional multimodality.”

### B2-4 — capacity is validation and should not carry novelty weight

**Status: open.** The capacity benchmarks are valuable QA, but current 2025--2026
literature makes this territory especially mature: Grebenkov's Steklov treatment of
non-spherical imperfect targets ([JCP 163, 034106](https://doi.org/10.1063/5.0278477)),
Grebenkov--Ward's planar competition ([doi:10.1017/S0956792525100284](https://doi.org/10.1017/S0956792525100284)),
and spherical reactive patches ([doi:10.1137/25M180562X](https://doi.org/10.1137/25M180562X)). Keep the capacity material as solver calibration and dimensional consistency, not a headline contribution.

### B2-5 — update the reaction-time landscape through 2026

**Status: open, nonblocking to originality.** Ye and Grebenkov now study the joint
first-reaction-time/boundary-local-time distribution under partial reaction
([JCP 164, 084102 (2026)](https://doi.org/10.1063/5.0317675)). It does not duplicate
the spatial modality fold, but it is a current first-reaction-distribution source and
would improve a JCP-facing literature paragraph.

### B3-1 — add an explicit “not claimed” sentence immediately after the abstract result list

Suggested text: “Neither multimodal first-passage densities, heterogeneous reactive
targets, Green reductions, nor capacity laws are claimed as new; the claim concerns
their fixed-transport connection at a spatial-reactivity modality fold.” This would
prevent editors from evaluating the paper against an unintended broad claim.

### B3-2 — keep three different uses of “mode” lexically separate

Use **density mode** for a time-domain maximum, **spectral mode/pole** for an
eigenvalue contribution, and **transport channel** for a path family. The manuscript
already warns that a spectral pole need not create a visible density mode; carry that
distinction into the abstract and cover letter.

### B3-3 — do not use journal metrics or third-party quartiles as quality claims

Metrics and domestic partition labels vary by year and category. They are suitable
for administrative routing, not as evidence that the result is scientifically strong.

## 6. Journal-fit audit

### 6.1 Physical Review E — **PASS after B1 revision; best immediate target**

**[C]** PRE explicitly covers statistical physics, stochastic processes, nonlinear
dynamics/bifurcations, biological physics, and computational physics. Its acceptance
criteria require a high-quality, significant, substantive addition. The official page
reports 2025 JIF 2.5 and ISSNs 2470-0045/2470-0053
([PRE About](https://journals.aps.org/pre/about)).

**[I]** The paper's central object is a stochastic first-reaction density and its
modality bifurcation; PRE has already published the closest first-passage papers cited
above. The finite CTMC certificate, finite-grid 2D fold/endpoints, and transparent
limitations form a coherent PRE regular article even without a continuum theorem.
The main editorial risk is novelty positioning, not scope.

**Recommended PRE pitch:** “A physical control of reaction-time modality under fixed
transport and reaction budget,” with the Luca/Lindsay/Holehouse distinctions in the
first page. Do not pitch “first multimodal first passage.”

### 6.2 The Journal of Chemical Physics — **scope PASS, evidence CONDITIONAL**

**[C]** AIP states that JCP publishes “quantitative and rigorous science of
long-lasting value in methods and applications of chemical physics.” Its official
journal finder lists chemical physics and biological physics, 2025 JCR JIF 3.7, and
ISSNs 0021-9606/1089-7690
([JCP description](https://publishing.aip.org/publications/journals/special-topics/jcp/);
[AIP journal finder](https://publishing.aip.org/publications/find-the-right-journal/)).
Grebenkov's heterogeneous catalytic surface paper and several current imperfect-
reaction papers in JCP confirm topical scope.

**[I]** JCP becomes the best target if the manuscript foregrounds a chemically
interpretable catalytic-patch problem and supplies a stronger continuum/calibration
link. In the current package, the decisive physical fold is not grid-converged, the
bounded trimodality is finite-grid, and the GIG design is screening only. That makes
an editor likely to ask whether the paper is primarily a mathematical stochastic-
process study rather than a lasting chemical-physics method.

**Gate:** JCP first is reasonable only after B1-1/B1-2 and preferably B2-2. Without
new numerical/continuum evidence, PRE is the lower-risk and better-aligned first
submission.

### 6.3 Physical Review Research — **FAIL for the present package**

**[C]** PRResearch is a fully open-access multidisciplinary journal covering all
physics and requires a high-quality, significant, authoritative and substantive
addition. The official page reports 2025 JIF 4.0 and ISSN 2643-1564
([PRResearch About](https://journals.aps.org/prresearch/about)); its subject list
includes statistical and chemical physics
([subjects](https://journals.aps.org/prresearch/subjects)).

**[I]** Scope is not the problem. The current result is narrow and technically rich,
but the principal continuum fold and general multidimensional design theorem are
both explicitly absent. The direct Grebenkov/Luca/Lindsay prior art also reduces
the apparent breadth of “multimodality” as a hook. PRResearch would become credible if the work
delivered one of the following: a continuum persistence theorem; a converged 2D
fold/phase boundary with independent solver validation; or a physically realized
multi-$d$, multi-patch design law with predictive tests outside the fitted cases.

### 6.4 Journal of Physics A — **viable alternative after refocus**

**[I]** J. Phys. A is a natural lineage venue for the exact propagator, transmission,
GIG, and fold algebra, and several closest Giuggioli papers appeared there. It becomes
competitive if the paper is shortened around the operator reduction, fold equations,
and mathematical design construction. The current manuscript's extensive catalytic
and finite-radius validation instead supports trying PRE/JCP first.

### 6.5 Recommended order

1. **If submitting without another continuum campaign:** PRE, then JCP, then J. Phys. A. Do not lead with PRResearch.
2. **If B2-2 is completed and a chemical use-case is sharpened:** JCP, then PRE.
3. **If a genuine continuum/multidimensional theorem is added:** reconsider PRResearch.

## 7. Domestic partition / “中科院分区” reporting

I make **no numerical CAS-zone assertion** for JCP, PRE, or PRResearch.

**[C]** The official service is the Chinese Academy of Sciences Literature and
Information Center journal partition platform, [fenqubiao.com](https://www.fenqubiao.com/).
CAS and university library pages state that the current platform requires authorized
IP/account access, provides both broad and narrow subject categories, and restricts
redistribution of the data
([CAS institute access page](https://scsio.cas.cn/lib/dzfw/zkyfqbcx/);
[USTC library description](https://lib.ustc.edu.cn/%E7%94%B5%E5%AD%90%E8%B5%84%E6%BA%90/%E4%B8%AD%E5%9B%BD%E7%A7%91%E5%AD%A6%E9%99%A2%E6%9C%9F%E5%88%8A%E5%88%86%E5%8C%BA%E5%9C%A8%E7%BA%BF%E5%B9%B3%E5%8F%B0/)). The publicly accessible pages do not expose the three journal records in a way I can independently verify.

Therefore the only defensible administrative procedure is:

1. query the official platform using the exact ISSN;
2. record the **version year**, **broad category**, **narrow category**, **zone**, and
   **TOP flag** from the authenticated result;
3. save an institutionally permitted screenshot or lookup certificate;
4. do not substitute LetPub, SCImago quartiles, JCR quartiles, or JIF for a CAS zone.

Exact lookup keys:

| Journal | Exact ISSN(s) | Publicly verified 2025 publisher metric |
|---|---|---|
| The Journal of Chemical Physics | 0021-9606; 1089-7690 | JIF 3.7 (AIP/2025 JCR data) |
| Physical Review E | 2470-0045; 2470-0053 | JIF 2.5 (APS 2025 metrics) |
| Physical Review Research | 2643-1564 | JIF 4.0 (APS 2025 metrics) |

These metrics are not CAS partitions.

## 8. Minimum remediation for a PASS

The novelty gate can pass without changing the scientific results if all of the
following are done:

1. add and discuss the direct Giuggioli multimodality/mode-control precedents,
   especially 10.1103/PhysRevE.102.062124, 10.1088/1367-2630/ad5d85,
   10.1088/1751-8121/ac9765, and arXiv:2508.10140;
2. add and distinguish Grebenkov's reaction-mechanism-induced bimodality,
   10.1103/PhysRevLett.125.078102;
3. rewrite the novelty paragraph so Green/Woodbury, GIG, capacity, and multiple
   peaks are explicitly prior machinery, while the matched physical fold is the
   object of the new claim;
4. add a foundational GIG first-hitting-time citation;
5. keep “finite-grid mechanism certificate” and “screening construction” in every
   high-visibility statement of trimodality/multidimensional design;
6. choose the journal route honestly: PRE for the current evidence; JCP after a
   stronger continuum/chemical layer; PRResearch only after a broader theorem or
   predictive continuum phase boundary.

After items 1--5, my novelty verdict would change to **PASS with B2 limitations**.
Item 6 is a strategic submission choice rather than a correctness condition.
