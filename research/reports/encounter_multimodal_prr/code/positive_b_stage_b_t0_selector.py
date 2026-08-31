"""Fail-closed tombstone for the retired unqualified T0 module name.

The only executable Stage-B-v5 T0 implementation is
``positive_b_stage_b_t1_selector_v5.py``.  Importing this historical name is
an error by design: a compatibility re-export would restore the
``PYTHONPATH``/``sys.modules`` substitution surface closed in Round 81.
"""

raise ImportError(
    "positive_b_stage_b_t0_selector is retired; import the byte-attested "
    "positive_b_stage_b_t1_selector_v5 implementation directly"
)
