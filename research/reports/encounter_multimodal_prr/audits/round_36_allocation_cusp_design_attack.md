# Round 36: fixed-budget allocation-cusp design attack

Date: 2026-07-13  
Role: adversarial algebra, protocol, and claim-boundary audit  
Verdict: **PASS-DESIGN / HOLD-SCIENCE**

## 1. Scope and noninterference boundary

This audit attacks the proposed next same-family PRR promotion stage.  It does
not audit a positive-`B` cusp result because none exists in the files reviewed,
and it neither runs nor reads the current positive-`B` held-out output.

The frozen positive-`B` producer, tests, protocol, and manifest were read only.
Their hashes at the end of this design pass were:

| role | SHA-256 |
|---|---|
| current positive-`B` producer | `0c70ffb4a9034772928e2fa95d2ca79ef33754e5aa4157a2f101e15cb312b003` |
| current positive-`B` tests | `ee784d1cf6cc4e7ee66968deb8f3421394f697eebee3a50f783533aa469a8f78` |
| current positive-`B` protocol | `f25a8107d7a975342a3b1cbbf84c29df26654a8f6310f0429cba5ffdf7bcda00` |
| current positive-`B` manifest | `01b435c834cec9e7bfde2069b19fcdcaa4e06178ccfe0d4b6082f0705dfd5805` |

The scientific sources used were:

| source | SHA-256 |
|---|---|
| Round 33 promotion audit | `4c2037ebcbeb2f6cc2a38ac56919d513120683a294249432cca1f615b85d4f56` |
| mixed-jet theorem | `3fc37bafc6320556322e80daa2c56bad9fd4b19e1856100caa8adf92341a8007` |
| broad `B=0` result | `6a18e668401ae5776eebd7bd58c7bd553838db21998efdba2865cea094ae207b` |
| broad `B=0` producer | `d1d68667f5cbb9c8363a94f2f9ea22540f841065e02696f669beca9758e3a233` |

New design evidence audited:

| file | SHA-256 |
|---|---|
| algebra prototype | `547a1a983f8683acc103a05d47bbdc0f2111f4b9f680c571fa4371642d81241a` |
| algebra tests | `fa664d8d8737c7491c5663da8922b40ddcec9599b10463bff835f71dd04af7be` |
| promotion design | `ad072e83004ea3e3b5c3d01a58a872b5aedca74d13400fa04d6f917d4a06d1f5` |

## 2. Severity convention

- **P0:** could make the reported cusp/fold claim false, result-informed, or
  mathematically misoriented.
- **P1:** would leave the confirmation non-fail-closed, noncomparable across
  grids, or insufficient for the intended promotion.
- **P2:** provenance, naming, or reproducibility defect that does not by itself
  reverse the scientific result.

The final open count for the **design** is `P0=0, P1=0, P2=0`.  This is not a
scientific pass: all physical computations described by the design remain to
be implemented, frozen, run, and independently audited.

## 3. P0 algebra attacks

### P0.A — row/column orientation and tangent sign

**Attack.**  The existing positive-`B` code propagates the probability column
with `Q_B^T`.  It would be easy to carry the budget-tangent block into an
allocation calculation with the wrong sign or place the coupling in the
adjoint block.  A plausible but wrong formula is
`s_i'=A s_i + B diag(u_i)p`.

**Resolution.**  The design starts from the row generator

\[
Q=Q_0-BD_\kappa,
\]

so the column derivative is exactly

\[
s_i'=Q^Ts_i-BD_{u_i}p.
\]

The explicit-CSR block generator places `-B diag(u_i)` below the base column
block.  Both allocation state derivatives agree with separately propagated
centred finite differences.  **Closed.**

### P0.B — confusing total-budget and fixed-budget allocation derivatives

**Attack.**  The current producer reports `f_B,f_tB,f_ttB` while holding the
weight vector fixed.  Those scalars cannot supply the two independent
simplex-tangent columns required by a fixed-total-budget cusp.

**Resolution.**  The new chart has `1^T P=0`; `B=0.01` never changes in the
target calculation.  The two fields
\(u_i=\sum_jP_{ji}\kappa_j\) change allocation only.  The design explicitly
prohibits using the current budget tangent as an allocation column.  **Closed.**

### P0.C — omitted direct observable derivatives

**Attack.**  Propagating `s_i` and evaluating only
\(B\kappa^Ts_i\) misses the direct derivative of the killing observable and
of each generator iterate.  This error can preserve plausible state
sensitivities while corrupting the projected rank.

**Resolution.**  The audited recurrence

