# Superseding active-package notice — 14 August 2026

This notice supersedes the “Authoritative terminal state” and theorem-only
submission instructions immediately below. Those sections are retained as a
historical record of the earlier resource-gated branch; they do **not** describe
or authorize the current PRR submission.

The active article is the single-author manuscript “Prescribing finite-window
reaction-time modes with a static fixed-budget Doi reactivity field,” by
Xiaoxiao Zhouyi. Its source of truth is:

- `manuscript/prr_submission/encounter_multimodal_prr_v2.tex`;
- `manuscript/prr_submission/encounter_multimodal_prr_v2_supplement.tex`;
- `manuscript/prr_submission/references.bib`; and
- the figures and `prr_assets/` files referenced by those sources.

Unlike the superseded theorem-only branch, the current package includes
finite-parameter off-lattice evidence: two 48-cell phase diagrams, operational
budget crossings, geometry and weight jitter campaigns, an `m=5`
demonstration, and a `d=3` spot check. It distinguishes the existential
topological threshold, an explicit sufficient analytic bound, and the
classifier-dependent operational crossing. No numerical continuum theorem is
claimed.

All three related manuscripts are sole-authored. The related manuscripts are
PRE **EU13106** and JCP **JCP26-AR-03623**; they must be disclosed as related
but distinct and supplied to the PRR editors for comparison. Current submission
actions and disclosure wording are in `submission/`. The old 20/30 July
theorem-only PDFs, archives, checklists, author list, and hashes are superseded
and must not be uploaded. A fresh deterministic rebuild, visual inspection,
public reproduction archive, and new hash manifest are required before portal
submission.

# Prescribed finite-window encounter-reaction modality under conserved reactivity

## Authoritative terminal state

The pre-registered largest-shape, control-free resource rehearsal selected
`HOLD_F0_METHOD_OR_RESOURCE`.  The canonical execution completed without
process swapping and within the wall-time allowance, but its measured peak
resident memory and Darwin peak process footprint exceeded the frozen limits.
The limits were not changed after observing the result.

Consequently:

- F0 is not accepted;
- no positive-budget production control was evaluated;
- the 36-row deterministic campaign, its mechanical sampling plan, and the
  dual-pool off-lattice calculation were not run;
- the active scientific result is the independently accepted exact-`m` Doi
  continuum theorem only; and
- strict numerical continuum convergence and componentwise root transfer are
  outside the selected paper and remain conditional on a future, explicitly
  stronger numerical claim.

The active reader sources are
`manuscript/encounter_multimodal_prr_submission.tex` and
`manuscript/encounter_multimodal_prr_submission_supplement.tex`.  Build and
audit them with:

```bash
.venv/bin/python \
  research/reports/encounter_multimodal_prr/code/compile_theorem_first_submission.py
```

The PDFs are published to `output/pdf/`.  The author-owned declarations and
public archive identifier still required before portal upload are listed in
`submission/AUTHOR_ACTIONS_BEFORE_PORTAL_UPLOAD.md`.

The fail-closed terminal aggregation is
`artifacts/data/encounter_prr_terminal_branch_v1.json`.  It records
F0=`HOLD_F0`, F1/F2/F3=`NOT_RUN`, zero formal F1 rows, no refit, and no
scientific authorization.  The clean reader archive is
`output/source/encounter_multimodal_prr_submission_source.tar.gz`.  The final
independent package audit is
`audits/final_submission_independent_audit_20260720.md`.

Everything below this notice is a historical research-program record.  Its
earlier “current,” “open,” or proposed execution statements are superseded by
the terminal state above and must not be used to authorize later stages.

This directory is the independent Physical Review Research project that follows
`encounter_heterogeneous_catalytic`.  It is not a revision folder for that
finite-model paper.  The new paper is gated by a continuum result:

> Under a physically defined conserved reactivity budget, construct and control
> stable multimodal reaction-time densities for prescribed finite designs, and
> verify their modality topology in a resolved encounter model.  For every fixed
> finite integer $d\ge2$, an independently audited theorem gives exactly every
> prescribed fixed finite number of nondegenerate maxima, separated by exactly
> one fewer nondegenerate minima, in a
> $d$- and $m$-dependent narrow-noise slab family of the exact physical Doi
> quotient, after taking the joint noise/slab-width and positive-budget limits
> sequentially.  Relative-prominence-qualified four-slab $B=0$ shapes are confirmed
> by exact physical-$d=2$ disk and physical-$d=3$ sphere kernels; a separate broad-
> patch $B=0$ chain bridges the exact $d=2$ kernel to four finite-volume meshes, and
> one finite-$B$ fold is confirmed on a single mesh.  At fixed $B=0.01$, one
> result-informed broad four-slab allocation, tested without refitting, has three
> event-mass-qualified modes on two held-out odd finite-volume meshes in one fixed
> reflecting box and the same solver family: five retained alternating roots are
> supported by the saved root screen only through $t=35$, while the valley-
> partitioned basin masses and tail checks extend through $t=100$.  This does not
> exclude additional extrema after $t=35$.  The later allocation-v6 cusp campaign
> terminated with `HOLD_SCIENCE_AUDIT_VALID`; it is preserved as a negative result,
> not an open gate to be repaired.  The active route is theorem-first: use the
> accepted exact-$m$ complete-topology theorem, then test prospectively frozen same-budget
> one-/two-/three-mode controls with a full-window interval certificate, all mesh/
> parity/alignment/box challenges, and an independent off-lattice event law.  The
> complete reader-facing proof and its theorem-first main/Supplemental package
> passed the independent hash-specific Round-149 audit with `P0=P1=P2=0`; this
> closes the analytical migration only and promotes no finite-parameter result.

## Scope boundary

- The earlier report establishes finite-generator response identities, spectral
  necessary conditions, and finite-grid mechanism certificates.
- This report adds a constructive exact-topology theory and a weak-budget
  model-specific continuum bridge; the focused finite-parameter evidence still
  required is physical `d=2`, while positive-budget `d=3` is optional unless a
  dimensional headline is used.
- Extra scans of the old sharp-mask discretization do not count as PRR evidence.
- Reduced GIG mixtures are analytical design and screening objects.  They are
  not evidence for a bounded Doi continuum until a uniform remainder or an
  independently converged continuum realization is supplied.

## Evidence gates

| Gate | Required evidence | Current status |
| --- | --- | --- |
| G0 | Reproducible finite-`m` GIG construction (`m=2,...,6`) and nondegenerate reduced cusp | PASS (reduced numerical scope only) |
| G1a | Exact physical-2D quotient operator geometry, budget, positivity, mass, and independent local references | PASS (42 mutation-hardened gates on 15,625 cells; `continuum_verified=false`) |
| G1b | Frozen full-simplex search and one physical-budget 2D fold with odd/even convergence | full simplex PASS; one $B=0.6$, 207,025-state fold PASS; mesh/box convergence open |
| G2 | Same-budget physical-2D control of finite-window modality | historical $B=0$ and one fixed $B=0.01$ point are context only; allocation-v6 is terminal `HOLD`; Round 167 accepts the 12-row control-free source/partition/free-axis/packed-rate preparation, and Rounds 168--170 freeze, independently reconstruct, and two-repeat outer-replay only the control-free factorized killing geometry.  Authenticated fixed-row physical-integral/raw-flux sources, the Round-172 genuine ideal refinement geometry, and the Round-173 ideal source-bound map/cut/killing contract do not constitute correlated production same-member containment.  Round 176 joins those current objects only as a non-promoting `n=0` metadata preflight and leaves nine blockers uncleared.  Round 177 prepares a predecessor-authority candidate and only the structural remedy for the Round-172 partition-hash defect (B04).  Round 178 independently accepts outcome-free factorization-v2, result-blind registry-v4, and structural member-v4 only as internal precommit foundations; the successor result-blind anti-vacuity policy-v4 is also independently accepted at its internal policy scope.  Round 179 prospectively freezes only a result-blind role-10 numerical operation-model v2; it supplies no numerical implementation or execution.  Round 180 freezes only a static plan-v2 vocabulary/validator and a 42-case synthetic mutation suite; no report-local runtime closure, plan, bundle, request, commitment, runner, or result is created.  Round 181 freezes four role-8/9 v3 basename/CLI HOLD sentinels but zero numerical implementations, and its live-runtime probe places the frozen Round-180 validator on a versioned-repair HOLD.  The complete candidate-native method/provenance closure (B06), executable replay plan, external commitment, ordered replay, and all nine blocker clearances remain false.  Concrete killing, the full operator, propagation/topology, the production resource gate, F0, and all 36 F1 rows remain open. |
| G3 | Independent off-lattice event-law validation without refitting | compiled state-dependent-hazard core and 22 method tests PASS; selector process/resource surface passed Rounds 151/153 on macOS (142/142 suite, 120/120 repair replays, 45 independent orphan probes, 8M synthetic gate); second-POSIX and causal second-parent contention handshakes remain P2, and F2/F3 science is unrun |
| G4 | Constructive physical finite-mode theorem plus weak-budget transfer | analytical core accepted in Rounds 118/120 (`ACCEPT-THEOREM-SPINE`); the integrated reader-facing exact-$m$ proof, theorem-first narrative, and frozen source bytes independently passed Round 149 with `P0=P1=P2=0` |
| G5 | Dimensional scope | exact fixed-finite-$d$ theorem is pointwise in $d$; historical physical-$d=3$ $B=0$ shape is context; the focused active numerical claim is physical $d=2$, with no positive-$B$ $d=3$ headline |
| G6 | One publication narrative with clean overlap/priority boundaries | the 7+24-page internal working set passes deterministic build and current full-page PDF QA; it imports no prospective F1/generated positive-budget payload, while overlap/priority closure, release, and submission remain `HOLD` |

The ideal fixed-box theorem layer now closes its scoped C1 composition, while
project-level and production-level complete C1 remain false.  The result-blind C0-v1
contract is immutable historical evidence: its ambiguous “weighted cell
projection” predates the exact-adjoint denominator choice, and its old living-
note source pin now correctly fails closed with `HOLD_C0_CONTRACT_SOURCES`.
The deterministic C0-v2 semantic base uses five C0-only/control-free
JSON sources and does not pin or open the living continuum note, the positive-
budget design note, or any scratch/result payload.  It freezes distinct
`J_h,P_h,A_h,S_h`, the global fixed-box mass gauge, real and optional-complex
form conventions, the row-generator convention, and the exact initial cell
masses; the independent verifier confirms strict support containment in all 12
declared boxes.  A second mathematical attack then found that measurable-
partition and positive-mass well-definedness assumptions were implicit.  The
immutable v2 bytes are therefore retained as a base, and the current C0-v3
wrapper freezes those preconditions explicitly and reconstructs all 36 axis
partitions, including four vertex-dual endpoint-half-volume axes and two
wrapped periodic rows, accounting for all 34,787,462 declared tensor cells.
This remains a local semantic/adversarial candidate only: the exact control
values still require a separately sealed result-blind source, complete C0 is
false, and the raw-to-gauged production bridge remains open.
The current v2/v3 implementation layer passes 86 focused static, currentness,
open-set, and mutation tests.  The latest robustness review closed deep and
over-wide-number JSON exceptions, direct-byte and growing-file size-cap gaps,
bare result/control filename detection, descriptor-relative one-shot
publication, and I/O HOLD normalization without changing either frozen
artifact.
The latest neutral C1 v2 diagnostic covers only the ideal
analytic, fixed-box, one-dimensional, free, cell-centred midpoint OU form.  It
records second-order cell-mass/map/edge ratios, a first-order full-cell density
ratio, exact flat boundary sentinels, and the nonzero detailed-balance residual
of independently selected production binary64 centres.  The repaired Mosco
sublemma remains candidate-labelled, but its final bytes and the repaired v2
diagnostic passed the local hash-specific Round-2 adversarial re-audits with
`P0=P1=P2=0` in their narrow scopes.  This narrow diagnostic did not itself
close any C1 composition.

