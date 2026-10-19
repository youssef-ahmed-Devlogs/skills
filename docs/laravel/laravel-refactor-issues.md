## What it does

`laravel-refactor-issues` does what [`refactor-issues`](../engineering/refactor-issues.md) does, for Laravel projects, with a ready search. Its `scan.sh` finds old code that breaks the rules in `.claude/rules/laravel`, in seconds, and names the rule file for each hit.

## When to reach for it

Type `/laravel-refactor-issues` in a Laravel project whose rules are in `.claude/rules/laravel`, one file per subject.

## Prerequisites

The rules in `.claude/rules/laravel`, with the file names its search names: `blade.md`, `cache.md`, `comments.md`, `config.md`, `controllers.md`, `enums.md`, `errors.md`, `excel.md`, `folders.md`, `form-requests.md`, `logging.md`, `models.md`, `naming.md`, `notifications.md`, `policies.md`, `routes.md`, `services.md` and `texts.md`. A project's own checks go in `docs/agents/refactor-checks.sh` and `docs/agents/refactor-checks.md`. You also need `gh`.
