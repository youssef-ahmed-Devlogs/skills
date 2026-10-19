## What it does

`setup-refactor-issues` prepares a project for [`refactor-issues`](./refactor-issues.md). It reads the project's own code rules, and writes two files: `docs/agents/refactor-checks.sh`, with one search for each rule a search can find, and `docs/agents/refactor-checks.md`, with one line for each rule only reading can see. When a stack's rules came with ready checks, such as `docs/agents/laravel-checks.sh` from [laravel-rules](https://github.com/youssef-ahmed-Devlogs/laravel-rules), it wires them in instead of writing them again. It also makes the labels the issues use.

## When to reach for it

Type `/setup-refactor-issues` once in a project, before the first `/refactor-issues`. Run it again when the rules change: it adds the checks of new rules and asks before it drops old ones.

## Prerequisites

Written code rules in the project, and `gh`. It stops when the project has no rules, since there is nothing to check against.
