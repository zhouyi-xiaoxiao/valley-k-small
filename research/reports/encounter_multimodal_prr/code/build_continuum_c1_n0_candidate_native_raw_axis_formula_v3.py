"""Fail-closed role-8 v3 producer entrypoint.

The Round-179 operation model assigns this exact basename to the future
plan-v2/request-v4 role-8 producer.  The numerical implementation and its
request-v4 authentication path are not complete in these bytes.  This
entrypoint therefore accepts only the frozen public CLI shape, performs
side-effect-free lexical checks, and terminates with one exact HOLD.  It never
opens the request and never creates, replaces, truncates, or removes the
requested artifact path.
"""

import argparse
import os
import sys

ROLE_ID = 8
ROLE_NAME = "role8_raw_axis_formula_primitive"
REQUEST_SCHEMA = "encounter_continuum_c1_n0_raw_axis_formula_request_v4"
OUTPUT_SCHEMA = "encounter_c1_n0_raw_axis_formula_primitive_source_v2"
PLAN_SCHEMA = "encounter_continuum_c1_n0_roles_8_10_replay_plan_v2"
RUNTIME_CLOSURE_SCHEMA = "encounter_continuum_c1_n0_roles_8_10_implementation_runtime_closure_v1"
METHOD_PARAMETER_IDS = (
    "raw_flux_directed_mpfr_320_v2",
    "raw_flux_directed_mpfr_640_sentinel_v2",
    "raw_flux_binary64_decode_v2",
    "exact_fraction_expression_dag_v2",
)
HOLD = "HOLD_CANDIDATE_RAW_AXIS_NUMERICAL_IMPLEMENTATION_INCOMPLETE"


class Role8V3Hold(RuntimeError):
    """Internal control-flow exception carrying only the exact public HOLD."""


class HoldArgumentParser(argparse.ArgumentParser):
    """Convert every CLI rejection into the same fail-closed status."""

    def error(self, message):
        del message
        raise Role8V3Hold(HOLD)


def _canonical_absolute_path(raw):
    if not isinstance(raw, str) or not raw:
        raise Role8V3Hold(HOLD)
    try:
        raw.encode("ascii")
    except UnicodeEncodeError as error:
        raise Role8V3Hold(HOLD) from error
    if (
        not raw.startswith("/")
        or "\\" in raw
        or "//" in raw
        or os.path.normpath(raw) != raw
        or os.path.abspath(raw) != raw
    ):
        raise Role8V3Hold(HOLD)
    return raw


def _parse_cli(argv=None):
    parser = HoldArgumentParser(
        description=__doc__,
        allow_abbrev=False,
        add_help=False,
    )
    parser.add_argument("--request", required=True)
    parser.add_argument("--output", required=True)
    arguments = parser.parse_args(argv)
    request = _canonical_absolute_path(arguments.request)
    output = _canonical_absolute_path(arguments.output)
    if request == output:
        raise Role8V3Hold(HOLD)
    return request, output


def _fail_closed_preflight(request, output):
    del request, output
    raise Role8V3Hold(HOLD)


def main(argv=None):
    try:
        request, output = _parse_cli(argv)
        _fail_closed_preflight(request, output)
    except Role8V3Hold:
        print(HOLD, file=sys.stderr)
        return 2
    raise AssertionError("unreachable role-8 v3 producer state")


if __name__ == "__main__":
    raise SystemExit(main())
