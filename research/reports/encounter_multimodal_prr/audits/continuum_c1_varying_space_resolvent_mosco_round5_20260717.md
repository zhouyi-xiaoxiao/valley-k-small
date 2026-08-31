# Varying-space reconstructed-resolvent-to-Mosco theorem: round 5

Date: 2026-07-17

Status: **LOCAL HASH-SPECIFIC ABSTRACT THEOREM-CANDIDATE PASS / P0=0 / P1=0 / P2=0 / FREE-TENSOR MOSCO IMPLICATION CLOSED / MODEL-SPECIFIC C1 HOLD / C2-C3 HOLD / PRR RELEASE HOLD**

## Decision

The exact proof-candidate bytes below give a self-contained varying-space
theorem:

> If `P_h=J_h^*`, the map norms are uniformly bounded,
> `||P_hJ_h-I|| -> 0`, and one reconstructed resolvent converges strongly,
> then the associated nonnegative closed forms generalized-Mosco converge in
> the strong/weak convention defined through `J_h`.

This closes the abstract gap deliberately left in Section 5 of the Round-4
free-form note.  In particular, once the one-axis geometric/refinement
premises are accepted, its direct free-tensor strong-resolvent construction
can be promoted to a free-tensor Mosco conclusion without invoking an
unchecked external tensorization or resolvent-equivalence citation.  The same
bytes then give the conditional bounded-killing perturbation.

This is not complete C1.  The real refinement source, accepted axis estimates,
exact control-specific physical-volume averages, production global gauge and
application enclosure, quantitative rate, box exhaustion, and root transfer
remain open.  The review is a local adversarial development audit tied to the
hash below, not external peer review or PRR acceptance.

## Exact audited bytes

- theorem candidate:
  `notes/continuum_c1_varying_space_resolvent_mosco_candidate.md`;
- line count: 571;
- byte count: 14,490;
- SHA-256:
  `0b9728535ed0216bc00d5ccb911575dd30bb531422130b2f7e2502a046f134f1`;
- encoding check: ASCII text, with no binary or generated-result payload.

The predecessor Round-4 note remains unchanged at SHA-256
`17b987d5090618e5346f81217afed7e57daccf878d4b93b8402724b3e002a562`.
The verified Round-4 handoff archive is also unchanged; this Round-5 note was
created afterward and is intentionally not represented as a member of that
archive.

## Proof spine checked

### Exact unitarization

With

\[
 G_h=P_hJ_h=J_h^*J_h,
 \qquad
 U_h=J_hG_h^{-1/2},
\]

the norm condition gives `G_h -> I` and makes `U_h` an exact isometry for all
sufficiently fine meshes.  Since `J_h=U_hG_h^{1/2}`, the `J_h` and `U_h`
strong/weak convergence conventions agree on every convergent sequence.  No
near-isometry is silently treated as unitary.

The review checked that the displayed expansion comparing
`U_hR_hU_h^*` with `J_hR_hP_h` is algebraically exact and does not require
`G_h` to commute with the resolvent.

### All resolvent shifts

On the moving range and its orthogonal complement, the function

\[
 g_\beta(x)=\frac{x}{1+(\beta-\eta)x},
 \qquad g_\beta(0)=0,
\]

maps the compressed `eta`-resolvent exactly to the compressed
`beta`-resolvent.  Its denominator stays positive even when `beta<eta`.
Strong polynomial approximation therefore transfers the one assumed shift to
every positive shift without assuming that the moving ranges are dense.

### Liminf

For a weakly convergent sequence, the proof inserts
`f=(L+beta)w`, `w in D(L)`, into the exact discrete resolvent minimization.
After taking the mesh liminf and then `beta` down to zero, it obtains

\[
 \liminf_h a_h(v_h,v_h)
 \ge 2\operatorname{Re}\langle Lw,v\rangle-a(w,w).
\]

The self-contained dual identity

\[
 a(v,v)=\sup_{w\in D(L)}
 \bigl(2\operatorname{Re}\langle Lw,v\rangle-a(w,w)\bigr)
\]

