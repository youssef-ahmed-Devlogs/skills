# Workspace format

The shape of each file in the workspace. Keep every file short: it is read at the start of each session.

## `PATH.md`

```md
# {Path name}

Goal: {What the user wants to be able to do at the end, in one or two sentences.}

Courses:
1. [{Course title}]({link}), {teacher or author}. Made: {year}. Versions: {tool} {version}. Status: done | in progress | not started. File: courses/01-{name}.md

Now: course {n}, step {step number and title}.

Project: {absolute path of the practice project, or "none"}. Versions: {tool} {version}, from {lock file}. Last commit read: {short hash}, {date}.
```

- The user picks the courses and their order. Never add one.
- Change the goal only after the user agrees, and write why in `NOTES.md`.

## `SOURCES.md`

```md
# Sources

Versions: {tool} {version}, {tool} {version}, as in PATH.md.

## {Topic, such as auth}

- [{Title}]({link}), {author or project}. Version: {version, or "any"}. Good for: {what it covers, and when to reach for it}. Used: steps {n}, {n}.

## Still looking for

- {A topic of the course with no good source yet.}
```

- Official docs come first, for the versions in `PATH.md`. Then the main community and security references, such as OWASP, and known experts. No sales pages.
- One heading per topic of the course. A new topic gets its heading when a step brings it.
- A docs source says its version: the docs of another version can say something else.
- When a version in the project changes, replace the docs sources of that tool with the docs of the new version.
- Remove a source that turned out wrong, and check again what rests on it, as SKILL.md says.

## `courses/01-<name>.md`

```md
# {Course title}

## Contents

- [~] 1.1 {Step title} (before we started)
- [x] 1.2 {Step title}
- [-] 1.3 {Step title} (skipped)
- [ ] 1.4 {Step title}

## Log

### 1.1 {Step title} ({date})

Covered, in the user's words: {their lines}.
Code: {files or commits of the project for this step, or "none"}.
Checked against: [{source}]({link}), [{source}]({link}).
- Q: {question}. Key points: {what a right answer holds}. Answer: right | half | wrong | don't know. {One line on what was missing.}

### Chapter 1 check ({date})

- Q: {question}. Answer: right | half | wrong | don't know.
```

- The contents follow the course's own split and numbers.
- `[x]` is done: ticked only after its checks pass. `[~]` was studied before the first session, and `[-]` was skipped on the user's ask: neither is checked one by one. Their main points live in the warm-ups and the chapter check.

## `FIX-LATER.md`

```md
# Fix later

## Open

- **{Short title}** ({Wrong preference | Old}). Course: step {n}. Project: `{file}`. The course does: {what}. Right: {what, and why}. Source: [{title}]({link}), version {v}.

## Fixed

- **{Short title}**. Fixed {date}, by the user | by the agent, on the user's ask. Commit {hash}, or "not committed yet".
```

- A danger now, and a step that breaks the course now, are fixed at once, and go straight under "Fixed".
- "Fixed by the user" is the normal case. Write "by the agent, on the user's ask" when you wrote it.

## `KNOWN.md`

```md
# What the user knows

## Before we started

- {What they said or showed they knew, and how well.} ({date})

## Shown since

- {An idea, in one line.} Shown: step {n}, {date}. Recalled: {date}, {date}.

## Wrong ideas dropped

- {The wrong idea, and the right one.} Step {n}, {date}.
```

- An idea goes under "Shown since" only after the user used it right.
- Each warm-up that recalls it adds a date. When a recall fails, write `Missed: {date}`, and bring it back in the next warm-up.

## `TERMS.md`

```md
# Terms

- **{The word in the user's language}** ({the original word}): {What it is, in one or two sentences.} The course calls it: {its name in the course, when it differs}.
```

- Add a word only once the user uses it right.
- When a later step shows a definition is wrong or too narrow, fix it in place.

## `gaps/<name>.md`

- One file per base, such as `gaps/sql.md`, read by the user later.
- It stands alone: the pieces taught, each with a short example and its source link, and the course step that needed it.
- A later piece of the same base is added to the same file.

## `NOTES.md`

A plain list: how the user likes to be helped, questions to come back to, and anything the next session should know.
