# Round 11 audit: mixed Neumann--periodic sector regularity and contour growth

Date: 2026-07-17

Status: **IDEAL FIXED-BOX ANALYTICAL CLOSURE / COMPLEX-CONVENTION ERRATUM
APPLIED / TWO PROOF AUDITS PASS / NEUTRAL FIXTURE 1482/1482 PASS /
SOURCE-BOUND COMPOSITION OPEN / COMPLETE C2 FALSE**

## 1. Audited successor and exact scope

The final Round-11 analytical successor is

- `notes/continuum_c2_mixed_neumann_periodic_sector_h2_candidate.md`;
- 753 lines, 18,715 bytes;
- SHA-256
  `4339385e8489984701aabedbd4ab0a28d69db5b2ffd7e2d1c91d1d4ba63564d9`.

It closes one ideal fixed-box premise selected after Rounds 9--10:

1. the mixed Neumann--periodic graph domain is `H2_NP`;
2. bounded sharp killing preserves that domain;
3. the killed operator has a control-uniform complex-sector `H2` graph
   estimate;
4. the first-factor-conjugated discrete form has the matching rotated
   coercivity; and
5. a conditional reconstructed-resolvent half-order rate has an explicit
   finite positive-time Dunford majorant for `r=0,1,2`.

It does **not** source-bind the map or killing residual constants, identify a
same production member, prove an unconditional reconstructed-resolvent rate,
close complete C1/C2, perform box C3, transfer roots, execute F0--F3 science,
or make the paper release eligible.

The theorem-first manuscript was deliberately not edited in this round.

## 2. Adversarial proof chronology

The first pre-freeze mathematical attack found and repaired four substantive
presentation/proof obligations:

- the lower-order absorption display and the converse operator-domain
  inclusion were made explicit;
- `P_h=J_h^*` and the first-factor-conjugated residual equation were stated
  rather than inferred;
- the globally normalized density was separated from any artificial-box
  renormalization; and
- the upper and lower Dunford ray orientations were frozen explicitly.

After those repairs, the first full proof audit checked the 751-line candidate
at SHA
`47fa2dacf2b7dbb8ada7318b0560a8b1595369feb009566fb496ba9e93592243`
and reported

```text
P0=0 / P1=0 / P2=0
```

A second independent referee rederived the same theorem chain and found no
P0 or P1.  It identified one wording-only P2: box normalization is

\[
 \pi_L=\pi/M_L,\qquad Z_L=Z M_L,
\]

not the informal replacement `Z -> box mass`.  The final note applies that
repair and updates only its status block.  A mechanical reverse-diff restored
the old 751-line bytes and exact old SHA, proving that no equation, proof, or
HOLD boundary changed.  The current 753-line SHA then received the final
verdict

```text
P0=0 / P1=0 / P2=0
```

## 3. Complex convention and the Round-10 erratum

The authoritative convention is

\[
 \langle u,v\rangle=\int\overline u\,v\,\pi\,dx,\qquad
 \mathfrak a(u,v)=\int(\nabla\overline u)^T\mathbf D\nabla v\,\pi\,dx.
\]

Thus the first factor is conjugated.  The correct Round-10 face residual is

\[
 R_{h,\mathrm{free}}(u;v_h)
 =\sum_e\overline{E_e(u)}(v_{e,+}-v_{e,-}).
\]

The frozen Round-10 sentence used the opposite convention.  Its absolute
residual bounds, real neutral rows, endpoint constant-mode obstruction, and
orders are unchanged because the two displayed expressions are complex
conjugates.  Round 11 records this as an erratum rather than silently changing
the frozen Round-10 bytes.

With the authoritative convention, the spectral coefficient in the second
form argument is `sigma+lambda`, not `sigma+conjugate(lambda)`, and

\[
 \omega_\lambda=e^{-i\arg(\lambda)/2}.
\]

The error equation must be tested in its first argument:

\[
 \mathfrak b_{h,c,\lambda}(v_h,e_h)
 =-\overline{R_{h,\mathrm{free}}(u;v_h)}
  -B\overline{R_{h,\mathrm{kill}}(u;v_h)}.
\]

These signs and conjugates were independently rederived in both proof audits
and attacked by the fixture mutation suite.

## 4. Mixed graph domain and bounded sharp killing

For physical `d=2`, the fixed quotient box is

\[
 \Omega_L=I_z\times I_\parallel\times\mathbb T_W,\qquad
 \mathbf D=\operatorname{diag}(D/2,2D,2D).
\]

The density is the restriction of the globally normalized Gaussian--torus
density, with `Z=2*pi*D*W/gamma`.  Its box mass `M_L` is strictly below one;
the analysis does not replace it by a box-normalized density.

Cosines on the two interval factors and Fourier modes on the torus identify
the constant-coefficient principal domain.  The drift
`b_0=D grad(log pi)` is bounded on the fixed box and is principal-operator
bounded with relative bound zero.  The weak converse uses

\[
 L_{\mathbf D}u=f+b_0\cdot\nabla u\in L^2
\]

and rectangular Neumann--periodic `L2` regularity.  Consequently

