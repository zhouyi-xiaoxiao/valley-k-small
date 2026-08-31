# Round 22: independent G1c formal-result audit

Date: 2026-07-13  
Auditor role: independent result/integrity adversary  
Overall assessment: **PASS for the narrow G1c discovery claim; HOLD for fold confirmation, continuum verification, and the project gate**

## Scope and immutable inputs

This audit did not modify the frozen runner, manifest, protocol, formal result,
integrity ledger, or any of the 66 formal checkpoints.  The audited identities
were:

| Item | SHA-256 |
|---|---|
| `continuum_g1c_simplex_manifest.json` | `543ee21928cf009867bd194d3bb2f6929a3557458733c50ff613c2f664f1d593` |
| `continuum_g1c_simplex.py` | `0625212963c85d2068fa209924bfa7086f7b192edbbbbde6ffc6f9109cfb63a5` |
| `g1c_simplex_protocol.md` | `af337ba273a1b12be4317c7f6e40caf219855f240f56fa9411cfa1edde9e2f99` |
| `continuum_g1c_simplex_result.json` | `cce1e34c599564dc932da6af4d4146c2c396836990e9b51414fc2f843e123bb4` |
| formal checkpoint integrity ledger | `acc321adba8af8fd3b4655fbcdb0aa6232ff455ee47abe57f0c7d964c3a306de` |

The manifest's G1a, G1b, and post-result-review artifact and producer hashes
were also recomputed from disk and agree with both the manifest and the formal
result provenance.

## Independent audit method

The principal result check did not call the production `analyze_simplex`
routine or its dynamic-programming matcher.

1. All checkpoint filenames, ledger entries, SHA-256 values, exact schema
   keys, control indices, integer triplets, weights, configuration hash,
   provenance, grid, and claim flags were reconstructed from the denominator-10
   simplex definition.
2. The sampled `f`, `f_t`, and `f_tt` curves were read directly from each
   checkpoint.  Exact-zero runs, sign brackets, linear roots, retained/excluded
   extrema, topology signatures, and the near-zero screen were reimplemented
   independently.
3. Every order-preserving same-kind matching was exhaustively enumerated on
   each edge.  The independent selector maximized cardinality and then
   minimized total time separation, rather than using the production dynamic
   program.
4. Crossing weights, boundary status, manual-review reasons, and all three
   gate states were rebuilt from those independent matches.
5. A copy of the formal checkpoints and ledger was resumed in a temporary
   namespace.  The runner restored 66 controls and computed zero controls.  Its
   normalized result was exactly equal to the formal result after removing
   invocation timestamps/runtime totals and normalizing only
   `resumed_this_invocation`.  The temporary result SHA-256 was
   `8a0429b9916fb366ec579d1c166893cc77c24cf128481cc11c59d74880d59c3a`.
6. The 22 focused tests in `test_continuum_g1c_simplex.py` passed.

The largest absolute discrepancy between the independently reconstructed
floating-point rows and the stored rows was
`3.9968028886505635e-15` (a summed time-separation field).  This is roundoff,
not a classification difference.

## Integrity and enumeration findings

- Exactly 66 unique controls are present in the frozen increasing-`(i,j)`
  enumeration; no orphan, missing, duplicate, temporary, or unledgered
  checkpoint was found.
- All 66 ledger hashes agree with the checkpoint bytes.  Each result-embedded
  control is exactly equal to its checkpoint, and each result checkpoint row
  agrees with the filename, hash, triplet, weight, and runtime in that file.
- Every curve has the six required fields and 321 finite samples at
  `t=0,0.25,...,80`.  Survival is nonincreasing to numerical tolerance.  A
  coarse trapezoidal `S(0)-S(t)` versus integral-of-`f` reasonableness check has
  maximum absolute residual `1.5529295546590736e-4`, consistent with the
  declared time spacing and not used as a root certificate.
- Independent L1-distance-two construction gives exactly 165 undirected
  triangular-lattice edges.

## Candidate and topology reconstruction

The independent reconstruction exactly reproduces:

| Quantity | Recomputed value |
|---|---:|
| matched extrema across all edges | 328 |
| controls with 1 / 3 retained `f_t` roots | 63 / 3 |
| controls with 2 / 4 retained `f_tt` extrema | 54 / 12 |
| interior near-zero controls | 0 |
| boundary near-zero diagnostics | 1 |
| eligible interior sign-crossing seeds | 3 |
| boundary sign-crossing diagnostics | 1 |
| unresolved whole-edge-zero matches | 0 |
| topology manual-review rows | 53 |

The three eligible seeds are:

| Edge | Linearly interpolated crossing weight | Endpoint `f_t` heights | Time separation |
|---|---|---|---:|
| `w_02_00_08`--`w_02_01_07` | `(0.2, 0.0680921304, 0.7319078696)` | `+5.7667706e-4`, `-2.7023000e-4` | `0.8617635` |
| `w_02_01_07`--`w_03_00_07` | `(0.2640122507, 0.0359877493, 0.7)` | `-2.7023000e-4`, `+1.5192357e-4` | `1.6468372` |
| `w_03_00_07`--`w_03_01_06` | `(0.3, 0.0177920886, 0.6822079114)` | `+1.5192357e-4`, `-7.0195914e-4` | `0.2124197` |

All three edges have at least one boundary endpoint, but their interpolated
crossings have three strictly positive weights.  They are therefore eligible
under the rule frozen before the run.  This does not make them three distinct
folds; they are three finite-grid seed edges and may sample one nearby fold
set.

The two correctly non-promoted boundary diagnostics are the near-zero
extremum at `w_04_00_06` and the sign crossing on the simplex face between
`w_03_00_07` and `w_04_00_06`.

All 53 manual-review rows reproduce exactly: 21 are interior--interior edges
and 32 touch the simplex boundary.  Their reason counts are 43 unmatched-left
extrema, 43 unmatched-right extrema, 8 retained-root-count changes, and 8
retained-topology-signature changes.  There are no ambiguous optimal
assignments and no whole-edge exact-zero cases.  Each of the three candidate
edges is among the eight `3 <-> 1` retained-root transitions.  That overlap is
why the result correctly requires topology review before choosing a segment;
it is not permission to promote an unmatched branch by itself.

## Three-valued action semantics

The manifest, protocol, implementation, result, and focused tests agree on the
following truth table:

| Eligible interior candidate | Topology review | Family-gate value | Required action |
|---|---|---|---|
| one or more | either | `true` | candidate-seed discovery only; review topology when flagged, then freeze at most one new confirmation segment |
| none | yes | `null` | inconclusive manual review; do not promote topology or retune inside G1c |
| none | no | `false` | fixed-family discovery failure; stop without physical retuning |

The realized branch is `3 candidates + review`, hence
`family_discovery_gate_passed=true` and
`PASS_ELIGIBLE_INTERIOR_CANDIDATE_SEED_FOUND`.  This Boolean is only the
finite-grid family-discovery gate.

## Claim-boundary audit

The result did **not** authorize a fold or a stronger claim:

- top-level, simplex-analysis, and all 66 checkpoint values have
  `continuum_verified=false` and `project_gate_passed=false`;
- `confirmation_segment_authorized=false`;
- `candidate_automatically_confirms_fold=false`;
- `candidate_automatically_selects_segment=false`;
- the formal status is `G1C_SIMPLEX_COMPLETE_CANDIDATE_SEED_ONLY`;
- the policy still requires a new frozen manifest and permits at most one
  later confirmation segment.

## Adversarial findings

- **P0: 0.** No integrity, provenance, enumeration, or claim-boundary failure.
- **P1: 0.** No material candidate, matching, boundary, manual-review, or
  three-valued-decision discrepancy.
- **P2: 0.** No audit-traceability defect requiring repair.

The 53 topology-review rows and the absent continuum/confirmation gates are
open scientific workflow gates, not defects in the G1c artifact.

## Authorization decision

**Authorized now:** enter the separately recorded manual review of the
candidate-bearing topology transitions.  After that review, a result-informed
but prospectively frozen G1d manifest may select **at most one** of the three
segments and add root residuals, control sensitivities, time/mesh convergence,
tail checks, and an independent numerical method.

**Not authorized now:** call any seed a confirmed fold, run a G1d confirmation
under the G1c manifest, select multiple segments, claim continuum verification,
or pass the PRR project gate.
