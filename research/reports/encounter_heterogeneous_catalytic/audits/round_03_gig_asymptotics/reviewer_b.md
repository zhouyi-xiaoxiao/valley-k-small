# Round 03 reviewer B — GIG asymptotics and multidimensional screening

Date: 2026-07-11  
Verdict: **needs revision; no B0 or B1, four B2 findings**  
Audited Git base: `3531353a515160b09899199a9257e7455a654b22`

Working-tree snapshot hashes:

- `manuscript/encounter_modality_jcp.tex`:
  `924a45631baede9b580c8c3d6bcc1b49a88ea53287dba5b6aede35eda1c5a3ea`;
- `notes/continuum_multid_theory.md`:
  `160c03ac5320c152d74a5050617f13efa4053a14ef01906ba7e96d8852b15148`;
- `notes/gig_fold_derivation.md`:
  `b5acde2c6e0acade320a3e90b860432dac6409b946ba4b42ad80c184aaf0f82f`;
- `notes/multid_gig_channel_design.md`:
  `7881e6392c5aa2ab18d62dd3ac08bd4b5fd3e3f852104c84197fe4a86cc925ae`;
- `code/validate_gig_fold.py`:
  `71a5c4385bc5714f9075f0e0baddad032709ed565e92c08f6904158f977ee510`;
- `code/validate_multid_gig_design.py`:
  `f22edb908bd2216c3c029f41badc8b2f73c04a3b0c5d1617420ec5e53fc3abbc`;
- `artifacts/data/gig_fold_summary.json`:
  `ecac31a16c4f6f98e30c8e8962fd5660b19efb90373b975b7e75cf28a315d125`;
- `artifacts/data/multid_gig_design_summary.json`:
  `d33f9e81d09ac1ece49fcc4eb35e77d0c2594b272ea3aca02896ee82652cce2d`.

The Git hash is a base commit rather than a complete immutable snapshot because
the audited files are in an already dirty working tree. I did not read or rely
on Reviewer A's Round 03 report. I changed no scientific source, test, artifact,
notebook, pipeline, or manifest; this file is my only write.

## Executive assessment

The analytical GIG chain is sound. With the manuscript's convention
`r=X1-X2`, walker 1 initially to the left means `r(0)=-ell`; therefore
`dr=u dt+sqrt(2 Dr)dW` with `u=v1-v2>0` and the factor
`(ell-u t)^2` have consistent signs. Multiplying the relative first-contact
density by the free centre heat kernel gives the displayed power, action, and
drift penalty. The omitted cross terms are independent of time and cancel from
a normalized conditional channel. Independent quadrature verified both the
Bessel-\(K\) normalization and its `B=0` limit, and an independent log-domain
reconstruction reproduced every saved simple root and every designed weight in
the 12 declared `d=1,...,4` cases.

The four revisions concern the strength and numerical domain of those results,
not the central mechanism. First, the code evaluates the cancellation-prone
mode formula even though the manuscript displays its stable equivalent, and it
evaluates the Bessel normalization outside log space; small `B` and large `A`
produce zeros, infinities, or NaNs. Second, the spatial clock construction needs
an explicit feasibility floor set by the irreducible relative action. Third,
the 12-case calculation isolates sign-changing roots but cannot support the
manuscript's unqualified word "exactly" while its own summary excludes an
interval certificate against tangential roots. Fourth, the canonical CTMC
comparison uses a `dt=0.5` sampled maximum despite exact semigroup derivatives
being available; refining the maxima changes the early relative error from
`17.2%` to `17.6%`.

Finite-patch Gaussian-ball integrations were also used adversarially. They show
that a patch radius comparable with the catalyst distance can move an isolated
clock substantially. This does not contradict the paper because finite-patch
realization and a mode-window remainder are explicitly excluded; those
limitations must remain.

## Findings

### B2-01 — The implementation does not use the manuscript's stable mode form or a stable log normalization

**Anchors**

- `manuscript/encounter_modality_jcp.tex:606-620` gives the correct Bessel-
  \(K\) normalizer, displays the rationalized stable mode as the second equality,
  and states the `B=0` limit.
