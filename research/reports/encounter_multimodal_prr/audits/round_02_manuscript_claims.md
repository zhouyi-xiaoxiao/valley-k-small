# Round 02 adversarial audit: manuscript claims versus theorem program

Date: 2026-07-13  
Scope: `manuscript/encounter_multimodal_prr.tex`,
`notes/theorem_program.md`, and `notes/research_contract.md`  
Action taken: audit only; no manuscript or theory note was modified.

## Verdict

**FAIL CLOSED for submission.**  The manuscript is candid that the continuum
program is unfinished, so it is not a wholesale attempt to pass conjectures off
as results.  It is nevertheless not claim-safe yet.  The central conserved
resource is not the same mathematical functional in all three documents, the
displayed model-to-continuum scaling is weaker and less precise than the theorem
target, numerical refinement is allowed to sound like a substitute for the
required analytical remainder, and the current novelty presentation repeats
several ingredients already assigned to the preceding encounter/DPMA work.

The reduced three-channel cusp is not the main problem: it is scoped to the
reduced family, and the manuscript correctly states that a cusp alone does not
prove trimodality.  The blockers are the physical realization, theorem status,
jet-complete transfer, and non-overlap boundary.

Severity used below:

- **P0 — release blocker:** submission or public scientific claim is unsafe.
- **P1 — major scientific correction:** the paper's theorem, model, or novelty
  can be misread or is inconsistent across the three sources.
- **P2 — precision/editorial correction:** not fatal alone, but must be fixed
  before a final claim audit.

## P0 — release blockers

### P0.1 The conserved “physical budget” is not one defined functional

**Conflict.**  The manuscript first defines a configuration-space killing field
`kappa(z)` supported in the encounter region (manuscript lines 93--103), but its
budget is then imposed only on a centre-coordinate field
`kappa_w(c)` (lines 108--115).  The research contract likewise defines installed
centre-field material by `integral kappa_w(c) dc = B` (contract lines 32--45).
The theorem program instead defines

`c_j = integral_D Psi_j(x) dx` and `c^T u = B`

for `Psi_j(x1,x2) = chi_a(x1-x2) psi_j(C_eta)` (theorem program lines
75--88 and 119--144).  These two costs coincide up to a common constant only
when the coordinate Jacobian, contact cross-section, domain, and all patch
supports make that factor independent of `j`.  That is not automatic in the
general bounded-domain theorem model.

**Why this blocks the paper.**  “Conserved spatial reactivity” is in the title
and is the control manifold on which every projection, fold, cusp, and mesh
comparison is defined.  If the cost changes between the theorem and numerical
model, the claimed control manifold changes too.

**Required repair.**  Select one resource definition and use it everywhere.
The contract-compatible choice is:

`K_w(x1,x2) = chi_a(x1-x2) B sum_j w_j phi_j(C_eta)`,

with the declared installed-catalyst cost
`C(w) = integral kappa_w(c) dc = B`.  Then define its finite-dimensional cost
covector explicitly and use that covector in every tangent projection.  If the
configuration-space integral is retained instead, replace the equal-weight
simplex by `c^T u = B` and account for unequal `c_j`.  In either choice, prove
the common-factor equivalence for any symmetry-reduced slab geometry; do not
silently assume it for arbitrary localized patches.

### P0.2 Equation (bridge) does not preserve the theorem program's scaling or budget

**Conflict.**  The manuscript writes

`f_{epsilon,a,rho,L}(t;w) = epsilon F_{m,d}(t;w) + r(t;w)`

(manuscript lines 191--203) after declaring a fixed budget `B`.  It does not
define whether `epsilon` is reaction strength, budget, contact radius, or an
overall density amplitude; it uses physical time in both terms; and it assumes
that the reduced mixture weights are already the physical amplitude controls.
The theorem program instead requires a dimensionless time, an independently
defined positive amplitude `A_epsilon`, a budget-preserving realization map
`u_epsilon(theta)`, and a budget `B_epsilon` conserved across controls for each
`epsilon` (theorem program lines 649--702).  It explicitly warns that a proof
with `B_epsilon -> 0` does not establish a theorem at one fixed nonzero budget.

