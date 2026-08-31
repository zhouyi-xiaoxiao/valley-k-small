# Round 156: theorem-first status and exact-hash closure

Date: 2026-07-14  
Mode: independent, adversarial, read-only except for this audit record  
Excluded: the 7,165,305-state production run, positive-budget science, and any
new selector stress campaign

## Verdict

**ACCEPT THE CURRENT EXACT-BYTE FILESYSTEM SNAPSHOT AS AN INTERNAL
THEOREM-FIRST WORKING SET / HOLD F0 / NO F1 / NO F2 / NO F3 / HOLD STRICT
CONTINUUM / HOLD PRR.**

New findings in this round are `P0=0`, `P1=0`, `P2=1`.  The one new P2 is
repository provenance: the complete report directory is still untracked and
`research/reports/report_registry.yaml` is modified, so this exact-byte verdict
has no commit identity and is not a version-controlled release.  The two
already-declared selector P2 items remain inherited boundaries rather than new
Round-156 defects: a second-POSIX replay and a causal second-parent contention
handshake.

This acceptance is hash-specific.  It does not authorize submission, a
finite-parameter modality claim, or a continuum theorem.

## Exact-byte anchors

### Theorem-first package

| File | Independently recomputed SHA-256 |
| --- | --- |
| `manuscript/encounter_multimodal_prr_theorem_first_working.tex` | `6e7393e44bb1da9bb196b839534fdf43e18dd90d0829d941ad7e155f4afcbc67` |
| `manuscript/encounter_multimodal_prr_supplement.tex` | `566b752f2d5c2c8fabdf0a421f16599317a697dd46f7d41b6b16475495cb2e65` |
| `manuscript/exact_m_theorem_full_proof.tex` | `a372b5a33d2203b8f3214a153f4aaf1e81497bf146c0ac1db1cfda97919c1c7b` |
| `manuscript/exact_m_theorem_spine.tex` | `79b0a4467a67999f605b8a5d8ec07e41a88c07edc8cdf1639ad6b8d4ce70658e` |
| `manuscript/references.bib` | `2f90b6735993c6d2fa8bb8f1a6c35c334706d02585361d4ee9238ac020ce9c76` |
| `code/compile_theorem_first_working.py` | `15098db6e731e23a31967077b79ace723849b5e8383169bb497fa57f9b92725e` |
| `code/test_compile_theorem_first_working.py` | `c48ecffdd4222ef7987151e20037c950c324eec867a814d1b806751ebb43aa7c` |
| `artifacts/data/theorem_first_working_compile.json` | `797d536e16016a0ba80d44d7be265197a12be47ecfdb4e20da67e46248008646` |
| `output/pdf/encounter_multimodal_prr_theorem_first_working.pdf` | `c766de16ca3a70eda63397d4d78ccb9f44415982afa4d4b6e0a295197488984b` |
| `output/pdf/encounter_multimodal_prr_theorem_first_supplement_working.pdf` | `3bf770bd28d577aaac54057601e315745d240d29246fa3831a1d39fc82f7dbea` |

### Independent audit and freeze chain

| File | Independently recomputed SHA-256 |
| --- | --- |
| `audits/round_149_exact_m_supplement_migration_independent_attack.md` | `f689002b01b1fff3549ed446c9b05efe3fbe3cfc4aa1a3b64c859bbb18dfea78` |
| `code/test_round149_exact_m_hash_freeze.py` | `3a7695c7fb1bcad8962263002e774317f26a196d296ed98be4a2af499f8de95c` |
| `audits/round_153_selector_round151_independent_attack.md` | `216749d4deb0b46ed25f7fff4358c9354e9a9e2425d2ba708395d070ceece462` |
| `code/test_round153_selector_hash_freeze.py` | `f166d615de8a7cfd0d5fd6fd0f16b10bcad84c7925df97bff82899f486bb42d8` |
| `audits/round_155_f0_packed_directed_action_independent_reaudit.md` | `f5757c5da6ca152f99c184cd921ab3babdb1fe63d3192d133fc8a737cc06ccc1` |
| `code/test_round155_f0_hash_freeze.py` | `89dc5c996eee81484b04f1f9fbac99dd6e4ed314e6bbb13f3078902ec99e41eb` |

### Living status surface

| File | Independently recomputed SHA-256 |
| --- | --- |
| `README.md` | `7b83d6582af6a072ecea83154150204d34e87e61f7ac0a2a294a47660671de54` |
| `notes/research_contract.md` | `81a811eda5566536d1208ef5c360e87dfba0ac4f47ab0ede43e436e6ba79450c` |
| `notes/theorem_program.md` | `0c382f8018174cbf46f1ae4bab53fa08af0cf9b8da2c817b8f634ccbcbe67b92` |
| `notes/continuum_next_stage_path.md` | `3d75dcd00b564d048dcf503591257502379268204bb418dd92f0dd72e8abe3d4` |
| `notes/f0_rate_interval_composition_next_stage.md` | `53382b59185d17fa5249a8074f5172b608cd5565cae9959fef0da948ee0256a1` |
| `manuscript/SUBMISSION_METADATA_REQUIRED.md` | `4b03714d296f07488b4579ed2dfd737fee86f7638f218fd1b77381674927658a` |
| `code/test_living_scope_consistency.py` | `6e35eade5edbd7745c6fc32f088d8c5e20be75978cc8d2d130e20741210b09d0` |
| `code/test_general_dimension_scope_consistency.py` | `1a0c672b7b64ddf9f6395e9df08a9328123e5e7a3a8281ce72066aa9555d2ef5` |
| `code/test_text_control_character_hygiene.py` | `ba5237f8b5fdbb64b023ce27432eae349eadefc21528272a7e9f694566fa3da8` |
| `../report_registry.yaml` | `3682349b0b166414b975d0272035bda1d485a5df568cb1ef67528b594a40a52f` |

