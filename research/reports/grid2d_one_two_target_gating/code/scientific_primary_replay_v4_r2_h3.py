#!/usr/bin/env python3
"""Independent raw-NPZ primary/ROPE replay for the append-only H3 layer."""
from __future__ import annotations

import hashlib
import json
import math
import statistics
from pathlib import Path
from typing import Any, Mapping, Sequence

from scipy.stats import t as student_t

import scientific_tail_replay_v4_r2_h2 as h2


def req(value: bool, message: str) -> None:
    if not value:
        raise ValueError(message)


def mean_ci(values: Sequence[float]) -> dict[str, float | int]:
    req(len(values) >= 2, "primary replay requires at least two disorder blocks")
    mean = statistics.fmean(values)
    sd = statistics.stdev(values)
    se = sd / math.sqrt(len(values))
    critical = float(student_t.ppf(0.975, len(values) - 1))
    half = critical * se
    return {
        "n_disorder_blocks": len(values), "mean": mean,
        "standard_deviation": sd, "standard_error": se,
        "t_critical": critical, "ci_half_width": half,
        "ci_lower": mean - half, "ci_upper": mean + half,
    }


def primary_contract(manifest: Mapping[str, Any]) -> dict[str, Any]:
    prereg = manifest.get("preregistration")
    req(isinstance(prereg, dict), "manifest preregistration missing")
    primary = prereg.get("primary_inference")
    req(isinstance(primary, dict), "manifest primary inference missing")
    geometry = primary.get("primary_geometry")
    contrast = primary.get("primary_amplitude_contrast")
    req(isinstance(geometry, dict) and isinstance(contrast, dict),
        "manifest primary geometry/contrast missing")
    contract = {
        "target2_x": int(geometry["target2_x"]),
        "target2_y": int(geometry["target2_y"]),
        "control": float(contrast["low"]),
        "treatment": float(contrast["high"]),
        "rope_half_width": float(primary["rope_absolute_probability"]),
        "confidence_level": float(primary["confidence_level"]),
    }
    req(contract == {
        "target2_x": 32, "target2_y": 24, "control": 0.0,
        "treatment": 0.2, "rope_half_width": 0.002,
        "confidence_level": 0.95,
    }, "frozen primary/ROPE contract drift")
    return contract


def condition_parameters(defaults: Mapping[str, Any], config: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "profile": config.get("profile"),
        "walkers": defaults["walkers"], "steps": defaults["steps"],
        "base_hold": defaults["base_hold"], "amplitude": config["amplitude"],
        "target_radius": defaults["target_radius"],
        "start_x": defaults["start_x"], "start_y": defaults["start_y"],
        "target1_x": defaults["target1_x"], "target1_y": defaults["target1_y"],
        "target2_x": config["target2_x"], "target2_y": config["target2_y"],
        "checkpoints": defaults["checkpoints"],
    }


def derive_primary(
    *, control_blocks: Mapping[int, float], treatment_blocks: Mapping[int, float],
    control_parameters: Mapping[str, Any],
    treatment_parameters: Mapping[str, Any], contract: Mapping[str, Any],
) -> dict[str, Any]:
    req(set(control_blocks) == set(treatment_blocks)
        and len(control_blocks) >= 2, "primary disorder pairing drift")
    control_other = dict(control_parameters)
    treatment_other = dict(treatment_parameters)
    req(control_other.pop("amplitude") == contract["control"]
        and treatment_other.pop("amplitude") == contract["treatment"]
        and control_other == treatment_other,
        "primary conditions differ beyond frozen amplitude contrast")
    effects = [float(treatment_blocks[block]) - float(control_blocks[block])
               for block in sorted(control_blocks)]
    stats = mean_ci(effects)
    lower = float(stats["ci_lower"])
    upper = float(stats["ci_upper"])
    rope_low = -float(contract["rope_half_width"])
    rope_high = float(contract["rope_half_width"])
    if upper < rope_low:
        decision = "negative_change"
    elif lower > rope_high:
        decision = "positive_change"
    elif lower >= rope_low and upper <= rope_high:
        decision = "practical_equivalence"
    else:
        decision = "inconclusive"
    control_id = hashlib.sha256(json.dumps(
        control_parameters, sort_keys=True, separators=(",", ":")).encode()).hexdigest()[:16]
    treatment_id = hashlib.sha256(json.dumps(
        treatment_parameters, sort_keys=True, separators=(",", ":")).encode()).hexdigest()[:16]
    comparison_id = hashlib.sha256(json.dumps(
        control_other, sort_keys=True, separators=(",", ":")).encode()).hexdigest()[:16]
    return {
        "horizon": int(control_parameters["steps"]),
        "target2": {"x": int(contract["target2_x"]),
                    "y": int(contract["target2_y"])},
        "estimand": ("gating_probability_drop(amplitude=0.20)-"
                      "gating_probability_drop(amplitude=0.00)"),
        "control_condition_id": control_id,
        "treatment_condition_id": treatment_id,
        "comparison_id": comparison_id,
        "rope": {"lower": rope_low, "upper": rope_high},
        "statistics": stats, "decision": decision,
    }


