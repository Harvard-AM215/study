# AM115/AM215 study skill

## Quick start

1. **Get the folder.** In a terminal: `git clone https://github.com/Harvard-AM215/study.git am115-study`
   (or click **Code → Download ZIP** above, unzip, and rename `study-main` to `am115-study`).
2. **Download the textbook into it:** `cd am115-study`, then `python3 scripts/get_textbook.py`
   (Windows: `py -3 scripts/get_textbook.py`).
3. **Open the folder in your agent.** Claude Code desktop app: in the Code tab, choose
   `am115-study`. Claude Code in a terminal: run `claude` in the folder. Codex: run
   `codex -s workspace-write` in the folder.
4. **Type `/study`** (Claude Code) or **`$study`** (Codex), pick a chapter, and write down its main
   ideas from memory when asked. The agent takes you through the rest in about an hour.

Details and troubleshooting are below.

## What this is

This course asks you to understand its models: what a chapter's main ideas are, how each one
follows from another, and why each step holds. A reliable way to find out how much of that you
have is to lay out a chapter's main ideas from memory, before you look, and then check what you
wrote against the textbook. What you left out, and the links you got wrong, show you what to
work on.

This folder is a **study skill** for your coding agent (Claude Code or Codex) that runs that
process with you, using the course textbook. In one session of about an hour you:

1. choose a chapter;
2. write down its main ideas and how they connect, from memory;
3. check that against the chapter's headings and its "Connections" section, with the agent;
4. repair one missing or wrong link in your own words, and answer one question on it;
5. keep the result as your map, in `my/map.md`.

The agent asks before it explains, and it does not correct your map until you have checked it
yourself. The research behind each of these choices is in [WHY.md](WHY.md).

## What you need

