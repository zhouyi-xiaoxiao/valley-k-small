# Round 01 reviewer B — model, units, and numerical conventions

## Verdict

**FAIL / submission blocked.** The principal reflecting-2D artifacts do not
implement the encounter-centre coordinate defined in the manuscript. This is
an identity-of-model error, not a plotting or tolerance issue. I assign one
`B0` and two `B1` findings. The row-vector, Kronecker-product, transpose,
channel-flux, mass-balance, and fold-derivative orientations survived the
independent checks below. This review changed no scientific source or artifact.

## Findings

### B0-01 — 2D code uses an arithmetic midpoint, not the declared diffusivity-weighted centre

**Claim/model anchors**

- `manuscript/encounter_modality_jcp.tex:250-256` defines every catalyst in the
  encounter-centre coordinate.
- `manuscript/encounter_modality_jcp.tex:277-330`, especially `288-290`, defines
  \(R=(D_2X_1+D_1X_2)/(D_1+D_2)\) and explains why it cancels mixed diffusion.
- `notes/continuum_multid_theory.md:66-143,151-164` derives the same coordinate
  and places Doi patches in that centre space.
- The abstract says “diffusivity-weighted encounter centre” at manuscript
  lines `52-54`.

**Implemented model**

- `packages/vkcore/src/vkcore/encounter2d.py:477-486` applies the finite-radius
  mask, then line `481` sets
  `centre = 0.5 * (first_position + coordinates[second_state])`.
- This equals the declared \(R\) only for \(D_1=D_2\). All headline reflecting
  2D families use \(D_1=0.0025\), \(D_2=0.0008\); see
  `validate_2d_matched_homogeneous.py:55-63` and
  `validate_2d_matched_fold.py:59-67`.

**Reproducible mask falsification**

I rebuilt the same closed node masks twice, changing only the centre formula.
Entries are `(arithmetic count, weighted count, symmetric difference / union)`.

| family/grid | near patch | far patch |
|---|---:|---:|
| fold, `11x7` | `(34, 32, 16.67%)` | `(40, 40, 9.52%)` |
| fold, `13x9` | `(109, 117, 22.05%)` | `(137, 131, 23.68%)` |
| principal endpoint, `13x9` | `(55, 53, 22.95%)` | `(63, 61, 14.93%)` |

Equal counts do not imply equal support: even the `11x7` far masks differ on
9.52% of their union.

I also repeated the fold construction with the weighted centre, without
changing source files:

| grid | `(tube,near,far)` | weighted `kappa_bar` | `(t_c,theta_c)` | `(f_ttt,f_ttheta)` |
|---|---:|---:|---:|---:|
| `11x7` | `(349,32,40)` | `1.76504297994` | `(18.0992420,0.0133048319)` | `(-7.8199e-6,2.83157e-4)` |
| `13x9` | `(1123,117,131)` | `1.80186999110` | `(16.4132551,0.218508011)` | `(-5.90613e-6,7.79564e-5)` |

Residuals were at most `8.7e-18`. The fold mechanism persists in this limited
check, but the `13x9` critical control moves from reported `0.25589201`
(`manuscript:826`) to `0.21850801`, an absolute shift `0.03738` (about 14.6%).
Persistence does not cure the model mismatch.

**Required resolution**

Choose and declare one model, then regenerate all affected reflecting-2D
artifacts, tables, figures, manifests, tests, and manuscript numbers:

1. Preferably make the Doi builder take centre weights/diffusivities and
   implement the declared weighted centre; or
2. redefine the physical catalyst coordinate as the arithmetic midpoint,
   rederive the relative/midpoint operator including nonzero mixed diffusion
   for \(D_1\ne D_2\), and remove claims that current patches directly realize
   the decoupled GIG centre coordinate.

Every manifest should record a machine-readable `centre_coordinate`. Renaming
the current midpoint as weighted centre is not acceptable.

### B1-01 — Reflecting 2D solver is a node-centred CTMC, not the stated finite-volume discretization

**Evidence**

- The manuscript calls it a “conservative finite-volume CTMC” at
  `manuscript/encounter_modality_jcp.tex:712-719`.
- `encounter2d.py:26-29` calls `RectangularGrid2D` a “Cell-centre grid including
  both physical boundaries”, but `49-55` uses `h=L/(n-1)` and `62-75` places
  states at `0,h,...,L`: these are boundary-including nodes.
- `encounter2d.py:368-389` omits outward jumps and uses the same `D/h^2` rate at
  boundary and interior nodes. Its zero-drift invariant measure is uniform over
  nodes.
- Contact and patch supports are binary node-centre tests
  (`encounter2d.py:477-491`), with no cell-volume weighting or cell averaging.

A three-node reflecting interval has stationary masses `(1/3,1/3,1/3)` under
this generator. A finite-volume discretization of uniform physical density
with half boundary control volumes has `(1/4,1/2,1/4)` and asymmetric
boundary-adjacent rates. On `11x7`, the uniform node chain gives perimeter
nodes mass `32/77=0.416`; trapezoidal physical control-volume weights give the
boundary strip `15/60=0.25`.

