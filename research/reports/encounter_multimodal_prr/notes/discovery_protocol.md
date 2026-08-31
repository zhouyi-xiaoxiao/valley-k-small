# Frozen G1b discovery protocol

Date frozen: 2026-07-13, before any (65\times65\times49) control-line result
was generated.

## Scope

This is a topology-discovery calculation, not continuum verification.  Its
only purpose is to decide whether the predeclared physical-budget line contains
a credible interior fold bracket worth taking into the odd/even convergence
campaign.  No result from this mesh may be labelled a continuum fold.

The earlier (25^3) eleven-control calculation is recorded as an engineering
scan: it found one sampled maximum throughout the line.  It neither changes the
protocol below nor counts as a project-gate failure.

## Frozen calculation

- physical dimension: (d=2);
- quotient mesh: ((N_z,N_{r_\parallel},N_{r_\perp})=(65,65,49)), hence
  207,025 cell-mass states;
- all physical parameters, box bounds, initial law, three slab profiles, and
  full installed budget: exactly those in `notes/continuum_g1_design.md`;
- control line:
  (w(\theta)=(1-\theta)(0.70,0.25,0.05)
  +\theta(0.05,0.25,0.70));
- controls: \(\theta=0,0.1,\ldots,1\);
- discovery window: (t\in[0,80]) with spacing (0.25);
- semigroup output is processed in chunks of at most 41 time points so the
  full state history is never retained;
- observables use generator actions, not finite-difference derivatives:
  (f=p^Tk), (f_t=p^TAk), (f_{tt}=p^TA^2k), and
  (f_{ttt}=p^TA^3k).

## Candidate logic

At each control, analysis begins at (t=0.5) and requires
(f(t)>10^{-12}\max_s f(s)).  This result-blind floor excludes the exact-zero
initial plateau from topology logic without changing the stored curves.  Each
maximal run of exact sampled zeros is collapsed to one bracket before applying
the time/density filter.  A bracket is eligible only when its left endpoint is
at or beyond the analysis start; an exact-zero run that starts in the
preanalysis interval cannot be moved into scope by using its midpoint.  Every
remaining sampled sign bracket of (f_t) is
retained.  Every remaining sampled sign bracket of (f_{tt}) is linearly
interpolated to estimate an extremum of (f_t).  A fold candidate is flagged if
either:

1. the dimensionless extremum height (|t f_t/f|) is below (0.05); or
2. a time-matched extremum branch changes the sign of (f_t) between adjacent
   controls.

These are deliberately permissive discovery flags.  They are not fold
residuals, an implicit-function certificate, or a substitute for the complete
fold jet.  Any bracket selected for confirmation must be frozen in a new
manifest before a finer-grid result is inspected.

An endpoint-only near-zero flag is diagnostic and does not authorize freezing
a confirmation bracket.  For matched adjacent controls, a strict opposite-sign
pair gives an interior bracket.  An exact sampled zero gives interior evidence
only when its own control satisfies \(0<\theta<1\); an exact zero only at
\(\theta=0\) or \(1\) remains endpoint diagnostic evidence.  The `freeze
candidate` action requires an interior discovery flag.  All sampled curves and
all brackets excluded by the declared time/density rules remain
machine-readable.

Adjacent-control extrema are matched without branch crossing: first maximize
the number of order-preserving, same-kind matches within the time tolerance,
then minimize their total time separation.  Multiple optimal assignments,
unmatched retained extrema, a retained (f_t)-root count or ordered-topology
change, or a change in excluded-bracket/extremum reason signatures blocks both
the `line empty` and `freeze candidate` actions and requires manual review.
These transition diagnostics are not fold evidence by themselves.

## Result-blind pre-run amendment

Before any formal (65\times65\times49) discovery result was generated, a
small dry-run exposed that (f(0)) and its generator-action jets can be exactly
zero for the contact-safe initial law.  The original inclusive sign-bracket
wording would therefore count adjacent pairs in a zero plateau as multiple
roots.  The manifest was amended, still result-blind, to add:

- `minimum_analysis_time = 0.5`;
- `relative_density_floor = 1e-12`; and
- one-bracket collapsing of every maximal exact-zero run.

A subsequent pre-run adversarial audit found that treating a matched exact
zero at \(\theta=0\) or \(1\) as an ordinary inclusive sign bracket could
incorrectly authorize an interior followup.  Before the formal run, the action
rule was therefore made explicit: strict opposite signs bracket an open-control
root, while a sampled exact zero is interior only at a sampled interior
control.  Dedicated tests cover exact zeros at \(\theta=0,0.1,0.9,1\).

The same pre-run audit pinned the required G1a foundation certificate before
any model assembly:

- artifact: `artifacts/data/continuum_g1_smoke.json`;
- schema/stage/status: `3` / `G1a_pre_fold_foundations` / `PASS`;
- claim state: `continuum_verified=false`;
- gates: `42/42` true; and
- SHA-256:
  `a0a1894dbe6dd37bad6973ca6f3dd29b651441f7b911a5406186bb86a18fd3c3`.

The producing model assembler is also pinned:

- code: `code/continuum_g1_smoke.py`;
- SHA-256:
  `e0322b212e466b1b640f5adcf30d67d119d2f6fe4cc622eb532082b6cd251701`.

Before assembly, the certificate's canonical `physical_parameters` and
`control_endpoints` must equal the current `PilotParameters`, `LOWER_WEIGHTS`,
and `UPPER_WEIGHTS` exactly, including JSON numeric types.  The canonical model
contract and its SHA-256 are recorded in discovery provenance.

The runner rejects a missing, relocated, altered, mistyped, failed-gate, or
hash-mismatched certificate before creating or resuming any control.  The
manifest pins this separate artifact, not its own hash; the manifest hash is
computed and recorded at run time.

The Round 11 pre-run adversarial replay also hardened the following fail-open
paths before any formal control was assembled:

- manifest comparison is recursively type-strict, so Boolean, integer, and
  floating-point values cannot pass by Python numeric equality;
- any zero run or opposite-sign bracket beginning before `t=0.5` is excluded
  with a machine-readable reason;
- matched branches use the order-preserving rule above, with unmatched,
  ambiguity, retained-root topology, and filter-boundary transitions retained;
- every checkpoint is atomically bound into
  `integrity_ledger.json`; orphan, missing, metadata-mismatched, or
  hash-mismatched files are rejected before checkpoint JSON is trusted; and
- resume freshly assembles the model, recomputes all foundation diagnostics,
  requires exact parameters/grid/weights/gate names and Boolean values, and
  checks curve, chunk, runtime, nonnegativity, survival, initial-mass, and
  generator-action bounds before reusing a checkpoint.

Exactly one process may write a checkpoint directory.  A non-blocking
exclusive `flock` on `.run.lock` is held for the complete run, so a second
writer fails before any checkpoint or temporary file is created.  The formal
repository-`.venv` guard runs before lock-directory creation.  After release,
`.run.lock` may remain with `status=RELEASED`, PID, start/finish times, run mode,
and configuration hash; it is operational diagnostic metadata, not a
scientific artifact or checkpoint-ledger entry.

These pre-run amendments change only analysis/action hygiene and prerequisite
validation.  The formal mesh, physical parameters, control line, time window,
spacing, chunk size, candidate height, and adjacent-control matching tolerance
remain unchanged.

## Fail-closed actions

- If the line yields a credible interior bracket, freeze only that bracket and
  implement the augmented control sensitivity before root continuation.
- Only if it yields no bracket *and* every adjacent transition has stable
  retained-root counts/topology, complete unambiguous extremum matching, and
  stable filter signatures may the one allowed simplex scan use spacing
  (0.1) and select one interior segment.  No physical parameter, patch,
  initial law, box, budget, or gate may be retuned.
- If that bounded simplex scan also has no topology boundary, this frozen
  family records `PROJECT GATE FAILED`; the earlier finite-model result remains
  intact, but this family cannot support the PRR continuum headline.

The root/tail audit to (t=200), odd/even convergence, enlarged-box test,
independent method, and observability floors belong to confirmation, not this
discovery decision.
