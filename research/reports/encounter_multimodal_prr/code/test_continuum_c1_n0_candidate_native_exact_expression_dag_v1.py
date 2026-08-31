from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import stat
import subprocess
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

CODE = Path(__file__).resolve().parent
BUILDER = CODE / "build_continuum_c1_n0_candidate_native_exact_expression_dag_v1.py"
VALIDATOR = CODE / "validate_continuum_c1_n0_candidate_native_exact_expression_dag_v1.py"
CLAIMS = {
    "external_predecessor_commitment_present": False,
    "ordered_roles_8_10_replay_executed": False,
    "production_data_read": False,
    "production_same_member_bridge_accepted": False,
    "release_eligible": False,
    "science_executed": False,
}
TEMPLATE_DOMAIN = b"encounter-c1-n0-candidate-native-exact-expression-dag-semantic-template-v2\0"


def load_module(path: Path, module_name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load test module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


BUILDER_MODULE = load_module(BUILDER, "_fixed_formula_dag_builder_test")
VALIDATOR_MODULE = load_module(VALIDATOR, "_fixed_formula_dag_validator_test")
SEMANTIC_TEMPLATE = BUILDER_MODULE.SEMANTIC_TEMPLATE
SEMANTIC_TEMPLATE_SHA256 = BUILDER_MODULE.SEMANTIC_TEMPLATE_SHA256


def canonical(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("ascii")


NONDEGENERATE_VALUES = {
    "M_L": ("8/1", "8/1"),
    "S_M": ("2/1", "2/1"),
    "S_R": ("2/1", "2/1"),
    "S_Y": ("2/1", "2/1"),
    "mu_M": ("1/2", "1/2"),
    "mu_R": ("1/2", "1/2"),
    "mu_Y": ("1/2", "1/2"),
    "mu_edge_left": ("1/2", "1/2"),
    "forward_q_interval": ("6/5", "13/10"),
    "mu_edge_right": ("1/1", "1/1"),
    "reverse_q_interval": ("29/50", "16/25"),
    "direct_left_kappa_interval": ("59/100", "63/100"),
    "direct_right_kappa_interval": ("3/5", "31/50"),
    "M_pi": ("3/10", "31/100"),
    "C_contact": ("1/2", "1/2"),
    "W_norm": ("1/1", "1/1"),
    "weight_0": ("1/4", "1/4"),
    "weight_1": ("1/4", "1/4"),
    "weight_2": ("1/4", "1/4"),
    "weight_3": ("1/4", "1/4"),
    "Phi_0": ("1/1", "1/1"),
    "Phi_1": ("1/1", "1/1"),
    "Phi_2": ("1/1", "1/1"),
    "Phi_3": ("1/1", "1/1"),
}


def interval_request(values: dict[str, tuple[str, str]]) -> dict[str, Any]:
    inputs = []
    for binding in SEMANTIC_TEMPLATE["outward_inputs"]:
        lower, upper = values[binding["input_id"]]
        inputs.append(
            {
                "input_id": binding["input_id"],
                "lower_exact": lower,
                "provenance_lane": binding["provenance_lane"],
                "upper_exact": upper,
                "value_type": binding["value_type"],
            }
        )
    return {
        "claim_boundary": CLAIMS,
        "inputs": inputs,
        "schema": "encounter_continuum_c1_n0_candidate_native_exact_expression_dag_request_v1",
        "semantic_template": SEMANTIC_TEMPLATE,
        "semantic_template_sha256": SEMANTIC_TEMPLATE_SHA256,
        "status": "OUTWARD_INTERVALS_AND_FIXED_FORMAL_IDENTITIES_ONLY",
    }


def nondegenerate_request() -> dict[str, Any]:
    return interval_request(NONDEGENERATE_VALUES)


def singleton_request() -> dict[str, Any]:
    values = {key: (lower, lower) for key, (lower, _) in NONDEGENERATE_VALUES.items()}
    values.update(
        {
            "reverse_q_interval": ("3/5", "3/5"),
            "direct_left_kappa_interval": ("3/5", "3/5"),
            "direct_right_kappa_interval": ("3/5", "3/5"),
            "M_pi": ("1/4", "1/4"),
        }
    )
    return interval_request(values)


def zero_nonnegative_request() -> dict[str, Any]:
    values = dict(NONDEGENERATE_VALUES)
    values.update(
        {
            "C_contact": ("0/1", "0/1"),
            "weight_0": ("0/1", "0/1"),
            "Phi_0": ("0/1", "0/1"),
            "Phi_1": ("0/1", "0/1"),
            "Phi_2": ("0/1", "0/1"),
            "Phi_3": ("0/1", "0/1"),
        }
    )
    return interval_request(values)


def asymmetric_four_profile_request() -> dict[str, Any]:
    request = singleton_request()
    replacements = {
        "C_contact": "4/7",
        "W_norm": "5/3",
        "weight_0": "1/1",
        "weight_1": "3/1",
        "weight_2": "9/1",
        "weight_3": "27/1",
        "Phi_0": "2/1",
        "Phi_1": "5/1",
        "Phi_2": "11/1",
        "Phi_3": "23/1",
    }
    for record in request["inputs"]:
        if record["input_id"] in replacements:
            record["lower_exact"] = replacements[record["input_id"]]
            record["upper_exact"] = replacements[record["input_id"]]
    return request


def write_request(path: Path, value: dict[str, Any] | None = None) -> None:
    path.write_bytes(canonical(nondegenerate_request() if value is None else value))
    path.chmod(0o444)


def run(*arguments: str, timeout: float = 10.0) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-I", "-B", *arguments],
        check=False,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def build_payload(
    tmp_path: Path,
    request_value: dict[str, Any],
) -> tuple[Path, Path, dict[str, Any]]:
    tmp_path.mkdir(parents=True, exist_ok=True)
    request = tmp_path / "request.json"
    artifact = tmp_path / "artifact.json"
    write_request(request, request_value)
    result = run(str(BUILDER), "--request", str(request), "--output", str(artifact))
    assert result.returncode == 0, result.stderr
    return request, artifact, json.loads(artifact.read_text(encoding="ascii"))


def outputs(section: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {record["output_name"]: record["value"] for record in section["outputs"]}


def test_template_is_value_free_fixed_and_source_separated() -> None:
    assert SEMANTIC_TEMPLATE == VALIDATOR_MODULE.SEMANTIC_TEMPLATE
    expected_sha = hashlib.sha256(TEMPLATE_DOMAIN + canonical(SEMANTIC_TEMPLATE)).hexdigest()
    assert SEMANTIC_TEMPLATE_SHA256 == expected_sha
    assert VALIDATOR_MODULE.SEMANTIC_TEMPLATE_SHA256 == expected_sha
    assert len(SEMANTIC_TEMPLATE["outward_inputs"]) == 24
    assert len(SEMANTIC_TEMPLATE["outward_nodes"]) == 20
    assert len(SEMANTIC_TEMPLATE["outward_assertions"]) == 6
    assert len(SEMANTIC_TEMPLATE["outward_outputs"]) == 12
    assert len(SEMANTIC_TEMPLATE["formal_atoms"]) == 21
    assert len(SEMANTIC_TEMPLATE["formal_nodes"]) == 24
    assert len(SEMANTIC_TEMPLATE["formal_assertions"]) == 6
    assert len(SEMANTIC_TEMPLATE["formal_outputs"]) == 16

    template_text = canonical(SEMANTIC_TEMPLATE).decode("ascii")
    assert "/" not in template_text
    assert all(
        value_key not in template_text
        for value_key in ("lower_exact", "upper_exact", "value_exact")
    )
    assert all(
        binding["semantic_shape"] == "interval" for binding in SEMANTIC_TEMPLATE["outward_inputs"]
    )
    request = nondegenerate_request()
    assert all(
        set(record)
        == {
            "input_id",
            "lower_exact",
            "provenance_lane",
            "upper_exact",
            "value_type",
        }
        for record in request["inputs"]
    )
    assert "formal_atoms" not in request
    assert all("shape" not in node for node in SEMANTIC_TEMPLATE["outward_nodes"])
    assert BUILDER.stem not in VALIDATOR.read_text(encoding="utf-8")


def test_nondegenerate_build_check_validate_and_determinism(tmp_path: Path) -> None:
    request = tmp_path / "request.json"
    artifact = tmp_path / "artifact.json"
    second = tmp_path / "artifact-second.json"
    write_request(request)
    built = run(str(BUILDER), "--request", str(request), "--output", str(artifact))
    assert built.returncode == 0, built.stderr
    checked = run(
        str(BUILDER),
        "--request",
        str(request),
        "--output",
        str(artifact),
        "--check",
    )
    assert checked.returncode == 0, checked.stderr
    verified = run(str(VALIDATOR), "--request", str(request), "--artifact", str(artifact))
    assert verified.returncode == 0, verified.stderr
    rebuilt = run(str(BUILDER), "--request", str(request), "--output", str(second))
    assert rebuilt.returncode == 0, rebuilt.stderr
    assert artifact.read_bytes() == second.read_bytes()
    assert stat.S_IMODE(artifact.stat().st_mode) == 0o444
    assert artifact.stat().st_nlink == 1

    payload = json.loads(artifact.read_text(encoding="ascii"))
    outward = payload["outward_interval_evaluation"]
    outward_outputs = outputs(outward)
    expected = {
        "G": ("1/1", "1/1"),
        "pi_h": ("1/8", "1/8"),
        "common_kappa_interval": ("3/5", "31/50"),
        "conductance": ("3/20", "31/200"),
        "rho": ("12/5", "62/25"),
        "V": ("1/2", "1/2"),
        "K_direct": ("25/124", "5/24"),
        "K_via_rho": ("25/124", "5/24"),
        "physical_weight_left": ("15/248", "31/480"),
        "physical_weight_right": ("1/16", "1/16"),
    }
    for output_name, (lower, upper) in expected.items():
        assert outward_outputs[output_name]["lower_exact"] == lower
        assert outward_outputs[output_name]["upper_exact"] == upper
    assert outward["value_semantics"] == ("outward_interval_arithmetic_no_exact_member_selector")
    assert payload["claim_boundary"] == CLAIMS

    formal = payload["formal_identity_proof"]
    formal_outputs = outputs(formal)
    common_formula = formal_outputs["common_flux_formula"]
    for name in (
        "kappa_direct_left_formula",
        "kappa_direct_right_formula",
        "flux_forward_formula",
        "flux_reverse_formula",
    ):
        assert formal_outputs[name] == common_formula
    assert formal_outputs["K_direct_formula"] == formal_outputs["K_via_rho_formula"]
    assert (
        formal_outputs["physical_weight_left_formula"]
        == formal_outputs["physical_weight_right_formula"]
    )
    assert len(formal_outputs["V_formula"]["terms"]) == 4
    atom_index = {atom_id: index for index, atom_id in enumerate(formal["atom_order"])}
    q_forward_term = formal_outputs["q_forward_formula"]["terms"][0]
    assert q_forward_term["exponents"][atom_index["kappa"]] == 1
    assert q_forward_term["exponents"][atom_index["mu_edge_left"]] == -1
    q_reverse_term = formal_outputs["q_reverse_formula"]["terms"][0]
    assert q_reverse_term["exponents"][atom_index["kappa"]] == 1
    assert q_reverse_term["exponents"][atom_index["mu_edge_right"]] == -1
    assert all(
        term["exponents"][atom_index["M_pi"]] == 0
        for term in formal_outputs["physical_weight_left_formula"]["terms"]
    )
    assert all(record["holds"] is True for record in formal["assertions"])
    assert formal["proof_scope"] == ("fixed_formula_identities_without_numeric_exact_selectors")
    assert formal["assumption_scope"] == ("conditional_on_authority_bound_exact_real_atoms")
    assert hashlib.sha256(artifact.read_bytes()).hexdigest() in verified.stdout


def test_singleton_and_zero_nonnegative_policy_sentinels(tmp_path: Path) -> None:
    _, _, singleton = build_payload(tmp_path / "singleton", singleton_request())
    singleton_outputs = outputs(singleton["outward_interval_evaluation"])
    assert all(
        record["lower_exact"] == record["upper_exact"] for record in singleton_outputs.values()
    )

    _, _, zero = build_payload(tmp_path / "zero", zero_nonnegative_request())
    zero_outputs = outputs(zero["outward_interval_evaluation"])
    for output_name in (
        "V",
        "K_direct",
        "K_via_rho",
        "physical_weight_left",
        "physical_weight_right",
    ):
        assert zero_outputs[output_name] == {
            "lower_exact": "0/1",
            "upper_exact": "0/1",
            "value_type": "interval_nonnegative",
        }


def test_four_common_flux_lanes_and_distinct_direct_provenance(tmp_path: Path) -> None:
    _, _, payload = build_payload(tmp_path, nondegenerate_request())
    outward = payload["outward_interval_evaluation"]
    input_receipts = {record["input_id"]: record for record in outward["inputs"]}
    assert (
        input_receipts["direct_left_kappa_interval"]["provenance_lane"]
        != input_receipts["direct_right_kappa_interval"]["provenance_lane"]
    )
    intersection_node = next(
        record for record in outward["nodes"] if record["node_id"] == "common_kappa_interval"
    )
    assert intersection_node["argument_ids"] == [
        "direct_left_kappa_interval",
        "direct_right_kappa_interval",
        "forward_product_kappa_interval",
        "reverse_product_kappa_interval",
    ]
    containment_ids = {
        record["assertion_id"]
        for record in outward["assertions"]
        if record["relation"] == "interval_contains"
    }
    assert {
        "common_flux_inside_direct_left",
        "common_flux_inside_direct_right",
        "common_flux_inside_forward",
        "common_flux_inside_reverse",
    } <= containment_ids


def test_independent_asymmetric_four_profile_exact_oracle(tmp_path: Path) -> None:
    _, _, payload = build_payload(tmp_path, asymmetric_four_profile_request())
    outward = payload["outward_interval_evaluation"]
    node_values = {record["node_id"]: record["value"] for record in outward["nodes"]}
    expected_profiles = {
        "weighted_profile_0": "2/1",
        "weighted_profile_1": "15/1",
        "weighted_profile_2": "99/1",
        "weighted_profile_3": "621/1",
        "weighted_profile_sum": "737/1",
        "V": "8844/35",
    }
    for node_id, expected in expected_profiles.items():
        assert node_values[node_id]["lower_exact"] == expected
        assert node_values[node_id]["upper_exact"] == expected

    independent_atom_order = (
        "M_L",
        "S_M",
        "S_R",
        "S_Y",
        "mu_M",
        "mu_R",
        "mu_Y",
        "mu_edge_left",
        "mu_edge_right",
        "M_pi",
        "W_norm",
        "kappa",
        "C_contact",
        "weight_0",
        "weight_1",
        "weight_2",
        "weight_3",
        "Phi_0",
        "Phi_1",
        "Phi_2",
        "Phi_3",
    )
    formal = payload["formal_identity_proof"]
    assert tuple(formal["atom_order"]) == independent_atom_order
    atom_index = {atom_id: index for index, atom_id in enumerate(independent_atom_order)}
    oracle_terms = []
    for profile_index in range(4):
        exponents = [0] * len(independent_atom_order)
        exponents[atom_index["C_contact"]] = 1
        exponents[atom_index["W_norm"]] = -1
        exponents[atom_index[f"weight_{profile_index}"]] = 1
        exponents[atom_index[f"Phi_{profile_index}"]] = 1
        oracle_terms.append({"coefficient_exact": "1/1", "exponents": exponents})
    oracle_value = {
        "terms": sorted(oracle_terms, key=lambda term: term["exponents"]),
        "value_type": "formal_q_laurent_polynomial_v1",
    }
    actual_value = outputs(formal)["V_formula"]
    oracle_domain = b"independent-asymmetric-four-profile-formal-oracle-v1\0"
    expected_oracle_digest = bytes(
        (
            136,
            9,
            114,
            154,
            157,
            6,
            62,
            217,
            134,
            90,
            199,
            18,
            187,
            71,
            235,
            34,
            253,
            74,
            179,
            144,
            220,
            213,
            221,
            49,
            56,
            45,
            4,
            249,
            67,
            83,
            147,
            201,
        )
    )
    assert actual_value == oracle_value
    assert (
        hashlib.sha256(oracle_domain + canonical(actual_value)).digest() == expected_oracle_digest
    )


def test_template_hash_is_independent_of_interval_values(tmp_path: Path) -> None:
    _, _, first = build_payload(tmp_path / "first", nondegenerate_request())
    _, _, second = build_payload(tmp_path / "second", singleton_request())
    assert first["request"]["sha256"] != second["request"]["sha256"]
    assert (
        first["semantic_template_sha256"]
        == second["semantic_template_sha256"]
        == SEMANTIC_TEMPLATE_SHA256
    )
    assert first["formal_identity_proof"] == second["formal_identity_proof"]


def test_check_missing_output_and_relative_paths_fail(tmp_path: Path) -> None:
    request = tmp_path / "request.json"
    missing = tmp_path / "missing.json"
    write_request(request)
    result = run(
        str(BUILDER),
        "--request",
        str(request),
        "--output",
        str(missing),
        "--check",
    )
    assert result.returncode != 0
    assert not missing.exists()
    result = run(
        str(BUILDER),
        "--request",
        request.name,
        "--output",
        str(missing),
    )
    assert result.returncode != 0
    assert "must be absolute" in result.stderr


def test_sources_have_no_literal_external_inventory_pins() -> None:
    hexadecimal = frozenset("0123456789abcdef")
    mutation_test = CODE / (
        "test_continuum_c1_n0_candidate_native_exact_expression_dag_mutations_v1.py"
    )
    for path in (BUILDER, VALIDATOR, Path(__file__), mutation_test):
        strings = [
            node.value
            for node in ast.walk(ast.parse(path.read_text(encoding="utf-8")))
            if isinstance(node, ast.Constant) and isinstance(node.value, str)
        ]
        assert not any(len(item) == 64 and set(item) <= hexadecimal for item in strings)
        assert not any(
            item.lower().endswith((".json", ".jsonl"))
            and any(marker in item.lower() for marker in ("source", "role", "raw", "integral"))
            for item in strings
        )
