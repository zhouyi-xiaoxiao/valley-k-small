# Source-bound genuine joint refinement families: v2

Date: 2026-07-17

Status: **CONTROL-FREE IDEAL GEOMETRIC AUTHORITY / TWELVE GENUINE
REFINEMENT SEQUENCES DEFINED / MODEL-SPECIFIC OPERATOR PREMISES OPEN /
COMPLETE C0-C3 FALSE / PRODUCTION ACCEPTANCE AND RELEASE FALSE**

## 0. Purpose and exact source boundary

The twelve rows in
`artifacts/data/physical_configuration_family_control_free_v1.json` are
finite mesh anchors.  They are not, by themselves, an `h -> 0` family.  This
note gives each row a separate dyadic successor sequence indexed by
`n in N_0`.  Level `n=0` reproduces the source row's box, alignment, sizes,
and periodic shift exactly.  Every later level keeps that box, alignment,
and the control-free physical parameters fixed while refining all three axes.

The construction is tied to these exact pre-existing bytes:

| role | report-relative path | SHA-256 |
|---|---|---|
| finite configuration anchors | `artifacts/data/physical_configuration_family_control_free_v1.json` | `063913c7fbc2b706ba85a0e3f06005bad23a2292749817294cbf41f5cdce4084` |
| global reference density | `artifacts/data/continuum_c1_reference_density_source_v1.json` | `7b890d727ad0b229557de1841ae82befb8d8f83e79edc6b5348b277c3024e575` |
| ideal mass, flux, map, and gauge formulae | `artifacts/data/continuum_c1_ideal_formula_source_v1.json` | `f31b637b659483102d787da7263cd45c72829b3fce3df2ff9100066dec94c2be` |
| product/contact factorization | `artifacts/data/continuum_c1_factorization_source_v1.json` | `70cb49e63c496d489887c764c812671b03a7352d5752f6663c377734739a1dca` |
| Round-4 theorem note | `notes/continuum_c1_free_form_and_functional_bridge_candidate.md` | `17b987d5090618e5346f81217afed7e57daccf878d4b93b8402724b3e002a562` |
| Round-4 hash-specific audit | `audits/continuum_c1_refinement_functional_bridge_round4_20260717.md` | `6ccdcd76a4049e198d13ae45d86570c17d7876a4ef28de8fb3fed0ea1b513134` |
| Round-5 theorem note | `notes/continuum_c1_varying_space_resolvent_mosco_candidate.md` | `0b9728535ed0216bc00d5ccb911575dd30bb531422130b2f7e2502a046f134f1` |
| Round-5 hash-specific audit | `audits/continuum_c1_varying_space_resolvent_mosco_round5_20260717.md` | `9e1cacca6c9c40675f31acbe743bbeccc74aca29b6378a641e1613ae48e55287` |
| fixed-row anti-vacuity policy | `artifacts/data/continuum_c1_c2_fixed_row_anti_vacuity_policy_v1.json` | `c8b9f3aca2b3a516935eeb1fdfb2bf542ba0da2d12ae4c11581f6f1ee607f628` |
| fixed-row member specification | `artifacts/data/continuum_c1_c2_fixed_row_member_spec_v1.json` | `e2166e62ae2e5e67a8e3eb058fe4333f59192525ca5614939f417ba285d8d2ef` |

All numerical geometry below is exact rational arithmetic.  A hexadecimal
binary64 endpoint is interpreted as the exact dyadic rational represented by
those bytes; it is not rounded again through decimal text.

No result payload, concrete control vector, positive budget, production raw
interval array, or root certificate is an input.  This note defines ideal
geometric sequences.  It does not assert that the level-zero ideal mass,
rate, flux, gauge, map, or killing member is contained in a correlated
production interval member.

## 1. Twelve dyadic joint sequences

Fix one source row `f` and one axis `a`.  Let `s_{f,a}` be the source size.
The box endpoints and the alignment label are held fixed for all `n`.

For a cell-centred reflecting or periodic axis, define

\[
  s_{f,a}(n)=s_{f,a}2^n,\qquad
  N_{f,a}(n)=s_{f,a}2^n .
  \tag{1.1}
\]

For a vertex-centred reflecting-dual axis, the source has
`s_{f,a}-1` intervals and define

\[
  N_{f,a}(n)=(s_{f,a}-1)2^n,\qquad
  s_{f,a}(n)=N_{f,a}(n)+1 .
  \tag{1.2}
\]

Writing `w_{f,a}` for the fixed interval width or periodic length,

