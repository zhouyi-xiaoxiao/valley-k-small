# Reproducibility environment baseline

Date: 2026-07-14

The report's numerical tests currently run in the repository-owned `.venv`
with CPython 3.12.13 and the exact direct versions recorded in
`code/requirements-reproducibility.txt`.  In particular, `gmpy2==2.2.1` is a
required direct dependency for directed MPFR bounds; it was missing from the
root dependency declarations when this baseline was added.

Verify an existing environment, without running any scientific calculation,
from the repository root:

```bash
.venv/bin/python \
  research/reports/encounter_multimodal_prr/code/check_reproducibility_environment.py
```

For an independent environment, create a CPython 3.12 virtual environment and
install the report-local direct baseline before running the same check:

```bash
python3.12 -m venv .venv-encounter-prr
.venv-encounter-prr/bin/python -m pip install \
  -r research/reports/encounter_multimodal_prr/code/requirements-reproducibility.txt
.venv-encounter-prr/bin/python \
  research/reports/encounter_multimodal_prr/code/check_reproducibility_environment.py
```

No from-zero installation was executed while creating this note, because the
current task intentionally avoided network access.  The exact-version file is
therefore a direct-dependency baseline, not yet a transitive wheel/hash lock.
External reproducibility remains open until a clean offline or separately
provisioned environment installs it, runs the focused suites, and records the
platform, compiler, BLAS/LAPACK, and package-artifact identities.

This environment check does not evaluate a positive budget, run F1/F2/F3, or
promote any continuum or PRR claim.
