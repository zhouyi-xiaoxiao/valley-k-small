# Round 45 independent post-result auditor closure and adversarial re-audit

Attack and closure date: 2026-07-14  
Final auditor SHA-256:
`8e84d8930393e4ba60a906519eef7f1734c713a273791153a55d1f6f16ec3985`  
Frozen v2 numerical manifest SHA-256:
`955e59bf333b5fd70e415a53dc26becae9c7a34c5d40f1230c96b1dab8f5677c`

## Decision

**GO-CODE / HOLD-PROTOCOL / HOLD-SCIENCE.  Final open code findings: P0: 0,
P1: 0, P2: 0.**

The final auditor snapshot survived all 42 original and adversarial tests,
including the three additional filesystem-identity attacks requested before
freeze: an initially symlinked evidence file, an initially symlinked manifest,
and a symlinked manifest-pinned producer file.  Ruff, Ruff format and Python
byte-compilation also pass.

`GO-CODE` means the auditor is ready to be frozen as the post-result
verification implementation.  It is not permission to release a scientific
claim.  Publication remains `HOLD-PROTOCOL` until an honest v2 post-result
audit protocol freezes the v2 numerical anchor, the final auditor and all five
test files.  It remains `HOLD-SCIENCE` because this re-audit deliberately did
not inspect or execute against the canonical formal result or reproducibility
evidence.

No canonical result, reproducibility-evidence JSON, or independent-audit JSON
was read or modified during this attack.  Every forged bundle was created
under an isolated pytest temporary directory.  The final auditor was not
edited by this independent re-audit.

## Adversarial history and closure

The initial Round-45 snapshot
`2dc235b2c0e4ece32f27781d54202bedeeebd0f2f21a761a4edcfa9bce15fedc`
was `NO-GO`: it accepted floating-point aliases for integer mesh triplets and
allowed a retained-root survival value to contradict the saved trace whenever
the survival gate itself reported a scientific HOLD.

Subsequent attacks exposed additional fail-open semantics: negative values in
fields declared to be absolute errors or residuals; boundary-layer fractions
outside `[0,1]`; an integer alias in a conditional floating-point peak ratio;
and a negative reported absolute mesh-agreement difference.  All were rejected
by the final snapshot with exact type, domain or sign checks.

The final filesystem-identity attack then replaced a regular audited input by
a symlink and tested symlinks at every initial external-input boundary.  The
final snapshot uses lexical absolute paths, repeated `lstat` checks for regular
non-symlink files, byte hashes, a source-code snapshot, pre- and post-replace
identity checks, a post-directory-fsync check, and rollback of a prior audit or
cleanup of a newly created audit after publication failure.

The complete attack set now verifies that the final auditor:

- requires exact integer mesh triplets at row, diagnostic and agreement
  locations;
- enforces every retained root's survival bracket independently of whether a
  scientific gate passes or reproduces a legitimate HOLD;
- enforces finite, nonnegative absolute-error and residual fields, `[0,1]`
  boundary fractions, and exact conditional scalar types;
- rejects Python Boolean/integer equality aliases in nested JSON structures;
- recursively rejects unauthorized claim keys, including inside nested lists;
- rejects forbidden claim promotion and near-synonyms for the exact producer
  limitation `no physical d=3 or project/publication gate`;
- rejects initial result, evidence and manifest symlinks, a symlinked
  manifest-pinned source, and a regular audited input replaced by a symlink;
- detects result, evidence, manifest, pinned-source or auditor-source changes
  across publication; and
- preserves a prior audit, or leaves no audit, after injected file-fsync,
  replace, directory-fsync or post-replace identity failures.

The frozen root-survival tolerance was attacked at its exact boundary: the
boundary value is accepted and the next representable float outside it is
rejected.

## Operational erratum v2

The v2 change is suitable for the audited numerical rerun as an operational
erratum.  The original formal execution reached JSON publication but failed
because `numpy.bool_` was not serializable; neither canonical output was
created.  The v2 normalizer admits only Python `bool` and `numpy.bool_` for the
affected Boolean gates and rejects integers, floats, strings and nulls.  The
numerical protocol did not change.

Frozen numerical anchors independently checked here:

| Role | SHA-256 |
| --- | --- |
| v2 manifest | `955e59bf333b5fd70e415a53dc26becae9c7a34c5d40f1230c96b1dab8f5677c` |
| v2 producer | `adb9434daeccca721ab9c1014f194e0cf9c5c6d0bf092d31e050c040b4b94da8` |
| v2 producer tests | `d60e837c949333d29f7287b17c5e24c6db742067a655bac5050b5966dc821329` |
| unchanged numerical protocol | `f25a8107d7a975342a3b1cbbf84c29df26654a8f6310f0429cba5ffdf7bcda00` |
| operational erratum | `9843b323898b7e0e9edd0eff33431cddb9fb3d4d572caa4d9ebc5d1e5649592c` |

