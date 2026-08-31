"""Pure constants for the result-blind roles 8--10 replay-v2 protocol.

This module deliberately performs no I/O and contains no numerical method.
It is the small semantics-free vocabulary shared by the future plan-v2
validator and the role-v3 protocol adapters.  The frozen operation model, not
this module, remains the normative contract authority.
"""

from __future__ import annotations

from typing import Final

OPERATION_MODEL_SCHEMA: Final = (
    "encounter_continuum_c1_n0_role10_numerical_operation_model_v2_candidate"
)
OPERATION_MODEL_STATUS: Final = (
    "RESULT_BLIND_CONTRACT_ONLY_CANDIDATE_NO_NUMERICAL_IMPLEMENTATION_OR_EXECUTION"
)
OPERATION_MODEL_SHA256: Final = "ac0c2b185be75f0ecef3e331fdfd47fc674ca151fa6b26600aff9f789a2f8a6b"
OPERATION_MODEL_REPORT_RELATIVE_PATH: Final = (
    "artifacts/data/continuum_c1_n0_role10_numerical_operation_model_v2_candidate.json"
)

PLAN_SCHEMA: Final = "encounter_continuum_c1_n0_roles_8_10_replay_plan_v2"
PLAN_STATUS: Final = "RESULT_BLIND_PRECOMMIT_REPLAY_PLAN_NO_EXECUTION_RESULTS"
RUNTIME_CLOSURE_SCHEMA: Final = (
    "encounter_continuum_c1_n0_roles_8_10_implementation_runtime_closure_v1"
)
RUNTIME_CLOSURE_STATUS: Final = (
    "FROZEN_SOURCE_SEPARATED_ROLES_8_10_IMPLEMENTATION_RUNTIME_CLOSURE_NO_EXECUTION_RESULTS"
)
BUNDLE_SCHEMA: Final = "encounter_continuum_c1_n0_precommit_candidate_bundle_v2"
BUNDLE_STATUS: Final = "RESULT_BLIND_PRECOMMIT_CANDIDATE_BUNDLE_NO_EXECUTION_RESULTS"
REQUEST_STATUS: Final = (
    "EXTERNAL_PREDECESSOR_COMMITMENT_BOUND_RESULT_BLIND_REQUEST_NO_EXECUTION_RESULT"
)

SHARED_PRECOMMIT_DOMAIN: Final = "encounter-shared-precommit-context-v2"
ENTRY_PROJECTION_DOMAIN: Final = "encounter-role-replay-entry-v2"
SHARED_REPLAY_DOMAIN: Final = "encounter-continuum-c1-n0-shared-replay-context-v2"
CONFIGURATION_INVENTORY_DOMAIN: Final = "encounter-continuum-c1-n0-configuration-row-inventory-v1"
PARTITION_INVENTORY_DOMAIN: Final = "encounter-continuum-c1-n0-partition-inventory-v1"
PROCESS_CONTRACT_SHA256: Final = "47ae856b647fa7be1119f68f684e36e253730bf2a87345ff634979d2893d4833"
GLOBAL_RUNNER_CONTRACT_SHA256: Final = (
    "27ccf524ba5b13c82b07376d57e632fa55573bb4f463182c16e9042832c1e91d"
)

PLAN_EXACT_KEYS: Final = (
    "claim_boundary",
    "entries",
    "runtime_closure",
    "schema",
    "shared_context",
    "shared_precommit_context_sha256",
    "slots",
    "status",
)
ENTRY_EXACT_KEYS: Final = (
    "entry_id",
    "input_authorities",
    "invocations",
    "method_selection",
    "output_slot_ids",
    "partition_path_bindings",
    "precommit_projection_sha256",
    "request_slot_id",
    "role",
    "runtime_role_id",
)
INVOCATION_EXACT_KEYS: Final = ("argv", "invocation_id", "process_contract_sha256")
SLOT_EXACT_KEYS: Final = (
    "kind",
    "lifecycle",
    "node_type",
    "ordinal",
    "path",
    "role",
    "schema",
    "slot_id",
)
PARTITION_BINDING_EXACT_KEYS: Final = (
    "configuration_index",
    "coordinate",
    "member_report_relative_path",
    "path",
    "sha256",
)
PIN_EXACT_KEYS: Final = ("path", "sha256")
SCHEMA_PIN_EXACT_KEYS: Final = ("path", "schema", "sha256")
REQUEST_EXACT_KEYS: Final = (
    "external_predecessor_commitment",
    "plan",
    "plan_entry_id",
    "role",
    "schema",
    "shared_precommit_context_sha256",
    "shared_replay_context_sha256",
    "status",
)
REQUEST_ROLE_EXACT_KEYS: Final = ("role_id", "role_name")

