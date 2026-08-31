"""Fail-closed rejected draft of the Round182 runtime-origin probe.

Round182 independent audits rejected v1 as evidence of runtime truth.  This
module is therefore an inert sentinel: it does not parse a specification,
inspect the filesystem, resolve a path, import gmpy2, or launch a process.
There is no PASS path.  A repaired design, if any, must use a new version.
"""

from __future__ import annotations

import sys
import typing

HOLD = "HOLD_CONTINUUM_C1_N0_RUNTIME_ORIGIN_PROBE_V1_REJECTED_DRAFT"
REJECTION = (
    "Round182 independent audits rejected v1 as runtime truth; "
    "the draft is inert and has no executable validation path."
)
HOLD_LINE = f"{HOLD}: {REJECTION}\n"
STATUS = "REJECTED_DRAFT_ROUND182_NO_RUNTIME_TRUTH"
HOST_RUNTIME_BYTE_COMPLETE = False
EXECUTABLE_VALIDATION_PATH_PRESENT = False


class ProbeFailure(RuntimeError):
    """The one fail-closed outcome exposed by the rejected v1 draft."""

    def __init__(self) -> None:
        super().__init__(HOLD_LINE[:-1])


def validate_runtime_origin_probe(spec_path: object = None) -> typing.NoReturn:
    """Reject immediately without observing or evaluating *spec_path*."""

    del spec_path
    raise ProbeFailure


def main(argv: typing.Sequence[str] | None = None) -> int:
    """Return the same rejection for every invocation, including help."""

    del argv
    sys.stderr.write(HOLD_LINE)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