**Required repair.**  Replace the schematic bridge by the actual normalized
target

`m0 A_epsilon^{-1} f_epsilon(m0 tau; u_epsilon(theta)) -> F(tau;theta)`

uniformly in the exact mode/fold/cusp jet on a declared compact window.  Define
the joint scaling path, `B_epsilon`, `A_epsilon`, and the physical realization
map.  State separately whether the theorem is (i) a weak-budget existence
result, or (ii) a stronger result at a fixed nonzero installed-catalyst budget.
Do not identify GIG probability weights with rate-volume products without the
transport prefactors and cost normalization.

### P0.3 The abstract lets numerical “testing” sound like the missing theorem

**Conflict.**  The abstract calls continuum persistence the “gating result” and
says the final paper will “test it” with a quotient, odd/even meshes, and an
independent numerical method (manuscript lines 57--62).  The research contract
requires a quantitative model-to-continuum bridge (contract lines 18--26), and
the theorem program says that bridge must become **PROVED**, at least in the
mode and fold jets (theorem program lines 820--834).  Mesh convergence and a
second solver can produce strong continuum numerical evidence; they do not
prove the uniform encounter-to-channel remainder.

**Required repair.**  Split the final-paper gate into two independent claims:

1. an analytical jet-level remainder theorem, with a displayed error tending
   to zero and quantitative margins; and
2. resolved 2D/3D numerical realizations with parity and independent-method
   checks.

The abstract should call the former a **theorem target** until proved and the
latter **continuum numerical verification**.  If the project elects to submit a
primarily numerical PRR paper instead, the theorem contract and headline must be
rewritten; numerical agreement must not inherit the word “persistence theorem.”

### P0.4 The manuscript does not disclose the overlap that defines its novelty

**Conflict.**  The contract says the preceding encounter work already contains
Green/Woodbury reduction, spectral sign variation, fixed-budget
Frechet/Duhamel response, finite folds, and reduced GIG screening (contract
lines 11--30).  The theorem program adds that DPMA already contains the
rank-one response, finite-CTMC fold classification, universal fold powers, and
a nondegenerate cusp (theorem program lines 22--43).  The manuscript has no
citation or disclosure of either predecessor, while the abstract and response
section say “we derive” the response and then present the generic fold powers
and cusp conditions (manuscript lines 53--56 and 155--187).  Its bibliography
contains neither predecessor.

**Why this blocks the paper.**  As written, a referee can reasonably conclude
that the claimed novelty is the response/fold/cusp package that the internal
contract expressly says is old.  Conversely, the genuinely non-overlapping
multi-rate projected-jet theorem is almost absent: the manuscript gives only a
scalar projected `f_t` direction.

**Required repair.**  Add an explicit related-work/non-overlap paragraph and
the predecessor citations or, until public identifiers exist, an accurate
companion-manuscript disclosure approved by both authors.  Mark Duhamel,
generic fold powers, and catastrophe normal forms as shared background.  Make
the new chain visible:

1. fixed-budget **multi-rate projected-jet controllability**;
2. a sufficient at-least-`m` theorem in the separated GIG class; and
3. the model-specific continuum jet estimate plus physical 2D/3D realization.

No “first response,” “first fold,” “first cusp,” or “first catastrophe” wording
is admissible.

### P0.5 The file is a three-page research prospectus with unresolved submission metadata

**Evidence.**  The source labels itself an independent working draft
(manuscript lines 1--3), the abstract and numerical section are written in the
future tense, and the acknowledgments explicitly say that funding and computing
statements await author confirmation (lines 255--257).  Author names and a live
email are already embedded in the TeX and PDF metadata, but there is no recorded
confirmation here of author order, corresponding-author role, affiliation,
title, or public disclosure of the related manuscripts.

**Required repair.**  Keep a hard no-submit flag until both authors confirm the
author block and overlap disclosure, all scientific gates are completed, the
pending acknowledgment is replaced, and data/code availability plus archival
identifiers are supplied.  Update the manual date at release and complete the
journal's final ethics/conflict/contribution checklist as applicable.  This
finding does **not** assert that the present names or order are wrong; it says
that they are publication metadata requiring explicit author approval.

