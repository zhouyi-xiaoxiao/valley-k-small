import math
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple, Set

import json
import numpy as np
from joblib import Parallel, delayed
import matplotlib
from matplotlib import colors

matplotlib.use("Agg")
import matplotlib.pyplot as plt


REPORT_ROOT = Path(__file__).resolve().parents[1]
FIGURES_DIR = REPORT_ROOT / "figures"
DATA_DIR = REPORT_ROOT / "data"


def _ensure_output_dirs() -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)


# -----------------------------
# Ground-truth model wiring
# -----------------------------
# Paper conventions:
# - Nodes labeled 1..N.
# - K = 2k (even), unbiased jump to any of ±1..±k uniformly (Eq. 1).
# - Artificial SWN for Fig. 3: n0 = 1, target n = N/2 (N even),
#   single shortcut between (n+1) and (n0+5), i.e. (N/2+1) <-> 6 (paper indexing).
#
# Internally we use 0..N-1 indexing; convert with (paper_idx-1).


@dataclass(frozen=True)
class GraphData:
    N: int
    K: int
    n0: int            # internal 0..N-1
    target: int        # internal 0..N-1
    sc_u: int          # internal shortcut endpoint
    sc_v: int          # internal shortcut endpoint
    neigh_pad: np.ndarray   # (N, deg_max) int16, padded with -1
    deg: np.ndarray         # (N,) int16
    src: np.ndarray         # (E,) int32  directed edges
    dst: np.ndarray         # (E,) int32
    w: np.ndarray           # (E,) float64 weights 1/deg(src)


def _wrap_paper(i: int, N: int) -> int:
    """Wrap integer index into {1,..,N}."""
    return ((i - 1) % N) + 1


def build_graph(
    N: int,
    K: int,
    n0_paper: int = 1,
    target_paper: Optional[int] = None,
    shortcut_offset: int = 5,
    directed_shortcut: bool = False,
) -> GraphData:
    """
    Build K-neighbour ring lattice with one shortcut:
        (target+1) <-> (n0+shortcut_offset)   in paper indexing.
    If directed_shortcut=True, use only (n0+shortcut_offset) -> (target+1).
    """
    if K % 2 != 0:
        raise ValueError("Model assumes K = 2k is even (Eq. 1).")
    if target_paper is None:
        if N % 2 != 0:
            raise ValueError("Paper uses target n=N/2; please use even N.")
        target_paper = N // 2

    n0 = n0_paper - 1
    target = target_paper - 1

    k = K // 2
    neigh: List[Set[int]] = [set() for _ in range(N)]
    for i in range(N):
        for r in range(1, k + 1):
            neigh[i].add((i + r) % N)
            neigh[i].add((i - r) % N)

    # Shortcut endpoints (paper): (target+1) and (n0+shortcut_offset)
    sc_u_paper = _wrap_paper(target_paper + 1, N)
    sc_v_paper = _wrap_paper(n0_paper + shortcut_offset, N)
    sc_u = sc_u_paper - 1
    sc_v = sc_v_paper - 1
    if directed_shortcut:
        neigh[sc_v].add(sc_u)
    else:
        neigh[sc_u].add(sc_v)
        neigh[sc_v].add(sc_u)

    deg = np.array([len(neigh[i]) for i in range(N)], dtype=np.int16)
    deg_max = int(deg.max())
    neigh_pad = -np.ones((N, deg_max), dtype=np.int16)
    for i in range(N):
        arr = np.fromiter(neigh[i], dtype=np.int16)
        neigh_pad[i, : arr.size] = arr

    # Directed edge list for fast master-equation propagation (vectorized)
    src_list: List[int] = []
    dst_list: List[int] = []
    w_list: List[float] = []
    for i in range(N):
        p = 1.0 / float(deg[i])
        for j in neigh[i]:
            src_list.append(i)
            dst_list.append(j)
            w_list.append(p)
    src = np.asarray(src_list, dtype=np.int32)
    dst = np.asarray(dst_list, dtype=np.int32)
    w = np.asarray(w_list, dtype=np.float64)

    return GraphData(
        N=N,
        K=K,
        n0=n0,
        target=target,
        sc_u=sc_u,
        sc_v=sc_v,
        neigh_pad=neigh_pad,
        deg=deg,
        src=src,
        dst=dst,
    w=w,
)


# -----------------------------
# Analytical / AW Inversion Method (Prototype)
# -----------------------------
def get_eigenvalues_ring(N: int, K: int) -> np.ndarray:
    """Structure function eigenvalues for K-neighbour ring."""
    k = K // 2
    l = np.arange(N, dtype=np.float64)
    cos_sum = np.zeros(N, dtype=np.float64)
    for r in range(1, k + 1):
        cos_sum += np.cos(2 * np.pi * r * l / N)
    lambda_l = (2.0 / K) * cos_sum
    return lambda_l.astype(np.complex128)


def get_Q_ring_z(diff_n: int, z: complex, N: int, lambda_l: np.ndarray) -> complex:
    """
    Ring propagator (Eq. S7): Q_{n0}(n, z) with translation invariance.
    """
    z_arr = np.atleast_1d(z).astype(np.complex128)
    l = np.arange(N, dtype=np.float64)
    numer = np.cos(2 * np.pi * l * diff_n / N)
    denom = 1.0 - z_arr[:, None] * lambda_l[None, :]
    res = np.sum(numer / denom, axis=1) / N
    if np.ndim(z) == 0:
        return res[0]
    return res


