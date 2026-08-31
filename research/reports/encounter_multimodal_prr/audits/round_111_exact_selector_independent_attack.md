# Round 111: independent attack on the exact rational modal selector

Date: 2026-07-14  
Audit role: implementation-independent finite-LP reconstruction and boundary attack  
Decision: **PASS finite rational selector / GO for an explicit v2 candidate-control amendment after interface repair / HOLD continuum certificate / HOLD F0 implementation and all positive-`B` science**  
Open findings: **P0 = 0, P1 = 2, P2 = 1**

## 1. Scope and non-execution boundary

This audit reviewed, without modifying, the exact-selector implementation,
tests, method artifact, design note, and author self-audit:

| object | SHA-256 at audit time |
|---|---|
| `code/modal_certificate_exact_selector.py` | `bda458aef64ba43a73178c732733b7355c8c88bd35a943536602c78bd7091bec` |
| `code/test_modal_certificate_exact_selector.py` | `43fd42572a28b66406967f5a9c3fe9db38fa6f0302c92cc9d5f4ddc995a76292` |
| `scratch/modal_certificate_exact_selector_method_only_result.json` | `77e8d4a0e567b313d23ce737bf584515a2de84b901fbfeca40917202be9cfd98` |
| `notes/modal_certificate_exact_selector_design.md` | `58cf55a0d3ffbd62250d931ff9ee8ac4bdd2cfffc8e5721d2e7c3a7864dd4f56` |
| `audits/round_109_exact_selector_self_audit.md` | `30123f832243606d738de13be8d37c02280c600e5ddcfb306a061750260d1262` |

The integration read also covered:

| object | SHA-256 at audit time |
|---|---|
| `notes/positive_b_fixed_control_robustness_design_v2.md` | `85351b42d9d5fa796476ccb82df969fca9e0e841503c3001e8a2f7b89b248dab` |
| `notes/modal_certificate_theory_and_prr_redirect.md` | `38dde114552d0cea69f714d7493d3cb6715e1b4ed436431045a50a57360326be` |

No positive-budget killed process, primary finite-volume configuration,
allocation-v6 branch, or off-lattice trajectory was run.  The executable
checks were restricted to the science-free exact-selector tests, exact
rational reconstruction, canonical replay, and a read-only B0 free-exposure
provenance replay at the already frozen checkpoints.

## 2. Executive verdict

The finite rational LP claim is independently accepted.  In particular:

- enumerating four active inequalities in addition to the simplex equality
  is complete for every vertex of the five-variable LP;
- an independent reduced-coordinate/Cramer reconstruction produced the same
  complete vertex sets, exact optima, and exact selected fractions;
- choosing the lexicographically smallest primary-optimal **vertex** is
  equivalent to sequential coordinate minimization over the entire
  primary-optimal face;
- `rho` is genuinely unrestricted, and a zero or negative exact optimum is a
  distinct HOLD rather than an artificial infeasibility;
- every serialized exact margin, scale, residual, and F0 difference
  reconstructs exactly from the frozen strings;
- the canonical artifact replays byte for byte; and
- the artifact consistently says that its source table is a rationalization
  of ordinary binary64 B0 output, not a continuum interval enclosure.

The result is therefore suitable as a deterministic selector for the three
**finite rationalized tables**.  It may also supply the normative exact
rational weights in an explicit pre-science v2 amendment, because v2 records
that no exact amended control has yet been evaluated at positive `B` and does
not silently identify it with the retired v1 controls.

That adoption is not yet an F0 or scientific PASS.  A contradictory v2 F0
instruction still tells an implementation to construct the controls from raw
hex ratios, and the true-continuum coefficient and full-window gates do not
exist.  Both P1 items below must remain hard stops.

## 3. Independent exact reconstruction

### 3.1 A different coordinate system and solver

The producer solves five-by-five active-set systems by exact Gauss--Jordan
elimination.  This audit did not call that solver for its independent
reconstruction.  It eliminated