## P1 — major scientific corrections

### P1.1 “Any finite `m` and physical dimension `d`” exceeds the contracted result

The introduction targets a continuum configuration for any finite mode count
and any physical dimension (manuscript lines 80--84).  The contract promises
resolved 2D and 3D realizations, not an arbitrary-`d` continuum theorem
(contract lines 21--26).  The theorem program proves arbitrary finite `m` only
inside the reduced GIG class and leaves its bounded finite-radius realization
conjectural (theorem program lines 381--399 and 455--477).  It also states that
the screening exponent `p=(d+3)/2` is not universal across patch geometries
(lines 812--816).

**Required repair.**  Use the precise split:

- “any prescribed finite `m`” only for the reduced GIG theorem;
- continuum transfer for a fixed finite design under declared asymptotics; and
- resolved physical evidence in `d=2` and `d=3` for the stated slab/localized
  geometry.

Retain arbitrary `d` only if a dimension- and geometry-explicit heat-kernel or
capacity theorem is actually supplied.  Replace “arbitrarily many” with “any
prescribed finite number” wherever an infinite-mode reading is possible.

### P1.2 The GIG theorem has incompatible status and a stronger manuscript statement

The manuscript labels the separated-channel statement a “Constructive theorem
target” and says the numerical pilot is not a proof (manuscript lines 139--147).
The theorem program labels Theorem 4.1 **PROVED within the GIG mixture class**
(theorem program lines 381--399 and 846--848).  At the same time, the manuscript
claims `m-1` **nondegenerate** minima, whereas Theorem 4.1 and Lemma 3.1 establish
only intervening local minima; nondegeneracy of those minima is not proved
(theorem program lines 303--318 and 395--399).

The contract also demands explicit robustness/observability margins.  The
theorem program proves finite-`m` modal existence but separately proves that
inverse-height weights do not give a uniform channel-mass or peak-height floor
as `m` or `R` grows (theorem program lines 479--524).

**Required repair.**  Establish one source of truth after an independent proof
check.  A defensible split is:

- **PROVED:** at least `m` nondegenerate maxima and at least `m-1` intervening
  minima for sufficiently large separation in the explicit GIG class;
- **not yet proved unless added:** nondegenerate separator minima, a usable
  closed quantitative threshold, and physical observability floors.

Remove “nondegenerate” from the minima unless a separator-curvature proof is
added.  Report how every weight, absolute peak height, prominence, and event
mass deteriorates with `m` and `R`; never imply a uniform-in-`m` observability
theorem.

### P1.3 “Locally optimal redistribution” is undefined and repeats only the old scalar case

The manuscript says that projecting the functional gradient of `f_t` onto the
budget tangent gives the locally optimal redistribution (manuscript lines
166--169).  A projection and an optimum require a declared inner product or
control norm, and positivity makes the statement valid only at an interior
control unless a tangent cone is used.  The theorem program correctly introduces
`M > 0`, a cost covector, a projected multi-jet matrix, a rank condition, and a
minimum-`M`-norm pseudoinverse (theorem program lines 194--261).

Moreover, changing `f_t` at one fixed time is not by itself control of a fold,
which is the simultaneous zero of `(f_t,f_tt)`.  The scalar direction is
explicitly identified by the theorem program as the previously derived `q=1`
case.

**Required repair.**  State the admissible finite patch-amplitude space, the
cost covector, an `M`-norm, interior/tangent-cone assumptions, and the multi-jet
rank condition.  Include the minimum-norm control formula for a target vector
of derivatives.  Any claimed physical controllability must add a continuum-
stable lower bound on the projected smallest singular value; abstract linear
algebra alone is not a model rank certificate.

### P1.4 The numerical fold gate omits part of the minimal persistence jet

The manuscript requires converged fold coordinates and nonzero `f_ttt` and
`f_{t theta}` (manuscript lines 220--223).  Those quantities establish the
normal-form determinant at a computed root, but the theorem program's minimal
jet for persistence is

