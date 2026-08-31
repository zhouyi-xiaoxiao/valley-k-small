# Round 03, reviewer A: GIG derivation, normalization, geometry, and scope

Date: 2026-07-11

Verdict: **needs bounded revision; no B0 or B1, three B2 findings and one B3 clarification**

Audited working-tree base: `3531353a515160b09899199a9257e7455a654b22`

The encounter report and its evidence were untracked in an already dirty
working tree. The Git hash is therefore only a base commit. The principal
working-tree snapshots audited here were:

- manuscript: `924a45631baede9b580c8c3d6bcc1b49a88ea53287dba5b6aede35eda1c5a3ea`;
- `validate_gig_fold.py`: `71a5c4385bc5714f9075f0e0baddad032709ed565e92c08f6904158f977ee510`;
- `validate_multid_gig_design.py`: `f22edb908bd2216c3c029f41badc8b2f73c04a3b0c5d1617420ec5e53fc3abbc`;
- `gig_fold_summary.json`: `ecac31a16c4f6f98e30c8e8962fd5660b19efb90373b975b7e75cf28a315d125`;
- `multid_gig_design_summary.json`: `d33f9e81d09ac1ece49fcc4eb35e77d0c2594b272ea3aca02896ee82652cce2d`;
- Lean continuum/design modules: `ae23060be3166c392eab2d8a0a5af5dcd1d3a4adf2a8b912fd8a0c2161e538b4` and
  `03c68e6084162ee8640869f8bbbed6a4322b6e7327bf32dd3cf396ec6426de41`.

Severity follows `audits/README.md`: B0 blocks submission, B1 requires a
material revision, B2 is a bounded correction or required caveat, and B3 is
optional polish.

## Executive assessment

The exact GIG-family algebra survives independent falsification. Multiplying
the one-dimensional relative first-contact law by the \(d\)-dimensional centre
point density gives the declared power

\[
\nu=(d+3)/2,
\]

and the declared positive actions

\[
A=\frac{\ell^2}{4D_r}+\frac{|z-R_0|^2}{4D_c},\qquad
B=\frac{u^2}{4D_r}+\frac{|v_c|^2}{4D_c}.
\]

The Bessel normalization, positive mode root, \(B\downarrow0\) mode limit,
ballistic/diffusive limits, symmetric distance map, and inverse-height weight
algebra all check out. Independent 70-digit quadrature reproduced the saved
normalizers, and an independent extended derivative scan reproduced all
3/5/7 alternating roots in all 12 multidimensional GIG cases.

The manuscript also draws the most important scientific boundary correctly:
the product law is a free-space, narrow-patch screening model, not a
finite-patch reflected Doi theorem. The exponent is explicitly called
non-universal (`manuscript/encounter_modality_jcp.tex:605-607`), the multi-clock
construction is explicitly screening-only (`:1331-1344`), and the absence of
a mode-window remainder is a listed limitation (`:1372-1373`).

Three bounded corrections are nevertheless required. The reported CTMC
comparison modes are sampled on a coarse time grid rather than solved in
continuous time; the \(B=0\) normalization omits its condition \(\nu>1\); and
the catalyst-distance rule omits the feasibility condition that the prescribed
action exceed the irreducible relative action. None changes the validated
fixed parameter family or the central screening conclusion.

## Findings

### F1 — B2: the quoted CTMC modes and the 17.2% early error come from a 0.5-time-unit sampling grid

The manuscript reports GIG/CTMC comparisons `26.50 versus 32.0` and
`180.19 versus 196.0`, with errors `17.2%` and `8.1%`
(`manuscript/encounter_modality_jcp.tex:818-824`). The saved summary records the
same values under `canonical_channel_comparison`.

The generator does not locate these CTMC modes from the exact channel
derivative. It propagates the semigroup only at

```text
canonical_times = np.linspace(0.0, 500.0, 1001)
```

and stores the time of the largest sampled peak
(`code/validate_gig_fold.py:902-919`). Thus the nominal CTMC time resolution is
`0.5`.

I independently solved

\[
\alpha e^{Tt}T b_j=0
\]

for each channel using Brent bracketing, and cross-checked the results by
bounded optimization of \(-\alpha e^{Tt}b_j\). The continuous-time modes are

