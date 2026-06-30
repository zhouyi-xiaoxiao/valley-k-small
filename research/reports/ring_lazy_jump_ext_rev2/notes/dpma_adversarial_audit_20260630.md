# DPMA package — Claude multi-agent adversarial audit (2026-06-30)

**Method:** 6 skeptic agents (one per claim cluster) attacked the 11 claims → each finding independently adversarially-verified (try to refute the finding itself) → a synthesis referee consolidated survivors. Tooling: Claude Code Workflow (`wf_f9fb1a8b-f2c`), opus, high effort; numerics on the repo venv (`.local-build/valley-k-small/.venv`, numpy+mpmath).

**Tally:** 33 findings raised, 31 survived adversarial verification. The mathematical core could not be broken on any derivation / physics / honesty axis; the package is held back by framing/honesty/prior-art defects.

---

## Synthesis referee

### PRR headline candidate
A directed transport shortcut to an absorber maps exactly, in the diffusive continuum limit, to 1D
first-passage with a tunable interior delta-sink (strength b, position theta=u/N), and the second
peak of the FPT density terminates at a threshold-free saddle-node bifurcation b_c=3.0764 (max+min
critical-point annihilation with sqrt(b_c-b) scaling; verified N-independently by the exact
finite-N chain). PRR-grade because it is a clean, classifier-free topological law - but only
headline-ready once the general-theta amplitude G_{xi,theta} is committed-verified and a working
master-function data-collapse figure exists.

### PRE headline candidate
Exact finite-N spectral control of a single directed-shortcut (rank-one diagonal killing) defect
on a lazy ring: the Montroll determinant D_u=a U_{N-1}+2 U_{u-1} U_{N-u-1}, the closed-form
channel-mass law pi_sc=rho/(a+L), and the uniform parallel-line spectral shift - a self-contained,
rigorously derived defect-resolvent theory whose antipodal case is the symmetric reduction, not an
isolated trick.

### Publishability recalibration
As-is the package is NOT submission-ready and the author's own as-is PRE estimate (10-15%) is
honest. Calibrated odds: PRE as-is ~10-15%; J.Phys.A ~55-65% (the exact finite-N results carry a
JPA paper today); PRE after rewrite ~60-70% (NOT 70-80% - the novelty-vs-Mattos/Godec/Giuggioli
gap is CONTENT, not framing, and can fail); PRR ~30-40% now, rising to ~50-60% ONLY after two
gating deliverables. The headline math (Laws 1/2/3, b_c, general-u determinant, channel law) is
correct and bulletproof; the gap to close is entirely honesty/framing/prior-art: (1) the four
'window boundary laws' (A(d), b_pl, N*, collapse asymptote) are analytic images of classifier
thresholds (10, 0.8, 0.1), not physics - reframe around the threshold-free b_c; (2) the
'G_{xi,theta} verified' claim is unbacked in the repo and the '6/6 gold-standard' is a self-
reproduction, not validation; (3) novelty over Giuggioli's defect-resolvent program (the
supervisor's own PRX) and Mattos 2012 (which is P(omega), not f(t)) is mis-stated and uncited; (4)
no working PRR collapse figure exists.

### Top actions (ranked)

1. RESOLVE THE TOP HONESTY DEFECT: either commit dpma_general_u_master_amplitudes.py that actually
   verifies general-theta G_{xi,theta} at theta=1/3,2/5 both branches to O(1/N^2) (math already
   reproduces ~3.9e-6 @ N=1200, ~30 min), or downgrade the 'VERIFIED/DONE' tags in the final report
   and integration note to 'TODO' to match the code header. Do not credit PRR for it until committed.