```text
w3 = 1 - w0 - w1 - w2
```

and represented every inequality in the four variables

```text
(w0,w1,w2,rho).
```

For each four-inequality active set, the audit used exact `Fraction` Cramer
determinants, checked every transformed inequality, reconstructed `w3`, and
deduplicated exact five-component points.  This is algebraically independent
of the producer's five-by-five Gauss--Jordan path.

The result was:

| table | active subsets | singular | feasible before deduplication | unique vertices | primary-optimal vertices | selected point matches artifact |
|---|---:|---:|---:|---:|---:|---|
| `m1` | 15 | 1 | 7 | 7 | 1 | yes |
| `m2` | 70 | 1 | 11 | 11 | 1 | yes |
| `m3` | 210 | 1 | 16 | 16 | 1 | yes |

For reproducibility, SHA-256 digests of the sorted exact vertex tuples in this
independent coordinate reconstruction were:

```text
m1  beb6e9858ed92e65c887e50cb2d300cfcd5614238018bbb957ef3b3199acc2b8
m2  27314d1ee24a491321f9c16d665244acc916d9cf838d44053380e5358b96b4d9
m3  2be4715d801efcf236ea39763db144c1379456c25d693e7a15b08331f6912052
```

The independently selected exact points were identical to the JSON fractions,
including `rho`.

### 3.2 Why the enumeration is complete

After the simplex equality, the feasible polyhedron has four affine degrees
of freedom.  Every vertex has at least four linearly independent active
inequalities; selecting those four gives a nonsingular system included in the
enumeration.  A degenerate vertex can be generated by more than one active
set, but exact tuple deduplication does not remove the point itself.

Although `rho` is unbounded below, this does not invalidate the maximization
argument.  The weight set is compact, and for every fixed `w` the largest
feasible value is

```text
rho(w) = min_l a_l dot w.
```

This continuous piecewise-linear function attains a finite maximum on the
compact weight polytope.  The primary-optimal face is bounded and contains a
vertex of the original polyhedron.  Exhausting the vertices therefore
exhausts all candidates for the primary optimum.

### 3.3 Why vertex lexicographic selection equals sequential LPs

Let `F0` be the primary-optimal face.  Minimizing `w0` over `F0` produces a
face `F1`; minimizing `w1` over `F1` produces a face `F2`, and so on.  Every
stage is the intersection with a supporting hyperplane.  After all four
weight coordinates and the already fixed primary `rho` have been selected,
the surviving weight vector is a singleton because the weights sum to one.
That singleton is a vertex of the primary face and hence a vertex of the
original polyhedron.  Therefore the lexicographically smallest point over
the whole primary-optimal face is present among the enumerated
primary-optimal vertices.  Taking the exact tuple minimum over those vertices
is the declared sequence of secondary LPs, not a solver-basis shortcut.

All three frozen tables happen to have only one primary-optimal vertex, but
the supplied synthetic extended-face fixture also exercises the nonunique
case.

## 4. Exact payload, provenance, and replay checks

### 4.1 Tests and lint

The science-free suite and lint returned:

```text
8 passed
ruff: All checks passed
```

The nonpositive fixture confirmed that no `rho >= 0` constraint is inserted:
the exact zero optimum returns
`HOLD_RATIONALIZED_OPTIMUM_NONPOSITIVE` with a selected zero-`rho` vertex.

### 4.2 Exact serialized identities

For every table, this audit reconstructed from the JSON alone:

- all weight fractions and their exact unit sum;
- every signed normalized checkpoint margin;
- `rho = min_l a_l dot w` exactly;
- every raw signed rationalized-table margin
  `scale_l (a_l dot w)`;
- every checkpoint residual `a_l dot w - rho`;
- every floor residual `w_j - 3/100`;
- every v1 F0 rational weight, selector-minus-F0 delta, and comparison margin.

All identities passed with no tolerance.  The minimum reconstructed raw
margins were exactly the fractions serialized in the artifact.  They remain
raw only in the declared internal relation

