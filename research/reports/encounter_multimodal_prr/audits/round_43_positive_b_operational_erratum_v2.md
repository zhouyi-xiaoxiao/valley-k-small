# Round 43: positive-budget operational erratum v2

Date: 2026-07-14  
Scope: first formal-run failure, minimal serialization repair, and v2 re-freeze

## Decision

**PASS for a serialization-only v2 repair; scientific result still pending.**

The first two-process formal execution did not produce a canonical numerical
result. Replica 1 completed both held-out meshes and then failed while
serializing its in-memory result:

```text
TypeError: unsupported JSON value bool at
$.heldout_mesh_rows[0].gates.survival_positive
```

The reported type name was NumPy's `bool_`, not native Python `bool`. The
failure occurred before a replica JSON, reproducibility record, or canonical
result was promoted. Both public output paths were confirmed absent. This is
an operational failure and supplies no scientific PASS/HOLD evidence.

## Mutation boundary

The v2 repair changes no physical parameter, geometry, weight, budget,
held-out mesh, time grid, root criterion, event-mass rule, tolerance, agreement
gate, PASS/HOLD decision, or prohibited-promotion flag.

The only executable change is a fail-closed helper that:

1. accepts native Python Boolean and NumPy Boolean scalar gate values;
2. converts them to native JSON Boolean values; and
3. rejects integers, floats, strings, nulls, and arbitrary truthy objects.

It is applied uniformly to tail, per-mesh, and cross-mesh gate mappings. One
new test reproduces NumPy-comparison Boolean scalars, confirms canonical JSON
serialization, and checks rejection of non-Boolean values. The formal
preflight count is therefore 16 rather than 15. The original scientific
protocol remains unchanged and a separate operational erratum is now an
additional frozen pin.

## Verification before v2 execution

- formal tests: `16 passed`;
- Ruff format: clean;
- Ruff lint: `All checks passed`;
- real `9 x 9 x 9` full `solve_mesh` path: 24 gate values, all native Boolean;
- the complete small-mesh row serialized to 141,575 canonical JSON bytes;
- v2 manifest exact-pin validation: 14 roles;
- canonical result: absent;
- two-process evidence: absent.

## v1 and v2 anchors

| Role | v1 failed-run SHA-256 | v2 SHA-256 |
| --- | --- | --- |
| manifest | `01b435c834cec9e7bfde2069b19fcdcaa4e06178ccfe0d4b6082f0705dfd5805` | `955e59bf333b5fd70e415a53dc26becae9c7a34c5d40f1230c96b1dab8f5677c` |
| producer | `0c70ffb4a9034772928e2fa95d2ca79ef33754e5aa4157a2f101e15cb312b003` | `adb9434daeccca721ab9c1014f194e0cf9c5c6d0bf092d31e050c040b4b94da8` |
| tests | `ee784d1cf6cc4e7ee66968deb8f3421394f697eebee3a50f783533aa469a8f78` | `d60e837c949333d29f7287b17c5e24c6db742067a655bac5050b5966dc821329` |
| scientific protocol | `f25a8107d7a975342a3b1cbbf84c29df26654a8f6310f0429cba5ffdf7bcda00` | unchanged |
| operational erratum | absent | `9843b323898b7e0e9edd0eff33431cddb9fb3d4d572caa4d9ebc5d1e5649592c` |

The v2 public process was started only after these hashes were fixed and was
given the v2 manifest hash externally. It again launches two fresh sequential
full replicas. No parameter may be tuned after seeing either replica.

## Remaining boundary

Even a successful v2 calculation licenses at most the frozen fixed-box,
two-mesh, result-informed positive-budget point. It cannot by itself establish
an allocation cusp, a continuum or unbounded-box limit, an independent-solver
result, physical `d=3`, or the PRR release gate.
