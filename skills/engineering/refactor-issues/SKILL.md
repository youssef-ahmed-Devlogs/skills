---
name: refactor-issues
description: Open the next batch of refactor issues that bring old code in line with the project's own code rules, safest first. Works in any project and any language.
disable-model-invocation: true
---

# Refactor issues

Each run opens the next **batch** of GitHub issues, at most 10 open at once, that bring old code in line with the rules of the project it runs in. One issue covers one file and all its breaks of those rules. The batch always comes from the safest **stage** that still has work, and inside it the simplest files go first.

A Laravel project that keeps its rules in `.claude/rules/laravel`, one file per subject, can use `/laravel-refactor-issues` instead: it does the same, with a ready search for those rules.

## The output never changes

The app may run on production for real users. A refactor changes only how the code is written. The business logic stays exactly as it is, and so does everything a user gets: the same pages, texts, redirects, status codes, API answers, mails and timing.

Every break is planned, none is skipped for being hard. For each one, find the way that applies the rule and keeps the output the same. For example:

- JSON that a client reads: it keeps its shape and its key names, even when the code that builds it moves.
- An error that shows a message: when its handling moves, the same message still shows.
- A text written in the code: when it moves to the translation files, it keeps the very same words.
- A job done at once today: it moves to a queue only when the delay changes nothing for the person.
- A renamed constant or case: the value stored in the database stays the same.

Only when no such way exists, after real search, does that break leave the file's issue. It gets its own issue with the label `review-critical` (see step 7). That issue changes nothing: it is a question for the owner, and no work starts on it until the owner decides.

## 1. Read the project's rules

Find every place the project says how code must be written, and read it all:

- `CLAUDE.md` and `AGENTS.md`, at the root and in every folder;
- `.claude/rules`, and any other rules folder of an agent;
- `CONTRIBUTING.md`, a coding standards file, and the docs these files point to;
- the config of its linters and formatters, for the rules they hold;
- `docs/agents/refactor-checks.md`, when it exists: the project's list of what only reading can see.

Only the lines that say how code must be written count, such as where a file goes, what a class may do, or how a name is written. Rules about branches, issues or reviews do not. A rule written for new code, such as "new helpers go in `src/lib`", counts for old code too: bringing old code in line with it is the point of this skill. These rules are the only source of what counts as a break.

When the project has no such rules, stop, and tell the user: this skill needs written rules to compare the code with.

## 2. Count the open issues

```bash
gh issue list --label refactor --state open --search "-label:review-critical" --json number --jq length
```

The batch size is 10 minus that number. Open `review-critical` issues do not count: they wait for the owner. At 0, stop and tell the user how many refactor issues are still open.

## 3. Find the candidates

Write down the scope first:

- in: the folders of the app's own source code;
- out: old migrations (an old migration is never edited), code that a tool writes, code of other authors, such as `vendor` or `node_modules`, and tests on their own (a test changes only with the file it tests).

Then check that the project has its checks file, `docs/agents/refactor-checks.sh`. When it is missing, stop and ask the user first, and recommend making it. Say that this skill's guidance is to keep the project's searches in that file: then every run checks the same things, in seconds, as a ready scan does.

- **They agree**: copy [refactor-checks.template.sh](refactor-checks.template.sh) of this skill's folder to `docs/agents/refactor-checks.sh`. Add one line for each rule of step 1 that a search can find, as the template's examples show: `check` for a pattern inside files, and `check_path` for a rule about a file's name or folder. Put the folders no check should look in, such as code that a tool writes, in `SKIP`, at the top of the file. Put each rule that only reading can check in `docs/agents/refactor-checks.md`, one line each: the rule, its file, and where to look. Run the script once to see that it works. Commit both files on a new branch, named as the project's rules say. When the project has a GitHub remote, open a pull request as its rules say; without one, tell the user the branch's name. Go on with this run on that branch, where the files are. Until the pull request is merged, run the skill from that branch, or it will not find the file.
- **They do not**: go on, and write the searches yourself in item 3 below.

Then find the files that may break a rule, with the fastest tools first:

