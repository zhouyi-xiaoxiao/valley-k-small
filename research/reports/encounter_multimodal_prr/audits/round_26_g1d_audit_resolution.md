# Round 26: G1d audit resolution

Date: 2026-07-13  
Status: **both Round-25 P2 documentation findings resolved without altering the frozen evidence chain**

## Resolution rule

The G1d protocol, runner, manifest, and result are byte-pinned historical
evidence.  They are not edited after the formal result merely to improve
notation or formatting.  This resolution therefore adds prospective wording,
focused regression tests, and manuscript scope language while preserving every
frozen SHA-256.

## P2.1: transpose portability

For a row generator (A) and column state (q), the general forward state
and sensitivity equations are

\[
 \dot q=A^{\mathsf T}q,
 \qquad
 \dot s=A^{\mathsf T}s+A_\lambda^{\mathsf T}q.
\]

Equation (2) of the frozen protocol omits the transpose on its lower-left
block.  In G1d the control changes diagonal killing only, so
(A_\lambda=A_\lambda^{\mathsf T}) exactly and the executed block is correct.
Every future protocol must nevertheless write the general transpose explicitly.
The new focused test verifies both facts: the frozen tangent is exactly
transpose-invariant, whereas a generic nondiagonal tangent is not.

## P2.2: side-root scope

The reported `root_count` values 3 and 1 count retained strict sign-changing
roots on the frozen (\Delta t=0.02), (t\in[3,18]) screen followed by exact
bracket refinement.  They robustly establish the four reported simple roots
and their local fold-normal-form ordering.  They do not exclude an
even-multiplicity root or an unresolved sub-grid pair.  The manuscript now
describes this explicitly as a sign-changing-root screen and does not use it
as a global phase-map or trimodality certificate.

## Added regression coverage

`code/test_continuum_g1d_fold_confirmation.py` adds five focused tests for:

1. the frozen affine segment and zero-sum budget tangent;
2. exact diagonal/transpose invariance of the frozen generator tangent;
3. the required transpose for a generic forward sensitivity;
4. the action-jet derivative recursion against centered matrix differences;
5. fail-closed result flags and the local side-topology record.

These tests are downstream audit coverage and are deliberately not inserted
into the already frozen G1d manifest.

## Final severity ledger

| severity | unresolved count | disposition |
| --- | ---: | --- |
| P0 | 0 | none found |
| P1 | 0 | none found |
| P2 | 0 | both Round-25 findings resolved prospectively |
| open scientific gate | 1 | odd/even mesh, box, and independent-solver convergence still required |

The allowed claim remains exactly one result-informed fold of the
(65\times65\times49) finite-volume Doi model at (B=0.6).
