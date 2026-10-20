## What it does

`refactor-issues` opens GitHub issues that bring old code in line with the rules your project already wrote, without changing what users get. Each run opens the next batch, at most 10 open at once. One issue covers one file and every rule it breaks.

It reads the rules from the project itself: `CLAUDE.md`, `AGENTS.md`, `.claude/rules`, `CONTRIBUTING.md` and the linters. It grades each file by how much a mistake could hurt, and starts with the safest files. A change that cannot keep the output the same becomes a question for you, not a refactor.

## When to reach for it

Type `/refactor-issues` when old code breaks rules you wrote later, and you want to fix it step by step, safest first.

| Your situation | Where to go |
| --- | --- |
| A project with written code rules, in any language | `refactor-issues` |
| A Laravel project | The rules and their ready checks from [laravel-rules](https://github.com/youssef-ahmed-Devlogs/laravel-rules), then `setup-refactor-issues` and this skill |
| A project with no written rules | Write the rules first: this skill stops without them |
| The batch is open, and you want it done | [`implement-refactor-issues`](./implement-refactor-issues.md) does it in one pull request |

## Prerequisites

Run [`setup-refactor-issues`](./setup-refactor-issues.md) once first: it writes the project's checks from its rules, and makes the labels. Without it, this skill stops and asks for it. You also need `gh`.
