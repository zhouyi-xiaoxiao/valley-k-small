# Round 48: Supplement mathematical repair record

Date: 2026-07-14  
Role: implement the findings of
`audits/round_46_supplement_math_attack.md` in the standalone analytical
Supplement  
Status: **repair implementation complete; this file is not an independent
mathematical re-audit**

## Scope and mutation boundary

The task-owned edits are limited to:

1. `manuscript/encounter_multimodal_prr_supplement.tex`; and
2. this repair record.

The main manuscript, positive-budget producer, post-result auditor, numerical
results, manifests, and protocols were not edited by this task.  The two clean
builds and rendered QA pages were written only under `/tmp`.  No compiled
Supplement PDF was published into the manuscript directory.

Round 46 input audit SHA-256:
`89d5799d08cff07b80104f7c571d055dbd59ba38dac1add8a227d37977571f0e`.

## Repair result

Every Round 46 P1/P2 item was implemented without widening the theorem scope or
changing the sequential limit order.

| Round 46 item | Implemented repair |
| --- | --- |
| P1.1 initial-state domain | Declared control- and budget-independent `q0`; added bounded `L2` and unbounded `X_pi` alternatives; separated arbitrary Hilbert-space data from nonnegative unit-mass probability data; normalized `pi`; specified positive-time versus integrated mass balance. |
| P1.2 nonsquare fold/cusp assembly | Replaced the ambiguous vector-control inverse by a frozen one-dimensional fold tangent and a frozen isometric two-plane `E` for the cusp; defined square maps; factored the cusp Jacobian; applied Weyl to the same restricted matrix `R_B E`. |
| P2.1 Cauchy margin | Defined an enlarged `2 delta` complex tube containing every closed radius-`delta` control polydisc. |
| P2.2 Dyson/time domain | Printed the ordered simplex and every intermediate free factor using an ordered product; restricted complex analyticity to `Re z > 0`, stated boundary norm extension separately, and restricted positivity/mass decrease to real nonnegative data and time. |
| P2.3 wrapped contact tail | Replaced the image-chart wording by a cylinder-geodesic separation inequality; added covariance eigenvalue bounds, a differentiated Gaussian-image majorant, lattice summability, and the normalized tail-integral identity. |
| P2.4 `W` to `Theta` | Constructed a frozen tangent chart for the compact interior weight set and explicitly invoked the enlarged complex tube after fixing `epsilon`. |
| P2.5 balanced peaks | Reapplied the theorem to the singleton balanced weight; separated the free maximum `t^{G,*}` from the Doi maximum `t^{B,*}`; printed `O_epsilon(B^2)` and the fixed-`epsilon`, `B downarrow 0` order. |
| P2.6 normalization domains | Specified `I_z` versus `R` profile normalization and inserted the normalized reversible density. |

The own-channel proof was also made more explicit by printing

\[
 A_j''(y)=\frac{\mu'(t_j)^2}{S(t_j)^2}
 \left(\frac{\mu'(t_j)^2y^2}{S(t_j)^2}-1\right)A_j(y)
\]

and choosing
\(0<L_0<\min_j S(t_j)/|\mu'(t_j)|\), subject to the predeclared target
neighborhoods.

## Preserved mathematical boundaries

The repaired source retains the exact direct-theorem order

\[
 \exists\epsilon_0>0\;\forall\epsilon\in(0,\epsilon_0)\;
 \exists B_0(\epsilon)>0\;\forall B\in(0,B_0(\epsilon))\;
 \forall w\in\mathcal W.
\]

It still does not assert:

- an interchange of the `epsilon` and `B` limits;
- a `B0` uniform as `epsilon` tends to zero;
- one geometry supporting unbounded mode count;
- an exact global root count or nondegenerate separator minima;
- a positive absolute event-mass floor;
- a finite-parameter numerical cusp/fold certificate;
- finite-volume, box, or discretization convergence;
- arbitrary localized catalysts or dimensions beyond physical `d=2,3`; or
- Lean verification of the semigroup, wrapped-tail, or fixed-mode theorem.

## Source and reproducible build snapshot

| Artifact | SHA-256 |
| --- | --- |
| pre-repair Supplement source | `23dd99b2e836eb6d1bfd90dc6e8cddaab955fb8725bc09d7436e5ef37e94446d` |
| repaired Supplement source | `de75e5a37adb83175f27ce8e1e78846c54781a858c4ff5411daab7b12e222278` |
| clean-build PDF A | `40fed2e0ff7fd1b6745db6a3b0ba4e6966d55b813f0b84c8b7247b42752cba88` |
| clean-build PDF B | `40fed2e0ff7fd1b6745db6a3b0ba4e6966d55b813f0b84c8b7247b42752cba88` |

The repaired source has 1,186 lines, 4,352 words, and 45,953 bytes.

Both builds used TeX Live 2025 through the repository-independent LaTeX
compile helper, with
`SOURCE_DATE_EPOCH=1783987200`, in separate initially empty directories:

- `/tmp/round48-supp-a.ReGtUQ`;
- `/tmp/round48-supp-b.eBNH8L`.

Both `latexmk` runs exited zero.  `cmp` returned zero, so the two PDFs are
byte-identical.  The common PDF has:

- 12 pages;
- 468,642 bytes;
- US Letter media box, `612 x 792` points;
- PDF version 1.7;
- no encryption; and
- embedded, subset fonts throughout.

The two logs contain no undefined citation/reference, overfull box, underfull
box, fatal error, or emergency stop.  Their only warning is the same harmless
RevTeX/hyperref `nameref` message replacing the changed `label` definition with
the kernel definition.  Critical pages covering the Dyson expansion,
fold/cusp slices, wrapped-tail proof, compact-weight bridge, and balanced-peak
corollary were rendered and visually checked; no clipping, overlap, malformed
equation, or reader-visible spacing token was found.

## Acceptance and remaining HOLD boundary

This record establishes that the requested repairs are present and that the
source has a deterministic clean build.  It does **not** constitute an
independent confirmation that no further mathematical defect exists.  A later
agent should re-read the repaired snapshot without relying on either Round 46
or this implementation record.

The Supplement can proceed to that re-audit.  PRR scientific release remains
**HOLD** independently of this repair, pending the same-family finite-parameter
allocation cusp and fold structure, event-mass-qualified multimodality,
odd/even mesh and box continuation, and an independent unbounded/off-lattice
killed-process validation without refitting.
