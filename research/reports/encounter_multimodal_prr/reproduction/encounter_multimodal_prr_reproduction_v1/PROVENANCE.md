# Provenance

The released archive is tag `v1.0.0` of
https://github.com/zhouyi-xiaoxiao/prescribed-reaction-time-modes.  The
source commit it was built from is recorded by the builder as
`release_commit` in `environment/reference_platform.json` (together with
`release_date`) and as `commit` in `CITATION.cff`; the tag is placed on the
commit that records these receipts.  Every stored record was produced by the
code shipped here: the 18 production rows and the W1--W5 and robustness
campaigns with seed `20260808` on the platform recorded in
`environment/reference_platform.json` (recorded 2026-08-14), and the
covariance-aware reclassification of all stored records on 2026-08-24
(`artifacts/data/exact_m_prr_upgrade/covariance_aware_reclassification.json`).
File hashes are listed in `MANIFEST.sha256`.

Each stochastic JSON records the seed used to construct its NumPy
`SeedSequence`; upgrade and robustness records also serialize the stream tag.
The 18 earlier production JSONs omit the tag field, but their deterministic
driver fixes it to `1` and writes it explicitly for new reruns.  Independent
robustness seeds are separate simulations.  The `dt` and `dt/2` comparisons
use the same declared seed and tag, while `dt` itself enters the entropy, so
the paths are independent rather than coupled.

The Lean 4 package under `lean/formal_lean_prr/` is shipped at the source
hashes quoted in the Supplemental Material (Table of SHA-256 anchors); the
builder recomputes those anchors and refuses to archive sources that differ.
Its axiom record `consolidated_axioms.txt` was written on 2026-08-25 after
the last source change; the audit reports `codex_lean_audit.txt` and
`codex_lean_recheck.txt` and the resolution record
`codex_lean_recheck_resolution.txt` document how the released sources were
reached.  No independent build log on the released hashes is included; the
build is reproduced with the commands in the package `README.md`.

If a persistent identifier is minted for this release, it is recorded in
`CITATION.cff` and `.zenodo.json`.
