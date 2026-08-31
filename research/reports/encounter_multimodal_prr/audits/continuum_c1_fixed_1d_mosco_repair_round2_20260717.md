# Continuum C1 fixed-1D ideal SG/Mosco repair: round 2

Date: 2026-07-17

Status: **LOCAL HASH-SPECIFIC ADVERSARIAL PASS / IDEAL FIXED-1D FREE FORM ONLY / COMPLETE C1 HOLD / C0-V1 STALE**

## Exact final bytes

- repaired Mosco candidate SHA-256:
  `11a3015cbaa38cd58d763052adf3858ad055f121cc83669aaeeb462252d35e79`;
- strict-continuum program SHA-256:
  `52c1b354be3fac0b1674ce0c0c4c85f38b76545bae1562ee071f20edc7689e0a`;
- v2 fixture generator SHA-256:
  `e32c32c89db92f4242b5db287300eb6e996b317d9ef0f8e32ae2b57df4facf45`;
- static/recomputation tests SHA-256:
  `1dec91277b94788fc67efac121d41eb012ec01333e50f2c455bf98b51a34f92d`;
- adversarial tests SHA-256:
  `3757de74ba3efaccd2d81884fb1b82a780ddaef491f9591e3507bb823aa5f951`;
- generated v2 artifact SHA-256:
  `19a97c14facda287c9ae37bf81c19fec5a2cbedd933124e8b9b2088e9feb724c`;
- immutable v1 artifact SHA-256:
  `d5acdad670656cccc974d40f56bac33292a1ae7a462acedb7588eb572147b9cc`;
- current C0-v1 staleness sentinel SHA-256:
  `e8388fca8888c35d18a154bcba555117366b4adee3e74eb9908a8108ee8799e9`.

The read-only audit agents did not edit the reviewed bytes and did not access
controls, result-bearing positive-budget data, or the network.  Because they
ran inside this local continuation, this record is an adversarial development
audit, not an external referee acceptance or complete-C1 promotion.

## Attack and repair chronology

The first mathematical attacks found one conditional P0 and several P1/P2
gaps in the earlier proof skeleton:

1. a complex-bilinear reading would make the quadratic form nonpositive;
2. the liminf paragraph assumed a bounded-energy sequence instead of starting
   from an arbitrary weakly convergent sequence and a liminf subsequence;
3. weak-limit identification and the varying-space convergence convention
   were unstated;
4. recovery invoked density without an explicit double-index diagonal;
5. `P_h` ambiguously denoted either a literal weighted average or the exact
   adjoint; and
6. the generic boundary energy defect was at risk of being misreported as
   second order.

The final proof bytes repair all six points.  They work over real Hilbert
spaces, specify the sesquilinear complexification, define strong and weak
convergence through `J_h`, distinguish

\[
 (P_hu)_i=m_i^{-1}\int_{C_i}u\pi,
 \qquad
 (A_hu)_i=M_i^{-1}\int_{C_i}u\pi,
 \qquad
 (S_hu)_i=u(x_i),
\]

and use `S_h` only on smooth recovery functions.  They also give an arbitrary-
sequence liminf argument, an explicit `k(h)` recovery diagonal, and distinct
operator symbols `mathcal L,mathcal L_h` in the variational resolvent step.

The final mathematical delta audit reports `P0=0`, `P1=0`, and `P2=0` for the
scoped ideal analytic, fixed-box, one-dimensional, free, cell-centred
reflecting OU form.  It verifies the exact map identities, uniform mass and
edge comparisons, interpolation inequality, lower-semicontinuity argument,
generic first-order boundary term, recovery sequence, and direct generalized
strong-resolvent minimizer argument.

## Code attack that prevented a false production bridge

The first v2 code re-audit returned **HOLD (P1)**.  The generator checked the
production intervals against the raw ungauged mass and conductance and then
used `g_h` times those quantities in the ideal form, while the artifact claimed
that the ideal form values were contained.  At 17 cells,
`g_h=3.98941852425341`; the raw conductance is contained but the gauge-scaled
conductance is not.

The repair does not widen or reinterpret the production intervals.  It records
four separate per-grid booleans:

- raw stationary mass containment: `true` on all seven grids;
- raw conductance containment: `true` on all seven grids;
- gauge-fixed stationary mass containment: `false` on all seven grids; and
- gauge-fixed conductance containment: `false` on all seven grids.

Accordingly,
`gauged_ideal_form_values_contained_in_production_outward_intervals=false` and
`production_gauge_linkage_proved=false`.  A later C1/C4 layer must apply the
same gauge with outward enclosure and charge the resulting width to `E_eval`.
Raw containment is no longer presented as a theorem-to-production bridge.

