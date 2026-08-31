#!/usr/bin/env python3
"""Main tests for the independently reconstructed member-v4 candidate."""

from __future__ import annotations

import ast
import copy
import importlib.util
import json
import os
import pathlib
import stat
import tempfile
import threading
import unittest
from typing import Any
from unittest import mock

HERE = pathlib.Path(__file__).resolve().parent
BUILD_PATH = HERE / "build_continuum_c1_c2_n0_member_spec_v4_candidate.py"
VALIDATE_PATH = HERE / "validate_continuum_c1_c2_n0_member_spec_v4_candidate.py"


def load_module(name: str, path: pathlib.Path) -> Any:
    specification = importlib.util.spec_from_file_location(name, path)
    if specification is None or specification.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


B = load_module("member_v4_builder_main_tests", BUILD_PATH)
V = load_module("member_v4_validator_main_tests", VALIDATE_PATH)


class MemberV4MainTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.candidate = B.build_candidate()
        cls.validator_candidate = V.expected_candidate()

    def test_known_identity_is_independently_reconstructed(self) -> None:
        self.assertEqual(
            self.candidate["member_identity_sha256"],
            "68c8f9eeaca5127e9fb49c4671731990869350b358c67632fb11513f26472193",
        )
        identity = {
            "configuration_order": self.candidate["configuration_order"],
            "configuration_semantic_ids": self.candidate["configuration_semantic_ids"],
            "member_semantics": self.candidate["member_semantics"],
            "n0_sequence_bindings": self.candidate["n0_sequence_bindings"],
            "role_bindings_1_through_4": self.candidate["role_bindings"],
        }
        self.assertEqual(
            B.domain_digest(B.IDENTITY_DOMAIN, identity),
            self.candidate["member_identity_sha256"],
        )

    def test_builder_and_source_separated_validator_match_exactly(self) -> None:
        self.assertEqual(
            B.canonical_bytes(self.candidate),
            V.encode_canonical(self.validator_candidate),
        )

    def test_validator_has_no_builder_import_or_execution(self) -> None:
        source = VALIDATE_PATH.read_text(encoding="utf-8")
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                names = [alias.name for alias in node.names]
                self.assertFalse(any("build_continuum" in name for name in names))
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                self.assertNotIn(node.func.id, {"eval", "exec"})
        self.assertNotIn("import build_continuum", source)

    def test_schema_status_and_all_claims_are_nonpromoting(self) -> None:
        self.assertEqual(self.candidate["schema"], B.SCHEMA)
        self.assertEqual(self.candidate["status"], B.STATUS)
        self.assertEqual(set(self.candidate["claim_boundary"]), set(B.CLAIM_KEYS))
        self.assertTrue(all(value is False for value in self.candidate["claim_boundary"].values()))

    def test_exact_twelve_rows_thirty_six_axes_and_counts(self) -> None:
        rows = self.candidate["n0_sequence_bindings"]
        self.assertEqual(len(rows), 12)
        self.assertEqual(sum(len(row["n0_axes"]) for row in rows), 36)
        self.assertEqual(self.candidate["reconstruction_counts"], B.EXPECTED_COUNTS)
        self.assertEqual(
            self.candidate["identity_properties"]["alignment_counts"],
            B.EXPECTED_ALIGNMENT_COUNTS,
        )

    def test_every_row_and_axis_has_exact_index_and_semantic_binding(self) -> None:
        for index, row in enumerate(self.candidate["n0_sequence_bindings"]):
            semantic = self.candidate["configuration_semantic_ids"][index]
            self.assertIs(type(row["configuration_index"]), int)
            self.assertIs(type(row["sequence_source_row_index"]), int)
            self.assertEqual(row["configuration_index"], index)
            self.assertEqual(row["sequence_source_row_index"], index)
            self.assertEqual(row["authority_label"], semantic["authority_label"])
            self.assertEqual(row["refinement_family_id"], semantic["refinement_family_id"])
            self.assertEqual(row["refinement_member_id"], semantic["refinement_member_id"])
            for coordinate, axis in zip(B.AXIS_ORDER, row["n0_axes"], strict=True):
                self.assertEqual(axis["coordinate"], coordinate)
                self.assertEqual(axis["refinement_family_id"], semantic["refinement_family_id"])
                self.assertEqual(axis["refinement_member_id"], semantic["refinement_member_id"])

    def test_role_bindings_are_exactly_roles_one_through_four(self) -> None:
        roles = self.candidate["role_bindings"]
        self.assertEqual(
            set(roles),
            {
                "configuration_source",
                "factorization_source",
                "ideal_formula_source",
                "reference_density_source",
            },
        )
        self.assertEqual(roles["factorization_source"]["path"], B.FACTORIZATION_RELATIVE)
        self.assertEqual(roles["factorization_source"]["sha256"], B.FACTORIZATION_SHA256)
        self.assertNotIn("registry", json.dumps(self.candidate).lower())

    def test_factorization_v1_fallback_constant_is_rejected(self) -> None:
        with mock.patch.object(
            B,
            "FACTORIZATION_RELATIVE",
            B.HISTORICAL_FACTORIZATION_V1_RELATIVE,
        ):
            with self.assertRaisesRegex(B.MemberBuildError, "v1 fallback"):
                B.validate_primary_sources()

    def test_identity_payload_uses_complete_member_semantics(self) -> None:
        complete = copy.deepcopy(self.candidate["member_semantics"])
        truncated = {"scalar_convention": complete["scalar_convention"]}
        identity = {
            "configuration_order": self.candidate["configuration_order"],
            "configuration_semantic_ids": self.candidate["configuration_semantic_ids"],
            "member_semantics": truncated,
            "n0_sequence_bindings": self.candidate["n0_sequence_bindings"],
            "role_bindings_1_through_4": self.candidate["role_bindings"],
        }
        self.assertNotEqual(
            B.domain_digest(B.IDENTITY_DOMAIN, identity),
            self.candidate["member_identity_sha256"],
        )

    def test_identity_excludes_registry_even_if_added_outside_payload(self) -> None:
        mutated = copy.deepcopy(self.candidate)
        mutated["method_parameter_registry"] = {"path": "forbidden"}
        self.assertNotEqual(B.canonical_bytes(mutated), B.canonical_bytes(self.candidate))
        self.assertNotIn("method_parameter_registry", self.candidate)

    def test_bool_index_is_rejected(self) -> None:
        (
            v3,
            reference,
            _ideal,
            _factor,
            configuration,
            refinement,
            bundle,
        ) = B.validate_primary_sources()
        refinement = copy.deepcopy(refinement)
        refinement["sequences"][0]["source_row_index"] = False
        with self.assertRaisesRegex(B.MemberBuildError, "exact integer"):
            B.reconstruct_bindings(v3, reference, configuration, refinement, bundle)

    def test_bool_state_count_is_rejected(self) -> None:
        (
            v3,
            reference,
            _ideal,
            _factor,
            configuration,
            refinement,
            bundle,
        ) = B.validate_primary_sources()
        configuration = copy.deepcopy(configuration)
        configuration["configurations"][0]["expected_states"] = True
        with self.assertRaisesRegex(B.MemberBuildError, "state-count"):
            B.reconstruct_bindings(v3, reference, configuration, refinement, bundle)

    def test_empty_semantic_identifier_is_rejected(self) -> None:
        (
            v3,
            reference,
            _ideal,
            _factor,
            configuration,
            refinement,
            bundle,
        ) = B.validate_primary_sources()
        v3 = copy.deepcopy(v3)
        v3["configuration_semantic_ids"][0]["refinement_member_id"] = ""
        with self.assertRaisesRegex(B.MemberBuildError, "semantic-id drift"):
            B.reconstruct_bindings(v3, reference, configuration, refinement, bundle)

    def test_row_reordering_is_rejected(self) -> None:
        (
            v3,
            reference,
            _ideal,
            _factor,
            configuration,
            refinement,
            bundle,
        ) = B.validate_primary_sources()
        configuration = copy.deepcopy(configuration)
        configuration["configurations"][0], configuration["configurations"][1] = (
            configuration["configurations"][1],
            configuration["configurations"][0],
        )
        with self.assertRaisesRegex(B.MemberBuildError, "label drift"):
            B.reconstruct_bindings(v3, reference, configuration, refinement, bundle)

    def test_partition_spacing_semantic_drift_is_rejected(self) -> None:
        (
            v3,
            reference,
            _ideal,
            _factor,
            configuration,
            refinement,
            bundle,
        ) = B.validate_primary_sources()
        refinement = copy.deepcopy(refinement)
        refinement["sequences"][0]["axes"][0]["spacing_h0_exact"] = "1/1"
        with self.assertRaisesRegex(B.MemberBuildError, "spacing"):
            B.reconstruct_bindings(v3, reference, configuration, refinement, bundle)

    def test_noncanonical_rational_is_rejected(self) -> None:
        self.assertRaises(B.MemberBuildError, B.rational, "2/2")
        self.assertRaises(B.MemberBuildError, B.rational, True)
        self.assertRaises(B.MemberBuildError, B.rational, "1/0")

    def test_canonical_parser_rejects_duplicate_float_nonascii_and_trailing_space(self) -> None:
        bad_payloads = (
            b'{"a": 1, "a": 2}\n',
            b'{"a": 1.5}\n',
            '{"a": "é"}\n'.encode(),
            b'{\n  "a": 1\n} \n',
        )
        for payload in bad_payloads:
            with self.subTest(payload=payload):
                with self.assertRaises(B.MemberBuildError):
                    B.parse_canonical(payload, "bad")

    def test_canonical_encoder_rejects_float_deep_tree_and_huge_integer(self) -> None:
        with self.assertRaises(B.MemberBuildError):
            B.canonical_bytes({"x": 0.5})
        deep: Any = None
        for _ in range(B.MAX_JSON_DEPTH + 2):
            deep = [deep]
        with self.assertRaises(B.MemberBuildError):
            B.canonical_bytes({"x": deep})
        with self.assertRaises(B.MemberBuildError):
            B.canonical_bytes({"x": 1 << 300})

    def test_safe_relative_path_rejects_escape_absolute_and_backslash(self) -> None:
        for value in ("../x", "/tmp/x", "a/./b", "a\\b", "", True):
            with self.subTest(value=value):
                with self.assertRaises(B.MemberBuildError):
                    B.safe_relative(value)

    def test_normative_reader_requires_exact_0444_and_nlink_one(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = pathlib.Path(directory) / "source.json"
            path.write_bytes(b"{}\n")
            for mode in (0o400, 0o555, 0o644):
                os.chmod(path, mode)
                with self.subTest(mode=oct(mode)):
                    with self.assertRaises(B.MemberBuildError):
                        B.read_regular(path, "mode test", normative=True)
            os.chmod(path, 0o444)
            hardlink = pathlib.Path(directory) / "hardlink.json"
            os.link(path, hardlink)
            with self.assertRaises(B.MemberBuildError):
                B.read_regular(path, "hardlink test", normative=True)

    def test_normative_reader_rejects_symlink_leaf_and_component(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            real = root / "real"
            real.mkdir()
            source = real / "source.json"
            source.write_bytes(b"{}\n")
            os.chmod(source, 0o444)
            leaf_link = real / "leaf.json"
            leaf_link.symlink_to(source)
            with self.assertRaises((B.MemberBuildError, OSError)):
                B.read_regular(leaf_link, "leaf symlink", normative=True)
            component_link = root / "component"
            component_link.symlink_to(real, target_is_directory=True)
            with self.assertRaises((B.MemberBuildError, OSError)):
                B.read_regular(component_link / "source.json", "component symlink", normative=True)

    def test_live_reopen_or_parent_drift_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = pathlib.Path(os.path.realpath(directory)) / "source.json"
            path.write_bytes(b"{}\n")
            os.chmod(path, 0o444)
            with mock.patch.object(
                B,
                "verify_anchored_parent",
                side_effect=B.MemberBuildError("synthetic parent drift"),
            ):
                with self.assertRaisesRegex(B.MemberBuildError, "parent drift"):
                    B.read_regular(path, "TOCTOU test", normative=True)

    def test_publication_is_no_replace_0444_single_link_and_canonical(self) -> None:
        payload = B.canonical_bytes({"schema": "publication_test"})
        with tempfile.TemporaryDirectory() as directory:
            output = pathlib.Path(os.path.realpath(directory)) / "candidate.json"
            B.publish_no_replace(output, payload)
            observed = output.stat()
            self.assertEqual(stat.S_IMODE(observed.st_mode), 0o444)
            self.assertEqual(observed.st_nlink, 1)
            self.assertEqual(output.read_bytes(), payload)
            with self.assertRaisesRegex(B.MemberBuildError, "refusing to replace"):
                B.publish_no_replace(output, payload)

    def test_stage_is_created_0400_before_final_fchmod(self) -> None:
        payload = B.canonical_bytes({"schema": "stage_mode_test"})
        modes: list[int] = []
        original = B._STAGE_OPEN

        def capture(
            leaf: str,
            flags: int,
            mode: int,
            *,
            dir_fd: int,
        ) -> int:
            modes.append(mode)
            return original(leaf, flags, mode, dir_fd=dir_fd)

        with tempfile.TemporaryDirectory() as directory:
            output = pathlib.Path(os.path.realpath(directory)) / "candidate.json"
            with mock.patch.object(B, "_STAGE_OPEN", capture):
                B.publish_no_replace(output, payload)
            self.assertEqual(modes, [0o400])
            self.assertEqual(stat.S_IMODE(output.stat().st_mode), 0o444)

    def test_stage_creation_baseexception_leaves_no_file_or_thread(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(os.path.realpath(directory))
            output = root / "candidate.json"
            before = {
                thread.ident
                for thread in threading.enumerate()
                if thread.name == "member-v4-stage-create"
            }
            with mock.patch.object(B, "_STAGE_OPEN", side_effect=KeyboardInterrupt()):
                with self.assertRaises(KeyboardInterrupt):
                    B.publish_no_replace(output, b"{}\n")
            after = {
                thread.ident
                for thread in threading.enumerate()
                if thread.name == "member-v4-stage-create"
            }
            self.assertEqual(before, after)
            self.assertEqual(list(root.iterdir()), [])

    def test_candidate_bytes_are_ascii_canonical(self) -> None:
        payload = B.canonical_bytes(self.candidate)
        self.assertEqual(payload.decode("ascii").encode("ascii"), payload)
        self.assertEqual(B.parse_canonical(payload, "candidate"), self.candidate)


if __name__ == "__main__":
    unittest.main()
