#!/usr/bin/env python3
"""Vendor promoted skills from mattpocock/skills into this Cursor plugin."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
UPSTREAM_URL = "https://github.com/mattpocock/skills.git"
CACHE_DIR = ROOT / ".cache" / "mattpocock-skills"
PLUGIN_NAME = "cursor-plugin"
PLUGIN_DISPLAY_NAME = "cursor-plugin"


def _run(args: list[str], cwd: Path) -> str:
    result = subprocess.run(args, cwd=cwd, check=True, capture_output=True, text=True)
    return result.stdout.strip()


def fetch_upstream(cache_dir: Path = CACHE_DIR) -> str:
    cache_dir.parent.mkdir(parents=True, exist_ok=True)
    if (cache_dir / ".git").is_dir():
        _run(["git", "fetch", "--depth", "1", "origin", "main"], cwd=cache_dir)
        _run(["git", "reset", "--hard", "origin/main"], cwd=cache_dir)
    else:
        _run(
            ["git", "clone", "--depth", "1", UPSTREAM_URL, str(cache_dir)],
            cwd=cache_dir.parent,
        )
    return _run(["git", "rev-parse", "HEAD"], cwd=cache_dir)


def _normalize_skill_rel(rel: str) -> str:
    return rel[2:] if rel.startswith("./") else rel


def sync_from_upstream(
    *,
    upstream: Path,
    dest: Path,
    sha: str,
    now: datetime | None = None,
) -> dict[str, Any]:
    manifest_path = upstream / ".claude-plugin" / "plugin.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    skill_rels = [_normalize_skill_rel(rel) for rel in manifest["skills"]]

    missing = [rel for rel in skill_rels if not (upstream / rel / "SKILL.md").is_file()]
    if missing:
        raise SystemExit("upstream skills missing SKILL.md:\n" + "\n".join(missing))

    skills_root = dest / "skills"
    if skills_root.exists():
        shutil.rmtree(skills_root)

    copied: list[str] = []
    for rel in skill_rels:
        src = upstream / rel
        target = dest / rel
        shutil.copytree(src, target)
        copied.append("./" + rel)

    license_src = upstream / "LICENSE"
    if license_src.is_file():
        shutil.copy2(license_src, dest / "LICENSE.mattpocock")

    stamp = (now or datetime.now(timezone.utc)).strftime("%Y-%m-%dT%H:%M:%SZ")
    lock = {
        "upstream": UPSTREAM_URL,
        "sha": sha,
        "version": manifest.get("version", "0.0.0"),
        "synced_at": stamp,
        "skills": copied,
    }
    (dest / "sources.lock.json").write_text(
        json.dumps(lock, indent=2) + "\n", encoding="utf-8"
    )

    plugin_dir = dest / ".cursor-plugin"
    plugin_dir.mkdir(parents=True, exist_ok=True)
    plugin = {
        "name": PLUGIN_NAME,
        "displayName": PLUGIN_DISPLAY_NAME,
        "description": (
            "Personal Cursor plugin. Currently vendors Matt Pocock's promoted "
            "engineering and productivity skills (MIT)."
        ),
        "version": manifest.get("version", "0.0.0"),
        "author": {"name": "void"},
        "homepage": manifest.get("homepage"),
        "repository": manifest.get("repository", UPSTREAM_URL),
        "license": manifest.get("license", "MIT"),
        "keywords": manifest.get("keywords", []),
        "skills": copied,
    }
    (plugin_dir / "plugin.json").write_text(
        json.dumps(plugin, indent=2) + "\n", encoding="utf-8"
    )
    return lock


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--upstream",
        type=Path,
        help="Existing clone of mattpocock/skills (skips fetch)",
    )
    args = parser.parse_args()

    if args.upstream:
        upstream = args.upstream.resolve()
        sha = _run(["git", "rev-parse", "HEAD"], cwd=upstream)
    else:
        sha = fetch_upstream()
        upstream = CACHE_DIR

    lock = sync_from_upstream(upstream=upstream, dest=ROOT, sha=sha)
    print(
        f"Synced {len(lock['skills'])} skills from mattpocock/skills@{sha[:7]} "
        f"(v{lock['version']})"
    )


if __name__ == "__main__":
    main()
