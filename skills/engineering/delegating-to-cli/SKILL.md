---
name: delegating-to-cli
description: Coordinate a list of fixes by handing each one to a separate Claude Code CLI session in a terminal tab. You write the issue, the CLI implements it, you discuss, review, merge and clean up. Use when the user wants work done by a CLI session while you only coordinate.
disable-model-invocation: true
---

# Delegating to CLI

## Before you start

This skill needs these skills: `code-review`, `codebase-design`, `implement`, `tdd`. Check that each one is installed: a folder of that name in `.agents/skills`, `.claude/skills` or `~/.claude/skills`. When one is missing, stop before anything else. Tell the user which one is missing and what this skill needs it for, and give the command that installs it:

```bash
npx skills add mattpocock/skills --skill code-review --skill codebase-design --skill implement --skill tdd
```

Go on once the user has installed it, or says to go on without it.

You are the **coordinator**. A separate Claude Code CLI session in a terminal tab is the **worker**. You don't write the code yourself. You:

1. prepare the work,
2. hand it over,
3. answer the worker's questions,
4. review the result,
5. merge,
6. clean up.

Then move to the next item.

Work through the list **one item at a time**, each in its own git worktree (step 4), so the worker never touches the checkout the user works in.

## Before the first item: confirm once

Ask the user only for what you can't find yourself, and remember the answers for the session:

- **Fallback.** The model and effort of the subagent that takes over when the worker stops (see "When the worker stops"). Default: the worker's.
- **Merge authority.** Do you merge PRs yourself after review, or does the user? Default: ask once.
- **Branch cleanup.** Delete each branch, local and remote, right after merge? Default: yes.

Find these yourself; don't ask:

- the issue tracker (`gh` and the repo remote),
- the base branch,
- the full test command,
- the formatter or linter command,
- the repo's own rules: how it names branches, writes issues and pull requests, labels them, lists deploy steps, and keeps its docs current.

Read `CLAUDE.md` or `AGENTS.md`, every file in `.claude/rules` (and any `.claude/rules` inside subfolders), every file in `docs/agents`, the docs they point to, `package.json` or `composer.json`, and the CI config.

**The repo's rules beat this skill.** Where the repo says how to do a step (a branch name, an issue or PR format, labels, review flags, deploy commands), do it the repo's way. The formats below are the defaults for a repo that says nothing.

## The loop, per item

### 1. Pick the flow

- If a router skill is installed (e.g. `/ask-matt`), consult it **every time** to choose the worker's skill flow:
    - a single-session fix is usually `/implement <issue>`, which drives `/tdd` and then `/code-review`;
    - a hard bug is `/diagnosing-bugs`;
    - a multi-session build is `/to-spec`, then `/to-tickets`, then `/implement` per ticket.
- Without a router, default to `/implement` if it exists. Otherwise tell the worker plainly: write failing tests first, then the fix, then review its own diff.

### 2. Investigate, then write the issue as if you were implementing it

Read the code first: the files, the line numbers, and the claims you are about to make. Verify each claim; don't copy it from an old report.

Then open an issue. When the repo has an issue shape, such as `.claude/rules/process/issues.md`, publish in two parts: the body in that format, short, for the owner to read, with `Full details are in the first comment.` as its last line; and the full issue in the structure below as the first comment, posted right after, with nothing cut, for the worker. With no format, the body holds this structure:

```markdown
## Problem

What is wrong, with file:line evidence and a concrete failing scenario.

## Product decision (made by the owner) <- only if one was needed

The exact rule the user chose. Mark it as fixed.

## Desired behaviour / design

What must be true afterwards. Name the module or seam that should own the rule.

## Out of scope

What not to touch, and where it will be handled instead.

## Acceptance

The tests that must exist. The full suite green. The linter clean.

## Implementer notes

- The files and line numbers above are a starting point, not a boundary. Change whatever else the fix needs.
- If a claim here is wrong, or you see a better design, don't silently follow the issue. Message the coordinating session with what you found and what you propose, and keep working on the parts that don't depend on it.
- Small, obvious corrections you can just make. Mention them in the commit message.
- If it clearly needs more than one session, send a PROPOSAL with a split instead of cutting corners.
```