def get_S_defect_z(
    n: int,
    n0: int,
    z: complex,
    N: int,
    K: int,
    sc_src: int,
    sc_dst: int,
    lambda_l: np.ndarray,
) -> complex:
    """
    Dyson-style correction for a single directed shortcut (source sc_src -> sc_dst).
    Only outgoing probabilities at sc_src are modified.
    """
    z_arr = np.atleast_1d(z).astype(np.complex128)
    # Base propagator on the ring
    Q_n0_n = get_Q_ring_z(n - n0, z_arr, N, lambda_l)

    k_half = K // 2
    original_neighbors = []
    for r in range(1, k_half + 1):
        original_neighbors.append((sc_src + r) % N)
        original_neighbors.append((sc_src - r) % N)

    defect_targets = original_neighbors + [sc_dst]
    eta_orig = 1.0 / (K + 1) - 1.0 / K
    eta_sc = 1.0 / (K + 1)
    etas = [eta_orig] * len(original_neighbors) + [eta_sc]

    # Solve for S_{n0}(sc_src, z)
    term_bracket = 0j
    for v_idx, v_node in enumerate(defect_targets):
        q_val = get_Q_ring_z(sc_src - v_node, z_arr, N, lambda_l)
        term_bracket += q_val * etas[v_idx]

    denom_src = 1.0 - z_arr * term_bracket
    denom_src = np.where(np.abs(denom_src) < 1e-14, 1e-14, denom_src)

    S_n0_src = get_Q_ring_z(sc_src - n0, z_arr, N, lambda_l) / denom_src

    # S_{n0}(n, z)
    correction = 0j
    for v_idx, v_node in enumerate(defect_targets):
        q_val = get_Q_ring_z(n - v_node, z_arr, N, lambda_l)
        correction += q_val * etas[v_idx]

    out = Q_n0_n + z_arr * correction * S_n0_src
    if np.ndim(z) == 0:
        return out[0]
    return out


def exact_first_absorption_aw(
    graph: GraphData,
    rho: float = 1.0,
    max_steps: int = 2000,
    r: Optional[float] = None,
) -> np.ndarray:
    """
    First-absorption A(t) via analytical propagator + AW inversion (prototype).
    Assumes directed shortcut (source = sc_v -> sc_u).
    """
    N, K = graph.N, graph.K
    lambda_l = get_eigenvalues_ring(N, K)
    sc_src, sc_dst = graph.sc_v, graph.sc_u

    t_vals = np.arange(1, max_steps + 1, dtype=np.int32)
    max_t = int(t_vals.max())
    if r is None:
        r = 10 ** (-4.0 / max_t)
    r = min(r, 0.995)

    # FFT length
    L = 2
    while L <= max_t + 100:
        L *= 2

    k_idx = np.arange(L, dtype=np.float64)
    z_vals = r * np.exp(1j * 2 * np.pi * k_idx / L)

    S_n0_t = get_S_defect_z(graph.target, graph.n0, z_vals, N, K, sc_src, sc_dst, lambda_l)
    S_t_t = get_S_defect_z(graph.target, graph.target, z_vals, N, K, sc_src, sc_dst, lambda_l)
    denom = (1.0 - rho) + rho * S_t_t
    denom = np.where(np.abs(denom) < 1e-14, 1e-14, denom)
    A_z = rho * S_n0_t / denom

    fft_res = np.fft.fft(A_z)
    A_t = np.zeros_like(t_vals, dtype=np.float64)
    for idx, t in enumerate(t_vals):
        A_t[idx] = ((1.0 / L) * (r ** (-t)) * fft_res[t]).real
    return A_t


def exact_first_absorption(
    graph: GraphData,
    rho: float = 1.0,
    max_steps: Optional[int] = None,
) -> np.ndarray:
    """
    Analytical exact first-absorption via AW inversion.
    """
    # FIX: avoid very large horizons; for SWN N=100, 2000 steps suffices.
    if max_steps is None:
        max_steps = 2000
    return exact_first_absorption_aw(graph, rho=rho, max_steps=max_steps)


# -----------------------------
# Exact Master-equation method
# -----------------------------
def exact_first_absorption_numerical(
    graph: GraphData,
    rho: float = 1.0,
    eps_remaining: float = 1e-12,
    max_steps: int = 500_000,
) -> np.ndarray:
    """
    Exact discrete-time first-absorption distribution A(t) via master-equation propagation:
        P_{t+1} = W P_t, with absorption at target after the jump.
    rho=1 -> first passage (perfect absorption).
    """
    N = graph.N
    p = np.zeros(N, dtype=np.float64)
    p[graph.n0] = 1.0

    out: List[float] = []
    remaining = 1.0
    t = 0
    while t < max_steps and remaining > eps_remaining:
        contrib = p[graph.src] * graph.w
        p_next = np.bincount(graph.dst, weights=contrib, minlength=N).astype(
            np.float64, copy=False
        )

        absorb = rho * p_next[graph.target]
        out.append(float(absorb))
        p_next[graph.target] *= (1.0 - rho)

        p = p_next
        remaining = float(p.sum())
        t += 1
    return np.asarray(out, dtype=np.float64)


# -----------------------------
# Peak detection (Fig. 3 caption)
# -----------------------------
def coarsegrain_two_steps(A: np.ndarray) -> np.ndarray:
    """
    For K=2 nearest-neighbour walks, parity causes many trivial micro-peaks.
    Coarse-grain by 2 steps to remove that artifact.
    """
    m = len(A) // 2
    Ac = A[: 2 * m].reshape(m, 2).sum(axis=1)
    if len(A) % 2 == 1:
        Ac = np.concatenate([Ac, [A[-1]]])
    return Ac


