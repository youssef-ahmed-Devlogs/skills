# Guide

Every skill here has its own page, with a real example and the cases it fits. Start with the table below to find the one you need.

## Which skill do I need?

| You want to | Use | Page |
| --- | --- | --- |
| Say what you really want, before the agent builds or writes anything | `interview-me` | [interview-me](./productivity/interview-me.md) |
| Do the same in a project, and write its glossary and ADRs as you go | `interview-with-docs` | [interview-with-docs](./productivity/interview-with-docs.md) |
| Learn a topic from zero, with lessons the agent builds | `tutor-me` | [tutor-me](./productivity/tutor-me.md) |
| Follow a course, a book or a path, with a teacher beside you | `study-with-me` | [study-with-me](./productivity/study-with-me.md) |
| Learn a code project you did not write, and keep up as it changes | `catch-me-up` | [catch-me-up](./productivity/catch-me-up.md) |
| Add a rule, a skill or a check for your agents, in the right place | `add-rule-or-skill` | [add-rule-or-skill](./productivity/add-rule-or-skill.md) |
| Understand what a skill does before you use it | `explain-skill` | [explain-skill](./productivity/explain-skill.md) |
| Hand a list of fixes to CLI workers, and review each one | `delegating-to-cli` | [delegating-to-cli](./engineering/delegating-to-cli.md) |
| Prepare a project to clean up its old code | `setup-refactor-issues` | [setup-refactor-issues](./engineering/setup-refactor-issues.md) |
| Open issues for old code that breaks your rules, safest first | `refactor-issues` | [refactor-issues](./engineering/refactor-issues.md) |
| Do those issues, in one pull request | `implement-refactor-issues` | [implement-refactor-issues](./engineering/implement-refactor-issues.md) |

## How they fit together

Some skills work alone. Others are steps of one job:

- **Clean up old code:** `setup-refactor-issues` once, then `refactor-issues` and `implement-refactor-issues` in turns, one batch at a time, until no file breaks a rule.
- **Learn:** `tutor-me` when you have no course and want the agent to teach you. `study-with-me` when you already follow a course or a book. `catch-me-up` when what you learn is one code project, and it keeps changing.
- **Think first:** `interview-me` before any work that is not clear yet. Other skills can run it too, to ask you before they act. `interview-with-docs` when the plan is inside a project, and its words and decisions should be written down.
- **Look after your agents:** `explain-skill` to learn what a skill does, and `add-rule-or-skill` to add something new where it belongs.

## How a skill starts

Most skills start only when you type their name, such as `/tutor-me Docker` in Claude Code or GitHub Copilot, or `$tutor-me Docker` in Codex. Each skill's page says where to run it, and whether to make a folder for it first. They never start by surprise.

`interview-me` is the one exception: you can type it, but the agent, or another skill, can also start it when a request is not clear yet.

## Install

The short way, for any agent:

```bash
npx skills add youssef-ahmed-Devlogs/skills
```

Other ways, one skill at a time, and updates: [Installing](./install.md).
