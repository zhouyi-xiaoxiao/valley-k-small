# Round 76: allocation-cusp v4 repair and result-blind freeze

Date: 2026-07-14  
Role: implementer repair of every Round-74 pre-run finding  
Status: **HOLD-INDEPENDENT-PRERUN / NO-GO-65-97**

## 1. Boundary

This round repaired the Round-74 `P0=1, P1=6, P2=0` findings without
opening, generating, deleting, or evaluating any mesh-65/97 scientific result.
It did not invoke the post-result auditor entrypoint.  Its only numerical model
was the permitted seven-cell explicit-CSR algebra dry run, executed twice after
the v4 freeze and compared byte for byte.

The five scientific/evidence/replica/audit paths were lexically absent before
and after the work.  The repaired package remains unauthorized until a new
independent result-blind attack accepts this exact v4 hash.

## 2. Frozen v4 anchors

| role | path | SHA-256 |
|---|---|---|
| external v4 manifest | `artifacts/data/positive_b_allocation_cusp_discovery_manifest.json` | `203b03b3f87656269760dd9283376195c56f9170b400b464c6cdd7b95e2e751f` |
| v4 runner | `code/positive_b_allocation_cusp_discovery.py` | `6c6af2cbec48297179381078a0da59a4ff4312b253ae496bb9b716df07e71a9a` |
| ordinary runner tests | `code/test_positive_b_allocation_cusp_discovery.py` | `69ff2b7b781977786fed91769c02037b8ccae2868784f221d5c50530e4baafbc` |
| Round-50 tests | `code/test_positive_b_allocation_cusp_discovery_round50.py` | `30ecf71b426705efa2b6728048093d2da5b96d507c89edc43883579dc4847dbb` |
| Round-61 tests | `code/test_positive_b_allocation_cusp_discovery_round61.py` | `90b106485ced34865426d572b01ea59ef98df8c627cf2cf9f77d98a809fb84a3` |
| Round-74 converted regressions | `code/test_positive_b_allocation_cusp_discovery_round74.py` | `b593da1f93465469f50aacf7f6adc1b68a77a63df95547e9a1b0663c4d1427eb` |
| discovery protocol v4 | `notes/positive_b_allocation_cusp_discovery_protocol.md` | `947db90dca645ce481b1aa2217002500933a8e34ec382c816b5099ec3bc80b64` |
| independent v4 auditor | `code/audit_positive_b_allocation_cusp_discovery_result.py` | `df07fd53b711bb3a2f87d8cb05d0baace3c0cbf3d905aac5c29097b359027b37` |
| independent-auditor tests | `code/test_audit_positive_b_allocation_cusp_discovery_result.py` | `5f4bf7230ca0adb6d42ed2928b643e45860353cf9afd0ebc311fc4ca2819fed8` |
| no-cycle protocol | `notes/positive_b_allocation_cusp_postresult_audit_protocol_v1.md` | `8ccd04f2d8abdfad90ff32998c014faf264d98f09014acb116074523f9d49b39` |
| direct runtime continuum dependency | `code/continuum_observable_four_patch.py` | `a553092f3d8bbf50fdf0124a3ea36ba32947c3b339cfcc0265a1cd7f6bc2d4da` |

The manifest has 23 unique report-relative direct pins.  The auditor, auditor
tests, this report, and the no-cycle protocol remain downstream of the manifest
to avoid a hash cycle; the auditor hard-codes the external v4 manifest hash.

## 3. Round-74 closure

### P0-1: real finite-volume factor/model gates

Closed.  Producer and independent auditor separately derive all three grid
spacings from frozen domain bounds, transverse width, and `N`; require four
patch integrals and both initial factor masses to equal one within `1e-10`;
reconstruct `contact_area_exact = pi*a^2`; require contact, patch, and initial
errors to be covered by finite nonnegative estimates no larger than `1e-10`
up to a frozen `5e-13` undercoverage allowance; and bound both generator
row-sum errors by `1e-10`.  `finite_factor_diagnostics` is no longer constant.
A single factor failure clears every dependent law/control/mesh PASS.

