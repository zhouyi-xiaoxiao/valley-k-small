# Round 82: independent post-edit attack on the fixed-finite-dimension repair

Date: 2026-07-14  
Predecessors: `audits/round_77_general_dimension_theory_attack.md` and
`audits/round_79_general_dimension_repair.md`  
Scope: independent read-only attack on the promoted general-\(d\) theorem,
all named living scope surfaces, the canonical article PDF/build manifest, and
the new scope regression test  
Mutation boundary: no pre-existing manuscript, Supplement, note, contract,
blueprint, test, numerical source, result, manifest, PDF, or figure was changed.
No scientific producer was run. This audit is the only repository file added.

## 1. Exact verdict

**HOLD-GENERAL-DIMENSION-PROMOTION.**

The mathematical core of the Round 79 extension survives the independent
attack: the direct theorem is valid pointwise for each fixed finite integer
physical dimension \(d\ge2\) and each fixed finite \(m\), with the order

\[
 \text{freeze }(d,m,\text{data})
 \longrightarrow \text{choose sufficiently small }\epsilon
 \longrightarrow \text{choose }0<B<B_0(\epsilon).
\]

The diagonal-Haar quotient, embedded contact ball, all-image lattice tail,
weighted-form analytic semigroup, and \(W^{-(d-1)}\) budget normalization do
not use a low-dimensional Sobolev embedding. No counterexample to the scoped
theorem was found.

Promotion is nevertheless held because the canonical main article, and hence
the canonical PDF, still describes the general-\(d\) contact set as a “disk or
sphere.” That is a two-/three-dimensional description inside a theorem claimed
for every fixed finite \(d\ge2\); for \(d\ge4\) the declared object is the embedded
minimum-image \(d\)-ball. The Supplement, direct theorem note, and article
appendix use the correct ball formulation, so this is a living-surface claim
contradiction rather than a failure of the underlying proof.

Open counts:

| P0 | P1 | P2 |
| ---: | ---: | ---: |
| 0 | 1 | 2 |

## 2. Severity ledger

| ID | Severity | Finding | Required disposition |
| --- | --- | --- | --- |
| R82-1 | **P1** | In `manuscript/encounter_multimodal_prr.tex`, lines 527--528, the subsection headed “every fixed finite \(d\ge2\)” assumes that the deterministic trajectory stays inside the “true disk or sphere of contact.” The same text is rendered on page 4 of the canonical PDF. A disk/sphere dichotomy covers the physical \(d=2,3\) cases, not the stated \(d\ge4\) theorem. It is also weaker than the precise chart-independent hypothesis used by the proof. | Replace it by the embedded minimum-image \(d\)-ball/contact-ball formulation and, preferably, state the margin \(\sup_{t\in I_*}|r_*(t)|_{\mathrm{mi}}\le a-\eta\). Rebuild the canonical PDF and manifest, then rerun an independent scope audit. |
| R82-2 | P2 | The sources correctly call \(B\) a dimensional budget and prohibit cross-dimensional comparisons, but none of the promoted living sources states its unit explicitly. With \(\kappa\) a rate, normalized \(\phi\) of unit \(L^{-1}\), and \(W^{-(d-1)}\), the dimensional theorem has \([B]=L^dT^{-1}\). This matters because a common numerical value of \(B\) across dimensions is not a physical comparison without a separately declared nondimensionalization. | Add one unit sentence near the general-\(d\) normalization in the main article and Supplement, distinguishing dimensional theorem \(B\) from any dimensionless numerical convention. Retain the existing no-cross-dimension caveat. |
| R82-3 | P2 | `code/test_general_dimension_scope_consistency.py` is predominantly token-presence testing. It requires “fixed finite,” a \(d\ge2\) token, “uniform,” and “lattice” somewhere in each source, but it does not enforce theorem-local quantifier order, a \(d\)-ball, the Haar/\(W^{-(d-1)}\) normalization, or negative rather than positive uniformity wording. It passed while R82-1 remained in the main article and PDF. | Mutation-harden the test: reject “disk or sphere” in the general-\(d\) theorem; require the nested \(\epsilon\)-then-\(B\) order; require contact ball/cut-locus/all-image wording and \(W^{-(d-1)}\); and check explicit negative uniform-in-\(d\), \(d\to\infty\), cross-dimensional budget/amplitude/mass, and numerical-\(d>3\) boundaries. |

R82-1 is a release-blocking scope defect even though its mathematical repair is
one sentence: the error occurs in the authoritative article theorem and in the
source-pinned PDF, not only in an archival note.

## 3. Adversarial mathematical audit

### 3.1 Outer quantifiers and sequential limits: PASS

The Supplement gives the exact order

\[
 \exists\epsilon_0(d,m,\text{data},\mathcal W)>0\;
 \forall\epsilon\in(0,\epsilon_0)\;
 \exists B_0(d,m,\text{data},\mathcal W,\epsilon)>0\;
 \forall B\in(0,B_0)\;
 \forall w\in\mathcal W.
\]

