# Candidate-native role-8--10 method authority v1

Date: 2026-07-18

Status:

```text
ROLE-10 NUMERICAL OPERATION MODEL V2 PROSPECTIVELY FROZEN
NO ROLE-10 NUMERICAL IMPLEMENTATION OR EXECUTION
B06 STRUCTURAL REMEDY NOT YET PREPARED
EXTERNAL PREDECESSOR COMMITMENT ABSENT
ROLES 8--10 PRODUCTION REPLAY NOT PERFORMED
SAME-MEMBER ACCEPTANCE FALSE
```

## 0. Purpose and nonclaim boundary

This note replaces the ambiguous phrase "run roles 8, 9, and 10 in order"
with an acyclic, result-blind method contract.  The role numbers name
scientific responsibilities; they are not an execution order.

The current legacy raw source reads the current role-9 stationary artifact
and then emits raw, gauge, and map quantities together.  That executable
`role 9 -> role 8` edge is an implementation accident, not a mathematical
dependency.  Adding hashes to that closure would preserve outcome binding and
would not clear B06.

The successor has three mutually result-independent primitive producers,
followed by two derived composition layers.  No primitive may read another
primitive's output.  This note does not authorize production, authenticate an
external predecessor, accept a correlated member, clear B06, or promote any
continuum or release claim.

## 1. Frozen primitive responsibilities

### 1.1 Role 8: raw formula primitive

Target schema:

```text
encounter_c1_n0_raw_axis_formula_primitive_source_v2
```

Precommitted inputs are the external predecessor commitment; roles 1, 2, 5,
6, and 7; member-v3 configuration and partition inventory; candidate-native
producer/verifier and runtime closures; and the selected method-parameter
records.

Role 8 must not read role 9, role 10, a control, a budget, a prior role-8
result, or any later acceptance receipt.  Its source-native output contains:

- exact axis-cell geometry and outward intervals for every raw
  `mu_i^a`;
- outward directed-rate intervals for both orientations of every axis edge;
- an independently evaluated formula interval for the exact common raw flux
  `kappa_e`;
- exact-zero reflecting-boundary rates and the unique frozen orientation of
  each periodic seam; and
- optional production envelopes only in fields distinct from the formula
  intervals and only as containment/evaluation-error evidence.

It must not output `M_L`, `M_x^pi`, `G`, `pi_h`, tensor conductances, or
`rho`.  The required formula identities are

```text
mu_i^a = nu_i^a exp(-Phi_a(x_i))
q_i_to_j^a = D_a / (nu_i^a d_ij) B(Phi_j-Phi_i)
kappa_e = mu_i q_i_to_j = mu_j q_j_to_i.
```

For the periodic axis, raw `mu_i` is the cell length and the raw common flux
is `D/h`; the physical `W^-1` normalization belongs to role 9 or the later
killing composition and must not be applied here.

### 1.2 Role 9: independent stationary physical integrals

Target schema:

```text
encounter_c1_n0_stationary_physical_integral_source_v2
```

Role 9 shares the committed authorities, member, partitions, registry, and
policy, but must not read role 8, role 10, `pi_h`, or a prior role-9 result.
Its source-native output contains:

- an outward physical integral for every one-axis cell;
- direct-domain, sum-of-cells, and legal joint intervals for every axis;
- direct and factorized `M_L` intervals and their legal intersection;
- the factorized tensor-cell expression
  `M_x^pi=M_i^(pi,z) M_j^(pi,r) M_k^(pi,y)`; and
- an exact partition-closure DAG and streaming digest, without materializing
  the largest tensor.

It must separately establish, for one density and one exact partition,

```text
M_x^pi = integral_Cx pi(x) dx
sum_x M_x^pi = M_L
M_L = integral_OmegaL pi(x) dx.
```

The periodic physical factor is `|Y_b|/W`, which is intentionally different
from role 8's raw periodic factor `|Y_b|`.  Role 9 must not output `G` or
`rho`.

### 1.3 Role 10: control-free killing-factor geometry

Target schema:

```text
encounter_c1_n0_killing_factor_geometry_source_v4
row schema:          encounter_c1_n0_killing_factor_geometry_row_v2
raw interval schema: encounter_c1_n0_killing_factor_geometry_raw_interval_file_v2
```

Precommitted inputs are roles 1, 3, 5, 6, and 7; the committed member and
partitions; the standalone factorization and killing-geometry authorities;
and complete candidate-native method/runtime closures.

The output contains:

- contact averages
  `C_ab=(|R_a||Y_b|)^-1 integral_(R_a x Y_b) 1_contact dR dY`;
- profile averages
  `Phi_jm=|M_m|^-1 integral_Mm phi_j(M) dM`;
- exact zero/full-cell classification and partial-cell outward enclosures;
- wrapped periodic-segment handling; and
- frozen profile order `0,1,2,3`, storage order, units, and native
  provenance.

`C` is dimensionless and `Phi` has inverse-length units.  Role 10 contains no
control weights, budget, concrete `V`, discrete diagonal `k`, reconstructed
`K`, or prior role-10 result.

The source-native representation is a bounded directory package with one
canonical top-level manifest, one canonical row manifest per configuration,
one contact file per row, and four separately named profile files per row.
The frozen logical layouts are

```text
C_ab:       shape [n_R,n_Y], flat index a*n_Y+b
Phi_jm:     shape [4,n_M],   four files in profile order 0,1,2,3
future V:   shape [n_M,n_R,n_Y], flat index (m*n_R+a)*n_Y+b
```