### P1-1: scan and root semantics

Closed.  Every scan now serializes the exact 691-point grid count and its
full-scan reference maximum per-budget density.  Both validators reconstruct
the mesh-specific `0.05` spacing, `[0.5,35]` window, endpoint-sign Boolean,
bracket grid alignment, root type from curvature, density/residual/curvature
eligibility, duplicate status, neighbour separation, ordered reason list,
eligible-root subset, and topology.

### P1-2 and P1-3: phase centre and honest nonzero roundoff

Closed.  The phase payload serializes `phase_centre_theta`; full-result
validation cross-links it to the actual mesh-97 cusp theta.  Each candidate is
checked directly as `theta_cusp_97 + radius*direction` using the preregistered
absolute tolerance `5e-13`.  No subtraction-based recovered centre or bitwise
array equality remains.  An honest centre `(0.01,-0.01)` is accepted while a
forged serialized centre or a phase cloud disconnected from the mesh-97 cusp
is rejected by producer and auditor.

### P1-4: native JSON number types

Closed at the recursive identity boundary.  Mesh coordinates, state counts,
schema versions, candidate/root/acceptance/lineage indices, pair index lists,
replica exit codes, and associated identifier/count fields require exact
native `int`; scientific scalars require exact native `float`; flags require
exact `bool`.  Float/int and bool/int alias mutations now fail in both paths.

### P1-5: complete runtime import snapshot

Closed.  `code/continuum_observable_four_patch.py` is a direct manifest pin,
is captured by `capture_complete_freeze_snapshot`, and is compared by metadata,
exact bytes, and SHA-256 at every existing freeze boundary.  The regression
suite mutates its captured payload and confirms snapshot comparison fails.

### P1-6: stale staging before replicas

Closed.  Both deterministic promotion staging paths are derived and required
lexically absent before the first subprocess, for real and unit-test paths.
Foreign staging is preserved.  Separate canonical-stage and evidence-stage
mutations both produce zero replica calls.

## 4. Verification

The complete permitted result-blind suite was:

```text
pytest collection/result: 72 passed
strict xfail/xpass:         0 / 0
Round-74 open contracts:    7 ordinary regressions, all passed
```

It comprised the ordinary, Round-50, Round-61, Stage-A, independent-auditor,
and converted Round-74 suites.  No test constructed a scientific mesh.

Two final CLI executions used only:

```text
--algebra-dry-run --cells 7
--expected-manifest-sha256 203b03b3f87656269760dd9283376195c56f9170b400b464c6cdd7b95e2e751f
```

Both returned zero with empty stderr and byte-identical stdout:

```text
stdout bytes:   1061
stdout SHA-256: 2165a4bf79bb74e62197cdb0978aa00b47063514eed04b8415d422585a97eca4
```

After this report was written, final `py_compile`, Ruff formatting, Ruff lint,
manifest canonicality, all 23 pin rehashes, and forbidden-path absence checks
were rerun and passed without altering any manifest-pinned byte.

## 5. Implementer self-audit and authorization

Against the seven Round-74 findings:

```text
P0 = 0
P1 = 0
P2 = 0
```

This is an implementer count, not independent authorization.  The exact state
is:

```text
HOLD-INDEPENDENT-PRERUN
NO-GO-MESH-65
NO-GO-MESH-97
NO POST-RESULT AUDIT
NO MANUSCRIPT OR PUBLICATION CLAIM
```

Only a fresh independent result-blind attack of manifest
`203b03b3f87656269760dd9283376195c56f9170b400b464c6cdd7b95e2e751f`
may consider authorizing the two frozen scientific replicas.  It may not tune
any radius, mesh, physical parameter, threshold, chart, or control from an
outcome.
