# Round 13: frozen formal-discovery result audit

Date: 2026-07-13  
Scope: independent, read-only audit of the completed
`65 x 65 x 49` control-line discovery run  
Verdict: **PASS for artifact integrity and fail-closed result semantics; no
fold or additional density-mode candidate was found on the frozen line.**

This verdict does not pass the continuum project gate.  The output correctly
retains `continuum_verified=false` and `project_gate_passed=false`.  Its
`line_has_discovery_flag=true` is caused only by a conservative unmatched-
extremum transition at `theta=0.7`; it must not be reported as a fold,
bimodality, or a physical discovery.

## Severity ledger

| Severity | Open findings | Disposition |
|---|---:|---|
| P0 | 0 | no integrity, provenance, or false-positive claim failure |
| P1 | 0 | no unresolved result-validation defect |
| P2 | 0 | no implementation defect found in this audit |

One protocol action remains mandatory but is not a defect: the topology
transition at `theta=0.7` requires a bounded manual review.  The present result
does **not** authorize the simplex fallback.

## 1. Frozen inputs and byte-level provenance

The hashes recorded by the result and integrity ledger reproduce from the
current files:

| Object | Reproduced SHA-256 |
|---|---|
| frozen manifest | `193c0fc1b7281dee2dd38b6c1152b73591dc0e0b82f5d3510edcd1e7e2dc7390` |
| discovery runner | `1411384398ed4e476dba15371cdfd662e94ed3a53cffdc02a1562201cfa7b52e` |
| runner tests | `70d6aec2b8155961f170c7a791ea8fd3c57286110cd12810cbc9a8f684d4d71b` |
| frozen protocol note | `8cbf2469fab0c18982028450f5c3f0c1ff188c3105ae280c5448fcf1cf23125d` |
| completed result | `2052c1d26211661995d6048b2cd3ca909f04ce48efb9a96c32bd153c7c63d40d` |
| checkpoint integrity ledger | `7a7fbe2c5d7798ae7fc2edad813cda3cae4002935f444b0ae442482a5c967f1a` |

The result also reproduces the pinned G1a artifact and producer hashes:

- foundation artifact:
  `a0a1894dbe6dd37bad6973ca6f3dd29b651441f7b911a5406186bb86a18fd3c3`;
- foundation producer:
  `e0322b212e466b1b640f5adcf30d67d119d2f6fe4cc622eb532082b6cd251701`.

The following cross-checks passed:

- the manifest is still `FROZEN_BEFORE_RUN` and specifies exactly
  `65 x 65 x 49 = 207025` states, 11 controls, and 321 times from `0` to
  `80` with spacing `0.25`;
- the result, ledger, and all checkpoints carry the same configuration hash
  `5ba499a4840f3ff35d181d9906c1895ac795794d2b92f58e04169d15568356a2`;
- all 11 ledger entries reproduce the SHA-256 of their current checkpoint
  bytes and their `theta_index`/`theta` metadata;
- all 11 checkpoint payloads equal their corresponding result-embedded
  control payloads exactly;
- the ledger configuration and provenance equal the result configuration and
  provenance exactly;
- all controls were computed in this invocation (`11` computed, `0` resumed),
  and the summed checkpoint runtimes (`387.9636923349899 s`) are consistent
  with the reported wall time (`388.20029208398773 s`);
- `.run.lock` is `RELEASED`, with the same run mode and configuration hash;
  and
- the independent replay of the runner test file passed: `48 passed`.

There is therefore no evidence of a stale, orphaned, substituted, or
post-hoc-modified control artifact.

## 2. Run-level status semantics

The status `DISCOVERY_LINE_COMPLETE` means only that the frozen computation
completed.  It does not mean that a fold was discovered or that the project
gate passed.  The decisive fields are:

```text
formal_frozen_run_completed = true
continuum_verified = false
project_gate_passed = false
near_zero_extremum_count = 0
adjacent_theta_sign_bracket_count = 0
assignment_ambiguity_count = 0
interior_discovery_flag = false
topology_transition_manual_review_required = true
next_protocol_action = topology_transition_requires_manual_review_before_line_action
```

`line_has_discovery_flag=true` is an umbrella diagnostic in the runner.  By
construction it is also set by any transition requiring manual review.  Here
it is set by unmatched retained extrema at the `0.6 -> 0.7` and
`0.7 -> 0.8` transitions, not by either fold-candidate rule.

## 3. All-control audit

Every control has all 38 current model/foundation gates true in addition to
the pinned 42-gate G1a preflight.  Every checkpoint has status
`THETA_COMPLETE`, contains six finite 321-point curve arrays, stores no full
state history, and retains both claim gates as false.  The one excluded
`f_t` root and one excluded `f_tt` extremum at each control are the declared
initial `t=0` zero plateau, with the same preanalysis/density-floor exclusion
signature at every control.

