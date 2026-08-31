# Round 6 audit: production global-gauge and killing bridge design

Date: 2026-07-17

Status: **DESIGN ACCEPTED FOR IMPLEMENTATION / SCIENTIFIC PASS FALSE /
PRODUCTION APPLICATION HOLD / COMPLETE C0-C2 FALSE**

## 1. Audited object

The final audited design is

- `notes/continuum_c1_production_gauge_killing_bridge_design_v1.md`;
- 883 lines, 36,810 bytes;
- SHA-256
  `d23c088f917832bb9d8078a046133556e8ee8547d8a062d3102a922881ba67e4`.

It is a result-blind design derivation for a two-stage bridge.  It is not a
symbolic machine artifact, not a concrete control/budget application, and not
a C1 or C2 proof.

## 2. Mathematical identities retained

The final bytes distinguish the following exact objects:

\[
 G_{h,L}=\frac{M_L}{S_zS_rS_y},
 \qquad
 \pi_{h,(i,j,k)}=G_{h,L}\mu_i^z\mu_j^r\mu_k^y,
\]

\[
 c_e=G_{h,L}\kappa_e\prod_{b\ne a}\mu_{x_b}^b,
 \qquad
 q_{xx'}=c_e/\pi_{h,x},
\]

and

\[
 V_{h,c,mab}=W^{-1}C_{ab}\sum_jw_j^{(c)}\Phi_{jm},
 \quad k=B V,
 \quad \rho=M^\pi/\pi_h,
 \quad K=V/\rho.
\]

Thus the discrete kernel diagonal remains `B*V`, while the reconstructed
continuum multiplier is `B*K`.  The design forbids substituting `K` or
`k/rho` into the discrete kernel.

The quotient measure is explicitly `dM dR dY`; the longitudinal Jacobian is
one, the transverse relative/common change preserves Haar measure, and the
`W^-1` quotient normalization remains visible.  The pinned periodic raw-mass
convention is `mu_b^y=|Y_b|`, `S_y=W`, and
`M_b^{pi,y}=|Y_b|/W`.

## 3. Correlated-member and mass closure

The design does not claim that arbitrary Cartesian combinations of interval
endpoints define reversible models.  Acceptance requires one common exact
member bound across density, formula, geometry, partition, refinement,
normalization, unit, raw mass, directed rate, and stationary-integral roles.

The expression DAG must verify exactly

\[
 \sum_{ijk}\mu_i^z\mu_j^r\mu_k^y=S_zS_rS_y,
 \quad G(S_zS_rS_y)=M_L,
 \quad \sum_x\pi_{h,x}=M_L,
\]

and the independent physical identity `sum_x M_x^pi=M_L`.  A residual
interval merely containing zero is not acceptance.  The two box-mass
enclosures may be intersected only after they are proved to concern the same
exact density and partition.

Forward and reverse raw flux intervals may be intersected only after an
independent ideal formula proves that both contain the same `kappa_e`.  Mere
overlap is not detailed balance; every empty common-flux or structural/raw-rate
intersection is HOLD.

## 4. Evidence architecture repairs

The iterative audit converted a prospective prose design into an implementable
acyclic dependency plan:

```text
external trust anchor
  -> operation model / verifier dependency closure
  -> member base specs
  -> member-spec manifest
  -> native enclosure sources
  -> stage-specific outer-open manifest
  -> symbolic candidate
  -> independent symbolic acceptance receipt
  -> separate control/budget application
  -> current-run output receipt
```

Key fail-closed properties are:

- bootstrap and stage payload sets have disjoint exact read Counters whose
  multiset union equals every report-file read;
- an outer manifest never authorizes itself and is not payload;
- current-run output receipts are never reopened as input;
- native interval/control/budget files never predict their own path or hash;
- source-native records and receipt provenance are separate;
- native record keys include member-spec, partition, refinement family/member,
  configuration, axis/factor, cell/edge, and quantity identities and must occur
  exactly once;
- record SHA-256 uses an explicit ASCII domain, one `0x00` byte, RFC 8785 JCS,
  Unicode NFC, and canonical rational strings;
- outward methods bind code, verifier, precision, rounding mode, special-
  function backend, analytic remainder rule, and parameter hashes;
- anti-vacuity policies are immutable predecessor-bound inputs rather than
  data-dependent thresholds or timestamps; and
- application v1 reads exactly the immutable symbolic candidate, its
  independent acceptance receipt, one exact-control source, and one budget
  source; its extra policy set is empty.

The symbolic candidate retains false acceptance/promotion flags.  The separate
acceptance receipt must bind the exact candidate SHA, independent audit
identities and hashes, correlated-member acceptance, symbolic-bridge
acceptance, and every stronger flag as false.  Invocation metadata cannot
waive that receipt.

## 5. Audit chronology

Two independent read-only lines attacked the design repeatedly.  They did not
edit the file, use the network, or read result/control/scratch/positive-budget
payloads.

The initial 516-line bytes had no P0 mathematical error but exposed missing
reference-density, formula, budget, open-set, source-binding, and completion-
layer obligations.  Subsequent rounds found and repaired:

1. a cross-file outer-manifest hash cycle;
2. native-source self-hashes;
3. missing trust-root versus payload separation;
4. an under-specified record locator and JSON canonicalization;
5. ambiguous control/budget exceptions and two-schema policies;
6. physical Jacobian and periodic normalization bindings;
7. a symbolic-candidate acceptance label with no independent witness; and
8. missing application bootstrap/payload Counter provenance.

The final exact bytes received two independent full read-only verdicts:

```text
audit line A: P0=0 / P1=0 / P2=0
audit line B: P0=0 / P1=0 / P2=0
```

The agreement is on the final SHA above, not on an earlier near-final draft.

## 6. Honest decision

The design is accepted only as the implementation authority for a future
symbolic, control-free, false-flag machine contract.  The following remain
false:

```text
symbolic_machine_contract_built       = false
symbolic_acceptance_receipt_built     = false
exact_controls_present                = false
budget_present                        = false
control_specific_killing_constructed  = false
end_to_end_evaluator_enclosure         = false
complete_C0                            = false
complete_C1                            = false
complete_C2                            = false
release_submission_science_execution  = false
```

Complete C1 still requires genuine joint refinement families and the
model-specific qualitative convergence premises.  Computable fixed-box
observable error belongs to C2.  Production interval propagation belongs to
`E_eval`, and neither can be borrowed from this design audit.