## Status-boundary attack

The current sources, PDFs, manifest, README, research contract, theorem
program, continuum path, F0 next-stage design, and submission checklist agree
on the following boundary:

1. **Accepted analytical result:** for each fixed finite `d` and `m`, an
   `m`-dependent support design yields the prescribed exact complete topology
   on one compact positive-time window after the ordered small-noise then
   small-positive-budget limits.  The result is pointwise in `d,m`, has
   asymptotically saturated contact on the design window, and supplies no
   useful common budget threshold, event-mass floor, topology outside the
   window, or same-support allocation switching result.  This is precisely the
   Round-149 support-design acceptance.
2. **Selector only:** Rounds 151/153 accept the exact selector/test bytes on the
   tested macOS process/resource surface.  The two portability/causal-handshake
   P2 items remain open.  No F0/F1/F2/F3 science follows from the selector.
3. **F0 primitive only:** Round 152 rejected the first directed-action bytes;
   Round 154 repaired them; Round 155 accepts the repaired exact bytes only as
   a bounded implementation primitive.  The public consistency digest is not
   authentication or a fresh verifier.  The next-stage note is explicitly
   design-only and now binds fresh-process authority, recurrence-radius
   provenance, the point lift, signed-zero policy, subordinate contracts,
   simultaneous memory phases, and the correct farthest-point box radius.
4. **Still open:** rate-interval composition, production
   uniformization/Poisson tails/jets/topology, independent replay, the actual
   7,165,305-state resource gate, all 36 F1 rows, F2/F3 off-lattice evidence,
   the strict discretization-to-continuum theorem, and author-confirmed release
   metadata.
5. **Release state:** `release_eligible=false`; F0, F1, F2, F3, strict
   continuum certification, and PRR submission all remain on HOLD.

No living document upgrades a historical `B=0` shape, the isolated
`B=0.01` finite-grid point, the failed allocation-v6 cusp campaign, or a
finite-grid refinement into the active theorem or a continuum claim.

## Build, PDF, and registry checks

- The targeted collection contained 124 tests across theorem compilation,
  theorem scope, Round-149/153/155 hash freezes, archived-manuscript routing,
  living/general-dimensional scope, text hygiene, exact-`m` stress, and the
  bounded packed F0 primitive.  Final result: **124/124 PASS**.
- Ruff lint and formatting checks passed on the 14 in-scope Python files.
- Registry resolution passed **6/6**, and `reportctl.py validate-registry`
  returned `OK: report registry is valid`.
- The active compiler manifest independently matches every listed source,
  log, and PDF hash; it records two byte-identical isolated builds of both
  documents, zero undefined citations/references, zero overfull boxes, and
  `release_eligible=false` without reading or evaluating positive-budget
  scientific values.
- Independent PDF inspection confirmed 5 main pages plus 20 supplemental
  pages, all `612 x 792` points with zero rotation; no encryption, JavaScript,
  embedded files, Type-3 fonts, unembedded fonts, NUL/replacement text, or
  Ghostscript parse failure.  All 25 rendered pages were inspected: no
  clipping, overlap, missing glyph, unreadable table, or broken page number was
  found.

## Historical routing

The active registry order names the theorem-first main, then the supplement,
then the historical main, and names the theorem-first compiler before the
legacy compiler.  `README.md` calls the legacy source a historical working
draft.  `artifacts/data/manuscript_compile.json` is marked
`ARCHIVED_HISTORICAL_WORKING_SET`, points to
`artifacts/data/theorem_first_working_compile.json` as its successor, and keeps
`release_eligible=false`.  The archived legacy source and manifest therefore
cannot silently replace the active theorem-first working set.

## Finding ledger

### P0

None.

### P1

None.

### P2-156-1: no version-control identity

`git status --short` reports:

```text
 M research/reports/report_registry.yaml
?? research/reports/encounter_multimodal_prr/
```

This does not invalidate the hash-specific internal snapshot, but it prevents
commit-level provenance, review, or release.  Before any external handoff, add
the intended report files and registry change through the repository's normal
review workflow, then rerun the exact-hash and registry closure on the staged
or committed bytes.

## Final exact-byte decision

The theorem-first analytical working set and its status surface are internally
consistent on the hashes above.  Any change to an anchored file voids this
Round-156 decision until the corresponding compilation, hash-freeze, scope,
PDF, and registry checks are rerun.  The decision is deliberately narrower
than scientific or submission acceptance: **support-design theorem accepted;
selector accepted only on the tested macOS surface with two inherited P2s; F0
bounded primitive accepted; F0/F1/F2/F3/strict continuum/PRR remain HOLD.**
