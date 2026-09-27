# AM115/AM215 study skill

A skill for your coding agent (Claude Code or Codex) that helps you study the course material
with the course textbook. It asks you questions **before** it explains anything, finds where
your understanding of a topic stops, keeps your own map of the concepts in `my/map.md`, and ends
each session with a study plan made of textbook sections and exercises.

The quizzes and written evaluations are taken without AI. So the skill is set up to give you
practice at answering on your own and to show you where you get stuck. An explanation you read
before trying seems clear, and you learn much less from it than from trying first.

## Getting it

**With git:**

```bash
git clone https://github.com/Harvard-AM215/study.git am115-study
```

**Without git:** on this repository's page, click **Code**, then **Download ZIP**, and unzip it.
Rename the folder to `am115-study` if you like.

To get updates later, run `git pull` in the folder, or download the ZIP again and copy your
`my/` folder into the new copy.

## Using it

Open the `am115-study` folder in your agent and start a new session:

- **Claude Code** (desktop app or terminal): type `/study`.
- **Codex**: run `codex` in the folder, then type `$study` (or "Use the study skill").

The skill asks four things: AM115 or AM215, two sentences about your background, how long you
have, and what you want to study (a lecture, a topic, or what the next quiz covers, which the
weekly Ed post says). A first session of 35 minutes is a good length.

Then answer each question on your own before you look anything up. A wrong answer is useful: it
shows you what to study. If the agent starts explaining before you have answered, tell it to
stop and ask the question again.

Codex needs permission to write files to save your map. If it says the folder is read-only,
start it with `codex -s workspace-write`.

## What it uses, and what it will not do

- It uses only the **course textbook**, which is public. A copy of the published chapters is in
  `textbook/`, and `course/lectures.md` says which sections go with which lecture.
- It will **not** tell you what is or is not on a quiz. The syllabus says quizzes "may draw on
  anything covered in lectures, readings, weekly exercises, and past P-Sets", and
  `course/lectures.md` is an index to the textbook, not a list of what can be asked.
- **Do not give it files from Canvas** (slides, quizzes, P-Set solutions). Course policy is that
  non-public course material is not given to AI tools.
- When the textbook does not settle whether your answer is right, it records the concept as
  "not assessed" instead of marking you wrong. The textbook is the authority on the
  mathematics; if the agent disagrees with it, go with the textbook.

## Your map and your data

`my/map.md` is yours: a small graph of the concepts you have studied, marked **secure**,
**partial**, **not yet** or **not assessed**, and your current study plan. It grows each time you
study. The `my/` folder is ignored by git, so it never ends up in a commit or a pull request. The
course does not collect your map or your conversations. (Your conversations do go to the AI
provider you use, as with any use of your agent.)

## Helping to improve it

This skill is new, and your experience is how we improve it, along with the textbook.

- At the end of a session the skill gives you a short "Feedback for the course" block. The
  weekly form on Ed may ask for it.
- You can [open an issue](https://github.com/Harvard-AM215/study/issues) describing what worked
  or what did not.
- You can propose a change with a pull request. See [CONTRIBUTING.md](CONTRIBUTING.md).
  Contributing is optional and is not graded. Issues and pull requests on this repository are
  public and show your GitHub account.

## License and credits

The skill and scripts are under the MIT License (see `LICENSE`). The textbook chapters in
`textbook/` are the course textbook's, copied here so the agent can read them.

The approach of finding the edge of what you know with graded questions, keeping a small
dependency map of the concepts, and motivating each step before stating it was inspired by Amos
Blomqvist's [learn](https://github.com/amosblomqvist/learn). No text or code from that
repository is used here.
