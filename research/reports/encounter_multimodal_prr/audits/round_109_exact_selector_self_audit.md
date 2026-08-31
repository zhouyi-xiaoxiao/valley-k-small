# Round 109: exact rational modal-selector self-audit

Date: 2026-07-14  
Audit role: implementation author performing a fail-closed method and boundary attack  
Decision: **PASS exact finite rational selector / HOLD continuum certificate / HOLD F0 compatibility / REQUIRE independent audit / NO positive-B authorization**  
Open scientific/dependency gates: **P0 = 0, P1 = 2, P2 = 1**

## 1. Reviewed immutable bytes

| object | SHA-256 |
|---|---|
| `code/modal_certificate_exact_selector.py` | `bda458aef64ba43a73178c732733b7355c8c88bd35a943536602c78bd7091bec` |
| `code/test_modal_certificate_exact_selector.py` | `43fd42572a28b66406967f5a9c3fe9db38fa6f0302c92cc9d5f4ddc995a76292` |
| `notes/modal_certificate_exact_selector_design.md` | `58cf55a0d3ffbd62250d931ff9ee8ac4bdd2cfffc8e5721d2e7c3a7864dd4f56` |
| `scratch/modal_certificate_exact_selector_method_only_result.json` | `77e8d4a0e567b313d23ce737bf584515a2de84b901fbfeca40917202be9cfd98` |
| `code/modal_certificate_lp_poc.py` | `4920411d65f85653cdec16da206a19d7a8eb42610b6d01936ceae41ec3a6ae6e` |
| `scratch/modal_certificate_lp_poc_result.json` | `6f04ef4c618677d6d26b80cd04e3d4f8c9918fd50a649cfc0dd0bf064ccce604` |
| `notes/modal_certificate_theory_and_prr_redirect.md` | `38dde114552d0cea69f714d7493d3cb6715e1b4ed436431045a50a57360326be` |
| `notes/positive_b_fixed_control_robustness_design_v1.md` | `891b49a3b9efbfa93c27c09e4f585a088b40f079c3ff5642536764f1523698d7` |

No positive-budget generator, finite-volume production row, allocation-v6
state, primary F1 mesh, or Monte Carlo trajectory was evaluated.  The only
kernel calculation in the audit was a read-only replay of the already
established B0 free-exposure coefficient source.

## 2. Executive verdict

The new implementation closes the solver-native selector defect at the only
level presently justified:

- the three coefficient tables are frozen decimal strings;
- every string is parsed as an exact `Fraction`;
- `rho` is unrestricted;
- every candidate active-set system is solved exactly;
- every candidate is checked against all exact constraints;
- primary objectives are compared exactly;
- the exact lexicographically smallest weight tuple resolves a primary tie;
- zero scales, invalid tables, infeasible floors, missing vertices, and
  nonpositive optima have distinct fail-closed statuses; and
- raw signed margins and row scales are serialized with exact numerators and
  denominators.

The artifact correctly refuses two promotions.  First, exactness of a
rationalized table is not continuum interval certification.  Second, the
new exact vertices are not byte-identical to the F0 `raw/S_c` controls, so
they are not silently installed as production controls.

Within the finite rational LP scope, no P0 or P1 mathematical defect was
found.  The remaining P1 items are external evidence/decision gates that the
artifact correctly marks HOLD.

## 3. Static and executable checks

### 3.1 Frozen decimal provenance replay

Using repository Python `3.12.13`, NumPy `2.5.1`, SciPy `1.18.0`, and only the
free-exposure `FourPatchContinuum(PRIMARY,broad_parameters())` path, an audit
script independently recomputed

```text
repr(max_j abs(d_lj))
repr(sign_l d_lj / max_j abs(d_lj)).
```

For `m1`, `m2`, and `m3`, checkpoint bytes, every row-scale byte, and every
signed normalized coefficient byte matched the frozen tables exactly:

```text
m1 times=True scales=True rows=True
m2 times=True scales=True rows=True
m3 times=True scales=True rows=True.
```

This proves table provenance from the present ordinary binary64 B0 kernel.  It
does not turn those bytes into outward continuum intervals.