def detect_peaks_fig3(
    A: np.ndarray, min_height: float = 1e-7, second_rel_height: float = 0.01
) -> List[Tuple[int, float]]:
    """
    Fig. 3 caption rule:
      mode at time t when A(t-1) < A(t) and A(t) > A(t+1),
      with A(t) > 1e-7.
      If a second mode exists, it must be >= 1% of the height of the highest.
    Returns list [(t_peak, height), ...] with t starting at 1.
    """
    if len(A) < 3:
        return []
    peaks: List[int] = []
    for i in range(1, len(A) - 1):
        if A[i - 1] < A[i] and A[i] > A[i + 1] and A[i] > min_height:
            peaks.append(i)

    if not peaks:
        return []

    heights = np.array([A[i] for i in peaks], dtype=np.float64)
    hmax = float(heights.max())
    good = [peaks[idx] for idx, h in enumerate(heights) if h >= second_rel_height * hmax]
    good.sort()
    return [(i + 1, float(A[i])) for i in good]


def peaks_and_valley(A: np.ndarray) -> Tuple[bool, List[Tuple[int, float]], Optional[int]]:
    peaks = detect_peaks_fig3(A)
    if len(peaks) < 2:
        return False, peaks, None

    (t1, _), (t2, _) = peaks[0], peaks[1]
    # open interval (t1, t2) => times t1+1..t2-1 => indices t1..t2-2
    seg = A[t1 : t2 - 1]
    if seg.size == 0:
        return True, peaks, None
    idx_min = int(np.argmin(seg))
    t_valley = (t1 + idx_min) + 1
    return True, peaks, t_valley


# -----------------------------
# Monte Carlo (vectorized) + joblib
# -----------------------------
def simulate_batch(
    N: int,
    K: int,
    n_walkers: int,
    rho: float,
    seed: int,
    n0_paper: int = 1,
    target_paper: Optional[int] = None,
    shortcut_offset: int = 5,
    return_paths: bool = False,
    n_paths_to_store: int = 0,
    track_crossings: bool = False,
    directed_shortcut: bool = False,
):
    """Vectorized MC for one batch. Returns: fp_times, paths (or None), (sc_u, sc_v), target."""
    graph = build_graph(
        N,
        K,
        n0_paper=n0_paper,
        target_paper=target_paper,
        shortcut_offset=shortcut_offset,
        directed_shortcut=directed_shortcut,
    )
    rng = np.random.default_rng(seed)

    pos = np.full(n_walkers, graph.n0, dtype=np.int16)
    active = np.ones(n_walkers, dtype=bool)
    fp_times = np.full(n_walkers, -1, dtype=np.int32)
    crossings = np.zeros(n_walkers, dtype=np.int16) if track_crossings else None

    paths: Optional[List[List[int]]] = None
    store_mask: Optional[np.ndarray] = None
    if return_paths and n_paths_to_store > 0:
        n_store = min(n_paths_to_store, n_walkers)
        paths = [[int(graph.n0)] for _ in range(n_store)]
        store_mask = np.zeros(n_walkers, dtype=bool)
        store_mask[:n_store] = True

    t = 0
    while active.any():
        idx = np.nonzero(active)[0]
        cur = pos[idx]
        degs = graph.deg[cur].astype(np.float64)
        r = (rng.random(size=idx.size) * degs).astype(np.int16)
        nxt = graph.neigh_pad[cur, r]
        if track_crossings:
            cross_mask = ((cur == graph.sc_u) & (nxt == graph.sc_v)) | ((cur == graph.sc_v) & (nxt == graph.sc_u))
            if cross_mask.any():
                crossings[idx[cross_mask]] += 1
        pos[idx] = nxt
        t += 1

        if paths is not None and store_mask is not None:
            stored_here = idx[store_mask[idx]]
            for j in stored_here:
                paths[int(j)].append(int(pos[j]))

        hit = pos[idx] == graph.target
        if hit.any():
            hit_idx = idx[hit]
            if rho >= 1.0:
                absorbed = hit_idx
            else:
                u = rng.random(size=hit_idx.size)
                absorbed = hit_idx[u < rho]
            fp_times[absorbed] = t
            active[absorbed] = False

    return fp_times, paths, (graph.sc_u, graph.sc_v), graph.target, crossings


