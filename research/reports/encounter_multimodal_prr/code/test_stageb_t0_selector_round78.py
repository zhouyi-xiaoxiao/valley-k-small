"""Round-81 regressions for every result-blind Round-78 package attack.

Only package/protocol bytes and hand-built synthetic fixtures are used.  This
test never opens or imports a Stage-A/Stage-B scientific object, producer,
manifest, result, FV/off-lattice implementation, or mesh output.
"""

# ruff: noqa: E402 -- exact bootstrap aliases must exist before fixture import
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

gmpy2 = sys.modules.get("gmpy2")
verified_loader = sys.modules.get("positive_b_stage_b_t0_verified_loader")
selector = sys.modules.get("positive_b_stage_b_t1_selector_v5")
if gmpy2 is None or verified_loader is None or selector is None:
    raise RuntimeError("tests require the isolated verified-selector bootstrap")
import test_positive_b_stage_b_t1_selector_v5 as fixtures

CODE_DIR = Path(__file__).resolve().parent
REPORT_ROOT = CODE_DIR.parent
EXPECTED_IMPLEMENTATION_SHA256 = "c7344bb8d6818f609c57614dd0d500c75fcc2229606865b1d9a4d05bc94cecfc"


def synthetic_attestation_bytes(runtime_site_root: Path | None = None) -> bytes:
    if runtime_site_root is None:
        runtime_site_root = Path(gmpy2.__file__).resolve().parent.parent
    files = {
        role: {
            "path": relative,
            "sha256": hashlib.sha256((REPORT_ROOT / relative).read_bytes()).hexdigest(),
        }
        for role, relative in verified_loader.COMMON_ATTESTED_PATHS.items()
    }
    record = {
        "authorization": selector.AUTHORIZATION_NONE,
        "files": files,
        "runtime_site_root": str(runtime_site_root),
        "schema": verified_loader.SYNTHETIC_ATTESTATION_SCHEMA,
        "status": "NON-PROMOTABLE-SYNTHETIC-TEST",
        "trust_contract": verified_loader._expected_trust_contract(),
    }
    return json.dumps(record, sort_keys=True, indent=2).encode("ascii") + b"\n"


