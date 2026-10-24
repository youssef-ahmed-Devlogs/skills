# setup-refactor-issues

Prepares a project for [`refactor-issues`](./refactor-issues.md). It turns the project's written code rules into searches and a reading list, and makes the labels the issues use. Run it once per project, and again when the rules change.

**Start it:** `/setup-refactor-issues`, in the project. It starts only when you type it.

## What it does

1. It reads every place that says how code must be written: `CLAUDE.md`, `AGENTS.md`, `.claude/rules`, `CONTRIBUTING.md` and the linters' config.
2. It finds ready checks that came with a stack's rules, such as `laravel-checks.sh` from [laravel-rules](https://github.com/youssef-ahmed-Devlogs/laravel-rules), and uses them instead of writing them again.
3. It writes `docs/agents/scripts/refactor-checks.sh`: one search for each rule a search can find.
4. It writes `docs/agents/refactor-checks.md`: one line for each rule only reading can see.
5. It runs the searches and shows you how many files each one finds, to catch a wrong search.
6. It makes the labels, such as `refactor` and the review flags, and opens a pull request.

It asks one question per message, and never removes a line of yours without asking.

## When to use it

| Your situation | Use |
| --- | --- |
| The first time, before `refactor-issues` | `setup-refactor-issues` |
| You added, changed or removed code rules | `setup-refactor-issues` again |
| The project has no written code rules | Write them first: this skill stops without them |

## Example

A TypeScript project. Its `CONTRIBUTING.md` says: no `console.log` in `src`, React components live in `src/components`, and a hook's name starts with `use`.

```text
You:    /setup-refactor-issues

Agent:  I found 3 code rules in CONTRIBUTING.md, and no ready checks.
        - "no console.log in src": a search can find it.
        - "components live in src/components": a search can find it, by file path.
        - "a hook's name starts with use": only reading can see it.

        I ran the two searches:
        - console.log: 14 files.
        - a component outside src/components: 3 files.
        Do these counts look right to you?

You:    Yes.

Agent:  Written: docs/agents/scripts/refactor-checks.sh (2 checks) and
        docs/agents/refactor-checks.md (1 line). Made 7 labels.
        Pull request #18 is open. Next step: /refactor-issues.
```

## More use cases

- **A Laravel project:** after `/setup-laravel-rules`, it wires in the ready Laravel checks, and adds checks only for the project's own rules.
- **New rules later:** it adds the checks of the new rules, and asks before it drops the check of a rule that is gone.

## What you get

Two files in the project, the labels on GitHub, and a pull request.

## What it needs

Written code rules in the project, and `gh` with a GitHub remote for the labels.