- `code/validate_gig_fold.py:61-79` evaluates raw `kv`, raw powers, and the
  subtractive first mode expression.
- `code/validate_multid_gig_design.py:56-68,80-90` likewise evaluates the raw
  normalizer and then exponentiates/divides in ordinary floating point.
- `tests/test_encounter_gig_fold.py:35-54` checks only the three moderate
  canonical channels. The multidimensional test fixes `B=0.01`; neither test
  contains a small-`B` continuity or large-action stress case.

For `A=1` and `nu=3.5`, direct evaluation gave:

| `B` | subtractive code mode | stable mode | relative error |
|---:|---:|---:|---:|
| `1e-8` | `0.285714274461668` | `0.285714285481050` | `3.86e-8` |
| `1e-12` | `0.285771406538515` | `0.285714285714262` | `2.00e-4` |
| `1e-16` | `0` | `0.285714285714286` | `1` |

The true `B -> 0` normalizer in this example is
`Gamma(2.5)=1.329340388179137`. The raw implementation returns `inf` at
`B=1e-250` and `nan` at `B=1e-300`. At the other extreme,
`A=1e8`, `B=0.01`, and `nu=3.5` give Bessel argument `2000`; raw `kv` makes
`Z=0`, even though the exponentially scaled `kve` value is finite
(`0.0280670145`). Density and weight calculations can consequently become
`0/0` or overflow.

No saved result is numerically invalidated by this test: the declared cases
have `B=0.009`, `0.01`, or `0.0405` and moderate Bessel arguments. This is why
the finding is B2 rather than B1. It does, however, invalidate an unrestricted
use of the code in precisely the small-drift and large-distance regimes that a
general screening construction should explore.

**Required resolution**

1. Evaluate every positive-`B` mode as
   `2*A/(nu + sqrt(nu**2 + 4*A*B))`, retaining the exact `B=0` branch.
2. Compute
   `log Z = log(2) + (1-nu)/2*(log A-log B) + log(kve(1-nu,x)) - x`
   for large/moderate `x=2*sqrt(A*B)`, with a small-`x` asymptotic branch that
   joins continuously to `A**(1-nu)*Gamma(nu-1)`.
3. Evaluate densities, inverse-height weights, mixtures, and derivative
   residuals in log/signed-log-sum-exp form.
4. Add stress tests spanning `B=0`, `B` below machine-epsilon scale, and Bessel
   arguments above the raw-`kv` underflow threshold.

### B2-02 — The catalyst-distance rule omits the physical feasibility condition

**Anchors**

- `manuscript/encounter_modality_jcp.tex:1300-1317` maps a prescribed isolated
  mode to `A_j=B m_j^2+p m_j` and then to the reference distance.
- `notes/multid_gig_channel_design.md:21-49` calls the first rule valid for any
  desired positive isolated mode, while lines `51-79` make the physical map.
- `code/validate_multid_gig_design.py:60-75` takes
  `sqrt(a-RELATIVE_ACTION)` without checking the radicand.

The GIG clock equation alone permits every `m>0`, but a catalyst location does
not. In general,

\[
A=A_{\rm rel}+\frac{|z-R_0|^2}{4D_c},\qquad
A_{\rm rel}=\frac{\ell^2}{4D_r},
\]

so the actual spatial construction is

\[
|z-R_0|=
\sqrt{4D_c\left(Bm^2+pm-A_{\rm rel}\right)},
\]

and it is real only if

\[
Bm^2+pm\geq A_{\rm rel}.
\]

Equivalently,

\[
m\geq m_{\min}=
\frac{\sqrt{p^2+4BA_{\rm rel}}-p}{2B}\quad(B>0),
\qquad m_{\min}=\frac{A_{\rm rel}}p\quad(B=0).
\]

For the reference family this gives minimum feasible modes
`0.12492197`, `0.09996003`, `0.08331020`, and `0.07141400` for
`d=1,2,3,4`, respectively. Calling `construction(1,(0.01,))` would therefore
produce a NaN distance, not a catalyst. All archived targets are safe: their
smallest radicand is `1.76`, and the 36 saved rows satisfy the two algebraic
identities to `1.82e-12` absolute error.

