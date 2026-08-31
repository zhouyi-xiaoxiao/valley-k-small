# Round 59: positive-budget broad-four-slab canonical result closure

Date: 2026-07-14  
Role: canonical post-result admission and claim-boundary closure  
Verdict: **PASS-FIXED-CONTROL-POSITIVE-B / HOLD-PRR-PROJECT**

## 1. Frozen execution and non-tuning boundary

The externally frozen numerical anchor was

```text
artifacts/data/positive_b_broad_four_slab_manifest.json
SHA-256 955e59bf333b5fd70e415a53dc26becae9c7a34c5d40f1230c96b1dab8f5677c
```

The formal entry point ran exactly two complete sequential subprocess replicas
under the manifest's one-thread environment.  Both replicas returned exit zero
and the same scientific status.  The parent compared their complete canonical
JSON bytes before promoting the result and reproducibility record.  Both hidden
replica files were removed after promotion.

No weight, budget, support, transport parameter, box, mesh, scan window,
threshold, or claim flag was changed after either replica was observed.  The
fixed physical allocation was

```text
B = 0.01
w = (0.28,
     0.27736690132708747,
     0.0857172266153233,
     0.3569158720575891).
```

## 2. Pre-audit provenance gate

Before opening the canonical JSON, the following checks passed:

- the manifest retained its exact external hash;
- all 14 manifest pins were ordinary nonsymlink files and matched their frozen
  SHA-256 values;
- the independent auditor retained SHA-256
  `8e84d8930393e4ba60a906519eef7f1734c713a273791153a55d1f6f16ec3985`;
- all five auditor test files retained their Round-51 hashes;
- the v2 post-result protocol retained SHA-256
  `d92e5ff2f238a4abb84b8534442122587a98793184f724357f6dc72039ac564b`;
- the Round-51 protocol audit retained SHA-256
  `e935007c0aa79bd19c6f9ace4304b33e15782fbee3b2d552579423e0f0372af0`;
- the canonical result and reproducibility inputs were regular nonsymlink
  files, the canonical independent-audit path was absent, and both hidden
  replicas were absent.

Only after that gate passed was the frozen canonical auditor invoked.  It was
invoked exactly once:

```bash
.venv/bin/python \
  research/reports/encounter_multimodal_prr/code/audit_positive_b_broad_four_slab_result.py
```

It returned exit zero and

```text
PASS_INDEPENDENT_RECONSTRUCTION
```

The auditor did not import the numerical producer.  It checked exact schema,
types, manifest and pin provenance, two-process evidence, negative claim
flags, and all saved mesh/agreement gates.  It independently reconstructed
the claim-bearing algebra available from the saved roots, survival values,
event masses, tangent rows, tail checkpoints, and two-mesh differences.  As
frozen in advance, it did not rerun the semigroup or witness the subprocesses.

## 3. Canonical artifact hashes

| role | path | SHA-256 |
|---|---|---|
| result | `artifacts/data/positive_b_broad_four_slab_result.json` | `51e8eb4bdb652124865d0c39e6f36b99d13ed61578b161e0f75b142cada49401` |
| two-process evidence | `artifacts/data/positive_b_broad_four_slab_reproducibility.json` | `6c0eccaae09ef95923843ddd7a141a27311e1575ee68d3301b4757b785ee9890` |
| independent audit | `artifacts/data/positive_b_broad_four_slab_independent_audit.json` | `60c541a6f0decd5431cefa5c203311176e61006586ce69043d5fcf5380ed517d` |

The reproducibility record contains two replica exit codes `[0,0]`, two copies
of the canonical result hash above, `byte_identical=true`, and
`canonical_promotion_after_comparison=true`.

## 4. Released positive-budget point

Both fixed-box odd cubic meshes retained five alternating simple stationary
roots, hence at least three local maxima on the declared finite window.

| quantity | mesh 113 | mesh 129 |
|---|---:|---:|
| root 1, maximum | 3.3367649301 | 3.3066991731 |
| root 2, minimum | 5.0943084947 | 5.0851516692 |
| root 3, maximum | 8.6222838014 | 8.5884766325 |
| root 4, minimum | 13.5614667007 | 13.5291737000 |
| root 5, maximum | 22.5488959397 | 22.5148180701 |
| minimum/maximum peak-height ratio | 0.8333934840 | 0.8391414833 |
| valley ratios | 0.7823931607, 0.8467280181 | 0.7646777489, 0.8437520432 |
| basin masses | 0.00521142784, 0.01662828849, 0.14837901354 | 0.00522783949, 0.01659738182, 0.14848157030 |
| survival at 100 | 0.8297812701 | 0.8296932084 |

