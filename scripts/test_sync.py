#!/usr/bin/env python3
"""Tests for syncing promoted skills from a fake upstream tree."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from sync import sync_from_upstream  # noqa: E402


def _write_skill(root: Path, rel: str, body: str) -> None:
    path = root / rel / "SKILL.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    (path.parent / "notes.md").write_text("supporting file\n", encoding="utf-8")


class SyncFromUpstreamTests(unittest.TestCase):
    def test_copies_only_promoted_skills_and_rewrites_cursor_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            upstream = Path(tmp) / "upstream"
            dest = Path(tmp) / "dest"
            dest.mkdir()

            _write_skill(upstream, "skills/engineering/tdd", "# tdd\n")
            _write_skill(upstream, "skills/productivity/grill-me", "# grill-me\n")
            _write_skill(upstream, "skills/deprecated/old", "# old\n")
            (upstream / "LICENSE").write_text("MIT License\nCopyright (c) 2026 Matt Pocock\n")
            manifest = {
                "name": "mattpocock-skills",
                "version": "1.2.3",
                "description": "upstream",
                "author": {"name": "Matt Pocock"},
                "homepage": "https://www.aihero.dev",
                "repository": "https://github.com/mattpocock/skills",
                "license": "MIT",
                "keywords": ["tdd"],
                "skills": [
                    "./skills/engineering/tdd",
                    "./skills/productivity/grill-me",
                ],
            }
            (upstream / ".claude-plugin").mkdir()
            (upstream / ".claude-plugin" / "plugin.json").write_text(
                json.dumps(manifest), encoding="utf-8"
            )

            lock = sync_from_upstream(
                upstream=upstream,
                dest=dest,
                sha="abc123def",
            )

            self.assertTrue((dest / "skills/engineering/tdd/SKILL.md").is_file())
            self.assertTrue((dest / "skills/engineering/tdd/notes.md").is_file())
            self.assertTrue((dest / "skills/productivity/grill-me/SKILL.md").is_file())
            self.assertFalse((dest / "skills/deprecated/old/SKILL.md").exists())
            self.assertTrue((dest / "LICENSE.mattpocock").is_file())

            plugin = json.loads((dest / ".cursor-plugin/plugin.json").read_text())
            self.assertEqual(plugin["name"], "cursor-plugin")
            self.assertEqual(
                plugin["skills"],
                ["./skills/engineering/tdd", "./skills/productivity/grill-me"],
            )
            self.assertEqual(plugin["license"], "MIT")

            self.assertEqual(lock["upstream"], "https://github.com/mattpocock/skills.git")
            self.assertEqual(lock["sha"], "abc123def")
            self.assertEqual(lock["version"], "1.2.3")
            self.assertEqual(len(lock["skills"]), 2)

    def test_keeps_only_engineering_and_productivity_buckets(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            upstream = Path(tmp) / "upstream"
            dest = Path(tmp) / "dest"
            dest.mkdir()
            _write_skill(upstream, "skills/engineering/tdd", "# tdd\n")
            _write_skill(upstream, "skills/engineering/new-in-bucket", "# extra\n")
            _write_skill(upstream, "skills/productivity/grill-me", "# grill-me\n")
            _write_skill(upstream, "skills/misc/migrate-to-shoehorn", "# no\n")
            _write_skill(upstream, "skills/in-progress/loop-me", "# no\n")
            (upstream / ".claude-plugin").mkdir()
            (upstream / ".claude-plugin" / "plugin.json").write_text(
                json.dumps(
                    {
                        "name": "mattpocock-skills",
                        "version": "1.2.3",
                        "skills": [
                            "./skills/engineering/tdd",
                            "./skills/productivity/grill-me",
                            "./skills/misc/migrate-to-shoehorn",
                        ],
                    }
                ),
                encoding="utf-8",
            )

            lock = sync_from_upstream(upstream=upstream, dest=dest, sha="abc")

            self.assertTrue((dest / "skills/engineering/tdd/SKILL.md").is_file())
            self.assertTrue((dest / "skills/engineering/new-in-bucket/SKILL.md").is_file())
            self.assertTrue((dest / "skills/productivity/grill-me/SKILL.md").is_file())
            self.assertFalse((dest / "skills/misc").exists())
            self.assertFalse((dest / "skills/in-progress").exists())
            self.assertEqual(
                lock["skills"],
                [
                    "./skills/engineering/new-in-bucket",
                    "./skills/engineering/tdd",
                    "./skills/productivity/grill-me",
                ],
            )

    def test_replaces_previously_vendored_skills_that_left_the_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            upstream = Path(tmp) / "upstream"
            dest = Path(tmp) / "dest"
            _write_skill(upstream, "skills/engineering/tdd", "# tdd\n")
            _write_skill(dest, "skills/engineering/retired", "# retired\n")
            (upstream / ".claude-plugin").mkdir(parents=True)
            (upstream / ".claude-plugin" / "plugin.json").write_text(
                json.dumps(
                    {
                        "name": "mattpocock-skills",
                        "version": "9.0.0",
                        "skills": ["./skills/engineering/tdd"],
                    }
                ),
                encoding="utf-8",
            )

            sync_from_upstream(upstream=upstream, dest=dest, sha="fff")

            self.assertTrue((dest / "skills/engineering/tdd/SKILL.md").is_file())
            self.assertFalse((dest / "skills/engineering/retired/SKILL.md").exists())


if __name__ == "__main__":
    unittest.main()
