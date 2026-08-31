# Round 09 Reviewer A recheck: novelty-repair closure

**Recheck date:** 2026-07-11

**Overall novelty gate:** **PASS with the previously declared B2 evidence limitations**

**B0/B1 blockers remaining:** **none**

**Recommended journal route for the frozen evidence package:** **PRE**

## 1. Recheck scope

This is a repair recheck, not a new literature search. Per instruction, I read only:

- `manuscript/encounter_modality_jcp.tex`;
- `manuscript/references.bib` (the manuscript's bibliography file);
- `notes/journal_target_20260711.md`; and
- my original `audits/round_09_novelty_journal/reviewer_a.md`.

I did not read a Reviewer B report and did not inspect or modify the scientific code,
data, figures, or manuscript source. The original review's source judgments are the
baseline for deciding whether its three mandatory novelty repairs have been closed.
In the table below, A1/A2/A3 map respectively to the original review's
B1-1/B1-2/B1-3.

| Repair gate | Frozen-candidate status | Decision |
|---|---|---|
| A1: disclose and distinguish the closest Giuggioli multi-peak/mode precedents | Closed | **PASS** |
| A2: remove established Green/Woodbury machinery from the grammatical novelty claim | Closed | **PASS** |
| A3: cite and distinguish Grebenkov's reactivity-induced mono-to-bimodal result | Closed | **PASS** |

## 2. A1 — Giuggioli/Luca prior-art positioning

**Decision: PASS; closed.**

The bibliography now contains all of the mandatory direct precedents from the
original review:

- Sarvaharman--Giuggioli 2020, DOI
  [10.1103/PhysRevE.102.062124](https://doi.org/10.1103/PhysRevE.102.062124)
  (`references.bib:233-242`);
- Das--Giuggioli 2022, DOI
  [10.1088/1751-8121/ac9765](https://doi.org/10.1088/1751-8121/ac9765)
  (`:244-253`);
- Marris--Giuggioli 2024, DOI
  [10.1088/1367-2630/ad5d85](https://doi.org/10.1088/1367-2630/ad5d85)
  (`:255-264`);
- Barbini--Giuggioli 2024, DOI
  [10.1088/1751-8121/ad7ca2](https://doi.org/10.1088/1751-8121/ad7ca2)
  (`:266-275`); and
- Marris *et al.* 2025,
  [arXiv:2508.10140](https://arxiv.org/abs/2508.10140)
  (`:277-286`), explicitly labeled as a preprint.

The introduction no longer describes the Giuggioli line only as propagator or
multi-target machinery. It now states explicitly that this program already contains
bias-generated bimodality, persistence-generated multimodality, route-generated
multiple peaks, and resetting/disorder-related mode reshaping
(`encounter_modality_jcp.tex:104-119`). It also calls the present paper a **direct
extension** of that program and disclaims a new Green or multi-target formalism.

The critical distinction is stated twice at high visibility:

- the introduction identifies the unresolved comparison as a time-independent
  spatial redistribution of finite-radius Doi reactivity at fixed transport and
  integrated killing (`:171-178`); and
- the prior-work subsection repeats the Giuggioli precedents and makes the matched
  physical experiment, not multiple peaks, the new object (`:1508-1537`).

This satisfies every required element of A1, including the explicit treatment of the
2024 multi-target chapter as a multiple-route/peak precedent and the preprint status of
the 2025 sparse-network work.

## 3. A2 — novelty grammar around Green/Woodbury machinery

**Decision: PASS; closed.**

The decisive repair is at `encounter_modality_jcp.tex:1525-1537`:

- established propagator, Green, and channel ideas are called a **computational
  layer**;
- the claimed increment is the matched experiment in which the transport generator
  and integrated killing budget remain fixed while only the static spatial Doi field
  is redistributed;
- the density transition is defined through (f_t=f_{tt}=0), nondegeneracy, and
  physical-path transversality; and
- the text expressly disclaims a first observation of multiple peaks, a new Woodbury
  identity, and a continuum modality theorem.

The abstract independently states that Green reductions, GIG hitting-time laws,
multimodal first passage, heterogeneous targets, and capacity scaling are not claimed
as new (`:82-84`). Thus, listing the reaction-support Green reduction among the
technical results (`:197-200`) no longer creates a plausible novelty claim: it is a
reported computational component whose prior status is explicit before and after the
results list.

No A2 blocker remains.

## 4. A3 — Grebenkov 2020 reactivity-induced bimodality

**Decision: PASS; closed.**

Grebenkov's 2020 paper is now present in the bibliography with the correct DOI,
[10.1103/PhysRevLett.125.078102](https://doi.org/10.1103/PhysRevLett.125.078102)
(`references.bib:288-297`). The manuscript makes the required mechanism distinction
in all three high-visibility locations:

- the abstract acknowledges encounter-history-dependent reactivity as an existing
  route to reaction-time multimodality (`encounter_modality_jcp.tex:49-53`);
- the introduction states that accumulated-local-time activation can transform a
  reaction-time density from monomodal to bimodal, then contrasts it with a static
  spatial volume-killing field at fixed transport and budget (`:140-147`); and
- the novelty subsection repeats both the precedent and the static-spatial matched
  distinction (`:1519-1537`).

This wording no longer permits the broad, incorrect interpretation that the paper is
the first to control reaction-time modality through reactivity. A3 is fully closed.

## 5. High-visibility overclaim audit

| Location | Assessment | Reason |
|---|---|---|
| Title | **PASS** | Claims a topic, not priority or a continuum theorem. |
| Abstract `:49-53` | **PASS** | Leads with the three established routes and immediately states the narrower static-spatial matched question. |
| Abstract `:65-84` | **PASS** | Reports finite-grid folds and trimodality, exposes the 0.242 nonconvergence, calls GIG screening, and disclaims continuum and broad prior-art claims. |
| Introduction `:101-178` | **PASS** | Explicitly separates encounter, heterogeneous reaction, gating, transport-generated peaks, and the remaining matched-Doi question. |
| GIG section `:639-684` | **PASS** | Adds the foundational first-hitting-time citation and calls the confined-channel use a screening approximation. |
| Main result list `:195-226` | **PASS** | Green/Woodbury is a technical result, while all finite-grid, capacity-validation, and trimodality boundaries are retained. |
| Prior-work subsection `:1508-1537` | **PASS** | This is now the strongest and most precise novelty statement in the paper. |
| Limitations `:1542-1578` | **PASS** | Withholds continuum convergence, Robin equivalence, general-(d) realization, a cusp, and a global root-count theorem. |
| Conclusions `:1597-1624` | **PASS, minor B3 wording opportunity** | The details remain finite-grid and the final paragraph withholds a continuum fold. The opening sentence could optionally say “in the declared finite models” for maximal editorial caution, but the current paragraph is not a blocker. |

Two optional B3 refinements would make the already acceptable wording even harder to
misread:

1. In abstract line 84, replace the pronoun-heavy phrase “their fixed-transport
   connection” with the exact object: “the derivative-certified density fold under
   the stated static-spatial, fixed-budget Doi redistribution.”
2. In conclusion line 1597, insert “in the declared finite models” after “provides”
   if the authors want every standalone sentence to carry the evidence level.

Neither is required for PASS because the surrounding abstract and conclusion already
state the finite-grid and noncontinuum boundaries explicitly.

## 6. Bibliography and journal-note checks

The frozen TeX has no citation key missing from `references.bib`. In addition to the
three mandatory repairs, the bibliography now includes the foundational GIG
first-hitting-time paper and direct gated-reaction precedents. These additions further
reduce the risk that an editor reads the fold, GIG family, or reaction-time
multimodality as a broad priority claim.

`notes/journal_target_20260711.md` is consistent with the repaired novelty boundary:

- PRE remains the recommended target for the present finite-grid mechanism package;
- JCP remains conditional on stronger continuum/chemical-physics evidence;
- PRResearch remains a stretch rather than a metric-driven choice; and
- no unverifiable current numerical domestic partition is asserted. The note instead
  records exact ISSNs, the historical-edition lookup rule, and the stated 2026
  discontinuation of the official CAS table.

## 7. Remaining evidence limitations and final verdict

The original B2 scientific limitations remain real: the 2D critical control is not
grid-converged, no independent Robin calculation is present, bounded trimodality is a
finite-grid certificate, and the multidimensional GIG construction is screening rather
than a bounded finite-radius theorem. These constrain the journal ceiling but do not
reopen the novelty wording gate because the frozen manuscript states them accurately.

**Final verdict: PASS.** A1, A2, and A3 are closed. I find **no remaining B0 or B1
novelty/prior-art blocker** in the frozen candidate. The manuscript may proceed on the
PRE route subject to the separate numerical, reproducibility, and final-production
audits; this recheck certifies only the requested novelty/prior-art repair.
