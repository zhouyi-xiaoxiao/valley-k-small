# Round 02 reviewer B — Green, Woodbury, resolvent, and zero mode

Date: 2026-07-11  
Verdict: **needs revision; no B0, one B1, three B2 findings**  
Audited Git base: `3531353a515160b09899199a9257e7455a654b22`  
Working-tree snapshot hashes:

- `packages/vkcore/src/vkcore/encounter.py`:
  `3df35e8e26443c6035d9a4e0a345087ad56eb9b5b829435b2f8fd31ae6063dfd`;
- `manuscript/encounter_modality_jcp.tex`:
  `6e893425fbee36a57d11411eb13983ba860d135972222cc8b7876b3598d9e547`;
- `notes/continuum_multid_theory.md`:
  `49f67b5fd746190245a219d388533cda4f34864570081e2568402ca18bd07518`;
- `tests/test_encounter_green_ctmc.py`:
  `df366668d9ce1e3a027b9f4963ebfd48e32960b1b18399ab06ba670c53a4f707`;
- `artifacts/data/gig_fold_summary.json`:
  `ecac31a16c4f6f98e30c8e8962fd5660b19efb90373b975b7e75cf28a315d125`.

The audited files were untracked in an already dirty working tree, so the Git
hash is a base commit rather than a complete immutable snapshot. Line anchors
refer to the hashed working-tree files above. I did not read or rely on the
other Round 02 review while forming this report, and I changed no scientific
source, artifact, notebook, pipeline, manifest, or other audit file.

## Executive assessment

The finite-matrix core is algebraically sound. An independent nonsymmetric,
complex-frequency test confirmed the **minus** sign in Woodbury, the order of
the noncommuting `G K` factors, and the channel-transform formula. Direct
quadrature confirmed the zero-frequency channel probabilities and first two
defective moments. Both the generic reaction-rate Jacobian and the actual
physical-fold sensitivity include the derivative of the killing observable;
the archived splitting probabilities were reproduced exactly.

The main revision is at the continuum interface. The stated model allows a
nonnegative killing multiplier, but the displayed theorem uses
`K^{-1}` without defining the restricted space on which `K` is boundedly
invertible. The finite code and Lean algebra already use the stronger,
inverse-free `(I + G K)` form, including at a zero channel rate. The manuscript
should use that form or state the missing strict-positivity/support hypothesis.

Two validation obligations also remain. First, the text correctly warns that a
restricted determinant root can be dark or numerator-cancelled, but no test or
artifact exercises either case and the production Green API rejects the left
half-plane where the finite killed poles lie. Second, the free-Green subtraction
loses channel accuracy near the reflecting zero mode while still returning a
result; callers receive diagnostics but no fail-closed threshold or automatic
switch to the stable killed solve.

## Findings

### B1-01 — The continuum theorem requires `K^{-1}`, but the declared model only assumes `K >= 0`

**Anchors**

- `manuscript/encounter_modality_jcp.tex:263-270` permits spatial rates
  `kappa_j >= 0` and indicator-supported patches.
- `manuscript/encounter_modality_jcp.tex:396-421` says that `Gamma` restricts to
  the “reactive tube” and then uses
  `(K^{-1}+G)^{-1}` in both the resolvent and support-density formulas.
- The same mismatch appears in
  `notes/continuum_multid_theory.md:273-324`.
- By contrast, `encounter.py:838-846,911-928` implements
  `M=I+G K` and never inverts `K`; `tests/test_encounter_green_ctmc.py:144-166`
  explicitly passes a zero channel rate.
- The Lean statement is also inverse-free:
  `FormalLean/Encounter.lean:203-238` proves the two-hotspot solve for
  `(I+G K)x=y`, including zero values of a rate when the renewal determinant is
  nonzero.

“Whenever the stated inverses exist” makes the displayed identity conditional,
but the required space and hypothesis are not stated. If `Gamma` restricts to
the whole contact tube, `K` is zero outside the catalytic patches. Even if
`Gamma` is intended to restrict to the essential support of `K`, the declared
`kappa_j >= 0` does not imply a positive essential lower bound, so multiplication
by `K^{-1}` need not be bounded.