def mc_first_passage_times_joblib(
    N: int,
    K: int,
    n_walkers: int,
    rho: float,
    seed: int = 0,
    batch_size: int = 50_000,
    n_jobs: int = -1,
    track_crossings: bool = False,
    directed_shortcut: bool = False,
    shortcut_offset: int = 5,
) -> Tuple[np.ndarray, Optional[np.ndarray]]:
    """
    Parallel MC using joblib (loky processes; spawn-safe under __main__ in scripts).
    """
    n_batches = int(math.ceil(n_walkers / batch_size))
    ss = np.random.SeedSequence(seed)
    child_seeds = ss.spawn(n_batches)

    def _run_batch(i: int, n_b: int):
        s = int(child_seeds[i].generate_state(1, dtype=np.uint64)[0])
        times, _, _, _, crosses = simulate_batch(
            N,
            K,
            n_b,
            rho=rho,
            seed=s,
            return_paths=False,
            track_crossings=track_crossings,
            directed_shortcut=directed_shortcut,
            shortcut_offset=shortcut_offset,
        )
        return times, crosses

    batch_sizes = [batch_size] * n_batches
    batch_sizes[-1] = n_walkers - batch_size * (n_batches - 1)

    if n_jobs == 1:
        outs = [_run_batch(i, nb) for i, nb in enumerate(batch_sizes)]
        times_all = np.concatenate([o[0] for o in outs], axis=0)
        if track_crossings:
            crosses_all = np.concatenate([o[1] for o in outs], axis=0)
            return times_all, crosses_all
        return times_all, None

    try:
        outs = Parallel(n_jobs=n_jobs, backend="loky")(
            delayed(_run_batch)(i, nb) for i, nb in enumerate(batch_sizes)
        )
    except PermissionError as e:
        # Some restricted environments disallow loky semaphore limits; fall back to sequential execution.
        print(f"[mc_first_passage_times_joblib] PermissionError ({e}); falling back to sequential.")
        outs = [_run_batch(i, nb) for i, nb in enumerate(batch_sizes)]

    times_all = np.concatenate([o[0] for o in outs], axis=0)
    if track_crossings:
        crosses_all = np.concatenate([o[1] for o in outs], axis=0)
        return times_all, crosses_all
    return times_all, None


# -----------------------------
# Classification + path analysis
# -----------------------------
def classify_by_valley_and_second_peak(
    fp_times: np.ndarray, *, t_valley: int, t2: int, delta: int
) -> Dict[str, np.ndarray]:
    """
    Four-way split by first-passage time T.

      direct:       T < t_valley - delta
      valley:       |T - t_valley| <= delta
      intermediate: t_valley + delta < T <= t2 + delta   (includes the 2nd-peak window)
      indirect:     T > t2 + delta
    """
    T = fp_times
    return {
        "direct": T < (t_valley - delta),
        "valley": (T >= (t_valley - delta)) & (T <= (t_valley + delta)),
        "intermediate": (T > (t_valley + delta)) & (T <= (t2 + delta)),
        "indirect": T > (t2 + delta),
    }


def shortcut_crossings(path: Sequence[int], u: int, v: int) -> List[int]:
    """Return step indices t (1..T) where edge u<->v is traversed."""
    out: List[int] = []
    for t in range(1, len(path)):
        a, b = path[t - 1], path[t]
        if (a == u and b == v) or (a == v and b == u):
            out.append(t)
    return out


def summarize_paths(paths: List[List[int]], sc_u: int, sc_v: int) -> Dict[str, float]:
    """
    Summary used to answer: do they take the shortcut? do they bounce back?
    """
    n = len(paths)
    if n == 0:
        return {"count": 0.0}
    n_cross = np.array([len(shortcut_crossings(p, sc_u, sc_v)) for p in paths], dtype=np.int32)
    first = np.array(
        [shortcut_crossings(p, sc_u, sc_v)[0] if len(shortcut_crossings(p, sc_u, sc_v)) else -1 for p in paths],
        dtype=np.int32,
    )
    fc = first[first != -1]
    return {
        "count": float(n),
        "frac_no_shortcut": float(np.mean(n_cross == 0)),
        "frac_one_cross": float(np.mean(n_cross == 1)),
        "frac_multi_cross": float(np.mean(n_cross >= 2)),
        "first_cross_t_median": float(np.median(fc)) if fc.size else float("nan"),
        "first_cross_t_p10": float(np.percentile(fc, 10)) if fc.size else float("nan"),
        "first_cross_t_p90": float(np.percentile(fc, 90)) if fc.size else float("nan"),
    }


def collect_representative_paths(
    N: int,
    K: int,
    rho: float,
    t_valley: int,
    t2: int,
    delta: int,
    n_per_class: int = 10,
    seed: int = 1234,
    batch_paths: int = 4000,
    directed_shortcut: bool = False,
    shortcut_offset: int = 5,
) -> Dict[str, List[List[int]]]:
    """
    Collect >= n_per_class full trajectories for each class by running batches with full path storage.
    """
    rng = np.random.default_rng(seed)
    out: Dict[str, List[List[int]]] = {
        "direct": [],
        "valley": [],
        "intermediate": [],
        "indirect": [],
    }

    while min(len(v) for v in out.values()) < n_per_class:
        s = int(rng.integers(0, 2**32 - 1))
        fp, paths, _, _, _ = simulate_batch(
            N,
            K,
            batch_paths,
            rho=rho,
            seed=s,
            return_paths=True,
            n_paths_to_store=batch_paths,
            directed_shortcut=directed_shortcut,
            shortcut_offset=shortcut_offset,
        )
        assert paths is not None
        masks = classify_by_valley_and_second_peak(fp, t_valley=t_valley, t2=t2, delta=delta)

        for cls in ("direct", "valley", "intermediate", "indirect"):
            idx = np.nonzero(masks[cls])[0]
            rng.shuffle(idx)
            for i in idx:
                if len(out[cls]) >= n_per_class:
                    break
                out[cls].append(paths[int(i)])

    return out


# -----------------------------
# Plotting helpers
# -----------------------------
def log_binned_density(times: np.ndarray, bins_per_decade: int = 25) -> Tuple[np.ndarray, np.ndarray]:
    """Logarithmic binning for smooth MC curves."""
    t = times[times > 0].astype(np.float64)
    t_min = max(1.0, float(t.min()))
    t_max = float(t.max())
    decades = math.log10(t_max) - math.log10(t_min)
    n_bins = max(10, int(math.ceil(decades * bins_per_decade)))
    edges = np.logspace(math.log10(t_min), math.log10(t_max), n_bins + 1)
    counts, _ = np.histogram(t, bins=edges)
    widths = np.diff(edges)
    density = counts / counts.sum() / widths
    centers = np.sqrt(edges[:-1] * edges[1:])
    return centers, density


