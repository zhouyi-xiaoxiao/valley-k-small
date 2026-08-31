# Round 03 adversarial audit: G1 continuum smoke

**Audited artifacts**

- notes/continuum_g1_design.md
- code/continuum_g1_smoke.py
- code/test_continuum_g1_smoke.py
- artifacts/data/continuum_g1_smoke.json

**Overall verdict:** **MAJOR / NEEDS REVISION**

**Release decision:** the present G1a result must be downgraded from an
unqualified **PASS** to **INCOMPLETE (foundation gates not yet
discriminating)**. There is no P0 evidence that the assembled operator is
mathematically wrong: the SG direction, tensor ordering, mass convention,
current geometry, and time-jet orientation all survive direct inspection.
The downgrade is caused by P1 evidence failures: several physically wrong
implementations still satisfy every current gate and emit PASS.

The JSON does contain an unusually good claim-scope warning: it explicitly
says “smoke only” and excludes a continuum fold, mesh convergence, cusp,
trimodality, and a PRR claim. Therefore its twelve booleans are truthful as
self-consistency checks. They are not yet sufficient evidence for the stronger
phrase “pre-fold G1 foundations passed”.

## 1. Verdict matrix

| Component | Verdict | Finding |
|---|---|---|
| SG flux direction and OU equilibrium | **PASS** | The row rates implement Eq. (5.1) with the correct drift direction, and the equilibrium test is sign-sensitive. |
| Kronecker ordering | **PASS / MINOR test gap** | The current order is \(z,r_\parallel,r_\perp\) with the transverse index fastest, consistently used by generators, killing, initial masses, and reshape. There is no asymmetric sentinel regression test. |
| Cell mass versus density | **PASS** | The state stores cell masses; patch masses are divided by \(h_z\) to form cell-average rates; contact geometry is a cell fraction. |
| Bump Jacobian | **PASS** | The change \(u=(x-x_0)/\epsilon\) is handled correctly; the width cancels in a cell mass. |
| Wrapped transverse initial law | **PASS / MINOR test gap** | The implementation works at a cut-crossing centre, but the supplied test uses centre zero and never exercises wrapping. |
| Initial first-moment gate | **MAJOR** | It is absent, and the saved coarse state does not reproduce the declared \(z\) and \(r_\parallel\) means when interpreted as the FV piecewise-constant law. |
| Circle--rectangle fractions | **PASS numerically / MAJOR evidence gap** | The current integration is plausible and globally accurate, but only total area is gated. A translated contact mask with the same area still passes all gates. QUADPACK returns an error estimate, not a certified upper bound. |
| Physical budget formula at frozen \(W=1,\theta=0.5\) | **PASS locally / MAJOR gate gap** | Individual patch integrals, endpoint controls, and zero derivative budget are not gated. Opposite normalization errors cancel exactly at the only tested control. |
| Total material amount for general \(W\) | **MINOR now; MAJOR before generalization** | The field called physical_budget stores \(\int\kappa dz=\mathcal B\), while Eq. (4.3) calls \(W^{d-1}\mathcal B\) the total installed amount. The frozen \(W=1\) hides the distinction. |
| \(f_t,f_{tt},f_{ttt}\) orientation | **PASS algebraically / MAJOR missing validation** | For \(\dot p=A^Tp\), the code correctly evaluates \(p^TA^nk\). None of the jet values is a PASS gate or is compared with finite differences/dense expm. |
| Discrete mass identities | **PASS but not independent** | killed row sums and differential balance are algebraic consequences of constructing \(A=Q-\operatorname{diag}k\); they cannot detect a misplaced mask or tensor permutation. |
| Boundary-layer fraction | **MINOR calculation bug + omitted gate** | Corners in the \(z\)- and \(r_\parallel\)-boundary layers are counted twice. The diagnostic is not a gate. |
| Saved JSON reproducibility | **PASS** | In-memory regeneration serializes to the same SHA-256 as the stored JSON. |
| Supplied tests | **PASS but insufficient** | All four tests pass; mutation attacks below show that this suite does not discriminate important physical errors. |

## 2. Checks that genuinely pass

### 2.1 SG direction and detailed balance

At a face with \(\mathrm{Pe}=bh/D_*\), the code uses

$$
q_{i\to i+1}=\frac{D_*}{h^2}\mathscr B(-\mathrm{Pe}),
\qquad
q_{i+1\to i}=\frac{D_*}{h^2}\mathscr B(\mathrm{Pe}).
$$