The future-`V` layout is metadata only; role 10 must not materialize it.
Every numeric file uses the registry-bound big-endian `>dd` closed outward
binary64 interval record.  Each row manifest must bind its three exact
partition files, configuration/member identity, factorization v2,
killing-geometry source, registry v4, the sealed-authentication mirror, the
result-blind request v4, and the producer runtime subclosure v1, plus logical
shapes, units, record counts, file byte lengths, and file SHA-256 values.
Across the frozen twelve-family inventory the exact expected counts are

```text
contact interval records       233,139
profile interval records         6,852
profile files                       48
configurations                       12.
```

The producer evaluates contact/profile enclosures with the precommitted
192-bit directed method and canonicalizes proved zero/full contact cells to
`[0,0]`/`[1,1]`.  Analytic disk area at 256 bits is a global
normalization/coverage anchor, not a replacement for cellwise integration.
The separate-source verifier reconstructs the geometry independently at
384 bits and uses 512 bits as a higher-precision same-backend containment
sentinel, including an independently coded disk oracle and rigorous
fourth-derivative Simpson remainder.  The 384/512 precision pair applies to
both verifier oracle families; the Simpson panel cap and remainder rule apply
only to the compact-bump profile integrals.  It checks that every verified
enclosure is contained in the published 192-bit producer interval, plus
aggregate area and unit profile-mass identities.  This is source independence,
not backend independence.  Neither producer nor verifier may read, import,
pin, or compare numerical bytes with
`physical_production_killing_geometry_v1`; that package is regression evidence
only and is not an authority or oracle for the candidate-native result.

The role-10 numeric gates are inherited unchanged from the predeclared legacy
method and frozen before any candidate-native output:

```text
producer contact-area width / radius^2       <= 1/10^10
producer analytic-area width / radius^2      <= 1/10^12
producer profile integral width              <= 1/10^10
published contact interval width             <= 2^-40
published profile cell-mass width            <= 2^-40
384-bit contact-oracle width                 <= 2^-180
oracle width / nonzero producer width         <= 1/8
verified aggregate profile-mass width         <= 1/10^10.
```

The compact-bump verifier additionally freezes at most \(2^{22}\) Simpson
panels, dyadic depth 64, stack depth 65, 20,000 breakpoints, and a 1,140-second
semantic deadline.  File/tree/JSON caps, exact component-bit caps, and the
primary target width are code-bound method parameters and must be copied from
the accepted independent-verifier design before commitment, not inferred from
new output.

The published package must be staged under the already authenticated output
parent, fsynced, and installed without replacement.  Reads must be
component-anchored with no symlink or multiply linked regular file accepted.
The manifest may record only precommitted inputs and newly generated package
inventory; an observed package hash, acceptance receipt, or verifier result
belongs to a distinct post-run receipt and must not be fed back into the
result-blind request.

## 2. Derived composition layers

### 2.1 Same-member mass/flux composition

This layer consumes the newly produced role-8 and role-9 sources only after
their independent validation.  It is not part of role 8.

For each configuration it computes

```text
S_a = sum_i mu_i^a
tilde_pi_x = mu_i^z mu_j^r mu_k^y
G = M_L / (S_z S_r S_y)
pi_h,x = G tilde_pi_x.
```

The operation DAG must preserve and verify the exact structural identities

```text
sum_x tilde_pi_x = S_z S_r S_y
G S_z S_r S_y = M_L
sum_x pi_h,x = M_L.
```

For each axis edge it forms forward and reverse flux intervals.  It may take

```text
[kappa_e] =
  [kappa_e]direct_from_left
  intersect [kappa_e]direct_from_right
  intersect [mu_i q_ij]
  intersect [mu_j q_ji]
```

only after the two orientation-specific direct-formula witnesses and identical
member bindings establish that all four enclose the same exact quantity.
Mere overlap is not a detailed-balance proof, and a hull is forbidden.

It then derives

```text
c_e = G kappa_e product_(spectator axes) mu
q_x_to_xprime = c_e / pi_h,x
q_x_to_x = -sum_(xprime != x) q_x_to_xprime
rho_x = M_x^pi / pi_h,x.
```

The result remains an outward candidate until a distinct acceptance receipt
certifies one correlated ideal member.

The current role-8 and role-9 v1 outputs contain all numerical primitives
needed for a nonproduction prototype: 5,037 raw `mu` cells, 5,013 directed
axis-edge pairs with four common-flux witnesses, 48 reflecting zeros, 5,037
physical stationary cells, 36 axis sums, and 12 joint masses.  They are not
eligible inputs to a production composition.  Both still bind historical
registry v3, neither request binds an external predecessor commitment, the
persisted member v3 still binds outcome-bound factorization v1, and neither
validator emits an immutable validation receipt.  Role 9 also lacks its
promised partition-closure/stream digest, while role 8 exposes exact geometry
only indirectly through partition pins.  These are schema defects, not
missing scientific primitives.

Before production, role 8 and role 9 must move to new request/output schemas
that bind the same external commitment, a persisted successor member,
registry v4 or later, a canonical 36-partition inventory digest, complete
report-local/native runtime closure, and reserved immutable validation
receipts.  Only then may a source-separated pair validator publish

```text
encounter_continuum_c1_n0_validated_role8_role9_pair_receipt_v1
```

