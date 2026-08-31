# Round 8 audit: neutral symbolic bridge contract fixture

Date: 2026-07-17

Status: **NEUTRAL EXACT-RATIONAL CONTRACT FIXTURE PASS / FORMAL PRODUCTION
CANDIDATE ABSENT / ACCEPTANCE RECEIPT ABSENT / COMPLETE C0--C3 FALSE**

## 1. Audited object and strict scope

Round 8 implements only the control-free, result-blind schema and algebra
fixture needed before a production gauge/killing bridge could be attempted.
It does not materialize either reserved formal object:

```text
encounter_c1_gauge_killing_symbolic_candidate_v1
encounter_c1_gauge_killing_symbolic_acceptance_receipt_v1
```

The report tree contains no file with either basename.  The eleven required
production payload roles are listed but unbound.  There is no control source,
budget source, result, production centre, geometry evidence, correlated ideal
member, evaluator enclosure, or science execution in this fixture.

This boundary is substantive.  Interval overlap of independently rounded
primitives is not evidence that one correlated ideal refinement member exists,
and the discrete killing diagonal `k=B*V` is not the reconstructed multiplier
`B*K`, where `K=V/rho`.

## 2. Final ten-file closure

| role | path | SHA-256 |
|---|---|---|
| neutral source | `artifacts/data/continuum_c1_symbolic_bridge_neutral_source_v1.json` | `2d038789cef7e863d45775d51fda0023e6082e22228be5314edc3b9185a6b6b6` |
| outer manifest | `artifacts/data/continuum_c1_symbolic_bridge_neutral_outer_manifest_v1.json` | `c196209e09cb7f0d4f51208e2f5c6173d201762bbd73f217110b8604c41158f1` |
| externally pinned operation model | `code/continuum_c1_symbolic_bridge_neutral_operation_model_v1.json` | `0870dd15d1b76933f87761368cb801e8ec186c50472f7686ce11f0d9ab9dee15` |
| canonical fixture | `artifacts/data/continuum_c1_symbolic_bridge_neutral_fixture_v1.json` | `2aa8facd4f820ae4d28af9eadb4acf095e64f68d3742c4816d9f02337413ebee` |
| builder | `code/build_continuum_c1_symbolic_bridge_neutral_fixture_v1.py` | `27a3ed5b4c1066a590463ad43f68bebb60362780edd05903309848b4a0f76718` |
| independent validator | `code/validate_continuum_c1_symbolic_bridge_neutral_fixture_v1.py` | `727ec3bb18a22e098b3e977fbfa17a3be14f09b54ccc707433f7ba559e35523d` |
| static/two-build test | `code/test_continuum_c1_symbolic_bridge_neutral_fixture_v1.py` | `88ea2b30061856761c3be057ecfb47c565a7a46afb5c46532384145d9d51cdbc` |
| mutation test | `code/test_continuum_c1_symbolic_bridge_neutral_fixture_mutations_v1.py` | `faabae1c29889f7d0703c63eae860089b19b92a1086bc8d008f2bf5a84ac0284` |
| eight-core-file currentness manifest | `artifacts/data/continuum_c1_symbolic_bridge_neutral_fixture_currentness_v1.json` | `6ad86a1b187f39cfdb0baba7f958e30a6a72fdc639a219234565c344629e130b` |
| currentness gate | `code/test_continuum_c1_symbolic_bridge_neutral_fixture_currentness_v1.py` | `807065b1e90dcc7fdd2229466648abdc0e5e706477b0f42e8abe4a918d492d89` |

The currentness manifest pins the first eight roles in exactly the table order.
It does not attempt a self-referential hash of itself or the gate; the later
handoff sidecar is responsible for freezing those two delivery bytes.

## 3. Exact neutral witnesses

Builder and independent validator separately reconstruct four rational facts:

1. The neutral global gauge is

   ```text
   G=(1/2)/(1*1*2)=1/4,
   ```

   giving two gauged cell masses `1/4` and exact mass residual zero.

2. The forward and reverse fluxes agree exactly,

   ```text
   2*(3/5)=3*(2/5)=6/5,
   ```

   and the neutral tensor conductance is

   ```text
   (1/7)*(6/5)*5=6/7.
   ```

3. With `M_pi=3/10`, `pi_h=1/4`, and `V=2/5`,

   ```text
   rho=M_pi/pi_h=6/5,
   K=V/rho=1/3,
   M_pi*K=pi_h*V=1/10.
   ```

4. Positive interval division gives

   ```text
   [3/10,31/100] / [1/4,13/50] = [15/13,31/25].
   ```

