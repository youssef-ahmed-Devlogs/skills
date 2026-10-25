# tutor-me

The agent teaches you a topic over many sessions, in the chat. It builds each lesson from trusted sources, then teaches it one part at a time, and moves on only when you show you understood.

**Start it:** `/tutor-me <topic>`, in an empty folder for that topic. It starts only when you type it.

## Before you start

**Install it:**

```bash
npx skills add youssef-ahmed-Devlogs/skills --skill tutor-me --skill interview-me
```

It asks which agents to install it for: pick every agent you use. Other ways, and updates: [Installing](../install.md).

**It needs:** [`interview-me`](./interview-me.md) from this repository, which it runs to settle your goal in the first session. When `interview-me` is missing, the skill stops and gives you the command:

```bash
npx skills add youssef-ahmed-Devlogs/skills --skill interview-me
```

**Where to run it:** A new, empty folder for the topic, outside any project. Make it yourself, such as `learn/docker` in your home folder, and open your agent in it. The skill does not make the folder: it writes its files in the folder you run it in. Come back to the same folder for every session of that topic.

**Call it:** in Claude Code or GitHub Copilot, type `/tutor-me Docker`. In Codex, type `$tutor-me Docker`.

**Agents:** Claude Code, Codex and GitHub Copilot, or any agent that reads skills. Its files are plain Markdown, so you can start with one agent and go on with another.

## What it does

1. The first session starts with an interview on what you want to do with the topic: one question at a time, with its guess each time, until you say yes to its summary. Then three short questions show what you know already. For a tool, a language or a framework, it finds the version you work with.
2. It builds a small lesson from official docs and known experts for your version, kept in `SOURCES.md`, as a file for itself. You never need to read it. A question you ask on the side is answered from a source too, with its link.
3. It teaches the lesson in the chat, one part at a time. Each part starts by asking whether you know it already.
4. It asks questions that make you recall or use the idea, one per message, and moves on after two right answers in a row.
5. A final check mixes the parts. The next session starts with a short recall of older lessons.

Every answer gets a reply:

- **Right:** "Right, because …", in two or three lines.
- **Half right:** which piece is right, which is missing or wrong, and the right answer for it.
- **Wrong:** the right answer and why, with no hints, then "what did you understand?".
- **"I don't know":** the explanation first, then a question.

## When to use it

| Your situation | Use |
| --- | --- |
| You want to learn a topic, and have no course | `tutor-me` |
| You already follow a course, a book or a path | [`study-with-me`](./study-with-me.md) |
| You only need one quick answer | Ask directly |

## Example

```text
You:    /tutor-me Docker

Agent:  What I understand: you want to learn Docker for your own work.
        How sure: 30%. Missing: what you will use it for, and what done looks like.

        ❓ Do you want Docker to run an app you already have, more than to learn it in general?
        ➡️ My guess: yes, since most people start Docker for one app of theirs.

You:    Yes. Run my Node app and its database on any machine with one command.
```

A few questions later, it says your goal back in a short summary, and you say yes. It writes `GOAL.md` from it, then:

```text
Agent:  Three short questions to see where you start. First one:
        what is the difference between an image and a container, in your words?

You:    I don't know.
```

It writes your goal and what you showed, builds the first lesson, "Run one container", and starts:

```text
Agent:  Lesson 1: Run one container. After it, you can start a ready image and reach it
        from your browser.

        Before I explain: what do you think `docker run -p 8080:80 nginx` does?

You:    It downloads nginx and runs it on port 8080.

Agent:  Half right. It does download nginx and run it, if it is not there yet. The missing
        piece: nginx listens on port 80 inside the container, and `-p 8080:80` connects
        your port 8080 to it. Without `-p`, your browser cannot reach it at all.
```

Run `/tutor-me` again in the same folder the next day. It starts with two recall questions, then goes on where you stopped.

## More use cases

- **A language for a new job:** "/tutor-me TypeScript", with a goal such as "read and fix the code of my team".
- **A topic that is not code:** personal finance, a language you speak, the rules of a sport.
- **A topic you knew once:** the first questions find what is still there, and the lessons skip it.
- **A practical skill:** a part can end with a small task to do outside the chat, such as running a command, and the check asks what happened.

## What you get

All in the folder you ran it in:

- `GOAL.md`, `SOURCES.md`, and `lessons/` with one file per lesson.
- `KNOWN.md`, what you showed you know, and `TERMS.md`, the words of the topic.
- `sheets/`: short sheets you can read later, such as commands or steps.


## Tips

- One folder per topic. A second topic gets its own folder.
- Answer in your own words. A right answer just after an explanation shows the idea is fresh, not that it will last: the recalls of later sessions show that.
