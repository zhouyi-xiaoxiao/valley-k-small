#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import numpy as np

from lazy_ring_aw_chebyshev import AWParams, chebyshev_T_all, chebyshev_U_n, choose_aw_params, sigma_of_z


@dataclass(frozen=True)
class ScanConfig:
    N_min: int
    N_max: int
    q: float
    beta: float
    start: int
    t_factor: float
    oversample: int
    r_pow10: float
    thresh: float
    second_frac: float
    time_ratio: float


def parse_args() -> ScanConfig:
    p = argparse.ArgumentParser(
        description=(
            "Full table scan for k=1 (K=2) lazy ring with directed shortcut u=n0 -> v=target "
            "(p taken from self-loop). Computes f(t) by AW inversion of the Chebyshev closed form."
        )
    )
    p.add_argument("--N-min", type=int, default=4)
    p.add_argument("--N-max", type=int, default=60)
    p.add_argument("--q", type=float, default=2.0 / 3.0, help="equal-prob baseline is 2/3 (stay/left/right each 1/3)")
    p.add_argument("--beta", type=float, default=0.02, help="p = beta*(1-q)")
    p.add_argument("--start", type=int, default=1)
    p.add_argument("--t-factor", type=float, default=4.0, help="compute up to t_max = ceil(t_factor * N^2)")
    p.add_argument("--oversample", type=int, default=4, help="AW m ~= oversample*(t_max+1) rounded to power-of-2")
    p.add_argument("--r-pow10", type=float, default=18.0, help="choose r so that r^m = 10^(-r_pow10)")
    p.add_argument("--thresh", type=float, default=1e-7, help="peak threshold h_min")
    p.add_argument("--second-frac", type=float, default=0.01, help="second peak height fraction vs highest peak")
    p.add_argument("--time-ratio", type=float, default=10.0, help="macro separation: require t2/t1 >= time_ratio")
    args = p.parse_args()
    return ScanConfig(
        N_min=int(args.N_min),
        N_max=int(args.N_max),
        q=float(args.q),
        beta=float(args.beta),
        start=int(args.start),
        t_factor=float(args.t_factor),
        oversample=int(args.oversample),
        r_pow10=float(args.r_pow10),
        thresh=float(args.thresh),
        second_frac=float(args.second_frac),
        time_ratio=float(args.time_ratio),
    )


def strict_local_modes(f: np.ndarray, *, thresh: float) -> list[tuple[int, float]]:
    modes: list[tuple[int, float]] = []
    T = int(f.size)
    for i in range(T):
        left = float(f[i - 1]) if i - 1 >= 0 else 0.0
        right = float(f[i + 1]) if i + 1 < T else 0.0
        fi = float(f[i])
        if fi > left and fi > right and fi >= thresh:
            modes.append((i + 1, fi))
    return modes


@dataclass(frozen=True)
class PeakSummary:
    n_modes: int
    paper_bimodal: bool
    macro_bimodal: bool
    t1: Optional[int]
    t2: Optional[int]
    h1: Optional[float]
    h2: Optional[float]


def summarize_peaks(
    f: np.ndarray, *, thresh: float, second_frac: float, time_ratio: float
) -> PeakSummary:
    modes = strict_local_modes(f, thresh=thresh)
    if len(modes) < 2:
        return PeakSummary(
            n_modes=len(modes),
            paper_bimodal=False,
            macro_bimodal=False,
            t1=None,
            t2=None,
            h1=None,
            h2=None,
        )
    top2 = sorted(modes, key=lambda x: -x[1])[:2]
    (t_a, h_a), (t_b, h_b) = top2
    hmax = max(h_a, h_b)
    hmin = min(h_a, h_b)
    paper = hmin >= second_frac * hmax
    t1, t2 = sorted([t_a, t_b])
    macro = bool(paper and (t2 / t1 >= time_ratio))
    # record heights aligned with t1,t2
    if t_a == t1:
        h1, h2 = h_a, h_b
    else:
        h1, h2 = h_b, h_a
    return PeakSummary(
        n_modes=len(modes),
        paper_bimodal=paper,
        macro_bimodal=macro,
        t1=int(t1),
        t2=int(t2),
        h1=float(h1),
        h2=float(h2),
    )


