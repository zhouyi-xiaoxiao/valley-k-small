#!/usr/bin/env python3
"""H13 killing tests for the unsealed secondary-R5 authority scaffold."""
from __future__ import annotations

import hashlib
import os
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import h13_pinned_controller_v4_r2 as controller
import h13_runtime_v4_r2 as runtime
import verify_v3_release_for_v4_r2_h13 as authority


ROOT = Path(__file__).resolve().parents[1]
H12_CONTROLLER_SHA256 = (
    "e3824df1224d28e4dd7e0a436b619fc6b3c22ecaefa829146d9e081946421421"
)
H12_PAYLOAD_SHA256 = (
    "bcc487d9910dd6cb5732f26ca18caecd20b7a24844083fd61b89c361fdae0e0a"
)
R3_HOLD_AUDIT_SHA256 = (
    "329fee6703080d8eff69fdc015eb3b0f21f2026378b1612a658106cc6efeb453"
)
R4_HOLD_AUDIT_SHA256 = (
    "7f18217760ace67d8d545e986ec0d67a4e63a355b348c5c05d1d967e08c02e75"
)
CONTROL_PYTHON = "/opt/cray/pe/python/3.11.7/bin/python3.11"
CONTROL_PYTHON_SHA256 = (
    "9270f0548999f7c4fa66df1c4fd4ec6a7edfc54ff5b8bd881d89a2cc891f6b94"
)


def sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def local_python_anchor() -> dict:
    path = Path(sys.executable).resolve()
    info = path.stat()
    return {
        "path": str(path),
        "sha256": sha(path),
        "device": info.st_dev,
        "inode": info.st_ino,
        "size": info.st_size,
        "mtime_ns": info.st_mtime_ns,
        "mode": stat.S_IMODE(info.st_mode),
        "uid": info.st_uid,
    }


