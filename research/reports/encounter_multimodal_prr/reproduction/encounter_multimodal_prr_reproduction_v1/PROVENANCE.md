# Provenance

The numerical campaign was run from repository commit
`3531353a515160b09899199a9257e7455a654b22`, with the archive-specific
classifier parameterization, W2 count retention, robustness driver, and
figure-label cleanup included in the files distributed here.

Each stochastic JSON records the seed used to construct its NumPy
`SeedSequence`; upgrade and robustness records also serialize the stream tag.
The 18 earlier production JSONs omit the tag field, but their deterministic
driver fixes it to `1` and writes it explicitly for new reruns.  Independent
robustness seeds are separate simulations.  The `dt` and `dt/2` comparisons
use the same declared seed and tag, while `dt` itself enters the entropy, so
the paths are independent rather than coupled.

No DOI has been assigned in this local tree.  Repository deposit metadata and
the final checksum manifest must be generated from the frozen release rather
than inferred from this provenance note.