PLAN_CLAIM_BOUNDARY: Final = {
    "external_predecessor_commitment_present": False,
    "ordered_roles_8_10_replay_executed": False,
    "production_same_member_bridge_accepted": False,
    "release_eligible": False,
}
RUNTIME_CLAIM_BOUNDARY: Final = {
    "complete_host_runtime_image": False,
    "complete_report_local_and_declared_numerical_runtime_closure": True,
    "host_runtime_dependencies_byte_pinned": False,
    "legacy_scientific_backend_imported": False,
    "output_or_result_hash_present": False,
    "result_artifact_dependency_present": False,
}

SHARED_CONTEXT_EXACT_KEYS: Final = (
    "anti_vacuity_policy",
    "configuration",
    "configuration_row_inventory_sha256",
    "factorization",
    "ideal_formula",
    "member_identity_sha256",
    "member_spec",
    "method_parameter_registry",
    "partition_inventory_sha256",
    "reference_density",
    "role10_operation_model",
)
AUTHORITY_SCHEMAS: Final = {
    "anti_vacuity_policy": "encounter_continuum_c1_c2_n0_anti_vacuity_policy_v4_candidate",
    "configuration": "encounter_physical_configuration_family_control_free_v1",
    "factorization": "encounter_continuum_c1_factorization_source_v2_candidate",
    "ideal_formula": "encounter_continuum_c1_ideal_formula_source_v1",
    "killing_geometry": "encounter_physical_killing_geometry_source_v1",
    "member_spec": "encounter_continuum_c1_c2_n0_member_spec_v4_candidate",
    "method_parameter_registry": (
        "encounter_continuum_c1_c2_n0_method_parameter_registry_v4_candidate"
    ),
    "reference_density": "encounter_continuum_c1_reference_density_source_v1",
    "sealed_authentication_mirror": (
        "encounter_continuum_c1_n0_role10_sealed_authentication_mirror_v1_candidate"
    ),
}
AUTHORITY_SHA256: Final = {
    "anti_vacuity_policy": ("599252aa1a9fd1d65d9ff3d0faa1e21bb2609da96cca6b6fff1e61a89ebff196"),
    "configuration": "063913c7fbc2b706ba85a0e3f06005bad23a2292749817294cbf41f5cdce4084",
    "factorization": "1cf32a65081dc4f381daae45a556e0e26dc9411eb248cd99e555b754ffad3e26",
    "ideal_formula": "f31b637b659483102d787da7263cd45c72829b3fce3df2ff9100066dec94c2be",
    "killing_geometry": "5543f76031d731cb5bcf3e4cdf3bdabaffacb2053400e3015d6ab57906a27669",
    "member_spec": "b2982e4e2b0bac208f80472d0de959fa152a5494c895677d081836c482e5f2d5",
    "method_parameter_registry": (
        "e403a9576abb08d3ada884cd283cce29ce8f877b0e9843cc8d5b911c8c0b0ac5"
    ),
    "reference_density": "7b890d727ad0b229557de1841ae82befb8d8f83e79edc6b5348b277c3024e575",
    "sealed_authentication_mirror": (
        "1ba1b582c17e90ab19f04f1aefce1ea5cf9a9dad8cbcfcaed309314014d8dc51"
    ),
}
MEMBER_IDENTITY_SHA256: Final = "68c8f9eeaca5127e9fb49c4671731990869350b358c67632fb11513f26472193"
CONFIGURATION_ROW_INVENTORY_SHA256: Final = (
    "8da99e7910cac1f2ba6b69fb2d0ec52b21412abfa1d59c898462e138d82ebbb2"
)
PARTITION_INVENTORY_SHA256: Final = (
    "f3507f4eec07e216bd54bcf4486ab5cef1589511367f781174b89fdfe2e7b51f"
)

