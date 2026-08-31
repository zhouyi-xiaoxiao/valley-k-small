# Round 60: positive-budget canonical closure independent re-audit

Date: 2026-07-14  
Role: independent read-only reconstruction and claim-boundary re-audit  
Verdict: **PASS-CANONICAL-CLOSURE / PASS-ROUND-59-AFTER-WORDING-REPAIR /
HOLD-PRR-PROJECT**

## 1. Scope and non-execution boundary

This round independently checked the public canonical result, two-process
reproducibility record, independent-audit JSON, frozen manifest and pins, and
the original Round-59 closure report. It did **not**:

- run or import the positive-`B` numerical producer;
- run the canonical auditor a second time;
- execute any semigroup or finite-volume mesh solve, or rerun any producer
  calculation;
- edit the manifest, any pinned file, or any of the three canonical JSON files;
- read or recreate a hidden replica; or
- edit the manuscript or README.

The checks below use only standard-library JSON/hash/arithmetic reconstruction
and direct inspection of the already published artifacts. The canonical audit
remains the single frozen-protocol invocation reported by Round 59.

## 2. Overall assessment

### Scientific assessment: ready to admit at the fixed-control scope

The exact result/evidence/audit hash chain is intact. All 14 manifest pins are
ordinary nonsymlink files and match. The released root times, topology, peak and
valley ratios, three basin masses, final survivals, two-mesh differences, and
tight-margin arithmetic all independently reconstruct from the canonical
result. The two-process record is internally exact and the independent audit
correctly says that it did not witness either subprocess or rerun the semigroup.

The scientific conclusion remains:

```text
PASS-FIXED-CONTROL-POSITIVE-B
HOLD-ALLOCATION-CUSP
HOLD-CONTINUUM-AND-UNBOUNDED-DOMAIN
HOLD-INDEPENDENT-SOLVER
HOLD-PHYSICAL-D3
HOLD-PRR-PROJECT
```

### Round-59 reporting assessment: two wording issues found and repaired

The original Round-59 file had no numerical, hash, topology, or decision error.
It had two avoidable wording ambiguities:

1. one sentence could be read as saying that the auditor independently
   reconstructed **all** gates, including quantities whose full state vectors
   were not saved; and
2. the negative-claim block did not distinguish serialized false Boolean fields
   from claim statuses kept false by the forbidden-promotion contract.

Both were repaired in Round 59 with prose-only edits. The admitted scientific
scope and every displayed number are unchanged. Open finding count after repair:

```text
P0 = 0
P1 = 0
P2 = 0
```

## 3. Hash and frozen-input verification

The supplied original Round-59 SHA was independently reproduced before the
wording repair. The repaired hash is recorded separately.

| Role | Independently observed SHA-256 | Verdict |
|---|---|---|
| Round 59, original supplied snapshot | `791870e2be6e9eafe4019c0ad6194a9bf8e757f925231416b37fd8949223748d` | MATCH before repair |
| Round 59, repaired prose-only snapshot | `c7825396ed44ac50017b599a6a4b1a43f8f0f531db5173f1b88a67fa9011a72f` | CURRENT |
| numerical manifest | `955e59bf333b5fd70e415a53dc26becae9c7a34c5d40f1230c96b1dab8f5677c` | MATCH |
| canonical result | `51e8eb4bdb652124865d0c39e6f36b99d13ed61578b161e0f75b142cada49401` | MATCH |
| two-process evidence | `6c0eccaae09ef95923843ddd7a141a27311e1575ee68d3301b4757b785ee9890` | MATCH |
| independent audit JSON | `60c541a6f0decd5431cefa5c203311176e61006586ce69043d5fcf5380ed517d` | MATCH |
| canonical auditor source | `8e84d8930393e4ba60a906519eef7f1734c713a273791153a55d1f6f16ec3985` | MATCH |
| original auditor tests | `757807729bee2dc9832bb741ba589843cd835e564aead0df7a67982b8a421fe0` | MATCH |
| Round-40 auditor attacks | `4d81932ab193eec77659d8262120cf49183528ac7e37501bc65c22b0d90e1b2a` | MATCH |
| Round-42 auditor attacks | `603aee3b506f1fcf348a06f8f784be4144eb65965e891861c498697743af237f` | MATCH |
| auditor resolution tests | `411a25081d48bc235ab78cc82d65a28ba00a87e775f72c406e907b08113669f3` | MATCH |
| Round-45 auditor attacks | `cec616f487337c6106aca664484fc930a148d5332187ffe6de47c74f03c35855` | MATCH |
| frozen post-result protocol v2 | `d92e5ff2f238a4abb84b8534442122587a98793184f724357f6dc72039ac564b` | MATCH |
| Round-51 protocol audit | `e935007c0aa79bd19c6f9ace4304b33e15782fbee3b2d552579423e0f0372af0` | MATCH |

The manifest contains exactly 14 pin roles. Independent `lstat` and SHA-256
checks gave:

```text
14 / 14 regular files
14 / 14 nonsymlinks
14 / 14 hashes matched
```