The v1 ideal-refinement contract remains an immutable finite-anchor contract:
its 12 rows were not themselves `h -> 0` sequences.  The separately frozen
Round-172 v2 successor now defines twelve genuine ideal dyadic refinement
families, including cell-centred, vertex-dual, periodic-base, and shrinking
periodic-half-shift alignments, with `h_f(n)=h_f(0)2^-n`.  At `n=0` it matches
only the saved configuration geometry.  It neither retroactively seals the
historically false predecessor-order flag nor proves correlated production
containment.

The abstract varying-space reconstructed-resolvent/Mosco and positive-time
implications remain accepted at their stated ideal scope.  Round 173 adds
source-bound symbolic map, sharp-contact cut-layer, reconstructed-killing, and
killing-residual bounds for the twelve formula-defined tails.  No theorem
constant is numerically evaluated there.

Separate authenticated fixed-row sources enclose physical axis-cell
integrals and reconstruct formula-defined common edge fluxes, directed rates,
and factorized density ratios.  The production field named `stationary_mass`
remains an ungauged representative quadrature primitive, not a physical cell
integral.  Producer and verifier use the same pinned `gmpy2`/MPFR backend, so
this is authenticated same-backend evidence, not backend independence.  No
single correlated mass/rate/flux/gauge/map/killing receipt exists.  Production
same-member containment, project-level complete C1/C2/C3, F0/F1, root
transfer, release, and submission remain false.

Round 174 now composes the accepted ideal premises on the same
formula-defined member for all twelve dyadic families, every real-simplex
control, every budget in an arbitrary fixed finite interval, and
`r=0,1,2` on compact positive-time windows.  It binds the actual compact-bump
initial source and proves the missing `pi_h^pc/pi -> 1` gate.  Its
existence-constant `O(h^(1/2))` resolvent and observable corollary has no
numerically evaluated or outwardly enclosed constant.  This closes ideal
fixed-box C1 at the theorem layer only; every project/production flag above
remains false.

Round 175 preserves the seven exact Round-174 objects and records two
post-freeze read-only re-audits.  The mathematical reviewer independently
rederived the density-ratio, uniformity, half-order resolvent, initial-law,
Dunford, and compact-positive-time steps; the executable reviewer reran 18
currentness checks and 8 hostile mutations.  The final ledger is
`P0=0`, `P1=0`, `P2=3`.  The three P2 items concern execution
provenance/hostile-writer atomicity, the absence of an independent numerical
or formal backend, and non-cryptographic referee provenance.  This receipt
satisfies the frozen note's separate-review gate without editing the reviewed
bytes and does not promote production C1, computable C2/C3, root transfer, or
release.

Round 176 adds a deliberately non-promoting production `n=0` same-member
preflight.  Its independent validator reconstructs 12 configuration joins,
36 exact partition joins, 5,037 stationary/raw cell identities, 5,013
oriented edge identities (including 12 periodic seams), and 48 ordered killing
profile indices from row manifests without materializing the 34,787,462-state
tensor.  The 97-case
static/currentness/mutation suite rejects retroactive policy sealing,
row/member/partition substitution, claim promotion, and confusion between
the discrete diagonal `B*V` and reconstructed multiplier `B*K`.  The artifact
is not the formal symbolic candidate or an acceptance receipt: all promotion
flags remain false and nine machine-readable blockers require a future
predecessor-sealed replay with complete native provenance.

Round 177 replaces the sequential metadata proposal with one seven-file
predecessor-authority candidate, published through a whole-directory
no-replace step under an explicit no-hostile-writer contract.  Its independent
reconstruction binds all 12 configuration rows and 36 partition objects,
freezes 10 parameter specifications, inventories nine legacy execution
kernels, and records a 74-node/109-edge predecessor-prefix DAG with 48
subordinate files.  A 69-case static/currentness/mutation suite rejects
coherent hash rewrites, path and policy substitution, malformed canonical
JSON, claim promotion, reserved names, symlinks, and hard links.  This prepares
only the structural remedy for B04; B04 itself remains uncleared.  B06 remains
explicitly false because no candidate-native parameterized producer/verifier
closure or exact-DAG execution method is frozen.  The bundled external-review
request is not an external commitment: all nine blockers remain
`cleared=false`, and no roles 8--10 replay, formal candidate, acceptance
receipt, production same-member bridge, C1--C3, F0--F3, or release claim is
made.  The final combined mathematical/provenance/code audit is
`P0=0`, `P1=0`, `P2=3` after repairing a mutation-suite false-positive P1.

Round 178 freezes three successor foundations without promoting them.  The
outcome-free factorization-v2 artifact, result-blind ten-record registry-v4,
and 12-row/36-partition structural member-v4 each passed source-separated
validation and independent adversarial review.  The member identity includes
factorization-v2 but deliberately excludes method/runtime policy and all
results.  The successor anti-vacuity policy-v4 now binds the exact accepted
member identity and registry while copying the complete predecessor thresholds
without reading any role-8--10 output.  Its canonical 4,774-byte artifact has
SHA-256
`599252aa1a9fd1d65d9ff3d0faa1e21bb2609da96cca6b6fff1e61a89ebff196`;
builder check, source-separated validation, 88 focused cases, and a fresh
read-only audit return `P0=0/P1=0/P2=0`.  The policy explicitly treats
`[8,9,10]` as catalog order rather than dependency edges and permits those
roles to execute in parallel only after commitment.  Complete role-8--10
committed-run schemas, the result-blind replay plan, a genuine external
commitment, fresh replay, and a same-member acceptance receipt are still
absent.

Round 179 freezes only the result-blind role-10 numerical operation-model v2
as a prospective precommit contract.  Its immutable 212,071-byte artifact has
SHA-256
`ac0c2b185be75f0ecef3e331fdfd47fc674ca151fa6b26600aff9f789a2f8a6b`,
mode `0444`, and one link; its builder has SHA-256
`927e6b83a525db082a9bef8c4d7cb7b17e7f8f690ff5984673e5a72b7c57c912`.
The historical v1 draft remains rejected and superseded before commitment,
and the existing plan-v1/request-v3 role entrypoints remain compatibility
shells rather than plan-v2 execution authority.  Two independent prospective
contract audits each report `P0=0/P1=0`; the sealed-authentication mirror
separately reports `P0=P1=P2=0`.  This freezes no numerical implementation or
execution, external commitment, B06 preparation or clearance, replay,
same-member acceptance, C1--C3, F0--F3, root transfer, release, or submission
claim.

Round 180 freezes only the static roles-8--10 plan-v2 protocol surface.  The
pure constants, independent validator, and focused tests have SHA-256 values
`4f0dbf1a243a9157f11176b89a3b27833cf6ccc76230cf976a1a985cbb178b15`,
`e1ab7c1eb4d8d1f8a9f3f2e0298513727d04c1dc93628fa2886bf9d4a81c991a`,
and `7d02c09c165b0dcbce5eef5fb85cda02b74db054162adff6d59ec87decbf4443`;
all are mode `0444`, one-link files.  The final static test suite passes
42/42 after repairs for strict JSON types, reachable import closure, dynamic
import aliases, full sealed-mirror-tree authentication, inventory replay,
cross-role source separation, slot freshness/disjointness, and exact modes.
Its ledger is `P0=0/P1=0/P2=4` at the static-only scope.  Actual runtime/ABI
truth, all role-v3 implementations, the global runner, and a frozen non-null
shared protocol remain mandatory HOLD boundaries.  No real runtime closure,
plan, bundle, request, commitment, output, receipt, B06, same-member, C1--C3,
F0--F3, root, release, or submission claim is produced.

Round 181 freezes only four role-8/9 v3 basename/CLI HOLD sentinels.  Their
producer/verifier paths and bytes are separate, every valid or malformed
invocation exposes one role-specific exit-2 HOLD, and 25/25 focused tests plus
an independent 36-case subprocess matrix pass.  The exact frozen shell hashes
are `61a23da6...15e69`, `efb02c33...8605e`, `1b76e146...6e22`, and
`ee6ecb5f...5283`; they import no numerical backend and publish no artifact or
receipt.  This occupies `4/6` required basenames but implements `0/6`
numerical entrypoints.  A live runtime-feasibility audit also shows that the
frozen Round-180 validator cannot faithfully admit the observed CPython/gmpy2
layout or ordinary stdlib closure without a versioned validator repair.  The
integrated ledger is `P0=0/P1=2/P2=4`; no runtime closure, plan, bundle,
request, commitment, replay, B06, same-member, continuum, root, release, or
submission gate is promoted.

Round 184 closes only the static-root materialization step left open by
Rounds 182--183.  The fixed external root now contains exactly five sealed
directories and six pinned files (1,716,156 bytes); the persistent static
inventory has SHA-256 `13b70e...8c6`, and the independently rebuilt
current-tree receipt has SHA-256 `786d60...08e`.  The final materializer,
validator, and 96-case suite are frozen at `4a4210...1ae`,
`737e8f...35f`, and `d0365b...e06`; pre- and postpublication reviews return
component `P0=P1=P2=0`.  The Darwin-correct policy permits and records only
the xattr name `com.apple.provenance` and explicitly does not read or claim
its value.  Nothing in this round imports or executes the sealed bytes:
the result-blind child, authenticated runtime probe, trusted origin adapter,
six-source-plus-runner closure, role-v3 implementations, replay, same-member,
C1--C3, F0--F3, root transfer, release, and submission remain false.  The
integrated ledger therefore remains `P0=0/P1=2/P2=4`.

Round 185 makes the first bounded numerical move past that static stop line.
In one ordinary process it recomputes the O113/Base raw SG factors, physical
stationary integrals, contact/profile factors, global gauge and `rho`, four
formal `V_j/K_j` bases, and the predeclared result-blind barycentre
`w=(1/4,1/4,1/4,1/4)`.  It streams the exact order of 1,442,897 states and
4,303,153 undirected topology edges without a dense tensor.  The final
29,191-byte temporary receipt has SHA-256 `2957b6...927c`; 12/12 focused
tests and two byte-identical clean replays pass.  Post-fix mathematical review
is `P0=P1=P2=0`; the code review retains one temporary-output-path hardening
P2.  The receipt explicitly discloses the exploratory control values and
keeps the production member, full numerical operator, killed diagonal,
C0--C3, F0/F1, release, and submission gates false.

