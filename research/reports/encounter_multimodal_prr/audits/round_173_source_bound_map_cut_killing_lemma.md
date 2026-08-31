# Round 173: source-bound map, cut-layer, and killing-residual lemma

Date: 2026-07-17

Status: **PASS IDEAL SOURCE-BOUND ROUND-11 INPUTS / TWELVE FIXED-BOX
FORMULA-DEFINED REFINEMENT FAMILIES / P0=0 / P1=0 / P2=2 DOCUMENTED /
HOLD PRODUCTION SAME-MEMBER / HOLD COMPLETE C1--C3 / HOLD RELEASE**

## Final exact bytes

| role | report-relative path | SHA-256 |
|---|---|---|
| mathematical note | `notes/continuum_c2_source_bound_map_cut_killing_lemma_v1.md` | `09c84f471e4d0b3b4e927e5c99a12999827b7e060bcc7ce02122a4107d8460ed` |
| canonical contract | `artifacts/data/continuum_c2_source_bound_map_cut_killing_contract_v1.json` | `f977939e97651e1d45d83bc4d80acd3d19e6fac7d4ae90c2803090c25cfa9ee3` |
| builder | `code/build_continuum_c2_source_bound_map_cut_killing_contract_v1.py` | `aa82d83dbe3dc16cd8e6d56500d3d81415938faeb56b6b86d2fa54828afc8831` |
| source/geometry validator | `code/validate_continuum_c2_source_bound_map_cut_killing_contract_v1.py` | `f42fe98cd98bc6064a70339fcd62716d3771033cefa07911371f7399caa4c3eb` |
| static/currentness tests | `code/test_continuum_c2_source_bound_map_cut_killing_contract_v1.py` | `1f339a97a36bef5b6e79a050f2d367dbfa077bd5e0ee069959f6e71c9e88f00d` |
| mutation tests | `code/test_continuum_c2_source_bound_map_cut_killing_contract_mutations_v1.py` | `8e9a979f55a9494ebd4d39c398f96cb9ad9a66b51a94c3047008a9debca9cf72` |

The source chain pins the Round-172 twelve-sequence authority, finite
configuration anchors, global reference density, ideal formula source,
factorization source, control-free killing geometry, Round-170 geometry
receipt, and the Round-4/9/10/11 theorem/audit pairs.  It contains no concrete
control vector, budget, propagated state, topology output, or root result.

## The ideal source-bound theorem

For each of the twelve fixed boxes and every dyadic level \(n\ge0\), let
\(h_f(n)\) be the largest declared axis spacing.  Exact source recomputation
gives a common sufficient contact-tube tail starting already at \(n=0\).
Vertex-dual endpoint half cells and wrapped periodic cells are included.

Writing \(r_{a,i}\) for the physical axis-cell integral divided by its
representative quadrature primitive, the global gauge gives

\[
 \rho_{ijk}
 =\frac{r_{M,i}}{\bar r_M}\frac{r_{R,j}}{\bar r_R},
 \qquad
 e^{-\Lambda_*h_f(n)}
 \le \rho_{ijk}\le
 e^{\Lambda_*h_f(n)} .
\]

For the exact-adjoint maps,

\[
 P_h=J_h^*,\qquad
 P_hJ_h=\operatorname{diag}\rho,\qquad
 J_hP_h=\rho_h^{\rm pc}E_h .
\]

The map estimates include

\[
 \|P_hJ_h-I\|=O(h),\qquad
 \|J_hP_hu-u\|_{L^2(\pi)}
 \le C_Ph\|u\|_{H^1(\Omega_f)} ,
\]

where the final ordinary-\(H^1\) constant is

\[
 C_P=\sqrt{\pi_+^*}
 \left\{
 C_{\rm av}+\Lambda_*e^{\Lambda_*H_*}
 \right\}.
\]

This density-equivalence factor is material; its omission in the first draft
was caught by the independent referee and repaired before acceptance.

For every symbolic real-simplex profile
\(\psi=\sum_{j=1}^4w_j\phi_j\), the unit-budget field is

\[
 V=W^{-1}\psi(M)\mathbf1_{D_a}(R,Y).
\]

If \(\delta_f(n)\) is the relative-cell diameter, the exact source facts imply

\[
 \delta<a,\qquad a+\delta<W/2,\qquad
 R_-<-a-\delta,\qquad R_+>a+\delta .
\]

Only under these conditions is the cut-cell union bounded by the Euclidean
annulus of area \(4\pi a\delta\).  Consequently,

