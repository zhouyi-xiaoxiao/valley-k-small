# PRR manuscript draft (reframed headline) — 2026-06-30

Draft for Physical Review Research (fallback: PRE). English, submission-style structure.
Honesty tags: **[proven]** analytic; **[verified]** numerically (tolerance stated); **[conjecture]**
numerically robust but unproven. Figures = `artifacts/figures/dpma_prr_figures.pdf` (A–F).
Prior-art is literature-checked (WebSearch, 2026-06-30). NOT to be pushed to the public repo
until Luca signs off on venue.

---

## Title (candidates)
1. **Saddle-node bifurcation of first-passage-time densities induced by a directed shortcut**
2. Topology-changing first-passage dynamics from a rank-one non-Hermitian defect
3. A single directed shortcut turns first-passage bimodality into an exactly solvable catastrophe

## Abstract (draft)
First-passage-time (FPT) densities in systems with a shortcut to the target are known to be
bimodal — a fast "direct" peak and a slow "indirect" peak. We show that this bimodality is the
observable-level signature of a **saddle-node bifurcation** that can be solved exactly. Modeling a
directed shortcut as a rank-one killing defect on a lazy lattice (continuum limit: diffusion with
an interior δ-sink of strength b at fractional position θ), we prove that the second FPT peak is
born and annihilated at a fold of the signed spectral mixture, characterized by the compact
criterion **S₁=S₂=0** (S_n=Σ_j G_j μ_j^n e^{−μ_j τ}; f′=−S₁, f″=S₂). The double peak exists **iff
0<b<b_c(θ)**, with an explicit boundary b_c(θ) (symmetric, minimum near θ≈0.38, endpoint law
b_c∼0.789/min(θ,1−θ)); at least three sign-alternating modes are required (two are impossible),
and the fold obeys the universal normal-form scaling gap∼(b_c−b)^{1/2}, prominence∼(b_c−b)^{3/2}.
The mechanism is generic, not lattice-specific: it follows model-independently from a low-rank
non-Hermitian defect (Woodbury), it generalizes to multiple shortcuts (two shortcuts produce a
**third** FPT peak organized by a cusp), and it survives on a two-dimensional lattice. The
threshold b_c is a time-domain morphology fold, **not** a spectral exceptional point. The result
turns a known phenomenology into a predictive, exactly solvable bifurcation with a measurable
threshold and universal scaling, testable in feedback-controlled colloidal search and engineered
transport networks.

## I. Introduction / significance
- **Known.** (i) A shortcut/relocation channel makes FPT densities bimodal — direct-vs-indirect
  paths, with a timescale-separation window [Godec–Metzler, PRX 6, 041037 (2016); small-world FPT
  literature]. (ii) Interior partially-absorbing / narrow-capture traps give multimodal capture-time
  densities when strategically arranged [Bressloff; Grebenkov]. (iii) Exact lattice-defect /
  Green-function methods are established [Giuggioli, PRX 10, 021045 (2020); Montroll–Weiss].
- **Gap.** These *exhibit* multimodality but do not classify or predict *when* a second peak exists
  as a control parameter varies — there is no bifurcation-theoretic account with a predictive
  threshold.
- **This work.** For a minimal directed-shortcut (rank-one killing) defect we give the exact
  bifurcation theory: a saddle-node criterion, the explicit existence boundary b_c(θ), a
  minimal-mode theorem, universal fold scaling, and universality (multiple shortcuts, 2D). Broad
  message: FPT distributions contain controllable time-domain structure — an emergent arrival-time
  scale with a sharp threshold — invisible to mean first-passage times and to spectral gaps.

## II. Model **[proven]**
Lazy ring of N sites (stay 1−q, hop q/2 each way), absorbing target v=0; a directed shortcut at
source u moves rate λ=β(1−q) off the u self-loop onto u→v. Deleting v leaves a Dirichlet path with
a **rank-one diagonal killing defect** −λe_u e_uᵀ (the transient generator stays symmetric even
though the shortcut is directed — verified: real spectrum). Exact generating function /
Montroll determinant D_u(y)=a U_{N−1}+2 U_{u−1} U_{N−u−1} (a=q/λ); F(t)=Σ_j B_j s_j^{t−1}.
Continuum limit (θ=u/N, b=β(1−q)N/q, τ=qt/N²): diffusion on [0,1] with an interior δ-sink,
spectral function D_θ(k;b)=k sin k + 2b sin(kθ)sin(k(1−θ))=0 (θ=1/2 → tan w=−2w/b), μ_j=k_j²/2.
Amplitudes G_{ξ,θ}(w)=2w²φ_{w,θ}(ξ)I/J (affected) + node term nπ[1−(−1)ⁿ]sin(nπξ) **[derived from
the defect resolvent (Sherman–Morrison residue), App. B; every intermediate verified — I/J closed
forms vs ∫φ,∫φ² to 1e-9, the exact identity J=sin(k)D_k/(4b) to 3e-15, the δ-sink jump condition
to 2e-14; full curve vs exact residues 1e-5 O(1/N). N→∞: fixed-mode residue convergence is
standard 1D operator theory; uniform C¹ moment convergence near the fold is an explicit,
labeled assumption. See `notes/dpma_amplitude_derivation_20260630.md`]**.