Round 6 now supplies an 883-line implementation design for that production
gauge/application enclosure.  It pins one global mass gauge, a common exact
flux behind forward/reverse rates, the physical quotient measure and
`W^-1` normalization, and the distinction between the discrete killing
diagonal `B*V` and reconstructed multiplier `B*K` with `K=V/rho`.  Two final
exact-byte design audits report `P0=P1=P2=0`, but no correlated production
same-member acceptance or application exists; Round 173 is an ideal
source-bound symbolic contract, Round 176 is only a metadata preflight, and
Round 177 is only a preproduction predecessor candidate.  Rounds 178--179 add
internal result-blind foundations and a prospective operation contract, but
not an implementation, commitment, or replay.  The independent production
receipt, exact controls, budget application, and complete C0--C2 all remain
false.

Round 7 selects a conditional quantitative route from an `O(h^(1/2))` sharp
cut-layer form defect through complex-sector reconstructed resolvents to
positive-time `r=0,1,2` observables for `tau>0`.  Its 539-line theory note
passed two exact-byte mathematical audits with `P0=P1=P2=0`.  A separate
result-blind unit-torus cut-layer fixture independently reconstructs 20 exact
rows and passes 97/97 static, mutation, and currentness assertions plus two
direct entry points; two final exact-byte fixture audits also report
`P0=P1=P2=0`.  This validates only the neutral geometry diagnostic.  QF1--QF2,
a production same-member complex-sector rate, complete C2, C3, and release
remain HOLD.

Round 8 freezes the first neutral symbolic-bridge schema/contract fixture.
Builder and independent validator separately reconstruct the exact global
gauge `1/4`, common flux `6/5`, tensor conductance `6/7`, reconstructed
multiplier `K=1/3`, physical-weight identity `1/10`, and positive interval
quotient `[15/13,31/25]`.  The final static, mutation, and currentness suites
pass 59/59 counted assertions plus two direct entry points.  A currentness
TOCTOU P1 found during adversarial review was repaired with descriptor-relative
parent/target snapshots and re-audited to `P0=P1=P2=0`.  This is still only a
neutral fixture: all eleven production roles are unbound, and the formal
symbolic candidate, independent acceptance receipt, correlated ideal member,
complete C0--C3, science execution, and release remain false.

Round 9 attacks QF2 itself.  An exact checkerboard calculation proves that
the standard nodal tensor-`Q1` all-discrete-pairs `O(h)` graph-form defect is
false in dimension at least two, including the declared vertex-dual Neumann x
vertex-dual Neumann x periodic alignment: the required constant grows like
`1/h` and, in quotient dimension three, like `8/(9h)`.  The exact-rational
fixture passes 90/90 tests and an independent `P0=P1=P2=0` audit.  The revised
conditional route uses a one-sided control-volume residual on a regular
continuum resolvent solution; its killing residual needs `H2 -> L-infinity`
only for that solution and `L2` for arbitrary discrete tests, so QF1 is no
longer critical to the main route.  At the close of Round 9 the free residual,
source-bound map/cut-layer inputs, mixed-boundary sector regularity, and
contour growth were open.  Rounds 10, 11, and 173 later close those inputs only
for the ideal formula-defined tails; no production C2 rate is claimed.

Round 10 closes the ideal one-sided **free** SG/control-volume residual
premise selected in Round 9.  Cell-centred reflected and both periodic shifts
have an `O(h)` energy-dual residual for `H2` operator-domain solutions.  The
vertex-dual endpoint half volumes give only `O(h^(1/2))`, and a smooth constant
mode proves that every uniform exponent greater than one half is false for
the current exact-adjoint map.  Exact tensor slicing cancels spectator
`m*rho=M`, needs no mixed derivatives, and is uniform for asynchronous
spacings with `h=max h_k`.  The neutral fixture passes 107/107 independent
checks and 30/30 fail-closed mutation assertions.  The final review found and
repaired a P1 in which a missing SciPy import could masquerade as mutation
rejection; the repaired harness requires a 107/107 baseline and explicit
semantic `ERROR` signatures.  Two mathematical reviews and the final
post-repair fixture review report `P0=P1=P2=0`.  At Round 10, production
binding, source-bound killing/map constants, the mixed-boundary sector
theorem, and contour growth were still open.  Rounds 11 and 173 later close
the ideal source-bound inputs only.  Production same-member containment,
complete C2/C3, and release remain `HOLD`.

Round 11 closes the ideal fixed-box mixed Neumann--periodic sector-regularity
and contour premise.  A cosine--Fourier domain argument gives
`D(H_c)=H2_NP` uniformly over bounded sharp killing; the sharp scalar sector
constant is `sin(theta/2)`, the reconstructed-resolvent composition decays
conditionally as `h^(1/2)/(sigma+|lambda|)^(1/2)`, and the positive-time
Dunford majorant is explicit for `r=0,1,2`.  Two proof audits close at
`P0=P1=P2=0` after one box-normalization wording P2, while a neutral
mixed-mode/sector/contour fixture passes 1436/1436 independent checks and
46/46 fail-closed mutation assertions after nested-schema, integer-type, and
same-branch baseline hardening.  Round 173 now supplies source-bound symbolic
map and sharp-contact killing-residual bounds for the twelve ideal
formula-defined refinement families.  Combined with Rounds 10--11, this
closes the stated ideal fixed-box input chain only.  It does not numerically
evaluate theorem constants or bind a production member; same-member
containment, project-level complete C1/C2/C3, root transfer, release, and
submission remain false.

PRR remains on HOLD.  The production promotion chain is: accepted exact-$m$
complete-topology theory -> Round-167 control-free initial/free-axis
preparation -> Rounds 168--170 control-free killing-geometry freeze and outer
replay -> still-open correlated same-member killed-operator receipt -> complete
science-free F0 -> no-refit 36-row F1 -> powered off-lattice F3.  The
authenticated fixed-row continuum sources do not skip the correlated
same-member or production-resource gates.

The strict-continuum chain is separate: C0 map/gauge semantics -> Round-172
twelve-family ideal dyadic geometry -> Round-173 ideal source-bound
map/cut/killing inputs -> the accepted Round-174 ideal fixed-box composition ->
Round-176 non-promoting `n=0` metadata preflight -> Round-177 preproduction
predecessor-authority candidate -> Round-178 factorization-v2/registry-v4/
member-v4 foundations and successor anti-vacuity policy -> Round-179
result-blind role-10 operation-model-v2 contract -> future replay-plan-v2/
runtime closure and candidate-native parameterized roles 8--10 producers/
verifiers -> genuine external predecessor commitment -> fresh ordered roles
8--10 replay -> independently streamed exact-DAG replay and a distinct
acceptance receipt -> project-level complete C1 -> numerically evaluated
same-member C2 composition -> box C3 -> componentwise root transfer.
Round 172 does not retroactively repair the historically unsealed predecessor
ordering.  Rounds 177--179 and the accepted successor policy-v4 prepare
result-blind structural and prospective operation-contract foundations but
explicitly leave B06, the executable plan/runtime closure, and the external
commitment/replay/receipt chain open.
Rounds 180--184 add only static plan vocabulary, HOLD entrypoint names,
authenticated-byte resolution, process mechanics, and the sealed static root
plus receipt.  They do not change the mathematical or scientific gate state.
Round 184 is the static-provenance stop line: the next runtime action, if
needed, is the smallest result-blind wrapper-import observation, while the
scientific priority is the actual roles 8--10 `n=0` same-member receipt and
numerically evaluated C2/C3 chain.
Round 185 now supplies a real one-row factorized exploratory composition and
a disclosed no-budget barycentre, but not the ordered production role replay
or acceptance receipt.  The next scientific step is therefore an independent
nonunit-`W` evaluator plus a budget-bound streamed O113 numerical operator,
followed by the externally committed role-8--10 replay; only after that should
the construction be extended across all twelve anchors and used to evaluate
C2/C3 constants.

The production stream's `stationary_mass` payload remains an ungauged
representative quadrature primitive.  The separate fixed-row physical-integral
and raw-flux artifacts use the same authenticated MPFR backend and do not alter
those production bytes or establish one correlated ideal member.  All
roundoff width remains in `E_eval`; no convergence theorem is claimed for
unrelated binary64 interval centres.

## Reproducible entry points

Run these commands from the repository root with the repository-owned Python
environment; the system `python3` on this machine does not provide the frozen
SciPy/pytest stack.

The first command is the explicit aggregate for the current continuum spine.
It covers Rounds 10--11 and 172--177 plus theorem-first manuscript
freshness/scope.  It is intentionally not a full-report test, CI attestation,
production run, or release gate.  The current allowlist fixes four standalone
neutral-fixture summaries totalling 1,619 assertions and 265 collected pytest
cases (333 JUnit entries after subtests); failures, errors, skips, xfails,
manifest drift, claim promotion, or before/after byte drift fail closed.
Round-176 and Round-177 subprocesses use Python `-I -B`.  The pre/post
snapshot covers all 77 manifest-declared Round-176 dependencies plus its
manifest, and all 74 manifest-declared Round-177 dependencies plus the
complete seven-file package (77 unique Round-177 paths).

