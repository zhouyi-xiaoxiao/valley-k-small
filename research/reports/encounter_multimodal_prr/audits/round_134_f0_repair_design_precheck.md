# Round 134: F0 saved-propagation and topology repair design precheck

Date: 2026-07-14  
Reviewer: independent repair-design auditor; no core/test edits  
Decision: **PASS REPAIR-DESIGN PRECHECK / READY FOR A FRESH BLACK-BOX ATTACK / HOLD FULL F0 ATTESTATION / NO F1**  
Core findings within this bounded repair: **P0 = 0, P1 = 0, P2 = 0**  
Open programme gates outside this bounded repair: **source/oracle attestation, independent implementation, and production resource feasibility**

## 1. Scope and non-science boundary

This round audited the fail-closed design and frozen implementation bytes for:

1. deterministic replay of a saved matrix-free uniformization propagation;
2. mandatory propagation replay before saved states enter the jet engine;
3. externally pinned full-window/root-band semantics;
4. fresh-oracle replay of all saved time tiles and Newton data; and
5. executable API call-site migration and mutation coverage.

No prospective selector value was read.  No positive installed budget, physical
positive-control killing field, F1 observable, modal result, or publication
claim was evaluated.  A pass here closes the Round-125 saved-object repair
design only; it is not an F0 artifact acceptance and cannot authorize F1.

## 2. Frozen bytes independently checked

| object | SHA-256 |
|---|---|
| `code/rate_defined_tensor_f0.py` | `321f12aa8a5df44ca9c9162704cccd0f2c526abf9577832b4824538b0afdb8e5` |
| `code/test_rate_defined_tensor_f0.py` | `f646ab3d545f698f225296baf774ae629776c17c2882b3f30d3a95cefa6bbd8d` |
| `code/test_rate_defined_tensor_f0_round125_adversarial.py` | `b7cf8f152cc5dcf32af642bc1c109ce6d8b0d1a9f0833b1fa9fbf1e3652d0646` |
| `code/verified_uniformization_enclosure.py` | `a4646f946b891133c972f62cd36a1cb177516793050c2b6e520cffceb57782ed` |
| `code/test_verified_uniformization_enclosure.py` | `6b842112f71bf88d8447a88ccba21ef1d9cbe89676912e80789e7ce964acbe34` |

The core changed during the early design review, so no conclusion in this
report is based on the earlier partial hashes.  The table above is the final
frozen target supplied after source and test edits stopped.

## 3. Independent executable replay

From the report root I ran:

```text
../../../.venv/bin/python -m pytest -q -rP \
  code/test_rate_defined_tensor_f0.py \
  code/test_rate_defined_tensor_f0_round125_adversarial.py \
  code/test_verified_uniformization_enclosure.py

44 passed
```

I also independently obtained:

```text
ruff check (the five frozen Python files)                 PASS
ruff format --check (core and its two F0 test files)      PASS
pytest -q code/test_text_control_character_hygiene.py     1 passed
```

The 44 tests include the two original Round-125 reject reproducers, exact
zero-time and multi-chunk propagation, every saved propagation/chunk field,
strict type mutations, semantic topology mutations, coherent interval-field
mutation, and a changed-oracle replay attack.

## 4. Saved propagation: complete fail-closed checklist

### 4.1 External contract, source objects, and schema

The auditor now requires, as keyword-only external inputs, all six quantities
that determine the numerical propagation:

```text
target_time
mean_cap
total_tail_tolerance
precision_bits
maximum_terms
maximum_chunks
```

It does not recover these values from the saved propagation.  The contract is
normalized by the same exact `Fraction`/strict-integer checks used by the
producer, and the chunk count is recomputed from `lambda * target_time` and
the externally supplied mean cap.  This closes the important coherent
"change the saved time and its self-reported settings together" route, as
long as the independent verifier obtains the six expected inputs from an
immutable manifest rather than from the artifact under test.

Before numerical replay the auditor:

- fully revalidates the rate-defined tensor kernel;
- fully revalidates the initial-state enclosure;
- requires the exact `MatrixFreePropagation`/tuple/NumPy schema;
- requires strict `Fraction`, built-in `int`, built-in `float`, and string
  types for the corresponding saved fields;
- binds the saved initial hash, exact mass cap, initial radius, construction
  tag, rate, and runtime tag to the supplied source objects; and
- binds target/elapsed time, all resource settings, chunk count, and chunk
  length to the external contract.

All 17 `MatrixFreePropagation` fields are therefore either externally bound,
recomputed, or compared to a deterministic replay:

```text
nominal, l1_error, exact_mass_cap, target_time, elapsed_time,
initial_source_sha256, initial_l1_error, kernel_construction,
rate_fraction, runtime_rounding_mode, mean_cap,
total_tail_tolerance, precision_bits, maximum_terms, maximum_chunks,
chunk_count, chunks.
```

### 4.2 Complete deterministic numerical replay

The saved auditor starts again from a copy of the validated initial nominal
vector and initial L1 radius.  For every expected chunk it independently
reexecutes the producer recurrence in the same frozen order:

1. form exact duration, exact Poisson mean, and exact allocated tail budget;
2. regenerate the directed-MPFR Poisson enclosure at the externally pinned
   precision and term cap;
3. initialize the accumulator, power, and error recurrences;
4. for every retained Poisson term recompute the L1 mass upper bound, weighted
   nominal accumulation, propagated state error, probability-weight error,
   and absolute accumulation ledger;
5. for every nonfinal power recompute the binary64 action-roundoff bound, the
   `delta_P` coefficient term, and the exact frozen matrix-free `Phat.T`
   action;
6. recompute accumulation gamma, subnormal allowance, tail error, and final
   chunk output radius;
7. compare the regenerated chunk against every saved chunk field; and
8. feed the regenerated nominal state and radius, not a saved intermediate,
   into the next chunk.

All 13 `MatrixFreeChunkLedger` fields are checked exactly:

```text
duration, mean, allocated_tail_tolerance, terms, poisson_tail_upper,
precision_bits, maximum_terms_cap, roundoff_gamma_index, delta_p_used,
propagated_power_error, weight_error, accumulation_roundoff,
output_l1_error.
```

Finally the auditor requires exact time closure, strict float64 final-state
schema, finite/nonnegative state and radius, `np.array_equal` with the
regenerated state, and exact equality with the regenerated final radius.  The
Round-125 all-zero nominal/all-zero error forgery is therefore rejected for a
numerical reason, not merely because more self-reported scalar fields were
added.

`weighted_power_error`, `tail_error`, and `absolute_accumulation` are not
separate saved dataclass fields.  This is not an authentication gap: each is
regenerated and contributes to the exactly compared output radius.  Saving
them later could improve human ledger transparency, but it is not required to
close the Round-125 mutation.

### 4.3 Jet-consumer boundary

`enclose_matrix_free_jets` now requires the validated initial enclosure and
the same six external contract values, invokes the complete propagation audit
first, and only then copies the saved state for generator actions.  The
absolute-time oracle passes its own exact requested time and frozen numerical
settings through this API.  Thus there is no remaining executable call path
in which a saved propagation can enter the jet engine after only a structural
self-consistency check.

## 5. Saved topology: complete fail-closed checklist

### 5.1 External topology contract

The generic saved-topology auditor now requires:

```text
oracle
expected_window_lower
expected_window_upper
expected_root_bands
expected_initial_derivative_sign
```

The expected window is exact and nonnegative.  The expected initial sign is a
strict integer in `{-1,+1}`.  Every external band has strict string/Fraction
schema, lies inside the window, is ordered and nonoverlapping, and has a
quarter-grid endpoint.  Starting from the external initial sign, the auditor
requires alternating `maximum/minimum` kinds and canonical `P1,Q1,P2,...`
role numbering.  The saved certificate's window, sign, fixed algorithmic
limits, root count, coverage flags, science-boundary flags, tuple schema, and
strict scalar types are then compared against that contract.

The physical wrapper separately pins `[1/2,35]`, initial sign `+1`, and the
immutable `physical_root_bands_v2(control_id)` table.  It never infers a role
band from an observed curve.

### 5.2 Full coverage and fresh tile replay

For every saved tile the auditor verifies:

- exact adjacency from the external window lower endpoint to upper endpoint;
- positive width, strict integer depth in `[0,20]`, and the exact
  `1/(4*2^depth)` dyadic width;
- strict Boolean candidate status and derivative sign in `{-1,0,+1}`;
- exact intersection of the two saved derivative consequences and of the two
  saved curvature consequences; and
- equality of all saved local intervals with a fresh `enclose_time_tile`
  call to the supplied oracle at the saved absolute time and depth.

A candidate must contain zero in the derivative, have strict nonzero
curvature, and be no wider than `1/40`; a noncandidate must have strict
derivative sign.  Contiguous candidate components are reconstructed from the
tile sequence, and their count must equal the externally pinned band/root
count.

### 5.3 Extrema semantics, alternation, and root bands

For each candidate component, root, and external band in strict order, the
auditor checks:

- exact role, kind, band endpoints, and candidate-cluster endpoints;
- strict containment of the cluster in its external band;
- `required_curvature_sign = -current_complement_sign`;
- `maximum <=> required_curvature_sign == -1` and
  `minimum <=> required_curvature_sign == +1`;
- that every candidate tile has that same curvature sign;
- that every noncandidate tile before and after successive components has the
  expected alternating derivative sign; and
- strict ordering of final root intervals.

This closes the Round-125 mutations of initial sign, role, and kind and also
prevents an arbitrary root label from being attached to a valid Newton trace.

### 5.4 Fresh Newton replay

Every saved root and Newton step receives strict schema checks.  The auditor
then freshly calls the oracle at every recomputed binary64 midpoint and
freshly recomputes the curvature enclosure on every current input interval.
It compares the saved midpoint derivative and curvature, recomputes division,
Newton image, interval intersection, interior-inclusion Boolean, and the
entire chained output interval.  At least one interior inclusion is required,
the final width is capped, and final curvature is freshly replayed once more.