\[
a_{r+1}=Qa_r,
\qquad b_{r+1,i}=Q_i a_r+Qb_{ri}
\]

gives

\[
f^{(r)}_{\theta_i}=B(s_i^Ta_r+p^Tb_{ri}).
\]

The prototype finite-differences orders zero through three, so the test covers
the direct term and specifically \(f_{ttt\theta_i}\).  **Closed.**

### P0.D — incomplete cusp Jacobian

**Attack.**  Solving `f_t=f_tt=f_ttt=0` with a Jacobian that stops at
`f_ttt` or omits `f_ttt,theta` can converge numerically while providing no
cusp nondegeneracy or correct Newton derivative.

**Resolution.**  The full matrix is

\[
\begin{pmatrix}
f_{tt}&f_{t\theta_1}&f_{t\theta_2}\\
f_{ttt}&f_{tt\theta_1}&f_{tt\theta_2}\\
f_{tttt}&f_{ttt\theta_1}&f_{ttt\theta_2}
\end{pmatrix}.
\]

The small explicit-CSR prototype compares this matrix against an independent
centred difference of the complete map `H=(f_t,f_tt,f_ttt)`.  The maximum
absolute discrepancy at the deterministic test point is `4.02e-13`.
**Closed.**

### P0.E — false projected-rank certificate from an arbitrary chart

**Attack.**  A two-column raw chart can create arbitrary singular values and
could accidentally align with a weak direction.  The historical fixed-first-
weight chart is also undesirable because the early event mass is already the
tightest margin.

**Resolution.**  The design freezes the Euclidean physical metric, constructs
the full three-dimensional Helmert tangent basis, and selects the two nonzero
right-singular response directions from the pinned `B=0` cusp.  The resulting
matrix `P` is unit-budget and orthonormal.  Its source response has singular
values `29.4585` and `4.96689`, so this is a canonical, well-conditioned
two-plane determined before positive-`B` allocation discovery.  Positive-`B`
rank must still pass a new held-out floor; the `B=0` value is not substituted
for it.  **Closed.**

### P0.F — wrong fold-branch sign or only one outgoing branch

**Attack.**  Starting pseudo-arclength exactly at the cusp gives a tangent in
the time direction and may cause both nominal branches to follow the same
half.  A sign error in the normal form can also put both predictors outside
the three-root wedge.

**Resolution.**  Expanding the stationary equation gives

\[
R_1\eta=f_{tttt}\tau^3/3,
\qquad R_2\eta=-f_{tttt}\tau^2/2
\]

to leading order.  The protocol seeds separately at `tau=+0.10` and
`tau=-0.10`, corrects at fixed time, then orients pseudo-arclength tangents
continuously.  Both halves must reach the same frozen distance and retain a
remote pair.  **Closed.**

## 4. P1 protocol attacks

### P1.A — discovery leaking into confirmation

**Attack.**  Repeatedly changing weights after seeing meshes 113/129, parity,
or enlarged boxes would turn the cusp and phase map into another
result-informed fine-grid scan.

**Resolution.**  Stage A is restricted to meshes 65 and 97.  Before any other
mesh, a new hash-pinned manifest must freeze the physical family, basis,
representatives, branch nodes, matrix, thresholds, tolerances, and negative
claim flags.  Fine-grid cusp re-solving is permitted only for the same
equations; physical weights of phase representatives cannot move.  **Closed.**

### P1.B — unbounded rescue search

**Attack.**  “Find one-, two-, and three-mode examples” without a search bound
can consume arbitrary scans and guarantees a selected-looking result.

**Resolution.**  The design permits exactly 32 radial controls around the
mesh-97 cusp, screens only mesh 65, advances at most three candidates per
target count to mesh 97, and uses a deterministic threshold-normalized score.
Absence is `HOLD`; the radius set cannot expand.  **Closed.**

### P1.C — unspecified finite-difference and fold-node choices

**Attack.**  An implementation could tune finite-difference steps until the
analytic jets appear correct or choose the most favorable fold nodes after
seeing confirmation meshes.

**Resolution.**  The design now fixes two allocation and two relative-time
steps, requires decreasing error before the roundoff floor, and chooses three
comparison nodes per branch by signed time offsets `0.25,0.50,0.75` with
deterministic tie-breaks.  These were repairs made during this attack before
any allocation result was run.  **Closed.**

### P1.D — two odd meshes mislabeled as convergence

**Attack.**  The current 113/129 pair shares odd alignment, box, SG flux, and
contact quadrature.  It cannot establish alignment robustness or a stable
continuum trend.

