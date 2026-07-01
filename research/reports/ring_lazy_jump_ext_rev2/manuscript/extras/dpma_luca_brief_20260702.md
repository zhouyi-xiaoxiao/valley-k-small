# DPMA manuscript — handoff brief for Luca (2026-07-02)

**Bottom line.** The paper is a **complete, submission-ready PRR manuscript** (11pp, RevTeX/PRR,
5 figures, 15 references, compiles clean). It has been through **two full triangulated audits** (three
adversaries — a repo-grounded Claude multi-agent workflow, ChatGPT gpt-5-5-thinking, and ChatGPT
Extended Pro gpt-5-5-pro — over two rounds each), all findings reconciled against ground-truth
computation, and then numerically strengthened. It is committed locally on branch
`dpma-audit-20260630` and **not pushed** — awaiting your go-ahead.

Files: `manuscript/dpma_prr_manuscript.tex` → `manuscript/build_prr/dpma_prr_manuscript.pdf`; all
verification scripts in `code/`; audit records in `notes/dpma_triangulated_audit*.md`.

## The result, in one paragraph
Shortcut-induced first-passage bimodality, long known phenomenologically, is the observable signature
of an **exactly solvable saddle-node fold** of a *signed* spectral mixture. Modeling a directed shortcut
to an absorbing target as a rank-one killing defect on a lazy ring (continuum limit: Brownian motion on
[0,1] with an interior δ-sink of strength *b* at θ), the finite-time diffusive-return peak is created
and annihilated at the compact criterion **S₁=S₂=0** (Φ′=−S₁, Φ″=S₂). We give the phase boundary
b_c(θ) (min at θ≈0.381; endpoint law b_c·θ→0.789026, resolved independently to 6 digits), the generic
(½, 3⁄2) fold scaling, a minimal-three-mode theorem, Woodbury model-independence, a rank-two **cusp**
organizing a triple peak, survival on a 2D lattice (fold at β_c²ᴰ≈0.69), a direct Monte-Carlo, an exact
channel decomposition (early=capture, late=diffusive), robustness to release position, an **independent
continuum Brownian-dynamics instance** reproducing the fold with no lattice/spectral input, and a
measurability estimate (~4×10⁴ trials to resolve b_c). b_c is a time-domain morphology fold, **not** a
spectral exceptional point.

## What the audits concluded
Both audit systems moved from "reject/transfer" (round 1) to **major-revision / defensible PRR** after
the revision. Consensus: the mathematical core is **correct and independently reproducible**; every
issue was framing/honesty/notation, plus the two significance additions. Repo-grounded auditing caught
and we fixed three real numerical points a text-only reviewer missed (a wrong 2D threshold, a circular
endpoint-constant check, an over-stated channel claim). The single most defensible novelty: the
**bifurcation-theoretic classification with a predictive, computable threshold**, distinct from the
known bimodality and from Giuggioli's defect-resolvent method.

## Venue recommendation: PRR first, PRE as the built-in fallback
- **PRR (recommended target).** The paper is now framed physics-first (the observable-level saddle-node,
  not "another solved ring"), and the additions both auditors said PRR hinges on are in: the
  independent Brownian instance (model-independence *demonstrated*, not just asserted), channel
  resolution, off-antipodal robustness, and a quantitative measurability claim. Extended Pro's final
  read: "a defensible PRR major-revision resubmission, possibly approaching acceptance after one more
  round." PRR also carries the higher domestic ranking and **auto-transfers to PRE** on rejection at no
  extra cost — so a PRR attempt is low-risk.
- **PRE / J. Phys. A (safe fallback).** The manuscript is already submittable to either as-is; the exact
  defect-resolvent solution carries it comfortably. This is the conservative choice if you'd rather bank
  the result.

My recommendation: **submit to PRR; let the automatic PRE fallback handle the downside risk.**

## What I need from you (the human-only items)
1. **Author order + affiliation** — confirm (currently "Xiaoxiao Zhouyi, Luca Giuggioli", UoB SMET).
2. **Funding line** — the acknowledgments has a placeholder (`% CONFIRM`); add the grant(s).
3. **Venue** — PRR-first (my rec) vs PRE/JPA.
4. **arXiv / public repo** — the branch is still local; say when to push and whether to arXiv on submission.
5. **A read of the physics framing**, especially Sec I (positioning vs your PRX 2020) and Sec V
   (realizations) — these are where your judgement matters most.

## Optional, non-blocking (I can do if you want a maximally strong PRR run)
A normal-form-prefactor script (restores displayed precision with a committed source) and a 2D
gap+prominence co-collapse test (makes "same fold morphology as 1D" fully rigorous). Neither changes any
auditor's verdict; the paper stands without them.