For positive constant drift,
\(\mathscr B(-\mathrm{Pe})=e^{\mathrm{Pe}}\mathscr
B(\mathrm{Pe})\), so the rightward rate is larger. For the OU drift, the
potential difference between adjacent cell centres is exactly
\(-\mathrm{Pe}\) in thermal units, so the cell-centre Gaussian used in the
test is an exact discrete reversible law. Testing
\(Q^T\pi=0\), rather than \(Q\pi=0\), is correct for a row generator and a
column mass vector.

The existing equilibrium test is therefore meaningful and catches a reversal
of the Bernoulli factors.

### 2.2 Kronecker and cell-mass conventions

The implementation consistently uses the C-order flattening

$$
i=\operatorname{ravel}(i_z,i_\parallel,i_\perp),
$$

with \(i_\perp\) fastest:

$$
Q=Q_z\otimes I_\parallel\otimes I_\perp
 +I_z\otimes Q_\parallel\otimes I_\perp
 +I_z\otimes I_\parallel\otimes Q_\perp.
$$

The following objects use the same order:

- contact.reshape(-1);
- numpy.kron(kappa, contact_relative);
- numpy.kron(midpoint_initial,
  numpy.kron(relative_parallel_initial, relative_perp_initial));
- states.reshape(time, midpoint, relative_parallel, relative_perp).

An asymmetric \(5\times6\times7\) sentinel showed that an interior row
connects only to the six expected coordinate neighbours, and an independent
construction of the killing vector had maximum discrepancy zero.

The mass/density distinction is also correct on the uniform Cartesian mesh:
initial arrays are marginal cell masses; patch bump masses are divided by
\(h_z\) to form \(\bar\phi\); and the circle area is divided by cell area to
form \(\bar\chi\). Thus \(p^Tk\) is a reaction-time density without an extra
cell-volume factor.

### 2.3 Bump Jacobian and periodic wrapping

The helper integrates

$$
\int_{I_k}\frac{1}{\epsilon I_0}
 e^{-1/(1-((x-x_0)/\epsilon)^2)}dx
=\frac{1}{I_0}\int_{(I_k-x_0)/\epsilon}
 e^{-1/(1-u^2)}du,
$$

so no factor of \(\epsilon\) is missing. A separate cut-crossing probe gave

    wrapped_mass 1.0000000000000004
    circular_mean 0.49500000000000005
    target 0.495

for a bump centred at \(0.495\) with half-width \(0.02\) on
\([-0.5,0.5)\).

The existing unit test does not establish this because its periodic bump is
centred at zero and never wraps. Add a boundary-centred circular-moment test.

### 2.4 Time-generator orientation

With a row generator \(A\) and column state,

$$
p(t)=e^{A^Tt}p_0,\qquad f=p^Tk,
$$

so

$$
f_t=p^TAk,\quad f_{tt}=p^TA^2k,\quad
f_{ttt}=p^TA^3k.
$$

Lines 483--505 implement exactly these formulas. There is no transpose error
in the current code.

This is a static verification, not a numerical gate. The reported jet ranges
are not used in gates at all. Replacing the three jet vectors by unrelated
vectors or zeros would leave status equal to PASS. Before fold work, compare
the jets against dense expm and high-order time differences on a small
asymmetric operator, as already required by Section 8.1(6).

## 3. P1: the contact gate admits a physically translated sink

The contact routine returns credible fractions for the current disk, but
build_payload only checks:

- each fraction lies in \([0,1]\) during construction;
- the sum of cell areas is \(\pi a^2\);
- the accumulated QUADPACK error estimate is small.

These checks cannot establish where the disk is or whether its tensor indices
are correct. The following mutation rolls the entire contact mask by three
periodic cells while preserving its total area and reported integration error:

    PYTHONPATH=research/reports/encounter_multimodal_prr/code \
    PYTHONDONTWRITEBYTECODE=1 .venv/bin/python - <<'PY'
    import numpy as np
    import continuum_g1_smoke as g1

    kw = dict(midpoint_cells=17, relative_parallel_cells=19,
              relative_perp_cells=17, theta=0.5,
              time_stop=20.0, time_points=61)
    good = g1.build_payload(**kw)
    original = g1.contact_cell_fractions

    def shifted(*args, **kwargs):
        fraction, area, error = original(*args, **kwargs)
        return np.roll(fraction, 3, axis=1), area, error

    g1.contact_cell_fractions = shifted
    bad = g1.build_payload(**kw)
    print(good["status"], bad["status"], all(bad["gates"].values()))
    print(good["solve"]["maximum_density"],
          bad["solve"]["maximum_density"])
    print(good["solve"]["final_survival"],
          bad["solve"]["final_survival"])
    PY

Observed output:

    PASS PASS True
    0.037468668234461086 0.03522522847547172
    0.4776290286724378 0.4951749114121032

