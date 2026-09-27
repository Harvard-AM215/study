#!/usr/bin/env bash
# Checks run locally and on every pull request.
#  1. The Codex and Claude Code copies of the skill are identical.
#  2. Every textbook file named in course/lectures.md exists in textbook/, apart from chapters
#     the index says are not public yet.
set -euo pipefail
cd "$(dirname "$0")/.."
status=0
if ! cmp -s .agents/skills/study/SKILL.md .claude/skills/study/SKILL.md; then
  echo "FAIL: .agents/skills/study/SKILL.md and .claude/skills/study/SKILL.md differ" >&2
  status=1
fi
# A chapter that is not public yet is allowed only where the index says "will then be in <file>".
while read -r f; do
  if [ ! -f "$f" ] && ! grep -q "will then be in \`$f\`" course/lectures.md; then
    echo "FAIL: course/lectures.md names $f, which is not in textbook/" >&2
    status=1
  fi
done < <(grep -o 'textbook/[A-Za-z0-9_]*\.md' course/lectures.md | sort -u)
[ "$status" -eq 0 ] && echo "ok: skill copies identical; index files present"
exit "$status"