**Required resolution:** state the feasibility inequality next to the general
distance rule, give the corresponding minimum-clock formula, and make the code
raise a clear error for a negative radicand. Distinguish an algebraically valid
GIG mode from a mode realizable by moving a catalyst while keeping
`ell,Dr,Dc,B` fixed.

### B2-03 — A sign-change scan does not certify the manuscript's unqualified exact root count

**Anchors**

- `code/validate_multid_gig_design.py:98-135` scans 240,000 logarithmic points,
  brackets sign changes, and checks only the derivative signs at the two finite
  endpoints. It explicitly does not use its near-zero diagnostic as an
  absence-of-roots proof.
- `notes/multid_gig_channel_design.md:129-146` accurately calls the result
  floating-point isolation rather than an interval proof against tangencies.
- `artifacts/data/multid_gig_design_summary.json:144-152` explicitly lists
  "interval-certified absence of tangential derivative roots" as not claimed.
- Nevertheless, `manuscript/encounter_modality_jcp.tex:1320-1326` says that
  each case has **exactly** `2m-1` critical points without carrying that
  qualification.

I independently reconstructed normalized components and inverse-height weights
in log space, scanned 300,000 points per case, and refined the scaled derivative
`t f'(t)/f(t)`. The root counts were

```text
[3,5,7, 3,5,7, 3,5,7, 3,5,7]
```

for dimensions 1 through 4. The largest difference from a saved root was
`9.10e-13`, and the largest relative spread among the designed weighted
isolated peak heights was `9.12e-16`. Thus every reported sign-changing simple
root is real and correctly classified. The logical gap is only exhaustiveness:
an even-multiplicity zero can touch the axis without changing sign, and a dense
floating-point grid cannot exclude it.

**Required resolution:** either change the manuscript to "the scan found
`2m-1` alternating simple roots in every tested case; no additional tangential
root is interval-certified absent", or add an exhaustive certificate. A clean
certificate would bound the scaled derivative on an interval partition and use
analytic positive/negative signs in the `t -> 0` and `t -> infinity` tails.
A total-positivity/root-count theorem for the common-`p`, common-`B` family
would be even stronger.

### B2-04 — The canonical CTMC error comparison uses sampled, not derivative-rooted, channel modes

**Anchors**

- `code/validate_gig_fold.py:902-919` samples `0,...,500` at 1001 points and
  stores the grid point selected by `find_peaks`; hence `dt=0.5`.
- `artifacts/data/gig_fold_summary.json:2-10` records `32.0`, `196.0`, and the
  resulting relative errors.
- `manuscript/encounter_modality_jcp.tex:818-824` reports those numbers as the
  canonical CTMC comparison, even though exact matrix-exponential channel
  derivatives are already available elsewhere in the same script.

I rooted

\[
f_j'(t)=\alpha e^{Tt}T b_j
\]

directly for the canonical `theta=0` model. The maxima are

| channel | sampled time | derivative-rooted time | second derivative |
|---|---:|---:|---:|
| near | `32.0` | `32.15340615430594` | `-3.81615e-6` |
| far | `196.0` | `196.14587000697063` | `-7.72864e-7` |

The GIG predictions remain `26.49697240017697` and
`180.18980501403163`. Relative to the refined CTMC modes, the errors are
`17.5920%` and `8.1348%`; the manuscript's sampled values give `17.1970%` and
`8.0664%`. The qualitative screening assessment is unchanged, the late value
still rounds to `8.1%`, and the exact finite-CTMC fold at `t=37.0749...` is not
affected. The early quoted error should, however, be `17.6%`, not `17.2%`, if
the comparison is presented without a grid uncertainty.

**Required resolution:** locate each channel maximum from its analytical
semigroup derivative, save the derivative residual and curvature, update the
summary/test/manuscript numbers, and reserve sampled grids for plotting. The
alternative is to label the modes as `dt=0.5` estimates and attach a sampling
error bound.

