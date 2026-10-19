---
name: laravel-refactor-issues
description: Open the next batch of refactor issues that bring old code in line with the Laravel conventions, safest first.
disable-model-invocation: true
---

# Laravel refactor issues

Each run opens the next **batch** of GitHub issues, at most 10 open at once, that bring old code in line with `.claude/rules/laravel` and the project's own code rules. One issue covers one file and all its breaks of the conventions. The batch always comes from the safest **stage** that still has work, and inside it the simplest files go first.

## The output never changes

The app runs on production for real users. A refactor changes only how the code is written. The business logic stays exactly as it is, and so does everything a user gets: the same pages, texts, redirects, status codes, JSON shape, mails and timing.

Every break is planned, none is skipped for being hard. For each one, find the way that applies the convention and keeps the output the same. For example:

- JSON that old JavaScript reads: return it through an API Resource with the same shape, by turning the `data` wrapping off for that Resource.
- A `try`/`catch` that shows a message: move the handling to the one place of `errors.md`, so the same message still shows.
- A text written in the code: move it to the lang files with the very same words.
- A mail sent at once today: queue it only when the delay changes nothing for the person; otherwise send it with `sendNow()`.
- An Enum case renamed: the stored value stays the same.

Only when no such way exists, after real search, does that break leave the file's issue. It gets its own issue with the label `review-critical` (see step 7). That issue changes nothing: it is a question for the owner, and no work starts on it until the owner decides.

## 1. Read the conventions

Read every file in `.claude/rules/laravel`, and the project's own rules: the files in `.claude/rules/project`, when it exists, and `docs/agents/refactor-checks.md`. In the project's rules, the lines that say how code must be written count too. They are the only source of what counts as a break. [CHECKS.md](CHECKS.md) only helps find candidates fast.

## 2. Count the open issues

```bash
gh issue list --label refactor --state open --search "-label:review-critical" --json number --jq length
```

The batch size is 10 minus that number. Open `review-critical` issues do not count: they wait for the owner. At 0, stop and tell the user how many refactor issues are still open.

The issues use these labels: `refactor`, `review-critical`, `ready-for-agent`, `ready-for-human`, and the three review flags of step 4. List the ones the repository has:

```bash
gh label list --limit 200 --json name --jq '.[].name'
```

Make each one that is missing, such as:

```bash
gh label create refactor --description "Bring old code in line with the Laravel conventions" --color 5319e7
gh label create review-critical --description "Would change what clients see or get: the owner decides before any work" --color b60205
```

## 3. Find the candidates

Run the search of [CHECKS.md](CHECKS.md). It covers this scope:

- in: `app`, `routes`, `resources/views`, `lang`, `config`, and each module in `Modules`;
- out: `database/migrations` (an old migration is never edited) and tests on their own (a test changes only with the file it tests).

Count each file's breaks as CHECKS.md says. Drop a file that already has a `refactor` issue open, or one closed as `wontfix`:

```bash
gh issue list --label refactor --state all --search "\"<path>\" in:title" --json number,state,labels
```

A file whose last `refactor` issue was closed as done, and that breaks a convention again, gets a new issue that links the old one.

## 4. Grade each candidate's risk

Give each candidate the review flag its change would need, by the levels of `.claude/rules/process/pull-requests.md`:

- `review-required`: the file touches sign-in, codes, tokens, roles, permissions, policies, or who owns a record; the change needs a migration or a data change; it changes a main feature, as the project's `AGENTS.md` names them, or what a public API answers; or no test covers what will change.
- `review-suggested`: the change touches what people see, such as a view, a text or a JSON answer, so a quick check that it still looks and answers the same is good.
- `review-optional`: the change touches nothing people see, and tests cover it.

In every level the output stays the same: the level says how much a mistake could hurt, not how much may change.

When unsure, pick the higher level. Read the file and its tests to decide: a guess from the path alone is a start, not a grade.

## 5. Pick the batch

The stage is `review-optional`. When no candidate is left at that level, the stage is `review-suggested`, then `review-required`. Never mix stages in one batch.

Inside the stage, order by fewest breaks first, then by the smallest file. Take as many as the batch size.

## 6. Confirm each file

Read each file of the batch in full. Confirm every hit is a real break of a convention, drop false hits, and add the breaks no search can see, such as logic in a controller or a missing Policy call in a Livewire action. A file left with no real break leaves the batch, and the next candidate takes its place.

For each break, write how the output stays the same, as the section above asks.

## 7. Open the issues

One issue per file, in the shape of [ISSUE.md](ISSUE.md), with the labels `refactor`, its review flag and `ready-for-agent`. Write it as `.claude/rules/process/issues.md` says.

A break that cannot keep the output the same gets its own issue, as the `review-critical` part of ISSUE.md says, with the labels `refactor`, `review-critical` and `ready-for-human`. It says what clients would see change, what was tried, and the choices for the owner. It is not part of the batch count.

## 8. Report

Tell the user, in a few lines: the issues opened with their links, the stage, and how many candidates are left in it.
