# Frozen independent post-result audit protocol v2

Freeze time: `2026-07-13T23:50:03Z` (`2026-07-14 00:50:03 BST`)  
Evidence timing: frozen while formal replica 1 was still running and before the
canonical result, two-process reproducibility record, or independent-audit JSON
existed.

## 1. Purpose and non-negotiable boundary

This protocol freezes a post-result **schema, provenance, and algebraic
reconstruction** of the result-informed broad four-slab positive-`B` experiment.
The auditor imports no numerical producer when it audits the canonical files.
It is not a second finite-volume solver and it did not observe either producer
subprocess execute.

The audit has four explicitly different evidence levels:

| Level | What the auditor establishes |
| --- | --- |
| Exact schema and provenance | canonical finite JSON; exact field sets and native JSON types; the v2 manifest and all 14 pins; physical inputs, weights, budget, mesh identities and limitation strings; result/evidence hashes and internally consistent two-process records |
| Algebraically reconstructed | topology labels from saved curvatures; scaled root identities; conditional peak/valley ratios; survival-defined basin masses and closure; tangent-row time-jet differences; tail checkpoint summaries; two-mesh nullable differences, gates and aggregate PASS/HOLD |
| Re-evaluated producer reports | gates depending on full-scan extrema, generator mass-balance residual, root state/mass-balance residuals, direct-versus-tangent state norms, and finite-volume factor diagnostics whose underlying full state vectors are not saved |
| Not established | an independent semigroup calculation, independently located roots, observed execution of two subprocesses, continuum or unbounded-domain convergence, an independent physical solver, a finite-`B` allocation cusp, physical `d=3`, or project/publication release |

A successful audit therefore licenses at most one result-informed,
fixed-control, fixed-box, two-mesh semidiscrete positive-`B` point. It cannot by
itself close the PRR project gate.

## 2. Frozen v2 numerical anchor

The externally frozen numerical manifest is:

```text
artifacts/data/positive_b_broad_four_slab_manifest.json
SHA-256 955e59bf333b5fd70e415a53dc26becae9c7a34c5d40f1230c96b1dab8f5677c
```

It contains exactly 14 pinned roles:

```text
B0_bridge_manifest
B0_bridge_producer
B0_bridge_result
exact_continuum_dependency
feasibility_N65_all_budgets
feasibility_N97_B001
feasibility_N97_B002
feasibility_producer
finite_volume_dependency
grid_dependency
operational_erratum
producer
protocol
tests
```

The scientific protocol pin remains
`f25a8107d7a975342a3b1cbbf84c29df26654a8f6310f0429cba5ffdf7bcda00`.
The v2 producer, tests, and serialization-only operational erratum are pinned
inside the manifest. The v2 producer suite passed 16 tests plus Ruff and format
checks at this freeze. No scientific input, threshold, held-out mesh, weight,
budget, scan window, or claim boundary changed in the operational erratum.

## 3. Frozen independent-auditor implementation

| Role | Path | SHA-256 |
| --- | --- | --- |
| auditor | `code/audit_positive_b_broad_four_slab_result.py` | `8e84d8930393e4ba60a906519eef7f1734c713a273791153a55d1f6f16ec3985` |
| original tests | `code/test_audit_positive_b_broad_four_slab_result.py` | `757807729bee2dc9832bb741ba589843cd835e564aead0df7a67982b8a421fe0` |
| Round-40 attacks | `code/test_audit_positive_b_broad_four_slab_result_round40.py` | `4d81932ab193eec77659d8262120cf49183528ac7e37501bc65c22b0d90e1b2a` |
| Round-42 attacks | `code/test_audit_positive_b_broad_four_slab_result_round42.py` | `603aee3b506f1fcf348a06f8f784be4144eb65965e891861c498697743af237f` |
| resolution regressions | `code/test_audit_positive_b_broad_four_slab_result_resolution.py` | `411a25081d48bc235ab78cc82d65a28ba00a87e775f72c406e907b08113669f3` |
| Round-45 closure attacks | `code/test_audit_positive_b_broad_four_slab_result_round45.py` | `cec616f487337c6106aca664484fc930a148d5332187ffe6de47c74f03c35855` |

The six-file audit suite passed `42` tests. Ruff check, Ruff format check, and
Python byte compilation passed. The closure record is
`audits/round_45_postresult_auditor_closure.md`, SHA-256
`7892d6e942a5448c80b2c9e11f5ce914d7e948843264fcef9d23b02d799545e8`.

Any byte change to the numerical manifest, one of its 14 pins, the auditor, or
any auditor test invalidates this freeze. A revised protocol must then be
frozen before the canonical result is audited; silent hash updates are
forbidden.

## 4. Fail-closed input and publication semantics

The canonical result, reproducibility record, manifest, every pinned input,
and auditor source must remain ordinary non-symlink files. The auditor retains
lexical absolute paths, repeated `lstat` regular-file checks, and byte hashes.
It checks identities during validation, immediately before publication,
immediately after atomic replacement, and after the output directory is
`fsync`ed.

Publication uses a same-directory exclusive staging file. If a failure occurs
after replacement, the transaction restores the prior independent-audit bytes
or removes the newly created audit and then `fsync`s the directory before
propagating the error. Tests inject file-`fsync`, replace, directory-`fsync`,
post-replace input swaps, source swaps, input symlinks, and output aliases.

Residual filesystem assumption: the result, evidence, manifest, pins and
auditor source are immutable and no non-cooperating writer acts during the
short audit-and-publication interval. Repeated lock-free checks cannot exclude
a writer that changes and restores bytes entirely between two checks. This
protocol does not claim otherwise.

## 5. One canonical post-result invocation

Before invocation, re-run the frozen source/test hash checks without editing
any frozen file. Then, from the repository root, run exactly:

```bash
.venv/bin/python \
  research/reports/encounter_multimodal_prr/code/audit_positive_b_broad_four_slab_result.py
```

The default paths are the only authorized paths:

```text
artifacts/data/positive_b_broad_four_slab_result.json
artifacts/data/positive_b_broad_four_slab_reproducibility.json
artifacts/data/positive_b_broad_four_slab_independent_audit.json
```

Interpret the outcome without tuning or rerunning scientific parameters:

- exit `0`, `PASS_INDEPENDENT_RECONSTRUCTION`: the saved point passes every
  frozen mesh and agreement gate within the limited scope above;
- exit `2`, `HOLD_REPRODUCED`: the canonical producer result is a legitimate
  scientific HOLD and must be preserved without threshold, control, geometry,
  weight, mesh, or budget adjustment; or
- any other nonzero exit or exception: operational/provenance inconsistency;
  no scientific PASS/HOLD may be inferred and no replacement audit may remain.

The internally consistent evidence record requires two sequential,
byte-identical producer results and canonical promotion only after comparison.
The auditor checks those recorded hashes and decisions; it does not claim to
have witnessed the processes.

## 6. Reporting and PRR release boundary

Regardless of the canonical outcome, keep these claims false unless separately
established by later frozen work:

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

A PASS may be integrated only with the phrases “result-informed,” “fixed-box,”
“two held-out finite-volume meshes,” and “same solver family.” A HOLD must be
reported as such. Neither branch authorizes a near-pass narrative.

The PRR project remains on scientific HOLD pending, at minimum, the same broad
family's finite-`B` allocation cusp and both folds, remote-pair and event-mass
qualification, odd/even mesh plus box continuation, and a frozen independent
unbounded/off-lattice killed-process validation without refitting.
