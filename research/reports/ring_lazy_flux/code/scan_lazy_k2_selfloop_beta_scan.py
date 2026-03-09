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
            "Scan shortcut probability scale beta for the k=1 (K=2) lazy ring selfloop-shortcut model.\n"
            "Uses paper-like geometry: start=n0, target=floor(N/2), u=n0+u_offset, v=target+v_offset.\n"
            "Shortcut probability is p = beta*(1-q), taken from the self-loop at u."
        )
    )
    p.add_argument("--N", type=int, default=100)
    p.add_argument("--q", type=float, default=2.0 / 3.0)
    p.add_argument("--start", type=int, default=1)
    p.add_argument("--u-offset", type=int, default=5)
    p.add_argument("--v-offset", type=int, default=1)
    p.add_argument(
        "--betas",
        type=str,
        default="0,0.001,0.002,0.005,0.01,0.02,0.05,0.1,0.2,0.5,1.0",
        help="comma-separated beta values (p = beta*(1-q))",
    )
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
    N = int(args.N)
    if N < 3:
        raise ValueError("N must be >= 3.")

    q = float(args.q)
    start = int(args.start) % N
    target = (N // 2) % N
    u = (start + int(args.u_offset)) % N
    v = (target + int(args.v_offset)) % N

    betas = [float(x.strip()) for x in str(args.betas).split(",") if x.strip() != ""]
    if len(betas) == 0:
        raise ValueError("No betas provided.")

    outdir = REPO_ROOT / "build" / "lazy_k2_selfloop_paper_geometry"
    outdir.mkdir(parents=True, exist_ok=True)
    csv_path = outdir / f"beta_scan_N{N}_q{q:.6g}_uoff{int(args.u_offset)}_voff{int(args.v_offset)}.csv"
    meta_path = outdir / f"beta_scan_N{N}_meta.txt"

    meta_path.write_text(
        "\n".join(
            [
                "k=1 (K=2) lazy ring selfloop-shortcut (p from self-loop at u)",
                f"N = {N}",
                f"q = {q}",
                f"start = {int(args.start)}",
                f"target = floor(N/2) = {target}",
                f"u = start+u_offset = {u}",
                f"v = target+v_offset = {v}",
                f"Tmax = {int(args.Tmax)}",
                f"eps_surv = {float(args.eps_surv)}",
                f"peak criterion: thresh={float(args.thresh)}, second_frac={float(args.second_frac)}, time_ratio={float(args.time_ratio)}",
                f"betas = {betas}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    rows: list[dict[str, object]] = []
    for beta in betas:
        p_sc = beta * (1.0 - q)
        if p_sc < -1e-15 or p_sc > (1.0 - q) + 1e-15:
            continue

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

        rows.append(
            {
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

    if len(rows) == 0:
        raise RuntimeError("No valid beta rows produced.")

    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        for r in rows:
            w.writerow(r)

    print(f"wrote {csv_path}")


if __name__ == "__main__":
    main()
