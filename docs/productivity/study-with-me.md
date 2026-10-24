# study-with-me

The agent follows you through a course, a book or a path you study on your own, like a teacher sitting beside you. The course teaches. The agent knows where you are, reads the code you write beside it, checks that each step stuck, and fills every gap, so you never need another course to finish this one.

**Start it:** `/study-with-me <course>`, in an empty folder outside your practice project. It starts only when you type it.

## Before you start

**Install it:**

```bash
npx skills add youssef-ahmed-Devlogs/skills --skill study-with-me
```

It asks which agents to install it for: pick every agent you use. Other ways, and updates: [Installing](../install.md).

**It needs:** Nothing. For the code part, a git repository for your practice project, so it can see what changed since the last session.

**Where to run it:** A new, empty folder for the course, outside your practice project. Make it yourself, such as `learn/laravel-course` in your home folder, and open your agent in it. The skill does not make the folder. Run inside your practice project, it asks for a folder outside it first, since its notes would end up in your commits. It asks for your practice project's folder in the first session.

**Call it:** in Claude Code or GitHub Copilot, type `/study-with-me Laravel from scratch`. In Codex, type `$study-with-me Laravel from scratch`.

**Agents:** Claude Code, Codex and GitHub Copilot, or any agent that reads skills. Its files are plain Markdown, so you can start with one agent and go on with another.

## What it does

1. **Setup, once:** it finds the course's table of contents and the versions it uses, asks your goal, where your practice project is, and which step you reached.
2. **After each step:** you say in a line or two what the step covered. It reads the code you wrote for it, runs it when it can, and asks one or two questions on the main point.
3. **It judges the course:** when a step differs from the official way, it says what kind of choice it is, with a source and a version.
4. **It fills gaps:** when you miss something the course takes for granted, it teaches just that, then sends you back to the same step.
5. **At the end:** you fix the wrong and old steps in your project yourself, and it checks each fix.

Its five words for a choice of the course:

- **Official:** what the official docs say, for your version.
- **Community advice:** not in the docs, but what most people who do this for real advise.
- **Sound preference:** one of several right ways. Keep it if you like.
- **Wrong preference:** against the docs or the community, with a real cost, such as a security hole.
- **Old:** right when the course was made, changed by a newer version.

## When to use it

| Your situation | Use |
| --- | --- |
| You follow a video course, a book or a path, maybe with a project beside it | `study-with-me` |
| You have no course, and want the agent to build the lessons | [`tutor-me`](./tutor-me.md) |
| You want to plan what to learn, not learn it yet | [`interview-me`](./interview-me.md) |

## Example

You study a Node and Express course from 2021, and you build its project on today's Express 5:

```text
You:    /study-with-me the Node.js and Express course of freeCodeCamp. I build its project
        in ~/code/node-practice. I want to build a full REST API with a database.

Agent:  I found the course: 2021, 8 hours, on Express 4.17. Its table of contents ends at
        Express Router. It has no database at all.
        Shall we shrink the goal to what the course covers, or add a second course of your
        choice for the database?
```

Later, it reads your project and finds a step that no longer works on your version:

```text
Agent:  🏷️ Old: line 59 of app.js is `app.all('*', ...)`, as in the course. On Express 5 the
        server crashes at start: "Missing parameter name at index 1: *". I ran it to check.
        Express 5 needs a named wildcard: `app.all('/{*splat}', ...)`. Source: the Express 5
        migration guide.
        This stops you from going on, so it is fixed now. Do you change it, or shall I?
```

When you finish a step, it checks it:

```text
You:    Done with 2.27, the POST form. The form sends its data, and we read it from req.body.

Agent:  Right, because the form sends `name=sara` as text, and the parser turns it into the
        object `{ name: 'sara' }` in `req.body`.
        A question: the input becomes `name="username"`. What does /login answer for sara?
```

When you miss the same base idea twice, such as what an object key is, it says the gap is bigger than this step, teaches only what the step needs in two or three small parts, saves it in `gaps/js-objects.md`, and brings you back to the same question.

## More use cases

- **A book, chapter by chapter:** it checks each chapter, and its exercises when you share them.
- **A path of several courses:** they go in one map, in your order. A single course is a path of one.
- **Starting in the middle:** the steps before your start are marked "before we started", and three short questions find what you know.
- **No project at all:** a course of design, writing or anything else works too. It checks what you understood, not code.
- **In a hurry:** skip the checks of a step. Its main point comes back later, in the recall at the start of a session, and the chapter check covers it too.

## What you get

All in the folder you ran it in:

- `PATH.md`: your goal, the courses, where you are, and your project's folder.
- `courses/`: one file per course, with its table of contents and what you showed at each step.
- `FIX-LATER.md`: the wrong and old steps, each with its source, to fix at the end.
- `gaps/`: what it taught to fill a big gap, for you to read again.
- `KNOWN.md` and `TERMS.md`: what you showed you know, and the words of the topic.

It never writes in your project, unless you say yes to one change.


## Tips

- Commit after each step. The commits tell it what you wrote, and where you are.
- When a video is hard, paste its transcript or the part you did not get. It cannot watch videos.