The article and direct note preserve the same order in prose. The dimension,
mode count, dimension-sized covariance, target times, compact interior weight
set, and contact margin are frozen before \(\epsilon\) is chosen. The
weak-reaction threshold is then allowed to depend on that fixed \(\epsilon\).
All core sources explicitly deny limit interchange, uniformity in \(d\) or
\(m\), and a \(d\to\infty\) statement.

No statement was found that one geometry realizes arbitrary \(m\), that one
\(B_0\) works across dimensions, or that the construction gives an exact
global modal count.

### 3.2 Exact Haar quotient: PASS

The Supplement, direct note, and mixed-jet note use the exact identity

\[
 \int_{\mathbb T_W^{d-1}}\!\int_{\mathbb T_W^{d-1}}
 h(y_1-y_2)\,\mathrm dy_1\mathrm dy_2
 =W^{d-1}\int_{\mathbb T_W^{d-1}}h(r_\perp)\,\mathrm dr_\perp.
\]

This is the quotient by diagonal transverse translation. It does not introduce
a nonexistent global transverse midpoint coordinate. The action and Haar
factor are valid for every fixed finite torus dimension \(d-1\).

### 3.3 Contact ball, cut locus, and every lattice image: PASS in the proof package; P1 in the main wording

For \(0<a<W/2\), the contact set is an embedded minimum-image \(d\)-ball
inside \(\mathbb R\times\mathbb T_W^{d-1}\), and its boundary is separated
from the torus cut locus. The contact-interior margin and the reverse triangle
inequality put every point of the complement at product-geodesic distance at
least \(\eta\) from the deterministic mean.

The Supplement does not infer that the complement lies in one chart. It writes
the wrapped density as a sum over all \(n\in\mathbb Z^{d-1}\), observes that
the geodesic lower bound applies to the minimum over lifts and hence to every
lift, and combines polynomial lattice-shell growth with Gaussian decay. This
is the correct fixed-dimensional proof of differentiated tail suppression.

The only failed propagation is R82-1: the main article replaces this general
object by the dimension-specific words “disk or sphere.”

### 3.4 Weighted form and analytic semigroup: PASS

For each fixed finite \(d\), the form domain is weighted \(H^1\) with
periodic traces in the \(d-1\) transverse directions and the declared
weighted-Neumann convention in the nonperiodic directions. The closed form

\[
 \mathfrak a_d(u,v)=
 \int(\nabla u)^{\mathsf T}\mathbf D_d\nabla\overline v\,\pi_d\,\mathrm dx
\]

gives a nonpositive self-adjoint generator on \(L^2(\pi_d\mathrm dx)\).
The map \(u\mapsto q=\pi_du\) is unitary into
\(X_{\pi_d}=L^2(\pi_d^{-1}\mathrm dx)\) on the unbounded cylinder.
The fixed-\(\epsilon\) killing profiles are bounded multiplication
operators, so bounded perturbation and the Dyson expansion provide the
positive-time mixed jets. No Sobolev embedding, trace estimate with a critical
dimension, or dimension-uniform constant is used.

The unbounded observable norm is correctly changed to
\(\|V\|_{X_\pi^*}=\|V\|_{L^2(\pi\mathrm dx)}\); the main
article does not incorrectly reuse its bounded-box similarity constant.

### 3.5 \(W^{-(d-1)}\), centre-space budget, and units: mathematical normalization PASS; explicit-unit P2

The general slab field is

\[
 K_{B,w,\epsilon}(Z,R)=
 \frac{B}{W^{d-1}}\chi_a(R)\sum_jw_j\phi_{j,\epsilon}(Z),
 \qquad \int\phi_{j,\epsilon}(z)\,\mathrm dz=1.
\]

The Haar-orbit volume \(W^{d-1}\) cancels the displayed factor, so the
installed **centre-space** amount is \(B\). It is not the integral of the
quotient killing field over all relative configurations. The same
\(W^{-(d-1)}\) occurs in every free-exposure channel and changes a common
amplitude, not the local sign/concavity argument or the within-dimension
balancing weights.

Dimensional analysis gives \([B]=L^dT^{-1}\) when the killing field has
unit \(T^{-1}\). The sources prohibit comparisons of dimensional budget,
amplitude, event mass, and \(B_0\) across dimensions; R82-2 asks only that
the unit be made explicit rather than left inferential.

### 3.6 Numerical-scope attack: PASS

No living surface or numerical manifest inspected claims numerical evidence
for \(d>3\). The numerical evidence remains:

- result-informed exact \(B=0\) free-exposure kernels in physical \(d=2\)
  and \(d=3\), with separately selected allocations and shape-only
  normalization;
- positive-budget fixed-control evidence only in physical \(d=2\), on the
  declared same-solver finite-volume meshes/box;
- no positive-budget physical-\(d=3\) result and no independently converged
  two-/three-dimensional headline.

