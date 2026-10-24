# Lesson format

A lesson is one Markdown file in `lessons/`, named `01-<dash-case-name>.md`, in the order of the path in `PROJECT.md`. The file is the plan you teach from in the chat, and the record of how far the user got. The user does not read it.

## Template

```md
---
status: in progress
started: 2026-10-24
finished:
checked at: a1b2c3d
code:
  - src/orders/
  - src/payments/refund.js
---

# {What the user will be able to do after this lesson}

For what the user needs: {one line, from PROJECT.md}

## Part 1: {one idea}

Status: done

Try first: {A question for the user to try before the explanation.}
Answer: {Its answer, with its key points.}

For users: {What this does for the people who use the project, in words a client would understand.}

In the code:
- {A point, short.} `{file}:{line}`
- {Another point.} `{file}`

Example: {One real flow traced through the code, such as what happens from a click to the saved row, with its files.}

Checks:
1. {A question that makes the user recall or use the idea.}
   Answer: {Its key points, and the wrong idea a wrong answer would show.}
2. {A question on a new case, such as what to tell a client.}
   Answer: {…}
3. {…}
4. {…}

## Part 2: {one idea}

Status: not started

…

## Final check

1. {A question that joins two parts.}
   Answer: {…}

## Waiting changes

- {date}, {pull request or commit}: {what it does for users}. Goes in part {n}.

## Log

- 2026-10-24, part 1, check 1: right.
- 2026-10-24, part 1, check 2: half, missed {key point}. Explained again with {new example}.
- 2026-10-27, change {pull request}: part 2 updated to the new code, checks 1 and 3 rewritten. Check on the change: right.
```

## Rules

- `status` at the top is `not started`, `in progress` or `done`. A part's `Status` is `not started`, `in progress` or `done`. Change them the moment they change: they are how the next session knows where to start.
- Fill `finished` when the final check passes.
- `code` lists the folders and files this lesson covers, and every file its points name. The catch-up uses it to find the lesson of each change, so a file a point names but `code` misses lets a change slip by. Add a path when the area grows.
- `checked at` is the commit the points and answers were checked against. Change it when a change updates them.
- One idea per part. When a part needs more than about five points, split it.
- Every point in the code names its file. A point with no file behind it stays out.
- Each answer lists its key points before you teach. Missing one of them makes a half answer.
- A change in this lesson's code updates its points and answers at once, and its log says what changed. Never keep an answer the code no longer backs.
- When a piece is taught early, for a part the user needed today, mark its part `done` and log why, so it is never taught again.
- Log each check asked, and its result, under `## Log`, so no session asks it again.