```text
near: 32.1534061543058,  f'' = -3.8161485075e-6
far:  196.145870006970,  f'' = -7.7286366068e-7
```

The derivative-root and optimizer estimates agreed to `1.1e-7` and `2.7e-6`,
respectively. Against these modes, the screening errors are

```text
early: 0.1759202035 = 17.5920%  -> 17.6% at one decimal
late:  0.0813479529 =  8.1348%  ->  8.1% at one decimal
```

The late rounded percentage is unchanged, but the early one is not. This is a
bounded numerical-reporting error, not a failure of the CTMC fold or GIG mode
formula.

**Required resolution.** Compute canonical channel modes by roots of the
analytic semigroup derivative, verify negative second derivative, regenerate
the summary/manifest/figure if they encode these values, update manuscript
lines 818--824, and add a regression that prevents a sampled grid maximum from
being labelled the CTMC mode.

### F2 — B2: the \(B=0\) normalization is stated without the necessary condition \(\nu>1\)

The manuscript says, without qualification,

\[
Z=A^{1-\nu}\Gamma(\nu-1)\quad(B=0)
\]

and then calls the normalization exact for the GIG family
(`manuscript/encounter_modality_jcp.tex:622-625`). Substitution \(y=A/t\)
gives

\[
\int_0^\infty t^{-\nu}e^{-A/t}\,dt
=A^{1-\nu}\int_0^\infty y^{\nu-2}e^{-y}\,dy,
\]

which is finite only for \(\nu>1\). At \(\nu=1\), direct partial integrals over
`[1,R]` grew from `1.17375` at `R=10` to `7.89128` at `R=10000`, consistent
with logarithmic divergence.

The repository already knows the correct condition: the theory note states
`nu>1` (`notes/gig_fold_derivation.md:71-83`), and `GIGChannel` rejects
`B=0, nu<=1` (`code/validate_gig_fold.py:53-64`). In the physical construction
\(\nu=(d+3)/2\ge2\), so no saved case is affected.

**Required resolution.** Add `for \(\nu>1\)` to the manuscript's \(B=0\)
normalization. Keep the mode statement separate: \(A/\nu\) is the positive
stationary mode for \(\nu>0\), but it is not the mode of a normalized density
when normalization fails.

### F3 — B2: the spatial design rule omits the minimum-action/real-distance condition

At the GIG level, choosing

\[
A_j=B m_j^2+p m_j
\]

does place a stationary mode at any \(m_j>0\). A physical catalyst location in
the stated reference geometry has the additional constraint

\[
A_j=A_{\rm rel}+\frac{|z_j-R_0|^2}{4D_c}\ge A_{\rm rel},\qquad
A_{\rm rel}=\frac{\ell^2}{4D_r}=\frac14.
\]

Hence the displayed distance

\[
|z_j-R_0|=\sqrt{Bm_j^2+p m_j-\tfrac14}
\]

is real only if

\[
Bm_j^2+p m_j\ge\tfrac14.
\]

The manuscript presents the prescription and distance map without this domain
condition (`manuscript/encounter_modality_jcp.tex:1303-1321`), and the theory
note first says “any desired” positive mode and then prints the square root
(`notes/multid_gig_channel_design.md:41-49,59-79`). The validator likewise
takes `np.sqrt(a - RELATIVE_ACTION)` without a guard
(`code/validate_multid_gig_design.py:44-48,60-76`). By contrast, the Lean
square-root theorem correctly assumes `a >= 1/4`
(`FormalLean/EncounterDesign.lean:88-94`).

For the reference \(B=0.01\), the minimum feasible mode is

\[
m_{\min}=\frac{-p+\sqrt{p^2+4B(1/4)}}{2B},
\]

equal to `0.12492197`, `0.09996003`, `0.08331020`, and `0.07141400` for
`d=1,2,3,4`. All validated targets are at least `1`, so every saved distance is
real and this finding does not alter the 12-case result.

**Required resolution.** State the feasibility inequality beside the distance
map, give the general condition \(A_j\ge \ell^2/(4D_r)\), and make the validator
fail explicitly when it is violated rather than returning `nan`.

### F4 — B3: make the time-independent drift cross factor explicit

Expanding the two Gaussian actions gives