```bash
.venv/bin/python -B research/reports/encounter_multimodal_prr/code/verify_current_continuum_spine.py
.venv/bin/python research/reports/encounter_multimodal_prr/code/continuum_c1_sg_manufactured.py
.venv/bin/python -m pytest -q research/reports/encounter_multimodal_prr/code/test_continuum_c1_sg_manufactured.py research/reports/encounter_multimodal_prr/code/test_continuum_c1_sg_manufactured_adversarial.py
.venv/bin/python research/reports/encounter_multimodal_prr/code/build_continuum_c1_ideal_refinement_contract_candidate_v1.py --check
.venv/bin/python research/reports/encounter_multimodal_prr/code/validate_continuum_c1_ideal_refinement_contract_candidate_v1.py
.venv/bin/python -m pytest -q research/reports/encounter_multimodal_prr/code/test_continuum_c1_ideal_refinement_contract_candidate_v1.py research/reports/encounter_multimodal_prr/code/test_continuum_c1_ideal_refinement_contract_v1_currentness.py research/reports/encounter_multimodal_prr/code/test_continuum_c1_ideal_refinement_contract_adversarial_v1.py
.venv/bin/python research/reports/encounter_multimodal_prr/code/continuum_c1_free_axes_tensor_diagnostic.py
.venv/bin/python -m pytest -q research/reports/encounter_multimodal_prr/code/test_continuum_c1_free_axes_tensor_diagnostic.py research/reports/encounter_multimodal_prr/code/test_continuum_c1_free_axes_tensor_diagnostic_mutations.py
.venv/bin/python research/reports/encounter_multimodal_prr/code/build_continuum_c2_cut_layer_neutral_fixture_v1.py --check
.venv/bin/python research/reports/encounter_multimodal_prr/code/validate_continuum_c2_cut_layer_neutral_fixture_v1.py
.venv/bin/python research/reports/encounter_multimodal_prr/code/test_continuum_c2_cut_layer_neutral_fixture_v1.py
.venv/bin/python research/reports/encounter_multimodal_prr/code/test_continuum_c2_cut_layer_neutral_fixture_mutations_v1.py
.venv/bin/python research/reports/encounter_multimodal_prr/code/test_continuum_c2_cut_layer_neutral_fixture_currentness_v1.py
.venv/bin/python research/reports/encounter_multimodal_prr/code/continuum_c2_one_sided_free_residual_neutral_fixture_v1.py --check
.venv/bin/python research/reports/encounter_multimodal_prr/code/test_continuum_c2_one_sided_free_residual_neutral_fixture_v1.py
.venv/bin/python research/reports/encounter_multimodal_prr/code/test_continuum_c2_one_sided_free_residual_neutral_fixture_mutations_v1.py
.venv/bin/python research/reports/encounter_multimodal_prr/code/continuum_c2_complex_sector_h2_neutral_fixture_v1.py --check
.venv/bin/python research/reports/encounter_multimodal_prr/code/test_continuum_c2_complex_sector_h2_neutral_fixture_v1.py
.venv/bin/python research/reports/encounter_multimodal_prr/code/test_continuum_c2_complex_sector_h2_neutral_fixture_mutations_v1.py
.venv/bin/python -I -m pytest -q research/reports/encounter_multimodal_prr/code/test_continuum_c1_mpfr_authenticated_execution_v1.py research/reports/encounter_multimodal_prr/code/test_continuum_c1_stationary_integral_source_v1.py research/reports/encounter_multimodal_prr/code/test_continuum_c1_stationary_integral_source_mutations_v1.py
.venv/bin/python -I -B research/reports/encounter_multimodal_prr/code/test_continuum_c1_fixed_row_raw_flux_authenticated_adversarial_v1.py --launcher-sha256 f73f61f40ad658c00bb40f27c6676998763d84383b5c86deff7e3bac48a12df4 --receipt-sha256 44af008a9a86cbb249209dd806fbb2633f4976aae5e5fbf234d55dfa36bad0e2
.venv/bin/python -B research/reports/encounter_multimodal_prr/code/build_continuum_c1_genuine_joint_refinement_family_v2.py --check
.venv/bin/python -B research/reports/encounter_multimodal_prr/code/validate_continuum_c1_genuine_joint_refinement_family_v2.py
.venv/bin/python -I -B research/reports/encounter_multimodal_prr/code/build_continuum_c1_n0_same_member_symbolic_preflight_candidate_v1.py --check
.venv/bin/python -I -B research/reports/encounter_multimodal_prr/code/validate_continuum_c1_n0_same_member_symbolic_preflight_candidate_v1.py
.venv/bin/python -I -B -m pytest -q research/reports/encounter_multimodal_prr/code/test_continuum_c1_n0_same_member_symbolic_preflight_candidate_v1.py research/reports/encounter_multimodal_prr/code/test_continuum_c1_n0_same_member_symbolic_preflight_candidate_mutations_v1.py
.venv/bin/python -I -B research/reports/encounter_multimodal_prr/code/build_continuum_c1_n0_predecessor_authority_candidate_v1.py --check
.venv/bin/python -I -B research/reports/encounter_multimodal_prr/code/validate_continuum_c1_n0_predecessor_authority_candidate_v1.py
.venv/bin/python -I -B -m pytest -q research/reports/encounter_multimodal_prr/code/test_continuum_c1_n0_predecessor_authority_candidate_v1.py research/reports/encounter_multimodal_prr/code/test_continuum_c1_n0_predecessor_authority_candidate_mutations_v1.py
.venv/bin/python -I -B research/reports/encounter_multimodal_prr/code/build_continuum_c1_n0_role10_numerical_operation_model_v2_candidate.py --check
.venv/bin/python -I -B research/reports/encounter_multimodal_prr/code/validate_continuum_c1_n0_role10_numerical_operation_model_v2_candidate.py
.venv/bin/python -I -B -m pytest -q research/reports/encounter_multimodal_prr/code/test_continuum_c1_n0_role10_numerical_operation_model_v2_candidate.py research/reports/encounter_multimodal_prr/code/test_continuum_c1_n0_role10_numerical_operation_model_mutations_v2_candidate.py
.venv/bin/python -B -m pytest -q -p no:cacheprovider research/reports/encounter_multimodal_prr/code/test_continuum_c1_n0_sealed_runtime_root_v1.py
o113_tmp=$(mktemp -d /tmp/encounter-o113-round185.XXXXXX)
env PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -I -B research/reports/encounter_multimodal_prr/code/explore_continuum_c1_n0_same_member_o113_v1.py --output "$o113_tmp/receipt.json"
env PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B -m pytest -q -p no:cacheprovider research/reports/encounter_multimodal_prr/code/test_explore_continuum_c1_n0_same_member_o113_v1.py
.venv/bin/python -B -m pytest -q research/reports/encounter_multimodal_prr/code/test_continuum_c1_genuine_joint_refinement_family_v2.py research/reports/encounter_multimodal_prr/code/test_continuum_c1_genuine_joint_refinement_family_mutations_v2.py
.venv/bin/python -B research/reports/encounter_multimodal_prr/code/build_continuum_c2_source_bound_map_cut_killing_contract_v1.py --check
.venv/bin/python -B research/reports/encounter_multimodal_prr/code/validate_continuum_c2_source_bound_map_cut_killing_contract_v1.py
.venv/bin/python -B -m pytest -q research/reports/encounter_multimodal_prr/code/test_continuum_c2_source_bound_map_cut_killing_contract_v1.py research/reports/encounter_multimodal_prr/code/test_continuum_c2_source_bound_map_cut_killing_contract_mutations_v1.py
.venv/bin/python -B research/reports/encounter_multimodal_prr/code/build_continuum_c1_twelve_family_ideal_fixed_box_c1_composition_v1.py --check
.venv/bin/python -B research/reports/encounter_multimodal_prr/code/validate_continuum_c1_twelve_family_ideal_fixed_box_c1_composition_v1.py
.venv/bin/python -B -m pytest -q research/reports/encounter_multimodal_prr/code/test_continuum_c1_twelve_family_ideal_fixed_box_c1_composition_v1.py research/reports/encounter_multimodal_prr/code/test_continuum_c1_twelve_family_ideal_fixed_box_c1_composition_mutations_v1.py
.venv/bin/python research/reports/encounter_multimodal_prr/code/build_continuum_c0_model_contract_candidate_v2.py --check
.venv/bin/python research/reports/encounter_multimodal_prr/code/validate_continuum_c0_model_contract_candidate_v2.py
.venv/bin/python -m pytest -q research/reports/encounter_multimodal_prr/code/test_continuum_c0_model_contract_candidate_v2.py research/reports/encounter_multimodal_prr/code/test_continuum_c0_model_contract_v2_currentness.py research/reports/encounter_multimodal_prr/code/test_continuum_c0_model_contract_adversarial_v2.py
.venv/bin/python research/reports/encounter_multimodal_prr/code/build_continuum_c0_model_contract_candidate_v3.py --check
.venv/bin/python research/reports/encounter_multimodal_prr/code/validate_continuum_c0_model_contract_candidate_v3.py
.venv/bin/python -m pytest -q research/reports/encounter_multimodal_prr/code/test_continuum_c0_model_contract_candidate_v3.py research/reports/encounter_multimodal_prr/code/test_continuum_c0_model_contract_adversarial_v3.py
.venv/bin/python -m pytest -q research/reports/encounter_multimodal_prr/code/test_continuum_c0_model_contract_current_staleness.py
.venv/bin/python research/reports/encounter_multimodal_prr/code/compile_theorem_first_working.py
.venv/bin/python research/reports/encounter_multimodal_prr/code/check_reproducibility_environment.py
.venv/bin/python -m pytest -q research/reports/encounter_multimodal_prr/code/test_compile_theorem_first_working.py
.venv/bin/python -m pytest -q research/reports/encounter_multimodal_prr/code/test_theorem_first_scope_consistency.py
.venv/bin/python research/reports/encounter_multimodal_prr/code/rate_defined_tensor_f0_production_initial_stream.py verify --bundle research/reports/encounter_multimodal_prr/artifacts/data/physical_production_initial_stream_v1
replay_dir=$(mktemp -d research/reports/encounter_multimodal_prr/tmp/clean-replay.XXXXXX)
.venv/bin/python research/reports/encounter_multimodal_prr/code/rate_defined_tensor_f0_production_initial_clean_replay.py --report-root research/reports/encounter_multimodal_prr --receipt "$replay_dir/receipt.json"
.venv/bin/python -m pytest -q research/reports/encounter_multimodal_prr/code/test_rate_defined_tensor_f0_production_initial_stream.py
.venv/bin/python research/reports/encounter_multimodal_prr/code/validate_gig_constructive.py
.venv/bin/python -m pytest -q research/reports/encounter_multimodal_prr/code/test_gig_constructive.py
.venv/bin/python research/reports/encounter_multimodal_prr/code/continuum_g1_smoke.py
.venv/bin/python -m pytest -q research/reports/encounter_multimodal_prr/code/test_continuum_g1_smoke.py
.venv/bin/python research/reports/encounter_multimodal_prr/code/continuum_g1_discovery.py --dry-run
.venv/bin/python -m pytest -q research/reports/encounter_multimodal_prr/code/test_continuum_g1_discovery.py
.venv/bin/python research/reports/encounter_multimodal_prr/code/continuum_g1_manual_review.py
.venv/bin/python -m pytest -q research/reports/encounter_multimodal_prr/code/test_continuum_g1_manual_review.py
.venv/bin/python research/reports/encounter_multimodal_prr/code/continuum_weak_budget_design.py
.venv/bin/python -m pytest -q research/reports/encounter_multimodal_prr/code/test_continuum_weak_budget_design.py
.venv/bin/python research/reports/encounter_multimodal_prr/code/plot_weak_budget_design.py
.venv/bin/python -m pytest -q research/reports/encounter_multimodal_prr/code/test_plot_weak_budget_design.py
.venv/bin/python research/reports/encounter_multimodal_prr/code/continuum_g1c_simplex.py --dry-run
.venv/bin/python -m pytest -q research/reports/encounter_multimodal_prr/code/test_continuum_g1c_simplex.py
.venv/bin/python research/reports/encounter_multimodal_prr/code/continuum_g1d_fold_confirmation.py --help
.venv/bin/python -m pytest -q research/reports/encounter_multimodal_prr/code/test_continuum_g1d_fold_confirmation.py
.venv/bin/python research/reports/encounter_multimodal_prr/code/continuum_observable_four_patch.py --help
.venv/bin/python -m pytest -q research/reports/encounter_multimodal_prr/code/test_continuum_observable_four_patch.py
.venv/bin/python research/reports/encounter_multimodal_prr/code/continuum_observable_four_patch_d3.py --help
.venv/bin/python -m pytest -q research/reports/encounter_multimodal_prr/code/test_continuum_observable_four_patch_d3.py
.venv/bin/python research/reports/encounter_multimodal_prr/code/continuum_broad_patch_b0_bridge.py --help
.venv/bin/python -m pytest -q research/reports/encounter_multimodal_prr/code/test_continuum_broad_patch_b0_bridge.py
.venv/bin/python research/reports/encounter_multimodal_prr/code/plot_observable_four_patch.py
.venv/bin/python -m pytest -q research/reports/encounter_multimodal_prr/code/test_plot_observable_four_patch.py
.venv/bin/python research/reports/encounter_multimodal_prr/code/plot_d2_d3_four_patch.py
.venv/bin/python -m pytest -q research/reports/encounter_multimodal_prr/code/test_plot_d2_d3_four_patch.py
.venv/bin/python research/reports/encounter_multimodal_prr/code/plot_positive_b_broad_four_slab.py
.venv/bin/python -m pytest -q research/reports/encounter_multimodal_prr/code/test_plot_positive_b_broad_four_slab.py
.venv/bin/python research/reports/encounter_multimodal_prr/code/build_positive_b_manuscript_input.py
.venv/bin/python -m pytest -q research/reports/encounter_multimodal_prr/code/test_build_positive_b_manuscript_input.py
.venv/bin/python research/reports/encounter_multimodal_prr/code/build_manuscript_inputs.py
.venv/bin/python -m pytest -q research/reports/encounter_multimodal_prr/code/test_compile_manuscript.py
.venv/bin/python -m pytest -q research/reports/encounter_multimodal_prr/code/test_living_scope_consistency.py
```

