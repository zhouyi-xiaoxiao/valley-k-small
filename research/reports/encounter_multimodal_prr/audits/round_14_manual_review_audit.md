# Round 14: post-result manual-review audit

Date: 2026-07-13  
Scope: independent audit of the separately frozen, post-result
`theta=0.7` diagnostic; no code or existing evidence artifact was modified  
Verdict: **PASS, but only for the bounded fixed-discretization statement that
the flagged `theta=0.7` feature is a reproduced subzero derivative wiggle and
not a numerical fold candidate under the frozen rules.**

This verdict does not convert the formal control line to `line empty`, does
not authorize the old simplex fallback, does not pass G1b or G2, and does not
establish a continuum nonfold theorem.  A new simplex study, if pursued, must
be frozen as a new, explicitly result-informed G1c protocol.

## Severity ledger

| Severity | Open findings | Disposition |
|---|---:|---|
| P0 | 0 | no evidence substitution, false fold claim, or claim-gate escape |
| P1 | 0 | no numerical-reproduction or classification failure |
| P2 | 0 | no unresolved implementation or documentation defect found |

The failed first execution described in Section 6 is a recorded procedural
deviation, not an open finding.  It cannot elevate this calculation to
predeclared evidence; the manifest already forbids that use.

## 1. Evidence audited and byte-level pins

The current files reproduce the following SHA-256 values:

| Object | SHA-256 |
|---|---|
| immutable formal discovery result | `2052c1d26211661995d6048b2cd3ca909f04ce48efb9a96c32bd153c7c63d40d` |
| formal discovery runner | `1411384398ed4e476dba15371cdfd662e94ed3a53cffdc02a1562201cfa7b52e` |
| manual-review manifest | `2b2e311e8e8609318bd566a127e8aca895e1db5dd8de8755fcfe77e731e29213` |
| manual-review protocol note | `912f5e10f79d2bd18075c11f3bcddc6cfb1a908b4963a76297cd890a09e90c63` |
| manual-review runner | `4453444abd878d771b59185aaee5371ae5d9c786fdb0da9222f25c0605035451` |
| manual-review tests | `49f39009ee04a2364c99d1debc818ddcfcd16a560346446fb53b0775539a6cb9` |
| successful manual-review result | `6f869fb4e961297a9ba4784c394fa56fbb083f1a89091aa0c27738331127de65` |

The manifest's `trigger.formal_result_sha256` equals the current formal-result
hash.  Its `trigger.formal_runner_sha256` equals both the formal result's
recorded producer hash and the current discovery runner hash.  The successful
manual-review result records the current manifest and runner hashes exactly.

The reviewed control also agrees in all three places:

```text
theta = 0.7
manifest weights = (0.245, 0.25, 0.505)
formal-result weights = (0.24500000000000002, 0.25, 0.5049999999999999)
line-formula weights = (1-theta)*(0.7,0.25,0.05)
                     + theta*(0.05,0.25,0.7)
```

The floating-point representations agree to the runner's frozen absolute
tolerance of `1e-15`.  The diagnostic uses the same
`65 x 65 x 49 = 207025`-state model and changes only the stored time grid from
spacing `0.25` to `0.05` on `t in [0,20]`.

## 2. Common-time numerical reproduction

There are 81 exact common times, `0, 0.25, ..., 20`.  An independent extraction
from the two stored curve arrays reproduced the result's maximum absolute
errors:

| Observable | maximum absolute error | frozen limit |
|---|---:|---:|
| `f` | `5.620504062164855e-16` | `5e-11` |
| `f_t` | `1.3357370765021415e-16` | `5e-11` |
| `f_tt` | `6.250662693604164e-16` | `5e-11` |
| `f_ttt` | `5.21712766033116e-14` | `5e-11` |
| survival | `1.3600232051658168e-14` | `5e-11` |

The worst error is about 958 times smaller than the acceptance limit.  The
alignment check requires exact equality of the common stored times, so these
are not nearest-neighbour comparisons on displaced grids.

This is a reproducibility check using the same sparse generator and SciPy
semigroup implementation on a five-times-finer time grid.  It is not an
independent PDE discretization, a mesh-convergence study, or an interval-error
bound.

## 3. Independent root and extremum count

A separate sign-change enumeration of the stored dense arrays after the
frozen `minimum_analysis_time=0.5` found exactly one retained sign change of
`f_t` and four retained sign changes of `f_tt`, matching the runner analysis.
The sole `f_t` root lies in `[5.55,5.60]`:

```text
linear root time = 5.5661960201
interpolated f   = 0.0372803073
interpolated f_tt = -0.0020857491
dimensionless curvature = -1.7334031151
topology = sampled maximum of f
```

Thus the dense diagnostic retains one sampled density maximum.  It does not
create a second density maximum or an intervening minimum.

The four extrema of `f_t` are:

| kind | linear time | interpolated `f_t` | `abs(t f_t/f)` |
|---|---:|---:|---:|
| maximum | `2.505387` | `+1.5656897e-2` | `2.606997` |
| minimum | `7.819388` | `-1.5292878e-3` | `0.344385` |
| maximum | `11.103846` | `-1.3837296e-3` | `0.512429` |
| minimum | `13.928348` | `-1.4126510e-3` | `0.755802` |

The extra late maximum--minimum pair is strictly below zero.  Its closest
approach to zero is `1.3837296e-3`, which is 13.84 times the frozen absolute
negative-margin requirement `1e-4`.  Its smaller dimensionless height is
`0.512429`, 10.25 times the frozen near-zero cutoff `0.05`.  Even if all three
late extrema are considered, their smallest dimensionless height is
`0.344385`, 6.89 times the cutoff.  Consequently
`near_zero_extremum_count=0` is supported with a substantial sampled margin.

All foundation gates are true, the stored curves contain 401 finite samples,
and the chunk diagnostics confirm that no full 207,025-state history was
stored.

## 4. Adversarial and regression checks

The current regression suite passed:

```text
manual-review tests: 3 passed
discovery-runner tests: 48 passed
ruff check: PASS
ruff format --check: PASS
```

Three additional read-only mutations were exercised against the current
runner using temporary files outside the evidence directory:

| Mutation | Expected guard | Outcome |
|---|---|---|
| change one byte-level field in the formal result | frozen formal-result hash | rejected before model assembly |
| change the manifest control weights | exact frozen-line weight check | rejected before model assembly |
| remove the formal manual-review trigger and repin the tampered formal bytes in a temporary manifest | semantic trigger check | rejected before model assembly |

All three attacks failed closed.  The common-time helper's existing tamper
test also changes one formal `f_t` value and detects the resulting `1e-4`
error.

## 5. Claim-semantics audit

The successful artifact keeps every project-level claim gate closed:

```text
evidence_timing = POST_RESULT_DIAGNOSTIC_NOT_PREDECLARED_DISCOVERY_EVIDENCE
continuum_verified = false
project_gate_passed = false
original_frozen_line_empty_action_authorized = false
```

Its `PASS_NEGATIVE_DERIVATIVE_WIGGLE_NOT_FOLD_AT_REVIEWED_CONTROL` status must
therefore be read as a numerical classification at this one control, mesh,
time window, and threshold set.  It supports:

> At `theta=0.7` on the fixed `65 x 65 x 49` discretization, five-times-finer
> time sampling reproduces four extrema of `f_t`, retains exactly one maximum
> of the density, and leaves the additional derivative extrema substantially
> below `f_t=0`; the flagged feature is not a fold candidate under the frozen
> numerical rules.

It does **not** support any of the following:

- a proof that no continuum fold exists at `theta=0.7`;
- a line-empty conclusion for the original 11-control formal study;
- stable branch matching across `theta=0.6,0.7,0.8`;
- authorization of the old spacing-`0.1` simplex fallback;
- bimodality, trimodality, a cusp, continuum convergence, or a passed PRR gate.

The manual-review protocol explicitly says that passing the local tests does
not satisfy the old line protocol's stable-extremum-matching condition.  The
result's `next_action` permits only freezing a new prospective G1c protocol or
stopping this physical family.  It is not an instruction to execute or
reinterpret the old simplex action.

## 6. First failed execution and successful rerun

The run operator reports that the first long execution completed the numerical
evaluation and then raised `AttributeError` while constructing the result
dictionary from a nonexistent `model.weights` attribute.  That attempt did
not write an artifact.

The current control flow corroborates the absence of contamination:

1. `main()` creates the temporary output only after `run()` returns a complete
   result, so an exception during result construction precedes all output I/O.
2. No temporary or alternative manual-review result file is present in the
   evidence directory.
3. The repair serializes the already-loaded manifest `weights`, after checking
   them against the frozen endpoint interpolation to `1e-15`; it does not
   change the assembler, semigroup evaluation, time grid, candidate rules, or
   classification thresholds.
4. The current result was produced by a complete new execution under the
   repaired script and records that script's SHA-256.  This runner has no
   checkpoint/resume path, so the successful process could not reuse numerical
   state from the failed process.

The failure and repair therefore have no numerical or artifact-integrity
impact on the successful result.  They do matter procedurally: this diagnostic
must not be described as an untouched preregistered run.  That restriction is
already stronger than needed here because the entire manual review was frozen
only after the formal result had been read and is explicitly labelled
post-result.

## 7. Final disposition

**Bounded manual-review gate: PASS.**  The formal flag at `theta=0.7` is
resolved locally as a reproducible, substantially subzero wiggle of `f_t`,
not as a density-mode fold candidate.  **Original formal-line action: still
inconclusive.  Old simplex fallback: not authorized.  Continuum and project
gates: still false.**
