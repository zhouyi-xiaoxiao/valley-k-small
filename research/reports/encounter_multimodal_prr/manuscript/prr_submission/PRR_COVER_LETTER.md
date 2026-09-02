<!-- Supersedes the longer 2026-08-14 working draft that conflated distinct
budget thresholds and described related manuscripts as non-overlapping. -->

# Cover letter — Physical Review Research

3 September 2026

Dear Editors,

Please consider my Regular Article, “Prescribing finite-window reaction-time
modes with a static fixed-budget Doi reactivity field,” for publication in
*Physical Review Research*.

The question is a design question of broad interest in diffusion-controlled
kinetics: a fixed reactivity budget — reactive patches on a surface, a
catalyst or enzyme load — installed once and never switched, is shown to
suffice for prescribing the number of peaks of a reaction-time distribution
on a chosen window, together with the complete peak–valley structure,
without the time-dependent barriers, gating states, or hidden kinetic phases
used by existing inverse-design constructions.

The manuscript asks whether a fixed amount of static spatial reactivity can be
arranged so that a two-particle Doi reaction-time density has exactly a
prescribed finite number of modes on a declared time window. Multimodal
first-passage densities are not themselves new: strategically placed traps,
multiple transport channels, stochastic gating, inverse first-passage
constructions, and multistage kinetic schemes can all produce or prescribe
rich timing laws. Nor is fixed-total spatial reactivity optimization itself
new; bulk, surface, and network variants precede this work. The specific
advance here is the conjunction of a more restrictive set of requirements.
The reactivity field is static in the
laboratory frame, nonnegative, and has a fixed centre-coordinate L1 mass;
the construction works for every fixed finite mode count and every fixed finite
physical dimension d >= 2; the theorem counts the complete alternating
stationary signature over the whole declared window uniformly over a compact
family of positive weights; and that signature is transferred from the free
exposure clock to a positive-budget Doi killed process.

The proof combines a global derivative-zero bound for separated Gaussian
exposure clocks, uniform root and complement margins after the encounter
contact factor is included, and compact-positive-time mixed-jet convergence.
The Gaussian-mixture mode bound and the Doi representation are prior
ingredients; their margin-bearing, whole-window positive-budget combination
under the static fixed-resource constraint is the new result. The quantifier
order is explicit: dimension and mode count are fixed first, then a sufficiently
small noise-and-width scale, and then a sufficiently small positive budget. No
claim is made about a common parameter set for all pairs (d, m), topology outside
the declared window, or switching among arbitrary mode counts on one fixed
support family.

A direct off-lattice realization tests the construction at finite parameters.
Two 48-cell mode-retention phase diagrams, operational budget-crossing
measurements, geometry and weight perturbations, an m = 5 realization, and a
d = 3 check show where the designed modes persist and where they are lost by
merger or depletion. That boundary is reproduced without adjustable
parameters, to within about 5%, by a mean-field hazard–survival law built from
the free exposure clock, so the finite-budget regime is quantitatively
understood; physically, the static slabs convert the deterministic relaxation
of a trapped pair into a prescribed sequence of reaction-time clocks. These
computations are presented as finite-parameter evidence: the classifier was
fixed in advance but is operational, and no numerical continuum theorem is
claimed. The manuscript also distinguishes the existential topological
threshold, an explicit sufficient analytic bound, and the
classifier-dependent numerical crossing. All code, the stored histogram
sufficient statistics and classifier diagnostics (including the
covariance-aware re-judgement of every stored record), and a Lean 4 package
that machine-checks kernels of the exact-m proof chain and selected kernels of
the explicit budget-threshold proposition (138 audited theorems, standard
axioms only) are public at
https://github.com/zhouyi-xiaoxiao/prescribed-reaction-time-modes (release
v1.0.0, SHA-256 manifest).

**Related manuscripts by the same author.** Two manuscripts from the same
research program are under consideration elsewhere:

1. “Geometry-controlled folds of first-passage-time bimodality under localized
   absorption,” submitted to *Physical Review E* (accession EU13106), studies
   folds of bimodality in a different localized-absorption model.
2. “Spectral diagnostics and local fixed-budget sensitivity of critical points
   in finite encounter-reaction models,” submitted to *The Journal of Chemical
   Physics* (manuscript JCP26-AR-03623), develops finite-state spectral and local
   fixed-budget-sensitivity tools and follows one matched-budget spatial
   redistribution path through a density-fold problem. It includes an exact
   fold-transfer theory, a two-discretization continuum-refinement bridge, and
   an off-lattice Brownian campaign with 20 million walkers per sampled
   control. Those calculations give a negative continuum result for that path:
   the finite-grid interior fold moves to the admissibility edge and no interior
   continuum fold remains. Its Supplemental Material also reports a bounded
   three-patch finite-grid trimodality diagnostic and a free-space narrow-patch
   GIG screen placing two to four prescribed clocks in dimensions one to four.

The JCP and PRR manuscripts therefore overlap in Doi/encounter coordinates,
fixed-budget spatial redistribution, continuum analysis, and off-lattice
simulation. They ask different questions on different control families. JCP
tests one fixed matched-budget path for a fold and rules out its interior
continuum persistence. The present PRR submission uses a different OU-slab
family to prove existence of arbitrary prescribed fixed finite modality,
including the exhaustive whole-window stationary signature, uniformity over
positive slab weights, and positive-budget topology transfer. Its separate
off-lattice campaigns map mode retention, operational thresholds, robustness,
(m=5), and (d=3); no scientific figure or table is reused from JCP. Current
copies of both related manuscripts and a point-by-point comparison will be
supplied to the editors.

Thank you for considering the manuscript.

Sincerely,

Xiaoxiao Zhouyi  
School of Engineering Mathematics and Technology  
University of Bristol, Bristol BS8 1TW, United Kingdom  
xiaoxiao.zhouyi@bristol.ac.uk