Label it the way the repo's triage labels say (e.g. `ready-for-agent`).

### 3. Product decisions: ask only for real ones

- A **product decision** is how the feature should behave for users. Examples: what counts as "complete", or how strictly answers match. Ask with one multiple-choice question. Put your recommendation first, marked "(Recommended)", and explain the trade-off of each option in one line.
- Everything else (design, naming, edge-case handling) **you decide**. Then tell the user what you decided, in one line, so they can object.
- Record each decision in the issue and in your memory: under `## Decisions` of the body when it has one, and under "Product decision" of the full issue.

### 4. Branch and worktree

The user may be working in the main checkout at the same time, so the worker gets its own **worktree**, and the main checkout's branch and files stay as they are.

1. Fetch the base, then create the branch and its worktree beside the repo: `git worktree add -b <branch> ../<repo>-<N> origin/<base>`. Name the branch the way the repo's rules say, or `fix/<short-name>` when they say nothing.
2. Make the worktree runnable. Copy the git-ignored files the app needs from the main checkout (e.g. `.env`, local config, enabled-module lists), and install the dependencies with the repo's install command (e.g. `composer install`, `npm ci`). Don't symlink a dependency folder: its autoloader would load code from the main checkout.
3. Run one fast test in the worktree. Done when it passes.

### 5. Launch the worker

First recommend the worker's model and effort, from what step 2 found about this item:

- **Cause known** with file:line, a few files in one layer, clear acceptance tests: a fast model at medium effort, e.g. `--model sonnet --effort medium`.
- **Cause still to find**, many files or layers, a design to choose, or a risky area such as permissions, money, data changes or migrations: the strongest model, e.g. `--model opus --effort medium`, with `high` for the hardest.

Pick the cheapest model that can finish the item without your help. Ask the user with one question: your pick first, marked "(Recommended)", with a one-line reason taken from the item (e.g. "CSS only, three known lines"), and one realistic alternative. Ask again for each item, unless the user set one model for the whole list.

Use the terminal tool that opens a visible tab (e.g. `run_in_terminal`) and title it `claude: issue #N`. The tool may refuse a `cwd` outside the session's folders, so start the command with `cd <worktree> &&`. The command template:

```
cd <worktree> && claude --model <model> --effort <effort> "/implement <issue-url>. Work only in this worktree (<worktree>) on the current branch <branch> and commit there. Never touch <main-checkout>: the user is working there. If you run a server for a browser check, use a port of your own. Do not push and do not open a PR. When you are completely finished, use ListAgents and send a message to the coordinating session (ref <your-ref>) saying DONE <N> with a one-paragraph summary; if you get blocked or disagree with the issue, message it with BLOCKED or PROPOSAL and the reason."; exit
```

- Get `<your-ref>` from `ListAgents`. It prints your own session's ref.
- **You own the worker's tab: you open it, and you close it, whatever happens.** The user never types in it. Close it yourself every time with the steps of the section "Close the worker", and never ask the user to close it.
- Keep the words `branch <branch>` in the command: the monitor below finds the worker's process by them.
- **The command must be printable ASCII.** A non-ASCII character such as an Arabic session name is refused, so refer to yourself by the ref, not the name.
- If you need to tell the worker something after launch, use `SendMessage` to its peer name from `ListAgents`.

### Close the worker

1. Close its tab with the terminal tool (e.g. `stop_terminal_tab` with `close: true`).
2. The tool may refuse and say the user typed in the tab. That is a false alarm: the user never types there. End the worker yourself with `pkill -f "[b]ranch <branch>"`; the brackets keep `pkill` from matching its own shell. The `; exit` at the end of the launch command then ends the tab's shell too.
3. The CLI can take a few seconds to exit. If it is still there after 5 seconds, run `pkill -KILL -f "[b]ranch <branch>"`.
4. A tab launched without `; exit` keeps an idle shell. End it with `kill -HUP <pid>`, where `<pid>` is the shell whose `/proc/<pid>/cwd` is the worktree.
5. Done when `pgrep -f "[b]ranch <branch>"` finds nothing and the tab is gone from the terminal tool's tab list.