1. **The project's own checks.** When the checks file exists, run it from the project root: `bash docs/agents/refactor-checks.sh`. Each line it prints is `<path> <TAB> <check> <TAB> <rule file> <TAB> <hits>`.
2. **Its linters.** Run the linters and static checks the project already has, and keep the hits that match a rule of step 1. When one cannot run, such as when its packages are not installed, say so in the report and rely on the searches.
3. **Your own searches.** For each rule a search can check that the checks file does not cover yet, such as a banned function, a folder or a name, write a search. Note the rule file each one serves:

   ```bash
   # code.md: never console.log in src/
   grep -rlP 'console\.log\(' --include='*.ts' src
   ```

4. **Reading.** For each rule that no search can check, such as "a handler holds no logic", read the files that rule is about, such as every file in `src/handlers`. `docs/agents/refactor-checks.md`, when it exists, lists these rules and where to look. A file that breaks one becomes a candidate here, like a hit of a search.

A file's number of breaks, for the order of step 5, is the number of rules it breaks, not the raw hits. A rule written in two places, such as in a rules file and in a linter's config, counts once. Drop a file that already has a `refactor` issue open, or one closed as `wontfix`:

```bash
gh issue list --label refactor --state all --search "\"<path>\" in:title" --json number,state,labels
```

A file whose last `refactor` issue was closed as done, and that breaks a rule again, gets a new issue that links the old one.

## 4. Grade each candidate's risk

Give each candidate the review flag its change would need. When the project has the levels of a review flag, such as `.claude/rules/process/pull-requests.md`, use them. Otherwise:

- `review-required`: the file touches sign-in, codes, tokens, roles, permissions, or who owns a record; the change needs a migration or a data change; it moves the logic of a main feature, such as checkout or sign-in, or changes how a public API answers; or no test covers logic that will change. Logic of a main feature, such as money or sign-in, stays at this level even when it only moves.
- `review-suggested`: the change touches what people see, such as a page, a text or a JSON answer; or it only moves or renames code that no test covers, and the logic stays exactly as it is.
- `review-optional`: the change touches nothing people see, and a test runs the code that changes. The test does not need to check the changed line yet: the issue's first step adds that check (see ISSUE.md).

The level follows the change, not the file: a log line in the core of the app is still a small change.

In every level the output stays the same: the level says how much a mistake could hurt, not how much may change.

When unsure, pick the higher level. Read the file and its tests to decide: a guess from the path alone is a start, not a grade.

## 5. Pick the batch

The stage is `review-optional`. When no candidate is left at that level, the stage is `review-suggested`, then `review-required`. Never mix stages in one batch.

Inside the stage, order by fewest breaks first, then by the smallest file. Take as many as the batch size.

## 6. Confirm each file

Read each file of the batch in full. Confirm every hit is a real break of a rule, drop false hits, and add the breaks no search can see. A file left with no real break leaves the batch, and the next candidate takes its place.

For each break, write how the output stays the same, as the section above asks.

## 7. Open the issues

First make the labels the issues use, when the repository lacks them. List the ones it has with `gh label list --limit 200 --json name --jq '.[].name'`, then make each missing one:

```bash
gh label create refactor --description "Bring old code in line with the project's rules" --color 5319e7
gh label create review-critical --description "Would change what users see or get: the owner decides before any work" --color b60205
gh label create review-required --description "A person must review it before the merge" --color d93f0b
gh label create review-suggested --description "A quick look before the merge is good" --color fbca04
gh label create review-optional --description "Safe to merge once the checks pass" --color 0e8a16
gh label create ready-for-agent --description "Clear enough for an agent to do" --color 1d76db
gh label create ready-for-human --description "A person must decide or do it" --color c5def5
```

One issue per file, in the shape of [ISSUE.md](ISSUE.md), with the labels `refactor`, its review flag and `ready-for-agent`. Write it as the project's rules for issues say.

A break that cannot keep the output the same gets its own issue, as the `review-critical` part of ISSUE.md says, with the labels `refactor`, `review-critical` and `ready-for-human`. It says what users would see change, what was tried, and the choices for the owner. It is not part of the batch count.

## 8. Report

Tell the user, in a few lines: the issues opened with their links, the stage, and how many candidates are left in it. When a search you wrote in step 3 would help every later run, offer to add it to `docs/agents/refactor-checks.sh` as a `check` line.
