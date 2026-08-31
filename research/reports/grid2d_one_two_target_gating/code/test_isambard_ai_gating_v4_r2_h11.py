#!/usr/bin/env python3
"""H11 killing tests for live accounting, scheduler recovery, and output transactions."""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import stat
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import build_isambard_ai_v4_r2_h11_payload as build
import h11_pinned_controller_v4_r2 as controller
import h11_runtime_v4_r2 as runtime


class H11Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.anchor = build.candidate_sha()
        controller.H11_SHA = cls.anchor

    def deploy(self, base: Path) -> Path:
        package = base / "package"
        package.mkdir(mode=0o700)
        for name in build.MEMBERS:
            target = package / name
            target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            shutil.copyfile(build.ROOT / name, target)
            os.chmod(target, 0o600)
        manifest = package / runtime.MAN
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
        state.write_text(json.dumps({"next": 9400000, "jobs": {}}))
        os.chmod(state, 0o600)
        sbatch = tools / "sbatch"
        sbatch.write_text(
            """#!/usr/bin/env python3
import json,os,sys
from pathlib import Path
s=Path(os.environ["H11_FAKE_STATE"]); v=json.loads(s.read_text()); j=str(v["next"]); v["next"]+=1
args=sys.argv[1:]; comment=next(x.split("=",1)[1] for x in args if x.startswith("--comment=")); work=next(x.split("=",1)[1] for x in args if x.startswith("--chdir=")); dep=next((x.split(":",1)[1] for x in args if x.startswith("--dependency=")),None)
script=s.parent/f"job-{j}.sh"; raw=sys.stdin.buffer.read(); script.write_bytes(raw); os.chmod(script,0o700)
v["jobs"][j]={"comment":comment,"work":work,"dep":dep,"state":"PENDING","reason":"JobHeldUser","script":str(script),"array":b"#SBATCH --array=" in raw}
s.write_text(json.dumps(v)); print(j)
"""
        )
        os.chmod(sbatch, 0o700)
        squeue = tools / "squeue"
        squeue.write_text(
            """#!/usr/bin/env python3
import json,os
v=json.load(open(os.environ["H11_FAKE_STATE"]))
for j,x in v["jobs"].items():
 if x["state"] in ("PENDING","RUNNING"): print(f"{j}|{x['comment']}|{x['state']}|{x['reason']}")
"""
        )
        os.chmod(squeue, 0o700)
        scontrol = tools / "scontrol"
        scontrol.write_text(
            """#!/usr/bin/env python3
import json,os,subprocess,sys,tempfile
from pathlib import Path
s=Path(os.environ["H11_FAKE_STATE"]); v=json.loads(s.read_text()); command=sys.argv[1]; j=sys.argv[-1]; x=v["jobs"][j]
if command=="show":
 dep="afterok:"+x["dep"] if x["dep"] else "(null)"
 print(f"JobId={j} JobState={x['state']} Reason={x['reason']} Comment={x['comment']} WorkDir={x['work']} Dependency={dep} Command=/tmp/slurm_script StdIn=/dev/null")
 raise SystemExit
if command=="release":
 x["state"]="RUNNING"; x["reason"]="None"; s.write_text(json.dumps(v))
 env=os.environ.copy(); tmp=Path(tempfile.mkdtemp(prefix="h11-fake-")).resolve(); env.update({"SLURM_JOB_ID":j,"SLURM_TMPDIR":str(tmp)})
 cp=subprocess.run(["bash",x["script"]],env=env,capture_output=True)
 v=json.loads(s.read_text()); v["jobs"][j]["state"]="COMPLETED" if cp.returncode==0 else "FAILED"; v["jobs"][j]["reason"]="None"; s.write_text(json.dumps(v))
 if cp.returncode: sys.stderr.buffer.write(cp.stderr); raise SystemExit(cp.returncode)
 print("released",j)
"""
        )
        os.chmod(scontrol, 0o700)
        sacct = tools / "sacct"
        sacct.write_text(
            """#!/usr/bin/env python3
import sys
j=sys.argv[sys.argv.index("-j")+1]
print(f"{j}|{j}|COMPLETED|0:0|7")
"""
        )
        os.chmod(sacct, 0o700)
        return state, sbatch, squeue, scontrol, sacct

    def setup_scheduler(self, temporary: str):
        base = Path(temporary).resolve()
        os.chmod(base, 0o700)
        package = self.deploy(base)
        run = base / "run"
        state, sbatch, squeue, scontrol, sacct = self.fake_tools(base)
        tools = tuple(map(str, (sbatch, squeue, scontrol, sacct)))
        return base, package, run, state, tools

    def submit_upstream(self, package, run, tools, environment):
        sbatch, squeue, scontrol, sacct = tools
        with patch.dict(os.environ, environment, clear=False):
            return controller.submit(
                package,
                run,
                "selftest_upstream",
                ["alpha", "one"],
                [],
                None,
                sbatch,
                squeue,
                scontrol,
                sacct,
            )

    def test_frozen_h7_through_h10_and_append_only_prefix(self):
        self.assertEqual(build.h10.verify(), build.H10_SHA)
        self.assertEqual(build.MEMBERS[: len(build.h10.MEMBERS)], build.h10.MEMBERS)
        expected = {
            "h7": "7cb7c5d0d6e34e9133ce74d81da69c4814ebd9db5af30081ae1a426abefcceee",
            "h8": "bb815db83632e67bf5b6c2d6f527bed2b3f9eaae4e1ac5c668a761b38065297a",
            "h9": "a00f515ab15bd25c2c6a028420ca4339d69ce13d3abf07ce78eff688eb470bfa",
            "h10": build.H10_SHA,
        }
        for tag, digest in expected.items():
            path = build.ROOT / f"notes/isambard_ai_v4_r2_{tag}_payload.sha256"
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), digest)

    def test_live_array_fixture_exact_480_and_identity_join(self):
        raw = (build.ROOT / "notes/isambard_ai_v4_r2_h10_sacct_live_array_fixture.psv").read_text()
        rows = controller.parse_array(raw, "9000000")
        self.assertEqual(len(rows), 480)
        self.assertEqual({row["array_task_id"] for row in rows}, set(range(480)))
        self.assertEqual(len({row["job_id_raw"] for row in rows}), 480)
        self.assertEqual(
            controller.runtime_identity(rows[37]),
            {
                "job_id_raw": "9100037",
                "job_id": "9000000_37",
                "array_job_id": "9000000",
                "array_task_id": 37,
            },
        )
        self.assertNotIn("state", controller.runtime_identity(rows[37]))

    def test_squeue_groups_array_rows_by_logical_parent_and_rejects_duplicate_parent(self):
        intent = "a" * 64
        raw = (
            f"7000000|H11:{intent}|PENDING|JobHeldUser\n"
            f"7000000|H11:{intent}|PENDING|JobHeldUser\n"
        )
        self.assertEqual(set(controller.parse_squeue(raw, intent)), {"7000000"})
        duplicate = raw + f"7000001|H11:{intent}|PENDING|JobHeldUser\n"
        self.assertEqual(set(controller.parse_squeue(duplicate, intent)), {"7000000", "7000001"})

    def test_scontrol_readback_requires_exact_fields_not_substrings(self):
        intent = "b" * 64
        run = Path("/tmp/h11-safe-run")
        raw = (
            f"JobId=7000000 JobState=PENDING Reason=JobHeldUser Comment=H11:{intent} "
            f"WorkDir={run} Dependency=afterok:6999999 Command=/tmp/slurm_script StdIn=/dev/null\n"
        )
        evidence = {
            "argv": ["scontrol", "show", "job", "-o", "7000000"],
            "raw_stdout": raw,
            "raw_stdout_sha256": hashlib.sha256(raw.encode()).hexdigest(),
            "fields": controller.parse_scontrol(raw),
        }
        controller.validate_held(evidence, "7000000", intent, run, "6999999")
        bad = {**evidence, "raw_stdout": raw.replace(str(run), str(run) + "-suffix")}
        bad["raw_stdout_sha256"] = hashlib.sha256(bad["raw_stdout"].encode()).hexdigest()
        bad["fields"] = controller.parse_scontrol(bad["raw_stdout"])
        with self.assertRaisesRegex(ValueError, "exact WorkDir"):
            controller.validate_held(bad, "7000000", intent, run, "6999999")

    def test_fullnode_science_bytes_and_directives(self):
        science = build.ROOT / controller.SCRIPTS["production"]
        self.assertEqual(
            runtime.sha(science),
            "30df2636b4459a3ff6c91ccb1cd6bca9e9ab7a6017a0bc4a334e4fbf64fc4bbe",
        )
        text = science.read_text()
        for directive in (
            "#SBATCH --nodes=1",
            "#SBATCH --ntasks=4",
            "#SBATCH --gpus=4",
            "#SBATCH --gpus-per-task=1",
            "#SBATCH --array=0-479%240",
        ):
            self.assertIn(directive, text)

    def test_two_job_fake_scheduler_end_to_end_and_accounting_raw_replay(self):
        with tempfile.TemporaryDirectory() as temporary:
            _, package, run, state, tools = self.setup_scheduler(temporary)
            environment = {"H11_FAKE_STATE": str(state), "H9_TEST_OUTPUT_NAME": "up"}
            upstream = self.submit_upstream(package, run, tools, environment)
            upstream_job = upstream["submission"]["job_id"]
            upstream_output = run / "artifacts/h9_e2e/up.txt"
            self.assertEqual(upstream_output.read_text(), "alpha:one\n")
            environment["H9_TEST_OUTPUT_NAME"] = "down"
            sbatch, squeue, scontrol, sacct = tools
            with patch.dict(os.environ, environment, clear=False):
                downstream = controller.submit(
                    package,
                    run,
                    "selftest_downstream",
                    ["beta", "two"],
                    [f"artifacts/h9_e2e/up.txt={runtime.sha(upstream_output)}"],
                    upstream_job,
                    sbatch,
                    squeue,
                    scontrol,
                    sacct,
                )
            self.assertEqual((run / "artifacts/h9_e2e/down.txt").read_text(), "beta:two\n")
            self.assertEqual(downstream["submission"]["dependency_afterok"], upstream_job)
            accounting = controller.json_mode(
                controller.accounting_path(run, "selftest_upstream", upstream_job)
            )
            self.assertEqual(
                hashlib.sha256(accounting["raw_stdout"].encode()).hexdigest(),
                accounting["raw_stdout_sha256"],
            )
            self.assertEqual(
                accounting["argv"][-1],
                "JobIDRaw,JobID,State,ExitCode,ElapsedRaw",
            )

    def test_crash_after_intent_before_dispatch_recovers(self):
        with tempfile.TemporaryDirectory() as temporary:
            _, package, run, state, tools = self.setup_scheduler(temporary)
            environment = {
                "H11_FAKE_STATE": str(state),
                "H9_TEST_OUTPUT_NAME": "intent",
                "H11_TEST_CRASH_AFTER_INTENT": "1",
            }
            with self.assertRaisesRegex(RuntimeError, "post-intent"):
                self.submit_upstream(package, run, tools, environment)
            environment.pop("H11_TEST_CRASH_AFTER_INTENT")
            result = self.submit_upstream(package, run, tools, environment)
            self.assertEqual(result["release"]["status"], "RELEASED_AFTER_DURABLE_SUBMISSION_RECEIPT")

    def test_crash_after_dispatch_before_sbatch_recovers(self):
        with tempfile.TemporaryDirectory() as temporary:
            _, package, run, state, tools = self.setup_scheduler(temporary)
            environment = {
                "H11_FAKE_STATE": str(state),
                "H9_TEST_OUTPUT_NAME": "dispatch",
                "H11_TEST_CRASH_AFTER_DISPATCH_BEFORE_SBATCH": "1",
            }
            with self.assertRaisesRegex(RuntimeError, "pre-sbatch"):
                self.submit_upstream(package, run, tools, environment)
            self.assertEqual(json.loads(state.read_text())["jobs"], {})
            environment.pop("H11_TEST_CRASH_AFTER_DISPATCH_BEFORE_SBATCH")
            self.submit_upstream(package, run, tools, environment)
            attempts = list((run / "artifacts/h11_dispatch").glob("*.json"))
            self.assertGreaterEqual(len(attempts), 3)

    def test_crash_after_sbatch_before_claim_recovers_by_unique_comment(self):
        with tempfile.TemporaryDirectory() as temporary:
            _, package, run, state, tools = self.setup_scheduler(temporary)
            environment = {
                "H11_FAKE_STATE": str(state),
                "H9_TEST_OUTPUT_NAME": "accepted",
                "H11_TEST_CRASH_AFTER_SBATCH_BEFORE_CLAIM": "1",
            }
            with self.assertRaisesRegex(RuntimeError, "pre-claim"):
                self.submit_upstream(package, run, tools, environment)
            self.assertEqual(len(json.loads(state.read_text())["jobs"]), 1)
            environment.pop("H11_TEST_CRASH_AFTER_SBATCH_BEFORE_CLAIM")
            result = self.submit_upstream(package, run, tools, environment)
            self.assertEqual(result["submission"]["status"], "PASS_EXACT_UNIQUE_HELD_JOB_DURABLE_BEFORE_RELEASE")

    def test_crash_after_submission_receipt_before_release_recovers(self):
        with tempfile.TemporaryDirectory() as temporary:
            _, package, run, state, tools = self.setup_scheduler(temporary)
            environment = {
                "H11_FAKE_STATE": str(state),
                "H9_TEST_OUTPUT_NAME": "receipt",
                "H11_TEST_CRASH_AFTER_SUBMISSION_RECEIPT": "1",
            }
            with self.assertRaisesRegex(RuntimeError, "pre-release"):
                self.submit_upstream(package, run, tools, environment)
            job = next(iter(json.loads(state.read_text())["jobs"]))
            self.assertTrue(controller.submission_path(run, "selftest_upstream", job).exists())
            environment.pop("H11_TEST_CRASH_AFTER_SUBMISSION_RECEIPT")
            result = self.submit_upstream(package, run, tools, environment)
            self.assertEqual(result["submission"]["job_id"], job)

    def test_crash_after_release_intent_before_release_recovers(self):
        with tempfile.TemporaryDirectory() as temporary:
            _, package, run, state, tools = self.setup_scheduler(temporary)
            environment = {
                "H11_FAKE_STATE": str(state),
                "H9_TEST_OUTPUT_NAME": "release-intent",
                "H11_TEST_CRASH_AFTER_RELEASE_INTENT": "1",
            }
            with self.assertRaisesRegex(RuntimeError, "release-intent"):
                self.submit_upstream(package, run, tools, environment)
            environment.pop("H11_TEST_CRASH_AFTER_RELEASE_INTENT")
            result = self.submit_upstream(package, run, tools, environment)
            self.assertEqual(result["release"]["status"], "RELEASED_AFTER_DURABLE_SUBMISSION_RECEIPT")

    def test_crash_after_scontrol_release_before_receipt_recovers_without_rewriting_submission(self):
        with tempfile.TemporaryDirectory() as temporary:
            _, package, run, state, tools = self.setup_scheduler(temporary)
            environment = {
                "H11_FAKE_STATE": str(state),
                "H9_TEST_OUTPUT_NAME": "post-release",
                "H11_TEST_CRASH_AFTER_SCONTROL_RELEASE": "1",
            }
            with self.assertRaisesRegex(RuntimeError, "post-scontrol-release"):
                self.submit_upstream(package, run, tools, environment)
            job = next(iter(json.loads(state.read_text())["jobs"]))
            submission = controller.submission_path(run, "selftest_upstream", job)
            before = runtime.sha(submission)
            environment.pop("H11_TEST_CRASH_AFTER_SCONTROL_RELEASE")
            result = self.submit_upstream(package, run, tools, environment)
            self.assertEqual(
                result["release"]["status"],
                "RECOVERED_ALREADY_RELEASED_AFTER_DURABLE_RELEASE_INTENT",
            )
            self.assertEqual(runtime.sha(submission), before)

    def test_repeated_submit_after_release_is_idempotent(self):
        with tempfile.TemporaryDirectory() as temporary:
            _, package, run, state, tools = self.setup_scheduler(temporary)
            environment = {"H11_FAKE_STATE": str(state), "H9_TEST_OUTPUT_NAME": "repeat"}
            first = self.submit_upstream(package, run, tools, environment)
            second = self.submit_upstream(package, run, tools, environment)
            self.assertEqual(first, second)
            self.assertEqual(len(json.loads(state.read_text())["jobs"]), 1)

    def test_duplicate_same_comment_fails_closed_even_with_one_known_job(self):
        with tempfile.TemporaryDirectory() as temporary:
            _, package, run, state, tools = self.setup_scheduler(temporary)
            environment = {
                "H11_FAKE_STATE": str(state),
                "H9_TEST_OUTPUT_NAME": "duplicate",
                "H11_TEST_CRASH_AFTER_SBATCH_BEFORE_CLAIM": "1",
            }
            with self.assertRaises(RuntimeError):
                self.submit_upstream(package, run, tools, environment)
            value = json.loads(state.read_text())
            job = next(iter(value["jobs"]))
            value["jobs"]["9499999"] = {**value["jobs"][job]}
            state.write_text(json.dumps(value))
            os.chmod(state, 0o600)
            environment.pop("H11_TEST_CRASH_AFTER_SBATCH_BEFORE_CLAIM")
            with self.assertRaisesRegex(ValueError, "duplicate same-comment"):
                self.submit_upstream(package, run, tools, environment)
            self.assertTrue(
                all(item["reason"] == "JobHeldUser" for item in json.loads(state.read_text())["jobs"].values())
            )

    def test_dependency_tamper_is_rejected_before_release(self):
        with tempfile.TemporaryDirectory() as temporary:
            _, package, run, state, tools = self.setup_scheduler(temporary)
            environment = {"H11_FAKE_STATE": str(state), "H9_TEST_OUTPUT_NAME": "up"}
            upstream = self.submit_upstream(package, run, tools, environment)
            upstream_job = upstream["submission"]["job_id"]
            input_path = run / "artifacts/h9_e2e/up.txt"
            environment.update(
                {
                    "H9_TEST_OUTPUT_NAME": "down",
                    "H11_TEST_CRASH_AFTER_SBATCH_BEFORE_CLAIM": "1",
                }
            )
            sbatch, squeue, scontrol, sacct = tools
            with patch.dict(os.environ, environment, clear=False):
                with self.assertRaises(RuntimeError):
                    controller.submit(
                        package,
                        run,
                        "selftest_downstream",
                        ["beta", "two"],
                        [f"artifacts/h9_e2e/up.txt={runtime.sha(input_path)}"],
                        upstream_job,
                        sbatch,
                        squeue,
                        scontrol,
                        sacct,
                    )
            value = json.loads(state.read_text())
            downstream_job = str(max(map(int, value["jobs"])))
            value["jobs"][downstream_job]["dep"] = "9999999"
            state.write_text(json.dumps(value))
            os.chmod(state, 0o600)
            environment.pop("H11_TEST_CRASH_AFTER_SBATCH_BEFORE_CLAIM")
            with patch.dict(os.environ, environment, clear=False):
                with self.assertRaisesRegex(ValueError, "exact Dependency"):
                    controller.submit(
                        package,
                        run,
                        "selftest_downstream",
                        ["beta", "two"],
                        [f"artifacts/h9_e2e/up.txt={runtime.sha(input_path)}"],
                        upstream_job,
                        sbatch,
                        squeue,
                        scontrol,
                        sacct,
                    )

    def transaction_fixture(self, base: Path, count: int = 2):
        run = base / "run"
        snapshot = base / "snapshot"
        run.mkdir(mode=0o700)
        snapshot.mkdir(mode=0o700)
        outputs = []
        for index in range(count):
            name = f"artifacts/out/file-{index}.txt"
            path = snapshot / name
            path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            path.write_text(f"value-{index}\n")
            os.chmod(path, 0o600)
            outputs.append({"path": name, "sha256": runtime.sha(path)})
        receipt = {
            "schema": "h11-runtime-receipt-v1",
            "status": "test",
            "outputs": outputs,
        }
        return run, snapshot, outputs, receipt

    def test_transaction_staged_inode_is_immutable_and_partial_promotion_recovers(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary).resolve()
            run, snapshot, outputs, receipt = self.transaction_fixture(base)
            tx = runtime.prepare_transaction(run, "phase-1", outputs, snapshot, receipt)
            with self.assertRaisesRegex(RuntimeError, "promotion crash"):
                runtime.recover_transaction(tx, crash_after=1)
            runtime.recover_transaction(tx)
            for item in outputs:
                staged = tx / "staged" / item["path"]
                target = run / item["path"]
                self.assertNotEqual(staged.stat().st_ino, target.stat().st_ino)
                self.assertEqual(staged.stat().st_nlink, target.stat().st_nlink, 1)
                self.assertEqual(stat.S_IMODE(staged.stat().st_mode), 0o400)
                self.assertEqual(stat.S_IMODE(target.stat().st_mode), 0o600)

    def test_transaction_post_link_and_post_commit_crashes_recover(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary).resolve()
            run, snapshot, outputs, receipt = self.transaction_fixture(base, 1)
            tx = runtime.prepare_transaction(run, "phase-link", outputs, snapshot, receipt)
            with self.assertRaisesRegex(RuntimeError, "post-link"):
                runtime.recover_transaction(tx, crash_after_link=0)
            runtime.recover_transaction(tx)
            target = run / outputs[0]["path"]
            self.assertEqual(target.stat().st_nlink, 1)
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary).resolve()
            run, snapshot, outputs, receipt = self.transaction_fixture(base, 1)
            tx = runtime.prepare_transaction(run, "phase-commit", outputs, snapshot, receipt)
            with self.assertRaisesRegex(RuntimeError, "post-commit"):
                runtime.recover_transaction(tx, crash_after_commit=True)
            runtime.recover_transaction(tx)
            self.assertTrue((run / "artifacts/h11_receipts/phase-commit.json").exists())

    def test_target_mutation_does_not_corrupt_stage_and_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary).resolve()
            run, snapshot, outputs, receipt = self.transaction_fixture(base, 1)
            tx = runtime.prepare_transaction(run, "phase-mutate", outputs, snapshot, receipt)
            runtime.recover_transaction(tx)
            staged = tx / "staged" / outputs[0]["path"]
            original = runtime.sha(staged)
            target = run / outputs[0]["path"]
            target.write_text("mutated\n")
            self.assertEqual(runtime.sha(staged), original)
            with self.assertRaisesRegex(ValueError, "existing target drift"):
                runtime.recover_transaction(tx)

    def test_claimed_transaction_and_unclaimed_incomplete_preparation_are_handled(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary).resolve()
            run, snapshot, outputs, receipt = self.transaction_fixture(base, 1)
            environment = {"H11_TEST_CRASH_AFTER_TRANSACTION_CLAIM": "1"}
            with patch.dict(os.environ, environment, clear=False):
                with self.assertRaisesRegex(RuntimeError, "post-claim"):
                    runtime.prepare_transaction(run, "phase-claim", outputs, snapshot, receipt)
            result = runtime.recover_all(run)
            self.assertIn("phase-claim", result["recovered"])
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary).resolve()
            run, snapshot, outputs, receipt = self.transaction_fixture(base, 1)
            environment = {"H11_TEST_CRASH_AFTER_STAGE": "1"}
            with patch.dict(os.environ, environment, clear=False):
                with self.assertRaisesRegex(RuntimeError, "pre-claim"):
                    runtime.prepare_transaction(run, "phase-orphan", outputs, snapshot, receipt)
            result = runtime.recover_all(run)
            self.assertEqual(result["recovered"], [])
            self.assertEqual(len(result["ignored_unclaimed_preparation_orphans"]), 1)


if __name__ == "__main__":
    unittest.main()
