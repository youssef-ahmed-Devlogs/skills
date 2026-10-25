# Workspace format

The shape of each file in the workspace, apart from the lessons, which have [LESSON-FORMAT.md](./LESSON-FORMAT.md). Keep every file short: it is read at the start of each session.

## `GOAL.md`

```md
# {Topic}

Goal: {What the user wants to do with the topic, in one or two sentences.}

Done when the user can:
- {A task anyone could watch them do.}

Version: {tool} {version}, from {lock file | the user}. Or "none" when the topic has no versions.

Time and limits: {How much time they have, what they know now, how they like to learn.}

Not for now: {Close topics they do not want yet.}
```

- One goal per workspace. A second topic with no link to it gets its own folder.
- The goal is a task, not a wish: "write the tests of my own app", not "know testing".
- Change it only after the user agrees, and add a line on why to `KNOWN.md`.

## `SOURCES.md`

```md
# Sources

- [{Title}]({link}), {author}. Version: {version, or "any"}. {What it covers, and which lessons used it.}

## Places to ask people

- [{Name}]({link}). {What to ask there.}

## Still looking for

- {A part of the goal with no good source yet.}
```

- Official docs and primary sources come first, then known experts. No sales pages.
- Each line says what the source is good for.
- A docs source says its version, the one in `GOAL.md`: the docs of another version can say something else. When the user moves to a new version, replace those sources.
- Remove a source that turned out wrong, and fix every lesson point and sheet line that cited it.
- When the user does not want places to ask people, say so here.

## `KNOWN.md`

```md
# What the user knows

## Before we started

- {What they said or showed they knew, and how well.} ({date})

## Shown since

- {An idea, in one line.} Shown: lesson 03, {date}. Recalled: {date}, {date}.

## Wrong ideas dropped

- {The wrong idea, and the right one.} Lesson 02, {date}.

## Goal changes

- {date}: {What changed, and why.}
```

- An idea goes under "Shown since" only after the user used it right, not after a lesson covered it.
- Each warm-up that recalls it adds a date. With no later date it is still fresh, not known.
- When a recall fails, write `Missed: {date}` after it, and bring it back in the next warm-up.
- Wrong ideas matter most: they show where the next lessons may trip.

## `TERMS.md`

```md
# Terms

- **{The word in the user's language}** ({the original word}): {What it is, in one or two sentences.} Not: {other names that mean the same, which the lessons do not use}.
```

- Add a word only once the user uses it right.
- One name per idea, the same in every lesson.
- When a later lesson shows a definition is wrong or too narrow, fix it in place.

## `sheets/<name>.md`

- One sheet per subject, such as one process, one set of commands or one table.
- It stands alone: no links into `lessons/`, a source link for each claim, and the best source of its lesson at the end.
- Short enough to read in a minute.

## `NOTES.md`

A plain list: how the user likes to be taught, questions to come back to, and anything the next session should know.
