#!/usr/bin/env python3
"""Paired fixed-mean GPU gating experiment using a frozen field pack."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np
import torch


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--field-pack", type=Path, required=True)
    parser.add_argument("--disorder-replicate", type=int, required=True)
    parser.add_argument("--walk-replicate", type=int, default=0)
    parser.add_argument("--amplitude", type=float, required=True)
    parser.add_argument("--target-fraction", type=float, default=0.50)
    parser.add_argument("--base-hold", type=float, default=0.30)
    parser.add_argument("--walkers", type=int, default=500_000)
    parser.add_argument("--steps", type=int, default=5_000)
    parser.add_argument("--batch-size", type=int, default=131_072)
    parser.add_argument("--target-radius", type=int, default=3)
    parser.add_argument("--device", choices=("cuda", "cpu"), default="cuda")
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def summarize_histogram(histogram: torch.Tensor, walkers: int) -> dict[str, Any]:
    hits = int(histogram.sum().item())
    probability = hits / walkers
    if hits == 0:
        return {
            "hits": 0,
            "probability": 0.0,
            "standard_error": 0.0,
            "mean_fpt": None,
            "median_fpt": None,
            "q90_fpt": None,
        }
    times = torch.arange(histogram.numel(), dtype=torch.float64)
    cumulative = torch.cumsum(histogram, dim=0)

    def quantile(value: float) -> int:
        return int(torch.searchsorted(cumulative, torch.tensor(math.ceil(value * hits))).item())

    return {
        "hits": hits,
        "probability": probability,
        "standard_error": math.sqrt(probability * (1.0 - probability) / walkers),
        "mean_fpt": float((times * histogram.to(torch.float64)).sum().item() / hits),
        "median_fpt": quantile(0.5),
        "q90_fpt": quantile(0.9),
    }


@torch.inference_mode()
def simulate_pair(
    args: argparse.Namespace,
    device: torch.device,
    hold: torch.Tensor,
) -> dict[str, Any]:
    width = int(hold.shape[1])
    height = int(hold.shape[0])
    start = (7, height // 2)
    target1 = (width - 10, height // 2)
    target2 = (width // 2, int(round(args.target_fraction * (height - 1))))
    radius2 = args.target_radius * args.target_radius
    directions_x = torch.tensor((1, -1, 0, 0), dtype=torch.long, device=device)
    directions_y = torch.tensor((0, 0, 1, -1), dtype=torch.long, device=device)
    one_hist1 = torch.zeros(args.steps + 1, dtype=torch.int64)
    two_hist1 = torch.zeros(args.steps + 1, dtype=torch.int64)
    two_hist2 = torch.zeros(args.steps + 1, dtype=torch.int64)
    pair_counts = torch.zeros(9, dtype=torch.int64)
    checkpoints = sorted(set((args.steps // 10, args.steps // 4, args.steps // 2, 3 * args.steps // 4, args.steps)))
    checkpoint_totals = {
        str(step): torch.zeros(6, dtype=torch.int64) for step in checkpoints
    }
    walk_seed = 1729 + args.disorder_replicate * 104729 + args.walk_replicate * 1009

    for batch_start in range(0, args.walkers, args.batch_size):
        count = min(args.batch_size, args.walkers - batch_start)
        generator = torch.Generator(device=device).manual_seed(walk_seed + batch_start)
        x_one = torch.full((count,), start[0], dtype=torch.long, device=device)
        y_one = torch.full((count,), start[1], dtype=torch.long, device=device)
        x_two = x_one.clone()
        y_two = y_one.clone()
        hit_one = torch.zeros(count, dtype=torch.int8, device=device)
        hit_two = torch.zeros(count, dtype=torch.int8, device=device)
        fpt_one = torch.zeros(count, dtype=torch.int32, device=device)
        fpt_two = torch.zeros(count, dtype=torch.int32, device=device)

        for step in range(1, args.steps + 1):
            random_move = torch.rand(count, generator=generator, device=device)
            direction = torch.randint(0, 4, (count,), generator=generator, device=device)

            active_one = hit_one == 0
            moving_one = active_one & (random_move >= hold[y_one, x_one])
            trial_x = (x_one + directions_x[direction]).clamp(0, width - 1)
            trial_y = (y_one + directions_y[direction]).clamp(0, height - 1)
            x_one = torch.where(moving_one, trial_x, x_one)
            y_one = torch.where(moving_one, trial_y, y_one)
            at1_one = active_one & (
                (x_one - target1[0]).square() + (y_one - target1[1]).square() <= radius2
            )
            hit_one[at1_one] = 1
            fpt_one[at1_one] = step

            active_two = hit_two == 0
            moving_two = active_two & (random_move >= hold[y_two, x_two])
            trial_x = (x_two + directions_x[direction]).clamp(0, width - 1)
            trial_y = (y_two + directions_y[direction]).clamp(0, height - 1)
            x_two = torch.where(moving_two, trial_x, x_two)
            y_two = torch.where(moving_two, trial_y, y_two)
            at1_two = active_two & (
                (x_two - target1[0]).square() + (y_two - target1[1]).square() <= radius2
            )
            hit_two[at1_two] = 1
            fpt_two[at1_two] = step
            still_active = hit_two == 0
            at2_two = still_active & (
                (x_two - target2[0]).square() + (y_two - target2[1]).square() <= radius2
            )
            hit_two[at2_two] = 2
            fpt_two[at2_two] = step

            if step in checkpoints:
                checkpoint_totals[str(step)] += torch.tensor((
                    int((hit_one == 1).sum().item()),
                    int((hit_one == 0).sum().item()),
                    int((hit_two == 1).sum().item()),
                    int((hit_two == 2).sum().item()),
                    int((hit_two == 0).sum().item()),
                    count,
                ), dtype=torch.int64)

        one_hist1 += torch.bincount(fpt_one[hit_one == 1].long(), minlength=args.steps + 1)[: args.steps + 1].cpu()
        two_hist1 += torch.bincount(fpt_two[hit_two == 1].long(), minlength=args.steps + 1)[: args.steps + 1].cpu()
        two_hist2 += torch.bincount(fpt_two[hit_two == 2].long(), minlength=args.steps + 1)[: args.steps + 1].cpu()
        pair_counts += torch.bincount(
            hit_one.long().cpu() * 3 + hit_two.long().cpu(), minlength=9
        )[:9]

    invalid_subset = int(pair_counts[1].item())
    if invalid_subset:
        raise AssertionError("paired target-1 subset invariant failed")
    one_target1 = summarize_histogram(one_hist1, args.walkers)
    two_target1 = summarize_histogram(two_hist1, args.walkers)
    two_target2 = summarize_histogram(two_hist2, args.walkers)
    one_unresolved = args.walkers - int(one_hist1.sum())
    two_unresolved = args.walkers - int(two_hist1.sum()) - int(two_hist2.sum())
    return {
        "one_target": {
            "target1": one_target1,
            "unresolved": one_unresolved,
            "unresolved_probability": one_unresolved / args.walkers,
            "mass_balance": (int(one_hist1.sum()) + one_unresolved) / args.walkers,
        },
        "two_targets": {
            "target1": two_target1,
            "target2": two_target2,
            "unresolved": two_unresolved,
            "unresolved_probability": two_unresolved / args.walkers,
            "mass_balance": (
                int(two_hist1.sum()) + int(two_hist2.sum()) + two_unresolved
            ) / args.walkers,
        },
        "paired_outcomes": {
            "one_unresolved__two_unresolved": int(pair_counts[0]),
            "one_unresolved__two_target1": int(pair_counts[1]),
            "one_unresolved__two_target2": int(pair_counts[2]),
            "one_target1__two_unresolved": int(pair_counts[3]),
            "one_target1__two_target1": int(pair_counts[4]),
            "one_target1__two_target2": int(pair_counts[5]),
            "invalid_two_target1_not_one_target1": invalid_subset,
        },
        "cumulative_counts": {
            key: {
                "one_target1": int(value[0]),
                "one_unresolved": int(value[1]),
                "two_target1": int(value[2]),
                "two_target2": int(value[3]),
                "two_unresolved": int(value[4]),
                "walkers": int(value[5]),
            }
            for key, value in checkpoint_totals.items()
        },
        "gating_probability_drop": (
            one_target1["probability"] - two_target1["probability"]
        ),
        "gating_probability_ratio": (
            two_target1["probability"] / one_target1["probability"]
            if one_target1["probability"] else None
        ),
        "target2_first_probability": two_target2["probability"],
    }


def main() -> None:
    args = parse_args()
    if args.device == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA requested but unavailable")
    device = torch.device(args.device)
    pack_bytes = args.field_pack.read_bytes()
    with np.load(args.field_pack) as pack:
        contrasts = np.asarray(pack["contrasts"], dtype=np.float64)
        seeds = np.asarray(pack["seeds"], dtype=np.int64)
    if not 0 <= args.disorder_replicate < contrasts.shape[0]:
        raise ValueError("disorder replicate is outside field pack")
    contrast = contrasts[args.disorder_replicate]
    hold_np = np.asarray(args.base_hold + args.amplitude * contrast, dtype="<f8")
    if hold_np.min() < 0.0 or hold_np.max() >= 1.0:
        raise ValueError("invalid holding probabilities")
    if abs(float(hold_np.mean()) - args.base_hold) > 1e-12:
        raise AssertionError("fixed-mean hold invariant failed")
    hold = torch.from_numpy(hold_np.astype(np.float32)).to(device)
    started = time.time()
    result = simulate_pair(args, device, hold)
    source = Path(__file__).resolve()
    payload = {
        "schema": "grid2d-one-two-target-gating-fixed-mean-gpu-v2",
        "parameters": {
            "walkers": args.walkers,
            "steps": args.steps,
            "batch_size": args.batch_size,
            "base_hold": args.base_hold,
            "amplitude": args.amplitude,
            "target_fraction": args.target_fraction,
            "target_radius": args.target_radius,
            "disorder_replicate": args.disorder_replicate,
            "disorder_seed": int(seeds[args.disorder_replicate]),
            "walk_replicate": args.walk_replicate,
        },
        "field": {
            "pack_filename": args.field_pack.name,
            "pack_sha256": hashlib.sha256(pack_bytes).hexdigest(),
            "hold_sha256_float64_le": hashlib.sha256(hold_np.tobytes()).hexdigest(),
            "minimum": float(hold_np.min()),
            "mean": float(hold_np.mean()),
            "maximum": float(hold_np.max()),
            "standard_deviation": float(hold_np.std()),
            "device_dtype": str(hold.dtype),
        },
        "provenance": {
            "source": source.name,
            "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
            "argv": sys.argv,
            "slurm": {
                key: os.environ.get(key)
                for key in (
                    "SLURM_JOB_ID", "SLURM_ARRAY_JOB_ID", "SLURM_ARRAY_TASK_ID",
                    "SLURM_JOB_NAME", "SLURM_NODELIST", "SLURM_CPUS_PER_TASK",
                    "SLURM_JOB_ACCOUNT", "SLURM_JOB_PARTITION",
                )
            },
        },
        "runtime": {
            "elapsed_seconds": time.time() - started,
            "hostname": platform.node(),
            "python": platform.python_version(),
            "numpy": np.__version__,
            "torch": torch.__version__,
            "cuda": torch.version.cuda,
            "device": str(device),
            "gpu": torch.cuda.get_device_name(0) if device.type == "cuda" else None,
        },
        **result,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "schema": payload["schema"],
        "elapsed_seconds": payload["runtime"]["elapsed_seconds"],
        "gating_probability_drop": payload["gating_probability_drop"],
        "source_sha256": payload["provenance"]["source_sha256"],
    }), flush=True)


if __name__ == "__main__":
    main()
