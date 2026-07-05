# Cover letter draft — PRR submission (DPMA saddle-node manuscript)

> Draft for Luca/Xiaoxiao to adapt. Defensive PRR framing per the 2026-07-02 external review:
> lead with "known phenomenology → exact fold threshold", disclaim first-observation, point to the
> reproducibility archive. Replace bracketed placeholders before use.

---

Dear Editors,

Please consider our manuscript "Saddle-node bifurcation of first-passage-time densities induced by
a directed shortcut" for publication in Physical Review Research as a Regular Article.

This manuscript does **not** claim the first observation of bimodal first-passage-time densities in
shortcut-assisted search — that phenomenology is well documented. What has been missing, and what
we provide, is an exact bifurcation-theoretic classification of it. In a minimal directed-shortcut
model (equivalently, a rank-one killing defect; in the diffusive limit, Brownian motion with an
interior delta-sink), the first-passage-time density is a signed spectral mixture, and the creation
and annihilation of its finite-time arrival peak is governed by the compact fold criterion
S1 = S2 = 0 in signed spectral moments. This yields:

- a computable threshold b_c(theta), with an endpoint constant fixed by an explicit half-line
  transform (B* = 0.7890262) and confirmed independently to six digits;
- the generic saddle-node exponents (1/2, 3/2) with prefactors analytic in the fold data;
- a minimal-mode theorem (at least three spectral modes, with alternating signs), consistent with
  Laguerre's rule for exponential sums;
- an experimentally measurable morphology transition, distinct from both the mean first-passage
  time and the spectral gap — and demonstrably *not* a spectral exceptional point.

The classification is validated by an independent chain that uses none of the exact machinery:
direct Monte Carlo on the lattice, an exact absorption-channel decomposition, off-gate starts
(under which both features are genuine interior peaks), and Brownian-dynamics simulations of the
physical delivery-gate protocol, with documented gate-width and time-step convergence. The fold
threshold itself converges from the finite lattice to the continuum as N^-2 (fitted exponent 2.08). Extensions (a
rank-two cusp organizing a triple-peak region; finite two-dimensional lattices) are presented as
supporting evidence with their limitations stated explicitly. In addition to these numerical
cross-checks, the manuscript's entire exact-algebra layer — the finite-N determinant and residue
chain, the splitting probability, the continuum amplitude and normalization identities, the
minimal-mode theorem, and the normal-form prefactors — has been machine-verified in Lean 4
against the mathlib library (46 theorems, no unproven placeholders, standard axioms only); the
formal audit package accompanies the reproducibility archive.

We believe the result is of interest to the broad Physical Review Research readership working on
stochastic transport, first-passage statistics, and controlled colloidal experiments: it converts
a familiar qualitative phenomenology into a predictive, exactly computable observable-level
bifurcation, with a concrete measurement protocol (a ratio observable resolvable in ~10^4–10^5
delivery-and-terminate trials).

All code and numerical data required to reproduce every figure and quoted number are publicly
available at [repository URL], archived at Zenodo, DOI: [DOI].
*(If the archive is not yet public at submission time, delete the previous sentence and rely on
the manuscript's availability statement.)*

Suggested referees: [names — e.g., researchers in first-passage theory / stochastic resetting /
diffusion-controlled reactions, excluding recent collaborators].

Sincerely,
Xiaoxiao Zhouyi and Luca Giuggioli
University of Bristol

---

## Notes for the authors (not part of the letter)

- **Title option** (external review suggestion, author decision): "Observable saddle-node
  bifurcation in shortcut-assisted first-passage statistics" — softer on "directed", stronger on
  the observable. Current title kept because the directed shortcut names the model honestly and the
  directedness caveat now appears in the abstract and Sec. I/II.
- Venue: PRR first (automatic PRE transfer on rejection); PRE directly is the conservative option.
- Before sending: mint the Zenodo DOI (see extras/reproducibility/README.md), fill the funding
  line, and confirm author order.
- The public repository/Zenodo package must include `code/formal_lean/` (sources + pinned
  `lake-manifest.json` + `axioms_report_20260705.txt`) so the letter's machine-verification
  sentence is backed by the archive; reviewers re-verify with `lake exe cache get && lake build`.
