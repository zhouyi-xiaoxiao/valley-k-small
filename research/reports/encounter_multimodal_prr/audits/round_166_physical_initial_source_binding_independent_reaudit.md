# Round 166: physical initial-source binding and independent re-audit

Date: 2026-07-14

Decision: **CONTROL-FREE PHYSICAL INITIAL-SOURCE METHOD PASS / CANONICAL
BYTE RECONSTRUCTION PASS / INDEPENDENT SEMANTIC CONTAINMENT PASS / FINAL
P0 = 0 / P1 = 0 / P2 = 0 / PRODUCTION STREAMING OPEN / OPERATOR-GEOMETRY
BINDING OPEN / F0 HOLD / NO POSITIVE-BUDGET EXECUTION / NOT RELEASE ELIGIBLE**

This round closes one deliberately small prerequisite: a physical
two-dimensional, control-free analytic initial law is now bound to a canonical
64-state finite-volume interval box, an exact lower-anchor target, and a
separate semantic replay.  It does not claim a production finite-volume run,
current-target lineage after propagation, a continuum limit, stationary
topology, survival or basin masses, or a positive-budget physical result.

All computation and review in this round were local.  No external submission,
network lookup, credential access, or positive-budget scientific-value read was
performed.

## Final integrated bytes

| Object | SHA-256 |
| --- | --- |
| artifacts/data/physical_initial_analytic_source_v1.json | 0b2efec5dc1abea1380ab862e46825e7b79658fe9bfa0ac6637e1426ed9f7f5f |
| code/rate_defined_tensor_f0_physical_initial_source.py | afef401d6edcfb5a770d4f01a5a1c38f7837cea47cd2d94c676a1e5974dc9417 |
| code/rate_defined_tensor_f0_physical_initial_replay.py | 755fd35001423bf931cc9cf2141ad2901a3a67036aa6a7d8e20bd849fe1c3796 |
| code/test_rate_defined_tensor_f0_physical_initial_source.py | 0e324a3cc3d61437568d4bf387fa1667594900026996ee8bd5c23157cc642989 |
| notes/continuum_research_program_v2.md | c639dc2b6fbe636c1f24340ea2ea96003487b3613bdd616399c3cd7cb984284c |
| notes/research_contract.md | 01804e5328f669236d9f53f38cbfdda813b37f41e2641c91940ad0e90e60038c |
| notes/continuum_next_stage_path.md | 49e5f6b12d8d5b6581c092b80b1bf2af3121054e7f88b6dfa4dcadf826a2cbd7 |
| code/test_continuum_research_program_v2_scope.py | 65566f202b8ddfe1c06c6237236769a3c859f58630b0c25b85a48acc6113fc6c |
| code/test_general_dimension_scope_consistency.py | 48885cd1a9701d5feae632ceef252bc191787eaae586d1293784b14725aa88da |
| code/test_round149_exact_m_hash_freeze.py | b61bf10c40fa5e6dca68b7d471538914de10b6faef36db9ff0714a8d64eb8708 |
| code/test_round165_continuum_c0a_working_set_freeze.py | 0a60e3466b0cd3796f08e456ae9a5b2bd5085e5fe90d9e2a053e3263b3c58a7e |
| manuscript/encounter_multimodal_prr_theorem_first_working.tex | baa40059995679065dcab4a9ec1ee62d5f4d0a19d53e352605a82b9c990cadbe |
| manuscript/encounter_multimodal_prr_supplement.tex | 8168abfd6c20d0f89e193329dd3bd7d1d34dbcfd7d4f5e59e0ac03cce301d7f1 |
| output/pdf/encounter_multimodal_prr_theorem_first_working.pdf | cd14b52523fb9cf5989416997d313a72d26d20f4f9b94159b663444acb354851 |
| output/pdf/encounter_multimodal_prr_theorem_first_supplement_working.pdf | 04953aa8377aada4d604fb2d8bd16ba1adee0a1d08022be7fe09433fdb346729 |
| artifacts/data/theorem_first_working_compile.json | 54feedc6838ac43305d1239d5e65644cd1aa325c640fe251fab26dda1462f038 |

The historical Round-149 and Round-165 tests now distinguish immutable audit
records from later, independently audited living successors.  Old hashes remain
verifiable in the immutable historical audits; they are not silently replaced
with Round-166 hashes.

## Canonical analytic source and exact partition

