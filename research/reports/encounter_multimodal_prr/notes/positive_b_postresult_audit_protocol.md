# Frozen independent post-result audit protocol

Freeze time: `2026-07-13T22:45:05Z`  
Evidence timing: frozen while the first formal replica was still running and
before either canonical result or reproducibility JSON existed.

## Boundary

This audit is separate from the numerical producer.  It imports no producer
code and cannot recompute the finite-volume semigroup.  Instead it reconstructs
from the eventual canonical JSON every reported mesh gate, the five-root
topology, curvature signs, peak and valley ratios, the three survival-defined
event-basin masses, their partition closure, all two-mesh agreement metrics,
the overall PASS/HOLD decision, and the two-process byte-identity evidence.

It must fail closed if the result:

- changes the externally frozen manifest or any of its thirteen source pins;
- changes the two held-out meshes, physical inputs, weights, or budget;
- promotes continuum, unbounded-domain, independent-solver, preregistration,
  or project-release flags;
- reports a scalar, Boolean gate, aggregate decision, replica exit code, or
  canonical hash inconsistent with the underlying saved values; or
- is not finite canonical JSON.

A passing audit licenses only one result-informed, fixed-box, two-mesh,
semidiscrete positive-`B` point.  It does not license an allocation cusp,
continuum limit, unbounded-box limit, independent physical solver, physical
`d=3` result, or PRR release.

## Frozen inputs

| Role | Path | SHA-256 |
| --- | --- | --- |
| numerical manifest | `artifacts/data/positive_b_broad_four_slab_manifest.json` | `01b435c834cec9e7bfde2069b19fcdcaa4e06178ccfe0d4b6082f0705dfd5805` |
| independent auditor | `code/audit_positive_b_broad_four_slab_result.py` | `eed476815960005271a3a5dce11f1054862bc1ba1d4b80df71b9862486639aa2` |
| auditor tests | `code/test_audit_positive_b_broad_four_slab_result.py` | `d408006873b6130df7f644beec9ad9c50bacc02955ede915e5ed9bbbf67cb2d8` |

At freeze, the focused auditor suite had `4 passed` and Ruff reported `All
checks passed`.  Neither `positive_b_broad_four_slab_result.json` nor
`positive_b_broad_four_slab_reproducibility.json` existed.

## Post-result command

From the repository root, without modifying the frozen files:

```bash
.venv/bin/python \
  research/reports/encounter_multimodal_prr/code/audit_positive_b_broad_four_slab_result.py
```

The independent audit JSON is written only after all checks pass or reproduce
a scientifically legitimate HOLD.  An operational or consistency failure must
not write a replacement result or reinterpret a near-pass.