The receipt must bind both request, artifact, validation-receipt, and verifier
closures; the common member identity and its configuration, reference
density, ideal formula, factorization, registry, policy, row stream, and
partition inventory; one external commitment; and the precommitted
mass/flux method.  It must recheck exact row-by-row and partition-by-partition
identity rather than infer same-member status from overlapping intervals.

The bounded composition artifact should use schema

```text
encounter_continuum_c1_n0_candidate_native_same_member_mass_flux_factorization_v1
```

and persist only axis-native factors, gauges, intersections, exit-rate
tables, exact recipes, counts, and stream digests.  It must not materialize a
dense tensor.  The frozen logical counts are:

```text
configuration rows                  12
axes                                36
axis cells                       5,037
axis edges                       5,013
positive directed axis rates    10,026
reflecting boundary zero rates      48
virtual tensor states        34,787,462
undirected tensor edges      103,898,944
logical tensor Q entries     242,585,350
```

The full cell and edge iterators must nevertheless be replayed by independent
producer and verifier implementations in a frozen order, using
domain-separated, length-framed chunk digests.  Chunk size, resource caps,
deadlines, and the exact operation-DAG extension for the gauge total,
three-axis conductance permutations, active-mass alias, `q=c/pi_h`, and row
sum zero must be benchmarked and frozen before commitment.  The already
accepted exact-DAG is only a local algebra kernel and does not prove those
composition identities by itself.

### 2.2 Control-free symbolic killing composition

This layer consumes the validated mass/flux composition, role 10, and role
11.  It retains positive symbolic weights satisfying exact row sum one and
forms

```text
V_c,mab(w) = W^-1 C_ab sum_j w_j^(c) Phi_jm
K = V/rho = V pi_h/M^pi
M^pi K = pi_h V.
```

There is no budget in this stage.  The later distinction is mandatory:

```text
discrete killing diagonal = B V
reconstructed continuum multiplier = B K.
```

The two rectangular-interval paths for `K` must have exactly equal endpoint
pairs when `rho` was derived from the same primitive rectangles.  They are
algebraically equivalent paths, not independent evidence.  Intersecting them
is permitted only when one path uses a separately committed independent
`rho` oracle.

Exact identities are not proved by choosing arbitrary rational points inside
the marginal intervals.  The exact quantities involving `exp`, `erf`, and
physical integrals are generally irrational, so a rational selector is not a
distinguished physical member.  The exact-DAG method therefore has two
separate lanes:

- a formal, value-free, formula-bound algebra lane, canonically normalized as
  sparse rational Laurent polynomials over a frozen symbol order; and
- an outward interval lane over exact rational endpoints.

The formal lane proves the common-flux, gauge, map, two-path `K`, and
`M^pi K=pi_h V` identities conditionally on the role-bound primitive atoms.
The interval lane computes enclosures and verifies legal intersections and
containments.  It must allow both singleton and nondegenerate intervals; width
requirements belong to the precommitted anti-vacuity policy, not the algebra
template.  Interval containment is not promoted to exact formal equality.

## 3. Acyclic operation DAG

```text
frozen authorities/member/policy/registry/schemas/code closures
                              |
                    external commitment
                      /       |       \
                  role 8    role 9    role 10
                      \       /
                 mass/flux composition
                          \
              role 10 + role 11 + composition
                              |
                     symbolic candidate
                              |
                independent acceptance receipt
```

The exact role edges are

```text
roles 1,2,5,6,7 + commitment -> role 8
roles 1,2,5,6,7 + commitment -> role 9
roles 1,3,5,6,7 + commitment -> role 10
role 8 + role 9 -> mass/flux composition
mass/flux composition + role 10 + role 11 -> symbolic candidate
symbolic candidate -> independent acceptance receipt.
```

Forbidden edges include `role 9 -> role 8`, primitive result to policy or
method registry, output to its own request, and any outer-manifest self-edge
or back-edge.

## 4. Precommit/postcommit boundary

Before an external commitment, freeze:

- exact bytes for roles 1--7 and 11;
- the independently validated member-v4 successor, all 36 partition SHA-256
  values, configuration and record order;
- schemas, exact record keys, units, coordinate and normalization conventions;
- every anti-vacuity threshold and resource cap;
- all role-8, role-9, role-10, composition, and exact-DAG producer/verifier
  sources plus complete report-local transitive closures;
- runtime/backend locks and the method-parameter registry;
- the operation-DAG template and expected geometry record counts; and
- fresh output roles and paths, but no output content digest.

The commitment and run requests require an explicit acyclic indirection.  A
request cannot both be hashed by the external commitment and contain that
commitment's hash.  Before commitment, publish a result-blind

```text
encounter_continuum_c1_n0_roles_8_10_replay_plan_v2
```

whose entries freeze each role's method/runtime closure, input authorities,
selected parameter records, exact argv, fresh artifact/validation-receipt
slots, request slot, and role-specific precommit-projection digest.  Its
shared context binds member v4 and its identity; configuration, reference,
ideal-formula, and factorization authorities; registry v4; anti-vacuity
policy; and canonical 12-row and 36-partition inventory digests.  It contains
no future artifact or receipt hash, acceptance bit, or observed summary.
The external predecessor commitment binds this plan's SHA.

The existing plan-v1/request-v3 role entrypoints are retained only as
historical compatibility shells.  They must not be selected by plan v2 or
mutated into dual-mode loaders.

