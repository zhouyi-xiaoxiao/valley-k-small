# Round 136: frozen F0 black-box strict-type audit

Date: 2026-07-14

Decision: `REJECT FROZEN F0 CORE / P0=1 / HOLD F1`

This report transcribes the result returned by a fresh agent launched with no
conversation fork.  The agent was restricted to the frozen F0 source/tests and
Rounds 125, 133, and 134; it did not read selector/design/control material and did
not run positive-budget science.  Its attempt to write the final artifact was
interrupted by an unrelated model safety filter, so the root process records the
already-returned numerical reproducer here without changing the frozen core.

## Frozen bytes verified by the auditor

- `code/rate_defined_tensor_f0.py`:
  `321f12aa8a5df44ca9c9162704cccd0f2c526abf9577832b4824538b0afdb8e5`
- `code/test_rate_defined_tensor_f0.py`:
  `f646ab3d545f698f225296baf774ae629776c17c2882b3f30d3a95cefa6bbd8d`
- `code/test_rate_defined_tensor_f0_round125_adversarial.py`:
  `b7cf8f152cc5dcf32af642bc1c109ce6d8b0d1a9f0833b1fa9fbf1e3652d0646`

The auditor independently observed 32/32 tests passing for the two frozen F0 test
modules, with Ruff and formatting checks passing, before adding its probe.

## Confirmed P0

`audit_matrix_free_propagation` checks the saved nominal state with
`isinstance(value, numpy.ndarray)` and later relies on NumPy equality dispatch.  A
strictly derived NumPy-array subtype can therefore alter equality dispatch while
carrying unrelated data.  The auditor supplied an all-zero saved nominal state in
such a subtype while leaving the remaining saved propagation fields coherent.

Observed result:

```text
genuine propagated nominal mass = 0.995012479192651
saved substituted nominal mass   = 0.0
audit_matrix_free_propagation     = returned normally
```

The downstream consumer did not repair the boundary.  It reran the same
dispatchable audit and then converted/consumed the zero state:

```text
enclose_matrix_free_jets order-0 scalar = 0.0
enclose_matrix_free_jets order-0 radius = 7.298327424002349e-14
```

Thus the saved-state replay can be bypassed inside the current in-memory API and a
false observable can enter the topology path.  This is claim-critical and is P0.

## Required repair family

1. Require exact built-in/dataclass types, not subclass acceptance, before invoking
   any NumPy operation or equality method on saved numerical objects.
2. Apply the same exact-type boundary to initial-law and kernel arrays and to all
   propagation/topology certificate containers and nested records.
3. Make canonical artifact parsing construct owned, plain C-contiguous `float64`
   arrays; reject object arrays, array subtypes, non-native layout, writable aliases,
   and unexpected containers before numerical replay.
4. Snapshot or make read-only every accepted array so audit-then-consume cannot see
   different bytes; the production verifier must run single-threaded from its own
   objects.
5. Add regressions proving that subtype/equality-dispatch substitution, mutable
   post-audit changes, and nested record subtypes all fail before jets.
6. Repeat a fresh frozen-hash black-box audit after the resource redesign, because
   that redesign will necessarily change the same data representations.

The bounded Round-133 arithmetic replay remains useful, but its previous acceptance
is superseded.  No F0, selector, attestation, resource, F1, or positive-budget gate
is released by this round.