The three canonical JSON files are also regular nonsymlink files, parse as
finite JSON, and retain the three Round-59 hashes after the prose repair. Both
hidden replica paths are absent.

## 4. Exact result/evidence/audit chain

The following equalities were checked directly:

1. Result, evidence, and independent-audit JSON all cite manifest
   `955e59...677c`.
2. The reproducibility record's `canonical_result_sha256` equals the observed
   result SHA; both entries of `replica_result_sha256` equal that same SHA.
3. The independent audit's `canonical_result_sha256` equals the observed result
   SHA and its `reproducibility_evidence_sha256` equals the observed evidence
   SHA.
4. The independent audit cites the observed auditor-source SHA.
5. The result's physical inputs, `B=0.01`, fixed weights, mesh identities, and
   required negative flags match the manifest exactly.
6. The weights are all positive, have minimum
   `0.0857172266153233`, and sum to `0.9999999999999999` in binary64; the
   result records `weights_refit=false`.
7. The result status, evidence status, aggregate gates, and independent-audit
   status are mutually consistent PASS values.

No missing, additional, nonfinite, or inconsistent claim-bearing value was
found in the inspected canonical chain.

## 5. Independent numerical reconstruction

### 5.1 Root topology and released scalar values

The canonical roots are strictly ordered. The sign of `f_tt` independently
recovers `maximum--minimum--maximum--minimum--maximum` on both meshes.

| Quantity | Mesh 113 | Mesh 129 | Round-59 display |
|---|---:|---:|---|
| root 1 | `3.3367649300617077` | `3.3066991730834485` | MATCH |
| root 2 | `5.094308494728989` | `5.085151669158436` | MATCH |
| root 3 | `8.622283801381938` | `8.588476632538264` | MATCH |
| root 4 | `13.561466700696581` | `13.529173700011155` | MATCH |
| root 5 | `22.54889593965799` | `22.51481807006199` | MATCH |
| peak min/max ratio | `0.8333934839503558` | `0.8391414832973296` | MATCH |
| valley ratios | `0.7823931607402063`, `0.8467280181266086` | `0.7646777489256341`, `0.8437520432151757` | MATCH |
| basin masses | `0.0052114278399768565`, `0.01662828849270659`, `0.14837901353866123` | `0.005227839493313069`, `0.01659738181932957`, `0.14848157030018083` | MATCH |
| survival at 100 | `0.8297812701286553` | `0.8296932083871765` | MATCH |

For each root, the saved scaled quantities were independently reconstructed as

```text
scaled residual  = abs(t * f_t / f)
scaled curvature = t^2 * f_tt / f.
```

Every reconstructed value equals the saved value at binary64 comparison
precision. The largest scaled root residual is
`2.0226874164196945e-13`, below `1e-8`; the smallest absolute scaled curvature
is `2.188110903419047`, above `0.05`.

The peak ratio was independently recomputed as the smallest divided by the
largest of the three peak densities. Each valley ratio was recomputed as its
valley density divided by the smaller adjacent peak density. All four values
match the result, audit JSON, and Round-59 rounding.

### 5.2 Basin masses and survival closure

Writing the two retained valley survivals as `S(v1)` and `S(v2)`, the three
values were reconstructed without using the saved basin-mass array:

```text
M1 = 1 - S(v1)
M2 = S(v1) - S(v2)
M3 = S(v2) - S(100).
```

For both meshes, these values equal the saved basin masses. Their sum equals
`1-S(100)` at the saved precision, and the stored partition discrepancy is
exactly zero. All six masses exceed the frozen `0.005` floor.

### 5.3 Two-mesh agreement

| Metric | Independently recomputed | Frozen ceiling | Verdict |
|---|---:|---:|---|
| maximum paired-root-time difference | `0.0340778695959969` | `0.10` | PASS |
| peak-ratio difference | `0.005747999346973787` | `0.03` | PASS |
| maximum valley-ratio difference | `0.017715411814572146` | `0.03` | PASS |
| maximum basin-mass difference | `0.00010255676151960103` | `0.01` | PASS |
| final-survival difference | `0.00008806174147879542` | `0.02` | PASS |

These are the exact values in both the canonical result and independent-audit
JSON. Every rounded value displayed in Round 59 is correct.

## 6. Tight-margin arithmetic

Round 59 correctly highlights the two scientifically tightest per-mesh margins:

```text
smallest mass                   = 0.0052114278399768565
mass minus 0.005 floor          = 0.00021142783997685644
relative margin versus floor    = 4.228556799537129 percent
Round-59 rounded percentage     = 4.23 percent

largest valley ratio            = 0.8467280181266086
0.85 ceiling minus ratio        = 0.003271981873391394
Round-59 rounded difference     = 0.0032719818733914

largest cross-mesh valley diff  = 0.017715411814572146
frozen agreement ceiling        = 0.03
```

There is no arithmetic discrepancy. These margins justify the later
parity/alignment, box, fine--large, and independent off-lattice program. They do
not weaken the frozen fixed-box PASS, but they prohibit describing the point as
high-margin, continuum robust, or independently validated.

