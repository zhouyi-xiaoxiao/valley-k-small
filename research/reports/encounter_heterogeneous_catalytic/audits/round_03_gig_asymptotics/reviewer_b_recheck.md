# Round 03 reviewer B recheck — revised GIG snapshot

Date: 2026-07-11  
Overall verdict: **PASS — all B2-01 through B2-04 revisions close**  
Audited Git base: `3531353a515160b09899199a9257e7455a654b22`

I rechecked B2-01 through B2-04 independently against the revised code, saved
artifacts, child manifests, aggregate publication manifest, executed notebook,
TeX source, and rendered PDF. I did not read or rely on Reviewer A's recheck.
No scientific source, test, artifact, notebook, manifest, or manuscript was
modified; this report is my only write.

## Frozen recheck snapshot

- `code/validate_gig_fold.py`:
  `3fcb7240c2f113589017d8bd2251c5d1dd8889980ce562bba75da2dc68084292`;
- `code/validate_multid_gig_design.py`:
  `be7a750ad6eb66745ebc8591096d8bbee2571a9e2b4221571c68620a77355aad`;
- `notes/gig_fold_derivation.md`:
  `76b4bd28531950f014340f81cf18c65c166576b8c322cef87d1cb1b76e75048b`;
- `notes/multid_gig_channel_design.md`:
  `986ff7d7d46a4040f97cf2d808a18f66252fc8c58d861cd3d4a6ef77088a9501`;
- `manuscript/encounter_modality_jcp.tex`:
  `60ac24a5ed2b277049ad9361c44b9db944d14f8f825fbcedea2bc99bf1e62091`;
- rendered `manuscript/encounter_modality_jcp.pdf`:
  `dffb1598296d174db09b6b86b4a6457a0c48ee86787ca6f8b8e2046090f31168`;
- `artifacts/data/gig_fold_summary.json`:
  `5802066c97a757cf651b809f166674a643046f6f5669f2677ed1e5d054e7ed1c`;
- `artifacts/data/multid_gig_design_summary.json`:
  `4cf5c5b9aea62c28a6294f0d65be8e7915d34197aa4bed7892930b3732a6e059`;
- `artifacts/data/gig_fold.manifest.json`:
  `18c0c23d69ecdf182892421ba1d77fe942c085708c990237daf3e9694969c216`;
- `artifacts/data/multid_gig_design.manifest.json`:
  `303285b44684f4bba3786ee0d179366a8fbd0d20a88c7cbaeb778d908baa2c72`;
- `artifacts/data/publication_pipeline.manifest.json`:
  `20d30585c086a123252bb75eb59d6c6d442257e12f48f3e3c5afcc5e0eeec1d9`;
- `notebooks/encounter_publication_validation.ipynb`:
  `c9662563c4862705041a22b38e43e1617c8afd8c2cdfa4b1e7961922a6d3cabd`.

The repository remains broadly dirty and the report tree is untracked relative
to the Git base, so the hashes above, rather than `HEAD` alone, define this
recheck.

## Finding-by-finding disposition

### B2-01 — stable mode, log normalizer, and log-sum-exp stress: PASS

**Revised implementation**

- `validate_gig_fold.py:44-66` evaluates the log-scaled Bessel function with
  `kve` below `x=1e5` and a four-term DLMF 10.40.2 large-argument expansion
  above that threshold.
- `validate_gig_fold.py:87-130` now evaluates `log Z`, has an exact `B=0`
  branch, fails closed outside the certified branches, and evaluates the
  rationalized mode
  `2A/(nu+sqrt(nu^2+4AB))`.
- `validate_gig_fold.py:132-153` forms the density from `log_density` rather
  than dividing two underflowed quantities.
- `validate_multid_gig_design.py:54-127` uses the same explicit small,
  intermediate, and large Bessel branches, stable log normalization, and
  fail-closed behavior; `130-162` uses log-sum-exp inverse-height weights.
