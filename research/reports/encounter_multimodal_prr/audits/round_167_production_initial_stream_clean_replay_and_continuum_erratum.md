# Round 167: production initial stream, clean replay, and continuum erratum

Date: 2026-07-15

Decision: **ACCEPT 12-ROW CONTROL-FREE PRODUCTION INITIAL PREPARATION /
ACCEPT DECLARED-SCOPE TWO-REPEAT CLEAN SERIALIZED REPLAY / RECORD ROUND-165
REVERSIBLE-DENSITY ERRATUM / FINAL P0 = 0 / P1 = 0 / P2 = 0 / KILLING
OPEN / FULL OPERATOR OPEN / PRODUCTION RESOURCE GATE OPEN / F0 HOLD / NO
POSITIVE-BUDGET EXECUTION / NOT RELEASE ELIGIBLE**

This round is the living successor to Round 166 for one science-free
prerequisite.  It expands the tiny initial-source witness to every one of the
12 frozen production geometries and binds the exact partitions, free-axis
rates, stationary masses, analytic initial marginals, sparse tensor boxes,
and native packed free-axis payloads through a small file-backed evidence
graph.  It also observes two complete serialized replays across five separate
`python -I` processes per repeat.

The acceptance is intentionally narrower than F0.  No contact-killing array,
full generator, uniformization, propagated target, time jet, survival curve,
root exclusion, topology certificate, positive budget, or scientific control
value is constructed or read.  The largest production row has not passed the
required measured full-operator resource gate.  Continuum convergence and PRR
release remain open.

All work in this round was local to the repository.  No external submission
was made.

## 1. Frozen sources and accepted dependencies

| Object | SHA-256 |
| --- | --- |
| code/rate_defined_tensor_f0_production_initial_stream.py | 2871976855a0c598b26b8d83b33f4ea3a027a2c826ccdb2ad9b678761093e6cb |
| code/rate_defined_tensor_f0_production_initial_rebuild.py | 1ed8ea255df01fca10e294994557b1efc8660f933683477a5a289593da7c1c14 |
| code/rate_defined_tensor_f0_production_initial_independent.py | e0121dd2f90bbebc5f973f4e80f7b43dea5ec2d0ac04e1f253a6618b35cf0a96 |
| code/rate_defined_tensor_f0_geometry_bound_packed_axes.py | baa4c12032174f179f1aed6ed9bde78dc6f1fb163e262980897ba3e893af8cc6 |
| code/rate_defined_tensor_f0_production_initial_clean_replay.py | d8d6793519e64e662e612dddcf7f97074249850029423056e073ff3c11a76a38 |
| code/test_rate_defined_tensor_f0_production_initial_stream.py | d32cb29878946f1464587293e0bb76af567c9e3b909e81308623addfa5a13544 |
| accepted production-configuration JSON | 063913c7fbc2b706ba85a0e3f06005bad23a2292749817294cbf41f5cdce4084 |
| accepted analytic initial source | 0b2efec5dc1abea1380ab862e46825e7b79658fe9bfa0ac6637e1426ed9f7f5f |
| accepted rate-defined F0 core | 321f12aa8a5df44ca9c9162704cccd0f2c526abf9577832b4824538b0afdb8e5 |
| accepted packed-action core | 447aa3bc224685ea1cc556d9d322dafba05ef148945d4ae41291f83e29f3deb4 |

The stream verifier checks the raw analytic-source bytes against the accepted
digest before parsing them.  Its verification entry point also pins the
imported F0 core.  Thus a semantically similar reserialization or a coherent
substitution of the implementation dependency does not inherit acceptance.

## 2. Canonical file-backed bundle

The canonical root is
`artifacts/data/physical_production_initial_stream_v1/`.  Its manifest has
SHA-256

~~~text
5d81d1c02ec2484f0b3d5fab3a825cf6f6331f7d3e4cc8dae224266201dfbd9e
~~~

The bundle covers the fixed order

~~~text
O113/Base, E128/Base, O129/Base, O161/Base,
M+, R+, MR+, MR+F, A_M, A_R, A_Y, A_MRY
~~~

and the following state counts:

| index | row | states |
| ---: | --- | ---: |
| 0 | O113/Base | 1,442,897 |
| 1 | E128/Base | 2,097,152 |
| 2 | O129/Base | 2,146,689 |
| 3 | O161/Base | 4,173,281 |
| 4 | M+ | 2,762,406 |
| 5 | R+ | 2,862,252 |
| 6 | MR+ | 3,683,208 |
| 7 | MR+F | 7,165,305 |
| 8 | A_M | 2,113,536 |
| 9 | A_R | 2,113,536 |
| 10 | A_Y | 2,097,152 |
| 11 | A_MRY | 2,130,048 |
| **total** |  | **34,787,462** |

There are 207 physical files including `bundle.json`, of which exactly 206 are
members of the reference graph:

~~~text
2 request files
+ 12 x (1 row manifest + 3 partitions + 9 free-rate files
        + 3 initial-marginal files + 1 sparse tensor file)
= 206 referenced files.
~~~

The stored bundle occupies 1,439,598 bytes.  Its virtual dense expansion is
556,599,392 bytes.  The evidence therefore exercises the production shapes
without materializing a dense interval vector.  Exact reference-graph checks
reject both an extra inventory sidecar and an attack that duplicates a
same-byte pointer while replacing the missing path with an unreferenced file.

Across all rows, the separate-source verifier covers 10,074 directed free
rates, 5,037 stationary masses, 5,037 initial-marginal intervals, and 722
active sparse tensor components.  The exact schemas bind configuration order,
coordinate roles, partition endpoints and volumes, periodic base/half shifts,
vertex-centred half volumes, Scharfetter--Gummel rate directions, stationary
relations, marginal axes, sparse C-order indices, big-endian canonical bytes,
and dense-expansion digests.

## 3. Distinct evidence layers

The receipts are not interchangeable.  Their file digests and their internal
domain-separated receipt digests are:

| Layer | File SHA-256 | Claimed receipt SHA-256 |
| --- | --- | --- |
| same-core relational reconstruction | 131ef316bbd70d7539c76bf83972b45643a2676b80c67fcfd78d6d8b089cc0b4 | 5a0154d7df78ce41876c27cd2fa6694c6e931a96b28f096992513f2a0d3c5659 |
| separate-source semantic containment | 2fb16af6545281f988ddf7527b5e88b46e98ec7e5a05fcbe1bb5bf457c6f9136 | df9df810e2bf6c061833c1ef81dbec590466b4b06310caad71d0cf00084d3290 |
| native packed free-axis geometry joins | 3b23c641ce82cb30a2f150d9956b235bca918948a40f57365f866e6aa54959fb | 5d8d11973633558b8eadd83b15e0961039e2c67ed4b0e91063125b65d0fb493a |
| two-repeat outer clean-process observer | e1b25ab5221434e26749e9b2103c04c36e27539a810e2a15c236c1806b333891 | f33dd0b2695464370e29a2896d3753e753525d9cf5d38b5917a616181096bf9b |

### 3.1 Same-core reconstruction

The relational implementation has a separate artifact parser and rebuilds all
206 referenced files byte for byte.  It intentionally uses the same numerical
core as the producer.  Its flags therefore state
`independent_numerical_implementation=false` and
`independent_semantic_replay_complete=false`.  It is a deterministic
relational reconstruction, not independent numerical evidence.

### 3.2 Separate-source semantic containment

The independent module has separate parsing, partition, rate, marginal, and
sparse-box logic.  It uses 256-bit directed MPFR and 32,768 Simpson panels per
unit, compared with the producer's separately pinned path.  It reconstructs
the exact partitions and checks that every independently derived quantity is
contained by the canonical outer envelope.

This is implementation separation, not backend independence.  Both paths use
`gmpy2`/MPFR and the same validated Simpson remainder lemma.  The receipt says

~~~text
backend_independence_scope = separate_source_and_higher_precision_same_gmpy2_mpfr_library
independent_semantic_replay_complete_for_declared_scope = true
independent_semantic_replay_complete = false
continuum_verified = false
f0_pass = false
~~~

No claim in the manuscript or this audit upgrades that boundary.

### 3.3 Packed free-axis geometry