**Resolution.**  The confirmation design adds `E128` and finer `O161`, keeps
the odd sequence 113/129/161, requires identical topology and strictly
decreasing successive odd-mesh differences, and retains raw differences
rather than inferring an order from two points.  **Closed as an empirical
convergence design.**  It remains explicitly short of a PDE theorem.

### P1.E — box enlargement can hide cancelling boundary errors

**Attack.**  Enlarging both nonperiodic coordinates once cannot distinguish
midpoint from relative-coordinate truncation and can hide cancellation.

**Resolution.**  The matrix separately enlarges the midpoint interval, the
relative-parallel interval, and both, with anisotropic cell counts chosen to
preserve approximate spacings.  Cusp jets, fold nodes, roots, masses, and
survival are required on every row.  **Closed as a bounded truncation
diagnostic.**

### P1.F — Boolean threshold passes without uncertainty headroom

**Attack.**  The known positive-`B` feasibility values put the smallest event
mass near `0.005`; a value can cross the Boolean floor while being unresolved
under mesh or box change.

**Resolution.**  For every promoted scalar, the design uses the conservative
value over the matrix and requires the empirical error to be no more than both
an absolute cap and one quarter of the remaining scientific margin.  A
near-threshold event mass therefore fails even if its point value is above
`0.005`.  **Closed.**

### P1.G — local cusp mistaken for global phase structure

**Attack.**  A cusp creates or removes only one local max--min pair.  It does
not prove trimodality without a remote pair, and a sign screen on `[0.5,35]`
does not establish an exact global modal count.

**Resolution.**  The design separately gates a remote simple pair, evaluates
full representative laws and event partitions, and uses “retained-window
maximum count” rather than global exact-count language.  The normal-form
discriminant is plotting guidance only.  **Closed.**

## 5. P2 attacks and repairs

1. The baseline box was initially labeled `B0`, which could be confused with
   zero installed budget.  It is now `Base`.  **Closed.**
2. “Visible convergence” was initially qualitative.  It now includes an
   explicit odd-mesh decreasing-difference gate plus absolute and margin-aware
   caps.  **Closed.**
3. Candidate endpoint signs were initially included in an undefined mixed-
   units score.  They are now eligibility conditions; the score uses only
   threshold-normalized continuous margins.  **Closed.**

## 6. Executed checks

From the repository virtual environment:

```text
python -m ruff format --check \
  code/allocation_cusp_algebra_prototype.py \
  code/test_allocation_cusp_algebra_prototype.py
2 files already formatted

python -m ruff check <the same two files>
All checks passed!

python -m pytest -q code/test_allocation_cusp_algebra_prototype.py
.... [100%]

python code/allocation_cusp_algebra_prototype.py
maximum cusp-Jacobian finite-difference error 4.016272991264058e-13
projected rank 2
```

The tests are deliberately small and independent of the matrix-free broad
producer.  They validate the equations, not the future physical result.

## 7. Remaining execution gates, not closed scientific claims

The design is ready to be implemented as a **new** chain, but the following
remain genuine work:

1. no broad-family allocation-cusp producer or manifest exists yet;
2. the current cubic builder must be generalized and independently tested for
   the anisotropic box matrix;
3. no Stage-A cusp, folds, remote pair, or representatives have been run;
4. no Stage-B parity, finer-mesh, or box value exists;
5. the event-mass margin may fail, and the protocol intentionally forbids a
   fine-grid rescue refit;
6. the 32-point discovery can miss a phase region; that means the bounded
   promotion attempt is inconclusive, not that the region is globally absent;
7. empirical mesh/box stability is not an interval continuum proof; and
8. the independent unbounded killed-process solver required by Round 33 is a
   later, separately frozen validation stage.

The anticipated resource risk is substantial but bounded: mesh 161 and the
anisotropic combined box contain millions of states, and cusp/fold tangents
triple or multiply the state payload.  The future implementation must stream
sequentially and preflight memory; reducing a confirmation mesh after seeing
results would violate the design.

## 8. Final verdict

The design now supplies the exact fixed-`B` two-direction allocation
sensitivities, direct observable derivatives, complete cusp map and Jacobian,
projected-rank metric, fold predictors/continuation equations, bounded
discovery, no-refit freeze, parity/box matrix, and margin-aware gates requested
by Round 33.

Therefore the correct status is:

- **PASS-DESIGN:** algebra and protocol are internally coherent and pass the
  explicit-CSR finite-difference attack;
- **HOLD-SCIENCE:** no physical positive-`B` allocation cusp, fold branch,
  representative phase region, convergence result, independent-solver result,
  or PRR gate is claimed.

That distinction must remain visible when the parent workflow integrates this
stage into the larger manuscript program.
