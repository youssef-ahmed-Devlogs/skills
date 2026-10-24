# implement-refactor-issues

Does the open refactor issues that [`refactor-issues`](./refactor-issues.md) opened: the whole batch, in one pull request, with what users get kept the same.

**Start it:** `/implement-refactor-issues`, or name the issues, such as `/implement-refactor-issues 20 21 22`. It starts only when you type it.

## Before you start

**Install it:**

```bash
npx skills add youssef-ahmed-Devlogs/skills --skill implement-refactor-issues
```

It asks which agents to install it for: pick every agent you use. Other ways, and updates: [Installing](../install.md).

**It needs:** The project set up by [`setup-refactor-issues`](./setup-refactor-issues.md), and open issues from `refactor-issues`. Then `gh`, and Matt Pocock's `tdd` and `code-review`:

```bash
npx skills add mattpocock/skills --skill tdd --skill code-review
```

**Where to run it:** Inside the project's folder. Make no folder: it makes the branch and opens the pull request itself.

**Call it:** in Claude Code or GitHub Copilot, type `/implement-refactor-issues`. In Codex, type `$implement-refactor-issues`.

**Agents:** Claude Code, Codex and GitHub Copilot, or any agent that reads skills.

## What it does

1. It takes the open batch of the safest review level, and lists it for you before it changes any file.
2. It reads the project's rules, each issue with its comments, and each file with its tests.
3. It makes one branch for the batch.
4. For each issue, smallest file first:
   - a test that checks what the code gives out, and passes on the old code;
   - the change, as the issue's decisions say, and nothing more;
   - the same tests again, with no change to them, the formatter, and the project's searches, to show the breaks are gone;
   - one commit, with the issue's number.
5. It runs the whole suite and the reviews the project names, and fixes what they find.
6. It opens one pull request that closes the issues done in full.

A change that turns out to change what users get is undone, never shipped. The issue gets a comment that says why.

## When to use it

| Your situation | Use |
| --- | --- |
| Refactor issues are open | `implement-refactor-issues` |
| No refactor issue is open | [`refactor-issues`](./refactor-issues.md) opens the next batch |
| An issue waits for your choice, with `review-critical` | Answer it first: this skill leaves it alone |

## Example

The batch of the refactor page is open:

```text
You:    /implement-refactor-issues

Agent:  The batch: 10 review-optional issues, #20 to #29. Starting with #20,
        src/utils/date.ts, the smallest file.

        #20: added a test that checks the dates it gives out. It passes on the old code.
        Removed the console.log lines. The same test passes. The search finds no line.
        Committed: "refactor(#20): date.ts drops console.log".
        ...
        #25: the change would move a log line that a support script reads. Undone, and
        explained in a comment on #25. Its other break is done.

        The whole suite passed: 340 tests. The code review found one leftover import,
        fixed and committed.

        Pull request #31 is open. It closes 9 issues; #25 is done in part.
        1 refactor issue is left open. Next: merge #31, then /refactor-issues.
```

## More use cases

- **Your own pick:** name the issues, and it does only those.
- **A file that turns out risky:** it does the safe breaks, leaves the rest with a reason, and the pull request says so.

## What you get

One branch, one commit per issue, and one pull request whose comment lists the tests that ran, what each review found, and what was left out and why.