def validate_primary_claim(actual: Mapping[str, Any],
                           expected: Mapping[str, Any]) -> None:
    h2.close_tree(actual, expected, "reduction.primary")


def replay(
    manifest_path: Path, raw_root: Path, reduction_path: Path,
    *, expected_blocks: int, tail_replay: Mapping[str, Any],
) -> dict[str, Any]:
    manifest = h2.strict_json(manifest_path)
    reduction = h2.strict_json(reduction_path, mode600=True)
    configs = manifest.get("cells")
    inventory = reduction.get("inventory")
    req(isinstance(configs, list) and isinstance(inventory, list),
        "primary manifest/reduction inventory missing")
    config_by_id = {int(row["cell_id"]): row for row in configs}
    inventory_by_id = {int(row["cell_id"]): row for row in inventory}
    req(set(config_by_id) == set(inventory_by_id),
        "primary manifest/reduction cell inventory drift")
    defaults = manifest["defaults"]
    contract = primary_contract(manifest)
    selected: dict[float, dict[int, dict[int, float]]] = {
        contract["control"]: {}, contract["treatment"]: {},
    }
    parameters: dict[float, dict[str, Any]] = {}
    raw_lines: list[str] = []
    for cell, config in config_by_id.items():
        amplitude = float(config["amplitude"])
        if not (int(config["target2_x"]) == contract["target2_x"]
                and int(config["target2_y"]) == contract["target2_y"]
                and amplitude in selected):
            continue
        row = inventory_by_id[cell]
        json_path = raw_root / row["json_path"]
        npz_path = raw_root / row["npz_path"]
        req(h2.sha(json_path) == row["json_sha256"]
            and h2.sha(npz_path) == row["npz_sha256"],
            f"primary cell {cell} raw hash reverse binding drift")
        metrics = h2.raw_checkpoint_metrics(npz_path, json_path, defaults, cell)
        block = int(config["disorder_replicate"])
        walk = int(config["walk_replicate"])
        streams = selected[amplitude].setdefault(block, {})
        req(walk not in streams, f"primary cell {cell} duplicate walk stream")
        streams[walk] = float(metrics["gating_probability_drop"])
        parameters[amplitude] = condition_parameters(defaults, config)
        raw_lines.append(f"{cell}\t{row['json_sha256']}\t{row['npz_sha256']}\n")
    block_means: dict[float, dict[int, float]] = {}
    for amplitude, by_block in selected.items():
        req(set(by_block) == set(range(expected_blocks)),
            f"primary amplitude {amplitude} disorder inventory drift")
        block_means[amplitude] = {}
        for block, streams in by_block.items():
            req(set(streams) == {0, 1},
                f"primary amplitude {amplitude} block {block} walk pair drift")
            block_means[amplitude][block] = statistics.fmean(
                streams[walk] for walk in (0, 1))
    primary = derive_primary(
        control_blocks=block_means[contract["control"]],
        treatment_blocks=block_means[contract["treatment"]],
        control_parameters=parameters[contract["control"]],
        treatment_parameters=parameters[contract["treatment"]],
        contract=contract,
    )
    validate_primary_claim(reduction.get("primary", {}), primary)
    tail = tail_replay.get("tail_gate")
    req(isinstance(tail, dict) and isinstance(tail.get("pass"), bool),
        "H3 requires H2 independent tail replay")
    sacct = reduction.get("audit", {}).get("sacct", {})
    sacct_ok = not bool(sacct.get("provided")) or sacct.get("verified") is True
    evidence = {
        "tail_gate_pass": tail["pass"],
        "primary_decision": primary["decision"],
        "sacct_verified_if_provided": sacct_ok,
        "ready": tail["pass"] and primary["decision"] != "inconclusive" and sacct_ok,
    }
    h2.close_tree(reduction.get("evidence_decision"), evidence,
                  "reduction.evidence_decision.h3")
    passed = tail["pass"] and primary["decision"] != "inconclusive" and sacct_ok
    return {
        "independently_recomputed_from_raw_npz": True,
        "selected_raw_cells": len(raw_lines),
        "disorder_blocks": expected_blocks,
        "raw_pair_digest": hashlib.sha256("".join(sorted(raw_lines)).encode()).hexdigest(),
        "primary": primary, "evidence_decision": evidence,
        "status": ("PASS_PRIMARY_ROPE_EVIDENCE" if passed else
                   ("HOLD_STAGE_A2_160K" if not tail["pass"] else
                    "HOLD_PRIMARY_INCONCLUSIVE")),
        "authorizes_ready_evidence": passed,
    }