Consequently a coherent edit of the local derivative/Taylor fields or Newton
fields cannot pass merely by preserving internal arithmetic identities.

## 6. Executable API call-site audit

A repository-wide search over executable Python found no stale old-signature
call site.  The migrated call graph is:

```text
propagate_matrix_free_absolute
  -> audit_matrix_free_propagation(external six-field contract)

MatrixFreeAbsoluteTimeJetOracle
  -> propagate_matrix_free_absolute
  -> enclose_matrix_free_jets(initial + external six-field contract)
  -> audit_matrix_free_propagation

certify_full_window_topology
  -> audit_full_window_topology(oracle + external window/bands/sign)

audit_physical_full_window_topology_v2
  -> audit_full_window_topology(oracle + immutable physical contract)
```

All direct calls in the main F0 tests and the Round-125 adversarial tests use
the new required arguments.  Historical audit prose containing the old call
shape remains historical evidence and is not executable.

## 7. Non-negotiable boundaries for the next attestation/verifier round

The repaired core verifies a saved object **relative to the supplied kernel,
initial enclosure, external contract, and oracle**.  It cannot by itself
authenticate who supplied those objects.  The forthcoming append-only F0
schema and independent verifier must therefore enforce all of the following:

1. **Oracle identity:** the production verifier must construct the
   `MatrixFreeAbsoluteTimeJetOracle` itself from pinned inputs.  It must never
   deserialize or trust an arbitrary callable supplied with a certificate.
   The generic callable API is appropriate for synthetic tests only.
2. **Source identity:** pin the external initial-law bytes and SHA-256, the
   geometry/killing inputs, kernel specification, all six propagation
   settings, the physical control role, and the external topology contract.
   A coherent alternative valid kernel/initial object is not rejected unless
   the verifier knows which object was required.
3. **Implementation identity:** pin the core and directed-uniformization
   hashes above plus the independent verifier hash.  Same-module replay is an
   excellent saved-mutation defense, but it is not an independent proof
   against a systematic bug shared by producer and replay code.
4. **Runtime identity:** record Python, NumPy/SciPy, gmpy2/MPFR, platform,
   IEEE-binary64/rounding-mode checks, and process command.  Exact nominal
   byte equality is intentionally stricter than interval overlap and may be
   environment-sensitive.
5. **Artifact identity:** use canonical schema bytes, append-only hashes, and
   a verifier that reads expected values from the immutable manifest rather
   than from the payload it is verifying.
6. **No authority leakage:** a method-only or synthetic PASS must retain
   `prospective_control_values_read=false` and
   `positive_budget_primary_control_evaluated=false` and cannot be promoted
   into an F1 row.

## 8. Resource warning before production

The strong design intentionally repeats work.  In the current direct oracle
path, one time sample performs the propagation, the producer's full replay,
and the jet consumer's full replay.  Topology construction then performs a
fresh full topology audit, including all tile and Newton oracle calls.  This
is correct but can multiply production CPU and memory pressure substantially.

No result in this round establishes feasibility for the 7,165,305-state
physical row, one complete topology certificate, two independent replicas,
or the 36-row campaign.  Before any positive-budget run, the resource gate
must measure at least one largest-shape killed kernel, one absolute-time
propagation including all replay passes, and a representative topology audit.
Caching or a compact verified representation may be introduced only with a
new hash and a new adversarial review; it may not weaken the saved-state
replay boundary silently.

## 9. Required fresh black-box attack matrix

Before the bounded repair can become part of an accepted F0 artifact, a new
reviewer should independently attack, at minimum:

### Propagation

- every top-level field and every field of an early, middle, and last chunk;
- final nominal bytes, dtype, shape, and radius;
- zero-time, one-chunk, and multi-chunk recurrence continuity;
- each of the six external contract values independently;
- mismatched or coherently altered initial/kernel objects against immutable
  expected source hashes; and
- runtime/precision/term/chunk-cap failure paths.

### Topology

- external window, initial sign, role, kind, band endpoint, ordering, and
  quarter-grid mutations;
- coverage gap/overlap, depth/width, candidate flag, derivative sign,
  candidate curvature, and complement-sign alternation;
- candidate-component split/merge/reordering and root-band reassignment;
- every Newton field, inclusion Boolean, final interval, and final curvature;
- a coherently edited tile interval ledger with the original oracle;
- the original certificate with a changed oracle; and
- the physical wrapper with a verifier-constructed oracle and externally
  pinned `control_id`.

## 10. Conclusion

The frozen repair implements the correct closure pattern: complete
deterministic propagation replay from an external numerical contract,
mandatory replay before jets, external root-band/role semantics, full-window
sign alternation, candidate-curvature binding, and fresh oracle replay of
tiles and interval Newton traces.  I found no omitted saved field or producer
operation that would preserve the Round-125 forged-state or forged-semantics
attack.

The correct next step is a different reviewer's black-box attack, followed by
the append-only external-source/oracle attestation and largest-shape resource
gate.  It is not a positive-control run and it is not F1.
