#!/usr/bin/env python3
"""Deterministic finite-matrix Green/pole/residue audit.

The fixture is an exact four-state product CTMC.  It demonstrates a shared
U-dark free/killed mode, a coupled killed pole detected by det(I+G K), and
nonzero channel residues whose sum vanishes for the total-flux observable.
Nothing in this script asserts continuum meromorphic continuation.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
from vkcore.encounter import (
    DEFAULT_GREEN_ACCURACY_TOLERANCE,
    build_ctmc_catalytic_encounter,
    ctmc_green_resolvent,
    point_initial_distribution,
    reflecting_ctmc_generator,
)
from vkcore.provenance import build_artifact_manifest, write_manifest

HERE = Path(__file__).resolve()
REPORT = HERE.parents[1]
REPO = HERE.parents[4]
DATA = REPORT / "artifacts" / "data"
NOTE = REPORT / "notes" / "finite_matrix_green_spectral_audit.md"
DATA.mkdir(parents=True, exist_ok=True)

JUMP_RATE = 2.0
REACTION_RATES = (0.5, 0.5)
COUPLED_POLE = -2.5
NEAR_POLE_EPSILON = 1e-4
DETERMINANT_POINTS = (0.37 + 0.19j, -0.23 + 0.11j)


def _stable(value: float, digits: int = 15) -> float:
    number = float(value)
    if abs(number) < 5e-16:
        return 0.0
    return float(f"{number:.{digits}g}")


def _real_array(values: Any) -> list[Any]:
    array = np.asarray(values, dtype=float)
    if array.ndim == 1:
        return [_stable(value) for value in array]
    return [[_stable(value) for value in row] for row in array]


def _complex(value: complex) -> dict[str, float]:
    number = complex(value)
    return {"real": _stable(number.real), "imag": _stable(number.imag)}


def _complex_array(values: Any) -> list[dict[str, float]]:
    return [_complex(value) for value in np.asarray(values).reshape(-1)]


def _selector(model: Any) -> np.ndarray:
    selector = np.zeros((model.state_count, model.channel_count), dtype=float)
    selector[model.catalytic_state_indices, np.arange(model.channel_count)] = 1.0
    return selector


def main() -> None:
    walker = reflecting_ctmc_generator(2, jump_rate=JUMP_RATE)
    model = build_ctmc_catalytic_encounter(
        walker,
        walker,
        catalytic_sites=(0, 1),
        reaction_rates=REACTION_RATES,
    )
    initial = point_initial_distribution(2, (0, 0))
    identity = np.eye(model.state_count)
    selector = _selector(model)
    rate_matrix = np.diag(model.reaction_rates)

    dark = np.asarray((0.0, 1.0, -1.0, 0.0)) / np.sqrt(2.0)
    dark_lambda = -2.0
    dark_payload = {
        "eigenvalue": dark_lambda,
        "normalized_vector": _real_array(dark),
        "selector_coupling_inf_norm": _stable(
            np.linalg.norm(selector.T @ dark, ord=np.inf)
        ),
        "free_eigen_residual_inf_norm": _stable(
            np.linalg.norm(model.free_generator @ dark - dark_lambda * dark, ord=np.inf)
        ),
        "killed_eigen_residual_inf_norm": _stable(
            np.linalg.norm(model.killed_generator @ dark - dark_lambda * dark, ord=np.inf)
        ),
        "interpretation": (
            "shared free/killed eigenmode invisible to U; the restricted determinant "
            "is not defined at this free eigenvalue"
        ),
    }

    coupled = np.asarray((1.0, 0.0, 0.0, -1.0)) / np.sqrt(2.0)
    free_spectrum = np.linalg.eigvalsh(model.free_generator)
    free_spectrum[np.abs(free_spectrum) < 1e-12] = 0.0
    killed_spectrum = np.linalg.eigvalsh(model.killed_generator)
    free_at_pole = COUPLED_POLE * identity - model.free_generator
    free_resolvent = np.linalg.solve(free_at_pole, identity)
    restricted_green = selector.T @ free_resolvent @ selector
    renewal = np.eye(model.channel_count) + restricted_green @ rate_matrix
    renewal_null = np.asarray((1.0, -1.0)) / np.sqrt(2.0)
    channel_residue = float(initial @ coupled) * (coupled @ model.channel_rate_matrix)
    total_observable = np.ones(model.channel_count)
    total_residue = float(channel_residue @ total_observable)

    pole_rejection: dict[str, str]
    try:
        ctmc_green_resolvent(model, initial, COUPLED_POLE)
    except ValueError as error:
        pole_rejection = {"exception": type(error).__name__, "message": str(error)}
    else:
        raise RuntimeError("exact killed pole was not rejected")

    near_pole = ctmc_green_resolvent(
        model,
        initial,
        COUPLED_POLE + NEAR_POLE_EPSILON,
        verify_direct=True,
    )
    scaled_near_pole = NEAR_POLE_EPSILON * near_pole.channel_transform

    determinant_checks: list[dict[str, Any]] = []
    for point in DETERMINANT_POINTS:
        green = ctmc_green_resolvent(model, initial, point, verify_direct=True)
        left = np.linalg.det(point * identity - model.killed_generator)
        right = np.linalg.det(point * identity - model.free_generator)
        right *= np.linalg.det(green.renewal_matrix)
        determinant_checks.append(
            {
                "s": _complex(point),
                "det_sI_minus_T": _complex(left),
                "det_sI_minus_L0_times_det_renewal": _complex(right),
                "absolute_error": _stable(abs(left - right)),
                "green_direct_resolvent_error": _stable(
                    green.max_direct_resolvent_error
                ),
                "green_accuracy_diagnostic": _stable(
                    green.max_accuracy_diagnostic
                ),
            }
        )

    zero_rate_model = build_ctmc_catalytic_encounter(
        walker,
        walker,
        catalytic_sites=(0, 1),
        reaction_rates=(0.0, 0.5),
    )
    zero_rate_s = -0.3 + 0.2j
    zero_rate_green = ctmc_green_resolvent(
        zero_rate_model,
        initial,
        zero_rate_s,
        verify_direct=True,
    )

    coupled_payload = {
        "eigenvalue": COUPLED_POLE,
        "normalized_vector": _real_array(coupled),
        "selector_coupling_l2_norm": _stable(np.linalg.norm(selector.T @ coupled)),
        "killed_eigen_residual_inf_norm": _stable(
            np.linalg.norm(
                model.killed_generator @ coupled - COUPLED_POLE * coupled,
                ord=np.inf,
            )
        ),
        "distance_to_free_spectrum": _stable(
            np.min(np.abs(free_spectrum - COUPLED_POLE))
        ),
        "restricted_green_at_pole": _real_array(restricted_green),
        "renewal_matrix_at_pole": _real_array(renewal),
        "renewal_determinant": _stable(np.linalg.det(renewal)),
        "renewal_smallest_singular_value": _stable(
            np.linalg.svd(renewal, compute_uv=False)[-1]
        ),
        "renewal_null_vector": _real_array(renewal_null),
        "renewal_null_residual_inf_norm": _stable(
            np.linalg.norm(renewal @ renewal_null, ord=np.inf)
        ),
        "api_rejection_at_exact_pole": pole_rejection,
        "near_pole": {
            "epsilon": NEAR_POLE_EPSILON,
            "s": COUPLED_POLE + NEAR_POLE_EPSILON,
            "epsilon_times_channel_transform": _complex_array(scaled_near_pole),
            "epsilon_times_total_transform": _complex(
                np.sum(scaled_near_pole)
            ),
            "max_difference_from_eigenprojector_residue": _stable(
                np.max(np.abs(scaled_near_pole - channel_residue))
            ),
            "green_method": near_pole.method,
            "green_accuracy_diagnostic": _stable(
                near_pole.max_accuracy_diagnostic
            ),
        },
    }

    residue_payload = {
        "initial_state": [0, 0],
        "observable": "total channel flux",
        "observable_channel_weights": _real_array(total_observable),
        "channel_residues": _real_array(channel_residue),
        "total_observable_residue": _stable(total_residue),
        "minimum_absolute_channel_residue": _stable(
            np.min(np.abs(channel_residue))
        ),
        "interpretation": (
            "each channel is coupled to the pole, but antisymmetric residues "
            "cancel in the summed observable"
        ),
    }

    if dark_payload["selector_coupling_inf_norm"] > 1e-14:
        raise RuntimeError("declared dark mode couples to U")
    if abs(coupled_payload["renewal_determinant"]) > 1e-13:
        raise RuntimeError("coupled killed pole did not zero the renewal determinant")
    if abs(residue_payload["total_observable_residue"]) > 1e-14:
        raise RuntimeError("channel residues did not cancel in total")
    if coupled_payload["near_pole"]["max_difference_from_eigenprojector_residue"] > 4e-6:
        raise RuntimeError("near-pole transform did not recover the channel residues")

    payload = {
        "claim_scope": (
            "exact finite 4x4 CTMC matrix audit only; no continuum operator "
            "meromorphic-continuation claim"
        ),
        "conventions": {
            "state_order": ["(0,0)", "(0,1)", "(1,0)", "(1,1)"],
            "row_generator": True,
            "green_domain": "finite complex s outside sigma(L0)",
            "green_method": "finite_free_green_woodbury",
            "default_accuracy_tolerance": DEFAULT_GREEN_ACCURACY_TOLERANCE,
        },
        "model": {
            "walker_generator": _real_array(walker),
            "free_generator": _real_array(model.free_generator),
            "killed_generator": _real_array(model.killed_generator),
            "selector": _real_array(selector),
            "rate_matrix": _real_array(rate_matrix),
            "free_spectrum": _real_array(free_spectrum),
            "killed_spectrum": _real_array(killed_spectrum),
        },
        "dark_shared_mode": dark_payload,
        "coupled_killed_pole": coupled_payload,
        "residue_cancellation": residue_payload,
        "determinant_lemma_checks": determinant_checks,
        "zero_rate_inverse_free_check": {
            "s": _complex(zero_rate_s),
            "reaction_rates": [0.0, 0.5],
            "channel_transform": _complex_array(
                zero_rate_green.channel_transform
            ),
            "zero_channel_transform": _complex(
                zero_rate_green.channel_transform[0]
            ),
            "direct_resolvent_error": _stable(
                zero_rate_green.max_direct_resolvent_error
            ),
        },
        "not_certified": [
            "continuum Fredholm or meromorphic continuation",
            "unbounded or trace-space reaction operators",
            "production-model pole isolation or Jordan structure",
            "Bromwich inversion or time-domain mode visibility beyond this fixture",
        ],
    }

    artifact = DATA / "finite_matrix_green_spectral_audit.json"
    artifact.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    manifest = build_artifact_manifest(
        repo_root=REPO,
        generator=str(HERE.relative_to(REPO)),
        command=["python", str(HERE.relative_to(REPO))],
        model_spec={
            "scope": "finite 4x4 matrix only",
            "walker_jump_rate": JUMP_RATE,
            "reaction_rates": list(REACTION_RATES),
            "catalytic_sites": [0, 1],
            "coupled_pole": COUPLED_POLE,
            "near_pole_epsilon": NEAR_POLE_EPSILON,
            "continuum_continuation_claimed": False,
        },
        dependencies=[
            NOTE,
            REPO / "packages" / "vkcore" / "src" / "vkcore" / "encounter.py",
            REPO / "packages" / "vkcore" / "src" / "vkcore" / "provenance.py",
        ],
        outputs=[artifact],
    )
    write_manifest(DATA / "finite_matrix_green_spectral_audit.manifest.json", manifest)


if __name__ == "__main__":
    main()
