# Round 79: fixed-finite-dimension theory repair and freeze

Date: 2026-07-14  
Predecessor: `audits/round_77_general_dimension_theory_attack.md`  
Scope: repair the five Round 77 findings in the analytical statement and its
living scope surfaces; rebuild and inspect the working article and analytical
Supplement. No numerical producer, allocation-cusp job, Stage-A/Stage-B
scientific object, or exactly-once positive-budget auditor was run.

## 1. Verdict

**SELF-REPAIR PASS / HOLD-INDEPENDENT-POSTEDIT-AUDIT.**

The direct construction is now stated pointwise for every fixed finite integer
physical dimension \(d\ge2\) and every fixed finite requested mode count. The
proof package explicitly freezes the dimension-sized geometry and data before
the sequential limits, uses the exact diagonal-Haar quotient, and replaces the
non-invariant single-chart argument by product-geodesic separation plus an
all-lattice-image Gaussian shell bound. It also states the dimensional
normalization and the absence of any uniform-in-\(d\), \(d\to\infty\), or
cross-dimensional budget/amplitude/event-mass claim.

This upgrade is analytical generality, not a numerical promotion. The only
finite numerical evidence remains physical \(d=2\) and \(d=3\), and the open
positive-budget allocation-cusp, continuation, independent-solver, and
positive-budget physical-\(d=3\) gates are unchanged.

Current self-audit counts are:

| P0 | P1 | P2 |
| ---: | ---: | ---: |
| 0 | 0 | 0 |

The claim remains held until an independent post-edit attack confirms both the
mathematics and the propagation across all living scope surfaces.

## 2. Round 77 disposition

| Finding | Repair | Disposition |
| --- | --- | --- |
| G77-1 | Added the outer quantifiers over fixed finite integers \(d\ge2\) and finite \(m\), with \(d\)- and \(m\)-dependent data and the order “freeze \(d,m\), then choose \(\epsilon\), then choose \(B\)”. | CLOSED |
| G77-2 | Removed the claim that the contact complement lies in one minimum-image chart. The proof now uses product-geodesic reverse-triangle separation and a fixed-dimensional summable bound over every lattice image. | CLOSED |
| G77-3 | Did not promote \(d=1\); the article theorem begins at \(d=2\), so no hidden zero-transverse convention is needed. | CLOSED BY SCOPE |
| G77-4 | Made \(W^{-(d-1)}\), dimension-sized transverse covariance, and dimension-dependent constants explicit; prohibited cross-dimensional comparison of dimensional \(B\), amplitudes, masses, and \(B_0\). | CLOSED |
| G77-5 | Replaced “all dimensions” with “every fixed finite integer \(d\ge2\)” and explicitly excluded uniform-in-\(d\), noninteger-dimension, \(d\to\infty\), and arbitrary localized-catalyst readings. | CLOSED |

## 3. Mathematical repair details

1. The exact symmetry reduction is expressed by the diagonal Haar identity on
   \(\mathbb T_W^{d-1}\), avoiding a nonexistent global torus midpoint chart.
2. The installed slab profile is normalized by \(W^{-(d-1)}\), so the
   centre-space amount is \(B\) separately in each fixed dimension.
3. The reversible-space semigroup argument uses the weighted \(H^1\) form
   domain and bounded perturbation. No low-dimensional Sobolev embedding is
   invoked.
4. Contact-tail derivatives are controlled through product-geodesic separation
   and polynomially growing fixed-dimensional lattice shells dominated by
   Gaussian decay.
5. Every constant may depend on the frozen dimension, geometry, covariance,
   profiles, target times, and mode count. No constant is asserted uniform in
   dimension.
6. The theorem still certifies at least \(m\) local maxima only. It does not
   rule out additional extrema or supply a dimension-uniform event-mass floor.

## 4. Frozen sources

| File | SHA-256 |
| --- | --- |
| `manuscript/encounter_multimodal_prr.tex` | `9ff234179adb4ac997347e4ad8152b869572d2391c79d67eef86b9dd1b9921c1` |
| `manuscript/encounter_multimodal_prr_supplement.tex` | `21d9bf4263d9bcb2fa6df5fac2c3607dde4de2259ad26062c8358214087ef024` |
| `notes/direct_physical_multimode_theorem.md` | `b406f49785fb36f525e9d689204642c187d40a30f4983d616305d8ad957a1afa` |
| `notes/pde_mixed_jet_theorem.md` | `6f7252fc42a7eecb1342477e95e639791fb6fb9c49e75ed91f89519ea7cd034e` |
| `README.md` | `31a3622d5ccb41107038c8a542b9d83a4469e4fc212e92914e78fa364df196d1` |
| `notes/research_contract.md` | `fd0340efd28e97142565840c0f32b362f233ae44bf39b500a508ac62f4f9be77` |
| `notes/theorem_program.md` | `ce23ecf940e5864facafea563588aecbd75555b23a16a0b4bf6178a2138e422e` |
| `notes/prr_focused_spine_rewrite_blueprint.md` | `585ea39754c133afd99c13e552c0ee5bbae2ebb0fc2a5809f15bef4d0ab02009` |
| `code/test_general_dimension_scope_consistency.py` | `ce869d09702902de52bc6baa3b168be91ffe54052800c4e02397aacdb2fb35e1` |

The README hash above is the pre-ledger hash used to freeze the scientific
wording. Adding this audit pointer changes only the directory index; the
independent post-edit audit must hash the files it actually reads.

## 5. Regression, compilation, and PDF QA

- `test_general_dimension_scope_consistency.py`,
  `test_living_scope_consistency.py`, and `test_compile_manuscript.py`:
  **17/17 PASS**.
- Ruff on the new scope test: **PASS**.
- Fail-closed article compiler: **PASS**; two clean builds are byte-identical.
- Compile manifest:
  `artifacts/data/manuscript_compile.json`, SHA-256
  `5935fa6300859eb867d4197148d4fe4fb54495e6011f135f3d0b26139289acf9`.
- Article PDF: 13 letter pages, 797,573 bytes, SHA-256
  `c77e39944cc6c1f0d79c7a4c671a02eb81ab78e50cc110a7ea529b63033f88d0`.
  All 45 font rows are embedded and subset; no Type-3 fonts, missing fonts,
  overfull boxes, unresolved references, or unresolved citations occur in the
  final TeX log. The final log retains ordinary two-column underfull-box
  notices; visual inspection found no clipping, collision, or unreadable line.
- Visual inspection covered the title/abstract, theorem statement and proof
  summary, \(d=2/d=3\) numerical boundary, gate ledger, discussion, and final
  references pages. No visible defect was found.
- A separate clean temporary Supplement build completed with 12 letter pages
  and zero final unresolved-reference/citation or overfull-box matches. The
  temporary build was not promoted as a canonical artifact.

## 6. Non-promotion boundary

Round 79 authorizes only an independent post-edit theory/scope audit. It does
not authorize an allocation-cusp run, a Stage-B scientific run, a claim that
dimensions above three have numerical support, or release/submission. The
project remains on scientific HOLD.