This matters on the coarse headline grids and for their raw-state-sum budgets.
By contrast, the periodic 2D capacity solver uses true cell centres and subcell
disk fractions (`encounter2d.py:85-137,181-225`), and the 3D solver uses
cell-centred, cell-averaged spheres (`encounter3d.py:40-89,160-220`). Those
capacity results do not establish the same discretization for the reflecting
pair solver.

**Required resolution:** either describe this consistently as a finite-state,
node-centred CTMC and restrict continuum language, or implement a genuine
finite-volume scheme with boundary cell volumes, volume-consistent rates, and
cell-averaged contact/patch masks. Store quadrature weights and test convergence
of physical integrals, not only unweighted state sums.

### B1-02 — The advertised control hierarchy comes from a third 2D parameter family

The manuscript explicitly distinguishes the principal matched family from the
fold family at `manuscript:798-813`. It does not similarly disclose, where
controls are interpreted at `862-890`, that those controls use a third set.

| family | `a`; starts | drifts `(v1,v2)` | patches/rates |
|---|---|---|---|
| principal matched | `.13`; `(.10,.35)` | `(.18,.02)` | `.25/.72`, radii `.18/.20`, rates `.5/15` |
| fold | `.17`; `(0,.28)` | `(.115,.02)` | same patch geometry/rates |
| mechanism controls | `.13`; `(.10,.35)` | `(.18,.02)` | `.28/.90`, radii `.12/.20`, rates `.2/4`; interior `.75/.18` |

Anchors are `validate_2d_matched_homogeneous.py:51-68`,
`validate_2d_matched_fold.py:54-74`, and
`validate_2d_mechanisms.py:52-68`. Thus single-patch, coalesced-patch,
interior-patch, and uniform-reactivity outcomes are not factorial ablations of
the principal matched family. They can be separate examples, but cannot alone
isolate causal factors in the headline model.

**Required resolution:** assign immutable family IDs and add a complete
parameter table. Either rerun adverse controls as within-family ablations of
the principal matched model, or replace “control hierarchy separates” by
“separate examples illustrate” and keep conclusions family-specific. The
three-patch script is yet another declared family
(`validate_2d_trimodal.py:54-72`) and must not be silently pooled later.

## Independent convention checks that passed

- **State/Kronecker order.** `encounter.py:5-8,241-277` and
  `encounter2d.py:10-13,433-469` consistently use `(i,j)->i*n+j`. With
  `A=[[-2,2],[3,-3]]`, `B=[[-5,5],[7,-7]]`, state `(0,1)` gives `Q[1,3]=2`,
  `Q[1,0]=7`, diagonal `-9`, and zero row sum.
- **Exponential orientation.** Row propagation `alpha exp(Qt)` and column
  propagation `exp(Q.T t) alpha` agreed to `1.11e-16`. The 2D transpose at
  `encounter2d.py:570-580` and initial Kronecker order at `642-657` agree.
- **Flux/mass balance.** A separate 3x3 Doi toy gave operator closure
  `1.78e-15` and dynamic `-S'(t)-f(t)=-2.78e-16`, consistent with
  `encounter2d.py:427-431,493-516,578-580`.
- **Fold derivative action.** `validate_2d_matched_fold.py:223-290` correctly
  pairs column states from `exp(A.T t)` with right actions `A k`. At the native
  `11x7` fold, analytic `f_ttheta=2.8264184459e-4`; centred differences at
  `h=1e-3,3e-4,1e-4` had relative errors `3.09e-5,2.78e-6,3.09e-7`.
- **Doi units.** Numerically, `D/h^2`, `v/h`, transverse drift/h, and `kappa`
  all have inverse-time units (`encounter2d.py:333-389`), and
  `Da=kappa*a^2/Dr` is dimensionless. No rate-unit algebra error was found.
- **Capacity quotient assumptions.** The 2D/3D capacity calculations explicitly
  assume translation invariance and a relative-position observable, under
  which `Dr=D1+D2` is exact. They do not validate centre-patterned bounded-domain
  modality; the manuscript states this at `929-954` and `979-1011`.

## Not certified here

This pass did not certify exhaustive positive-time root isolation, absence of
tangential GIG roots, continuum convergence of the reflecting 2D fold,
Doi–Robin equivalence, or physical realization of designed GIG weights. These
belong to later audit rounds. In particular, the sign-change scan in
`validate_multid_gig_design.py:98-135` is not a proof that no even-multiplicity
roots exist; its summary records this limitation at `323-330`.

## Submission gate

Round 01 cannot close until B0-01 is resolved by a declared model choice and
full artifact regeneration, and both B1 findings are corrected or accompanied
by explicit claim downgrades. Retain the passed orientation checks as
regression tests during regeneration.
