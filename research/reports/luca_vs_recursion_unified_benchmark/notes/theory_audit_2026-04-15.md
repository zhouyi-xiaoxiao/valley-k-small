# Theory Audit for `luca_vs_recursion_unified_benchmark`

Date: 2026-04-15

Scope:
- Audit the active unified benchmark against the Giuggioli/Sarvaharman propagator-renewal literature.
- Check the chain `paper source -> formula description -> repo solver -> benchmark wording`.
- Record where the implementation already matches the intended mathematics and where only the report wording needed correction.

Primary literature anchors:
- PRE 102, 062124 (2020): confined biased lattice propagators, single-target FPT / PGF backbone.
- Phys. Rev. Research 5, 043281 (2023): bounded heterogeneous environments and sparse heterogeneity formalism.
- J. Stat. Mech. 013201 (2023) / arXiv:2211.12388: heterogeneous media propagators and explicit FPT expressions.
- arXiv:2311.00464: review-level synthesis of bounded and heterogeneous lattice search formalisms.

Audit checklist:

1. `RING-1T-paper`
- Mathematical object: single-target renewal from a closed-form ring propagator plus a rank-one shortcut-column correction.
- Repo anchor: `packages/vkcore/src/vkcore/ring/jumpover_pipeline.py`
- Solver pair: `ring_analytic_aw` vs `ring_time_absorption`
- Audit result: implementation is consistent with the intended transform-domain route; report wording needed stronger provenance and explicit mention of the rank-one defect correction.

2. `ENC-FIXED`
- Mathematical object: fixed-site renewal on the pair torus.
- Repo anchor: `packages/vkcore/src/vkcore/ring/encounter.py`
- Solver pair: `encounter_fixedsite_gf_aw` vs `pair_fixedsite_time_recursion`
- Audit result: implementation is consistent, but the benchmark configuration is a `beta=0` control. Report wording previously risked overselling it as a shortcut-defect example; corrected to a pair-propagator control.

3. `ENC-ANY`
- Mathematical object: diagonal-target renewal on the pair torus with a shortcut-induced defect line.
- Repo anchor: `packages/vkcore/src/vkcore/ring/encounter.py`
- Solver pair: `encounter_anywhere_gf_aw` vs `pair_time_recursion`
- Audit result: implementation matches the intended pair-kernel plus finite-dimensional defect correction picture. Report wording was retained but made more explicit about the defect-line role.

4. `TT-C1`
- Mathematical object: two-target renewal from selected propagators recovered on a reduced heterogeneity support.
- Repo anchor: `packages/vkcore/src/vkcore/comparison/unified.py`
- Solver pair: `two_target_defect_reduced_aw` vs `two_target_sparse_exact`
- Audit result: implementation is not a full dense global inverse over all transient states. Report wording previously used a too-generic resolvent formula; corrected to selected-propagator recovery language.

5. `TT-LF1`
- Mathematical object: same two-target selected-propagator renewal as C1, but in an ultra-sparse support regime.
- Repo anchor: `packages/vkcore/src/vkcore/comparison/unified.py`
- Solver pair: `two_target_defect_reduced_aw` vs `two_target_sparse_exact`
- Audit result: implementation is consistent. Report wording now clarifies that LF1 is a sparse-support positive anchor for the same theory family, not a different method.

6. `REF-S0`
- Mathematical object: low-defect reflecting-lattice single-target renewal where full AW remains feasible.
- Repo anchor: `packages/vkcore/src/vkcore/comparison/unified.py`
- Solver pair: `reflecting_full_aw` vs `reflecting_exact_recursion`
- Audit result: implementation is consistent. Report wording now states clearly that this is a low-defect feasibility marker and should not be generalized to generic 2D heterogeneous cases.

Overall conclusion:
- No solver correction was required for the active unified benchmark.
- The main work item was provenance tightening and wording correction in the generated CN/EN manuscripts, tables, and README.
