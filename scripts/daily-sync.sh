#!/usr/bin/env bash
# Daily job: refresh vendored skills, commit, and push if a remote exists.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

python3 "$ROOT/scripts/test_sync.py"
python3 "$ROOT/scripts/sync.py"

if git diff --quiet && git diff --cached --quiet && [[ -z "$(git ls-files --others --exclude-standard)" ]]; then
  echo "No skill changes."
  exit 0
fi

sha="$(python3 -c 'import json; print(json.load(open("sources.lock.json"))["sha"][:7])')"
git add -A
git commit -m "chore(sync): mattpocock/skills@${sha}"

if git remote get-url origin >/dev/null 2>&1; then
  git pull --rebase --autostash origin "$(git rev-parse --abbrev-ref HEAD)"
  git push origin HEAD
fi
