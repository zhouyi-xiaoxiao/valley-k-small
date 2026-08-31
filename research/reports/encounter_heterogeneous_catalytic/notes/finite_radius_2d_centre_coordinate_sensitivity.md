# Finite-radius 2D centre-coordinate sensitivity

## Claim boundary

This is a deterministic **finite-grid sensitivity audit**. It compares two
different catalyst coordinates while fixing the domain, transport, starts,
contact radius, catalyst locations, radii, and intrinsic rates:

\[
C_\eta=\eta X_1+(1-\eta)X_2.
\]

- The declared physical catalyst coordinate is the midpoint,
  `eta=0.5`.
- The diagnostic comparator is the scalar-diffusion noise-decoupling
  coordinate, `eta=D2/(D1+D2)=0.242424...`.

These coordinates are **not equivalent** when `D1 != D2`. Agreement of a
classifier on one grid does not establish equivalence, and disagreement on a
coarse grid does not by itself establish a continuum modality difference.

## Principal matched endpoint family

The audited family has `D1=0.0025`, `D2=0.0008`, longitudinal drifts `0.18`
and `0.02`, starts `(0.10,0.50)` and `(0.35,0.50)`, contact radius `0.13`, and
near/far patches `(centre, radius, rate)` equal to
`((0.25,0.50),0.18,0.50)` and `((0.72,0.50),0.20,15.0)`.

Only `eta` changes in the patterned model. Because that change alters which
coarse product states belong to a catalyst, it also changes the raw state-sum
killing budget. The homogeneous control is therefore re-matched separately
within every `(grid, eta)` pair. This preserves the endpoint control question
inside each coordinate convention; it does not rescale the patterned models
to force the two conventions to agree.

The canonical multiscale classifier gives:

| grid | midpoint patterned | weighted patterned | interpretation |
|---|---|---|---|
| `9x5` | shoulder | shoulder | same label, different mask and density |
| `11x7` | bimodal | bimodal | same label, different mask and density |
| `13x9` | bimodal | bimodal | same label, different mask and density |

All six separately matched homogeneous controls are resolved-unimodal under
the declared canonical classifier. Direct finite-matrix semigroup derivative
evaluations retain their
small strict secondary maxima below the resolution threshold. The result is
therefore a direct warning against treating coordinate conventions as
interchangeable even though the three tested endpoint labels agree. The
coarsest comparison is a shoulder under both conventions, while the two finer
comparisons retain bimodality. The mask and quantitative density differences
do not by themselves establish that either difference persists in a continuum
limit.

## Discrete mask mismatch

The Jaccard distance below is `|M_midpoint triangle M_weighted| / |union|`:

| grid | near | far |
|---|---:|---:|
| `9x5` | `0.22222` (`7` versus `9` states) | `0.10000` (`9` versus `10`) |
| `11x7` | `0.10000` (`18` versus `20`) | `0.07692` (`24` versus `26`) |
| `13x9` | `0.22951` (`55` versus `53`) | `0.14925` (`63` versus `61`) |

The nonmonotone differences are another reason not to infer continuum
equivalence from three coarse node grids.

Tail-survival diagnostics are serialized to 12 significant digits. This is
well beyond the thresholds used here and removes irrelevant last-bit drift in
the sparse-exponential tail check; all stored density arrays retain full binary
precision.

## Supplemental three-patch check

A separate `13x9` three-patch family was cheap enough to compare. Both
coordinates remain classifier-trimodal (three modes), but the near, middle,
and far mask Jaccard distances are respectively `0.55556`, `0.33333`, and
`0.50000`. This is a sensitivity diagnostic only. It is not pooled with the
principal matched family and is not a bounded-domain trimodality theorem.

## Reproduction and artifacts

- generator: `code/validate_2d_centre_coordinate.py`;
- structured results: `artifacts/data/finite_radius_2d_centre_coordinate.json`;
- endpoint table: `artifacts/data/finite_radius_2d_centre_coordinate_endpoints.csv`;
- mask table: `artifacts/data/finite_radius_2d_centre_coordinate_masks.csv`;
- series: `artifacts/data/finite_radius_2d_centre_coordinate_series.npz`;
- figure: `artifacts/figures/finite_radius_2d_centre_coordinate_sensitivity.pdf`;
- provenance: `artifacts/data/finite_radius_2d_centre_coordinate.manifest.json`.

The validator is part of the Round 01 model-convention remediation. Its
claim-safe summary and figure are wired into the manuscript, and the generator
and artifact tests are included in the publication workflow.
