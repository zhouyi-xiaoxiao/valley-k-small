# Round 51 independent audit of the frozen post-result protocol v2

Audit date: 2026-07-14  
Audited protocol:
`notes/positive_b_postresult_audit_protocol_v2.md`  
Protocol SHA-256:
`d92e5ff2f238a4abb84b8534442122587a98793184f724357f6dc72039ac564b`

## Decision

**GO-PROTOCOL / HOLD-SCIENCE.  P0: 0, P1: 0, P2: 0.**

The v2 protocol accurately freezes the numerical and auditor anchors, states
the auditor's actual independence boundary, and matches the implementation's
fail-closed validation, publication transaction and exit semantics.  It is
suitable to govern one later canonical post-result invocation.

This audit did not open any hidden replica and did not run the canonical
auditor.  It did not read or modify a canonical result, reproducibility record,
or independent-audit JSON.  The protocol itself was not edited.

## Frozen-anchor verification

The protocol bytes independently hash to
`d92e5ff2f238a4abb84b8534442122587a98793184f724357f6dc72039ac564b`.

The v2 numerical manifest is an ordinary non-symlink file and independently
hashes to
`955e59bf333b5fd70e415a53dc26becae9c7a34c5d40f1230c96b1dab8f5677c`.
Its `pinned_files` object contains exactly the 14 roles listed by the protocol:

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

Every one of the 14 referenced paths currently names an ordinary non-symlink
file, and every actual SHA-256 matches its manifest entry.  This includes the
scientific protocol pin
`f25a8107d7a975342a3b1cbbf84c29df26654a8f6310f0429cba5ffdf7bcda00`,
the v2 producer
`adb9434daeccca721ab9c1014f194e0cf9c5c6d0bf092d31e050c040b4b94da8`,
the v2 producer tests
`d60e837c949333d29f7287b17c5e24c6db742067a655bac5050b5966dc821329`,
and the operational erratum
`9843b323898b7e0e9edd0eff33431cddb9fb3d4d572caa4d9ebc5d1e5649592c`.

The auditor and all five test files are ordinary non-symlink files and match
the protocol exactly:

| Role | SHA-256 |
| --- | --- |
| auditor | `8e84d8930393e4ba60a906519eef7f1734c713a273791153a55d1f6f16ec3985` |
| original tests | `757807729bee2dc9832bb741ba589843cd835e564aead0df7a67982b8a421fe0` |
| Round-40 attacks | `4d81932ab193eec77659d8262120cf49183528ac7e37501bc65c22b0d90e1b2a` |
| Round-42 attacks | `603aee3b506f1fcf348a06f8f784be4144eb65965e891861c498697743af237f` |
| resolution regressions | `411a25081d48bc235ab78cc82d65a28ba00a87e775f72c406e907b08113669f3` |
| Round-45 attacks | `cec616f487337c6106aca664484fc930a148d5332187ffe6de47c74f03c35855` |

The cited Round-45 closure record also matches its frozen hash
`7892d6e942a5448c80b2c9e11f5ce914d7e948843264fcef9d23b02d799545e8`.

## Test-evidence verification

The frozen suites were rerun without pytest cache creation:

```text
auditor suites: 42 passed
v2 producer suite: 16 passed
Ruff: All checks passed
Ruff format: 8 files already formatted
```

The protocol's `42` and `16` claims are therefore current for the frozen
bytes, not copied from an unverified earlier report.

## Independence-boundary attack

The four levels in Section 1 match the auditor implementation and do not
promote saved producer data into an independent-solver claim:

1. **Exact schema and provenance** correctly covers canonical finite JSON,
   exact schemas and types, the exact-manifest anchor and its 14 pins, frozen
   inputs, limitations, and hash consistency of the recorded two-process
   evidence.
2. **Algebraically reconstructed** correctly covers quantities recomputable
   from saved scalars and traces: topology/curvature identities, conditional
   ratios, event-basin mass closure, tangent time-jet differences, tail
   summaries, two-mesh nullable metrics, gates and aggregate PASS/HOLD.
