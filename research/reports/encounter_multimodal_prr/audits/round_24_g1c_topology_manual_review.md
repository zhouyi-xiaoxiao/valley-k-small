# Round 24: G1c post-result topology manual review

Date: 2026-07-13  
Evidence timing: **post-result diagnostic; not prospective discovery evidence**

## Verdict

**RESOLVED FOR ONE-SEGMENT CONFIRMATION; NOT RESOLVED AS A GLOBAL PHASE MAP.**

The independently audited G1c artifact contains 53 triangular-lattice edges
flagged for manual review because the order-preserving extremum matcher left
one or more extrema of \(f_t\) unmatched.  The flags do not all have the same
meaning.  Re-reading the stored, root-filtered endpoint topology gives:

| endpoint topology | edge count | interpretation |
| --- | ---: | --- |
| one root at both endpoints | 45 | extremum-assignment ambiguity or a subzero derivative wiggle; no endpoint mode-count change |
| one root versus three roots | 8 | an endpoint-resolved max--min pair is created or destroyed |

Exactly three of the 66 controls have three retained roots of \(f_t\), with
maximum--minimum--maximum topology:

\[
 (0.1,0,0.9),\qquad(0.2,0,0.8),\qquad(0.3,0,0.7).
\]

All other sampled controls have one retained density maximum.  Thus the
coarse simplex identifies a boundary-attached two-mode region.  Its fold sheet
enters the strict simplex interior: the separately matched sign analysis gives
three eligible interior seed estimates,

\[
\begin{aligned}
 &(0.2,0.0680921304,0.7319078696),\\
 &(0.2640122507,0.0359877493,0.7),\\
 &(0.3,0.0177920886,0.6822079114).
\end{aligned}
\]

The remaining five root-count-changing review edges touch the boundary and do
not invalidate these three strict-interior crossings.  The 45 equal-root-count
flags cannot be used to claim that no additional unsampled folds exist; they
therefore remain a limitation of the coarse global phase map.

## Deterministic segment-selection rule

Before any high-resolution fold confirmation, choose among the three already
eligible G1c seeds by the following lexicographic rule:

1. maximize the minimum interpolated catalyst weight (largest distance from
   the simplex boundary);
2. if tied, minimize the endpoint extremum-time separation;
3. if still tied, use the lexicographically smallest ordered endpoint pair.

This selects the segment

\[
 (0.2,0,0.8)\longleftrightarrow(0.2,0.1,0.7),
\]

with seed \((0.2,0.0680921304,0.7319078696)\).  Its minimum estimated weight
is \(0.0680921\), compared with \(0.0359877\) and \(0.0177921\) for the other
two seeds.  This rule selects one confirmation segment only; it does not rank
or erase the other candidate folds.

## Scope of the resolution

The manual-review prerequisite in the G1c outcome policy is satisfied for the
narrow action "freeze at most one new confirmation segment."  The following
claims remain forbidden:

- that the interpolated seed is already a fold;
- that the fold is continuum stable;
- that the 45 equal-root-count review edges contain no unsampled transition;
- that the boundary-attached two-mode region is the complete phase diagram;
- that the project or PRR scientific gate has passed.

The next permissible calculation is a new frozen G1d protocol on the selected
segment.  It must solve \(f_t=f_{tt}=0\) at finer time/control resolution and
report the complete fold jet
\(\{f_t,f_{tt},f_{ttt},f_{t\lambda},f_{tt\lambda}\}\), positivity, mass
balance, root topology on both sides, and an explicit no-continuum-claim flag.

## Severity ledger

| severity | count | disposition |
| --- | ---: | --- |
| P0 | 0 | no review flag was promoted directly to a fold |
| P1 | 0 | one-segment selection is deterministic and boundary-aware |
| P2 | 0 | all counts and coordinates reproduce the frozen G1c artifact |
| open scope limitation | 1 | the complete phase map remains unresolved |