The same attack found that the alternating-vector `I_h-J_h` value was merely
serialized as a literal.  The repaired generator now reconstructs its jumps,
conductance, energy, and two exact half-cell ramp integrals with `Fraction`
arithmetic, asserts the identity internally, and the static test independently
recomputes it from the serialized values.

## Neutral v2 numerical findings

The seven fixed grids are `N=17,33,65,129,257,513,1025`.  The last-pair
observed orders are:

- exact-adjoint map-ratio supremum error: `2.0006568006409537`;
- cell-mass-ratio supremum error: `1.9899162478893226`;
- ideal edge/interpolant-ratio supremum error: `1.9821041802837749`; and
- full-cell density-ratio supremum error: `1.0906102408239533`.

At 1025 cells the full-cell density-ratio error remains
`0.13074234611923943`.  The production-centre detailed-balance residual and
recursive reversible-mass shape drift are nonzero (about `4.664e-16` and
`4.063e-15`), so independently selected binary64 centres are not treated as an
exact reversible `h -> 0` sequence.

The exact flat-density sentinels establish:

\[
 E_h[x]=1-h/2,
 \qquad
 E_h[x^2]=4/3-2h+(2/3)h^2,
\]

and, for `N=4`, `h=1/2`, and `v=(0,1,0,1)`,

\[
 \mathfrak a_h(v,v)=3,
 \qquad
 \|I_hv-J_hv\|^2=1/16.
\]

These checks support the local consistency lemmas; they do not prove Mosco
convergence by finite-table extrapolation.

## Executed checks

- generator run: PASS, with two successive regenerations reproducing artifact
  SHA-256 `19a97c14facda287c9ae37bf81c19fec5a2cbedd933124e8b9b2088e9feb724c`;
- `py_compile`: PASS;
- Ruff on the C1 generator and both C1 test modules: PASS;
- C1 static/recomputation tests: 15/15 PASS;
- C1 adversarial tests: 8/8 PASS;
- combined C1 suite: 23/23 PASS;
- final read-only code re-audit: 22/22 formula/artifact-focused tests PASS,
  excluding only the living-note string-coupling test;
- current C0-v1 staleness sentinel: 1/1 PASS;
- theorem-first/living scope consistency: 9/9 PASS; and
- fail-closed theorem-first compiler: PASS, reproducing the frozen seven-page
  main SHA-256 `577d2d4b494633a3e009f13fbd581a9c889d7c84fd11c18e5b3367a6e4b1a42e`
  and 23-page Supplement SHA-256
  `70de25968298d58222bbab10639a2253067f5c01d4d6462d743e3e6eca5790fb`.

The historical C0-v1 candidate and its verifier are intentionally unchanged.
That candidate pins an older hash of `notes/continuum_research_program_v2.md`.
The living program now contains the exact-adjoint map and gauge-bridge repairs,
so the old 18-test C0 suite no longer has a current all-green baseline: the
combined C0+C1 run gives 36 PASS and five C0 failures, all rooted in
`HOLD_C0_CONTRACT_SOURCES`.  This is the intended fail-closed result, not a
reason to overwrite the v1 source hash.  A versioned C0-v2 contract is the next
repair.

## Accepted scope and nonclaims

This round locally clears only the ideal analytic, fixed-box, one-dimensional,
free, cell-centred reflecting OU generalized-Mosco sublemma and its direct
generalized strong-resolvent consequence.  The candidate note remains
candidate-labelled so these exact audited bytes are not rewritten merely to
self-promote their status.

The round does **not** establish:

- a production-centre convergence theorem or gauge-applied interval enclosure;
- the relative OU axis, periodic axis, tensorization, or vertex-dual alignment;
- sharp-contact killing or controlled forms;
- the varying-space functional-calculus bridge for
  `mathcal L_h^r exp(-t mathcal L_h)`, `r=0,1,2`;
- a quantitative C2 rate, C3 box exhaustion, or componentwise root transfer;
- F0, F1, F3, positive-budget science, or release eligibility; or
- a current complete-C0 contract.

Complete C1 and PRR submission remain **HOLD**.  The next strict-continuum
sequence is: create and audit C0-v2 with the repaired maps and gauge boundary;
prove the relative/periodic/tensor/vertex free-form extensions; add
sharp-contact killing consistency; then supply a self-contained functional-
calculus bridge before any quantitative C2 or topology-transfer claim.
