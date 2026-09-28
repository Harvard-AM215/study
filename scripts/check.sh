#!/usr/bin/env bash
# Checks run locally and on every pull request. No network.
#  1. The Codex and Claude Code copies of the skill are identical.
#  2. The download script's offline tests pass.
#  3. If the textbook has been downloaded, every textbook file named in course/lectures.md is in
#     textbook/, apart from chapters the index says are not public yet.
set -euo pipefail
cd "$(dirname "$0")/.."
status=0
if ! cmp -s .agents/skills/study/SKILL.md .claude/skills/study/SKILL.md; then
  echo "FAIL: .agents/skills/study/SKILL.md and .claude/skills/study/SKILL.md differ" >&2
  status=1
fi
if ! python3 scripts/test_get_textbook.py >/dev/null 2>&1; then
  echo "FAIL: scripts/test_get_textbook.py" >&2
  status=1
fi
if [ -d textbook ]; then
  # A chapter that is not public yet is allowed only where the index says "will then be in <file>".
  while read -r f; do
    if [ ! -f "$f" ] && ! grep -q "will then be in \`$f\`" course/lectures.md; then
      echo "FAIL: course/lectures.md names $f, which is not in textbook/" >&2
      status=1
    fi
  done < <(grep -o 'textbook/[A-Za-z0-9_]*\.md' course/lectures.md | sort -u)
else
  echo "note: textbook/ not downloaded; skipped the index check (run scripts/get_textbook.py)"
fi
[ "$status" -eq 0 ] && echo "ok"
exit "$status"
