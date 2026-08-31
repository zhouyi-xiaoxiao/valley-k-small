# Round 35 positive-B broad-four-slab pre-run resolution

Date: 2026-07-13

## Decision

**GO for the separately controlled frozen held-out run.** P0: 0. P1: 0.
P2: 0.

This is only a pre-run authorization for the fixed `N=113` and `N=129` calculation.
It is not a scientific PASS, a continuum or unbounded-domain result, an
independent-solver confirmation, or a project/publication gate.

The only valid external manifest anchor for the next run is

```text
01b435c834cec9e7bfde2069b19fcdcaa4e06178ccfe0d4b6082f0705dfd5805
```

The earlier anchor
`648de30d12258485b4285862c105fc9a5d524d70a3e27268e5a471d86ff08ba7`
is retired and must not be used.

## Scope and execution boundary

This re-audit covered exactly the producer, its 15-test suite, the protocol,
the manifest, and the parent Round 32 audit. The safe verification described
below did not invoke either formal execution mode or complete either held-out
mesh. A separate aborted coordinated launch is disclosed next.

During the coordinated repair, the parent operator reported that a command
using the retired anchor was launched for approximately one second and then
interrupted with `SIGINT`. It was stopped before any metric or output was
produced. A post-event namespace check found no canonical result,
reproducibility record, replica output, staging file, or backup file. This
aborted pre-output launch is not scientific evidence and does not consume the
held-out calculation.

## Frozen-file anchors

| Role | SHA-256 |
|---|---|
| producer | `0c70ffb4a9034772928e2fa95d2ca79ef33754e5aa4157a2f101e15cb312b003` |
| tests | `ee784d1cf6cc4e7ee66968deb8f3421394f697eebee3a50f783533aa469a8f78` |
| protocol | `f25a8107d7a975342a3b1cbbf84c29df26654a8f6310f0429cba5ffdf7bcda00` |
| manifest | `01b435c834cec9e7bfde2069b19fcdcaa4e06178ccfe0d4b6082f0705dfd5805` |

`validate_manifest()` accepted the exact manifest and verified all 13 pinned
roles against their live file hashes.

## Round 32 closure

### Null-safe structural HOLD — closed

The producer computes the peak ratio, both valley ratios, and three event
masses only for the exact
`maximum-minimum-maximum-minimum-maximum` topology
(`positive_b_broad_four_slab.py:905-929`). Otherwise these values remain JSON
`null`, and the corresponding mesh and cross-mesh gates fail explicitly
(`:933-1002`, `:1106-1201`). Undefined basin sums are also `null`. Recursive
finite-number validation and canonical `allow_nan=False` serialization reject
all NaN and infinity values before writing (`:232-258`). The malformed and
wrong-topology regression cases write byte-stable finite HOLD JSON.

### Full manifest and pin closure — closed

The validator requires the exact top-level key set and recursively exact types
and values for the scientific parameters, provenance, selection record, claim
scope, thresholds, preflight declarations, reproducibility contract, execution
boundary, negative claim flags, and forbidden promotions (`:1036-1066`).

It also requires the exact 13 pin roles and exact role-to-path mapping, rejects
duplicate paths, absolute paths, parent traversal, malformed/non-lowercase
hashes, non-files, and resolved paths outside the report root, and verifies the
live SHA-256 of every pin (`:1068-1103`). The standard mutation suite passed;
an additional temporary symlink-escape probe was rejected. The manifest itself
is protected by the external anchor above rather than a self-referential pin.

### Two-fresh-process harness and caught-failure preservation — closed

The public entry constructs two distinct replica outputs and two
`sys.executable` commands (`:1264-1269`, `:1423-1451`). Synchronous
`subprocess.run(..., check=False)` calls execute them sequentially and accept a
scientific HOLD exit code of 2 (`:1319-1335`). Before promotion, the driver
checks raw-byte identity, canonical finite JSON, PASS/HOLD status, exit-code
consistency, result manifest hash, and an unchanged on-disk manifest
(`:1336-1361`). It stages deterministic evidence before making the canonical
result the commit marker (`:1363-1389`).

The permanent tests observed two fresh PIDs for identical HOLD and PASS cases,
promoted both only after byte identity, and preserved prior canonical/evidence
sentinels on mismatch. Additional safe temporary probes confirmed preservation
for an abnormal replica exit, a missing output, and a HOLD/exit-code mismatch.

The initial static audit identified one P2 wording defect: the old protocol's
blanket word “crash” could be read as claiming hard `SIGKILL` or power-loss
atomicity across two file replacements. The final protocol now precisely limits
byte-for-byte preservation to detected replica errors and caught process or
filesystem exceptions, expressly disclaims hard-crash consistency, and
requires downstream comparison of the reproducibility record's canonical hash
with the observed canonical result
(`positive_b_broad_four_slab_protocol.md:130-146`). This closes the P2 without
changing any scientific code or gate.

### Tail gates through `t=100` — closed

The scan records minimum sampled density from `t=0.5`, adjacent sampled
survival increases, minimum state, and differential mass balance through
`t=35` (`positive_b_broad_four_slab.py:535-673`). Sequential tail propagation
at the frozen `35,50,75,100` checkpoints records density, survival, minimum
state, and mass balance, including `S(35)-S(100)` and the maximum adjacent
survival increase (`:799-873`). The mesh gates combine scan and tail density,
survival monotonicity, state positivity, and mass-balance checks (`:876-885`,
`:961-988`). Small-`N` direct `expm_multiply` checks and injected negative
density, survival-increase, and negative-state mutations passed.

### Exact valley definition — closed

For each minimum, the producer computes

```text
valley density / min(left adjacent peak density, right adjacent peak density)
```

at `positive_b_broad_four_slab.py:915-922`, exactly matching the frozen
valley-to-smaller-adjacent-peak definition.

## Safe verification

- `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -q -ra -p no:cacheprovider research/reports/encounter_multimodal_prr/code/test_positive_b_broad_four_slab.py`
  — **15 passed, 0 skipped**.
- `.venv/bin/ruff check` on the producer and test — passed.
- In-memory Python compilation of both Python files — passed.
- JSON parsing, exact manifest validation, all 13 live pin hashes, and the
  external manifest SHA-256 — passed.
- Safe temporary mutation probes for symlink escape and replica abnormal-exit,
  missing-output, and inconsistent-exit preservation — passed.
- Post-check artifact namespace — only
  `positive_b_broad_four_slab_manifest.json` exists; no result or execution
  residue exists.

## Remaining run conditions

The next operator must use the public `--execute-frozen` entry with the exact
current external anchor. Any hash change invalidates this GO and requires a new
pre-run audit. After execution, downstream use must verify that the
reproducibility record's `canonical_result_sha256` matches the observed
canonical result bytes. All negative claim flags and protocol limitations
remain binding regardless of PASS or HOLD.
