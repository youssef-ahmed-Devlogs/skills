# Workspace format

The shape of each file in the workspace, apart from the lessons, which have [LESSON-FORMAT.md](./LESSON-FORMAT.md). Keep every file short: it is read at the start of each session.

## `PROJECT.md`

```md
# {Project name}

Folder: {absolute path of the project}
Main branch: {the branch the team merges into, such as main}
Last commit read: {short hash}, {date}

Needs: {What the user needs from the project, in one or two sentences, such as "steer the agents on the payment work and answer the client's questions on it".}

## Path

1. What the project does, and for whom. Status: done. File: lessons/01-what-it-does.md
2. Its big parts, and how they connect. Status: in progress. File: lessons/02-big-parts.md
3. {Area}. Status: not started. File: lessons/03-{name}.md

Now: lesson {n}, part {n}.

Paused: lesson {n}, part {n}, at {the question or point}, to learn {idea}. File: gaps/{name}.md
```

- Write the `Paused` line only while a gap is open, and remove it when you come back to the part.

- The path goes from the top down: what the project does, its big parts, then one lesson per area, the ones users touch most first.
- Add a lesson when a new area appears, at its place. Never reorder the path to follow the day's work.
- Change "Needs" only after the user agrees, and write why in `NOTES.md`.

## `CHANGES.md`

```md
# Changes

## {date}: {short hash} to {short hash}

- **{Short title}** ({pull request or commit}). For users: {what it does for the people who use the project, in one or two lines}. Lesson: 05. Explained: yes | waiting | next session.

Dropped: {how many small fixes, style changes, package updates and test changes, in one line}.
```

- Newest first.
- `waiting` is a change in a part not reached yet: its part teaches it. `next session` is a change in a part the user finished or started that did not fit this session's three.
- The "For users" line is what the user can tell a client, with no code.

## `MAP.md`

```md
# {Project name}

What it does: {one or two lines, for whom and why}.

## Parts

- **{Part}**: {what it does for the people who use the project, in one line}. Code: `{folder}`. Learned: yes | not yet.

## New since {date}

- {Change, in one plain line.}

Read at commit {short hash}, {date}.
```

- The only file the user reads, such as before a meeting. Write it in words a client would understand, with code paths only after them.
- Write it in the first session, with one line for each area. Update it when a lesson is done, and after each catch-up.
- A part not learned yet still gets its one line, so the map has no holes.
- Keep it short enough to read in two minutes.

## `KNOWN.md`

```md
# What the user knows

## Before we started

- {What they said or showed they knew, and how well.} ({date})

## Shown since

- {A point, in one line.} Shown: lesson 03, {date}, at {short hash}. Recalled: {date}, {date}.
- {A point.} Shown: lesson 02, {date}. Changed: {date}, {what changed}. Recall it again.

## Wrong ideas dropped

- {The wrong idea, and the right one.} Lesson 02, {date}.
```

- A point goes under "Shown since" only after the user used it right, not after a lesson covered it.
- Each warm-up that recalls it adds a date. With no later date it is still fresh, not known.
- When the code behind a point changes, add `Changed`. The point is not known again until a warm-up recalls the new version.
- When a recall fails, write `Missed: {date}`, and bring it back in the next warm-up.

## `gaps/<name>.md`

```md
# {Idea, such as caching or Redis}

Needed by: lesson {n}, part {n}. Taught: {date}.

## {Piece}

- {A point, short.} [{source}]({link})

Example: {One example, from the project's code when it fits.} `{file}`

Checks:
- Q: {question}. Answer: right | half | wrong | don't know.
```

- One file per idea. A later piece of the same idea goes in the same file.
- A source link for each point. The user reads this file again later.

## `NOTES.md`

A plain list: how the user likes to be taught, questions to come back to, docs that disagree with the code, ideas to learn later with the part that needed each, and anything the next session should know.
