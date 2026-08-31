# Round 161: hash-specific independent attack on the packed rate action

Date: 2026-07-14

Decision: **ACCEPT EXACT HASHES AS A BOUNDED METHOD PRIMITIVE / P0 = 0 /
P1 = 0 / P2 = 0 WITHIN SCOPE / HOLD F0 / NO F1 / HOLD PRR**

This was an independent, read-only numerical and source attack on the current
packed rate-action bytes.  It supersedes the stale-byte concern left after
Round 159: that round inspected an older producer hash, whereas this audit
recomputed and attacked the exact current hashes below.  No file was edited by
the independent auditor.  No network, remote service, authentication
protocol, positive-budget input, F1 row, Monte Carlo calculation, or
production-size state space was used.

The accepted object remains a same-process, array-bearing, science-free method
primitive.  It is not an authoritative recurrence result and it is not an F0
certificate.

## Frozen inputs

| Object | SHA-256 |
| --- | --- |
| `code/rate_defined_tensor_f0_packed_rate_action.py` | `7c1586e54bac2008ac910d5c2b910cee5206dab8c19948f5b5857db6563813c9` |
| `code/test_rate_defined_tensor_f0_packed_rate_action.py` | `b5127aa26ab3179986b5ad5cafbcae55c3dd6768217a2b500ea496f1f833939f` |
| `code/rate_defined_tensor_f0_packed.py` | `447aa3bc224685ea1cc556d9d322dafba05ef148945d4ae41291f83e29f3deb4` |
| `code/rate_defined_tensor_f0_packed_interval_action.py` | `2f3201a9eb1b6fbe577b43c3b046ad5f7f369816a7d4a32f4381506e63494f2a` |

The report tree is not presently a clean tracked release object, so the
complete hashes above, rather than filenames or working-tree status alone,
are the continuation authority for this decision.

## Mathematical enclosure checked

For a centre vector `c` with published \(\ell_1\) radius \(e\), the producer
first bounds \(m=\lVert c\rVert_1\) and the outward-rounding error \(a\) of the
centre action.  With fixed whole-box uniformization rate and subordinate
matrix radii \(\delta_P,\delta_Q\), it publishes

\[
 e_P^+ = e + \delta_P m + a,
 \qquad
 e_Q^+ = (\lVert\widehat Q\rVert_\infty+\delta_Q)e
          + \delta_Q m + a.
\]

The first inequality uses nonnegative substochastic \(P\), hence
\(\lVert P^T h\rVert_1\leq\lVert h\rVert_1\).  The second uses
\(\lVert Q\rVert_\infty\leq
\lVert\widehat Q\rVert_\infty+\delta_Q\).  The implementation performs each
nonnegative reduction and radius operation with explicit upward binary64
rounding and fails closed on non-finite intermediates.

The independent audit also confirmed that the stage-1 kernel chooses one
uniformization rate from the entire rate box, couples each selected outgoing
rate and killing value to the corresponding diagonal and `P` self
coefficient, and accumulates coincident forward/backward periodic-size-2
edges rather than overwriting them.  A rate endpoint is selected once per
`(direction, axis, coordinate)` and reused across all tensor rows, so the
oracle attacks the intended globally coupled uncertainty set rather than a
larger row-wise box.

## Independent attacks and observed results

The saved project suite passed:

```text
.venv/bin/python -m pytest -q \
  research/reports/encounter_multimodal_prr/code/test_rate_defined_tensor_f0_packed_rate_action.py

59 passed
```

A separate read-only harness then checked:

| Attack | Coverage | Result |
| --- | ---: | --- |
| fully uncertain periodic-size-2 rate box | 64 globally coupled vertices | PASS |
| point-plus-ball `P`/`Q` enclosures | 640 exact containment checks | PASS |
| directed binary64 rounding | 250 independent `Fraction` comparisons | PASS |
| one-ULP-too-small fixed \(\lambda\) | explicit rejection | PASS |
| addition and multiplication overflow | stable fail-closed result | PASS |

After the fixed-\(\lambda\) construction, the action is affine in the rate
parameters.  The norm of the difference is convex, so the globally coupled
rate-box vertices together with the \(\ell_1\)-ball extreme points cover the
interior for this bounded one-step enclosure.

The resource ledger was recomputed independently.  Its exact claim is a
simultaneously-live numerical payload upper bound, not a Python allocator,
RSS, swap, or wall-time proof.  A worst supported-dimension subordinate JSON
stress case used at most `39,528` encoded bytes; its simultaneous text plus
encoded estimate was `79,056 <= 131,072`, leaving `52,016` bytes.  The caller's
pre-owned arrays and kernel remain outside that ledger, as the source states.

## Why F0 remains held

The accepted bytes force the public boundary

```text
authoritative = false
fresh_process = false
science_executed = false
f0_pass = false
```

They do not propagate a time-dependent state, evaluate a Poisson tail or
generator jet, classify stationary topology over a time window, run an
independent full recurrence, or establish the largest-shape RSS/time gate.
They did not read a prospective control or positive budget.  Consequently,
this round closes only the current-hash composition concern.  It does not
close F0, authorize F1, provide a continuum result, or change the manuscript's
release status.

## Next admissible step

The next numerical step may use these exact hashes to build a tiny,
science-free packed uniformization/Poisson recurrence with conservative tail
and resource accounting.  That new layer must be independently attacked on
its own hashes before any production-size promotion.  Rate-interval
composition, repeated-step radius propagation, jets, topology, production
resources, and independent replay remain separate fail-closed gates.