I tested a seeded seven-state nonsymmetric generator at
`s=0.37+0.41j`, with three selected hotspots and rates `(0,0.7,1.9)`.
The inverse-free formula had full-resolvent error `1.67e-16` and channel error
`5.55e-17`; `K` had rank two and `inv(K)` raised `LinAlgError`. With all rates
positive, the displayed inverse-`K` formula and support-density formula agreed
with the direct solve to `8.78e-17` and `9.86e-17`, respectively. Thus the sign
is right, but the theorem as connected to the allowed model class is incomplete.

**Required resolution**

State explicitly that the support Hilbert space is chosen so that `K` is
boundedly invertible, with a positive essential lower bound, **or** replace the
displayed form by the inverse-free identity

\[
R=R_0-R_0\Gamma^*K(I+GK)^{-1}\Gamma R_0,
\qquad
y=K(I+GK)^{-1}u=(I+KG)^{-1}Ku.
\]

For finite hotspots, use `det(I+G K)` as the primary secular determinant and
state its scaling relation to `det(K^{-1}+G)` only when every rate is nonzero.
This would align the continuum text, finite code, zero-rate test, and Lean
theorem without changing the numerical artifacts.

### B2-01 — Pole, numerator, residue, and dark-mode warnings are correct but untested and unavailable through the Green API

**Anchors**

- `manuscript/encounter_modality_jcp.tex:447-462` introduces the restricted
  determinant and correctly warns about numerator cancellation, zero observable
  residues, and modes dark to `U`.
- `manuscript/encounter_modality_jcp.tex:1217-1221` says that an observable fold
  depends on both poles and residues.
- `encounter.py:762-777,883-897` rejects every `s` with negative real part.
  Finite killed-generator poles lie in that left half-plane.
- `tests/test_encounter_green_ctmc.py:39-166` checks positive-real and one
  positive-real complex frequency, direct Woodbury agreement, derivatives, and
  a zero rate, but contains no determinant-root, eigenprojection, numerator,
  residue, cancellation, or dark-mode case. No dedicated Green artifact records
  those checks.

I built an example using the production constructors: two symmetric two-site
walkers, both co-location sites reactive, and rates `(0.5,0.5)`. The killed
eigenvalues are

`(-4.26556444, -2.5, -2.0, -0.23443556)`.

At `lambda=-2.5`, `det(I+G(lambda)K)=0`, but the two channel residues for an
initial mass at `(0,0)` are `(0.25,-0.25)`. Their total residue is exactly zero.
Numerically,

| epsilon | `epsilon * channel transform` | `epsilon * total transform` |
|---:|---:|---:|
| `1e-3` | `(0.25003118,-0.24996882)` | `6.24e-5` |
| `1e-6` | `(0.25000003,-0.24999997)` | `6.25e-8` |
| `1e-9` | `(0.24999998,-0.24999998)` | `6.25e-11` |

The same production model has the dark vector `(0,1,-1,0)`: `U^T v=0`, and
both the free and killed generators retain eigenvalue `-2` exactly. The API
rejects evaluation at `-2.499` before either phenomenon can be audited.

These counterexamples validate the manuscript's warning; they do not contradict
it. The gap is evidence coverage. Before presenting pole/residue analysis as a
validated bridge, add a finite-dimensional eigenprojection or meromorphic
continuation helper and regression tests for (i) a coupled determinant root,
(ii) source- or observable-numerator cancellation, (iii) channel residues that
cancel in the total flux, and (iv) a dark full-generator eigenmode. If this is
left for future work, say explicitly that current code validates the
right-half-plane resolvent identity only and that no numerical conclusion in
the paper was inferred from a secular root.

### B2-02 — The free-Green path is not fail-closed near the reflecting zero mode

**Anchors**

- `manuscript/encounter_modality_jcp.tex:464-472` correctly routes exactly
  `s=0` to the killed solve.
- `encounter.py:793-828` rejects an operator only at an SVD-based numerical
  singularity threshold.
- `encounter.py:883-959` returns free-Green results at any accepted `Re(s)>0`,
  even when its own killed-resolvent equation error is large.
- The smallest nonzero test frequency is `s=0.03`
  (`tests/test_encounter_green_ctmc.py:39-65`); there is no `s downarrow 0`
  conditioning sweep.

For the test file's own irreducible `3x3` two-channel model, I compared the
free-Green channel transform with the direct killed solve:

| `s` | max channel abs. error | max channel relative error | killed equation error |
|---:|---:|---:|---:|
| `1e-8` | `2.99e-10` | `9.59e-10` | `5.34e-9` |
| `1e-12` | `6.34e-7` | `2.04e-6` | `5.75e-5` |
| `1e-14` | `2.51e-4` | `8.07e-4` | `6.66e-3` |

At `1e-14` the function still returns channel values; it rejects only at about
`1e-15` for this case. The total happens to remain accurate because the two
channel errors have opposite sign, which makes total-mass checking insufficient.
No headline artifact was found to depend on these tiny positive frequencies,
and the direct `s=0` route is stable, so this is not a B0.

Add a conditioning sweep and a declared accuracy gate. The Green routine should
either raise when the reconstructed resolvent/channel residual exceeds a
tolerance, automatically switch to a direct killed solve below a justified
cutoff, or expose a zero-mode-separated formulation that avoids subtracting
divergent terms. Tests must check each channel, not only their sum.

### B2-03 — The full `K`-dependent observable sensitivity is implemented but not stated as an equation

**Anchors**

- `manuscript/encounter_modality_jcp.tex:477-484` gives only
  `R_theta=R T_theta R` and says in prose that extra observable terms are needed
  when `K` depends on the parameter.
- `encounter.py:1009-1061` correctly implements
  `dF/dk_j=(alpha R u_j)[e_j^T-u_j^T R B]`.
- The physical fold explicitly changes both the killed operator and observable
  (`manuscript:699-714`); `validate_gig_fold.py:335-353` includes the state,
  generator, and observable contributions.
- The finite-radius fold also includes `k_theta` in
  `validate_2d_matched_fold.py:270-293`.

The missing term is not cosmetic. In my random zero-rate directional test, the
full derivative of the formerly zero channel was `0.14457867`; retaining only
the resolvent derivative gave exactly zero for that component. The implemented
Jacobian agreed with centered finite differences at positive rates to
`4.26e-11`, and with a one-sided derivative at a zero rate to `5.05e-9`.

For the archived physical fold, an independent sparse solve reproduced the
splitting vector
`(8.945768022901476e-6, 0.9999910542319812)` exactly and summed to
`1+4e-15`. Centered finite differences of `f_t` at fixed fold time converged to
the archived `f_{t theta}=-9.4584861967e-10`; relative errors were
`1.67e-7, 1.48e-8, 1.85e-9` for steps `1e-3, 3e-4, 1e-4`.

Add the full fixed-support formula

\[
\partial_\theta[\alpha R U K]
=\alpha_\theta RUK+\alpha R T_\theta RUK
 +\alpha R U_\theta K+\alpha R U K_\theta,
\]

with terms removed only under explicit fixed-`alpha`/fixed-`U` assumptions.
State separately that moving a sharp patch changes `U` and need not be a smooth
parameter on a fixed finite grid. This makes the manuscript's “exact
sensitivity” claim match the implementation that already passes.

## Independent checks that passed

1. **Woodbury sign and noncommuting order.** For the seeded nonsymmetric
   seven-state case at complex `s`, the production-order formula agreed with the
   direct killed resolvent to `1.67e-16`. Reversing the Woodbury correction to a
   plus sign produced error `0.7144`. The source's minus sign and `G K` order are
   correct.
2. **Restricted support density for invertible `K`.** With positive unequal
   rates, `(K^{-1}+G)^{-1}u` agreed with `K U^T R q` to `9.86e-17`.
3. **Zero-frequency channel moments.** On the random transient case, direct
   matrix powers gave channel mass, first moment, and second moment agreeing
   with independent `quad_vec` integration to `4.44e-16`, `1.78e-15`, and
   `1.24e-14`. The channel masses were
   `(0,0.25310456,0.74689544)` and summed to `1+2.2e-16`.
4. **Zero channel rates.** The inverse-free finite formula remained well posed
   with one rate exactly zero. The existing zero-rate and zero-frequency tests
   are scientifically appropriate for the globally transient case.
5. **Splitting probability and mass closure.** The physical-fold splitting
   values in `gig_fold_summary.json:104-122` were independently reproduced;
   their extreme imbalance is disclosed in the manuscript at `737-741` and
   `1299-1301`.