- `validate_multid_gig_design.py:179-252` evaluates the mixture score `f'/f`
  and curvature ratio from posterior component fractions. Root isolation no
  longer depends on an underflowed raw derivative.
- Regression coverage appears at
  `tests/test_encounter_gig_fold.py:57-84` and
  `tests/test_encounter_multid_gig_design.py:68-99`.

**Independent checks**

| case | revised result | assessment |
|---|---:|---|
| `A=1, B=1e-16, nu=3.5` mode | `0.2857142857142857` | equals stable limit |
| `A=1, B=1e-300, nu=3.5` log Z | `0.28468287047291918` | agrees with `B=0` to binary64 precision |
| `A=1e8, B=.01, nu=3.5` log Z | `-2031.662326733992` | finite beyond raw-`kv` underflow |
| same case, density at mode | `1.7869146578e-4` | positive, finite, negative curvature |
| multid modes `(1,1e3,1e6)` | log weights all finite; sum `0.9999999999999996` | log-sum-exp stress passes |
| `A=1e20, B=.01, nu=3.5`, `x=2e9` log Z | `-2000000073.110358` | equals the exact half-integer large-`x` formula |
| `A=1e12, B=1e6, nu=1.5`, `x=2e9` | finite positive mode density | exact `K_{1/2}` regression passes |

The updated saved GIG parameters also include `log_normalization`, and both
child manifests hash the revised generators and regenerated outputs. No current
artifact uses the unstable legacy path.

I also checked the branch boundary at `x=99999`, `100000`, and `100001` for
`K_{5/2}`. Scalar and vectorized implementations agreed with the exact
`sqrt(pi/(2x))*exp(-x)*(1+3/x+3/x^2)` expression to displayed binary64
precision at all three points and at `x=2e9`. The earlier large-`x` residual is
therefore closed rather than merely excluded from the paper's parameter range.

### B2-02 — catalyst-distance feasibility: PASS

- The general condition and reference threshold are now stated at
  `manuscript/encounter_modality_jcp.tex:1338-1343` and render correctly in the
  PDF.
- `notes/multid_gig_channel_design.md:76-93` separates an algebraically valid
  clock from a real catalyst location and lists the four thresholds.
- `validate_multid_gig_design.py:130-162` rejects nonpositive modes and raises
  before taking a square root when `B*m^2+p*m < 1/4`.
- The summary and child manifest both record `distance_feasibility` and the
  dimension-specific minimum modes.
- `tests/test_encounter_multid_gig_design.py:55-65` checks points immediately
  above and below the boundary for all four dimensions.

My tighter `1 +/- 1e-10` boundary probe also passed. The below-threshold cases
raised the promised `ValueError`; above-threshold distances were about `5e-6`.
Every archived target remains well inside the domain (`m>=1`).

### B2-03 — root-count wording and evidence boundary: PASS

- The manuscript now says the finite scan **found** the `2m-1` alternating
  simple critical points and explicitly says that an interval-certified
  exclusion of additional tangential roots is not claimed
  (`manuscript:1345-1351`).
- The summary key is now
  `all_cases_have_one_detected_mode_per_channel`, and its `not_claimed` list
  retains the tangential-root exclusion
  (`multid_gig_design_summary.json:2,154-159`).
- The child manifest declares a 240,000-point sign scan rather than an interval
  proof (`multid_gig_design.manifest.json:2-7,20-24`).
- The notebook consumes the new `detected` key and keeps the result inside its
  free-space narrow-patch screening boundary.

An independent 300,000-point log-domain reconstruction returned root counts

```text
[3,5,7, 3,5,7, 3,5,7, 3,5,7]
```

The maximum difference from the regenerated root CSV was `8.53e-13`; the
relative spread of the equalized weighted isolated heights was `9.12e-16`.
Therefore every claimed detected simple root is reproduced, while the
non-certified possibility is now stated rather than silently excluded.

