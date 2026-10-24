# add-rule-or-skill

You have an idea for your agents, such as "always do X" or "a command that does Y". This skill finds out whether it already exists, and if not, what it should be and where it goes. It writes nothing until you agree.

**Start it:** `/add-rule-or-skill <your idea>`. It starts only when you type it.

## What it does

1. It says your idea back in one or two sentences, and asks one question when the answer changes the place, such as "every time, or only for some files?".
2. It searches the project, your own setup and your shared repositories, so you do not add a second copy of something.
3. It reads the official docs again, that day, since tools change. Earlier answers may be out of date.
4. It gives one verdict: it already exists, it exists with something missing, it clashes with something, or it is new, with what kind it should be and where.
5. Once you agree, it writes it and opens a pull request.

The kinds it picks from: a line in `AGENTS.md` or `CLAUDE.md`, a rule for some files, a skill, a hook or a CI check, a test, an output style, a subagent, a template, or an ADR.

## When to use it

| Your situation | Use |
| --- | --- |
| You have an idea for your agents, and do not know where it goes | `add-rule-or-skill` |
| You want to know what an existing skill does | [`explain-skill`](./explain-skill.md) |
| You want to think a bigger plan through first | [`interview-me`](./interview-me.md) |

## Example

```text
You:    /add-rule-or-skill the agent must run the formatter before every commit

Agent:  So: before each commit, the formatter runs on the changed files, in every session.
        One question: must it happen every time without fail, or is it advice?

You:    Every time.

Agent:  I searched AGENTS.md, .claude/rules, your skills and ~/.claude. CLAUDE.md says
        "format before you commit", but nothing makes it happen.

        Verdict: it exists, but as advice only. An instruction is a request, not a
        guarantee. What you want is a hook: a PreToolUse hook in .claude/settings.json
        that runs the formatter before `git commit`. Keep the line in CLAUDE.md, so the
        agent knows why. Sources, read today: the Claude Code hooks docs.

        Shall I write the hook here, for this project only?
```

## More use cases

- **A rule of code:** "controllers stay thin". It may find the rule exists, and offer a check too, such as a test or a search, so old code that breaks it is found.
- **A personal habit:** "answer me in Arabic". That goes to your own setup, not to the team's project.
- **A new skill:** a procedure you repeat, such as preparing a release. It writes the skill in your skills repository, with its line in the README.
- **A clash:** your idea fights an existing rule. It names both, and asks which one wins.

## What you get

A verdict with links to what it read, and, once you agree, the file in the right place with a pull request.

## What it needs

Matt Pocock's [`writing-for-agents`](https://github.com/mattpocock/skills), which it follows when it writes a skill or a rule. When it is missing, the skill stops and gives you the command that installs it.
