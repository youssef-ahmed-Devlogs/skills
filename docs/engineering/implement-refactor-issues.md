## What it does

`implement-refactor-issues` does the refactor issues that [`refactor-issues`](./refactor-issues.md) opened. It takes the open batch, safest first, fixes each file as its issue says, and opens one pull request that closes the whole batch.

Each issue gets a test first, a test that passes on the old code. Then the file changes, and the same tests pass again with no change to them. The project's checks run again on each file, to show its breaks are gone. A change that would change what users get is undone, and the issue says why.

## When to reach for it

Type `/implement-refactor-issues` when refactor issues are open and you want them done, without writing a prompt each time.

| Your situation | Where to go |
| --- | --- |
| Refactor issues are open | `implement-refactor-issues` |
| No refactor issue is open | [`refactor-issues`](./refactor-issues.md) opens the next batch |
| An issue waits for your choice, with `review-critical` | Answer it first: this skill leaves it alone |

## Prerequisites

The project is set up with [`setup-refactor-issues`](./setup-refactor-issues.md), and has open issues from `refactor-issues`. You need `gh`, and Matt Pocock's `tdd` and `code-review`: `npx skills add mattpocock/skills --skill tdd --skill code-review`.