### 6. Monitor cheaply

Every wake re-sends your whole context, so the monitor speaks only on **new commits**, a **stall**, or the process exiting, and the worker's DONE message is the real signal. **An interactive CLI does not exit when it finishes**, so don't wait for the process to exit.

A worker can also **stall** without exiting or committing: a usage limit, a question it waits on, a permission prompt. A watch on commits and exit alone stays silent through that, so the monitor also reports when the worktree has not changed for 10 minutes.

```bash
cd <worktree>; sleep 15; seen=""; last=""; idle=0
while true; do
  cur=$(git log --format='%h %s' <base>..<branch> 2>/dev/null)
  if [ "$cur" != "$seen" ]; then comm -13 <(echo "$seen"|sort) <(echo "$cur"|sort) | sed 's/^/commit: /'; seen=$cur; fi
  state=$( { git status --porcelain; git diff; git ls-files -o --exclude-standard -z | xargs -0 -r cat; } 2>/dev/null | md5sum)
  if [ "$state" != "$last" ]; then last=$state; idle=0; else idle=$((idle+20)); fi
  if [ $idle -gt 0 ] && [ $((idle % 600)) -eq 0 ]; then echo "STALL? no file change for $((idle/60)) min"; fi
  pgrep -f "branch <branch>" >/dev/null || { echo "CLI process exited"; break; }
  sleep 20
done
```

- Run it as a Monitor with the maximum timeout (30 min), and re-arm it on expiry.
- On every expiry and every `STALL?`, read the worker's terminal (e.g. `read_terminal`). A worker still reading or testing is fine: say so and go on. A worker that stopped goes to "When the worker stops" below.
- Stop the monitor once DONE arrives.
- After each event, tell the user in one or two lines what happened.

### When the worker stops

The worker stops when it hits a usage limit, crashes, or waits on something only a human can give. Act at once:

1. Tell the user what you saw on its terminal, in one line.
2. Make sure it cannot resume by itself: a CLI waiting on a usage limit continues on its own when the limit resets, and two writers in one worktree corrupt each other's work. Close it as the section "Close the worker" says.
3. Hand the item to a **subagent** (the Agent tool) with the fallback model and effort, run in the background, in the same worktree and branch. Give it the issue, the repo's rules, what the worker left (commits and uncommitted files, to keep or redo), and the same limits as the worker: no push, no PR, commit on the branch, a final report.
4. Treat its completion notice as DONE and review it in step 8 like any worker's result.

Wait for the limit to reset instead only when the user asks for that.

### 7. Discuss with the worker; don't escalate

When the worker sends PROPOSAL or BLOCKED:

- Evaluate it on the merits. Workers often catch real mistakes in the issue.
- Reply with clear numbered decisions: build this, skip that, keep this rule.
- Mark scope explicitly as IN or OUT.
- Go back to the user **only** for a genuine product decision. Otherwise decide, then report what was agreed in a few lines.

### 8. Review: you are the last gate

The worker already ran its own review. Yours is independent, and it is the only gate when the repo has no CI.

1. Read the whole diff against the issue: `git diff <base>..<branch>`.
2. Run the **full** test suite in the worktree, not only the worker's tests. Run the formatter or linter in check mode.
3. Hunt for what tests usually miss:
    - **Nullable relations.** A foreign key that is nullable or nulls on delete, or soft-deleted parents.
    - **Status guards.** Does a transition also apply to rows in states it shouldn't touch, such as withdrawn, archived or deleted?
    - **Races and idempotency.** Can the effect fire twice: certificates, emails, webhooks, points?
    - **External side effects inside a transaction.** Run them after commit.
    - **Behaviour changes** that users or reports will notice.
    - **Migrations.** Can `down()` run? Are indexes kept that foreign keys depend on?
    - **Docs and rules.** Did the change update every doc, rule and comment that names the code it changed, as the repo's rules ask?
    - **The repo's own rules.** Does the diff break any rule in `.claude/rules`, `docs/agents`, `AGENTS.md` or `CLAUDE.md`?

