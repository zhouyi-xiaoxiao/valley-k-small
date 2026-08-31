# Round 25: observable four-patch exact-continuum self-audit

Date: 2026-07-13  
Evidence timing: **result-informed confirmation; not prospective discovery**

## Verdict

**PASS FOR THE DECLARED FREE-EXPOSURE CONFIRMATION; HOLD FOR FINITE \(B\),
INTERVAL CERTIFICATION, AND THE PROJECT/PRR GATE.**

The direct continuum calculation confirms an observable three-maximum,
two-minimum density for the preidentified four-patch geometry.  The formal
candidate grid, eligibility thresholds, and lexicographic selection rule were
frozen before the formal run.  Ten candidates pass, and the rule selects
\(s=0.11\), rather than the previously known passing hint \(s=0.15\).  This
removes step-level cherry-picking inside the declared grid but does not turn
the geometry itself into a preregistered discovery.

Within this deliberately narrow claim boundary, the audit finds no P0, P1, or
P2 defect.  The scientific promotion gates listed below remain open by design.

## Frozen evidence chain

| component | SHA-256 |
| --- | --- |
| producer `code/continuum_observable_four_patch.py` | `a553092f3d8bbf50fdf0124a3ea36ba32947c3b339cfcc0265a1cd7f6bc2d4da` |
| tests `code/test_continuum_observable_four_patch.py` | `c3a2c11c71daf9fcb04e1db9e7c4e489a515d7dfbbb51bc470d310d0c3f76243` |
| protocol `notes/observable_four_patch_protocol.md` | `cbfb6fbe7b69fb66f3b25f7bcde404929a53cf1e8d2045c5fa037fe0fa8432a1` |
| manifest `artifacts/data/continuum_observable_four_patch_manifest.json` | `1c79fcb31abbc622cee20e915d60f55337376d7555c1c25dab210b3cc5976a69` |
| result `artifacts/data/continuum_observable_four_patch_result.json` | `4a929cdaf915a9b6180acc0c272a16ae77087d097f2d078b6483c6c9b320a9fc` |

The producer verifies the first four hashes against the manifest before doing
the formal calculation.  A second full run to a temporary destination is
byte-identical to the result artifact and has the same result hash.  The
human-readable result note is downstream documentation and is not included in
the preregistered computational chain.

## Numerical result under attack

For the physical \(d=2\), \(\mathbb R\times\mathbb T_1\) geometry with
\(D=0.002\), OU stiffness \(0.1\), OU mean \(0.95\), contact radius
\(0.16\), initial half-width \(0.004\), and four patches of half-width
\(0.008\) centred at \((0.35,0.60,0.75,0.90)\), the fixed-\(w_0=0.28\)
slice gives the cusp

\[
 t_c=13.328031989459639,
 \qquad
 w_c=(0.28,0.2301948478196556,0.2093239647769527,
      0.2804811874033918).
\]

The scaled fourth derivative is \(-42.81178483244579\), the unfolding
singular-value ratio is \(0.2564052360511239\), and the largest scaled cusp
residual is \(1.10\times10^{-12}\).  The protocol-fixed strict inward normal
is

\[
 d=(0,0.357362931876667,-0.933965596218893,
       0.576602664342226).
\]

The selected step \(s=0.11\) has weights

\[
 w_*=(0.28,0.2695047703260889,0.1065877491928744,
       0.3439074804810367)
\]

and five alternating stationary points:

| type | time | density |
| --- | ---: | ---: |
| maximum | 3.204037879399 | 0.205485676850 |
| minimum | 5.085467473831 | 0.137014856945 |
| maximum | 8.688467026035 | 0.240579863273 |
| minimum | 13.328031989460 | 0.200031534136 |
| maximum | 22.660102216665 | 0.238831447697 |

The minimum/maximum peak-height ratio is \(0.8541266673541315\).  The two
valley-to-smaller-adjacent-peak ratios are \(0.6667854375339219\) and
\(0.8375426940831652\), respectively.  They pass the declared floors and
ceilings, although the second valley has only \(0.0124573059\) headroom below
the \(0.85\) ceiling.  This margin should therefore be treated as a numerical
quantity to preserve in later positive-budget and finite-element tests, not
as a qualitative visual impression.

## Independent attacks and reproducibility

1. A producer-free real Taylor-jet implementation independently recovers the
   cusp time, weights, fourth derivative, and unfolding ratio to the reported
   numerical precision.
2. A separate producer-free closed-real-derivative calculation at \(w_*\)
   recovers all five roots within \(1.1\times10^{-12}\), including their
   max--min--max--min--max ordering and the reported observability ratios.
3. Coarse, primary, and fine direct-continuum configurations agree: the cusp
   time spread is \(1.43\times10^{-11}\), the weight spread is
   \(1.02\times10^{-14}\), and the primary/fine scaled-fourth-derivative
   difference is \(8.84\times10^{-9}\).
4. The half-chord contact integral agrees with an independent polar-disk
   quadrature at \(t=1,5,13,25\), with maximum relative discrepancy
   \(6.61\times10^{-15}\).
5. Direct-product Cauchy jets agree with a factorwise Leibniz construction at
   order \(10^{-13}\), and the first Cauchy jet agrees with the closed real
   derivative at order \(10^{-16}\).
6. All ten focused tests pass.  Ruff lint and format checks pass.  The full
   formal result is byte-reproducible.

## Root-completeness limitation

The formal root census scans \(t\in[0.1,100]\) at spacing \(0.002\), refines
every retained sign-changing bracket, rejects the explicitly declared early
subfloor numerical-zero run, and checks that there is no above-floor sampled
plateau.  At the selected weights, the exact real derivative is positive at
\(t=0.1\) and negative at \(t=100\).  The independent dense scan finds the
same five roots.

This is strong floating-point evidence, not an interval-exhaustive proof that
no tangential double root or unresolved oscillation exists between samples.
Consequently `continuum_verified` remains false in the result schema.  An
interval root enclosure or an analytic variation bound is required before
using the stronger word "certified."

## Claim-boundary audit

The result flags are correctly negative or positive:

| flag | value | audit disposition |
| --- | --- | --- |
| `preregistered_discovery` | false | geometry and one passing hint were known before freeze |
| `continuum_verified` | false | no interval-exhaustive root certificate |
| `finite_B_Doi_verified` | false | no killed-Doi finite-budget solve at this geometry |
| `project_gate_passed` | false | physical \(d=3\), positive-budget robustness, and manuscript-level synthesis remain open |
| `observable_free_exposure_confirmation_passed` | true | supported by the frozen direct-continuum calculation |

The broader half-width-\(0.08\), initial-half-width-\(0.02\) variant is
recorded in the narrow manifest as known and excluded.  It requires a separate
protocol, producer, manifest, result, and audit.  It must not be substituted
for this geometry after seeing either result.

No main manuscript TeX file was edited in this round.

## Severity ledger

| severity | count | disposition |
| --- | ---: | --- |
| P0 | 0 | no unsupported finite-\(B\), interval, or PRR/project claim is made |
| P1 | 0 | frozen selection, observability thresholds, and evidence timing are explicit |
| P2 | 0 | independent derivatives, convergence, polar geometry, tests, and byte rerun agree |
| open promotion gate | 3 | interval root certificate, finite-\(B\) killed-Doi validation, and physical \(d=3\)/general theory |

