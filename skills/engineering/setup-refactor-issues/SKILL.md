---
name: setup-refactor-issues
description: Prepare a project for /refactor-issues. Writes its checks file and reading list from the project's own code rules, wires in the ready checks of a stack's rules, and makes the labels. Run once per project, and again when its rules change. Works in any project and any language.
disable-model-invocation: true
---

# Set up refactor issues

`/refactor-issues` finds old code that breaks the project's written rules, and opens issues to fix it. It needs three things in the project, and this skill makes them:

- `docs/agents/refactor-checks.sh`: one search for each rule a search can find;
- `docs/agents/refactor-checks.md`: one line for each rule that only reading can see;
- the labels its issues use.

Run it once per project. Run it again when the rules change: it adds the checks of new rules, and drops the checks of rules that are gone.

## How to work

- Ask the user **one question per message**, with your recommended answer and why. Find what you can yourself, and only ask to confirm it.
- Never replace or delete a line of the user's without asking.
- Work on a new branch, named as the project's rules say, never on the main branch. Make it from the branch that has the project's rules: the main branch, or the branch of a setup that is not merged yet, such as the one `/setup-laravel-rules` made.

## 1. Find the rules

Find every place the project says how code must be written, and read it all:

- `CLAUDE.md` and `AGENTS.md`, at the root and in every folder;
- `.claude/rules`, and any other rules folder of an agent;
- `CONTRIBUTING.md`, a coding standards file, and the docs these files point to;
- the config of its linters and formatters, for the rules they hold.

Only the lines that say how code must be written count, such as where a file goes, what a class may do, or how a name is written. Rules about branches, issues or reviews do not. A rule written for new code, such as "new helpers go in `src/lib`", counts for old code too.

When the project has no such rules, stop, and tell the user to write them first. For a Laravel project, `/setup-laravel-rules` from `youssef-ahmed-Devlogs/laravel-rules` puts ready rules in.

## 2. Find the ready checks

Some rules come with ready checks from their own repository, such as `docs/agents/laravel-checks.sh` and `docs/agents/laravel-checks.md`, which `/setup-laravel-rules` copies. List every `docs/agents/*-checks.sh` other than `refactor-checks.sh`, and its `.md` beside it.

The rules these files check need no check of yours. Never edit them: their repository replaces them on each update. A rule of the project that they do not cover, such as one in `.claude/rules/project`, gets its check in the project's own files below.

## 3. Write the checks file

When `docs/agents/refactor-checks.sh` is missing, copy [refactor-checks.template.sh](refactor-checks.template.sh) of this skill's folder there. Then fill it in:

1. **The ready checks.** Under the line `# The ready checks of a stack's rules`, add one line for each file of step 2, such as `source docs/agents/laravel-checks.sh | not_skipped`. The pipe keeps the folders of `SKIP` out of them too.
2. **The folders to skip.** Put in `SKIP`, at the top, the folders no check should look in, such as code that a tool writes.
3. **The project's own checks.** Add one line for each rule of step 1 that a search can find and no ready check covers. A folder of the project's own code that the ready checks do not search gets lines for their rules too, such as JS kept in `public/assets` when they search `resources/js` only. Write the lines as the template's examples show: `check` for a pattern inside files, and `check_path` for a rule about a file's name or folder. The second field names the rule's file, such as `project/roles.md`.
4. **Try it.** Run `bash docs/agents/refactor-checks.sh` from the project root, and show the user how many files each check finds. A check that finds every file, or none where you know of one, is wrong: fix it.

When the file exists, bring it up to date: add a check for each rule that has none, a `source` line for each new ready file, and ask before you remove the check of a rule that is gone.

## 4. Write the reading list

In `docs/agents/refactor-checks.md`, write one line for each rule of step 1 that only reading can see, and that no ready list covers: the rule's file, what breaks it, and where to look. Name each rule's file by its path under `.claude/rules`, such as `project/roles.md`, and say so at the top of the list. For example: `` `project/roles.md`: a role checked by its name, in `app/Http` ``.

At its top, add one line for each ready list of step 2: `` Also read `docs/agents/laravel-checks.md`: the checks of the Laravel rules. ``

## 5. Make the labels

List the labels the repository has with `gh label list --limit 200 --json name --jq '.[].name'`, then make each missing one:

```bash
gh label create refactor --description "Bring old code in line with the project's rules" --color 5319e7
gh label create review-critical --description "Would change what users see or get: the owner decides before any work" --color b60205
gh label create review-required --description "A person must review it before the merge" --color d93f0b
gh label create review-suggested --description "A quick look before the merge is good" --color fbca04
gh label create review-optional --description "Safe to merge once the checks pass" --color 0e8a16
gh label create ready-for-agent --description "Clear enough for an agent to do" --color 1d76db
gh label create ready-for-human --description "A person must decide or do it" --color c5def5
```

When the project has no GitHub remote, skip this step, and tell the user that `/refactor-issues` opens GitHub issues, so it needs one.

## 6. Finish

1. Commit both files. When the project has a GitHub remote, push and open a pull request, as the project's rules say. Without one, tell the user the branch's name.
2. Tell the user, in a few lines: how many rules got a check, how many are on the reading list, which ready checks are wired in, and the next step: `/refactor-issues`. Until the pull request is merged, run it from this branch, where the files are.

Done when both files are in the project, the labels exist, and the pull request's link or the branch's name is given.
