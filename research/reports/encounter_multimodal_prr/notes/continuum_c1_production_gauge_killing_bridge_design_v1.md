# Two-stage production gauge and killing bridge design v1

Date: 2026-07-17

Status: **FAIL-CLOSED DESIGN ONLY / CORRELATED IDEAL MEMBER NOT YET MATERIALIZED / PRODUCTION APPLICATION BRIDGE HOLD / COMPLETE C0-C1 FALSE**

## 0. Purpose and nonclaim boundary

The abstract varying-space theorem is now locally audited, but the production
pipeline still stores ungauged stationary primitives, directed rate
enclosures, and a control-free contact/support factor bundle.  Those objects
do not yet bind one global gauged ideal operator, physical stationary cell
masses, the map ratio `rho`, or the reconstructed killing multiplier.

This note specifies the missing C1/C4 bridge as two stages: a result-blind,
control-free symbolic stage and a later, separately authorized control/budget
application stage.  It is a prospective schema and algorithm, not a PASS
receipt.  This design-note derivation reads no result, control-value,
positive-budget, scratch, root, propagation, or topology payload.  It does not
authorize construction of a concrete killing field, F0/F1/F3 execution,
complete C0/C1, C2/C3, release, or submission.

The design is pinned conceptually to the following current report-relative
objects; a hash without its bound path is not a source binding:

- C0 mathematical source,
  `artifacts/data/continuum_c0_mathematical_source_v2.json`, SHA-256
  `522bd667e5f6fd6a4d12f270f0c2f4b9e86be9b207d471961d4f67db972df559`;
- control-free configuration source,
  `artifacts/data/physical_configuration_family_control_free_v1.json`, SHA-256
  `063913c7fbc2b706ba85a0e3f06005bad23a2292749817294cbf41f5cdce4084`;
- control-free killing geometry authority,
  `artifacts/data/physical_killing_geometry_source_v1.json`, SHA-256
  `5543f76031d731cb5bcf3e4cdf3bdabaffacb2053400e3015d6ab57906a27669`;
- existing embedded factorization-contract object at
  `artifacts/data/physical_production_killing_geometry_v1/bundle.json#factorization_contract`,
  canonical-object SHA-256
  `de42fefbfc163fdcffd573d49d1156d761341c78b3756903755579dc8e9b23af`;
- Round-4 C1 ideal-refinement contract,
  `artifacts/data/continuum_c1_ideal_refinement_contract_candidate_v1.json`,
  SHA-256
  `93b13d8c6864c54896ff2d71d143856554d8e2de94acd8ba4f43cc3a2534987b`;
- Round-5 varying-space theorem,
  `notes/continuum_c1_varying_space_resolvent_mosco_candidate.md`, SHA-256
  `0b9728535ed0216bc00d5ccb911575dd30bb531422130b2f7e2502a046f134f1`.

The embedded factorization object is candidate provenance, not yet the
standalone immutable `factorization_source` required below.  It must be
materialized and independently hash-pinned before that source role can pass.

The current killing-geometry candidate bundle at
`artifacts/data/physical_production_killing_geometry_v1/bundle.json` has
SHA-256
`f29c29360f3d7db58694aeaeddc7cae8e1eaaac25d8ce6d5792a9ebacf455684`,
but its separate-source verification remains same-backend/design-status and
does not by itself authorize this bridge.  It must remain an input candidate,
not an accepted conclusion.

## 1. Exact target identities

### 1.1 One global fixed-box gauge

An immutable `reference_density_source` must first define the exact density
`pi`, all physical parameters, its normalization convention, coordinate order,
and units.  An immutable `ideal_formula_source` must separately freeze the raw
primitive formula `mu_i^a=nu_i^a exp(-Phi_a(x_i))`, including the definition of
`nu_i^a`, the exact Scharfetter--Gummel/Bernoulli directed-rate formula, and the
periodic primitive.  This note does not manufacture any of those formulae from
production centres.

For each axis `a in {z,r,y}`, let `mu^a_i` denote the resulting exact ideal raw
stationary primitive and put

\[
 S_a=\sum_i\mu_i^a.
\]

For the product box, let

\[
 M_L=\int_{\Omega_L}\pi(x)\,dx,
 \qquad
 \widetilde\pi_{h,(i,j,k)}=\mu_i^z\mu_j^r\mu_k^y.
\]

The only permitted production gauge is

\[
 G_{h,L}=\frac{M_L}{S_zS_rS_y},
 \qquad
 \pi_{h,(i,j,k)}=G_{h,L}\widetilde\pi_{h,(i,j,k)}.
 \tag{1.1}
\]

