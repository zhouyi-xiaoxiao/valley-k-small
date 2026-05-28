# 2D Two-Target Local-Bias Basin Experiment Plan

Purpose: test whether a plain 2D reflecting rectangle, without corridor
geometry, can produce a smoother near/far double-peak first-passage
distribution by adding a local bias basin around the near target.

## Configuration

- Domain: reflecting rectangle, no corridor walls.
- Start: `(3, 6)`.
- Far target: `(19, 6)`, aligned with the global east bias.
- Near targets scanned: `(5, 9)`, `(7, 9)`, `(5, 3)`, `(7, 3)`.
- Absorption: process stops immediately when either target is reached.
- Global transport: east bias moves walkers toward the far target.
- Local near-target basin:
  - radius `R_b` around the near target;
  - weak inward local bias points toward the near target;
  - local holding/slowing increases residence inside the basin.

## Small Scan

The exploratory scan in
`research/reports/final_multitimescale_fpt_encounter/code/scan_grid2d_local_bias_basin.py`
uses:

- `R_b in {2.5, 3.5, 4.5}`;
- global east bias `g in {0.08, 0.12, 0.16, 0.20}`;
- local inward bias `ell in {0.00, 0.04, 0.08, 0.12}`;
- local hold `h in {0.00, 0.25, 0.45}`.

For each case, the exact raw discrete-time PMF is classified with the existing
peak classifier. Display plots use 4-step binned probability mass only for
readability.

## Preliminary Outcome

The scan found 210 raw classifier-confirmed `double_peak` cases out of 576.
Among cases with actual local inward bias (`ell > 0`), it found 126
`double_peak` cases.

The most useful local-bias examples are not produced by strong local attraction.
They use weak local inward bias plus moderate local holding. A representative
case is:

- near target `(5, 3)` or `(5, 9)`;
- `R_b = 2.5`;
- global east bias `g = 0.16`;
- local inward bias `ell = 0.04`;
- local hold `h = 0.25`.

In that case:

- raw classifier: `double_peak`;
- near-channel mass: about `0.190`;
- far-channel mass: about `0.471`;
- raw peak times: `t1 = 11`, `tv = 45`, `t2 = 74`;
- `R_peak` about `0.36`;
- `R_valley` about `0.32`;
- late peak is far-channel dominated.

## Interpretation

Local inward bias alone tends to make near-target absorption earlier and can
sharpen the first peak. The smoother mechanism needs a local basin, not just
a local arrow:

1. Global east bias keeps a delayed far-target channel alive.
2. Weak local inward bias gives the near target a capture basin.
3. Local holding/slowing broadens residence in the basin, so the near-channel
   contribution is less like a one-step spike.
4. The total curve becomes a near-dominated early peak plus a far-dominated
   broad late bump.

The current best wording is therefore not "local bias creates double peaks" by
itself. A safer claim is:

> In a plain 2D reflecting rectangle, smoother two-target double-peak-like
> curves can be designed by combining global transport toward the far target
> with a weak local near-target capture basin and moderate local residence.

## Next Scan

The next scan should refine the local-bias-positive region:

- near target: fix `(5, 9)` and `(5, 3)` first;
- `R_b`: scan `2.0` to `3.5`;
- global bias: scan `0.12` to `0.20`;
- local inward bias: scan `0.02` to `0.08`;
- local hold: scan `0.15` to `0.35`;
- record both raw classifier label and visual binned-shape diagnostics.

Do not claim a full 2D phase diagram until this refined scan is complete.
