#!/usr/bin/env python3
"""H12 killing tests for environment isolation and executable authority."""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import stat
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import build_isambard_ai_v4_r2_h12_payload as build
import h12_pinned_controller_v4_r2 as controller
import h12_runtime_v4_r2 as runtime
import test_isambard_ai_gating_v4_r2_h11 as h11_tests


class H12Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.anchor = build.candidate_sha()
        controller.H12_SHA = cls.anchor

    def deploy(self, base: Path) -> Path:
        package = base / "package"
        package.mkdir(mode=0o700)
        for name in build.MEMBERS:
            target = package / name
            target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            shutil.copyfile(build.ROOT / name, target)
            os.chmod(target, 0o600)
        manifest = package / controller.MAN
        manifest.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        manifest.write_bytes(build.candidate_bytes())
        os.chmod(manifest, 0o600)
        for current, _, _ in os.walk(package):
            os.chmod(current, 0o700)
        return package

    def fake_tools(self, base: Path):
        tools = base / "tools"
        tools.mkdir(mode=0o700)
        state = base / "state.json"
        state.write_text(json.dumps({"next": 9600000, "jobs": {}, "scheduler_env_keys": []}))
        os.chmod(state, 0o600)
        state_literal = repr(str(state))
        sbatch = tools / "sbatch"
        sbatch.write_text(
            f"""#!/usr/bin/python3
import json,os,sys
from pathlib import Path
s=Path({state_literal}); v=json.loads(s.read_text()); j=str(v["next"]); v["next"]+=1
args=sys.argv[1:]; assert args.count("--export=NIL")==1
comment=next(x.split("=",1)[1] for x in args if x.startswith("--comment="))
work=next(x.split("=",1)[1] for x in args if x.startswith("--chdir="))
dep=next((x.split(":",1)[1] for x in args if x.startswith("--dependency=")),None)
script=s.parent/f"job-{{j}}.sh"; raw=sys.stdin.buffer.read(); script.write_bytes(raw); os.chmod(script,0o700)
v["scheduler_env_keys"]=sorted(os.environ)
v["jobs"][j]={{"comment":comment,"work":work,"dep":dep,"state":"PENDING","reason":"JobHeldUser","script":str(script),"array":b"#SBATCH --array=" in raw}}
s.write_text(json.dumps(v)); print(j)
"""
        )
        os.chmod(sbatch, 0o700)
        squeue = tools / "squeue"
        squeue.write_text(
            f"""#!/usr/bin/python3
import json
v=json.load(open({state_literal}))
for j,x in v["jobs"].items():
 if x["state"] in ("PENDING","RUNNING"): print(f"{{j}}|{{x['comment']}}|{{x['state']}}|{{x['reason']}}")
"""
        )
        os.chmod(squeue, 0o700)
        scontrol = tools / "scontrol"
        scontrol.write_text(
            f"""#!/usr/bin/python3
import json,os,subprocess,sys,tempfile
from pathlib import Path
s=Path({state_literal}); v=json.loads(s.read_text()); command=sys.argv[1]; j=sys.argv[-1]; x=v["jobs"][j]
if command=="show":
 dep="afterok:"+x["dep"] if x["dep"] else "(null)"
 print(f"JobId={{j}} JobState={{x['state']}} Reason={{x['reason']}} Comment={{x['comment']}} WorkDir={{x['work']}} Dependency={{dep}} Command=/tmp/slurm_script StdIn=/dev/null")
 raise SystemExit
if command=="release":
 x["state"]="RUNNING"; x["reason"]="None"; s.write_text(json.dumps(v))
 env=os.environ.copy(); tmp=Path(tempfile.mkdtemp(prefix="h12-fake-")).resolve()
 env.update({{"SLURM_JOB_ID":j,"SLURM_TMPDIR":str(tmp)}})
 cp=subprocess.run(["/bin/bash",x["script"]],env=env,capture_output=True)
 v=json.loads(s.read_text()); v["jobs"][j]["state"]="COMPLETED" if cp.returncode==0 else "FAILED"; v["jobs"][j]["reason"]="None"; s.write_text(json.dumps(v))
 if cp.returncode: sys.stderr.buffer.write(cp.stderr); raise SystemExit(cp.returncode)
 print("released",j)
"""
        )
        os.chmod(scontrol, 0o700)
        sacct = tools / "sacct"
        sacct.write_text(
            """#!/usr/bin/python3
import sys
j=sys.argv[sys.argv.index("-j")+1]
print(f"{j}|{j}|COMPLETED|0:0|7")
"""
        )
        os.chmod(sacct, 0o700)
        anchors = {
            name: controller.secure_root_executable(path, allow_user_owned=True)
            for name, path in {
                "sbatch": sbatch,
                "squeue": squeue,
                "scontrol": scontrol,
                "sacct": sacct,
            }.items()
        }
        return state, anchors

    def setup_scheduler(self, temporary: str):
        base = Path(temporary).resolve()
        os.chmod(base, 0o700)
        package = self.deploy(base)
        run = base / "run"
        state, anchors = self.fake_tools(base)
        return base, package, run, state, anchors

    def local_python_anchor(self):
        path = Path(os.sys.executable).resolve()
        info = path.stat()
        return {
            "path": str(path),
            "sha256": runtime.sha(path),
            "device": info.st_dev,
            "inode": info.st_ino,
            "size": info.st_size,
            "mtime_ns": info.st_mtime_ns,
            "mode": stat.S_IMODE(info.st_mode),
            "uid": info.st_uid,
        }

    def submit_upstream(self, package, run, anchors, environment):
        with patch.dict(os.environ, environment, clear=False), patch.object(
            controller, "python_anchor", return_value=self.local_python_anchor()
        ), patch.object(
            controller, "tool_anchors", return_value=anchors
        ):
            return controller.submit(
                package,
                run,
                "selftest_upstream",
                ["alpha", "one"],
                [],
                None,
            )

    def test_frozen_h11_append_only_and_detached_controller(self):
        self.assertEqual(build.h11.verify(), build.H11_SHA)
        self.assertEqual(build.MEMBERS[: len(build.h11.MEMBERS)], build.h11.MEMBERS)
        self.assertNotIn("code/h12_pinned_controller_v4_r2.py", build.MEMBERS)
        self.assertEqual(
            hashlib.sha256(
                (build.ROOT / "notes/isambard_ai_v4_r2_h11_payload.sha256").read_bytes()
            ).hexdigest(),
            controller.H11_SHA,
        )
        self.assertEqual(
            hashlib.sha256(
                (build.ROOT / "code/h11_pinned_controller_v4_r2.py").read_bytes()
            ).hexdigest(),
            controller.H11_CONTROLLER_SHA,
        )

    def test_h11_bash_env_attack_executes_before_bound_wrapper(self):
        h11_tests.H11Tests.setUpClass()
        legacy = h11_tests.H11Tests()
        with tempfile.TemporaryDirectory() as temporary:
            base, package, run, state, tools = legacy.setup_scheduler(temporary)
            hook = base / "attack.sh"
            marker = base / "H11_ATTACK_EXECUTED"
            hook.write_text('printf "H11_ENV_INJECTED\\n" > "$H12_ATTACK_MARKER"\n')
            os.chmod(hook, 0o600)
            environment = {
                "H11_FAKE_STATE": str(state),
                "H9_TEST_OUTPUT_NAME": "legacy-injected",
                "BASH_ENV": str(hook),
                "H12_ATTACK_MARKER": str(marker),
            }
            result = legacy.submit_upstream(package, run, tools, environment)
            self.assertEqual(
                result["release"]["status"], "RELEASED_AFTER_DURABLE_SUBMISSION_RECEIPT"
            )
            self.assertEqual(marker.read_text(), "H11_ENV_INJECTED\n")

    def test_h12_blocks_bash_env_python_path_and_path_hijack_end_to_end(self):
        with tempfile.TemporaryDirectory() as temporary:
            base, package, run, state, anchors = self.setup_scheduler(temporary)
            attack = base / "attack"
            attack.mkdir(mode=0o700)
            marker = base / "H12_ATTACK_MARKER"
            hook = attack / "bash_env.sh"
            hook.write_text('printf "BASH_ENV\\n" >> "$H12_ATTACK_MARKER"\n')
            os.chmod(hook, 0o600)
            for name in ("bash", "python3", "base64", "mktemp"):
                path = attack / name
                path.write_text(
                    f'#!/bin/sh\nprintf "{name}\\n" >> "$H12_ATTACK_MARKER"\nexit 99\n'
                )
                os.chmod(path, 0o700)
            environment = {
                "H9_TEST_OUTPUT_NAME": "h12-clean",
                "BASH_ENV": str(hook),
                "PYTHONPATH": str(attack),
                "PATH": f"{attack}:/usr/bin:/bin",
                "H12_ATTACK_MARKER": str(marker),
            }
            result = self.submit_upstream(package, run, anchors, environment)
            self.assertFalse(marker.exists())
            self.assertEqual(
                (run / "artifacts/h9_e2e/h12-clean.txt").read_text(), "alpha:one\n"
            )
            self.assertEqual(
                result["h12"]["status"],
                "PASS_H12_ISOLATED_ENVIRONMENT_AND_PINNED_EXECUTABLES",
            )
            self.assertEqual(result["submission"]["sbatch_argv"].count("--export=NIL"), 1)
            state_value = json.loads(state.read_text())
            self.assertNotIn("BASH_ENV", state_value["scheduler_env_keys"])
            self.assertNotIn("PYTHONPATH", state_value["scheduler_env_keys"])
            self.assertTrue(
                {"HOME", "LANG", "LC_ALL", "LOGNAME", "PATH", "SHELL", "USER"}
                <= set(state_value["scheduler_env_keys"])
            )
            job = result["submission"]["job_id"]
            receipt = controller.base.json_mode(
                run / f"artifacts/h11_receipts/selftest_upstream-{job}.json"
            )
            self.assertEqual(receipt["h12"], self.anchor)
            self.assertEqual(
                receipt["h12_status"], "PASS_H12_ENVIRONMENT_ISOLATED_EXECUTION"
            )
            self.assertNotIn("BASH_ENV", receipt["science_environment_keys"])
            self.assertNotIn("PYTHONPATH", receipt["science_environment_keys"])

    def test_h12_two_job_dependency_requires_h12_envelope_and_receipt(self):
        with tempfile.TemporaryDirectory() as temporary:
            _, package, run, _, anchors = self.setup_scheduler(temporary)
            upstream = self.submit_upstream(
                package, run, anchors, {"H9_TEST_OUTPUT_NAME": "up"}
            )
            upstream_job = upstream["submission"]["job_id"]
            source = run / "artifacts/h9_e2e/up.txt"
            with patch.dict(
                os.environ, {"H9_TEST_OUTPUT_NAME": "down"}, clear=False
            ), patch.object(
                controller, "python_anchor", return_value=self.local_python_anchor()
            ), patch.object(
                controller, "tool_anchors", return_value=anchors
            ):
                downstream = controller.submit(
                    package,
                    run,
                    "selftest_downstream",
                    ["beta", "two"],
                    [f"artifacts/h9_e2e/up.txt={runtime.sha(source)}"],
                    upstream_job,
                )
            self.assertEqual(
                downstream["submission"]["dependency_afterok"], upstream_job
            )
            self.assertEqual(
                (run / "artifacts/h9_e2e/down.txt").read_text(), "beta:two\n"
            )
            envelope = controller.envelope_path(
                run, "selftest_upstream", upstream_job
            )
            before = runtime.sha(envelope)
            repeated = self.submit_upstream(
                package, run, anchors, {"H9_TEST_OUTPUT_NAME": "up"}
            )
            self.assertEqual(repeated["submission"]["job_id"], upstream_job)
            self.assertEqual(runtime.sha(envelope), before)

    def test_wrapper_and_production_shape_are_exact(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary).resolve()
            os.chmod(base, 0o700)
            package = self.deploy(base)
            rows = controller.verify_package(package)
            run = base / "run"
            run.mkdir(mode=0o700)
            with patch.object(
                controller,
                "python_anchor",
                return_value={
                    "path": str(Path(os.sys.executable).resolve()),
                    "sha256": runtime.sha(Path(os.sys.executable).resolve()),
                    "device": Path(os.sys.executable).resolve().stat().st_dev,
                    "inode": Path(os.sys.executable).resolve().stat().st_ino,
                    "size": Path(os.sys.executable).resolve().stat().st_size,
                    "mtime_ns": Path(os.sys.executable).resolve().stat().st_mtime_ns,
                    "mode": stat.S_IMODE(Path(os.sys.executable).resolve().stat().st_mode),
                    "uid": Path(os.sys.executable).resolve().stat().st_uid,
                },
            ):
                wrapper, _, _ = controller.render(
                    package, run, "production", ["x"] * 5, [], rows
                )
            text = wrapper.decode()
            self.assertTrue(text.startswith("#!/bin/bash\n"))
            self.assertNotIn("#!/usr/bin/env bash", text)
            self.assertIn("#SBATCH --export=NIL", text)
            self.assertIn(" -I -B -E -s ", text)
            for directive in (
                "#SBATCH --nodes=1",
                "#SBATCH --ntasks=4",
                "#SBATCH --gpus=4",
                "#SBATCH --gpus-per-task=1",
                "#SBATCH --array=0-479%240",
            ):
                self.assertIn(directive, text)
            self.assertEqual(
                runtime.sha(build.ROOT / controller.SCRIPTS["production"]),
                "30df2636b4459a3ff6c91ccb1cd6bca9e9ab7a6017a0bc4a334e4fbf64fc4bbe",
            )

    def test_user_owned_scheduler_executable_is_not_production_authority(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary).resolve() / "sbatch"
            path.write_text("#!/bin/sh\nexit 0\n")
            os.chmod(path, 0o700)
            with self.assertRaisesRegex(ValueError, "executable authority"):
                controller.secure_root_executable(path)
            anchor = controller.secure_root_executable(path, allow_user_owned=True)
            path.write_text("#!/bin/sh\nexit 1\n")
            with self.assertRaisesRegex(ValueError, "scheduler executable changed"):
                controller.revalidate_anchor(anchor)


if __name__ == "__main__":
    unittest.main()