### 3.2 Tests and lint

The science-free suite returned

```text
8 passed
ruff: All checks passed.
```

The fixtures attack:

- exact hexadecimal parsing and all three F0 dyadic raw sums;
- an extended primary-optimal face whose deterministic answer depends on the
  lexicographic secondary rule;
- a zero exact optimum;
- an infeasible exact simplex floor;
- a zero checkpoint scale;
- a malformed normalized row;
- all three broad frozen tables; and
- top-level continuum and F0 compatibility HOLD semantics.

### 3.3 Canonical replay and append-only behavior

Two complete in-memory builds were byte-identical to each other and to the
saved `54,781`-byte canonical JSON:

```text
artifact_equals_rebuild = True
two_rebuilds_equal      = True.
```

For every selected vertex, the exact simplex residual was `0/1`, and the
smallest exact inequality residual was zero rather than a negative tolerance
excursion.  A second attempt to write the canonical path exited nonzero with

```text
method-only output already exists; refusing overwrite.
```

## 4. Mathematical attack

### 4.1 Vertex enumeration is complete for this LP

There are five variables and one affine simplex equality, hence four affine
degrees of freedom.  Every vertex has four linearly independent active
inequalities in addition to the equality.  Enumerating all four-element
subsets of the checkpoint and floor inequalities therefore includes every
vertex; degeneracy only makes more than one subset generate the same exact
point.  Singular subsets are rejected, and exact point tuples deduplicate the
remainder.

Because the weight simplex with an admissible floor is compact and
`rho <= min_l a_l dot w`, the primary maximum is finite and attained.  A
linear objective attains a maximum at a vertex.  The enumerated exact maximum
is therefore an exact global optimum of the frozen rational LP, not a local
or tolerance-qualified optimum.

The active-set counts also match the independent combinatorics:

| table | inequalities | four-active subsets | unique feasible vertices | primary-optimal vertices |
|---|---:|---:|---:|---:|
| `m1` | 6 | `C(6,4)=15` | 7 | 1 |
| `m2` | 8 | `C(8,4)=70` | 11 | 1 |
| `m3` | 10 | `C(10,4)=210` | 16 | 1 |

### 4.2 Unrestricted `rho` and nonpositive failure semantics

The implementation places no lower bound on `rho`.  A synthetic table with
opposing rows has exact optimum zero and returns

```text
HOLD_RATIONALIZED_OPTIMUM_NONPOSITIVE
```

rather than becoming artificially infeasible under `rho>=0`.  This closes
the Round-103/Round-106 failure-semantics objection for the finite rational
selector.

### 4.3 Lexicographic selector

For a synthetic primary face defined by `rho <= w0+w1`, exact optimization
leaves a continuum of primary optima after `w2=w3=1/10`.  The enumerator
selects

```text
(w0,w1,w2,w3) = (1/10,7/10,1/10,1/10)
```

exactly, which is the lexicographically smallest primary optimizer.  No
iteration order or external solver basis enters the result.

### 4.4 Exact result reconstruction

The saved optima are:

| control | exact finite-LP status | displayed `rho` | displayed smallest reconstructed raw signed margin |
|---|---|---:|---:|
| `m1` | PASS | `0.88099041195984484681` | `0.09879189274140475529` |
| `m2` | PASS | `0.32540424848060426430` | `0.001818065840583040156` |
| `m3` | PASS | `0.13616273641487362346` | `0.001424914662273619541` |

Every displayed decimal has an exact rational counterpart in the artifact.
The raw signed values are exact only for `frozen_scale * frozen_normalized_row
dot w`; they are not promoted to true-continuum derivative margins.

## 5. Boundary attacks

### 5.1 Rational exactness versus continuum exactness: HOLD correctly preserved

The frozen coefficients were produced by ordinary quadrature and rounded to
binary64 before their shortest decimal representations were recorded.  No
simultaneous outward error box links them to the true continuum derivative
rows.  Exact vertex enumeration therefore proves neither robust feasibility
under coefficient perturbation nor a continuum optimum sign.

