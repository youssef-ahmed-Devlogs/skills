## What it does

`delegating-to-cli` works through a list of fixes with you as the coordinator. For each item it writes or reads the issue, opens a separate Claude Code CLI session in a terminal tab as the worker, and gives it the issue. It answers the worker's questions, reviews the diff against the repository's own rules, merges, and cleans up. Then it moves to the next item.

Each item runs in its own git worktree, so the worker never touches the folder you work in.

## When to reach for it

Type `/delegating-to-cli` when you have several fixes that touch different parts of the code, and you want to watch and steer each one in its own tab.

| Your situation | Where to go |
| --- | --- |
| A list of separate fixes, one pull request each | `delegating-to-cli` |
| One small fix you can do right here | Matt Pocock's [`implement`](https://github.com/mattpocock/skills) |
| One task for a worker in the background, with no tab to watch | A delegate skill, such as [`claude-delegate`](https://github.com/amElnagdy/delegate-skills) |

## Prerequisites

The worker uses Matt Pocock's `implement`, `tdd`, `code-review` and `codebase-design`. When one is missing, the skill stops and gives you the command that installs it. You also need the `claude` CLI and `gh`.