ROLE_ORDER: Final = (8, 9, 10)
ROLE_NAMES: Final = {
    8: "role8_raw_axis_formula_primitive",
    9: "role9_stationary_physical_integral",
    10: "role10_killing_factor_geometry",
}
REQUEST_SCHEMAS: Final = {
    8: "encounter_continuum_c1_n0_raw_axis_formula_request_v4",
    9: "encounter_continuum_c1_n0_stationary_integrals_request_v4",
    10: "encounter_continuum_c1_n0_killing_factor_geometry_request_v4",
}
NORMATIVE_INPUT_AUTHORITY_KEYS: Final = {
    8: (
        "anti_vacuity_policy",
        "configuration",
        "ideal_formula",
        "member_spec",
        "method_parameter_registry",
        "reference_density",
        "sealed_authentication_mirror",
    ),
    9: (
        "anti_vacuity_policy",
        "configuration",
        "ideal_formula",
        "member_spec",
        "method_parameter_registry",
        "reference_density",
        "sealed_authentication_mirror",
    ),
    10: (
        "anti_vacuity_policy",
        "configuration",
        "factorization",
        "ideal_formula",
        "killing_geometry",
        "member_spec",
        "method_parameter_registry",
        "sealed_authentication_mirror",
    ),
}
METHOD_PARAMETER_IDS: Final = {
    8: (
        "raw_flux_directed_mpfr_320_v2",
        "raw_flux_directed_mpfr_640_sentinel_v2",
        "raw_flux_binary64_decode_v2",
        "exact_fraction_expression_dag_v2",
    ),
    9: (
        "stationary_directed_mpfr_320_v2",
        "stationary_directed_mpfr_640_sentinel_v2",
        "exact_fraction_expression_dag_v2",
    ),
    10: (
        "killing_contact_profile_mpfr_192_v3",
        "killing_analytic_disk_area_mpfr_256_v3",
        "killing_source_independent_same_backend_verifier_v3",
        "killing_exact_contact_cell_classification_v3",
    ),
}
SOURCE_BASENAMES: Final = {
    8: {
        "producer_basename": "build_continuum_c1_n0_candidate_native_raw_axis_formula_v3.py",
        "verifier_basename": "validate_continuum_c1_n0_candidate_native_raw_axis_formula_v3.py",
    },
    9: {
        "producer_basename": "build_continuum_c1_n0_candidate_native_stationary_integrals_v3.py",
        "verifier_basename": "validate_continuum_c1_n0_candidate_native_stationary_integrals_v3.py",
    },
    10: {
        "producer_basename": "build_continuum_c1_n0_candidate_native_killing_factor_geometry_v3.py",
        "verifier_basename": "validate_continuum_c1_n0_candidate_native_killing_factor_geometry_v3.py",
    },
}