```text
frozen decimal scale * frozen decimal normalized row * exact rational weight.
```

They are not enclosures of the analytical derivative.

### 4.3 Table hashes and B0 provenance

Independent canonical compact-JSON hashing reproduced the table hashes:

```text
m1  20f8ed31ab95a20f14b66a42325cebe0991f265a886cf28374ad568328065afc
m2  bf2b117a3cbfdcc712030abcc353631f3dd366f539f51152234ab2713f05168c
m3  0f76d711b8ff65999e17c2281e14ad0311c7877a37887c9e342345657fc68377
```

A read-only replay of the present B0 free-exposure kernel, using each table's
frozen checkpoint vector as one batch, reproduced every checkpoint byte,
row-scale `repr`, and signed normalized coefficient `repr`.  This verifies
provenance from the current ordinary binary64 path.  It does not add an error
bound around those values.

### 4.4 Canonical artifact replay

Two in-memory method builds were identical to one another and to the saved
`54,781`-byte artifact:

```text
saved SHA-256   = 77e8d4a0e567b313d23ce737bf584515a2de84b901fbfeca40917202be9cfd98
rebuild SHA-256 = 77e8d4a0e567b313d23ce737bf584515a2de84b901fbfeca40917202be9cfd98
```

The saved source hashes match the current source objects that the producer
declares.  The top-level status remains
`HOLD_METHOD_ONLY_NOT_A_CONTINUUM_OR_F0_CONTROL_CERTIFICATE`, and
`authorized_scientific_command` is null.

## 5. F0 compatibility and v2 adoption

### 5.1 V1 mismatch is real and correctly held

The exact-selector weights differ from the v1 exact dyadic raw-over-sum
controls for all three rows.  The comparison code and JSON correctly preserve
those exact mismatches, distinguish whether the v1 point satisfies the new
exact `3/100` floor, and set `replacement_authorized=false`.

No tolerance argument can turn this into v1 compatibility.  The exact
selector artifact is right to keep
`HOLD_F0_CONTROL_COMPATIBILITY_NO_SILENT_REPLACEMENT`.

### 5.2 V2 may adopt the vertices only as an explicit new contract

Section 4.1 of v2 explicitly retires the v1 mathematical controls before any
positive-`B` evaluation of the amended controls and defines the new weights by
the exact numerator/denominator paths in the pinned JSON.  This is the honest
branch allowed by the selector artifact.  Subject to P1-1 below, this audit
accepts those exact rational vertices for v2 as:

> result-informed, finite-rational-LP-selected, prospectively fixed candidate
> controls whose own positive-budget evaluations are held out.

It does **not** accept any of these stronger descriptions:

- exact binary64/dyadic reproductions of the v1 controls;
- interval-certified continuum-selector outputs;
- complete one-/two-/three-mode continuum certificates;
- evidence that the same topologies persist at `B=0.01`; or
- authorization to create or execute F1.

## 6. Findings

### R111-P1-1 — v2 still contains a control-construction instruction for the retired v1 branch

V2 Section 4.2 normatively defines each amended control from

```text
selector_results[c].selected.weights[j]
```

in the pinned exact-rational JSON.  However, its F0 checklist still requires:

```text
exact rational control construction from raw hex ratios.
```

Those raw hex ratios are the retired v1 inputs.  Following that F0 bullet
would reconstruct the wrong exact controls and immediately violate v2's own
no-refit and hash contract.

**Required closure before F0 implementation:** replace the F0 requirement
with exact numerator/denominator construction from the pinned selector JSON,
add a negative fixture proving that the v1 raw-hex path is rejected, and pin
this independent audit in v2.  If historical v1 reconstruction remains in
the implementation, it must be comparison-only and impossible to select as a
v2 production control.

The related theory note still says to freeze an “exact binary64 selector,”
whereas the accepted object is an exact **decimal-rationalized finite-table**
selector.  V2 or a versioned theory addendum must explicitly supersede that
number-system wording; it must not describe decimal rationals as exact dyadic
binary64 coefficients.

