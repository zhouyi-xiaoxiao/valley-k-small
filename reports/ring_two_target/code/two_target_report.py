#!/usr/bin/env python3
"""Generate figures/data for the two-target lazy ring report."""
from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List

import numpy as np


@dataclass(frozen=True)
class CaseConfig:
    name: str
    N: int
    K: int
    q: float
    drift: float
    beta: float
    start: int
    target1: int
    target2: int
    src: int | None
    dst: int | None
    max_steps: int
    eps_surv: float


@dataclass(frozen=True)
class PeakInfo:
    t: int
    height: float


def _roll(p: np.ndarray, shift: int) -> np.ndarray:
    return np.roll(p, shift)


def step_lazy_ring(
    p: np.ndarray,
    *,
    K: int,
    q: float,
    drift: float,
) -> np.ndarray:
    if K == 2:
        p_plus = q * (1.0 + drift) / 2.0
        p_minus = q * (1.0 - drift) / 2.0
        p_next = (1.0 - q) * p
        p_next = p_next + p_plus * _roll(p, 1) + p_minus * _roll(p, -1)
        return p_next
    if K == 4:
        p_plus = q * (1.0 + drift) / 2.0
        p_minus = q * (1.0 - drift) / 2.0
        p_next = (1.0 - q) * p
        p_next = p_next + (p_plus / 2.0) * (_roll(p, 1) + _roll(p, 2))
        p_next = p_next + (p_minus / 2.0) * (_roll(p, -1) + _roll(p, -2))
        return p_next
    raise ValueError(f"Unsupported K={K} (use 2 or 4).")


def apply_shortcut(
    p: np.ndarray,
    p_next: np.ndarray,
    *,
    q: float,
    beta: float,
    src: int | None,
    dst: int | None,
) -> np.ndarray:
    if beta <= 0 or src is None or dst is None:
        return p_next
    p_sc = beta * (1.0 - q)
    if p_sc <= 0:
        return p_next
    src = int(src)
    dst = int(dst)
    mass = p[src]
    if mass == 0:
        return p_next
    # Move probability mass from self-loop at src to shortcut dst.
    p_next[src] -= p_sc * mass
    p_next[dst] += p_sc * mass
    return p_next


