# PRE cover-letter draft (single author, revised 2026-07-31, r3)

Dear Editors,

Please consider the enclosed manuscript, **"Spectral diagnostics and local
fixed-budget sensitivity of critical points in finite encounter-reaction
models,"** for publication as a Regular Article in *Physical Review E*.

Reaction-time densities of confined encounter reactions can acquire several
temporal structures through established transport and reactivity mechanisms;
Besga *et al.* (*Phys. Rev. E* **104**, L012102 (2021)) demonstrated a
Brownian first-passage shape transition of exactly this fold type. The
question addressed here is narrower and differential: when transport and the
initial law are fixed, how does redistributing a static finite-radius Doi
killing field change the positive-time critical points of a finite
encounter-reaction model, what does a fixed reactivity budget permit, and
what survives the continuum limit?

The paper makes four contributions. First, a reaction-support
Green--Woodbury reduction separates free transport, reaction geometry, and
killing strength. Second, a generalized-Descartes corollary gives a
necessary ordered-residue sign-variation gate for the number of interior
modes of a reversible finite model; the reversibility hypothesis is
verified directly for both generators to which the gate is applied. Third,
an exact Frechet--Duhamel identity gives the response of the critical-point
equation to every killing rate, with projection onto a declared budget
tangent space identifying the locally steepest feasible redistribution;
folds located by direct matrix-exponential derivatives in a two-reactant
chain and a finite-radius two-dimensional family recover the generic 1/2
and 3/2 normal-form exponents, and, for the encounter chain, the
normal-form amplitude to better than one percent. Fourth -- and this is
the part we believe will most interest referees -- an exact fold-transfer
theory (jet convergence from sectorial resolvent convergence, a
quantitative implicit-function transfer theorem, and a-posteriori
extrapolation control) is instantiated by a cell-averaged refinement
ladder run to 33x33 nodes under two independent transport discretizations
on the Isambard-AI facility, together with a 2x10^7-walker lattice-free
Brownian realization. The verdict is a sharp negative result with a clean
physical mechanism: the physical matched-budget path carries no interior
continuum fold; the finite-grid critical controls are mask-aliasing
artifacts; and the organizing fold sits at the admissibility edge of the
redistribution family, where the far-channel rate vanishes. At fixed
budget, spatial redistribution on this path tunes but cannot merge the two
arrival-time scales.

Scope boundaries are stated explicitly throughout, and exact algebraic
components of the calculus are machine-checked in Lean 4, with the
verification scope stated precisely in the Supplemental Material.

Disclosure of related work: a separate manuscript by the same author,
"Geometry-controlled folds of first-passage-time bimodality under localized
absorption," is under review at *Physical Review E* (submitted 30 July 2026;
accession code EU13106; the manuscript entered external review on 30 July 2026). It concerns
localized absorption of a single-particle first-passage law on an interval
and on finite networks. The present paper concerns two-particle encounter
reactions, a spectral necessary condition, a budget-constrained sensitivity
calculus, and a discrete-to-continuum transfer study; no numerical
evidence, model, or theorem overlaps between the two manuscripts.

The manuscript is not under consideration elsewhere, and I have no conflicts
of interest to declare.

Suggested referees familiar with imperfect reactivity, Doi-model numerics,
and first-passage phenomena:

- Denis S. Grebenkov (CNRS / Ecole Polytechnique, France)
- Samuel A. Isaacson (Boston University, USA)
- Paul C. Bressloff (Imperial College London, UK)
- Aljaz Godec (MPI for Multidisciplinary Sciences, Goettingen, Germany)

Thank you for your consideration.

Sincerely,
Xiaoxiao Zhouyi
School of Engineering Mathematics and Technology, University of Bristol
xiaoxiao.zhouyi@bristol.ac.uk