\[
-\frac{(\ell-ut)^2}{4D_rt}
-\frac{|\delta-v_ct|^2}{4D_ct}
=-\frac At-Bt
+\frac{\ell u}{2D_r}+\frac{\delta\!\cdot v_c}{2D_c},
\qquad \delta=z-R_0.
\]

Thus the signs and the squared contributions to \(A\) and \(B\) are correct.
The last two terms are time-independent and cancel when an individual channel
is normalized, but they are channel- and direction-dependent amplitudes. They
must be absorbed into physical splitting weights, not silently discarded when
mapping catalyst strengths. The note says “up to a time-independent capture
factor” (`notes/gig_fold_derivation.md:45-55`), and the manuscript already says
that physical realization of the designed weights remains open
(`manuscript/encounter_modality_jcp.tex:1331-1335`), so this is clarity rather
than a scientific defect.

**Suggested resolution.** Add the expanded constant factor after
Eq. `gig-parameters` and state explicitly that \(g_j\) is the normalized
conditional shape while the constant contributes to its splitting amplitude.

## Checks that passed

| Topic | Independent falsification and result |
|---|---|
| Power, action, and drift signs | Direct expansion of the relative IG and centre Gaussian gives \(t^{-3/2}t^{-d/2}=t^{-(d+3)/2}\), the printed \(A,B>0\), and only the time-independent cross factor described in F4. The sign convention is consistent with initial relative position \(-\ell\) and positive closing drift \(u\). |
| Bessel normalization | At 70 digits, direct improper quadrature and \(2(A/B)^{(1-\nu)/2}K_{1-\nu}(2\sqrt{AB})\) agreed to below `2e-67` for the early channel, late channel, the `d=1,m=1` design, and the extreme `d=4,m=1000` design. Reproduced normalizers include `0.0008507229892408168184`, `0.0008302110402645749938`, and `1.0371613884697901e-18`. |
| Mode equation | The log derivative \(A/t^2-\nu/t-B\) gives \(Bt^2+\nu t-A=0\). For \(A,B,\nu>0\), the numerator \(A-\nu t-Bt^2\) is strictly decreasing on positive time, so the printed positive root is the unique global mode. High-precision score residuals were below `6e-72`; the early and late modes reproduce `26.49697240017697` and `180.18980501403161`. |
| \(B=0\) and asymptotics | For three cases with \(\nu>1\), direct \(B=0\) quadrature reproduced \(A^{1-\nu}\Gamma(\nu-1)\) to at worst `2.1e-15`. At `B=1e-10`, the mode was within `1.27e-10` relative of \(A/\nu\). For the boundary IG, \(t_m/d\to1/v\), while at zero drift \(t_m/d^2=1/(6D)\) exactly. |
| Canonical geometry | Recomputed \(D_r=0.45\), \(D_c=0.077777\ldots\), \(u=0.15\), and \(v_c=0.093333\ldots\). These give early `(A,B,nu)=(81.4285714,0.0405,2)` and late `(562.5,0.009,1.5)`, matching `gig_channel_parameters.csv` and `geometry_to_channels` (`validate_gig_fold.py:110-165`). |
| Multidimensional action and distance | For every saved row, \(A_j-(Bm_j^2+pm_j)=0\), \(A_j/m_j^2-p/m_j-B=0\) to at most `2.14e-16`, and \(|z_j-R_0|^2-(A_j-1/4)\) was at most `1.82e-12` in binary64. The symmetric diffusion map and its feasibility hypothesis are also encoded in Lean (`EncounterDesign.lean:58-94`). |
| Inverse-height weights | In all 12 cases, weights summed to one and the spread of \(w_jg_j(m_j)\) was at most `6.94e-18`. The algebra is correctly proved for positive heights in `EncounterDesign.lean:98-163`. This equalizes isolated weighted peaks, not the exact maxima of an overlapping physical mixture. |
| Multimode numerical family | An independently implemented, log-scaled derivative scan on 500,001 points over `[1e-5,1e7]` reproduced exactly 3, 5, and 7 roots with alternating curvature for 2, 3, and 4 channels in every `d=1..4` case. It reproduced the minimum peak/valley ratio `1.996154388507492` and maximum scaled residual about `2.28e-13`, supporting the weaker manuscript gates `>1.9` and `<2e-10`. |
| Focused regression tests | `uv run pytest -q tests/test_encounter_gig_fold.py tests/test_encounter_multid_gig_design.py` completed with `7 passed`. |
| Lean scope and hygiene | `EncounterContinuum.lean:205-303` proves the log derivative, quadratic stationary equation, positive stationary root, and \(B=0\) stationary root; `EncounterDesign.lean` proves prescribed-action, distance, and inverse-height identities. The modules explicitly exclude GIG normalization, PDE validity, remainder bounds, and mixture root persistence (`EncounterContinuum.lean:18-21`; `EncounterDesign.lean:15-19`). Stored axiom reports list only standard Lean/mathlib axioms, and no `sorry`, `admit`, or `native_decide` occurs in these two sources. I did not perform a fresh Lean build because `lake` was not installed in this execution environment. |

