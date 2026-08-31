# Round 122: exact-(m) spine living-scope closure

Date: 2026-07-14  
Decision: **PASS-LIVING-SCOPE / HOLD-POSITIVE-B / HOLD-PRR**

## Purpose

Rounds 118 and 120 independently accepted the repaired exact-(m) analytical
spine, but the living route documents still described it as a pending repair.
This closure updates only claim status and publication routing.  It creates no
positive-budget result and does not authorize F1.

## Accepted analytical statement

For every fixed finite $d\ge2$ and prescribed fixed finite $m$, the
declared $d$- and $m$-dependent narrow-slab Doi family has exactly $m$
nondegenerate maxima and $m-1$ nondegenerate minima on its declared compact
positive-time window after first fixing sufficiently small $\varepsilon>0$
and then taking $0<B<B_0(\varepsilon)$.  The statement is not uniform in
$d$, $m$, or $\varepsilon$, gives no useful numerical $B_0$, supplies
no event-mass floor, and does not describe topology outside the declared
window.

The accepted theorem bytes are

```text
notes/exact_m_mode_encounter_theorem_v2.md
e78a0d77959d50214d56ef4708a20ac465232883fbbdd4ee42fe488c0b95c85d
```

with independent closure

```text
audits/round_120_exact_m_theorem_v2_p2_closure.md
dfc0381ddbc87a7c338978f80f5a9c9219536409b06905a03f5cdcd2fafbb10e
```

## Living records

```text
README.md
52ee7bce2e7069f336e4889485436c4f836273c6db9de2a5b5800b2349500be8

notes/research_contract.md
2f3259f3e7a3ebf89c3d1a2c86781e46913aa4d1b03ee5fb3a75106627204efe

notes/theorem_program.md
081123a6cba44803e1d3e1e85c27a97cb37eeb5dfbe74151a70724ad5ce6ea49

notes/prr_focused_spine_rewrite_blueprint.md
192629645c9b137250699cb166c8a647844ef20fa3a5dddbef91331972bb97ca

notes/literature_gap_20260713.md
1993b24f460adf063188f896ecc39c91cd52ec49b737459a2ab7d73202ad7ecf

code/test_living_scope_consistency.py
94468a588fd33a7e811a2eedccf3ee83b0d33d67252e474757d7a5c0b7083069
```

The documents now agree that allocation-v6 is terminal, exact-(m) is the
accepted analytical spine, the active finite-parameter target is physical
(d=2), and the remaining conjuncts are the science-free F0 acceptance, all
36 frozen F1 rows, and independent F3 event-law validation.  A numerical cusp
and positive-budget physical (d=3) are not gates for the focused paper.

## Regression

```text
pytest code/test_living_scope_consistency.py = 2 passed
ruff check code/test_living_scope_consistency.py = PASS
stale exact-m HOLD / cusp-required / d3-required phrase scan = clean
positive budget evaluated = false
```

The historical manuscript remains explicitly non-submittable and is not
silently promoted by this closure.
