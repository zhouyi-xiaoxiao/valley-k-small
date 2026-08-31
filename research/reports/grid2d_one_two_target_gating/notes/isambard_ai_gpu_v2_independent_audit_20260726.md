# Isambard-AI fixed-mean GPU v2 independent audit

Date: 2026-07-26

## Verdict

The `5780429` main array is a complete and internally consistent GH200
cross-backend data set for one finite-horizon endpoint contrast. It is valid
raw evidence, but it is not by itself a manuscript-grade campaign and must not
be described as an asymptotic splitting-probability result.

## Frozen inventory

- Main array: `5780429`, tasks `0..31`, all `COMPLETED 0:0`.
- Exact task coverage: 32 files, one file per array task, no duplicate task,
  no extra task, and no scientific-key conflict.
- Inventory digest: `50c7ff47e955b05bf57aca83530429dec8119c0ec279787edf831bcf9d9970c1`.
- Executed source SHA-256:
  `85e1b293f03669f2d1e533129d407aad34a0205380c0a84de289052d64f3b745`.
- Frozen field-pack SHA-256:
  `28d8879690a8ca307b5db03823aa39110d9734c2ec5ea68243facda9fe83cc8f`.
- Schema: `grid2d-one-two-target-gating-fixed-mean-gpu-v2`.

The main array is exactly 16 disorder blocks at amplitude `0.00` and the same
16 blocks at amplitude `0.20`. Every task uses `walk_replicate=0`, 500,000
walkers, 5,000 steps, target fraction `0.50`, target radius 3, and base hold
probability `0.30`. The separate check job `5780428_0`, interactive runs, and
v1 files are excluded from the main inventory.

## Integrity checks

All 32 tasks passed:

- executed-source and field-pack hash checks;
- task-to-amplitude/disorder mapping;
- frozen disorder seed and reconstructed field hash checks;
- fixed field mean `0.30` and valid holding-probability range;
- one-target and two-target mass balance;
- paired target-1 subset and exhaustive paired-category identities;
- probability, standard-error, and FPT-summary reconstruction;
- checkpoint mass, monotonicity, subset, and final-count equality;
- finite scalar output checks.

The JSON schema has no explicit success field. Completion is therefore bound
externally to the Slurm accounting receipt plus this invariant audit; the raw
JSON must not be said to self-certify success.

## Block-paired endpoint contrast

For amplitude `0.20 - 0.00`, paired over the 16 disorder blocks (Student-t,
15 degrees of freedom):

| Quantity at 5,000 steps | Paired mean | 95% interval |
|---|---:|---:|
| Gating drop | -0.003472125 | [-0.005559801, -0.001384449] |
| Target-2 first probability | -0.007756875 | [-0.013797335, -0.001716415] |

The unresolved probabilities remain large: approximately `0.730--0.750` in
the one-target system and `0.332--0.371` in the two-target system. The safe
interpretation is therefore a finite-horizon, aligned-geometry endpoint
effect. It does not distinguish delayed absorption from a change in eventual
splitting probability.

## Required continuation

The preregistered v3 campaign must prioritize longer horizons, a second
independent walk stream, the full geometry surface, amplitude dose response,
and additional independent disorder blocks. A strict reducer must freeze the
expected inventory and compute uncertainty over disorder blocks, after
averaging walk streams within each block.
