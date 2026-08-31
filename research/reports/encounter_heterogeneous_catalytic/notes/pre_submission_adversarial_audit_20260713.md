# Independent PRE-oriented adversarial audit — 2026-07-13

## Decision

**Major revision completed at the claim-accuracy layer; release remains on
HOLD.** No error was found that overturns the exact finite-matrix identities or
the archived finite-state fold calculations. The manuscript is a strong
topical fit for *Physical Review E*, but the finite-grid evidence does not
support a continuum modality theorem and the submission metadata and clean-tag
release chain remain author-owned blockers.

The acceptance ranges below are reviewer judgments, not official journal
statistics:

| Package state | Estimated chance of external review | Estimated eventual PRE acceptance |
|---|---:|---:|
| Pre-audit manuscript | 50--65% | 25--35% |
| Present claim/literature/formal repairs, without new continuum numerics | 65--75% | 40--50% |
| Plus prospective held-out validation of the projected design direction | 75--85% | 50--60% |
| Plus independent converged FV/FEM, Robin, or Brownian validation | 80--90% | 60--70% |

## Submission-blocking findings repaired in this pass

1. **Closest same-journal prior art.** Besga *et al.*, *Phys. Rev. E* **104**,
   L012102 (2021), DOI
   [10.1103/PhysRevE.104.L012102](https://doi.org/10.1103/PhysRevE.104.L012102),
   already demonstrated a Brownian first-passage shape transition driven by
   the target-distance/initial-spread ratio. The manuscript now cites it in
   the abstract-facing positioning, introduction, and novelty discussion and
   explicitly disclaims priority for a two-clock transition or the equations
   `f_t=f_tt=0`. The retained distinction is static finite-radius Doi killing
   redistributed at fixed transport, fixed initial law, and fixed discrete
   budget.
2. **Overbroad design language.** The title and main narrative now describe
   *local fixed-budget sensitivity of critical points*. The result is a
   unit-norm infinitesimal optimum in a declared metric, not a finite-amplitude
   shape or binary-mask optimizer.
3. **Operational versus mathematical modality.** M2D-E is now described as
   amplification and operational resolution of an already strict secondary
   maximum. Only M2D-F and the finite CTMC carry fold claims.
4. **Regularity logic.** Joint local `C^3` convergence of the density is stated
   as one sufficient condition; the more minimal requirement is `C^1`
   convergence of `H=(f_t,f_tt)`. They are no longer called equivalent.
5. **Visible figure/data mismatch.** The catalytic-coordinate figure title is
   now derived from the JSON classification. The coarse `9x5` panel reads
   `midpoint: shoulder; weighted: shoulder`; a regression test protects this
   text. The 2D capacity panel now says `target-area law`, not `point sink`.
6. **Formal verification entry point.** A bare `lake build` now defaults to the
   legacy root and all three Encounter modules, while the legacy
   `FormalLean.lean` public-root boundary remains unchanged. The publication
   integrity gate checks this target list fail-closed.
7. **Central Lean coverage.** Six new sorry-free theorems in a general real
   inner-product design space establish budget-projection tangency, feasible
   response preservation, the Cauchy--Schwarz upper bound, feasibility and
   unit norm of the normalized direction, and attainment of the bound. With
   the `M`-inner product and Riesz vectors `M^{-1}c`, `M^{-1}g`, these are the
   manuscript's weighted projection and optimal infinitesimal direction.
8. **Matrix-function attribution.** The Fréchet derivative of the matrix
   exponential now cites Al-Mohy and Higham, DOI
   [10.1137/080716426](https://doi.org/10.1137/080716426).

## Major scientific limitations intentionally left open

- The three M2D-F critical controls are nonmonotone, span approximately
  `0.262`, and move substantially under a second budget measure. Their cell
  Péclet numbers are not in a controlled refinement regime. These are finite
  graph certificates, not a converged two-dimensional Doi fold.
- The 3% resolved-mode rule has no experiment-specific detector or noise
  model. Strict extrema and classifier-resolved modes must remain separate.
- The production spectral sign counts greatly exceed the necessary minima and
  are a falsification gate, not a mode-count predictor.
- Channel labels such as closing, trip, and return remain interpretations
  consistent with flux and scaling evidence, not a pathwise decomposition.
- The main article is long and broad. Capacity, coordinate sensitivity,
  multi-channel GIG screening, and some adverse controls are candidates for a
  Supplement if editorial focus remains a concern.
- Lean does not verify the generalized-Descartes theorem, matrix-exponential
  derivative, floating-point roots, PDE regularity, grid convergence, or a
  continuum limit. The theorem count must never be used as a proxy for those
  obligations.

## Highest-value next scientific additions

1. At a preregistered M2D-F baseline, compute the projected direction `h_*`
   before scanning; test held-out finite amplitudes against random feasible and
   near-to-far directions.
2. Continue a fold curve in two physical controls rather than presenting one
   tuned path.
3. Replace the current upwind node scheme with a cell-centred FV/FEM sequence
   satisfying `Pe_h<1`, resolve each patch by multiple cells, and hold a single
   physical budget and initial law fixed across odd and even grids.
4. Add an independent Robin/radiation or Brownian validation.

## Release boundary

Do not label the package submission-ready until the authors approve names,
order, affiliations, ORCIDs, funding, conflicts, CRediT contributions, public
data/code DOI and license, and the PRE data form. Then execute the documented
clean source tag -> full release -> artifact tag -> verify release -> final
proof-check chain. A passing dirty development run is scientific evidence, not
a release proof.