The article caption explicitly says that the two dimensions use different
allocations. No surface asserts one allocation robust across dimensions, or
compares raw \(B\), peak amplitude, or event mass across dimensions.

## 4. Living-surface and build audit

### 4.1 Frozen bytes actually inspected

| Surface | SHA-256 |
| --- | --- |
| `audits/round_77_general_dimension_theory_attack.md` | `ee9b133c03923f3f226476a3283cb63e4a0123a348dc40a3a3e4c867f2d7813c` |
| `audits/round_79_general_dimension_repair.md` | `24af4c9ca983e21f83cc023b36f951d15b3f0d4800ab43b551bc6ea00072689d` |
| `manuscript/encounter_multimodal_prr.tex` | `9ff234179adb4ac997347e4ad8152b869572d2391c79d67eef86b9dd1b9921c1` |
| `manuscript/encounter_multimodal_prr_supplement.tex` | `21d9bf4263d9bcb2fa6df5fac2c3607dde4de2259ad26062c8358214087ef024` |
| `notes/direct_physical_multimode_theorem.md` | `b406f49785fb36f525e9d689204642c187d40a30f4983d616305d8ad957a1afa` |
| `notes/pde_mixed_jet_theorem.md` | `6f7252fc42a7eecb1342477e95e639791fb6fb9c49e75ed91f89519ea7cd034e` |
| `README.md` | `9eec3cf36ff33648586d595231513375061a990d864effc98ec26b2a4442d6cb` |
| `notes/research_contract.md` | `fd0340efd28e97142565840c0f32b362f233ae44bf39b500a508ac62f4f9be77` |
| `notes/theorem_program.md` | `ce23ecf940e5864facafea563588aecbd75555b23a16a0b4bf6178a2138e422e` |
| `notes/prr_focused_spine_rewrite_blueprint.md` | `585ea39754c133afd99c13e552c0ee5bbae2ebb0fc2a5809f15bef4d0ab02009` |
| `code/test_general_dimension_scope_consistency.py` | `ce869d09702902de52bc6baa3b168be91ffe54052800c4e02397aacdb2fb35e1` |
| `artifacts/data/manuscript_compile.json` | `5935fa6300859eb867d4197148d4fe4fb54495e6011f135f3d0b26139289acf9` |
| `manuscript/encounter_multimodal_prr.pdf` | `c77e39944cc6c1f0d79c7a4c671a02eb81ab78e50cc110a7ea529b63033f88d0` |

The current README hash differs from the pre-ledger README hash printed in
Round 79 exactly as Round 79 warned; the scientific wording and current bytes,
not the stale pre-ledger hash, were audited here.

### 4.2 Read-only regression and compile evidence

The following focused tests were run without invoking a scientific producer:

```text
../../../.venv/bin/python -m pytest -q \
  code/test_general_dimension_scope_consistency.py \
  code/test_living_scope_consistency.py \
  code/test_compile_manuscript.py

17 passed
```

Ruff on the new scope test also passed. These results establish that the
current checks are green; R82-3 explains why that green status is not
sufficient to accept the general-\(d\) propagation.

Using TeX Live only in a temporary directory and the manifest's
`SOURCE_DATE_EPOCH=1783900800`, an independent article compile completed in 13
letter pages. Its PDF was byte-identical to the canonical PDF:

```text
c77e39944cc6c1f0d79c7a4c671a02eb81ab78e50cc110a7ea529b63033f88d0
```

The canonical manifest has `status=PASS`, `release_eligible=false`, the correct
article source hash, the same PDF hash, byte-identical clean-rebuild status,
45 embedded/subset font rows, zero Type-3 rows, and zero recorded missing-file,
overfull-box, unresolved-reference, or unresolved-citation counts. Visual
inspection of article pages 4--5 found no clipping or collision; it also
confirmed that R82-1 is visibly rendered on page 4.

A separate temporary Supplement compile completed in 12 letter pages with
embedded fonts and no overfull box, undefined reference, or undefined citation
match. It was not promoted or written into the repository. The compile manifest
is explicitly an article-build manifest and does not pretend to be a canonical
Supplement manifest.

Thus the article PDF and compile manifest are byte-consistent with the source.
That consistency propagates, rather than cures, R82-1.

## 5. Acceptance conditions

The fixed-finite-\(d\) repair may be accepted after all of the following:

1. replace the main article's “disk or sphere” phrase by the embedded
   minimum-image \(d\)-ball/contact-interior hypothesis;
2. regenerate the canonical article PDF and fail-closed compile manifest;
3. strengthen `test_general_dimension_scope_consistency.py` so the same
   dimension-specific phrase and a reversed/blurred quantifier order fail;
4. state the unit or nondimensionalization of \(B\) explicitly; and
5. obtain an independent post-fix check with P0=P1=0.

Until then the scoped mathematical theorem remains credible, but the Round 79
general-dimension promotion is **HOLD**. This verdict does not change the
larger project-level HOLD for the allocation cusp, continuation,
independent-solver, or positive-budget physical-\(d=3\) gates.