def fpt_two_targets(
    cfg: CaseConfig,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    N = cfg.N
    p = np.zeros(N, dtype=float)
    p[cfg.start % N] = 1.0

    f_total: List[float] = [0.0]
    f_t1: List[float] = [0.0]
    f_t2: List[float] = [0.0]
    surv: List[float] = [1.0]

    t1 = cfg.target1 % N
    t2 = cfg.target2 % N

    for _t in range(1, cfg.max_steps + 1):
        p_next = step_lazy_ring(p, K=cfg.K, q=cfg.q, drift=cfg.drift)
        p_next = apply_shortcut(
            p,
            p_next,
            q=cfg.q,
            beta=cfg.beta,
            src=cfg.src,
            dst=cfg.dst,
        )

        hit1 = p_next[t1]
        hit2 = p_next[t2]
        hit_total = hit1 + hit2

        f_total.append(float(hit_total))
        f_t1.append(float(hit1))
        f_t2.append(float(hit2))

        # Absorb at both targets
        p_next[t1] = 0.0
        p_next[t2] = 0.0
        p = p_next

        s = float(p.sum())
        surv.append(s)
        if s < cfg.eps_surv:
            break

    return (
        np.asarray(f_total, dtype=float),
        np.asarray(f_t1, dtype=float),
        np.asarray(f_t2, dtype=float),
        np.asarray(surv, dtype=float),
    )


def detect_peaks(f: np.ndarray, *, h_min: float = 1e-12) -> List[PeakInfo]:
    peaks: List[PeakInfo] = []
    if f.size < 3:
        return peaks
    for t in range(1, f.size - 1):
        if f[t] >= h_min and f[t] > f[t - 1] and f[t] > f[t + 1]:
            peaks.append(PeakInfo(t=t, height=float(f[t])))
    return peaks


def peak_metrics(peaks: List[PeakInfo]) -> dict:
    if len(peaks) == 0:
        return {
            "n_peaks": 0,
            "t1": None,
            "h1": None,
            "t2": None,
            "h2": None,
            "h2_over_h1": None,
            "macro": False,
            "paper": False,
        }
    max_h = max(p.height for p in peaks)
    valid = [p for p in peaks if p.height >= 0.01 * max_h]
    valid_sorted = sorted(valid, key=lambda p: p.t)
    paper = len(valid_sorted) >= 2
    t1 = valid_sorted[0] if valid_sorted else None
    t2 = valid_sorted[-1] if len(valid_sorted) >= 2 else None
    h2_over_h1 = None
    macro = False
    if t1 is not None and t2 is not None and t1.height > 0:
        h2_over_h1 = t2.height / t1.height
        macro = t1.t > 0 and (t2.t / t1.t >= 10.0)
    return {
        "n_peaks": len(peaks),
        "t1": t1.t if t1 else None,
        "h1": t1.height if t1 else None,
        "t2": t2.t if t2 else None,
        "h2": t2.height if t2 else None,
        "h2_over_h1": h2_over_h1,
        "macro": macro,
        "paper": paper,
    }


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def save_series_csv(path: Path, f: np.ndarray, f1: np.ndarray, f2: np.ndarray, surv: np.ndarray) -> None:
    with path.open("w", newline="") as f_out:
        writer = csv.writer(f_out)
        writer.writerow(["t", "f_total", "f_target1", "f_target2", "survival"])
        for t in range(len(f)):
            writer.writerow([t, f[t], f1[t], f2[t], surv[t]])


def render_case_table_tex(cases: List[CaseConfig], outpath: Path) -> None:
    def esc(text: str) -> str:
        return text.replace("_", "\\_")
    lines = []
    lines.append("\\begin{tabular}{lllllll}")
    lines.append("\\toprule")
    lines.append("Case & $N$ & $K$ & $q$ & $g$ & $\\beta$ & targets \\\\")
    lines.append("\\midrule")
    for c in cases:
        targets = f"({c.target1},{c.target2})"
        lines.append(
            f"{esc(c.name)} & {c.N} & {c.K} & {c.q:.3f} & {c.drift:.2f} & {c.beta:.3f} & {targets} \\\\")
    lines.append("\\bottomrule")
    lines.append("\\end{tabular}")
    outpath.write_text("\n".join(lines), encoding="utf-8")


def render_peak_table_tex(metrics: List[dict], outpath: Path) -> None:
    def esc(text: str) -> str:
        return text.replace("_", "\\_")
    lines = []
    lines.append("\\begin{tabular}{llllllll}")
    lines.append("\\toprule")
    lines.append("Case & $t_1$ & $h_1$ & $t_2$ & $h_2$ & $h_2/h_1$ & paper & macro \\\\")
    lines.append("\\midrule")
    for m in metrics:
        def fmt(val, fmt_str):
            return "-" if val is None else fmt_str.format(val)
        lines.append(
            f"{esc(m['name'])} & {fmt(m['t1'], '{:d}')} & {fmt(m['h1'], '{:.2e}')} & {fmt(m['t2'], '{:d}')} & {fmt(m['h2'], '{:.2e}')} & {fmt(m['h2_over_h1'], '{:.2f}')} & {m['paper']} & {m['macro']} \\\\")
    lines.append("\\bottomrule")
    lines.append("\\end{tabular}")
    outpath.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--outdir", type=str, default="outputs")
    args = parser.parse_args()

    base_dir = Path(__file__).resolve().parent.parent
    outdir = (base_dir / args.outdir).resolve()
    data_dir = (base_dir / "data").resolve()
    tables_dir = (base_dir / "tables").resolve()
    ensure_dir(outdir)
    ensure_dir(data_dir)
    ensure_dir(tables_dir)

    cases: List[CaseConfig] = [
        CaseConfig(
            name="A_no_sc_K2",
            N=20,
            K=2,
            q=2.0 / 3.0,
            drift=0.6,
            beta=0.0,
            start=0,
            target1=18,
            target2=10,
            src=None,
            dst=None,
            max_steps=3000,
            eps_surv=1e-12,
        ),
        CaseConfig(
            name="B_no_sc_K4",
            N=30,
            K=4,
            q=2.0 / 3.0,
            drift=0.6,
            beta=0.0,
            start=0,
            target1=27,
            target2=15,
            src=None,
            dst=None,
            max_steps=4000,
            eps_surv=1e-12,
        ),
        CaseConfig(
            name="C_sc_K2",
            N=60,
            K=2,
            q=2.0 / 3.0,
            drift=0.0,
            beta=0.02,
            start=0,
            target1=30,
            target2=31,
            src=5,
            dst=31,
            max_steps=9000,
            eps_surv=1e-12,
        ),
        CaseConfig(
            name="D_sc_K4",
            N=60,
            K=4,
            q=2.0 / 3.0,
            drift=0.0,
            beta=0.02,
            start=0,
            target1=30,
            target2=31,
            src=5,
            dst=31,
            max_steps=9000,
            eps_surv=1e-12,
        ),
        CaseConfig(
            name="E_triple_K4",
            N=30,
            K=4,
            q=0.9,
            drift=0.8,
            beta=0.0,
            start=0,
            target1=29,
            target2=20,
            src=None,
            dst=None,
            max_steps=5000,
            eps_surv=1e-12,
        ),
    ]

    metrics_rows: List[dict] = []

    # Per-case series
    case_series = {}
    for cfg in cases:
        f_total, f1, f2, surv = fpt_two_targets(cfg)
        case_series[cfg.name] = (f_total, f1, f2, surv)

        save_series_csv(outdir / f"{cfg.name}_fpt.csv", f_total, f1, f2, surv)

        peaks = detect_peaks(f_total)
        m = peak_metrics(peaks)
        m["name"] = cfg.name
        metrics_rows.append(m)

    # Heatmap scan: N vs beta for shortcut geometry
    Ns = list(range(30, 81, 5))
    betas = [round(x, 2) for x in np.linspace(0.0, 0.08, 9)]

    for K in (2, 4):
        flags = np.zeros((len(Ns), len(betas)), dtype=float)
        rows = []
        for iN, N in enumerate(Ns):
            for ib, beta in enumerate(betas):
                cfg = CaseConfig(
                    name=f"scan_K{K}_N{N}_b{beta:.2f}",
                    N=N,
                    K=K,
                    q=2.0 / 3.0,
                    drift=0.0,
                    beta=beta,
                    start=0,
                    target1=N // 2,
                    target2=(N // 2 + 1) % N,
                    src=5 % N,
                    dst=(N // 2 + 1) % N,
                    max_steps=7000,
                    eps_surv=1e-12,
                )
                f_total, _, _, _ = fpt_two_targets(cfg)
                peaks = detect_peaks(f_total)
                m = peak_metrics(peaks)
                flag = 2 if m["macro"] else (1 if m["paper"] else 0)
                flags[iN, ib] = flag
                rows.append(
                    {
                        "N": N,
                        "K": K,
                        "beta": beta,
                        "flag": flag,
                        "n_peaks": m["n_peaks"],
                        "t1": m["t1"],
                        "h1": m["h1"],
                        "t2": m["t2"],
                        "h2": m["h2"],
                        "h2_over_h1": m["h2_over_h1"],
                        "paper": m["paper"],
                        "macro": m["macro"],
                    }
                )

        csv_path = data_dir / f"scan_bimodality_K{K}.csv"
        with csv_path.open("w", newline="") as f_out:
            writer = csv.DictWriter(f_out, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

    # Save configs
    configs_path = data_dir / "model_configs.json"
    configs_path.write_text(json.dumps([asdict(c) for c in cases], indent=2), encoding="utf-8")

    csv_path = data_dir / "model_configs.csv"
    with csv_path.open("w", newline="") as f_out:
        writer = csv.DictWriter(f_out, fieldnames=list(asdict(cases[0]).keys()))
        writer.writeheader()
        for c in cases:
            writer.writerow(asdict(c))

    # Tables
    render_case_table_tex(cases, tables_dir / "case_configs.tex")
    render_peak_table_tex(metrics_rows, tables_dir / "case_peaks.tex")


if __name__ == "__main__":
    main()
