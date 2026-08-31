# Round 137: root-process control-blindness boundary

Date: 2026-07-14

Decision: `ROOT PROCESS PERMANENTLY NOT AUTHORIZED FOR F1`

## Event

After the Round 133 F0 repair had been frozen and after the Round 135 selector
repair had been delegated, the root process ran a broad read-only resource search.
The output unintentionally included lines from historical positive-control design
notes.  No positive-budget model evaluation, propagation, topology computation, or
scientific selection was run.

This is recorded as a provenance boundary rather than silently treating the root
process as still control-blind.

## Objects frozen before the boundary

- F0 core SHA-256:
  `321f12aa8a5df44ca9c9162704cccd0f2c526abf9577832b4824538b0afdb8e5`
- F0 main-test SHA-256:
  `f646ab3d545f698f225296baf774ae629776c17c2882b3f30d3a95cefa6bbd8d`
- Round-125 adversarial-test SHA-256:
  `b7cf8f152cc5dcf32af642bc1c109ce6d8b0d1a9f0833b1fa9fbf1e3652d0646`
- Selector-v2 source audited in Round 131 SHA-256:
  `b6be1efa755659fac62143779690ae2cf67f06c8ea7c4eacfaf90db971862bc8`

The selector Round-131 repair agent was launched before this boundary.  The fresh
F0 black-box agent was launched afterward with no conversation fork and with an
explicit prohibition on reading control/design notes.

## Fail-closed consequence

1. The current root process may inspect method, tests, resource behavior, and audit
   reports, but may not edit the frozen F0/selector scientific path or execute F1.
2. Any further source repair must be performed by a narrowly scoped clean agent and
   followed by a new independent frozen-hash audit.
3. The eventual F1 executable must start in a clean process, verify pinned source,
   input, runtime, initial-law, kernel, selector, and contract hashes before reading
   authorized controls, and construct the physical oracle itself.
4. The clean runner must emit an append-only attestation proving that no pre-read
   exploratory result could alter code, bands, acceptance rules, or resource caps.
5. Until that runner and the largest-shape resource gate pass, the only valid status
   is `HOLD F1 / HOLD positive-B`.
