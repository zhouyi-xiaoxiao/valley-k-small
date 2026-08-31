from __future__ import annotations

import modal_certificate_lp_poc as modal
import numpy as np
import pytest


def test_spec_rejects_non_alternating_or_mismatched_checkpoints() -> None:
    with pytest.raises(ValueError, match="alternate"):
        modal.SignCertificateSpec("bad", 1, (1.0, 2.0), (1, 1), 0.0).validate(2)
    with pytest.raises(ValueError, match="2m"):
        modal.SignCertificateSpec("bad", 2, (1.0, 2.0), (1, -1), 0.0).validate(2)


def test_solver_rejects_zero_scale_and_nonfinite_rows() -> None:
    spec = modal.SignCertificateSpec("m1", 1, (1.0, 2.0), (1, -1), 0.0)
    with pytest.raises(ValueError, match="positive finite scale"):
        modal.solve_sign_certificate(np.zeros((2, 2)), spec)
    with pytest.raises(ValueError, match="all be finite"):
        modal.solve_sign_certificate(np.asarray([[1.0, np.nan], [-1.0, -2.0]]), spec)


def test_synthetic_separated_channels_have_positive_two_mode_certificate() -> None:
    times = np.asarray((0.5, 1.5, 3.5, 4.5), dtype=float)
    centres = np.asarray((1.0, 4.0), dtype=float)
    width = 0.35
    displacement = times[:, None] - centres[None, :]
    values = np.exp(-0.5 * (displacement / width) ** 2)
    derivatives = -(displacement / width**2) * values
    spec = modal.SignCertificateSpec("synthetic_m2", 2, tuple(times), (1, -1, 1, -1), 0.05)
    result = modal.solve_sign_certificate(derivatives, spec)
    assert result["status"] == modal.STATUS_PASS
    assert result["normalized_margin"] > 0.4
    assert min(result["weights"]) >= 0.05
    assert sum(result["weights"]) == pytest.approx(1.0, abs=2.0e-13)


def test_broad_primary_selector_matches_exploratory_regression() -> None:
    rows = modal.select_broad_controls()
    expected = {
        "m1": (
            (0.03, 0.9100000000000001, 0.03, 0.03),
            0.8809904119598448,
        ),
        "m2": (
            (0.5420243013882049, 0.03, 0.048245050837663034, 0.37973064777413196),
            0.32540424848060423,
        ),
        "m3": (
            (0.40162853586287739, 0.2761816314605931, 0.03, 0.29218983267652948),
            0.13616273641487356,
        ),
    }
    for name, (weights, margin) in expected.items():
        assert rows[name]["status"] == modal.STATUS_PASS
        assert rows[name]["weights"] == pytest.approx(weights, abs=2.0e-12)
        assert rows[name]["normalized_margin"] == pytest.approx(margin, abs=2.0e-12)


def test_canonical_json_rejects_nonfinite_payload() -> None:
    with pytest.raises(ValueError):
        modal.canonical_json({"bad": float("nan")})