For physical dimension two, the quotient coordinates are ordered as midpoint
`M`, parallel relative coordinate `R`, and periodic perpendicular relative
coordinate `Y`.  The source is the independent product

\[
 b(u)={\bf1}_{|u|<1}\exp[-(1-u^2)^{-1}],\qquad
 \beta_{h,c}(x)=\frac{b((x-c)/h)}{hI_b},\qquad
 I_b=\int_{-1}^{1}b(u)\,du,
\]

with periodic image summation in `Y`.  The exact binary64 words are

~~~text
M0 =  0x1.1eb851eb851ecp-3
R0 = -0x1.6666666666666p-2
Y0 =  0x0.0p+0
h  =  0x1.47ae147ae147bp-6
W  =  1
~~~

The tiny verifier constructs four uniform cells on each of the exact domains

~~~text
M: [-0x1.0000000000000p-2,  0x1.d99999999999ap+0]
R: [-0x1.ccccccccccccdp+0,  0x1.ccccccccccccdp+0]
Y: [0,1) periodic
~~~

and proves exact coverage with no positive-measure gap or overlap.  The C-order
flat index is `i = 16*j_M + 4*j_R + j_Y`.

The producer uses one shared normalizer enclosure, 16384 composite-Simpson
panels per unit, 192-bit directed exponentials, exact dyadic triple products,
and one final outward binary64 rounding.  It then rebuilds the packed component
bytes and target from the canonical source.  The canonical raw component-box
digest is

~~~text
8f11fe01f350ccbabb88c325896795c269f02dbf8fa80b8cd9eeec3addd462f7
~~~

A distinct but internally consistent unit-mass interval box is rejected by the
deterministic byte-rederivation gate.

## Exact structural witness and lower-anchor radius

Support placement gives the midpoint marginal `(1,0,0,0)` and the parallel
relative marginal `(0,1,0,0)`.  Evenness of the compact bump at the periodic cut
gives the perpendicular marginal `(1/2,0,0,1/2)`.  Therefore the exact tensor
witness has value `1/2` at C-order components 4 and 7 and zero at every other
component.

Every claimed interval endpoint must contain this exact witness.  The canonical
lower-anchor target has exact radius

\[
 1-\sum_i\ell_i=\frac{6051}{2^{53}}
 =6.717959522006822\ldots\times10^{-13}<10^{-12}.
\]

This exact witness, not numerical rectangle overlap, proves analytic-source
containment for the tiny partition.

## Independent semantic replay

The replay module independently parses and validates the full source semantics,
including physical and quotient dimensions, coordinate order, compact-bump
definition, shared normalization, exact starts and half-width, periodic image
rule, period, total mass, and control-free scope.  It uses a separately
implemented directed-MPFR monotone-rectangle enclosure with 8192 panels per
unit and 224-bit arithmetic.

The rectangle computation is only a broad numerical consistency check.  It is
not used to claim canonical endpoint identity.  The replay receipt binds the
source and configuration, algorithm and precision, full manifest digest, raw
component link, logical and array shapes, exact structural witness, claimed and
replayed marginal endpoint digests, replayed component digest, state counts,
masses, geometry, certificate identifiers, and scope flags.  Its validator is
explicitly structure-only.

A broad `[0,1]^64` box contains the semantic witness and therefore passes
semantic containment, while the producer correctly rejects it as noncanonical.
Mutations of source width, coordinate order, period, periodic wrap, start,
marginal halves, zero cells, tensor order, manifest role or shape, target,
certificate, and bound binding are all rejected by the appropriate layer.

The independent replay remains same-process.  It does not rederive canonical
endpoint identity, produce a clean serialized whole-result replay, bind a
production resource gate, or establish F0.

## Propagation and provenance boundary

Every propagation chunk receives the canonical source bytes and original
derivation and independently rederives the initial certificate.  Chunk zero
must match the canonical initial target and bound-target binding exactly; a
forged but structurally valid one-hot target is rejected.  The wrapper retains
only the analytic source certificate across later chunks.

The final fields state the boundary directly:

~~~text
canonical_initial_source_bound              = true on the initial certificate
analytic_source_certificate_retained        = true in the wrapper
independent_replay_receipt_retained          = false
result_self_contained_source_provenance      = false
current_target_lineage_replayed              = false after initial propagation
operator_axis_geometry_bound                 = false
positive_budget_scientific_result_read       = false
production_gate / F0 / F1 / release          = false
~~~

