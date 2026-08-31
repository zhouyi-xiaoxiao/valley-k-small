# Round 85 allocation-cusp v6 repair freeze

Date: 2026-07-14  
Decision: **HOLD-INDEPENDENT-PRERUN**  
Scientific launch status: **not authorized; mesh 65 and mesh 97 were not built or run**

## 1. Scope and final severity ledger

This implementer round repairs the two independent Round-84 findings without
changing the frozen scientific design. It closes the false fixed-hash claim,
freezes the bounded non-system native closure actually used by the authorized
bootstrap and imported stack, adds adversarial regressions, and refreshes the
no-cycle provenance chain.

Final open findings:

| severity | count |
|---|---:|
| P0 | 0 |
| P1 | 0 |
| P2 | 0 |

The release decision remains HOLD because this is an implementer repair, not
the fresh independent pre-run review required before any mesh-65/97 launch.

## 2. Hash-randomization and ordering repair

- Formal parents and children retain `-I -S -B`.
- `PYTHONHASHSEED=0` was removed from the formal environment, manifest, and
  protocol. Under `-I`, `ignore_environment=1` and `hash_randomization=1` are
  required explicitly.
- Three isolated adversarial processes demonstrated differing string hashes
  while producing identical canonical bytes from set-derived input.
- Gate maps, candidate/representative ordering, tie breaks, and serialization
  cross explicit sorting boundaries. Canonical JSON remains `sort_keys=True`.
- The two full formal replicas remain an exact canonical-byte equality gate;
  no full replica was executed in this pre-run repair because doing so would
  construct the prohibited scientific meshes.

## 3. Bounded native provenance repair

The producer and independent auditor separately rebuild the same bounded
non-system Mach-O witness. Each row freezes the install name, all observed
lexical aliases, resolved path, size, SHA-256, `LC_RPATH`s, recursively resolved
load commands, and exact loaded phases. `@loader_path`, `@executable_path`, and
`@rpath` are resolved explicitly. `/System/Library`, `/usr/lib`, and the signed
Cryptex system library prefix terminate at the separately attested dyld-cache
leaf. Actual Homebrew dependencies including OpenSSL `libcrypto`, xz `liblzma`,
and mpdecimal are included.

The final exact phase sequence is:

| phase | non-system mapped images |
|---|---:|
| `bootstrap_pre_third_party` | 13 |
| `runner_post_import` | 93 |
| `post_manifest_validation` | 94 |
| `full_stack_post_import` | 98 |

The initially attempted three-phase cells-7 smoke failed closed before algebra:
the post-validation process had one extra image, `pyexpat`. Exact differencing
showed no missing image and exactly that one extra path. Staged probes identified
the cause as `signed_dyld_cache_provenance -> platform.mac_ver()`. The repair
therefore preserves the pure 93-image runner phase and adds a distinct exact
94-image post-validation phase; it does not weaken any comparison to a subset.
The full-stack phase is measured in the same real order and contains 98 images.

Final closure:

- image count: `98`
- closure SHA-256:
  `5f857bf207eb181ca758e501f394584cb8c2833c5764712133d53f9018295cb0`
- producer rebuild equals independent-auditor rebuild exactly.

The Python/hash/bootstrap primitive is stated as a bootstrap trust root. The
frozen closure is a reproducibility and drift witness under the
no-concurrent-writer/no-OneDrive-replacement contract, not a claim to prevent a
malicious same-UID process.

## 4. Frozen artifacts

| artifact | SHA-256 |
|---|---|
| v6 manifest | `2e1223f6206c6ebc4adc5c11ed67672afdc55f68e90f725cf8b6930bb67b9948` |
| discovery runner | `b32260ad18abd3f159b7cac1dcd600be2507ff2a89cf60712c5c6f66ccbd70da` |
| independent auditor | `38b7822efce5ddd3b0220549a94a259f393c44150f66a61140f9b58029bf23f0` |
| discovery protocol v6 | `3c56b307bed70c52152c31764aa84020b7c45770ea656e00fe1d54d47b51ab2b` |
| no-cycle post-result protocol v6 | `393b648c9ba36acc47b9c9acfbc86a82946df495fb36928f6ded91e826ca03b7` |
| Round-85 regressions | `60665c7edaa3cd5a85213415529c43ccd38c69a6390186075bff3c109bc341a9` |
| ordinary discovery tests | `1b68eb77b087b18bb5136950482e7cbb5d12194cc3d6fd57f9cc8dfaf77ea722` |
| Round-50 regressions | `073976ff5aa213cccd6b5d5f5442a1aa90229b28c0d9a124d4a3476a6f51b27d` |
| retained Round-80 regressions | `25c7b4ba6e81bfc407c159194314f6295b0443d770ed61f11b4123c343b8c0ae` |
| independent auditor tests | `f2f38f04892d652cef9b88849cfb059defe7d3b3468ad4de86c66f333a2bd8fa` |
| Stage-A tests | `c2370dfc69e1e775b486a8a9653f1877d2a28a5003999507ce65017bfcecc065` |
| immutable Round-84 attack | `49d8163e749f909d25d48ad5634f60e285308ab3507c237ef6e9569e05ff6862` |

The manifest contains 27 unique report-relative pins: the prior 25 plus the
immutable Round-84 report and the Round-85 regression file. The independent
auditor and no-cycle protocol remain outside that manifest and point forward to
the manifest hash, so no file hashes itself directly or indirectly.

## 5. Verification evidence

All commands ran from `research/reports/encounter_multimodal_prr` with the
repository `.venv` and `PYTHONDONTWRITEBYTECODE=1`.

1. `ruff format --check`: 11 files already formatted; exit 0.
2. `ruff check`: all checks passed; exit 0.
3. `py_compile`: exit 0.
4. `git diff --check`: exit 0.
5. Combined pytest invocation: 106 tests collected and all 106 passed in one
   run (the retained 97 plus nine Round-85 regressions); exit 0.
6. Final isolated `-I -S -B` cells-7 smoke against manifest
   `2e1223f...b9948`: `PASS_ALGEBRA_DRY_RUN_HOLD_SCIENCE`, explicit-CSR maximum
   action error `2.220446049250313e-16`, and
   `scientific_meshes_executed=[]`; exit 0.
7. The manifest is canonical JSON; all 27 pinned hashes rehash exactly.
8. All five scientific/evidence/replica/audit destinations and both promotion
   staging paths remained lexically absent after every check.

The first combined regression attempt exposed four stale test assumptions
(two mocked formal paths omitted the new native gate, one expected 25 pins, and
one stripped the bootstrap's final newline). Those tests were updated to model
the v6 boundary, then the manifest and forward hashes were rebuilt before the
single final 106-test green run.

## 6. Freeze decision

**HOLD-INDEPENDENT-PRERUN.** The v6 implementer package is internally green and
the Round-84 findings are repaired, but no mesh-65/97 execution is authorized by
this report. A fresh independent pre-run adversarial review must verify these
frozen hashes and return a separate authorization decision.
