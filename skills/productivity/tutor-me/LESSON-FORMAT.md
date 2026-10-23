# Lesson format

A lesson is one Markdown file in `lessons/`, named `01-<dash-case-name>.md`. Take the highest number there and add one. The file is the plan you teach from in the chat, and the record of how far the user got. The user does not read it.

## Template

```md
---
status: in progress
started: 2026-10-23
finished:
---

# {What the user will be able to do after this lesson}

For the goal: {one line}
Best source: [{title}]({link})

## Part 1: {one idea}

Status: done

Try first: {A question for the user to try before the explanation.}
Answer: {Its answer, with its key points.}

Explain:
- {A point, short.} [{source}]({link})
- {Another point.}

Example: {One concrete example, tied to the goal when possible.}

Checks:
1. {A question that makes the user recall or use the idea.}
   Answer: {Its key points, and the wrong idea a wrong answer would show.}
2. {A question on a new case.}
   Answer: {…}
3. {…}
4. {…}

## Part 2: {one idea}

Status: in progress

…

## Final check

1. {A question that joins two parts.}
   Answer: {…}

## Log

- 2026-10-23, part 1, check 1: right.
- 2026-10-23, part 1, check 2: half, missed {key point}. Explained again with {new example}.
- {What was hard, which explanation worked, what the user asked.}
```

## Rules

- `status` at the top is `not started`, `in progress` or `done`. A part's `Status` is `not started`, `in progress` or `done`. Change them the moment they change: they are how the next session knows where to start.
- Fill `finished` when the final check passes.
- One idea per part. When a part needs more than about five points, split it.
- Every claim links its source. A point with no trusted source stays out.
- Each answer lists its key points before you teach. Missing one of them makes a half answer.
- Write the checks to need recall or use, never a yes. Give choices only when the topic needs them.
- Log each check asked, and its result, under `## Log`, so no session asks it again. `KNOWN.md` takes from there what matters later.
