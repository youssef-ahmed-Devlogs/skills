# catch-me-up

The agent teaches you a code project you did not write, or no longer know, in the chat, from the code itself. Each session starts with what changed since the last one, so you keep up while the project moves every day.

**Start it:** `/catch-me-up <what you need from the project>`, inside the project's folder. It starts only when you type it.

## What it does

1. It asks what you need from the project, such as steering the agents that write its code or answering a client, and three short questions that show what you know.
2. It reads the project itself, and builds a path from the top down: what the project does, its big parts, then one lesson per area. It also writes a short map you can read from the first day.
3. It teaches each lesson in the chat, one part at a time, from two sides: what it does for the people who use the project, and how the code does it, with the files.
4. It asks questions that make you recall or use what you learned, one per message, such as what to tell a client, or where a change belongs.
5. Each next session starts with a short catch-up on the new commits. A change in a part you learned is explained, and its checks are updated. A change in a part you have not reached gets one or two plain lines, and waits for that part.
6. When you need a part today that the path has not reached, it teaches the older pieces it rests on first, then that part.
7. When a part rests on an idea from outside the project that you do not have, such as object-oriented code, caching, queues, Redis or a package, it offers in one line to pause and learn it first. On a yes, it saves where you stopped, teaches the idea, then brings you back. On a no, it explains only what the part needs, and keeps the idea for later.

Every answer gets a reply: "Right, because …", which piece is right and which is missing, or the right answer and why, with no hints, then "what did you understand?".

## When to use it

| Your situation | Use |
| --- | --- |
| A code project that is new to you, or that agents wrote while you were away | `catch-me-up` |
| A topic to learn, not one project | [`tutor-me`](./tutor-me.md) |
| A course or a book you follow on your own | [`study-with-me`](./study-with-me.md) |
| A plan to think through in a project before the work starts | [`interview-with-docs`](./interview-with-docs.md) |

## Example

An online shop. Agents wrote most of its code in the last months, and you need to answer the client's questions on it.

```text
You:    /catch-me-up I need to answer the client's questions and steer the agents

Agent:  Three short questions first, to see where you start. First one:
        what does this shop sell, and to whom, in your words?

You:    Clothes, to people in one country. I think there is a wholesale part now.
```

It reads the code, and builds the path: what the shop does, its big parts, then orders, payments, wholesale and the rest.

```text
Agent:  Lesson 3: How an order is paid. After it, you can tell the client what happens
        when a payment fails, and see when an agent puts payment code in the wrong place.

        Before I explain: when the card is refused, what do you think happens to the order?

You:    It is deleted.

Agent:  Wrong. The order stays, with the status "waiting for payment", and the customer
        can pay again for 24 hours (src/payments/confirm.js:41). After that a scheduled
        job cancels it (src/jobs/cancel-unpaid.js). Nothing is deleted, so the client can
        still see every refused payment. What did you understand, in your words?
```

Run it again the next day. It reads the new commits first:

```text
Agent:  Since yesterday: 14 commits, 3 changes worth knowing, 9 small fixes dropped.

        In a lesson you learned: unpaid orders now wait 48 hours, not 24
        (src/jobs/cancel-unpaid.js). A client asks why a customer still has an unpaid
        order after two days. What do you answer?
```

## More use cases

- **A new job:** your first weeks on a big project, with a map of it you can read before each meeting.
- **A project you built long ago:** the first questions find what you still know, and the lessons skip it.
- **A feature you discuss today:** it teaches the older parts the feature rests on, then the feature, and counts them in your path.
- **A day with time to dig:** you reach code built on something you never learned, such as a cache or a queue, say yes to the pause, learn it, and go back to the same question.
- **A busy project:** at most three changes are explained in depth per session, and the rest wait, so the path still moves.

## What you get

All in `~/.catch-me-up/<project>/`, never inside the project:

- `MAP.md`: a short map of the project in plain words, for you to read.
- `PROJECT.md`, the path and where you are, and `lessons/` with one file per lesson.
- `CHANGES.md`: each change since you started, in one or two plain lines.
- `KNOWN.md`: what you showed you know, and what changed under it.
- `gaps/`: the ideas you paused to learn, to read again later.

The project itself is only read: no files, no commits, no branch changes.

## What it needs

Git, in the project's folder. Without it, it can teach, but not catch up.

## Tips

- Run it in the same project folder each time, so it finds its workspace.
- Read `MAP.md` before a meeting: it says what each part does in words a client understands.
- Answer in your own words. A point counts as known only after a later session recalls it.
