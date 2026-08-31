# Round 32 positive-B broad-four-slab pre-run attack

## Decision

**NO-GO.** P0: none. P1: three. P2: one. Do not start the N113/N129
held-out calculation until the P1 items are closed and the pinned hashes are
refrozen.

## Findings

### P1 — A legitimate scientific HOLD can fail before any JSON is written

`code/positive_b_broad_four_slab.py:808-832` assigns `math.inf` to agreement
metrics whenever either mesh does not have exactly five roots, two valley
ratios, or three event masses. `code/positive_b_broad_four_slab.py:108-112`
then serializes with `allow_nan=False`, which rejects those infinities. Thus a
held-out root-count/topology failure reaches the intended HOLD logic but
`main()` crashes at `code/positive_b_broad_four_slab.py:928` instead of
preserving the negative result artifact.

Required closure: use `null` for unavailable metrics with their gates set
explicitly false (or another finite, schema-declared representation), and add a
test that a wrong-topology pair writes canonical JSON with
`all_gates_passed=false`.

### P1 — The formal manifest validator is not fail-closed

`code/positive_b_broad_four_slab.py:764-797` freezes only a subset of the
manifest and accepts a missing required pin. Safe mutation probes confirmed
that all of the following pass `validate_manifest()`:

- changing `physical_parameters.contact_radius` from 0.16 to 0.17, even though
  `build_model()` consumes manifest parameters at
  `code/positive_b_broad_four_slab.py:258`;
- deleting the `tests` entry from `pinned_files`; and
- replacing `claim_scope` by `continuum theorem verified`, which is copied into
  the formal result at `code/positive_b_broad_four_slab.py:880`.

The same unchecked surface includes `known_before_freeze`, `selection_record`,
`preflight_validation`, `execution_boundary`, and `forbidden_promotions`
(`artifacts/data/positive_b_broad_four_slab_manifest.json:7-37,113-145,200-207`).
This can change the model, erase held-out provenance, weaken dependency pins,
or promote the claim without a validation failure.

Required closure: freeze the full scientific/provenance/claim contract, require
the exact pin-label set, and require every resolved pin path to remain under
the report directory. Add negative mutation tests for each class.

### P1 — The required two-complete-process byte-identity check is declared but not enforced

The protocol requires two complete formal processes to emit byte-identical
JSON at `notes/positive_b_broad_four_slab_protocol.md:115-118`, and the manifest
repeats the contract at
`artifacts/data/positive_b_broad_four_slab_manifest.json:127-137`. However,
`code/positive_b_broad_four_slab.py:927-928` performs one run and one write.
`code/test_positive_b_broad_four_slab.py:363-395` compares only two small-N
same-process binary probes, while `code/test_positive_b_broad_four_slab.py:480-489`
writes the same toy payload twice. Neither checks two complete processes.

Required closure: use a sequential formal wrapper that writes two independent
outputs, byte-compares them, and only then promotes the canonical result; retain
the comparison evidence without adding nondeterministic metadata.

### P2 — Positivity/monotonicity coverage stops short of the stated time horizon

The gate at `code/positive_b_broad_four_slab.py:700-710` checks root densities,
the final **survival**, and sampled survival increments only on the scan through
t=35 (`code/positive_b_broad_four_slab.py:446-449`). It does not record a
minimum sampled density and does not check `S(100) <= S(35)`, although the
protocol states positive density and survival monotonicity and propagates to
T=100 (`notes/positive_b_broad_four_slab_protocol.md:131-145`). Generator and
state-positivity gates reduce the risk, but the declared numerical gate is not
measured over the whole reported horizon.

Required closure: gate minimum sampled density on the intended interval and at
least check final survival against scan-end survival (or sample the tail).

## Checks that cleared

- Generator and adjoint orientation, vector/matrix actions, and analytic traces:
  implementation `code/positive_b_broad_four_slab.py:132-236`; explicit-CSR
  attack `code/test_positive_b_broad_four_slab.py:60-157`.
- Time jets and tangent jets: implementation
  `code/positive_b_broad_four_slab.py:273-277,342-370,559-625`; explicit and
  central-difference attacks `code/test_positive_b_broad_four_slab.py:160-281`.
- Chunk boundaries, saved left checkpoints, local root propagation, and direct
  reproduction: `code/positive_b_broad_four_slab.py:421-555` and
  `code/test_positive_b_broad_four_slab.py:284-332`.
- Event definitions at `code/positive_b_broad_four_slab.py:664-670` match the
  frozen three-basin definitions.
- Current producer/test/protocol SHA-256 values exactly match manifest lines
  149, 153, and 157; validation of every currently listed dependency passed.
- Current formal result artifact is absent. No N113/N129 or
  `--execute-frozen` command was run in this audit.

## Safe verification performed

- Targeted small-N pytest: **10 passed**.
- Ruff on producer and test: **passed**.
- Static/hash/mutation checks: **passed**, with the fail-open mutations above
  reproduced.

The four frozen inputs are currently untracked in Git. Before the held-out run,
the repaired manifest itself also needs an immutable pre-run anchor (normally a
commit or separately recorded manifest SHA-256); otherwise its internally
declared hashes do not protect the manifest from being edited alongside them.
