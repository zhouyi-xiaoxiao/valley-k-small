# Round 02 resolution — Green, Woodbury, resolvent, and spectral scope

Date: 2026-07-11  
Status: **PASS WITH FINITE/CONTINUUM SCOPE SPLIT**  
Submission gate: **reopened for Round 02; later rounds remain open**

Both reviewers independently confirmed the finite Woodbury sign and order,
channel transform, Laplace derivatives, zero-frequency moments, mass balance,
and reaction-rate sensitivity. They also independently found that the paper's
primary \(K^{-1}\) formula did not cover its declared nonnegative/zero-rate
model class. The reviewers differed only in emphasis: Reviewer A elevated the
unproved negative-half-plane continuum language to B1; Reviewer B additionally
required a near-zero fail-closed numerical gate and an explicit full observable
sensitivity equation. All findings were addressed.

## Disposition

### Inverse-free primary identity

The primary volume-reaction result now uses

\[
M=I+GK,
\qquad
R=R_0-R_0\Gamma^*K M^{-1}\Gamma R_0,
\]

\[
x=\Gamma Rq_0=M^{-1}u,
\qquad y=Kx=K M^{-1}u.
\]

No inverse of \(K\) is required. The \((K^{-1}+G)^{-1}\) representation is
retained only as a corollary when \(K\) is boundedly invertible. The finite
renewal determinant is consistently

\[
\Delta(s)=\det[I+G(s)K],
\]

which agrees with the code and Lean algebra and remains meaningful when a
channel rate is zero.

### Finite spectral result versus continuum Laplace response

The claim is split into two mathematical layers.

1. For finite matrices and \(s\notin\sigma(L_0)\), the Green API now accepts
   any finite complex parameter and verifies
   \(\det(sI-T)=\det(sI-L_0)\det(I+GK)\). Negative \(s\) is called a finite
   rational-resolvent evaluation, not a physical Laplace transform.
2. The continuum operator result remains restricted to the right-half-plane
   Laplace response. Fredholm compactness, meromorphic continuation, Bromwich
   inversion, and continuum pole/residue claims are expressly not established.

The direct `ctmc_channel_laplace` API remains restricted to
\(\operatorname{Re}s\ge0\), so the two interfaces cannot be silently confused.

### Executable pole, dark-mode, and residue certificate

`validate_finite_green_spectrum.py` generates a deterministic exact `4x4`
fixture. It verifies:

- a shared dark eigenvector \((0,1,-1,0)^\mathsf T\) with
  \(U^\mathsf Tv=0\) and free/killed eigenvalue \(-2\);
- a coupled killed pole \(s_*=-5/2\), at distance \(1/2\) from the free
  spectrum, with \(\det[I+G(s_*)K]=0\);
- channel residues \((1/4,-1/4)\), each nonzero, whose ordinary total-flux
  residue is exactly zero;
- determinant-lemma agreement in both right and left half-planes; and
- an inverse-free zero-rate channel check.

At the exact killed pole the full Green solve fails closed because the renewal
matrix is singular. The artifact is a finite spectral exclusion/cancellation
certificate, not a production-fold spectrum or continuum theorem.

### Zero mode and numerical fail-closed behavior

The splitting formula now states locally that the full killed live operator
must be transient and \(-T\) invertible; initial-class-only transience requires
a reachable-transient-subspace or explicit Poisson/Drazin formulation.

For small nonzero \(s\), `ctmc_green_resolvent` records method
`finite_free_green_woodbury` and applies a configurable default
`1e-8` accuracy gate to free/renewal residuals, reconstructed killed-equation
error, condition-number roundoff bounds, and optional direct discrepancy. It
does not silently switch methods. In the regression sweep, `s=1e-7` passes and
agrees channelwise with the direct killed solve; `s=1e-8` is rejected before
the deliberately loosened diagnostic run develops `1e-8` channel error.

### Complete observable sensitivity

The manuscript and theory note now state, for \(F=\alpha RUK\),

\[
\partial_\theta F
=\alpha_\theta RUK+\alpha RT_\theta RUK
 +\alpha RU_\theta K+\alpha RUK_\theta.
\]

The fixed-initial, fixed-support rate Jacobian retains the resolvent and direct
observable terms. Moving a sharp support is explicitly excluded from smooth
fixed-grid sensitivity claims.

## Revalidation

- Relevant seven-file encounter suite: `50 passed`.
- Focused Green and spectral suite: `30 passed` before workflow integration.
- Integrated Green/spectral/notebook/manuscript/pipeline subset: `35 passed`
  after excluding only the intentionally stale aggregate-manifest hash checks.
- Spectral JSON and manifest regenerated deterministically; the validator's
  independent rerun was byte-identical.
- Executed publication notebook: 18 code cells, zero errors, ten passing claim
  rows, and `continuum_green_meromorphic_continuation_claimed=false`.
- Manuscript: 20 pages, 12 figures, and zero undefined references, undefined
  citations, overfull boxes, or missing files.

## Commands

```text
PYTHONPATH=packages/vkcore/src .venv/bin/python \
  research/reports/encounter_heterogeneous_catalytic/code/validate_finite_green_spectrum.py

PYTHONPATH=packages/vkcore/src .venv/bin/python -m pytest -q \
  tests/test_encounter_green_ctmc.py \
  tests/test_encounter_green_uniformization.py \
  tests/test_encounter_green_spectral_artifact.py \
  tests/test_encounter_publication_notebook.py \
  tests/test_encounter_manuscript.py \
  tests/test_encounter_publication_pipeline.py \
  -k 'not child_manifests_record_hashed_outputs and not aggregate_manifest_has_no_self_hash_and_covers_all_layers'

PYTHONPATH=packages/vkcore/src .venv/bin/python \
  research/reports/encounter_heterogeneous_catalytic/code/compile_manuscript.py
```

## Retained boundary

Round 02 does not certify continuum meromorphic continuation, operator-domain
hypotheses for an unbounded or Robin trace reaction, production-model pole
isolation/Jordan conditioning, Bromwich inversion, or a spectral proof of
time-domain modality. Those claims are absent or explicitly withheld. The
time-domain folds remain direct semigroup results rather than deductions from a
secular root.
