/-
Axiom-hygiene report for the DPMA formal audit package.

`lake env lean AxiomsReport.lean` prints, for every audited theorem, the axioms it
depends on. The audit passes iff every line shows a subset of
  [propext, Classical.choice, Quot.sound]
(Lean's standard classical axioms). Any `sorryAx` here means an unproved theorem;
any other axiom means the package smuggled in an assumption. Both are audit failures.
-/
import FormalLean

-- Module 1: Trig
#print axioms DPMA.sin_product_identity
#print axioms DPMA.chebyshev_product
#print axioms DPMA.chebyshev_recurrence
#print axioms DPMA.green_jump
#print axioms DPMA.green_column_solves
#print axioms DPMA.montroll_determinant
#print axioms DPMA.numerator_collapse
#print axioms DPMA.antipodal_factorization

-- Module 2: JumpCondition
#print axioms DPMA.branch_deriv_left
#print axioms DPMA.branch_deriv_right
#print axioms DPMA.jump_value
#print axioms DPMA.jump_iff_secular
#print axioms DPMA.phi_continuous_at_theta
#print axioms DPMA.phi_dirichlet
#print axioms DPMA.antipodal_collapse

-- Module 3: Normalization
#print axioms DPMA.J_identity_abstract
#print axioms DPMA.J_identity
#print axioms DPMA.antipodal_sin_sq
#print axioms DPMA.antipodal_J
#print axioms DPMA.antipodal_G

-- Module 4: MinimalModes
#print axioms DPMA.Phi_hasDerivAt
#print axioms DPMA.S1_hasDerivAt
#print axioms DPMA.no_two_mode_fold
#print axioms DPMA.no_two_mode_fold_exp
#print axioms DPMA.three_mode_ratio
#print axioms DPMA.three_mode_alternating

-- Module 5: NormalForm
#print axioms DPMA.Phinf_hasDerivAt
#print axioms DPMA.nf_roots
#print axioms DPMA.nf_gap
#print axioms DPMA.nf_prominence_exact
#print axioms DPMA.nf_prominence
#print axioms DPMA.prominence_constant

-- Module 6: PiSc
#print axioms DPMA.sherman_morrison_solve
#print axioms DPMA.pisc_solves
#print axioms DPMA.pisc_value
#print axioms DPMA.pisc_antipodal

-- Module 7: HalfLine
#print axioms DPMA.r0_11_closed
#print axioms DPMA.sm_scalar
#print axioms DPMA.flux_at_zero
#print axioms DPMA.fhat_assembly
#print axioms DPMA.fhat_levy
#print axioms DPMA.cut_g_transform
#print axioms DPMA.cut_normSq
#print axioms DPMA.cut_denominator_form
#print axioms DPMA.cut_denominator_pos
#print axioms DPMA.cut_im