## 7. Two-process statement and auditor independence boundary

### 7.1 What the saved two-process record establishes

The reproducibility JSON has the exact schema and values:

```text
independent_process_count = 2
execution_order = sequential
replica_exit_codes = [0, 0]
replica_result_sha256 = [canonical SHA, canonical SHA]
byte_identical = true
canonical_promotion_after_comparison = true
```

This is internally consistent two-process evidence. It does not itself let this
re-audit witness historical process execution. The independent-audit JSON
correctly stores both

```text
two_process_evidence_record_consistent = true
independent_process_execution_observed_by_auditor = false.
```

Round 59 states this boundary correctly.

### 7.2 What the canonical auditor did independently

The saved result is sufficient to algebraically reconstruct:

- scaled root residuals and curvatures;
- conditional peak and valley ratios;
- conditional event-basin masses and closure;
- tangent-row time-jet differences and summary maxima;
- tail checkpoint summaries; and
- two-mesh agreement metrics and gates.

The auditor could only re-evaluate **producer-reported certified values** for:

- full-scan minimum density and state component;
- full-scan maximum adjacent survival increase and mass-balance residual;
- the generator killing/mass-balance identity residual;
- root minimum-state components and mass-balance residuals;
- direct-versus-tangent state-norm residuals; and
- finite-volume factor quadrature and row-sum diagnostics.

It did not independently regenerate the full state vectors, locate roots using
a second semigroup, or rerun the FV calculation. The repaired Round-59 wording
now preserves this exact distinction next to the gate summary.

## 8. Negative flags and strongest admitted wording

### 8.1 Serialized negative flags

The canonical result contains the following five false flags both at top level
and in an identical `required_claim_flags` mapping:

```text
preregistered_discovery = false
continuum_interval_verified = false
unbounded_domain_FV_limit_verified = false
independent_solver_verified = false
project_gate_passed = false
```

The independent audit repeats them and adds:

```text
allocation_cusp_verified = false
fixed_box_two_mesh_semidiscrete_point_only = true
```

It also correctly records that it did not observe process execution. The names
`physical_d3_verified` and `publication_gate_passed` are intentionally forbidden
from appearing in the canonical result. Their promotion remains false through
the manifest's forbidden-promotion list, the result's explicit limitation
`no physical d=3 or project/publication gate`, and the frozen post-result
protocol. The repaired Round-59 report now distinguishes absent forbidden keys
from serialized false flags.

### 8.2 Strongest wording admitted

The strongest supported sentence is:

> At `B=0.01`, the result-informed broad-four-slab fixed control (an unchanged
> allocation selected from the leading free-exposure design) has at least three
> event-mass-qualified modes on the declared finite-time window on two held-out
> odd finite-volume meshes in one fixed reflected box and the same solver
> family.

Every qualifier is material. In particular, this result does not establish:

- an allocation cusp, either fold branch, or a phase diagram;
- an exact global count of three modes;
- interval certification;
- mesh/parity or box convergence;
- a continuum or unbounded-domain FV limit;
- an independent killed-process solver;
- physical-`d=3` positive-budget modality; or
- a project/publication/PRR gate.

## 9. Findings and repairs

### Repaired P1-1: gate-independence wording

The original Round-59 sentence “the independently reconstructed gates all
passed” was broader than the frozen independence boundary because some gates
depend on producer-reported extrema/residuals whose underlying states are not
saved. The surrounding text already denied a semigroup rerun, so this was a
reporting overstatement rather than a canonical-audit or numerical failure.

**Repair:** Round 59 now separates algebraically reconstructed gates from gates
re-evaluated using producer-reported certified values and explicitly denies
state/semigroup recomputation. **CLOSED.**

### Repaired P2-1: negative-flag serialization and exact qualifier wording

The original false-claim block did not say which names are actual JSON fields.
Its admitted sentence encoded the design provenance and unchanged control but
did not use the exact material phrases `result-informed` and `fixed control`.

**Repair:** Round 59 now distinguishes the five canonical-result flags, the
audit-only allocation-cusp flag, and the two forbidden absent result keys; the
admitted sentence now carries the exact material qualifiers. **CLOSED.**

No canonical artifact, manifest, pin, scientific threshold, value, or decision
was changed by either repair.

## 10. Final decision

After independent re-hashing, arithmetic reconstruction, claim review, and the
two prose repairs:

```text
Round-59 fixed-control scientific PASS: CONFIRMED
Canonical hash chain: PASS
All 14 pins: PASS
Root/ratio/mass/survival arithmetic: PASS
Two-mesh agreement arithmetic: PASS
Tight-margin arithmetic: PASS
Two-process record consistency: PASS, NOT INDEPENDENTLY WITNESSED
Auditor independence wording: PASS AFTER REPAIR
Negative-claim boundary: PASS AFTER REPAIR
Open P0/P1/P2: 0 / 0 / 0
Overall PRR project: HOLD
```

The fixed-control positive-`B` point is a genuine and necessary result. It is
not the missing same-family allocation cusp, continuum/box/parity closure, or
independent unbounded killed-process validation.