**Consequence:** v2 control adoption is conditionally acceptable, but F0
implementation is HOLD until this interface is made single-valued.

### R111-P1-2 — continuum feasibility and the complete finite-window certificate remain absent

The exact selector has no simultaneous outward enclosures connecting its
frozen coefficient strings to the true free-exposure derivative coefficients.
Its positive `rho` values therefore prove positivity only for the three
rationalized finite LPs.  Checkpoint signs alone also prove only the local
at-least-extremum statement; they cannot exclude extra or even-multiplicity
stationary points on `[0.5,35]`.

**Required continuum feasibility gate:** for every checkpoint and channel,
construct simultaneous outward enclosures of the unnormalized signed
derivative and a strictly positive outward enclosure of the row scale.  For
each adopted exact rational weight, prove a strictly positive lower bound on
every signed checkpoint margin under the complete coefficient uncertainty.
Equivalently, a rigorously implemented robust interval LP may prove a positive
worst-case optimum, but ordinary quadrature agreement or additional printed
digits is not sufficient.

**Required complete-window gate:** choose ordered peak/valley boxes whose
closed gaps cover the whole declared window; certify outward endpoint
derivative signs and strict uniform curvature of the required type in every
box; and certify a strict fixed-sign derivative margin on every complement
gap, including both window endpoints.  Only that box-and-complement coverage
can support “exactly one/two/three” at B0.

For an analytical transfer to positive budget, the raw box-endpoint,
complement, and curvature margins must then be compared with explicit
monotone mixed-jet error bounds over every `beta in [0,B]`.  A positive-B
semidiscrete F1 still separately needs its validated all-configuration
interval-time certificate, and off-lattice F3 cannot prove absence of extra
modes.

**Consequence:** continuum/publication status and F1 authorization remain
HOLD even after the exact rational vertices are adopted by v2.

### R111-P2-1 — the binary64 source row is batch-context sensitive at a repeated checkpoint

The same mathematical checkpoint `t=5.5` appears in `m1` and `m2`.  The
present B0 kernel gives one-ulp-different row scales and normalized rows when
that time is evaluated in the two different frozen time batches:

```text
m1 batch scale at 5.5 = 0.2674801474024189
m2 batch scale at 5.5 = 0.2674801474024188.
```

This does not invalidate either finite rational table: the batch vectors and
their decimal strings are frozen and independently reproduced.  It is,
however, direct evidence that the strings are execution-context-dependent
binary64 observations rather than canonical continuum coefficients.

**Required closure for a future continuum selector:** define a canonical
per-time coefficient evaluation protocol or, preferably, enclose the true
coefficient once with an outward interval that contains all admissible
roundoff/quadrature paths.  Do not use agreement with one frozen batching as
an interval certificate.

## 7. Adoption and gate decision

```text
finite rational LP definition                    = PASS
complete vertex enumeration                      = PASS, independently reconstructed
primary optimum                                  = PASS, exact
sequential lexicographic equivalence              = PASS
unrestricted rho / nonpositive HOLD              = PASS
exact payload and raw rationalized margins        = PASS
canonical replay                                  = BYTE-IDENTICAL
v1 F0 exact compatibility                         = FAIL AS EXPECTED / HOLD
explicit v2 pre-science rational-vertex amendment = GO AFTER P1-1 REPAIR
continuum coefficient feasibility                 = MISSING / HOLD
full-window B0 box-and-complement certificate      = MISSING / HOLD
positive-B F0/F1 execution                         = NOT AUTHORIZED
P0                                                = 0
P1                                                = 2
P2                                                = 1
```

**Final decision:** v2 should adopt the exact rational vertices, because the
amendment is explicit, pre-science for those exact controls, deterministic,
and independently reproduced.  It must adopt them only as finite-rational-
selector candidate controls and must first repair the stale raw-hex F0
instruction.  The adoption does not close the continuum feasibility or
full-window topology gates and does not authorize any positive-`B` run.
