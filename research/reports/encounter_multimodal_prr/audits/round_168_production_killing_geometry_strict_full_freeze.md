# Round 168: strict-full production killing-geometry freeze

Date: 2026-07-15

Status: **GO AS SEPARATE-SOURCE VERIFIER INPUT ONLY / SAME-CORE PRODUCER / NO
INDEPENDENT ACCEPTANCE / NO CONCRETE KILLING / NO FULL OPERATOR / F0 HOLD**

## 1. Exact freeze

| Object | SHA-256 |
| --- | --- |
| producer source | `2cada45143914edf1142daf6a5b7a8b5367757c664855dd6d836e7f43935dd9b` |
| producer tests | `887a19536e2f81d4c99dda198cb4f7d488c9ccfff52673c843cec47bf8a2852c` |
| authority | `5543f76031d731cb5bcf3e4cdf3bdabaffacb2053400e3015d6ab57906a27669` |
| canonical `bundle.json` | `f29c29360f3d7db58694aeaeddc7cae8e1eaaac25d8ce6d5792a9ebacf455684` |
| 76-file path-sorted tree | `b05dd83f3756528c0fd09f78f3a79eb4b1894e2bb423e45e1af55f6cce928568` |
| factorization contract | `de42fefbfc163fdcffd573d49d1156d761341c78b3756903755579dc8e9b23af` |
| family relation | `3f2bf086ffac6d30b65ab0c0be866432756d3581979b8a3372bf8c7891bbf1c8` |
| partition-reference graph | `ce259a13975f43b7eeec4f468b0fe1ed92d1d4b9b60ac9b93ebb0f4418c3267e` |

The whole-tree digest is SHA-256 over `shasum -a 256` lines emitted in
lexicographic **relative-path order** with bundle-relative `./...` paths.  It
is not a sort of the complete hash-first lines.

## 2. Trigger and repair

The first independent-source implementation exposed a contract mismatch:
2,559 of 4,142 cells proved geometrically full were serialized as
`[1-ulp,1]` or `[1-2 ulp,1]`, while the frozen independent contract requires
the exact singleton `[1,1]`.

The design was not weakened.  The producer now independently applies exact
rational corner classification after the accepted numerical contact builder:

- the squared norm is convex on each axis-aligned rectangle, so all four
  exact corners inside or on the closed disk prove the whole rectangle full;
- a periodic split cell is full only if every segment-pair rectangle is full;
- exact segment lengths must sum to the declared cell volume before any
  singleton replacement; and
- replacement is permitted only when the original outward numerical interval
  already contains one.

The accepted general F0 core was not modified.  The repaired producer and its
disk verifier both apply the same strict-full postcondition, and the manifest
records
`contact_full_cell_serialization=exact_[1,1]_after_exact_rational_corner_classification`.

## 3. Exact workload and canonical classes

The regenerated bundle contains:

```text
contact records                    233,139
exact zero contact cells           227,693
exact unit contact cells             4,142
partial contact cells                1,304
active contact cells                 5,446
support records                       6,852
raw interval records                239,991
raw interval bytes                3,839,856
files                                    76
non-root directories                     14
```

All 257 current products involving a periodic split transverse cell remain
exact `[0,0]`.  Synthetic tests cover far-corner equality, a split cell with
one nonfull component, and segment-volume mismatch.

## 4. Reproducibility and adversarial result

- The producer test source collected and passed 13/13 tests, exit zero.
- Two complete builds in distinct previously absent directories were
  byte-identical.
- Both fresh trees and the installed canonical tree passed disk verification.
- The installed tree was rehashed after replacement and matched the freeze.
- Strict tree closure, special/symlink/hard-link rejection, exact relations,
  source pins, range/quality ledgers, deterministic rebuild, and immutable
  nonpromotion flags remained active.

The independent exact-hash adversarial assessment was:

```text
P0 = 0
P1 = 0
P2 = 2
verdict = GO FOR SEPARATE-SOURCE VERIFIER INPUT ONLY
```

The two nonblocking P2 coverage gaps are:

1. no dedicated depth-four mutation for the maximum-relative-depth branch;
2. no fully coherent quality-ledger-only mutation that also rewrites every
   affected row, inventory, relation, and family digest.

Code inspection confirmed the corresponding fail-closed depth and recomputed
ledger-equality branches.  These tests remain required before a broader
release claim, but neither changes the narrow producer-input verdict.

## 5. Nonpromotion boundary

This freeze is same-core producer evidence.  It does not establish an
independent backend, an independently accepted contact/support oracle, a
weighted physical killing field, a single physical operator, propagation,
topology, a resource gate, F0, F1, continuum convergence, or PRR release.

```text
strict-full factor bundle       = FROZEN / SAME-CORE ONLY
separate-source verifier        = IMPLEMENTATION IN PROGRESS / UNACCEPTED
two-child clean replay          = NOT BUILT / NOT RUN
literal-zero packed baseline    = NOT AUTHORIZED YET
synthetic factor operators      = NOT AUTHORIZED YET
full physical operator          = ABSENT
F0                              = HOLD
F1                              = NOT AUTHORIZED
continuum C1-C3                 = OPEN
PRR release                     = HOLD
```