A bare `TargetUniformizationResult` does not carry the analytic source
certificate.  No current result is therefore presented as a self-contained
proof of full source-to-current-target history.

## Adversarial review history

Three independent readers reviewed the producer, replay, propagation boundary,
tests, and manuscript integration.  Their first passes found substantive issues
that were repaired rather than waived:

- rectangle overlap was initially described too strongly;
- propagation initially accepted coherent alternate certificate/target pairs;
- a forged current nominal target could share the initial certificate;
- marginal digests used native rather than canonical big-endian packing;
- manifest role, shape, and receipt fields were under-bound;
- budget-read and receipt-retention wording was too broad;
- the control-volume program overgeneralized cell-centred geometry;
- the manuscript omitted the periodic image sum, exact domains, cell formula,
  C-order index, and independent replay precision.

After the fixes, the source reviewer, replay reviewer, manuscript reviewer, and
integrated boundary reviewer each returned `P0 = 0, P1 = 0, P2 = 0` on their
final reviewed surfaces.  The historical-freeze migration was separately
tested so that acceptance of Round 166 does not rewrite Round 149 or Round 165.

## Regression, build, and visual evidence

The eight-layer local numerical regression passed:

~~~text
packed kernel
directed interval action
rate-action composition
tiny uniformization
target-aware adapter
independent semantic replay
tiny-Q jets
physical initial-source producer/replay

combined result                                172 / 172 passed
~~~

The status, theory, environment, compile, and historical-freeze suite passed
70/70, including the Round-166 freeze.  A focused integrated selection passed
60/60.  Ruff check and format check passed on all eight changed Python files in
that pass.  Repository
documentation-path and science-rule checks passed.

The report-owned compiler performed two isolated builds of each document and
published only after all fail-closed checks passed:

~~~text
status                         PASS_INTERNAL_THEOREM_FIRST_WORKING_SET
main pages                     6
Supplemental pages            22
main rebuilds byte-identical  yes
Supplemental rebuilds byte-identical yes
all fonts embedded            yes
Type-3 fonts                  0
overfull boxes                0
undefined references          0
undefined citations           0
Ghostscript parse             pass
release_eligible              false
positive_budget_evaluated     false
positive_budget_scientific_values_read false
~~~

All six main pages and all twenty-two Supplemental pages were rendered and
visually checked.  Pages 20--21 of the Supplemental Material, which contain the
new initial-source section, were also inspected at full rendered scale.  No
clipping, overlap, broken formula, or unreadable transition was found.

The main PDF now has six physical pages, but page 6 contains only the final two
bibliography entries.  It is therefore not honest to describe this as six pages
of body: the theorem-first body remains approximately five pages.  The new
Supplemental section is substantive rather than padding.  Page count is not a
publication gate.

## Remaining production and continuum path

The next finite-volume step is a file-backed source-to-box stream over all 12
prescribed production configurations and axis triples, including
vertex-centred endpoint half volumes and periodic base/half shifts.  It must
bind the operator rows to exactly the same axis geometry and create an
independent clean serialized full-history replay.  The 7,165,305-state row
requires a separately measured production resource gate.

Only after that may F0 address full-window topology, largest-row evidence,
survival, basin and common-window masses, and cross-configuration agreement.
No positive-budget F1 execution is authorized by this round.

The continuum program remains staged:

~~~text
concrete hash-bound model and identification maps       = OPEN C0
fixed-box Mosco / strong-resolvent convergence           = OPEN C1
initial projection convergence J_h P_h q0 -> q0          = OPEN C2
computable positive-time spatial errors r=0,1,2          = OPEN C2
first/second derivative box-truncation errors            = OPEN C3
complete continuum root/topology transfer                = HOLD
independent clean continuum audit                         = OPEN
~~~

The tiny exact source box is a necessary initial-data preflight; it is not a
proof of finite-volume convergence.

## Final status

~~~text
control-free analytic source semantics          = FROZEN
tiny exact partition and canonical interval box = METHOD PASS
exact structural containment witness            = PROVED
independent semantic replay                      = PASS WITH STATED SCOPE
current-target serialized lineage                = OPEN
production source-to-box streaming               = OPEN
operator-axis geometry binding                   = OPEN
production resource gate                         = OPEN
F0 complete finite-volume certificate            = HOLD
F1 positive-budget campaign                      = NOT AUTHORIZED / NOT RUN
strict continuum topology                        = HOLD
PRR submission package                           = HOLD
~~~
