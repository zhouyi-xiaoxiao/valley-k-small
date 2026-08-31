# Round 143: selector-v2 certificate-boundary repair

Date: 2026-07-14  
Role: implementer / science-free certificate repair  
Decision: **CANDIDATE PASS FOR CERTIFICATE SHAPE ONLY / HOLD F1 / HOLD POSITIVE B**

## Scope

This round used only exact-rational and synthetic probability fixtures.  It did
not read any prospective control, evaluate a positive reaction budget, run a
semigroup, execute F1/F2/F3, generate a trajectory, or run Monte Carlo.

## Repairs

- Every special-function endpoint is decoded with an exact precision-dependent
  mantissa shape.  Unused low bits must be zero; a syntactically valid but
  non-MPFR endpoint can no longer pass by changing only those bits.
- The parent recomputes the decision and precision ladder from the returned
  endpoints instead of trusting a worker-supplied decision label.
- The frozen 68-record schedule is bound by exact family counts, record types,
  identifiers, order, and SHA-256.  Each record receives a request and response
  receipt.
- Numerical evaluation follows mandatory runtime verification inside the
  worker.  Source, executable, runtime-spec, and ordinary dependency files are
  read through stable descriptor snapshots rather than path-level pre/post
  hashes.
- The generic executor labels caller-supplied schedules
  `CALLER_SUPPLIED_UNCLASSIFIED`; only the explicit science-free resource
  wrapper assigns `SYNTHETIC_RESOURCE_FIXTURE`.
- Worker timeout, exit, stderr, response schema, response size, and peak-RSS
  failures remain fail-closed.

## Adversarial coverage

The focused tests include valid endpoint probes across every precision rung,
low-bit endpoint mutations, runtime-before-evaluation inversions, schedule
order/family/id/hash mutations, parent-side recomputation disagreement, stable
file-snapshot mutations, and generic-versus-synthetic labelling checks.

The certificate repair was subsequently attacked in Round 145 at selector
SHA-256

```text
29fd0a76816dd0da1f613f73d53feaa244d28161e759b3958fc617cbd532b23d
```

Round 145 found no remaining P0 in this certificate surface.  Its separate P1
concerned worker-lock lifetime after parent death, not endpoint or schedule
certificate semantics.

## Boundary

This is an implementation record.  It does not certify the future 36-row F1
inputs, the full-window topology observable, the underlying physical solver,
or any scientific conclusion.