The periodic convention is fixed, not inferred: if `Y_b` is a possibly wrapped
physical periodic cell, then `mu_b^y=|Y_b|`, `S_y=W`, and
`M_b^{pi,y}=|Y_b|/W`.  With this convention the ideal product source gives the
analytical factorization `g_h^z g_h^r/W`.  Replacing `mu_b^y=|Y_b|` by the
normalized primitive `|Y_b|/W` is a different convention and must fail closed.
The implementation must nevertheless compute and certify the single global
scalar in (1.1).  Multiplying independently rounded axis gauges, normalizing
each axis to one, normalizing each row, or applying cellwise gauges is a
different object and must fail closed.

### 1.2 One common conductance per undirected edge

For an axis edge `i<->i'`, exact detailed balance defines one raw common flux

\[
 \kappa_e=\mu_i^a q^a_{i\to i'}
          =\mu_{i'}^a q^a_{i'\to i}.
 \tag{1.2}
\]

For the tensor edge at fixed coordinates on the other axes,

\[
 c_e=G_{h,L}\,\kappa_e
     \prod_{b\ne a}\mu_{x_b}^b.
 \tag{1.3}
\]

The theorem member is generated structurally from this same `c_e` and the
same gauged endpoint masses:

\[
 q_{xx'}=\frac{c_e}{\pi_{h,x}},
 \qquad
 q_{x'x}=\frac{c_e}{\pi_{h,x'}},
 \qquad
 q_{xx}=-\sum_{x'\ne x}q_{xx'}.
 \tag{1.4}
\]

Independently selected forward/backward binary64 centres are not this ideal
member and need not be reversible.  They may be enclosed and charged to
`E_eval`; they cannot define the theorem object.

### 1.3 Exact physical-volume killing averages

For the tensor cell

\[
 C_{mab}=M_m\times R_a\times Y_b,
\]

the quotient physical-volume measure is
`dx=dM dr_parallel dY` (written below as `dM dR dY`).  The longitudinal map
`M=(X_1+X_2)/2`, `R=X_1-X_2` has unit absolute Jacobian, and the transverse
relative/common-coordinate change preserves Haar measure.  Integrating out the
common transverse coordinate produces the explicit `W^{-1}` normalization in
the quotient density.  These Jacobian and Haar statements, including any
constant under a future coordinate convention, must be proved and hash-pinned
in the reference-density and factorization authorities; they may not be
inferred from array shapes.

The current control-free geometry candidate purports to supply outward
enclosures of the exact physical-volume averages

\[
 \Phi_{jm}=\frac1{|M_m|}\int_{M_m}\phi_j(M)\,dM,
 \qquad
 C_{ab}=\frac1{|R_a||Y_b|}
 \int_{R_a\times Y_b}{\bf1}_{\rm contact}(R,Y)\,dR\,dY.
 \tag{1.5}
\]

The compact-bump and partial disk integrals are generally irrational exact
reals.  Stored binary64 endpoints are exact dyadic rationals enclosing those
reals; they are not the exact averages or distinguished centres.  Exact
zero/full contact cells remain genuine `0/1` values.

A future sealed control source must map every finite control id to exactly
four nonnegative rational weights `w_j^(c)` with exact row sum one.  The first
application schema explicitly requires `w_j^(c)>0`; zero weights require a
separately audited successor schema and hash rather than a silent parser
relaxation.  The symbolic continuum field is

\[
 V_c(M,R,Y)=W^{-1}{\bf1}_{\rm contact}(R,Y)
             \sum_jw_j^{(c)}\phi_j(M).
\]

Fubini on the actual Cartesian product cells, including endpoint half volumes
and wrapped periodic segments, gives

\[
 V_{h,c,mab}=W^{-1}C_{ab}\sum_jw_j^{(c)}\Phi_{jm}.
 \tag{1.6}
\]

The current family has `W=1`, but the schema must retain and test the explicit
`W^{-1}` factor.  A global budget `B` is applied later:

\[
 k_{h,c,mab}=B\,V_{h,c,mab}.
 \tag{1.7}
\]

The symbolic bridge contains no weight values and no budget value.  A later
native budget source stores `B`, its units, admissible sign, exact
representation, and semantic provenance; its own path and hash are added only
by the later outer-open manifest and receipt.  No application default or
self-hash is permitted.

### 1.4 Map ratio and reconstructed multiplier

The continuum stationary mass of a physical cell is an independent quantity:

\[
 M_x^\pi=\int_{C_x}\pi(x)\,dx.
\]

The exact map ratio and reconstructed multiplier are

\[
 \rho_x=\frac{M_x^\pi}{\pi_{h,x}},
 \qquad
 K_{h,c,x}^{pc}=\frac{V_{h,c,x}}{\rho_x}
 =\frac{V_{h,c,x}\pi_{h,x}}{M_x^\pi}.
 \tag{1.8}
\]

These identities give

\[
 M_x^\pi K_{h,c,x}^{pc}=\pi_{h,x}V_{h,c,x}.
 \tag{1.9}
\]

The distinction is mandatory:

- the discrete kernel diagonal is `k=B*V`;
- the reconstructed continuum multiplier is `B*K=B*V/rho`.

Production must never replace the kernel diagonal by `B*K` or `k/rho`.

## 2. Primitive source roles

The bridge must use separate immutable roles rather than one recursively
self-certifying artifact.  A `bootstrap_trust_set`, fixed externally by an
independently audited predecessor receipt or invocation, contains the
`operation_model_source`, `verifier_entry_source`, and any report-local verifier
dependency closure.  Before reading any outer-open manifest, the operation
model binds all those paths/hashes, the expected
outer-open-manifest path/hash and schema, all resource caps, and the two-repeat
snapshot policy.  The outer-open manifest cannot authorize itself and does not
list the bootstrap set.  The following list names every dependency role; the
explicit stage-specific read sets after the list decide which are payload
inputs and which are bootstrap or output artifacts:

1. `reference_density_source`: exact `pi`, normalization, physical parameters,
   coordinate order, units, `W`, and the periodic convention;
2. `ideal_formula_source`: the raw `mu`, SG/Bernoulli directed-rate, periodic,
   gauge, common-flux, map, and reconstruction formulae, independent of every
   production centre;
3. `factorization_source`: a future standalone immutable authority for the
   exact contact/profile factorization; the current embedded object cannot yet
   fill this role;
4. `configuration_source`: ids, axis roles, alignments, sizes, shapes, exact
   half volumes, wrapped segments, period, and joint refinement labels;
5. `member_spec_manifest`: created after roles 1--4 and binding only their
   hashes plus the shared semantic ids; it contains no enclosure-source hash;
6. `outward_method_registry_source`: immutable replay metadata for every
   interval method id, created before the enclosure sources;
7. `anti_vacuity_policy_source`: exact rational width/resource thresholds
   frozen before enclosure sources, with ordering established by an immutable
   predecessor audit/commit/receipt hash rather than by timestamp alone;
8. `raw_axis_enclosure_source`: outward intervals for every `mu_i^a` and
   directed ideal rate, with formula and rounding-method ids;
9. `stationary_integral_source`: independently computed outward intervals for
   `M_L` and every `M_x^pi` from the reference density, never from `pi_h`;
10. `killing_geometry_source`: outward contact and support-average factors with
   exact-real/enclosure semantics;
11. `symbolic_control_method_source`: profile count, nonnegativity, exact-sum
   constraint, finite control ids, and no control values;
12. `future_exact_control_source`: separately sealed rational weight rows whose
    provenance, rather than their mere format, determines whether they are
    result-blind;
13. `future_budget_parameter_source`: separately sealed native `B`, units,
    admissible sign, exact value/enclosure, and semantic provenance, with its
    own path/hash supplied only by role 16;
14. `symbolic_candidate_source`: the immutable output of the control-free
    symbolic construction, retaining its own false acceptance/promotion flags;
15. `symbolic_acceptance_receipt_source`: a distinct immutable independent-
    audit receipt binding the exact symbolic-candidate SHA, verifier/auditor and
    operation-model hashes, `one_correlated_distinguished_ideal_member_is_contained=true`,
    `symbolic_bridge_accepted=true`, and every stronger claim flag false;
16. `outer_open_manifest`: created only after all selected input bytes are
    frozen; it is the sole authority for their real paths and SHA-256 values
    and also binds the acyclic source-dependency DAG; and
17. distinct current-run `symbolic_receipt` and `application_receipt` output
    roles binding the
    `outer_open_manifest` hash and containing
    derived intervals, expression DAGs, streaming digests, resource ledgers,
    and role-specific claim flags.

Each invocation has one stage-specific outer-open manifest.  With `sqcup`
denoting disjoint union, the read sets are exactly

```text
bootstrap_trust_set
  = {operation_model_source, verifier_entry_source}
    sqcup verifier_dependency_closure

bootstrap_open_set
  = bootstrap_trust_set sqcup {outer_open_manifest}

symbolic_payload_open_set
  = outer_manifest_selected_roles_1_through_11

application_payload_open_set
  = {symbolic_candidate_source,
     symbolic_acceptance_receipt_source,
     future_exact_control_source,
     future_budget_parameter_source}

application_policy_input_sources = empty in schema v1

outer_open_manifest not_in either payload_open_set
current_run_output_receipts not_in any read set
bootstrap_open_set intersection stage_payload_open_set = empty
bootstrap_open_counter + stage_payload_open_counter
  = complete_multiset_of_report_file_reads
```

The operation model hash-pins every report-local verifier helper before it is
opened; that exact set is `verifier_dependency_closure`, which may be empty for
a single-file verifier.  The current run writes receipts only after successful
closure and never reopens them as inputs.

The application operation model must verify the symbolic acceptance receipt's
candidate SHA and all named acceptance/stronger-false flags before reading any
control or budget value.  A generic invocation trust anchor cannot waive or
replace that receipt.  Any future extra application policy file requires a new
schema with a named, finite-cardinality role rather than changing the empty v1
set.

No outer-manifest-selected payload source may bind the later
`outer_open_manifest` hash: base specs feed the member-spec manifest, enclosure
sources bind the member-spec hash, and the outer-open manifest then binds all
payload-source hashes.  The bootstrap operation model is the unique source
allowed to bind the expected outer-open-manifest hash before it is read; the
receipts record the verified hash afterward.  The bootstrap set, outer
manifest, anti-vacuity policy, and selected payload bytes all enter both clean-
process snapshots.  Self-edges and back-edges are forbidden.

The symbolic bridge may be frozen before roles 12--13 exist.  It must then
keep `control_specific_killing_constructed=false`.  No placeholder, default,
uniform, centre-derived, or application-code budget/weight may be substituted.

There are two record types.  A source-native record, written before its own
file digest exists, must bind

```text
source_native_interval_record
configuration_id
axis_or_factor_role
cell_or_edge_id
ideal_quantity_id
member_spec_manifest_sha256
physical_parameter_bundle_sha256
configuration_geometry_sha256
partition_sha256
refinement_family_id
refinement_member_id
ideal_formula_id
ideal_formula_version
coordinate_order
normalization_convention
unit
outward_method_id
outward_method_registry_sha256
lower_exact_p_over_q
upper_exact_p_over_q
```

and must not contain or predict its own path or SHA-256.  After the source
bytes and outer-open manifest are frozen, a receipt provenance record adds

```text
receipt_provenance_interval_record
source_role
source_path
source_sha256
source_native_record_schema
source_native_record_key
source_native_record_sha256
```

from the outer-open manifest.  If a native record cites an upstream formula or
method authority, that field is named `origin_source_sha256`; it is never the
digest of the file containing the record.

The native-record digest is the SHA-256 of the ASCII bytes
`encounter-source-native-record-v1`, followed by exactly one byte `0x00`,
followed by `canonical_record_bytes`:

```text
SHA256(ASCII("encounter-source-native-record-v1") || 0x00
       || canonical_record_bytes)
```

Here `canonical_record_bytes` is RFC 8785 JSON Canonicalization Scheme output
after requiring every input string to be Unicode NFC and encoding every
rational as its unique reduced `p/q` string with positive denominator; arrays
retain their schema-frozen order.  Duplicate keys, non-NFC strings, and JSON
floats are rejected before canonicalization.  The record key is the tuple

```text
(source_role,
 member_spec_manifest_sha256,
 partition_sha256,
 refinement_family_id,
 refinement_member_id,
 configuration_id,
 axis_or_factor_role,
 cell_or_edge_id,
 ideal_quantity_id)
```

under the named schema/version.  This complete key must occur exactly once in
its source.  The receipt verifier locates the native record by that key and
recomputes the digest from source bytes; it must not trust a copied digest
field.

JSON floats are forbidden.  Optional production centres are stored only as
exact binary64 hex and must be checked for containment; they never define the
ideal quantity.  Every enclosure role and native entry must bind identical
member/parameter/geometry/partition/formula metadata where it purports to
describe the same exact quantity.  The outer-open manifest determines the path
actually opened.  A receipt-level `source_path` is provenance only: it must
equal the manifest value and must never be followed recursively.

The same no-self-path/no-self-hash rule applies to every selected native source,
not only interval files.  In particular, exact-control and budget native files
store semantic values and upstream authority digests only; their own path and
SHA-256 exist solely in the outer-open manifest and receipt provenance.

For each `outward_method_id`, the registry must bind at least

```text
producer_code_sha256 / verifier_code_sha256
precision_bits / rounding_mode
special_function_backend_and_version
analytic_remainder_rule
method_parameter_sha256
```

The independent verifier may use a different implementation, but its code and
configuration hashes must then be recorded in the receipt.

## 3. Correlated-member semantics

The required acceptance invariant is:

```text
one_correlated_distinguished_ideal_member_is_contained = true
every_cartesian_combination_of_interval_endpoints_is_a_model = false
```

The current design state is instead
`one_correlated_distinguished_ideal_member_is_contained=false`; the true value
above may appear only in a later accepted receipt after the cross-source
bindings, exact formula witnesses, and replay have all passed.

This distinction prevents three false promotions:

1. intervals for masses, rates, gauge, and conductances share source
   dependencies and cannot be selected independently while preserving total
   mass;
2. independently selected directed rate endpoints need not satisfy detailed
   balance; and
3. separately rounded `V`, `rho`, and `K` endpoints need not obey (1.9) as
   pointwise equalities.

A canonical expression DAG must preserve the shared primitives and the one
distinguished exact member.  Interval arithmetic certifies its containment;
it does not certify every endpoint combination.

## 4. Fail-closed outward algorithm

All interval endpoints are canonical exact `Fraction` values.  For
nonnegative intervals,

\[
 [a,b][c,d]=[ac,bd],
 \qquad
 [a,b]/[c,d]=[a/d,b/c]
\]

is permitted only after proving `c>0`.

### Step A: source and contamination closure

- validate the external trust anchor, then open only the exact
  `bootstrap_open_set` consisting of the pinned operation model, verifier entry,
  verifier dependency closure, and operation-model-pinned outer-open manifest;
  verify the latter's path/hash before parsing it;
- use separate exact payload allowlists from that outer-open manifest for the
  symbolic and application schemas, and open only the ordinary report-relative
  paths declared there;
- snapshot/hash before parsing;
- reject duplicate JSON keys, noncanonical rationals, nonfinite values,
  symlinks, hard-link aliases, descriptor drift, oversized/deep inputs, and
  result, scratch, root, propagation, topology, and positive-budget-result path
  components in both stages;
- in the symbolic stage, reject every control-value or budget-value source;
- in the application stage, allow exactly one manifest-declared exact-control
  source and one manifest-declared budget source, with no broader result-tree
  access; these two source-only files are the sole machine-recognized exceptions
  to the control-value/budget-value ban, must themselves have no banned path
  component, and do not authorize any parent or sibling tree;
- record every opened report-relative regular file, regardless of suffix;
  require separate exact read-only Counters for `bootstrap_open_set` and
  the stage-specific `payload_open_set`, require those sets to be disjoint, and require their
  multiset union to equal all report-file opens; separately freeze runtime/
  interpreter/library components that are not report files;
- treat embedded source paths as equality-checked provenance and never follow
  them; and
- require role-specific expected flags: the application may set
  `exact_controls_present=true`, but complete C0--C3, release, submission, and
  science-execution flags remain false.

### Step B: partitions and product identities

Reconstruct every axis partition independently.  Verify positive volumes,
endpoint half volumes, wrapped periodic segments, exact box coverage, shapes,
state counts, period, coordinate order, and the ideal product-mass premise.
Reject any attempt to infer a partition from binary64 centres alone.  Require
all roles claiming the same ideal member to agree exactly on the manifest,
physical-parameter, geometry, partition, refinement-family/member, formula,
normalization, coordinate-order, and unit bindings.  Same textual cell or edge
ids do not establish that equality.

### Step C: single global gauge

First preserve and symbolically verify the exact DAG identities

\[
 \sum_{ijk}\mu_i^z\mu_j^r\mu_k^y=S_zS_rS_y,
 \qquad G(S_zS_rS_y)=M_L,
 \qquad \sum_x\pi_{h,x}=M_L.
 \tag{4.1}
\]

The receipt must record `symbolic_mass_residual_exactly_zero=true`; a wide
interval residual that merely contains zero is not a substitute.  Independently
verify the physical partition identity

\[
 \sum_x M_x^\pi=M_L.
 \tag{4.2}
\]

Only after proving that the box oracle and all cell-mass oracles concern the
same exact density and partition may one form the joint box enclosure

\[
 [M_L]_{\rm joint}=[M_L]_{\rm oracle}\cap\sum_x[M_x^\pi].
 \tag{4.3}
\]

An empty intersection is HOLD.  Compute outward intervals

\[
 [S_a]=\sum_i[\mu_i^a],
 \qquad
 [S]=[S_z][S_r][S_y],
 \qquad
 [G]=[M_L]_{\rm joint}/[S].
 \tag{4.4}
\]

Require positive lower bounds for every factor and denominator.  For each
cell, derive `[tilde_pi_x]` and `[pi_h,x]=[G][tilde_pi_x]`.  Aggregate widths
must meet exact rational anti-vacuity thresholds in the immutable policy source
frozen before any enclosure input; a prior audit/commit/predecessor-receipt hash
establishes the ordering, while a timestamp is auxiliary metadata only.

### Step D: common conductances

For each axis edge compute the oriented flux enclosures

\[
 [F_e]=[\mu_i^a][q_{i\to i'}^a],
 \qquad
 [R_e]=[\mu_{i'}^a][q_{i'\to i}^a].
\]

An independent ideal formula source and oracle must first establish from the
pinned SG/Bernoulli formula and identical cross-source member bindings that
both enclose the same exact `kappa_e` from (1.2).  Only then may the
implementation take

\[
 [\kappa_e]=[F_e]\cap[R_e].
 \tag{4.5}
\]

An empty intersection is HOLD; taking the hull is forbidden.  Mere overlap of
two production intervals, without the independent common-flux proof, is not a
detailed-balance certificate.  Derive tensor `[c_e]` from (1.3), including the
other-axis masses, and generate the correlated ideal rates structurally from
(1.4).  They may be intersected with the original directed rate enclosures;
any empty structural-rate/raw-rate intersection is HOLD.

### Step E: stationary cell masses and `rho`

Compute each `[M_x^pi]` from an independent density-integral oracle, using the
actual half/wrapped cells and exact product measure.  It must not be derived
from `pi_h` or the raw discrete masses.  The box/cell identity (4.2) and joint
enclosure (4.3) must already have passed.  Derive

\[
 [\rho_x]=[M_x^\pi]/[\pi_{h,x}]
\]

only after both lower bounds are strictly positive.  Require finite upper
bounds and a separate asymptotic/refinement ledger; a finite table does not
prove `rho->1`.

### Step F: symbolic and concrete killing

The control-free layer stores the exact monotone enclosure rule

\[
 [V_{h,c,mab}]
 =W^{-1}[C_{ab}]
  \sum_j w_j^{(c)}[\Phi_{jm}]
 \tag{4.6}
\]

symbolically.  After a separately sealed exact control row exists, apply the
same formula with exact rational weights satisfying the first-application
schema policy.  Only a later authorized application may read its separately
sealed budget source,
verify its unit and exact rational/binary64 representation, enforce the
source-declared sign condition (strictly positive for the present positive-
budget target), add `[B]`, and create `[k]=[B][V]`.

Derive the reconstructed multiplier along two exact-equality paths:

\[
 [K]_{(1)}=[V]/[\rho],
 \qquad
 [K]_{(2)}=[V][\pi_h]/[M^\pi].
 \tag{4.7}
\]

After independently checking the exact identity (1.8), one verifier code path
must recompute path 1 from the serialized `[rho]`, while a separate code path
must recompute path 2 directly from primitive `[V]`, `[pi_h]`, and `[M^pi]`.
When `[rho]` was itself derived from those same rectangular primitive
intervals, require the two endpoint pairs to be exactly equal; calling their
intersection independent evidence is forbidden.  Intersection may tighten an
enclosure only if `[rho]` comes from a separately bound independent oracle.
Label `[B][K]` as the reconstructed killed multiplier, never as the discrete
kernel diagonal.

### Step G: streaming and publication

Do not allocate the largest tensor.  Retain axis factors, `C[a,b]`,
`Phi[j,m]`, and the expression DAG; stream cell/edge records in frozen order
through a chunk digest.  A two-repeat outer process may publish only after
byte-identical receipts, distinct clean child processes, complete tree/open
sets, resource caps, and rollback-safe one-shot publication.

## 5. Two distinct candidate machine schemas

The control-free schema is named explicitly:

```text
encounter_c1_gauge_killing_symbolic_candidate_v1
|
+-- source_bindings
|   +-- predecessor trust anchor / operation-model and verifier hashes
|   +-- pinned outer-open manifest / disjoint bootstrap and payload Counters
|   +-- payload paths, SHA-256 values, roles, all-report-file open closure
|   +-- common member/parameter/geometry/partition/formula/unit digests
|   +-- control_value_sources = [] / budget_value_sources = []
|
+-- member_semantics
|   +-- one_correlated_distinguished_ideal_member_is_contained = false
|       until accepted symbolic replay
|   +-- every_cartesian_interval_member_is_a_model = false
|
+-- configurations[]
|   +-- configuration_id / refinement family and member / alignment / shape
|   +-- independent box and cell mass intervals / exact mass DAG identities
|   +-- axes[]: partitions / raw masses / directed rates
|   +-- global gauge / gauged masses / common fluxes / conductances / rho
|   +-- contact averages / profile averages / W / symbolic weight constraints
|   +-- symbolic V / K expression DAGs; no concrete V, k, B*K records
|   +-- streaming digests / maxima / precommitted width ledgers
|
+-- error_ledger
|   +-- ideal_vs_continuum = E_space
|   +-- production_enclosure_and_centre_vs_ideal = E_eval
|
+-- claim_boundary
    +-- exact_controls_present = false / budget_present = false
    +-- control_specific_killing_constructed = false
    +-- symbolic_bridge_accepted = false until independent audit
    +-- complete_C0/C1/C2/C3 = false
    +-- release/submission/science_execution = false
```

The later, separately authorized schema is named explicitly and has a different
key set:

```text
encounter_c1_gauge_killing_control_budget_application_candidate_v1
|
+-- symbolic_candidate_source path / sha256 from outer manifest
+-- symbolic_acceptance_receipt_source path / sha256 from outer manifest
|   +-- candidate sha equality / independent audit identities and hashes
|   +-- correlated-member and symbolic-acceptance flags true
|   +-- complete/release/submission/science-execution flags false
+-- application_source_bindings
|   +-- exactly one sealed exact-control source
|   +-- exactly one sealed budget-parameter source with unit/sign/value
|   +-- application_policy_input_sources = []
|   +-- disjoint exact bootstrap_open_counter / payload_open_counter
|   +-- Counter union equals every report-file open
+-- concrete_application[]
|   +-- exact positive weight rows for the first parser / exact row sums
|   +-- B / V / k=B*V / rho / K / B*K expression DAGs and intervals
|   +-- two-path K endpoint equality or separately justified tightening
+-- claim_boundary
    +-- exact_controls_present = true / budget_present = true after verification
    +-- control_specific_killing_constructed = true only after verification
    +-- end_to_end_evaluator_enclosure = false until propagated
    +-- complete_C0/C1/C2/C3 = false
    +-- release/submission/science_execution = false
```

The symbolic candidate, its independent acceptance receipt, and the later
control application must have distinct paths, schemas, hashes, and open
policies.  A later application must verify the candidate/receipt binding; it
may not rewrite or promote either input.

## 6. Exact rational sanity witnesses

Neutral witnesses should be frozen before implementing production-scale
records:

1. global gauge:
   `M_L=1/2`, `S_z=S_r=1`, `S_y=2`, hence `G=1/4`;
2. common flux:
   `mu_i=2`, `mu_j=3`, `q_ij=3/5`, `q_ji=2/5`, hence both oriented products
   equal `6/5`; with other-axis mass product `5` and `G=1/7`, tensor
   conductance is `6/7`;
3. reconstruction:
   `pi_h=1/4`, `M_pi=3/10`, `rho=6/5`, `V=2/5`, `K=1/3`, and
   `M_pi*K=pi_h*V=1/10`; and
4. nondegenerate interval division:
   `M_pi=[3/10,31/100]`, `pi_h=[1/4,13/50]`, giving
   `rho=[15/13,31/25]`.

These are algebra sentinels only, not physical parameter values or convergence
evidence.

## 7. Required adversarial mutations

At minimum, the verifier must reject:

- replacing `M_L` by one, separate axis normalization, or omitting one axis
  from the global denominator;
- replacing the pinned periodic primitive `mu_b^y=|Y_b|` by `|Y_b|/W`, or
  otherwise changing normalization without a new manifest/formula digest;
- deleting endpoint half volumes or one wrapped periodic segment;
- accepting `0 in residual_interval` in place of exact symbolic mass closure,
  changing `M_L` relative to the physical-cell mass sum, deriving `M_x^pi`
  from `pi_h`, or omitting a product-measure factor;
- swapping forward/reverse edge ids, using an interval hull instead of an
  intersection, or accepting an empty intersection;
- claiming a common ideal flux from overlap alone without an independent
  formula/source witness;
- reusing the same quantity id with a different parameter/geometry digest,
  mixing two refinement members, drifting unit/normalization/coordinate order,
  or following an embedded provenance path;
- creating a self-edge/back-edge in the source-dependency DAG or making an
  enclosure source bind the later outer-open-manifest hash;
- requiring a source-native interval record to embed or predict the SHA-256 of
  the file that contains it, or letting the outer manifest authorize itself;
- making a native control/budget source predict its own path or hash, merging
  the bootstrap/payload open Counters, or omitting either set from full closure;
- listing the outer-open manifest as payload, omitting the symbolic candidate
  or its acceptance receipt from an application payload, or reopening a
  current-run output receipt as input;
- relabelling a candidate as accepted without the independent acceptance
  receipt, changing the candidate SHA bound by that receipt, waiving the receipt
  through an invocation flag, or adding an unnamed v1 application-policy file;
- omitting refinement/member/partition identity from a native-record key,
  accepting a duplicate complete key, or hashing non-JCS/non-NFC record bytes;
- omitting the two spectator-axis masses from a tensor conductance;
- generating a matrix from independent rate endpoints and claiming every
  member is reversible;
- transposing the row/column convention, using a positive diagonal, omitting a
  neighbour from the diagonal sum, or producing a nonzero row sum;
- inserting `1/2` into a single-count undirected-edge form, or deleting `1/2`
  from an equivalent double-count directed-edge form;
- substituting a point sample for either physical-volume average;
- deleting `W^{-1}`, one contact/profile factor, or one weight;
- accepting `w_j<=0` in the first-application schema, a nonunit exact weight
  sum, a wrong profile mapping, or an unsealed control source;
- accepting a budget with the wrong path, hash, sign, unit, or exact
  representation, or reading a default budget from application code;
- confusing `V`, `k=B*V`, `K=V/rho`, or `B*K`;
- inverting `rho`, setting it to one, or dividing by an interval whose lower
  endpoint is zero;
- calling the two algebraically identical rectangular `K` paths independent,
  or implementing both purported verifier paths with the same faulty helper;
- using a production centre plus empirical padding to define the ideal;
- choosing or loosening an anti-vacuity cap after reading the enclosure data;
- failing to recompute a derived interval from primitive endpoints;
- charging production width to `E_space` or a spatial defect to `E_eval`;
- materializing the largest tensor despite the factorized contract;
- source-path/hash/open-count drift, extra data opens, writes during audit,
  duplicate JSON keys, noncanonical rationals, symlinks, TOCTOU, or claim-
  promotion mutations.

## 8. Error ownership

The following separation is nonnegotiable:

```text
E_space:
  exact ideal finite-volume/form/map/contact discretization versus continuum

E_eval:
  directed integral/rate/gauge/mass/killing enclosures,
  production centre versus the contained distinguished ideal member,
  and downstream interval propagation/roundoff
```

Primitive interval width is not yet the final observable `E_eval`.  An
end-to-end semigroup/observable enclosure must propagate the expression-DAG
uncertainty.  Conversely, a point-sampling or cut-cell approximation defect is
not roundoff and must not be hidden inside `E_eval`.

## 9. Current blockers and honest decision

The current design makes no promoted scientific claim and has no certified
scientific error budget.  False flags do not imply that the candidate inputs
or design are error-free.  Promotion is blocked by:

1. no independently accepted full raw-axis/refinement source for every
   genuine `h->0` family;
2. no independently accepted reference-density/formula authorities binding
   `pi`, raw `mu`, SG/Bernoulli rates, periodic convention, parameters, and
   units;
3. no independent `M_L` and `M_x^pi` enclosure source with physical partition
   closure;
4. no standalone cross-bound exact factorization source or common-ideal-flux
   oracle;
5. no sealed exact rational control rows or budget-parameter source;
6. no accepted separate-source same-backend replay for the geometry factors;
   independent-backend evidence also remains false;
7. no accepted two-stage source/open-policy implementation; and
8. no end-to-end evaluator enclosure containing the distinguished ideal
   member.

The completion layers are distinct:

1. symbolic bridge acceptance requires exact source/formula/member bindings,
   gauge/factor/mass/common-flux verification, the rational witnesses, and an
   independent adversarial audit;
2. control-specific application additionally requires the sealed exact-control
   and budget sources and the application-only open policy;
3. end-to-end evaluator completion additionally requires propagation of the
   contained member through the observable enclosure; and
4. complete C1 additionally requires genuine joint refinement families and
   model-specific qualitative convergence premises, including only the
   consistency estimates needed to prove convergence; computable observable
   error bounds and rates remain C2.

Promoting any layer before its own prerequisites would be a P0 scientific
error.  The next implementation milestone is only the **symbolic,
control-free, false-flag machine contract** plus the four exact rational
witnesses above.  Only after independent adversarial acceptance should the
separate exact-control/budget application be implemented.