Only after that commitment exists may a thin role-specific request-v4 wrapper
bind the commitment SHA, replay-plan SHA, plan entry id, shared precommit
context digest, and a shared replay-context digest.  Producer and verifier
must reopen the commitment and prove that it binds the plan, then prove the
request/output/receipt paths and exact invocation equal the selected plan
entry.  This structure removes the hash cycle without allowing post-result
method changes.

The shared digest domains are frozen as

```text
encounter-shared-precommit-context-v2
encounter-continuum-c1-n0-shared-replay-context-v2
encounter-role-replay-entry-v2
encounter-continuum-c1-n0-configuration-row-inventory-v1
encounter-continuum-c1-n0-partition-inventory-v1
```

The partition stream is ordered by configuration index and then
`midpoint`, `relative_parallel`, `relative_perpendicular`.  Its records bind
logical relative paths and exact partition semantics; absolute execution
paths belong only to the replay plan.

Before commitment, do not inspect future role-8--10 outputs and do not freeze
their unknown hashes.  No output may be used to revise a threshold, method,
parameter, policy, or resource cap.

After commitment:

1. generate roles 8, 9, and 10, which may run in parallel;
2. independently validate them and freeze a replay-input manifest binding
   their observed hashes;
3. execute and validate the mass/flux composition;
4. execute and validate the control-free symbolic candidate; and
5. issue a distinct independent-auditor receipt.

The predecessor commitment fixes the method before results exist; it does not
pre-accept unknown outputs.  The actual output manifest and candidate digest
must be bound by a later, distinct invocation trust anchor.

## 5. Candidate-native closure rules

Every method entry binds its parameter record, output schema, role scope,
normalization, units, producer, source-separated verifier, and complete
transitive report-local dependency closure.  A closure may not import a whole
legacy scientific module merely to reuse a numerical kernel.

The candidate-native parameter registry has schema

```text
encounter_continuum_c1_c2_n0_method_parameter_registry_v3_candidate
```

and retains the ten v2 parameter identifiers while changing their authority
records and digests under the v3 domain.  The exact ordered scopes are

```text
raw records:
  [role8_raw_axis_formula_primitive]

stationary records:
  [role9_stationary_physical_integral]

exact_fraction_expression_dag_v2:
  [role8_raw_axis_formula_primitive,
   role9_stationary_physical_integral,
   same_member_mass_flux_composition,
   symbolic_killing_composition]

killing records:
  [role10_killing_factor_geometry].
```

The registry has exactly five top-level keys, ten entries, an all-false claim
boundary, and no result or observed-output field.  Same-backend sentinels use
the precision-independent relation
`primary_interval_contains_higher_precision_same_backend_sentinel`; method
ids and the actual 320/640 precisions remain separately exact-bound.

The standalone v3 candidate is
`artifacts/data/continuum_c1_c2_n0_method_parameter_registry_v3_candidate.json`,
SHA-256
`6c1879edaefe5f99da4fffcb76e12466862577376c305e14c857b880067e3b32`.
Its builder and source-separated validator reconstruct all ten records rather
than validating only the three selected by one consumer.  This is a candidate
byte object, not an external commitment or B06 clearance.

Independent role-10 preimplementation audit has since made v3 historical and
nonterminal: its role-10 records do not freeze the complete producer-to-oracle
coverage, 384/512 containment, classifier, anti-vacuity, and resource
parameters.  The bytes and SHA above are retained for chronology; they must
not be used by a new external commitment.  Registry v4 supersedes them with a
new path, schema, digest domain, and complete result-blind role-10 records.

Registry-v4 is now accepted as an internal result-blind precommit authority at
`artifacts/data/continuum_c1_c2_n0_method_parameter_registry_v4_candidate.json`,
SHA-256
`e403a9576abb08d3ada884cd283cce29ce8f877b0e9843cc8d5b911c8c0b0ac5`,
with schema
`encounter_continuum_c1_c2_n0_method_parameter_registry_v4_candidate`.
The earlier `d1ad73...`, `3f0487...`, `b285f3...`, `9f0a01...`, and
`c9b577...` bytes are chronology only.  The last two were rejected because
they overstated the 512-bit contact scope.

The accepted record states the implementation exactly: all 1,304 partial
contact cells are recomputed at 384 bits, the first partial cell in each of 12
rows is additionally checked at 512 bits, and all 6,852 support cells plus 48
support aggregates use paired 384/512 checks.  Published 192-bit records are
read as candidate enclosures for containment; oracle reconstruction does not
use their numerical values.  Exact tree/file/JSON/raw-leaf caps, three replay
deadlines, two canonical policy preimages, contact-area identities, and
support-normalization identities are frozen.

Independent review recomputed all ten record digests, both policy digests, 30
implementation mappings, and the contact/support aggregates.  Builder
`--check`, source-separated validation, 122 focused cases, Ruff checks, and
the final no-drift rehash pass with exact `0444`, one-link publication.  The
verdict is `P0=0/P1=0/P2=0`.  This is internal method authority only, not an
external commitment or B06 clearance.