These are algebra sanity witnesses only.  They neither bind a production
configuration nor show that arbitrary Cartesian interval choices form one
model.

## 4. Provenance and open-ledger boundary

The operation-model SHA must be supplied externally on every builder and
validator invocation.  It pins the builder, design authority, independent
validator, and neutral outer manifest, and it declares an empty verifier
dependency closure.  The manifest selects only the neutral source and contains
no DAG edge, control, budget, result, scratch, root, propagation, or topology
payload.

Every selected report input is opened descriptor-relative, component by
component, with no-follow semantics and pre/post descriptor/name checks.  The
builder records exactly six explicit construction snapshots:

```text
operation model + builder + Round-6 design + validator + outer manifest + source
```

The artifact deliberately says

```text
explicit_snapshot_counter_union_exact       = true
complete_process_report_file_open_closure   = false
prebootstrap_runtime_or_import_opens_traced = false
```

Thus it does not confuse its explicit construction snapshots with a complete
trace of interpreter or import activity.  Output uses a same-directory
exclusive temporary file, fsync, atomic no-overwrite linking, directory fsync,
and no output reread.  `--check` computes the expected canonical artifact hash
without opening the output path.

## 5. Executable verification

The final bytes pass:

```text
builder --check                  PASS / OUTPUT_NOT_OPENED
independent validator           PASS
static and two-build suite       5/5 PASS
adversarial mutation suite      46/46 PASS
eight-core-file currentness      8/8 PASS
```

The counted total is `59/59`, plus the two direct entry-point passes.  The
mutation suite rejects altered identities, claim promotion, bool/int/float
aliases, duplicate JSON keys, non-NFC content, stale descriptor hashes,
manifest self-authorization, control/budget/result role insertion, path
escape, dependency-closure drift, external operation-model hash mismatch, and
attempts to use either reserved formal output basename.

The independent validator does not import or call the builder.  It separately
recomputes descriptor hashes, the domain-separated native-record digest, all
four rational witnesses, the six-snapshot ledger, and the complete expected
artifact.

## 6. Adversarial repair chronology

The first design was not accepted.  Pre-implementation attacks required an
external operation-model trust anchor, replacement of a false full-process
open claim by the honest explicit-snapshot ledger, pollution-path bans over
all construction inputs, a fixed neutral-only output basename, an explicit
empty verifier dependency closure, and a validator-owned expected-artifact
reconstruction rather than reverse self-authorization.  Those conditions were
implemented before the canonical artifact was frozen.

After the first ten-file freeze, a read-only reproducibility audit found one
P1 in the currentness gate.  The original gate could read an old inode while a
live OneDrive name was concurrently replaced because it did not retain parent
directory descriptors or recheck the named target after reading.  The final
gate at SHA `807065...d492d89` repairs this with mandatory `O_DIRECTORY` and
`O_NOFOLLOW`, descriptor-relative traversal, retained parent descriptors,
single-hard-link regular-file checks, and pre/open/post/live-name comparisons
of device, inode, mode, link count, size, mtime, and ctime.  The finding was
then retested by its original auditor and closed.

On the final repaired bytes, the two independent read-only audit lines are:

```text
mathematics and scope:    P0=0 / P1=0 / P2=0
byte reproducibility:     P0=0 / P1=0 / P2=0
```

These are local hash-specific adversarial reviews, not external referee
acceptance.

## 7. Honest decision and next obligations

Round 8 establishes a neutral exact-rational schema/fixture and a reproducible
way to reject false promotion.  It does not establish the formal symbolic
machine contract, an independent symbolic acceptance receipt, a same-member
production application, or any continuum rate.  The following remain false:

```text
production payload roles 1--11 bound                 = false
one correlated distinguished ideal member contained = false
formal symbolic candidate materialized               = false
symbolic acceptance receipt materialized             = false
end-to-end evaluator enclosure                        = false
complete C0                                           = false
complete C1                                           = false
complete C2                                           = false
complete C3                                           = false
release/submission/science execution                  = false
```

The production branch may advance only after independent sources bind all
eleven roles and prove one correlated member without reading controls or
budgets into the symbolic acceptance stage.  Separately, the continuum branch
must repair or replace QF2, prove a quantitative complex-sector resolvent
estimate, and keep `E_space`, `E_eval`, and `E_box` in disjoint ledgers.

The theorem-first manuscript remains unchanged at seven main pages plus
twenty-four Supplemental pages.  Round 8 is a research-contract successor; it
does not add manuscript pages or promote release eligibility.