class H13Tests(unittest.TestCase):
    def test_h12_is_frozen_and_h13_is_append_only_unsealed(self):
        h12_manifest = ROOT / "notes/isambard_ai_v4_r2_h12_payload.sha256"
        self.assertEqual(sha(h12_manifest), H12_PAYLOAD_SHA256)
        self.assertEqual(
            sha(ROOT / "code/h12_pinned_controller_v4_r2.py"),
            H12_CONTROLLER_SHA256,
        )
        for line in h12_manifest.read_text().splitlines():
            digest, name = line.split("  ", 1)
            self.assertEqual(sha(ROOT / name), digest, name)
        self.assertFalse(
            (ROOT / "notes/isambard_ai_v4_r2_h13_payload.sha256").exists()
        )
        self.assertEqual(controller.H13_SHA, "__H13_PAYLOAD_SHA_PENDING__")

    def test_pending_h13_and_secondary_r5_contracts_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "authority contract pending"):
            controller.authority_contract_ready()
        with self.assertRaisesRegex(ValueError, "secondary R5 contract pending"):
            authority.contract_ready()
        self.assertEqual(
            controller.AUTHORITY_INPUT_SCHEMA,
            authority.AUTHORITY_INPUT_SCHEMA,
        )
        self.assertEqual(
            controller.AUTHORITY_INPUT_SCHEMA,
            "h13-secondary-authority-cli-v1",
        )
        pending_values = (
            controller.SECONDARY_RELEASE_SCHEMA,
            controller.SECONDARY_RELEASE_STATUS,
            controller.SECONDARY_AUDIT_SCHEMA,
            controller.SECONDARY_AUDIT_STATUS,
            *authority.EXPECTED_SECONDARY_MEMBER_NAMES,
        )
        self.assertTrue(all("PENDING" in value for value in pending_values))

    def test_controller_entrypoint_rejects_plain_python_and_ignores_sitecustomize(self):
        python = Path("/usr/bin/python3")
        if not python.exists():
            self.skipTest("/usr/bin/python3 is unavailable")
        source = ROOT / "code/h13_pinned_controller_v4_r2.py"
        with tempfile.TemporaryDirectory() as temporary:
            attack = Path(temporary)
            marker = attack / "sitecustomize-executed"
            (attack / "sitecustomize.py").write_text(
                "from pathlib import Path\n"
                f"Path({str(marker)!r}).write_text('executed\\n')\n"
            )
            environment = os.environ.copy()
            environment["PYTHONPATH"] = str(attack)
            plain = subprocess.run(
                [str(python), str(source), "--help"],
                env=environment,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(plain.returncode, 126)
            self.assertIn("requires the absolute -I isolated shebang", plain.stderr)
            self.assertEqual(marker.read_text(), "executed\n")
            marker.unlink()
            isolated = subprocess.run(
                [str(python), "-I", "-B", "-E", "-s", str(source), "--help"],
                env=environment,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(isolated.returncode, 0, isolated.stderr)
            self.assertFalse(marker.exists())
            self.assertIn("{submit,finalize}", isolated.stdout)

    def test_remote_control_python_is_exactly_pinned(self):
        source = (ROOT / "code/h13_pinned_controller_v4_r2.py").read_text()
        self.assertEqual(source.splitlines()[0], f"#!{CONTROL_PYTHON} -I")
        self.assertEqual(controller.CONTROL_PYTHON, CONTROL_PYTHON)
        self.assertEqual(controller.CONTROL_PYTHON_SHA256, CONTROL_PYTHON_SHA256)
        self.assertIn("sys.flags.isolated", source)
        self.assertIn("sys.flags.ignore_environment", source)
        self.assertIn("sys.flags.no_user_site", source)

    def test_h13_scripts_have_no_module_or_path_resolved_runtime_tools(self):
        scripts = {
            phase: (ROOT / name).read_text()
            for phase, name in controller.SCIENCE_SCRIPTS.items()
        }
        self.assertEqual(set(scripts), {"v3_authority_h13", "canary", "production"})
        for phase, text in scripts.items():
            with self.subTest(phase=phase):
                self.assertTrue(text.startswith("#!/bin/bash\n"))
                self.assertNotIn("module load", text)
                self.assertNotIn("command -v python3", text)
                self.assertEqual(text.count("#SBATCH --export=NIL"), 1)
                self.assertIn("/usr/bin/apptainer exec", text)
                self.assertIn("python3 -I -B -E -s", text)
                self.assertIn("h13_pinned_source |", text)
                self.assertNotIn(" -s code/", text)
        for phase in ("canary", "production"):
            self.assertIn("/usr/bin/srun", scripts[phase])
        self.assertNotIn("/usr/bin/srun", scripts["v3_authority_h13"])
        self.assertEqual(runtime.MODULE_PHASES, frozenset())
        for phase in controller.CAMPAIGN_ORDER:
            self.assertIsNone(runtime.module_init(phase))

    def test_single_fd_reader_accepts_exact_and_rejects_links(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            os.chmod(root, 0o700)
            exact = root / "exact.bin"
            exact.write_bytes(b"bound bytes\n")
            os.chmod(exact, 0o600)
            digest = sha(exact)
            self.assertEqual(
                runtime.read_beneath_once(
                    root, "exact.bin", expected_sha256=digest
                ),
                b"bound bytes\n",
            )
            hardlink = root / "hardlink.bin"
            os.link(exact, hardlink)
            with self.assertRaisesRegex(ValueError, "unsafe package member"):
                runtime.read_beneath_once(
                    root, "hardlink.bin", expected_sha256=digest
                )
            hardlink.unlink()
            exact.unlink()
            outside = root.parent / f"{root.name}-outside"
            outside.write_bytes(b"outside\n")
            try:
                symlink = root / "symlink.bin"
                symlink.symlink_to(outside)
                with self.assertRaises((ValueError, OSError)):
                    runtime.read_beneath_once(
                        root,
                        "symlink.bin",
                        expected_sha256=sha(outside),
                    )
            finally:
                outside.unlink(missing_ok=True)

    def test_authority_inputs_are_single_fd_copied_into_snapshot(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            os.chmod(root, 0o700)
            run = root / "run"
            snapshot = root / "snapshot"
            run.mkdir(mode=0o700)
            snapshot.mkdir(mode=0o700)
            source = run / "artifacts/r5/member.json"
            source.parent.mkdir(parents=True, mode=0o700)
            source.write_bytes(b'{"bound":true}\n')
            os.chmod(source, 0o600)
            digest = sha(source)
            imported = runtime.copy_inputs_hardened(
                run,
                snapshot,
                [{"path": "artifacts/r5/member.json", "sha256": digest}],
                {},
            )
            copied = snapshot / "artifacts/r5/member.json"
            self.assertEqual(
                imported,
                {"artifacts/r5/member.json": digest},
            )
            self.assertEqual(copied.read_bytes(), b'{"bound":true}\n')
            self.assertEqual(stat.S_IMODE(copied.stat().st_mode), 0o400)
            hardlink = run / "artifacts/r5/member-hardlink.json"
            os.link(source, hardlink)
            with self.assertRaisesRegex(ValueError, "unsafe package member"):
                runtime.copy_inputs_hardened(
                    run,
                    root / "unused-snapshot",
                    [{
                        "path": "artifacts/r5/member-hardlink.json",
                        "sha256": digest,
                    }],
                    {},
                )
            runtime_source = (ROOT / "code/h13_runtime_v4_r2.py").read_text()
            self.assertIn(
                "module.copy_snapshot = copy_snapshot_hardened",
                runtime_source,
            )
            self.assertIn(
                "module.copy_inputs = copy_inputs_hardened",
                runtime_source,
            )

    def test_pinned_launcher_executes_captured_modules_and_rejects_drift(self):
        with tempfile.TemporaryDirectory() as temporary:
            package = Path(temporary)
            os.chmod(package, 0o700)
            code = package / "code"
            notes = package / "notes"
            code.mkdir(mode=0o700)
            notes.mkdir(mode=0o700)
            dependency = code / "bound_dependency.py"
            entry = code / "bound_entry.py"
            dependency.write_text("VALUE = 7\n")
            entry.write_text(
                "import bound_dependency\n"
                "print(f'bound={bound_dependency.VALUE}')\n"
            )
            for path in (dependency, entry):
                os.chmod(path, 0o400)
            rows = (
                f"{sha(dependency)}  code/bound_dependency.py\n"
                f"{sha(entry)}  code/bound_entry.py\n"
            )
            manifest = notes / "isambard_ai_v4_r2_h13_payload.sha256"
            manifest.write_text(rows)
            os.chmod(manifest, 0o400)
            anchor = sha(manifest)
            attack = package.parent / f"{package.name}-pythonpath"
            attack.mkdir(mode=0o700)
            marker = attack / "sitecustomize-marker"
            (attack / "sitecustomize.py").write_text(
                "from pathlib import Path\n"
                f"Path({str(marker)!r}).write_text('executed\\n')\n"
            )
            environment = os.environ.copy()
            environment["PYTHONPATH"] = str(attack)
            try:
                command = [
                    sys.executable,
                    "-I",
                    "-B",
                    "-E",
                    "-s",
                    "-",
                    anchor,
                    "code/bound_entry.py",
                ]
                accepted = subprocess.run(
                    command,
                    input=runtime.PINNED_PYTHON_LAUNCHER,
                    cwd=package,
                    env=environment,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(accepted.returncode, 0, accepted.stderr)
                self.assertEqual(accepted.stdout, "bound=7\n")
                self.assertFalse(marker.exists())
                os.chmod(dependency, 0o600)
                dependency.write_text("VALUE = 999\n")
                os.chmod(dependency, 0o400)
                rejected = subprocess.run(
                    command,
                    input=runtime.PINNED_PYTHON_LAUNCHER,
                    cwd=package,
                    env=environment,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertNotEqual(rejected.returncode, 0)
                self.assertIn(
                    "bound source hash drift code/bound_dependency.py",
                    rejected.stderr,
                )
            finally:
                for path in attack.iterdir():
                    path.unlink()
                attack.rmdir()

    def test_rendered_wrapper_has_one_export_and_exact_production_shape(self):
        production = controller.SCIENCE_SCRIPTS["production"]
        rows = {
            production: sha(ROOT / production),
            controller.RUNTIME: sha(ROOT / controller.RUNTIME),
        }
        with tempfile.TemporaryDirectory() as temporary:
            run = Path(temporary).resolve()
            os.chmod(run, 0o700)
            with patch.object(
                controller, "python_anchor", return_value=local_python_anchor()
            ):
                wrapper, binding, final_sha = controller.render(
                    ROOT,
                    run,
                    "production",
                    ["payload", "release", "release-sha", "canary", "canary-sha"],
                    [],
                    rows,
                )
        text = wrapper.decode()
        self.assertTrue(text.startswith("#!/bin/bash\n"))
        self.assertEqual(text.count("#SBATCH --export=NIL"), 1)
        self.assertIn(" -I -B -E -s ", text)
        self.assertIn("unset BASH_ENV ENV CDPATH GLOBIGNORE PYTHONPATH", text)
        self.assertEqual(len(binding), 64)
        self.assertEqual(sha_bytes(wrapper), final_sha)
        for directive in (
            "#SBATCH --nodes=1",
            "#SBATCH --ntasks=4",
            "#SBATCH --gpus=4",
            "#SBATCH --gpus-per-task=1",
            "#SBATCH --time=02:00:00",
            "#SBATCH --array=0-479%240",
        ):
            self.assertEqual(text.count(directive), 1, directive)

    def test_production_cell_mapping_is_exact_bijective_23040(self):
        text = (
            ROOT / controller.SCIENCE_SCRIPTS["production"]
        ).read_text()
        self.assertIn(
            "cell=$((10#$TASK+480*(10#$gpu+4*bundle)))",
            text,
        )
        self.assertIn(
            "cell=$((10#$TASK+480*(gpu+4*bundle)))",
            text,
        )
        cells = {
            task + 480 * (gpu + 4 * bundle)
            for task in range(480)
            for gpu in range(4)
            for bundle in range(12)
        }
        self.assertEqual(len(cells), 23040)
        self.assertEqual(min(cells), 0)
        self.assertEqual(max(cells), 23039)
        self.assertEqual(controller.CAMPAIGN_ORDER, (
            "v3_authority_h13",
            "canary",
            "production",
        ))

    def test_r3_hold_is_anchored_and_r3_is_not_secondary_authority(self):
        audit = (
            ROOT
            / "notes/grid2d_gpu_v3_secondary_r3_independent_hold_audit_20260727.md"
        )
        self.assertEqual(sha(audit), R3_HOLD_AUDIT_SHA256)
        self.assertIn("HOLD — do not sync, submit, publish", audit.read_text())
        r4_audit = (
            ROOT
            / "notes/grid2d_gpu_v3_secondary_r4_independent_hold_audit_20260727.md"
        )
        self.assertEqual(sha(r4_audit), R4_HOLD_AUDIT_SHA256)
        self.assertIn(
            "use R4 to unlock the full-node H13",
            r4_audit.read_text(),
        )
        h13_sources = "\n".join(
            (ROOT / name).read_text()
            for name in (
                "code/h13_pinned_controller_v4_r2.py",
                "code/verify_v3_release_for_v4_r2_h13.py",
                "code/isambard_ai_gating_v4_r2_v3_authority_h13.sbatch",
            )
        )
        self.assertNotIn("grid2d_gpu_v3_secondary_r3", h13_sources)
        self.assertNotIn("SECONDARY_R3", h13_sources)
        self.assertIn("SECONDARY_R5", h13_sources)
        self.assertNotIn(
            "grid2d-one-two-target-gating-secondary-max-t-r4",
            h13_sources,
        )
        self.assertEqual(
            controller.REJECTED_SECONDARY_R4_PAYLOAD_SHA256,
            "e02ac46aa968ff725f83b08a759b81cfea37197dca710c42544f78ecac0387af",
        )
        self.assertEqual(
            controller.REJECTED_SECONDARY_R4_CONTRACT_SHA256,
            "c90ebc92958c1ddb82aa0f54919a32f8e0c3ca64c7ea90dbf7c97dc20da232b4",
        )
        r5_runbook = (
            ROOT
            / "notes/isambard_ai_v4_r2_h13_secondary_r5_hold_runbook.md"
        ).read_text()
        self.assertIn("Secondary R4 is also **not** an H13 authority", r5_runbook)
        self.assertIn("forged counts could pass", r5_runbook)


if __name__ == "__main__":
    unittest.main()