The previous role-3 source,
`artifacts/data/continuum_c1_factorization_source_v1.json`, is not eligible for
a new predecessor commitment: it binds both the current production killing
bundle's embedded factorization object and a two-repeat output receipt.  The
outcome-free replacement is
`artifacts/data/continuum_c1_factorization_source_v2_candidate.json`, SHA-256
`1cf32a65081dc4f381daae45a556e0e26dc9411eb248cd99e555b754ffad3e26`.
It binds only the control-free configuration, initial exact partition bundle,
and physical killing-geometry authority; freezes the unit longitudinal
Jacobian, periodic Haar `W^-1` normalization, `C_ab Phi_jm` factorization,
profile order, and storage order; and contains no role-10 enclosure payload,
control weight, budget, production killing tensor, or acceptance claim.  Its
builder check, source-separated validator, and 44 focused cases pass.

The new immutable successor member is

```text
artifacts/data/continuum_c1_c2_n0_member_spec_v4_candidate.json
encounter_continuum_c1_c2_n0_member_spec_v4_candidate
SHA-256 b2982e4e2b0bac208f80472d0de959fa152a5494c895677d081836c482e5f2d5
```

Its identity domain is
`encounter-continuum-c1-c2-n0-member-identity-v4`, and its identity payload
includes the complete configuration order, semantic ids, member
semantics, 12 sequence bindings, and mathematical role-1--4 source bindings.
The factorization-v2 path/SHA is therefore part of the mathematical member
identity.  The method-parameter registry is deliberately not: precision,
remainder, and resource-policy revisions must not create a different
mathematical member.  Registry v4 belongs instead to the separately committed
execution context and each role-8--10 request.  The identity digest
for the current source bytes is
`68c8f9eeaca5127e9fb49c4671731990869350b358c67632fb11513f26472193`;
an independent third reconstruction reproduced it from all 12 configurations,
36 partitions, complete semantics, sequence bindings, and role-1--4 pins.
That replay also recovered 5,037 cells, 5,013 edges, 12 periodic seams, and
34,787,462 virtual states.  Factorization, configuration, reference-density,
and ideal-formula authorities are now all exact `0444`, one-link inputs;
historical per-row and partition evidence may remain mode `0644` because it
is content-addressed lineage evidence rather than the normative role-1--4
authority set.

The first independent audit found `P0=0/P1=0/P2=1`: the builder required all
five joint-refinement `established_scope` geometry flags to be exactly
`True`, while the source-separated validator did not mirror those gates.
The validator now mirrors all five checks and the mutation suite contains
five coherent-repin attacks, including `shape_regularity_proved=false`.
Builder check, source-separated validation, and 94 focused cases (26 main
plus 68 mutations) pass after this validator-only repair.  The artifact and
member-identity bytes are unchanged.  A fresh read-only audit independently
reproduced the identity, exercised all five coherent-repin mutations and both
installed-byte race windows, and returned `P0=0/P1=0/P2=0`.  Member v4 is
therefore accepted only as the structural mathematical member; it does not
authorize a production replay.

The successor anti-vacuity policy v4 now binds this member and registry
without reading role-8--10 outputs:

```text
artifacts/data/continuum_c1_c2_n0_anti_vacuity_policy_v4_candidate.json
SHA-256 599252aa1a9fd1d65d9ff3d0faa1e21bb2609da96cca6b6fff1e61a89ebff196
```

It copies the complete v3 requirements, join requirements, and threshold
lineage; all 18 promotion claims remain exactly false.  Current and prototype
enclosures are ineligible, retroactive acceptance is forbidden, timestamp
ordering is insufficient, and a fresh result-blind replay remains mandatory.
The `[8,9,10]` field is explicitly a catalog order that implies no dependency
edge; roles 8, 9, and 10 may execute in parallel only after commitment.
Builder check, source-separated validation, 88 focused cases, Ruff checks, and
a fresh read-only reconstruction pass.  The independent verdict is
`P0=0/P1=0/P2=0` at the internal result-blind policy scope.  This policy is not
an external predecessor commitment and does not authorize replay.

### 5.1 Round-179 role-10 numerical operation model v2

The historical v1 operation-model draft is retained as authenticated lineage
but was rejected and superseded before any external commitment.  Its
execution-facing defects are recorded as post-run claim contradiction,
singleton-classification undercoverage, wire-schema and semantic-validator
underclosure, three-output transaction underclosure, absent ten-slot plan-v2
isolation, and process isolation stated only in prose.

The prospective replacement is
`artifacts/data/continuum_c1_n0_role10_numerical_operation_model_v2_candidate.json`.
Its schema is
`encounter_continuum_c1_n0_role10_numerical_operation_model_v2_candidate`
and its status remains
`RESULT_BLIND_CONTRACT_ONLY_CANDIDATE_NO_NUMERICAL_IMPLEMENTATION_OR_EXECUTION`.
The immutable artifact is 212,071 bytes, mode `0444`, link count one, with
SHA-256
`ac0c2b185be75f0ecef3e331fdfd47fc674ca151fa6b26600aff9f789a2f8a6b`.
The frozen builder, independent validator, positive tests, and mutation/race
tests have SHA-256 values
`927e6b83a525db082a9bef8c4d7cb7b17e7f8f690ff5984673e5a72b7c57c912`,
`a58909e0b43f0680bc1ac9954236083094efa240e50210876a05e7e9c0c78531`,
`b32b1e734197897306a41696c381b19a4e47b56aaa7136d9b226b68f4a42559a`,
and
`8e7a1d5a08dc9ba59c80daf37e793ac030f2995e96b9a2ee56fd7c3d5035c249`,
respectively; each is mode `0444` with one link.