The producer suite has 16 passing tests, with Ruff and format checks green.
This supports `GO-ERRATUM`; it does not prejudge the scientific outcome.

## Real structural-HOLD check

As a non-fixture structural check, the v2 producer was called directly at the
small, non-held-out mesh `N=9`, without invoking the formal execution harness
or writing outputs.  It generated one retained maximum and a structural HOLD.
Passing that in-memory row to the final auditor's reconstruction returned:

```text
root_count = 1
topology = ["maximum"]
reported_all_mesh_gates_passed = false
reconstructed_all_mesh_gates_passed = false
factor_diagnostic_key_count = 13
```

This confirms that the strict conditional schema accepts a real
producer-generated structural HOLD rather than assuming the desired five-root
PASS topology.  The actual OneDrive output directory also passed a read-only
directory-fsync capability check.

## Reproducible verification

Final files:

| File | SHA-256 |
| --- | --- |
| `code/audit_positive_b_broad_four_slab_result.py` | `8e84d8930393e4ba60a906519eef7f1734c713a273791153a55d1f6f16ec3985` |
| `code/test_audit_positive_b_broad_four_slab_result.py` | `757807729bee2dc9832bb741ba589843cd835e564aead0df7a67982b8a421fe0` |
| `code/test_audit_positive_b_broad_four_slab_result_round40.py` | `4d81932ab193eec77659d8262120cf49183528ac7e37501bc65c22b0d90e1b2a` |
| `code/test_audit_positive_b_broad_four_slab_result_round42.py` | `603aee3b506f1fcf348a06f8f784be4144eb65965e891861c498697743af237f` |
| `code/test_audit_positive_b_broad_four_slab_result_resolution.py` | `411a25081d48bc235ab78cc82d65a28ba00a87e775f72c406e907b08113669f3` |
| `code/test_audit_positive_b_broad_four_slab_result_round45.py` | `cec616f487337c6106aca664484fc930a148d5332187ffe6de47c74f03c35855` |

Verification result:

```text
42 passed
Ruff: All checks passed
Ruff format: 6 files already formatted
py_compile: passed
```

The Round-45 file contributes 15 closure tests.  None calls the final auditor
on the canonical formal artifacts.

## Honest independence and claim boundary

This auditor is an independent schema-and-algebra reconstruction, not an
independent numerical solver.  It imports no producer code during canonical
auditing and recomputes topology labels, ratios, event-basin mass partitions,
mesh agreement, Boolean gates and aggregate PASS/HOLD decisions from saved
values.  It also checks the reproducibility record's canonical byte hashes and
internal consistency.

It does **not** recompute the finite-volume semigroup, independently locate the
reported extrema, independently evaluate generator/root residuals or tangent
state-norm residuals, independently recalculate finite-volume factor
diagnostics, or observe the two producer subprocesses execute.  Those values
remain producer-reported inputs whose schema, finiteness, domains, tolerances
and downstream algebra are audited.  The eventual audit JSON must preserve
this boundary explicitly.

The publication transaction assumes no non-cooperating concurrent writer
mutates an audited input immediately after the final identity check.  No
finite sequence of ordinary filesystem checks can exclude such a last-instant
race.  The v2 protocol must therefore require immutable inputs and no
concurrent writers for the short audit-and-publication interval, rather than
claim an absolute lock-free guarantee.

## Remaining release gate

The current `notes/positive_b_postresult_audit_protocol.md` is stale: it pins
the v1 manifest and early auditor/test hashes, and overstates what is known
about independent semigroup reproduction and the execution of two producer
processes.  Before any canonical post-result audit is run, replace it with a
v2 protocol that freezes the six final files above and states:

1. the algebraic/schema reconstruction boundary;
2. the exact producer-reported quantities that are not independently
   recomputed;
3. the immutable-input/no-concurrent-writer assumption;
4. the precheck, atomic replace, directory-fsync, final identity check and
   rollback semantics; and
5. the rule that `PASS_INDEPENDENT_RECONSTRUCTION` is only a fixed-box,
   two-mesh, semidiscrete positive-`B` result, not a continuum, unbounded-domain,
   independent-solver, physical-`d=3`, allocation-cusp or project-release
   claim.

After that protocol is frozen, the final auditor may be run once against the
canonical artifacts.  Only its actual PASS/HOLD/operational-failure outcome
can close `HOLD-SCIENCE`.
