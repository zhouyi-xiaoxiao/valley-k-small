# Round 171: authenticated fixed-row stationary-integral and raw-flux sources

Date: 2026-07-17

Status: **PASS AUTHENTICATED SAME-BACKEND FIXED-ROW SOURCE EVIDENCE /
PASS INDEPENDENT SOURCE RECONSTRUCTION / HOLD SAME-MEMBER ACCEPTANCE /
HOLD COMPLETE C1--C3 / HOLD PRODUCTION KILLING / HOLD RELEASE**

## Exact final source and execution chain

### Runtime authority

| role | report-relative path | SHA-256 |
|---|---|---|
| authenticated launcher | `code/run_continuum_c1_mpfr_authenticated_v1.py` | `f73f61f40ad658c00bb40f27c6676998763d84383b5c86deff7e3bac48a12df4` |
| four-target execution authority | `code/continuum_c1_mpfr_execution_authority_v1.json` | `1697b0e1ebd9c1dcc38d827a62d07c2e75b397e25e5e7e0f88bad4d9edac32ab` |
| provenance/currentness tests | `code/test_continuum_c1_mpfr_authenticated_execution_v1.py` | `b226a9c68625dd6a8d08e6c3d966e608e2951ee117134d99bdf73ca777971236` |

The operator bootstrap starts the pinned CPython with `-I -S`, opens the
launcher with `O_NOFOLLOW`, compares `fstat` before and after its descriptor
read, checks lexical path device/inode identity, verifies the operator-frozen
launcher digest, and compiles only the captured bytes.  The launcher then
authenticates the retained Round-95 `gmpy2` closure before executing a
descriptor snapshot of one scientific target.

The accepted runtime is machine-specific:

```text
system       = Darwin arm64
Python ABI   = CPython 3.12
gmpy2        = 2.2.1
MPFR         = 4.2.1
GMP          = 6.3.0
MPC          = 1.3.1
```

Native images remain path-loaded under the explicit no-hostile-same-UID-writer
contract.  The protection claim is defense in depth, not cryptographic
immutability or cross-platform backend independence.

### Stationary physical cell integrals

| role | report-relative path | SHA-256 |
|---|---|---|
| builder | `code/build_continuum_c1_stationary_integral_source_v1.py` | `a85aede0700a2ae13001edfa527f2929860da00dec413c3c5a5755198b220f17` |
| canonical artifact | `artifacts/data/continuum_c1_stationary_integral_source_v1.json` | `03db61b4aa9c2b7a4ab2fd78c86fbbf90dd1548657c615d91c1526ae3ed77212` |
| independent validator | `code/validate_continuum_c1_stationary_integral_source_v1.py` | `0dc5ee8ae5e3d7ff051e90855c246ef65ceaad7ccf7d9a9f50b40175321668a2` |
| static/currentness tests | `code/test_continuum_c1_stationary_integral_source_v1.py` | `4ee3b6a11576788e5a5a6053565a2375b8e6861cbe211a619c083842f571ffe6` |
| mutation tests | `code/test_continuum_c1_stationary_integral_source_mutations_v1.py` | `25197c115f7cde94b3fa438d5f10e7c3ff5e54df3f38afb66fca566bdda9f8d9` |
| builder receipt | `artifacts/data/continuum_c1_stationary_integral_authenticated_outer_receipt_v1.json` | `b2096a8b1ffe920e701f9314e0673ccd099bfd2bcdda4c01b025630ea34ead1a` |
| validator receipt | `artifacts/data/continuum_c1_stationary_integral_validator_authenticated_outer_receipt_v1.json` | `26d2b9a3fd49f7f8d4cf893431b1f134c2ae2efae3bf15e1615ca28766603571` |

The independent validator reconstructs all 36 exact partitions and evaluates
5,037 factorized physical axis-cell integrals: 3,446 Gaussian and 1,591
periodic cells.  Every 320-bit directed interval contains its 640-bit
same-backend sentinel.  The tensor box mass retains the globally normalized,
unconditioned density and is strictly below one.

These quantities are physical cell integrals.  They are distinct from the
production files historically named `stationary_mass`, whose entries are the
ungauged representative quadrature primitives
\(\mu_i=\nu_i e^{-\Phi(x_i)}\).

### Raw formula mass, rates, and common edge flux

| role | report-relative path | SHA-256 |
|---|---|---|
| builder | `code/build_continuum_c1_fixed_row_raw_flux_source_v1.py` | `48b29162e533c02950b673d8b207efc771091b9b16581967a5e9ef487bf20a92` |
| canonical artifact | `artifacts/data/continuum_c1_fixed_row_raw_flux_source_v1.json` | `04fee91f8708d90febc23e1f1ee4cfc1cb4800b9e35980eb99006fad327b40f3` |
| independent validator | `code/validate_continuum_c1_fixed_row_raw_flux_source_v1.py` | `8f86118ea279b80746b8d981bbe0e0ce2cf2b0cef286bb981b74d8ea79195c1a` |
| authenticated adversarial harness | `code/test_continuum_c1_fixed_row_raw_flux_authenticated_adversarial_v1.py` | `13309c8dda6130b188bcf1048151a3cc1d8d1d36ef9665fe04d37ccfcac423bf` |
| builder receipt | `artifacts/data/continuum_c1_fixed_row_raw_flux_authenticated_outer_receipt_v1.json` | `480b8b152396442b462952d0f6919a0ddbb5783365d0e02ff252f6d406c44f95` |
| validator receipt | `artifacts/data/continuum_c1_fixed_row_raw_flux_validator_authenticated_outer_receipt_v1.json` | `44af008a9a86cbb249209dd806fbb2633f4976aae5e5fbf234d55dfa36bad0e2` |