The model specifies future source-v4/row-v2/raw-v2 wire contracts, request-v4,
replay-plan-v2, runtime-closure-v1, ten global slots, a pinned global runner,
and the single public role-10 three-output transaction.  All 99 normative
internal pointer references resolve to 49 unique targets; `103` is not the
current count.  The independent v1-plus-two-delta oracle reconstructs the
artifact without importing or executing the builder.  Builder check, both
validator modes, 25 positive tests, 21 mutation/race tests, Ruff, and
`py_compile` pass.  These are prospective contracts, not executed processes
or numerical output.

Two independent prospective contract audits each returned `P0=0/P1=0`; the
final freeze ledger is `P0=0/P1=0/P2=2`.  The two P2 limitations are the
explicitly non-byte-complete host runtime and operational cleanup/recovery:
a successful future implementation may leave an empty hidden stage root unless
it adds a normative removal, while a crash can leave unjournaled invocation
working, `HOME`, and `TMPDIR` directories that require fail-closed manual
recovery.  The separate sealed-authentication-mirror audit returned
`P0=P1=P2=0`.  None of these results is an external predecessor commitment,
B06 preparation or clearance, role-10 implementation or execution, replay,
same-member acceptance, C1--C3, F0--F3, root transfer, release, or submission
evidence.

The artifact field named `dependency_closure` has a deliberately narrow
scope: it is a role-3 local derivation skeleton over three terminal,
content-addressed canonical JSON inputs.  Its edges do not claim the
transitive provenance or internal dependency graph of those terminal inputs.
Nested path/hash fields and partition-bundle inventories remain downstream
provenance or consumer obligations, not dependencies authenticated by this
candidate.  It is not a complete code/runtime or historical-provenance
closure, and `formal_selected_source_dag_complete` remains false.  Complete
method-level consumers must separately open and authenticate the nested
configuration, initial-geometry, partition, and killing authorities.

The current authenticated stationary/raw launcher is not reusable as
candidate-native authority because it permits only `--check` and pins the
current result bytes.  The current killing producer imports the broad F0 and
initial-stream modules, and its legacy closure does not pin the imported
uniformization, NumPy, SciPy, extension, and native-library closure.  The
current killing verifier also pins the current result and derived tree/policy
digests.  Those modules are algorithm references only.

Safe reuse requires extraction into new source-separated implementations of
small algorithms such as exact rational parsing, directed MPFR arithmetic,
Gaussian segment integration, partition reconstruction,
Scharfetter--Gummel/Bernoulli formulae, binary64 endpoint decoding,
contact-disk classification, compact-bump integration, and Simpson remainder
bounds.  Producer and scientific verifier must not share their numerical
implementation.

A result-blind run request binds input path/SHA pairs, member and registry
digests, code/runtime closure, exact argv, output schema, and a fresh output
path.  It contains no observed artifact hash, tree digest, relation digest,
acceptance bit, or result summary.  Observed hashes first appear in post-run
receipts.

### 5.2 Round-180 static plan-v2 precommit protocol

Round 180 freezes only the protocol vocabulary and a static package validator:

```text
code/continuum_c1_n0_roles_8_10_protocol_constants_v2.py
SHA-256 4f0dbf1a243a9157f11176b89a3b27833cf6ccc76230cf976a1a985cbb178b15

code/validate_continuum_c1_n0_roles_8_10_precommit_package_v2.py
SHA-256 e1ab7c1eb4d8d1f8a9f3f2e0298513727d04c1dc93628fa2886bf9d4a81c991a

code/test_continuum_c1_n0_roles_8_10_precommit_package_v2.py
SHA-256 7d02c09c165b0dcbce5eef5fb85cda02b74db054162adff6d59ec87decbf4443
```

All three are `0444`, one-link files.  The validator seals its constants by
exact hash, joins every used constant back to the authenticated operation
model, uses strict JSON types and exact modes, recomputes member/inventory
digests, authenticates the complete 40-entry mirror tree, enforces global
producer/verifier report-local source separation, and computes the least
root-reachable static import closure without importing candidate modules.
Dynamic import aliases, general ambiguous from-imports, result vocabulary,
legacy scientific imports, all ten pre-existing future slots, mirror-tree
output descendants, and disconnected dependency components are rejected.
The final synthetic/adversarial suite passes 42/42.

The success status explicitly says `STATIC_STRUCTURE_ONLY`.  No actual
runtime-closure-v1, replay-plan-v2, bundle-v2, request-v4, external commitment,
output, or receipt exists in the report tree.  The static ledger is
`P0=0/P1=0/P2=4`: real Python/native/ABI truth, all six role-v3 numerical
entrypoints, the global runner and its one-shot freshness/launch graph, and an
exact frozen allowlist for any non-null shared protocol remain open.  This is
therefore not B06 preparation or clearance and not replay authority.

### 5.3 Round-181 role-8/9 v3 CLI HOLD sentinels

Round 181 freezes the four operation-model-v2 role-8/9 source basenames only
as fail-closed CLI sentinels.  The exact source hashes are:

```text
role-8 producer  61a23da6ff9ea416f55db3698449cbefb77bfeb21e570d604adee0ded7615e69
role-8 verifier  efb02c33f1779d3cb501451e9f7d72a1c31f2f1795cedcb0c83d0a23c788605e
role-9 producer  1b76e1463d5a388f15669d86922db86154011f78913528b9efa2ad98bd376e22
role-9 verifier  ee6ecb5f1a2db3c21114ddad3faf89fa8fa2aac334d50cfc254592b8eac35283
```