def smooth_series(y: np.ndarray, window: int = 5) -> np.ndarray:
    """Simple moving-average smoother (keeps length)."""
    if window <= 1 or y.size == 0:
        return y
    window = min(window, y.size)
    kernel = np.ones(window, dtype=np.float64) / float(window)
    return np.convolve(y, kernel, mode="same")


def smooth_heatmap(H: np.ndarray, sigma: float = 1.0) -> np.ndarray:
    """Separable Gaussian-like smoothing without extra deps."""
    if sigma <= 0 or H.size == 0:
        return H
    radius = max(1, int(3 * sigma))
    xs = np.arange(-radius, radius + 1, dtype=np.float64)
    kernel = np.exp(-(xs**2) / (2 * sigma * sigma))
    kernel /= kernel.sum()
    # convolve columns then rows
    H1 = np.apply_along_axis(lambda m: np.convolve(m, kernel, mode="same"), 0, H)
    H2 = np.apply_along_axis(lambda m: np.convolve(m, kernel, mode="same"), 1, H1)
    return H2


def plot_distribution(A_exact: np.ndarray, mc_times: np.ndarray, title: str, outpath: str, n_walkers: int = None) -> None:
    t_exact = np.arange(1, len(A_exact) + 1, dtype=np.int32)
    centers, dens = log_binned_density(mc_times)
    dens_smooth = smooth_series(dens, window=7)

    fig, ax = plt.subplots(figsize=(7.2, 4.2), dpi=160)
    ax.plot(t_exact, A_exact, lw=2.0, label="Exact (master eq.)")
    ax.plot(centers, dens_smooth, lw=2.0, ls="--", label="MC (log-binned, smoothed)")
    ax.set_xscale("log")
    ax.set_xlabel("time $t$ (steps, log scale)")
    ax.set_ylabel("first-absorption probability / density")
    if n_walkers is not None:
        ax.text(0.02, 0.95, f"MC walkers: {n_walkers:,}", transform=ax.transAxes, va="top", ha="left", fontsize=9, bbox=dict(facecolor="white", alpha=0.7, edgecolor="none"))
    ax.set_title(title)
    ax.grid(True, which="both", alpha=0.25)
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(outpath)
    plt.close(fig)


def plot_trajectories(
    paths_by_class: Dict[str, List[List[int]]],
    N: int,
    K: int,
    sc_u: int,
    sc_v: int,
    target: int,
    outpath: str,
) -> None:
    colors = {"direct": "tab:blue", "valley": "tab:purple", "intermediate": "tab:green", "indirect": "tab:red"}
    fig, ax = plt.subplots(figsize=(7.2, 4.6), dpi=160)

    # paper-indexing for y-axis
    sc_u_p = sc_u + 1
    sc_v_p = sc_v + 1
    tgt_p = target + 1

    # Draw shortcut as a “bridge” at fixed x ~ 5% of max plotted time
    maxT = max(max(len(p) for p in ps) for ps in paths_by_class.values())
    x0 = 0.05 * maxT
    ax.plot([x0, x0], [sc_u_p, sc_v_p], lw=6, alpha=0.35, color="goldenrod", zorder=5)
    ax.text(x0, 0.5 * (sc_u_p + sc_v_p), "shortcut", va="center", ha="left", fontsize=9, color="saddlebrown", weight="bold")

    ax.axhline(tgt_p, lw=1.5, ls=":", alpha=0.6)
    ax.text(0.99, (tgt_p - 1) / (N - 1), "target", transform=ax.transAxes, ha="right", va="bottom", fontsize=9)

    for cls, paths in paths_by_class.items():
        for p in paths:
            y = np.asarray(p, dtype=np.int32) + 1
            x = np.arange(len(y), dtype=np.int32)
            ax.plot(x, y, lw=1.2, alpha=0.85, color=colors[cls])

    ax.set_xlabel("time $t$")
    ax.set_ylabel("node index (paper: 1..N)")
    ax.set_ylim(1, N)
    ax.set_title(f"Representative trajectories (N={N}, K={K})")
    ax.grid(True, alpha=0.2)
    fig.tight_layout()
    fig.savefig(outpath)
    plt.close(fig)


def plot_trajectories_split(
    paths_by_class: Dict[str, List[List[int]]],
    N: int,
    K: int,
    sc_u: int,
    sc_v: int,
    target: int,
    out_prefix: str,
) -> None:
    colors = {"direct": "tab:blue", "valley": "tab:purple", "intermediate": "tab:green", "indirect": "tab:red"}
    sc_u_p, sc_v_p, tgt_p = sc_u + 1, sc_v + 1, target + 1

    for cls, paths in paths_by_class.items():
        fig, ax = plt.subplots(figsize=(7.2, 4.2), dpi=160)
        maxT = max(len(p) for p in paths) if paths else 1
        x0 = 0.05 * maxT
        ax.plot([x0, x0], [sc_u_p, sc_v_p], lw=6, alpha=0.35, color="goldenrod", zorder=5)
        ax.text(x0, 0.5 * (sc_u_p + sc_v_p), "shortcut", va="center", ha="left", fontsize=8, color="saddlebrown", weight="bold")

        ax.axhline(tgt_p, lw=1.2, ls=":", alpha=0.6, color="gray")
        ax.text(0.99, (tgt_p - 1) / (N - 1), "target", transform=ax.transAxes, ha="right", va="bottom", fontsize=8)

        for p in paths:
            y = np.asarray(p, dtype=np.int32) + 1
            x = np.arange(len(y), dtype=np.int32)
            ax.plot(x, y, lw=1.6, alpha=0.9, color=colors[cls])

        ax.set_xlabel("time $t$")
        ax.set_ylabel("node index (paper: 1..N)")
        ax.set_ylim(1, N)
        ax.set_title(f"{cls.title()} trajectories (N={N}, K={K})")
        ax.grid(True, alpha=0.15)
        fig.tight_layout()
        fig.savefig(f"{out_prefix}_traj_{cls}.png")
        plt.close(fig)


