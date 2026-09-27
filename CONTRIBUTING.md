# Contributing

Suggestions from people who use the skill are the main way it gets better. Contributing is
optional and is not graded. Everything on this repository, including issues and pull requests,
is public and shows your GitHub account.

## Reporting what worked and what did not

Open an issue. The most useful reports say what you were studying (lecture or chapter and
section), what the agent did, and what you expected instead. **Do not paste whole
conversations**, and do not include anything personal, your grades, or any file from Canvas.

## Proposing a change

1. Fork the repository and make a branch.
2. Edit the skill in `.agents/skills/study/SKILL.md`, then copy the file to
   `.claude/skills/study/SKILL.md` so that the two copies are identical (Codex reads the first,
   Claude Code the second). `scripts/check.sh` checks this, and so does the check that runs on
   every pull request.
3. Try the change in a real study session before you open the pull request, and say in the pull
   request what you tried and what changed.
4. Open the pull request. A member of the course staff reviews it.

**What belongs here:** changes to how the skill runs a study session (the questions it asks,
how it gives hints, how it keeps the map, how it plans), and corrections to the lecture index in
`course/lectures.md`.

**What does not:** changes to `textbook/`, which is a copy of the course textbook. Report
problems in the textbook through the weekly form on Ed or an issue instead, and the staff will
fix the textbook itself.