\[
 D(H_0)=H^2_{\mathrm{NP}}(\Omega_L),\qquad
 \|u\|_{H^2}\le C_{\mathrm{NP}}
   \{\|H_0u\|+\|u\|\}.
\]

For every real simplex control, the sharp contact killing field is a bounded
nonnegative multiplier.  The bounded-perturbation theorem therefore gives

\[
 D(H_c)=D(H_0)=H^2_{\mathrm{NP}}(\Omega_L).
\]

No derivative of the contact indicator and no interface condition appear.
The dimension-three embedding `H2 -> L-infinity` belongs only to the still
open killing-residual bound; it is not used to prove the graph domain.

## 5. Sector geometry and resolvent powers

For

\[
 \Lambda_\theta=\{0\}\cup
 \{\lambda\ne0:|\arg\lambda|\le\pi-\theta\},
 \qquad s_\theta=\sin(\theta/2),
\]

the exact scalar geometry is

\[
 |a+\lambda|\ge s_\theta(a+|\lambda|),\qquad a\ge0.
\]

The constant is sharp at the boundary angle with `a=|lambda|`.  Applying this
to the spectrum of `H_c` yields, with `q=sigma+|lambda|`,

\[
 q\|u\|_{L^2}+q^{1/2}\|u\|_{H^1}+\|u\|_{H^2}
 \le C_{\mathrm{reg}}\|f\|_{L^2}.
\]

The `H2` term is uniformly bounded; it does not decay like
`|lambda|^(-1)` for arbitrary `L2` data.

Under the explicitly unclosed source assumptions for free residual, killing
residual, projection error, and reconstruction stability, rotated coercivity
gives

\[
 \left\|
 J_h(H_{h,c}+\sigma+\lambda)^{-1}P_h
 -(H_c+\sigma+\lambda)^{-1}
 \right\|
 \le
 \frac{C_{\mathrm{sec}}h^{1/2}}
 {(\sigma+|\lambda|)^{1/2}}.
\]

This is a conditional composition.  Its constant is not accepted until those
source assumptions are proved from frozen physical inputs and tied to the
same production member.

## 6. Dunford orientation and explicit majorant

The contour rays are

\[
 \lambda=\rho e^{\pm i(\pi-\theta)}.
\]

The upper ray is oriented `rho: 0 -> infinity`; the lower is oriented
`rho: infinity -> 0`.  Reversing both changes the overall sign.  With that
orientation,

\[
 H_c^re^{-tH_c}
 =\frac{e^{\sigma t}}{2\pi i}
 \int_{\Gamma_\theta}
 (-\lambda-\sigma)^re^{t\lambda}
 (H_c+\sigma+\lambda)^{-1}\,d\lambda.
\]

The two rays change the norm prefactor from `1/(2*pi)` to `1/pi`.  For
`t in [tau,T]`, `tau>0`, the remaining scalar majorant is

\[
 \int_0^\infty e^{-a\rho}
  (\sigma+\rho)^{r-1/2}\,d\rho
 =
 e^{a\sigma}a^{-(r+1/2)}
 \Gamma(r+\tfrac12,a\sigma),
 \qquad a=\tau\cos\theta.
\]

It is finite for `r=0,1,2` and grows at most like
`tau^(-(r+1/2))` as `tau` decreases.  No estimate at `tau=0` is claimed.

Both proof audits checked the residue sign.  Separate scalar numerical
reconstruction gave errors at machine precision before the canonical fixture
was frozen.

## 7. Neutral reproducibility fixture

The final fixture files are:

| role | path | SHA-256 |
|---|---|---|
| builder | `code/continuum_c2_complex_sector_h2_neutral_fixture_v1.py` | `6b4f4bb0484c1b66a1527ba0fd6707258d2d84aede24046c4e312b08ae074f7b` |
| canonical artifact | `artifacts/data/continuum_c2_complex_sector_h2_neutral_fixture_v1.json` | `c6975c3748761dd4314f424f6aec3b3781c0382aa5c8e957b72b0c0ef4cef001` |
| independent verifier | `code/test_continuum_c2_complex_sector_h2_neutral_fixture_v1.py` | `0a4b2df21e60103cb5a69783d0c28af68dc57de50593697bc9ff46fcd09c5a34` |
| mutation verifier | `code/test_continuum_c2_complex_sector_h2_neutral_fixture_mutations_v1.py` | `bbe0346af698dd87d1e83d997882cb85073cf900163fb6d0edd680685d5a208a` |

The artifact has 2,992 lines, 95,491 bytes, and canonical SHA
`c6975c3748761dd4314f424f6aec3b3781c0382aa5c8e957b72b0c0ef4cef001`.
It contains no control result, budget experiment, production member, reaction
time, modal root, or release flag.

The initial executable bytes printed `1436/1436` plus `38/38`, but a third
independent fixture attack proved that this receipt was not yet sufficient.
It constructed two canonical counterexamples that the custom-artifact branch
accepted:

1. an unknown `complete_C2=true` key nested inside one rotated-coercivity row;
2. `p_neumann_z=true` in place of integer one, exploiting Python's
   `True == 1`.