def plot_class_counts(counts: Dict[str, int], total: int, outpath: str, title: str = "Class breakdown") -> None:
    labels = ["direct", "valley", "intermediate", "indirect"]
    vals = [counts.get(k, 0) for k in labels]
    colors_bar = ["tab:blue", "tab:purple", "tab:green", "tab:red"]
    perc = [100.0 * v / total if total > 0 else 0.0 for v in vals]

    fig, ax = plt.subplots(figsize=(6.0, 4.0), dpi=170)
    bars = ax.bar(labels, vals, color=colors_bar, alpha=0.9)
    pad = max(vals) * 0.08 if vals else 1
    ax.set_ylim(0, max(vals) * 1.3 + 1 if vals else 1)
    for b, p, v in zip(bars, perc, vals):
        ax.text(
            b.get_x() + b.get_width() / 2,
            b.get_height() + pad * 0.15,
            f"{v} ({p:.1f}%)",
            ha="center",
            va="bottom",
            fontsize=9,
            color="black",
            weight="bold",
        )
    ax.set_ylabel("count (representative paths)")
    ax.set_title(title)
    fig.tight_layout()
    fig.savefig(outpath)
    plt.close(fig)


def plot_shortcut_usage_bars(usage: Dict[str, Dict[str, float]], outpath: str) -> None:
    labels = ["direct", "valley", "intermediate", "indirect"]
    frac_no = [usage.get(k, {}).get("frac_no", 0.0) for k in labels]
    frac_one = [usage.get(k, {}).get("frac_one", 0.0) for k in labels]
    frac_multi = [usage.get(k, {}).get("frac_multi", 0.0) for k in labels]

    x = np.arange(len(labels))
    width = 0.25

    fig, ax = plt.subplots(figsize=(7.0, 4.2), dpi=170)
    b1 = ax.bar(x - width, frac_no, width, label="no shortcut", color="#7f7f7f")
    b2 = ax.bar(x, frac_one, width, label="one crossing", color="#1f77b4")
    b3 = ax.bar(x + width, frac_multi, width, label="multiple crossings", color="#d62728")

    def annotate(bars, data):
        for bar, val in zip(bars, data):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.01,
                f"{val*100:.1f}%",
                ha="center",
                va="bottom",
                fontsize=8,
            )

    annotate(b1, frac_no)
    annotate(b2, frac_one)
    annotate(b3, frac_multi)

    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("fraction of walkers")
    ax.set_title("Shortcut usage by class (MC ensemble)")
    ax.legend(frameon=False, ncol=3)
    ax.grid(True, axis="y", alpha=0.2)
    fig.tight_layout()
    fig.savefig(outpath)
    plt.close(fig)


def plot_heatmap_class(
    paths: List[List[int]],
    N: int,
    target: int,
    sc_u: int,
    sc_v: int,
    outpath: str,
    cmap: str = "magma",
    norm_by_time: bool = True,
) -> None:
    if not paths:
        return
    # Flatten time/node pairs
    times = np.concatenate([np.arange(len(p), dtype=np.int32) for p in paths])
    nodes = np.concatenate([np.asarray(p, dtype=np.int32) + 1 for p in paths])  # paper indexing

    t_max = int(times.max())
    # Use integer bins for nodes; time bins up to max time
    t_bins = np.arange(0, t_max + 2, 1, dtype=np.int32)
    n_bins = np.arange(1, N + 2, 1, dtype=np.int32)

    H, xedges, yedges = np.histogram2d(times, nodes, bins=[t_bins, n_bins])
    if norm_by_time:
        with np.errstate(invalid="ignore", divide="ignore"):
            row_sums = H.sum(axis=1, keepdims=True)
            H = np.where(row_sums > 0, H / row_sums, 0.0)

    # Smooth to make the heatmap visually continuous
    H = smooth_heatmap(H, sigma=1.0)

    # Clip to 99th percentile to enhance contrast, then apply power norm to boost low signals
    finite_vals = H[np.isfinite(H) & (H > 0)]
    vmax = np.percentile(finite_vals, 99) if finite_vals.size else 1.0
    H_clipped = np.clip(H, 0, vmax)

    fig, ax = plt.subplots(figsize=(7.6, 4.2), dpi=180)
    extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]
    norm = colors.PowerNorm(gamma=0.5, vmin=0, vmax=vmax if vmax > 0 else None)
    im = ax.imshow(
        H_clipped.T,
        aspect="auto",
        origin="lower",
        cmap=cmap,
        extent=extent,
        norm=norm,
        interpolation="bilinear",
    )
    cbar = fig.colorbar(im, ax=ax, pad=0.02)
    cbar.set_label("visit probability" if norm_by_time else "visit count")
    cbar.outline.set_edgecolor("black")
    cbar.outline.set_linewidth(0.8)

    # Overlay target and shortcut endpoints
    tgt_p = target + 1
    ax.axhline(tgt_p, color="cyan", ls="--", lw=1.2, alpha=0.8, label="target")
    x_sc = 0.05 * (xedges[-1] - xedges[0])
    ax.scatter([x_sc, x_sc], [sc_u + 1, sc_v + 1], color="gold", s=40, zorder=6, edgecolor="k", linewidth=0.5, label="shortcut ends")

    ax.set_xlabel("time $t$")
    ax.set_ylabel("node index (paper: 1..N)")
    ax.set_title("Trajectory density heatmap")
    ax.legend(
        loc="upper right",
        frameon=True,
        facecolor="white",
        framealpha=0.9,
        edgecolor="none",
    )
    fig.tight_layout()
    fig.savefig(outpath)
    plt.close(fig)