The independent validator snapshots all 206 production inventory files,
reconstructs the 36 partitions, decodes 108 raw binary interval files, and
checks:

```text
formula-defined ungauged mu cells      = 5,037
saved directed rate entries            = 10,074
undirected adjacent edges              = 5,013
positive saved rate entries            = 10,026
reflecting exact-zero boundary entries = 48
virtual tensor states                  = 34,787,462
```

For every reflecting cell-centred, reflecting vertex-dual, periodic-base, and
periodic-half-shift axis, the formula-defined raw mass and directed rates lie
inside the saved intervals.  On every edge a single formula-defined common
conductance \(\kappa\) lies inside both saved raw flux products and their
intersection.  The exact rational reconstruction also checks the factorized
box mass, global gauge, inverse gauge, and \(\rho\) range.

The 768-bit route is alternate only for the Bernoulli algebra and function
evaluation: positive arguments use `expm1`, while negative arguments use
\(a/(1-e^{-a})\).  Its mass evaluation repeats the same exponential route at
higher precision.  All 320/640/768-bit paths share the same authenticated
`gmpy2`/MPFR backend and interval infrastructure.  This is an alternate
Bernoulli-route sentinel, not backend, library, or full-implementation
independence.

## Currentness attack and repair

An intermediate PASS was rejected after an independent audit noticed that its
receipts named launcher SHA `0b5083...` while the live launcher had already
changed.  No scientific conclusion was accepted from those stale receipts.

The authority, launcher, four targets, two artifacts, and four receipts were
then frozen and rerun as one chain.  For every final receipt:

```text
live authority digest equals receipt pin = true
live launcher digest equals receipt pin  = true
live target digest equals authority pin  = true
live artifact digest equals authority pin = true
target exit code                         = 0
ambient MPFR precision                   = 53
ambient MPFR rounding                    = RoundToNearest
all claim-boundary booleans              = false
```

The raw validator receipt was independently parsed against all four live
objects after the last run.  The provenance owner confirmed that no launcher,
authority, scientific source, or scientific artifact changed afterward.

## Adversarial reproduction

The final provenance plus stationary suites were rerun together:

```text
/Users/ae23069/.local-build/valley-k-small/.venv/bin/python -I -m pytest -q \
  research/reports/encounter_multimodal_prr/code/test_continuum_c1_mpfr_authenticated_execution_v1.py \
  research/reports/encounter_multimodal_prr/code/test_continuum_c1_stationary_integral_source_v1.py \
  research/reports/encounter_multimodal_prr/code/test_continuum_c1_stationary_integral_source_mutations_v1.py
.................................                                        [100%]
33 passed
```

The 12 provenance tests cover exact currentness of all four receipts, direct
entry HOLD before a fake `gmpy2` can execute, hostile current directory,
forbidden `PYTHONPATH`, ambient 53-bit context, target and artifact path
replacement, symlink rejection, strict Boolean types, self-pin mutation, and
wrong operator digest.  The 21 stationary tests cover canonical bytes,
partition closure, counts, endpoint/periodic semantics, source pins, hostile
working directory, direct-entry HOLD, and semantic/type/cardinality
mutations.

The independently rerun raw-flux harness used the final launcher and receipt
pins:

```text
/Users/ae23069/.local-build/valley-k-small/.venv/bin/python -I -B \
  research/reports/encounter_multimodal_prr/code/test_continuum_c1_fixed_row_raw_flux_authenticated_adversarial_v1.py \
  --launcher-sha256 f73f61f40ad658c00bb40f27c6676998763d84383b5c86deff7e3bac48a12df4 \
  --receipt-sha256 44af008a9a86cbb249209dd806fbb2633f4976aae5e5fbf234d55dfa36bad0e2
```

It reproduced the canonical authenticated receipt, held direct
unauthenticated execution, and rejected same-member smuggling, periodic seam
reorientation, and source-pin substitution inside the authenticated target.
Ruff semantic checks pass.  The exact audited raw validator and harness are
retained without a post-audit formatting-only rewrite.

## Exact acceptance boundary

The independent validators, not the builders alone, are the acceptance gates.
The raw builder has weaker inventory traversal and pathname-read hardening
than the validator and is not independently sufficient.

Round 171 establishes fixed-row source consistency for twelve finite anchors:
physical stationary integrals, formula-defined raw masses/rates, common raw
edge fluxes, factorized gauge, and \(\rho\).  It does **not** issue the
separately ordered correlated receipt needed to bind physical
mass/rate/flux/gauge/map/killing as one accepted production member.  It also
does not provide a refinement limit, concrete control, budget, killing
diagonal, full operator, propagation, or topology.

The following remain false:

```text
backend_independence_claimed                  = false
same_member_acceptance_receipt_present        = false
formal_production_bridge_accepted             = false
production_source_roles_1_through_11_bound    = false
concrete_killing_reconstructed                = false
complete_C0 / complete_C1 / complete_C2 / complete_C3 = false
F0_complete / F1_complete                     = false
release_eligible / submission_eligible        = false
```

Round 171 is therefore authenticated evidence for the fixed-row formula and
source layer.  It is not a production continuum theorem or a PRR science
result.
