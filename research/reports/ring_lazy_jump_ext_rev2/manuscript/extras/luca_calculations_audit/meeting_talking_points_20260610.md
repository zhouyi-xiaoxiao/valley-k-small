# Meeting prep — Luca, MVB, 2026-06-10 morning

**Claim to answer:** "Simple algebra shows the long time has the log correction;
only a miraculous combination makes the coefficient of t·alpha^t disappear."

**One-sentence answer:** The t·alpha^t terms do appear in the expanded route — but
their *total* coefficient is q·f_l·g_l·[Σ_j c_j/(s_j−α_l) − β(1−q)/q], and the
bracket is identically zero by a 3-line partial-fraction identity; the "miracle"
is built into H, whose denominator contains the same W̃_u that creates the α-modes.

---

## 1. Meet his algebra head-on (agree first)

He will write the diagonal convolution
Σ_{c} α^{t−1−c}·α^{c−1} = (t−1)·α^{t−2}  ✓ correct — these terms exist in the
expansion. The question is ONLY their total coefficient.

## 2. Collect the coefficient (whiteboard, 2 lines)

The (t−1)α_l^{t−2} terms come from exactly two places (H(0)-group and H₊-group):

    −q·h₀·f_l(u,v)·g_l(n₀,u,v)·(t−1)α_l^{t−2}
    +q·f_l(u,v)·g_l(n₀,u,v)·(t−1)α_l^{t−2} · Σ_j c_j/(s_j−α_l)

    Total:  K_l = q f_l g_l [ Σ_j c_j/(s_j−α_l) − h₀ ],   h₀ = β(1−q)/q

## 3. The sum rule (3 lines, the "simple algebra")

With s = 1/z:   Ĥ(s) = Π_l(s−α_l) / [ a·Π_j(s−s_j) ]      (T_L and D factorized)
Partial fractions (deg L / deg L):  Ĥ(s) = 1/a + Σ_j c_j/(s−s_j)
Set s = α_m → LHS = 0 (numerator zero) →  Σ_j c_j/(s_j−α_m) = 1/a · a/q·... = h₀  ∎

So K_l ≡ 0 for EVERY l, every n₀, every (N, q, β>0). Nothing is tuned.

**If he asks "and the plain α^{t−1} terms?"** — they cancel too, with a second
(derivative) sum rule. Differentiate the partial fraction at s=α_m:

    Σ_j c_j/(s_j−α_l)² = −Ĥ′(α_l) = −T_L′(η_l)/(q·D(η_l)) = −L/q
    (D(η_l)=U_{L−1}(η_l) since T_L(η_l)=0, and T_L′=L·U_{L−1}  →  β-independent!)

Then the full plain-α coefficient collection (manuscript Eq. 63):
  • W-mode pieces (groups 2+3): q·h₀·g_l − q·g_l·Σc_j/(s_j−α_l) = 0   (value rule)
  • Off-diagonal pieces (groups 4+5): same bracket × (−qh₀ and +qh₀) = 0  (value rule)
  • Remainder: f_l(n₀,v) + q·f_l(u,v)·g_l·(−L/q) = f_l(n₀,v) − (N/2)f_l(u,v)g_l = 0
    (residue identity, since sin²((2l−1)πL/N)=1)
EVERY α-dependent term in the expansion cancels explicitly — no pole-reading,
no numerator argument, just collected coefficients. Only s_j^{t−1} survive.

**Why it's structural, not miraculous:**
H̃ = h₀ / (1 + zβ(1−q)·W̃_u(u,z)). The SAME W̃_u that supplies every α_l-mode
of W_{n₀}(u,·) and F_u(v,·) diverges in the denominator of H̃
→ H̃(1/α_l) = 0 at ALL the α's simultaneously (g_l(u,u,v)=2/N ≠ 0 for all l).
Double pole (numerator) × zero (H̃) = simple pole; the leftover simple pole
cancels against the baseline by f_l(n₀,v)·g_l(u,u) = g_l(n₀,u)·f_l(u,v).

## 4. Where HIS t·α^t coefficient comes from (the diagnosis)

