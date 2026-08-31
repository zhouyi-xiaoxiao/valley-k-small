# Reproduction package: finite-window reaction-time modes

This archive accompanies **“Prescribing finite-window reaction-time modes
with a static fixed-budget Doi reactivity field”** by Xiaoxiao Zhouyi.  It
contains the exact scripts, stored Monte Carlo sufficient statistics,
robustness checks, and publication figures used for the numerical claims.

No DOI is assigned in this local package.  If the archive is deposited, cite
the version and DOI shown by the repository record rather than inventing one.

## Contents

- `code/`: deterministic off-lattice simulator, W1–W5 drivers, campaign
  summary, and robustness driver.
- `artifacts/data/exact_m_offlattice_production/`: high-statistics anchor
  simulations.
- `artifacts/data/exact_m_prr_upgrade/`: W1 phase-diagram cells, W2 empirical
  operational-threshold probes, W3 jitter tests, W4 five-mode example, W5
  three-dimensional spot check, and the added classifier/seed/time-step
  robustness results.
- `artifacts/figures/`: PDF and PNG versions of the six numerical figures.
- `manuscript/`: final compiled article and Supplemental Material when the
  release package is frozen.
- `environment/`: the Python package versions and platform provenance of the
  reference run.
- `.zenodo.json` and `CITATION.cff`: deposit and citation metadata with no
  fabricated DOI.
- `RESULTS_SUMMARY.md`: a compact, explicitly qualified guide to the added
  classifier, seed, and time-step robustness records.
- `MANIFEST.sha256`: SHA-256 checksums, generated only after the release tree
  is frozen.

## Environment

The reference computations used CPython 3.12.13 on arm64 macOS.  Create an
isolated environment from the archive root:

```bash
python3.12 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r environment/requirements.txt
```

Only NumPy is needed for simulation.  Matplotlib is needed to regenerate the
figures, and mpmath is needed for the independent Dyson-bound calculations.

## Fast reproduction from stored counts

These commands do not rerun Monte Carlo walkers:

```bash
python code/exact_m_prr_robustness.py --phase sensitivity
python code/exact_m_prr_upgrade_w1.py --phase figure
python code/exact_m_prr_upgrade_w2.py --figure-only
python code/exact_m_prr_upgrade_w3.py --figure-only
python code/exact_m_prr_upgrade_w4.py --replot
python code/exact_m_prr_upgrade_w5.py --replot
```

The first command reclassifies the stored 0.02-wide histogram counts over the
declared bandwidth and relative-prominence grids.  The remaining commands
recreate all six numerical figures in `artifacts/figures/`.

The independent high-precision analytic checks can be rerun with:

```bash
python code/b0_dyson_numerics.py
python code/b0_dyson_chaincheck.py
```

## Full stochastic reproduction

First audit that the archive contains the exact 18-row production matrix
underlying Supplemental Table S-I:

```bash
python code/exact_m_offlattice_production.py --phase audit
```

A quick executable test traverses the same complete matrix at reduced walker
count in a separate, explicitly non-production directory:

```bash
python code/exact_m_offlattice_production.py --phase smoke --workers 3
```

The 18 production rows (17 at `dt=0.001`, plus the reported `dt=0.0005`
twin) can be rerun without overwriting the archived records with:

```bash
python code/exact_m_offlattice_production.py --phase full --workers 3 \
  --output-subdir exact_m_offlattice_production_rerun
```

This uses five million walkers per row, chunk size 250,000, seed 20260808,
`tmax=4`, and classifier bandwidth 0.04.  The subsequent W1--W5 upgrade and
robustness campaigns can be rerun with:

```bash
python code/exact_m_prr_upgrade_preflight.py
python code/exact_m_prr_upgrade_w1.py --phase all --workers 5
python code/exact_m_prr_upgrade_w2.py --workers 5
python code/exact_m_prr_upgrade_w3.py --workers 5 --replicas 50
python code/exact_m_prr_upgrade_w4.py --walkers 5000000
python code/exact_m_prr_upgrade_w5.py --walkers 5000000
python code/exact_m_prr_robustness.py --phase seeds --workers 3 \
  --seed-walkers 1000000
python code/exact_m_prr_robustness.py --phase dt --workers 3 \
  --dt-walkers 500000
python code/exact_m_prr_upgrade_campaign_summary.py
```

The high-statistics campaign is computationally substantial.  Each JSON
records its own walker count, seed, step size, model parameters, measured
runtime, histogram counts, classifier output, and validation gates.  Upgrade
and robustness records also serialize their stream tags.  The 18 older
production records serialize the seed but not the tag; the deterministic
production driver fixes their tag to `1`, audits their complete parameter
matrix, and writes the tag explicitly in new reruns.  The robustness driver
is resumable: it reuses completed per-run JSON files unless `--force` is
given.

## Legacy schema names

The directory/file names `w2_b0_empirical`, `B0_empirical.json`, and
`exact_m_b0_empirical_prr`, together with serialized W2 keys such as `b0`,
`b0_bracket`, and `b0_lower_bound`, are frozen legacy schema identifiers.
They mean the protocol-defined operational transition
`B_op(eps)` under the stated finite-walker histogram classifier only.  They
must not be read as the theorem threshold `B_top` or the sufficient bound
`B_cert`.  Filenames such as `..._B0.125...` instead encode the ordinary
budget value `B=0.125` and do not use a `B0` symbol.

## What is and is not retained

Individual walker trajectories and unbinned reaction times are not retained.
They are generated in memory and reduced to declared histogram counts to keep
the archive compact.  The stored counts and bin edges are sufficient to
reproduce the reported classifier, sensitivity analysis, peak locations, and
figures, but not analyses that require trajectories, unbinned event times, or
a different base histogram bin width.  See `DATA_AVAILABILITY.md` for the data
dictionary and this limitation in full.

## Integrity and licensing

After the release tree is frozen, verify it from the archive root with:

```bash
shasum -a 256 -c MANIFEST.sha256
```

Source code is licensed under the MIT License (`LICENSE-CODE`).  Stored data,
figures, documentation, and compiled manuscript files are licensed under
Creative Commons Attribution 4.0 International (`LICENSE-DATA`).