def aw_invert_batched(Fz: np.ndarray, *, r: float) -> np.ndarray:
    """
    Batched AW inversion:
      Fz has shape (B, m) where Fz[b,k] = F(r*exp(2π i k/m)).
    Returns a[b,t] for t=0..m-1.
    """
    m = int(Fz.shape[1])
    fft = np.fft.fft(Fz, axis=1) / float(m)
    t = np.arange(m, dtype=np.float64)
    scale = (r ** (-t)).astype(np.float64, copy=False)
    return fft * scale[None, :]


def fpt_genfun_cheb_u_start_v_target_batched(
    z: np.ndarray, *, N: int, q: float, p: float, distances: list[int]
) -> np.ndarray:
    """
    Specialization of Eq. (F_cheb_closed) for the scan setting:
      start=n0, u=start, v=target.
    The dependence on the endpoint is only through the ring distance d=dist(start,target).

    Returns:
      Fz[d_index, k] = \\tilde F(z_k) for each requested distance.
    """
    z = np.asarray(z, dtype=np.complex128)
    sig = sigma_of_z(z, q)

    T = chebyshev_T_all(sig, N)
    U_Nm1 = chebyshev_U_n(sig, N - 1)
    C = (q * z) * ((sig * sig) - 1.0) * U_Nm1

    N0 = T[0] + T[N]
    Nd_list = [(T[d] + T[N - d]) for d in distances]
    Nd = np.stack(Nd_list, axis=0)

    # With u=start and v=target:
    #   F = (Nd*C - z p (Nd^2 - N0^2)) / (N0*C - z p (Nd^2 - N0^2)).
    S = (z * p)[None, :] * (Nd * Nd - (N0[None, :] * N0[None, :]))
    num = Nd * C[None, :] - S
    den = (N0[None, :] * C[None, :]) - S
    den = np.where(np.abs(den) < 1e-30, 1e-30 + 0j, den)
    return num / den


def write_longtable_tex(rows: list[dict[str, str]], *, outpath: Path, caption: str, label: str) -> None:
    header = (
        "\\begin{longtable}{rrrrrrr}\n"
        f"\\caption{{{caption}}}\\\\\n"
        f"\\label{{{label}}}\\\\\n"
        "\\toprule\n"
        "$N$ & target & $d$ & paper & macro & $t_1$ & $t_2$\\\\\n"
        "\\midrule\n"
        "\\endfirsthead\n"
        "\\toprule\n"
        "$N$ & target & $d$ & paper & macro & $t_1$ & $t_2$\\\\\n"
        "\\midrule\n"
        "\\endhead\n"
        "\\bottomrule\n"
        "\\endfoot\n"
    )
    lines = [header]
    for r in rows:
        lines.append(
            f"{r['N']} & {r['target']} & {r['d']} & {r['paper']} & {r['macro']} & {r['t1']} & {r['t2']}\\\\\n"
        )
    lines.append("\\end{longtable}\n")
    outpath.parent.mkdir(parents=True, exist_ok=True)
    outpath.write_text("".join(lines), encoding="utf-8")


