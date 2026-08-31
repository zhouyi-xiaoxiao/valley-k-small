# Round 11 reviewer A — mathematical generality and counterexamples

Date: 2026-07-13

## Falsification target

I inspected the fold/cusp sections of
`manuscript/encounter_modality_jcp.tex`, Sections 7--9 of
`notes/continuum_multid_theory.md`, and the finite killed-generator formulas.
I tried to falsify the proposed general claims by weakening regularity,
removing budget transversality, and collapsing the killing support.

## Findings

1. **B1 — density C2 convergence is insufficient for fold persistence.**
   The old large-separation discussion correctly used C2 convergence to
   preserve already simple extrema, but that order cannot preserve uniqueness
   and nondegeneracy of a fold.  For
   `f=theta*t+t^3/3` and `f_n=f+2*n^-3*sin(n*t)`, `f_n -> f` in C2, while the
   nearby double stationary point of every approximant has zero third time
   derivative.  The fold bridge must require joint C3 convergence, or C1
   convergence of `H=(f_t,f_tt)`.
2. **B1 — killing/channel rank is not a mode-count bound.** Two 12-stage
   Erlang branches of rates 12 and 1.2, initialized with equal weights and
   feeding a single state killed at rate 100, give a max/min/max density.  Thus
   rank-one killing can be bimodal.  Any statement that `m` patches or support
   rank `m` bounds the number of modes is false.
3. **B1 — budget projection is part of the theorem, not an implementation
   detail.** A physical fold direction exists at fixed budget exactly when
   the `f_t` killing gradient does not vanish on the budget tangent space.
   For a two-control cusp, the projected `f_t` and `f_tt` gradients must have
   rank two.  Unconstrained rank is insufficient.
4. **B2 — the existing fold/cusp algebra is correct under its explicit
   nondegeneracy hypotheses.** The determinant
   `det D_(t,theta)(f_t,f_tt)=-f_ttheta*f_ttt` is correct.  The fold is standard
   singularity theory and cannot by itself supply novelty.
5. **B2 — the Duhamel derivative must include the observable derivative.**
   When the varied killing field is also the measured reaction flux,
   differentiating only the semigroup omits the direct `e^(Tt) h` term.

## Required remediation

- State joint C3 fold persistence and the C2 counterexample.
- Add the full Fréchet--Duhamel derivative and budget-projected optimizer.
- Include the rank-one bimodal counterexample and forbid patch-count mode
  bounds.
- Keep cusp and continuum conclusions conditional on projected rank and
  model-specific convergence.

No error was found in the existing finite-matrix fold roots or normal-form
exponents.