All four are `0444`, one-link files.  They implement only exact argv parsing
and one role-specific implementation-incomplete HOLD, import no numerical
backend, do not open supplied paths, and publish nothing.  The focused suites
pass 25/25 after repairs for help-exit success, alternate parser diagnostics,
premature native loading, and test-oracle import gaps.  Hence
`CLI HOLD shells=4/6` while `numerical implementations=0/6`.

The accompanying live runtime probe finds two replay-readiness P1 blockers in
the frozen Round-180 validator: its hard-coded top-level gmpy2-extension model
does not match the observed wrapper plus `gmpy2.gmpy2` topology, and its
candidate-source import/mode profile cannot admit the observed stdlib/runtime
prefix.  These findings require a versioned result-blind validator repair;
they do not authorize a runtime closure, plan, bundle, request, commitment, or
execution and do not change the operation-model-v2 bytes in this round.

### 5.4 Round-182 rejected probe and frozen AST-only resolver

Round 182 independently rejects both initial runtime-truth helper drafts.  The
v1 origin-probe basename is now a frozen inert sentinel with no PASS, path,
filesystem, import, or subprocess surface:

```text
sentinel       432d8d83e3e691033b091037a216adb46199ff891aea1bb02696670397b42ffa
sentinel tests 10430990964d7a12b5220ca6dce5371d14d1a5456f659dd06ae6359ce2280012
```

The replacement static component accepts only caller-authenticated immutable
bytes, exact SHA-bearing dependency records, mandatory dotted parents, and an
independently supplied runtime package-member classification.  It distinguishes
report-local `.py`, runtime-prefix `.py`, opaque runtime-prefix `.so`, the
numerical native extension, builtin, and frozen origins.  The frozen bytes are:

```text
resolver       9b59af9bcbaab9159cbfc8a468c7b9aeb7fd576734fb451728fa2dafec57cbe9
resolver tests 99974d01b16818fc44713cd9e52c246e902d898241f26dc3f5015c6606efc306
```

The focused resolver suite passes 93/93.  A read-only live check represents
the observed `gmpy2` wrapper as `file_runtime_prefix` and the nested
`gmpy2.gmpy2` image as `numerical_native_extension`.  This is only an AST and
byte-join component freeze: there is still no sealed runtime authority,
trusted origin classifier, hardened v2 child/supervisor, v3 precommit adapter,
six numerical implementations, global runner, or actual runtime closure.
The integrated replay-readiness ledger remains `P0=0/P1=2/P2=4`, and no plan,
bundle, request, commitment, execution, output, receipt, or promotion is
authorized.

### 5.5 Round-183 static runtime inventory and generic supervisor

Round 183 freezes two more components without creating runtime authority.  The
static inventory builder, source-separated validator, and tests are:

```text
builder   a41e68012f66c5e9e71cdd780caad7ee64ea3425e39aa72e031d4f58a7e98390  31,510 bytes
validator b68b42fced8e28f9b2584295aba1937d147222e4e61d0fcf808e74c142d501e4  31,132 bytes
tests     2625757a1e49ed3863f293afc4af859fbea3a1432fd0986fbb8d3ce5f1e82ffc  26,376 bytes
```

All three are `0444`, one-link files and the focused suite passes 92/92.  The
component binds the operation-model and process-section hashes, exact proposed
six-file layout, five Mach-O images, thirteen edges, and explicit Homebrew/
Apple host boundaries from caller-authenticated immutable bytes.  Its
canonical 11,715-byte in-memory inventory has SHA-256
`13b70ec6194bbad62e19cea2538f19a8351e6f6ad820ac7a09d0adf25433b8c6`,
but no persistent JSON was published and the recommended external root is
absent.  Its final static ledger is `P0=0/P1=0/P2=1`; the P2 is
builder/validator parser-oracle common-mode risk.

The generic supervisor and tests are:

```text
supervisor 8714c0646f394f30b1fea8e4ffb9cc1760513897f010c67058b21800aa58b45b  32,287 bytes
tests      7bc21953779b45147f34740d938336dde6e15ca2cedb009e21b83d12ffdcdb52  26,551 bytes
```

Both are `0444`, one-link files.  After two independent HOLD audits and two
repairs, 32/32 focused cases plus five root-level repeat loops pass.  The
component provides bounded nonblocking capture, observed PGID/SID ownership,
one absolute cleanup bound, TERM--KILL--reap/group/pipe evidence, and
fail-closed capture/deadline handling.  It deliberately does not authenticate
the executable, close pathname-to-`Popen` or escaped-descendant boundaries,
interpret child semantics, or implement the operation-model deadline adapter.
Its final generic ledger is `P0=0/P1=0/P2=2`.

The static inventory is A, a future authority-bound child/probe is B, and the
eventual `runtime_closure` must additionally join A+B to the Round-182 AST
resolver, trusted origin adapter, six actual role-v3 sources, and the global
runner.  Neither B nor that final closure exists.  The integrated ledger
therefore remains `P0=0/P1=2/P2=4`; there is no materialization, probe, plan,
bundle, request, external commitment, execution, output, receipt, replay,
B06 preparation or clearance, same-member acceptance, C1--C3, F0--F3, root
transfer, release, or submission promotion.

## 6. B06 decision rule

`B06_structural_remedy_prepared=true` requires all of the following:

- every role-8, role-9, and role-10 method points to candidate-native
  result-blind producer/verifier code;
- `exact_fraction_expression_dag_v2` is a real method entry rather than only
  a parameter record;
- mass/flux and symbolic-composition methods are also bound;
- every method binds its complete transitive code/runtime dependency closure;
- output schemas, role scope, parameter digest, normalization, units, and
  backend-independence status are explicit;
- no method source binds a legacy member, current role result, or current
  result-tree digest; and
- the frozen operation DAG is acyclic and matches Section 3.

Those conditions prepare the structural remedy but do not clear B06.
`B06_cleared=true` additionally requires a genuine external predecessor
commitment and a fresh ordered replay under that commitment.  Same-member
acceptance, C1/C2/C3, F0--F3, release, and submission remain separate later
gates.

## 7. Required adversarial attacks

At minimum, the candidate-native test suites must reject:

- any current role-8, role-9, or role-10 artifact path or digest in source or
  request authority;
- a writable, symlinked, or multiply linked request, input, code, or output;
- a request substituted after commitment or an output substituted before
  validation;
- an unknown report-local import or incomplete native-library closure;
- a role-8 read of role 9 or role 10, or a role-9/10 read of any primitive
  result;
- a result hash, result-derived policy, or acceptance value in a precommit
  request;
- noncanonical JSON, duplicate keys, floats, bool/integer aliases, non-NFC
  strings, unsafe paths, or noncanonical rationals;
- partition, wrapped-periodic, endpoint-half-volume, unit, normalization, or
  storage-order drift;
- empty common-flux intersection, hull substitution, or overlap promoted as
  an exact common-flux proof;
- `M^pi` derived from `pi_h`, per-axis normalization in place of the single
  global gauge, or accidental normalization of `M_L` to one;
- duplicate or missing `W^-1`;
- conflation of `V`, `B V`, `K`, and `B K`;
- a same-backend precision sentinel advertised as backend independence;
- a mutation rejected only by an earlier permission gate rather than by the
  intended semantic check; and
- materialization of the largest tensor rather than bounded streaming.

## 8. Present implementation ledger

As of this note:

```text
legacy dependency and result-binding audit       = COMPLETE
candidate-native responsibility/DAG contract     = THIS NOTE
outcome-free role-3 factorization candidate       = INDEPENDENTLY ACCEPTED INTERNAL COMPONENT
standalone v3 method-parameter registry           = HISTORICAL; NONTERMINAL
standalone v4 method-parameter registry           = INDEPENDENTLY ACCEPTED INTERNAL PRECOMMIT AUTHORITY
successor structural member v4                    = INDEPENDENTLY ACCEPTED STRUCTURAL MEMBER ONLY
successor anti-vacuity policy v4                  = INDEPENDENTLY ACCEPTED INTERNAL RESULT-BLIND POLICY
generic exact-Fraction/formal DAG producer/verifier = INDEPENDENTLY ACCEPTED; P0/P1/P2 ZERO
candidate-native role-8 primitive v1              = TRANSITIONAL; NOT COMMITTABLE
candidate-native role-8 primitive v2              = HISTORICAL PLAN-V1/REQUEST-V3 COMPATIBILITY SHELL
candidate-native role-9 primitive v1              = TRANSITIONAL; NOT COMMITTABLE
candidate-native role-9 primitive v2              = HISTORICAL PLAN-V1/REQUEST-V3 COMPATIBILITY SHELL
candidate-native role-8 v3 basenames               = 2/2 FROZEN CLI HOLD SENTINELS; 0/2 NUMERICAL
candidate-native role-9 v3 basenames               = 2/2 FROZEN CLI HOLD SENTINELS; 0/2 NUMERICAL
role-10 operation model v1                        = HISTORICAL; REJECTED/SUPERSEDED BEFORE COMMITMENT
role-10 operation model v2                        = PROSPECTIVELY FROZEN CONTRACT ONLY; P0=0/P1=0/P2=2
plan-v2 static vocabulary/validator               = FROZEN STATIC SCOPE ONLY; 42/42; P0=0/P1=0/P2=4
live runtime-closure feasibility                   = P1 HOLD; VERSIONED VALIDATOR REPAIR REQUIRED
static runtime byte-pin inventory                  = FROZEN COMPONENT ONLY; 92/92; NO JSON/ROOT/PROBE
generic isolated-process supervisor                = FROZEN COMPONENT ONLY; 32/32 + 5 LOOPS
plan-v1/request-v3 role entrypoints               = HISTORICAL COMPATIBILITY SHELLS ONLY
role-10 sealed-authentication mirror              = INDEPENDENTLY AUDITED; P0/P1/P2 ZERO
candidate-native role-10 numerical primitive      = NOT IMPLEMENTED / NOT EXECUTED
mass/flux composition producer/verifier           = NOT IMPLEMENTED
complete transitive/runtime closure registry      = NOT IMPLEMENTED
runtime-closure-v1 / replay-plan-v2 / bundle-v2   = ABSENT / ABSENT / ABSENT
global roles-8--10 runner v2                      = NOT IMPLEMENTED
B06 structural remedy prepared                    = FALSE
external predecessor commitment                   = ABSENT
fresh role-8--10 replay                           = NOT PERFORMED
same-member acceptance                            = FALSE
```

This ledger must be updated from current bytes and independent test evidence;
the design alone is not completion evidence.
