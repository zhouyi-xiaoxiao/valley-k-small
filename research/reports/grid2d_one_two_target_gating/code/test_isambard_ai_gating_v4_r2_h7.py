#!/usr/bin/env python3
"""Killing tests for the H7 closed-world packaging boundary."""
from __future__ import annotations

import os
import shutil
import tempfile
import unittest
from pathlib import Path

import build_isambard_ai_v4_r2_h7_payload as build


class H7ClosedWorldTests(unittest.TestCase):
    def package(self) -> tuple[tempfile.TemporaryDirectory, Path]:
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name) / "h7"
        root.mkdir(mode=0o700)
        relatives = (*build.MEMBERS, build.MANIFEST_RELATIVE)
        for relative in relatives:
            source = build.ROOT / relative
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
            os.chmod(target, 0o600)
        for directory, children, _files in os.walk(root):
            os.chmod(directory, 0o700)
            for child in children:
                os.chmod(Path(directory) / child, 0o700)
        return temporary, root

    def verify(self, root: Path) -> dict:
        return build.verify_closed_world(root, build.sha(build.OUT))

    def test_exact_closed_world_package_passes(self):
        temporary, root = self.package()
        with temporary:
            receipt = self.verify(root)
            self.assertEqual(receipt["status"],
                             "PASS_H7_CLOSED_WORLD_PACKAGE")
            self.assertEqual(receipt["manifest_members"], 118)
            self.assertEqual(receipt["total_files"], 119)
            self.assertFalse(receipt["authorizes_slurm_submission"])

    def test_missing_member_rejected(self):
        temporary, root = self.package()
        with temporary:
            (root / build.V3_PACK_RELATIVE).unlink()
            with self.assertRaisesRegex(ValueError, "inventory drift"):
                self.verify(root)

    def test_extra_member_rejected(self):
        temporary, root = self.package()
        with temporary:
            extra = root / "unexpected.txt"
            extra.write_bytes(b"unexpected")
            os.chmod(extra, 0o600)
            with self.assertRaisesRegex(ValueError, "inventory drift"):
                self.verify(root)

    def test_extra_empty_directory_rejected(self):
        temporary, root = self.package()
        with temporary:
            extra = root / "unexpected-directory"
            extra.mkdir(mode=0o700)
            with self.assertRaisesRegex(ValueError,
                                        "directory inventory drift"):
                self.verify(root)

    def test_member_byte_drift_rejected(self):
        temporary, root = self.package()
        with temporary:
            target = root / build.H7_MEMBERS[2]
            target.write_bytes(target.read_bytes() + b"\n")
            os.chmod(target, 0o600)
            with self.assertRaisesRegex(ValueError, "member byte drift"):
                self.verify(root)

    def test_member_mode_drift_rejected(self):
        temporary, root = self.package()
        with temporary:
            os.chmod(root / build.V3_PACK_RELATIVE, 0o644)
            with self.assertRaisesRegex(ValueError, "member mode drift"):
                self.verify(root)

    def test_member_external_hardlink_rejected(self):
        temporary, root = self.package()
        with temporary:
            target = root / build.V3_PACK_RELATIVE
            external = Path(temporary.name) / "external-pack.npz"
            target.replace(external)
            os.link(external, target)
            with self.assertRaisesRegex(ValueError, "link-count drift"):
                self.verify(root)

    def test_member_symlink_rejected(self):
        temporary, root = self.package()
        with temporary:
            target = root / build.V3_PACK_RELATIVE
            external = Path(temporary.name) / "external-pack.npz"
            target.replace(external)
            target.symlink_to(external)
            with self.assertRaisesRegex(ValueError,
                                        "non-regular or symlinked"):
                self.verify(root)

    def test_external_manifest_anchor_rejected(self):
        temporary, root = self.package()
        with temporary:
            with self.assertRaisesRegex(ValueError,
                                        "external manifest anchor drift"):
                build.verify_closed_world(root, "0" * 64)

    def test_append_only_parent_and_v3_pack_anchors(self):
        self.assertEqual(build.h6.verify(), build.H6_PAYLOAD_SHA256)
        self.assertEqual(build.sha(build.ROOT / build.V3_PACK_RELATIVE),
                         build.V3_PACK_SHA256)
        self.assertEqual(build.MEMBERS[:len(build.h6.MEMBERS)],
                         build.h6.MEMBERS)
        self.assertEqual(build.H7_MEMBERS[0],
                         "notes/isambard_ai_v4_r2_h6_payload.sha256")
        self.assertIn(build.V3_PACK_RELATIVE, build.H7_MEMBERS)


if __name__ == "__main__":
    unittest.main()