def main() -> None:
    cfg = parse_args()
    if cfg.N_min < 3 or cfg.N_max < cfg.N_min:
        raise ValueError("Need 3 <= N_min <= N_max.")
    if not (0.0 < cfg.q < 1.0):
        raise ValueError("q must be in (0,1).")
    if cfg.oversample < 2:
        raise ValueError("oversample must be >= 2.")

    p_sc = cfg.beta * (1.0 - cfg.q)
    if p_sc < 0.0 or p_sc > (1.0 - cfg.q) + 1e-15:
        raise ValueError("beta yields p outside [0,1-q].")

    outdir = REPO_ROOT / "build" / "lazy_k2_aw_scan"
    outdir.mkdir(parents=True, exist_ok=True)
    csv_path = outdir / "lazy_K2_equalprob_full_scan.csv"
    meta_path = outdir / "lazy_K2_equalprob_full_scan_meta.txt"
    tex_path_cn = REPO_ROOT / "tables" / "lazy_K2_equalprob_full_scan_table_cn.tex"
    tex_path_en = REPO_ROOT / "tables" / "lazy_K2_equalprob_full_scan_table_en.tex"

    meta_path.write_text(
        "\n".join(
            [
                "k=1 (K=2) lazy ring + directed shortcut (u=n0 -> v=target, p from self-loop)",
                f"N_range = [{cfg.N_min}, {cfg.N_max}]",
                f"q = {cfg.q}",
                f"beta = {cfg.beta}",
                f"p = beta*(1-q) = {p_sc}",
                f"start n0 = {cfg.start}",
                f"t_max(N) = ceil({cfg.t_factor} * N^2)",
                f"AW params: oversample={cfg.oversample}, r_pow10={cfg.r_pow10} (so r^m = 10^(-r_pow10))",
                f"peak criterion: thresh={cfg.thresh}, second_frac={cfg.second_frac}, time_ratio={cfg.time_ratio}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    csv_rows: list[dict[str, str]] = []
    tex_rows: list[dict[str, str]] = []

    for N in range(cfg.N_min, cfg.N_max + 1):
        start = cfg.start % N
        t_max = int(np.ceil(cfg.t_factor * (N * N)))
        aw_params: AWParams = choose_aw_params(t_max, oversample=cfg.oversample, r_pow10=cfg.r_pow10)
        k = np.arange(aw_params.m, dtype=np.float64)
        z = aw_params.r * np.exp(1j * 2.0 * np.pi * k / float(aw_params.m))

        # Unique distances (reflection symmetry around the start node)
        distances = list(range(1, int(N // 2) + 1))
        Fz = fpt_genfun_cheb_u_start_v_target_batched(z, N=N, q=cfg.q, p=p_sc, distances=distances)
        a = aw_invert_batched(Fz, r=aw_params.r)
        f = a[:, 1 : (t_max + 1)].real.astype(np.float64, copy=False)
        f = np.maximum(f, 0.0)

        for i, d in enumerate(distances):
            summ = summarize_peaks(f[i], thresh=cfg.thresh, second_frac=cfg.second_frac, time_ratio=cfg.time_ratio)
            targets = [(start + d) % N]
            t_minus = (start - d) % N
            if t_minus not in targets:
                targets.append(t_minus)
            targets = sorted(targets)

            for target in targets:
                row = {
                    "N": str(N),
                    "start": str(start),
                    "target": str(target),
                    "d": str(d),
                    "t_max": str(t_max),
                    "m": str(aw_params.m),
                    "r": f"{aw_params.r:.17g}",
                    "p": f"{p_sc:.17g}",
                    "thresh": f"{cfg.thresh:.17g}",
                    "n_modes": str(summ.n_modes),
                    "paper": "1" if summ.paper_bimodal else "0",
                    "macro": "1" if summ.macro_bimodal else "0",
                    "t1": "" if summ.t1 is None else str(summ.t1),
                    "t2": "" if summ.t2 is None else str(summ.t2),
                    "h1": "" if summ.h1 is None else f"{summ.h1:.17g}",
                    "h2": "" if summ.h2 is None else f"{summ.h2:.17g}",
                }
                csv_rows.append(row)

                # TeX table keeps only the core columns.
                tex_rows.append(
                    {
                        "N": row["N"],
                        "target": row["target"],
                        "d": row["d"],
                        "paper": row["paper"],
                        "macro": row["macro"],
                        "t1": row["t1"] if row["t1"] else "--",
                        "t2": row["t2"] if row["t2"] else "--",
                    }
                )

    # Write CSV
    with csv_path.open("w", newline="", encoding="utf-8") as fcsv:
        fieldnames = list(csv_rows[0].keys()) if csv_rows else []
        w = csv.DictWriter(fcsv, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(csv_rows)

    # Write LaTeX longtable (appendix)
    write_longtable_tex(
        tex_rows,
        outpath=tex_path_cn,
        caption=(
            "完整扫描表（等概率基准 $q=2/3$，取 $\\beta=0.02$ 使 $p=0.006666\\ldots$，"
            "起点 $n_0=1$，shortcut 取 $u=n_0\\to v=\\mathrm{target}$）。"
            "paper/macro 为 0/1；$d$ 为 $n_0$ 到终点的环距离。"
        ),
        label="tab:fullscan-cn",
    )
    write_longtable_tex(
        tex_rows,
        outpath=tex_path_en,
        caption=(
            "Full scan table (equal-prob baseline $q=2/3$, $\\beta=0.02$ so $p=0.006666\\ldots$, "
            "start $n_0=1$, shortcut $u=n_0\\to v=\\mathrm{target}$). "
            "paper/macro are 0/1; $d$ is the ring distance from $n_0$."
        ),
        label="tab:fullscan-en",
    )

    print(f"wrote {csv_path}")
    print(f"wrote {meta_path}")
    print(f"wrote {tex_path_cn}")
    print(f"wrote {tex_path_en}")


if __name__ == "__main__":
    main()
