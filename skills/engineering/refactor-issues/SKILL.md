---
name: refactor-issues
description: Open the next batch of refactor issues that bring old code in line with the project's own code rules, safest first. Works in any project and any language.
disable-model-invocation: true
---

# Refactor issues

Each run opens the next **batch** of GitHub issues, at most 10 open at once, that bring old code in line with the rules of the project it runs in. One issue covers one file and all its breaks of those rules. When two files must change together, such as a view and the script it calls, one issue covers both: it is named after the main file and names the other. The batch always comes from the safest **stage** that still has work, and inside it the simplest files go first.

It works from the files that `/setup-refactor-issues` writes in the project: run that skill once first.

## The output never changes

The app may run on production for real users. A refactor changes only how the code is written. The business logic stays exactly as it is, and so does everything a user gets: the same pages, texts, redirects, status codes, API answers, mails and timing.

Every break is planned, none is skipped for being hard. For each one, find the way that applies the rule and keeps the output the same. For example:

- JSON that a client reads: it keeps its shape and its key names, even when the code that builds it moves.
- An error that shows a message: when its handling moves, the same message still shows.
- A text written in the code: when it moves to the translation files, it keeps the very same words.
- A job done at once today: it moves to a queue only when the delay changes nothing for the person.
- A renamed constant or case: the value stored in the database stays the same.

Only when no such way exists, after real search, does that break leave the file's issue. It gets its own issue with the label `review-critical` (see step 8). That issue changes nothing: it is a question for the owner, and no work starts on it until the owner decides.

## 1. Check the setup

This skill opens GitHub issues: when the project has no GitHub remote, stop and say so. The project also needs `docs/agents/scripts/refactor-checks.sh`, and the label `refactor` in its repository:

```bash
test -f docs/agents/scripts/refactor-checks.sh && gh label list --search refactor --json name --jq '.[].name'
```

When either is missing, stop. Tell the user the project is not set up for this skill yet, and to run `/setup-refactor-issues` first: it writes the project's checks from its rules and makes the labels. When that skill is not installed, give the command:

```bash
npx skills add youssef-ahmed-Devlogs/skills --skill setup-refactor-issues
```

## 2. Read the project's rules

Find every place the project says how code must be written, and read it all:

- `CLAUDE.md` and `AGENTS.md`, at the root and in every folder;
- `.claude/rules`, and any other rules folder of an agent;
- `CONTRIBUTING.md`, a coding standards file, and the docs these files point to;
- the config of its linters and formatters, for the rules they hold;
- `docs/agents/refactor-checks.md`, the project's list of what only reading can see, and every list it names, such as `docs/agents/laravel-checks.md`. A list says in which folder its rule files are.

Only the lines that say how code must be written count, such as where a file goes, what a class may do, or how a name is written. Rules about branches, issues or reviews do not. A rule written for new code, such as "new helpers go in `src/lib`", counts for old code too: bringing old code in line with it is the point of this skill. These rules are the only source of what counts as a break.

## 3. Count the open issues

```bash
gh issue list --label refactor --state open --search "-label:review-critical" --json number --jq length
```

The batch size is 10 minus that number. Open `review-critical` issues do not count: they wait for the owner. At 0, stop and tell the user how many refactor issues are still open.

## 4. Find the candidates

Write down the scope first:

- in: the folders of the app's own source code;
- out: old migrations (an old migration is never edited), code that a tool writes, code of other authors, such as `vendor` or `node_modules`, and tests on their own (a test changes only with the file it tests).

Then find the files that may break a rule, with the fastest tools first:

1. **The project's checks.** Run them from the project root: `bash docs/agents/scripts/refactor-checks.sh`. It runs the ready checks of a stack's rules too, such as `laravel-checks.sh`. Each line it prints is `<path> <TAB> <check> <TAB> <rule file> <TAB> <hits>`.
2. **Its linters.** Run the linters and static checks the project already has, and keep the hits that match a rule of step 2. When one cannot run, such as when its packages are not installed, say so in the report and rely on the searches.
3. **Your own searches.** For each rule a search can check that the checks file does not cover yet, such as a banned function, a folder or a name, write a search. Note the rule file each one serves:

   ```bash
   # code.md: never console.log in src/
   grep -rlP 'console\.log\(' --include='*.ts' src
   ```

4. **Reading.** For each rule that no search can check, such as "a handler holds no logic", read the files that rule is about, such as every file in `src/handlers`. `docs/agents/refactor-checks.md`, and the lists it names, give these rules and where to look. A file that breaks one becomes a candidate here, like a hit of a search.

A file's number of breaks, for the order of step 6, is the number of rules it breaks, not the raw hits. A rule written in two places, such as in a rules file and in a linter's config, counts once. Drop a file that already has a `refactor` issue open, or one closed as `wontfix`:

```bash
gh issue list --label refactor --state all --search "\"<path>\" in:title" --json number,state,labels
```

A file whose last `refactor` issue was closed as done, and that breaks a rule again, gets a new issue that links the old one.

## 5. Grade each candidate's risk

Give each candidate the review flag its change would need. When the project has the levels of a review flag, such as `.claude/rules/workflow/pull-requests.md`, use them. Otherwise:

- `review-required`: the file touches sign-in, codes, tokens, roles, permissions, or who owns a record; the change needs a migration or a data change; it moves the logic of a main feature, such as checkout or sign-in, or changes how a public API answers; or no test covers logic that will change. Logic of a main feature, such as money or sign-in, stays at this level even when it only moves.
- `review-suggested`: the change touches what people see, such as a page, a text or a JSON answer; or it only moves or renames code that no test covers, and the logic stays exactly as it is.
- `review-optional`: the change touches nothing people see, and a test runs the code that changes, such as a feature test that sends a request through it. The test does not need to check the changed line yet: the issue's first step adds that check (see ISSUE.md).

The level follows the change, not the file: a log line in the core of the app is still a small change.

In every level the output stays the same: the level says how much a mistake could hurt, not how much may change.

When unsure, pick the higher level. Read the file and its tests to decide: a guess from the path alone is a start, not a grade.

## 6. Pick the batch

The stage is `review-optional`. When no candidate is left at that level, the stage is `review-suggested`, then `review-required`. Never mix stages in one batch.

Inside the stage, order by fewest breaks first, then by the smallest file. Take as many as the batch size.

## 7. Confirm each file

Read each file of the batch in full. Confirm every hit is a real break of a rule, drop false hits, and add the breaks no search can see. A file left with no real break leaves the batch, and the next candidate takes its place.

For each break, write how the output stays the same, as the section above asks.

## 8. Open the issues

Open each `review-critical` issue below first, so the refactor issue of its file can name it. Then one issue per file, in the shape of [ISSUE.md](ISSUE.md), with the labels `refactor`, its review flag and `ready-for-agent`. Write it as the project's rules for issues say.

A break that cannot keep the output the same gets its own issue, as the `review-critical` part of ISSUE.md says, with the labels `refactor`, `review-critical` and `ready-for-human`. It says what users would see change, what was tried, and the choices for the owner. It is not part of the batch count.

## 9. Report

Tell the user, in a few lines: the issues opened with their links, the stage, and how many candidates are left in it. The next step is `/implement-refactor-issues`, which does the batch in one pull request. When a search you wrote in step 4 would help every later run, offer to add it to `docs/agents/scripts/refactor-checks.sh` as a `check` line, or to run `/setup-refactor-issues` again.