The physically wrong mask changes the maximum density by about \(6.0\%\) and
still passes every gate. This is a direct false-positive counterexample, not
merely a missing cosmetic test.

Required repair:

1. add independent local geometry checks, not just total area;
2. use asymmetric cell sentinels to verify \((r_\parallel,r_\perp)\) ordering;
3. check disk centroid, coordinate reflections, and selected per-cell
   fractions against an independent analytic/high-precision implementation;
4. persist per-cell or normwise comparison evidence;
5. expose a genuine quadrature-control parameter and perform the doubled-order
   comparison required by the design.

SciPy quad returns a deterministic numerical estimate named abserr; it is not
a rigorous guaranteed upper bound. The JSON key
contact_area_error_bound therefore overstates the evidence. Either use a
validated analytic circle-segment formula/interval enclosure or rename and
independently convergence-test the estimate.

## 4. P1: one midpoint budget check can hide patch errors

The current patch construction is correct for the frozen inputs. However,
status checks the aggregate budget only at the requested \(\theta\), and both
the artifact and tests use \(\theta=0.5\). At that point the near and far
weights are equal (\(0.375,0.375\)), allowing opposite normalization errors to
cancel.

This mutation multiplies the near patch integral by \(1.2\) and the far patch
integral by \(0.8\):

    PYTHONPATH=research/reports/encounter_multimodal_prr/code \
    PYTHONDONTWRITEBYTECODE=1 .venv/bin/python - <<'PY'
    import continuum_g1_smoke as g1

    original = g1.bump_cell_masses
    def biased(edges, *, centre, half_width, period=None):
        mass, error = original(edges, centre=centre,
                               half_width=half_width, period=period)
        if abs(half_width-0.08) < 1e-14 and abs(centre-0.48) < 1e-14:
            mass = 1.2*mass
        if abs(half_width-0.08) < 1e-14 and abs(centre-0.86) < 1e-14:
            mass = 0.8*mass
        return mass, error

    g1.bump_cell_masses = biased
    common = dict(midpoint_cells=17, relative_parallel_cells=19,
                  relative_perp_cells=17, time_stop=2, time_points=5)
    for theta in (0.5, 0.0, 1.0):
        out = g1.build_payload(theta=theta, **common)
        print(theta, out["status"],
              out["geometry_and_budget"]["physical_budget"],
              out["geometry_and_budget"]["budget_relative_error"])
    PY

Observed output:

    0.5 PASS 0.6000000000000001 1.8503717077085943e-16
    0.0 FAIL 0.678 0.13000000000000012
    1.0 FAIL 0.5220000000000001 0.12999999999999975

Thus the only tested control can pass while both endpoints have \(13\%\)
budget error. This directly contradicts the design requirement to check every
patch and every tested control without meshwise cancellation.

Required repair:

- gate all three individual integrals
  \(h_z\sum_k\bar\phi_{j,k}=1\);
- gate \(\sum_jw_j(\theta)=1\) and nonnegativity at both endpoints;
- gate the aggregate budget at \(\theta=0,0.5,1\), or prove and record the
  affine endpoint implication;
- gate \(h_z\sum_k\partial_\theta\kappa_k=0\);
- persist the patchwise values and quadrature estimates in the JSON.

There is also a hidden \(W=1\) naming trap. For a custom \(W=2\) pilot the
model reports physical_budget \(=0.6\), while Eq. (4.3) gives total installed
material \(W\mathcal B=1.2\). The killing field correctly uses the per-unit
transverse budget \(\mathcal B\); the output should report both quantities
under unambiguous names before any multi-\(d\) generalization.

## 5. P1: the initial first-moment gate is absent and currently fails

The product cell masses are nonnegative, sum to one, and are exactly
contact-safe on the saved grid. Those gates pass. Section 8.1(4) also requires
the discrete law to reproduce the declared first moments, but neither the
payload nor the tests compute them.

For the saved \(25^3\) grid, interpreting the finite-volume reconstruction as
piecewise constant gives

| Coordinate | Declared mean | Discrete mean | Error |
|---|---:|---:|---:|
| \(z\) | \(0.14\) | \(0.1280000000\) | \(-0.0120000000\) |
| \(r_\parallel\) | \(-0.35\) | \(-0.3057072888\) | \(+0.0442927112\) |
| wrapped \(r_\perp\) | \(0\) | \(0\) | \(0\) |

On the declared \(65\times65\times49\) discovery mesh, the errors are still
approximately \(7.67\times10^{-4}\) in \(z\) and
\(1.088\times10^{-2}\) in \(r_\parallel\). This is expected when a bump
narrower than a cell is represented only by cell average mass; it is not
evidence that bump integration is wrong. It does mean the declared gate has
not been operationalized.