## III. Existence theorem (the headline) **[proven criterion + verified constants]**
With S_n(τ;b)=Σ_j G_j μ_j^n e^{−μ_j τ}, f′=−S₁ and f″=S₂, so the second peak is born/annihilated at
a **saddle-node**: **S₁(τ_c,b_c)=0, S₂(τ_c,b_c)=0**, nondeg S₃≠0, ∂_b S₁≠0. Consequences:
- **Existence:** the second peak exists iff **0<b<b_c(θ)**; b_c(θ) is a single fold — no re-entrant
  window **[verified: single contiguous b-interval at θ=0.5,0.3]**.
- **Boundary b_c(θ):** symmetric b_c(θ)=b_c(1−θ), minimum at θ≈0.381 (b_c≈2.16), endpoint law
  b_c∼0.7890261736/min(θ,1−θ) (half-line boundary layer) **[verified: b_c(θ) matches to 1e-6;
  b_c(1/2)=3.0764]**. Fig. A.
- **Minimal-mode theorem [proven]:** a two-mode fold is impossible even with signs; ≥3
  sign-alternating modes are required.
- **Normal-form scaling [verified]:** gap∼(b_c−b)^{1/2}, prominence∼(b_c−b)^{3/2}. Figs. B, C.

## IV. Universality **[proven genericity + verified instances]**
- **Model-independence [proven]:** for any absorbing Markov generator, a rank-m killing defect gives
  det(sI−Q_b)=det(sI−Q_0)det[I_m+BW(s)] (Woodbury); the fold S₁=S₂=0 is a property of the signed
  spectral mixture, not the ring. The double-peak region is an **open set** (structurally stable),
  not fine-tuned. Honest scope: *not* "every shortcut makes a peak," but "peak birth/death is
  generically a fold."
- **Multiple shortcuts [verified]:** explicit m=2 determinant with a new b₁b₂ interaction term
  (matches exact spectrum ~1e-5); **two shortcuts produce a THIRD peak** — exact ring (N=1500)
  shows peaks at τ=3.0e-4/5.3e-3/6.1e-2 — organized by a cusp **[conjecture: cusp expected at
  S₁=S₂=S₃=0; not yet located]**. Fig. D.
- **Beyond 1D [verified]:** on a 2D torus the same capture+diffusive double peak folds at
  β_c^{2D}≈0.55–0.65, present at L=17,25,33 (2D survival). Figs. E, F. **[open: a single-site 2D
  sink is marginal (log-divergent self-Green fn) so the large-L b_c(L) scaling needs
  renormalization — future work.]**

## V. Physical realization & non-Hermitian character
Embedding: the shortcut = a **localized Poissonian target-delivery channel** (−b|u⟩⟨u| in the
survival sector; a gate of width a × local trigger rate k → δ-sink κ∼ka). Realizations
(strongest → most caveated): (1) feedback-controlled Brownian/active-particle search with an
optical-tweezer/microfluidic delivery gate at θ (b = trigger rate; place gate near θ≈0.38);
(2) engineered/small-world transport with a one-way express edge to an absorbing node (two edges →
test the triple peak); (3) intracellular motor-capture (in vitro). **Non-Hermitian, no overclaim:**
Q_b is a passive open-Markov loss defect — **not** PT-symmetric, and **b_c is not an exceptional
point** [verified: eigenvalues stay real, simple, smooth through b_c — no coalescence]; the
√-scaling is a saddle-node of a scalar f(t;b), not EP eigenvalue splitting (same exponent,
different object). Universal experimental prediction: the fold scaling exponents (1/2, 3/2) and the
two-shortcut triple peak.

## VI. Discussion / relation to prior work (honest)
We do not claim shortcut bimodality (Godec–Metzler; small-world) or interior-trap multimodality
(Bressloff; Grebenkov) or the exact lattice-defect method (Giuggioli; Montroll–Weiss). Our net
increment is the **exactly-solvable bifurcation-theoretic classification**: the saddle-node
criterion, the predictive threshold b_c(θ), the minimal-mode theorem, universal scaling, and
universality (rank-m cusp / 2D). (Mattos–Mejía-Monasterio–Metzler–Oshanin, PRE 86, 031143 (2012) is
a splitting-probability P(ω) bimodality, not f(t) — cited correctly.)
**Open / proof-level (narrowed 2026-06-30):** the G_{ξ,θ} derivation is now done (App. B), so what
remains is: the single N→∞ assumption of uniform C¹ moment convergence near the fold (fixed-mode
residue convergence is already standard 1D operator theory — App. B); locating the cusp
(S₁=S₂=S₃=0) that organizes the two-shortcut triple peak; the 2D large-L marginal scaling of
b_c(L) (2D point-sink log-renormalization); elementary closed forms for M, c_w(d).

## Methods / reproducibility
Exact determinant + amplitudes: `code/dpma_general_u_master*.py`; saddle-node certification +
scaling: `code/dpma_saddle_node_certification.py`; b_c(θ) + uniqueness: `code/dpma_saddle_node_bc_theta.py`;
rank-m / triple peak: `code/dpma_multishortcut.py`; 2D: `code/dpma_2d_universality.py`; figures:
`code/dpma_prr_figures.py`. venv numpy+mpmath+matplotlib.

## Notes for Luca (venue)
Headline now leads with the certified saddle-node + threshold + universality (ring = exactly-
solvable example), and prior-art is honestly scoped after a real literature check (bimodality is
known; the bifurcation classification is ours). Suggest: PRR first (higher 分区; low-friction PRE
transfer with reports), expecting a likely PRE landing. Remaining before submission = prose
polish + convert to RevTeX + (optional) close a proof-level gap or two for referee-proofing.