# -----------------------------
# Scan driver
# -----------------------------
def _compress_even_ranges(vals: List[int], step: int = 2) -> List[Tuple[int, int]]:
    if not vals:
        return []
    vals = sorted(vals)
    out: List[Tuple[int, int]] = []
    s = prev = vals[0]
    for v in vals[1:]:
        if v == prev + step:
            prev = v
        else:
            out.append((s, prev))
            s = prev = v
    out.append((s, prev))
    return out


def scan_bimodality(
    N_min: int = 10,
    N_max: int = 160,
    K_values: Sequence[int] = (2, 4, 6, 8),
    rho: float = 1.0,
    directed_shortcut: bool = False,
    shortcut_offset: int = 5,
    outpath: Optional[str] = None,
) -> None:
    _ensure_output_dirs()
    print(f"Scan (rho={rho}): even N in [{N_min},{N_max}], K in {list(K_values)}")
    results: Dict[int, List[int]] = {}
    details: Dict[int, List[Dict[str, object]]] = {}
    for K in K_values:
        def _check(N: int) -> Optional[int]:
            g = build_graph(N, K, shortcut_offset=shortcut_offset, directed_shortcut=directed_shortcut)
            A = exact_first_absorption(g, rho=rho)
            A_use = coarsegrain_two_steps(A) if K == 2 else A
            bim, _, _ = peaks_and_valley(A_use)
            return N if bim else None

        checked = Parallel(n_jobs=-1)(
            delayed(_check)(N) for N in range(N_min, N_max + 1, 2)
        )
        bimodal_N = [x for x in checked if x is not None]
        results[K] = bimodal_N
        # detailed per-N info (recomputed for clarity)
        det_list: List[Dict[str, object]] = []
        for N in range(N_min, N_max + 1, 2):
            g = build_graph(N, K, shortcut_offset=shortcut_offset, directed_shortcut=directed_shortcut)
            A = exact_first_absorption(g, rho=rho)
            A_use = coarsegrain_two_steps(A) if K == 2 else A
            bim, peaks, t_val = peaks_and_valley(A_use)
            det_list.append({"N": N, "bimodal": bool(bim), "peaks": peaks, "t_valley": t_val})
        details[K] = det_list

        ranges = _compress_even_ranges(bimodal_N, step=2)
        if not ranges:
            print(f"K={K}: no bimodality detected")
        else:
            pretty = ", ".join([f"{a}" if a == b else f"{a}..{b}" for a, b in ranges])
            print(f"K={K}: bimodal N ranges: {pretty}  (count={len(bimodal_N)})")

    if outpath is not None:
        plot_bimodality_map(results, outpath=outpath, N_min=N_min, N_max=N_max)
    # Save raw scan data
    scan_raw = {
        "N_min": N_min,
        "N_max": N_max,
        "rho": rho,
        "directed_shortcut": directed_shortcut,
        "shortcut_offset": shortcut_offset,
        "results": results,
        "details": details,
    }
    with (DATA_DIR / "bimodality_scan.json").open("w", encoding="utf-8") as f:
        json.dump(scan_raw, f, indent=2)

# -----------------------------
# Bimodality map plot
# -----------------------------
def plot_bimodality_map(results: Dict[int, List[int]], outpath: str, N_min: int, N_max: int) -> None:
    fig, ax = plt.subplots(figsize=(7.5, 3.0), dpi=170)
    for K, Ns in sorted(results.items()):
        if Ns:
            ax.scatter(Ns, [K] * len(Ns), label=f"K={K}", s=16)
    ax.set_xlim(N_min - 2, N_max + 2)
    ax.set_xlabel("N (even)")
    ax.set_ylabel("K")
    ax.set_title("Bimodality presence by (N, K)")
    ax.grid(True, alpha=0.3)
    ax.legend(frameon=False, ncol=len(results))
    fig.tight_layout()
    fig.savefig(outpath)
    plt.close(fig)