## Independent checks that passed

1. **Relative first-contact convention and drift sign.** The manuscript defines
   `r=X1-X2` at lines `312-315`. In the stated closing geometry the initial
   value is `-ell`, so positive `u=v1-v2` drives it toward zero. The density
   `ell/sqrt(4 pi Dr t^3) exp[-(ell-u t)^2/(4 Dr t)]` is therefore correct and
   integrates to one for `u>=0`. Adding `r(0)=-ell` explicitly near line 574
   would remove an avoidable reader ambiguity but is not a sign error.
2. **Centre heat kernel, multiplication, and constants.** With
   `delta=z-R0`, expansion gives time-independent multiplier
   `exp[ell*u/(2Dr)+delta.vc/(2Dc)]` and time-dependent terms
   `exp[-A/t-Bt]` with exactly the displayed `A` and `B`. The multiplier cancels
   from a normalized conditional channel but belongs to a physical splitting
   weight. The paper correctly leaves physical realization of designed weights
   open.
3. **Units.** `A` has units of time, `B` inverse time, `AB` is dimensionless,
   and `p` is dimensionless. `Z` has units `time^(1-p)`, so normalized `g` has
   density units `1/time`. The general distance formula above has length units.
4. **Bessel normalization and zero-drift limit.** Direct quadrature agreed with
   the formula to relative errors `1.27e-16` and `1.31e-16` for the canonical
   early and late channels. For `A=3.7,B=0,p=2.5`, quadrature gave
   `0.1245209297069245` versus the formula's
   `0.1245209297069246` (`8.92e-16` relative error). The mode equation
   `Bt^2+pt-A=0`, stable expression, and limit `A/p` are exact.
5. **Fixed-shape fold algebra.** Factoring the positive product `g1*g2` out of
   the determinant produces
   `a1*(a2^2+b2)-a2*(a1^2+b1)`. After clearing powers of time, its degree-six
   polynomial has precisely two positive real roots,
   `28.041093744754254...` and `157.527847347135856...`; the other roots are
   two negative reals and one complex-conjugate pair. Both positive roots give
   the archived admissible weights `3.672348776e-5` and `0.8780596892`.
6. **Reference geometry, distances, and weights.** The CTMC-to-Brownian map
   `D_i=q_i/2`, `v_i=q_i*bias_i` reproduces
   `Dr=0.45`, `Dc=0.077777...`, `u=0.15`, and `vc=0.093333...`, then all saved
   canonical `A`, `B`, and GIG modes. Across all 36 multidimensional parameter
   rows, the target-mode equation and distance equation pass to `1.82e-12`, all
   weights are positive and sum to one, and inverse isolated heights equalize
   weighted isolated peaks to `9.12e-16` relative spread.
7. **Declared 12-case modality result.** An independent log-domain calculation
   reproduced all 60 saved critical points, their alternating signs, and their
   reported root locations. This validates the detected simple roots and mode
   counts subject to B2-03's explicitly limited exhaustiveness.
8. **Focused tests.** The following read-only run completed `7 passed`:

   ```text
   PYTHONDONTWRITEBYTECODE=1 uv run --no-sync pytest -q \
     -p no:cacheprovider \
     tests/test_encounter_gig_fold.py \
     tests/test_encounter_multid_gig_design.py
   ```

## Adversarial finite-patch check and claim boundary

I replaced point evaluation of the centre heat kernel by the exact probability
that an isotropic Gaussian centre lies inside a radius-`rho` ball. For the
reference `Dr=1`, `Dc=1/4`, `ell=1`, `u=0`, and `|vc|=0.1` family, multiplying
that probability by the relative first-contact density gives the following
isolated modes:

| `d` | target | `rho=.05` | `rho=.2` | `rho=.5` | `rho=1` | `rho=2` |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 1 | 0.99773 | 0.96323 | 0.76056 | 0.28866 | 0.16390 |
| 1 | 10 | 9.99792 | 9.96673 | 9.78984 | 9.12621 | 6.05678 |
| 4 | 1 | 0.99902 | 0.98417 | 0.89883 | 0.58696 | 0.14605 |
| 4 | 10 | 9.99911 | 9.98574 | 9.91048 | 9.63629 | 8.45271 |