was checked with spectral truncations.  It handles a nontrivial kernel and
gives `+infinity` for `v` outside the form domain; no finite-energy assumption
is smuggled into the liminf statement.

### Recovery

For each positive `beta`, the proof takes

\[
 v_h^\beta=\beta(L_h+\beta)^{-1}U_h^*v.
\]

Exact isometry gives the square-compression identity, and the resolvent
equation gives an exact energy formula in terms of the compressed resolvent
and its square.  Fixed-`beta` strong and energy convergence followed by
`beta -> infinity` and a diagonal produces form-energy equality for
`v in D(a)`.  Outside the form domain the same diagonal supplies the required
strong approximation while the extended-energy upper bound is automatic.

This construction itself proves the needed asymptotic approximation of the
moving ranges.  It does not assume their density in advance.

## Tensor and killing attack chronology

The first exact-byte tensor/killing audit found `P0=0`, `P1=0`, `P2=3`:

1. the asynchronously refined three-axis limit and uniform product bounds
   needed to be explicit;
2. the tensor identities needed to be restricted to completed Hilbert tensor
   products and the ideal product-mass/global-gauge hypothesis; and
3. the convergence-in-measure multiplier step needed the fixed measure,
   common bound, and strong square-root-multiplier line written out.

The final bytes repair all three:

- `h=(h_z,h_r,h_y)` is a directed multi-index with
  `max(h_z,h_r,h_y)->0`, and the algebraic-tensor density argument carries an
  explicit uniform product-map bound and Laplace dominator;
- `m_ijk=m_i^z m_j^r m_k^y` and the tensor adjoint/factorization are stated
  only under the ideal product-mass/global-gauge premise, expressly excluding
  independently rounded production gauges; and
- on `dmu=pi dx`, `0<=K_h,V<=M`, strong multiplication by `sqrt(K_h)` on
  every fixed `L2(mu)` test is proved before the weak-product/lower-
  semicontinuity step.  The recovery remainder is separately justified under
  the finite measure `|v|^2 dmu`.

The final tensor/killing delta review on the exact hash above reports
`P0=0`, `P1=0`, `P2=0`.

## Independent final reviews

Three read-only attacks covered disjoint emphases on the final 571-line
bytes:

- a main-theorem review of Sections 1--5 returned
  `P0=0`, `P1=0`, `P2=0`;
- a separate line-by-line attack on unitarization, all shifts, signs, spectral
  duality, kernels, non-dense moving ranges, and recovery returned
  `P0=0`, `P1=0`, `P2=0`; and
- the repaired tensor/killing review returned
  `P0=0`, `P1=0`, `P2=0`.

No reviewer edited the bytes.  The audits used only the named theory notes,
no network, and no result, control, scratch, production-centre, or positive-
budget payload.

Two optional generality comments were not graded as P2: finitely many initial
meshes with `delta_h>=1` may be assigned arbitrary recovery values, and a
fully abstract directed-set version may state a countable cofinal threshold
base.  The declared maximum-mesh refinement families already have the
sequential/cofinal structure used by the diagonal proof.

## Retained nonclaims and next model-specific route

This round closes only an abstract implication.  It does **not** establish:

- that the twelve finite anchors are refinement sequences;
- final acceptance of every relative, vertex-dual, or periodic axis estimate;
- exact control-specific physical-volume contact averages;
- a production raw-to-global-gauged or ideal-to-evaluator enclosure;
- a cut-cell, spatial, or evaluator rate;
- C2, C3, continuum root margins, or root transfer;
- positive-budget F0/F1/F3 science; or
- complete C0/C1, release, submission, or journal acceptance.

The next result-blind step is now model-specific rather than abstract:

1. freeze genuine admissible refinement sequences for every declared
   alignment;
2. bind exact physical-volume killing averages to the same cells and global
   ideal gauge;
3. prove the outward production application enclosure without using result-
   bearing payloads; and
4. only then select a quantitative C2 route, keeping cut-cell, free-form, and
   evaluator errors separate.