| theta | weights | retained roots of `f_t` | retained extrema of `f_t` | near-zero extrema | retained density topology |
|---:|---|---:|---:|---:|---|
| 0.0 | `(0.700, 0.250, 0.050)` | 1 | 2 | 0 | sampled maximum |
| 0.1 | `(0.635, 0.250, 0.115)` | 1 | 2 | 0 | sampled maximum |
| 0.2 | `(0.570, 0.250, 0.180)` | 1 | 2 | 0 | sampled maximum |
| 0.3 | `(0.505, 0.250, 0.245)` | 1 | 2 | 0 | sampled maximum |
| 0.4 | `(0.440, 0.250, 0.310)` | 1 | 2 | 0 | sampled maximum |
| 0.5 | `(0.375, 0.250, 0.375)` | 1 | 2 | 0 | sampled maximum |
| 0.6 | `(0.310, 0.250, 0.440)` | 1 | 2 | 0 | sampled maximum |
| 0.7 | `(0.245, 0.250, 0.505)` | 1 | 4 | 0 | sampled maximum |
| 0.8 | `(0.180, 0.250, 0.570)` | 1 | 2 | 0 | sampled maximum |
| 0.9 | `(0.115, 0.250, 0.635)` | 1 | 2 | 0 | sampled maximum |
| 1.0 | `(0.050, 0.250, 0.700)` | 1 | 2 | 0 | sampled maximum |

The retained density-peak time moves from `4.413688` to `10.687314` across
the line.  Its interpolated dimensionless curvature is negative at every
control (from `-3.178368` through a least-magnitude value of `-1.033547`), so
the sampled critical point is consistently a nondegenerate maximum, not a
minimum or unresolved root.  No adjacent matched extremum branch changes the
sign of `f_t`.

## 4. What happens at `theta=0.7`

At `theta=0.7`, the sole retained root of `f_t` is

```text
t = 5.5723898138
f = 0.0372679758
f_tt = -0.0020818033
dimensionless curvature = -1.7345501765
```

It is the only sampled density maximum.  The four retained extrema of `f_t`
are:

| kind | interpolated time | interpolated `f_t` | `abs(t f_t / f)` |
|---|---:|---:|---:|
| maximum | 2.506037 | `+1.5647822e-2` | 2.604552 |
| minimum | 7.829821 | `-1.5281453e-3` | 0.344745 |
| maximum | 11.110270 | `-1.3839237e-3` | 0.512950 |
| minimum | 13.926377 | `-1.4125477e-3` | 0.755559 |

Thus the additional late-time wiggle is entirely below `f_t=0`.  The late
local maximum is `-1.3839237e-3`, and its dimensionless height is 10.26 times
the frozen candidate cutoff `0.05`.  Even the smallest dimensionless height
among the three late extrema is `0.344745`, 6.89 times the cutoff.  The rise
from the first late minimum to the late maximum is only
`1.4422159e-4`; the late maximum remains 9.60 such amplitudes below zero.

A fold creating or destroying density modes requires simultaneous
`f_t=0` and `f_tt=0`.  These data supply sampled `f_tt` sign changes, but the
corresponding `f_t` values are negative with a substantial frozen-metric
margin.  They therefore show, at most, a shallow subzero wiggle in the
derivative of the density.  They do **not** show a new root of `f_t`, a new
maximum/minimum of the density, a fold, or multimodality.

The non-crossing matcher correctly refuses to hide the topology change:

- at `0.6 -> 0.7`, extrema 2 and 3 on the right are unmatched;
- at `0.7 -> 0.8`, extrema 1 and 2 on the left are unmatched;
- retained `f_t`-root count and ordered root topology remain stable;
- filter signatures remain stable; and
- there is no assignment ambiguity and no sign bracket.

Because the time spacing is `0.25` and the zero locations are linearly
interpolated, this artifact alone should not decide whether the very shallow
`f_tt` sign changes are a numerically resolved feature or a tolerance-level
semigroup effect.  That classification is exactly the purpose of the required
manual review.  It does not change the negative fold conclusion from the
frozen candidate rules.

## 5. Permitted next action

**Manual review: allowed and required.**  It should be a separately recorded,
explicitly post-result diagnostic on the unchanged model, mesh, weights, and
physical parameters.  A defensible minimum check is denser time sampling and
tighter/independent semigroup evaluation around `theta=0.7`, `t` approximately
`7--15`, retaining direct `f_t`, `f_tt`, and `f_ttt` generator-action jets.
Its purpose is to classify the unmatched subzero wiggle, not to tune a fold
candidate.

**Simplex fallback: not currently authorized.**  The frozen protocol permits
the spacing-`0.1` simplex only after a line-empty decision with complete,
unambiguous extremum matching and stable transition signatures.  The present
result deliberately withholds that decision.  Merely observing that the
wiggle is below zero is not enough to bypass the recorded manual-review gate.
Any later authorization must cite a documented manual-review resolution under
the frozen no-retuning rules; it cannot reinterpret
`line_has_discovery_flag=true` as a fold finding.

**Candidate confirmation/continuation: not authorized.**  There is no
interior near-zero extremum and no adjacent-theta sign bracket to freeze.

## 6. Claim boundary

The strongest statement supported by this run is:

> On the frozen `65 x 65 x 49`, `t in [0,80]`, spacing-`0.25` discovery line,
> every sampled control has exactly one retained critical point of the density,
> a maximum.  No frozen fold-candidate rule fires.  One subzero derivative-
> topology transition near `theta=0.7` requires manual review before any line-
> empty or simplex action.

It is not evidence of continuum convergence, an infinite-time root count, a
2D physical cusp, a fold manifold, bimodality, or PRR-level project-gate
completion.