The scripts write only report-owned outputs. Numerical producers use
`artifacts/data/`; the theorem-first compiler uses a closed analytical source
allowlist and transactionally publishes the main PDF, Supplemental PDF, logs,
and manifest after two byte-identical isolated builds of each document.  The
historical `code/compile_manuscript.py` path is retained for archival
reconstruction, not as the active paper entry point.  That legacy compiler
publishes its generated inputs, PDF, logs, and manifest only after its source
and figure pins and both clean builds pass.  The smoke
command is a pre-fold implementation check. The discovery command shown above
is deliberately a 315-state dry-run; the completed 207,025-state formal run
required the explicit frozen-run flag and all preflight gates.  The manual
review is explicitly post-result evidence: it resolves the `theta=0.7`
subzero derivative wiggle but does not retroactively authorize the original
line-empty action or verify a continuum fold.

The positive-$B$ broad-four-slab result is a closed canonical record, not a
normal rerunnable entry point: two complete sequential producer replicas were
byte-identical before canonical promotion, and the frozen post-result auditor
was then invoked exactly once.  Re-running that auditor would violate its
declared protocol and is therefore intentionally omitted from the command list.

## Directory map

- `notes/research_contract.md`: claim, overlap, and stop/go policy.
- `notes/theorem_program.md`: proof obligations and evidence levels.
- `notes/continuum_g1_design.md`: exact quotient and numerical acceptance gates.
- `notes/discovery_protocol.md`: result-blind frozen 207,025-state discovery protocol.
- `notes/manual_review_protocol.md`: separately frozen post-result diagnostic boundary.
- `notes/pde_mixed_jet_theorem.md`: proved weak-budget continuum mixed-jet and
  conditional fold/cusp/rank persistence theorem, with finite-budget limits.
- `notes/direct_physical_multimode_theorem.md`: audited direct theorem for each
  fixed finite integer $d\ge2$ and prescribed fixed finite mode count in a
  $d$-, $m$-, and epsilon-dependent physical slab family, including its
  sequential-limit, non-uniform-in-$d$, and event-mass limits.
- `notes/exact_m_mode_encounter_theorem_candidate.md`: archived attacked v1;
  Round 112 identified the false crossover-complement dominance step.
- `notes/exact_m_mode_encounter_theorem_v2.md`: repaired exact-$m$ global
  topology and fixed-$\varepsilon$ weak-budget Doi theorem; independently
  accepted by Rounds 118 and 120 at SHA `e78a0d77959d50214d56ef4708a20ac465232883fbbdd4ee42fe488c0b95c85d`.
  Its original candidate-status prose is intentionally preserved because those
  accepted bytes are immutable; Round 149 separately accepts the migrated
  paper proof.
- `notes/modal_certificate_theory_and_prr_redirect.md`: repaired
  box-and-complement modal-certificate theorem and theorem-first route.
- `notes/positive_b_fixed_control_robustness_design_v2.md`: active no-refit F0
  design for exact-rational same-budget one-/two-/three-mode candidates; no
  primary positive-$B$ command is currently authorized.
- `notes/verified_semigroup_enclosure_design.md`: selected directed-
  uniformization enclosure.  Round 150 introduced the first bounded directed
  packed-action primitive; Round 152 rejected those bytes, and independent
  Round 155 accepted the repaired Round-154 bytes only as a bounded primitive.
  Rate-interval composition,
  uniformization, Poisson tails, jets, topology, independent replay, and
  production resources remain open.
- `notes/f1_to_f2_common_observable_selector_v1.md`: pre-F1 mechanical common-
  cut/window, uncertainty, multiplicity, power, and RNG design.  The selector-v2
  implementation and its tested-macOS process/resource surface are accepted by
  Rounds 151/153; second-POSIX portability, a causal second-parent contention
  handshake, and all F1/F2 science remain open.
- `notes/continuum_next_stage_path.md`: theorem-first claim ladder and the
  pre-science, 36-row deterministic, continuum-envelope, off-lattice, audit,
  and manuscript branches for the next physical-`d=2` stage.
- `notes/continuum_research_program_v2.md`: strict-continuum C0--C3 and root-
  transfer contract.  It now distinguishes the ideal analytic SG form from
  production interval centres and freezes the exact-adjoint `P_h` denominator.
- `notes/continuum_c1_fixed_1d_free_ou_mosco_candidate.md`: repaired
  fixed-box ideal one-dimensional free-OU Mosco/strong-resolvent proof
  candidate, with arbitrary-sequence liminf, diagonal recovery, exact map
  algebra, and production-boundary exclusions; fresh independent acceptance
  remains open.
- `notes/continuum_c1_free_form_and_functional_bridge_candidate.md`: result-
  blind successor proof candidate for the relative, periodic, tensor-product,
  vertex-dual, and physical-volume killing forms, followed by a self-contained
  varying-space resolvent-to-positive-time functional bridge.  Its abstract
  implications are instantiated for the ideal twelve-family tails by Round
  174; the production application bridge, computable rates, and release remain
  false.
- `notes/continuum_c1_varying_space_resolvent_mosco_candidate.md`: 571-line
  self-contained theorem candidate turning one reconstructed resolvent limit
  and near-isometric adjoint maps into generalized Mosco convergence, with
  conditional free-tensor and bounded-killing corollaries.  Its final local
  exact-byte audits have `P0=P1=P2=0`; Round 174 instantiates it only for the
  ideal twelve-family fixed-box composition.
- `notes/continuum_c1_production_gauge_killing_bridge_design_v1.md`: audited
  two-stage DESIGN for a global-gauge, common-flux, physical-mass, and
  reconstructed-killing application bridge with acyclic source/receipt
  provenance.  No correlated production same-member contract or application
  exists yet; Round 173 is an ideal source-bound symbolic contract only.
- `notes/continuum_c1_n0_candidate_native_role_8_10_method_authority_v1.md`:
  current candidate-native responsibility, plan-v2, runtime, transaction, and
  nonclaim authority.  Round 179 freezes only its prospective role-10
  operation-model contract; role-10 implementation and execution remain absent.
- `notes/continuum_c2_quantitative_positive_time_route_candidate.md`:
  conditional fixed-box C2 route from a sharp cut-layer form defect through
  complex-sector resolvents and positive-time Dunford transfer.  Its
  conservative `h^(1/2)` target is not a proved or production-bound rate.
- `notes/continuum_c2_mixed_neumann_periodic_sector_h2_candidate.md`:
  Round-11 ideal fixed-box closure of the mixed graph domain, bounded sharp
  killing domain preservation, complex-sector `H2` estimate, conditional
  half-order resolvent comparison, and explicit Dunford growth.  Ideal source
  binding is supplied separately by Round 173; numerical constant evaluation,
  production containment, and complete C2 remain false.
- `notes/continuum_c1_genuine_joint_refinement_family_v2.md`: source-defined
  dyadic refinement geometry for all twelve fixed boxes, including
  vertex-dual endpoint half cells and shrinking periodic half shifts.  Its
  level-zero production match is geometric only.
- `notes/continuum_c2_source_bound_map_cut_killing_lemma_v1.md`: Round-173
  ideal symbolic gauge/map, contact cut-layer, reconstructed-killing, and
  killing-residual bounds.  Constants are not numerically evaluated and no
  production same-member receipt follows.
- `notes/continuum_c1_twelve_family_ideal_fixed_box_C1_composition_v1.md`:
  Round-174 accepted composition for the complete real simplex, every fixed finite
  budget cap, all twelve ideal dyadic tails, the actual compact-bump initial
  source, and positive-time orders `r=0,1,2`.  Its theorem-layer conclusion
  does not promote project or production `complete_C1`.
- `notes/reproducibility_environment.md`: exact direct Python baseline,
  environment-only verification command, and the still-open clean-install and
  transitive-lock boundary.
- `notes/f0_rate_interval_composition_next_stage.md`: Round-155-cleared
  next-stage design for composing centre-action boxes with exact stage-1 rate
  witnesses in a point-plus-$l^1$-ball representation before any Poisson
  propagation; the bounded primitive is accepted, while F0 remains held.
- `notes/weak_budget_design_protocol.md`: result-informed free-exposure cusp
  reproduction and complete sampled-simplex boundary.
- `notes/g1c_simplex_protocol.md`: prospectively frozen result-informed full-simplex
  finite-grid discovery protocol.
- `notes/g1d_fold_confirmation_protocol.md`: frozen one-segment finite-budget
  fold confirmation protocol.
- `notes/observable_four_patch_protocol.md`: result-informed exact-continuum
  physical-$d=2$ four-slab cusp and relative-shape confirmation protocol.
- `notes/observable_four_patch_d3_protocol.md`: result-informed exact sphere-
  kernel physical-$d=3$ analogue with a direct spherical-coordinate cross-check.
- `notes/broad_patch_b0_bridge_protocol.md`: separately frozen broad-patch
  exact-kernel-to-four-mesh $B=0$ bridge; it does not claim positive $B$.
- `notes/positive_b_broad_four_slab_protocol.md`: disclosed low-mesh budget
  selection and frozen held-out-mesh protocol for the fixed broad four-slab
  positive-$B$ killed-Doi test.
- `notes/positive_b_postresult_audit_protocol_v2.md`: frozen exactly-once
  independent post-result reconstruction and reporting boundary.
- `notes/literature_gap_20260713.md`: primary-literature collision and novelty audit.
- `code/validate_gig_constructive.py`: deterministic reduced-model pilot.
- `code/continuum_g1_smoke.py`: exact-quotient low-resolution operator smoke.
- `code/build_manuscript_inputs.py`: fail-closed generation of manuscript TeX
  macros from the release-pinned $d=2/d=3$ four-slab, broad-bridge, G1c, and
  G1d JSON artifacts and their nested source chains.  It uses descriptor-level
  same-byte snapshots for the release manifest and all 38 unique/reused source
  roles, enforces exact per-family schemas and role cardinalities, rejects
  non-finite or duplicate-key JSON and recursive claim promotion, and renders
  only from the already-verified immutable payloads.