This is an adversarial width test, not a Doi solve: it retains independent free
relative/centre motion and simply integrates the centre factor over a finite
ball. It confirms that the point-patch clock is recovered as `rho -> 0` and
also falsifies any width-independent extrapolation. The manuscript already
calls the exponent a narrow-patch screening value at lines `602-604`, excludes
finite-patch averaging at `1328-1332`, and states the missing mode-window
remainder at `1370-1373`. No finite-width physical conclusion is therefore
contradicted. These caveats should not be weakened.

## Claims explicitly not certified by this review

- No global GIG law, uniform mode-window remainder, or reflected-image error
  bound is certified.
- `p=(d+3)/2` is not certified as a universal exponent for a full finite-radius
  `d`-dimensional encounter. The paper correctly notes that relative-surface
  flux, tangential integration, and patch averaging can change the power.
- No bounded-domain continuum two-, three-, or four-mode theorem follows from
  the free-space construction.
- The designed abstract weights are not certified as splitting probabilities
  realizable by finite patches and intrinsic rates.
- Absence of unobserved even-multiplicity derivative roots remains uncertified
  unless B2-03 is resolved by interval bounds or a root-count theorem.
- The finite-CTMC fold is exact only for the declared finite model; this review
  does not promote it to a lattice-to-continuum fold.

## Executable audit checks

The focused test command is given above. The numerical checks were independent
one-off Python evaluations with bytecode disabled. Their essential executable
forms were:

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python - <<'PY'
import numpy as np
from scipy.special import kv, kve
A=1.; nu=3.5
for B in (1e-8,1e-12,1e-16,1e-250,1e-300):
    unstable=(-nu+np.sqrt(nu*nu+4*A*B))/(2*B)
    stable=2*A/(nu+np.sqrt(nu*nu+4*A*B))
    with np.errstate(all='ignore'):
        Z=2*(A/B)**((1-nu)/2)*kv(1-nu,2*np.sqrt(A*B))
    print(B,unstable,stable,Z)
print('large-A raw/scaled',kv(-2.5,2000.),kve(-2.5,2000.))
PY
```

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python - <<'PY'
import importlib.util, sys
from pathlib import Path
from scipy.optimize import brentq
from scipy.sparse.linalg import expm_multiply
p=Path('research/reports/encounter_heterogeneous_catalytic/code/validate_gig_fold.py')
s=importlib.util.spec_from_file_location('gig_audit',p)
m=importlib.util.module_from_spec(s); sys.modules[s.name]=m; s.loader.exec_module(m)
model=m.physical_ctmc(0.0)
def derivative(t,j,order):
    state=expm_multiply(model.killed_generator.T*t,model.initial)
    observable=model.channel_rates[:,j].copy()
    for _ in range(order): observable=model.killed_generator@observable
    return float(state@observable)
for j,bracket in enumerate(((20.,50.),(150.,250.))):
    root=brentq(lambda t: derivative(t,j,1),*bracket,xtol=1e-12)
    print(root,derivative(root,j,2))
PY
```

For root reconstruction I used
`R(t)=t*f'(t)/f(t)`, log-Bessel normalization via `kve`, signed log-sum-exp,
a 300,000-point log grid, and Brent refinement. For the finite-patch check I
used `scipy.stats.ncx2.logcdf(rho**2/(2*Dc*t),d,nc)` with
`nc=|z-R0-vc*t|**2/(2*Dc*t)` and optimized the product with the relative
first-contact density in log time. These formulas specify the independent
checks without creating another untracked scientific artifact.

## Submission gate

Round 03 has no GIG-algebra or mechanism-level B0/B1 blocker. Before using the
construction as a numerically general design tool, resolve B2-01 and B2-02.
Before retaining the manuscript's exact root-count wording and quantitative
canonical error, resolve B2-03 and B2-04. The free-space/narrow-patch,
finite-state/continuum, and abstract-weight/physical-weight boundaries must
remain explicit.