**If you find a real problem, don't merge and don't go back to the user.** Send the worker a numbered list: the problem, a concrete failing scenario, the fix you expect, and the regression test you expect. Re-arm the monitor. Re-review when DONE arrives again.

### 9. Merge and clean up

Only with merge authority. Otherwise push, open the PR (steps 1 and 2), hand it to the user, and tell them the worktree and branch you will remove once they say it is merged.

1. `git push -u origin <branch>`, from the worktree.
2. `gh pr create`, following the repo's pull request rules first (title, labels, review flags, server or deploy commands). When the repo sets no format, give the body these sections:
    - **Summary**
    - **Decisions**: who made each one
    - **Deploy steps**: commands to run once
    - **Out of scope**
    - **Verification**: the suite count, the linter, the problems your review found and how they were fixed
    - `Closes #N`
3. `gh pr merge <N> --merge`, using the repo's merge style.
4. `git fetch`. Leave the main checkout's branch and files as the user has them.
5. Close the worker as the section "Close the worker" says, and stop any server it started.
6. `git worktree remove <worktree>`, then `git branch -d <branch> && git push origin --delete <branch>`.
7. Confirm the issue closed: `gh issue view <N> --json state`.
8. If the repo's rules name a step after a merge, such as syncing a staging branch, ask the user once whether you do it for every item.

### 10. Record and report

- Update a progress memory: done items with their issue and PR numbers, decisions, deploy steps, and what's next.
- Tell the user, briefly:
    - what was fixed;
    - any behaviour change;
    - any deploy step, with the command in its own code block;
    - what's next.
- Then start the next item, unless the user asked to pause.

## Pitfalls already learned

- **The worker sits idle after finishing.** Waiting for the process to exit leaves both sessions waiting. Always ask for the DONE message.
- **Don't claim work you haven't done.** Example: "I split it into a separate issue" before the issue exists. If you said it, correct yourself at once.
- **Account claims.** The worker CLI may run under a different account than you. Don't claim it shares your usage without checking real usage numbers.
- **Blocked actions.** Auto-mode safety checks may block merges, branch deletion of unmerged branches, or edits to permission settings. Never work around them. Tell the user the exact command or setting to run themselves.
- **Unmerged branches.** Delete only branches git considers merged. Report the others with their unique commits, if any, and let the user decide.
- **The full suite catches regressions; it doesn't prove the new paths.** Read the diff for null and status paths every time.
- **The user works in the main checkout.** Switching its branch, even briefly, moves their files under them. All worker activity stays in the worktree.
- **A stall looks like silence.** A worker stuck on a usage limit neither commits nor exits, and the user noticed before the coordinator did. The stall check in step 6 is there for this.

## Learning from use

This skill improves by running it. When something goes wrong that it didn't prevent, or the user corrects how you coordinate, **propose** a change to the skill in the same session, and edit the file only after the user approves it:

1. Draft the change. Change the step that should have prevented it; when no step fits, add one bullet to "Pitfalls already learned": a bold short lesson, then the rule. Merge it into an existing step or bullet that says the same thing, instead of adding a second one.
2. Write it for any project: no project, repo, ticket or file names, no dates. Keep the general cause and the general fix.
3. Show the user the proposal: what went wrong, in one line, and the exact text you would add or change. Ask them to approve or reject it.
4. Approved: edit the skill as shown. When the skill lives in a git repo, commit the edit straight to that repo's main branch and push it, with only the skill's files in the commit. Rejected: leave the skill unchanged, and go on with the work.