The old kernels (s_k^t − x^t)/(s_k(s_k−x)) = Σ_{c=0}^{t−1} x^{t−1−c} s_k^{c−1}
use the pole expansion H(t″)=Σ c_k s_k^{t″−1} at t″=0.
But H(0) = β(1−q)/q, while Σ_k c_k/s_k = β(1−q)/q − c_∞, with

    c_∞ = T_L(1−1/q)/D(1−1/q) ≠ 0.       (N=10, q=2/3, β=4/7 → c_∞ = 2/11 exactly)

That substitution turns the bracket from 0 into +c_∞:
the "log correction" coefficient = q f_l g_l c_∞ = the time-zero boundary
mismatch of the H-expansion. It is an artifact, not a tail property.

## 5. The independent killer argument (no formulas needed)

For t≥1, F is a linear functional of powers of the transient submatrix
(delete row/col v). That submatrix is SYMMETRIC (shortcut only lowers the u
diagonal; the moved mass exits via the absorbing column).
Symmetric ⇒ diagonalizable ⇒ F(t) = Σ κ_i λ_i^t, pure geometric modes.
t·λ^t needs a Jordan block — impossible for a symmetric matrix, for ANY parameters.
Spectrum = {γ_r} ∪ {s_j}; the s_j strictly interlace the α_l for β>0,
so α_l is not even in the spectrum.

## 6. Numbers if asked (all in Appendix C.1.1 of the revised PDF)

- Exact finite-matrix PMF vs Σ_j B_j s_j^{t−1}: agree to 1.7e−52, t ≤ 600 (50-digit).
- F(t)/(t·α_1^t) → 0  (1.1e−12 by t=600, N=10 β=4/7);  F(t)/(B_1 s_1^{t−1}) → 1.
- Sum rule verified to 1.1e−50 for every l; K_l = 0 to 1.5e−52.
- Folded-kernel route: deviation/( (t−1)α_1^{t−2} ) → q f_1 g_1 c_∞ exactly.
- β-sweeps N=10/12/100 on (0,1]: γ_1 < s_1 < α_1 everywhere (no crossing).

## 7. Two analytic bonuses now in the PDF (Appendix C, p.19)

- **No crossing, ever:** at the γ_r locations U_{L−1}=0, so D = a·T_L = a(−1)^r ≠ 0.
  Hence s_j = γ_r is impossible for any β>0 — his proposed s_1=γ_1 transition
  criterion cannot occur. Sign bracket: D(cos π/L) = −a < 0 < 1/sin(π/2L) = D(η_1)
  ⟹ γ_1 < s_1 < α_1 for ALL 0<q<1, 0<β≤1 (proof, not sampling).
- **B_ρ1 > 0 strictly** (no "assuming B≠0"): B_ρj = qU_{ρ−1}(y_j)[T_L(y_j)−1]/[T_L(y_j)D′(y_j)];
  at y_1: T_L ∈ (−1,0), U_{ρ−1} > 0, D′ > 0 ⟹ B_ρ1 > 0. Grid-checked, 3486 cases, min 1.2e−4.

## 8. If pressed on residues (use gently, only if he doubts the c_j)

His printed Eq. (c_k) formula does not reproduce the residues of his own H:
numerically it is off by factors ~3×10³–2.6×10⁴ (e.g. k=1: −161.35 vs true −0.0062,
N=10, q=2/3, β=4/7). Quickest neutral self-check for him: compute H(1), H(2) from
the series of H̃ directly, then compare Σ_k c_k s_k^{t−1} with his c_k — it fails;
with c_j = qT_L(y_j)/D′(y_j) it matches to machine precision.
(Diplomatic framing: "the residue normalisation in Eq. (ck) seems off — with
residues taken directly from D the expansion reproduces H exactly.")

## Tone

- He partially fixed the sign issue after your minimal note (his 06-06 update uses
  the corrected 1+ denominator in the propagator and H), so the conversation is
  working — keep it collaborative.
- Concede what's true: the t·α^t terms DO appear mid-derivation (your Eq. 58 shows
  them explicitly). The disagreement is only about whether they survive collection.
- If he wants one thing to check himself: H̃(1/α_1) = 0 numerically, or
  Σ_j c_j/(s_j−α_1) = β(1−q)/q with his own c_k values.
