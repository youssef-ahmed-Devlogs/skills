# delegating-to-cli

You have a list of fixes. The agent becomes the coordinator: for each fix it writes the issue, hands it to a separate Claude Code CLI session in its own terminal tab, answers that worker's questions, reviews its work, merges, and cleans up. Then it takes the next fix.

**Start it:** `/delegating-to-cli`, with your list. It starts only when you type it.

## Before you start

**Install it:**

```bash
npx skills add youssef-ahmed-Devlogs/skills --skill delegating-to-cli
```

It asks which agents to install it for: pick every agent you use. Other ways, and updates: [Installing](../install.md).

**It needs:** Matt Pocock's `implement`, `tdd`, `code-review` and `codebase-design`, which the workers use. When one is missing, the skill stops and gives you the command that installs it. Then the `claude` CLI, `gh`, and a terminal tool that opens visible tabs, such as the terminal of the Claude desktop app.

**Where to run it:** Inside the project's folder, a git repository with a GitHub remote. Make no folder: it makes one git worktree per fix, beside the project's folder, and removes it after the merge.

**Call it:** in Claude Code or GitHub Copilot, type `/delegating-to-cli`. In Codex, type `$delegating-to-cli`.

**Agents:** Claude Code only, for now. The worker is the `claude` CLI, and the coordinator talks to it with tools of the Claude desktop app. It does not work with Codex or GitHub Copilot yet.

## What it does

1. It asks once what it cannot find itself: who merges, the fallback model if a worker stops, and whether to delete branches after merge. The rest, such as the test command and the issue format, it reads from the repository.
2. For each fix, it reads the code, checks every claim, and writes an issue the worker can follow.
3. It asks you only real product questions, such as how a feature should behave for users. It decides the design itself, and tells you in one line.
4. It makes a git worktree for the fix, so the worker never touches the folder you work in.
5. It suggests the cheapest model that can do the fix, with a reason, and opens the worker in a tab named `claude: issue #N`.
6. It watches for new commits, a stall or the end, without polling you. When the worker stops, such as on a usage limit, a subagent takes over.
7. It reviews the diff and runs the full test suite. A real problem goes back to the worker, not to you.
8. It merges, closes the worker's tab, removes the worktree and the branch, and reports.

## When to use it

| Your situation | Use |
| --- | --- |
| A list of separate fixes, one pull request each | `delegating-to-cli` |
| One small fix you can do right here | Matt Pocock's [`implement`](https://github.com/mattpocock/skills) |
| One task for a worker in the background, with no tab to watch | A delegate skill, such as [`claude-delegate`](https://github.com/amElnagdy/delegate-skills) |

## Example

QA sent three bugs for a shop app:

```text
You:    /delegating-to-cli
        1. The cart total ignores the coupon after a refresh.
        2. The "forgot password" mail has a broken link.
        3. The orders page crashes for a user with no orders.

Agent:  Before the first one: do you merge the pull requests after my review, or do I?

You:    You do.

Agent:  Issue #41 is open for the cart bug: the coupon is read before the cart loads,
        in src/cart/total.ts line 32. Cause known, two files, clear tests.
        Worker: sonnet at medium effort (Recommended), or opus?

You:    sonnet.

Agent:  The worker runs in the tab "claude: issue #41", in its own worktree.
```

A few minutes later:

```text
Agent:  Worker sent DONE 41. I ran the full suite: 212 passed. One problem in review:
        a coupon that expired while in the cart still counts. Sent back with a test to add.
        ...
        Merged pull request #42, closed issue #41, removed the worktree and the branch.
        Next: issue 2, the broken link.
```

## More use cases

- **A backlog of small issues:** each one gets its own worker, review and pull request.
- **Work while you code elsewhere:** the workers stay in their worktrees, and your checkout stays as you left it.
- **Long fixes:** the issue holds the full context, so a worker with a fresh context does the work, and yours stays short.

## What you get

For each fix: an issue, a reviewed pull request, merged or handed to you, and the worktree and branch cleaned up. At the end, a short report with any deploy step.


## Tips

- It follows the repository's own rules first, such as its branch names and pull request format.
- When it gets something wrong, it offers a change to its own skill text, and edits it only on your yes.