6. **`K`-dependent sensitivity.** Both the generic finite-matrix Jacobian and
   the actual fold transversality converged under independent parameter
   perturbations. The potentially dangerous direct derivative of the observable
   is present in code.
7. **Continuum scope.** The manuscript limits the volume identity to operator
   hypotheses and explicitly separates Robin trace spaces
   (`manuscript:424-429`), states that implemented validation is finite
   dimensional (`1297-1298`), and does not infer density modes directly from
   determinant roots (`459-462`). Those scope statements should remain.
8. **Current focused tests.** The command below completed `17 passed`:

   ```text
   uv run --no-sync pytest -q \
     tests/test_encounter_green_ctmc.py \
     tests/test_encounter_green_uniformization.py \
     tests/test_encounter.py
   ```

## Commands and reproducibility record

All diagnostics were read-only shell or here-document calculations; no helper
script or artifact was written.

```text
rg -n -i -e woodbury -e green -e resolvent -e zero.frequency \
  -e moment -e pole -e residue -e numerator -e splitting -e sensitivity \
  manuscript/ notes/ packages/vkcore/src/vkcore/encounter.py \
  code/ tests/test_encounter*.py

uv run --no-sync pytest -q tests/test_encounter_green_ctmc.py \
  tests/test_encounter_green_uniformization.py tests/test_encounter.py
```

The random-matrix command used `numpy.random.default_rng(20260711)`, a dense
seven-state row generator with strictly positive off-diagonal rates, selectors
`U=I[:,(0,3,6)]`, and the frequencies/rates reported above. It evaluated both
the direct inverse and the formulas

```python
R0 = inv(s*I - L0)
G = U.T @ R0 @ U
M = I_hotspot + G @ K
Rwb = R0 - R0 @ U @ K @ solve(M, U.T @ R0)
Fwb = alpha @ R0 @ U @ K @ inv(M)
```

against `inv(s*I-T)` and repeated the calculation with the deliberately wrong
plus sign. Zero-frequency moments were independently integrated with
`scipy.integrate.quad_vec` over `[0,infinity)`.

The pole/cancellation command used only production constructors:

```python
w = reflecting_ctmc_generator(2, 2.0)
m = build_ctmc_catalytic_encounter(
    w, w, catalytic_sites=(0, 1), reaction_rates=(0.5, 0.5)
)
```

It diagonalized `m.killed_generator`, evaluated `det(I+G K)` at `-2.5`, and
computed the channel residues from the exact antisymmetric eigenvector. The
small-`s` command swept `s=10**(-k)`, `k=0,...,16`, and compared
`ctmc_green_resolvent(..., verify_direct=True)` with
`ctmc_channel_laplace` channel by channel.

The archived fold check imported `validate_gig_fold.py`, rebuilt
`physical_ctmc(theta)` at the JSON value, solved
`(-T)^T occupation = initial`, and differentiated rebuilt `f_t` values at
`theta +/- h`; it did not call the script's fold locator.

## Exclusions and residual scope

- I did not certify continuum operator domains, compactness/meromorphic
  continuation, an unbounded or trace-space reaction operator, or a Robin
  analogue. The manuscript already treats these as conditional or future work.
- I did not prove a uniform zero-mode cancellation bound. The reported sweep is
  a numerical falsifier for the current dense reference implementation.
- The zero-frequency direct routine requires `-T` to be globally nonsingular.
  Reducible chains with only an initial-state reachable transient subspace,
  partial absorption, Drazin/group inverses, and quasi-stationary projections
  remain outside its declared implementation scope.
- I did not audit root isolation, fold continuation, finite-radius convergence,
  GIG asymptotics, Lean statement fidelity, global manifests, or PDF layout;
  those belong to later rounds.
- No current scientific conclusion was found to depend on a negative-frequency
  secular root or on the inaccurate tiny-positive-`s` Green values.

## Round gate

There is no sign error requiring retraction of the finite CTMC calculations.
Round 02 should nevertheless remain open until B1-01 is resolved in the
continuum statement. B2-01 and B2-02 require executable regression coverage or
an explicit downgrade to a right-half-plane-only reference identity; B2-03
requires the full observable-sensitivity formula and fixed-support hypothesis
to be visible. After those changes, rerun the focused Green tests plus the
singular-`K`, pole-cancellation, dark-mode, and `s downarrow 0` cases above.
