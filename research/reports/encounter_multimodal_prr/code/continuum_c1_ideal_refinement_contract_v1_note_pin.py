"""Single update point for the living C1 theorem-note byte pin.

The theorem note may receive a fresh mathematical-audit patch.  When that
happens, update only ``THEOREM_NOTE_SHA256`` here, rebuild the versioned
candidate, and then update the candidate hash in the standalone verifier.
"""

from pathlib import Path

THEOREM_NOTE_RELATIVE = Path(
    "notes/continuum_c1_free_form_and_functional_bridge_candidate.md"
)
THEOREM_NOTE_SHA256 = (
    "17b987d5090618e5346f81217afed7e57daccf878d4b93b8402724b3e002a562"
)
