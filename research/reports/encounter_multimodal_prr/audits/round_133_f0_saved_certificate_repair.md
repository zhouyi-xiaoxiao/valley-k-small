# Round 133: F0 saved-certificate repair

Date: 2026-07-14

Decision: `PASS_LOCAL_REPAIR / HOLD_INDEPENDENT_ATTACK`

This round repairs the two release-blocking findings reproduced in Round 125.  It is
method-only work.  No prospective positive-budget control was read or evaluated, and
this report does not authorize F1.

## Frozen objects

- `code/rate_defined_tensor_f0.py`
  - pre-repair partial-edit SHA-256:
    `971e12fb9742ea93cec03ab4f3286f88143e1f0551d748aae67cb4dd4f5be431`
  - repaired SHA-256:
    `321f12aa8a5df44ca9c9162704cccd0f2c526abf9577832b4824538b0afdb8e5`
- `code/test_rate_defined_tensor_f0.py`
  - repaired SHA-256:
    `f646ab3d545f698f225296baf774ae629776c17c2882b3f30d3a95cefa6bbd8d`
- `code/test_rate_defined_tensor_f0_round125_adversarial.py`
  - repaired SHA-256:
    `b7cf8f152cc5dcf32af642bc1c109ce6d8b0d1a9f0833b1fa9fbf1e3652d0646`

## P0 propagation repair

`audit_matrix_free_propagation` now requires six external contract values: target
time, mean cap, total tail tolerance, MPFR precision, term cap, and chunk cap.  It
validates the kernel and initial enclosure, checks strict saved-field types, derives
the chunk count from the external contract, and then recomputes every Poisson weight
enclosure, every matrix-free power, every directed roundoff/error term, every chunk
ledger field, the final nominal vector, and the final radius.  The nominal vector is
compared bit for bit with `numpy.array_equal`.

`enclose_matrix_free_jets` now requires the initial enclosure and the same six
external values and runs the complete propagation audit before consuming a saved
state.  A coherent all-zero state/error forgery is rejected.

The mutation matrix covers all top-level contract/identity/output fields and all 13
chunk-ledger fields, including NumPy scalar and container type substitutions.  Zero
time and genuine multi-chunk paths are both replayed.

## P1 topology repair

`audit_full_window_topology` now requires an external window, ordered root bands,
initial derivative sign, and an absolute-time oracle.  It binds roles, kinds, band
bounds, alternation, candidate curvature, complement signs, strict schema types,
dyadic tile geometry, candidate widths, coverage, root ordering, and every Newton
step to the external contract.

The auditor also freshly calls the supplied oracle for every saved tile, Newton
midpoint, Newton input curvature interval, and final root curvature interval.  Thus a
coherently altered interval ledger or a different oracle is rejected rather than
passing merely because its saved fields agree with one another.

`audit_physical_full_window_topology_v2` pins the physical `[1/2,35]` window and the
predeclared v2 role bands.  A future production verifier must construct its oracle
itself from pinned kernel, initial-law, and propagation-contract objects; an arbitrary
artifact-supplied callable is not an authority.

## Reproduction

From `research/reports/encounter_multimodal_prr`:

```text
../../../.venv/bin/python -m ruff format --check \
  code/rate_defined_tensor_f0.py \
  code/test_rate_defined_tensor_f0.py \
  code/test_rate_defined_tensor_f0_round125_adversarial.py

../../../.venv/bin/python -m ruff check \
  code/rate_defined_tensor_f0.py \
  code/test_rate_defined_tensor_f0.py \
  code/test_rate_defined_tensor_f0_round125_adversarial.py

../../../.venv/bin/python -m pytest -q \
  code/test_rate_defined_tensor_f0.py \
  code/test_rate_defined_tensor_f0_round125_adversarial.py \
  code/test_verified_uniformization_enclosure.py
```

Observed: formatting and Ruff passed; pytest reported `44 passed`.

`../../../.venv/bin/python -m pytest -q code/test_text_control_character_hygiene.py`
also passed.

## Remaining gates

1. A different agent must attack the frozen hashes above and reproduce the complete
   suite before this repair is accepted.
2. The full physical resource path remains unresolved.  The safe path currently
   computes the propagation once, replays it in the producer audit, and replays it
   again before jets.  This three-pass cost must be measured rather than hidden.
3. Append-only attestation, schema parsing, and a verifier that independently
   constructs the physical oracle remain separate F0 requirements.
4. F1 remains forbidden until those gates and the selector independent audit pass.
