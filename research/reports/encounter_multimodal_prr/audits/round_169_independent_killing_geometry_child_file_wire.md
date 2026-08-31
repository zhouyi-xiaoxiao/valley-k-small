# Round 169: independent killing-geometry child file wire

Date: 2026-07-15

Status: **PASS CHILD MATHEMATICAL CORE AND CHILD FILE WIRE ONLY / HOLD OUTER CLEAN REPLAY / HOLD CONCRETE KILLING / HOLD OPERATOR / HOLD F0 / HOLD F1 / HOLD RELEASE**

## Exact reviewed inputs

- independent verifier source SHA-256:
  `70942ed70eabd1cca48499d004550670bd12acfe714e4d6ca43308a210f1fb4d`;
- independent verifier test SHA-256:
  `8a37f622d21e826894061980c7c8ecbb247afae6ac7c1151d063f8532c228123`;
- living design SHA-256:
  `f6c810ca77251b6f1c1683a8c85d2eb015bacb0fedcd0fe7ffb3174341e106f2`;
- operation-model-v2 SHA-256:
  `53f709139c380e9512740a6fdabcd7570c1822650817915454ddbd7d7395feb0`;
- frozen producer source SHA-256:
  `2cada45143914edf1142daf6a5b7a8b5367757c664855dd6d836e7f43935dd9b`;
- frozen candidate bundle SHA-256:
  `f29c29360f3d7db58694aeaeddc7cae8e1eaaac25d8ce6d5792a9ebacf455684`.

The operation model now defines thirteen ordered input-snapshot components,
including the design bytes that the child actually reads.  It also records
the honest runtime boundary: the venv launcher is verified and executed, its
resolved regular target is byte-bound, but the complete standard-library,
dynamic-library and kernel filesystem closure is not claimed.

## Source corrections closed in this round

1. The root-local 384/512 Simpson implementation records every sampled
   dyadic coordinate, rather than reporting only root-breakpoint bit lengths.
   The production maximum is now honestly reported as 76 bits.
2. The accepted production leaf partition is frozen at
   `5899c7ba287a274717d2460479f92a9a9f00cb2d6af273d79f5f1be257b4275b`.
   A separate one-root synthetic traversal is frozen at
   `fca7cdcb2928512afc39b4e74d46f4d6e8737fc6a1312cced1c1648799fbcf8a`.
3. The semantic deadline is checked before, between and after each root's
   384/512 fourth-derivative bounds.
4. The design no longer overstates ordinary Fraction/MPQ cap checks as a
   universal pre-allocation theorem.  Only the MPFR-to-MPQ conversion has the
   explicit exponent/precision preconversion guard.
5. The child implements the exact six-argument file wire, exclusive
   `O_EXCL|O_NOFOLLOW` publication, stable reread, bound success/HOLD
   acknowledgement and two-key unbound-HOLD fallback.

## Reproduced checks

The final-hash test file passed all 38 tests in one process:

```text
38 passed
18.64 s wall
302,530,560 bytes maximum resident set size reported by time(1)
407,814,912 bytes peak memory footprint reported by time(1)
```

The same final source was then invoked twice as two ordinary isolated Python
processes through the new child file wire.  These were not private staged
outer runs and therefore are not clean-replay acceptance evidence.

| observation | direct run 0 | direct run 1 |
| --- | ---: | ---: |
| child exit | 0 | 0 |
| child status | child-only PASS | child-only PASS |
| semantic bytes | 14,732 | 14,732 |
| semantic SHA-256 | `e28d5bf63abfcf1f44ace9c701a806f680e43a7964de036bd204963110d95eb2` | same |
| semantic raw bytes | byte-identical by `cmp` | byte-identical by `cmp` |
| observation SHA-256 | `d890dd9097eb4a9cc93198a243f35a9bca1a94f4a5a4d5a937150ee125fee0ca` | `4ed88e67bc858033265120a817a3e31a090afd06bb34fa3296f43d5d8d44a202` |
| child-observed peak RSS | 329,859,072 bytes | 367,951,872 bytes |
| external wall time | 17.82 s | 16.78 s |

The observations are intentionally different because nonce, run index, PID,
elapsed time and RSS do not belong in the deterministic semantic body.

The deterministic receipt retains the accepted numerical facts:

- 234,278 primary tree nodes and 117,213 accepted leaves;
- 234,574 paired sample evaluations with complete 512-in-384 sample nesting;
- 148/148 root-M4, 117,213/117,213 leaf-panel and 148/148 table containments;
- normalizer containment and 6,852/6,852 support-cell containments;
- maximum exact-component size 1,176 bits and maximum coordinate-component
  size 76 bits;
- no independent 512-bit `2^-68` adaptive claim.

## Acceptance boundary

This round accepts the mathematical child core and its bounded file wire for
continued implementation.  It does **not** issue the sole downstream outer
status.  The following remain required:

1. exact outer-runner source and mutation tests;
2. four-phase raw input-snapshot equality for both runs;
3. direct-child reap, process-group absence, independent stdout/stderr EOF,
   parent-FD/selector closure and private-stage removal;
4. two serialized private-stage runs with distinct child PIDs and identical
   complete semantic bytes;
5. an exclusively published, stably reread outer receipt.

No concrete killing array, single physical operator, full operator, installed
budget, propagation, topology, F0, F1, continuum result or PRR release is
authorized by this round.