- `code/build_positive_b_manuscript_input.py`: separate fail-closed TeX macro
  generation from the canonical result, two-process record, exactly-once audit,
  and all 14 frozen provenance pins for the fixed-control positive-$B$ point. It
  reads ordinary nonsymlink files through same-byte descriptor snapshots and
  independently reconstructs all 24 per-mesh gates and all five mesh-agreement
  gates, including saved-trace extrema, root brackets, probability domains, and
  scan/tail junctions.
- `code/plot_weak_budget_design.py`: byte-reproducible vector figure for the
  result-informed $B=0$ diagnostic; it recomputes every plotted value.
- `code/plot_observable_four_patch.py`: source-pinned physical-$d=2$ relative-
  shape figure; its human-readable labels make no event-mass claim.
- `code/plot_d2_d3_four_patch.py`: deterministic vector comparison of the
  physical-$d=2$ disk and physical-$d=3$ sphere $B=0$ relative shapes.
- `code/plot_positive_b_broad_four_slab.py`: deterministic, claim-scoped
  fixed-control $B=0.01$ density/root and event-basin figure; the PDF and its
  source-pinned metadata sidecar are published as one rollback-safe pair. Its
  visible scope distinguishes the $t\leq35$ root screen from the $t\leq100$
  basin-mass/tail checks and disclaims post-$35$ root exclusion.
- `code/compile_manuscript.py`: clean temporary LaTeX build, PDF hygiene gate,
  strict per-figure metadata/claim/source-role contracts, same-byte input
  snapshots, and a rollback-safe multi-output publication transaction for the
  archived historical working set.
- `code/compile_theorem_first_working.py`: active analytical-only compiler with
  a closed source allowlist, four isolated builds, byte-identity gates, TeX/PDF/
  font/text checks, normalized reproducible logs, and rollback-safe publication.
- `code/rate_defined_tensor_f0_packed_interval_action.py`: Round-154-repaired
  science-free packed interval action for frozen-order $P^T$ and signed $Q^T$,
  with per-operation outward rounding, source/kernel/input hash bindings,
  owned read-only outputs, and a `16N+81B` fixed-payload ledger.  This is an
  implementation primitive accepted for the repaired Round-154 bytes by the
  independent Round-155 re-audit, not F0 acceptance.
- `code/rate_defined_tensor_f0_production_initial_stream.py` and its separate
  rebuild/independent/geometry verifiers: exact-schema 12-row control-free
  source, partition, marginal, free-axis-rate, sparse-box, and native packed-
  axis preparation.  The accepted scope contains no killing, full operator,
  propagation, topology, positive-budget value, or F0 result.
- `code/rate_defined_tensor_f0_production_initial_clean_replay.py`: standard-
  library outer observer that runs two complete serialized repeats, each with
  five separate `python -I` processes, and retains a pinned receipt.  This is
  process-boundary replay on one runtime, not hermetic or cross-backend
  independence.
- `code/test_living_scope_consistency.py`: regression guard that keeps the
  README, research contract, theorem program, focused rewrite blueprint, and
  working manuscript aligned on the fixed-point result and its open gates.
- `code/continuum_c1_sg_manufactured.py` and its two test modules: neutral
  single-axis v2 map/form diagnostic, exact flat affine/quadratic/interpolant
  sentinels, raw-primitive interval containment, explicit failure of the
  gauge-scaled form-containment bridge, and mutation attacks.  Passing this
  diagnostic is not a Mosco proof or a production-centre limit.
- `code/build_continuum_c1_ideal_refinement_contract_candidate_v1.py`, its
  standalone verifier, note pin, and three test modules: result-blind,
  fail-closed machine contract for the prospective ideal refinement families,
  tensor gauge, physical-volume killing, and conditional functional bridge.
  Its finite configurations are structural anchors, not a convergence
  sequence, and every promotion flag remains false.
- `code/continuum_c1_free_axes_tensor_diagnostic.py` and its two test modules:
  neutral numerical fixture for midpoint, vertex-dual, periodic, and separable
  tensor identities.  It streams exact factorized checks without allocating a
  three-dimensional array and is not production evidence.
- `code/build_continuum_c2_cut_layer_neutral_fixture_v1.py`, the independent
  integer validator, two test suites, and currentness gate: exact-rational
  neutral cut-cell fixture with a machine-checked Machin upper bound for pi,
  strict JSON types, 20 frozen rows, and 97/97 assertions.  It computes no
  contact fractions, controls, budgets, semigroups, or production values.
- `code/continuum_c2_complex_sector_h2_neutral_fixture_v1.py` and its
  independent and mutation verifiers: canonical neutral mixed-NP
  mode/sector/contour algebra with 1436/1436 semantic checks and 46/46
  fail-closed mutation assertions.  It does not prove weighted PDE
  regularity, source binding, production containment, or C2.
- `artifacts/data/continuum_c0_model_contract_candidate_v1.json` and its old
  verifier/tests: immutable historical C0-v1 bytes.  Only the dedicated
  current-staleness sentinel belongs to the current suite; the old 6/6 and
  12/12 results apply only to their then-pinned sources.
- `artifacts/data/continuum_c0_mathematical_source_v2.json`,
  `continuum_c0_control_method_commitment_v2.json`, and
  `continuum_c0_model_contract_candidate_v2.json`: C0-only mathematical and
  method commitments plus the deterministic current semantic candidate.  The
  method commitment intentionally contains no control values or payload path.
- `code/build_continuum_c0_model_contract_candidate_v2.py`,
  `validate_continuum_c0_model_contract_candidate_v2.py`, and the three C0-v2
  test modules: one-shot producer, independent same-byte/source-pinned
  verifier, currentness checks, and mutation attacks.  Their PASS does not
  close complete C0 or the production gauge/application bridge.
- `artifacts/data/continuum_c0_measure_partition_preconditions_v1.json` and
  `continuum_c0_model_contract_candidate_v3.json`: canonical well-definedness
  preconditions and the immutable versioned wrapper over the v2 semantic base;
  the wrapper keeps complete C0, the production gauge bridge, and release
  false.
- `code/build_continuum_c0_model_contract_candidate_v3.py`,
  `validate_continuum_c0_model_contract_candidate_v3.py`, and the two C0-v3
  test modules: reproducible wrapper, independent semantic/geometry verifier,
  actual-versus-declared source-open check, and adversarial mutations over all
  36 axes and 34,787,462 tensor cells.
- `audits/continuum_c0_model_contract_v3_adversarial_round3_20260717.md`:
  hash-specific v1-to-v3 chronology, mathematical well-definedness review,
  code hardening rounds, exact test/compile receipts, and retained C0/C1/PRR
  HOLD boundaries.
- `manuscript/encounter_multimodal_prr.tex`: claim-gated historical working
  draft; it still contains the superseded at-least-`m` theorem wording and is
  not the theorem-first source.
- `manuscript/exact_m_theorem_spine.tex`: independently accepted reader-facing
  exact-`m` theorem fragment, with compact-window and sequential-limit
  restrictions explicit.
- `manuscript/exact_m_theorem_full_proof.tex`: complete reader-facing proof of
  the common-variance zero bound, adjacent isolation, exact pure topology,
  posterior-sector complement, slow-factor transfer, and fixed-$\varepsilon$
  Doi embedding; frozen and independently accepted in Round 149.
- `manuscript/encounter_multimodal_prr_theorem_first_working.tex`: separate
  theorem-first working source whose seven-page PDF now includes the audited
  physical-`d=2` C0-A quotient and natural-decay operator realization plus the
  exact-`m` spine; it imports no generated positive-`B` result macros and makes
  no new finite-parameter topology or finite-volume-to-continuum claim.
- `output/pdf/encounter_multimodal_prr_theorem_first_working.pdf`: rendered
  theorem-first working PDF from two byte-identical isolated builds.
- `manuscript/encounter_multimodal_prr_supplement.tex` and
  `output/pdf/encounter_multimodal_prr_theorem_first_supplement_working.pdf`:
  twenty-four-page analytical working Supplement and its byte-reproducible
  rendered PDF.  Proposition S3.3 states the conditional varying-space
  positive-time bridge; Sec.~S4 remains a distinct, more general at-least-`m`
  result, and Sec.~S5 contains the complete exact-`m` proof accepted for its
  frozen bytes in Round 149.
- `manuscript/inputs/positive_b_results.tex`: generated fixed-control-only
  positive-budget values; its header explicitly forbids cusp, continuum,
  independent-solver, and PRR-ready promotion.
- `artifacts/data/manuscript_compile.json`: archived 13-page historical-build
  record.  It preserves its original source/bibliography/PDF hashes, is marked
  `ARCHIVED_HISTORICAL_WORKING_SET`, and is superseded by the theorem-first
  manifest while remaining `release_eligible=false`.
- `artifacts/data/theorem_first_working_compile.json`: source/PDF hashes and
  compile, text, PDF-structure, and publication record for the active 7+24-physical-page
  theorem-first main/Supplement working set; `release_eligible=false`, with both
  positive-budget evaluation flags false.
- `artifacts/data/continuum_c1_sg_manufactured_v1.json`: immutable first-round
  neutral diagnostic retained for its historical audit hash.
- `artifacts/data/continuum_c1_sg_manufactured_v2.json`: current neutral
  single-axis diagnostic with uniform cell-mass, exact-adjoint map, ideal edge-
  interpolant, density-ratio, boundary-order, and production-centre residual
  ledgers; all C1/production-limit/release flags remain false.
- `artifacts/data/continuum_c1_ideal_refinement_contract_candidate_v1.json`:
  result-blind C1 ideal-refinement/rate contract candidate pinned to the
  audited mathematical successor note and C0-only sources; all complete-C1,
  production, C2/C3, and release booleans are false.
- `artifacts/data/continuum_c1_free_axes_tensor_diagnostic_v1.json`: neutral
  finite-grid identity and order fixture for free axes and tensor
  factorization; its twelve rows are diagnostic anchors only.
- `artifacts/data/continuum_c1_symbolic_bridge_neutral_source_v1.json`,
  `continuum_c1_symbolic_bridge_neutral_fixture_v1.json`, and
  `continuum_c1_symbolic_bridge_neutral_fixture_currentness_v1.json`: the
  Round-8 neutral symbolic schema/algebra source, canonical exact-rational
  fixture, and eight-core-file currentness manifest.  They bind no production
  role and materialize neither reserved formal candidate nor receipt.
- `artifacts/data/continuum_c2_cut_layer_neutral_source_v1.json`,
  `continuum_c2_cut_layer_neutral_fixture_v1.json`, and
  `continuum_c2_cut_layer_neutral_fixture_currentness_v1.json`: result-blind
  unit-torus cut-layer source, exact 20-row fixture, and six-file hash gate.
  The finite `9/4` value is not a theorem constant; complete C2 remains false.
- `artifacts/data/continuum_c2_qf2_checkerboard_obstruction_v1.json`: exact
  twelve-row `d=1,2,3`, `N=2,4,8,16` obstruction to the standard tensor-`Q1`
  all-pairs `O(h)` QF2 implementation.  It explicitly does not refute other
  reconstructions or the regular-solution residual route.