The direct design note now uses the same wording: “the finite scan found the
expected sign-changing simple roots” and immediately retains the
interval-arithmetic limitation (`notes/multid_gig_channel_design.md:155-167`).
The earlier editorial mismatch is closed. The notebook could additionally
assert the tangential-root `not_claimed` item, but it does not make an exhaustive
root-count claim and this is not a remaining correctness issue.

### B2-04 — continuous CTMC channel modes: PASS

- `validate_gig_fold.py:366-484` evaluates
  `alpha exp(Tt) T^n b_channel`, brackets derivative crossings, refines them
  with Brent, requires negative curvature, and selects the largest channel
  maximum.
- `gig_fold_summary.json:2-40` stores root brackets, derivative residuals,
  curvatures, method, and the revised relative errors.
- Regression coverage is at `tests/test_encounter_gig_fold.py:87-107`.
- The TeX and rendered PDF both report `32.1534`, `196.1459`, `17.6%`, and
  `8.1%`, explicitly distinguishing derivative roots from sampled maxima
  (`manuscript:831-840`).

Independent horizon/grid sweeps gave the same maxima:

| channel | rooted time | root count | dimensionless curvature |
|---|---:|---:|---:|
| near | `32.1534061543059` | 1 | `-3.7445163` |
| far | `196.14587000697` | 1 | `-6.8415940` |

Results were stable for horizons `300`, `500`, and `1000` and scan spacings
from `1` down to `0.25`. Recomputing the errors directly from the saved modes
gave exactly `0.17592020350762813` and `0.08134795289020483`.

## Artifact, manifest, notebook, and manuscript synchronization

**PASS.** I recomputed every declared SHA-256 rather than trusting timestamps:

- `gig_fold.manifest.json`: `2/2` source hashes and `9/9` output hashes match;
- `multid_gig_design.manifest.json`: `4/4` source hashes and `6/6` output hashes
  match;
- `publication_pipeline.manifest.json`: all `64/64` source hashes and `97/97`
  output hashes match, including both child manifests, both GIG summaries, the
  tests, notebook, TeX, rendered PDF, and figures.

The saved notebook's inventory hashes for `gig_fold_summary.json`
(`5802066c97a757cf...`) and `multid_gig_design_summary.json`
(`4cf5c5b9aea62c28...`) match the current files. I then executed the notebook
top-to-bottom **in memory**, without rewriting it: all 18 code cells ran in
order, there were no error outputs, and the final
`VALIDATION_SUMMARY_JSON` retained `all_claims_pass=true`.

The PDF text independently contains the revised continuous CTMC modes, errors,
distance feasibility threshold, and tangential-root caveat. It is therefore not
a stale render of the TeX.

The multid child manifest now directly hashes
`notes/multid_gig_channel_design.md` in addition to the generator,
`vkcore/provenance.py`, and `notes/continuum_multid_theory.md`. The earlier child
provenance gap is closed.

## Executed tests

The final frozen snapshot completed:

```text
PYTHONDONTWRITEBYTECODE=1 uv run --no-sync pytest -q \
  -p no:cacheprovider \
  tests/test_encounter_gig_fold.py \
  tests/test_encounter_multid_gig_design.py

............ [100%]
12 passed
```

Additional independent checks covered high-precision Bessel normalization,
small-`B` continuity, large-action stress, feasibility on both sides of the
boundary, 12-case root reconstruction, continuous CTMC mode roots under five
horizon/resolution choices, all manifest hashes, PDF text, and an in-memory
notebook execution.

## Final disposition

All four original B2 paper-facing issues are closed. The GIG algebra, declared
small/intermediate/large numerical branches, catalyst feasibility,
detected-root claim boundary, continuous
CTMC comparison, saved artifacts, notebook, manifests, TeX, and PDF are mutually
consistent. Round 03 may close.

No unresolved issue from B2-01 through B2-04 remains on this frozen snapshot.
The already declared scientific limitations—no interval proof against
tangential roots, no finite-patch mode-window remainder, no physical realization
of abstract mixture weights, and no bounded continuum multimodality theorem—are
scope boundaries, not failed revisions.