For every row and every axis, canonical forward/backward big-endian rate files
are converted to the native packed interval-action representation and
round-tripped exactly.  Six conversion receipt digests are bound per row, for
72 total joins.  The first and last wrapper bindings are

~~~text
O113/Base  4cf8c21dead08aeb26ecf90b2019a761d0e424aaa82d9e35b4ce26c8d63c9208
A_MRY      5cccd37be46a68408540c1c1e4b16e7820a74cffccab167e00648add16e35095
~~~

The flag `free_axis_operator_geometry_bound_all_rows=true` means only that
these forward/back packed free-axis rate payloads are joined to the exact
partition and axis-relation hashes.  It does **not** mean that contact killing
or the full operator has been constructed.  The same receipt explicitly keeps
`killing_contact_geometry_bound=false`, `full_operator_bound=false`,
`propagation_executed=false`, and `f0_pass=false`.

### 3.4 Outer clean-process replay

The standard-library outer orchestrator performs two complete repeats.  Each
repeat launches five separate isolated Python processes in this order:

~~~text
producer -> same-core verifier -> separate-source verifier
         -> packed-axis binder, with serialized files between stages
~~~

The observed implementation actually uses five distinct `python -I` processes
per repeat: producer, producer verifier, relational rebuild, separate-source
verifier, and geometry binder.  Ten distinct fresh PIDs were observed across
the two repeats.  Both repeats produced the same evidence digest:

~~~text
865bcd7c57aff7f635fa6032ddd47b393f9d34e9fd74e6b5873d59fe4dc1bd10
865bcd7c57aff7f635fa6032ddd47b393f9d34e9fd74e6b5873d59fe4dc1bd10
~~~

The inner receipts correctly retain `fresh_process=false`; only the outer
observer claims the process boundaries it actually witnessed.  Here “clean”
means separate `python -I` processes and serialized stage boundaries on the
same pinned runtime.  It does not mean a hermetic clean installation,
operating-system independence, or cross-backend reproduction.  The outer
receipt explicitly records `independent_backend=false`.

The retained-receipt validator requires an external
`expected_receipt_sha256`.  It checks exact top-level, source, evidence, row,
shape, and 72-conversion-digest schemas.  A dedicated external-authority test
pins the validator source, receipt file, and accepted domain digest, then
proves that a coherently rewritten and rehashed evidence object is rejected as
not the pinned result.

## 4. Adversarial repair history

The final bytes resulted from multiple independent attacks rather than a
single green producer run.  The repaired findings included:

- pinning the raw analytic-source bytes and imported F0 core at verification;
- replacing permissive JSON relationships with exact top, nested, row,
  partition, rate, marginal, sparse, and receipt schemas;
- verifying the exact 206-path reference graph rather than only its count;
- rejecting promotion keys, noncanonical source bytes, periodic-cut
  substitution, unreferenced sidecars, and duplicate same-byte pointers;
- making the separate-source path check all metadata relations instead of
  trusting producer summaries;
- retaining explicit generic negative flags even when the narrower declared
  source/partition/free-axis scope passes;
- pinning rebuild, independent, packed-core, and geometry sources in the
  geometry layer, and checking receipt self-digests and all row joins;
- requiring exact canonical stdout, no unexpected stderr, serialized receipt
  rereads, and CLI-to-file receipt-digest equality at every process boundary;
- requiring two exact evidence repeats and ten distinct observed PIDs; and
- adding an external authority pin so a self-consistent rewritten receipt
  cannot appoint itself as the accepted result.

The final independent source reviewer returned `P0=0, P1=0, P2=0` for source,
partition, free-rate, marginal, sparse, reference-graph, and nonpromotion
scope.  The clean-replay reviewer returned `P0=0, P1=0, P2=0` for the declared
serialized replay scope.  The final boundary review returned `P0=0, P1=0,
P2=0` after the external authority pin was added and the two wording
boundaries in Sections 3.3--3.4 were made explicit.

## 5. Round-165 reversible-density erratum

The immutable Round-165 audit contains an isotropic Gaussian exponent that is
incompatible with its displayed anisotropic diffusion matrix.  That historical
file and hash remain unchanged, but its formula is not evidence and must not
be copied forward.

For the physical three-coordinate quotient,

