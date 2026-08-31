"""Fail-closed producer shell for candidate-native role-10 killing geometry.

The shared verifier module owns only protocol and authority validation.  This
producer invokes those gates using its independently pinned producer identity,
then raises the mandatory numerical-implementation hold.  It cannot create the
planned directory artifact.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Final, NoReturn, Sequence

import validate_continuum_c1_n0_candidate_native_killing_factor_geometry_v2 as _core

REQUEST_SCHEMA: Final = _core.REQUEST_SCHEMA
OUTPUT_SCHEMA: Final = _core.OUTPUT_SCHEMA
RECEIPT_SCHEMA: Final = _core.RECEIPT_SCHEMA
PLAN_SCHEMA: Final = _core.PLAN_SCHEMA
BUNDLE_SCHEMA: Final = _core.BUNDLE_SCHEMA
COMMITMENT_SCHEMA: Final = _core.COMMITMENT_SCHEMA
ROLE_ID: Final = _core.ROLE_ID
ROLE_NAME: Final = _core.ROLE_NAME
PLAN_STATUS: Final = _core.PLAN_STATUS
BUNDLE_STATUS: Final = _core.BUNDLE_STATUS
REQUEST_STATUS: Final = _core.REQUEST_STATUS
COMMITMENT_STATUS: Final = _core.COMMITMENT_STATUS

MEMBER_SCHEMA: Final = _core.MEMBER_SCHEMA
MEMBER_SHA256: Final = _core.MEMBER_SHA256
MEMBER_IDENTITY_SHA256: Final = _core.MEMBER_IDENTITY_SHA256
PARAMETER_SCHEMA: Final = _core.PARAMETER_SCHEMA
PARAMETER_SHA256: Final = _core.PARAMETER_SHA256
FACTORIZATION_SCHEMA: Final = _core.FACTORIZATION_SCHEMA
FACTORIZATION_SHA256: Final = _core.FACTORIZATION_SHA256
ANTI_VACUITY_POLICY_SCHEMA: Final = _core.ANTI_VACUITY_POLICY_SCHEMA
ANTI_VACUITY_POLICY_SHA256: Final = _core.ANTI_VACUITY_POLICY_SHA256
REFERENCE_SCHEMA: Final = _core.REFERENCE_SCHEMA
FORMULA_SCHEMA: Final = _core.FORMULA_SCHEMA
CONFIGURATION_SCHEMA: Final = _core.CONFIGURATION_SCHEMA

PRECOMMIT_CONTEXT_DOMAIN: Final = _core.PRECOMMIT_CONTEXT_DOMAIN
REPLAY_CONTEXT_DOMAIN: Final = _core.REPLAY_CONTEXT_DOMAIN
PRECOMMIT_PROJECTION_DOMAIN: Final = _core.PRECOMMIT_PROJECTION_DOMAIN
CONFIGURATION_INVENTORY_DOMAIN: Final = _core.CONFIGURATION_INVENTORY_DOMAIN
PARTITION_INVENTORY_DOMAIN: Final = _core.PARTITION_INVENTORY_DOMAIN
COMMITMENT_MESSAGE_DOMAIN: Final = _core.COMMITMENT_MESSAGE_DOMAIN
CONFIGURATION_INVENTORY_SHA256: Final = _core.CONFIGURATION_INVENTORY_SHA256
PARTITION_INVENTORY_SHA256: Final = _core.PARTITION_INVENTORY_SHA256

CONTACT_PROFILE_PARAMETER_ID: Final = _core.CONTACT_PROFILE_PARAMETER_ID
ANALYTIC_AREA_PARAMETER_ID: Final = _core.ANALYTIC_AREA_PARAMETER_ID
VERIFIER_PARAMETER_ID: Final = _core.VERIFIER_PARAMETER_ID
CLASSIFICATION_PARAMETER_ID: Final = _core.CLASSIFICATION_PARAMETER_ID

HOLD_REQUEST: Final = _core.HOLD_REQUEST
HOLD_AUTHORITY: Final = _core.HOLD_AUTHORITY
HOLD_RUNTIME: Final = _core.HOLD_RUNTIME
HOLD_METHOD: Final = _core.HOLD_METHOD
HOLD_PARTITION: Final = _core.HOLD_PARTITION
HOLD_CANDIDATE_KILLING_NUMERICAL_IMPLEMENTATION_INCOMPLETE: Final = (
    _core.HOLD_CANDIDATE_KILLING_NUMERICAL_IMPLEMENTATION_INCOMPLETE
)
HOLD_NUMERICAL_INCOMPLETE: Final = _core.HOLD_NUMERICAL_INCOMPLETE

_REQUEST_KEYS: Final = _core._REQUEST_KEYS
_PLAN_KEYS: Final = _core._PLAN_KEYS
_PLAN_ENTRY_KEYS: Final = _core._PLAN_ENTRY_KEYS
_EXPECTED_METHOD_SELECTION: Final = _core._EXPECTED_METHOD_SELECTION

canonical_bytes = _core.canonical_bytes
_domain_digest = _core._domain_digest
_runtime_versions = _core._runtime_versions
_configuration_inventory = _core._configuration_inventory
_partition_inventory = _core._partition_inventory
_validate_result_blind_keys = _core._validate_result_blind_keys


class CandidateKillingFailure(RuntimeError):
    """Producer-side fail-closed exception."""

    def __init__(self, code: str, detail: str = "") -> None:
        self.code = code
        self.detail = detail
        message = code if code == HOLD_NUMERICAL_INCOMPLETE else f"{code}: {detail}"
        super().__init__(message)


def _translate(error: _core.CandidateKillingVerificationFailure) -> NoReturn:
    raise CandidateKillingFailure(error.code, error.detail) from error


def build_from_request(request_path: Path, output_path: Path) -> NoReturn:
    """Validate the complete shell and stop before any numerical/output action."""

    try:
        _core.validate_protocol(
            request_path,
            output_path,
            None,
            caller_path=Path(__file__).resolve(),
            caller_role="producer",
        )
    except _core.CandidateKillingVerificationFailure as error:
        _translate(error)
    raise CandidateKillingFailure(HOLD_NUMERICAL_INCOMPLETE)


def _parse_cli(argv: Sequence[str] | None = None) -> tuple[Path, Path]:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--request", required=True)
    parser.add_argument("--output", required=True)
    arguments = parser.parse_args(argv)
    try:
        request = _core._absolute(arguments.request, HOLD_REQUEST, "request CLI")
        output = _core._absolute(arguments.output, HOLD_REQUEST, "output CLI")
    except _core.CandidateKillingVerificationFailure as error:
        _translate(error)
    if request == output:
        raise CandidateKillingFailure(HOLD_REQUEST, "CLI paths must differ")
    return request, output


def main(argv: Sequence[str] | None = None) -> int:
    try:
        request, output = _parse_cli(argv)
        build_from_request(request, output)
    except CandidateKillingFailure as error:
        print(error, file=sys.stderr)
        return 2
    raise AssertionError("role-10 producer shell cannot claim success")


if __name__ == "__main__":
    raise SystemExit(main())
