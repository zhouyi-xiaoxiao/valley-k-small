# Physical embedding & non-Hermitian framing (PRR roadmap #3)

Derived by ChatGPT gpt-5-5-pro (chat 70843063); the one checkable technical claim (b_c is a
fold, not an exceptional point) is numerically verified here. This is the PRR "why it matters" /
significance section content.

## Core embedding rule
p′(t)=Q_0 p(t) − b|u⟩⟨u|p(t); f(t)=−d/dt(1·p)=f_0(t)+b·p_u(t). The "shortcut" is a **localized
Poissonian target-delivery channel**: while the searcher is at u it is irreversibly delivered to
the absorbing target v at rate b — in the survival sector this is a **local killing/absorption
term −b|u⟩⟨u|**, not a transport edge. A finite gate of width a with local trigger rate k →
a δ-sink of strength κ∼ka; the paper's dimensionless b is κ normalized by the diffusive hop scale.
**Sharp framing (not "shortcuts make search faster"):** a single localized delivery channel
creates an *additional arrival-time scale* — a second peak in the full FPT density — with a
predictable threshold b_c(θ).

## Realizations (ranked by cleanliness; honest caveats)
1. **STRONGEST — controlled Brownian / active-particle search with a target-teleport gate.**
   Target = absorbing wall / detector / reaction zone at x=L. Shortcut = a narrow "gate" at x=θL
   where a feedback controller (holographic tweezers, microfluidic pulse, active-particle feedback)
   occasionally delivers the particle to the target and ends the trial. b = local delivery hazard
   rate (tunable via trigger prob/frame, trap duty cycle, Poisson trigger inside the gate).
   Observable = many trials from a fixed start, record first-arrival time; for fixed θ scan b →
   the max–min pair appears for 0<b<b_c(θ) and annihilates at b_c. Put the gate near θ≈0.38/0.62
   (smallest b_c). **Caveat:** standard stochastic resetting (reset-to-initial) is NOT this problem
   (it reinjects into the survival domain); need reset-to-target-and-terminate, or a delivery pulse
   with negligible transit (finite narrow transit → δ-sink survives after convolution, b_c shifts).
   Ties to real optical-tweezer resetting/FPT experiments [verify cites before manuscript].
2. **Engineered / small-world transport with a one-way express edge to an absorbing node.**
   Target = sink/detector/exit node. Shortcut = one-way edge u→v; since v absorbs, it appears in
   the non-target subgenerator only as extra loss −b|u⟩⟨u|. b = express-edge rate/conductance/
   routing prob/valve rate. Observable = inject tracers/packets/photons/droplets, record first
   arrival, vary b. **Two express edges → cleanest test of the rank-2 prediction (third FPT peak +
   cusp in (b₁,b₂)).** Platforms: microfluidic maze w/ one-way valve; programmable packet-routing
   graph; electrical random-walk analog w/ tunable shunt-to-ground at u; photonic net w/ tunable
   lossy link. **Caveat:** a *generic* small-world shortcut is insufficient (bidirectional / non-
   absorbing target / queueing breaks the rank-one killing structure); real infrastructure =
   motivation, not verification.
3. **Intracellular active transport (motor-driven capture).** Target = nuclear pore / MTOC /
   synapse / receptor cluster / reaction site. Shortcut = capture zone u where cargo binds a motor
   and is delivered directionally (fast-delivery limit = killing at u). b = motor-capture/activation
   rate (motor density, ATP, optogenetic recruitment, affinity). Cleanest **in vitro** (patterned
   diffusion + localized motor strip + track to a fluorescent target). **Caveat:** live-cell is a
   stretch (finite run times, reversible binding, crowding, multiple targets); in-cell data tests
   *robustness*, not the literal b_c(θ).
**Would NOT lead with:** animal/robot search (memoryful/adaptive — robot demo OK, animals fragile);
epidemic first-arrival through a hub (biggest stretch — branching/depletion/interventions; analogy only).

## Non-Hermitian framing — precise, no overclaim
- **Open classical Markov / passive non-Hermitian loss defect.** Q_b is the survival generator of a
  killed Markov process; probability leaks into the absorbing target. Analogous to an effective
  non-Hermitian Hamiltonian with a localized absorber / imaginary potential.
- **NOT PT-symmetric** — no balanced gain/loss; passive loss only.
- **b_c is NOT an exceptional point.** An EP needs spectral degeneracy + eigenvector coalescence
  (defective / Jordan block). b_c is a **time-domain morphology fold** (S₁=S₂=0: a max and min of
  f(t) collide); the eigenvalues μ_j(b) and residues G_j(b) stay smooth & simple through b_c. The
  fold arises from cancellation among ≥3 SIGNED modal contributions, not eigenvalue coalescence.
  **Verified numerically** (`code/`, antipodal N=200): across b=2.9→3.3 through b_c=3.076 the
  transient eigenvalues are all real, simple (min consecutive gap ~1.7e-4, bounded away from 0),
  and vary smoothly — no coalescence. So it's a fold, not an EP.
- **The √-scaling is NOT EP square-root splitting.** At an EP, *eigenvalues* split as √(param);
  here the *FPT-extrema times* split as (b_c−b)^{1/2} because a scalar f(t;b) has a saddle-node.
  Same exponent, different object. In the reversible 1D limit the δ-sink operator is self-adjoint
  (Sturm–Liouville) → no spectral EP at all.

## PRR significance sentence
"A single one-way shortcut to a target can create a new, universal arrival-time peak with a
predictable threshold, showing that first-passage statistics contain controllable time-domain
structure invisible to mean first-passage times or spectral gaps."

## Universal experimental prediction
Best single test = the **fold scaling** (fixed θ, b↑b_c): |τ_+−τ_-|∝(b_c−b)^{1/2},
prominence Δf∝(b_c−b)^{3/2} — constants system-dependent, **exponents + cubic fold collapse
universal**. More dramatic: the rank-2 **triple peak + cusp** from two independently tunable gates.