Moreover, the checkpoint LP is only an at-least-mode sign certificate.  The
artifact contains no outward interval curvature boxes and no complement
derivative certificate on `[0.5,35]`.  It therefore cannot prove an exact
one-/two-/three-mode continuum topology.  The saved top-level status

```text
HOLD_CONTINUUM_COEFFICIENTS_NOT_INTERVAL_CERTIFIED
```

is necessary and correct.

### 5.2 F0 exact-control compatibility: HOLD correctly preserved

The selector vertices differ exactly from all three controls already defined
in F0 as binary64 raw ratios divided by their exact dyadic sums:

| control | exact equality | F0 weight satisfies exact selector floor | maximum absolute component delta |
|---|---|---|---:|
| `m1` | false | false | `1.5821e-17` |
| `m2` | false | true | `7.7274e-18` |
| `m3` | false | false | `1.5812e-16` |

For `m1`, the F0 comparison point lies just outside the new exact-floor
feasible set and can consequently have a slightly larger rationalized-table
margin; the artifact does not mislabel that signed difference as an
optimality gap over a feasible point.  For feasible comparisons, the exact
selector gap is nonnegative.

Every compatibility row records `replacement_authorized=false`.  The
artifact correctly requires either:

1. an F0 v1 amendment and independent audit before any positive-`B` output;
   or
2. retention of the existing F0 controls, with this selector kept as a
   candidate/method result and the prior broad-family pilot disclosed.

The numerical smallness of the differences is not a license to ignore the
frozen-control boundary.

### 5.3 Positive-budget contamination: none found

The producer has no imports or code paths to the continuum kernel, FV model,
killed semigroup, or Monte Carlo core.  Its top-level fields explicitly say:

```text
positive_budget_evaluated = false
primary_finite_volume_grid_evaluated = false
continuum_kernel_executed_by_this_producer = false
external_lp_solver_used = false
authorized_scientific_command = null.
```

No old allocation-v6 or historical-anchor value enters an objective or gate.

## 6. Findings and required closure

| ID | priority | finding | consequence | closure |
|---|---:|---|---|---|
| R109-P1-1 | P1 | no outward continuum coefficient enclosure or full-window box-and-complement certificate exists | finite rational exactness cannot become a continuum or exact-topology claim | construct and independently validate a new outward interval coefficient/curvature/complement version; ordinary quadrature agreement is insufficient |
| R109-P1-2 | P1 | exact-selector vertices differ from the frozen F0 controls | silently installing them would violate the no-refit/freeze boundary | before any positive-`B` run, either amend F0 v1 and independently audit it or retain F0 weights and demote this result to method/candidate evidence |
| R109-P2-1 | P2 | this is a self-audit, not an implementation-independent acceptance | author reconstruction cannot by itself close the F0 evidence gate | commission an independent replay/attack of table bytes, enumeration completeness, exact outputs, and compatibility semantics |

These are not permissions to relax the claim.  They are why the top-level
artifact is HOLD despite three exact finite-LP PASS rows.

## 7. Final ledger

```text
frozen decimal-table provenance              = REPRODUCED AT B0
exact Fraction parsing                       = PASS
unrestricted-rho LP                          = PASS
all vertex candidates solved/checked exactly = PASS
primary optimum                              = PASS FOR FINITE RATIONAL LP
lexicographic tie break                       = PASS
raw margins and row scales serialized         = PASS IN RATIONALIZED UNITS
distinct failure states                       = PASS
canonical replay                              = BYTE-IDENTICAL
append-only refusal                           = PASS
continuum coefficient intervals               = MISSING / HOLD
full-window exact topology certificate         = MISSING / HOLD
F0 control byte compatibility                  = FAIL / HOLD, NO REPLACEMENT
positive-budget science                        = NOT RUN / NOT AUTHORIZED
independent implementation acceptance          = NOT YET PERFORMED
P0                                             = 0
P1                                             = 2
P2                                             = 1
```

**Final decision: the exact rationalized selector is publication-grade as a
finite-LP method artifact, but it is not a continuum certificate and it is
not compatible with silently replacing the already frozen F0 controls.  F1
remains unauthorized.**
