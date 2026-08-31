"""Round-94 regressions for the Round-93 transient-wrapper exploit.

Only the authenticated package sources, copied runtime bytes, and hand-built
synthetic selector fixtures are used. No scientific object, producer,
manifest, result, mesh, FV, or off-lattice calculation is opened or run.
"""

from __future__ import annotations

# ruff: noqa: E402, I001 -- verified bootstrap aliases precede fixture imports
import builtins
import hashlib
import json
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
import test_stageb_t0_selector_round78 as round78


CODE_DIR = Path(__file__).resolve().parent


class Round94TransientWrapperAndTrustContractTests(unittest.TestCase):
    def test_round93_transient_wrapper_exploit_has_zero_execution_and_clean_output(self) -> None:
        authentic_site = Path(gmpy2.__file__).resolve().parent.parent
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            runtime_site = root / "runtime"
            runtime_site.mkdir()
            shutil.copytree(authentic_site / "gmpy2", runtime_site / "gmpy2")
            shutil.copytree(authentic_site / "gmpy2.libs", runtime_site / "gmpy2.libs")

            sentinel = root / "round93-hostile-wrapper-executed"
            hostile_wrapper = root / "hostile-wrapper.py"
            hostile_wrapper.write_text(
                "import builtins as _builtins\n"
                f"open({str(sentinel)!r}, 'w', encoding='utf-8').write('executed')\n"
                "from .gmpy2 import *\n"
                "_real_exec = _builtins.exec\n"
                "def _hijacked_exec(code, globals=None, locals=None):\n"
                "    result = _real_exec(code, globals, locals)\n"
                "    if isinstance(globals, dict) and "
                "'select_saved_controls_bytes' in globals:\n"
                "        globals['exp_rn'] = lambda _value: 42.0\n"
                "        authentic = globals['select_saved_controls_bytes']\n"
                "        def forged(payload):\n"
                "            value = globals['parse_canonical_json_bytes'](authentic(payload))\n"
                "            value['branches'][0]['selected'][0]['index'] = 999\n"
                "            return globals['canonical_json_bytes'](value)\n"
                "        globals['select_saved_controls_bytes'] = forged\n"
                "    return result\n"
                "_builtins.exec = _hijacked_exec\n",
                encoding="utf-8",
            )
            authentic_wrapper = root / "authentic-wrapper.py"
            authentic_wrapper.write_bytes((runtime_site / "gmpy2" / "__init__.py").read_bytes())

            attestation_path = root / "synthetic-attestation-v2.json"
            attestation_bytes = round78.synthetic_attestation_bytes(runtime_site)
            attestation_path.write_bytes(attestation_bytes)
            payload_path = root / "synthetic-selector-payload.json"
            payload_path.write_bytes(fixtures.synthetic_payload_bytes())
            loader_path = CODE_DIR / "positive_b_stage_b_t0_verified_loader.py"

            command = (
                "import hashlib,json,os,pathlib,sys,types; "
                f"lp=pathlib.Path({str(loader_path)!r}); "
                "lb=lp.read_bytes(); "
                "lm=types.ModuleType('_round94_captured_loader'); "
                "lm.__file__=str(lp); lm.__package__=''; lm.__loader__=None; "
                "sys.modules[lm.__name__]=lm; "
                "exec(compile(lb,str(lp),'exec',dont_inherit=True),lm.__dict__); "
                "sys.dont_write_bytecode=True; "
                "guard=lm._RuntimeIdentityGuard(); "
                f"ap=pathlib.Path({str(attestation_path)!r}); "
                "ab=ap.read_bytes(); ah=hashlib.sha256(ab).hexdigest(); "
                "expected,rr,context=lm._consume_external_attestation(ap,ah); "
                "sp=pathlib.Path(lm.__file__).parent/lm.IMPLEMENTATION_NAME; "
                "source=lm._read_exact_source(sp); "
                "assert hashlib.sha256(source).hexdigest()==expected; "
                "snap=lm._verify_runtime_tree(rr); "
                f"os.replace({str(hostile_wrapper)!r},snap.package_init); "
                "lm._load_verified_gmpy2(snap,guard); "
                f"os.replace({str(authentic_wrapper)!r},snap.package_init); "
                "s=lm._execute_frozen_selector("
                "entry_context=context,expected_sha256=expected,guard=guard,"
                "source=source,source_path=sp); "
                f"payload=pathlib.Path({str(payload_path)!r}).read_bytes(); "
                "out=s.parse_canonical_json_bytes(s.select_saved_controls_bytes(payload)); "
                "print(json.dumps({"
                "'exp_rn':s.exp_rn(1.0),"
                "'index':out['branches'][0]['selected'][0]['index'],"
                "'mode':out['package_runtime']['entry']['mode'],"
                "'status':out['package_runtime']['entry']['external_attestation_status'],"
                "'production_eligible':"
                "out['package_runtime']['entry']['production_eligible'],"
                "'trust_contract':out['package_runtime']['trust_contract']"
                "},sort_keys=True))"
            )
            completed = subprocess.run(
                [sys.executable, "-I", "-S", "-c", command],
                check=False,
                capture_output=True,
                text=True,
            )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        result = json.loads(completed.stdout)
        self.assertFalse(sentinel.exists(), "transient hostile wrapper executed")
        self.assertNotEqual(result["exp_rn"], 42.0)
        self.assertEqual(result["index"], 10)
        self.assertEqual(result["mode"], "VERIFIED-ISOLATED-SYNTHETIC-TEST")
        self.assertEqual(result["status"], "NON-PROMOTABLE-SYNTHETIC-TEST")
        self.assertIs(result["production_eligible"], False)
        self.assertEqual(result["trust_contract"], verified_loader._expected_trust_contract())

    def test_builtins_identity_drift_holds_before_public_output_bytes(self) -> None:
        payload = fixtures.synthetic_payload_bytes()
        for name in ("exec", "__import__"):
            original = getattr(builtins, name)
            setattr(builtins, name, lambda *_args, **_kwargs: None)
            try:
                with (
                    self.subTest(name=name),
                    self.assertRaisesRegex(
                        verified_loader.FrozenLoadError,
                        rf"runtime identity guard HOLD.*builtins\.{name} drift",
                    ),
                ):
                    selector.select_saved_controls_bytes(payload)
            finally:
                setattr(builtins, name, original)
        decoded = selector.parse_canonical_json_bytes(selector.select_saved_controls_bytes(payload))
        self.assertEqual(decoded["branches"][0]["selected"][0]["index"], 10)

    def test_midcall_builtins_hijack_returns_no_verified_output(self) -> None:
        payload = fixtures.synthetic_payload_bytes()
        authentic_select = selector._select_saved_controls
        authentic_exec = builtins.exec
        returned: bytes | None = None

        def hijack_after_selection(decoded: object) -> dict[str, object]:
            result = authentic_select(decoded)
            builtins.exec = lambda *_args, **_kwargs: None
            return result

        try:
            with (
                mock.patch.object(
                    selector,
                    "_select_saved_controls",
                    hijack_after_selection,
                ),
                self.assertRaisesRegex(
                    verified_loader.FrozenLoadError,
                    r"runtime identity guard HOLD.*builtins\.exec drift",
                ),
            ):
                returned = selector.select_saved_controls_bytes(payload)
        finally:
            builtins.exec = authentic_exec
        self.assertIsNone(returned)
        decoded = selector.parse_canonical_json_bytes(selector.select_saved_controls_bytes(payload))
        self.assertEqual(decoded["branches"][0]["selected"][0]["index"], 10)

    def test_output_mode_and_trust_contract_are_exact_and_nonpromotable(self) -> None:
        output = selector.parse_canonical_json_bytes(
            selector.select_saved_controls_bytes(fixtures.synthetic_payload_bytes())
        )
        package = output["package_runtime"]
        self.assertEqual(package["trust_contract"], verified_loader._expected_trust_contract())
        self.assertEqual(
            package["runtime"]["python_wrapper_execution"],
            "VERIFIED-DESCRIPTOR-SNAPSHOT-COMPILE-EXEC",
        )
        self.assertEqual(
            package["entry"]["external_attestation_schema"],
            verified_loader.SYNTHETIC_ATTESTATION_SCHEMA,
        )
        self.assertEqual(
            package["entry"]["external_attestation_status"],
            "NON-PROMOTABLE-SYNTHETIC-TEST",
        )
        self.assertEqual(package["entry"]["mode"], "VERIFIED-ISOLATED-SYNTHETIC-TEST")
        self.assertIs(package["entry"]["production_eligible"], False)

    def test_record_trust_contract_and_mode_cross_products_hold(self) -> None:
        base = json.loads(round78.synthetic_attestation_bytes())
        mutations: tuple[tuple[str, object, str], ...] = (
            (
                "changed trust contract",
                {
                    **base,
                    "trust_contract": {
                        **base["trust_contract"],
                        "protection_claim": "CRYPTOGRAPHIC-IMMUTABILITY",
                    },
                },
                "trust-contract drift",
            ),
            (
                "missing trust contract",
                {key: value for key, value in base.items() if key != "trust_contract"},
                "schema/canonical-byte drift",
            ),
            (
                "synthetic schema with production status",
                {**base, "status": "INDEPENDENT-ATTACK-PASS"},
                "synthetic attestation status drift",
            ),
            (
                "production schema without production roles",
                {
                    **base,
                    "schema": verified_loader.PRODUCTION_ATTESTATION_SCHEMA,
                    "status": "INDEPENDENT-ATTACK-PASS",
                },
                "package-role closure drift",
            ),
        )
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            for label, record, message in mutations:
                with self.subTest(label=label):
                    payload = json.dumps(record, sort_keys=True, indent=2).encode("ascii") + b"\n"
                    path = root / f"{label.replace(' ', '-')}.json"
                    path.write_bytes(payload)
                    with self.assertRaisesRegex(
                        verified_loader.FrozenLoadError,
                        message,
                    ):
                        verified_loader._consume_external_attestation(
                            path,
                            hashlib.sha256(payload).hexdigest(),
                        )


if __name__ == "__main__":
    unittest.main()