- `artifacts/data/continuum_c2_one_sided_free_residual_neutral_fixture_v1.json`:
  Round-10 neutral ideal one-axis residual fixture.  Smooth cell-centred and
  periodic probes support at least first order, while the vertex-dual constant
  mode converges to the analytic `sqrt(h)` obstruction.  All continuum-rate,
  production, science, C1--C3, and release flags remain false.
- `artifacts/data/continuum_c2_complex_sector_h2_neutral_fixture_v1.json`:
  Round-11 neutral constant-coefficient mixed-NP, bounded-multiplier,
  sector-geometry, `lambda=-z`, oriented Dunford, and incomplete-gamma
  fixture.  Every physical promotion flag is strict Boolean false.
- `artifacts/data/continuum_c1_stationary_integral_source_v1.json` and
  `continuum_c1_fixed_row_raw_flux_source_v1.json`: authenticated same-backend
  Round-171 fixed-row sources for physical axis-cell integrals and formula-defined
  raw masses, rates, common edge fluxes, gauge, and density ratios.  They are
  not a correlated production member.
- `artifacts/data/continuum_c1_genuine_joint_refinement_family_v2.json`:
  Round-172 twelve-family ideal dyadic geometry authority.
- `artifacts/data/continuum_c2_source_bound_map_cut_killing_contract_v1.json`:
  Round-173 source/hash-bound symbolic ideal contract with all production and
  project promotion flags false.
- `artifacts/data/continuum_c1_twelve_family_ideal_fixed_box_C1_composition_v1.json`:
  Round-174 ideal fixed-box composition contract; existence-constant
  half-order conclusions are distinct from computable C2 evidence.
- `artifacts/data/continuum_c1_c2_n0_member_spec_v2.json`,
  `continuum_c1_c2_n0_anti_vacuity_policy_v2.json`,
  `continuum_c1_symbolic_control_method_source_v1.json`,
  `continuum_c1_n0_same_member_preflight_outer_manifest_v1.json`, and
  `continuum_c1_n0_same_member_symbolic_preflight_candidate_v1.json`:
  Round-176's successor metadata and strictly non-promoting level-`n=0`
  same-member preflight.  They expose nine uncleared blockers and materialize
  neither the reserved formal candidate nor an acceptance receipt.
- `artifacts/data/continuum_c1_c2_n0_predecessor_authority_candidate_v1/`:
  Round-177's canonical seven-file preproduction package.  It freezes the
  candidate member, anti-vacuity policy, parameter and method registries,
  predecessor-prefix manifest, external-review request, and bundle.  B04
  structural preparation is true; B06, external commitment, ordered replay,
  every blocker clearance, and every scientific/release promotion are false.
- `artifacts/data/continuum_c1_n0_role10_numerical_operation_model_v1_candidate.json`
  and `continuum_c1_n0_role10_numerical_operation_model_v2_candidate.json`:
  authenticated historical rejected v1 lineage and the immutable Round-179
  prospective result-blind v2 contract.  The latter is 212,071 bytes with
  SHA-256 `ac0c2b18...f8a6b`; neither file is numerical execution evidence.
- `audits/continuum_c1_sg_manufactured_round1_20260717.md`: immutable v1
  diagnostic boundary and first mutation-sentinel record.
- `audits/continuum_c1_fixed_1d_mosco_repair_round2_20260717.md`: hash-specific
  proof/code attack, gauge-containment P1 repair, executable interpolant
  sentinel, C0-v1 staleness boundary, and local scoped `P0=P1=P2=0` re-audits.
- `audits/continuum_c1_refinement_functional_bridge_round4_20260717.md`:
  Round-4 hash-specific chronology for the successor proof candidate, machine
  contract, neutral free-axis/tensor fixture, conditional manuscript
  integration, and retained complete-C1/C2/C3/release HOLD boundary.
- `audits/continuum_c1_varying_space_resolvent_mosco_round5_20260717.md`:
  Round-5 hash-specific attacks on unitarization, all resolvent shifts, the
  dual liminf formula, recovery diagonal, asynchronous finite tensor products,
  and bounded physical-volume multipliers; the then-open ideal premises are
  composed only later in Round 174.
- `audits/continuum_c1_production_gauge_killing_bridge_design_round6_20260717.md`:
  Round-6 design-only audit of the global gauge, common flux, physical
  normalization, reconstructed killing, and acyclic evidence architecture.
- `audits/continuum_c2_quantitative_positive_time_route_round7_20260717.md`:
  Round-7 theory/fixture audit, including the pi-certificate and numeric-alias
  repair chronology, final 97/97 executable assertions, and retained C2 HOLD.
- `audits/continuum_c1_symbolic_bridge_neutral_contract_round8_20260717.md`:
  Round-8 exact-identity, provenance, 59/59 test, currentness-P1 repair, and
  final ten-file `P0=P1=P2=0` audit with all production/C0--C3 flags false.
- `audits/continuum_c2_qf2_checkerboard_residual_route_round9_20260717.md`:
  exact checkerboard no-go theorem, 90/90 fixture, mixed-boundary extension,
  and conditional one-sided residual/sector route with complete C2 retained
  false.
- `audits/continuum_c2_one_sided_free_sg_residual_round10_20260717.md`:
  exact flux proof, vertex endpoint sharpness, asynchronous tensor slicing,
  107/107 independent checks, the mutation-preflight P1 repair, 30/30
  fail-closed mutation assertions, and retained production/C2/C3 HOLD boundary.
- `audits/continuum_c2_mixed_neumann_periodic_sector_h2_round11_20260717.md`:
  complex-convention erratum, mixed graph-domain and sector proof chronology,
  contour orientation, 1482/1482 neutral fixture receipt, current 7+24-page
  PDF QA, and the retained source-binding/C2/C3/release boundary.
- `audits/round_170_production_killing_geometry_two_repeat_outer_replay.md`:
  two-repeat outer-process acceptance of the control-free factorized killing
  geometry only; concrete killing and the full operator remain absent.
- `audits/round_171_fixed_row_stationary_raw_flux_authenticated_source_audit.md`:
  authenticated MPFR executed-byte/currentness boundary, physical-integral
  reconstruction, common raw-flux containment, and explicit same-backend and
  same-member nonclaims.
- `audits/round_172_genuine_joint_refinement_family_v2.md` and
  `audits/round_173_source_bound_map_cut_killing_lemma.md`: exact-byte
  geometry/source-bound audit trail for the twelve ideal tails.
- `audits/round_174_twelve_family_ideal_fixed_box_c1_composition.md`:
  repaired-byte independent mathematical and executable audit of the ideal
  twelve-family fixed-box C1 composition; final `P0=0`, `P1=0`, with two
  documented non-blocking provenance/formalization `P2` limitations.
- `audits/round_175_round174_post_audit_acceptance_receipt.md`: durable
  post-freeze trace for the separate mathematical and executable re-audits of
  the seven exact Round-174 objects; final `P0=0`, `P1=0`, `P2=3`, with no
  production, computable-C2/C3, root-transfer, or release promotion.
- `audits/round_176_production_n0_same_member_symbolic_preflight.md`:
  hash-specific mathematical/executable review and repair chronology for the
  metadata preflight; final `P0=0`, `P1=0`, `P2=2`, with nine blockers and no
  correlated same-member, formal-candidate, C1--C3, F0--F3, or release
  promotion.
- `audits/round_177_n0_predecessor_authority_structural_candidate.md`:
  hash-specific mathematical, provenance, and executable audit of the
  whole-directory candidate under its no-hostile-writer contract; final
  `P0=0`, `P1=0`, `P2=3` after a mutation-suite P1 repair, with B04 prepared,
  B06 open, all nine `cleared=false`, and no external commitment, roles 8--10
  replay, same-member acceptance, C1--C3, F0--F3, or release promotion.
- `audits/round_178_candidate_native_role_8_10_method_closure.md`:
  repair and independent-audit chronology for the outcome-free factorization,
  result-blind registry-v4, and structural member-v4 foundations.  The final
  internal artifacts are factorization `1cf32a...`, registry `e403a9...`, and
  member `b2982e...` with identity `68c8f9...`; none is an external
  commitment, complete B06 closure, fresh roles 8--10 replay, same-member
  acceptance, C1--C3, F0--F3, root-transfer, or release evidence.
- `audits/round_179_role10_numerical_operation_model_v2.md`: frozen-byte,
  independent-oracle, 46-case, and adversarial audit record for the prospective
  role-10 operation-model-v2 contract, with implementation, execution,
  commitment, B06, same-member, continuum, and release gates retained false.
- `audits/round_180_roles_8_10_plan_v2_static_precommit_protocol.md`:
  hash-specific freeze and adversarial repair ledger for the plan-v2 static
  vocabulary/validator, with 42/42 synthetic tests and every runtime,
  implementation, commitment, replay, scientific, and release gate retained
  false.
- `audits/round_181_roles_8_9_v3_cli_hold_shells_and_runtime_feasibility.md`:
  hash-specific audit of four role-8/9 v3 fail-closed basename/CLI sentinels
  and the first live runtime-feasibility probe; numerical implementations
  remain `0/6`, and the integrated ledger is `P0=0/P1=2/P2=4`.
- `audits/round_182_runtime_helper_prototype_rejection_and_static_closure_repair.md`:
  independent rejection of the first runtime-truth helper drafts, conversion
  of the v1 origin probe into a frozen inert HOLD sentinel, and component-scope
  freeze of the caller-authenticated AST resolver after 93/93 focused cases.
  The real wrapper plus `gmpy2.gmpy2` topology is representable, but no trusted
  runtime authority, v3 adapter, actual six-source/runner closure, plan,
  bundle, request, commitment, or replay exists.
- `audits/round_183_static_runtime_inventory_and_generic_process_supervisor.md`:
  rejection and two-stage repair chronology for the static runtime-inventory
  and generic process-supervisor prototypes.  The final component scopes pass
  92/92 and 32/32 focused cases plus five supervisor repeat loops, but the
  recommended sealed root and persistent inventory JSON remain absent, no
  authenticated runtime probe or actual six-source/runner closure exists, and
  the integrated ledger remains `P0=0/P1=2/P2=4`.
- `audits/round_184_sealed_static_runtime_root_materialization.md`: frozen
  one-shot materializer, independent current-tree validator, 96-case suite,
  exact external six-file root, and persistent inventory/receipt acceptance
  at component `P0=P1=P2=0`.  It records the Darwin provenance-name
  supersession and preserves every import, probe, runtime-closure, role-v3,
  replay, same-member, continuum, science, release, and submission nonclaim.
- `audits/round_185_o113_exploratory_same_process_composition.md`: first real
  O113/Base same-process factorized numerical composition, disclosed
  result-blind barycentre, 12-case deterministic replay suite, and independent
  post-fix mathematical/code attacks.  It accepts the bounded exploratory
  component at `P0=P1=0` with one temporary-output hardening P2 and leaves
  production same-member, the full numerical operator, C0--C3, F0/F1,
  release, and submission false.