Claude Code (the desktop app or the terminal) or Codex, set up as in
[Section 1](https://harvard-am215.github.io/textbook/sec01-agent-setup/). You also need Python 3:
if `python3 --version` (Windows: `py -3 --version`) prints a version number, you have it;
otherwise install it from [python.org](https://www.python.org/downloads/).

## Set it up (5 minutes)

1. **Get the folder.**
   - With git: `git clone https://github.com/Harvard-AM215/study.git am115-study`
   - Without git: on this page, click **Code**, then **Download ZIP**, and unzip it. The folder
     it makes is called `study-main`; rename it to `am115-study`.
2. **Download the textbook into it.** In a terminal, in the folder:

   ```bash
   python3 scripts/get_textbook.py
   ```

   On Windows, type `py -3 scripts/get_textbook.py` instead. It prints "Textbook up to date in
   textbook/: … pages". The first time takes a minute or two. The skill runs this again at the
   start of every session when it can, and then downloads only what changed, such as a newly
   published chapter.
3. **Open the folder itself** in your agent, not the folder above it. The skill is found only
   when the agent starts inside this folder (`am115-study`, or whatever you named it).
   - **Claude Code desktop app:** in the Code tab, choose the `am115-study` folder.
   - **Claude Code in a terminal:** `cd am115-study`, then `claude`.
   - **Codex:** `cd am115-study`, then `codex -s workspace-write`. (Without
     `-s workspace-write`, Codex cannot save your map.)
4. **Start the skill.** In Claude Code, type `/study`. In Codex, type `$study` (or "Use the study
   skill"). Claude Code asks permission to run the download script; allow it. Codex usually
   cannot reach the internet, which is why you ran step 2 yourself.

## A session, step by step

The skill asks which course you are in, how long you have, and which chapter you want to
understand better. Then:

1. **From memory.** It asks you for the chapter's 3 to 5 main ideas and how they connect, without
   opening the chapter or your notes. Write what you can; "I only remember two" is a useful
   answer. It will not correct you yet.
2. **Check.** You open the chapter together and compare your map with its headings and its
   "Connections" section. It asks you first what is missing or wrong, then says what it sees,
   citing the section.
3. **Repair.** You restate one corrected link in your own words, and answer one question about it
   from the chapter's exercises or worked examples. If your map had nothing missing or wrong, you
   test one of its links the same way. If you miss, you get one hint and a second
   try before any explanation.
4. **Your map.** It updates `my/map.md`, draws each chapter's graph as a picture next to it
   (`my/map-chapter-6.svg` for Chapter 6, which opens in any web browser), and gives you a short
   "For the course" block with what changed, which the weekly Ed form may ask for.

If you have more time, ask it for more practice on the same chapter. Next session, it reads your
map and offers to continue.

## If something goes wrong

- **`/study` or `$study` does nothing, or the agent does not know the skill.** You opened the
  wrong folder. Close the session and open `am115-study` itself (set-up step 3).
- **Codex says the folder is read-only, or it cannot save the map.** Start it with
  `codex -s workspace-write`.
- **The download fails.** Check your internet connection and run
  `python3 scripts/get_textbook.py` again. If you already have a copy, the skill uses it and tells
  you its date.
- **A chapter is missing.** It may not be public yet. Run the download again after it is
  announced.
- **Your map shows a block of code starting with `graph TD` instead of a diagram.** Your
  Markdown viewer does not draw mermaid graphs; many do not. Open the picture of that chapter's
  graph, `my/map-chapter-6.svg` for Chapter 6, in a web browser. If it is not there, run
  `python3 scripts/render_map.py` (Windows: `py -3 scripts/render_map.py`) to draw it.
- **The agent explains before you have answered.** Tell it to stop and ask the question again.
- **You think the agent is wrong.** Check the section it names. The textbook is the authority on
  the mathematics; go with the textbook, and note it on the Ed form.

Windows and the Download ZIP route have not been tested yet. If something fails there, please
[open an issue](https://github.com/Harvard-AM215/study/issues) saying what you typed and what
happened.

## Updating

With git: `git pull` in the folder, then `python3 scripts/get_textbook.py`. With the ZIP: download
it again and copy your `my/` folder into the new copy, then run the script.

## What it uses, and what it will not do

- It uses only the **course textbook**, which is public. `scripts/get_textbook.py` downloads the
  published chapters from https://harvard-am215.github.io/textbook/ into `textbook/`, and
  `course/lectures.md` says which sections go with which lecture.
- It will **not** tell you what is or is not on a quiz. The syllabus says quizzes "may draw on
  anything covered in lectures, readings, weekly exercises, and past P-Sets".
- **Do not give it files from Canvas** (slides, quizzes, P-Set solutions). Course policy is that
  non-public course material is not given to AI tools.
- When the textbook does not settle whether your answer is right, it says so instead of marking
  you wrong.

## Your map and your data

`my/map.md` is yours: each chapter you have mapped, with every idea marked **recalled**,
**added** or **repaired**, and a plan if you asked for more practice. Next to it,
`my/map-chapter-6.svg` and the like are pictures of each chapter's graph, drawn by
`scripts/render_map.py`; if you edit a graph yourself, run that script to redraw them. The `my/`
and `textbook/` folders are ignored by git, so they never end up in a commit or a pull request.
The course does not collect your map or your conversations. (Your conversations do go to the AI
provider you use, as with any use of your agent.)

## Helping to improve it

This skill is new, and your experience is how we improve it, along with the textbook.

- The weekly form on Ed asks how a session went.
- You can [open an issue](https://github.com/Harvard-AM215/study/issues) describing what worked
  or what did not.
- You can propose a change with a pull request. See [CONTRIBUTING.md](CONTRIBUTING.md).
  Contributing is optional and is not graded. Issues and pull requests on this repository are
  public and show your GitHub account.

## License and credits

The skill and scripts are under the MIT License (see `LICENSE`). The textbook is downloaded from
its public site and is not part of this repository.

The approach of finding the edge of what you know with questions of increasing difficulty, keeping a small
dependency map of the concepts, and motivating each step before stating it was inspired by Amos
Blomqvist's [learn](https://github.com/amosblomqvist/learn). No text or code from that
repository is used here.