2. REFRAME THE BOUNDARY SECTION PHYSICS-FIRST: promote the threshold-free saddle-node b_c=3.0764 (add
   the analytic Phi'=Phi''=0 condition + the two fold diagnostics) and the convention-free constants
   M=3.700260, c_w(d) to headline; demote A(d), b_pl, N*, collapse-asymptote to convention-tagged
   classifier corollaries with the thresholds (H, VF) shown explicitly as parameters. Strike 'zero
   free parameters'/'exactly closed'/'gap closed' and the docstring 'no free input'.

3. FIX THE PRIOR-ART / NOVELTY FRAMING: cite Giuggioli PRX 2020 (supervisor's own defect-resolvent
   program) and Montroll-Weiss; correct the Mattos 2012 characterization (P(omega) ratio bimodality,
   not f(t)); scope novelty to the exact finite-N directed-shortcut determinant + pi_sc + parallel-
   line law (NOT the textbook delta-sink spectrum). Run the interior point-sink FPT prior-art search
   (Grebenkov/Bressloff/Lawley) and add the quantified known-vs-new paragraph the report's own panel
   demands.

4. PRODUCE THE SURVIVING PRR COLLAPSE FIGURE: plot Phi=(N^2/q)F vs tau for x=0.05 (Regime-A, both
   peaks diffusive, h1/h2->0.577) across 3-4 N and 2-3 b, plus the fixed-d=4 two-block collapse
   (diffusive block under (tau,b), capture peak under h1*N~q*b*c_w(d)/d). Correct the 'near-
   antipodal' attribution: the controlling variable is source-layer d=O(1), not theta near 1/2.

5. FIX THE ATTRIBUTION-TABLE pi_sc CONFLATION: state the first-peak time-local mass is only
   ~0.12-0.28 of the all-time channel integral pi_sc (3-4x gap; ~72-83% of shortcut absorptions
   arrive after the valley); quantify the factor once instead of 'measured < pi_sc'.

6. TIDY THE REMAINING MINORS: split the no-Jordan chain (symmetry=>no t*lambda^t; positive off-
   diagonals=>simple=>residue well-defined); add the simple-roots one-liner and the correct factor-2
   origin (cut-bond inverse hopping weight 2/q, not two boundary fluxes); add the b_c<=>6.15 unit-
   conversion sentence; correct the q-time-unit gloss (tau=q*t collapse is leading-order not exact);
   add mpmath/overflow guards to t~N^2 scans; rename '6/6 gold-standard' to 'implementation cross-
   check'.

### Overall
The DPMA package contains a genuinely strong, numerically bulletproof mathematical core (exact
finite-N single-defect spectral control: Montroll determinant D_u, channel-mass law
pi_sc=rho/(a+L), q-reduction via a*b=N, parallel-line spectral shift, and a real threshold-free
saddle-node b_c=3.0764) that I could not break on any derivation, physics interpretation, or
honesty axis. Every CONFIRMED finding survived adversarial re-derivation. The package is held back
almost entirely by framing/honesty defects, not correctness: four headline 'boundary laws' are
analytic images of classifier thresholds rather than physics, a key PRR-lever amplitude is marked
'verified' but is uncommitted (contradicted by its own code's TODO), the '6/6 gold-standard' is a
self-reproduction, and novelty over Giuggioli's defect-resolvent program (the supervisor's own
PRX) and Mattos 2012 (a ratio-bimodality result, not f(t)) is mis-stated and uncited.
Encouragingly, the package's own simulated referee panel already flags most of these as fatal, and
the correct fixes (b_c as headline, the delta-sink as a textbook correspondence, the finite-N
determinant as the real novelty) are half-built in-repo. Decisive verdict: ship to J.Phys.A now
(~55-65%); PRE/PRR are reachable only after the four gating actions above - chiefly committing the
general-theta verification, reframing around b_c, and fixing the prior-art citations.


---

## Confirmed findings (full)


### Laws 1–3 (channel-mass, spectral-shift, q-reduction)

**[MINOR] CONFIRMED** — Law 1 channel-mass: pi_sc=rho/(a+L) (antipodal) and general-u
pi_sc^(u)(r)=2min(r,u)[N-max(r,u)]/(aN+2u(N-u)), derived from a rank-one diagonal killing defect
at u via resolvent/renewal.

*Argument:* The derivation is a genuine Sherman-Morrison rank-one resolvent identity, not a fit. The shortcut
subtracts lam=beta(1-q) from the u self-loop, i.e. perturbs the pure-Dirichlet transient block by
exactly -lam*e_u e_u^T. The renewal/Dyson resolvent for a rank-one perturbation gives
G(r,u)=G0(r,u)/(1+lam G0(u,u)), so pi_sc=lam*G(r,u)=lam*G0(r,u)/(1+lam G0(u,u)). I verified
independently: (a) G0(i,j)=(2/q)min(i,j)(N-max)/N is the z=1 Green function of the bare Dirichlet
path (|err|<2e-13); (b) the Sherman-Morrison expression equals the exact lam*[(I-M)^-1]_{r,u} to
~1e-15 across N=40..200, including large beta=0.2; (c) lam*[(I-M)^-1]_{r,u} equals the explicit
time-summed flux sum_t lam*p_t(u) to ~1e-12, confirming the 'total mass absorbed via shortcut over
all time' interpretation; (d) channel split pi_sc+pi_direct sums to total mass=1.0; (e) antipodal
algebra rho/(a+L) follows cleanly (2L*rho/(aN+2L^2) with N=2L). The general-u formula matches
exact to 1e-14 across 4 configs including r>u and off-center u.

*Falsifier:* Build the (N-1)x(N-1) transient block for any (N,u,r,beta), compute lam*[(I-M)^-1]_{r,u}, and
compare to 2min(r,u)(N-max)/(aN+2u(N-u)); a disagreement above ~1e-12 at moderate beta would
refute. Also: if pi_sc+pi_direct != total absorbed mass, the conservation interpretation breaks.

*Fix:* None needed for the math. Optionally state explicitly in the report that the derivation is
Sherman-Morrison for a rank-one diagonal perturbation -lam*e_u e_u^T, which makes the rigor self-
evident to a referee.

*Verification:* holds=True, confidence=high, corrected_severity=minor


**[MAJOR] NEEDS-FIX** — Honesty admission: 'channel mass (pi_sc) != time-resolved first-peak mass'; the report's note says
measured pre-valley mass < pi_sc, and the TL;DR attribution table assigns the first peak's
'channel mass' to the pi_sc closed form.

*Argument:* The admission EXISTS (report lines 78-80 and footnote in the attribution table) but understates
the magnitude badly, which risks misleading a reader who skims the table. I measured: at
N=100,d=4,beta=0.02 pi_sc=0.307 but the pre-valley (first-peak) absorbed mass is only 0.070; at
beta=0.03 pi_sc=0.394 vs pre-valley 0.111. That is a 3-4x gap, not a near-equality. So saying the
first peak's mass 'is controlled by the pi_sc closed form' is actively misleading: pi_sc is an
all-time channel integral dominated by mass that arrives AFTER the valley (much of the shortcut
flux is slow). The phrase 'controlled by pi_sc' should not appear next to the first
(early/capture) peak. The conflation is, however, LOCALIZED: I verified the downstream
attributions (second peak = mode 1 ~100-115%, long tail = mode 1 single term) are time-resolved
mode shares at fixed t that never use pi_sc, so they are NOT tainted by this conflation.

*Falsifier:* Compute pre-valley cumulative F-mass vs pi_sc=rho/(a+L) for the C.2 window cells; if the ratio
were ~1 (within, say, 20%) the 'pi_sc controls the first peak' language would be fair. It is
~0.2-0.35, refuting that language.

*Fix:* In the attribution table replace 'its channel mass is controlled by pi_sc' with 'pi_sc is the all-
time shortcut-channel integral; the early-peak time-local mass is a small fraction of it (measured
~0.2-0.35 of pi_sc in the C.2 window)'. Quantify the gap once in the report so the admission
carries the actual 3-4x factor rather than the vague 'measured < pi_sc'.

*Verification:* holds=True, confidence=high, corrected_severity=major


**[MINOR] CONFIRMED** — Law 3 q-reduction: the characteristic determinant D(y)=a T_L(y)+U_{L-1}(y) contains no q; the
whole structure depends only on (N,d,b), with q entering solely as the time unit 1-s=q(1-y).

*Argument:* Verified exact. Key identity: a*b = q/(beta(1-q)) * beta(1-q)N/q = N exactly (checked across q in
{0.1,0.5,0.667,0.9}), so a=N/b is fixed by (N,b) with q absent. Thus the alpha roots y_j of D
depend only on (L,a)=(N,b), q-free; the full y-spectrum (alpha+gamma) is q-invariant at fixed
(N,b) to 1e-15 across q in {2/3,1/2,0.9}. (An apparent 4e-3 q-discrepancy I first saw was a pure
eigenvalue-ordering artifact from sorting s instead of y across near-degenerate alpha/gamma pairs;
it vanishes when the y-spectrum is compared as a set.) Amplitudes B_j=q*num(y)/D'(y) carry q only
as the explicit prefactor; in pi_sc=sum B_j/(1-s_j)=sum B_j/(q(1-y_j)) the q cancels, so pi_sc is
EXACTLY q-invariant (verified identical to 10 digits across q in {0.1,0.5,0.9,0.667}). Nothing is
hidden in the boundary/numerator terms. The report's caveat that window-classifier q-invariance is
only approximate (0.3-0.5% on the lower boundary) is correctly attributed to the classifier acting
on DISCRETE t (continuous tau=q*t collapses; discrete-t peak detection samples q-dependently) - an
honest and accurate statement.

*Falsifier:* At fixed (N,b), pick two q values, form the y-spectra and pi_sc; if y-sets differed above ~1e-13
or pi_sc differed at all, the exact-reduction claim would fail. It holds. Separately, if the
window boundary were q-invariant to machine precision, the 'approximate on window' caveat would be
over-cautious (it is not - discrete-t effect is real).

*Fix:* None for the law itself. Could strengthen by noting a*b=N is the exact mechanism (a is q-free),
and that pi_sc q-invariance is exact while window q-invariance is approximate purely from
discrete-time sampling - both already correctly characterized.

*Verification:* holds=True, confidence=high, corrected_severity=minor



### Claims 4 & 8 (boundary law A(d), classifier circularity)

**[MAJOR] NEEDS-FIX** — Claim 4: A(d)=C2(0)·d/(10(1-q)·c_w(d)) is a derived 'window boundary LAW' for the lower edge of
the clear-double-peak window (beta_lo·N^2 -> A(d)).

*Argument:* The formula is algebraically and numerically correct as a description of where the classifier's
lower edge sits, but its '10' is not a physical constant — it is literally HRATIO_HI, the
analyst's h2/h1 height-ratio threshold. The derivation (dpma_reduced_model.py) sets h2/h1 = 10 at
the lower edge, with h1 = capture peak = beta(1-q)·c_w/d and h2 = around peak = C2(0)/N^2 (treated
beta-independent), giving beta·N^2 = C2(0)·d/(10(1-q)c_w). I confirmed numerically that the lower
edge tracks the knob: the package's OWN artifact dpma_threshold_sensitivity.csv gives beta_lo·N^2
= 15.53/12.38/10.28 for H=8/10/12 (∝1/H to ~0.7%), and my independent bisection gave 18.33/9.13
for H=5/10 (ratio 2.01, exact 1/H). So A(d) is the analytic image of one classifier knob, not an
emergent physical law. The C2(0) and c_w(d) FACTORS are genuine physics (around-wave amplitude
q·M=2.46684 and capture-wave peak), and that two-component decomposition is a real, defensible
result. But calling the whole boundary a 'law' over-credits the convention-dependent prefactor.

*Falsifier:* Re-derive A(d) with HRATIO_HI=H general: it predicts A(d)=C2(0)·d/(H(1-q)c_w(d)), i.e. A∝1/H.
Running dpma_threshold_sensitivity at H=5,8,10,12,20 and checking beta_lo·N^2·H ≈ const (within
~1%, until another condition binds) confirms the '10' is the knob. If beta_lo·N^2 were INDEPENDENT
of H over a finite H-range, the boundary would be physical and this finding would be refuted.

*Fix:* Re-frame: report the two physical constants C2(0)=qM and c_w(d) as the result, and state
A(d)=C2(0)·d/(H(1-q)c_w(d)) with H exhibited as the explicit classifier parameter, NOT a baked-in
10. Lead with the saddle-node b_c (intrinsic) and present A(d) as the convention-dependent
observability scale = (physics)·(1/H).

*Verification:* holds=True, confidence=high, corrected_severity=major


**[MAJOR] NEEDS-FIX** — Claim 4 (plateau branch): the upper window edge is a plateau beta_hi·N -> ~3.147 / b_pl=1.5733,
characterized by the valley equation Phi(x_v)=0.8·Phi(x_p2).

*Argument:* Same defect as the lower edge: the '0.8' in the valley equation is VALLEY_FRAC verbatim. The
package's own dpma_threshold_sensitivity.csv shows the upper edge moves monotonically and smoothly
with the knob: beta_hi·N = 2.476 / 3.168 / 4.120 for valley_frac = 0.7 / 0.8 / 0.9 (N=100), 'no
cliff' as the report itself notes. dpma_binding_conditions.csv shows that JUST outside the upper
edge, valley_frac = 0.8059 universally across all N (44..240) — i.e. the upper edge is by
construction the level set {valley_frac = 0.8}. So 'b_pl=1.5733' is the value of the
valley_frac=0.8 contour, not an intrinsic plateau. The genuine physics here (the master function
Phi(x;b) from tan w=-2w/b, and that the valley/peak ratio is a single-valued function of b that is
N-invariant) is real and strong; the plateau NUMBER is convention.

*Falsifier:* Vary VALLEY_FRAC in {0.6,0.7,0.8,0.9} and recompute b_pl from the same Phi valley equation
Phi(x_v)=VF·Phi(x_p2); b_pl should move monotonically with VF (already shown: 2.476/3.168/4.120
for 0.7/0.8/0.9 in the finite-N artifact). If b_pl were stationary in VF over a finite interval,
it would be a physical plateau and this would be refuted.

*Fix:* Demote the plateau number to a convention-tagged observability edge: b_pl(VF). Present the
N-invariance of the valley/peak ratio vs b (which IS physical and convention-free as a function)
as the result, and let the reader pick VF.

*Verification:* holds=True, confidence=high, corrected_severity=major


**[MINOR] CONFIRMED** — Claim 4 (collapse asymptote): the collapse branch beta_hi·N^2 -> 100·A(d) because the two edges
share the same condition with ratio 10<->0.1.

*Argument:* Internally consistent and correctly stated as convention-dependent: 100 = (HRATIO_HI/HRATIO_LO) =
10/0.1, the two h2/h1 thresholds. Predicted 909 (d=3) vs Richardson ~917 is a fair ~1% match. The
report does not oversell this as physical — it explicitly ties it to the 10<->0.1 height-ratio
band. The arithmetic identity 100·A(d) inherits the same 1/H convention-dependence as A(d), but
that is stated.

*Falsifier:* If beta_hi·N^2 / beta_lo·N^2 deviated materially from HRATIO_HI/HRATIO_LO=100 (say converged to a
different ratio under large-N extrapolation), the 'same condition' story would break. The
~917/9.09 ≈ 101 measured ratio supports it.

*Fix:* None needed for correctness; just keep the explicit '100 = 10/0.1 = ratio of the two height-ratio
thresholds' caveat so it is never mistaken for physics.

*Verification:* holds=True, confidence=high, corrected_severity=minor


**[MINOR] NEEDS-FIX** — Claim 4 (binding switch): N*(d) = 10·C2(b_pl)·d/(q·b_pl·c_w(d)) with N*(3)~360, N*(4)~450.

*Argument:* N* is a real crossover (which of two classifier conditions binds the upper edge: valley_depth for
N<N* vs height_balance for N>N*), and dpma_binding_conditions.csv corroborates the mechanism
(lower edge fails at hratio≈10.15 i.e. height_balance; upper edge fails at valley_frac≈0.806 i.e.
valley_depth). But N* is doubly convention-dependent: it is the N where two THRESHOLD level sets
(the 10 and the 0.8) cross. The formula again hardcodes 10 and uses b_pl (itself the 0.8 contour).
Predicted 355/478 vs audit 360/450 — the d=4 match (478 vs 450) is ~6% off, weaker than the
report's tidy presentation suggests, and depends on C2(b_pl) evaluated at a single finite N=240
(not extrapolated).

*Falsifier:* Recompute N* with HRATIO band [1/H,H] and VALLEY_FRAC=VF as free parameters; N* must move with
both. If N* were invariant under reasonable threshold changes, it would be physical. Also:
extrapolate C2(b_pl) in 1/N (currently fixed at N=240) and check whether N*(4) prediction moves
toward 450 or stays at 478.

*Fix:* State N*(d) as the crossover of two named classifier conditions (valley-depth vs height-balance),
exhibit both thresholds as parameters, and give a 1/N-extrapolated C2(b_pl) with an error bar so
the 478-vs-450 gap is honestly bounded.

*Verification:* holds=True, confidence=high, corrected_severity=minor


**[MAJOR] NEEDS-FIX** — Claim 8: the C.2 classifier defines 'clear double peak' via first-two-time-peaks + 5 thresholds,
and the boundary laws are validated by the 'gold-standard 6/6 C.2 reproduction'.

*Argument:* The 'gold-standard' table is NOT an independent ground truth. The expected dict in validate_c2
(n0=1,2 clear on [0.002,0.030], n0=4,5,6 None) traces to notes/external_inputs/chatgpt_share_...md
line 51, which explicitly says '你们已有的 N=100 scan 就显示' — it is the SAME project's own earlier scan
of the IDENTICAL model under the IDENTICAL clear-double-peak notion. So '6/6 reproduction'
demonstrates code/implementation determinism (eigh vs Chebyshev, time-ordering, t=1 candidate
handling), not empirical validation of the labels. Predicting-your-own-classifier's-label IS
circular for the boundary laws: A(d) and b_pl are exact analytic images of the classifier's level
sets (shown above), so 'the law predicts the window edge' is tautological — the window edge is
DEFINED as the threshold crossing. The package partially escapes this with the saddle-node b_c (a
threshold-free topological boundary: existence of a (valley,peak) pair in F(t)), which I verified
runs and gives b_c(Phi)=3.0764 with the exact finite-N chain bracketing [3.05,3.10] at N=400 —
classifier-free. That is the correct escape. But the document still foregrounds the classifier
window as a 'law' and the saddle-node as an add-on.

*Falsifier:* Circularity test: pick ANY monotone feature map (e.g. a different 5-threshold rule) and you can
derive an equally-good 'boundary law' as the analytic image of those thresholds — the existence of
a clean A(d)-style formula is not evidence the boundary is physical. The non-circular core is
exactly the parts that survive removing the classifier: (i) the topological saddle-node b_c, and
(ii) the F(t)=capture+around two-component decomposition. Falsifier for b_c being physical: check
it is N-independent across N=400/800/1200 (report claims this; I only confirmed N=400 — run
dpma_saddle_node to comp

*Fix:* Restructure so the physics-first chain is the headline: (1) exact spectral master function
Phi(x;b) and tan w=-2w/b; (2) saddle-node existence boundary b_c (convention-free, N-independent —
finish the N=800/1200 verification); (3) the two-component capture/around decomposition with
physical constants C2(0)=qM and c_w(d). Then present the C.2 window strictly as a downstream,
convention-tagged observability sub-interval of (0,b_c), with A(d)=C2(0)d/(H(1-q)c_w) and b_pl(VF)
shown as explicit functions of the thresholds. Rename the '6/6 C.2 reproduction' from 'gold-
standard validation' to 'implementation cross-check (same model, same convention)'. Never call the
classifier window a 'law'.

*Verification:* holds=True, confidence=high, corrected_severity=major


**[MINOR] UNDER-CLAIMED** — C2(0)=q·M with M=3.700260 (theta-series max) and c_w(d)=d·max_t W_free(d,t) are physical constants
of the two-component reduced model.

*Argument:* These two constants ARE the genuinely physical, convention-free content of the boundary section,
and they are currently somewhat buried under the convention-laden A(d) framing. C2(0)=2.466836
(1/N^2-extrapolated) matches q·M=2.466840 to 6 figures and is d-independent (verified: d=3,4,5 all
give 2.46684) — a clean, non-trivial result tying the around-wave peak to the antipodal first-
passage theta-series maximum. c_w(d) -> e^{-1/2}/sqrt(2pi) continuum limit is also clean. These
deserve to be stated as the result, not as ingredients of a classifier-dependent prefactor.

*Falsifier:* If C2(0) showed residual d-dependence beyond extrapolation noise, or did not converge to q·M, the
physical interpretation would weaken. Verified d-independence to 6 figures and q·M match to 6
figures — robust.

*Fix:* Promote C2(0)=qM and c_w(d) (with continuum limits) to named physical results of the section;
present the observability scale A(d) as physics·(1/H) downstream.

*Verification:* holds=True, confidence=high, corrected_severity=minor



### Claims 5 & 6 (master function, saddle-node b_c)

**[MAJOR] CONFIRMED** — Claim 6: b_c=3.0764 is a genuine threshold-free saddle-node bifurcation of the first-passage
density's critical points; the second peak exists iff b<b_c.

*Argument:* I tested the actual bifurcation signature, not just the boundary value. (1) Critical-point count
of the continuum master function Phi(x;b): for b below b_c there is exactly one interior maximum
AND one interior minimum; at b_c their positions converge (0.0386 vs 0.0381) and BOTH disappear
simultaneously above b_c (count 1+1 -> 0). A max and a min colliding and annihilating is exactly a
saddle-node/fold. (2) I confirmed the normal-form scaling: the separation of the two merging
critical points Delta_x scales as sqrt(b_c-b), with Delta_x/sqrt(b_c-b) = 0.0248 held constant
across b_c-b = 1e-2 ... 1e-4 (two decades). That square-root law is the defining fingerprint of a
fold and rules out a smooth shoulder->peak (inflection) crossover, which would show no critical-
point pair and no sqrt scaling. (3) b_c=3.07643 from Phi is corroborated by the EXACT finite-N
chain: at N=400 the late interior maximum is present at b=3.07 and gone at b=3.08, straddling
3.076 with no classifier involved. (4) Existence is genuinely one-sided: the (valley,peak) pair
persists in Phi for all b down to 1e-4, so the region is (0,b_c). (5) Internal-consistency cross-
check: b_c=3.076 in b-units equals beta*N = b*q/(1-q) = 6.15, matching the independently quoted
physical merge edge beta_hi*N~6.15 in the ChatGPT digest. This is the strongest, most defensible
result in the cluster and is correctly labeled.

*Falsifier:* Would be refuted if (a) the critical-point count near b_c did not drop by exactly 2 (a max+min
pair), or (b) Delta_x/sqrt(b_c-b) drifted (non-constant) as b->b_c (indicating not a fold), or (c)
the exact finite-N chain bracket did not straddle 3.076 N-independently. None of these occurred.

*Fix:* None needed for correctness. For the manuscript, state explicitly the two diagnostics I ran
(critical-point pair annihilation + sqrt(b_c-b) separation scaling) as the proof it is a fold,
since 'saddle-node' will otherwise read as an assertion. Also note b_c is the merge/topological
boundary of Phi, distinct from the classifier window edge (the report already does this via the
6.15 vs 3.1475 distinction; keep it).

*Verification:* holds=True, confidence=high, corrected_severity=major


**[MINOR] CONFIRMED** — Claim 5: continuum reduction to [0,1] diffusion with interior delta-sink; root eq tan w = -2w/b,
mu_j=2w_j^2 exact; G_j amplitudes; b->0 recovers parallel-lines law mu_j -> (2j-1)^2 pi^2/2 + 2b
and theta-max M=3.700260.

*Argument:* The spectral skeleton is correct and the honesty about exactness is accurate. Verified: (i) mu_j
matches the exact Chebyshev modes to rel 1e-6..1e-4 at N=800 and converges as O(1/N^2); the root
eq tan w=-2w/b is the textbook delta-well-on-an-interval eigenvalue condition and is reproduced
exactly. (ii) The b->0 limit recovers w_j->(2j-1)pi/2, mu_j->(2j-1)^2 pi^2/2 and G_j->(-1)^{j-1}
2pi(2j-1) to all printed digits, and the +2b first-order shift (parallel-lines law) is recovered
with (mu-mu0)/b = 1.9998..2.0000 across j. (iii) max Phi/q -> 3.7003 as b->0, matching M=3.700260.
(iv) The report does NOT label Phi as exact: G_j is correctly flagged as leading-order 1/N. I
confirmed G_j rel error halves on N-doubling (1.07e-2, 5.49e-3, 2.78e-3, 1.40e-3 at
N=400/800/1600/3200; ratio->2), i.e. exactly O(1/N), matching the report's explicit caveat that
G_j is 1/N leading and Phi is ~0.55% off at N=800.

*Falsifier:* Refuted if mu_j did not converge O(1/N^2) to the exact modes, if the +2b coefficient were not 2,
or if G_j error did not scale O(1/N) (e.g. if it were O(1) the closed form would be wrong, not
just leading-order).

*Fix:* None for the math. Keep the explicit 'G_j is 1/N-leading, Phi not exact' caveat in the manuscript
exactly as in the final report; do not let the headline shorten it to 'exact master function'.

*Verification:* holds=True, confidence=high, corrected_severity=minor


**[MAJOR] NEEDS-FIX** — b_pl=1.57332 closes the plateau gap to measured 1.5738 at error 0.03% ('gap closed'); b_pl defined
by Phi(x_valley)=0.8*Phi(x_peak2) is given 'with no free input' (docstring of
dpma_master_function.py).

*Argument:* Two problems. (A) The '0.8 valley-depth ratio' is the C.2 classifier's threshold, NOT a physical
condition, so the docstring claim 'b_pl with no free input' (lines 17-20) is false. I confirmed
the dependence is steep: b_pl(thr=0.75)=1.390, b_pl(0.80)=1.573, b_pl(0.85)=1.788 -- a ~13% swing
per 0.05 of an arbitrary threshold. b_pl is a thresholded classifier quantity, not a physical
constant (the report's own section eight admits '0.8 都是人为阈值', but the code docstring and the 'no
free input' phrasing contradict that). (B) The '0.03% gap closed' precision is overstated/partly
fortuitous. The continuum uses leading-order G_j, which carries ~1-2% error at the measured
N=240-320. I perturbed the amplitudes by a 1% alternating-sign factor (the size of the real
finite-N G_j error) and b_pl moved by ~5% (1.573 -> 1.495 or 1.653). So a controlled comparison
should quote a b_pl uncertainty of order several percent, not 0.03%. The 0.03% agreement between a
leading-order continuum value and a finite-N measurement is within the noise of the approximation,
not a tight closure.

*Falsifier:* Refuted if b_pl were insensitive to the 0.8 threshold (it is not: 0.05 -> ~13%) and insensitive to
O(1%) amplitude error (it is not: 1% -> ~5%). Conversely, if a NEXT-order (1/N) corrected G_j were
derived and b_pl(N) then extrapolated to match 1.5738 within a stated few-percent band, the
closure would be controlled and this would upgrade to CONFIRMED.

*Fix:* (1) Delete 'giving b_pl with no free input' from dpma_master_function.py docstring; state b_pl is
the value of the classifier's 0.8 valley-ratio threshold in the continuum and report the
threshold-sensitivity table (0.75/0.80/0.85 -> 1.39/1.57/1.79) inline. (2) Replace 'error 0.03%,
gap closed' with an honest band: 'leading-order continuum b_pl=1.573; finite-N (leading-G)
amplitude error of ~1% implies a +-several-percent band, consistent with the measured 1.5738'. (3)
Demote b_pl from headline; promote the threshold-free b_c (Claim 6), which the report already
recommends in section eight.

*Verification:* holds=True, confidence=high, corrected_severity=minor


**[MINOR] NEEDS-FIX** — Novelty: the delta-sink continuum picture / spectral framework (tan w=-2w/b) and the exact single-
defect Montroll determinant D=a T_L+U_{L-1} have no counterpart in Mattos 2012 / Godec-Metzler
2016 (section four).

*Argument:* The transcendental spectrum tan w = -2w/b is literally the eigenvalue condition for a Dirac delta
potential/sink on an interval -- standard point-interaction quantum mechanics and standard in
first-passage 'partially reactive / point-sink' literature (Grebenkov and others). Presenting the
delta-sink spectral equation as new would be an over-claim. The report's defensible increment is
the EXACT finite-N spectral control via the single-defect Montroll determinant plus the closed
channel law pi_sc -- which is plausibly new -- but section four asserts 'no literature
counterpart' for the whole framework without quantifying against the cited papers, and the
report's own section eight concedes the novelty is 'asserted not quantified' (a self-flagged gap).

*Falsifier:* Refuted (i.e. the novelty claim stands) only if a literature search shows Mattos 2012 / Godec-
Metzler 2016 / Grebenkov sink papers do NOT contain (a) the interval delta-sink first-passage
spectrum and (b) an exact finite-N single-defect determinant for a directed shortcut. The delta-
well spectrum part is near-certain to have prior art; the finite-N determinant part is the
genuinely defensible piece.

*Fix:* Scope the novelty claim precisely: claim novelty for the EXACT finite-N rank-one-killing
determinant D=a T_L+U_{L-1} (and its general-u form) and the closed channel law pi_sc, NOT for the
delta-sink continuum spectrum (cite the standard point-interaction / point-sink first-passage
results for tan w=-2w/b). Add the one-paragraph quantified known-vs-new comparison section eight
already lists as a TODO.

*Verification:* holds=True, confidence=high, corrected_severity=minor


**[COSMETIC] CONFIRMED** — N*(d) binding-switch scale from exact master constants: N*(3)~348-355, N*(4)~466-478 vs measured
~360/~450.

*Argument:* The master-function run gives N*(3)=348, N*(4)=466 using the exact continuum C2(b_pl) and c_w(d);
the reduced-model run gives 355/478; both bracket the measured ~360/~450. The prediction inherits
the b_pl uncertainty (it uses b_pl and C2(b_pl)), so the ~3-5% spread between the two derivations
is consistent with the b_pl band found above, not a discrepancy. Fairly stated as 'predicted ~
measured'.

*Falsifier:* Refuted if N* predictions moved outside the ~340-480 range under reasonable b_pl variation, or if
measured N* were tightly pinned (it is quoted only as ~360/~450, i.e. itself approximate).

*Fix:* When the b_pl band is stated honestly (previous finding), propagate it to N* and quote N*(3) and
N*(4) with a corresponding +-few-percent band rather than single integers.

*Verification:* holds=True, confidence=high, corrected_severity=minor



### Claim 7 (general-u master function)

**[MINOR] CONFIRMED** — Spectral determinant D_u(y)=a U_{N-1}(y)+2 U_{u-1}(y) U_{N-u-1}(y) is the correct general-u
determinant, derived from the Dirichlet path + rank-one interior killing defect (matrix-
determinant lemma).

*Argument:* I re-derived this independently of the repo's V1 eigen-vanishing test. The transient matrix is A =
A0 - lam*e_u e_u^T (A0 = symmetric tridiagonal, diag 1-q, offdiag q/2; lam=beta(1-q) removed from
the u self-loop). I computed the characteristic polynomial det((1-q+q y)I - A) symbolically-
numerically at 50 dps and divided by the claimed D_u(y) at five distinct y values per case, for 7
cases including u!=N/2, u adjacent to the boundary, and odd N. The ratio was y-INDEPENDENT to
~1e-54 (machine zero) in every case, and equal to the fixed prefactor (q/2)^(N-1)*beta(1-q)*(3/2).
y-independence over the whole y-line (not just at roots) is a far stronger test than 'vanishes at
eigen-y' and proves D_u IS the spectral determinant up to a y-independent constant. The matrix-
determinant-lemma route det(I-zA)=det(I-zA0)*(1+z*lam*W0_uu) reproduces exactly the boxed
H_{N,u}=A_N/(aA_N+2A_uA_{N-u}) in the transcript. CONFIRMED, but the integration note tags it
plain VERIFIED without noting the residue formula B_rj=qN/D_u'(y_j) silently requires SIMPLE
roots.

*Falsifier:* Recompute det((1-q+q y)I - A)/D_u(y) at >=4 distinct y for any (N,u,beta); if the ratio varies
with y beyond 1e-40 (50 dps), D_u is wrong. Or find a (N,u,beta) where D_u has a genuine double
root (D_u=D_u'=0) -- then B_rj diverges and the claimed time-domain sum is invalid.

*Fix:* Add one sentence to the integration note §1 and the docstring: 'all roots simple (verified:
minimum eigenvalue gap >2.6e-4 across N<=89, all u, beta<=0.5; node-protected frozen modes are
generically non-degenerate with shifted modes); residue formula assumes this.'

*Verification:* holds=True, confidence=high, corrected_severity=minor


**[MINOR] CONFIRMED** — The cross-term coefficient is exactly 2: D_u = a U_{N-1} + 2 U_{u-1} U_{N-u-1}.

*Argument:* I tested alternative coefficients c in D = a U_{N-1} + c U_{u-1} U_{N-u-1} against the exact char-
poly (N=8,u=3,50 dps). c=2 gives y-spread ~3e-54 (exact); c=1 gives ~1.9e-5 and c=3 gives ~8.4e-6
(both fail y-independence by 49 orders of magnitude). The coefficient 2 is uniquely correct, not a
fitted/coincidental value. Origin: the 2 comes from the Green-function prefactor 2/(zq) in W0
combined with F0_r=(A_r+A_{N-r})/A_N (two boundary fluxes from sites 1 and N-1), so D_u = a A_N +
2 A_u A_{N-u}. The two-flux structure is physically the two ways the walk reaches the absorber v
from the path ends.

*Falsifier:* Set c!=2 in D and check vanishing at exact eigen-y for any non-antipodal (N,u): a nonzero residual
of order 1 (not roundoff) refutes any c!=2.

*Fix:* None needed; consider stating in the manuscript that the factor 2 is fixed by the two boundary
fluxes to v, so a reader sees it is structural, not empirical.

*Verification:* holds=True, confidence=high, corrected_severity=minor


**[COSMETIC] CONFIRMED** — The A_N-cancellation that collapses the apparent denominator A_N*D_u to D_u (yielding the
piecewise N_{r,u}) is rigorous, via A_{N-r}A_u - A_r A_{N-u} = A_N A_{u-r} (and mirror).

*Argument:* I verified both Chebyshev product identities at 40 dps over 200 random (N,r,u,y) draws each with
zero failures (tolerance 1e-25). These are the load-bearing identities making the spurious
A_N=U_{N-1} factor removable, exactly analogous to the antipodal T_L removable pole.
Independently, I confirmed the FULL collected generating function F^(u)_r(z)=N_{r,u}(y)/D_u(y)
equals the exact resolvent z*e_r^T(I-zA)^{-1}b to ~1e-16 at GENERIC z (0.3,0.7,0.95 -- not
eigenvalues) for the non-antipodal case N=14,u=5 across all r including r<u and r>u. This
validates the entire rank-one-update + cancellation chain, not just the spectrum.

*Falsifier:* Evaluate A_{N-r}A_u - A_r A_{N-u} - A_N A_{u-r} at random y for r<=u; any nonzero result (beyond
roundoff) breaks the cancellation and the piecewise numerator.

*Fix:* None.

*Verification:* holds=True, confidence=high, corrected_severity=cosmetic


**[MINOR] CONFIRMED** — The continuum limit is diffusion on [0,1] with absorbing ends and an interior delta-sink at
x=theta=u/N, giving the master spectral condition M_theta(w;b)=w sin2w + b sin(2 theta w)
sin(2(1-theta) w)=0; theta=1/2 reduces to tan w=-2w/b.

*Argument:* I derived this from scratch from -1/2 phi'' + b delta(x-theta) phi = E phi, phi(0)=phi(1)=0.
Piecewise phi=A sin(kx) on (0,theta), B sin(k(1-x)) on (theta,1), continuity at theta, and the
standard delta-jump phi'(theta+)-phi'(theta-)=2b phi(theta). Eliminating A,B gives -k sin k = 2b
sin(k theta) sin(k(1-theta)); with k=2w this is exactly w sin2w + b sin(2 theta w)
sin(2(1-theta)w)=0. theta=1/2 -> w sin2w + b sin^2 w=0 -> 2w cos w + b sin w=0 -> tan w=-2w/b. I
then confirmed numerically: discrete scaled spectrum N^2(1-s_j)/q at theta=1/3, N=900 =
[7.12,22.79,44.41,81.77,126.44] matches continuum 2w_j^2 = [7.12,22.79,44.41,81.78,126.44] to ~4
digits (clean O(1/N^2)). The derivation and the b=beta(1-q)N/q scaling are both correct.

*Falsifier:* Use the WRONG jump condition (e.g. phi'(theta+)-phi'(theta-)=b phi(theta), missing the factor 2)
and check against discrete spectrum: it would mispredict roots by O(1). Or test the continuum 2w^2
vs N^2(1-s)/q at a second theta and larger N; divergence beyond O(1/N^2) would refute.

*Fix:* Record the explicit jump-condition derivation (it is missing from both the integration note and
the transcript, which assert M_theta without showing the eigenproblem). The factor-2 in the jump
(and hence the 'b' vs '2b' normalization) is the one place a referee could trip; show it.

*Verification:* holds=True, confidence=high, corrected_severity=minor


**[MINOR] NEEDS-FIX** — (novelty/framing) 'A directed shortcut to the absorber becomes an interior delta sink in the
first-passage continuum limit' is presented as a PRR-flavoured headline physical insight; the
antipodal result is 'the symmetric reduction of a rank-one killing theory, not an isolated trick.'

*Argument:* The mathematics is correct and the reduction-of-rank-one framing is fair. But the delta-sink
continuum object itself is textbook: an interior point interaction (delta potential) on an
interval with Dirichlet ends is a classical solvable model (point interactions / Kronig-Penney /
Schrodinger delta well). The transcript's own PRR self-estimate (50-65% with the continuum master)
is internally generated by ChatGPT and is echoed in the note; the note correctly cross-checks it
against the repo's own panel (PRE-solid, PRR-reachable-only-after-reframing) and lands on the more
sober reading. So the note is mostly honest, but the phrase 'more PRR-flavoured / 更有 PRR 味道'
attached to the frozen-mode + delta-sink structure risks selling a standard mathematical-physics
correspondence as a new physical discovery. The novelty is the EXACT finite-N general-u Chebyshev
determinant and the channel-mass law, not the delta-sink limit per se.

*Falsifier:* A literature check finding interior-delta-sink first-passage / survival spectra already published
(they exist) would confirm the continuum object is not novel; conversely, finding no prior exact
finite-N Chebyshev determinant for a single tunable-position rank-one killing defect on a lazy
ring would confirm THAT is the real contribution.

*Fix:* In the manuscript, lead the novelty claim with the exact finite-N general-u determinant + channel-
mass law (genuinely the new result), and present the delta-sink limit as 'the continuum limit is
the (standard) interior point-interaction diffusion problem, which makes the spectral structure
transparent' -- a clarifying correspondence, not a new physics claim. Drop or soften the
unqualified 'PRR-flavoured' adjective.

*Verification:* holds=True, confidence=high, corrected_severity=minor


**[MINOR] NEEDS-FIX** — No-Jordan / no t*lambda^t theorem generalises to all u: deleting v leaves a symmetric Jacobi
matrix with +q/2 off-diagonals, hence simple real spectrum, hence no secular t*lambda^t tail at
any shortcut position.

*Argument:* The conclusion (no t*lambda^t tail) is correct and the symmetric-Jacobi argument is the right
reason: a real symmetric matrix is ALWAYS diagonalizable, so no Jordan block, so the PMF is a pure
geometric sum sum_j B_j s_j^{t-1}. However the stated chain 'symmetric Jacobi => simple => no
Jordan' overstates one link: positivity of off-diagonals (an unreduced Jacobi matrix) guarantees
SIMPLE spectrum, but symmetry ALONE already guarantees diagonalizability (no Jordan) even with
repeated eigenvalues. The 'simple' claim is the stronger one and it is what the residue formula
actually needs; my degeneracy scan (N<=89, all u, beta<=0.5) found min gap 2.7e-4 with no genuine
degeneracy, supporting simplicity in practice, but the note records 'no t*lambda^t' and 'simple'
as if one implies the other. They are logically independent (no-Jordan needs only symmetry).

*Falsifier:* Construct any symmetric matrix with a repeated eigenvalue (trivial) to show symmetry alone kills
Jordan blocks; separately, the unreduced-Jacobi simplicity theorem (Golub-Van Loan) needs strictly
nonzero off-diagonals, which holds here (q/2>0) -- exhibit it. A would-be counterexample to no-t-
lambda would require a defective transient matrix, impossible for a real symmetric one.

*Fix:* Split the statement: (i) symmetry => diagonalizable => no t*lambda^t tail for ANY u (this is the
robust theorem); (ii) strictly positive off-diagonals (q/2>0) => spectrum simple => residue
formula B_rj=qN/D_u'(y_j) well-defined. Cite the unreduced-Jacobi simplicity result for (ii).

*Verification:* holds=True, confidence=high, corrected_severity=minor



### Claims 9 & 10 (θ-collapse retirement, novelty/prior-art)

**[MAJOR] REFUTED** — Claim 9b (integration note line 175/196) — 'double peaks exist in the near-antipodal/competing-
branch geometry'; near-antipodal theta is offered as where the collapse lives and as the positive
control.

*Argument:* The operative variable is the SOURCE-LAYER distance d=|j0-u|=O(1), NOT proximity of theta to 1/2.
Two tests: (i) near-antipodal theta=0.45,0.48 WITH macro start xi=0.7 gives 0/30 double peaks at
N=180,300 — near-antipodality does NOT rescue a macroscopic start; (ii) strongly non-antipodal
theta=1/3,1/4 WITH a near-source start d=3,4 gives 18-21/30 double peaks (N=300) — just as many as
near-antipodal d=3,4 (20-21/30). So double peaks are generic for any theta once d=O(1); 'near-
antipodal/competing-branch' is a mis-attribution of the cause. The 140-double-peak positive
control quoted in the note must have used a near-source start, not merely a near-antipodal theta +
macro start.

*Falsifier:* Run the C.2 classifier over a b-grid for (theta, d) with theta strongly non-antipodal (e.g. 1/4)
and d=O(1) (3-4) at N>=300. If clear_double count is ~0, my claim is wrong. I measured 18-20/30,
refuting the near-antipodal framing.

*Fix:* Rewrite the note: replace 'double peaks exist in near-antipodal/competing-branch geometry' with
'double peaks exist for any shortcut position theta provided the start lies in the source layer
d=|j0-u|=O(1); the controlling variable is d, not theta.' State the positive control's actual
geometry (near-source start) explicitly.

*Verification:* holds=True, confidence=high, corrected_severity=minor


**[MINOR] CONFIRMED** — Claim 9c — The rho-prop-N family (fixed x=d/N=0.05) is a salvageable PRR collapse geometry: its
clear b-window is N-invariant.

*Argument:* Verified two ways. (1) The shipped CSV artifacts/data/dpma_rhoN_family_scan.csv has the x=0.05
clear-double b-window = [0.08275, 1.41659] IDENTICAL across N=60,80,120,160,240 (11 grid points
each); x=0.1 and x=0.2 give 0 clear doubles. (2) A genuine curve-collapse check I ran: at fixed
b=0.5, plotting Phi=(N^2/q)F vs tau=qt/N^2 for N=80,160,240 overlays to 4 significant figures (Phi
at tau=0.05/0.1/0.2/0.4 = 3.766/3.850/2.231/0.688 essentially N-independent; peak height 4.129 at
identical tau=0.0718). This is PRR-grade collapse.

*Falsifier:* If the Phi(tau) curves for x=0.05 spread by more than O(1/N) as N grows, or the b-window edges
drift on a finer grid, the collapse is fake. I saw <0.05% spread at N=80->240; deviations scale
O(1/N) consistent with subleading corrections.

*Fix:* Promote this to THE collapse figure: plot Phi_{x}(tau;b)=(N^2/q)F vs tau for 3-4 N at fixed x=0.05
and 2-3 b values, showing overlay + the N-invariant b-window. Caveat honestly: x=0.05 keeps d=x*N
growing, so this is a Regime-B matched-asymptotics curve (early peak fades as 1/N relative to late
peak), NOT the pure Regime-A Phi_{xi,theta}; the collapse holds in scaled (tau,b) coordinates for
the late/diffusive structure. Use a finer b-grid near the edges to show edge stability rather than
the 18-point coarse grid.

*Verification:* holds=True, confidence=high, corrected_severity=minor


**[MINOR] UNDER-CLAIMED** — Claim 9 (exact geometry/parameters to test) — what collapse geometry + parameters should be run.

*Argument:* The report only proposes x=0.05 vaguely. A sharper, more defensible PRR collapse exists: fix small
d=O(1) (the original antipodal C.2 geometry, d=3 or 4) and collapse in (tau=qt/N^2,
b=beta(1-q)N/q). This is Regime B but the LATE peak + valley + tail collapse cleanly because they
are governed by the continuum master Phi_theta(tau;b) (tan w=-2w/b at theta=1/2), which the report
already verified to 3.5e-6. The early capture peak is the only non-collapsing feature and it has
its own scaling h1*N ~ const. So the clean PRR statement is: the diffusive part collapses under b,
the capture peak collapses under d-scaling — a two-block matched collapse.

*Falsifier:* Overlay (N^2/q)F vs tau at fixed d=4 across N=200,400,800 at b=1.0. If the late peak/valley/tail
do NOT overlay (after the early-peak transient), the master-function collapse is wrong. The
report's own G_{xi,theta} verification (3.5e-6 @ N=1200) predicts they will.

*Fix:* Specify two collapse figures: (A) fixed d=4, vary N in {200,400,800}, vary b in {0.3,1.0,1.5};
show Phi vs tau diffusive-block overlay. (B) fixed x=0.05 full-curve overlay. State which features
collapse under which scaling (b for the diffusive block, d for the capture block).

*Verification:* holds=True, confidence=high, corrected_severity=minor


**[MAJOR] NEEDS-FIX** — Claim 10 (report §four, lines 185-189) — characterizes Mattos-Mejia-Monasterio-Metzler-Oshanin
2012 as prior 'double-peak first-passage (direct vs indirect paths)' phenomenology that this work
extends.

*Argument:* Mattos 2012 (PRE 86, 031143) bimodality is in P(omega), the distribution of the trajectory-
similarity ratio omega=tau1/(tau1+tau2) of two independent FPT realizations — an M-shaped
distribution of a RATIO, used to argue when the MFPT is meaningful. It is NOT bimodality of the
first-passage DENSITY f(t) in time. The DPMA report's double peak is in f(t) itself (two peaks in
time). Conflating these overstates the overlap with Mattos and mis-frames the novelty boundary.
The 'direct vs indirect' language is closer to two-length-scale bounded-domain geometry, again not
a two-peaked f(t).

*Falsifier:* Read Mattos 2012 Sec. on P(omega): if their headline bimodality is of f(t) vs t (not P(omega)),
this finding is wrong. The abstract/figures show M-shaped P(omega), confirming the distinction.

*Fix:* Rephrase: 'Mattos 2012 established bimodality of the trajectory-similarity ratio P(omega) as a
diagnostic for MFPT (in)validity in two-length-scale domains; our double peak is in the FPT
density f(t) itself, driven by an explicit competing-channel mechanism. The phenomenologies are
related (two timescales) but the observable differs.' This SHARPENS rather than weakens the
novelty.

*Verification:* holds=True, confidence=high, corrected_severity=major


**[MAJOR] REFUTED** — Claim 10 — novelty increment list (§four) asserts the single-defect Montroll determinant
D=aT_L+U_{L-1} 'unified framework' and resolvent channel law have 'no literature counterpart'
(文献中均无对应).

*Argument:* The rank-one resolvent / single-defect technique used here (pi_sc = lambda*G0/(1+lambda*G0(u,u)),
Montroll-Weiss defect determinant) IS the standard lattice defect technique. Giuggioli's program
(PRX 10, 021045, 2020 and follow-ups, e.g. multi-target search 2023) inserts absorbing/reactive
defects on bounded lattices via exactly this Green's-function rank-one (Dyson) update and gives
closed-form Green's functions/FPT with defects. The audit prompt explicitly names Giuggioli PRX
2020 as prior art, yet the report §four does NOT cite Giuggioli at all and claims method novelty.
Claiming the defect-determinant METHOD is new is an over-claim and is the most falsifiable novelty
assertion in the package.

*Falsifier:* Check Giuggioli PRX 2020 / arXiv 2311.00464: if they do NOT use rank-one Green's-function defect
insertion for absorbing sites, the method-novelty claim stands. They do (defect technique is the
paper's core), so the 'no literature counterpart' claim for the method is refuted.

*Fix:* Cite Giuggioli PRX 2020 explicitly. Re-scope the novelty: the defect TECHNIQUE is standard
(Montroll/Giuggioli); what is new is its application to a DIRECTED shortcut (off-self-loop rate ->
directed edge u->v) which produces a rank-one DIAGONAL KILLING defect (an interior absorbing
sink), not a reflecting/reactive site, plus the resulting closed-form channel-mass law pi_sc and
the uniform spectral-shift/parallel-line law. Drop '文献中均无对应' for the framework.

*Verification:* holds=True, confidence=high, corrected_severity=major


**[MAJOR] UNDER-CLAIMED** — Claim 10 (single most defensible novelty claim) — what is the genuinely new, defensible
contribution.

*Argument:* The package buries its strongest defensible novelty. It is NOT 'double-peak FPT' (Mattos/Godec
adjacent) and NOT 'defect technique' (Giuggioli). The single most defensible claim: a DIRECTED
interior shortcut to the absorber maps exactly, in the diffusive continuum limit, to a 1D first-
passage problem with an INTERIOR delta-SINK at x=theta=u/N, with closed-form transcendental
spectrum M_theta(w;b)=w sin2w + b sin2(theta w) sin2((1-theta)w)=0 (theta=1/2 -> tan w=-2w/b) and
a tunable defect POSITION theta and STRENGTH b. An absorbing interior delta-sink (mass-removing,
not reflecting/partially-reactive) with closed-form position-and-strength-resolved FPT spectrum is
the part least likely to be in Mattos/Godec/Giuggioli, all of which treat domain geometry or
boundary/site reactivity, not a directed-transport-induced interior killing measure with this two-
parameter master equation.

*Falsifier:* A prior-art hit that gives the FPT spectrum of 1D diffusion on [0,1] with an interior delta
absorber of tunable position+strength in closed form M_theta(w;b)=0 would refute novelty. Search
terms: 'first passage interior delta sink/killing tunable position', 'point sink first passage
interval spectrum', 'partially absorbing interior point diffusion FPT'. If
Grebenkov/Lawley/Bressloff already published this exact two-parameter spectrum, the claim
collapses to a re-derivation.

*Fix:* Make the headline: 'Directed interior shortcut = tunable interior delta-sink; closed-form two-
parameter (theta,b) FPT spectrum M_theta(w;b)=0.' Add a one-paragraph quantified prior-art table:
Mattos=ratio bimodality/MFPT validity; Godec=few-encounter proximity (no interior sink);
Giuggioli=defect technique for reflecting/absorbing SITES on lattices (no directed shortcut, no
continuum delta-sink master eq). Run the falsifier search before submission; this is the gating
prior-art check the report currently skips.

*Verification:* holds=True, confidence=high, corrected_severity=major



### Claim 11 + completeness critic

**[MAJOR] NEEDS-FIX** — CLAIM 11 ladder: PRE as-is ~10-15%, J.Phys.A ~55-65%, PRE after rewrite ~70-80%, PRR needs the
master function as headline.

*Argument:* The qualitative ordering is honest and the as-is PRE number (10-15%) is realistically self-
critical — most groups would over-rate themselves here, so credit for that. But three calibration
problems make the upper rungs optimistic. (a) PRR ~50-65% (the cross-checked ChatGPT/panel range)
is anchored on the general-u + continuum master function as the headline lever, yet that lever's
amplitude formula G_{xi,theta} is NOT actually verified in the repo (see next finding) — the PRR
estimate is conditioned on work the package asserts done but has not delivered. Discount PRR to
~30-40% until G is verified and a real collapse figure exists. (b) 'PRE after rewrite ~70-80%'
treats the rewrite as pure framing ('落差全在 framing, 不在 correctness'). That is the classic author
blind spot: the referees' cited fatal point #3 (novelty vs Mattos 2012 / Godec-Metzler 2016 'only
asserted, not quantified') is a CONTENT gap, not framing — quantifying genuine novelty against
PRX-level prior art can fail, and would cap PRE nearer 55-65%. (c) The two independent estimates
'agreeing' (panel vs ChatGPT) is weak corroboration: ChatGPT proposed the general-u result, so its
optimism and the panel's optimism share a common, still-unverified, source. Net: ladder is
directionally right but the PRR and post-rewrite-PRE rungs are 10-20 points high.

*Falsifier:* If, after (i) a committed script verifies G_{xi,theta} to O(1/N^2) across both branches AND (ii) a
quantified one-paragraph novelty delta vs Mattos2012/Godec2016 with a concrete metric is written,
an independent first-passage referee rates post-rewrite PRE >=70% and PRR >=50%, the ladder stands
as-is. If either gating item cannot be delivered, the rungs are confirmed optimistic.

*Fix:* Re-state the ladder as conditional: 'PRR ~30-40% NOW, ~50-60% ONLY after G_{xi,theta} is verified
and a working collapse figure exists'; 'post-rewrite PRE ~60-70%, gated on a quantified novelty
paragraph not just reframing'. Drop the 'agreement of two estimates' as corroboration or note the
shared-source dependency.

*Verification:* holds=True, confidence=high, corrected_severity=major


**[BLOCKER] REFUTED** — Continuum amplitude G_{xi,theta}(w;b) for general (non-antipodal) theta is VERIFIED: '6
macroscopic configs (both branches), max rel dev 3.5e-6 @ N=1200, clean O(1/N^2)' (final report
line 171; integration note item 2 ✅ and to-do #2 'DONE round-3').

*Argument:* The prose claims directly contradict the only committed general-u artifact.
code/dpma_general_u_master.py (the NEWEST file, regenerated 2026-06-29) states verbatim in its
header: 'NOT yet verified (stated by source, left as TODO): closed-form continuum amplitudes
G_{xi,theta}(w;b); the macroscopic two-peak window W_{xi,theta}.' Its output
artifacts/tables/dpma_general_u_master.txt verifies V1-V6 = determinant, finite-N time domain,
channel mass, spectral shift, antipodal reduction, and the SPECTRAL EQUATION M_theta — but
contains NO amplitude (G) verification at all. I grepped the entire code/ and artifacts/ tree: the
strings '3.5e-6', 'N=1200', 'macroscopic config', '0.996' (the claimed normalisation) and any
general-theta G test appear in NO script or table; only the ANTIPODAL theta=1/2 amplitude is
checked (dpma_master_function.txt V1, rel dev ~0.2-0.5% at N=800, i.e. O(1/N), not 3.5e-6 and not
general-theta). Therefore the central PRR-lever verification is asserted in two narrative files
but does not exist as reproducible evidence in the package. This is exactly the kind of unbacked
claim a referee or a reproducibility check would catch, and it sits under the result the report
itself nominates to headline PRR.

*Falsifier:* Produce/point to a committed script that evaluates the closed-form G_{xi,theta}(w_j;b),
reconstructs (N^2/q)F^(u)_r(t) -> Phi_{xi,theta}(tau;b) for theta in {1/3,2/5}, xi on both
branches, and shows max rel dev ~3.5e-6 at N=1200 with O(1/N^2) decay. If such a script reproduces
the claimed numbers, this is REFUTED-as-finding (claim was true). Currently no such artifact
exists.

*Fix:* Either (a) add and commit dpma_general_u_master_amplitudes.py that actually performs the
G_{xi,theta} verification and writes a table, then keep the ✅, OR (b) downgrade final-report line
171 and integration-note item 2 / to-do #2 from '已验证/✅ DONE' to '〜 PLAUSIBLE — spectral eq +
antipodal amplitude verified; general-theta amplitude NOT yet checked (TODO)', matching the code
header. Do not headline PRR on an unverified amplitude.

*Verification:* holds=True, confidence=high, corrected_severity=major


**[MINOR] CONFIRMED** — Threshold-free saddle-node boundary b_c = 3.0764: 'the second peak exists iff b < b_c'; exact
finite-N chain gives bracket [3.05,3.10] N-independent (N=400/800/1200), nominated as the
headline-grade intrinsic result.

*Argument:* I reproduced the Phi-based b_c independently: phi() has a topological (valley, late-peak) pair for
b<=3.07 and loses it for b>=3.08 — genuinely threshold-free (pure extremum topology, no 0.8/0.1/10
cut), bisection -> 3.076. This is the correct choice for a PRR/PRE headline because it removes the
referees' unanimous fatal point #1 (window constants are classifier outputs). It is also UNDER-
played relative to its strength in one place: the report keeps presenting classifier window
constants (A(d), b_pl=1.573) as co-equal results, when b_c subsumes them as the intrinsic
statement. NOTE this is the single result I'd headline for BOTH venues: for PRE as the physical
upper boundary; the general-u master function is the PRR differentiator ONLY once G is verified.

*Falsifier:* If an independent extremum-tracking of Phi(x;b) (finer grid, or analytic d/dx Phi=0 double-root
condition) places the saddle-node anywhere outside [3.05,3.10], or if the finite-N coalescence is
found to drift with N (not N-independent) once float overflow in evaluate() is replaced by mpmath
at large t, the claim is weakened.

*Fix:* Promote b_c to the lead intrinsic result in section 八 and the abstract; demote A(d)/b_pl to
'classifier-window corollaries (thresholded sub-interval of (0,b_c))'. Add a one-line analytic
saddle-node condition (Phi'=Phi''=0) so b_c is a solved equation, not just a bisection number.

*Verification:* holds=True, confidence=high, corrected_severity=minor


**[MINOR] NEEDS-FIX** — Internal consistency of the two 'physical merge' numbers: saddle-node exact chain bracket b in
[3.05,3.10] (dpma_saddle_node.txt) vs integration-note 'bare merge edge beta_hi*N ~= 6.15' at d=3.

*Argument:* These look contradictory (3.05-3.10 vs 6.15 for the same d=3 coalescence event) and a referee
skimming both files will flag it. They are in fact the SAME event in different units:
saddle_node.py sets beta = q*b/((1-q)*N), so beta*N = q/(1-q)*b = 2*b at q=2/3, and b in
[3.05,3.10] maps to beta*N in [6.10,6.20], matching 6.15. So no error — but the package never
states this conversion, and uses 'b' and 'beta_hi*N' interchangeably as 'the merge edge' across
two documents. That is a presentation defect that undercuts the credibility of the headline b_c.

*Falsifier:* If beta*N = (q/(1-q))*b does NOT hold for the convention actually used in both scripts (check
evaluate() call signatures), then there is a real numeric inconsistency rather than a units gap.

*Fix:* Add one sentence wherever b_c and the 6.15 merge edge co-occur: 'in beta*N units, b_c=3.076 <=>
beta*N = (q/(1-q))*b_c = 6.15 at q=2/3', so the saddle-node and the source-layer merge edge are
the same event.

*Verification:* holds=True, confidence=high, corrected_severity=minor


**[MAJOR] NEEDS-FIX** — Completeness / referee-catchable gaps across the package (the explicit prompt list: continuum
amplitude G at small tau, multiple shortcuts, non-Hermitian u->w!=v, elementary closed forms for M
/ c_w / b_pl; plus a real PRR collapse figure).

*Argument:* Enumerating what a referee would catch as missing/unverified: (1) [most serious] general-theta
G_{xi,theta} verification absent (see blocker above) — and with it, no SMALL-tau behaviour of Phi
is documented anywhere: dpma_master_function V2 only samples x>=0.01 and reports a flat ~0.5%
bias, so the claimed integral-normalisation ∫Phi dtau=0.996 and the small-tau (capture-region)
amplitude are untested; matched-asymptotics Regime B is described but never assembled into a
single validated F = F_early + (q/N^2)Phi curve. (2) NO valid PRR collapse figure exists: the
theta-collapse figure was REFUTED and retired (0/60 double peaks at fixed non-antipodal theta),
and the proposed replacement (rho∝N x=0.05 family, or near-antipodal geometry) is named but the
collapse FIGURE itself is not produced — a PRR submission cannot headline a master function with
no working data-collapse plot. (3) Multiple shortcuts: only the m×m determinant structure
det[I+zΛW0_UU] is sketched (integration note §5) — no derivation, no numeric check, correctly
tagged future. (4) Non-Hermitian u->w!=v: pure prose, zero calculation; the interesting claims
(complex eigenvalues / exceptional points / transient amplification) are unverified speculation —
fine as 'discussion' but must not leak into novelty claims. (5) M=3.700260, c_w(d), b_pl=1.573
have NO elementary closed form — they are roots of transcendental/thet…

*Falsifier:* For each: (1) a committed script reconstructing the full matched-asymptotic F and showing ∫Phi=1
to small-tau resolution; (2) a committed collapse figure (multiple N) for the surviving family;
(6) re-running the large-N saddle-node/boundary scripts in mpmath and getting the SAME brackets.
If all reproduce, the gaps are closed.

*Fix:* In section 八, add an explicit 'verified vs asserted vs future' table: VERIFIED (antipodal master
fn + amplitude, A(d), pi_sc, spectral shift, b_c, finite-N general-u D_u/F/pi_sc); ASSERTED-BUT-
UNVERIFIED (general-theta G, small-tau Phi, ∫Phi=1, merge-edge largeN under float64); FUTURE
(multiple shortcuts, non-Hermitian, inverse tomography, elementary forms of M/c_w/b_pl). Produce
the surviving collapse figure before claiming PRR-reachable. Add mpmath/overflow guards to all
t~N^2 scans and re-confirm b_c.

*Verification:* holds=True, confidence=high, corrected_severity=major