# -----------------------------
# Example single-case runner
# -----------------------------
def run_case(
    N: int,
    K: int,
    rho: float = 1.0,
    n_walkers: int = 200_000,
    seed: int = 0,
    delta_frac: float = 0.05,
    out_prefix: str = "valley",
    mc_n_jobs: int = -1,
    directed_shortcut: bool = False,
    shortcut_offset: int = 5,
) -> None:
    _ensure_output_dirs()
    g = build_graph(N, K, shortcut_offset=shortcut_offset, directed_shortcut=directed_shortcut)
    A = exact_first_absorption(g, rho=rho)
    A_use = coarsegrain_two_steps(A) if K == 2 else A

    bim, peaks, t_valley = peaks_and_valley(A_use)
    print(f"(N={N}, K={K}, rho={rho}) peaks={peaks}")
    if not bim or len(peaks) < 2:
        print("Not bimodal under Fig.3 rules; skipping classification.")
        return

    (t1, _), (t2, _) = peaks[0], peaks[1]
    delta = max(1, int(delta_frac * (t2 - t1)))
    print(f"t2={t2}, delta={delta}")

    mc_times, mc_cross = mc_first_passage_times_joblib(
        N,
        K,
        n_walkers,
        rho=rho,
        seed=seed,
        batch_size=50_000,
        n_jobs=mc_n_jobs,
        track_crossings=True,
        directed_shortcut=directed_shortcut,
        shortcut_offset=shortcut_offset,
    )

    # Classify full MC ensemble for true proportions
    if t_valley is None:
        raise RuntimeError("Expected t_valley for bimodal case.")
    t_valley_i = int(t_valley)
    mc_masks = classify_by_valley_and_second_peak(mc_times, t_valley=t_valley_i, t2=int(t2), delta=delta)
    mc_counts = {cls: int(np.sum(mask)) for cls, mask in mc_masks.items()}
    plot_class_counts(
        mc_counts,
        total=n_walkers,
        outpath=str(FIGURES_DIR / f"{out_prefix}_class_counts_mc.pdf"),
        title="Class breakdown (MC walkers)",
    )

    # Full-MC shortcut usage by class
    usage_stats: Dict[str, Dict[str, float]] = {}
    if mc_cross is not None:
        for cls, mask in mc_masks.items():
            cross_cls = mc_cross[mask]
            total_cls = cross_cls.size
            if total_cls == 0:
                stats = {"frac_no": 0.0, "frac_one": 0.0, "frac_multi": 0.0}
            else:
                stats = {
                    "frac_no": float(np.mean(cross_cls == 0)),
                    "frac_one": float(np.mean(cross_cls == 1)),
                    "frac_multi": float(np.mean(cross_cls >= 2)),
                }
            usage_stats[cls] = stats
            print(f"{cls:8s} shortcut usage (MC): {stats}")
        plot_shortcut_usage_bars(usage_stats, outpath=str(FIGURES_DIR / f"{out_prefix}_shortcut_usage_mc.pdf"))

    centers_save, dens_save = log_binned_density(mc_times)
    dens_smooth_save = smooth_series(dens_save, window=7)

    plot_distribution(
        A_use,
        mc_times,
        title=f"N={N}, K={K}, rho={rho}",
        outpath=str(FIGURES_DIR / f"{out_prefix}_dist.pdf"),
        n_walkers=n_walkers,
    )

    # Dense heatmaps from full-path MC sample (no trajectory overlays)
    fp_full, paths_full, _, _, _ = simulate_batch(
        N,
        K,
        n_walkers,
        rho=rho,
        seed=seed + 123,
        return_paths=True,
        n_paths_to_store=min(n_walkers, 50_000),
        directed_shortcut=directed_shortcut,
        shortcut_offset=shortcut_offset,
    )
    masks_full = classify_by_valley_and_second_peak(fp_full, t_valley=t_valley_i, t2=int(t2), delta=delta)
    if paths_full is not None:
        n_store = len(paths_full)
        paths_by_class_full = {}
        for cls, mask in masks_full.items():
            idx = np.nonzero(mask[:n_store])[0]
            paths_by_class_full[cls] = [paths_full[int(i)] for i in idx]
            plot_heatmap_class(
                paths_by_class_full[cls],
                N=N,
                target=g.target,
                sc_u=g.sc_u,
                sc_v=g.sc_v,
                outpath=str(FIGURES_DIR / f"{out_prefix}_heat_{cls}.pdf"),
                cmap="magma",
                norm_by_time=True,
        )

    # Save raw metrics
    metrics = {
        "N": N,
        "K": K,
        "rho": rho,
        "peaks": peaks,
        "t2": int(t2),
        "t_valley": t_valley,
        "delta": delta,
        "mc_counts": mc_counts,
        "shortcut_usage": usage_stats,
    }
    with (DATA_DIR / f"{out_prefix}_metrics.json").open("w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    np.savez_compressed(
        DATA_DIR / f"{out_prefix}_curves.npz",
        t_exact=np.arange(1, len(A_use) + 1),
        A_exact=A_use,
        mc_centers=centers_save,
        mc_density_smooth=dens_smooth_save,
    )

    print(
        f"Saved: figures/{out_prefix}_dist.pdf, figures/{out_prefix}_heat_[direct|valley|intermediate|indirect].pdf, "
        f"figures/{out_prefix}_class_counts_mc.pdf, figures/{out_prefix}_shortcut_usage_mc.pdf, "
        f"data/{out_prefix}_metrics.json, data/{out_prefix}_curves.npz"
    )


if __name__ == "__main__":
    # 1) Scan requested ranges
    scan_bimodality(
        N_min=10,
        N_max=160,
        K_values=(2, 4, 6, 8),
        rho=1.0,
        directed_shortcut=True,
        shortcut_offset=5,
        outpath=str(FIGURES_DIR / "bimodality_map.pdf"),
    )

    # 2) A representative “Valley regime” case (edit as needed)
    run_case(
        N=100,
        K=6,
        rho=1.0,
        n_walkers=2_000_000,
        seed=0,
        out_prefix="N100K6",
        mc_n_jobs=-1,
        directed_shortcut=True,
        shortcut_offset=5,
    )
