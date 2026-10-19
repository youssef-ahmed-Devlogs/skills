# The issues this skill opens

Both kinds follow the project's issue shape. When the project has issue templates in `.github/ISSUE_TEMPLATE`, a refactor issue fills `.github/ISSUE_TEMPLATE/refactor.md`, and a `review-critical` one fills `feature.md`. Without a template, use the sections below. This file adds only what is special to this skill.

## A refactor issue

- Labels: `refactor`, its review flag and `ready-for-agent`.
- Title: ``Refactor: `<path>` follows the conventions``. The path in backticks is how later runs find the issue.
- `## Why` starts with "`<path>` was written before the conventions. It breaks <n> of them.", then one line per break: the line number, what the code does, what the rule asks, and the file the rule is in. This list may pass 5 lines: it names every break.
- `## Decisions` starts with "Only the code changes. What users get stays the same.", then one line per break on how the output stays the same, such as "The JSON keeps its shape and its key names."
- `## What to do`: the steps in order. The first is always the tests: those that check the part that will change, or a new one that does and passes on the old code before any change. A test that only runs the code, and does not check that part, is not enough. The test checks what the code gives out, such as its result or what it writes, never how it works inside: so it passes on the old code and on the new. The last runs them again, with no change to them. A data change follows the project's rules for it.
- `## Done when` always holds "The old tests pass with no change to them."
- The last line is `Found by /refactor-issues.`, or `Follows #<number>.` when an earlier refactor issue exists for this file.

## A `review-critical` issue

A break that cannot keep the output the same.

- Labels: `refactor`, `review-critical` and `ready-for-human`.
- Title: ``Decision: `<path>` <what would change>``, such as ``Decision: `src/mail/welcome.ts` would arrive late if queued``.
- `## Why`: the break and the file its rule is in, and what users would see change.
- `## Decisions`: the choices for the owner, each with what users would see. The first is always "Leave the code as it is, and close this issue as `wontfix`."
- `## What to do`: each way that was tried, and why it still changes the output.
- `## Done when`: the owner picks a choice.
