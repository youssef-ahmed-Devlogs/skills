# tutor-me

The agent teaches you a topic over many sessions, in the chat. It builds each lesson from trusted sources, then teaches it one part at a time, and moves on only when you show you understood.

**Start it:** `/tutor-me <topic>`, in an empty folder for that topic. It starts only when you type it.

## Before you start

**Install it:**

```bash
npx skills add youssef-ahmed-Devlogs/skills --skill tutor-me
```

It asks which agents to install it for: pick every agent you use. Other ways, and updates: [Installing](../install.md).

**It needs:** Nothing.

**Where to run it:** A new, empty folder for the topic, outside any project. Make it yourself, such as `learn/docker` in your home folder, and open your agent in it. The skill does not make the folder: it writes its files in the folder you run it in. Come back to the same folder for every session of that topic.

**Call it:** in Claude Code or GitHub Copilot, type `/tutor-me Docker`. In Codex, type `$tutor-me Docker`.

**Agents:** Claude Code, Codex and GitHub Copilot, or any agent that reads skills. Its files are plain Markdown, so you can start with one agent and go on with another.

## What it does

1. It asks what you want to do with the topic, and three short questions that show what you know already. For a tool, a language or a framework, it finds the version you work with.
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

Agent:  What do you want to be able to do with Docker?

You:    Run my Node app and its database on any machine with one command.

Agent:  Good. Three short questions to see where you start. First one:
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