\[
 \|V_h^{\rm pc}-V\|_{L^2(\pi)}
 \le C_{V,\mathrm{cut}}h^{1/2}
   +(L_\Psi/W)h .
\]

With \(K_h^{\rm pc}=V_h^{\rm pc}/\rho_h^{\rm pc}\),

\[
 \|K_h^{\rm pc}-V\|_{L^2(\pi)}
 \le C_{K,\mathrm{cut}}h^{1/2}+C_{K,\mathrm{map}}h ,
\]

and, for the ordinary fixed-box \(H^2\) regular solution in quotient
dimension three,

\[
 |R_{h,\mathrm{kill}}(u;v_h)|
 \le C_{\mathrm{kill}}h^{1/2}
 \|u\|_{H^2(\Omega_f)}\|v_h\|_{1,h}.
\]

No derivative of the sharp indicator is used.  The half order is the square
root of the cut-layer measure.

## Adversarial chronology

The first independent referee rederived the gauge, map identities, annulus
conditions, sharp-contact average, reconstructed multiplier, and residual
algebra.  It found no counterexample to their orders, but rejected the first
freeze with two P1 findings:

1. the displayed \(C_P\) silently changed from weighted to ordinary \(H^1\)
   without the factor \(\sqrt{\pi_+^*}\), and the defect propagated into
   \(C_{\rm kill}\);
2. the validator validated one artifact read and then reopened the path to
   print a digest, allowing a PASS line to name unvalidated replacement
   bytes.

The repair added the norm-equivalence factor, propagated it through the
residual constant, and changed the validator to decode and hash one retained
descriptor snapshot.  Builder and validator snapshots now use
`O_NOFOLLOW`, regular-file and size checks, `fstat` before/after, and lexical
path device/inode identity.  Tests cover the repaired constant, single-
snapshot digest, symlink rejection, path replacement, strict Boolean types,
source currentness, and promotion-field mutations.

The same referee then reviewed the repaired exact bytes and reran the focused
suite.  Its final verdict is

```text
P0 = 0
P1 = 0
P2 = 2
```

The two retained P2 items are stated limitations, not silently upgraded
evidence:

- the local standard-library replay does not authenticate the interpreter,
  executed source bytes, or a hostile concurrent same-UID writer; and
- the executable contract independently reconstructs pinned exact geometry
  and source facts, but its analytical part is an exact-string contract plus
  a separate human proof audit, not an independent backend or machine proof.

## Reproduction

The final bytes were rerun from the repository root:

```text
.venv/bin/python -m ruff check <builder> <validator> <two test files>
All checks passed!

.venv/bin/python -m ruff format --check <the same four files>
4 files already formatted

.venv/bin/python \
  research/reports/encounter_multimodal_prr/code/build_continuum_c2_source_bound_map_cut_killing_contract_v1.py \
  --check
PASS ... sha256=f977939e... tail_start_n=0

.venv/bin/python \
  research/reports/encounter_multimodal_prr/code/validate_continuum_c2_source_bound_map_cut_killing_contract_v1.py
PASS ... validated_snapshot_sha256=f977939e...

.venv/bin/python -m pytest -q \
  research/reports/encounter_multimodal_prr/code/test_continuum_c2_source_bound_map_cut_killing_contract_v1.py \
  research/reports/encounter_multimodal_prr/code/test_continuum_c2_source_bound_map_cut_killing_contract_mutations_v1.py
....................                                                     [100%]
20 passed
```

Two clean-process builder/validator repeats also passed.  The hostile suite
contains 22 semantic and three malformed variants in addition to the
baseline.

## Exact acceptance boundary

Round 173 closes the missing map and sharp-killing residual inputs only for
the **ideal, formula-defined, fixed-box dyadic tails** and symbolic controls
in the complete simplex.  It does not show that level \(n=0\) is one
correlated production mass/rate/flux/gauge/map/killing member.

The following remain false:

```text
numerically_evaluated_theorem_constants              = false
production_n0_correlated_containment_receipt_present = false
production_same_member_bridge_accepted               = false
concrete_control_selected / positive_budget_present  = false
complete_C0 / complete_C1 / complete_C2 / complete_C3 = false
box_exhaustion / root_transfer                        = false
F0_complete / F1_complete                             = false
release_eligible / submission_eligible                = false
```

The strongest admissible citation is therefore: the source-bound symbolic
map/gauge and sharp-killing residual premises needed by the conditional
Round-11 ideal fixed-box argument are closed for the exact twelve
formula-defined refinement families.  Production C1/C2 and the PRR science
claim remain separate obligations.
