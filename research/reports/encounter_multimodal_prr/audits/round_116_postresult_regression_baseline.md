# Round 116: post-result regression baseline

Date: 2026-07-14  
Role: repository-wide science-free regression and static-check audit  
Decision: **PASS APPLICABLE POST-RESULT TESTS / PRESERVE PRE-RUN FAIL-CLOSED GUARDS / NO SCIENCE PASS**

## 1. Boundary

This audit did not run a primary positive-budget control, a production FV
campaign, an off-lattice trajectory, or a manuscript promotion command.  It
checked the current repository after the terminal allocation-v6 result and
its audit artifacts already existed.  Test success below is software evidence
only.

## 2. Applicable post-result tests

The ordinary test batch excluded only:

- the three tests that require the repository's authenticated `python -I -S`
  selector bootstrap; and
- the six historical `test_positive_b_allocation_cusp_discovery*.py` pre-run
  files whose explicit contract requires all discovery result/evidence/audit
  paths to be absent.

Collection contained exactly 421 tests.  The batch exited zero:

```bash
ignores=()
for f in code/test_positive_b_allocation_cusp_discovery*.py; do
  ignores+=(--ignore="$f")
done
../../../.venv/bin/python -m pytest -q -ra -p no:cacheprovider code \
  "${ignores[@]}" \
  --ignore=code/test_positive_b_stage_b_t1_selector_v5.py \
  --ignore=code/test_stageb_t0_selector_round78.py \
  --ignore=code/test_stageb_t0_selector_round94.py
```

The authenticated selector command

```bash
../../../.venv/bin/python -I -S \
  code/run_stageb_t0_selector_tests_isolated.py
```

ran 54 tests and reported `OK`.

## 3. Shared-process import guard

A deliberately naive all-code pytest process preloaded
`continuum_g1_smoke` before the allocation discovery module.  The latter
correctly rejected the preloaded module as a substitution risk.  The two
affected method checks were rerun in fresh processes and both passed:

```text
test_small_explicit_csr_and_mixed_observable_jets          PASS
test_small_grid_physical_law_and_factor_diagnostics       PASS
```

This is evidence that the shared-process errors were test-order isolation,
not failures of the small explicit CSR or physical-law implementation.

## 4. Why the historical pre-run tests remain red

The current repository legitimately contains the append-only terminal
allocation discovery result, reproducibility record, and independent audit.
Several historical pre-run tests assert that these paths do not exist.  They
therefore fail closed on the present post-result tree, exactly as their frozen
launch boundary intended.  Deleting or moving the scientific artifacts to
make those tests green would destroy the evidence state and is forbidden.

The applicable post-result result-auditor tests are included in the 421-test
passing batch.  No historical pre-run assertion was weakened, skipped inside
its own file, or rewritten.

## 5. Static check

Ruff passed on all code except one immutable historical formatting exception:

```text
code/test_stageb_v3_design_round67.py
SHA-256 fc17fbbd5e648a6b8629fb07d6030931c3dcaa820466851f6a88e84b28317342
```

That exact SHA is pinned by
`audits/round_67_stageb_v3_independent_attack.md`; changing import order would
break the historical audit chain for no runtime or scientific benefit.  Ruff
therefore ran with that one path explicitly excluded, and all remaining files
passed.  The frozen file's own four tests were run directly and reported
`OK`.

## 6. Ledger

```text
applicable post-result ordinary tests     = 421 PASS
authenticated isolated-selector tests     = 54 PASS
fresh-process import-guard checks          = 2 PASS
all active code excluding one frozen lint  = RUFF PASS
frozen Round-67 file runtime tests          = 4 PASS
primary positive-B science executed         = NO
off-lattice science executed                = NO
scientific or PRR gate promoted              = NO
```

The repository baseline is suitable for continued F0 implementation.  It is
not evidence that the new theorem, F1 fixed controls, F2 plan, F3 event law,
or manuscript release has passed.
