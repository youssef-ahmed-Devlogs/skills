---
name: add-rule-or-skill
description: Talk through something new the user wants an agent to know or do, such as a rule, a skill or a check, and decide what it should be and where it goes, or show that it already exists. Use when the user wants to add a rule, skill, hook, template or any instruction and does not know its place.
disable-model-invocation: true
---

# Add a rule or a skill

## Before you start

This skill needs these skills: `writing-for-agents`. Check that each one is installed: a folder of that name in the project's `.agents/skills`, `.claude/skills` or `.github/skills`, or in `~/.agents/skills`, `~/.claude/skills`, `~/.codex/skills` or `~/.copilot/skills`. When one is missing, stop before anything else. Tell the user which one is missing and what this skill needs it for, and give the command that installs it:

```bash
npx skills add mattpocock/skills --skill writing-for-agents
```

Go on once the user has installed it, or says to go on without it.

The user describes something they want agents to know or do. Find out whether it already exists, and if not, what it should be and where it lives. Every recommendation rests on official docs and the practice of professional teams, with links. Nothing is written until the user agrees.

## 1. Understand what they want

Restate it in one or two sentences: the behaviour they want, when it should happen, and for which projects. Ask one question when the answer changes the place: does it hold every time, or only for some files or some tasks? Must it happen without fail, or is it advice?

## 2. Look for it everywhere

Search before you suggest anything new. Read each place below that exists, and note every part that already covers the idea, even in other words:

- **This project**: `AGENTS.md` and `CLAUDE.md` at every level, `.claude`, `.codex`, `.github/copilot-instructions.md`, `.github/instructions`, `.github/agents`, `.github/hooks`, `docs/agents`, `.github` templates and workflows, tests such as `arch()` tests, and git hooks. Note which agents the project uses: [PLACES.md](PLACES.md) says how to tell.
- **Its skills**: `.agents/skills`, `.claude/skills` and `.github/skills`, and their "Before you start" parts.
- **The user's own setup**: `~/.claude` (its `CLAUDE.md`, rules, skills and output styles), `~/.codex` (its `AGENTS.md` and config), `~/.copilot`, `~/.agents/skills`, and the memory files.
- **The user's shared repositories**: the repositories of skills or rules the user installs into every project, such as their own skills repository. Ask for them when you do not know them.

Done when every place was searched for the idea's key words and their synonyms.

## 3. Research it again, every time

Tools change, so earlier answers may be out of date. Do this research on every run, even for an idea that looks like one you saw before:

1. Fetch each page in the Sources of [PLACES.md](PLACES.md) again, today. Note what each one says now about the kind that may fit.
2. Search the official docs of anything else the idea touches: the agent, the tool, or the framework, such as the Laravel or Pest docs.
3. Search how professional teams do it now: well-known open source repositories, and the engineering blogs of the vendors. Prefer the primary source over a summary of it.
4. Compare with `PLACES.md`. When a source now says something different, the source wins: say what changed, and offer to fix `PLACES.md` in this skill's own repository.

Done when every source in `PLACES.md` was fetched today, and each claim you will make has a link you read today.

## 4. Give the verdict

Base it on today's research, not on memory. Start with one of these, in one line:

- **It already exists**: name the file or skill, quote the line, and show how to use it.
- **It exists, with something missing or extra**: name the file, and say what to add, change or cut.
- **It clashes with something**: name both, and the choice to make.
- **It is new**: say what kind it should be, where it goes, and why, with the source.

Then say where it lives, in a place that every agent the project uses reads, as [PLACES.md](PLACES.md) says, so the project can go on with another agent: **a shared repository** when every project, or every project of a stack, needs it; **this project** when only it does; **the user's own setup** when it is a personal preference for every project, not a rule for the team. A mechanical rule that can be checked gets a check too: a test, a hook, CI, or a search for the refactor skills: in `docs/agents/scripts/refactor-checks.sh`, or in the ready checks of a stack's rules, such as `docs/agents/scripts/laravel-checks.sh` of `laravel-rules`.

End with the links you read today. Discuss one question per reply, each with your recommended answer and why. Done when the user agrees on the kind and the place, or decides to drop it.

## 5. Make it, once agreed

Write it where it was agreed, in very simple English:

- **A skill**: follow `writing-for-agents`. Write it so it works with every agent: no tool, command or file that only one agent has, unless the skill says what to do without it. In a skills repository, add it in every place that repository's `AGENTS.md` or `CLAUDE.md` lists, such as its README rows and its docs page, in the shape it gives. Name the skills it calls in its "Before you start" part.
- **A rule for a stack**: a file in `rules/<stack>` with `paths`, and its check in that stack's ready checks, such as `docs/agents/scripts/laravel-checks.sh`.
- **A line for every session**: the project's `AGENTS.md`, or the user's shared rules that every project gets. When the project has a `CLAUDE.md`, it imports `AGENTS.md` with `@AGENTS.md`. Keep it short; move details to a file it points at.
- **A kind only some agents have**, such as a rule for some files or an agent hook: make it for each agent the project uses, and name it in one line of `AGENTS.md`, as [PLACES.md](PLACES.md) says.
- **A decision that matters**: an ADR, as the project's rules on decisions say, such as a `decisions.md`.

Open a pull request for it. Done when its link is given to the user.
