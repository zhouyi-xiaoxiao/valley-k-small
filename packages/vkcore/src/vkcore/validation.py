from __future__ import annotations

from collections.abc import Mapping, Sequence

import numpy as np


ArrayLike = Sequence[float] | np.ndarray
ComponentLike = Mapping[str, ArrayLike] | Sequence[ArrayLike] | np.ndarray


def _as_float_array(values: ArrayLike, *, name: str) -> np.ndarray:
    arr = np.asarray(values, dtype=float)
    if not np.all(np.isfinite(arr)):
        raise ValueError(f"{name} contains non-finite values")
    return arr


def check_nonnegative(P: ArrayLike, tol: float = 1e-15) -> bool:
    """Validate that all entries are nonnegative up to a small tolerance."""

    arr = _as_float_array(P, name="P")
    min_value = float(np.min(arr)) if arr.size else 0.0
    if min_value < -float(tol):
        raise ValueError(f"P has negative entries below tolerance: min={min_value:g}")
    return True


def check_row_stochastic(P: ArrayLike, tol: float = 1e-12) -> bool:
    """Validate a discrete-time transition matrix with rows summing to one.

    Note on defaults: row sums accumulate O(n) float additions, so this check
    uses 1e-12, while ``check_nonnegative`` defaults to the tighter 1e-15 for
    entrywise sign checks. When called from here, nonnegativity inherits this
    looser ``tol`` on purpose — both checks then describe the same matrix at
    the same precision.
    """

    arr = _as_float_array(P, name="P")
    if arr.ndim != 2:
        raise ValueError(f"P must be a 2D transition matrix, got ndim={arr.ndim}")
    check_nonnegative(arr, tol=tol)
    row_sums = arr.sum(axis=1)
    err = float(np.max(np.abs(row_sums - 1.0))) if row_sums.size else 0.0
    if err > float(tol):
        raise ValueError(f"P rows are not stochastic: max row-sum error={err:g}")
    return True


def mass_balance_error(f: ArrayLike, survival: ArrayLike) -> float:
    """Return max error in the discrete identity f[t] = S[t] - S[t + 1].

    ``survival`` may have length ``len(f) + 1`` for a closed finite horizon, or
    length ``len(f)`` when only consecutive survival differences are available.
    In the second case the final mass point cannot be checked.
    """

    f_arr = _as_float_array(f, name="f").reshape(-1)
    s_arr = _as_float_array(survival, name="survival").reshape(-1)
    if s_arr.size == f_arr.size + 1:
        expected = s_arr[:-1] - s_arr[1:]
        observed = f_arr
    elif s_arr.size == f_arr.size:
        if s_arr.size < 2:
            return 0.0 if f_arr.size <= 1 else float("inf")
        expected = s_arr[:-1] - s_arr[1:]
        observed = f_arr[:-1]
    else:
        raise ValueError(
            "survival length must equal len(f) or len(f) + 1; "
            f"got len(f)={f_arr.size}, len(survival)={s_arr.size}"
        )
    return float(np.max(np.abs(observed - expected))) if observed.size else 0.0


def check_mass_balance(f: ArrayLike, survival: ArrayLike, tol: float = 1e-10) -> bool:
    """Validate the discrete survival-to-density mass-balance identity."""

    err = mass_balance_error(f, survival)
    if err > float(tol):
        raise ValueError(f"mass balance failed: error={err:g}")
    return True


def _components_array(components: ComponentLike) -> np.ndarray:
    if isinstance(components, Mapping):
        values = list(components.values())
        if not values:
            return np.empty((0, 0), dtype=float)
        return np.vstack([_as_float_array(v, name=f"component {k}").reshape(-1) for k, v in components.items()])

    arr = np.asarray(components, dtype=float)
    if not np.all(np.isfinite(arr)):
        raise ValueError("components contains non-finite values")
    if arr.ndim == 1:
        return arr.reshape(1, -1)
    if arr.ndim != 2:
        raise ValueError(f"components must be 1D/2D or mapping of 1D arrays, got ndim={arr.ndim}")
    return arr


def decomposition_error(total: ArrayLike, components: ComponentLike) -> float:
    """Return max error in total[t] = sum_c components[c, t]."""

    total_arr = _as_float_array(total, name="total").reshape(-1)
    comp_arr = _components_array(components)
    if comp_arr.size == 0 and total_arr.size == 0:
        return 0.0
    if comp_arr.ndim != 2 or comp_arr.shape[1] != total_arr.size:
        raise ValueError(
            "component length mismatch: "
            f"total length={total_arr.size}, component shape={comp_arr.shape}"
        )
    summed = comp_arr.sum(axis=0)
    return float(np.max(np.abs(total_arr - summed))) if total_arr.size else 0.0


def check_channel_decomposition(
    total: ArrayLike,
    components: ComponentLike,
    tol: float = 1e-10,
) -> bool:
    """Validate that a total distribution equals the sum of channel components."""

    err = decomposition_error(total, components)
    if err > float(tol):
        raise ValueError(f"channel decomposition failed: error={err:g}")
    return True