\[
  h_{f,a}(n)=\frac{w_{f,a}}{N_{f,a}(n)}
            =h_{f,a}(0)2^{-n}.
  \tag{1.3}
\]

The representative points, dual cells, ordinary cells, and periodic wrapped
segments are then exactly those prescribed by the alignment contracts in the
configuration source and by the Round-4 ideal formulae.

On a periodic base alignment, `sigma_{f,y}(n)=0`.  On a periodic half-shift
alignment,

\[
  \sigma_{f,y}(n)=\frac12h_{f,y}(n).
  \tag{1.4}
\]

Thus the two half-shift anchors have
`sigma(0)=1/256` because `W=1` and `s(0)=128`, exactly matching their source
rows.  The half-shift partitions need not be nested between successive
levels; nestedness is neither claimed nor needed for the geometric
vanishing-mesh statement.  Their torus cells remain translations of uniform
periodic cells.

The joint three-axis level is

\[
  \mathcal T_f(n)=
  \mathcal T_{f,M}(n)\mathbin{\times}
  \mathcal T_{f,R}(n)\mathbin{\times}
  \mathcal T_{f,Y}(n).
  \tag{1.5}
\]

Equations (1.1)--(1.5), together with each row's exact anchor data, specify
twelve infinite sequences rather than twelve isolated meshes.

## 2. Vanishing mesh and finite-family uniformity

For each row put

\[
  H_f(0)=\max_a h_{f,a}(0),\qquad
  H_f(n)=\max_a h_{f,a}(n).
\]

Equation (1.3) gives the exact identity

\[
  H_f(n)=H_f(0)2^{-n}\longrightarrow0.
  \tag{2.1}
\]

There are only twelve rows, so

\[
  H_*(0)=\max_{1\le f\le12}H_f(0)<\infty,\qquad
  \max_f H_f(n)=H_*(0)2^{-n}\longrightarrow0.
  \tag{2.2}
\]

This is genuine finite-family uniformity.  It is not an assertion of
uniformity over an undeclared continuum of boxes or controls.

All ordinary and periodic cell side lengths equal the corresponding
`h_{f,a}(n)`.  A reflecting-dual endpoint side has length
`h_{f,a}(n)/2`, and an interior dual side has length `h_{f,a}(n)`.
Consequently a tensor cell volume divided by
`h_M(n)h_R(n)h_Y(n)` lies in

\[
  \{1,\tfrac12,\tfrac14\};
  \tag{2.3}
\]

the lower value occurs only when both nonperiodic axes use endpoint dual
cells.  Within each row, all axis-spacing ratios are independent of `n`.
Taking a maximum over twelve rows gives a finite Cartesian side-aspect bound.
In the torus metric, a wrapped periodic cell has diameter at most its full
periodic width; its two-segment storage representation does not create a
degenerate physical cell.  These observations give a uniform
shape-regularity and diameter-to-zero certificate for the declared finite
family.

They do not prove uniform edge-consistency, map-defect, coercivity, resolvent,
Mosco, or evaluator constants.  Those analytic premises remain separate.

## 3. Fixed physics, global gauge, and product maps

Across every level of each row, freeze the reference-source values of
`particle_diffusion`, `ou_stiffness`, `ou_mean`, and `W`, and freeze the row's
two nonperiodic intervals.  The global reference density is the unrestricted
normalization

\[
 \pi(M,R,Y)=Z^{-1}
 \exp\!\left[
 -\frac{\gamma(M-\bar M)^2}{D}
 -\frac{\gamma R^2}{4D}
 \right],
 \qquad
 Z=\frac{2\pi D W}{\gamma}.
 \tag{3.1}
\]

Restriction to a finite box does not conditionally renormalize this density.
For ideal axis primitives,

\[
 \mu_i^a=\nu_i^a e^{-\Phi_a(x_i^a)}
 \quad(a=M,R),\qquad
 \mu_k^Y=\nu_k^Y ,
 \tag{3.2}
\]

define `S_a=sum_i mu_i^a`, the global box mass
`M_L=integral_{Omega_L} pi`, and

\[
 G_h=\frac{M_L}{S_M S_R S_Y},\qquad
 \pi_{h,ijk}=G_h\mu_i^M\mu_j^R\mu_k^Y.
 \tag{3.3}
\]

Hence, algebraically and at every level,

\[
 \sum_{ijk}\pi_{h,ijk}=M_L.
 \tag{3.4}
\]

Let `C_{ijk}` be the actual tensor cell, including dual half volumes and
wrapped periodic segments, and let