For each mesh every frozen gate passed.  The auditor algebraically reconstructed
the gates supported by the saved roots, survival values, event masses, tangent
rows, tail checkpoints, and two-mesh summaries.  For gates whose underlying
full state vectors or full-scan extrema were not saved, it re-evaluated the
producer-reported certified extrema and residuals against the frozen thresholds;
it did not recompute those states or the semigroup.  The combined gate set
included:

- alternating topology, root residuals and curvature;
- peak and valley shape margins;
- positive density and survival, state nonnegativity tolerance, and monotone
  survival through the final time;
- `Q 1 = -B kappa`, differential mass balance on the scan, roots, tail and
  final time, and event-partition closure;
- all three event-basin masses above `0.005`; and
- direct-versus-tangent state and time-jet reproduction.

All two-mesh agreement gates also passed.  The largest paired-root-time
difference was `0.0340778696`, peak-ratio difference `0.00574799935`, maximum
valley-ratio difference `0.0177154118`, maximum basin-mass difference
`0.000102556762`, and final-survival difference `0.0000880617415`.

## 5. Tight margins that must remain visible

This is a genuine PASS, but it is not a high-margin result in every direction.

- The smallest basin mass is `0.0052114278399768565`, only
  `0.0002114278399768565` above the frozen `0.005` floor, a `4.23%` margin
  relative to that floor.
- The largest valley ratio is `0.8467280181266086`, only
  `0.0032719818733914` below the frozen `0.85` ceiling.
- The largest two-mesh valley-ratio difference is `0.017715411814572146`
  against a `0.03` agreement ceiling.

These are reasons for the predeclared parity, box, fine--large, and independent
off-lattice program.  They are not reasons to relax a gate, refit the control,
or describe the result as continuum robust.

## 6. Exact claim admitted by this closure

The strongest admitted reader-facing statement is:

> At `B=0.01`, the result-informed broad-four-slab fixed control (an unchanged
> allocation selected from the leading free-exposure design) has at least three
> event-mass-qualified modes on the declared finite-time window on two held-out
> odd finite-volume meshes in one fixed reflected box and the same solver
> family.

The words `result-informed`, `fixed control`, `fixed box`, `two odd meshes`,
`same solver family`, `declared window`, and `at least` remain scientifically
material.

The canonical result stores the first five false Boolean flags below both at the
top level and in `required_claim_flags`.  The independent audit repeats those
five and additionally stores `allocation_cusp_verified=false`.  The manifest's
forbidden-promotion list, the result limitations, and the frozen protocol keep
physical-`d=3` and publication-gate claims false; those final two names are
intentionally absent as canonical-result keys.

```text
preregistered_discovery = false
continuum_interval_verified = false
unbounded_domain_FV_limit_verified = false
independent_solver_verified = false
allocation_cusp_verified = false
physical_d3_verified = false
project_gate_passed = false
publication_gate_passed = false
```

In particular, this point is not an allocation cusp, does not provide either
fold branch or a phase diagram, does not establish an exact global modal
count, and is not a continuum, unbounded-domain, independent-solver,
physical-`d=3`, or PRR release result.

## 7. Authorization decision

This round changes the project state from “positive-`B` fixed point pending” to
**PASS-FIXED-CONTROL-POSITIVE-B**.  It authorizes a narrowly qualified internal
manuscript insertion and use of the canonical hashes as inputs to later frozen
validation designs.

It does not authorize a cusp-centered title, the main allocation phase figure,
or submission.  The next scientific gates remain:

1. independently close and freeze the repaired allocation-cusp Stage-A v2
   producer, protocol, manifest, tests, and post-result auditor;
2. run meshes 65 and 97 only as low-mesh discovery after a separate zero-open-
   P0/P1 pre-run attack;
3. freeze and execute the no-refit Stage-B parity/alignment/box/fine--large
   matrix with a correctly centered deterministic uncertainty envelope; and
4. freeze and execute the powered unbounded off-lattice Doi validation with a
   universal thinning bound, global inference ledger, and no top-up.

The overall PRR project therefore remains **HOLD** despite this successful and
necessary numerical milestone.
