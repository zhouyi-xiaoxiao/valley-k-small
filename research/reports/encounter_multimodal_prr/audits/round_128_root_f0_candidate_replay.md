# Round 128: root replay of the rate-defined F0 candidate

Date: 2026-07-14  
Decision: **PASS ROOT METHOD REPLAY / HOLD INDEPENDENT F0 ACCEPTANCE / NO F1**

## Scope and frozen candidate

This replay tested the current science-free rate-defined tensor candidate.  It
did not load the prospective `lp_m1`, `lp_m2`, or `lp_m3` control values, form a
positive-budget physical killing row, propagate a production state, or create
an F1 manifest.

```text
code/rate_defined_tensor_f0.py
98ae6d219359ad676243786f03441e30d32891847da4bf0fde263af2e084b007

code/test_rate_defined_tensor_f0.py
0e454e4fbb81765f46673bb47f009830163332f200a5885d505c36bfcc4b9122

code/benchmark_rate_defined_tensor_f0.py
15e264826c1e77c2f62e1290f28dd981f62bfcb2b03625cc603fffe8afd485d4

code/benchmark_physical_geometry_f0.py
b19a0bfe21d3a2e8a43fbc615255e24af6076016a50210ad3b86fece0d38d988

notes/rate_defined_tensor_f0_production_integration_design.md
09028b5ca3655fe1b52a32681f2f71139d09f5f4148a5e3f368226c1d78d7f77
```

## Unit and lint replay

```text
../../../.venv/bin/python -m pytest -q code/test_rate_defined_tensor_f0.py
23 passed

../../../.venv/bin/ruff check \
  code/rate_defined_tensor_f0.py \
  code/test_rate_defined_tensor_f0.py \
  code/benchmark_rate_defined_tensor_f0.py \
  code/benchmark_physical_geometry_f0.py
All checks passed
```

The tests include exact row-corner enumeration on a small kernel, derived-
diagonal rejection, SG/periodic structure, deterministic matrix-free versus
explicit-CSR actions, directed Poisson propagation, jet enclosures, topology
coverage and mutation replay, physical configuration identities, and
control-source rejection.

## Twelve control-blind physical geometries

The exact command was

```text
/usr/bin/time -lp ../../../.venv/bin/python \
  code/benchmark_physical_geometry_f0.py \
  --science-free-control-blind --precision-bits 192
```

The append-only noncanonical timing sidecar is

```text
artifacts/data/f0_control_blind_geometry_replay_20260714.json
5d4de445b3f21444f44e6123f04b70c67259b3b9d1529e1ba8c2aa63c6d8b1b6
```

All 12 configurations were constructed in the normative order.  The payload
records `prospective_control_values_read=false`, exact zero installed-budget
relative radius, independent containment of the disk-area diagnostic, maximum
support/initial normalization widths below `4.482e-13`, and contact-area
interval widths between `4.95e-16` and `6.96e-16`.  Its internal total was
51.98 s; wall time was 53.92 s.  The conservative larger of the two macOS
`time -lp` memory counters was 2,032,338,792 bytes.  The base workload for one
control over all configurations is 34,787,462 states; the largest geometry is
`MR+F` with 7,165,305 states.

## Neutral N=33 rate/action replay

The exact command was

```text
/usr/bin/time -lp ../../../.venv/bin/python \
  code/benchmark_rate_defined_tensor_f0.py \
  --science-free-neutral --profile neutral-n33 --actions 200
```

The sidecar is

```text
artifacts/data/f0_neutral_n33_replay_20260714.json
bf038bf26f8c70f4fdff11654ad32c63a85be1e9550e662b6b2e66877bfee497
```

The 35,937-state construction and 200 matrix-free/CSR actions completed in
20.62 s wall time with a conservative 84,312,064-byte maximum-resident-set
counter.  The matrix-free/CSR L1 discrepancy was `3.993e-16`; the structural
certificate records a rate-derived diagonal, nonnegative off-diagonal and Doi
killing intervals, exact-dyadic substochastic uniformization rows, detailed
balance by construction, and the Dirichlet-form sign.

## `delta_P` branch clarification

The sidecar has

```text
delta_p_direct_exact < delta_p_via_q_exact
delta_p_exact = delta_p_direct_exact.
```

This is not an understated radius.  `delta_p_direct_exact` and
`delta_p_via_q_exact` are separately derived upper bounds on the same target
operator distance; therefore their minimum is also an upper bound.  The
builder requires the direct branch not to exceed the independent
`delta_Q/lambda` branch, the validator recomputes both from source intervals,
and the small-kernel test enumerates every interval corner and checks its
actual row distance against the selected minimum.

## Remaining gates

This replay does not establish production feasibility for one 7.16-million-
state killed kernel, the full 36-row campaign, or two complete process
replicas.  It also supplies no append-only F0 schema/attestation, no independent
verifier, no accepted common-observable selector, and no positive-budget
scientific value.  Those are independent P1 gates.  Consequently the only
valid conclusion is method-candidate readiness for independent attack; F1
remains unauthorized.