`{f_t, f_tt, f_ttt, f_{t theta}, f_{tt theta}}`

(theorem program lines 543--577).  In particular, `f_{tt theta}` is required for
`C^1` convergence of `H=(f_t,f_tt)`.  Merely observing nonzero jets on successive
grids is not an a priori/a posteriori continuum root certificate.

**Required repair.**  Display the exact fold jet and require convergence of all
its entries, including `f_{tt theta}`, on a neighborhood of the root.  Pair
parity extrapolation with either a justified `||H_h-H||_{C^1}` error bound and
an implicit-function/Newton--Kantorovich certificate, or describe the outcome
strictly as a converged numerical fold rather than a proved continuum fold.

### P1.5 The cusp conditions are correct, but the persistence gate is incomplete

The manuscript correctly gives `f_t=f_tt=f_ttt=0`, `f_tttt != 0`, rank two of
the projected `(f_t,f_tt)` gradients, and the need for a remote max--min pair
before claiming trimodality (manuscript lines 178--187).  This part survives the
logical audit.  However, “the corresponding fourth-order jets” does not identify
the exact transfer set promised in the abstract.  The theorem program requires

`{f_t,f_tt,f_ttt,f_tttt, f_{t theta_i},f_{tt theta_i},f_{ttt theta_i}: i=1,2}`

(theorem program lines 579--636).  The research contract gives a singular-value
floor but no explicit continuum convergence/residual floor for the full cusp
jet (contract lines 72--83).

**Required repair.**  Display the exact cusp jet, add scaled residual and
nonzero-`f_tttt` gates, require convergence of `f_{ttt theta_i}`, and certify the
remote critical-point pair with the same root, curvature, prominence, and tail
margins.  Keep “reduced cusp” and “continuum cusp” as separate evidence labels.

### P1.6 “Exact translation quotient” needs its symmetry and retained centre coordinate

The manuscript proposes an “exact translation quotient” but does not say what
coordinate is integrated out or which catalyst symmetries make the marginal
closed (manuscript lines 211--218).  The theorem program expressly forbids
treating a translation-invariant relative-coordinate mean-time quotient as a
centre-patterned 3D reaction-time-density realization (theorem program lines
807--810).

An exact quotient can be valid if it removes only a common symmetry coordinate
while retaining the centre coordinate on which reactivity is patterned.  It
then represents a restricted patch family, for example transversely invariant
slabs, not arbitrary localized disks or balls.

**Required repair.**  State the full coordinates, the integrated symmetry
coordinate, the retained centre variable, the closure proof, and the exact
patch/transport/initial-law symmetry assumptions.  Call slabs “slabs.”  Do not
promote that calculation to a localized-patch or generic 3D realization; the
independent 3D/off-lattice gate must preserve genuine centre patterning.

### P1.7 The manuscript never defines how a reduced channel simplex becomes the physical simplex

The same symbol `w` is used for normalized GIG mixture weights and for physical
catalyst weights (manuscript lines 108--115, 129--145, and 191--203).  The
theorem program explicitly says that GIG weights map to rate-volume products
only after transport prefactors and conserved costs are included (theorem
program lines 455--477).  Without a realization map, a reduced cusp in the GIG
simplex is not automatically a cusp reachable by redistributing fixed catalyst.

**Required repair.**  Use separate symbols for probabilistic mixture weights
and physical amplitudes.  Define and analyze the budget-preserving realization
map between them, including its Jacobian and rank.  A fold/cusp can transfer
only if that map remains interior and nonsingular in the relevant control
directions.

## P2 — precision and editorial corrections

### P2.1 The evidence vocabulary is inconsistent and “NO-GO” has two meanings

The theorem program has four labels: **PROVED**, **NUMERICALLY VERIFIED**,
**CONJECTURAL**, and **NO-GO**, with NO-GO reserved for a counterexample or
regularity obstruction (theorem program lines 9--20).  The contract adds
**CONTINUUM VERIFIED** and redefines NO-GO as a failed project gate (contract
lines 47--59).  The manuscript uses a third, lower-case three-level vocabulary
(manuscript lines 86--89).