- `artifacts/data/physical_production_initial_stream_v1/`: canonical 12-row,
  206-entry file-backed source/partition/free-axis/sparse-box bundle.
- `artifacts/data/physical_production_initial_stream_v1_relational_receipt.json`,
  `_independent_receipt.json`, and `_geometry_receipt.json`: same-core,
  separately implemented semantic, and packed-axis geometry joins.  The last
  establishes only forward/back free-axis rate payloads tied to exact
  partition and axis-relation hashes; it does not establish killing or the
  full generator.
- `artifacts/data/physical_production_initial_clean_process_replay_v1.json`:
  two-repeat outer-process receipt with ten distinct observed PIDs and explicit
  negative promotion flags for F0, continuum, and positive-budget science.
- `manuscript/SUBMISSION_METADATA_REQUIRED.md`: hard no-submit checklist.
- `manuscript/README.md`: human-facing source/PDF pointer.  Only the
  theorem-first main and Supplemental working set is active; the similarly
  named 13-page manuscript is an archived historical reconstruction and must
  not be uploaded as the current paper.
- `artifacts/data/gig_constructive_pilot.json`: machine-readable G0 evidence.
- `artifacts/data/manuscript_numerical_sources_manifest.json`: fail-closed
  release manifest for all five current numerical result families, including
  manifests, producers, tests, protocols, dependencies, and the G1d-to-G1c pin.
- `artifacts/data/continuum_g1_smoke.json`: machine-readable G1a smoke evidence.
- `artifacts/data/continuum_g1_discovery_manifest.json`: frozen G1b discovery inputs.
- `artifacts/data/continuum_g1_discovery_result.json`: completed formal line evidence.
- `artifacts/data/continuum_g1_manual_review_result.json`: five-times-finer
  time-sampling diagnosis at the flagged control.
- `artifacts/data/continuum_weak_budget_design_result.json`: discrete $B=0$
  free-exposure cusp and 5,151-control screen; all continuum/finite-$B$ flags false.
- `artifacts/data/continuum_g1c_simplex_manifest.json`: byte-pinned 66-control
  G1c design; a candidate can seed only a separately frozen confirmation.
- `artifacts/data/continuum_g1d_fold_confirmation_result.json`: one audited
  $B=0.6$, 207,025-state finite-grid fold with the complete mixed fold jet.
- `artifacts/data/continuum_observable_four_patch_result.json`: byte-reproducible
  exact-kernel four-slab cusp and three-maximum/two-minimum confirmation; all
  interval, finite-$B$, and project claim flags remain false.
- `artifacts/data/continuum_observable_four_patch_d3_result.json`: byte-identical
  exact sphere-kernel physical-$d=3$ confirmation with a non-Bessel spherical-
  coordinate cross-check; finite-$B$/independent-PDE/project flags remain false.
- `artifacts/data/continuum_broad_patch_b0_bridge_result.json`: result-informed
  broad-patch $B=0$ exact-kernel/four-mesh bridge; positive-$B$ and unbounded-box-
  limit flags remain false.
- `artifacts/data/positive_b_broad_four_slab_result.json`: canonical fixed-control
  $B=0.01$ two-odd-mesh result with five alternating simple stationary roots on
  the saved screen through $t=35$, three positive basin reaction masses and tail
  checks through $t=100$, no post-$35$ root exclusion, and all continuum/project
  flags false.
- `artifacts/data/positive_b_broad_four_slab_reproducibility.json`: internally
  consistent two-process byte-identity and canonical-promotion record; the
  post-result auditor did not witness the two historical subprocesses.
- `artifacts/data/positive_b_broad_four_slab_independent_audit.json`: frozen
  exactly-once algebraic reconstruction of the saved canonical evidence; it is
  not an independent semigroup or solver rerun.
- `artifacts/figures/positive_b_broad_four_slab.pdf` and its `_metadata.json`
  sidecar: manuscript-ready rendering of the fixed-control result, pinned to
  the canonical result, reproducibility record, independent audit, plotter,
  and plot tests; the figure states all negative scope boundaries on-page.
- `audits/round_03_g1_smoke_attack.md` and `audits/round_03_resolution.md`:
  mutation attack and closure evidence for G1a.
- `audits/round_16_g1c_prerun_audit.md`, `audits/round_17_weak_budget_audit.md`,
  and `audits/round_19_pde_theory_resolution.md`: independent pre-run,
  numerical, and theorem-resolution gates.
- `audits/round_23_direct_multimode_theory_attack.md`: repaired adversarial
  audit of the direct physical fixed-finite-mode theorem.
- `audits/round_25_g1d_fold_audit.md` and
  `audits/round_26_g1d_audit_resolution.md`: independent fold reconstruction
  and the fail-closed resolution of two portability/root-scope P2 findings.
- `audits/round_25_observable_four_patch_self_audit.md`: independent real-jet,
  root, quadrature, and claim-boundary reconstruction of the four-slab result.
- `audits/round_28_observable_four_patch_d3_self_audit.md`: physical-$d=3$
  representation, convergence, reproducibility, and claim-boundary audit.
- `audits/round_61_allocation_v2_independent_prerun_attack.md`,
  `audits/round_64_allocation_v3_repair_freeze.md`, and
  `audits/round_74_allocation_v3_independent_prerun_attack.md`: allocation-cusp
  attack/repair history.  The fresh v3 attack found one P0 and six P1 defects;
  no $65/97$ scientific run is authorized until a repaired version passes a
  new independent pre-run audit.
- `audits/round_59_positive_b_canonical_result_closure.md` and
  `audits/round_60_positive_b_closure_independent_reaudit.md`: canonical
  positive-budget closure, independent hash/arithmetic reconstruction, tight-
  margin disclosure, and the fixed-control-only claim boundary.
- `audits/round_63_positive_b_figure_closure.md` and
  `audits/round_66_positive_b_figure_provenance_addendum.md`: deterministic
  vector-figure closure, visual QA, five-role source provenance, and atomic
  PDF/metadata publication tests without rerunning the scientific auditor.
- `audits/round_67_stageb_v3_independent_attack.md`,
  `audits/round_69_stageb_v4_design_resolution.md`,
  `audits/round_70_stageb_v4_independent_attack.md`, and
  `audits/round_72_stageb_v5_design_resolution.md`: repeated Stage-B design
  attacks and v5 repair.
- `audits/round_73_stageb_v5_independent_attack.md`: independent exact-arithmetic
  attack with P0=P1=P2=0 and verdict `ACCEPT-DESIGN / HOLD-EXECUTION`.  It
  authorizes only construction and independent audit of the synthetic T0
  selector package; no Stage-A, Stage-B, or off-lattice science is authorized.
- `audits/round_68_positive_b_main_integration_independent_attack.md`: the
  independent manuscript-integration HOLD that triggered strict same-byte
  source snapshots, reconstructed numerical gates, figure-metadata contracts,
  and explicit $t=35$ versus $t=100$ wording.
- `audits/round_71_positive_b_main_integration_closure.md`: independent
  P0=P1=P2=0 closure of that integration scope, including 97/97 focused tests,
  static analysis, immutable verified input snapshots, and byte-identical
  clean PDF builds.  Its verdict is `ACCEPT-MAIN-INTEGRATION` only; allocation
  cusp, continuation, independent killed-process, and PRR promotion remain
  held.
- `audits/round_77_general_dimension_theory_attack.md` and
  `audits/round_79_general_dimension_repair.md`,
  `audits/round_82_general_dimension_independent_postedit_attack.md`, and
  `audits/round_84_general_dimension_scope_repair.md`: mathematical
  admissibility, proof/scope promotion, independent detection of one surviving
  dimension-specific contact phrase, and its explicit $d$-ball/unit/test
  repair.  Promotion remains held for an independent post-fix recheck and does
  not add numerical support beyond physical $d=2,3$.
- `audits/round_149_exact_m_supplement_migration_independent_attack.md`:
  hash-specific independent acceptance of the complete paper proof and
  theorem-first 5+20-page build (`P0=P1=P2=0`), without finite-parameter or PRR
  promotion.
- `audits/round_151_selector_orphan_test_race_repair.md`: withdraws the
  Round-147 macOS lock P1 as a harness false positive, accepts the final
  process-lifetime/resource surface on the tested runtime, and retains one
  second-POSIX portability P2.
- `audits/round_153_selector_round151_independent_attack.md`: independent
  read-only closure of the final selector/test bytes (`P0=P1=0`), including 45
  fresh orphan-lock probes and the full 142-test suite; it retains second-POSIX
  and causal-contention-handshake P2 items.
- `audits/round_150_f0_packed_directed_action_stage.md`: implementation and
  self-audit of the bounded packed directed-action primitive (56 small-state
  tests); production F0 and independent acceptance remain held.
- `audits/round_152_f0_packed_directed_action_independent_attack.md`: rejects
  the Round-150 bytes after reproducing a bound-runtime stride-2 Boolean ufunc
  defect at production-relevant block sizes; it also requires heterogeneous
  saved oracles and preserves fresh-verifier/runtime-probe P2 boundaries.
- `audits/round_154_f0_packed_directed_action_repair.md`: repairs the validator
  P1 with contiguous scratch, adds vectorized runtime probes, heterogeneous
  exact oracles, and a consistency digest while keeping F0 held.
- `audits/round_155_f0_packed_directed_action_independent_reaudit.md`:
  independently accepts the repaired bytes only as a bounded implementation
  primitive; 99 fresh block-size processes and 320 heterogeneous exact rows
  pass, while authentication/fresh verifier and all later F0 stages stay open.
- `audits/round_167_production_initial_stream_clean_replay_and_continuum_erratum.md`:
  hash-specific closure of the 12-row control-free source/partition/free-axis
  bundle, packed-axis joins, two-repeat clean serialized replay, manuscript
  integration, and the Round-165 reversible-density erratum.  It keeps killing,
  the full generator, production resource evidence, F0, continuum topology,
  positive-budget science, and release explicitly open.
- `audits/round_168_production_killing_geometry_strict_full_freeze.md`:
  independently audits the regenerated exact-full producer and 76-file bundle
  at `P0=0`, `P1=0`, `P2=2`, accepting it only as input to the separate-source
  verifier.  It records 227,693 exact-zero, 4,142 exact-unit and 1,304 partial
  contact cells while keeping concrete killing, operator assembly, F0/F1,
  continuum and release held.

## Non-negotiable reporting rules

Every claimed mode must be supported by isolated alternating roots of
`f_t`, nonzero curvature margins, a prominence threshold, and a tail/root
isolation interval.  A cusp alone does not prove trimodality: a remote
maximum--minimum pair must also persist.  Fold transfer requires the relevant
joint third-order jets; cusp transfer requires the relevant fourth-order jets.
The word `root_count` in a sampled sign-change screen is never an
interval-exhaustive exclusion of tangential or sub-grid roots.  A free-exposure
relative-shape pass is never relabeled as positive-$B$ event-mass evidence.  In
the fixed positive-budget record, root support ends with the saved $t\leq35$
screen, whereas event-mass and tail support ends at $t=100$; neither is an
interval proof and the latter does not exclude post-$35$ extrema.