3. **Re-evaluated producer reports** correctly identifies gates whose extrema
   or residual inputs are producer-reported because the full vectors or
   semigroup trajectory are absent.
4. **Not established** explicitly excludes an independent semigroup, newly
   located roots, witnessed subprocess execution, continuum/unbounded-domain
   convergence, an independent physical solver, an allocation cusp, physical
   `d=3`, and project/publication release.

The later statement that two sequential, byte-identical results are required
is expressly limited to internal consistency of the evidence record.  The
protocol correctly says the auditor checks recorded hashes and decisions but
did not witness either process execute.

## Filesystem and transaction semantics

The protocol matches the final auditor on all attacked boundaries:

- result, evidence, manifest, every pin, and auditor source are required to be
  ordinary non-symlink files;
- paths are retained lexically rather than normalized through a symlink;
- `lstat` regular-file checks and byte hashes are repeated during validation,
  immediately before replacement, immediately after replacement, and after
  the output-directory `fsync`;
- staging is same-directory and exclusive;
- a failure after replacement restores the exact prior audit or removes a new
  audit, then directory-`fsync`s before propagating the error; and
- output aliases, initial and replacement symlinks, source/input swaps, and
  injected file-`fsync`, replace and directory-`fsync` failures are covered by
  the frozen tests.

The residual lock-free race is neither hidden nor overstated.  The protocol
requires immutable inputs and no non-cooperating concurrent writer during the
short audit/publication interval and explicitly disclaims protection against a
change-and-restore occurring wholly between checks.  This is the correct
operational assumption for the implemented transaction.

## Invocation and outcome semantics

The prescribed repository-root command and all three default paths match the
auditor constants.  The outcome mapping matches `main()`:

| Process outcome | Meaning |
| --- | --- |
| exit `0`, `PASS_INDEPENDENT_RECONSTRUCTION` | all frozen mesh and agreement gates pass within the limited fixed-box/two-mesh scope |
| exit `2`, `HOLD_REPRODUCED` | the canonical scientific HOLD is internally and algebraically reproduced |
| other nonzero exit or exception | operational/provenance failure; neither scientific PASS nor HOLD may be inferred |

On a publication exception, no new replacement audit remains; if an older
audit existed, its exact bytes are restored.  Thus the protocol's wording is
consistent with rollback rather than implying deletion of valid prior
evidence.

## Current canonical-artifact state

Existence checks only, without opening any candidate file, found:

```text
ABSENT  artifacts/data/positive_b_broad_four_slab_result.json
ABSENT  artifacts/data/positive_b_broad_four_slab_reproducibility.json
ABSENT  artifacts/data/positive_b_broad_four_slab_independent_audit.json
```

The protocol is therefore frozen before all three canonical artifacts, as
required.  `HOLD-SCIENCE` remains mandatory until the formal execution has
finished and the one authorized canonical audit has returned an actual result.

## PRR claim boundary

The eight claims in Section 6 remain false or forbidden-by-schema as
appropriate:

```text
preregistered_discovery
continuum_interval_verified
unbounded_domain_FV_limit_verified
independent_solver_verified
allocation_cusp_verified
physical_d3_verified
project_gate_passed
publication_gate_passed
```

The first four and `project_gate_passed` are exact false fields in the frozen
manifest/result contract.  Allocation-cusp, physical-`d=3`, and publication
promotion keys are rejected at unauthorized result locations; the eventual
audit boundary also records the allocation-cusp claim as false.  The protocol
does not allow a post-result PASS to silently promote any of them.

Consequently, even a later exit-0 audit licenses only the explicitly qualified
result-informed, fixed-control, fixed-box, two-held-out-mesh, same-solver-family
semidiscrete point.  It does not close the PRR project gate or replace the
subsequent cusp, continuation, remote-pair/event-mass, and independently frozen
off-lattice/unbounded validation program.