SLOT_TEMPLATES: Final = (
    {
        "kind": "request",
        "lifecycle": "future_request_after_commitment_then_immutable_input",
        "node_type": "file",
        "ordinal": 0,
        "role": 8,
        "schema": REQUEST_SCHEMAS[8],
        "slot_id": "role8_request",
    },
    {
        "kind": "artifact",
        "lifecycle": "must_be_absent_before_global_launch_atomic_no_replace_output",
        "node_type": "file",
        "ordinal": 1,
        "role": 8,
        "schema": "encounter_c1_n0_raw_axis_formula_primitive_source_v2",
        "slot_id": "role8_artifact",
    },
    {
        "kind": "validation_receipt",
        "lifecycle": "must_be_absent_before_global_launch_atomic_no_replace_output",
        "node_type": "file",
        "ordinal": 2,
        "role": 8,
        "schema": "encounter_c1_n0_raw_axis_formula_primitive_validation_receipt_v1",
        "slot_id": "role8_validation_receipt",
    },
    {
        "kind": "request",
        "lifecycle": "future_request_after_commitment_then_immutable_input",
        "node_type": "file",
        "ordinal": 3,
        "role": 9,
        "schema": REQUEST_SCHEMAS[9],
        "slot_id": "role9_request",
    },
    {
        "kind": "artifact",
        "lifecycle": "must_be_absent_before_global_launch_atomic_no_replace_output",
        "node_type": "file",
        "ordinal": 4,
        "role": 9,
        "schema": "encounter_c1_n0_stationary_physical_integral_source_v2",
        "slot_id": "role9_artifact",
    },
    {
        "kind": "validation_receipt",
        "lifecycle": "must_be_absent_before_global_launch_atomic_no_replace_output",
        "node_type": "file",
        "ordinal": 5,
        "role": 9,
        "schema": "encounter_c1_n0_stationary_physical_integral_validation_receipt_v1",
        "slot_id": "role9_validation_receipt",
    },
    {
        "kind": "request",
        "lifecycle": "future_request_after_commitment_then_immutable_input",
        "node_type": "file",
        "ordinal": 6,
        "role": 10,
        "schema": REQUEST_SCHEMAS[10],
        "slot_id": "role10_request",
    },
    {
        "kind": "artifact",
        "lifecycle": "must_be_absent_before_global_launch_atomic_no_replace_output",
        "node_type": "directory",
        "ordinal": 7,
        "role": 10,
        "schema": "encounter_c1_n0_killing_factor_geometry_source_v4",
        "slot_id": "role10_artifact_directory",
    },
    {
        "kind": "semantic_receipt",
        "lifecycle": "must_be_absent_before_global_launch_atomic_no_replace_output",
        "node_type": "file",
        "ordinal": 8,
        "role": 10,
        "schema": "encounter_c1_n0_killing_factor_geometry_semantic_receipt_v2",
        "slot_id": "role10_semantic_receipt",
    },
    {
        "kind": "outer_validation_receipt",
        "lifecycle": "must_be_absent_before_global_launch_atomic_no_replace_output",
        "node_type": "file",
        "ordinal": 9,
        "role": 10,
        "schema": "encounter_c1_n0_killing_factor_geometry_validation_receipt_v3",
        "slot_id": "role10_outer_validation_receipt",
    },
)
REQUEST_SLOT_IDS: Final = {
    8: "role8_request",
    9: "role9_request",
    10: "role10_request",
}
OUTPUT_SLOT_IDS: Final = {
    8: ("role8_artifact", "role8_validation_receipt"),
    9: ("role9_artifact", "role9_validation_receipt"),
    10: (
        "role10_artifact_directory",
        "role10_semantic_receipt",
        "role10_outer_validation_receipt",
    ),
}
OUTPUT_SLOT_ID_SET: Final = (
    "role8_artifact",
    "role8_validation_receipt",
    "role9_artifact",
    "role9_validation_receipt",
    "role10_artifact_directory",
    "role10_semantic_receipt",
    "role10_outer_validation_receipt",
)
COORDINATE_ORDER: Final = ("midpoint", "relative_parallel", "relative_perpendicular")
PARTITION_BINDING_COUNT: Final = 36

INVOCATION_TEMPLATES: Final = {
    8: {
        "producer": {
            "invocation_id": "role8_raw_axis_formula_producer_v3",
            "argv": (
                "{role8_pinned_python}",
                "-I",
                "-B",
                "{role8_pinned_producer}",
                "--request",
                "{slot:role8_request}",
                "--output",
                "{slot:role8_artifact}",
            ),
        },
        "verifier": {
            "invocation_id": "role8_raw_axis_formula_verifier_v3",
            "argv": (
                "{role8_pinned_python}",
                "-I",
                "-B",
                "{role8_pinned_verifier}",
                "--request",
                "{slot:role8_request}",
                "--output",
                "{slot:role8_artifact}",
                "--receipt",
                "{slot:role8_validation_receipt}",
            ),
        },
    },
    9: {
        "producer": {
            "invocation_id": "role9_stationary_integrals_producer_v3",
            "argv": (
                "{role9_pinned_python}",
                "-I",
                "-B",
                "{role9_pinned_producer}",
                "--request",
                "{slot:role9_request}",
                "--output",
                "{slot:role9_artifact}",
            ),
        },
        "verifier": {
            "invocation_id": "role9_stationary_integrals_verifier_v3",
            "argv": (
                "{role9_pinned_python}",
                "-I",
                "-B",
                "{role9_pinned_verifier}",
                "--request",
                "{slot:role9_request}",
                "--output",
                "{slot:role9_artifact}",
                "--receipt",
                "{slot:role9_validation_receipt}",
            ),
        },
    },
    10: {
        "transaction_orchestrator": {
            "invocation_id": "role10_killing_geometry_transaction_orchestrator_v3",
            "argv": (
                "{role10_pinned_python}",
                "-I",
                "-B",
                "{role10_pinned_verifier}",
                "--request",
                "{slot:role10_request}",
                "--output",
                "{slot:role10_artifact_directory}",
                "--semantic-receipt",
                "{slot:role10_semantic_receipt}",
                "--receipt",
                "{slot:role10_outer_validation_receipt}",
            ),
        }
    },
}