class Round81ImportAndRuntimeRepairs(unittest.TestCase):
    def test_legacy_name_is_a_fail_closed_tombstone(self) -> None:
        completed = subprocess.run(
            [sys.executable, "-c", "import positive_b_stage_b_t0_selector"],
            check=False,
            capture_output=True,
            env={**os.environ, "PYTHONPATH": str(CODE_DIR)},
            text=True,
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("is retired", completed.stderr)

    def test_direct_import_holds_before_fake_legacy_or_critical_modules_execute(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            temporary_root = Path(temporary)
            fake = temporary_root / "positive_b_stage_b_t0_selector.py"
            fake.write_text(
                'raise RuntimeError("forged legacy module was imported")\n',
                encoding="utf-8",
            )
            critical_sentinels: list[Path] = []
            for module_name in ("ctypes", "platform", "sysconfig"):
                sentinel = temporary_root / f"forged-{module_name}-executed"
                critical_sentinels.append(sentinel)
                (temporary_root / f"{module_name}.py").write_text(
                    "from pathlib import Path\n"
                    f"Path({str(sentinel)!r}).write_text('executed')\n"
                    f"raise RuntimeError('forged {module_name} was imported')\n",
                    encoding="utf-8",
                )
            environment = os.environ.copy()
            environment["PYTHONPATH"] = os.pathsep.join((temporary, str(CODE_DIR)))
            command = (
                "import sys,types; "
                "m=types.ModuleType('positive_b_stage_b_t0_selector'); "
                "m.select_saved_controls_bytes=lambda _:b'forged'; "
                "sys.modules['positive_b_stage_b_t0_selector']=m; "
                "import positive_b_stage_b_t1_selector_v5 as s; "
                "print(s.__file__); print(s.exp_rn(1.0).hex())"
            )
            completed = subprocess.run(
                [sys.executable, "-c", command],
                check=False,
                capture_output=True,
                env=environment,
                text=True,
            )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("requires the isolated verified loader", completed.stderr)
        self.assertNotIn("forged legacy module was imported", completed.stderr)
        self.assertTrue(all(not sentinel.exists() for sentinel in critical_sentinels))

    def test_descriptor_loader_ignores_fake_v5_pythonpath(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            temporary_root = Path(temporary).resolve()
            fake_v5 = temporary_root / selector.IMPLEMENTATION_NAME
            fake_v5.write_text(
                "def exp_rn(_value): return 1.0\n",
                encoding="utf-8",
            )
            sentinel = temporary_root / "sitecustomize-executed"
            (temporary_root / "sitecustomize.py").write_text(
                f"from pathlib import Path\nPath({str(sentinel)!r}).write_text('executed')\n",
                encoding="utf-8",
            )
            environment = os.environ.copy()
            environment["PYTHONPATH"] = temporary
            loader_path = CODE_DIR / "positive_b_stage_b_t0_verified_loader.py"
            attestation_path = temporary_root / "synthetic-external-attestation.json"
            attestation_bytes = synthetic_attestation_bytes()
            attestation_path.write_bytes(attestation_bytes)
            attestation_sha256 = hashlib.sha256(attestation_bytes).hexdigest()
            command = (
                "import hashlib,importlib.util,json,pathlib; "
                f"a=pathlib.Path({str(attestation_path)!r}).read_bytes(); "
                f"assert hashlib.sha256(a).hexdigest()=={attestation_sha256!r}; "
                "d=json.loads(a); "
                f"p={str(loader_path)!r}; "
                "assert hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()=="
                "d['files']['loader']['sha256']; "
                "q=importlib.util.spec_from_file_location('exact_round81_loader',p); "
                "m=importlib.util.module_from_spec(q); q.loader.exec_module(m); "
                f"s=m.load_frozen_selector({str(attestation_path)!r},{attestation_sha256!r}); "
                "print(s.__file__); print(s.exp_rn(1.0).hex())"
            )
            completed = subprocess.run(
                [sys.executable, "-I", "-S", "-c", command],
                check=False,
                capture_output=True,
                env=environment,
                text=True,
            )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(Path(completed.stdout.splitlines()[0]).name, selector.IMPLEMENTATION_NAME)
        self.assertEqual(completed.stdout.splitlines()[1], "0x1.5bf0a8b145769p+1")
        self.assertFalse(sentinel.exists(), "sitecustomize executed before the trust boundary")

    def test_hostile_top_level_runtime_modules_have_zero_execution(self) -> None:
        authentic_site = Path(gmpy2.__file__).resolve().parent.parent
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            runtime_site = root / "hostile-site"
            runtime_site.mkdir()
            shutil.copytree(authentic_site / "gmpy2", runtime_site / "gmpy2")
            shutil.copytree(authentic_site / "gmpy2.libs", runtime_site / "gmpy2.libs")
            sentinels: list[Path] = []
            for module_name in ("platform", "sysconfig", "ctypes"):
                sentinel = root / f"{module_name}-executed"
                sentinels.append(sentinel)
                (runtime_site / f"{module_name}.py").write_text(
                    f"from pathlib import Path\nPath({str(sentinel)!r}).write_text('executed')\n"
                    "raise RuntimeError('hostile runtime-root module executed')\n",
                    encoding="utf-8",
                )
            sibling_sentinel = root / "sibling-executed"
            sibling = runtime_site / "sibling_package"
            sibling.mkdir()
            (sibling / "__init__.py").write_text(
                f"from pathlib import Path\nPath({str(sibling_sentinel)!r}).write_text('executed')\n",
                encoding="utf-8",
            )
            sentinels.append(sibling_sentinel)
            attestation_path = root / "synthetic-attestation.json"
            attestation = synthetic_attestation_bytes(runtime_site)
            attestation_path.write_bytes(attestation)
            attestation_sha256 = hashlib.sha256(attestation).hexdigest()
            loader_path = CODE_DIR / "positive_b_stage_b_t0_verified_loader.py"
            command = (
                "import importlib.util; "
                f"p={str(loader_path)!r}; "
                "q=importlib.util.spec_from_file_location('hostile_root_loader',p); "
                "m=importlib.util.module_from_spec(q); q.loader.exec_module(m); "
                f"s=m.load_frozen_selector({str(attestation_path)!r},{attestation_sha256!r}); "
                "print(s.exp_rn(1.0).hex())"
            )
            completed = subprocess.run(
                [sys.executable, "-I", "-S", "-c", command],
                check=False,
                capture_output=True,
                text=True,
            )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(completed.stdout.strip(), "0x1.5bf0a8b145769p+1")
        self.assertTrue(all(not sentinel.exists() for sentinel in sentinels))

    def test_extra_gmpy2_package_file_holds_before_package_execution(self) -> None:
        authentic_site = Path(gmpy2.__file__).resolve().parent.parent
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            runtime_site = root / "hostile-site"
            runtime_site.mkdir()
            shutil.copytree(authentic_site / "gmpy2", runtime_site / "gmpy2")
            shutil.copytree(authentic_site / "gmpy2.libs", runtime_site / "gmpy2.libs")
            sentinel = root / "extra-package-file-executed"
            (runtime_site / "gmpy2" / "hostile.py").write_text(
                f"from pathlib import Path\nPath({str(sentinel)!r}).write_text('executed')\n",
                encoding="utf-8",
            )
            attestation_path = root / "synthetic-attestation.json"
            attestation = synthetic_attestation_bytes(runtime_site)
            attestation_path.write_bytes(attestation)
            attestation_sha256 = hashlib.sha256(attestation).hexdigest()
            loader_path = CODE_DIR / "positive_b_stage_b_t0_verified_loader.py"
            command = (
                "import importlib.util; "
                f"p={str(loader_path)!r}; "
                "q=importlib.util.spec_from_file_location('extra_file_loader',p); "
                "m=importlib.util.module_from_spec(q); q.loader.exec_module(m); "
                f"m.load_frozen_selector({str(attestation_path)!r},{attestation_sha256!r})"
            )
            completed = subprocess.run(
                [sys.executable, "-I", "-S", "-c", command],
                check=False,
                capture_output=True,
                text=True,
            )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("gmpy2 package exact-file closure drift", completed.stderr)
        self.assertFalse(sentinel.exists())

    def test_nonisolated_loader_entry_is_hold(self) -> None:
        loader_path = CODE_DIR / "positive_b_stage_b_t0_verified_loader.py"
        dummy_attestation = CODE_DIR / "positive_b_stage_b_t0_runtime_lock_v2.json"
        command = (
            "import importlib.util; "
            f"p={str(loader_path)!r}; "
            "q=importlib.util.spec_from_file_location('nonisolated_loader',p); "
            "m=importlib.util.module_from_spec(q); q.loader.exec_module(m); "
            f"m.load_frozen_selector({str(dummy_attestation)!r},{'1' * 64!r})"
        )
        completed = subprocess.run(
            [sys.executable, "-c", command],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("python -I -S isolation", completed.stderr)

    def test_native_loader_environment_is_rejected_before_runtime_import(self) -> None:
        loader_path = CODE_DIR / "positive_b_stage_b_t0_verified_loader.py"
        dummy_attestation = CODE_DIR / "positive_b_stage_b_t0_runtime_lock_v2.json"
        command = (
            "import importlib.util; "
            f"p={str(loader_path)!r}; "
            "q=importlib.util.spec_from_file_location('injected_loader',p); "
            "m=importlib.util.module_from_spec(q); q.loader.exec_module(m); "
            f"m.load_frozen_selector({str(dummy_attestation)!r},{'1' * 64!r})"
        )
        environment = os.environ.copy()
        environment["DYLD_LIBRARY_PATH"] = "/tmp/round81-forbidden"
        completed = subprocess.run(
            [sys.executable, "-I", "-S", "-c", command],
            check=False,
            capture_output=True,
            env=environment,
            text=True,
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("native-loader injection environment is forbidden", completed.stderr)

    def test_preloaded_critical_stdlib_names_hold_before_source_execution(self) -> None:
        loader_path = CODE_DIR / "positive_b_stage_b_t0_verified_loader.py"
        dummy_attestation = CODE_DIR / "positive_b_stage_b_t0_runtime_lock_v2.json"
        for module_name in ("ctypes", "platform", "sysconfig"):
            with self.subTest(module_name=module_name):
                command = (
                    "import importlib.util,sys,types; "
                    f"sys.modules[{module_name!r}]=types.ModuleType({module_name!r}); "
                    f"p={str(loader_path)!r}; "
                    "q=importlib.util.spec_from_file_location('preload_guard_loader',p); "
                    "m=importlib.util.module_from_spec(q); q.loader.exec_module(m); "
                    f"m.load_frozen_selector({str(dummy_attestation)!r},{'1' * 64!r})"
                )
                completed = subprocess.run(
                    [sys.executable, "-I", "-S", "-c", command],
                    check=False,
                    capture_output=True,
                    text=True,
                )
                self.assertNotEqual(completed.returncode, 0)
                self.assertIn(
                    "critical selector stdlib module was preloaded",
                    completed.stderr,
                )

    def test_postload_critical_stdlib_substitution_holds(self) -> None:
        for module_name in ("ctypes", "platform", "sysconfig"):
            with (
                self.subTest(module_name=module_name),
                mock.patch.dict(sys.modules, {module_name: object()}),
                self.assertRaisesRegex(selector.Hold, "critical stdlib identity drift"),
            ):
                selector.verify_mpfr_runtime()
        selector.verify_mpfr_runtime()

    def test_isolated_loader_rejects_wrong_external_pin_before_runtime_import(self) -> None:
        loader_path = CODE_DIR / "positive_b_stage_b_t0_verified_loader.py"
        dummy_attestation = CODE_DIR / "positive_b_stage_b_t0_runtime_lock_v2.json"
        command = (
            "import importlib.util; "
            f"p={str(loader_path)!r}; "
            "q=importlib.util.spec_from_file_location('exact_round81_loader_bad_pin',p); "
            "m=importlib.util.module_from_spec(q); q.loader.exec_module(m); "
            f"m.load_frozen_selector({str(dummy_attestation)!r},{'0' * 64!r})"
        )
        completed = subprocess.run(
            [sys.executable, "-I", "-S", "-c", command],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("external T0 attestation SHA-256 mismatch", completed.stderr)

    def test_fake_gmpy2_wrapper_override_is_rejected_at_import_startup(self) -> None:
        package_root = Path(gmpy2.__file__).resolve().parent
        site_root = package_root.parent
        extension = package_root / selector.GMPY2_EXTENSION_NAME
        libraries = site_root / "gmpy2.libs"
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            fake_package = root / "gmpy2"
            fake_package.mkdir()
            shutil.copy2(extension, fake_package / extension.name)
            shutil.copytree(libraries, root / libraries.name)
            sentinel = root / "fake-wrapper-executed"
            (fake_package / "__init__.py").write_text(
                "from pathlib import Path\n"
                f"Path({str(sentinel)!r}).write_text('executed')\n"
                "from .gmpy2 import *\n"
                "_authentic_exp = exp\n"
                "def exp(_value): return mpfr(1)\n",
                encoding="utf-8",
            )
            environment = os.environ.copy()
            environment["PYTHONPATH"] = os.pathsep.join((temporary, str(CODE_DIR)))
            completed = subprocess.run(
                [sys.executable, "-c", "import positive_b_stage_b_t1_selector_v5"],
                check=False,
                capture_output=True,
                env=environment,
                text=True,
            )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("requires the isolated verified loader", completed.stderr)
        self.assertFalse(sentinel.exists(), "fake gmpy2 wrapper executed before entry HOLD")

    def test_in_memory_wrapper_override_is_rejected(self) -> None:
        with (
            mock.patch.object(selector.gmpy2, "exp", lambda _value: selector.gmpy2.mpfr(1)),
            self.assertRaisesRegex(selector.Hold, "wrapper override"),
        ):
            selector.verify_mpfr_runtime()
        selector.verify_mpfr_runtime()

    def test_bundled_library_closure_drift_is_rejected(self) -> None:
        drifted = selector.GMPY2_BUNDLED_LIBRARY_HASHES + (("forged.dylib", "0" * 64),)
        with (
            mock.patch.object(selector, "GMPY2_BUNDLED_LIBRARY_HASHES", drifted),
            self.assertRaisesRegex(selector.Hold, "closure drift"),
        ):
            selector.verify_mpfr_runtime()

    def test_loaded_native_image_closure_drift_is_rejected(self) -> None:
        with (
            mock.patch.object(selector, "_loaded_gmpy2_native_images", return_value=set()),
            self.assertRaisesRegex(selector.Hold, "native-image closure drift"),
        ):
            selector.verify_mpfr_runtime()

    def test_public_output_carries_executed_byte_attestation(self) -> None:
        result = selector.parse_canonical_json_bytes(
            selector.select_saved_controls_bytes(fixtures.synthetic_payload_bytes())
        )
        package = result["package_runtime"]
        self.assertEqual(package["implementation_sha256"], EXPECTED_IMPLEMENTATION_SHA256)
        self.assertEqual(package["entry"]["mode"], "VERIFIED-ISOLATED-SYNTHETIC-TEST")
        self.assertEqual(len(package["entry"]["external_attestation_sha256"]), 64)
        self.assertEqual(
            package["runtime"]["package_init_sha256"],
            selector.GMPY2_PACKAGE_INIT_SHA256,
        )
        self.assertEqual(
            package["runtime"]["bundled_libraries_sha256"],
            dict(selector.GMPY2_BUNDLED_LIBRARY_HASHES),
        )


class Round81ArithmeticAndSchemaRepairs(unittest.TestCase):
    def test_extreme_negative_exp_has_correct_three_endpoints(self) -> None:
        for value in (-1000.0, -1.0e20, -float.fromhex("0x1.fffffffffffffp+1023")):
            with self.subTest(value=value):
                self.assertEqual(selector.exp_down64(value), 0.0)
                self.assertEqual(selector.exp_rn(value), 0.0)
                self.assertEqual(selector.exp_up64(value), selector.MIN_SUBNORMAL)

    def test_sparse_ordered_node_ids_use_array_neighbors(self) -> None:
        payload = fixtures.synthetic_selector_payload()
        for branch in payload["saved_branches"]:
            for node, acceptance_index in zip(branch["nodes"], (10, 20, 30), strict=True):
                node["acceptance_index"] = acceptance_index
            branch["comparison_records"][0]["acceptance_index"] = 20
        result = selector._select_saved_controls(payload)
        self.assertEqual(
            [branch["comparison_acceptance_index"] for branch in result["branches"]],
            [20, 20],
        )

    def test_bool_index_alias_remains_rejected(self) -> None:
        payload = fixtures.synthetic_selector_payload()
        payload["candidate_generation"][0]["index"] = True
        raw = selector.canonical_json_bytes(payload)
        with self.assertRaisesRegex(selector.Hold, "unsigned 64-bit integer"):
            selector.select_saved_controls_bytes(raw)

    def test_runtime_lock_matches_the_attested_dependency_closure(self) -> None:
        runtime_lock = CODE_DIR / "positive_b_stage_b_t0_runtime_lock_v2.json"
        self.assertEqual(
            hashlib.sha256(runtime_lock.read_bytes()).hexdigest(),
            selector.RUNTIME_LOCK_SHA256,
        )


if __name__ == "__main__":
    unittest.main()