The design should specify a mesh-scaled tolerance or require convergence of
discrete moments. The smoke payload must report:

- reconstructed linear moments in both nonperiodic coordinates;
- circular moment/resultant for the wrapped coordinate;
- their errors relative to the frozen initial law;
- a fail-closed tolerance appropriate to the stage.

If “reproduce” was intended to mean analytic moments of the underlying bump
rather than moments of the FV reconstruction, that interpretation must be
stated; the current artifact records neither.

## 6. Boundary diagnostic is not a fraction of a set union

Lines 513--518 add masses in the outer two \(z\) layers and the outer two
\(r_\parallel\) layers. States lying in both are counted twice. A unit mass in
a \(z/r_\parallel\) corner therefore produces boundary_mass \(=2\), so the
reported “fraction” can exceed one.

For the current run this is a conservative overestimate, not a false pass.
Use a boolean union mask (and preferably report the two coordinate
contributions separately). Handle grids with fewer than four cells
explicitly, because the first-two and last-two slices then overlap as well.

More importantly, maximum_boundary_layer_fraction is not present in gates.
The saved value \(6.34\times10^{-6}\) is far above the eventual Section
8.3(6) threshold \(10^{-8}\), although this coarse \(t\le40\) smoke is not
expected to pass the full box audit. This confirms that status PASS must not
be consumed as a Section 8/G1 result.

## 7. Self-consistency gates are partly tautological

The checks

$$
A\mathbf1+k=0
\quad\text{and}\quad
p^T(A\mathbf1)+p^Tk=0
$$

follow from the same construction
\(A=Q-\operatorname{diag}k\). They are valuable implementation invariants,
but the second is not an independent time-discretization validation and
cannot detect a wrong local mask, coordinate permutation, or wrong jet vector.

Section 8.1(6) already specifies the missing independent checks:

- sparse expm_multiply versus dense scipy.linalg.expm on a small operator;
- one full step versus two half steps;
- state and augmented sensitivity comparisons;
- finite-difference or complex-step checks of \(f_t,f_{tt},f_{ttt}\) and,
  later, \(\theta\)-derivatives.

At minimum, G1a should implement the small dense reference and jet checks now.

## 8. Saved artifact and test reproducibility

The supplied tests run successfully:

    PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest \
      -p no:cacheprovider -q \
      research/reports/encounter_multimodal_prr/code/test_continuum_g1_smoke.py

Observed:

    .... [100%]

The stored JSON also matches current serialization:

    stored SHA-256:
    ac1fa79306b1cd9847e728913b5099e195143e9e82b9c39304c443f4e8ec5d5f

    regenerated SHA-256:
    ac1fa79306b1cd9847e728913b5099e195143e9e82b9c39304c443f4e8ec5d5f

Direct Python dictionary equality is false only because dataclass tuples
serialize to JSON arrays and reload as lists; the bytes generated by the
script are identical.

## 9. Required fixes before G1a can regain PASS

### P1 blockers

1. Add local contact-geometry and asymmetric tensor-order gates capable of
   rejecting the translated-mask counterexample.
2. Replace or qualify the claimed contact error bound and add the independent
   doubled-control comparison required by the design.
3. Gate each patch integral, endpoint budgets, and the zero budget derivative;
   do not rely on the symmetric midpoint control.
4. Define and gate discrete initial first moments, including a circular
   transverse diagnostic.
5. Add a small dense-exponential reference and numerical time-jet checks.
6. Make the stage explicit in machine-readable form, for example
   stage = G1a_pre_fold_smoke and status = INCOMPLETE/PASS, so a generic PASS
   cannot be promoted to “Continuum Verified”.

### P2 / minor corrections

1. Count the union of nonperiodic boundary layers without duplicate corners.
2. Report per-unit transverse budget and total installed material separately.
3. Add a wrapped bump test whose support crosses the torus cut.
4. Add input validation for uniform monotone edges in the helpers that divide
   by the first cell width.
5. Persist individual bump/contact quadrature diagnostics rather than only
   aggregate totals.

## 10. Final decision

- **No P0:** no current evidence that SG direction, generator orientation,
  present tensor ordering, cell-mass scaling, bump Jacobian, or the current
  circle integral is mathematically wrong.
- **Multiple P1s:** physically misplaced contact, endpoint budget failure, and
  corrupted/unchecked jet evidence can evade the present PASS logic.
- **Current G1a PASS:** **downgrade to INCOMPLETE / NEEDS REVISION**.
- **Full G1 / PRR continuum claim:** remains explicitly unavailable, as the
  JSON correctly states.

Once the P1 gates are repaired, the existing implementation is a sound base
for the fold search; the required work is evidence hardening rather than a
rewrite of the continuum operator.