The same audit found a P2 in which the mutation baseline used the frozen
default branch while every mutation used the custom-artifact branch, and
generic `ERROR` wrapping did not distinguish assertion rejection from an
internal `KeyError` or `TypeError`.

The repaired verifier requires exact key sets for coercivity,
`lambda=-z`, Dunford-target, and incomplete-gamma rows, plus strict integer
types for every affected mode/order coordinate.  Its final error line includes
the exception class.  The mutation harness now requires both the frozen
`1436/1436` baseline and an unchanged custom-copy `1430/1430` baseline, permits
only `AssertionError` for well-formed semantic mutations, and separately
permits the exact parser categories for duplicate and malformed JSON.  Seven
new attacks cover all repaired nested-key and Boolean/integer paths.  Both
counterexamples are now rejected.  The same independent fixture auditor
rechecked the four final SHAs without editing them and reported

```text
P0=0 / P1=0 / P2=0
```

The finite neutral diagnostic covers:

- 45 constant-coefficient mixed Neumann--periodic principal modes on
  `(-1,1)^2 x T_1`;
- an exact-rational bounded sharp-multiplier ledger;
- 100 scalar sector-distance samples, including the sharp one-half case;
- 75 first-factor-conjugated rotated-coercivity samples;
- five `(sigma+rho)^(-1/2)` resolvent-majorant samples;
- ten `lambda=-z` mappings;
- eighteen independently integrated oriented scalar Dunford contours; and
- nine independent quadrature/incomplete-gamma comparisons for Eq. (8.6).

The executable receipts are

```text
builder --check       PASS / output_not_written=true
independent verifier  1436/1436 PASS
custom-copy baseline   1430/1430 PASS within mutation preflight
mutation verifier       46/46 PASS
Ruff                    PASS
total counted         1482/1482 PASS
```

The independent verifier reconstructs the modes, rational multiplier ledger,
sector geometry, rotation, contour integrals, and gamma integrals without
calling the builder's mathematical row functions.  It calls the builder only
to verify deterministic clean builds, exact frozen bytes, read-only check
mode, exclusive-write rejection, and absent-output behavior.

The mutation harness first requires the exact `1436/1436` frozen baseline and
the `1430/1430` custom-copy baseline used by all mutations.  Every mutation
must then produce exactly one allowed classified `ERROR`, exit one, no
summary, and no traceback, `ModuleNotFoundError`, or `ImportError`.  Its 41
semantic attacks include second-factor conjugation, wrong rotation, wrong
sector, reversed rays, false `H2` decay, `tau=0`, indicator differentiation,
nested promotion keys, Boolean/integer aliases, and C2/production promotion;
duplicate-key, noncanonical, and malformed JSON attacks complete the 46
counted checks.

This fixture is deliberately finite and neutral.  Its principal-mode window
does not prove the weighted PDE graph-domain theorem, and its binary64/SciPy
quadratures do not source-bind an infinite-dimensional rate.

## 8. Manuscript and PDF boundary

The repository compiler was rerun without importing Round 11 into the
theorem-first sources.  The current compile manifest is

- `artifacts/data/theorem_first_working_compile.json`;
- SHA-256
  `03a9be39a44e16db66f65ff41ce48fcf5ff640702e9f35c16d072d126d4c8e81`;
- `release_eligible=false`.

It publishes byte-reproducible Letter PDFs:

| document | pages | SHA-256 |
|---|---:|---|
| theorem-first main | 7 | `78e2e5169f0397073e4edc3deaad27bf4563f856999eea8468d0e698b51f306a` |
| theorem-first Supplemental | 24 | `a3716ded14c480188c3504ad86e7318129aa32ada57ada2caf6b7767d26c9cf7` |

An independent TeX Live build also completed for both sources.  Full-page
render inspection covered all 31 pages; no clipping, overlap, missing page,
Type-3 font, or unembedded font was found.  Existing underfull boxes and the
awkward but legible Table II wrapping are presentation P2s, not a reason to
smuggle Round 11 into the manuscript.

The focused compiler/scope suite passes 19/19.

## 9. Verdict and next continuum step

```text
mixed NP graph-domain theorem candidate          = ACCEPT LOCALLY
bounded sharp killing preserves the domain       = ACCEPT LOCALLY
control-uniform complex-sector H2 estimate        = ACCEPT LOCALLY
rotated-coercivity and contour algebra            = ACCEPT LOCALLY
neutral reproducibility fixture                   = ACCEPT
source-bound map constant                         = OPEN
source-bound cut-layer/killing constant           = OPEN
same ideal member inside production enclosure     = OPEN
unconditional reconstructed-resolvent C2 rate     = FALSE
complete C1 / C2 / C3 / root transfer             = FALSE
release and submission                            = FALSE
```

The next step is no longer another sector theorem or another fitted slope.
It is to instantiate the map and killing residual assumptions from the frozen
global gauge, exact-adjoint projection, physical contact volumes, and
production source files; prove that one accepted production member contains
the same ideal member; and subject that source composition to independent
source-opening and mutation audits.  Only then can Eq. (7.12) become an
unconditional C2 input, followed by box C3 and componentwise root transfer.
