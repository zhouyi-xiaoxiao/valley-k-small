"""Fail-closed role-9 v3 stationary-integral producer entrypoint.

Round 179 fixes the numerical operation model and Round 180 fixes the
plan-v2/request-v4 protocol, but neither round supplies a source-separated
role-9 numerical implementation.  This future-version entrypoint therefore
freezes the public CLI and role-specific protocol identities without opening
the request or touching its planned output.  Every syntactically valid
invocation terminates at the exact implementation-incomplete HOLD below.
"""

from __future__ import annotations

import argparse
import os
import pathlib
import sys
import typing

REQUEST_SCHEMA: typing.Final = "encounter_continuum_c1_n0_stationary_integrals_request_v4"
OUTPUT_SCHEMA: typing.Final = "encounter_c1_n0_stationary_physical_integral_source_v2"
RECEIPT_SCHEMA: typing.Final = "encounter_c1_n0_stationary_physical_integral_validation_receipt_v1"
PLAN_SCHEMA: typing.Final = "encounter_continuum_c1_n0_roles_8_10_replay_plan_v2"
BUNDLE_SCHEMA: typing.Final = "encounter_continuum_c1_n0_precommit_candidate_bundle_v2"
RUNTIME_CLOSURE_SCHEMA: typing.Final = (
    "encounter_continuum_c1_n0_roles_8_10_implementation_runtime_closure_v1"
)
COMMITMENT_SCHEMA: typing.Final = "encounter_external_predecessor_commitment_v1"
REQUEST_STATUS: typing.Final = (
    "EXTERNAL_PREDECESSOR_COMMITMENT_BOUND_RESULT_BLIND_REQUEST_NO_EXECUTION_RESULT"
)
ROLE_ID: typing.Final = 9
ROLE_NAME: typing.Final = "role9_stationary_physical_integral"
PRODUCER_BASENAME: typing.Final = (
    "build_continuum_c1_n0_candidate_native_stationary_integrals_v3.py"
)
VERIFIER_BASENAME: typing.Final = (
    "validate_continuum_c1_n0_candidate_native_stationary_integrals_v3.py"
)

DIRECT_AUTHORITY_KEYS: typing.Final = (
    "anti_vacuity_policy",
    "configuration",
    "ideal_formula",
    "member_spec",
    "method_parameter_registry",
    "reference_density",
    "sealed_authentication_mirror",
)
METHOD_PARAMETER_IDS: typing.Final = (
    "stationary_directed_mpfr_320_v2",
    "stationary_directed_mpfr_640_sentinel_v2",
    "exact_fraction_expression_dag_v2",
)
METHOD_PARAMETER_SHA256S: typing.Final = (
    "1226335c739734613508bacbaba3d8fb7f6c0607557d11190fe846ba08000da7",
    "67d76049763a982144e2b41fc1722ce6e4663bccb8bdcec9e2af398d7c1511f9",
    "c1e11de7305a3035973e98d1913e14075f0ba3b2a32180a73689aee4c9b4b851",
)
PLANNED_NUMERICAL_BACKEND_MODULE: typing.Final = "gmpy2"

HOLD_CANDIDATE_STATIONARY_NUMERICAL_IMPLEMENTATION_INCOMPLETE: typing.Final = (
    "HOLD_CANDIDATE_STATIONARY_NUMERICAL_IMPLEMENTATION_INCOMPLETE"
)
HOLD_NUMERICAL_INCOMPLETE: typing.Final = (
    HOLD_CANDIDATE_STATIONARY_NUMERICAL_IMPLEMENTATION_INCOMPLETE
)


class CandidateStationaryV3Failure(RuntimeError):
    """Fail-closed producer exception with a stable machine-readable code."""

    def __init__(self, detail: str = "") -> None:
        self.code = HOLD_NUMERICAL_INCOMPLETE
        self.detail = detail
        super().__init__(HOLD_NUMERICAL_INCOMPLETE)


class HoldArgumentParser(argparse.ArgumentParser):
    """Convert every CLI rejection into the same public fail-closed HOLD."""

    def error(self, message: str) -> typing.NoReturn:
        raise CandidateStationaryV3Failure(message)


def _canonical_absolute_path(value: str, label: str) -> pathlib.Path:
    """Check only lexical CLI form; deliberately perform no filesystem I/O."""

    if (
        not value
        or "\x00" in value
        or not value.startswith("/")
        or value.startswith("//")
        or os.path.normpath(value) != value
        or os.path.abspath(value) != value
    ):
        raise CandidateStationaryV3Failure(f"{label} must be a canonical absolute path")
    return pathlib.Path(value)


def _assert_frozen_source_contract() -> None:
    """Reject accidental drift before reaching the mandatory numerical HOLD."""

    if (
        pathlib.Path(__file__).name != PRODUCER_BASENAME
        or ROLE_ID != 9
        or ROLE_NAME != "role9_stationary_physical_integral"
        or len(DIRECT_AUTHORITY_KEYS) != 7
        or len(METHOD_PARAMETER_IDS) != 3
        or len(METHOD_PARAMETER_IDS) != len(METHOD_PARAMETER_SHA256S)
        or PLANNED_NUMERICAL_BACKEND_MODULE != "gmpy2"
    ):
        raise CandidateStationaryV3Failure("frozen role-9 v3 producer identity drift")


def build_from_request(
    request_path: pathlib.Path,
    output_path: pathlib.Path,
) -> typing.NoReturn:
    """Stop before request authentication, numerical work, or publication."""

    _assert_frozen_source_contract()
    request = _canonical_absolute_path(str(request_path), "request")
    output = _canonical_absolute_path(str(output_path), "output")
    if request == output:
        raise CandidateStationaryV3Failure("request and output paths must differ")
    raise CandidateStationaryV3Failure()


def _parse_cli(
    argv: typing.Sequence[str] | None = None,
) -> tuple[pathlib.Path, pathlib.Path]:
    parser = HoldArgumentParser(
        description=__doc__,
        allow_abbrev=False,
        add_help=False,
    )
    parser.add_argument("--request", required=True)
    parser.add_argument("--output", required=True)
    arguments = parser.parse_args(argv)
    request = _canonical_absolute_path(arguments.request, "request CLI")
    output = _canonical_absolute_path(arguments.output, "output CLI")
    if request == output:
        raise CandidateStationaryV3Failure("request and output CLI paths must differ")
    return request, output


def main(argv: typing.Sequence[str] | None = None) -> int:
    try:
        request, output = _parse_cli(argv)
        build_from_request(request, output)
    except CandidateStationaryV3Failure:
        print(HOLD_NUMERICAL_INCOMPLETE, file=sys.stderr)
        return 2
    raise AssertionError("role-9 v3 producer cannot claim success")


if __name__ == "__main__":
    raise SystemExit(main())
