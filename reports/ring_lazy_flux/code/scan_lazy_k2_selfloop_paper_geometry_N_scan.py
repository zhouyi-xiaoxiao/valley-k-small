#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import numpy as np

from lazy_ring_flux_bimodality import bimodality_macro, bimodality_paper, fpt_pmf_flux_ring


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=(
            "Scan N for the k=1 (K=2) lazy ring selfloop-shortcut model under a paper-like geometry:\n"
            "  start=n0, target=floor(N/2), u=n0+u_offset, v=target+v_offset,\n"
            "  p = beta*(1-q) taken from the self-loop at u.\n"
            "Records paper/macro bimodality and the dominant peak times."
        )
    )
    p.add_argument("--N-min", type=int, default=10)
    p.add_argument("--N-max", type=int, default=200)
    p.add_argument("--q", type=float, default=2.0 / 3.0)
    p.add_argument("--beta", type=float, default=0.02)
    p.add_argument("--start", type=int, default=1)
    p.add_argument("--u-offset", type=int, default=5)
    p.add_argument("--v-offset", type=int, default=1)
    p.add_argument("--Tmax", type=int, default=200_000)
    p.add_argument("--eps-surv", type=float, default=1e-14)
    p.add_argument("--thresh", type=float, default=1e-7)
    p.add_argument("--second-frac", type=float, default=0.01)
    p.add_argument("--time-ratio", type=float, default=10.0)
    return p.parse_args()


def top2_by_height(peaks: tuple[tuple[int, float], ...]) -> list[tuple[int, float]]:
    top2 = sorted(peaks, key=lambda x: -x[1])[:2]
    return sorted(top2, key=lambda x: x[0])


def valley_ratio(f: np.ndarray, *, t1: int, t2: int, hmin: float) -> float:
    if t2 - t1 < 2:
        return float("nan")
    interior = f[t1 : (t2 - 1)]
    if interior.size == 0:
        return float("nan")
    return float(np.min(interior)) / float(hmin)


def main() -> None:
    args = parse_args()
    N_min = int(args.N_min)
    N_max = int(args.N_max)
    if N_min < 3 or N_max < N_min:
        raise ValueError("Need 3 <= N_min <= N_max.")

    q = float(args.q)
    beta = float(args.beta)
    p_sc = beta * (1.0 - q)
    if p_sc < 0.0 or p_sc > (1.0 - q) + 1e-15:
        raise ValueError("beta yields p outside [0, 1-q].")

    outdir = REPO_ROOT / "build" / "lazy_k2_selfloop_paper_geometry"
    outdir.mkdir(parents=True, exist_ok=True)
    csv_path = outdir / f"scan_selfloop_paper_geometry_N{N_min}_{N_max}_beta{beta:.6g}.csv"
    meta_path = outdir / f"scan_selfloop_paper_geometry_N{N_min}_{N_max}_beta{beta:.6g}_meta.txt"

    meta_path.write_text(
        "\n".join(
            [
                "k=1 (K=2) lazy ring selfloop-shortcut (p from self-loop at u)",
                "paper-like geometry per N: target=floor(N/2), u=n0+u_offset, v=target+v_offset",
                f"N_range = [{N_min}, {N_max}]",
                f"q = {q}",
                f"beta = {beta}",
                f"p = beta*(1-q) = {p_sc}",
                f"start = {int(args.start)}",
                f"u_offset = {int(args.u_offset)}",
                f"v_offset = {int(args.v_offset)}",
                f"Tmax = {int(args.Tmax)}",
                f"eps_surv = {float(args.eps_surv)}",
                f"peak criterion: thresh={float(args.thresh)}, second_frac={float(args.second_frac)}, time_ratio={float(args.time_ratio)}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    rows: list[dict[str, object]] = []
    paper_cnt = 0
    macro_cnt = 0

    for N in range(N_min, N_max + 1):
        start = int(args.start) % N
        target = (N // 2) % N
        u = (start + int(args.u_offset)) % N
        v = (target + int(args.v_offset)) % N

        f, surv = fpt_pmf_flux_ring(
            N,
            q,
            start,
            target,
            model="selfloop",
            u=u,
            v=v,
            p=p_sc,
            Tmax=int(args.Tmax),
            eps_surv=float(args.eps_surv),
        )

        paper_ok, peaks = bimodality_paper(f, thresh=float(args.thresh), second_frac=float(args.second_frac))
        macro_ok, _ = bimodality_macro(
            f,
            time_ratio=float(args.time_ratio),
            thresh=float(args.thresh),
            second_frac=float(args.second_frac),
        )

        t1 = None
        t2 = None
        h1 = None
        h2 = None
        vratio = None
        if len(peaks) >= 2:
            (t1, h1), (t2, h2) = top2_by_height(peaks)
            hmin = float(min(h1, h2))
            vratio = valley_ratio(f, t1=int(t1), t2=int(t2), hmin=hmin)

        paper_cnt += int(bool(paper_ok))
        macro_cnt += int(bool(macro_ok))

        rows.append(
            {
                "N": int(N),
                "start": int(start),
                "target": int(target),
                "u": int(u),
                "v": int(v),
                "q": float(q),
                "beta": float(beta),
                "p": float(p_sc),
                "paper": int(bool(paper_ok)),
                "macro": int(bool(macro_ok)),
                "t1": "" if t1 is None else int(t1),
                "t2": "" if t2 is None else int(t2),
                "h1": "" if h1 is None else float(h1),
                "h2": "" if h2 is None else float(h2),
                "valley_ratio": "" if vratio is None else float(vratio),
                "steps": int(len(f)),
                "surv": float(surv),
                "mass": float(f.sum()),
            }
        )

    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        for r in rows:
            w.writerow(r)

    print(f"wrote {csv_path}")
    print(f"paper_bimodal_count={paper_cnt} macro_bimodal_count={macro_cnt} over N={N_min}..{N_max}")


if __name__ == "__main__":
    main()