## Commands and executable checks

Commands were run from the repository root.

```text
uv run pytest -q \
  tests/test_encounter_gig_fold.py \
  tests/test_encounter_multid_gig_design.py
# 7 passed

PYTHONPATH=packages/vkcore/src uv run python - <<'PY'
# Imported validate_gig_fold.py, formed alpha exp(Tt) b_j and
# alpha exp(Tt) T b_j, solved each channel derivative with brentq,
# and cross-checked by minimize_scalar.
PY

uv run python - <<'PY'
# Used mpmath at 70 digits to compare improper quadrature with the
# Bessel and B=0 gamma normalizers, check mode scores, and audit the
# B -> 0, large-distance ballistic, and zero-drift diffusive limits.
PY

uv run python - <<'PY'
# Independently read multid_gig_design_parameters.csv, reconstructed
# normalized channels and mixture derivatives, scanned 500001 log points
# on [1e-5,1e7], refined every sign change, and checked weights, distances,
# curvature alternation, root residuals, and peak/valley ratios.
PY

rg -n "sorry|admit|native_decide" \
  research/reports/ring_lazy_jump_ext_rev2/code/formal_lean/FormalLean/EncounterContinuum.lean \
  research/reports/ring_lazy_jump_ext_rev2/code/formal_lean/FormalLean/EncounterDesign.lean
# no matches
```

## Inspected evidence

- `manuscript/encounter_modality_jcp.tex`, especially the GIG derivation,
  canonical comparison, multidimensional design, limitations, and formal-scope
  paragraphs;
- `notes/gig_fold_derivation.md` and `notes/multid_gig_channel_design.md`;
- `code/validate_gig_fold.py` and `code/validate_multid_gig_design.py`;
- `gig_channel_parameters.csv`, `gig_drift_scaling.csv`,
  `gig_fold_summary.json`, all multidimensional parameter/root/case tables,
  `multid_gig_design_summary.json`, and their manifests;
- `tests/test_encounter_gig_fold.py` and
  `tests/test_encounter_multid_gig_design.py`;
- `FormalLean/EncounterContinuum.lean`, `FormalLean/EncounterDesign.lean`, the
  formal README, and both saved axiom-hygiene reports.

## Not-certified boundary

This review certifies the GIG **family algebra** and the stated finite numerical
family only. It does not certify:

1. that \(p=(d+3)/2\) is the universal exponent of a physical \(d\)-dimensional
   encounter process; it follows here from a one-dimensional normal/closing
   first-hit factor times a \(d\)-dimensional centre point-density factor;
2. a finite-radius, finite-patch, bounded-domain, or reflected Doi derivation of
   any GIG channel, or a uniform error bound on a window containing its mode;
3. that tangential contact integration, centre-patch averaging, image paths,
   anisotropy, or the regular Green part leave \(p,A,B\) unchanged;
4. a physical construction of the inverse-height splitting weights using
   patch volumes and intrinsic reactivities;
5. an interval-arithmetic proof that no tangential/even-multiplicity derivative
   roots exist outside the numerically isolated roots; or
6. persistence of the three- and four-mode GIG mixtures in a bounded
   finite-radius encounter model.

Those exclusions agree with the current manuscript and artifact `not_claimed`
fields. Within that boundary, I found no B0/B1 error in the exponent, actions,
normalization for its valid parameter domain, mode roots, geometry mapping of
the validated cases, inverse-height weights, or multimode numerical evidence.