**Required repair.**  Adopt one ontology, for example:

- **PROVED**;
- **NUMERICALLY VERIFIED — REDUCED**;
- **NUMERICALLY VERIFIED — CONTINUUM**;
- **CONJECTURAL**;
- **MATHEMATICAL NO-GO**; and
- **PROJECT GATE FAILED**.

The phrase “gating result” in the abstract should be “submission gate” or
“theorem target” until the result exists.

### P2.2 The current title is conditional on gates that have not passed

“Constructive control ... under conserved spatial reactivity” reads as an
achieved physical result, while the body says the physical bridge, 2D fold, and
3D realization are future work.  That is tolerable for a clearly internal
working draft, but not for a circulated preprint or submission.

**Required repair.**  Until the bridge and continuum gates pass, use an
explicitly qualified internal title or watermark.  Restore the strong title
only when the abstract can report completed results in the past tense with
quantitative evidence.

### P2.3 Quantify the reduced cusp rather than alternating between “cusp” and “candidate”

The abstract says a calculation “locates a well-conditioned cusp” (manuscript
lines 50--53), while the status section calls it a “reduced cusp candidate”
(lines 230--234).  This is not a continuum overclaim, but the evidence label is
unstable.

**Required repair.**  If deterministic residual, fourth-derivative, interior-
weight, and rank/conditioning gates have passed, call it **NUMERICALLY VERIFIED
in the reduced GIG family** and report the conditioning metric.  Otherwise use
“candidate” in both places.  In neither case call it a trimodal phase without
five isolated alternating critical points and a persistent remote pair.

### P2.4 Keep author-owned facts out of automated “fixes”

The names, order, email, funding, and relation to the companion works are
author-owned facts.  An automated audit may detect missing confirmation but
must not invent a funding source, reorder authors, add a corresponding author,
or fabricate a citation status.

**Required repair.**  Record explicit author confirmation as a release gate and
then update the metadata once.  The unresolved acknowledgment and predecessor
identifier should remain conspicuous until confirmed, not be silently deleted.

## Claims that passed this round

The following manuscript boundaries are correct and should be preserved:

1. The reduced mixture is not represented as a bounded continuum Doi result
   (manuscript lines 228--236).
2. The model-to-continuum bridge is explicitly called a theorem target rather
   than an established property (lines 189--209).
3. The broad fold/cusp time-derivative orders are correct: fold transfer reaches
   third order and cusp transfer reaches fourth order, subject to the missing
   mixed derivatives listed above.
4. The manuscript correctly refuses to infer trimodality from a cusp alone and
   requires a persistent remote maximum--minimum pair (lines 183--187).
5. It correctly demands isolated derivative roots, curvature, prominence, and
   tail isolation rather than visual peak counting (lines 220--226).
6. It correctly states that software/reproducibility PASS is not scientific or
   journal PASS (lines 238--242).

## Mandatory repair order before Round 03

1. Freeze one physical resource functional and one notation for the full
   configuration-space killing field.
2. Reconcile the GIG theorem's actual proved statement and evidence label;
   remove the unsupported nondegenerate-minimum and uniform-observability
   readings.
3. Replace the schematic bridge by the normalized, budget-preserving
   realization theorem and separate analytical proof from numerical evidence.
4. Rewrite the novelty paragraph and bibliography around the preceding
   encounter/DPMA boundary; promote multi-rate projected-jet controllability,
   not the old scalar projection or generic catastrophe facts.
5. Put the exact fold and cusp jets, including all mixed derivatives, into both
   theorem and numerical acceptance gates.
6. State the quotient symmetry and slab/localized-patch scope, then restrict
   the continuum dimension claim to what is actually proved or resolved.
7. Obtain author confirmation and clear every submission placeholder only after
   the scientific gates pass.

Round 03 should fail automatically if any abstract sentence cannot be mapped to
exactly one evidence label and one stored proof or numerical certificate.