RUNTIME_EXACT_KEYS: Final = (
    "claim_boundary",
    "global_runner",
    "host_runtime_trust_boundary",
    "process_contract",
    "roles",
    "schema",
    "status",
)
RUNTIME_ROLE_EXACT_KEYS: Final = (
    "allowed_shared_protocol",
    "code_inputs",
    "native_libraries",
    "native_runtime",
    "python_executable",
    "python_imports",
    "report_local_dependencies",
    "resolved_python_dependencies",
    "role_id",
    "role_name",
)
RUNTIME_CODE_INPUT_EXACT_KEYS: Final = ("producer", "verifier")
RUNTIME_SIDE_EXACT_KEYS: Final = ("producer", "verifier")
NATIVE_LIBRARY_ROLES: Final = ("gmpy2_extension", "libgmp", "libmpfr", "libmpc")
GLOBAL_RUNNER_BASENAME: Final = "execute_continuum_c1_n0_roles_8_10_replay_v2.py"
GLOBAL_RUNNER_ID: Final = "roles_8_10_global_replay_runner_v2"
GLOBAL_RUNNER_EXACT_KEYS: Final = (
    "code_input",
    "python_executable",
    "python_imports",
    "python_runtime",
    "report_local_dependencies",
    "resolved_python_dependencies",
    "runner_contract_sha256",
    "runner_id",
)
HOST_RUNTIME_EXACT_KEYS: Final = (
    "byte_complete",
    "darwin_kernel_release",
    "machine",
    "macos_build_version",
    "scope",
    "status",
)
HOST_RUNTIME_SCOPE: Final = (
    "CPython_builtin_and_frozen_module_carrier_bytes_not_separately_pinned_"
    "beyond_the_Python_executable_ABI_and_version",
    "non_report_dynamic_dependencies_of_the_Python_executable_and_stdlib_or_"
    "prefix_extension_modules",
    "macOS_dyld_shared_cache_usr_lib_and_System_frameworks",
)
HOST_RUNTIME_STATUS: Final = "DECLARED_HOST_RUNTIME_TRUST_BOUNDARY_NOT_BYTE_COMPLETE"

BUNDLE_EXACT_KEYS: Final = (
    "claim_boundary",
    "member_spec",
    "method_parameter_registry",
    "operation_model",
    "replay_plan",
    "runtime_closure",
    "schema",
    "shared_precommit_context_sha256",
    "status",
)
BUNDLE_PIN_SCHEMAS: Final = {
    "member_spec": AUTHORITY_SCHEMAS["member_spec"],
    "method_parameter_registry": AUTHORITY_SCHEMAS["method_parameter_registry"],
    "operation_model": OPERATION_MODEL_SCHEMA,
    "replay_plan": PLAN_SCHEMA,
    "runtime_closure": RUNTIME_CLOSURE_SCHEMA,
}

FORBIDDEN_RESULT_KEY_FRAGMENTS: Final = (
    "acceptance",
    "artifact_digest",
    "artifact_sha",
    "classification_digest",
    "expected_output",
    "expected_result",
    "observed_output",
    "observed_result",
    "output_digest",
    "output_sha",
    "pass_receipt",
    "production_result",
    "receipt_digest",
    "receipt_sha",
    "result_artifact",
    "result_digest",
    "result_receipt",
    "result_sha",
    "role8_result",
    "role9_result",
    "role10_result",
)
FORBIDDEN_PRECOMMIT_FIELDS: Final = (
    "acceptance_bit",
    "artifact_sha256",
    "budget",
    "concrete_V",
    "control_weights",
    "discrete_diagonal_k",
    "independent_trust_domain_receipt_hash",
    "observed_output_digest",
    "observed_result",
    "reconstructed_K",
    "result_summary",
    "role10_result_digest",
    "tree_digest",
)
FORBIDDEN_SCIENTIFIC_PAYLOADS: Final = (
    "384_bit_oracle_interval_values",
    "512_bit_sentinel_interval_values",
    "dense_V",
    "dense_k",
    "dense_K",
    "pi_h",
    "role8_result",
    "role9_result",
)
FORBIDDEN_LEGACY_IMPORT_PREFIXES: Final = ("numpy", "rate_defined_tensor_f0", "scipy")
FORBIDDEN_LEGACY_RESULT_BASENAMES: Final = (
    "continuum_c2_killing_geometry_production_binding_v1.json",
    "physical_production_killing_geometry_two_repeat_outer_receipt_v1.json",
    "physical_production_killing_geometry_v1",
)
