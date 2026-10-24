---
name: implement-refactor-issues
description: Do the open refactor issues that /refactor-issues opened, one batch in one pull request, with what users get kept the same. Works in any project and any language.
disable-model-invocation: true
---

# Implement refactor issues

`/refactor-issues` opens refactor issues in batches, safest first. This skill does them: it takes the open batch, fixes each file as its issue says, and opens one pull request for the whole batch, which closes every issue in it.

## Before you start

This skill calls two skills of Matt Pocock: `tdd`, to write each test first, and `code-review`, to review the batch. When one is missing, stop and give the command that installs it:

```bash
npx skills add mattpocock/skills --skill tdd --skill code-review
```

## The output never changes

A refactor changes only how the code is written. The business logic stays exactly as it is, and so does everything a user gets: the same pages, texts, redirects, status codes, API answers, mails and timing. Each issue says, under `## Decisions`, how its output stays the same. Follow it.

When a change turns out to change the output after all, undo that change. Never ship it. Step 5 says what to do instead.

## 1. Check the setup

- The project has a GitHub remote, and `gh auth status` shows a signed-in user.
- `docs/agents/scripts/refactor-checks.sh` exists. When it does not, stop: the project needs `/setup-refactor-issues` first.

## 2. Pick the batch

```bash
gh issue list --label refactor --label ready-for-agent --state open --search "-label:review-critical" --limit 50 --json number,title,labels
```

- When the user names issues, take those.
- Otherwise, the stage is the safest review flag that still has open issues: `review-optional`, then `review-suggested`, then `review-required`. Take every open issue of that stage. Never mix stages in one batch.
- With no open issue, stop, and say that the next step is `/refactor-issues`.

Tell the user the issues of the batch, with their titles, before you change any file.

## 3. Read before you change

- The project's rules: `AGENTS.md`, `CLAUDE.md`, `.claude/rules`, `.github/copilot-instructions.md`, `.github/instructions` and the docs they name. Its rules for branches, commits, tests and pull requests hold for this work.
- Each issue in full, with its comments: `gh issue view <number> --comments`. Read the issues it names too, such as a `review-critical` one.
- Each file of the batch and its tests.

## 4. Make the branch

Make one branch from the main branch, named as the project's rules say. Without such a rule, name it for the batch, such as `refactor/504-533-optional-batch`.

## 5. Do each issue

Go from the smallest file to the biggest. For each issue:

1. **Tests first.** Do the first step of its `## What to do`, with the `tdd` skill: a test that checks what the code gives out, and passes on the old code before any change.
2. **The changes.** Fix each break that `## Why` lists, the way `## Decisions` says. Change nothing the issue does not name: a break it puts out of scope stays.
3. **Check it.** Run the tests of the file, with no change to them, and the project's formatter on the changed files. Then run `bash docs/agents/scripts/refactor-checks.sh | grep -F '<path>'`: no line of a fixed break may be left.
4. **Commit** the issue's change on its own, with its number in the message.

When a break cannot keep the output the same, undo its change, and say on the issue, in a comment, what would change and why. When the file's other breaks are done, the issue stays in the batch and its pull request line says it is done in part. When nothing of it can be done, take it out of the batch, and give it the label `ready-for-human` in place of `ready-for-agent`.

## 6. Check the batch

1. Run the whole test suite once, and every other check the project's CI runs, such as arch tests or a linter.
2. Run the reviews the project's rules name. Without such a rule, call the `code-review` skill on the branch.
3. Fix what they find, and commit the fixes.

## 7. Open the pull request

Push the branch and open one pull request, as the project's rules for pull requests say:

- Its title names the batch, such as ``Refactor: ten more files follow the conventions (504 to 513)``.
- Its review flag is the stage of the batch, with its label.
- Its body says that users see no change, then what changed in plain words, and one `Closes #<number>` line for each issue done in full.
- Its comment says which tests ran and their result, what each review found and how it was fixed, and each issue or break left out, with the reason.

## 8. Report

Tell the user, in a few lines: the pull request's link, the issues it closes, each issue or break left out and why, and how many open refactor issues are left. The next step: merge it, then `/refactor-issues` for the next batch.