\[
 M^\pi_{ijk}=\int_{C_{ijk}}\pi\,dx,\qquad
 \rho_{ijk}=M^\pi_{ijk}/\pi_{h,ijk}.
 \tag{3.5}
\]

Then the Round-4/5 maps are defined on each level by

\[
 J_hv=\sum_{ijk}v_{ijk}{\bf1}_{C_{ijk}},\qquad
 (P_hu)_{ijk}=\pi_{h,ijk}^{-1}
 \int_{C_{ijk}}u\pi\,dx .
 \tag{3.6}
\]

Equations (3.3)--(3.6) fix the product/gauge/map objects to which the
abstract theorem notes refer.  The present successor does not independently
prove the required `rho -> 1`, edge-form, resolvent, or same-member production
premises.  In particular, exact formula definition is not production
containment.

## 4. Exact physical-volume killing averages: qualitative route

For one fixed bounded nonnegative field `V` on a row's fixed box, define

\[
 V_{h,ijk}
 =|C_{ijk}|^{-1}\int_{C_{ijk}}V(x)\,dx .
 \tag{4.1}
\]

This is the physical-volume average, not a `pi`-weighted average.  The
contact/profile factorization source provides a symbolic route for evaluating
(4.1), but it supplies no concrete control combination here.

The declared partitions are uniformly shape-regular and their maximum
diameter tends to zero by Section 2.  For continuous `V`, uniform continuity
therefore gives `J_hV_h -> V` uniformly.  For general
`V in L^p`, `1<=p<infinity`, approximate by continuous functions and use that
physical-cell averaging is an `L^p` contraction.  On each fixed box the
smooth positive density (3.1) is bounded above and below, so the same
conclusion holds in `L^p(pi dx)`.  Thus, for a fixed bounded `V`,

\[
 J_hV_h\longrightarrow V
 \quad\hbox{in }L^2(\pi dx),\qquad
 0\le J_hV_h\le\|V\|_\infty.
 \tag{4.2}
\]

Together with an independently established `rho_h -> 1`, (4.2) is exactly
the qualitative multiplier premise `K_h^{pc}=V_h/rho_h -> V` used in the
Round-4/5 bounded-killing argument.  This note supplies the genuine
geometric sequence and the qualitative averaging route.  It does not supply
a quantitative cut-cell rate, a concrete control-specific `V`, a production
application enclosure, or acceptance of the remaining free-form premises.

## 5. Anti-vacuity and level-zero production boundary

The fixed-row anti-vacuity policy explicitly records
`policy_predecessor_order_independently_sealed=false` and
`formal_production_bridge_accepted=false`.  It predates this successor and
cannot retrospectively seal an infinite refinement family or its level-zero
production relation.

Likewise, the fixed-row member specification explicitly records
`genuine_refinement_sequence_present=false` and
`production_bridge_accepted=false`.  This successor repairs only the first
absence for the ideal geometry by defining the twelve sequences.  It does not
mutate that historical file and does not repair the production bridge.

At `n=0`, exact equality of sizes, endpoints, alignments, and periodic shifts
is an equality to the configuration geometry source only.  A production
claim still requires a separately ordered, independent correlated receipt
showing that one common formula-defined member is contained simultaneously
in the saved mass/rate/flux/gauge/map/killing intervals.  Marginal interval
overlap, separate witnesses, or this geometric source cannot substitute for
that receipt.

## 6. Exact claim decision

This successor establishes only:

```text
twelve source-bound n in N_0 sequences        = DEFINED
n=0 exact configuration-geometry anchors      = VERIFIED BY CONSTRUCTION
maximum axis spacing -> 0                      = PROVED, EXACT DYADIC RATE
finite-12-family geometric uniformity          = PROVED
shape regularity / physical-volume route       = PROVED QUALITATIVELY
global ideal gauge and product-map definitions = BOUND TO FROZEN FORMULAE
```

It does not establish:

```text
accepted model-specific free-form estimates    = OPEN
production n=0 correlated containment          = OPEN
production same-member bridge                  = OPEN
concrete control or budget                      = ABSENT
concrete control-specific killing averages     = OPEN
quantitative cut-cell/evaluator rates           = OPEN
complete C0, C1, C2, or C3                     = FALSE
F0/F1/root transfer                            = FALSE
release or submission eligibility              = FALSE
```

The next admissible step is a new, independently ordered correlated
level-zero receipt followed by source-uniform analytic estimates on these
actual sequences.  The fixed finite set allows a maximum over twelve
row-specific constants only after each required constant has genuinely been
proved; finiteness alone does not manufacture those estimates.