\[
 \mathbf D=\operatorname{diag}(D/2,2D,2D),\qquad
 b=(-\gamma(z-\bar z),-\gamma r_\parallel,0),
\]

the normalized reversible density is

\[
 \pi=Z^{-1}\exp\!\left[-\frac{\gamma(z-\bar z)^2}{D}
                         -\frac{\gamma r_\parallel^2}{4D}\right],
 \qquad Z=\frac{2\pi D W}{\gamma}.
\]

Indeed,

\[
 \nabla\log\pi=
 \left(-\frac{2\gamma(z-\bar z)}{D},
       -\frac{\gamma r_\parallel}{2D},0\right),
 \qquad \mathbf D\nabla\log\pi=b.
\]

The living continuum program, Supplemental Material, and
`notes/continuum_next_stage_path.md` use this corrected anisotropic density.
This algebraic correction does not prove C0--C3, Mosco convergence, a
computable continuum error, or continuum topology.

## 6. Manuscript and living-scope integration

| Object | SHA-256 |
| --- | --- |
| manuscript/encounter_multimodal_prr_theorem_first_working.tex | 7771c89c937d9a2561964de7cc12699f816bcaaa4525710dd647bf1b76747b3c |
| manuscript/encounter_multimodal_prr_supplement.tex | b8182df7e269a90c81e504121db99ae0867c7c5cab8e093be3d32e6a86a58b86 |
| notes/research_contract.md | 9dc8f028ebc97bf81f5d0a9e775e246ecddce838abd4d0fc0029f45fdeeec697 |
| notes/continuum_next_stage_path.md | e69c31489ca53b3594509f0f274f022a773a73407e19a9144bddf65ed64f362f |
| notes/continuum_research_program_v2.md | c639dc2b6fbe636c1f24340ea2ea96003487b3613bdd616399c3cd7cb984284c |
| README.md | 2a318c9b17df74b8f6709697bcddb044f71e8979eaea00cd1d6949f758748572 |
| code/test_general_dimension_scope_consistency.py | 5d7f5d1a42f08c0bdf6dc61400674ae8abd32fdc94f53d8d6f849a6278257af5 |

The theorem-first main calls the numerical object a control-free preparation,
not a reaction-time result.  The Supplement gives the exact 12-row size table,
evidence layers, same-backend limitation, and negative scope.  The living
contract and continuum path make killing, full-generator assembly,
propagation, topology, the largest-row resource gate, F0, and all 36 F1 rows
open.

Round 149 remains the immutable authority for the exact-`m` proof migration,
and Round 165 remains an immutable historical record.  Their frozen audits and
historical hashes were not rewritten.  The living whole-file claim-surface
guard now pins the separately reviewed Round-167 successor bytes and still
mutation-tests every surface.

## 7. Regression, build, and visual evidence

The focused production-initial suite collected and passed 25/25 tests.  The
external retained-receipt authority test also passed alone, 1/1.  The six
production-initial Python files passed Ruff check, Ruff format check, and
`py_compile`; their hashes were unchanged before and after those checks.

The independent-focused tests cover, among other cases:

~~~text
configuration order and duplicate/non-finite JSON
all 12 exact partitions and state counts
206-file graph and small stored representation
same-core 206-file byte reconstruction
separate-source rate/mass/marginal/sparse containment
canonical-to-native packed roundtrips
isolated-process CLIs and receipt joins
promotion, endian, source, cut, sidecar, and pointer mutations
retained clean-replay external authority
~~~

A 40/40 cross-scope suite passed for the theorem-first compiler, manuscript
scope, continuum-program scope, fixed-dimension boundaries, immutable Round-149
mathematical core, and immutable Round-165 historical audit.
A separate Round-167 immutable-freeze suite passed 3/3, pinning the integrated
sources, canonical receipts, living manuscript bytes, rendered outputs, this
audit, exact bundle size/reference counts, and every negative promotion flag.

The report-owned compiler then completed two isolated builds of each document
and reproduced the same canonical hashes:

| Output | Pages | Bytes | SHA-256 |
| --- | ---: | ---: | --- |
| theorem-first main PDF | 6 | 371,951 | 937a109118bee0a3a445816cd8ed0b5ff915b038b51f0ca1eb343186af31d4aa |
| theorem-first Supplement PDF | 23 | 562,980 | 70de25968298d58222bbab10639a2253067f5c01d4d6462d743e3e6eca5790fb |
| compile manifest | - | 6,996 | f7712228afab0ec47000b2e29a28507c2a96abc3c76cd91ffa72efc97e44ab75 |

The manifest records:

~~~text
status                                  PASS_INTERNAL_THEOREM_FIRST_WORKING_SET
main rebuilds byte-identical            true
Supplement rebuilds byte-identical      true
all fonts embedded                      true
Type-3 fonts                            0
overfull boxes                          0
undefined references                    0
undefined citations                     0
Ghostscript parse                       true
release_eligible                        false
positive_budget_evaluated               false
positive_budget_scientific_values_read  false
~~~

All 29 Letter-size physical pages were rendered and visually reviewed.  The
new production-method pages, formal-boundary table, and final two Supplemental
pages were also inspected at original detail.  No clipping, overlap, missing
glyph, broken rule, unreadable table, or page-transition defect was found.  The
large lower blank region on the final reference page is normal final-page
layout, not missing content.

The main PDF has six physical pages, but approximately five pages are body and
page 6 is bibliography.  This is an honest compact theorem-first working
skeleton, not a claim that the final PRR Article is complete.  The 23-page
Supplement contains substantive proof and method material rather than padding.
Page count is not a promotion gate; the missing finite-parameter and continuum
results are.

## 8. Exact nonpromotion boundary

The strongest accepted statement is:

> All 12 frozen control-free production geometries have a reproducible,
> file-backed analytic-source/partition/free-axis/sparse-box preparation; a
> separate-source same-backend verifier contains the declared quantities; the
> canonical free-axis rates are joined to native packed payloads; and two
> serialized five-process repeats produce identical pinned evidence.

It is not admissible to infer any of the following:

~~~text
contact-killing geometry                 NOT CONSTRUCTED
full generator / operator                NOT CONSTRUCTED
uniformization or propagated target      NOT RUN
full-window stationary topology          NOT TESTED
survival or basin masses                  NOT COMPUTED
largest-row full-operator resource gate  NOT MEASURED
independent numerical backend            NOT PROVIDED
F0 complete certificate                  HOLD
F1 positive-budget 36-row campaign       NOT AUTHORIZED / NOT RUN
continuum C0-C3                          OPEN
continuum modality topology              HOLD
PRR release                              HOLD
~~~

## 9. Next authorized path

The next F0 work must add contact-killing geometry and assemble the actual
rate-defined full operator without reading prospective controls.  It must then
measure the 7,165,305-state path, including peak resident memory, temporary
storage, cleanup, and failure behavior, before any full-window propagation is
authorized.  Only a separately audited full-operator and resource gate may
proceed to uniformization, jets, interval root exclusion, topology, survival,
and basin-mass certificates.

The continuum route remains separate and ordered:

~~~text
C0  freeze the hash-bound physical model and identification maps
C1  prove fixed-box finite-volume form/Mosco or strong-resolvent convergence
C2  derive computable positive-time spatial errors for r=0,1,2
C3  derive first/second derivative box-truncation errors
then compose only accepted error ledgers with accepted finite-volume margins
~~~

No positive-budget scientific row is needed or authorized for these theory and
method steps.

## 10. Final status

~~~text
12-row source/partition/sparse-box stream       = ACCEPTED METHOD EVIDENCE
same-core exact-byte relational rebuild         = ACCEPTED WITH SAME-CORE LABEL
separate-source semantic containment            = ACCEPTED FOR DECLARED SCOPE
native packed free-axis joins                    = ACCEPTED FOR FREE AXES ONLY
two-repeat serialized five-process replay       = ACCEPTED FOR DECLARED SCOPE
Round-165 anisotropic-density correction         = RECORDED AND DERIVED
theorem-first main/Supplement build              = PASS INTERNAL WORKING SET
final adversarial findings                       = P0 0 / P1 0 / P2 0
killing/full operator/resource gate              = OPEN
F0                                               = HOLD
F1 positive-budget campaign                      = NOT AUTHORIZED / NOT RUN
strict continuum topology                        = HOLD
PRR submission package                           = HOLD
~~~
