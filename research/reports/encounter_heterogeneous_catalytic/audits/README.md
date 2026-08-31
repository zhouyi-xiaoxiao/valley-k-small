# Adversarial audit ledger

These are publication audits, not implementation summaries.  A round counts
only when at least two independent reviewer roles inspect the frozen evidence,
write actionable findings with severity and file/claim anchors, and the root
agent records a remediation decision plus revalidation evidence.

Severity levels:

- `B0`: submission blocker; the affected claim or artifact cannot ship;
- `B1`: major revision; materially changes derivation, evidence, or framing;
- `B2`: bounded correction or required caveat;
- `B3`: optional polish.

A round may close with an unresolved finding only when the corresponding claim
is explicitly removed or retained as a visible limitation.  “No obvious
problem” is not a passing audit.  Reviewer reports must state what they tried
to falsify, which files/data they inspected, and which checks were actually
executed.

The thirteen required rounds are:

1. model definitions, units, coordinate and row/column conventions;
2. Green/Woodbury/resolvent, zero mode, numerator/residue, and sensitivities;
3. GIG derivation, normalization, geometry mapping, and approximation scope;
4. fold/cusp/multimode catastrophe algebra and transversality;
5. root isolation, continuation, conditioning, tails, and convergence;
6. finite-radius 2D/3D physics, capacity, boundaries, and controls;
7. Lean statement fidelity, assumptions, axioms, and coverage boundary;
8. data, figures, notebook, manifests, one-command workflow, and PDF QA;
9. prior art, novelty language, Luca/Giuggioli relationship, and journal fit;
10. independent JCP/PRE-style referee simulation and final claim audit.
11. mathematical generality, counterexamples, literature priority, and
    continuum-regularity boundary;
12. fixed-budget design-gradient and reversible spectral production
    validation;
13. hostile journal-ceiling, claim/evidence, presentation, and release
    reassessment after the generality upgrade.

Each directory contains `reviewer_a.md`, `reviewer_b.md`, and
`resolution.md`.  The machine-readable status and revalidation commands are
aggregated in `audit_ledger.json` after the final round.
